"""run_hm3_ptrue.py — CLI orchestrator for h-m3 P(True) confidence elicitation experiment."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from h_m3.config import (
    CONFIDENCE_SCORES_FILENAME,
    DEFAULT_FIGURES_DIR,
    DEFAULT_HM1_RESULTS,
    DEFAULT_HM2_RESULTS,
    DEFAULT_OUTPUT_DIR,
    MODEL_IDS,
    MODEL_SHORT_NAMES,
    PTRUE_PROMPT_FALLBACK,
    PTRUE_PROMPT_TEMPLATE,
    STD_GATE_THRESHOLD,
    VERIFIED_RESULTS_FILENAME,
    FigureConfig,
)
from h_m3.data_loader import (
    build_pair_iterator,
    filter_hard_easy_tiers,
    load_evalplus_problems,
    load_solutions_jsonl,
    load_tier_assignments,
)
from h_m3.evaluate import (
    build_verified_results,
    compute_gate_metrics,
    compute_secondary_metrics,
    evaluate_gate,
)
from h_m3.ptrue_extractor import (
    _last_out_logits_sample,
    run_ptrue_inference_for_model,
    verify_ptrue_mechanism,
)
from h_m3.visualize import (
    plot_c_by_tier,
    plot_c_cdf,
    plot_c_histograms,
    plot_c_vs_pass_at_1,
    plot_gate_check,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="h-m3: P(True) Confidence Elicitation")
    parser.add_argument(
        "--hm1_results_dir",
        default=DEFAULT_HM1_RESULTS,
        help=f"Path to h-e1/results directory (default: {DEFAULT_HM1_RESULTS})",
    )
    parser.add_argument(
        "--hm2_results_dir",
        default=DEFAULT_HM2_RESULTS,
        help=f"Path to h-m2/results directory (default: {DEFAULT_HM2_RESULTS})",
    )
    parser.add_argument(
        "--output_dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for JSON results (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--figures_dir",
        default=DEFAULT_FIGURES_DIR,
        help=f"Output directory for figures (default: {DEFAULT_FIGURES_DIR})",
    )
    parser.add_argument(
        "--device",
        default="cuda",
        help="Device to use (default: cuda)",
    )
    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Run smoke test: 2 problems × 1 solution per model",
    )
    parser.add_argument(
        "--fallback_prompt",
        action="store_true",
        help="Force use of PTRUE_PROMPT_FALLBACK instead of primary prompt",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point. Exit codes: 0=gate PASS, 1=gate FAIL, 2=runtime error."""
    try:
        args = parse_args()

        hm1_dir = Path(args.hm1_results_dir)
        hm2_dir = Path(args.hm2_results_dir)
        output_dir = Path(args.output_dir)
        figures_dir = Path(args.figures_dir)

        output_dir.mkdir(parents=True, exist_ok=True)
        figures_dir.mkdir(parents=True, exist_ok=True)

        prompt_template = PTRUE_PROMPT_FALLBACK if args.fallback_prompt else PTRUE_PROMPT_TEMPLATE
        logger.info(f"Using {'fallback' if args.fallback_prompt else 'primary'} prompt template")

        # ── Step 1: Load data ──────────────────────────────────────────────────
        logger.info("Loading tier assignments...")
        tier_df = load_tier_assignments(hm2_dir)
        tier_df = filter_hard_easy_tiers(tier_df)
        logger.info(f"Filtered tier_df: {len(tier_df)} rows")

        logger.info("Loading EvalPlus problems...")
        problems = load_evalplus_problems()

        logger.info("Loading solutions from h-e1/m-1 results...")
        all_solutions: dict[str, dict[str, list[dict]]] = {}
        for model_id in MODEL_IDS:
            model_short = MODEL_SHORT_NAMES[model_id]
            try:
                all_solutions[model_short] = load_solutions_jsonl(hm1_dir, model_short)
            except FileNotFoundError as e:
                logger.error(f"Solutions not found for {model_short}: {e}")
                return 2

        # ── Step 2: Build pair iterator ────────────────────────────────────────
        pairs = build_pair_iterator(tier_df, all_solutions, problems)
        logger.info(f"Total pairs: {len(pairs)}")

        # Smoke test: subsample
        if args.smoke_test:
            logger.info("SMOKE TEST mode: using 2 problems × 1 solution per model")
            smoke_pairs = []
            per_model_count: dict[str, int] = {}
            seen_problems: set[str] = set()
            for p in pairs:
                m = p["model_short"]
                if len(seen_problems) < 2 or p["task_id"] in seen_problems:
                    if per_model_count.get(m, 0) < 2 and p["sol_idx"] == 0:
                        smoke_pairs.append(p)
                        per_model_count[m] = per_model_count.get(m, 0) + 1
                        seen_problems.add(p["task_id"])
            pairs = smoke_pairs
            logger.info(f"Smoke test pairs: {len(pairs)}")

        # ── Step 3: Per-model P(True) inference ────────────────────────────────
        all_results: dict[str, dict] = {}  # model_short → {task_id: {tier, confidence_scores, ...}}
        confidence_scores_by_model: dict[str, list[float]] = {}
        correctness_by_model: dict[str, list[int]] = {}
        tiers_by_model: dict[str, list[str]] = {}

        for model_id in MODEL_IDS:
            model_short = MODEL_SHORT_NAMES[model_id]
            model_pairs = [p for p in pairs if p["model_short"] == model_short]
            if not model_pairs:
                logger.warning(f"No pairs for {model_short}")
                continue

            checkpoint_path = output_dir / f"ptrue_checkpoint_{model_short}.json"
            logger.info(f"Running inference for {model_short}: {len(model_pairs)} pairs")

            results = run_ptrue_inference_for_model(
                model_id=model_id,
                pairs=model_pairs,
                device=args.device,
                checkpoint_path=checkpoint_path,
                prompt_template=prompt_template,
            )
            all_results[model_short] = results

            # Aggregate confidence scores
            all_c = []
            all_corr = []
            all_tiers = []
            for task_data in results.values():
                all_c.extend(task_data.get("confidence_scores", []))
                all_corr.extend(task_data.get("correctness_labels", []))
                tier = task_data.get("tier", "unknown")
                all_tiers.extend([tier] * len(task_data.get("confidence_scores", [])))

            confidence_scores_by_model[model_short] = all_c
            correctness_by_model[model_short] = all_corr
            tiers_by_model[model_short] = all_tiers

        # ── Step 4: Mechanism verification ────────────────────────────────────
        out_logits_sample = list(_last_out_logits_sample)
        mechanism_ok, indicators = verify_ptrue_mechanism(confidence_scores_by_model, out_logits_sample)
        logger.info(f"Mechanism indicators: {indicators}")

        # ── Step 5: Gate evaluation ────────────────────────────────────────────
        gate_metrics = compute_gate_metrics(confidence_scores_by_model)
        gate_pass, gate_detail = evaluate_gate(gate_metrics, STD_GATE_THRESHOLD)
        logger.info(f"Gate result: {'PASS' if gate_pass else 'FAIL'}")
        logger.info(f"Gate detail: {gate_detail}")

        # ── Step 6: Fallback prompt retry (if gate FAIL) ───────────────────────
        if not gate_pass and not args.fallback_prompt:
            logger.warning("Gate FAIL — retrying with fallback prompt (FR-9)")
            confidence_scores_fallback: dict[str, list[float]] = {}
            correctness_fallback: dict[str, list[int]] = {}
            tiers_fallback: dict[str, list[str]] = {}

            for model_id in MODEL_IDS:
                model_short = MODEL_SHORT_NAMES[model_id]
                model_pairs = [p for p in pairs if p["model_short"] == model_short]
                if not model_pairs:
                    continue

                fallback_checkpoint = output_dir / f"ptrue_checkpoint_{model_short}.fallback.json"
                results_fb = run_ptrue_inference_for_model(
                    model_id=model_id,
                    pairs=model_pairs,
                    device=args.device,
                    checkpoint_path=fallback_checkpoint,
                    prompt_template=PTRUE_PROMPT_FALLBACK,
                )
                all_c_fb = []
                all_corr_fb = []
                all_tiers_fb = []
                for task_data in results_fb.values():
                    all_c_fb.extend(task_data.get("confidence_scores", []))
                    all_corr_fb.extend(task_data.get("correctness_labels", []))
                    tier = task_data.get("tier", "unknown")
                    all_tiers_fb.extend([tier] * len(task_data.get("confidence_scores", [])))

                confidence_scores_fallback[model_short] = all_c_fb
                correctness_fallback[model_short] = all_corr_fb
                tiers_fallback[model_short] = all_tiers_fb

            gate_metrics_fb = compute_gate_metrics(confidence_scores_fallback)
            gate_pass_fb, gate_detail_fb = evaluate_gate(gate_metrics_fb)
            logger.info(f"Fallback gate result: {'PASS' if gate_pass_fb else 'FAIL'}")

            if gate_pass_fb:
                # Use fallback results
                logger.info("Using fallback prompt results (gate PASS)")
                confidence_scores_by_model = confidence_scores_fallback
                correctness_by_model = correctness_fallback
                tiers_by_model = tiers_fallback
                gate_metrics = gate_metrics_fb
                gate_pass = gate_pass_fb
                gate_detail = gate_detail_fb

        # ── Step 7: Secondary metrics ──────────────────────────────────────────
        secondary_metrics = compute_secondary_metrics(
            confidence_scores_by_model,
            correctness_by_model,
            tiers_by_model,
        )

        # Warn if confidence range narrower than expected
        for model_short, metrics in secondary_metrics.items():
            if metrics:
                min_c = metrics.get("min_c", 0)
                max_c = metrics.get("max_c", 1)
                if not (0.2 <= min_c and max_c >= 0.9):
                    logger.warning(
                        f"{model_short}: c range [{min_c:.3f}, {max_c:.3f}] "
                        f"narrower than expected [0.2, 0.9]"
                    )

        # ── Step 8: Save results ───────────────────────────────────────────────
        # Save raw confidence scores
        confidence_scores_path = output_dir / CONFIDENCE_SCORES_FILENAME
        with open(confidence_scores_path, "w") as f:
            json.dump(
                {
                    "confidence_scores_by_model": confidence_scores_by_model,
                    "correctness_by_model": correctness_by_model,
                    "tiers_by_model": tiers_by_model,
                    "per_task_results": {
                        model_short: {
                            task_id: {
                                "tier": data["tier"],
                                "pass_at_1": data["pass_at_1"],
                                "confidence_scores": data["confidence_scores"],
                                "correctness_labels": data["correctness_labels"],
                            }
                            for task_id, data in model_results.items()
                        }
                        for model_short, model_results in all_results.items()
                    }
                },
                f, indent=2,
            )
        logger.info(f"Saved confidence scores: {confidence_scores_path}")

        # Save verified results (FR-10.1)
        verified_results = build_verified_results(gate_metrics, gate_pass, gate_detail, secondary_metrics)
        verified_path = output_dir / VERIFIED_RESULTS_FILENAME
        with open(verified_path, "w") as f:
            json.dump(verified_results, f, indent=2)
        logger.info(f"Saved verified results: {verified_path}")

        # ── Step 9: Generate figures ───────────────────────────────────────────
        fig_cfg = FigureConfig()
        plot_gate_check(gate_metrics, STD_GATE_THRESHOLD, figures_dir / fig_cfg.fig1_filename)
        plot_c_histograms(confidence_scores_by_model, figures_dir / fig_cfg.fig2_filename)
        plot_c_vs_pass_at_1(confidence_scores_by_model, correctness_by_model, figures_dir / fig_cfg.fig3_filename)

        # Build confidence_by_model_tier for Fig 4
        confidence_by_model_tier: dict[str, dict[str, list[float]]] = {}
        for model_short in confidence_scores_by_model:
            scores = confidence_scores_by_model[model_short]
            tiers = tiers_by_model.get(model_short, [])
            confidence_by_model_tier[model_short] = {
                "hard": [s for s, t in zip(scores, tiers) if t == "hard"],
                "easy": [s for s, t in zip(scores, tiers) if t == "easy"],
            }
        plot_c_by_tier(confidence_by_model_tier, figures_dir / fig_cfg.fig4_filename)
        plot_c_cdf(confidence_scores_by_model, figures_dir / fig_cfg.fig5_filename)
        logger.info("All 5 figures generated")

        # ── Summary ────────────────────────────────────────────────────────────
        logger.info("=" * 60)
        logger.info("H-M3 EXPERIMENT COMPLETE")
        logger.info(f"Gate (MUST_WORK): {'PASS ✓' if gate_pass else 'FAIL ✗'}")
        for model_short, m in gate_metrics.items():
            logger.info(
                f"  {model_short}: std(c)={m['std_c']:.4f} "
                f"({'PASS' if m['gate_pass'] else 'FAIL'})"
            )
        logger.info("=" * 60)

        return 0 if gate_pass else 1

    except Exception as e:
        logger.exception(f"Runtime error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
