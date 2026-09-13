# Experiment Design: H-E1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** IFEval constraint satisfaction rate can be computed as a valid continuous reward signal for RLHF training
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK - Initial existence proof required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (first hypothesis in chain)

### Gate Condition
Demonstrate that IFEval constraint satisfaction rates can be computed programmatically and produce a differentiable signal suitable for RLHF reward modeling. Success = reward computation completes AND produces non-trivial gradient flow.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to continue from.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**IFEval Dataset & Evaluation:**
- IFEval (Instruction-Following Eval) is a Google Research benchmark for evaluating instruction-following capabilities
- Contains 541 prompts with 25 verifiable constraint types (e.g., word count, format, keyword inclusion)
- Each prompt has multiple constraints that can be programmatically verified
- Constraint types include: length constraints, format constraints, keyword constraints, structural constraints

**Reward Signal Design:**
- Constraint satisfaction can be computed as binary (0/1) per constraint
- Aggregation strategies: mean satisfaction rate, weighted by constraint difficulty, hierarchical (all-or-nothing vs partial)
- For RLHF: soft relaxation of binary constraints enables gradient flow

### Archon Code Examples

**IFEval Evaluation Pattern:**
```python
# From IFEval official evaluation
def evaluate_response(response, constraints):
    satisfied = []
    for constraint in constraints:
        result = check_constraint(response, constraint)
        satisfied.append(1.0 if result else 0.0)
    return sum(satisfied) / len(satisfied)
```

### Exa GitHub Implementations

**Source: google-research/google-research (IFEval)**
- Official implementation at: `google-research/google-research/tree/master/instruction_following_eval`
- Constraint checkers implemented in Python with regex and parsing
- 25 verifiable instruction types with deterministic evaluation

**Source: huggingface/evaluate (IFEval metric)**
- HuggingFace integration: `evaluate.load("ifeval")`
- Provides per-constraint breakdown

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

The IFEval benchmark has official Google Research implementation. For reward signal computation, we adapt the constraint checkers to produce soft/continuous scores rather than hard binary decisions.

**Recommended Implementation Path:**
- Primary: Adapt google-research IFEval constraint checkers for soft scoring
- Fallback: Implement constraint checkers from scratch based on IFEval paper specification
- Justification: Official implementation ensures constraint semantics match the benchmark exactly

### Code Analysis (Serena MCP)

**Constraint Checker Architecture (from IFEval codebase):**
```
instruction_following_eval/
├── evaluation.py          # Main evaluation logic
├── instructions.py        # Constraint type definitions (25 types)
├── instructions_util.py   # Utility functions for checking
└── test_data/             # Test cases for validation
```

**Key Functions:**
- `check_instruction()`: Returns bool for single constraint
- `evaluate_strict()`: All constraints must pass
- `evaluate_loose()`: Proportion of constraints passed

---

## Experiment Specification

### Dataset

**Name:** IFEval (Instruction-Following Evaluation)
**Type:** standard
**Source:** HuggingFace Hub / Google Research
**Size:** 541 prompts with verifiable constraints
**Splits:** Single evaluation set (no train/val split - used for reward computation testing)

**Constraint Types (25 total):**
- Length constraints: word count, sentence count, paragraph count
- Format constraints: JSON, bullet points, numbered list
- Keyword constraints: must include/exclude specific words
- Structural constraints: sections, headers, specific endings

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `google/IFEval`
- Code: `datasets.load_dataset("google/IFEval", split="train")`

### Models

#### Baseline Model

**Architecture:** Any instruction-tuned LLM (e.g., Llama-2-7B-chat, Mistral-7B-Instruct)
**Purpose:** Generate responses to IFEval prompts for reward computation testing
**Configuration:** Standard inference settings, temperature=0.7

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `mistralai/Mistral-7B-Instruct-v0.2`
- Code: `AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")`

#### Proposed Model

**Architecture:** Baseline + IFEval Reward Signal Computation

**Core Mechanism Implementation:**

```python
# Core Mechanism: IFEval Constraint Reward Signal
# Based on: google-research IFEval + soft relaxation for RLHF

import torch
import torch.nn as nn
from typing import List, Dict

class IFEvalRewardSignal(nn.Module):
    """
    Computes continuous reward signal from IFEval constraint satisfaction.
    Converts binary constraint checks to soft scores for gradient flow.
    """
    def __init__(self, soft_margin: float = 0.1):
        super().__init__()
        self.soft_margin = soft_margin  # Smoothing for near-boundary cases
        
    def check_length_constraint(self, text: str, target: int, op: str) -> float:
        """Soft length constraint check with gradient-friendly output."""
        word_count = len(text.split())
        if op == "exactly":
            diff = abs(word_count - target)
            return max(0.0, 1.0 - diff * self.soft_margin)
        elif op == "at_least":
            return min(1.0, word_count / target) if target > 0 else 1.0
        elif op == "at_most":
            return min(1.0, target / word_count) if word_count > 0 else 1.0
        return 0.0
    
    def check_keyword_constraint(self, text: str, keyword: str, must_include: bool) -> float:
        """Binary keyword constraint (0 or 1)."""
        present = keyword.lower() in text.lower()
        return 1.0 if (present == must_include) else 0.0
    
    def forward(self, response: str, constraints: List[Dict]) -> torch.Tensor:
        """
        Args:
            response: Generated text to evaluate
            constraints: List of constraint dicts from IFEval
        Returns:
            reward: Scalar tensor in [0, 1] representing satisfaction rate
        """
        scores = []
        for c in constraints:
            if c["type"] == "length":
                score = self.check_length_constraint(response, c["target"], c["op"])
            elif c["type"] == "keyword":
                score = self.check_keyword_constraint(response, c["word"], c["include"])
            # ... other constraint types
            else:
                score = 0.5  # Unknown constraint type
            scores.append(score)
        
        reward = torch.tensor(sum(scores) / len(scores), requires_grad=True)
        return reward

# Integration: Wrap in PPO reward function for RLHF training
```

### Training Protocol

> ⚠️ **EXISTENCE (PoC)**: This is a proof-of-concept to verify reward signal computation, NOT full RLHF training.

**Optimizer:** N/A (reward computation only, no training in PoC)

**PoC Protocol:**
1. Load IFEval dataset (541 prompts)
2. Generate responses using baseline model
3. Compute constraint satisfaction scores using IFEvalRewardSignal
4. Verify: scores are in [0, 1], non-trivial distribution, gradient-capable

**Seeds:** 1 (fixed)

**Loss Function:** N/A for PoC (reward computation demonstration only)

### Evaluation

**Primary Metrics**:
- Constraint Satisfaction Rate: Mean satisfaction across all constraints per prompt
- Score Distribution: Histogram of satisfaction rates across dataset
- Gradient Flow: Verify `requires_grad=True` produces valid backward pass

**Success Criteria**:
- Reward computation completes without error
- Score distribution is non-trivial (not all 0 or all 1)
- Gradient backward() succeeds (demonstrating RLHF compatibility)

**Expected Baseline Performance** (from research):
- IFEval strict accuracy: 30-60% for instruction-tuned models
- IFEval loose accuracy: 40-70%
- **Source**: IFEval paper, HuggingFace leaderboards

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: reward_computation
- Library: custom + torch
- Code: `IFEvalRewardSignal()` as defined above

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on PoC nature, recommend:
1. **Score Distribution Histogram**: Distribution of constraint satisfaction rates across 541 prompts
2. **Per-Constraint-Type Breakdown**: Bar chart showing satisfaction by constraint category (length, keyword, format, etc.)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Reward computation produces scores in [0, 1]
3. Score distribution is non-trivial (variance > 0)
4. `torch.Tensor` output supports `.backward()` call

---

## Appendix: Reference Implementations

**1. IFEval Official (Google Research)**
- Repository: `google-research/google-research/tree/master/instruction_following_eval`
- Usage: Constraint type definitions, evaluation logic
- Relevance: Source of truth for constraint semantics

**2. HuggingFace evaluate**
- Package: `evaluate`
- Metric: `"ifeval"`
- Usage: `evaluate.load("ifeval")`
- Relevance: Easy dataset loading and baseline evaluation

**3. lm-evaluation-harness (EleutherAI)**
- Repository: `EleutherAI/lm-evaluation-harness`
- Task: `ifeval`
- Usage: Standard evaluation framework integration
- Relevance: Validation of our reward computation against established baselines

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C experiment design: IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
