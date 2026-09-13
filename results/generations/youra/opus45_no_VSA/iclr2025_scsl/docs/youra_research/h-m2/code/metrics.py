from sklearn.metrics import accuracy_score


def per_group_accuracy(y_true: list, y_pred: list, groups: list) -> dict:
    accs = {}
    unique_groups = set(groups)
    for g in unique_groups:
        mask = [i for i, grp in enumerate(groups) if grp == g]
        if len(mask) > 0:
            yt = [y_true[i] for i in mask]
            yp = [y_pred[i] for i in mask]
            accs[g] = accuracy_score(yt, yp)
    return accs


def worst_group_accuracy(y_true: list, y_pred: list, groups: list) -> float:
    accs = per_group_accuracy(y_true, y_pred, groups)
    if len(accs) == 0:
        return 0.0
    return min(accs.values())
