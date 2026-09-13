"""H-M5 Gate Evaluation: Gate logic and failure pivot analysis"""
import pandas as pd
from correlation import period_correlation
from config import CONFIG


def evaluate_gate(
    r_pre: float, r_post: float, p_value: float, n_pre: int, n_post: int
) -> dict:
    """Gate evaluation: r_pre > 0.6, r_post < 0.4, p < 0.05."""
    gate_pass = (
        r_pre > CONFIG.gate_r_pre_min and
        r_post < CONFIG.gate_r_post_max and
        p_value < CONFIG.gate_p_value_max
    )

    return {
        "gate_pass": gate_pass,
        "r_pre": r_pre,
        "r_post": r_post,
        "p_value": p_value,
        "n_pre": n_pre,
        "n_post": n_post,
        "thresholds": {
            "r_pre_min": CONFIG.gate_r_pre_min,
            "r_post_max": CONFIG.gate_r_post_max,
            "p_value_max": CONFIG.gate_p_value_max,
        }
    }


def failure_pivot(gini_df: pd.DataFrame) -> pd.DataFrame:
    """If gate fails: analyze other modality pairs."""
    pairs = [
        ("CV", "Audio"),
        ("NLP", "Audio"),
        ("CV", "Tabular"),
        ("NLP", "Tabular"),
        ("Audio", "Tabular"),
    ]

    results = []
    for col_a, col_b in pairs:
        r_pre, n_pre = period_correlation(gini_df, col_a, col_b, end=CONFIG.pre_cutoff)
        r_post, n_post = period_correlation(gini_df, col_a, col_b, start=CONFIG.post_cutoff)

        results.append({
            "pair": f"{col_a}-{col_b}",
            "r_pre": r_pre,
            "r_post": r_post,
            "delta": r_pre - r_post if not (pd.isna(r_pre) or pd.isna(r_post)) else None,
            "n_pre": n_pre,
            "n_post": n_post,
        })

    return pd.DataFrame(results)
