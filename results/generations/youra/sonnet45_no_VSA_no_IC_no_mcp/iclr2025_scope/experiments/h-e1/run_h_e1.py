"""Main experiment runner (Tasks L-12, L-13, L-14)."""
import sys
import json
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'h-e1'))

from specter_encoder import SPECTEREncoder
from reference_corpus import ReferenceCorpusBuilder
from domain_mapper import DomainMapper
from baseline import random_baseline
from evaluate import Evaluator
from visualize import plot_gate_metrics, plot_confidence_histogram, plot_confusion_matrix


def main():
    """Main experiment orchestration (Task L-13)."""
    print("="*60)
    print("H-E1: SPECTER Domain Mapping Experiment")
    print("="*60)

    # Task L-12: Load minimal input corpus
    data_path = "data/h-e1/minimal_input_corpus.csv"
    print(f"\n[1/9] Loading data from {data_path}")
    df = pd.read_csv(data_path)
    inputs = df['input_text'].tolist()
    labels = df['true_domain'].tolist()
    print(f"  Loaded {len(inputs)} inputs ({len([l for l in labels if l=='NLP'])} NLP, {len([l for l in labels if l=='CV'])} CV)")

    # Initialize encoder
    print("\n[2/9] Initializing SPECTER encoder")
    encoder = SPECTEREncoder()

    # Build or load reference corpus
    print("\n[3/9] Building reference corpus")
    builder = ReferenceCorpusBuilder(encoder)
    ref_embeddings, ref_labels = builder.build(domains=["NLP", "CV"], papers_per_domain=100)
    print(f"  Reference corpus: {ref_embeddings.shape[0]} papers, {ref_embeddings.shape[1]} dims")

    # Train domain mapper
    print("\n[4/9] Training domain mapper")
    mapper = DomainMapper(encoder, n_neighbors=5, confidence_threshold=0.7)
    mapper.fit(ref_embeddings, ref_labels)

    # Baseline predictions
    print("\n[5/9] Running baseline (random)")
    baseline_preds = random_baseline(inputs)

    # Proposed predictions
    print("\n[6/9] Running proposed method (SPECTER+k-NN)")
    proposed_preds, confidences = mapper.predict(inputs)
    print(f"  Predictions: {len(proposed_preds)}, UNKNOWN: {proposed_preds.count('UNKNOWN')}")

    # Evaluate
    print("\n[7/9] Computing metrics")
    evaluator = Evaluator()
    baseline_metrics = evaluator.compute_metrics(labels, baseline_preds)
    proposed_metrics = evaluator.compute_metrics(labels, proposed_preds)

    print(f"  Baseline accuracy: {baseline_metrics['accuracy']:.2%}")
    print(f"  Proposed accuracy: {proposed_metrics['accuracy']:.2%}")

    # Mechanism verification
    test_embeddings = encoder.encode(inputs[:5])  # Sample for verification
    verification = evaluator.verify_mechanism(
        embedding_shape=test_embeddings.shape,
        predictions=proposed_preds,
        baseline_acc=baseline_metrics['accuracy'],
        proposed_acc=proposed_metrics['accuracy']
    )
    print(f"  Mechanism verification: {verification}")

    # Visualizations
    print("\n[8/9] Generating visualizations")
    plot_gate_metrics(baseline_metrics['accuracy'], proposed_metrics['accuracy'], target=0.7)
    plot_confidence_histogram(confidences, threshold=0.7)
    cm = evaluator.get_confusion_matrix(labels, proposed_preds)
    plot_confusion_matrix(cm)

    # Save results (Task L-14)
    print("\n[9/9] Saving results")
    gate_passed = proposed_metrics['accuracy'] >= 0.7
    results = {
        'baseline': baseline_metrics,
        'proposed': proposed_metrics,
        'verification': verification,
        'gate_passed': gate_passed,
        'gate_result': 'PASS' if gate_passed else 'FAIL'
    }

    output_path = "outputs/h-e1/metrics.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved metrics to {output_path}")

    print("\n" + "="*60)
    print(f"EXPERIMENT COMPLETE")
    print(f"  Baseline: {baseline_metrics['accuracy']:.2%}")
    print(f"  Proposed: {proposed_metrics['accuracy']:.2%}")
    print(f"  Gate: {'PASS' if gate_passed else 'FAIL'} (target ≥70%)")
    print(f"  Mechanism: {'ACTIVATED' if verification['all_passed'] else 'FAILED'}")
    print("="*60)


if __name__ == '__main__':
    main()
