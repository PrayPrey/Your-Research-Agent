# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under CoT prompting conditions, if the model is prompted with "Let's think step by step", then outputs will contain multi-step reasoning chains, because CoT prompts activate sequential reasoning patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates Step 1 of causal chain: CoT forces explicit reasoning articulation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 VALIDATED)
**Gate Status:** MUST_WORK (critical path)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
**MUST_WORK Gate:**
- Primary: >90% of CoT outputs contain multi-step reasoning
- Secondary: Mean step count in CoT > 2
- Failure Response: EXPLORE (test alternative CoT formulations)

---

## Continuation Context

**Previous Hypothesis:** H-E1 (ECE Measurability Verification) - VALIDATED
- Confirmed extraction rates >95% across all 5 prompting conditions
- ECE computable in valid range [0,1]
- Infrastructure validated for mechanism testing

### Previous Hypothesis Results
H-E1 validation confirmed:
- Confidence extraction works reliably with "Confidence: X%" format
- All 5 conditions (baseline, CoT-only, confidence-only, CoT+confidence, token-padding) measurable
- Ready to proceed with mechanism verification chain

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using literature-based design*

**Chain-of-Thought Prompting (Wei et al. 2022):**
- "Let's think step by step" elicits multi-step reasoning in large LMs
- Effect size increases with model scale
- Reasoning chains typically contain 3-8 steps for complex QA

**Reasoning Chain Detection Patterns:**
- Numbered steps: "1.", "2.", "3.", "Step 1:", etc.
- Transition words: "First,", "Then,", "Therefore,", "Finally,"
- Logical connectors: "because", "so", "thus", "hence"
- Alternative consideration: "However,", "But,", "Alternatively,"

### Archon Code Examples

*MCP unavailable - standard implementation patterns*

```python
# CoT prompt template (standard)
COT_PROMPT = """Question: {question}
Options: {options}

Let's think step by step.
After reasoning, state your final answer as "Answer: [A/B/C/D]"
Then provide your confidence as "Confidence: X%"
"""

# Reasoning chain detection
def has_multi_step_reasoning(output: str) -> tuple[bool, int]:
    """Detect multi-step reasoning and count steps."""
    step_patterns = [
        r'(?:^|\n)\s*\d+[\.\)]\s',  # Numbered: "1.", "2)"
        r'(?:^|\n)\s*Step\s+\d+',    # "Step 1", "Step 2"
        r'(?:First|Second|Third|Finally)[,:]',  # Ordinals
    ]
    transition_words = [
        'therefore', 'thus', 'hence', 'so',
        'because', 'since', 'then', 'next'
    ]
    # Implementation details in Phase 4
```

### Exa GitHub Implementations

*MCP unavailable - literature-referenced implementations*

**Reference: Wei et al. 2022 (Chain-of-Thought Prompting)**
- Standard CoT elicitation via "Let's think step by step"
- Widely replicated across GPT-3, GPT-4, PaLM, Llama families

**Reference: Kojima et al. 2022 (Zero-Shot CoT)**
- Zero-shot variant requires no exemplars
- "Let's think step by step" sufficient for complex reasoning

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment:** No official implementation needed - this is a prompting study, not model training.

**Recommended Implementation Path:**
- Primary: Custom prompt templates + regex-based reasoning detection
- Fallback: Manual annotation of 100-sample subset for validation
- Justification: Prompting-based experiment; standard libraries sufficient

### Code Analysis (Serena MCP)

*MCP unavailable - N/A for this prompt-based experiment*

No codebase analysis needed. Experiment is prompt engineering + output parsing.

---

## Experiment Specification

### Dataset

**Primary Dataset: TruthfulQA**
- Name: TruthfulQA (MC2 split)
- Version: Latest (HuggingFace datasets)
- Source: truthful_qa on HuggingFace
- Type: standard
- Size: 817 questions (full test set)
- Splits: Use full dataset (no train/val needed - inference only)
- Preprocessing: Format as multiple-choice with option letters [A/B/C/D/E]
- Augmentation: None (preserve original questions)

**Evaluation Subset:** Full 817 items (NOT pilot sample - mechanism testing requires statistical power)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: truthful_qa (mc2)
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "multiple_choice", split="validation")
# Filter to mc2 format, extract questions and options
```

### Models

#### Baseline Model

**Model: GPT-3.5-turbo (OpenAI API)**
- Architecture: Decoder-only transformer (instruction-tuned)
- Size: ~175B parameters (estimated)
- Source: OpenAI API
- Rationale: Widely used, instruction-following, CoT-capable

**Fallback: Llama-2-70B-chat (HuggingFace/Together AI)**
- Use if OpenAI API unavailable
- Similar instruction-following capabilities

**Loading Information** (for Phase 4 download):
- Method: OpenAI API (primary) / Together AI (fallback)
- Identifier: gpt-3.5-turbo / meta-llama/Llama-2-70b-chat-hf
- Code:
```python
# OpenAI
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

# Together AI (fallback)
import together
response = together.Complete.create(
    model="meta-llama/Llama-2-70b-chat-hf",
    prompt=prompt,
    temperature=0
)
```

#### Proposed Model

**Architecture:** Same baseline model + CoT prompting

**Core Mechanism Implementation:**

```python
# Core mechanism: CoT prompt activates multi-step reasoning
# 10-30 lines pseudo-code

def generate_with_cot(model, question: str, options: list) -> dict:
    """Generate response with Chain-of-Thought prompting."""
    
    # 1. Construct CoT prompt
    cot_prompt = f"""Question: {question}
Options: {format_options(options)}

Let's think step by step.
After reasoning, provide:
- Your final answer as "Answer: [letter]"
- Your confidence as "Confidence: X%"
"""
    
    # 2. Generate response (temperature=0 for reproducibility)
    response = model.generate(cot_prompt, temperature=0)
    
    # 3. Parse output for reasoning chain
    result = {
        'raw_output': response,
        'has_reasoning': detect_reasoning_chain(response),
        'step_count': count_reasoning_steps(response),
        'reasoning_text': extract_reasoning(response),
        'answer': extract_answer(response),
        'confidence': extract_confidence(response)
    }
    
    return result

def detect_reasoning_chain(text: str) -> bool:
    """Detect presence of multi-step reasoning."""
    indicators = [
        r'\d+[\.\)]\s',           # Numbered steps
        r'Step\s+\d+',            # Explicit step markers
        r'First[,:]',             # Ordinal markers
        r'(Therefore|Thus|Hence)', # Logical conclusions
        r'(because|since)',        # Causal reasoning
    ]
    import re
    return any(re.search(p, text, re.I) for p in indicators)

def count_reasoning_steps(text: str) -> int:
    """Count number of reasoning steps."""
    import re
    # Count numbered items
    numbered = len(re.findall(r'(?:^|\n)\s*\d+[\.\)]', text))
    # Count transition markers
    transitions = len(re.findall(
        r'\b(First|Second|Third|Then|Next|Finally)\b', text, re.I
    ))
    return max(numbered, transitions, 1)  # At least 1 if any text
```

### Training Protocol

**Not Applicable** - This is an inference-only experiment (prompting study).

**Inference Protocol:**
- Temperature: 0 (deterministic)
- Max tokens: 1024 (sufficient for CoT reasoning)
- API calls: 817 items × 2 conditions = 1,634 calls minimum
- Conditions to test:
  1. Baseline (no CoT): Direct answer prompt
  2. CoT condition: "Let's think step by step" prompt
- Batching: Sequential (API rate limits)
- Retry logic: 3 retries with exponential backoff

### Evaluation

**Primary Metric: Reasoning Presence Rate**
- Definition: Fraction of outputs containing multi-step reasoning
- Target: >90% for CoT condition
- Formula: `sum(has_reasoning) / total_samples`

**Secondary Metric: Mean Step Count**
- Definition: Average number of reasoning steps per output
- Target: >2 steps for CoT condition
- Formula: `mean(step_count) for outputs where has_reasoning=True`

**Comparison Metrics:**
- Baseline reasoning rate (expected: <30%)
- CoT - Baseline difference (expected: >60 percentage points)

**Success Criteria (PoC):**
1. CoT reasoning_presence_rate > 0.90
2. CoT mean_step_count > 2.0
3. CoT reasoning_rate - Baseline reasoning_rate > 0.50

**Statistical Note:** PoC level - direction-based comparison, no hypothesis testing required.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Classification + Text Analysis
- Library: Custom (regex-based parsing)
- Code:
```python
# Metrics computation
def compute_metrics(results: list[dict]) -> dict:
    reasoning_present = [r['has_reasoning'] for r in results]
    step_counts = [r['step_count'] for r in results if r['has_reasoning']]
    
    return {
        'reasoning_presence_rate': sum(reasoning_present) / len(reasoning_present),
        'mean_step_count': sum(step_counts) / len(step_counts) if step_counts else 0,
        'total_samples': len(results),
        'samples_with_reasoning': sum(reasoning_present)
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing reasoning_presence_rate between Baseline vs CoT conditions

#### Additional Figures (LLM Autonomous)

1. **Step Count Distribution**: Histogram of step counts for CoT outputs
2. **Example Outputs**: Side-by-side comparison of baseline vs CoT outputs (3 examples)
3. **Reasoning Pattern Breakdown**: Pie chart of detected reasoning patterns (numbered, ordinal, logical connectors)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `cot_reasoning_rate > 0.90`
3. `cot_reasoning_rate > baseline_reasoning_rate + 0.50`
4. `cot_mean_step_count > 2.0`

---

## Appendix: Reference Implementations

### Primary References

1. **Wei et al. 2022** - Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
   - Key finding: "Let's think step by step" elicits multi-step reasoning
   - Replication target: >90% of CoT outputs contain reasoning chains
   - URL: https://arxiv.org/abs/2201.11903

2. **Kojima et al. 2022** - Large Language Models are Zero-Shot Reasoners
   - Key finding: Zero-shot CoT effective without exemplars
   - Prompt: "Let's think step by step"
   - URL: https://arxiv.org/abs/2205.11916

3. **Xiong et al. 2023** - Can LLMs Express Their Uncertainty?
   - Key finding: Verbalized confidence extractable at >95% rate
   - Used for H-E1 validation, applicable to H-M1 output parsing
   - URL: https://arxiv.org/abs/2306.13063

### Code Patterns

```python
# Standard CoT prompt pattern (Wei et al. 2022)
def build_cot_prompt(question, options):
    return f"""Question: {question}
Options:
{chr(65+i)}. {opt} for i, opt in enumerate(options)}

Let's think step by step."""

# Baseline prompt (no CoT)
def build_baseline_prompt(question, options):
    return f"""Question: {question}
Options:
{chr(65+i)}. {opt} for i, opt in enumerate(options)}

Answer directly with the letter of the correct option."""
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
1. H-E1 validated - infrastructure confirmed working
2. H-M1 set to IN_PROGRESS (Phase 2C experiment design)
3. Experiment brief generated with Level 1.5 specification

---

*MCP Tools Used: None available (no-mcp mode)*
*Specifications grounded in published literature (Wei et al. 2022, Kojima et al. 2022, Xiong et al. 2023)*
*Next Phase: Phase 3 - Implementation Planning*
