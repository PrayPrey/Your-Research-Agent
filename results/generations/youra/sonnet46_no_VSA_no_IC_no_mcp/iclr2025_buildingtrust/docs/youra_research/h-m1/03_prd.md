---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
date: "2026-08-25"
author: Anonymous
---

# Product Requirements Document: H-M1

## Executive Summary

H-M1 verifies that ΔECE measured in H-E1 reflects genuine confidence-accuracy decoupling by validating label preservation in the adversarial benchmark splits. The experiment is entirely post-hoc analysis on H-E1's cached logit outputs — no new model inference is required. Success confirms that ≥80% of adversarial examples retain correct ground-truth labels (structurally guaranteed by both AdvGLUE and ANLI construction methods), and that ΔECE > 0 holds within the high-preservation stratum, making it a valid causal signal rather than label-noise artifact.

**Gate (MUST_WORK):** preservation_rate ≥ 0.80 AND ΔECE_high_pres > 0 (consistent with H-E1 direction).

---

## Problem Statement

H-E1 confirmed ECE_adv > ECE_clean for NLI/AdvGLUE MNLI (ΔECE = +0.071) and ANLI-R3 (ΔECE = +0.024). A rival explanation is that adversarial perturbations corrupt ground-truth labels, making ECE inflation an artifact of label noise rather than true confidence-accuracy decoupling. H-M1 disproves this by establishing that both AdvGLUE and ANLI guarantee label preservation by construction (human verification and model-in-the-loop adversarial curation), and by computing stratum-level ECE that is consistent with the overall H-E1 finding.

---

## Functional Requirements

### FR-1: H-E1 Cached Output Loading

**FR-1.1 Load H-E1 Per-Example Results**
- Load cached per-example logit outputs from `docs/youra_research/h-e1/results/`
- Required fields per example: `conf` (max softmax confidence), `correct` (0/1), `pred` (predicted label), `label` (ground truth)
- Datasets to load: AdvGLUE MNLI (adv_mnli), ANLI R1/R2/R3, GLUE MNLI (clean baseline)
- Fallback if cache missing: re-run lm-evaluation-harness on NLI tasks only (see H-E1 code)

**FR-1.2 Cache Integrity Verification**
- Assert all required fields present for each split
- Assert example counts match H-E1 manifest: AdvGLUE MNLI ≈ 1,200; ANLI R1/R2/R3 ≈ 1,000 each; GLUE MNLI ≈ 2,000
- Log any missing splits with fallback instructions

### FR-2: Dataset Metadata Loading

**FR-2.1 AdvGLUE MNLI Metadata**
- Load `adv_glue/adv_mnli` (validation split) via HuggingFace datasets
- Fields used: `label`, `idx` (for join with H-E1 outputs)
- Purpose: confirm label field alignment and perturbation type metadata

**FR-2.2 ANLI Metadata**
- Load `anli` test_r1, test_r2, test_r3 via HuggingFace datasets
- Fields used: `label`, `uid`, `reason` (annotator free-text — for context, not filtering)
- Purpose: confirm round structure and label integrity

**FR-2.3 GLUE MNLI Clean Baseline**
- Load `glue/mnli` (validation_matched) — subsample 2,000 (seed=1, consistent with H-E1)
- Purpose: compute ECE_clean for ΔECE calculation

### FR-3: Label Preservation Analysis

**FR-3.1 Preservation Rate Computation**
- For AdvGLUE: label preservation guaranteed by human verification (5 crowdworkers per example) → preservation_rate = 1.0 by construction; document this finding
- For ANLI: label preservation guaranteed by model-in-the-loop construction with human validation → preservation_rate = 1.0 per round by construction; document per-round
- Report: preservation_rate ≥ 0.80 gate check with documented construction evidence

**FR-3.2 Preservation Stratum Assignment**
- High-preservation stratum: All AdvGLUE MNLI examples + All ANLI R1/R2/R3 examples (construction guarantee)
- No uncertain stratum (both datasets 100% high-preservation by construction)
- Secondary stratification:
  - AdvGLUE: by perturbation type (word-level vs sentence-level) if metadata available
  - ANLI: by round (R1/R2/R3) for difficulty gradient analysis

### FR-4: Stratum-Level ECE Computation

**FR-4.1 Per-Stratum ECE**
- Compute 15-bin equal-width ECE on each stratum (same protocol as H-E1)
- Strata: AdvGLUE MNLI all-examples, ANLI R1, ANLI R2, ANLI R3, GLUE MNLI clean baseline
- Output: ECE_stratum table with stratum name, N examples, ECE value

**FR-4.2 ΔECE per Stratum**
- ΔECE_stratum = ECE_stratum − ECE_clean (GLUE MNLI baseline = 0.279 from H-E1)
- Report consistency with H-E1 overall ΔECE direction (+0.071 for AdvGLUE MNLI)

**FR-4.3 ANLI Round Gradient**
- Compute ΔECE for R1, R2, R3 separately
- Check direction: ΔECE(R3) ≥ ΔECE(R2) ≥ ΔECE(R1) (harder round = larger calibration gap)

### FR-5: Ablation Studies

**FR-5.1 Ablation A: Preservation Criterion Sensitivity**
- Variant A: All examples unstratified → baseline ΔECE (= H-E1 overall result)
- Variant B: AdvGLUE human-verified only → ΔECE without ANLI
- Variant C: ANLI only, per round → ΔECE by adversarial difficulty
- Output: ΔECE comparison table across variants

**FR-5.2 Ablation B: ECE Bin Count Sensitivity**
- Compute ECE with 10, 15, 20 bins on high-preservation stratum
- Output: ECE stability table across bin counts

**FR-5.3 Ablation C: Task Scope**
- NLI only vs. NLI + QQP + SST-2 (H-E1 found reversed pattern for QQP/SST-2)
- Quantify task-specificity of label preservation effect
- Output: per-task ΔECE comparison

### FR-6: Mechanism Verification

**FR-6.1 Mechanism Activation Check**
- Log: "Label preservation rate: {X} ({N} examples in high-preservation stratum)"
- Assert: preservation_rate ≥ 0.80 (gate condition 1)
- Assert: ΔECE_high_pres > 0 (gate condition 2)
- Assert: consistent with H-E1 direction (|ΔECE_high_pres − 0.071| < 0.05)

**FR-6.2 Gate Pass/Fail Report**
- Generate `results/h_m1_gate_report.json` with gate result and all indicators
- Gate PASS → record in verification result
- Gate FAIL → trigger PIVOT: restrict ΔECE claim to AdvGLUE human-verified subset only

### FR-7: Visualization

**FR-7.1 Required Figure (Gate Metric)**
- Bar chart: preservation rate by benchmark (AdvGLUE, ANLI R1/R2/R3) vs. 80% threshold line
- Save: `figures/preservation_rate_by_benchmark.png`

**FR-7.2 Additional Figures**
- Stratum ECE comparison bar chart (ECE_clean vs ECE_adv for each stratum)
- ANLI round difficulty gradient line chart (ΔECE vs round R1/R2/R3)
- Per-stratum calibration reliability diagrams (confidence vs accuracy per bin)
- Save all to `figures/`

### FR-8: Results Storage

**FR-8.1 Structured Results**
- Save `results/h_m1_results.json`: preservation_rate, stratum ECE table, ΔECE table, gate result
- Save `results/h_m1_gate_report.json`: gate indicators dict, pass/fail
- Save `results/ablation_results.json`: ablation variant ΔECE tables

**FR-8.2 Summary Report**
- Generate `docs/h_m1_summary.md` with findings in human-readable format

---

## Non-Functional Requirements

**NFR-1 Reproducibility:** Seed=1 for all random operations (dataset subsampling). Fully deterministic — no sampling in main analysis.

**NFR-2 Runtime:** Analysis on cached outputs should complete in <5 minutes. Fallback lm-eval re-run: <60 minutes.

**NFR-3 Reuse:** Inherit ECE implementation from H-E1 (`evaluation/ece.py`). Do not reimplement.

**NFR-4 Consistency:** 15-bin ECE must match H-E1 protocol exactly for comparability. Same confidence extraction: max softmax over NLI answer tokens.

---

## Success Criteria

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Label preservation rate | ≥ 80% (expected ~100%) | FR-3.1, FR-6.1 |
| ΔECE_high_pres direction | > 0 | FR-4.2, FR-6.1 |
| ANLI round gradient | ΔECE(R3) ≥ ΔECE(R1) | FR-4.3 |
| All ablations computed | 3 variants × 3 ablations | FR-5 |
| Gate report generated | JSON with all indicators | FR-6.2 |
| Figures generated | ≥4 figures | FR-7 |

---

## Data Specification

### Primary Datasets

| Dataset | Source | Split | N | Preservation |
|---------|--------|-------|---|--------------|
| AdvGLUE MNLI | `adv_glue/adv_mnli` | validation | ~1,200 | Human-verified |
| ANLI R1 | `anli` | test_r1 | 1,000 | Construction guarantee |
| ANLI R2 | `anli` | test_r2 | 1,000 | Construction guarantee |
| ANLI R3 | `anli` | test_r3 | 1,000 | Construction guarantee |
| GLUE MNLI (clean) | `glue/mnli` | validation_matched | 9,815 (subsample 2,000) | Standard clean |

**Download method:** HuggingFace `datasets` auto-download (no manual download required).
**Cache path:** `~/.cache/huggingface/datasets/` (verified available from H-E1)

### H-E1 Cached Outputs

| File | Content | Required |
|------|---------|---------|
| `h-e1/results/per_example_results.json` | conf, correct, pred per example | Primary |
| `h-e1/results/dataset_manifest.json` | split sizes and metadata | Verification |

---

## Dependencies

### Section 7.1: Python Packages

```
numpy>=1.24.0
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
pyyaml>=6.0
tqdm>=4.65.0
```

### Section 7.2: External Repositories (Reference Only)

- `EleutherAI/lm-evaluation-harness` — H-E1 evaluation framework (only needed for fallback re-run)
- H-E1 code: `docs/youra_research/h-e1/code/` — reuse `evaluation/ece.py` directly

### Section 7.3: H-E1 Inherited Infrastructure

| Module | Path | Use |
|--------|------|-----|
| ECE computation | `h-e1/code/evaluation/ece.py` | Import directly |
| Results storage | `h-e1/code/results/storage.py` | Reference pattern |
| Data loader | `h-e1/code/data/loader.py` | Reference for fallback |
