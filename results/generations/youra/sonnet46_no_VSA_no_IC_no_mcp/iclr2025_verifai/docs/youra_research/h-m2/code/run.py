"""H-M2 experiment: Condition A vs B per-category repair rate differential."""

import json
import logging
import os
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Path setup: h-e1 provides shared pipeline utilities
_h_e1_path = str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code")
sys.path.insert(0, _h_e1_path)
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from openai import OpenAI
from repair_loop import run_condition_a, run_condition_b, run_mypy
from analysis import compute_differential
from visualize import generate_all_figures
from config import ExperimentConfig


def _load_checkpoint(path: pathlib.Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"results_a": [], "results_b": [], "completed_ids_a": [], "completed_ids_b": []}


def _save_checkpoint(path: pathlib.Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))


def main() -> None:
    cfg = ExperimentConfig()

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("OPENAI_API_KEY", "")
        except ImportError:
            pass
    if not api_key:
        logger.error("OPENAI_API_KEY not set.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    results_dir = pathlib.Path(cfg.results_dir)
    figures_dir = pathlib.Path(cfg.figures_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_path = pathlib.Path(cfg.checkpoint_path)
    ckpt = _load_checkpoint(checkpoint_path)
    completed_a = set(ckpt["completed_ids_a"])
    completed_b = set(ckpt["completed_ids_b"])
    results_a = ckpt["results_a"]
    results_b = ckpt["results_b"]

    # Load HumanEval+ problems
    from pipeline import load_problems
    problems = load_problems("humaneval+")
    task_ids = list(problems.keys())
    logger.info(f"H-M2: {len(task_ids)} HumanEval+ problems, seed={cfg.seed}, k_max={cfg.k_max}")

    # --- Condition A: execution-only repair ---
    logger.info("=== Condition A: Execution-Only Repair ===")
    remaining_a = [tid for tid in task_ids if tid not in completed_a]
    logger.info(f"Remaining: {len(remaining_a)} problems")
    for i, tid in enumerate(remaining_a):
        if i % 20 == 0:
            logger.info(f"[CondA] {i}/{len(remaining_a)}")
        try:
            result = run_condition_a(client, tid, problems[tid], cfg.seed, cfg.k_max)
            results_a.append(result)
            completed_a.add(tid)
            ckpt["results_a"] = results_a
            ckpt["completed_ids_a"] = list(completed_a)
            _save_checkpoint(checkpoint_path, ckpt)
        except Exception as e:
            logger.error(f"[CondA] Error on {tid}: {e}")

    # --- Condition B: execution+mypy repair ---
    logger.info("=== Condition B: Execution+Mypy Repair ===")
    remaining_b = [tid for tid in task_ids if tid not in completed_b]
    logger.info(f"Remaining: {len(remaining_b)} problems")
    for i, tid in enumerate(remaining_b):
        if i % 20 == 0:
            logger.info(f"[CondB] {i}/{len(remaining_b)}")
        try:
            result = run_condition_b(client, tid, problems[tid], cfg.seed, cfg.k_max)
            results_b.append(result)
            completed_b.add(tid)
            ckpt["results_b"] = results_b
            ckpt["completed_ids_b"] = list(completed_b)
            _save_checkpoint(checkpoint_path, ckpt)
        except Exception as e:
            logger.error(f"[CondB] Error on {tid}: {e}")

    logger.info(f"Collected: {len(results_a)} CondA, {len(results_b)} CondB records")

    # --- Analysis ---
    logger.info("=== Differential Analysis ===")
    analysis = compute_differential(results_a, results_b)

    logger.info(f"Type-error problems (n={analysis['type_error']['n']}): "
                f"CondA={analysis['type_error']['rate_A']:.1%}, "
                f"CondB={analysis['type_error']['rate_B']:.1%}, "
                f"delta={analysis['type_error']['delta']:+.3f}")
    logger.info(f"Non-type-error problems (n={analysis['non_type_error']['n']}): "
                f"CondA={analysis['non_type_error']['rate_A']:.1%}, "
                f"CondB={analysis['non_type_error']['rate_B']:.1%}, "
                f"delta={analysis['non_type_error']['delta']:+.3f}")
    logger.info(f"Differential: {analysis['differential']:+.3f}")
    logger.info(f"Gate (SHOULD_WORK, differential > 0): "
                f"{'PASS' if analysis['gate_passed'] else 'FAIL'}")
    logger.info(f"Mechanism activated: {analysis['mechanism_activated']}")

    # --- Save results ---
    # Raw per-problem results
    with open(results_dir / "condition_a_results.jsonl", "w") as f:
        for r in results_a:
            f.write(json.dumps({k: v for k, v in r.items() if k != "solution"}) + "\n")
    with open(results_dir / "condition_b_results.jsonl", "w") as f:
        for r in results_b:
            f.write(json.dumps({k: v for k, v in r.items() if k != "solution"}) + "\n")

    # Analysis summary
    with open(results_dir / "analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    # Gate result
    gate_result = {
        "gate_type": "SHOULD_WORK",
        "gate_passed": analysis["gate_passed"],
        "primary_metric": "differential",
        "differential": analysis["differential"],
        "delta_type": analysis["type_error"]["delta"],
        "delta_non": analysis["non_type_error"]["delta"],
        "type_error_n": analysis["type_error"]["n"],
        "non_type_error_n": analysis["non_type_error"]["n"],
        "mechanism_activated": analysis["mechanism_activated"],
        "analysis": analysis,
    }
    with open(results_dir / "gate_result.json", "w") as f:
        json.dump(gate_result, f, indent=2)

    # CSV for outputs
    import csv
    csv_rows = []
    a_by_id = {r["task_id"]: r for r in results_a}
    b_by_id = {r["task_id"]: r for r in results_b}
    type_ids = set()
    for r in results_a:
        if r.get("initial_mypy_errors", 0) > 0:
            type_ids.add(r["task_id"])
    for tid in task_ids:
        ra = a_by_id.get(tid, {})
        rb = b_by_id.get(tid, {})
        csv_rows.append({
            "task_id": tid,
            "category": "type_error" if tid in type_ids else "non_type_error",
            "initial_mypy_errors": ra.get("initial_mypy_errors", 0),
            "cond_a_passed": ra.get("final_passed", False),
            "cond_b_passed": rb.get("final_passed", False),
        })
    with open(results_dir / "../code/outputs/results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
        writer.writeheader()
        writer.writerows(csv_rows)

    # Figures
    try:
        generate_all_figures(analysis, results_a, results_b, figures_dir)
    except Exception as e:
        logger.warning(f"Figure generation failed (non-fatal): {e}")

    logger.info(f"H-M2 experiment complete. Gate: {'PASS' if analysis['gate_passed'] else 'FAIL'}")


if __name__ == "__main__":
    main()
