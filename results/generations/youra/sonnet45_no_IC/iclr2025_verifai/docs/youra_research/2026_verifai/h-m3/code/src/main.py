"""Main pipeline for h-m3 constraint inference validation."""

import sys
import json
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from src.data_loader import DataLoader
from src.semantic_encoder import SemanticEncoder
from src.contradiction_detector import ContradictionDetector
from src.ground_truth_validator import GroundTruthValidator
from src.gate_evaluator import GateEvaluator
from src.threshold_tuner import ThresholdTuner
from src.visualizer import Visualizer

def main():
    """Main execution pipeline."""
    print("=" * 60)
    print("H-M3: CONSTRAINT INFERENCE VIA SEMANTIC SIMILARITY")
    print("=" * 60)

    # Initialize configuration
    config = Config()

    print(f"\nTransformer: {Config.SENTENCE_TRANSFORMER_MODEL}")
    print(f"Similarity threshold: {Config.SIMILARITY_THRESHOLD}")
    print(f"Gate: Recall ≥{Config.RECALL_ACCEPTABLE} (target ≥{Config.RECALL_TARGET}), FP <{Config.FP_RATE_LIMIT}")

    # 1. Load h-m2 outputs
    print("\n=== 1. LOADING H-M2 EXTRACTION OUTPUTS ===")
    loader = DataLoader(Config.H_M2_OUTPUT_FOLDER)

    try:
        assumptions = loader.load_assumptions()
        claims = loader.load_claims()
        print(f"✓ Loaded {len(assumptions)} assumptions, {len(claims)} claims")
    except Exception as e:
        print(f"✗ Error loading h-m2 outputs: {e}")
        return 1

    # 2. Filter by phase
    print("\n=== 2. PHASE FILTERING ===")
    early_assumptions = loader.filter_by_phase(assumptions, Config.EARLY_PHASES)
    later_claims = loader.filter_by_phase(claims, Config.LATER_PHASES)
    pairs = loader.create_phase_pairs(early_assumptions, later_claims)

    print(f"✓ Filtered {len(early_assumptions)} early assumptions (Phase {Config.EARLY_PHASES})")
    print(f"✓ Filtered {len(later_claims)} later claims (Phase {Config.LATER_PHASES})")
    print(f"✓ Generated {len(pairs)} assumption-claim pairs")

    if len(early_assumptions) == 0 or len(later_claims) == 0:
        print("✗ No pairs to process (empty assumptions or claims)")
        return 1

    # 3. Semantic encoding
    print("\n=== 3. SEMANTIC ENCODING ===")
    encoder = SemanticEncoder(
        Config.SENTENCE_TRANSFORMER_MODEL
    )

    print("Encoding assumptions and claims...")
    assumption_embeddings, claim_embeddings = encoder.encode_assumptions_and_claims(
        early_assumptions, later_claims
    )
    print(f"✓ Encoded {assumption_embeddings.shape[0]} assumptions → {assumption_embeddings.shape[1]}-dim vectors")
    print(f"✓ Encoded {claim_embeddings.shape[0]} claims → {claim_embeddings.shape[1]}-dim vectors")

    similarity_matrix = encoder.compute_similarity_matrix(
        assumption_embeddings, claim_embeddings
    )
    print(f"✓ Computed similarity matrix: {similarity_matrix.shape}")

    # 4. Contradiction detection
    print(f"\n=== 4. CONTRADICTION DETECTION (threshold <{Config.SIMILARITY_THRESHOLD}) ===")
    detector = ContradictionDetector(Config.SIMILARITY_THRESHOLD)

    contradictions = detector.detect_contradictions(similarity_matrix, pairs)
    detector.save_contradictions(contradictions, config.DETECTED_CONTRADICTIONS_FILE)

    print(f"✓ Detected {len(contradictions)} potential contradictions")
    print(f"✓ Saved to {config.DETECTED_CONTRADICTIONS_FILE}")

    # 5. Ground truth validation
    print("\n=== 5. GROUND TRUTH VALIDATION ===")
    gt_path = config.GROUND_TRUTH_FOLDER / config.KNOWN_FAILURES_FILE
    validator = GroundTruthValidator(gt_path)

    ground_truth = validator.load_ground_truth()
    print(f"✓ Loaded {len(ground_truth)} known failures")

    matches = validator.match_detected_to_ground_truth(contradictions, ground_truth)
    confusion_matrix = validator.compute_confusion_matrix(matches, len(pairs))

    print(f"✓ TP: {confusion_matrix['TP']}, FP: {confusion_matrix['FP']}, FN: {confusion_matrix['FN']}, TN: {confusion_matrix['TN']}")

    # 6. Gate evaluation
    print("\n=== 6. GATE EVALUATION ===")
    evaluator = GateEvaluator(
        Config.RECALL_TARGET,
        Config.RECALL_ACCEPTABLE,
        Config.FP_RATE_LIMIT
    )

    metrics = evaluator.compute_metrics(confusion_matrix)
    gate_status = evaluator.check_gate_condition(metrics)

    print(f"Recall: {metrics['recall']:.3f} (target ≥{Config.RECALL_TARGET}, acceptable ≥{Config.RECALL_ACCEPTABLE})")
    print(f"FP Rate: {metrics['fp_rate']:.3f} (limit <{Config.FP_RATE_LIMIT})")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Gate Status: {gate_status['status']}")
    print(f"Target Met: {gate_status['target_met']}")

    # 7. Threshold tuning (optional)
    tuning_results = None
    if config.ENABLE_THRESHOLD_TUNING:
        print("\n=== 7. THRESHOLD TUNING ===")
        tuner = ThresholdTuner(Config.TUNING_THRESHOLDS)

        tuning_results = tuner.tune_threshold(
            similarity_matrix, pairs, ground_truth, validator, len(pairs)
        )
        optimal = tuner.find_optimal_threshold(tuning_results, Config.FP_RATE_LIMIT)

        print(f"Optimal threshold: {optimal['threshold']} (recall: {optimal['recall']:.3f}, FP: {optimal['fp_rate']:.3f})")

        for result in tuning_results:
            print(f" Threshold {result['threshold']}: recall={result['recall']:.3f}, FP={result['fp_rate']:.3f}")

    # 8. Visualization
    print("\n=== 8. VISUALIZATION ===")
    visualizer = Visualizer(config.FIGURES_FOLDER, Config.FIGURE_DPI)

    results = {
        'metrics': metrics,
        'gate_status': gate_status,
        'contradictions': contradictions,
        'confusion_matrix': confusion_matrix,
        'similarity_matrix': similarity_matrix.cpu().numpy().tolist(),
        'threshold': Config.SIMILARITY_THRESHOLD,
        'tuning_results': tuning_results
    }

    visualizer.generate_all_figures(results)
    print(f"✓ Figures saved to {config.FIGURES_FOLDER}")

    # 9. Save results
    evaluator.save_results(results, config.RESULTS_FILE)
    print(f"✓ Results saved to {config.RESULTS_FILE}")

    # 10. Final summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate: {gate_status['status']}")
    print(f"Recall: {metrics['recall']:.3f}, FP Rate: {metrics['fp_rate']:.3f}")
    print("=" * 60)

    return 0 if gate_status['status'] == 'PASS' else 1

if __name__ == "__main__":
    exit(main())
