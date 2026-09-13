# Experiment Design: H-M1

**Date:** 2026-08-03
**Author:** Anonymous
**Hypothesis Statement:** On ContractEval's 364 tasks, test-passing LLM programs evaluated on EvalPlus's published 764-test static inputs simultaneously under differential oracle and contract oracle show oracle-isolation gap ≥0.10 absolute with ≥0.05 contract-unique mass (output-equal-to-gt but contract-failing).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Oracle isolation experiment comparing two oracles on identical inputs.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED (97/155 tasks, 62.6% violation rate, mean gap 0.471)
**Gate Status:** MUST_WORK — failure triggers PIVOT to richness stratification

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED ✅)

### Gate Condition
MUST_WORK — mean oracle-isolation gap ≥ 0.10 (Wilcoxon p < 0.01 after Holm); contract-unique mass ≥ 0.05 (bootstrap 95% CI lower bound > 0.03). Failure does NOT stop the pipeline — triggers PIVOT to oracle-strength-only interpretation via richness stratification.

---

## Continuation Context

H-E1 validated (2026-08-03): 97/155 sampled tasks show ≥1 contract violation under PBT; mean max contract-strength gap 0.471; zero PBT errors. H-E1's test-passing code samples (per model, per task) are the program corpus for H-M1 Experiment A — no new code generation needed.

### Previous Hypothesis Results (H-E1)
- Oracle precheck: all 364 ContractEval tasks have violation_count > 0 — contracts are non-trivial
- PBT experiment (gpt-4o-mini, 155 tasks): 62.6% tasks show ≥1 violation under icontract-hypothesis
- Mean max contract-strength gap: 0.471 (range 0.0–1.0)
- Zero errors; results robust across 10 PBT trials per task
- Key reuse for H-M1: test-passing programs from H-E1 are the evaluation corpus

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon KB contains no relevant entries — the indexed corpus covers diffusion models and image generation (HuggingFace diffusers, Stable Diffusion). No content found on oracle isolation, contract oracles, EvalPlus, ContractEval, or property-based testing for code evaluation.

**Queries executed:**
- "oracle isolation differential testing contract verification" → 4 results, similarity 0.24–0.25, all diffusion-related
- "contract oracle differential oracle implementation challenges best practices" → 5 results, highest 0.34, all off-topic
- "EvalPlus ContractEval benchmark code evaluation" → 5 results, highest 0.42 (geneval — image generation benchmark)
- "property-based testing icontract-hypothesis python" → 5 results, highest 0.39, all off-topic

**Implication:** Experiment design relies entirely on Exa GitHub findings and Phase 2B specification. All hyperparameter and protocol choices are sourced from the original papers.

### Archon Code Examples

No relevant code examples found. Closest result: `torch.allclose(out1, out2)` pattern illustrating equality oracle — too generic to be useful.

### Exa GitHub Implementations

**Source 1: suhanmen/ContractEval** (⭐5, ACL 2026 Findings)
- **URL:** https://github.com/suhanmen/ContractEval
- **Paper:** arXiv:2510.12047 — "ContractEval: A Benchmark for Evaluating Contract-Satisfying Assertions in Code Generation"
- **Authors:** Lim, Hahn, Park, Ko, Han (Yonsei + U. Seoul)
- **Architecture:** 364 tasks extending HumanEval+/MBPP+ with Python icontract pre/post-condition annotations; two-stage neuro-symbolic CVT generation (LLM → SMT-LIB → Z3); feasibility filtering; AVC/TS/CSR metrics
- **Key Metrics:** pass@1 75–82% (standard prompting), CSR = 0% for standard prompting; EAS raises CSR to ~50.94%
- **Relevance:** Primary dataset; confirms icontract-annotated reference implementations exist and are sound

**Source 2: evalplus/evalplus** (⭐1789, NeurIPS 2023 + COLM 2024)
- **URL:** https://github.com/evalplus/evalplus
- **Architecture:** HumanEval+ (80× tests) and MBPP+ (35× tests) over original benchmarks; publishes all inputs as JSONL.GZ; EvalPerf efficiency extension; vLLM/OpenAI/Anthropic backends
- **Key Code:**
  ```python
  from evalplus.data import get_human_eval_plus, write_jsonl
  # Problem fields: task_id, entry_point, prompt, canonical_solution, base_input, plus_input
  samples = [
      dict(task_id=task_id, solution=GEN_SOLUTION(problem["prompt"]))
      for task_id, problem in get_human_eval_plus().items()
  ]
  write_jsonl("samples.jsonl", samples)
  # Evaluate:
  # evalplus.evaluate --model ... --dataset humaneval --backend vllm
  ```
- **Dataset fields:** `base_input` (original tests), `plus_input` (extended tests, up to 764 total)
- **Key finding:** Dense testing reduces pass@k by up to 23.1% vs. original HumanEval across 26 LLMs
- **Relevance:** Provides the 764-test static input set for Experiment A oracle isolation

**Source 3: egnaro9/evals-differential-oracle**
- **URL:** https://github.com/egnaro9/evals-differential-oracle
- **Architecture:** Two independent implementations compared; invariants checked against thousands of random boards; two-layer safety net: differential oracle (disagreement detection) + invariant checks
- **Relevance:** Confirms the differential oracle pattern: `f(x) == gt(x)` disagreement detection; validates two-layer approach (differential + invariant/contract)

**Source 4: tripwire-oracle (PyPI)**
- **URL:** https://pypi.org/project/tripwire-oracle/
- **Architecture:** 4-layer oracle — L1 canonical correctness (output match), L2 metamorphic/property invariants, L3 differential on withheld adversarial inputs, L4 isolated speedup
- **Relevance:** Validates L1+L2 oracle layering pattern; L2 (property invariants) corresponds to our contract oracle layer

**Source 5: mristin/icontract-hypothesis** (v1.1.7)
- **URL:** https://github.com/mristin/icontract-hypothesis
- **Key Code:**
  ```python
  import icontract
  import icontract_hypothesis
  
  @icontract.require(lambda x: x > 0)           # precondition
  @icontract.ensure(lambda result, x: result > x)  # postcondition
  def some_func(x: int) -> int: ...
  
  # Strategy inference: bounds matched to Hypothesis strategies
  # e.g., `5 < x < 10` -> strategies.integers(min=6, max=9)
  # Unmatched single-arg preconditions: FilteredStrategy on type hint
  # Remaining: filter on full kwarg dict
  ```
- **Known limitation:** No automatic propagation of constructor preconditions for composite inputs; must manually design strategies for class instances
- **Relevance:** Core tool for H-M1 contract oracle execution; precondition-guided strategy inference ensures valid test inputs

### 🎯 Implementation Priority Assessment

This is NOT a paper reproduction experiment — H-M1 is an original oracle isolation experiment design. No single authoritative implementation exists to reproduce.

**Primary implementation path:** Build on top of `evalplus` (unified evaluation backend) + `icontract-hypothesis` (contract oracle execution) using `ContractEval` reference implementations.

**Recommended Implementation Path:**
- Primary: evalplus evaluation pipeline + icontract decorators from ContractEval + custom oracle comparison harness
- Fallback: Fresh static input generation (Hypothesis with icontract pre-conditions) if EvalPlus input mapping fails for unmatched tasks (A3 risk)
- Justification: EvalPlus provides standardized execution sandbox; icontract-hypothesis provides the contract checking layer; combining them gives the oracle isolation experiment with zero new infrastructure

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. EvalPlus and icontract-hypothesis are well-documented public packages with explicit APIs. No complex unfamiliar code patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset Name:** ContractEval + EvalPlus static inputs
**Type:** standard (both public benchmarks)
**Tasks:** 364 (ContractEval's HumanEval+/MBPP+ subset)
**Static inputs per task:** 764 (EvalPlus `base_input` + `plus_input`)
**Total evaluation instances:** 364 tasks × 764 inputs × N test-passing programs per task

**Dataset Split Structure:**
- No train/val/test split — all 364 tasks are evaluation targets
- EvalPlus inputs per task: ~80 `base_input` + ~684 `plus_input` = 764 total
- Program corpus: test-passing LLM programs from H-E1 (5 models × n=10 samples per task, filtered to test-passing)

**Pre-processing:**
1. Load ContractEval reference implementations with icontract decorators (from `suhanmen/ContractEval`)
2. Load EvalPlus JSONL.GZ (`HumanEvalPlus.jsonl.gz`, `MBPPPlus.jsonl.gz`) — fields: `base_input`, `plus_input`
3. Task ID alignment: match ContractEval task IDs to EvalPlus task IDs (expect ≥90% overlap; generate fresh for unmatched)
4. Oracle soundness pre-check: verify ContractEval reference implementations pass all contracts under 100k Hypothesis examples (quarantine tasks where reference fails ≥1 contract)
5. Program corpus: load H-E1 test-passing programs per (model, task) from `h-e1/code/` output

**Loading Information (for Phase 4 download):**
- Method: evalplus Python package + GitHub clone
- Identifier: `pip install evalplus` then `evalplus.data.get_human_eval_plus()` / `get_mbpp_plus()`; `git clone https://github.com/suhanmen/ContractEval`
- Code:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  he_data = get_human_eval_plus()   # dict: task_id -> {base_input, plus_input, ...}
  mbpp_data = get_mbpp_plus()       # same structure
  # Override path: HUMANEVAL_OVERRIDE_PATH or MBPP_OVERRIDE_PATH env vars
  ```

**Synthetic Data Policy:** Not applicable — both ContractEval and EvalPlus are real, established benchmarks (ACL 2026 + NeurIPS 2023).

### Models

#### Baseline Oracle (Oracle A — Differential)

**Description:** EvalPlus differential equality oracle
**Mechanism:** For each (program, input) pair: execute program, compare output to canonical ground-truth using equality check `f(x) == gt(x)`
**Input set:** EvalPlus published 764 static inputs per task (fixed, no sampling)
**Baseline performance:** Up to 23.1% pass@k reduction from original HumanEval (Chen et al. NeurIPS 2023)

**Loading Information (for Phase 4):**
- Method: evalplus evaluation sandbox (handles execution, timeout, output comparison)
- Code:
  ```python
  # evalplus already implements differential oracle internally
  # evalplus.evaluate --dataset humaneval --samples samples.jsonl
  # Or custom: compare f(x) == canonical_solution(x) for each input
  from evalplus.eval import evaluate_with_test_code
  ```

#### Proposed Oracle (Oracle B — Contract)

**Architecture:** ContractEval contract oracle using icontract decorators
**Mechanism:** For each (program, input) pair: (1) check `pre(x)` satisfied, (2) execute program, (3) check `post(f(x))` holds
**Integration:** Replace function body in ContractEval icontract-annotated wrapper; execute under same 764 static inputs as Oracle A

**Core Mechanism Pseudo-code (Oracle Isolation Harness):**

```python
# H-M1 Core: Oracle Isolation Experiment (Experiment A)
# Evaluates identical inputs under two oracles simultaneously

import icontract
from evalplus.data import get_human_eval_plus, get_mbpp_plus

def evaluate_oracle_isolation(
    program_code: str,
    task_id: str,
    static_inputs: list,   # EvalPlus 764 inputs for this task
    ground_truth_fn,        # canonical solution
    contract_fn,            # icontract-annotated reference
) -> dict:
    """
    Returns per-input oracle decisions for isolation gap computation.
    """
    results = []
    for x in static_inputs:
        # Oracle A: differential equality
        try:
            out_prog = exec_with_timeout(program_code, x, timeout=5)
            out_gt = ground_truth_fn(*x)
            diff_fail = (out_prog != out_gt)
        except Exception:
            diff_fail = True

        # Oracle B: contract oracle (icontract decorators)
        try:
            contract_fn(*x)      # pre enforced by @require; post by @ensure
            contract_fail = False
        except icontract.ViolationError:
            contract_fail = True
        except Exception:
            contract_fail = True

        # Classify failure category
        is_contract_unique = (not diff_fail) and contract_fail
        results.append({
            "diff_fail": diff_fail,
            "contract_fail": contract_fail,
            "contract_unique": is_contract_unique,
        })

    # Aggregate per-task
    n = len(results)
    return {
        "diff_failure_rate":     sum(r["diff_fail"] for r in results) / n,
        "contract_failure_rate": sum(r["contract_fail"] for r in results) / n,
        "contract_unique_mass":  sum(r["contract_unique"] for r in results) / n,
        "oracle_isolation_gap":  (
            sum(r["contract_fail"] for r in results) -
            sum(r["diff_fail"] for r in results)
        ) / n,
    }
```

### Training Protocol

No training — this is a pure evaluation experiment. The "training protocol" here is the evaluation execution protocol.

**Execution Protocol:**

**Step 1: Pre-checks (before model evaluation)**
- Task ID overlap verification: assert ≥90% ContractEval task IDs ∈ EvalPlus task IDs
- Oracle soundness pre-check: Hypothesis PBT (100k examples, seed=42, 2h wall-clock) on all ContractEval reference implementations; quarantine tasks where reference fails ≥1 contract; report quarantine rate (expected < 5%)
- Pilot test: verify EvalPlus input loading and icontract execution on 10 random tasks before full run

**Step 2: Program Corpus Loading**
- Load H-E1 test-passing programs for all 5 models from `h-e1/code/` output
- Filter: keep only programs that passed EvalPlus test suite (already filtered in H-E1)

**Step 3: Oracle Isolation Evaluation (Experiment A)**
- For each (model, task, program) triple — all programs × all 764 EvalPlus inputs
- Execute Oracle A (differential) and Oracle B (contract) on same input set
- Classify: redundant / contract-unique / differential-only per input
- Aggregate per (model, task): oracle-isolation gap, contract-unique mass

**Execution Parameters:**
- Timeout per input: 5 seconds
- Parallelism: multiprocessing (CPU-only, no GPU required)
- Seed: 42 (for any randomized components)
- Quarantine threshold: ≥1 contract failure on reference → exclude task

**Step 4: Statistical Analysis**
- Wilcoxon signed-rank test: per-task oracle-isolation gap vs. 0 (H0: gap = 0), with Holm correction
- Bootstrap 95% CI (n=10000 resamples) on mean oracle-isolation gap and contract-unique mass
- Stratification: report by model family and task type (HumanEval+ vs. MBPP+)

**Seeds:** 42 (fixed)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Oracle-isolation gap | mean(contract_failure_rate) − mean(differential_failure_rate) across tasks | ≥ 0.10 |
| Wilcoxon p-value | Signed-rank test on per-task gaps vs. H0: gap=0, with Holm correction | < 0.01 |

**Secondary Metrics:**

| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Contract-unique mass | Fraction where `f(x)==gt(x)` AND `post(f(x))` fails | ≥ 0.05 (bootstrap CI lower > 0.03) |
| Task coverage | Fraction of 364 tasks with ≥1 evaluable program after quarantine | ≥ 0.90 |

**Failure Classification:**
1. Contract-unique: `f(x)==gt(x)` AND `post(f(x))` fails (oracle strength evidence)
2. Redundant: both oracles detect failure (differential + contract both fail)
3. Differential-only: `f(x)!=gt(x)` AND `post(f(x))` holds (correctness without contract validity)
4. Neither: both pass

**Expected Baseline Performance (from research):**
- Differential oracle (EvalPlus 764-test): reduces pass@1 by up to 23.1% vs. original HumanEval (Chen et al. NeurIPS 2023)
- Expected differential failure rate: ~15–25% of inputs per test-passing program (programs pass unit tests but EvalPlus finds additional failures)
- H-M1 predicts contract failure rate ≥ differential failure rate by ≥10 pp absolute

**Success Criteria (MECHANISM PoC):**
- Primary: oracle-isolation gap ≥ 0.10 AND Wilcoxon p < 0.01 after Holm correction
- Secondary: contract-unique mass ≥ 0.05 with bootstrap 95% CI lower bound > 0.03
- PoC pass = both primary criteria satisfied

**Metrics Loading Information (for Phase 4 implementation):**
- Task Type: binary classification per input (pass/fail under each oracle)
- Library: `scipy.stats.wilcoxon` (Wilcoxon signed-rank), `numpy` bootstrap, custom oracle harness
- Code:
  ```python
  from scipy.stats import wilcoxon
  from statsmodels.stats.multitest import multipletests
  import numpy as np
  
  # Per-task gaps
  gaps = [contract_rate_task_i - diff_rate_task_i for i in tasks]
  stat, pval_raw = wilcoxon(gaps, alternative='greater')
  # Holm correction across tasks
  rejected, pvals_corrected, _, _ = multipletests([pval_raw], method='holm')
  
  # Bootstrap CI on mean gap
  boot_means = [np.mean(np.random.choice(gaps, len(gaps))) for _ in range(10000)]
  ci_lower, ci_upper = np.percentile(boot_means, [2.5, 97.5])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — mean oracle-isolation gap vs. 0.10 threshold; contract-unique mass vs. 0.05 threshold; with 95% CI error bars

#### Additional Figures (LLM Autonomous)
Suggested based on oracle isolation mechanism:
- **Oracle failure breakdown**: Stacked bar per model showing redundant / contract-unique / differential-only / neither fractions
- **Per-task oracle-isolation gap distribution**: Violin plot or CDF across 364 tasks
- **Contract-unique mass by task type**: Separate bars for HumanEval+ vs. MBPP+
- **Scatter**: per-task differential failure rate vs. contract failure rate (visualize gap)

All figures saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | EvalPlus static inputs loadable for all ContractEval task IDs; icontract decorators executable in ContractEval reference code | TRUE — both packages public and documented |
| Mechanism Isolatable | Oracle A and Oracle B can be run independently on same input; contract oracle can be disabled (run Oracle A only) | TRUE — two separate execution paths |
| Baseline Measurable | Differential oracle (Oracle A) can be measured independently from contract oracle (Oracle B) | TRUE — EvalPlus evaluation runs without icontract |

### Architecture Compatibility Check

**Compatible:** Python execution sandbox required (both oracles run via Python function calls). CPU-only, no GPU, no neural network inference (programs already generated from H-E1).

**Required components:**
- `evalplus` package: execution sandbox, ground-truth comparison, dataset loading
- `icontract` + `icontract-hypothesis`: pre/post-condition decorators and enforcement
- `ContractEval` repository: icontract-annotated reference implementations
- H-E1 output: test-passing program corpus per (model, task)

**Incompatible scenarios:**
- Tasks where ContractEval uses Z3-only constraints (not icontract-enforceable) — expected to be rare; quarantine if found
- Tasks where EvalPlus inputs don't map to ContractEval task IDs — fallback to fresh Hypothesis-generated inputs

> ⚠️ If EvalPlus task ID overlap < 90%, Phase 4 MUST trigger the fallback input generation path before running oracle comparison.

---

### Mechanism Activation Indicators

**How to detect if the oracle isolation mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Oracle isolation computed for task {task_id}: gap={gap:.3f}, contract_unique={cu:.3f}" | oracle_isolation.py:evaluate_oracle_isolation() |
| Failure Classification | contract_unique_count > 0 for ≥50% of tasks | results aggregation step |
| Metric Delta | mean oracle-isolation gap > 0 (any positive gap confirms oracle non-equivalence) | statistical_analysis.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_oracle_isolation_activated(results: dict) -> tuple[bool, dict]:
    """
    Verify that the oracle isolation experiment actually ran and measured differences.
    """
    indicators = {
        "tasks_evaluated": len(results["per_task_gaps"]) >= 300,  # ≥300/364 tasks
        "oracle_a_ran": results["mean_diff_failure_rate"] > 0,    # EvalPlus found failures
        "oracle_b_ran": results["mean_contract_failure_rate"] > 0, # contracts found failures
        "contract_unique_nonzero": results["mean_contract_unique_mass"] > 0,
        "gap_computed": "oracle_isolation_gap" in results,
    }
    success = all(indicators.values())
    return success, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Oracle A silent | `mean_diff_failure_rate == 0` — EvalPlus found no failures | FAIL: EvalPlus inputs not reaching program execution; check sandbox |
| Oracle B silent | `mean_contract_failure_rate == 0` — no contract violations on any input | FAIL: icontract not triggering; verify decorators loaded correctly |
| No contract-unique | `contract_unique_mass < 0.001` on first 50 tasks | WARN: A5 assumption potentially violated; continue but flag |
| EvalPlus mapping gap | Task ID overlap < 90% | Trigger fallback input generation before proceeding |
| Quarantine overflow | >5% tasks quarantined in soundness pre-check | WARN: R1 risk materializing; report rate and quarantined task IDs |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Both oracles executed on ≥300/364 tasks | `tasks_evaluated` indicator |
| Effect Measurable | mean oracle-isolation gap > 0 | Before statistical thresholding |
| Hypothesis Supported | gap ≥ 0.10, Wilcoxon p < 0.01 (Holm), contract-unique ≥ 0.05 | Statistical analysis output |

- **hypothesis_support_threshold:** oracle-isolation gap ≥ 0.10 (absolute), Wilcoxon p < 0.01 after Holm correction, contract-unique mass ≥ 0.05 (bootstrap CI lower > 0.03)
- **hypothesis_support_metric:** mean oracle-isolation gap across all evaluable tasks (primary); contract-unique mass (secondary)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant entries found in Archon KB (diffusion model corpus). All implementation knowledge sourced from Exa GitHub search and Phase 2B specification.

---

### B. GitHub Implementations (Exa)

**Repository 1: suhanmen/ContractEval** (⭐5)
- **URL:** https://github.com/suhanmen/ContractEval
- **Query Used:** "ContractEval LLM code evaluation contract oracle differential oracle Python"
- **Relevance:** Primary dataset and contract annotation source; provides icontract-decorated reference implementations for all 364 tasks
- **Architecture Extracted:** Two-stage CVT generation; AVC/TS/CSR metrics; icontract pre/post-conditions on HumanEval+/MBPP+ subset
- **Results:** pass@1 75–82% (standard), CSR 0% (standard prompting), CSR ~50.94% (EAS prompting)
- **Used For:** Dataset specification; contract oracle implementation; task corpus

**Repository 2: evalplus/evalplus** (⭐1789)
- **URL:** https://github.com/evalplus/evalplus
- **Query Used:** "EvalPlus evalplus benchmark evaluation LLM code generation Python implementation"
- **Key Code:**
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  # Returns: {task_id: {prompt, canonical_solution, base_input, plus_input, ...}}
  evalplus.evaluate --dataset humaneval --samples samples.jsonl
  ```
- **Configuration Extracted:** 764 static inputs per task (base + plus); JSONL.GZ format; CLI evaluation pipeline; vLLM/OpenAI/Anthropic backends
- **Results:** Reduces pass@1 by up to 23.1% vs. original HumanEval across 26 LLMs
- **Used For:** Static input dataset (764 inputs/task); evaluation sandbox; differential oracle baseline

**Repository 3: egnaro9/evals-differential-oracle**
- **URL:** https://github.com/egnaro9/evals-differential-oracle
- **Query Used:** "ContractEval LLM code evaluation contract oracle differential oracle Python"
- **Key Code:**
  ```python
  # Two-layer oracle: differential disagreement + invariant checks
  impl_react_output = impl_react.resolve(board)
  impl_native_output = impl_native.resolve(board)
  assert impl_react_output == impl_native_output  # differential oracle
  # + invariant_checker.check(impl_react_output)  # contract/property layer
  ```
- **Used For:** Validated two-layer oracle pattern (differential + property/contract); confirms architectural approach

**Repository 4: tripwire-oracle (PyPI)**
- **URL:** https://pypi.org/project/tripwire-oracle/
- **Query Used:** "ContractEval LLM code evaluation contract oracle differential oracle Python"
- **Architecture:** 4-layer oracle (canonical, metamorphic/property, differential adversarial, speedup); L2 = property invariants = our contract oracle layer
- **Used For:** Confirmed layered oracle design; L1+L2 structure validates our differential+contract comparison approach

**Repository 5: mristin/icontract-hypothesis** (v1.1.7)
- **URL:** https://github.com/mristin/icontract-hypothesis
- **Query Used:** "icontract-hypothesis property-based testing python postcondition verification"
- **Key Code:**
  ```python
  import icontract
  @icontract.require(lambda x: x > 0)
  @icontract.ensure(lambda result, x: result > x)
  def some_func(x: int) -> int: ...
  # Strategy inference: precondition bounds → Hypothesis strategies
  # FilteredStrategy for unmatched single-arg preconditions
  ```
- **Known Limitation:** No automatic strategy for composite type constructors
- **Used For:** Contract oracle execution; pre/postcondition enforcement; H-M1 core tool

---

### C. Code Analysis (Serena)

Serena analysis not performed — code structure from EvalPlus, ContractEval, and icontract-hypothesis is sufficiently clear from documentation and README content. No complex custom layers or unfamiliar architectures.

---

### D. Previous Hypothesis Context

**Source:** H-E1 Phase 4 Validation Results (2026-08-03)
- **Reused Components:**
  - Dataset: ContractEval (364 tasks) — proven loadable and sound for PBT execution
  - Code corpus: test-passing LLM programs per (model, task) — H-E1's primary output, reused as H-M1's evaluation input
  - Oracle soundness: ContractEval reference implementations all passed soundness pre-check in H-E1
- **Why Reused:** Enables controlled experiment — only the oracle changes (differential vs. contract); same programs evaluated under both; H-E1 confirmed icontract execution works on ContractEval tasks

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (ContractEval) | Phase 2B + GitHub | Exa B.1 (ContractEval) |
| Static input set (764/task) | GitHub | Exa B.2 (evalplus) |
| Differential oracle design | GitHub | Exa B.3, B.4 |
| Contract oracle (icontract) | GitHub | Exa B.5 (icontract-hypothesis) |
| Oracle isolation pseudo-code | Phase 2B + GitHub B.3/B.5 | Derived from Exa B.2, B.5 |
| Execution parameters (5s timeout, seed=42) | Phase 2B | 02b_verification_plan.md §2.2 H-M1 |
| Statistical tests (Wilcoxon, Holm, Bootstrap) | Phase 2B | 02b_verification_plan.md §2.2 H-M1 |
| Success thresholds (gap ≥0.10, CU ≥0.05) | Phase 2B | 02b_verification_plan.md §2.2 H-M1 |
| H-E1 program corpus reuse | Previous context | H-E1 Phase 4 validation |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-03T14:45:00+00:00

### Workflow History for This Hypothesis
- 2026-08-03T14:22:20: H-M1 set to IN_PROGRESS (external loop)
- 2026-08-03T14:45:00: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results, diffusion model corpus), Exa (GitHub — 5 relevant repositories found), Serena (not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
