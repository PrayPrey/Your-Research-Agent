# PRD: H-M2 Feedback Specificity Gradient Measurement

**Hypothesis:** H-M2
**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Type:** MECHANISM — measurement study (no training)

---

## 1. Goal

Measure whether four formal feedback categories (execution monitoring, static analysis/Pyright, type checking/mypy, SMT/Z3) exhibit a measurable specificity gradient when applied independently to the same set of failing LLM-generated code solutions from H-M1. Operationalize specificity as (a) character count of feedback string and (b) structured field count of feedback output. Confirm the ordering: SMT ≥ static analysis / type checking > execution monitoring.

---

## 2. Success Criteria

| Criterion | Target | Priority |
|-----------|--------|----------|
| Verifier activation | All 4 verifiers produce non-zero output on ≥10% of failing solutions | MUST |
| Ordering direction | Mean char_count: SMT ≥ {static, type} > execution | MUST |
| Statistical significance | Kruskal-Wallis p < 0.05 on char_count across 4 groups | SHOULD |
| Pairwise difference | >20% mean char_count difference between adjacent categories | SHOULD |
| Code runs clean | No crash on full 538-problem corpus | MUST |
| Z3 fallback | If Z3 timeout >80% → reduce to 3-category; document limitation | SHOULD |

---

## 3. Dataset

### 3.1 Primary Input

- **Source:** H-M1 failing solutions — `docs/youra_research/h-m1/code/results/h-m1/results.jsonl`
- **Problems:** 538 total (HumanEval 164 + MBPP 374)
- **Experimental subset:** Failing solutions only (~100-200 at GPT-4o-mini ~75-80% pass@1)
- **Preprocessing:** None — raw Python code strings; each solution written to temp `.py` file for subprocess invocation
- **No new generation:** H-M2 reuses H-M1 outputs directly

### 3.2 Dataset Loading

```python
# Primary: load H-M1 results
import json
records = [json.loads(l) for l in open("results/h-m1/results.jsonl")]
failing = [r for r in records if not r["passed"]]

# Reference datasets (for problem metadata if needed)
from datasets import load_dataset
humaneval = load_dataset("openai/openai_humaneval")
mbpp = load_dataset("google-research-datasets/mbpp", "sanitized")
```

---

## 4. Functional Requirements

### FR-1: Feedback Measurement Pipeline

Apply 4 verifiers independently to each failing solution and record (char_count, field_count):

| Verifier | Category | Tool | Output |
|----------|----------|------|--------|
| Execution monitoring | baseline | Python subprocess (stderr capture) | char_count=len(stderr), field_count=1 |
| Static analysis | formal-1 | Pyright v1.1+ `--outputjson` | char_count=len(JSON stdout), field_count=sum(len(e) for e in generalDiagnostics) |
| Type checking | formal-2 | mypy v1.0+ `--no-error-summary` | char_count=len(stdout), field_count=count(lines with ": error:") |
| SMT solving | formal-3 | Z3 Python API (z3-solver 4.12+) | char_count=len(str(model)), field_count=len(model) if sat else 0 |

### FR-2: Z3 Constraint Extraction

Extract Z3-compatible constraints from problem docstring using GPT-4o-mini prompt. Apply to failing code solution. Measure counterexample (if sat) or record 0 (if unsat/timeout).

### FR-3: Statistical Analysis

- Primary test: `scipy.stats.kruskal(exec_chars, static_chars, type_chars, smt_chars)`
- Post-hoc: Dunn's test with Bonferroni correction (`scikit_posthocs.posthoc_dunn`)
- Effect size: ε² = H / (n-1)
- Report: mean, median, std, p-value, ε² per verifier category

### FR-4: Mechanism Verification

Sanity check: each verifier must produce non-zero char_count on ≥1 sample failing solution before full run.

### FR-5: Visualization

| Figure | Type | Output Path |
|--------|------|-------------|
| Mean char_count per verifier (gate metric) | Bar chart with 95% CI | figures/bar_mean_char_count.png |
| char_count distribution per verifier | Box plot | figures/box_char_count.png |
| char_count vs bug_type cross-tabulation | Heatmap | figures/heatmap_char_bug_type.png |
| CDF of char_count per verifier | CDF plot | figures/cdf_char_count.png |
| char_count vs field_count per verifier | Scatter plot | figures/scatter_char_field.png |

### FR-6: Result Persistence

Save per-problem measurement records to `results/h-m2/results.jsonl` and summary statistics to `results/h-m2/summary.json`.

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Timeout | 10 seconds per verifier call (prevent Z3/subprocess hang) |
| Parallelism | 4 workers for problem-level parallelism; verifiers sequential per problem |
| Reproducibility | Deterministic (no sampling in H-M2 itself; seeds N/A) |
| Cost | ~$0.02 additional (Z3 constraint extraction LLM calls only) |

---

## 6. Outputs

| Artifact | Path | Description |
|----------|------|-------------|
| Per-problem records | `results/h-m2/results.jsonl` | {task_id, verifier, char_count, field_count, timeout} per (problem, verifier) |
| Summary statistics | `results/h-m2/summary.json` | Mean/median/std per verifier; KW test result; ordering confirmed flag |
| Figures | `figures/` | 5 required figures (see FR-5) |

---

## 7. Dependencies

### 7.1 Python Packages

```
pyright>=1.1.0          # static analysis (via npm or pip install pyright)
mypy>=1.0.0             # type checking
z3-solver>=4.12.0       # SMT solving
scipy>=1.11.0           # kruskal, mannwhitneyu
scikit-posthocs>=0.7.0  # Dunn's post-hoc test
matplotlib>=3.7.0       # visualization
seaborn>=0.12.0         # heatmap, box plots
pandas>=2.0.0           # data manipulation
openai>=1.0.0           # Z3 constraint extraction
datasets>=2.14.0        # HuggingFace (reference data)
```

### 7.2 External Repositories / Reference Implementations

- Pyright: https://github.com/microsoft/pyright (invoked via subprocess `--outputjson`)
- mypy: https://mypy.readthedocs.io (invoked via subprocess)
- Z3: https://github.com/Z3Prover/z3 (Python API)

### 7.3 Base Hypothesis Dependency

- H-M1 results: `docs/youra_research/h-m1/code/results/h-m1/results.jsonl` (failing solutions)
- H-M1 infrastructure reused: execution harness, OpenAI client setup

---

## 8. Out of Scope

- No new GPT-4o-mini code generation (H-M2 reuses H-M1 failing solutions)
- No repair loop (single-pass measurement only)
- No model training or fine-tuning
- LLM-based repair using these feedbacks (that is H-M3/M4)
