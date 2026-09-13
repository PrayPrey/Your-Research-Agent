# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Under RLTF's fine-grained reward scheme, if an error occurs, then reward penalties are applied specifically to tokens at the error line location via traceback parsing.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Tests whether fine-grained feedback localizes to error-line tokens.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 = PASS)
**Gate Status:** MUST_WORK - failure stops workflow

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
Gradient concentration at error-line tokens must exceed gradient at other lines. >80% of penalty gradient must concentrate within ±2 lines of traceback location.

---

## Continuation Context

H-M1 builds on H-E1's validation that error-type gating improves sample efficiency. H-M1 tests the **first causal step** in the mechanism chain: does fine-grained feedback actually localize credit to error-line tokens?

### Previous Hypothesis Results (H-E1)
- **Status:** PASS
- **Key Findings:**
  - Error classification correctly identifies U_line vs U_ignore errors
  - Gating activation rate: ~13% (within expected 10-15% range)
  - Fine-gated condition outperformed fine-always
  - Implementation in `h-e1/code/reward.py` provides error classification and reward computation

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP services unavailable in batch mode. Using established patterns from:
1. RLTF paper (Le et al., 2022) - Fine-grained reward equations 4-5
2. H-E1 validated implementation - reward.py error classification

Key patterns identified:
- Traceback parsing via regex: `File ".*?", line (\d+)`
- Token-to-line mapping for gradient attribution
- Per-token reward assignment based on line match

### Archon Code Examples

From H-E1 validated implementation (`h-e1/code/reward.py`):

```python
def parse_traceback_line(traceback_str: str) -> Optional[int]:
    """Extract failing source line number from traceback."""
    matches = re.findall(r'File ".*?", line (\d+)', traceback_str)
    if matches:
        return int(matches[-1])  # Last frame = actual error location
    return None

def compute_gated_reward(code_tokens, traceback, gating):
    rewards = torch.zeros(len(code_tokens))
    error_line = parse_traceback_line(traceback)
    if error_line is not None:
        for idx, token in enumerate(code_tokens):
            if token.line == error_line:
                rewards[idx] = -1.0  # Fine-grained penalty
            else:
                rewards[idx] = -0.1  # Coarse penalty
    return rewards
```

### Exa GitHub Implementations

**Note:** MCP services unavailable. Reference implementations from literature:
1. **RLTF official**: Uses adaptive granularity reward (Eq 4-5)
2. **CodeRL**: Token-level critic for reward assignment
3. **PPO implementations**: Standard gradient computation with per-token rewards

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M1 does not require external implementation search — it validates **existing mechanism** in RLTF.

**Recommended Implementation Path:**
- Primary: Extend H-E1's reward.py with gradient tracking
- Fallback: Standalone gradient analysis script
- Justification: H-E1 implementation already validated; minimal modification needed

### Code Analysis (Serena MCP)

**Note:** MCP services unavailable. Manual analysis of H-E1 codebase:
- `reward.py:104-106` applies per-token penalties at error line
- Token dataclass tracks line numbers
- Gradient flows through reward tensor to model

---

## Experiment Specification

### Dataset

**Name:** APPS (Automated Programming Progress Standard)
**Type:** standard
**Source:** https://github.com/hendrycks/apps
**Train Size:** 5000 problems (from Phase 2A selection)
**Test Size:** 5000 problems

**For H-M1 Gradient Analysis:**
- Sample: 500 failing code samples with tracebacks
- Distribution: Mix of U_line and U_ignore error types
- Purpose: Measure gradient concentration, not train a model

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: codeparrot/apps
- Code:
```python
from datasets import load_dataset
ds = load_dataset("codeparrot/apps", split="train[:5000]")
```

### Models

#### Baseline Model

**Name:** CodeT5-large
**Type:** encoder-decoder (Salesforce/codet5-large)
**Parameters:** 770M
**Purpose:** Generate code samples for gradient analysis

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: Salesforce/codet5-large
- Code:
```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-large")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-large")
```

#### Proposed Model

**Architecture:** Baseline + Gradient Tracking for Fine-Grained Rewards

**Core Mechanism Implementation:**

```python
# H-M1: Gradient Concentration Analysis
# Tests whether fine-grained reward localizes gradient to error-line tokens

import torch
from typing import List, Tuple, Dict
import re

def analyze_gradient_concentration(
    model,
    code_tokens: List[str],
    token_lines: List[int],
    traceback: str,
    reward_fn
) -> Dict[str, float]:
    """
    Measure gradient concentration at error-line tokens.
    
    Returns:
        - error_line_gradient: mean |grad| at error line tokens
        - other_line_gradient: mean |grad| at other tokens
        - concentration_ratio: error_line / other_line
        - within_2_lines_pct: % of gradient within ±2 lines
    """
    # Parse error line from traceback
    matches = re.findall(r'File ".*?", line (\d+)', traceback)
    error_line = int(matches[-1]) if matches else None
    
    if error_line is None:
        return {"error": "no_traceback_line"}
    
    # Forward pass with gradient tracking
    model.zero_grad()
    logits = model(code_tokens)  # Shape: [seq_len, vocab]
    
    # Apply fine-grained reward
    rewards = reward_fn(code_tokens, token_lines, error_line)
    
    # Compute per-token loss weighted by reward
    loss = -(logits.log_softmax(-1) * rewards.unsqueeze(-1)).sum()
    loss.backward()
    
    # Collect gradients per token
    token_grads = []
    for param in model.parameters():
        if param.grad is not None:
            token_grads.append(param.grad.abs().mean().item())
    
    # Aggregate by line
    line_gradients = {}
    for idx, line in enumerate(token_lines):
        if line not in line_gradients:
            line_gradients[line] = []
        line_gradients[line].append(token_grads[idx] if idx < len(token_grads) else 0)
    
    # Compute metrics
    error_grad = sum(line_gradients.get(error_line, [0])) / max(1, len(line_gradients.get(error_line, [1])))
    other_grads = [v for k, vlist in line_gradients.items() for v in vlist if k != error_line]
    other_grad = sum(other_grads) / max(1, len(other_grads))
    
    # Within ±2 lines
    nearby_lines = set(range(error_line - 2, error_line + 3))
    nearby_grad = sum(sum(line_gradients.get(l, [0])) for l in nearby_lines)
    total_grad = sum(sum(vlist) for vlist in line_gradients.values())
    within_2_pct = nearby_grad / max(1e-8, total_grad)
    
    return {
        "error_line": error_line,
        "error_line_gradient": error_grad,
        "other_line_gradient": other_grad,
        "concentration_ratio": error_grad / max(1e-8, other_grad),
        "within_2_lines_pct": within_2_pct,
        "success": error_grad > other_grad and within_2_pct > 0.8
    }


def run_gradient_analysis(
    model,
    samples: List[Tuple[str, str]],  # (code, traceback) pairs
    reward_fn
) -> Dict[str, float]:
    """
    Aggregate gradient concentration across many samples.
    
    Success criteria:
    - mean(concentration_ratio) > 1.0
    - mean(within_2_lines_pct) > 0.80
    """
    results = []
    for code, traceback in samples:
        tokens, lines = tokenize_with_lines(code)
        result = analyze_gradient_concentration(
            model, tokens, lines, traceback, reward_fn
        )
        if "error" not in result:
            results.append(result)
    
    if not results:
        return {"error": "no_valid_samples"}
    
    return {
        "n_samples": len(results),
        "mean_concentration_ratio": sum(r["concentration_ratio"] for r in results) / len(results),
        "mean_within_2_lines_pct": sum(r["within_2_lines_pct"] for r in results) / len(results),
        "success_rate": sum(1 for r in results if r["success"]) / len(results),
        "primary_criterion_met": sum(r["concentration_ratio"] > 1.0 for r in results) / len(results) > 0.8,
        "secondary_criterion_met": sum(r["within_2_lines_pct"] > 0.8 for r in results) / len(results) > 0.8,
    }
```

### Training Protocol

**Note:** H-M1 is a **mechanism analysis** experiment, not a full training run.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Analysis samples | 500 | Statistical power for concentration test |
| Sample sources | APPS train failures | Real error distribution |
| Error types | Mixed U_line + U_ignore | Compare localization by type |
| Gradient computation | Single backward pass | Per-sample analysis |
| Aggregation | Mean concentration ratio | Primary metric |

**Protocol:**
1. Generate 500 failing code samples from APPS using CodeT5
2. Execute each sample, collect tracebacks
3. For each sample with traceback:
   - Tokenize code with line numbers
   - Apply fine-grained reward (error-line penalty)
   - Compute gradients
   - Measure concentration at error line vs other lines
4. Aggregate statistics across all samples
5. Test success criteria

### Evaluation

**Primary Metric:** Gradient concentration ratio (error_line / other_lines)
**Success Threshold:** ratio > 1.0 for >80% of samples

**Secondary Metric:** Percentage of gradient within ±2 lines of error
**Success Threshold:** >80% within ±2 lines for >80% of samples

**Statistical Test:** One-sample t-test (mean ratio > 1.0, p < 0.05)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: gradient_analysis
- Library: torch (native gradient computation)
- Code:
```python
# No external metrics library needed
# Gradient analysis uses torch.autograd
loss.backward()
grad_magnitude = param.grad.abs().mean()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean gradient at error-line vs other lines

#### Additional Figures (LLM Autonomous)

1. **gradient_concentration_histogram.png**: Distribution of concentration ratios across 500 samples
2. **line_gradient_heatmap.png**: Heatmap showing gradient magnitude by line position (error line centered)
3. **error_type_comparison.png**: Concentration ratio for U_line vs U_ignore errors
4. **within_lines_distribution.png**: Distribution of "% gradient within ±2 lines" metric

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `mean(concentration_ratio) > 1.0`
3. `mean(within_2_lines_pct) > 0.80`

**Gate Verdict Logic:**
```
IF concentration_ratio > 1.0 AND within_2_pct > 0.80:
    PASS → Proceed to H-M2
ELSE:
    FAIL → STOP workflow, localization mechanism broken
```

---

## Ablation Studies

| Variant | Purpose | Modification |
|---------|---------|--------------|
| Full sample (500) | Primary result | Standard analysis |
| U_line only (250) | Error-type effect | Filter to U_line errors |
| U_ignore only (250) | Error-type effect | Filter to U_ignore errors |
| Random baseline | Sanity check | Random line penalties |

**Expected Results:**
- U_line: Higher concentration ratio (localization reliable)
- U_ignore: Lower concentration ratio (localization unreliable)
- Random: ratio ≈ 1.0 (no localization)

---

## Appendix: Reference Implementations

### RLTF Paper Reference
- **Source:** Le et al., "RLTF: Reinforcement Learning from Unit Test Feedback for Code Generation" (2022)
- **Equations:** Fine-grained reward (Eq 4-5)
- **Key insight:** Per-token penalties based on error location

### H-E1 Implementation Reference
- **File:** `h-e1/code/reward.py`
- **Functions:**
  - `parse_traceback_line()` - Extract error line from traceback
  - `compute_gated_reward()` - Apply per-token penalties
- **Status:** Validated, tests passing

### Gradient Analysis References
- PyTorch autograd for per-token gradients
- Standard RL policy gradient: ∇θ J = E[∇θ log π(a|s) · R]

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M1 set to IN_PROGRESS (Phase 2C start)
- Prerequisites: H-E1 VALIDATED (PASS)

---

*MCP Tools Used: None (batch mode)*
*All specifications grounded in H-E1 validated implementation and RLTF paper*
*Next Phase: Phase 3 - Implementation Planning*
