# Product Requirements Document: h-e1

**Project:** Conditional Mechanistic Complementarity of Formal Repair Strategies for LLM-Generated Python Code
**Hypothesis:** h-e1 (EXISTENCE / FOUNDATION)
**Date:** 2026-05-09
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Status:** Phase 2C Complete → Phase 3 PRD Generation

---

## 1. Executive Summary

This PRD defines implementation requirements for **h-e1**: an EXISTENCE (PoC) hypothesis that validates the foundational toolchain operationality for formal repair strategy experiments. The experiment verifies that three formal repair tools—SynCode (grammar-constrained decoding), z3-solver (SMT constraint encoding), and mypy/ast (static analysis feedback)—operate correctly on CodeLlama-7B-generated Python code using HumanEval and MBPP benchmarks.

**Gate:** MUST_WORK — failure blocks all downstream mechanism hypotheses (h-m1 through h-m4).

**Success Criteria (all three required):**
1. `Δ_ast > 0` — SynCode-constrained pool has lower ast.parse failure rate than baseline pool
2. `z3_eligibility_rate ≥ 0.15` — Z3 can encode ≥15% of HumanEval problems as SMT constraints
3. `mypy_structured_output_rate ≥ 0.90` — mypy.api.run() returns parseable output on ≥90% of samples

---

## 2. Problem Statement

Before testing whether formal repair strategies exhibit mechanistic complementarity (main hypothesis), we must establish that:
- The benchmark infrastructure (evalplus HumanEval+/MBPP+) is loadable and functional
- CodeLlama-7B generates plausible Python code completions without Docker dependency
- SynCode integrates with HuggingFace via LogitsProcessor interface and reduces syntactic failures
- Z3 can encode a meaningful fraction of HumanEval problems as SMT constraints
- mypy.api.run() returns structured, parseable type-error output

This is a pure **infrastructure validation** experiment—no training, no novel model, no performance comparison. The goal is operational verification of the three-tool pipeline.

---

## 3. Functional Requirements

### FR-1: evalplus Dataset Loading

**Description:** Load HumanEval+ (164 problems) and MBPP+ (374 problems) using the official evalplus pip package.

**Acceptance Criteria:**
- `get_human_eval_plus()` returns exactly 164 problem dicts, each with keys: `task_id`, `prompt`, `canonical_solution`, `test`
- `get_mbpp_plus()` returns exactly 374 problem dicts
- Dataset loading completes without errors in Python-native environment (no Docker required)

**Dependencies:** `pip install evalplus>=0.3.0`

---

### FR-2: CodeLlama-7B Baseline Generation (Frozen Pool)

**Description:** Load CodeLlama-7B via HuggingFace transformers and generate a frozen baseline pool of N=20 samples per HumanEval problem with fixed seeds.

**Acceptance Criteria:**
- Model loads via `AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-hf", device_map="auto")`
- Tokenizer loads via `AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")`
- Generation parameters: temperature=0.8, max_new_tokens=256, seeds=[0..19]
- Pool format: `{task_id: [completion_str × 20]}` serialized to JSONL at `h-e1/data/baseline_pool.jsonl`
- Baseline ast.parse failure rate measurable and non-trivially > 0 (expected 5–15%)

**Dependencies:** `pip install transformers>=4.35 accelerate torch`

---

### FR-3: SynCode Grammar-Constrained Generation

**Description:** Integrate SynCode LogitsProcessor with CodeLlama-7B to generate a grammar-constrained pool for the same HumanEval problems.

**Acceptance Criteria:**
- SynCode importable: `from syncode import SynCode`
- SynCode wraps HuggingFace model: `SynCode(model=model, grammar="python", tokenizer=tokenizer, mode="grammar_mask")`
- Grammar-constrained pool generated: N=20 samples per problem, same seeds as baseline
- Pool serialized to `h-e1/data/syncode_pool.jsonl`
- Mechanism verification: log `grammar_decoder.filtered_count` per generation step; assert count > 0 for ≥50% of problems (confirms SynCode constraint is active)

**Dependencies:** `pip install syncode` (fallback: `git clone uiuc-focal-lab/syncode && pip install -e .`)

---

### FR-4: Z3 SMT Constraint Eligibility Check

**Description:** For each HumanEval problem, attempt to encode its postconditions as Z3 SMT constraints. Report the eligibility rate.

**Acceptance Criteria:**
- Z3 importable: `import z3`
- Eligibility check: parse docstring assertions, attempt Z3 LIA encoding, timeout=2000ms
- Output: `{task_id: bool}` dict of SMT eligibility per problem
- Eligibility rate: `eligible_count / 164` (target ≥ 0.15)
- Results saved to `h-e1/data/z3_eligibility.json`

**Dependencies:** `pip install z3-solver>=4.12.0`

---

### FR-5: mypy Structured Feedback Check

**Description:** Run mypy.api.run() on a sample of baseline-generated code completions. Verify that structured, parseable type-error output is returned.

**Acceptance Criteria:**
- mypy importable: `import mypy.api`
- For a sample of N=10 HumanEval problems (first baseline completion per problem):
  - Call `mypy.api.run([temp_file, "--ignore-missing-imports"])`
  - Response is a 3-tuple `(stdout, stderr, exit_code)` with exit_code ∈ {0, 1}
  - `mypy_rate = successes / 10` (target ≥ 0.90)
- Results saved to `h-e1/data/mypy_results.json`

**Dependencies:** `pip install mypy>=1.0`

---

### FR-6: Existence Check Integration and Metrics Computation

**Description:** Run all three operationality checks and compute the primary gate metrics.

**Acceptance Criteria:**
- `Δ_ast = ast_fail_rate(baseline_pool) - ast_fail_rate(syncode_pool)` computed over all HumanEval problems
- `z3_eligibility_rate = eligible_problems / 164` computed
- `mypy_structured_output_rate` computed from FR-5 sample
- Gate evaluation: PASS if all 3 conditions met; PARTIAL if 2/3; FAIL if SynCode shows no effect AND z3_rate < 0.15
- Results logged to `h-e1/results/metrics.json`

**Dependencies:** Python stdlib (`ast`, `json`)

---

### FR-7: Visualization

**Description:** Generate required figures for gate metric reporting.

**Required Figures:**
1. **Gate Metrics Bar Chart** (`h-e1/figures/gate_metrics.pdf` + `.png`): Three-panel bar chart showing:
   - Panel 1: ast.parse failure rate — baseline vs SynCode, with direction-of-improvement annotation
   - Panel 2: Z3 eligibility rate vs threshold (0.15 dashed line)
   - Panel 3: mypy structured output rate vs threshold (0.90 dashed line)
2. **Per-problem ast.parse failure heatmap** (`h-e1/figures/ast_failure_heatmap.pdf` + `.png`): Per-problem failure rates for baseline vs SynCode (sorted)
3. **Z3 eligibility per-problem** (`h-e1/figures/z3_eligibility.pdf` + `.png`): Bar chart of Z3 encodability per HumanEval problem cluster
4. **mypy error type distribution** (`h-e1/figures/mypy_error_types.pdf` + `.png`): Breakdown of mypy error categories across sampled problems

**Acceptance Criteria:**
- All figures saved to `h-e1/figures/` in both PDF and PNG
- All figures use matplotlib/seaborn with publication-quality formatting
- PASS/FAIL annotation on each gate metric panel

**Dependencies:** `pip install matplotlib>=3.7 seaborn>=0.12`

---

## 4. Data Specification

### Dataset 1: HumanEval+ (Primary)

| Property | Value |
|----------|-------|
| Source | evalplus pip package |
| Size | 164 problems |
| Loading | `from evalplus.data import get_human_eval_plus` |
| Manual Download | No (auto via PyPI) |
| Use | All 3 operationality checks (SynCode pool, Z3 eligibility, mypy feedback) |

### Dataset 2: MBPP+ (Scope Validation)

| Property | Value |
|----------|-------|
| Source | evalplus pip package |
| Size | 374 problems |
| Loading | `from evalplus.data import get_mbpp_plus` |
| Manual Download | No (auto via PyPI) |
| Use | Scope validation — confirm tool operationality extends beyond HumanEval |

### Generated Data: Frozen Baseline Pool

| Property | Value |
|----------|-------|
| Source | In-experiment generation |
| Size | 164 × 20 = 3,280 samples |
| Storage | `h-e1/data/baseline_pool.jsonl` |
| Format | `{task_id, completion, seed, generation_time}` per line |

### Generated Data: SynCode-Constrained Pool

| Property | Value |
|----------|-------|
| Source | In-experiment generation |
| Size | 164 × 20 = 3,280 samples |
| Storage | `h-e1/data/syncode_pool.jsonl` |
| Format | `{task_id, completion, seed, filtered_token_count}` per line |

---

## 5. Models

| Model | HuggingFace ID | Parameters | Role |
|-------|---------------|------------|------|
| CodeLlama-7B | `codellama/CodeLlama-7b-hf` | 7B | Baseline + SynCode-wrapped generation |

**Loading:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-hf", device_map="auto"
)
```

**Generation parameters:** temperature=0.8, max_new_tokens=256, seeds=[0..19]

**Expected baseline performance:** pass@1 ~30–37% on HumanEval; ast.parse failure rate ~5–15%

---

## 6. Non-Functional Requirements

### NFR-1: Single GPU Execution
All experiments run on one GPU (select via `CUDA_VISIBLE_DEVICES`, lowest memory usage). CPU fallback enabled via `device_map="auto"`.

### NFR-2: No Docker Dependency
All tools must be pip-installable and operate without Docker. This is a Python-native environment constraint.

### NFR-3: Reproducibility
Fixed seeds (seeds=[0..19]) for all pool generation. Results must be deterministic within ±0.5% across runs.

### NFR-4: Compute Budget
- Baseline pool generation (CodeLlama-7B, 164 × 20): ~2–4 hours single GPU
- SynCode pool generation (same scale): ~3–6 hours (grammar constraint overhead)
- Z3 eligibility check (164 problems, 2000ms timeout): < 30 minutes
- mypy sample check (10 problems): < 5 minutes
- Total: ≤ 12 hours single GPU

### NFR-5: Output Format
All metrics in JSON (`h-e1/results/metrics.json`). All figures in PDF + PNG (`h-e1/figures/`).

---

## 7. Dependencies

### Python Packages
```
evalplus>=0.3.0
transformers>=4.35.0
torch>=2.0.0
accelerate>=0.20.0
syncode            # grammar-constrained decoding
z3-solver>=4.12.0
mypy>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
numpy>=1.24.0
scipy>=1.10.0
pyyaml>=6.0
```

### External (Optional Fallback)
- `git clone https://github.com/uiuc-focal-lab/syncode` — if PyPI syncode fails

---

## 8. Success Criteria

### Gate: MUST_WORK

| Condition | Metric | Threshold | Gate Impact |
|-----------|--------|-----------|-------------|
| SynCode operational | `Δ_ast = ast_fail_rate_baseline - ast_fail_rate_syncode` | `Δ_ast > 0` | REQUIRED |
| Z3 eligibility | `z3_eligibility_rate = eligible/164` | `≥ 0.15` | REQUIRED |
| mypy operational | `mypy_structured_output_rate` | `≥ 0.90` | REQUIRED |

**PASS:** All 3 conditions met → h-m1 through h-m4 unblocked
**PARTIAL:** Any 2 of 3 conditions met → scope reduction, limited progression
**FAIL:** SynCode shows no effect AND z3_rate < 0.15 → route to Phase 0

---

## 9. Out of Scope

- Training or fine-tuning any model
- Comparing strategy performance against each other (reserved for h-m1 through h-m4)
- Multi-language evaluation (Python-native only)
- Docker-based execution environments
- Publishing results or writing paper sections (Phase 6)

---

*Generated: Phase 3 Step 2 — PRD (inline execution, no-mcp environment)*
*Input: h-e1/02c_experiment_brief.md*
*Output: h-e1/03_prd.md*
*Workflow: BMAD v6 PRD Workflow (executed inline)*
