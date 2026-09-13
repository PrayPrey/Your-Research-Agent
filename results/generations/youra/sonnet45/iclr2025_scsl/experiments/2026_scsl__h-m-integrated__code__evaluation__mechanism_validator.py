"""Mechanism validation functions for M1/M2/M3 gate checks."""

import sys
from pathlib import Path
import numpy as np
import torch
from typing import Dict, Any, List, Tuple
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score, silhouette_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

# Add h-e1 to path
h_e1_path = Path(__file__).parent.parent.parent.parent / 'h-e1' / 'code'
sys.path.insert(0, str(h_e1_path))


def validate_m1(
    embeddings: np.ndarray,
    groups: np.ndarray,
    ami_threshold: float = 0.4,
    silhouette_threshold: float = 0.3
) -> Dict[str, Any]:
    """Validate M1: InfoNCE creates high AMI spurious clusters.

    Args:
        embeddings: Embeddings from SimCLR [N, 2048]
        groups: True group labels [N]
        ami_threshold: Threshold for AMI (default: 0.4)
        silhouette_threshold: Threshold for silhouette score (default: 0.3)

    Returns:
        Dictionary with validation results
    """
    # Run k-means clustering
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings)

    # Compute AMI
    ami_score = adjusted_mutual_info_score(groups, cluster_labels)

    # Compute Silhouette score
    silhouette = silhouette_score(embeddings, cluster_labels)

    # Check gate condition
    ami_pass = ami_score >= ami_threshold
    silhouette_pass = silhouette >= silhouette_threshold

    return {
        'ami_score': float(ami_score),
        'silhouette_score': float(silhouette),
        'ami_threshold': ami_threshold,
        'silhouette_threshold': silhouette_threshold,
        'ami_pass': ami_pass,
        'silhouette_pass': silhouette_pass,
        'gate_pass': ami_pass,  # Primary condition
        'cluster_labels': cluster_labels
    }


def validate_m2(
    ami_values: List[float],
    delta_wga_values: List[float],
    ami_threshold: float = 0.4,
    delta_wga_threshold: float = 2.0,
    pvalue_threshold: float = 0.05
) -> Dict[str, Any]:
    """Validate M2: AMI predicts cluster-balanced retraining efficacy.

    Args:
        ami_values: List of AMI values across checkpoints
        delta_wga_values: List of ΔWGA improvements across checkpoints
        ami_threshold: Threshold for high AMI (default: 0.4)
        delta_wga_threshold: Threshold for improvement in pp (default: 2.0)
        pvalue_threshold: Threshold for statistical significance (default: 0.05)

    Returns:
        Dictionary with validation results
    """
    ami_arr = np.array(ami_values)
    delta_wga_arr = np.array(delta_wga_values)

    # Compute Pearson correlation
    correlation, pvalue = stats.pearsonr(ami_arr, delta_wga_arr)

    # Stratified analysis: high AMI vs low AMI
    high_ami_mask = ami_arr >= ami_threshold
    low_ami_mask = ami_arr < 0.3

    if high_ami_mask.sum() > 0:
        high_ami_mean_delta = delta_wga_arr[high_ami_mask].mean()
    else:
        high_ami_mean_delta = 0.0

    if low_ami_mask.sum() > 0:
        low_ami_mean_delta = delta_wga_arr[low_ami_mask].mean()
    else:
        low_ami_mean_delta = 0.0

    # Check gate conditions
    correlation_pass = (pvalue < pvalue_threshold) and (correlation > 0)
    stratified_pass = high_ami_mean_delta >= delta_wga_threshold

    return {
        'correlation': float(correlation),
        'pvalue': float(pvalue),
        'pvalue_threshold': pvalue_threshold,
        'high_ami_mean_delta_wga': float(high_ami_mean_delta),
        'low_ami_mean_delta_wga': float(low_ami_mean_delta),
        'delta_wga_threshold': delta_wga_threshold,
        'correlation_pass': correlation_pass,
        'stratified_pass': stratified_pass,
        'gate_pass': correlation_pass and stratified_pass
    }


def validate_m3(
    ami_simclr: float,
    ami_lassl: float,
    auc_simclr: float,
    auc_lassl: float,
    reduction_threshold: float = 0.3,
    auc_threshold: float = 0.05
) -> Dict[str, Any]:
    """Validate M3: LA-SSL disperses clusters while preserving separability.

    Args:
        ami_simclr: AMI for SimCLR at epoch 100
        ami_lassl: AMI for LA-SSL at epoch 100
        auc_simclr: Linear separability AUC for SimCLR
        auc_lassl: Linear separability AUC for LA-SSL
        reduction_threshold: Threshold for AMI reduction (default: 0.3 = 30%)
        auc_threshold: Threshold for AUC preservation (default: 0.05)

    Returns:
        Dictionary with validation results
    """
    # Compute AMI reduction percentage
    ami_reduction = (ami_simclr - ami_lassl) / ami_simclr if ami_simclr > 0 else 0.0

    # Compute AUC delta (absolute difference)
    auc_delta = abs(auc_simclr - auc_lassl)

    # Check gate conditions
    reduction_pass = ami_reduction >= reduction_threshold
    auc_pass = auc_delta < auc_threshold

    return {
        'ami_simclr': float(ami_simclr),
        'ami_lassl': float(ami_lassl),
        'ami_reduction': float(ami_reduction),
        'reduction_threshold': reduction_threshold,
        'auc_simclr': float(auc_simclr),
        'auc_lassl': float(auc_lassl),
        'auc_delta': float(auc_delta),
        'auc_threshold': auc_threshold,
        'reduction_pass': reduction_pass,
        'auc_pass': auc_pass,
        'gate_pass': reduction_pass and auc_pass
    }


def compute_ami_evolution(
    checkpoints: List[str],
    embeddings_list: List[np.ndarray],
    groups: np.ndarray
) -> List[Tuple[int, float]]:
    """Compute AMI evolution across training epochs.

    Args:
        checkpoints: List of checkpoint paths (e.g., 'epoch_10.pt')
        embeddings_list: List of embeddings for each checkpoint [N, 2048]
        groups: True group labels [N]

    Returns:
        List of (epoch, AMI) tuples
    """
    ami_evolution = []

    for checkpoint_path, embeddings in zip(checkpoints, embeddings_list):
        # Extract epoch number from checkpoint name
        epoch = int(checkpoint_path.split('_')[-1].split('.')[0])

        # Compute AMI
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        ami_score = adjusted_mutual_info_score(groups, cluster_labels)

        ami_evolution.append((epoch, float(ami_score)))

    # Sort by epoch
    ami_evolution.sort(key=lambda x: x[0])

    return ami_evolution


def compute_linear_separability(
    embeddings: np.ndarray,
    groups: np.ndarray
) -> float:
    """Compute linear separability using logistic regression AUC.

    Args:
        embeddings: Embeddings [N, 2048]
        groups: Group labels [N] (4 groups)

    Returns:
        Macro-average AUC for multi-class classification
    """
    # Train logistic regression
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(embeddings, groups)

    # Predict probabilities
    probs = clf.predict_proba(embeddings)

    # Compute macro-average AUC (one-vs-rest for each group)
    auc = roc_auc_score(groups, probs, multi_class='ovr', average='macro')

    return float(auc)


def generate_mechanism_report(
    m1_result: Dict,
    m2_result: Dict,
    m3_result: Dict,
    output_path: str
) -> None:
    """Generate mechanism validation report.

    Args:
        m1_result: M1 validation results
        m2_result: M2 validation results
        m3_result: M3 validation results
        output_path: Path to save markdown report
    """
    report = f"""# Mechanism Validation Report: h-m-integrated

## M1: InfoNCE Creates Spurious Clusters

**Gate Type:** MUST_WORK (Primary)

**Results:**
- AMI Score: {m1_result['ami_score']:.4f}
- Silhouette Score: {m1_result['silhouette_score']:.4f}
- Threshold: AMI ≥ {m1_result['ami_threshold']}

**Status:** {'✅ PASS' if m1_result['gate_pass'] else '❌ FAIL'}

---

## M2: Clusterability Predicts Intervention Efficacy

**Gate Type:** MUST_WORK (Primary)

**Results:**
- Pearson Correlation: {m2_result['correlation']:.4f}
- P-value: {m2_result['pvalue']:.6f}
- High-AMI Mean ΔWGA: {m2_result['high_ami_mean_delta_wga']:.2f}pp
- Low-AMI Mean ΔWGA: {m2_result['low_ami_mean_delta_wga']:.2f}pp
- Thresholds: p < {m2_result['pvalue_threshold']}, ΔWGA ≥ {m2_result['delta_wga_threshold']}pp

**Status:** {'✅ PASS' if m2_result['gate_pass'] else '❌ FAIL'}

---

## M3: LA-SSL Disperses Clusters While Preserving Separability

**Gate Type:** Secondary (Can Fail Gracefully)

**Results:**
- AMI Reduction: {m3_result['ami_reduction']*100:.1f}%
- SimCLR AMI: {m3_result['ami_simclr']:.4f}
- LA-SSL AMI: {m3_result['ami_lassl']:.4f}
- AUC Delta: {m3_result['auc_delta']:.4f}
- Thresholds: Reduction ≥ {m3_result['reduction_threshold']*100:.0f}%, ΔAUC < {m3_result['auc_threshold']}

**Status:** {'✅ PASS' if m3_result['gate_pass'] else '❌ FAIL'}

---

## Overall Gate Verdict

**Primary Gates (M1 + M2):** {'✅ PASS' if (m1_result['gate_pass'] and m2_result['gate_pass']) else '❌ FAIL'}

**Secondary Gate (M3):** {'✅ PASS' if m3_result['gate_pass'] else '❌ FAIL'}

**Hypothesis Status:** {'VALIDATED' if (m1_result['gate_pass'] and m2_result['gate_pass']) else 'FAILED'}

---

## Summary

This report validates the 3-step causal mechanism:
- M1: InfoNCE loss creates geometrically separable spurious clusters
- M2: High clusterability predicts cluster-balanced retraining efficacy
- M3: LA-SSL disperses spurious structure while preserving signal

**Note:** M3 is secondary and can fail gracefully. M1+M2 passing is sufficient for hypothesis validation.
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f'Mechanism validation report saved: {output_path}')
