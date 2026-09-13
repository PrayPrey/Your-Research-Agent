"""Main experiment orchestration for h-e1."""

import json
from pathlib import Path
from config import get_config
from data.loader import load_hh_rlhf, filter_by_turn_count
from data.preprocessor import parse_conversation
from analysis.reformulation import ReformulationAnalyzer
from analysis.diversity import compute_diversity
from analysis.statistics import report_statistics
from visualization.plots import save_all_figures


def run_experiment():
    """Run end-to-end reformulation slope experiment."""
    config = get_config()

    print("=" * 80)
    print("Experiment: h-e1 - Reformulation Slope Analysis")
    print("=" * 80)

    # ========== ETL Phase ==========
    print("\n[1/5] ETL: Loading and filtering dataset...")
    raw_conversations = load_hh_rlhf(config)
    filtered_conversations = filter_by_turn_count(raw_conversations, config.min_turns)

    print("\n[2/5] ETL: Parsing conversations...")
    conversations = []
    for idx, raw_conv in enumerate(filtered_conversations):
        conv = parse_conversation(raw_conv, idx)
        conversations.append(conv)
    print(f"Parsed {len(conversations)} conversations")

    # ========== Analysis Phase ==========
    print("\n[3/5] Analysis: Computing reformulation slopes...")
    analyzer = ReformulationAnalyzer(config.sbert_model_name)

    slopes = []
    query_diversity_scores = []
    response_diversity_scores = []

    for i, conv in enumerate(conversations):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(conversations)} conversations")

        # Extract queries and responses
        queries = [turn.user_query for turn in conv.turns]
        responses = [turn.ai_response for turn in conv.turns]

        # Compute reformulation slope
        slope = analyzer.compute_reformulation_slope(
            queries,
            config.semantic_threshold,
            config.syntactic_threshold
        )
        slopes.append(slope)

        # Compute diversity
        query_div = compute_diversity(queries)
        response_div = compute_diversity(responses)
        query_diversity_scores.append(query_div)
        response_diversity_scores.append(response_div)

    print(f"\nComputed slopes for {len(slopes)} conversations")

    # ========== Statistical Validation ==========
    print("\n[4/5] Validation: Running statistical tests...")
    stats_report = report_statistics(slopes, config.alpha)

    print("\n" + "=" * 80)
    print("STATISTICAL RESULTS")
    print("=" * 80)
    print(f"Mean Slope:          {stats_report['mean_slope']:.6f}")
    print(f"Median Slope:        {stats_report['median_slope']:.6f}")
    print(f"Std Slope:           {stats_report['std_slope']:.6f}")
    print(f"T-statistic:         {stats_report['t_statistic']:.4f}")
    print(f"P-value:             {stats_report['p_value']:.6f}")
    print(f"Cohen's d:           {stats_report['cohens_d']:.4f}")
    print(f"Significant (α={config.alpha}): {stats_report['significant']}")
    print(f"Negative slopes:     {stats_report['negative_count']}/{stats_report['total_count']} ({stats_report['negative_percentage']:.1f}%)")
    print("=" * 80)

    # ========== Gate Evaluation ==========
    print("\n[GATE EVALUATION]")
    gate_passed = stats_report['mean_slope'] < 0
    print(f"Gate Condition: mean_slope < 0")
    print(f"Actual: {stats_report['mean_slope']:.6f}")
    print(f"GATE RESULT: {'PASS' if gate_passed else 'FAIL'}")

    # ========== Visualization ==========
    print("\n[5/5] Visualization: Generating figures...")
    save_all_figures(
        slopes,
        query_diversity_scores,
        response_diversity_scores,
        config.figures_dir
    )

    # ========== Save Results ==========

    # Convert numpy types to native Python for JSON serialization
    def convert_numpy(obj):
        """Convert numpy types to native Python types."""
        import numpy as np
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        return obj

    results = {
        "hypothesis_id": "h-e1",
        "gate_condition": "mean_slope < 0",
        "gate_result": "PASS" if gate_passed else "FAIL",
        "statistics": convert_numpy(stats_report),
        "sample_size": len(conversations),
        "config": {
            "min_turns": config.min_turns,
            "semantic_threshold": config.semantic_threshold,
            "syntactic_threshold": config.syntactic_threshold,
            "alpha": config.alpha,
            "random_seed": config.random_seed
        }
    }

    output_path = Path(config.output_dir) / "results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)

    return results


if __name__ == "__main__":
    results = run_experiment()
