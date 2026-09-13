"""Run H-M1 repair loop on remaining HumanEval+ problems (125-163) and combine results."""

import json
import logging
import os
import pathlib
import re
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "h-e1/code"))
sys.path.insert(0, str(pathlib.Path(__file__).parent / "code"))

from openai import OpenAI
from repair_loop import repair_loop_condition_b, run_mypy_with_output
from analysis import aggregate_results, verify_mechanism_activated
from visualize import generate_all_figures
from pipeline import load_problems

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

# Find already-processed task IDs from log
done_tasks = set()
log_path = pathlib.Path("docs/youra_research/h-m1/humaneval_run.log")
if log_path.exists():
    with open(log_path) as f:
        for line in f:
            m = re.search(r'mypy_errors_round_1: \d+ \[(\w+/\d+)\]', line)
            if m:
                done_tasks.add(m.group(1))
logger.info(f"Already done: {len(done_tasks)} tasks")

# Load all HumanEval+ problems
problems = load_problems("humaneval+")
remaining = {tid: prob for tid, prob in problems.items() if tid not in done_tasks}
logger.info(f"Remaining: {len(remaining)} tasks")

# Run remaining
new_records = []
total = len(remaining)
for i, (task_id, problem) in enumerate(remaining.items()):
    if i % 10 == 0:
        logger.info(f"Progress: {i}/{total}")
    try:
        records = repair_loop_condition_b(client, task_id, problem, "humaneval+", seed=42, k_max=5)
        new_records.extend(records)
    except Exception as e:
        logger.error(f"Skipping {task_id}: {e}")

logger.info(f"New records: {len(new_records)}")

# Save new records
jsonl_path = results_dir / "humaneval_remaining_rounds.jsonl"
with open(jsonl_path, "w") as f:
    for r in new_records:
        rec = {k: v for k, v in r.items() if k not in ("solution", "mypy_stdout")}
        f.write(json.dumps(rec) + "\n")

# Now reconstruct full records from both logs
# Parse the original log to reconstruct records
def parse_log_to_records(log_file):
    """Reconstruct minimal records from log lines (no exec_passed info)."""
    records = {}  # (task_id, round) -> mypy_count
    with open(log_file) as f:
        for line in f:
            m = re.search(r'mypy_errors_round_(\d+): (\d+) \[(\w+/\d+)\]', line)
            if m:
                rnd, cnt, tid = int(m.group(1)), int(m.group(2)), m.group(3)
                records[(tid, rnd)] = cnt

    # Convert to list format
    result = []
    tasks_seen = set()
    for (tid, rnd), cnt in records.items():
        tasks_seen.add(tid)
        result.append({
            "task_id": tid,
            "benchmark": "humaneval",
            "round": rnd,
            "mypy_error_count": cnt,
            "exec_passed": False,  # unknown from log, assume not passed
            "repaired": rnd > 1,
        })
    return result

prior_records = parse_log_to_records("docs/youra_research/h-m1/humaneval_run.log")
logger.info(f"Prior records reconstructed: {len(prior_records)}")

# Combine: use new_records (which have exec_passed) for remaining, prior for done
all_records = prior_records + new_records
logger.info(f"Total combined records: {len(all_records)}")

# Analysis
summary = aggregate_results(all_records, k_max=5)
logger.info(f"Summary:\n{json.dumps(summary, indent=2)}")

summary_path = results_dir / "summary_humaneval.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

logger.info("=== GATE EVALUATION ===")
gate_passed = False
for benchmark, stats in summary.items():
    rho = stats["spearman_rho"]
    pval = stats["p_value"]
    r5_lt_r1 = stats["round5_less_than_round1"]
    gate = stats["gate_passed"]
    logger.info(f"{benchmark}: rho={rho:.4f}, p={pval:.4f}, round5<round1={r5_lt_r1}, gate_passed={gate}")
    if benchmark == "humaneval":
        gate_passed = gate

activated, indicators = verify_mechanism_activated(all_records, benchmark="humaneval+")
logger.info(f"Mechanism activated: {activated}")
logger.info(f"Indicators: {indicators}")

gate_result = {
    "gate_type": "MUST_WORK",
    "primary_benchmark_used": "humaneval",
    "note": "MBPP+ has 0/378 problems with mypy errors at round 1; HumanEval+ used for gate",
    "gate_passed": gate_passed,
    "summary": summary,
    "mechanism_activated": activated,
    "mechanism_indicators": indicators,
}
gate_path = results_dir / "gate_result.json"
with open(gate_path, "w") as f:
    json.dump(gate_result, f, indent=2)
logger.info(f"Gate result: {gate_passed}")

try:
    generate_all_figures(all_records, summary, figures_dir)
    logger.info("Figures generated")
except Exception as e:
    logger.warning(f"Figure generation failed (non-fatal): {e}")

logger.info(f"H-M1 COMPLETE. Gate passed: {gate_passed}")
