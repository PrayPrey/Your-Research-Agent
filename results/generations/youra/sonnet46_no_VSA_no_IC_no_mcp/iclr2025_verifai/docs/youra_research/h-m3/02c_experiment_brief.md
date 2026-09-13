# Experiment Design: h-m3

**Date:** 2026-08-26
**Author:** Anonymous
**Hypothesis Statement:** On full HumanEval+ (164) and MBPP+ (378) with GPT-4o-mini, Condition B (execution+mypy, k=5) achieves strictly higher pass@1 averaged over k=1..5 rounds than Condition A (execution-only, k=5), because structured type-error signal enables more targeted repairs than binary execution pass/fail.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (MUST_WORK) Template** — Primary empirical test of main hypothesis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m2 (SHOULD_WORK gate, FAILED — limitation recorded; ceiling effect on type-error category; continuing per SHOULD_WORK policy)
**Gate Status:** MUST_WORK — p < 0.05 on MBPP+; absolute pass@1 improvement ≥ 1%

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (SHOULD_WORK, completed with limitation)

### Gate Condition
MUST_WORK — Condition B (execution+mypy, k=5) must achieve strictly higher pass@1 averaged over k=1..5 rounds than Condition A (execution-only, k=5) on MBPP+ (p < 0.05, absolute delta ≥ 1%). Failure: PIVOT or ABANDON.

---

## Continuation Context

h-m3 is the primary empirical test of the main hypothesis. Prerequisites:
- **h-e1 (VALIDATED):** ≥10% of failing solutions have ≥1 mypy error on both benchmarks — sufficient mypy signal density exists.
- **h-m1 (VALIDATED):** Spearman ρ < 0 confirmed — mypy error count decreases monotonically across repair rounds — LLM incorporates mypy feedback (mechanism is active).
- **h-m2 (FAILED, SHOULD_WORK):** Ceiling effect (90.9%/90.9%) on type-error-specific repair rate. Primary confound target: extra-context-length in Condition B. This does not preclude aggregate pass@1 gains in h-m3.

**Key insight from h-m2:** The ceiling effect is per-category (type-error problems). h-m3 measures net pass@1 across all problem categories, where the mypy signal may still produce measurable aggregate improvement. The extra-context-length confound identified in h-m2 should be controlled: log token counts per condition to distinguish signal from context-length effect.

### Previous Hypothesis Results (if applicable)
- h-m1: Spearman ρ = negative (confirmed). Optimal hyperparameters: GPT-4o-mini, temperature=0.0 for repair rounds, k=5, execution feedback provided alongside mypy in Condition B.
- h-m2: repair_rate_type_A=90.9%, repair_rate_type_B=90.9%, delta_type=0.000. Route: EXPLORE (extra-context-length confound primary target).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Note: Archon MCP unavailable in this session. Findings derived from web search and domain knowledge.*

**Query 1: LLM Code Repair Loop — Experiment Design**
- **"How Many Tries Does It Take?" (arxiv 2604.10508, 2026):**
  - Dataset: HumanEval (164) and MBPP Sanitized (257 problems), up to 5 repair attempts
  - Improvement: +4.9 to +17.1 pp on HumanEval; +16.0 to +30.0 pp on MBPP across 7 models
  - Feedback type: execution error messages (no static analysis condition)
  - Key insight: Most gains concentrate in first 2 rounds; self-repair is a robust property of modern LLMs
  - Hyperparameters: temperature=0 (greedy) for repair rounds, greedy decoding for reproducibility

- **LLMloop (arxiv 2603.23613, 2026):**
  - Dataset: HumanEval-X (Java, 164 problems)
  - Feedback types: compilation errors, test failures, static analysis (PMD), test generation, mutation analysis
  - Model: GPT-4o-mini, adaptive temperature (start 0.0, +0.1 per retry)
  - Improvement: baseline 71.65% → LLMloop 80.85% pass@1 (+9.2 pp)
  - Key insight: Compilation/static analysis loop first; later stages diminish. Static analysis adds signal beyond execution.

- **Self-Repair is Not a Silver Bullet (ICLR 2024):**
  - Self-repair gains are often modest when cost is considered; vary within and between datasets
  - Diversity in initial programs matters for self-repair effectiveness

**Query 2: mypy as Repair Signal**
- **"Automated Type Annotation in Python Using LLMs" (arxiv 2508.00422, 2025):**
  - Generate–check–repair loop driven by mypy type checker
  - GPT-4o-mini: 0.78 repair rounds on average; succeeds without repair in 86.4% of converged cases
  - mypy error messages (with line numbers, expected vs actual types) fed back as repair signal
  - Key insight: Exact mypy output (not summarized) is most effective; few iterations needed for type annotation tasks
  - Limitation: type annotation ≠ code generation repair — different task, but demonstrates mypy signal is actionable

**Query 3: FeedbackEval (arxiv 2504.06939)**
- Mixed feedback achieves highest success rate in code repair across feedback types
- References GPT-4o-mini, Claude 3.5 Sonnet, Qwen 2.5 — contemporary models

### Archon Code Examples

*Note: Archon MCP unavailable. Code patterns derived from web research.*

**Pattern 1: Iterative Repair Loop (from Johin2/iterative-code-repair, github.com)**
```python
# Core pattern: execute → feedback → repair × k rounds
for round_k in range(1, max_rounds + 1):
    result = executor.run(code, test_cases)
    if result.passed:
        break
    feedback = format_feedback(result.error, result.stdout)
    code = llm.repair(problem_description, code, feedback)
```
- Temperature: 0 for repair rounds (greedy for reproducibility)
- Feedback: execution error message + stdout/stderr

**Pattern 2: mypy Feedback Integration (from arxiv 2508.00422)**
```python
# mypy feedback loop
import subprocess
mypy_result = subprocess.run(
    ["mypy", "--ignore-missing-imports", "--no-strict-optional", code_file],
    capture_output=True, text=True
)
if mypy_result.returncode != 0:
    mypy_feedback = mypy_result.stdout  # exact error messages with line numbers
    code = llm.repair(problem, code, execution_feedback + "\n" + mypy_feedback)
```

### Exa GitHub Implementations

**Repository 1: Johin2/iterative-code-repair**
- URL: https://github.com/Johin2/iterative-code-repair
- Relevance: Directly implements iterative self-repair with execution feedback on HumanEval + MBPP Sanitized, up to 5 rounds, 7 models
- Architecture: code_executor.py (sandboxed Python execution) + self_repair.py (prompt construction)
- Key finding: Temperature=0 for repair, greedy decoding; self-repair universally improves all models on both benchmarks
- Results: +4.9 to +17.1 pp HumanEval, +16.0 to +30.0 pp MBPP
- Limitation: No mypy/static analysis condition — pure execution feedback only

**Repository 2: evalplus/evalplus**
- URL: https://github.com/evalplus/evalplus
- Relevance: Official EvalPlus evaluation framework for HumanEval+ (164 problems, 80x more tests) and MBPP+ (378 problems v0.2.0, 35x more tests)
- Key code:
  ```bash
  pip install evalplus --upgrade
  # Evaluate generated samples:
  evalplus.evaluate --model [MODEL] --dataset [humaneval|mbpp] --backend vllm --greedy
  ```
- Dataset loading:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  humaneval_problems = get_human_eval_plus()   # dict of 164 problems
  mbpp_problems = get_mbpp_plus()              # dict of 378 problems
  ```
- Evaluation: pass@1 via greedy decoding (canonical); pass@k via temperature sampling

**Repository 3: ravinravi03/LLMLOOP**
- URL: https://github.com/ravinravi03/LLMLOOP
- Relevance: Combines execution + static analysis (PMD for Java) in iterative loop; demonstrates static analysis adds signal beyond execution-only
- Key insight: Static analysis loop applied AFTER compilation loop; staged feedback hierarchy
- Limitation: Java-only (PMD), not Python/mypy — conceptual reference only

**Serena Analysis Needed:** false (code is clear from search results; Python execution + mypy subprocess call is straightforward)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

No single prior paper implements exactly execution+mypy vs execution-only comparison on HumanEval+/MBPP+ with GPT-4o-mini. This is novel. Implementation must be built from components:
1. EvalPlus framework (evalplus/evalplus) — dataset loading and pass@1 evaluation
2. Execution feedback loop pattern (Johin2/iterative-code-repair) — Python execution sandbox
3. mypy integration pattern (arxiv 2508.00422) — subprocess mypy call, exact error message format

**Recommended Implementation Path:**
- Primary: Build from evalplus + openai Python SDK + subprocess mypy
- Fallback: Adapt Johin2/iterative-code-repair to add mypy Condition B
- Justification: No existing repo implements this exact 2-condition comparison; components are well-established

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Execution + mypy subprocess integration does not require semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset: MBPP+ (EvalPlus v0.2.0)**
- Name: MBPP+ (Mostly Basic Python Programming, EvalPlus augmented)
- Type: standard (programmatic-api via evalplus library)
- Source: evalplus/evalplus GitHub repository
- Size: 378 problems (v0.2.0, removed incorrect test lists from original 399)
- Split: All 378 problems used (no train/test split — benchmark evaluation)
- Path: auto (downloaded via `from evalplus.data import get_mbpp_plus`)
- Hypothesis Fit: Sufficient statistical power to detect 1% absolute pass@1 improvement (primary benchmark per Phase 2B)

**Secondary Dataset: HumanEval+ (EvalPlus)**
- Name: HumanEval+ (EvalPlus augmented, 80x more tests than original)
- Type: standard (programmatic-api via evalplus library)
- Source: evalplus/evalplus GitHub repository
- Size: 164 problems
- Split: All 164 problems used
- Path: auto (downloaded via `from evalplus.data import get_human_eval_plus`)
- Hypothesis Fit: Secondary replication benchmark; positive (non-significant) delta sufficient per Phase 2B success criteria

**Synthetic Data Policy Check:** PASSED — both datasets are real, established benchmarks from EvalPlus (standard type). No synthetic data.

**Loading Information:**
- Method: Python API (evalplus library)
- Identifier: evalplus PyPI package v≥0.3.0
- Code:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  mbpp_problems = get_mbpp_plus()        # {task_id: {prompt, canonical_solution, test, ...}}
  humaneval_problems = get_human_eval_plus()
  ```

### Models

#### Baseline Model

**Architecture:** GPT-4o-mini (OpenAI API, azure or direct)
- Type: API-based LLM
- Source: OpenAI API (`openai` Python SDK)
- Role: Code generator (initial generation) + repair agent (repair rounds)
- Configuration:
  - Initial generation: temperature=0.8, n=1 (per seed), max_tokens=2048
  - Repair rounds: temperature=0.0 (greedy, deterministic), max_tokens=2048
  - Seeds: 3 (repeated runs with fixed seeds via API call repetition at temperature=0.8)
  - Repair budget: k=5 rounds maximum per problem per condition

**Loading Information:**
- Method: OpenAI Python SDK
- Identifier: `gpt-4o-mini`
- Code:
  ```python
  from openai import OpenAI
  client = OpenAI()  # uses OPENAI_API_KEY env var
  response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.8,  # initial generation
      max_tokens=2048
  )
  ```

#### Proposed Model

**Architecture:** Same GPT-4o-mini + mypy type-checking feedback in repair prompt

**Integration Point:** Repair prompt construction — after each failed execution, Condition B appends mypy output to the feedback before calling the LLM repair step.

**Core Mechanism Implementation:**

```python
# Core Mechanism: execution+mypy repair feedback (Condition B)
# Baseline (Condition A) uses execution_feedback only
# Proposed (Condition B) augments with mypy_feedback

import subprocess, tempfile, os

def get_mypy_feedback(code: str) -> str:
    """Run mypy in permissive mode; return error string or empty."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        fpath = f.name
    result = subprocess.run(
        ["mypy", "--ignore-missing-imports", "--no-strict-optional",
         "--no-error-summary", fpath],
        capture_output=True, text=True, timeout=10
    )
    os.unlink(fpath)
    if result.returncode == 0:
        return ""  # no type errors
    return result.stdout.strip()

def build_repair_prompt(problem: dict, code: str,
                        exec_feedback: str, condition: str) -> str:
    """Construct repair prompt for Condition A or B."""
    base = (
        f"Problem:\n{problem['prompt']}\n\n"
        f"Your previous solution:\n```python\n{code}\n```\n\n"
        f"Execution result (FAILED):\n{exec_feedback}\n\n"
    )
    if condition == "B":
        mypy_fb = get_mypy_feedback(code)
        if mypy_fb:
            base += f"Type checker (mypy) errors:\n{mypy_fb}\n\n"
    base += "Fix the code. Return ONLY the corrected Python function."
    return base

def repair_loop(problem, initial_code, executor, llm, condition, max_k=5):
    """Run k-round repair loop for given condition (A or B)."""
    code = initial_code
    results = []  # pass@1 at each round
    for k in range(1, max_k + 1):
        passed, exec_fb = executor.run(code, problem["tests"])
        results.append(int(passed))
        if passed:
            break
        prompt = build_repair_prompt(problem, code, exec_fb, condition)
        code = llm.generate(prompt, temperature=0.0)
    return results, code
```

### Training Protocol

*Note: This is not a training experiment — no model weights are updated. "Training protocol" = experiment execution protocol.*

**Experiment Execution Protocol:**

**Phase 1: Initial Generation (Seeds 1–3)**
- For each seed s ∈ {1, 2, 3}:
  - Generate initial solution for all MBPP+ (378) and HumanEval+ (164) problems
  - Model: GPT-4o-mini, temperature=0.8, max_tokens=2048
  - Record: initial code per (problem_id, seed)

**Phase 2: Repair Loop (Conditions A and B, k=1..5)**
- For each problem × seed × condition ∈ {A, B}:
  - Run repair_loop() with max_k=5
  - Condition A: execution feedback only
  - Condition B: execution feedback + mypy feedback (when mypy detects errors)
  - Record: pass@1 at each round k, final code, mypy error count per round

**Control Variables (must be identical across conditions):**
- Same initial generated code (same seed, same problem)
- Same repair LLM (GPT-4o-mini, temperature=0.0)
- Same prompt template except mypy block
- Same execution sandbox (EvalPlus test runner)
- Same max_tokens, same k limit

**Additional Logging (for h-m2 confound analysis):**
- Token count per repair prompt (Condition A vs B) — to measure context-length difference
- mypy error count per round per problem (for h-m1 re-validation)
- Failure category per problem (type-error vs non-type-error via mypy)

**No-Repair Baseline (Condition 0):**
- Record pass@1 from initial generation only (k=0) for all 3 seeds
- This gives the starting baseline before any repair

**Seeds:** 3 (for statistical stability; Welch's t-test on per-problem deltas requires variance estimate)

**Estimated API Cost:**
- Initial generation: (378+164) × 3 seeds = 1,626 calls
- Repair: up to 1,626 × 5 rounds × 2 conditions = 16,260 calls (upper bound; many problems solved early)
- Total: ~7,400–10,000 calls at GPT-4o-mini pricing ($0.15/1M input, $0.60/1M output) → $10–15

**Optimizer:** N/A (API-based inference, no gradient descent)
**Loss Function:** N/A (pass@1 via EvalPlus test suite)

### Evaluation

**Primary Metric (MBPP+):**
- pass@1 at round k — fraction of 378 problems solved after exactly k repair rounds (cumulative: solved at any round ≤ k)
- Primary summary: mean pass@1 averaged over rounds k=1..5 and seeds 1..3
- Statistical test: Welch's t-test on per-problem improvement delta (Cond B pass@1 − Cond A pass@1) on MBPP+

**Secondary Metric (HumanEval+):**
- Same pass@1 computation on 164 problems
- Success criterion: positive delta (even non-significant)

**Success Criteria:**
- MUST_WORK gate: p < 0.05 on MBPP+ (Welch's t-test, per-problem delta) AND absolute pass@1 improvement ≥ 1% on MBPP+
- Secondary: positive pass@1 delta on HumanEval+ (direction only)

**Expected Baseline Performance (from research):**
- GPT-4o-mini no-repair pass@1: ~55–65% on MBPP+ (estimated from EvalPlus leaderboard)
- Execution-only repair (Condition A, k=5): +16 to +30 pp improvement expected (from Johin2/iterative-code-repair on MBPP Sanitized with similar models)
- Source: arxiv 2604.10508, EvalPlus leaderboard

**Failure Detection:**
- If Condition B pass@1 < Condition A pass@1: check token counts — if Condition B prompts are substantially longer, context-length confound may be active
- If p ≥ 0.05 on both: PIVOT — check H-M1 trajectory for this experiment run

**Metrics Loading Information:**
- Task Type: code_generation_pass@k
- Library: evalplus (built-in test runner) + scipy (Welch's t-test)
- Code:
  ```python
  from scipy import stats
  # per_problem_delta[i] = mean_{seeds,rounds} pass(B,i) - mean_{seeds,rounds} pass(A,i)
  t_stat, p_value = stats.ttest_ind(
      pass_B_per_problem, pass_A_per_problem, equal_var=False
  )
  absolute_improvement = pass_B_mean - pass_A_mean
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — Condition A vs Condition B pass@1 on MBPP+ and HumanEval+, with error bars (±1 std across seeds)

#### Additional Figures (LLM Autonomous)
- **Repair Trajectory by Round:** Line plot — mean pass@1 per round k (k=0..5) for Conditions A, B, and no-repair baseline, for both benchmarks
- **Per-Problem Delta Distribution:** Histogram of per-problem (B−A) deltas on MBPP+ (shows spread of effect)
- **mypy Error Count by Round:** Line plot — mean mypy error count per round k for Condition B (validates h-m1 mechanism; from logged data)
- **Token Count Comparison:** Bar chart — mean prompt token count per round for Condition A vs B (confound control from h-m2)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions (verify before reporting results):**
- mechanism_exists: Yes — mypy subprocess call is standard Python; verifiable
- mechanism_isolatable: Yes — Condition A and B differ only in mypy block in repair prompt
- baseline_measurable: Yes — EvalPlus pass@1 is deterministic given greedy decoding

**Architecture Compatibility:**
- GPT-4o-mini receives mypy output as text in repair prompt — no architecture changes needed
- mypy in permissive mode (`--ignore-missing-imports --no-strict-optional`) runs on any Python function

**Activation Indicators:**
- mechanism_log_message: "MYPY_FEEDBACK_ADDED: {n_errors} errors for problem {task_id} round {k}"
- tensor_shape_change: N/A (NLP task)
- metric_delta_expected: pass@1(B) > pass@1(A) by ≥1% on MBPP+

**Mechanism Verification Code:**
```python
# Verify mechanism is active: mypy produces non-empty output on at least some problems
mypy_triggered_count = sum(1 for fb in mypy_feedbacks if fb != "")
print(f"mypy feedback triggered on {mypy_triggered_count}/{total_repair_attempts} repair attempts")
assert mypy_triggered_count > 0, "Mechanism never activated — check mypy installation"
# Cross-check with h-e1: at least 10% of failing solutions should trigger mypy
```

**Failure Detection:**
- If mypy_triggered_count == 0: mypy not installed or incorrect path — abort
- If Condition B token counts >> Condition A: context-length confound is active — log and report
- If p ≥ 0.05 on both benchmarks: check per-round trajectory; if pass@1 curves are parallel, confound or ceiling effect

**hypothesis_support_threshold:** p < 0.05 AND absolute delta ≥ 0.01
**hypothesis_support_metric:** Welch's t-test p-value on per-problem pass@1 delta (B−A) on MBPP+

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (execution + mypy feedback loop completes for all problems)
2. pass@1(Condition B) > pass@1(Condition A) on MBPP+ with p < 0.05

---

## Appendix: Reference Implementations

### A. Web Search Sources (Archon MCP unavailable — web search used)

**Source A.1: "How Many Tries Does It Take?" (arxiv 2604.10508)**
- Query: "LLM code repair loop execution feedback pass@1 improvement HumanEval MBPP"
- Key insights: +4.9 to +17.1 pp on HumanEval, +16.0 to +30.0 pp on MBPP with up to 5 repair rounds; temperature=0 for repair; 7 models evaluated
- Used for: baseline performance expectations, repair protocol design, hyperparameter choices
- URL: https://arxiv.org/abs/2604.10508

**Source A.2: LLMloop (arxiv 2603.23613)**
- Query: "LLM code repair loop execution feedback pass@1 improvement"
- Key insights: Static analysis adds signal beyond execution-only; staged feedback hierarchy; GPT-4o-mini, adaptive temperature
- Used for: justification for adding mypy as feedback channel; implementation strategy
- URL: https://arxiv.org/abs/2603.23613

**Source A.3: "Automated Type Annotation in Python Using LLMs" (arxiv 2508.00422)**
- Query: "mypy type checking LLM code generation repair feedback loop Python benchmark 2025"
- Key insights: mypy error messages (line numbers, expected vs actual types) are actionable for GPT-4o-mini; 0.78 repair rounds on average; exact mypy output most effective
- Used for: mypy feedback format design, confirmation that GPT-4o-mini can parse mypy output
- URL: https://arxiv.org/abs/2508.00422

### B. GitHub Implementations (Exa/Web Search)

**Repository B.1: Johin2/iterative-code-repair**
- URL: https://github.com/Johin2/iterative-code-repair
- Query: "LLM code repair mypy static analysis execution feedback HumanEval MBPP Python"
- Key code:
  ```python
  # code_executor.py: sandboxed Python execution
  # self_repair.py: prompt construction and code extraction
  # temperature=0 for repair, greedy decoding
  ```
- Configuration extracted: temperature=0 (repair), up to 5 rounds, HumanEval+MBPP Sanitized
- Results: +4.9–17.1 pp HumanEval, +16–30 pp MBPP
- Used for: repair loop structure, hyperparameter choices

**Repository B.2: evalplus/evalplus**
- URL: https://github.com/evalplus/evalplus
- Key code:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  # HumanEval+: 164 problems, 80x more tests
  # MBPP+: 378 problems v0.2.0, 35x more tests
  ```
- Used for: dataset loading, pass@1 evaluation framework

**Repository B.3: ravinravi03/LLMLOOP**
- URL: https://github.com/ravinravi03/LLMLOOP
- Key insight: compilation + static analysis (PMD) loop outperforms execution-only
- Used for: conceptual justification of multi-signal feedback hierarchy

### C. Code Analysis (Serena)
Serena analysis not performed — code from search results was sufficiently clear.

### D. Previous Hypothesis Context
- **h-m1 (VALIDATED):** Optimal repair hyperparameters confirmed — GPT-4o-mini, temperature=0.0 repair, k=5, both benchmarks. Mypy error count decreases monotonically (Spearman ρ < 0). Reusing these hyperparameters.
- **h-m2 (FAILED, SHOULD_WORK):** Ceiling effect on type-error category repair rate. Extra-context-length is primary confound to track. Token count logging added to h-m3 protocol.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Primary dataset: MBPP+ (378) | EvalPlus standard | B.2 (evalplus/evalplus) |
| Secondary dataset: HumanEval+ (164) | EvalPlus standard | B.2 (evalplus/evalplus) |
| Model: GPT-4o-mini | Phase 2B selection | 02b_verification_plan.md §1.3 |
| Initial temperature=0.8 | Phase 2B + h-m1 | 02b_verification_plan.md §2.2 H-M3 |
| Repair temperature=0.0 | h-m1 validated | Prior hypothesis results |
| k=5 repair rounds | Phase 2B + A.1 | 02b_verification_plan.md §1.5 A4; arxiv 2604.10508 |
| mypy permissive mode flags | Phase 2B + A.3 | 02b_verification_plan.md §1.5 A3; arxiv 2508.00422 |
| Execution sandbox design | B.1 | Johin2/iterative-code-repair |
| mypy subprocess integration | A.3 | arxiv 2508.00422 |
| Pass@1 evaluation | B.2 | evalplus/evalplus |
| Welch's t-test on per-problem delta | Phase 2B | 02b_verification_plan.md §2.2 H-M3 |
| Token-count confound logging | h-m2 limitation | Prior hypothesis results |
| Expected baseline performance | A.1 | arxiv 2604.10508 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state managed via state blocks)
**Date:** 2026-08-26

### Workflow History for This Hypothesis
- h-m3 set to IN_PROGRESS (2026-08-26T11:46:38)
- Phase 2C experiment design started (2026-08-26)
- Phase 2C experiment design completed (2026-08-26)

---

*MCP Tools Used: WebSearch (Archon MCP unavailable), WebFetch (Exa substitute), Serena skipped (code clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
