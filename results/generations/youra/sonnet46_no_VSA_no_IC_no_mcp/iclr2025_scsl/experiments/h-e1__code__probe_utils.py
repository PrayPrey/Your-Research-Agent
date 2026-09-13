import logging
import numpy as np
import torch
from sklearn.linear_model import LogisticRegression

from config import PROBE_C, PROBE_MAX_ITER, PROBE_SOLVER
from data_utils import get_balanced_probe_indices


def train_probe(features, labels):
    """LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs'). fit and return."""
    clf = LogisticRegression(C=PROBE_C, max_iter=PROBE_MAX_ITER, solver=PROBE_SOLVER, n_jobs=-1)
    clf.fit(features, labels)
    return clf


def eval_probe(clf, features, labels):
    """Returns accuracy score."""
    return float(clf.score(features, labels))


def compute_ratio(
    feats_val,
    task_lbls_val,
    spur_lbls_val,
    metadata_val,
    feats_test,
    task_lbls_test,
    spur_lbls_test,
    seed,
    paradigm,
):
    """
    Group-balanced probe train split from val, evaluate on test.
    Returns {'ratio': float, 'spurious_acc': float, 'task_acc': float}
    """
    np.random.seed(seed)
    torch.manual_seed(seed)

    idx = get_balanced_probe_indices(metadata_val, seed)

    X_tr = feats_val[idx].numpy()
    y_task_tr = task_lbls_val[idx].numpy()
    y_spur_tr = spur_lbls_val[idx].numpy()

    X_te = feats_test.numpy()
    y_task_te = task_lbls_test.numpy()
    y_spur_te = spur_lbls_test.numpy()

    clf_task = train_probe(X_tr, y_task_tr)
    clf_spur = train_probe(X_tr, y_spur_tr)

    acc_task = eval_probe(clf_task, X_te, y_task_te)
    acc_spur = eval_probe(clf_spur, X_te, y_spur_te)

    assert acc_task > 0.5, f"Task probe below chance: {acc_task:.3f}"
    assert acc_spur > 0.5, f"Spurious probe below chance: {acc_spur:.3f}"

    ratio = acc_spur / acc_task
    logging.info(
        f"Paradigm={paradigm}, seed={seed}, spurious_acc={acc_spur:.3f}, "
        f"task_acc={acc_task:.3f}, ratio={ratio:.4f}"
    )
    return {'ratio': ratio, 'spurious_acc': acc_spur, 'task_acc': acc_task}
