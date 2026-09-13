# Verification Plan: Geometric Uncertainty Quantification via Hidden State Subspace Analysis

**Date:** 2026-05-12
**Hypothesis ID:** H-GeometricUQ-v1
**Confidence:** 0.75
**Total Hypotheses:** 3

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under epistemic uncertainty conditions (factual knowledge questions in TruthfulQA), if we extract geometric features (participation ratio, eigenvalue spectrum, condition number) from layers 24-31 hidden states at pre-generation final token position, then these features will achieve Spearman |ρ| > 0.4 correlation with ground-truth semantic entropy, because uncertain model states exhibit lower-dimensional geometric signatures (collapsed subspaces) detectable via spectral analysis of the hidden state manifold.

### 1.2 Alternative Hypothesis (H0)
There is no significant correlation (|ρ| < 0.3 or p > 0.05) between geometric features extracted from pre-generation hidden states and semantic entropy on TruthfulQA. Any observed correlation is spurious and explained by confounds (sequence length, perplexity, token frequency).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA (standard) | Designed to elicit epistemic uncertainty - contains questions where models lack factual knowledge |
| **Model** | Llama-3-8B-Instruct | Standard instruction-tuned LLM with accessible hidden states, 32 layers enabling 24-31 range extraction |

**Dataset Details:**
- Source: HuggingFace datasets (truthful_qa, generation config)
- Path: truthful_qa/generation

**Model Details:**
- Type: decoder-only transformer
- Source: meta-llama/Meta-Llama-3-8B-Instruct

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Semantic Entropy (Farquhar et al. 2024) | AUROC ~0.80+ | TruthfulQA | ~1500ms latency per query (K=10 sampling + NLI), not production-viable for real-time |
| Semantic Entropy Probes (Kossen et al. 2024) | AUROC ~0.80 | TruthfulQA | Requires supervised training with SE labels, black-box predictions, not interpretable |
| SelfCheckGPT (Manakul et al. 2023) | AUROC ~0.75 | Multiple QA datasets | 5-20x latency overhead due to sampling, not real-time capable |
| Perplexity Baseline | - | - | Token-level perplexity from model logits (control baseline) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Semantic entropy from K=10 samples is sufficient ground truth for uncertainty | Farquhar et al., Nature 2024 validated this approach; convergence studies show K=10 is sufficient | Ground truth labels would be unreliable, making validation impossible |
| A2 | Layers 24-31 capture decision-relevant representations | Proximity to output logits suggests these layers encode final decision-making features | Would need layer ablation study to find optimal range; may shift to earlier/later layers |
| A3 | Participation ratio from 9 samples is statistically stable | Requires empirical validation via bootstrap CV < 0.15 | Multi-metric ensemble would compensate; could expand to 12-16 layers if needed |
| A4 | TruthfulQA epistemic uncertainty generalizes to other factual QA domains | TruthfulQA is standard benchmark for factual uncertainty | Hypothesis would be dataset-specific; would need cross-dataset validation |
| A5 | Geometric properties are architecture-invariant within Llama family | Initial scoping assumption based on shared transformer architecture | Would need per-architecture calibration; limits generalization claims |

### 1.6 Research Gap & Novelty

**Key Innovation:** Intrinsic geometric properties as interpretable uncertainty signals requiring only single forward pass, enabling <10ms production overhead.

**Differentiation from Prior Work:**
- **vs. Kossen et al. (2024):** They train supervised probe (black-box predictor), we use intrinsic geometry (interpretable, no training for feature extraction)
- **vs. Farquhar et al. (2024):** They compute SE via multi-sample NLI (~1500ms), we approximate with <10ms geometry computation
- **vs. SelfCheckGPT (Manakul et al. 2023):** They require 5-20 samples (5-20x latency), we achieve single-pass inference

**Scope Reduction:** 75% of claims are BUILD_ON (established facts from prior work). Only PROVE_NEW claims (geometric correlation, subspace collapse mechanism, single-pass approximation) require verification.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M-integrated | Mechanism | MUST_WORK | H-E1 | READY |
| H-C1 | Condition | SHOULD_WORK | H-E1, H-M-integrated | READY |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Geometric-Semantic Entropy Correlation

**Type:** EXISTENCE  
**Statement:** Under epistemic uncertainty conditions (TruthfulQA factual questions), if we extract geometric features (participation ratio, eigenvalue spectrum, condition number) from layers 24-31 hidden states at pre-generation final token position, then these features will achieve Spearman |ρ| > 0.4 correlation with ground-truth semantic entropy, because uncertain model states exhibit measurable geometric signatures.

**Rationale:** Validates the fundamental existence claim that geometric properties can serve as uncertainty proxies. Without established correlation, the entire hypothesis collapses.

**Variables:**
- IV: Participation Ratio (PR), Eigenvalue Decay Rate (α), Condition Number (κ)
- DV: Semantic Entropy (SE, 0-3 bits from K=10 sampling)
- CV: Model (Llama-3-8B-Instruct), layers (24-31), position (final token), SE parameters (K=10, T=0.7, DeBERTa-NLI)

**Verification Protocol:**
1. Load TruthfulQA dataset (817 questions), split 70/30 train/test
2. Extract hidden states from layers 24-31 at final token position for each question
3. Compute geometric features: PR = trace(C)²/(||C||²_F·d), eigenvalue decay α, condition number κ
4. Compute ground truth SE via K=10 sampling + DeBERTa-NLI clustering
5. Calculate Spearman correlation between each geometric feature and SE on test set
6. Bootstrap validation (1000 resamples) for 95% CI and stability check (CV < 0.15 for PR)

**Success Criteria:**
- Primary: Spearman |ρ| > 0.4 with 95% CI excluding 0.3, p < 0.001
- Secondary: Bootstrap CV < 0.15 for participation ratio (statistical stability)

**Gate:**
- Type: MUST_WORK
- If Fail: If |ρ| < 0.3 or p > 0.05, abandon hypothesis - geometric properties don't proxy uncertainty

**Prerequisites:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.6 Prediction P1, Phase 2A Readiness SH1

---

#### H-M-integrated: Four-Step Causal Mechanism Chain

**Type:** MECHANISM  
**Statement:** Under epistemic uncertainty, the complete causal mechanism operates: (1) Model encounters factual question lacking confident knowledge → (2) Pre-generation hidden states compress into lower-dimensional subspace → (3) Spectral signatures emerge (PR decreases, eigenvalue decay accelerates, condition number increases) → (4) Geometric properties correlate with semantic entropy, providing single-pass proxy.

**Rationale:** Explains WHY H-E1 correlation exists through mechanistic understanding. Validates each causal link to enable interpretable uncertainty detection rather than black-box correlation.

**Variables:**
- IV: Epistemic Uncertainty Condition (high-SE vs low-SE questions)
- DV: Subspace dimensionality (PR), spectral geometry (α, κ), correlation with SE
- CV: Model, layers, position, dataset split

**Verification Protocol:**
1. Split TruthfulQA test set by median SE into high-uncertainty and low-uncertainty groups
2. Compare mean PR, eigenvalue decay α, condition number κ between groups via t-test
3. Validate predicted directionality: PR_high < PR_low (collapsed subspace), κ_high > κ_low (ill-conditioned)
4. Regression analysis: verify negative slope for PR~SE, positive slope for κ~SE
5. Ablation study: test layer ranges (16-23, 20-27, 24-31) to justify layer selection empirically
6. Control validation: compare epistemic (TruthfulQA) vs non-epistemic tasks to confirm mechanism is epistemic-specific

**Success Criteria:**
- Primary: PR significantly lower for high-SE questions (t-test p < 0.01), negative Spearman correlation PR~SE
- Secondary: Eigenvalue decay faster for high-SE, condition number higher for high-SE, layer 24-31 outperforms other ranges

**Gate:**
- Type: MUST_WORK
- If Fail: If correlation direction reverses or no group differences, mechanism hypothesis fails - return to black-box approaches

**Prerequisites:** H-E1 (correlation must exist before explaining mechanism)

**Source:** Phase 2A Section 1.3 Causal Mechanism (4 steps), Phase 2A Readiness SH2

---

#### H-C1: Architecture Invariance within Llama Family

**Type:** CONDITION  
**Statement:** The geometric uncertainty mechanism generalizes across Llama-family architectures (Llama-2-7B, Llama-3-8B) with correlation magnitude degrading by no more than 0.15, meaning if Llama-3-8B achieves |ρ|=0.45, Llama-2-7B must achieve |ρ| ≥ 0.30.

**Rationale:** Tests the boundary condition of architecture generalization. Success enables broader deployment without per-model retraining; failure indicates architecture-specific calibration required.

**Variables:**
- IV: Model Architecture (Llama-2-7B vs Llama-3-8B)
- DV: Correlation magnitude (Spearman |ρ| between PR and SE)
- CV: Dataset (TruthfulQA test), SE computation (K=10, DeBERTa-NLI), layer range strategy

**Verification Protocol:**
1. Replicate H-E1 protocol on Llama-2-7B using identical methodology
2. Extract hidden states from layers 24-31 (or proportional final 25% of layers) at final token
3. Compute PR, eigenvalue decay, condition number using identical formulas
4. Calculate Spearman correlation between geometric features and SE
5. Compare correlation magnitudes: |Δρ| = |ρ_Llama2 - ρ_Llama3| must be ≤ 0.15
6. Ablation: test fixed (layers 24-31) vs proportional (final 25%) layer selection strategies

**Success Criteria:**
- Primary: |Δρ| ≤ 0.15 and both correlations remain |ρ| > 0.30
- Secondary: DeLong test shows no significant difference (p > 0.05), proportional range more robust than fixed

**Gate:**
- Type: SHOULD_WORK
- If Fail: If |Δρ| > 0.25 or Llama-2 drops to |ρ| < 0.25, limit claims to Llama-3 specific, flag need for per-architecture calibration

**Prerequisites:** H-E1 (correlation established on Llama-3), H-M-integrated (mechanism understood)

**Source:** Phase 2A Section 1.5 Scope (architecture-invariance assumption A5)

---

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 (Foundation)
  ↓
H-M-integrated (Mechanism explanation)
  ↓
H-C1 (Architecture generalization)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Spearman \|ρ\| > 0.4, p < 0.001, 95% CI excludes 0.3 | ABANDON - geometric properties don't proxy uncertainty |
| H-M-integrated | MUST_WORK | PR_high < PR_low (p<0.01), negative PR~SE correlation | PIVOT - correlation exists but mechanism wrong, use black-box |
| H-C1 | SHOULD_WORK | \|Δρ\| ≤ 0.15, both \|ρ\| > 0.30 | SCOPE - limit to Llama-3 specific, note calibration needed |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | Experiment Design (H-E1, H-M-integrated, H-C1) | 15-20 min |
| Phase 3 | Implementation Planning | 25-35 min |
| Phase 4 | Coding & PoC Validation | 2-4 hours |
| Phase 5 | Baseline Comparison (if enabled) | 1-2 hours |

**Total Duration:** 3-6 hours (PoC verification)

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-05-12*
