# Phase 2A Research Hypothesis: Unified Efficiency via Jacobian Stable Rank

**Session:** 2026-05-12T00:57:00Z  
**Gap ID:** Gap 1 - Unified Training Framework for Joint Optimization  
**Workflow:** phase2a-dialogue v9.0.0 (Self-Contained Tikitaka Loop)  
**Exchanges:** 15 (converged to consensus)

---

## Executive Summary

Through 15 exchanges of rigorous multi-perspective critique, we converged on a testable hypothesis: **Regularizing the residual-corrected stable rank of layer-wise Jacobians during pretraining produces foundation models with mechanistically-linked efficiency properties across parameter adaptation (LoRA), memory (KV cache), and computation (sparse attention).**

The hypothesis evolved from an initial fuzzy "unified sparsity" metaphor (Exchange 1) to a concrete mathematical framework with precise measurements, falsification criteria, and a three-phase experimental roadmap. Key breakthrough: Dr. Ally (Exchange 6) introduced **Jacobian stable rank** as the mechanistic bridge linking all three efficiency dimensions. Critical refinement: Prof. Vera (Exchange 12) formalized the **residual-corrected metric** to remove identity-term confounds from residual connections.

**Verdict:** 5 STRONG, 1 MODERATE consensus across all 6 personas.

---

## Core Hypothesis

### Statement

> Under pretraining with residual-corrected Jacobian stable rank regularization, if models are trained to minimize sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2 per layer, then they will exhibit cross-level efficiency properties (low-rank adaptation, KV compressibility, sparse attention), because the layer-wise Jacobian constraint propagates through Fisher spectrum, activation covariance, and attention entropy structures.

### Mathematical Formulation

For a pre-norm transformer block: h_{ℓ+1} = h_ℓ + F_ℓ(LN(h_ℓ))

The total Jacobian is: J_ℓ = I + J̃_ℓ, where J̃_ℓ := ∂F_ℓ(LN(h_ℓ))/∂h_ℓ

The **residual-corrected stable rank** is:

```
sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2
```

where:
- ||J̃_ℓ||_F^2 estimated via Hutchinson trace estimation
- ||J̃_ℓ||_2^2 estimated via randomized power iteration (10 probe vectors, 5 iterations)

### Null Hypothesis (H0)

There is **no significant correlation** (Pearson r < 0.3) between residual-corrected Jacobian stable rank and efficiency metrics (intrinsic LoRA rank, KV covariance effective rank, attention entropy) across layers and random seeds at iso-perplexity.

---

## Three Testable Predictions

### P1: Structural Constraint Validity

**Statement:** Pretraining with explicit sr_ℓ^res regularization reduces mean residual-corrected stable rank by ≥20% relative to baseline while maintaining iso-perplexity (≤1% deviation).

**Test Method:**
- Pretrain 3 model variants: (A) baseline, (B) explicit regularization, (C) implicit control
- 3 random seeds each, 125M parameters, 10B tokens from C4
- Measure sr_ℓ^res every N steps during training

**Success Criteria:**
- Mean sr_ℓ^res reduction ≥20% across layers
- Perplexity deviation ≤1% vs. baseline
- Layer variance in rank reduction < 2× mean (no compensatory redistribution)

**Falsification:** If reduction < 20%, OR perplexity > 1%, OR layer variance > 2× mean → P1 fails.

---

### P2: Cross-Metric Correlation

**Statement:** Pearson r ≥ 0.5 between sr_ℓ^res and each efficiency metric across layers and seeds, after controlling for confounds.

**Test Method:**
1. Post-training measurements:
   - Intrinsic LoRA rank via random direction probes (95% downstream accuracy threshold)
   - KV covariance effective rank via SVD (90% variance threshold)
   - Attention entropy: -Σ p_ij log p_ij per layer
2. Compute Pearson correlations across layers and 9 training runs
3. Mediation analysis controlling for corpus entropy and model width
4. Entropy-controlled Fisher test: measure Fisher rank directly under temperature-scaled logits

**Success Criteria:**
- Pearson r ≥ 0.5 for all three metric pairs (sr_ℓ^res vs. LoRA, KV, attention)
- Mediation analysis: sr_ℓ^res explains ≥50% of variance beyond confounds
- Entropy-controlled Fisher correlation r ≥ 0.5 (validates mechanism)

**Falsification:** If r < 0.3 for any two metrics, OR mediation < 30%, OR entropy-controlled Fisher r < 0.3 → P2 fails.

---

### P3: Efficiency Gains (Pareto Dominance)

**Statement:** Regularized models achieve Pareto dominance in ≥2 pairwise efficiency comparisons at iso-perplexity, with ≥10% hypervolume improvement in 3D efficiency space.

**Test Method:**
1. Plot 2D Pareto fronts:
   - x: LoRA rank, y: KV compression ratio
   - x: LoRA rank, y: Attention sparsity
   - x: KV compression ratio, y: Attention sparsity
2. Test strict dominance: regularized model achieves (lower x AND better y) vs. baseline
3. Compute hypervolume indicator in 3D (LoRA, KV, attention) space

**Success Criteria:**
- Pareto dominance in ≥2 of 3 pairwise fronts
- Hypervolume improvement ≥10%
- At equal perplexity and equal total training compute

**Falsification:** If dominance in < 2 fronts, OR hypervolume < 10%, OR requires > 30% additional compute → P3 fails.

---

## Mechanistic Chain

### Step 1: Jacobian Constraint

**Description:** Residual-corrected stable rank regularization during pretraining constrains effective rank of layer-wise representation transformations (J_ℓ = I + J̃_ℓ).

**Evidence:** Hutchinson trace + randomized power iteration make sr_ℓ^res tractable for gradient-based optimization (~15% training overhead).

**Falsifier:** If sr_ℓ^res cannot be reduced ≥20% without perplexity degradation, OR reduction is due to residual magnitude shrinking (not functional rank), mechanism fails.

### Step 2: Propagation to Efficiency Dimensions

**Description:** Constrained Jacobian stable rank propagates to Fisher spectrum (adaptation), activation covariance (KV), and attention structure via mathematical coupling.

**Evidence:**
- Fisher ≈ J^T J (under local linearization)
- Σ_ℓ ≈ J_ℓ Σ_{ℓ-1} J_ℓ^T (covariance propagation)
- Attention entropy bounded by interaction degrees of freedom

**Falsifier:** If Pearson r < 0.3 between sr_ℓ^res and any two efficiency metrics, OR entropy-controlled Fisher test shows correlation collapse, propagation link is invalid.

### Step 3: Downstream Performance Gains

**Description:** Cross-level efficiency manifests as: lower LoRA rank for fine-tuning, higher KV compression at iso-accuracy, sparser attention patterns.

**Evidence:** Pareto dominance in ≥2 pairwise comparisons demonstrates practical utility.

**Falsifier:** If unified objective fails to achieve Pareto dominance or ≥10% hypervolume improvement at iso-perplexity, efficiency gains are not realizable.

---

## Experimental Design

### Three-Phase Roadmap

**Phase 1: Correlation Validation (3 months, 125M scale)**

- **Models:** 3 variants × 3 seeds = 9 training runs
  - (A) Baseline transformer
  - (B) Explicit sr_ℓ^res regularization
  - (C) Implicit control (adaptive learning rates)
- **Dataset:** C4 (10B token subset)
- **Measurements:**
  - During training: sr_ℓ^res, perplexity, per-layer representation rank, gradient SNR
  - Post-training: intrinsic LoRA rank, KV effective rank, attention entropy
- **Success Gate:** P1 and P2 validated (r ≥ 0.5, iso-perplexity maintained)

**Phase 2: Mechanistic Validation (conditional on Phase 1 success)**

- **Tests:**
  - Entropy-controlled Fisher rank measurement (temperature-scaled logits)
  - Noise-transport experiment (inject isotropic perturbations, measure output covariance rank)
  - Temporal ordering (Granger causality: sr_ℓ^res reduction precedes efficiency gains)
  - Mediation analysis (sr_ℓ^res explains ≥50% variance beyond confounds)
  - Intervention experiments (subset-layer regularization to test causal localization)
- **Scaling test:** 125M, 350M, 1B parameters
  - Width-normalized metric: nsr_ℓ = sr_ℓ^res / d
  - Test log-log slope: slope_reg < slope_baseline (super-logarithmic decay)
- **Success Gate:** All mechanistic tests pass, correlation strengthens with scale

**Phase 3: Efficiency & Robustness (conditional on Phase 2 success)**

- **Domain robustness:** Natural language (C4), code (The Stack), controlled entropy-sweep corpus
- **Baseline comparison:** Unified objective vs. independent optimization stack (baseline + post-hoc ARD-LoRA + KV compression + attention pruning) at equal total compute
- **Pareto analysis:** Report 2D fronts and 3D hypervolume
- **Success Gate:** P3 validated (Pareto dominance + hypervolume ≥10%)

### Datasets & Baselines

**Datasets:**
- Primary: C4 (10B tokens for Phase 1, full for Phase 2/3)
- Robustness: The Stack (code corpus, high-entropy domain)
- Controlled: Entropy-sweep corpus (natural language + shuffled tokens at varying ratios)

**Baselines:**
1. Standard transformer pretraining (no regularization)
2. Independent optimization stack (baseline + post-hoc LoRA + KV + attention)
3. Factorized regularization (three independent penalties: nuclear norm, entropy, sparsity - ablation)

---

## Key Assumptions & Risks

### A1: Local Linearization Validity

**Assumption:** Linearized propagation Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T is globally informative for KV covariance structure.

**Consequence if Violated:** If nonlinearities destroy linearization, Jacobian rank won't predict KV compressibility.

**Validation:** Noise-transport experiment (inject perturbations, measure propagated covariance rank).

### A2: Fisher Approximation

**Assumption:** Fisher ≈ J^T J holds under entropy-controlled conditions.

**Consequence if Violated:** If output entropy dominates Fisher spectrum more than Jacobian structure, correlation collapses.

**Validation:** Direct empirical Fisher measurement under temperature-scaled logits.

### A3: Iso-Perplexity Sufficiency

**Assumption:** Iso-perplexity control ensures functional capacity is preserved.

**Consequence if Violated:** If capacity redistributes unevenly (early layers collapse, later layers compensate), global constraint is actually depth reallocation.

**Validation:** Layerwise sensitivity audit (layer variance < 2× mean threshold).

### A4: Measurement Noise

**Assumption:** Spectral norm estimation via randomized power iteration has acceptable variance (CV < 15%).

**Consequence if Violated:** If CV > 20%, correlation tests are noise-dominated and underpowered.

**Validation:** Upfront validation on 50M model (Weeks 1-4) with failure threshold.

**HIGH RISK:** This is the primary feasibility bottleneck identified by Prof. Pax.

### A5: Structural Causality

**Assumption:** Correlation reflects structural coupling, not confounds (optimizer bias, corpus entropy, width).

**Consequence if Violated:** If mediation < 30%, correlation is spurious.

**Validation:** Mediation analysis + Granger causality + intervention experiments.

---

## Novelty & Differentiation

### Core Novelty

**First work to test whether parameter efficiency (LoRA), memory efficiency (KV compression), and computational efficiency (sparse attention) are correlated manifestations of a single structural property (Jacobian stable rank) vs. independent dimensions.**

### Paradigm Shift

**From:** Train general model → post-hoc optimization per deployment scenario (LoRA + KV compression + attention pruning)

**To:** Train for efficiency-readiness via unified structural constraint → deploy without additional tuning

**Impact:** Reduces deployment optimization from N×M (scenarios × dimensions) to N+M complexity.

### Differentiation from Prior Work

| Work | What It Does | Our Difference |
|------|-------------|----------------|
| ARD-LoRA (Shinwari et al. 2025) | Optimizes rank allocation during fine-tuning | We optimize for adaptation-readiness **during pretraining** via Jacobian constraint |
| KV-CAT (Gelberg et al. 2026) | Trains for KV compressibility in isolation | We test **mechanistic coupling** between KV, parameters, attention via shared constraint |
| Mamba-2 (Dao & Gu 2024) | Architectural change (SSMs replacing attention) | **Objective-level change** (stable rank regularization) that's architecture-agnostic |

---

## Feasibility Assessment

### Meets Constraints: ✓

- **No new benchmarks:** Uses C4, The Stack (existing datasets) and standard metrics
- **No synthetic data:** Real pretraining corpora only
- **No human evaluation:** All metrics automated (SVD, correlation, entropy)

### Resource Requirements

**Compute:**
- Phase 1: Single 8-GPU node, 3 months (9 × 125M models)
- Phase 2: 2-3 GPU nodes, 2 months (scaling + mechanistic tests)
- Phase 3: 4-6 GPU nodes, 3 months (1B scale + robustness)

**Critical Path:** Measurement infrastructure validation (Weeks 1-4).

### Risk Mitigation

**HIGH RISK: Measurement Noise (CV > 20%)**
- **Impact:** Invalidates correlation tests (r ≥ 0.5 threshold becomes meaningless)
- **Mitigation:** Upfront validation on 50M model with failure threshold. If CV > 20%, refine estimators or pivot to proxy metrics before Phase 1.

**MEDIUM RISK: Causality vs. Correlation**
- **Impact:** Stable rank may be proxy for optimizer bias, not causal driver
- **Mitigation:** Three-pronged validation: mediation analysis, Granger causality, intervention experiments

**LOW RISK: Standard Measurements**
- LoRA rank, KV SVD, attention entropy have existing implementations

### Decision Gates

1. **Week 4:** Measurement validation succeeds (CV < 15% on 50M model)
2. **Phase 1 end:** P1 and P2 validated (r ≥ 0.5, iso-perplexity)
3. **Phase 2 end:** Mechanistic tests pass (mediation ≥ 50%, entropy-controlled Fisher r ≥ 0.5)
4. **Phase 3 end:** P3 validated (Pareto dominance)

---

## Expected Outcomes

### If Hypothesis Confirmed

**Scientific Impact:**
- Demonstrates efficiency dimensions are correlated manifestations of trainable structure, not independent
- Shifts paradigm from post-hoc optimization to pretraining-time emergence

**Practical Impact:**
- Enables "train once, deploy efficiently" - models support LoRA, KV compression, sparse attention without post-deployment tuning
- Reduces optimization complexity from N×M to N+M

**Follow-Up Research:**
- Efficiency-aware architecture search
- Transfer efficiency prediction (predict adaptation efficiency without fine-tuning)
- Continual learning (test if structured representations reduce catastrophic forgetting)

### If Hypothesis Refuted

**Scientific Impact:**
- Proves efficiency dimensions are fundamentally orthogonal
- Justifies current separate-optimization practices as theoretically necessary

**Practical Impact:**
- Redirects research toward improving individual efficiency techniques
- Clarifies deployment optimization must remain multi-stage

**Follow-Up Research:**
- Investigate why efficiency dimensions decouple despite shared architecture
- Develop better independent optimization for each dimension
- Study task-specific efficiency profiles

---

## Persona Verdicts

| Persona | Role | Verdict | Key Concern |
|---------|------|---------|-------------|
| 🔭 Dr. Nova | Novelty | **STRONG** | None - paradigm shift is genuine |
| 🔬 Prof. Vera | Falsifiability | **STRONG** | Measurement validation required upfront |
| 🎯 Dr. Sage | Significance | **STRONG** | None - both success and failure advance field |
| ⚙️ Prof. Pax | Feasibility | **MODERATE** | HIGH RISK: Spectral norm noise (CV > 20%) |
| 🛡️ Dr. Ally | Strengthening | **STRONG** | None - hypothesis now concrete and testable |
| 🔍 Prof. Rex | Stress-Test | **STRONG** | Mitigation strategies address all major objections |

**Consensus:** 5 STRONG, 1 MODERATE → READY for Phase 2B

---

## Discussion Evolution

### Key Exchanges

**Exchange 1 (Dr. Nova):** Proposed fuzzy "unified sparsity" metaphor  
**Exchange 6 (Dr. Ally):** **BREAKTHROUGH** - Introduced Jacobian stable rank as mechanistic bridge  
**Exchange 12 (Prof. Vera):** **CRITICAL REFINEMENT** - Formalized residual-corrected metric sr_ℓ^res  
**Exchange 15 (Prof. Pax):** Finalized implementation roadmap with measurement validation gate

### Convergence Criteria Met

✓ Specific core claim with mathematical formulation  
✓ Mechanistic explanation (Jacobian → Fisher/covariance/attention)  
✓ Testable predictions with quantitative thresholds (r ≥ 0.5, ≥20%, Pareto dominance)  
✓ Novelty articulated (first test of correlation vs. independence)  
✓ Feasibility established (phased approach with early stopping gates)  
✓ Major objections addressed (residual confound, measurement noise, causality, scaling)

---

## Phase 2B Readiness: ✓ READY

All required sections present in `03_refinement.yaml`:
- **Section 0:** Established facts (4 BUILD_ON, 1 PROVE_NEW)
- **Section 1.1:** Core hypothesis statement with H0
- **Section 1.2:** Variables table (1 IV, 4 DVs, 4 controlled)
- **Section 1.3:** 3-step causal mechanism with falsifiers
- **Section 1.4:** 5 key assumptions (A1-A5) with violation consequences
- **Section 1.5:** Scope and limitations
- **Section 1.6:** 3 testable predictions (P1, P2, P3) with success/falsification criteria
- **Section 2:** Experimental setup (datasets, model, baselines)
- **Section 3:** Novelty differentiation
- **Section 4:** Related work and baselines
- **Section 5:** Phase 2B readiness with open questions

**Open Questions for Phase 2B:**
1. Does correlation strengthen with width (125M → 1B) or plateau?
2. Do high-entropy domains (code) weaken correlations or preserve them?
3. Can morphable architecture (attention↔SSM) learn efficiency structure dynamically?
4. Is measurement infrastructure reliable at 1B+ scale?
