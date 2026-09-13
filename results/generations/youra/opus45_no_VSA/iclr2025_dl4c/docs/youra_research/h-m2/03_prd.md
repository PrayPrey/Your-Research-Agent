# PRD: H-M2 DiD Semantic Sensitivity Experiment

**Date:** 2026-08-08
**Hypothesis:** DiD contrast [(A-C)_RL - (A-C)_CE] > 0 for semantic feedback sensitivity
**Gate:** SHOULD_WORK
**Dependency:** H-E1 (validated checkpoints)

---

## 1. Objective

Verify whether RL-trained models extract more semantic signal from execution feedback than CE-trained models via Difference-in-Differences analysis.

## 2. Scope

### In Scope
- Load H-E1 checkpoints (RL, CE models)
- Evaluate on HumanEval+ (164 problems)
- Implement feedback perturbation (Actual vs Control)
- Compute DiD contrast with bootstrap CI
- Generate required visualizations

### Out of Scope
- Additional training (evaluation only)
- MBPP+ evaluation (HumanEval+ sufficient for mechanism test)
- Multi-iteration refinement (K=1 isolates feedback effect)

## 3. Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| F1 | Load RL/CE checkpoints from H-E1 | P0 |
| F2 | Single-shot generation on HumanEval+ | P0 |
| F3 | Execute code, capture error feedback | P0 |
| F4 | Generate control feedback (wrong-problem shuffle) | P0 |
| F5 | Refinement with feedback injection | P0 |
| F6 | Compute pass@1 per condition (4 cells) | P0 |
| F7 | Bootstrap DiD contrast with 95% CI | P0 |
| F8 | 2×2 grouped bar chart | P0 |
| F9 | DiD contrast bar with CI | P0 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NF1 | Reproducibility | Fixed seeds (42, 43, 44) |
| NF2 | Evaluation time | < 4 hours total |
| NF3 | Memory | < 24GB GPU |

## 4. Data Flow

```
H-E1 Checkpoints → Load Models → Single-shot Eval → 
    ↓ (failed problems)
Execute & Get Feedback → 
    ├── Actual: Real error message
    └── Control: Wrong-problem feedback
         ↓
Refinement Generation → Execution → Pass/Fail → 
    ↓
Aggregate → DiD Contrast → Bootstrap CI → 
    ↓
Visualizations + Results
```

## 5. Success Criteria

- **Code Execution:** All 4 conditions complete without error
- **Primary Metric:** DiD > 0 (point estimate)
- **Statistical:** 95% CI lower bound > 0 preferred, p < 0.10 acceptable for SHOULD_WORK

## 6. Deliverables

1. `did_evaluator.py` - Main evaluation script
2. `feedback_perturbation.py` - Control feedback generation
3. `bootstrap_analysis.py` - Statistical analysis
4. `results.json` / `results.csv` - Raw results
5. `figures/did_bar_chart.png` - 2×2 grouped bars
6. `figures/did_contrast_ci.png` - DiD with confidence interval
7. `04_validation.md` - Validation report

## 7. Timeline Estimate

| Phase | Duration |
|-------|----------|
| Setup | 0.5h |
| Implementation | 2h |
| Evaluation | 2h |
| Analysis | 0.5h |
| **Total** | **5h** |

---

*Source: 02c_experiment_brief.md*
