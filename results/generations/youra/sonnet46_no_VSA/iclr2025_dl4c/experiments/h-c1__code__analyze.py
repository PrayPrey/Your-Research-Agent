"""
H-C1: Statistical analysis — η² comparison across scales.
Computes η² at 7B, compares to H-E2 η² at 1.3B.
SHOULD_WORK gate: PASS if η²_7B < η²_1.3B for ≥1 benchmark.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from config import (
    CONDITIONS, SEEDS, BENCHMARKS, H_E2_RESULTS_CSV, RESULTS_JSON,
    REPORT_PATH, FIGURES_DIR, H_E2_REF_ETA_SQ, ALPHA,
)


def compute_eta_squared(values_by_condition: dict) -> float:
    """One-way ANOVA η² = SS_between / SS_total from condition groups."""
    groups = [values_by_condition[c] for c in CONDITIONS if values_by_condition.get(c)]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) < 2:
        return float("nan")
    all_vals = [x for g in groups for x in g]
    grand_mean = np.mean(all_vals)
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_total = sum((x - grand_mean) ** 2 for x in all_vals)
    if ss_total == 0:
        return 0.0
    return float(ss_between / ss_total)


def load_h_e2_results(h_e2_csv: str = H_E2_RESULTS_CSV) -> dict:
    """Load H-E2 pass@1 results (1.3B). Returns {condition: {benchmark: [pass@1 × seeds]}}."""
    p = Path(h_e2_csv)
    if not p.exists():
        print(f"[WARN] H-E2 CSV not found at {h_e2_csv}; using hardcoded reference values")
        return {
            "humaneval_only": {"humaneval": [0.39634, 0.25610, 0.39634]},
            "mbpp_only": {"humaneval": [0.29268, 0.27439, 0.26220]},
            "leetcode_only": {"humaneval": [0.0, 0.0, 0.09146]},
            "equal_mix": {"humaneval": [0.10366, 0.09756, 0.10366]},
        }
    df = pd.read_csv(h_e2_csv)
    results = {c: {b: [] for b in BENCHMARKS} for c in CONDITIONS}
    for _, row in df.iterrows():
        cond = row["condition"]
        bench = row["benchmark"]
        if cond in results and bench in results[cond]:
            results[cond][bench].append(float(row["pass1"]))
    return results


def compare_scales(
    eta_sq_7b: dict,
    eta_sq_1b: dict,
) -> dict:
    """Evaluate SHOULD_WORK gate. PASS if η²_7B < η²_1.3B for ≥1 benchmark."""
    comparison = {}
    gate_pass = False
    for bench in BENCHMARKS:
        v7 = eta_sq_7b.get(bench)
        v1 = eta_sq_1b.get(bench)
        attenuated = (
            (v7 is not None and v1 is not None and not np.isnan(v7) and not np.isnan(v1))
            and v7 < v1
        )
        comparison[bench] = {
            "eta_sq_7b": v7,
            "eta_sq_1b": v1,
            "attenuated": attenuated,
            "cohens_f_7b": float(np.sqrt(v7 / (1 - v7))) if v7 and 0 < v7 < 1 else None,
            "cohens_f_1b": float(np.sqrt(v1 / (1 - v1))) if v1 and 0 < v1 < 1 else None,
        }
        if attenuated:
            gate_pass = True

    return {
        "gate_verdict": "PASS" if gate_pass else "NULL",
        "gate_satisfied": gate_pass,
        "per_benchmark": comparison,
        "eta_sq_7b": eta_sq_7b,
        "eta_sq_1b": eta_sq_1b,
        "summary": (
            "Attenuation confirmed: η²_7B < η²_1.3B for ≥1 benchmark"
            if gate_pass else
            "Null result: source effect robust to scale (informative, does not block pipeline)"
        ),
    }


def verify_h_c1_mechanism(results_7b: dict, results_1b: dict) -> tuple:
    """Verify scale attenuation is measurable. Returns (all_complete, indicators)."""
    indicators = {}
    for benchmark in BENCHMARKS:
        all_complete = all(
            len(results_7b.get(cond, {}).get(benchmark, [])) == 3
            for cond in CONDITIONS
        )
        indicators[f"{benchmark}_complete"] = all_complete

        condition_means_7b = [
            np.mean(results_7b.get(cond, {}).get(benchmark, [np.nan]))
            for cond in CONDITIONS
            if results_7b.get(cond, {}).get(benchmark)
        ]
        var_7b = float(np.var(condition_means_7b)) if condition_means_7b else float("nan")

        condition_means_1b = [
            np.mean(results_1b.get(cond, {}).get(benchmark, [np.nan]))
            for cond in CONDITIONS
            if results_1b.get(cond, {}).get(benchmark)
        ]
        var_1b = float(np.var(condition_means_1b)) if condition_means_1b else float("nan")

        indicators[f"{benchmark}_attenuation"] = (
            not np.isnan(var_7b) and not np.isnan(var_1b) and var_7b < var_1b
        )
        indicators[f"{benchmark}_var_7b"] = var_7b
        indicators[f"{benchmark}_var_1b"] = var_1b

    all_complete = all(indicators[k] for k in indicators if "_complete" in k)
    return all_complete, indicators


def run_full_analysis(
    results_7b: dict,
    h_e2_results_path: str = H_E2_RESULTS_CSV,
    output_file: str = RESULTS_JSON,
) -> dict:
    """Full analysis pipeline. Returns and saves final results.json."""
    results_1b = load_h_e2_results(h_e2_results_path)

    eta_sq_7b = {}
    eta_sq_1b = {}
    for bench in BENCHMARKS:
        vals_7b = {c: results_7b.get(c, {}).get(bench, []) for c in CONDITIONS}
        vals_7b = {c: v for c, v in vals_7b.items() if len(v) > 0}
        eta_sq_7b[bench] = compute_eta_squared(vals_7b) if vals_7b else float("nan")

        vals_1b = {c: results_1b.get(c, {}).get(bench, []) for c in CONDITIONS}
        vals_1b = {c: v for c, v in vals_1b.items() if len(v) > 0}
        if len(vals_1b) == 4:
            eta_sq_1b[bench] = compute_eta_squared(vals_1b)
        else:
            # Fall back to reference value from H-E2 ANOVA F-stat
            eta_sq_1b[bench] = H_E2_REF_ETA_SQ.get(bench)

    gate = compare_scales(eta_sq_7b, eta_sq_1b)
    complete_ok, indicators = verify_h_c1_mechanism(results_7b, results_1b)

    final = {
        **{c: results_7b.get(c, {}) for c in CONDITIONS},
        "eta_sq_7b": eta_sq_7b,
        "eta_sq_1b": eta_sq_1b,
        "gate": gate,
        "mechanism_indicators": indicators,
        "mechanism_complete": complete_ok,
        "generated_at": datetime.now().isoformat(),
    }

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(final, f, indent=2)
    print(f"Analysis saved: {output_file}")
    return final


def write_report(final: dict, report_path: str = REPORT_PATH) -> None:
    gate = final["gate"]
    lines = [
        "H-C1 Statistical Analysis Report",
        "==================================",
        f"Date: {datetime.now().isoformat(timespec='seconds')}",
        f"Model: deepseek-ai/deepseek-coder-7b-base (vs H-E2: 1.3b-base)",
        "",
        "=== η² Effect Size Comparison ===",
        f"{'Benchmark':<15} {'η²_7B':>10} {'η²_1.3B':>10} {'Attenuated':>12}",
        "-" * 50,
    ]
    for bench in BENCHMARKS:
        pb = gate["per_benchmark"].get(bench, {})
        v7 = pb.get("eta_sq_7b")
        v1 = pb.get("eta_sq_1b")
        att = pb.get("attenuated", False)
        v7s = f"{v7:.4f}" if v7 is not None and not (isinstance(v7, float) and np.isnan(v7)) else "N/A"
        v1s = f"{v1:.4f}" if v1 is not None and not (isinstance(v1, float) and np.isnan(v1)) else "N/A"
        lines.append(f"{bench:<15} {v7s:>10} {v1s:>10} {str(att):>12}")
    lines += [
        "",
        "=== Gate Evaluation (SHOULD_WORK) ===",
        f"Verdict: {gate['gate_verdict']}",
        f"Gate Satisfied: {gate['gate_satisfied']}",
        f"Summary: {gate['summary']}",
        "",
        "=== Mechanism Verification ===",
        f"All complete: {final['mechanism_complete']}",
    ]
    for k, v in final["mechanism_indicators"].items():
        lines.append(f"  {k}: {v}")

    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Report: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="H-C1 Statistical Analysis")
    parser.add_argument("--results_json", default=RESULTS_JSON)
    parser.add_argument("--h_e2_csv", default=H_E2_RESULTS_CSV)
    parser.add_argument("--report_out", default=REPORT_PATH)
    parser.add_argument("--figures_dir", default=FIGURES_DIR)
    parser.add_argument("--smoke", action="store_true", help="Smoke: run on synthetic data")
    args = parser.parse_args()

    if args.smoke:
        df_test = pd.DataFrame({
            "condition": CONDITIONS[:4],
            "pass1": [0.3, 0.4, 0.2, 0.35],
        })
        vals = {c: [v] for c, v in zip(CONDITIONS, [0.3, 0.4, 0.2, 0.35])}
        eta = compute_eta_squared(vals)
        print(f"Smoke OK: compute_eta_squared={eta:.4f}")
        return

    if not Path(args.results_json).exists():
        print(f"[ERROR] Results not found: {args.results_json}")
        return

    with open(args.results_json) as f:
        data = json.load(f)

    results_7b = {c: data.get(c, {}) for c in CONDITIONS}
    final = run_full_analysis(results_7b, args.h_e2_csv, args.results_json)
    write_report(final, args.report_out)

    gate = final["gate"]
    print(f"\nGate: {gate['gate_verdict']} (satisfied={gate['gate_satisfied']})")
    print(gate["summary"])


if __name__ == "__main__":
    main()
