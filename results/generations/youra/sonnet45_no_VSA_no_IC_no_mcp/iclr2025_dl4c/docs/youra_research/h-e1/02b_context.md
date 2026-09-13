# Hypothesis Context: H-E1

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Prerequisites:** None

---

## Hypothesis Statement

Under code generation tasks with varying specification completeness (HumanEval, MBPP, SWE-bench), if we measure pairwise correlations between execution, AI, and human feedback on same code samples, then correlation patterns will exist and be measurable with sufficient statistical power to detect task-dependent differences.

---

## Rationale

Validates that feedback modalities can be collected on same samples and that correlation structure is detectible. Foundation for mechanism hypotheses — if correlations are all noise or uniform, task-dependent hypothesis fails before testing mechanism.

---

## Variables

- **Independent Variable:** Task Type (competitive/basic/realistic)
- **Dependent Variable:** Pairwise Feedback Correlation (Pearson r)
- **Controlled Variables:** Base model, sample size (100/dataset), human rater pool

---

## Experimental Setup (from Phase 2A)

### Dataset
- **Name:** HumanEval + MBPP + SWE-bench (tri-dataset)
- **Type:** standard
- **Justification:** Three datasets span specification completeness spectrum: HumanEval (complete), MBPP (intermediate), SWE-bench (underspecified). Enables testing task-dependent correlation hypothesis.
- **Source:** OpenAI (HumanEval), Google (MBPP), Princeton NLP (SWE-bench)
- **Path:** Public benchmarks: HumanEval via openai/human-eval, MBPP via google-research/google-research, SWE-bench via princeton-nlp/SWE-bench

### Model
- **Name:** Codex (code-davinci-002) or CodeGen (Salesforce/codegen-16B-mono)
- **Type:** Pre-trained code generation model
- **Justification:** Frozen checkpoint ensures feedback modality is only variable. Strong baseline model (SoTA on HumanEval) ensures generated code is diverse enough to reveal correlation structure.
- **Source:** OpenAI API (Codex) or Hugging Face (CodeGen)

---

## Verification Protocol

1. Generate 100 code samples per dataset (HumanEval, MBPP, SWE-bench) with frozen Codex/CodeGen
2. Collect execution feedback (test pass/fail), AI reward scores, human ratings (5-point scale, 3 raters)
3. Compute pairwise correlations (execution-human, AI-human, execution-AI) per dataset
4. Verify human rater inter-reliability (Cohen's kappa >0.6)
5. Bootstrap confidence intervals (1000 iterations) to confirm correlations statistically distinguishable

---

## Success Criteria (PoC)

### Primary
- All three pairwise correlations measurable (not noise: p<0.05)

### Secondary
- Human inter-rater reliability Cohen's kappa >0.6

---

## Failure Response

**IF fails:** ABANDON (correlation study infeasible)

---

## Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Execution-only feedback (CodeRL 2022) | ~70-80% pass@1 | HumanEval, APPS |
| Human feedback for general text (RLHF 2022) | N/A for code | InstructGPT human preferences |
| AI feedback (RLAIF 2023) | Comparable to human on text | General text generation |

**Best Baseline:** ~70-80% pass@1 on HumanEval with execution-only feedback (CodeRL 2022)

---

## Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Human ratings (5-point scale) accurately measure intent alignment for code correctness | Standard practice in code review and human evaluation studies; validated by inter-rater reliability checks | If human ratings unreliable (Cohen's kappa <0.6), correlation measurements are noise, experiment fails |
| A2 | 100 samples per dataset provide sufficient statistical power to detect correlation differences of ≥0.3 | Power analysis: n=100 gives 80% power to detect r=0.3 difference at α=0.05 | If sample size insufficient, correlations have wide confidence intervals, can't distinguish task-dependent from uniform structure |
| A3 | Execution feedback (test pass/fail) is a valid measure of functional correctness | Foundational assumption in code generation benchmarks (HumanEval, MBPP, SWE-bench all use test-based evaluation) | If tests are buggy or incomplete, execution feedback is invalid — but this would affect all code generation research, not just this study |
| A4 | AI feedback (reward model trained on code corpora) measures learned patterns distinct from execution correctness | Construct validity check: AI models learn from static code, not runtime behavior | If AI reward model is secretly execution-based (e.g., trained on test pass/fail labels), modalities aren't orthogonal |
| A5 | Task type categorization (competitive, basic, realistic) reflects genuine differences in specification completeness | HumanEval = competitive programming contests (complete specs), SWE-bench = GitHub issues (underspecified), MBPP = educational problems (intermediate) — established benchmark distinctions | If all three datasets have similar specification completeness, task type is a spurious variable, no reason for correlation structure to vary |

---

## Dependencies

**Prerequisites:** None (foundation hypothesis)

**Dependent Hypotheses:** H-M1, H-M2, H-M3 (all mechanism hypotheses depend on H-E1 existence proof)

---

**Source:** Phase 2B Verification Plan Section 2.2 (H-E1 Specification)
