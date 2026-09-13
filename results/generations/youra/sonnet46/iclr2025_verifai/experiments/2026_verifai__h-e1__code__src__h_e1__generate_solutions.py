"""Solution generation for H-E1: model loading + k=5 solution generation."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from evalplus.data import get_human_eval_plus, get_mbpp_plus

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

GENERATION_CONFIG: dict = dict(
    temperature=0.8, top_p=0.95, max_new_tokens=512, do_sample=True
)
K: int = 5
SEED: int = 42


def load_all_problems() -> tuple[dict, dict]:
    """Load HumanEval+ and MBPP+ problem dicts.
    Returns: (problems_he, problems_mbpp)
      problems_he:   {task_id: problem_dict}  # 164 problems
      problems_mbpp: {task_id: problem_dict}  # 378 problems
    """
    problems_he = get_human_eval_plus()
    problems_mbpp = get_mbpp_plus()
    return problems_he, problems_mbpp


def partition_by_benchmark(
    problems_he: dict,
    problems_mbpp: dict,
) -> dict[str, str]:
    """Map each task_id to its benchmark name.
    Returns: {task_id: "humaneval" | "mbpp"}  # 542 entries total
    """
    benchmark_map: dict[str, str] = {}
    for task_id in problems_he:
        benchmark_map[task_id] = "humaneval"
    for task_id in problems_mbpp:
        benchmark_map[task_id] = "mbpp"
    return benchmark_map


def load_model_and_tokenizer(
    model_id: str,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load model in float16 with device_map='auto'.
    Returns: (model, tokenizer) ready for .generate()
    """
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer


def format_prompt(problem: dict, benchmark: str) -> str:
    """Format problem into a generation prompt string.
    benchmark: "humaneval" | "mbpp"
    Returns: prompt string (includes function signature + docstring)
    """
    prompt = problem.get("prompt", "")
    return prompt


def generate_k_solutions(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problem: dict,
    benchmark: str = "humaneval",
    k: int = K,
    seed: int = SEED,
) -> list[str]:
    """Generate k solutions for one problem via sampling.
    Returns: list[str] of length k — raw generated code strings
    """
    torch.manual_seed(seed)
    prompt = format_prompt(problem, benchmark)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            do_sample=True,
            temperature=GENERATION_CONFIG["temperature"],
            top_p=GENERATION_CONFIG["top_p"],
            max_new_tokens=GENERATION_CONFIG["max_new_tokens"],
            num_return_sequences=k,
            pad_token_id=tokenizer.eos_token_id,
        )
    solutions = [
        tokenizer.decode(o[input_len:], skip_special_tokens=True)
        for o in outputs
    ]
    return solutions


def generate_solutions(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problems: dict,
    benchmark_map: dict[str, str],
    k: int = K,
    seed: int = SEED,
) -> dict[str, list[str]]:
    """Generate k solutions for all problems in dict.
    Returns: {task_id: [str × k]}
    """
    result: dict[str, list[str]] = {}
    total = len(problems)
    for i, (task_id, problem) in enumerate(problems.items()):
        benchmark = benchmark_map.get(task_id, "humaneval")
        result[task_id] = generate_k_solutions(model, tokenizer, problem, benchmark, k, seed)
        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"  Progress: {i+1}/{total} problems generated", flush=True)
    return result


def save_solutions(solutions: dict, output_path: str) -> None:
    """Save solutions as JSONL. One JSON object per line.
    Format: {"task_id": str, "solutions": [str × k]}
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        for task_id, sols in solutions.items():
            f.write(json.dumps({"task_id": task_id, "solutions": sols}) + "\n")


def load_existing_solutions(path: str) -> Optional[dict]:
    """Load JSONL solutions file if it exists, else return None.
    Returns: {task_id: [str × k]} or None
    """
    if not os.path.exists(path):
        return None
    result = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                result[obj["task_id"]] = obj["solutions"]
    return result


def generate_solutions_for_model(
    model_id: str,
    problems: dict,
    benchmark_map: dict[str, str],
    output_path: str,
    k: int = K,
    seed: int = SEED,
) -> dict:
    """Generate solutions for one model with reuse check.
    Returns: {task_id: [str × k]}
    """
    existing = load_existing_solutions(output_path)
    if existing is not None:
        print(f"Reusing solutions from {output_path}")
        return existing
    model, tokenizer = load_model_and_tokenizer(model_id)
    solutions = generate_solutions(model, tokenizer, problems, benchmark_map, k, seed)
    save_solutions(solutions, output_path)
    return solutions


def main(args=None) -> None:
    """Entry point: generate k=5 solutions per model."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate k=5 solutions")
    parser.add_argument("--model_id", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="results")
    parser.add_argument("--smoke_test", action="store_true", help="Only use 5 problems")
    if args is None:
        args = parser.parse_args()

    problems_he, problems_mbpp = load_all_problems()
    problems_all = {**problems_he, **problems_mbpp}
    benchmark_map = partition_by_benchmark(problems_he, problems_mbpp)

    if args.smoke_test:
        problems_all = dict(list(problems_all.items())[:5])

    model_short = MODEL_SHORT_NAMES.get(args.model_id, args.model_id.split("/")[-1])
    output_path = os.path.join(args.output_dir, f"solutions_{model_short}.jsonl")

    solutions = generate_solutions_for_model(
        args.model_id, problems_all, benchmark_map, output_path
    )
    print(f"Generated solutions for {len(solutions)} problems -> {output_path}")


if __name__ == "__main__":
    main()
