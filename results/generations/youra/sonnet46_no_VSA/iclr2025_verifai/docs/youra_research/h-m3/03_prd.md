# Product Requirements Document: H-M3 Adaptive PBT Contribution Experiment

**Hypothesis ID:** H-M3
**Type:** MECHANISM (PoC)
**Date:** 2026-08-03
**Gate:** MUST_WORK
**Base Hypothesis:** H-M1 (VALIDATED — oracle isolation gap = 0.4012)

---

## 1. Overview

H-M3 tests whether Hypothesis PBT with icontract-hypothesis (5k adaptive examples per triple) finds additional contract violations beyond the EvalPlus static oracle (764 fixed inputs per task, Experiment A from H-M1). The experiment computes a paired per-triple adaptive contribution = Exp_B_failure_rate − Exp_A_failure_rate and tests whether mean adaptive contribution > 0 (Wilcoxon p < 0.05).

**Key design principle:** Only the input generation strategy changes between Experiment A (static, 764 EvalPlus inputs) and Experiment B (adaptive, 5k icontract-hypothesis inputs). Contracts, programs, and models are identical. Experiment A results are reused directly from H-M1 — no re-running.

**Continuation context:** H-M1 established oracle-isolation gap = 0.4012 (40% of EvalPlus CVT inputs match gt_plain but fail contract). H-M3 asks: does adaptive PBT guided by pre-conditions explore input regions not covered by those 764 fixed inputs, thereby finding more contract violations?

---

## 2. Objectives

- **Primary:** Mean adaptive contribution (Exp_B − Exp_A failure rate) > 0, Wilcoxon signed-rank p < 0.05 after Holm correction
- **Secondary:** Adaptive contribution > 0.03 absolute for ≥ 50% of tasks
- **Mechanism proof:** Demonstrate pre-condition-guided adaptive search discovers contract violations in input regions not sampled by 764 static EvalPlus inputs

---

## 3. Prerequisites

- H-M1 VALIDATED (MUST_WORK gate satisfied):
  - `h-m1/results/oracle_isolation_results.json` — Experiment A static oracle per-triple results
  - `h-m1/results/per_task_results.csv` — per-task static failure rates
  - `h-m1/code/` — LLM program corpus (5 models × 364 tasks × n=10) already filtered for test-passing
  - Quarantine list: 0 tasks (100% coverage confirmed)
- H-E1 VALIDATED (MUST_WORK gate satisfied)
- ContractEval repository cloned (icontract-decorated reference implementations)
- icontract-hypothesis v1.1.7 installed

---

## 4. Functional Requirements

### FR-1: Data Loading (Reuse from H-M1)

- Load H-M1 Experiment A results from `h-m1/results/oracle_isolation_results.json`
  - Format per entry: `{task_id, model, program_idx, static_failure_rate, failed_inputs: [...]}`
- Load LLM program corpus from `h-m1/code/` (test-passing programs already filtered)
- Load ContractEval task functions with icontract `@require`/`@ensure` decorators
- Verify 364 tasks available (quarantine list empty from H-M1)
- Load EvalPlus task metadata: `from evalplus.data import get_human_eval_plus, get_mbpp_plus`
- Expected triples: 364 tasks × 5 models × ≤10 programs = up to 18,200 (model, task, program)

### FR-2: Compatibility Pre-check

- Run pre-experiment check on 20 representative tasks to calibrate icontract-hypothesis filter rates
- Flag tasks where filter_rate > 0.95 as high-filter candidates
- Log pre-check results before full Experiment B run
- Proceed with full run if ≥ 15/20 tasks yield ≥ 100 valid examples

### FR-3: Experiment B — Adaptive PBT Oracle (Core)

For each (model, task, program) triple:
- Wrap LLM program with ContractEval icontract `@require`/`@ensure` decorators
- Run `icontract_hypothesis.test_with_inferred_strategy` with:
  - `max_examples=5000`
  - `seed=42`
  - `deadline=None`
  - `suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much]`
  - Wall-clock timeout: 60 seconds per triple
- Track per triple:
  - `adaptive_failure_rate` = violations / valid_examples
  - `n_valid` = count of examples not rejected by pre-condition filter
  - `n_failures` = post-condition violations detected
  - `filter_rate` = 1.0 − (n_valid / 5000)
- Flag triple as low-yield if `n_valid < 100` OR `filter_rate > 0.95`
- Parallelism: `multiprocessing.Pool` with 16–32 workers (embarrassingly parallel by task × model)
- Seed: fixed 42 (single run, reproducible)

### FR-4: Yield Check and Quarantine

- After Experiment B, compute per-task yield statistics
- Flag tasks with `filter_rate > 0.95` OR `mean(n_valid) < 100` across programs
- Report as "low-yield tasks" in results (do NOT quarantine from analysis unless filter_rate = 1.0)
- Tasks with `n_valid = 0` for ALL programs: exclude from paired comparison, report count

### FR-5: Adaptive Contribution Computation

- Per triple: `adaptive_gap = adaptive_failure_rate − static_failure_rate`
- Join on (task_id, model, program_idx) between Exp B results and H-M1 Exp A results
- Aggregate:
  - Mean adaptive contribution across all paired triples
  - Per-model mean adaptive contribution (5 models)
  - Per-task-type mean (HumanEval+ vs MBPP+)
  - Fraction of tasks where mean(adaptive_gap) > 0.03

### FR-6: Statistical Analysis

- **Primary test:** Wilcoxon signed-rank (Exp_B_rates, Exp_A_rates, alternative="greater")
  - Null: adaptive_contribution = 0
  - Significance: p < 0.05 after Holm correction for per-model sub-analyses
- **Bootstrap 95% CI:** n=10,000 resamples on mean adaptive contribution (seed=42)
- **Per-model sub-analyses:** Wilcoxon per model (5 tests) with Holm correction
- **Sanity check:** Wilcoxon two-sided p < 0.5 to verify measurable difference exists
- Report: stat, p_raw, p_holm_corrected, mean_gap, CI_lower, CI_upper

### FR-7: Mechanism Activation Verification

Verify Experiment B ran and produced meaningful output:
- `yield_sufficient`: ≥ 80% of triples with n_valid ≥ 100
- `filter_not_total`: no triple with filter_rate = 1.0 (all rejected)
- `adaptive_gap_measurable`: adaptive rates differ from static rates for ≥ 1 triple
- `triples_covered`: ≥ 10,000 valid triples evaluated (out of ~18,200 expected)
- Gate: ≥ 3/4 indicators must pass

Failure modes to detect:
- `StrategyInferenceError` for > 20% of tasks → FAIL
- `n_valid = 0` for > 20% of tasks → FAIL
- All adaptive rates match static rates exactly → FAIL (configuration error)

### FR-8: Visualization

- **Required (gate metrics):** Bar chart — mean adaptive contribution vs. 0 threshold; with 95% CI error bars
- **Additional:**
  1. Scatterplot: Exp_A_rate vs Exp_B_rate per task (points above diagonal = adaptive finds more)
  2. Histogram: per-task adaptive gap distribution (Exp_B − Exp_A), with 0-line
  3. Histogram: per-task filter rate distribution; flag high-filter tasks
  4. Bar chart: model-stratified adaptive contribution (5 model families)
  5. Bar chart: task-type breakdown (HumanEval+ vs MBPP+ adaptive contribution)
- Save all figures to `h-m3/figures/`

### FR-9: Results Output

- JSON results: `h-m3/results/experiment_b_results.jsonl` (one entry per triple)
- CSV per-task: `h-m3/results/per_task_adaptive_contribution.csv`
- Low-yield report: `h-m3/results/low_yield_tasks.csv`
- Summary report: `h-m3/results/summary_report.md`

---

## 5. Non-Functional Requirements

- **Reproducibility:** seed=42 throughout; fixed icontract-hypothesis v1.1.7; deterministic outputs
- **Scale:** Full 364 ContractEval tasks; 5k adaptive examples per triple; ~18,200 triples
- **Performance:** CPU-only multiprocessing (16–32 workers); estimated wall-clock 50–100h single-core → 2–4h parallelized
- **Reuse:** Experiment A results loaded from H-M1 — no re-computation of static oracle
- **Isolation:** No GPU required; no new LLM API calls

---

## 6. Directory Structure

```
h-m3/
├── code/
│   ├── data_loader.py                   # Load H-M1 Exp A results + LLM programs + ContractEval
│   ├── compatibility_check.py           # Pre-experiment 20-task filter rate calibration (FR-2)
│   ├── experiment_b_runner.py           # Core adaptive PBT runner (FR-3)
│   ├── yield_checker.py                 # Per-task yield analysis and quarantine (FR-4)
│   ├── adaptive_contribution.py         # Exp_B vs Exp_A paired comparison (FR-5)
│   ├── statistical_analysis.py          # Wilcoxon + bootstrap + Holm (FR-6)
│   ├── mechanism_verifier.py            # Activation indicators (FR-7)
│   ├── visualization.py                 # Figure generation (FR-8)
│   └── run_experiment.py                # Main entry point
├── results/
│   ├── experiment_b_results.jsonl
│   ├── per_task_adaptive_contribution.csv
│   ├── low_yield_tasks.csv
│   └── summary_report.md
└── figures/
    ├── gate_metrics_adaptive_contribution.png
    ├── scatter_exp_a_vs_exp_b.png
    ├── adaptive_gap_distribution.png
    ├── filter_rate_distribution.png
    ├── model_stratified_contribution.png
    └── task_type_breakdown.png
```

---

## 7. Dependencies

### Python Packages

```
icontract-hypothesis==1.1.7
icontract>=2.6.0
hypothesis>=6.100.0
evalplus==0.3.1
scipy>=1.11.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
```

### External Repositories

- `suhanmen/ContractEval` (git clone): icontract-decorated task functions
- H-M1 outputs (local): `h-m1/results/oracle_isolation_results.json`, `h-m1/code/`

---

## 8. Success Criteria

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Mean adaptive contribution | > 0 | Phase 2B |
| Wilcoxon p-value (Holm corrected) | < 0.05 | Phase 2B |
| Adaptive contribution > 0.03 | ≥ 50% of tasks | Phase 2B (secondary) |
| Mechanism activated | ≥ 80% triples with n_valid ≥ 100 | FR-7 |
| Triples covered | ≥ 10,000 | FR-7 |

---

## 9. Failure Response

Gate type: MUST_WORK. Failure (mean contribution ≈ 0 or p > 0.05) triggers PIVOT to oracle-strength interpretation: "contract semantics alone drive the gap; adaptive search adds nothing." This is a publishable finding via H-M1 (oracle isolation gap = 0.4012 remains valid). Pipeline continues via H-M1 contribution.

---

## 10. Risks

| Risk | Mitigation |
|------|------------|
| High filter rate (> 0.95) for many tasks | Compatibility pre-check on 20 tasks before full run; FilteredStrategy fallback |
| StrategyInferenceError for > 20% tasks | Use `FilteredStrategy` explicit fallback; report percentage |
| Wall-clock > 4h even parallelized | Reduce budget from 5k to 1k for remaining tasks; report as limitation |
| Adaptive rates identical to static rates | Fail-fast with mechanism verifier; verify ContractEval loading |
| H-M1 results file missing | Validate existence before Exp B starts; STOP if missing |

---

*Phase 2C source: h-m3/02c_experiment_brief.md*
*Base hypothesis: H-M1 (oracle isolation gap = 0.4012)*
*Generated: 2026-08-03*
