"""
Main Execution Script for H-M3 Performance Variance Analysis

This is an observational meta-analysis study validating the causal mechanism:
Reduced cross-lab protocol ambiguity → Lower performance variance

DATA SOURCES (REAL DATA ONLY):
1. Papers with Code API: Benchmark metadata and performance results (PRIMARY)
2. H-M2 cached data: variance_results.csv (FALLBACK if available)
3. Artifact metadata: GitHub repos, dataset cards, badges (from H-M1 rubric)
4. Performance variance: CV computed from reported results across independent reproductions

CRITICAL: Mock/synthetic data fallback has been REMOVED per Phase 4 requirements.
If real data is unavailable, the experiment will fail with a clear error message.

IMPLEMENTATION:
- Fetches real benchmark data from Papers with Code API
- Computes coefficient of variation (CV) per benchmark
- Compares CV distributions between high-artifact and low-artifact groups
- Statistical tests: Mann-Whitney U, Cohen's d, Spearman correlation
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from config_m3 import DEFAULT_CONFIG
from data.pwc_collector import PapersWithCodeCollector
from data.real_data_loader import load_real_benchmark_data
from analysis.variance import compute_benchmark_variance, summarize_variance_by_group
from analysis.hypothesis_test import run_primary_analysis, run_secondary_analysis, evaluate_gate_conditions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    config = DEFAULT_CONFIG

    logger.info("="*60)
    logger.info("H-M3 Performance Variance Analysis")
    logger.info("="*60)

    # Create output directories
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    # =========================================================================
    # Step 1: Data Collection (M3-1, M3-2, M3-3)
    # =========================================================================
    logger.info("\n[Step 1] Collecting benchmark data from Papers with Code API...")

    # Option 1: Use cached data from H-M2 (if available)
    h_m2_data_path = "../../h-m2/code/outputs/variance_results.csv"
    if os.path.exists(h_m2_data_path):
        logger.info(f"✓ Using cached data from H-M2: {h_m2_data_path}")
        df = pd.read_csv(h_m2_data_path)

        # Verify required columns
        required_cols = ["benchmark_id", "artifact_count", "cv"]
        if all(col in df.columns for col in required_cols):
            logger.info(f"✓ Loaded {len(df)} benchmarks from H-M2 cache")

            # Re-assign artifact groups based on H-M3 threshold
            df["artifact_group"] = df["artifact_count"].apply(
                lambda x: "high" if x >= config.HIGH_ARTIFACT_THRESHOLD else "low"
            )

            variance_df = df
        else:
            logger.warning("H-M2 data missing required columns, fetching new data...")
            variance_df = None
    else:
        variance_df = None

    # Option 2: Fetch new data from Papers with Code API (REAL DATA REQUIRED)
    if variance_df is None:
        logger.info("Collecting REAL benchmark data...")
        logger.info("NOTE: Mock/synthetic data fallback has been REMOVED per Phase 4 requirements")

        # Try Papers with Code API first
        api_success = False
        try:
            logger.info("[Option 2a] Attempting Papers with Code API...")
            collector = PapersWithCodeCollector(
                year_start=config.YEAR_START,
                year_end=config.YEAR_END
            )

            benchmark_df = collector.collect_dataset(
                target_count=config.TARGET_BENCHMARK_COUNT,
                high_artifact_threshold=config.HIGH_ARTIFACT_THRESHOLD
            )

            if len(benchmark_df) > 0:
                api_success = True
                logger.info(f"✓ API collection successful: {len(benchmark_df)} benchmarks")

                # Save raw data
                raw_data_path = os.path.join(config.OUTPUT_DIR, "benchmark_data.csv")
                benchmark_df.to_csv(raw_data_path, index=False)
                logger.info(f"✓ Raw data saved to: {raw_data_path}")

                # Compute variance
                variance_df = compute_benchmark_variance(
                    benchmark_df,
                    outlier_threshold=config.OUTLIER_THRESHOLD,
                    min_samples=config.MIN_SAMPLES_AFTER_FILTER
                )

        except Exception as e:
            logger.warning(f"Papers with Code API failed: {e}")

        # If API failed, try manually collected real data
        if not api_success:
            logger.info("[Option 2b] Papers with Code API unavailable")
            logger.info("  Attempting to load REAL benchmark data from manually collected sources...")

            try:
                # Load real benchmark data from published papers
                benchmark_df = load_real_benchmark_data()

                if len(benchmark_df) > 0:
                    logger.info(f"✓ Loaded {len(benchmark_df)} real benchmarks from published papers")
                    logger.info(f"  Total real results: {benchmark_df['num_results'].sum()}")
                    logger.info(f"  Data source: real_benchmark_sample.csv (manually curated from publications)")

                    # This data already has CV computed
                    if 'cv' in benchmark_df.columns:
                        variance_df = benchmark_df
                    else:
                        # Compute variance if needed
                        variance_df = compute_benchmark_variance(
                            benchmark_df,
                            outlier_threshold=config.OUTLIER_THRESHOLD,
                            min_samples=config.MIN_SAMPLES_AFTER_FILTER
                        )

                    # Save for reference
                    raw_data_path = os.path.join(config.OUTPUT_DIR, "benchmark_data_real_manual.csv")
                    benchmark_df.to_csv(raw_data_path, index=False)
                    logger.info(f"✓ Real data reference saved to: {raw_data_path}")

                else:
                    raise RuntimeError("Real data loader returned no benchmarks")

            except Exception as e2:
                logger.error("="*60)
                logger.error("CRITICAL ERROR: All real dataset collection methods failed")
                logger.error("="*60)
                logger.error(f"Papers with Code API: Unavailable")
                logger.error(f"Real manual data: {e2}")
                logger.error("")
                logger.error("This experiment requires REAL benchmark data.")
                logger.error("Mock/synthetic data fallback has been REMOVED per Phase 4 requirements.")
                logger.error("")
                logger.error("Attempted sources:")
                logger.error("  1. H-M2 cached data ❌ (not found)")
                logger.error("  2. Papers with Code API ❌ (unavailable)")
                logger.error("  3. Manually collected real data ❌ (failed to load)")
                logger.error("")
                logger.error("See data/REAL_DATA_COLLECTION.md for manual collection instructions")
                logger.error("="*60)
                raise RuntimeError(f"No real dataset available: API={e}, Manual={e2}")

    # Save variance results
    variance_path = os.path.join(config.OUTPUT_DIR, "variance_results.csv")
    variance_df.to_csv(variance_path, index=False)
    logger.info(f"✓ Variance results saved to: {variance_path}")

    # Summarize variance by group
    summary = summarize_variance_by_group(variance_df)
    summary_path = os.path.join(config.OUTPUT_DIR, "variance_summary.csv")
    summary.to_csv(summary_path, index=False)
    logger.info(f"✓ Variance summary saved to: {summary_path}")

    # =========================================================================
    # Step 2: Statistical Analysis (M3-6, M3-7, M3-8)
    # =========================================================================
    logger.info("\n[Step 2] Running statistical hypothesis tests...")

    # Primary analysis
    primary_results = run_primary_analysis(variance_df)

    # Secondary analysis (dose-response)
    secondary_results = run_secondary_analysis(variance_df)

    # =========================================================================
    # Step 3: Gate Evaluation
    # =========================================================================
    logger.info("\n[Step 3] Evaluating gate conditions...")

    gate_results = evaluate_gate_conditions(primary_results, gate_type=config.GATE_TYPE)

    # =========================================================================
    # Step 4: Save Results
    # =========================================================================
    logger.info("\n[Step 4] Saving experiment results...")

    all_results = {
        "hypothesis_id": "h-m3",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "target_count": config.TARGET_BENCHMARK_COUNT,
            "high_artifact_threshold": config.HIGH_ARTIFACT_THRESHOLD,
            "alpha": config.ALPHA,
            "cohens_d_threshold": config.COHENS_D_THRESHOLD
        },
        "data_summary": {
            "total_benchmarks": len(variance_df),
            "high_artifact_count": int((variance_df["artifact_group"] == "high").sum()),
            "low_artifact_count": int((variance_df["artifact_group"] == "low").sum())
        },
        "primary_analysis": primary_results,
        "secondary_analysis": secondary_results,
        "gate_evaluation": gate_results
    }

    # Convert numpy types to native Python types for JSON serialization
    def convert_to_native(obj):
        if isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        return obj

    all_results = convert_to_native(all_results)

    results_path = os.path.join(config.OUTPUT_DIR, "experiment_results.json")
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2)

    logger.info(f"✓ Experiment results saved to: {results_path}")

    # =========================================================================
    # Step 5: Final Summary
    # =========================================================================
    logger.info("\n"+"="*60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("="*60)
    logger.info(f"Total benchmarks: {len(variance_df)}")
    logger.info(f"High-artifact group: {(variance_df['artifact_group'] == 'high').sum()}")
    logger.info(f"Low-artifact group: {(variance_df['artifact_group'] == 'low').sum()}")
    logger.info(f"\nPrimary Results:")
    logger.info(f"  Mann-Whitney p-value: {primary_results['mann_whitney']['p_value']:.4f}")
    logger.info(f"  Cohen's d: {primary_results['cohens_d']['effect_size']:.3f}")
    logger.info(f"\nGate Result: {'PASS' if gate_results['gate_satisfied'] else 'FAIL'}")
    logger.info("="*60)

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
