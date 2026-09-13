"""SimCLR SSL training loop with LARS optimizer and checkpointing.

Reference:
- Chen et al. 2020 - SimCLR
- You et al. 2017 - LARS optimizer
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import Optional, Tuple, Callable
from tqdm import tqdm


class DualAugmentationDataset(Dataset):
    """Wrapper dataset that applies two different augmentations to each sample.

    SimCLR requires two augmented views of the same image for contrastive learning.

    Args:
        base_dataset: Base dataset (e.g., WaterbirdsDataset)
        transform: Transform to apply twice (should include randomness)
    """

    def __init__(self, base_dataset: Dataset, transform: Callable):
        self.base_dataset = base_dataset
        self.transform = transform

    def __len__(self) -> int:
        return len(self.base_dataset)

    def __getitem__(self, idx: int) -> Tuple[Tuple[torch.Tensor, torch.Tensor], int, int]:
        """Get two augmented views of the same sample.

        Returns:
            (view1, view2): Two augmented versions of the same image
            label: Original label
            group: Original group ID
        """
        # Get base sample (already transformed by base dataset)
        # We need the raw image, so we'll get from base dataset's raw data
        if hasattr(self.base_dataset, 'metadata'):
            # WaterbirdsDataset - load raw image
            from PIL import Image
            import os
            row = self.base_dataset.metadata.iloc[idx]
            img_path = os.path.join(self.base_dataset.root_dir, row['img_filename'])
            image = Image.open(img_path).convert('RGB')
            label = int(row['y'])
            place = int(row['place'])
            group = label * 2 + place
        else:
            # TensorDataset (for testing) - convert tensor to PIL Image
            import torchvision.transforms.functional as F
            from PIL import Image

            tensor_img, label, group = self.base_dataset[idx]

            # Convert tensor to PIL Image for transform pipeline
            # Tensor is in [C, H, W] format with values in [0, 1]
            image = F.to_pil_image(tensor_img)

        # Apply transform twice to get two different views
        view1 = self.transform(image)
        view2 = self.transform(image)

        return (view1, view2), label, group


class LARS(torch.optim.Optimizer):
    """Layer-wise Adaptive Rate Scaling (LARS) optimizer.

    Reference: You et al. 2017 - Large Batch Training of Convolutional Networks

    Args:
        params: Model parameters
        lr: Learning rate
        momentum: Momentum factor
        weight_decay: Weight decay (L2 penalty)
        trust_coefficient: LARS trust coefficient (eta)
    """

    def __init__(
        self,
        params,
        lr: float = 1.0,
        momentum: float = 0.9,
        weight_decay: float = 1e-6,
        trust_coefficient: float = 0.001
    ):
        defaults = dict(
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay,
            trust_coefficient=trust_coefficient
        )
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        """Perform a single optimization step."""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            weight_decay = group['weight_decay']
            momentum = group['momentum']
            trust_coefficient = group['trust_coefficient']
            lr = group['lr']

            for p in group['params']:
                if p.grad is None:
                    continue

                param = p.data
                grad = p.grad.data

                # Add weight decay
                if weight_decay != 0:
                    grad = grad.add(param, alpha=weight_decay)

                # Compute local learning rate (LARS)
                param_norm = torch.norm(param)
                grad_norm = torch.norm(grad)

                if param_norm != 0 and grad_norm != 0:
                    local_lr = trust_coefficient * param_norm / grad_norm
                else:
                    local_lr = 1.0

                # Apply momentum
                param_state = self.state[p]
                if 'momentum_buffer' not in param_state:
                    buf = param_state['momentum_buffer'] = torch.clone(grad).detach()
                else:
                    buf = param_state['momentum_buffer']
                    buf.mul_(momentum).add_(grad)

                # Update parameters
                param.add_(buf, alpha=-lr * local_lr)

        return loss


class SSLTrainer:
    """SimCLR SSL training loop.

    Trains SimCLR model with NT-Xent loss and LARS optimizer.
    Supports checkpointing and loss logging.

    Args:
        model: SimCLR model
        train_loader: DataLoader with dual augmentations
        device: Device to train on ('cuda' or 'cpu')
        checkpoint_dir: Directory to save checkpoints
        lr: Learning rate (default: 0.3 for batch_size=256)
        weight_decay: Weight decay (default: 1e-6)
        temperature: NT-Xent temperature (default: 0.5)
        momentum: LARS momentum (default: 0.9)
    """

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        device: str = 'cuda',
        checkpoint_dir: str = 'checkpoints',
        lr: float = 0.3,
        weight_decay: float = 1e-6,
        temperature: float = 0.5,
        momentum: float = 0.9
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.device = device
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.temperature = temperature

        # Initialize LARS optimizer
        self.optimizer = LARS(
            self.model.parameters(),
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay
        )

        self.current_epoch = 0

    def train_epoch(self, epoch: int) -> float:
        """Train for one epoch.

        Args:
            epoch: Current epoch number

        Returns:
            Average loss for the epoch
        """
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch}')

        for batch in pbar:
            (view1, view2), labels, groups = batch

            # Move to device
            view1 = view1.to(self.device)
            view2 = view2.to(self.device)

            # Forward pass through both views
            _, z_i = self.model(view1)
            _, z_j = self.model(view2)

            # Import nt_xent_loss here to avoid circular import
            from models.simclr import nt_xent_loss

            # Compute contrastive loss
            loss = nt_xent_loss(z_i, z_j, temperature=self.temperature)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            # Update metrics
            total_loss += loss.item()
            num_batches += 1

            # Update progress bar
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})

        avg_loss = total_loss / num_batches
        self.current_epoch = epoch

        return avg_loss

    def train(self, num_epochs: int, save_freq: int = 50) -> None:
        """Train for multiple epochs with checkpointing.

        Args:
            num_epochs: Total number of epochs to train
            save_freq: Save checkpoint every N epochs
        """
        for epoch in range(num_epochs):
            avg_loss = self.train_epoch(epoch)

            print(f'Epoch {epoch}: avg_loss = {avg_loss:.4f}')

            # Save checkpoint at specified frequency
            if (epoch + 1) % save_freq == 0 or epoch == num_epochs - 1:
                checkpoint_path = self.save_checkpoint(epoch + 1)
                print(f'Saved checkpoint: {checkpoint_path}')

    def save_checkpoint(self, epoch: int) -> str:
        """Save model checkpoint.

        Args:
            epoch: Current epoch number

        Returns:
            Path to saved checkpoint
        """
        checkpoint_path = self.checkpoint_dir / f'simclr_epoch_{epoch}.pth'

        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, checkpoint_path)

        return str(checkpoint_path)

    def load_checkpoint(self, checkpoint_path: str) -> int:
        """Load model checkpoint.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            Epoch number from checkpoint
        """
        checkpoint = torch.load(checkpoint_path, map_location=self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        epoch = checkpoint['epoch']

        self.current_epoch = epoch

        return epoch

    def get_frozen_encoder(self) -> nn.Module:
        """Get encoder with frozen weights for downstream tasks.

        Returns:
            Frozen encoder module
        """
        encoder = self.model.get_encoder()
        encoder.eval()

        # Freeze all parameters
        for param in encoder.parameters():
            param.requires_grad = False

        return encoder
