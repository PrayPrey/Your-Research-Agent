"""Gate verification for H-M1 MUST_WORK gate."""
import logging

logger = logging.getLogger(__name__)


def verify_gate(
    preservation_rate: float,
    stratum_ece: float,
    clean_ece: float,
    h_e1_delta: float = 0.071,
) -> tuple:
    """
    Returns (passed: bool, indicators: dict).
    indicators keys:
      preservation_rate_ok    - preservation_rate >= 0.80
      delta_ece_positive      - (stratum_ece - clean_ece) > 0
      consistent_with_h_e1   - |delta_ece - h_e1_delta| < 0.05
    Gate passes iff preservation_rate_ok AND delta_ece_positive.
    """
    delta_ece = stratum_ece - clean_ece
    indicators = {
        "preservation_rate_ok":  preservation_rate >= 0.80,
        "delta_ece_positive":    delta_ece > 0,
        "consistent_with_h_e1": abs(delta_ece - h_e1_delta) < 0.05,
        "preservation_rate":    preservation_rate,
        "stratum_ece":          stratum_ece,
        "clean_ece":            clean_ece,
        "delta_ece":            delta_ece,
        "h_e1_delta":           h_e1_delta,
    }
    passed = indicators["preservation_rate_ok"] and indicators["delta_ece_positive"]
    logger.info(
        "Gate: passed=%s pres_rate=%.4f delta_ece=%.4f consistent_with_h_e1=%s",
        passed, preservation_rate, delta_ece, indicators["consistent_with_h_e1"]
    )
    if not passed:
        logger.warning(
            "[PIVOT] Gate FAIL — restricting ΔECE claim to AdvGLUE human-verified subset only; "
            "document ANLI limitation; narrow scope"
        )
    return passed, indicators
