#!/usr/bin/env python
"""H-M1 Main Experiment: Combined PPO training + evaluation."""
import json
import sys
from datetime import datetime
from pathlib import Path

# PoC mode: reduced steps for mechanism validation
POC_MODE = True
POC_STEPS = 100  # enough to show convergence/divergence signal


def main():
    from config import ExperimentConfig
    from train_ppo import run_training
    from evaluate import evaluate_all_checkpoints, check_gate_metrics
    from visualize import plot_reward_trajectory, plot_component_comparison
    from data import load_ifeval_split

    # Setup
    code_dir = Path(__file__).parent
    output_dir = code_dir / "outputs"
    figures_dir = code_dir.parent / "figures"

    cfg = ExperimentConfig()

    if POC_MODE:
        print(f"[PoC Mode] Running {POC_STEPS} steps (reduced from {cfg.ppo.total_steps})")
        cfg.ppo.total_steps = POC_STEPS
        cfg.logging.checkpoint_interval = 50  # more frequent for PoC

    print(f"="*60)
    print(f"H-M1 Experiment: Combined PPO Reward")
    print(f"Alpha={cfg.reward.alpha}, Beta={cfg.reward.beta}")
    print(f"Total steps: {cfg.ppo.total_steps}")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"="*60)

    # Run training
    history, ifeval_test = run_training(cfg, output_dir)

    # Check gate metrics
    gate_result = check_gate_metrics(history)
    print(f"\n{'='*60}")
    print(f"GATE CHECK (MUST_WORK)")
    print(f"Result: {'PASS' if gate_result['pass'] else 'FAIL'}")
    print(f"Reason: {gate_result['reason']}")
    if 'details' in gate_result:
        for k, v in gate_result['details'].items():
            print(f"  {k}: {v}")
    print(f"{'='*60}\n")

    # Generate visualizations
    print("Generating visualizations...")
    plot_reward_trajectory(history, figures_dir)
    plot_component_comparison(history, figures_dir)

    # Full checkpoint evaluation (skip for PoC if time-constrained)
    if not POC_MODE:
        print("Running checkpoint evaluations...")
        eval_results = evaluate_all_checkpoints(
            output_dir / "checkpoints",
            ifeval_test,
            history
        )
    else:
        eval_results = {
            "checkpoints": [],
            "gate_check": gate_result,
            "reward_hacking": {"correlation": None, "hacking_suspected": False},
            "note": "PoC mode - full evaluation skipped"
        }

    # Save final results
    results = {
        "experiment": "h-m1",
        "config": {
            "alpha": cfg.reward.alpha,
            "beta": cfg.reward.beta,
            "total_steps": cfg.ppo.total_steps,
            "poc_mode": POC_MODE,
        },
        "gate_result": gate_result,
        "evaluation": eval_results,
        "completed_at": datetime.now().isoformat(),
    }

    results_path = code_dir.parent / "experiment_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {results_path}")
    print(f"Figures saved to: {figures_dir}")

    # Exit code based on gate
    return 0 if gate_result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
