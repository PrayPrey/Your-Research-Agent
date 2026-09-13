# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Structured error format achieves statistically significant higher repair success rate than raw compiler output on HumanEval+ and MBPP+ benchmarks across CodeLlama-7B, CodeLlama-34B, and GPT-4
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for h-e1)
**Gate Status:** MUST_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Structured error format must achieve higher repair success rate than raw compiler output. This is a MUST_WORK gate - failure stops the pipeline.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query: "structured error format code repair"**

Key findings from research literature:
1. **Error Parsing Approaches**: Modern code repair systems parse compiler diagnostics into structured JSON with line numbers, error categories, and normalized messages
2. **Input Format Impact**: Studies show that structured error context improves LLM repair performance by providing clearer signals about error location and type
3. **Common Patterns**: Error blocks typically contain: file name, line number, error code, error description, and suggested fix

**Query: "LLM code repair benchmark evaluation"**

1. **EvalPlus Framework**: Standard benchmark extending HumanEval and MBPP with 80x and 35x more test cases respectively
2. **Evaluation Protocol**: Generate code, execute tests, measure pass@k metrics
3. **Repair Loop**: Submit code → compile → parse errors → prompt LLM → iterate

### Archon Code Examples

**Structured Error Format Pattern:**
```python
class StructuredError:
    def __init__(self, raw_output: str):
        self.line_number: int = None
        self.error_type: str = None  # syntax, type, name, attribute
        self.error_message: str = None
        self.code_context: str = None  # surrounding lines
        self.suggested_fix: str = None
    
    def to_prompt_format(self) -> str:
        return f"""Error at line {self.line_number}:
Type: {self.error_type}
Message: {self.error_message}
Context:
{self.code_context}
"""
```

### Exa GitHub Implementations

**[VERIFIED - WebSearch]** evalplus/evalplus
- URL: https://github.com/evalplus/evalplus
- Description: Official EvalPlus benchmark implementation for HumanEval+ and MBPP+
- Installation: `pip install evalplus`
- HuggingFace: `evalplus/humanevalplus`

**[VERIFIED - WebSearch]** CCrepairBench
- URL: https://arxiv.org/html/2509.15690
- Description: High-fidelity benchmark for compilation repair with structured error parsing
- Relevance: ErrorParser converts unstructured diagnostics to structured JSON

**[VERIFIED - WebSearch]** FastFixer
- URL: https://arxiv.org/pdf/2410.21285
- Description: CodeLlama-7B fine-tuned for code repair using LoRA
- Training: LR=1e-4, batch=4, LoRA rank=8, max_length=4096

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Source | Priority | Justification |
|--------|----------|---------------|
| evalplus/evalplus | P1 | Official benchmark, standard evaluation |
| HuggingFace CodeLlama | P1 | Official model weights |
| FastFixer pattern | P2 | Proven fine-tuning approach |

**Recommended Implementation Path:**
- Primary: Use evalplus library for benchmark evaluation, HuggingFace for model loading
- Fallback: Direct HumanEval/MBPP dataset loading from HuggingFace datasets
- Justification: evalplus is the standard tool; CodeLlama models are officially available

### Code Analysis (Serena MCP)

Not available - proceeding without Serena analysis. Core patterns identified from web research are sufficient for implementation.

---

## Experiment Specification

### Dataset

**Dataset 1: HumanEval+**
- **Name:** HumanEval+ (EvalPlus extended)
- **Type:** standard
- **Source:** evalplus/humanevalplus on HuggingFace
- **Size:** 164 problems with 80x more test cases than original
- **Task:** Python function generation from docstring
- **Splits:** Full set used for evaluation

**Dataset 2: MBPP+**
- **Name:** MBPP+ (EvalPlus extended)
- **Type:** standard
- **Source:** evalplus/mbppplus on HuggingFace
- **Size:** 399 problems (human-verified subset) with 35x more test cases
- **Task:** Python function generation from natural language description
- **Splits:** Full set used for evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + evalplus library
- Identifier: `evalplus/humanevalplus`, `evalplus/mbppplus`
- Code:
```python
# Option 1: evalplus library (recommended)
pip install evalplus
evalplus.evaluate --model MODEL --dataset humaneval --backend hf

# Option 2: Direct HuggingFace loading
from datasets import load_dataset
humaneval_plus = load_dataset("evalplus/humanevalplus")
mbpp_plus = load_dataset("evalplus/mbppplus")
```

### Models

#### Baseline Model

**Model 1: CodeLlama-7B-Instruct**
- **Architecture:** LLaMA-based, 7B parameters, instruction-tuned
- **Source:** HuggingFace `codellama/CodeLlama-7b-Instruct-hf`
- **Purpose:** Smaller model, faster iteration, resource-efficient baseline

**Model 2: CodeLlama-34B-Instruct**
- **Architecture:** LLaMA-based, 34B parameters, instruction-tuned
- **Source:** HuggingFace `codellama/CodeLlama-34b-Instruct-hf`
- **Purpose:** Larger model to test scaling effects

**Model 3: GPT-4**
- **Architecture:** OpenAI proprietary
- **Source:** OpenAI API
- **Purpose:** State-of-the-art comparison point

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers + OpenAI API
- Identifier: `codellama/CodeLlama-7b-Instruct-hf`, `codellama/CodeLlama-34b-Instruct-hf`, `gpt-4`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# CodeLlama-7B
model_7b = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-Instruct-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer_7b = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")

# CodeLlama-34B
model_34b = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-34b-Instruct-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)

# GPT-4
import openai
client = openai.OpenAI()
response = client.chat.completions.create(model="gpt-4", messages=[...])
```

#### Proposed Model

**Architecture:** Same models as baseline, but with structured error format in prompt

**Core Mechanism Implementation:**

```python
import re
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class StructuredError:
    """Parsed compiler error in structured format."""
    line_number: int
    error_type: str  # SyntaxError, TypeError, NameError, AttributeError, etc.
    error_message: str
    code_context: List[str]  # Lines around the error
    
def parse_compiler_output(raw_output: str, source_code: str) -> StructuredError:
    """Convert raw compiler output to structured format."""
    # Extract line number
    line_match = re.search(r'line (\d+)', raw_output, re.IGNORECASE)
    line_number = int(line_match.group(1)) if line_match else 0
    
    # Extract error type
    error_type_match = re.search(r'(\w+Error|\w+Exception)', raw_output)
    error_type = error_type_match.group(1) if error_type_match else "UnknownError"
    
    # Extract error message (text after the error type)
    msg_match = re.search(rf'{error_type}:\s*(.+?)(?:\n|$)', raw_output)
    error_message = msg_match.group(1).strip() if msg_match else raw_output
    
    # Extract code context (3 lines before and after)
    lines = source_code.split('\n')
    start = max(0, line_number - 3)
    end = min(len(lines), line_number + 2)
    code_context = [f"{i+1}: {lines[i]}" for i in range(start, end)]
    
    return StructuredError(
        line_number=line_number,
        error_type=error_type,
        error_message=error_message,
        code_context=code_context
    )

def format_structured_prompt(error: StructuredError, original_code: str) -> str:
    """Format structured error for LLM prompt."""
    context_str = '\n'.join(error.code_context)
    return f"""Fix the following Python code error.

## Error Information
- **Line:** {error.line_number}
- **Type:** {error.error_type}
- **Message:** {error.error_message}

## Code Context (around error):
```python
{context_str}
```

## Full Code:
```python
{original_code}
```

Provide the corrected complete code:
"""

def format_raw_prompt(raw_output: str, original_code: str) -> str:
    """Format raw compiler output for LLM prompt (baseline)."""
    return f"""Fix the following Python code based on the error.

## Compiler Output:
{raw_output}

## Code:
```python
{original_code}
```

Provide the corrected complete code:
"""

# Main comparison logic
def repair_with_structured(model, tokenizer, code: str, raw_error: str) -> str:
    """Repair using structured error format."""
    error = parse_compiler_output(raw_error, code)
    prompt = format_structured_prompt(error, code)
    return generate_code(model, tokenizer, prompt)

def repair_with_raw(model, tokenizer, code: str, raw_error: str) -> str:
    """Repair using raw compiler output (baseline)."""
    prompt = format_raw_prompt(raw_error, code)
    return generate_code(model, tokenizer, prompt)
```

### Training Protocol

**No training required** - This is an inference-only experiment comparing prompt formats.

**Inference Configuration:**
- Temperature: 0.0 (greedy decoding for reproducibility)
- Max new tokens: 512
- Batch size: 1 (sequential evaluation)
- Number of repair attempts: 5 per problem (to measure repair success rate)

**Experimental Protocol:**
1. Generate initial code from problem description
2. Execute code against test cases
3. If fails: parse error, create prompt (structured vs raw), generate repair
4. Repeat repair loop up to 5 times
5. Record pass@1 after each repair attempt

### Evaluation

**Primary Metrics:**
- **Pass@1**: Percentage of problems solved correctly after repair
- **Repair Success Rate**: (problems_fixed / problems_with_errors) × 100
- **Repair Attempts to Success**: Average number of repair iterations needed

**Comparison:**
- Structured Error Format vs Raw Compiler Output
- Across 3 models: CodeLlama-7B, CodeLlama-34B, GPT-4
- Across 2 benchmarks: HumanEval+, MBPP+

**Success Criteria (PoC):**
- Structured format shows higher Pass@1 than raw format
- Direction of improvement consistent across at least 2 of 3 models

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code Generation / Code Repair
- Library: evalplus (built-in execution and evaluation)
- Code:
```python
# evalplus handles execution and pass@k computation
from evalplus.evaluate import evaluate_functional_correctness

results = evaluate_functional_correctness(
    sample_file="samples.jsonl",
    k=[1],
    n_workers=4,
    timeout=3.0
)
pass_at_1 = results["pass@1"]
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing Pass@1 for Structured vs Raw format across all 3 models

#### Additional Figures (LLM Autonomous)

1. **Repair Success Rate by Model**: Grouped bar chart showing repair success rate
2. **Repair Iterations Distribution**: Histogram of attempts needed to fix per problem
3. **Error Type Breakdown**: Stacked bar showing which error types benefit most from structured format
4. **HumanEval+ vs MBPP+ Comparison**: Side-by-side comparison across benchmarks

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `structured_pass@1 > raw_pass@1` for majority of model/benchmark combinations

---

## Appendix: Reference Implementations

### EvalPlus Benchmark
- **Repository:** https://github.com/evalplus/evalplus
- **Paper:** "Is Your Code Generated by ChatGPT Really Correct?" (NeurIPS 2023)
- **HuggingFace:** evalplus/humanevalplus, evalplus/mbppplus
- **Installation:** `pip install evalplus`

### CodeLlama Models
- **7B Instruct:** https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf
- **34B Instruct:** https://huggingface.co/codellama/CodeLlama-34b-Instruct-hf
- **Paper:** "Code Llama: Open Foundation Models for Code" (Meta AI, 2023)

### Related Code Repair Work
- **CCrepairBench:** High-fidelity C++ compilation repair benchmark with structured error parsing
- **FastFixer:** CodeLlama fine-tuning for code repair (LoRA, LR=1e-4, batch=4)
- **MORepair:** Multi-objective fine-tuning for code repair

### Error Parsing Patterns
- **WARP Framework:** Structured error context formatted into prompts
- **Shadow Job Pipeline:** Error blocks with file, line, code, description

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C experiment design completed
- experiment_design.status: COMPLETED
- experiment_design.file: 02c_experiment_brief.md

---

*MCP Tools Used: WebSearch (EvalPlus, CodeLlama, code repair research)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
