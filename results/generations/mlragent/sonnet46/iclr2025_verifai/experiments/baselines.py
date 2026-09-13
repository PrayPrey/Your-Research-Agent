"""
Baseline methods for comparison with ExecGuide:
1. Standard greedy decoding (no verification guidance)
2. Post-hoc repair (generate then test-and-repair)
3. Execution-only steering (no SMT, only test case feedback)
4. SMT-only steering (no execution, only SMT feedback)
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Tuple, Dict, Optional
import time
import re


def generate_code_greedy(
    prompt: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    max_new_tokens: int = 256,
    temperature: float = 0.7,
    device: torch.device = None,
) -> str:
    """Standard greedy/sampling decoding - no verification guidance."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        if temperature > 0:
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                pad_token_id=tokenizer.eos_token_id,
            )
        else:
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

    input_len = inputs["input_ids"].shape[1]
    generated = outputs[0][input_len:]
    code = tokenizer.decode(generated, skip_special_tokens=True)
    return code


def generate_multiple_samples(
    prompt: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    num_samples: int = 5,
    max_new_tokens: int = 256,
    temperature: float = 0.8,
    device: torch.device = None,
) -> List[str]:
    """Generate multiple samples for pass@k evaluation."""
    samples = []
    for _ in range(num_samples):
        code = generate_code_greedy(prompt, model, tokenizer, max_new_tokens, temperature, device)
        samples.append(code)
    return samples


def post_hoc_repair(
    prompt: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problem_id: str,
    entry_point: str,
    test_cases: list,
    max_repair_rounds: int = 3,
    max_new_tokens: int = 256,
    device: torch.device = None,
) -> Tuple[str, int, float]:
    """
    Post-hoc repair baseline: generate, test, repair loop.
    Returns (final_code, num_repair_rounds, time_taken).
    """
    from spec_augment import run_test_cases

    start_time = time.time()

    # Initial generation
    code = generate_code_greedy(prompt, model, tokenizer, max_new_tokens, device=device)

    def extract_function(generated: str, func_name: str, original_prompt: str) -> str:
        """Extract complete function from generated code."""
        full_code = original_prompt + generated
        # Try to find the function definition
        lines = full_code.split('\n')
        in_func = False
        func_lines = []
        for line in lines:
            if f'def {func_name}(' in line:
                in_func = True
            if in_func:
                func_lines.append(line)
                # Stop at next top-level function (dedented def)
                if len(func_lines) > 1 and line and not line.startswith(' ') and not line.startswith('\t') and 'def ' in line:
                    func_lines = func_lines[:-1]
                    break
        return '\n'.join(func_lines) if func_lines else full_code

    best_code = extract_function(code, entry_point, prompt)
    pass_rate, _, _ = run_test_cases(best_code, problem_id, entry_point)

    rounds_used = 0
    for repair_round in range(max_repair_rounds):
        if pass_rate >= 1.0:
            break

        # Create repair prompt
        repair_prompt = (
            f"{prompt}\n"
            f"# Previous attempt:\n{code}\n\n"
            f"# The above code has issues. Please write a corrected version:\n"
        )
        code = generate_code_greedy(repair_prompt, model, tokenizer, max_new_tokens, device=device)
        repaired_code = extract_function(code, entry_point, repair_prompt)

        new_pass_rate, _, _ = run_test_cases(repaired_code, problem_id, entry_point)
        if new_pass_rate >= pass_rate:
            best_code = repaired_code
            pass_rate = new_pass_rate

        rounds_used = repair_round + 1

    elapsed = time.time() - start_time
    return best_code, rounds_used, elapsed


def execution_only_steering(
    prompt: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problem_id: str,
    entry_point: str,
    num_candidates: int = 4,
    max_new_tokens: int = 256,
    device: torch.device = None,
) -> Tuple[str, float]:
    """
    Execution-only steering: generate multiple candidates, select best by test pass rate.
    No SMT verification - pure execution-based selection.
    """
    from spec_augment import run_test_cases

    candidates = generate_multiple_samples(
        prompt, model, tokenizer,
        num_samples=num_candidates,
        max_new_tokens=max_new_tokens,
        device=device
    )

    best_code = candidates[0]
    best_pass_rate = 0.0

    for cand in candidates:
        full_code = prompt + cand
        pass_rate, _, _ = run_test_cases(full_code, problem_id, entry_point)
        if pass_rate > best_pass_rate:
            best_pass_rate = pass_rate
            best_code = full_code

    return best_code, best_pass_rate


def smt_only_steering(
    prompt: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problem_id: str,
    num_candidates: int = 4,
    max_new_tokens: int = 256,
    device: torch.device = None,
) -> Tuple[str, float]:
    """
    SMT-only steering: generate multiple candidates, select best by SMT consistency.
    No execution feedback.
    """
    from spec_augment import check_smt_consistency

    candidates = generate_multiple_samples(
        prompt, model, tokenizer,
        num_samples=num_candidates,
        max_new_tokens=max_new_tokens,
        device=device
    )

    best_code = candidates[0] if candidates else ""
    best_smt_score = 0.0

    for cand in candidates:
        full_code = prompt + cand
        smt_score = check_smt_consistency(full_code, problem_id)
        if smt_score > best_smt_score:
            best_smt_score = smt_score
            best_code = full_code

    return best_code, best_smt_score
