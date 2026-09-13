"""
visualize.py — Figure generation for H-M1 attention entropy analysis.
"""
from __future__ import annotations

import logging
import os
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from analyze import MetricsAggregator, StatisticalResult

logger = logging.getLogger(__name__)


def plot_entropy_per_layer(
    results: List[StatisticalResult],
    aggregator: MetricsAggregator,
    model_label: str,
    save_path: str,
) -> None:
    """Line plot: entropy per layer for both conditions with SE shading; p<0.05 marked."""
    layer_metrics = aggregator.get_layer_metrics()
    layers = [lm.layer_idx for lm in layer_metrics]

    baseline_means = [np.mean(lm.baseline_entropy) if lm.baseline_entropy else 0.0 for lm in layer_metrics]
    proposed_means = [np.mean(lm.proposed_entropy) if lm.proposed_entropy else 0.0 for lm in layer_metrics]

    def se(vals):
        return np.std(vals) / np.sqrt(len(vals)) if len(vals) > 1 else 0.0

    baseline_se = [se(lm.baseline_entropy) for lm in layer_metrics]
    proposed_se = [se(lm.proposed_entropy) for lm in layer_metrics]
    sig_layers = [r.layer_idx for r in results if r.entropy_pvalue < 0.05]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(layers, baseline_means, label="Baseline", color="steelblue")
    ax.fill_between(layers,
                    np.array(baseline_means) - np.array(baseline_se),
                    np.array(baseline_means) + np.array(baseline_se),
                    alpha=0.2, color="steelblue")
    ax.plot(layers, proposed_means, label="Eviction-Aware", color="darkorange")
    ax.fill_between(layers,
                    np.array(proposed_means) - np.array(proposed_se),
                    np.array(proposed_means) + np.array(proposed_se),
                    alpha=0.2, color="darkorange")
    for sl in sig_layers:
        ax.axvline(x=sl, color="red", alpha=0.15, linewidth=0.8)
    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Attention Entropy (nats)")
    ax.set_title(f"Attention Entropy per Layer — {model_label}")
    ax.legend()
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {save_path}")


def plot_hh_concentration(
    results: List[StatisticalResult],
    aggregator: MetricsAggregator,
    model_label: str,
    save_path: str,
) -> None:
    """Line plot: HH concentration per layer; asterisks at significant layers."""
    layer_metrics = aggregator.get_layer_metrics()
    layers = [lm.layer_idx for lm in layer_metrics]
    baseline_means = [np.mean(lm.baseline_hh_concentration) if lm.baseline_hh_concentration else 0.0 for lm in layer_metrics]
    proposed_means = [np.mean(lm.proposed_hh_concentration) if lm.proposed_hh_concentration else 0.0 for lm in layer_metrics]
    sig_layers = {r.layer_idx for r in results if r.hh_pvalue < 0.05}

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(layers, baseline_means, label="Baseline", color="steelblue")
    ax.plot(layers, proposed_means, label="Eviction-Aware", color="darkorange")
    for i, l in enumerate(layers):
        if l in sig_layers:
            ymax = max(baseline_means[i], proposed_means[i])
            ax.annotate("*", xy=(l, ymax), ha="center", fontsize=12, color="red")
    ax.set_xlabel("Layer Index")
    ax.set_ylabel("HH Concentration (top-20%)")
    ax.set_title(f"Heavy-Hitter Concentration per Layer — {model_label}")
    ax.legend()
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {save_path}")


def plot_pvalue_heatmap(
    results: List[StatisticalResult],
    save_path: str,
) -> None:
    """Heatmap: layer x metric (-log10 p-value); p=0.05 threshold line."""
    layers = [r.layer_idx for r in results]
    entropy_vals = [-np.log10(max(r.entropy_pvalue, 1e-300)) for r in results]
    hh_vals = [-np.log10(max(r.hh_pvalue, 1e-300)) for r in results]
    data = np.array([entropy_vals, hh_vals])

    fig, ax = plt.subplots(figsize=(14, 3))
    im = ax.imshow(data, aspect="auto", cmap="YlOrRd", vmin=0)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Entropy", "HH Conc."])
    ax.set_xticks(range(len(layers)))
    ax.set_xticklabels(layers, fontsize=6)
    ax.set_xlabel("Layer Index")
    ax.set_title("-log10(p-value) Heatmap")
    plt.colorbar(im, ax=ax, label="-log10(p)")
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {save_path}")


def plot_entropy_by_category(
    aggregator: MetricsAggregator,
    save_path: str,
) -> None:
    """Bar plot: mean entropy for both conditions."""
    layer_metrics = aggregator.get_layer_metrics()
    if not layer_metrics:
        return
    baseline_vals = [v for lm in layer_metrics for v in lm.baseline_entropy]
    proposed_vals = [v for lm in layer_metrics for v in lm.proposed_entropy]
    if not baseline_vals or not proposed_vals:
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Baseline", "Eviction-Aware"],
           [float(np.mean(baseline_vals)), float(np.mean(proposed_vals))],
           color=["steelblue", "darkorange"], width=0.4)
    ax.set_ylabel("Mean Attention Entropy (nats)")
    ax.set_title("Mean Entropy: Baseline vs Eviction-Aware")
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {save_path}")


def plot_gate_summary(
    gate_result: dict,
    save_path: str,
) -> None:
    """Bar chart: % layers with p<0.05; target line at 50%."""
    fraction = gate_result.get("fraction_significant", 0.0)
    fig, ax = plt.subplots(figsize=(6, 4))
    color = "green" if gate_result.get("passed", False) else "salmon"
    ax.bar(["Significant Layers"], [fraction * 100], color=color, width=0.4)
    ax.axhline(y=50.0, color="red", linestyle="--", label="Gate threshold (50%)")
    ax.set_ylim(0, 110)
    ax.set_ylabel("% Layers with p < 0.05")
    gate_str = "PASS" if gate_result.get("passed", False) else "FAIL"
    ax.set_title(f"Gate Summary: {gate_str} ({fraction*100:.1f}% significant)")
    ax.legend()
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {save_path}")


def generate_all_figures(results_per_model: list, figures_dir: str) -> List[str]:
    """Generate all figures for all model pairs. Returns list of saved paths."""
    os.makedirs(figures_dir, exist_ok=True)
    saved = []
    for model_result in results_per_model:
        label = model_result["model_label"]
        stat_results_data = model_result.get("stat_results", [])
        aggregator = model_result.get("aggregator")
        gate = model_result.get("gate", {})
        if aggregator is None:
            continue
        stat_results = [StatisticalResult(**r) for r in stat_results_data]

        for fname, fn, args in [
            (f"entropy_per_layer_{label}.png", plot_entropy_per_layer, (stat_results, aggregator, label)),
            (f"hh_concentration_{label}.png", plot_hh_concentration, (stat_results, aggregator, label)),
            (f"pvalue_heatmap_{label}.png", plot_pvalue_heatmap, (stat_results,)),
            (f"entropy_by_category_{label}.png", plot_entropy_by_category, (aggregator,)),
            (f"gate_summary_{label}.png", plot_gate_summary, (gate,)),
        ]:
            path = os.path.join(figures_dir, fname)
            fn(*args, path)
            saved.append(path)
    return saved
