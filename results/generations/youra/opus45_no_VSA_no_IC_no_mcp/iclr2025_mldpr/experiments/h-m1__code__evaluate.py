"""Gate checking and summary for h-m1 correlation experiment."""

from config import CONFIG


def check_gate(analysis: dict) -> bool:
    """MUST_WORK gate: fails if r_pearson > -0.2 or r_pearson >= 0."""
    r = analysis.get("r_pearson", 0)
    fail_threshold = CONFIG["fail_r_threshold"]
    return r < fail_threshold and r < 0


def summarize(analysis: dict, names: list, dnsi: "np.ndarray", gap: "np.ndarray") -> dict:
    """Generate summary for correlation results."""
    import numpy as np

    gate_passed = check_gate(analysis)

    return {
        "n_benchmarks": analysis["n"],
        "benchmarks": names,
        "r_pearson": analysis["r_pearson"],
        "p_pearson": analysis["p_pearson"],
        "r_spearman": analysis["r_spearman"],
        "p_spearman": analysis["p_spearman"],
        "ci_95": [analysis["ci_95_lower"], analysis["ci_95_upper"]],
        "hypothesis_supported": analysis["hypothesis_supported"],
        "gate_passed": gate_passed,
        "dnsi_values": {n: float(d) for n, d in zip(names, dnsi)},
        "gap_values": {n: float(g) for n, g in zip(names, gap)},
    }
