import numpy as np
from scipy.stats import bootstrap
from sklearn.metrics import roc_auc_score
from typing import Dict, Tuple


def compute_auroc_with_ci(
    y_true: np.ndarray,
    scores: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
    confidence_level: float = 0.95,
) -> Tuple[float, float, float]:
    # Scores are POSITIVE (negated log-probs from H-E1 convention).
    # Higher score = more uncertain = wrong → negate for roc_auc_score.
    auroc = roc_auc_score(y_true, -scores)

    def stat(yt, sc):
        if len(np.unique(yt)) < 2:
            return np.nan
        return roc_auc_score(yt, -sc)

    res = bootstrap(
        (y_true, scores), stat,
        n_resamples=n_bootstrap,
        confidence_level=confidence_level,
        paired=True,
        method="percentile",
        random_state=seed,
    )
    return auroc, float(res.confidence_interval.low), float(res.confidence_interval.high)


def compute_diff_ci(
    y_true: np.ndarray,
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
    confidence_level: float = 0.95,
) -> Dict[str, float]:
    diff = float(roc_auc_score(y_true, -scores_a) - roc_auc_score(y_true, -scores_b))

    def stat(yt, sa, sb):
        if len(np.unique(yt)) < 2:
            return np.nan
        return roc_auc_score(yt, -sa) - roc_auc_score(yt, -sb)

    res = bootstrap(
        (y_true, scores_a, scores_b), stat,
        n_resamples=n_bootstrap,
        confidence_level=confidence_level,
        paired=True,
        method="percentile",
        random_state=seed,
    )
    return {
        "diff": diff,
        "ci_lower": float(res.confidence_interval.low),
        "ci_upper": float(res.confidence_interval.high),
    }


def _collect_bootstrap_dist(
    labels: np.ndarray,
    scores: np.ndarray,
    n_bootstrap: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = len(labels)
    vals = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        if len(np.unique(labels[idx])) < 2:
            continue
        vals.append(roc_auc_score(labels[idx], -scores[idx]))
    return np.array(vals)


def compute_auroc_table(
    data: Dict,
    n_bootstrap: int = 1000,
    seed: int = 42,
    confidence_level: float = 0.95,
) -> Dict:
    auroc_out = {}
    bootstrap_samples = {}

    for (model, dataset, agg), (scores, labels) in data.items():
        auroc, ci_lo, ci_hi = compute_auroc_with_ci(
            labels, scores, n_bootstrap, seed, confidence_level
        )
        auroc_out[(model, dataset, agg)] = {
            "auroc": auroc, "ci_lower": ci_lo, "ci_upper": ci_hi
        }
        bootstrap_samples[(model, dataset, agg)] = _collect_bootstrap_dist(
            labels, scores, n_bootstrap, seed
        )

    diff_out = {}
    pairs = set((m, d) for (m, d, _) in data.keys())
    for (model, dataset) in pairs:
        key_min  = (model, dataset, "min")
        key_mean = (model, dataset, "mean")
        if key_min not in data or key_mean not in data:
            continue
        scores_min, labels = data[key_min]
        scores_mean = data[key_mean][0]
        diff_out[(model, dataset)] = compute_diff_ci(
            labels, scores_min, scores_mean, n_bootstrap, seed, confidence_level
        )

    return {
        "auroc": auroc_out,
        "diff": diff_out,
        "bootstrap_samples": bootstrap_samples,
    }
