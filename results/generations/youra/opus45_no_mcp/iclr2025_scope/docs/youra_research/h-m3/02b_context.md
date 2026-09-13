# Phase 2B Context: H-M3

**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Title:** LoRA Adaptation Efficiency Depends on Landscape Geometry

---

## Hypothesis Statement

Under LoRA fine-tuning on fixed architecture, if loss landscape has lower sharpness, then adaptation achieves better generalization with lower effective rank because flatter minima enable more efficient low-rank approximation.

---

## Gate Condition

**Type:** MUST_WORK
**Pass Condition:** Spearman correlation rho > 0.5 between sharpness and effective rank
**Secondary:** Lower sharpness correlates with smaller generalization gap
**Fail Action:** EXPLORE alternative landscape metrics

---

## Prerequisites

| Prerequisite | Status | Key Results |
|--------------|--------|-------------|
| H-M2 | VALIDATED | Sharpness ratio 0.65 (seq/ret), sequential tasks show 35% lower sharpness |

---

## Variables

**Independent:**
- Landscape sharpness (measured via SAM perturbation)

**Dependent:**
- LoRA effective rank (SVD, 90% energy threshold)
- Generalization gap (train accuracy - test accuracy)

**Controlled:**
- LoRA hyperparameters (rank=16, alpha=32)
- Training duration (convergence)
- Architecture (Mamba with LoRA)

---

## Verification Protocol

1. Categorize tasks by measured sharpness (from H-M2 results)
2. Apply LoRA adaptation to convergence on each task
3. Compute LoRA effective rank via SVD (90% energy threshold)
4. Measure generalization gap (training accuracy - test accuracy)
5. Compute Spearman correlation between sharpness and effective rank

---

## Success Criteria

**Primary (PoC):**
- Spearman correlation rho > 0.5 between sharpness and effective rank

**Secondary:**
- Lower sharpness correlates with smaller generalization gap

---

## Datasets

| Dataset | Task Type | Sharpness (H-M2) | Test Size |
|---------|-----------|------------------|-----------|
| GSM8K | Sequential | 1.512 | 1,319 |
| Natural Questions | Retrieval | 2.326 | 3,610 |

---

## Model Configuration

| Parameter | Value |
|-----------|-------|
| Architecture | Mamba with LoRA |
| Model Dimension | 512 |
| State Dimension | 16 |
| Layers | 4 |
| LoRA Rank | 16 |
| LoRA Alpha | 32 |

---

## Previous Hypothesis Results

**H-M2 Key Findings:**
- Sequential tasks (GSM8K): sharpness = 1.512
- Retrieval tasks (NQ): sharpness = 2.326
- Sharpness ratio = 0.65 (< 0.8 threshold)
- Sequential tasks exhibit 35% lower sharpness

**Implications for H-M3:**
- Use H-M2 sharpness measurements as input
- Expect lower effective rank for GSM8K (lower sharpness)
- Expect smaller generalization gap for GSM8K

---

*Generated for Phase 2C Experiment Design*
*Date: 2026-08-19*
