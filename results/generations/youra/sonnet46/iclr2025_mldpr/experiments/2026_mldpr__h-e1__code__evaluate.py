"""evaluate.py — Gate Metrics + Mechanism Activation Check for H-E1."""
import json
import numpy as np
import pandas as pd
from pathlib import Path

COVERAGE_THRESHOLD = 0.70
PEARSON_THRESHOLD = 0.70
PILOT_MIN_COVERAGE = 0.30

GATE_CONFIG = {
    "coverage_threshold": 0.70,
    "pearson_threshold": 0.70,
    "pilot_min_coverage": 0.30,
    "results_output_path": "results/h_e1_results.json",
    "mechanism_indicators": [
        "scoring_ran",
        "coverage_achievable",
        "weighting_effect",
        "human_correlation_positive",
    ],
    "failure_codes": {
        "coverage": "COVERAGE_BELOW_THRESHOLD",
        "validation": "VALIDATION_BELOW_THRESHOLD",
        "pilot": "PILOT_COVERAGE_FAILED",
        "api": "API_UNAVAILABLE",
    },
}


class PilotCoverageFailedError(Exception):
    """Raised when pilot coverage check fails."""
    pass


def check_pilot_coverage(pilot_df: pd.DataFrame) -> None:
    """Check if pilot coverage meets minimum threshold per repo.

    Args:
        pilot_df: Scored pilot DataFrame with 'repository' and 'weighted_dts_score'.

    Raises:
        PilotCoverageFailedError: If any repo has coverage < PILOT_MIN_COVERAGE.
    """
    if "repository" not in pilot_df.columns or "weighted_dts_score" not in pilot_df.columns:
        print("  [Pilot] Warning: missing required columns, skipping coverage check")
        return

    repos = pilot_df["repository"].unique()
    for repo in repos:
        subset = pilot_df[pilot_df["repository"] == repo]
        if len(subset) == 0:
            continue
        coverage = float((subset["weighted_dts_score"] > 0).mean())
        print(f"  [Pilot] {repo}: coverage = {coverage:.3f} (min: {PILOT_MIN_COVERAGE})")
        if coverage < PILOT_MIN_COVERAGE:
            raise PilotCoverageFailedError(
                f"Pilot coverage for {repo} = {coverage:.3f} < {PILOT_MIN_COVERAGE}. "
                f"API field mapping may be broken."
            )


def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Check that all 4 mechanism activation indicators are True.

    Args:
        results: Results dict with mechanism indicator fields.

    Returns:
        (all_passed: bool, indicators: dict[str, bool])
    """
    indicators = {
        "scoring_ran": bool(results.get("scoring_ran", False)),
        "coverage_achievable": bool(results.get("coverage_rate", 0) > 0),
        "weighting_effect": _check_weighting_effect(results),
        "human_correlation_positive": bool(results.get("pearson_r", -1) > 0),
    }
    all_passed = all(indicators.values())
    return all_passed, indicators


def _check_weighting_effect(results: dict) -> bool:
    """Check if weighted scores differ from unweighted (weighting has effect)."""
    weighted_mean = results.get("weighted_dts_mean", None)
    unweighted_mean = results.get("unweighted_dts_mean", None)
    if weighted_mean is None or unweighted_mean is None:
        return False
    # Weighting has effect if scores differ by any amount
    return abs(weighted_mean - unweighted_mean) > 1e-6


def evaluate_gate(results: dict) -> dict:
    """Evaluate MUST_WORK gate for H-E1.

    Args:
        results: Full results dict.

    Returns:
        Dict with keys: gate_passed (bool), failure_code (str|None), failure_message (str|None).
    """
    coverage_rate = results.get("coverage_rate", 0)
    pearson_r = results.get("pearson_r", 0)

    failures = []

    if coverage_rate < COVERAGE_THRESHOLD:
        failures.append({
            "code": GATE_CONFIG["failure_codes"]["coverage"],
            "message": f"Coverage {coverage_rate:.3f} < threshold {COVERAGE_THRESHOLD}",
        })

    if pearson_r < PEARSON_THRESHOLD:
        failures.append({
            "code": GATE_CONFIG["failure_codes"]["validation"],
            "message": f"Pearson r {pearson_r:.3f} < threshold {PEARSON_THRESHOLD}",
        })

    if not failures:
        return {
            "gate_passed": True,
            "failure_code": None,
            "failure_message": None,
            "gate_type": "MUST_WORK",
            "criteria_met": {
                "coverage": coverage_rate >= COVERAGE_THRESHOLD,
                "pearson_r": pearson_r >= PEARSON_THRESHOLD,
            },
        }
    else:
        return {
            "gate_passed": False,
            "failure_code": failures[0]["code"],
            "failure_message": "; ".join(f["message"] for f in failures),
            "gate_type": "MUST_WORK",
            "criteria_met": {
                "coverage": coverage_rate >= COVERAGE_THRESHOLD,
                "pearson_r": pearson_r >= PEARSON_THRESHOLD,
            },
            "all_failures": failures,
        }


def build_results_dict(
    df: pd.DataFrame,
    pearson_stats: dict,
    mechanism_indicators: dict,
) -> dict:
    """Assemble h_e1_results.json payload.

    Args:
        df: Scored corpus DataFrame.
        pearson_stats: Output from compute_pearson_correlation().
        mechanism_indicators: Output from verify_mechanism_activated().

    Returns:
        Full results dict ready for JSON serialization.
    """
    from scorer import compute_coverage_rate

    repos = df["repository"].unique().tolist() if "repository" in df.columns else []

    results = {
        # Scoring metadata
        "scoring_ran": True,
        "n_datasets": int(len(df)),
        "n_by_repo": {repo: int((df["repository"] == repo).sum()) for repo in repos},
        # Coverage metrics
        "coverage_rate": float(compute_coverage_rate(df)),
        **{f"coverage_rate_{repo}": float(compute_coverage_rate(df, repo=repo)) for repo in repos},
        # DTS score statistics
        "weighted_dts_mean": float(df["weighted_dts_score"].mean()) if "weighted_dts_score" in df.columns else 0.0,
        "weighted_dts_std": float(df["weighted_dts_score"].std()) if "weighted_dts_score" in df.columns else 0.0,
        "unweighted_dts_mean": float(df["unweighted_dts_score"].mean()) if "unweighted_dts_score" in df.columns else 0.0,
        "unweighted_dts_std": float(df["unweighted_dts_score"].std()) if "unweighted_dts_score" in df.columns else 0.0,
        # Per-section coverage by repo
        "per_section_coverage": _compute_per_section_coverage(df, repos),
        # Human validation
        "pearson_r": pearson_stats.get("pearson_r", 0.0),
        "pearson_p_value": pearson_stats.get("p_value", 1.0),
        "pearson_ci_lower": pearson_stats.get("ci_lower", 0.0),
        "pearson_ci_upper": pearson_stats.get("ci_upper", 0.0),
        "n_human_validated": pearson_stats.get("n_samples", 0),
        # Mechanism indicators
        "mechanism_indicators": mechanism_indicators,
        # Gate thresholds
        "coverage_threshold": COVERAGE_THRESHOLD,
        "pearson_threshold": PEARSON_THRESHOLD,
    }

    # Add viz data
    if "in_human_subsample" in df.columns:
        human_subset = df[df["in_human_subsample"] == True]
        if len(human_subset) > 0 and "weighted_dts_score" in human_subset.columns:
            results["auto_scores_for_viz"] = human_subset["weighted_dts_score"].tolist()

    return results


def _compute_per_section_coverage(df: pd.DataFrame, repos: list) -> dict:
    """Compute mean per-section coverage by repo."""
    from scorer import DTS_SECTIONS
    result = {}
    for section in DTS_SECTIONS:
        col = f"per_section_{section}"
        if col in df.columns:
            result[section] = {
                "overall": float(df[col].mean()),
                **{repo: float(df[df["repository"] == repo][col].mean())
                   for repo in repos
                   if len(df[df["repository"] == repo]) > 0},
            }
    return result


def save_results(results: dict, output_path: str = "results/h_e1_results.json") -> None:
    """Save results dict to JSON.

    Args:
        results: Results dict.
        output_path: Path to save JSON file.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  [Evaluate] Results saved: {output_path}")
