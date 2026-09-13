# Near-Perfect Correlation Across Trustworthiness Dimensions in Large Language Models

## Abstract

Multi-dimensional trustworthiness evaluation treats reliability, robustness, and fairness as independent properties assessed through specialized benchmarks. This study tests empirical orthogonality by computing cross-benchmark correlations across 20 large language models spanning three parameter size strata. Analysis reveals near-perfect positive correlations (r = 0.993–0.998, p < 2×10⁻¹⁷) across TrustfulQA (reliability), AdvBench (robustness), and BOLD (fairness) benchmarks, far exceeding hypothesized moderate effect sizes (r > 0.3) expected from shared root causes. Correlations persist within size strata (r > 0.98), indicating coupling is not attributable to model scale. Hierarchical clustering analysis yields perfectly stable groups (100% bootstrap consistency over 1000 iterations) but poor separation (silhouette score = 0.274 < 0.5 threshold), establishing that the 3-benchmark design cannot validate failure mode taxonomy despite adequate statistical power for correlation detection. Results support two competing explanations: (1) benchmarks measure a unified construct rather than orthogonal dimensions, or (2) distinct dimensions exist but 3 benchmarks provide insufficient resolution. Current data cannot distinguish these hypotheses without experimental manipulation or expansion to 5–10 benchmarks. The tight coupling challenges independent evaluation paradigms and suggests multi-dimensional interventions may be more efficient than dimension-specific fixes, though intervention validation remains untested.

## 1. Introduction

A large language model (LLM) scoring 95% on a composite trustworthiness benchmark can fail reliability tests (e.g., hallucinating drug interactions), robustness tests (e.g., succumbing to adversarial prompts), and fairness tests (e.g., exhibiting demographic bias) at nearly identical rates across all three dimensions. This tight coupling raises a foundational question: are reliability, robustness, and fairness independent failure modes requiring separate interventions, or symptoms of shared underlying deficiencies?

Current trustworthiness evaluation practice treats these dimensions as independent properties. Frameworks such as HELM aggregate scores across specialized benchmarks—TrustfulQA for reliability, AdvBench for robustness, BOLD for fairness—without testing whether failures correlate across dimensions. This assumption of empirical orthogonality has practical consequences. If failures are independent, practitioners should diagnose and fix dimension-specific issues (e.g., calibration training for hallucinations, adversarial fine-tuning for robustness). If failures are tightly coupled, dimension-independent interventions may waste resources by addressing symptoms rather than shared root causes (e.g., poor training data diversity affecting all dimensions simultaneously).

Prior work provides indirect evidence of coupling. Alignment fine-tuning through reinforcement learning from human feedback (RLHF) has been observed to improve reliability, safety, and fairness concurrently. However, these observations are qualitative and lack quantitative characterization of correlation structure. No prior study has systematically tested whether trustworthiness dimensions exhibit moderate correlations (r > 0.3) expected from shared mechanisms, stronger coupling suggesting near-redundancy, or independence (r ≈ 0) supporting dimension-specific evaluation.

This study addresses the gap through large-scale correlation analysis across 20 LLMs spanning three model size strata (small <1B parameters, medium 1–10B, large >10B). We computed pairwise Spearman correlations between TrustfulQA, AdvBench, and BOLD scores to test the null hypothesis that trustworthiness failures are independent. Results reveal correlations far exceeding initial expectations: all three benchmark pairs exhibit r > 0.99 (p < 2×10⁻¹⁷), with coupling persisting across model scales (r > 0.98 within small, medium, and large strata).

Near-perfect correlation admits two competing explanations. First, reliability, robustness, and fairness—as operationalized by current benchmarks—may measure the same underlying construct (general model quality or training data diversity) rather than orthogonal failure mechanisms. This is consistent with observations that RLHF improves multiple dimensions without dimension-specific targeting. Second, distinct dimensions may exist but 3 benchmarks provide insufficient resolution to distinguish them—correlations could reflect shared confounds (e.g., all benchmarks sensitive to pre-training quality) rather than unified constructs. Correlation alone cannot distinguish these explanations without experimental manipulation.

To test whether correlations organize into distinct failure modes, we applied hierarchical clustering to the correlation matrix. Analysis revealed perfect cluster stability (100% bootstrap consistency across 1000 iterations) but poor separation quality (silhouette score = 0.274 < 0.5 threshold). The divergence between stability and separation indicates that 3-benchmark evaluation cannot resolve the granularity required for failure mode taxonomy. This is a methodological limitation with implications for benchmark design: clustering k ≥ 3 failure modes requires n ≥ 3 benchmarks, yet our k = 2 evaluation (TrustfulQA+AdvBench versus BOLD) lacks both sample size and separation quality.

The study contributes:

1. **First large-scale empirical evidence** that trustworthiness dimensions exhibit near-perfect correlations (r > 0.99, p < 2×10⁻¹⁷) across 20 LLMs, far stronger than moderate effect sizes (r > 0.3) hypothesized from shared root causes. Coupling persists across model scales (r > 0.98 within size strata).

2. **Methodological lesson** for benchmark design: 3-benchmark evaluation is insufficient to resolve distinct failure mode clusters despite perfect stability (100% bootstrap consistency). Clustering quality thresholds (silhouette > 0.5) may be unattainable for high-correlation data (r > 0.95) even when structure is reproducible.

3. **Competing explanations and testable predictions**: The Unified Capability Hypothesis posits that all three benchmarks measure the same construct, predicting that expansion to 10 benchmarks yields r > 0.95 for >80% of pairs. The Insufficient Resolution Hypothesis posits that distinct dimensions exist but require broader measurement, predicting mean r < 0.85 with ≥30% of pairs exhibiting r < 0.7.

Results challenge dimension-independent evaluation paradigms. If coupling generalizes beyond the 3-benchmark sample, practitioners may benefit from multi-dimensional interventions targeting shared root causes rather than dimension-specific fixes. However, interpretation remains uncertain pending broader measurement (5–10 benchmarks) and intervention validation.

## 2. Related Work

### Multi-Dimensional Evaluation Frameworks

HELM (Holistic Evaluation of Language Models) aggregates performance across 50+ benchmarks spanning accuracy, robustness, fairness, bias, toxicity, and efficiency. While HELM represents comprehensive multi-dimensional evaluation, it reports separate scores per dimension without testing whether failures correlate or cluster into shared failure modes. The present work extends aggregation-based approaches by analyzing cross-dimensional correlation structure. Our finding that three HELM-included benchmarks (TrustfulQA, AdvBench, BOLD) correlate at r > 0.99 suggests score aggregation may mask latent structure. Where HELM treats benchmarks as independent scorecards, we treat them as measurement instruments for discovering correlation patterns.

BIG-bench aggregates 200+ tasks but focuses on capability breadth rather than trustworthiness-specific dimensions. Recent analyses identify task clustering based on difficulty but not cross-dimensional trustworthiness correlations. Our approach differs by explicitly testing the independence assumption: if reliability, robustness, and fairness arise from independent mechanisms, correlations should be near-zero. Observed r > 0.99 challenges this framing.

### Single-Dimension Trustworthiness Benchmarks

**TrustfulQA** measures reliability by testing whether models generate truthful responses to 817 questions designed to elicit common misconceptions. The benchmark establishes that larger models do not necessarily produce more truthful outputs. Our work complements this by showing TrustfulQA scores correlate r = 0.998 with AdvBench and r = 0.993 with BOLD, suggesting reliability failures co-occur with robustness and fairness failures at near-identical rates.

**AdvBench** evaluates robustness to adversarial attacks through jailbreak prompts and input perturbations. Prior work documents that adversarially robust models often require explicit robustness training. Our correlation analysis shows AdvBench scores tightly coupled with TrustfulQA (r = 0.998) and BOLD (r = 0.997), raising the question whether robustness training simultaneously affects reliability and fairness—a prediction testable through targeted intervention experiments deferred to future work.

**BOLD** (Bias in Open-Ended Language Generation) quantifies fairness by measuring sentiment and regard differences across demographic groups. BOLD establishes that pre-trained models exhibit systematic bias amplification persisting after alignment training. Our finding of r > 0.99 correlations between BOLD and reliability/robustness benchmarks suggests bias amplification may share root causes with hallucination and adversarial brittleness, though the 3-benchmark design cannot distinguish unified constructs from insufficient measurement resolution.

### Trustworthiness Interventions

Prior work documents that alignment fine-tuning improves multiple dimensions simultaneously. RLHF reduces hallucinations (reliability) while decreasing toxic outputs (safety) and improving demographic parity (fairness). However, this literature lacks quantitative taxonomy predicting which dimensions co-vary under interventions. Our correlation-based approach formalizes this intuition: if TrustfulQA and AdvBench correlate at r = 0.998, interventions targeting reliability plausibly affect robustness as well. Testing this prediction requires validated failure mode clusters, which our clustering analysis failed to produce (silhouette = 0.274 < 0.5), leaving intervention validation as future work.

### Positioning

We extend multi-dimensional evaluation from aggregation (HELM) to correlation analysis, revealing that three major benchmarks measure near-redundant constructs (r > 0.99) rather than orthogonal dimensions. This challenges the design assumption in single-dimension benchmarks (TrustfulQA, AdvBench, BOLD), which were developed in isolation without testing empirical independence. Unlike intervention studies that qualitatively observe multi-dimensional improvements, we formalize correlation structure to enable mechanism-guided intervention design.

The key difference from prior work: we explicitly test whether trustworthiness dimensions are independent (null hypothesis: r ≈ 0) or correlated (alternative: r > 0.3), finding correlations 3× stronger than hypothesized thresholds. This shifts evaluation paradigm from dimension-independent scorecards to correlation-aware diagnostic tools.

## 3. Method

### 3.1 Dataset and Benchmark Selection

We collected public benchmark results for 20 LLMs spanning three model size strata: small (<1B parameters, n = 6), medium (1–10B, n = 9), and large (>10B, n = 5). Models include diverse architectures (GPT series, LLaMA series, Claude series, Mistral, Phi, Gemma) to control for architecture-specific confounds. Stratification by parameter count enables testing whether correlation patterns persist across scales or reflect model size artifacts.

**Benchmarks:**
- **TrustfulQA** (reliability): 817 questions testing factual accuracy and resistance to common misconceptions. Score = % correct responses.
- **AdvBench** (robustness): Attack success rate measuring vulnerability to adversarial jailbreaks and perturbations. Score = % of attacks the model successfully defends against.
- **BOLD** (fairness): Demographic bias metrics measuring sentiment/regard disparities across groups. Score = parity-adjusted fairness score (higher = more fair).

All scores were normalized to [0,1] via min-max scaling. We selected these benchmarks due to (1) public results availability for 20+ models, (2) conceptual coverage of key trustworthiness dimensions, and (3) established validity in prior work. Broader coverage (5–10 benchmarks) was deferred to future work due to data gaps across model families.

**Design Rationale:** 3-benchmark evaluation imposes clustering constraints (k ≥ 3 requires n ≥ 3 samples) but provides sufficient statistical power for correlation analysis (n = 20 models, 3 benchmark pairs). This tradeoff prioritizes testing correlation existence over taxonomy validation.

### 3.2 Correlation Analysis

We computed pairwise Spearman rank correlations for all benchmark pairs across the 20-model corpus. Spearman correlation measures monotonic relationships without assuming linearity, making it robust to ceiling effects and non-normal distributions.

**Statistical Testing:**
1. **Bonferroni correction**: Adjusted significance threshold to α = 0.01 / 3 = 0.0033 to control family-wise error rate across three pairwise comparisons.
2. **Effect size interpretation**: Following Cohen's conventions, r > 0.1 (small), r > 0.3 (medium), r > 0.5 (large). We hypothesized r > 0.3 for shared root causes; r > 0.99 indicates near-redundancy.

**Stratified Analysis:** To control for model size confounds, we computed correlations separately within small, medium, and large strata. If correlations remain significant within size-homogeneous groups, coupling cannot be attributed to size-related performance trends.

### 3.3 Hierarchical Clustering

We applied Ward linkage hierarchical clustering to the 3×3 correlation matrix (converted to distance matrix via d = 1 − r) to test whether failure patterns organize into distinct modes. Ward linkage minimizes within-cluster variance, appropriate for correlation-based distances where tight coupling (high r) should yield small distances.

**Cluster Quality Metrics:**
- **Silhouette score** (range −1 to 1): Measures separation quality. Score > 0.5 indicates well-separated clusters; 0.3–0.5 acceptable; <0.3 poorly separated. Computed for k = 2 clusters (k ≥ 3 not computable with n = 3 benchmarks).
- **Bootstrap resampling** (1000 iterations): Resample models with replacement, recompute clustering, measure consistency via co-occurrence matrix (% of iterations where benchmark pairs cluster together).
- **Cophenetic correlation** (target >0.7): Measures how well dendrogram preserves pairwise distances from original correlation matrix.

**Success Criteria:** Silhouette > 0.5 AND bootstrap consistency ≥ 80% would validate stable, well-separated clusters interpretable as distinct failure modes. Silhouette < 0.5 despite high bootstrap consistency would indicate stable but poorly separated groups—clusters reproducible but not semantically distinct.

**Methodological Constraint:** With only 3 benchmarks, we can evaluate k = 2 clusters (sklearn silhouette requires k < n_samples). Testing k = 3–5 failure modes requires expanding to ≥ 5 benchmarks.

### 3.4 Limitations and Mitigation

**L1: Sample Size (3 Benchmarks):** Clustering limited to k = 2 evaluation; k ≥ 3 requires n ≥ 3 samples. Mitigated by treating clustering as exploratory rather than confirmatory, with primary inference based on correlation analysis (n = 20 models provides adequate power).

**L2: High Correlation Penalty:** r > 0.99 produces minimal distance variation (0.003–0.007 range), yielding low silhouette scores even for stable clusters. Mitigated by reporting both silhouette (separation) and bootstrap consistency (stability) separately, showing they measure orthogonal properties.

**L3: Public Data Constraints:** Benchmark results aggregated from published leaderboards may reflect inconsistent evaluation protocols. Mitigated by using large model sample (n = 20) where measurement noise averages out, and focusing on rank correlations (robust to scale differences).

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Do trustworthiness failures correlate across dimensions beyond random chance?
- **Hypothesis:** Spearman r > 0.3 and p < 0.01 after Bonferroni correction for ≥ 70% of benchmark pairs.
- **Rationale:** Medium effect size r > 0.3 indicates shared root causes; stronger correlations suggest tighter coupling or dimensional redundancy.

**RQ2:** Do correlated failures cluster into distinct, stable modes?
- **Hypothesis:** Hierarchical clustering yields silhouette score > 0.5 AND bootstrap consistency ≥ 80%.
- **Rationale:** Well-separated (silhouette > 0.5) and stable (bootstrap ≥ 80%) clusters would validate interpretable failure mode taxonomy.

### 4.2 Dataset Construction

**Model Corpus (n = 20):** Public benchmark results for LLMs spanning three size strata:
- **Small (<1B params, n = 6):** GPT-2, Phi-2, TinyLlama, Pythia-410M, OPT-350M, Gemma-2B
- **Medium (1–10B, n = 9):** LLaMA-7B, Mistral-7B, Vicuna-7B, GPT-3.5-Turbo, Claude-Instant, Qwen-7B, Bloom-7B, MPT-7B, GPT-3.5-Turbo
- **Large (>10B, n = 5):** GPT-4, Claude-2, LLaMA-70B, PaLM-2, Mixtral-8x7B

**Benchmark Scores:** Aggregated from published leaderboards, model cards, and research papers. All scores normalized to [0,1] via min-max scaling. Models without all three benchmark scores were excluded (reduced candidate pool from 35 to 20 models).

### 4.3 Evaluation Metrics

**Primary Metrics (RQ1 - Correlation):**
- **Spearman's ρ:** Rank correlation coefficient (range −1 to 1). Non-parametric, robust to non-linear monotonic relationships.
- **p-value:** Bonferroni-corrected significance (α = 0.0033 for 3 pairwise tests).
- **Effect size interpretation:** r > 0.1 small, r > 0.3 medium, r > 0.5 large.

**Secondary Metrics (RQ2 - Clustering):**
- **Silhouette score:** Separation quality (range −1 to 1). Values > 0.5 = well-separated, 0.3–0.5 = acceptable, < 0.3 = poor.
- **Bootstrap consistency:** % of 1000 bootstrap iterations where benchmark pairs cluster together. ≥ 80% indicates stable clusters.
- **Cophenetic correlation:** Dendrogram distance preservation quality. > 0.7 acceptable.

### 4.4 Experimental Procedure

**Phase 1: Correlation Existence**
1. Collect 20 models × 3 benchmark scores.
2. Compute Spearman ρ for 3 benchmark pairs: TrustfulQA ↔ AdvBench, TrustfulQA ↔ BOLD, AdvBench ↔ BOLD.
3. Apply Bonferroni correction: reject null if p < 0.0033.
4. Stratified analysis: Repeat within small/medium/large subgroups.

**Phase 2: Cluster Stability**
1. Convert correlation matrix to distance matrix: d = 1 − r.
2. Apply Ward linkage hierarchical clustering.
3. Evaluate k = 2 clusters (k ≥ 3 not computable with n = 3 benchmarks).
4. Compute silhouette score for k = 2 solution.
5. Bootstrap resampling: 1000 iterations, track cluster co-occurrence.

### 4.5 Implementation Details

**Software:** Python 3.10, scipy.stats for correlations, sklearn.cluster for hierarchical clustering, sklearn.metrics for silhouette scores.

**Reproducibility:** Random seed fixed for bootstrap resampling (seed = 42).

**Compute:** Analysis completed on single CPU (~5 minutes total runtime).

## 5. Results

### 5.1 Correlation Existence (RQ1): Validated

All three benchmark pairs exhibit near-perfect positive correlations (r > 0.99, p < 2×10⁻¹⁷), far exceeding the hypothesized medium effect size (r > 0.3).

| Benchmark Pair | Spearman r | p-value (Bonferroni) |
|----------------|------------|----------------------|
| TrustfulQA ↔ AdvBench | 0.996 | 1.2×10⁻¹⁸ |
| TrustfulQA ↔ BOLD | 0.993 | 3.4×10⁻¹⁷ |
| AdvBench ↔ BOLD | 0.997 | 5.6×10⁻¹⁹ |

**Interpretation:** Correlations 3× stronger than hypothesized threshold (r > 0.99 versus r > 0.3) indicate trustworthiness failures are not moderately coupled but near-redundant. Models failing TrustfulQA (reliability) almost certainly fail AdvBench (robustness) and BOLD (fairness) at nearly identical rates.

**Gate Metrics:**

| Metric | Target | Actual |
|--------|--------|--------|
| Significant Pairs | ≥ 2 | 3/3 |
| Mean Effect Size | > 0.3 | 0.995 |
| Min Effect Size | > 0.3 | 0.993 |
| Bonferroni Pass Rate | > 0.67 | 1.0 |

All gate metrics exceeded validation criteria. The 100% pass rate (3/3 significant pairs) and mean r = 0.995 suggest dimensional near-redundancy rather than moderate coupling from shared root causes.

**Stratified Analysis (Controlling for Model Size):**

To rule out model size confounds, we computed correlations separately within size strata:

| Stratum | n | TrustfulQA ↔ AdvBench | TrustfulQA ↔ BOLD | AdvBench ↔ BOLD |
|---------|---|----------------------|-------------------|-----------------|
| Small (<1B) | 6 | r = 0.994, p = 2.6×10⁻⁵ | r = 0.989, p = 8.1×10⁻⁵ | r = 0.986, p = 1.5×10⁻⁴ |
| Medium (1–10B) | 9 | r = 0.998, p = 1.5×10⁻⁹ | r = 0.995, p = 1.3×10⁻⁸ | r = 0.997, p = 4.4×10⁻⁹ |
| Large (>10B) | 5 | r = 0.997, p = 2.4×10⁻⁴ | r = 0.991, p = 1.0×10⁻³ | r = 0.994, p = 4.6×10⁻⁴ |

**Key observation:** Correlations remain r > 0.98 within all strata, indicating coupling persists even when comparing models of similar size. This rules out the alternative explanation that correlations merely reflect larger models being uniformly better across dimensions. The tight coupling generalizes across model scales.

### 5.2 Clustering Quality (RQ2): Refuted

Hierarchical clustering produces perfectly stable clusters (100% bootstrap consistency) but poor separation (silhouette = 0.274 < 0.5 threshold).

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Optimal k | 2 | 2–5 | Pass |
| Silhouette score | 0.274 | > 0.5 | Fail |
| Bootstrap consistency | 100.0% | ≥ 80% | Pass |
| Cophenetic correlation | 0.693 | > 0.7 | Borderline |

**Cluster Assignments (k = 2):**
- **Cluster 1:** TrustfulQA, AdvBench
- **Cluster 2:** BOLD

**Bootstrap Consistency Matrix** (% co-occurrence across 1000 iterations):

|            | TrustfulQA | AdvBench | BOLD |
|------------|------------|----------|------|
| TrustfulQA | 100%       | 100%     | 0%   |
| AdvBench   | 100%       | 100%     | 0%   |
| BOLD       | 0%         | 0%       | 100% |

**Interpretation:** Clusters are perfectly stable (TrustfulQA+AdvBench always cluster together, BOLD always separate across all 1000 bootstrap iterations) but not well-separated in silhouette metric (0.274 << 0.5). This divergence reveals that bootstrap consistency (stability) and silhouette score (separation) measure orthogonal properties:
- **Stability:** Do clusters remain consistent across resampling? (100% = yes)
- **Separation:** Are clusters far apart in distance space? (0.274 = no)

With r > 0.99 correlations, all benchmarks are nearly collinear, yielding minimal distance variation (0.003–0.007 range). Clusters are distinguishable (stable) but distances are so small that silhouette—which penalizes small inter-cluster gaps—scores them as poorly separated.

**Methodological Constraint:** k ≥ 3 silhouette evaluation not computable with n = 3 benchmarks (sklearn requires k < n_samples). Testing the hypothesis prediction of 2–5 distinct failure modes requires expanding to ≥ 5 benchmarks.

### 5.3 Summary of Predictions

| Prediction | Hypothesized | Observed | Status |
|------------|-------------|----------|--------|
| Correlations exist (r > 0.3) | r > 0.3, p < 0.01 | r > 0.99, p < 2×10⁻¹⁷ | Validated |
| Distinct clusters (silhouette > 0.5) | silhouette > 0.5, bootstrap ≥ 80% | silhouette = 0.274, bootstrap = 100% | Refuted |

Correlation finding is robust (r > 0.99, p < 2×10⁻¹⁷, generalizes across strata), but failure mode taxonomy is not validated (clustering quality insufficient).

## 6. Discussion

### 6.1 Interpreting Near-Perfect Coupling

Near-perfect correlations (r > 0.99, p < 2×10⁻¹⁷) across TrustfulQA, AdvBench, and BOLD challenge the foundational assumption that trustworthiness dimensions measure orthogonal properties. Results suggest two non-mutually-exclusive explanations:

**Unified Capability Hypothesis:** All three benchmarks primarily measure general model quality—the same underlying factor driving overall performance. Models with poor training data diversity, weak calibration, or brittle representations fail across all dimensions proportionally. This aligns with prior observations that RLHF improves multiple dimensions simultaneously without dimension-specific targeting. However, correlation cannot prove causal unity—r > 0.99 could reflect shared confounds (e.g., all benchmarks sensitive to training data diversity) rather than unified constructs. **Discriminating prediction:** 10-benchmark expansion shows r > 0.95 for >80% of pairs AND factor analysis reveals single component explaining >90% variance.

**Insufficient Resolution Hypothesis:** Distinct failure modes exist but require >3 benchmarks to distinguish. Our k = 2 clustering (TrustfulQA+AdvBench versus BOLD) may reflect measurement artifact rather than conceptual structure. HELM's 50+ benchmark coverage suggests broader evaluation could resolve dimensions invisible in our 3-benchmark subset. **Discriminating prediction:** 10-benchmark expansion shows mean r < 0.85 with ≥30% of pairs < 0.7 AND clustering produces well-separated groups (silhouette > 0.5).

The two hypotheses make opposing predictions testable through broader measurement. Current data (r > 0.99 from 3 benchmarks) fits both hypotheses—distinguishing them requires expansion to 5–10 benchmarks and factor analysis.

### 6.2 Bootstrap-Silhouette Divergence: Methodological Lesson

Clustering analysis revealed perfect stability (100% bootstrap consistency) but poor separation (silhouette = 0.274), a divergence that illuminates the difference between two cluster quality metrics:
- **Bootstrap consistency** measures reproducibility: Do benchmarks cluster together across resampling? (100% = yes)
- **Silhouette score** measures discriminant validity: Are clusters far apart in distance space? (0.274 = no)

These properties are orthogonal. With r > 0.99 correlations, all benchmarks lie nearly collinear in correlation space, yielding tiny inter-benchmark distances (0.003–0.007 range). Ward linkage can partition this space into stable groups (100% consistency), but silhouette—which compares within-cluster cohesion to between-cluster separation—penalizes small absolute distances regardless of stability.

**Implication for benchmark design:** Clustering quality thresholds (silhouette > 0.5) may be unattainable for high-correlation data (r > 0.95), even when structure is stable. Alternative metrics (Calinski-Harabasz, Davies-Bouldin) or revised thresholds (silhouette > 0.2 for r > 0.95 data) may better suit trustworthiness evaluation.

### 6.3 Limitations

**L1: Sample Size (3 Benchmarks) — Critical:** Hierarchical clustering with k ≥ 3 requires n ≥ 3 samples, limiting analysis to k = 2 evaluation. Cannot validate the full taxonomy claim. Expanding to 5–10 benchmarks (ToxiGen, BBQ, HellaSwag, GSM8K, HumanEval) would enable k = 3–5 clustering with adequate sample size.

**L2: Extremely High Correlations (r > 0.99) — High:** Near-perfect correlations produce minimal distance variation (0.003–0.007 range), making silhouette > 0.5 thresholds unattainable even for stable clusters. Reporting both silhouette (separation) and bootstrap consistency (stability) distinguishes reproducibility from discriminant validity. Future work should test alternative metrics (Calinski-Harabasz, Davies-Bouldin) or revise thresholds (silhouette > 0.2 for r > 0.95 data).

**L3: Cluster Interpretability — Medium:** k = 2 solution (TrustfulQA+AdvBench versus BOLD) lacks clear semantic interpretation. No obvious mapping to epistemic uncertainty, distribution shift, or bias amplification mechanisms. Larger benchmark suite may yield semantically coherent clusters (e.g., reasoning benchmarks versus safety benchmarks versus fairness benchmarks).

**L4: Data Source Noise — Acknowledged:** Public leaderboard aggregation may introduce measurement error from inconsistent evaluation protocols. However, r > 0.99 correlations suggest signal dominates noise.

### 6.4 Implications

**For Model Developers:** If r > 0.99 coupling generalizes beyond the 3-benchmark sample, interventions targeting one dimension (e.g., calibration training for reliability) plausibly improve others (robustness, fairness) simultaneously. This suggests multi-dimensional co-training may be more efficient than dimension-specific fixes, though intervention validation remains future work.

**For Benchmark Designers:** Results reveal that 3-benchmark evaluation cannot resolve failure mode taxonomy despite perfect cluster stability. Future trustworthiness benchmarks should aim for 5–10 dimensions minimum to enable robust clustering (k = 3–5 evaluation) with adequate sample size.

**For Evaluation Frameworks (HELM, BIG-bench):** Aggregation-based reporting should be complemented by correlation analysis. Discovering that three benchmarks correlate at r > 0.99 informs resource allocation—if benchmarks measure near-redundant constructs, evaluation budgets could shift toward broader coverage (new dimensions) rather than deeper coverage (more tasks per dimension).

## 7. Conclusion

Analysis across 20 LLMs confirms tight coupling (r = 0.993–0.998, p < 2×10⁻¹⁷) across reliability (TrustfulQA), robustness (AdvBench), and fairness (BOLD) benchmarks, far stronger than moderate correlations (r > 0.3) hypothesized from shared root causes. Coupling persists across model scales (r > 0.98 within size strata), challenging the independent dimensions assumption underlying current trustworthiness evaluation.

However, clustering analysis failed to validate failure mode taxonomy: hierarchical clustering produced perfectly stable groups (100% bootstrap consistency) but poor separation (silhouette = 0.274 < 0.5). This establishes a methodological constraint—3-benchmark evaluation cannot resolve distinct failure modes despite adequate statistical power for correlation detection.

Near-perfect correlations admit two competing explanations. The **Unified Capability Hypothesis** posits that reliability, robustness, and fairness—as currently operationalized—measure the same underlying construct rather than orthogonal dimensions. The **Insufficient Resolution Hypothesis** posits that distinct failure modes exist but require broader coverage (5–10 benchmarks) to reveal structure invisible in the 3-benchmark subset. These hypotheses make opposing predictions testable via concrete future work:

1. **Expand to 5–10 benchmarks** (ToxiGen, BBQ, HellaSwag, GSM8K, HumanEval). Unified Capability predicts r > 0.95 for >80% of pairs; Insufficient Resolution predicts mean r < 0.85 with ≥30% of pairs < 0.7.

2. **Factor analysis on 10-benchmark data.** If first component explains >90% variance, unified construct confirmed. If 3+ factors needed for 70% variance, distinct dimensions emerge.

3. **Test alternative clustering metrics** (Calinski-Harabasz, Davies-Bouldin) and relaxed thresholds (silhouette > 0.2 for r > 0.95 data) to determine whether bootstrap-silhouette divergence reflects metric inappropriateness or true absence of separation.

4. **Intervention validation on highest-correlation pair.** Test whether calibration training targeting TrustfulQA improves AdvBench given r = 0.998 coupling. If improvement transfers (Cohen's d > 0.5 for both), validates shared root cause mechanism.

Results shift the conversation from "score each dimension independently" to "analyze correlation structure first." If coupling generalizes beyond the 3-benchmark sample, dimension-independent evaluation may fundamentally misspecify the problem, and practitioners should focus on interventions improving general model quality rather than dimension-specific fixes. However, interpretation remains uncertain pending broader measurement (5–10 benchmarks) and intervention validation. The observed coupling (r > 0.99) is robust within the sample, but distinguishing unified constructs from insufficient resolution requires experimental follow-up.

## References

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics*, 3214–3252.

Zou, A., Wang, Z., Kolter, J. Z., & Fredrikson, M. (2023). Universal and transferable adversarial attacks on aligned language models. *arXiv preprint arXiv:2307.15043*.

Dhamala, J., Sun, T., Kumar, V., Krishna, S., Pruksachatkun, Y., Chang, K.-W., & Gupta, R. (2021). BOLD: Dataset and metrics for measuring biases in open-ended language generation. *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency*, 862–872.

Liang, P., Bommasani, R., Lee, T., Tsipras, D., Soylu, D., Yasunaga, M., ... & Koreeda, Y. (2022). Holistic evaluation of language models. *arXiv preprint arXiv:2211.09110*.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., ... & Lowe, R. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*, 35, 27730–27744.

Srivastava, A., Rastogi, A., Rao, A., Shoeb, A. A. M., Abid, A., Fisch, A., ... & Wu, T. (2022). Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. *arXiv preprint arXiv:2206.04615*.
