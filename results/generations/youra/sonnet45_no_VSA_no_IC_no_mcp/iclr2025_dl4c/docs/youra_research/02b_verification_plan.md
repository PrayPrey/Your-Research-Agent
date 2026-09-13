# Verification Plan: Task-Dependent Feedback Orthogonality in Code Generation Alignment

**Date:** 2026-08-25
**Hypothesis ID:** H-FeedbackOrthogonality-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under code generation tasks with varying specification completeness (competitive programming, basic problems, realistic software tasks), if we measure pairwise correlations between execution-based feedback, AI reward model feedback, and human rating feedback on the same generated code samples, then execution-human correlation will vary systematically by task type (>0.8 for competitive, 0.6-0.8 for basic, <0.5 for realistic) while AI-human correlation remains stable (0.5-0.7 across all types), because execution feedback measures runtime behavior that only proxies human intent when specifications are fully test-capturable, while AI feedback measures learned patterns that partially overlap with intent regardless of specification completeness.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in execution-human or AI-human correlation structure across task types (competitive, basic, realistic). All pairwise correlations remain within 0.1 of each other across datasets.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + MBPP + SWE-bench (tri-dataset) (standard) | Three datasets span specification completeness spectrum: HumanEval (complete), MBPP (intermediate), SWE-bench (underspecified). Enables testing task-dependent correlation hypothesis. |
| **Model** | Codex (code-davinci-002) or CodeGen (Salesforce/codegen-16B-mono) | Frozen checkpoint ensures feedback modality is only variable. Strong baseline model (SoTA on HumanEval) ensures generated code is diverse enough to reveal correlation structure. |

**Dataset Details:**
- Source: OpenAI (HumanEval), Google (MBPP), Princeton NLP (SWE-bench)
- Path: Public benchmarks: HumanEval via openai/human-eval, MBPP via google-research/google-research, SWE-bench via princeton-nlp/SWE-bench

**Model Details:**
- Type: Pre-trained code generation model
- Source: OpenAI API (Codex) or Hugging Face (CodeGen)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Execution-only feedback (CodeRL 2022) | ~70-80% pass@1 | HumanEval, APPS |
| Human feedback for general text (RLHF 2022) | N/A for code | InstructGPT human preferences |
| AI feedback (RLAIF 2023) | Comparable to human on text | General text generation |

**Best Baseline:** ~70-80% pass@1 on HumanEval with execution-only feedback (CodeRL 2022)

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Human ratings (5-point scale) accurately measure intent alignment for code correctness | Standard practice in code review and human evaluation studies; validated by inter-rater reliability checks | If human ratings unreliable (Cohen's kappa <0.6), correlation measurements are noise, experiment fails |
| A2 | 100 samples per dataset provide sufficient statistical power to detect correlation differences of ≥0.3 | Power analysis: n=100 gives 80% power to detect r=0.3 difference at α=0.05 | If sample size insufficient, correlations have wide confidence intervals, can't distinguish task-dependent from uniform structure |
| A3 | Execution feedback (test pass/fail) is a valid measure of functional correctness | Foundational assumption in code generation benchmarks (HumanEval, MBPP, SWE-bench all use test-based evaluation) | If tests are buggy or incomplete, execution feedback is invalid — but this would affect all code generation research, not just this study |
| A4 | AI feedback (reward model trained on code corpora) measures learned patterns distinct from execution correctness | Construct validity check: AI models learn from static code, not runtime behavior | If AI reward model is secretly execution-based (e.g., trained on test pass/fail labels), modalities aren't orthogonal |
| A5 | Task type categorization (competitive, basic, realistic) reflects genuine differences in specification completeness | HumanEval = competitive programming contests (complete specs), SWE-bench = GitHub issues (underspecified), MBPP = educational problems (intermediate) — established benchmark distinctions | If all three datasets have similar specification completeness, task type is a spurious variable, no reason for correlation structure to vary |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic mapping of feedback orthogonality space (pairwise correlations between execution/AI/human feedback) segmented by task type for code generation.

**Key Innovation:** Reframing alignment comparison from "which feedback wins" to "where does each feedback type provide unique signal" — shifts research question from competitive to complementary modalities.

**Differentiation:**
- **CodeRL (Le et al. 2022):** Used execution-only feedback for RL fine-tuning. We compare execution vs AI vs human feedback orthogonality, no training involved.
- **RLAIF (Lee et al. 2023):** Compared AI vs human feedback for general text generation, not code-specific, and didn't include execution feedback.
- **HumanEval+ (Liu et al. 2023):** Revealed hidden test gap but didn't systematically measure feedback signal correlations or segment by task type.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Feedback Correlation Structure Exists and Varies**

**Statement**: Under code generation tasks with varying specification completeness (HumanEval, MBPP, SWE-bench), if we measure pairwise correlations between execution, AI, and human feedback on same code samples, then correlation patterns will exist and be measurable with sufficient statistical power to detect task-dependent differences.

**Rationale**: Validates that feedback modalities can be collected on same samples and that correlation structure is detectible. Foundation for mechanism hypotheses — if correlations are all noise or uniform, task-dependent hypothesis fails before testing mechanism.

**Variables** (from Phase 2A):
- Independent: Task Type (competitive/basic/realistic)
- Dependent: Pairwise Feedback Correlation (Pearson r)
- Controlled: Base model, sample size (100/dataset), human rater pool

**Verification Protocol**:
1. Generate 100 code samples per dataset (HumanEval, MBPP, SWE-bench) with frozen Codex/CodeGen
2. Collect execution feedback (test pass/fail), AI reward scores, human ratings (5-point scale, 3 raters)
3. Compute pairwise correlations (execution-human, AI-human, execution-AI) per dataset
4. Verify human rater inter-reliability (Cohen's kappa >0.6)
5. Bootstrap confidence intervals (1000 iterations) to confirm correlations statistically distinguishable

**Success Criteria** (PoC):
- Primary: All three pairwise correlations measurable (not noise: p<0.05)
- Secondary: Human inter-rater reliability Cohen's kappa >0.6

**Failure Response**:
- IF fails: ABANDON (correlation study infeasible)

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 1.6 Prediction P1 (primary prediction) + Section 5 SH1 (existence)

---
**H-M1: Specification Completeness Determines Test-Intent Capture**

**Statement**: Under code generation tasks, if task specifications are fully captured by tests (competitive programming), then execution feedback captures human intent dimensions, but if specifications are underspecified (realistic software), then execution feedback misses critical intent dimensions only humans evaluate, because tests can only proxy intent when they encode all intent requirements.

**Rationale**: Tests causal chain Step 1 — whether specification completeness actually determines how well tests capture human intent. Validates construct validity assumption: execution measures "test-passable" not "human-approved" when tests don't capture full spec.

**Variables**:
- Independent: Specification completeness (operationalized as task type: HumanEval complete, SWE-bench underspecified)
- Dependent: Intent dimension coverage (qualitative analysis of disagreement cases)
- Controlled: Same human raters, same code samples

**Verification Protocol**:
1. Identify disagreement cases (execution PASS but human rating LOW, or vice versa)
2. Qualitatively code failure modes: what did execution miss that humans caught?
3. Categorize by task type: competitive vs realistic
4. Quantify: % of disagreement cases where intent dimensions were missed
5. Validate: competitive tasks have fewer missed dimensions than realistic

**Success Criteria** (PoC):
- Primary: Qualitative analysis shows specification underspecified tasks (SWE-bench) have >2× missed intent dimensions vs competitive (HumanEval)
- Secondary: Missed dimensions cluster by task type (not random)

**Failure Response**:
- IF fails: PIVOT (specification completeness may not be the right construct)

**Dependencies**: H-E1 (need correlation data + disagreement cases)

**Source**: Phase 2A Section 1.3 Causal Step 1 + Falsifier

---
**H-M2: Execution Correlation Depends on Specification Completeness**

**Statement**: Under code generation tasks, if tests fully capture intent (competitive), then execution-human correlation >0.8 (strong proxy), but if tests underspecify intent (realistic), then execution-human correlation <0.5 (weak proxy), because execution feedback quality as intent proxy depends on test coverage of intent dimensions.

**Rationale**: Tests causal chain Step 2 — the core task-dependent correlation hypothesis. If this fails (correlations uniform across tasks), the orthogonality hypothesis is refuted but we've learned execution suffices everywhere (still publishable outcome per Phase 2A key tension).

**Variables**:
- Independent: Task type (competitive/basic/realistic)
- Dependent: Execution-human correlation (Pearson r)
- Controlled: Same base model, sample size, human raters

**Verification Protocol**:
1. Compute execution-human Pearson r per dataset from H-E1 data
2. Test correlation difference across task types: HumanEval vs SWE-bench
3. Statistical test: ANOVA on correlation coefficients, post-hoc Tukey HSD
4. Bootstrap variance: between-task variance ≥2× within-task variance
5. Validate predicted pattern: HumanEval >0.8, MBPP 0.6-0.8, SWE-bench <0.5

**Success Criteria** (PoC):
- Primary: Execution-human correlation varies by task (ANOVA p<0.05, effect size >0.3)
- Secondary: Between-task variance ≥2× within-task variance

**Failure Response**:
- IF fails: EXPLORE (execution-dominance outcome — still publishable)

**Dependencies**: H-E1, H-M1 (need correlation data + validated mechanism)

**Source**: Phase 2A Section 1.3 Causal Step 2 + Section 1.6 Prediction P1

---
**H-M3: AI Feedback Stable Across Specification Types**

**Statement**: Under code generation tasks with varying specification completeness, if AI reward models measure learned surface patterns (not runtime behavior), then AI-human correlation remains stable (0.5-0.7) across all task types (competitive, basic, realistic), because pattern-based feedback doesn't depend on whether tests capture full specifications.

**Rationale**: Tests causal chain Step 3 — validates that AI feedback orthogonality is fundamentally different from execution (stable vs task-dependent). Confirms construct validity: AI measures patterns, execution measures runtime correctness.

**Variables**:
- Independent: Task type (competitive/basic/realistic)
- Dependent: AI-human correlation (Pearson r)
- Controlled: Same AI reward model, same human raters

**Verification Protocol**:
1. Compute AI-human Pearson r per dataset from H-E1 data
2. Test correlation stability across task types
3. Statistical test: variance in AI-human correlations <0.1 across datasets
4. Compare to H-M2: AI variance << execution variance
5. Validate AI-human stays in 0.5-0.7 range regardless of task type

**Success Criteria** (PoC):
- Primary: AI-human correlation variance across tasks <0.1 (stable)
- Secondary: AI variance < execution variance (orthogonality confirmed)

**Failure Response**:
- IF fails: PIVOT (AI feedback may also be task-dependent)

**Dependencies**: H-E1, H-M2 (need both execution and AI correlation data)

**Source**: Phase 2A Section 1.3 Causal Step 3 + Section 1.6 Prediction P2

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
H-E1 → H-M1 → H-M2 → H-M3
```
<!-- Sequential chain: Existence → Mechanism steps 1-3 -->

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Evidence of feedback correlation variation exists | STOP - reassess hypothesis |
| H-M1 | MUST_WORK | Specification completeness affects test-intent capture | PIVOT - refine mechanism |
| H-M2 | SHOULD_WORK | Execution-human correlation task-dependent | Document limitation |
| H-M3 | SHOULD_WORK | AI-human correlation stable across tasks | Document limitation |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 | 2 weeks |
| Phase 2 (cont.) | H-M2, H-M3 | 2 weeks |

**Total Duration:** 6 weeks

---
