# Experiment Design: H-E1

**Date:** 2026-08-24
**Author:** PrayPrey
**Hypothesis Statement:** Different model scales (7B/70B/proprietary) exhibit statistically different FP/FN error ratios when judging code correctness
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (entry point)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (entry point)

### Gate Condition
Chi-square test for independence (scale × error_type). p < 0.05 required for MUST_WORK gate satisfaction.

---

## Continuation Context

First hypothesis in verification chain. No previous context.

### Previous Hypothesis Results (if applicable)
N/A - Entry point hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches in KB. General LLM evaluation patterns found:
- Model evaluation frameworks use FID/metrics hooks for quality assessment
- Benchmark evaluation typically uses multi-GPU distributed evaluation
- BibTeX citations show LLM.int8() quantization paper relevant for efficient 7B inference

### Archon Code Examples

- Translation evaluation hooks with interval-based metrics assessment
- Multi-GPU evaluation scripts for model quality comparison
- Benchmark evaluation patterns from mmgeneration/StyleGAN-V

### Exa GitHub Implementations

**Primary Sources Found:**

1. **evalplus/evalplus** (3.3k stars) - Rigorous LLM4Code evaluation
   - HumanEval+ (164 problems, 80x more tests than original)
   - MBPP+ (378 problems after v0.2.0 cleanup)
   - Docker-based safe execution
   - `pip install evalplus[vllm]`

2. **CodeLLM-Research/CodeJudge-Eval** (COLING25) - LLM judges for code understanding
   - Directly tests LLM-as-judge paradigm
   - MIT license, HuggingFace dataset available

3. **hongcha0/CodeJudgeBench** (ACL 2026) - Benchmarking LLM-as-a-Judge for Coding Tasks
   - Apache 2.0 license
   - Supports codegen and coderepair tasks
   - vllm backend support: `python run.py --model_name Qwen/Qwen3-8B --task codegen`

4. **ScalerLab/JudgeBench** (131 stars) - LLM-Based Judges benchmark
   - 350 GPT-4o response pairs + 270 Claude-3.5-Sonnet pairs
   - General judge evaluation (not code-specific)

5. **openai/human-eval** (3.3k stars) - Original HumanEval benchmark
   - `evaluate_functional_correctness()` for pass@k metrics
   - Sandboxed execution recommended

### Implementation Priority Assessment

**CRITICAL: For LLM judge experiments, use established benchmark infrastructure**

**Recommended Implementation Path:**
- Primary: EvalPlus (evalplus/evalplus) + CodeJudgeBench framework
- Fallback: Direct HumanEval+ problems with custom judge harness
- Justification: EvalPlus provides execution ground-truth; CodeJudgeBench provides judge evaluation patterns

### Code Analysis (Serena MCP)

*Skipped - No existing codebase to analyze. This is a new experiment.*

---

## Experiment Specification

### Dataset

**Primary Dataset: HumanEval+ (EvalPlus)**
- **Name:** HumanEval+
- **Type:** standard (programmatic-api)
- **Source:** evalplus/evalplus via HuggingFace or pip
- **Problems:** 164 coding problems
- **Test Coverage:** 80x more tests than original HumanEval
- **Ground Truth:** Execution-based pass/fail from EvalPlus test suite

**Loading Information** (for Phase 4 download):
- Method: pip + HuggingFace datasets
- Identifier: `evalplus` package + `evalplus/humanevalplus` dataset
- Code:
```python
# Install
pip install evalplus

# Load problems
from evalplus.data import get_human_eval_plus
problems = get_human_eval_plus()

# Or via HuggingFace
from datasets import load_dataset
ds = load_dataset("evalplus/humanevalplus")
```

**Sample Size:** 164 problems × multiple code solutions per model = ~1000+ judge verdicts total

### Models

#### Baseline Model

**Multi-Scale LLM Judges** (3 tiers):

| Tier | Model | Parameters | Source |
|------|-------|------------|--------|
| 7B | DeepSeek-Coder-7B-Instruct | 7B | HuggingFace |
| 70B | CodeLlama-70B-Instruct | 70B | HuggingFace |
| Proprietary | GPT-4 | Unknown | OpenAI API |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers + vllm + OpenAI API
- Identifier: `deepseek-ai/deepseek-coder-7b-instruct`, `codellama/CodeLlama-70b-Instruct-hf`, `gpt-4`
- Code:
```python
# 7B via vllm (efficient inference)
from vllm import LLM
model_7b = LLM(model="deepseek-ai/deepseek-coder-7b-instruct")

# 70B via vllm
model_70b = LLM(model="codellama/CodeLlama-70b-Instruct-hf", tensor_parallel_size=4)

# GPT-4 via API
from openai import OpenAI
client = OpenAI()
```

#### Proposed Model

**Architecture:** Multi-scale judge comparison framework

**Core Mechanism Implementation:**

```python
# Core Mechanism: Scale-Dependent Error Analysis
# Based on: CodeJudgeBench evaluation framework

class LLMJudgeEvaluator:
    """
    Evaluate LLM judges across scales, collect FP/FN error patterns.
    """
    def __init__(self, models: dict, prompt_template: str):
        self.models = models  # {"7B": model_7b, "70B": model_70b, "proprietary": gpt4_client}
        self.prompt = prompt_template
        self.results = {"7B": [], "70B": [], "proprietary": []}
    
    def judge_code(self, problem: dict, solution: str, scale: str) -> dict:
        """
        Args:
            problem: HumanEval+ problem dict
            solution: Generated code solution
            scale: "7B" | "70B" | "proprietary"
        Returns:
            {"verdict": bool, "execution_truth": bool, "error_type": "TP"|"TN"|"FP"|"FN"}
        """
        # Format prompt with problem + solution
        prompt = self.prompt.format(problem=problem["prompt"], solution=solution)
        
        # Get LLM verdict (temperature=0 for determinism)
        verdict = self._get_verdict(scale, prompt)
        
        # Get execution ground truth from EvalPlus
        execution_truth = self._run_evalplus(problem["task_id"], solution)
        
        # Classify error type
        error_type = self._classify_error(verdict, execution_truth)
        
        return {"verdict": verdict, "execution_truth": execution_truth, "error_type": error_type}
    
    def _classify_error(self, verdict: bool, truth: bool) -> str:
        if verdict and truth: return "TP"
        if not verdict and not truth: return "TN"
        if verdict and not truth: return "FP"  # False Positive
        return "FN"  # False Negative

# Integration: Run all 3 scales on same problems, collect error distributions
```

### Training Protocol

**N/A - Evaluation experiment, no training required.**

**Inference Configuration:**
- **Temperature:** 0 (deterministic)
- **Prompt:** Zero-shot code correctness judgment (pilot-selected)
- **Max tokens:** 512
- **Repetitions:** 1 per (problem, solution, scale) triple

**Seeds:** 1 (fixed - deterministic inference)

> **EXISTENCE (PoC)**: Single seed sufficient for PoC validation.

### Evaluation

**Primary Metrics:**
- Judge-Execution Agreement (accuracy)
- False Positive Rate (FPR) per scale
- False Negative Rate (FNR) per scale
- Chi-square statistic for scale × error_type independence

**Success Criteria:**
- Chi-square p < 0.05 (statistically different error patterns across scales)

**Expected Baseline Performance** (from CodeJudgeBench paper):
- Random baseline: 50% agreement
- Weak models (7B): ~60-70% agreement
- Strong models (GPT-4): ~80-85% agreement
- **Source:** CodeJudgeBench ACL 2026, CodeJudge-Eval COLING25

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (correct/incorrect judgment)
- Library: scipy.stats + sklearn.metrics
- Code:
```python
from scipy.stats import chi2_contingency
from sklearn.metrics import confusion_matrix, accuracy_score

# Build contingency table: scale × error_type
contingency = pd.crosstab(df['scale'], df['error_type'])
chi2, p_value, dof, expected = chi2_contingency(contingency)

# Per-scale metrics
for scale in ["7B", "70B", "proprietary"]:
    scale_df = df[df['scale'] == scale]
    acc = accuracy_score(scale_df['execution_truth'], scale_df['verdict'])
    cm = confusion_matrix(scale_df['execution_truth'], scale_df['verdict'])
    fpr = cm[0,1] / (cm[0,0] + cm[0,1])  # FP / (TN + FP)
    fnr = cm[1,0] / (cm[1,0] + cm[1,1])  # FN / (FN + TP)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Chi-square p-value vs 0.05 threshold bar

#### Additional Figures (LLM Autonomous)
- Stacked bar chart: Error type distribution per scale (TP/TN/FP/FN)
- Heatmap: Scale × Error Type contingency table
- Line plot: Agreement rate by scale (ordered 7B → 70B → proprietary)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Chi-square p < 0.05 (error patterns differ across scales)

---

## Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - LLM judge inference is standard capability
- **mechanism_isolatable:** True - Each scale evaluated independently
- **baseline_measurable:** True - EvalPlus provides execution ground truth

### Architecture Compatibility
- **Compatible:** All models support chat/instruct format
- **Verification:** Test prompt format on 1 problem before full run

### Activation Indicators
- **mechanism_log_message:** `"Scale {scale}: Judging problem {task_id}"`
- **tensor_shape_change:** N/A (not applicable to LLM inference)
- **metric_delta_expected:** FPR/FNR should differ by scale

### Mechanism Verification Code
```python
def verify_mechanism_active(results: pd.DataFrame) -> bool:
    """Verify that scale-dependent patterns exist."""
    # Check 1: All scales have results
    assert set(results['scale'].unique()) == {"7B", "70B", "proprietary"}
    
    # Check 2: Error types are not uniform
    for scale in results['scale'].unique():
        scale_errors = results[results['scale'] == scale]['error_type'].value_counts()
        assert len(scale_errors) >= 2, f"Scale {scale} has only one error type"
    
    # Check 3: Chi-square computable
    contingency = pd.crosstab(results['scale'], results['error_type'])
    assert contingency.shape[0] == 3 and contingency.shape[1] >= 2
    
    return True
```

### Success Threshold
- **hypothesis_support_metric:** Chi-square p-value
- **hypothesis_support_threshold:** p < 0.05

---

## Appendix: Reference Implementations

### Primary References

1. **EvalPlus** - https://github.com/evalplus/evalplus
   - Execution-based ground truth for HumanEval+
   - Docker sandboxing for safe code execution
   - Citation: Liu et al., NeurIPS 2023

2. **CodeJudgeBench** - https://github.com/hongcha0/CodeJudgeBench
   - LLM-as-judge evaluation framework
   - vllm backend support
   - Citation: Jiang et al., ACL 2026

3. **CodeJudge-Eval** - https://github.com/CodeLLM-Research/CodeJudge-Eval
   - LLM judges for code understanding
   - HuggingFace dataset available
   - Citation: COLING 2025

### Code Snippets

**EvalPlus Evaluation:**
```bash
pip install --upgrade "evalplus[vllm] @ git+https://github.com/evalplus/evalplus"
evalplus.evaluate --model "model-name" --dataset humaneval --backend vllm --greedy
```

**Chi-square Test:**
```python
from scipy.stats import chi2_contingency
chi2, p, dof, expected = chi2_contingency(contingency_table)
print(f"Chi-square: {chi2:.2f}, p-value: {p:.4f}")
```

---

## State Information

**State File:** verification_state.yaml (via ablation override)
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- Phase 2C started: 2026-08-24
- experiment_design.status: IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
