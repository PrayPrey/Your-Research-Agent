from dataclasses import dataclass

import pandas as pd
import statsmodels.api as sm
from scipy.stats import pearsonr
from statsmodels.stats.outliers_influence import variance_inflation_factor

from config import CFG


@dataclass
class GateResult:
    gate: str
    passed: bool
    value: float
    threshold: float
    message: str


def compute_partial_r2(predictor: pd.Series, controls: pd.DataFrame) -> float:
    """OLS residualization: partial_r2 = 1 - rsquared(predictor ~ controls)."""
    if controls is None or controls.shape[1] == 0:
        return 1.0
    X = sm.add_constant(controls.dropna())
    y = predictor.loc[X.index].dropna()
    X = X.loc[y.index]
    if len(y) < controls.shape[1] + 2:
        raise ValueError(f"Insufficient observations for OLS: n={len(y)}")
    model = sm.OLS(y, X).fit()
    return 1.0 - model.rsquared


class VIFChecker:
    COVARIATES = [
        "log_unique_paper_count_at_intro_z",
        "paper_diversity_ratio_at_intro_z",
        "task_age",
        "log_publication_volume",
        "benchmark_introduction_year",
    ]

    def compute(self, panel: pd.DataFrame) -> dict:
        cols = [c for c in self.COVARIATES if c in panel.columns]
        if len(cols) < 2:
            raise ValueError(f"Need >=2 covariates for VIF; found: {cols}")
        sub = panel[cols].dropna()

        # Drop perfectly collinear columns (|r| > 0.9999) iteratively
        # This handles the case where task_age = 2024 - intro_year by construction
        removed = set()
        for i in range(len(cols)):
            if cols[i] in removed:
                continue
            for j in range(i + 1, len(cols)):
                if cols[j] in removed:
                    continue
                r = sub[[cols[i], cols[j]]].corr().iloc[0, 1]
                if abs(r) > 0.9999:
                    print(
                        f"WARNING: Perfect collinearity |r|={abs(r):.6f} between "
                        f"'{cols[i]}' and '{cols[j]}' — excluding '{cols[j]}' from VIF"
                    )
                    removed.add(cols[j])

        active_cols = [c for c in cols if c not in removed]
        if len(active_cols) < 2:
            print("WARNING: After collinearity removal, <2 active covariates — skipping VIF")
            return {c: 1.0 for c in cols}

        X = sm.add_constant(sub[active_cols])
        vif_dict = {}
        for i, col in enumerate(active_cols):
            vif_dict[col] = variance_inflation_factor(X.values, i + 1)
        # Excluded cols get VIF = NaN (marked as excluded)
        for col in removed:
            vif_dict[col] = float("nan")
        return vif_dict

    def collinearity_failsafe(self, stats_df: pd.DataFrame) -> float:
        r, _ = pearsonr(
            stats_df["log_unique_paper_count_at_intro_z"],
            stats_df["paper_diversity_ratio_at_intro_z"],
        )
        if abs(r) > CFG.collinearity_r_max:
            print(
                f"WARNING: High collinearity r={r:.3f}; "
                "H-M1 should use single predictor only"
            )
        return r


class GateValidator:
    def g0_coverage(self, n_matched: int, n_total: int = None) -> GateResult:
        if n_total is None:
            n_total = CFG.n_benchmarks
        coverage = n_matched / n_total
        passed = coverage >= CFG.g0_coverage_min
        msg = f"G0 COVERAGE: {coverage:.3f} (threshold>={CFG.g0_coverage_min})"
        print(msg)
        return GateResult(
            gate="G0", passed=passed, value=coverage,
            threshold=CFG.g0_coverage_min, message=msg,
        )

    def g1_log_count_time_independence(
        self, stats_df: pd.DataFrame, panel: pd.DataFrame
    ) -> GateResult:
        merged = stats_df.merge(
            panel[["task_path", "task_age", "benchmark_introduction_year"]],
            on="task_path", how="left",
        )
        predictor = merged["log_unique_paper_count_at_intro_z"]
        controls = merged[["task_age", "benchmark_introduction_year"]]
        pr2 = compute_partial_r2(predictor, controls)
        passed = pr2 > CFG.g1_partial_r2_min
        msg = f"G1 LOG-COUNT TIME-INDEP: partial_r2={pr2:.4f} (threshold>{CFG.g1_partial_r2_min})"
        print(msg)
        return GateResult(
            gate="G1", passed=passed, value=pr2,
            threshold=CFG.g1_partial_r2_min, message=msg,
        )

    def g2_diversity_ratio_time_independence(
        self, stats_df: pd.DataFrame, panel: pd.DataFrame
    ) -> GateResult:
        merged = stats_df.merge(
            panel[["task_path", "task_age", "benchmark_introduction_year"]],
            on="task_path", how="left",
        )
        predictor = merged["paper_diversity_ratio_at_intro_z"]
        controls = merged[["task_age", "benchmark_introduction_year"]]
        pr2 = compute_partial_r2(predictor, controls)
        passed = pr2 > CFG.g2_partial_r2_min
        msg = f"G2 DIV-RATIO TIME-INDEP: partial_r2={pr2:.4f} (threshold>{CFG.g2_partial_r2_min})"
        print(msg)
        return GateResult(
            gate="G2", passed=passed, value=pr2,
            threshold=CFG.g2_partial_r2_min, message=msg,
        )

    def g3_diversity_variance(self, stats_df: pd.DataFrame) -> GateResult:
        std_val = stats_df["paper_diversity_ratio_at_intro"].std()
        passed = std_val > CFG.g3_std_min
        msg = f"G3 DIV-VARIANCE: std={std_val:.4f} (threshold>{CFG.g3_std_min})"
        print(msg)
        return GateResult(
            gate="G3", passed=passed, value=std_val,
            threshold=CFG.g3_std_min, message=msg,
        )

    def g4_vif(self, enriched_panel: pd.DataFrame) -> GateResult:
        checker = VIFChecker()
        vif_dict = checker.compute(enriched_panel)
        import math
        finite_vifs = [v for v in vif_dict.values() if not math.isnan(v)]
        max_vif = max(finite_vifs) if finite_vifs else 1.0
        if max_vif >= CFG.g4_vif_max:
            passed = False
        elif max_vif >= CFG.g4_vif_warn:
            print(f"WARNING: VIF in warn range: {vif_dict}")
            passed = True
        else:
            passed = True
        msg = f"G4 VIF: max={max_vif:.2f} (warn>={CFG.g4_vif_warn}, fail>={CFG.g4_vif_max})"
        print(msg)
        return GateResult(
            gate="G4", passed=passed, value=max_vif,
            threshold=CFG.g4_vif_max, message=msg,
        )

    def run_all(
        self,
        stats_df: pd.DataFrame,
        panel: pd.DataFrame,
        n_matched: int,
        enriched_panel: pd.DataFrame = None,
    ) -> list:
        if enriched_panel is None:
            enriched_panel = panel.merge(stats_df, on="task_path", how="left")

        gate_fns = [
            lambda: self.g0_coverage(n_matched),
            lambda: self.g1_log_count_time_independence(stats_df, panel),
            lambda: self.g2_diversity_ratio_time_independence(stats_df, panel),
            lambda: self.g3_diversity_variance(stats_df),
            lambda: self.g4_vif(enriched_panel),
        ]

        results = []
        for fn in gate_fns:
            result = fn()
            results.append(result)
            if not result.passed:
                print(f"FAIL FAST: {result.message}")
                raise SystemExit(1)
        return results
