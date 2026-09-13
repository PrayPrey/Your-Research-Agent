# Experiment Design: H-M3

**Date:** 2026-08-03
**Author:** Anonymous
**Hypothesis Statement:** Under ContractEval's 364 tasks, if Hypothesis PBT with icontract-hypothesis (5k adaptive examples) is compared to static EvalPlus oracle (764 fixed inputs) on the same LLM programs, then the adaptive PBT contract-failure rate exceeds the static oracle contract-failure rate by > 0 absolute (mean adaptive gap > oracle-isolation gap), because Hypothesis's adaptive input generation guided by pre-conditions explores input regions not covered by any fixed test set.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests "does adaptive search contribute beyond static oracle?"

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 VALIDATED (MUST_WORK gate satisfied; oracle-isolation gap = 0.4012)
**Gate Status:** MUST_WORK — gate not yet evaluated (will require mean adaptive contribution > 0, Wilcoxon p < 0.05)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (VALIDATED), H-E1 (VALIDATED)

### Gate Condition

**MUST_WORK gate:** Mean adaptive contribution > 0 (Wilcoxon signed-rank p < 0.05 after Holm correction). Secondary: adaptive contribution > 0.03 absolute for ≥50% of tasks.

**Failure Response:** PIVOT to oracle-strength interpretation — "contract semantics, not adaptive search, drives the gap." Still valid contribution via H-M1.

---

## Continuation Context

**This is a continuation experiment** building on H-M1 (Experiment A — static oracle isolation).

### Previous Hypothesis Results (H-M1)
- Oracle isolation gap = 0.4012 (threshold ≥ 0.10); 4× above gate threshold
- Mean contract-unique mass = 0.4023 (40% of EvalPlus CVT inputs: LLM matches gt_plain but contract rejects)
- Wilcoxon signed-rank p = 5.88e-38 after Holm correction
- Task coverage: 364/364 (100%); 0 quarantined; 10,432 (model, task, program) triples evaluated
- Consistent across models (gap 0.40–0.41) and both task types (HumanEval+ 0.52, MBPP+ 0.35)

**H-M3 Design Principle:** Reuse H-M1 Experiment A (static oracle) results directly. Add Experiment B (adaptive PBT) and compute per-triple difference. IV changes only: input generation strategy. Oracle (ContractEval contracts), programs, and models are identical between A and B.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "property-based testing adaptive input generation contract oracle experiment design"**
- No domain-relevant results (similarity scores 0.31–0.39; results from diffusion/image model domain)
- Archon KB does not contain PBT/code-evaluation literature

**Query 2: "hypothesis testing icontract-hypothesis Python code generation LLM evaluation benchmark"**
- No domain-relevant results (similarity 0.37–0.42; CV/image generation domain)

**Query 3: "static oracle vs adaptive testing code correctness evaluation comparison"**
- No domain-relevant results (similarity 0.31–0.36; image diffusion domain)

**Query 4 (Code): "hypothesis property-based testing icontract Python code evaluation"**
- No matching implementation examples

**Assessment:** Archon KB is populated with CV/image-gen literature and does not cover PBT or LLM code-evaluation research. Primary implementation guidance sourced from Exa GitHub.

### Archon Code Examples

No domain-relevant code examples found in Archon KB.

### Exa GitHub Implementations

**Query 1: "icontract-hypothesis hypothesis property-based testing Python contract verification LLM code generation"**

**Repository 1**: mristin/icontract-hypothesis (⭐ 90)
- **URL**: https://github.com/mristin/icontract-hypothesis
- **Relevance**: Primary tool for Experiment B — infers Hypothesis strategies from icontract preconditions, enabling adaptive PBT guided by contract pre-conditions
- **Key Interface**:
  ```python
  # Strategy inference from pre-conditions (icontract decorators)
  import icontract_hypothesis
  from hypothesis import given, settings

  # Approach 1: Explicit strategy inference
  strategy = icontract_hypothesis.infer_strategy(func_with_contracts)

  @given(strategy)
  def test_func(args):
      func_with_contracts(args)

  # Approach 2: Automatic testing via CLI
  # pyicontract-hypothesis test --path module.py
  ```
- **Key Configuration** (relevant to 5k budget):
  - `@settings(max_examples=5000)` controls adaptive example budget
  - Seed: `@settings(max_examples=5000, deriving_seed=42)` for reproducibility
  - FilteredStrategy handles pre-condition filtering automatically
- **Pre-condition Pattern Matching**: Matches integer bounds (`5 < x < 10` → `st.integers(min=6, max=9)`), float bounds, regex patterns for strings
- **Yield Concern**: Tasks with complex pre-conditions may have high filter rates → per-task yield must be logged
- **Source**: https://github.com/mristin/icontract-hypothesis (MIT license)

**Repository 2**: HypothesisWorks/hypothesis (⭐ 8788)
- **URL**: https://github.com/hypothesisworks/hypothesis
- **Relevance**: Core PBT engine; adaptive shrinking and example generation that icontract-hypothesis builds on
- **Key Settings for Experiment B**:
  ```python
  from hypothesis import settings, HealthCheck
  settings.register_profile("experiment_b",
      max_examples=5000,
      suppress_health_check=[HealthCheck.too_slow],
      deadline=None  # No per-example deadline
  )
  settings.load_profile("experiment_b")
  ```
- **Reproducibility**: `hypothesis.seed(42)` or `@settings(database=None, deriving_seed=42)` for fixed runs
- **Source**: https://github.com/hypothesisworks/hypothesis (custom license)

**Query 2: "evalplus EvalPlus benchmark LLM code generation evaluation ContractEval HumanEval MBPP"**

**Repository 3**: evalplus/evalplus (⭐ 1789, NeurIPS 2023)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: Source of Experiment A static inputs (764 tests/task) reused from H-M1; also code generation pipeline for multi-model sampling
- **Loading Interface**:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus, write_jsonl
  # Returns dict: task_id -> {prompt, contract, plus_input, base_input, ...}
  humaneval_tasks = get_human_eval_plus()
  mbpp_tasks = get_mbpp_plus()
  ```
- **Code Generation** (n=10 samples per model per task):
  ```bash
  evalplus.codegen --model "gpt-4o-mini" \
                   --dataset humaneval \
                   --backend openai \
                   --n 10 \
                   --root ./results/
  ```
- **Supported backends**: openai (OPENAI_API_KEY), anthropic (ANTHROPIC_API_KEY), vllm, hf
- **Source**: https://github.com/evalplus/evalplus (Apache-2.0)

**Query 3: "ContractEval suhanmen contract evaluation LLM code postcondition precondition Python GitHub ACL 2026"**

**Repository 4**: suhanmen/ContractEval (⭐ 5, ACL 2026 Findings)
- **URL**: https://github.com/suhanmen/ContractEval
- **Relevance**: Source of 364 tasks with icontract pre/post-condition contracts; provides reference implementations for oracle soundness check
- **Task Format**: Each task has (i) original prompt + functional tests, (ii) contract-aware reconstructed prompt, (iii) CVTs from SMT pipeline, (iv) reference code with contracts
- **Key Finding from Paper**: Standard prompting yields 0% contract satisfaction (CSR=0) under SMT-based evaluation; 23–41% with contract-aware prompting
- **Integration**: Tasks are strict subset of HumanEval+/MBPP+ → EvalPlus inputs map cleanly via task_id
- **Source**: https://github.com/suhanmen/ContractEval (MIT license)
- **Paper**: Lim et al., ACL 2026 Findings, https://aclanthology.org/2026.findings-acl.2112/

**Serena Analysis Needed:** false — library APIs are well-documented; no complex custom architecture requiring semantic analysis.

### 🎯 Implementation Priority Assessment

**CRITICAL: For this experiment, icontract-hypothesis is the core adaptive search tool and is the ground-truth implementation.**

**Recommended Implementation Path:**
- Primary: mristin/icontract-hypothesis (official, 90 stars) — strategy inference from ContractEval icontract decorators
- Fallback: Manual Hypothesis strategy with explicit pre-condition filtering
- Justification: icontract-hypothesis directly reads icontract `@require`/`@ensure` decorators used in ContractEval, making strategy inference automatic and correct. Manual approach requires re-implementing pre-condition parsing.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (icontract-hypothesis and evalplus are well-documented libraries; no custom complex architecture requiring semantic analysis)

---

## Experiment Specification

### Dataset

**Dataset A (Primary — Reused from H-M1):** EvalPlus static inputs (764 tests/task)
- **Type:** programmatic-api (published JSON, direct from evalplus package)
- **Source:** evalplus/evalplus, HumanEval+ v0.1.10, MBPP+ v0.2.0
- **Coverage:** All 364 ContractEval tasks (HumanEval+ ∩ ContractEval + MBPP+ ∩ ContractEval)
- **Role in H-M3:** Experiment A baseline — already evaluated in H-M1; results reused directly without re-running

**Dataset B (New for H-M3):** Hypothesis PBT adaptive inputs (5k examples/task/program)
- **Type:** programmatic-api (generated by icontract-hypothesis at runtime from ContractEval pre-conditions)
- **Source:** icontract-hypothesis v1.1.7 + ContractEval pre-condition contracts
- **Budget:** max_examples=5000, seed=42, 60s wall-clock timeout per (task, program) pair
- **Coverage:** Same 364 ContractEval tasks; per-task yield tracked (flag tasks with <100 valid examples)

**Dataset C (Programs — Reused from H-M1):** LLM-generated code samples
- **Type:** programmatic-api (generated via evalplus.codegen with n=10 per model per task)
- **Models:** 5 families (GPT-4o-mini via openai backend; Claude-3-haiku via anthropic backend; DeepSeek-Coder-V2-Lite, CodeLlama-13B, CodeLlama-34B via vllm/hf backend)
- **Filter:** Test-passing programs only (pass all EvalPlus base+plus functional tests)
- **Status:** Already generated and filtered in H-M1 — reuse directly

**Loading Information (for Phase 4 download):**
- Method: programmatic-api (evalplus package + ContractEval GitHub clone)
- Identifier: `pip install evalplus==0.3.1 icontract-hypothesis==1.1.7 icontract`
- Code:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  import subprocess
  # Clone ContractEval for icontract-decorated reference implementations
  # git clone https://github.com/suhanmen/ContractEval ./data/contracteval
  humaneval_tasks = get_human_eval_plus()  # 164 HumanEval+ tasks in ContractEval subset
  mbpp_tasks = get_mbpp_plus()             # 200 MBPP+ tasks in ContractEval subset
  ```

### Models

#### Baseline Model

**Architecture:** Multi-model evaluation pipeline (5 LLM families via evalplus)
- **Type:** API (closed) + vLLM/HuggingFace (open)
- **Models:** GPT-4o-mini, Claude-3-haiku, DeepSeek-Coder-V2-Lite-Instruct, CodeLlama-13B-Instruct, CodeLlama-34B-Instruct
- **Role:** Code generation + test-passing filter (inherited from H-M1 — programs already available)

**Baseline Oracle (Experiment A — from H-M1):** EvalPlus static oracle
- 764 fixed inputs per task (evalplus package, auto-downloaded)
- Contract oracle: for each input x, check `pre(x) → post(f(x))`
- Per-triple result: (model, task, program) → {static_failure_rate, static_failure_inputs}
- Status: **Already computed in H-M1** — reuse result CSV/JSONL directly

**Loading Information (for Phase 4):**
- Method: reuse H-M1 outputs (no re-download needed)
- Identifier: `{h-m1_output_folder}/experiment_a_results.jsonl`
- Code:
  ```python
  import json
  with open("h-m1/experiment_a_results.jsonl") as f:
      exp_a_results = [json.loads(l) for l in f]
  # Format: {task_id, model, program_idx, static_failure_rate, failed_inputs: [...]}
  ```

#### Proposed Model

**Architecture:** Same LLM programs + Hypothesis PBT adaptive oracle (icontract-hypothesis)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Adaptive PBT via icontract-hypothesis
# Based on: mristin/icontract-hypothesis (github.com/mristin/icontract-hypothesis)
# Purpose: Find contract violations beyond the 764 static EvalPlus inputs using
#          Hypothesis's adaptive shrinking guided by ContractEval pre-conditions

import icontract
import icontract_hypothesis
from hypothesis import given, settings, HealthCheck, seed

def run_experiment_b_for_triple(
    task_func_with_contracts,   # LLM program wrapped with @require/@ensure decorators
    task_id: str,
    model: str,
    program_idx: int,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42
) -> dict:
    """
    Runs adaptive PBT (Experiment B) for one (model, task, program) triple.
    Returns: failure_rate, n_valid_examples, n_failures, filter_rate
    """
    violation_count = 0
    valid_count = 0

    @settings(
        max_examples=budget,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
        deadline=None
    )
    @seed(rng_seed)
    @icontract_hypothesis.test_with_inferred_strategy
    def test_program(args):
        nonlocal violation_count, valid_count
        valid_count += 1
        try:
            result = task_func_with_contracts(**args)
            # Post-condition check via icontract @ensure decorators
            # icontract raises ViolationError automatically if @ensure fails
        except icontract.ViolationError:
            violation_count += 1
        except Exception:
            pass  # Pre-condition filter or unrelated error

    test_program()  # Runs budget adaptive examples

    filter_rate = 1.0 - (valid_count / budget) if budget > 0 else 1.0
    failure_rate = violation_count / valid_count if valid_count > 0 else 0.0

    return {
        "task_id": task_id, "model": model, "program_idx": program_idx,
        "adaptive_failure_rate": failure_rate,
        "n_valid": valid_count, "n_failures": violation_count,
        "filter_rate": filter_rate
    }

# Integration: Run for each (model, task, program) triple in ContractEval × 5 models × n=10
# Per-task yield check: flag tasks where filter_rate > 0.95 or valid_count < 100
```

### Training Protocol

**N/A for this experiment** — no model training. This is a program evaluation experiment.

**Computation Protocol:**

| Phase | Action | Scale |
|-------|--------|-------|
| H-M1 reuse | Load Experiment A static oracle results | 364 tasks × 5 models × 10 programs = 18,200 triples (pre-computed) |
| Oracle soundness | Reuse H-M1 quarantine list | 0 tasks quarantined in H-M1; reuse directly |
| Experiment B | Run icontract-hypothesis (5k examples, seed=42, 60s) per triple | ~18,200 triples → wall-clock ~50–100h single-core (parallelizable by task) |
| Yield check | Flag tasks with filter_rate > 0.95 OR valid_count < 100 | Per-task report |
| Comparison | Compute adaptive_gap = Exp_B_rate − Exp_A_rate per triple | 18,200 paired observations |
| Statistics | Wilcoxon signed-rank + Holm correction + bootstrap 95% CI | Per-task and pooled |

**Parallelization:** Embarrassingly parallel by (model, task) pair. Recommend `multiprocessing.Pool` with 16–32 workers. Each worker handles one task × one model (10 programs).

**Seeds:** seed=42 (fixed, single run). No multiple seeds required.

### Evaluation

**Primary Metric:**
- **Adaptive Contribution** = mean(Exp_B_failure_rate − Exp_A_failure_rate) across tasks × models
  - Positive = adaptive PBT finds additional violations beyond static oracle
  - Expected range: 0.05–0.20 based on H-M1 (static oracle already finds 0.40; adaptive explores new input regions)

**Secondary Metric:**
- Fraction of tasks where adaptive contribution > 0.03 absolute (target: ≥50%)
- Per-task filter rate distribution (report low-yield tasks: filter_rate > 0.95)

**Statistical Tests:**
- Wilcoxon signed-rank test (paired): H0: adaptive_contribution = 0; alternative: > 0
- Holm correction for multiple comparisons (per-model sub-analyses)
- Bootstrap 95% CI on mean adaptive contribution (B=10,000 resamples)
- Significance threshold: p < 0.05 (primary)

**Success Criteria:**
- Primary: mean adaptive contribution > 0, Wilcoxon p < 0.05 (Holm-corrected)
- Secondary: adaptive contribution > 0.03 for ≥50% of tasks

**Expected Baseline Performance (from H-M1 established facts):**
- Experiment A static oracle failure rate: mean 0.40 (range 0.35–0.41 across models)
- Adaptive contribution expected positive: Hypothesis explores pre-condition-guided input regions not covered by 764 fixed EvalPlus inputs
- If contribution ≈ 0: oracle-strength (contract semantics alone) explains gap; adaptive search adds nothing → publishable pivot to H-M1 interpretation

**Metrics Loading Information (for Phase 4 implementation):**
- Task Type: contract-violation detection (binary per example, aggregated as rate)
- Library: `scipy.stats.wilcoxon`, `numpy`, `scipy.stats.bootstrap`
- Code:
  ```python
  from scipy.stats import wilcoxon
  import numpy as np

  # Paired comparison per triple
  exp_a_rates = np.array([r["static_failure_rate"] for r in triples])
  exp_b_rates = np.array([r["adaptive_failure_rate"] for r in triples])
  adaptive_gaps = exp_b_rates - exp_a_rates

  stat, p_value = wilcoxon(exp_b_rates, exp_a_rates, alternative="greater")
  mean_gap = np.mean(adaptive_gaps)
  ci = np.percentile(
      [np.mean(np.random.choice(adaptive_gaps, len(adaptive_gaps))) for _ in range(10000)],
      [2.5, 97.5]
  )
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of mean adaptive contribution vs. 0 threshold, with 95% CI error bars

#### Additional Figures (LLM Autonomous)

1. **Paired comparison plot**: Scatterplot of Exp_A_rate vs Exp_B_rate per task (diagonal = no difference); points above diagonal = adaptive finds more violations
2. **Per-task adaptive gap distribution**: Histogram of (Exp_B − Exp_A) per task, with 0-line
3. **Filter rate distribution**: Histogram of per-task filter rates; flag high-filter tasks
4. **Model-stratified adaptive contribution**: Bar chart by model family showing adaptive contribution per model
5. **Task-type breakdown**: HumanEval+ vs MBPP+ adaptive contribution comparison

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | icontract-hypothesis can infer strategies from ContractEval `@require` decorators | TRUE — confirmed by icontract-hypothesis docs; ContractEval uses standard icontract syntax |
| Mechanism Isolatable | Experiment B (adaptive) vs Experiment A (static) are independently measurable; same contracts, same programs | TRUE — by design: Exp A reused from H-M1, Exp B is new run |
| Baseline Measurable | Experiment A (static oracle) results available from H-M1 | TRUE — H-M1 validated with 100% task coverage |

### Architecture Compatibility Check

**System under test:** icontract-hypothesis strategy inference applied to ContractEval task functions

**Required Features:**
- ContractEval task functions decorated with `@icontract.require` pre-conditions
- Type annotations on function arguments (required for strategy inference)
- icontract-hypothesis able to parse bound conditions and generate typed inputs

**Incompatible Cases (must handle gracefully):**
- Tasks with complex pre-conditions that icontract-hypothesis cannot match to patterns → `FilteredStrategy` fallback; high filter_rate
- Tasks with no type annotations → icontract-hypothesis falls back to `st.from_type()` or raises `StrategyInferenceError`
- Tasks where filter_rate > 0.95 (>95% of generated inputs rejected) → exclude from Exp B analysis; report as limitation

**Mitigation:** Run pre-experiment compatibility check on 20 tasks to calibrate filter rate distribution before full Exp B run.

### Mechanism Activation Indicators

**How to detect if adaptive PBT is actually exploring new input space:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Experiment B: task_id={tid} valid={n} filter_rate={r:.2f}"` per task | experiment_b_runner.py:run_experiment_b_for_triple() |
| Adaptive gap | mean(Exp_B_rate − Exp_A_rate) > 0 | analysis.py:compute_adaptive_contribution() |
| Coverage check | Exp B explores inputs not in Exp A's 764 static set | verified by comparing failure inputs sets |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_experiment_b_activated(results: list[dict]) -> tuple[bool, dict]:
    """Verify Experiment B (adaptive PBT) ran and produced meaningful output."""
    indicators = {
        "yield_sufficient": sum(r["n_valid"] >= 100 for r in results) / len(results) >= 0.80,
        "filter_not_total": all(r["filter_rate"] < 0.99 for r in results),
        "adaptive_gap_measurable": any(r["adaptive_failure_rate"] != r.get("static_failure_rate", 0)
                                       for r in results),
        "triples_covered": len(results) >= 10000  # Expect ~18,200 triples
    }
    passed = sum(indicators.values()) >= 3  # At least 3/4 must pass
    return passed, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Strategy inference error | `StrategyInferenceError` exception for >20% of tasks | FAIL: ContractEval pre-conditions incompatible with icontract-hypothesis |
| Total filter (rate=1.0) | All 5000 examples rejected by pre-condition filter | Exclude task; report quarantine |
| Zero valid examples | n_valid = 0 for >20% of tasks | FAIL: Experiment B cannot run; hypothesis cannot be evaluated |
| Adaptive gap = static | All adaptive rates match H-M1 static rates exactly | FAIL: Experiment B not actually running (likely loading H-M1 results twice) |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | ≥80% of tasks with ≥100 valid adaptive examples | yield check per task |
| Effect Measurable | mean(Exp_B − Exp_A) ≠ 0 | paired t-test p < 0.5 (sanity check) |
| Hypothesis Supported | Wilcoxon p < 0.05, mean adaptive contribution > 0 | scipy.stats.wilcoxon, alternative="greater" |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Experiment B runs without catastrophic failure (≥80% task yield)
2. mean adaptive contribution > 0 (Wilcoxon p < 0.05)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB contains CV/image-generation literature only. No relevant sources found for PBT or LLM code evaluation domain.
- 3 knowledge queries executed (similarity scores 0.31–0.44)
- 2 code example queries executed
- 0 domain-relevant results extracted

### B. GitHub Implementations (Exa)

**Repository 1**: mristin/icontract-hypothesis (⭐ 90)
- **URL**: https://github.com/mristin/icontract-hypothesis
- **Query Used**: "icontract-hypothesis hypothesis property-based testing Python contract verification LLM code generation GitHub"
- **Relevance**: Core tool for Experiment B — strategy inference from icontract pre-conditions
- **Key Code** (annotated):
  ```python
  # icontract-hypothesis core pattern:
  # 1. Decorate function with @icontract.require pre-conditions
  # 2. Call test_with_inferred_strategy to auto-infer Hypothesis strategies
  @icontract_hypothesis.test_with_inferred_strategy
  def test_my_func(): ...
  # Hypothesis generates inputs satisfying @require automatically
  # FilteredStrategy rejects inputs violating pre-conditions
  ```
- **Configuration Extracted**: `max_examples=5000`, `seed=42`, `HealthCheck.filter_too_much` suppression
- **Used For**: Core mechanism pseudo-code; Experiment B protocol design

**Repository 2**: HypothesisWorks/hypothesis (⭐ 8788)
- **URL**: https://github.com/hypothesisworks/hypothesis
- **Query Used**: same as above (co-returned with icontract-hypothesis)
- **Relevance**: Underlying PBT engine; `@settings` configuration for budget and reproducibility
- **Configuration Extracted**: `settings.register_profile`, `HealthCheck` suppression, `seed()` usage
- **Used For**: Training protocol / computation protocol parameters

**Repository 3**: evalplus/evalplus (⭐ 1789)
- **URL**: https://github.com/evalplus/evalplus
- **Query Used**: "evalplus EvalPlus benchmark LLM code generation evaluation ContractEval HumanEval MBPP GitHub"
- **Relevance**: Source of Experiment A static inputs (reused from H-M1); code generation pipeline (`evalplus.codegen`)
- **Key Code** (annotated):
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  # Loads task dict with prompt, base_input, plus_input, contract, solution
  # plus_input = 764 additional tests per task (Experiment A basis)
  ```
- **Configuration Extracted**: `evalplus.codegen --n 10 --backend openai/anthropic/vllm`
- **Used For**: Dataset loading code; Experiment A (static oracle) baseline definition

**Repository 4**: suhanmen/ContractEval (⭐ 5, ACL 2026)
- **URL**: https://github.com/suhanmen/ContractEval
- **Query Used**: "ContractEval suhanmen contract evaluation LLM code postcondition precondition Python GitHub ACL 2026"
- **Relevance**: Source of 364 task contracts (icontract `@require`/`@ensure` decorators); paper results for baseline context
- **Paper Results**: 0% CSR under standard prompting; 23–41% with contract-aware prompting (SMT-based evaluation)
- **Used For**: Dataset specification; oracle definition; pre-condition compatibility assessment

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear (icontract-hypothesis and evalplus are well-documented libraries with complete API documentation; no custom complex architecture requiring semantic analysis)

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — H-M1
- **File**: `h-m1/04_validation.md`
- **Reused Components**:
  - Programs: LLM-generated test-passing programs (5 models × 364 tasks × n=10) — fully reused
  - Experiment A results: static oracle failure rates per (model, task, program) triple — reused directly as Exp A baseline
  - Quarantine list: 0 tasks quarantined — all 364 tasks usable
  - Oracle soundness: pre-verified in H-M1 (100k examples, 2h per task)
- **Why Reused**: Enables controlled experiment — only input generation strategy changes between Exp A and Exp B; contracts, programs, and models are identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset A (static inputs) | GitHub + H-M1 | evalplus/evalplus (B.3), H-M1 results (D) |
| Dataset B (adaptive PBT) | GitHub | mristin/icontract-hypothesis (B.1) |
| Dataset C (LLM programs) | H-M1 | H-M1 validated results (D) |
| Core mechanism pseudo-code | GitHub | icontract-hypothesis API (B.1), hypothesis settings (B.2) |
| Computation protocol | GitHub + Phase 2B | evalplus.codegen (B.3), 02b_verification_plan.md §2.4 H-M3 |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md §2.4 H-M3 success criteria |
| Statistical tests | Phase 2B | 02b_verification_plan.md §2.4 H-M3 verification protocol |
| Filter rate threshold | Phase 2B | 02b_verification_plan.md §1.5 Risk R2 (A2 assumption) |
| Failure response pivot | Phase 2B | 02b_verification_plan.md §2.4 H-M3 failure response |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written; restated in state block)
**Date:** 2026-08-03T00:00:00+00:00

### Workflow History for This Hypothesis
- 2026-08-03T15:33:48: H-M3 set to IN_PROGRESS (external loop Phase 2C → 3 → 4)
- 2026-08-03: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no domain matches), Exa (GitHub — 4 repositories), Serena (skipped — not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
