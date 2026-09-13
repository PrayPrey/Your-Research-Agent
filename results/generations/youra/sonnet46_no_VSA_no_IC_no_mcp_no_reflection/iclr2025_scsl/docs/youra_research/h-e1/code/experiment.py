"""H-E1: Gradient Alignment Signal Existence Verification.

Tests whether per-sample last-layer gradient alignment ROC-AUC exceeds
per-sample loss ROC-AUC for predicting spurious-minority group membership.
"""

from __future__ import annotations
import argparse
import json
import os
import random
import sys

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.func import functional_call, vmap, grad
from torch.optim import SGD
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, roc_curve
import torchvision.models as tvm
from tqdm import tqdm

from config import DatasetConfig, WATERBIRDS_CONFIG, CELEBA_CONFIG
from data.dataset import get_loaders


# ─── Reproducibility ────────────────────────────────────────────────────────

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ─── Model ──────────────────────────────────────────────────────────────────

def build_model(n_classes: int, device: torch.device) -> nn.Module:
    """ResNet-50 ImageNet pretrained, last layer replaced to Linear(2048, n_classes)."""
    model = tvm.resnet50(weights=tvm.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, n_classes)
    return model.to(device)


# ─── Training ───────────────────────────────────────────────────────────────

def train_epoch(model: nn.Module, loader: DataLoader,
                optimizer: SGD, device: torch.device) -> float:
    model.train()
    total_loss = 0.0
    n = 0
    for x, y, _ in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = F.cross_entropy(logits, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * x.size(0)
        n += x.size(0)
    return total_loss / n


# ─── Per-sample gradient probe ───────────────────────────────────────────────

def _extract_fc_params(model: nn.Module) -> tuple[dict, dict]:
    """Extract last-layer (fc) parameters and all model buffers."""
    fc_params = {
        name: param.detach()
        for name, param in model.named_parameters()
        if name.startswith('fc.')
    }
    all_buffers = dict(model.named_buffers())
    return fc_params, all_buffers


def _per_sample_loss(fc_params: dict, all_buffers: dict,
                     model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Cross-entropy loss for a single sample using functional_call."""
    x_batch = x.unsqueeze(0)
    y_batch = y.unsqueeze(0)
    merged_params = {**dict(model.named_parameters()), **fc_params}
    logits = functional_call(model, (merged_params, all_buffers), (x_batch,))
    return F.cross_entropy(logits, y_batch)


def compute_probe(model: nn.Module, loader: DataLoader,
                  device: torch.device) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute per-sample alignment and loss scores over the full training set.

    Returns:
        alignment_scores: (N,) negated cosine similarity (high = spurious-minority)
        loss_scores:      (N,) per-sample cross-entropy loss
        group_ids:        (N,) group membership labels
    """
    model.eval()
    fc_params, all_buffers = _extract_fc_params(model)
    fc_params   = {k: v.to(device) for k, v in fc_params.items()}
    all_buffers = {k: v.to(device) for k, v in all_buffers.items()}

    # Capture buffers and model via closure — vmap only vectorizes over fc_params, x, y
    def _loss_fn_closed(fc_p, x, y):
        return _per_sample_loss(fc_p, all_buffers, model, x, y)

    _grad_fn  = grad(_loss_fn_closed, argnums=0)
    _vmap_grad = vmap(_grad_fn, in_dims=(None, 0, 0))

    all_alignments, all_losses, all_groups = [], [], []
    for x_batch, y_batch, group_batch in tqdm(loader, desc="probe", leave=False):
        x_batch = x_batch.to(device)
        y_batch = y_batch.to(device)

        per_sample_grads = _vmap_grad(fc_params, x_batch, y_batch)

        # Flatten to (B, D)
        g_flat = torch.cat([
            v.flatten(start_dim=1) for v in per_sample_grads.values()
        ], dim=1)

        # Per-batch mean gradient
        # ponytail: per-batch mean approximates global mean; upgrade to two-pass if noisy
        g_mean = g_flat.mean(dim=0, keepdim=True)

        cos_sim   = F.cosine_similarity(g_flat, g_mean.expand_as(g_flat), dim=1)
        alignment = -cos_sim  # negate: low alignment → high predictor score

        with torch.no_grad():
            logits = model(x_batch)
            loss   = F.cross_entropy(logits, y_batch, reduction='none')

        all_alignments.append(alignment.detach().cpu().numpy())
        all_losses.append(loss.cpu().numpy())
        all_groups.append(group_batch.numpy())

    return (
        np.concatenate(all_alignments),
        np.concatenate(all_losses),
        np.concatenate(all_groups),
    )


# ─── ROC-AUC evaluation ──────────────────────────────────────────────────────

def evaluate_roc_auc(scores: np.ndarray, group_ids: np.ndarray,
                     minority_group_ids: frozenset) -> float:
    y_binary = np.isin(group_ids, list(minority_group_ids)).astype(int)
    minority_count = y_binary.sum()
    if minority_count == 0 or minority_count == len(y_binary):
        raise ValueError(
            f"Degenerate binary labels: minority={minority_count}, N={len(y_binary)}. "
            f"Check minority_group_ids={minority_group_ids}."
        )
    return float(roc_auc_score(y_binary, scores))


# ─── Run one dataset ────────────────────────────────────────────────────────

def run_dataset(cfg: DatasetConfig, device: torch.device,
                wilds_root: str, output_dir: Path) -> list[dict]:
    print(f"\n{'='*60}")
    print(f"Dataset: {cfg.name.upper()}")
    print(f"  epochs={cfg.n_epochs}, lr={cfg.lr}, batch={cfg.batch_size}")
    print(f"  checkpoint_epochs={cfg.checkpoint_epochs}")
    print(f"  minority_group_ids={cfg.minority_group_ids}")
    print(f"{'='*60}")

    set_seed(cfg.seed)
    train_loader, _, _, train_eval_loader = get_loaders(cfg, wilds_root)

    model = build_model(cfg.n_classes, device)
    optimizer = SGD(model.parameters(), lr=cfg.lr, momentum=0.9, weight_decay=1e-4)

    checkpoint_set = set(cfg.checkpoint_epochs)
    results = []
    probe_data_by_epoch = {}

    for epoch in range(1, cfg.n_epochs + 1):
        loss_val = train_epoch(model, train_loader, optimizer, device)

        if epoch in checkpoint_set:
            print(f"\nEpoch {epoch}: train_loss={loss_val:.4f} — computing probe...")
            alignment_scores, loss_scores, group_ids = compute_probe(
                model, train_eval_loader, device
            )

            align_auc = evaluate_roc_auc(alignment_scores, group_ids, cfg.minority_group_ids)
            loss_auc  = evaluate_roc_auc(loss_scores, group_ids, cfg.minority_group_ids)
            wins      = align_auc > loss_auc

            row = {
                "dataset":           cfg.name,
                "epoch":             epoch,
                "alignment_roc_auc": align_auc,
                "loss_roc_auc":      loss_auc,
                "alignment_wins":    wins,
                "train_loss":        loss_val,
            }
            results.append(row)
            probe_data_by_epoch[epoch] = {
                "alignment_scores": alignment_scores,
                "loss_scores":      loss_scores,
                "group_ids":        group_ids,
            }

            print(f"  alignment_roc_auc={align_auc:.4f}  loss_roc_auc={loss_auc:.4f}  wins={wins}")

        if epoch in checkpoint_set and epoch == max(checkpoint_set):
            break  # don't train beyond last probe epoch if no reason to

    # Visualizations
    _plot_roc_auc_vs_epoch([r for r in results if r["dataset"] == cfg.name], output_dir, cfg.name)
    if 5 in probe_data_by_epoch:
        _plot_score_distribution(probe_data_by_epoch[5], output_dir, cfg.name, cfg.minority_group_ids)
    best_epoch = max(results, key=lambda r: r["alignment_roc_auc"])["epoch"]
    if best_epoch in probe_data_by_epoch:
        _plot_roc_curves(probe_data_by_epoch[best_epoch], output_dir, cfg.name, cfg.minority_group_ids, best_epoch)

    return results


# ─── Visualization ──────────────────────────────────────────────────────────

def _plot_roc_auc_vs_epoch(results: list[dict], output_dir: Path, dataset_name: str) -> None:
    epochs     = [r["epoch"]             for r in results]
    align_aucs = [r["alignment_roc_auc"] for r in results]
    loss_aucs  = [r["loss_roc_auc"]      for r in results]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(epochs, align_aucs, 'b-o', label='Alignment ROC-AUC')
    ax.plot(epochs, loss_aucs,  'r-s', label='Loss ROC-AUC')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('ROC-AUC')
    ax.set_title(f'{dataset_name.capitalize()}: Alignment vs Loss ROC-AUC')
    ax.legend()
    ax.grid(True, alpha=0.3)
    path = output_dir / f'roc_auc_vs_epoch_{dataset_name}.png'
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def _plot_score_distribution(probe_data: dict, output_dir: Path,
                              dataset_name: str, minority_group_ids: frozenset) -> None:
    alignment = probe_data["alignment_scores"]
    group_ids = probe_data["group_ids"]
    minority_mask = np.isin(group_ids, list(minority_group_ids))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.violinplot([alignment[~minority_mask], alignment[minority_mask]], positions=[0, 1])
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Majority', 'Minority'])
    ax.set_ylabel('Alignment Score (negated cos sim)')
    ax.set_title(f'{dataset_name.capitalize()}: Score Distribution at Epoch 5')
    path = output_dir / f'score_distribution_epoch5_{dataset_name}.png'
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def _plot_roc_curves(probe_data: dict, output_dir: Path,
                     dataset_name: str, minority_group_ids: frozenset, epoch: int) -> None:
    alignment = probe_data["alignment_scores"]
    loss      = probe_data["loss_scores"]
    group_ids = probe_data["group_ids"]
    y_binary  = np.isin(group_ids, list(minority_group_ids)).astype(int)

    fpr_a, tpr_a, _ = roc_curve(y_binary, alignment)
    fpr_l, tpr_l, _ = roc_curve(y_binary, loss)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr_a, tpr_a, label='Alignment')
    ax.plot(fpr_l, tpr_l, label='Loss')
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.4)
    ax.set_xlabel('FPR')
    ax.set_ylabel('TPR')
    ax.set_title(f'{dataset_name.capitalize()}: ROC Curves (Epoch {epoch})')
    ax.legend()
    path = output_dir / f'roc_curves_best_epoch_{dataset_name}.png'
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


# ─── Combined 2×1 plot ───────────────────────────────────────────────────────

def plot_combined_roc_auc(all_results: list[dict], output_dir: Path) -> None:
    wb = [r for r in all_results if r["dataset"] == "waterbirds"]
    ca = [r for r in all_results if r["dataset"] == "celeba"]

    fig, axes = plt.subplots(2, 1, figsize=(7, 8))
    for ax, rows, title in zip(axes, [wb, ca], ["Waterbirds", "CelebA"]):
        epochs     = [r["epoch"]             for r in rows]
        align_aucs = [r["alignment_roc_auc"] for r in rows]
        loss_aucs  = [r["loss_roc_auc"]      for r in rows]
        ax.plot(epochs, align_aucs, 'b-o', label='Alignment ROC-AUC')
        ax.plot(epochs, loss_aucs,  'r-s', label='Loss ROC-AUC')
        ax.set_title(title)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('ROC-AUC')
        ax.legend()
        ax.grid(True, alpha=0.3)

    fig.suptitle('H-E1: Alignment vs Loss ROC-AUC', fontsize=13)
    fig.tight_layout()
    path = output_dir / 'roc_auc_vs_epoch.png'
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"\nSaved combined figure: {path}")


# ─── Results I/O ────────────────────────────────────────────────────────────

def save_results(results: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {path}")


# ─── Gate evaluation ────────────────────────────────────────────────────────

def evaluate_gate(all_results: list[dict]) -> dict:
    wb = [r for r in all_results if r["dataset"] == "waterbirds"]
    ca = [r for r in all_results if r["dataset"] == "celeba"]

    wb_wins = [r["alignment_wins"] for r in wb]
    ca_wins = [r["alignment_wins"] for r in ca]

    wb_any_win = any(wb_wins)
    ca_any_win = any(ca_wins)
    gate_satisfied = wb_any_win and ca_any_win

    return {
        "gate_type":       "MUST_WORK",
        "gate_satisfied":  gate_satisfied,
        "waterbirds_wins": wb_wins,
        "celeba_wins":     ca_wins,
        "waterbirds_any_win": wb_any_win,
        "celeba_any_win":     ca_any_win,
        "all_results":        all_results,
    }


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wilds-root',      default='/home/PrayPrey/.wilds_cache')
    parser.add_argument('--wilds-root-celeba', default='/home/PrayPrey/.wilds')
    parser.add_argument('--output-dir',      default='./outputs')
    parser.add_argument('--figures-dir',     default='../figures')
    parser.add_argument('--results-file',    default='./outputs/results.csv')
    parser.add_argument('--experiment-json', default='../experiment_results.json')
    parser.add_argument('--dataset',         default='both', choices=['waterbirds', 'celeba', 'both'])
    parser.add_argument('--device',          default='cuda' if torch.cuda.is_available() else 'cpu')
    args = parser.parse_args()

    device     = torch.device(args.device)
    output_dir = Path(args.output_dir)
    fig_dir    = Path(args.figures_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    print(f"Device: {device}")
    if device.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(device)}")

    all_results = []

    if args.dataset in ('waterbirds', 'both'):
        import dataclasses
        wb_cfg = dataclasses.replace(WATERBIRDS_CONFIG,
                                     root_dir=f"{args.wilds_root}/waterbirds_v1.0")
        wb_results = run_dataset(wb_cfg, device, args.wilds_root, fig_dir)
        all_results.extend(wb_results)

    if args.dataset in ('celeba', 'both'):
        import dataclasses
        ca_cfg = dataclasses.replace(CELEBA_CONFIG,
                                     root_dir=f"{args.wilds_root_celeba}/celebA_v1.0")
        ca_results = run_dataset(ca_cfg, device, args.wilds_root_celeba, fig_dir)
        all_results.extend(ca_results)

    # Combined figure
    plot_combined_roc_auc(all_results, fig_dir)

    # Gate evaluation
    gate = evaluate_gate(all_results)

    # Save results
    save_results(all_results, output_dir / 'results.json')

    # Save experiment_results.json (for pipeline)
    experiment_results = {
        "status": "completed",
        "gate_type": "MUST_WORK",
        "gate_satisfied": gate["gate_satisfied"],
        "results": all_results,
        "metrics": {
            "waterbirds_any_alignment_win": gate["waterbirds_any_win"],
            "celeba_any_alignment_win":     gate["celeba_any_win"],
        }
    }
    with open(args.experiment_json, 'w') as f:
        json.dump(experiment_results, f, indent=2)

    # Save CSV for pipeline
    import csv
    csv_path = Path(args.results_file)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if all_results:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)

    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    for r in all_results:
        status = "✓ WINS" if r["alignment_wins"] else "✗ LOSES"
        print(f"  {r['dataset']:12s} epoch={r['epoch']:3d}: "
              f"align={r['alignment_roc_auc']:.4f}  loss={r['loss_roc_auc']:.4f}  {status}")

    print()
    print(f"Gate (MUST_WORK): {'PASS ✓' if gate['gate_satisfied'] else 'FAIL ✗'}")
    print(f"  Waterbirds alignment wins ≥1 epoch: {gate['waterbirds_any_win']}")
    print(f"  CelebA alignment wins ≥1 epoch:     {gate['celeba_any_win']}")

    sys.exit(0 if gate['gate_satisfied'] else 1)


if __name__ == '__main__':
    main()
