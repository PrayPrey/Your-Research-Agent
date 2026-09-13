"""Baseline computations for H-M2."""
from data import EnsembleInput


def per_judge_accuracy(inputs: list) -> dict:
    """Compute accuracy per judge."""
    correct = {}
    total = {}
    for inp in inputs:
        for judge, verdict in inp.verdicts.items():
            correct[judge] = correct.get(judge, 0) + (verdict == inp.ground_truth)
            total[judge] = total.get(judge, 0) + 1
    return {j: correct[j] / total[j] for j in correct}


def per_judge_fpr_fnr(inputs: list) -> dict:
    """Compute FPR/FNR per judge."""
    stats = {}
    for inp in inputs:
        for judge, verdict in inp.verdicts.items():
            if judge not in stats:
                stats[judge] = {"fp": 0, "fn": 0, "tp": 0, "tn": 0}
            if verdict and inp.ground_truth:
                stats[judge]["tp"] += 1
            elif verdict and not inp.ground_truth:
                stats[judge]["fp"] += 1
            elif not verdict and inp.ground_truth:
                stats[judge]["fn"] += 1
            else:
                stats[judge]["tn"] += 1

    result = {}
    for j, s in stats.items():
        fpr = s["fp"] / (s["fp"] + s["tn"]) if (s["fp"] + s["tn"]) > 0 else 0
        fnr = s["fn"] / (s["fn"] + s["tp"]) if (s["fn"] + s["tp"]) > 0 else 0
        result[j] = {"fpr": fpr, "fnr": fnr}
    return result


def best_single_judge(accuracies: dict) -> tuple:
    """Return (judge, accuracy) with highest accuracy."""
    return max(accuracies.items(), key=lambda x: x[1])


def random_avg_baseline(accuracies: dict) -> float:
    """Expected accuracy of random judge selection."""
    return sum(accuracies.values()) / len(accuracies)
