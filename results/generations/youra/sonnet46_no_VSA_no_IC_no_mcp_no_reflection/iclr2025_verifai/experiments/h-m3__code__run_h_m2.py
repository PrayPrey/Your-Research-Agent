"""H-M2: Feedback Specificity Measurement Experiment."""
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))
from src.load_h_m1 import load_failing_records
from src.z3_extractor import Z3ConstraintExtractor
from src.measure import FeedbackMeasurer
from src.analyze import run_analysis
from src.visualize import generate_all_figures
from src.write_results import write_records, write_summary

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "h-m2")


def verify_tool_activation(measurer: FeedbackMeasurer) -> None:
    """Sanity check: all tools produce output on failing sample code."""
    sample_func = '''def add(a, b):
    """Add two numbers and return the result."""
    return a - b  # intentional bug
'''
    sample_runnable = sample_func + "\nassert add(1, 2) == 3\n"
    results = {
        "execution": measurer.measure_execution(sample_runnable),
        "pyright": measurer.measure_pyright(sample_func),
        "mypy": measurer.measure_mypy(sample_func),
    }
    for name, r in results.items():
        if r["char_count"] > 0:
            print(f"  ✓ {name}: char_count={r['char_count']}")
        else:
            print(f"  ⚠ {name}: char_count=0 (may be OK for some tools on this sample)")
    print("Sanity check done.")


def process_record(rec: dict, measurer: FeedbackMeasurer, extractor: Z3ConstraintExtractor) -> list[dict]:
    code = rec["code"]
    task_id = rec["task_id"]
    bug_type = rec.get("bug_type", "unknown")
    source = rec.get("source", "unknown")

    constraints = extractor.extract(task_id, code)
    runnable = rec.get("runnable", code)
    measurements = measurer.measure_all(code, constraints, runnable=runnable)

    out = []
    for m in measurements:
        out.append({
            "task_id": task_id,
            "source": source,
            "bug_type": bug_type,
            "verifier": m["verifier"],
            "char_count": m["char_count"],
            "field_count": m["field_count"],
            "timeout": m["timeout"],
        })
    return out


def main() -> None:
    print("=== H-M2: Feedback Specificity Measurement ===\n")

    client = OpenAI()
    measurer = FeedbackMeasurer(timeout_secs=10)
    extractor = Z3ConstraintExtractor(client, model="gpt-4o-mini")

    print("Step 1: Loading H-M1 failing solutions...")
    failing = load_failing_records()
    print(f"  → {len(failing)} failing solutions\n")

    print("Step 2: Sanity check verifier activation...")
    verify_tool_activation(measurer)
    print()

    print("Step 3: Measuring feedback specificity (4 verifiers × all failing solutions)...")
    all_records = []
    completed = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_record, rec, measurer, extractor): rec for rec in failing}
        for future in as_completed(futures):
            try:
                result = future.result()
                all_records.extend(result)
            except Exception as e:
                print(f"  Error: {e}")
            completed += 1
            if completed % 20 == 0:
                print(f"  Progress: {completed}/{len(failing)}")

    print(f"  → {len(all_records)} total measurements ({len(failing)} problems × 4 verifiers)\n")

    print("Step 4: Statistical analysis...")
    analysis = run_analysis(all_records)
    pv = analysis["per_verifier"]
    for v in ["execution", "mypy", "pyright", "z3"]:
        if v in pv:
            print(f"  {v}: mean={pv[v]['mean']:.1f} chars, n={pv[v]['n']}")
    kw = analysis["kruskal_wallis"]
    print(f"\n  Kruskal-Wallis: H={kw['H']:.3f}, p={kw['p']:.4f}")
    print(f"  Effect size ε²={analysis['effect_size_epsilon2']:.4f}")
    print(f"  Z3 coverage: {analysis['z3_coverage_pct']}%")
    print(f"  Ordering confirmed: {analysis['ordering_confirmed']}")
    print(f"  Direction confirmed: {analysis['direction_confirmed']}")
    print()

    print("Step 5: Generating figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    generate_all_figures(all_records, FIGURES_DIR)

    print("Step 6: Persisting results...")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    write_records(all_records, os.path.join(RESULTS_DIR, "results.jsonl"))
    write_summary(analysis, os.path.join(RESULTS_DIR, "summary.json"))

    print("\n=== GATE VERDICT ===")
    # SHOULD_WORK gate: direction confirmed even without full stat sig
    if analysis["ordering_confirmed"]:
        gate = "PASS"
        reason = "Ordering SMT>=static>execution confirmed + KW p<0.05"
    elif analysis["direction_confirmed"]:
        gate = "PASS"
        reason = "Direction confirmed (SHOULD_WORK gate — direction sufficient)"
    elif kw["p"] < 0.05:
        gate = "PASS"
        reason = "KW p<0.05 (group differences significant)"
    else:
        gate = "FAIL"
        reason = "Neither ordering nor significance confirmed"

    print(f"Gate Result: {gate}")
    print(f"Reason: {reason}")
    analysis["gate_result"] = gate
    analysis["gate_reason"] = reason
    write_summary(analysis, os.path.join(RESULTS_DIR, "summary.json"))
    print("\nEXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
