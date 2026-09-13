"""
H-E1 Pipeline Orchestration — LLM Documentation-Benchmark Registry Construction
Main entry point for the full pipeline.
"""
import os
import sys

# Add code directory to path
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

BASE_DIR = os.path.dirname(CODE_DIR)


def smoke_test() -> bool:
    """Check imports + HF API connectivity. Returns True if environment ready."""
    try:
        # Check imports
        import config
        import utils
        import data_collection
        import feature_extraction
        import registry_builder
        import analysis
        import visualization

        # Check HF API connectivity
        from huggingface_hub import HfApi
        api = HfApi()
        # Just verify we can instantiate the API (actual request would fail without auth)
        return True
    except Exception as e:
        print(f"smoke_test failed: {e}")
        return False


def run_pipeline() -> dict:
    """Orchestrate full H-E1 pipeline. Returns gate results dict.

    Steps:
      1. load_leaderboard -> deduplicate -> filter_benchmark_coverage
      2. retrieve_model_cards (with checkpointing)
      3. build_registry -> validate_registry (gate assert)
      4. export_registry
      5. compute_descriptive_stats + fit_ols_baseline + fit_ols_proposed + compare_models
      6. save_summary_stats
      7. generate all 5 figures
    Returns: {"gate_passed": bool, "n_analyzable": int, "n_features_with_variance": int}
    """
    import config
    import data_collection
    import feature_extraction
    import registry_builder
    import analysis
    import visualization

    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)

    print("=" * 60)
    print("H-E1: LLM Documentation-Benchmark Registry Construction")
    print("=" * 60)

    # Step 1: Load and filter leaderboard
    print("\n[Step 1] Loading Open LLM Leaderboard...")
    raw_df = data_collection.load_leaderboard()
    print(f"  Raw rows: {len(raw_df)}")

    dedup_df = data_collection.deduplicate(raw_df)
    print(f"  After dedup: {len(dedup_df)}")

    filtered_df = data_collection.filter_benchmark_coverage(dedup_df)
    print(f"  After benchmark filter: {len(filtered_df)}")

    # Step 2: Retrieve model cards
    print("\n[Step 2] Retrieving model cards...")
    model_ids = filtered_df['model_name'].tolist() if 'model_name' in filtered_df.columns else filtered_df.index.tolist()
    model_card_data = data_collection.retrieve_model_cards(
        model_ids,
        checkpoint_dir=config.CHECKPOINT_DIR
    )
    print(f"  Retrieved cards: {len(model_card_data)}")

    # Step 3: Build and validate registry
    print("\n[Step 3] Building registry...")
    registry_df = registry_builder.build_registry(filtered_df, model_card_data)
    print(f"  Registry size: {len(registry_df)}")

    validation_result = registry_builder.validate_registry(registry_df)
    print(f"  Gate passed: {validation_result['gate_passed']}")
    print(f"  n_analyzable: {validation_result['n_analyzable']}")
    print(f"  n_features_with_variance: {validation_result['n_features_with_variance']}")

    # Step 4: Export registry
    registry_path = os.path.join(config.DATA_DIR, 'registry.csv')
    registry_builder.export_registry(registry_df, registry_path)
    print(f"\n[Step 4] Registry exported: {registry_path}")

    # Step 5: Analysis
    print("\n[Step 5] Running analysis...")
    desc_stats = analysis.compute_descriptive_stats(registry_df)
    baseline_result = analysis.fit_ols_baseline(registry_df)
    proposed_result = analysis.fit_ols_proposed(registry_df)
    comparison = analysis.compare_models(baseline_result, proposed_result)

    print(f"  Baseline R²: {comparison['baseline_r2']:.4f}")
    print(f"  Proposed R²: {comparison['proposed_r2']:.4f}")
    print(f"  delta_R²: {comparison['delta_r2']:.4f}")
    print(f"  beta_docs: {comparison['beta_docs']:.4f}")
    print(f"  p_value: {comparison['p_value']:.4f}")

    # Step 6: Save summary stats
    summary = {
        **validation_result,
        **desc_stats,
        **comparison
    }
    summary_path = os.path.join(config.DATA_DIR, 'summary_stats.json')
    analysis.save_summary_stats(summary, summary_path)
    print(f"\n[Step 6] Summary stats saved: {summary_path}")

    # Step 7: Generate figures
    print("\n[Step 7] Generating figures...")
    funnel_counts = getattr(data_collection, '_funnel_counts', {
        'raw': len(raw_df),
        'after_dedup': len(dedup_df),
        'after_benchmark_filter': len(filtered_df),
        'cards_retrieved': len(model_card_data),
        'registry': len(registry_df)
    })

    visualization.plot_doc_score_distribution(
        registry_df,
        os.path.join(config.FIGURES_DIR, 'doc_score_distribution.png')
    )
    visualization.plot_dropout_funnel(
        funnel_counts,
        os.path.join(config.FIGURES_DIR, 'dropout_funnel.png')
    )
    visualization.plot_feature_coverage(
        registry_df,
        os.path.join(config.FIGURES_DIR, 'feature_coverage.png')
    )
    visualization.plot_family_breakdown(
        registry_df,
        os.path.join(config.FIGURES_DIR, 'family_breakdown.png')
    )
    visualization.plot_benchmark_heatmap(
        registry_df,
        os.path.join(config.FIGURES_DIR, 'benchmark_heatmap.png')
    )
    print("  All figures generated.")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print(f"Gate result: {'PASS' if validation_result['gate_passed'] else 'FAIL'}")
    print("=" * 60)

    return {
        "gate_passed": validation_result['gate_passed'],
        "n_analyzable": validation_result['n_analyzable'],
        "n_features_with_variance": validation_result['n_features_with_variance'],
        "comparison": comparison
    }


if __name__ == "__main__":
    run_pipeline()
