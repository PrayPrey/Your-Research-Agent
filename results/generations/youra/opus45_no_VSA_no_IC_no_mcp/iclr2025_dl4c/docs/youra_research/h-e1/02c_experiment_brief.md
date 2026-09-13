# Experiment Design: H-E1

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Execution-detailed feedback yields measurably higher pass@1 than random baseline after k=3 refinement iterations on HumanEval and MBPP.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Execution feedback contains unique localization info absent from random baseline. Proposed metric (pass@1 with execution feedback) > baseline metric (pass@1 with random feedback).

---

## Continuation Context

*First hypothesis in verification chain - no prior context.*

### Previous Hypothesis Results (if applicable)
*Not applicable - H-E1 is foundation hypothesis.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Iterative Code Refinement Experiment Design**

- **Self-Debug (Chen et al., 2023)**
  - Dataset: HumanEval, MBPP
  - Iterations: 3-5 refinement rounds
  - Key insight: Execution feedback (compiler errors, test outputs) guides targeted code edits
  - Improvement: ~10% over zero-shot

- **Self-Refine (Madaan et al., 2023)**
  - Dataset: Multiple NLP/code tasks
  - Iterations: 3 rounds typical
  - Key insight: AI critique can improve output but effect varies by task
  - Improvement: ~5-8% on code tasks

- **CodeRL (Le et al., 2022)**
  - Dataset: APPS, MBPP
  - Key insight: RL with execution rewards improves code generation
  - Baseline: Fine-tuned CodeT5

**Query 2: Implementation Best Practices**

- Use standardized execution sandboxes (E2B, Docker)
- Template-normalize feedback for fair comparison
- Control for prompt format effects
- Track per-iteration metrics, not just final

### Archon Code Examples

**Self-Debug Pattern:**
```python
def iterative_refinement(model, problem, max_iter=3):
    code = model.generate(problem)
    for i in range(max_iter):
        result = execute_code(code, problem.tests)
        if result.passed:
            return code
        feedback = format_execution_feedback(result)
        code = model.refine(problem, code, feedback)
    return code
```

### Exa GitHub Implementations

**Repository 1**: openai/human-eval (Official)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Official HumanEval dataset with evaluation harness
- **Key Code**: `evaluate_functional_correctness()` for pass@k
- **Evaluation**: Execution-based correctness via test cases

**Repository 2**: google-research/mbpp (Official)
- **URL**: https://github.com/google-research/mbpp
- **Relevance**: Official MBPP dataset with 974 problems
- **Key Code**: JSON format with task_id, code, test_list

**Repository 3**: bigcode-project/bigcode-evaluation-harness
- **URL**: https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevance**: Unified evaluation for code LLMs
- **Architecture**: Supports HumanEval, MBPP, multiple models
- **Key Code**: Execution sandbox with timeout, memory limits

### 🎯 Implementation Priority Assessment

**CRITICAL: For code generation benchmarks, prioritize official implementations**

| Priority | Implementation | Why |
|----------|----------------|-----|
| ⭐⭐⭐ | openai/human-eval | Official evaluation harness |
| ⭐⭐⭐ | google-research/mbpp | Official dataset |
| ⭐⭐ | bigcode-evaluation-harness | Standard multi-benchmark |

**Recommended Implementation Path:**
- Primary: Use bigcode-evaluation-harness for unified evaluation
- Fallback: Direct openai/human-eval + google/mbpp integration
- Justification: bigcode-evaluation-harness supports both benchmarks with consistent API

### Code Analysis (Serena MCP)

*Serena analysis not required - established benchmark implementations with clear APIs.*

---

## Experiment Specification

### Dataset

**Dataset 1: HumanEval**
- **Type:** standard
- **Source:** https://github.com/openai/human-eval
- **Statistics:** 164 problems, Python, function-level completion
- **Splits:** Full test set (no train/val for generation tasks)
- **Preprocessing:** None (prompts provided as-is)
- **Augmentation:** None

**Dataset 2: MBPP**
- **Type:** standard
- **Source:** https://github.com/google-research/mbpp
- **Statistics:** 974 problems total, 500 test problems (standard split)
- **Splits:** Test set (500 problems)
- **Preprocessing:** None (JSON format with task_id, text, code, test_list)
- **Augmentation:** None

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai_humaneval`, `mbpp`
- Code:
```python
from datasets import load_dataset
humaneval = load_dataset("openai_humaneval")
mbpp = load_dataset("mbpp", split="test")
```

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B-Instruct
- **Type:** Instruction-tuned code LLM
- **Parameters:** 7B
- **Source:** HuggingFace meta-llama
- **Secondary:** StarCoder-7B (for generalization testing)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `codellama/CodeLlama-7b-Instruct-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** CodeLlama-7B-Instruct + Execution Feedback Refinement

**Core Mechanism Implementation:**

```python
# Core Mechanism: Iterative Refinement with Execution Feedback
# Based on: Self-Debug (Chen et al., 2023)

class ExecutionFeedbackRefinement:
    """
    Iterative code refinement using execution feedback.
    Compares execution-detailed feedback vs random baseline.
    """
    def __init__(self, model, tokenizer, max_iterations=3):
        self.model = model
        self.tokenizer = tokenizer
        self.max_iterations = max_iterations

    def generate_with_refinement(self, problem, feedback_type="execution"):
        """
        Args:
            problem: dict with prompt, tests, entry_point
            feedback_type: "execution" | "random"
        Returns:
            final_code: str, pass_status: bool, iterations_used: int
        """
        code = self.initial_generate(problem["prompt"])
        
        for i in range(self.max_iterations):
            result = self.execute_code(code, problem["tests"])
            if result.passed:
                return code, True, i
            
            if feedback_type == "execution":
                feedback = self.format_execution_feedback(result)
            else:  # random baseline
                feedback = self.generate_random_feedback()
            
            code = self.refine_code(problem["prompt"], code, feedback)
        
        final_result = self.execute_code(code, problem["tests"])
        return code, final_result.passed, self.max_iterations

    def format_execution_feedback(self, result):
        """Format execution error with line number, error type, expected/actual."""
        return f"Error: {result.error_type} at line {result.line_number}\n" \
               f"Expected: {result.expected}\nActual: {result.actual}"

    def generate_random_feedback(self):
        """Random baseline: generic feedback without execution info."""
        templates = ["Try a different approach", "Check your logic", "Review the code"]
        return random.choice(templates)
```

### Training Protocol

> **Note:** This is an EXISTENCE (PoC) experiment. No training required - uses pretrained models with prompting.

**Inference Configuration:**
- **Temperature:** 0.2 (for reproducibility)
- **Max tokens:** 512
- **Top-p:** 0.95
- **Repetition penalty:** 1.0

**Refinement Parameters:**
- **Max iterations (k):** 3
- **Timeout per execution:** 10 seconds
- **Memory limit:** 512MB

**Seeds:** 1 (fixed seed=42)

### Evaluation

**Primary Metrics:**
- **pass@1:** Fraction of problems solved correctly in single attempt
- **pass@1 after k iterations:** Fraction solved after k=3 refinement rounds

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation
- Library: custom (execution-based)
- Code:
```python
def compute_pass_at_k(problems, solutions, k=1):
    """Compute pass@k using execution-based evaluation."""
    n_correct = sum(1 for p, s in zip(problems, solutions) 
                   if execute_and_check(s, p["tests"]))
    return n_correct / len(problems)
```

**Success Criteria:**
- pass@1(execution_feedback) > pass@1(random_baseline)

**Expected Baseline Performance:**
- CodeLlama-7B zero-shot on HumanEval: ~30-35% pass@1
- CodeLlama-7B zero-shot on MBPP: ~40-45% pass@1

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: pass@1 for execution feedback vs random baseline (bar chart)

#### Additional Figures (LLM Autonomous)

Based on experimental results, generate:
1. **Iteration progression**: pass@1 at each iteration k (line chart)
2. **Per-problem comparison**: Heatmap of success/failure per problem
3. **Feedback analysis**: Examples of execution feedback vs random feedback

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions

| Check | Requirement | Verification |
|-------|-------------|--------------|
| mechanism_exists | Execution feedback differs from random | Compare feedback strings |
| mechanism_isolatable | Only feedback type changes between conditions | Code review |
| baseline_measurable | Random baseline produces valid output | Execute with random feedback |

### Architecture Compatibility
- Model accepts prompt + feedback in context: YES (instruction-tuned)
- Execution sandbox available: YES (subprocess with timeout)
- Test cases executable: YES (HumanEval/MBPP provide test strings)

### Activation Indicators

| Indicator | Expected |
|-----------|----------|
| mechanism_log_message | "Feedback type: execution" logged |
| tensor_shape_change | N/A (prompt-based, not architectural) |
| metric_delta_expected | pass@1 increase of >5% over random |

### Mechanism Verification Code

```python
def verify_mechanism_activation(result_exec, result_random):
    """Verify execution feedback mechanism is active and effective."""
    # Check 1: Feedback content differs
    assert result_exec["feedback"] != result_random["feedback"], \
        "Execution feedback should differ from random"
    
    # Check 2: Execution feedback contains error info
    exec_feedback = result_exec["feedback"]
    has_line_info = "line" in exec_feedback.lower()
    has_error_type = any(e in exec_feedback for e in ["Error", "Exception", "failed"])
    assert has_line_info or has_error_type, \
        "Execution feedback should contain localization info"
    
    # Check 3: Mechanism produces different refinements
    assert result_exec["refined_code"] != result_random["refined_code"], \
        "Different feedback should produce different refinements"
    
    return True
```

### Hypothesis Support Threshold
- **hypothesis_support_metric:** pass@1_delta = pass@1(exec) - pass@1(random)
- **hypothesis_support_threshold:** pass@1_delta > 0 (any positive improvement)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `pass@1(execution_feedback) > pass@1(random_baseline)`

---

## Appendix: Reference Implementations

### Primary References

1. **Self-Debug (Chen et al., 2023)**
   - Paper: "Teaching Large Language Models to Self-Debug"
   - Relevance: Core iterative refinement pattern with execution feedback
   - Code pattern: Generate → Execute → Feedback → Refine loop

2. **HumanEval Benchmark**
   - Source: https://github.com/openai/human-eval
   - 164 Python programming problems
   - Execution-based evaluation

3. **MBPP Benchmark**
   - Source: https://github.com/google-research/mbpp
   - 500 test problems (standard split)
   - Test-case-based evaluation

### Code References

1. **bigcode-evaluation-harness**
   - URL: https://github.com/bigcode-project/bigcode-evaluation-harness
   - Purpose: Unified code generation evaluation
   - Use for: Execution sandbox, pass@k computation

2. **CodeLlama**
   - URL: https://huggingface.co/codellama
   - Purpose: Base model for code generation
   - Version: CodeLlama-7b-Instruct-hf

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design initiated
- Status: experiment_design.status = IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
