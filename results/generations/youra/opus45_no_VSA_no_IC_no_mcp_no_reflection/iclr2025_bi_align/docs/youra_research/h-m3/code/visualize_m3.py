"""H-M3 Visualization: AlpacaEval sweep analysis."""
import matplotlib.pyplot as plt
from pathlib import Path


def plot_baseline_vs_sweep_bar(results: dict, out_dir: str) -> None:
    """Bar chart: B2 vs T1-T4 AlpacaEval LC win rates."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    names = ["B2", "T1", "T2", "T3", "T4"]
    values = [results.get(n, {}).get("alpaca_lc", 0) for n in names]
    colors = ["red"] + ["steelblue"] * 4

    plt.figure(figsize=(8, 6))
    bars = plt.bar(names, values, color=colors)

    b2_val = results.get("B2", {}).get("alpaca_lc", 0)
    threshold = 0.95 * b2_val
    plt.axhline(y=threshold, color="orange", linestyle="--", label=f"0.95×B2={threshold:.3f}")

    plt.xlabel("Configuration")
    plt.ylabel("AlpacaEval LC Win Rate")
    plt.title("H-M3: Helpfulness Maintenance under Multi-Objective Training")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{out_dir}/alpaca_eval_bar.png", dpi=150)
    plt.close()


def plot_pareto_frontier(results: dict, out_dir: str) -> None:
    """Scatter: IFEval acc (x) vs AlpacaEval LC (y)."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))

    for name, data in results.items():
        x = data.get("ifeval_acc", 0)
        y = data.get("alpaca_lc", 0)
        color = "red" if name == "B2" else "steelblue"
        marker = "s" if name == "B2" else "o"
        plt.scatter(x, y, c=color, marker=marker, s=100, label=name)
        plt.annotate(name, (x, y), textcoords="offset points", xytext=(5, 5))

    plt.xlabel("IFEval Strict Accuracy")
    plt.ylabel("AlpacaEval LC Win Rate")
    plt.title("H-M3: Pareto Frontier (Controllability vs Helpfulness)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{out_dir}/pareto_frontier.png", dpi=150)
    plt.close()


def plot_alpha_line(results: dict, out_dir: str) -> None:
    """Line chart: win rate vs alpha value."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    data_points = []
    for name, data in results.items():
        alpha = data.get("alpha", 1.0 if name == "B2" else None)
        if alpha is not None:
            data_points.append((alpha, data.get("alpaca_lc", 0), name))

    data_points.sort(key=lambda x: x[0])
    alphas = [d[0] for d in data_points]
    scores = [d[1] for d in data_points]
    names = [d[2] for d in data_points]

    plt.figure(figsize=(8, 6))
    plt.plot(alphas, scores, "o-", color="steelblue", markersize=8)

    for a, s, n in data_points:
        plt.annotate(n, (a, s), textcoords="offset points", xytext=(5, 5))

    b2_idx = names.index("B2") if "B2" in names else -1
    if b2_idx >= 0:
        threshold = 0.95 * scores[b2_idx]
        plt.axhline(y=threshold, color="orange", linestyle="--", label=f"0.95×B2")

    plt.xlabel("Alpha (Helpfulness Weight)")
    plt.ylabel("AlpacaEval LC Win Rate")
    plt.title("H-M3: Win Rate vs Alpha")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{out_dir}/alpha_line.png", dpi=150)
    plt.close()


def generate_all_figures(results: dict, out_dir: str) -> None:
    """Generate all H-M3 figures."""
    plot_baseline_vs_sweep_bar(results, out_dir)
    plot_pareto_frontier(results, out_dir)
    plot_alpha_line(results, out_dir)
    print(f"Figures saved to {out_dir}/")


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python visualize_m3.py <results.json> [output_dir]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        results = json.load(f)

    out_dir = sys.argv[2] if len(sys.argv) > 2 else "figures"
    generate_all_figures(results, out_dir)
