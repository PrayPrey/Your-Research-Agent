# Experiments

Our experimental design tests four specific claims about coupling patterns in LLM trustworthiness dimensions. Rather than exploratory analysis, we frame each experiment as testing a hypothesis derived from our core insight: coupling exists but is sparse and model-specific.

## Experimental Questions

We structure our evaluation around four cascading questions:

1. **Does coupling exist?** (h-e1) We first establish whether co-occurrence patterns between trustworthiness dimensions exceed chance levels. Without detectable coupling, subsequent analyses are moot.

2. **Is coupling difficulty-independent?** (h-m1) Detecting correlation is insufficient—we must distinguish genuine shared vulnerabilities from spurious artifacts where hard instances fail on all dimensions simultaneously. Instance difficulty is a known confound in multi-dimensional evaluation.

3. **How broad is coupling?** (h-m2) If coupling exists and is genuine, does it span many dimension pairs (indicating broad architectural bottlenecks) or few pairs (suggesting targeted vulnerability clusters)?

4. **Are coupling profiles model-specific?** (h-c1) Do different models exhibit distinct coupling patterns—fingerprints reflecting different training approaches or architectural choices?

## Datasets

We evaluate three model variants (GPT-4, Claude-3-Sonnet, Llama-3-70B) on 500 instances per model, with 100 instances per trustworthiness dimension (truthfulness, robustness, fairness, safety, privacy). Each instance carries binary labels (pass/fail) for all five dimensions, enabling pairwise co-occurrence analysis across 10 dimension pairs.

**Synthetic data limitation:** All Phase 4 experiments used synthetic coupling data designed to emulate benchmark structure (MultiTrust/TrustLLM remain gated). Coupling patterns were initialized with target correlation values (phi 0.35-0.40 for truthfulness-robustness and fairness-safety pairs, phi 0.15-0.25 for remaining pairs) and perturbed with 7% noise to introduce model-specific variation. This validates measurement methodology but defers real-world coupling characterization to Phase 5.

## Experimental Design

### h-e1: Coupling Existence Test

**Method:** Phi coefficient analysis on 2×2 contingency tables (pass/fail on dimension A vs dimension B).

**Rationale:** Phi coefficient measures effect size for binary associations, interpretable on [0,1] scale where 0 indicates independence and 1 indicates perfect correlation. Unlike chi-square alone (significance test), phi quantifies coupling strength.

**Threshold:** phi ≥ 0.3 (medium effect size per Cohen's benchmarks) AND p < 0.01 (statistical significance).

**Gate criterion:** ≥1 model exhibits ≥1 significant dimension pair. This existence proof establishes coupling as a measurable phenomenon before characterizing its properties.

### h-m1: Difficulty-Independence Validation

**Method:** Dual validation approach:
1. **Partial correlation:** Control for instance difficulty via partial phi coefficient (phi_AB.D where D is difficulty score)
2. **Quartile stratification:** Split instances by difficulty quartiles (Q0=easy, Q3=hard) and compute phi within each quartile

**Rationale:** Instance difficulty is a known PMC (point of maximum correlation) confound—if hard instances fail on all dimensions, raw coupling estimates inflate. Partial correlation isolates genuine coupling from this artifact. Quartile stratification provides complementary non-parametric validation: if coupling persists across difficulty levels, it is not driven solely by hard instances.

**Threshold:** partial phi ≥ 0.25 for ≥2 dimension pairs AND coupling observable in ≥3 of 4 difficulty quartiles.

**Gate criterion:** MUST_WORK. Difficulty-independence distinguishes our claim (shared vulnerability mechanisms) from alternative explanation (measurement artifacts).

### h-m2: Coupling Breadth Analysis

**Method:** Count significant dimension pairs per model with Bonferroni correction for multiple testing (alpha = 0.01/30 tests ≈ 0.00033).

**Rationale:** Testing 10 dimension pairs × 3 models = 30 comparisons inflates family-wise error rate. Bonferroni correction controls false positives at cost of conservative thresholds. We preregistered ≥3 pairs per model as "broad coupling" threshold based on combinatorial argument: 10 pairs = sparse (1-2 pairs), moderate (3-5 pairs), broad (6+ pairs).

**Threshold:** ≥3 significant pairs (phi ≥ 0.3, p_adj < 0.01) for ≥2 of 3 models.

**Gate criterion:** SHOULD_WORK (exploratory). This tests our sparse coupling hypothesis (FAIL = narrow coupling, PASS = broad coupling).

### h-c1: Model-Specific Fingerprints

**Method:** Mantel test comparing 10×10 coupling matrices (phi values for all dimension pairs) across model pairs. Permutation test (10,000 iterations) generates null distribution of matrix correlations.

**Rationale:** If coupling profiles are model-specific, coupling matrices should differ structurally (low Pearson r between matrices). Mantel test accounts for matrix structure and provides significance test via permutation.

**Threshold:** Mantel r < 0.7 (low similarity) AND p < 0.0167 (Bonferroni-corrected for 3 model pairs) for ≥1 model pair.

**Gate criterion:** SHOULD_WORK. Model-specificity is the deployment-relevant finding (coupling as selection criterion).

## Metrics

- **Phi coefficient:** Effect size for 2×2 contingency tables, computed as sqrt(chi-square / n). Ranges [0,1] with interpretable thresholds (0.1=small, 0.3=medium, 0.5=large).
- **Chi-square p-value:** Statistical significance test for independence hypothesis. Alpha = 0.01 (conservative) to control false positives.
- **Partial phi:** Phi coefficient after removing linear relationship with difficulty score. Implemented via pingouin.partial_corr with Pearson method.
- **Mantel r:** Pearson correlation between vectorized upper-triangle entries of two coupling matrices. Permutation-based p-value via scikit-bio.stats.distance.mantel.

## Statistical Considerations

**Multiple testing correction:** h-m2 applies Bonferroni correction (alpha_adj = 0.01/30). h-e1/h-m1 test prespecified pairs (truthfulness-robustness, fairness-safety) without correction, justified by prior work documenting these couplings.

**Power analysis:** Mantel test requires n ≥ 500 instances/dimension for detecting r = 0.5 at 80% power (Legendre & Legendre). Our sample (n = 100/dimension) is underpowered for h-c1, acknowledged as limitation.

**Difficulty independence assumption:** Synthetic difficulty scores generated as Normal(0.5, 0.15) with constraint |corr(difficulty, dimension)| < 0.2. This ensures difficulty is uncorrelated with dimensions, validating independence assumption for partial correlation.

## Why These Choices Test the Claims

Each experiment maps directly to a claim in our sparse coupling hypothesis:

- **h-e1 → "Coupling exists":** Phi coefficient quantifies co-occurrence strength; significance test rejects independence hypothesis.
- **h-m1 → "Coupling reflects shared vulnerabilities":** Partial correlation isolates genuine coupling from difficulty confound; quartile persistence shows coupling isn't driven by hard-instance artifacts.
- **h-m2 → "Coupling is sparse":** Counting significant pairs across models reveals whether coupling is narrow (1-2 pairs) or broad (3+ pairs).
- **h-c1 → "Coupling profiles are model-specific":** Mantel test detects structural differences in coupling matrices, indicating distinct vulnerability architectures.

This cascading design builds evidence incrementally: existence → genuineness → breadth → specificity. Each experiment's success strengthens subsequent tests' interpretability.
