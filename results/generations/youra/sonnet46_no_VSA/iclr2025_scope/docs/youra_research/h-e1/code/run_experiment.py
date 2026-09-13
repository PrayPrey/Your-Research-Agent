"""Main orchestration script for H-E1 experiment."""
import os
import sys
import json
import argparse
import time
from pathlib import Path

CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
sys.path.insert(0, str(CODE_DIR))

from config import (
    TEACHER_MODEL, CHECKPOINTS_DIR, RESULTS_DIR, FIGURES_DIR,
)


def load_checkpoints_state() -> dict:
    """Load existing checkpoints if available."""
    state_path = HYPOTHESIS_DIR / "results" / "run_state.json"
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return {}


def save_checkpoints_state(state: dict) -> None:
    """Save experiment state for resuming."""
    state_path = HYPOTHESIS_DIR / "results" / "run_state.json"
    state_path.parent.mkdir(exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def run_full_experiment(
    skip_distill: bool = False,
    skip_eval: bool = False,
    skip_analysis: bool = False,
    mohawk_checkpoint: str | None = None,
    lawcat_checkpoint: str | None = None,
    hybrid4_checkpoint: str | None = None,
) -> dict:
    """Run all experiment phases. Returns analysis results."""

    state = load_checkpoints_state()

    # ─── Phase 1: Distillation ────────────────────────────────────────────────
    if not skip_distill:
        if not state.get("mohawk_checkpoint"):
            print("\n" + "=" * 70)
            print("PHASE 1a: MOHAWK-SSM 3-stage distillation")
            print("=" * 70)
            from distill_mohawk import run_full_mohawk_pipeline
            mohawk_ckpt = run_full_mohawk_pipeline(
                output_base=str(CHECKPOINTS_DIR / "mohawk")
            )
            state["mohawk_checkpoint"] = mohawk_ckpt
            save_checkpoints_state(state)
        else:
            mohawk_ckpt = state["mohawk_checkpoint"]
            print(f"[Resume] MOHAWK checkpoint: {mohawk_ckpt}")

        if not state.get("lawcat_checkpoint"):
            print("\n" + "=" * 70)
            print("PHASE 1b: LAWCAT 2-phase distillation")
            print("=" * 70)
            from distill_lawcat import run_full_lawcat_pipeline
            lawcat_ckpt = run_full_lawcat_pipeline(
                output_base=str(CHECKPOINTS_DIR / "lawcat")
            )
            state["lawcat_checkpoint"] = lawcat_ckpt
            save_checkpoints_state(state)
        else:
            lawcat_ckpt = state["lawcat_checkpoint"]
            print(f"[Resume] LAWCAT checkpoint: {lawcat_ckpt}")

        if not state.get("hybrid4_checkpoint"):
            print("\n" + "=" * 70)
            print("PHASE 1c: Hybrid-4 construction + Stage 3")
            print("=" * 70)
            from distill_hybrid4 import run_hybrid4_pipeline
            hybrid4_ckpt = run_hybrid4_pipeline(
                mohawk_ssm_checkpoint=mohawk_ckpt,
                output_dir=str(CHECKPOINTS_DIR / "hybrid4" / "stage3"),
            )
            state["hybrid4_checkpoint"] = hybrid4_ckpt
            save_checkpoints_state(state)
        else:
            hybrid4_ckpt = state["hybrid4_checkpoint"]
            print(f"[Resume] Hybrid-4 checkpoint: {hybrid4_ckpt}")
    else:
        # Use provided checkpoints or state
        mohawk_ckpt = mohawk_checkpoint or state.get("mohawk_checkpoint")
        lawcat_ckpt = lawcat_checkpoint or state.get("lawcat_checkpoint")
        hybrid4_ckpt = hybrid4_checkpoint or state.get("hybrid4_checkpoint")
        if not all([mohawk_ckpt, lawcat_ckpt, hybrid4_ckpt]):
            raise ValueError(
                "skip_distill=True but checkpoints not provided. "
                "Pass --mohawk-checkpoint, --lawcat-checkpoint, --hybrid4-checkpoint"
            )

    # ─── Phase 2: Evaluation ──────────────────────────────────────────────────
    if not skip_eval and not state.get("evaluation_done"):
        print("\n" + "=" * 70)
        print("PHASE 2: LongBench v2 evaluation (all 4 models)")
        print("=" * 70)
        from evaluate import run_all_evaluations
        eval_results = run_all_evaluations(
            teacher_path=TEACHER_MODEL,
            mohawk_ckpt=mohawk_ckpt,
            lawcat_ckpt=lawcat_ckpt,
            hybrid4_ckpt=hybrid4_ckpt,
            results_dir=str(RESULTS_DIR),
        )
        state["evaluation_done"] = True
        save_checkpoints_state(state)
    else:
        if skip_eval:
            print("[Skip] Evaluation")
        else:
            print("[Resume] Evaluation already done")

    # ─── Phase 3: Analysis ────────────────────────────────────────────────────
    if not skip_analysis:
        print("\n" + "=" * 70)
        print("PHASE 3: Statistical analysis")
        print("=" * 70)
        from analyze import run_analysis
        analysis_results = run_analysis(results_dir=str(RESULTS_DIR))

        # Save structured experiment_results.json
        exp_results_path = HYPOTHESIS_DIR / "experiment_results.json"
        with open(exp_results_path, "w") as f:
            json.dump(analysis_results, f, indent=2)
        print(f"experiment_results.json saved to {exp_results_path}")

        # ─── Phase 4: Visualization ───────────────────────────────────────────
        print("\n" + "=" * 70)
        print("PHASE 4: Figure generation")
        print("=" * 70)
        from visualize import generate_all_figures
        generate_all_figures(
            delta_norms=analysis_results.get("delta_norms", {}),
            analysis_results=analysis_results,
            figures_dir=str(FIGURES_DIR),
        )

        return analysis_results
    else:
        print("[Skip] Analysis")
        return {}


def main():
    p = argparse.ArgumentParser(description="H-E1: MOHAWK vs LAWCAT LongBench v2 experiment")
    p.add_argument("--skip-distill", action="store_true",
                   help="Skip distillation (use existing checkpoints)")
    p.add_argument("--skip-eval", action="store_true",
                   help="Skip evaluation (use existing results)")
    p.add_argument("--skip-analysis", action="store_true",
                   help="Skip analysis and visualization")
    p.add_argument("--mohawk-checkpoint", type=str, default=None)
    p.add_argument("--lawcat-checkpoint", type=str, default=None)
    p.add_argument("--hybrid4-checkpoint", type=str, default=None)
    args = p.parse_args()

    start = time.time()
    results = run_full_experiment(
        skip_distill=args.skip_distill,
        skip_eval=args.skip_eval,
        skip_analysis=args.skip_analysis,
        mohawk_checkpoint=args.mohawk_checkpoint,
        lawcat_checkpoint=args.lawcat_checkpoint,
        hybrid4_checkpoint=args.hybrid4_checkpoint,
    )
    elapsed = time.time() - start
    print(f"\nTotal experiment time: {elapsed/3600:.2f} hours")

    if results:
        gate = results.get("gate_passed", False)
        ratio = results.get("interaction_ratio", 0.0)
        print(f"\nFinal gate result: {'PASS' if gate else 'FAIL'}")
        print(f"Interaction ratio: {ratio:.4f}")


if __name__ == "__main__":
    main()
