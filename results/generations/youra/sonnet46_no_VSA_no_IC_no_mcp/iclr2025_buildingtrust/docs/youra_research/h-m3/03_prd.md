---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: H-M3
hypothesis_type: MECHANISM
tier: FULL
date: "2026-08-25"
author: Anonymous
---

# Product Requirements Document: H-M3

## Executive Summary

H-M3 tests whether the confidence-accuracy gap confirmed in H-M2 (soft-fail EXPLORE) manifests as measurable elevated **Expected Calibration Error (ECE)** under adversarial perturbation. The experiment computes ΔECE = ECE(adversarial) − ECE(clean) for each (model, task) cell using existing H-E1 lm-evaluation-harness outputs. Success requires ΔECE > 0.05 for ≥60% of cells AND mean ΔECE > 0 (one-sample t-test p < 0.05), confirming adversarial perturbation systematically degrades LLM calibration.

**Gate (SHOULD_WORK):** ΔECE > 0.05 in ≥60% of cells AND mean ΔECE > 0 (p < 0.05) — failure allows continuation as EXPLORE finding.

---

## Problem Statement

H-M2 confirmed a confidence-accuracy gap (mean ΔAcc = −0.0105, mean conf_wrong_adv = 0.6162) but failed both quantitative thresholds. H-M3 asks whether these moderate gaps — when systematic across bins — accumulate into measurable calibration degradation (ΔECE > 0.05). ECE = Σ_b |acc(b) − conf(b)| × |b|/n captures aggregate miscalibration across all confidence levels. Even small per-example gaps, if systematic, produce ECE increases. H-M3 tests this directly on the same (model, task) cells as H-M2, using label-preserved subsets from H-M1.

**Scope (inherited from H-E1/H-M1/H-M2):** Single model (Llama-2-7b-hf) due to H-E1 data scope. The 4-model grid (Llama-2-7b-hf, Llama-2-7b-chat-hf, Llama-2-13b-chat-hf, Mistral-7B-Instruct-v0.1) is the PRD ideal; actual scope is constrained by available H-E1 outputs.

---

## Functional Requirements

### FR-1: H-E1 Result File Loading

**FR-1.1 Locate and Load JSONL Files**
- Locate H-E1 lm-evaluation-harness per-example JSONL outputs in `docs/youra_research/h-e1/results/`
- Required pattern: `{model}_{task}_{split}.jsonl` for all available cells
- Required JSONL fields per example: `resps` (list of log-likelihoods per answer choice), `target` (correct answer index), `acc`
- Fail early with clear error if JSONL files missing: "H-E1 --log_samples results not found at {path}. Re-run H-E1 with --log_samples flag."
- Log available cell coverage at startup (which model×task×split combinations exist)

**FR-1.2 JSONL Format Handling**
- Parse `resps` field: `log_likelihoods = [r[0] for r in item["resps"]]` (one scalar per answer choice)
- Apply softmax: `probs = softmax(log_likelihoods)` using `scipy.special.softmax`
- Extract per example: `pred_idx = np.argmax(probs)`, `max_conf = float(probs[pred_idx])`, `is_correct = (pred_idx == item["target"])`

**FR-1.3 Label-Preserved Subset Filter (H-M1 Inheritance)**
- Apply H-M1 label-preserved subset filter before ECE computation
- Only compute ECE on label-preserved examples (≥80% of examples per H-M1)
- If H-M1 subset file not available: warn and use all examples (document in results)

**FR-1.4 Integrity Check**
- Assert ≥200 examples per JSONL file
- Log degenerate softmax warning if std(probs) < 0.01 for any example
- Report file coverage (models × tasks × splits) in pre-flight check

### FR-2: ECE Computation Per Cell

**FR-2.1 Cell Definition**
- Cells: (model) × (task) × {clean, adversarial}
- Minimum expected: Llama-2-7b-hf × {AdvGLUE-SST2, AdvGLUE-QQP, AdvGLUE-MNLI/MNLI-MM, ANLI-R1, ANLI-R2, ANLI-R3} = 6–8 cells minimum
- Clean counterpart tasks: GLUE tasks for AdvGLUE; MultiNLI for ANLI

**FR-2.2 ECE Computation (Guo 2017 Standard)**
For each (model, task, split) cell:
```python
def compute_ece_from_logits(logits_per_example, labels, n_bins=15):
    """
    Args:
        logits_per_example: List[np.array] — shape (n_choices,) per example
        labels: np.array shape (N,) — ground truth indices
        n_bins: int — 15 equal-width bins [0, 1] (Guo 2017)
    Returns:
        ece: float, confidences: np.array, correct: np.array
    """
    from scipy.special import softmax
    confidences = np.array([softmax(lgt).max() for lgt in logits_per_example])
    predictions = np.array([softmax(lgt).argmax() for lgt in logits_per_example])
    correct = (predictions == labels).astype(float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (confidences >= bin_boundaries[i]) & (confidences < bin_boundaries[i+1])
        if mask.sum() > 0:
            bin_acc = correct[mask].mean()
            bin_conf = confidences[mask].mean()
            ece += (mask.sum() / len(confidences)) * abs(bin_acc - bin_conf)
    return ece, confidences, correct
```

**FR-2.3 ΔECE Computation**
For each (model, task) cell:
```python
def compute_delta_ece(cell_results):
    """
    cell_results: dict with keys 'clean' and 'adversarial'
    Returns: delta_ece, ece_clean, ece_adv
    """
    ece_clean, _, _ = compute_ece_from_logits(**cell_results['clean'])
    ece_adv, _, _ = compute_ece_from_logits(**cell_results['adversarial'])
    return ece_adv - ece_clean, ece_clean, ece_adv
```
- Log: `"ECE computed: clean={ece_clean:.4f}, adv={ece_adv:.4f}, ΔECE={delta:.4f} for ({model}, {task})"`

**FR-2.4 ECE Sanity Check**
- Expected range: 0.0 ≤ ECE(clean) ≤ 0.5
- Sanity check against Kadavath 2022: ECE(clean) typically 0.05–0.15 for open-weight LLMs
- If ECE(clean) > 0.25 for all cells: FLAG as possible logit extraction artifact

### FR-3: Gate Evaluation

**FR-3.1 Per-Cell Gate Check**
For each (model, task) cell:
- `cell_pass = (delta_ece > 0.05)`

**FR-3.2 Global Gate**
- `gate_pass_count = sum(cell_pass for all cells)`
- `gate_pass_rate = gate_pass_count / total_cells`
- H-M3 primary gate condition 1: `gate_pass_rate >= 0.60`

**FR-3.3 Statistical Gate (One-Sample t-test)**
- H0: mean ΔECE ≤ 0
- Test: `scipy.stats.ttest_1samp(delta_ece_values, popmean=0, alternative='greater')`
- H-M3 primary gate condition 2: p < 0.05 AND mean ΔECE > 0
- Both conditions required for PASS; either failing → EXPLORE

**FR-3.4 Gate Report Generation**
- Generate `results/h_m3_gate_report.json` with:
  - `gate_pass_rate`, `gate_pass_count`, `total_cells`
  - `mean_delta_ece`, `t_stat`, `p_value`
  - `passed_cells`: list of (model, task) pairs with ΔECE > 0.05
  - `failed_cells`: list with ΔECE value
  - `overall_result`: "PASS" or "EXPLORE"
  - `note`: single-model-scope limitation if applicable

### FR-4: Secondary Analyses

**FR-4.1 Mean Aggregates**
- `mean_delta_ece`: mean(ΔECE) across all cells
- `mean_ece_clean`: mean(ECE_clean) across all cells (sanity check)
- `mean_ece_adv`: mean(ECE_adv) across all cells

**FR-4.2 ANLI Difficulty Gradient**
- Compute ΔECE per ANLI round: R1, R2, R3
- Expected direction: ΔECE(R3) ≥ ΔECE(R2) ≥ ΔECE(R1) — harder rounds → larger miscalibration
- Report: direction confirmed or not (consistent with H-M2 ANLI gradient finding)

**FR-4.3 Per-Bin Calibration Gap Analysis**
- For 2–3 representative (model, task) cells, extract per-bin calibration gap:
  - `bin_gap(b) = |acc(b) − conf(b)|` for clean and adversarial
  - Which confidence bins show largest increase under adversarial stress
- Report: which bin ranges are most affected

**FR-4.4 Task-Type Comparison**
- NLI tasks (ANLI R1/R2/R3 + AdvGLUE MNLI): mean ΔECE
- Sentiment/paraphrase tasks (AdvGLUE SST2/QQP): mean ΔECE
- Purpose: confirm whether NLI tasks drive ECE increase (consistent with H-E1/H-M2 patterns)

### FR-5: Ablation Studies

**FR-5.1 Ablation A: ECE Bin Count Sensitivity**
- Variant A1: n_bins=10 (fewer bins)
- Variant A2: n_bins=15 (Guo 2017 standard — primary)
- Variant A3: n_bins=20 (more bins)
- Purpose: confirm ΔECE > 0.05 gate is robust to bin count choice

**FR-5.2 Ablation B: ΔECE Threshold Sensitivity**
- Variant B1: threshold = 0.03 (looser) → new gate_pass_rate
- Variant B2: threshold = 0.05 (standard — primary)
- Variant B3: threshold = 0.10 (stricter) → new gate_pass_rate
- Purpose: test sensitivity of gate condition

**FR-5.3 Ablation C: Label-Preserved vs All Examples**
- Variant C1: ECE on H-M1 label-preserved subset (primary)
- Variant C2: ECE on ALL examples (no label filter)
- Purpose: quantify effect of label-preservation filter on ECE signal

### FR-6: Mechanism Activation Verification

**FR-6.1 Activation Verification Function**
```python
def verify_mechanism_activated(results_dict):
    """Verify ECE computation completed and ΔECE signal is present."""
    indicators = {
        "ece_computed": all(
            r['ece_clean'] is not None and r['ece_adv'] is not None
            for r in results_dict.values()
        ),
        "baseline_in_range": all(
            0.0 <= r['ece_clean'] <= 0.5 for r in results_dict.values()
        ),
        "delta_positive_majority": (
            sum(1 for r in results_dict.values() if r['delta_ece'] > 0)
            >= len(results_dict) / 2
        )
    }
    activated = all(indicators.values())
    return activated, indicators
```

**FR-6.2 Failure Detection**

| Failure Mode | Detection | Action |
|---|---|---|
| Missing JSONL | `Path(results_path).exists()` | FAIL EARLY with path info |
| ECE not computed | `ece_clean is None` for any cell | FAIL: logit extraction issue |
| ECE out of range | `ECE < 0` or `ECE > 1` | FAIL: implementation error — check softmax normalization |
| ΔECE uniformly ≤ 0 | All cells show ΔECE ≤ 0 | EXPLORE: adversarial does not increase miscalibration |
| Clean ECE > 0.25 all cells | Sanity check failure | FLAG: possible logit extraction artifact |

### FR-7: Visualization

**FR-7.1 Required Figure (Gate Metric)**
- **ΔECE Bar Chart**: ΔECE per (model, task) cell, horizontal line at 0.05 gate threshold
- Color-coded: green = ΔECE > 0.05 (pass), red = ΔECE ≤ 0.05 (fail)
- Save: `figures/delta_ece_per_cell.png`

**FR-7.2 Additional Figures (Phase 4 Coder Autonomous)**
1. **Calibration Reliability Diagrams**: clean vs. adversarial overlay for 2–3 representative (model, task) pairs. Save: `figures/reliability_diagram_{model}_{task}.png`
2. **ΔECE Heatmap**: rows = models, columns = tasks (for multi-model if available). Save: `figures/delta_ece_heatmap.png`
3. **Per-Bin Calibration Gap**: stacked bar showing per-bin |acc(b) − conf(b)| for clean and adversarial. Save: `figures/per_bin_calibration_gap.png`
4. **ECE Clean vs Adversarial Scatter**: x = ECE(clean), y = ECE(adversarial), diagonal = no change line. Save: `figures/ece_scatter.png`
5. **ANLI Gradient Bar Chart**: mean ΔECE per ANLI round (R1, R2, R3). Save: `figures/anli_ece_gradient.png`

All figures saved to `docs/youra_research/h-m3/figures/`.

### FR-8: Results Storage

**FR-8.1 Structured Results**
- `results/h_m3_ece_table.csv`: per-cell ECE(clean), ECE(adv), ΔECE, cell_pass
- `results/h_m3_delta_ece.json`: ΔECE per cell with metadata
- `results/h_m3_gate_report.json`: gate result, t-stat, p-value, per-cell pass/fail
- `results/h_m3_secondary_results.json`: aggregates, ANLI gradient, per-bin analysis, ablation results

**FR-8.2 Summary Report**
- Generate `results/h_m3_summary.md` with findings in human-readable format
- Include: gate result, mean ΔECE, t-stat, p-value, top 3 cells by ΔECE, ANLI gradient finding

---

## Non-Functional Requirements

**NFR-1 Reproducibility:** Deterministic — ECE computation is pure numpy/scipy with no stochastic operations. No seed required.

**NFR-2 Runtime:** < 10 minutes total (Python/numpy post-processing on cached JSONL files). GPU not required.

**NFR-3 Reuse:** Inherit JSONL loading pattern from H-M2 (`cache_loader.py` or equivalent). Reuse softmax extraction pattern. Do not reimplement JSONL parsing.

**NFR-4 Data Integrity:** Pre-flight check must verify required JSONL files exist and are non-empty before any ECE computation.

**NFR-5 Fail-Early:** If H-E1 `--log_samples` JSONL files are absent, fail immediately with diagnostic message pointing to H-E1 re-run command.

**NFR-6 n_bins Parameterizable:** ECE computation must accept `n_bins` as parameter (default=15) to support ablation studies.

---

## Success Criteria

| Criterion | Threshold | Source |
|---|---|---|
| ΔECE > 0.05 gate_pass_rate | ≥ 0.60 | FR-3.2, H-M3 hypothesis |
| Mean ΔECE > 0 (t-test) | p < 0.05 | FR-3.3 |
| ECE(clean) sanity check | 0.05–0.15 expected (Kadavath 2022) | FR-2.4 |
| All 3 ablations computed | 3 variant sets each | FR-5 |
| Gate report generated | JSON with all indicators | FR-3.4 |
| Mechanism activated | verify_mechanism_activated() returns True | FR-6.1 |
| Figures generated | ≥5 figures | FR-7 |
| Pre-flight check | JSONL files verified | FR-1.4 |

---

## Data Specification

### Primary Data (H-E1 Results — Already Available)

| File Pattern | Content | Required |
|---|---|---|
| `h-e1/results/{model}_{task}_adversarial.jsonl` | Per-example logits (adversarial split) | Primary |
| `h-e1/results/{model}_{task}_clean.jsonl` | Per-example logits (clean split) | Primary |

**Note:** No new dataset downloads required for core computation. All data from H-E1 cached JSONL.

### Reference Datasets (Clean Counterparts — Auto-Download)

| Dataset | HF Identifier | Split | N | Purpose |
|---|---|---|---|---|
| GLUE SST-2 | `nyu-mll/glue` (sst2) | validation | 872 | Clean baseline for AdvGLUE-SST2 |
| GLUE QQP | `nyu-mll/glue` (qqp) | validation | 40,430 | Clean baseline for AdvGLUE-QQP |
| GLUE MNLI | `nyu-mll/glue` (mnli) | validation_matched | 9,815 | Clean baseline for AdvGLUE-MNLI |
| MultiNLI | `nyu-mll/multi_nli` | validation_matched | 9,832 | Clean baseline for ANLI |
| AdvGLUE | `AI-Secure/adv_glue` | test | ~13,167 | Adversarial NLU benchmark |
| ANLI | `facebook/anli` | test_r1/r2/r3 | 3,200 | Adversarial NLI (R1/R2/R3) |

**Download method:** HuggingFace `datasets` auto-download (already cached from H-E1/H-M1/H-M2).

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
netcal>=1.3.5  # optional: for reliability diagrams (pip install netcal)
pathlib (stdlib)
json (stdlib)
csv (stdlib)
```

### Section 7.2: External Repositories (Reference Only)

- `EleutherAI/lm-evaluation-harness` — H-E1 evaluation framework (source of JSONL format; only for fallback re-run)
- `EFS-OpenSource/calibration-framework (NetCal)` — optional library for reliability diagrams

### Section 7.3: H-E1 and H-M2 Inherited Infrastructure

| Module | Path | Use |
|---|---|---|
| JSONL loading pattern | `h-e1/code/` | JSONL format reference |
| Config path patterns | `h-m1/code/config.py` or `h-m2/code/config.py` | Reuse path conventions |
| Softmax extraction | `h-m2/code/` | Reuse logit→probability extraction |
| Results writer | `h-e1/code/results/storage.py` | write_json pattern |
