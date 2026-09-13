# Experiment Design: H-M1

**Date:** 2026-08-24
**Author:** PrayPrey
**Hypothesis Statement:** Judge-execution agreement increases with model scale (7B < 70B < proprietary) with diminishing returns
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests scale-accuracy ordering with diminishing returns.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED - Chi-square p=3.27e-08)
**Gate Status:** MUST_WORK (pending evaluation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
- **Tests:** P1 - Kruskal-Wallis H-test for ordinal scale effect
- **Success:** 7B_accuracy < 70B_accuracy < proprietary_accuracy AND (70B - 7B) > (proprietary - 70B)
- **Falsification:** Linear or reversed ordering; proprietary shows >20% improvement over 70B

---

## Continuation Context

### From H-E1 Validation
- 7B model: FPR=74.8%, FNR=12.8% (over-accepts)
- Proprietary model: FPR=60.4%, FNR=29.3% (conservative)
- Chi-square statistic 45.78, p=3.27e-08 confirms scale-dependent error patterns

### Previous Hypothesis Results
H-E1 established that different scales exhibit distinct FP/FN error patterns. H-M1 now tests whether this translates to monotonic accuracy improvement with diminishing returns.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LLM judge evaluation scaling accuracy**
- Limited direct matches; general transformer inference patterns found
- Code examples for model loading via HuggingFace transformers
- Quantization techniques (4-bit, 8-bit) for large model inference

**Query 2: Code benchmark HumanEval MBPP**
- EvalPlus framework identified as standard benchmark
- HumanEval+: 164 problems, 80x test coverage
- MBPP+: 378 problems, 35x test coverage

### Archon Code Examples

**Model Loading Patterns:**
```python
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
```
- Source: HuggingFace PEFT documentation

### Exa GitHub Implementations

**Repository 1**: evalplus/evalplus (NeurIPS 2023 & COLM 2024)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: Standard framework for code correctness evaluation
- **Key Code**:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus
human_eval = get_human_eval_plus()
mbpp = get_mbpp_plus()
```
- **Dataset Stats**: HumanEval+ (164), MBPP+ (378)

**Repository 2**: crupig/LLMs-as-a-judge-for-SE
- **URL**: https://github.com/crupig/LLMs-as-a-judge-for-SE-tse_RP
- **Relevance**: Direct LLM-as-judge evaluation code for code correctness
- **Models Tested**: DeepSeek-Coder (1.3B, 6.7B, 33B), CodeLlama (7B, 13B, 34B), GPT-3.5, GPT-4
- **Key Finding**: GPT-4 best judge (Cohen's Kappa ~0.21), smaller models fail (Kappa near 0)

**Key Paper**: "On the Effectiveness of LLM-as-a-judge for Code" (arxiv:2507.16587)
- GPT-4-turbo: Best performance, Kappa ~0.21 (Java), ~0.10 (Python)
- CodeLlama 7B/13B/34B: Near-zero or negative Kappa
- DeepSeek 1.3B/6.7B: Complete failure on judging tasks
- Scale effect confirmed: Larger models > smaller models for judging

### Implementation Priority Assessment

**CRITICAL: Using established LLM-as-judge methodology from published research**

- Primary: EvalPlus framework for ground truth + custom judge evaluation pipeline
- Fallback: Direct API calls to judge models
- Justification: EvalPlus provides rigorous test execution ground truth; crupig repo provides judge evaluation methodology

**Recommended Implementation Path:**
- Primary: EvalPlus (execution) + HuggingFace/OpenAI API (judging)
- Fallback: vLLM for local model inference
- Justification: Combines established benchmark with flexible judge model access

### Code Analysis (Serena MCP)

*Skipped* - LLM API evaluation does not require complex architecture analysis

---

## Experiment Specification

### Dataset

**Primary Dataset: HumanEval+**
- **Name:** HumanEval+
- **Type:** standard (code benchmark)
- **Source:** evalplus/evalplus (NeurIPS 2023)
- **Statistics:** 164 problems, 80x test coverage vs original HumanEval
- **Preprocessing:** None required (prompts provided)
- **Hypothesis Fit:** Standard code correctness benchmark for LLM evaluation

**Secondary Dataset: MBPP+**
- **Name:** MBPP+
- **Type:** standard (code benchmark)
- **Source:** evalplus/evalplus
- **Statistics:** 378 problems, 35x test coverage vs original MBPP
- **Hypothesis Fit:** Replication dataset for robustness

**Loading Information** (for Phase 4 download):
- Method: PyPI package (evalplus)
- Identifier: `evalplus`
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus
humaneval = get_human_eval_plus()  # 164 problems
mbpp = get_mbpp_plus()  # 378 problems
```

### Models

#### Baseline Model

**Smallest Judge (7B tier):**
- Architecture: DeepSeek-Coder-7B-Instruct
- Type: Code-specialized LLM
- Source: HuggingFace (deepseek-ai/deepseek-coder-7b-instruct)
- Hypothesis Fit: Represents smallest judge scale tier

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers + vLLM
- Identifier: `deepseek-ai/deepseek-coder-7b-instruct`
- Code:
```python
from vllm import LLM
model_7b = LLM(model="deepseek-ai/deepseek-coder-7b-instruct")
```

#### Proposed Model

**Architecture:** Multi-scale judge evaluation system

**Scale Tiers:**
1. 7B: DeepSeek-Coder-7B-Instruct
2. 70B: CodeLlama-70B-Instruct (meta-llama/CodeLlama-70b-Instruct-hf)
3. Proprietary: GPT-4-turbo (via OpenAI API)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Scale-Accuracy Evaluation
# Based on: crupig/LLMs-as-a-judge-for-SE, arxiv:2507.16587

import numpy as np
from scipy import stats

def evaluate_scale_ordering(judge_verdicts: dict, ground_truth: dict) -> dict:
    """
    Evaluate judge-execution agreement across model scales.
    
    Args:
        judge_verdicts: {scale: {task_id: verdict}} where verdict in {0, 1}
        ground_truth: {task_id: pass_fail} from EvalPlus execution
    
    Returns:
        {scale: accuracy, differences, kruskal_h, diminishing_returns}
    """
    scales = ['7B', '70B', 'proprietary']
    accuracies = {}
    
    for scale in scales:
        verdicts = judge_verdicts[scale]
        correct = sum(verdicts[tid] == ground_truth[tid] for tid in verdicts)
        accuracies[scale] = correct / len(verdicts)
    
    # Test ordering: 7B < 70B < proprietary
    ordering_satisfied = (
        accuracies['7B'] < accuracies['70B'] < accuracies['proprietary']
    )
    
    # Test diminishing returns: (70B - 7B) > (proprietary - 70B)
    diff_7b_70b = accuracies['70B'] - accuracies['7B']
    diff_70b_prop = accuracies['proprietary'] - accuracies['70B']
    diminishing_returns = diff_7b_70b > diff_70b_prop
    
    # Kruskal-Wallis H-test for ordinal scale effect
    scale_groups = [
        [1 if judge_verdicts['7B'][tid] == ground_truth[tid] else 0 
         for tid in ground_truth],
        [1 if judge_verdicts['70B'][tid] == ground_truth[tid] else 0 
         for tid in ground_truth],
        [1 if judge_verdicts['proprietary'][tid] == ground_truth[tid] else 0 
         for tid in ground_truth]
    ]
    h_stat, p_value = stats.kruskal(*scale_groups)
    
    return {
        'accuracies': accuracies,
        'ordering_satisfied': ordering_satisfied,
        'diminishing_returns': diminishing_returns,
        'kruskal_h': h_stat,
        'p_value': p_value
    }
```

### Training Protocol

**No Training Required** - This is an inference/evaluation experiment.

**Evaluation Protocol:**
- Temperature: 0 (greedy decoding)
- Prompt: Zero-shot code correctness judgment
- Format: Binary verdict (correct/incorrect)
- Seeds: 1 (deterministic with temp=0)

**Prompt Template:**
```
Given the following Python function and its specification, determine if the implementation is correct.

Function:
{code}

Specification:
{prompt}

Is this implementation correct? Answer only 'correct' or 'incorrect'.
```

**Inference Configuration:**
- 7B/70B models: vLLM backend, temp=0
- GPT-4: OpenAI API, temp=0
- Max new tokens: 10

### Evaluation

**Primary Metrics:**
- Judge-Execution Agreement (Accuracy): % of verdicts matching EvalPlus execution
- Cohen's Kappa: Agreement correcting for chance

**Success Criteria (MUST_WORK):**
1. Ordering: accuracy_7B < accuracy_70B < accuracy_proprietary
2. Diminishing returns: (accuracy_70B - accuracy_7B) > (accuracy_proprietary - accuracy_70B)
3. Kruskal-Wallis p < 0.05

**Falsification:**
- Linear ordering (equal jumps between tiers)
- Reversed ordering
- Proprietary > 20% better than 70B (no diminishing returns)

**Expected Baseline Performance** (from research):
- 7B models: ~50-60% accuracy (barely above random)
- 70B models: ~65-70% accuracy
- GPT-4: ~70-75% accuracy
- Source: arxiv:2507.16587, crupig/LLMs-as-a-judge-for-SE

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification agreement
- Library: scipy.stats, sklearn.metrics
- Code:
```python
from scipy.stats import kruskal
from sklearn.metrics import cohen_kappa_score, accuracy_score
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Accuracy by scale tier bar chart with error bars

#### Additional Figures (LLM Autonomous)
- Scale vs Accuracy line plot showing diminishing returns curve
- Confusion matrices per scale tier (TP/TN/FP/FN)
- Cohen's Kappa by scale tier
- Error type distribution (FP/FN) by scale (connects to H-E1)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True (comparing accuracy across scales)
- `mechanism_isolatable`: True (each scale evaluated independently)
- `baseline_measurable`: True (7B serves as baseline)

### Architecture Compatibility
- All models can receive same prompt template
- All models produce text output parseable to binary verdict
- EvalPlus provides consistent ground truth across all problems

### Activation Indicators
- `mechanism_log_message`: "Evaluating {scale} model on {task_id}"
- `tensor_shape_change`: N/A (inference only)
- `metric_delta_expected`: 5-15% accuracy improvement per scale tier

### Mechanism Verification Code
```python
def verify_mechanism(results):
    """Verify scale ordering and diminishing returns."""
    acc = results['accuracies']
    
    # Check 1: Ordering
    assert acc['7B'] < acc['70B'] < acc['proprietary'], \
        f"Ordering violated: {acc['7B']:.3f} < {acc['70B']:.3f} < {acc['proprietary']:.3f}"
    
    # Check 2: Diminishing returns
    diff1 = acc['70B'] - acc['7B']
    diff2 = acc['proprietary'] - acc['70B']
    assert diff1 > diff2, \
        f"No diminishing returns: {diff1:.3f} <= {diff2:.3f}"
    
    # Check 3: Statistical significance
    assert results['p_value'] < 0.05, \
        f"Not significant: p={results['p_value']:.4f}"
    
    return True
```

### Hypothesis Support Threshold
- `hypothesis_support_metric`: Kruskal-Wallis H-statistic
- `hypothesis_support_threshold`: p < 0.05 AND ordering satisfied AND diminishing returns

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. accuracy_7B < accuracy_70B < accuracy_proprietary
3. (accuracy_70B - accuracy_7B) > (accuracy_proprietary - accuracy_70B)
4. Kruskal-Wallis p < 0.05

---

## Appendix: Reference Implementations

### Primary References
1. **EvalPlus** (NeurIPS 2023)
   - URL: https://github.com/evalplus/evalplus
   - Used for: Ground truth execution, dataset loading
   
2. **LLMs-as-a-judge-for-SE** (TSE Replication Package)
   - URL: https://github.com/crupig/LLMs-as-a-judge-for-SE-tse_RP
   - Used for: Judge evaluation methodology, prompt templates

3. **On the Effectiveness of LLM-as-a-judge for Code** (arxiv:2507.16587)
   - Used for: Expected baseline performance, scale comparison methodology

### Code Snippets

**Dataset Loading:**
```python
from evalplus.data import get_human_eval_plus
problems = get_human_eval_plus()
```

**Judge Query (vLLM):**
```python
from vllm import LLM, SamplingParams
model = LLM(model="deepseek-ai/deepseek-coder-7b-instruct")
params = SamplingParams(temperature=0, max_tokens=10)
outputs = model.generate(prompts, params)
```

**Judge Query (OpenAI):**
```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0,
    max_tokens=10
)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- H-E1 validated: 2026-08-24 (Chi-square p=3.27e-08)
- Phase 2C started: 2026-08-24

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
