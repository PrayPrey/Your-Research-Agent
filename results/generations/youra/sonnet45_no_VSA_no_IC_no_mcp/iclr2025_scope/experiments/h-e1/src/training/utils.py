import torch
import random
import numpy as np
import os


def set_seed(seed: int = 42):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def save_checkpoint(
    path: str,
    step: int,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    loss: float
):
    """Save training checkpoint."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save({
        'step': step,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss
    }, path)


def load_checkpoint(path: str, model: torch.nn.Module, optimizer: torch.optim.Optimizer = None):
    """Load training checkpoint."""
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['step'], checkpoint['loss']
