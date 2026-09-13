---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-03-17T00:49:00Z"
hypothesis_id: H-MarginFlip-v1
pipeline_project_id: adb36f20-2548-4b70-b0ee-2a68f806d5de
phase2b_task_id: 199fb665-576f-42a5-870c-c88ed3c6da4e
phase2c_task_id: 39226cec-675b-4be2-b998-27ad9abca8ca
---

# Verification Plan: Geometric Fingerprints of Alignment — Pre-Alignment Confidence Margin Predicts Argmax Instability

**Date:** 2026-03-17
**Hypothesis ID:** H-MarginFlip-v1
**Confidence:** 0.78
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard RLHF alignment (PPO and DPO) on LLMs of scale 1.4B–7B, if pre-alignment confidence margin (top-1 minus top-2 log-probability on base model MCQ items) is low, then post-alignment argmax inversion probability is higher, because DPO's log-odds optimization objective amplifies existing option-probability differences more directly than PPO's KL-penalized gradient, creating method-specific geometric fingerprints in how alignment restructures decision boundaries — fingerprints detectable from the base model alone.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in argmax inversion probability between low-margin and high-margin MCQ items after controlling for KL divergence between base and aligned models. Equivalently: the Margin × Method interaction term is not significantly different from zero, meaning PPO and DPO do not differ in how they relate pre-alignment margin to argmax stability.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MMLU (primary) + TruthfulQA + ARC-Challenge (cross-benchmark validation) (standard) | MMLU provides 57 subject categories with ~14K items enabling category-level analysis; TruthfulQA tests alignment-sensitive knowledge; ARC tests factual MCQ. Together they cover factual, reasoning, and safety-relevant MCQ types. |
| **Model** | Pythia-1.4B/6.9B base + aligned variants; Llama-7B base + aligned variants | Matched base→aligned pairs with documented alignment method (PPO vs DPO). Pythia family provides scale variation. Tulu-2 provides matched PPO/DPO pair from same base. Li et al. used same Pythia models. |

**Dataset Details:**
- Source: HuggingFace datasets: cais/mmlu, truthful_qa, allenai/ai2_arc
- Path: Loaded via lm-evaluation-harness --tasks mmlu,truthfulqa_mc1,arc_challenge

**Model Details:**
- Type: decoder-only transformer
- Source: EleutherAI/pythia-{1.4b,6.9b} on HuggingFace Hub; allenai/tulu-2-base + tulu-2-dpo-7b + tulu-2-ppo-7b; meta-llama/Llama-2-7b-hf + aligned variants

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Li et al. [2024] post-alignment trustworthiness evaluation | Characterizes trustworthiness degradation (e.g., -25% truthfulness) but no pre-alignment predictors | Anthropic HH, Pythia 1.4B/2.8B/6.9B/Llama-7B |
| Fan et al. [2026] pretraining→SFT accuracy ranking correlation | R²=0.7–0.9 cross-stage accuracy correlation depending on benchmark | 20 benchmarks, 240M/1B models |
| Plaut et al. [2024] MSP correctness prediction | 245/280 significant AUROCs; R²=0.94 for MSP-correctness across 15 models | ARC, HellaSwag, MMLU, TruthfulQA, WinoGrande |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pre-alignment base model log-probs are accessible and meaningful for MCQ on MMLU/TruthfulQA/ARC | Plaut et al. [2024] successfully extract meaningful MSPs from 15 fine-tuned LLMs on same benchmark suite | Margin cannot be computed — experiment is infeasible |
| A2 | Publicly available base→aligned model pairs exist with documented alignment method (PPO vs DPO) and matching base checkpoints | HuggingFace Hub: allenai/tulu-2-base vs tulu-2-dpo-7b vs tulu-2-ppo-7b; Pythia base with TRL-aligned variants | Must run fresh alignment — increases scope significantly |
| A3 | Alignment-induced logit perturbations on MCQ are systematic enough to detect statistically across N~14K MMLU items | h-m3 results: 99.7% argmax shift for PPO at 1.4B confirms large effect size exists for at least one model | Effect sizes below detectable threshold — experiment inconclusive |
| A4 | DPO and PPO produce distinguishably different variance structures in logit deltas, not just different magnitudes | Xu et al. [2024]: DPO suffers distribution shift, PPO has KL constraint — mechanistically distinct behavior expected | Interaction term is zero — hypothesis is falsified but cleanly |
| A5 | Pre-alignment base model confidence geometry is sufficiently stable to encode structural information | Fan et al. [2026]: accuracy rankings transfer from pretraining to SFT with non-zero correlation | Margin is noise at pre-alignment stage — entire predictive framework collapses |

### 1.6 Research Gap & Novelty

**Gap:** No existing study connects pre-alignment base model confidence geometry to post-alignment argmax stability. h-m3 confirmed H2 (argmax redistribution) exists; this work predicts WHEN and WHERE H2 is most severe, enabling systematic pre-deployment risk assessment.

**Novelty:** First empirical study with method-specific (PPO vs DPO) geometric signatures. Extends Fan et al.'s pretraining→SFT correlation work to pretraining→RLHF. Key innovation: pre-alignment confidence margin as a practical pre-deployment diagnostic for alignment-induced decision boundary instability.

**Scope Reduction (55%):** 5 of 7 claims in the established facts registry are BUILD_ON (pre-validated). Only 2 PROVE_NEW claims require new experimental verification: (1) margin→flip correlation, (2) method-specific geometric signatures.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Margin Encodes Post-Alignment Argmax Stability**

**Statement:** Under standard RLHF alignment on MCQ benchmarks (MMLU/TruthfulQA/ARC), if pre-alignment confidence margin (top-1 minus top-2 log-prob, z-scored within model) is low, then post-alignment argmax inversion probability is significantly higher, confirming the existence of a predictive geometric signal in base model confidence landscapes.

**Rationale:** This foundational hypothesis establishes that pre-alignment base model logit geometry encodes epistemic uncertainty in a manner predictive of post-alignment behavior. Without this correlation existing at statistically significant levels (AUROC ≥ 0.75 on cross-benchmark evaluation), the entire predictive framework collapses. This existence check must be confirmed before investigating method-specific mechanisms.

**Variables:**
- Independent: Pre-alignment confidence margin (continuous, z-scored within model; log-prob(top-1) − log-prob(top-2))
- Dependent: Argmax flip indicator (binary: 1 if argmax(aligned) ≠ argmax(base))
- Controlled: KL divergence (base ‖ aligned), answer position, model scale

**Verification Protocol:**
1. Extract base model log-probs via lm-evaluation-harness on MMLU (~14K items), TruthfulQA, ARC-Challenge for all model pairs.
2. Compute confidence margin = log-prob(top-1) − log-prob(top-2), z-scored within each model pair.
3. Compute flip indicator (1 if argmax changes from base to aligned model) for all items × model pairs.
4. Fit logistic regression: logit P(flip) = β₀ + β₁·margin + β₄·KL; test β₁ < 0, p < 0.005.
5. Compute cross-benchmark AUROC: train on MMLU, evaluate on TruthfulQA and ARC; require AUROC ≥ 0.75.

**Success Criteria:**
- Primary: β₁ < 0, p < 0.005 (Bonferroni-corrected), partial η² ≥ 0.06
- Secondary: Cross-benchmark AUROC ≥ 0.75 on held-out TruthfulQA/ARC
- Tertiary: Monotonically decreasing P(flip|margin quintile) curve (non-monotonic = falsified)

**Failure Response:**
- IF fails (β₁ ≥ 0 or AUROC < 0.65): STOP — foundational existence claim is wrong; reassess entire hypothesis

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 1.6 P1 (primary prediction); Section 5 sh1_existence

---

**H-M1: Alignment Injects Structured (Non-Isotropic) Logit Perturbations**

**Statement:** Under RLHF alignment of LLMs (PPO and DPO), if alignment-induced logit deltas (aligned_logits − base_logits) are computed per MCQ item across model pairs, then the perturbations are axis-specific and non-isotropic (structured), because Li et al. [2024] empirically confirmed heterogeneous, axis-specific trustworthiness changes rather than isotropic noise post-RLHF.

**Rationale:** This mechanism step validates that the logit perturbation from alignment has structure (not random noise), which is a necessary precondition for the margin-specific amplification effect in H-M2/H-M3. If perturbations are isotropic, the causal chain from pre-alignment geometry to post-alignment flip is broken.

**Variables:**
- Independent: Alignment method (PPO vs DPO) and model family
- Dependent: Variance of logit delta across MCQ option axes; cosine consistency within model pair
- Controlled: KL divergence magnitude, model scale

**Verification Protocol:**
1. Compute logit delta vectors (Δ = aligned_4D_logits − base_4D_logits) for each MCQ item across all model pairs.
2. Measure anisotropy: compute eigenvalue ratio of Δ covariance matrix; isotropic ≡ uniform eigenvalues.
3. Test whether Δ variance is significantly higher along the base model's decision axis vs. orthogonal axes (paired t-test per model family).
4. Replicate across Pythia-1.4B, Pythia-6.9B, Tulu-2 (3 model families minimum).
5. Compare anisotropy magnitude between PPO and DPO groups.

**Success Criteria:**
- Primary: Anisotropy ratio significantly > 1.0 (p < 0.05) in ≥ 2 of 3 model families
- Secondary: Logit delta variance higher along decision axis than orthogonal (directional test)

**Failure Response:**
- IF fails (isotropic): EXPLORE — document as null result for perturbation structure; mechanism chain narrows to H-E1 only

**Dependencies:** H-E1

**Source:** Phase 2A Section 1.3 Causal Step 2; Li et al. [2024] evidence

---

**H-M2: DPO's Objective Amplifies Low-Margin Regions More Than PPO**

**Statement:** Under standard RLHF alignment (PPO vs DPO), if logit delta variance is decomposed by pre-alignment margin quintile, then DPO produces significantly higher logit delta variance in low-margin regions (bottom quintile) compared to PPO, because DPO's log-odds objective (L_DPO ∝ log σ(β·log ratio)) directly amplifies option-probability differences while PPO's KL penalty globally constrains distributional drift.

**Rationale:** This is the core method-specific mechanism step. It tests whether the theoretical derivation from DPO/PPO loss functions (Xu et al. [2024]) maps to empirically observable differences in how alignment perturbs low-margin items. This is the mechanistic explanation for why DPO should produce more argmax flips at low margin than PPO.

**Variables:**
- Independent: Alignment method (PPO vs DPO); pre-alignment margin quintile
- Dependent: Logit delta variance per margin quintile per method
- Controlled: KL divergence (overall update magnitude); model scale; training data (matched pairs)

**Verification Protocol:**
1. Stratify MCQ items by pre-alignment margin quintile (Q1=lowest, Q5=highest margin).
2. Compute logit delta variance for PPO and DPO groups within each quintile.
3. Apply mixed-effects model: variance ~ method × quintile + KL + (1|model_family).
4. Test Method × Quintile interaction: DPO should show higher variance specifically in Q1.
5. Verify KL-controlled: run model with and without KL covariate; interaction must survive KL inclusion.

**Success Criteria:**
- Primary: Method × Quintile interaction significant (p < 0.05); DPO variance > PPO variance in Q1
- Secondary: Interaction survives KL covariate control (effect doesn't disappear when KL added)
- Tertiary: Consistent across ≥ 2 model families

**Failure Response:**
- IF fails: EXPLORE — document as null result for method-specific variance; scope narrows to P(flip|margin) without method distinction

**Dependencies:** H-M1

**Source:** Phase 2A Section 1.3 Causal Step 3; Xu et al. [2024] mechanism

---

**H-M3: Margin × Method Interaction Predicts Differential Flip Rates (KL-Controlled)**

**Statement:** Under RLHF alignment (PPO and DPO) on LLMs 1.4B–7B, the Margin × Method interaction term in the mixed-effects logistic regression (logit P(flip) = β₀ + β₁·margin + β₂·method + β₃·(margin×method) + β₄·KL) is in the predicted direction — DPO shows steeper flip-rate increase as margin decreases — and this interaction survives KL divergence control, confirming the effect is geometric rather than magnitude-based.

**Rationale:** This is the primary falsifiable test of the method-specific geometric fingerprint claim. If DPO and PPO differ in P(flip|margin) only because DPO produces larger policy shifts (higher KL), including KL as covariate will eliminate the interaction. If the geometric structure survives KL control, it confirms method-specific geometric signatures independent of update magnitude.

**Variables:**
- Independent: Confidence margin (continuous, z-scored), alignment method (PPO/DPO/SFT)
- Dependent: Argmax flip indicator (binary)
- Controlled: KL divergence, answer position, model scale, dataset

**Verification Protocol:**
1. Fit primary mixed-effects logistic regression with full interaction model (β₀–β₅).
2. Test β₃ direction: coefficient for margin×method must be in predicted direction (DPO steeper).
3. Test β₃ significance: p < 0.05 for interaction term.
4. Compare model with vs. without KL covariate: β₃ must remain significant with KL included.
5. Compute Odds Ratio for 1-SD margin decrease for DPO vs PPO; target OR ≥ 1.8 for DPO.

**Success Criteria:**
- Primary: β₃ in predicted direction at p < 0.05, consistent across ≥ 3 model families
- Secondary: Odds Ratio ≥ 1.8 for DPO at 1-SD margin decrease
- Tertiary: β₃ survives KL covariate inclusion (KL-controlled effect)

**Failure Response:**
- IF β₃ disappears when KL added: PIVOT to magnitude-based explanation; revise hypothesis
- IF β₃ in wrong direction: ABORT method-specific claim; retain margin main effect (H-E1) only

**Dependencies:** H-M2

**Source:** Phase 2A Section 1.6 P2; Section 1.3 Key Tension (KL confound)

---

**H-M4: DPO Logit Deltas Show Higher Cosine Alignment with Base Decision Axis at Low Margin**

**Statement:** Under standard RLHF alignment, if cosine similarity between alignment-induced logit delta and base model decision axis (normalized top-1 minus top-2 logit direction) is computed per MCQ item, then DPO items in the bottom margin quintile show significantly higher cosine alignment than PPO items in the same quintile, confirming DPO amplifies along the existing boundary direction while PPO diffuses more globally.

**Rationale:** This geometric confirmation test provides mechanistic evidence for the directional amplification claim. High cosine alignment between Δ and the base decision axis means alignment pushes the logit in the same direction as the pre-existing top-1/top-2 gradient — amplifying the boundary structure. This distinguishes structural amplification from random perturbation.

**Variables:**
- Independent: Alignment method (PPO vs DPO), margin quintile
- Dependent: Cosine similarity between Δ_logit and base_decision_axis (normalized)
- Controlled: KL divergence, margin quintile (matched comparison)

**Verification Protocol:**
1. For each MCQ item: compute base_decision_axis = unit vector in direction (top1_logit − top2_logit) in 4D option space.
2. Compute Δ_logit = aligned_4D_logits − base_4D_logits for each model pair.
3. Compute cosine(Δ_logit, base_decision_axis) per item per method.
4. Compare mean cosine by method × margin quintile (bottom Q1 focus).
5. Apply Welch's t-test: DPO Q1 cosine > PPO Q1 cosine; use bootstrap CIs (N=3-4 model pairs, small sample).

**Success Criteria:**
- Primary: DPO items in Q1 show significantly higher cosine alignment than PPO (Welch's t, p < 0.05)
- Secondary: Effect consistent across ≥ 2 benchmarks

**Failure Response:**
- IF fails: EXPLORE — document as null for geometric directionality; retain statistical interaction (H-M3) even if geometric interpretation fails

**Dependencies:** H-M3

**Source:** Phase 2A Section 1.6 P3; Section 1.3 Causal Step 3 (boundary amplification)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | β₁ < 0, p < 0.005, AUROC ≥ 0.75 | STOP — reassess entire hypothesis |
| H-M1 | MUST_WORK | Anisotropy ratio > 1.0, p < 0.05 in ≥ 2 families | EXPLORE — narrow scope |
| H-M2 | SHOULD_WORK | DPO variance > PPO variance Q1, KL-controlled | EXPLORE — document null |
| H-M3 | SHOULD_WORK | β₃ predicted direction, p < 0.05, OR ≥ 1.8 | PIVOT or ABORT method claim |
| H-M4 | SHOULD_WORK | DPO Q1 cosine > PPO Q1, p < 0.05 | EXPLORE — geometric null |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |
| **Total** | 5 hypotheses | **7 weeks** |

**Total Duration:** 7 weeks (formula: 2 + 4 + 1 = 7; H-E1 2w + H-M1 2w + H-M2–4 each 1w)

---

## 4. Risk Analysis

### 4.1 Risk-Assumption Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Log-prob extraction infeasible | A1 | H-E1, H-M1, H-M2, H-M3, H-M4 | Critical |
| R2: No matched PPO/DPO model pairs | A2 | H-M2, H-M3, H-M4 | High |
| R3: Effect sizes below detection threshold | A3 | H-E1, H-M1–H-M4 | High |
| R4: PPO/DPO variance structures indistinct | A4 | H-M2, H-M3 | Medium |
| R5: Base model confidence geometry is noise | A5 | H-E1 (and all downstream) | Critical |

### 4.2 Mitigation Strategies

**Risk R1 (Critical): Log-prob extraction infeasible**
- Source: A1 — log-probs not accessible/meaningful
- Prevention: Verify lm-evaluation-harness `--output_path` flag works on all target models before full run; test with 100-item pilot on 1 model pair
- Detection: Pilot test returns NaN, inf, or uniform distributions
- Response: PIVOT to alternative extraction (direct HuggingFace forward pass); ABORT if all extraction methods fail

**Risk R2 (High): No matched PPO/DPO model pairs**
- Source: A2 — no documented base→aligned pairs available
- Prevention: Pre-verify HuggingFace Hub availability (tulu-2 pairs, Pythia TRL variants) before experiment setup
- Detection: Model cards missing alignment method specification; no base checkpoint available
- Response: SCOPE — use only available pairs (minimum: tulu-2 PPO/DPO matched pair); if <2 pairs available, ABORT method comparison

**Risk R3 (High): Effect sizes below detection threshold**
- Source: A3 — perturbations too small across N~14K items
- Prevention: Pre-power analysis using h-m3 PPO effect (99.7% flip rate at 1.4B) to set expectations; note effect may be much smaller for margin-specific subset
- Detection: β₁ not significant at p < 0.005 even with full 14K item MMLU set
- Response: EXPLORE — run on larger item set (all 3 benchmarks combined); if still null, document as genuine null result

**Risk R4 (Medium): PPO/DPO variance indistinct**
- Source: A4 — methods produce similar logit delta structures
- Prevention: Include SFT-only baseline to calibrate method-sensitivity measurement
- Detection: Method × Quintile interaction p > 0.1 in all model families
- Response: PIVOT — report null for method-specific interaction; retain margin main effect from H-E1 as primary contribution

**Risk R5 (Critical): Base model confidence geometry is noise**
- Source: A5 — pre-alignment confidence margin has no signal
- Prevention: Validate margin-correctness correlation before flip analysis (replicate Plaut et al. on our specific model set)
- Detection: MSP-correctness AUROC < 0.60 on base models
- Response: ABORT — foundational assumption violated; route to Phase 0 with finding: margin-correctness link fails on this model set

### 4.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Log-prob extraction infeasible | A1 | Critical | All | Pilot test + fallback extraction |
| R2 | No matched model pairs on HuggingFace | A2 | High | H-M2–M4 | Pre-verify Hub before full run |
| R3 | Effect below detection threshold | A3 | High | All | Power analysis + multi-benchmark |
| R4 | PPO/DPO structures indistinct | A4 | Medium | H-M2–M3 | SFT baseline calibration |
| R5 | Base geometry is noise | A5 | Critical | H-E1→All | Plaut replication check first |

Critical Risks: 2 | High Risks: 2 | Medium Risks: 1 | Low Risks: 0

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Existence]
    H-E1: Margin encodes argmax stability
    (MUST_WORK gate — no dependencies)
         │
         ▼ Gate 1 (MUST PASS before proceeding)
[Level 1 - Mechanism: Structured Perturbation]
    H-M1: Alignment injects non-isotropic logit perturbations
    (MUST_WORK gate — depends on H-E1)
         │
         ▼
[Level 2 - Mechanism: DPO Amplification]
    H-M2: DPO amplifies low-margin regions more than PPO
    (SHOULD_WORK gate — depends on H-M1)
         │
         ▼
[Level 3 - Mechanism: Interaction Test]
    H-M3: Margin × Method interaction survives KL control
    (SHOULD_WORK gate — depends on H-M2)
         │
         ▼
[Level 4 - Mechanism: Geometric Confirmation]
    H-M4: DPO logit deltas cosine-aligned with base decision axis
    (SHOULD_WORK gate — depends on H-M3)
         │
         ▼

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2    │ W3-4    │ W5      │ W6      │ W7
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 1: Foundation
  H-E1             │ ████████│         │         │         │
  [Gate 1]         │         │ ◆       │         │         │
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 2: Mechanisms
  H-M1             │         │ ████████│         │         │
  H-M2             │         │         │ ████    │         │
  H-M3             │         │         │         │ ████    │
  H-M4             │         │         │         │         │ ████
  [Gate 2]         │         │         │         │         │    ◆
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 + 1 + 1 (H-M2–4) = 7 weeks
Slack Available: 0 weeks (all sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (not required)

Verification Phases: 2
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1–H-M4): 5 weeks

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
Step 2: Evaluate Gate 1 → If PASS, proceed; if FAIL, STOP
Step 3: Execute H-M1 (Structured perturbation) — Week 3-4
Step 4: Evaluate H-M1 MUST_WORK gate → If FAIL, scope to H-E1 only
Step 5: Execute H-M2 (DPO amplification at low margin) — Week 5
Step 6: Execute H-M3 (Margin × Method interaction, KL-controlled) — Week 6
Step 7: Execute H-M4 (Cosine geometric confirmation) — Week 7
Step 8: Evaluate Gate 2 — Document outcome for Phase 5/6
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Pre-alignment confidence margin is a predictive geometric signal for post-alignment argmax stability, with method-specific signatures (DPO > PPO flip rates at low margin) that survive KL divergence control — confirming geometric restructuring rather than magnitude-based effects.

**Supporting Evidence:**
1. Plaut et al. [2024]: MSP predicts correctness with R²=0.94 — confirming base model logit geometry encodes epistemically meaningful signal
2. Li et al. [2024]: RLHF induces axis-specific, heterogeneous trustworthiness changes — confirming structured (non-isotropic) perturbations
3. Xu et al. [2024]: DPO suffers distribution shift via direct log-odds amplification; PPO's KL term constrains drift — mechanistic basis for method-specific signatures

**Strengths:**
- Mechanistically grounded: method-specific predictions derived from loss function forms (not post-hoc)
- Pre-registered falsification criteria: β₁ direction, p-value threshold, AUROC minimum
- KL covariate control addresses key confound (magnitude vs. geometry distinction)
- Uses established model families and datasets (Li et al. exact setup replicable)

**Expected Outcomes:**
- Primary (P1): β₁ < 0, p < 0.005, AUROC ≥ 0.75 (margin predicts flip)
- Secondary (P2): β₃ predicted direction, DPO steeper at low margin, OR ≥ 1.8
- Tertiary (P3): DPO logit deltas cosine-aligned with base decision axis in Q1

### 6.2 Antithesis (H0-Based)

**Null Hypothesis:** There is no significant difference in argmax inversion probability between low-margin and high-margin MCQ items after KL control. The Margin × Method interaction is zero.

**Counter-Arguments:**
1. KL confound: DPO simply produces larger policy shifts — all observed margin-flip correlation may be explained by KL magnitude, not geometric structure
2. Model heterogeneity: Pythia-1.4B showed extreme PPO catastrophe (rho=-0.3241 in h-m3) suggesting below-capability behavior distorting the systematic analysis
3. Benchmark contamination: models trained after MMLU publication may show non-representative behavior

**Potential Failure Points:**
- R5 materializes: base model margin is noise → H-E1 fails immediately
- R4 materializes: PPO/DPO interaction disappears under KL control → H-M3 falsified
- Small N problem: cosine projection test underpowered at N=3-4 model pairs

**Conditions Under Which H0 Would Be Supported:**
- β₁ ≥ 0 OR p ≥ 0.005 (margin main effect null)
- β₃ not in predicted direction OR disappears when KL added
- No significant cosine alignment difference between methods

### 6.3 Synthesis

The verification plan addresses the thesis-antithesis dialectic through structured sequential testing:

**Resolution Path:**
1. **H-E1 (Foundation):** Tests margin main effect (β₁) with strict KL control — if H0 holds even without method distinction, the entire framework is wrong (Gate 1 = STOP)
2. **H-M1 (Perturbation structure):** Tests non-isotropy claim directly — separates structural from random perturbation before attributing to method
3. **H-M2–H-M3 (Method interaction):** Tests method-specific claim with and without KL covariate — the KL-controlled interaction test is the critical discriminator between "DPO bigger update" and "DPO geometric structure"
4. **H-M4 (Cosine confirmation):** Provides geometric interpretation beyond statistical correlation

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1 + H-M2 + H-M3 + H-M4 all pass → Complete geometric fingerprint confirmed
2. **Partial Support (margin main effect only):** H-E1 passes, H-M3 β₃ not significant after KL → Margin predicts flips but not method-specifically; contribution still valid (pre-deployment diagnostic without method distinction)
3. **Partial Support (geometric without cosine):** H-M3 passes, H-M4 fails → Statistical interaction confirmed but geometric interpretation limited; still publishable
4. **No Support:** H-E1 fails → Foundational claim wrong; route to Phase 0

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Margin predicts flip (β₁ < 0) | Random correlation; KL confound | H-E1 with KL covariate |
| Mechanism | Structured non-isotropic perturbation | Isotropic noise indistinguishable | H-M1 anisotropy test |
| Method-specificity | DPO amplifies more at low margin | DPO just has larger KL shift | H-M3 KL-controlled interaction |
| Geometry | DPO aligns Δ with base decision axis | Cosine underpowered at N=3-4 | H-M4 with bootstrap CIs |
| Generalization | Cross-benchmark AUROC ≥ 0.75 | Benchmark-specific effect | Cross-benchmark evaluation |

**Overall Robustness Score:** High (multiple independent tests, KL control pre-specified, pre-registered falsification criteria)

**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Appendices

### 7.1 Executive Summary

**Main Hypothesis:** H-MarginFlip-v1 — Pre-alignment confidence margin (top-1 minus top-2 log-prob, z-scored) predicts post-alignment argmax flip probability with method-specific signatures (DPO > PPO at low margin).
- ID: H-MarginFlip-v1 | Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (55% scope reduction from 5 BUILD_ON established facts)
- Sub-Hypotheses: 5 total (H-E1, H-M1–H-M4; no H-C needed)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1 MUST_WORK; Gate 2: Post-H-M4)

**Risk Assessment:** High (2 Critical risks: R1 log-prob extraction, R5 base geometry noise)
- Primary concerns: A1 extraction feasibility, A5 base model signal validity

**Immediate Action:** Run Plaut replication (margin-correctness AUROC check on base models) before full H-E1 experiment to validate A5. Then begin H-E1 with pilot 100-item test.

### 7.2 Conclusions

**Key Achievements:**
- 5 sub-hypotheses across 2 phases, covering causal chain from base geometry → perturbation structure → method-specific amplification → geometric confirmation
- H0 addressed: β₃ interaction term must be non-zero and survive KL control

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Pre-alignment margin monotonically predicts flip probability; AUROC ≥ 0.75 cross-benchmark
- Gate 1: MUST PASS (β₁ < 0, p < 0.005)

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Alignment perturbations are non-isotropic (structured); anisotropy ratio > 1.0
- H-M2: DPO amplifies low-margin regions; higher Δ variance in Q1 for DPO vs PPO
- H-M3: Margin × Method interaction survives KL control; β₃ predicted direction, OR ≥ 1.8
- H-M4: DPO logit deltas cosine-aligned with base decision axis; geometric structural confirmation
- Gate 2: H-E1 + H-M1 MUST_WORK; H-M2–H-M4 SHOULD_WORK (scope narrowing if fail)

**Critical Decision Points:**
1. **Gate 1 (Foundation):** H-E1 must pass — FAIL → STOP, reassess hypothesis entirely
2. **Gate 2 (Mechanisms):** H-M1 must pass — FAIL → narrow to existence contribution only; H-M2–H-M4 failures document limitations but don't block Phase 5

**Open Questions:**
- Does the margin-flip relationship generalize to instruction-tuned base models (SFT→RLHF) vs. raw base→RLHF?
- Is the capability threshold real (segmented regression) or smooth scaling? (Pythia-1.4B PPO catastrophe)
- Does the cosine projection test (H-M4) have sufficient power at N=3-4 model pairs, even with bootstrap CIs?

**Recommendations:**
1. **Immediate Actions:** Validate A5 first (Plaut replication on our specific model set); run pilot on 100 MMLU items × 1 model pair to confirm extraction pipeline
2. **Resource Allocation:** Allocate 7 weeks for critical path; reserve 1 week buffer for HuggingFace model download delays
3. **Failure Management:** Document all null results explicitly; maintain bootstrap CIs for H-M4 regardless of outcome

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (ID: H-MarginFlip-v1, schema: v10.0.0)
- Gap ID: gap-1 — "No Systematic Study of H2 Boundary-Shift Severity as Predictable Function of Pre-Alignment Model Properties"

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (ClearThought scientific method ×2, structured argumentation ×1, Archon pipeline ×1)
- Tools: scientificmethod (2x: H-E1 + H-M integrated), structuredargumentation (1x: dialectical analysis)

---

*Generated by YouRA Phase 2B (v6.0 Compact) | 2026-03-17*
