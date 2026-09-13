import numpy as np
from sklearn.linear_model import LogisticRegression


def compute_cv_for_feature(
    features: np.ndarray,
    labels: np.ndarray,
    n_subsets: int = 5,
    subset_frac: float = 0.2,
    n_epochs: int = 10,
    seed: int = 42,
) -> tuple:
    rng = np.random.RandomState(seed)
    n_samples = len(features)
    subset_size = int(n_samples * subset_frac)

    C_values = np.logspace(-3, 2, n_epochs)
    trajectories = []

    for s in range(n_subsets):
        idx = rng.choice(n_samples, subset_size, replace=False)
        X, y = features[idx], labels[idx]
        accs = []
        for C in C_values:
            clf = LogisticRegression(C=C, max_iter=1000, random_state=seed, solver="lbfgs")
            clf.fit(X, y)
            accs.append(clf.score(X, y))
        trajectories.append(accs)

    improvement_rates = [traj[-1] - traj[0] for traj in trajectories]
    cv = np.std(improvement_rates) / (np.mean(improvement_rates) + 1e-8)

    return cv, trajectories


def run_cv_analysis(
    features: np.ndarray,
    y_labels: np.ndarray,
    place_labels: np.ndarray,
    n_subsets: int = 5,
    subset_frac: float = 0.2,
    n_epochs: int = 10,
    seed: int = 42,
) -> dict:
    background_cv, background_traj = compute_cv_for_feature(
        features, place_labels, n_subsets, subset_frac, n_epochs, seed
    )
    bird_type_cv, bird_type_traj = compute_cv_for_feature(
        features, y_labels, n_subsets, subset_frac, n_epochs, seed
    )

    return {
        "background_cv": float(background_cv),
        "bird_type_cv": float(bird_type_cv),
        "trajectories": {
            "background": background_traj,
            "bird_type": bird_type_traj,
        },
    }
