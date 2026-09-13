# Product Requirements Document: H-M1 Oracle Isolation Experiment

**Hypothesis ID:** H-M1
**Type:** MECHANISM (PoC)
**Date:** 2026-08-03
**Gate:** MUST_WORK

---

## 1. Overview

H-M1 tests whether ContractEval's contract oracle is semantically richer than EvalPlus's differential equality oracle when both are applied to identical static test inputs. The experiment measures the oracle-isolation gap (contract-failure rate minus differential-failure rate) and contract-unique mass (fraction where program output equals ground truth but contract fails). Hypothesis confirms if gap ≥ 0.10 absolute with contract-unique mass ≥ 0.05.

**Key insight:** Same 764 EvalPlus static inputs evaluated under two oracles simultaneously — only the oracle changes, not the inputs. This isolates oracle strength from input generation strategy.

---

## 2. Objectives

- **Primary:** Measure oracle-isolation gap ≥ 0.10 (Wilcoxon p < 0.01 after Holm correction)
- **Secondary:** Measure contract-unique mass ≥ 0.05 (bootstrap 95% CI lower bound > 0.03)
- **Mechanism proof:** Demonstrate that contracts catch failures missed by differential equality testing

---

## 3. Prerequisites

- H-E1 VALIDATED (done): test-passing LLM programs exist at `h-e1/code/` per (model, task)
- ContractEval repository cloned (icontract-annotated reference implementations)
- EvalPlus package installed (provides 764 static inputs per task)

---

## 4. Functional Requirements

### FR-1: Data Loading
- Load ContractEval 364 tasks with icontract pre/post-condition decorators
- Load EvalPlus static inputs per task: `base_input` + `plus_input` = 764 total
- Verify task ID overlap ≥ 90%; generate fresh Hypothesis inputs for unmatched tasks
- Load H-E1 test-passing programs from `h-e1/code/` output directory

### FR-2: Oracle Soundness Pre-check
- Run Hypothesis PBT (100k examples, seed=42) on all ContractEval reference implementations
- Quarantine tasks where reference implementation fails ≥ 1 contract
- Expected quarantine rate < 5% (327+ tasks remaining evaluable)
- Report quarantine list to stdout and results file

### FR-3: Oracle Isolation Evaluation (Core)
- For each (model, task, program) triple, evaluate all 764 EvalPlus static inputs under:
  - **Oracle A (differential):** `f(x) == gt(x)` equality check
  - **Oracle B (contract):** assert pre(x) satisfied AND post(f(x)) holds via icontract
- Classify each (program, input) pair:
  - `redundant`: both oracles detect failure
  - `contract_unique`: `f(x)==gt(x)` AND post fails
  - `differential_only`: `f(x)!=gt(x)` AND post holds
  - `neither`: both pass
- Execution timeout: 5 seconds per input
- Parallelism: multiprocessing (CPU-only)
- Seed: 42

### FR-4: Aggregation
- Per-task oracle-isolation gap = contract_failure_rate − differential_failure_rate
- Per-task contract-unique mass = contract_unique_count / total_inputs
- Aggregate across tasks: mean ± std for gap and contract-unique mass
- Stratify by: model family (5 models), task type (HumanEval+ vs MBPP+)

### FR-5: Statistical Analysis
- Wilcoxon signed-rank test on per-task gaps vs. H0: gap = 0 (alternative: greater), with Holm correction
- Bootstrap 95% CI (n=10000 resamples, seed=42) on mean gap and contract-unique mass
- Report: stat, p-value raw, p-value corrected, CI lower, CI upper

### FR-6: Mechanism Activation Verification
- Verify both oracles actually executed: mean_diff_failure_rate > 0 AND mean_contract_failure_rate > 0
- Verify ≥ 300/364 tasks evaluated
- Verify contract_unique_count > 0 for ≥ 50% of evaluated tasks
- Fail fast if oracle A or B is silent (misconfiguration)

### FR-7: Visualization
- **Required:** Bar chart — mean oracle-isolation gap vs. 0.10 threshold; contract-unique mass vs. 0.05 threshold; with 95% CI error bars
- **Optional:** Stacked bar per model (redundant / contract-unique / differential-only / neither)
- **Optional:** Violin/CDF of per-task oracle-isolation gap distribution
- **Optional:** Scatter: per-task differential failure rate vs. contract failure rate
- Save to `h-m1/figures/`

### FR-8: Results Output
- JSON results file: `h-m1/results/oracle_isolation_results.json`
- CSV per-task breakdown: `h-m1/results/per_task_results.csv`
- Summary report: `h-m1/results/summary_report.md`

---

## 5. Non-Functional Requirements

- **Reproducibility:** seed=42 throughout; all outputs deterministic
- **Scale:** Full 364 ContractEval tasks, 764 inputs/task, ≥ 1 test-passing program per task per model
- **Performance:** CPU-only multiprocessing; expected wall-clock < 4 hours on 8-core machine
- **Isolation:** No GPU required; no new LLM API calls (programs reused from H-E1)

---

## 6. Directory Structure

```
h-m1/
├── code/
│   ├── data_loader.py           # ContractEval + EvalPlus + H-E1 corpus loading
│   ├── oracle_isolation.py      # Core oracle evaluation harness (FR-3)
│   ├── soundness_check.py       # Oracle soundness pre-check (FR-2)
│   ├── statistical_analysis.py  # Wilcoxon + bootstrap (FR-5)
│   ├── visualization.py         # Figure generation (FR-7)
│   └── run_experiment.py        # Main entry point (orchestrates FR-1 to FR-8)
├── results/
│   ├── oracle_isolation_results.json
│   ├── per_task_results.csv
│   └── summary_report.md
└── figures/
    ├── gate_metrics_comparison.png
    ├── oracle_failure_breakdown.png
    ├── gap_distribution.png
    └── scatter_failure_rates.png
```

---

## 7. Success Criteria

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Oracle-isolation gap | ≥ 0.10 | Phase 2B |
| Wilcoxon p-value | < 0.01 (Holm corrected) | Phase 2B |
| Contract-unique mass | ≥ 0.05 (CI lower > 0.03) | Phase 2B |
| Task coverage | ≥ 90% (≥ 327/364 evaluable) | Phase 2B |

---

## 8. Failure Response

Gate type: MUST_WORK. Failure (gap ≤ 0.02 or p > 0.05) triggers PIVOT to oracle-strength-only interpretation via richness stratification. Pipeline continues.

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| EvalPlus task ID overlap < 90% | Fallback: generate inputs via Hypothesis with icontract preconditions |
| Reference implementations fail contracts (quarantine > 5%) | Report rate; proceed with remaining tasks if ≥ 300 evaluable |
| Oracle B silent (no contract violations) | Fail fast with diagnostic; verify icontract decorators loading correctly |
| Oracle A silent (no differential failures) | Fail fast; check EvalPlus sandbox execution |

---

*Phase 2C source: h-m1/02c_experiment_brief.md*
*Generated: 2026-08-03*
