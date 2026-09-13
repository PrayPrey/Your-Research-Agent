#!/usr/bin/env python3
"""H-M1: Temporal structure test for GLUE/SuperGLUE leaderboards."""
import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# --- Constants ---
BENCHMARKS = {
    "glue":      "data/glue_timeseries_clean.csv",
    "superglue": "data/superglue_timeseries_clean.csv",
}
FIGURES_DIR  = "docs/youra_research/h-m1/figures"
RESULTS_JSON = "docs/youra_research/h-m1/results.json"

RHO_MONO_THRESHOLD  = 0.8
RHO_DECEL_THRESHOLD = -0.3
BASELINE_RHO_MONO  = 0.0
BASELINE_RHO_DECEL = 0.0

CSV_COL_MONTHS = "months"
CSV_COL_SCORE  = "monthly_max"

MIN_MONTHS_SPAN = 24
MIN_OBS         = 20
MIN_SCORE_STD   = 0.001


# --- Data loading & validation ---

def load_timeseries(csv_path: str) -> tuple:
    if not Path(csv_path).exists():
        raise FileNotFoundError(
            f"H-E1 output not found: {csv_path}. Re-run H-E1 data pipeline."
        )
    df = pd.read_csv(csv_path)
    required = {CSV_COL_MONTHS, CSV_COL_SCORE}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}. Got: {list(df.columns)}")
    df = df.sort_values(CSV_COL_MONTHS).reset_index(drop=True)
    times  = df[CSV_COL_MONTHS].to_numpy(dtype=np.int64)
    scores = df[CSV_COL_SCORE].to_numpy(dtype=np.float64)
    time_span = int(times.max() - times.min())
    if time_span < MIN_MONTHS_SPAN:
        raise ValueError(f"Time span {time_span} months < required {MIN_MONTHS_SPAN}.")
    if len(scores) < MIN_OBS:
        raise ValueError(f"Only {len(scores)} observations < required {MIN_OBS}.")
    if scores.std() < MIN_SCORE_STD:
        raise ValueError(f"Score std {scores.std():.4f} too low — degenerate series.")
    return times, scores


# --- Gain rate computation ---

def compute_gains(times: np.ndarray, scores: np.ndarray) -> tuple:
    gains = np.diff(scores)
    gain_times = times[1:]
    return gain_times, gains


def split_inflection(gains: np.ndarray, inflection_idx=None) -> tuple:
    if inflection_idx is None:
        inflection_idx = len(gains) // 2
    inflection_idx = max(0, min(inflection_idx, len(gains)))
    return gains[:inflection_idx], gains[inflection_idx:]


# --- Core temporal analysis ---

def test_temporal_signal(times, scores, gains, gain_times) -> dict:
    rho_mono, _ = stats.spearmanr(times, scores)

    if len(gains) < 2:
        rho_decel = float("nan")
    else:
        rho_decel, _ = stats.spearmanr(gain_times, gains)

    pre_gains, post_gains = split_inflection(gains)
    if len(pre_gains) == 0 or len(post_gains) == 0:
        pre_post_ratio = float("nan")
    else:
        pre_mean  = float(np.mean(pre_gains))
        post_mean = float(np.mean(post_gains))
        if post_mean <= 0:
            pre_post_ratio = float("inf")
        else:
            pre_post_ratio = pre_mean / post_mean

    return {
        "rho_monotonic":  float(rho_mono),
        "rho_decel":      float(rho_decel),
        "pre_post_ratio": pre_post_ratio,
        "n_months":       len(scores),
        "n_gains":        len(gains),
        "pass":           (float(rho_mono) > RHO_MONO_THRESHOLD and float(rho_decel) < RHO_DECEL_THRESHOLD),
    }


# --- Results reporting ---

def print_results_table(benchmark_results: dict) -> None:
    header = f"{'Benchmark':<12} {'rho_mono':>9} {'rho_decel':>10} {'pre/post':>10} {'Pass?':>7}"
    print("\n" + "=" * len(header))
    print("H-M1 Results: Temporal Signal Detection")
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for bm, r in benchmark_results.items():
        ratio = r["pre_post_ratio"]
        ratio_str = f"{ratio:.2f}" if math.isfinite(ratio) else "inf" if ratio == float("inf") else "nan"
        print(f"{bm.upper():<12} {r['rho_monotonic']:>9.3f} {r['rho_decel']:>10.3f} "
              f"{ratio_str:>10} {'PASS' if r['pass'] else 'FAIL':>7}")
    print("=" * len(header))


def save_results_json(benchmark_results: dict, out_path: str) -> None:
    def _safe(v):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return str(v)
        return v

    overall_pass = all(r["pass"] for r in benchmark_results.values())
    passed_count = sum(1 for r in benchmark_results.values() if r["pass"])
    if passed_count == len(benchmark_results):
        verdict = "PASS"
    elif passed_count > 0:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    payload = {
        "overall_pass": overall_pass,
        "overall_verdict": verdict,
        "benchmarks": {
            bm: {
                **{k: _safe(v) for k, v in r.items()},
                "baseline_rho_monotonic": BASELINE_RHO_MONO,
                "baseline_rho_decel": BASELINE_RHO_DECEL,
            }
            for bm, r in benchmark_results.items()
        },
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)


# --- Visualization ---

def plot_gate_metrics(benchmark_results: dict, out_dir: str) -> None:
    benchmarks = list(benchmark_results.keys())
    colors = {"glue": "#2196F3", "superglue": "#FF9800"}
    metrics = ["rho_monotonic", "rho_decel"]
    x = np.arange(len(metrics))
    width = 0.3
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, bm in enumerate(benchmarks):
        vals = [benchmark_results[bm]["rho_monotonic"], benchmark_results[bm]["rho_decel"]]
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, vals, width, label=bm.upper(),
                      color=colors.get(bm, "gray"), alpha=0.85)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    val + 0.03 * (1 if val >= 0 else -1),
                    f"{val:.3f}", ha="center",
                    va="bottom" if val >= 0 else "top", fontsize=9)
    ax.axhline(RHO_MONO_THRESHOLD,  color="green", linestyle="--", linewidth=1.5,
               label=f"Mono threshold ({RHO_MONO_THRESHOLD})")
    ax.axhline(RHO_DECEL_THRESHOLD, color="red",   linestyle="--", linewidth=1.5,
               label=f"Decel threshold ({RHO_DECEL_THRESHOLD})")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(["rho(time, score)\n[Monotonicity]", "rho(time, gain_rate)\n[Deceleration]"])
    ax.set_ylabel("Spearman rho")
    ax.set_ylim(-1.1, 1.1)
    ax.set_title("H-M1 Gate Metrics: Temporal Signal Detection")
    ax.legend()
    fig.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out_dir}/gate_metrics.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_score_trajectory(all_data: dict, out_dir: str) -> None:
    colors = {"glue": "#2196F3", "superglue": "#FF9800"}
    fig, ax = plt.subplots(figsize=(10, 5))
    for bm, (times, scores) in all_data.items():
        ax.plot(times, scores, marker="o", markersize=3, linewidth=1.5,
                color=colors.get(bm, "gray"), label=bm.upper())
    ax.set_xlabel("Months Since Benchmark Release")
    ax.set_ylabel("Normalized Composite Score [0, 1]")
    ax.set_title("H-M1: Score-Over-Time Trajectory (GLUE + SuperGLUE)")
    ax.legend()
    fig.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out_dir}/score_trajectory.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_gain_rate(all_data: dict, out_dir: str, window: int = 3) -> None:
    colors = {"glue": "#2196F3", "superglue": "#FF9800"}
    fig, ax = plt.subplots(figsize=(10, 4))
    for bm, (gain_times, gains) in all_data.items():
        color = colors.get(bm, "gray")
        ax.scatter(gain_times, gains, s=20, alpha=0.6, color=color, label=f"{bm.upper()} gains")
        trend = pd.Series(gains).rolling(window, min_periods=1).mean().to_numpy()
        ax.plot(gain_times, trend, linewidth=2, color=color, label=f"{bm.upper()} trend")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Months Since Benchmark Release")
    ax.set_ylabel("Month-Over-Month Score Gain")
    ax.set_title("H-M1: Gain Rate Over Time (Deceleration Test)")
    ax.legend()
    fig.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out_dir}/gain_rate.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_pre_post_inflection(all_data: dict, out_dir: str) -> None:
    benchmarks = list(all_data.keys())
    fig, axes = plt.subplots(1, len(benchmarks), figsize=(5 * len(benchmarks), 4), sharey=True)
    if len(benchmarks) == 1:
        axes = [axes]
    for ax, bm in zip(axes, benchmarks):
        pre_gains, post_gains = all_data[bm]
        ax.boxplot([pre_gains, post_gains], labels=["Pre-inflection", "Post-inflection"],
                   patch_artist=True,
                   boxprops=dict(facecolor="#BBDEFB"),
                   medianprops=dict(color="navy", linewidth=2))
        ax.axhline(0, color="red", linewidth=0.8, linestyle="--")
        ax.set_title(bm.upper())
        ax.set_ylabel("Score Gain per Month")
    fig.suptitle("H-M1: Gain Rate Pre vs Post Inflection", fontsize=13)
    fig.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out_dir}/pre_post_inflection.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# --- CLI ---

def parse_args():
    p = argparse.ArgumentParser(description="H-M1: Temporal structure test for GLUE/SuperGLUE.")
    p.add_argument("--glue-csv",      default=BENCHMARKS["glue"])
    p.add_argument("--superglue-csv", default=BENCHMARKS["superglue"])
    p.add_argument("--out-dir",       default="docs/youra_research/h-m1")
    p.add_argument("--figures-dir",   default=FIGURES_DIR)
    return p.parse_args()


# --- Main ---

def main() -> None:
    args = parse_args()
    csv_paths = {
        "glue":      args.glue_csv,
        "superglue": args.superglue_csv,
    }
    figures_dir = args.figures_dir
    results_json_path = str(Path(args.out_dir) / "results.json")

    benchmark_results = {}
    trajectory_data  = {}
    gain_data        = {}
    inflection_data  = {}

    for bm, csv_path in csv_paths.items():
        print(f"\nProcessing {bm.upper()} ({csv_path})")
        try:
            times, scores = load_timeseries(csv_path)
        except FileNotFoundError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(2)
        except ValueError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(2)

        print(f"  Loaded: {len(scores)} months, span [{times.min()}, {times.max()}]")
        gain_times, gains = compute_gains(times, scores)
        result = test_temporal_signal(times, scores, gains, gain_times)
        benchmark_results[bm] = result

        pre_gains, post_gains = split_inflection(gains)
        trajectory_data[bm] = (times, scores)
        gain_data[bm]        = (gain_times, gains)
        inflection_data[bm]  = (pre_gains, post_gains)

        print(f"  rho_monotonic={result['rho_monotonic']:.3f}  (threshold > {RHO_MONO_THRESHOLD})")
        print(f"  rho_decel={result['rho_decel']:.3f}  (threshold < {RHO_DECEL_THRESHOLD})")
        ratio = result["pre_post_ratio"]
        ratio_str = f"{ratio:.2f}" if math.isfinite(ratio) else str(ratio)
        print(f"  pre_post_ratio={ratio_str}  (expected > 1.0)")
        print(f"  Gate: {'PASS' if result['pass'] else 'FAIL'}")

    print_results_table(benchmark_results)
    save_results_json(benchmark_results, results_json_path)
    print(f"\nResults JSON: {results_json_path}")

    print("\nGenerating figures...")
    plot_gate_metrics(benchmark_results, figures_dir)
    plot_score_trajectory(trajectory_data, figures_dir)
    plot_gain_rate(gain_data, figures_dir)
    plot_pre_post_inflection(inflection_data, figures_dir)
    print(f"Figures saved to: {figures_dir}/")

    overall_pass = all(r["pass"] for r in benchmark_results.values())
    print(f"\nOverall Gate: {'PASS' if overall_pass else 'FAIL'}")
    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    # Self-check: synthetic monotonic + decelerating series
    if "--self-check" in sys.argv:
        t = np.arange(15, 45)
        s = 1 / (1 + np.exp(-0.3 * (t - 15))) * 0.8 + 0.1
        gt, g = compute_gains(t, s)
        r = test_temporal_signal(t, s, g, gt)
        assert r["rho_monotonic"] > 0.8,  f"Expected rho_mono > 0.8, got {r['rho_monotonic']:.3f}"
        assert r["rho_decel"] < -0.3,     f"Expected rho_decel < -0.3, got {r['rho_decel']:.3f}"
        assert r["pre_post_ratio"] > 1.0, f"Expected pre_post_ratio > 1.0, got {r['pre_post_ratio']:.3f}"
        assert r["pass"] is True
        print("Self-check PASSED")
    else:
        main()
