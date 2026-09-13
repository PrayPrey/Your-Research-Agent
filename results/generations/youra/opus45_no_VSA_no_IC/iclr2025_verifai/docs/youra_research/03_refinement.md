# Phase 2A Refinement Summary

**Hypothesis ID:** h-sa-correlation-001  
**Gap:** SA-Correctness Correlation Quantification  
**Status:** Phase 2B Ready  
**Date:** 2026-08-24

---

## Core Hypothesis

Static analysis metrics (pylint score, mypy error count, radon cyclomatic complexity) exhibit **moderate positive correlation (point-biserial r ≥ 0.35)** with functional correctness (pass@1) on HumanEval/MBPP for LLM-generated code, **after controlling for code length** as a confounding variable.

---

## Testable Predictions

| # | Prediction | Success Criterion | Measurement |
|---|------------|-------------------|-------------|
| 1 | Pylint score correlates with pass@1 | r ≥ 0.35, p < 0.05 | Partial point-biserial |
| 2 | Ensemble SA score beats individual | r_ensemble > max(r_individual) | Weighted combination |
| 3 | Correlation generalizes across LLMs | std(r_per_model) < 0.15 | Cross-model comparison |

---

## Variables

**Independent (SA Metrics):**
- Pylint score (0-10)
- Mypy error count
- Mypy type coverage (%)
- Radon cyclomatic complexity

**Dependent:**
- Pass@1 (binary: 0/1)

**Control:**
- Code length (LOC or tokens)

---

## Experimental Setup

- **Datasets:** HumanEval (164) + MBPP (399) = 563 problems
- **LLMs:** GPT-4, Claude-3-Opus, Llama-70B, Codestral
- **Samples:** 100 completions/problem/LLM ≈ 225K samples
- **SA Tools:** pylint, mypy, radon, bandit
- **Ground Truth:** EvalPlus test execution

---

## Novelty Claims

1. First quantified correlation study between SA metrics and functional correctness
2. First to control for code length confound
3. First to test cross-model generalization of SA predictiveness

---

## Feasibility Assessment

| Criterion | Status |
|-----------|--------|
| Existing benchmarks | ✅ HumanEval, MBPP, EvalPlus |
| No new frameworks | ✅ Standard SA tools |
| No synthetic data | ✅ LLM generations are real |
| No human evaluation | ✅ Automated test execution |

---

## Round Table Consensus

| Persona | Assessment | Confidence |
|---------|------------|------------|
| 🔭 Dr. Nova | SUPPORT | 85% |
| 🔬 Prof. Vera | SUPPORT | 90% |
| 🎯 Dr. Sage | SUPPORT | 80% |
| ⚙️ Prof. Pax | SUPPORT | 95% |
| 🛡️ Dr. Ally | STRONG SUPPORT | 88% |
| 🔍 Prof. Rex | CONDITIONAL | 75% |

**Average Confidence:** 85.5%  
**Recommendation:** PROCEED TO PHASE 2B

---

## Phase 2B Seeds

1. Define exact ensemble weighting strategy
2. Statistical power analysis for sample size
3. Threshold for "actionable" correlation in rejection sampling
