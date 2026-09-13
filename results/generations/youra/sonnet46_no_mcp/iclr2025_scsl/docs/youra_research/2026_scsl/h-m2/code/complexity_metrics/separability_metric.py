import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import List, Dict, Any, Optional


def probe_learning_curve(
    features: np.ndarray,
    labels: np.ndarray,
    n_samples_list: List[int],
    seeds: List[int],
    c: float = 1.0,
    max_iter: int = 1000,
) -> Dict[str, Any]:
    assert len(features) == len(labels), "features and labels must have same length"

    per_seed_accs = np.zeros((len(seeds), len(n_samples_list)))

    for i, seed in enumerate(seeds):
        rng = np.random.RandomState(seed)
        for j, n in enumerate(n_samples_list):
            n_actual = min(n, len(features))
            idx = rng.choice(len(features), size=n_actual, replace=False)
            X_train, y_train = features[idx], labels[idx]

            if len(np.unique(y_train)) < 2:
                per_seed_accs[i, j] = 0.5
                continue

            clf = LogisticRegression(C=c, max_iter=max_iter, random_state=seed, solver="lbfgs")
            clf.fit(X_train, y_train)
            per_seed_accs[i, j] = clf.score(features, labels)

    mean_accs = per_seed_accs.mean(axis=0).tolist()
    std_accs = per_seed_accs.std(axis=0).tolist()

    log_n = np.log(np.array(n_samples_list, dtype=float))
    auc = float(np.trapz(mean_accs, log_n) / (log_n[-1] - log_n[0]))

    samples_to_90pct: Optional[int] = None
    for n, acc in zip(n_samples_list, mean_accs):
        if acc >= 0.90:
            samples_to_90pct = n
            break

    return {
        "n_samples_list": n_samples_list,
        "mean_accs": mean_accs,
        "std_accs": std_accs,
        "per_seed_accs": per_seed_accs,
        "auc": auc,
        "samples_to_90pct": samples_to_90pct,
    }


def compute_separability_metric(
    features: np.ndarray,
    spurious_labels: np.ndarray,
    core_labels: np.ndarray,
    n_samples_list: List[int],
    seeds: List[int],
) -> Dict[str, Any]:
    spurious_curve = probe_learning_curve(features, spurious_labels, n_samples_list, seeds)
    core_curve = probe_learning_curve(features, core_labels, n_samples_list, seeds)

    spurious_auc = spurious_curve["auc"]
    core_auc = core_curve["auc"]

    auc_ratio = spurious_auc / (core_auc + 1e-10)
    direction_correct = spurious_auc > core_auc  # spurious easier = higher AUC with fewer samples

    # p_value from last t-test across seeds at full N
    from scipy import stats
    spurious_full = spurious_curve["per_seed_accs"][:, -1]
    core_full = core_curve["per_seed_accs"][:, -1]
    t_stat, p_value = stats.ttest_ind(spurious_full, core_full, equal_var=False)

    return {
        "spurious_curve": spurious_curve,
        "core_curve": core_curve,
        "auc_ratio": float(auc_ratio),
        "samples_to_90_spurious": spurious_curve["samples_to_90pct"],
        "samples_to_90_core": core_curve["samples_to_90pct"],
        "direction_correct": bool(direction_correct),
        "spurious_auc": float(spurious_auc),
        "core_auc": float(core_auc),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
    }
