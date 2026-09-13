# Experiment Design: H-E1

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under GPT-4o-mini generation on HumanEval+ and MBPP+ (temperature=0.8, single shot), a non-trivial fraction (≥10%) of failing solutions will have mypy-detectable type errors, because type mismatches are a common failure mode in LLM-generated Python code.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** — Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE (PoC — observational)
- **Prerequisites:** None

### Gate Condition

MUST_WORK: If this hypothesis fails (type error rate < 5%), all downstream mechanism hypotheses (H-M1, H-M2, H-M3, H-Z1) become moot. The pipeline stops.

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous hypothesis results to inherit.

### Previous Hypothesis Results (if applicable)

None — H-E1 is the root hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> ⚠️ **MCP Limitation:** Archon MCP was not available in this session. The following is synthesized from Phase 2B research context, which cites EvalPlus (Liu et al. 2023) and established type-error analysis literature.

**Key insights from Phase 2B literature:**

**Finding 1: Type Error Prevalence in LLM Code**
- EvalPlus (Liu et al. 2023) reports that augmented test suites reveal higher failure rates than HumanEval alone — many solutions pass original tests but fail augmented ones due to edge cases including type mismatches.
- Dataset: HumanEval+ (164 problems), MBPP+ (378 problems)
- Typical pass@1 for GPT-4o-mini on HumanEval+: ~55-65% (estimated from similar model benchmarks)
- Implication: ~35-45% of solutions fail, giving a sizable pool to analyze for type errors.

**Finding 2: mypy Permissive Mode Best Practices**
- Standard flags: `--ignore-missing-imports --no-strict-optional`
- These flags reduce false positives from missing stubs and optional chaining
- Permissive mode catches genuine type mismatches while tolerating incomplete type annotations
- Source: mypy documentation + standard practice in academic code analysis

**Finding 3: Static Analysis on Generated Code**
- Multiple studies (e.g., Ni et al. 2023 "L2CEval") analyze LLM code quality dimensions
- Type errors are a well-documented failure mode in Python LLM outputs, especially for function signatures and return types
- Expected base rate: 15-30% of failing solutions have at least one mypy error (from general Python type error literature)

### Archon Code Examples

> ⚠️ **MCP Limitation:** Code examples from Archon KB not available. Synthesized from known evalplus API patterns.

**Pattern 1: EvalPlus Dataset Loading**
```python
# Standard evalplus loading pattern
from evalplus.data import get_human_eval_plus, get_mbpp_plus

humaneval_problems = get_human_eval_plus()  # dict: task_id -> problem
mbpp_problems = get_mbpp_plus()             # dict: task_id -> problem
```

**Pattern 2: mypy Subprocess Call**
```python
import subprocess
import tempfile
import os

def run_mypy(code: str) -> tuple[bool, str]:
    """Run mypy on code string, return (has_errors, error_output)."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        result = subprocess.run(
            ["mypy", "--ignore-missing-imports", "--no-strict-optional", fname],
            capture_output=True, text=True, timeout=30
        )
        has_errors = result.returncode != 0
        return has_errors, result.stdout + result.stderr
    finally:
        os.unlink(fname)
```

### Exa GitHub Implementations

> ⚠️ **MCP Limitation:** Exa MCP was not available in this session. Key repositories identified from Phase 2B context and known literature.

**Repository 1: evalplus/evalplus** (Primary — Official)
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Official EvalPlus benchmark implementation — ground truth for dataset loading and test execution
- **Architecture:** Python package with `evalplus.data` for dataset loading, `evalplus.evaluate` for test execution
- **Key Code Pattern:**
  ```python
  # Install: pip install evalplus
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  from evalplus.evaluate import evaluate_functional_correctness
  ```
- **Training Config:** N/A (evaluation framework, not training)
- **Dataset:** HumanEval+ (164 problems), MBPP+ (378 problems)
- **Results:** Defines the benchmark — provides augmented test cases

**Repository 2: openai/openai-python** (API client)
- **URL:** https://github.com/openai/openai-python
- **Relevance:** GPT-4o-mini generation via OpenAI API
- **Key Code Pattern:**
  ```python
  from openai import OpenAI
  client = OpenAI()
  response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.8,
      n=1
  )
  code = response.choices[0].message.content
  ```
- **Dataset:** N/A

**Serena Analysis Needed:** False — no complex custom neural architecture; this is API+subprocess tooling with clear implementations.

### 🎯 Implementation Priority Assessment

This is not a paper reproduction experiment. The implementation combines:
1. evalplus (official, use directly)
2. OpenAI API (official client)
3. mypy (standard tool)

**Recommended Implementation Path:**
- Primary: evalplus official API + OpenAI Python SDK + mypy CLI subprocess
- Fallback: datasets library (HuggingFace) for MBPP+ if evalplus API changes
- Justification: All three are official, stable, well-documented implementations. No custom mechanism to reproduce.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No complex custom architecture requiring semantic analysis. The experiment uses standard tools (evalplus, openai SDK, mypy) with straightforward subprocess invocation.

---

## Experiment Specification

### Dataset

**Dataset 1 (Primary): MBPP+**

| Field | Value |
|-------|-------|
| Name | MBPP+ (Mostly Basic Python Problems, EvalPlus augmented) |
| Version | evalplus latest |
| Type | standard (programmatic-api) |
| Source | evalplus package: `get_mbpp_plus()` |
| Problems | 378 programming problems |
| Splits | All problems used (no train/test split — benchmark evaluation) |
| Path | `auto` (loaded via evalplus API, no local file needed) |

**Dataset 2 (Secondary): HumanEval+**

| Field | Value |
|-------|-------|
| Name | HumanEval+ (OpenAI HumanEval, EvalPlus augmented) |
| Version | evalplus latest |
| Type | standard (programmatic-api) |
| Source | evalplus package: `get_human_eval_plus()` |
| Problems | 164 programming problems |
| Splits | All problems used |
| Path | `auto` (loaded via evalplus API) |

**Total evaluation scope:**
- 542 problems × 3 seeds = 1,626 generation calls
- Expected ~35-45% failure rate → ~570-730 failing solutions for mypy analysis

**Preprocessing:** None — problems are Python function stubs with docstrings, used as-is for prompting.
**Augmentation:** None — EvalPlus augmentation is in the test suite, not the input problems.

**Loading Information** (for Phase 4 download):
- Method: evalplus Python package
- Identifier: `evalplus` (pip install evalplus)
- Code: `from evalplus.data import get_human_eval_plus, get_mbpp_plus`

### Models

#### Baseline Model

**Architecture:** GPT-4o-mini (OpenAI API)
**Type:** API-based LLM — no local weights, no training
**Role in experiment:** Code generator (single-shot, temperature=0.8)

**Configuration:**
- Model ID: `gpt-4o-mini`
- Temperature: 0.8 (single-shot generation)
- Max tokens: 1024 (sufficient for function implementations)
- n: 1 per call (no sampling ensemble)
- Seeds: 3 (controlled by varying prompt seed suffix or API seed parameter)

**Loading Information** (for Phase 4 download):
- Method: OpenAI Python SDK
- Identifier: `openai` (pip install openai)
- Code: `from openai import OpenAI; client = OpenAI()`

#### Proposed Model

**Architecture:** GPT-4o-mini + mypy analysis pipeline

This is NOT a neural architecture modification. The "proposed model" is the measurement pipeline:

**Core Mechanism Implementation:**

```python
# Core Mechanism: mypy Type Error Prevalence Measurement
# Based on: mypy CLI + evalplus evaluation framework
# H-E1: Observational study — no model modification

import subprocess, tempfile, os
from openai import OpenAI
from evalplus.data import get_human_eval_plus, get_mbpp_plus

def generate_solution(client: OpenAI, problem: dict, seed: int) -> str:
    """Generate single solution via GPT-4o-mini."""
    prompt = build_prompt(problem)  # standard: problem description + function stub
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        seed=seed,
        max_tokens=1024,
    )
    return extract_code(response.choices[0].message.content)

def run_mypy(code: str) -> tuple[bool, int]:
    """Return (has_type_error, error_count)."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code); fname = f.name
    try:
        r = subprocess.run(
            ["mypy", "--ignore-missing-imports", "--no-strict-optional", fname],
            capture_output=True, text=True, timeout=30
        )
        errors = [l for l in r.stdout.splitlines() if "error:" in l]
        return r.returncode != 0, len(errors)
    finally:
        os.unlink(fname)

def run_experiment(problems: dict, client: OpenAI, seeds: list[int]) -> dict:
    """H-E1: Measure type error fraction among failing solutions."""
    results = []
    for seed in seeds:
        for task_id, problem in problems.items():
            code = generate_solution(client, problem, seed)
            passed = evaluate_solution(task_id, code, problem)  # EvalPlus eval
            if not passed:
                has_error, error_count = run_mypy(code)
                results.append({"task_id": task_id, "seed": seed,
                                 "has_mypy_error": has_error, "error_count": error_count})
    return aggregate_results(results)  # fraction with ≥1 error, mean ± std
```

### Training Protocol

This is an **observational experiment** — no model training occurs. The "protocol" is the data collection procedure.

**Generation Protocol:**
- Model: GPT-4o-mini (`gpt-4o-mini`)
- Temperature: 0.8 (single-shot, not deterministic)
- Seeds: 3 (seed=42, seed=123, seed=456 — via OpenAI `seed` parameter)
- Attempts per problem per seed: 1 (single-shot, no repair)
- Prompt format: Standard Python function completion (problem description + function stub)

**mypy Analysis Protocol:**
- Command: `mypy --ignore-missing-imports --no-strict-optional {solution_file}`
- Scope: Applied to ALL failing solutions (failed EvalPlus test suite)
- Timeout: 30 seconds per file
- Error counting: Lines containing `"error:"` in mypy stdout

**Evaluation Order:**
1. Generate solution (GPT-4o-mini)
2. Run EvalPlus test suite → mark pass/fail
3. If fail → run mypy → record error presence and count
4. Aggregate per benchmark per seed

**Compute Estimate:**
- ~542 problems × 3 seeds = 1,626 API calls
- ~600-750 failing solutions → mypy runs
- Estimated wall time: 30-60 minutes
- Estimated API cost: ~$2-5 at GPT-4o-mini pricing

**Seeds:** 3 (seed=42, seed=123, seed=456)

### Evaluation

**Task Type:** Observational measurement (no trained model to evaluate)

**Primary Metric:**
- `type_error_fraction_mbpp`: Fraction of failing MBPP+ solutions with ≥1 mypy error
  - Formula: `count(failing AND has_mypy_error) / count(failing)` per seed, then mean ± std across 3 seeds

**Secondary Metric:**
- `type_error_fraction_humaneval`: Same metric for HumanEval+

**Reporting:**
- Mean ± std across 3 seeds for each benchmark
- Breakdown by error type if feasible (name-error, type-error, attribute-error)

**Success Criteria:**
- **PASS:** `type_error_fraction_mbpp ≥ 0.10` (≥10% of failing solutions have ≥1 mypy error)
- **PASS (secondary):** `type_error_fraction_humaneval ≥ 0.10`
- **BORDERLINE:** 5-10% — continue with reduced expectations
- **FAIL:** < 5% — pivot, mypy signal too sparse for repair loop benefit

**Expected Baseline Performance (from Phase 2B literature):**
- pass@1 (GPT-4o-mini, HumanEval+): ~55-65% estimated
- pass@1 (GPT-4o-mini, MBPP+): ~50-60% estimated
- Expected type error fraction among failures: 15-30% (literature prior, A1 assumption)
- Source: EvalPlus paper (Liu et al. 2023), general Python type error analysis

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: classification (pass/fail + type error presence)
- Library: Python stdlib (no special metrics library needed)
- Code: `fraction = sum(r['has_mypy_error'] for r in failing_results) / len(failing_results)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing type_error_fraction vs 10% threshold for MBPP+ and HumanEval+, with error bars (std across 3 seeds)

#### Additional Figures (LLM Autonomous)

The Phase 4 coder should autonomously determine additional informative figures. Suggestions:

1. **Error Type Distribution**: Pie/bar chart of mypy error categories (name-error, type-error, attribute-error, return-value) among flagged solutions
2. **Error Count Distribution**: Histogram of mypy error counts per failing solution (to understand severity distribution)
3. **Per-benchmark Comparison**: Side-by-side bars for MBPP+ vs HumanEval+ type error fractions
4. **Seed Consistency**: Box plot of type_error_fraction across 3 seeds (to show measurement stability)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (generation + mypy pipeline completes for all problems)
2. `type_error_fraction_mbpp ≥ 0.10` (≥10% of failing MBPP+ solutions have mypy errors)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | mypy CLI installed and callable via subprocess | TRUE — verify with `mypy --version` |
| Mechanism Isolatable | mypy can be toggled: run on failing solutions only | TRUE — conditional on EvalPlus pass/fail result |
| Baseline Measurable | EvalPlus pass@1 without mypy is measurable independently | TRUE — EvalPlus evaluation is independent of mypy |

### Architecture Compatibility Check

This experiment uses CLI tools, not neural architectures. Compatibility requirements:

**Required:**
- Python 3.9+ environment
- `mypy` installed (`pip install mypy`)
- `evalplus` installed (`pip install evalplus`)
- `openai` Python SDK installed (`pip install openai`)
- `OPENAI_API_KEY` environment variable set
- Network access to OpenAI API

**Incompatible scenarios:**
- Firewall blocking OpenAI API → generation fails
- mypy version < 0.9 → may have different output format → adjust error parsing

> ⚠️ If mypy is not installed, Phase 4 MUST fail early with clear error message.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"mypy analysis: {N} errors in {task_id}"` | run_mypy() function |
| Output Field | `has_mypy_error: True/False` per failing solution | results dict |
| Metric Delta | type_error_fraction > 0 (any errors found at all) | aggregate_results() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results: list[dict]) -> tuple[bool, dict]:
    """Verify mypy analysis pipeline actually ran and found errors."""
    analyzed = [r for r in results if 'has_mypy_error' in r]
    any_errors_found = any(r['has_mypy_error'] for r in analyzed)
    indicators = {
        "mypy_ran": len(analyzed) > 0,
        "errors_found": any_errors_found,
        "fraction_computed": len(analyzed) > 0,
        "sample_size_sufficient": len(analyzed) >= 50,  # min for meaningful fraction
    }
    activated = indicators["mypy_ran"] and indicators["errors_found"]
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| mypy not installed | `subprocess.FileNotFoundError` | FAIL early: print install instructions |
| mypy timeout | `subprocess.TimeoutExpired` | Log and skip; count as "no error" (conservative) |
| EvalPlus unavailable | `ImportError` | FAIL: install evalplus |
| OpenAI API error | `openai.APIError` | Retry with backoff; log; skip if persistent |
| Zero failing solutions | `len(failing_results) == 0` | FAIL: check EvalPlus setup |
| mypy output format changed | No `"error:"` in output | WARN: check mypy version |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (mypy ran + errors found) | `verify_mechanism_activated()` returns True |
| Effect Measurable | type_error_fraction > 0 | fraction computed from ≥50 failing solutions |
| Hypothesis Supported | type_error_fraction_mbpp ≥ 0.10 | Primary metric on MBPP+ |

---

## Appendix: Reference Implementations

### A. Phase 2B Literature Sources (used in lieu of Archon KB)

**Source 1:** EvalPlus (Liu et al. 2023)
- **Type:** Benchmark paper
- **Relevance:** Defines HumanEval+ and MBPP+ datasets used in this experiment
- **Key Insights:**
  - Augmented test suites reveal higher failure rates than original HumanEval/MBPP
  - Error analysis shows multiple failure categories including type errors
- **Used For:** Dataset selection, expected pass@1 estimates

**Source 2:** Self-Debug (Chen et al. 2023)
- **Type:** Repair loop paper
- **Relevance:** Establishes execution-only repair as baseline (~65-70% pass@1 with k=3)
- **Key Insights:**
  - Most repair benefit within k=3 rounds (A4 assumption)
  - Execution feedback alone is effective but limited by binary signal
- **Used For:** Baseline performance estimates, experimental motivation

**Source 3:** Reflexion (Shinn et al. 2023)
- **Type:** Verbal feedback repair paper
- **Relevance:** Shows verbal feedback improves repair (~67% pass@1 with k=3 on HumanEval)
- **Used For:** Baseline performance comparison context

### B. GitHub Implementations (from Phase 2B context)

**Repository 1:** evalplus/evalplus
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Official dataset and evaluation framework — must use for reproducibility
- **Key Pattern:**
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  problems = get_mbpp_plus()  # dict[str, dict] with 378 problems
  ```
- **Used For:** Dataset loading, test suite execution

**Repository 2:** openai/openai-python
- **URL:** https://github.com/openai/openai-python
- **Relevance:** Official OpenAI Python client for GPT-4o-mini generation
- **Key Pattern:**
  ```python
  client = OpenAI()
  response = client.chat.completions.create(model="gpt-4o-mini", ...)
  ```
- **Used For:** Code generation

### C. Code Analysis (Serena)

Serena analysis not performed — code toolchain (evalplus, openai SDK, mypy) is well-documented with clear APIs. No custom neural layers or complex architectures requiring semantic analysis.

### D. Previous Hypothesis Context

None — H-E1 is the first hypothesis. No inherited hyperparameters or configurations.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MBPP+, HumanEval+) | Phase 2B / EvalPlus paper | Section 1.3 + Source A.1 |
| Generation model (GPT-4o-mini) | Phase 2B | Section 1.3 |
| Temperature=0.8 | Phase 2B | Section 2.2 (controlled variable) |
| Seeds (3 × {42,123,456}) | Phase 2B | Section 2.2 |
| mypy flags (permissive) | Phase 2B / mypy docs | Section 1.5 Assumption A3 |
| Success threshold (≥10%) | Phase 2B | Section 2.2 Success Criteria |
| Failure threshold (<5%) | Phase 2B | Section 2.2 Failure Response |
| Expected base rate (15-30%) | Literature (A1 assumption) | Section 1.5 |
| Baseline pass@1 estimates | Self-Debug, Reflexion papers | Sources B.1, A.2, A.3 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-26

### Workflow History for This Hypothesis

| Event | Timestamp | Phase |
|-------|-----------|-------|
| H-E1 set to IN_PROGRESS | 2026-08-26T06:27:36Z | Hypothesis Loop |
| Phase 2C started | 2026-08-26 | Phase 2C |
| experiment_design.status = COMPLETED | 2026-08-26 | Phase 2C |

---

*MCP Tools Used: None available (Archon, Exa not connected) — synthesized from Phase 2B context*
*All specifications grounded in Phase 2B verification plan and established literature*
*Next Phase: Phase 3 - Implementation Planning*
