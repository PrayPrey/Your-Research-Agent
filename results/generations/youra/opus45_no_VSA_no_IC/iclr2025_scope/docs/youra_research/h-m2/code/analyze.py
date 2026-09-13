"""Analysis: r_opt extraction, log-linear regression, bootstrap CI, plotting."""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

from config import MODELS, Paths, AnalysisConfig


def compute_r_opt(sweep_csv: str, output_csv: str | None = None) -> pd.DataFrame:
    """Extract optimal rank per (model, seed). Ties use geometric mean."""
    paths = Paths()
    output_csv = output_csv or paths.optimal_ranks_csv

    df = pd.read_csv(sweep_csv)

    results = []
    for model in df["model"].unique():
        n_params = MODELS[model]
        for seed in df["seed"].unique():
            subset = df[(df["model"] == model) & (df["seed"] == seed)]
            max_f1 = subset["f1_score"].max()
            best_ranks = subset[subset["f1_score"] == max_f1]["rank"].values

            if len(best_ranks) > 1:
                r_opt = np.exp(np.mean(np.log(best_ranks)))
            else:
                r_opt = best_ranks[0]

            results.append({
                "model": model,
                "N": n_params,
                "seed": seed,
                "r_opt": r_opt,
                "best_f1": max_f1,
            })

    result_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    result_df.to_csv(output_csv, index=False)
    print(f"Optimal ranks saved: {output_csv}")

    return result_df


def fit_scaling_law(optimal_ranks: pd.DataFrame, n_bootstrap: int = 1000, output_json: str | None = None) -> dict:
    """Fit log(r_opt) = alpha*log(N) + log(c) with bootstrap CI."""
    paths = Paths()
    output_json = output_json or paths.scaling_fit_json

    x = np.log(optimal_ranks["N"].values)
    y = np.log(optimal_ranks["r_opt"].values)

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    alpha = slope
    c = np.exp(intercept)
    r2 = r_value ** 2

    boot_alphas = []
    np.random.seed(42)
    for _ in range(n_bootstrap):
        idx = np.random.choice(len(x), len(x), replace=True)
        if len(np.unique(x[idx])) < 2:
            continue
        s, *_ = stats.linregress(x[idx], y[idx])
        boot_alphas.append(s)

    ci_low, ci_high = np.percentile(boot_alphas, [2.5, 97.5])

    result = {
        "alpha": float(alpha),
        "alpha_ci_low": float(ci_low),
        "alpha_ci_high": float(ci_high),
        "c": float(c),
        "r2": float(r2),
        "p_value": float(p_value),
        "std_err": float(std_err),
        "n_bootstrap": n_bootstrap,
        "n_data_points": len(x),
    }

    os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Scaling fit saved: {output_json}")

    return result


def plot_scaling(fit_result: dict, optimal_ranks: pd.DataFrame, output_png: str | None = None) -> None:
    """Generate log-log scaling plot with fit line and CI band."""
    paths = Paths()
    output_png = output_png or paths.scaling_plot_png

    os.makedirs(os.path.dirname(output_png) or ".", exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    log_n = np.log10(optimal_ranks["N"].values)
    log_r = np.log10(optimal_ranks["r_opt"].values)

    ax.scatter(log_n, log_r, alpha=0.7, s=100, c="steelblue", edgecolors="black", linewidth=0.5)

    alpha = fit_result["alpha"]
    c = fit_result["c"]
    x_line = np.linspace(log_n.min() - 0.1, log_n.max() + 0.1, 100)
    y_line = alpha * x_line * np.log(10) / np.log(10) + np.log10(c)

    y_line_actual = np.log10(c * (10 ** x_line) ** alpha)
    ax.plot(x_line, y_line_actual, "r-", linewidth=2, label=f"Fit: α={alpha:.3f}")

    ci_low = fit_result["alpha_ci_low"]
    ci_high = fit_result["alpha_ci_high"]
    y_low = np.log10(c * (10 ** x_line) ** ci_low)
    y_high = np.log10(c * (10 ** x_line) ** ci_high)
    ax.fill_between(x_line, y_low, y_high, alpha=0.2, color="red", label=f"95% CI: [{ci_low:.3f}, {ci_high:.3f}]")

    ax.set_xlabel("log₁₀(N) - Model Parameters", fontsize=12)
    ax.set_ylabel("log₁₀(r_opt) - Optimal Rank", fontsize=12)
    ax.set_title("LoRA Optimal Rank Scaling Law (h-e1)", fontsize=14)
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    textstr = f"R² = {fit_result['r2']:.3f}\nα ∈ (0.3, 0.7): {'PASS' if 0.3 < alpha < 0.7 else 'FAIL'}"
    ax.text(0.95, 0.05, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment="bottom", horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_png, dpi=150)
    plt.close()
    print(f"Scaling plot saved: {output_png}")


def check_pass_fail(fit_result: dict) -> dict:
    """Check if results meet success criteria."""
    alpha = fit_result["alpha"]
    ci_low = fit_result["alpha_ci_low"]
    ci_high = fit_result["alpha_ci_high"]
    r2 = fit_result["r2"]

    checks = {
        "alpha_in_range": 0.3 < alpha < 0.7,
        "ci_excludes_zero": ci_low > 0,
        "ci_excludes_one": ci_high < 1,
        "r2_threshold": r2 > 0.7,
    }
    checks["overall_pass"] = all(checks.values())

    return checks


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze rank sweep results")
    parser.add_argument("--sweep-csv", default="results/h-e1_rank_sweep.csv")
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--figures-dir", default="figures")

    args = parser.parse_args()

    optimal_df = compute_r_opt(
        args.sweep_csv,
        os.path.join(args.output_dir, "h-e1_optimal_ranks.csv"),
    )

    fit = fit_scaling_law(
        optimal_df,
        output_json=os.path.join(args.output_dir, "h-e1_scaling_fit.json"),
    )

    plot_scaling(
        fit,
        optimal_df,
        os.path.join(args.figures_dir, "h-e1_scaling_plot.png"),
    )

    checks = check_pass_fail(fit)
    print("\n=== Pass/Fail Criteria ===")
    for k, v in checks.items():
        print(f" {k}: {'PASS' if v else 'FAIL'}")
