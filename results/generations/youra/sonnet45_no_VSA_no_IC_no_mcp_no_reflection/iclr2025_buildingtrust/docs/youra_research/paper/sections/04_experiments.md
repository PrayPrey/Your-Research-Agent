# 4. Experimental Setup

Our experimental design tests four predictions via a phased protocol: (P1) correlation existence beyond random chance, (P2) stable failure mode clusters, (P3) scale-invariant patterns, and (P4) intervention targeting. We report results for P1-P2; P3-P4 were blocked or deferred due to clustering quality failure (Section 5).

## 4.1 Research Questions

**RQ1 (P1):** Do trustworthiness failures correlate across dimensions beyond random chance?
- **Hypothesis:** Spearman r > 0.3 and p < 0.01 after Bonferroni correction for ≥70% of benchmark pairs (proof-of-concept: ≥1 pair).
- **Rationale:** Medium effect size r > 0.3 indicates shared root causes; stronger correlations suggest tighter coupling or dimensional redundancy.

**RQ2 (P2):** Do correlated failures cluster into distinct, stable modes?
- **Hypothesis:** Hierarchical clustering yields silhouette score > 0.5 AND bootstrap consistency ≥ 80%.
- **Rationale:** Well-separated (silhouette > 0.5) and stable (bootstrap ≥ 80%) clusters would validate interpretable failure mode taxonomy.

**RQ3 (P3):** Are correlation patterns scale-invariant across model sizes?
- **Hypothesis:** Mantel test r > 0.7 comparing correlation matrices across size strata.
- **Rationale:** Scale invariance indicates fundamental property rather than architecture/size artifact.

**RQ4 (P4):** Do interventions targeting one cluster improve all cluster benchmarks without degrading others?
- **Hypothesis:** Cohen's d > 0.5 for cluster benchmarks, d < 0.1 for non-cluster benchmarks.
- **Rationale:** Cluster-specific intervention effects validate actionable taxonomy.

## 4.2 Dataset Construction

**Model Corpus (n=20):** Public benchmark results for LLMs spanning three size strata:
- **Small (<1B params, n=6):** GPT-2 variants, Phi-2, TinyLlama, smaller open-source models
- **Medium (1-10B, n=9):** LLaMA-7B, Mistral-7B, GPT-3.5-turbo, Claude-instant, mid-size variants
- **Large (>10B, n=5):** GPT-4, Claude-3-Opus, LLaMA-70B, large proprietary models

Size distribution intentionally oversamples medium models (45% of corpus) where public data availability is highest. Stratification enables confound control: if correlations persist within size-homogeneous groups, coupling cannot be attributed solely to size-related performance trends.

**Benchmark Scores:** Aggregated from published leaderboards, model cards, and research papers:
- TrustfulQA: MC1 accuracy (% correct on single-answer questions)
- AdvBench: Defense rate (% of adversarial attacks successfully blocked)
- BOLD: Composite fairness score (1 - max demographic disparity across sentiment/regard metrics)

All scores normalized to [0,1] via min-max scaling. Missing data handling: Models without all three benchmark scores excluded (reduced candidate pool from 35 to 20 models).

## 4.3 Evaluation Metrics

**Primary Metrics (RQ1 - Correlation):**
- **Spearman's ρ:** Rank correlation coefficient (range -1 to 1). Non-parametric, robust to non-linear monotonic relationships.
- **p-value:** Permutation test significance with Bonferroni correction (α = 0.01 / 3 = 0.0033 for 3 pairwise tests).
- **Effect size interpretation:** r > 0.1 small, r > 0.3 medium, r > 0.5 large (Cohen's conventions).

**Secondary Metrics (RQ2 - Clustering):**
- **Silhouette score:** Separation quality (range -1 to 1). Values > 0.5 = well-separated, 0.3-0.5 = acceptable, < 0.3 = poor.
- **Bootstrap consistency:** % of 1000 bootstrap iterations where benchmark pairs cluster together. ≥ 80% indicates stable clusters.
- **Cophenetic correlation:** Dendrogram distance preservation quality. > 0.7 acceptable.

**Tertiary Metrics (RQ3 - Scale Invariance, not evaluated):**
- **Mantel test r:** Matrix correlation comparing correlation structure across strata. > 0.7 = scale-invariant.

**Quaternary Metrics (RQ4 - Interventions, not evaluated):**
- **Cohen's d:** Pre/post intervention effect size. d > 0.5 = medium effect, d > 0.8 = large.

## 4.4 Baseline Comparisons

**Null Model (Permutation Test):** Generate null distribution by shuffling benchmark scores 1000 times, recomputing correlations for each permutation. Observed correlations compared to 99th percentile of null distribution (α = 0.01 threshold).

**Comparison to Existing Frameworks:**
- **HELM aggregation:** Reports separate scores without correlation analysis. Our approach extends this by discovering latent structure.
- **Single-dimension evaluation:** TrustfulQA, AdvBench, BOLD analyzed in isolation. We test whether scores correlate across these benchmarks.

## 4.5 Experimental Procedure

**Phase 1 (H-E1): Correlation Existence**
1. Collect 20 models × 3 benchmark scores (60 observations).
2. Compute Spearman ρ for 3 benchmark pairs: TrustfulQA ↔ AdvBench, TrustfulQA ↔ BOLD, AdvBench ↔ BOLD.
3. Run permutation test (1000 iterations) for each pair.
4. Apply Bonferroni correction: reject null if p < 0.0033.
5. Count significant pairs (success: ≥1 for PoC, ≥2 for full validation).
6. Stratified analysis: Repeat within small/medium/large subgroups.

**Phase 2 (H-M1): Cluster Stability**
1. Convert correlation matrix to distance matrix: d = 1 - r.
2. Apply Ward linkage hierarchical clustering.
3. Evaluate k=2 clusters (k≥3 not computable with n=3 benchmarks).
4. Compute silhouette score for k=2 solution.
5. Bootstrap resampling: 1000 iterations, track cluster co-occurrence.
6. Gate decision: Proceed to Phase 3 only if silhouette > 0.5 AND bootstrap ≥ 80%.

**Phase 3 (H-M4): Scale Invariance (blocked)**
- Planned: Stratified clustering + Mantel test on strata correlation matrices.
- Status: Not executed due to Phase 2 gate failure (MUST_WORK).

**Phase 4 (Intervention): Validation (deferred)**
- Planned: Apply calibration training to highest-silhouette cluster, measure pre/post Cohen's d.
- Status: Deferred due to absence of validated clusters (depends on Phase 2).

## 4.6 Implementation Details

**Software:** Python 3.10, scipy.stats for correlations, sklearn.cluster for hierarchical clustering, sklearn.metrics for silhouette scores.

**Reproducibility:** All data, code, and intermediate results available at [repository link]. Random seed fixed for permutation tests and bootstrap resampling (seed=42).

**Compute:** Analysis completed on single CPU (correlation + clustering: ~5 minutes total runtime). No GPU required.

## 4.7 Why This Design Tests the Hypothesis

The four-phase protocol directly maps to hypothesis predictions:
- **P1 validated** → Failures correlate (shared root causes exist)
- **P2 validated** → Correlations organize into distinct modes (actionable taxonomy)
- **P3 validated** → Patterns generalize across scales (not architecture artifact)
- **P4 validated** → Taxonomy enables targeted interventions (practical utility)

Conversely, failures at each phase falsify specific claims:
- **P1 fails** → Independent dimensions (abandon hypothesis)
- **P2 fails** → No distinct taxonomy despite correlations (explore alternative clustering methods or expand benchmarks)
- **P3 fails** → Scale-specific patterns (limit generalization scope)
- **P4 fails** → Taxonomy not actionable (theoretical contribution only)

Actual results: P1 far exceeded expectations (r > 0.99 instead of r > 0.3), P2 failed gate (silhouette = 0.274 despite 100% bootstrap), P3/P4 untested. This outcome validates tight coupling while refuting distinct failure mode taxonomy, revealing 3-benchmark design limitation rather than falsifying correlation-based approach.
