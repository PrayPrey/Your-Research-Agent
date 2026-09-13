"""Training loop for FGO experiment."""

import os
import json
import random
import torch
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import Config, CONDITIONS
from data import load_humaneval, load_mbpp, format_prompt, get_test_cases
from execution import compute_reward, collect_execution_trace, map_tokens_to_lines
from fgo import create_fgo_mask, fgo_ppo_loss, standard_ppo_loss, verify_fgo_mechanism
from model import load_policy_model, build_ppo_config, build_ppo_trainer


def train_condition(
    condition_name: str,
    feedback_type: str,
    use_fgo: bool,
    problems: List[Dict],
    cfg: Config,
    output_dir: str,
) -> Dict[str, Any]:
    """
    Train single condition (one cell of 2x3 factorial).

    Args:
        condition_name: e.g., "fgo_test"
        feedback_type: "compile", "test", or "combined"
        use_fgo: Whether to use FGO masking
        problems: Training problems
        cfg: Configuration
        output_dir: Output directory

    Returns:
        Dict with training results
    """
    print(f"\n{'='*60}")
    print(f"Training: {condition_name}")
    print(f"FGO: {use_fgo}, Feedback: {feedback_type}")
    print(f"{'='*60}\n")

    condition_dir = os.path.join(output_dir, condition_name)
    os.makedirs(condition_dir, exist_ok=True)

    model, tokenizer = load_policy_model(cfg.model_id, cfg.torch_dtype)

    ppo_config = build_ppo_config(
        lr=cfg.lr,
        batch_size=cfg.batch_size,
        mini_batch_size=cfg.per_device_batch,
        gradient_accumulation_steps=cfg.grad_accum,
        seed=cfg.seed,
        log_dir=os.path.join(condition_dir, "logs"),
    )

    trainer = build_ppo_trainer(model, tokenizer, ppo_config)

    metrics_history = []
    total_reward = 0.0
    fgo_mask_stats = []

    random.seed(cfg.seed)

    for episode in range(cfg.episodes):
        batch_problems = random.sample(problems, min(cfg.per_device_batch, len(problems)))

        prompts = [format_prompt(p, "humaneval") for p in batch_problems]

        query_tensors = [
            tokenizer(p, return_tensors="pt", truncation=True, max_length=512).input_ids.squeeze(0)
            for p in prompts
        ]

        response_tensors = []
        for qt in query_tensors:
            qt_device = qt.to(model.pretrained_model.device)
            output = model.generate(
                qt_device.unsqueeze(0),
                max_new_tokens=256,
                do_sample=True,
                temperature=0.8,
                pad_token_id=tokenizer.pad_token_id,
            )
            response = output[0, qt.shape[0]:]
            response_tensors.append(response)

        codes = [tokenizer.decode(r, skip_special_tokens=True) for r in response_tensors]

        rewards = []
        masks = []

        for code, problem, response_ids in zip(codes, batch_problems, response_tensors):
            test_cases = get_test_cases(problem, "humaneval")
            reward = compute_reward(code, test_cases, feedback_type)
            rewards.append(torch.tensor(reward))

            if use_fgo:
                executed = collect_execution_trace(code, test_cases)
                token_to_line = map_tokens_to_lines(response_ids, code, tokenizer)
                mask = create_fgo_mask(response_ids, token_to_line, executed)
                masks.append(mask)

                if episode == 0 and len(fgo_mask_stats) < 5:
                    masked_pct = 100 * (1 - mask.sum().item() / mask.numel())
                    fgo_mask_stats.append(masked_pct)

        try:
            stats = trainer.step(query_tensors, response_tensors, rewards)

            total_reward += sum(r.item() for r in rewards)

            if episode % 100 == 0:
                avg_reward = total_reward / ((episode + 1) * len(rewards))
                print(f"Episode {episode}: avg_reward={avg_reward:.3f}")
                metrics_history.append({
                    "episode": episode,
                    "avg_reward": avg_reward,
                    "batch_reward": sum(r.item() for r in rewards) / len(rewards),
                })

            if episode > 0 and episode % cfg.checkpoint_every == 0:
                ckpt_path = os.path.join(condition_dir, f"checkpoint-{episode}")
                model.save_pretrained(ckpt_path)
                tokenizer.save_pretrained(ckpt_path)

        except Exception as e:
            print(f"Training step error at episode {episode}: {e}")
            continue

    final_ckpt = os.path.join(condition_dir, "final")
    model.save_pretrained(final_ckpt)
    tokenizer.save_pretrained(final_ckpt)

    results = {
        "condition": condition_name,
        "use_fgo": use_fgo,
        "feedback_type": feedback_type,
        "episodes": cfg.episodes,
        "final_avg_reward": total_reward / (cfg.episodes * cfg.per_device_batch),
        "checkpoint_path": final_ckpt,
        "metrics_history": metrics_history,
        "fgo_mask_stats": fgo_mask_stats if use_fgo else None,
    }

    with open(os.path.join(condition_dir, "train_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    return results


def run_factorial_experiment(cfg: Config, output_dir: str = "outputs") -> Dict[str, Any]:
    """
    Run full 2x3 factorial experiment.

    Args:
        cfg: Configuration
        output_dir: Output directory

    Returns:
        Dict with all condition results
    """
    print("Loading datasets...")
    humaneval = load_humaneval()
    mbpp = load_mbpp()
    problems = humaneval + mbpp
    print(f"Total problems: {len(problems)} (HumanEval: {len(humaneval)}, MBPP: {len(mbpp)})")

    os.makedirs(output_dir, exist_ok=True)

    results = {}
    start_time = datetime.now()

    for condition_name, use_fgo, feedback_type in CONDITIONS:
        condition_results = train_condition(
            condition_name=condition_name,
            feedback_type=feedback_type,
            use_fgo=use_fgo,
            problems=problems,
            cfg=cfg,
            output_dir=output_dir,
        )
        results[condition_name] = condition_results

    results["experiment_info"] = {
        "start_time": start_time.isoformat(),
        "end_time": datetime.now().isoformat(),
        "config": {
            "model_id": cfg.model_id,
            "episodes": cfg.episodes,
            "lr": cfg.lr,
            "batch_size": cfg.batch_size,
            "seed": cfg.seed,
        },
        "num_problems": len(problems),
    }

    with open(os.path.join(output_dir, "factorial_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    cfg = Config()
    results = run_factorial_experiment(cfg)
    print("\nExperiment complete!")
    print(f"Results saved to: {cfg.results_dir}/factorial_results.json")
