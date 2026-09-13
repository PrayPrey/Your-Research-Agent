# Product Requirements Document: H-M2

**Hypothesis:** Error Localization Varies by Type
**Type:** MECHANISM
**Date:** 2026-08-19
**Author:** Anonymous

---

## 1. Executive Summary

Validate that RLTF's error categorization (U_line vs U_ignore) correlates with actual traceback localization accuracy. This MECHANISM hypothesis tests the theoretical foundation of error-type gating.

**Core Claim:** U_line errors have significantly higher localization accuracy than U_ignore errors.

---

## 2. Problem Statement

RLTF categorizes Python errors into U_line (traceback points to actual bug) and U_ignore (traceback misleading). This categorization is based on exception semantics, but has not been empirically validated for localization accuracy differences.

**Research Question:** Does the U_line/U_ignore categorization actually separate reliable from unreliable error localization?

---

## 3. Functional Requirements

### FR-1: Error Sample Collection
- Generate 500+ failing code samples from APPS training set
- Use CodeT5-small for efficient error generation
- Target: 250+ U_line errors, 250+ U_ignore errors
- Reuse H-M1 error samples where categorization exists

### FR-2: Error Categorization
- Implement RLTF categorization rules from paper Appendix B
- U_LINE_ERRORS: SyntaxError, IndentationError, NameError, TypeError, AttributeError, ZeroDivisionError, IndexError, KeyError, ValueError
- U_IGNORE_ERRORS: AssertionError, RuntimeError, TimeoutError, RecursionError, MemoryError

### FR-3: Ground Truth Localization
- For each error sample, determine actual bug line location
- Approach: AST-based heuristics with manual spot-check validation
- Tolerance: ±2 lines for accuracy measurement

### FR-4: Localization Accuracy Measurement
- Compare traceback-reported line to actual bug line
- Compute accuracy per category: (correct_in_tolerance / total) × 100%
- Output: U_line_accuracy, U_ignore_accuracy

### FR-5: Statistical Comparison
- Chi-square test for accuracy difference significance
- Mann-Whitney U test as secondary validation
- Success: p < 0.05 for accuracy difference

### FR-6: Visualization
- Bar chart: U_line vs U_ignore accuracy with error bars
- Distribution plot: traceback-to-actual line distances
- Breakdown by specific exception type

---

## 4. Data Specification

### Primary Dataset
- **Name:** APPS (Automated Programming Progress Standard)
- **Source:** https://github.com/hendrycks/apps
- **Loading:** `load_dataset("codeparrot/apps", split="train")`
- **Size:** 5,000 training problems
- **Note:** Auto-downloads via HuggingFace datasets (no manual download needed)

### Model for Error Generation
- **Name:** CodeT5-small
- **Source:** Salesforce/codet5-small
- **Loading:** `AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-small")`
- **Purpose:** Generate failing code samples for error analysis

### H-M1 Samples (Reuse)
- **Location:** ../h-m1/code/ or equivalent checkpoint
- **Content:** 500 samples with error categories (U_line: 329, U_ignore: 171)
- **Note:** Reuse if available to maintain consistency

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (42) for all random operations
- Save all intermediate results to checkpoint files

### NFR-2: Statistical Power
- Minimum 250 samples per category for chi-square validity
- Report confidence intervals on accuracy estimates

### NFR-3: Validation
- Manual spot-check of 50 ground truth annotations
- Report inter-rater reliability if multiple annotators

---

## 6. Success Criteria

| Metric | Target | Type |
|--------|--------|------|
| U_line accuracy > U_ignore accuracy | p < 0.05 | Primary |
| U_line accuracy | > 80% | Secondary |
| U_ignore accuracy | < 60% | Secondary |
| Sample count per category | ≥ 250 | Quality |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12.0
transformers>=4.20.0
datasets>=2.0.0
scipy>=1.7.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.11.0
pyyaml>=6.0
```

### 7.2 External References
- RLTF Paper: Error categorization (Appendix B)
- H-M1 Codebase: Error sample generation patterns
- Python Exception Hierarchy: Traceback semantics

---

## 8. Evaluation Protocol

1. Load APPS dataset (auto-download)
2. Generate/load error samples (500+ total)
3. Categorize by RLTF rules (U_line vs U_ignore)
4. Determine ground truth bug locations (AST heuristics)
5. Compute localization accuracy per category
6. Run chi-square test for significance
7. Generate visualizations
8. Report results with confidence intervals

---

## 9. Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| Error categories | RLTF Paper Appendix B |
| Sample targets | Phase 2C Experiment Brief |
| Success criteria | Phase 2B Verification Plan |
| Statistical tests | Standard research practice |
