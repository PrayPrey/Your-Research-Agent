"""H-E1 Train: Generation + reward computation driver."""
import os
import sys
import torch
from config import Config
from data import load_ifeval, parse_constraints
from model import IFEvalRewardSignal, BaselineChecker, load_generator, generate_responses


def run(cfg: Config) -> dict:
    """Run existence PoC: generate responses and compute rewards."""
    print(f"Loading IFEval dataset from {cfg.dataset_id}...")
    examples = load_ifeval(cfg)
    print(f"Loaded {len(examples)} examples")

    prompts = [ex["prompt"] for ex in examples]
    all_constraints = [parse_constraints(ex) for ex in examples]

    print(f"Loading generator model {cfg.model_id}...")
    model, tokenizer, device = load_generator(cfg)
    print(f"Model loaded on {device}")

    print(f"Generating {len(prompts)} responses...")
    responses = generate_responses(model, tokenizer, prompts, cfg, device)
    print(f"Generated {len(responses)} responses")

    del model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    print("Computing rewards with IFEvalRewardSignal...")
    reward_signal = IFEvalRewardSignal(soft_margin=cfg.soft_margin)
    baseline_checker = BaselineChecker()

    soft_rewards = []
    hard_rewards = []
    per_constraint = {}

    for i, (response, constraints) in enumerate(zip(responses, all_constraints)):
        if not constraints:
            continue

        soft_reward = reward_signal(response, constraints)
        soft_rewards.append(soft_reward)

        hard_reward = baseline_checker.check(response, constraints)
        hard_rewards.append(hard_reward)

        for c in constraints:
            c_type = c.get("type", "unknown")
            if c_type not in per_constraint:
                per_constraint[c_type] = {"soft": [], "hard": []}

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(responses)} examples")

    print(f"Computed rewards for {len(soft_rewards)} examples")

    rewards_tensor = torch.stack(soft_rewards)
    print(f"Rewards tensor shape: {rewards_tensor.shape}")
    print(f"requires_grad: {rewards_tensor.requires_grad}")

    print("Testing backward pass...")
    try:
        loss = rewards_tensor.sum()
        loss.backward()
        grad_flow_ok = True
        print("Backward pass successful")
    except Exception as e:
        grad_flow_ok = False
        print(f"Backward pass failed: {e}")

    return {
        "rewards": rewards_tensor.detach(),
        "hard_rewards": torch.tensor(hard_rewards),
        "per_constraint": per_constraint,
        "grad_flow_ok": grad_flow_ok,
        "num_examples": len(soft_rewards),
        "responses": responses,
    }


if __name__ == "__main__":
    cfg = Config()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg.output_dir = os.path.join(base_dir, "figures")
    os.makedirs(cfg.output_dir, exist_ok=True)

    results = run(cfg)

    print("\n=== Summary ===")
    print(f"Num examples: {results['num_examples']}")
    print(f"Soft rewards - mean: {results['rewards'].mean():.4f}, std: {results['rewards'].std():.4f}")
    print(f"Hard rewards - mean: {results['hard_rewards'].mean():.4f}, std: {results['hard_rewards'].std():.4f}")
    print(f"Gradient flow: {'OK' if results['grad_flow_ok'] else 'FAILED'}")

    torch.save(results, os.path.join(cfg.output_dir, "results.pt"))
    print(f"\nResults saved to {cfg.output_dir}/results.pt")
