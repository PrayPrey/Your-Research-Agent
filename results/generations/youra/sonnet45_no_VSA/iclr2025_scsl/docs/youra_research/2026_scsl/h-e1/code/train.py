"""Training loop implementation."""
import torch
import torch.optim as optim
import torch.nn.functional as F
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-e1/code')
from config import TRAINING_CONFIG
from data import get_dataloaders
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


def train_condition(condition: str):
    """
    Train model for single experimental condition.

    Args:
        condition: Augmentation condition

    Returns:
        dict: {model, train_losses, test_accs, per_class_acc}
    """
    # Set seed
    torch.manual_seed(TRAINING_CONFIG["seed"])

    # Get device
    device = torch.device(TRAINING_CONFIG["device"])

    # Get data
    train_loader, test_loader = get_dataloaders(
        condition,
        batch_size=TRAINING_CONFIG["batch_size"]
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

    for epoch in range(1, TRAINING_CONFIG["epochs"] + 1):
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, device)
        train_losses.append(train_loss)

        # Test
        test_acc = test_epoch(model, test_loader, device)
        test_accs.append(test_acc)

        # Step scheduler
        scheduler.step()

        print(f"[{condition}] Epoch {epoch}/{TRAINING_CONFIG['epochs']}: "
              f"Loss={train_loss:.4f}, Acc={test_acc:.2f}%")

    return {
        "model": model,
        "train_losses": train_losses,
        "test_accs": test_accs
    }
