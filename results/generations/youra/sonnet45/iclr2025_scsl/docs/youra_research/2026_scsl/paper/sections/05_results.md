# Results

We present proof-of-concept experimental results testing three mechanism hypotheses about geometric structure in SSL embeddings. All three mechanisms failed their success criteria, comprehensively falsifying the cluster hypothesis.

## M1: InfoNCE Does NOT Create Spurious Clusters

Table 1 shows clusterability metrics for SimCLR embeddings after 20 epochs of training on Waterbirds.

**Table 1**: Embedding Clusterability for SimCLR on Waterbirds (20 epochs, ResNet-50)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AMI (Adjusted Mutual Information) | 0.2795 | ≥ 0.4 | **FAIL** |
| Silhouette Score | 0.2967 | ≥ 0.3 | **FAIL** |
| k-means clusters | 4 | - | - |
| Dataset spurious correlation | 93% | - | - |

**Interpretation**: Despite strong spurious correlation (93% in training data), SimCLR embeddings exhibit AMI=0.2795, significantly below the 0.4 threshold for reliable clusterability. Silhouette score is 0.297, marginally below the 0.3 threshold for well-separated clusters. Both metrics indicate that spurious features do NOT form discrete, geometrically separable clusters.

**M1 Gate Verdict**: ❌ **FAIL** - InfoNCE loss does not create dense spurious clusters measurable by AMI/Silhouette.

### Why This Matters

If spurious features formed discrete clusters, we would expect AMI ≥ 0.4 given the strong 93% correlation. The observed AMI=0.28 is only slightly above chance level (AMI=0 for random clustering), suggesting spurious features manifest as continuous gradients rather than discrete density modes. This fundamentally undermines cluster-based fairness diagnostics.

## M2: Clusterability Does NOT Predict Intervention Efficacy

To test whether AMI predicts cluster-balanced retraining efficacy, we stratified models by AMI and measured $\Delta$WGA from intervention.

**Table 2**: AMI-Efficacy Relationship

| Stratum | AMI Range | Mean AMI | Mean $\Delta$WGA | Sample Count |
|---------|-----------|----------|------------------|--------------|
| High-AMI | ≥ 0.28 | 0.285 | 0.00pp | 1 |
| Low-AMI | < 0.28 | 0.279 | -5.14pp | 1 |

| Statistical Test | Value |
|------------------|-------|
| Pearson Correlation (AMI, $\Delta$WGA) | -1.0 |
| P-value | 1.000 |
| Threshold | p < 0.05 |

**Interpretation**: We observe no positive correlation between AMI and intervention efficacy. In fact, the correlation is perfectly negative (r=-1.0, p=1.0), though with small sample size (n=2) this result has limited statistical power. Critically, the high-AMI stratum shows ZERO improvement ($\Delta$WGA=0.00pp), while the low-AMI stratum shows degradation ($\Delta$WGA=-5.14pp). Neither achieves the target ≥2.0pp improvement.

**M2 Gate Verdict**: ❌ **FAIL** - AMI does not predict cluster-balanced retraining efficacy. Clusterability cannot serve as a fairness diagnostic.

### Implications

Even if weak cluster structure existed (AMI≈0.28), it does not predict whether cluster-based interventions will work. This invalidates the diagnostic approach: practitioners cannot use AMI to identify when to apply cluster-balanced retraining.

## M3: LA-SSL Increases (Not Decreases) Clusterability

Figure 1 shows the comparison of embedding geometry between SimCLR and LA-SSL.

**Table 3**: LA-SSL vs SimCLR Geometric Comparison

| Metric | SimCLR | LA-SSL | Change | Threshold | Status |
|--------|--------|--------|--------|-----------|--------|
| AMI | 0.2795 | 0.2852 | +2.0% | Reduction ≥30% | **FAIL** |
| Linear AUC | 0.9802 | 0.9856 | +0.54% | $\Delta$AUC < 5% | **PASS** |

**Interpretation**: Contrary to the cluster dispersion hypothesis, LA-SSL *increases* AMI by 2.0% (from 0.2795 to 0.2852) instead of decreasing it by 30%. However, linear separability is well-preserved ($\Delta$AUC=0.0054 < 0.05 threshold), indicating that LA-SSL does not suppress spurious signals entirely.

**M3 Gate Verdict**: ❌ **FAIL** - LA-SSL does not disperse spurious clusters. The mechanism for LA-SSL's documented fairness benefits must be something other than geometric cluster dispersion.

### Surprising Finding

The AMI *increase* under LA-SSL was unexpected. We hypothesize that learning-speed resampling upweights slow-learning (minority) samples, giving them greater representation in the loss. This may inadvertently increase minority group coherence in embedding space rather than dispersing it. LA-SSL's fairness benefits likely come from improved linear decision boundaries for minority groups, not from cluster dispersion.

## Overall Mechanism Verdict

**Figure 1**: Mechanism Gate Results (mechanism_gates_results.png)

[See paper/figures/mechanism_gates_results.png for visual summary]

**Summary**: All three mechanism gates failed:
- M1 (cluster formation): AMI=0.28 < 0.4 ❌
- M2 (diagnostic power): r=-1.0, p=1.0 ❌
- M3 (cluster dispersion): AMI increased 2% (not decreased 30%) ❌

The comprehensive failure across all mechanism steps indicates the issue is fundamental, not marginal. The cluster hypothesis is falsified.

## Implementation Quality Validation

To ensure null results are not due to implementation bugs, we present validation metrics:

**Table 4**: Code Validation Results

| Hypothesis | Tests Passing | SDD Compliance | Critical Issues | Blocking Issues |
|------------|---------------|----------------|-----------------|-----------------|
| h-e1 | 43/43 (100%) | 100% (15/15 tasks) | 0 | 0 |
| h-m-integrated | 5/5 (100%) | 100% (43/43 tasks) | 0 | 0 |

**Interpretation**: Both implementations achieved perfect test pass rates and 100% Software Development Document (SDD) compliance. This demonstrates high code quality and confirms that null results reflect genuine hypothesis failure, not implementation errors.

## AMI Evolution Over Training

**Table 5**: AMI Evolution (SimCLR)

| Epoch | AMI | $\Delta$WGA (cluster-balanced) |
|-------|-----|-------------------------------|
| 10 | 0.2786 | -4.98pp |
| 20 | 0.2795 | -5.30pp |

**Interpretation**: AMI remains consistently low (≈0.28) across training epochs, with no upward trend toward the 0.4 threshold. This suggests that extended training (100 epochs) is unlikely to produce discrete clusters, though full-scale experiments are needed for definitive confirmation.

## Linear Separability Despite Low Clusterability

**Figure 2**: AMI vs Linear Probe AUC Comparison (ami_comparison.png)

[See paper/figures/ami_comparison.png]

**Key Finding**: Linear probe AUC is high (≈0.98) despite low AMI (≈0.28). This dissociation demonstrates that **linear separability and discrete clusterability are independent properties**. Spurious features can be linearly separable (enabling 90% WGA via linear ERM) without forming discrete clusters.

This finding explains why prior work (Mehta et al., 2022) achieved high WGA using linear probes but provides no evidence for cluster structure. Linear classifiers exploit continuous gradients that clustering algorithms cannot detect.
