# Hypothesis Context: h-m1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-25
**Main Hypothesis:** Task-Dependent Feedback Orthogonality in Code Generation Alignment
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under code generation tasks, if we compare zero-shot AI feedback (prompting) vs supervised AI feedback (trained on human labels), then supervised AI-human correlation will exceed zero-shot by ≥0.2 points, because supervision directly optimizes for human judgment alignment while zero-shot relies on pretrained priors.

### Type
MECHANISM

### Rationale
Tests whether supervised learning improves AI-human alignment beyond zero-shot prompting. Validates that training on human annotations produces measurable improvement in correlation. Foundation for h-m3 which targets >0.7 absolute threshold.

---

## Verification Protocol

### Conceptual Test
1. Collect human annotations on code quality
2. Split: train (70%), val (15%), test (15%)
3. Train supervised AI model on train set
4. Compare test set correlations: zero-shot vs supervised
5. Measure improvement magnitude

### Success Criteria
- **Primary (MUST_WORK Gate):** Supervised AI-human correlation exceeds zero-shot by ≥0.2 points
- **Secondary:** Statistical significance (p < 0.05)
- **Tertiary:** Absolute supervised correlation >0.6

### Variables
- **Independent Variable:** Training paradigm (zero-shot vs supervised)
- **Dependent Variable:** AI-human correlation (Spearman ρ)
- **Controlled Variables:** Same code samples, same human raters, same test set

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Selected Dataset
- **Name:** HumanEval + MBPP with Human Annotations
- **Type:** standard
- **Source:** OpenAI (HumanEval), Google (MBPP) + human quality annotations
- **Path:** Use h-e1 cached data
- **Hypothesis Fit:** Human annotations enable supervised training; reuse h-e1 data for controlled comparison

### Selected Model
- **Name:** CodeBERT (supervised fine-tuning)
- **Type:** Pre-trained code encoder fine-tuned for quality prediction
- **Source:** HuggingFace (microsoft/codebert-base)
- **Hypothesis Fit:** Code encoder captures patterns; regression head predicts human scores

---

## Baseline & Comparison Targets

### Baseline Methods
- **h-e1 Zero-shot AI Feedback:** GPT-3.5 prompted for code quality assessment

### Baseline Performance
- **h-e1 AI-human correlation:** r=0.45 (HumanEval), r=0.52 (MBPP)

### Gap Analysis
Target: Supervised correlation should reach ≥0.65 (0.45 + 0.2 improvement)

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-e1:** VALIDATED (baseline correlation r=0.45-0.52 established)

### Gate Information

**Gate Type:** MUST_WORK

**Consequence if Fails:** 
- Block h-m3
- Reassess whether supervision helps at all

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses

```
h-e1 (VALIDATED) → h-m1 (VALIDATED) → h-m3 (IN_PROGRESS)
```

**Builds on:** h-e1 (reuses data, baseline correlation)
**Enables:** h-m3 (extends to >0.7 target if h-m1 shows supervision works)

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** VALIDATED
**Workflow Status:** ACTIVE

---

*Optimized for single-hypothesis experiment design*
