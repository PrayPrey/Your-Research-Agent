# Product Requirements Document: H-M3
## Unreliable Localization Causes Gradient Noise

**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Date:** 2026-08-19
**Prerequisites:** H-M2 (VALIDATED)

---

## 1. Executive Summary

H-M3 tests whether applying fine-grained penalties at traceback-reported locations causes gradient noise when error localization is unreliable. Building on H-M1's proof that gradients concentrate at traceback lines (16.11x ratio) and H-M2's proof that U_ignore errors have only 20% localization accuracy vs 100% for U_line, this experiment measures whether U_ignore gradient concentration targets WRONG tokens (noise) vs correct source locations.

**Success Criteria:**
- Mean GT concentration (U_line) > Mean GT concentration (U_ignore)
- Noise ratio for U_ignore samples > 1.0 (gradient at traceback > gradient at ground truth)
- Statistical significance: p < 0.05

---

## 2. Problem Statement

### 2.1 Background
H-M1 proved fine-grained penalties cause gradient concentration at traceback locations. H-M2 proved U_ignore error tracebacks are unreliable (80% wrong). The question: does unreliable localization translate to gradient NOISE (signal at wrong tokens)?

### 2.2 Core Question
When fine-grained penalties are applied to U_ignore errors, do gradients concentrate at:
- (a) The traceback-reported line (wrong location = noise), or
- (b) The actual bug location (correct = signal)?

If (a), this proves the mechanism by which U_ignore errors introduce noise into training.

---

## 3. Functional Requirements

### FR-1: Sample Generation with Ground Truth
- Generate 500 U_line error samples and 500 U_ignore error samples from APPS
- Each sample includes: code, traceback, error_type, traceback_line, ground_truth_line
- Reuse H-M2's ground_truth.py for actual bug location extraction
- Reuse H-M1's sample_collector.py for traceback parsing

### FR-2: Gradient Concentration at Ground Truth
- For each sample, measure gradient magnitude at:
  - Traceback-reported line tokens (tb_grad)
  - Ground-truth bug line tokens (gt_grad)
  - Other line tokens (other_grad)
- Compute GT concentration ratio: gt_grad / other_grad
- Compute noise ratio: tb_grad / gt_grad (>1 means gradient at wrong place)

### FR-3: Error Type Stratification
- Separate analysis for U_line samples (expected: high GT concentration)
- Separate analysis for U_ignore samples (expected: low GT concentration, high noise)
- Compare distributions between categories

### FR-4: Statistical Comparison
- Independent t-test: U_line GT concentration vs U_ignore GT concentration
- Mann-Whitney U test (non-parametric alternative)
- Cohen's d effect size calculation
- 95% bootstrap confidence intervals

### FR-5: Visualization
- **Required:** Box plot comparing GT concentration ratio for U_line vs U_ignore
- Histogram of noise_ratio for U_ignore samples
- Gradient heatmap example: one U_line vs one U_ignore sample
- Scatter plot: GT concentration vs noise_ratio by error type

---

## 4. Data Specification

### 4.1 Primary Dataset
- **Name:** APPS (subset)
- **Source:** codeparrot/apps
- **Loading:** `datasets.load_dataset("codeparrot/apps", split="train")`
- **Preprocessing:** Filter for execution errors, categorize by error type

### 4.2 Sample Requirements
- 500 U_line error samples (traceback = ground truth)
- 500 U_ignore error samples (traceback ≠ ground truth 80% of time)
- Ground truth from H-M2's AST-based heuristics

---

## 5. Model Specification

### 5.1 Baseline Model
- **Name:** CodeT5-small (PoC) / CodeT5-large (full)
- **Source:** Salesforce/codet5-small
- **Parameters:** 60M (small) / 770M (large)
- **Purpose:** Pre-trained model for gradient analysis (no fine-tuning)

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| GT concentration (U_line) | gradient_at_ground_truth / gradient_elsewhere | Higher than U_ignore |
| GT concentration (U_ignore) | gradient_at_ground_truth / gradient_elsewhere | Lower than U_line |
| Noise ratio (U_ignore) | gradient_at_traceback / gradient_at_ground_truth | > 1.0 |

### 6.2 Secondary Metrics
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Concentration difference | mean(U_line) - mean(U_ignore) | > 0, p < 0.05 |
| Effect size | Cohen's d between distributions | d > 0.5 (medium effect) |

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
| sample_collector.py | h-m1/code/ | classify_error, parse_traceback_line, execute_code_safely |
| ground_truth.py | h-m2/code/ | find_bug_line_ast, annotate_ground_truth |
| config.py | h-m2/code/ | U_LINE_ERRORS, U_IGNORE_ERRORS sets |

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Analysis of 1000 samples should complete in <2 hours on single A100

### NFR-2: Reproducibility
- All random seeds fixed (seed=42)
- Results deterministic given same input samples

### NFR-3: Statistical Rigor
- Report 95% CI for all point estimates
- Use both parametric and non-parametric tests

---

## 9. Success Criteria

### 9.1 PoC Pass (Minimum)
1. Code runs without error
2. Mean GT concentration (U_line) > Mean GT concentration (U_ignore)
3. Difference is statistically significant (p < 0.05)

### 9.2 Full Validation
1. All PoC criteria met
2. Mean noise ratio for U_ignore > 1.0 (gradient concentrates at WRONG location)
3. Effect size Cohen's d > 0.5
4. All 4 required figures generated

---

## 10. Out of Scope

- Training experiments (this is analysis only)
- Multi-model comparison
- Runtime optimization
- Production deployment
