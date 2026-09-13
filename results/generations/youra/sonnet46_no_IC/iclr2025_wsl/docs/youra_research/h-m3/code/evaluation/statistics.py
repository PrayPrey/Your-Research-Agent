"""Statistical analysis for H-M3 interpolation results."""
import numpy as np
from scipy import stats


def compute_statistics(results):
    """
    results: [{task, acc_latent, acc_ws, delta}, ...]
    Returns dict with overall and per-task statistics.
    """
    acc_latent = np.array([r['acc_latent'] for r in results])
    acc_ws = np.array([r['acc_ws'] for r in results])
    delta = acc_latent - acc_ws

    mean_delta = float(delta.mean())
    std_delta = float(delta.std())
    n_pairs = len(results)

    t_stat, p_value = stats.ttest_rel(acc_latent, acc_ws)
    t_stat, p_value = float(t_stat), float(p_value)

    cohen_d = mean_delta / std_delta if std_delta > 1e-10 else 0.0
    pct_pairs_positive = float((delta > 0).mean())

    gate_pass = bool(mean_delta > 0 and p_value < 0.05)

    tasks = list(set(r['task'] for r in results))
    per_task = {}
    for task in sorted(tasks):
        task_delta = np.array([r['acc_latent'] - r['acc_ws']
                               for r in results if r['task'] == task])
        per_task[task] = {
            'mean_delta': float(task_delta.mean()) if len(task_delta) > 0 else 0.0,
            'std_delta': float(task_delta.std()) if len(task_delta) > 0 else 0.0,
            'n': int(len(task_delta)),
            'mean_acc_latent': float(np.mean([r['acc_latent'] for r in results if r['task'] == task])),
            'mean_acc_ws': float(np.mean([r['acc_ws'] for r in results if r['task'] == task])),
        }

    return {
        'mean_delta': mean_delta,
        'std_delta': std_delta,
        'n_pairs': n_pairs,
        't_stat': t_stat,
        'p_value': p_value,
        'cohen_d': cohen_d,
        'pct_pairs_positive': pct_pairs_positive,
        'gate_pass': gate_pass,
        'mean_acc_latent': float(acc_latent.mean()),
        'mean_acc_ws': float(acc_ws.mean()),
        'per_task': per_task,
    }


def format_report(stats_dict, results):
    """Format statistics as markdown report string."""
    g = stats_dict
    gate_str = "✅ PASS" if g['gate_pass'] else "⚠️ DOCUMENT"

    lines = [
        f"## Gate Result: {gate_str}",
        "",
        f"Gate condition: mean(acc_latent) > mean(acc_ws) AND p < 0.05",
        f"Result: mean_delta={g['mean_delta']:.4f}, p={g['p_value']:.4f}",
        "",
        "### Overall Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| N pairs | {g['n_pairs']} |",
        f"| mean(acc_latent) | {g['mean_acc_latent']:.4f} |",
        f"| mean(acc_ws) | {g['mean_acc_ws']:.4f} |",
        f"| mean(delta) | {g['mean_delta']:.4f} ± {g['std_delta']:.4f} |",
        f"| t-statistic | {g['t_stat']:.4f} |",
        f"| p-value | {g['p_value']:.4f} |",
        f"| Cohen's d | {g['cohen_d']:.4f} |",
        f"| % pairs positive | {g['pct_pairs_positive']:.1%} |",
        "",
        "### Per-Task Breakdown",
        "",
        "| Task | N | mean(acc_latent) | mean(acc_ws) | mean(delta) |",
        "|------|---|-----------------|--------------|-------------|",
    ]

    for task, pt in g['per_task'].items():
        lines.append(
            f"| {task} | {pt['n']} | {pt['mean_acc_latent']:.4f} | "
            f"{pt['mean_acc_ws']:.4f} | {pt['mean_delta']:.4f} |"
        )

    return "\n".join(lines)
