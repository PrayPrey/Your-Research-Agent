from __future__ import annotations
from typing import TYPE_CHECKING

import pandas as pd
from scipy.stats import kruskal, spearmanr

if TYPE_CHECKING:
    from config import Config


class StatsAnalyzer:
    def __init__(self, config: "Config"):
        self.config = config

    def compute_rates(self, labels: dict[str, list[int]]) -> pd.DataFrame:
        """Compute per-subtask contamination rates.
        Returns DataFrame with columns: subtask, n_items, n_contaminated, rate."""
        rows = []
        for subtask, lbls in labels.items():
            n = len(lbls)
            c = sum(lbls)
            rows.append({
                "subtask": subtask,
                "n_items": n,
                "n_contaminated": c,
                "rate": c / n if n else 0.0,
            })
        return pd.DataFrame(rows)

    def kruskal_wallis(self, labels: dict[str, list[int]]) -> dict:
        """Kruskal-Wallis H-test across all sub-tasks.
        Returns {kruskal_stat, p_value, gate_pass, max_pair_diff}."""
        label_lists = list(labels.values())
        stat, p = kruskal(*label_lists)
        rates = {k: sum(v) / len(v) for k, v in labels.items() if v}
        max_diff = max(rates.values()) - min(rates.values()) if rates else 0.0
        return {
            "kruskal_stat": float(stat),
            "p_value": float(p),
            "gate_pass": bool(p < self.config.gate_p_threshold),
            "max_pair_diff": float(max_diff),
        }

    def spearman_correlation(
        self, rates_a: pd.Series, rates_b: pd.Series
    ) -> tuple[float, float]:
        """Spearman rho between two rate series (primary vs sensitivity).
        Returns (rho, p_value)."""
        rho, p = spearmanr(rates_a.values, rates_b.values)
        return float(rho), float(p)

    def sanity_check(self, rates_df: pd.DataFrame, reference: dict) -> pd.DataFrame:
        """Compare our rates vs WIMBD Table 2 (tolerance ±5 pp).
        Returns DataFrame[subtask, our_rate, ref_rate, diff, within_tol]."""
        rows = []
        for subtask, ref_rate in reference.items():
            our = rates_df.loc[rates_df["subtask"] == subtask, "rate"]
            our_val = float(our.iloc[0]) if len(our) else float("nan")
            diff = abs(our_val - ref_rate)
            rows.append({
                "subtask": subtask,
                "our_rate": our_val,
                "ref_rate": ref_rate,
                "diff": diff,
                "within_tol": diff <= self.config.max_pair_diff_threshold,
            })
        return pd.DataFrame(rows)

    def assert_gate(self, p_value: float) -> None:
        """Hard assertion: p_value < gate_p_threshold or raise AssertionError."""
        assert p_value < self.config.gate_p_threshold, (
            f"Gate FAILED: p={p_value:.4f} >= {self.config.gate_p_threshold}"
        )
