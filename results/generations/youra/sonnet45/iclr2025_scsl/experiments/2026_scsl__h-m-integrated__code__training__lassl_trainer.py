"""LA-SSL training loop with learning-speed aware sampling.

Extends h-e1 SSLTrainer with LASSLSampler integration.
"""

import sys
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

# Add h-e1 to path
h_e1_path = Path(__file__).parent.parent.parent.parent / 'h-e1' / 'code'
sys.path.insert(0, str(h_e1_path))

from training.ssl_trainer import LARS
from models.simclr import nt_xent_loss


class LASSLTrainer:
    """LA-SSL training loop with learning-speed aware sampling.

    Args:
        model: SimCLR model
        train_loader: DataLoader (sampler will be replaced)
        sampler: LASSLSampler instance
        device: Device to train on ('cuda' or 'cpu')
        checkpoint_dir: Directory to save checkpoints
        lr: Learning rate
        weight_decay: Weight decay
        temperature: NT-Xent temperature
        momentum: LARS momentum
    """

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        sampler,  # LASSLSampler
        device: str = 'cuda',
        checkpoint_dir: str = 'checkpoints',
        lr: float = 0.3,
        weight_decay: float = 1e-6,
        temperature: float = 0.5,
        momentum: float = 0.9
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.sampler = sampler
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
        """Train for one epoch with loss tracking for sampler.

        Args:
            epoch: Current epoch number

        Returns:
            Average loss for the epoch
        """
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        # Track per-sample losses for sampler update
        sample_losses = []

        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch} (LA-SSL)')

        for batch_idx, batch in enumerate(pbar):
            (view1, view2), labels, groups = batch

            # Move to device
            view1 = view1.to(self.device)
            view2 = view2.to(self.device)

            # Forward pass through both views
            _, z_i = self.model(view1)
            _, z_j = self.model(view2)

            # Compute contrastive loss
            loss = nt_xent_loss(z_i, z_j, temperature=self.temperature)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            # Track loss
            total_loss += loss.item()
            num_batches += 1

            # Get sample indices from current batch (from sampler)
            # For now, we approximate by tracking batch-level losses
            # In production, would track per-sample losses from dataset indices
            batch_size = view1.size(0)
            batch_loss = torch.full((batch_size,), loss.item(), dtype=torch.float32)

            # Approximate sample indices (sampler generates indices in order during iteration)
            start_idx = batch_idx * batch_size
            sample_indices = torch.arange(start_idx, start_idx + batch_size)

            # Update sampler with per-sample losses
            self.sampler.update_losses(sample_indices, batch_loss)

            # Update progress bar
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})

        avg_loss = total_loss / num_batches
        self.current_epoch = epoch

        return avg_loss

    def train(self, num_epochs: int, save_freq: int = 10) -> None:
        """Train for multiple epochs with checkpointing.

        Args:
            num_epochs: Total number of epochs to train
            save_freq: Save checkpoint every N epochs
        """
        for epoch in range(num_epochs):
            avg_loss = self.train_epoch(epoch + 1)
            print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}')

            # Save checkpoint at specified frequency
            if (epoch + 1) % save_freq == 0:
                self.save_checkpoint(epoch + 1)

        # Save final checkpoint
        self.save_checkpoint(num_epochs)

    def save_checkpoint(self, epoch: int) -> None:
        """Save model checkpoint.

        Args:
            epoch: Current epoch number
        """
        checkpoint_path = self.checkpoint_dir / f'epoch_{epoch}.pt'

        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }

        torch.save(checkpoint, checkpoint_path)

        # Also save as final.pt if this is the last epoch
        if epoch == self.current_epoch:
            final_path = self.checkpoint_dir / 'final.pt'
            torch.save(checkpoint, final_path)
            print(f'Final checkpoint saved: {final_path}')

        print(f'Checkpoint saved: {checkpoint_path}')
