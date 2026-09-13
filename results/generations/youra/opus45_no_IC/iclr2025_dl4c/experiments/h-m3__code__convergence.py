"""Convergence measurement for H-M3: Compare FGO vs Standard PPO learning efficiency."""

import torch
import random
import numpy as np
from typing import List, Dict, Set, Any, Optional
from collections import defaultdict

from fgo import create_fgo_mask, fgo_ppo_loss, standard_ppo_loss
from trace_collector import ExecutionTraceCollector
from token_mapper import LineToTokenMapper
from execution import compute_reward


def _build_token_to_line_list(
    line_map: Dict[int, int],
    seq_len: int
) -> List[int]:
    """Convert Dict[token_idx, line_num] to List[int] for create_fgo_mask."""
    result = [0] * seq_len
    for tok_idx, line_num in line_map.items():
        if tok_idx < seq_len:
            result[tok_idx] = line_num
    return result


def measure_convergence_efficiency(
    model,
    tokenizer,
    train_problems: List[Dict],
    eval_problems: List[Dict],
    fgo_enabled: bool,
    max_steps: int = 500,
    eval_interval: int = 50,
    target_pass1: float = 0.3,
    seed: int = 42,
    device: str = "cuda",
) -> Dict[str, Any]:
    """
    Measure convergence efficiency by tracking pass@1 over training steps.

    Returns:
        {steps_to_target, final_pass1, learning_curve, loss_curve}
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    trace_collector = ExecutionTraceCollector()
    token_mapper = LineToTokenMapper(tokenizer)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=1e-5,
        weight_decay=0.01
    )

    learning_curve = []
    loss_curve = []
    steps_to_target = None

    model.train()

    for step in range(max_steps):
        problem = random.choice(train_problems)
        prompt = problem["prompt"]
        test_code = problem.get("test", "")

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=128,
                do_sample=True,
                temperature=0.8,
                pad_token_id=tokenizer.pad_token_id,
            )

        response_ids = outputs[0, inputs["input_ids"].shape[1]:]
        generated_code = tokenizer.decode(response_ids, skip_special_tokens=True)
        full_code = prompt + generated_code

        reward = compute_reward(full_code, test_code, "test")

        response_inputs = tokenizer(generated_code, return_tensors="pt", return_offsets_mapping=True)
        response_inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in response_inputs.items()}

        model_outputs = model(response_inputs["input_ids"], labels=response_inputs["input_ids"])
        logprobs = -model_outputs.loss.unsqueeze(0).unsqueeze(0)  # Simplified: use neg loss as proxy
        old_logprobs = logprobs.detach()

        seq_len = response_inputs["input_ids"].shape[1]
        advantages = torch.full((1, seq_len), reward, device=device)

        if fgo_enabled:
            executed_lines = trace_collector.collect_trace(full_code, test_code)
            line_map = token_mapper.map_offsets_to_lines(generated_code, response_inputs.get("offset_mapping", [[]])[0].tolist())
            token_to_line = _build_token_to_line_list(line_map, seq_len)
            mask = create_fgo_mask(response_inputs["input_ids"][0], token_to_line, executed_lines)
            mask = mask.unsqueeze(0)
            loss = fgo_ppo_loss(logprobs.expand(1, seq_len), old_logprobs.expand(1, seq_len), advantages, mask)
        else:
            loss = standard_ppo_loss(logprobs.expand(1, seq_len), old_logprobs.expand(1, seq_len), advantages)

        optimizer.zero_grad()
        if loss.requires_grad:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        loss_curve.append((step, loss.item() if hasattr(loss, 'item') else float(loss)))

        if step % eval_interval == 0:
            pass1 = evaluate_pass1_quick(model, tokenizer, eval_problems[:50], device)
            learning_curve.append((step, pass1))
            print(f"[{'FGO' if fgo_enabled else 'STD'}] Step {step}: pass@1={pass1:.3f}")

            if steps_to_target is None and pass1 >= target_pass1:
                steps_to_target = step

    final_pass1 = learning_curve[-1][1] if learning_curve else 0.0

    return {
        "steps_to_target": steps_to_target if steps_to_target is not None else max_steps,
        "final_pass1": final_pass1,
        "learning_curve": learning_curve,
        "loss_curve": loss_curve,
        "condition": "fgo" if fgo_enabled else "standard",
        "seed": seed,
    }


def evaluate_pass1_quick(
    model,
    tokenizer,
    problems: List[Dict],
    device: str = "cuda"
) -> float:
    """Quick pass@1 evaluation on a subset of problems."""
    model.eval()
    correct = 0
    total = len(problems)

    with torch.no_grad():
        for problem in problems:
            prompt = problem["prompt"]
            test_code = problem.get("test", "")

            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(device) for k, v in inputs.items()}

            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,  # Greedy for eval
                pad_token_id=tokenizer.pad_token_id,
            )

            response = outputs[0, inputs["input_ids"].shape[1]:]
            generated = tokenizer.decode(response, skip_special_tokens=True)
            full_code = prompt + generated

            reward = compute_reward(full_code, test_code, "test")
            if reward == 1.0:
                correct += 1

    model.train()
    return correct / total if total > 0 else 0.0
