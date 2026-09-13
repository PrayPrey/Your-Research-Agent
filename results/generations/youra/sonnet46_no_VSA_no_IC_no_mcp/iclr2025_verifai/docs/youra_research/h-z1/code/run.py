"""H-Z1 experiment runner: curate → Z3 spec validate → repair B vs C → report."""

import json
import logging
import os
import sys
import time
from pathlib import Path

# Wire h-e1 pipeline imports
_H_E1_CODE = Path(__file__).parent.parent.parent / "h-e1" / "code"
sys.path.insert(0, str(_H_E1_CODE))
sys.path.insert(0, str(Path(__file__).parent))

from config import Z1Config
from z3_utils import (curate_arithmetic_subset, generate_z3_spec,
                       validate_z3_spec, extract_z3_counterexample)
from repair_loop import repair_loop_b, repair_loop_c
from visualize import (plot_gate_metrics, plot_z3_funnel,
                        plot_per_round_curve, plot_ce_found_rate)
from pipeline import load_problems, generate_solution
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(Path(__file__).parent / "experiment.log"), mode="a"),
    ]
)
logger = logging.getLogger(__name__)

SPEC_CODES_PATH = None  # set in main


def _load_spec_codes() -> dict:
    """Load saved spec codes from disk."""
    if SPEC_CODES_PATH and SPEC_CODES_PATH.exists():
        return json.loads(SPEC_CODES_PATH.read_text())
    return {}


def _save_spec_codes(spec_codes: dict):
    if SPEC_CODES_PATH:
        SPEC_CODES_PATH.write_text(json.dumps(spec_codes, indent=2))


def main():
    cfg = Z1Config()
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    global SPEC_CODES_PATH
    SPEC_CODES_PATH = cfg.results_dir / "spec_codes.json"

    # Load API key from .env
    try:
        from dotenv import load_dotenv
        load_dotenv("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_verifai/.env")
    except ImportError:
        pass

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set.")
        sys.exit(1)
    client = OpenAI(api_key=api_key)

    logger.info("=" * 60)
    logger.info("H-Z1 Experiment: Z3 CE Feedback for LLM Code Repair")
    logger.info("=" * 60)

    # Step 1: Load HumanEval+
    logger.info("Step 1: Loading HumanEval+ problems...")
    all_problems = load_problems("humaneval+")
    logger.info(f"Loaded {len(all_problems)} problems")

    # Step 2: Curate arithmetic subset
    logger.info("Step 2: Curating arithmetic-heavy subset...")
    curated = curate_arithmetic_subset(all_problems)
    logger.info(f"Curated subset: {len(curated)} problems")

    # Step 3: Generate + validate Z3 specs (with resume support)
    validated_path = cfg.results_dir / "validated_subset.json"
    spec_codes = _load_spec_codes()

    if validated_path.exists() and len(spec_codes) > 0:
        saved = json.loads(validated_path.read_text())
        validated_subset = {tid: curated[tid] for tid in saved if tid in curated}
        logger.info(f"Resuming: loaded {len(validated_subset)} validated specs from disk")
        funnel_counts = {
            "total_problems": len(all_problems),
            "curated": len(curated),
            "spec_generated": len(curated),
            "spec_valid": len(validated_subset),
        }
    else:
        logger.info("Step 3: Generating and validating Z3 specs...")
        validated_subset = {}
        funnel_counts = {
            "total_problems": len(all_problems),
            "curated": len(curated),
            "spec_generated": 0,
            "spec_valid": 0,
        }

        for i, (task_id, problem) in enumerate(curated.items()):
            logger.info(f"  Z3 spec [{i+1}/{len(curated)}]: {task_id}")
            try:
                spec_code = generate_z3_spec(problem, client)
                funnel_counts["spec_generated"] += 1

                result = validate_z3_spec(spec_code, problem, timeout=cfg.z3_timeout)
                if result.valid:
                    validated_subset[task_id] = problem
                    spec_codes[task_id] = spec_code
                    funnel_counts["spec_valid"] += 1
                    logger.info(f"    {task_id}: VALID spec")
                else:
                    logger.info(f"    {task_id}: INVALID — {result.reject_reason}")
            except Exception as e:
                logger.warning(f"    {task_id}: spec generation error: {e}")
            time.sleep(0.1)

        # Save validated subset and spec codes
        _save_spec_codes(spec_codes)
        with open(validated_path, "w") as f:
            json.dump({tid: {"task_id": p["task_id"], "entry_point": p["entry_point"]}
                       for tid, p in validated_subset.items()}, f, indent=2)

        logger.info(f"Valid Z3 specs: {len(validated_subset)}/{len(curated)}")

        if len(validated_subset) < cfg.min_valid_z3_specs:
            logger.warning(
                f"Only {len(validated_subset)} valid specs — below minimum {cfg.min_valid_z3_specs}. "
                "Proceeding with available subset (PoC mode)."
            )

    # Step 4: Generate initial solutions with resume support
    initial_solutions_path = cfg.results_dir / "initial_solutions.json"
    if initial_solutions_path.exists():
        initial_solutions = json.loads(initial_solutions_path.read_text())
        logger.info(f"Resuming: loaded {len(initial_solutions)} initial solutions from disk")
    else:
        logger.info("Step 4: Generating initial solutions (shared, seed=42, temp=0.8)...")
        initial_solutions = {}
        for i, (task_id, problem) in enumerate(validated_subset.items()):
            logger.info(f"  Initial gen [{i+1}/{len(validated_subset)}]: {task_id}")
            sol = generate_solution(client, problem, seed=cfg.seed)
            initial_solutions[task_id] = sol
            time.sleep(0.1)
        initial_solutions_path.write_text(json.dumps(initial_solutions, indent=2))

    # Step 5: Run repair loops with resume support
    b_results_path = cfg.results_dir / "condition_b_results.jsonl"
    c_results_path = cfg.results_dir / "condition_c_results.jsonl"

    # Load existing results for resume
    def load_jsonl(path):
        results = []
        if path.exists():
            for line in path.read_text().strip().split("\n"):
                if line.strip():
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return results

    b_results = load_jsonl(b_results_path)
    c_results = load_jsonl(c_results_path)
    done_b = {r["task_id"] for r in b_results}
    done_c = {r["task_id"] for r in c_results}
    logger.info(f"Resuming repair loops: {len(done_b)} B done, {len(done_c)} C done")

    logger.info("Step 5: Running repair loops...")
    b_file = open(b_results_path, "a")
    c_file = open(c_results_path, "a")

    try:
        for i, (task_id, problem) in enumerate(validated_subset.items()):
            initial_sol = initial_solutions.get(task_id, "")
            if not initial_sol:
                logger.warning(f"  Skipping {task_id}: no initial solution")
                continue

            logger.info(f"  [{i+1}/{len(validated_subset)}] {task_id}")

            # Condition B
            if task_id not in done_b:
                logger.info(f"    Condition B...")
                result_b = repair_loop_b(problem, initial_sol, client, cfg)
                row_b = {
                    "task_id": result_b.task_id,
                    "condition": "B",
                    "passed": result_b.passed,
                    "rounds_to_pass": result_b.rounds_to_pass,
                    "z3_ce_found_count": 0,
                }
                b_results.append(row_b)
                b_file.write(json.dumps(row_b) + "\n")
                b_file.flush()
                logger.info(f"    B: passed={result_b.passed}, rounds={result_b.rounds_to_pass}")
                time.sleep(0.1)
            else:
                logger.info(f"    B: already done (skipping)")

            # Condition C
            if task_id not in done_c:
                spec_code = spec_codes.get(task_id, "")
                logger.info(f"    Condition C...")
                result_c = repair_loop_c(problem, initial_sol, spec_code, client, cfg)
                row_c = {
                    "task_id": result_c.task_id,
                    "condition": "C",
                    "passed": result_c.passed,
                    "rounds_to_pass": result_c.rounds_to_pass,
                    "z3_ce_found_count": result_c.z3_ce_found_count,
                }
                c_results.append(row_c)
                c_file.write(json.dumps(row_c) + "\n")
                c_file.flush()
                logger.info(f"    C: passed={result_c.passed}, rounds={result_c.rounds_to_pass}, "
                            f"z3_ce_found={result_c.z3_ce_found_count}")
                time.sleep(0.1)
            else:
                logger.info(f"    C: already done (skipping)")

    finally:
        b_file.close()
        c_file.close()

    # Step 6: Compute summary metrics
    logger.info("Step 6: Computing summary metrics...")
    # Only count problems present in both B and C
    b_by_task = {r["task_id"]: r for r in b_results}
    c_by_task = {r["task_id"]: r for r in c_results}
    common_tasks = set(b_by_task.keys()) & set(c_by_task.keys())
    n = len(common_tasks)

    pass_b = sum(1 for tid in common_tasks if b_by_task[tid]["passed"])
    pass_c = sum(1 for tid in common_tasks if c_by_task[tid]["passed"])
    pass_rate_b = pass_b / n if n > 0 else 0.0
    pass_rate_c = pass_c / n if n > 0 else 0.0
    delta = pass_rate_c - pass_rate_b

    n_ce_found = sum(1 for tid in common_tasks if c_by_task[tid]["z3_ce_found_count"] > 0)
    ce_found_rate = n_ce_found / n if n > 0 else 0.0

    summary = {
        "hypothesis_id": "h-z1",
        "n_problems": n,
        "curated_count": len(curated),
        "spec_valid_count": len(validated_subset),
        "pass_b": pass_b,
        "pass_c": pass_c,
        "pass_rate_b": pass_rate_b,
        "pass_rate_c": pass_rate_c,
        "delta": delta,
        "gate_condition": "pass_rate_c > pass_rate_b",
        "gate_pass": delta > 0,
        "z3_spec_validity_rate": len(validated_subset) / max(len(curated), 1),
        "z3_ce_found_rate": ce_found_rate,
        "funnel_counts": funnel_counts,
        "b_results": [b_by_task[t] for t in common_tasks],
        "c_results": [c_by_task[t] for t in common_tasks],
    }

    logger.info(f"Results: n={n}, pass_B={pass_b}/{n} ({pass_rate_b*100:.1f}%), "
                f"pass_C={pass_c}/{n} ({pass_rate_c*100:.1f}%), delta={delta*100:+.1f}pp")
    logger.info(f"Gate: pass_rate_C > pass_rate_B: {summary['gate_pass']}")

    # Step 7: Save results
    logger.info("Step 7: Saving results...")
    (cfg.results_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    exp_results_path = Path(__file__).parent.parent / "experiment_results.json"
    exp_results_path.write_text(json.dumps(summary, indent=2))
    logger.info(f"Saved experiment_results.json: {exp_results_path}")

    # Step 8: Generate figures
    logger.info("Step 8: Generating figures...")
    try:
        import matplotlib
        plot_gate_metrics(summary, cfg.figures_dir)
        plot_z3_funnel(funnel_counts, cfg.figures_dir)
        plot_per_round_curve(
            [b_by_task[t] for t in common_tasks],
            [c_by_task[t] for t in common_tasks],
            cfg.figures_dir
        )
        plot_ce_found_rate([c_by_task[t] for t in common_tasks], cfg.figures_dir)
        logger.info("All figures generated.")
    except Exception as e:
        logger.warning(f"Figure generation error (non-fatal): {e}")

    # Final gate check
    logger.info("=" * 60)
    logger.info(f"GATE RESULT: {'PASS' if summary['gate_pass'] else 'FAIL'}")
    logger.info(f"  pass@1_C ({pass_rate_c*100:.1f}%) {'>' if summary['gate_pass'] else '<='} "
                f"pass@1_B ({pass_rate_b*100:.1f}%)")
    logger.info(f"  Delta: {delta*100:+.1f} percentage points")
    logger.info(f"  Valid Z3 specs: {len(validated_subset)} (min required: {cfg.min_valid_z3_specs})")
    logger.info(f"  Z3 CE found rate: {ce_found_rate*100:.1f}%")
    logger.info("=" * 60)
    logger.info("EXPERIMENT COMPLETE")

    return summary


if __name__ == "__main__":
    main()
