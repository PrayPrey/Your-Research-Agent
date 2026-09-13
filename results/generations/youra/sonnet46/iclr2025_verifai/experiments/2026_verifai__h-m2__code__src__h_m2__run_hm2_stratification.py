"""H-M2: CLI Orchestrator — Difficulty Tier Stratification & Cross-Model Jaccard Analysis.

Exit codes:
    0: Gate PASS
    1: Gate FAIL (methodology ran but threshold not met)
    2: Runtime error
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_HM1_RESULTS: str = "../../h-m1/results"
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"
RESULTS_FILENAME: str = "stratification_results.json"
TIER_CSV_FILENAME: str = "tier_assignments.csv"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="H-M2: Difficulty Tier Stratification and Cross-Model Jaccard Analysis",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--hm1_results_dir",
        type=str,
        default=DEFAULT_HM1_RESULTS,
        help="Path to h-m1/results/ directory containing pass_at_1_hm1_verified.json",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for stratification_results.json and tier_assignments.csv",
    )
    parser.add_argument(
        "--figures_dir",
        type=str,
        default=DEFAULT_FIGURES_DIR,
        help="Output directory for generated figures",
    )
    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Run in smoke test mode (skip figures)",
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    return parser.parse_args()


def save_stratification_results(results: dict, output_path: Path) -> None:
    """Write stratification_results.json."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Convert sets to sorted lists for JSON serialization
    serializable = _make_serializable(results)
    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)
    logger.info("Results saved: %s", output_path)


def _make_serializable(obj):
    """Recursively convert sets/tuples to JSON-serializable types."""
    if isinstance(obj, set):
        return sorted(obj)
    elif isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_make_serializable(i) for i in obj]
    elif isinstance(obj, float):
        return round(obj, 6)
    return obj


def save_tier_assignments_csv(df, output_path: Path) -> None:
    """Write tier_assignments.csv."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Tier assignments CSV saved: %s (rows=%d)", output_path, len(df))


def format_gate_output(gate_pass: bool, gate_detail: dict) -> str:
    """Format gate result as structured JSON string for stdout."""
    output = {
        "gate_result": "PASS" if gate_pass else "FAIL",
        "gate_type": gate_detail.get("gate_type"),
        "threshold": gate_detail.get("threshold"),
        "max_jaccard": gate_detail.get("max_jaccard"),
        "passing_pairs_count": gate_detail.get("passing_pairs_count"),
        "results": gate_detail.get("results"),
    }
    return json.dumps(output, indent=2)


def main() -> None:
    """Orchestrate: load → tier → jaccard → histogram → gate → visualize → save."""
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Resolve paths
    hm1_results_dir = Path(args.hm1_results_dir)
    output_dir = Path(args.output_dir)
    figures_dir = Path(args.figures_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    try:
        # ── Late imports (avoid import-time matplotlib issues) ──────────────────
        from h_m2.stratify import (
            load_hm1_pass_at_1,
            compute_difficulty_tiers,
            compute_per_benchmark_tiers,
            validate_tier_sizes,
        )
        from h_m2.jaccard import (
            compute_cross_model_jaccard,
            compute_per_benchmark_jaccard,
            compute_consensus_set,
            compute_overlap_counts_by_n_models,
        )
        from h_m2.analyze import (
            compute_histograms,
            build_tier_assignments_df,
        )
        from h_m2.evaluate import (
            evaluate_gate,
            verify_mechanism_activated,
            build_stratification_results,
        )

        # ── Step 1: Load pass@1 data ────────────────────────────────────────────
        logger.info("Loading H-M1 pass@1 data from %s ...", hm1_results_dir)
        pass_at_1_data = load_hm1_pass_at_1(hm1_results_dir)
        n_models = len(pass_at_1_data)
        n_tasks = len(next(iter(pass_at_1_data.values())))
        logger.info("  Loaded %d models × %d tasks", n_models, n_tasks)

        # ── Step 2: Tier stratification ─────────────────────────────────────────
        logger.info("Computing difficulty tiers ...")
        tiers = compute_difficulty_tiers(pass_at_1_data)
        per_benchmark_tiers = compute_per_benchmark_tiers(pass_at_1_data)
        tier_validation = validate_tier_sizes(tiers)
        logger.info("  Tier validation: %d models checked", len(tier_validation))

        # ── Step 3: Jaccard computation ─────────────────────────────────────────
        logger.info("Computing Jaccard similarities ...")
        jaccard_results = compute_cross_model_jaccard(tiers)
        per_benchmark_jaccard = compute_per_benchmark_jaccard(per_benchmark_tiers)
        consensus = compute_consensus_set(tiers)
        overlap_counts = compute_overlap_counts_by_n_models(tiers)
        logger.info("  Computed %d pairs; consensus hard: %d problems",
                    len(jaccard_results), consensus["n"])

        # ── Step 4: Histogram and distribution analysis ─────────────────────────
        logger.info("Computing histograms ...")
        histograms = compute_histograms(pass_at_1_data)
        tier_df = build_tier_assignments_df(pass_at_1_data, tiers)

        # ── Step 5: Gate evaluation ─────────────────────────────────────────────
        logger.info("Evaluating SHOULD_WORK gate ...")
        gate_pass, gate_detail = evaluate_gate(jaccard_results)
        mechanism_activated, mechanism_indicators = verify_mechanism_activated(
            tiers, jaccard_results
        )

        # ── Step 6: Build results payload ───────────────────────────────────────
        results_payload = build_stratification_results(
            pass_at_1_data=pass_at_1_data,
            tiers=tiers,
            per_benchmark_tiers=per_benchmark_tiers,
            jaccard_results=jaccard_results,
            per_benchmark_jaccard=per_benchmark_jaccard,
            consensus=consensus,
            gate_detail=gate_detail,
            mechanism_indicators=mechanism_indicators,
        )

        # ── Step 7: Save results ────────────────────────────────────────────────
        results_path = output_dir / RESULTS_FILENAME
        save_stratification_results(results_payload, results_path)

        tier_csv_path = output_dir / TIER_CSV_FILENAME
        save_tier_assignments_csv(tier_df, tier_csv_path)

        # ── Step 8: Visualization ───────────────────────────────────────────────
        if not args.smoke_test:
            from h_m2.visualize_hm2 import (
                FIG_FILENAMES,
                plot_jaccard_bars,
                plot_pass_at_1_histograms,
                plot_tier_size_summary,
                plot_jaccard_heatmap,
                plot_consensus_hard_pie,
            )
            logger.info("Generating 5 figures ...")

            plot_jaccard_bars(
                jaccard_results,
                figures_dir / FIG_FILENAMES["jaccard_bars"],
            )
            plot_pass_at_1_histograms(
                pass_at_1_data,
                figures_dir / FIG_FILENAMES["histograms"],
            )
            plot_tier_size_summary(
                per_benchmark_tiers,
                figures_dir / FIG_FILENAMES["tier_summary"],
            )
            plot_jaccard_heatmap(
                jaccard_results,
                figures_dir / FIG_FILENAMES["heatmap"],
            )
            plot_consensus_hard_pie(
                overlap_counts,
                figures_dir / FIG_FILENAMES["consensus_pie"],
            )
            logger.info("  All 5 figures saved to %s", figures_dir)

        # ── Step 9: Print gate summary ──────────────────────────────────────────
        gate_summary = format_gate_output(gate_pass, gate_detail)
        print("\n" + "=" * 60)
        print(f"H-M2 STRATIFICATION COMPLETE")
        print("=" * 60)
        print(f"Gate:          {'PASS ✓' if gate_pass else 'FAIL ✗'}")
        print(f"Max Jaccard:   {gate_detail['max_jaccard']:.4f}")
        print(f"Threshold:     {gate_detail['threshold']} (strict >)")
        print(f"Passing pairs: {gate_detail['passing_pairs_count']}/3")
        print(f"CSV rows:      {len(tier_df)} (expected 542)")
        print("=" * 60)
        print("\nGATE JSON:")
        print(gate_summary)

        # Exit 0=PASS, 1=FAIL
        sys.exit(0 if gate_pass else 1)

    except Exception as e:
        logger.error("Runtime error: %s", e, exc_info=True)
        print(json.dumps({"error": str(e), "gate_result": "ERROR"}))
        sys.exit(2)


if __name__ == "__main__":
    main()
