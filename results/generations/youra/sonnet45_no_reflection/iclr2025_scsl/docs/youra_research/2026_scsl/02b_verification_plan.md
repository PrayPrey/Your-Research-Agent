# Verification Plan: Jacobian Stable Rank Unified Efficiency Framework

**Date:** 2026-05-12
**Hypothesis ID:** H-JacobianStableRank-v1
**Confidence:** 0.75
**Total Hypotheses:** 2

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under pretraining with residual-corrected Jacobian stable rank regularization, if models are trained to minimize sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2 per layer, then they will exhibit cross-level efficiency properties (low-rank adaptation, KV compressibility, sparse attention), because the layer-wise Jacobian constraint propagates through Fisher spectrum, activation covariance, and attention entropy structures.

### 1.2 Alternative Hypothesis (H0)
There is no significant correlation (Pearson r < 0.3) between residual-corrected Jacobian stable rank and efficiency metrics (LoRA rank, KV compression ratio, attention entropy) across layers and random seeds at iso-perplexity.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | C4 (primary), The Stack (domain robustness) (standard) | C4 provides standard natural language pretraining. The Stack tests domain robustness (high-entropy code). Both are existing, real datasets meeting feasibility constraints. |
| **Model** | Transformer (GPT-2 style decoder) | Standard architecture with clear layer-wise Jacobian structure (J_ℓ = I + J̃_ℓ due to residual connections). Enables residual-corrected stable rank computation. Pre-norm variant preferred for stable training dynamics. |

**Dataset Details:**
- Source: HuggingFace Datasets
- Path: allenai/c4 (10B token subset for Phase 1), bigcode/the-stack (code corpus for Phase 2 robustness)

**Model Details:**
- Type: Autoregressive decoder-only transformer
- Source: HuggingFace Transformers library

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard Transformer Pretraining | Perplexity baseline on C4/The Stack (to be measured) | C4, The Stack |
| ARD-LoRA + KV Compression + Sparse Attention (Independent Stack) | State-of-art efficiency via independent optimization of each dimension | Varies per technique |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Local linearization of transformer blocks is globally informative for KV covariance structure | Linearized propagation Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T used in neural tangent kernel (NTK) analysis | If nonlinearities (GELU, attention softmax) destroy linearization, Jacobian rank won't predict KV compressibility. Noise-transport experiment required to validate. |
| A2 | Fisher information matrix approximation F ≈ J^T J holds under entropy-controlled conditions | Standard approximation for locally linear models with isotropic output noise | If output entropy dominates Fisher spectrum more than Jacobian structure, correlation will collapse when entropy-controlled. Requires direct empirical Fisher measurement. |
| A3 | Iso-perplexity control ensures functional capacity is preserved (no over-constraint) | Perplexity is standard measure of language modeling quality | If capacity redistributes unevenly (early layers collapse, later layers compensate), global constraint is actually depth reallocation. Layerwise sensitivity audit required. |
| A4 | Spectral norm estimation via randomized power iteration has acceptable measurement noise (CV < 15%) | 10 probe vectors with 5 iterations gives CV ~5-8% based on Lanczos method studies | If CV > 20%, correlation tests are noise-dominated and statistically underpowered. Requires upfront measurement validation on 50M toy model. |
| A5 | Correlation between stable rank and efficiency metrics reflects structural coupling, not confounds (corpus entropy, model width, optimizer bias) | Mediation analysis can test whether stable rank explains variance beyond confounds | If mediation analysis shows stable rank explains < 30% of variance after controlling for confounds, correlation is spurious. Requires explicit mediation tests in Phase 2. |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First work to test whether parameter efficiency (LoRA), memory efficiency (KV compression), and computational efficiency (sparse attention) are correlated manifestations of a single structural property (Jacobian stable rank) vs. independent dimensions requiring separate optimization.

**Key Innovation:** Shifts paradigm from post-hoc efficiency engineering (train general model → add LoRA → compress KV → sparsify attention) to pretraining-time emergence of efficiency-ready models via unified structural constraint.

**Differentiation:**
- **vs. ARD-LoRA (Shinwari et al. 2025):** ARD-LoRA optimizes rank allocation during fine-tuning, assumes pretrained model as given. Our framework optimizes for adaptation-readiness during pretraining by constraining Jacobian stable rank.
- **vs. KV-CAT (Gelberg et al. 2026):** KV-CAT trains for KV compressibility in isolation, doesn't consider interaction with parameter efficiency or attention structure. We test mechanistic coupling via shared Jacobian constraint.
- **vs. Mamba-2 (Dao & Gu 2024):** Mamba-2 is architectural change (SSMs replacing attention). We propose objective-level change (stable rank regularization) that's architecture-agnostic and tests correlation hypothesis.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M-integrated | Mechanism | SHOULD_WORK | H-E1 | READY |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Stable Rank Reducibility

**Statement**: Under pretraining with explicit residual-corrected Jacobian stable rank (sr_ℓ^res) regularization, if models are trained to minimize sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2 per layer, then mean stable rank reduces by ≥20% relative to baseline while maintaining iso-perplexity (≤1% deviation), because the regularization directly constrains the effective rank of layer-wise representation transformations.

**Rationale**: This hypothesis validates that the proposed stable rank metric is (1) measurable with acceptable noise (CV < 15%), (2) controllable via gradient-based optimization, and (3) reducible without sacrificing model quality. It is the foundation for all downstream mechanistic claims.

**Variables** (from Phase 2A):
- **Independent**: Regularization Type (baseline, explicit sr_ℓ^res penalty, implicit control via adaptive LR)
- **Dependent**: Residual-Corrected Jacobian Stable Rank (sr_ℓ^res via Hutchinson trace + randomized power iteration)
- **Controlled**: Perplexity (≤1% deviation), Model Width (125M, d=768), Training Corpus (C4, 10B tokens), Random Seeds (3 per variant)

**Verification Protocol**:
1. Pretrain three 125M GPT-2 models on C4 (10B tokens): baseline, explicit sr_ℓ^res regularization, implicit control
2. Measure per-layer sr_ℓ^res every 1000 steps via Hutchinson trace (10 vectors) + randomized power iteration (5 iterations)
3. Tune regularization weight λ adaptively to maintain iso-perplexity (≤1% deviation across all variants)
4. Compute mean sr_ℓ^res reduction relative to baseline, layer-wise variance, and measurement CV
5. Validate upfront on 50M toy model that spectral norm estimation achieves CV < 15% before Phase 1 commitment

**Success Criteria**:
- **Primary**: Mean sr_ℓ^res reduction ≥20% in explicit regularization vs baseline, AND perplexity deviation ≤1%
- **Secondary**: Layer variance in rank reduction <2× mean (no compensatory redistribution), AND measurement CV <15%

**Failure Response**:
- IF sr_ℓ^res reduction <20%: Regularization too weak → increase λ range or explore alternative penalties
- IF perplexity degrades >1%: Over-constraint → relax λ or add capacity buffer
- IF CV >20%: Measurement unreliable → refine estimators or use gradient norm proxies → ABORT Phase 1

**Gate**:
- **Type**: MUST_WORK
- **If Fail**: The stable rank metric itself is not controllable → invalidates entire hypothesis chain → pivot to alternative structural metrics (e.g., effective rank via SVD, gradient flow analysis)

**Prerequisites**: None (foundation hypothesis)

**Source**: Phase 2A Prediction P1, Causal Step 1

---

#### H-M-integrated: Mechanistic Propagation Chain

**Statement**: Under residual-corrected Jacobian stable rank regularization during pretraining, if sr_ℓ^res is reduced by ≥20% (H-E1 validated), then Pearson correlation r ≥0.5 exists between sr_ℓ^res and efficiency metrics (intrinsic LoRA rank, KV covariance effective rank, attention entropy) across layers and seeds, because the Jacobian constraint propagates through Fisher spectrum (F ≈ J^T J), activation covariance (Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T), and attention entropy structure, manifesting as cross-level efficiency properties.

**Rationale**: This hypothesis tests the core mechanistic claim that stable rank is not merely correlated with efficiency but structurally coupled via mathematical propagation through linearized dynamics. It integrates all three causal steps (constraint → propagation → manifestation) into a unified correlation test with mechanistic validation via entropy-controlled Fisher measurement and noise-transport experiments.

**Variables** (from Phase 2A):
- **Independent**: Residual-Corrected Jacobian Stable Rank (mean sr_ℓ^res from H-E1 validated models)
- **Dependent**: Intrinsic LoRA Rank (95% accuracy via random direction probes), KV Covariance Effective Rank (SVD at 90% variance), Attention Entropy (-Σ p_ij log p_ij per layer)
- **Controlled**: Perplexity (iso-perplexity from H-E1), Corpus Entropy (C4 natural language primary, The Stack code for robustness), Model Width (125M baseline, 350M and 1B for scaling), Random Seeds (3 per variant)

**Verification Protocol**:
1. Use H-E1 validated models (baseline, explicit sr_ℓ^res, implicit control) for post-training measurements
2. Measure efficiency metrics: LoRA rank via random direction probes on GLUE/SQuAD, KV rank via empirical covariance SVD, attention entropy averaged per layer
3. Compute Pearson correlations between sr_ℓ^res and each efficiency metric across layers (12 layers) and seeds (3 seeds) = 36 data points per metric
4. Run mediation analysis: structural equation modeling with sr_ℓ^res as mediator, confounds (corpus entropy, model width) as covariates, efficiency as outcome
5. Mechanistic validation: (a) Entropy-controlled Fisher measurement to validate F ≈ J^T J assumption, (b) Noise-transport experiment (inject isotropic Gaussian at layer ℓ, measure output covariance rank)

**Success Criteria**:
- **Primary**: Pearson r ≥0.5 between sr_ℓ^res and all three efficiency metrics (LoRA, KV, attention), AND mediation analysis shows sr_ℓ^res explains ≥50% variance beyond confounds
- **Secondary**: Entropy-controlled Fisher test maintains r ≥0.5 (validates mechanism under controlled conditions)

**Failure Response**:
- IF r <0.3 for any two metrics: Efficiency dimensions are independent → valuable negative result → ABANDON unified framework, document orthogonality
- IF correlation exists but mediation <30%: sr_ℓ^res is proxy not causal driver → PIVOT to optimizer implicit bias study
- IF entropy-controlled Fisher r <0.3: Linearization assumption violated → EXPLORE nonlinear propagation models

**Gate**:
- **Type**: SHOULD_WORK
- **If Fail**: If correlation exists but mediation fails, pivot to optimizer dynamics research. If no correlation, confirms efficiency dimensions are orthogonal (valuable negative result). Phase 5 comparison may still show unified objective has practical benefits even without mechanistic coupling.

**Prerequisites**: H-E1 (validated stable rank reducibility with measurement infrastructure)

**Source**: Phase 2A Predictions P2-P3, Causal Steps 2-3 (integrated)

---

---

## 3. Risk Analysis

### Risk Identification from Key Assumptions

Each key assumption (A1-A5) from Phase 2A represents a potential failure point. This section maps assumptions to risks, identifies affected hypotheses, and defines mitigation strategies.

---

**Risk R1: Linearization Breakdown**

**Source Assumption:** A1 - Local linearization of transformer blocks is globally informative for KV covariance structure

**Description:** If nonlinearities (GELU, attention softmax) destroy the linearization assumption Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T, then Jacobian rank measurements won't predict KV compressibility, breaking the mechanistic link between stable rank and efficiency metrics.

**Affected Hypotheses:** H-M-integrated (mechanistic propagation claim)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Run noise-transport experiment (inject isotropic Gaussian perturbations at layer ℓ, measure output covariance rank) to empirically validate linearized propagation
2. **Detection:** Compare predicted covariance rank (from Jacobian product) vs. empirical covariance rank - divergence >30% indicates linearization failure
3. **Response:**
   - PIVOT: If linearization fails, explore nonlinear propagation models (e.g., higher-order Taylor terms, kernel methods)
   - SCOPE: Restrict claims to layers where linearization holds (typically early-middle layers)
   - ABORT: If linearization fails everywhere, mechanistic coupling claim is invalid - but correlation tests can still validate empirical coupling

**Early Warning Indicators:**
- Noise-transport experiment shows covariance rank divergence >30% from linearized prediction
- Layer-wise correlation analysis shows correlation collapse in deeper layers (where nonlinearity dominates)

---

**Risk R2: Fisher Approximation Invalidity**

**Source Assumption:** A2 - Fisher information matrix approximation F ≈ J^T J holds under entropy-controlled conditions

**Description:** If output entropy dominates Fisher spectrum more than Jacobian structure, then the assumed link F ≈ J^T J breaks down, and Fisher rank won't correlate with stable rank even if Jacobian coupling is real.

**Affected Hypotheses:** H-M-integrated (Fisher spectrum propagation)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Conduct entropy-controlled Fisher measurement by temperature-scaling logits to control output entropy, then measure Fisher rank directly
2. **Detection:** Compare entropy-controlled Fisher rank vs. sr_ℓ^res correlation - if r <0.3 under entropy control, Fisher approximation fails
3. **Response:**
   - PIVOT: If Fisher approximation fails, use gradient flow metrics (gradient norm ratios, Hessian spectral analysis) as alternative mechanistic measures
   - SCOPE: Restrict Fisher-based claims to temperature-scaled regime where approximation holds
   - ABORT: If entropy-controlled Fisher shows no correlation, Fisher propagation mechanism is invalid

**Early Warning Indicators:**
- Entropy-controlled Fisher correlation r <0.3 (vs. expected r ≥0.5)
- Temperature scaling significantly changes correlation magnitude (indicates entropy confound)

---

**Risk R3: Capacity Redistribution (Layerwise Collapse)**

**Source Assumption:** A3 - Iso-perplexity control ensures functional capacity is preserved (no over-constraint)

**Description:** If stable rank regularization causes uneven capacity redistribution (early layers collapse, later layers compensate), then global iso-perplexity hides local constraint violations, and the "unified constraint" is actually depth reallocation.

**Affected Hypotheses:** H-E1 (stable rank reducibility), H-M-integrated (global propagation)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Monitor per-layer representation rank (effective rank of activation covariance) and gradient SNR throughout training - early layers should not collapse
2. **Detection:** Compute layer variance in stable rank reduction - if variance >2× mean, capacity is redistributing not globally constrained
3. **Response:**
   - PIVOT: If redistribution detected, switch to per-layer adaptive λ (stronger regularization on layers with high rank, weaker on low-rank layers)
   - SCOPE: Document which layers are truly constrained vs. compensating, revise claims to "layerwise structural coupling" not "global constraint"
   - ABORT: If all rank reduction comes from 2-3 layers, global constraint claim fails

**Early Warning Indicators:**
- Layer variance in sr_ℓ^res reduction >2× mean
- Early layers (1-4) show >50% rank reduction while late layers (9-12) show <10%
- Gradient SNR drops significantly in early layers (indicates capacity loss)

---

**Risk R4: Measurement Noise Dominates Correlation**

**Source Assumption:** A4 - Spectral norm estimation via randomized power iteration has acceptable measurement noise (CV < 15%)

**Description:** If spectral norm estimation achieves CV >20%, then correlation tests are statistically underpowered (signal-to-noise ratio too low), and observed correlations r=0.3-0.5 could be noise-dominated artifacts rather than real structural coupling.

**Affected Hypotheses:** H-E1 (measurement infrastructure), H-M-integrated (correlation claims)

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Upfront validation on 50M toy model during Weeks 1-4 - measure spectral norm CV with 10 probe vectors, 5 iterations. Only proceed to Phase 1 if CV <15%
2. **Detection:** Continuous monitoring of CV throughout Phase 1 training - flag runs where CV >15%
3. **Response:**
   - PIVOT: If CV >15% on 50M model, increase probe vectors (10→20) or iterations (5→10) until CV <15%
   - SCOPE: If CV remains >15%, use proxy metrics (gradient norm statistics, SVD-based rank) that have lower measurement noise
   - ABORT: If all alternatives fail to achieve CV <20%, measurement infrastructure is unreliable - abandon spectral norm approach, use full SVD (expensive but accurate)

**Early Warning Indicators:**
- Upfront validation on 50M model shows CV >15%
- Phase 1 training runs show CV drift upward over time (indicates numerical instability)
- Correlation strength varies dramatically across random seeds (indicates noise sensitivity)

---

**Risk R5: Confound-Driven Correlation (Spurious Causality)**

**Source Assumption:** A5 - Correlation between stable rank and efficiency metrics reflects structural coupling, not confounds (corpus entropy, model width, optimizer bias)

**Description:** High mutual information between stable rank and efficiency could result from shared response to third variables (optimizer implicit bias pushing toward low-rank solutions, corpus entropy forcing compression) rather than direct mechanistic propagation. Correlation exists but causality is reversed or indirect.

**Affected Hypotheses:** H-M-integrated (mechanistic coupling claim)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Design mediation analysis upfront - use structural equation modeling with stable rank as mediator, confounds (corpus entropy, model width, optimizer hyperparameters) as covariates, efficiency metrics as outcomes
2. **Detection:** Mediation analysis result: if stable rank explains <30% of efficiency variance after controlling for confounds, correlation is spurious
3. **Response:**
   - PIVOT: If mediation <30%, shift research focus to optimizer implicit bias and training dynamics (why do both stable rank and efficiency emerge together?)
   - SCOPE: Revise claims from "stable rank causes efficiency" to "stable rank correlates with efficiency via shared optimizer dynamics"
   - ABORT: If mediation shows negative or near-zero direct effect, stable rank is outcome variable not driver - mechanistic coupling hypothesis refuted

**Early Warning Indicators:**
- Mediation analysis shows stable rank explains <30% variance beyond confounds
- Corpus entropy or model width has stronger direct effect on efficiency than stable rank
- Temporal ordering (Granger causality) shows efficiency changes precede stable rank changes (reversed causality)

---

### 3.1 Risk-Hypothesis Mapping

| Risk ID | Risk | Source | Affected Hypotheses | Severity |
|---------|------|--------|---------------------|----------|
| R1 | Linearization Breakdown | A1 | H-M-integrated | High |
| R2 | Fisher Approximation Invalidity | A2 | H-M-integrated | High |
| R3 | Capacity Redistribution | A3 | H-E1, H-M-integrated | Medium |
| R4 | Measurement Noise Dominates | A4 | H-E1, H-M-integrated | **Critical** |
| R5 | Confound-Driven Correlation | A5 | H-M-integrated | High |

**Risk Distribution:**
- Critical: 1 (R4)
- High: 3 (R1, R2, R5)
- Medium: 1 (R3)
- Low: 0

---

### 3.2 Mitigation Strategies Summary

| Risk | Prevention | Detection | Response |
|------|-----------|-----------|----------|
| R1 | Noise-transport experiment | Covariance rank divergence >30% | PIVOT to nonlinear models |
| R2 | Entropy-controlled Fisher measurement | Correlation r <0.3 under control | PIVOT to gradient flow metrics |
| R3 | Monitor per-layer rank + gradient SNR | Layer variance >2× mean | Adaptive per-layer λ |
| R4 | Upfront validation on 50M (CV <15%) | CV >15% in Phase 1 | Increase probes or use SVD |
| R5 | Mediation analysis design | Mediation <30% variance | PIVOT to optimizer bias study |

**Critical Path Risk:** R4 (Measurement Noise) has earliest detection gate (Weeks 1-4 upfront validation). If R4 fails, entire Phase 1 is blocked.

---

### 3.3 Risk Summary

| Risk | Severity | Mitigation | Owner Hypothesis |
|------|----------|------------|------------------|
| R4: Measurement Noise | **Critical** | Upfront 50M validation, CV <15% gate | H-E1, H-M-integrated |
| R1: Linearization Breakdown | High | Noise-transport experiment | H-M-integrated |
| R2: Fisher Approximation Fails | High | Entropy-controlled Fisher test | H-M-integrated |
| R5: Spurious Causality | High | Mediation analysis (≥50% variance) | H-M-integrated |
| R3: Capacity Redistribution | Medium | Layerwise sensitivity audit | H-E1, H-M-integrated |

**Total Risks:** 5 (1 Critical, 3 High, 1 Medium)

---

## 4. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 2 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1: Stable Rank Reducibility
         │ (MUST_WORK gate)
         │ Prerequisites: None
         │ Test: Validate sr_ℓ^res is measurable, controllable, reducible
         │
         ▼
[Level 1 - Mechanism]
    H-M-integrated: Mechanistic Propagation Chain
         │ (SHOULD_WORK gate)
         │ Prerequisites: H-E1 validated
         │ Test: Correlation r≥0.5, mediation ≥50%, entropy-controlled Fisher
         │
         ▼
[Terminal]
    Phase 5: Baseline Comparison (deferred)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M-integrated → Phase 5
Total Depth: 2 levels
Parallelization: None (sequential execution required)
═══════════════════════════════════════════════════════════
```

**Verification Phases:**

**Phase 1 - Foundation (Week 1-4 + Phase 1 training)**
- **H-E1**: Validate stable rank reducibility
  - Upfront validation (Weeks 1-4): Measurement infrastructure on 50M model (CV <15% gate)
  - Phase 1 training (Months 1-3): 125M models on C4, 3 variants × 3 seeds
  - **Gate 1 (MUST_WORK)**: If sr_ℓ^res reduction <20% OR perplexity >1% OR CV >20% → STOP
  - If fail: Stable rank metric not controllable → pivot to alternative structural metrics

**Phase 2 - Mechanistic Validation (Phase 2 training)**
- **H-M-integrated**: Test mechanistic propagation
  - Post-training measurements: LoRA rank, KV rank, attention entropy
  - Correlation analysis: Pearson r across layers and seeds (36 data points per metric)
  - Mechanistic validation: entropy-controlled Fisher, noise-transport, mediation analysis
  - **Gate 2 (SHOULD_WORK)**: If r <0.3 for any two metrics → efficiency dimensions orthogonal
  - If fail: Valuable negative result → document independence, proceed to Phase 5 for practical comparison

**Phase 3 - Baseline Comparison (Deferred to Phase 5)**
- Compare unified objective vs. independent optimization stack at equal compute
- Pareto dominance testing in 2D fronts (LoRA-KV, LoRA-attention, KV-attention)
- **Gate 3 (DETERMINES_SUCCESS)**: Pareto dominance in ≥2 fronts + ≥10% hypervolume improvement

---

### 4.1 Dependency Hierarchy

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Type | Prerequisites | Gate Type | If Fail Action |
|-------|-----------|------|---------------|-----------|----------------|
| 0 | H-E1 | Existence | None | MUST_WORK | STOP - pivot to alternative metrics |
| 1 | H-M-integrated | Mechanism | H-E1 | SHOULD_WORK | CONTINUE - negative result valuable |

Critical Path Length: 2
Sequential Execution Required: Yes (H-M-integrated depends on H-E1 validated models)
Parallelization Opportunities: None (dependencies are strict)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Gate Conditions Summary:**

| Gate | Hypothesis | Type | Pass Condition | Fail Consequence |
|------|-----------|------|----------------|------------------|
| Gate 1 | H-E1 | MUST_WORK | sr_ℓ^res reduction ≥20% AND perplexity ≤1% deviation AND CV <15% | STOP entire pipeline - stable rank not controllable |
| Gate 2 | H-M-integrated | SHOULD_WORK | Pearson r ≥0.5 for all metrics AND mediation ≥50% | CONTINUE - orthogonality is valuable negative result, Phase 5 still tests practical utility |

**Dependency Rationale:**

1. **H-E1 Foundation**: Must validate measurement infrastructure and controllability before testing mechanistic claims
   - If H-E1 fails, no point testing correlations since the independent variable itself is unmeasurable/uncontrollable
   - CV <15% gate is critical path risk (R4) - blocks entire Phase 1

2. **H-M-integrated Sequential**: Requires H-E1 validated models as input
   - Uses trained models from H-E1 for post-training efficiency measurements
   - Cannot parallelize - must wait for H-E1 training to complete
   - SHOULD_WORK gate allows pipeline continuation even if correlations fail (negative result valuable)

---

## 5. Timeline & Execution Plan

### 5.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 2 Hypotheses (Phase 1-2 Execution)
═══════════════════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ Weeks 1-4  │ Month 1    │ Month 2    │ Month 3    │ Phase 2    │
                      │ Validation │            │            │            │ (Cond.)    │
──────────────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
PHASE 1: Foundation
  Upfront Validation  │ ████████   │            │            │            │            │
  (50M model, CV<15%) │            │            │            │            │            │
  [Gate 0]            │         ◆  │            │            │            │            │
                      │            │            │            │            │            │
  H-E1 Training       │            │ ██████████ │ ██████████ │ ██████████ │            │
  (125M × 3 variants) │            │            │            │            │            │
  [Gate 1]            │            │            │            │            │ ◆          │
──────────────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
PHASE 2: Mechanistic Validation (Conditional on Gate 1 PASS)
  H-M-integrated      │            │            │            │            │ ██████████ │
  Post-training tests │            │            │            │            │ (2 months) │
  [Gate 2]            │            │            │            │            │         ◆  │
──────────────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
═══════════════════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point

Total Duration: 3-5 months
  - Upfront validation: 4 weeks (Gate 0: CV <15%)
  - Phase 1 (H-E1): 3 months training (Gate 1: sr_ℓ^res reduction ≥20%)
  - Phase 2 (H-M-integrated): 2 months post-training analysis (Gate 2: r ≥0.5, conditional)

Critical Path: Upfront Validation → H-E1 Training → H-M-integrated Analysis
═══════════════════════════════════════════════════════════════════════════════════════════
```

**Timeline Notes:**
- **Weeks 1-4 (Upfront Validation)**: Measurement infrastructure validation on 50M toy model
  - **Gate 0 (CRITICAL)**: CV <15% for spectral norm estimation - if fail, ABORT Phase 1
- **Months 1-3 (Phase 1 Training)**: 9 training runs (3 variants × 3 seeds) on 125M models
  - **Gate 1 (MUST_WORK)**: sr_ℓ^res reduction ≥20% AND perplexity ≤1% - if fail, STOP pipeline
- **Phase 2 (Conditional, 2 months)**: Post-training measurements and mechanistic validation
  - Only executed if Gate 1 passes
  - **Gate 2 (SHOULD_WORK)**: r ≥0.5 correlations - if fail, negative result is valuable

---

### 5.2 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: Gate 0 → H-E1 → Gate 1 → H-M-integrated → Gate 2

Total Duration: 3-5 months
  - Minimum (if Gate 1 fails): 3.5 months (validation + training only)
  - Maximum (if all pass): 5.5 months (validation + training + mechanistic tests)

Duration Breakdown:
  1. Upfront Validation: 4 weeks (0.9 months)
  2. H-E1 Training: 3 months (9 runs on single 8-GPU node)
  3. H-M-integrated Analysis: 2 months (post-training measurements, correlation tests)

Slack Available: 0 weeks (all sequential, no parallelization)

Bottleneck Analysis:
  - **Critical bottleneck**: H-E1 training (3 months) - cannot be shortened without reducing:
    * Training corpus size (10B tokens minimum for stable perplexity)
    * Number of seeds (3 minimum for statistical power)
    * Model count (3 variants required for comparison)
  - **Early failure opportunity**: Gate 0 (Week 4) - if CV >15%, saves 3+ months by aborting early
  - **Decision point**: Gate 1 (Month 3 end) - determines whether to invest 2 more months in Phase 2

Acceleration Options:
  - Parallelization: NOT POSSIBLE (H-M-integrated requires H-E1 trained models)
  - Resource scaling: Could use 2-3 GPU nodes to reduce H-E1 from 3 months to 6-8 weeks
  - Scope reduction: Could test at 50M scale only (faster training) but sacrifices validity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5.3 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 2
  - H-E1 (Existence): Stable rank reducibility validation
  - H-M-integrated (Mechanism): Mechanistic propagation chain (3 causal steps integrated)

Verification Phases: 2
  1. Phase 1 - Foundation (H-E1): 3 months training
  2. Phase 2 - Mechanistic Validation (H-M-integrated): 2 months analysis (conditional)

Total Duration: 3.5-5.5 months
  - Minimum path (Gate 1 fail): 3.5 months
  - Maximum path (all gates pass): 5.5 months

Critical Path Length: 5.5 months (if all hypotheses validated)

Execution Mode: Sequential chain (no parallelization)

Compute Resources:
  - Upfront validation: 1 GPU, 4 weeks (50M model)
  - Phase 1 training: Single 8-GPU node, 3 months (125M models × 9 runs)
  - Phase 2 analysis: 1-2 GPUs, 2 months (post-training measurements)
  - Total GPU-months: ~24-30 GPU-months (single node utilization)

Storage Requirements:
  - Model checkpoints: ~50GB (9 runs × 5-6GB each)
  - KV cache samples: ~100GB (validation set activations for covariance analysis)
  - Logs and metrics: ~10GB (per-step sr_ℓ^res measurements, training curves)
  - Total: ~160GB

Personnel:
  - 1 researcher (full-time)
  - Measurement infrastructure development: Weeks 1-4 (critical path)
  - Training supervision: Months 1-3 (monitoring, adaptive λ tuning)
  - Analysis: Phase 2 (2 months, post-training measurements and statistical tests)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5.4 Execution Order

**Step 1**: Upfront Validation (Weeks 1-4)
- Train 50M toy model with sr_ℓ^res measurement infrastructure
- Validate spectral norm estimation: CV <15% with 10 probe vectors, 5 iterations
- Test layerwise sensitivity metrics (representation rank, gradient SNR)
- **Gate 0 Decision**: If CV >15%, increase probes/iterations or ABORT

**Step 2**: H-E1 Foundation Training (Months 1-3)
- Pretrain 9 models: 3 variants (baseline, explicit sr_ℓ^res, implicit control) × 3 seeds
- Dataset: C4, 10B tokens per run
- Model: 125M GPT-2 (d=768, 12 layers)
- Measurements: Per-layer sr_ℓ^res every 1000 steps via Hutchinson trace + power iteration
- Adaptive λ tuning: PID control to maintain iso-perplexity (≤1% deviation)
- **Gate 1 Decision**: If sr_ℓ^res reduction ≥20% AND perplexity ≤1% AND layer variance <2× mean → PASS, proceed to Phase 2. If fail → STOP pipeline.

**Step 3**: H-M-integrated Mechanistic Validation (Phase 2, Conditional, 2 months)
- Use H-E1 validated models for post-training measurements
- Month 1: Efficiency metric collection
  * LoRA rank via random direction probes on GLUE/SQuAD
  * KV effective rank via empirical covariance SVD on validation set
  * Attention entropy averaged per layer
- Month 2: Mechanistic validation + statistical analysis
  * Correlation analysis: Pearson r across 36 data points (12 layers × 3 seeds) per metric
  * Mediation analysis: Structural equation modeling with sr_ℓ^res as mediator, confounds as covariates
  * Entropy-controlled Fisher measurement (temperature-scaled logits)
  * Noise-transport experiment (isotropic perturbation propagation)
- **Gate 2 Decision**: If r ≥0.5 for all metrics AND mediation ≥50% → mechanistic coupling validated. If r <0.3 → orthogonality confirmed (valuable negative result).

**Step 4**: Phase 5 Baseline Comparison (Deferred)
- Compare unified objective vs. independent optimization stack at equal total compute
- Pareto dominance testing in 2D efficiency fronts
- Hypervolume improvement calculation
- **Gate 3 Decision**: Determines practical success (DETERMINES_SUCCESS gate)

**Final**: Verification complete - proceed to paper writing (Phase 6)

---

## 6. Dialectical Analysis

This section applies thesis-antithesis-synthesis dialectical evaluation to ensure robust verification planning by considering opposing viewpoints and potential failure modes.

---

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS: Unified Efficiency via Jacobian Stable Rank
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Core Claim:** Under pretraining with residual-corrected Jacobian stable rank regularization, if models are trained to minimize sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2 per layer, then they will exhibit cross-level efficiency properties (low-rank adaptation, KV compressibility, sparse attention), because the layer-wise Jacobian constraint propagates through Fisher spectrum, activation covariance, and attention entropy structures.

**Supporting Evidence:**
1. **Causal Mechanism (3-step chain):**
   - Step 1: Regularization constrains Jacobian stable rank during pretraining (J_ℓ = I + J̃_ℓ residual decomposition enables tractable optimization)
   - Step 2: Constrained stable rank propagates to Fisher spectrum (F ≈ J^T J), activation covariance (Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T), and attention structure via mathematical coupling
   - Step 3: Propagation manifests as downstream efficiency: lower LoRA rank, higher KV compression, sparser attention

2. **Theoretical Foundations:**
   - Linearized analysis of transformer dynamics (NTK framework, covariance propagation)
   - Fisher information approximation F ≈ J^T J under entropy-controlled conditions
   - Residual connections provide structural decomposition J_ℓ = I + J̃_ℓ that isolates functional rank

3. **Empirical Feasibility:**
   - Hutchinson trace + randomized power iteration make sr_ℓ^res tractable (expected CV ~5-8%)
   - ARD-LoRA, KV-CAT, Mamba-2 demonstrate independent efficiency dimensions are trainable
   - Iso-perplexity control via adaptive regularization weight tuning is standard practice

**Strengths:**
- **Unified Framework**: Single structural property (Jacobian stable rank) potentially explains three efficiency dimensions, reducing N×M optimization complexity to N+M
- **Mechanistic Testability**: Clear propagation links (Jacobian → Fisher, covariance, attention) enable validation via entropy-controlled tests and noise-transport experiments
- **Practical Value**: If confirmed, enables "train once, deploy efficiently" paradigm - models naturally support adaptation, compression, and sparsity without post-processing

**Expected Outcomes:**
- **Primary (P1)**: sr_ℓ^res reduction ≥20% at iso-perplexity (≤1% deviation) with layer variance <2× mean
- **Secondary (P2)**: Pearson r ≥0.5 between sr_ℓ^res and all three efficiency metrics, mediation ≥50% variance explained beyond confounds
- **Tertiary (P3)**: Pareto dominance in ≥2 pairwise efficiency fronts with ≥10% hypervolume improvement at equal compute (Phase 5)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6.2 Antithesis Development

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS: Efficiency Dimensions Are Orthogonal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Null Hypothesis (H0):** There is no significant correlation (Pearson r < 0.3) between residual-corrected Jacobian stable rank and efficiency metrics (LoRA rank, KV compression ratio, attention entropy) across layers and random seeds at iso-perplexity.

**Counter-Arguments:**

1. **Independent Optimization Success:** ARD-LoRA, KV-CAT, and Mamba-2 achieve state-of-art efficiency by targeting each dimension independently. Their success suggests efficiency dimensions are orthogonal, not coupled - otherwise independent optimization would fail.

2. **Linearization Breakdown:** Transformer dynamics are highly nonlinear (GELU activations, attention softmax). Local linearization F ≈ J^T J and Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T may not hold globally, especially in deeper layers where nonlinearity dominates. If linearization fails, Jacobian rank cannot predict covariance/attention structure.

3. **Confound-Driven Correlation:** High mutual information between stable rank and efficiency could result from shared optimizer implicit bias (SGD naturally pushes toward low-rank solutions) or capacity pressure (both stable rank and efficiency respond to model width constraints), not direct mechanistic propagation. Correlation exists but causality is reversed or indirect.

4. **Measurement Noise Dominates:** Spectral norm estimation via randomized power iteration is noisy (CV could exceed 15-20%). If measurement variance is high, observed correlations r=0.3-0.5 may be noise-dominated artifacts rather than real structural coupling.

5. **Scope Limitations:** Hypothesis assumes transformer architectures with residual connections and layer normalization. Non-residual architectures, encoder-only models, or models >7B parameters are excluded. Even within transformers, infinite-width limit (NTK regime) may exhibit full-rank dynamics despite regularization.

**Potential Failure Points (from Risk Analysis):**
- **R1 (Linearization Breakdown)**: If noise-transport experiment shows covariance rank divergence >30% from linearized prediction → mechanistic link broken
- **R2 (Fisher Approximation Fails)**: If entropy-controlled Fisher correlation r <0.3 → F ≈ J^T J assumption violated
- **R4 (Measurement Noise)**: If CV >20% in upfront validation → correlation tests statistically underpowered
- **R5 (Spurious Causality)**: If mediation analysis shows sr_ℓ^res explains <30% variance after controlling for confounds → correlation not causal

**Conditions Under Which H0 Would Be Supported:**
- **Pearson r < 0.3** for any two efficiency metrics across layers and seeds → efficiency dimensions are independent
- **Mediation < 30%** variance explained by sr_ℓ^res after controlling for corpus entropy, model width, optimizer bias → correlation is confound-driven
- **Entropy-controlled Fisher r < 0.3** → linearization assumption F ≈ J^T J fails, breaking mechanistic link
- **Layer-wise correlation collapse** in deeper layers → nonlinearity destroys propagation, coupling is limited to early layers only

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS: Testable Mechanistic Hypothesis with Valuable Negative Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Balanced Assessment:**

The hypothesis H-JacobianStableRank-v1 presents a testable claim that efficiency dimensions (parameter, memory, computation) are correlated manifestations of a single structural property (Jacobian stable rank) that propagates via linearized dynamics. However, the null hypothesis raises valid concerns that: (1) efficiency dimensions may be fundamentally orthogonal as evidenced by independent optimization success, (2) linearization assumptions may not hold globally in highly nonlinear transformers, and (3) observed correlations may be confound-driven rather than causally mechanistic.

**Resolution Path:**

The verification plan resolves this dialectic through a **three-stage empirical test** with **mechanistic validation gates**:

1. **Foundation Verification (H-E1, Gate 1 MUST_WORK):** 
   - Establishes that stable rank is measurable (CV <15%), controllable (reducible by ≥20%), and does not degrade quality (iso-perplexity ≤1%)
   - **If H-E1 fails:** Thesis immediately refuted - stable rank metric itself is unreliable, no point testing correlations
   - **If H-E1 passes:** Measurement infrastructure validated, proceed to mechanistic tests

2. **Mechanistic Validation (H-M-integrated, Gate 2 SHOULD_WORK):**
   - Tests correlation hypothesis: r ≥0.5 between sr_ℓ^res and all three efficiency metrics
   - **Critical mechanistic gates:**
     * Entropy-controlled Fisher test: validates F ≈ J^T J assumption under controlled conditions
     * Noise-transport experiment: validates Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T covariance propagation
     * Mediation analysis: tests whether sr_ℓ^res causally explains ≥50% efficiency variance beyond confounds
   - **If mechanistic gates pass:** Thesis supported - structural coupling confirmed via linearized propagation
   - **If correlation exists but mechanistic gates fail:** Antithesis partially supported - correlation is confound-driven (optimizer bias), pivot to training dynamics research
   - **If no correlation (r <0.3):** Antithesis fully supported - efficiency dimensions are orthogonal (valuable negative result)

3. **Practical Utility Test (Phase 5, Gate 3 DETERMINES_SUCCESS):**
   - Even if mechanistic coupling fails, unified objective may still have practical benefits
   - Tests Pareto dominance: does single regularization achieve multi-dimensional efficiency better than independent optimization?
   - **If Pareto dominance:** Practical success regardless of mechanistic understanding
   - **If no dominance:** Both thesis and practical utility refuted

**Conditions for Thesis Support:**
- **Full Support:** H-E1 passes AND H-M-integrated passes (r ≥0.5, mediation ≥50%, mechanistic gates pass) → unified efficiency framework validated
- **Partial Support (Practical):** H-E1 passes, H-M-integrated fails, but Phase 5 shows Pareto dominance → practical utility without mechanistic understanding
- **Partial Support (Empirical):** H-E1 passes, correlation exists (r ≥0.5) but mediation fails → empirical coupling confirmed, mechanism unclear

**Conditions for Antithesis Support:**
- **Full Support (Orthogonality):** H-M-integrated shows r <0.3 for any two metrics → efficiency dimensions are independent (ARD-LoRA, KV-CAT, Mamba correctly treat them as separate)
- **Partial Support (Confound):** Correlation exists but mediation <30% → sr_ℓ^res is outcome variable not driver, optimizer bias is true mechanism
- **Partial Support (Measurement Failure):** H-E1 fails at Gate 0 (CV >20%) or Gate 1 (sr_ℓ^res reduction <20%) → metric unreliable, cannot test thesis

**Nuanced Outcome Possibilities:**

1. **Scenario A - Full Thesis Validation:**
   - H-E1 passes (sr_ℓ^res reducible at iso-perplexity)
   - H-M-integrated passes (r ≥0.5, mediation ≥50%, mechanistic gates pass)
   - Phase 5 shows Pareto dominance
   - **Outcome:** Unified efficiency framework confirmed - paradigm shift to pretraining-time emergence

2. **Scenario B - Valuable Negative Result (Orthogonality):**
   - H-E1 passes (measurement validated)
   - H-M-integrated fails (r <0.3)
   - **Outcome:** Efficiency dimensions are fundamentally independent - justifies current separate-optimization practices, redirects future research

3. **Scenario C - Empirical Success, Mechanistic Failure:**
   - H-E1 passes, correlation exists (r ≥0.5)
   - Mediation fails (<30%) or entropy-controlled Fisher fails (r <0.3)
   - **Outcome:** Correlation is real but mechanism is wrong - pivot to optimizer implicit bias research

4. **Scenario D - Practical Utility Without Theory:**
   - H-M-integrated fails (no correlation or mediation fails)
   - Phase 5 shows Pareto dominance anyway
   - **Outcome:** Unified objective works in practice for unknown reasons - useful but not theoretically understood

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution Strategy |
|--------|-----------------|----------------------|---------------------|
| **Measurability** | sr_ℓ^res computable via Hutchinson + power iteration (CV ~5-8%) | CV may exceed 20%, making correlations noise-dominated | Upfront validation on 50M model (Gate 0), abort if CV >15% |
| **Controllability** | sr_ℓ^res reducible by ≥20% via gradient-based regularization | Over-constraint may degrade perplexity >1% or cause capacity redistribution | Adaptive λ tuning for iso-perplexity, layerwise sensitivity audit (variance <2× mean) |
| **Mechanistic Link** | Jacobian constraint propagates via F ≈ J^T J, Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T | Linearization breaks in nonlinear transformers (GELU, softmax) | Entropy-controlled Fisher test, noise-transport experiment to validate propagation empirically |
| **Causality** | sr_ℓ^res causally drives efficiency via structural coupling | Correlation may be confound-driven (optimizer bias, capacity pressure) | Mediation analysis (≥50% variance explained), temporal ordering (Granger causality), intervention experiments |
| **Generalization** | Unified framework applies broadly to transformer pretraining | Limited to residual architectures, 125M-1B scale, autoregressive decoders | Explicit scope boundaries, scaling validation (125M→350M→1B), domain robustness (C4 vs The Stack) |
| **Practical Utility** | Single objective achieves multi-dimensional efficiency (N+M complexity) | Independent optimization may be fundamentally necessary (N×M unavoidable) | Phase 5 Pareto dominance testing - if unified fails, confirms orthogonality thesis |

**Overall Robustness Score:** Medium-High

**Justification:**
- **High Robustness (Testability):** Clear falsification criteria at each gate - hypothesis is rigorously testable with quantitative thresholds (CV <15%, r ≥0.5, mediation ≥50%)
- **Medium Robustness (Mechanistic Claims):** Linearization assumptions (F ≈ J^T J) are strong and may not hold globally, but can be empirically validated via entropy-controlled tests and noise-transport experiments
- **High Robustness (Value Preservation):** Negative results are scientifically valuable - proving orthogonality justifies current practices and redirects research, making the hypothesis non-risky from a research investment perspective

**Confidence in Verification Plan:** 0.75 (from Phase 2A)

**Factors Supporting Confidence:**
- Measurement infrastructure validated upfront (Gate 0) before expensive training
- Sequential gating allows early failure detection (H-E1 fail → stop, saves 2+ months)
- Mechanistic validation gates separate correlation from causation (mediation analysis, entropy-controlled tests)
- Multiple outcome scenarios preserve research value (Scenarios A-D all contribute to understanding)

**Factors Reducing Confidence:**
- Strong linearization assumptions may not hold in highly nonlinear transformers
- Confound control relies on mediation analysis - if confounds are unknown, analysis may miss them
- Scope limited to 125M-1B scale, transformer-only, autoregressive-only - generalization uncertain
- Phase 2 conditional on Phase 1 success - if H-E1 fails, no mechanistic validation possible

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Pretraining with residual-corrected Jacobian stable rank regularization produces foundation models with mechanistically-linked efficiency properties across adaptation (low-rank fine-tuning), memory (KV compression), and computation (sparse attention).

- **Hypothesis ID:** H-JacobianStableRank-v1
- **Confidence:** 0.75

**Verification Structure:**
- **Mode:** Incremental (Phase 2A-driven, 20% scope reduction via Established Facts)
- **Sub-Hypotheses:** 2 total
  - H-E1: Stable rank reducibility (Existence)
  - H-M-integrated: Mechanistic propagation chain (3 causal steps integrated)
- **Duration:** 3.5-5.5 months (Phase 1: 3 months, Phase 2: 2 months conditional)
- **Critical Gates:** 3 decision points (Gate 0: CV <15%, Gate 1: MUST_WORK, Gate 2: SHOULD_WORK)

**Risk Assessment:** 1 Critical, 3 High, 1 Medium
- **Primary concerns:** Measurement noise (R4, critical path blocker), linearization breakdown (R1), spurious causality (R5)
- **Mitigation:** Upfront validation on 50M model (Gate 0), entropy-controlled tests, mediation analysis

**Dialectical Evaluation:** Thesis (unified efficiency) vs. Antithesis (orthogonality) resolved via mechanistic validation gates. Negative results are scientifically valuable.

**Immediate Action:** Begin upfront validation (Weeks 1-4) on 50M model to test measurement infrastructure before Phase 1 commitment.

---

### 7.2 Verification Execution Order

**Phase 1: Foundation (4 weeks upfront + 3 months training)**

1. **Upfront Validation (Weeks 1-4):**
   - Train 50M toy model with sr_ℓ^res measurement infrastructure
   - Validate spectral norm estimation: CV <15% with 10 probe vectors, 5 iterations
   - **Gate 0 (Critical Blocker):** If CV >15% → increase probes/iterations or ABORT Phase 1

2. **H-E1 Training (Months 1-3):**
   - 9 training runs: 3 variants (baseline, explicit sr_ℓ^res, implicit control) × 3 seeds
   - Model: 125M GPT-2 on C4 (10B tokens)
   - Adaptive λ tuning for iso-perplexity (≤1% deviation)
   - **Gate 1 (MUST_WORK):** If sr_ℓ^res reduction ≥20% AND perplexity ≤1% AND layer variance <2× mean → PASS, proceed to Phase 2. If fail → STOP pipeline.

**Phase 2: Mechanistic Validation (2 months, conditional on Gate 1 PASS)**

3. **H-M-integrated Analysis:**
   - Month 1: Post-training efficiency measurements (LoRA rank, KV rank, attention entropy)
   - Month 2: Mechanistic validation (entropy-controlled Fisher, noise-transport, mediation analysis)
   - **Gate 2 (SHOULD_WORK):** If r ≥0.5 for all metrics AND mediation ≥50% → mechanistic coupling validated. If r <0.3 → orthogonality confirmed (valuable negative result).

**Phase 5: Baseline Comparison (Deferred)**
- Compare unified objective vs. independent optimization stack at equal compute
- Pareto dominance testing in 2D efficiency fronts
- **Gate 3 (DETERMINES_SUCCESS):** Practical utility test

---

### 7.3 Critical Decision Points

**Gate 0: Measurement Infrastructure Validation (Week 4)**
- **Condition:** Spectral norm estimation CV <15% on 50M model
- **If FAIL:** Increase probe vectors (10→20) or iterations (5→10), or use SVD-based rank (expensive but accurate)
- **If ABORT:** Measurement unreliable → pipeline blocked, pivot to alternative structural metrics

**Gate 1: Foundation Validation (Month 3 end)**
- **Condition:** H-E1 passes (sr_ℓ^res reduction ≥20%, perplexity ≤1%, layer variance <2× mean)
- **If PASS:** Proceed to Phase 2 mechanistic validation (invest 2 more months)
- **If FAIL:** STOP pipeline → stable rank metric not controllable, pivot to alternative efficiency frameworks

**Gate 2: Mechanistic Validation (Phase 2 end)**
- **Condition:** Pearson r ≥0.5 for all metrics AND mediation ≥50% AND entropy-controlled Fisher r ≥0.5
- **If PASS:** Mechanistic coupling validated → unified efficiency framework confirmed
- **If FAIL (r <0.3):** Orthogonality confirmed → valuable negative result, justifies current separate-optimization practices
- **If PARTIAL (correlation exists but mediation fails):** Empirical coupling without mechanistic understanding → pivot to optimizer bias research

---

### 7.4 Open Questions

From Phase 2A Section 5:

1. **Scaling Behavior:** Does correlation strengthen with model width (125M → 350M → 1B) or plateau/degrade? Width-normalized metrics (nsr_ℓ = sr_ℓ^res / d) may reveal scaling asymptotics.

2. **Domain Robustness:** Do high-entropy domains (code, multilingual) weaken correlations or preserve them at different absolute rank levels? The Stack robustness tests will address this.

3. **Morphable Architecture:** Can attention↔SSM gating learn efficiency structure dynamically, or is fixed allocation sufficient? Deferred to Phase 3 due to implementation complexity (custom CUDA kernels required).

4. **Measurement Reliability at Scale:** Is spectral norm estimation reliable at 1B+ scale, or does noise dominate? Scaling validation (125M→350M→1B) will test this.

---

### 7.5 Recommendations

**Immediate Actions (Week 1):**
1. Set up 50M toy model training environment (single GPU, HuggingFace Transformers)
2. Implement Hutchinson trace + randomized power iteration for sr_ℓ^res measurement
3. Begin upfront validation with CV monitoring

**Resource Allocation:**
- **Compute:** Single 8-GPU node for 3-5 months (Phase 1-2)
- **Storage:** ~160GB (model checkpoints, KV cache samples, logs)
- **Personnel:** 1 researcher full-time (measurement infrastructure critical weeks 1-4)

**Risk Mitigation Priorities:**
1. **R4 (Critical):** Upfront validation Week 4 decision point - DO NOT proceed to Phase 1 if CV >15%
2. **R1 (High):** Design noise-transport experiment during Phase 1 training, execute in Phase 2
3. **R5 (High):** Plan mediation analysis methodology before Phase 2 (identify confounds: corpus entropy, model width, optimizer hyperparameters)

**Success Criteria Summary:**
- **Minimum Success:** H-E1 validates measurement infrastructure (Gate 1 pass) - enables future stable rank research
- **Moderate Success:** H-M-integrated shows correlation (r ≥0.5) - empirical coupling confirmed
- **Full Success:** Mechanistic validation passes (mediation ≥50%, entropy-controlled Fisher r ≥0.5) - unified efficiency framework validated

**Alternative Research Paths (if gates fail):**
- **Gate 0 fail:** Pivot to SVD-based rank metrics or gradient flow analysis (less noisy alternatives)
- **Gate 1 fail:** Pivot to alternative structural metrics (effective rank, gradient norm ratios)
- **Gate 2 fail (orthogonality):** Document independence, redirect to improving individual efficiency techniques (valuable contribution)

---

### 7.6 Appendices

**A. Notation Reference**

| Symbol | Definition |
|--------|------------|
| sr_ℓ^res | Residual-corrected Jacobian stable rank = \|\|J̃_ℓ\|\|_F^2 / \|\|J̃_ℓ\|\|_2^2 |
| J_ℓ | Layer-wise Jacobian (J_ℓ = I + J̃_ℓ due to residual connections) |
| F | Fisher information matrix (F ≈ J^T J under linearization) |
| Σ_ℓ | Activation covariance at layer ℓ (Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T) |
| CV | Coefficient of variation (measurement noise metric) |

**B. Hypothesis Type Legend**

- **H-E (Existence):** Validates that the phenomenon exists and is measurable
- **H-M (Mechanism):** Tests causal chain steps that explain how/why the phenomenon works
- **H-C (Condition):** Tests boundary conditions where the mechanism applies (optional, not included in this plan)
- **H-CP (Comparison):** Compares against baselines to establish practical superiority (deferred to Phase 5)

**C. Gate Type Legend**

- **MUST_WORK:** Failure stops the pipeline - hypothesis is invalid without this foundation
- **SHOULD_WORK:** Failure narrows scope but allows continuation - partial validation possible
- **DETERMINES_SUCCESS:** Failure means no practical utility, but scientific contribution may remain

**D. Related Work Context**

From Phase 2A Section 4:

- **ARD-LoRA (Shinwari et al. 2025):** 99.3% of full fine-tuning performance with 0.32% trainable parameters via gradient-based importance scoring
- **KV-CAT (Gelberg et al. 2026):** Training transformers for KV cache compressibility via pretraining-time objectives
- **Mamba-2 (Dao & Gu 2024):** 2-8× speedup over transformers via sub-quadratic state-space architectures (1422 citations)

These works demonstrate that individual efficiency dimensions are trainable. Our hypothesis tests whether they are correlated manifestations of a single structural property or orthogonal dimensions requiring separate optimization.

---

*Generated by YouRA Phase 2B Planning | 2026-05-12*
