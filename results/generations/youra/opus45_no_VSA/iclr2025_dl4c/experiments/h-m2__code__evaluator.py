"""Evaluation loop for H-M2 DiD experiment."""
import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase

from config import Config
from feedback import execute_and_get_feedback, classify_error_type, build_tests, get_control_feedback


def single_shot(model: PreTrainedModel, tokenizer: PreTrainedTokenizerBase, prompt: str, cfg: Config) -> str:
    """Greedy generation."""
    device = next(model.parameters()).device
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            do_sample=False,
            max_new_tokens=cfg.max_new_tokens,
        )

    code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if code.startswith(prompt):
        code = code[len(prompt):].strip()
    return code


def build_feedback_bank(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    problems: dict,
    cfg: Config,
) -> dict[str, dict]:
    """Single-shot evaluate all problems, build feedback bank."""
    bank = {}
    for task_id, problem in problems.items():
        prompt = problem["prompt"]
        tests = build_tests(problem)
        code = single_shot(model, tokenizer, prompt, cfg)
        pass_rate, error_msg = execute_and_get_feedback(code, tests)
        error_type = classify_error_type(error_msg)
        bank[task_id] = {
            "code": code,
            "pass_rate": pass_rate,
            "error_msg": error_msg,
            "error_type": error_type,
        }
    return bank


def refine_with_feedback(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    prompt: str,
    code: str,
    feedback_msg: str,
    tests: list[str],
    cfg: Config,
) -> bool:
    """Single refinement step, returns whether refined code passes."""
    refine_prompt = (
        f"{prompt}\n"
        f"# Previous attempt:\n{code}\n"
        f"# Error:\n{feedback_msg}\n"
        f"# Fixed code:"
    )
    refined_code = single_shot(model, tokenizer, refine_prompt, cfg)
    pass_rate, _ = execute_and_get_feedback(refined_code, tests)
    return pass_rate == 1.0


def evaluate_condition(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    problems: dict,
    feedback_bank: dict[str, dict],
    condition: str,
    model_name: str,
    cfg: Config,
    seed: int,
) -> list[dict]:
    """Evaluate one (model, condition) cell across all problems."""
    results = []
    for task_id, problem in problems.items():
        cached = feedback_bank[task_id]
        single_shot_pass = cached["pass_rate"] == 1.0
        tests = build_tests(problem)

        if single_shot_pass:
            refined_pass = True
        else:
            if condition == "actual":
                fb = cached["error_msg"]
            else:
                fb = get_control_feedback(task_id, feedback_bank, seed)
            refined_pass = refine_with_feedback(
                model, tokenizer, problem["prompt"], cached["code"], fb, tests, cfg
            )

        results.append({
            "problem_id": task_id,
            "model": model_name,
            "condition": condition,
            "single_shot_pass": single_shot_pass,
            "refined_pass": refined_pass,
            "error_type": cached["error_type"],
        })
    return results


def run_all_conditions(
    models: dict[str, tuple],
    problems: dict,
    cfg: Config,
) -> list[dict]:
    """Run all 4 cells (RL/CE x actual/control) with feedback banks built per model."""
    all_results = []

    for model_name in cfg.model_names:
        model, tokenizer = models[model_name]
        print(f"Building feedback bank for {model_name}...")
        feedback_bank = build_feedback_bank(model, tokenizer, problems, cfg)

        for condition in cfg.conditions:
            for seed in cfg.seeds:
                print(f"Evaluating {model_name}/{condition}/seed={seed}...")
                results = evaluate_condition(
                    model, tokenizer, problems, feedback_bank, condition, model_name, cfg, seed
                )
                all_results.extend(results)

    return all_results
