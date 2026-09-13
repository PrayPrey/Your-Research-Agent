# Phase 4 Validation Report: h-m2

**Generated:** 2026-03-18T13:00:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5 (h-m3)
**Gate Type:** SHOULD_WORK
**Gate Result:** ✅ PASS

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-m2 |
| **Type** | MECHANISM |
| **Statement** | Under model-specific pass@1 stratification, if problems are assigned to hard (pass@1=0.0) and easy (pass@1>=0.6) tiers per model, then tier assignments reflect genuine competence differences (Jaccard similarity of hard-tier problem sets across models > 0.3), because structurally hard problems tend to be hard across different architectures. |
| **Prerequisites** | h-m1 (PASS) |
| **Base Hypothesis** | h-m1 (incremental — consumes pass_at_1_hm1_verified.json) |
| **Duration** | ~1 hour (Phase 4 coding + experiment) |
| **Conda Env** | youra-h-m2 |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 17 |
| Completed | 17 |
| Coder-Validator Cycles | 1 |
| Tasks with Fixes | 3 (pyproject.toml build-backend, test_jaccard_ab expected value, EXPECTED_JACCARD_BC value) |
| Budget Used | 17/30 |

### Generated Files

| File | Description |
|------|-------------|
| `src/h_m2/__init__.py` | Package init |
| `src/h_m2/stratify.py` | Tier stratification: `load_hm1_pass_at_1`, `compute_difficulty_tiers`, `validate_tier_sizes` |
| `src/h_m2/jaccard.py` | Jaccard analysis: `jaccard_similarity`, `compute_cross_model_jaccard`, `compute_consensus_set` |
| `src/h_m2/analyze.py` | Distribution analysis: `compute_histograms`, `build_tier_assignments_df` |
| `src/h_m2/evaluate.py` | Gate evaluation: `evaluate_gate`, `verify_mechanism_activated`, `build_stratification_results` |
| `src/h_m2/visualize_hm2.py` | 5-figure visualization suite |
| `src/h_m2/run_hm2_stratification.py` | CLI orchestrator (argparse, exit codes 0/1/2) |
| `tests/test_jaccard.py` | 19 unit tests for jaccard module |
| `tests/test_stratify.py` | 19 unit tests for stratify module |
| `tests/test_evaluate.py` | 14 unit tests for evaluate module |
| `pyproject.toml` | Package build config (setuptools.build_meta) |
| `requirements.txt` | numpy, matplotlib, pandas, pytest |

### Test Results

| Test Suite | Tests | Passed | Failed |
|------------|-------|--------|--------|
| test_jaccard.py | 19 | 19 | 0 |
| test_stratify.py | 19 | 19 | 0 |
| test_evaluate.py | 14 | 14 | 0 |
| **Total** | **52** | **52** | **0** |

---

## Code Quality Checklist

- [✓] Syntax validation passed (all modules import without errors)
- [✓] Type hints compliance (Python 3.10+, `from __future__ import annotations`)
- [✓] API signatures match 03_logic.md
- [✓] `jaccard_similarity` returns float in [0.0, 1.0] with empty-set guard
- [✓] `compute_cross_model_jaccard` uses sorted keys + itertools.combinations for deterministic pairs
- [✓] `compute_consensus_set` uses percentage = n / 542
- [✓] JACCARD_GATE_THRESHOLD = 0.3 (strict greater-than, 0.30 does NOT pass)
- [✓] CodeLlama degenerate case (n_easy=0 on HumanEval) triggers UserWarning, not ValueError
- [✓] `matplotlib.use("Agg")` before all imports in visualize module
- [✓] CLI exit codes: 0=PASS, 1=FAIL, 2=error
- [✓] All 52 unit tests passing

---

## Experiment Results

### Tier Sizes (Combined HumanEval+ MBPP+, 542 problems)

| Model | n_hard | n_easy | n_medium | total |
|-------|--------|--------|----------|-------|
| Llama3-8B | 228 (42.1%) | 167 (30.8%) | 147 (27.1%) | 542 |
| CodeLlama-7B | 341 (62.9%) | 37 (6.8%) | 164 (30.3%) | 542 |
| DeepSeek-6.7B | 173 (31.9%) | 200 (36.9%) | 169 (31.2%) | 542 |

**Note:** CodeLlama-7B has n_easy=0 on HumanEval benchmark (degenerate — confirmed by h-e1). Combined tiers use all 542 problems per the 03_tasks.yaml specification.

### Tier Sizes by Benchmark

| Model | Benchmark | n_hard | n_easy | n_medium |
|-------|-----------|--------|--------|----------|
| Llama3-8B | HumanEval | 78 | 39 | 47 |
| Llama3-8B | MBPP | 150 | 128 | 100 |
| CodeLlama-7B | HumanEval | 142 | 0 | 22 |
| CodeLlama-7B | MBPP | 199 | 37 | 142 |
| DeepSeek-6.7B | HumanEval | 68 | 24 | 72 |
| DeepSeek-6.7B | MBPP | 105 | 176 | 97 |

### Cross-Model Jaccard Similarity (Hard Tier, Combined)

| Pair | Jaccard | Threshold | Passes |
|------|---------|-----------|--------|
| Llama3-8B vs CodeLlama-7B | **0.5462** | > 0.3 | ✅ PASS |
| Llama3-8B vs DeepSeek-6.7B | **0.5305** | > 0.3 | ✅ PASS |
| CodeLlama-7B vs DeepSeek-6.7B | **0.4561** | > 0.3 | ✅ PASS |

### Cross-Model Jaccard by Benchmark

| Pair | HumanEval | MBPP |
|------|-----------|------|
| Llama3-8B vs CodeLlama-7B | 0.5278 | 0.5580 |
| Llama3-8B vs DeepSeek-6.7B | 0.5368 | 0.5269 |
| CodeLlama-7B vs DeepSeek-6.7B | 0.4384 | 0.4686 |

**Observation:** Jaccard values are consistent across benchmarks (range 0.44-0.56), indicating the cross-architecture difficulty overlap is benchmark-agnostic.

### Consensus Hard Set

| Metric | Value |
|--------|-------|
| Problems hard for ALL 3 models | **133** |
| As fraction of 542 | **24.5%** |
| HumanEval consensus hard | 50 problems |
| MBPP consensus hard | 83 problems |

133 problems (24.5% of 542) are universally hard across all 3 model families, strongly supporting the hypothesis that structurally hard problems are architecture-independent.

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | SHOULD_WORK |
| **Threshold** | > 0.3 (strict greater-than) |
| **Max Jaccard** | 0.5462 |
| **Pairs Passing** | 3/3 |
| **Gate Satisfied** | ✅ True |
| **Result** | ✅ **PASS** |

### Mechanism Indicators

| Indicator | Status |
|-----------|--------|
| tiers_populated | ✅ True |
| jaccard_computed | ✅ True |
| jaccard_non_trivial | ✅ True |
| tier_sizes_valid | ✅ True |
| **all_activated** | ✅ True |

**Gate Assessment:** All 3 model pairs significantly exceed the J > 0.3 threshold (minimum J = 0.4561, maximum J = 0.5462). The gate passes by a comfortable margin (+0.156 above threshold for the lowest pair). This strongly validates the hypothesis that difficulty tier assignments reflect genuine structural difficulty.

---

## Generated Figures

| Figure | File | Description |
|--------|------|-------------|
| Jaccard Bar Chart | `figures/jaccard_similarity_bars.png` | 3 model pairs × Jaccard score + dashed threshold line (0.3) |
| Pass@1 Histograms | `figures/pass_at_1_histograms.png` | 3×2 grid: 3 models × 2 benchmarks, 6-point bins, tier-colored |
| Tier Size Summary | `figures/tier_size_summary.png` | Stacked bar: hard/medium/easy per model per benchmark |
| Jaccard Heatmap | `figures/jaccard_heatmap.png` | 3×3 symmetric Jaccard matrix (Blues colormap) |
| Consensus Hard Pie | `figures/consensus_hard_pie.png` | Pie: problems hard for 1/3, 2/3, 3/3 models |

---

## Next Steps

Gate Result: **PASS** → Proceed directly to h-m3 (next hypothesis in dependency chain).

h-m3 is now UNBLOCKED. No reflection or modification required.

---

## Phase 2C Handoff

### Proven Components

| Component | File | Type | Evidence |
|-----------|------|------|----------|
| `load_hm1_pass_at_1` | `src/h_m2/stratify.py` | Data loader | Loads 3×542 pass@1 dict, validates schema |
| `split_by_benchmark` | `src/h_m2/stratify.py` | Data splitter | HumanEval/Mbpp prefix split, verified by tests |
| `compute_difficulty_tiers` | `src/h_m2/stratify.py` | Tier stratification | HARD_THRESHOLD=0.0, EASY_THRESHOLD=0.6, disjoint sets |
| `validate_tier_sizes` | `src/h_m2/stratify.py` | Validation | min_size=20, CodeLlama UserWarning for n_easy=0 |
| `jaccard_similarity` | `src/h_m2/jaccard.py` | Core metric | Handles empty sets, returns float [0,1] |
| `compute_cross_model_jaccard` | `src/h_m2/jaccard.py` | Cross-model analysis | Sorted keys, itertools.combinations, deterministic |
| `compute_consensus_set` | `src/h_m2/jaccard.py` | Consensus computation | All-model intersection, percentage = n/542 |
| `compute_overlap_counts_by_n_models` | `src/h_m2/jaccard.py` | Overlap histogram | Keys 1-N models |
| `evaluate_gate` | `src/h_m2/evaluate.py` | Gate evaluation | SHOULD_WORK, strict J>0.3 threshold |
| `build_tier_assignments_df` | `src/h_m2/analyze.py` | DataFrame builder | 542-row CSV with n_models_hard column |
| `run_hm2_stratification.py` | `src/h_m2/` | CLI orchestrator | Full pipeline, exit 0/1/2 |

### Optimal Hyperparameters

```yaml
# h-m2 Confirmed Parameters (for h-m3 reference)
tier_thresholds:
  hard: 0.0        # pass@1 == 0.0 exactly
  easy: 0.6        # pass@1 >= 0.6
  medium: residual # all other

dataset:
  name: EvalPlus (HumanEval+ 164 + MBPP+ 378)
  n_problems_combined: 542
  benchmarks: [humaneval, mbpp]
  input_file: h-m1/results/pass_at_1_hm1_verified.json

models:
  - NousResearch/Meta-Llama-3-8B
  - codellama/CodeLlama-7b-hf
  - deepseek-ai/deepseek-coder-6.7b-base

jaccard_gate:
  type: SHOULD_WORK
  threshold: 0.3
  comparison: strict_greater_than  # 0.30 does NOT pass
  achieved: 0.5462  # well above threshold

tier_sizes_achieved:
  llama3_8b:   {hard: 228, easy: 167, medium: 147}
  codellama_7b: {hard: 341, easy: 37,  medium: 164}
  deepseek_6.7b: {hard: 173, easy: 200, medium: 169}

consensus_hard_set:
  n: 133
  percentage: 0.2454  # 24.5% of 542 problems universally hard
```

### Lessons Learned

**What Worked:**
- Pure statistical analysis (no GPU/model inference) — fast, reproducible
- Incremental design: consuming h-m1's `pass_at_1_hm1_verified.json` directly was clean and simple
- `itertools.combinations` with `sorted(tiers.keys())` ensures deterministic pair ordering
- `np.isclose` for float bin matching in histograms (critical for exact 6-point bins from k=5 sampling)
- SHOULD_WORK gate type was appropriate — results significantly exceed threshold (0.45+ vs 0.30)
- Separating concerns: stratify.py, jaccard.py, analyze.py, evaluate.py, visualize_hm2.py — clean architecture

**What Didn't Work (Fixes Required):**
- `pyproject.toml` initial build-backend was `setuptools.backends.legacy:build` → caused `BackendUnavailable`. Fixed to `setuptools.build_meta`
- `test_jaccard_ab` expected `1/3` but correct answer is `0.5` (intersection=2, union=4) — test fixture calculation error
- `EXPECTED_JACCARD_BC` was `2/5` but hard_b∩hard_c={t3} only → correct is `1/5` — fixture verification gap

**Unexpected Findings:**
- Jaccard values are much higher than expected threshold (all pairs 0.45+, minimum 0.4561). This is strong evidence that problem difficulty is largely architecture-independent.
- CodeLlama-7B has dramatically more hard problems (341 vs 173-228) — this model struggles broadly with code generation at k=5
- Consensus hard set is 24.5% of all problems (133/542), much larger than minimum threshold requirement

**Key Insight:** The strong Jaccard overlap (0.45-0.55) confirms that EvalPlus benchmark difficulty is primarily determined by problem structure/complexity rather than model-specific weaknesses. This validates the foundation for h-m3 (P(True) confidence elicitation) and h-m4 (DELTA_ECE computation) — the tier boundaries are meaningful and stable across architectures.

### Recommendations for Dependent Hypotheses

#### h-m3: P(True) Confidence Elicitation (MUST_WORK gate)

1. **Use combined 542-problem tier assignments** from `h-m2/results/tier_assignments.csv` as direct input. The CSV has columns: `task_id, benchmark, llama3_tier, codellama_tier, deepseek_tier, n_models_hard, n_models_easy`.

2. **Hard tier sizes are sufficient for ECE computation:**
   - Llama3-8B: 228 hard (>>20 threshold)
   - CodeLlama-7B: 341 hard (>>20 threshold)
   - DeepSeek-6.7B: 173 hard (>>20 threshold)

3. **Use per-model tier assignments** (not consensus) for P(True) analysis. Each model's own hard/easy split determines which problems to use for DELTA_ECE computation.

4. **CodeLlama warning:** n_easy=37 combined (borderline for M=15 bins). Use MBPP-only tiers (n_easy=37) for CodeLlama easy-tier ECE to ensure adequate bin coverage.

5. **Suggested architecture for h-m3:** Load `tier_assignments.csv` from h-m2 to get per-model tier labels, then map each `(model, task_id)` pair to its tier for confidence stratification.

6. **GPU requirement:** h-m3 requires logprob extraction (P(True) via `generate()` with `logprobs=True`). Recommend CUDA_VISIBLE_DEVICES=<empty_gpu> with bfloat16 precision.

7. **Expected P(True) range:** Run 3 validation showed P(True) ∈ [0.57, 0.91] for all 3 model families under zero-shot prompting. This is non-degenerate and sufficient for ECE calibration curves.

#### h-m4: DELTA_ECE Computation (MUST_WORK gate)

- The 133-problem consensus hard set provides a strong anchor for understanding which problems are structurally hard across all models.
- ECE(hard) will be computed using per-model hard tiers (not consensus), as specified in the main hypothesis.
- Temperature scaling holdout (20%) applies to full per-model tier assignments.

---

## Appendix

### Output Files

| File | Description |
|------|-------------|
| `h-m2/results/stratification_results.json` | Full pipeline results payload |
| `h-m2/results/tier_assignments.csv` | 542-row per-task tier assignments |
| `h-m2/experiment_results.json` | Gate + metrics summary |
| `h-m2/figures/jaccard_similarity_bars.png` | Jaccard bar chart |
| `h-m2/figures/pass_at_1_histograms.png` | Pass@1 histograms |
| `h-m2/figures/tier_size_summary.png` | Tier size stacked bars |
| `h-m2/figures/jaccard_heatmap.png` | Jaccard similarity heatmap |
| `h-m2/figures/consensus_hard_pie.png` | Consensus hard pie chart |

### Key Constants (for reference)

```python
HARD_THRESHOLD = 0.0   # pass@1 == 0.0
EASY_THRESHOLD = 0.6   # pass@1 >= 0.6
JACCARD_GATE_THRESHOLD = 0.3  # strict greater-than
N_PROBLEMS_COMBINED = 542
MODEL_IDS = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]
```

### Checkpoint State

```yaml
hypothesis_id: h-m2
current_step: 8
gate_result: PASS
tasks:
  total: 17
  completed: 17
  failed: 0
coder_validator_cycles: 1
unattended_mode: true
```

### Verification State Update

- `sub_hypotheses.h-m2.status`: IN_PROGRESS → **COMPLETED**
- `sub_hypotheses.h-m2.gate.satisfied`: null → **true**
- `sub_hypotheses.h-m2.gate.result`: null → **PASS**
- `sub_hypotheses.h-m2.validation.status`: NOT_STARTED → **COMPLETED**
- `statistics.validated_sub_hypotheses`: 2 → **3**
- `statistics.gates_passed`: 2 → **3**
- `workflow.next_action`: Execute Phase 2C → 3 → 4 for **h-m3**
