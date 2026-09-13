"""
H-C1: EvalPlus evaluation runner.
Evaluates all 12 checkpoints × 2 benchmarks = 24 pass@1 scores.
Results stored as JSON: {condition: {benchmark: [pass@1 × 3 seeds]}}.
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from config import (
    CONDITIONS, SEEDS, BENCHMARKS, CHECKPOINT_DIR,
    EVALPLUS_OUTPUT_DIR, RESULTS_JSON, RESULTS_CSV,
)


def run_evalplus(checkpoint_dir: str, benchmark: str, output_dir: str) -> dict:
    """Two-step evalplus: codegen → evaluate. Returns {stdout, output_path}."""
    root = Path(output_dir) / f"{Path(checkpoint_dir).name}_{benchmark}"
    root.mkdir(parents=True, exist_ok=True)

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

    samples_files = list(root.rglob("*.jsonl"))
    non_raw = [f for f in samples_files if "raw" not in f.name]
    samples_path = str(non_raw[0]) if non_raw else (
        str(samples_files[0]) if samples_files else str(root / "samples.jsonl")
    )

    eval_cmd = [
        sys.executable, "-m", "evalplus.evaluate",
        benchmark,
        "--samples", samples_path,
    ]
    print(f"  Evaluate: {' '.join(eval_cmd)}")
    r2 = subprocess.run(eval_cmd, capture_output=True, text=True)
    combined_stdout = r1.stdout + r2.stdout

    results_json_path = samples_path.replace(".jsonl", "_results.json")
    return {
        "stdout": combined_stdout,
        "stderr": r1.stderr + r2.stderr,
        "output_path": results_json_path,
        "samples_path": samples_path,
    }


def parse_evalplus_output(output_path: str, stdout: str) -> float:
    """Extract pass@1 from JSON file or stdout."""
    p = Path(output_path)
    if p.exists():
        with open(p) as f:
            data = json.load(f)
        if "pass@1" in data:
            return float(data["pass@1"])
        for key in ("pass_at_1", "pass_at1"):
            if key in data:
                return float(data[key])
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


def evalplus_evaluate(
    model_path: str,
    benchmark: str,
    output_dir: str = EVALPLUS_OUTPUT_DIR,
) -> float:
    """Run EvalPlus subprocess, parse pass@1. Returns float in [0, 1]."""
    result = run_evalplus(model_path, benchmark, output_dir)
    return parse_evalplus_output(result["output_path"], result["stdout"])


def _load_existing(results_json: str) -> dict:
    if Path(results_json).exists():
        with open(results_json) as f:
            return json.load(f)
    return {}


def _save_json(data: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def evaluate_all_models(
    checkpoint_dir: str = CHECKPOINT_DIR,
    output_file: str = RESULTS_JSON,
    output_dir: str = EVALPLUS_OUTPUT_DIR,
    skip_existing: bool = True,
) -> dict:
    """Evaluate all 12 checkpoints × 2 benchmarks = 24 evals.
    Returns nested dict {condition: {benchmark: [pass@1 × 3 seeds]}}."""
    existing = _load_existing(output_file)
    results = defaultdict(lambda: defaultdict(list))

    # Pre-populate from existing
    for cond in CONDITIONS:
        for bench in BENCHMARKS:
            existing_vals = (
                existing.get(cond, {}).get(bench, [])
                if isinstance(existing.get(cond, {}).get(bench), list)
                else []
            )
            results[cond][bench] = list(existing_vals)

    for condition in CONDITIONS:
        for i, seed in enumerate(SEEDS):
            ckpt = f"{checkpoint_dir}/condition_{condition}_seed_{seed}"
            if not Path(ckpt).exists():
                print(f"[WARN] Checkpoint not found: {ckpt} — skipping")
                continue
            for benchmark in BENCHMARKS:
                # Check if this seed index already computed
                current_vals = results[condition][benchmark]
                if skip_existing and len(current_vals) > i and current_vals[i] >= 0:
                    print(f"Skipping (exists): {condition} seed={seed} {benchmark}")
                    continue
                print(f"\n--- Evaluating: {condition} seed={seed} on {benchmark} ---")
                pass1 = evalplus_evaluate(ckpt, benchmark, output_dir)
                # Ensure list is long enough
                while len(results[condition][benchmark]) <= i:
                    results[condition][benchmark].append(-1.0)
                results[condition][benchmark][i] = pass1
                # Save incrementally
                _save_json(dict({k: dict(v) for k, v in results.items()}), output_file)
                print(f"  pass@1={pass1:.4f}")

    final = {k: dict(v) for k, v in results.items()}
    _save_json(final, output_file)
    return final


def main():
    parser = argparse.ArgumentParser(description="H-C1 EvalPlus Runner")
    parser.add_argument("--condition", choices=CONDITIONS)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--benchmark", choices=BENCHMARKS)
    parser.add_argument("--checkpoint_dir", default=CHECKPOINT_DIR)
    parser.add_argument("--output_file", default=RESULTS_JSON)
    parser.add_argument("--output_dir", default=EVALPLUS_OUTPUT_DIR)
    parser.add_argument("--all", action="store_true", help="Evaluate all 12 models")
    parser.add_argument("--smoke", action="store_true", help="Smoke: just check evalplus importable")
    args = parser.parse_args()

    if args.smoke:
        from evalplus.data import get_human_eval_plus
        n = len(get_human_eval_plus())
        print(f"Smoke OK: evalplus has {n} HumanEval+ problems")
        return

    if args.all:
        results = evaluate_all_models(args.checkpoint_dir, args.output_file, args.output_dir)
        print(f"Evaluation complete. Results saved to {args.output_file}")
        return

    if not (args.condition and args.seed and args.benchmark):
        parser.error("Provide --condition, --seed, --benchmark or use --all")

    ckpt = f"{args.checkpoint_dir}/condition_{args.condition}_seed_{args.seed}"
    pass1 = evalplus_evaluate(ckpt, args.benchmark, args.output_dir)
    print(f"pass@1 = {pass1:.4f}")


if __name__ == "__main__":
    main()
