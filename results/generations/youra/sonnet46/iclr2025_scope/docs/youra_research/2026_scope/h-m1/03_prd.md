# Product Requirements Document: h-m1

**stepsCompleted:** [step-01-initialize, step-02-prd]
**Hypothesis:** h-m1 — Cross-Distribution Stability of MLP Activation Sparsity Profiles
**Date:** 2026-05-08
**Phase:** Phase 3 Implementation Planning
**PRD Version:** 1.0

---

## Executive Summary

This PRD defines the implementation requirements for validating **h-m1**: that layer-wise MLP activation sparsity profiles in LLaMA-3.1-8B are stable across 4 diverse calibration distributions (Alpaca, WikiText-103, SST-2 val, MNLI val), with ICC(3,k) > 0.75 and all 6 pairwise Kendall's tau >= 0.6. This is a pure measurement study extending h-e1's validated infrastructure to 2 additional distributions and stronger statistical reliability tests (ICC). Success directly enables h-m3 and h-m4 (rank allocation experiments).

**Hypothesis Type:** MECHANISM (INCREMENTAL — depends on h-e1 PASS)
**Gate Type:** MUST_WORK
**Gate Condition:** ICC(3,k) > 0.75 AND tau_min >= 0.6 (all 6 pairwise pairs)
**Task Budget:** 30 tasks max (FULL tier)

---

## Problem Statement

H-E1 validated that LLaMA-3.1-8B layer-wise MLP activation sparsity varies significantly (CV=0.544 > 0.3) and is stable between Alpaca and WikiText-103 (Kendall's tau=0.786 >= 0.6). However, this was tested on only 2 distributions. Before using sparsity profiles to guide LoRA rank allocation (h-m3, h-m4), we must confirm that:

1. Sparsity profiles are **reliably consistent** across 4 semantically diverse distributions (instruction-following, general prose, sentiment, NLI)
2. This stability holds under a stronger multi-rater reliability metric (ICC(3,k))
3. All pairwise distribution combinations yield tau >= 0.6

If either gate condition fails, h-m3 and h-m4 are blocked — the sparsity profiles are distribution-dependent artifacts, not stable architectural signatures.

---

## Functional Requirements

### FR-1: Multi-Distribution Dataset Loading
- **FR-1.1:** Load Alpaca calibration set: `tatsu-lab/alpaca`, train split, 512 samples, `instruction + input + output` concatenated fields
- **FR-1.2:** Load WikiText-103 calibration set: `wikitext-103-raw-v1`, test split, 512 sliding-window chunks of 512 tokens (reuse h-e1/code/data_utils.py)
- **FR-1.3:** Load SST-2 validation set: `nyu-mll/glue` (sst2), validation split, 512 samples, `sentence` field padded/truncated to 512 tokens
- **FR-1.4:** Load MNLI validation set: `nyu-mll/glue` (mnli), validation_matched split, 512 samples, `premise + " [SEP] " + hypothesis` concatenated, padded/truncated to 512 tokens
- **FR-1.5:** All datasets tokenized with `meta-llama/Llama-3.1-8B` AutoTokenizer, max_length=512, padding=True, truncation=True
- **FR-1.6:** DataLoaders: batch_size=8, shuffle=False for all distributions

### FR-2: LLaMA-3.1-8B Activation Sparsity Measurement
- **FR-2.1:** Load `meta-llama/Llama-3.1-8B` with `torch_dtype=torch.float16, device_map="auto"`, set to eval mode
- **FR-2.2:** Register forward hooks on `model.model.layers[i].mlp.gate_proj` for all 32 layers (reuse h-e1/code/measure_sparsity.py)
- **FR-2.3:** For each distribution, compute per-layer sparsity as mean fraction of `|activations| < epsilon` over 512 samples, yielding shape (32,) per distribution
- **FR-2.4:** Primary epsilon = 0.01; also run sensitivity analysis for epsilon ∈ {0.001, 0.01, 0.05, 0.1}
- **FR-2.5:** Seeds: `numpy.random.seed(42)`, `torch.manual_seed(42)` before each measurement run
- **FR-2.6:** Set `CUDA_VISIBLE_DEVICES` to single GPU (lowest memory usage) before running

### FR-3: Statistical Analysis — ICC(3,k)
- **FR-3.1:** Build long-format DataFrame: columns `[layer, distribution, sparsity]` with 4 × 32 = 128 rows (primary epsilon=0.01)
- **FR-3.2:** Compute ICC using `pingouin.intraclass_corr(data=df, targets="layer", raters="distribution", ratings="sparsity")`
- **FR-3.3:** Extract ICC(3,k) value and 95% CI from results where `Type == "ICC3k"`
- **FR-3.4:** Gate check: `icc3k > 0.75`
- **FR-3.5:** Repeat ICC computation for each of the 4 epsilon values (sensitivity analysis)

### FR-4: Statistical Analysis — Pairwise Kendall's Tau
- **FR-4.1:** Compute all C(4,2) = 6 pairwise Kendall's tau values using `scipy.stats.kendalltau` on the shape-(32,) sparsity vectors
- **FR-4.2:** Pairs: alpaca_vs_wikitext, alpaca_vs_sst2, alpaca_vs_mnli, wikitext_vs_sst2, wikitext_vs_mnli, sst2_vs_mnli
- **FR-4.3:** Record tau value and p-value for each pair
- **FR-4.4:** Compute tau_min = minimum of all 6 tau values
- **FR-4.5:** Gate check: all 6 tau values >= 0.6 (i.e., tau_min >= 0.6)
- **FR-4.6:** Repeat for each of the 4 epsilon values (sensitivity analysis)

### FR-5: Gate Evaluation and Result Reporting
- **FR-5.1:** Evaluate combined gate: PASS if `icc3k > 0.75` AND `tau_min >= 0.6`; FAIL otherwise
- **FR-5.2:** Generate structured results JSON: `h-m1/experiment_results.json` with all metrics, gate status, and per-epsilon sensitivity results
- **FR-5.3:** Print gate evaluation summary to stdout: ICC(3,k) value, all 6 tau values, gate result (PASS/FAIL)
- **FR-5.4:** On FAIL: log which condition(s) failed and numeric gap to threshold

### FR-6: Visualization
- **FR-6.1 (Mandatory):** Gate metrics bar chart: ICC(3,k) and tau_min vs thresholds (0.75 and 0.6 dashed lines) → `h-m1/figures/gate_metrics.png`
- **FR-6.2:** Sparsity profile heatmap: 32 layers × 4 distributions, colormap → `h-m1/figures/sparsity_heatmap.png`
- **FR-6.3:** Pairwise tau matrix: 4×4 symmetric heatmap (diagonal=1.0) → `h-m1/figures/pairwise_tau_matrix.png`
- **FR-6.4:** ICC confidence interval: bar with 95% CI for ICC3k vs 0.75 threshold → `h-m1/figures/icc_confidence.png`
- **FR-6.5:** Layer-by-layer sparsity lines: 4 overlaid lines, x=layer index, y=sparsity → `h-m1/figures/sparsity_profiles_overlay.png`
- **FR-6.6:** Epsilon sensitivity: ICC(3,k) and tau_min vs 4 epsilon values → `h-m1/figures/epsilon_sensitivity.png`
- **FR-6.7:** All figures saved to `h-m1/figures/` directory

### FR-7: Code Reuse from h-e1
- **FR-7.1:** Reuse `h-e1/code/measure_sparsity.py` — forward hook measurement infrastructure (gate_proj, epsilon=0.01)
- **FR-7.2:** Reuse `h-e1/code/data_utils.py` — Alpaca and WikiText-103 dataset loaders
- **FR-7.3:** Extend data_utils.py to add SST-2 val and MNLI val loaders (FR-1.3, FR-1.4)
- **FR-7.4:** Create new `h-m1/code/compute_icc.py` for ICC(3,k) computation via pingouin
- **FR-7.5:** Create new `h-m1/code/run_experiment.py` as main entry point orchestrating all FR-2 through FR-6

---

## Non-Functional Requirements

### NFR-1: Performance
- **NFR-1.1:** Total runtime ≤ 30 minutes on single H100 GPU (4 distributions × ~5-7 min each)
- **NFR-1.2:** Peak GPU memory ≤ 20GB (LLaMA-3.1-8B float16 ≈ 15GB + hook overhead)
- **NFR-1.3:** CPU memory ≤ 32GB for dataset loading and statistics

### NFR-2: Reproducibility
- **NFR-2.1:** Fixed seeds (numpy seed=42, torch seed=42) for all random operations
- **NFR-2.2:** Deterministic data sampling (shuffle=False on DataLoaders)
- **NFR-2.3:** All results saved to `experiment_results.json` for Phase 6 paper writing

### NFR-3: Code Quality
- **NFR-3.1:** Modular design: separate modules for data loading, measurement, statistics, visualization
- **NFR-3.2:** Each module independently testable
- **NFR-3.3:** Docstrings on public functions
- **NFR-3.4:** Requirements.txt specifying: torch, transformers, datasets, numpy, scipy, pingouin, pandas, matplotlib, seaborn

### NFR-4: Environment
- **NFR-4.1:** Single GPU only (`CUDA_VISIBLE_DEVICES` set to lowest-memory GPU)
- **NFR-4.2:** Python 3.10+, PyTorch 2.x
- **NFR-4.3:** HuggingFace cache directory available for model/dataset downloads

---

## Dependencies

### External Dependencies
| Dependency | Version | Purpose |
|-----------|---------|---------|
| torch | ≥2.0 | Model inference, forward hooks |
| transformers | ≥4.40 | LLaMA-3.1-8B loading, tokenizer |
| datasets | ≥2.18 | HuggingFace dataset loading |
| numpy | ≥1.24 | Array operations, statistics |
| scipy | ≥1.11 | Kendall's tau (scipy.stats.kendalltau) |
| pingouin | ≥0.5.4 | ICC(3,k) computation (intraclass_corr) |
| pandas | ≥2.0 | Long-format DataFrame for pingouin |
| matplotlib | ≥3.7 | Figure generation |
| seaborn | ≥0.12 | Heatmap visualization |

### Internal Dependencies
| Dependency | Source | Status |
|-----------|--------|--------|
| h-e1/code/measure_sparsity.py | Phase 4 h-e1 | VALIDATED (16/16 tests pass) |
| h-e1/code/data_utils.py | Phase 4 h-e1 | VALIDATED |
| meta-llama/Llama-3.1-8B | HuggingFace Hub | Must be accessible |
| verification_state.yaml | Phase 2B/2C | Exists, h-m1 status IN_PROGRESS |

---

## Success Criteria

### Primary Gate (MUST_WORK)
| Criterion | Threshold | Expected | Method |
|-----------|-----------|----------|--------|
| ICC(3,k) across 4 distributions | > 0.75 | 0.80–0.95 | pingouin.intraclass_corr, ICC3k type |
| tau_min (all 6 pairwise Kendall's tau) | >= 0.6 | 0.65–0.80 | scipy.stats.kendalltau, minimum of 6 pairs |

### Secondary Validation
| Criterion | Target | Purpose |
|-----------|--------|---------|
| Epsilon sensitivity: ICC holds for ≥3/4 epsilon values | ICC3k > 0.75 for ≥3/4 | Robustness check |
| Epsilon sensitivity: tau_min >= 0.6 for ≥3/4 epsilon values | tau_min >= 0.6 for ≥3/4 | Robustness check |
| All 6 individual tau values >= 0.6 | All 6 | Confirms no outlier distribution pair |
| Code runs without error | 0 exceptions | Basic correctness |
| All 6 figures generated | 6 PNG files | Visualization completeness |

### Gate Outcome Actions
| Gate Result | Action |
|-------------|--------|
| PASS (both conditions met) | → Unlock h-m3, h-m4; update verification_state.yaml |
| FAIL (either condition not met) | → Block h-m3, h-m4; log failure in Serena memory; consider routing to alternative |

---

## Acceptance Criteria

1. `h-m1/experiment_results.json` contains `gate_result: "PASS"` with ICC(3,k) > 0.75 and tau_min >= 0.6
2. `h-m1/figures/gate_metrics.png` generated showing both metrics above thresholds
3. All 5 additional figures generated in `h-m1/figures/`
4. Code executes end-to-end with `python h-m1/code/run_experiment.py` without errors
5. Results consistent with h-e1 validated data (Alpaca vs WikiText-103 tau should be ≈0.786)

---

## Out of Scope

- Fine-tuning or training of any model
- LoRA rank allocation computation (h-m3, h-m4)
- Comparison with AdaLoRA or other rank allocation methods
- Sparsity measurement on non-MLP modules (attention layers)
- New activation sparsity measurement methodology (reuse h-e1 approach)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ICC(3,k) < 0.75 (hypothesis fails) | Low (LaRoSA evidence supports stability) | High (blocks h-m3/h-m4) | Pre-check tau values; consider fallback with 3/4 distributions |
| SST-2 very short sentences cause outlier sparsity | Medium | Medium | Padding to 512 tokens normalizes length effect; check tau for sst2 pairs |
| pingouin not installed | Low | Low | Add to requirements.txt; install with pip |
| LLaMA-3.1-8B not accessible | Low | High | Verify model access before experiment run |
