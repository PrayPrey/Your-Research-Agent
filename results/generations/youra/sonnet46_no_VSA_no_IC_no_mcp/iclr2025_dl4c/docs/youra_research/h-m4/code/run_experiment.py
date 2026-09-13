"""
A-9: Orchestration + gate reporting for h-m4.
# Ensure local code/ takes priority over inherited h-e1/code on sys.path
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).parent))

Two computation tracks:
  Track 1 (7B): Re-analysis of h-e1 results — JT test on difficulty-stratified deltas.
  Track 2 (1.3B): New SFT + RLEF-Fraction training — delta ratio sanity check.

Gate (SHOULD_WORK):
  Primary: JT p < 0.05 AND z > 0 (7B monotone trend)
  Secondary: delta_ratio >= 1.0 (1.3B sanity check)

Usage:
  python run_experiment.py            # full run (both tracks)
  python run_experiment.py --track 7b   # 7B re-analysis only (fast)
  python run_experiment.py --track 1b3  # 1.3B training only
"""
import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from config import H_M4_Config, BENCHMARK_ORDER


def run_7b_track(cfg: H_M4_Config) -> dict:
    from reanalyze import run_7b_analysis
    return run_7b_analysis(cfg)


def run_1b3_track(cfg: H_M4_Config) -> dict:
    from train_1_3b import train_sft_1_3b, train_rlef_1_3b, validate_rlef_checkpoint
    from evaluate_1_3b import evaluate_model, compute_delta_ratio_1_3b

    print("\n=== 1.3B Track: SFT + RLEF-Fraction ===")

    # Check if checkpoints already exist (resume support)
    sft_final = cfg.paths.sft_1_3b_dir + "/final"
    if not Path(sft_final).exists():
        print("[1.3B] Training SFT...")
        sft_final = train_sft_1_3b(cfg)
    else:
        print(f"[1.3B] SFT checkpoint found: {sft_final}")

    rlef_final = cfg.paths.rlef_1_3b_dir + "/final"
    if not Path(rlef_final).exists():
        print("[1.3B] Training RLEF-Fraction...")
        rlef_final = train_rlef_1_3b(cfg, sft_final)
    else:
        print(f"[1.3B] RLEF checkpoint found: {rlef_final}")

    reward_log = cfg.paths.logs_dir + "/reward_monitoring.jsonl"
    checkpoint_valid = validate_rlef_checkpoint(rlef_final, reward_log_path=reward_log)
    print(f"[1.3B] Checkpoint validation: {'PASS' if checkpoint_valid else 'WARN'}")

    print("[1.3B] Evaluating SFT checkpoint...")
    sft_results = evaluate_model(sft_final, "sft_1_3b", cfg)
    print(f"[1.3B] SFT results: {sft_results}")

    print("[1.3B] Evaluating RLEF-Fraction checkpoint...")
    rlef_results = evaluate_model(rlef_final, "rlef_fraction_1_3b", cfg)
    print(f"[1.3B] RLEF results: {rlef_results}")

    delta_ratio, deltas_1b3 = compute_delta_ratio_1_3b(rlef_results, sft_results)

    return {
        "sft_results": sft_results,
        "rlef_results": rlef_results,
        "deltas_1b3": deltas_1b3,
        "delta_ratio_1b3": delta_ratio,
        "delta_ratio_gate": delta_ratio >= cfg.gate.delta_ratio_min,
        "checkpoint_valid": checkpoint_valid,
    }


def evaluate_gate(results_7b: dict, results_1b3: dict, cfg: H_M4_Config) -> dict:
    jt_gate = results_7b.get("gate_passed", False)
    delta_ratio = results_1b3.get("delta_ratio_1b3", float("nan"))
    ratio_gate = results_1b3.get("delta_ratio_gate", False)

    overall_pass = jt_gate  # primary gate; ratio is secondary
    action = "SHOULD_WORK_CONFIRMED" if overall_pass else cfg.gate.null_result_action

    return {
        "jt_gate_pass": jt_gate,
        "delta_ratio": delta_ratio,
        "delta_ratio_gate_pass": ratio_gate,
        "overall_pass": overall_pass,
        "action": action,
    }


def save_results(results: dict, cfg: H_M4_Config) -> str:
    os.makedirs(cfg.paths.results_dir, exist_ok=True)
    out_path = str(Path(cfg.paths.results_dir) / "experiment_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"[Results] Saved to {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", choices=["7b", "1b3", "all"], default="all")
    args = parser.parse_args()

    cfg = H_M4_Config()

    results_7b = {}
    results_1b3 = {
        "deltas_1b3": {bm: float("nan") for bm in BENCHMARK_ORDER},
        "delta_ratio_1b3": float("nan"),
        "delta_ratio_gate": False,
        "note": "1.3B track skipped",
    }

    if args.track in ("7b", "all"):
        results_7b = run_7b_track(cfg)

    if args.track in ("1b3", "all"):
        results_1b3 = run_1b3_track(cfg)

    gate = evaluate_gate(results_7b, results_1b3, cfg)

    combined = {
        "hypothesis": "h-m4",
        "date": datetime.now().isoformat(),
        "track": args.track,
        "results_7b": results_7b,
        "results_1b3": results_1b3,
        "gate": gate,
    }

    save_results(combined, cfg)

    # Generate figures
    try:
        from analyze import generate_all_figures
        fig_input = {
            "deltas_7b": results_7b.get("deltas_7b", {}),
            "cis_7b": results_7b.get("cis", {}),
            "jt_z_7b": results_7b.get("jt_z", 0.0),
            "jt_p_7b": results_7b.get("jt_p", 1.0),
            "is_monotone_7b": results_7b.get("is_monotone", False),
            "violations_7b": results_7b.get("trend", {}).get("violations", []),
            "deltas_1b3": results_1b3.get("deltas_1b3", {}),
            "delta_ratio_1b3": results_1b3.get("delta_ratio_1b3", float("nan")),
        }
        fig_paths = generate_all_figures(fig_input, cfg)
        print(f"[Figures] Generated {len(fig_paths)} figures")
    except Exception as e:
        print(f"[Figures] Warning: {e}")

    # Gate report
    print("\n" + "="*60)
    print("GATE RESULT (h-m4 SHOULD_WORK)")
    print("="*60)
    print(f"  JT test gate: {'PASS' if gate['jt_gate_pass'] else 'FAIL'}")
    jt_z = results_7b.get("jt_z", float("nan"))
    jt_p = results_7b.get("jt_p", float("nan"))
    print(f"    z={jt_z:.4f}, p={jt_p:.4f} (threshold: p<0.05, z>0)")
    print(f"  Delta ratio gate: {'PASS' if gate['delta_ratio_gate_pass'] else 'FAIL'}")
    print(f"    ratio={gate['delta_ratio']:.3f} (threshold: >=1.0)")
    print(f"  Overall: {'PASS' if gate['overall_pass'] else 'FAIL'}")
    print(f"  Action: {gate['action']}")
    print("="*60)

    return combined


if __name__ == "__main__":
    main()
