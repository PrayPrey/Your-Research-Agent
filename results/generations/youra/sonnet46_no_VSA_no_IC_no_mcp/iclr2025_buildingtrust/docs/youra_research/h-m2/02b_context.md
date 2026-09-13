# Hypothesis Context: H-M2

**Generated from:** Phase 2B Verification Plan (JIT by Phase 2C step-01)
**Date:** 2026-08-25
**Main Hypothesis:** H-DeltaECE-v1 — ΔECE as Adversarial Reliability Signal for Open-Weight LLMs
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement

Under adversarial perturbation on AdvGLUE and ANLI splits, if open-weight LLMs are evaluated on label-preserved adversarial examples (H-M1 confirmed), then mean accuracy drops by ≥10 percentage points while mean maximum softmax confidence remains ≥0.70 across ≥60% of (model, task) cells, because adversarial perturbations alter surface features that disrupt model predictions without triggering the model's uncertainty-reduction mechanisms — leaving confidence high while accuracy falls.

### Type

MECHANISM

### Rationale

This mechanism hypothesis tests Step 2 of the causal chain: that the accuracy-confidence gap opens under adversarial stress. This is the direct precondition for elevated ECE — ECE increases mathematically when confidence stays high while accuracy drops. Confirming this gap exists in the specific model-task combinations studied validates the mechanism before measuring its ECE consequence.

---

## Verification Protocol

### Conceptual Test

1. For each (model, task) pair, compute accuracy on clean and adversarial splits; calculate ΔAcc per pair.
2. For adversarial split examples with wrong predictions, extract max softmax confidence values; compute mean confidence.
3. Verify: ΔAcc ≤ −0.10 (10pp drop) for ≥60% of (model, task) cells; mean confidence on wrong adversarial predictions ≥ 0.70.
4. Plot accuracy vs. confidence scatter per (model, task) to visualize the gap opening.
5. Report: ΔAcc per cell, confidence distributions on adversarial misclassifications, cross-model comparison.

### Success Criteria

- Primary: ≥60% of (model, task) cells show ΔAcc ≤ −0.10 with mean adversarial confidence ≥ 0.70 on wrong predictions
- Secondary: Base models (Llama-2-7B-base) show larger confidence-accuracy gap than chat variants

### Variables

- **Independent Variable:** Input perturbation condition (clean vs. adversarial split per H-M1-verified label-preserved pairs)
- **Dependent Variable:** ΔAcc = Accuracy(adversarial) − Accuracy(clean); mean max softmax confidence on adversarial examples with wrong predictions
- **Controlled Variables:** Same lm-evaluation-harness protocol and prompt templates as H-E1; label-preserved examples only (H-M1 filter)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset

- **Name:** AdvGLUE (adversarial GLUE) + ANLI (Adversarial NLI) — with GLUE/MultiNLI clean counterparts
- **Type:** standard (established adversarial NLP benchmarks on HuggingFace)
- **Source:** HuggingFace datasets hub
- **Path:** `adversarial_glue` (HF) / `facebook/anli` (HF); clean: `nyu-mll/glue` (HF) / `multi_nli` (HF)
- **Hypothesis Fit:** AdvGLUE and ANLI are the benchmark adversarial NLP datasets with human-verified label preservation; paired clean splits (GLUE, MultiNLI) provide the accuracy baseline for ΔAcc computation. H-M1 has confirmed label preservation rate = 1.000 — all examples are valid for H-M2 measurement.

### Selected Model

- **Name:** Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-Instruct-v0.1
- **Type:** Open-weight decoder-only transformer (logit-extractable)
- **Source:** meta-llama/Llama-2-7b-hf, meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, mistralai/Mistral-7B-Instruct-v0.1 (HuggingFace)
- **Hypothesis Fit:** Open-weight models allow softmax confidence extraction from logits; base vs. chat comparison tests whether RLHF reduces overconfidence; Mistral provides cross-architecture control.

---

## Baseline & Comparison Targets

### Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Accuracy-based robustness evaluation | 15-30% accuracy drop under adversarial perturbation | AdvGLUE, ANLI |
| Clean-split accuracy (H-E1 results) | ~60-80% clean accuracy for LLMs on MNLI/SNLI-type tasks | GLUE clean splits |
| Max softmax confidence on correct clean examples | ~0.80-0.95 (overconfident) | LLM calibration literature |

### Baseline Performance

From H-E1 validation results:
- ECE_clean (MNLI-style): ~0.279 (established in H-M1 validation)
- AdvGLUE MNLI: ECE_adv = 0.3497, ΔECE = +0.0707

### Gap Analysis

H-M1 confirmed: ΔECE > 0 driven by confidence-accuracy decoupling. H-M2 directly measures the ΔAcc and confidence components that produce this decoupling. Expected: accuracy drops ~10-20pp while confidence stays ≥0.70 on wrong adversarial predictions.

---

## Dependencies and Gate Conditions

### Prerequisites

- H-E1: VALIDATED (PASS) — ECE computation infrastructure confirmed
- H-M1: VALIDATED (PASS) — Label preservation rate = 1.000, ΔECE mechanism confirmed

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues ← **H-M2 gate type**
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** EXPLORE — Document as finding; investigate whether models may be adaptively reducing confidence on adversarial inputs; narrow claim to specific model-task cells where gap exists.

**Phase Assignment:** Phase 2 — Mechanisms

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses

H-M2 is the second step in the three-step causal chain:
- H-E1 → established ECE can be measured (VALIDATED)
- H-M1 → established label preservation makes ΔECE valid (VALIDATED)
- **H-M2** → establishes the accuracy-confidence gap that mechanistically produces elevated ECE
- H-M3 → tests that ΔECE captures this gap quantitatively (downstream)

H-M2 uses the same lm-evaluation-harness runs as H-E1 (no new inference required — only post-hoc extraction of accuracy and confidence from existing H-E1 results files).

---

## Verification State Reference

**State File:** verification_state.yaml (ABLATION MODE — not read/written directly)
**Current Status:** IN_PROGRESS (Phase 2C)
**Workflow Status:** ACTIVE

---

*Optimized for single-hypothesis experiment design*
*JIT-generated by Phase 2C step-01 from 02b_verification_plan.md*
