# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-BioConstruct-SC-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of [single-cell foundation models evaluated on standardized benchmark task batteries], if [a hierarchical Item Response Theory measurement framework combined with multi-source construct validity assessment is applied], then [biological representation quality can be rigorously measured as latent constructs on common scales, enabling fair cross-model comparison and operational definition of "meaningful representation"] because [psychometric measurement theory provides 70+ years of established mathematical foundations for latent trait estimation, and construct validity criteria (convergent, discriminant, criterion) operationalize meaningfulness through empirical evidence requirements].

**Alternative Hypothesis (H0):**
Biological foundation model representation quality cannot be meaningfully decomposed into measurable latent constructs, OR hierarchical IRT methodology is fundamentally inappropriate for biological task performance data (violates core assumptions beyond repair), OR construct validity evidence provides no additional information beyond raw task performance metrics.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Foundation model architecture | Independent | Model identifier (scGPT, Geneformer, UCE, scEMB, etc.) with architecture family categorization | ~10-15 models across 3-4 architecture families |
| Hierarchical IRT ability estimates (θ_general) | Dependent | General biological understanding factor estimated via bifactor IRT model using TAM R package or mirt-py | θ ∈ [-3, +3] on standardized scale |
| Hierarchical IRT ability estimates (θ_specific) | Dependent | Construct-specific ability factors (empirically determined via EFA, expected 2-4 constructs) | θ ∈ [-3, +3] per construct |
| Convergent validity coefficient | Dependent | Correlation between model embeddings for similar cell types across independent datasets | r > 0.7 indicates strong convergent validity |
| Discriminant validity coefficient | Dependent | Separation between functionally distinct cell types in embedding space | Silhouette > 0.3 indicates adequate discriminant validity |
| Criterion validity coefficient | Dependent | Correlation between model predictions and multi-source biological ground truth consensus | r > 0.5 with ≥2/3 source agreement |
| Task battery | Controlled | Fixed set of 80 calibrated benchmark tasks spanning empirically-determined biological constructs | 20 tasks per construct (estimated 4 constructs) |
| Ground truth sources | Controlled | ENCODE ChIP-seq GRNs, Reactome/KEGG pathways, Perturb-seq Atlas | Consensus required from ≥2 of 3 sources |

### 1.3 Causal Mechanism

**Step 1: Exploratory Factor Analysis → Construct Structure**
Apply EFA to model × task performance matrix to identify empirical construct structure. Expected 2-4 interpretable factors.

**Step 2: Construct Structure → Hierarchical IRT Specification**
Specify bifactor IRT model with general factor (θ_general) and specific factors (θ_specific₁...θ_specificₖ).

**Step 3: Hierarchical IRT Calibration → Ability Estimates**
Estimate model ability parameters using MCMC or EM algorithm. Place all models on common measurement scale via equating.

**Step 4: Ability Estimates + Ground Truth → Construct Validity Evidence**
Assess convergent, discriminant, and criterion validity using multi-source biological ground truth.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| EFA → Constructs | Janssen et al. (2000) Hierarchical IRT | Factor analysis identifies latent constructs from response patterns | Strong |
| Constructs → Bifactor IRT | Mun et al. (2019) Multivariate HO-IRT | Higher-order structure estimable via MCMC | Strong |
| IRT → Ability Estimates | TAM R package, mirt-py | Established software with convergence diagnostics | Strong |
| Estimates → Validity | Wu et al. (2025) scFM Benchmark | 12 metrics including knowledge-based evaluation | Medium |

**Key Tension:**
- **Tension:** Traditional IRT assumes large examinee samples (N>100), but only ~10-15 foundation models exist.
- **Resolution:** Hierarchical IRT reduces parameters; bootstrap quantifies uncertainty; Bayesian estimation handles small samples.

### 1.4 Key Assumptions

1. **Biological understanding decomposes into measurable latent constructs**
   - Consequence if violated: Framework reduces to single-factor model (still useful but less informative)

2. **Hierarchical IRT assumptions hold with bifactor specification**
   - Consequence if violated: Model misfit detected via posterior predictive checks; alternative IRT models available

3. **Task performance reflects representation quality, not memorization**
   - Consequence if violated: Validity evidence would show inconsistent patterns across task types

4. **Multi-source ground truth consensus provides reliable criterion validity**
   - Consequence if violated: Criterion validity inconclusive; convergent/discriminant validity still informative

5. **Construct structure stable across architecture families**
   - Consequence if violated: Separate structures per family; cross-family comparison limited

### 1.5 Scope & Boundaries

**Applies to:** Single-cell foundation models, representation learning evaluation, task batteries with sufficient diversity

**Does NOT apply to:** Cross-scale models, protein language models, real-time deployment evaluation, structure prediction models

**Known Limitations:** Small model sample size, incomplete ground truth coverage, single-cell domain specificity

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Construct Validity Predicts Generalization):**
Models with higher construct validity scores (convergent r > 0.7, discriminant silhouette > 0.3, criterion r > 0.5) will demonstrate superior generalization to held-out tasks compared to models with high raw performance but low validity.

*Measurement:* Independent t-test or Mann-Whitney U, α = 0.05, Cohen's d > 0.5 expected

**Secondary Predictions:**

**P2 (Hierarchical Structure Provides Information Gain):**
Bifactor model will show significantly better fit than single-factor model (ΔBIC > 10, ΔAIC > 10).

**P3 (Cross-Model Ranking Consistency):**
IRT-based ability rankings (θ_general) will correlate (r > 0.6) with aggregate task rankings but provide additional construct-specific information.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:
1. **Factor Analysis Failure:** EFA yields no interpretable factor structure
2. **Model Misfit:** Hierarchical IRT fails posterior predictive checks or convergence
3. **Validity-Generalization Dissociation:** High validity scores show no relationship (r < 0.2) with generalization
4. **Ground Truth Disagreement:** Sources disagree fundamentally (pairwise r < 0.3)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 10 models per group; bootstrap uncertainty quantification essential
**Tests:** Independent t-test/Mann-Whitney U (α = 0.05); Parallel analysis + MAP for dimensionality; Posterior predictive checks
**Report Format:** Point estimates with 95% CI, effect sizes (Cohen's d, r), bootstrap-based IRT parameter uncertainty

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does biological foundation model task performance data contain latent construct structure identifiable via exploratory factor analysis?"
- Verification type: Empirical (EFA on model-task matrix)
- Critical: MUST PASS for framework to proceed

**SH2 (Mechanism):**
"Does the proposed 4-step causal mechanism produce reliable and valid measurements?"

Decomposes into 4 sub-hypotheses:
- H-M1: EFA → Construct Structure
- H-M2: Construct Structure → Hierarchical IRT Specification
- H-M3: Hierarchical IRT → Ability Estimates
- H-M4: Ability Estimates + Ground Truth → Validity Evidence

**SH3 (Comparison):**
"Does BioConstruct-SC provide superior evaluation compared to existing task-specific metrics?"
- Maps to: P1 (validity-generalization) and P3 (ranking consistency)

**Total sub-hypotheses in Phase 2B:** 6 (SH1 + 4 mechanism + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-BioConstruct-SC-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] Testable predictions (P1 primary, P2-P3 secondary)
- [x] Falsification criteria defined (4 criteria)
- [x] Baselines identified
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **Data Availability:** Are task performance data available for ~10-15 foundation models on comparable task sets?
2. **Factor Analysis Feasibility:** Is model-to-task ratio sufficient for stable EFA? May need regularization.
3. **Implementation Priority:** Sequential recommended - SH1 first, then mechanism verification.
4. **Ground Truth Assembly:** Data engineering effort required for ENCODE, Reactome, Perturb-seq integration.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
