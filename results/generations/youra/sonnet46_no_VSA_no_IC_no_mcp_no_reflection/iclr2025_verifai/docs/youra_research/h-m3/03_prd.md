# PRD: H-M3 Feedback-Guided Repair Loop — Specificity-Repair Correlation

**Hypothesis:** H-M3
**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Type:** MECHANISM — controlled repair loop experiment (inference-time, no training)

---

## 1. Executive Summary

H-M3 tests whether feedback specificity (as measured in H-M2) causally drives per-iteration repair success rate. Using the same 538-problem corpus (HumanEval + MBPP) and four verifier feedback categories from H-M2, this experiment runs 3-iteration repair loops with GPT-4o-mini and measures per-iteration-1 repair success rate per category. The gate condition is a positive Spearman rank correlation (ρ > 0) between H-M2 empirical specificity ranks and observed iter1 repair success rates.

---

## 2. Problem Statement

H-M2 established that four feedback categories exhibit a measurable specificity gradient (Pyright ≫ Execution > Mypy ≫ Z3 by char_count). H-M3 asks: does higher-specificity feedback actually improve how efficiently an LLM repairs failing code? If specificity causes targeted edits, categories with higher information content should produce higher per-iteration-1 repair success rates, as the LLM can locate and fix the specific error rather than attempting broad edits.

---

## 3. Success Criteria

| Criterion | Target | Priority |
|-----------|--------|----------|
| Repair loop runs without error | All 538 × 4 = 2,152 repair sequences complete (or fail gracefully) | MUST |
| Gate metric computed | Spearman ρ between specificity ranks and iter1_rates | MUST |
| Gate passes | ρ > 0 (positive direction) | SHOULD_WORK |
| iter1 sample size | ≥ 100 initially-failing problems per well-sampled category (pyright, execution, mypy) | MUST |
| Z3 caveat documented | Z3 included in correlation with caveat: N≈8 (6.3% coverage) | MUST |
| Figures generated | All 5 required figures saved to figures/ | MUST |
| Result persistence | Per-problem repair records in results/h-m3/results.jsonl | MUST |

---

## 4. Data Specification

### 4.1 Primary Input — Reused from H-M1/H-M2

- **Source:** H-M1 initial solutions — `docs/youra_research/h-m1/code/results/h-m1/results.jsonl`
- **Problems:** 538 total (HumanEval 164 + MBPP 374)
- **Starting point for repair:** Initially-failing solutions (GPT-4o-mini pass@1 ~75-80%; expected ~100-200 failures)
- **Preprocessing:** Filter `records` where `passed == False`; use `solution` field as initial solution for repair
- **No new dataset download required** — uses H-M1 artifacts and H-M2 verifier infrastructure

### 4.2 Dataset Loading

```python
# Load H-M1 failing solutions (starting point for repair)
import json

records = [json.loads(l) for l in open("results/h-m1/results.jsonl")]
failing = [r for r in records if not r["passed"]]
# Expected: ~100-200 records

# Reference datasets (for problem metadata: prompt, test_cases)
from human_eval.data import read_problems
humaneval_problems = read_problems()  # 164 problems

from datasets import load_dataset
mbpp = load_dataset("mbpp", split="test")  # 374 problems
```

### 4.3 Dataset Statistics for H-M3

| Dataset | Problems | Initially Failing (expected) | Repair Sequences |
|---------|----------|------------------------------|-----------------|
| HumanEval | 164 | ~35-45 | ~35-45 × 4 = ~160 |
| MBPP | 374 | ~75-120 | ~75-120 × 4 = ~380 |
| **Total** | **538** | **~110-165** | **~440-660** |

**Z3 special case:** Only ~6.3% of problems will have Z3 feedback (N≈8 from H-M2); Z3 included with caveat.

---

## 5. Functional Requirements

### FR-1: Repair Loop Infrastructure

Implement `run_repair_loop()` that takes an initially-failing problem+solution and runs up to 3 repair iterations using a specified verifier:

```python
REPAIR_PROMPT_TEMPLATE = """
Problem: {problem_prompt}

Previous solution (FAILED):
```python
{previous_solution}
```

Feedback from {feedback_category} verifier:
{feedback_text}

Fix the solution. Return only the corrected code:
```python
"""

def run_repair_loop(
    problem: dict,          # {id, prompt, test_cases}
    initial_solution: str,  # From H-M1 (temp=0.2)
    verifier,               # One of 4 verifier classes from H-M2
    model: str = "gpt-4o-mini",
    max_iterations: int = 3,
    temperature: float = 0.0,
) -> dict:
    """Returns: {problem_id, category, iter1_pass, iter2_pass, iter3_pass, iterations_to_pass}"""
```

**Parameters (fixed across all categories):**
- Repair temperature: 0.0 (deterministic; from Olausson 2023, Shinn 2023)
- Max iterations: 3 (diminishing returns after 3; from Olausson 2023)
- Model: gpt-4o-mini (same as H-M1/H-M2)
- Prompt template: identical across all categories (only `{feedback_text}` varies)

### FR-2: Verifier Integration (Reuse H-M2 Infrastructure)

All 4 verifier classes from H-M2 are reused without modification. Each must expose `.get_feedback(solution: str, problem: dict) -> str`.

| Verifier | Category | H-M2 Specificity Rank | Expected N (failing) |
|----------|----------|----------------------|----------------------|
| PyrightVerifier | pyright | 1 (highest, 24,358 chars) | ~100-165 |
| ExecutionVerifier | execution | 2 (202 chars) | ~100-165 |
| MypyVerifier | mypy | 3 (49 chars) | ~100-165 |
| Z3Verifier | z3 | 4 (2 chars, 6.3% coverage) | ~8 |

**Import paths (from H-M2 actual code — verify against h-m2/code/):**
- Verifier classes: `from verifiers import ExecutionVerifier, PyrightVerifier, MypyVerifier, Z3Verifier`
- Evaluation: `from evaluator import evaluate_solution`

### FR-3: Controlled Experiment Design

- **Independent Variable:** Feedback category (4 levels: pyright, execution, mypy, z3)
- **Dependent Variable:** Per-iteration-1 repair success rate (`iter1_rate[cat]`)
- **Controls:** Same problem set, same model, same prompt template, same max_iterations
- **Measurement:** For each initially-failing problem, run repair loop once per verifier category
- **Formula:** `iter1_rate[cat] = count(iter1_pass == True) / count(initially_failing)`

### FR-4: Statistical Analysis

**Primary gate metric:**

```python
from scipy.stats import spearmanr

specificity_ranks = [1, 2, 3, 4]   # From H-M2: pyright, execution, mypy, z3
iter1_rates = [rate_pyright, rate_execution, rate_mypy, rate_z3]
rho, pval = spearmanr(specificity_ranks, iter1_rates)
# Gate: rho > 0
```

**Secondary metrics:**
- Mean iterations to first pass per category: `mean(iterations_to_pass)` among eventually-passing problems
- Negative correlation of mean_iterations with specificity rank (secondary gate)
- Bootstrap 95% CI on iter1_rate per category (N_bootstrap=1000)

**Note on statistical power:** With n=4 categories, Spearman has no power for significance testing (critical ρ=1.0 at α=0.05). The gate is directional (ρ > 0), not significance-based. Within-category estimates are precise (N≥100 per category for well-sampled verifiers).

### FR-5: Ablation / Sensitivity Analysis

| Ablation | Description | Why |
|----------|-------------|-----|
| Without Z3 | Recompute Spearman over 3 categories only | Z3 N≈8 may distort correlation |
| Iteration-2 correlation | Repeat Spearman for iter2_rate | Check if specificity advantage persists |
| By dataset | Separate analysis for HumanEval vs MBPP | Dataset-specific effects |
| Bug-type subgroup | Stratify by H-M1 bug_type | Link repair difficulty to error category |

### FR-6: Visualization

| Figure | Type | Path | Required |
|--------|------|------|----------|
| iter1_rate per category (gate metric) | Bar chart + 95% CI | figures/bar_iter1_rate.png | MANDATORY |
| Cumulative repair rate across iterations 1-3 | Line chart (4 lines) | figures/line_cumulative_repair.png | MANDATORY |
| Mean iterations heatmap: bug_type × category | Heatmap | figures/heatmap_mean_iterations.png | MANDATORY |
| Feedback length vs repair rate | Scatter + regression | figures/scatter_length_vs_rate.png | MANDATORY |
| Z3 subgroup analysis (N≈8) | Scatter with annotation | figures/scatter_z3_subgroup.png | SUPPLEMENTARY |

> All figures saved to `docs/youra_research/h-m3/figures/` (create directory if needed).

### FR-7: Mechanism Verification Check

Before full run, verify repair loop fires correctly:

```python
def verify_mechanism(problems_sample, verifiers):
    for cat, verifier in verifiers.items():
        result = run_repair_loop(
            problem=problems_sample[0],
            initial_solution="def solution(): pass  # intentionally wrong",
            verifier=verifier,
            max_iterations=1
        )
        assert result["iter1_pass"] in [True, False]
        print(f"✓ {cat}: iter1_pass={result['iter1_pass']}")
```

### FR-8: Result Persistence

- **Per-problem records:** `results/h-m3/results.jsonl` — one record per (problem_id, category, iteration)
- **Summary stats:** `results/h-m3/summary.json` — iter1_rates, Spearman ρ, gate result
- **Schema:**
```json
{
  "problem_id": "HumanEval/0",
  "category": "pyright",
  "iter1_pass": true,
  "iter2_pass": null,
  "iter3_pass": null,
  "iterations_to_pass": 1,
  "feedback_length": 24358
}
```

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Timeout | Inherit H-M2 timeouts: Pyright 10s, execution 5s, mypy 10s, Z3 30s |
| Parallelism | 4 workers (problem-level); verifiers run sequentially per problem for controlled measurement |
| Determinism | temperature=0.0 for repair = deterministic; no seeds needed |
| Cost | ~$0.50-2.00 (est. 2,152 repair calls × avg 500 tokens × $0.60/1M = ~$0.65) |
| Reproducibility | All repair calls logged to results.jsonl; H-M1 initial solutions fixed |

---

## 7. Dependencies

### 7.1 Python Packages

```
# Inherited from H-M2 (no new installs needed):
pyright>=1.1.0         # static analysis verifier
mypy>=1.0.0            # type checking verifier
z3-solver>=4.12.0      # SMT verifier
scipy>=1.11.0          # spearmanr
matplotlib>=3.7.0      # visualization
seaborn>=0.12.0        # heatmap
pandas>=2.0.0          # data manipulation
openai>=1.0.0          # GPT-4o-mini repair calls
datasets>=2.14.0       # MBPP loading

# New for H-M3:
human-eval             # HumanEval evaluation harness (openai/human-eval)
```

### 7.2 External Repositories

- HumanEval harness: `pip install human-eval` (openai/human-eval) — `evaluate_functional_correctness()`
- MBPP: via HuggingFace `datasets` (already in H-M2)

### 7.3 Base Hypothesis Dependencies

| Artifact | Source | Usage |
|----------|--------|-------|
| H-M1 results | `h-m1/code/results/h-m1/results.jsonl` | Initial failing solutions (repair starting point) |
| H-M2 verifier classes | `h-m2/code/verifiers.py` | PyrightVerifier, ExecutionVerifier, MypyVerifier, Z3Verifier |
| H-M2 specificity ranks | H-M2 04_validation.md | Pyright=1, Execution=2, Mypy=3, Z3=4 |
| H-M2 evaluator | `h-m2/code/evaluator.py` | `evaluate_solution()` |

---

## 8. Out of Scope

- No new code generation (uses H-M1 initial solutions)
- No model training or fine-tuning
- No modification to H-M2 verifier classes
- Multi-turn repair beyond 3 iterations
- Repair with hybrid/combined feedback (single category per run only)
- Human evaluation of repair quality
