import sys
import os
import numpy as np


def load_bootstrap_auroc(hm2_code_dir: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "hm2_evaluate",
        os.path.join(hm2_code_dir, "evaluate.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.bootstrap_auroc


def compute_all_aurocs(
    scg_scores: dict,
    se_scores: dict,
    te_scores: dict,
    em_labels: dict,
    cfg,
) -> dict:
    bootstrap_auroc = load_bootstrap_auroc(cfg.hm2_code_dir)

    qids = list(scg_scores.keys())
    labels = [em_labels[q] for q in qids]
    scg_list = [scg_scores[q] for q in qids]
    se_list = [se_scores[q] for q in qids]
    te_list = [te_scores[q] for q in qids]

    auroc_scg, ci_scg_lo, ci_scg_hi = bootstrap_auroc(scg_list, labels, cfg.n_bootstrap, cfg.seed)
    auroc_se, ci_se_lo, ci_se_hi = bootstrap_auroc(se_list, labels, cfg.n_bootstrap, cfg.seed)
    auroc_te, ci_te_lo, ci_te_hi = bootstrap_auroc(te_list, labels, cfg.n_bootstrap, cfg.seed)

    delta = abs(auroc_scg - auroc_se)
    gate_passed = delta <= cfg.delta_auroc_gate
    scg_vs_te_advantage = auroc_scg - auroc_te

    return {
        "auroc_scg": auroc_scg,
        "ci_scg": [ci_scg_lo, ci_scg_hi],
        "auroc_se": auroc_se,
        "ci_se": [ci_se_lo, ci_se_hi],
        "auroc_te": auroc_te,
        "ci_te": [ci_te_lo, ci_te_hi],
        "delta": delta,
        "gate_passed": gate_passed,
        "scg_vs_te_advantage": scg_vs_te_advantage,
    }
