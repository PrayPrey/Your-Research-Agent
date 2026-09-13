# H-E1 Phase 4 Validation Report

**Hypothesis:** H-E1 — EXISTENCE: Layer-wise MLP Activation Sparsity in LLaMA-3.1-8B  
**Gate Type:** MUST_WORK  
**Gate Result:** PASS  
**Completed:** 2026-05-08T10:30:00Z

---

## Hypothesis Statement

Layer-wise MLP activation sparsity in LLaMA-3-8B varies significantly across layers (CV > 0.3) on 512-sample Alpaca calibration set, and this ranking is stable across Alpaca vs. WikiText-103 (Kendall's tau_calibration >= 0.6) and across input lengths 128 vs. 512 tokens.

---

## Gate Conditions

| Condition | Threshold | Value | Result |
|-----------|-----------|-------|--------|
| CV (coefficient of variation) | > 0.3 | **0.544** | PASS |
| tau_calibration (Kendall's tau, Alpaca vs WikiText-103) | >= 0.6 | **0.786** | PASS |

**Overall Gate: PASS**

---

## Experiment Setup

- **Model:** meta-llama/Llama-3.1-8B (float16, device_map=auto)
- **GPU:** NVIDIA H100 NVL (100 GB VRAM)
- **Datasets:** tatsu-lab/alpaca (512 samples) + wikitext-103-raw-v1 (512 chunks)
- **Measurement:** Forward hook on `gate_proj` layer of each of 32 MLP blocks
- **Sparsity definition:** fraction of |activations| < epsilon
- **Conditions:** 3 datasets × 4 epsilon values = 12 total conditions

---

## Results Table (All Epsilon Values)

| Epsilon | CV (Alpaca Long) | tau_calibration | tau_length |
|---------|-----------------|-----------------|------------|
| 0.001   | 0.549           | 0.790           | 0.883      |
| **0.010** (primary) | **0.544** | **0.786** | **0.899** |
| 0.050   | 0.528           | 0.778           | 0.875      |
| 0.100   | 0.484           | 0.782           | 0.879      |

All four epsilon values exceed both gate thresholds, demonstrating robustness.

---

## Key Findings

1. **Significant layer-wise variation:** CV = 0.544 at primary epsilon (0.01), well above the 0.3 threshold. Sparsity is not uniform across the 32 LLaMA-3.1-8B MLP layers.

2. **Stable cross-dataset ranking:** Kendall's tau = 0.786 between Alpaca and WikiText-103 sparsity rankings, confirming the layer ordering reflects model architecture rather than input-distribution artifacts.

3. **Stable cross-length ranking:** tau_length = 0.899, showing the layer sparsity ranking is consistent across 128-token and 512-token inputs.

4. **Epsilon robustness:** All 4 epsilon values (0.001–0.1) yield CV > 0.3 and tau >= 0.6. The sparsity phenomenon is not threshold-sensitive.

5. **Mean sparsity and std verified:** mean = 0.0227, std = 0.0124 at primary condition, confirming non-trivial variation.

---

## Figures Generated

All figures saved to `h-e1/figures/`:

| Figure | File | Description |
|--------|------|-------------|
| Gate Metrics Bar | `gate_metrics.png` | CV and tau_calibration vs thresholds |
| Sparsity Profile | `sparsity_profile.png` | Per-layer sparsity across 32 layers (Alpaca vs WikiText) |
| Epsilon Sensitivity | `epsilon_sensitivity.png` | CV and tau across 4 epsilon values |
| Length Sensitivity | `length_sensitivity.png` | Short (128) vs long (512) sparsity with tau annotation |
| Rank Correlation Scatter | `rank_correlation.png` | Layer rank scatter between Alpaca and WikiText-103 |

---

## Mechanism Verification

- `len_ok: True` — 32 layer values returned
- `mean_positive: True` — non-zero sparsity observed
- `std_nonzero: True` — meaningful variation across layers
- `mean_value: 0.0227`, `std_value: 0.0124`

---

## Implementation Summary

**Files generated:**
- `code/config.py` — ExperimentConfig dataclass
- `code/data_utils.py` — Alpaca + WikiText-103 dataloaders
- `code/measure_sparsity.py` — Forward hook measurement engine (closure factory pattern)
- `code/compute_metrics.py` — CV, Kendall's tau computation
- `code/visualize.py` — 5 figures (headless matplotlib)
- `code/run_experiment.py` — Full pipeline orchestration
- `code/run_experiment_wrapper.sh` — Env-clean launcher with mandatory trap
- `code/tests/test_measure_sparsity.py` — 16 unit tests, all passing

**Test suite:** 16/16 tests passing (pytest)

**Experiment log:** `code/experiment.log`  
**Results JSON:** `experiment_results.json`

---

## Pipeline Continuation

H-E1 PASS unblocks the following hypotheses:
- **h-m1** (MECHANISM): Cross-distribution sparsity stability — prerequisites now met
- **h-m2** (MECHANISM): Epsilon robustness of sparsity ordering — prerequisites now met

H-m3 and H-m4 remain blocked pending h-m1 and h-m2 respectively.

---

## Conclusion

**H-E1 is VALIDATED.** LLaMA-3.1-8B MLP activation sparsity exhibits significant cross-layer variation (CV=0.544) with stable layer ranking across different text distributions (tau=0.786) and input lengths (tau=0.899). This confirms the existence of a meaningful sparsity signal that can be used for LoRA rank allocation in subsequent hypotheses.
