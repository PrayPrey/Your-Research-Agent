# Tasks: H-E1 (EXISTENCE / PoC)

**Hypothesis**: PELT change-point detection identifies statistically significant change point in aggregate Gini coefficient time series within 2019-2022 window at α=0.05

**Tier**: LIGHT (EXISTENCE type)
**Budget**: Max 15 tasks
**Actual**: 8 tasks

---

## Task List

| ID | Task | Description | Complexity | File(s) |
|----|------|-------------|------------|---------|
| A-1 | Setup config | config.py constants, folder structure | 4 | config.py |
| A-2 | Data loading | HF dataset load, triplet parsing, date filter | 10 | data.py |
| A-3 | Gini aggregation | monthly counts + Gini coefficient series | 9 | data.py |
| A-4 | Baseline model | MonotonicTrendModel (scipy linregress + BIC) | 6 | model.py |
| A-5 | Proposed model | GiniChangePointDetector (PELT rbf + segmented trends) | 12 | model.py |
| A-6 | Evaluation/gates | BIC comparison, target-window check, gate PASS/FAIL | 8 | evaluate.py |
| A-7 | Visualization | 3 required figures | 7 | visualize.py |
| A-8 | Orchestration | train.py wiring all modules, results.json output | 6 | train.py |

---

## Complexity Distribution

- **VeryHigh (18-20)**: None
- **High (14-17)**: None
- **Medium (9-13)**: A-2, A-3, A-5
- **Low (4-8)**: A-1, A-4, A-6, A-7, A-8

---

## Dependencies

```
A-1 (config) → A-2 (data loading) → A-3 (gini) → A-4, A-5 (models)
                                              ↘ A-6 (evaluate) → A-7 (viz) → A-8 (orchestrate)
```

---

## Gate Criteria

| Gate | Criterion | Threshold |
|------|-----------|-----------|
| G-1 | Change point in target window | 2019-2022 |
| G-2 | Statistical significance | α=0.05 |
| G-3 | BIC improvement | Segmented < Monotonic |

---

## Execution Order

1. A-1: Setup config
2. A-2: Data loading
3. A-3: Gini aggregation
4. A-4: Baseline model
5. A-5: Proposed model
6. A-6: Evaluation/gates
7. A-7: Visualization
8. A-8: Orchestration

**Total Complexity Score**: 62 (within LIGHT tier budget)
