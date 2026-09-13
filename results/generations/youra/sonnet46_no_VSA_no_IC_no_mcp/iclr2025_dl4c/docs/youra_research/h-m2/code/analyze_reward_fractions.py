"""analyze_reward_fractions.py — H-M2: Post-hoc analysis of H-E1 reward monitoring JSONL.

Reads logs/reward_monitoring.jsonl from H-E1 training run, computes non-zero reward
fractions per APPS difficulty bucket, evaluates SHOULD_WORK gate, and generates figures.

Log format (H-E1 SimpleGRPOTrainer):
  {"step": int, "loss": float, "intro_reward": float|null,
   "interview_reward": float|null, "competition_reward": float|null}

Column mapping: intro_reward -> introductory, interview_reward -> interview,
                competition_reward -> competition
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BUCKETS = ["introductory", "interview", "competition"]
COLORS = ["steelblue", "darkorange", "firebrick"]
COL_MAP = {
    "intro_reward": "introductory",
    "interview_reward": "interview",
    "competition_reward": "competition",
}
GATE_THRESHOLD = 0.10


def load_reward_log(log_path: str) -> list[dict]:
    """Parse JSONL reward log; skip malformed lines."""
    records = []
    for line in Path(log_path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def detect_nonzero(reward: float) -> bool:
    """Return reward > 0."""
    return reward > 0.0


def compute_nonzero_fractions(log_records: list[dict]) -> dict[str, float]:
    """Compute per-bucket fraction of steps with mean reward > 0."""
    indicators: dict[str, list[float]] = {v: [] for v in COL_MAP.values()}
    for rec in log_records:
        for col, bucket in COL_MAP.items():
            val = rec.get(col)
            if val is not None:
                indicators[bucket].append(float(detect_nonzero(val)))
    return {k: float(np.mean(v)) if v else 0.0 for k, v in indicators.items()}


def compute_step_series(log_records: list[dict]) -> dict[str, list]:
    """Extract per-step reward values for line-plot figure."""
    series: dict[str, list] = {"steps": [], "introductory": [], "interview": [], "competition": []}
    for rec in log_records:
        series["steps"].append(rec.get("step", 0))
        for col, bucket in COL_MAP.items():
            series[bucket].append(rec.get(col))
    return series


def save_results(fractions: dict, output_path: str, counts: dict = None) -> dict:
    """Write reward_fractions.json; return result dict."""
    comp = fractions.get("competition", 0.0)
    intro = fractions.get("introductory", 0.0)
    interview = fractions.get("interview", 0.0)
    monotonicity = intro >= interview >= comp
    result = {
        "hypothesis": "h-m2",
        "gate_condition": f"competition_nonzero_fraction > {GATE_THRESHOLD}",
        "fractions": {k: round(v, 4) for k, v in fractions.items()},
        "gate_result": "PASS" if comp > GATE_THRESHOLD else "FAIL",
        "sample_counts": counts or {},
        "monotonicity_holds": monotonicity,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(result, indent=2))
    return result


def plot_bucket_fractions(fractions: dict, threshold: float, output_dir: str) -> None:
    """Figure 1: bar chart per bucket with threshold line."""
    vals = [fractions.get(b, 0.0) for b in BUCKETS]
    fig, ax = plt.subplots()
    ax.bar(BUCKETS, vals, color=COLORS)
    ax.axhline(threshold, color="black", linestyle="--", label=f"threshold={threshold}")
    ax.set_ylabel("Non-zero reward fraction")
    ax.set_title("H-M2: Non-Zero Reward Fraction by Difficulty")
    ax.set_ylim(0, max(max(vals) * 1.2, threshold * 1.5))
    ax.legend()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(str(Path(output_dir) / "fig1_nonzero_fraction_bar.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_fraction_over_steps(step_records: dict, output_dir: str) -> None:
    """Figure 2: non-zero reward fraction vs training step (3 curves)."""
    steps = step_records["steps"]
    fig, ax = plt.subplots()
    for bucket, color in zip(BUCKETS, COLORS):
        vals = step_records.get(bucket, [])
        nz = [float(v > 0) if v is not None else float("nan") for v in vals]
        ax.plot(steps, nz, label=bucket, color=color, alpha=0.8)
    ax.set_xlabel("Training step")
    ax.set_ylabel("Non-zero reward (step indicator)")
    ax.set_title("H-M2: Non-Zero Reward Over Training Steps")
    ax.legend()
    fig.savefig(str(Path(output_dir) / "fig2_nonzero_fraction_step.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_reward_histogram(log_records: list[dict], output_dir: str) -> None:
    """Figure 3: reward distribution histogram per bucket."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    for ax, (col, bucket), color in zip(axes, COL_MAP.items(), COLORS):
        vals = [r[col] for r in log_records if r.get(col) is not None]
        if vals:
            ax.hist(vals, bins=min(20, max(5, len(vals) // 2)), color=color, edgecolor="white")
        ax.set_title(bucket)
        ax.set_xlabel("Mean reward per step")
    axes[0].set_ylabel("Count")
    fig.suptitle("H-M2: Reward Distribution by Difficulty")
    fig.tight_layout()
    fig.savefig(str(Path(output_dir) / "fig3_reward_histogram.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_correlation(fractions: dict, output_dir: str) -> None:
    """Figure 4: difficulty bucket index vs mean non-zero fraction scatter."""
    vals = [fractions.get(b, 0.0) for b in BUCKETS]
    fig, ax = plt.subplots()
    ax.scatter(range(len(BUCKETS)), vals, c=COLORS, s=120, zorder=3)
    ax.plot(range(len(BUCKETS)), vals, "--", color="gray", alpha=0.5)
    ax.set_xticks(range(len(BUCKETS)))
    ax.set_xticklabels(BUCKETS)
    ax.set_ylabel("Non-zero fraction")
    ax.set_title("H-M2: Difficulty vs Non-Zero Fraction (Correlation)")
    fig.savefig(str(Path(output_dir) / "fig4_correlation_scatter.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def assert_gate(fractions: dict, threshold: float = GATE_THRESHOLD) -> bool:
    """Return True if competition fraction > threshold; print PASS/FAIL."""
    comp = fractions.get("competition", 0.0)
    result = "PASS" if comp > threshold else "FAIL"
    print(f"[H-M2 GATE] competition={comp:.4f} threshold={threshold} -> {result}")
    return comp > threshold


def main(log_path: str, results_dir: str, figures_dir: str) -> dict:
    """End-to-end post-hoc analysis pipeline."""
    print(f"[H-M2] Loading reward log: {log_path}")
    records = load_reward_log(log_path)
    print(f"[H-M2] Loaded {len(records)} log records")

    if not records:
        print("[H-M2] ERROR: No records found in reward log")
        sys.exit(1)

    fractions = compute_nonzero_fractions(records)
    series = compute_step_series(records)

    print(f"[H-M2] Non-zero fractions:")
    for bucket, frac in fractions.items():
        print(f"  {bucket}: {frac:.4f}")

    counts = {
        bucket: sum(1 for r in records if r.get(col) is not None)
        for col, bucket in COL_MAP.items()
    }

    result = save_results(fractions, output_path=f"{results_dir}/reward_fractions.json", counts=counts)
    print(f"[H-M2] Results saved to {results_dir}/reward_fractions.json")

    plot_bucket_fractions(fractions, threshold=GATE_THRESHOLD, output_dir=figures_dir)
    plot_fraction_over_steps(series, output_dir=figures_dir)
    plot_reward_histogram(records, output_dir=figures_dir)
    plot_correlation(fractions, output_dir=figures_dir)
    print(f"[H-M2] Figures saved to {figures_dir}/")

    gate_passed = assert_gate(fractions)
    result["gate_passed"] = gate_passed
    print(f"[H-M2] Gate result: {result['gate_result']}")
    print(f"[H-M2] Monotonicity holds: {result['monotonicity_holds']}")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="../../h-e1/code/logs/reward_monitoring.jsonl")
    parser.add_argument("--results", default="../results")
    parser.add_argument("--figures", default="../figures")
    args = parser.parse_args()
    main(log_path=args.log, results_dir=args.results, figures_dir=args.figures)
