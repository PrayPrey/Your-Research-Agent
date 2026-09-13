"""H-E1 Evaluate: Metrics + figures for gate validation."""
import os
import torch
import matplotlib.pyplot as plt
from config import Config


def check_gate_metrics(results: dict) -> dict:
    """Check PoC gate criteria."""
    rewards = results["rewards"]

    min_val = rewards.min().item()
    max_val = rewards.max().item()
    range_ok = (min_val >= 0.0) and (max_val <= 1.0)

    variance = rewards.var().item()
    variance_ok = variance > 0.0

    grad_flow_ok = results.get("grad_flow_ok", False)

    code_execution_ok = True

    return {
        "code_execution": code_execution_ok,
        "score_range": range_ok,
        "score_variance": variance_ok,
        "gradient_flow": grad_flow_ok,
        "all_passed": all([code_execution_ok, range_ok, variance_ok, grad_flow_ok]),
        "metrics": {
            "min": min_val,
            "max": max_val,
            "mean": rewards.mean().item(),
            "std": rewards.std().item(),
            "variance": variance,
        }
    }


def plot_score_distribution(rewards: torch.Tensor, out_dir: str) -> str:
    """Plot histogram of reward scores."""
    plt.figure(figsize=(10, 6))
    plt.hist(rewards.numpy(), bins=50, edgecolor='black', alpha=0.7)
    plt.xlabel('Reward Score')
    plt.ylabel('Frequency')
    plt.title('IFEval Soft Reward Score Distribution')
    plt.axvline(rewards.mean().item(), color='red', linestyle='--', label=f'Mean: {rewards.mean():.3f}')
    plt.legend()
    plt.tight_layout()

    path = os.path.join(out_dir, 'score_distribution.png')
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_soft_vs_hard(soft_rewards: torch.Tensor, hard_rewards: torch.Tensor, out_dir: str) -> str:
    """Plot comparison of soft vs hard rewards."""
    plt.figure(figsize=(10, 6))
    plt.scatter(hard_rewards.numpy(), soft_rewards.numpy(), alpha=0.3, s=10)
    plt.xlabel('Hard (Binary) Reward')
    plt.ylabel('Soft (Continuous) Reward')
    plt.title('Soft vs Hard Reward Comparison')
    plt.plot([0, 1], [0, 1], 'r--', label='Identity')
    plt.legend()
    plt.tight_layout()

    path = os.path.join(out_dir, 'soft_vs_hard.png')
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_gate_comparison(gate_results: dict, out_dir: str) -> str:
    """Plot gate criteria pass/fail."""
    criteria = ['code_execution', 'score_range', 'score_variance', 'gradient_flow']
    values = [1 if gate_results[c] else 0 for c in criteria]
    colors = ['green' if v else 'red' for v in values]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(criteria, values, color=colors, edgecolor='black')
    plt.ylim(0, 1.5)
    plt.ylabel('Pass (1) / Fail (0)')
    plt.title('H-E1 MUST_WORK Gate Criteria')

    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                'PASS' if val else 'FAIL', ha='center', fontweight='bold')

    plt.xticks(rotation=15)
    plt.tight_layout()

    path = os.path.join(out_dir, 'gate_comparison.png')
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def generate_all_figures(results: dict, gate_results: dict, out_dir: str) -> list[str]:
    """Generate all required figures."""
    os.makedirs(out_dir, exist_ok=True)

    figures = []
    figures.append(plot_score_distribution(results["rewards"], out_dir))
    figures.append(plot_soft_vs_hard(results["rewards"], results["hard_rewards"], out_dir))
    figures.append(plot_gate_comparison(gate_results, out_dir))

    return figures


if __name__ == "__main__":
    cfg = Config()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg.output_dir = os.path.join(base_dir, "figures")

    results_path = os.path.join(cfg.output_dir, "results.pt")
    if not os.path.exists(results_path):
        print("No results.pt found. Run train.py first.")
        exit(1)

    results = torch.load(results_path, weights_only=False)
    gate_results = check_gate_metrics(results)

    print("=== Gate Metrics ===")
    for k, v in gate_results.items():
        print(f"  {k}: {v}")

    figures = generate_all_figures(results, gate_results, cfg.output_dir)
    print(f"\nGenerated figures: {figures}")
