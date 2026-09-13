"""
Main experiment pipeline for h-m2 temporal lead time validation.
Orchestrates all modules and evaluates gate criteria.
"""
import json
from pathlib import Path
from typing import Dict

from citation_fetcher import CitationFetcher, create_mock_citation_data
from adoption_detector import AdoptionDetector
from lead_time_analyzer import LeadTimeAnalyzer
from statistical_validator import StatisticalValidator
from visualizer import TemporalVisualizer
from config import (
    BENCHMARK_SHIFT_PAIRS,
    PRECEDE_FRACTION_TARGET,
    LEAD_TIME_THRESHOLD
)


def run_temporal_validation(output_dir: Path) -> Dict:
    """
    Execute h-m2 temporal lead time validation pipeline.

    Returns:
        Dict with gate evaluation results
    """
    print("=" * 60)
    print("H-M2 TEMPORAL LEAD TIME VALIDATION")
    print("=" * 60)

    output_dir = Path(output_dir)
    data_dir = output_dir / "data"
    results_dir = output_dir / "results"

    # Step 1: Citation data (already cached from setup)
    print("\n[1/6] Loading citation data...")
    fetcher = CitationFetcher()
    papers = ['gpt3', 'vit', 'llama']
    citation_data = {}

    for paper_id in papers:
        cache_file = fetcher.cache_dir / f"{paper_id}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                import pandas as pd
                citation_data[paper_id] = pd.DataFrame(json.load(f))
            print(f"  Loaded {paper_id}: {len(citation_data[paper_id])} months")
        else:
            print(f"  Warning: No citation data for {paper_id}")

    # Step 2: Detect adoption dates
    print("\n[2/6] Detecting adoption dates...")
    detector = AdoptionDetector()
    adoption_dates = {}

    for paper_id, df in citation_data.items():
        adoption_date = detector.detect_adoption_date(df)
        adoption_dates[paper_id] = adoption_date
        print(f"  {paper_id}: {adoption_date}")

    # Save adoption dates
    with open(data_dir / "shift_adoption_dates.json", 'w') as f:
        json.dump(adoption_dates, f, indent=2)

    # Step 3: Compute lead times
    print("\n[3/6] Computing lead times...")
    analyzer = LeadTimeAnalyzer()
    saturation_dates = analyzer.load_saturation_dates()
    lead_times = analyzer.compute_lead_times(saturation_dates, adoption_dates)
    metrics = analyzer.compute_metrics(lead_times)

    print(f"  Precede fraction: {metrics['precede_fraction']:.1%}")
    print(f"  Mean lead time: {metrics['mean_lead_time']:.1f} months")

    # Save lead times
    lead_time_results = {
        'pairs': lead_times,
        'metrics': metrics
    }
    with open(results_dir / "lead_times.json", 'w') as f:
        json.dump(lead_time_results, f, indent=2)

    # Step 4: Statistical validation
    print("\n[4/6] Running statistical tests...")
    validator = StatisticalValidator()

    binomial_result = validator.mcnemar_test(lead_times)
    permutation_result = validator.permutation_baseline(
        saturation_dates, adoption_dates, BENCHMARK_SHIFT_PAIRS
    )
    effect_size = validator.compute_effect_size(lead_times)

    validation_results = {
        'binomial_test': binomial_result,
        'permutation_test': permutation_result,
        'effect_size': effect_size
    }

    with open(results_dir / "statistical_validation.json", 'w') as f:
        json.dump(validation_results, f, indent=2)

    # Step 5: Visualizations
    print("\n[5/6] Generating visualizations...")
    visualizer = TemporalVisualizer()
    visualizer.plot_timeline(lead_times)
    visualizer.plot_lead_time_distribution(lead_times)
    visualizer.plot_citation_curves(citation_data)

    # Step 6: Gate evaluation
    print("\n[6/6] Evaluating gate criteria...")
    gate_result = evaluate_gate(metrics, validation_results)

    return {
        'metrics': metrics,
        'validation': validation_results,
        'gate': gate_result
    }


def evaluate_gate(metrics: Dict, validation: Dict) -> Dict:
    """
    Evaluate SHOULD_WORK gate criteria.

    Gate: SHOULD_WORK
    Primary: Precede fraction ≥60% AND mean lead time >6 months
    Secondary: Statistical significance p<0.05

    Args:
        metrics: Lead time metrics
        validation: Statistical validation results

    Returns:
        Dict with gate pass/fail decision and reasoning
    """
    precede_fraction = metrics['precede_fraction']
    mean_lead = metrics['mean_lead_time']
    p_value = validation['binomial_test']['p_value']

    # Primary criteria
    criterion_p1 = precede_fraction >= PRECEDE_FRACTION_TARGET
    criterion_s1 = mean_lead > LEAD_TIME_THRESHOLD
    criterion_s3 = p_value < 0.05

    gate_pass = criterion_p1 and criterion_s1

    gate_result = {
        'result': 'PASS' if gate_pass else 'FAIL',
        'criteria': {
            'P1_precede_fraction': {
                'value': precede_fraction,
                'target': PRECEDE_FRACTION_TARGET,
                'pass': criterion_p1
            },
            'S1_mean_lead_time': {
                'value': mean_lead,
                'target': LEAD_TIME_THRESHOLD,
                'pass': criterion_s1
            },
            'S3_statistical_significance': {
                'value': p_value,
                'target': 0.05,
                'pass': criterion_s3
            }
        },
        'summary': _generate_gate_summary(
            gate_pass, precede_fraction, mean_lead, p_value
        )
    }

    print(f"\nGate Result: {gate_result['result']}")
    print(f"  P1 Precede fraction: {precede_fraction:.1%} (≥{PRECEDE_FRACTION_TARGET:.0%}): {'✓' if criterion_p1 else '✗'}")
    print(f"  S1 Mean lead time: {mean_lead:.1f}mo (>{LEAD_TIME_THRESHOLD}mo): {'✓' if criterion_s1 else '✗'}")
    print(f"  S3 Statistical significance: p={p_value:.4f} (<0.05): {'✓' if criterion_s3 else '✗'}")

    return gate_result


def _generate_gate_summary(gate_pass: bool, precede_fraction: float,
                           mean_lead: float, p_value: float) -> str:
    """Generate human-readable gate summary."""
    if gate_pass:
        return (
            f"Temporal precedence validated: {precede_fraction:.0%} of saturations "
            f"preceded paradigm shifts by mean {mean_lead:.1f} months. "
            f"Saturation signals are leading indicators of benchmark exhaustion."
        )
    else:
        return (
            f"Gate FAIL: Precede fraction {precede_fraction:.0%} or mean lead time "
            f"{mean_lead:.1f}mo below threshold. Temporal claim refuted."
        )


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent
    results = run_temporal_validation(output_dir)

    # Save final results
    results_file = output_dir / "results" / "experiment_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Experiment complete. Results saved to {results_file}")
    print(f"{'='*60}")
