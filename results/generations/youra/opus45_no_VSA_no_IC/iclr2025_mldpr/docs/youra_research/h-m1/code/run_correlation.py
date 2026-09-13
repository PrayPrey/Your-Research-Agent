#!/usr/bin/env python3
"""H-M1: BFS-Gap Correlation Analysis.

Tests whether Benchmark Fingerprint Score (BFS) correlates with cross-dataset
performance gap. Uses H-E1 artifacts: finetuned checkpoints + probe features.

Gate: SHOULD_WORK - r > 0.3 and p < 0.05 for positive correlation.
"""
import sys
from pathlib import Path

# Add H-E1 code to path for imports
h_e1_code = Path(__file__).parent.parent.parent / "h-e1" / "code"
sys.path.insert(0, str(h_e1_code))

import json
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from sklearn.linear_model import LogisticRegression
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from glob import glob
from tqdm import tqdm

from model import FeatureResNet50
from data import build_dataloader, DATASET_NUM_CLASSES
from config import Config as E1Config

torch.backends.cudnn.enabled = False


def load_h_e1_probe_classifier(feature_dir: str, probe_C: float, probe_max_iter: int):
    """Retrain H-E1's fingerprint classifier on saved features."""
    features = np.load(f"{feature_dir}/features.npy")
    labels = np.load(f"{feature_dir}/labels.npy")
    model_ids = np.load(f"{feature_dir}/model_ids.npy")

    clf = LogisticRegression(C=probe_C, max_iter=probe_max_iter, n_jobs=-1)
    clf.fit(features, labels)
    return clf, features, labels, model_ids


def compute_bfs(clf, features: np.ndarray, model_ids: np.ndarray,
                model_idx: int, true_benchmark_idx: int) -> float:
    """BFS = mean predict_proba confidence for true benchmark class."""
    mask = model_ids == model_idx
    feats = features[mask]
    if len(feats) == 0:
        return 0.0
    probs = clf.predict_proba(feats)
    return float(probs[:, true_benchmark_idx].mean())


def train_transfer_head(model: nn.Module, train_loader, device, num_classes, epochs=5, lr=0.01):
    """Train linear head on cross-dataset with frozen backbone."""
    head = nn.Linear(2048, num_classes).to(device)
    opt = SGD(head.parameters(), lr=lr, momentum=0.9)
    criterion = nn.CrossEntropyLoss()

    model.eval()
    for _ in range(epochs):
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            with torch.no_grad():
                feats = model.extract_features(x)
            logits = head(feats)
            loss = criterion(logits, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
    return head


def evaluate_transfer(model: nn.Module, head: nn.Linear, test_loader, device) -> float:
    """Evaluate transfer accuracy with trained head."""
    model.eval()
    head.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            feats = model.extract_features(x)
            logits = head(feats)
            preds = logits.argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)
    return correct / total if total > 0 else 0.0


def run_correlation(bfs_array: np.ndarray, gap_array: np.ndarray):
    """Pearson r and p-value."""
    r, p = pearsonr(bfs_array, gap_array)
    return float(r), float(p)


def plot_bfs_gap_scatter(bfs_array, gap_array, r, p, save_path, labels=None):
    """Scatter plot with regression line."""
    plt.figure(figsize=(8, 6))
    plt.scatter(bfs_array, gap_array, s=100, alpha=0.7)

    if labels:
        for i, lbl in enumerate(labels):
            plt.annotate(lbl, (bfs_array[i], gap_array[i]),
                        textcoords="offset points", xytext=(5, 5), fontsize=8)

    slope, intercept = np.polyfit(bfs_array, gap_array, 1)
    x_line = np.linspace(min(bfs_array), max(bfs_array), 100)
    plt.plot(x_line, slope * x_line + intercept, 'r--', alpha=0.8)

    plt.xlabel('Benchmark Fingerprint Score (BFS)', fontsize=12)
    plt.ylabel('Performance Gap (In-domain - NABirds)', fontsize=12)
    plt.title(f'BFS vs Performance Gap\nr = {r:.3f}, p = {p:.4f}', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved scatter plot to {save_path}")


def main():
    e1_cfg = E1Config()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    h_e1_dir = h_e1_code
    data_root = h_e1_dir / "data"
    output_dir = Path(__file__).parent

    ckpt_dir = h_e1_dir / "models" / "finetuned"
    feature_dir = h_e1_dir / "features"

    ckpt_paths = sorted(glob(str(ckpt_dir / "*.pt")))
    if not ckpt_paths:
        raise RuntimeError(f"No checkpoints found in {ckpt_dir}")
    print(f"Found {len(ckpt_paths)} checkpoints")

    print("Loading probe classifier...")
    clf, features, labels, model_ids = load_h_e1_probe_classifier(
        str(feature_dir), e1_cfg.probe_C, e1_cfg.probe_max_iter
    )

    benchmarks_found = set()
    for p in ckpt_paths:
        name = Path(p).stem.rsplit('_seed', 1)[0]
        benchmarks_found.add(name)
    benchmarks = sorted(benchmarks_found)
    benchmark_to_idx = {b: i for i, b in enumerate(benchmarks)}
    print(f"Benchmarks: {benchmarks}")

    cross_loaders = {}
    for b in benchmarks:
        if b == "flowers":
            cross_loaders[b] = {
                "train": build_dataloader("flowers", str(data_root), train=True, batch_size=32, num_workers=4),
                "test": build_dataloader("flowers", str(data_root), train=False, batch_size=32, num_workers=4),
            }
        elif b == "cifar100":
            from torchvision import datasets, transforms
            transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])
            cifar_train = datasets.CIFAR100(str(data_root), train=True, transform=transform, download=False)
            cifar_test = datasets.CIFAR100(str(data_root), train=False, transform=transform, download=False)
            cross_loaders[b] = {
                "train": torch.utils.data.DataLoader(cifar_train, batch_size=32, shuffle=True, num_workers=4),
                "test": torch.utils.data.DataLoader(cifar_test, batch_size=32, shuffle=False, num_workers=4),
            }

    bfs_scores, gaps, model_meta = [], [], []

    for model_idx, ckpt_path in enumerate(tqdm(ckpt_paths, desc="Processing models")):
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
        benchmark = ckpt["benchmark"]
        seed = ckpt["seed"]
        in_domain_acc = ckpt["acc"]

        true_idx = benchmark_to_idx.get(benchmark, 0)
        bfs = compute_bfs(clf, features, model_ids, model_idx, true_idx)

        if benchmark in DATASET_NUM_CLASSES:
            num_classes = DATASET_NUM_CLASSES[benchmark]
        elif benchmark == "cifar100":
            num_classes = 100
        else:
            num_classes = 102

        model = FeatureResNet50(num_classes, pretrained=False)
        model.load_state_dict(ckpt["state_dict"])
        model.to(device).eval()

        cross_benchmark = "cifar100" if benchmark == "flowers" else "flowers"
        cross_num_classes = 100 if cross_benchmark == "cifar100" else 102
        cross_train = cross_loaders[cross_benchmark]["train"]
        cross_test = cross_loaders[cross_benchmark]["test"]

        print(f"\n[{benchmark} seed={seed}] Training transfer head for {cross_benchmark}...")
        head = train_transfer_head(model, cross_train, device, cross_num_classes, epochs=3)
        transfer_acc = evaluate_transfer(model, head, cross_test, device)

        gap = in_domain_acc - transfer_acc

        bfs_scores.append(bfs)
        gaps.append(gap)
        model_meta.append({
            "benchmark": benchmark,
            "seed": int(seed),
            "bfs": bfs,
            "in_domain_acc": in_domain_acc,
            "transfer_acc": transfer_acc,
            "cross_benchmark": cross_benchmark,
            "gap": gap,
        })
        print(f"[{benchmark} seed={seed}] BFS={bfs:.4f}, in_domain={in_domain_acc:.4f}, "
              f"transfer={transfer_acc:.4f}, gap={gap:.4f}")

    bfs_array = np.array(bfs_scores)
    gap_array = np.array(gaps)

    if len(bfs_array) < 2:
        raise RuntimeError(f"Need at least 2 models for correlation, got {len(bfs_array)}")
    if np.std(bfs_array) < 1e-6 or np.std(gap_array) < 1e-6:
        print("WARNING: Near-zero variance in BFS or Gap scores")

    r, p = run_correlation(bfs_array, gap_array)
    print(f"\nCorrelation: r = {r:.4f}, p = {p:.4f}")

    gate_pass = bool(r > 0.3 and p < 0.05)
    print(f"Gate (r>0.3 and p<0.05): {'PASS' if gate_pass else 'FAIL'}")

    labels_for_plot = [f"{m['benchmark']}_s{m['seed']}" for m in model_meta]
    plot_bfs_gap_scatter(
        bfs_array, gap_array, r, p,
        str(output_dir / "figures" / "bfs_gap_scatter.png"),
        labels=labels_for_plot
    )

    results = {
        "per_model": model_meta,
        "pearson_r": r,
        "p_value": p,
        "n_models": len(bfs_array),
        "gate_pass": gate_pass,
        "gate_threshold": {"r": 0.3, "p": 0.05},
    }

    results_path = output_dir / "results" / "experiment_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved results to {results_path}")

    return results


def demo():
    """Sanity check on synthetic data."""
    rng = np.random.RandomState(42)
    fake_bfs = rng.uniform(0.5, 1.0, size=15)
    fake_gap = fake_bfs * 0.4 + rng.normal(0, 0.03, size=15)
    r, p = run_correlation(fake_bfs, fake_gap)
    assert r > 0.3 and p < 0.05, f"Sanity check failed: r={r}, p={p}"
    print("demo() OK: correlation pipeline works on synthetic data")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run sanity check only")
    args = parser.parse_args()

    if args.demo:
        demo()
    else:
        results = main()
        sys.exit(0 if results["gate_pass"] else 1)
