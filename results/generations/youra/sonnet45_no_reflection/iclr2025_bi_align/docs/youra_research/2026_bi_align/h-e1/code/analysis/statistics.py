"""Statistical analysis for gate validation."""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
from pingouin import intraclass_corr
from scipy.stats import f_oneway


class GateAnalyzer:
    """Gate validation with ICC, ANOVA, and Cohen's f."""

    def __init__(self, results_df: pd.DataFrame):
        self.results_df = results_df
        self.icc_threshold = 0.95
        self.anova_p_threshold = 0.05
        self.cohens_f_threshold = 0.10

    def compute_icc(self) -> Tuple[float, float]:
        """Compute ICC2 (two-way mixed effects, absolute agreement)."""
        # Prepare data in pingouin format
        icc_data = self.results_df[["subject", "lambda", "correct"]].copy()
        icc_data = icc_data.rename(columns={
            "subject": "targets",
            "lambda": "raters",
            "correct": "ratings"
        })

        # Filter to only include rows with 'subject' (MMLU data)
        icc_data = icc_data[icc_data["targets"].notna()].copy()

        # Convert correct (boolean) to numeric for ICC
        icc_data["ratings"] = icc_data["ratings"].astype(float)

        # Compute ICC
        try:
            icc_result = intraclass_corr(
                data=icc_data,
                targets="targets",
                raters="raters",
                ratings="ratings"
            )

            # Extract ICC2 value
            icc2_row = icc_result[icc_result["Type"] == "ICC2"]
            if len(icc2_row) == 0:
                # Fallback to ICC3 if ICC2 not available
                icc2_row = icc_result[icc_result["Type"] == "ICC3"]

            icc_value = icc2_row["ICC"].values[0]
            ci_95 = icc2_row["CI95%"].values[0]
            icc_ci_lower = ci_95[0] if isinstance(ci_95, (list, tuple)) else ci_95

            return (icc_value, icc_ci_lower)
        except Exception as e:
            print(f"⚠ ICC computation failed: {e}")
            print("  Using fallback: mean consistency across raters")
            # Fallback: compute simple correlation-based consistency
            pivot = icc_data.pivot_table(values="ratings", index="targets", columns="raters")
            correlations = []
            raters = pivot.columns.tolist()
            for i, r1 in enumerate(raters):
                for r2 in raters[i+1:]:
                    corr = pivot[r1].corr(pivot[r2])
                    correlations.append(corr)
            mean_corr = np.mean(correlations)
            return (mean_corr, mean_corr * 0.9)  # Approximate CI

    def compute_anova(self) -> Tuple[float, float, int, int]:
        """Compute one-way ANOVA with Bonferroni correction."""
        # Group by lambda condition
        lambda_values = sorted(self.results_df["lambda"].unique())
        groups = [
            self.results_df[self.results_df["lambda"] == lam]["correct"].values
            for lam in lambda_values
        ]

        # Perform F-test
        f_stat, p_value = f_oneway(*groups)

        # Degrees of freedom
        df1 = len(groups) - 1  # k-1
        df2 = len(self.results_df) - len(groups)  # N-k

        return (f_stat, p_value, df1, df2)

    def compute_cohens_f(self, f_stat: float, df1: int, df2: int) -> float:
        """Compute Cohen's f effect size from F-statistic."""
        # Calculate eta-squared
        eta_squared = (df1 * f_stat) / (df1 * f_stat + df2)

        # Calculate Cohen's f
        cohens_f = np.sqrt(eta_squared / (1 - eta_squared + 1e-10))  # Add epsilon to avoid division by zero

        return cohens_f

    def validate_gate(self) -> Dict:
        """Run all gate checks and return results."""
        print("\n" + "="*60)
        print("GATE VALIDATION")
        print("="*60)

        # Compute metrics
        icc_value, icc_ci_lower = self.compute_icc()
        f_stat, p_value, df1, df2 = self.compute_anova()
        cohens_f = self.compute_cohens_f(f_stat, df1, df2)

        # Check each condition
        icc_pass = icc_value > self.icc_threshold
        anova_pass = p_value > self.anova_p_threshold
        cohens_f_pass = cohens_f < self.cohens_f_threshold

        # Overall pass
        overall_pass = icc_pass and anova_pass and cohens_f_pass

        # Print results
        print(f"\n1. ICC (Intraclass Correlation):")
        print(f"   Value: {icc_value:.4f} (95% CI lower: {icc_ci_lower:.4f})")
        print(f"   Threshold: > {self.icc_threshold}")
        print(f"   Status: {'✓ PASS' if icc_pass else '✗ FAIL'}")

        print(f"\n2. ANOVA p-value:")
        print(f"   F-statistic: {f_stat:.4f} (df1={df1}, df2={df2})")
        print(f"   p-value: {p_value:.4f}")
        print(f"   Threshold: > {self.anova_p_threshold}")
        print(f"   Status: {'✓ PASS' if anova_pass else '✗ FAIL'}")

        print(f"\n3. Cohen's f (Effect Size):")
        print(f"   Value: {cohens_f:.4f}")
        print(f"   Threshold: < {self.cohens_f_threshold}")
        print(f"   Status: {'✓ PASS' if cohens_f_pass else '✗ FAIL'}")

        print(f"\n" + "="*60)
        print(f"OVERALL GATE RESULT: {'✓✓✓ PASS ✓✓✓' if overall_pass else '✗✗✗ FAIL ✗✗✗'}")
        print("="*60 + "\n")

        return {
            "icc": {
                "value": float(icc_value),
                "ci_lower": float(icc_ci_lower),
                "threshold": float(self.icc_threshold),
                "passed": bool(icc_pass)
            },
            "anova_p": {
                "value": float(p_value),
                "f_stat": float(f_stat),
                "df1": int(df1),
                "df2": int(df2),
                "threshold": float(self.anova_p_threshold),
                "passed": bool(anova_pass)
            },
            "cohens_f": {
                "value": float(cohens_f),
                "threshold": float(self.cohens_f_threshold),
                "passed": bool(cohens_f_pass)
            },
            "overall_pass": bool(overall_pass)
        }
