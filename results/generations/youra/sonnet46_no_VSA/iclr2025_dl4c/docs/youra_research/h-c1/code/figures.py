"""
H-C1: Figure generation.
4 figures: eta_sq_comparison (MANDATORY), pass1_by_condition_scale,
seed_variance_7b, scale_attenuation_scatter.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from config import CONDITIONS, SEEDS, BENCHMARKS, FIGURES_DIR, RESULTS_JSON


def plot_eta_sq_comparison(
    eta_sq_7b: dict,
    eta_sq_1b: dict,
    out_path: str,
) -> None:
    """MANDATORY: Grouped bar chart η² at 1.3B vs 7B per benchmark."""
    benchmarks = [b for b in BENCHMARKS if eta_sq_7b.get(b) is not None or eta_sq_1b.get(b) is not None]
    x = np.arange(len(benchmarks))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 5))
    vals_1b = [eta_sq_1b.get(b, 0) or 0 for b in benchmarks]
    vals_7b = [eta_sq_7b.get(b, 0) or 0 for b in benchmarks]

    bars1 = ax.bar(x - width / 2, vals_1b, width, label="η² at 1.3B (H-E2)", color="#2196F3", alpha=0.85)
    bars2 = ax.bar(x + width / 2, vals_7b, width, label="η² at 7B (H-C1)", color="#FF5722", alpha=0.85)

    ax.set_xlabel("Benchmark")
    ax.set_ylabel("η² (proportion of variance explained)")
    ax.set_title("Scale Attenuation of Source Identity Effect\nη² at 1.3B vs 7B")
    ax.set_xticks(x)
    ax.set_xticklabels([b.capitalize() for b in benchmarks])
    ax.legend()
    ax.set_ylim(0, 1)

    for bar in bars1 + bars2:
        h = bar.get_height()
        if h > 0.01:
            ax.annotate(f"{h:.3f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_pass1_by_condition_scale(
    results_7b: dict,
    results_1b: dict,
    out_path: str,
) -> None:
    """Grouped bar chart: mean pass@1 per condition × scale × benchmark."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    x = np.arange(len(CONDITIONS))
    width = 0.35

    for ax, bench in zip(axes, BENCHMARKS):
        means_1b = [np.mean(results_1b.get(c, {}).get(bench, [0])) for c in CONDITIONS]
        means_7b = [np.mean(results_7b.get(c, {}).get(bench, [0])) for c in CONDITIONS]
        stds_7b = [np.std(results_7b.get(c, {}).get(bench, [0])) for c in CONDITIONS]

        ax.bar(x - width / 2, means_1b, width, label="1.3B (H-E2)", color="#2196F3", alpha=0.85)
        ax.bar(x + width / 2, means_7b, width, yerr=stds_7b, capsize=3,
               label="7B (H-C1)", color="#FF5722", alpha=0.85)
        ax.set_title(f"{bench.capitalize()} pass@1 by Condition × Scale")
        ax.set_ylabel("pass@1")
        ax.set_xticks(x)
        ax.set_xticklabels([c.replace("_", "\n") for c in CONDITIONS], fontsize=8)
        ax.legend(fontsize=8)
        ax.set_ylim(0, 1)

    plt.suptitle("Pass@1 by Source Condition and Model Scale", fontsize=12)
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_seed_variance_7b(
    results_7b: dict,
    out_path: str,
) -> None:
    """Box plots of pass@1 across 3 seeds per condition at 7B."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, bench in zip(axes, BENCHMARKS):
        data = [results_7b.get(c, {}).get(bench, []) for c in CONDITIONS]
        ax.boxplot(data, patch_artist=True,
                   boxprops=dict(facecolor="#FF5722", alpha=0.6))
        ax.set_xticks(range(1, len(CONDITIONS) + 1))
        ax.set_xticklabels([c.replace("_", "\n") for c in CONDITIONS])
        for i, vals in enumerate(data):
            ax.scatter([i + 1] * len(vals), vals, color="black", s=20, zorder=5)
        ax.set_title(f"{bench.capitalize()} — Seed Variance at 7B")
        ax.set_ylabel("pass@1")
        ax.set_ylim(0, 1)

    plt.suptitle("Per-Seed pass@1 Distribution at 7B (H-C1)", fontsize=12)
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_scale_attenuation_scatter(
    eta_sq_7b: dict,
    eta_sq_1b: dict,
    out_path: str,
) -> None:
    """Scatter: x=η²_1.3B, y=η²_7B; diagonal = no attenuation."""
    fig, ax = plt.subplots(figsize=(5, 5))
    max_val = 0
    for bench in BENCHMARKS:
        v1 = eta_sq_1b.get(bench)
        v7 = eta_sq_7b.get(bench)
        if v1 is None or v7 is None:
            continue
        ax.scatter(v1, v7, label=bench.capitalize(), s=100, zorder=5)
        ax.annotate(bench, (v1, v7), textcoords="offset points", xytext=(8, 5), fontsize=9)
        max_val = max(max_val, v1, v7)

    lim = min(max_val * 1.15 + 0.05, 1.0)
    ax.plot([0, lim], [0, lim], "k--", lw=1, label="No attenuation (y=x)")
    ax.set_xlabel("η²_1.3B (H-E2)")
    ax.set_ylabel("η²_7B (H-C1)")
    ax.set_title("Scale Attenuation Scatter\n(below diagonal = attenuation confirmed)")
    ax.legend(fontsize=8)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def generate_all_figures(
    results_7b: dict,
    results_1b: dict,
    eta_sq_7b: dict,
    eta_sq_1b: dict,
    figures_dir: str = FIGURES_DIR,
) -> None:
    """Generate and save all 4 required figures."""
    plot_eta_sq_comparison(
        eta_sq_7b, eta_sq_1b,
        str(Path(figures_dir) / "eta_sq_comparison.png"),
    )
    plot_pass1_by_condition_scale(
        results_7b, results_1b,
        str(Path(figures_dir) / "pass1_by_condition_scale.png"),
    )
    plot_seed_variance_7b(
        results_7b,
        str(Path(figures_dir) / "seed_variance_7b.png"),
    )
    plot_scale_attenuation_scatter(
        eta_sq_7b, eta_sq_1b,
        str(Path(figures_dir) / "scale_attenuation_scatter.png"),
    )
    print(f"All figures saved to: {figures_dir}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="H-C1 Figure Generation")
    parser.add_argument("--results_json", default=RESULTS_JSON)
    parser.add_argument("--figures_dir", default=FIGURES_DIR)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    if args.smoke:
        # Render to /tmp to verify matplotlib works
        eta_7b = {"humaneval": 0.35, "mbpp": 0.40}
        eta_1b = {"humaneval": 0.81, "mbpp": 0.75}
        plot_eta_sq_comparison(eta_7b, eta_1b, "/tmp/test_eta_sq.png")
        print("Smoke OK: figures.py renders correctly")
        return

    if not Path(args.results_json).exists():
        print(f"[ERROR] Results not found: {args.results_json}")
        return

    with open(args.results_json) as f:
        data = json.load(f)

    results_7b = {c: data.get(c, {}) for c in CONDITIONS}
    eta_sq_7b = data.get("eta_sq_7b", {})
    eta_sq_1b = data.get("eta_sq_1b", {})

    from analyze import load_h_e2_results
    from config import H_E2_RESULTS_CSV
    results_1b = load_h_e2_results(H_E2_RESULTS_CSV)

    generate_all_figures(results_7b, results_1b, eta_sq_7b, eta_sq_1b, args.figures_dir)


if __name__ == "__main__":
    main()
