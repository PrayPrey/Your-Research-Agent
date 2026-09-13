# Phase 2C Research Notes: H-C1

**Hypothesis ID:** h-c1  
**Date:** 2026-08-19  
**Phase:** 2C (Experiment Design)

---

## Research Context

H-C1 tests whether coupling patterns across trustworthiness dimensions are model-specific (behavioral fingerprints) or universal (architectural property). This CONDITION hypothesis depends on:
- **h-e1 (PASS):** Confirmed coupling exists between trustworthiness dimensions
- **h-m2 (FAILED):** Multi-pair coupling not established, making cross-model comparison necessary

---

## Dataset Selection Research

### Primary Choice: TrustLLM Benchmark

**[VERIFIED - SCHOLAR]** Sun et al., "TrustLLM: Trustworthiness in Large Language Models" (2024)
- **Citations:** 361
- **Semantic Scholar ID:** fb4dc0178e5d7347b1615c48caf05347b6e5eb48
- **Availability:** Publicly available via Hugging Face (https://github.com/HowieHwong/TrustLLM)
- **Coverage:** 6 dimensions (truthfulness, safety, fairness, robustness, privacy, ethics)
- **Scale:** 30+ datasets, 16 models evaluated
- **Evaluation:** API-based (no internal states required)

**Decision rationale:**
- Most comprehensive multi-dimensional trustworthiness benchmark
- High citation count indicates field acceptance
- Public availability reduces dataset acquisition risk
- API-based evaluation matches our behavioral coupling approach

### Alternative: DecodingTrust

**[VERIFIED - SCHOLAR]** Wang et al., "DecodingTrust" (2024)
- **Coverage:** 8 trustworthiness dimensions
- **URL:** https://decodingtrust.github.io/
- **Status:** Fallback option if TrustLLM unavailable

### Composite Fallback

If neither TrustLLM nor DecodingTrust accessible:
- TruthfulQA (truthfulness)
- AdvGLUE (robustness)
- BBQ (fairness)
- CValues (safety)
- ConfAIde (privacy)

**Timeline impact:** +1 week for data collection/integration

---

## Statistical Method Research

### Mantel Test Implementation

**[VERIFIED - EXA]** jwcarr/mantel (GitHub)
- **URL:** https://github.com/jwcarr/mantel
- **Stars:** 37 | **License:** MIT
- **PyPI:** https://pypi.org/project/mantel/ (v2.2.3, updated 2025-12-09)
- **Dependencies:** numpy ≥1.10, scipy ≥1.0
- **Features:** Pearson/Spearman correlation, permutation testing, deterministic mode
- **Status:** Production-ready

**Alternative:** scikit-bio
- **URL:** https://github.com/scikit-bio/scikit-bio/blob/main/skbio/stats/distance/_mantel.py
- **Function:** `skbio.stats.distance.mantel()`
- **Features:** Multiple correlation methods, automatic ID matching
- **Status:** Heavier dependency but more robust for distance matrices

**Decision:** Use jwcarr/mantel as primary (lightweight), scikit-bio as fallback

### Phi Coefficient Implementation

**[VERIFIED - EXA - CODE_CONTEXT]** sklearn.metrics.matthews_corrcoef
- **Equivalence:** Matthews correlation coefficient = phi coefficient for 2×2 tables
- **Formula:** φ = (n11·n00 - n10·n01) / √(n1·n0·n·0·n·1)
- **Documentation:** https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html
- **Status:** Standard implementation, widely used

**Advanced option:** KaveIO/PhiK
- **URL:** https://github.com/kaveio/phik
- **Stars:** 171 | **License:** Apache 2.0
- **Features:** Generalization to categorical/ordinal/interval variables
- **Status:** Future extension possibility (not needed for binary coupling)

---

## Coupling Literature Review

### Multi-Dimensional Coupling Evidence

**[VERIFIED - SCHOLAR]** Xiao et al., "Enhancing Multiple Dimensions of Trustworthiness in LLMs via Sparse Activation Control" (2024)
- **Citations:** 9
- **Semantic Scholar ID:** 09992d02d809c9598c192277ec24c918849beca0
- **Key finding:** Demonstrates coupling between honesty, safety, and factuality dimensions via sparse activation control
- **Relevance:** Provides mechanistic evidence for dimension coupling (supports behavioral coupling hypothesis)
- **Implication:** If coupling has mechanistic basis, it may be model-specific (architecture-dependent)

### Trade-off Analysis

**[VERIFIED - SCHOLAR]** Li & Li, "Triangular Trade-off between Robustness, Accuracy, and Fairness in Deep Neural Networks: A Survey" (2024)
- **Citations:** 32
- **Semantic Scholar ID:** 13b0444d079bea1c8c57a6082200b67ab5f4616e
- **Key finding:** Systematic analysis of trade-offs between robustness, accuracy, and fairness
- **Relevance:** Establishes precedent for dimension coupling (trade-offs = negative coupling)
- **Implication:** Trade-offs may manifest as negative phi coefficients in coupling matrix

---

## Sample Size Determination

### Statistical Power Analysis

**Requirement:** Chi-square test validity requires expected frequency ≥5 per cell in 2×2 contingency table

**Target:** 500 instances per model
- 100 instances per dimension × 5 dimensions
- 10 pairwise comparisons per model
- Each comparison has n=100 pairs

**Effect size detection:**
- Medium effect (φ=0.3) requires n≥100 per pair for 80% power
- Large effect (φ=0.5) requires n≥30 per pair
- Conservative choice: n=100 ensures detection of medium effects

**Justification:**
- Too small (n<50): Risk of Type II error (missing real coupling)
- Too large (n>1000): Computational cost without statistical gain
- 500 instances balances power vs. cost

---

## Cross-Model Comparison Strategy

### Model Selection

**Target models:**
1. **GPT-4** (OpenAI) - Frontier closed model
2. **Claude 3** (Anthropic) - Alternative frontier model
3. **Llama 3** (Meta) - Open-source frontier model

**Rationale:**
- Diverse architectures (different training data, RLHF strategies)
- All evaluated in TrustLLM benchmark
- Representative of deployment landscape

### Mantel Test Interpretation Thresholds

**r < 0.7:** Distinct coupling profiles → Model-specific fingerprints (PASS)
- Moderate-to-low correlation indicates substantial differences
- Justification: r=0.7 means 49% shared variance, 51% model-specific

**0.7 ≤ r < 0.9:** Moderate similarity (PARTIAL)
- Mixed universal + model-specific components
- Justification: Some architectural commonality with residual differences

**r ≥ 0.9:** Nearly identical coupling → Universal property (FAIL)
- High correlation indicates architectural constraint
- Justification: r=0.9 means 81% shared variance, coupling driven by transformer architecture

**Multiple testing correction:**
- 3 pairwise comparisons → Bonferroni-adjusted α = 0.05/3 = 0.0167
- Conservative approach prevents false positives

---

## Risk Assessment

### Risk 1: Cross-Model Homogeneity (40% likelihood)

**Symptom:** Mantel r > 0.9 for all pairs

**Why likely:**
- All models use transformer architecture
- RLHF may induce universal coupling patterns
- Prerequisite h-m2 FAILED (insufficient multi-pair coupling variation)

**Mitigation:**
- Reframe as "universal coupling architecture" discovery
- Compute partial correlations controlling for model size
- Still publishable as negative result (Tier 2)

### Risk 2: Insufficient Coupling Variation (30% likelihood)

**Symptom:** All phi coefficients in narrow range (0.25-0.35) across models

**Why likely:**
- h-e1 showed coupling exists but didn't quantify strength distribution
- Narrow phi range → small Mantel correlation differences

**Mitigation:**
- Increase sample size to 1000 instances (improves precision)
- Use dimension-specific binarization thresholds (vs. median split)
- Report narrow effect sizes with confidence intervals

### Risk 3: Dataset Unavailability (10% likelihood)

**Symptom:** TrustLLM/DecodingTrust not accessible

**Mitigation:**
- Fallback to composite benchmark (TruthfulQA + AdvGLUE + BBQ + CValues + ConfAIde)
- API-based re-evaluation if needed
- Timeline impact: +1 week

---

## Expected Outcomes Analysis

### Scenario A: PASS (r < 0.7 for ≥1 pair)

**Likelihood:** 30%

**Narrative:** "Coupling patterns as model selection criteria"
- Model-specific fingerprints enable evidence-based deployment
- Example: High robustness-fairness coupling in Claude → preferred for safety-critical apps

**Publication tier:** Tier 1 (positive result, novel contribution)

### Scenario B: FAIL (r ≥ 0.9 for all pairs)

**Likelihood:** 40%

**Narrative:** "Universal coupling architecture in LLMs"
- First characterization of fundamental architectural property
- All transformer models exhibit similar coupling patterns
- Reframe from "fingerprints" to "architectural constraints"

**Publication tier:** Tier 2 (publishable negative result)

### Scenario C: PARTIAL (0.7 ≤ r < 0.9)

**Likelihood:** 30%

**Narrative:** "Hybrid coupling: universal + model-specific components"
- Some coupling patterns universal (architecture)
- Some patterns model-specific (training/RLHF)
- Decompose into shared vs. residual components

**Publication tier:** Tier 1 (nuanced positive result)

---

## Phase 2C Deliverables

✅ **02c_experiment_brief.md:** Complete experiment specification
- Dataset: TrustLLM (500 instances per model)
- Method: Mantel test on coupling matrices
- Success criterion: r < 0.7 for ≥1 model pair
- Statistical validation: Bonferroni-corrected α=0.0167

✅ **Implementation resources identified:**
- jwcarr/mantel (Mantel test)
- sklearn.metrics.matthews_corrcoef (phi coefficient)
- scipy.stats.chi2_contingency (significance testing)

✅ **Risk mitigation strategies defined:**
- Cross-model homogeneity → reframe as universal coupling
- Insufficient variation → increase sample size
- Dataset unavailability → composite benchmark fallback

---

## Phase 3 Readiness

**Status:** READY FOR PHASE 3

**Next steps:**
1. Generate PRD (Product Requirements Document)
2. Design Architecture (module decomposition)
3. Specify Logic (pseudo-code for coupling/Mantel functions)
4. Define Config (hyperparameters, thresholds)
5. Create Archon task breakdown

**Expected Phase 3 duration:** 3 hours  
**Expected Phase 4 duration:** 6 hours  
**Total h-c1 timeline:** 9 hours

---

**Research Notes Status:** COMPLETE  
**Date:** 2026-08-19  
**Next Phase:** Phase 3 (Implementation Planning)
