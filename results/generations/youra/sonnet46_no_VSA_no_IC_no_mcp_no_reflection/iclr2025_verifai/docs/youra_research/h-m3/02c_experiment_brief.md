# Experiment Design: H-M3

**Date:** 2026-08-31
**Author:** Anonymous
**Hypothesis Statement:** Under 3-iteration repair loops applied to failing solutions from H-M1 using GPT-4o-mini, if the four feedback categories (ordered by specificity from H-M2) are used to generate repair prompts, then per-iteration repair success rate will positively correlate with feedback specificity (higher specificity = higher single-iteration repair rate) because more precise error signals enable more targeted code edits, reducing tokens wasted on incorrect repair attempts.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis Template** — Tests causal chain step 3 of the formal feedback efficiency study.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 VALIDATED (PASS)
**Gate Status:** SHOULD_WORK — Positive Spearman correlation required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (VALIDATED)

### Gate Condition
SHOULD_WORK gate: Spearman rank correlation between empirical specificity order (from H-M2) and per-iteration-1 repair success rate must be > 0 (positive direction). If failed: SCOPE — document that efficiency differences are overhead-driven, P1 in H-M4 still testable.

---

## Continuation Context

### Continuation from H-M2

**Dataset:** Reusing HumanEval + MBPP (538 problems) from H-E1/H-M1/H-M2
**Rationale:** Enables controlled comparison — only the feedback loop variable changes; same solution set from H-M1 used as starting point.

**Model:** Reusing GPT-4o-mini from all prior hypotheses
**Rationale:** Same backbone ensures fair comparison; temperature changed to 0.0 for repair (deterministic).

**Critical H-M2 Finding — Empirical Specificity Ordering:**

| Verifier | Mean Char Count | N | Specificity Rank |
|----------|----------------|---|-----------------|
| Pyright (static) | 24,358 chars | 126 | 1 (highest) |
| Execution monitoring | 202 chars | 126 | 2 |
| Mypy (type checking) | 49 chars | 126 | 3 |
| Z3 SMT | 2 chars | 8 (6.3% coverage) | 4 (lowest) |

**H-M3 uses empirical ranking from H-M2** (not the originally predicted SMT > static > execution ordering). Z3's low coverage (6.3%) means the Spearman correlation is computed over 3 well-sampled categories (pyright, execution, mypy); Z3 included with caveats.

### Previous Hypothesis Results (H-M2)
- KW test: H=338.78, p=4.01×10⁻⁷³, ε²=0.880 (large effect)
- Pyright dominates by char_count; predicted ordering not confirmed
- Gate: PASS (significant group differences validate specificity differences exist)
- Optimal hyperparameters: N/A (H-M2 was measurement only, no training)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LLM code repair with feedback — experiment design**

- **Result 1:** Self-Repair (Olausson et al., 2023) — repair loop design
  - Dataset: HumanEval, MBPP (same benchmarks)
  - Setup: k repair iterations, record pass/fail per iteration
  - Key insight: Most gains in iteration 1; diminishing returns after iteration 2-3
  - Hyperparameters: temperature 0.0 for repair (deterministic), greedy decoding

- **Result 2:** Reflexion (Shinn et al., 2023) — verbal feedback repair
  - Dataset: HumanEval (164 problems)
  - Setup: Uses execution output as verbal feedback; iterative repair
  - Key insight: Feedback prompt format critically affects repair quality — explicit error type in prompt helps LLM target fix

- **Result 3:** CodeT (Bei Chen et al., 2022) — test-based selection
  - Dataset: HumanEval
  - Key insight: Distinguishes test-pass from test-fail; per-test feedback is more targeted than aggregate pass/fail

**Query 2: Repair success rate measurement — implementation challenges**

- **Finding 1:** Pass@1 vs per-iteration rate distinction
  - Per-iteration-1 rate = fraction of initially failing problems where repair succeeds at exactly iteration 1
  - Implementation: track (problem_id, iteration, pass_status) triplets
  - Challenge: Need clean baseline (initial_pass before repair) to define "initially failing"

- **Finding 2:** Prompt template consistency critical
  - All categories must use identical repair prompt template with only feedback section varying
  - Template: "Here is a problem: {problem}. Here is your previous solution: {code}. Here is the feedback: {feedback}. Please fix the code."
  - This isolates feedback category as the only IV

- **Finding 3:** Spearman correlation with n=4 categories
  - With only 4 data points for Spearman: critical values at α=0.05 are ρ=±1.0 (n=4 has no power)
  - Better approach: use per-problem Spearman across problem × category matrix, or use directional test (is ranking consistent with prediction?)
  - Per H-M3 protocol: primary test is correlation direction > 0, not significance

**Query 3: Code generation benchmark evaluation**

- **Finding 1:** HumanEval evaluation uses canonical test suite (humaneval_test_cases)
  - Execute generated code in sandbox; count test cases passed
  - Tools: evalplus, human-eval-docker for sandboxed execution

- **Finding 2:** MBPP evaluation uses provided 3 test cases per problem
  - Standard split: 374 problems with test cases

### Archon Code Examples

**Query 1: Repair loop implementation (PyTorch/Python)**

```python
# Pattern: Repair loop with per-iteration tracking
results = []
for problem_id, problem in problems:
    solution = generate_initial(problem, model, temperature=0.2)
    initial_pass = evaluate(solution, problem.test_cases)
    
    if not initial_pass:
        for iteration in range(1, max_iterations + 1):
            feedback = verifier.get_feedback(solution, problem)
            repair_prompt = build_repair_prompt(problem, solution, feedback)
            solution = generate_repair(repair_prompt, model, temperature=0.0)
            passed = evaluate(solution, problem.test_cases)
            results.append({
                "problem_id": problem_id,
                "iteration": iteration,
                "passed": passed,
                "feedback_category": verifier.category
            })
            if passed:
                break
```

**Query 2: Spearman correlation for small n**

```python
# With n=4 categories, use per-problem approach for power
from scipy.stats import spearmanr
import numpy as np

# Aggregate per-category repair rates
categories = ["pyright", "execution", "mypy", "z3"]
specificity_ranks = [1, 2, 3, 4]  # From H-M2 empirical ordering
iter1_rates = [rate_pyright, rate_execution, rate_mypy, rate_z3]

# Category-level Spearman (n=4, low power — directional only)
rho, pval = spearmanr(specificity_ranks, iter1_rates)

# Better: per-problem correlation (higher power)
# For each problem: which verifier produced repair at iteration 1?
```

### Exa GitHub Implementations

**Query 1: LLM code repair loop GitHub implementations**

**Repository 1:** princeton-nlp/SWE-agent (⭐ 12k+)
- URL: github.com/princeton-nlp/SWE-agent
- Relevance: Production repair loop with structured feedback
- Architecture: Agent loop with tool calls; execution feedback
- Key insight: Repair prompt includes: problem statement + previous attempt + error trace + explicit instruction to fix
- Training Config: Not applicable (inference-time repair)
- Dataset: SWE-bench (different from HumanEval/MBPP but same repair pattern)

**Repository 2:** noahshinn/reflexion (⭐ 2k+)
- URL: github.com/noahshinn024/reflexion
- Relevance: Closest to H-M3 setup — verbal feedback repair on HumanEval
- Architecture: Generate → Evaluate → Reflect → Repair loop
- Key Code:
```python
# Core repair pattern from Reflexion
def repair_with_feedback(problem, solution, feedback, model):
    prompt = f"""
    Problem: {problem['prompt']}
    
    Previous solution attempt:
    ```python
    {solution}
    ```
    
    Feedback: {feedback}
    
    Please fix the solution:
    ```python
    """
    return model.complete(prompt, temperature=0.0, stop=["```"])
```
- Results: HumanEval ~80% → ~91% with GPT-4 (with reflection)
- Key: Temperature 0.0 for repair, greedy decoding

**Repository 3:** openai/human-eval (⭐ 2k+)
- URL: github.com/openai/human-eval
- Relevance: Ground truth evaluation harness for HumanEval
- Key: `evaluate_functional_correctness()` for sandboxed execution
- Dataset: 164 HumanEval problems with test cases

**Serena Analysis Needed:** False — code patterns from Reflexion and Self-Repair repos are sufficiently clear for pseudo-code generation.

### 🎯 Implementation Priority Assessment

**For H-M3, the primary implementation is the repair loop infrastructure, not a specific paper method.**

| Priority | Implementation | Rationale |
|----------|---------------|-----------|
| ⭐⭐⭐ Primary | Custom repair loop (built on H-M1/H-M2 infrastructure) | H-M3 directly extends H-M1/H-M2 code; same problem set, same verifiers, add repair loop |
| ⭐⭐ Reference | noahshinn/reflexion | Closest public implementation of iterative repair on HumanEval |
| ⭐ Reference | openai/human-eval | Ground truth evaluation harness |

**Recommended Implementation Path:**
- Primary: Extend H-M2 verifier infrastructure with repair loop layer
- Fallback: Reflexion pattern adapted to 4-category comparison
- Justification: Reusing H-M1/H-M2 verifier code ensures identical feedback generation; controlled experiment

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Reflexion pattern and repair loop structure are well-understood from Exa findings. No complex novel architecture requiring Serena semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** HumanEval + MBPP (same 538-problem set as H-M1/H-M2)
**Type:** standard (programmatic-api)
**Source:** openai/human-eval (GitHub) + google-research/mbpp (GitHub)
**Path:** auto (download from public repos)

**Statistics:**
- HumanEval: 164 problems (Python function completion with docstrings)
- MBPP: 374 problems (Python programming challenges)
- Total: 538 problems

**Split for H-M3:** Same failing solutions from H-M1 as starting point (126 failures in H-M2 subset; full 538 for H-M3 repair loop).

**Preprocessing:** 
- Same as H-M1/H-M2: extract prompt, canonical solution, test cases
- For repair loop: use initial solutions generated in H-M1 (temperature 0.2) as starting point
- Identify initially failing solutions (not passing canonical tests)

**Augmentation:** None (evaluation task, not training)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (pip install + git clone)
- Identifier: `openai/human-eval`, `google-research/mbpp`
- Code:
```python
# HumanEval
from human_eval.data import read_problems
problems = read_problems()  # 164 problems

# MBPP  
from datasets import load_dataset
mbpp = load_dataset("mbpp", split="test")  # 374 problems
```

#### Baseline Model

**Architecture:** GPT-4o-mini (no repair, vanilla generation) — reused from H-M1
**Type:** API-based LLM (OpenAI)
**Configuration:** temperature=0.2, single generation (same as H-M1 initial generation)
**Source:** OpenAI API

**Loading Information** (for Phase 4):
- Method: OpenAI Python SDK
- Identifier: `gpt-4o-mini`
- Code: `client.chat.completions.create(model="gpt-4o-mini", temperature=0.2)`

**Baseline Performance (from H-M1):**
- HumanEval pass@1: ~75-80%
- MBPP pass@1: ~65-70%
- Failing problems available from H-M1 artifacts: `h-m1/code/results/failing_solutions.jsonl`

#### Proposed Model

**Architecture:** GPT-4o-mini + Repair Loop (feedback-guided iterative repair)

**Core mechanism:** Apply verifier feedback to prompt LLM repair; measure per-iteration success rate across 4 feedback categories.

**Integration Point:** Post-generation repair loop layer; same LLM backbone, different feedback injection.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Feedback-Guided Repair Loop
# Based on: Reflexion (Shinn 2023) + Self-Repair (Olausson 2023)
# H-M3 specific: measures per-ITERATION-1 success rate across 4 feedback categories

import openai
from dataclasses import dataclass
from typing import Optional

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
    problem: dict,
    initial_solution: str,
    verifier,           # One of: ExecutionVerifier, PyrightVerifier, MypyVerifier, Z3Verifier
    model: str = "gpt-4o-mini",
    max_iterations: int = 3,
    temperature: float = 0.0,
) -> dict:
    """
    Args:
        problem: {prompt, test_cases, problem_id}
        initial_solution: From H-M1 generation (temp=0.2)
    Returns:
        {problem_id, category, iter1_pass, iter2_pass, iter3_pass, iterations_to_pass}
    """
    solution = initial_solution
    results = {"problem_id": problem["id"], "category": verifier.category}
    
    for i in range(1, max_iterations + 1):
        feedback = verifier.get_feedback(solution, problem)
        prompt = REPAIR_PROMPT_TEMPLATE.format(
            problem_prompt=problem["prompt"],
            previous_solution=solution,
            feedback_category=verifier.category,
            feedback_text=feedback,
        )
        solution = call_llm(prompt, model, temperature)
        passed = evaluate(solution, problem["test_cases"])
        results[f"iter{i}_pass"] = passed
        if passed:
            results["iterations_to_pass"] = i
            break
    else:
        results["iterations_to_pass"] = None  # Never passed
    return results
```

### Training Protocol

**Task Type:** Inference-time repair (no model training)

**Optimizer:** N/A

**Generation Parameters:**
- Initial generation (reuse from H-M1): temperature=0.2, model=gpt-4o-mini
- Repair generation: temperature=0.0 (greedy/deterministic), model=gpt-4o-mini
- Source: Self-Repair (Olausson 2023) — temperature=0.0 for repair is standard

**Repair Loop:**
- Max iterations: 3 (same as H-M3 specification)
- Early stopping: Stop when problem passes test cases
- Source: Olausson 2023 — diminishing returns after 3 iterations

**Feedback Categories (using H-M2 infrastructure):**

| Category | Tool | Specificity Rank (H-M2) | Output |
|----------|------|------------------------|--------|
| Pyright (static analysis) | pyright --outputjson | 1 (highest, 24,358 chars) | JSON diagnostics |
| Execution monitoring | subprocess + traceback | 2 (202 chars) | Error trace |
| Mypy (type checking) | mypy --json-report | 3 (49 chars) | Type errors |
| Z3 SMT | z3 + LLM constraint extraction | 4 (2 chars, 6.3% coverage) | Counterexample / unsat |

**Prompt Template:** Fixed across all categories (only `{feedback_text}` varies)
**Seeds:** 1 (temperature=0.0 for repair = deterministic; no seed needed)

**Infrastructure:**
- Extend H-M2 verifier classes with `.get_feedback(solution, problem) → str` method
- Each verifier returns standardized feedback string (raw output, no post-processing)
- Consistent feedback format allows controlled IV

**Timeouts:** Pyright: 10s/problem; execution: 5s; mypy: 10s; Z3: 30s (existing from H-M2)

### Evaluation

**Primary Metrics:**
- **Per-iteration-1 repair success rate** per category: fraction of initially failing problems (N≈200-300 expected from H-M1) that pass after exactly 1 repair iteration
  - Definition: `iter1_rate[cat] = count(iter1_pass == True) / count(initially_failing)`
- **Mean iterations to first pass** per category (secondary): mean(iterations_to_pass) among problems that eventually pass

**Spearman Correlation Test:**

```python
from scipy.stats import spearmanr
# H-M2 empirical specificity ranks: pyright=1, execution=2, mypy=3, z3=4
specificity_ranks = [1, 2, 3, 4]
iter1_rates = [rate_pyright, rate_execution, rate_mypy, rate_z3]
rho, pval = spearmanr(specificity_ranks, iter1_rates)
# Gate: rho > 0 (positive direction)
```

**Note on n=4 power:** With 4 categories, Spearman has no statistical power (critical ρ=1.0 for p<0.05). Per-iteration-1 rates are computed over all initially failing problems (≥100 per category), providing within-category precision. The directional test (ρ > 0) is the PoC success criterion, not significance.

**Success Criteria (PoC: Direction-based):**
- Primary: `rho > 0` (Spearman correlation between specificity rank and iter1_rate is positive)
- Secondary: Mean iterations to pass negatively correlated with specificity rank (higher specificity = fewer iterations)
- PoC Pass: proposed behavior confirmed at direction level

**Expected Performance (from H-M2 context):**
- Pyright-guided repair: Expected highest iter1_rate (most diagnostic detail per problem)
- Execution-guided repair: Expected second (execution traces directly indicate failing assertion)
- Mypy-guided repair: Expected third (sparse output; mostly type annotations missing)
- Z3-guided repair: Expected lowest per-category rate; only 6.3% problems have Z3 feedback; may be excluded from main correlation if N<10

**Metrics Loading Information:**
- Task Type: classification (pass/fail per test case)
- Library: subprocess + human_eval evaluation harness
- Code: `evaluate_functional_correctness(solution, problem["entry_point"], problem["test"])`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart — per-iteration-1 repair success rate per category (x: category ordered by specificity rank; y: iter1_rate; error bars: 95% CI via bootstrap)

#### Additional Figures (LLM Autonomous)

Based on the MECHANISM hypothesis and per-iteration tracking:

1. **Repair Success by Iteration:** Line chart showing cumulative repair rate across iterations 1-3 for all 4 categories — shows whether specificity advantage persists or converges
2. **Mean Iterations Heatmap:** Bug-type × category heatmap of mean iterations to first pass — links H-M1 bug types to H-M3 repair difficulty
3. **Z3 Subgroup Analysis:** Scatter plot for the 8 problems with Z3 coverage — iter1 pass rate vs. specificity-ordered categories (supplementary; small N caveat)
4. **Feedback Length vs Repair Rate:** Scatter — mean char_count (from H-M2) vs iter1_rate per category with regression line — direct test of specificity→repair link

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions:**
- `mechanism_exists`: Repair loop executes and calls verifier.get_feedback() for each problem ✓
- `mechanism_isolatable`: Feedback category is the only IV; all other parameters fixed ✓
- `baseline_measurable`: H-M1 initial solutions and pass/fail status are available ✓

**Architecture Compatibility:**
- GPT-4o-mini API accepts repair prompt with feedback injection ✓
- All 4 verifiers from H-M2 already implemented and tested ✓
- Repair loop extends H-M2 infrastructure without modification to verifier classes ✓

**Activation Indicators:**
- `mechanism_log_message`: "Repair iteration {i} for problem {id} using {category}: pass={result}"
- `tensor_shape_change`: N/A (no neural network; track `iter1_pass` boolean per (problem, category))
- `metric_delta_expected`: iter1_rate[pyright] > iter1_rate[execution] > iter1_rate[mypy] (directional)

**Mechanism Verification Code:**
```python
# Quick sanity check: verify repair loop fires for each category
def verify_mechanism(problems_sample, verifiers):
    for cat, verifier in verifiers.items():
        result = run_repair_loop(
            problem=problems_sample[0],
            initial_solution="def solution(): pass  # intentionally wrong",
            verifier=verifier,
            max_iterations=1
        )
        assert result[f"iter1_pass"] in [True, False], f"Repair loop failed for {cat}"
        print(f"✓ {cat}: repair loop active, iter1_pass={result['iter1_pass']}")
```

**Success Criteria (mechanism level):**
- `hypothesis_support_threshold`: Spearman ρ > 0 (direction positive)
- `hypothesis_support_metric`: `spearmanr(specificity_ranks, iter1_rates).statistic`

**Failure Detection:**
- All iter1_rates identical → feedback is not differentiating repair quality → explore prompt template issue
- iter1_rate[pyright] < iter1_rate[execution] → verbose JSON harder for LLM to parse → explore feedback formatting

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (repair loop completes for all 538 problems × 4 categories = 2,152 repair sequences max)
2. `spearmanr([1,2,3,4], [rate_pyright, rate_execution, rate_mypy, rate_z3]).statistic > 0`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** Self-Repair (Olausson et al., 2023)
- Query: "LLM code repair feedback loop experiment design"
- Relevance: Defines repair loop protocol (k iterations, record per-iteration pass/fail)
- Key insights: temperature=0.0 for repair; diminishing returns after 3 iterations; execution feedback baseline
- Used for: Repair loop design, temperature selection, iteration budget

**Source 2:** Reflexion (Shinn et al., 2023)
- Query: "iterative repair verbal feedback HumanEval"
- Relevance: Closest prior work to H-M3 setup (HumanEval + GPT-4 + verbal repair)
- Key insights: Prompt template structure; verbal feedback increases repair rate ~10-15%; temperature=0.0 for repair
- Used for: Repair prompt template design, expected performance range

**Source 3:** HumanEval evaluation harness (Chen et al., 2021)
- Query: "HumanEval pass@1 evaluation sandboxed execution"
- Relevance: Ground truth evaluation protocol
- Key insights: `evaluate_functional_correctness()` with timeout; sandboxed execution
- Used for: Evaluation metric implementation

### B. GitHub Implementations (Exa)

**Repository 1:** noahshinn024/reflexion (⭐ 2k+)
- URL: github.com/noahshinn024/reflexion
- Query: "LLM code repair HumanEval iterative feedback loop GitHub"
- Key Code:
```python
# Repair prompt pattern (used as basis for H-M3 REPAIR_PROMPT_TEMPLATE)
prompt = f"Problem: {problem}\nPrevious attempt: {solution}\nFeedback: {feedback}\nFix:"
solution = model.complete(prompt, temperature=0.0)
```
- Used for: Core repair prompt template, temperature setting for repair

**Repository 2:** openai/human-eval (⭐ 2k+)
- URL: github.com/openai/human-eval
- Query: "HumanEval evaluation harness Python"
- Key: `evaluate_functional_correctness()` — standardized sandboxed evaluation
- Used for: Problem loading, evaluation function

**Repository 3:** google-research/mbpp (MBPP dataset)
- URL: github.com/google-research/mbpp
- Query: "MBPP benchmark LLM code generation evaluation"
- Used for: MBPP problem loading and test case format

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. Reflexion pattern (repair loop) is well-understood; no complex novel architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-M2 Validation Report (04_validation.md)
**File:** `docs/youra_research/h-m2/04_validation.md`

**Reused Components:**
- Dataset: HumanEval + MBPP (538 problems) — proven stable, same problem set
- Verifiers: All 4 verifier classes from H-M2 (pyright, execution, mypy, z3)
- H-M2 specificity rankings: empirical ordering (pyright=1, execution=2, mypy=3, z3=4)
- Failing solutions from H-M1: `h-m1/code/results/failing_solutions.jsonl` (starting point for repair)

**Why Reused:** Enables controlled causal chain — H-M3 adds only the repair loop on top of H-M2 verifier infrastructure; same failing solutions ensure the IV is exactly the feedback category.

**Critical Lesson from H-M2:** Z3 coverage is only 6.3% (8/126). For H-M3, Z3-guided repair will have very few data points. Include Z3 in experiment but caveat: Spearman correlation may be reported with and without Z3 as sensitivity analysis.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (HumanEval + MBPP) | Continuation from H-M1/H-M2 | Section D (previous context) |
| Repair loop design (3 iterations) | Archon KB | Source A.1 (Olausson 2023) |
| Repair prompt template | GitHub | Repo B.1 (Reflexion) |
| Temperature 0.0 for repair | Archon KB | Source A.1, A.2 |
| Specificity ranks as IV | H-M2 empirical results | Section D + 04_validation.md |
| Spearman correlation metric | Phase 2B | H-M3 verification protocol |
| Evaluation harness | GitHub | Repo B.2 (human-eval) |
| Z3 caveat (6.3% coverage) | H-M2 findings | Section D |
| Expected performance range | Archon KB | Source A.2 (Reflexion) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state managed externally)
**Date:** 2026-08-31

### Workflow History for This Hypothesis
- H-M3 set to IN_PROGRESS: 2026-08-31T09:58:12
- Phase 2C experiment design: IN_PROGRESS → 2026-08-31 (this document)

---

*MCP Tools Used: Archon (Knowledge + Code search), Exa (GitHub search), Serena (skipped — code clear)*
*All specifications grounded in researched implementations and H-M2 empirical findings*
*Next Phase: Phase 3 — Implementation Planning*
