import matplotlib
matplotlib.use("Agg")

import sys
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu


@dataclass
class H_M1Config:
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"
    fallback_script: str = "docs/youra_research/h-e1/code/profile_mbpp.py"
    k: int = 50
    seed: int = 42
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    min_mean_var_difference: float = 0.0


FIG1 = {"figsize": (8, 5), "colors": {"variance_50": "steelblue", "random_50": "darkorange"},
        "strip_jitter": 0.15, "strip_alpha": 0.5, "strip_size": 4}
FIG2 = {"figsize": (8, 5), "bins": 10, "range": [0.0, 0.25], "alpha": 0.6,
        "colors": {"variance_50": "steelblue", "random_50": "darkorange"}}
FIG3 = {"figsize": (9, 5), "boundary_color": "red", "boundary_linestyle": "--",
        "shaded_alpha": 0.12, "shaded_color": "steelblue"}
FIG4 = {"figsize": (8, 5), "linestyles": {"variance_50": "-", "random_50": "--"},
        "colors": {"variance_50": "steelblue", "random_50": "darkorange"}, "legend_loc": "lower right"}
FIGURE_DEFAULTS = {"dpi": 150, "tight_layout": True}


def load_profiling_output(json_path: Path):
    """Parse H-E1 JSON → (problem_ids, p_i, variance_i), all shape (N,)."""
    if not json_path.exists():
        raise FileNotFoundError(f"Profiling JSON not found: {json_path}")

    with open(json_path) as f:
        data = json.load(f)

    problems = data["problems"]
    sorted_keys = sorted(problems.keys(), key=int)

    problem_ids = np.array([int(k) for k in sorted_keys])
    p_i = np.array([problems[k]["p_i"] for k in sorted_keys])
    variance_i = np.array([problems[k]["variance_i"] for k in sorted_keys])

    assert np.all((p_i >= 0) & (p_i <= 1)), "p_i out of [0,1]"
    assert np.all((variance_i >= 0) & (variance_i <= 0.25 + 1e-9)), "variance_i out of [0,0.25]"

    return problem_ids, p_i, variance_i


def run_fallback_profiling(results_dir: Path) -> Path:
    """Rerun H-E1 profiling via subprocess. Returns regenerated JSON path."""
    script = "docs/youra_research/h-e1/code/profile_mbpp.py"
    print(f"Running fallback profiling: {script}")
    subprocess.run([sys.executable, script], check=True)
    json_path = results_dir.parent.parent / "h-e1" / "results" / "mbpp_variance_profile.json"
    return json_path


def compare_selections(variance_i: np.ndarray, problem_ids: np.ndarray,
                       k: int = 50, seed: int = 42) -> dict:
    """Run variance-vs-random selection comparison."""
    N = len(variance_i)
    ranked_idx = np.argsort(variance_i)[::-1]
    variance_50_idx = ranked_idx[:k]
    rng = np.random.default_rng(seed)
    random_50_idx = rng.choice(N, k, replace=False)

    variance_50_var = variance_i[variance_50_idx]
    random_50_var = variance_i[random_50_idx]

    mean_var_selected = float(np.mean(variance_50_var))
    mean_var_random = float(np.mean(random_50_var))
    difference = mean_var_selected - mean_var_random
    boundary_gap = float(variance_i[ranked_idx[k - 1]] - variance_i[ranked_idx[k]])
    gate_passed = difference > 0

    mwu_stat, mwu_p = mannwhitneyu(variance_50_var, random_50_var, alternative="greater")

    # Mechanism verification asserts
    assert len(variance_50_idx) == k
    assert variance_i[ranked_idx[0]] >= variance_i[ranked_idx[-1]]
    assert np.all(variance_i[variance_50_idx] >= variance_i[ranked_idx[k]])

    return {
        "gate_passed": gate_passed,
        "mean_var_selected": mean_var_selected,
        "mean_var_random": mean_var_random,
        "difference": difference,
        "boundary_gap": boundary_gap,
        "mwu_stat": float(mwu_stat),
        "mwu_p": float(mwu_p),
        "variance_50_ids": problem_ids[variance_50_idx].tolist(),
        "random_50_ids": problem_ids[random_50_idx].tolist(),
        "seed": seed,
        "n_total": N,
        "k": k,
    }


def make_figures(variance_i: np.ndarray, variance_50_idx: np.ndarray,
                 random_50_idx: np.ndarray, p_i: np.ndarray, figures_dir: Path) -> None:
    """Save fig1–fig4 PNGs to figures_dir."""
    figures_dir.mkdir(parents=True, exist_ok=True)

    var_selected = variance_i[variance_50_idx]
    var_random = variance_i[random_50_idx]
    k = len(variance_50_idx)
    N = len(variance_i)

    # Fig 1: bar + strip plot
    fig, ax = plt.subplots(figsize=FIG1["figsize"])
    x = [0, 1]
    means = [float(np.mean(var_selected)), float(np.mean(var_random))]
    colors = [FIG1["colors"]["variance_50"], FIG1["colors"]["random_50"]]
    ax.bar(["variance-50", "random-50"], means, color=colors, alpha=0.7)
    jitter = FIG1["strip_jitter"]
    rng = np.random.default_rng(0)
    ax.scatter(rng.uniform(-jitter, jitter, k), var_selected,
               alpha=FIG1["strip_alpha"], s=FIG1["strip_size"] ** 2, color=colors[0])
    ax.scatter(1 + rng.uniform(-jitter, jitter, k), var_random,
               alpha=FIG1["strip_alpha"], s=FIG1["strip_size"] ** 2, color=colors[1])
    ax.set_ylabel("variance_i = p_i*(1-p_i)")
    ax.set_title("Mean Variance: Top-50 by Variance vs Random-50")
    plt.tight_layout()
    fig.savefig(figures_dir / "fig1_mean_comparison.png", dpi=FIGURE_DEFAULTS["dpi"])
    plt.close(fig)

    # Fig 2: side-by-side histograms
    fig, axes = plt.subplots(1, 2, figsize=FIG2["figsize"], sharey=True)
    bins, rng_h, alpha = FIG2["bins"], FIG2["range"], FIG2["alpha"]
    axes[0].hist(variance_i, bins=bins, range=rng_h, color="grey", alpha=0.4, label="all-374")
    axes[0].hist(var_selected, bins=bins, range=rng_h, alpha=alpha,
                 color=FIG2["colors"]["variance_50"], label="variance-50")
    axes[0].set_title("Variance-50 Distribution")
    axes[0].legend()
    axes[1].hist(variance_i, bins=bins, range=rng_h, color="grey", alpha=0.4, label="all-374")
    axes[1].hist(var_random, bins=bins, range=rng_h, alpha=alpha,
                 color=FIG2["colors"]["random_50"], label="random-50")
    axes[1].set_title("Random-50 Distribution")
    axes[1].legend()
    for ax in axes:
        ax.set_xlabel("variance_i")
    axes[0].set_ylabel("count")
    plt.tight_layout()
    fig.savefig(figures_dir / "fig2_histograms.png", dpi=FIGURE_DEFAULTS["dpi"])
    plt.close(fig)

    # Fig 3: rank plot
    sorted_var = variance_i[np.argsort(variance_i)[::-1]]
    fig, ax = plt.subplots(figsize=FIG3["figsize"])
    ax.plot(range(1, N + 1), sorted_var, color="steelblue")
    ax.axvline(k, color=FIG3["boundary_color"], linestyle=FIG3["boundary_linestyle"],
               label=f"rank-{k} boundary")
    ax.axvspan(1, k, alpha=FIG3["shaded_alpha"], color=FIG3["shaded_color"], label="selected region")
    ax.set_xlabel("rank (by variance, descending)")
    ax.set_ylabel("variance_i")
    ax.set_title("Variance Distribution by Rank")
    ax.legend()
    plt.tight_layout()
    fig.savefig(figures_dir / "fig3_rank_plot.png", dpi=FIGURE_DEFAULTS["dpi"])
    plt.close(fig)

    # Fig 4: empirical CDF
    fig, ax = plt.subplots(figsize=FIG4["figsize"])
    for arr, label, color, ls in [
        (np.sort(var_selected), "variance-50", FIG4["colors"]["variance_50"], FIG4["linestyles"]["variance_50"]),
        (np.sort(var_random), "random-50", FIG4["colors"]["random_50"], FIG4["linestyles"]["random_50"]),
    ]:
        y = np.linspace(0, 1, len(arr))
        ax.plot(arr, y, label=label, color=color, linestyle=ls)
    ax.set_xlabel("variance_i")
    ax.set_ylabel("cumulative fraction")
    ax.set_title("Empirical CDF: Variance-50 vs Random-50")
    ax.legend(loc=FIG4["legend_loc"])
    plt.tight_layout()
    fig.savefig(figures_dir / "fig4_cdf.png", dpi=FIGURE_DEFAULTS["dpi"])
    plt.close(fig)


def save_results(results: dict, results_dir: Path) -> None:
    """Write results dict → results_dir/comparison_results.json."""
    results_dir.mkdir(parents=True, exist_ok=True)
    out = results_dir / "comparison_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved: {out}")


def main() -> int:
    cfg = H_M1Config()
    json_path = Path(cfg.profiling_json)
    results_dir = Path(cfg.results_dir)
    figures_dir = Path(cfg.figures_dir)

    # Load profiling output (fallback if missing)
    try:
        problem_ids, p_i, variance_i = load_profiling_output(json_path)
    except FileNotFoundError:
        print(f"WARNING: {json_path} not found — running fallback profiling")
        json_path = run_fallback_profiling(results_dir)
        problem_ids, p_i, variance_i = load_profiling_output(json_path)

    print(f"Loaded {len(problem_ids)} problems from profiling output")
    print(f"variance_i: mean={np.mean(variance_i):.4f}, max={np.max(variance_i):.4f}")

    # Core comparison
    results = compare_selections(variance_i, problem_ids, k=cfg.k, seed=cfg.seed)

    print(f"\n=== H-M1 Gate Result ===")
    print(f"mean_var_selected = {results['mean_var_selected']:.4f}")
    print(f"mean_var_random   = {results['mean_var_random']:.4f}")
    print(f"difference        = {results['difference']:.4f}")
    print(f"boundary_gap      = {results['boundary_gap']:.4f}")
    print(f"mwu_stat          = {results['mwu_stat']:.2f}")
    print(f"mwu_p             = {results['mwu_p']:.4f}")
    print(f"gate_passed       = {results['gate_passed']}")

    # Figures
    ranked_idx = np.argsort(variance_i)[::-1]
    variance_50_idx = ranked_idx[:cfg.k]
    rng = np.random.default_rng(cfg.seed)
    random_50_idx = rng.choice(len(variance_i), cfg.k, replace=False)
    make_figures(variance_i, variance_50_idx, random_50_idx, p_i, figures_dir)
    print(f"Figures saved to {figures_dir}")

    # Save results
    save_results(results, results_dir)

    gate_str = "PASSED" if results["gate_passed"] else "FAILED"
    print(f"\nGATE: {gate_str}")
    return 0 if results["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
