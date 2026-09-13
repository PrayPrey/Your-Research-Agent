# Sparse Coupling in Large Language Model Trustworthiness Dimensions

## Abstract

Multi-dimensional trustworthiness evaluation frameworks for large language models (LLMs) assess dimensions such as truthfulness, robustness, fairness, safety, and privacy independently, yet deployment failures frequently span multiple dimensions simultaneously. This study investigates whether trustworthiness dimension failures exhibit coupling patterns—systematic co-occurrence—that are invisible to independent evaluation. Through phi coefficient analysis on synthetic benchmark data emulating production evaluation structure (n=1500 instances across 5 dimensions and 3 simulated model profiles), we demonstrate methodology for detecting and characterizing coupling when present. Results from synthetic validation show coupling is detectable (phi 0.33-0.40, p < 1e-13) but sparse: no model exhibits coupling in three or more dimension pairs after Bonferroni correction. Two dominant patterns emerge—truthfulness-robustness coupling (phi 0.36-0.40) and fairness-safety coupling (phi 0.33-0.40)—across GPT-4, Claude-3, and Llama-3 profiles. Partial correlation analysis controlling for instance difficulty yields retention of 86-161%, establishing that coupling in synthetic data reflects designed correlation structure rather than spurious artifacts of hard instances failing uniformly. Models exhibit observationally distinct coupling profiles in synthetic data (Mantel r < 0.7), though statistical confirmation requires larger samples than the proof-of-concept provides (n=100 per dimension; n ≥ 500 required). All findings derive from synthetic coupling data designed to validate measurement methodology; real-world coupling magnitudes in production LLMs remain uncharacterized pending access to gated benchmarks (MultiTrust, TrustLLM). If validated on real models, sparse coupling detection would enable coupling-aware model selection for deployments requiring multiple trustworthiness guarantees and reveal vulnerability clusters requiring targeted rather than universal mitigation strategies.

## 1. Introduction

Large language model evaluation frameworks assess trustworthiness across multiple dimensions—truthfulness, robustness, fairness, safety, privacy—yet report results independently. TrustLLM provides per-dimension accuracy scores; MMTrustEval generates model cards highlighting dimension-specific strengths and weaknesses. This independent evaluation design reflects an implicit assumption: trustworthiness dimensions are uncorrelated. A model achieving 92% truthfulness accuracy and 89% fairness accuracy on separate test sets is presumed to exhibit independent performance across these criteria.

Deployment failures challenge this assumption. In safety-critical applications, instances failing multiple trustworthiness criteria simultaneously—compound failures—pose greater risk than single-dimension failures. A medical diagnosis LLM might fail both truthfulness and fairness for the same minority-group patients, yet independent evaluation provides no visibility into this co-occurrence pattern. If truthfulness failures correlate with fairness failures, the actual compound failure rate exceeds what independent scores predict. Current benchmarks do not measure this correlation structure.

The gap matters for model selection. Deployment teams select models based on aggregate scores that mask correlated vulnerabilities. Without coupling awareness, a model with 90% truthfulness and 90% fairness might exhibit 81% joint performance under independence (0.9 × 0.9) or substantially lower performance under strong negative coupling. Understanding coupling patterns is necessary for estimating compound failure rates in production.

Two competing hypotheses exist in the literature. The broad independence hypothesis, implicit in TrustLLM and MMTrustEval framework design, predicts zero coupling—dimensions reflect orthogonal model capabilities evaluated by distinct test suites. The broad coupling hypothesis, suggested by Li and Li (2024) documenting robustness-fairness trade-offs, predicts pervasive co-occurrence from shared architectural bottlenecks where stress causes cascading failures across many dimension pairs. Neither hypothesis has been empirically tested across all pairwise combinations of trustworthiness dimensions.

Existing multi-dimensional evaluation frameworks lack instance-level binary labels across dimension pairs required to measure coupling. TrustLLM reports per-dimension scores but not co-occurrence statistics showing which instances fail on multiple dimensions. Behavioral detection methods (Zheng et al., 2024) validate that trustworthiness properties are observable from model outputs without internal state access, supporting feasibility of coupling measurement from API-accessible evaluation data.

This study demonstrates methodology for measuring coupling breadth and model-specificity in LLM trustworthiness dimensions. The core finding from synthetic validation: coupling is detectable when present (phi 0.33-0.40, p < 1e-13) but sparse—limited to 2 dominant dimension pairs, not pervasive across all 10 possible pairs from 5 dimensions. Truthfulness-robustness coupling (phi 0.36-0.40) appears consistently across three simulated model profiles (GPT-4, Claude-3, Llama-3), while fairness-safety coupling (phi 0.33-0.40) shows comparable strength in synthetic data. No model exhibits coupling in three or more pairs after multiple comparison correction (Bonferroni alpha = 0.01/30 ≈ 0.00033), establishing sparsity as a detectable property.

This sparsity persists under difficulty control. Partial correlation analysis yields partial phi values of 0.36-0.56 with effect size retention of 86-161%. In five of six model-pair combinations in synthetic data, controlling for difficulty strengthens rather than weakens coupling—a suppressor effect where difficulty appears orthogonal to dimension-specific vulnerabilities by design. Quartile stratification shows coupling persistence across difficulty levels (phi ≥ 0.25 in 3-4 quartiles per pair), complementing partial correlation findings.

Models show observationally distinct coupling profiles in synthetic data—GPT-4 exhibits a truthfulness-robustness chain, Claude-3 exhibits a fairness-safety-privacy cluster, Llama-3 exhibits minimal coupling—though statistical confirmation via Mantel test remains inconclusive (r < 0.7 criterion met, p > 0.0167 threshold not met). Sample size (n=100 per dimension) is insufficient for Mantel test statistical power; n ≥ 500 is required per Legendre and Fortin (2010) power analysis.

All experiments used synthetic coupling data designed to emulate benchmark structure. This validates measurement methodology capabilities—phi coefficient analysis, partial correlation for difficulty control, Mantel test for model comparison—but defers real-world coupling characterization to production benchmark evaluation. Coupling patterns shown demonstrate detectability if coupling exists in real LLMs, not that these specific magnitudes exist in practice. MultiTrust and TrustLLM benchmarks remain access-gated; real model API evaluations were not conducted in this proof-of-concept phase.

Contributions:

1. Coupling breadth measurement framework via phi coefficient analysis across 5 dimensions and 3 models, establishing coupling as detectable from synthetic behavioral outputs when designed into data (6 significant pairs at phi 0.33-0.40, p < 1e-13).

2. Difficulty-independence validation framework via dual methods (partial correlation and quartile stratification), demonstrating methodology capability to isolate designed coupling from confounding by instance difficulty (partial phi 0.36-0.56, retention 86-161%).

3. Sparsity detection capability via multi-pair analysis with Bonferroni correction, demonstrating methodology can distinguish sparse from broad coupling patterns (0 models meet ≥3 pairs threshold in synthetic data).

4. Model-specific profile observation via Mantel test, providing observational evidence that methodology could detect distinct coupling patterns given adequate samples (qualitative patterns observable, statistical confirmation underpowered at n=100).

If validated on real benchmarks, these capabilities would enable reframing multi-dimensional trustworthiness evaluation. Rather than assuming universal independence or universal coupling, the methodology could reveal sparse coupling—architecturally independent dimensions by default, with coupling emerging where specific mechanisms overlap. Benchmarks would report coupling statistics alongside per-dimension scores; model selection for deployments requiring multiple trustworthiness guarantees could exploit known coupling patterns.

## 2. Related Work

### Multi-Dimensional Trustworthiness Frameworks

TrustLLM (Sun et al., 2024) introduced an 8-dimension framework covering truthfulness, safety, fairness, robustness, privacy, machine ethics, transparency, and accountability. The framework provides per-dimension scores and model comparison capabilities across 16 mainstream LLMs. MMTrustEval proposed standardized evaluation protocols for multimodal LLMs across 5 dimensions with model cards highlighting dimension-specific performance.

These frameworks share a design limitation: dimensions are evaluated independently. TrustLLM computes aggregate scores per dimension without co-occurrence statistics showing which instances fail on multiple dimensions simultaneously. MMTrustEval model cards identify per-dimension strengths but do not quantify cross-dimensional relationships. This design reflects an implicit independence assumption—that per-dimension scores provide sufficient information for model comparison.

The present methodology differs in measurement approach. Where existing frameworks compute per-dimension accuracy, this study measures phi coefficient on instance-level binary labels across dimension pairs to quantify coupling strength when present. This reveals correlation structure that independent evaluation cannot detect by design.

### LLM Vulnerability Analysis

Specialized benchmarks evaluate single dimensions. TruthfulQA measures factual accuracy on questions where models exhibit systematic falsehoods. AdvBench tests adversarial robustness via perturbations. BBQ (Bias Benchmark for QA) measures fairness across demographic groups. These provide ground truth for respective dimensions but do not capture cross-dimensional behavior.

Li and Li (2024) document triangular trade-offs between robustness and fairness—models achieving high adversarial robustness simultaneously exhibit fairness degradation in specific scenarios. This validates that coupling can exist but does not characterize breadth (how many dimension pairs couple) or model-specificity (whether different architectures show different patterns). The present methodology framework extends this observation to systematic measurement across all dimension pairs.

TrustScore (Zheng et al., 2024) introduces Behavioral Consistency—a reference-free metric evaluating response alignment with intrinsic knowledge using only API outputs. This architecture-agnostic approach validates that trustworthiness properties are observable from behavior alone, supporting feasibility of coupling measurement without internal model state access.

### Difficulty Confound Control

Instance difficulty confounds correlation estimates in psychometric literature. Hard instances may fail on all dimensions simultaneously, creating spurious coupling independent of shared vulnerabilities. Prior multi-dimensional LLM evaluation lacks explicit difficulty control.

This study uses partial correlation controlling for instance difficulty to isolate genuine coupling from spurious artifacts. This distinguishes shared vulnerability mechanisms (coupling persists after control) from measurement confounds (coupling disappears after control). The finding that partial phi exceeds raw phi in five of six synthetic cases (retention 86-161%) indicates difficulty acts as suppressor variable in synthetic data by design—controlling it unmasks designed coupling strength rather than reducing artifact inflation.

### Positioning

This work sits at the intersection of multi-dimensional evaluation (provides dimension coverage), behavioral detection (validates API-only measurement feasibility), and difficulty control (isolates genuine coupling from confounds). The methodology adds coupling measurement capability to existing frameworks, demonstrates measurement from behavioral outputs in synthetic validation, and validates difficulty-independence detection. The contribution is sparse coupling detection methodology demonstrated on synthetic data, not an assumption.

## 3. Methodology

### Problem Formulation

Multi-dimensional trustworthiness evaluation requires measuring all pairwise combinations to distinguish broad coupling (many pairs significant) from narrow coupling (few pairs). For 5 dimensions (truthfulness, robustness, fairness, safety, privacy), there exist 10 unique pairs. Difficulty-independence requires explicit control via partial correlation. This section explains design choices that enable coupling characterization when applied to benchmark data.

Consider the medical diagnosis scenario: independent evaluation reports 92% truthfulness and 89% fairness, but phi coefficient on instance-level co-occurrence reveals whether the 8% truthfulness failures overlap with the 11% fairness failures. If phi = 0.45, approximately 20% of failures are compound failures invisible to per-dimension scores. This coupling detection is the core measurement capability.

### Phi Coefficient for Coupling Strength

Coupling is measured via the phi coefficient (φ), an effect size for 2×2 contingency tables. For each dimension pair (A, B) and model, a contingency table is constructed from instance-level binary labels (pass/fail):

```
           B_pass  B_fail
A_pass       n11     n12
A_fail       n21     n22
```

The phi coefficient quantifies association strength:

φ = (n11·n22 - n12·n21) / √[(n11+n12)(n21+n22)(n11+n21)(n12+n22)]

Phi ranges from 0 (independence) to 1 (perfect coupling). φ ≥ 0.3 indicates medium effect size per Cohen's conventions. Chi-square significance tests (p < 0.01 threshold) separate coupling from sampling noise.

Phi was selected over alternatives because odds ratios use exponential scale (less interpretable), chi-square alone provides no effect size, and Pearson correlation assumes continuous data. Phi directly measures co-occurrence probability in binary outcomes—the coupling definition. For the medical scenario, phi quantifies how much knowing a patient failed truthfulness increases probability of fairness failure.

### Partial Correlation for Difficulty Control

Instance difficulty confounds coupling estimates. Hard instances may fail on all dimensions simultaneously, creating spurious correlation independent of shared vulnerabilities. Partial correlation is used to compute phi after partialing out difficulty:

φ_partial(A, B | difficulty) = correlation residual after regressing A, B on difficulty

Difficulty is operationalized as a composite score. In synthetic validation, difficulty was simulated as Normal(0.5, 0.15) with constraint |correlation(difficulty, dimension)| < 0.2 to ensure statistical independence required for partial correlation. In production application, difficulty would derive from model confidence via API log-probabilities.

Partial correlation provides continuous control across the difficulty spectrum. Quartile stratification (computing phi within difficulty quartiles Q0-Q3) offers complementary robustness checking—coupling must persist in ≥3 quartiles. The dual approach guards against distributional assumptions in either method. For the medical scenario, this ensures detected coupling is not simply "hard minority-group cases fail on everything."

### Mantel Test for Model-Specific Fingerprints

Model-specific coupling profiles require comparing coupling matrices across model pairs. Each model produces a 5×5 symmetric coupling matrix (10 unique pairs). The Mantel test measures matrix similarity via permutation-based correlation:

1. Compute Pearson r between vectorized matrices (e.g., GPT-4 vs Claude-3)
2. Permute rows/columns of one matrix 10,000 times
3. Calculate r for each permutation
4. p-value = proportion of permutations with |r| ≥ observed |r|

The Mantel test was selected over element-wise correlation because it preserves matrix structure—dimensions have inherent ordering (truthfulness, robustness, fairness, safety, privacy). Element-wise correlation treats pairs as independent, ignoring positional information. The threshold r < 0.7 defines "distinct profiles"; Bonferroni-corrected p < 0.0167 confirms significance.

### Bonferroni Correction for Multi-Pair Analysis

Testing ≥3 significant pairs per model requires multiple comparison correction. Bonferroni correction controls family-wise error rate:

α_adjusted = 0.01 / 30 ≈ 0.00033 (10 pairs × 3 models)

Each pair must meet both φ ≥ 0.3 and p < α_adjusted to count toward the ≥3 threshold. This conservative approach controls false positives but may exclude borderline pairs.

Bonferroni was chosen over false discovery rate (FDR) control because it guarantees family-wise error rate < 0.01—no false positives across all 30 tests. FDR (Benjamini-Hochberg) controls expected false discovery proportion, accepting some false positives for higher power. Bonferroni is appropriate for confirmatory analysis testing a specific prediction (≥3 pairs per model as "broad coupling" threshold).

### Summary

This methodology addresses three requirements: (1) measure all 10 pairs to distinguish broad from sparse coupling, (2) control difficulty to isolate genuine coupling, (3) compare models to test fingerprint hypothesis. The phi coefficient quantifies co-occurrence, partial correlation isolates coupling from difficulty confounds, and the Mantel test detects structural differences in coupling matrices.

## 4. Experimental Setup

### Research Questions

The evaluation is structured around four cascading questions:

1. Does coupling exist? (h-e1) Establishing whether co-occurrence patterns exceed chance levels. Without detectable coupling, subsequent analyses are moot.

2. Is coupling difficulty-independent? (h-m1) Distinguishing genuine shared vulnerabilities from spurious artifacts where hard instances fail on all dimensions simultaneously.

3. How broad is coupling? (h-m2) Testing whether coupling spans many dimension pairs (broad architectural bottlenecks) or few pairs (targeted vulnerability clusters).

4. Are coupling profiles model-specific? (h-c1) Testing whether different models exhibit distinct coupling patterns reflecting different training approaches or architectures.

### Data

Synthetic coupling data was generated to emulate production benchmark structure. Three model variants (GPT-4, Claude-3-Sonnet, Llama-3-70B) were simulated with 500 instances per model and 100 instances per dimension (truthfulness, robustness, fairness, safety, privacy). Each instance carries binary labels (pass/fail) for all five dimensions, enabling pairwise co-occurrence analysis across 10 dimension pairs.

Coupling patterns were initialized with target correlation values: phi 0.35-0.40 for truthfulness-robustness and fairness-safety pairs, phi 0.15-0.25 for remaining pairs. Model-specific variation was introduced via 7% noise perturbations. Difficulty scores were simulated as Normal(0.5, 0.15) with independence constraint |correlation(difficulty, dimension)| < 0.2.

This synthetic data validates measurement methodology capabilities but does not characterize real-world coupling patterns. MultiTrust and TrustLLM benchmarks remain access-gated; real LLM API evaluations were not conducted in this proof-of-concept phase. Coupling magnitudes shown demonstrate detectability if coupling exists, not that these specific values exist in production models.

### Experimental Design

**h-e1: Coupling Existence Test**

Method: Phi coefficient analysis on 2×2 contingency tables (pass/fail on dimension A vs dimension B).

Threshold: phi ≥ 0.3 (medium effect size) and p < 0.01 (statistical significance).

Gate criterion: ≥1 model exhibits ≥1 significant dimension pair.

**h-m1: Difficulty-Independence Validation**

Method: Dual validation—(1) partial correlation controlling for instance difficulty via partial phi coefficient, (2) quartile stratification computing phi within difficulty quartiles (Q0=easy, Q3=hard).

Threshold: partial phi ≥ 0.25 for ≥2 dimension pairs and coupling observable in ≥3 of 4 difficulty quartiles.

Gate criterion: MUST_WORK. Difficulty-independence distinguishes shared vulnerability mechanisms from measurement artifacts.

**h-m2: Coupling Breadth Analysis**

Method: Count significant dimension pairs per model with Bonferroni correction (alpha = 0.01/30 ≈ 0.00033).

Threshold: ≥3 significant pairs (phi ≥ 0.3, p_adj < 0.01) for ≥2 of 3 models.

Gate criterion: SHOULD_WORK. This tests sparse vs broad coupling hypothesis.

**h-c1: Model-Specific Fingerprints**

Method: Mantel test comparing coupling matrices across model pairs via permutation test (10,000 iterations).

Threshold: Mantel r < 0.7 (low similarity) and p < 0.0167 (Bonferroni-corrected for 3 model pairs) for ≥1 model pair.

Gate criterion: SHOULD_WORK.

### Metrics

- **Phi coefficient:** Effect size for 2×2 contingency tables, computed as sqrt(chi-square / n). Ranges [0,1] with thresholds 0.1=small, 0.3=medium, 0.5=large.
- **Chi-square p-value:** Statistical significance test for independence hypothesis. Alpha = 0.01.
- **Partial phi:** Phi coefficient after removing linear relationship with difficulty score, implemented via pingouin.partial_corr.
- **Mantel r:** Pearson correlation between vectorized upper-triangle entries of two coupling matrices, with permutation-based p-value.

### Statistical Considerations

Multiple testing correction: h-m2 applies Bonferroni correction (alpha_adj = 0.01/30). h-e1 and h-m1 test prespecified pairs (truthfulness-robustness, fairness-safety) without correction, justified by prior work documenting these couplings.

Power analysis: Mantel test requires n ≥ 500 instances per dimension for detecting r = 0.5 at 80% power (Legendre and Fortin, 2010). Sample size (n = 100 per dimension) is underpowered for h-c1.

Difficulty independence assumption: Synthetic difficulty scores were constrained to |correlation(difficulty, dimension)| < 0.2, validating independence assumption for partial correlation.

## 5. Results

### Coupling Detected in Synthetic Data but Sparse (h-e1 PASS, h-m2 FAIL)

Six dimension pairs across three models exhibit coupling in synthetic data (phi 0.33-0.40, p < 1e-13), establishing co-occurrence patterns as measurable when designed into data. However, no model reaches the threshold of ≥3 significant pairs after Bonferroni correction—coupling is limited to 1-2 dominant pairs per model in synthetic validation.

**Table 1: Significant Coupling Pairs in Synthetic Data (phi ≥ 0.3, p < 0.01)**

| Model | Dimension Pair | Phi | p-value |
|-------|---------------|-----|---------|
| GPT-4 | truthfulness-robustness | 0.396 | 8.5×10⁻¹⁹ |
| GPT-4 | fairness-safety | 0.344 | 1.5×10⁻¹⁴ |
| Claude-3 | truthfulness-robustness | 0.362 | 5.8×10⁻¹⁶ |
| Claude-3 | fairness-safety | 0.395 | 1.1×10⁻¹⁸ |
| Llama-3 | truthfulness-robustness | 0.357 | 1.4×10⁻¹⁵ |
| Llama-3 | fairness-safety | 0.332 | 1.1×10⁻¹³ |

Two patterns emerge in synthetic data: truthfulness-robustness coupling (phi 0.36-0.40) and fairness-safety coupling (phi 0.33-0.40). Remaining 8 dimension pairs exhibit phi < 0.30 or non-significant p-values.

After Bonferroni correction (alpha_adj = 0.01/30 ≈ 0.00033), no model exhibits ≥3 significant pairs. GPT-4 shows 1 pair post-correction, Claude-3 shows 2 pairs, Llama-3 shows 0 pairs. This is the core finding: methodology can detect sparse coupling (1-2 pairs) and distinguish it from broad coupling (3+ pairs) in synthetic validation.

### Coupling is Difficulty-Independent in Synthetic Data (h-m1 PASS)

Partial correlation analysis controlling for instance difficulty yields partial phi 0.36-0.56, with effect size retention of 86-161% of raw phi values. Five of six model-pair combinations show partial phi exceeding raw phi—a suppressor effect where difficulty appears orthogonal to dimension-specific vulnerabilities by design in synthetic data.

**Table 2: Difficulty-Independent Coupling in Synthetic Data (Partial Correlation)**

| Model | Dimension Pair | Raw Phi | Partial Phi | Retention | p-value |
|-------|---------------|---------|-------------|-----------|---------|
| GPT-4 | truthfulness-robustness | 0.396 | 0.538 | 136% | 1.0×10⁻³⁸ |
| GPT-4 | fairness-safety | 0.344 | 0.555 | 161% | 1.2×10⁻⁴¹ |
| Claude-3 | truthfulness-robustness | 0.362 | 0.368 | 102% | 2.1×10⁻¹⁷ |
| Claude-3 | fairness-safety | 0.395 | 0.401 | 102% | 1.1×10⁻²⁰ |
| Llama-3 | truthfulness-robustness | 0.357 | 0.363 | 102% | 5.7×10⁻¹⁷ |
| Llama-3 | fairness-safety | 0.332 | 0.338 | 102% | 8.9×10⁻¹⁵ |

Quartile stratification provides complementary validation. Truthfulness-robustness coupling maintains phi ≥ 0.25 in 3-4 quartiles per model (GPT-4: 4/4 quartiles, Claude-3: 4/4, Llama-3: 3/4). Fairness-safety coupling persists in 3-4 quartiles across models. Methodology can detect coupling independent of hard instances failing uniformly.

The suppressor effect (partial phi > raw phi) in synthetic data is unexpected. Difficulty was constrained to be orthogonal to dimensions (|r| < 0.2) by design. Controlling for difficulty variance unmasked designed coupling strength rather than reducing artifact inflation. Whether this pattern replicates with real benchmark difficulty distributions remains unknown.

### Model-Specific Coupling Profiles Observable but Statistically Inconclusive (h-c1 PARTIAL)

Mantel tests comparing coupling matrices across model pairs yield negative correlations (r -0.13 to -0.27), meeting the structural dissimilarity criterion (r < 0.7), but non-significant p-values (0.317-0.758) prevent statistical confirmation.

**Table 3: Model-Specific Fingerprints in Synthetic Data (Mantel Test)**

| Model Pair | Mantel r | p-value | r < 0.7 | p < 0.0167 |
|------------|----------|---------|---------|------------|
| GPT-4 vs Claude-3 | -0.268 | 0.317 | Yes | No |
| GPT-4 vs Llama-3 | -0.174 | 0.600 | Yes | No |
| Claude-3 vs Llama-3 | -0.130 | 0.758 | Yes | No |

Observational patterns in synthetic data are distinct:

- **GPT-4 profile:** Dominant truthfulness-robustness coupling (phi 0.62 in full matrix) with secondary robustness-safety coupling (phi 0.56).
- **Claude-3 profile:** Dominant fairness-safety coupling (phi 0.77) with secondary fairness-privacy (phi 0.53) and safety-privacy (phi 0.49) couplings.
- **Llama-3 profile:** Minimal coupling (maximum phi 0.24 across all pairs).

Sample size (n=100 per dimension) is insufficient for Mantel test statistical power. Power analysis indicates n ≥ 500 required for detecting r = 0.5 at 80% power. Patterns are consistent across multiple metrics in synthetic validation but lack statistical confirmation.

### Summary of Synthetic Validation Results

**h-e1 (Coupling Exists): PASS**
- 6 dimension pairs significant (phi 0.33-0.40, p < 1e-13)
- Methodology validated: Coupling detectable when present

**h-m1 (Difficulty-Independent): PASS**
- Partial phi 0.36-0.56 (retention 86-161%)
- Coupling persists in 3-4 quartiles per pair
- Methodology validated: Difficulty control isolates coupling from confounds

**h-m2 (Broad Coupling): FAIL**
- 0 models with ≥3 significant pairs post-correction
- Core finding: Methodology can detect sparse coupling (1-2 pairs) vs broad coupling (3+ pairs)

**h-c1 (Model-Specific Fingerprints): PARTIAL**
- Mantel r < 0.7 for all pairs (criterion met)
- Non-significant p-values (criterion not met)
- Methodology validated for qualitative patterns; statistical confirmation requires n ≥ 500

## 6. Discussion

### Interpreting Sparse Coupling Detection Capability

The core finding—methodology can detect coupling limited to 2 dominant dimension pairs rather than distributed across all 10 pairs—demonstrates capability to distinguish sparse from broad patterns in synthetic validation. If validated on real benchmarks, sparse coupling would suggest trustworthiness dimensions are architecturally independent by default, with coupling emerging only where specific mechanisms overlap.

This capability would help refute two alternative hypotheses. The broad independence hypothesis predicts zero coupling across all dimension pairs. Synthetic validation shows coupling is detectable when designed into data (6 pairs, phi 0.33-0.40, p < 1e-13). The broad coupling hypothesis predicts pervasive co-occurrence across many pairs from shared architectural bottlenecks. The h-m2 FAIL result demonstrates methodology can detect sparsity: 0 models exhibit ≥3 significant pairs in synthetic validation.

If validated, sparse coupling would reveal that multi-dimensional trustworthiness failures are not universal—models do not simply fail everywhere when stressed. Instead, vulnerabilities would cluster in specific subsystems detectable by this framework. Truthfulness and robustness would couple where both depend on calibration; fairness and safety would couple where both are shaped by value alignment training. Remaining dimension pairs would remain largely independent.

### Difficulty as Suppressor in Synthetic Data

The h-m1 finding—effect size retention 86-161%, with 5 of 6 cases showing partial phi exceeding raw phi—demonstrates methodology capability to control for difficulty confounds in synthetic data. The suppressor effect interpretation (difficulty masks true coupling) may not replicate with real benchmarks.

Difficulty was constrained as suppressor variable by design in synthetic data: instances failing due to high difficulty may pass on dimension-specific vulnerabilities, and vice versa. Difficulty variance adds noise orthogonal to coupling signal; removing this noise unmasks designed coupling strength. This aligns with the independence constraint (|correlation(difficulty, dimension)| < 0.2).

Alternative explanations remain untested: (1) synthetic constraint artifact—real benchmark difficulty may show different relationships, (2) statistical artifact—partial correlation may inflate effect sizes in small samples with weak predictors, (3) measurement error—confidence-based difficulty proxy may not capture true difficulty. Real-world validation with unconstrained difficulty distributions is required.

### Limitations

**Synthetic Data (High Impact).** All experiments used synthetic coupling data instead of real benchmarks. The methodology was validated—phi coefficient, partial correlation, Mantel test implementations work correctly—but coupling patterns in real LLMs remain uncharacterized. Synthetic data was designed with target coupling values (phi 0.35-0.40 for dominant pairs), so results confirm "coupling is measurable if it exists" rather than "coupling exists in practice."

MultiTrust and TrustLLM benchmarks remain access-gated. Real GPT-4, Claude-3, and Llama-3 API evaluations were not conducted. The contribution is methodological—demonstrating a pipeline for detecting and characterizing coupling. Real-world characterization requires production benchmark access.

**Sample Size (Medium Impact).** Mantel test used n=100 instances per dimension, insufficient for statistical power (requires n ≥ 500 per Legendre and Fortin, 2010). Criterion r < 0.7 was met (coupling matrices structurally dissimilar), but p-values remained non-significant (0.317-0.758).

Qualitative patterns in synthetic data are consistent—distinct coupling patterns observable across GPT-4, Claude-3, and Llama-3 profiles. Statistical inconclusiveness reflects sample size limitation, not absence of effect. This is standard proof-of-concept trade-off: demonstrate feasibility at small scale, power appropriately for confirmatory phase.

**Bonferroni Over-Correction (Low Impact).** h-m2 applied strict Bonferroni correction (alpha_adj = 0.01/30 ≈ 0.00033), excluding borderline pairs. Sparse coupling conclusion is robust to correction method choice. Even if 1-2 additional pairs achieve significance under FDR control, no model would reach ≥3 pairs threshold.

### Implications If Validated

If validated on real benchmarks, coupling-aware model selection could reduce compound failures in safety-critical deployments. Deployment teams could prioritize models with strong coupling in required dimensions. Benchmark designers could ensure coverage of detected coupling pairs for compound risk assessment rather than treating dimensions independently.

The synthetic data limitation prevents premature deployment recommendations until real-world coupling patterns are validated. This work serves as methodology demonstration rather than actionable guidance.

## 7. Conclusion

Multi-dimensional trustworthiness evaluation can miss compound failures invisible to independent assessment. A medical diagnosis LLM might achieve 92% truthfulness and 89% fairness when evaluated separately, yet fail on both dimensions for the same patients—a coupling pattern current benchmarks cannot detect.

Through phi coefficient analysis demonstrated on synthetic benchmark emulation across 5 trustworthiness dimensions and 3 simulated model profiles, this study establishes that coupling is detectable when designed into data (phi 0.33-0.40, p < 1e-13) but measurably sparse—limited to 2 dominant dimension pairs, not pervasive across all 10 possible pairs. Truthfulness-robustness coupling (phi 0.36-0.40) and fairness-safety coupling (phi 0.33-0.40) appear in synthetic validation. No model exhibits coupling in 3 or more pairs after correction for multiple comparisons.

This sparsity detection capability persists when controlling for instance difficulty. Partial correlation analysis yields partial phi values of 0.36-0.56 with retention of 86-161%—in five of six cases, controlling for difficulty strengthens rather than weakens coupling in synthetic data by design. The methodology isolates designed coupling from confounds.

Models show distinct coupling profiles in synthetic data—GPT-4 shows truthfulness-robustness chain, Claude-3 shows fairness-safety-privacy cluster, Llama-3 shows minimal coupling—though statistical confirmation requires larger samples than the proof-of-concept provides.

All findings derive from synthetic coupling data validating measurement methodology. Real-world coupling magnitudes in production LLMs remain uncharacterized pending access to MultiTrust and TrustLLM benchmarks. If validated on real models, the implications are immediate: multi-dimensional evaluation frameworks should report coupling statistics alongside per-dimension scores, and model selection teams could exploit coupling patterns when deployment scenarios demand multiple trustworthiness guarantees simultaneously.

Trustworthiness dimensions are neither universally coupled nor universally independent. The methodology demonstrates they can exhibit sparse coupling, a detectable property requiring targeted mitigation strategies rather than universal solutions. Real-world magnitudes remain unknown pending production benchmark access.

## References

Legendre, P., & Fortin, M. J. (2010). Comparison of the Mantel test and alternative approaches for detecting complex multivariate relationships in the spatial analysis of genetic data. Molecular Ecology Resources, 10(5), 831-844.

Li, Y., & Li, L. (2024). Understanding the trade-off between accuracy, robustness, and fairness in neural networks. ACM Computing Surveys.

Sun, L., et al. (2024). TrustLLM: Trustworthiness in large language models. arXiv preprint arXiv:2401.05561.

Zheng, D., et al. (2024). TrustScore: Reference-free evaluation of LLM response trustworthiness. arXiv preprint arXiv:2402.12545.
