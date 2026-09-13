"""Adaptive contribution computation: paired Exp_B - Exp_A statistics."""
import sys
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon as scipy_wilcoxon
from statsmodels.stats.multitest import multipletests

H1_CODE_DIR = Path(__file__).parent.parent.parent / "h-m1" / "code"
if str(H1_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(H1_CODE_DIR))

from statistical_analysis import bootstrap_ci, wilcoxon_holm


@dataclass
class ContributionStats:
    mean_adaptive_gap: float
    wilcoxon_stat: float
    wilcoxon_p_raw: float
    wilcoxon_p_holm: float
    ci_lower: float
    ci_upper: float
    fraction_tasks_gt_threshold: float
    by_model: dict
    by_task_type: dict
    gate_passed: bool
    n_paired_triples: int


def join_exp_a_b(
    exp_a: list[dict],
    exp_b: list[dict],
    excluded_tasks: list[str],
) -> tuple[list[float], list[float], list[dict]]:
    excluded = set(excluded_tasks)
    a_index = {
        (r["task_id"], r["model"], r["program_idx"]): r
        for r in exp_a
        if r["task_id"] not in excluded
    }
    a_rates, b_rates, paired = [], [], []
    for r in exp_b:
        tid = r["task_id"] if isinstance(r, dict) else r.task_id
        model = r["model"] if isinstance(r, dict) else r.model
        pidx = r["program_idx"] if isinstance(r, dict) else r.program_idx
        error = r.get("error") if isinstance(r, dict) else r.error
        b_rate = r["adaptive_failure_rate"] if isinstance(r, dict) else r.adaptive_failure_rate
        tt = r.get("task_type", "unknown") if isinstance(r, dict) else "unknown"

        if tid in excluded:
            continue
        if error is not None:
            continue
        key = (tid, model, pidx)
        if key not in a_index:
            continue
        a_rec = a_index[key]
        a_rate = a_rec["static_failure_rate"]
        a_rates.append(a_rate)
        b_rates.append(b_rate)
        paired.append({
            "task_id": tid,
            "model": model,
            "program_idx": pidx,
            "static_failure_rate": a_rate,
            "adaptive_failure_rate": b_rate,
            "adaptive_gap": b_rate - a_rate,
            "task_type": a_rec.get("task_type", tt),
        })
    return a_rates, b_rates, paired


def _per_model_wilcoxon(paired_records: list[dict]) -> dict:
    model_gaps: dict[str, list[float]] = {}
    for r in paired_records:
        model_gaps.setdefault(r["model"], []).append(r["adaptive_gap"])

    models = list(model_gaps.keys())
    raw_ps, stats_vals, means = [], [], []
    for m in models:
        g = model_gaps[m]
        nonzero = [x for x in g if x != 0.0]
        if len(nonzero) < 2:
            stats_vals.append(0.0)
            raw_ps.append(1.0)
        else:
            try:
                s, p = scipy_wilcoxon(g, alternative="greater")
                stats_vals.append(float(s))
                raw_ps.append(float(p))
            except Exception:
                stats_vals.append(0.0)
                raw_ps.append(1.0)
        means.append(float(np.mean(g)))

    _, holm_ps, _, _ = multipletests(raw_ps, method="holm")
    return {
        m: {"stat": stats_vals[i], "p_raw": raw_ps[i], "p_holm": float(holm_ps[i]), "mean_gap": means[i]}
        for i, m in enumerate(models)
    }


def compute_adaptive_contribution(
    exp_a_rates: list[float],
    exp_b_rates: list[float],
    paired_records: list[dict],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> ContributionStats:
    gaps = [b - a for a, b in zip(exp_a_rates, exp_b_rates)]
    mean_gap = float(np.mean(gaps)) if gaps else 0.0
    stat, p_raw, p_holm = wilcoxon_holm(gaps)
    ci_lower, ci_upper = bootstrap_ci(gaps, n_bootstrap, seed)

    task_means: dict[str, list[float]] = {}
    for r in paired_records:
        task_means.setdefault(r["task_id"], []).append(r["adaptive_gap"])
    per_task_gaps = [float(np.mean(v)) for v in task_means.values()]
    fraction_gt = sum(1 for g in per_task_gaps if g > 0.03) / max(len(per_task_gaps), 1)

    model_stats = _per_model_wilcoxon(paired_records)
    by_model = {
        m: {"mean_gap": d["mean_gap"], "n_triples": sum(1 for r in paired_records if r["model"] == m)}
        for m, d in model_stats.items()
    }

    type_gaps: dict[str, list[float]] = {}
    for r in paired_records:
        type_gaps.setdefault(r["task_type"], []).append(r["adaptive_gap"])
    by_task_type = {tt: {"mean_gap": float(np.mean(g))} for tt, g in type_gaps.items()}

    return ContributionStats(
        mean_adaptive_gap=mean_gap,
        wilcoxon_stat=stat,
        wilcoxon_p_raw=p_raw,
        wilcoxon_p_holm=p_holm,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        fraction_tasks_gt_threshold=fraction_gt,
        by_model=by_model,
        by_task_type=by_task_type,
        gate_passed=(mean_gap > 0.0 and p_holm < 0.05),
        n_paired_triples=len(paired_records),
    )


def save_results(stats: ContributionStats, paired_records: list[dict], results_dir: str = "results/") -> None:
    import csv, json
    rdir = Path(results_dir)
    rdir.mkdir(parents=True, exist_ok=True)

    csv_path = rdir / "per_task_adaptive_contribution.csv"
    with open(csv_path, "w", newline="") as f:
        if paired_records:
            writer = csv.DictWriter(f, fieldnames=list(paired_records[0].keys()))
            writer.writeheader()
            writer.writerows(paired_records)

    md = rdir / "summary_report.md"
    with open(md, "w") as f:
        f.write("# H-M3 Summary Report\n\n")
        f.write(f"**Mean adaptive gap**: {stats.mean_adaptive_gap:.4f}\n")
        f.write(f"**Wilcoxon stat**: {stats.wilcoxon_stat:.4f}, p_raw={stats.wilcoxon_p_raw:.4e}, p_holm={stats.wilcoxon_p_holm:.4e}\n")
        f.write(f"**95% CI**: [{stats.ci_lower:.4f}, {stats.ci_upper:.4f}]\n")
        f.write(f"**Fraction tasks gap>0.03**: {stats.fraction_tasks_gt_threshold:.3f}\n")
        f.write(f"**Gate passed**: {stats.gate_passed}\n")
        f.write(f"**Paired triples**: {stats.n_paired_triples}\n\n")
        f.write("## By Model\n")
        for m, d in stats.by_model.items():
            f.write(f"- {m}: mean_gap={d['mean_gap']:.4f}, n={d['n_triples']}\n")
        f.write("\n## By Task Type\n")
        for tt, d in stats.by_task_type.items():
            f.write(f"- {tt}: mean_gap={d['mean_gap']:.4f}\n")
