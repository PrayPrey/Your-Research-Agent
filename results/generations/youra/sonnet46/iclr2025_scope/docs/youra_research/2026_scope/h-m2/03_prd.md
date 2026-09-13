# Product Requirements Document: h-m2

**stepsCompleted:** [step-01-initialize, step-02-prd]
**Hypothesis:** h-m2 — Epsilon-Threshold Robustness of MLP Activation Sparsity Variation
**Date:** 2026-05-08
**Phase:** Phase 3 Implementation Planning
**PRD Version:** 1.0

---

## Executive Summary

This PRD defines the implementation requirements for validating **h-m2**: that layer-wise MLP activation sparsity variation in LLaMA-3-8B (CV > 0.3) is robust to epsilon threshold choice, holding for at least 3 of 4 epsilon values in {0.001, 0.01, 0.05, 0.1}, and that layer rank ordering is stable across epsilon values (Kendall's tau between epsilon conditions >= 0.7). This is a pure measurement study that extends h-e1's validated infrastructure to compute **cross-epsilon rank ordering stability** — a new metric not measured in h-e1. Success directly unblocks h-m3 (which requires both h-m1 and h-m2 to PASS).

**Hypothesis Type:** MECHANISM (INCREMENTAL — depends on h-e1 PASS)
**Gate Type:** MUST_WORK
**Gate Condition:** CV > 0.3 for ≥ 3 of 4 epsilon values AND Kendall's tau ≥ 0.7 for ≥ 1 adjacent epsilon pair
**Task Budget:** 30 tasks max (FULL tier)

---

## Problem Statement

H-E1 validated that LLaMA-3-8B layer-wise MLP activation sparsity varies significantly (CV=0.544 > 0.3) and already confirmed all 4 epsilon values yield CV > 0.3 (as secondary criteria). However, H-E1 did not measure **cross-epsilon rank ordering stability**: whether the layer that is "most sparse" under epsilon=0.001 is also "most sparse" under epsilon=0.1. This matters because:

1. The LoRA rank allocation algorithm uses sparsity **ranking** (not absolute values) to decide per-layer rank
2. If layer ranking changes dramatically between epsilon choices, the allocation is epsilon-sensitive — a critical fragility
3. H-M2 quantifies this fragility with Kendall's tau across all 6 pairwise epsilon combinations

If either gate condition fails (CV collapses for ≥ 2 epsilon values OR all 6 cross-epsilon tau < 0.7), the sparsity signal is threshold-sensitive and cannot reliably guide rank allocation for h-m3/h-m4.

---

## Functional Requirements

### FR-1: Dataset Loading (Reuse from h-e1)

- **FR-1.1:** Load Alpaca calibration set: `tatsu-lab/alpaca`, train split, 512 samples, same seed=42 as h-e1
- **FR-1.2:** Tokenize with `meta-llama/Meta-Llama-3-8B` AutoTokenizer, max_length=512, padding=True, truncation=True
- **FR-1.3:** DataLoader: batch_size=8, shuffle=False
- **FR-1.4 (Secondary):** Load WikiText-103: `wikitext-103-raw-v1`, test split, 512 samples — for cross-distribution secondary metric (tau per epsilon, Alpaca vs. WikiText per epsilon value)
- **FR-1.5:** All dataset loading reuses h-e1/code/data_utils.py via copy into h-m2/code/

### FR-2: LLaMA-3-8B Activation Sparsity Measurement (Multi-Epsilon)

- **FR-2.1:** Load `meta-llama/Meta-Llama-3-8B` with `torch_dtype=torch.float16, device_map="auto"`, set eval mode
- **FR-2.2:** Register forward hooks on `model.model.layers[i].mlp.gate_proj` for all 32 layers (reuse h-e1/code/measure_sparsity.py pattern)
- **FR-2.3:** For each of 4 epsilon values {0.001, 0.01, 0.05, 0.1}, compute per-layer sparsity as mean fraction of `|activations| < epsilon` over 512 Alpaca samples — yielding shape (32,) per epsilon
- **FR-2.4:** Measure all 4 epsilon values in a single forward pass sequence (avoid reloading model per epsilon)
- **FR-2.5:** Seeds: `numpy.random.seed(42)`, `torch.manual_seed(42)` before measurement run
- **FR-2.6:** Set `CUDA_VISIBLE_DEVICES` to single GPU (lowest memory usage) before running

### FR-3: CV Robustness Check (Per Epsilon)

- **FR-3.1:** For each epsilon value, compute `CV = std(sparsity_vec) / mean(sparsity_vec)` over the 32-layer sparsity vector
- **FR-3.2:** Count how many epsilon values satisfy `CV > 0.3`
- **FR-3.3:** Primary gate check (CV component): `count_cv_pass >= 3` (at least 3 of 4 epsilon values)
- **FR-3.4:** Report CV value for each epsilon in results JSON and stdout

### FR-4: Cross-Epsilon Rank Ordering Stability (Kendall's Tau)

- **FR-4.1:** Compute all C(4,2) = 6 pairwise Kendall's tau between epsilon-indexed sparsity vectors
- **FR-4.2:** Pairs: 0.001_vs_0.01, 0.001_vs_0.05, 0.001_vs_0.1, 0.01_vs_0.05, 0.01_vs_0.1, 0.05_vs_0.1
- **FR-4.3:** Use `scipy.stats.kendalltau(sparsity_eps1, sparsity_eps2, variant='b')` for tie-corrected tau_b
- **FR-4.4:** Record tau value and p-value for each pair
- **FR-4.5:** Primary gate check (tau component): at least 1 adjacent pair (e.g., 0.01_vs_0.05) has `tau >= 0.7`
- **FR-4.6:** Report all 6 tau values in results JSON and stdout

### FR-5: Secondary Metric — Cross-Distribution Tau Per Epsilon

- **FR-5.1:** For each epsilon value, compute Kendall's tau between Alpaca sparsity vector and WikiText-103 sparsity vector
- **FR-5.2:** Report `tau_calibration[epsilon]` for all 4 epsilon values
- **FR-5.3:** Expected: all 4 values >= 0.6 (h-e1 secondary criteria confirmed this for epsilon=0.01)
- **FR-5.4:** This is a secondary (non-gate) metric for paper reporting

### FR-6: Gate Evaluation and Result Reporting

- **FR-6.1:** Evaluate combined gate: PASS if `count_cv_pass >= 3` AND `max_cross_epsilon_tau >= 0.7`; FAIL otherwise
- **FR-6.2:** Generate structured results JSON: `h-m2/experiment_results.json` with all CV values, all 6 cross-epsilon tau values, gate status
- **FR-6.3:** Print gate evaluation summary to stdout with all metrics
- **FR-6.4:** On FAIL: log which condition(s) failed and numeric gaps to thresholds
- **FR-6.5:** Verify mechanism activation: all 32 layers measured, all 4 epsilon vectors computed, all 6 pairs computed

### FR-7: Visualization (Required Figures)

- **FR-7.1 (Mandatory):** Gate metrics bar chart: CV values per epsilon and max cross-epsilon tau vs. thresholds → `h-m2/figures/gate_metrics.png`
- **FR-7.2:** Cross-epsilon tau heatmap: 4×4 symmetric Kendall's tau matrix (6 off-diagonal values, diagonal=1.0) → `h-m2/figures/cross_epsilon_tau_heatmap.png`
- **FR-7.3:** Sparsity profile overlay: 32-layer sparsity profiles for all 4 epsilon values on single plot → `h-m2/figures/sparsity_profiles_overlay.png`
- **FR-7.4:** CV vs. epsilon plot: bar/line chart showing CV for each epsilon with 0.3 threshold line → `h-m2/figures/cv_per_epsilon.png`
- **FR-7.5:** All figures saved to `h-m2/figures/` directory

### FR-8: Code Reuse from h-e1

- **FR-8.1:** Reuse `h-e1/code/measure_sparsity.py` — forward hook measurement infrastructure; copy into h-m2/code/
- **FR-8.2:** Reuse `h-e1/code/data_utils.py` — Alpaca and WikiText-103 dataset loaders; copy into h-m2/code/
- **FR-8.3:** Create new `h-m2/code/config.py` extending h-e1 ExperimentConfig with cross-epsilon tau thresholds
- **FR-8.4:** Create new `h-m2/code/compute_metrics.py` for CV, cross-epsilon tau, gate evaluation
- **FR-8.5:** Create new `h-m2/code/visualize.py` for h-m2-specific figures (4 plots)
- **FR-8.6:** Create new `h-m2/code/run_experiment.py` as main entry point

---

## Non-Functional Requirements

### NFR-1: Performance
- **NFR-1.1:** Total runtime ≤ 15 minutes on single GPU (2 datasets × ~5 min each; much simpler than h-m1)
- **NFR-1.2:** Peak GPU memory ≤ 20GB (LLaMA-3-8B float16 ≈ 15GB + hook overhead)
- **NFR-1.3:** CPU memory ≤ 16GB for dataset loading and statistics

### NFR-2: Reproducibility
- **NFR-2.1:** Fixed seeds (numpy seed=42, torch seed=42) matching h-e1 exactly
- **NFR-2.2:** Deterministic data sampling (shuffle=False, same range(512) selection as h-e1)
- **NFR-2.3:** All results saved to `experiment_results.json` for Phase 6 paper writing

### NFR-3: Code Quality
- **NFR-3.1:** Modular design: separate modules for config, data loading, measurement, metrics, visualization
- **NFR-3.2:** Each module independently testable with pytest
- **NFR-3.3:** Requirements.txt specifying all dependencies

### NFR-4: Environment
- **NFR-4.1:** Single GPU only (`CUDA_VISIBLE_DEVICES` set to lowest-memory GPU)
- **NFR-4.2:** Python 3.10+, PyTorch 2.x
- **NFR-4.3:** HuggingFace cache directory available for model/dataset downloads

---

## Data Specification

### Primary Dataset
| Property | Value |
|----------|-------|
| Name | Stanford Alpaca |
| HuggingFace ID | `tatsu-lab/alpaca` |
| Split | train |
| Samples | 512 (range(512), seed=42) |
| Fields used | `instruction + input + output` |
| Download | Auto via `load_dataset("tatsu-lab/alpaca")` |
| Manual download needed | No |

### Secondary Dataset (for FR-5)
| Property | Value |
|----------|-------|
| Name | WikiText-103 |
| HuggingFace ID | `wikitext` config `wikitext-103-raw-v1` |
| Split | test |
| Samples | 512 sliding-window chunks |
| Download | Auto via `load_dataset("wikitext", "wikitext-103-raw-v1")` |
| Manual download needed | No |

---

## Dependencies

### External Dependencies
| Dependency | Version | Purpose |
|-----------|---------|---------|
| torch | ≥2.0 | Model inference, forward hooks |
| transformers | ≥4.40 | LLaMA-3-8B loading, tokenizer |
| datasets | ≥2.18 | HuggingFace dataset loading |
| numpy | ≥1.24 | Array operations, CV computation |
| scipy | ≥1.11 | Kendall's tau (scipy.stats.kendalltau) |
| matplotlib | ≥3.7 | Figure generation |
| seaborn | ≥0.12 | Heatmap visualization |

**Note:** `pingouin` is NOT required for h-m2 (no ICC computation). Simpler dependency set than h-m1.

### Internal Dependencies
| Dependency | Source | Status |
|-----------|--------|--------|
| h-e1/code/measure_sparsity.py | Phase 4 h-e1 | VALIDATED (gate PASS) |
| h-e1/code/data_utils.py | Phase 4 h-e1 | VALIDATED |
| meta-llama/Meta-Llama-3-8B | HuggingFace Hub | Must be accessible |
| verification_state.yaml | Phase 2B/2C | Exists, h-m2 status IN_PROGRESS |

---

## Success Criteria

### Primary Gate (MUST_WORK)
| Criterion | Threshold | Expected | Method |
|-----------|-----------|----------|--------|
| CV robustness | CV > 0.3 for ≥ 3/4 epsilon values | All 4 (h-e1 secondary confirmed) | `scipy.stats.variation(sparsity_vec)` |
| Cross-epsilon tau | max(tau) ≥ 0.7 for ≥ 1 adjacent pair | High (>0.8) — ICC=0.9846 implies structural stability | `scipy.stats.kendalltau(eps_i, eps_j, variant='b')` |

### Secondary Validation
| Criterion | Target | Purpose |
|-----------|--------|---------|
| tau_calibration per epsilon | ≥ 0.6 for all 4 epsilon | Confirms h-e1 cross-dataset stability extends to all epsilons |
| All 6 cross-epsilon tau ≥ 0.7 | All 6 | Full stability across all threshold pairs |
| Code runs without error | 0 exceptions | Basic correctness |
| All 4 figures generated | 4 PNG files | Visualization completeness |

### Gate Outcome Actions
| Gate Result | Action |
|-------------|--------|
| PASS (both conditions met) | → Unblocks h-m3 (jointly with h-m1 PASS already satisfied) |
| FAIL (CV collapses or tau < 0.7) | → Block h-m3; PIVOT to L1 activation magnitude as alternative proxy |

---

## Acceptance Criteria

1. `h-m2/experiment_results.json` contains `gate_result: "PASS"` with CV pass count ≥ 3 and max cross-epsilon tau ≥ 0.7
2. `h-m2/figures/gate_metrics.png` generated showing both metrics vs. thresholds
3. All 3 additional figures generated in `h-m2/figures/`
4. Code executes end-to-end with `python h-m2/code/run_experiment.py` without errors
5. Results consistent with h-e1 validated Alpaca sparsity data (epsilon=0.01 CV should be ≈ 0.544)

---

## Out of Scope

- Fine-tuning or training of any model
- LoRA rank allocation computation (h-m3, h-m4)
- New calibration distributions beyond Alpaca + WikiText-103 (h-m1 covers multi-distribution)
- ICC(3,k) computation (h-m1 covers cross-distribution reliability; h-m2 covers cross-epsilon stability)
- New activation sparsity measurement methodology

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CV collapses at extreme epsilons (0.001 or 0.1) | Low (h-e1 secondary all pass) | Medium | Gate requires only 3/4; 1 failure tolerated |
| Cross-epsilon tau < 0.7 (unexpected ordering flip) | Low (ICC=0.9846 implies stability) | High (blocks h-m3) | Check adjacent pairs first (0.01_vs_0.05 expected high) |
| meta-llama/Meta-Llama-3-8B access issue | Low | High | Use cached weights from h-e1 run |
| Hook not firing (wrong module path) | Very Low (validated by h-e1) | Medium | Verify with 1-batch test before full run |
