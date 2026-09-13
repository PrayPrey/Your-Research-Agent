"""Run H-M1 repair loop on HumanEval+ only and save results."""

import json
import logging
import os
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "h-e1/code"))
sys.path.insert(0, str(pathlib.Path(__file__).parent / "code"))

from openai import OpenAI
from repair_loop import run_all_benchmarks
from analysis import aggregate_results, verify_mechanism_activated
from visualize import generate_all_figures

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    logger.error("OPENAI_API_KEY not set")
    sys.exit(1)

client = OpenAI(api_key=api_key)

results_dir = pathlib.Path("docs/youra_research/h-m1/results")
figures_dir = pathlib.Path("docs/youra_research/h-m1/figures")
results_dir.mkdir(parents=True, exist_ok=True)
figures_dir.mkdir(parents=True, exist_ok=True)

logger.info("H-M1: running HumanEval+ repair loop (k_max=5, seed=42)")

records = run_all_benchmarks(
    client=client,
    benchmarks=["humaneval+"],
    seed=42,
    k_max=5,
)

logger.info(f"Collected {len(records)} per-round records")

# Save JSONL
jsonl_path = results_dir / "humaneval_rounds.jsonl"
with open(jsonl_path, "w") as f:
    for r in records:
        rec = {k: v for k, v in r.items() if k not in ("solution", "mypy_stdout")}
        f.write(json.dumps(rec) + "\n")
logger.info(f"Saved {len(records)} records to {jsonl_path}")

# Analysis
summary = aggregate_results(records, k_max=5)
logger.info(f"Summary: {json.dumps(summary, indent=2)}")

summary_path = results_dir / "summary_humaneval.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

# Gate eval (HumanEval+ is secondary, but MBPP+ has 0 mypy errors so we use HumanEval+)
logger.info("=== GATE EVALUATION (HumanEval+) ===")
for benchmark, stats in summary.items():
    rho = stats["spearman_rho"]
    pval = stats["p_value"]
    r5_lt_r1 = stats["round5_less_than_round1"]
    gate = stats["gate_passed"]
    logger.info(f"{benchmark}: rho={rho:.4f}, p={pval:.4f}, round5<round1={r5_lt_r1}, gate_passed={gate}")

activated, indicators = verify_mechanism_activated(records, benchmark="humaneval+")
logger.info(f"Mechanism activated: {activated}")
logger.info(f"Indicators: {indicators}")

gate_result = {
    "gate_type": "MUST_WORK",
    "primary_benchmark_used": "humaneval",
    "note": "MBPP+ has 0 mypy errors at round 1 (confirmed by prior run), so HumanEval+ is used for gate",
    "gate_passed": summary.get("humaneval", {}).get("gate_passed", False),
    "summary": summary,
    "mechanism_activated": activated,
    "mechanism_indicators": indicators,
}
gate_path = results_dir / "gate_result.json"
with open(gate_path, "w") as f:
    json.dump(gate_result, f, indent=2)
logger.info(f"Gate result saved to {gate_path}")

try:
    generate_all_figures(records, summary, figures_dir)
    logger.info("Figures generated")
except Exception as e:
    logger.warning(f"Figure generation failed (non-fatal): {e}")

logger.info(f"H-M1 complete. Gate passed: {gate_result['gate_passed']}")
