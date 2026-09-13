"""H-P0: DFR Backbone Identity Sanity Check.

Verifies that DFR and ERM ResNet-50 layer4 features are numerically identical
across 3 seed pairs on 50 fixed Waterbirds test images.
Gate: mean cosine similarity >= 0.9999 AND variance < 1e-6 for all seeds.
"""
import os
import sys
import json
import pathlib
import warnings
warnings.filterwarnings("ignore")

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from huggingface_hub import hf_hub_download
from wilds import get_dataset

# Add code dir to path for config import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C


def get_transform():
    """Standard ImageNet normalization transform."""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def load_test_images(n=C.N_IMAGES, seed=C.DATA_SEED, wilds_cache=C.WILDS_CACHE):
    """Load fixed subset of Waterbirds WILDS test images.

    Returns:
        images: (n, 3, 224, 224) float32 tensor
        background_labels: (n,) int64 tensor — group_array % 2 (0=land, 1=water)
    """
    print(f"Loading Waterbirds WILDS test split from {wilds_cache}...")
    dataset = get_dataset(dataset="waterbirds", download=False, root_dir=wilds_cache)
    test_data = dataset.get_subset("test", transform=get_transform())
    print(f"  Test split size: {len(test_data)} images")

    torch.manual_seed(seed)
    indices = torch.randperm(len(test_data))[:n]

    images = []
    labels = []
    for idx in indices.tolist():
        x, y, metadata = test_data[idx]
        images.append(x)
        labels.append(int(metadata[0]) % 2)  # group_array % 2 = background (0=land, 1=water)

    images = torch.stack(images)       # (n, 3, 224, 224)
    labels = torch.tensor(labels, dtype=torch.long)  # (n,)

    assert images.shape == C.EXPECTED_SHAPES["images"], f"Image shape wrong: {images.shape}"
    assert set(labels.tolist()).issubset({0, 1}), f"Unexpected label values: {set(labels.tolist())}"
    print(f"  Loaded {n} images (seed={seed}), labels: {labels.tolist()[:10]}...")
    return images, labels


def download_checkpoint(seed, method, hf_repo=C.HF_REPO, local_dir=C.CHECKPOINT_DIR):
    """Get checkpoint path — use local archive first, fall back to HuggingFace Hub."""
    # Try local archive first (pre-cached from previous pipeline runs)
    local_archive = pathlib.Path(C.LOCAL_CHECKPOINT_ARCHIVE) / f"{method}_seed{seed}.pt"
    if local_archive.exists():
        print(f"  Using cached checkpoint: {local_archive}")
        return local_archive

    # Fall back to HuggingFace download
    os.makedirs(local_dir, exist_ok=True)
    filename = C.CHECKPOINT_MAP[method][seed]
    print(f"  Downloading {method}_seed{seed}: {filename}")
    local_path = hf_hub_download(
        repo_id=hf_repo,
        filename=filename,
        local_dir=local_dir,
        repo_type="model",
    )
    return pathlib.Path(local_path)


def load_model(ckpt_path, device=C.DEVICE, n_classes=2):
    """Load ResNet-50 from izmailovpavel checkpoint."""
    model = torchvision.models.resnet50(weights=None)
    model.fc = nn.Linear(2048, n_classes)

    ckpt_dict = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    # Handle potential wrapper keys
    if isinstance(ckpt_dict, dict) and "model_state_dict" in ckpt_dict:
        ckpt_dict = ckpt_dict["model_state_dict"]
    elif isinstance(ckpt_dict, dict) and "model" in ckpt_dict:
        ckpt_dict = ckpt_dict["model"]
    elif isinstance(ckpt_dict, dict) and "state_dict" in ckpt_dict:
        ckpt_dict = ckpt_dict["state_dict"]

    model.load_state_dict(ckpt_dict)
    model = model.to(device)
    model.eval()
    return model


def extract_layer4_features(model, images, device=C.DEVICE):
    """Extract pooled layer4 features from ResNet-50.

    Args:
        images: (B, 3, 224, 224) float32
    Returns:
        features: (B, 2048) float32
    """
    captured = []

    def hook_fn(module, input, output):
        captured.append(output.detach().cpu())

    handle = model.layer4.register_forward_hook(hook_fn)
    with torch.no_grad():
        _ = model(images.to(device))
    handle.remove()

    feat = captured[0]  # (B, 2048, 7, 7)
    pool = nn.AdaptiveAvgPool2d((1, 1))
    feat = pool(feat).flatten(1)  # (B, 2048)

    assert feat.shape == C.EXPECTED_SHAPES["features"], f"Feature shape wrong: {feat.shape}"
    assert feat.norm(dim=1).min() > 0, "Features contain zero vectors"
    return feat


def compute_cosine_similarity(feat1, feat2):
    """Compute pairwise cosine similarity between two feature sets.

    Returns dict with mean, variance, per_sample.
    """
    sim = F.cosine_similarity(feat1, feat2, dim=1)  # (N,)
    return {
        "mean": sim.mean().item(),
        "variance": sim.var().item(),
        "per_sample": sim,
    }


def evaluate_gate(results):
    """Evaluate MUST_WORK gate for H-P0.

    Returns True iff all seeds pass mean >= GATE_MEAN_SIM AND variance < GATE_VARIANCE.
    """
    gate_passed = True
    for seed, r in results.items():
        if r["mean_cosine_sim"] < C.GATE_MEAN_SIM:
            gate_passed = False
            print(f"  FAIL seed {seed}: mean_cosine_sim={r['mean_cosine_sim']:.6f} < {C.GATE_MEAN_SIM}")
        if r["variance"] >= C.GATE_VARIANCE:
            gate_passed = False
            print(f"  FAIL seed {seed}: variance={r['variance']:.2e} >= {C.GATE_VARIANCE}")
    return gate_passed


def run_probe(features, background_labels):
    """Fit logistic regression probe on ERM features vs background label.

    Returns accuracy float.
    """
    X = features.numpy()
    y = background_labels.numpy()
    clf = LogisticRegression(solver="lbfgs", C=1e9, max_iter=1000, random_state=42)
    # With 50 samples use 5-fold CV for a fair estimate
    try:
        scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")
        return float(scores.mean())
    except Exception:
        # Fallback: train on all, report train accuracy (sanity only)
        clf.fit(X, y)
        return float(clf.score(X, y))


def save_figures(results, output_dir=None):
    """Save visualization figures."""
    if output_dir is None:
        output_dir = C.FIGURES_DIR
    os.makedirs(output_dir, exist_ok=True)

    seeds = sorted(results.keys())

    # Bar chart: mean cosine similarity per seed
    fig, ax = plt.subplots(figsize=(7, 4))
    means = [results[s]["mean_cosine_sim"] for s in seeds]
    bars = ax.bar([f"Seed {s}" for s in seeds], means, color="steelblue", width=0.5)
    ax.axhline(y=C.GATE_MEAN_SIM, color="red", linestyle="--", label=f"Gate threshold ({C.GATE_MEAN_SIM})")
    # Y-axis: zoom in around 1.0
    all_vals = means + [C.GATE_MEAN_SIM]
    ymin = max(0.998, min(all_vals) - 0.001)
    ax.set_ylim([ymin, 1.0005])
    ax.set_xlabel("Seed")
    ax.set_ylabel("Mean Cosine Similarity")
    ax.set_title("H-P0: DFR vs ERM Layer4 Feature Cosine Similarity")
    ax.legend()
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.00005,
                f"{val:.6f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cosine_similarity_per_seed.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Histogram: per-sample cosine similarity
    fig, axes = plt.subplots(1, len(seeds), figsize=(5 * len(seeds), 4), sharey=True)
    if len(seeds) == 1:
        axes = [axes]
    for ax, seed in zip(axes, seeds):
        per_sample = results[seed]["per_sample"].numpy()
        # Use auto bins; if all values identical, show as single bar
        # When all values nearly identical, show text instead of histogram
        data_range = per_sample.max() - per_sample.min()
        if data_range < 1e-5:
            ax.text(0.5, 0.5, f"All values ≈ {per_sample.mean():.8f}\n(range={data_range:.2e})",
                    ha="center", va="center", transform=ax.transAxes, fontsize=10)
            ax.set_xlim([0.999, 1.001])
        else:
            ax.hist(per_sample, bins=20, color="steelblue", edgecolor="black")
        ax.axvline(x=C.GATE_MEAN_SIM, color="red", linestyle="--", label="Gate")
        ax.set_title(f"Seed {seed} (n={len(per_sample)})")
        ax.set_xlabel("Cosine Similarity")
        if ax == axes[0]:
            ax.set_ylabel("Count")
    plt.suptitle("H-P0: Per-Sample Cosine Similarity Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "per_sample_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()

    print(f"  Figures saved to {output_dir}")


def save_results(results, gate_passed, probe_acc, output_dir=None):
    """Save results.json and 04_validation.md."""
    if output_dir is None:
        output_dir = os.path.dirname(C.OUTPUT_DIR)  # h-p0/

    os.makedirs(C.OUTPUT_DIR, exist_ok=True)

    # Build JSON-serializable results
    per_seed = {}
    for seed, r in results.items():
        per_seed[str(seed)] = {
            "mean_cosine_sim": r["mean_cosine_sim"],
            "variance": r["variance"],
        }

    result_obj = {
        "hypothesis_id": "h-p0",
        "gate_passed": gate_passed,
        "gate_threshold_mean_sim": C.GATE_MEAN_SIM,
        "gate_threshold_variance": C.GATE_VARIANCE,
        "per_seed": per_seed,
        "secondary_probe_accuracy": probe_acc,
        "conclusion": f"{'PASS' if gate_passed else 'FAIL'}: DFR and ERM backbones are {'numerically identical' if gate_passed else 'NOT identical — redesign H-M3 needed'}",
    }

    results_path = os.path.join(C.OUTPUT_DIR, "similarity_results.json")
    with open(results_path, "w") as f:
        json.dump(result_obj, f, indent=2)
    print(f"  Results saved to {results_path}")

    # Also save to h-p0/ root for pipeline compatibility
    root_results_path = os.path.join(os.path.dirname(C.OUTPUT_DIR), "results.json")
    with open(root_results_path, "w") as f:
        json.dump(result_obj, f, indent=2)

    return result_obj


def main():
    """Orchestrate full H-P0 sanity check experiment."""
    print("=" * 60)
    print("H-P0: DFR Backbone Identity Sanity Check")
    print("=" * 60)
    print(f"Device: {C.DEVICE}")

    os.makedirs(C.OUTPUT_DIR, exist_ok=True)
    os.makedirs(C.FIGURES_DIR, exist_ok=True)
    os.makedirs(C.CHECKPOINT_DIR, exist_ok=True)

    # Load fixed test images once
    images, background_labels = load_test_images()

    results = {}
    erm_features_seed1 = None

    for seed in C.SEEDS:
        print(f"\n--- Seed {seed} ---")

        # ERM checkpoint
        erm_ckpt = download_checkpoint(seed=seed, method="erm")
        erm_model = load_model(erm_ckpt)
        erm_feats = extract_layer4_features(erm_model, images)
        del erm_model

        # DFR checkpoint
        dfr_ckpt = download_checkpoint(seed=seed, method="dfr")
        dfr_model = load_model(dfr_ckpt)
        dfr_feats = extract_layer4_features(dfr_model, images)
        del dfr_model

        # Cosine similarity
        sim = compute_cosine_similarity(erm_feats, dfr_feats)
        results[seed] = {
            "mean_cosine_sim": sim["mean"],
            "variance": sim["variance"],
            "per_sample": sim["per_sample"],
            "erm_feats": erm_feats,
        }
        print(f"  mean_cosine_sim={sim['mean']:.8f}, variance={sim['variance']:.2e}")

        if seed == 1:
            erm_features_seed1 = erm_feats

    # Gate evaluation
    print("\n--- Gate Evaluation ---")
    gate_passed = evaluate_gate(results)
    print(f"H-P0 Gate: {'PASS' if gate_passed else 'FAIL'}")

    # Secondary: ERM probe accuracy
    print("\n--- Secondary Validation: ERM Background Probe ---")
    probe_acc = run_probe(erm_features_seed1, background_labels)
    print(f"ERM probe accuracy (background): {probe_acc:.3f}")

    # Save outputs
    print("\n--- Saving Outputs ---")
    save_figures(results)
    result_obj = save_results(results, gate_passed, probe_acc)

    print("\n" + "=" * 60)
    print(f"CONCLUSION: {result_obj['conclusion']}")
    print("=" * 60)
    return gate_passed


if __name__ == "__main__":
    main()
