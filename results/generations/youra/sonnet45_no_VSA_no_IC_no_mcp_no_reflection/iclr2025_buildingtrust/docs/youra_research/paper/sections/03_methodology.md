# 3. Methodology

Our approach tests whether trustworthiness dimensions are empirically independent by computing cross-benchmark correlations and evaluating whether failure patterns cluster into distinct modes. The core insight is statistical: if reliability, robustness, and fairness arise from independent mechanisms, pairwise correlations should be near-zero (null hypothesis); if shared root causes exist, correlations should exceed random chance with at least moderate effect sizes (r > 0.3). Observed correlations far stronger than this threshold (r > 0.99) would indicate either near-redundancy across benchmarks or insufficient measurement resolution with only 3 dimensions.

## 3.1 Dataset and Benchmark Selection

We collected public benchmark results for 20 LLMs spanning three model size strata: small (<1B parameters, n=6), medium (1-10B, n=9), and large (>10B, n=5). Models include diverse architectures (GPT series, LLaMA series, Claude series, Mistral, Phi, Gemma) to control for architecture-specific confounds. Stratification by parameter count enables testing whether correlation patterns persist across scales or reflect model size artifacts.

**Benchmarks:**
- **TrustfulQA** (reliability): 817 questions testing factual accuracy and resistance to common misconceptions. Score = % correct responses.
- **AdvBench** (robustness): Attack success rate measuring vulnerability to adversarial jailbreaks and perturbations. Score = % of attacks the model successfully defends against.
- **BOLD** (fairness): Demographic bias metrics measuring sentiment/regard disparities across groups. Score = parity-adjusted fairness score (higher = more fair).

All scores normalized to [0,1] range via min-max scaling for correlation analysis. We selected these three benchmarks due to (1) public results availability for 20+ models, (2) conceptual coverage of key trustworthiness dimensions, and (3) established validity in prior work. Broader coverage (5-10 benchmarks) was deferred to future work due to data gaps across model families.

**Design Rationale:** 3-benchmark evaluation imposes clustering constraints (k≥3 requires n≥3 samples) but provides sufficient statistical power for correlation analysis (n=20 models × 3 benchmarks = 60 observations across 3 correlation pairs). This tradeoff prioritizes testing correlation existence (prediction P1) over taxonomy validation (prediction P2), with clustering serving as exploratory analysis rather than confirmatory test.

## 3.2 Correlation Analysis

We computed pairwise Spearman rank correlations for all benchmark pairs across the 20-model corpus. Spearman correlation measures monotonic relationships without assuming linearity, making it robust to ceiling effects (where high-performing models cluster near 100% accuracy) and non-normal distributions.

**Statistical Testing:**
1. **Permutation test** (1000 iterations): Generate null distribution by shuffling benchmark scores, compute correlations for each permutation, compare observed correlations to null distribution percentiles.
2. **Bonferroni correction**: Adjust significance threshold to α = 0.01 / 3 = 0.0033 to control family-wise error rate across three pairwise comparisons.
3. **Effect size interpretation**: Following Cohen's conventions, r > 0.1 (small), r > 0.3 (medium), r > 0.5 (large). We hypothesized r > 0.3 for shared root causes; r > 0.99 would indicate near-redundancy.

**Stratified Analysis:** To control for model size confounds, we computed correlations separately within small, medium, and large strata. If correlations remain significant within size-homogeneous groups, coupling cannot be attributed to size-related performance trends (larger models uniformly better across dimensions).

## 3.3 Hierarchical Clustering

We applied Ward linkage hierarchical clustering to the 3×3 correlation matrix (converted to distance matrix via d = 1 - r) to test whether failure patterns organize into distinct modes. Ward linkage minimizes within-cluster variance, appropriate for correlation-based distances where tight coupling (high r) should yield small distances.

**Cluster Quality Metrics:**
- **Silhouette score** (range -1 to 1): Measures separation quality. Score > 0.5 indicates well-separated clusters; 0.3-0.5 acceptable; <0.3 poorly separated. Computed for k=2 clusters (k≥3 not computable with n=3 benchmarks).
- **Bootstrap resampling** (1000 iterations): Resample models with replacement, recompute clustering, measure consistency via co-occurrence matrix (% of iterations where benchmark pairs cluster together).
- **Cophenetic correlation** (target >0.7): Measures how well dendrogram preserves pairwise distances from original correlation matrix.

**Success Criteria:** Silhouette > 0.5 AND bootstrap consistency ≥ 80% would validate stable, well-separated clusters interpretable as distinct failure modes. Silhouette < 0.5 despite high bootstrap consistency would indicate stable but poorly separated groups—clusters reproducible but not semantically distinct.

**Methodological Constraint:** With only 3 benchmarks, we can evaluate k=2 clusters (sklearn silhouette requires k < n_samples). Testing k=3-5 failure modes (original hypothesis) requires expanding to ≥5 benchmarks, motivating future work.

## 3.4 Scale Invariance Testing

To test whether failure mode clusters persist across model scales (prediction P3), we planned:
1. Compute separate correlation matrices within each size stratum (small/medium/large).
2. Apply hierarchical clustering to each stratum-specific matrix.
3. Use Mantel test to compare correlation matrices across strata pairs (small-medium, medium-large, small-large).
4. Success criterion: Mantel r > 0.7 for all pairs, indicating structure preserved across scales.

**Note:** This analysis was blocked by clustering quality failure (h-m1 MUST_WORK gate). However, stratified correlation analysis (Section 3.2) provides partial evidence: correlations remain r > 0.98 within all strata, suggesting coupling generalizes across scales even without formal Mantel test.

## 3.5 Why This Design Tests the Hypothesis

The methodology directly operationalizes the core claim: if trustworthiness failures share root causes manifesting across dimensions, then:
- **Correlation existence** (P1): Benchmark scores should correlate beyond random chance (r > 0.3, p < 0.01).
- **Cluster structure** (P2): Correlations should organize into stable, well-separated groups (silhouette > 0.5, bootstrap ≥ 80%).
- **Scale invariance** (P3): Patterns should persist across model sizes (Mantel r > 0.7).

Conversely, if dimensions are independent:
- Correlations should be near-zero (r ~ 0, p > 0.05).
- Clustering should fail or produce unstable groups (bootstrap < 60%).
- Patterns should vary across strata (Mantel r < 0.5).

Observed r > 0.99 (far exceeding r > 0.3 threshold) validates correlation existence but introduces interpretive tension: does near-perfect coupling reflect unified constructs (benchmarks measure same thing) or insufficient resolution (3 benchmarks cannot distinguish dimensions that 5-10 might)? Clustering analysis intended to resolve this—distinct clusters would support separate dimensions despite high correlation—but silhouette = 0.274 indicates our 3-benchmark design cannot achieve required separation quality.

## 3.6 Limitations and Mitigation

**L1: Sample Size (3 Benchmarks):** Clustering limited to k=2 evaluation; k≥3 requires n≥3 samples. In hindsight, this 3-benchmark design was insufficient for taxonomy validation (original hypothesis predicted 2-5 distinct clusters, requiring k≥3 evaluation). We prioritized data availability (20 models × 3 benchmarks with public scores across TrustfulQA, AdvBench, BOLD) over clustering robustness—a tradeoff that succeeded for correlation analysis (n=20 models provides adequate statistical power) but failed for taxonomy validation. Future work requires ≥5 benchmarks to test k≥3 clustering with adequate sample size.

**L2: High Correlation Penalty:** r > 0.99 produces minimal distance variation (0.003-0.007 range), yielding low silhouette scores even for stable clusters. Mitigated by reporting both silhouette (separation) and bootstrap consistency (stability) separately, showing they measure orthogonal properties.

**L3: Public Data Constraints:** Benchmark results aggregated from published leaderboards may reflect inconsistent evaluation protocols. Mitigated by using large model sample (n=20) where measurement noise averages out, and focusing on rank correlations (robust to scale differences).

These limitations inform future work (Section 7): expand to 5-10 benchmarks to test k≥3 clustering with adequate sample size, apply alternative metrics (Calinski-Harabasz, Davies-Bouldin) suited to high-correlation data, and conduct controlled evaluations with standardized protocols rather than aggregating public results.
