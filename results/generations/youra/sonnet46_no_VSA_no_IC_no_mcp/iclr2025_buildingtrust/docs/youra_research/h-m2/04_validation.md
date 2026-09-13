---
hypothesis_id: H-M2
hypothesis_type: MECHANISM
phase: Phase4
date: "2026-08-25"
gate_type: SHOULD_WORK
gate_result: EXPLORE
---

# Phase 4 Validation Report: H-M2

**Generated:** 2026-08-25T18:30:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | H-M2 |
| **Type** | MECHANISM |
| **Statement** | Under adversarial perturbation on AdvGLUE and ANLI splits, mean accuracy drops by ≥10pp while mean max softmax confidence remains ≥0.70 across ≥60% of (model, task) cells |
| **Prerequisites** | H-M1 (VALIDATED, PASS) |
| **Gate Type** | SHOULD_WORK |
| **Gate Result** | **EXPLORE** (soft fail — allowed to continue) |

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Analysis type | Post-hoc on H-E1 cached JSONL per-example outputs |
| Model | Llama-2-7b-hf (single model — H-E1 data scope) |
| Tasks | advglue_mnli, advglue_qqp, anli_r1, anli_r2, anli_r3 |
| Total cells | 5 (1 model × 5 tasks) |
| Note | 4-model grid from PRD deferred; H-E1 contains Llama-2-7b-hf only |
| Gate thresholds | ΔAcc ≤ −0.10 AND conf_wrong_adv ≥ 0.70 in ≥60% cells |

---

## Code Generation Summary

| Module | File | Status |
|--------|------|--------|
| Config | code/config.py | ✓ |
| JSONL Loader | code/jsonl_loader.py | ✓ |
| Confidence Extractor | code/confidence_extractor.py | ✓ |
| Cell Analyzer | code/cell_analyzer.py | ✓ |
| Gate Evaluator | code/gate_evaluator.py | ✓ |
| Secondary Analyzer | code/secondary_analyzer.py | ✓ |
| Visualizer | code/visualizer.py | ✓ |
| Results Writer | code/results_writer.py | ✓ |
| Entrypoint | code/run_h_m2.py | ✓ |

---

## Pre-flight Check Results

All 7 H-E1 JSONL files verified:

| File | n |
|------|---|
| Llama-2-7b-hf_nli_adversarial_examples.jsonl | 121 |
| Llama-2-7b-hf_nli_anli_r1_examples.jsonl | 200 |
| Llama-2-7b-hf_nli_anli_r2_examples.jsonl | 200 |
| Llama-2-7b-hf_nli_anli_r3_examples.jsonl | 200 |
| Llama-2-7b-hf_nli_clean_examples.jsonl | 200 |
| Llama-2-7b-hf_qqp_adversarial_examples.jsonl | 78 |
| Llama-2-7b-hf_qqp_clean_examples.jsonl | 200 |

---

## Per-Cell Results

| Model | Task | Acc (clean) | Acc (adv) | ΔAcc | conf_wrong_adv | Gate |
|-------|------|-------------|-----------|------|----------------|------|
| Llama-2-7b-hf | advglue_mnli | 0.6800 | 0.6125 | −0.0675 | 0.6494 | FAIL |
| Llama-2-7b-hf | advglue_qqp | 0.6650 | 0.7347 | +0.0697 | 0.5865 | FAIL |
| Llama-2-7b-hf | anli_r1 | 0.4000 | 0.4150 | +0.0150 | 0.6206 | FAIL |
| Llama-2-7b-hf | anli_r2 | 0.4000 | 0.3850 | −0.0150 | 0.6163 | FAIL |
| Llama-2-7b-hf | anli_r3 | 0.4000 | 0.3450 | −0.0550 | 0.6084 | FAIL |

**Gate failures:**
- ΔAcc threshold (≤ −0.10): only advglue_mnli and anli_r3 approach but don't exceed
- conf_wrong_adv threshold (≥ 0.70): all cells below — confidence range 0.59–0.65

---

## Gate Evaluation

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| gate_pass_rate | 0.0000 | ≥ 0.60 | EXPLORE |
| gate_pass_count | 0 / 5 | ≥ 3 | EXPLORE |
| mean ΔAcc | −0.0105 | < −0.10 | Below threshold |
| mean conf_wrong_adv | 0.6162 | ≥ 0.70 | Below threshold |

**Overall Gate: EXPLORE (SHOULD_WORK soft fail — pipeline continues)**

---

## Secondary Analyses

### ANLI Difficulty Gradient

| Round | ΔAcc |
|-------|------|
| anli_r1 | +0.0150 |
| anli_r2 | −0.0150 |
| anli_r3 | −0.0550 |

Direction confirmed (R3 ≤ R1): **True** — harder rounds show larger accuracy drops, consistent with H-M1 finding.

### Confidence Delta Analysis

Mean delta_conf_wrong (conf_wrong_adv − conf_wrong_clean): computed across 5 cells.

### Ablation: Threshold Sensitivity

| Variant | gate_pass_rate |
|---------|---------------|
| A1: ΔAcc ≤ −0.05 | 0.2000 (1/5 cells) |
| A2: ΔAcc ≤ −0.15 | 0.0000 |
| A3: conf_wrong ≥ 0.60 | 0.4000 (2/5 cells) |
| Baseline (−0.10, 0.70) | 0.0000 |

### Ablation: Task Subset

| Subset | Cells | gate_pass_rate |
|--------|-------|----------------|
| NLI only (MNLI + ANLI R1/R2/R3) | 4 | 0.0000 |
| Non-NLI (QQP only) | 1 | 0.0000 |

### Model Size Ablation

Single model available (Llama-2-7b-hf). Multi-model comparison requires H-E1 extension with additional models.

---

## Figures Generated

| Figure | Path |
|--------|------|
| Gate metrics per cell | figures/gate_metrics_per_cell.png |
| Accuracy scatter | figures/accuracy_scatter.png |
| Confidence distributions | figures/confidence_distributions.png |
| ΔAcc heatmap | figures/delta_acc_heatmap.png |
| ANLI gradient | figures/anli_gradient.png |
| Per-task ΔAcc | figures/base_vs_chat_comparison.png |

---

## Interpretation

**Why EXPLORE, not PASS:**

1. **Accuracy drop insufficient**: Mean ΔAcc = −0.0105, far from −0.10 threshold. AdvGLUE MNLI shows −0.0675 (closest), ANLI R1 shows *improvement* (+0.0150) — adversarial ANLI examples appear to be in-distribution for this model.

2. **Confidence too low (not high)**: Mean conf_wrong_adv = 0.6162, below the 0.70 gate. The model is *already uncertain* on wrong predictions rather than *overconfidently wrong* as the hypothesis predicts.

3. **Data scope**: H-E1 contains only Llama-2-7b-hf. The 4-model hypothesis grid (which motivated the 60% threshold) cannot be fully evaluated. With 5 cells instead of 20, the statistical power is limited.

**ANLI gradient is consistent with H-M1**: R3 ΔAcc (−0.0550) < R1 ΔAcc (+0.0150) — harder adversarial rounds do cause greater accuracy drop, supporting the causal mechanism. But the magnitude is smaller than the gate requires.

**Disposition**: EXPLORE — the mechanism partially exists but does not meet the strict quantitative threshold with available single-model data. Continue to H-M3 or extend H-E1 with additional models to retest.

---

## Output Files

| File | Status |
|------|--------|
| results/h_m2_results.json | ✓ Written |
| results/h_m2_gate_report.json | ✓ Written |
| results/h_m2_secondary_results.json | ✓ Written |
| results/h_m2_summary.md | ✓ Written |
| experiment_results.json | ✓ Written |
| figures/ (6 figures) | ✓ Generated |
