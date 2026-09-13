# Product Requirements Document: H-M2 Scale-Ensemble
## Scale-Ensemble Outperformance Validation

**Version**: 1.0
**Date**: 2026-08-24
**Hypothesis**: H-M2 (MECHANISM)
**Gate**: SHOULD_WORK

---

## Executive Summary

Validate that scale-ensemble (majority vote across 7B/70B/proprietary judges) outperforms the best individual judge by ≥3% accuracy on code correctness evaluation. This builds on H-E1's finding that different model scales exhibit statistically distinct FP/FN error patterns.

---

## Problem Statement

Individual LLM judges for code correctness have accuracy limitations. H-E1 demonstrated scale-dependent error patterns (7B over-accepts, proprietary conservative). The hypothesis is that combining judgments via majority vote can leverage complementary error profiles to exceed any single judge's performance.

---

## Functional Requirements

### FR1: Data Loading
- Load H-E1 judge outputs (per-problem verdicts for 3 scale tiers)
- Load EvalPlus ground truth from cached HumanEval+ (164 problems)
- Verify data integrity: all 164 problems have verdicts from all 3 judges

### FR2: Best Single Judge Identification
- Compute accuracy for each judge tier against ground truth
- Identify best single judge (expected: GPT-4/proprietary)
- Store per-judge metrics: accuracy, FPR, FNR

### FR3: Ensemble Methods
- **Majority Vote**: Simple 2-of-3 consensus
- **Weighted Majority**: Weight by per-tier accuracy from H-E1
- **Unanimous Agreement**: Flag high-confidence cases (all agree)

### FR4: Statistical Comparison
- Build McNemar contingency table (ensemble vs best single)
- Compute McNemar test statistic and p-value (exact test for n<25 discordant pairs)
- Report accuracy difference with confidence interval

### FR5: Ablation Variants
- **AB1**: Majority vote only (primary)
- **AB2**: Weighted majority (weight by H-E1 accuracy)
- **AB3**: 2-tier subset (exclude 7B, test 70B+proprietary)
- **AB4**: Random baseline (random selection among judges)

### FR6: Baselines
- Best single judge accuracy
- Random ensemble (average of individual accuracies)
- CodeBERTScore (~58% from literature)

### FR7: Metrics and Reporting
- Primary: Accuracy improvement percentage (ensemble - best single)
- Secondary: McNemar p-value, chi² statistic
- Tertiary: Per-category analysis (unanimous vs split verdicts)

---

## Non-Functional Requirements

### NFR1: Compute Efficiency
- Total runtime < 5 minutes (no GPU required)
- Reuse cached H-E1 data (no new model inference)

### NFR2: Reproducibility
- Deterministic ensemble computation
- Seed-free (no randomization in primary ensemble)

### NFR3: Statistical Rigor
- Use exact McNemar test for small discordant counts
- Report 95% confidence intervals

---

## Success Criteria

| Criterion | Success | Partial | Fail |
|-----------|---------|---------|------|
| Accuracy improvement | ≥3% | 2-3% | <2% |
| McNemar p-value | <0.05 | <0.10 | ≥0.10 |
| Sample coverage | 164/164 | N/A | <164 |

---

## Dependencies

### Data Dependencies
- H-E1 judge outputs (per-problem verdicts)
- EvalPlus HumanEval+ ground truth (cached)

### Package Dependencies
- `mlxtend>=0.23.0` (McNemar test)
- `numpy`, `pandas` (data manipulation)
- `evalplus` (dataset loading)

---

## Out of Scope

- New model inference (reuse H-E1 outputs)
- Training or fine-tuning
- Cross-dataset generalization (MBPP+ for replication only)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Best single already ≥95% | Document ceiling effect; focus on error reduction |
| Correlated errors | Expected from H-E1; this IS the mechanism |
| Small sample (164) | Exact McNemar test; MBPP+ replication |

---

## Appendix: Phase 2C Traceability

- **Dataset**: HumanEval+ (164) ✓
- **Models**: 7B, 70B, Proprietary ✓
- **Ensemble strategies**: Majority, weighted, unanimous ✓
- **Baselines**: Best single, random, CodeBERTScore ✓
- **Ablations**: AB1-AB4 ✓
- **Statistical test**: McNemar ✓
