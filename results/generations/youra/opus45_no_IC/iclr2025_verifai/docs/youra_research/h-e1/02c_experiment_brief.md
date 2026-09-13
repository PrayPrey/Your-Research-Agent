# Experiment Design: H-E1

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** Error classes targeted by grammar constraints, static analysis, and SMT-guided repair are largely independent (overlap < 30% Jaccard index)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Jaccard < 0.30 required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
Jaccard index < 0.30 for all strategy pairs (grammar vs static, grammar vs SMT, static vs SMT)

---

## Continuation Context

This is the foundation hypothesis - first in verification chain. No previous results to build on.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in sequence.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for Jaccard similarity in code generation context. Standard set overlap metrics apply:
- Jaccard Index = |A ∩ B| / |A ∪ B|
- Used in evaluation pipelines for comparing model outputs

### Archon Code Examples

No direct Jaccard implementation examples found. Standard Python implementation straightforward:
```python
def jaccard_index(set_a, set_b):
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0
```

### Exa GitHub Implementations

**Grammar-Constrained Decoding:**
1. **eth-sri/type-constrained-code-generation** (PLDI 2025) - 99 stars
   - Type-safe incremental parsing for constrained LLM generation
   - TypeScript focus but demonstrates technique
   
2. **structuredllm/syncode** - 337 stars
   - Grammar-augmented LLM generation framework
   - Supports Python grammar constraints
   - 99% accuracy on JSON, transferable to code
   
3. **guidance-ai/llguidance** - 803 stars
   - Shipped in OpenAI, vLLM, llama.cpp
   - Production-grade constrained decoding

4. **epfl-dlab/GCD** - 57 stars
   - Grammar-Constrained Decoding for Structured NLP
   - HuggingFace Transformers integration via transformers-CFG

5. **amazon-science/incremental-parsing** - 18 stars
   - Incremental Python parser for constrained generation
   - Paper: "Constrained Decoding for Fill-in-the-Middle Code Language Models" (arXiv:2402.17988)

**HumanEval Evaluation:**
- **openai/human-eval** - Official benchmark, 3K+ stars
- 164 problems, JSONL format, `evaluate_functional_correctness` script
- `pass@k` metric computation built-in

**Static Analysis (Bandit/Pylint):**
- Bandit: 300+ security tests, CWE-mapped, AST-based
- Pylint: 200+ rules, semantic analysis via AST
- Integration: `pip install pylint bandit`, run via CLI

**Z3 SMT Solver:**
- **Z3Prover/z3** - 12,349 stars
- Python bindings: `from z3 import *`
- Used for formal verification of code properties

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Source | Priority | Rationale |
|--------|----------|-----------|
| openai/human-eval | Primary | Official benchmark, standardized evaluation |
| structuredllm/syncode | Primary | Active, well-documented, Python support |
| Bandit/Pylint | Primary | Standard tools, pip-installable |
| Z3Prover/z3 | Primary | Official solver, Python bindings |

**Recommended Implementation Path:**
- Primary: Use existing tools (syncode, Bandit, Pylint, Z3) with HumanEval benchmark
- Fallback: Implement minimal grammar checker if syncode integration complex
- Justification: All components well-established, avoid reimplementation

### Code Analysis (Serena MCP)

Serena analysis not required - using external benchmarks and tools, no codebase-specific implementation patterns needed.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | HumanEval |
| **Source** | openai/human-eval (GitHub) |
| **Size** | 164 problems |
| **Split** | All 164 (no train/test split needed for overlap analysis) |
| **Format** | JSONL with prompt, test, entry_point |

**Preprocessing:**
1. Load via `human_eval.data.read_problems()`
2. Generate n=10 samples per problem per model
3. Total: 164 × 10 × 2 models = 3,280 code samples

**Loading Information** (for Phase 4 download):
- Method: pip install + git clone
- Identifier: `pip install human-eval` or `git clone https://github.com/openai/human-eval`
- Code:
```python
from human_eval.data import read_problems
problems = read_problems()  # Dict[task_id, problem_dict]
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Models** | CodeLlama-7B-hf, GPT-4 |
| **Source** | meta-llama/CodeLlama-7b-hf (HF), OpenAI API |
| **Temperature** | 0.2 |
| **Samples per problem** | n=10 |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers / OpenAI API
- Identifier: `meta-llama/CodeLlama-7b-hf`, `gpt-4`
- Code:
```python
# CodeLlama
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-hf")

# GPT-4
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(model="gpt-4", messages=[...])
```

#### Proposed Model

**Architecture:** Baseline + Three verification strategies applied independently

**Core Mechanism Implementation:**

```python
# Core Experiment: Measure error class overlap via Jaccard index

def run_verification_strategies(samples: list[dict]) -> dict[str, set]:
    """Apply each strategy, return sets of improved problem IDs."""
    
    grammar_improved = set()
    static_improved = set()
    smt_improved = set()
    
    for sample in samples:
        task_id = sample["task_id"]
        code = sample["completion"]
        
        # Strategy 1: Grammar constraints (syntax)
        # Check if code has syntax errors
        baseline_syntax_ok = check_syntax(code)
        constrained_code = apply_grammar_constraints(code)
        constrained_syntax_ok = check_syntax(constrained_code)
        if constrained_syntax_ok and not baseline_syntax_ok:
            grammar_improved.add(task_id)
        
        # Strategy 2: Static analysis (semantics)
        # Run Bandit + Pylint
        baseline_issues = run_static_analysis(code)
        fixed_code = apply_static_feedback(code, baseline_issues)
        fixed_issues = run_static_analysis(fixed_code)
        if len(fixed_issues) < len(baseline_issues):
            static_improved.add(task_id)
        
        # Strategy 3: SMT repair (specifications)
        # Apply Z3-based verification (HumanEval-Verus subset)
        if has_formal_spec(task_id):
            baseline_spec_pass = verify_spec(code, task_id)
            repaired_code = smt_guided_repair(code, task_id)
            repaired_spec_pass = verify_spec(repaired_code, task_id)
            if repaired_spec_pass and not baseline_spec_pass:
                smt_improved.add(task_id)
    
    return {
        "grammar": grammar_improved,
        "static": static_improved,
        "smt": smt_improved
    }

def compute_jaccard_overlap(sets: dict[str, set]) -> dict[str, float]:
    """Compute pairwise Jaccard indices."""
    pairs = [
        ("grammar", "static"),
        ("grammar", "smt"),
        ("static", "smt")
    ]
    results = {}
    for a, b in pairs:
        intersection = len(sets[a] & sets[b])
        union = len(sets[a] | sets[b])
        jaccard = intersection / union if union > 0 else 0.0
        results[f"{a}_vs_{b}"] = jaccard
    return results

# Main execution
improved_sets = run_verification_strategies(all_samples)
overlaps = compute_jaccard_overlap(improved_sets)
# Gate check: all overlaps < 0.30
```

### Training Protocol

**No training required** - This is an analysis experiment measuring error class overlap.

| Parameter | Value |
|-----------|-------|
| **Type** | Inference + Analysis |
| **GPU** | 1x A100 (for CodeLlama inference) |
| **Inference time** | ~30 min for 3,280 samples |
| **Analysis time** | ~10 min for overlap computation |

### Evaluation

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **Jaccard(grammar, static)** | Overlap between grammar-improved and static-improved sets | < 0.30 |
| **Jaccard(grammar, smt)** | Overlap between grammar-improved and SMT-improved sets | < 0.30 |
| **Jaccard(static, smt)** | Overlap between static-improved and SMT-improved sets | < 0.30 |
| **Mean Jaccard** | Average of all pairwise overlaps | < 0.30 |

**PoC Success Criteria:**
- Primary: All pairwise Jaccard indices < 0.30
- Secondary: Mean Jaccard < 0.25 (strong independence)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Set overlap analysis
- Library: Built-in Python set operations
- Code:
```python
def jaccard_index(set_a: set, set_b: set) -> float:
    if len(set_a | set_b) == 0:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing all 3 pairwise Jaccard indices vs 0.30 threshold line

#### Additional Figures (LLM Autonomous)

1. **Venn Diagram**: 3-circle Venn showing overlap between grammar/static/SMT improved sets
2. **Per-Model Comparison**: Side-by-side Jaccard values for CodeLlama-7B vs GPT-4
3. **Problem Category Heatmap**: Which problem types are improved by which strategies

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. All Jaccard indices < 0.30

**Gate Decision:**
- PASS: Proceed to H-M1 (grammar constraints mechanism)
- FAIL: STOP - reassess multiplicative model, investigate overlap sources

---

## Appendix: Reference Implementations

### Grammar-Constrained Decoding
| Repository | Stars | Notes |
|------------|-------|-------|
| structuredllm/syncode | 337 | Primary choice - Python CFG support |
| guidance-ai/llguidance | 803 | Production-grade, vLLM integration |
| epfl-dlab/transformers-CFG | ~100 | HuggingFace native |

### Static Analysis
| Tool | Purpose | Install |
|------|---------|---------|
| Bandit | Security vulnerabilities | `pip install bandit` |
| Pylint | Code quality/bugs | `pip install pylint` |

### SMT Verification
| Tool | Purpose | Install |
|------|---------|---------|
| Z3 | SMT solving | `pip install z3-solver` |

### HumanEval Extensions
| Dataset | Purpose | Source |
|---------|---------|--------|
| HumanEval | Base benchmark | openai/human-eval |
| HumanEval-Verus | Formal specs (23 problems) | secure-foundations/human-eval-verus |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis
- 2026-08-12: Phase 2C started - experiment design
- 2026-08-12: MCP research completed (Archon KB, Exa GitHub)
- 2026-08-12: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
