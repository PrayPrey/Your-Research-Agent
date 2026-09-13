import matplotlib.pyplot as plt
import os


def plot_gate_metrics_comparison(initial: dict, final: dict, out_path: str) -> None:
    categories = ["Security Issues", "Reliability Issues"]
    initial_vals = [initial.get("security", 0), initial.get("reliability", 0)]
    final_vals = [final.get("security", 0), final.get("reliability", 0)]

    x = range(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))
    bars1 = ax.bar([i - width/2 for i in x], initial_vals, width, label="Initial", color="salmon")
    bars2 = ax.bar([i + width/2 for i in x], final_vals, width, label="Final", color="lightgreen")

    ax.set_ylabel("Issue Count")
    ax.set_title("H-M2: Static Analysis Feedback Loop - Issue Reduction")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()

    for bar in bars1 + bars2:
        h = bar.get_height()
        ax.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_issue_reduction_over_iterations(history: list[dict], out_path: str) -> None:
    if not history:
        return

    iterations = [h["iteration"] for h in history]
    security = [h["security_count"] for h in history]
    reliability = [h["reliability_count"] for h in history]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(iterations, security, "o-", label="Security Issues", color="red")
    ax.plot(iterations, reliability, "s-", label="Reliability Issues", color="blue")

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Issue Count")
    ax.set_title("Issue Reduction Over Feedback Iterations")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_cwe_distribution(prompts: list[dict], out_path: str) -> None:
    cwe_counts = {}
    for p in prompts:
        cwe = p.get("cwe", "unknown")
        cwe_counts[cwe] = cwe_counts.get(cwe, 0) + 1

    sorted_cwes = sorted(cwe_counts.items(), key=lambda x: -x[1])[:15]
    cwes = [c[0] for c in sorted_cwes]
    counts = [c[1] for c in sorted_cwes]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(cwes, counts, color="steelblue")
    ax.set_xlabel("Count")
    ax.set_ylabel("CWE Category")
    ax.set_title("Top 15 CWE Categories in Dataset")
    ax.invert_yaxis()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
