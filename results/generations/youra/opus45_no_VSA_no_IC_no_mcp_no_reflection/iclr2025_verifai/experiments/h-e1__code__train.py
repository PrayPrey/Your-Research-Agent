import json
import os
import time

import config
from generate import load_humaneval, generate_solution
from analyze import run_pylint_analysis
from evaluate import evaluate

def run_experiment() -> list[dict]:
    problems = load_humaneval()
    results = []

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    for i, p in enumerate(problems):
        print(f"[{i+1}/{len(problems)}] Processing {p['task_id']}...")
        code = generate_solution(p["prompt"], p["canonical_solution"])
        analysis = run_pylint_analysis(code)

        warning_codes = [m.get("symbol", "") for m in analysis["messages"]]

        results.append({
            "task_id": p["task_id"],
            "generated_code": code,
            "actionable_count": analysis["actionable_count"],
            "messages": analysis["messages"],
            "warning_codes": warning_codes,
        })

    with open(config.GENERATIONS_FILE, "w") as f:
        json.dump([{"task_id": r["task_id"], "code": r["generated_code"]} for r in results], f, indent=2)

    with open(config.PYLINT_RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    return results

def main() -> None:
    t0 = time.time()

    results = run_experiment()
    metrics = evaluate(results)

    elapsed = time.time() - t0
    status = "PASS" if metrics["gate_passed"] else "FAIL"

    print(f"\n{'='*50}")
    print(f"Gate: {status} (rate={metrics['warning_rate']:.2%}, threshold={config.GATE_THRESHOLD:.0%})")
    print(f"Avg warnings per problem: {metrics['avg_warnings']:.2f}")
    print(f"Elapsed time: {elapsed/60:.1f} min")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
