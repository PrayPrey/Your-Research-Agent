"""
Training pipeline for H-E1 SAM+SWA experiment
Implements 5 training methods: ERM, SAM, SWA, Joint, Sequential
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim.swa_utils import update_bn
import time
from typing import Dict, Tuple, List, Optional
import numpy as np

from optimizers.methods import enable_running_stats, disable_running_stats


def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer,
    criterion: nn.Module,
    device: str,
    method: str,
    epoch: int,
    swa_start: int = 75,
    gradient_clip_norm: float = 1.0
) -> Dict[str, float]:
    """
    Train for one epoch with method-specific logic.

    Args:
        model: Model to train
        dataloader: Training data loader
        optimizer: Optimizer or wrapper (SAM, JointSAMSWA, etc.)
        criterion: Loss function (BCEWithLogitsLoss)
        device: Device (cuda/cpu)
        method: Training method (ERM, SAM, SWA, Joint, Sequential)
        epoch: Current epoch number
        swa_start: Epoch to start SWA
        gradient_clip_norm: Gradient clipping threshold

    Returns:
        metrics: {"loss": mean_loss, "accuracy": mean_acc}
    """
    model.train()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for batch_idx, batch_data in enumerate(dataloader):
        # Unpack batch (handle both ColoredMNIST and CelebA formats)
        if len(batch_data) == 3:
            inputs, targets, metadata = batch_data
        else:
            inputs, targets = batch_data[0], batch_data[1]

        inputs, targets = inputs.to(device), targets.to(device)
        targets = targets.float()  # For BCEWithLogitsLoss

        if method == "ERM":
            # Standard SGD
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs[:, 1], targets)  # Binary classification
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
            optimizer.step()

        elif method == "SAM":
            # SAM two-step gradient
            enable_running_stats(model)
            outputs = model(inputs)
            loss = criterion(outputs[:, 1], targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
            optimizer.first_step(zero_grad=True)

            disable_running_stats(model)
            outputs_perturbed = model(inputs)
            loss_perturbed = criterion(outputs_perturbed[:, 1], targets)
            loss_perturbed.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
            optimizer.second_step(zero_grad=True)

        elif method == "SWA":
            # Standard SGD + SWA averaging after swa_start
            optimizer["optimizer"].zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs[:, 1], targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
            optimizer["optimizer"].step()

        elif method == "Joint":
            # Joint SAM+SWA (wrapper handles both)
            enable_running_stats(model)
            outputs = model(inputs)
            loss = criterion(outputs[:, 1], targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
            optimizer.sam.first_step(zero_grad=True)

            disable_running_stats(model)
            outputs_perturbed = model(inputs)
            loss_perturbed = criterion(outputs_perturbed[:, 1], targets)
            loss_perturbed.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
            optimizer.sam.second_step(zero_grad=True)

        elif method == "Sequential":
            # SAM until swa_start, then SGD+SWA
            if epoch < swa_start:
                # Use SAM
                enable_running_stats(model)
                outputs = model(inputs)
                loss = criterion(outputs[:, 1], targets)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
                optimizer["sam"].first_step(zero_grad=True)

                disable_running_stats(model)
                outputs_perturbed = model(inputs)
                loss_perturbed = criterion(outputs_perturbed[:, 1], targets)
                loss_perturbed.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
                optimizer["sam"].second_step(zero_grad=True)
            else:
                # Use SGD
                optimizer["sgd"].zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs[:, 1], targets)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
                optimizer["sgd"].step()

        # Track metrics
        total_loss += loss.item() * inputs.size(0)
        preds = (outputs[:, 1] > 0).long()
        total_correct += (preds == targets.long()).sum().item()
        total_samples += inputs.size(0)

    return {
        "loss": total_loss / total_samples,
        "accuracy": total_correct / total_samples
    }


def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: str
) -> Dict[str, float]:
    """
    Evaluate model on validation/test set.

    Args:
        model: Model to evaluate
        dataloader: Evaluation data loader
        criterion: Loss function
        device: Device (cuda/cpu)

    Returns:
        metrics: {"loss": mean_loss, "accuracy": mean_acc}
    """
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    with torch.no_grad():
        for batch_data in dataloader:
            # Unpack batch
            if len(batch_data) == 3:
                inputs, targets, metadata = batch_data
            else:
                inputs, targets = batch_data[0], batch_data[1]

            inputs, targets = inputs.to(device), targets.to(device)
            targets = targets.float()

            outputs = model(inputs)
            loss = criterion(outputs[:, 1], targets)

            total_loss += loss.item() * inputs.size(0)
            preds = (outputs[:, 1] > 0).long()
            total_correct += (preds == targets.long()).sum().item()
            total_samples += inputs.size(0)

    return {
        "loss": total_loss / total_samples,
        "accuracy": total_correct / total_samples
    }


def compute_worst_group_acc(
    model: nn.Module,
    dataloader: DataLoader,
    dataset_name: str,
    device: str
) -> Tuple[float, List[float]]:
    """
    Compute worst-group accuracy (min across 4 demographic groups).

    Args:
        model: Model to evaluate
        dataloader: Data loader with group metadata
        dataset_name: Dataset name (ColoredMNIST, CelebA)
        device: Device (cuda/cpu)

    Returns:
        worst_group_acc: Minimum accuracy across groups
        group_accs: List of 4 per-group accuracies [G0, G1, G2, G3]
    """
    model.eval()

    if dataset_name == "ColoredMNIST":
        group_correct = [0, 0, 0, 0]
        group_total = [0, 0, 0, 0]

        with torch.no_grad():
            for inputs, targets, metadata in dataloader:
                inputs, targets = inputs.to(device), targets.to(device)
                colors = metadata["color"].to(device)

                outputs = model(inputs)
                preds = (outputs[:, 1] > 0).long()

                # Group assignment: group_id = label * 2 + color
                groups = targets * 2 + colors

                for g in range(4):
                    mask = (groups == g)
                    if mask.sum() > 0:
                        group_correct[g] += (preds[mask] == targets[mask]).sum().item()
                        group_total[g] += mask.sum().item()

        group_accs = [
            group_correct[g] / group_total[g] if group_total[g] > 0 else 0.0
            for g in range(4)
        ]
        worst_group_acc = min(group_accs)

        return worst_group_acc, group_accs

    elif dataset_name == "CelebA":
        # Use WILDS evaluator
        try:
            from wilds import get_dataset
        except ImportError:
            raise ImportError("WILDS package required for CelebA evaluation")

        all_preds = []
        all_targets = []
        all_metadata = []

        with torch.no_grad():
            for batch_data in dataloader:
                inputs = batch_data[0].to(device)
                targets = batch_data[1]
                metadata = batch_data[2]

                outputs = model(inputs)
                preds = (outputs[:, 1] > 0).long().cpu()

                all_preds.append(preds)
                all_targets.append(targets)
                all_metadata.append(metadata)

        all_preds = torch.cat(all_preds)
        all_targets = torch.cat(all_targets)
        all_metadata = torch.cat(all_metadata)

        # Use WILDS official evaluator
        dataset = get_dataset("celebA", root_dir="data/celeba")
        results, _ = dataset.eval(all_preds, all_targets, all_metadata)

        worst_group_acc = results["acc_wg"]
        group_accs = [
            results.get(f"acc_y:0_a:0", 0.0),
            results.get(f"acc_y:0_a:1", 0.0),
            results.get(f"acc_y:1_a:0", 0.0),
            results.get(f"acc_y:1_a:1", 0.0)
        ]

        return worst_group_acc, group_accs

    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")


def train_method(
    method: str,
    dataset_name: str,
    seed: int,
    config: object,
    output_dir: str = "outputs/h-e1"
) -> dict:
    """
    Full training pipeline for one method on one dataset.

    Args:
        method: Training method (ERM, SAM, SWA, Joint, Sequential)
        dataset_name: Dataset name (ColoredMNIST, CelebA)
        seed: Random seed
        config: Configuration object (from get_config())
        output_dir: Output directory for checkpoints/logs

    Returns:
        results: {
            "method": method,
            "dataset": dataset_name,
            "seed": seed,
            "test_wg_acc": worst_group_acc,
            "test_avg_acc": avg_acc,
            "training_time": elapsed_time
        }
    """
    # Set seed
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Import here to avoid circular dependency
    from data.datasets import get_dataloaders
    from models.resnet import get_model
    from optimizers.methods import get_optimizer

    # Get data loaders
    batch_size = config.data.batch_size
    dataloaders = get_dataloaders(
        dataset_name=dataset_name,
        batch_size=batch_size,
        root_dir=str(config.project_root / "data" / dataset_name.lower())
    )
    train_loader = dataloaders["train"]
    val_loader = dataloaders["val"]
    test_loader = dataloaders["test"]

    # Get model (check if pretrained attribute exists)
    pretrained = getattr(config.training, "pretrained", True)
    model = get_model(method, pretrained=pretrained)

    # Get device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    # Get learning rate and epochs
    if dataset_name == "CelebA":
        lr = getattr(config.training, "lr_celeba", 0.0001)
        epochs = getattr(config.training, "epochs_celeba", 50)
    else:
        lr = getattr(config.training, "lr", 0.001)
        epochs = getattr(config.training, "epochs", 100)

    # Get optimizer
    swa_start = int(epochs * 0.75)
    optimizer = get_optimizer(
        method=method,
        model=model,
        lr=lr,
        momentum=getattr(config.training, "momentum", 0.9),
        weight_decay=getattr(config.training, "weight_decay", 0.0001),
        rho=getattr(config.training, "rho", 0.05),
        swa_start=swa_start,
        swa_lr=getattr(config.training, "swa_lr", 0.05),
        epochs=epochs
    )

    # Loss function
    criterion = nn.BCEWithLogitsLoss()

    # Training loop
    start_time = time.time()
    best_val_wg_acc = 0.0
    validate_every = getattr(config.training, "validate_every", 5) if dataset_name == "ColoredMNIST" else getattr(config.training, "validate_every_celeba", 2)

    print(f"\nTraining {method} on {dataset_name} (seed={seed})")
    print(f"Epochs: {epochs}, LR: {lr}, SWA start: {swa_start}")

    for epoch in range(epochs):
        # Train epoch
        train_metrics = train_epoch(
            model=model,
            dataloader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            device=device,
            method=method,
            epoch=epoch,
            swa_start=swa_start,
            gradient_clip_norm=getattr(config.training, "gradient_clip_norm", 1.0)
        )

        # Validation
        if epoch % validate_every == 0 or epoch == epochs - 1:
            val_wg_acc, val_group_accs = compute_worst_group_acc(
                model, val_loader, dataset_name, device
            )

            print(f"Epoch {epoch}/{epochs}: "
                  f"Train Loss={train_metrics['loss']:.4f}, "
                  f"Train Acc={train_metrics['accuracy']:.4f}, "
                  f"Val WG Acc={val_wg_acc:.4f}")

            if val_wg_acc > best_val_wg_acc:
                best_val_wg_acc = val_wg_acc

        # SWA-specific end-of-epoch updates
        if method == "SWA" and epoch >= swa_start:
            optimizer["swa_model"].update_parameters(model)
            optimizer["swa_scheduler"].step()
        elif method == "Joint":
            optimizer.on_epoch_end(epoch)
        elif method == "Sequential" and epoch >= swa_start:
            optimizer["swa_model"].update_parameters(model)
            optimizer["swa_scheduler"].step()

    # Post-training BN update for SWA methods
    if method == "SWA":
        print("Updating BN statistics for SWA model...")
        # Custom update_bn that handles device transfer
        swa_model = optimizer["swa_model"]
        swa_model.eval()
        with torch.no_grad():
            for batch_data in train_loader:
                if len(batch_data) == 3:
                    inputs = batch_data[0]
                else:
                    inputs = batch_data[0]
                inputs = inputs.to(device)
                swa_model(inputs)
        final_model = optimizer["swa_model"]
    elif method == "Joint":
        print("Updating BN statistics for Joint SAM+SWA model...")
        optimizer.finalize(train_loader, device=device)
        final_model = optimizer.get_model()
    elif method == "Sequential":
        print("Updating BN statistics for Sequential model...")
        swa_model = optimizer["swa_model"]
        swa_model.eval()
        with torch.no_grad():
            for batch_data in train_loader:
                if len(batch_data) == 3:
                    inputs = batch_data[0]
                else:
                    inputs = batch_data[0]
                inputs = inputs.to(device)
                swa_model(inputs)
        final_model = optimizer["swa_model"]
    else:
        final_model = model

    # Final evaluation
    print("Computing final test metrics...")
    test_wg_acc, test_group_accs = compute_worst_group_acc(
        final_model, test_loader, dataset_name, device
    )
    test_metrics = evaluate(final_model, test_loader, criterion, device)

    elapsed_time = time.time() - start_time
    elapsed_hours = elapsed_time / 3600.0

    print(f"Completed: Test WG Acc={test_wg_acc:.4f}, Test Avg Acc={test_metrics['accuracy']:.4f}, Time={elapsed_hours:.2f}h")

    return {
        "method": method,
        "dataset": dataset_name,
        "seed": seed,
        "test_wg_acc": test_wg_acc,
        "test_avg_acc": test_metrics["accuracy"],
        "test_group_accs": test_group_accs,
        "training_time_hours": elapsed_hours
    }
