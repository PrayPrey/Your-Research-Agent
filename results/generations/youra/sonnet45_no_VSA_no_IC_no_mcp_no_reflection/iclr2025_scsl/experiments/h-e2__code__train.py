"""
Training orchestration for h-e2: Extended training with gradient and forgetting tracking.
"""

import sys
sys.path.append('/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/code')

from dataclasses import dataclass
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.transforms.functional as TF
import numpy as np

from data import DatasetConfig, get_dataloader
from model_v2 import get_baseline_model, AblationTrainer
from config import TrainConfig, EXTENDED_TRAIN_CONFIG, GRADIENT_TRACKER_CONFIG
from trackers import GradientVarianceTracker, ForgettingTracker


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_predictions(model: nn.Module, dataloader: DataLoader, variant: str, device: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Get all predictions and labels. Returns: ([N], [N])"""
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)

            if variant == 'spurious':
                images = TF.gaussian_blur(images, kernel_size=15)
            elif variant == 'core':
                images = TF.rgb_to_grayscale(images, num_output_channels=3)

            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.append(preds.cpu())
            all_labels.append(labels)

    return torch.cat(all_preds), torch.cat(all_labels)


def train_with_tracking(
    trainer: AblationTrainer,
    variant: str,
    dataloader: DataLoader,
    max_epochs: int,
    grad_tracker: GradientVarianceTracker,
    forget_tracker: ForgettingTracker,
    checkpoint_epochs: list[int]
) -> int | None:
    """
    Train variant with gradient and prediction tracking.
    Returns convergence epoch or None.
    """
    for epoch in range(1, max_epochs + 1):
        # Standard training epoch
        avg_loss = trainer.train_epoch(dataloader, variant)

        # Log gradient norm (call after backward pass in train_epoch)
        # Need to do one extra backward to capture gradients
        trainer.model.train()
        for images, labels in dataloader:
            images = images.to(trainer.device)
            labels = labels.to(trainer.device)

            if variant == 'spurious':
                images = TF.gaussian_blur(images, kernel_size=15)
            elif variant == 'core':
                images = TF.rgb_to_grayscale(images, num_output_channels=3)

            trainer.optimizer.zero_grad()
            outputs = trainer.model(images)
            loss = trainer.criterion(outputs, labels)
            loss.backward()

            # Log gradient norm
            grad_norm = grad_tracker.log_gradient_norm(trainer.model)
            break  # Just need gradients from one batch

        # Log predictions for forgetting tracking
        preds, labels_all = get_predictions(trainer.model, dataloader, variant, trainer.device)
        forget_tracker.log_predictions(epoch, preds, labels_all)

        # Check convergence
        accuracy = trainer.compute_accuracy(dataloader, variant)

        if epoch % 5 == 0 or epoch in checkpoint_epochs:
            print(f"  Epoch {epoch}/{max_epochs} | Loss: {avg_loss:.4f} | Acc: {accuracy:.2%} | GradNorm: {grad_norm:.4f}")

        if accuracy >= trainer.target_accuracy:
            print(f"  → Converged at epoch {epoch} (accuracy {accuracy:.2%})")
            return epoch

    print(f"  → NO CONVERGENCE (final accuracy {accuracy:.2%})")
    return None


def run_single_experiment_with_tracking(config: TrainConfig) -> dict:
    """
    Extend h-e1 training with variance + forgetting tracking.

    Returns:
        {
            'dataset': str,
            'seed': int,
            'E_spurious': int | None,
            'E_core': int | None,
            'variance_spurious': list[float],
            'variance_core': list[float],
            'forgetting_spurious': float,
            'forgetting_core': float,
            'variance_ratio': float
        }
    """
    set_seed(config.seed)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"\n{'='*60}")
    print(f"Running {config.dataset} | Seed {config.seed} (with tracking)")
    print(f"{'='*60}")

    # Load data
    dataset_config = DatasetConfig(name=config.dataset, batch_size=config.batch_size)
    train_loader = get_dataloader(dataset_config, split='train')

    checkpoint_epochs = GRADIENT_TRACKER_CONFIG['checkpoint_epochs']

    # Train spurious variant with tracking
    print("\n[Spurious-only variant]")
    model_s = get_baseline_model(config.dataset, pretrained=False)
    trainer_s = AblationTrainer(model_s, config.dataset, config.lr, config.weight_decay, device)
    grad_tracker_s = GradientVarianceTracker(window_size=GRADIENT_TRACKER_CONFIG['window_size'])
    forget_tracker_s = ForgettingTracker(num_samples=len(train_loader.dataset))

    E_spurious = train_with_tracking(
        trainer_s, 'spurious', train_loader, config.max_epochs,
        grad_tracker_s, forget_tracker_s, checkpoint_epochs
    )

    # Train core variant with tracking
    print("\n[Core-only variant]")
    model_c = get_baseline_model(config.dataset, pretrained=False)
    trainer_c = AblationTrainer(model_c, config.dataset, config.lr, config.weight_decay, device)
    grad_tracker_c = GradientVarianceTracker(window_size=GRADIENT_TRACKER_CONFIG['window_size'])
    forget_tracker_c = ForgettingTracker(num_samples=len(train_loader.dataset))

    E_core = train_with_tracking(
        trainer_c, 'core', train_loader, config.max_epochs,
        grad_tracker_c, forget_tracker_c, checkpoint_epochs
    )

    # Compute metrics
    var_s = grad_tracker_s.get_all_variances(checkpoint_epochs)
    var_c = grad_tracker_c.get_all_variances(checkpoint_epochs)

    mean_var_s = np.mean([v for v in var_s if v > 0]) if any(v > 0 for v in var_s) else 0.0
    mean_var_c = np.mean([v for v in var_c if v > 0]) if any(v > 0 for v in var_c) else 0.0
    variance_ratio = mean_var_s / mean_var_c if mean_var_c > 0 else float('inf')

    return {
        'dataset': config.dataset,
        'seed': config.seed,
        'E_spurious': E_spurious,
        'E_core': E_core,
        'variance_spurious': var_s,
        'variance_core': var_c,
        'forgetting_spurious': forget_tracker_s.compute_forgetting_events(),
        'forgetting_core': forget_tracker_c.compute_forgetting_events(),
        'variance_ratio': variance_ratio
    }


if __name__ == '__main__':
    # Test with single seed
    config = TrainConfig(
        dataset=EXTENDED_TRAIN_CONFIG['dataset'],
        lr=EXTENDED_TRAIN_CONFIG['lr'],
        max_epochs=EXTENDED_TRAIN_CONFIG['max_epochs'],
        weight_decay=EXTENDED_TRAIN_CONFIG['weight_decay'],
        batch_size=EXTENDED_TRAIN_CONFIG['batch_size'],
        seed=EXTENDED_TRAIN_CONFIG['seed']
    )

    results = run_single_experiment_with_tracking(config)
    print("\n" + "="*60)
    print("Experiment complete. Results:")
    print(f"  E_spurious: {results['E_spurious']}")
    print(f"  E_core: {results['E_core']}")
    print(f"  Variance ratio: {results['variance_ratio']:.4f}")
    print(f"  Forgetting (spurious): {results['forgetting_spurious']:.4f}")
    print(f"  Forgetting (core): {results['forgetting_core']:.4f}")
