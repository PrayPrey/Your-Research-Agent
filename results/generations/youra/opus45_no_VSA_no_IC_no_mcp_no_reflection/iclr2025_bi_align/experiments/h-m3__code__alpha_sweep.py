"""Alpha sweep orchestration for H-M3."""
import dataclasses
import json
from pathlib import Path
from typing import Optional

from config import ExperimentConfig, RewardConfig, ALPHA_SWEEP_CONFIGS
from train_ppo import run_training
from evaluate import run_checkpoint_eval, check_gate_metrics
from alpaca_eval import evaluate_alpaca_eval


def run_sweep(
    configs: dict[str, RewardConfig],
    base_cfg: ExperimentConfig,
    output_dir: str,
    alpaca_num_prompts: Optional[int] = 100,
) -> dict:
    """Run training + evaluation for each alpha/beta config."""
    results = {}
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for name, reward_cfg in configs.items():
        print(f"\n{'='*60}")
        print(f"Running config: {name} (alpha={reward_cfg.alpha}, beta={reward_cfg.beta})")
        print(f"{'='*60}")

        cfg = dataclasses.replace(base_cfg, reward=reward_cfg)
        run_out_dir = out_path / name

        try:
            history, ifeval_test = run_training(cfg, run_out_dir)
            final_ckpt = run_out_dir / "checkpoints" / f"step_{cfg.ppo.total_steps}"

            alpaca_lc = evaluate_alpaca_eval(
                str(final_ckpt),
                str(run_out_dir / "alpaca_eval"),
                alpaca_num_prompts,
            )

            ifeval_result = run_checkpoint_eval(str(final_ckpt), ifeval_test)
            gate = check_gate_metrics(history)

            results[name] = {
                "alpaca_lc": alpaca_lc,
                "ifeval_acc": ifeval_result["ifeval_acc"],
                "gate": gate,
                "history": history,
                "alpha": reward_cfg.alpha,
                "beta": reward_cfg.beta,
            }

            print(f"  AlpacaEval LC: {alpaca_lc:.4f}")
            print(f"  IFEval Acc: {ifeval_result['ifeval_acc']:.4f}")
            print(f"  Gate: {'PASS' if gate['pass'] else 'FAIL'}")

        except Exception as e:
            print(f"  ERROR: {e}")
            results[name] = {
                "alpaca_lc": 0.0,
                "ifeval_acc": 0.0,
                "gate": {"pass": False, "reason": str(e)},
                "history": [],
                "alpha": reward_cfg.alpha,
                "beta": reward_cfg.beta,
                "error": str(e),
            }

    return results


def verify_gate(results: dict) -> bool:
    """FR-5: best(T1..T4) >= 0.95 * B2."""
    if "B2" not in results:
        print("ERROR: B2 baseline not found")
        return False

    b2_lc = results["B2"]["alpaca_lc"]
    t_scores = {k: v["alpaca_lc"] for k, v in results.items() if k != "B2"}

    if not t_scores:
        print("ERROR: No T* configurations found")
        return False

    best_name = max(t_scores, key=t_scores.get)
    best_score = t_scores[best_name]
    threshold = 0.95 * b2_lc
    passed = best_score >= threshold

    print(f"\n{'='*60}")
    print(f"Gate Verification (H-M3)")
    print(f"{'='*60}")
    print(f"  B2 Baseline: {b2_lc:.4f}")
    print(f"  Best T*: {best_name} = {best_score:.4f}")
    print(f"  Threshold (0.95 * B2): {threshold:.4f}")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    print(f"{'='*60}")

    return passed


def save_results(results: dict, output_path: str) -> None:
    """Save results to JSON, excluding non-serializable history."""
    serializable = {}
    for name, data in results.items():
        serializable[name] = {k: v for k, v in data.items() if k != "history"}

    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default="outputs")
    parser.add_argument("--alpaca_prompts", type=int, default=100)
    parser.add_argument("--ppo_steps", type=int, default=100)
    args = parser.parse_args()

    from config import PPOConfig

    base_cfg = ExperimentConfig()
    base_cfg.ppo.total_steps = args.ppo_steps

    results = run_sweep(
        ALPHA_SWEEP_CONFIGS,
        base_cfg,
        args.output_dir,
        args.alpaca_prompts,
    )

    gate_passed = verify_gate(results)
    save_results(results, f"{args.output_dir}/experiment_results.json")

    print(f"\nFinal Gate: {'PASS' if gate_passed else 'FAIL'}")
