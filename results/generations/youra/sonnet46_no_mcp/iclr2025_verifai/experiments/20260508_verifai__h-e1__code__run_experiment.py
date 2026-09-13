"""
run_experiment.py — h-e1 EXISTENCE PoC Pipeline

Verifies that formal repair tools (SynCode, Z3, mypy) are operationally
functional with CodeLlama-7B on HumanEval+/MBPP benchmarks.

Gate conditions (MUST_WORK):
  - delta_ast > 0  (SynCode reduces AST parse failures)
  - z3_eligibility_rate >= 0.15  (Z3 encodes >=15% of HumanEval problems)
  - mypy_structured_rate >= 0.90  (mypy returns structured output)
"""

import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESEARCH_DIR = os.path.join(BASE_DIR, "..")


def get_paths(base: str = RESEARCH_DIR):
    return {
        "data": os.path.join(base, "data"),
        "results": os.path.join(base, "results"),
        "figures": os.path.join(base, "figures"),
        "baseline_pool": os.path.join(base, "data", "baseline_pool.jsonl"),
        "syncode_pool": os.path.join(base, "data", "syncode_pool.jsonl"),
        "z3_eligibility": os.path.join(base, "data", "z3_eligibility.json"),
        "mypy_results": os.path.join(base, "data", "mypy_results.json"),
        "metrics": os.path.join(base, "results", "metrics.json"),
    }


def load_pool_from_jsonl(path: str):
    pool = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            task_id = record["task_id"]
            if task_id not in pool:
                pool[task_id] = []
            pool[task_id].append(record["completion"])
    return pool


def main():
    parser = argparse.ArgumentParser(description="h-e1 EXISTENCE PoC Experiment")
    parser.add_argument(
        "--load_pools",
        action="store_true",
        help="Load existing pools from disk (skip generation)",
    )
    parser.add_argument(
        "--skip_syncode",
        action="store_true",
        help="Skip SynCode pool generation (use baseline pool for both)",
    )
    parser.add_argument(
        "--base_dir",
        default=RESEARCH_DIR,
        help="Base directory for h-e1 outputs",
    )
    parser.add_argument(
        "--num_problems",
        type=int,
        default=None,
        help="Limit HumanEval problems to first N (PoC subset). None = all 164.",
    )
    args = parser.parse_args()

    paths = get_paths(args.base_dir)
    for d in [paths["data"], paths["results"], paths["figures"]]:
        os.makedirs(d, exist_ok=True)

    sys.path.insert(0, BASE_DIR)
    from data_loader import load_humaneval_plus, load_mbpp_plus, validate_datasets
    from metrics import MetricsEvaluator
    from mypy_checker import MypyChecker
    from visualization import Visualizer
    from z3_eligibility import Z3EligibilityChecker

    # ─────────────────────────────────────────────────────────────────
    # Step 1: Load Datasets
    # ─────────────────────────────────────────────────────────────────
    print("\n[1/7] Loading datasets...")
    humaneval = load_humaneval_plus()
    mbpp = load_mbpp_plus()
    validate_datasets(humaneval, mbpp)
    print(f"  HumanEval: {len(humaneval)} problems")
    print(f"  MBPP: {len(mbpp)} problems")

    if args.num_problems is not None:
        keys = sorted(humaneval.keys())[:args.num_problems]
        humaneval = {k: humaneval[k] for k in keys}
        print(f"  PoC subset: using first {len(humaneval)} HumanEval problems")

    # ─────────────────────────────────────────────────────────────────
    # Step 2: Generate Baseline Pool
    # ─────────────────────────────────────────────────────────────────
    if args.load_pools and os.path.exists(paths["baseline_pool"]):
        print("\n[2/7] Loading baseline pool from disk...")
        baseline_pool = load_pool_from_jsonl(paths["baseline_pool"])
        print(f"  Loaded {len(baseline_pool)} tasks from {paths['baseline_pool']}")
    else:
        print("\n[2/7] Generating baseline pool (CodeLlama-7B, N=20)...")
        from baseline_generator import BaselineGenerator
        gen = BaselineGenerator()
        print("  Loading model...")
        gen.load_model()
        print("  Generating samples...")
        baseline_pool = gen.generate_pool(
            humaneval,
            seeds=list(range(20)),
            output_path=paths["baseline_pool"],
        )
        print(f"  Baseline pool: {len(baseline_pool)} tasks")

    # ─────────────────────────────────────────────────────────────────
    # Step 3: Generate SynCode Pool
    # ─────────────────────────────────────────────────────────────────
    if args.skip_syncode:
        print("\n[3/7] SynCode skipped — using baseline pool for delta_ast computation")
        syncode_pool = baseline_pool
    elif args.load_pools and os.path.exists(paths["syncode_pool"]):
        print("\n[3/7] Loading SynCode pool from disk...")
        syncode_pool = load_pool_from_jsonl(paths["syncode_pool"])
        print(f"  Loaded {len(syncode_pool)} tasks from {paths['syncode_pool']}")
    else:
        print("\n[3/7] Generating SynCode grammar-constrained pool...")
        from syncode_generator import SyncodeGenerator
        sgen = SyncodeGenerator()
        print("  Loading SynCode model...")
        sgen.load_model()
        print("  Generating constrained samples...")
        syncode_pool = sgen.generate_pool(
            humaneval,
            seeds=list(range(20)),
            output_path=paths["syncode_pool"],
        )
        active = sgen.verify_constraint_active(syncode_pool)
        print(f"  SynCode constraint active: {active}")
        print(f"  SynCode pool: {len(syncode_pool)} tasks")

    # ─────────────────────────────────────────────────────────────────
    # Step 4: Z3 Eligibility Check
    # ─────────────────────────────────────────────────────────────────
    if args.load_pools and os.path.exists(paths["z3_eligibility"]):
        print("\n[4/7] Loading Z3 eligibility from disk...")
        with open(paths["z3_eligibility"], "r") as f:
            eligibility = json.load(f)
        print(f"  Loaded {len(eligibility)} entries")
    else:
        print("\n[4/7] Checking Z3 SMT eligibility...")
        checker = Z3EligibilityChecker(timeout_ms=2000)
        eligibility = checker.check_all(humaneval, paths["z3_eligibility"])

    # ─────────────────────────────────────────────────────────────────
    # Step 5: mypy Structured Output Check
    # ─────────────────────────────────────────────────────────────────
    if args.load_pools and os.path.exists(paths["mypy_results"]):
        print("\n[5/7] Loading mypy results from disk...")
        with open(paths["mypy_results"], "r") as f:
            mypy_results = json.load(f)
        print(f"  Loaded {len(mypy_results)} entries")
    else:
        print("\n[5/7] Running mypy structured output checks...")
        mypy_checker = MypyChecker()
        mypy_results = mypy_checker.check_pool(
            baseline_pool, paths["mypy_results"], sample_size=50
        )

    # ─────────────────────────────────────────────────────────────────
    # Step 6: Compute Metrics & Evaluate Gate
    # ─────────────────────────────────────────────────────────────────
    print("\n[6/7] Computing metrics and evaluating gate...")
    evaluator = MetricsEvaluator()
    delta_ast = evaluator.compute_delta_ast(baseline_pool, syncode_pool)
    z3_rate = evaluator.compute_z3_eligibility_rate(eligibility)
    mypy_rate = evaluator.compute_mypy_structured_rate(mypy_results)
    metrics = evaluator.evaluate_gate(delta_ast, z3_rate, mypy_rate, paths["metrics"])

    # ─────────────────────────────────────────────────────────────────
    # Step 7: Generate Figures
    # ─────────────────────────────────────────────────────────────────
    print("\n[7/7] Generating figures...")
    viz = Visualizer(paths["figures"])
    pools = {"baseline": baseline_pool, "syncode": syncode_pool}
    viz.save_all(metrics, pools, eligibility, mypy_results)

    # ─────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate result: {'PASS' if metrics['gate_pass'] else 'FAIL'}")
    print(f"  delta_ast        = {delta_ast:.4f}  (>0: {delta_ast > 0})")
    print(f"  z3_eligibility   = {z3_rate:.4f}  (>=0.15: {z3_rate >= 0.15})")
    print(f"  mypy_structured  = {mypy_rate:.4f}  (>=0.90: {mypy_rate >= 0.90})")
    print(f"\nOutputs:")
    print(f"  metrics:  {paths['metrics']}")
    print(f"  figures:  {paths['figures']}/")
    print("=" * 60)

    return 0 if metrics["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
