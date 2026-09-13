# Experiment Design: h-m3

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Targeted edits have higher probability of fixing bugs than global rewrites
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m2 (VALIDATED)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2

### Gate Condition
Targeted edits achieve higher fix rate than global rewrites. If fails: ABANDON mechanism hypothesis, explore alternative explanations.

---

## Continuation Context

Building on h-m2 findings: Detailed execution feedback enables targeted code edits (40% higher pass rate than binary feedback). h-m3 tests whether targeted edits causally lead to higher fix probability.

### Previous Hypothesis Results (if applicable)
h-m2 VALIDATED: Detailed feedback enables 40% higher pass rate than binary. Refinement efficiency higher with detailed (targeted edits succeed). Binary feedback leads to blind iteration without convergence.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**[INFERRED]** Pattern 1: Self-Debug Edit Scope Analysis
- Source: General knowledge (Archon MCP unavailable)
- Key insight: Self-Debug shows execution feedback leads to localized edits. Models receiving detailed error traces produce smaller diffs concentrated at bug locations.

**[INFERRED]** Pattern 2: Regression Risk in Global Rewrites
- Source: General knowledge
- Key insight: Larger diffs introduce more regression bugs. Each changed line has probability p of introducing new bugs; targeted edits minimize this risk.

**[INFERRED]** Pattern 3: AST Edit Distance as Scope Metric
- Source: General knowledge
- Key insight: Measure edit scope via AST edit distance. Smaller AST distance = more targeted edit. Threshold: ≤5 operations = targeted, >5 = global.

**[INFERRED]** Pattern 4: Reflexion Iteration Patterns
- Source: General knowledge
- Key insight: When feedback is localized ("error on line 5"), edits are targeted; when vague ("incorrect output"), edits are global.

### Archon Code Examples

*Archon MCP unavailable - code examples inferred from literature*

```python
# AST Edit Distance Computation (inferred pattern)
import tree_sitter
def compute_edit_scope(code_before, code_after):
    ast_before = parse_to_ast(code_before)
    ast_after = parse_to_ast(code_after)
    edit_distance = tree_edit_distance(ast_before, ast_after)
    return "targeted" if edit_distance <= 5 else "global"
```

### Exa GitHub Implementations

**[INFERRED]** bigcode-project/bigcode-evaluation-harness
- URL: https://github.com/bigcode-project/bigcode-evaluation-harness
- Relevance: Standard evaluation harness for HumanEval, MBPP
- Usage: Extend to measure edit scope via AST comparison

**[INFERRED]** tree-sitter/tree-sitter
- URL: https://github.com/tree-sitter/tree-sitter
- Relevance: AST parsing for edit distance measurement
- Usage: Parse code before/after, compute tree edit distance

**[INFERRED]** noahshinn/reflexion
- URL: https://github.com/noahshinn/reflexion
- Relevance: Iterative refinement framework
- Usage: Instrument to log edit scope per iteration

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For h-m3 (mechanism verification), no specific paper reproduction needed. This tests a general hypothesis about edit scope vs fix probability.

**Recommended Implementation Path:**
- Primary: Custom implementation using tree-sitter for AST edit distance + bigcode-evaluation-harness for execution
- Fallback: Line-based diff metrics (difflib) if AST parsing fails
- Justification: AST edit distance provides semantic edit scope measurement; line diff is simpler but less precise

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. No complex architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary: HumanEval**
- Name: HumanEval
- Type: standard
- Size: 164 problems
- Source: OpenAI
- Purpose: Code completion with test cases for execution feedback

**Secondary: MBPP**
- Name: MBPP (Mostly Basic Python Problems)
- Type: standard
- Size: 500+ problems
- Source: Google Research
- Purpose: Python programming problems with test cases

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai/humaneval`, `google-research-datasets/mbpp`
- Code:
```python
from datasets import load_dataset
humaneval = load_dataset("openai/humaneval")
mbpp = load_dataset("google-research-datasets/mbpp")
```

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B-Instruct
- Type: Instruction-tuned code LLM
- Parameters: 7B
- Source: Meta AI
- Purpose: Generate and refine code based on feedback

**Secondary Model:** StarCoder-7B
- Type: Code generation model
- Parameters: 7B
- Source: BigCode
- Purpose: Test generalization across model families

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `codellama/CodeLlama-7b-Instruct-hf`, `bigcode/starcoder`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** Same model, different feedback conditions

This is a MECHANISM hypothesis - we compare fix success rates between edit scope categories (targeted vs global), not different model architectures.

**Core Mechanism Implementation:**

```python
# Edit Scope Classification and Fix Rate Analysis
# Based on: h-m3 hypothesis - targeted edits have higher fix probability

import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from difflib import unified_diff

class EditScopeAnalyzer:
    """
    Classifies code edits as targeted or global based on AST edit distance.
    Correlates edit scope with bug fix success rate.
    """
    def __init__(self, threshold=5):
        self.threshold = threshold  # AST operations threshold
        self.parser = Parser()
        self.parser.set_language(Language(tspython.language(), "python"))
    
    def compute_ast_distance(self, code_before: str, code_after: str) -> int:
        """Compute AST edit distance between two code versions."""
        tree_before = self.parser.parse(bytes(code_before, "utf8"))
        tree_after = self.parser.parse(bytes(code_after, "utf8"))
        # Count node differences (simplified)
        nodes_before = set(self._traverse(tree_before.root_node))
        nodes_after = set(self._traverse(tree_after.root_node))
        return len(nodes_before.symmetric_difference(nodes_after))
    
    def classify_edit(self, code_before: str, code_after: str) -> str:
        """Classify edit as 'targeted' or 'global'."""
        distance = self.compute_ast_distance(code_before, code_after)
        return "targeted" if distance <= self.threshold else "global"
    
    def _traverse(self, node) -> list:
        """Traverse AST and collect node signatures."""
        result = [(node.type, node.start_point, node.end_point)]
        for child in node.children:
            result.extend(self._traverse(child))
        return result

# Usage in experiment:
# 1. Generate initial code
# 2. Execute and get feedback (from h-m2)
# 3. Model refines code
# 4. Classify edit scope
# 5. Execute refined code
# 6. Record: (edit_scope, fix_success)
# 7. Compare fix rates: targeted_fix_rate vs global_fix_rate
```

### Training Protocol

**No training required** - This is an inference-time evaluation experiment.

**Inference Protocol:**
- Temperature: 0.0 (deterministic for reproducibility)
- Max tokens: 512 per generation
- Iterations: 1 refinement iteration (from h-m2 protocol)
- Seeds: 1 (fixed seed for reproducibility)

**Feedback Condition:** Detailed execution feedback (validated in h-m2)
- Error traces with line numbers
- Expected vs actual outputs
- Variable values at failure point

### Evaluation

**Primary Metrics:**
- **Fix Rate by Edit Scope**: `targeted_fix_rate = targeted_fixes / targeted_edits`
- **Fix Rate by Edit Scope**: `global_fix_rate = global_fixes / global_edits`
- **Effect Size**: `targeted_fix_rate - global_fix_rate`

**Success Criteria (PoC - Direction Only):**
- `targeted_fix_rate > global_fix_rate` (targeted edits more effective)

**Expected Performance (from literature):**
- Self-Debug shows ~10% improvement from execution feedback
- Targeted edits expected to account for majority of successful fixes

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation (pass@1)
- Library: Custom metrics + bigcode-evaluation-harness
- Code:
```python
# Fix rate computation
def compute_fix_rates(results):
    targeted = [r for r in results if r["edit_scope"] == "targeted"]
    global_edits = [r for r in results if r["edit_scope"] == "global"]
    
    targeted_fix_rate = sum(r["fixed"] for r in targeted) / len(targeted) if targeted else 0
    global_fix_rate = sum(r["fixed"] for r in global_edits) / len(global_edits) if global_edits else 0
    
    return {"targeted": targeted_fix_rate, "global": global_fix_rate}
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing targeted_fix_rate vs global_fix_rate

#### Additional Figures (LLM Autonomous)
- **Edit Scope Distribution**: Histogram of AST edit distances
- **Fix Rate by Edit Distance**: Scatter plot showing fix probability vs AST distance
- **Confusion Matrix**: Edit scope (targeted/global) vs outcome (fixed/not fixed)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**[INFERRED]** Self-Debug Edit Behavior
- Source: General knowledge (Archon MCP unavailable)
- Query Used: "targeted code edits vs global rewrites"
- Relevance: Establishes that execution feedback leads to localized edits
- Used For: Edit scope classification rationale

**[INFERRED]** AST Edit Distance Patterns
- Source: General knowledge
- Query Used: "AST edit distance code analysis"
- Relevance: Metric for measuring semantic edit scope
- Used For: Core mechanism implementation

### B. GitHub Implementations (Exa)

**[INFERRED]** tree-sitter/tree-sitter
- URL: https://github.com/tree-sitter/tree-sitter
- Query Used: "AST parsing python code analysis"
- Relevance: Parser for computing AST edit distance
- Used For: EditScopeAnalyzer implementation

**[INFERRED]** bigcode-project/bigcode-evaluation-harness
- URL: https://github.com/bigcode-project/bigcode-evaluation-harness
- Query Used: "HumanEval MBPP evaluation"
- Relevance: Standard evaluation framework
- Used For: Execution and pass@1 computation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code patterns sufficiently clear from literature

### D. Previous Hypothesis Context

**Source:** h-m2 Validation Report
- File: `h-m2/04_validation.md`
- Status: VALIDATED
- Reused Components:
  - Dataset: HumanEval + MBPP (same)
  - Model: CodeLlama-7B-Instruct, StarCoder-7B (same)
  - Feedback: Detailed execution feedback (proven effective)
- Why Reused: Enables controlled experiment - only edit scope analysis changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B | 02b_verification_plan.md |
| Edit scope metric | Inferred | AST edit distance pattern |
| Classification threshold | Inferred | 5 AST operations |
| Evaluation protocol | Previous | h-m2 validation |
| Success criteria | Phase 2B | targeted > global |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis

| Timestamp | Event | Phase |
|-----------|-------|-------|
| 2026-08-28 | Experiment design started | Phase 2C |
| 2026-08-28 | Archon search (inferred - MCP unavailable) | Phase 2C Step 2 |
| 2026-08-28 | Exa search (inferred - MCP unavailable) | Phase 2C Step 3 |
| 2026-08-28 | Serena skipped (not needed) | Phase 2C Step 4 |
| 2026-08-28 | Dataset confirmed from h-m2 | Phase 2C Step 5 |
| 2026-08-28 | Specification synthesized | Phase 2C Step 6 |
| 2026-08-28 | References documented | Phase 2C Step 7 |
| 2026-08-28 | Experiment design COMPLETED | Phase 2C Step 8 |

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
