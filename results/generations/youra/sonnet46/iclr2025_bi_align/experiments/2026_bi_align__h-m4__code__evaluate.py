"""
evaluate.py - Gate check and mechanism activation verification for h-m4.

Implements >=2/3 cross-model gate criterion for the SHOULD_WORK hypothesis.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from regression import MediationResult, OLSStageResult

logger = logging.getLogger(__name__)

SURFACE_FEATURE_COLS = ['response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len']


@dataclass
class GateResult:
    """Gate evaluation result for a single SBERT model."""
    model_name: str
    gate_pass: bool
    beta_pm_positive: bool
    p_significant: bool
    beta_pm_value: float
    p_value: float
    secondary_check_pass: bool  # |beta_pm_full / beta_pm_reduced| > 0.5


@dataclass
class OverallGateResult:
    """Cross-model gate evaluation result."""
    overall_pass: bool
    models_passed: int
    models_required: int
    gate_results: Dict[str, GateResult]
    interpretation: str


def verify_mechanism_activated(
    model_result,
    beta_pm: float,
    p_pm: float,
    surface_cols: List[str],
) -> Tuple[bool, Dict[str, bool]]:
    """Check 5 activation indicators.

    Indicators:
      1. model_fitted: model_result is not None
      2. beta_pm_nonzero: beta_pm != 0 and not nan
      3. p_value_valid: p_pm is a valid float (not nan/inf)
      4. n_obs_sufficient: nobs >= 1000
      5. surface_controls_included: all SURFACE_FEATURE_COLS present

    Args:
        model_result: OLSStageResult or None
        beta_pm: beta coefficient for pm_proxy
        p_pm: p-value for pm_proxy
        surface_cols: List of surface feature column names used

    Returns:
        Tuple (all_activated: bool, indicators: Dict[str, bool])
    """
    import math

    indicators = {}

    # 1. Model fitted
    indicators['model_fitted'] = model_result is not None

    # 2. beta_pm nonzero
    indicators['beta_pm_nonzero'] = (
        not math.isnan(beta_pm) and beta_pm != 0.0
    )

    # 3. p_value valid
    indicators['p_value_valid'] = (
        not math.isnan(p_pm) and not math.isinf(p_pm)
    )

    # 4. n_obs sufficient
    if model_result is not None:
        nobs = getattr(model_result, 'nobs', 0)
        indicators['n_obs_sufficient'] = nobs >= 1000
    else:
        indicators['n_obs_sufficient'] = False

    # 5. Surface controls included
    if surface_cols:
        indicators['surface_controls_included'] = all(
            col in SURFACE_FEATURE_COLS for col in surface_cols
        )
    else:
        indicators['surface_controls_included'] = False

    all_activated = all(indicators.values())
    return all_activated, indicators


def check_gate(
    beta_pm: float,
    p_pm: float,
    beta_pm_reduced: float,
    significance_level: float = 0.05,
    model_name: str = '',
) -> GateResult:
    """Check gate for a single SBERT model.

    Gate criterion:
      - beta_pm > 0 (positive direction)
      - p_pm < significance_level (statistically significant)
    Secondary check:
      - |beta_pm_full / beta_pm_reduced| > 0.5 (PM effect retained after controls)

    Args:
        beta_pm: beta_pm from Stage 2 (full model)
        p_pm: p-value from Stage 2 (full model)
        beta_pm_reduced: beta_pm from Stage 1 (pm-only model)
        significance_level: Significance threshold (default 0.05)
        model_name: Model name for logging

    Returns:
        GateResult
    """
    import math

    beta_pm_positive = (not math.isnan(beta_pm)) and (beta_pm > 0)
    p_significant = (not math.isnan(p_pm)) and (p_pm < significance_level)

    # Secondary check: PM effect retained
    if (not math.isnan(beta_pm_reduced)) and (beta_pm_reduced != 0) and (not math.isnan(beta_pm)):
        ratio = abs(beta_pm / beta_pm_reduced)
        secondary_check_pass = ratio > 0.5
    else:
        secondary_check_pass = False

    gate_pass = beta_pm_positive and p_significant

    return GateResult(
        model_name=model_name,
        gate_pass=gate_pass,
        beta_pm_positive=beta_pm_positive,
        p_significant=p_significant,
        beta_pm_value=float(beta_pm),
        p_value=float(p_pm),
        secondary_check_pass=secondary_check_pass,
    )


def evaluate_cross_model_gate(
    mediation_results: Dict[str, MediationResult],
    models_required: int = 2,
    significance_level: float = 0.05,
) -> OverallGateResult:
    """Evaluate >=2/3 gate criterion across all SBERT models.

    Args:
        mediation_results: Dict mapping model_name -> MediationResult
        models_required: Minimum number of models that must pass (default 2)
        significance_level: Significance threshold (default 0.05)

    Returns:
        OverallGateResult
    """
    gate_results = {}
    models_passed = 0

    for model_name, med_result in mediation_results.items():
        gate_result = check_gate(
            beta_pm=med_result.beta_pm_full,
            p_pm=med_result.stage_full.p_pm,
            beta_pm_reduced=med_result.beta_pm_reduced,
            significance_level=significance_level,
            model_name=model_name,
        )
        gate_results[model_name] = gate_result
        if gate_result.gate_pass:
            models_passed += 1

    overall_pass = models_passed >= models_required

    if overall_pass:
        interpretation = (
            f"GATE PASS: PM-proxy positively predicts C_sem^H←A above surface controls "
            f"in {models_passed}/{len(mediation_results)} SBERT models "
            f"(required: {models_required}). Hypothesis H-M4 CONFIRMED."
        )
    else:
        interpretation = (
            f"GATE FAIL: PM-proxy effect not sufficiently robust. "
            f"Only {models_passed}/{len(mediation_results)} models passed "
            f"(required: {models_required}). Hypothesis H-M4 NOT CONFIRMED."
        )

    logger.info(f"[H-M4 GATE] {'PASS' if overall_pass else 'FAIL'}: "
                f"{models_passed}/{len(mediation_results)} models passed")

    return OverallGateResult(
        overall_pass=overall_pass,
        models_passed=models_passed,
        models_required=models_required,
        gate_results=gate_results,
        interpretation=interpretation,
    )


def generate_gate_report(overall_result: OverallGateResult) -> str:
    """Generate human-readable gate summary string for 04_validation.md.

    Args:
        overall_result: OverallGateResult from evaluate_cross_model_gate()

    Returns:
        Multi-line string with gate summary
    """
    lines = [
        "## H-M4 Gate Evaluation",
        "",
        f"**Overall Gate:** {'PASS' if overall_result.overall_pass else 'FAIL'}",
        f"**Models Passed:** {overall_result.models_passed}/{len(overall_result.gate_results)}",
        f"**Models Required:** {overall_result.models_required}",
        "",
        "### Per-Model Results",
        "",
    ]

    for model_name, gate_result in overall_result.gate_results.items():
        lines += [
            f"#### {model_name}",
            f"- Gate Pass: {gate_result.gate_pass}",
            f"- beta_PM > 0: {gate_result.beta_pm_positive} (beta={gate_result.beta_pm_value:.4f})",
            f"- p < 0.05: {gate_result.p_significant} (p={gate_result.p_value:.4f})",
            f"- PM effect retained (>0.5): {gate_result.secondary_check_pass}",
            "",
        ]

    lines += [
        "### Interpretation",
        "",
        overall_result.interpretation,
    ]

    return "\n".join(lines)
