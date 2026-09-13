# Product Requirements Document: H-M4
## Gating Removes Noise, Improves Signal

**Hypothesis ID:** H-M4
**Type:** MECHANISM
**Date:** 2026-08-19
**Prerequisites:** H-M3 (VALIDATED)

---

## 1. Executive Summary

H-M4 tests whether gating fine-grained penalties to U_line errors only improves overall gradient signal-to-noise ratio (SNR) compared to applying fine-grained penalties unconditionally. Building on:
- H-M1: Gradients concentrate at traceback lines (16.11x ratio)
- H-M2: U_line has 100% localization accuracy vs 20% for U_ignore
- H-M3: U_ignore errors produce noisier gradients (concentration 1.398 vs 1.594)

This experiment compares aggregate SNR between two policies:
- **Fine-always**: Apply fine-grained penalty to ALL errors
- **Fine-gated**: Apply fine-grained penalty only to U_line errors

**Success Criteria:**
- SNR_fine_gated > SNR_fine_always
- Improvement statistically significant (p < 0.05)
- 95% CI non-overlapping

---

## 2. Problem Statement

### 2.1 Background
H-M3 proved that per-sample gradient concentration differs between U_line (1.594) and U_ignore (1.398) errors. The question: when aggregating across a batch of errors, does excluding U_ignore from fine-grained penalties improve overall signal-to-noise?

### 2.2 Core Question
Does gating (excluding noisy U_ignore samples from fine-grained penalties) produce better aggregate gradient quality than unconditional application?

---

## 3. Functional Requirements

### FR-1: Sample Collection
- Reuse H-M3 sample collection: 500 samples (250 U_line + 250 U_ignore)
- Each sample includes: code, traceback, error_type, traceback_line, ground_truth_line
- Reuse H-M3's NoiseSample dataclass and collection functions

### FR-2: Gradient Collection
- For each sample, compute gradients using H-M1's extract_token_gradients
- Store per-sample gradient metrics: signal (gt_grad), noise (non-gt variance)
- Reuse H-M3's measure_sample_noise function

### FR-3: Policy Comparison
- **Fine-always policy**: Include ALL 500 samples in aggregate SNR
- **Fine-gated policy**: Include only 250 U_line samples in aggregate SNR
- Compute SNR = mean(signal) / mean(noise) for each policy

### FR-4: Statistical Validation
- Bootstrap 95% confidence intervals (1000 iterations)
- Permutation test for significance (p < 0.05)
- Effect size: percentage improvement

### FR-5: Visualization
- **Required:** SNR comparison bar chart with error bars
- SNR bootstrap distribution boxplot
- Signal vs noise scatter by policy
- Per-error-type contribution breakdown

---

## 4. Data Specification

### 4.1 Primary Dataset
- **Name:** APPS (subset)
- **Source:** codeparrot/apps
- **Loading:** `datasets.load_dataset("codeparrot/apps", split="train[:500]")`
- **Preprocessing:** Filter for execution errors, categorize by error type

### 4.2 Sample Requirements
- 250 U_line error samples
- 250 U_ignore error samples
- Balanced distribution for fair comparison

---

## 5. Model Specification

### 5.1 Baseline Model
- **Name:** CodeT5-small
- **Source:** Salesforce/codet5-small
- **Parameters:** 60M
- **Purpose:** Gradient analysis (no fine-tuning)

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| SNR_fine_always | mean(signal) / mean(noise) for all samples | Baseline |
| SNR_fine_gated | mean(signal) / mean(noise) for U_line only | > SNR_fine_always |
| Improvement % | (gated - always) / always × 100 | > 0% |

### 6.2 Secondary Metrics
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| p-value | Permutation test | < 0.05 |
| 95% CI overlap | Bootstrap intervals | Non-overlapping |

---

## 7. Dependencies

### 7.1 Python Packages
- torch >= 2.0.0
- transformers >= 4.30.0
- datasets >= 2.12.0
- scipy >= 1.10.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- seaborn >= 0.12.0

### 7.2 Base Hypothesis Modules (Reused)
| Module | Source | Functions |
|--------|--------|-----------|
| gradient_analysis.py | h-m1/code/ | extract_token_gradients, tokenize_with_lines |
| noise_analysis.py | h-m3/code/ | measure_sample_noise, run_noise_analysis |
| sample_builder.py | h-m3/code/ | NoiseSample, collect_stratified_samples |
| config.py | h-m3/code/ | H_M3_Config, NoiseConfig |

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Analysis of 500 samples should complete in <1 hour on single A100

### NFR-2: Reproducibility
- All random seeds fixed (seed=42)
- Results deterministic given same input samples

### NFR-3: Statistical Rigor
- Report 95% CI for all point estimates
- Bootstrap with 1000 iterations minimum

---

## 9. Success Criteria

### 9.1 PoC Pass (Minimum)
1. Code runs without error
2. SNR_fine_gated > SNR_fine_always
3. p < 0.05 (permutation test)

### 9.2 Full Validation
1. All PoC criteria met
2. 95% CI non-overlapping
3. All 4 required figures generated
4. Improvement > 5% (expected 10-15% based on H-M3)

---

## 10. Out of Scope

- Full training experiments
- Multi-model comparison
- Runtime optimization
- Production deployment
