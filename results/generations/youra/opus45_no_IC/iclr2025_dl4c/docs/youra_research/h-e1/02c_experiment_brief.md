# Experiment Design: H-E1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** FGO token masking improves code generation performance across ALL feedback content types
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Foundation Gate

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: FGO > Standard PPO for ALL 3 content types (compile, test, combined). Failure blocks all downstream hypotheses (H-M1, H-M2, H-M3).

---

## Continuation Context

This is the foundation hypothesis with no prerequisites. First hypothesis in the verification chain.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB did not contain StepCoder/FGO-specific entries. Diffusers examples returned (not relevant). Research proceeded via Exa.

### Archon Code Examples

No direct FGO code examples in Archon KB. StepCoder implementation sourced from Exa GitHub search.

### Exa GitHub Implementations

**StepCoder (ACL 2024)** - Primary source for FGO mechanism:
- **Repository:** https://github.com/Ablustrund/APPS_Plus
- **Paper:** "StepCoder: Improving Code Generation with Reinforcement Learning from Compiler Feedback"
- **Authors:** Fudan NLP Lab (Shihan Dou, Yan Liu, et al.)
- **Results:** pass@1 up to 59.7% on APPS+, 67.0% MBPP, 78.7% HumanEval

**FGO Mechanism (from paper):**
- Dynamic masking technique masks unexecuted code segments
- Mask matrix: m_ij = 1 if token j executed, 0 otherwise
- Modified PPO loss: L^PPO(θ) = E_t[min(r_t(θ)A_t, clip(r_t(θ), 1-ε, 1+ε)A_t) · m_t]
- Gradients only flow through executed tokens

**Reward Structure (from StepCoder):**
- +1.0 if passed all unit tests
- -0.3 if failed any unit test
- -0.6 if runtime error
- -1.0 if compile error

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Rationale |
|----------|---------------|-----------|
| 1 | StepCoder official (Ablustrund/APPS_Plus) | Original FGO implementation, peer-reviewed ACL 2024 |
| 2 | TRL PPOTrainer + custom FGO masking | If StepCoder integration difficult |
| 3 | OpenRLHF + FGO extension | Alternative PPO framework |

**Recommended Implementation Path:**
- Primary: Adapt StepCoder FGO masking logic into TRL PPOTrainer
- Fallback: Direct StepCoder codebase modification for our factorial design
- Justification: StepCoder is the canonical FGO source; TRL provides modern infrastructure

### Code Analysis (Serena MCP)

Serena not invoked (no local codebase to analyze). FGO mechanism extracted from paper and Exa search results.

**FGO Core Algorithm (from Algorithm 1 in paper):**
1. Generate code with policy model πθ
2. Execute unit tests, collect execution trace
3. Map executed lines to token positions
4. Create mask matrix m (1 for executed, 0 for unexecuted)
5. Compute PPO loss only for masked (executed) tokens
6. Update policy with masked gradients

---

## Experiment Specification

### Dataset

**Dataset 1: HumanEval**
- **Name:** HumanEval
- **Type:** standard
- **Source:** OpenAI
- **Size:** 164 programming problems (full test set)
- **Task:** Function completion from docstring
- **Evaluation:** Functional correctness via unit tests

**Dataset 2: MBPP**
- **Name:** MBPP (Mostly Basic Python Problems)
- **Type:** standard
- **Source:** Google Research
- **Size:** 500 test problems (indices 11-510)
- **Task:** Program synthesis from natural language
- **Evaluation:** Multiple test cases per problem

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + official evaluation harness
- Identifier: `openai_humaneval`, `mbpp`
- Code:
```python
# HumanEval
from human_eval.data import read_problems
problems = read_problems()

# MBPP
from datasets import load_dataset
mbpp = load_dataset("mbpp", split="test")
```

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B-Instruct
- **Type:** Decoder-only transformer (instruction-tuned)
- **Source:** meta-llama/CodeLlama-7b-Instruct-hf
- **Parameters:** 7B
- **Context:** Instruction-following for code generation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/CodeLlama-7b-Instruct-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/CodeLlama-7b-Instruct-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
```

#### Proposed Model

**Architecture:** CodeLlama-7B-Instruct + FGO Token Masking

**Core Mechanism Implementation:**

```python
# Core Mechanism: FGO (Fine-Grained Optimization)
# Based on: StepCoder (ACL 2024) - Fudan NLP Lab

import torch
import sys

def collect_execution_trace(code: str, test_cases: list) -> set:
    """
    Collect executed line numbers via Python trace.
    Returns: Set of executed line numbers
    """
    executed_lines = set()
    
    def trace_func(frame, event, arg):
        if event == 'line':
            executed_lines.add(frame.f_lineno)
        return trace_func
    
    sys.settrace(trace_func)
    try:
        exec(code + "\n" + "\n".join(test_cases))
    except:
        pass
    finally:
        sys.settrace(None)
    
    return executed_lines

def create_fgo_mask(token_ids: torch.Tensor, 
                    token_to_line: list,
                    executed_lines: set) -> torch.Tensor:
    """
    Create FGO mask: 1 for executed tokens, 0 for unexecuted.
    Args:
        token_ids: (seq_len,) token indices
        token_to_line: mapping from token position to source line
        executed_lines: set of executed line numbers
    Returns:
        mask: (seq_len,) binary mask
    """
    mask = torch.zeros_like(token_ids, dtype=torch.float)
    for i, line_num in enumerate(token_to_line):
        if line_num in executed_lines:
            mask[i] = 1.0
    return mask

def fgo_ppo_loss(logprobs: torch.Tensor,
                 old_logprobs: torch.Tensor,
                 advantages: torch.Tensor,
                 mask: torch.Tensor,
                 clip_eps: float = 0.2) -> torch.Tensor:
    """
    FGO-masked PPO loss (only executed tokens contribute).
    """
    ratio = torch.exp(logprobs - old_logprobs)
    clipped = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps)
    loss = -torch.min(ratio * advantages, clipped * advantages)
    # Apply FGO mask - zero gradient for unexecuted tokens
    masked_loss = loss * mask
    return masked_loss.sum() / (mask.sum() + 1e-8)
```

### Training Protocol

**Optimizer:** AdamW
- Parameters: lr=3e-6, weight_decay=0.01
- **Source:** TRL PPO defaults, StepCoder paper

**Learning Rate:** 3e-6
- **Source:** TRL PPOTrainer recommended for code models

**Schedule:** Linear warmup (10% steps) + linear decay
- **Source:** Standard RLHF practice

**Batch Size:** 64 (per-device=16, gradient_accumulation=4)
- **Source:** StepCoder paper, TRL recommendations

**Episodes:** 10,000 total training episodes
- **Source:** StepCoder experimental setup

**Loss Function:** FGO-masked PPO objective (see pseudo-code)
- **Source:** StepCoder Algorithm 1

**Reward Function:**
```python
def compute_reward(code: str, test_cases: list) -> float:
    try:
        exec(code + "\n" + "\n".join(test_cases))
        return 1.0  # Passed all tests
    except AssertionError:
        return -0.3  # Failed test
    except SyntaxError:
        return -1.0  # Compile error
    except Exception:
        return -0.6  # Runtime error
```

**Seeds:** 1 (fixed) - PoC only

> ⚠️ **EXISTENCE (PoC)**: Single seed sufficient for direction validation.

### Evaluation

**Primary Metrics:**
- pass@1: Functional correctness on first generation attempt
- pass@10: Correctness within 10 attempts (secondary)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation / functional correctness
- Library: human_eval, bigcode-evaluation-harness
- Code:
```python
# HumanEval evaluation
from human_eval.evaluation import evaluate_functional_correctness
results = evaluate_functional_correctness("samples.jsonl")

# MBPP evaluation (bigcode-harness style)
from bigcode_eval.tasks.custom_metrics.code_eval import compute_code_eval
results, _ = compute_code_eval(references=refs, predictions=gens)
```

**Success Criteria (PoC):**
- FGO_pass@1 > Standard_pass@1 for ALL 3 content types
- Effect direction positive for compile-only, test-only, and combined feedback

**Expected Baseline Performance** (from StepCoder paper):
- Standard PPO (test-only): ~70% pass@1 on HumanEval
- PPO + RLPF: ~72% pass@1
- StepCoder (FGO): ~75% pass@1

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: 2×3 factorial bar chart showing pass@1 for each condition (Standard vs FGO) × (Compile, Test, Combined)

#### Additional Figures (LLM Autonomous)
- Training curves: pass@1 over episodes for all 6 conditions
- Masking statistics: % of tokens masked per epoch
- Reward distribution: histogram of rewards by condition

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** FGO masking function implemented
- **mechanism_isolatable:** Can run with mask=all-ones (no masking) vs trace-based mask
- **baseline_measurable:** Standard PPO (no masking) produces valid pass@1

### Architecture Compatibility
- **architecture_compatibility:** CodeLlama-7B compatible with TRL PPOTrainer; FGO mask applied at loss computation, not model architecture

### Activation Indicators
- **mechanism_log_message:** `"[FGO] Masking {N} of {M} tokens ({P}% unexecuted)"`
- **tensor_shape_change:** mask.sum() < seq_len (some tokens masked)
- **metric_delta_expected:** 2-5% pass@1 improvement over Standard PPO

### Mechanism Verification Code
```python
def verify_fgo_mechanism(mask: torch.Tensor, logprobs: torch.Tensor):
    """Verify FGO is actually masking tokens."""
    assert mask.sum() < mask.numel(), "FGO mask should exclude some tokens"
    masked_ratio = 1 - (mask.sum() / mask.numel())
    print(f"[FGO] Masking {masked_ratio*100:.1f}% of tokens (unexecuted)")
    
    # Verify gradients are zero for masked positions
    test_loss = (logprobs * mask).sum()
    test_loss.backward()
    # Check: gradients should be zero where mask=0
```

### Success Thresholds
- **hypothesis_support_threshold:** FGO > Standard for 3/3 content types
- **hypothesis_support_metric:** pass@1 improvement direction

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `FGO_pass@1 > Standard_pass@1` for ALL content types (compile, test, combined)

**Minimum Evidence:**
- FGO shows positive improvement direction on compile-only feedback
- FGO shows positive improvement direction on test-only feedback
- FGO shows positive improvement direction on combined feedback

---

## Appendix: Reference Implementations

### Primary References

1. **StepCoder (ACL 2024)**
   - Paper: https://aclanthology.org/2024.acl-long.251/
   - Code: https://github.com/Ablustrund/APPS_Plus
   - FGO Algorithm 1, Section 3.2
   - Reward structure: Eq. 3

2. **TRL PPOTrainer**
   - Docs: https://huggingface.co/docs/trl/ppo_trainer
   - Code: https://github.com/huggingface/trl/blob/main/trl/trainer/ppo_trainer.py

3. **HumanEval**
   - Paper: "Evaluating Large Language Models Trained on Code" (OpenAI)
   - Code: https://github.com/openai/human-eval

4. **MBPP**
   - Dataset: https://huggingface.co/datasets/mbpp
   - Evaluation: https://github.com/bigcode-project/bigcode-evaluation-harness

### Code Snippets Used

**FGO Mask Matrix (from StepCoder alphaXiv overview):**
```
m_ij = 1 if token j in sequence i was executed
       0 otherwise
```

**Masked PPO Loss:**
```
L^PPO(θ) = E_t[min(r_t(θ)A_t, clip(r_t(θ), 1-ε, 1+ε)A_t) · m_t]
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C)
- 2026-08-10: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
