import numpy as np


def bootstrap_delta(
    m1_scores: list,
    m2_scores: list,
    tasks: list,
    n_per_task: int = 100,
    n_resamples: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Bootstrap CI for macro-F1 delta (M1 - M2).
    m1_scores, m2_scores: flat list of per-example F1, ordered task0*n, task1*n, ...
    Returns {"ci_lower", "ci_upper", "samples", "delta", "m1_macro", "m2_macro"}
    """
    m1 = np.array(m1_scores)
    m2 = np.array(m2_scores)
    n_tasks = len(tasks)
    n_total = n_tasks * n_per_task

    assert len(m1) == n_total, f"Expected {n_total} scores, got {len(m1)}"
    assert len(m2) == n_total, f"Expected {n_total} scores, got {len(m2)}"

    # Observed macro-F1
    m1_macro = m1.reshape(n_tasks, n_per_task).mean(axis=1).mean()
    m2_macro = m2.reshape(n_tasks, n_per_task).mean(axis=1).mean()
    observed_delta = float(m1_macro - m2_macro)

    rng = np.random.default_rng(seed)
    bootstrap_deltas = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n_total, size=n_total)
        m1_boot = m1[idx].reshape(n_tasks, n_per_task).mean(axis=1).mean()
        m2_boot = m2[idx].reshape(n_tasks, n_per_task).mean(axis=1).mean()
        bootstrap_deltas.append(float(m1_boot - m2_boot))

    samples = np.array(bootstrap_deltas)
    ci_lower = float(np.percentile(samples, 2.5))
    ci_upper = float(np.percentile(samples, 97.5))

    return {
        "delta": observed_delta,
        "m1_macro": float(m1_macro),
        "m2_macro": float(m2_macro),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "samples": samples,
    }
