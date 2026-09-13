# Experiment Design: H-M1

**Date:** 2026-03-24
**Author:** Anonymous
**Hypothesis Statement:** RLHF instruction tuning inflates logit margins uniformly including for incorrect predictions, measurable as E[margin|incorrect]_instruct > E[margin|incorrect]_base.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests whether margin inflation affects incorrect predictions specifically

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 COMPLETED with PASS)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
- **Gate Type:** MUST_WORK
- **Pass Condition:** E[margin|incorrect]_instruct > E[margin|incorrect]_base with p < 0.05
- **Fail Action:** PIVOT to alternative mechanism

---

## Continuation Context

**Building on H-E1 Results:**

H-M1 directly extends H-E1 by analyzing the conditional margin distributions that underlie the AUROC degradation. The H-E1 results showed:
- Both Qwen and Mistral families exhibit significant AUROC degradation
- Mean margin inflation is dramatic (Mistral: correct ~8x, incorrect ~17x)
- This suggests margin inflation is non-uniform across correct/incorrect predictions

H-M1 hypothesis: The disproportionate margin inflation for incorrect predictions is the mechanism driving AUROC degradation.

### Previous Hypothesis Results (if applicable)

**H-E1 Results (Prerequisite):**
- Qwen: AUROC degradation +0.0222 (base 0.8298 vs instruct 0.8076)
- Mistral: AUROC degradation +0.0385 (base 0.7797 vs instruct 0.7413)
- **Key Insight:** Mean margins inflate for both correct and incorrect predictions, but the relative inflation for incorrect predictions appears larger (e.g., Mistral: correct margins ~8x, incorrect margins ~17x)
- **Implication:** H-M1 should find E[margin|incorrect]_instruct > E[margin|incorrect]_base

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Queries Executed:**
1. "logit margin confidence calibration LLM" (5 results)
2. "RLHF instruction tuning overconfidence" (4 results)
3. "MMLU benchmark evaluation LLM" (5 results)
4. "confidence calibration temperature scaling" (2 results)

**Key Findings:**
- Archon KB contains limited direct content on LLM confidence calibration research
- Related findings on LogitsProcessor (HuggingFace diffusers) show patterns for manipulating logit distributions
- OpenAI instruction-following documentation confirms RLHF training affects output behavior
- Temperature scaling concepts in consistency models provide calibration baselines

**Relevant Patterns:**
1. **Logit extraction:** Standard pattern via `model.generate()` with `output_scores=True` or direct forward pass
2. **Custom LogitsProcessor:** Can bias specific tokens - similar concept to margin analysis
3. **LoRA/PEFT documentation:** Shows how fine-tuning modifies model distributions

**Gap Identified:** No direct implementations of conditional margin analysis (correct vs incorrect) in Archon KB. This is a novel analysis approach.

### Archon Code Examples

**Search Queries Executed:**
1. "logit softmax margin PyTorch" (5 results)
2. "LLM inference evaluation metrics" (5 results)
3. "HuggingFace model output logits" (5 results)

**Relevant Code Patterns:**

1. **Attention weight computation (PyTorch docs):**
```python
attn_weight = query @ key.transpose(-2, -1) * scale_factor
attn_weight = torch.softmax(attn_weight, dim=-1)
```
Pattern: softmax normalization of logit-like scores

2. **Custom LogitsProcessor (HuggingFace):**
```python
class CustomLogitsProcessor(LogitsProcessor):
    def __call__(self, input_ids, scores):
        # Manipulate logits before sampling
        return scores + self.bias
```
Pattern: Logit manipulation for controlled generation

3. **Model state loading (Apple ANE):**
```python
optimized_model = DistilBertForSequenceClassification(config).eval()
optimized_model.load_state_dict(baseline_model.state_dict())
```
Pattern: Base vs fine-tuned model comparison setup

**Implementation Insight:** H-E1 codebase already contains `compute_conditional_margins()` function that computes exactly what H-M1 needs. Reuse this directly.

### Exa GitHub Implementations

**Search Queries Executed:**
1. "LLM confidence calibration logit margin RLHF GitHub PyTorch implementation"
2. "MMLU evaluation LLM inference multiple choice confidence score GitHub"
3. "permutation test conditional mean statistical analysis Python scipy"

**Highly Relevant Repositories:**

**1. ml-stat-Sustech/Disagreement-Aware-Calibration** (NeurIPS'25) ⭐6
- **URL:** https://github.com/ml-stat-Sustech/Disagreement-Aware-Calibration
- **Relevance:** Direct match - evaluates LLM calibration on MCQ tasks
- **Key Feature:** `generation/` module for collecting logits, `calibration/` for metrics
- **Structure:** Modular pipeline for MCQ calibration evaluation
- **Technologies:** vllm, torch, netcal, scikit-learn

**2. appier-research/llm-calibration** ⭐4
- **URL:** https://github.com/appier-research/llm-calibration
- **Relevance:** Response-to-capability calibration in LLMs
- **Datasets:** MMLU, GPQA, GSM8K, TruthfulQA
- **Method:** Repeated sampling to estimate expected accuracy

**3. NIKHIL0VERMA/LLM-Confidence-Calibration-Benchmark** ⭐7
- **URL:** https://github.com/NIKHIL0VERMA/LLM-Confidence-Calibration-Benchmark
- **Relevance:** Benchmarks LLM calibration across reasoning tasks
- **Features:** Reliability diagrams, confidence extraction

**4. TIGER-AI-Lab/MMLU-Pro** (NeurIPS'24) ⭐352
- **URL:** https://github.com/TIGER-AI-Lab/MMLU-Pro
- **Relevance:** Standard MMLU evaluation framework
- **Key Insight:** 10-choice format reduces random guessing

**Statistical Analysis Reference:**
- **scipy.stats.permutation_test:** Exact function for H-M1's statistical test
- **Usage:** `permutation_type='independent'` for comparing base vs instruct margin distributions
- **Documentation:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html

**Serena Analysis Needed:** No (H-E1 codebase already contains required functions)

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment for H-M1:**
- This is a novel statistical analysis, not a paper reproduction
- No external implementation exists for this specific analysis
- H-E1 codebase provides the foundational infrastructure

**Recommended Implementation Path:**
- Primary: Extend H-E1 codebase with conditional margin analysis
- Fallback: Not applicable (analysis is straightforward)
- Justification: H-E1 already computes margins and correctness; H-M1 adds statistical comparison

### Code Analysis (Serena MCP)

*Skipped* - Code from H-E1 codebase is sufficiently clear and directly reusable.

**Existing H-E1 Code Assets (Available for Reuse):**

1. **`metrics.py::compute_conditional_margins()`** - Computes exactly what H-M1 needs:
```python
def compute_conditional_margins(margins, correctness):
    correct_mask = correctness == 1
    incorrect_mask = correctness == 0
    mean_correct = np.mean(margins[correct_mask])
    mean_incorrect = np.mean(margins[incorrect_mask])
    return {"mean_correct": mean_correct, "mean_incorrect": mean_incorrect}
```

2. **`inference.py::run_model_inference()`** - Full inference pipeline with checkpointing
3. **`data.py`** - MMLU loading and preprocessing
4. **`visualize.py`** - Figure generation utilities

**No Additional Serena Analysis Required:** The H-E1 codebase provides complete infrastructure for H-M1.

---

## Experiment Specification

### Dataset

**Continuation Experiment:** Reuses H-E1 cached inference results (no additional inference needed)

| Field | Value |
|-------|-------|
| **Name** | MMLU (Massive Multitask Language Understanding) |
| **Type** | standard |
| **Source** | HuggingFace Datasets (`cais/mmlu`) |
| **Split** | test (full) |
| **Sample Count** | 14,042 samples |
| **Task Format** | Multiple-choice QA (4 options: A, B, C, D) |

**Preprocessing (from H-E1):**
- Zero-shot prompting with MCQ format
- Answer choices formatted as " A", " B", " C", " D" (space-prefixed)
- Correctness: argmax(choice_logits) == ground_truth

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `cais/mmlu`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("cais/mmlu", "all", split="test")
```

### Models

#### Baseline Models (Base vs Instruct Pairs)

**Reusing H-E1 Inference Results:**

| Family | Base Model | Instruct Model | Status |
|--------|------------|----------------|--------|
| Qwen | `Qwen/Qwen2.5-7B` | `Qwen/Qwen2.5-7B-Instruct` | Cached |
| Mistral | `mistralai/Mistral-7B-v0.1` | `mistralai/Mistral-7B-Instruct-v0.2` | Cached |
| Llama | `meta-llama/Llama-2-7b-hf` | `meta-llama/Llama-2-7b-chat-hf` | Skipped (gated) |

**Loading Information** (for Phase 4 - reuse from H-E1):
- Method: HuggingFace Transformers
- Identifier: Model IDs as listed above
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="cuda",
    trust_remote_code=True
)
```

**Key Point:** H-M1 does NOT require new model inference. It reanalyzes the cached margins/correctness arrays from H-E1.

#### Proposed Analysis

**Analysis Type:** Statistical comparison of conditional margin distributions

**Core Mechanism Under Test:**
- H-M1 tests whether RLHF instruction tuning inflates margins uniformly for incorrect predictions
- This explains WHY AUROC degrades (established in H-E1): margins become less informative about correctness

**Core Mechanism Implementation (Analysis Pipeline):**

```python
# Core Analysis: Conditional Margin Comparison
# Based on: H-E1 metrics.py::compute_conditional_margins()
# Purpose: Test E[margin|incorrect]_instruct > E[margin|incorrect]_base

import numpy as np
from scipy import stats

def analyze_conditional_margins(
    base_margins: np.ndarray,      # (N,) margins from base model
    base_correct: np.ndarray,      # (N,) correctness labels for base
    inst_margins: np.ndarray,      # (N,) margins from instruct model
    inst_correct: np.ndarray,      # (N,) correctness labels for instruct
) -> dict:
    """
    Compare E[margin|incorrect] between base and instruct models.

    Returns:
        Dict with mean_base_incorrect, mean_inst_incorrect,
        ratio, t_statistic, p_value
    """
    # Extract incorrect predictions only
    base_incorrect_mask = base_correct == 0
    inst_incorrect_mask = inst_correct == 0

    margins_base_incorrect = base_margins[base_incorrect_mask]
    margins_inst_incorrect = inst_margins[inst_incorrect_mask]

    # Compute conditional means
    mean_base = np.mean(margins_base_incorrect)
    mean_inst = np.mean(margins_inst_incorrect)

    # Permutation test (or t-test for large samples)
    result = stats.permutation_test(
        (margins_inst_incorrect, margins_base_incorrect),
        statistic=lambda x, y: np.mean(x) - np.mean(y),
        permutation_type='independent',
        alternative='greater',
        n_resamples=9999
    )

    return {
        "mean_base_incorrect": mean_base,
        "mean_inst_incorrect": mean_inst,
        "inflation_ratio": mean_inst / mean_base if mean_base > 0 else np.inf,
        "p_value": result.pvalue,
        "gate_pass": result.pvalue < 0.05 and mean_inst > mean_base
    }
```

### Training Protocol

**Not Applicable** - H-M1 is a statistical analysis hypothesis, not a training experiment.

**Analysis Protocol:**
1. Load cached inference results from H-E1 (margins, correctness arrays)
2. Partition samples into correct vs incorrect predictions
3. Compute conditional margin distributions
4. Run statistical comparison (permutation test)
5. Generate visualizations

**No Training Required:** H-M1 reuses H-E1 inference results.

### Evaluation

**Primary Metric:** E[margin|incorrect] comparison

**Gate Condition (MUST_WORK):**
- E[margin|incorrect]_instruct > E[margin|incorrect]_base
- p-value < 0.05 (one-tailed permutation test)

**Success Criteria:**
1. Direction: mean_inst_incorrect > mean_base_incorrect (both families)
2. Statistical significance: p < 0.05 for each family
3. Effect consistency: Both Qwen and Mistral show same direction

**Expected Baseline Performance (from H-E1 data):**
- H-E1 showed dramatic margin inflation in instruct models
- Qwen: correct margins ~2x, Mistral: correct margins ~8x
- Hypothesis predicts disproportionate inflation for incorrect predictions

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (no model training)
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import permutation_test
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: E[margin|incorrect] base vs instruct bar chart per family

#### Additional Figures (LLM Autonomous)

1. **Margin Distribution KDE Plots**: Kernel density estimates of margin distributions, split by correctness (4 subplots: base-correct, base-incorrect, inst-correct, inst-incorrect)
2. **Box Plots**: Box plots comparing margin distributions across conditions
3. **Inflation Ratio Chart**: Ratio of instruct/base margins for correct vs incorrect predictions
4. **Forest Plot**: Effect sizes with 95% CIs across families

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. E[margin|incorrect]_instruct > E[margin|incorrect]_base for tested families
3. Statistical significance: p < 0.05

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: Logit/Softmax Calibration Patterns
- **Type**: Knowledge base technical documentation
- **Query Used**: "logit margin confidence calibration LLM"
- **Relevance**: Established patterns for logit manipulation and softmax normalization
- **Key Insights**:
  - Custom LogitsProcessor can bias token selection via score manipulation
  - Standard attention weight pattern uses softmax normalization
- **Used For**: Understanding logit extraction patterns

**Source A.2**: RLHF/Instruction Tuning Effects
- **Type**: Knowledge base article
- **Query Used**: "RLHF instruction tuning overconfidence"
- **Relevance**: Background on how RLHF affects model outputs
- **Key Insights**:
  - Instruction-following behavior is trained via preference optimization
  - LoRA/PEFT modifies model distributions in targeted ways
- **Used For**: Theoretical grounding for margin inflation hypothesis

### B. GitHub Implementations (Exa)

**Repository B.1**: ml-stat-Sustech/Disagreement-Aware-Calibration (⭐6)
- **URL**: https://github.com/ml-stat-Sustech/Disagreement-Aware-Calibration
- **Query Used**: "LLM confidence calibration logit margin RLHF GitHub"
- **Relevance**: Direct precedent for LLM calibration evaluation on MCQ
- **Structure**:
  - `generation/` - logit collection
  - `calibration/` - metrics computation
  - `common/` - utilities
- **Used For**: Validation of experimental approach

**Repository B.2**: appier-research/llm-calibration (⭐4)
- **URL**: https://github.com/appier-research/llm-calibration
- **Query Used**: Same as above
- **Relevance**: Response-to-capability calibration methodology
- **Used For**: Complementary perspective on calibration metrics

**Repository B.3**: TIGER-AI-Lab/MMLU-Pro (⭐352)
- **URL**: https://github.com/TIGER-AI-Lab/MMLU-Pro
- **Query Used**: "MMLU evaluation LLM inference"
- **Relevance**: Standard MMLU evaluation framework
- **Used For**: Dataset loading and evaluation patterns

**Statistical Reference**: scipy.stats.permutation_test
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- **Query Used**: "permutation test conditional mean statistical analysis Python scipy"
- **Relevance**: Exact statistical method for H-M1 gate evaluation
- **Used For**: Statistical analysis implementation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - H-E1 codebase was sufficiently clear and directly reusable.

**H-E1 Codebase Reference**:
- **Path**: `h-e1/code/`
- **Key Files**:
  - `metrics.py`: `compute_conditional_margins()` - exact function needed
  - `inference.py`: Model loading and margin extraction
  - `data.py`: MMLU dataset loading
- **Used For**: Direct code reuse for H-M1 implementation

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-E1
- **File**: `h-e1/04_validation.md`
- **Reused Components**:
  - Cached inference results (margins, correctness arrays)
  - Model loading infrastructure
  - Visualization utilities
- **Why Reused**: H-M1 is a continuation analysis that reanalyzes H-E1 data

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous Hypothesis | H-E1 (MMLU cached) |
| Model selection | Previous Hypothesis | H-E1 (same base/instruct pairs) |
| Conditional margin computation | H-E1 Code | metrics.py |
| Statistical test method | Documentation | scipy.stats.permutation_test |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md Section 2.2 |
| Gate criteria | Phase 2B | H-M1 specification |
| Visualization patterns | GitHub | B.1, B.2 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-24

### Workflow History for This Hypothesis
- 2026-03-24: Hypothesis h-m1 set to IN_PROGRESS (Phase 2C experiment design started)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
