# Experiment Brief: h-e1 — Contract-Strength Gap Existence on Full ContractEval

**Phase:** 2C — Experiment Design
**Hypothesis ID:** h-e1
**Date:** 2026-08-03
**Target:** ContractEval full 364-task suite, execution-based PBT

---

## 1. Hypothesis Recap

**Statement:** On ContractEval's full 364 HumanEval+/MBPP+ tasks, LLM-generated programs that pass all unit tests exhibit a non-zero contract-strength gap (fraction failing ≥1 contract under Hypothesis PBT with icontract-hypothesis strategy inference).

**Success Criteria:**
- Primary: mean contract-strength gap > 0, bootstrap 95% CI lower bound > 0.01
- Secondary: gap replicates h-e1 prior 7.42% lower bound on tractable subset

**Gate:** MUST_WORK — failure stops all H-M hypotheses.

---

## 2. Dataset

### 2.1 Primary Dataset: ContractEval

| Field | Value |
|-------|-------|
| Name | ContractEval |
| Type | standard (real benchmark, ACL 2026) |
| Source | github.com/suhanmen/ContractEval |
| Tasks | 364 (HumanEval+ subset + MBPP+ subset) |
| Per-task content | Task description (explicit preconditions), Python pre/postcondition contracts (`@icontract.require` / `@icontract.ensure`), reference implementation, unit test inputs |
| License | MIT |

**Dataset acquisition:**
```bash
git clone https://github.com/suhanmen/ContractEval
```

ContractEval is a strict subset of HumanEval+ and MBPP+ — all 364 tasks map directly to EvalPlus task IDs (assumption A3 from verification plan). Task ID overlap must be verified (≥90% expected) before proceeding to H-M1.

### 2.2 Secondary Dataset: EvalPlus Static Inputs

| Field | Value |
|-------|-------|
| Name | EvalPlus HumanEval+ / MBPP+ published inputs |
| Type | standard (NeurIPS 2023) |
| Source | github.com/evalplus/evalplus |
| Tests per task | 764 (HumanEval+), 108.5 avg (MBPP+) |
| Format | JSON (published, versioned) |

Used in H-M1 (oracle isolation) only. For h-e1 (Experiment B / adaptive PBT), EvalPlus unit tests are used solely for the test-passing filter step.

---

## 3. Models

| Model | Family | Backend | Size | Source |
|-------|--------|---------|------|--------|
| GPT-4o-mini | OpenAI (closed) | `openai` | ~8B MoE | OpenAI API |
| Claude-3-haiku | Anthropic (closed) | `anthropic` | ~20B | Anthropic API |
| DeepSeek-Coder-V2-Lite | DeepSeek (open) | `vllm` | 16B | HuggingFace |
| CodeLlama-13B-Instruct | Meta (open) | `vllm` | 13B | HuggingFace |
| CodeLlama-34B-Instruct | Meta (open) | `vllm` | 34B | HuggingFace |

**Generation config:** n=10 samples per (model, task), greedy off, temperature=0.8 for diversity.
**Fallback:** If API rate limiting >10% errors, reduce to n=5 (see Risk R4 in verification plan).

---

## 4. Experiment Design

### 4.1 Overview

h-e1 requires a single experiment (Experiment B: adaptive PBT) to establish existence of the contract-strength gap. The experiment is a pipeline:

```
Step 0: Oracle soundness pre-check
Step 1: Code generation (evalplus.codegen)
Step 2: Unit test filtering (evalplus.evaluate)
Step 3: Contract wrapping (icontract)
Step 4: Hypothesis PBT (icontract_hypothesis.test_with_inferred_strategy)
Step 5: Gap computation + statistical test
```

### 4.2 Step-by-Step Protocol

#### Step 0 — Oracle Soundness Pre-check (prerequisite, ~2h wall-clock)

Run Hypothesis PBT against ContractEval **reference implementations** at high budget. Quarantine any task where the reference fails a contract.

```python
from hypothesis import given, settings, HealthCheck
import icontract_hypothesis

@settings(
    max_examples=100_000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
def soundness_check(task):
    """Returns True if reference implementation passes all contracts."""
    wrapped_ref = wrap_with_icontract(task.reference_code, task.preconditions, task.postconditions)
    try:
        icontract_hypothesis.test_with_inferred_strategy(wrapped_ref)
        return True
    except icontract.errors.ViolationError:
        return False  # quarantine this task
```

Tasks failing soundness check are removed from all subsequent analyses. Expected quarantine rate: <5% (expert-written contracts per Lim et al. 2025).

#### Step 1 — Code Generation

```bash
# For each model
evalplus.codegen \
    --model "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct" \
    --backend vllm \
    --dataset humaneval \
    --n_samples 10 \
    --temperature 0.8 \
    --root ./results/generated/
```

Override dataset to ContractEval tasks by passing custom task JSON (ContractEval provides task descriptions with explicit contracts in prompts).

**Total generations:** 5 models × 364 tasks × 10 samples = 18,200 programs.

#### Step 2 — Unit Test Filtering

Keep only test-passing programs (pass@1 under EvalPlus evaluation):

```bash
evalplus.evaluate \
    --dataset humaneval \
    --samples ./results/generated/{model}/samples.jsonl
```

Record per-(model, task) pass count. Programs failing unit tests are excluded from contract checking — contract-strength gap is measured only over test-passing programs.

**Expected yield:** ~30-70% of programs pass unit tests (model-dependent).

#### Step 3 — Contract Wrapping

For each test-passing program, inject icontract decorators matching ContractEval's pre/postconditions:

```python
import icontract
import icontract_hypothesis
from hypothesis import given, settings, HealthCheck

def wrap_program_with_contracts(program_source: str, preconditions: list[str], postconditions: list[str]) -> callable:
    """
    Dynamically compile program_source and decorate with icontract.
    preconditions / postconditions are Python lambda strings from ContractEval.
    """
    exec(compile(program_source, "<llm_program>", "exec"), namespace := {})
    fn = namespace["solution"]
    
    for pre in reversed(preconditions):
        fn = icontract.require(eval(pre))(fn)
    for post in postconditions:
        fn = icontract.ensure(eval(post))(fn)
    return fn
```

**Note on filter rate (Risk R2):** icontract-hypothesis infers strategies from `@icontract.require` preconditions by pattern-matching bounds and regex, falling back to `FilteredStrategy` for complex conditions. Tasks with complex quantified preconditions may yield <100 valid samples per 5k budget. Per-task filter rate must be logged; tasks with <100 valid samples are flagged and reported as low-yield but not excluded from gap computation (gap=0 for these tasks is a conservative lower bound).

#### Step 4 — Hypothesis PBT Contract Checking

```python
@settings(
    max_examples=5_000,
    seed=42,
    deadline=timedelta(seconds=60),
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
def run_pbt_contract_check(wrapped_fn) -> dict:
    """
    Returns: {violated: bool, n_valid_examples: int, violation_input: Any | None}
    """
    violation = {"violated": False, "n_valid": 0, "violation_input": None}
    
    @given(icontract_hypothesis.infer_strategy(wrapped_fn))
    @settings(max_examples=5_000, seed=42, deadline=timedelta(seconds=60))
    def inner_test(**kwargs):
        violation["n_valid"] += 1
        wrapped_fn(**kwargs)  # raises ViolationError on contract failure
    
    try:
        inner_test()
    except icontract.errors.ViolationError as e:
        violation["violated"] = True
        violation["violation_input"] = str(e)
    
    return violation
```

**Per-triple cost:** ≤60s wall-clock. Total: ~18,200 programs × 60s / CPU_parallelism. With 32 cores, ≈ 9.5h.

#### Step 5 — Gap Computation & Statistical Test

```python
import numpy as np
from scipy import stats

def compute_contract_strength_gap(results: dict) -> dict:
    """
    results[model][task] = list of {violated: bool, n_valid: int}
    """
    per_task_gaps = []
    
    for task_id in soundness_passed_tasks:
        test_passing_programs = [r for model in models for r in results[model][task_id] if r["passed_unit_tests"]]
        if not test_passing_programs:
            continue
        n_violated = sum(1 for r in test_passing_programs if r["violated"])
        gap = n_violated / len(test_passing_programs)
        per_task_gaps.append(gap)
    
    mean_gap = np.mean(per_task_gaps)
    
    # Bootstrap 95% CI
    bootstrap_means = [
        np.mean(np.random.choice(per_task_gaps, size=len(per_task_gaps), replace=True))
        for _ in range(10_000)
    ]
    ci_lower, ci_upper = np.percentile(bootstrap_means, [2.5, 97.5])
    
    return {
        "mean_gap": mean_gap,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n_tasks": len(per_task_gaps),
        "h_e1_passed": ci_lower > 0.01,
    }
```

**Success condition:** `ci_lower > 0.01` (bootstrap 95% CI lower bound strictly positive).

---

## 5. Metrics

| Metric | Computation | h-e1 Threshold |
|--------|-------------|----------------|
| Contract-strength gap (per task) | fraction of test-passing programs failing ≥1 contract | — |
| Mean gap (pooled) | mean over all soundness-passed tasks × all models | > 0 |
| Bootstrap 95% CI lower bound | 10k bootstrap resamplings of per-task gaps | > 0.01 (primary) |
| Per-task filter rate | valid_examples / 5000 attempted | Report distribution; flag <100/5000 |
| Quarantine rate | tasks failing soundness check / 364 | Report; expect <5% |
| Test-pass yield | programs passing unit tests / generated | Report per model |

**Secondary metric:** Does pooled mean gap replicate ≥7.42% from prior h-e1 tractable-subset result? Report as comparison.

---

## 6. Baselines

h-e1 is an existence test — no baseline comparison required for the primary gate. Baselines are used in H-M1 (oracle isolation vs. EvalPlus differential oracle). For context, report:

| Baseline | Value | Source |
|----------|-------|--------|
| h-e1 prior (tractable 25.82% subset) | 7.42% contract violation rate | Phase 4 established fact |
| ContractEval SMT-based (5 open models, Z3) | 0% contract satisfaction (all failed) | Lim et al. 2025 |
| EvalPlus differential testing additional failures | up to 23.1% vs. original HumanEval | EvalPlus NeurIPS 2023 |

---

## 7. Infrastructure & Environment

### 7.1 Dependencies

```txt
icontract>=2.7.3
icontract-hypothesis==1.1.7
hypothesis>=6.100.0
evalplus>=0.3.1
numpy>=1.24.0
scipy>=1.10.0
openai>=1.11.1
anthropic>=0.34.1
vllm>=0.5.1
transformers>=4.43.0
tqdm>=4.56.0
```

### 7.2 Hardware

| Component | Requirement |
|-----------|-------------|
| GPU | 1× A100 80GB (or 2× A40 48GB) for vLLM open models |
| CPU | 32+ cores for parallel Hypothesis PBT |
| RAM | 32GB system (vLLM model loading) |
| Storage | ~20GB (generated programs + results) |
| Runtime | ~12h total (2h soundness + 2h codegen + ~9h PBT at 32 cores) |

### 7.3 Cost Estimate

| Item | Estimate |
|------|----------|
| GPT-4o-mini (364 tasks × 10 samples) | ~$8 |
| Claude-3-haiku (364 tasks × 10 samples) | ~$12 |
| Open models (vLLM, self-hosted) | GPU time only |
| Total API cost | ~$20-30 (well within $50-100 budget) |

---

## 8. Risk Mitigation (h-e1 specific)

| Risk | Early Warning | Response |
|------|---------------|----------|
| R1: Oracle soundness failure | >5% tasks quarantined in Step 0 | Report quarantine rate; proceed on remaining set |
| R2: Low icontract-hypothesis yield | >30% tasks with filter_rate <2% (< 100/5000) | Flag tasks; compute gap on valid-example tasks only; report as limitation |
| R4: API rate limiting | >10% API errors during codegen | Reduce n_samples to 5; continue |

**Pilot recommendation (before full run):** Test Steps 0-4 on 20 randomly sampled ContractEval tasks to:
1. Measure icontract-hypothesis filter rate distribution
2. Validate contract wrapping pipeline
3. Estimate wall-clock time per task

---

## 9. Expected Outputs

### 9.1 Files

```
results/
  soundness/
    soundness_results.jsonl       # per-task soundness check outcomes
    quarantine_list.txt           # task IDs failing soundness
  generated/
    {model}/
      samples.jsonl               # raw LLM outputs
      eval_results.jsonl          # unit test pass/fail per program
  pbt/
    {model}/
      pbt_results.jsonl           # per-(task, program): {violated, n_valid, violation_input}
  analysis/
    gap_summary.json              # mean_gap, CI, n_tasks, h_e1_passed
    per_task_gaps.csv             # task-level breakdown
    filter_rate_distribution.csv  # icontract-hypothesis yield per task
```

### 9.2 Primary Result Table

```
Model               | Test-pass rate | Programs checked | Contract violations | Gap (95% CI)
GPT-4o-mini         |     XX%        |      XXXX        |        XXX          | X.XX% [X.XX, X.XX]
Claude-3-haiku      |     XX%        |      XXXX        |        XXX          | X.XX% [X.XX, X.XX]
DeepSeek-Coder-V2-Lite |  XX%        |      XXXX        |        XXX          | X.XX% [X.XX, X.XX]
CodeLlama-13B       |     XX%        |      XXXX        |        XXX          | X.XX% [X.XX, X.XX]
CodeLlama-34B       |     XX%        |      XXXX        |        XXX          | X.XX% [X.XX, X.XX]
POOLED              |     XX%        |      XXXX        |        XXX          | X.XX% [X.XX, X.XX]
```

---

## 10. Gate Decision Protocol

After computing `gap_summary.json`:

```
IF ci_lower > 0.01:
    h-e1 PASSED → proceed to H-M1 (Phase 2C for h-m1)
    
ELSE IF mean_gap > 0 but ci_lower <= 0.01:
    h-e1 BORDERLINE → investigate:
    (a) Is quarantine rate high (>15%)?
    (b) Is filter rate high for majority of tasks?
    (c) Is n_valid_examples per task too low for meaningful inference?
    Report findings; may proceed to H-M1 with caveat.
    
ELSE (mean_gap ≈ 0):
    h-e1 FAILED → STOP all H-M hypotheses
    Reassess: (a) execution-based checking tractability at scale;
              (b) icontract-hypothesis incompatibility with ContractEval contract syntax;
              (c) whether ContractEval postconditions are purely equality predicates
```

---

## 11. Research Sources

### Archon KB
**[NOT_FOUND - ARCHON]** No relevant entries found across 3 queries (property-based testing, icontract-hypothesis, ContractEval). Archon KB contains diffusion model / image generation content unrelated to code verification.

### Exa Implementation Resources

**[VERIFIED - EXA]** `mristin/icontract-hypothesis` v1.1.7
- URL: https://github.com/mristin/icontract-hypothesis
- Stars: 87 | Language: Python | License: MIT
- Key API: `test_with_inferred_strategy(fn)`, `infer_strategy(fn)`, `assume_preconditions`
- Strategy inference: bounds-matching on `int`/`float`/`datetime`, regex on `str`, `FilteredStrategy` for complex conditions
- Performance: 48ms/run (inferred strategy) vs 79ms (assume + filter)

**[VERIFIED - EXA]** `suhanmen/ContractEval` (ACL 2026 Findings)
- URL: https://github.com/suhanmen/ContractEval
- Stars: 5 | Language: Python | License: MIT
- 364 tasks with pre/postcondition contracts; SMT+LLM pipeline for evaluation
- Paper: Lim et al. 2025 — 0% contract satisfaction for 5 open-source LLMs under standard prompting

**[VERIFIED - EXA]** `evalplus/evalplus` v0.3.1 (NeurIPS 2023)
- URL: https://github.com/evalplus/evalplus
- Stars: 1789 | Language: Python | License: Apache-2.0
- Backends: openai, anthropic, vllm, hf, google, ollama
- Commands: `evalplus.codegen`, `evalplus.evaluate`, `evalplus.sanitize`
- HumanEval+: 80x test augmentation; MBPP+: 35x test augmentation

---

*Phase 2C Experiment Brief — Generated 2026-08-03*
*Hypothesis: h-e1 | Status: COMPLETED*
