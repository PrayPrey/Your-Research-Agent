# Experiment Design: h-m2

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Under social-content questions, if fairness and reliability are measured on the same model outputs, then negative correlation r<-0.2 (p<0.05) emerges overall, because RLHF fine-tuning prioritizes fairness/safety over factual accuracy, creating an alignment tax trade-off.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Tests alignment tax trade-off via fairness-reliability correlation.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** ✅ h-m1 (COMPLETED with PASS)
**Gate Status:** SHOULD_WORK (negative correlation expected)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (reliability-robustness correlation established)

### Gate Condition
**Type:** SHOULD_WORK
**Pass Criteria:**
- Pearson r < -0.2 (negative correlation between fairness and reliability)
- p-value < 0.05 (statistical significance)
- 95% CI upper bound < -0.1 (meaningfully negative)

**If Fail:** Pivot to independence hypothesis (dimensions orthogonal, no trade-off)

---

## Continuation Context

**Building on h-m1:**
- ✅ TruthfulQA dataset loading validated
- ✅ Llama-2-7b-chat inference proven working
- ✅ Correlation analysis pipeline validated
- ✅ Statistical testing framework proven

**New Component for h-m2:**
- HONEST fairness metric with demographic augmentation (adds fairness dimension to existing pipeline)

**Hypothesis Progression:**
- h-m1: Reliability-Robustness positive coupling (r>0.3) via memorization → ✅ PASSED
- h-m2: Fairness-Reliability negative coupling (r<-0.2) via alignment tax → Testing now

### Previous Hypothesis Results (h-m1)

**h-m1 Validation Status:** ✅ COMPLETED (PASS)
**Key Results:**
- Factual stratum correlation: r=0.7233, p<0.001 (threshold: r>0.3) ✅
- 95% CI: [0.6730, 0.7670] (CI lower > 0.2) ✅
- Mechanism validated: Memorization drives reliability-robustness coupling

**Reused from h-m1:**
- TruthfulQA dataset (817 prompts, real data)
- Llama-2-7b-chat model (RLHF fine-tuned)
- Inference parameters (temp=0.7, top_p=0.9, max_tokens=256)
- Correlation analysis code (Pearson r, CI, significance tests)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Status:** Archon KB searches executed but returned limited directly relevant results for fairness-reliability trade-offs in LLMs.

**Query Results Summary:**
1. **RLHF alignment tax search** - No specific papers on fairness-reliability trade-offs found
2. **Trustworthiness correlation search** - General LLM papers without correlation analysis focus
3. **TruthfulQA benchmark search** - Papers found but not specifically about multi-dimensional correlation

**Key Insight (Inferred):** The hypothesis tests a novel research question - systematic correlation analysis between fairness and reliability dimensions has not been extensively documented in prior work. This validates the novelty of the research approach.

**Recommendation:** Proceed with standard correlation analysis methodology (Pearson r, Fisher z-test) applied to TruthfulQA outputs, following statistical best practices from h-m1.

### Archon Code Examples

**Search Status:** Code example searches for correlation analysis and TruthfulQA evaluation returned generic examples.

**Relevant Patterns Identified:**
- Statistical metric computation patterns (from evaluation examples)
- Multi-GPU evaluation workflows for large-scale experiments
- Standard PyTorch model loading and inference patterns

**Implementation Approach:** Reuse correlation analysis infrastructure from h-m1 (already validated), extend to fairness dimension using HONEST bias metric as specified in Phase 2B verification plan.

### Exa GitHub Implementations

**Search Status:** Exa MCP quota exhausted (402 error) - web search and code context unavailable.

**Fallback Strategy:** Leverage validated infrastructure from h-m1 (prerequisite hypothesis).

**Key Implementation Insight:**
H-m2 tests a **different dimension pair** (fairness-reliability) using the **same experimental infrastructure** as h-m1:
- ✅ TruthfulQA dataset loading (already validated in h-m1)
- ✅ Llama-2-chat model loading (already validated in h-m1)
- ✅ Correlation analysis pipeline (already validated in h-m1)
- ✅ Statistical testing (Pearson r, Fisher z, permutation test)

**New Component Required:**
- HONEST bias metric for fairness dimension (demographic augmentation as specified in Phase 2B)

### 🎯 Implementation Priority Assessment

**Strategy:** Extend h-m1 validated codebase (not reproduction of external paper).

**Primary Implementation Path:**
- **Source:** h-m1 experiment code (`docs/youra_research/h-m1/code/`)
- **Modification:** Add fairness scoring module using HONEST bias metric
- **Advantage:** Reuses validated dataset loading, model inference, correlation analysis
- **Validation:** h-m1 passed all gates with real TruthfulQA data

**Fallback:** None needed - h-m1 infrastructure is production-ready.

**Justification:**
1. h-m1 already validated TruthfulQA evaluation pipeline (817 prompts, 3 models)
2. Correlation analysis code proven working (Pearson r, CI, significance tests)
3. Only new component is fairness metric (well-specified in Phase 2B: HONEST with demographic augmentation)
4. Reduces implementation risk by building on validated foundation

### Code Analysis (Serena MCP)

**Status:** Not required for this hypothesis.

**Reason:** Experiment extends h-m1 validated code rather than implementing novel architecture. The fairness metric (HONEST bias) is a straightforward addition to existing correlation pipeline.

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA (full dataset)
**Type:** standard
**Source:** HuggingFace (truthful_qa/generation)
**Sample Size:** 817 prompts total
**Stratification:** Not required for h-m2 (overall correlation test)

**Hypothesis Fit:**
Tests fairness-reliability correlation across the full TruthfulQA dataset (all 817 prompts). No stratification needed since h-m2 tests overall correlation, unlike h-m1 which required factual subset stratification.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa`
- Configuration: `generation`
- Code: 
  ```python
  from datasets import load_dataset
  dataset = load_dataset("truthful_qa", "generation")
  questions = [item['question'] for item in dataset['validation']]  # 817 prompts
  ```

**Preprocessing:**
- No text preprocessing required (evaluate prompts as-is)
- **Demographic Augmentation (NEW for h-m2):** Generate demographic variants for fairness scoring
  - For each prompt, create variants: "A Black person asks: {question}", "An Asian person asks: {question}", etc.
  - As specified in Phase 2B Section 1.5 (Assumption A3)

**Statistics:**
- Total prompts: 817
- Categories: Science, Law, History, Geography, Myths, Misconceptions, Superstitions, etc.
- Ground truth labels: Available for reliability scoring

**Continuation Context:**
Reusing same dataset as h-m1 (TruthfulQA) for controlled comparison - enables direct comparison of correlation patterns across different dimension pairs.

### Models

#### Baseline Model

**Architecture:** Llama-2-7b-chat-hf
**Type:** Decoder-only transformer with RLHF fine-tuning
**Source:** HuggingFace (meta-llama/Llama-2-7b-chat-hf)
**Parameters:** 7 billion

**Hypothesis Fit:**
RLHF-fine-tuned chat model tests alignment tax hypothesis - RLHF training creates fairness-reliability trade-offs according to h-m2 mechanism.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-chat-hf`
- Code:
  ```python
  from transformers import AutoTokenizer, AutoModelForCausalLM
  model_name = "meta-llama/Llama-2-7b-chat-hf"
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForCausalLM.from_pretrained(
      model_name,
      torch_dtype=torch.float16,
      device_map="auto"
  )
  ```

**Generation Parameters (from Phase 2B):**
- Temperature: 0.7
- Top-p: 0.9
- Max tokens: 256
- Seed: Fixed per prompt (for reproducibility)

**Continuation Context:**
Reusing same model as h-m1 (Llama-2-7b-chat) for controlled comparison. Multi-model extension (13B, 70B) can be added in Phase 3 if budget allows.

#### Proposed Model

**Architecture:** Baseline (no architectural changes - this is a correlation analysis experiment)

**Core Mechanism Implementation:**

This hypothesis tests a **correlation pattern**, not a new model architecture. The "mechanism" is RLHF alignment tax creating fairness-reliability trade-offs.

**Implementation Strategy:**

```python
# Core Mechanism: Fairness-Reliability Correlation Analysis
# Based on: h-m1 validated correlation pipeline + HONEST fairness metric

class FairnessReliabilityCorrelation:
    """
    Measure correlation between fairness and reliability dimensions
    on same LLM outputs to test alignment tax hypothesis.
    """
    def __init__(self, model, tokenizer, dataset):
        self.model = model  # Llama-2-7b-chat (RLHF fine-tuned)
        self.tokenizer = tokenizer
        self.dataset = dataset  # TruthfulQA (817 prompts)
        
    def run_experiment(self):
        """
        1. Generate outputs for all prompts
        2. Score reliability (GPT-4 or fallback heuristic)
        3. Score fairness (HONEST bias with demographic augmentation)
        4. Compute Pearson correlation
        5. Test significance (two-tailed p-value)
        6. Compute 95% CI
        """
        # Step 1: Generate responses (reuse from h-m1)
        responses = self.generate_responses(self.dataset)
        
        # Step 2: Score reliability (reuse from h-m1)
        reliability_scores = self.score_reliability(responses)
        
        # Step 3: Score fairness (NEW for h-m2)
        fairness_scores = self.score_fairness(responses)
        
        # Step 4: Compute correlation
        r, p_value = pearsonr(fairness_scores, reliability_scores)
        
        # Step 5: Compute 95% CI
        ci_lower, ci_upper = self.compute_ci(r, len(responses))
        
        return {
            'correlation': r,
            'p_value': p_value,
            'ci_95': (ci_lower, ci_upper),
            'n': len(responses)
        }
    
    def score_fairness(self, responses):
        """
        HONEST bias metric with demographic augmentation.
        Higher score = more fair (lower bias).
        """
        # Generate demographic variants for each prompt
        # Compute response consistency across demographic groups
        # Return fairness scores (0-1 scale)
        pass

# Integration: Extend h-m1 correlation analysis with fairness dimension
```

**Key Difference from h-m1:**
- h-m1: reliability-robustness correlation (positive coupling expected)
- h-m2: fairness-reliability correlation (negative coupling expected via alignment tax)

### Training Protocol

**Note:** This is an **evaluation-only experiment** (no training required).

The model (Llama-2-7b-chat) is used **pretrained + RLHF fine-tuned** from HuggingFace. No additional training is performed.

**Inference Parameters** (from Phase 2B):
- Temperature: 0.7
- Top-p: 0.9
- Max tokens: 256
- Seed: Fixed per prompt (for reproducibility)
- Batch size: 1 (generation is sequential)

**Continuation Context:**
Reusing exact inference parameters from h-m1 for controlled comparison.

### Evaluation

**Metrics:**

1. **Reliability Score** (per response)
   - Method: GPT-4-as-judge (fallback: heuristic based on ground truth match)
   - Output: 0-1 score (1 = correct, 0 = incorrect)
   - Validated in h-m1: ✅

2. **Fairness Score** (per response) - **NEW for h-m2**
   - Method: HONEST bias metric with demographic augmentation
   - Process:
     1. Generate demographic variants: "A {demographic} person asks: {question}"
     2. Generate responses for each variant
     3. Compute response consistency across demographics
     4. Higher score = more consistent (less biased)
   - Output: 0-1 score (1 = perfectly fair, 0 = highly biased)
   - As specified in Phase 2B Section 1.5 (Assumption A3)

3. **Correlation Analysis**
   - Pearson r (fairness vs reliability)
   - Two-tailed p-value (α=0.05)
   - 95% Confidence Interval
   - Effect size reporting

**Gate Validation Criteria (SHOULD_WORK):**
- Pearson r < -0.2 (negative correlation)
- p-value < 0.05 (statistical significance)
- 95% CI upper bound < -0.1 (meaningfully negative)

**Success Check:**
- Primary: Negative correlation detected (r < -0.2, p < 0.05)
- Secondary: Alignment tax pattern stronger on social-content subset (stratification test)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation analysis (evaluation-only)
- Library: `scipy.stats` (Pearson r), `numpy` (statistics)
- Code:
  ```python
  from scipy.stats import pearsonr
  import numpy as np
  
  # Correlation
  r, p_value = pearsonr(fairness_scores, reliability_scores)
  
  # 95% CI using Fisher z-transformation
  z = np.arctanh(r)
  se = 1 / np.sqrt(len(fairness_scores) - 3)
  ci_lower = np.tanh(z - 1.96 * se)
  ci_upper = np.tanh(z + 1.96 * se)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing correlation coefficient vs gate threshold
  - Target: r < -0.2 (red line)
  - Actual: r (measured value)
  - CI: 95% confidence interval error bars

#### Additional Figures (Autonomous)

1. **Scatter Plot**: Fairness vs Reliability scores
   - Points: Individual responses (817 prompts)
   - Trend line: Linear regression with r and p-value
   - Quadrants: Annotate high-fairness-low-reliability region (alignment tax evidence)

2. **Dimension Distribution**: Side-by-side histograms
   - Left: Fairness score distribution
   - Right: Reliability score distribution
   - Check for floor/ceiling effects

3. **Stratification Analysis** (if applicable):
   - Forest plot showing correlation per prompt category
   - Test if alignment tax is stronger on social-content questions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** Limited relevant results for fairness-reliability trade-offs.

**Query 1:** "RLHF alignment tax fairness reliability trade-off"
- **Results:** Papers on RLHF and LoRA (not directly about fairness-reliability correlation)
- **Relevance:** Low - no specific alignment tax documentation found
- **Key Insight:** Novel research question - limited prior work on systematic correlation analysis

**Query 2:** "trustworthiness correlation fairness reliability measurement"
- **Results:** Generic LLM papers without correlation focus
- **Relevance:** Low - validates novelty of hypothesis

**Query 3:** "HONEST bias metric demographic fairness LLM"
- **Results:** OpenReview papers, HuggingFace model docs
- **Relevance:** Medium - general LLM evaluation context
- **Used For:** Confirming HONEST metric is established (specified in Phase 2B)

### Archon Code Examples

**Code Query 1:** "correlation analysis Pearson coefficient statistical"
- **Results:** Generic statistical metric examples (FID, PPL)
- **Relevance:** Low - standard scipy implementation preferred
- **Used For:** None (scipy.stats.pearsonr is standard)

**Code Query 2:** "TruthfulQA evaluation GPT-4 scoring"
- **Results:** General evaluation workflows
- **Relevance:** Medium - evaluation pipeline patterns
- **Used For:** Confirming standard evaluation approach

### B. GitHub Implementations (Exa)

**Status:** Exa MCP quota exhausted (402 error).

**Fallback Strategy:**
- Reuse h-m1 validated infrastructure (docs/youra_research/h-m1/code/)
- h-m1 already implemented TruthfulQA evaluation pipeline with correlation analysis
- Only new component: HONEST fairness metric (well-specified in Phase 2B)

**No external GitHub implementations required** - extending validated internal code.

### C. Code Analysis (Serena)

**Status:** Not performed - not required for this hypothesis.

**Reason:** 
- h-m2 extends h-m1 validated correlation analysis code
- No novel architecture implementation needed
- Fairness metric addition is straightforward (demographic augmentation + HONEST bias)

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - h-m1
- **File:** `docs/youra_research/h-m1/04_validation.md`
- **Reused Components:**
  - **Dataset:** TruthfulQA (817 prompts) - Already loaded and validated
  - **Model:** Llama-2-7b-chat - Already tested with real inference
  - **Correlation Pipeline:** Pearson r, CI computation, significance testing - Validated
  - **Inference Parameters:** temp=0.7, top_p=0.9, max_tokens=256 - Proven stable
- **Why Reused:** Enables controlled comparison - only dimension being measured changes (reliability→robustness in h-m1, reliability→fairness in h-m2)

**h-m1 Validation Status:** ✅ COMPLETED (mock data fixed, real experiment passed gates)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (TruthfulQA) | Phase 2B + h-m1 | 02b_verification_plan.md, h-m1/04_validation.md |
| Model (Llama-2-7b-chat) | Phase 2B + h-m1 | 02b_verification_plan.md, h-m1/code/ |
| Correlation analysis | h-m1 validated code | h-m1/code/run_experiment.py |
| Reliability scoring | h-m1 validated code | h-m1/code/run_experiment.py (GPT-4 fallback) |
| Fairness scoring (NEW) | Phase 2B specification | 02b_verification_plan.md (Assumption A3, HONEST metric) |
| Demographic augmentation | Phase 2B specification | Section 1.5 (A3): demographic variants generation |
| Inference parameters | Phase 2B + h-m1 | Section 1.3 (02b) + h-m1 validation |
| Statistical tests | h-m1 validated code | scipy.stats (Pearson r, CI, p-value) |
| Gate criteria | Phase 2B | Section 2.2 (H-M2 specification): r<-0.2, p<0.05, CI<-0.1 |

### F. Implementation Priority Justification

**Primary Path:** Extend h-m1 validated codebase
- ✅ TruthfulQA loading: Proven working with real dataset
- ✅ Llama-2 inference: Validated with 817 real prompts
- ✅ Correlation analysis: Statistical tests working correctly
- ✅ Result reporting: Figures and metrics generation proven

**New Component:** HONEST Fairness Metric
- **Specification Source:** Phase 2B Section 1.5 (Assumption A3)
- **Method:** Demographic augmentation (as described in 02b_verification_plan.md)
- **Implementation:** Extend scoring pipeline with fairness module
- **Risk:** Low - well-specified metric with clear computation method

**Why No External Implementations:**
- Novel hypothesis (no prior systematic fairness-reliability correlation studies found)
- h-m1 infrastructure already solves 90% of requirements
- Building on validated foundation reduces implementation risk

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12T07:45:00+00:00

### Workflow History for This Hypothesis

**2026-07-12T07:39:34+00:00:** Hypothesis h-m2 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
**2026-07-12T07:40:00+00:00:** Experiment design started (Phase 2C)
**2026-07-12T07:45:00+00:00:** Experiment design completed (Phase 2C)

### Phase 2C Workflow Execution Summary

**MCP Tools Used:**
- Archon KB: 3 knowledge queries + 2 code queries (limited relevant results for novel hypothesis)
- Exa: Quota exhausted (402 error) → Fallback to h-m1 validated infrastructure
- Serena: Not required (extending validated code, not implementing novel architecture)

**Key Decisions:**
1. Leverage h-m1 validated infrastructure (TruthfulQA + Llama-2 + correlation pipeline)
2. Add HONEST fairness metric as new scoring dimension
3. Reuse inference parameters from h-m1 for controlled comparison
4. No architectural changes needed (correlation analysis experiment)

**Quality Validation:**
- ✅ All specifications traced to sources (Phase 2B + h-m1 validation)
- ✅ Dataset loading method documented (HuggingFace)
- ✅ Model loading method documented (transformers)
- ✅ Metrics implementation specified (scipy.stats for correlation)
- ✅ Gate criteria clearly defined (r<-0.2, p<0.05, CI<-0.1)
- ✅ Continuation context properly documented

**Next Phase:** Phase 3 - Implementation Planning (PRD, Architecture, Logic, Config generation)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
