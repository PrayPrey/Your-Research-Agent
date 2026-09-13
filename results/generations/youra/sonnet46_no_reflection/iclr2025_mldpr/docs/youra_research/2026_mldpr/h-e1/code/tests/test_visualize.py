"""Tests for task-006: visualize.py spec compliance."""
import pytest
import numpy as np
import pandas as pd
import os


def _make_domain_signals(n=20, domain="cv"):
    rng = np.random.default_rng(42)
    rows = (
        [{"benchmark": f"sat_{i}", "label": "saturated",
          "hd_signal": float(rng.normal(1.0, 0.3)), "domain": domain}
         for i in range(n // 2)]
        + [{"benchmark": f"h_{i}", "label": "healthy",
            "hd_signal": float(rng.normal(0.0, 0.3)), "domain": domain}
           for i in range(n // 2)]
    )
    return pd.DataFrame(rows)


def _make_domain_results():
    return {
        "cv": {"discriminability": {"p_value": 0.01, "cohens_d": 0.8, "auc": 0.85,
                                    "n_sat": 10, "n_healthy": 10},
               "baseline_auc": 0.6, "signal_auc": 0.85,
               "roc_data": {"fpr": [0, 0.1, 0.5, 1.0], "tpr": [0, 0.7, 0.9, 1.0]},
               "baseline_roc": {"fpr": [0, 0.5, 1.0], "tpr": [0, 0.5, 1.0]}},
        "nlp": {"discriminability": {"p_value": 0.02, "cohens_d": 0.7, "auc": 0.80,
                                     "n_sat": 10, "n_healthy": 10},
                "baseline_auc": 0.58, "signal_auc": 0.80,
                "roc_data": {"fpr": [0, 0.2, 0.5, 1.0], "tpr": [0, 0.6, 0.85, 1.0]},
                "baseline_roc": {"fpr": [0, 0.5, 1.0], "tpr": [0, 0.5, 1.0]}},
        "tabular": {"discriminability": {"p_value": 0.03, "cohens_d": 0.6, "auc": 0.75,
                                         "n_sat": 10, "n_healthy": 10},
                    "baseline_auc": 0.55, "signal_auc": 0.75,
                    "roc_data": {"fpr": [0, 0.3, 0.5, 1.0], "tpr": [0, 0.65, 0.8, 1.0]},
                    "baseline_roc": {"fpr": [0, 0.5, 1.0], "tpr": [0, 0.5, 1.0]}},
    }


def test_generate_all_figures_creates_pngs(tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    from visualize import generate_all_figures
    domain_signals = {d: _make_domain_signals(domain=d) for d in ("cv", "nlp", "tabular")}
    domain_results = _make_domain_results()
    temporal_results = {
        "cv": {6: {"cohens_d": 0.3}, 12: {"cohens_d": 0.5},
               18: {"cohens_d": 0.65}, 24: {"cohens_d": 0.8}},
        "nlp": {6: {"cohens_d": 0.2}, 12: {"cohens_d": 0.4},
                18: {"cohens_d": 0.6}, 24: {"cohens_d": 0.7}},
        "tabular": {6: {"cohens_d": 0.15}, 12: {"cohens_d": 0.35},
                    18: {"cohens_d": 0.5}, 24: {"cohens_d": 0.6}},
    }
    out_dir = str(tmp_path)
    generate_all_figures(domain_results, domain_signals, temporal_results, out_dir)
    # Check at least gate_metrics.png was created
    assert os.path.exists(os.path.join(out_dir, "gate_metrics.png"))
