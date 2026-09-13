# Phase 2B Context: h-m2

**Generated:** 2026-08-25
**Source:** 02b_verification_plan.md (extracted)

---

## Hypothesis Information

**ID:** h-m2
**Type:** MECHANISM
**Gate:** MUST_WORK

**Statement:**
Under code generation tasks, if tests fully capture intent (competitive), then execution-human correlation >0.8 (strong proxy), but if tests underspecify intent (realistic), then execution-human correlation <0.5 (weak proxy), because execution feedback quality as intent proxy depends on test coverage of intent dimensions.

**Rationale:**
Tests causal chain Step 2 — the core task-dependent correlation hypothesis. If this fails (correlations uniform across tasks), the orthogonality hypothesis is refuted but we've learned execution suffices everywhere (still publishable outcome per Phase 2A key tension).

---

## Prerequisites

**Direct Dependencies:** h-e1, h-m1

**Prerequisite Results:**
- h-e1: VALIDATED — correlation infrastructure working, all pairwise correlations statistically significant
- h-m1: VALIDATED — specification completeness determines test-intent capture confirmed

---

## Variables

**Independent Variable:** Task type (competitive/basic/realistic)
**Dependent Variable:** Execution-human correlation (Pearson r)
**Controlled Variables:** Same base model, sample size, human raters

---

## Experimental Setup

### Dataset
**Name:** HumanEval + MBPP + SWE-bench (tri-dataset)
**Type:** standard
**Source:** OpenAI (HumanEval), Google (MBPP), Princeton NLP (SWE-bench)
**Justification:** Three datasets span specification completeness spectrum: HumanEval (complete), MBPP (intermediate), SWE-bench (underspecified). Enables testing task-dependent correlation hypothesis.

**Sample Size:** Full standard test sets per dataset
- HumanEval: 164 problems
- MBPP: 500 problems
- SWE-bench: 300 instances

### Model
**Name:** Salesforce/codegen-350M-mono
**Type:** Pre-trained code generation model (frozen checkpoint)
**Source:** Hugging Face
**Justification:** Frozen checkpoint ensures feedback modality is only variable. Proven model from h-e1 validation.

---

## Verification Protocol

1. Compute execution-human Pearson r per dataset from H-E1 data
2. Test correlation difference across task types: HumanEval vs SWE-bench
3. Statistical test: ANOVA on correlation coefficients, post-hoc Tukey HSD
4. Bootstrap variance: between-task variance ≥2× within-task variance
5. Validate predicted pattern: HumanEval >0.8, MBPP 0.6-0.8, SWE-bench <0.5

---

## Success Criteria (PoC)

**Primary:** Execution-human correlation varies by task (ANOVA p<0.05, effect size >0.3)
**Secondary:** Between-task variance ≥2× within-task variance

---

## Failure Response

**IF fails:** EXPLORE (execution-dominance outcome — still publishable)

---

## Gate Condition

**Type:** MUST_WORK
**Requirement:** PoC must demonstrate task-dependent variance in execution-human correlation
**Consequence if fails:** BLOCKS h-m3 (dependent hypothesis)

---

## Continuation Context from Prerequisites

### From h-e1 (VALIDATED):
- Pairwise correlation infrastructure working
- HumanEval exec-human r=0.68, ai-human r=0.45, exec-ai r=0.38
- MBPP exec-human r=0.71, ai-human r=0.52, exec-ai r=0.41
- Cohen's kappa=0.72 (strong inter-rater reliability)
- Data collection pipeline validated

### From h-m1 (VALIDATED):
- Specification completeness determines test-intent capture confirmed
- SWE-bench showed 2.3× missed intent dimensions vs HumanEval
- Qualitative failure modes cluster by task type
- Construct validity established

---

**Next Phase:** Phase 2C - Experiment Design
