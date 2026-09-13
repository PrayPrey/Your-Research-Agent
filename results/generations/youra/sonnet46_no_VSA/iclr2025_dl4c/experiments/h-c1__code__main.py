"""
H-C1 pipeline orchestrator.
Stages: train → evaluate → analyze → figures
"""
import argparse
import json
import sys
from pathlib import Path

from config import (
    CONDITIONS, SEEDS, BENCHMARKS,
    CHECKPOINT_DIR, H_E2_DATASETS_DIR, H_E2_RESULTS_CSV,
    RESULTS_JSON, REPORT_PATH, FIGURES_DIR, EVALPLUS_OUTPUT_DIR,
)


def verify_checkpoints(checkpoint_dir: str = CHECKPOINT_DIR) -> dict:
    """Return {key: path} for existing checkpoints."""
    found = {}
    for condition in CONDITIONS:
        for seed in SEEDS:
            key = f"{condition}_seed{seed}"
            path = f"{checkpoint_dir}/condition_{condition}_seed_{seed}"
            if Path(path).exists():
                found[key] = path
    return found


def main():
    parser = argparse.ArgumentParser(description="H-C1 full pipeline")
    parser.add_argument("--stage", default="all",
                        choices=["train", "evaluate", "analyze", "figures", "all"])
    parser.add_argument("--checkpoint_dir", default=CHECKPOINT_DIR)
    parser.add_argument("--data_dir", default=H_E2_DATASETS_DIR)
    parser.add_argument("--h_e2_results", default=H_E2_RESULTS_CSV)
    parser.add_argument("--results_json", default=RESULTS_JSON)
    parser.add_argument("--figures_dir", default=FIGURES_DIR)
    parser.add_argument("--lora", action="store_true", help="Use LoRA (OOM fallback)")
    parser.add_argument("--skip_existing", action="store_true", default=True)
    parser.add_argument("--smoke", action="store_true", help="Smoke test all stages")
    args = parser.parse_args()

    if args.stage in ("train", "all"):
        from train import run_all_training
        print(f"\n{'='*60}\nSTAGE: TRAIN\n{'='*60}")
        if args.smoke:
            from train import run_sft
            run_sft("humaneval_only", 42, args.checkpoint_dir, args.data_dir, smoke=True)
        else:
            checkpoint_map = run_all_training(
                args.checkpoint_dir, args.data_dir,
                use_lora=args.lora,
                skip_existing=args.skip_existing,
            )
            print(f"Training complete. {len(checkpoint_map)} checkpoints.")

    if args.stage in ("evaluate", "all"):
        from evaluate import evaluate_all_models
        print(f"\n{'='*60}\nSTAGE: EVALUATE\n{'='*60}")
        if args.smoke:
            from evaluate import evalplus_evaluate
            from evalplus.data import get_human_eval_plus
            n = len(get_human_eval_plus())
            print(f"Smoke OK: evalplus has {n} HumanEval+ problems")
        else:
            checkpoint_map = verify_checkpoints(args.checkpoint_dir)
            if not checkpoint_map:
                print("[ERROR] No checkpoints found. Run train stage first.")
                sys.exit(1)
            results = evaluate_all_models(
                args.checkpoint_dir, args.results_json, EVALPLUS_OUTPUT_DIR,
                skip_existing=args.skip_existing,
            )
            print(f"Evaluation complete.")

    if args.stage in ("analyze", "all"):
        from analyze import run_full_analysis, write_report
        print(f"\n{'='*60}\nSTAGE: ANALYZE\n{'='*60}")
        if args.smoke:
            from analyze import compute_eta_squared
            vals = {c: [0.3, 0.4, 0.2] for c in CONDITIONS}
            eta = compute_eta_squared(vals)
            print(f"Smoke OK: eta_sq={eta:.4f}")
        else:
            if not Path(args.results_json).exists():
                print(f"[ERROR] Results not found: {args.results_json}")
                sys.exit(1)
            with open(args.results_json) as f:
                data = json.load(f)
            results_7b = {c: data.get(c, {}) for c in CONDITIONS}
            final = run_full_analysis(results_7b, args.h_e2_results, args.results_json)
            write_report(final, REPORT_PATH)
            gate = final["gate"]
            print(f"\nGate: {gate['gate_verdict']} (satisfied={gate['gate_satisfied']})")
            print(gate["summary"])

    if args.stage in ("figures", "all"):
        from figures import generate_all_figures
        from analyze import load_h_e2_results
        print(f"\n{'='*60}\nSTAGE: FIGURES\n{'='*60}")
        if args.smoke:
            from figures import plot_eta_sq_comparison
            plot_eta_sq_comparison({"humaneval": 0.35}, {"humaneval": 0.81}, "/tmp/smoke_eta.png")
            print("Smoke OK: figures render")
        else:
            if not Path(args.results_json).exists():
                print(f"[ERROR] Results not found: {args.results_json}")
                sys.exit(1)
            with open(args.results_json) as f:
                data = json.load(f)
            results_7b = {c: data.get(c, {}) for c in CONDITIONS}
            eta_sq_7b = data.get("eta_sq_7b", {})
            eta_sq_1b = data.get("eta_sq_1b", {})
            results_1b = load_h_e2_results(args.h_e2_results)
            generate_all_figures(results_7b, results_1b, eta_sq_7b, eta_sq_1b, args.figures_dir)

    print(f"\nH-C1 pipeline stage '{args.stage}' complete.")


if __name__ == "__main__":
    main()
