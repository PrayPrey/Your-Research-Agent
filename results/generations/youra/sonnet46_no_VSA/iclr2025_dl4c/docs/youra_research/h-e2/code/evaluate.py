"""
H-E2: EvalPlus Evaluation Runner
Runs evalplus.evaluate per (condition, seed, benchmark), parses pass@1, writes CSV.
"""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

BENCHMARKS = ["humaneval", "mbpp"]
CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS = [42, 123, 777]
RESULTS_COLUMNS = ["condition", "seed", "benchmark", "pass1", "n_problems"]


def run_evalplus(checkpoint_dir: str, benchmark: str, output_dir: str) -> dict:
    """Run evalplus 0.3.1 two-step: codegen -> evaluate. Returns dict with stdout and samples path."""
    root = Path(output_dir) / f"{Path(checkpoint_dir).name}_{benchmark}"
    root.mkdir(parents=True, exist_ok=True)

    # Step 1: codegen (single GPU via CUDA_VISIBLE_DEVICES=0)
    env = {**__import__("os").environ, "CUDA_VISIBLE_DEVICES": "0"}
    codegen_cmd = [
        sys.executable, "-m", "evalplus.codegen",
        checkpoint_dir,
        benchmark,
        "--backend", "hf",
        "--root", str(root),
        "--greedy", "True",
        "--trust_remote_code", "True",
        "--dtype", "bfloat16",
    ]
    print(f"  Codegen: {' '.join(codegen_cmd)}")
    r1 = subprocess.run(codegen_cmd, capture_output=True, text=True, env=env)
    if r1.returncode != 0:
        print(f"[ERROR] codegen failed:\n{r1.stderr[-1000:]}")

    # Locate generated samples jsonl (evalplus stores in root/{benchmark}/*.jsonl)
    samples_files = list(root.rglob("*.jsonl"))
    # Prefer non-raw files
    non_raw = [f for f in samples_files if "raw" not in f.name]
    samples_path = str(non_raw[0]) if non_raw else (str(samples_files[0]) if samples_files else str(root / "samples.jsonl"))

    # Step 2: evaluate
    eval_cmd = [
        sys.executable, "-m", "evalplus.evaluate",
        benchmark,
        "--samples", samples_path,
    ]
    print(f"  Evaluate: {' '.join(eval_cmd)}")
    r2 = subprocess.run(eval_cmd, capture_output=True, text=True)
    combined_stdout = r1.stdout + r2.stdout
    combined_stderr = r1.stderr + r2.stderr

    # Evalplus writes scores to a _results.json beside the samples file
    results_json = samples_path.replace(".jsonl", "_results.json")
    return {"stdout": combined_stdout, "stderr": combined_stderr, "output_path": results_json, "samples_path": samples_path}


def parse_evalplus_output(output_path: str, stdout: str) -> float:
    """Extract pass@1 from JSON output file or stdout."""
    # Try JSON file first
    p = Path(output_path)
    if p.exists():
        with open(p) as f:
            data = json.load(f)
        # EvalPlus JSON: {"pass@1": 0.234, ...} or nested
        if "pass@1" in data:
            return float(data["pass@1"])
        for key in ("pass_at_1", "pass_at1"):
            if key in data:
                return float(data[key])
    # Fallback: parse stdout
    for line in stdout.split("\n"):
        lower = line.lower()
        if "pass@1" in lower or "pass_at_1" in lower:
            for part in line.split():
                try:
                    v = float(part.strip(",:"))
                    if 0.0 <= v <= 1.0:
                        return v
                except ValueError:
                    pass
    print(f"[WARN] Could not parse pass@1 from {output_path}")
    return -1.0


def collect_result(
    condition: str,
    seed: int,
    benchmark: str,
    pass1: float,
    n_problems: int,
    results_csv: str,
) -> None:
    """Append one row to results CSV (create with header if absent)."""
    csv_path = Path(results_csv)
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
            "n_problems": n_problems,
        })
    print(f"  Wrote result: condition={condition} seed={seed} benchmark={benchmark} pass@1={pass1:.4f}")


def evaluate_checkpoint(
    condition: str,
    seed: int,
    benchmark: str,
    checkpoint_dir: str,
    results_csv: str,
    evalplus_output_dir: str,
) -> float:
    """Full pipeline for one (condition, seed, benchmark) triple."""
    print(f"\n--- Evaluating: {condition} seed={seed} on {benchmark} ---")
    result = run_evalplus(checkpoint_dir, benchmark, evalplus_output_dir)
    pass1 = parse_evalplus_output(result["output_path"], result["stdout"])
    n = {"humaneval": 164, "mbpp": 378}[benchmark]
    collect_result(condition, seed, benchmark, pass1, n, results_csv)
    return pass1


def main():
    parser = argparse.ArgumentParser(description="H-E2 EvalPlus Runner")
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--benchmark", choices=BENCHMARKS, required=True)
    parser.add_argument("--checkpoint_dir", required=True)
    parser.add_argument("--results_csv", default="results/all_results.csv")
    parser.add_argument("--evalplus_output_dir", default="results")
    parser.add_argument("--smoke", action="store_true", help="Smoke: just check evalplus importable")
    args = parser.parse_args()

    if args.smoke:
        from evalplus.data import get_human_eval_plus
        n = len(get_human_eval_plus())
        print(f"Smoke OK: evalplus has {n} HumanEval+ problems")
        return

    evaluate_checkpoint(
        condition=args.condition,
        seed=args.seed,
        benchmark=args.benchmark,
        checkpoint_dir=args.checkpoint_dir,
        results_csv=args.results_csv,
        evalplus_output_dir=args.evalplus_output_dir,
    )


if __name__ == "__main__":
    main()
