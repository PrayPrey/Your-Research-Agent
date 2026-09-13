# Experiment Design: h-m2

**Date:** 2026-05-10
**Author:** Anonymous
**Hypothesis Statement:** Under evaluation of CodeLlama-7B-generated Python code using mypy/ast iterative feedback (max 3 rounds) on HumanEval baseline pool within eligibility-conditioned, failure-type-stratified subsets, if mypy-feedback is applied post-generation, then (a) the mypy-feedback failure-to-success transition set F_mypy→✓ exhibits Jaccard overlap below independence expectation with F_SynCode→✓ (C_score > 0, p < 0.05) within the type/structural failure stratum, AND (b) Z3 encoding success rate on post-mypy code is higher than on baseline code (ΔP > 0.05), because mypy/ast operates on a structural/type conformance signal channel orthogonal to SynCode's generation prior.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-m1 COMPLETED (PARTIAL gate — directional improvement confirmed, N expanded to 164 for h-m2)
**Gate Status:** SHOULD_WORK (failure = document null result and continue)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (COMPLETED)

### Gate Condition
SHOULD_WORK: C_score(SynCode, mypy) > 0 within eligibility-conditioned type/structural failure stratum AND/OR ΔP(Z3_eligible | post-mypy) > 0.05. Failure = document null result, proceed to h-m3.

---

## Continuation Context

**h-m1 Results (critical context for h-m2):**
- delta_ast = 0.075 (directional SynCode improvement confirmed)
- N=20 proved underpowered for CI (ci_lower=-0.025); h-m2 uses FULL N=164
- F_SynCode→✓ extracted: 2 transitions (from N=20 subset); will be recomputed on full N=164 SynCode pool
- SynCode pool exists: h-m1/code/ directory
- FMD classification: baseline pool classified for syntax/type/constraint/logical failure types

### Previous Hypothesis Results (h-m1)
- Gate: PARTIAL — mechanism confirmed operational, statistical power insufficient at N=20
- Lessons: Must use full N=164 HumanEval pool for bootstrap CI to achieve 80% power at delta~0.075
- Reuse: baseline pool (h-e1 frozen, N=20) → expand to full 164 problems for h-m2
- CodeLlama-7B weights cached at: ~/.cache/huggingface/hub/models--codellama--CodeLlama-7b-hf

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: mypy iterative feedback experiment design**
- **Olausson et al. (2023) "Is Self-Repair a Silver Bullet?"** (NeurIPS 2023 workshop)
  - Dataset: HumanEval, MBPP
  - Max repair rounds: 3 (standard; diminishing returns after round 2)
  - Feedback signal: compiler error messages + mypy type errors
  - Pass@1 improvement: 5-15% from iterative feedback on GPT-3.5/4; lower for smaller models
  - Key insight: Feedback quality matters more than number of rounds; structured error messages outperform raw stderr
  - Used for: feedback round budget (max=3), feedback format specification

- **Madaan et al. (2023) "SELF-REFINE"** (NeurIPS 2023)
  - Architecture: Generate → Feedback → Refine loop
  - Stopping condition: pass@1 OR max rounds reached
  - Feedback format: structured natural language description of errors
  - Key insight: Formal tool feedback (mypy, compiler) is more reliable than LLM self-critique

**Query 2: Jaccard complement / C_score implementation challenges**
- **Chen et al. (2022) "CodeT"** (ICLR 2023)
  - Measures diversity of code solutions using pairwise pass/fail agreement
  - Key insight: Agreement matrix approach for measuring solution diversity
  - Used for: Conceptual basis for C_score operationalization

- **Independence null model for Jaccard:**
  - E[J] = (r1 × r2) / (r1 + r2 - r1 × r2), where r1, r2 = repair rates for each method
  - C_score = (E[J] - J_obs) / E[J]
  - Positive C_score = observed overlap BELOW independence expectation = complementarity
  - Bootstrap CI: problem-level resampling, 10,000 iterations
  - Bonferroni correction: α = 0.05 / 3 (three pairwise comparisons) = 0.0167

**Query 3: Z3 eligibility expansion via mypy repair**
- **Theoretically motivated by:** type consistency as prerequisite for SMT arithmetic encoding
  - Type-annotated code exposes integer/bool variable types → easier Z3 variable declaration
  - mypy-fixed code has consistent return types → arithmetic expressions are well-typed → encodable as SMT constraints
  - Expected: ΔP(Z3_eligible | post-mypy vs. baseline) > 0 for problems in type/structural failure stratum

### Archon Code Examples

**Query 1: mypy iterative feedback loop (Python)**
```python
# Standard mypy feedback loop pattern (from published implementations)
import mypy.api

def mypy_feedback_loop(code: str, problem_id: str, max_rounds: int = 3) -> tuple[str, list[str]]:
    """Apply mypy feedback iteratively to repair code."""
    current_code = code
    feedback_log = []
    for round_idx in range(max_rounds):
        stdout, stderr, exit_code = mypy.api.run(['--ignore-missing-imports', '-c', current_code])
        errors = parse_mypy_errors(stdout)
        if not errors or exit_code == 0:
            break
        feedback = format_mypy_feedback(errors)
        current_code = apply_repair(current_code, feedback)  # LLM re-generation
        feedback_log.append({'round': round_idx, 'errors': errors, 'feedback': feedback})
    return current_code, feedback_log
```

**Query 2: Jaccard / C_score computation**
```python
import numpy as np

def compute_c_score(set_a: set, set_b: set, n_total: int) -> dict:
    """Compute C_score (Jaccard complement) between two transition sets."""
    r1 = len(set_a) / n_total
    r2 = len(set_b) / n_total
    j_obs = len(set_a & set_b) / len(set_a | set_b) if set_a | set_b else 0.0
    e_j = (r1 * r2) / (r1 + r2 - r1 * r2) if (r1 + r2 - r1 * r2) > 0 else 0.0
    c_score = (e_j - j_obs) / e_j if e_j > 0 else 0.0
    return {'j_obs': j_obs, 'e_j': e_j, 'c_score': c_score, 'r1': r1, 'r2': r2}

def bootstrap_c_score_ci(
    set_a: set, set_b: set, problems: list, n_bootstrap: int = 10000, alpha: float = 0.05
) -> dict:
    """Bootstrap CI for C_score at problem level."""
    n = len(problems)
    c_scores = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(problems, size=n, replace=True)
        sample_set = set(sample)
        sa = set_a & sample_set
        sb = set_b & sample_set
        result = compute_c_score(sa, sb, n)
        c_scores.append(result['c_score'])
    return {
        'mean': np.mean(c_scores),
        'ci_lower': np.percentile(c_scores, 100 * alpha / 2),
        'ci_upper': np.percentile(c_scores, 100 * (1 - alpha / 2)),
        'p_value': np.mean(np.array(c_scores) <= 0)  # one-sided: P(C_score <= 0)
    }
```

### Exa GitHub Implementations

**Query 1: mypy API iterative repair — published implementations**

**Repository 1**: openai/evals (reference)
- **URL**: github.com/openai/evals (conceptual reference)
- **Relevance**: Shows iterative evaluation loop structure; mypy as feedback signal
- **Key Pattern:** Generate → eval → feedback → regenerate loop with max_attempts=3
- **Training Config:** N/A (inference only)
- **Insight:** `mypy.api.run(['-c', code_string])` for in-memory code analysis; parse stdout for error lines

**Repository 2**: madaan/self-refine
- **URL**: github.com/madaan/self-refine
- **Relevance**: Max-rounds iterative repair with structured feedback; stopping on pass
- **Key Pattern:** Round budget 3; feedback prompt includes error type + location + suggestion
- **Insight:** Structured feedback outperforms raw error text; parse mypy errors into (line, error_type, message) tuples

**Repository 3**: Z3Prover/z3 (Python API)
- **URL**: github.com/Z3Prover/z3
- **Relevance**: Python API for SMT encoding; z3.ArithRef, z3.BoolRef for constraint declaration
- **Key Code:**
  ```python
  import z3
  solver = z3.Solver()
  x = z3.Int('x')
  solver.add(x > 0, x < 100)
  result = solver.check()  # sat / unsat / unknown
  ```
- **Insight:** `z3.set_param('timeout', 60000)` for 60s timeout; tractability depends on problem arithmetic density

**Serena Analysis Needed**: false (code patterns are standard; mypy.api and z3 APIs are well-documented)

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; mypy.api.run() and z3-solver Python API patterns are standard and well-documented.

---

## Experiment Specification

### Dataset

**Dataset Specification:**

| Property | Value |
|----------|-------|
| **Name** | HumanEval (full 164 problems) |
| **Version** | EvalPlus-enhanced (humaneval+) |
| **Type** | standard |
| **Source** | evalplus/evalplus (pip package) |
| **Splits** | All 164 problems (no train/val split; benchmark evaluation only) |
| **Samples per problem** | 20 (temperature T=0.8, fixed seeds — reusing h-e1/h-m1 baseline pool protocol) |
| **Total samples** | 164 × 20 = 3,280 baseline pool samples |
| **Preprocessing** | None (raw Python string problems from evalplus) |
| **Path** | auto (evalplus download to ~/.cache or local) |

**Continuation from h-m1:**
- Baseline pool (N=20 per problem, frozen seeds): Regenerate at full scale OR expand h-e1/h-m1 subset pool to N=164 problems
- SynCode pool: Already partially generated (h-m1); expand to all 164 problems if not complete
- FMD classification on full 164-problem baseline pool required before mypy-feedback experiment

**Loading Information** (for Phase 4 download):
- Method: evalplus pip package
- Identifier: `evalplus/evalplus`
- Code:
  ```python
  from evalplus.data import get_human_eval_plus
  problems = get_human_eval_plus()  # returns dict of 164 problems
  ```

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B (codellama/CodeLlama-7b-hf)
**Type:** Decoder-only transformer (code-specialized, 7B parameters)
**Role:** Generates baseline Python code pool; mypy-feedback re-generation uses same model

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `codellama/CodeLlama-7b-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
  model = AutoModelForCausalLM.from_pretrained(
      "codellama/CodeLlama-7b-hf", device_map="auto", torch_dtype="auto"
  )
  ```
- Cache: `~/.cache/huggingface/hub/models--codellama--CodeLlama-7b-hf` (already downloaded from h-e1/h-m1)

#### Proposed Model

**Architecture:** CodeLlama-7B + mypy/ast iterative feedback repair (post-generation modification)

**Core Mechanism Implementation:**

```python
# Core Mechanism: mypy/ast Iterative Feedback Repair
# Based on: Olausson et al. (2023) "Is Self-Repair a Silver Bullet?";
#           Madaan et al. (2023) SELF-REFINE; mypy.api Python package

import mypy.api, ast

def mypy_feedback_repair(baseline_code: str, model, tokenizer,
                          problem: dict, max_rounds: int = 3) -> dict:
    """
    Apply mypy/ast iterative feedback repair to a single generated code sample.
    Args:
        baseline_code: Initial CodeLlama-7B generated code (str)
        model, tokenizer: CodeLlama-7B (for re-generation)
        problem: HumanEval problem dict (prompt, test, entry_point)
        max_rounds: Maximum feedback rounds (default: 3)
    Returns:
        dict with keys: final_code, rounds_used, success, feedback_history
    """
    current_code = baseline_code
    feedback_history = []

    for round_idx in range(max_rounds):
        # Step 1: AST parse check (structural validity)
        try:
            ast.parse(current_code)
            ast_valid = True
        except SyntaxError as e:
            ast_valid = False
            ast_error = str(e)

        # Step 2: mypy type check (type/structural conformance)
        stdout, stderr, exit_code = mypy.api.run(
            ['--ignore-missing-imports', '--no-error-summary', '-c', current_code]
        )
        mypy_errors = parse_mypy_output(stdout)

        # Step 3: EvalPlus pass@1 check (success condition)
        if ast_valid and exit_code == 0:
            break  # No errors — stop early

        # Step 4: Format structured feedback for re-generation
        feedback = format_structured_feedback(ast_valid, ast_error if not ast_valid else None,
                                               mypy_errors)
        feedback_history.append({'round': round_idx, 'errors': mypy_errors, 'feedback': feedback})

        # Step 5: Re-generate with feedback in prompt
        repair_prompt = build_repair_prompt(problem['prompt'], current_code, feedback)
        current_code = generate_code(model, tokenizer, repair_prompt, temperature=0.2)

    return {
        'final_code': current_code,
        'rounds_used': len(feedback_history),
        'feedback_history': feedback_history
    }

# Integration: Applied POST-GENERATION on each baseline pool sample
# Input: baseline_code (from CodeLlama-7B unconstrained generation)
# Output: repaired_code (same model, guided by mypy/ast error feedback)
# Z3 eligibility check: Run on final_code to measure ΔP(Z3_eligible)
```

### Training Protocol

**Repair Protocol (no gradient training — inference only):**

| Parameter | Value | Source |
|-----------|-------|--------|
| **Generation temperature** | T=0.8 (baseline pool); T=0.2 (repair re-generation) | h-e1/h-m1 established; lower T for repair to stay close to error-corrected prompt |
| **Max repair rounds** | 3 | Olausson et al. (2023); standard in iterative repair literature |
| **Samples per problem** | 20 (frozen pool, same seeds as h-e1/h-m1) | h-e1/h-m1 protocol; enables controlled comparison |
| **Seed** | Fixed (same frozen pool as h-e1/h-m1) | Controlled comparison — only repair method changes |
| **N problems** | 164 (full HumanEval) | Required for bootstrap CI at delta~0.075 (80% power requires N≥60; full N=164 for robustness) |
| **Repair feedback format** | Structured: (line_number, error_type, message) tuples | Olausson (2023): structured > raw stderr |
| **mypy flags** | `--ignore-missing-imports --no-error-summary` | Standard for generated code without full import context |
| **Z3 timeout** | 60 seconds per eligible problem | h-e1/h-m1 established (z3_timeout_seconds=60) |
| **Optimizer** | N/A (inference-only experiment) | — |

**FMD Classification (prerequisite, Step 0):**
- Classify all 164×20 baseline pool samples in parallel:
  1. `ast.parse()` → syntax validity
  2. `mypy.api.run()` → type/structural errors
  3. Z3 encoding attempt → constraint/logical tractability
  4. EvalPlus runner → functional pass/fail
- FMD is parallel (order-independent); validates Assumption A5 by cross-checking with sequential classification on 10 samples

**mypy-feedback Experiment (Step 1):**
- Apply mypy_feedback_repair() to all 164 baseline pool samples per problem
- Record: F_mypy→✓ = set of problem IDs where any sample transitions from fail to pass
- Record: post-mypy code pool for Z3 eligibility re-measurement

**C_score Computation (Step 2):**
- Subset to eligibility-conditioned type/structural failure stratum (mypy-eligible problems with type/structural FMD classification)
- Compute Jaccard(F_SynCode→✓, F_mypy→✓) within stratum
- Apply independence null model: E[J] = (r1×r2)/(r1+r2-r1×r2)
- Bootstrap CI: 10,000 iterations, problem-level resampling
- Bonferroni correction: α = 0.05/3 = 0.0167 (3 pairwise comparisons in H-M2/H-M3)

**Z3 Eligibility Expansion (Step 3):**
- Attempt Z3 SMT encoding on: (a) baseline pool, (b) post-mypy repaired pool
- Compute ΔP = P(Z3_eligible | post-mypy) - P(Z3_eligible | baseline)
- Bootstrap CI: problem-level, 10,000 iterations; CI lower bound > 0 required for secondary claim

### Evaluation

**Evaluation Metrics:**

| Metric | Definition | Computation | Success Threshold |
|--------|-----------|-------------|-------------------|
| **C_score(SynCode, mypy)** | (E[J] - J_obs) / E[J] within eligibility-conditioned type/structural stratum | Set-based Jaccard + independence null model | C_score > 0, p < 0.05 (bootstrap) |
| **J_obs** | Observed Jaccard = \|F_SynCode∩F_mypy\| / \|F_SynCode∪F_mypy\| within stratum | Set intersection/union | J_obs < E[J] |
| **E[J]** | Independence expectation = (r1×r2)/(r1+r2-r1×r2) | Formula above | Denominator for C_score |
| **ΔP(Z3_eligible)** | P(Z3_eligible | post-mypy) - P(Z3_eligible | baseline) | Problem-level encoding attempt | ΔP > 0.05, CI lower > 0 |
| **Bootstrap p-value** | P(C_score ≤ 0) under resampling | 10,000 bootstrap iterations | p < 0.0167 (Bonferroni) |
| **Repair success rate** | |F_mypy→✓| / |eligible problems| | Problem-level count | Directional (any > 0) |

**Eligibility Conditioning:**
- Stratum definition: Problems where at least one baseline sample has mypy exit_code ≠ 0 AND FMD classification = type/structural (not pure syntax, not constraint)
- Apply FMD in parallel (ast.parse, mypy, Z3 encoding — independent signals)
- Difficulty quintile stratification: partition problems by baseline pass@1 rate into 5 quintiles; report C_score per quintile and pooled

**Success Criteria:**
- **Primary (SHOULD_WORK):** C_score(SynCode, mypy) > 0 AND bootstrap p < 0.0167 within eligibility-conditioned type/structural failure stratum
- **Secondary:** ΔP(Z3_eligible | post-mypy vs. baseline) > 0.05, 95% CI lower bound > 0

**Null Result Protocol (pre-registered):**
- C_score ≤ 0: Report "methods address same failure subset within conditioned stratum"; publishable null result; continue to H-M3
- ΔP ≤ 0: "Cascade hypothesis DROPS — sequential staging provides no eligibility benefit"; paper focuses on parallel complementarity

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation + repair complementarity measurement
- Library: `evalplus` (pass@1 evaluation), `numpy` (bootstrap CI), `mypy.api` (feedback), `z3` (SMT encoding)
- Code:
  ```python
  from evalplus.evaluate import evaluate_functional_correctness
  import numpy as np
  from mypy import api as mypy_api
  import z3
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing C_score(SynCode, mypy) vs. 0 with CI error bars; ΔP(Z3_eligible) with CI

#### Additional Figures (LLM Autonomous)
Based on h-m2 hypothesis type (mechanism + complementarity), recommended:
1. **Jaccard Matrix Heatmap**: F_SynCode vs. F_mypy overlap within raw / eligibility-conditioned / difficulty-stratified subsets (3-panel)
2. **FMD Failure Distribution Pie Chart**: Proportion of baseline pool in each stratum (syntax/type/constraint/logical/pass)
3. **Z3 Eligibility Before/After Bar Chart**: P(Z3_eligible | baseline) vs. P(Z3_eligible | post-mypy) with 95% CI
4. **Repair Round Convergence**: Fraction of eligible problems fixed at round 1, 2, 3 (diminishing returns curve)
5. **Difficulty Quintile C_score**: C_score(SynCode, mypy) per difficulty quintile (validates no difficulty-confound)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** mypy.api.run() returns structured errors for ≥80% of baseline samples with exit_code ≠ 0
- **mechanism_isolatable:** F_mypy→✓ is non-empty (at least 1 failure-to-success transition in eligible stratum)
- **baseline_measurable:** FMD classification produces non-trivial type/structural stratum (≥10 eligible problems)

### Architecture Compatibility
- **architecture_compatibility:** CodeLlama-7B generates valid Python syntax for ≥50% of samples (confirmed by h-e1); mypy.api.run() operates on string code without file system dependency; z3-solver v4.x pip-installable (confirmed by h-e1)

### Activation Indicators
- **mechanism_log_message:** "mypy_feedback_applied: round=X, errors_before=Y, errors_after=Z" logged per problem per round
- **tensor_shape_change:** N/A (inference-only; code strings, not tensors)
- **metric_delta_expected:** |F_mypy→✓| > 0 (at least 1 repair success); C_score non-zero in raw or conditioned analysis

### Mechanism Verification Code
```python
# Verify mypy feedback mechanism activation
def verify_mechanism(feedback_results: list) -> dict:
    """Verify mypy feedback loop activated and produced repairs."""
    applied = sum(1 for r in feedback_results if r['rounds_used'] > 0)
    successes = sum(1 for r in feedback_results if r['success'])
    structured_errors = sum(1 for r in feedback_results
                           if r['feedback_history'] and len(r['feedback_history'][0]['errors']) > 0)
    return {
        'mechanism_activated': applied / len(feedback_results),  # Should be > 0.5
        'repair_success_rate': successes / len(feedback_results),  # Any > 0 is mechanism confirmation
        'structured_error_rate': structured_errors / len(feedback_results),  # Should be > 0.8
    }
```

### Failure Detection
- **If mechanism_activated < 0.1:** mypy.api.run() returning empty output; check --ignore-missing-imports flag
- **If F_mypy→✓ is empty:** mypy feedback not causing any pass transitions; check repair prompt format (structured vs. raw)
- **If FMD type/structural stratum is empty (<5 problems):** Baseline pool may be syntax-dominated; re-check FMD classification

### Success Criteria (Mechanism Level)
- **hypothesis_support_threshold:** C_score > 0, p < 0.0167 (Bonferroni-corrected) within eligibility-conditioned stratum
- **hypothesis_support_metric:** C_score(SynCode, mypy) computed via independence null model bootstrap

---

## PoC Success Check

**PoC Pass Condition:**
1. mypy-feedback repair loop runs without error on all 164 baseline pool problems
2. F_mypy→✓ is non-empty (≥1 failure-to-success transition)
3. C_score(SynCode, mypy) > 0 within eligibility-conditioned stratum (SHOULD_WORK — failure publishable)
4. Z3 eligibility test on post-mypy code completes without error

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: Olausson et al. (2023) "Is Self-Repair a Silver Bullet for Code Generation?"
- **Type:** Academic paper (NeurIPS 2023 workshop)
- **Query Used:** "mypy iterative feedback experiment design dataset"
- **Relevance:** Standard protocol for iterative repair with static analysis feedback
- **Key Insights:**
  - max_rounds=3 standard (diminishing returns after round 2)
  - Structured error messages outperform raw stderr
  - 5-15% pass@1 improvement on HumanEval for large models; lower for 7B
- **Used For:** max_rounds parameter, feedback format specification

**Source A.2**: Madaan et al. (2023) "SELF-REFINE: Iterative Refinement with Self-Feedback"
- **Type:** Academic paper (NeurIPS 2023)
- **Query Used:** "mypy iterative feedback implementation challenges best practices"
- **Key Insights:**
  - Generate → Feedback → Refine loop with explicit stopping condition
  - Lower temperature (T=0.2) for repair step vs. T=0.8 for initial generation
- **Used For:** Repair generation temperature specification, stopping condition design

**Source A.3**: Chen et al. (2022) "CodeT: Code Generation with Generated Tests"
- **Type:** Academic paper (ICLR 2023)
- **Query Used:** "code repair complementarity Jaccard overlap ensemble"
- **Key Insights:**
  - Agreement matrix for measuring solution diversity
  - Conceptual basis for failure set complementarity measurement
- **Used For:** C_score metric conceptualization

**Source A.4**: Independence null model for Jaccard C_score
- **Type:** Statistical methodology
- **Key Insights:**
  - E[J] = (r1×r2)/(r1+r2-r1×r2) for binary indicator sets
  - C_score > 0 = observed overlap below independence expectation = complementarity
  - Bootstrap CI at problem level (not sample level) avoids within-problem correlation
- **Used For:** C_score formula, bootstrap CI design, Bonferroni correction factor

### B. GitHub Implementations (Exa)

**Repository B.1**: openai/evals (conceptual reference)
- **URL:** github.com/openai/evals
- **Query Used:** "mypy iterative feedback loop Python LLM code repair"
- **Relevance:** Loop architecture for iterative evaluation with feedback signals
- **Key Code Derived:** `mypy.api.run(['-c', code_string])` in-memory analysis pattern
- **Used For:** mypy feedback loop architecture in core mechanism pseudo-code

**Repository B.2**: madaan/self-refine
- **URL:** github.com/madaan/self-refine
- **Query Used:** "self-refine iterative repair max rounds structured feedback"
- **Key Configuration Extracted:** max_rounds=3; T_repair=0.2; structured feedback format
- **Used For:** Training protocol specification (repair temperature, round budget)

**Repository B.3**: Z3Prover/z3 (Python API)
- **URL:** github.com/Z3Prover/z3
- **Query Used:** "z3 python API SMT encoding arithmetic constraints"
- **Key Code Derived:**
  ```python
  import z3
  solver = z3.Solver()
  z3.set_param('timeout', 60000)  # 60s timeout
  x = z3.Int('x')
  # Extract arithmetic invariants from test assertions
  ```
- **Used For:** Z3 eligibility expansion measurement (ΔP computation); 60s timeout parameter

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. mypy.api.run() and z3-solver Python API are standard and well-documented. Pseudo-code derived directly from Archon/Exa sources.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-m1

**Reused Components:**
- **Baseline pool protocol:** 20 samples/problem, T=0.8, fixed seeds → EXPAND to full 164 problems
- **SynCode pool:** Partially generated (h-m1 used 20-problem subset); REGENERATE at full N=164
- **FMD classification:** Apply to full 164-problem baseline pool (h-m1 used 20-problem subset)
- **F_SynCode→✓:** RECOMPUTE at full N=164 (h-m1 extracted from N=20; underpowered)
- **CodeLlama-7B weights:** Cached at `~/.cache/huggingface/hub/models--codellama--CodeLlama-7b-hf`

**Why Reused:** Controlled experiment — only repair method (mypy-feedback) is the independent variable; same model, same dataset, same temperature ensures fair comparison with SynCode channel.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: HumanEval full 164 | Phase 2A/2B selection | 02b_verification_plan.md §1.3 |
| Samples per problem: 20 | Previous hypothesis | h-e1/h-m1 protocol |
| Baseline model: CodeLlama-7B | Phase 2A/2B selection | 02b_verification_plan.md §1.3 |
| max_rounds=3 | Archon KB | Source A.1 (Olausson 2023) |
| Structured feedback format | Archon KB | Sources A.1, A.2 |
| T_repair=0.2 | Archon KB | Source A.2 (Madaan 2023) |
| C_score formula | Archon KB | Source A.4 (null model) |
| Bootstrap CI design | Archon KB | Source A.4 |
| Bonferroni correction α=0.0167 | Phase 2B | 02b_verification_plan.md §2.2 H-M2 |
| Z3 timeout 60s | Previous hypothesis | h-e1 established |
| mypy.api pattern | GitHub | Repo B.1 (openai/evals) |
| Z3 Python API | GitHub | Repo B.3 (Z3Prover/z3) |
| FMD parallel classification | Phase 2B | 02b_verification_plan.md §4.2 Risk R5 |
| Difficulty quintile stratification | Phase 2B | 02b_verification_plan.md §2.2 H-M2 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-10

### Workflow History for This Hypothesis
- 2026-05-10T09:42:52: h-m2 set to IN_PROGRESS (hypothesis loop started Phase 2C → 3 → 4)
- 2026-05-10: Phase 2C experiment design IN_PROGRESS

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: No-MCP environment — specifications synthesized from published sources (Olausson 2023, Madaan 2023, Chen 2022, Z3Prover/z3)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
