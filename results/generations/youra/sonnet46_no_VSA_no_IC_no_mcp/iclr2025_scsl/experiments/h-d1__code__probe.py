import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedShuffleSplit
from config import PROBE_C, PROBE_MAX_ITER, SEEDS, CELEBA_PROBE_RESULTS_PATH


def train_probe(features, labels, seed, C=PROBE_C, max_iter=PROBE_MAX_ITER):
    clf = LogisticRegression(C=C, solver='lbfgs', max_iter=max_iter,
                             random_state=seed, n_jobs=-1)
    clf.fit(features, labels)
    return clf


def eval_probe(clf, features, labels):
    preds = clf.predict(features)
    return balanced_accuracy_score(labels, preds)


def compute_ratio_one_seed(features, task_labels, spurious_labels,
                            train_idx, test_idx, seed):
    X_train = features[train_idx]
    X_test  = features[test_idx]

    clf_s = train_probe(X_train, spurious_labels[train_idx], seed)
    spurious_acc = eval_probe(clf_s, X_test, spurious_labels[test_idx])

    clf_t = train_probe(X_train, task_labels[train_idx], seed)
    task_acc = eval_probe(clf_t, X_test, task_labels[test_idx])

    ratio = spurious_acc / max(task_acc, 1e-6)
    return {'spurious_acc': spurious_acc, 'task_acc': task_acc, 'ratio': ratio}


def build_balanced_split(task_labels, spurious_labels, all_idx, seed, test_frac=0.2):
    """Build group-balanced train/test split from given indices."""
    rng = np.random.default_rng(seed)
    groups = {}
    for t in [0, 1]:
        for s in [0, 1]:
            mask = (task_labels[all_idx] == t) & (spurious_labels[all_idx] == s)
            groups[(t, s)] = all_idx[mask]

    min_size = min(len(v) for v in groups.values())
    train_list, test_list = [], []
    for idx in groups.values():
        chosen = rng.choice(idx, size=min_size, replace=False)
        n_test = max(1, int(test_frac * min_size))
        test_list.append(chosen[:n_test])
        train_list.append(chosen[n_test:])

    return np.concatenate(train_list), np.concatenate(test_list)


def run_celeba_probing(features_by_paradigm, task_labels, spurious_labels,
                       all_idx, seeds=SEEDS, save_path=None):
    """
    5-seed probing for each paradigm.
    Returns {'erm': [ratio_s0..s4], 'moco': [ratio_s0..s4]}
    """
    results = {}
    for paradigm, features in features_by_paradigm.items():
        ratios = []
        for seed in seeds:
            train_idx, test_idx = build_balanced_split(
                task_labels, spurious_labels, all_idx, seed=seed)
            r = compute_ratio_one_seed(features, task_labels, spurious_labels,
                                       train_idx, test_idx, seed)
            ratios.append(r['ratio'])
            print(f"  [{paradigm}] seed={seed} spurious={r['spurious_acc']:.4f} "
                  f"task={r['task_acc']:.4f} ratio={r['ratio']:.4f}")
        results[paradigm] = ratios

    if save_path:
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"[probe] Saved CelebA probe results → {save_path}")

    return results
