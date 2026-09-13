import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)

# Statistical configuration
ALPHA = 0.05
COHEN_D_SMALL = 0.2
COHEN_D_MEDIUM = 0.5
COHEN_D_LARGE = 0.8
CONFOUND_THRESHOLD = 0.05
RATIO_DIFF_THRESHOLD = 0.05
ALTERNATIVE = "less"    # H1: ratios_no_background < ratios_original
COLLAPSE_TASK_ACC_THRESHOLD = 0.534


def check_collapse(task_probe_acc: float, majority_class_baseline: float = 0.534) -> dict:
    """Detect representation collapse."""
    collapsed = task_probe_acc < majority_class_baseline
    result = {
        "collapsed": collapsed,
        "task_probe_acc": task_probe_acc,
        "threshold": majority_class_baseline,
    }
    if collapsed:
        logger.warning(
            f"COLLAPSE DETECTED: task_probe_acc={task_probe_acc:.3f} < {majority_class_baseline:.3f}. "
            "Seed marked FAILED."
        )
    return result


def paired_ttest(ratios_no_bg: list, ratios_original: list) -> dict:
    """Paired one-sided t-test: H1: ratios_no_bg < ratios_original."""
    a = np.array(ratios_no_bg)
    b = np.array(ratios_original)
    t_stat, p_value = stats.ttest_rel(a, b, alternative=ALTERNATIVE)

    # Cohen's d (paired)
    diff = b - a
    cohen_d = diff.mean() / (diff.std(ddof=1) + 1e-8)

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "cohen_d": float(cohen_d),
        "n_seeds": len(a),
        "mean_ratio_no_bg": float(a.mean()),
        "mean_ratio_original": float(b.mean()),
        "ratio_diff_mean": float(b.mean() - a.mean()),
    }


def confound_check(task_accs_no_bg: list, task_accs_original: list, threshold: float = CONFOUND_THRESHOLD) -> dict:
    """Check if task accuracy differs significantly between conditions (confound)."""
    a = np.array(task_accs_no_bg)
    b = np.array(task_accs_original)
    task_acc_diff = abs(float(b.mean() - a.mean()))
    is_confounded = task_acc_diff > threshold
    return {
        "task_acc_diff": task_acc_diff,
        "mean_task_acc_no_bg": float(a.mean()),
        "mean_task_acc_original": float(b.mean()),
        "is_confounded": is_confounded,
        "threshold": threshold,
    }


def compute_verdict(ratio_diff_mean: float, p_value: float, task_acc_diff: float) -> str:
    """Determine experimental verdict."""
    if task_acc_diff > CONFOUND_THRESHOLD:
        return "INCONCLUSIVE"
    if ratio_diff_mean >= RATIO_DIFF_THRESHOLD and p_value < ALPHA:
        return "CONFIRMED"
    return "FAIL"
