#!/usr/bin/env python3
"""
H-E1 Main Experiment: Logistic Growth Fit on Papers With Code Benchmarks.

Gate: scipy curve_fit converges AND R² > 0.9 for BOTH GLUE and SuperGLUE.
Exit code: 0 = PASS, 1 = FAIL.
"""
import json
import os
import sys
import traceback
from pathlib import Path

from data_retrieval import fetch_benchmark
from preprocessing import preprocess
from fitting import fit_linear, fit_logistic
from evaluation import evaluate
from visualization import plot_all, plot_gate_metrics, plot_parameter_summary

BENCHMARKS = [
    {"id": "glue", "release_date": "2019-02-01", "name": "GLUE"},
    {"id": "super-glue", "release_date": "2019-05-01", "name": "SuperGLUE"},
]

GATE_R2_THRESHOLD = 0.9

CODE_DIR = Path(__file__).parent
OUTPUTS_DIR = CODE_DIR / "outputs"
FIGURES_DIR = CODE_DIR.parent / "figures"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def run_benchmark(spec: dict) -> dict:
    bid = spec["id"]
    name = spec["name"]
    release = spec["release_date"]
    print(f"\n{'='*60}")
    print(f"Processing: {name} (id={bid})")
    print(f"{'='*60}")

    print(f"  Fetching data from Papers With Code API...")
    raw = fetch_benchmark(bid)
    print(f"  Raw entries: {len(raw)}")

    print(f"  Preprocessing...")
    t, y = preprocess(raw, release_date=release, min_date="2019-01-01")
    print(f"  Entries after dedup: {len(t)}  |  t range: [{t.min():.1f}, {t.max():.1f}] months")

    print(f"  Fitting linear model...")
    lin = fit_linear(t, y)
    print(f"  Linear R²={lin['r2']:.4f}, AIC={lin['aic']:.2f}")

    print(f"  Fitting logistic model...")
    log = fit_logistic(t, y)
    print(f"  Logistic converged={log['converged']}, R²={log['r2']:.4f}, AIC={log['aic']:.2f}")
    if log["converged"]:
        K, r, t0 = log["popt"]
        print(f"  Params: K={K:.4f}, r={r:.4f}, t0={t0:.2f}")

    ev = evaluate(lin, log)

    gate_passed = log["converged"] and log["r2"] >= GATE_R2_THRESHOLD
    print(f"  Gate (converged AND R²>{GATE_R2_THRESHOLD}): {'PASS ✓' if gate_passed else 'FAIL ✗'}")

    print(f"  Generating figures...")
    plot_all(bid, t, y, lin, log, str(FIGURES_DIR))

    return {
        "benchmark_id": bid,
        "name": name,
        "n_entries": int(len(t)),
        "t_range": [float(t.min()), float(t.max())],
        "linear_result": {"r2": lin["r2"], "aic": lin["aic"]},
        "logistic_result": {
            "converged": log["converged"],
            "r2": float(log["r2"]) if log["converged"] else None,
            "aic": float(log["aic"]) if log["converged"] else None,
            "popt": log["popt"].tolist() if log["converged"] else None,
            "ci95": log["ci95"].tolist() if log["converged"] else None,
        },
        "evaluation": ev,
        "gate_passed": gate_passed,
    }


def main() -> None:
    print("H-E1: Logistic Growth Fit on Papers With Code")
    print(f"Gate threshold: R² > {GATE_R2_THRESHOLD} for BOTH benchmarks\n")

    results = {}
    errors = {}

    for spec in BENCHMARKS:
        try:
            results[spec["id"]] = run_benchmark(spec)
        except Exception as e:
            print(f"\n[ERROR] {spec['name']}: {e}")
            traceback.print_exc()
            errors[spec["id"]] = str(e)
            results[spec["id"]] = {
                "benchmark_id": spec["id"],
                "name": spec["name"],
                "error": str(e),
                "gate_passed": False,
            }

    # Gate evaluation
    all_passed = all(
        r.get("gate_passed", False) for r in results.values()
    ) and len(errors) == 0

    print(f"\n{'='*60}")
    print("GATE EVALUATION SUMMARY")
    print(f"{'='*60}")
    for bid, r in results.items():
        status = "PASS ✓" if r.get("gate_passed") else "FAIL ✗"
        r2 = r.get("logistic_result", {}).get("r2")
        conv = r.get("logistic_result", {}).get("converged")
        print(f"  {r['name']}: {status}  (converged={conv}, R²={r2})")
    print(f"\nOverall Gate: {'PASS ✓' if all_passed else 'FAIL ✗'}")

    # Generate aggregate figures
    try:
        valid = {k: v for k, v in results.items() if "logistic_result" in v and v["logistic_result"].get("converged")}
        if valid:
            plot_gate_metrics(valid, str(FIGURES_DIR))
            plot_parameter_summary(valid, str(FIGURES_DIR))
            print("  Saved gate_metrics.png and parameter_summary.png")
    except Exception as e:
        print(f"  [WARN] Figure generation failed: {e}")

    # Save results JSON
    output = {
        "hypothesis_id": "h-e1",
        "status": "completed",
        "gate_result": "PASS" if all_passed else "FAIL",
        "gate_satisfied": all_passed,
        "metrics": {
            bid: {
                "converged": r.get("logistic_result", {}).get("converged", False),
                "r2": r.get("logistic_result", {}).get("r2"),
                "n_entries": r.get("n_entries"),
            }
            for bid, r in results.items()
        },
        "benchmarks": results,
        "errors": errors,
    }

    results_path = OUTPUTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to: {results_path}")

    # Also save CSV summary
    csv_path = OUTPUTS_DIR / "results.csv"
    with open(csv_path, "w") as f:
        f.write("benchmark,n_entries,converged,r2,aic_logistic,aic_linear,delta_aic,gate_passed\n")
        for bid, r in results.items():
            lr = r.get("logistic_result", {})
            ev = r.get("evaluation", {})
            f.write(
                f"{bid},{r.get('n_entries', '')},{lr.get('converged', False)},"
                f"{lr.get('r2', '')},{lr.get('aic', '')},"
                f"{r.get('linear_result', {}).get('aic', '')},{ev.get('delta_aic', '')},"
                f"{r.get('gate_passed', False)}\n"
            )
    print(f"CSV saved to: {csv_path}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
