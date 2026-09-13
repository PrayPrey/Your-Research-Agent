import os
import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import ExperimentConfig, get_config
from rewards import run_evalplus_tests
from ast_metric import compute_ast_semantic_edit_distance
from kl_metric import load_checkpoint_kl_log, match_checkpoints


_DEEPSEEK_CHAT_TEMPLATE = (
    "You are an AI programming assistant, utilizing the DeepSeek Coder model, "
    "developed by DeepSeek Company, and you only answer questions related to computer science. "
    "For politically sensitive questions, security and privacy issues, and other non-computer "
    "science questions, you will refuse to answer.\n"
    "### Instruction:\n{instruction}\n### Response:\n"
)


def generate_solutions(
    model_dir: str,
    problems: dict,
    cfg: ExperimentConfig,
    max_new_tokens: int = 512,
) -> dict:
    """Generate one solution per problem. Returns {task_id: completion}."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        torch_dtype=torch.bfloat16 if cfg.dtype == "bfloat16" else torch.float16,
        trust_remote_code=True,
        device_map="auto",
    )
    model.eval()

    solutions = {}
    with torch.no_grad():
        for task_id, problem in problems.items():
            prompt = _DEEPSEEK_CHAT_TEMPLATE.format(instruction=problem["prompt"])
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
            gen = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
            completion = tokenizer.decode(gen[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            solutions[task_id] = completion

    return solutions


def run_evalplus_evaluation(solutions: dict) -> dict:
    """Run EvalPlus tests for all solutions. Returns {task_id: {passed, error_type}}."""
    results = {}
    for task_id, completion in solutions.items():
        results[task_id] = run_evalplus_tests(task_id, completion)
    return results


def bootstrap_ci(
    values: list,
    n_samples: int = 10000,
    ci: float = 0.95,
    seed: int = 42,
) -> dict:
    """Bootstrap confidence interval for mean.
    Returns {mean, lower, upper, n}.
    """
    rng = np.random.default_rng(seed)
    arr = np.array(values, dtype=float)
    means = np.array([
        rng.choice(arr, size=len(arr), replace=True).mean()
        for _ in range(n_samples)
    ])
    alpha = (1 - ci) / 2
    return {
        "mean": float(arr.mean()),
        "lower": float(np.percentile(means, 100 * alpha)),
        "upper": float(np.percentile(means, 100 * (1 - alpha))),
        "n": len(arr),
    }


def compute_semantic_edit_per_kl(
    grpo_solutions: dict,
    dpo_solutions: dict,
    reference_solutions: dict,
    grpo_kl_log: list,
    dpo_kl_log: list,
    cfg: ExperimentConfig,
) -> dict:
    """Compute semantic-edit-per-KL for matched GRPO and DPO checkpoints.
    Returns {grpo_edit_per_kl: list, dpo_edit_per_kl: list, matched_pairs: list}
    """
    matched = match_checkpoints(grpo_kl_log, dpo_kl_log, tolerance=cfg.kl_tolerance)
    if not matched:
        return {"grpo_edit_per_kl": [], "dpo_edit_per_kl": [], "matched_pairs": []}

    # Compute AST edit distances
    task_ids = list(reference_solutions.keys())
    grpo_dists = []
    dpo_dists = []
    for task_id in task_ids:
        ref_code = reference_solutions.get(task_id, "")
        grpo_code = grpo_solutions.get(task_id, "")
        dpo_code = dpo_solutions.get(task_id, "")
        if ref_code and grpo_code:
            grpo_dists.append(compute_ast_semantic_edit_distance(ref_code, grpo_code))
        if ref_code and dpo_code:
            dpo_dists.append(compute_ast_semantic_edit_distance(ref_code, dpo_code))

    # Filter out inf values
    grpo_dists = [d for d in grpo_dists if d != float("inf")]
    dpo_dists = [d for d in dpo_dists if d != float("inf")]

    mean_grpo_edit = float(np.mean(grpo_dists)) if grpo_dists else float("nan")
    mean_dpo_edit = float(np.mean(dpo_dists)) if dpo_dists else float("nan")

    # Per-matched-pair edit/kl
    grpo_per_kl = []
    dpo_per_kl = []
    for pair in matched:
        if pair["kl_grpo"] > 0 and mean_grpo_edit == mean_grpo_edit:
            grpo_per_kl.append(mean_grpo_edit / pair["kl_grpo"])
        if pair["kl_dpo"] > 0 and mean_dpo_edit == mean_dpo_edit:
            dpo_per_kl.append(mean_dpo_edit / pair["kl_dpo"])

    return {
        "grpo_edit_per_kl": grpo_per_kl,
        "dpo_edit_per_kl": dpo_per_kl,
        "matched_pairs": matched,
        "mean_grpo_edit": mean_grpo_edit,
        "mean_dpo_edit": mean_dpo_edit,
    }


def run_full_evaluation(
    grpo_checkpoint: str,
    dpo_checkpoint: str,
    cfg: ExperimentConfig = None,
    output_path: str = None,
) -> dict:
    """Full evaluation pipeline. Returns results dict."""
    if cfg is None:
        cfg = get_config()
    if output_path is None:
        output_path = os.path.join(cfg.output_dir, "eval_results.json")

    from data import load_humaneval_plus
    problems = load_humaneval_plus()

    # Reference solutions are canonical solutions from evalplus
    reference_solutions = {
        task_id: problem.get("canonical_solution", "")
        for task_id, problem in problems.items()
    }

    print("Generating GRPO solutions...")
    grpo_solutions = generate_solutions(grpo_checkpoint, problems, cfg)

    print("Generating DPO solutions...")
    dpo_solutions = generate_solutions(dpo_checkpoint, problems, cfg)

    print("Running EvalPlus evaluation...")
    grpo_eval = run_evalplus_evaluation(grpo_solutions)
    dpo_eval = run_evalplus_evaluation(dpo_solutions)

    grpo_pass_rate = sum(1 for r in grpo_eval.values() if r["passed"]) / len(grpo_eval)
    dpo_pass_rate = sum(1 for r in dpo_eval.values() if r["passed"]) / len(dpo_eval)

    print(f"GRPO pass@1: {grpo_pass_rate:.3f}, DPO pass@1: {dpo_pass_rate:.3f}")

    grpo_kl_log = load_checkpoint_kl_log(grpo_checkpoint)
    dpo_kl_log = load_checkpoint_kl_log(dpo_checkpoint)

    metric_data = compute_semantic_edit_per_kl(
        grpo_solutions, dpo_solutions, reference_solutions,
        grpo_kl_log, dpo_kl_log, cfg,
    )

    grpo_per_kl = metric_data["grpo_edit_per_kl"]
    dpo_per_kl = metric_data["dpo_edit_per_kl"]

    differential = [g - d for g, d in zip(grpo_per_kl, dpo_per_kl)]

    if differential:
        ci_result = bootstrap_ci(differential, n_samples=cfg.bootstrap_samples, ci=cfg.bootstrap_ci)
    else:
        ci_result = {"mean": float("nan"), "lower": float("nan"), "upper": float("nan"), "n": 0}

    gate_satisfied = (
        ci_result["lower"] > 0
        and abs(ci_result["mean"]) >= cfg.gate_magnitude
        and ci_result["n"] > 0
    )

    results = {
        "grpo_pass_rate": grpo_pass_rate,
        "dpo_pass_rate": dpo_pass_rate,
        "grpo_edit_per_kl": grpo_per_kl,
        "dpo_edit_per_kl": dpo_per_kl,
        "differential": differential,
        "bootstrap_ci": ci_result,
        "gate_satisfied": gate_satisfied,
        "metric_data": metric_data,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Evaluation results saved to {output_path}")
    print(f"Gate satisfied: {gate_satisfied} | CI: [{ci_result['lower']:.4f}, {ci_result['upper']:.4f}] | mean: {ci_result['mean']:.4f}")

    return results
