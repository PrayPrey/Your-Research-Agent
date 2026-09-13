# Experiment Design: H-M1

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** Grammar-constrained decoding reduces compilation errors by >50% compared to baseline through prefix automata enforcement
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> MECHANISM Hypothesis - Tests causal mechanism of grammar constraint effectiveness

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 validated with Jaccard < 0.30)
**Gate Status:** MUST_WORK - Compilation errors must decrease with grammar constraints

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
Compilation errors decrease with grammar-constrained decoding applied (constrained < baseline).

---

## Continuation Context

### Previous Hypothesis Results (H-E1)

**Gate Status:** PASS
- grammar_vs_static Jaccard: 0.2012
- grammar_vs_smt Jaccard: 0.0244
- static_vs_smt Jaccard: 0.0
- Mean overlap: 0.0752 (threshold: 0.30)

**Implication:** Error class independence confirmed. Grammar constraints target distinct error class from static analysis and SMT, validating that grammar-constrained decoding provides unique value in the pipeline.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Grammar Constrained Decoding Experiment**
- Limited direct results in KB for code generation grammar constraints
- Related work on consistency decoding and structured generation found

**Query 2: Constrained Decoding Implementation**
- References to OpenReview papers on decoding strategies
- DFA-based approaches mentioned for efficient constraint enforcement

### Archon Code Examples

- No direct grammar-constrained code generation examples in KB
- Redirected to Exa search for implementation code

### Exa GitHub Implementations

**Repository 1**: [structuredllm/syncode](https://github.com/structuredllm/syncode) (337 stars)
- **URL**: https://github.com/structuredllm/syncode
- **Relevance**: State-of-the-art grammar-constrained decoding framework for LLMs
- **Key Results**: 96.07% syntax error reduction on Python and Go code
- **Architecture**: DFA mask store for efficient token filtering
- **Key Features**:
  - Works with any HuggingFace model
  - Built-in CFGs for Python, Go, Java, SQL, JSON
  - Supports greedy, beam search, nucleus sampling
  - ~10% generation overhead

**Key Code** (from SynCode):
```python
from syncode import Syncode

# Load grammar-constrained model
syn_llm = Syncode(
    model="meta-llama/CodeLlama-7b-hf",
    mode='grammar_strict',  # or 'grammar_mask'
    grammar='python',
    quantize=True,
    device='cuda'
)

# Generate with constraints
output = syn_llm.infer(prompt)
```

**Training Config**: N/A (inference-time constraint, no training required)

**Repository 2**: [openai/human-eval](https://github.com/openai/human-eval) (3333 stars)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Standard benchmark for code generation evaluation
- **Dataset**: 164 programming problems with function signatures, docstrings, and unit tests
- **Evaluation**: Pass@k metric with sandboxed execution

**Paper Reference**: Ugare et al. 2024, "SynCode: LLM Generation with Grammar Augmentation" (arXiv:2403.01632)
- Demonstrates 96.07% syntax error reduction
- Uses offline-constructed DFA mask store
- Soundness and completeness guarantees for CFG

### Implementation Priority Assessment

**CRITICAL: For mechanism verification, use established implementation**

**Recommended Implementation Path:**
- Primary: SynCode library (pip install syncode)
- Fallback: Outlines library (alternative grammar constraint framework)
- Justification: SynCode has proven 96% syntax error reduction, direct HuggingFace integration, and built-in Python grammar

### Code Analysis (Serena MCP)

*Skipped* - SynCode library provides ready-to-use implementation; no complex code analysis needed.

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval
**Type**: standard

**Statistics**:
- Total problems: 164
- Split: test only (no train/val)
- Format: Function signature + docstring + unit tests
- Language: Python

**Preprocessing**:
- Extract prompts from dataset
- Use function signature + docstring as generation prompt
- Generate n=10 samples per problem at temperature=0.2

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai/openai_humaneval`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("openai/openai_humaneval", split="test")
# Or via evalplus:
from evalplus.data import get_human_eval_plus
problems = get_human_eval_plus()
```

### Models

#### Baseline Model

**Architecture**: CodeLlama-7B (autoregressive LLM)
**Configuration**:
- Parameters: 7B
- Context: 16K tokens
- Vocabulary: 32K tokens

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/CodeLlama-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/CodeLlama-7b-hf",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-hf")
```

#### Proposed Model

**Architecture**: CodeLlama-7B + Grammar-Constrained Decoding (SynCode)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Grammar-Constrained Decoding via SynCode
# Based on: Ugare et al. 2024 (arXiv:2403.01632)

from syncode import Syncode

class GrammarConstrainedGenerator:
    """
    Wraps LLM with grammar constraints using DFA mask store.
    Ensures syntactically valid Python code at generation time.
    """
    def __init__(self, model_name, grammar='python'):
        # Initialize SynCode with Python grammar
        self.syn_llm = Syncode(
            model=model_name,
            mode='grammar_strict',
            grammar=grammar,
            quantize=True,
            device='cuda'
        )
    
    def generate(self, prompt, num_samples=10, temperature=0.2):
        """
        Generate code with grammar constraints.
        
        Args:
            prompt: Function signature + docstring
            num_samples: Number of samples to generate
            temperature: Sampling temperature
        Returns:
            List of syntactically valid code completions
        """
        completions = []
        for _ in range(num_samples):
            output = self.syn_llm.infer(
                prompt,
                temperature=temperature,
                max_new_tokens=512
            )
            completions.append(output)
        return completions

# Integration: Replace standard model.generate() with syn_llm.infer()
```

### Training Protocol

**Note**: Grammar-constrained decoding is an inference-time technique. No training required.

**Generation Parameters**:
- **Temperature**: 0.2 (from Phase 2A controlled variables)
- **Max tokens**: 512
- **Samples per problem**: n=10
- **Total generations**: 164 problems × 10 samples = 1,640 samples

**Baseline Generation**:
- Standard autoregressive decoding (no constraints)
- Same temperature and sampling parameters

**Constrained Generation**:
- SynCode grammar_strict mode
- Python CFG enforced via DFA mask store

**Seeds**: 1 (fixed for reproducibility)

### Evaluation

**Primary Metrics**:
- **Compilation Error Rate**: Percentage of generated samples that fail Python syntax check
  - Measured via `ast.parse()` or `compile()`
  
**Success Criteria**:
- constrained_error_rate < baseline_error_rate (direction only for PoC)

**Expected Baseline Performance** (from research):
- Baseline (unconstrained): Variable syntax error rate depending on model
- Constrained (SynCode): ~96% syntax error reduction (from paper)
- **Source**: Ugare et al. 2024

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation
- Library: ast (Python standard library)
- Code:
```python
import ast

def check_syntax(code: str) -> bool:
    """Returns True if code is syntactically valid."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def compilation_error_rate(samples: list) -> float:
    """Calculate percentage of samples with syntax errors."""
    errors = sum(1 for s in samples if not check_syntax(s))
    return errors / len(samples)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing baseline vs constrained compilation error rates

#### Additional Figures (LLM Autonomous)
- Error rate by problem difficulty (if available)
- Sample-level syntax validity heatmap

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `constrained_error_rate < baseline_error_rate`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: OpenReview forum (gU58d5QeGv)
- **Type**: Knowledge base article
- **Query Used**: "constrained decoding implementation challenges"
- **Relevance**: Background on structured generation challenges
- **Used For**: Understanding problem space

### B. GitHub Implementations (Exa)

**Repository 1**: structuredllm/syncode (337 stars)
- **URL**: https://github.com/structuredllm/syncode
- **Query Used**: "syncode grammar constrained decoding code generation"
- **Relevance**: Primary implementation for grammar constraints
- **Key Code**:
```python
from syncode import Syncode
syn_llm = Syncode(model=model_name, mode='grammar_strict', grammar='python')
output = syn_llm.infer(prompt)
```
- **Configuration Extracted**: mode='grammar_strict', grammar='python'
- **Their Results**: 96.07% syntax error reduction
- **Used For**: Core mechanism implementation, evaluation methodology

**Repository 2**: openai/human-eval (3333 stars)
- **URL**: https://github.com/openai/human-eval
- **Query Used**: "HumanEval dataset loading Python"
- **Relevance**: Standard benchmark dataset
- **Used For**: Dataset specification

**Paper 1**: Ugare et al. 2024
- **URL**: https://arxiv.org/abs/2403.01632
- **Title**: "SynCode: LLM Generation with Grammar Augmentation"
- **Key Finding**: DFA mask store enables efficient grammar-guided generation
- **Used For**: Mechanism design, expected results

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - SynCode provides ready-to-use library implementation

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-E1
- **Reused Components**: None (first mechanism hypothesis)
- **Context**: H-E1 validated error class independence, enabling H-M1 to proceed

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A | 02b_verification_plan.md Section 1.3 |
| Baseline model | Phase 2A | 02b_verification_plan.md Section 1.3 |
| Mechanism design | Exa GitHub | structuredllm/syncode |
| Pseudo-code | Exa GitHub + Paper | syncode repo + arXiv:2403.01632 |
| Expected results | Paper | Ugare et al. 2024 (96.07% reduction) |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md H-M1 spec |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis
- 2026-08-12: H-M1 set to IN_PROGRESS
- 2026-08-12: Phase 2C experiment design initiated
- 2026-08-12: Research completed (Archon + Exa)
- 2026-08-12: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
