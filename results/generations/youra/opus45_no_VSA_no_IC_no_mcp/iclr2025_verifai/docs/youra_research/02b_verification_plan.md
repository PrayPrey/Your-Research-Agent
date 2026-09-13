# Verification Plan: Error Format for LLM Self-Repair

**Date:** 2026-08-28
**Hypothesis ID:** H-ErrorFormat-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the setting of LLM self-repair on code generation benchmarks (HumanEval+, MBPP+), if static analysis errors are formatted as structured templates with intermediate-specificity fix suggestions, then repair success rates will improve over raw compiler output, because structured formatting reduces the representational gap between compiler output and LLM training distribution while intermediate hints provide useful direction without creating copy-paste dependency.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in repair success rate across error format conditions (raw, verbose-raw, structured, scrambled) after controlling for information content and prompt length.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | EvalPlus (HumanEval+ and MBPP+) (standard) | Provides 80x more test cases than original benchmarks, enabling robust error collection from model failures |
| **Model** | CodeLlama-7B, CodeLlama-34B, GPT-4 | Spans parameter scales from 7B to 100B+ to test scale interaction hypothesis |

**Dataset Details:**
- Source: https://github.com/evalplus/evalplus
- Path: evalplus/evalplus

**Model Details:**
- Type: code generation LLM
- Source: HuggingFace (CodeLlama), OpenAI API (GPT-4)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Self-repair with raw compiler output | +4.9% minimum improvement | HumanEval, MBPP |
| CompCoder compiler-in-loop | 44% to 89% compilation success | Custom compilation tasks |
| No Self-Repair | Base model generation | HumanEval+, MBPP+ |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Information content can be held constant across format conditions | Reconstruction test design allows verification | Format effects would be confounded with information differences |
| A2 | Real model failures from HumanEval+/MBPP+ are representative of errors LLMs make in practice | EvalPlus benchmarks are standard evaluation with 80x more test cases | Findings may not generalize to production use cases |
| A3 | Error type distribution in benchmark is balanced enough for stratified analysis | Will monitor and report distribution; stratified sampling if needed | Underpowered subanalyses for rare error types |
| A4 | Self-repair framework (theoxo/self-repair) is correctly implemented | ICLR 2024 publication with released code and reproduction artifacts | Baseline may be misconfigured |
| A5 | GPT-4 is not at ceiling for repair of complex error types | Type/semantic errors still challenging per InspectCoder paper | Format benefits may only appear for smaller models |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic study of error message FORMAT for LLM self-repair; prior work focuses on WHETHER to include feedback, not HOW to format it.

**Key Innovation:** Introduces representational alignment hypothesis + fix specificity dimension.

**Scope Reduction:** 40% (BUILD_ON claims excluded from verification)

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

#### H-E1: Structured Error Format Improves Repair Success

**Type:** EXISTENCE
**Statement:** Under LLM self-repair on HumanEval+/MBPP+, if errors are formatted as structured templates (PROBLEM/LOCATION/CONTEXT/ROOT CAUSE), then repair success rate improves over raw compiler output.

**Variables:**
- IV: Error Format (Raw vs Structured)
- DV: Repair Success Rate
- CV: Information content, temperature, max iterations, prompt template

**Success Criteria:**
- Structured format achieves >5% absolute improvement in repair success rate over Raw
- p < 0.05 (BH-FDR corrected)

**Gate:**
- Type: MUST_WORK
- If Fail: Core hypothesis invalid, stop pipeline

**Prerequisites:** None

**Verification Protocol:**
1. Generate code with base model on HumanEval+/MBPP+
2. Collect failures with static analysis errors
3. Apply self-repair with Raw format (control)
4. Apply self-repair with Structured format (treatment)
5. Compare repair success rates with paired t-test
6. Report effect size (Cohen's d)

---

#### H-M1: Representational Alignment Drives Improvement

**Type:** MECHANISM
**Statement:** The improvement from structured formatting occurs because structured templates transform compiler output toward LLM training distribution (natural language, clear sections).

**Variables:**
- IV: Format type (Structured vs Scrambled)
- DV: Repair success rate
- CV: Information content identical between conditions

**Success Criteria:**
- Structured > Scrambled with p < 0.05
- This isolates structure from information content

**Gate:**
- Type: MUST_WORK
- If Fail: Structure not the driver, reconsider mechanism

**Prerequisites:** H-E1

**Verification Protocol:**
1. Create Scrambled condition: same content as Structured, random section order
2. Run self-repair with both conditions
3. Compare repair success rates
4. If Structured > Scrambled: representational alignment confirmed
5. If Structured = Scrambled: information content drives effect, not structure

---

#### H-M2: Information Preservation Through Transformation

**Type:** MECHANISM
**Statement:** All diagnostic content is retained through format transformation, enabling fair comparison.

**Variables:**
- IV: Format transformation applied
- DV: Information reconstruction accuracy
- CV: Source error content

**Success Criteria:**
- Third-party LLM can reconstruct original error details from structured format with >95% accuracy
- No systematic information loss for any error type

**Gate:**
- Type: SHOULD_WORK
- If Fail: Adjust transformation to preserve information

**Prerequisites:** H-M1

**Verification Protocol:**
1. Apply structured transformation to 100 sample errors
2. Ask separate LLM to reconstruct original error from structured format
3. Measure reconstruction accuracy
4. Check for systematic losses by error type
5. Iterate transformation if accuracy < 95%

---

#### H-M3: Scaffolded Guidance Through Intermediate Fix Specificity

**Type:** MECHANISM
**Statement:** Intermediate-specificity fix hints (Level 1-2) outperform both no hints (Level 0) and exact fixes (Level 3), because they activate relevant model knowledge without bypassing reasoning.

**Variables:**
- IV: Fix Specificity Level (0, 1, 2, 3)
- DV: Repair success rate
- CV: Error format fixed at Structured

**Success Criteria:**
- Level 1 or 2 achieves highest repair success rate
- Inverted-U pattern: Quadratic term significant with peak at Level 1-2

**Gate:**
- Type: SHOULD_WORK
- If Fail: Adjust fix specificity strategy

**Prerequisites:** H-M2

**Verification Protocol:**
1. Fix error format at Structured
2. Vary fix specificity across 4 levels
3. Run self-repair for each level
4. Fit polynomial contrast model
5. Test for significant quadratic term
6. Report optimal level

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Structured > Raw, p < 0.05 | STOP pipeline |
| H-M1 | MUST_WORK | Structured > Scrambled, p < 0.05 | Revise mechanism |
| H-M2 | SHOULD_WORK | Reconstruction accuracy > 95% | Iterate transformation |
| H-M3 | SHOULD_WORK | Quadratic term significant | Adjust strategy |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Existence | H-E1 | 2-3 days |
| Phase 2: Core Mechanism | H-M1 | 2-3 days |
| Phase 3: Information Test | H-M2 | 1-2 days |
| Phase 4: Specificity Test | H-M3 | 2-3 days |

**Total Duration:** 7-11 days

---

## 4. Risk Analysis

### 4.1 Key Risks

| Risk | Probability | Impact | Hypothesis Affected |
|------|-------------|--------|---------------------|
| R1: Information content varies across formats | Medium | High | H-E1, H-M1 |
| R2: Error type distribution imbalanced | Medium | Medium | H-E1 |
| R3: GPT-4 at ceiling for simple errors | Medium | Medium | H-E1, H-M3 |
| R4: Self-repair framework misconfigured | Low | High | All |
| R5: Format preferences model-specific | Medium | Low | H-M1, H-M3 |

### 4.2 Mitigation Strategies

| Risk | Mitigation |
|------|------------|
| R1 | Reconstruction test validates information preservation (H-M2) |
| R2 | Stratified sampling, report distribution, subgroup analysis |
| R3 | Focus on Type/Semantic errors where ceiling not reached |
| R4 | Use published ICLR 2024 framework, reproduce baseline first |
| R5 | Test across 3 model scales, report interactions |

---

## 5. Dependency Graph (DAG)

```
┌───────────────────────────────────────────────────────┐
│                 VERIFICATION DAG                      │
└───────────────────────────────────────────────────────┘

   ┌─────────┐
   │  H-E1   │  [MUST_WORK]
   │Existence│  Structured > Raw
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │  H-M1   │  [MUST_WORK]
   │Alignment│  Structured > Scrambled
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │  H-M2   │  [SHOULD_WORK]
   │Info Test│  Reconstruction > 95%
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │  H-M3   │  [SHOULD_WORK]
   │Scaffold │  Inverted-U pattern
   └─────────┘

Legend:
  → : Hard dependency (must pass)
  [MUST_WORK] : Critical gate
  [SHOULD_WORK] : Optimization gate
```

---

## 6. Timeline (Gantt)

```
Week 1                    Week 2
Day 1  2  3  4  5  6  7  8  9  10 11
├──────────────────────────────────┤
│ H-E1 ████████░░░░░░░░░░░░░░░░░░░░│ (Days 1-3)
│ H-M1 ░░░░░░░░████████░░░░░░░░░░░░│ (Days 4-6)
│ H-M2 ░░░░░░░░░░░░░░░░████░░░░░░░░│ (Days 7-8)
│ H-M3 ░░░░░░░░░░░░░░░░░░░░████████│ (Days 9-11)
├──────────────────────────────────┤
         ▲           ▲
         │           │
      Gate 1      Gate 2
    (H-E1 pass)  (H-M1 pass)

Critical Path: H-E1 → H-M1 → H-M2 → H-M3
```

---

## 7. Dialectical Analysis

### 7.1 Thesis

Structured error formatting improves LLM self-repair by reducing representational gap between compiler output and model training distribution. Intermediate-specificity hints further improve performance by activating relevant knowledge without creating dependency.

### 7.2 Antithesis (H0 Defense)

1. **Information content dominates:** If Scrambled = Structured, then structure adds no value
2. **Length confound:** Longer prompts may simply provide more context, not better format
3. **Model-specific effects:** Format preferences may be learned artifacts of specific training data
4. **Ceiling effects:** GPT-4 may already extract maximum information from any format

### 7.3 Synthesis

The experimental design addresses each antithesis:
- Scrambled condition isolates structure from content
- Verbose-Raw controls for length with unstructured content
- Multi-model testing reveals model-specific vs universal effects
- Error type stratification tests for ceiling effects

### 7.4 Robustness Assessment

| Challenge | Design Response | Confidence |
|-----------|-----------------|------------|
| Information confound | Reconstruction test (H-M2) | High |
| Length confound | Verbose-Raw condition | High |
| Model specificity | 3 model scales tested | Medium |
| Ceiling effects | Focus on Type/Semantic errors | Medium |

---

## 8. Executive Summary

### Key Decisions

1. **4 sub-hypotheses:** H-E1 (existence), H-M1-M3 (mechanism chain)
2. **40% scope reduction:** BUILD_ON claims excluded
3. **Sequential execution:** Linear dependency chain
4. **7-11 day timeline:** Conservative estimate with gate checkpoints

### Critical Path

H-E1 → H-M1 are MUST_WORK gates. If either fails, pipeline stops.

### Success Definition

- H-E1 pass: Structured > Raw (p < 0.05)
- H-M1 pass: Structured > Scrambled (p < 0.05)
- H-M2 pass: Reconstruction > 95%
- H-M3 pass: Inverted-U pattern for fix specificity

### Next Steps

1. Run Phase 2C for detailed experiment design per hypothesis
2. Begin with H-E1 implementation in Phase 3
3. Proceed through gate checkpoints

---

## Appendix: Established Facts (BUILD_ON)

These claims are accepted as pre-validated and require citation only:

1. Self-repair yields minimum +4.9% improvement across all models tested (arXiv:2604.10508)
2. Compiler feedback improves compilation success (44% to 89% in CompCoder)
3. Syntactic/runtime errors are more tractable than logical failures

---

*Generated by Phase 2B Verification Planning Workflow*
*Status: COMPLETE*
*Steps Completed: step-00 through step-10*
