"""Statistical analysis for H-M3 repair loop results."""
from collections import defaultdict

import numpy as np
from scipy.stats import spearmanr

# H-M2 empirical specificity ranks (fixed from 04_validation.md)
# Pyright: 1 (highest, 24358 chars avg), Execution: 2 (202), Mypy: 3 (49), Z3: 4 (2)
SPECIFICITY_RANKS = {"pyright": 1, "execution": 2, "mypy": 3, "z3": 4}

# Mean char_count from H-M2 (for scatter plot)
H_M2_CHAR_COUNTS = {"pyright": 24358, "execution": 202, "mypy": 49, "z3": 2}


def compute_iter_rates(results: list) -> dict:
    """Compute per-category iter1/2/3 success rates and bootstrap CIs."""
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)

    rates = {}
    for cat, recs in by_cat.items():
        n = len(recs)
        iter1 = [r.iter1_pass for r in recs]
        iter2 = [r.iter2_pass for r in recs if r.iter2_pass is not None]
        iter3 = [r.iter3_pass for r in recs if r.iter3_pass is not None]

        iter1_rate = float(np.mean(iter1)) if iter1 else 0.0
        iter2_rate = float(np.mean(iter2)) if iter2 else 0.0
        iter3_rate = float(np.mean(iter3)) if iter3 else 0.0

        ci1 = bootstrap_ci(iter1) if iter1 else (0.0, 0.0)

        # mean iterations to pass (among those that passed)
        passed_iters = [r.iterations_to_pass for r in recs if r.iterations_to_pass is not None]
        mean_iters = float(np.mean(passed_iters)) if passed_iters else None

        rates[cat] = {
            "n": n,
            "iter1_rate": iter1_rate,
            "iter2_rate": iter2_rate,
            "iter3_rate": iter3_rate,
            "iter1_ci_lo": ci1[0],
            "iter1_ci_hi": ci1[1],
            "mean_iters_to_pass": mean_iters,
            "char_count": H_M2_CHAR_COUNTS.get(cat, 0),
        }
    return rates


def bootstrap_ci(passes: list, n_bootstrap: int = 1000, ci: float = 0.95) -> tuple:
    """Bootstrap confidence interval for a success rate."""
    arr = np.array(passes, dtype=float)
    n = len(arr)
    if n == 0:
        return (0.0, 0.0)
    boot_means = [np.mean(np.random.choice(arr, n, replace=True)) for _ in range(n_bootstrap)]
    alpha = (1 - ci) / 2
    return (float(np.percentile(boot_means, alpha * 100)), float(np.percentile(boot_means, (1 - alpha) * 100)))


def run_spearman(iter_rates: dict, include_z3: bool = True) -> dict:
    """Spearman correlation between specificity LEVEL and iter1_rates.

    Uses inverted ranks so that pyright (rank=1, highest specificity) maps to
    specificity_level=4, z3 (rank=4, lowest) maps to level=1.
    Gate ρ > 0 then means: higher specificity level → higher repair rate (hypothesis confirmed).
    """
    n_cats = len(SPECIFICITY_RANKS)
    cats = ["pyright", "execution", "mypy"]
    if include_z3 and "z3" in iter_rates and iter_rates["z3"]["n"] >= 5:
        cats.append("z3")

    available = [c for c in cats if c in iter_rates]
    if len(available) < 2:
        return {"rho": 0.0, "pval": 1.0, "n_categories": len(available), "gate_pass": False}

    # Invert ranks: specificity_level = n_cats - rank + 1 (pyright: 4, execution: 3, mypy: 2, z3: 1)
    ranks = [n_cats - SPECIFICITY_RANKS[c] + 1 for c in available]
    rates = [iter_rates[c]["iter1_rate"] for c in available]

    if len(set(rates)) == 1:
        # All identical — no correlation computable
        rho, pval = 0.0, 1.0
    else:
        rho, pval = spearmanr(ranks, rates)
        rho = float(rho)
        pval = float(pval)

    return {
        "rho": rho,
        "pval": pval,
        "n_categories": len(available),
        "categories_used": available,
        "ranks_used": ranks,
        "rates_used": rates,
        "gate_pass": gate_verdict(rho),
    }


def gate_verdict(rho: float) -> bool:
    """SHOULD_WORK gate: Spearman ρ > 0."""
    return rho > 0


def run_ablations(results: list, iter_rates: dict) -> dict:
    """4 ablation analyses."""
    # Ablation 1: without Z3
    spearman_no_z3 = run_spearman(iter_rates, include_z3=False)

    # Ablation 2: iter2_rate correlation
    iter2_rates = {c: {"iter1_rate": v["iter2_rate"], "n": v["n"]} for c, v in iter_rates.items()}
    spearman_iter2 = run_spearman(iter2_rates, include_z3=True)

    # Ablation 3: by dataset (humaneval vs mbpp)
    he_results = [r for r in results if r.problem_id.startswith("HE_") or r.problem_id.startswith("HumanEval")]
    mbpp_results = [r for r in results if r.problem_id.startswith("MB_") or r.problem_id.startswith("Mbpp")]
    he_rates = compute_iter_rates(he_results) if he_results else {}
    mbpp_rates = compute_iter_rates(mbpp_results) if mbpp_results else {}
    spearman_he = run_spearman(he_rates) if he_rates else {}
    spearman_mbpp = run_spearman(mbpp_rates) if mbpp_rates else {}

    # Ablation 4: by bug_type
    by_bug = defaultdict(list)
    for r in results:
        by_bug[r.bug_type].append(r)
    bug_rates = {bt: compute_iter_rates(recs) for bt, recs in by_bug.items() if len(recs) >= 5}

    return {
        "without_z3": spearman_no_z3,
        "iter2_correlation": spearman_iter2,
        "by_dataset": {"humaneval": spearman_he, "mbpp": spearman_mbpp},
        "by_bug_type": {bt: run_spearman(rates) for bt, rates in bug_rates.items()},
    }


def run_analysis(results: list) -> dict:
    """Full analysis: iter_rates + spearman + ablations + gate."""
    iter_rates = compute_iter_rates(results)
    spearman_with_z3 = run_spearman(iter_rates, include_z3=True)
    spearman_without_z3 = run_spearman(iter_rates, include_z3=False)
    ablations = run_ablations(results, iter_rates)

    gate_pass = spearman_with_z3["gate_pass"] or spearman_without_z3["gate_pass"]

    return {
        "iter_rates": iter_rates,
        "spearman_with_z3": spearman_with_z3,
        "spearman_without_z3": spearman_without_z3,
        "gate_pass": gate_pass,
        "gate_rho": spearman_with_z3["rho"],
        "ablations": ablations,
        "n_total_results": len(results),
    }
