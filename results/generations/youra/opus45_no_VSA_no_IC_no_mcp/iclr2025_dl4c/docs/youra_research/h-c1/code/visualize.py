"""Visualization functions for H-C1 experiment."""
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

plt.style.use('seaborn-v0_8-whitegrid')


def plot_exec_advantage_bar(complexity_effect_result: dict, out_path: str) -> None:
    """Bar chart comparing execution advantage on HumanEval vs MBPP."""
    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ['HumanEval\n(Simple)', 'MBPP\n(Complex)']
    values = [
        complexity_effect_result["humaneval_exec_advantage"],
        complexity_effect_result["mbpp_exec_advantage"],
    ]
    colors = ['#5DA5DA', '#FAA43A']

    bars = ax.bar(labels, values, color=colors, edgecolor='black', linewidth=1.2)

    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_ylabel('Execution Advantage\n(pass@1_exec - pass@1_critic)', fontsize=12)
    ax.set_title('Execution Feedback Advantage by Task Complexity', fontsize=14, fontweight='bold')

    for bar, val in zip(bars, values):
        ax.annotate(f'{val:.3f}', xy=(bar.get_x() + bar.get_width()/2, val),
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

    effect = complexity_effect_result["complexity_effect"]
    supported = complexity_effect_result["hypothesis_supported"]
    status = "SUPPORTED" if supported else "NOT SUPPORTED"
    ax.text(0.95, 0.95, f'Complexity Effect: {effect:.3f}\nHypothesis: {status}',
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_pass_at_1_grouped(
    he_results: list[dict], mbpp_results: list[dict], out_path: str
) -> None:
    """Grouped bar chart: pass@1 for (execution, AI-critic) x (HumanEval, MBPP)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    he_exec = np.mean([r["execution_pass"] for r in he_results]) if he_results else 0
    he_critic = np.mean([r["critic_pass"] for r in he_results]) if he_results else 0
    mbpp_exec = np.mean([r["execution_pass"] for r in mbpp_results]) if mbpp_results else 0
    mbpp_critic = np.mean([r["critic_pass"] for r in mbpp_results]) if mbpp_results else 0

    x = np.array([0, 1])
    width = 0.35

    exec_vals = [he_exec, mbpp_exec]
    critic_vals = [he_critic, mbpp_critic]

    bars1 = ax.bar(x - width/2, exec_vals, width, label='Execution Feedback', color='#5DA5DA', edgecolor='black')
    bars2 = ax.bar(x + width/2, critic_vals, width, label='AI-Critic Feedback', color='#FAA43A', edgecolor='black')

    ax.set_ylabel('pass@1', fontsize=12)
    ax.set_title('Pass@1 by Feedback Mechanism and Benchmark', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(['HumanEval (Simple)', 'MBPP (Complex)'], fontsize=11)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.0)

    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 3), textcoords='offset points',
                        ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_error_type_breakdown(results: list[dict], out_path: str) -> None:
    """Stacked bar showing error types per benchmark (HumanEval vs MBPP)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    he_results = [r for r in results if not r["problem_id"].startswith("mbpp_")]
    mbpp_results = [r for r in results if r["problem_id"].startswith("mbpp_")]

    he_types = Counter([r.get("exec_feedback_type", "unknown") for r in he_results])
    mbpp_types = Counter([r.get("exec_feedback_type", "unknown") for r in mbpp_results])

    all_types = sorted(set(he_types.keys()) | set(mbpp_types.keys()))

    he_counts = [he_types.get(t, 0) for t in all_types]
    mbpp_counts = [mbpp_types.get(t, 0) for t in all_types]

    x = np.array([0, 1])
    width = 0.5

    colors = plt.cm.Set2(np.linspace(0, 1, len(all_types)))

    bottom_he = np.zeros(1)
    bottom_mbpp = np.zeros(1)

    for i, (t, color) in enumerate(zip(all_types, colors)):
        ax.bar(0, he_counts[i], width, bottom=bottom_he[0], label=t if i == 0 or t not in all_types[:i] else "", color=color, edgecolor='black')
        ax.bar(1, mbpp_counts[i], width, bottom=bottom_mbpp[0], color=color, edgecolor='black')
        bottom_he[0] += he_counts[i]
        bottom_mbpp[0] += mbpp_counts[i]

    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Execution Feedback Type Distribution', fontsize=14, fontweight='bold')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['HumanEval', 'MBPP'], fontsize=11)
    ax.legend(title='Feedback Type', loc='upper right')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_complexity_scatter(results: list[dict], out_path: str) -> None:
    """Scatter: problem complexity proxy vs execution advantage."""
    fig, ax = plt.subplots(figsize=(10, 6))

    he_results = [r for r in results if not r["problem_id"].startswith("mbpp_")]
    mbpp_results = [r for r in results if r["problem_id"].startswith("mbpp_")]

    he_x = list(range(len(he_results)))
    he_y = [r["execution_advantage"] for r in he_results]
    mbpp_x = list(range(len(mbpp_results)))
    mbpp_y = [r["execution_advantage"] for r in mbpp_results]

    ax.scatter(he_x, he_y, alpha=0.6, label='HumanEval', color='#5DA5DA', s=30)
    ax.scatter([x + len(he_results) + 10 for x in mbpp_x], mbpp_y, alpha=0.6,
               label='MBPP', color='#FAA43A', s=30)

    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=len(he_results) + 5, color='red', linestyle=':', alpha=0.3)

    if he_y:
        ax.axhline(y=np.mean(he_y), color='#5DA5DA', linestyle='-', alpha=0.7, linewidth=2)
    if mbpp_y:
        ax.axhline(y=np.mean(mbpp_y), color='#FAA43A', linestyle='-', alpha=0.7, linewidth=2)

    ax.set_xlabel('Problem Index', fontsize=12)
    ax.set_ylabel('Execution Advantage', fontsize=12)
    ax.set_title('Execution Advantage by Problem', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    print("Visualize module loaded")
