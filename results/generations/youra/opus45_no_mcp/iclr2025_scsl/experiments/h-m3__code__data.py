"""H-M3 Data: WGA curve loading from H-E1 checkpoints using real Waterbirds evaluation"""
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from typing import Optional
from torchvision import models, transforms
from torch.utils.data import DataLoader

try:
    from wilds import get_dataset
    from wilds.common.data_loaders import get_eval_loader
    WILDS_AVAILABLE = True
except ImportError:
    WILDS_AVAILABLE = False

from config import DetectionConfig, CONFIG

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Use H-E1 data directory where dataset is already downloaded
DEFAULT_DATA_ROOT = str(Path(__file__).parent.parent.parent / "h-e1/code/data")

_dataset_cache = {}
_loader_cache = {}


def build_resnet50(num_classes: int = 2) -> nn.Module:
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def get_eval_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_waterbirds_loader(split: str = "val", batch_size: int = 128, root_dir: str = None) -> DataLoader:
    if root_dir is None:
        root_dir = DEFAULT_DATA_ROOT
    cache_key = (split, batch_size, root_dir)
    if cache_key in _loader_cache:
        return _loader_cache[cache_key]

    if not WILDS_AVAILABLE:
        raise ImportError("wilds package required: pip install wilds")

    if root_dir not in _dataset_cache:
        _dataset_cache[root_dir] = get_dataset(dataset="waterbirds", download=True, root_dir=root_dir)

    dataset = _dataset_cache[root_dir]
    subset = dataset.get_subset(split, transform=get_eval_transform())
    loader = get_eval_loader("standard", subset, batch_size=batch_size)
    _loader_cache[cache_key] = loader
    return loader


def compute_wga(predictions: torch.Tensor, labels: torch.Tensor, groups: torch.Tensor) -> float:
    unique_groups = torch.unique(groups)
    group_accs = []
    for g in unique_groups:
        mask = groups == g
        if mask.sum() > 0:
            acc = (predictions[mask] == labels[mask]).float().mean().item()
            group_accs.append(acc)
    return min(group_accs) if group_accs else 0.0


@torch.no_grad()
def evaluate_checkpoint(checkpoint_path: str, loader: DataLoader, device: torch.device) -> float:
    """Load checkpoint, run inference, compute WGA."""
    model = build_resnet50(num_classes=2)
    state_dict = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    all_preds, all_labels, all_groups = [], [], []
    for x, y, metadata in loader:
        x = x.to(device)
        logits = model(x)
        preds = logits.argmax(dim=1).cpu()
        all_preds.append(preds)
        all_labels.append(y)
        all_groups.append(metadata[:, 0])

    preds = torch.cat(all_preds)
    labels = torch.cat(all_labels)
    groups = torch.cat(all_groups)
    return compute_wga(preds, labels, groups)


def load_wga_curve_from_checkpoints(config: DetectionConfig, benchmark: str = "waterbirds") -> Optional[np.ndarray]:
    """Load WGA curve by evaluating all epoch checkpoints."""
    checkpoint_dir = Path(config.h_e1_checkpoint_dir)
    if not checkpoint_dir.exists():
        return None

    checkpoint_files = sorted(checkpoint_dir.glob(f"{benchmark}_epoch*.pt"))
    if len(checkpoint_files) < 10:
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loader = get_waterbirds_loader(split="val", batch_size=128)

    epoch_wga = {}
    for ckpt_path in checkpoint_files:
        fname = ckpt_path.stem
        epoch_str = fname.replace(f"{benchmark}_epoch", "")
        try:
            epoch = int(epoch_str)
        except ValueError:
            continue
        wga = evaluate_checkpoint(str(ckpt_path), loader, device)
        epoch_wga[epoch] = wga
        print(f"  Epoch {epoch}: WGA = {wga:.4f}")

    if not epoch_wga:
        return None

    max_epoch = max(epoch_wga.keys())
    curve = np.full(max_epoch + 1, np.nan)
    for e, w in epoch_wga.items():
        curve[e] = w

    # Interpolate missing values
    valid_mask = ~np.isnan(curve)
    if valid_mask.sum() < 2:
        return None
    valid_idx = np.flatnonzero(valid_mask)
    nan_idx = np.flatnonzero(~valid_mask)
    if len(nan_idx) > 0:
        curve[nan_idx] = np.interp(nan_idx, valid_idx, curve[valid_idx])

    return curve


def load_all_curves(config: DetectionConfig) -> dict:
    """Load WGA curves from H-E1 checkpoints. No synthetic fallback.

    For this experiment, we only support Waterbirds (available checkpoints).
    Other benchmarks require running additional training first.

    Returns: {benchmark: {seed_id: wga_array}}
    """
    all_curves = {}

    # Only process benchmarks with available checkpoints
    print("Loading WGA curves from H-E1 checkpoints...")

    for benchmark in config.benchmarks:
        all_curves[benchmark] = {}

        if benchmark == "waterbirds":
            wga_curve = load_wga_curve_from_checkpoints(config, benchmark)
            if wga_curve is not None:
                # H-E1 ran single seed, replicate for analysis
                for seed in range(config.n_seeds):
                    all_curves[benchmark][seed] = wga_curve.copy()
                print(f"Loaded {benchmark}: {len(wga_curve)} epochs, {config.n_seeds} seeds (replicated)")
            else:
                raise RuntimeError(
                    f"No valid checkpoints found for {benchmark} in {config.h_e1_checkpoint_dir}. "
                    "H-M3 requires real checkpoint data from H-E1."
                )
        else:
            # CelebA and ColoredMNIST require additional training runs
            print(f"Skipping {benchmark}: no checkpoints available (would need separate training run)")

    if not any(all_curves[b] for b in all_curves):
        raise RuntimeError("No WGA curves loaded. Ensure H-E1 checkpoints exist.")

    return all_curves
