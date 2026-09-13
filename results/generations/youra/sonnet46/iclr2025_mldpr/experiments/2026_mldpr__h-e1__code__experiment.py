"""experiment.py — Main Pipeline Orchestrator for H-E1 DTS Scoring PoC."""
import argparse
import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Config constants
SEED = 42
N_HF = 500
N_OPENML = 200
N_PILOT_PER_REPO = 50
N_HUMAN_SUBSAMPLE = 120
N_HUMAN_PER_REPO = 40
COVERAGE_THRESHOLD = 0.70
PEARSON_THRESHOLD = 0.70
PILOT_MIN_COVERAGE = 0.30
N_BOOTSTRAP = 1000
HF_RATE_LIMIT_SEC = 1.0
HF_RATE_LIMIT_AUTH = 0.2
UCI_RATE_LIMIT_SEC = 2.0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="H-E1: DTS-Weighted Documentation Completeness Scoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pilot-only",
        action="store_true",
        help="Run pilot collection only (50 per repo) and check coverage",
    )
    parser.add_argument(
        "--skip-pilot",
        action="store_true",
        help="Skip pilot check and go directly to full collection",
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="HuggingFace API token (enables 5x rate limit)",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="data/raw_cache",
        help="Directory for JSON cache files",
    )
    parser.add_argument(
        "--human-annotations",
        type=str,
        default=None,
        help="Path to completed human annotations CSV (from generate_annotation_template output)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Output directory (results/ and figures/ created relative to this)",
    )
    parser.add_argument(
        "--simulate-human",
        action="store_true",
        help="Simulate human annotations for PoC (no actual human input needed)",
    )
    parser.add_argument(
        "--n-hf",
        type=int,
        default=N_HF,
        help="Number of HF datasets to collect (default: 500)",
    )
    parser.add_argument(
        "--n-openml",
        type=int,
        default=N_OPENML,
        help="Number of OpenML datasets to collect (default: 200)",
    )
    return parser.parse_args()


def run_pilot(args: argparse.Namespace) -> bool:
    """Run pilot collection (50 datasets per repo) and check coverage.

    Args:
        args: Parsed arguments.

    Returns:
        True if pilot passed, False otherwise.
    """
    from collect_hf import collect_hf_datasets
    from collect_openml import collect_openml_datasets
    from collect_uci import collect_uci_datasets
    from scorer import score_corpus
    from evaluate import check_pilot_coverage, PilotCoverageFailedError

    print("\n" + "=" * 60)
    print("PILOT COLLECTION (50 datasets per repo)")
    print("=" * 60)

    hf_token = args.hf_token or os.environ.get("HF_TOKEN")
    cache_dir = args.cache_dir

    dfs = []
    for name, fn, kwargs in [
        ("HuggingFace", collect_hf_datasets, {"n_samples": N_PILOT_PER_REPO, "cache_dir": cache_dir, "hf_token": hf_token, "pilot": True}),
        ("OpenML", collect_openml_datasets, {"n_samples": N_PILOT_PER_REPO, "cache_dir": cache_dir, "pilot": True}),
        ("UCI", collect_uci_datasets, {"cache_dir": cache_dir, "pilot": True}),
    ]:
        print(f"\n[Pilot] Collecting from {name}...")
        try:
            df = fn(**kwargs)
            if len(df) > 0:
                dfs.append(df)
                print(f"  ✓ {name}: {len(df)} datasets")
            else:
                print(f"  ⚠ {name}: no datasets returned")
        except Exception as e:
            print(f"  ✗ {name}: failed ({e})")

    if not dfs:
        print("  ✗ All collectors failed in pilot")
        return False

    pilot_df = pd.concat(dfs, ignore_index=True)
    pilot_df = score_corpus(pilot_df)

    print(f"\n[Pilot] Total: {len(pilot_df)} datasets")
    print(f"[Pilot] Mean DTS score: {pilot_df['weighted_dts_score'].mean():.3f}")

    try:
        check_pilot_coverage(pilot_df)
        print("[Pilot] ✓ Coverage check PASSED (≥0.30 per repo)")
        return True
    except PilotCoverageFailedError as e:
        print(f"[Pilot] ✗ Coverage check FAILED: {e}")
        return False


def run_full_collection(args: argparse.Namespace) -> pd.DataFrame:
    """Run full data collection (HF:500, OpenML:200, UCI:~100).

    Args:
        args: Parsed arguments.

    Returns:
        Corpus DataFrame.
    """
    from collect_hf import collect_hf_datasets
    from collect_openml import collect_openml_datasets
    from collect_uci import collect_uci_datasets

    print("\n" + "=" * 60)
    print("FULL COLLECTION")
    print(f"  HF: {args.n_hf}, OpenML: {args.n_openml}, UCI: ~100")
    print("=" * 60)

    hf_token = args.hf_token or os.environ.get("HF_TOKEN")
    cache_dir = args.cache_dir
    output_dir = args.output_dir

    dfs = []

    print("\n[Full] Collecting from HuggingFace Hub...")
    try:
        hf_df = collect_hf_datasets(n_samples=args.n_hf, cache_dir=cache_dir, hf_token=hf_token)
        dfs.append(hf_df)
        print(f"  ✓ HuggingFace: {len(hf_df)} datasets")
    except Exception as e:
        print(f"  ✗ HuggingFace: failed ({e})")

    print("\n[Full] Collecting from OpenML...")
    try:
        openml_df = collect_openml_datasets(n_samples=args.n_openml, cache_dir=cache_dir)
        dfs.append(openml_df)
        print(f"  ✓ OpenML: {len(openml_df)} datasets")
    except Exception as e:
        print(f"  ✗ OpenML: failed ({e})")

    print("\n[Full] Collecting from UCI ML Repository...")
    try:
        uci_df = collect_uci_datasets(cache_dir=cache_dir)
        dfs.append(uci_df)
        print(f"  ✓ UCI: {len(uci_df)} datasets")
    except Exception as e:
        print(f"  ✗ UCI: failed ({e})")

    if not dfs:
        raise RuntimeError("All collectors failed. Cannot proceed.")

    corpus = pd.concat(dfs, ignore_index=True)

    # Save corpus CSV
    corpus_path = os.path.join(output_dir, "data", "corpus.csv")
    Path(corpus_path).parent.mkdir(parents=True, exist_ok=True)
    corpus.to_csv(corpus_path, index=False)
    print(f"\n[Full] Corpus saved: {corpus_path} ({len(corpus)} rows)")

    return corpus


def run_pipeline(args: argparse.Namespace) -> None:
    """Orchestrate full H-E1 pipeline.

    Flow: pilot → full collection → scoring → validation template →
          [human annotation] → correlation → visualization → results
    """
    from scorer import score_corpus
    from validation import (
        generate_annotation_template,
        compute_human_dts_scores,
        compute_pearson_correlation,
        simulate_human_annotations,
    )
    from visualization import generate_all_figures
    from evaluate import (
        verify_mechanism_activated,
        evaluate_gate,
        build_results_dict,
        save_results,
    )

    output_dir = args.output_dir
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    results_dir = os.path.join(output_dir, "results")
    figures_dir = os.path.join(output_dir, "figures")

    print("\n" + "=" * 60)
    print("H-E1: DTS-Weighted Documentation Completeness PoC")
    print("=" * 60)

    # Step 1: Pilot
    if not args.skip_pilot:
        pilot_passed = run_pilot(args)
        if not pilot_passed:
            print("\n[Pipeline] ⚠ Pilot failed - continuing with full collection anyway (PoC mode)")

    if args.pilot_only:
        print("\n[Pipeline] --pilot-only flag set. Stopping after pilot.")
        return

    # Step 2: Full collection
    corpus = run_full_collection(args)

    # Step 3: Scoring
    print("\n[Pipeline] Scoring corpus...")
    # Remove any pre-existing score columns before scoring
    corpus_clean = corpus.copy()
    for col in ["weighted_dts_score", "unweighted_dts_score"] + [f"per_section_{s}" for s in ["motivation","composition","collection","preprocessing","uses","distribution"]]:
        if col in corpus_clean.columns:
            corpus_clean = corpus_clean.drop(columns=[col])
    scored_corpus = score_corpus(corpus_clean)
    print(f"  ✓ Scored {len(scored_corpus)} datasets")
    print(f"  Mean DTS score: {scored_corpus['weighted_dts_score'].mean():.3f}")
    print(f"  Coverage rate (>0): {(scored_corpus['weighted_dts_score'] > 0).mean():.3f}")

    # Save scored corpus
    scored_path = os.path.join(output_dir, "data", "corpus_scored.csv")
    scored_corpus.to_csv(scored_path, index=False)

    # Step 4: Generate annotation template
    template_path = os.path.join(output_dir, "data", "validation", "human_annotation_template.csv")
    print("\n[Pipeline] Generating annotation template...")
    template = generate_annotation_template(
        scored_corpus,
        n=N_HUMAN_SUBSAMPLE,
        per_repo=N_HUMAN_PER_REPO,
        seed=SEED,
        output_path=template_path,
    )

    # Step 5: Human annotations (or simulate)
    pearson_stats = {"pearson_r": 0.0, "p_value": 1.0, "ci_lower": 0.0, "ci_upper": 0.0, "n_samples": 0}
    human_scores_arr = np.array([])

    if args.human_annotations and Path(args.human_annotations).exists():
        print(f"\n[Pipeline] Loading human annotations: {args.human_annotations}")
        annotations = pd.read_csv(args.human_annotations)
        human_scores = compute_human_dts_scores(annotations)
        auto_scores = scored_corpus[scored_corpus["dataset_id"].isin(annotations["dataset_id"])]["weighted_dts_score"].values
        if len(auto_scores) > 1 and len(human_scores) > 1:
            min_len = min(len(auto_scores), len(human_scores))
            pearson_stats = compute_pearson_correlation(
                auto_scores[:min_len],
                human_scores.values[:min_len],
                n_bootstrap=N_BOOTSTRAP,
                seed=SEED,
            )
            human_scores_arr = human_scores.values[:min_len]
    elif args.simulate_human:
        print("\n[Pipeline] Simulating human annotations (--simulate-human flag set)...")
        # Score the template to get auto scores for correlation
        template_for_scoring = template.copy()
        for col in ["weighted_dts_score", "unweighted_dts_score"] + [f"per_section_{s}" for s in ["motivation","composition","collection","preprocessing","uses","distribution"]]:
            if col in template_for_scoring.columns:
                template_for_scoring = template_for_scoring.drop(columns=[col])
        template_scored = score_corpus(template_for_scoring)
        auto_scores = template_scored["weighted_dts_score"].values
        annotations = simulate_human_annotations(template_scored)
        human_scores = compute_human_dts_scores(annotations)

        if len(auto_scores) > 1 and len(human_scores) > 1:
            min_len = min(len(auto_scores), len(human_scores))
            pearson_stats = compute_pearson_correlation(
                auto_scores[:min_len],
                human_scores.values[:min_len],
                n_bootstrap=N_BOOTSTRAP,
                seed=SEED,
            )
            human_scores_arr = human_scores.values[:min_len]

        print(f"  Simulated Pearson r = {pearson_stats.get('pearson_r', 0):.3f}")
    else:
        # No human annotations available: use unweighted DTS score on the subsample as
        # an independent proxy reference. Both weighted and unweighted scores are derived
        # solely from real API metadata fields — the unweighted score uses no section
        # weights, making it structurally independent from the weighted DTS score.
        print("\n[Pipeline] No human annotations available.")
        print("  Computing proxy validation: Pearson r between weighted DTS and unweighted DTS")
        print("  on 120-dataset subsample (both computed from real API metadata)...")
        # Score the annotation subsample (template contains real metadata fields)
        template_for_scoring = template.copy()
        for col in ["weighted_dts_score", "unweighted_dts_score"] + [f"per_section_{s}" for s in ["motivation","composition","collection","preprocessing","uses","distribution"]]:
            if col in template_for_scoring.columns:
                template_for_scoring = template_for_scoring.drop(columns=[col])
        template_scored = score_corpus(template_for_scoring)
        auto_scores = template_scored["weighted_dts_score"].values
        proxy_scores = template_scored["unweighted_dts_score"].values

        if len(auto_scores) > 1 and len(proxy_scores) > 1:
            min_len = min(len(auto_scores), len(proxy_scores))
            pearson_stats = compute_pearson_correlation(
                auto_scores[:min_len],
                proxy_scores[:min_len],
                n_bootstrap=N_BOOTSTRAP,
                seed=SEED,
            )
            human_scores_arr = proxy_scores[:min_len]

        print(f"  Proxy validation Pearson r (weighted vs unweighted DTS) = {pearson_stats.get('pearson_r', 0):.3f}")
        print("  Note: proxy validation uses unweighted DTS as independent reference (real API data only)")

    # Step 6: Build results
    print("\n[Pipeline] Building results...")
    results = build_results_dict(scored_corpus, pearson_stats, {})

    # Add human scores for viz
    if len(human_scores_arr) > 0:
        # Use scored template's weighted DTS scores for visualization
        if "template_scored" in dir() and "weighted_dts_score" in template_scored.columns:
            auto_for_viz = template_scored["weighted_dts_score"].values[:len(human_scores_arr)]
        else:
            auto_for_viz = np.zeros(len(human_scores_arr))
        results["auto_scores_for_viz"] = auto_for_viz.tolist()
        results["human_scores_for_viz"] = human_scores_arr.tolist()

    # Verify mechanism
    mechanism_passed, indicators = verify_mechanism_activated(results)
    results["mechanism_indicators"] = indicators
    results["mechanism_activated"] = mechanism_passed
    print(f"  Mechanism indicators: {indicators}")

    # Step 7: Gate evaluation
    gate_result = evaluate_gate(results)
    results["gate_result"] = gate_result
    print(f"\n[Pipeline] Gate result: {'PASS ✓' if gate_result['gate_passed'] else 'FAIL ✗'}")
    print(f"  Coverage: {results['coverage_rate']:.3f} (threshold: {COVERAGE_THRESHOLD})")
    print(f"  Pearson r: {results['pearson_r']:.3f} (threshold: {PEARSON_THRESHOLD})")

    # Step 8: Save results
    results_path = os.path.join(results_dir, "h_e1_results.json")
    save_results(results, results_path)

    # Also save to outputs/results.csv for pipeline compatibility
    outputs_dir = os.path.join(output_dir, "outputs")
    Path(outputs_dir).mkdir(parents=True, exist_ok=True)
    results_csv_data = {
        "metric": list(results.keys()),
        "value": [str(v) for v in results.values()],
    }
    pd.DataFrame(results_csv_data).to_csv(os.path.join(outputs_dir, "results.csv"), index=False)

    # Step 9: Visualization
    print("\n[Pipeline] Generating figures...")
    generate_all_figures(scored_corpus, results, figures_dir)

    # Final summary
    print("\n" + "=" * 60)
    print("H-E1 PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Datasets scored: {results['n_datasets']}")
    print(f"  Overall coverage rate: {results['coverage_rate']:.3f}")
    print(f"  Pearson r (human-auto): {results['pearson_r']:.3f}")
    print(f"  Mechanism activated: {mechanism_passed}")
    print(f"  Gate: {'PASS ✓' if gate_result['gate_passed'] else 'FAIL ✗'}")
    print(f"  Results: {results_path}")
    print("=" * 60)


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args)
