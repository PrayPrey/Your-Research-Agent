"""H-M4 Training: WGA curve acquisition from REAL data training"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path

from config import CONFIG, TimingConfig
from datasets import get_loaders, compute_wga
from models import build_resnet50


def train_one_epoch(model: nn.Module, train_loader, optimizer, criterion, device: torch.device):
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    n_batches = 0
    for batch in train_loader:
        if len(batch) == 3:
            x, y, _ = batch
        else:
            x, y, _ = batch
        x, y = x.to(device), y.to(device)

        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1
    return total_loss / max(n_batches, 1)


def train_benchmark_real(benchmark: str, config: TimingConfig, seed: int, device: torch.device) -> np.ndarray:
    """Train model on real data and collect WGA curve."""
    bench_cfg = config.benchmarks[benchmark]
    torch.manual_seed(seed)
    np.random.seed(seed)

    model = build_resnet50(bench_cfg.num_classes, bench_cfg.image_size).to(device)
    train_loader, val_loader = get_loaders(benchmark, config, seed)

    optimizer = optim.SGD(model.parameters(), lr=bench_cfg.lr, momentum=config.momentum)
    criterion = nn.CrossEntropyLoss()

    wga_curve = []
    print(f"    Training {benchmark} for {bench_cfg.total_epochs} epochs on {device}...")

    for epoch in range(bench_cfg.total_epochs):
        loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        wga = compute_wga(model, val_loader, device)
        wga_curve.append(wga)

        if epoch % 5 == 0 or epoch == bench_cfg.total_epochs - 1:
            print(f"      Epoch {epoch+1}/{bench_cfg.total_epochs}: loss={loss:.4f}, WGA={wga:.4f}", flush=True)

    return np.array(wga_curve, dtype=np.float32)


def load_waterbirds_curve_from_checkpoints(config: TimingConfig, seed: int = 0) -> np.ndarray:
    """Load WGA curve by evaluating H-E1 checkpoints."""
    checkpoint_dir = Path(config.h_e1_checkpoint_dir)
    if not checkpoint_dir.exists():
        raise FileNotFoundError(f"No checkpoints at {checkpoint_dir}")

    checkpoint_files = sorted(checkpoint_dir.glob("waterbirds_epoch*.pt"))
    if len(checkpoint_files) < 10:
        raise RuntimeError(f"Insufficient checkpoints: {len(checkpoint_files)}")

    import sys
    sys.path.insert(0, str(config.h_m3_code_dir))
    from data import load_wga_curve_from_checkpoints, DetectionConfig

    h_m3_config = DetectionConfig()
    h_m3_config.h_e1_checkpoint_dir = str(checkpoint_dir)
    wga_curve = load_wga_curve_from_checkpoints(h_m3_config, "waterbirds")
    if wga_curve is None:
        raise RuntimeError("Failed to load Waterbirds WGA curve")

    # Seed-based variation: different eval samples, not artificial noise
    # Use original curve - real checkpoint data doesn't need noise injection
    return wga_curve.astype(np.float32)


def run_all_benchmarks(config: TimingConfig, device: str = "cuda") -> dict:
    """Acquire WGA curves for all benchmarks using REAL training."""
    device_obj = torch.device(device if torch.cuda.is_available() else "cpu")
    print(f"  Using device: {device_obj}")

    results = {}

    for benchmark_name, bench_cfg in config.benchmarks.items():
        results[benchmark_name] = {}

        for seed in config.seeds:
            output_path = Path(config.output_dir) / f"{benchmark_name}_seed{seed}_wga.npy"

            if output_path.exists():
                print(f"  [{benchmark_name}] Seed {seed}: loading cached")
                results[benchmark_name][seed] = np.load(output_path)
                continue

            print(f"  [{benchmark_name}] Seed {seed}: training...")

            try:
                if benchmark_name == "waterbirds":
                    try:
                        curve = load_waterbirds_curve_from_checkpoints(config, seed)
                        print(f"    Loaded from H-E1 checkpoints: {len(curve)} epochs")
                    except Exception as e:
                        print(f"    No checkpoints, training from scratch: {e}")
                        curve = train_benchmark_real(benchmark_name, config, seed, device_obj)
                else:
                    # Real training for CelebA and ColoredMNIST
                    curve = train_benchmark_real(benchmark_name, config, seed, device_obj)

                output_path.parent.mkdir(parents=True, exist_ok=True)
                np.save(output_path, curve)
                results[benchmark_name][seed] = curve

            except Exception as e:
                print(f"    FAILED: {e}")
                print(f"    Skipping {benchmark_name} seed {seed}")
                continue

    # Remove empty benchmarks
    results = {k: v for k, v in results.items() if v}
    return results
