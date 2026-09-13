# Adversary Review - Round 2

## Executive Summary
- FATAL: 0
- MAJOR: 0
- Recommendation: CONDITIONAL_ACCEPT

## Numerical Verification Log

| Claim | Paper Value | Source (04_validation.md) | Match |
|-------|-------------|---------------------------|-------|
| BERT upper sparsity | 1.18% | 0.0118 (1.18%) | YES |
| GPT-2 upper sparsity | 100% | 1.0 (100%) | YES |
| Sparsity diff | 98.82% | 0.9882 (98.82%) | YES |
| BERT top eigenvalue | 0.0455 | 0.0455 | YES |
| GPT-2 top eigenvalue | 0.502 | 0.502 | YES |
| Eigenvalue diff | 90.93% | 90.93% | YES |
| Eigenvalue ratio | 11x | 11.03x | YES |
| TRAK proj_64 BERT AUC | 0.941 | 0.941 | YES |
| TRAK proj_64 GPT-2 AUC | 0.944 | 0.944 | YES |
| TRAK proj_64 diff | 0.36% | 0.36% | YES |
| TRAK proj_256 diff | 0.56% | 0.56% | YES |
| TRAK proj_1024 diff | 0.11% | 0.11% | YES |
| TracIn ckpt1 BERT | 0.979 | 0.979 | YES |
| TracIn ckpt1 GPT-2 | 0.949 | 0.949 | YES |
| TracIn ckpt1 diff | +3.03% | +3.03% | YES |
| TracIn ckpt2 diff | +1.42% | +1.42% | YES |
| TracIn ckpt3 diff | +1.13% | +1.13% | YES |
| EK-FAC BERT AUC | 0.941 | 0.941 | YES |
| EK-FAC GPT-2 AUC | 0.944 | 0.944 | YES |
| EK-FAC table diff | +0.32% | +0.27% (ground truth) | MINOR |

## Issues from R1 - Verification

### MAJOR-1: TRAK Results Table Discrepancy
**Status: FIXED**
- Table now shows correct values matching validation file
- proj_64=0.36%, proj_256=0.56%, proj_1024=0.11%
- BERT AUC correctly shows 0.941 at all budgets

### MAJOR-2: TracIn Table Has Incorrect Structure
**Status: FIXED**
- TracIn table now shows correct decreasing BERT AUC pattern (0.979→0.977→0.976)
- GPT-2 values correct (0.949→0.963→0.965)
- Differences correctly calculated

## New Issues Found

### MINOR-1: EK-FAC Difference Inconsistency
- Abstract/conclusion: "0.27%" difference
- Table: "+0.32%" difference
- Ground truth yaml: 0.27%
- H-M4 validation: shows 0.27% in prediction table
- **Recommendation:** Minor cosmetic fix; use 0.32% consistently (matches calculated value from AUC 0.944-0.941)

No FATAL or MAJOR issues identified.

## Credibility Assessment
- Baselines fairly compared: YES (same params, layers, training protocol)
- Limitations honestly stated: YES (2 seeds, single dataset, model scale)
- Statistical claims valid: YES (p-values correctly reported, significance caveats clear)

---

*R2 Review Complete*
