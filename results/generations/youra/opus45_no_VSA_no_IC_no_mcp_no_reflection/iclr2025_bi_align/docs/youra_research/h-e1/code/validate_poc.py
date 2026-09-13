"""H-E1 PoC Validation: Test reward signal mechanism with synthetic responses."""
import os
import sys
import torch
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data import load_ifeval, parse_constraints
from model import IFEvalRewardSignal, BaselineChecker


def generate_synthetic_response(prompt: str, constraints: list[dict]) -> str:
    """Generate synthetic response that partially satisfies constraints."""
    import random
    random.seed(42)

    response_parts = []
    word_target = 100

    for c in constraints:
        if c.get("type") == "length":
            word_target = c.get("target", 100)
        elif c.get("type") == "keyword":
            keywords = c.get("keywords", [])
            if c.get("must_include", True) and keywords:
                if random.random() > 0.3:
                    response_parts.extend(keywords[:2])

    base_words = ["The", "response", "includes", "various", "elements", "to", "satisfy",
                  "the", "given", "constraints", "while", "demonstrating", "proper",
                  "format", "and", "structure", "as", "requested", "by", "the", "user"]

    while len(response_parts) < word_target:
        response_parts.extend(base_words)

    return " ".join(response_parts[:word_target])


def run_validation(cfg: Config) -> dict:
    """Run PoC validation with synthetic responses."""
    print("Loading IFEval dataset...")
    examples = load_ifeval(cfg)
    print(f"Loaded {len(examples)} examples")

    all_constraints = [parse_constraints(ex) for ex in examples]

    print("Generating synthetic responses for validation...")
    responses = []
    for i, ex in enumerate(examples):
        constraints = all_constraints[i]
        response = generate_synthetic_response(ex["prompt"], constraints)
        responses.append(response)
    print(f"Generated {len(responses)} synthetic responses")

    print("Computing rewards with IFEvalRewardSignal...")
    reward_signal = IFEvalRewardSignal(soft_margin=cfg.soft_margin)
    baseline_checker = BaselineChecker()

    soft_rewards = []
    hard_rewards = []

    for i, (response, constraints) in enumerate(zip(responses, all_constraints)):
        if not constraints:
            soft_rewards.append(torch.tensor(0.5, dtype=torch.float32))
            hard_rewards.append(0.5)
            continue

        soft_reward = reward_signal(response, constraints)
        soft_rewards.append(soft_reward)

        hard_reward = baseline_checker.check(response, constraints)
        hard_rewards.append(hard_reward)

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(responses)} examples")

    print(f"Computed rewards for {len(soft_rewards)} examples")

    rewards_tensor = torch.stack(soft_rewards)
    print(f"Rewards tensor shape: {rewards_tensor.shape}")
    print(f"requires_grad: {rewards_tensor.requires_grad}")

    print("Testing backward pass...")
    reward_signal.zero_grad()
    loss = rewards_tensor.sum()
    loss.backward()

    grad_flow_ok = reward_signal.scale.grad is not None
    print(f"Gradient flow: {'OK' if grad_flow_ok else 'FAILED'}")
    if grad_flow_ok:
        print(f"  scale.grad = {reward_signal.scale.grad.item():.6f}")

    return {
        "rewards": rewards_tensor.detach(),
        "hard_rewards": torch.tensor(hard_rewards),
        "grad_flow_ok": grad_flow_ok,
        "num_examples": len(soft_rewards),
    }


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


def generate_figures(results: dict, gate_results: dict, out_dir: str) -> list[str]:
    """Generate validation figures."""
    os.makedirs(out_dir, exist_ok=True)
    figures = []

    rewards = results["rewards"]
    plt.figure(figsize=(10, 6))
    plt.hist(rewards.numpy(), bins=50, edgecolor='black', alpha=0.7)
    plt.xlabel('Reward Score')
    plt.ylabel('Frequency')
    plt.title('IFEval Soft Reward Score Distribution (541 prompts)')
    plt.axvline(rewards.mean().item(), color='red', linestyle='--',
                label=f'Mean: {rewards.mean():.3f}')
    plt.legend()
    plt.tight_layout()
    path = os.path.join(out_dir, 'score_distribution.png')
    plt.savefig(path, dpi=150)
    plt.close()
    figures.append(path)

    plt.figure(figsize=(10, 6))
    plt.scatter(results["hard_rewards"].numpy(), rewards.numpy(), alpha=0.3, s=10)
    plt.xlabel('Hard (Binary) Reward')
    plt.ylabel('Soft (Continuous) Reward')
    plt.title('Soft vs Hard Reward Comparison')
    plt.plot([0, 1], [0, 1], 'r--', label='Identity')
    plt.legend()
    plt.tight_layout()
    path = os.path.join(out_dir, 'soft_vs_hard.png')
    plt.savefig(path, dpi=150)
    plt.close()
    figures.append(path)

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
    figures.append(path)

    return figures


if __name__ == "__main__":
    cfg = Config()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg.output_dir = os.path.join(base_dir, "figures")

    results = run_validation(cfg)
    gate_results = check_gate_metrics(results)

    print("\n=== Gate Metrics ===")
    for k, v in gate_results.items():
        print(f"  {k}: {v}")

    figures = generate_figures(results, gate_results, cfg.output_dir)
    print(f"\nGenerated figures: {figures}")

    torch.save({**results, "gate_results": gate_results},
               os.path.join(cfg.output_dir, "results.pt"))
    print(f"Results saved to {cfg.output_dir}/results.pt")

    print("\n=== FINAL VERDICT ===")
    print(f"GATE PASSED: {gate_results['all_passed']}")
