import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.config import ExperimentConfig
from data.corpus import DatasetCorpus
from api.fetcher import MetadataFetcher
from analysis.coverage import CoverageAnalyzer
from visualization.plots import Visualizer

def main():
    """Execute h-e2 coverage measurement."""
    config = ExperimentConfig()

    # Load corpus
    corpus = DatasetCorpus(config.corpus_path)
    df = corpus.load()

    if not corpus.validate():
        print("ERROR: Corpus validation failed (need 100 NLP + 100 CV)")
        return

    print(f"Loaded {len(df)} datasets ({len(corpus.get_by_domain('NLP'))} NLP, {len(corpus.get_by_domain('CV'))} CV)")

    # Initialize components
    fetcher = MetadataFetcher(
        retry_count=config.retry_count,
        rate_limit=config.rate_limit,
        timeout=config.timeout
    )
    analyzer = CoverageAnalyzer(fetcher)
    visualizer = Visualizer()

    # Measure coverage
    print("\nMeasuring API coverage...")
    results = analyzer.measure_coverage(df)

    # Breakdowns
    domain_breakdown = analyzer.breakdown_by_domain(results['results_df'])
    source_breakdown = analyzer.breakdown_by_source(results['results_df'])

    # Generate plots
    os.makedirs(f"{config.output_dir}/figures", exist_ok=True)
    visualizer.plot_coverage_vs_threshold(
        results['coverage_pct'],
        config.threshold,
        f"{config.output_dir}/figures/coverage_vs_threshold.png"
    )
    visualizer.plot_domain_comparison(
        domain_breakdown['nlp_pct'],
        domain_breakdown['cv_pct'],
        f"{config.output_dir}/figures/domain_comparison.png"
    )
    visualizer.plot_source_breakdown(
        source_breakdown,
        f"{config.output_dir}/figures/source_breakdown.png"
    )

    # Gate check
    gate_passed = results['coverage_pct'] >= config.threshold

    # Save results
    os.makedirs(f"{config.output_dir}/results", exist_ok=True)
    output = {
        "coverage_pct": float(results['coverage_pct']),
        "covered": int(results['covered']),
        "total": int(results['total']),
        "gate_passed": bool(gate_passed),
        "threshold": float(config.threshold),
        "domain_breakdown": {k: float(v) for k, v in domain_breakdown.items()},
        "source_breakdown": {k: int(v) for k, v in source_breakdown.items()}
    }

    with open(f"{config.output_dir}/{config.results_file}", 'w') as f:
        json.dump(output, f, indent=2)

    # Log gate status
    print(f"\n{'='*50}")
    print(f"RESULTS:")
    print(f"  Coverage: {results['coverage_pct']}% ({results['covered']}/{results['total']})")
    print(f"  NLP: {domain_breakdown['nlp_pct']}%")
    print(f"  CV: {domain_breakdown['cv_pct']}%")
    print(f"  PwC only: {source_breakdown['pwc_only']}")
    print(f"  HF only: {source_breakdown['hf_only']}")
    print(f"  Both: {source_breakdown['both']}")
    print(f"  Neither: {source_breakdown['neither']}")
    print(f"\nGATE (≥{config.threshold}%): {'✓ PASS' if gate_passed else '✗ FAIL'}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
