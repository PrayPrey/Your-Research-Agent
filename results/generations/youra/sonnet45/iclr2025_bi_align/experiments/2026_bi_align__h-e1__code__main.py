"""Main execution pipeline for H-E1 linguistic marker extraction.

This script orchestrates the complete analysis pipeline:
1. Load HH-RLHF dataset
2. Extract linguistic markers
3. Compute statistics
4. Generate visualizations
5. Evaluate gate condition
6. Save results
"""

import os
import sys
import json
import re
import pandas as pd
import numpy as np
from datetime import datetime

from config import Config
from data_loader import HHRLHFDataLoader
from extractor import LinguisticMarkerExtractor
from analyzer import StatisticalAnalyzer
from visualizer import Visualizer


def main():
    """Main execution pipeline."""
    print("=" * 80)
    print("H-E1: Linguistic Marker Extraction and Analysis")
    print("=" * 80)
    print()

    # Initialize configuration
    config = Config()
    print(f"Configuration:")
    print(f"  Dataset: {config.dataset_name}")
    print(f"  Splits: {config.splits}")
    print(f"  Random seed: {config.random_seed}")
    print(f"  Gate CV threshold: {config.gate_threshold_cv}")
    print(f"  Gate precision threshold: {config.gate_threshold_precision}")
    print()

    # Set random seed
    np.random.seed(config.random_seed)

    # Step 1: Load data
    print("STEP 1: Loading dataset...")
    print("-" * 80)
    loader = HHRLHFDataLoader()
    datasets = loader.load_dataset()

    # Use a sample for PoC validation (10K responses for faster processing)
    print("\n⚠️  Using sample of 10,000 responses for PoC validation")
    print("   (Full dataset: ~339K responses would take hours to process)")
    all_responses = loader.get_all_responses()
    np.random.seed(config.random_seed)
    sample_indices = np.random.choice(len(all_responses), size=min(10000, len(all_responses)), replace=False)
    responses = [all_responses[i] for i in sorted(sample_indices)]
    print(f"   Sampled {len(responses)} responses from {len(all_responses)} total")
    print()

    # Step 2: Extract features
    print("STEP 2: Extracting linguistic markers...")
    print("-" * 80)
    extractor = LinguisticMarkerExtractor(
        spacy_model=config.spacy_model,
        hedging_markers=config.hedging_markers,
        alternative_patterns=config.alternative_patterns
    )

    print(f"Processing {len(responses)} responses...")
    print("Using batch processing for efficiency...")

    # Extract texts for batch processing
    texts = [r['text'] for r in responses]

    # Use spaCy's pipe for efficient batch processing
    print("Running spaCy NLP pipeline in batches...")
    docs = list(extractor.nlp.pipe(texts, batch_size=1000, n_process=1))

    print("Extracting features from processed documents...")
    features_list = []

    for i, (response, doc) in enumerate(zip(responses, docs)):
        # Extract features from pre-processed doc
        word_count = len([token for token in doc if token.is_alpha])

        if word_count == 0:
            modal_freq = hedging_freq = alt_freq = 0.0
        else:
            # Extract modal verbs from doc
            modal_count = len([token for token in doc if token.tag_ == 'MD'])
            modal_freq = (modal_count / word_count) * 100

            # Extract hedging markers
            text_lower = response['text'].lower()
            words = text_lower.split()
            hedging_count = sum(1 for marker in extractor.hedging_markers if marker in words)
            hedging_freq = (hedging_count / word_count) * 100

            # Extract alternative-framing
            alt_count = sum(len(re.findall(pattern, response['text'], re.IGNORECASE))
                           for pattern in extractor.alternative_patterns)
            alt_freq = (alt_count / word_count) * 100

        # Combine with metadata
        combined = {
            **response,
            'modal_freq': modal_freq,
            'hedging_freq': hedging_freq,
            'alt_freq': alt_freq,
            'word_count': word_count
        }
        features_list.append(combined)

        # Progress reporting
        if (i + 1) % 10000 == 0:
            print(f"  Processed {i + 1}/{len(responses)} responses...")

    print(f"✓ Extracted features from {len(features_list)} responses")
    print()

    # Convert to DataFrame
    df = pd.DataFrame(features_list)

    # Step 3: Compute statistics
    print("STEP 3: Computing statistics...")
    print("-" * 80)
    analyzer = StatisticalAnalyzer(random_seed=config.random_seed)

    # Overall statistics for each marker type
    modal_features = df['modal_freq'].values
    hedging_features = df['hedging_freq'].values
    alt_features = df['alt_freq'].values

    modal_stats = analyzer.compute_statistics(modal_features)
    hedging_stats = analyzer.compute_statistics(hedging_features)
    alt_stats = analyzer.compute_statistics(alt_features)

    print(f"Modal Verb Statistics:")
    print(f"  Mean: {modal_stats['mean']:.4f}")
    print(f"  Std: {modal_stats['std']:.4f}")
    print(f"  CV: {modal_stats['cv']:.4f}")
    print()

    print(f"Hedging Marker Statistics:")
    print(f"  Mean: {hedging_stats['mean']:.4f}")
    print(f"  Std: {hedging_stats['std']:.4f}")
    print(f"  CV: {hedging_stats['cv']:.4f}")
    print()

    print(f"Alternative-Framing Statistics:")
    print(f"  Mean: {alt_stats['mean']:.4f}")
    print(f"  Std: {alt_stats['std']:.4f}")
    print(f"  CV: {alt_stats['cv']:.4f}")
    print()

    # Cross-split validation
    print("Cross-split validation...")
    split_features = {}
    for split_name in df['split'].unique():
        split_df = df[df['split'] == split_name]
        split_features[split_name] = split_df['modal_freq'].values

    split_stats = analyzer.cross_split_validation(split_features)

    for split_name, stats in split_stats.items():
        print(f"  {split_name}: CV = {stats['cv']:.4f}")
    print()

    # Estimate precision
    precision = analyzer.estimate_precision(modal_features)
    print(f"Estimated extraction precision: {precision:.2%}")
    print()

    # Step 4: Generate visualizations
    print("STEP 4: Generating visualizations...")
    print("-" * 80)
    visualizer = Visualizer(output_dir=config.figures_dir, dpi=config.dpi)

    # Create figures directory
    os.makedirs(config.figures_dir, exist_ok=True)

    # MANDATORY: Gate metrics plot
    gate_metrics = {
        'modal_cv': modal_stats['cv'],
        'precision': precision
    }
    gate_targets = {
        'modal_cv': config.gate_threshold_cv,
        'precision': config.gate_threshold_precision
    }
    visualizer.plot_gate_metrics(
        gate_metrics,
        gate_targets,
        os.path.join(config.figures_dir, "gate_metrics.png")
    )

    # Optional: Distribution plot
    visualizer.plot_distribution(
        modal_features,
        "Modal Verbs",
        os.path.join(config.figures_dir, "distribution.png")
    )

    # Optional: Split comparison
    visualizer.plot_split_comparison(
        split_features,
        "Modal Verbs",
        os.path.join(config.figures_dir, "split_comparison.png")
    )

    # Optional: Correlation plot
    visualizer.plot_correlation(
        modal_features,
        hedging_features,
        os.path.join(config.figures_dir, "correlation.png")
    )
    print()

    # Step 5: Evaluate gate condition
    print("STEP 5: Evaluating gate condition...")
    print("-" * 80)
    gate_result = analyzer.gate_evaluation(
        cv=modal_stats['cv'],
        precision=precision,
        cv_threshold=config.gate_threshold_cv,
        precision_threshold=config.gate_threshold_precision
    )

    print(f"Gate Evaluation:")
    print(f"  Modal CV: {modal_stats['cv']:.4f} (threshold: {config.gate_threshold_cv})")
    print(f"  Precision: {precision:.4f} (threshold: {config.gate_threshold_precision})")
    print(f"  Result: {'PASS' if gate_result else 'FAIL'}")
    print()

    # Step 6: Save results
    print("STEP 6: Saving results...")
    print("-" * 80)

    # Save features CSV
    features_path = os.path.join(config.output_dir, config.features_file)
    df.to_csv(features_path, index=False)
    print(f"✓ Saved features: {features_path}")

    # Save statistics JSON
    statistics = {
        'hypothesis_id': 'h-e1',
        'timestamp': datetime.now().isoformat(),
        'dataset': {
            'name': config.dataset_name,
            'total_responses': len(responses),
            'splits': {split: len(df[df['split'] == split]) for split in df['split'].unique()}
        },
        'modal_verbs': modal_stats,
        'hedging_markers': hedging_stats,
        'alternative_framing': alt_stats,
        'cross_split_validation': {k: v for k, v in split_stats.items()},
        'precision': float(precision),
        'gate_evaluation': {
            'cv_threshold': config.gate_threshold_cv,
            'precision_threshold': config.gate_threshold_precision,
            'modal_cv': modal_stats['cv'],
            'precision': float(precision),
            'result': 'PASS' if gate_result else 'FAIL'
        }
    }

    stats_path = os.path.join(config.output_dir, config.statistics_file)
    with open(stats_path, 'w') as f:
        json.dump(statistics, f, indent=2)
    print(f"✓ Saved statistics: {stats_path}")
    print()

    # Final summary
    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"Total responses analyzed: {len(responses)}")
    print(f"Modal verb CV: {modal_stats['cv']:.4f}")
    print(f"Extraction precision: {precision:.2%}")
    print(f"Gate result: {'PASS ✓' if gate_result else 'FAIL ✗'}")
    print("=" * 80)

    return 0 if gate_result else 1


if __name__ == "__main__":
    sys.exit(main())
