# Phase 2B Context: H-M1 (Annotation Consistency)

**Generated from:** 02b_verification_plan.md  
**Date:** 2026-04-19

---

## Hypothesis Information

**ID:** h-m1  
**Type:** MECHANISM (Step 1)  
**Prerequisites:** h-e1

**Statement:**  
Under controlled annotation conditions, if human annotators evaluate response pairs using HH-RLHF harmlessness criteria, then inter-annotator agreement will be substantial (κ ≥ 0.70) and align with original HH-RLHF labels (≥75% agreement), because explicit criteria reduce subjective variation in violation detection.

**Rationale:**  
Validates that human judgment process produces consistent signal. Low agreement would indicate label noise undermines downstream geometric analysis.

---

## Variables

**Independent:**
- Annotation protocol (explicit criteria vs intuitive judgment)

**Dependent:**
- Inter-annotator agreement (Cohen's κ)
- Alignment with HH-RLHF (proportion)

**Controlled:**
- Annotator training
- Sample selection (stratified by violation type)

---

## Verification Protocol

1. Recruit 3 annotators and provide HH-RLHF annotation guidelines training
2. Sample 300 response pairs from HH-RLHF harmless subset (100 per violation type)
3. Collect independent annotations for chosen/rejected classification
4. Compute Cohen's κ across annotators and proportion agreement with original labels
5. Test against H0: κ < 0.60 vs H1: κ ≥ 0.70

---

## Success Criteria

**Primary:** Cohen's κ ≥ 0.70 across annotators  
**Secondary:** ≥75% agreement with original HH-RLHF labels

**Gate:** SHOULD_WORK  
**Failure Response:** If κ < 0.60, EXPLORE refined criteria or PIVOT to expert-only annotation subset

---

## Experimental Setup

**Dataset:** HH-RLHF harmless subset
- **Source:** Anthropic (publicly available)
- **Path:** https://huggingface.co/datasets/Anthropic/hh-rlhf
- **Hypothesis Fit:** Contains 160K+ validated chosen/rejected pairs with explicit harmlessness annotations
- **Sample Size:** 300 response pairs (stratified by violation type)

**Model:** N/A (human annotation study)
- **Type:** Human annotation protocol
- **Hypothesis Fit:** Tests consistency of human judgment using explicit criteria

**Baselines:**
1. Original HH-RLHF labels (ground truth comparison)
2. Random agreement baseline (κ = 0)

---

## Dependencies

**Prerequisite:** h-e1 (COMPLETED - base-rate validation passed)
- h-e1 Result: 45.6% genuine violations (p=0.0063), κ=0.498 (fair agreement)
- Implication: Sufficient genuine violations exist to test annotation consistency

---

## Source

Phase 2A Causal Step 1 - Phase 2B Section 2
