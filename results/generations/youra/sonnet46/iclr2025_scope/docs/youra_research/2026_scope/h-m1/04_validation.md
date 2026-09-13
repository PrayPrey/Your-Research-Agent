# Phase 4 Validation Report: h-m1

**Generated:** 2026-05-08T07:56:00Z
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5 (next hypothesis)

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-m1 |
| **Type** | MECHANISM |
| **Statement** | Layer-wise MLP activation sparsity profiles in LLaMA-3-8B are stable across diverse calibration distributions (Alpaca, WikiText-103, SST-2 val, MNLI val), with ICC > 0.75 and all pairwise Kendall's tau >= 0.6 |
| **Gate Type** | MUST_WORK |
| **Gate Result** | **PASS** |
| **Prerequisite** | h-e1 (PASS) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 24 |
| Completed | 24 |
| In Progress | 0 |
| Remaining | 0 |
| Coder-Validator Cycles | 1 |
| Hypothesis Type | INCREMENTAL (extends h-e1) |

### Generated / Extended Files

| File | Lines | Description |
|------|-------|-------------|
| `code/config.py` | 56 | ExperimentConfig with h-m1 fields (icc_threshold, 4 datasets) |
| `code/data_utils.py` | 140 | Extended: SST-2 (SetFit/sst2) + MNLI (nyu-mll/multi_nli) loaders |
| `code/measure_sparsity.py` | 110 | Extended: measure_all_distributions wrapper |
| `code/compute_icc.py` | 60 | NEW: ICC(3,k) via pingouin, build_icc_dataframe, compute_icc_sensitivity |
| `code/compute_metrics.py` | 126 | Extended: compute_pairwise_tau, compute_tau_min, evaluate_gate, compute_tau_sensitivity |
| `code/visualize.py` | 204 | NEW: 6 plot functions (gate metrics, heatmap, tau matrix, ICC CI, overlay, sensitivity) |
| `code/run_experiment.py` | 209 | NEW: Full pipeline orchestrator (16 measurements + stats + figures + JSON output) |
| `code/run_experiment_wrapper.sh` | 22 | CUDA env fix wrapper (env -i pattern) |

### Test Files (32 tests, all pass)

| Test File | Tests |
|-----------|-------|
| `tests/test_config.py` | 8 |
| `tests/test_compute_icc.py` | 6 |
| `tests/test_compute_metrics.py` | 5 |
| `tests/test_data_utils.py` | 3 |
| `tests/test_measure_sparsity.py` | 2 |
| `tests/test_visualize.py` | 4 |
| `tests/test_run_experiment.py` | 4 |

---

## Code Quality Checklist

- [✓] Syntax validation passed (all 7 modules import cleanly)
- [✓] Type hints compliance (Dict, List, Optional, Any throughout)
- [✓] API signatures match 03_logic.md specifications
- [✓] Pingouin 0.6.1 compatibility verified (ICC(C,k) type, CI95 column)
- [✓] CUDA visibility via env -i pattern (matches h-e1 proven approach)
- [✓] HF dataset cache compatibility verified (SetFit/sst2, nyu-mll/multi_nli)
- [✓] No mock/synthetic data in main code
- [✓] 32/32 unit tests pass

---

## Experiment Results

### Primary Metrics (epsilon = 0.01)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| ICC(3,k) | **0.9846** | > 0.75 | ✅ PASS |
| ICC 95% CI | [0.97, 0.99] | — | — |
| tau_min (all 6 pairs) | **0.7339** | >= 0.6 | ✅ PASS |

### All 6 Pairwise Kendall's Tau (epsilon = 0.01)

| Pair | tau | p-value |
|------|-----|---------|
| alpaca vs wikitext | 0.7863 | 2.03e-13 |
| alpaca vs sst2 | 0.9395 | 3.35e-24 |
| alpaca vs mnli | 0.9476 | 3.51e-25 |
| wikitext vs sst2 | **0.7339** (min) | 2.78e-11 |
| wikitext vs mnli | 0.7500 | 6.81e-12 |
| sst2 vs mnli | 0.9839 | 3.94e-31 |

All p-values < 1e-10 (highly statistically significant).

### ICC(3,k) Sensitivity Across Epsilon Values

| Epsilon | ICC(3,k) | tau_min |
|---------|---------|---------|
| 0.001 | 0.9862 | 0.7339 |
| 0.01 (primary) | **0.9846** | **0.7339** |
| 0.05 | 0.9878 | 0.7419 |
| 0.1 | 0.9872 | 0.7540 |

Results are robust across all 4 epsilon values — ICC > 0.98 and tau_min >= 0.73 in all cases.

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Criterion 1** | ICC(3,k) = 0.9846 > 0.75 ✅ |
| **Criterion 2** | All 6 pairwise tau >= 0.6 (min=0.7339) ✅ |
| **Result** | **PASS** |
| **Satisfied** | true |

---

## Experiment Execution

| Field | Value |
|-------|-------|
| Model | LLaMA-3.1-8B (meta-llama/Llama-3.1-8B) |
| GPU | NVIDIA H100 NVL (100GB VRAM), GPU 0 |
| VRAM Used | 18.4 GB |
| Distributions | Alpaca, WikiText-103, SST-2 val, MNLI val (512 samples each) |
| Epsilons Tested | 0.001, 0.01, 0.05, 0.1 |
| Total Runs | 16 (4 dists × 4 epsilons) |
| Batch Size | 8 (64 forward passes per run) |
| Duration | ~5 minutes |
| Exit Code | 0 (success) |
| Datasets | tatsu-lab/alpaca, Salesforce/wikitext-103, SetFit/sst2, nyu-mll/multi_nli |

---

## Generated Figures

| File | Description |
|------|-------------|
| `figures/gate_metrics.png` | Bar chart: ICC(3,k) and tau_min vs thresholds |
| `figures/sparsity_heatmap.png` | Heatmap: 4 distributions × 32 layers sparsity values |
| `figures/pairwise_tau_matrix.png` | 4×4 tau matrix for all pairwise comparisons |
| `figures/icc_confidence.png` | ICC(3,k) point estimate with 95% CI |
| `figures/sparsity_profiles_overlay.png` | Overlaid sparsity profiles for all 4 distributions |
| `figures/epsilon_sensitivity.png` | ICC and tau sensitivity across 4 epsilon values |

---

## Next Steps

Gate PASS (MUST_WORK) → **Proceed to next hypothesis in pipeline.**

- h-m1 prerequisite satisfied: h-m3 (Sparsity-Rank Correlation) is now unblocked
- h-m2 (Epsilon Robustness) is also unblocked (prerequisite: h-e1 only)
- Both h-m2 and h-m3 can now be executed

---

## Phase 2C Handoff

### Proven Components

| Component | File | Type | Status |
|-----------|------|------|--------|
| ExperimentConfig (h-m1) | config.py | configuration | ✅ Validated |
| load_sst2_dataloader | data_utils.py | data loading | ✅ Validated (SetFit/sst2) |
| load_mnli_dataloader | data_utils.py | data loading | ✅ Validated (nyu-mll/multi_nli) |
| load_all_dataloaders | data_utils.py | data loading | ✅ Validated (4-dist dict) |
| measure_all_distributions | measure_sparsity.py | measurement | ✅ Validated |
| build_icc_dataframe | compute_icc.py | statistics | ✅ Validated |
| compute_icc3k | compute_icc.py | statistics | ✅ Validated (pingouin 0.6.1) |
| compute_icc_sensitivity | compute_icc.py | statistics | ✅ Validated |
| compute_pairwise_tau | compute_metrics.py | statistics | ✅ Validated |
| evaluate_gate | compute_metrics.py | gate eval | ✅ Validated |
| compute_tau_sensitivity | compute_metrics.py | statistics | ✅ Validated |
| All 6 figure functions | visualize.py | visualization | ✅ Validated |
| run_experiment.py | run_experiment.py | orchestration | ✅ Validated |

### Optimal Hyperparameters

```yaml
primary_epsilon: 0.01
n_samples: 512
batch_size: 8
max_length: 512
model: meta-llama/Llama-3.1-8B
torch_dtype: float16
device_map: auto
icc_threshold: 0.75
tau_threshold: 0.6
conda_env: youra-h-m1
datasets:
  alpaca: tatsu-lab/alpaca
  wikitext: wikitext/wikitext-103-raw-v1
  sst2: SetFit/sst2  # NOT nyu-mll/glue sst2 (cache incompatibility)
  mnli: nyu-mll/multi_nli  # NOT nyu-mll/glue mnli (cache incompatibility)
```

### Lessons Learned

**What Worked:**
- INCREMENTAL approach: reusing h-e1 measurement infrastructure (register_hooks, measure_layer_sparsity) saved significant implementation time
- pingouin.intraclass_corr is straightforward for ICC(3,k) once correct type name "ICC(C,k)" and column "CI95" are known
- env -i CUDA_VISIBLE_DEVICES pattern (from h-e1) works reliably for h-m1 as well
- All 4 datasets available in HuggingFace cache — no downloads needed

**What Didn't Work / Required Fixes:**
- Initial dataset IDs wrong: `nyu-mll/glue sst2/mnli` was cached only for `cola` config. Correct IDs: `SetFit/sst2` (field: `text`) and `nyu-mll/multi_nli` (fields: `premise`, `hypothesis`)
- pingouin API: version 0.6.1 uses Type="ICC(C,k)" not "ICC3k", and column "CI95" not "CI95%"
- Python stdout buffering meant experiment.log showed no output until flush — monitoring required GPU utilization check

**Key Insights:**
- **Sparsity profiles are remarkably distribution-stable**: ICC=0.9846 far exceeds the 0.75 threshold, suggesting sparsity is a stable structural property rather than calibration artifact
- **WikiText shows lower correlation with the others** (tau_min in wikitext pairs = 0.73-0.75) vs instruction-tuned data pairs (sst2/mnli tau=0.98), possibly due to text domain differences
- **Epsilon choice is immaterial**: ICC > 0.98 for all 4 epsilon values — any reasonable threshold works

### Recommendations for Dependent Hypotheses

**For h-m3 (Sparsity-Rank Correlation):**
- Use Alpaca as primary calibration distribution (stable, widely used)
- The 32-layer sparsity profile from h-m1 (primary_epsilon=0.01) can be directly reused for rank allocation
- Expected high tau values (>0.73 even for WikiText) mean any single distribution suffices for rank allocation
- Reuse: config.py, data_utils.py, measure_sparsity.py, compute_metrics.py directly from h-m1

**For h-m2 (Epsilon Robustness):**
- h-m1 sensitivity analysis already confirms ICC > 0.98 for all epsilons — h-m2 should PASS easily
- Reuse: all of h-m1 code, the icc_sensitivity and tau_sensitivity dicts from experiment_results.json

**General:**
- The CUDA env-i pattern is proven — use in all future experiment wrappers
- Always verify HuggingFace dataset cache IDs before setting TRANSFORMERS_OFFLINE=1
- SetFit/sst2 uses field "text" (not "sentence"); nyu-mll/multi_nli uses "premise" + "hypothesis"

---

## Appendix

### Key Files

| File | Path |
|------|------|
| Experiment Results | `h-m1/experiment_results.json` |
| Experiment Log | `h-m1/code/experiment.log` |
| Terminal Log | `h-m1/code/terminal.log` |
| Checkpoint | `h-m1/04_checkpoint.yaml` |
| Figures | `h-m1/figures/` (6 figures) |

### Checkpoint State Summary

```yaml
current_step: 8
hypothesis_id: h-m1
tasks_completed: 24/24
validation_passed: true
dry_run_status: passed
experiment_status: completed
gate_result: PASS
full_experiment_completed: true
archon_task_status: done
```
