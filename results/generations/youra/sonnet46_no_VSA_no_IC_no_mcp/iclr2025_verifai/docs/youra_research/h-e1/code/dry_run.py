"""Dry run: 5 MBPP+ problems, 1 seed, validates full pipeline without full API cost."""

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

    # Load first 5 MBPP+ problems only
    all_problems = load_problems("mbpp+")
    problems = dict(list(all_problems.items())[:5])

    logger.info(f"Dry run: {len(problems)} problems, seed=42")

    results = []
    for task_id, problem in problems.items():
        code = generate_solution(client, problem, seed=42)
        if not code:
            continue
        passed = evaluate_solution(task_id, code, problem)
        if not passed:
            has_error, error_count, categories, stdout = run_mypy(code)
            results.append({
                "task_id": task_id,
                "seed": 42,
                "benchmark": "mbpp+",
                "passed": passed,
                "has_mypy_error": has_error,
                "error_count": error_count,
                "error_categories": categories,
            })
            logger.info(f"  {task_id}: FAIL, mypy_error={has_error}, count={error_count}")
        else:
            logger.info(f"  {task_id}: PASS")

    logger.info(f"Dry run complete: {len(results)} failing solutions analyzed")

    if results:
        summary = aggregate(results)
        activated, indicators = verify_mechanism_activated(results)
        logger.info(f"Mechanism activated: {activated}, indicators: {indicators}")
    else:
        logger.info("All 5 problems passed — no failing solutions to analyze (expected for small subset)")
        summary = {}

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "dry_run_results.json"
    with open(out, "w") as f:
        json.dump({"results": results, "summary": summary}, f, indent=2)

    logger.info(f"Dry run results: {out}")
    logger.info("DRY RUN COMPLETE")


if __name__ == "__main__":
    main()
