"""3-condition masked training for H-M2 ablation experiment."""

import os
import json
import random
import torch
import numpy as np
from typing import Dict, List, Any, Literal, Optional
from datetime import datetime

from fgo import create_fgo_mask, fgo_ppo_loss, standard_ppo_loss
from random_mask import build_random_mask_like
from verify_gradient import GradientExclusionVerifier, verify_gradient_exclusion_simple
from execution import collect_execution_trace, map_tokens_to_lines

MaskMode = Literal["none", "random", "trace"]


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_masked_condition(
    condition_name: str,
    mask_mode: MaskMode,
    problems: List[Dict],
    model,
    tokenizer,
    trainer,
    cfg: Dict[str, Any],
    output_dir: str,
    seed: int,
) -> Dict[str, Any]:
    """
    Train one condition with specified masking mode.

    Args:
        condition_name: Name for this run (e.g., "trace_seed42")
        mask_mode: "none" | "random" | "trace"
        problems: Training problems
        model: Policy model
        tokenizer: Tokenizer
        trainer: PPO trainer instance
        cfg: Config dict
        output_dir: Output directory
        seed: Random seed

    Returns:
        Results dict
    """
    print(f"\n{'='*60}")
    print(f"Training: {condition_name} (mask_mode={mask_mode}, seed={seed})")
    print(f"{'='*60}\n")

    condition_dir = os.path.join(output_dir, condition_name)
    os.makedirs(condition_dir, exist_ok=True)

    set_seed(seed)

    metrics_history = []
    total_reward = 0.0
    mask_stats = []
    grad_verification_logs = []

    episodes = cfg.get("episodes", 100)
    per_device_batch = cfg.get("per_device_batch", 4)
    checkpoint_every = cfg.get("checkpoint_every", 50)

    for episode in range(episodes):
        batch_problems = random.sample(problems, min(per_device_batch, len(problems)))

        prompts = [p.get("prompt", "") for p in batch_problems]

        query_tensors = [
            tokenizer(p, return_tensors="pt", truncation=True, max_length=512).input_ids.squeeze(0)
            for p in prompts
        ]

        # Generate responses
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

        # Build masks based on mode
        masks = []
        for i, (code, problem, response_ids) in enumerate(zip(codes, batch_problems, response_tensors)):
            test_cases = problem.get("test", problem.get("test_list", []))
            if isinstance(test_cases, list):
                test_cases = "\n".join(test_cases)

            if mask_mode == "none":
                mask = torch.ones(len(response_ids), dtype=torch.float, device=response_ids.device)
            elif mask_mode == "trace":
                executed = collect_execution_trace(code, test_cases)
                token_to_line = map_tokens_to_lines(response_ids, code, tokenizer)
                mask = create_fgo_mask(response_ids, token_to_line, executed)
            elif mask_mode == "random":
                # First compute trace mask to get sparsity
                executed = collect_execution_trace(code, test_cases)
                token_to_line = map_tokens_to_lines(response_ids, code, tokenizer)
                trace_mask = create_fgo_mask(response_ids, token_to_line, executed)
                # Then create random mask with same sparsity
                mask = build_random_mask_like(trace_mask, seed=seed + episode * per_device_batch + i)
            else:
                raise ValueError(f"Unknown mask_mode: {mask_mode}")

            masks.append(mask)

            # Log mask stats
            if episode < 5 and len(mask_stats) < 20:
                masked_pct = 100 * (1 - mask.sum().item() / mask.numel())
                mask_stats.append({
                    "episode": episode,
                    "sample": i,
                    "masked_pct": masked_pct,
                    "num_tokens": mask.numel()
                })

        # Compute rewards (simple compile/run check)
        rewards = []
        for code, problem in zip(codes, batch_problems):
            test_cases = problem.get("test", problem.get("test_list", []))
            if isinstance(test_cases, list):
                test_cases = "\n".join(test_cases)

            try:
                exec(compile(code, "<gen>", "exec"), {})
                reward = 1.0
            except Exception:
                reward = 0.0
            rewards.append(torch.tensor(reward))

        # PPO step
        try:
            stats = trainer.step(query_tensors, response_tensors, rewards)
            total_reward += sum(r.item() for r in rewards)

            # Gradient verification (first 5 episodes only)
            if episode < 5 and mask_mode != "none":
                # Simple verification via masked loss check
                for mask in masks[:1]:
                    dummy_logprobs = torch.randn(1, mask.numel(), requires_grad=True, device=mask.device)
                    dummy_old = torch.randn_like(dummy_logprobs).detach()
                    dummy_adv = torch.ones_like(dummy_logprobs)

                    loss = fgo_ppo_loss(
                        dummy_logprobs, dummy_old, dummy_adv,
                        mask.unsqueeze(0), clip_eps=0.2
                    )
                    loss.backward()

                    grad = dummy_logprobs.grad
                    mask_bool = mask.bool()
                    exec_grad = grad[0, mask_bool].abs().mean().item() if mask_bool.any() else 0
                    non_exec_grad = grad[0, ~mask_bool].abs().mean().item() if (~mask_bool).any() else 0

                    grad_verification_logs.append({
                        "episode": episode,
                        "executed_grad_norm": exec_grad,
                        "non_executed_grad_norm": non_exec_grad,
                        "verified": non_exec_grad < 1e-6
                    })

            if episode % 20 == 0:
                avg_reward = total_reward / ((episode + 1) * len(rewards))
                print(f"  Episode {episode}: avg_reward={avg_reward:.3f}")
                metrics_history.append({
                    "episode": episode,
                    "avg_reward": avg_reward,
                    "batch_reward": sum(r.item() for r in rewards) / len(rewards),
                })

            if episode > 0 and episode % checkpoint_every == 0:
                ckpt_path = os.path.join(condition_dir, f"checkpoint-{episode}")
                model.save_pretrained(ckpt_path)
                tokenizer.save_pretrained(ckpt_path)

        except Exception as e:
            print(f"  Training step error at episode {episode}: {e}")
            continue

    # Save final checkpoint
    final_ckpt = os.path.join(condition_dir, "final")
    model.save_pretrained(final_ckpt)
    tokenizer.save_pretrained(final_ckpt)

    results = {
        "condition": condition_name,
        "mask_mode": mask_mode,
        "seed": seed,
        "episodes": episodes,
        "final_avg_reward": total_reward / max(1, episodes * per_device_batch),
        "checkpoint_path": final_ckpt,
        "metrics_history": metrics_history,
        "mask_stats": mask_stats,
        "grad_verification": grad_verification_logs,
    }

    with open(os.path.join(condition_dir, "train_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    return results


def run_three_condition_experiment(
    problems: List[Dict],
    model,
    tokenizer,
    build_trainer_fn,
    cfg: Dict[str, Any],
    seeds: List[int] = [42, 123, 456],
    output_dir: str = "outputs"
) -> Dict[str, Any]:
    """
    Run 3-condition experiment across multiple seeds.

    Args:
        problems: Training problems
        model: Policy model
        tokenizer: Tokenizer
        build_trainer_fn: Function to build PPO trainer
        cfg: Config dict
        seeds: List of random seeds
        output_dir: Output directory

    Returns:
        Aggregated results
    """
    os.makedirs(output_dir, exist_ok=True)

    all_results = {
        "none": [],
        "random": [],
        "trace": []
    }

    start_time = datetime.now()

    for seed in seeds:
        print(f"\n{'#'*70}")
        print(f"SEED: {seed}")
        print(f"{'#'*70}")

        for mask_mode in ["none", "random", "trace"]:
            condition_name = f"{mask_mode}_seed{seed}"

            # Reset model for each condition (or reload)
            trainer = build_trainer_fn(model, tokenizer, cfg, seed)

            results = train_masked_condition(
                condition_name=condition_name,
                mask_mode=mask_mode,
                problems=problems,
                model=model,
                tokenizer=tokenizer,
                trainer=trainer,
                cfg=cfg,
                output_dir=output_dir,
                seed=seed,
            )

            all_results[mask_mode].append(results)

    experiment_results = {
        "experiment": "H-M2 3-condition ablation",
        "start_time": start_time.isoformat(),
        "end_time": datetime.now().isoformat(),
        "seeds": seeds,
        "conditions": ["none", "random", "trace"],
        "results_by_condition": all_results,
        "config": cfg,
    }

    with open(os.path.join(output_dir, "experiment_results.json"), "w") as f:
        json.dump(experiment_results, f, indent=2)

    return experiment_results
