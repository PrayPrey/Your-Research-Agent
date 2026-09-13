"""Statistical tests for H-M2."""
import numpy as np
from scipy import stats as scipy_stats


def mcnemar_table(y_true: np.ndarray, y_pred1: np.ndarray, y_pred2: np.ndarray) -> np.ndarray:
    """Build 2x2 contingency table for McNemar test.

    Returns [[both_correct, pred1_only], [pred2_only, both_wrong]]
    """
    correct1 = (y_pred1 == y_true)
    correct2 = (y_pred2 == y_true)

    both_correct = np.sum(correct1 & correct2)
    pred1_only = np.sum(correct1 & ~correct2)
    pred2_only = np.sum(~correct1 & correct2)
    both_wrong = np.sum(~correct1 & ~correct2)

    return np.array([[both_correct, pred1_only], [pred2_only, both_wrong]])


def mcnemar_test(table: np.ndarray, exact: bool = True) -> dict:
    """McNemar test for paired nominal data.

    Returns chi2, p_value.
    """
    b, c = table[0, 1], table[1, 0]

    if b + c == 0:
        # No discordant pairs — methods are identical
        return {"chi2": None, "p_value": 1.0, "b": int(b), "c": int(c)}

    if exact and (b + c) < 25:
        # Exact binomial test
        p_value = scipy_stats.binomtest(min(b, c), b + c, 0.5).pvalue
        chi2 = None
    else:
        # Chi-square approximation
        chi2 = (abs(b - c) - 1) ** 2 / (b + c) if (b + c) > 0 else 0
        p_value = scipy_stats.chi2.sf(chi2, df=1)

    return {"chi2": chi2, "p_value": p_value, "b": int(b), "c": int(c)}


def wilson_ci(p: float, n: int, z: float = 1.96) -> tuple:
    """Wilson score confidence interval."""
    denom = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (center - margin, center + margin)


def compare_ensemble_vs_best(
    y_true: np.ndarray,
    y_ensemble: np.ndarray,
    y_best_single: np.ndarray,
    p_threshold: float = 0.05,
    improvement_target: float = 0.03
) -> dict:
    """Full comparison: McNemar + accuracy + improvement + verdict."""
    table = mcnemar_table(y_true, y_ensemble, y_best_single)
    test_result = mcnemar_test(table, exact=True)

    acc_ensemble = np.mean(y_ensemble == y_true)
    acc_best = np.mean(y_best_single == y_true)
    improvement = acc_ensemble - acc_best
    improvement_pct = improvement * 100

    ci = wilson_ci(acc_ensemble, len(y_true))

    hypothesis_supported = (improvement >= improvement_target) and (test_result["p_value"] < p_threshold)

    return {
        "contingency_table": table.tolist(),
        "chi2": test_result["chi2"],
        "p_value": test_result["p_value"],
        "discordant_pairs": {"ensemble_only": test_result["b"], "best_only": test_result["c"]},
        "acc_ensemble": acc_ensemble,
        "acc_best_single": acc_best,
        "improvement": improvement,
        "improvement_pct": improvement_pct,
        "ci_95": ci,
        "hypothesis_supported": hypothesis_supported
    }


def pivot_analysis(inputs: list, ensemble_fn, unanimity_fn) -> dict:
    """Split accuracy by unanimous vs split verdicts."""
    unanimous_correct = 0
    unanimous_total = 0
    split_correct = 0
    split_total = 0

    for inp in inputs:
        is_unanimous = unanimity_fn(inp.verdicts)
        ens_verdict = ensemble_fn(inp.verdicts)
        is_correct = ens_verdict == inp.ground_truth

        if is_unanimous:
            unanimous_total += 1
            unanimous_correct += is_correct
        else:
            split_total += 1
            split_correct += is_correct

    return {
        "unanimous_acc": unanimous_correct / unanimous_total if unanimous_total > 0 else None,
        "unanimous_n": unanimous_total,
        "unanimous_correct": unanimous_correct,
        "split_acc": split_correct / split_total if split_total > 0 else None,
        "split_n": split_total,
        "split_correct": split_correct
    }
