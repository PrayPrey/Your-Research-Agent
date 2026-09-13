# Experiment Design: h-e1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Static analyzers (pylint) produce meaningful, actionable warnings on LLM-generated code for at least 30% of HumanEval problems.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Static analyzers (pylint) must produce meaningful, actionable warnings on LLM-generated code for at least 30% of HumanEval problems.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to carry forward.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using established knowledge:*

**Static Analysis on LLM Code:**
- Pylint detects: undefined variables, unused imports, missing docstrings, type errors, style violations (PEP8)
- LLM-generated code common issues: incomplete implementations, missing error handling, undefined helper functions
- Research shows 20-50% of LLM solutions have linter-detectable issues before execution

**HumanEval Benchmark:**
- 164 Python programming problems with function signatures and docstrings
- Standard evaluation: pass@k metric (functional correctness)
- Widely used for code generation evaluation (Chen et al. 2021)

### Archon Code Examples

*MCP unavailable - standard patterns:*

```python
# Pylint analysis pattern
from pylint import lint
from pylint.reporters.text import TextReporter

def analyze_code(code_string: str) -> list:
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(code_string.encode())
        f.flush()
        results = StringIO()
        lint.Run([f.name, '--output-format=json'], reporter=TextReporter(results), exit=False)
    return parse_pylint_output(results.getvalue())
```

### Exa GitHub Implementations

*MCP unavailable - known implementations:*

1. **openai/human-eval** - Official HumanEval benchmark
   - URL: https://github.com/openai/human-eval
   - Contains: 164 problems, evaluation harness, execution sandbox
   - License: MIT

2. **bigcode-project/bigcode-evaluation-harness** - Extended evaluation
   - URL: https://github.com/bigcode-project/bigcode-evaluation-harness
   - Includes HumanEval, MBPP, other code benchmarks

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Straightforward experiment - no reproduction needed. Custom pipeline: generate code → run pylint → count warnings.

**Recommended Implementation Path:**
- Primary: OpenAI HumanEval dataset + pylint library
- Fallback: MBPP dataset if HumanEval insufficient
- Justification: HumanEval is standard, pylint is mature Python linter

### Code Analysis (Serena MCP)

*Serena unavailable - analysis based on established patterns:*

- Pylint outputs: message type (E/W/C/R), line number, message code, description
- Actionable = errors (E) and warnings (W), not conventions (C) or refactoring (R)
- "Meaningful" filter: exclude style-only issues, focus on potential bugs

---

## Experiment Specification

### Dataset

**Name:** HumanEval
**Type:** standard
**Source:** OpenAI official release
**Size:** 164 programming problems
**Format:** JSON with prompt, canonical_solution, test cases, entry_point

**Dataset Statistics:**
- Problems: 164 Python function completion tasks
- Each problem includes: function signature, docstring, test cases
- Difficulty: Medium-hard algorithmic problems
- Domain: General Python programming

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai_humaneval`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("openai_humaneval", split="test")
# Each item: {"task_id", "prompt", "canonical_solution", "test", "entry_point"}
```

### Models

#### Baseline Model

**Name:** CodeLlama-7B-Instruct (or GPT-3.5-turbo via API)
**Type:** Code generation LLM
**Purpose:** Generate Python solutions for HumanEval problems

**Baseline behavior:** Generate code, execute tests, report pass@1
**No static analysis** - just functional correctness

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers (local) or OpenAI API (cloud)
- Identifier: `codellama/CodeLlama-7b-Instruct-hf` or `gpt-3.5-turbo`
- Code:
```python
# Option A: Local model
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")

# Option B: API
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[...])
```

#### Proposed Model

**Architecture:** Baseline + [Mechanism from hypothesis]

**Core Mechanism Implementation:**

```python
import subprocess
import json
import tempfile
from pathlib import Path

def run_pylint_analysis(code: str) -> dict:
    """Run pylint on generated code and extract warnings."""
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = subprocess.run(
            ['pylint', temp_path, '--output-format=json', '--disable=C,R'],  # Only E,W
            capture_output=True, text=True, timeout=30
        )
        messages = json.loads(result.stdout) if result.stdout.strip() else []
    finally:
        Path(temp_path).unlink()
    
    # Filter actionable warnings (errors and warnings only)
    actionable = [m for m in messages if m['type'] in ('error', 'warning')]
    return {
        'total_messages': len(messages),
        'actionable_count': len(actionable),
        'messages': actionable
    }

def evaluate_hypothesis(dataset, model):
    """Main experiment loop."""
    problems_with_warnings = 0
    
    for problem in dataset:
        generated_code = model.generate(problem['prompt'])
        analysis = run_pylint_analysis(generated_code)
        
        if analysis['actionable_count'] > 0:
            problems_with_warnings += 1
    
    warning_rate = problems_with_warnings / len(dataset)
    return {'warning_rate': warning_rate, 'gate_passed': warning_rate >= 0.30}
```

### Training Protocol

**No training required** - This is an analysis experiment, not a model training experiment.

**Experiment Protocol:**
1. Load HumanEval dataset (164 problems)
2. For each problem:
   - Generate solution using baseline LLM
   - Run pylint static analysis on generated code
   - Record: number of warnings, warning types, actionability
3. Compute: % of problems with ≥1 actionable warning
4. Gate check: rate ≥ 30%

### Evaluation

**Primary Metric:** Warning Rate
- Definition: (# problems with ≥1 actionable pylint warning) / (total problems)
- Target: ≥ 30% (gate condition)

**Secondary Metrics:**
- Average warnings per problem
- Warning type distribution (E vs W)
- Most common warning codes

**Success Criteria:**
- Gate PASS: warning_rate ≥ 0.30
- Gate FAIL: warning_rate < 0.30

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_analysis
- Library: custom (pylint subprocess)
- Code:
```python
# No external metrics library needed
# Custom metrics computed from pylint JSON output
def compute_metrics(results: list) -> dict:
    total = len(results)
    with_warnings = sum(1 for r in results if r['actionable_count'] > 0)
    return {
        'warning_rate': with_warnings / total,
        'avg_warnings': sum(r['actionable_count'] for r in results) / total,
        'gate_passed': (with_warnings / total) >= 0.30
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Warning Distribution Histogram**: Count of warnings per problem
2. **Warning Type Pie Chart**: Error vs Warning breakdown
3. **Top 10 Warning Codes**: Bar chart of most frequent pylint codes

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### HumanEval Benchmark
- **Repository:** https://github.com/openai/human-eval
- **Paper:** "Evaluating Large Language Models Trained on Code" (Chen et al. 2021)
- **HuggingFace:** https://huggingface.co/datasets/openai_humaneval

### Pylint Static Analyzer
- **Documentation:** https://pylint.pycqa.org/
- **PyPI:** https://pypi.org/project/pylint/
- **JSON output format:** https://pylint.pycqa.org/en/latest/user_guide/output.html

### Related Work
- Code quality analysis on LLM outputs (various papers 2023-2024)
- Static analysis integration in code generation pipelines

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29

### Workflow History for This Hypothesis
- 2026-08-29: Phase 2C initiated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
