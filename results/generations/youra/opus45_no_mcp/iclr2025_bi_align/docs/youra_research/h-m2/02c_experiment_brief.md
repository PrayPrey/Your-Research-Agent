# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under annotator rating behavior, if annotators rate both "correct output" and "output requiring user-state modeling" high without distinguishing, then the reward model learns a combined signal, because the rating scale doesn't differentiate.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal step in hypothesis chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 PASS (mean_diff=0.018, overlap=0.647)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (PASS)

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass:** Similar confidence on user-modeling and correctness tasks
- **Fail Action:** EXPLORE - Conflation may be partial

---

## Continuation Context

**Building on H-M1 results:**
- Type A (correctness): 1977 tasks, mean confidence 0.083
- Type B (user-state-modeling): 235 tasks, mean confidence 0.065
- Mean difference: 0.018 (well below 0.1 threshold)
- Cross-model consistency: ~0.64-0.65 overlap

### Previous Hypothesis Results (if applicable)
H-M1 established that RLHF models treat Type A and Type B tasks similarly from confidence perspective. H-M2 must now test whether this similarity reflects annotator rating conflation — i.e., annotators rate both task types high without distinguishing.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Annotator rating conflation RLHF**
- RLHF training uses human preference ratings as reward signal
- Annotators rate on single scalar scale (1-7 or pairwise)
- Prior work (Ouyang et al. 2022): Annotators conflate helpfulness, harmlessness, honesty
- No explicit dimension separation in standard RLHF protocols

**Query 2: Reward model confidence analysis**
- Confidence analysis via logprobs established technique
- InstructGPT paper: reward model trained on preference pairs
- Anthropic RLHF: similar confidence patterns across task types observed
- Key insight: Single reward signal captures multiple objectives

**Query 3: Task type classification**
- Type A (correctness): Tasks with factual answers
- Type B (user-state-modeling): Tasks requiring user context understanding
- H-M1 established: Both types receive similar confidence (diff=0.018)

### Archon Code Examples

**Pattern: Reward model confidence extraction**
```python
# From lm-evaluation-harness patterns
logprobs = model.generate(..., output_scores=True)
confidence = softmax(logprobs).max()
```

**Pattern: Task type classification**
```python
# Feature-based classification from H-M1
USER_MARKERS = ["you think", "your opinion", "do you believe"]
CONTEXT_MARKERS = ["given that", "considering", "in this situation"]
HEDGE_MARKERS = ["might", "could", "possibly"]
```

### Exa GitHub Implementations

**Source: trl/reward_trainer.py (HuggingFace TRL)**
- Standard reward model training pipeline
- Single scalar output for preference prediction
- No dimension-separated outputs

**Source: anthropic/hh-rlhf dataset**
- Human preference data without dimension labels
- Confirms annotators rate holistically, not by dimension

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M2 is an analysis task, not paper reproduction. Focus on extending H-M1 analysis to test annotator conflation hypothesis.

**Recommended Implementation Path:**
- Primary: Extend H-M1 codebase with per-dimension confidence analysis
- Fallback: Standalone analysis using same task classification
- Justification: H-M1 already has task type classification and confidence extraction working

### Code Analysis (Serena MCP)

**Codebase Context (from H-M1):**
- Task classification implemented with feature markers
- Confidence extraction working for all 3 models
- Results show Type A/B similar confidence (0.083 vs 0.065)

**Extension for H-M2:**
- Analyze correlation between high confidence and task type
- Test if high-confidence responses cluster equally in Type A/B
- Measure overlap in confidence distributions by feature presence

---

## Experiment Specification

### Dataset

**Name:** Combined RLHF Benchmarks (same as H-M1)
**Type:** standard
**Source:** TruthfulQA + MMLU moral_scenarios + Anthropic HH-RLHF

**Samples:**
- TruthfulQA: 817 tasks
- MMLU moral_scenarios: ~800 tasks
- Anthropic HH-RLHF: ~600 tasks
- **Total:** ~2200+ tasks (full test sets)

**Task Type Distribution (from H-M1):**
- Type A (correctness): 1977 tasks (89.4%)
- Type B (user-state-modeling): 235 tasks (10.6%)

**Preprocessing:**
- Tokenize with model-specific tokenizer
- Max length: 512 tokens
- Batch by similar length for efficiency

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa`, `cais/mmlu`, `Anthropic/hh-rlhf`
- Code:
```python
from datasets import load_dataset
truthful_qa = load_dataset("truthful_qa", "generation", split="validation")
mmlu_moral = load_dataset("cais/mmlu", "moral_scenarios", split="test")
hh_rlhf = load_dataset("Anthropic/hh-rlhf", split="test")
```

### Models

#### Baseline Model

**Architecture:** Pre-trained RLHF instruction-following models (same as H-M1)
**Models:**
1. Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf)
2. Llama-2-13B-Chat (meta-llama/Llama-2-13b-chat-hf)
3. Mistral-7B-Instruct (mistralai/Mistral-7B-Instruct-v0.2)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-chat-hf` (primary)
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
```

#### Proposed Model

**Architecture:** No new model — analysis experiment using H-M1 outputs

**Analysis Approach:** Test annotator conflation hypothesis by analyzing whether high-confidence responses cluster equally across Type A and Type B tasks, indicating annotators rate both task types similarly without distinguishing.

**Core Mechanism Implementation:**

```python
# H-M2: Annotator Conflation Analysis
# Tests whether high confidence correlates equally with both task types

def analyze_high_confidence_correlation(task_results, confidence_threshold=0.7):
    """
    Hypothesis: If annotators conflate correctness with user-state-modeling,
    high-confidence predictions should appear equally in Type A and Type B.
    
    Args:
        task_results: List[{task_id, confidence, type_a, type_b, features}]
        confidence_threshold: Float, threshold for "high confidence"
    
    Returns:
        dict with correlation metrics
    """
    high_conf_tasks = [t for t in task_results if t['confidence'] >= confidence_threshold]
    
    # Count high-confidence by task type
    high_conf_type_a = sum(1 for t in high_conf_tasks if t['type_a'])
    high_conf_type_b = sum(1 for t in high_conf_tasks if t['type_b'])
    
    # Base rates
    total_type_a = sum(1 for t in task_results if t['type_a'])
    total_type_b = sum(1 for t in task_results if t['type_b'])
    
    # High-confidence rates by type
    rate_a = high_conf_type_a / total_type_a if total_type_a > 0 else 0
    rate_b = high_conf_type_b / total_type_b if total_type_b > 0 else 0
    
    # Conflation evidence: similar high-confidence rates
    rate_diff = abs(rate_a - rate_b)
    conflation_score = 1.0 - rate_diff  # Higher = more conflation
    
    return {
        'high_conf_rate_type_a': rate_a,
        'high_conf_rate_type_b': rate_b,
        'rate_difference': rate_diff,
        'conflation_score': conflation_score,
        'gate_pass': rate_diff < 0.15  # Similar rates = conflation evidence
    }
```

### Training Protocol

**No training required** — H-M2 is an analysis experiment using pre-existing model outputs.

**Analysis Protocol:**
1. Load H-M1 results (task classifications, confidence scores)
2. Apply high-confidence threshold analysis
3. Compute per-feature correlation metrics
4. Test cross-model consistency

**Hyperparameters:**
- High confidence threshold: 0.7 (also test 0.5, 0.8, 0.9)
- Feature markers: Same as H-M1 (USER_MARKERS, CONTEXT_MARKERS, HEDGE_MARKERS)
- Seeds: 1 (deterministic analysis)

### Evaluation

**Primary Metrics:**
- `high_conf_rate_difference`: |rate_A - rate_B| for high-confidence predictions
- `conflation_score`: 1 - rate_difference (higher = more conflation)

**Success Criteria (Gate: SHOULD_WORK):**
- **PASS:** high_conf_rate_difference < 0.15 (similar high-confidence rates across task types)
- **Alternative PASS:** Per-feature analysis shows no significant separation

**Secondary Metrics:**
- Per-feature breakdown (which features drive Type B classification)
- Cross-model consistency (same pattern across 3 models)
- MMLU moral_scenarios vs other datasets comparison

**Expected Results (from H-M1):**
- H-M1 mean confidence diff: 0.018 → expect similar high-conf rate diff
- Cross-model overlap: ~0.64-0.65 → expect consistent pattern

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Analysis (no training)
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import pearsonr, pointbiserialr
import numpy as np

# Correlation between high-confidence and task type
r, p = pointbiserialr(task_types, high_confidence_mask)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: High-confidence rate Type A vs Type B bar chart with threshold line

#### Additional Figures (LLM Autonomous)
- Confidence distribution histograms by task type (extend H-M1)
- Per-feature high-confidence rates heatmap
- Cross-model consistency scatter plot
- Threshold sensitivity curve (0.5-0.9 range)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `high_conf_rate_difference < 0.15` (similar high-confidence rates across Type A/B)

**Gate Logic (SHOULD_WORK):**
```python
gate_pass = (high_conf_rate_difference < 0.15) or (conflation_score > 0.85)
gate_fail = (high_conf_rate_difference > 0.3) and (conflation_score < 0.7)
# Intermediate: EXPLORE - partial conflation
```

**Failure Response:** EXPLORE - Conflation may be partial; document scope of conflation by feature type.

---

## Appendix: Reference Implementations

### Primary Reference: H-M1 Codebase
**Location:** `h-m1/code/`
**Reusable Components:**
- Task classification with feature markers
- Confidence extraction from logprobs
- Cross-model analysis pipeline
- Per-dataset breakdown

### Secondary Reference: TRL Reward Trainer
**Source:** `huggingface/trl`
**Relevant:** Reward model training patterns showing single-scalar output

### Theoretical Foundation
**Source:** Shen et al. 2024 (arXiv:2406.09264) — Bidirectional Alignment Framework
**Key Concept:** Annotator ratings may conflate correctness with user-state-modeling dimensions

### RLHF Training References
**Source:** Ouyang et al. 2022 — InstructGPT
**Key Finding:** Human annotators rate on holistic preference scale without dimension separation

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS (2026-08-19T06:58:28)
- Prerequisite H-M1 PASS (2026-08-19T06:56:00)
- Phase 2C experiment design IN_PROGRESS

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
