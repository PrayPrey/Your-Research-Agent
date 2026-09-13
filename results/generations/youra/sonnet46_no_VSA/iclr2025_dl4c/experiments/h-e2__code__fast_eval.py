"""
Fast batch evaluation using HuggingFace model directly.
Generates all solutions in batches, then runs evalplus evaluation.
"""
import argparse
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


BENCHMARKS = {
    "humaneval": {"get_data": "get_human_eval_plus", "n_problems": 164},
    "mbpp": {"get_data": "get_mbpp_plus", "n_problems": 378},
}
CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
RESULTS_COLUMNS = ["condition", "seed", "benchmark", "pass1", "n_problems"]
MAX_NEW_TOKENS = 512
BATCH_SIZE = 8


def load_model(checkpoint_dir: str, device: str = "cuda:0"):
    print(f"Loading model from {checkpoint_dir}...")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"  # for batch generation

    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_dir,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    ).to(device)
    model.eval()
    return model, tokenizer


def generate_solutions(model, tokenizer, prompts: list, device: str = "cuda:0") -> list:
    """Generate solutions for a list of prompts in batches."""
    solutions = []
    for i in range(0, len(prompts), BATCH_SIZE):
        batch = prompts[i:i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}/{(len(prompts)+BATCH_SIZE-1)//BATCH_SIZE} ({len(batch)} prompts)...")

        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048 - MAX_NEW_TOKENS,
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                temperature=1.0,
                pad_token_id=tokenizer.eos_token_id,
            )

        # Decode only the generated part
        for j, output in enumerate(outputs):
            input_len = inputs["input_ids"][j].shape[0]
            generated = output[input_len:]
            solution = tokenizer.decode(generated, skip_special_tokens=True)
            solutions.append(solution)

    return solutions


def write_samples_jsonl(task_ids: list, solutions: list, output_path: str) -> None:
    """Write solutions in evalplus jsonl format."""
    with open(output_path, "w") as f:
        for task_id, solution in zip(task_ids, solutions):
            f.write(json.dumps({"task_id": task_id, "solution": solution}) + "\n")


def run_evalplus_evaluate(benchmark: str, samples_path: str) -> float:
    """Evaluate solutions directly using evalplus Python API. Returns pass@1."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from evalplus.evaluate import check_correctness, get_groundtruth

    if benchmark == "humaneval":
        from evalplus.data import get_human_eval_plus, get_human_eval_plus_hash
        data = get_human_eval_plus()
        expected = get_groundtruth(data, get_human_eval_plus_hash(), [])
    else:
        from evalplus.data import get_mbpp_plus, get_mbpp_plus_hash
        data = get_mbpp_plus()
        expected = get_groundtruth(data, get_mbpp_plus_hash(), [])

    # Load solutions
    solutions = {}
    with open(samples_path) as f:
        for line in f:
            row = json.loads(line)
            solutions[row["task_id"]] = row["solution"]

    # Evaluate
    n_correct = 0
    n_total = 0
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {}
        for task_id, problem in data.items():
            if task_id not in solutions:
                continue
            solution = solutions[task_id]
            full_solution = problem["prompt"] + solution
            fut = executor.submit(
                check_correctness,
                dataset=benchmark,
                completion_id=n_total,
                problem=problem,
                solution=full_solution,
                expected_output=expected.get(task_id, {}),
                base_only=True,
                fast_check=True,
            )
            futures[fut] = task_id
            n_total += 1

        for fut in as_completed(futures):
            task_id = futures[fut]
            try:
                result = fut.result()
                # result keys: completion_id, task_id, solution, base, plus
                base = result.get("base")
                if base and isinstance(base, tuple) and len(base) == 2:
                    status, passes = base
                    if status == "pass" and passes and passes[0]:
                        n_correct += 1
            except Exception:
                pass

    pass1 = n_correct / n_total if n_total > 0 else 0.0
    print(f"  Direct eval: {n_correct}/{n_total} correct = pass@1={pass1:.4f}")
    return pass1


def evaluate_checkpoint(
    condition: str,
    seed: int,
    benchmark: str,
    checkpoint_dir: str,
    results_csv: str,
    output_dir: str,
    device: str = "cuda:0",
) -> float:
    """Full pipeline for one (condition, seed, benchmark) triple."""
    print(f"\n=== Evaluating: {condition} seed={seed} on {benchmark} ===")

    # Check if already in CSV
    csv_path = Path(results_csv)
    if csv_path.exists():
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                if (row["condition"] == condition and int(row["seed"]) == seed
                        and row["benchmark"] == benchmark and float(row["pass1"]) >= 0):
                    print(f"  Already evaluated: pass@1={row['pass1']}")
                    return float(row["pass1"])

    # Check if samples already generated
    out_dir = Path(output_dir) / f"{condition}_seed{seed}_{benchmark}"
    out_dir.mkdir(parents=True, exist_ok=True)
    samples_path = str(out_dir / "samples.jsonl")

    if not Path(samples_path).exists():
        # Load data
        if benchmark == "humaneval":
            from evalplus.data import get_human_eval_plus
            data = get_human_eval_plus()
        else:
            from evalplus.data import get_mbpp_plus
            data = get_mbpp_plus()

        task_ids = list(data.keys())
        prompts = [data[tid]["prompt"] for tid in task_ids]

        # Generate
        model, tokenizer = load_model(checkpoint_dir, device)
        solutions = generate_solutions(model, tokenizer, prompts, device)
        del model  # free GPU memory
        torch.cuda.empty_cache()

        write_samples_jsonl(task_ids, solutions, samples_path)
        print(f"  Generated {len(solutions)} solutions -> {samples_path}")
    else:
        print(f"  Using existing samples: {samples_path}")

    # Evaluate
    pass1 = run_evalplus_evaluate(benchmark, samples_path)

    # Write to CSV
    n = BENCHMARKS[benchmark]["n_problems"]
    write_header = not csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULTS_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "condition": condition,
            "seed": seed,
            "benchmark": benchmark,
            "pass1": pass1,
            "n_problems": n,
        })

    print(f"  Result: pass@1={pass1:.4f}")
    return pass1


def main():
    parser = argparse.ArgumentParser(description="Fast batch evaluation")
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--benchmark", choices=list(BENCHMARKS.keys()), required=True)
    parser.add_argument("--checkpoint_dir", required=True)
    parser.add_argument("--results_csv", default="../results/all_results.csv")
    parser.add_argument("--output_dir", default="../results/fast_eval")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    evaluate_checkpoint(
        condition=args.condition,
        seed=args.seed,
        benchmark=args.benchmark,
        checkpoint_dir=args.checkpoint_dir,
        results_csv=args.results_csv,
        output_dir=args.output_dir,
        device=args.device,
    )


if __name__ == "__main__":
    main()
