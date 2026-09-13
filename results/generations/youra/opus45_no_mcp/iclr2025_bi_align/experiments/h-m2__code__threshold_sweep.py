"""H-M2 Threshold Sweep: High-confidence rate across thresholds."""
from loader import MODEL_FIELDS


def high_conf_rate(records: list, task_type: str, threshold: float, field: str = None) -> tuple:
    """
    Compute high-confidence rate for task_type.
    Returns (rate, n_high, n_total).
    If field is None, uses average across MODEL_FIELDS.
    """
    type_tasks = [t for t in records if t["task_type"] == task_type]
    n_total = len(type_tasks)
    if n_total == 0:
        return 0.0, 0, 0

    n_high = 0
    for t in type_tasks:
        if field:
            conf = t.get(field, 0)
        else:
            conf = sum(t.get(f, 0) for f in MODEL_FIELDS) / len(MODEL_FIELDS)
        if conf >= threshold:
            n_high += 1

    return n_high / n_total, n_high, n_total


def sweep_thresholds(records: list, thresholds: list = None) -> dict:
    """
    Sweep thresholds [0.5, 0.6, 0.7, 0.8, 0.9].
    Returns {threshold: {"A": rate, "B": rate, "diff": float}}.
    """
    if thresholds is None:
        thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]

    results = {}
    for th in thresholds:
        rate_a, n_a, tot_a = high_conf_rate(records, "A", th)
        rate_b, n_b, tot_b = high_conf_rate(records, "B", th)
        results[th] = {
            "A": rate_a,
            "B": rate_b,
            "diff": abs(rate_a - rate_b),
            "n_high_A": n_a,
            "n_high_B": n_b,
            "n_total_A": tot_a,
            "n_total_B": tot_b,
        }
    return results
