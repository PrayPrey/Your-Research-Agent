"""Main experiment script for H-C1: Edge Case Robustness Validation"""

import sys
import os
import logging
import json
import time
from datetime import datetime
import pandas as pd

# Add h-m3 to path
sys.path.append('../../h-m3/code/src')
sys.path.append('src')

from checkpoint_only_extractor import CheckpointOnlyExtractor
from edge_case_curator import EdgeCaseModelCurator
from classifier_loader import ClassifierLoader
from edge_case_evaluator import EdgeCaseEvaluator
from failure_analyzer import FailureModeAnalyzer

import config_h_c1 as config

# Setup logging
logging.basicConfig(
    level=config.LOGGING_CONFIG['level'],
    format=config.LOGGING_CONFIG['format'],
    datefmt=config.LOGGING_CONFIG['datefmt'],
    handlers=[
        logging.FileHandler(config.OUTPUT_FILES['experiment_log']),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 80)
    logger.info("H-C1: Edge Case Robustness Validation")
    logger.info("=" * 80)

    start_time = time.time()

    # Step 1: Curate edge case models
    logger.info("\n" + "=" * 80)
    logger.info("Step 1: Edge Case Model Curation")
    logger.info("=" * 80)

    curator = EdgeCaseModelCurator(min_models_per_family=config.MIN_MODELS_PER_FAMILY)

    try:
        validated_models = curator.validate_availability(
            config.EDGE_CASE_MODELS,
            config.FALLBACK_MODELS
        )
    except RuntimeError as e:
        logger.error(f"Model availability check failed: {e}")
        return

    # Flatten validated models
    all_edge_models = []
    for family, models in validated_models.items():
        all_edge_models.extend(models)

    # Assign ground truth labels (edge case families)
    edge_case_labels = curator.assign_ground_truth_labels(all_edge_models)
    logger.info(f"Assigned edge case labels for {len(edge_case_labels)} models")

    # Map edge cases to standard families (CNN/Transformer/Hybrid) for evaluation
    edge_to_standard_mapping = {
        'NormFree': 'CNN',  # CNN without normalization layers
        'SENet': 'CNN',  # CNN with squeeze-excitation
        'RegNet': 'CNN',  # Scaled CNN architecture
        'ViT-Extreme': 'Transformer',  # Vision Transformer
        'Unknown': 'Unknown'
    }

    ground_truth_labels = {
        model: edge_to_standard_mapping.get(edge_case_labels[model], 'Unknown')
        for model in all_edge_models
    }
    logger.info("Mapped edge cases to standard families (CNN/Transformer/Hybrid)")

    # Step 2: Load classifier
    logger.info("\n" + "=" * 80)
    logger.info("Step 2: Load Classifier")
    logger.info("=" * 80)

    loader = ClassifierLoader(
        classifier_path=config.PATHS['h_e1_classifier'],
        scaler_path=config.PATHS['h_e1_scaler']
    )

    classifier, scaler = loader.load_or_train()

    # Step 3: Extract features
    logger.info("\n" + "=" * 80)
    logger.info("Step 3: Feature Extraction")
    logger.info("=" * 80)

    extractor = CheckpointOnlyExtractor(cache_dir=config.PATHS['cache_dir'])
    extraction_start = time.time()

    logger.info(f"Extracting features from {len(all_edge_models)} edge case models...")
    result = extractor.extract_batch(all_edge_models)

    extraction_time = time.time() - extraction_start
    logger.info(f"Extraction completed in {extraction_time:.2f}s")

    features_df = result['features']

    # Add edge family labels (both edge case and standard)
    features_df['edge_case_family'] = features_df['model_name'].map(edge_case_labels)
    features_df['edge_family'] = features_df['model_name'].map(ground_truth_labels)

    # Validate NormFree flag
    normfree_models = features_df[features_df['edge_family'] == 'NormFree']
    if len(normfree_models) > 0:
        normfree_flagged = (normfree_models['no_norm_flag'] == 1).all()
        logger.info(f"NormFree validation: all models have no_norm_flag=1? {normfree_flagged}")
        if not normfree_flagged:
            logger.warning("Some NormFree models have no_norm_flag=0. Check labeling.")

    # Save features
    features_df.to_csv(config.OUTPUT_FILES['edge_features_csv'], index=False)
    logger.info(f"Features saved to {config.OUTPUT_FILES['edge_features_csv']}")

    # Step 4: Evaluation
    logger.info("\n" + "=" * 80)
    logger.info("Step 4: Evaluation")
    logger.info("=" * 80)

    evaluator = EdgeCaseEvaluator(classifier, scaler, config.FEATURE_NAMES)

    # Predict
    predictions_df = evaluator.predict_edge_cases(features_df)
    predictions_df.to_csv(config.OUTPUT_FILES['predictions_csv'], index=False)
    logger.info(f"Predictions saved to {config.OUTPUT_FILES['predictions_csv']}")

    # Overall accuracy
    overall_acc = evaluator.compute_overall_accuracy(predictions_df)

    # Per-family accuracy (by edge case family for detailed analysis)
    per_family_acc = {}
    for edge_family in ['NormFree', 'SENet', 'RegNet', 'ViT-Extreme', 'Unknown']:
        family_df = features_df[features_df['edge_case_family'] == edge_family]
        if len(family_df) > 0:
            family_model_names = family_df['model_name'].values
            family_preds = predictions_df[predictions_df['model_name'].isin(family_model_names)]
            n_total = len(family_preds)
            n_correct = family_preds['correct'].sum()
            per_family_acc[edge_family] = {
                'accuracy': n_correct / n_total if n_total > 0 else 0.0,
                'correct': int(n_correct),
                'total': int(n_total)
            }
            logger.info(f"{edge_family}: {per_family_acc[edge_family]['accuracy']:.3f} ({n_correct}/{n_total})")

    # Degradation
    baseline_acc = config.ACCURACY_THRESHOLDS['baseline_expected']
    degradation = baseline_acc - overall_acc['accuracy']
    logger.info(f"Degradation: {degradation:.3f} ({baseline_acc:.3f} - {overall_acc['accuracy']:.3f})")

    # Gate decision
    gate_status, gate_rationale = evaluator.evaluate_gate_decision(
        overall_acc['accuracy'],
        per_family_acc,
        threshold=config.GATE_CRITERIA['P1_overall_accuracy_min'],
        min_passing_families=config.GATE_CRITERIA['P2_passing_families_min']
    )
    logger.info(f"Gate decision: {gate_status}")
    logger.info(f"Rationale: {gate_rationale}")

    # Save accuracy results
    accuracy_results = {
        'overall_edge': overall_acc,
        'per_family': per_family_acc,
        'overall_baseline': {'accuracy': baseline_acc},
        'degradation': degradation,
        'gate_decision': gate_status,
        'gate_rationale': gate_rationale
    }

    with open(config.OUTPUT_FILES['accuracy_by_family_json'], 'w') as f:
        json.dump(accuracy_results, f, indent=2)
    logger.info(f"Accuracy results saved to {config.OUTPUT_FILES['accuracy_by_family_json']}")

    # Step 5: Failure Analysis
    logger.info("\n" + "=" * 80)
    logger.info("Step 5: Failure Analysis")
    logger.info("=" * 80)

    analyzer = FailureModeAnalyzer()

    # Confusion matrix
    analyzer.generate_confusion_matrix(
        predictions_df,
        config.OUTPUT_FILES['confusion_matrix_png']
    )

    # Feature distributions (no baseline for now)
    analyzer.analyze_feature_distributions(
        features_df,
        None,
        config.FEATURE_NAMES,
        config.OUTPUT_FILES['feature_distributions_png']
    )

    # Systematic patterns (need to add edge_case_family to predictions_df)
    predictions_with_edge = predictions_df.copy()
    predictions_with_edge['edge_case_family'] = predictions_with_edge['model_name'].map(
        features_df.set_index('model_name')['edge_case_family']
    )
    systematic_patterns = {}
    for family in ['NormFree', 'SENet', 'RegNet', 'ViT-Extreme', 'Unknown']:
        family_preds = predictions_with_edge[predictions_with_edge['edge_case_family'] == family]
        if len(family_preds) > 0:
            misclassified = family_preds[~family_preds['correct']]
            n_total = len(family_preds)
            n_misclassified = len(misclassified)
            if n_misclassified == 0:
                systematic_patterns[family] = 'No failures'
            elif n_misclassified == n_total:
                common_pred = misclassified['predicted_family'].mode()
                if len(common_pred) > 0:
                    systematic_patterns[family] = f'All {n_misclassified} models misclassified as {common_pred[0]}'
                else:
                    systematic_patterns[family] = f'All {n_misclassified} models misclassified'
            else:
                systematic_patterns[family] = f'{n_misclassified}/{n_total} partial failures'

    # Failure report (use predictions with edge case family)
    misclassified_df = predictions_with_edge[~predictions_with_edge['correct']]
    analyzer.generate_failure_report(
        misclassified_df,
        systematic_patterns,
        config.OUTPUT_FILES['failure_analysis_md']
    )

    # Step 6: Generate validation report
    logger.info("\n" + "=" * 80)
    logger.info("Step 6: Generate Validation Report")
    logger.info("=" * 80)

    total_time = time.time() - start_time

    with open(config.OUTPUT_FILES['validation_report_md'], 'w') as f:
        f.write('# H-C1 Validation Report\n\n')
        f.write(f'**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write(f'**Hypothesis:** Statistical features maintain >70% accuracy on edge cases\n\n')

        f.write('## 1. Executive Summary\n\n')
        f.write(f'- **Overall Accuracy:** {overall_acc["accuracy"]:.1%} ')
        f.write(f'(95% CI: [{overall_acc["ci_lower"]:.1%}, {overall_acc["ci_upper"]:.1%}])\n')
        f.write(f'- **Degradation:** {degradation:.1%} (baseline: {baseline_acc:.1%})\n')
        f.write(f'- **Gate Status:** {gate_status}\n')
        f.write(f'- **Rationale:** {gate_rationale}\n\n')

        f.write('## 2. Results\n\n')
        f.write('### Overall Metrics\n\n')
        f.write(f'- Sample size: {overall_acc["sample_size"]}\n')
        f.write(f'- Correct predictions: {overall_acc["correct"]}\n')
        f.write(f'- Extraction time: {extraction_time:.2f}s\n')
        f.write(f'- Total runtime: {total_time:.2f}s\n\n')

        f.write('### Per-Family Accuracy\n\n')
        f.write('| Family | Accuracy | Correct | Total | Status |\n')
        f.write('|--------|----------|---------|-------|--------|\n')
        threshold = config.GATE_CRITERIA['P1_overall_accuracy_min']
        for family, stats in per_family_acc.items():
            status = 'PASS' if stats['accuracy'] >= threshold else 'FAIL'
            f.write(f'| {family} | {stats["accuracy"]:.1%} | {stats["correct"]} | {stats["total"]} | {status} |\n')
        f.write('\n')

        f.write('## 3. Failure Mode Analysis\n\n')
        f.write(f'See detailed analysis in `{config.OUTPUT_FILES["failure_analysis_md"]}`\n\n')

        f.write('### Key Findings\n\n')
        for family, pattern in systematic_patterns.items():
            f.write(f'- **{family}:** {pattern}\n')
        f.write('\n')

        f.write('## 4. Conclusion\n\n')
        if gate_status == 'PASS':
            f.write('The edge case robustness validation **PASSED** the SHOULD_WORK gate. ')
            f.write('Statistical features generalize to edge case architectures with acceptable degradation.\n\n')
        else:
            f.write('The edge case robustness validation requires **DOCUMENTATION**. ')
            f.write('While some edge cases are handled, systematic failures indicate scope boundaries.\n\n')

        f.write('## 5. Recommendations\n\n')
        if degradation > config.GATE_CRITERIA['degradation_max']:
            f.write(f'- Degradation ({degradation:.1%}) exceeds threshold ({config.GATE_CRITERIA["degradation_max"]:.0%})\n')
        for family, stats in per_family_acc.items():
            if stats['accuracy'] < threshold:
                f.write(f'- {family} accuracy ({stats["accuracy"]:.1%}) below threshold - consider targeted features\n')

    logger.info(f"Validation report saved to {config.OUTPUT_FILES['validation_report_md']}")

    logger.info("\n" + "=" * 80)
    logger.info("H-C1 Experiment Complete")
    logger.info(f"Total time: {total_time:.2f}s")
    logger.info(f"Gate decision: {gate_status}")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
