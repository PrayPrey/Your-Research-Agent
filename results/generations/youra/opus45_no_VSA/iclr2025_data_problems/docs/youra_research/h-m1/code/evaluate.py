import numpy as np
from detect import compute_ccr


def bootstrap_ccr_diff(ccr_ppl: np.ndarray, ccr_rand: np.ndarray,
                       n_bootstrap: int = 1000) -> tuple[float, float, np.ndarray]:
    """
    Bootstrap test for CCR difference.
    Returns (mean_diff, p_value, bootstrap_diffs).
    """
    rng = np.random.default_rng(42)
    diffs = []

    for _ in range(n_bootstrap):
        idx_ppl = rng.choice(len(ccr_ppl), len(ccr_ppl), replace=True)
        idx_rand = rng.choice(len(ccr_rand), len(ccr_rand), replace=True)
        diff = np.mean(ccr_ppl[idx_ppl]) - np.mean(ccr_rand[idx_rand])
        diffs.append(diff)

    diffs = np.array(diffs)
    mean_diff = np.mean(ccr_ppl) - np.mean(ccr_rand)
    # p-value: proportion of bootstrap samples where diff <= 0
    p_value = np.mean(diffs <= 0)

    return mean_diff, p_value, diffs


def evaluate_all(results: dict, benchmark: list[dict], n: int = 8) -> dict:
    """Compute CCR for all strategy-seed combinations."""
    ccr_results = {}
    for strategy, seeds_data in results.items():
        ccr_results[strategy] = {}
        for seed, data in seeds_data.items():
            corpus = data["corpus"]
            ccr = compute_ccr(corpus, benchmark, n=n)
            ccr_results[strategy][seed] = ccr
            print(f"CCR[{strategy}][seed={seed}] = {ccr:.4f}")
    return ccr_results
