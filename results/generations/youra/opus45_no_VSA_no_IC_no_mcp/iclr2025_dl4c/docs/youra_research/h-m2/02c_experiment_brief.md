# Experiment Design: H-M2

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Execution-detailed feedback yields higher pass@1 than execution-binary (pass/fail only) because detailed error traces enable targeted code edits rather than global rewrites.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Testing causal link between feedback granularity and edit behavior.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 VALIDATED)
**Gate Status:** SHOULD_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
Localized (execution-detailed) feedback produces smaller diffs than non-localized (execution-binary) feedback. Edits concentrate at actual bug location with detailed feedback.

---

## Continuation Context

**Continuing from H-E1 validation:**
- Execution feedback loop confirmed working
- CodeLlama-7B-Instruct successful on HumanEval/MBPP
- Refinement mechanism verified (34/164 HumanEval partial run)
- Infrastructure reused: execution sandbox, feedback formatting, evaluation harness

### Previous Hypothesis Results (H-E1)
- **Result:** PASS - PoC demonstrates working implementation
- **Key Finding:** Execution feedback provides unique localization info
- **Baseline pass@1:** ~30-35% HumanEval, ~40-45% MBPP
- **Reusable Components:** Execution sandbox, model loading, dataset handling

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Feedback Granularity in Code Refinement**

- **Self-Debug (Chen et al., 2023)**
  - Key insight: Detailed error traces (line numbers, error types) outperform simple pass/fail
  - Ablation: Removing line numbers reduces performance by ~5%
  - Edit pattern: Detailed feedback leads to surgical edits

- **Reflexion (Shinn et al., 2023)**
  - Feedback types tested: binary, verbal, detailed traces
  - Finding: More granular feedback enables better self-reflection
  - Mechanism: Specific info constrains hypothesis space

**Query 2: Edit Scope Analysis**

- **CodeRL (Le et al., 2022)**
  - Edit metric: AST edit distance used to measure change scope
  - Finding: Successful fixes tend to have smaller edit distances
  - Implication: Targeted edits more likely to succeed

- **AlphaCode (Li et al., 2022)**
  - Sampling strategy: Generate many, filter by execution
  - Relevant: Shows execution signal value, not edit targeting

### Archon Code Examples

**Edit Scope Measurement Pattern:**
```python
import difflib
import ast

def measure_edit_scope(original_code, refined_code):
    """Measure edit scope via multiple metrics."""
    # Line-level diff
    diff = list(difflib.unified_diff(
        original_code.splitlines(),
        refined_code.splitlines()
    ))
    lines_changed = sum(1 for d in diff if d.startswith('+') or d.startswith('-'))
    
    # AST distance (if both parse)
    try:
        ast_orig = ast.parse(original_code)
        ast_refined = ast.parse(refined_code)
        ast_distance = compute_ast_distance(ast_orig, ast_refined)
    except:
        ast_distance = None
    
    return {
        "lines_changed": lines_changed,
        "total_lines": len(original_code.splitlines()),
        "change_ratio": lines_changed / max(1, len(original_code.splitlines())),
        "ast_distance": ast_distance
    }
```

### Exa GitHub Implementations

**Repository 1**: openai/human-eval (Official)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Official HumanEval dataset with evaluation harness
- **Key Code**: `evaluate_functional_correctness()` for pass@k

**Repository 2**: bigcode-project/bigcode-evaluation-harness
- **URL**: https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevance**: Unified evaluation supporting multiple benchmarks
- **Key Code**: Execution sandbox with timeout, memory limits

**Repository 3**: microsoft/CodeBERT (Edit Analysis)
- **URL**: https://github.com/microsoft/CodeBERT
- **Relevance**: Code diff analysis tools
- **Key Code**: AST-based code comparison utilities

### 🎯 Implementation Priority Assessment

**CRITICAL: For mechanism hypothesis, need both feedback formatting AND edit measurement**

| Priority | Implementation | Why |
|----------|----------------|-----|
| ⭐⭐⭐ | H-E1 infrastructure | Reuse execution sandbox, model loading |
| ⭐⭐⭐ | difflib (stdlib) | Line-level edit scope measurement |
| ⭐⭐ | ast (stdlib) | AST distance for semantic edit scope |

**Recommended Implementation Path:**
- Primary: Extend H-E1 codebase with binary feedback condition and edit metrics
- Fallback: Standalone implementation with same interfaces
- Justification: H-E1 already has working execution and refinement loop

### Code Analysis (Serena MCP)

*Serena analysis not required - building on validated H-E1 infrastructure.*

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
- **Preprocessing:** None
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

**Architecture:** CodeLlama-7B-Instruct (reused from H-E1)
- **Type:** Instruction-tuned code LLM
- **Parameters:** 7B
- **Source:** HuggingFace meta-llama

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

**Architecture:** CodeLlama-7B-Instruct + Feedback Granularity Comparison

**Core Mechanism Implementation:**

```python
# Core Mechanism: Feedback Granularity Ablation
# Tests: execution-detailed vs execution-binary feedback

class FeedbackGranularityExperiment:
    """
    Compare edit behavior under different feedback granularity levels.
    IV: Feedback type (detailed vs binary)
    DV: Edit scope (lines changed, AST distance)
    """
    def __init__(self, model, tokenizer, max_iterations=3):
        self.model = model
        self.tokenizer = tokenizer
        self.max_iterations = max_iterations
        self.edit_metrics = []

    def format_detailed_feedback(self, result):
        """Execution-DETAILED: Full error trace with localization."""
        return f"""Error: {result.error_type} at line {result.line_number}
Message: {result.error_message}
Expected: {result.expected}
Actual: {result.actual}
Traceback: {result.traceback[-3:]}"""  # Last 3 lines of traceback

    def format_binary_feedback(self, result):
        """Execution-BINARY: Only pass/fail, no localization."""
        if result.passed:
            return "Test passed."
        else:
            return "Test failed."

    def generate_with_refinement(self, problem, feedback_type="detailed"):
        """
        Args:
            problem: dict with prompt, tests, entry_point
            feedback_type: "detailed" | "binary"
        Returns:
            final_code, pass_status, iterations_used, edit_metrics
        """
        code = self.initial_generate(problem["prompt"])
        iteration_edits = []
        
        for i in range(self.max_iterations):
            result = self.execute_code(code, problem["tests"])
            if result.passed:
                return code, True, i, iteration_edits
            
            # IV manipulation: feedback granularity
            if feedback_type == "detailed":
                feedback = self.format_detailed_feedback(result)
            else:  # binary
                feedback = self.format_binary_feedback(result)
            
            old_code = code
            code = self.refine_code(problem["prompt"], code, feedback)
            
            # DV measurement: edit scope
            edit_scope = self.measure_edit_scope(old_code, code)
            edit_scope["iteration"] = i
            edit_scope["feedback_type"] = feedback_type
            iteration_edits.append(edit_scope)
        
        final_result = self.execute_code(code, problem["tests"])
        return code, final_result.passed, self.max_iterations, iteration_edits

    def measure_edit_scope(self, old_code, new_code):
        """Measure edit scope via diff metrics."""
        import difflib
        diff = list(difflib.unified_diff(
            old_code.splitlines(), new_code.splitlines()
        ))
        lines_changed = sum(1 for d in diff if d.startswith(('+', '-')) 
                          and not d.startswith(('+++', '---')))
        total_lines = max(len(old_code.splitlines()), 1)
        
        return {
            "lines_changed": lines_changed,
            "total_lines": total_lines,
            "change_ratio": lines_changed / total_lines,
            "is_global_rewrite": lines_changed > total_lines * 0.5
        }
```

### Training Protocol

> **Note:** This is a MECHANISM experiment. No training required - uses pretrained models with prompting.

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

**Primary Metrics (Mechanism-focused):**
- **Edit scope (lines_changed):** Average lines changed per refinement iteration
- **Change ratio:** lines_changed / total_lines
- **Global rewrite rate:** Fraction of edits where change_ratio > 0.5
- **pass@1:** Success rate after k=3 iterations (secondary)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation + edit_analysis
- Library: custom (difflib-based)
- Code:
```python
def compute_edit_metrics(edit_records):
    """Aggregate edit scope metrics by feedback type."""
    detailed = [e for e in edit_records if e["feedback_type"] == "detailed"]
    binary = [e for e in edit_records if e["feedback_type"] == "binary"]
    
    return {
        "detailed_avg_lines_changed": np.mean([e["lines_changed"] for e in detailed]),
        "binary_avg_lines_changed": np.mean([e["lines_changed"] for e in binary]),
        "detailed_global_rewrite_rate": np.mean([e["is_global_rewrite"] for e in detailed]),
        "binary_global_rewrite_rate": np.mean([e["is_global_rewrite"] for e in binary]),
    }
```

**Success Criteria:**
- avg_lines_changed(detailed) < avg_lines_changed(binary)
- global_rewrite_rate(detailed) < global_rewrite_rate(binary)

**Expected Baseline Performance (from H-E1):**
- CodeLlama-7B with detailed feedback: ~40% pass@1 (HumanEval)
- Binary feedback expected: ~35% pass@1 (5% degradation hypothesis)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Edit Scope Comparison**: Box plot of lines_changed by feedback type

#### Additional Figures (LLM Autonomous)

Based on experimental results, generate:
1. **Edit scope distribution**: Histogram of change_ratio for detailed vs binary
2. **Global rewrite rate**: Bar chart comparing rewrite rates
3. **Iteration progression**: Lines changed per iteration by feedback type
4. **Success vs edit scope**: Scatter plot of fix success vs edit scope

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions

| Check | Requirement | Verification |
|-------|-------------|--------------|
| mechanism_exists | Detailed vs binary feedback produces different edits | Compare edit scopes |
| mechanism_isolatable | Only feedback granularity changes between conditions | Code review |
| baseline_measurable | Binary feedback produces valid output | Execute with binary feedback |

### Architecture Compatibility
- Model accepts prompt + feedback in context: YES (instruction-tuned)
- Execution sandbox available: YES (reused from H-E1)
- Edit measurement available: YES (difflib stdlib)

### Activation Indicators

| Indicator | Expected |
|-----------|----------|
| feedback_content_differs | Binary: "Test failed." vs Detailed: full trace |
| edit_scope_differs | Detailed edits should be more targeted |
| metric_delta_expected | lines_changed ratio < 0.8 (detailed/binary) |

### Mechanism Verification Code

```python
def verify_mechanism_activation(detailed_edits, binary_edits):
    """Verify feedback granularity mechanism affects edit behavior."""
    import numpy as np
    
    # Check 1: Feedback content differs
    assert detailed_edits[0]["feedback_type"] == "detailed"
    assert binary_edits[0]["feedback_type"] == "binary"
    
    # Check 2: Edit scope differs
    detailed_avg = np.mean([e["lines_changed"] for e in detailed_edits])
    binary_avg = np.mean([e["lines_changed"] for e in binary_edits])
    
    # Check 3: Detailed feedback produces smaller edits
    edit_ratio = detailed_avg / max(binary_avg, 1)
    print(f"Edit scope ratio (detailed/binary): {edit_ratio:.2f}")
    
    mechanism_active = edit_ratio < 1.0  # Detailed should be smaller
    return mechanism_active, {
        "detailed_avg_lines": detailed_avg,
        "binary_avg_lines": binary_avg,
        "edit_ratio": edit_ratio
    }
```

### Hypothesis Support Threshold
- **hypothesis_support_metric:** edit_scope_ratio = lines_changed(detailed) / lines_changed(binary)
- **hypothesis_support_threshold:** edit_scope_ratio < 0.9 (detailed edits 10%+ smaller)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `avg_lines_changed(detailed) < avg_lines_changed(binary)`
3. Mechanism verified: detailed feedback produces more targeted edits

---

## Appendix: Reference Implementations

### Primary References

1. **Self-Debug (Chen et al., 2023)**
   - Paper: "Teaching Large Language Models to Self-Debug"
   - Relevance: Shows detailed error traces improve refinement
   - Ablation: Removing line numbers hurts performance

2. **H-E1 Validation Results**
   - Reused: Execution sandbox, model loading, dataset handling
   - Proven: Refinement loop works on HumanEval/MBPP

### Code References

1. **difflib (Python stdlib)**
   - Purpose: Line-level diff computation
   - Use for: Edit scope measurement

2. **ast (Python stdlib)**
   - Purpose: AST parsing and comparison
   - Use for: Semantic edit distance (optional)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design initiated
- Prerequisite H-E1: VALIDATED
- Status: experiment_design.status = IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
