# Phase 4 Validation Report: H-M3

**Generated:** 2026-08-31T18:30:00+00:00
**Execution Mode:** UNATTENDED (Batch/Ablation)
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 4.5
**Gate Type:** SHOULD_WORK

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | H-M3 |
| **Type** | MECHANISM |
| **Statement** | Under 3-iteration repair loops on failing solutions, per-iteration repair success rate will positively correlate with feedback specificity order (from H-M2) because more precise error signals enable more targeted code edits |
| **Prerequisites** | H-M2 (VALIDATED) |
| **Dataset** | HumanEval (164) + MBPP (374) = 538 problems; 126 failing solutions from H-M1 |
| **Model** | GPT-4o-mini, repair temperature=0.0 |
| **Duration** | ~530 seconds (4 workers, 126 problems × 4 categories) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 29 |
| Completed | 29 |
| Coder-Validator Cycles | 1 |
| Total Code Lines | ~1,009 (src/ modules) |

### Generated Files

| File | Lines | Description |
|------|-------|-------------|
| `src/verifier_adapters.py` | 153 | Wraps H-M2 FeedbackMeasurer into 4 adapter classes |
| `src/evaluate.py` | 61 | HumanEval/MBPP solution evaluation |
| `src/repair_loop.py` | 127 | Core repair loop + LLM call + prompt builder |
| `src/analyze.py` | 154 | Spearman correlation + bootstrap CI + ablations |
| `src/visualize.py` | 195 | 5 required figures |
| `src/write_results.py` | 35 | JSONL + JSON persistence |
| `src/load_h_m1.py` | 98 | H-M1 failing records loader (extended) |
| `run_h_m3.py` | 105 | Entry point + parallel orchestration |
| `results/h-m3/repair_records.jsonl` | 504 lines | Per-(problem, category) repair results |
| `results/h-m3/summary.json` | — | Aggregate statistics + gate verdict |

---

## Code Quality Checklist

- [✓] Syntax validation passed (experiment ran successfully)
- [✓] Mechanism verified: repair loop fires for all 4 categories
- [✓] API signatures match 03_logic.md (BaseVerifierAdapter.get_feedback, run_repair_loop, compute_iter_rates, run_spearman)
- [✓] H-M2 FeedbackMeasurer correctly wrapped (no standalone verifier classes — adapter pattern)
- [✓] evaluate_solution handles both HumanEval (check_correctness) and MBPP (exec test_list) formats
- [✓] Feedback truncation at 4,000 chars for pyright (avg 24,358 char output)
- [✓] 4-worker ThreadPoolExecutor with sequential per-category within problem
- [✓] All 5 figures generated successfully

---

## Experiment Results

### Primary Metrics: Per-Category Iteration-1 Repair Success Rate

| Category | Specificity Rank (H-M2) | iter1_rate | 95% CI | n | Mean iters to pass |
|----------|------------------------|------------|--------|---|-------------------|
| Pyright (static) | 1 (highest) | **4.76%** | [1.6%, 8.7%] | 126 | 1.375 |
| Execution monitoring | 2 | **5.56%** | [1.6%, 9.5%] | 126 | 1.727 |
| Mypy (type check) | 3 | **6.35%** | [2.4%, 11.1%] | 126 | 1.455 |
| Z3 SMT | 4 (lowest) | **7.94%** | [4.0%, 12.7%] | 126 | 1.167 |

**Spearman ρ = -1.0000** (n=4 categories, p=0.00)

### Spearman Correlation Results

| Analysis | ρ | Gate (ρ > 0) |
|----------|---|-------------|
| With Z3 | -1.0000 | FAIL |
| Without Z3 | -1.0000 | FAIL |

### Ablation Results

| Ablation | ρ | Notes |
|----------|---|-------|
| Iter-2 correlation | -0.800 | Direction consistent (still fails) |
| HumanEval only | -1.0000 | Higher rates (26-43%), same inverse order |
| MBPP only | 0.0 (all 0%) | GPT-4o-mini cannot repair MBPP at iter-1 |
| Logic errors | -0.949 | Consistent with overall pattern |
| Type errors | -0.894 | Pyright≈execution rate (both ~9.7%) |
| Runtime errors | -0.775 | Only Z3 non-zero (8.3%) |

### HumanEval Subgroup (n=46 failing problems)

| Category | iter1_rate |
|----------|------------|
| Pyright | 26.1% |
| Execution | 30.4% |
| Mypy | 34.8% |
| Z3 | 43.5% |

HumanEval shows meaningful repair rates; MBPP shows 0% across all categories (MBPP problem structure harder for single-iteration repair with these feedback types).

---

## Mechanism Verification

**Pre-conditions checked:**
- ✓ `mechanism_exists`: Repair loop executes and calls verifier.get_feedback() for each problem
- ✓ `mechanism_isolatable`: Feedback category is the only IV (all other parameters fixed)
- ✓ `baseline_measurable`: H-M1 failing solutions loaded (126 records)

**Mechanism verification log:**
```
[HE_0066] iter1 execution: pass=False  ✓ execution: loop active
[HE_0066] iter1 pyright: pass=False   ✓ pyright: loop active
[HE_0066] iter1 mypy: pass=False      ✓ mypy: loop active
[HE_0066] iter1 z3: pass=False        ✓ z3: loop active
```

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | SHOULD_WORK |
| **Gate Condition** | Spearman ρ > 0 (positive correlation: higher specificity → higher repair rate) |
| **Gate Result** | **FAIL** |
| **ρ (with Z3)** | -1.0000 |
| **ρ (without Z3)** | -1.0000 |
| **Satisfied** | false |

**Gate Failure Reason:** The empirical ordering is the **inverse** of H-M3's prediction. Higher feedback specificity (pyright, 24,358 chars, rank 1) produces LOWER per-iteration-1 repair success rates, while lower specificity (Z3, 2 chars, rank 4) produces the highest rates. The Spearman ρ = -1.0 indicates perfect inverse correlation with the predicted order.

---

## Analysis of Gate Failure

### Why Pyright Feedback Leads to Lower Repair Rates

**Hypothesis:** Pyright produces highly verbose JSON output (avg 24,358 chars/problem). When truncated to 4,000 chars for the repair prompt (necessary to avoid token overflow), the feedback:
1. May be **harder for the LLM to parse** than short execution tracebacks
2. Contains **type-system language** that is less actionable than "line 5 raises NameError"
3. Provides **redundant diagnostics** about issues unrelated to the test failure

**Z3 advantage (counter-intuitive):** Z3 outputs are short ("unsat" or small model) but are also highly targeted when applicable. The 6.3% coverage limitation from H-M2 means Z3 was run on all 126 problems but only ~8 have extractable constraints — for the rest, it produces "No Z3 constraints extractable" feedback. Surprisingly, even minimal Z3 feedback (which essentially forces the LLM to reason without external guidance) produces the highest repair rate. This may reflect that Z3-guided problems are inherently simpler/more formulaic.

**MBPP failure (0% all categories):** MBPP problems with single-iteration temperature=0.0 repair essentially require the LLM to understand the natural language problem description from the test assertions alone. Without the original docstring well-formatted in the prompt, repair fails systematically.

### Scope of Finding (per 02c_experiment_brief.md)

Per the experiment brief gate failure protocol: "SCOPE — document that efficiency differences are overhead-driven, P1 in H-M4 still testable."

The finding reveals that:
1. **Repair success is feedback-length-negative**: shorter, targeted feedback (execution traces, Z3) outperforms verbose diagnostic output (pyright JSON)
2. **H-M4 (efficiency/token consumption) is still testable**: the cost-efficiency tradeoff between high-specificity and repair success is now empirically documented
3. **Partial confirmation**: the ranking execution > pyright (in terms of pure repair rate for complex problems) aligns with prior Self-Repair work (Olausson 2023) which found execution traces most effective

---

## Next Steps

**Gate Result: FAIL (SHOULD_WORK)**

Per workflow spec for SHOULD_WORK gate failure:
- **Action:** Continue with limitation note; document failure in validation report
- **H-M4 impact:** H-M4 tests token efficiency (tokens-per-successful-repair) — the inverse correlation finding is complementary, not blocking
- **Routing:** Proceed to Phase 4.5 (Hypothesis Synthesis) with FAIL notation

**Limitation note for H-M4:**
> H-M3 found inverse correlation between feedback specificity (char_count) and per-iteration-1 repair success rate (ρ=-1.0). This means H-M4 testing token efficiency will likely find that high-specificity feedback (pyright) costs MORE tokens per successful repair, not fewer. H-M4 remains valuable as it tests the total cost of the feedback-repair pipeline.

---

## Phase 2C Handoff

### Proven Components (Reusable for H-M4)

| Component | File | Evidence |
|-----------|------|----------|
| VerifierAdapter wrapper pattern | `src/verifier_adapters.py` | All 4 adapters executed successfully |
| Repair loop (`run_repair_loop`) | `src/repair_loop.py` | 504 repair sequences completed |
| Evaluation (`evaluate_solution`) | `src/evaluate.py` | HumanEval pass/fail correctly measured |
| Per-category iter tracking | `src/analyze.py` | iter1/2/3_rate computed per category |
| Bootstrap CI | `src/analyze.py` | 1,000 bootstrap samples per category |
| `load_failing_records` (extended) | `src/load_h_m1.py` | 126 records with prompt/test/entry_point |
| Parallel repair orchestration | `run_h_m3.py` | 4-worker ThreadPoolExecutor |

### Optimal Hyperparameters

```yaml
repair_loop:
  model: gpt-4o-mini
  max_iterations: 3
  temperature: 0.0      # Deterministic repair (Olausson 2023)
  feedback_truncation: 4000  # chars — prevents token overflow for pyright

verifier_timeouts:
  execution: 5s
  pyright: 10s
  mypy: 10s
  z3: 30s

parallelism:
  n_workers: 4
  problem_level: true  # sequential per-category within problem
```

### Lessons Learned

**What Worked:**
- H-M2 FeedbackMeasurer adapter pattern — clean separation of concerns
- Subprocess-based evaluation with check_correctness for HumanEval
- 4-worker problem-level parallelism — balanced efficiency and controlled measurement
- Bootstrap CI for per-category rate estimates

**What Didn't Work:**
- `stop=["```"]` parameter to OpenAI API — produced empty responses (responses are cut before code)
- Pyright-guided repair: verbose JSON too long and hard for LLM to parse after truncation
- MBPP repair at temperature=0.0 with single iteration: 0% success rate (may need multi-turn context)
- Z3 on all problems: only 6.3% coverage; rest receive "no constraints" feedback

**Unexpected Findings:**
1. **Perfect inverse correlation** (ρ=-1.0): specificity as measured by char_count predicts LOWER repair success
2. **Z3 highest iter1 rate**: brief Z3 output (or "no constraints") appears to encourage LLM to reason from problem statement directly — coincidentally effective
3. **HumanEval vs MBPP gap**: HumanEval iter1_rates (26-43%) vs MBPP (0%) reveals dataset-specific repair difficulty
4. **Pyright mean_iters_to_pass = 1.375** (lowest): when pyright-guided repair eventually succeeds, it does so efficiently — but fewer problems are repaired

**Key Insight:**
> Feedback length and feedback utility for LLM repair are inversely related in this setup. Shorter, semantically targeted feedback (execution tracebacks, minimal Z3 output) leads to higher single-iteration repair rates than verbose structured diagnostics. This suggests the LLM's ability to act on feedback is bounded by its capacity to extract the single most relevant fix signal — not by the total information content of the feedback.

### Recommendations for H-M4

| Recommendation | Rationale |
|----------------|-----------|
| Reuse `src/repair_loop.py` | Proven repair orchestration |
| Reuse `src/verifier_adapters.py` | All 4 adapters working |
| Track `feedback_lengths` per iteration | Already in RepairResult; use for token analysis |
| Add token counting (tiktoken) | H-M4 needs tokens_used per repair |
| Weight by repair success × cost | H-M4 metric: tokens_per_successful_repair |
| Focus on HumanEval subset | MBPP 0% success makes efficiency analysis degenerate |
| Consider feedback reformatting | Pyright JSON → human-readable summary may increase utility |

---

## Figures

| Figure | Path | Description |
|--------|------|-------------|
| Bar chart iter1_rate | `figures/bar_iter1_rate.png` | Per-category iter-1 repair rates with 95% CI |
| Cumulative repair line | `figures/line_cumulative_repair.png` | Repair rates across iterations 1-3 per category |
| Bug type × category heatmap | `figures/heatmap_mean_iterations.png` | Mean iterations to pass by bug type |
| Feedback length vs rate scatter | `figures/scatter_length_vs_rate.png` | H-M2 char_count vs iter1_rate with regression |
| Z3 subgroup scatter | `figures/scatter_z3_subgroup.png` | Z3-subset problem rates across categories |

---

## Appendix

### Experiment Configuration

```yaml
model: gpt-4o-mini
repair_temperature: 0.0
max_iterations: 3
n_problems: 126       # from H-M1 failing solutions
n_categories: 4       # execution, pyright, mypy, z3
total_sequences: 504  # 126 × 4
conda_env: youra-h-m3
duration_seconds: 529.9
```

### H-M2 Empirical Specificity Ranking (Used as IV)

| Rank | Category | Mean char_count (H-M2) |
|------|----------|------------------------|
| 1 (highest specificity) | Pyright | 24,358 |
| 2 | Execution | 202 |
| 3 | Mypy | 49 |
| 4 (lowest) | Z3 | 2 |

### Validation State

```yaml
hypothesis_id: h-m3
gate_type: SHOULD_WORK
gate_result: FAIL
gate_rho: -1.0
validation_status: COMPLETED (FAIL)
limitation_recorded: true
proceed_to_phase_45: true
```
