import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr, spearmanr

MIN_SAMPLE_COUNT = 500


def compute_disagreement_rate(bai_scores, reward_scores):
    """Compute disagreement rate using quartile analysis."""
    bai_arr = np.array(bai_scores).reshape(-1, 1)
    reward_arr = np.array(reward_scores).reshape(-1, 1)

    bai_z = StandardScaler().fit_transform(bai_arr).flatten()
    reward_z = StandardScaler().fit_transform(reward_arr).flatten()

    q25_bai, q75_bai = np.percentile(bai_z, [25, 75])
    q25_rw, q75_rw = np.percentile(reward_z, [25, 75])

    hh = (bai_z >= q75_bai) & (reward_z >= q75_rw)  # high-high
    hl = (bai_z >= q75_bai) & (reward_z <= q25_rw)  # high-low (disagreement)
    lh = (bai_z <= q25_bai) & (reward_z >= q75_rw)  # low-high (disagreement)
    ll = (bai_z <= q25_bai) & (reward_z <= q25_rw)  # low-low

    disagreement_rate = (hl.sum() + lh.sum()) / len(bai_scores)

    return {
        "disagreement_rate": disagreement_rate,
        "hh_count": int(hh.sum()),
        "hl_count": int(hl.sum()),
        "lh_count": int(lh.sum()),
        "ll_count": int(ll.sum()),
        "bai_z": bai_z,
        "reward_z": reward_z,
        "q_bounds": {
            "q25_bai": q25_bai, "q75_bai": q75_bai,
            "q25_rw": q25_rw, "q75_rw": q75_rw,
        },
    }


def compute_correlations(bai_scores, reward_scores):
    """Compute Pearson and Spearman correlations."""
    pearson_r, pearson_p = pearsonr(bai_scores, reward_scores)
    spearman_r, spearman_p = spearmanr(bai_scores, reward_scores)

    return {
        "pearson_r": pearson_r,
        "pearson_p": pearson_p,
        "spearman_r": spearman_r,
        "spearman_p": spearman_p,
    }


def verify_mechanism(results):
    """Verify mechanism validity checks."""
    checks = {}

    checks["bai_variance_ok"] = results.get("bai_variance", 0) > 0.01
    checks["reward_variance_ok"] = results.get("reward_variance", 0) > 0.01
    checks["disagreement_rate_valid"] = 0 < results.get("disagreement_rate", 0) < 0.5
    checks["sample_count_ok"] = results.get("sample_count", 0) >= MIN_SAMPLE_COUNT

    verification_passed = all(checks.values())

    return {**checks, "verification_passed": verification_passed}
