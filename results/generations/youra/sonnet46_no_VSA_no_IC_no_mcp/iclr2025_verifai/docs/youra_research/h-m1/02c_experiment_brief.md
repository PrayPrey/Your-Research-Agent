# Experiment Design: H-M1

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under execution+mypy repair (Condition B, k=1..5 rounds), the mean mypy error count per problem decreases monotonically from round 1 to round 5, because LLM uses structured mypy error messages to generate subsequent repair attempts with fewer type violations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests causal step 2→3: does structured mypy feedback reduce type errors across repair rounds?

---

## Workflow Status

**Verification State:** IN_PROGRESS (ABLATION MODE)
**Prerequisites Satisfied:** H-E1 PASS (41.2% overall failing solutions have mypy-detectable type errors; HumanEval+: 70.0%)
**Gate Status:** MUST_WORK — failure stops pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (SATISFIED)

### Gate Condition
MUST_WORK: Spearman ρ < 0 (mean mypy error count per round k=1..5 must show negative correlation with round number). If this fails, the mypy feedback channel is not active and H-M2/H-M3 are blocked.

---

## Continuation Context

**Previous Hypothesis:** H-E1 (VALIDATED)

**Proven Components from H-E1:**
- EvalPlus test suite execution pipeline (functional)
- mypy invocation on generated Python code (`mypy --ignore-missing-imports --no-strict-optional`)
- GPT-4o-mini generation at temperature=0.8 for initial solutions
- HumanEval+ (164 problems) and MBPP+ (378 problems) problem sets loaded
- Primary error category confirmed: `[name-defined]` (undefined names) — 70% of HumanEval+ failing solutions

**Key Insight for H-M1:** H-E1 showed type errors are prevalent (70% on HumanEval+). H-M1 tests whether the repair loop reduces this count across rounds. The experiment reuses H-E1 infrastructure, adding a repair loop with execution+mypy feedback.

### Previous Hypothesis Results (H-E1)
- HumanEval+: 21/30 failing solutions (70.0%) have mypy-detectable type errors
- MBPP+: 0/21 failing solutions (0.0%) have mypy-detectable type errors
- Overall: 21/51 (41.2%) — gate threshold ≥10% satisfied
- Mechanism activated: True

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable — WebSearch used as fallback*

**Query 1: LLM repair loop mypy type error reduction**

- **"Is Three the Magic Number?" (arXiv:2607.05197, 2025)**
  - Finding: First 3-4 repair iterations capture most gains; later rounds show diminishing returns
  - Relevant hyperparameters: k=3-4 optimal; beyond k=5 marginal
  - Key insight: Error count reduction is concentrated in early rounds — consistent with monotonic decrease hypothesis
  - Used for: Training protocol (k=5 rounds), success criteria design

- **"How Many Tries Does It Take?" (arXiv:2604.10508, 2025)**
  - Finding: Self-repair improves pass rates +4.9 to +17.1pp on HumanEval; +16.0 to +30.0pp on MBPP
  - Error repair rates by type: name errors ~77%, syntax errors ~66%, assertion/logic errors ~45%
  - Key insight: Name errors (our dominant error category from H-E1) repair at highest rate (~77%) — supporting H-M1
  - First two rounds capture 76-95% of total achievable improvement
  - Used for: Expected baseline trajectory, success criteria

- **"LLMloop" (arXiv:2603.23613, ICSME 2025)**
  - Finding: Automated iterative feedback loop with static analysis (compilation + static analysis issues + test failures)
  - Approach: Separate loops for compilation errors, static analysis issues, test failures
  - Key insight: Static analysis as distinct feedback channel — directly validates our Condition B design
  - Used for: Experiment design (separate mypy pass from execution feedback)

**Query 2: PyTy and mypy-based LLM repair**

- **PyTy (ICSE 2024, sola-st/PyTy)**
  - Finding: LLM-based repair of Python type errors using mypy feedback
  - Approach: Initial prompt → mypy errors → repair prompt with exact error messages (line numbers + expected vs actual types)
  - Key insight: mypy error format (human-readable, line-specific) is directly usable as LLM repair prompt
  - Used for: Condition B prompt design (include full mypy stderr in repair prompt)

### Archon Code Examples

*Archon MCP unavailable — patterns derived from web research*

**Pattern 1: Repair Loop Structure (from LLMloop / Self-Debug pattern)**
```python
# Standard repair loop pattern from literature
for round_k in range(1, K+1):
    solution = llm_generate(problem, feedback=prev_feedback)
    exec_result = run_tests(solution, test_cases)
    mypy_result = run_mypy(solution)
    mypy_error_count = count_errors(mypy_result)
    # record (problem_id, round_k, mypy_error_count)
    prev_feedback = format_feedback(exec_result, mypy_result)
    if exec_result.passed:
        break
```

**Pattern 2: mypy invocation (from PyTy / standard practice)**
```python
import subprocess
result = subprocess.run(
    ["mypy", "--ignore-missing-imports", "--no-strict-optional", solution_file],
    capture_output=True, text=True
)
error_lines = [l for l in result.stdout.splitlines() if ': error:' in l]
error_count = len(error_lines)
```

### Exa GitHub Implementations

**Repository 1: Johin2/iterative-code-repair** (GitHub)
- **URL:** https://github.com/Johin2/iterative-code-repair
- **Relevance:** Direct implementation of iterative self-repair on HumanEval/MBPP with k=5 rounds
- **Architecture:** Python script, OpenAI API (GPT models), execution feedback
- **Training Config:**
  - Benchmarks: HumanEval (164), MBPP Sanitized (257)
  - Rounds: k=1..5
  - Feedback: execution errors (test failures)
  - No mypy integration (our H-M1 adds this)
- **Key finding:** Name errors repaired at ~77% across rounds — confirms our primary error type is most amenable to repair
- **Used for:** Baseline implementation pattern, per-round error tracking design

**Repository 2: sola-st/PyTy** (GitHub)
- **URL:** https://github.com/sola-st/PyTy
- **Relevance:** Mypy-driven repair — shows mypy error format fed to LLM for repair
- **Key code pattern:** Exact mypy stderr (with line:col, error message, expected type) used as repair prompt input
- **Used for:** Condition B prompt design (mypy feedback format)

**Repository 3: madaan/self-refine** (GitHub)
- **URL:** https://github.com/madaan/self-refine
- **Relevance:** General iterative self-improvement loop with feedback
- **Used for:** Confirmation of repair loop paradigm

**Serena Analysis Needed:** false — code patterns from search results are sufficiently clear

### Code Analysis (Serena MCP)

*Skipped* — Serena MCP unavailable. Code from search results (Johin2/iterative-code-repair, sola-st/PyTy) was sufficiently clear for pseudo-code generation.

---

## Experiment Specification

### Dataset

**Primary Dataset: MBPP+**
- **Name:** MBPP+ (Mostly Basic Python Problems Plus)
- **Type:** standard
- **Version:** v0.2.0 (378 problems, reduced from 399 after broken task removal)
- **Source:** EvalPlus / HuggingFace
- **Split:** Full problem set (all 378 problems used)
- **Hypothesis Fit:** MBPP+ problems have diverse Python programming tasks; higher volume (378) provides statistical power for Spearman correlation test

**Secondary Dataset: HumanEval+**
- **Name:** HumanEval+ (Human Evaluation Plus)
- **Type:** standard
- **Version:** Latest (164 problems)
- **Source:** EvalPlus / HuggingFace
- **Split:** Full problem set (all 164 problems used)
- **Hypothesis Fit:** HumanEval+ showed 70% type error rate in H-E1 — high-signal dataset for tracking error count reduction

**Synthetic Data Policy Check:** PASSED — both datasets are real, established standard benchmarks.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + evalplus package
- Identifier (MBPP+): `"evalplus/mbppplus"`
- Identifier (HumanEval+): `"evalplus/humanevalplus"`
- Code:
```python
from evalplus.data import get_mbpp_plus, get_human_eval_plus
mbpp_problems = get_mbpp_plus()   # dict: task_id -> {prompt, test, entry_point}
he_problems = get_human_eval_plus()
```

### Models

#### Baseline Model

**Architecture:** GPT-4o-mini (OpenAI API)
**Type:** API-based LLM (no local weights)
**Role in Condition B:** Generator for repair rounds

**Configuration:**
- Initial generation: temperature=0.8, 1 sample (inherited from H-E1)
- Repair rounds (k=1..5): temperature=0.0 (deterministic — enables reproducibility)
- Max tokens: 2048 per generation
- System prompt: Standard Python coding assistant

**Loading Information** (for Phase 4):
- Method: OpenAI Python SDK
- Identifier: `"gpt-4o-mini"`
- Code:
```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": repair_prompt}],
    temperature=0.0,
    max_tokens=2048
)
```

#### Proposed Model (Condition B)

**Architecture:** GPT-4o-mini + Execution feedback + mypy feedback (Condition B)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Execution+mypy Repair Loop (Condition B)
# Based on: Johin2/iterative-code-repair + PyTy pattern
import subprocess, re

def run_mypy(code_str: str, tmp_path: str) -> tuple[int, str]:
    """Run mypy on code string, return (error_count, stderr)."""
    with open(tmp_path, 'w') as f:
        f.write(code_str)
    result = subprocess.run(
        ["mypy", "--ignore-missing-imports", "--no-strict-optional", tmp_path],
        capture_output=True, text=True, timeout=10
    )
    errors = [l for l in result.stdout.splitlines() if ': error:' in l]
    return len(errors), result.stdout

def repair_loop_condition_b(problem, k_max=5):
    """Execution+mypy repair loop. Returns per-round mypy error counts."""
    solution = initial_generate(problem)  # temperature=0.8
    round_error_counts = []

    for k in range(1, k_max + 1):
        # Run EvalPlus tests
        exec_passed, exec_feedback = run_evalplus_tests(solution, problem)
        # Run mypy
        mypy_count, mypy_feedback = run_mypy(solution, f"/tmp/sol_{k}.py")
        round_error_counts.append((k, mypy_count))

        if exec_passed:
            break  # early exit on pass

        # Build repair prompt with BOTH feedback signals
        repair_prompt = build_repair_prompt(
            problem, solution, exec_feedback, mypy_feedback
        )
        solution = llm_generate(repair_prompt, temperature=0.0)

    return round_error_counts  # [(1, n1), (2, n2), ..., (k, nk)]
```

### Training Protocol

**Inherited from H-E1 (controlled comparison — only repair loop added):**

**LLM:** GPT-4o-mini (OpenAI API)
- Initial generation: temperature=0.8, top_p=1.0
- Repair rounds: temperature=0.0 (deterministic)
- Max tokens: 2048

**Repair Rounds:** k=1..5
- Source: "Is Three the Magic Number?" (arXiv:2607.05197) — first 3-4 rounds capture most gains; k=5 provides complete trajectory

**Seeds:** 1 fixed seed for initial generation (inherited from H-E1 infrastructure)
- Source: H-E1 used 3 seeds; H-M1 uses 1 seed (mechanism check, not power study)

**mypy Configuration:**
```
mypy --ignore-missing-imports --no-strict-optional <solution_file>
```
- Source: H-E1 validated this configuration; PyTy uses same flags

**Feedback Format for Repair Prompt:**
```
Problem: {problem_prompt}
Previous solution:
{previous_solution}

Execution feedback:
{test_failure_output}

Type checker (mypy) feedback:
{mypy_stderr}

Please fix the above errors and provide a corrected solution.
```

**Timeout per mypy call:** 10 seconds
**Timeout per LLM call:** 60 seconds
**Total API calls estimate:** ~7,400 (378 + 164 problems × 5 rounds × 1 seed × ~2 conditions)

**Cost estimate:** ~$10-15 (GPT-4o-mini pricing)

### Evaluation

**Primary Metrics:**

1. **Mean mypy error count per round** — `mean_errors_k` for k=1..5
   - Computed across all problems that had ≥1 mypy error at round 1
   - Mean ± std across problems for each round

2. **Spearman ρ (error count vs round number)**
   - Computed on `[mean_errors_1, mean_errors_2, ..., mean_errors_5]` vs `[1, 2, 3, 4, 5]`
   - Per dataset (MBPP+, HumanEval+) separately

**Success Criteria:**
- **Primary:** Spearman ρ < 0 (negative — error count decreases with round number) on MBPP+
- **Secondary:** Mean error count at round 5 < mean error count at round 1 on both benchmarks

**PoC Pass Condition:**
1. Code runs without error (repair loop executes k=1..5 for all problems)
2. Spearman ρ < 0 on primary dataset (MBPP+)

**Expected Baseline Performance (from research):**
- From "How Many Tries Does It Take?" (arXiv:2604.10508): first 2 rounds capture 76-95% of total error reduction
- Expected trajectory: sharp drop rounds 1→2, slower decline rounds 3→5
- Source: Johin2/iterative-code-repair results

**Metrics Loading Information** (for Phase 4):
- Task Type: correlation analysis (no ML training)
- Library: `scipy.stats.spearmanr`
- Code:
```python
from scipy.stats import spearmanr
rounds = [1, 2, 3, 4, 5]
mean_errors = [compute_mean_errors(results, k) for k in rounds]
rho, pval = spearmanr(rounds, mean_errors)
passed = rho < 0
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart — mean mypy error count per round (k=1..5) for MBPP+ and HumanEval+

#### Additional Figures (LLM Autonomous)
- **Error count trajectory:** Line plot of mean mypy error count ± std vs round k (1..5) for both datasets — primary evidence for monotonic decrease
- **Per-problem heatmap:** Heatmap (problems × rounds) of mypy error count — shows heterogeneity across problems
- **Error count distribution:** Box plots at each round (k=1..5) showing distribution of per-problem mypy error counts

> Phase 4 Coder MUST include figure generation logic. All figures saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (repair loop executes for all problems)
2. `Spearman ρ < 0` on MBPP+ (error count decreases across rounds)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | mypy repair feedback channel implemented in Condition B | TRUE — explicit mypy subprocess call in repair loop |
| Mechanism Isolatable | Can run with/without mypy output in repair prompt | TRUE — Condition A (execution-only) serves as control |
| Baseline Measurable | Round 1 mypy error count measurable independently | TRUE — mypy run after initial generation before repair |

### Architecture Compatibility Check

GPT-4o-mini via API — no architectural constraints. mypy works on any valid Python file.

**Required Features:**
- Python code generation via OpenAI API (GPT-4o-mini)
- subprocess access for mypy execution
- EvalPlus test runner

**Incompatible Architectures:** None — mechanism is API-level (prompt augmentation), not model-level modification.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"mypy_errors_round_{k}: {count}"` logged per problem per round | `repair_loop.py:repair_loop_condition_b()` |
| Error Count Delta | `mean_errors_k < mean_errors_{k-1}` for majority of rounds | `analysis.py:compute_trajectory()` |
| Metric Delta | Spearman ρ < 0 between round number and mean error count | `analysis.py:compute_spearman()` |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_mechanism_activated(round_error_counts: dict) -> tuple[bool, dict]:
    """Verify mypy feedback channel reduces error counts across rounds."""
    from scipy.stats import spearmanr
    rounds = sorted(round_error_counts.keys())
    mean_errors = [round_error_counts[k]['mean'] for k in rounds]
    rho, pval = spearmanr(rounds, mean_errors)
    indicators = {
        "log_found": all(k in round_error_counts for k in range(1, 6)),
        "rho_negative": rho < 0,
        "round5_less_than_round1": mean_errors[-1] < mean_errors[0]
    }
    activated = indicators["log_found"] and indicators["rho_negative"]
    return activated, {"rho": rho, "pval": pval, **indicators}
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (mypy errors logged for all rounds) | Log file check |
| Effect Measurable | round_5_mean < round_1_mean | Before/after comparison |
| Hypothesis Supported | Spearman ρ < 0 on MBPP+ | `scipy.stats.spearmanr` on mean error trajectory |

- **hypothesis_support_threshold:** Spearman ρ < 0 (p-value reported but not threshold; direction is sufficient for MECHANISM PoC)
- **hypothesis_support_metric:** Spearman ρ of (mean mypy error count per round) vs (round number k=1..5) on MBPP+

---

## Appendix: Reference Implementations

### A. Web Search / Knowledge Sources (Archon MCP Unavailable)

**Source 1: "Is Three the Magic Number?" (arXiv:2607.05197)**
- **Type:** Research paper (empirical study)
- **Query used:** "arxiv 'is three the magic number' LLM repair loop error count per round"
- **Relevance:** Directly characterizes iteration count behavior in LLM repair loops
- **Key Insights:**
  - First 3-4 iterations capture most improvement; diminishing returns after
  - Consistent pattern across multiple models and task types
- **Used for:** Training protocol (k=5 rounds), expected trajectory shape

**Source 2: "How Many Tries Does It Take?" (arXiv:2604.10508)**
- **Type:** Research paper
- **Query used:** "Self-Debug iterative repair LLM Python code generation HumanEval MBPP error count per round"
- **Key Insights:**
  - Name errors repaired at ~77%, syntax ~66%, assertion/logic ~45%
  - First 2 rounds capture 76-95% of total improvement
  - Self-repair universally effective on HumanEval (164) and MBPP
- **Used for:** Expected error reduction rates, benchmark selection confirmation

**Source 3: LLMloop (arXiv:2603.23613, ICSME 2025)**
- **Type:** Tool paper
- **Key Insights:**
  - Static analysis as distinct feedback channel (separate from execution)
  - Validates our Condition B design separating mypy from execution feedback
- **Used for:** Condition B feedback channel design

**Source 4: PyTy (ICSE 2024, sola-st/PyTy)**
- **Type:** Research paper + GitHub implementation
- **URL:** https://github.com/sola-st/PyTy
- **Key Insights:**
  - mypy error format (line:col + expected vs actual type) is directly usable in LLM repair prompts
  - This approach generates usable fixes
- **Used for:** Repair prompt design for Condition B; mypy subprocess invocation pattern

### B. GitHub Implementations (Exa/WebSearch)

**Repository 1: Johin2/iterative-code-repair** (GitHub)
- **URL:** https://github.com/Johin2/iterative-code-repair
- **Query used:** "Johin2 iterative-code-repair GitHub Python GPT mypy static analysis HumanEval MBPP repair rounds"
- **Relevance:** Direct implementation of k=5 repair rounds on HumanEval/MBPP with OpenAI API
- **Configuration extracted:** k=5, execution feedback, OpenAI API
- **Their results:** +4.9 to +17.1pp on HumanEval; +16.0 to +30.0pp on MBPP
- **Used for:** Baseline repair loop implementation pattern; per-round error tracking design

**Repository 2: sola-st/PyTy** (GitHub)
- **URL:** https://github.com/sola-st/PyTy
- **Relevance:** mypy-driven type error repair with LLMs
- **Key code:**
```python
# Pattern from PyTy: run mypy, feed errors back to LLM
result = subprocess.run(["mypy", "--ignore-missing-imports",
                        "--no-strict-optional", file_path],
                       capture_output=True, text=True)
errors = [l for l in result.stdout.splitlines() if ': error:' in l]
# Include errors in repair prompt
```
- **Used for:** mypy subprocess invocation, error count extraction, repair prompt design

**Repository 3: madaan/self-refine** (GitHub)
- **URL:** https://github.com/madaan/self-refine
- **Relevance:** General iterative refinement loop (validates paradigm)
- **Used for:** Confirmation of repair loop paradigm

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — Serena MCP unavailable. Code from Johin2/iterative-code-repair and sola-st/PyTy was sufficiently clear for pseudo-code generation.

### D. Previous Hypothesis Context (H-E1)

**Source:** H-E1 validation results (COMPLETED)
- **Reused Components:**
  - EvalPlus test suite runner (proven functional)
  - mypy invocation: `mypy --ignore-missing-imports --no-strict-optional` (validated)
  - GPT-4o-mini generation pipeline (established)
  - Dataset loading: `evalplus.data.get_mbpp_plus()`, `get_human_eval_plus()`
- **Why reused:** Controlled experiment — only the repair loop + mypy feedback is added; all other components held constant

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Primary dataset (MBPP+, 378 problems) | Phase 2A selection | 02b_verification_plan.md §1.3 |
| Secondary dataset (HumanEval+, 164 problems) | Phase 2A selection | 02b_verification_plan.md §1.3 |
| Dataset loading code | Web search | evalplus PyPI + HuggingFace |
| Model (GPT-4o-mini, temp=0.0 for repair) | Phase 2A selection + H-E1 | 02b_verification_plan.md §1.3; H-E1 validation |
| mypy invocation flags | H-E1 validated | H-E1 experiment code |
| Repair loop structure | GitHub (Johin2) + LLMloop | B.1, A.3 |
| mypy feedback in prompt | PyTy pattern | B.2, A.4 |
| k=5 rounds | Research papers | A.1 (Is Three Magic), A.2 (How Many Tries) |
| Error reduction trajectory shape | Research papers | A.2 (first 2 rounds = 76-95%) |
| Spearman ρ metric | Phase 2B | 02b_verification_plan.md §H-M1 |
| scipy.stats.spearmanr | stdlib | Standard Python scientific stack |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written)
**Date:** 2026-08-26

### Workflow History for This Hypothesis
- H-E1 VALIDATED: 2026-08-26 (prerequisite satisfied)
- H-M1 experiment_design.status set to IN_PROGRESS: 2026-08-26 (Phase 2C start)
- H-M1 experiment_design.status set to COMPLETED: 2026-08-26 (Phase 2C complete)

---

*MCP Tools Used: WebSearch (Archon/Exa fallback — Archon and Exa MCPs unavailable in this environment)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
