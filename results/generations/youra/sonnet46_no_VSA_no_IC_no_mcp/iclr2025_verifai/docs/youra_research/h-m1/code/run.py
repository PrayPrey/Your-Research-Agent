"""H-M1 experiment entry point: repair loop + Spearman analysis + gate evaluation."""

import json
import logging
import os
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# H-E1 first so H-M1 modules can shadow (e.g. config.py, visualize.py)
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code"))
# H-M1 code takes precedence
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from openai import OpenAI
from repair_loop import run_all_benchmarks, run_mypy_with_output
from analysis import aggregate_results, verify_mechanism_activated
from visualize import generate_all_figures
from config import ExperimentConfig

# Ensure H-E1 pipeline is on path (repair_loop also does this but belt-and-suspenders)
_h_e1_path = str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code")
if _h_e1_path not in sys.path:
    sys.path.insert(0, _h_e1_path)


def main() -> None:
    # Load config
    cfg = ExperimentConfig()

    # Verify OPENAI_API_KEY
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("OPENAI_API_KEY", "")
        except ImportError:
            pass
    if not api_key:
        logger.error("OPENAI_API_KEY not set. Exiting.")
        sys.exit(1)

    # Verify mypy is available
    try:
        run_mypy_with_output("x: int = 1")
    except FileNotFoundError:
        logger.error("mypy not found. Install with: pip install mypy")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Create output directories
    results_dir = pathlib.Path(cfg.results_dir)
    figures_dir = pathlib.Path(cfg.figures_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"H-M1 experiment: k_max={cfg.k_max}, seed={cfg.seed}, benchmarks={cfg.benchmarks}")

    # Run repair loop across all benchmarks
    records = run_all_benchmarks(
        client=client,
        benchmarks=cfg.benchmarks,
        seed=cfg.seed,
        k_max=cfg.k_max,
    )

    logger.info(f"Collected {len(records)} per-round records")

    # Save raw records as JSONL (without solution text for size)
    benchmarks_found = list(set(r["benchmark"] for r in records))
    for benchmark in benchmarks_found:
        bench_records = [r for r in records if r["benchmark"] == benchmark]
        jsonl_path = results_dir / f"{benchmark}_rounds.jsonl"
        with open(jsonl_path, "w") as f:
            for r in bench_records:
                rec = {k: v for k, v in r.items() if k != "solution" and k != "mypy_stdout"}
                f.write(json.dumps(rec) + "\n")
        logger.info(f"Saved {len(bench_records)} records to {jsonl_path}")

    # Compute analysis
    summary = aggregate_results(records, k_max=cfg.k_max)

    # Save summary
    summary_path = results_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to {summary_path}")

    # Gate evaluation (primary: MBPP+, secondary: HumanEval+)
    logger.info("=== GATE EVALUATION ===")
    gate_passed_overall = False
    for benchmark, stats in summary.items():
        rho = stats["spearman_rho"]
        pval = stats["p_value"]
        r5_lt_r1 = stats["round5_less_than_round1"]
        gate = stats["gate_passed"]
        logger.info(
            f"{benchmark}: rho={rho:.4f}, p={pval:.4f}, "
            f"round5<round1={r5_lt_r1}, gate_passed={gate}"
        )
        if benchmark in ("mbpp", "mbpp+"):
            gate_passed_overall = gate

    # Mechanism activation check
    activated, indicators = verify_mechanism_activated(records, benchmark="mbpp+")
    logger.info(f"Mechanism activated: {activated}")
    logger.info(f"Indicators: {indicators}")

    # Save gate result
    gate_result = {
        "gate_type": "MUST_WORK",
        "gate_passed": gate_passed_overall,
        "primary_benchmark": "mbpp",
        "summary": summary,
        "mechanism_activated": activated,
        "mechanism_indicators": indicators,
    }
    gate_path = results_dir / "gate_result.json"
    with open(gate_path, "w") as f:
        json.dump(gate_result, f, indent=2)
    logger.info(f"Gate result saved to {gate_path}")

    # Generate figures
    try:
        generate_all_figures(records, summary, figures_dir)
        logger.info("Figures generated")
    except Exception as e:
        logger.warning(f"Figure generation failed (non-fatal): {e}")

    logger.info(f"H-M1 experiment complete. Gate passed: {gate_passed_overall}")


if __name__ == "__main__":
    main()
