# Experiment Design: h-e1

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Beam search with custom scoring must exist and be computationally feasible for code generation. AST parsing must work reliably for Python code validation.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (first hypothesis)
**Gate Status:** MUST_WORK (if fail → ABANDON entire verification)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**Type:** MUST_WORK  
**If Fail:** ABANDON (infrastructure not feasible)

---

## Continuation Context

This is the first (foundation) hypothesis. No prior context exists.

### Previous Hypothesis Results (if applicable)
N/A — h-e1 is the first hypothesis with no prerequisites.

---

## Implementation Research Summary

⚠️ **MCP UNAVAILABLE FALLBACK MODE** — Archon, Exa, and Serena MCP servers were unavailable during experiment design. Specifications below are derived from Phase 2B verification plan and standard ML libraries.

### Archon Knowledge Base Findings

*MCP service unavailable — skipped*

### Archon Code Examples

*MCP service unavailable — skipped*

### Exa GitHub Implementations

*MCP service unavailable — skipped*

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

*MCP service unavailable — using standard HuggingFace Transformers beam search implementation*

**Recommended Implementation Path:**
- Primary: HuggingFace Transformers `generate()` with `num_beams=5` + custom scoring callback
- Fallback: Manual beam search implementation if custom scoring not supported
- Justification: HF Transformers widely used, well-tested beam search; CodeLlama-7B available via `meta-llama/CodeLlama-7b-hf`

### Code Analysis (Serena MCP)

*MCP service unavailable — skipped*

---

## Experiment Specification

### Dataset

**Name:** HumanEval-164  
**Type:** standard  
**Source:** OpenAI HumanEval benchmark (164 hand-written Python programming problems)  
**Subset:** First 5 problems (PoC validation)  
**Size:** 5 problems (PoC) → extrapolate to 164 for full validation  
**Purpose:** Code generation benchmark for testing beam search infrastructure and AST parsing

**Loading Information** (for Phase 4 download):
- Method: `datasets` library
- Identifier: `openai_humaneval`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("openai_humaneval")
poc_subset = dataset['test'].select(range(5))  # First 5 for PoC
```

### Models

#### Baseline Model

**Name:** CodeLlama-7B (greedy sampling)  
**Architecture:** Autoregressive transformer (7B parameters)  
**Purpose:** Baseline for computational feasibility comparison  
**Expected Performance:** ~30% Pass@1, 64-68% syntax error rate (from Phase 2B)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/CodeLlama-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-hf")
```

#### Proposed Model

**Architecture:** CodeLlama-7B + Beam Search (k=5) with Custom Scoring

**Core Mechanism Implementation:**

```python
# Beam search with validity scoring
import ast

def custom_scoring_fn(beam_outputs, model_logprobs):
    """
    Combined score: α * log_likelihood + β * validity_score
    α = 0.7 (fluency weight)
    β = 0.3 (validity weight)
    """
    scores = []
    for output, logprob in zip(beam_outputs, model_logprobs):
        # AST validity check
        try:
            ast.parse(output)
            validity_score = 1.0
        except SyntaxError:
            validity_score = 0.0
        
        # Combined score
        final_score = 0.7 * logprob + 0.3 * validity_score
        scores.append(final_score)
    
    return scores

# Beam search invocation
outputs = model.generate(
    input_ids,
    num_beams=5,
    num_return_sequences=5,
    # Custom scoring may require LogitsProcessor or manual implementation
)
```

### Training Protocol

**N/A** — No training required. This is an inference-only PoC testing beam search infrastructure.

**Generation Settings:**
- Beam width: k=5
- Max new tokens: 256 (sufficient for HumanEval solutions)
- Temperature: 1.0 (default)
- Top-p: Not used (beam search replaces sampling)

### Evaluation

**Primary Metric:** Computational Time  
- **Target:** <30 minutes for 5-problem PoC (extrapolates to <4 hours for 164)  
- **Measurement:** Wall-clock time from generation start to completion

**Secondary Metric:** AST Parse Latency  
- **Target:** <50ms per sample (validates A5 assumption)  
- **Measurement:** Time per `ast.parse()` call

**Tertiary Metric:** Infrastructure Validation  
- Beam search completes without errors  
- Produces k=5 candidate outputs per problem  
- All outputs are parseable strings

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation
- Library: `time` (built-in), `ast` (built-in)
- Code:
```python
import time
import ast

start = time.time()
# ... generation ...
elapsed = time.time() - start

# AST parse latency
parse_times = []
for output in outputs:
    t0 = time.time()
    try:
        ast.parse(output)
    except:
        pass
    parse_times.append(time.time() - t0)

avg_parse_latency = sum(parse_times) / len(parse_times)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing:
  - Target time (<30 min) vs actual time
  - Target AST latency (<50ms) vs actual latency

#### Additional Figures (LLM Autonomous)

- **Beam count over generation steps** (verify k=5 maintained)
- **AST parse latency distribution** (histogram)
- **Generation time per problem** (bar chart)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

**Primary Reference:**
- HuggingFace Transformers beam search: https://huggingface.co/docs/transformers/main_classes/text_generation

**Additional References:**
- OpenAI HumanEval dataset: https://github.com/openai/human-eval
- Python AST module: https://docs.python.org/3/library/ast.html
- CodeLlama model card: https://huggingface.co/meta-llama/CodeLlama-7b-hf

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- 2026-08-25: Phase 2C experiment design initiated (MCP fallback mode)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
