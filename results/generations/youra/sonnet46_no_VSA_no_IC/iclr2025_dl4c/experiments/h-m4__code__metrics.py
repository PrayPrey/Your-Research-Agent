import json
from pathlib import Path
from typing import Optional


def compute_metrics(pass_at_1: dict, cfg) -> dict:
    """
    Computes improvement, gap_vs_random50, P1 gate.
    Returns gate_results dict matching FR-9 JSON schema.
    """
    baseline = pass_at_1["variance50"]["step_0"]

    improvement = {}
    for cond in cfg.conditions:
        improvement[cond] = {}
        for step in cfg.steps:
            val = pass_at_1[cond].get(step)
            improvement[cond][step] = (val - baseline) if val is not None else None

    improvement_variance50_50 = improvement["variance50"]["step_50"]
    improvement_random50_50 = improvement["random50"]["step_50"]

    if improvement_variance50_50 is not None and improvement_random50_50 is not None:
        gap_vs_random50 = improvement_variance50_50 - improvement_random50_50
        p1_pass = (
            improvement_variance50_50 >= cfg.p1_improvement_pp and
            gap_vs_random50 >= cfg.p1_gap_pp
        )
    else:
        gap_vs_random50 = None
        p1_pass = False

    return {
        "gate_passed": p1_pass,
        "p1_pass": p1_pass,
        "p3_pass": None,
        "baseline_pass_at_1": baseline,
        "pass_at_1": pass_at_1,
        "improvement": improvement,
        "gap_vs_random50_at_50": gap_vs_random50,
        "efficiency_ratio": None,
        "thresholds": {
            "p1_improvement_pp": cfg.p1_improvement_pp * 100,
            "p1_gap_pp": cfg.p1_gap_pp * 100,
            "p3_efficiency": cfg.p3_efficiency,
        },
        "n_samples_per_problem": cfg.n_samples,
        "n_problems": 164,
        "dataset": "humaneval_plus",
    }


def finalize_p3(results: dict, cfg) -> dict:
    """Compute P3 efficiency ratio if both variance50 and full374 achieve >= p1_improvement_pp."""
    improvement_variance50 = results["improvement"]["variance50"]["step_50"]
    improvement_full374 = results["improvement"].get("full374", {}).get("step_50")

    if improvement_full374 is not None and improvement_variance50 is not None:
        if improvement_variance50 >= cfg.p1_improvement_pp and improvement_full374 >= cfg.p1_improvement_pp:
            if improvement_full374 > 0:
                efficiency_ratio = improvement_variance50 / improvement_full374
                results["efficiency_ratio"] = efficiency_ratio
                results["p3_pass"] = efficiency_ratio >= cfg.p3_efficiency
            else:
                results["efficiency_ratio"] = None
                results["p3_pass"] = None
        else:
            results["p3_pass"] = None
    return results


def save_gate_results(results: dict, cfg) -> None:
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)
    out = f"{cfg.results_dir}/gate_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[H-M4] gate_results.json saved to {out}")


def print_gate_summary(results: dict) -> None:
    baseline = results["baseline_pass_at_1"]
    imp_var = results["improvement"]["variance50"]["step_50"]
    gap = results["gap_vs_random50_at_50"]
    p1 = results["p1_pass"]

    for cond in results["pass_at_1"]:
        for step, val in results["pass_at_1"][cond].items():
            if val is not None:
                assert 0.0 <= val <= 1.0, f"Invalid pass@1 {val}: {cond}/{step}"

    print(f"[H-M4] baseline pass@1 = {baseline:.4f} ({baseline*100:.2f}%)")
    if imp_var is not None:
        print(f"[H-M4] improvement_variance50 at step50 = {imp_var*100:.2f}pp")
    if gap is not None:
        print(f"[H-M4] gap_vs_random50 at step50 = {gap*100:.2f}pp")
    print(f"[H-M4] P1 gate: {'PASS' if p1 else 'FAIL'}")
    if results.get("p3_pass") is not None:
        print(f"[H-M4] P3 efficiency_ratio = {results['efficiency_ratio']:.3f} "
              f"({'PASS' if results['p3_pass'] else 'FAIL'})")
