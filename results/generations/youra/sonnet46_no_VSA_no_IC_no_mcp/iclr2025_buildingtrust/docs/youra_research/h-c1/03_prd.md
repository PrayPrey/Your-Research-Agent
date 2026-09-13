---
title: "PRD: h-c1 — RLHF Calibration Moderation Experiment"
hypothesis_id: h-c1
hypothesis_type: CONDITION
date: 2026-08-25
author: yoon303@ust.ac.kr
phase: 3
stepsCompleted: [prd]
---

# Product Requirements Document: h-c1
## RLHF Alignment as Moderator of Adversarial Calibration Degradation

---

## 1. Executive Summary

This experiment tests whether RLHF alignment moderates calibration degradation under adversarial NLP inputs. Specifically, it compares ΔECE (ECE_adversarial − ECE_clean) between Llama-2-7B-base (no RLHF) and Llama-2-7B-chat (RLHF-aligned) across the same adversarial benchmark pairs established in H-E1 and H-M1.

**Core claim:** RLHF-aligned models exhibit significantly lower ΔECE than their base counterparts, confirming that RLHF training calibrates confidence expression to reduce the overconfidence pattern that drives ΔECE > 0 under adversarial perturbation.

**Hypothesis type:** CONDITION (SHOULD_WORK gate)
**Prerequisites:** H-E1 (PASS), H-M1 (PASS)
**Reuse rate:** ~70% — this experiment reuses H-E1 infrastructure; only chat model evaluation is new

---

## 2. Problem Statement

H-E1 confirmed that adversarial NLP inputs increase ECE for Llama-2-7B-base on NLI tasks (ΔECE_base = +0.071 for AdvGLUE MNLI). H-M1 confirmed this degradation is driven by confidence-accuracy decoupling (overconfidence). H-C1 asks: does RLHF alignment suppress this overconfidence mechanism?

**Testable prediction:** ΔECE_chat < ΔECE_base on ≥60% of (task, split) cells.

---

## 3. Functional Requirements

### FR-1: Model Evaluation — Llama-2-7B-base (Baseline)
- **FR-1.1:** Load `meta-llama/Llama-2-7b-hf` in float16 with `device_map="auto"`
- **FR-1.2:** Evaluate on GLUE MNLI (clean, 1,000 examples) → extract answer-token logits → compute ECE_base_clean
- **FR-1.3:** Evaluate on AdvGLUE MNLI (adversarial, validation split) → compute ECE_base_adv
- **FR-1.4:** Evaluate on MultiNLI (clean, 1,000 examples) → compute ECE_base_clean_anli
- **FR-1.5:** Evaluate on ANLI R1, R2, R3 (test splits, 1,000 each) → compute ECE_base_adv_R1/R2/R3
- **FR-1.6:** Compute ΔECE_base per (task, split) cell: ΔECE = ECE_adv − ECE_clean
- **Note:** ΔECE_base values from H-E1 may be reused if available; skip recomputation if cache hit

### FR-2: Model Evaluation — Llama-2-7B-chat (RLHF-Aligned)
- **FR-2.1:** Load `meta-llama/Llama-2-7b-chat-hf` in float16 with `device_map="auto"`
- **FR-2.2:** Apply same prompt templates and MCQ format as H-E1 (identical controlled conditions)
- **FR-2.3:** Evaluate on same dataset splits as FR-1.2–FR-1.5
- **FR-2.4:** Compute ECE_chat_clean and ECE_chat_adv for each (task, split) cell
- **FR-2.5:** Compute ΔECE_chat per cell: ΔECE_chat = ECE_chat_adv − ECE_chat_clean

### FR-3: Paired Comparison and Gate Metrics
- **FR-3.1:** Implement `compare_rlhf_moderation(base_results, chat_results)` → ΔΔECE = ΔECE_base − ΔECE_chat per cell
- **FR-3.2:** Compute moderation_rate = fraction of cells where ΔECE_chat < ΔECE_base
- **FR-3.3:** Implement `verify_rlhf_moderation_activated(base_results, chat_results)` → 4 indicator checks
- **FR-3.4:** Apply label-preservation filter from H-M1 (rate ≥ 0.80 per cell; confirmed 1.000 for AdvGLUE)
- **FR-3.5:** Gate evaluation: moderation_rate ≥ 0.60 AND ΔΔECE > 0.01 on NLI cell → CONFIRMED

### FR-4: ECE Computation
- **FR-4.1:** 15-bin equal-width ECE (Guo 2017 standard, inherited from H-E1)
- **FR-4.2:** Confidence = max softmax over answer tokens (entailment/neutral/contradiction)
- **FR-4.3:** Support both torchmetrics (`MulticlassCalibrationError`) and custom implementation
- **FR-4.4:** Min samples per cell: 200; max samples: 1,000

### FR-5: Visualization
- **FR-5.1 (Mandatory):** Paired bar chart — ΔECE_base vs ΔECE_chat across all (task, split) cells
- **FR-5.2:** ECE reliability diagrams (2×2 grid: base vs chat, clean vs adversarial) for NLI task
- **FR-5.3:** ΔΔECE scatter plot (ΔECE_chat vs ΔECE_base per cell with identity line)
- **FR-5.4:** ANLI gradient comparison (ΔECE by R1→R3 for base vs chat)
- All figures saved to `docs/youra_research/h-c1/figures/`

### FR-6: Result Persistence
- **FR-6.1:** Save per-cell results to `docs/youra_research/h-c1/results/hc1_results.json`
- **FR-6.2:** Save validation report to `docs/youra_research/h-c1/04_validation.md`
- **FR-6.3:** Log mechanism activation indicators per cell

---

## 4. Data Specification

### 4.1 Adversarial Splits (Evaluation Targets)

| Dataset | HF Identifier | Split | Task | N | Role |
|---------|---------------|-------|------|---|------|
| AdvGLUE MNLI | `adv_glue` / `adv_glue_mnli` | validation | NLI-3way | ~1,000 | adversarial |
| ANLI R1 | `allenai/anli` | test_r1 | NLI-3way | 1,000 | adversarial |
| ANLI R2 | `allenai/anli` | test_r2 | NLI-3way | 1,000 | adversarial |
| ANLI R3 | `allenai/anli` | test_r3 | NLI-3way | 1,000 | adversarial |

### 4.2 Clean Counterparts (Baselines)

| Dataset | HF Identifier | Split | Task | N | Role |
|---------|---------------|-------|------|---|------|
| GLUE MNLI | `glue` / `mnli` | validation_matched | NLI-3way | 1,000 (subsample) | clean |
| MultiNLI | `multi_nli` | validation_matched | NLI-3way | 1,000 (subsample) | clean |

**Loading:**
```python
from datasets import load_dataset
adv_glue = load_dataset("adv_glue", "adv_glue_mnli")
glue_mnli = load_dataset("glue", "mnli", split="validation_matched").select(range(1000))
anli = {f"r{i}": load_dataset("allenai/anli", split=f"test_r{i}") for i in [1,2,3]}
multi_nli = load_dataset("multi_nli", split="validation_matched").select(range(1000))
```

**Download status:** All datasets auto-download via HuggingFace datasets library. No manual download required. ✓

### 4.3 Evaluation Cells

| Cell ID | Clean Split | Adversarial Split | Task |
|---------|-------------|-------------------|------|
| NLI-AdvGLUE | GLUE MNLI | AdvGLUE MNLI | NLI |
| NLI-ANLI-R1 | MultiNLI | ANLI R1 | NLI |
| NLI-ANLI-R2 | MultiNLI | ANLI R2 | NLI |
| NLI-ANLI-R3 | MultiNLI | ANLI R3 | NLI |

Total cells: 4 × 2 models = 8 evaluation runs

---

## 5. Non-Functional Requirements

- **NFR-1:** GPU memory ≤ 40GB (float16; single Llama-2-7B fits on one A100)
- **NFR-2:** Total wall-clock time ≤ 4 hours (sequential base + chat evaluation)
- **NFR-3:** Deterministic results (seed=1; evaluation is deterministic given fixed model)
- **NFR-4:** Reproducible via single script: `python evaluate_hc1.py`
- **NFR-5:** Results must match H-E1 base ECE values within ±0.005 (consistency check)

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Code runs without error | Both models evaluated | PoC |
| moderation_rate ≥ 0.60 | ≥60% of cells: ΔECE_chat < ΔECE_base | Gate (SHOULD_WORK) |
| ΔΔECE_NLI > 0.01 | NLI/AdvGLUE cell shows substantive moderation | Secondary |
| H-E1 consistency | Base ECE values within ±0.005 of H-E1 reported values | Sanity |

**Gate type:** SHOULD_WORK — failure documented as EXPLORE finding, not pipeline blocker.

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
numpy>=1.24.0
matplotlib>=3.7.0
torchmetrics>=1.0.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External Repositories / Reference

- EleutherAI/lm-evaluation-harness (reference implementation; may use directly or adapt)
- H-E1 results: `docs/youra_research/h-e1/04_validation.md` (ΔECE_base values)
- H-M1 results: `docs/youra_research/h-m1/04_validation.md` (label-preservation rates)

### 7.3 Model Artifacts

| Model | HF ID | Cache | Status |
|-------|-------|-------|--------|
| Llama-2-7B-base | meta-llama/Llama-2-7b-hf | `~/.cache/huggingface/hub/models--meta-llama--Llama-2-7b-hf` | ✅ Verified (H-E1) |
| Llama-2-7B-chat | meta-llama/Llama-2-7b-chat-hf | `~/.cache/huggingface/hub/models--meta-llama--Llama-2-7b-chat-hf` | ⚠️ May need download |

---

## 8. Out of Scope

- Training or fine-tuning any model
- Evaluating models beyond Llama-2-7B pair
- QQP or SST-2 tasks (NLI only — focused on where H-E1 showed signal)
- Temperature scaling or post-hoc calibration correction
- Any new model architectures

---

## Applied: Hypothesis CONDITION Template
## Applied: H-E1 Infrastructure Reuse Pattern
