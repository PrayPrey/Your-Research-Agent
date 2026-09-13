"""H-M2 Analysis: Logistic regression for standard benchmark adoption."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_papers, load_hhi_table
from labeling import label_papers

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "code" / "outputs"
FIGURES_DIR = BASE_DIR / "figures"


def fit_baseline(df: pd.DataFrame):
    """P(standard) ~ 1 (intercept only)."""
    return smf.logit("standard_benchmark ~ 1", data=df).fit(disp=0)


def fit_model(df: pd.DataFrame, add_controls: bool = False):
    """P(standard) ~ prior_hhi [+ C(venue)]."""
    formula = "standard_benchmark ~ prior_hhi"
    if add_controls:
        formula += " + C(venue)"
    return smf.logit(formula, data=df).fit(disp=0)


def extract_metrics(model_results, df: pd.DataFrame, hhi_param: str = "prior_hhi") -> Dict[str, Any]:
    """Extract all metrics from model results."""
    conf_int = model_results.conf_int()

    metrics = {
        "beta_hhi": float(model_results.params.get(hhi_param, 0)),
        "p_value": float(model_results.pvalues.get(hhi_param, 1.0)),
        "odds_ratio": float(np.exp(model_results.params.get(hhi_param, 0))),
        "ci_lower": float(np.exp(conf_int.loc[hhi_param, 0])) if hhi_param in conf_int.index else None,
        "ci_upper": float(np.exp(conf_int.loc[hhi_param, 1])) if hhi_param in conf_int.index else None,
        "n_papers": int(model_results.nobs),
        "n_venue_years": int(df[['venue', 'year']].drop_duplicates().shape[0]),
        "pseudo_r2": float(model_results.prsquared),
        "llr_p": float(model_results.llr_pvalue),
        "aic": float(model_results.aic),
        "bic": float(model_results.bic),
    }

    return metrics


def hosmer_lemeshow(model_results, df: pd.DataFrame, groups: int = 10) -> Tuple[float, float]:
    """Hosmer-Lemeshow goodness-of-fit test.

    Bins predicted probabilities into deciles, computes chi2 test.
    """
    pred_probs = model_results.predict()
    observed = df['standard_benchmark'].values

    # Create decile bins
    try:
        bins = pd.qcut(pred_probs, groups, duplicates='drop')
    except ValueError:
        # Not enough unique values for requested bins
        bins = pd.cut(pred_probs, groups, duplicates='drop')

    # Compute observed and expected counts per bin
    obs_grouped = pd.DataFrame({'prob': pred_probs, 'obs': observed, 'bin': bins})

    chi2_stat = 0.0
    for _, group in obs_grouped.groupby('bin'):
        n = len(group)
        if n == 0:
            continue
        obs_positive = group['obs'].sum()
        exp_positive = group['prob'].sum()
        exp_negative = n - exp_positive
        obs_negative = n - obs_positive

        if exp_positive > 0:
            chi2_stat += ((obs_positive - exp_positive) ** 2) / exp_positive
        if exp_negative > 0:
            chi2_stat += ((obs_negative - exp_negative) ** 2) / exp_negative

    # degrees of freedom = groups - 2
    dof = max(len(obs_grouped['bin'].unique()) - 2, 1)
    p_value = 1 - stats.chi2.cdf(chi2_stat, dof)

    return float(chi2_stat), float(p_value)


def gate_check(metrics: Dict[str, Any]) -> bool:
    """Gate: beta_hhi > 0 AND p_value < 0.05."""
    return metrics["beta_hhi"] > 0 and metrics["p_value"] < 0.05


def verify_mechanism_activation(metrics: Dict[str, Any]) -> Tuple[bool, Dict[str, bool]]:
    """Verify mechanism activation conditions.

    Returns:
        (passed, {coefficient_positive, statistically_significant, effect_meaningful})
    """
    checks = {
        "coefficient_positive": metrics["beta_hhi"] > 0,
        "statistically_significant": metrics["p_value"] < 0.05,
        "effect_meaningful": abs(metrics["beta_hhi"]) > 0.1,
    }
    passed = checks["coefficient_positive"] and checks["statistically_significant"]
    return passed, checks


def main(pwc_path: Optional[str] = None) -> Dict[str, Any]:
    """Run complete H-M2 analysis pipeline.

    Returns:
        Results dictionary with all metrics and gate status.
    """
    print("=" * 60)
    print("H-M2: Standard Benchmark Adoption Analysis")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/7] Loading PWC papers...")
    papers_df = load_papers(pwc_path)

    print("\n[2/7] Loading HHI table...")
    hhi_df = load_hhi_table()

    # Step 2: Label papers
    print("\n[3/7] Labeling papers with standard benchmark usage...")
    labeled_df = label_papers(papers_df, hhi_df)

    # Check minimum papers requirement
    if len(labeled_df) < 500:
        print(f"WARNING: Only {len(labeled_df)} papers, below 500 minimum")

    # Step 3: Fit models
    print("\n[4/7] Fitting baseline model (intercept only)...")
    baseline_results = fit_baseline(labeled_df)
    baseline_metrics = {
        "intercept": float(baseline_results.params['Intercept']),
        "base_rate": float(np.exp(baseline_results.params['Intercept']) / (1 + np.exp(baseline_results.params['Intercept']))),
        "n_papers": int(baseline_results.nobs),
        "aic": float(baseline_results.aic),
    }
    print(f"  Base adoption rate: {baseline_metrics['base_rate']:.3f}")

    print("\n[5/7] Fitting proposed model (prior_hhi)...")
    proposed_results = fit_model(labeled_df, add_controls=False)
    proposed_metrics = extract_metrics(proposed_results, labeled_df)

    print(f"  β(prior_HHI) = {proposed_metrics['beta_hhi']:.4f}")
    print(f"  p-value = {proposed_metrics['p_value']:.6f}")
    print(f"  Odds Ratio = {proposed_metrics['odds_ratio']:.4f}")
    print(f"  95% CI: [{proposed_metrics['ci_lower']:.4f}, {proposed_metrics['ci_upper']:.4f}]")

    print("\n[6/7] Fitting controlled model (+ venue dummies)...")
    controlled_results = fit_model(labeled_df, add_controls=True)
    controlled_metrics = extract_metrics(controlled_results, labeled_df)

    print(f"  β(prior_HHI) = {controlled_metrics['beta_hhi']:.4f}")
    print(f"  p-value = {controlled_metrics['p_value']:.6f}")

    # Hosmer-Lemeshow test
    hl_chi2, hl_p = hosmer_lemeshow(proposed_results, labeled_df)
    proposed_metrics["hosmer_lemeshow_chi2"] = hl_chi2
    proposed_metrics["hosmer_lemeshow_p"] = hl_p
    print(f"  Hosmer-Lemeshow: χ² = {hl_chi2:.2f}, p = {hl_p:.4f}")

    # Step 4: Gate check and mechanism verification
    print("\n[7/7] Gate check and mechanism verification...")
    gate_passed = gate_check(proposed_metrics)
    mechanism_passed, mechanism_checks = verify_mechanism_activation(proposed_metrics)

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  Gate (β > 0 AND p < 0.05): {'PASSED' if gate_passed else 'FAILED'}")
    print(f"  Mechanism activation: {'PASSED' if mechanism_passed else 'FAILED'}")
    for check, status in mechanism_checks.items():
        print(f"    - {check}: {'✓' if status else '✗'}")

    # Compile results
    results = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "gate_passed": gate_passed,
        "mechanism_activated": mechanism_passed,
        "mechanism_checks": mechanism_checks,
        "proposed_model": proposed_metrics,
        "controlled_model": controlled_metrics,
        "baseline_model": baseline_metrics,
        "data_stats": {
            "n_papers_total": int(len(papers_df)),
            "n_papers_labeled": int(len(labeled_df)),
            "n_venue_years": int(labeled_df[['venue', 'year']].drop_duplicates().shape[0]),
            "adoption_rate": float(labeled_df['standard_benchmark'].mean()),
        },
        "coefficient_stable": (
            proposed_metrics["beta_hhi"] > 0 and controlled_metrics["beta_hhi"] > 0
        ),
    }

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_path = RESULTS_DIR / "results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    # Generate visualizations
    print("\nGenerating visualizations...")
    try:
        from visualize import generate_all
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        generate_all(
            proposed_metrics=proposed_metrics,
            controlled_metrics=controlled_metrics,
            baseline_metrics=baseline_metrics,
            labeled_df=labeled_df,
            model_results=proposed_results,
            out_dir=str(FIGURES_DIR)
        )
        print(f"Figures saved to: {FIGURES_DIR}")
    except Exception as e:
        print(f"Warning: Visualization failed: {e}")

    # Save CSV for Phase 5
    csv_path = RESULTS_DIR / "results.csv"
    labeled_df.to_csv(csv_path, index=False)
    print(f"Labeled data saved to: {csv_path}")

    return results


if __name__ == "__main__":
    results = main()

    # Print final gate verdict
    print("\n" + "=" * 60)
    if results["gate_passed"]:
        print("GATE VERDICT: PASSED")
        print("H-M2 hypothesis supported: Prior HHI predicts standard benchmark adoption")
    else:
        print("GATE VERDICT: FAILED")
        print("H-M2 hypothesis not supported at α = 0.05")
    print("=" * 60)
