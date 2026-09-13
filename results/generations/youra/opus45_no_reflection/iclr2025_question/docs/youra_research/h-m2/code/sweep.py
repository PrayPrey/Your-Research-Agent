"""Sweep: Layer-wise probe training + bootstrap CI + inverted-U verification."""

import numpy as np
from sklearn.metrics import roc_auc_score

from probe import LinearProbe, train_probe, evaluate_auroc


def run_layer_sweep(
    train_states: dict,
    train_labels,
    val_states: dict,
    val_labels,
    cfg,
) -> dict:
    """Train+eval one LinearProbe per layer. Returns {layer_idx: {"auroc", "probe", "losses", "preds", "labels_np"}}."""
    results = {}
    layer_indices = sorted(train_states.keys())

    for idx in layer_indices:
        print(f"\n=== Training probe for layer {idx} ===")
        probe, losses = train_probe(train_states[idx], train_labels, cfg)
        auroc, preds, labels_np = evaluate_auroc(probe, val_states[idx], val_labels)
        print(f"Layer {idx}: AUROC = {auroc:.4f}")

        results[idx] = {
            "auroc": auroc,
            "probe": probe,
            "losses": losses,
            "preds": preds,
            "labels_np": labels_np,
        }

    return results


def bootstrap_auroc_ci(
    labels: np.ndarray,
    preds: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple:
    """Percentile bootstrap 95% CI on AUROC. Returns (ci_low, ci_high)."""
    rng = np.random.default_rng(seed)
    n = len(labels)
    scores = []

    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        if len(np.unique(labels[idx])) < 2:
            continue
        scores.append(roc_auc_score(labels[idx], preds[idx]))

    if len(scores) < 10:
        return 0.0, 1.0

    return np.percentile(scores, 2.5), np.percentile(scores, 97.5)


def verify_inverted_u_pattern(
    layer_aurocs: dict,
    num_layers: int = 32,
) -> dict:
    """Gate check: compare early(~25%), middle(~60%), final(100%) AUROC."""
    layers = sorted(layer_aurocs.keys())
    early, middle, final = layers[1], layers[4], layers[-1]

    auroc_early = layer_aurocs[early]
    auroc_middle = layer_aurocs[middle]
    auroc_final = layer_aurocs[final]

    middle_beats_final = auroc_middle > auroc_final
    middle_beats_early = auroc_middle > auroc_early

    peak_layer = max(layer_aurocs, key=layer_aurocs.get)
    peak_depth_pct = (peak_layer + 1) / num_layers * 100

    return {
        "early_layer": early,
        "middle_layer": middle,
        "final_layer": final,
        "auroc_early": auroc_early,
        "auroc_middle": auroc_middle,
        "auroc_final": auroc_final,
        "middle_beats_final": middle_beats_final,
        "middle_beats_early": middle_beats_early,
        "peak_layer": peak_layer,
        "peak_depth_pct": peak_depth_pct,
        "inverted_u_detected": middle_beats_final and middle_beats_early,
        "gate_satisfied": middle_beats_final,
    }
