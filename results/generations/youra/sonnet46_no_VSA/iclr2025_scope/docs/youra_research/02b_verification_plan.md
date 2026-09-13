---
hypothesis_title: "Task-Type × Conversion-Strategy Interaction in Sub-Quadratic Transformer Conversion (H-Conv1D-v1)"
hypothesis_id: "H-Conv1D-v1"
confidence_level: 0.78
total_hypothesis_count: 4
date: "2026-08-03"
workflow: "phase2b-planning"
research_mode: "incremental"
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-08-03T13:15:00Z"
pipeline_project_id: "218d7ff4-2555-4582-b35d-36d95fb2f5c1"
phase2b_task_id: "96f981d4-4b1f-40c6-b6c8-b1f3e80447cf"
phase2c_task_id: "4d15d059-b0e5-43ed-911e-b05383ef05cf"
---

# Verification Plan: Task-Type × Conversion-Strategy Interaction in Sub-Quadratic Transformer Conversion (H-Conv1D-v1)

**Date:** 2026-08-03
**Hypothesis ID:** H-Conv1D-v1
**Confidence:** 0.78
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under fixed-budget (≤1B tokens) short-context distillation of LLaMA-3-8B,
if we compare MOHAWK-SSM conversion versus LAWCAT-linear-attention conversion
on LongBench v2 task categories,
then MOHAWK-SSM will exhibit ≥2× larger normalized accuracy degradation on
retrieval-heavy categories (multi-doc QA, synthetic) compared to generation-heavy
categories (summarization, few-shot), while LAWCAT will exhibit a significantly
more uniform profile across categories,
because MOHAWK-SSM compresses context into bounded state vectors losing exact
needle-token addresses, whereas LAWCAT's causal Conv1D preserves local
token-to-token attention enabling shallower retrieval degradation.

### 1.2 Alternative Hypothesis (H0)

There is no significant task-type × conversion-strategy interaction on LongBench v2
normalized accuracy: degradation is uniform across categories for both MOHAWK-SSM
and LAWCAT-linear-attention conversions of LLaMA-3-8B.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench v2 (standard) | 503 questions across 6 task categories (single-doc QA, multi-doc QA, summarization, few-shot, synthetic, code) at 8k–2M context. Provides the task-category contrast needed for the interaction test. Official benchmark with established baselines. |
| **Model** | LLaMA-3-8B (Meta) | Fixed base model for all conversions — eliminates capability confound (H-E1 lesson). 8B scale representative of production-relevant models. MOHAWK and LAWCAT both have demonstrated pipelines at 7-8B scale. |

**Dataset Details:**
- Source: THUDM/LongBench
- Path: https://github.com/THUDM/LongBench

**Model Details:**
- Type: Decoder-only transformer, 8B parameters
- Source: meta-llama/Llama-3-8B on HuggingFace

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| MOHAWK Phi-Mamba (Phi-1.5 → Mamba) | Strong retention on lm-eval short-context tasks; no LongBench v2 data | lm-eval standard; perplexity on WT-103/Pile |
| LAWCAT Mistral-7B → linear attention | >90% passkey retrieval at 22K tokens; competitive S-NIAH 1&2&3 | S-NIAH (synthetic), BABILong (synthetic QA), passkey retrieval |
| Overflow Prevention recurrent models (Falcon3-Mamba, RecurrentGemma, RWKV6) | Chunk-based inference competitive on most LongBench v2 categories; systematic degradation on multi-doc QA and synthetic | LongBench v2 (directly applicable as scratch-trained SSM baseline) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | MOHAWK matrix approximation quality at N=512 is representative of long-range (N≤8k) approximation quality (sub-linear error scaling) | MOHAWK Tables 6-7: SSD Frobenius error ≈0.097 at N=64/512; theoretical SSD expressivity analysis | Retrieval degradation attributable to approximation breakdown not architecture; hypothesis scope must be reframed |
| A2 | LAWCAT's causal Conv1D provides meaningful local attention within convolution window width | LAWCAT paper: depth-separable Conv1D enhances local dependency modeling; competitive S-NIAH retrieval | β_depth slopes identical for LAWCAT and MOHAWK; Conv1D mechanism does not differentiate retrieval profiles |
| A3 | LLaMA-3-8B distillation with ≤1B tokens achieves sufficient alignment (perplexity gap ≤5%, L2 ratio ≤0.15) | LAWCAT: <0.1% pre-training budget for Mistral-7B; MOHAWK: 3B tokens for 1.3B model; extrapolated | Results reflect undertrained student not architectural limits; more tokens required |
| A4 | LongBench v2's 6 task categories provide sufficient contrast between retrieval-heavy and generation-heavy tasks | LongBench v2 paper: 503 diverse questions with explicit task-category diversity; Overflow Prevention confirms patterns | Interaction test lacks statistical power; additional contrast measures needed |
| A5 | Hybrid-4 baseline using middle-layer attention retention is appropriate control for 'attention necessity' | MOHAWK Table 2: Hybrid-4 achieves 66.0 vs 67.2 teacher on general tasks | If only early or late layers matter, Hybrid-4's middle-layer choice is suboptimal; layer-localization ablation needed |

### 1.6 Research Gap & Novelty

**Gap:** No prior paper evaluates both MOHAWK-SSM and LAWCAT-linear-attention on the same LongBench v2 task-category splits with the same base model. MOHAWK uses Phi-1.5 on lm-eval; LAWCAT uses Mistral-7B on synthetic retrieval tasks only.

**Novelty:** First controlled factorial comparison of MOHAWK-SSM vs. LAWCAT-linear-attention conversion strategies on LongBench v2 with fixed base model (LLaMA-3-8B). Fixed base model enables pure within-subject measurement of conversion effect — no capability confound. Scope reduction: 57% of claims are established (BUILD_ON) — only 2 PROVE_NEW claims require hypothesis verification.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Task-Type × Strategy Interaction Existence**

**Type:** EXISTENCE
**Statement:** Under fixed-budget (≤1B tokens) short-context distillation of LLaMA-3-8B, a statistically significant task-type × conversion-strategy interaction exists on LongBench v2 normalized accuracy degradation (Δ_norm): MOHAWK-SSM exhibits ≥2× larger Δ_norm on retrieval-heavy categories (multi-doc QA, synthetic) than on generation-heavy categories (summarization, few-shot), while LAWCAT-linear-attention exhibits a significantly more uniform degradation profile.

**Rationale:**
This is the primary PROVE_NEW claim (Claim 6 in Phase 2A established facts). Prior work cannot answer this because MOHAWK and LAWCAT were evaluated on different base models and benchmarks. Fixed base model design (H-E1 lesson applied) eliminates capability confound.

**Variables (from Phase 2A):**
- Independent: Conversion Strategy (MOHAWK-SSM, LAWCAT, Hybrid-4) × Task Category (6 LongBench v2 categories)
- Dependent: Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher per category per strategy
- Controlled: Base model (LLaMA-3-8B fixed), distillation budget (≤1B tokens, C4, 2048-token max), LongBench v2 full 503-question set

**Verification Protocol (3-5 steps):**
1. Convert LLaMA-3-8B with MOHAWK Stage 1+2 (≤1B tokens C4) and LAWCAT (≤1B tokens C4) — enforce perplexity gate ≤5% and alignment ratio ≤0.15 before evaluation.
2. Evaluate all converted models (+ Hybrid-4 + teacher) on LongBench v2 full 503-question set with per-example accuracy logging.
3. Compute Δ_norm per category per strategy; fit mixed-effects model: Δ_norm ~ TaskType * Strategy + (1|Task).
4. Test interaction term significance (p<0.01, Holm correction) and bootstrap 95% CI for Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval).
5. Report ratio with CI; confirm statistical significance of task-type × strategy interaction.

**Success Criteria (PoC: Direction-based):**
- Primary: Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0 with 95% bootstrap CI strictly above 1.0
- Secondary: Interaction term p<0.01 after Holm correction in mixed-effects model

**Failure Response:**
- IF fails: PIVOT — investigate curriculum-length confound (mixed-length distillation ablation as alternative explanation); if still fails, reassess main hypothesis H-Conv1D-v1

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1 (sh1_existence), Prediction P1

---

---
**H-M1: SSM Bounded-State Frobenius Gate (Matrix Approximation Viability)**

**Type:** MECHANISM
**Statement:** Under MOHAWK Stage 1+2 conversion of LLaMA-3-8B with SSD structured mixer, the matrix approximation Frobenius error scales sub-linearly from N=512 to N=8k (log-log slope ≤0.5 and 90th percentile error ≤0.3 at N=8k), confirming that the SSD approximation quality established at short-context training is not catastrophically degraded at long-context inference — i.e., the mechanism operates via architectural bounded-state bias, not pure approximation breakdown.

**Rationale:**
This is Step 1 of the 3-step causal chain. If Frobenius error scales super-linearly, retrieval degradation is attributable to approximation breakdown (training artifact) rather than inherent SSM bounded-state limits — the key interpretive confound that must be ruled out before the architectural claim can stand.

**Variables (from Phase 2A):**
- Independent: Matrix type (SSD, Toeplitz) × sequence length N ∈ {512, 1k, 2k, 4k, 8k}
- Dependent: Frobenius error at each N; log-log slope of Frobenius error vs N
- Controlled: LLaMA-3-8B architecture; MOHAWK Stage 1 matrix fitting procedure

**Verification Protocol (3-5 steps):**
1. Run Day 0 gate check: fit MOHAWK SSD mixer to LLaMA-3-8B attention matrices at N ∈ {512, 1k, 2k, 4k, 8k} (<1 GPU-day).
2. Compute Frobenius error at each N; fit log-log regression to estimate scaling slope.
3. Check: slope ≤ 0.5 AND 90th percentile error ≤ 0.3 at N=8k.
4. If gate passes: interpret retrieval degradation as bounded-state architectural bias. If gate fails: abort — retrieval degradation is approximation breakdown, not architectural.
5. Record gate result as mechanistic evidence for H-M2 interpretation.

**Success Criteria (PoC: Direction-based):**
- Primary: Frobenius log-log slope ≤ 0.5 AND 90th pct error ≤ 0.3 at N=8k
- Secondary: SSD error < Toeplitz error at all N (replicates MOHAWK Table 6-7 finding)

**Failure Response:**
- IF fails: STOP — abort downstream distillation; reframe hypothesis as "approximation-quality failure under budget" not "architectural SSM bounded-state bias"; route to Phase 2A-Dialogue

**Dependencies:** None (runs in parallel with H-E1 Day 0; must pass before H-E1 downstream evaluation)

**Source:** Phase 2A Causal Step 1, Assumption A1

---

---
**H-M2: SSM Bounded-State Exponential Forgetting → Retrieval Depth-Slope**

**Type:** MECHANISM
**Statement:** MOHAWK-SSM converted LLaMA-3-8B exhibits a significantly steeper needle-depth accuracy degradation slope than LAWCAT-converted LLaMA-3-8B on LongBench v2 multi-doc QA and synthetic tasks, quantified as |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| in logistic regression of P(correct) ~ DepthPercentile + (1|Task), because SSM bounded-state exponential forgetting (h_t = A·h_{t-1} + B·x_t) loses exact positional identity of early tokens while LAWCAT's causal Conv1D preserves local token-to-token attention within a sliding window.

**Rationale:**
This is Step 2 of the causal chain — the mechanistic heart of H-Conv1D-v1. The depth-slope differential (P2 in Phase 2A) is the sharpest falsifier of the Conv1D mechanism claim. A positive result confirms that degradation is not uniformly distributed across needle positions but concentrated at greater depths, exactly as predicted by SSM forgetting dynamics.

**Variables (from Phase 2A):**
- Independent: Conversion Strategy (MOHAWK-SSM vs LAWCAT)
- Dependent: β_depth (logistic regression coefficient of accuracy on needle depth percentile), per-model
- Controlled: Evaluation subset (LongBench v2 multi-doc QA + synthetic, ~166 questions); base model (LLaMA-3-8B fixed)

**Verification Protocol (3-5 steps):**
1. From H-E1 evaluation run, extract per-example needle depth percentile for multi-doc QA and synthetic tasks (built into LongBench v2 per-example metadata).
2. Fit per-model logistic regression: P(correct) ~ DepthPercentile + (1|Task), separately for MOHAWK-SSM and LAWCAT.
3. Compute β_depth coefficients and 95% CIs for both models.
4. Test: |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| with non-overlapping 95% CIs; at least one β_depth significantly < 0 (p<0.01, Holm).
5. Report coefficient ratio with CI; assess Conv1D mechanism support.

**Success Criteria (PoC: Direction-based):**
- Primary: |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| with non-overlapping 95% CIs
- Secondary: β_depth^SSM significantly < 0 (p<0.01); β_depth^LAWCAT closer to 0

**Failure Response:**
- IF fails: EXPLORE — document as "Conv1D mechanism insufficient to differentiate depth-slope"; P2 fails but H-E1 interaction may still hold; narrow scope of main claim

**Dependencies:** H-M1 (Frobenius gate must pass to interpret depth-slope as architectural, not approximation-driven); H-E1 data collection provides the per-example depth metadata

**Source:** Phase 2A Causal Step 2, Prediction P2, Assumption A2

---

---
**H-M3: Generation-Heavy Task Tolerance → Asymmetric Degradation Profile**

**Type:** MECHANISM
**Statement:** MOHAWK-SSM converted LLaMA-3-8B shows significantly greater normalized degradation on retrieval-heavy categories (multi-doc QA, synthetic) than on generation-heavy categories (summarization, few-shot), while the within-strategy category contrast for LAWCAT is significantly smaller, because SSM state accumulation tolerates lossy semantic compression (summarization needs global semantics, few-shot needs local pattern copying) but fails exact positional retrieval (multi-doc QA, synthetic needles require address preservation).

**Rationale:**
This is Step 3 of the causal chain — explaining WHY the interaction pattern takes the specific 2×-threshold form. Generation tasks are structurally forgiving of bounded-state forgetting; retrieval tasks are not. Confirming this step completes the mechanistic explanation from architecture to task performance.

**Variables (from Phase 2A):**
- Independent: Task type (retrieval-heavy: multi-doc QA, synthetic vs generation-heavy: summarization, few-shot) × Conversion Strategy
- Dependent: Within-strategy category contrast ratio: Δ_norm^retrieval / Δ_norm^generation per strategy
- Controlled: Same LongBench v2 evaluation as H-E1; same LLaMA-3-8B base model

**Verification Protocol (3-5 steps):**
1. From H-E1 evaluation results, compute within-strategy category contrasts: Δ_norm^retrieval / Δ_norm^generation for MOHAWK-SSM and LAWCAT separately.
2. Test that MOHAWK-SSM contrast ratio ≥ 2.0 (confirms asymmetric degradation as predicted).
3. Test that LAWCAT contrast ratio is significantly closer to 1.0 than MOHAWK-SSM (confirms more uniform LAWCAT profile).
4. Fit mediation model: Acc_retrieval ~ Strategy + AlignmentRatio + PPL_gap + MatrixError to isolate architectural effect from training quality confound.
5. Confirm generation-heavy categories show ≤5% Δ_norm for MOHAWK-SSM (distinguishing from H-E1 which tests retrieval degradation magnitude).

**Success Criteria (PoC: Direction-based):**
- Primary: MOHAWK-SSM Δ_norm^retrieval / Δ_norm^generation ≥ 2.0; LAWCAT ratio significantly < MOHAWK ratio (non-overlapping CIs)
- Secondary: Mediation regression confirms architectural effect survives controlling for alignment quality and perplexity gap

**Failure Response:**
- IF fails: EXPLORE — if H-E1 still passes, the interaction exists but mechanism is not fully explained by this asymmetry model; document as partial support; narrow scope of main claim

**Dependencies:** H-M2 (depth-slope analysis provides mechanistic grounding for asymmetry claim); H-E1 provides the category-level Δ_norm data

**Source:** Phase 2A Causal Step 3, Prediction P1+P3

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-M1 ──┐
        ├──→ H-E1 ──→ H-M2 ──→ H-M3
(Day 0) │    (Data)   (Depth)  (Asymmetry)
        │
Note: H-M1 is a Day 0 gate check; if it passes, H-E1 distillation and evaluation proceed.
H-M2 and H-M3 use the same evaluation data as H-E1 (no additional runs needed).
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Δ_norm^SSM(retrieval)/Δ_norm^LAWCAT(retrieval) ≥ 2.0, CI above 1.0; interaction p<0.01 | STOP — reassess main hypothesis; route to Phase 2A-Dialogue |
| H-M1 | MUST_WORK | Frobenius log-log slope ≤ 0.5; 90th pct error ≤ 0.3 at N=8k | STOP — abort distillation; reframe as approximation-quality failure |
| H-M2 | SHOULD_WORK | \|β_depth^SSM\| ≥ 2× \|β_depth^LAWCAT\|, non-overlapping CIs | EXPLORE — narrow Conv1D mechanism claim; H-E1 may still hold |
| H-M3 | SHOULD_WORK | MOHAWK Δ_norm^retrieval/generation ≥ 2.0; LAWCAT ratio significantly smaller | EXPLORE — partial support; narrow scope of main claim |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation + Gate | H-M1 (Day 0 gate) + H-E1 distillation + evaluation | Weeks 1-4 (Day 0: 1 day; LAWCAT distillation: ~7 days; MOHAWK+Hybrid-4: ~6 days; Eval: ~2 days) |
| Phase 2: Mechanism Analysis | H-M2 + H-M3 (from H-E1 data) | Week 5 (statistical analysis only, no new training) |

**Total Duration:** ~5 weeks (14 GPU-days distillation + 1 GPU-day evaluation + analysis)

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Frobenius error scales super-linearly (slope > 0.5 at N=8k) | A1 | H-M1, H-M2 (interpretation), H-E1 (scope) | **Critical** |
| R2: Conv1D mechanism insufficient — β_depth slopes statistically indistinguishable | A2 | H-M2, P2 | **High** |
| R3: Alignment failure at ≤1B token budget (perplexity gap > 5% or L2 ratio > 0.15) | A3 | H-E1, H-M2, H-M3 | **High** |
| R4: LongBench v2 categories lack retrieval/generation contrast (insufficient statistical power) | A4 | H-E1, H-M3 | **Medium** |
| R5: Hybrid-4 middle-layer choice suboptimal — early/late layers matter more | A5 | H-M3 (attention necessity), P3 | **Medium** |

### 4.2 Mitigation Strategies

**Risk R1: Frobenius error super-linear scaling**
- Source Assumption: A1 — MOHAWK approximation quality at N=512 representative of N=8k
- Affected: H-M1 (direct test), H-M2 (interpretation), H-E1 (architectural claim scope)
- Severity: Critical
- Prevention: Day 0 gate check (< 1 GPU-day) before any distillation investment
- Detection: Log-log regression on Frobenius error at N ∈ {512, 1k, 2k, 4k, 8k}; abort criterion: slope > 0.5 OR 90th pct > 0.3 at N=8k
- Response: ABORT downstream distillation; reframe as "approximation-quality failure under short-context distillation budget" — still publishable contribution on conversion failure modes
- Early Warning: Frobenius slope already > 0.3 at N=4k during gate check

**Risk R2: Conv1D mechanism insufficient**
- Source Assumption: A2 — LAWCAT Conv1D provides meaningful local attention within convolution window
- Affected: H-M2 (primary), P2 (secondary prediction)
- Severity: High
- Prevention: H-E1 provides interaction evidence independent of H-M2; H-M2 failure narrows but does not invalidate H-E1
- Detection: β_depth coefficient comparison with bootstrap CIs; if CIs overlap, mechanism unsupported
- Response: EXPLORE — narrow main claim to "interaction exists but Conv1D mechanism is insufficient to explain depth-slope differential"; still publishable with H-E1 evidence
- Early Warning: β_depth^LAWCAT not significantly negative (p > 0.05) on multi-doc QA subset

**Risk R3: Alignment failure at ≤1B token budget**
- Source Assumption: A3 — 1B token budget sufficient for LLaMA-3-8B alignment
- Affected: H-E1, H-M2, H-M3 (all downstream)
- Severity: High
- Prevention: Pre-registered perplexity gate (≤5% relative gap) and alignment ratio gate (≤0.15) enforced before LongBench evaluation
- Detection: Perplexity monitoring during distillation; L2 hidden-state alignment ratio tracking
- Response: BUDGET EXPANSION — attempt 2B token budget (doubles compute); if still failing, reduce scope to Mistral-7B at same budget where LAWCAT is proven
- Early Warning: Perplexity gap > 3% at 500M token checkpoint; alignment ratio > 0.10 at midway

**Risk R4: Insufficient statistical power per category**
- Source Assumption: A4 — 503 questions sufficient contrast across categories
- Affected: H-E1 (interaction test), H-M3 (within-strategy contrast)
- Severity: Medium
- Prevention: Power analysis pre-check: ~83 questions per category gives ~70% power at α=0.01 for medium effect (d=0.5); acceptable
- Detection: Mixed-effects model confidence intervals; if interaction term CI is very wide, power was insufficient
- Response: SCOPE — report directional evidence; supplement with Overflow Prevention scratch-trained SSM results as convergent validity
- Early Warning: Per-category Δ_norm standard error > 0.05 in initial evaluation

**Risk R5: Hybrid-4 middle-layer choice suboptimal**
- Source Assumption: A5 — 4 middle attention layers are appropriate control for attention necessity
- Affected: H-M3 (P3 prediction), attention-necessity claim
- Severity: Medium
- Prevention: Hybrid-4 result is secondary/P3 — H-E1 and H-M2 are primary; Hybrid-4 failure does not invalidate main contribution
- Detection: If Hybrid-4 fully matches full MOHAWK on all categories, middle layers are sufficient (actually supports that attention locality matters)
- Response: EXPLORE — if Hybrid-4 matches full replacement, attribution shifts to "layer quantity matters, not type" — Phase 4 extension
- Early Warning: Hybrid-4 shows ≥8% Δ_norm on retrieval categories (approaching MOHAWK full replacement level)

### 4.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Frobenius super-linear scaling | A1 | **Critical** | H-M1, H-M2, H-E1 | Day 0 gate check; abort criterion pre-registered |
| R2 | Conv1D β_depth indistinguishable | A2 | **High** | H-M2 | EXPLORE narrow claim; H-E1 independent of H-M2 |
| R3 | Alignment failure at 1B budget | A3 | **High** | H-E1, H-M2, H-M3 | Perplexity gate + alignment ratio pre-registered |
| R4 | Insufficient per-category power | A4 | **Medium** | H-E1, H-M3 | Power analysis pre-check; supplement with published baselines |
| R5 | Hybrid-4 middle-layer suboptimal | A5 | **Medium** | H-M3 | Secondary prediction; H-E1 and H-M2 primary |

Critical Risks: 1 | High Risks: 2 | Medium Risks: 2 | Low Risks: 0

---

## 5. Dependency Graph (DAG) + Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Parallel Initialization]
    H-M1 (Frobenius Gate — Day 0, <1 GPU-day)
    NO dependencies — run first, blocks everything

         │ (MUST PASS)
         ▼

[Level 1 — Foundation]
    H-E1 (Existence — Distillation + LongBench Evaluation)
    Depends on: H-M1 (gate must pass)
    Gate: MUST_WORK → if fails: STOP

         │ (Data from H-E1 evaluation reused for H-M2, H-M3)
         ▼

[Level 2 — Core Mechanism]
    H-M2 (Needle-Depth Slope — statistical analysis)
    Depends on: H-E1 data + H-M1 interpretation

         │
         ▼

[Level 3 — Asymmetry Profile]
    H-M3 (Generation vs Retrieval Asymmetry)
    Depends on: H-M2 (mechanistic grounding)

═══════════════════════════════════════════════════════════
Critical Path: H-M1 → H-E1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-M1 | None | MUST_WORK |
| 1 | H-E1 | H-M1 (gate) | MUST_WORK |
| 2 | H-M2 | H-E1 (data) | SHOULD_WORK |
| 3 | H-M3 | H-M2 (context) | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses (14 GPU-days + analysis)
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ Day 0 │ Week 1-2 │ Week 3-4 │ Week 5
─────────────────┼───────┼──────────┼──────────┼────────
PHASE 1: Gate + Foundation
  H-M1 (Frobenius) │ ████  │          │          │
  [Gate 1-M1]       │    ◆  │          │          │
  LAWCAT distill    │       │ ████████ │          │
  MOHAWK+Hybrid-4   │       │ ████████ │          │
  LongBench eval    │       │          │ ████     │
  H-E1 analysis     │       │          │ ████  ◆  │
  [Gate 1-E1]       │       │          │      ◆   │
─────────────────┼───────┼──────────┼──────────┼────────
PHASE 2: Mechanism Analysis (from H-E1 data)
  H-M2 (depth-slope)│      │          │          │ ████
  H-M3 (asymmetry)  │      │          │          │ ████
  [Synthesis]        │      │          │          │    ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: ~5 weeks (14 GPU-days + statistical analysis)
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

- Critical Path: H-M1 → H-E1 (distillation) → H-E1 (evaluation) → H-M2 → H-M3
- Total Duration: ~5 weeks
  - Day 0: H-M1 Frobenius gate (< 1 GPU-day)
  - Week 1-2: LAWCAT + MOHAWK + Hybrid-4 distillation (~13 GPU-days)
  - Week 3-4: LongBench v2 evaluation (~1 GPU-day) + H-E1 statistical analysis
  - Week 5: H-M2 + H-M3 analysis (from H-E1 data — no new training)
- Note: H-M2 and H-M3 require no additional GPU compute — they reuse H-E1 per-example evaluation data.

### 5.5 Resource Summary

Total Hypotheses: 4 (H-E1, H-M1, H-M2, H-M3)
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0

Verification Phases: 2
1. Foundation (H-M1 gate + H-E1 distillation + evaluation): ~4 weeks
2. Mechanism Analysis (H-M2 + H-M3 statistical analysis): ~1 week

Total GPU-days: ~14 (LAWCAT ~7, MOHAWK Stage 1+2 ~4, Hybrid-4 ~2, Eval ~1)
Execution Mode: Sequential chain with data reuse at H-M2/H-M3 stage

### 5.6 Execution Order

**Step 1**: Execute H-M1 Frobenius gate — Day 0 (< 1 GPU-day)
**Step 2**: Evaluate Gate H-M1 → If slope > 0.5 or 90th pct > 0.3 at N=8k: STOP; otherwise proceed
**Step 3**: Execute LAWCAT distillation (Week 1-2, 2×A100, ~1B tokens C4)
**Step 4**: Execute MOHAWK Stage 1+2 + Hybrid-4 Stage 3 distillation (Week 2-3, 4×A100)
**Step 5**: Enforce perplexity gate (≤5%) and alignment gate (L2 ratio ≤0.15) for each model
**Step 6**: Execute LongBench v2 evaluation on all models (~6 hours per model per 1×A100)
**Step 7**: Evaluate Gate H-E1 → compute interaction term and ratio; if fails: STOP and route to Phase 2A-Dialogue
**Step 8**: Execute H-M2 needle-depth regression (Week 5, statistical analysis)
**Step 9**: Execute H-M3 asymmetry analysis + mediation regression (Week 5, statistical analysis)
**Final**: Verification complete — proceed to Phase 4.5 synthesis

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Under fixed-budget (≤1B tokens) distillation, MOHAWK-SSM conversion of LLaMA-3-8B produces ≥2× larger normalized accuracy degradation on retrieval-heavy LongBench v2 categories than generation-heavy categories, while LAWCAT-linear-attention exhibits a more uniform profile, due to MOHAWK's bounded state vector forgetting exact needle-token addresses vs. LAWCAT's causal Conv1D preserving local token-to-token attention.

**Supporting Evidence:**
1. Causal mechanism grounded in MOHAWK's SSD state update (h_t = A·h_{t-1} + B·x_t) — exponential forgetting of early-token positions mathematically follows from the recurrence structure
2. LAWCAT Conv1D local dependency mechanism demonstrated at S-NIAH and BABILong (Liu et al., EMNLP 2025); direct mechanistic basis for shallower depth-degradation slope
3. Overflow Prevention [2505.07793]: scratch-trained SSMs (Falcon3-Mamba, RecurrentGemma, RWKV6) show systematic degradation on LongBench v2 multi-doc QA and synthetic categories — convergent evidence for SSM retrieval weakness

**Strengths:**
- Fixed base model design eliminates H-E1 capability-tier confound (H-E1 lesson directly applied)
- Three independent bodies of evidence (MOHAWK fidelity, LAWCAT Conv1D, Overflow Prevention benchmark)
- Pre-registered 5 disconfirmation pathways before experiment
- Day 0 Frobenius gate provides cheap insurance against interpretive errors

**Expected Outcomes:**
- Primary (P1): Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0, CI strictly above 1.0, p<0.01
- Secondary (P2): |β_depth^SSM| ≥ 2× |β_depth^LAWCAT|, non-overlapping 95% CIs
- Tertiary (P3): Hybrid-4 max Δ_norm ≤ 0.05; MOHAWK full Δ_norm ≥ 0.10 on retrieval

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant task-type × conversion-strategy interaction on LongBench v2 normalized accuracy: degradation is uniform across categories for both MOHAWK-SSM and LAWCAT-linear-attention conversions of LLaMA-3-8B.

**Counter-Arguments:**
1. Architecture-vs-curriculum confound: short-only distillation (2048-token max) may independently cause retrieval degradation regardless of architecture — both MOHAWK and LAWCAT may fail retrieval due to curriculum, not bounded-state limits
2. Assumption A3 violation risk: LLaMA-3-8B is larger than Mistral-7B (LAWCAT) and Phi-1.5 (MOHAWK); at ≤1B tokens, neither model may achieve sufficient alignment, making any downstream difference attributable to undertrained weights rather than architectural effects
3. Statistical power concern: ~83 questions per LongBench v2 category may be insufficient to achieve p<0.01 interaction significance after Holm correction, especially if effect size is moderate

**Potential Failure Points:**
- Frobenius error scales super-linearly → R1 (retrieval degradation is approximation breakdown, not bounded-state bias)
- Perplexity gate fails for one model → R3 (undertrained student confounds architectural comparison)
- β_depth slopes overlap → R2 (Conv1D mechanism insufficient; degradation is not depth-dependent)

**Conditions Under Which H0 Would Be Supported:**
- If interaction term p ≥ 0.01 after Holm correction in mixed-effects model
- If Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) bootstrap CI includes or falls below 2.0
- If mixed-length distillation ablation (Phase 4) shows interaction disappears → curriculum was the driver

### 6.3 Synthesis

**Balanced Assessment:**

H-Conv1D-v1 presents a testable and methodologically clean hypothesis with strong mechanistic grounding. The fixed-base-model design directly addresses the key failure mode of H-E1 (capability-tier confound). However, the null hypothesis raises valid concerns about the architecture-vs-curriculum confound — a concern acknowledged and explicitly pre-registered for Phase 4 ablation.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Day 0 Frobenius gate (H-M1):** Eliminates approximation-breakdown confound before any distillation investment
2. **Sequential mechanism testing (H-M1→H-E1→H-M2→H-M3):** Tests each causal chain step separately, allowing localization of any failure
3. **Pre-registered gate conditions:** Allow early detection of H0 support before resource commitment; perplexity gate protects against undertrained-student confound
4. **Mediation regression (H-M3):** Statistically controls for alignment quality and perplexity gap in the architectural effect estimate

**Conditions for Thesis Support:**
- H-M1 MUST_WORK gate passes (sub-linear Frobenius scaling)
- H-E1 MUST_WORK gate passes (≥2× ratio with CI above 1.0, p<0.01)
- P1 primary prediction confirmed

**Conditions for Antithesis Support:**
- H-M1 fails (Frobenius super-linear) → approximation-quality failure
- H-E1 fails (ratio < 2× or p ≥ 0.01) → uniform degradation; H0 supported
- Phase 4 mixed-length ablation shows interaction disappears → curriculum was the driver

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-M1 + H-E1 + H-M2 + H-M3 all pass → Thesis fully validated; all 3 causal chain steps confirmed
2. **Partial Support:** H-E1 passes but H-M2 fails → Interaction exists but Conv1D depth-slope mechanism insufficient; narrow claim to interaction phenomenon without full mechanistic explanation
3. **Narrow Support:** H-E1 passes, H-M2 and H-M3 fail → Interaction exists but mechanism unclear; still publishable with H-E1 evidence alone
4. **No Support:** H-M1 or H-E1 fails → Antithesis supported; route to Phase 2A-Dialogue or Phase 0

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Approximation quality | SSD sub-linear Frobenius scaling at long N | Super-linear scaling → approximation breakdown | H-M1 Frobenius gate test |
| Bounded-state forgetting | h_t recurrence causes exponential forgetting | Degradation due to curriculum (short-only training) | Mediation regression; Phase 4 ablation |
| Conv1D local preservation | Conv1D sliding window preserves depth identity | Conv1D window too narrow to differentiate | H-M2 β_depth regression test |
| Task-type contrast | Generation tolerates lossy compression, retrieval requires exact position | Categories may not differ sufficiently | LongBench v2 category diversity + power analysis |
| Attention necessity | Hybrid-4 (4 middle layers) needed for retrieval | Full replacement may be sufficient | H-M3 P3 test (secondary) |

**Overall Robustness Score:** High — five independent falsification pathways pre-registered; Day 0 gate provides cheap insurance; mediation regression statistically controls key confound

**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-Conv1D-v1 — Task-type × conversion-strategy interaction in sub-quadratic LLaMA-3-8B conversion (confidence: 0.78)

**Verification Structure:**
- Mode: Incremental (Phase 2A data pre-seeded; 57% scope reduction)
- Sub-Hypotheses: 4 total (H-E1: 1, H-M1-3: 3)
- Phases: 2 phases over ~5 weeks (14 GPU-days compute)
- Critical Gates: 2 MUST_WORK decision points (H-M1 Frobenius, H-E1 interaction)

**Risk Assessment:** Medium-High
- Primary concerns: (1) Alignment failure at ≤1B token budget for LLaMA-3-8B-scale models [R3-High]; (2) Frobenius super-linear scaling before distillation [R1-Critical]

**Immediate Action:** Begin Day 0 H-M1 Frobenius gate check — cheapest possible insurance before 14 GPU-day distillation investment

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases fully specified with quantitative success criteria
- H0 explicitly addressed: no significant task-type × strategy interaction
- 57% scope reduction from Phase 2A established facts — verification focused on 2 PROVE_NEW claims only
- Data reuse: H-M2 and H-M3 require zero additional GPU compute (derived from H-E1 evaluation data)

**Verification Execution Order:**

**Phase 1: Foundation + Gate** (~4 weeks)
- H-M1: Frobenius error gate — Day 0, MUST PASS (slope ≤ 0.5, 90th pct ≤ 0.3 at N=8k)
- H-E1: LAWCAT + MOHAWK + Hybrid-4 distillation + LongBench v2 evaluation
- Gate: Δ_norm ratio ≥ 2.0, CI above 1.0, interaction p<0.01 — MUST PASS

**Phase 2: Mechanism Analysis** (~1 week)
- H-M2: Needle-depth logistic regression (from H-E1 data)
- H-M3: Generation vs retrieval asymmetry + mediation regression (from H-E1 data)
- These are SHOULD_WORK; failure narrows but does not invalidate

**Critical Decision Points:**

1. **Gate H-M1 (Day 0):** Frobenius gate
   - FAIL → STOP distillation immediately; reframe hypothesis; route to Phase 2A-Dialogue
   - PASS → Proceed to H-E1 distillation

2. **Gate H-E1 (Week 4):** Interaction test
   - FAIL → STOP; route to Phase 2A-Dialogue for hypothesis redesign
   - PASS → Proceed to H-M2 + H-M3 mechanism analysis

**Open Questions:**
- Does architecture-vs-curriculum confound affect results? (mixed-length distillation ablation deferred to Phase 4)
- Which specific attention layers (early/middle/late) are structurally necessary for retrieval? (layer-localization deferred to Phase 4)
- Does MOHAWK Stage 3 (logit distillation) recover retrieval performance beyond Stage 1+2? (stage ablation is part of H-M sub-hypothesis)

**Recommendations:**

1. **Immediate Actions:**
   - Run Day 0 H-M1 Frobenius gate check first (< 1 GPU-day insurance)
   - Pre-register all success criteria and gates before starting distillation
   - Set up perplexity + alignment ratio monitoring scripts before training begins

2. **Resource Allocation:**
   - Allocate 14 GPU-days for critical path (LAWCAT: ~7, MOHAWK+Hybrid-4: ~6, eval: ~1)
   - Reserve 2× buffer for alignment failures (possible 2B token budget expansion)

3. **Failure Management:**
   - Document all gate results with timestamps
   - Execute PIVOT/EXPLORE strategies as defined per risk mitigation plan
   - Pre-register mediation regression specification before LongBench evaluation

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-Conv1D-v1)
- Generated: 2026-08-03T14:30:00Z
- Convergence: 15 exchanges, 6 criteria met
- Scope reduction: 57% (5/7 claims BUILD_ON)

**B. MCP Tool Usage Summary**
- Total MCP calls: 2 (incremental mode)
- Tools: mcp__clearThought__scientificmethod (2×: H-E1 hypothesis+experiment; H-M-integrated hypothesis)
- Mode: Incremental (Phase 2A pre-seeded; 4-6 call budget, used 2)

**C. Established Facts (BUILD_ON — not re-verified)**
1. MOHAWK 3-stage distillation pipeline converts transformers to SSM with demonstrated accuracy retention at 1.3B scale [MOHAWK NeurIPS 2024]
2. LAWCAT achieves >90% passkey retrieval at 22K tokens from Mistral-7B with <1B distillation tokens [Liu et al., EMNLP 2025]
3. Scratch-trained SSMs (Falcon3-Mamba, RecurrentGemma, RWKV6) show systematic retrieval degradation on LongBench v2 [Overflow Prevention, 2025]
4. MOHAWK matrix approximation fidelity correlates with downstream accuracy (Frobenius-accuracy link established)
5. MOHAWK Hybrid-4 (4 attention layers) recovers 66.0 vs 67.2 teacher average on lm-eval tasks
