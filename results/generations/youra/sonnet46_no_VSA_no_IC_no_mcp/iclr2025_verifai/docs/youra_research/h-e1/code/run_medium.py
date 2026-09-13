"""Medium-scale run: 100 problems per benchmark, 1 seed. Statistical power for >=10% gate."""

import json
import logging
import os
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(pathlib.Path(__file__).parent))


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_verifai/.env")
    except ImportError:
        pass

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set")
        sys.exit(1)

    import subprocess
    try:
        subprocess.run(["mypy", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        logger.error("mypy not found")
        sys.exit(1)

    from pipeline import (
        load_problems,
        generate_solution,
        evaluate_solution,
        run_mypy,
        aggregate,
        verify_mechanism_activated,
        RESULTS_DIR,
    )
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    N_PROBLEMS = 100  # per benchmark
    SEED = 42
    BENCHMARKS = ["mbpp+", "humaneval+"]

    all_results = []

    for benchmark in BENCHMARKS:
        all_problems = load_problems(benchmark)
        problems = dict(list(all_problems.items())[:N_PROBLEMS])
        logger.info(f"=== Running {benchmark} seed={SEED} ({len(problems)} problems) ===")

        failing = 0
        for i, (task_id, problem) in enumerate(problems.items()):
            if i % 20 == 0:
                logger.info(f"  {benchmark}: {i}/{len(problems)}, failing so far: {failing}")

            code = generate_solution(client, problem, seed=SEED)
            if not code:
                logger.warning(f"  Skipping {task_id}: empty generation")
                continue

            passed = evaluate_solution(task_id, code, problem)
            if not passed:
                failing += 1
                has_error, error_count, categories, stdout = run_mypy(code)
                all_results.append({
                    "task_id": task_id,
                    "seed": SEED,
                    "benchmark": benchmark,
                    "passed": passed,
                    "has_mypy_error": has_error,
                    "error_count": error_count,
                    "error_categories": categories,
                })
                logger.info(f"  {task_id}: FAIL, mypy_error={has_error}, count={error_count}")

        logger.info(f"Finished {benchmark}: {failing} failing / {len(problems)} problems")

    logger.info(f"Total failing solutions: {len(all_results)}")

    summary = aggregate(all_results)
    activated, indicators = verify_mechanism_activated(all_results)

    logger.info("=== Mechanism Verification ===")
    for k, v in indicators.items():
        logger.info(f"  {k}: {v}")
    logger.info(f"  activated: {activated}")

    # Gate evaluation
    gate_pass = 0.10
    gate_borderline = 0.05
    gate_satisfied = False
    gate_result = "FAIL"

    for bm, bm_summary in summary.items():
        frac = bm_summary["type_error_fraction_mean"]
        logger.info(f"  {bm}: type_error_fraction={frac:.3f} (gate={gate_pass})")
        if frac >= gate_pass:
            gate_satisfied = True
            gate_result = "PASS"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results_path = RESULTS_DIR / "results.jsonl"
    with open(results_path, "w") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")

    summary_path = RESULTS_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump({
            "summary": summary,
            "gate": {
                "pass_threshold": gate_pass,
                "borderline_threshold": gate_borderline,
                "satisfied": gate_satisfied,
                "result": gate_result,
            },
            "mechanism": {
                "activated": activated,
                "indicators": indicators,
            },
            "experiment_config": {
                "n_problems_per_benchmark": N_PROBLEMS,
                "seed": SEED,
                "benchmarks": BENCHMARKS,
                "model": "gpt-4o-mini",
                "temperature": 0.8,
            }
        }, f, indent=2)

    logger.info(f"Results: {results_path} ({len(all_results)} records)")
    logger.info(f"Summary: {summary_path}")
    logger.info(f"GATE: {gate_result} (satisfied={gate_satisfied})")
    logger.info("MEDIUM RUN COMPLETE")


if __name__ == "__main__":
    main()
