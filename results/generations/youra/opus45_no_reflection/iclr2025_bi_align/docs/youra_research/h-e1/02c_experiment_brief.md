# Experiment Design: H-E1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Collaboration score extracts agency signals orthogonal to preference labels (correlation < 0.7)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - blocking downstream hypotheses

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation)

### Gate Condition
Correlation between collab_score_v2 and preference labels must be < 0.7. If >= 0.7, signal is redundant with preference labels and BiDPO hypothesis fails at foundation level.

---

## Continuation Context

First hypothesis in verification chain. No previous results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - This is the foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for DPO correlation analysis. General findings:
- Diffuser-based models with LoRA fine-tuning patterns available
- Multi-objective optimization patterns documented for diffusion models
- No specific preference correlation analysis examples in KB

### Archon Code Examples

No directly relevant DPO/preference correlation code in Archon KB. Fallback to Exa GitHub search.

### Exa GitHub Implementations

**Key Findings:**

1. **HH-RLHF Dataset Structure** (Anthropic/hh-rlhf):
   - Format: JSONL with "chosen" and "rejected" response pairs
   - Subsets: helpful-base, harmless-base, red-team-attempts
   - Loading: `load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")`
   - ~160,800 preference pairs in full dataset

2. **TRL DPOTrainer Multi-Loss Support** (huggingface/trl):
   - Native support for `loss_type=["sigmoid", "bco_pair", "sft"]` with `loss_weights`
   - `router_aux_loss_coef` for auxiliary loss integration
   - Can extend for custom auxiliary losses

3. **MODPO Implementation** (ZHZisZZ/modpo):
   - ACL'24 paper: "Beyond One-Preference-Fits-All Alignment"
   - Adds margin to DPO loss for multi-objective steering
   - Directly relevant pattern for BiDPO auxiliary loss

4. **LewallenAE/rlhf-eval**:
   - Dataset quality analysis tool for HH-RLHF
   - Semantic similarity, readability mismatch detectors
   - Useful patterns for text analysis on preference data

### Implementation Priority Assessment

**CRITICAL: For H-E1, no model training required - pure statistical analysis**

**Recommended Implementation Path:**
- Primary: Direct HH-RLHF analysis with scipy.stats correlation
- Fallback: N/A (simple statistical test)
- Justification: Existence hypothesis only requires correlation computation, not training

### Code Analysis (Serena MCP)

Not applicable - H-E1 is a statistical analysis task, no codebase to analyze.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | Anthropic HH-RLHF |
| **Version** | Latest (HuggingFace) |
| **Source** | Anthropic/hh-rlhf |
| **Type** | standard |
| **Subset** | helpful-base |
| **Train Split** | ~160,800 pairs |
| **Sample Size** | 1,000 random pairs (per protocol) |
| **Preprocessing** | Extract final assistant response from conversation |
| **Augmentation** | None |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: Anthropic/hh-rlhf
- Code:
```python
from datasets import load_dataset

dataset = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base", split="train")
# Sample 1000 random pairs
dataset = dataset.shuffle(seed=42).select(range(1000))
```

### Models

#### Baseline Model

No model required for H-E1. This is a statistical analysis experiment.

**Loading Information** (for Phase 4 download):
- Method: N/A
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** N/A (statistical analysis only)

**Core Mechanism Implementation:**

```python
import re
import numpy as np
from scipy import stats

def compute_collab_score_v2(response: str) -> float:
    """
    Length-normalized collaboration score measuring agency-preservation signals.
    
    Signals (HCI research-derived):
    1. Reasoning traces: "because", "since", "therefore", "this means"
    2. Uncertainty acknowledgment: "I think", "might", "could", "uncertain"
    3. User engagement: "you could", "consider", "option", question marks
    4. Explanation depth: numbered lists, "first", "second", "step"
    """
    if not response or len(response) < 10:
        return 0.0
    
    response_lower = response.lower()
    word_count = len(response.split())
    
    # Reasoning trace signals
    reasoning_patterns = [
        r'\bbecause\b', r'\bsince\b', r'\btherefore\b', 
        r'\bthis means\b', r'\bas a result\b', r'\bso that\b'
    ]
    reasoning_score = sum(len(re.findall(p, response_lower)) for p in reasoning_patterns)
    
    # Uncertainty acknowledgment signals
    uncertainty_patterns = [
        r'\bi think\b', r'\bmight\b', r'\bcould be\b',
        r'\bperhaps\b', r'\buncertain\b', r'\bpossibly\b'
    ]
    uncertainty_score = sum(len(re.findall(p, response_lower)) for p in uncertainty_patterns)
    
    # User engagement signals
    engagement_patterns = [
        r'\byou could\b', r'\bconsider\b', r'\boption\b',
        r'\byou might\b', r'\bwhat do you\b'
    ]
    engagement_score = sum(len(re.findall(p, response_lower)) for p in engagement_patterns)
    question_count = response.count('?')
    engagement_score += question_count
    
    # Explanation depth signals
    depth_patterns = [
        r'\bfirst\b', r'\bsecond\b', r'\bthird\b',
        r'\bstep \d', r'^\d+\.', r'^-\s'
    ]
    depth_score = sum(len(re.findall(p, response_lower, re.MULTILINE)) for p in depth_patterns)
    
    # Combine and normalize by word count
    raw_score = reasoning_score + uncertainty_score + engagement_score + depth_score
    normalized_score = raw_score / np.sqrt(word_count)  # sqrt normalization
    
    return normalized_score


def compute_correlation(dataset, n_samples: int = 1000) -> dict:
    """
    Compute Pearson correlation between collab_score and preference labels.
    
    Returns:
        dict with correlation, p_value, and score distributions
    """
    chosen_scores = []
    rejected_scores = []
    
    for i, example in enumerate(dataset):
        if i >= n_samples:
            break
            
        chosen_text = extract_assistant_response(example['chosen'])
        rejected_text = extract_assistant_response(example['rejected'])
        
        chosen_scores.append(compute_collab_score_v2(chosen_text))
        rejected_scores.append(compute_collab_score_v2(rejected_text))
    
    # Create paired data for correlation
    # Label: chosen=1, rejected=0
    all_scores = chosen_scores + rejected_scores
    all_labels = [1] * len(chosen_scores) + [0] * len(rejected_scores)
    
    correlation, p_value = stats.pearsonr(all_scores, all_labels)
    
    return {
        'correlation': correlation,
        'p_value': p_value,
        'chosen_mean': np.mean(chosen_scores),
        'rejected_mean': np.mean(rejected_scores),
        'chosen_std': np.std(chosen_scores),
        'rejected_std': np.std(rejected_scores),
        'gate_passed': abs(correlation) < 0.7
    }


def extract_assistant_response(conversation: str) -> str:
    """Extract the final assistant response from HH-RLHF conversation format."""
    # HH-RLHF format: "\n\nHuman: ...\n\nAssistant: ..."
    parts = conversation.split('\n\nAssistant: ')
    if len(parts) > 1:
        return parts[-1].strip()
    return conversation
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Training Required** | No | Statistical analysis only |
| **Computation** | CPU sufficient | Correlation on 2000 text samples |
| **Random Seed** | 42 | Reproducibility |
| **Sample Size** | 1000 pairs | Per Phase 2B protocol |

### Evaluation

| Metric | Formula | Threshold | Justification |
|--------|---------|-----------|---------------|
| **Pearson Correlation** | r(collab_score, label) | r < 0.7 | Orthogonality criterion |
| **P-value** | From Pearson test | p < 0.05 | Statistical significance |
| **Score Variance** | std(scores) | > 0 | Meaningful signal exists |
| **Mean Difference** | chosen_mean - rejected_mean | Reported | Direction of association |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical correlation
- Library: scipy.stats
- Code:
```python
from scipy import stats
import numpy as np

correlation, p_value = stats.pearsonr(scores, labels)
variance = np.var(scores)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing correlation coefficient vs 0.7 threshold

#### Additional Figures (LLM Autonomous)

1. **Score Distribution Histogram**: Chosen vs rejected collab_score distributions (overlapping histograms)
2. **Scatter Plot**: collab_score vs preference label with regression line
3. **Box Plot**: Side-by-side comparison of chosen/rejected score distributions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `abs(correlation) < 0.7` (signal is orthogonal to preference)

**Secondary Success Indicators:**
- Score variance > 0 (signal has information content)
- Chosen and rejected distributions are distinguishable
- P-value < 0.05 (correlation is statistically significant)

---

## Appendix: Reference Implementations

### 1. HH-RLHF Dataset Loading (TRL/HuggingFace)
```python
# Source: huggingface/trl examples/datasets/hh-rlhf-helpful-base.py
from datasets import load_dataset

dataset = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")
```

### 2. Text Analysis Patterns (LewallenAE/rlhf-eval)
```python
# Source: LewallenAE/rlhf-eval - detector patterns
# Readability, length ratio, semantic similarity detectors
# Adapted for collaboration score computation
```

### 3. Multi-Objective DPO Pattern (ZHZisZZ/modpo)
```python
# Source: MODPO - margin-based multi-objective extension
# Relevant for H-M1+ hypotheses (training integration)
# Loss: L_MODPO = L_DPO + margin_term
```

### 4. Scipy Correlation Analysis
```python
# Standard statistical correlation
from scipy import stats
r, p = stats.pearsonr(x, y)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18T13:47:47Z

### Workflow History for This Hypothesis
1. 2026-08-18: H-E1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
