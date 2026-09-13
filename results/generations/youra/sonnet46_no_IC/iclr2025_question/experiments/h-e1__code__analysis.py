"""h-e1 analysis: degeneracy screen, corrected AUROC, gate, mechanism verify (A-5)."""
import json
import logging
import math
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from constants import (AUROC_GATE, BASELINE_TOLERANCE, DEGENERACY_AGREEMENT_MIN,
                       DEGENERACY_ENTROPY_PCT, H_E1_REFERENCES, N_LAYERS, RESULTS_DIR)

log = logging.getLogger("h_e1.analysis")
SIGNALS = ["entropy", "maxprob", "adj_kl"]


def degeneracy_screen(entropy_grid, top1_agreement, vocab_size):
    """Drop layer if mean entropy within 1% of ln|V| OR top1_agreement < 5%.
    Returns retained 0-indexed layers (FR-4.1)."""
    ln_V = math.log(vocab_size)
    mean_entropy = np.nanmean(entropy_grid, axis=0)   # (32,)
    return [l for l in range(N_LAYERS) if not (
        abs(mean_entropy[l] - ln_V) / ln_V < DEGENERACY_ENTROPY_PCT
        or top1_agreement[l] < DEGENERACY_AGREEMENT_MIN)]


def corrected_auroc(labels, scores):
    """(max(auc, 1-auc), was_flipped). Logs raw direction (R8).
    Caller must pre-filter NaN scores."""
    raw_auc = roc_auc_score(labels, scores)
    flipped = raw_auc < 0.5
    log.info(f"raw_auc={raw_auc:.4f} flipped={flipped}")
    return max(raw_auc, 1 - raw_auc), flipped


def build_auroc_grid(cache_df, retained_layers):
    """(n_retained, 3) corrected AUROC per layer x signal, selection split only."""
    sel = cache_df[cache_df["split"] == "selection"]
    labels = sel["label"].to_numpy()
    grid = np.full((len(retained_layers), 3), np.nan)
    for i, l in enumerate(retained_layers):
        for j, sig in enumerate(SIGNALS):
            col = sel[f"{sig}_L{l + 1}"].to_numpy()
            if np.isnan(col).any():
                log.info(f"skip AUROC L{l + 1}/{sig}: NaN present")
                continue
            try:
                auc, flipped = corrected_auroc(labels, col)
            except ValueError as e:
                log.warning(f"AUROC undefined L{l + 1}/{sig}: {e}")
                continue
            if flipped:
                log.info(f"AUROC direction flip: layer=L{l + 1} signal={sig}")
            grid[i, j] = auc
    return grid


def check_baseline_anchor(final_layer_entropy_auroc, model_key, dataset_name):
    ref = H_E1_REFERENCES[(model_key, dataset_name)]
    return abs(final_layer_entropy_auroc - ref) <= BASELINE_TOLERANCE


def verify_mechanism_activated(signals, auroc_grid, log_text):
    """signals: per-cell aggregate dict — {"entropy": (32,) example-mean array,
    "model_key", "dataset_name", "final_layer_entropy_auroc"} (03_logic.md A-5.2)."""
    detail = {
        "log_found": "Lens sweep: model=" in log_text,
        "layer_dim_correct": signals["entropy"].shape == (N_LAYERS,),
        "depth_variation": bool(np.nanstd(auroc_grid[:, 0]) > 0.01),
        "baseline_reproduced": check_baseline_anchor(
            signals["final_layer_entropy_auroc"], signals["model_key"],
            signals["dataset_name"]),
    }
    return all(detail.values()), detail


def evaluate_gate(auroc_grid, retained_layers):
    """Gate uses INTERMEDIATE retained layers only (excludes idx 31)."""
    is_final = [l == N_LAYERS - 1 for l in retained_layers]
    final_pos = is_final.index(True) if True in is_final else None
    keep = [not f for f in is_final]
    inter_grid = auroc_grid[keep]
    inter_layers = [l for l, f in zip(retained_layers, is_final) if not f]

    if inter_grid.size == 0 or np.isnan(inter_grid).all():
        log.warning("All intermediate layers degenerate or empty")
        return {"best_layer": None, "best_signal": None, "best_auroc": float("nan"),
                "gate_pass": False, "final_layer_entropy_auroc": float("nan"),
                "depth_beats_final": None}

    i, j = np.unravel_index(np.nanargmax(inter_grid), inter_grid.shape)
    best_auroc = float(inter_grid[i, j])
    final_auroc = float(auroc_grid[final_pos, 0]) if final_pos is not None else float("nan")
    return {"best_layer": inter_layers[i] + 1, "best_signal": SIGNALS[j],
            "best_auroc": best_auroc, "gate_pass": best_auroc >= AUROC_GATE,
            "final_layer_entropy_auroc": final_auroc,
            "depth_beats_final": (best_auroc > final_auroc)
            if final_pos is not None else None}


def _nan_to_none(x):
    return None if (isinstance(x, float) and math.isnan(x)) else x


def write_cell_report(model_key, dataset_name, auroc_grid, retained_layers, counts):
    """UniFact-schema per-cell JSON -> results/{model}_{dataset}_report.json (FR-5.1)."""
    gate = evaluate_gate(auroc_grid, retained_layers)
    report = {
        "model": model_key, "dataset": dataset_name,
        "retained_layers": [l + 1 for l in retained_layers],
        "dropped_layers": [l + 1 for l in range(N_LAYERS) if l not in retained_layers],
        "signals": SIGNALS,
        "auroc_grid": [[_nan_to_none(float(v)) for v in row] for row in auroc_grid],
        "positive_cases": int(counts["positive"]),
        "negative_cases": int(counts["negative"]),
        "gate": {k: _nan_to_none(v) for k, v in gate.items()},
    }
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(f"{RESULTS_DIR}/{model_key}_{dataset_name}_report.json").write_text(
        json.dumps(report, indent=2))
    return report
