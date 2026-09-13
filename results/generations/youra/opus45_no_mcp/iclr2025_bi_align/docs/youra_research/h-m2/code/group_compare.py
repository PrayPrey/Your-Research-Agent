"""H-M2 Group Compare: Type A vs Type B rate comparison with gate check."""
from scipy import stats
from threshold_sweep import high_conf_rate


def compare_groups(records: list, threshold: float = 0.7) -> dict:
    """
    Compare high-conf rates Type A vs Type B.
    Returns gate_pass based on:
      PASS: rate_diff < 0.15 OR conflation_score > 0.85
    """
    rate_a, n_high_a, n_total_a = high_conf_rate(records, "A", threshold)
    rate_b, n_high_b, n_total_b = high_conf_rate(records, "B", threshold)

    rate_diff = abs(rate_a - rate_b)
    conflation_score = 1 - rate_diff

    # Chi-square test for independence
    n_low_a = n_total_a - n_high_a
    n_low_b = n_total_b - n_high_b
    contingency = [[n_high_a, n_high_b], [n_low_a, n_low_b]]

    try:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    except ValueError:
        chi2, p_value = 0.0, 1.0

    # Gate logic
    gate_pass = (rate_diff < 0.15) or (conflation_score > 0.85)
    gate_fail = (rate_diff > 0.3) and (conflation_score < 0.7)

    return {
        "rate_A": rate_a,
        "rate_B": rate_b,
        "rate_difference": rate_diff,
        "conflation_score": conflation_score,
        "n_high_A": n_high_a,
        "n_high_B": n_high_b,
        "n_total_A": n_total_a,
        "n_total_B": n_total_b,
        "chi2": chi2,
        "chi2_p": p_value,
        "gate_pass": gate_pass,
        "gate_fail": gate_fail,
        "threshold": threshold,
    }
