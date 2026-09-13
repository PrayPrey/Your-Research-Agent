# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-GMS-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition that two neural network models are fine-tuned from the same pre-trained base with Linear Mode Connectivity (LMC), if we compute a Geometric Mergeability Score (GMS) combining gradient alignment (α), singular value subspace overlap (β), and Fisher information distance (γ), then models with GMS > τ will merge successfully with bounded performance loss ε, because GMS quantifies the loss barrier height between models in parameter space.

**Alternative Hypothesis (H0):**
There is no significant correlation between the proposed GMS metric and actual model merging performance; the three GMS components (α, β, γ) do not provide predictive power beyond random selection of model pairs.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Gradient Alignment (α) | Independent | Cosine similarity: α = cos(g_A, g_B) on validation batch at base model parameters | [-1.0, 1.0]; high values (>0.5) indicate compatible tasks |
| SVD Overlap (β) | Independent | Frobenius norm of top-k singular vector overlap: β = \|\|U_A^T U_B\|\|_F / √k using randomized SVD, k=50 | [0.0, 1.0]; high values (>0.7) indicate shared subspace |
| Fisher Distance (γ) | Independent | Diagonal Fisher-Rao distance: γ = √(Σᵢ (θ_A^i - θ_B^i)² · (F_A^i + F_B^i)/2) using empirical Fisher on validation set | [0, ∞); low values (<1.0) indicate similar importance weighting |
| Merged Performance | Dependent | Accuracy on both tasks after averaging: L(0.5θ_A + 0.5θ_B) | [0%, 100%] |
| GMS Prediction Accuracy | Dependent | Spearman correlation between GMS and merge performance across model pairs | ρ > 0.7 for strong correlation |
| Model Architecture | Controlled | Fixed to same architecture (e.g., ViT-B/16, RoBERTa-base) | Same for all model pairs |
| Base Model | Controlled | Same pre-trained checkpoint (ImageNet-21k or similar) | Fixed |
| Merge Ratio λ | Controlled | Fixed at 0.5 for uniform averaging | 0.5 |

### 1.3 Causal Mechanism

**Causal Chain (N=2):**

```
Step 1: GMS Components (α, β, γ) → Loss Barrier Height Estimation
   ↓
Step 2: Loss Barrier Height Estimation → Merge Success Prediction
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Landscaping LMC (2024) | Barrier height directly determines merge performance via "mountainside and ridge" model | Strong |
| Step1 → Step2 | Demystifying Mergeability (2026) | "subspace overlap and gradient alignment consistently emerge as foundational, method-agnostic prerequisites" | Strong |
| α component | Demystifying Mergeability (2026) | Gradient alignment is method-agnostic predictor of merge success | Strong |
| β component | TSV-Merge (2024, 64 citations) | Top-k singular vectors capture 99% task information; subspace overlap measures interference | Strong |
| γ component | A Unified Analysis for FWA (2024) | Fisher-weighted averaging provides convergence bounds O(log(T/k)/√T) | Medium |

**Key Tension:**
- **Tension:** Demystifying Mergeability (2026) found "substantial variation in success drivers (46.7% metric overlap; 55.3% sign agreement)" across different merging methods
- **Resolution:** GMS uses equal weights (w₁ = w₂ = w₃ = 1/3) as default to capture method-agnostic foundations; method-specific weight tuning is future work

### 1.4 Key Assumptions

1. **Linear Mode Connectivity (LMC) holds for fine-tuned models**
   - Evidence: Model Soups (1322 citations), Landscaping LMC (2024)
   - Consequence if violated: GMS would not correlate with merge success

2. **Task-specific information concentrates in top-k singular values**
   - Evidence: TSV-Merge (10% → 99% accuracy)
   - Consequence if violated: SVD overlap (β) would miss important task-specific information

3. **Fisher diagonal approximation captures parameter importance sufficiently**
   - Evidence: Standard in PEFT/pruning literature
   - Consequence if violated: Fisher distance (γ) would underestimate parameter importance

4. **GMS components provide complementary (non-redundant) information**
   - Evidence: Each measures different geometric aspect
   - Consequence if violated: Unified GMS would be redundant; single component would suffice

### 1.5 Scope & Boundaries

**Applies to:**
- LoRA adapters fine-tuned from same base
- Full fine-tuned models from same pre-trained checkpoint
- Same-architecture model pairs

**Does NOT apply to:**
- Cross-architecture merging (e.g., ViT + ResNet)
- Fundamentally incompatible tasks (e.g., classification + generation)
- Models trained from different random initializations

**Known limitations:**
- Threshold τ may require per-domain calibration
- Equal weights may not be optimal for all merging methods
- Theoretical bounds are sketches, not formal proofs

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (GMS-Performance Correlation):**
GMS will achieve Spearman correlation ρ > 0.7 with merged model performance across diverse model pairs.

*Measurement:*
- Spearman ρ > 0.7 with p < 0.05
- Sample: n ≥ 30 model pairs across 3+ task families
- Statistical test: Spearman rank correlation with bootstrap 95% CI

*Basis:*
Demystifying Mergeability (2026) shows gradient alignment + subspace overlap are foundational predictors

**Secondary Predictions:**

**P2 (Component Complementarity):**
Each GMS component (α, β, γ) will contribute independently, with pairwise correlations < 0.7.

**P3 (Threshold Generalization):**
Threshold τ calibrated on one task family will generalize to held-out families with AUC > 0.75.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure:** ρ < 0.5 between GMS and merge performance
2. **Redundancy Failure:** Pairwise correlation between α, β, γ > 0.9
3. **Generalization Failure:** Threshold τ fails to transfer (AUC < 0.6)
4. **Baseline Failure:** GMS does not outperform random selection (AUC ≤ 0.5)

### 1.7 Statistical Verification Design

**Sample Size:** n ≥ 30 model pairs (power analysis for ρ detection)
**Statistical Test:** Spearman correlation, bootstrap 95% CI
**Report Format:** ρ, 95% CI, p-value, component correlation matrix

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the proposed GMS metric correlate significantly (ρ > 0.5) with merged model performance?"
- Maps to: Primary prediction P1
- Verification type: Empirical correlation analysis
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is the proposed geometric mechanism (barrier height estimation via α, β, γ) the actual cause of predictive power?"
- Maps to: Causal chain (N=2 steps)
- Decomposes into:
  - **H-M1:** GMS components collectively estimate loss barrier height
  - **H-M2:** Low barrier height implies merge success
- Verification type: Causal analysis (component ablation)

**SH3 (Comparison):**
"Does GMS outperform baseline prediction methods (random selection, single-component predictors)?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical

**Total Sub-Hypotheses for Phase 2B:** 4 (SH1, H-M1, H-M2, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-GMS-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=2 steps)
- [x] Causal chain length (N=2) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist
- [x] Falsification criteria defined
- [x] Baselines identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** ~1 GPU-hour per model pair; ~2-3 days for full validation
2. **Data Availability:** Need 30+ fine-tuned models from HuggingFace across 3 task families
3. **Priority Order:** SH1 (existence) → H-M1/H-M2 (mechanism) → SH3 (comparison)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
