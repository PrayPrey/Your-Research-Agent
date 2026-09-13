import numpy as np
from scipy import stats


def verify_invariance_mechanism(mps_verbatim: np.ndarray, mps_paraphrase: np.ndarray) -> dict:
    mean_v = np.mean(mps_verbatim)
    mean_p = np.mean(mps_paraphrase)
    std_v = np.std(mps_verbatim)

    mechanism_active = mean_p > mean_v
    difference = mean_p - mean_v
    effect_size = difference / std_v if std_v > 0 else 0.0

    t_stat, p_value = stats.ttest_ind(mps_paraphrase, mps_verbatim)

    print(f"[MECHANISM CHECK] Verbatim MPS: {mean_v:.4f} (std: {std_v:.4f})")
    print(f"[MECHANISM CHECK] Paraphrase MPS: {mean_p:.4f} (std: {np.std(mps_paraphrase):.4f})")
    print(f"[MECHANISM CHECK] Difference: {difference:.4f}")
    print(f"[MECHANISM CHECK] Effect Size (Cohen's d): {effect_size:.4f}")
    print(f"[MECHANISM CHECK] t-statistic: {t_stat:.4f}, p-value: {p_value:.4e}")
    print(f"[MECHANISM CHECK] Mechanism Active: {mechanism_active}")

    return {
        "mechanism_active": bool(mechanism_active),
        "mps_verbatim": float(mean_v),
        "mps_paraphrase": float(mean_p),
        "std_verbatim": float(std_v),
        "std_paraphrase": float(np.std(mps_paraphrase)),
        "difference": float(difference),
        "effect_size": float(effect_size),
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
    }


def aggregate_across_seeds(results_per_seed: list) -> dict:
    effect_sizes = [r["effect_size"] for r in results_per_seed]
    differences = [r["difference"] for r in results_per_seed]
    mechanism_active_count = sum(1 for r in results_per_seed if r["mechanism_active"])

    return {
        "mean_effect_size": float(np.mean(effect_sizes)),
        "std_effect_size": float(np.std(effect_sizes)),
        "mean_difference": float(np.mean(differences)),
        "std_difference": float(np.std(differences)),
        "mechanism_active_count": mechanism_active_count,
        "total_seeds": len(results_per_seed),
        "reproducibility": f"{mechanism_active_count}/{len(results_per_seed)} seeds",
    }
