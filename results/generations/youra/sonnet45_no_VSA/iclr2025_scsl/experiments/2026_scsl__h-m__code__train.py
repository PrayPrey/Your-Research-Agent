"""Training loop with multi-seed support."""
import torch
import torch.optim as optim
import torch.nn.functional as F
from pathlib import Path
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-m/code')
from config import TRAINING_CONFIG, OUTPUT_CONFIG
from data import get_dataloaders, set_seed
from model import MNISTNet


def train_epoch(model, train_loader, optimizer, device):
    """Single training epoch."""
    model.train()
    total_loss = 0.0

    for data, target in train_loader:
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    return total_loss / len(train_loader)


def test_epoch(model, test_loader, device):
    """Single test epoch."""
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)

    return 100.0 * correct / total


def save_checkpoint(model, condition: str, seed: int, output_dir: str) -> str:
    """
    Save trained model checkpoint.

    Args:
        model: Trained model
        condition: Condition name
        seed: Seed value
        output_dir: Output directory

    Returns:
        Path to saved checkpoint
    """
    ckpt_dir = Path(output_dir) / OUTPUT_CONFIG["checkpoints_dir"]
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    ckpt_path = ckpt_dir / f"{condition}_seed{seed}.pth"
    torch.save(model.state_dict(), ckpt_path)

    return str(ckpt_path)


def train_condition_with_seed(condition: str, seed: int, epochs: int = 14):
    """
    Train model for (condition, seed) pair.

    Args:
        condition: Augmentation condition
        seed: Random seed
        epochs: Number of epochs (default 14)

    Returns:
        dict: {model, train_losses, test_accs, checkpoint_path}
    """
    # Set seed
    set_seed(seed)

    # Get device
    device = torch.device(TRAINING_CONFIG["device"])

    # Get data
    train_loader, test_loader = get_dataloaders(
        condition,
        batch_size=TRAINING_CONFIG["batch_size"],
        seed=seed
    )

    # Initialize model
    model = MNISTNet().to(device)

    # Optimizer & scheduler
    optimizer = optim.Adadelta(
        model.parameters(),
        lr=TRAINING_CONFIG["lr"]
    )
    scheduler = optim.lr_scheduler.StepLR(
        optimizer,
        step_size=TRAINING_CONFIG["step_size"],
        gamma=TRAINING_CONFIG["gamma"]
    )

    # Training loop
    train_losses = []
    test_accs = []

    for epoch in range(1, epochs + 1):
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, device)
        train_losses.append(train_loss)

        # Test
        test_acc = test_epoch(model, test_loader, device)
        test_accs.append(test_acc)

        # Step scheduler
        scheduler.step()

        if epoch % 5 == 0 or epoch == epochs:
            print(f"[{condition}/seed{seed}] Epoch {epoch}/{epochs}: "
                  f"Loss={train_loss:.4f}, Acc={test_acc:.2f}%")

    # Save checkpoint
    checkpoint_path = save_checkpoint(model, condition, seed, OUTPUT_CONFIG["output_dir"])

    return {
        "model": model,
        "train_losses": train_losses,
        "test_accs": test_accs,
        "checkpoint_path": checkpoint_path
    }
