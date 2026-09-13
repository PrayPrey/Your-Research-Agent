def evaluate_gate(r_partial: float, p_val: float, boot_ci_lower: float) -> dict:
    passes = (r_partial > 0) and (p_val < 0.05) and (abs(r_partial) >= 0.15)
    return {
        'passes_gate': passes,
        'r_partial': r_partial,
        'p_val': p_val,
        'boot_ci_lower': boot_ci_lower,
        'r_threshold': 0.15,
        'alpha': 0.05
    }
