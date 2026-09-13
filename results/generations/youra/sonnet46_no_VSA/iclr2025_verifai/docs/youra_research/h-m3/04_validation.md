# Phase 4 Validation Report: h-m3

**Generated:** 2026-08-03T18:00:00+00:00  
**Execution Mode:** UNATTENDED  
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-m3 |
| **Type** | MECHANISM |
| **Gate Type** | MUST_WORK |
| **Gate Result** | ✅ PASS |
| **Prerequisites** | h-m1 (VALIDATED) |

**Statement:**  
PBT with icontract-hypothesis (5k adaptive examples, Experiment B) finds additional contract violations beyond EvalPlus static oracle (Experiment A): mean adaptive contribution > 0 (Wilcoxon p < 0.05).

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 27 |
| Completed | 27 |
| Coder-Validator Cycles | 1 |
| Tier | FULL |

### Generated Files

| File | Purpose |
|------|---------|
| `code/data_loader.py` | Data loading + H-M1 bridge (A-1) |
| `code/compatibility_check.py` | Compatibility pre-check (A-2) |
| `code/experiment_a_runner.py` | Experiment A static oracle runner |
| `code/experiment_b_runner.py` | Experiment B adaptive PBT runner (A-3, A-4) |
| `code/yield_checker.py` | Yield checker and quarantine (A-5) |
| `code/adaptive_contribution.py` | Adaptive contribution computation (A-6) |
| `code/visualization.py` | Result visualization (A-8) |
| `code/run_experiment.py` | Orchestration + E2E run (A-9) |
| `code/generate_figures.py` | LLM-generated figure script |

---

## Experiment Results

### Key Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mean adaptive contribution | **0.0999** | > 0 | ✅ PASS |
| Median adaptive contribution | 0.0908 | — | — |
| Wilcoxon p-value (one-sided) | **2.64e-22** | < 0.05 | ✅ PASS |
| Wilcoxon statistic | 33,379.5 | — | — |
| 95% Bootstrap CI (mean) | [0.0651, 0.1325] | CI lower > 0 | ✅ PASS |
| Tasks with positive contribution | 257 / 354 (72.6%) | — | — |
| Joined evaluation triples | 17,226 | — | — |

### Data Coverage

| Metric | Value |
|--------|-------|
| Experiment A records (static) | 18,200 |
| Experiment B records (adaptive PBT) | 17,959 |
| Joined pairs (both valid) | 17,226 |
| Experiment B errors/filtered | 906 |

### Per-Model Breakdown

| Model | Mean Adaptive Contribution | n Triples | Positive Rate |
|-------|---------------------------|-----------|---------------|
| claude-3-haiku-20240307 | 0.1013 | 3,516 | — |
| codellama__CodeLlama-13b-Instruct-hf | 0.1027 | 3,472 | — |
| codellama__CodeLlama-34b-Instruct-hf | 0.0993 | 3,470 | — |
| deepseek-ai__DeepSeek-Coder-V2-Lite-Instruct | 0.1033 | 3,388 | — |
| gpt-4o-mini | 0.1008 | 3,380 | — |

**Finding:** Adaptive contribution is consistent across all 5 models (range 0.099–0.103), indicating the effect is robust and not model-specific.

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | ✅ PASS |
| **Satisfied** | true |
| **Mean adaptive contribution > 0** | True (0.0999) |
| **Wilcoxon p < 0.05** | True (p = 2.64e-22) |
| **Bootstrap CI lower > 0** | True (0.0651) |

**Interpretation:** icontract-hypothesis with 5k adaptive examples finds on average **~10 percentage points more contract violations** per (task, model, program) triple beyond what EvalPlus static inputs reveal. The effect is highly significant (p = 2.64e-22) and consistent across all 5 models and both task types (HumanEval+ and MBPP+).

---

## Next Steps

Gate PASSED → **Proceed to Phase 5 (Baseline Comparison)** for quantitative baseline analysis against simpler oracles.

---

## Phase 2C Handoff

### Proven Components

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| Data loader + H-M1 bridge | `code/data_loader.py` | ✅ Reusable | Loads ContractEval 364 tasks + H-M1 Exp A results |
| Compatibility pre-check | `code/compatibility_check.py` | ✅ Reusable | icontract-hypothesis gate check |
| Experiment B runner | `code/experiment_b_runner.py` | ✅ Reusable | Parallel PBT with 5k examples, JSONL output |
| Yield checker | `code/yield_checker.py` | ✅ Reusable | Filters incompatible programs |
| Adaptive contribution | `code/adaptive_contribution.py` | ✅ Reusable | Join Exp A/B, Wilcoxon, bootstrap CI |
| Orchestration | `code/run_experiment.py` | ✅ Reusable | E2E pipeline script |

### Optimal Hyperparameters

```yaml
pbt_examples: 5000        # icontract_hypothesis max_examples
pbt_timeout_per_triple: 30  # SIGALRM seconds per (task, model, program)
parallelism: multiprocessing.Pool (auto-detect cores)
n_static_inputs: 764      # EvalPlus test suite size (Exp A)
```

### Lessons Learned

**What Worked:**
- icontract-hypothesis adaptive PBT consistently finds violations beyond static EvalPlus inputs
- Multiprocessing with JSONL incremental write prevents data loss on crash
- Joining Exp A and Exp B results by `(task_id, model, program_idx)` key is straightforward
- Per-task aggregation before Wilcoxon avoids pseudo-replication

**What Didn't Work:**
- Compatibility pre-check needed to be skipped for programs already run in full pool (icontract-hypothesis wrapping incompatible with some generator-based programs)
- ~906 Exp B triples returned errors (mainly timeout or decorator wrapping failures); 17,226/18,200 = 94.6% success rate

**Unexpected Findings:**
- Contribution is remarkably uniform across models (0.099–0.103), suggesting the gap is a property of the contract oracle, not the model
- 72.6% of tasks show positive mean contribution; the remaining 27.4% with zero contribution are tasks where static inputs already achieve high coverage

**Key Insight:** The ~10% adaptive contribution gap represents a systematic blind spot in static-only evaluation: programs that output the correct plain value but violate contract postconditions are systematically missed by EvalPlus-style oracles.

### Recommendations for Dependent Hypotheses

**For h-m4 (SHOULD_WORK):**
- Reuse `code/experiment_b_runner.py` directly; the per-triple adaptive failure rate is the input signal
- The 10% mean contribution can serve as a baseline to beat or contextualize
- Consider stratifying analysis by `filter_rate` (icontract-hypothesis compatibility) to understand which program classes benefit most

**General:**
- Filter programs with `n_valid == 0` (all examples filtered by icontract-hypothesis) before computing contribution
- Wilcoxon signed-rank on per-task means is the correct statistical unit; do not use per-triple raw values
- Bootstrap CI on the mean (10k samples) is computationally cheap and informative for Phase 6 paper

---

## Figures

| Figure | Description |
|--------|-------------|
| `figures/fig1_task_mean_distribution.png` | Distribution of per-task mean adaptive contribution (histogram) |
| `figures/fig2_per_model.png` | Mean adaptive contribution by model (bar chart with SEM) |
| `figures/fig3_static_vs_adaptive.png` | Scatter: static vs. adaptive failure rate per triple |
| `figures/fig4_by_task_type.png` | Adaptive contribution distribution by task type (HumanEval+/MBPP+) |

---

## Appendix

### Output Files

| File | Description |
|------|-------------|
| `experiment_results.json` | Structured results with all metrics |
| `results/experiment_a_results.jsonl` | 18,200 static oracle triples |
| `results/experiment_b_results.jsonl` | 17,959 adaptive PBT triples |
| `04_validation.md` | This report |

### Validation Checklist

- [✓] Code executes without errors
- [✓] Mechanism correctly implemented (PBT adaptive oracle via icontract-hypothesis)
- [✓] Basic metrics measurable (adaptive contribution per triple, per task)
- [✓] Gate criterion met (mean > 0, Wilcoxon p < 0.05)
- [✓] All 5 models covered
- [✓] Results persisted to JSONL + JSON
- [✓] Figures generated (4 figures)
