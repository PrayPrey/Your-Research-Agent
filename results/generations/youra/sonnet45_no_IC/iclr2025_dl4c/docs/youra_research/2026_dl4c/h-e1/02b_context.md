# Per-Hypothesis Context: h-e1

**Generated:** 2026-07-12
**Source:** Extracted from 02b_verification_plan.md
**Hypothesis ID:** h-e1
**Type:** EXISTENCE

---

## Hypothesis Statement

Under training conditions with access to execution, human, and AI feedback, if we apply tri-modal RL framework with dynamic weight scheduling across three phases, then we achieve ≥3% absolute improvement in harmonic mean of pass@1 and human preference scores vs. best single-feedback baseline, because sequential capability building requires phase-appropriate feedback emphasis.

---

## Hypothesis Details

### Type & Rationale

**Type:** EXISTENCE

**Rationale:**
Validates that tri-modal integration actually improves performance over single-feedback baselines. This is the foundation hypothesis - if it fails, the entire approach is invalidated. Tests the core claim that combining three feedback modalities with dynamic scheduling yields measurable improvement.

### Variables

**Independent Variable:**
- Feedback Integration Strategy (5-level categorical)
  - execution-only
  - human-only  
  - AI-only
  - tri-modal-static
  - tri-modal-dynamic

**Dependent Variables:**
- **Primary:** Harmonic Mean Performance = harmonic_mean(pass@1, human_preference) ∈ [0,1]
- **Secondary:** Pass@1 Correctness, Human Preference Score

**Controlled Variables:**
- Model Architecture: 1.5B parameters
- Dataset: HumanEval + MBPP
- RL Algorithm: PPO
- Evaluation Protocol: N=200 held-out, independent blind annotators

---

## Experimental Setup (from Phase 2A)

### Dataset

**Name:** HumanEval + MBPP (standard)
**Justification:** Competitive programming tasks with automated test cases (execution feedback available). Well-established benchmarks for code generation evaluation.
**Details:**
- Source: OpenAI HumanEval (164 problems) + Google MBPP (500 problems)
- Path: https://github.com/openai/human-eval, https://github.com/google-research/google-research/tree/master/mbpp

### Model

**Name:** 1.5B Parameter Code LLM
**Justification:** RL fine-tuning requires pre-trained code model as initialization. 1.5B size balances performance and computational cost (~5000 GPU-hours feasible).
**Details:**
- Type: Transformer decoder (Codex-style architecture)
- Source: Pre-trained checkpoint (e.g., CodeGen, StarCoder)

---

## Verification Protocol

**Steps:**

1. Train 5 baseline models (execution-only, human-only, AI-only, tri-modal-static, tri-modal-dynamic) on HumanEval+MBPP training set.

2. Evaluate all models on held-out test set (N=200) with independent human annotators for preference scores.

3. Calculate harmonic mean (pass@1 × human_preference) for each model configuration.

4. Perform independent samples t-test comparing tri-modal-dynamic vs. best single-feedback baseline (α=0.05, two-tailed).

5. Report effect size and confidence intervals for improvement magnitude.

---

## Success Criteria (PoC: Direction-based)

**Primary:**
- Tri-modal-dynamic harmonic mean > best baseline harmonic mean AND
- p < 0.05 AND
- improvement ≥ 3% absolute

**Secondary:**
- No correctness regression: pass@1_tri-modal ≥ 0.9 × pass@1_execution-only

---

## Gate Condition

**Type:** MUST_WORK

**Pass Condition:** ≥3% improvement (p<0.05) AND tri-modal > all single-feedback baselines

**Fail Action:** ABANDON entire approach → Phase 0 (approach invalidated)

---

## Dependencies

**Prerequisites:** None (foundation hypothesis)

**Dependent Hypotheses:**
- h-m1: Phase 1 Execution-Heavy Foundation (depends on h-e1)
- h-m2: Phase 2 AI-Feedback Quality Refinement (depends on h-m1)
- h-m3: Phase 3 Human-Feedback Edge Cases (depends on h-m2)

---

## Baseline Methods (for Comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| PPOCoder (execution feedback RL) | ~30% absolute improvement (40% → 70% pass@1 on MBPP) | MBPP |
| RLHF for Code (human feedback only) | Subjective quality improvement (no quantitative pass@1 reported) | Various code generation tasks |
| Themis (multi-criteria reward model) | Multi-dimensional quality scores (correctness + style + efficiency) | 350K+ preference pairs |

---

## Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Execution feedback, human feedback, and AI feedback capture orthogonal quality dimensions | Execution tests correctness (objective), human rates quality (subjective), AI approximates human preferences (learned). Different measurement modalities suggest orthogonality. | If feedback types are highly correlated (redundant information), tri-modal integration provides no benefit over single-feedback (Occam's razor favors simpler model). |
| A2 | Sequential capability building holds (correctness prerequisite for quality optimization) | Intuitive reasoning: Can't optimize code quality if code doesn't execute. Needs empirical validation. | If quality can be optimized independently of correctness, dynamic scheduling is unnecessary (static weights or parallel optimization suffice). |
| A5 | Reward signal distributions can be normalized compatibly (percentile rank transformation) | Process-supervised RL [Ye et al., 2025] uses percentile normalization successfully. Statistical transformation handles distributional differences. | If percentile transformation loses critical information (e.g., long-tail rare events), aggregated reward may miss important signals. |

---

## Risk Analysis

**High Severity Risks:**

**R1: Feedback Redundancy** (from A1)
- If feedback types are highly correlated, tri-modal provides no benefit
- Mitigation: Measure pairwise correlation (target r < 0.7), pivot to two-modal if needed

**Medium Severity Risks:**

**R2: Non-Sequential Optimization** (from A2)
- If quality can be optimized independently, dynamic scheduling is unnecessary
- Mitigation: Compare static vs dynamic tri-modal, simplify to static if no difference

---

## Research Gap & Novelty

**Preserved Novelty:** Online integration of three heterogeneous feedback signals (execution, human, AI) during RL training with dynamic weight scheduling

**Key Innovation:** Dynamic weight schedule that adapts feedback emphasis to training phase (correctness → quality → edge cases), enabling multi-objective optimization via sequential capability building

**Differentiation:**
- PPOCoder: Single-feedback (execution-only). We extend to tri-modal with dynamic integration.
- Curriculum-RLAIF: Single-feedback (AI-only) with curriculum on task difficulty. We add execution+human feedback and curriculum on feedback type.
- Themis: Multi-criteria reward model trained offline, used for ranking. We use multi-modal rewards online during RL with dynamic weights.
- Process-Supervised RL: Process-level execution feedback. We add human+AI feedback integration for quality beyond correctness.

---

**Source Verification Plan:** 02b_verification_plan.md (Sections 1, 2.2)
**Generated by:** Phase 2C Step 1 (JIT context extraction)
