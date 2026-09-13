# Experiment Design: h-m3

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Under cascade routing conditions (N=20 from H-E1), if pytest execution is conditionally gated (run only when mypy clean) instead of always running (aggregation), then tokens-per-successful-task remains within 15% of aggregation baseline, because conditional gating skips expensive 5-10 second test execution when static errors exist without excessive verbosity trade-off.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates specific causal mechanism with controlled comparison.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m1 COMPLETED)
**Gate Status:** SHOULD_WORK gate - failure documented as limitation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (mypy error detection validation)

### Gate Condition
**Gate Type:** SHOULD_WORK
**Failure Action:** EXPLORE - Alternative token normalization strategies
**Success Criteria:** Cascade tokens-per-task ≤ 1.15 × Aggregation baseline (≤15% overhead)

---

## Continuation Context

**H-M1 Results (Prerequisite Completed):**
- Mypy error detection rate: 99.6% (far exceeds 30% gate threshold)
- Validates that static analysis catches vast majority of errors before execution
- Justifies conditional gating strategy: skip execution when mypy fails

### Previous Hypothesis Results (if applicable)
**H-M1 Validation:** Gate PASSED with 99.6% mypy detection rate across 35 dual-sensitive tasks and 700 total iterations. This high detection rate strongly supports the conditional gating hypothesis - if mypy catches 99.6% of errors, then execution can be safely skipped when mypy fails, enabling token efficiency.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Token Efficiency & LLM Feedback**
- Found resources on model efficiency and quantization (bitsandbytes, 4-bit transformers)
- T-GATE repository shows conditional gating for diffusion models (similar concept to our hypothesis)
- Key insight: Conditional execution gating is established pattern for computational efficiency

**Query 2: Conditional Gating & Execution Cost**
- T-GATE (https://github.com/HaozheLiu-ST/T-GATE): Cross-attention gating for efficiency
- Pattern: Skip expensive operations when early signals indicate failure
- Relevance: Similar principle - skip test execution when static analysis fails

**Query 3: HumanEval & Code Generation Metrics**
- Limited direct HumanEval results in Archon KB
- General evaluation metrics documentation (FID, PPL for generative models)
- Need to search Exa for HumanEval-specific implementations

**Key Takeaways:**
- Conditional gating for efficiency is proven pattern
- Token counting for LLM generation exists but not specific to code generation
- Need implementation-specific code from GitHub (Step 3)

### Archon Code Examples

**Token Counting Pattern (from GPT-2 example):**
```python
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
token_count = inputs["input_ids"].shape[1]
max_new_tokens = 50 - token_count
```
**Insight:** Use tokenizer to count input/output tokens for efficiency measurement

**Evaluation Metrics Pattern:**
```python
metrics = dict(
    metric_name=dict(
        type='MetricType',
        num_images=50000
    )
)
```
**Insight:** Structure evaluation with explicit metric configuration

**Code Not Directly Applicable:**
- Most code examples focus on image/audio generation metrics
- Need HumanEval-specific code evaluation patterns from Exa search

### Exa GitHub Implementations

**Query 1: HumanEval Evaluation & Token Measurement**

**Repository 1: openai/human-eval** (⭐2,578)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Official OpenAI HumanEval benchmark implementation - primary reference
- **Architecture**: Execution-based evaluation with pass@k metric
- **Key Components**:
  - `human_eval.data.read_problems()` - Load 164 tasks
  - `human_eval.evaluation.evaluate_functional_correctness()` - Execute and score
  - Pass@k metric implementation with unbiased estimation
- **Evaluation Protocol**:
  ```python
  from human_eval.data import write_jsonl, read_problems
  problems = read_problems()
  # Generate samples: {"task_id": "...", "completion": "..."}
  # Evaluate: evaluate_functional_correctness(samples.jsonl)
  # Output: {'pass@1': ..., 'pass@10': ..., 'pass@100': ...}
  ```
- **Token Counting Pattern** (from related sources):
  ```python
  inputs = tokenizer(prompt, return_tensors="pt")
  token_count = inputs["input_ids"].shape[1]
  # Track tokens per iteration, sum for total
  ```

**Repository 2: Token Efficiency in LLM Code Generation**
- **Source**: Multiple blog posts and implementations
- **Key Patterns**:
  - Model routing for cost optimization (70% savings via conditional routing)
  - Token profiling: Track by query type, feature, user
  - LiteLLM wrapper for observability: `litellm.completion()` with cost tracking
  - Semantic caching: 40-60% token reduction on repeated queries
- **Relevance to H-M3**: Conditional gating (skip execution when mypy fails) mirrors model routing pattern (skip expensive models for simple queries)

**Query 2: LLM Feedback Loops & Testing**

**Repository: pseudocode package** (feedback loop pattern)
- **URL**: Referenced in Quansight blog post
- **Pattern**: Automated test feedback to LLM
  1. Generate code from spec
  2. Run tests (pytest)
  3. If fail: resubmit errors to LLM
  4. Iterate until tests pass
- **Relevance**: Our cascade routing implements similar feedback loop:
  - Run mypy (static analysis)
  - If pass: run pytest (execution)
  - Track tokens at each step
- **Code Pattern**:
  ```python
  # Run static analysis
  mypy_result = run_mypy(code)
  tokens_used += count_tokens(mypy_result)

  if mypy_result.success:
      # Only run tests if static analysis passes
      pytest_result = run_pytest(code)
      tokens_used += count_tokens(pytest_result)

  total_tokens_per_task = tokens_used
  ```

**Serena Analysis Needed**: No - code patterns are clear and well-documented

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment**: This is NOT a paper reproduction - this is original hypothesis testing using established tools (HumanEval benchmark, mypy, pytest). No single "official implementation" exists.

**Recommended Implementation Path:**
- Primary: **openai/human-eval official repository** for HumanEval evaluation framework
- Secondary: **Custom implementation** for cascade vs aggregation routing logic
- Fallback: Standard PyTorch/transformers patterns for CodeLlama-7B loading
- Justification: Official HumanEval ensures reproducible evaluation; routing logic is novel and requires custom implementation

### Code Analysis (Serena MCP)

**Status**: Not needed - code patterns are clear from Exa search results. Implementation straightforward:
1. HumanEval loading: Use `human_eval.data.read_problems()`
2. Token counting: Use tokenizer's `input_ids.shape[1]`
3. Routing logic: Custom conditional (if mypy clean, run pytest)
4. Evaluation: Standard pass@k from official repo

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval with HumanEval+ augmented tests
- **Type**: Standard benchmark (code generation)
- **Source**: `evalplus` Python package (`pip install evalplus`)
- **Tasks**: 164 hand-written Python programming problems
- **Test Coverage**: 80+ robustness tests per task via HumanEval+
- **Purpose**: Dual-sensitive task selection (N=20 from H-E1 classification)

**Task Selection Protocol** (from H-E1):
1. Load full HumanEval dataset (164 tasks)
2. Filter to N=20 dual-sensitive tasks identified in H-E1
3. Dual-sensitive = tasks where ≥1 solution fails mypy but passes tests AND ≥1 passes mypy but fails tests

**Data Splits**: No train/val/test - this is evaluation-only (all 20 tasks used for experiment)

**Loading Information** (for Phase 4 download):
- Method: Python package installation + custom task loader
- Identifier: `evalplus` package + H-E1 task IDs
- Code:
  ```python
  # Install: pip install evalplus
  from evalplus.data import get_human_eval_plus
  problems = get_human_eval_plus()

  # Load dual-sensitive task IDs from H-E1 results
  # (stored in h-e1/04_validation.md)
  dual_sensitive_task_ids = [...]  # N=20 tasks from H-E1
  selected_problems = {tid: problems[tid] for tid in dual_sensitive_task_ids}
  ```

### Models

#### Baseline Model

**Model**: CodeLlama-7B (Base)
- **Type**: Base code generation model (NOT instruction-tuned)
- **Parameters**: 7B
- **Source**: HuggingFace Hub (`codellama/CodeLlama-7b-hf`)
- **Rationale**: Tests feedback routing on base model; 7B size enables <30min inference while testing routing policy effects
- **Why Base (not Instruct)**: Tests pure feedback routing without instruction-following confounds

**Tokenizer**: CodeLlama tokenizer (for token counting)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` library
- Identifier: `codellama/CodeLlama-7b-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer

  model_name = "codellama/CodeLlama-7b-hf"
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForCausalLM.from_pretrained(
      model_name,
      torch_dtype=torch.float16,
      device_map="auto"
  )
  model.eval()
  ```

#### Proposed Model

**Architecture:** CodeLlama-7B + Conditional Execution Gating Feedback Router

**Integration**: No model modification - routing logic is external to model (controls feedback presentation)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Conditional Execution Gating (Cascade Routing)
# Based on: LLM feedback loop patterns + model routing efficiency research

class CascadeRouter:
    """
    Conditional feedback routing: static analysis first, execution only if clean.
    Tracks token efficiency vs simultaneous aggregation baseline.
    """
    def __init__(self, model, tokenizer, max_iterations=10):
        self.model = model
        self.tokenizer = tokenizer
        self.max_iterations = max_iterations
        self.token_limit_per_source = 1000  # Equal limits

    def route_feedback(self, task, code_attempt):
        """
        Cascade routing: mypy → (if clean) → pytest

        Returns:
            feedback_str: Single-source feedback for this iteration
            tokens_used: Token count for this iteration
        """
        # Step 1: Run static analysis (mypy --strict)
        mypy_result = run_mypy_strict(code_attempt)
        mypy_feedback = format_mypy_output(mypy_result)
        tokens_used = count_tokens(self.tokenizer, mypy_feedback)

        # Step 2: Conditional execution gating
        if mypy_result.success:  # Clean = no mypy errors
            # Gate OPEN: Run execution tests
            pytest_result = run_pytest(task, code_attempt)
            pytest_feedback = format_pytest_output(pytest_result)
            tokens_used += count_tokens(self.tokenizer, pytest_feedback)
            return pytest_feedback, tokens_used
        else:
            # Gate CLOSED: Skip execution, return mypy errors only
            return mypy_feedback, tokens_used

class AggregationRouter:
    """
    Baseline: Simultaneous multi-source aggregation.
    Both mypy + pytest every iteration, concatenated.
    """
    def route_feedback(self, task, code_attempt):
        # Always run both sources
        mypy_result = run_mypy_strict(code_attempt)
        pytest_result = run_pytest(task, code_attempt)

        # Concatenate feedback
        combined = format_mypy_output(mypy_result) + "\n" + format_pytest_output(pytest_result)
        tokens_used = count_tokens(self.tokenizer, combined)
        return combined, tokens_used

# Integration: External to model - controls feedback generation loop
```

**Key Parameters:**
- `max_iterations`: 10 (standard for code generation tasks)
- `token_limit_per_source`: 1000 tokens (enforced equally both conditions)
- `temperature`: 0.7 (standard for code generation)

### Training Protocol

**No Training Required** - This is an evaluation-only experiment using pretrained CodeLlama-7B.

**Inference Protocol:**

**Experimental Conditions:**
1. **CASCADE**: Conditional execution gating (mypy → if clean → pytest)
2. **AGGREGATION**: Simultaneous both sources (mypy + pytest every iteration)

**Per-Task Protocol:**
1. Load task from dual-sensitive set (N=20 from H-E1)
2. Initialize code generation with task prompt
3. For each iteration (max 10):
   - Generate code completion using CodeLlama-7B
   - Route feedback based on condition (CASCADE or AGGREGATION)
   - Track tokens used this iteration
   - If solution passes all tests: STOP, record success
4. Record metrics:
   - Total tokens used (sum across all iterations)
   - Iterations to solution
   - Final pass/fail status

**Model Configuration:**
- Temperature: 0.7
- Max tokens per generation: 512
- Sampling: True (do_sample=True)
- Top-p: 0.95
- Model dtype: float16 (for memory efficiency)

**Controlled Variables:**
- Model: CodeLlama-7B (same for both conditions)
- Task set: Same N=20 dual-sensitive tasks
- Token limits: 1000 per source per iteration (enforced equally)
- Max iterations: 10 (same for both)
- Random seed: 42 (for reproducibility)

**Execution Environment:**
- Single GPU (CUDA_VISIBLE_DEVICES set)
- PyTorch + HuggingFace Transformers
- Python 3.8+

### Evaluation

**Primary Metric: Tokens-Per-Successful-Task**

**Definition:**
```python
tokens_per_task = sum(tokens_used_per_iteration) / total_tasks
# Where: only count tasks that eventually succeeded (passed all tests)
```

**Gate Validation:**
- **Hypothesis Claim**: Cascade ≤ 1.15 × Aggregation (≤15% overhead)
- **Calculation**: `cascade_tokens_per_task / aggregation_tokens_per_task ≤ 1.15`
- **Gate Type**: SHOULD_WORK (failure = document limitation, continue)

**Secondary Metrics (for analysis):**
1. **Gating Efficiency**: % of iterations where execution was skipped (CASCADE only)
   ```python
   gating_efficiency = (iterations_mypy_failed / total_iterations) * 100
   ```

2. **Token Breakdown**:
   - Tokens from mypy feedback
   - Tokens from pytest feedback
   - Total per condition

3. **Success Metrics** (for verification):
   - Tasks solved successfully (both conditions)
   - Mean iterations to solution
   - Pass@1 rate (should be similar both conditions)

**Comparison Protocol:**
- Within-task paired comparison (same 20 tasks both conditions)
- Controlled variables: model, tasks, token limits
- Independent variable: routing policy (CASCADE vs AGGREGATION)
- Dependent variable: tokens-per-successful-task

**Expected Results:**
- H-M1 showed 99.6% mypy detection rate → most iterations skip execution in CASCADE
- Expected: CASCADE slightly higher tokens-per-task due to routing overhead, but ≤15%
- If CASCADE > 1.15 × AGGREGATION: gate fails, document as limitation

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation evaluation with token efficiency measurement
- Library: Custom metrics (token counting via tokenizer, pass/fail via HumanEval framework)
- Code:
  ```python
  from transformers import AutoTokenizer
  from human_eval.evaluation import evaluate_functional_correctness

  tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")

  def count_tokens(text):
      return len(tokenizer.encode(text))

  def compute_tokens_per_task(results):
      successful_tasks = [r for r in results if r['passed']]
      total_tokens = sum(r['total_tokens'] for r in successful_tasks)
      return total_tokens / len(successful_tasks)

  # Gate check
  cascade_tpt = compute_tokens_per_task(cascade_results)
  aggregation_tpt = compute_tokens_per_task(aggregation_results)
  ratio = cascade_tpt / aggregation_tpt
  gate_passed = ratio <= 1.15
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Figure 2: Token Efficiency Comparison**
- Bar chart: CASCADE vs AGGREGATION tokens-per-task
- Include error bars (if multiple seeds used)
- Horizontal line at 1.15× ratio threshold

**Figure 3: Token Breakdown**
- Stacked bar chart showing mypy vs pytest token contribution
- Separate bars for CASCADE vs AGGREGATION
- Shows where tokens are spent

**Figure 4: Gating Efficiency**
- Line chart: % of iterations with execution skipped (CASCADE only)
- X-axis: Task index, Y-axis: Gating efficiency %
- Shows how often conditional gating activates

**Figure 5: Iterations to Solution** (optional)
- Histogram comparing iteration counts CASCADE vs AGGREGATION
- Verifies routing doesn't harm convergence speed

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `cascade_tokens_per_task ≤ 1.15 × aggregation_tokens_per_task`

---

## Appendix: Reference Implementations

### Primary References

**1. OpenAI HumanEval Official Repository**
- URL: https://github.com/openai/human-eval
- Stars: 2,578
- Purpose: Official evaluation framework for code generation
- Key Files:
  - `human_eval/data.py` - Task loading
  - `human_eval/evaluation.py` - Pass@k metric
  - `human_eval/execution.py` - Safe code execution
- Usage: Primary evaluation harness for both conditions

**2. HumanEval+ (EvalPlus)**
- Package: `evalplus` (pip install evalplus)
- Purpose: Extended test cases (80+ per task)
- Relevance: Enables robust dual-sensitive task classification (H-E1)
- URL: Referenced in Phase 2B verification plan

**3. CodeLlama Model**
- HuggingFace: `codellama/CodeLlama-7b-hf`
- Paper: "Code Llama: Open Foundation Models for Code" (Meta, 2023)
- Purpose: Base code generation model for both conditions

### Implementation Patterns

**4. Token Efficiency & Model Routing**
- Source: Multiple blog posts on LLM cost optimization
- Pattern: Conditional routing for 70% cost savings
- Relevance: CASCADE routing mirrors model routing efficiency principle
- Key Insight: Skip expensive operations when early signals indicate failure

**5. LLM Feedback Loop Testing**
- Source: Quansight blog post on pseudocode package
- Pattern: Automated test feedback to LLM
- Relevance: Feedback routing implementation pattern
- Key Pattern:
  ```python
  # Generate → Test → If fail, resubmit errors → Iterate
  while not tests_pass and iterations < max_iter:
      feedback = get_feedback(code, tests)
      code = llm.generate(prompt + feedback)
  ```

**6. Mypy Static Analysis**
- Tool: `mypy --strict` mode
- Purpose: Type checking and compositional guarantees
- Relevance: Primary gating signal for CASCADE condition
- Expected detection rate: 99.6% (from H-M1 validation)

**7. Pytest Execution Testing**
- Tool: `pytest` with HumanEval test suites
- Purpose: Functional correctness validation
- Relevance: Secondary feedback source (gated in CASCADE, always-on in AGGREGATION)

### Code Snippets Referenced

**Token Counting (from Exa search):**
```python
inputs = tokenizer(text, return_tensors="pt")
token_count = inputs["input_ids"].shape[1]
```

**HumanEval Evaluation (from official repo):**
```python
from human_eval.data import read_problems
from human_eval.evaluation import evaluate_functional_correctness

problems = read_problems()
# Generate solutions and save to jsonl
evaluate_functional_correctness("samples.jsonl")
# Output: {'pass@1': ..., 'pass@10': ..., 'pass@100': ...}
```

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T17:08:03Z

### Workflow History for This Hypothesis
- 2026-03-18T17:08:03Z: Hypothesis h-m3 set to IN_PROGRESS
- 2026-03-18T17:08:03Z: External loop starting Phase 2C → 3 → 4 for h-m3

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
