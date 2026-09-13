import numpy as np
from scipy import stats
from tqdm import tqdm


def tercile_continuation_analysis(
    deltas: np.ndarray,
    continuations: np.ndarray,
    conversation_ids: np.ndarray,
    n_boot: int = 2000,
    seed: int = 42
) -> dict:
    t1, t2 = np.percentile(deltas, [33.33, 66.67])
    terciles = np.where(deltas <= t1, 1, np.where(deltas <= t2, 2, 3))

    tercile_rates = {}
    tercile_counts = {}
    for t in [1, 2, 3]:
        mask = terciles == t
        tercile_rates[t] = continuations[mask].mean()
        tercile_counts[t] = mask.sum()

    rates = [tercile_rates[1], tercile_rates[2], tercile_rates[3]]
    monotonic = rates[0] > rates[1] > rates[2]

    rho, p_naive = stats.spearmanr(deltas, continuations)
    p_robust, boot_rhos = cluster_bootstrap_pvalue(
        deltas, continuations, conversation_ids, n_boot=n_boot, seed=seed
    )

    return {
        "tercile_rates": tercile_rates,
        "tercile_counts": tercile_counts,
        "tercile_thresholds": {"t1": float(t1), "t2": float(t2)},
        "monotonic": monotonic,
        "spearman_rho": float(rho),
        "p_naive": float(p_naive),
        "p_robust": float(p_robust),
        "boot_rhos": boot_rhos,
        "n_samples": len(deltas)
    }


def cluster_bootstrap_pvalue(
    deltas: np.ndarray,
    continuations: np.ndarray,
    conversation_ids: np.ndarray,
    n_boot: int = 2000,
    seed: int = 42
) -> tuple[float, np.ndarray]:
    unique_ids = np.unique(conversation_ids)
    id_to_indices = {cid: np.where(conversation_ids == cid)[0] for cid in unique_ids}
    C = len(unique_ids)

    rng = np.random.default_rng(seed)
    boot_rhos = np.empty(n_boot)

    for b in tqdm(range(n_boot), desc="Bootstrap"):
        sampled_ids = rng.choice(unique_ids, size=C, replace=True)
        idx = np.concatenate([id_to_indices[cid] for cid in sampled_ids])

        if len(np.unique(continuations[idx])) < 2:
            boot_rhos[b] = 0.0
            continue

        rho_b, _ = stats.spearmanr(deltas[idx], continuations[idx])
        boot_rhos[b] = 0.0 if np.isnan(rho_b) else rho_b

    p_robust = 2 * min(np.mean(boot_rhos >= 0), np.mean(boot_rhos <= 0))
    p_robust = min(p_robust, 1.0)

    return p_robust, boot_rhos


def verify_mechanism(tercile_rates: dict, p_robust: float, alpha: float = 0.05) -> dict:
    t1_rate = tercile_rates[1]
    t2_rate = tercile_rates[2]
    t3_rate = tercile_rates[3]

    mechanism_active = t1_rate > t3_rate
    monotonic = t1_rate > t2_rate > t3_rate
    effect_size = t1_rate - t3_rate
    significant = p_robust < alpha

    passes_gate = monotonic and significant

    return {
        "mechanism_active": mechanism_active,
        "monotonic_trend": monotonic,
        "effect_size": float(effect_size),
        "p_robust": float(p_robust),
        "significant": significant,
        "passes_gate": passes_gate
    }
