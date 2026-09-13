# Product Requirements Document: h-m1

**Project:** Conditional Mechanistic Complementarity of Formal Repair Strategies for LLM-Generated Python Code
**Hypothesis:** h-m1 (MECHANISM / INCREMENTAL — prerequisite: h-e1)
**Date:** 2026-05-09
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Status:** Phase 2C Complete → Phase 3 PRD Generation

---

## 1. Executive Summary

This PRD defines implementation requirements for **h-m1**: a MECHANISM hypothesis that verifies SynCode grammar-constrained decoding operates via a distinct syntactic failure channel — measurably reducing ast.parse failure rate in CodeLlama-7B-generated Python code on the full HumanEval benchmark (164 problems, N=20 per problem).

**Hypothesis Statement:** Under evaluation of CodeLlama-7B-generated Python code using SynCode grammar-constrained decoding vs. unconstrained baseline on HumanEval (N=20 frozen pool per problem), if SynCode is applied at generation time via LogitsProcessor CFG masking, then the SynCode-generated pool shows statistically significant reduction in ast.parse failure rate compared to baseline pool (directional improvement, bootstrap 95% CI), because SynCode masks tokens that violate Python CFG pushdown automaton during generation, eliminating syntactic invalidity by construction.

**Gate:** MUST_WORK — failure blocks h-m2, h-m3, h-m4.

**Success Criteria (both required):**
1. `delta_ast = mean(baseline_failure_rate) - mean(syncode_failure_rate) > 0`
2. Bootstrap 95% CI lower bound > 0 (CI excludes 0, one-sided)

**Incremental Context:** Builds on h-e1 (COMPLETED: delta_ast=0.075, z3_eligibility=0.25, mypy_structured=1.0). Reuses CodeLlama-7B cached weights, T=0.8, fixed seed scheme. Extends from 20-problem subset to full 164-problem HumanEval.

---

## 2. Problem Statement

H-E1 established operational toolchain existence (SynCode reduces ast.parse failure rate on 20-problem subset; delta_ast=0.075). H-M1 must now rigorously verify the mechanism with statistical significance on the full benchmark:

1. Generate frozen pools (baseline + SynCode) for all 164 HumanEval problems, N=20 samples each
2. Measure per-problem ast.parse failure rates for both conditions
3. Compute `delta_ast` and bootstrap 95% CI to confirm statistical significance
4. Classify failures via Failure Mode Distribution (FMD) to confirm SynCode operates specifically on the syntax stratum
5. Extract and serialize F_SynCode→✓ transition set for downstream use by h-m2/h-m3

This is an **inference-only statistical experiment** — no model training, no novel architecture. The goal is mechanistic verification that SynCode's CFG LogitsProcessor causally reduces syntactic invalidity.

---

## 3. Functional Requirements

### FR-1: Extend Baseline Frozen Pool to 164 Problems

**Description:** Generate or extend the baseline (unconstrained CodeLlama-7B) frozen pool from h-e1's 20 problems to the full 164 HumanEval problems.

**Acceptance Criteria:**
- Baseline pool covers all 164 HumanEval+ problems (from evalplus)
- N=20 samples per problem with fixed seeds: `seed = problem_idx × 100 + sample_idx`
- First 20 problems reuse h-e1 baseline pool if available at `h-e1/data/baseline_pool.jsonl`; remaining 144 generated fresh with identical parameters
- Generation parameters: temperature=0.8, max_new_tokens=512, do_sample=True, top_p=0.95
- Pool serialized to `h-m1/data/baseline_pool.jsonl` (format: `{task_id, problem_idx, sample_idx, seed, completion, ast_valid}`)
- Baseline ast.parse failure rate computed per problem and stored

**Dependencies:** `pip install evalplus>=0.3.0 transformers>=4.35.0 torch accelerate`

---

### FR-2: SynCode-Constrained Pool Generation (164 Problems)

**Description:** Generate SynCode-constrained (CFG LogitsProcessor) pool for all 164 HumanEval problems, using identical seeds as baseline.

**Acceptance Criteria:**
- SynCode model initialized: `SynCode(model='codellama/CodeLlama-7b-hf', grammar='python', mode='grammar_mask', device='auto', max_new_tokens=512)`
- N=20 samples per problem, identical seed scheme as baseline
- `constraint_active` flag logged per sample: `[SynCode] constraint_active={bool} problem={idx} sample={idx}`
- Pool serialized to `h-m1/data/syncode_pool.jsonl` (format: `{task_id, problem_idx, sample_idx, seed, completion, ast_valid, constraint_active}`)
- SynCode pool generation completes for all 164 problems without crashing

**Dependencies:** `pip install syncode` (fallback: `git clone https://github.com/uiuc-focal-lab/syncode && pip install -e .`)

---

### FR-3: AST Parse Failure Rate Computation

**Description:** Compute per-problem ast.parse failure rates for baseline and SynCode pools, then compute delta_ast.

**Acceptance Criteria:**
- For each of 164 problems: `failure_rate_i = count(ast.parse fails in pool_i) / N` for both conditions
- Arrays `baseline_failure_rates[164]` and `syncode_failure_rates[164]` computed
- `delta_ast = mean(baseline_failure_rates) - mean(syncode_failure_rates)` computed
- Results saved to `h-m1/results/ast_failure_rates.json`:
  ```json
  {
    "per_problem": [{"task_id": ..., "baseline_rate": ..., "syncode_rate": ..., "delta": ...}],
    "aggregate": {"baseline_mean": ..., "syncode_mean": ..., "delta_ast": ...}
  }
  ```

**Dependencies:** Python stdlib (`ast`, `json`)

---

### FR-4: Bootstrap CI Statistical Test

**Description:** Perform paired bootstrap CI (10,000 iterations) at problem level to determine if delta_ast is statistically significant.

**Acceptance Criteria:**
- Bootstrap CI computed using paired problem-level differences (164 problem pairs)
- `n_bootstrap=10000`, alpha=0.05, one-sided (tests reduction)
- Output: `(delta_mean, ci_lower, ci_upper, p_value)` where p_value = fraction of bootstrap samples ≤ 0
- Gate evaluation: PASS if `delta_ast > 0` AND `ci_lower > 0`
- Results saved to `h-m1/results/bootstrap_ci.json`

**Gate Logic:**
| Condition | Result |
|-----------|--------|
| delta_ast > 0 AND ci_lower > 0 | MUST_WORK PASS |
| delta_ast > 0 AND ci_lower ≤ 0 | Insufficient evidence — PARTIAL (explore) |
| delta_ast ≤ 0 | MUST_WORK FAIL → re-route to Phase 2A |

**Dependencies:** `pip install numpy>=1.24.0`

---

### FR-5: Failure Mode Distribution (FMD) Classification

**Description:** Classify each completion's failure type using Python-native signals to verify SynCode reduces specifically the syntax stratum.

**Acceptance Criteria:**
- FMD classification for all samples in both pools:
  - `syntax`: `ast.parse()` raises `SyntaxError`
  - `type`: `mypy.api.run()` returns type errors (exit_code=1 with error messages)
  - `functional`: EvalPlus test suite fails (ast_valid=True but tests fail)
  - `success`: All checks pass
- FMD summary computed: proportion of each category for baseline vs SynCode pools
- Syntax stratum shift: `syntax_rate_baseline - syntax_rate_syncode > 0` (directional check)
- Results saved to `h-m1/results/fmd_results.json`

**Dependencies:** `pip install mypy>=1.0.0 evalplus>=0.3.0`

---

### FR-6: F_SynCode→✓ Transition Set Extraction

**Description:** Extract and serialize the F_SynCode→✓ set — all (problem_idx, sample_idx) pairs where baseline fails ast.parse AND SynCode succeeds.

**Acceptance Criteria:**
- For each (problem_idx, sample_idx): identify transitions where `baseline[i][j].ast_valid=False` AND `syncode[i][j].ast_valid=True`
- Transition set serialized to `h-m1/results/F_SynCode_success_transitions.json`:
  ```json
  {
    "transitions": [{"problem_idx": ..., "sample_idx": ..., "task_id": ...}],
    "transition_count": ...,
    "transition_rate": ...,
    "coverage_by_problem": [{"problem_idx": ..., "task_id": ..., "transitions": ...}]
  }
  ```
- Required by h-m2 for Jaccard overlap / C_score complementarity analysis
- Transition count and rate logged as summary statistics

**Dependencies:** Python stdlib (`json`)

---

### FR-7: Mechanism Verification Pre-Check

**Description:** Before running full experiment, verify SynCode's CFG LogitsProcessor is actively constraining generation (not just nominal integration).

**Acceptance Criteria:**
- Pre-check verifies:
  1. `GrammarAlignedLogitsProcessor` present in model's logits_processor list
  2. 5-sample test run: `constraint_active_rate ≥ 0.3` (at least 30% of test samples show active constraint)
  3. Baseline failure rate measurable on 5 test samples (non-trivially > 0 confirms problem difficulty)
- If pre-check fails: log warning and proceed with explicit note in results
- Pre-check result saved to `h-m1/results/mechanism_verification.json`

---

### FR-8: Visualization

**Description:** Generate required figures for gate metric reporting and analysis.

**Required Figures (Mandatory):**

1. **Gate Metrics Comparison Bar Chart** (`h-m1/figures/gate_metrics.pdf` + `.png`):
   - X-axis: Conditions (Baseline, SynCode)
   - Y-axis: ast.parse failure rate (aggregate mean)
   - Error bars: 95% bootstrap CI
   - Annotation: delta_ast value, CI bounds, PASS/FAIL gate result
   - Dashed line at baseline mean for reference

2. **Per-Problem Failure Rate Scatter Plot** (`h-m1/figures/per_problem_scatter.pdf` + `.png`):
   - X: Baseline ast.parse failure rate (per problem)
   - Y: SynCode ast.parse failure rate (per problem)
   - Diagonal line = no improvement; points below diagonal = SynCode benefit
   - Color: problem difficulty quartile (based on baseline pass@1)
   - Annotation: count of problems below/above diagonal

3. **FMD Comparison Bar Chart** (`h-m1/figures/fmd_comparison.pdf` + `.png`):
   - Side-by-side bars: Baseline vs SynCode
   - X: Failure categories (syntax, type, functional, success)
   - Y: Proportion of all samples
   - Shows shift from syntax failures under SynCode constraint

4. **F_SynCode→✓ Transition Heatmap** (`h-m1/figures/transition_heatmap.pdf` + `.png`):
   - 164 problems × 20 samples grid (or subset if too large)
   - Color: baseline_fail+syncode_success (transition), baseline_fail+syncode_fail, baseline_pass
   - Reveals which problems benefit most from SynCode constraint

**Acceptance Criteria:**
- All figures saved to `h-m1/figures/` in both PDF and PNG formats
- matplotlib/seaborn with publication-quality formatting (fontsize ≥ 11, dpi=150)
- PASS/FAIL annotation on gate metric panel
- All figures generated even if experiment fails (with partial data)

**Dependencies:** `pip install matplotlib>=3.7.0 seaborn>=0.12.0`

---

## 4. Data Specification

### Dataset 1: HumanEval+ (Full Benchmark)

| Property | Value |
|----------|-------|
| Source | evalplus pip package |
| Size | 164 problems (full test set) |
| Loading | `from evalplus.data import get_human_eval_plus` |
| Manual Download | No (auto via PyPI) |
| Split | Full test set — no train/val split needed |
| Use | Baseline pool generation, SynCode pool generation, bootstrap CI |

### Generated Data: Baseline Frozen Pool

| Property | Value |
|----------|-------|
| Source | In-experiment generation (CodeLlama-7B unconstrained) |
| Size | 164 × 20 = 3,280 samples |
| Storage | `h-m1/data/baseline_pool.jsonl` |
| Format | `{task_id, problem_idx, sample_idx, seed, completion, ast_valid}` per line |
| Reuse from h-e1 | First 20 problems (if h-e1/data/baseline_pool.jsonl exists) |

### Generated Data: SynCode-Constrained Pool

| Property | Value |
|----------|-------|
| Source | In-experiment generation (CodeLlama-7B + SynCode CFG LogitsProcessor) |
| Size | 164 × 20 = 3,280 samples |
| Storage | `h-m1/data/syncode_pool.jsonl` |
| Format | `{task_id, problem_idx, sample_idx, seed, completion, ast_valid, constraint_active}` per line |

### Output Data: Statistical Results

| File | Content |
|------|---------|
| `h-m1/results/ast_failure_rates.json` | Per-problem failure rates, aggregate delta_ast |
| `h-m1/results/bootstrap_ci.json` | Bootstrap CI results, p_value, gate decision |
| `h-m1/results/fmd_results.json` | FMD classification distribution |
| `h-m1/results/F_SynCode_success_transitions.json` | F_SynCode→✓ transition set (used by h-m2) |
| `h-m1/results/mechanism_verification.json` | Pre-check results |
| `h-m1/results/metrics.json` | Consolidated gate metrics |

---

## 5. Models

| Model | HuggingFace ID | Parameters | Role |
|-------|---------------|------------|------|
| CodeLlama-7B (Baseline) | `codellama/CodeLlama-7b-hf` | 7B | Unconstrained generation pool |
| CodeLlama-7B + SynCode | `codellama/CodeLlama-7b-hf` + SynCode CFG | 7B | Grammar-constrained generation pool |

**Loading:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-hf", device_map="auto"
)
```

**SynCode Wrapping:**
```python
from syncode import SynCode
syncode_model = SynCode(
    model='codellama/CodeLlama-7b-hf',
    grammar='python',
    mode='grammar_mask',
    device='auto',
    max_new_tokens=512
)
```

**Generation Parameters:** temperature=0.8, max_new_tokens=512, do_sample=True, top_p=0.95
**Seed Scheme:** `seed = problem_idx × 100 + sample_idx` (identical for both conditions)
**Cache:** `~/.cache/huggingface/hub/models--codellama--CodeLlama-7b-hf` (from h-e1)

**Expected baseline performance:** ast.parse failure rate ~5–15%; SynCode delta_ast ≥ 0.03 (from h-e1: 0.075 on 20-problem subset)

---

## 6. Non-Functional Requirements

### NFR-1: Single GPU Execution
All experiments run on one GPU. Select via `CUDA_VISIBLE_DEVICES=<lowest_memory_gpu>` before running. CPU fallback via `device_map="auto"`.

### NFR-2: No Docker Dependency
All tools pip-installable. Python-native environment. No Docker, no containers.

### NFR-3: Reproducibility
Fixed seed scheme (`seed = problem_idx × 100 + sample_idx`). Results deterministic within ±0.5% across runs. Seeds identical for baseline and SynCode conditions (controlled comparison).

### NFR-4: Incremental Execution Support
Code must support resuming from checkpoint if interrupted:
- Track completed problems in `h-m1/results/progress.json`
- Skip problems already generated; append to existing JSONL files

### NFR-5: Compute Budget
- Baseline pool generation (164 × 20): ~2–4 hours single GPU
- SynCode pool generation (164 × 20): ~4–8 hours single GPU (CFG parsing overhead ~2×)
- Statistical analysis + visualization: < 30 minutes
- Total: ≤ 12 hours single GPU

### NFR-6: Output Format
Gate metrics in `h-m1/results/metrics.json`. All figures in PDF + PNG at `h-m1/figures/`. Pools in JSONL at `h-m1/data/`.

---

## 7. Dependencies

### Python Packages
```
evalplus>=0.3.0
transformers>=4.35.0
torch>=2.0.0
accelerate>=0.20.0
syncode                # grammar-constrained decoding (Ugare et al. 2024)
mypy>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
numpy>=1.24.0
scipy>=1.10.0
pyyaml>=6.0
```

### From H-E1 (Reused)
- CodeLlama-7B model weights (cached)
- Baseline pool for first 20 problems (extend to 164)
- SynCode pip package (confirmed operational)
- Seed scheme (confirmed reproducible)

### External (Optional Fallback)
- `git clone https://github.com/uiuc-focal-lab/syncode` — if PyPI syncode install fails

---

## 8. Success Criteria

### Gate: MUST_WORK

| Condition | Metric | Threshold | Gate Impact |
|-----------|--------|-----------|-------------|
| SynCode reduces ast.parse failures | `delta_ast = mean(baseline_rate) - mean(syncode_rate)` | `> 0` | REQUIRED |
| Statistical significance | Bootstrap 95% CI lower bound | `> 0` (CI excludes 0) | REQUIRED |

**PASS:** Both conditions met → h-m2, h-m3, h-m4 unblocked; proceed to Phase 4.5
**PARTIAL (delta_ast > 0, CI includes 0):** Insufficient statistical power — explore with larger N or different CI method
**FAIL (delta_ast ≤ 0):** SynCode shows no effect → EXPLORE LogitsProcessor integration → re-route to Phase 2A if unfixable

### Secondary Metrics (Non-gating)
- FMD syntax stratum reduction: directional decrease in syntax failure proportion under SynCode
- `constraint_active_rate` ≥ 0.3 across all samples (mechanism verification)
- F_SynCode→✓ transition set generated and serialized for h-m2

---

## 9. Out of Scope

- Training or fine-tuning any model
- Comparison between repair strategies (reserved for h-m2, h-m3, h-m4)
- Multi-language evaluation (Python-only)
- Docker-based execution
- Z3 repair or mypy feedback repair (scoped to h-m2, h-m3)
- MBPP evaluation (h-m1 uses HumanEval only for statistical power; MBPP reserved for h-m4)
- Pass@1 functional correctness (h-m1 focuses on ast.parse syntactic correctness)
- Publishing results (Phase 6)

---

*Generated: Phase 3 Step 2 — PRD (inline execution, no-mcp environment; BMAD bmm PRD workflow not installed)*
*Input: h-m1/02c_experiment_brief.md*
*Output: h-m1/03_prd.md*
*Predecessor: h-e1/03_prd.md (pattern reference)*
