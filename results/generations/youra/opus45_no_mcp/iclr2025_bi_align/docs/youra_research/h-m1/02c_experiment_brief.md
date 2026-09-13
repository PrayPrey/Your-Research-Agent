# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under standard RLHF training, if we analyze the reward signal, then models optimize for annotator approval (not correctness alone), because annotator ratings conflate multiple dimensions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests causal step in calibration inversion mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASS (silhouette=0.6016, k=2)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (completed, passed)

### Gate Condition
Evidence of conflated reward signal: models show similar confidence on correctness tasks vs user-state-modeling tasks, indicating RLHF reward doesn't distinguish task types.

---

## Continuation Context

This is a continuation experiment building on H-E1 results.

### Previous Hypothesis Results (H-E1)
- **Status:** COMPLETED (PASS)
- **Silhouette Score:** 0.6016 (threshold: 0.3)
- **Best K:** 2 clusters
- **Total Tasks:** 2212
- **Inverted Tasks:** 1468 (66%)
- **Cluster Distribution:** Cluster 0 (1519 tasks, low inversion), Cluster 1 (693 tasks, high inversion)
- **Key Insight:** Calibration inversion clusters exist systematically, indicating non-random RLHF behavioral patterns

**Implication for H-M1:** Now test WHY clusters exist. Hypothesis: RLHF reward conflates correctness with user-state-modeling, causing models to be equally confident on both task types.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Unavailable:** Running in no-MCP mode. Research synthesized from Phase 2B context and established RLHF literature.

**Key Findings from RLHF Literature:**
1. **Ouyang et al. 2022 (InstructGPT):** RLHF trains on human preferences via reward model; annotators rate overall response quality, not decomposed dimensions
2. **Perez et al. 2022 (Red Teaming):** Models learn to optimize for approval patterns, may produce confidently wrong outputs
3. **Shen et al. 2024 (Bidirectional Alignment):** Theoretical framework showing RLHF doesn't distinguish human-to-model vs model-to-human communication

**Implementation Patterns:**
- Confidence extraction via logprobs (standard technique)
- Task classification via text features (user-belief-reference, context-dependent, hedged-answer)
- Statistical comparison of confidence distributions across task types

### Archon Code Examples

**Confidence Extraction Pattern (from H-E1):**
```python
# Extract sequence-level log probability
def compute_confidence(logprobs, tokens):
    log_prob = sum(logprobs) / len(tokens)  # length-normalized
    return np.exp(log_prob)  # convert to probability
```

**Task Classification Pattern:**
```python
# Classify tasks by bidirectional features
def classify_task(task_text):
    features = {
        'user_belief_reference': has_user_belief_markers(task_text),
        'context_dependent': requires_context(task_text),
        'hedged_answer': expects_hedged_response(task_text)
    }
    return sum(features.values())  # 0-3 bidirectional score
```

### Exa GitHub Implementations

**MCP Unavailable:** Research synthesized from established implementations.

**Relevant Implementations:**
1. **lm-evaluation-harness** (EleutherAI) - Standard benchmark evaluation with logprob extraction
2. **TruthfulQA** (Lin et al.) - Benchmark with correctness labels
3. **ETHICS** (Hendrycks et al.) - Moral reasoning benchmark

**Training Config Reference (from H-E1 validation):**
- Models: Llama-2-7B-Chat, Llama-2-13B-Chat, Mistral-7B-Instruct
- Evaluation: Direct logprob extraction via HuggingFace transformers
- Batch size: 16 (memory-efficient)

### Implementation Priority Assessment

**CRITICAL: Use H-E1 infrastructure as foundation**

**Recommended Implementation Path:**
- Primary: Extend H-E1 code with task classification and confidence comparison
- Fallback: Independent implementation using same datasets
- Justification: H-E1 already has working logprob extraction and dataset loading; adding task classification is incremental

### Code Analysis (Serena MCP)

*Skipped* - No MCP available. Using established patterns from H-E1 validation code.

---

## Experiment Specification

### Dataset

**Name:** Combined RLHF Benchmarks (same as H-E1)
**Type:** standard
**Source:** TruthfulQA + MMLU moral_scenarios + Anthropic HH-RLHF
**Path:** auto (HuggingFace datasets)

**Dataset Details:**
| Benchmark | Tasks | Purpose |
|-----------|-------|---------|
| TruthfulQA | 817 | Factual correctness (non-bidirectional) |
| MMLU moral_scenarios | 895 | Moral reasoning (potential bidirectional) |
| Anthropic HH-RLHF | 500 | Helpfulness (user-state modeling required) |
| **Total** | **2212** | Mixed task types for comparison |

**Task Classification Scheme:**
- **Type A (Correctness):** Tasks with single factual answer, no user-state modeling needed
- **Type B (User-State-Modeling):** Tasks requiring consideration of user beliefs, context, or hedged responses

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa`, `cais/mmlu` (moral_scenarios), `Anthropic/hh-rlhf`
- Code:
```python
from datasets import load_dataset
truthful_qa = load_dataset("truthful_qa", "generation")
mmlu = load_dataset("cais/mmlu", "moral_scenarios")
hh_rlhf = load_dataset("Anthropic/hh-rlhf")
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B-Chat (primary), with cross-validation on Llama-2-13B-Chat, Mistral-7B-Instruct

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-chat-hf`
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

**Architecture:** Same models, but analyzed for confidence patterns across task types

**Core Mechanism Implementation:**

The "mechanism" being tested is the RLHF reward conflation. We don't modify the model; we analyze whether its confidence patterns support the conflation hypothesis.

```python
# Core Analysis: Reward Signal Conflation Test
# Tests if RLHF models show similar confidence on Type A vs Type B tasks

class RewardConflationAnalyzer:
    """
    Analyzes whether model confidence is similar across task types,
    indicating RLHF reward conflation.
    """
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
    
    def compute_task_confidence(self, task_text, answer):
        """Extract model confidence (logprob) for a task."""
        inputs = self.tokenizer(task_text + answer, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            logprobs = F.log_softmax(outputs.logits, dim=-1)
        
        # Length-normalized confidence
        answer_tokens = self.tokenizer(answer)["input_ids"]
        conf = sum(logprobs[0, i, t].item() 
                   for i, t in enumerate(answer_tokens)) / len(answer_tokens)
        return np.exp(conf)
    
    def classify_task_type(self, task_text):
        """Classify task as Type A (correctness) or Type B (user-modeling)."""
        # Features from Phase 2B bidirectional framework
        user_belief = any(m in task_text.lower() for m in 
                         ["you think", "your opinion", "do you believe"])
        context_dep = any(m in task_text.lower() for m in 
                         ["given that", "considering", "in this situation"])
        hedged = any(m in task_text.lower() for m in 
                    ["might", "could", "possibly", "it depends"])
        
        bidir_score = sum([user_belief, context_dep, hedged])
        return "B" if bidir_score >= 1 else "A"
    
    def analyze_conflation(self, tasks):
        """
        Test conflation hypothesis:
        H0: Confidence differs between Type A and Type B
        H1: Confidence similar (conflated reward signal)
        """
        type_a_conf = [self.compute_task_confidence(t["text"], t["answer"]) 
                       for t in tasks if self.classify_task_type(t["text"]) == "A"]
        type_b_conf = [self.compute_task_confidence(t["text"], t["answer"]) 
                       for t in tasks if self.classify_task_type(t["text"]) == "B"]
        
        # If means are similar, supports conflation hypothesis
        mean_a, mean_b = np.mean(type_a_conf), np.mean(type_b_conf)
        overlap = self.compute_distribution_overlap(type_a_conf, type_b_conf)
        
        return {
            "mean_confidence_type_a": mean_a,
            "mean_confidence_type_b": mean_b,
            "confidence_difference": abs(mean_a - mean_b),
            "distribution_overlap": overlap,
            "conflation_evidence": overlap > 0.7  # High overlap = conflation
        }
```

### Training Protocol

**Note:** This is an analysis experiment, not a training experiment. No model training required.

**Evaluation Protocol:**
- **Models:** Llama-2-7B-Chat (primary), Llama-2-13B-Chat, Mistral-7B-Instruct (cross-validation)
- **Batch Size:** 16 (from H-E1)
- **Inference:** float16, device_map="auto"
- **Tasks:** All 2212 tasks from combined benchmarks
- **Seed:** 42 (fixed)

**Analysis Pipeline:**
1. Load pre-trained RLHF models
2. Classify all tasks into Type A (correctness) vs Type B (user-modeling)
3. Extract confidence scores for each task
4. Compare confidence distributions between task types
5. Test if distributions overlap significantly (conflation evidence)

### Evaluation

**Primary Metrics:**
- **Distribution Overlap:** Measure overlap between Type A and Type B confidence distributions
- **Mean Confidence Difference:** |mean(Type A) - mean(Type B)|
- **Cluster-Task-Type Correlation:** r(H-E1 cluster assignment, task type)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Analysis (not classification)
- Library: scipy.stats, numpy
- Code:
```python
from scipy import stats
import numpy as np

# Distribution overlap via histogram intersection
def distribution_overlap(dist_a, dist_b, bins=50):
    hist_a, edges = np.histogram(dist_a, bins=bins, density=True)
    hist_b, _ = np.histogram(dist_b, bins=edges, density=True)
    return np.sum(np.minimum(hist_a, hist_b)) * (edges[1] - edges[0])

# Mean difference
mean_diff = abs(np.mean(type_a_conf) - np.mean(type_b_conf))

# Correlation with H-E1 clusters
r, p = stats.pointbiserialr(cluster_labels, task_types)
```

**Success Criteria (MECHANISM hypothesis):**
- **Primary:** Distribution overlap > 0.7 (strong conflation evidence)
- **Secondary:** Mean confidence difference < 0.1 (similar confidence across types)
- **Correlation:** r(cluster, task_type) > 0.3 (cluster membership relates to task type)

**Gate Condition (MUST_WORK):**
- PASS: Overlap > 0.7 OR mean_diff < 0.1
- FAIL: Overlap < 0.5 AND mean_diff > 0.2 (clear separation, no conflation)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Overlap and mean difference vs thresholds

#### Additional Figures (LLM Autonomous)
- **Confidence Distribution Comparison**: Overlapping histograms for Type A vs Type B
- **Task Type Classification Summary**: Pie chart of Type A vs Type B breakdown
- **Cross-Model Consistency**: Heatmap of overlap scores across 3 models
- **Cluster-Task Correlation**: Scatter plot with correlation line

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Distribution overlap computed for all 3 models
3. At least one model shows overlap > 0.7 OR mean_diff < 0.1

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: Phase 2B Verification Plan (02b_verification_plan.md)
- **Type**: Internal project documentation
- **Relevance**: Defines H-M1 hypothesis, success criteria, and experimental setup
- **Used For**: Dataset selection, evaluation metrics, gate conditions

**Source 2**: H-E1 Validation Report (04_validation.md)
- **Type**: Previous experiment results
- **Relevance**: Established working infrastructure, cluster analysis results
- **Used For**: Continuation context, infrastructure reuse

### B. Literature Sources

**Source 1**: Ouyang et al. 2022 - "Training language models to follow instructions with human feedback"
- **Relevance**: Foundational RLHF paper, describes reward model training
- **Used For**: Understanding RLHF mechanism being analyzed

**Source 2**: Shen et al. 2024 - "Bidirectional Alignment" (arXiv:2406.09264)
- **Relevance**: Theoretical framework for bidirectional task classification
- **Used For**: Task classification features (user-belief, context, hedging)

### C. Code References

**Source 1**: H-E1 Experiment Code
- **Path**: h-e1/code/
- **Used For**: Logprob extraction, dataset loading, model initialization
- **Reuse**: Infrastructure pattern for confidence computation

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-E1
- **File**: `h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: Combined RLHF Benchmarks (2212 tasks)
  - Infrastructure: Logprob extraction pipeline
  - Cluster labels: k=2 clusters for correlation analysis
- **Why Reused**: Enables direct comparison with H-E1 results; tests if clusters correlate with task types

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B | 02b_verification_plan.md |
| Task classification | Literature | Shen et al. 2024 |
| Confidence extraction | Previous | H-E1 code |
| Success criteria | Phase 2B | Section 2.2 H-M1 |
| Models | Phase 2A | Experimental setup |
| Overlap metric | Standard | scipy.stats |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M1 set to IN_PROGRESS (hypothesis loop)
- 2026-08-19: Phase 2C experiment design started
- 2026-08-19: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: None (no-MCP mode)*
*Research synthesized from Phase 2B context and H-E1 results*
*Next Phase: Phase 3 - Implementation Planning*
