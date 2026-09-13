# Verification Plan: RLHF Alignment vs. Calibration Trade-off in LLMs

**Date:** 2026-03-14
**Hypothesis ID:** H-AlignCalib-v1
**Confidence:** 0.78
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under conditions where instruction-tuned LLMs (SFT, PPO, DPO) are compared to their pretrained
base counterparts using forced-choice evaluation (lm-eval log-probability continuation on MMLU,
TruthfulQA MC1, HellaSwag), if alignment training increases with reward-optimization pressure
(SFT < DPO < PPO), then the Brier reliability component of Expected Calibration Error will
increase monotonically in the same order (PPO >= DPO > SFT), because alignment objectives
systematically perturb logit distributions — either via monotonic scale inflation (H1),
decision-boundary restructuring (H2), or framing-susceptibility induction (H3) — and these
mechanisms are empirically discriminable via pre-specified logit-space tests.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in Brier reliability (overconfidence component of ECE) between
instruction-tuned aligned models and their base counterparts, and no consistent ordering
PPO >= DPO > SFT in ΔReliability across model families and benchmarks.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MMLU (standard) | 57 subjects × ~14k questions; log-prob continuation scoring; native lm-eval v0.4.11 support |
| **Model** | Pythia alignment ladder (1.4B/2.8B/6.9B SFT/DPO/PPO) | Identical pretraining across all alignment variants; cleanest causal isolation |

**Dataset Details:**
- Source: HuggingFace datasets — cais/mmlu
- Path: lm-eval-harness: --tasks mmlu

**Model Details:**
- Type: autoregressive_causal_lm
- Source: EleutherAI/pythia-{1.4b|2.8b|6.9b}, aligned variants from Li et al. 2024 (HuggingFace)

**Secondary Datasets:** TruthfulQA MC1 (--tasks truthfulqa_mc1), HellaSwag (--tasks hellaswag)

**Secondary Models:** LLaMA-2 7B/13B (SFT+RLHF/PPO), Mistral 7B Instruct v0.1 (SFT-only), Falcon 7B Instruct (SFT-only, sensitivity check)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Base model ECE (Pythia pretrained) | Well-calibrated per Xie et al. 2024 | MMLU, TruthfulQA MC1, HellaSwag |
| LLaMA-2-Chat (Xie et al. 2024) | ECE=0.298 (MMLU), 0.507 (TruthfulQA) | MMLU, TruthfulQA, TriviaQA |
| Li et al. 2024 Pythia SFT/PPO/DPO | ~25% truthfulness drop (not ECE) | BBQ, AdvGLUE, ETHICS, ConfAIde |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pythia SFT/PPO/DPO HuggingFace checkpoints faithfully represent Li et al. 2024 alignment stages | Li et al. 2024 cites EleutherAI Pythia; public model cards | Causal ladder breaks; within-family comparison invalidated |
| A2 | lm-eval log-prob continuation scoring is fair across base and aligned models | Both accept continuation-style prompts; lm-eval v0.4.11 standard | ΔECE may reflect format mismatch, not alignment |
| A3 | Brier reliability correctly measures overconfidence independent of resolution changes | Standard Brier decomposition (Murphy 1973) | ECE changes cannot distinguish overconfidence from discriminability collapse |
| A4 | Softmax-normalized 4-option probs reflect epistemic uncertainty | Guo et al. 2017, Xie et al. 2024 standard approach | Softmax normalization may inflate apparent overconfidence; pre-softmax margin is diagnostic control |
| A5 | PPO rewards do not explicitly penalize overconfidence | Coste et al. 2023; standard Anthropic HH reward model | PPO may not show greater ΔReliability than SFT |

### 1.6 Research Gap & Novelty

First systematic paired base/aligned ECE comparison across multiple model families AND alignment methods,
with mechanistic decomposition using Brier reliability/resolution and logit-space diagnostics (rank
correlation, margin analysis, shared/changed prediction split). Tests *which mechanism* dominates
(scale, boundary shift, or framing susceptibility) with distinct falsifiable predictions per mechanism.
The alignment-method gradient (PPO >= DPO > SFT in ΔReliability) is a novel contribution with theoretical
grounding in reward optimization theory, and ATS as a mechanistic diagnostic probe.

**Scope reduction from Phase 2A Established Facts:** 43% — 5 of 8 claims are BUILD_ON (pre-validated);
only 3 PROVE_NEW claims require Phase 2B-4 verification.

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
**H-E1: Alignment Training Increases Brier Reliability (Existence)**

**Statement**: Under forced-choice evaluation (lm-eval log-prob continuation on MMLU), if alignment training is applied (SFT, DPO, PPO) to Pythia base models, then ΔECE > 0 and ΔBrier reliability > 0 with bootstrap 95% CI lower > 0 for at least one alignment method (PPO or DPO) in at least 2/3 Pythia model sizes.

**Rationale** (2-3 sentences):
This is the foundational existence test — verifying that alignment training measurably degrades calibration beyond what is observed in paired pretrained base models. Without this, the mechanistic sub-hypotheses (H-M1 through H-M4) have no empirical grounding. The 43% scope reduction from Phase 2A means this claim is already well-motivated but not yet systematically verified in a multi-family, multi-alignment-method design.

**Variables** (from Phase 2A):
- Independent: Alignment method (SFT, DPO, PPO)
- Dependent: ΔBrier reliability (aligned minus base), ΔECE
- Controlled: Base pretraining checkpoint (Pythia family), evaluation format (lm-eval v0.4.11), benchmark items

**Verification Protocol** (3-5 steps):
1. Run lm-eval v0.4.11 on all 9 Pythia checkpoints (3 sizes × 3 alignment) on full MMLU (~14k items).
2. Extract per-item 4-option log-prob vectors; compute 15-bin equal-width ECE and Brier decomposition (reliability, resolution).
3. Compute ΔBrier_reliability = reliability_aligned − reliability_base for each of 9 aligned-base pairs.
4. Bootstrap 95% CI (n=1000) for each ΔECE; run paired Wilcoxon signed-rank test across model sizes.
5. Test gradient ordering: ΔReliability_PPO >= ΔReliability_DPO > ΔReliability_SFT (sign test across 3 sizes).

**Success Criteria** (PoC: Direction-based):
- Primary: ΔBrier reliability > 0 for PPO or DPO with bootstrap CI lower bound > 0, in ≥2/3 Pythia sizes
- Secondary: ΔECE > 0 in at least 2/3 benchmarks for PPO condition

**Failure Response**:
- IF fails: STOP — reassess entire hypothesis H-AlignCalib-v1; alignment may not drive calibration degradation in this model family

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (sh1_existence), Section 1.6 Prediction P1

---

---
**H-M1: Base Pretrained Models Are Well-Calibrated**

**Statement**: Under greedy-decoded log-probability evaluation on MMLU, Pythia base models (1.4B, 2.8B, 6.9B) show ECE < 0.15 before any alignment training, confirming that pretraining yields naturally calibrated logit distributions as the causal baseline for alignment-induced shifts.

**Rationale** (2-3 sentences):
This hypothesis establishes the "Causal Step 1" of the mechanism: that base pretraining yields calibrated outputs from which alignment deviates. If base models are already miscalibrated, alignment-induced ΔECE cannot be attributed to alignment alone. This is a BUILD_ON claim per Phase 2A but requires explicit quantitative confirmation for mechanistic validity in this specific model family.

**Variables** (from Phase 2A):
- Independent: Pretraining stage (base vs aligned)
- Dependent: ECE_base (expected < 0.15 per Xie et al. 2024)
- Controlled: Same MMLU items, lm-eval v0.4.11, greedy decoding

**Verification Protocol** (3-5 steps):
1. Extract ECE_base from the same lm-eval runs used for H-E1 (no additional compute required).
2. Compute 15-bin equal-width ECE for each Pythia base model on MMLU.
3. Verify ECE_base < 0.15 for all 3 sizes; report per-size values.
4. Compare ECE_base vs ECE_SFT as the minimal alignment-induced shift.
5. Document if base ECE is systematically below the aligned variants for all sizes.

**Success Criteria** (PoC: Direction-based):
- Primary: ECE_base < 0.15 for all 3 Pythia sizes on MMLU
- Secondary: ECE_base < ECE_SFT for all 3 sizes

**Failure Response**:
- IF fails: EXPLORE — investigate whether pretraining data characteristics cause miscalibration; document as scope limitation

**Dependencies**: H-E1 (existence of alignment-induced ECE increase must be confirmed first)

**Source**: Phase 2A Section 1.3 Causal Step 1, evidence: Xie et al. 2024

---

---
**H-M2: Alignment Shifts Logit Distributions Toward Higher Confidence**

**Statement**: Under forced-choice MMLU evaluation, alignment training (SFT/DPO/PPO) increases mean pre-softmax logit margins (top-1 minus top-2 log-prob before normalization) relative to base models, with margin inflation ordered PPO >= DPO > SFT across Pythia model sizes, operationalizing the confidence inflation causal mechanism.

**Rationale** (2-3 sentences):
This is Causal Step 2: alignment objectives (PPO reward maximization with KL penalty; DPO preference likelihood reshaping) incentivize logit distributions that appear more certain. Measuring pre-softmax margins directly tests whether the mechanism operates at the logit level rather than as a post-hoc normalization artifact (addressing A4 assumption). Margin inflation distinguishes genuine confidence shift from softmax compression effects.

**Variables** (from Phase 2A):
- Independent: Alignment method (SFT, DPO, PPO), model size (1.4B, 2.8B, 6.9B)
- Dependent: Pre-softmax margin inflation = mean(top-1 logit − top-2 logit), aligned minus base
- Controlled: Same MMLU items; log-prob outputs from lm-eval v0.4.11 evaluation

**Verification Protocol** (3-5 steps):
1. Extract pre-softmax log-prob vectors from lm-eval outputs (same run as H-E1/H-M1).
2. Compute per-item margin = logit_rank1 − logit_rank2 for each of 4 options.
3. Compute mean margin per model; compute Δmargin = margin_aligned − margin_base.
4. Test gradient ordering PPO >= DPO > SFT via paired Wilcoxon across 3 Pythia sizes.
5. Report mean Δmargin with 95% CI per alignment method; verify sign is positive for PPO.

**Success Criteria** (PoC: Direction-based):
- Primary: Δmargin > 0 for PPO in ≥2/3 Pythia sizes (bootstrap CI lower > 0)
- Secondary: Ordering Δmargin_PPO >= Δmargin_DPO > Δmargin_SFT confirmed in sign test

**Failure Response**:
- IF fails: EXPLORE — test whether alignment acts post-softmax (normalization artifact); document as H2 (boundary shift) candidate

**Dependencies**: H-M1 (base calibration confirmed)

**Source**: Phase 2A Section 1.3 Causal Step 2; evidence: Li et al. 2024 PPO objective, Coste et al. 2023

---

---
**H-M3: Mechanism Discrimination — H1 (Scale Distortion) vs H2 (Boundary Shift) vs H3 (Framing)**

**Statement**: The dominant alignment-induced logit perturbation mechanism is H1 (monotonic scale distortion): Spearman rank correlation between base and aligned 4-option log-prob vectors is ≥0.9 (preserving rank order), and the Brier reliability increase is concentrated in shared-argmax items (pure confidence inflation), not changed-argmax items (accuracy collapse). H2 (boundary shift) is diagnosed if ρ < 0.85; H3 (framing susceptibility) is diagnosed via TruthfulQA MC1 alignment × distractor interaction.

**Rationale** (2-3 sentences):
This is Causal Step 3: discriminating between three mechanistically distinct explanations for calibration degradation. Each has a distinct pre-registered falsifier: H1 fails if ρ < 0.8; H2 fails if reliability equally degrades in shared/changed-prediction subsets; H3 fails if distractor effects are uniform across alignment methods. The mechanism discrimination determines both the theoretical contribution and the scope of ATS effectiveness.

**Variables** (from Phase 2A):
- Independent: Alignment method, argmax consistency partition (shared vs changed argmax)
- Dependent: Spearman ρ (base vs aligned 4-option log-prob vectors), Brier reliability per subset, TruthfulQA × distractor interaction
- Controlled: Same MMLU items, identical log-prob evaluation

**Verification Protocol** (3-5 steps):
1. For each MMLU item, compute Spearman ρ over the 4-option log-prob vector between base and aligned model.
2. Partition items into shared-argmax (same top-1 option) and changed-argmax subsets.
3. Compute Brier reliability separately for shared-argmax and changed-argmax subsets per alignment method.
4. Test if shared-argmax reliability degradation is significant (Cohen's d ≥ 0.1) — H1 signature.
5. On TruthfulQA MC1: test alignment × alternative-hypothesis presentation interaction on ECE.

**Success Criteria** (PoC: Direction-based):
- Primary: Mean ρ ≥ 0.9 for all alignment methods (H1: scale distortion consistent)
- Secondary: Brier reliability increases in shared-argmax subset, Cohen's d ≥ 0.1 for PPO

**Failure Response**:
- IF ρ < 0.85: Document H2 (boundary restructuring) as the dominant mechanism; update ATS applicability
- IF neither H1/H2: Test H3 framing as fallback explanation; EXPLORE alternative calibration interventions

**Dependencies**: H-M2 (margin inflation mechanism established)

**Source**: Phase 2A Section 1.3 Causal Step 3; evidence: ATS [Xie 2024], Chhikara et al. 2025

---

---
**H-M4: Net Effect — Brier Reliability Gradient PPO>=DPO>SFT and ATS Correction**

**Statement**: The net effect of alignment on Brier reliability follows the gradient PPO >= DPO > SFT across Pythia model sizes and MMLU subjects, consistent with reward optimization pressure magnitude. ATS post-hoc correction reduces ECE by ≥50% for aligned models, confirming the distortion is encoded in hidden state representations (mechanism is correctable without retraining).

**Rationale** (2-3 sentences):
This is Causal Step 4: the quantitative prediction of the full causal chain. The ordering PPO >= DPO > SFT is the primary falsifiable claim of H-AlignCalib-v1, grounded in the reward optimization pressure gradient. ATS correction ≥50% provides independent mechanistic confirmation that the calibration distortion follows a hidden-state pattern — if ATS fails to correct, the mechanism may be architectural rather than representational.

**Variables** (from Phase 2A):
- Independent: Alignment method (SFT, DPO, PPO), model size (1.4B, 2.8B, 6.9B)
- Dependent: ΔBrier reliability gradient across alignment methods; post-ATS ECE reduction percentage
- Controlled: Same MMLU evaluation; ATS pretrained weights from Xie et al. 2024 repository

**Verification Protocol** (3-5 steps):
1. From H-E1 results: extract ΔBrier_reliability per alignment method per Pythia size.
2. Sign test for ordering ΔReliability_PPO >= ΔReliability_DPO > ΔReliability_SFT across 3 sizes.
3. Apply pretrained ATS model (from Xie et al. 2024 code) to each aligned Pythia model on MMLU.
4. Compute post-ATS ECE and compare to pre-ATS; report % reduction and bootstrap CI.
5. Verify ATS reduction ≥50% for PPO models; report per-size ATS effectiveness.

**Success Criteria** (PoC: Direction-based):
- Primary: ΔReliability ordering PPO >= DPO > SFT in ≥2/3 Pythia sizes (sign test)
- Secondary: ATS reduces ECE by ≥50% for PPO models on MMLU (directional confirmation of representational encoding)

**Failure Response**:
- IF gradient fails: PIVOT — document partial gradient (e.g., PPO > SFT but not DPO > SFT); report as nuanced finding
- IF ATS correction fails: EXPLORE — distortion may be architectural (weight-level), not hidden-state-encoded

**Dependencies**: H-M3 (mechanism type identified)

**Source**: Phase 2A Section 1.3 Causal Step 4; evidence: Xie et al. 2024 ATS results, Li et al. 2024 PPO/DPO experiments

---

---

## 3. Risk Analysis

### 3.1 Assumption-to-Risk Mapping

| Risk | Source | Description | Severity | Affected |
|------|--------|-------------|----------|---------|
| R1 | A1 | Pythia alignment checkpoints don't match Li et al. 2024 stages | High | H-E1, H-M1, H-M2, H-M4 |
| R2 | A2 | lm-eval log-prob scoring is out-of-distribution for chat models | High | H-E1, H-M2, H-M3 |
| R3 | A3 | Brier reliability conflates overconfidence with resolution collapse | Critical | H-E1, H-M3, H-M4 |
| R4 | A4 | Softmax normalization inflates apparent overconfidence | Medium | H-M2, H-M3 |
| R5 | A5 | PPO reward penalizes overconfidence, dampening gradient | Medium | H-M4 |

**Critical: 1 | High: 2 | Medium: 2 | Low: 0**

### 3.2 Mitigation Strategies

**Risk R1: Checkpoint Fidelity**
- **Source Assumption:** A1 — Pythia checkpoints faithfully represent Li et al. 2024
- **Affected:** H-E1, H-M1, H-M2, H-M4
- **Severity:** High
- **Mitigation:**
  1. Prevention: Verify model cards and Li et al. 2024 Appendix B for exact HuggingFace checkpoint IDs before evaluation
  2. Detection: Cross-check model performance on Li et al.'s own benchmark tasks (BBQ, AdvGLUE)
  3. Response: PIVOT to LLaMA-2 family as primary causal chain; document Pythia checkpoint discrepancy

**Risk R2: Format Mismatch**
- **Source Assumption:** A2 — log-prob continuation is fair for chat models
- **Affected:** H-E1, H-M2, H-M3
- **Severity:** High
- **Mitigation:**
  1. Prevention: Run pilot evaluation on Pythia 1.4B base vs SFT; verify ΔECE direction before full evaluation
  2. Detection: If ΔECE is negative for SFT (better calibration than base), format mismatch is the likely cause
  3. Response: SCOPE — restrict to base vs SFT comparison; exclude DPO/PPO if format mismatch is severe

**Risk R3: Brier Decomposition Confound (CRITICAL)**
- **Source Assumption:** A3 — Brier reliability correctly measures overconfidence
- **Affected:** H-E1, H-M3, H-M4 (core mechanistic interpretation)
- **Severity:** Critical
- **Mitigation:**
  1. Prevention: Always compute Brier resolution alongside reliability; report both
  2. Detection: If ΔECE increases while ΔResolution also increases (accuracy collapse), decompose is confounded
  3. Response: Use shared-argmax partition (H-M3) to isolate confidence inflation from accuracy collapse; this is the primary diagnostic control

**Risk R4: Softmax Normalization Artifact**
- **Source Assumption:** A4 — softmax reflects epistemic uncertainty
- **Affected:** H-M2, H-M3
- **Severity:** Medium
- **Mitigation:**
  1. Prevention: Always run pre-softmax margin analysis alongside ECE computation
  2. Detection: If pre-softmax margins don't inflate while ECE increases, softmax artifact is likely
  3. Response: EXPLORE — report pre-softmax margins as primary evidence; reframe H-M2 around margin analysis

**Risk R5: PPO Reward Self-Regulation**
- **Source Assumption:** A5 — PPO does not penalize overconfidence
- **Affected:** H-M4 (gradient ordering)
- **Severity:** Medium
- **Mitigation:**
  1. Prevention: Review Li et al. 2024 reward model specifications before experiment
  2. Detection: If ΔReliability_PPO ≈ ΔReliability_DPO, reward self-regulation is a candidate explanation
  3. Response: PIVOT — document as "attenuation effect"; report DPO > SFT ordering as primary finding

### 3.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Primary Mitigation |
|----|------|--------|----------|----------|--------------------|
| R1 | Checkpoint fidelity | A1 | High | H-E1, H-M1, H-M2, H-M4 | Verify model cards; pivot to LLaMA-2 |
| R2 | Format mismatch | A2 | High | H-E1, H-M2, H-M3 | Pilot eval; scope to SFT-only if needed |
| R3 | Brier confound | A3 | Critical | H-E1, H-M3, H-M4 | Brier decomposition + shared-argmax partition |
| R4 | Softmax artifact | A4 | Medium | H-M2, H-M3 | Pre-softmax margin analysis |
| R5 | PPO self-regulation | A5 | Medium | H-M4 | Review reward model specs |

---

## 4. Execution Structure

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root]
    H-E1 (Existence — no dependencies)
    MUST_WORK: Alignment increases Brier reliability on MMLU
         │
         ▼
[Level 1 — Mechanism Foundation]
    H-M1 ← H-E1
    MUST_WORK: Base models are well-calibrated (ECE < 0.15)
         │
         ▼
[Level 2 — Confidence Shift]
    H-M2 ← H-M1
    SHOULD_WORK: Alignment inflates pre-softmax margins PPO>=DPO>SFT
         │
         ▼
[Level 3 — Mechanism Discrimination]
    H-M3 ← H-M2
    SHOULD_WORK: H1 scale distortion dominates (ρ≥0.9, shared-argmax inflation)
         │
         ▼
[Level 4 — Net Causal Effect]
    H-M4 ← H-M3
    SHOULD_WORK: ΔReliability gradient PPO>=DPO>SFT; ATS corrects ≥50%
         │
         ▼
[Phase 5 — Baseline Comparison — DEFERRED]
    H-CP (Cross-family generalization): LLaMA-2/Mistral/Falcon → Phase 5

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 4.3 Verification Phases with Gate Conditions

**Phase 1 — Foundation (2 weeks)**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | ΔECE > 0 with bootstrap CI lower > 0 for PPO/DPO in ≥2/3 Pythia sizes | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, reassess H-AlignCalib-v1 entirely.

**Phase 2 — Core Mechanisms (4 weeks)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK |
| H-M2 | H-M1 | SHOULD_WORK |
| H-M3 | H-M2 | SHOULD_WORK |
| H-M4 | H-M3 | SHOULD_WORK |

→ **Gate 2**: H-M1 must pass (base calibration confirmed). H-M2 through H-M4 failures narrow mechanistic claims but do not invalidate.

### 4.4 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  H-M4           │         │         │         │   ████  │
  [Gate 2]       │         │         │         │        ◆│
─────────────────┴─────────┴─────────┴─────────┴─────────┘
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════

Note: H-M2, H-M3, H-M4 reuse the same lm-eval evaluation run as H-E1.
Parallelization opportunity: all 5 hypotheses can be evaluated in 1-2
computational runs; the "week" units represent analysis/writing phases.
```

**Critical Path Analysis:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
  Formula: 2 (H-E1) + 4 (H-M1 through H-M4)
Compute Note: Single lm-eval run (~9 models × 3 benchmarks) covers all hypotheses.
Slack Available: 0 weeks (all sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Resource Summary:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (none required)

Verification Phases: 2
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1 to H-M4): 4 weeks

Total Duration: 6 weeks
Critical Path: 6 weeks
Execution Mode: Sequential analysis chain; parallelized compute
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Execution Order:**
1. Execute lm-eval evaluation for all 9 Pythia checkpoints on MMLU, TruthfulQA MC1, HellaSwag (parallel compute) — Week 1
2. Run Brier decomposition and ECE analysis → H-E1 evaluation — Week 2
3. Evaluate Gate 1 → If pass, proceed
4. Extract base ECE → H-M1 evaluation — Week 3
5. Compute pre-softmax margins → H-M2 evaluation — Week 4 (same data)
6. Compute Spearman ρ + shared/changed-argmax Brier split → H-M3 evaluation — Week 5
7. Run ATS correction + gradient sign test → H-M4 evaluation — Week 6
8. Evaluate Gate 2 → Proceed to Phase 2C experiment design

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Alignment training (SFT < DPO < PPO) monotonically increases Brier reliability (overconfidence), empirically discriminable via logit-space diagnostics.

**Supporting Evidence:**
1. Xie et al. 2024: ATS corrects ECE by 58-82%, implying systematic logit distortion from alignment
2. Coste et al. 2023: PPO reward hacking inflates confidence via proxy reward exploitation
3. Li et al. 2024: PPO/DPO show ~25% truthfulness degradation on Pythia ladder — same models, same checkpoints

**Strengths:**
- Clear causal mechanism with 4 testable steps
- Pre-registered mechanism discrimination (H1/H2/H3) with distinct falsifiers
- Multiple converging evidence sources across independent papers

**Expected Outcomes:**
- Primary: ΔBrier reliability > 0 in PPO/DPO with CI lower > 0, gradient PPO>=DPO>SFT
- Secondary: Shared-argmax reliability inflation (Cohen's d ≥ 0.1) for PPO
- Tertiary: ρ ≥ 0.9 confirming H1 scale distortion mechanism

### 5.2 Antithesis

**Null Hypothesis (H0):** No significant Brier reliability increase under alignment; no PPO>=DPO>SFT ordering.

**Counter-Arguments:**
1. Accuracy collapse explanation: Li et al. 2024 shows ~25% truthfulness drop for PPO/DPO; ECE could increase from resolution collapse (lower discriminability), not overconfidence
2. Format mismatch: Chat models evaluated via continuation prompts (not chat-template) may show format-induced calibration artifacts unrelated to alignment
3. Softmax normalization artifact: 4-option softmax normalization concentrates probability on fewer options, inflating apparent ECE even without logit-level changes

**Potential Failure Points:**
- R3 (Critical): Brier reliability increase is actually resolution collapse from accuracy degradation
- R2 (High): Format mismatch dominates ΔECE signal over alignment mechanism
- R1 (High): Checkpoint mismatch invalidates causal chain interpretation

**Conditions Under Which H0 Would Be Supported:**
- ΔECE ≤ 0 for all alignment methods or ΔReliability not significantly > 0
- Shared-argmax reliability does NOT increase (accuracy collapse is driver, not confidence inflation)
- Gradient ordering fails: DPO ≥ PPO or SFT ≥ DPO

### 5.3 Synthesis

The thesis presents a testable multi-hypothesis mechanistic claim with converging support from 3 independent papers. The antithesis raises one critical methodological concern — the accuracy-calibration confound — that is directly addressed by the design.

**Resolution Path:**

The verification plan resolves the dialectic through:
1. **Foundation verification (H-E1):** Establishes ΔECE > 0 existence before mechanism attribution
2. **Shared-argmax partition (H-M3):** Isolates confidence inflation from accuracy collapse by restricting to items where base and aligned models agree on the answer
3. **Pre-softmax margin analysis (H-M2):** Tests logit-level mechanism directly, bypassing softmax normalization artifact
4. **Brier decomposition (all steps):** Always reports reliability AND resolution separately

**Conditions for Thesis Support:**
- H-E1 MUST_WORK gate passes: ΔBrier reliability > 0 with CI lower > 0
- Shared-argmax reliability inflates in H-M3 (Cohen's d ≥ 0.1) — accuracy collapse ruled out
- Gradient PPO >= DPO > SFT confirmed by sign test in H-M4

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1-4 all pass → Thesis validated with mechanism identified
2. **Partial Support (H1 only):** H-E1 + H-M1-2 pass; H-M3 shows H2 instead of H1 → Refined thesis: boundary shift dominates
3. **Partial Support (existence only):** H-E1 passes; H-M gradient fails → Alignment degrades calibration but ordering not monotonic with reward pressure
4. **No Support:** H-E1 fails → Antithesis supported; accuracy collapse or format mismatch is the actual driver

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | ΔECE > 0 under alignment | Accuracy collapse inflates ECE | H-E1 + shared-argmax partition |
| Mechanism | H1 scale distortion (ρ≥0.9) | H2 boundary restructuring (ρ<0.85) | H-M3 Spearman rho test |
| Gradient | PPO >= DPO > SFT in ΔReliability | Reward self-regulation flattens gradient | H-M4 sign test + ATS diagnostic |
| Scope | Holds across Pythia 1.4B-6.9B | Scale sensitivity (small vs 7B+ models) | Phase 5 cross-family validation |

**Overall Robustness Score:** High — three independent diagnostic controls address the three main threats to internal validity

**Confidence in Verification Plan:** 0.78

---

## 6. Summary & Conclusions

### 6.1 Executive Summary

**Main Hypothesis:** Alignment training (SFT<DPO<PPO) monotonically increases Brier reliability (overconfidence), empirically discriminable via logit-space tests.
- ID: H-AlignCalib-v1 | Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (43% scope reduction from Established Facts)
- Sub-Hypotheses: 5 total — H-E1 (Existence) + H-M1-4 (4-step causal chain)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Foundation + Mechanisms)
- Compute: Single lm-eval run covers all hypotheses; parallelization opportunity

**Risk Assessment:** High (1 Critical, 2 High risks) — mitigated by shared-argmax partition and Brier decomposition

**Immediate Action:** Begin Phase 1 with H-E1 (lm-eval evaluation of all 9 Pythia checkpoints on MMLU)

### 6.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases
- H0 addressed: No significant Brier reliability difference or PPO>=DPO>SFT ordering
- Pre-registered mechanism discrimination framework (H1/H2/H3) with distinct falsifiers

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: ΔECE > 0, ΔBrier reliability > 0, bootstrap CI lower > 0 for PPO/DPO in ≥2/3 Pythia sizes
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: ECE_base < 0.15 for Pythia 1.4B/2.8B/6.9B (Causal Step 1 confirmation)
- H-M2: Pre-softmax margin inflation PPO>=DPO>SFT (Causal Step 2 — confidence inflation)
- H-M3: Spearman ρ ≥ 0.9, shared-argmax Brier inflation (Causal Step 3 — H1 scale distortion)
- H-M4: ΔReliability gradient + ATS correction ≥50% (Causal Step 4 — net causal effect)
- Gate 2: H-M1 must pass

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess entire H-AlignCalib-v1
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → EXPLORE base calibration; document as scope limitation
   - H-M2/M3/M4 OPTIONAL FAIL → Document as mechanistic limitation; narrow thesis

**Open Questions:**
- Do Mistral-7B-Instruct and Falcon-7B-Instruct (SFT-only) show comparable ΔECE magnitude to Pythia-PPO, or significantly less?
- Does the distractor-augmented calibration test (H3 framing susceptibility) require standard prompts or modified lm-eval harness?
- Is Falcon-7B-Instruct training data heterogeneity severe enough to exclude from primary analysis?
- What pre-softmax margin threshold distinguishes 'logit scale inflation' from 'natural accuracy improvement' cases?

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (lm-eval evaluation of 9 Pythia checkpoints)
   - Set up Brier decomposition pipeline before evaluation

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path
   - Single GPU sufficient for lm-eval (inference-only); reserve compute for 9 model × 3 benchmark evaluations
   - Reserve buffer for ATS application (H-M4) if ATS code requires additional setup

3. **Failure Management:**
   - Document all gate failures with specific metrics
   - Execute PIVOT strategies per hypothesis failure response
   - Use shared-argmax partition as primary diagnostic if H-E1 signal is ambiguous

### 6.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/20260315_buildingtrust/03_refinement.yaml (ID: H-AlignCalib-v1)
- Schema version: 10.0.0 | Generated: 2026-03-14 | Convergence: 16 exchanges, all 6 personas

**B. MCP Tool Usage Summary**
- Total MCP calls: 3 (scientificmethod)
- Tools: mcp__clearThought__scientificmethod (3x) — H-E1 verification, H-M1-M2 chain, H-M3-M4 discrimination
- Established Facts skipped (BUILD_ON): 5 of 8 claims (43% scope reduction)

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-14*
