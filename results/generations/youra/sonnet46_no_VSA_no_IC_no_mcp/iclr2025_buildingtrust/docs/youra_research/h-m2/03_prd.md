---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: H-M2
hypothesis_type: MECHANISM
tier: FULL
date: "2026-08-25"
author: Anonymous
---

# Product Requirements Document: H-M2

## Executive Summary

H-M2 decomposes the ECE increase confirmed in H-E1 and H-M1 into its two constituent signals: **accuracy drop** and **confidence maintenance** under adversarial perturbation. The experiment is entirely post-hoc analysis on existing H-E1 lm-evaluation-harness JSONL result files — no new model inference required. Success confirms that ≥60% of (model, task) cells show ΔAcc ≤ −0.10 **AND** mean max softmax confidence on wrong adversarial predictions ≥ 0.70, establishing confidence-accuracy decoupling as the causal mechanism behind ΔECE > 0.

**Gate (SHOULD_WORK):** gate_pass_rate ≥ 0.60 — failure allows continuation as EXPLORE finding.

---

## Problem Statement

H-E1 confirmed ECE_adv > ECE_clean (ΔECE = +0.0707 for AdvGLUE MNLI; confirmed across ANLI rounds). H-M1 confirmed label preservation = 1.000 by construction, ruling out label-noise as the driver. H-M2 now measures the two components that produce ΔECE > 0: (1) accuracy drops under adversarial perturbation, and (2) model confidence remaining high even on wrong adversarial predictions. If both hold simultaneously in ≥60% of (model, task) cells, confidence-accuracy decoupling is confirmed as the causal mechanism.

---

## Functional Requirements

### FR-1: H-E1 Result File Loading

**FR-1.1 Locate and Load JSONL Files**
- Locate H-E1 lm-evaluation-harness per-example JSONL outputs in `docs/youra_research/h-e1/results/`
- Required files: `{model}_{task}_{split}.jsonl` for all 4 models × 5 tasks × 2 splits = 40 files
- Required JSONL fields per example: `resps` (list of log-likelihoods per answer choice), `target` (correct answer index), `acc`
- Fail early with clear error if any JSONL file missing: "H-E1 --log_samples results not found at {path}. Re-run H-E1 with --log_samples flag."

**FR-1.2 JSONL Format Handling**
- Parse `resps` field: `log_likelihoods = [r[0] for r in item["resps"]]` (one scalar per answer choice)
- Apply softmax: `probs = softmax(log_likelihoods)` using `scipy.special.softmax`
- Extract: `pred_idx = np.argmax(probs)`, `max_conf = float(probs[pred_idx])`, `is_correct = (pred_idx == item["target"])`

**FR-1.3 Integrity Check**
- Assert ≥200 examples per JSONL file (H-E1 guarantee)
- Log degenerate logit warning if `std(probs) < 0.01` for any example
- Report file sizes and example counts in pre-flight check

### FR-2: Per-Cell Accuracy and Confidence Extraction

**FR-2.1 Cell Definition**
- Cells: 4 models × 5 tasks = 20 cells
  - Models: Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-Instruct-v0.1
  - Tasks: AdvGLUE-MNLI, AdvGLUE-QQP, ANLI-R1, ANLI-R2, ANLI-R3

**FR-2.2 Per-Cell Statistics**
For each (model, task) cell, compute from BOTH clean and adversarial splits:
- `accuracy`: mean(is_correct) over all examples
- `mean_conf_wrong`: mean(max_conf for wrong predictions)
- `mean_conf_correct`: mean(max_conf for correct predictions)
- `n_wrong`: count of wrong predictions
- `n_total`: total examples

**FR-2.3 Delta Computation**
- `delta_acc = accuracy_adversarial - accuracy_clean` (negative = accuracy drop)
- `conf_wrong_adv`: mean_conf_wrong from adversarial split

### FR-3: Gate Evaluation

**FR-3.1 Per-Cell Gate Check**
For each (model, task) cell:
- `cell_pass = (delta_acc <= -0.10) AND (conf_wrong_adv >= 0.70)`

**FR-3.2 Global Gate**
- `gate_pass_count = sum(cell_pass for all 20 cells)`
- `gate_pass_rate = gate_pass_count / 20`
- H-M2 PASS if `gate_pass_rate >= 0.60` (≥12 of 20 cells)

**FR-3.3 Gate Report Generation**
- Generate `results/h_m2_gate_report.json` with:
  - `gate_pass_rate`, `gate_pass_count`, `total_cells`
  - `passed_cells`: list of (model, task) pairs that passed
  - `failed_cells`: list with failure reason ("delta_acc", "conf_wrong", "both")
  - `overall_result`: "PASS" or "EXPLORE"

### FR-4: Secondary Analyses

**FR-4.1 Mean Aggregates**
- `mean_delta_acc`: mean(delta_acc) across all 20 cells
- `mean_conf_wrong_adv`: mean(conf_wrong_adv) across all 20 cells
- `mean_conf_correct_adv`: mean(mean_conf_correct) for adversarial split across cells

**FR-4.2 Base vs Chat Comparison**
- Compare ΔAcc: Llama-2-7B-base vs Llama-2-7B-chat (same architecture, different tuning)
- Hypothesis: base model shows larger accuracy drop (less robust to adversarial examples)
- Report: ΔAcc_base vs ΔAcc_chat per task, averaged across tasks

**FR-4.3 ANLI Difficulty Gradient**
- Compute mean ΔAcc per ANLI round: R1, R2, R3 averaged across 4 models
- Check direction: ΔAcc(R3) ≤ ΔAcc(R1) — harder rounds → larger accuracy drop
- Report: direction confirmed or not

**FR-4.4 Confidence Change Under Adversarial Stress**
- `delta_conf_wrong = conf_wrong_adv - conf_wrong_clean` per cell
- Positive = confidence on wrong predictions INCREASED under adversarial stress
- Report: mean delta_conf_wrong across cells

### FR-5: Ablation Studies

**FR-5.1 Ablation A: Threshold Sensitivity**
- Variant A1: ΔAcc threshold at −0.05 (looser) → new gate_pass_rate
- Variant A2: ΔAcc threshold at −0.15 (stricter) → new gate_pass_rate
- Variant A3: conf_wrong threshold at 0.60 (looser) → new gate_pass_rate
- Purpose: test robustness of gate condition selection

**FR-5.2 Ablation B: Task Subset Analysis**
- NLI-only cells (AdvGLUE-MNLI + ANLI R1/R2/R3): 4 × 4 = 16 cells
- Non-NLI cells (AdvGLUE-QQP only): 4 × 1 = 4 cells
- Purpose: confirm NLI tasks drive the signal (H-E1 found QQP had different pattern)

**FR-5.3 Ablation C: Model Size Effect**
- 7B models (Llama-2-7B-base, Llama-2-7B-chat, Mistral-7B) vs 13B (Llama-2-13B-chat)
- Compare mean ΔAcc and mean conf_wrong_adv by size
- Purpose: test whether larger models are more or less susceptible to accuracy-confidence decoupling

### FR-6: Mechanism Activation Verification

**FR-6.1 Activation Indicators**
- Log: `"ΔAcc for cell {model}_{task}: {value:.4f}"` for all 20 cells
- Log: `"conf_wrong_adv for cell {model}_{task}: {value:.4f}"` for all 20 cells
- Log: `"gate_pass_rate: {value:.4f} ({'PASS' if value >= 0.60 else 'EXPLORE'})"` at end

**FR-6.2 Failure Detection**
| Failure Mode | Detection | Action |
|---|---|---|
| Missing JSONL | `Path(results_path).exists()` | FAIL EARLY with path info |
| Degenerate logits | `std(probs) < 0.01` | WARN per cell |
| Low conf_wrong_adv < 0.50 | gate dim fails | EXPLORE: "Adaptive uncertainty present" |
| Small ΔAcc > −0.05 | gate dim fails | EXPLORE: "Task-level robustness present" |
| gate_rate < 0.60 | overall gate fails | EXPLORE: soft fail, continue to H-M3 |

### FR-7: Visualization

**FR-7.1 Required Figure (Gate Metric)**
- Bar chart with grouped bars: ΔAcc and conf_wrong_adv per (model, task) cell vs gate thresholds
- X-axis: 20 cells (4 models × 5 tasks), Y-axis: metric value
- Threshold lines: ΔAcc = −0.10, conf_wrong = 0.70
- Color coding: green = gate pass, red = gate fail
- Save: `figures/gate_metrics_per_cell.png`

**FR-7.2 Additional Figures (Phase 4 Coder Autonomous)**
1. **Accuracy-Confidence Scatter**: x = accuracy_clean, y = accuracy_adv per model; diagonal = no drop; bubble size = conf_wrong_adv. Save: `figures/accuracy_scatter.png`
2. **Confidence Distribution Histograms**: max softmax confidence on wrong adversarial predictions, one subplot per model. Save: `figures/confidence_distributions.png`
3. **ΔAcc Heatmap**: 4×5 heatmap of ΔAcc values (model × task), annotate gate status. Save: `figures/delta_acc_heatmap.png`
4. **ANLI Gradient Bar Chart**: mean ΔAcc per ANLI round across models. Save: `figures/anli_gradient.png`
5. **Base vs Chat Comparison**: grouped bar chart of ΔAcc for all 4 models. Save: `figures/base_vs_chat_comparison.png`

All figures saved to `docs/youra_research/h-m2/figures/`.

### FR-8: Results Storage

**FR-8.1 Structured Results**
- `results/h_m2_results.json`: all 20 cell statistics (accuracy_clean, accuracy_adv, delta_acc, conf_wrong_clean, conf_wrong_adv, conf_correct_adv, cell_pass)
- `results/h_m2_gate_report.json`: gate result, per-cell pass/fail, gate_pass_rate
- `results/h_m2_secondary_results.json`: aggregates, base/chat comparison, ANLI gradient, ablation results

**FR-8.2 Summary Report**
- Generate `docs/h_m2_summary.md` with findings in human-readable format
- Include: gate result, top 3 cells by ΔAcc, ANLI gradient finding, base/chat comparison

---

## Non-Functional Requirements

**NFR-1 Reproducibility:** Deterministic — no stochastic operations (pure post-hoc analysis). No seed required.

**NFR-2 Runtime:** < 5 minutes total (pure Python/numpy post-processing on cached JSONL files). No GPU required.

**NFR-3 Reuse:** Inherit from H-M1: `config.py` path patterns. Read H-E1 JSONL directly using same format as H-M1's `cache_loader.py`. Do not reimplement confidence extraction.

**NFR-4 Data Integrity:** Pre-flight check must verify all 40 JSONL files exist and are non-empty before any computation.

**NFR-5 Fail-Early:** If H-E1 `--log_samples` JSONL files are absent, fail immediately with diagnostic message pointing to H-E1 re-run command.

---

## Success Criteria

| Criterion | Threshold | Source |
|---|---|---|
| gate_pass_rate | ≥ 0.60 (≥12/20 cells) | FR-3.2, H-M2 hypothesis |
| mean ΔAcc across all cells | < −0.10 | FR-4.1 |
| mean conf_wrong_adv | ≥ 0.70 | FR-4.1 |
| All 3 ablations computed | 3 variant sets | FR-5 |
| Gate report generated | JSON with all indicators | FR-3.3 |
| Figures generated | ≥5 figures | FR-7 |
| Pre-flight check | 40 JSONL files verified | FR-1.3 |

---

## Data Specification

### Primary Data (H-E1 Results — Already Available)

| File Pattern | Content | Required |
|---|---|---|
| `h-e1/results/{model}_{task}_adversarial.jsonl` | Per-example logits (adversarial split) | Primary |
| `h-e1/results/{model}_{task}_clean.jsonl` | Per-example logits (clean split) | Primary |

**Note:** No new dataset downloads required. All data from H-E1 cached JSONL.

### Reference Datasets (Metadata Only — Auto-Download)

| Dataset | HF Identifier | Split | N | Purpose |
|---|---|---|---|---|
| AdvGLUE MNLI | `adversarial_glue` (adv_mnli) | validation | ~1,000 | Label verification |
| AdvGLUE QQP | `adversarial_glue` (adv_qqp) | validation | ~800 | Label verification |
| ANLI R1 | `facebook/anli` | test_r1 | 1,000 | Label verification |
| ANLI R2 | `facebook/anli` | test_r2 | 1,000 | Label verification |
| ANLI R3 | `facebook/anli` | test_r3 | 1,200 | Label verification |
| GLUE MNLI | `nyu-mll/glue` (mnli) | validation_matched | 9,815 | Clean accuracy baseline |
| GLUE QQP | `nyu-mll/glue` (qqp) | validation | 40,430 | Clean accuracy baseline |

**Download method:** HuggingFace `datasets` auto-download (already cached from H-E1/H-M1).

---

## Dependencies

### Section 7.1: Python Packages

```
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
datasets>=2.14.0
pyyaml>=6.0
tqdm>=4.65.0
pathlib (stdlib)
json (stdlib)
```

### Section 7.2: External Repositories (Reference Only)

- `EleutherAI/lm-evaluation-harness` — H-E1 evaluation framework (source of JSONL format; only for fallback re-run)

### Section 7.3: H-E1 and H-M1 Inherited Infrastructure

| Module | Path | Use |
|---|---|---|
| JSONL format reference | `h-e1/code/` | JSONL loading pattern |
| Config path patterns | `h-m1/code/config.py` | Reuse path conventions |
| Results writer | `h-e1/code/results/storage.py` | write_json pattern |
