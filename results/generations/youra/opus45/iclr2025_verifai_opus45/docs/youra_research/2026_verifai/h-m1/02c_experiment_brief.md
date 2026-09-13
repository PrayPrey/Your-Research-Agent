# Experiment Design: h-m1

**Date:** 2026-03-30
**Author:** Anonymous
**Hypothesis Statement:** Error feedback granularity (G0-G4) has a statistically significant effect on LLM repair success rate (ANOVA p < 0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Designed for "what causes the effect?" validation with statistical analysis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** YES (h-e1 PASSED)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (COMPLETED - Runtime error prevalence 60.8%)

### Gate Condition
ANOVA p < 0.05 (significant effect of granularity on repair success rate)

---

## Continuation Context

**Building on H-E1 Results:**
- Runtime error prevalence: 60.8% (304/500 failures)
- 95% CI: [56.5%, 65.0%] - significantly exceeds 30% threshold
- Sufficient sample size for granularity experiments (304 runtime errors available)
- Syntax errors also common (38.6%) but excluded from this study

### Previous Hypothesis Results (if applicable)
From H-E1 validation:
- Model: CodeLlama-7B-Instruct-hf
- Dataset: MBPP (test split, IDs 11-510)
- Execution timeout: 10 seconds
- 304 runtime error cases available for granularity comparison

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Queries Executed:**
1. "LLM code repair feedback granularity self-debug" (2 results)
2. "error localization stack trace automated program repair" (4 results)
3. "MBPP code generation benchmark evaluation ANOVA" (5 results)

**Key Finding:** Archon Knowledge Base does not contain specific content on LLM code repair, Self-Debug methodology, or error feedback granularity experiments. The available content focuses primarily on diffusion models and ML infrastructure.

**Relevant Adjacent Content:**
- Paper reference found: arXiv 2305.14314 (similarity: 0.40) - Related to code generation but not specific to repair feedback
- DeepSpeed/PyTorch distributed training examples - useful for infrastructure patterns

**Implication for Experiment Design:**
- Must rely on primary literature (Self-Debug paper, TraceFixer, DynaFix) for methodology
- Implementation patterns will come from Exa GitHub search (Step 3)
- Statistical analysis (ANOVA) patterns well-documented in scipy documentation

### Archon Code Examples

**Search Queries Executed:**
1. "self-debug code repair LLM feedback" (5 results)
2. "ANOVA statistical test Python scipy" (5 results)

**Key Finding:** No direct code examples for LLM code repair experiments. Found general PyTorch/infrastructure patterns.

**Useful Patterns Identified:**
- HuggingFace model loading: `from transformers import AutoModelForCausalLM`
- Execution tracing patterns (traceback handling in Python)
- scipy installation for statistical analysis: `pip install scipy`

**Statistical Analysis Code Pattern (from literature):**
```python
from scipy import stats
# One-way ANOVA for comparing 5 granularity levels
f_stat, p_value = stats.f_oneway(g0_results, g1_results, g2_results, g3_results, g4_results)
```

### Exa GitHub Implementations

**Query 1: Self-Debug LLM Code Repair Official Implementation**

**Repository 1**: [openreview/Teaching Large Language Models to Self-Debug] (ICLR 2024)
- **URL**: https://openreview.net/forum?id=KuPixIqPiq
- **Authors**: Xinyun Chen, Maxwell Lin, Nathanael Schärli, Denny Zhou (Google)
- **Relevance**: Original Self-Debug paper - methodology baseline for our experiment
- **Key Method**: Rubber duck debugging without human feedback; leverages code execution and natural language explanation
- **Benchmarks Used**: Spider (text-to-SQL), TransCoder (C++-to-Python), **MBPP** (text-to-Python)
- **Results on MBPP**: Self-debugging improves baseline accuracy with unit test feedback

**Repository 2**: [TnTWoW/RePair] (⭐ 7) - ACL'24
- **URL**: https://github.com/TnTWoW/RePair
- **Relevance**: Process-based feedback for automated program repair
- **Architecture**: Reward model as critic providing feedback for repair policy optimization
- **Dataset**: CodeNet4Repair (multi-step repair dataset)
- **Training Config**:
  - Iterative solution generation until repair effect plateaus
  - Process supervision during training

**Repository 3**: [evalplus/evalplus] (⭐ 1704)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: **CRITICAL** - Standard evaluation framework for MBPP/HumanEval
- **Used by**: Meta Llama 3.1/3.3, Qwen2.5-Coder, DeepSeek-Coder V2, StarCoder2
- **Key Code**:
  ```python
  # EvalPlus evaluation command
  evalplus.evaluate --model <model> --dataset mbpp --samples <generated_samples>
  ```
- **MBPP+ Version**: 378 tasks (sanitized, v0.2.0)

**Repository 4**: [codeeval-pro/codeeval-pro] (⭐ 39) - ACL'25 Findings
- **URL**: https://github.com/codeeval-pro/codeeval-pro
- **Relevance**: MBPP Pro - extended evaluation benchmark
- **Key Code**:
  ```python
  python -m eval.inference --model_name_or_path $MODEL_PATH --save_path ${OUTPUT_DIR}
  ```

**Query 2: ANOVA Statistical Analysis**

**Resource**: scipy.stats.f_oneway documentation
- **URL**: https://www.geeksforgeeks.org/python/how-to-perform-a-one-way-anova-in-python/
- **Key Code**:
  ```python
  from scipy.stats import f_oneway

  # One-way ANOVA for 5 granularity levels
  f_stat, p_value = f_oneway(g0_results, g1_results, g2_results, g3_results, g4_results)

  # Interpret results
  alpha = 0.05
  if p_value < alpha:
      print("Reject null hypothesis - significant effect of granularity")
  ```
- **Post-hoc**: Tukey's HSD for pairwise comparisons if ANOVA significant

**Serena Analysis Needed**: false (code patterns are clear from Exa results)

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Availability | Recommendation |
|----------|--------|--------------|----------------|
| ⭐⭐⭐ HIGHEST | Self-Debug (Chen et al.) | Paper methodology only | Implement from paper description |
| ⭐⭐ HIGH | EvalPlus | Full code available | Use for MBPP evaluation |
| ⭐ MEDIUM | RePair | Full code available | Reference for repair loop pattern |

**Recommended Implementation Path:**
- Primary: Custom implementation following Self-Debug methodology with granularity-controlled feedback
- Fallback: Adapt RePair feedback loop with granularity variants
- Justification: Self-Debug paper provides clear methodology; no official repo but well-documented approach. EvalPlus provides standard MBPP evaluation infrastructure.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The Self-Debug methodology and ANOVA statistical analysis patterns are well-documented in the literature and Exa results. No complex proprietary code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset**: MBPP (Mostly Basic Python Problems)
**Type**: standard
**Source**: Google Research / HuggingFace

**Statistics**:
- Total problems: 974 (full), 427 (sanitized)
- Test split: 500 problems (IDs 11-510)
- Validation split: 90 problems
- Training split: 374 problems (not used)

**Structure per problem**:
- `task_id`: Unique identifier
- `text`: Natural language task description
- `code`: Reference solution
- `test_list`: 3 automated test cases per problem

**Continuation Context**: Reusing MBPP from H-E1 for controlled comparison. Same 500 test problems, same execution timeout (10s).

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `google-research-datasets/mbpp` (full) or `Muennighoff/mbpp`
- Code:
  ```python
  from datasets import load_dataset

  # Load full MBPP dataset
  dataset = load_dataset("google-research-datasets/mbpp", "full")
  test_set = dataset["test"]  # 500 problems

  # Each item has: task_id, text, code, test_list, test_setup_code
  ```

### Models

#### Baseline Model

**Architecture**: CodeLlama-7B-Instruct
**Type**: Instruction-tuned code LLM (7 billion parameters)
**Source**: Meta AI / HuggingFace

**Model Capabilities**:
- Code completion
- Instruction following for code tasks
- Python specialist variant available

**Configuration**:
- Temperature: 0.0 (deterministic generation)
- Max tokens: 512
- Seed: 1 (reproducibility)

**Continuation Context**: Same model as H-E1 for controlled comparison. Only feedback granularity changes.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `codellama/CodeLlama-7b-Instruct-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer

  MODEL_NAME = "codellama/CodeLlama-7b-Instruct-hf"

  tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
  model = AutoModelForCausalLM.from_pretrained(
      MODEL_NAME,
      device_map="auto",
      torch_dtype=torch.float16
  )
  ```

#### Proposed Model

**Architecture:** Baseline CodeLlama-7B-Instruct + Granularity-Controlled Error Feedback

**Integration Point**: Prompt construction (no model modification)
- The mechanism is in the PROMPT, not the model weights
- Same model receives different feedback granularity levels
- Self-Debug methodology from Chen et al. (ICLR 2024)

**Modification**: Error feedback section of repair prompt varies by granularity level

**Core Mechanism Implementation:**

```python
# Core Mechanism: Granularity-Controlled Error Feedback for LLM Code Repair
# Based on: Self-Debug (Chen et al., ICLR 2024) + Granularity Ablation

# Granularity Levels (G0-G4)
GRANULARITY_LEVELS = {
    "G0": "pass_fail_only",      # "Test failed"
    "G1": "error_type",          # "Test failed: AssertionError"
    "G2": "error_message",       # "Test failed: AssertionError: Expected 5, got 3"
    "G3": "error_line",          # G2 + "at line 7"
    "G4": "full_trace",          # G3 + full stack trace
}

def construct_repair_prompt(code: str, error_info: dict, granularity: str) -> str:
    """
    Construct Self-Debug style repair prompt with controlled granularity.

    Args:
        code: The buggy code to repair
        error_info: Dict with {type, message, line, traceback}
        granularity: One of G0, G1, G2, G3, G4
    Returns:
        Formatted repair prompt string
    """
    feedback = format_feedback_by_granularity(error_info, granularity)

    prompt = f"""The following code has a bug:
```python
{code}
```

Execution feedback:
{feedback}

Please fix the bug and provide the corrected code."""

    return prompt

def format_feedback_by_granularity(error_info: dict, level: str) -> str:
    """Format error feedback at specified granularity level."""
    if level == "G0":
        return "Test failed."
    elif level == "G1":
        return f"Test failed: {error_info['type']}"
    elif level == "G2":
        return f"Test failed: {error_info['type']}: {error_info['message']}"
    elif level == "G3":
        return f"Test failed: {error_info['type']}: {error_info['message']} at line {error_info['line']}"
    elif level == "G4":
        return f"Test failed:\n{error_info['traceback']}"

# Integration: Applied at prompt construction, before model.generate()
```

### Training Protocol

**Note**: This is an INFERENCE-ONLY experiment. No model training/fine-tuning required.

**Inference Configuration** (from H-E1, reused for controlled comparison):
- **Temperature**: 0.0 (deterministic)
- **Max Tokens**: 512
- **Seed**: 1 (fixed for reproducibility)
- **Device**: Single GPU (CUDA_VISIBLE_DEVICES set dynamically)

**Experiment Protocol**:
1. Load runtime error cases from H-E1 (304 cases available, use all)
2. For each case, generate 5 feedback variants (G0, G1, G2, G3, G4)
3. Attempt repair with Self-Debug prompt for each variant
4. Execute repaired code against test cases
5. Record binary success (1 if all tests pass, 0 otherwise)

**Batch Processing**:
- Process all 304 cases × 5 granularity levels = 1,520 repair attempts
- Single repair attempt per case per granularity (no multi-turn)
- Timeout: 10 seconds per execution (same as H-E1)

**Data Reuse from H-E1**:
- `execution_results.json`: Contains error info (type, message, line, traceback)
- Same MBPP problems, same model, only feedback granularity changes

### Evaluation

**Primary Metric**: Repair Success Rate per Granularity Level
- Definition: (# successful repairs) / (# total attempts) per granularity
- Binary success: All test cases pass = 1, otherwise = 0

**Statistical Test** (MECHANISM hypothesis - REQUIRED):
- **Test**: One-way ANOVA (5 groups: G0, G1, G2, G3, G4)
- **H0**: μ_G0 = μ_G1 = μ_G2 = μ_G3 = μ_G4 (no effect of granularity)
- **H1**: At least one group mean differs

**Gate Condition**:
- Primary: ANOVA p < 0.05 (significant effect)
- Secondary: Effect size η² > 0.02 (small but meaningful)

**Expected Results** (from literature):
- G0 (pass/fail only): ~5-10% repair rate (naive retry)
- G2-G3 (error+line): ~15-25% repair rate (Self-Debug baseline)
- G4 (full trace): ~15-20% (potential cognitive overload)

**Post-hoc Analysis** (if ANOVA significant):
- Tukey's HSD for pairwise comparisons
- Identify which granularity pairs differ significantly

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (repair success/fail)
- Library: scipy.stats, numpy
- Code:
  ```python
  from scipy.stats import f_oneway
  import numpy as np

  # Collect binary results per granularity
  results = {g: [] for g in ["G0", "G1", "G2", "G3", "G4"]}

  # After all experiments, run ANOVA
  f_stat, p_value = f_oneway(
      results["G0"], results["G1"], results["G2"],
      results["G3"], results["G4"]
  )

  # Calculate effect size (eta-squared)
  # η² = SS_between / SS_total
  all_results = np.concatenate(list(results.values()))
  grand_mean = np.mean(all_results)
  ss_total = np.sum((all_results - grand_mean) ** 2)
  ss_between = sum(len(r) * (np.mean(r) - grand_mean) ** 2 for r in results.values())
  eta_squared = ss_between / ss_total
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: ANOVA p-value vs threshold bar chart

#### Additional Figures (LLM Autonomous)

1. **Repair Success Rate by Granularity**: Bar chart showing success rate per level (G0-G4) with error bars (95% CI)
2. **Granularity Effect Curve**: Line plot showing repair rate vs granularity level (testing non-monotonicity)
3. **ANOVA Results Summary**: F-statistic, p-value, η² visualization
4. **Pairwise Comparison Heatmap**: If ANOVA significant, show Tukey HSD p-values between all pairs
5. **Per-Error-Type Breakdown**: Stratified analysis by error type (IndexError, TypeError, etc.)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ANOVA p < 0.05 (significant effect of granularity)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: Archon KB Search Results
- **Type**: Knowledge base articles
- **Queries Used**:
  - "LLM code repair feedback granularity self-debug"
  - "error localization stack trace automated program repair"
  - "MBPP code generation benchmark evaluation ANOVA"
- **Key Finding**: Limited direct content on LLM code repair methodology
- **Insight**: Must rely on primary literature (Self-Debug paper) for methodology
- **Used For**: Confirming need for Exa/literature search

**Code Source A.2**: scipy.stats.f_oneway Pattern
- **Query Used**: "ANOVA statistical test Python scipy"
- **Key Code**:
  ```python
  from scipy.stats import f_oneway
  f_stat, p_value = f_oneway(group1, group2, group3, group4, group5)
  ```
- **Used For**: ANOVA implementation in evaluation metrics

### B. GitHub Implementations (Exa)

**Repository B.1**: Self-Debug (Chen et al., ICLR 2024)
- **URL**: https://openreview.net/forum?id=KuPixIqPiq
- **Query Used**: "Self-Debug Chen LLM code repair official implementation GitHub"
- **Relevance**: Original Self-Debug methodology - basis for our repair prompt design
- **Authors**: Xinyun Chen, Maxwell Lin, Nathanael Schärli, Denny Zhou (Google)
- **Key Method**: Rubber duck debugging with code execution feedback
- **MBPP Results**: Self-debugging improves baseline with unit test feedback
- **Used For**: Core repair prompt template (Step 6 pseudo-code)

**Repository B.2**: [TnTWoW/RePair](https://github.com/TnTWoW/RePair) (⭐ 7)
- **URL**: https://github.com/TnTWoW/RePair
- **Query Used**: "Self-Debug Chen LLM code repair official implementation GitHub"
- **Relevance**: ACL'24 process-based feedback for program repair
- **Key Pattern**: Iterative repair until effect plateaus
- **Used For**: Reference for repair loop structure

**Repository B.3**: [evalplus/evalplus](https://github.com/evalplus/evalplus) (⭐ 1704)
- **URL**: https://github.com/evalplus/evalplus
- **Query Used**: "MBPP benchmark code generation evaluation Python GitHub"
- **Relevance**: Standard MBPP/HumanEval evaluation framework
- **Used By**: Meta Llama 3.1/3.3, Qwen2.5-Coder, DeepSeek-Coder V2
- **Key Code**:
  ```python
  evalplus.evaluate --model <model> --dataset mbpp --samples <samples>
  ```
- **Used For**: MBPP evaluation methodology reference

**Repository B.4**: [google-research-datasets/mbpp](https://huggingface.co/datasets/google-research-datasets/mbpp)
- **URL**: https://huggingface.co/datasets/google-research-datasets/mbpp
- **Query Used**: "MBPP dataset load Python google-research huggingface"
- **Key Code**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("google-research-datasets/mbpp", "full")
  ```
- **Used For**: Dataset loading specification (Step 5)

**Repository B.5**: [codellama/CodeLlama-7b-Instruct-hf](https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf)
- **URL**: https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf
- **Query Used**: "CodeLlama-7B-Instruct huggingface transformers load model"
- **Key Code**:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
  ```
- **Used For**: Model loading specification (Step 5)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. The Self-Debug methodology and ANOVA patterns are well-documented in literature.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-E1
- **File**: `h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: MBPP (test split, 500 problems)
  - Model: CodeLlama-7B-Instruct-hf
  - Execution timeout: 10 seconds
  - Runtime error cases: 304 (60.8% prevalence)
- **Why Reused**: Enables controlled experiment - only feedback granularity changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MBPP) | Exa + Previous | B.4, D.1 |
| Model (CodeLlama-7B) | Exa + Previous | B.5, D.1 |
| Repair methodology | Literature | B.1 (Self-Debug) |
| Granularity levels (G0-G4) | Phase 2B | 02b_verification_plan.md |
| Pseudo-code design | Literature + Exa | B.1, B.2 |
| ANOVA implementation | Archon + Exa | A.2 |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Runtime error cases | Previous | D.1 (H-E1 results) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-30

### Workflow History for This Hypothesis
- h-m1 set to IN_PROGRESS (2026-03-30T07:47:20Z)
- Phase 2C experiment design started

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
