import sys
import os
import json
import importlib
import numpy as np


def load_bootstrap_auroc(hm2_code_dir: str):
    """Returns bootstrap_auroc callable from h-m2/code/evaluate.py."""
    # Resolve relative to THIS file if path is relative
    if not os.path.isabs(hm2_code_dir):
        base = os.path.dirname(os.path.abspath(__file__))
        hm2_code_dir = os.path.normpath(os.path.join(base, hm2_code_dir))
    if hm2_code_dir not in sys.path:
        sys.path.insert(0, hm2_code_dir)
    spec = importlib.util.spec_from_file_location(
        "hm2_evaluate", os.path.join(hm2_code_dir, "evaluate.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.bootstrap_auroc


def load_hm3_baselines(hm3_results_path: str, cfg) -> tuple:
    """
    Returns (auroc_te, auroc_se, em_labels, se_scores, te_scores) from h-m3/results.json.
    Falls back to cfg constants if key missing.
    """
    if not os.path.isabs(hm3_results_path):
        base = os.path.dirname(os.path.abspath(__file__))
        hm3_results_path = os.path.normpath(os.path.join(base, hm3_results_path))
    try:
        with open(hm3_results_path, "r") as f:
            data = json.load(f)
        auroc_te = data.get("auroc_te", cfg.auroc_te_baseline)
        auroc_se = data.get("auroc_se", cfg.auroc_se_baseline)
        em_labels = data.get("em_labels", {})
        se_scores = data.get("se_scores", {})
        te_scores = data.get("te_scores", {})
        return auroc_te, auroc_se, em_labels, se_scores, te_scores
    except FileNotFoundError:
        print(f"WARNING: h-m3 results not found at {hm3_results_path}, using cfg fallback values")
        return cfg.auroc_te_baseline, cfg.auroc_se_baseline, {}, {}, {}


def compute_ece(confidences: list, em_labels: dict, n_bins: int = 10) -> float:
    """10-bin ECE. Returns scalar float."""
    confs = np.array(confidences)
    labels = np.array(list(em_labels.values()), dtype=float)
    N = len(confs)

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        if i < n_bins - 1:
            mask = (confs >= lo) & (confs < hi)
        else:
            mask = (confs >= lo) & (confs <= hi)

        bin_count = mask.sum()
        if bin_count == 0:
            continue

        bin_conf = confs[mask].mean()
        bin_acc = labels[mask].mean()
        ece += (bin_count / N) * abs(bin_acc - bin_conf)

    return float(ece)


def compute_vc_auroc(vc_uncertainties: list, em_labels: dict, cfg) -> dict:
    """
    Bootstrap AUROC for VC. Returns dict with auroc, CI, gate results, ECE.
    """
    bootstrap_auroc = load_bootstrap_auroc(cfg.hm2_code_dir)

    qids = list(em_labels.keys())
    labels = [em_labels[q] for q in qids]
    scores = vc_uncertainties

    auroc_vc, ci_lo, ci_hi = bootstrap_auroc(scores, labels, cfg.n_bootstrap, cfg.seed)

    vc_confidences = [1.0 - u for u in vc_uncertainties]
    ece = compute_ece(vc_confidences, em_labels)

    gate_vc_lt_te = auroc_vc < cfg.auroc_te_baseline
    gate_vc_lt_se = auroc_vc < cfg.auroc_se_baseline
    gate_passed = gate_vc_lt_te and gate_vc_lt_se

    return {
        "auroc_vc": auroc_vc,
        "auroc_vc_ci": [ci_lo, ci_hi],
        "auroc_te": cfg.auroc_te_baseline,
        "auroc_se": cfg.auroc_se_baseline,
        "delta_te": abs(auroc_vc - cfg.auroc_te_baseline),
        "delta_se": abs(auroc_vc - cfg.auroc_se_baseline),
        "gate_vc_lt_te": gate_vc_lt_te,
        "gate_vc_lt_se": gate_vc_lt_se,
        "gate_passed": gate_passed,
        "ece": ece,
    }
