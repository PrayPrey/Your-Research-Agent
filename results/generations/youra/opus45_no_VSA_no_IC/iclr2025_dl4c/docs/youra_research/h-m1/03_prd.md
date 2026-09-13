# PRD: H-M1 Scale-Accuracy Ordering Experiment

**Hypothesis ID:** H-M1
**Type:** MECHANISM
**Date:** 2026-08-24
**Author:** PrayPrey

---

## 1. Executive Summary

Validate that judge-execution agreement increases with model scale (7B < 70B < proprietary) with diminishing returns. Building on H-E1's validated finding that different scales exhibit distinct FP/FN ratios, H-M1 tests whether this translates to monotonic accuracy improvement.

## 2. Problem Statement

### 2.1 Context
H-E1 confirmed scale-dependent error patterns (Chi-square p=3.27e-08). H-M1 must verify the accuracy ordering holds and exhibits diminishing returns.

### 2.2 Success Criteria (MUST_WORK Gate)
1. **Ordering:** accuracy_7B < accuracy_70B < accuracy_proprietary
2. **Diminishing returns:** (accuracy_70B - accuracy_7B) > (accuracy_proprietary - accuracy_70B)
3. **Statistical significance:** Kruskal-Wallis p < 0.05

### 2.3 Falsification Conditions
- Linear ordering (equal jumps between tiers)
- Reversed ordering at any tier
- Proprietary >20% better than 70B (no diminishing returns)

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR1 | Load HumanEval+ dataset (164 problems) | P0 |
| FR2 | Execute ground truth via EvalPlus | P0 |
| FR3 | Query 7B judge (DeepSeek-Coder-7B) | P0 |
| FR4 | Query 70B judge (CodeLlama-70B) | P0 |
| FR5 | Query proprietary judge (GPT-4-turbo) | P0 |
| FR6 | Compute accuracy per scale | P0 |
| FR7 | Compute Kruskal-Wallis H-test | P0 |
| FR8 | Generate gate metrics figures | P1 |
| FR9 | Support MBPP+ replication | P2 |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR1 | Deterministic inference | temp=0 |
| NFR2 | Full dataset evaluation | 164 problems |
| NFR3 | Results reproducibility | single seed |

## 4. Technical Constraints

### 4.1 Dependencies
- evalplus (PyPI)
- vLLM (7B, 70B inference)
- OpenAI API (GPT-4-turbo)
- scipy.stats, sklearn.metrics

### 4.2 Hardware Requirements
- 7B: ~14GB VRAM
- 70B: ~140GB VRAM or quantized version
- API: Network access

### 4.3 Data Requirements
- HumanEval+: 164 problems
- MBPP+: 378 problems (optional replication)

## 5. Scope

### 5.1 In Scope
- Three-scale judge evaluation
- Accuracy and Kappa metrics
- Statistical testing (Kruskal-Wallis)
- Gate metrics visualization

### 5.2 Out of Scope
- Model fine-tuning
- New judge architectures
- Intermediate scale tiers (13B, 33B)

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| 70B VRAM insufficient | Medium | High | Use quantized model |
| API rate limits | Low | Medium | Batch requests with delays |
| Unexpected ordering | Medium | High | Document as valid falsification |

## 7. Deliverables

1. `run_experiment.py` - Main evaluation script
2. `judge_utils.py` - Judge query utilities
3. `metrics.py` - Accuracy/Kappa computation
4. `figures/` - Gate metrics visualizations
5. `04_validation.md` - Results report

---

*Phase 3 PRD for H-M1 MECHANISM hypothesis*
