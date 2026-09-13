import numpy as np
from scipy import stats
from typing import Dict, List
from config import CONFIG

def analyze_structure_effect(paired_results: List[Dict]) -> Dict:
    """McNemar chi2 + BCa-approx bootstrap CI + Cohen's d."""
    n = len(paired_results)

    structured_success = np.array([1 if r["structured_passed"] else 0 for r in paired_results])
    scrambled_success = np.array([1 if r["scrambled_passed"] else 0 for r in paired_results])

    structured_rate = structured_success.mean()
    scrambled_rate = scrambled_success.mean()
    delta = structured_rate - scrambled_rate

    # Discordant pairs for McNemar's test
    b = ((structured_success == 1) & (scrambled_success == 0)).sum()  # Structured wins
    c = ((structured_success == 0) & (scrambled_success == 1)).sum()  # Scrambled wins

    if b + c > 0:
        chi2 = (abs(b - c) - 1) ** 2 / (b + c)
        p_value = 1 - stats.chi2.cdf(chi2, df=1)
    else:
        p_value = 1.0

    # Bootstrap confidence interval
    bootstrap_deltas = []
    rng = np.random.default_rng(42)
    for _ in range(CONFIG["bootstrap_replicas"]):
        idx = rng.choice(n, n, replace=True)
        boot_delta = structured_success[idx].mean() - scrambled_success[idx].mean()
        bootstrap_deltas.append(boot_delta)
    ci_lower, ci_upper = np.percentile(bootstrap_deltas, [2.5, 97.5])

    # Cohen's d approximation for paired binary
    if structured_rate > 0 and scrambled_rate > 0:
        pooled_std = np.sqrt((structured_success.var() + scrambled_success.var()) / 2)
        cohens_d = delta / pooled_std if pooled_std > 0 else 0.0
    else:
        cohens_d = 0.0

    gate_pass = p_value < CONFIG["significance_alpha"] and delta > 0

    return {
        "n_samples": n,
        "structured_rate": float(structured_rate),
        "scrambled_rate": float(scrambled_rate),
        "delta": float(delta),
        "p_value": float(p_value),
        "ci_95": (float(ci_lower), float(ci_upper)),
        "discordant_structured_wins": int(b),
        "discordant_scrambled_wins": int(c),
        "cohens_d": float(cohens_d),
        "gate_pass": gate_pass,
    }

def gate_check(results: Dict, alpha: float = None) -> bool:
    alpha = alpha or CONFIG["significance_alpha"]
    return results["p_value"] < alpha and results["delta"] > 0
