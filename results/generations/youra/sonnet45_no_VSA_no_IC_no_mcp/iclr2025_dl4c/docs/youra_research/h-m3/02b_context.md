# Hypothesis Context: h-m3

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-25
**Main Hypothesis:** Task-Dependent Feedback Orthogonality in Code Generation Alignment
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under code generation tasks, if we train AI feedback model with human annotations as ground truth (supervised learning), then AI-human correlation >0.7 (strong proxy), because supervised learning directly optimizes model to mimic human judgment patterns.

### Type
MECHANISM

### Rationale
Tests whether supervised learning can close the AI-human correlation gap identified in h-e1 (baseline r=0.45-0.52). Validates that direct supervision on human judgments produces stronger alignment than zero-shot or pattern-based approaches. Critical for understanding if AI feedback can serve as reliable human proxy with proper training.

---

## Verification Protocol

### Conceptual Test
1. Collect human annotations on code quality (reuse h-e1 data)
2. Train supervised AI feedback model (regression: code → human score)
3. Measure AI-human correlation on held-out test set
4. Compare to h-e1 baseline (zero-shot AI feedback)

### Success Criteria
- **Primary (MUST_WORK Gate):** Spearman correlation(AI_supervised, human) > 0.7 on test set
- **Secondary:** Statistical significance (p < 0.05)
- **Tertiary:** Improvement over h-e1 baseline (r=0.45-0.52)

### Variables
- **Independent Variable:** Training paradigm (supervised on human labels vs zero-shot)
- **Dependent Variable:** AI-human correlation (Spearman ρ)
- **Controlled Variables:** Same code samples, same human raters, same evaluation protocol as h-e1

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval + MBPP with Human Annotations
- **Type:** standard
- **Source:** OpenAI (HumanEval), Google (MBPP) + human quality annotations
- **Path:** Use h-e1 cached data (`/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets`)
- **Hypothesis Fit:** Same evaluation samples as h-e1 ensure controlled comparison; human annotations provide supervised learning target

### Selected Model
- **Name:** CodeBERT or CodeT5 (supervised fine-tuning)
- **Type:** Pre-trained code encoder fine-tuned for regression
- **Source:** HuggingFace Transformers (microsoft/codebert-base or Salesforce/codet5-base)
- **Hypothesis Fit:** Code-specific encoder captures structural patterns; fine-tuning on human scores directly optimizes for alignment

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For MECHANISM hypotheses like h-m3, baseline context establishes expected improvements.

### Baseline Methods
- **h-e1 Zero-shot AI Feedback:** GPT-3.5-based code quality assessment via prompting
- **h-m1 Supervised Learning (first attempt):** Achieved r=0.65 (below >0.7 target)

### Baseline Performance
- **h-e1 AI-human correlation:** r=0.45 (HumanEval), r=0.52 (MBPP)
- **h-m1 Supervised AI-human correlation:** r=0.65 (improvement but insufficient)

### Gap Analysis
Current gap: 0.05 correlation points below >0.7 gate (h-m1 achieved 0.65)

**Why gap exists (h-m1 reflection):**
- Potential insufficient model capacity
- Limited training data (797 samples may be borderline)
- Possible suboptimal hyperparameters or architecture choice

**h-m3 improvement strategy:**
- Increase model capacity (CodeT5-large vs CodeT5-base)
- Add data augmentation or multi-task learning
- Tune learning rate schedule more carefully
- Consider ensemble or ranking loss instead of regression MSE

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-e1:** VALIDATED (correlation measurement infrastructure working, baseline AI-human r=0.45-0.52)
- **h-m1:** VALIDATED (supervised learning improves over zero-shot, achieved r=0.65)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** 
- Block dependent hypotheses
- Trigger reflection: Why couldn't supervision reach >0.7?
- Possible pivot: Reconsider >0.7 threshold or investigate data quality issues

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 2 weeks (training + evaluation)

---

## Dependency Context

### Relationship to Other Hypotheses

**Sequential Chain Position:**
```
h-e1 (VALIDATED) → h-m1 (VALIDATED) → h-m3 (IN_PROGRESS)
```

**Builds on:**
- **h-e1:** Reuses correlation measurement code, evaluation protocol, human annotations
- **h-m1:** Extends supervised learning approach with improved architecture/training

**Enables (if successful):**
- Downstream hypotheses requiring reliable AI feedback proxy (>0.7 correlation threshold)
- Potential Phase 5 comparison with alternative supervision methods

**If h-m3 fails:**
- Question whether >0.7 is achievable with current data/model setup
- May need to adjust gate threshold or collect more diverse training data

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** experiment_design.status = COMPLETED
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation (h-e1, h-m1 VALIDATED)
3. Dependency information for controlled experiments (reuse h-e1 data)
4. Success criteria for evaluation design (>0.7 correlation, p<0.05)
5. **Baseline comparison targets:** h-e1 r=0.45-0.52, h-m1 r=0.65

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (supervised learning on code quality)
3. Use baseline metrics to set comparison targets (beat h-m1's 0.65, reach >0.7)
4. Design concrete experiment specification (Level 1.5)
5. Output: h-m3/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-M* (Mechanism)**: Baseline (h-e1, h-m1) establishes improvement potential — h-m3 must exceed h-m1's 0.65 and reach >0.7

---

*Optimized for single-hypothesis experiment design*
*Critical: Reuse h-e1 data for controlled comparison*
