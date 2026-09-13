"""H-E1 experiment entry point. Run from repo root:
    conda run -n youra-h-e1 python docs/youra_research/h-e1/code/run.py
"""

import json
import logging
import os
import pathlib
import sys

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Load OPENAI_API_KEY from environment (set by caller or .env)
    try:
        from dotenv import load_dotenv
        load_dotenv("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_verifai/.env")
    except ImportError:
        pass  # dotenv optional

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set. Export it or put it in .env file.")
        sys.exit(1)

    # Verify mypy is installed
    import subprocess
    try:
        subprocess.run(["mypy", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        logger.error("mypy not found. Install it: pip install mypy")
        sys.exit(1)

    # Import pipeline after env check
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from pipeline import (
        BENCHMARKS,
        SEEDS,
        aggregate,
        run_benchmark,
        save_results,
        verify_mechanism_activated,
    )
    from visualize import generate_all_figures, FIGURES_DIR

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    all_results = []

    for benchmark in BENCHMARKS:
        for seed in SEEDS:
            logger.info(f"=== Running {benchmark} seed={seed} ===")
            results = run_benchmark(client, benchmark, seed)
            all_results.extend(results)
            logger.info(f"  {len(results)} failing solutions with mypy analysis")

    logger.info(f"Total failing solutions analyzed: {len(all_results)}")

    summary = aggregate(all_results)
    activated, indicators = verify_mechanism_activated(all_results)

    logger.info("=== Mechanism Verification ===")
    for k, v in indicators.items():
        logger.info(f"  {k}: {v}")
    logger.info(f"  activated: {activated}")

    save_results(all_results, summary)
    generate_all_figures(all_results, summary, FIGURES_DIR)

    # Gate evaluation
    logger.info("=== Gate Evaluation (MUST_WORK) ===")
    mbpp_fraction = summary.get("mbpp+", {}).get("type_error_fraction_mean", 0.0)
    he_fraction = summary.get("humaneval+", {}).get("type_error_fraction_mean", 0.0)

    logger.info(f"  MBPP+  type_error_fraction: {mbpp_fraction:.3f}")
    logger.info(f"  HEval+ type_error_fraction: {he_fraction:.3f}")

    GATE_PASS = 0.10
    GATE_BORDERLINE = 0.05

    if mbpp_fraction >= GATE_PASS:
        gate = "PASS"
    elif mbpp_fraction >= GATE_BORDERLINE:
        gate = "BORDERLINE"
    else:
        gate = "FAIL"

    logger.info(f"  Gate result: {gate}")
    logger.info("EXPERIMENT COMPLETE")

    # Write experiment_results.json for pipeline
    results_path = pathlib.Path("docs/youra_research/h-e1/experiment_results.json")
    with open(results_path, "w") as f:
        json.dump({
            "gate_result": gate,
            "gate_type": "MUST_WORK",
            "mbpp_type_error_fraction_mean": mbpp_fraction,
            "mbpp_type_error_fraction_std": summary.get("mbpp+", {}).get("type_error_fraction_std", 0.0),
            "humaneval_type_error_fraction_mean": he_fraction,
            "humaneval_type_error_fraction_std": summary.get("humaneval+", {}).get("type_error_fraction_std", 0.0),
            "total_failing_analyzed": len(all_results),
            "mechanism_activated": activated,
            "mechanism_indicators": indicators,
            "summary": summary,
        }, f, indent=2)

    logger.info(f"Experiment results written to {results_path}")


if __name__ == "__main__":
    main()
