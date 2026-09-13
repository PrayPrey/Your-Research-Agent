#!/usr/bin/env python3
"""
H-M1 Annotation Consistency Study - Main Experiment Runner
Real annotation study using HH-RLHF dataset with trained annotators
"""

import yaml
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.metrics import cohen_kappa_score
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.loader import load_hh_rlhf_dataset
from data.sampler import stratified_sample

def load_config(config_path="config.yaml"):
    """Load configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_h_e1_annotations():
    """
    Load real human annotations from h-e1 study.
    These are UNTRAINED annotators who achieved κ = 0.498 (fair agreement).
    """
    h_e1_path = Path(__file__).parent.parent.parent / 'h-e1' / 'code' / 'data'

    # Load annotations
    annotations_df = pd.read_csv(h_e1_path / 'annotations.csv')
    final_labels_df = pd.read_csv(h_e1_path / 'final_labels.csv')
    samples_df = pd.read_csv(h_e1_path / 'hh_rlhf_samples.csv')

    # Pivot annotations to get annotator columns
    pivot = annotations_df.pivot(index='sample_id', columns='annotator_id', values='judgment')
    pivot = pivot.astype(int)  # Convert True/False to 1/0

    # Merge with samples to get text (h-e1 uses 'id', annotations use 'sample_id')
    samples_with_annotations = samples_df.merge(
        pivot.reset_index(),
        left_on='id',
        right_on='sample_id',
        how='inner'
    )

    # Get ground truth (final consensus labels)
    ground_truth_dict = dict(zip(final_labels_df['sample_id'], final_labels_df['final_label']))

    return samples_with_annotations, ground_truth_dict


def load_trained_annotator_data():
    """
    Load REAL annotations from trained annotators.

    This experiment requires actual human annotation data collected AFTER
    training annotators with explicit HH-RLHF criteria.

    CRITICAL: This is NOT a simulation. Real annotation studies require:
    1. Recruit 3 annotators with NLP/safety background
    2. Train them with HH-RLHF annotation guidelines (1 hour)
    3. Calibration phase: 50 samples with feedback
    4. Independent annotation: 300 test samples per annotator
    5. Collect judgments via annotation interface

    For PoC purposes, we demonstrate the analysis pipeline using h-e1 data
    as a proxy, but NOTE THIS LIMITATION in validation report.
    """
    # Check for real trained annotation data
    trained_data_path = Path(__file__).parent / 'data' / 'trained_annotations.csv'

    if not trained_data_path.exists():
        print("\n" + "!"*60)
        print("WARNING: Real trained annotator data not found")
        print(f"Expected path: {trained_data_path}")
        print("")
        print("This experiment requires REAL human annotations from trained")
        print("annotators. The current implementation uses h-e1 untrained data")
        print("as a PoC demonstration of the analysis pipeline.")
        print("")
        print("To complete this experiment properly:")
        print("  1. Collect real annotations from 3 trained annotators")
        print("  2. Save to data/trained_annotations.csv")
        print("  3. Re-run experiment with real data")
        print("!"*60 + "\n")
        return None

    # Load real trained annotations
    trained_df = pd.read_csv(trained_data_path)
    print(f"   ✓ Loaded real trained annotations from {trained_data_path}")
    return trained_df


def load_real_annotation_data(config):
    """
    Load REAL human annotations from trained annotators.

    This experiment requires actual trained annotator data. If not available,
    uses h-e1 untrained data as PoC demonstration with clear limitations.
    """
    print("=" * 60)
    print("H-M1: Annotation Consistency Study with Trained Annotators")
    print("=" * 60)

    n_samples = config['experiment']['test_sample_size']
    seed = config['experiment']['seed']

    # Try to load real trained annotator data
    print(f"\n1. Checking for real trained annotator data...")
    trained_data = load_trained_annotator_data()

    if trained_data is not None:
        # Use real trained annotations
        print(f"   ✓ Using REAL trained annotator data")
        # Parse trained data format
        # Expected columns: sample_id, annotator_1, annotator_2, annotator_3, ground_truth
        annotations = trained_data[['annotator_1', 'annotator_2', 'annotator_3']].values.T
        ground_truth = trained_data['ground_truth'].values
        return ground_truth, annotations, trained_data

    # Fallback: Use h-e1 untrained data for PoC demonstration
    print(f"\n   Using h-e1 UNTRAINED data as PoC demonstration (LIMITATION)")
    print(f"   NOTE: This does NOT test the training hypothesis properly")

    print(f"\n2. Loading h-e1 untrained annotations...")
    samples_with_annotations, ground_truth_dict = load_h_e1_annotations()
    print(f"   ✓ Loaded {len(samples_with_annotations)} samples")
    print(f"   ✓ h-e1 baseline: κ = 0.498 (fair agreement, UNTRAINED)")

    # Subsample to target size
    print(f"\n3. Sampling {n_samples} cases...")
    np.random.seed(seed)
    sampled_df = samples_with_annotations.sample(n=min(n_samples, len(samples_with_annotations)),
                                                   random_state=seed)

    # Extract annotations and ground truth
    annotations = sampled_df[[1, 2, 3]].values.T  # (3, n_samples)
    ground_truth = np.array([ground_truth_dict[sid] for sid in sampled_df['sample_id']])

    print(f"   ✓ Sampled {len(sampled_df)} cases")

    # Compute baseline metrics
    k12 = cohen_kappa_score(annotations[0], annotations[1])
    k13 = cohen_kappa_score(annotations[0], annotations[2])
    k23 = cohen_kappa_score(annotations[1], annotations[2])
    avg_kappa = np.mean([k12, k13, k23])

    print(f"\n   UNTRAINED baseline metrics:")
    print(f"   Average κ: {avg_kappa:.3f}")

    # Agreement with ground truth
    for i in range(3):
        agreement = np.mean(annotations[i] == ground_truth)
        print(f"   Annotator {i+1}: {agreement:.1%} agreement with ground truth")

    # Save samples for reference
    output_dir = Path(config['outputs']['data_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    sampled_df.to_csv(output_dir / 'sampled_data.csv', index=False)
    print(f"\n   ✓ Sample data saved to {output_dir / 'sampled_data.csv'}")

    print("\n" + "!"*60)
    print("LIMITATION: Using UNTRAINED h-e1 data, not trained annotators")
    print("Expected result: κ ≈ 0.50 (will likely FAIL gates)")
    print("Proper experiment requires collecting real trained annotations")
    print("!"*60 + "\n")

    return ground_truth, annotations, sampled_df

def compute_inter_annotator_agreement(annotations):
    """Compute pairwise Cohen's kappa"""
    n_annotators = annotations.shape[0]
    kappa_matrix = np.zeros((n_annotators, n_annotators))
    
    pairwise_kappas = []
    for i in range(n_annotators):
        for j in range(i + 1, n_annotators):
            kappa = cohen_kappa_score(annotations[i], annotations[j])
            kappa_matrix[i, j] = kappa
            kappa_matrix[j, i] = kappa
            pairwise_kappas.append(kappa)
        kappa_matrix[i, i] = 1.0
    
    avg_kappa = np.mean(pairwise_kappas)
    return avg_kappa, pairwise_kappas, kappa_matrix

def compute_agreement_with_original(annotations, ground_truth):
    """Compute agreement with ground truth"""
    n_annotators = annotations.shape[0]
    agreements = []
    
    for i in range(n_annotators):
        agreement = np.mean(annotations[i] == ground_truth)
        agreements.append(agreement)
    
    mean_agreement = np.mean(agreements)
    return mean_agreement, agreements

def statistical_test(pairwise_kappas, config):
    """One-sample t-test"""
    h0_threshold = config['statistical_analysis']['h0_threshold']
    alpha = config['statistical_analysis']['alpha']
    
    # H0: κ < 0.60 vs H1: κ ≥ 0.70
    t_stat, p_value = stats.ttest_1samp(pairwise_kappas, h0_threshold, alternative='greater')
    
    mean_kappa = np.mean(pairwise_kappas)
    ci_lower, ci_upper = stats.t.interval(0.95, len(pairwise_kappas)-1,
                                          loc=mean_kappa,
                                          scale=stats.sem(pairwise_kappas))
    
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'mean_kappa': mean_kappa,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper
    }

def gate_decision(avg_kappa, avg_agreement, p_value, config):
    """Determine gate result"""
    kappa_threshold = config['gates']['primary_kappa_threshold']
    agreement_threshold = config['gates']['secondary_agreement_threshold']
    alpha = config['gates']['alpha']
    
    primary_pass = (avg_kappa >= kappa_threshold) and (p_value < alpha)
    secondary_pass = (avg_agreement >= agreement_threshold)
    
    if primary_pass and secondary_pass:
        return "PASS"
    elif primary_pass or secondary_pass:
        return "PARTIAL"
    else:
        return "FAIL"

def generate_visualizations(kappa_matrix, agreements, avg_kappa, avg_agreement, config):
    """Generate required figures"""
    output_dir = Path(config['outputs']['figures_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Figure 1: Gate metrics comparison
    fig, ax = plt.subplots(figsize=(8, 6))
    metrics = ['Cohen\'s κ', 'Agreement Rate']
    actual = [avg_kappa, avg_agreement]
    target = [config['gates']['primary_kappa_threshold'], 
              config['gates']['secondary_agreement_threshold']]
    
    x = np.arange(len(metrics))
    width = 0.35
    ax.bar(x - width/2, target, width, label='Target', alpha=0.7)
    ax.bar(x + width/2, actual, width, label='Actual', alpha=0.7)
    ax.set_ylabel('Value')
    ax.set_title('Gate Metrics: Target vs Actual')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.axhline(y=0.70, color='r', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'gate_metrics.png', dpi=150)
    plt.close()
    
    # Figure 2: Inter-annotator agreement matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(kappa_matrix, annot=True, fmt='.3f', cmap='RdYlGn', 
                vmin=0, vmax=1, ax=ax, cbar_kws={'label': 'Cohen\'s κ'})
    ax.set_title('Inter-Annotator Agreement Matrix')
    ax.set_xlabel('Annotator')
    ax.set_ylabel('Annotator')
    plt.tight_layout()
    plt.savefig(output_dir / 'inter_annotator_matrix.png', dpi=150)
    plt.close()
    
    # Figure 3: Agreement distribution
    fig, ax = plt.subplots(figsize=(8, 6))
    x = range(1, len(agreements) + 1)
    ax.bar(x, agreements, alpha=0.7)
    ax.axhline(y=config['gates']['secondary_agreement_threshold'], 
               color='r', linestyle='--', label='Threshold (75%)')
    ax.set_xlabel('Annotator')
    ax.set_ylabel('Agreement Rate')
    ax.set_title('Agreement with Original Labels')
    ax.set_ylim([0, 1])
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_dir / 'agreement_distribution.png', dpi=150)
    plt.close()
    
    print(f"✓ Generated 3 figures in {output_dir}/")

def main():
    """Main experiment execution"""
    config = load_config()

    print(f"\nConfiguration:")
    print(f"   Sample size: {config['experiment']['test_sample_size']}")
    print(f"   Annotators: {config['experiment']['n_annotators']}")
    print(f"   Primary gate: κ ≥ {config['gates']['primary_kappa_threshold']}")
    print(f"   Secondary gate: agreement ≥ {config['gates']['secondary_agreement_threshold']}")

    print(f"\nLoading real annotation data from HH-RLHF...")
    ground_truth, annotations, samples_df = load_real_annotation_data(config)
    print(f"\n   ✓ Loaded {len(ground_truth)} samples × {annotations.shape[0]} annotators")
    
    print(f"\n" + "="*60)
    print(f"ANALYSIS: Computing Metrics on Real Data")
    print(f"="*60)

    print(f"\n4. Computing inter-annotator agreement...")
    avg_kappa, pairwise_kappas, kappa_matrix = compute_inter_annotator_agreement(annotations)
    print(f"   Average pairwise κ: {avg_kappa:.3f}")
    print(f"   Pairwise κ values: {[f'{k:.3f}' for k in pairwise_kappas]}")

    print(f"\n5. Computing agreement with original HH-RLHF labels...")
    avg_agreement, agreements = compute_agreement_with_original(annotations, ground_truth)
    print(f"   Mean agreement: {avg_agreement:.3f}")
    print(f"   Per-annotator: {[f'{a:.3f}' for a in agreements]}")

    print(f"\n6. Statistical hypothesis testing...")
    test_results = statistical_test(pairwise_kappas, config)
    print(f"   t-statistic: {test_results['t_statistic']:.3f}")
    print(f"   p-value: {test_results['p_value']:.4f}")
    print(f"   95% CI: [{test_results['ci_lower']:.3f}, {test_results['ci_upper']:.3f}]")

    print(f"\n7. Gate decision...")
    decision = gate_decision(avg_kappa, avg_agreement, test_results['p_value'], config)
    print(f"   Primary gate (κ ≥ 0.70): {'PASS' if avg_kappa >= 0.70 else 'FAIL'}")
    print(f"   Secondary gate (agreement ≥ 0.75): {'PASS' if avg_agreement >= 0.75 else 'FAIL'}")
    print(f"   Overall: {decision}")

    print(f"\n8. Generating visualizations...")
    generate_visualizations(kappa_matrix, agreements, avg_kappa, avg_agreement, config)
    
    # Save results
    results = {
        'experiment': {
            'hypothesis_id': 'h-m1',
            'timestamp': datetime.now().isoformat(),
            'sample_size': config['experiment']['test_sample_size'],
            'n_annotators': config['experiment']['n_annotators']
        },
        'metrics': {
            'avg_kappa': float(avg_kappa),
            'pairwise_kappas': [float(k) for k in pairwise_kappas],
            'avg_agreement': float(avg_agreement),
            'per_annotator_agreement': [float(a) for a in agreements]
        },
        'statistical_test': {
            't_statistic': float(test_results['t_statistic']),
            'p_value': float(test_results['p_value']),
            'ci_lower': float(test_results['ci_lower']),
            'ci_upper': float(test_results['ci_upper'])
        },
        'gate': {
            'decision': decision,
            'primary_threshold': config['gates']['primary_kappa_threshold'],
            'secondary_threshold': config['gates']['secondary_agreement_threshold'],
            'primary_result': 'PASS' if avg_kappa >= 0.70 else 'FAIL',
            'secondary_result': 'PASS' if avg_agreement >= 0.75 else 'FAIL'
        },
        'baseline_comparison': {
            'h_e1_kappa': config['baseline_comparison']['h_e1_kappa'],
            'h_m1_kappa': float(avg_kappa),
            'improvement': float(avg_kappa - config['baseline_comparison']['h_e1_kappa'])
        }
    }
    
    output_file = Path(config['outputs']['results_file'])
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n9. Results saved to {output_file}")
    
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")

    # Check if we used real trained data or fallback
    trained_data_exists = Path(__file__).parent / 'data' / 'trained_annotations.csv'
    if trained_data_exists.exists():
        print(f"Data Source: REAL trained annotator data ({len(ground_truth)} samples)")
    else:
        print(f"Data Source: h-e1 UNTRAINED fallback ({len(ground_truth)} samples)")
        print("LIMITATION: This uses untrained annotators, not trained ones")
        print("Expected κ ≈ 0.50 (fair), NOT substantial agreement")

    print(f"Gate Result: {decision}")
    print(f"Comparison to h-e1 baseline: {results['baseline_comparison']['improvement']:+.3f}")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    main()
