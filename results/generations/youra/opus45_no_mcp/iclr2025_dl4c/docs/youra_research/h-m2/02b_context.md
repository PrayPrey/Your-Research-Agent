# Phase 2B Context: H-M2

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Title:** Error Localization Varies by Type
**Gate:** SHOULD_WORK

## Hypothesis Statement

Under RLTF's error categorization, if errors are classified as U_line vs U_ignore, then U_line errors have significantly higher localization accuracy than U_ignore errors.

## Rationale

Tests whether RLTF's categorization actually separates reliable from unreliable localization. This is the foundation for gating logic.

## Variables

- **Independent:** error category (U_line vs U_ignore)
- **Dependent:** localization accuracy (correct line identification rate)
- **Controlled:** error traceback format, Python version

## Prerequisites

- **h-m1:** VALIDATED (PASS) - Fine-Grained Feedback Targets Error Line Tokens
  - Gradient concentration at error-line > gradient_other_lines: PASS (16.11x)
  - >80% penalty within ±2 lines: PASS (100%)

## Experimental Setup (from Phase 2A)

### Dataset
- **Name:** APPS
- **Type:** standard
- **Source:** https://github.com/hendrycks/apps
- **Train Size:** 5000 problems

### Model
- **Name:** CodeT5-large
- **Type:** encoder-decoder
- **Source:** Salesforce/codet5-large
- **Parameters:** 770M

## Success Criteria

- **Primary:** U_line accuracy > U_ignore accuracy (p<0.05)
- **Secondary:** U_line accuracy >80%, U_ignore accuracy <60%

## Verification Protocol

1. Collect 500+ error samples from APPS training, categorized by RLTF rules
2. For each error, compare traceback-reported line to actual bug location
3. Compute accuracy per category: correct_line / total_errors
4. Compare U_line accuracy vs U_ignore accuracy
5. Statistical test: chi-square for accuracy difference

## Failure Response

- IF fails: PIVOT to refined categorization scheme
