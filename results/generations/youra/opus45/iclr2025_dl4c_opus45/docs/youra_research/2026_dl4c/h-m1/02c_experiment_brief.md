# Experiment Design: H-M1

**Date:** 2026-03-24
**Author:** Anonymous
**Hypothesis Statement:** RL binary execution reward creates flat zero-reward basin over all non-executable programs, concentrating RL failures in assertion errors (code runs but wrong output)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 PASS)
**Gate Status:** MUST_WORK - Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED - PASS)

### Gate Condition
P(assertion | failure, RL) > P(assertion | failure, DPO) with statistical significance (p < 0.05)

---

## Continuation Context

This is a MECHANISM hypothesis that builds on H-E1's existence finding. H-M1 tests the specific causal mechanism: that RL's binary execution reward creates a "flat zero-reward basin" where all non-executable programs receive identical zero reward, creating pressure to first achieve execution before optimizing semantics. This should concentrate RL failures in assertion errors (code runs but produces wrong output).

### Previous Hypothesis Results (if applicable)
H-E1 validated successfully:
- Chi-square: 35.27 (p = 2.19e-08)
- Cramér's V: 0.2147
- RL assertion proportion: 2.1% vs DPO: 0.0%
- Direction already consistent with H-M1 prediction

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "RL execution reward code generation training"**
- Results primarily returned diffusion model training content (LoRA adapters, consistency models)
- No direct matches for code generation RL training patterns
- **Insight:** Archon KB lacks specific code generation RL content

**Query 2: "CodeRL binary reward training implementation"**
- Results returned diffusion/image generation content
- No CodeRL-specific documentation found
- **Insight:** Need to rely on original paper and GitHub implementations

**Query 3: "DPO preference alignment code generation"**
- Results related to diffusers library DPO training
- No code-specific DPO training content found
- **Insight:** DPO methodology documentation needed from HuggingFace TRL

**Key Takeaway:** Archon KB does not contain code generation alignment-specific content. Implementation must rely on:
1. Original CodeRL paper (Wang et al., ICLR 2023)
2. EvalPlus library for code execution
3. HuggingFace transformers for model loading

### Archon Code Examples

**Query 1: "code generation evaluation HumanEval execution"**
- No direct code examples for HumanEval evaluation found
- Results showed general evaluation scripts (FID, video metrics)
- **Insight:** Use EvalPlus library directly (evalplus/evalplus on GitHub)

**Query 2: "chi-square test error proportion Python statistics"**
- No statistical test code examples matched
- **Insight:** Use scipy.stats.chi2_contingency and scipy.stats.fisher_exact

**Code Pattern from Serena Memory (global/phase45/dl4c_alignment_signatures_2026):**
- Validated codebase exists: 9 modules (1,800 lines) for profiling + clustering
- Reusable components: HumanEval+ data loader, CodeProfiler, statistical tests
- Optimal config: temperature=0.8 for code generation

### Exa GitHub Implementations

**Query 1: CodeRL Official Implementation (HIGHEST PRIORITY)**

**Repository**: [salesforce/CodeRL](https://github.com/salesforce/CodeRL) (⭐ 558)
- **URL**: https://github.com/salesforce/CodeRL
- **Relevance**: Official implementation of CodeRL (NeurIPS 2022) - the exact RL-aligned model we're testing
- **Architecture**: CodeT5-large (770M) encoder-decoder, trained with actor-critic RL
- **Key Insight - Binary Reward Structure**:
  - CodeRL uses unit test pass/fail as binary reward signal
  - All execution failures (syntax, runtime) receive ZERO reward
  - Only programs passing unit tests receive positive reward
  - This confirms H-M1's "zero-reward basin" mechanism
- **Training Protocol**:
  - Pretrained on CodeSearchNet + Python GitHub Code
  - Fine-tuned with actor-critic RL using unit test feedback
  - Critic network trained to estimate program quality
- **Model Checkpoint**: `Salesforce/codet5-large-ntp-py` on HuggingFace
- **Evaluation**: Uses APPS and MBPP benchmarks with pass@k metrics

**Repository**: [evalplus/evalplus](https://github.com/evalplus/evalplus) (⭐ 1701+)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: Standard evaluation framework for HumanEval+ and MBPP+
- **Key Features**:
  - HumanEval+: 80x more tests than original (164 problems)
  - MBPP+: 35x more tests than original (399 problems from sanitized 427)
  - Automated execution with detailed error traces
- **Installation**: `pip install evalplus --upgrade`
- **Usage**:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  # Load problems
  problems = get_human_eval_plus()  # or get_mbpp_plus()
  # Evaluate samples
  # evalplus.evaluate --dataset humaneval --samples samples.jsonl
  ```
- **Error Classification**: Execution provides error type (syntax/runtime/assertion) through exception handling

**Query 2: Statistical Testing (Fisher's Exact / Chi-Square)**

**Source**: scipy.stats documentation
- **Chi-square test**: `scipy.stats.chi2_contingency(observed)` for contingency tables
- **Fisher's exact test**: `scipy.stats.fisher_exact(table, alternative='two-sided')` for 2x2 tables
- **When to use**:
  - Chi-square: Large samples (expected freq ≥ 5 per cell)
  - Fisher's exact: Small samples or when expected freq < 5
- **For H-M1**: Use Fisher's exact for assertion proportion comparison (2x2: RL/DPO × assertion/non-assertion)

**Code Pattern for Proportion Comparison**:
```python
from scipy.stats import fisher_exact, chi2_contingency
import numpy as np

# 2x2 contingency table: [RL_assertion, RL_other], [DPO_assertion, DPO_other]
table = np.array([[rl_assertion, rl_other], [dpo_assertion, dpo_other]])

# Fisher's exact test (one-sided: RL > DPO)
odds_ratio, p_value = fisher_exact(table, alternative='greater')
```

**Serena Analysis Needed**: false (code patterns are clear, reuse H-E1 infrastructure)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Assessment:**
1. **HIGHEST**: Reuse H-E1 execution results (already collected with official models)
2. **SECONDARY**: CodeRL official implementation (salesforce/CodeRL) already used in H-E1
3. **TERTIARY**: evalplus framework for error classification (already used in H-E1)

**Recommended Implementation Path:**
- Primary: Reuse H-E1 outputs (`h-e1/outputs/rl_execution_results.json`, `h-e1/outputs/dpo_execution_results.json`)
- Fallback: Re-run H-E1 experiment if data files are corrupted
- Justification: H-E1 already collected error classifications using official CodeRL model and evalplus framework. Reusing this data ensures consistency across the hypothesis chain and avoids redundant computation.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. H-M1 reuses the error classification infrastructure from H-E1:

**Reusable Components from H-E1:**
1. `h-e1/code/` - Complete experiment codebase (data loading, model inference, error classification)
2. `h-e1/outputs/rl_execution_results.json` - RL model error classifications
3. `h-e1/outputs/dpo_execution_results.json` - DPO model error classifications
4. Error taxonomy parser (syntax/runtime/assertion classification)

**Key H-E1 Results to Analyze:**
- RL assertion proportion: 5/235 = 2.1%
- DPO assertion proportion: 0/530 = 0.0%
- H-M1 tests if this difference is statistically significant with one-sided Fisher's exact test

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval+ and MBPP+ (standard)
**Type**: standard (code generation benchmark)
**Source**: evalplus/evalplus (GitHub, 1701+ stars)
**Splits**:
- HumanEval+: 164 problems with 80x test coverage
- MBPP+: 399 problems (sanitized subset with 35x test coverage)
- Total: 563 problems × 2 models = 1,126 samples (same as H-E1)

**Preprocessing**: None (problems used as-is with docstring prompts)
**Augmentation**: Multiple temperature samples (T=0.8, n=1 per problem for PoC)

**⚠️ DATA REUSE from H-E1:**
H-M1 will REUSE the execution results already collected in H-E1:
- `h-e1/outputs/rl_execution_results.json` (RL model error classifications)
- `h-e1/outputs/dpo_execution_results.json` (DPO model error classifications)
- This avoids redundant model inference and ensures exact same samples

**Loading Information** (for Phase 4 download):
- Method: REUSE from H-E1 (no new download needed)
- Identifier: evalplus/evalplus
- Code:
```python
# Reuse H-E1 results - no new inference needed
import json
with open("../h-e1/outputs/rl_execution_results.json") as f:
    rl_results = json.load(f)
with open("../h-e1/outputs/dpo_execution_results.json") as f:
    dpo_results = json.load(f)
```

### Models

#### Baseline Model

**RL Model (Treatment)**: Salesforce/codet5-large-ntp-py (CodeRL-770M)
- **Architecture**: CodeT5 encoder-decoder (770M parameters)
- **Alignment Method**: Execution-based RL with binary pass/fail reward
- **Reward Topology**: Zero reward for ALL execution failures (syntax, runtime); positive reward only for passing tests
- **This is the mechanism H-M1 tests**: Binary reward creates flat zero-reward basin

**DPO Model (Control)**: codellama/CodeLlama-7b-Instruct-hf
- **Architecture**: Decoder-only (7B parameters)
- **Alignment Method**: Direct Preference Optimization from human preferences
- **Reward Topology**: Continuous preference signal from pairwise comparisons, no explicit execution feedback

**⚠️ MODEL INFERENCE REUSE from H-E1:**
No new model inference needed - H-M1 analyzes the existing H-E1 outputs.

**Loading Information** (for Phase 4 download):
- Method: REUSE from H-E1 (models already run)
- Identifier: N/A (no new inference)
- Code: N/A (reuse existing results)

#### Proposed Model

**Architecture:** Analysis of H-E1 error distribution data to test zero-reward basin mechanism

**Analysis Approach:**
- Extract assertion error proportions from H-E1 results
- Compute one-sided Fisher's exact test: P(assertion | failure, RL) > P(assertion | failure, DPO)
- Document CodeRL's binary reward structure as the causal mechanism

**Core Mechanism Implementation:**

```python
# H-M1: Zero-Reward Basin Mechanism Analysis
# Based on: H-E1 execution results + CodeRL paper (Wang et al., NeurIPS 2022)

import json
import numpy as np
from scipy.stats import fisher_exact

def load_h_e1_results():
    """Load pre-computed error classifications from H-E1."""
    with open("../h-e1/outputs/rl_execution_results.json") as f:
        rl_results = json.load(f)
    with open("../h-e1/outputs/dpo_execution_results.json") as f:
        dpo_results = json.load(f)
    return rl_results, dpo_results

def classify_errors(results):
    """Count error types from execution results."""
    counts = {"syntax": 0, "runtime": 0, "assertion": 0, "pass": 0}
    for r in results:
        if r["status"] == "pass":
            counts["pass"] += 1
        else:
            counts[r["error_type"]] += 1
    return counts

def test_zero_reward_basin(rl_counts, dpo_counts):
    """
    H-M1 Gate: P(assertion | failure, RL) > P(assertion | failure, DPO)

    Mechanism: RL's binary execution reward creates flat zero-reward basin
    over all non-executable programs, concentrating RL failures in assertion
    errors (code runs but wrong output).
    """
    # Compute failure totals (exclude passes)
    rl_failures = rl_counts["syntax"] + rl_counts["runtime"] + rl_counts["assertion"]
    dpo_failures = dpo_counts["syntax"] + dpo_counts["runtime"] + dpo_counts["assertion"]

    # 2x2 contingency table: [RL, DPO] x [assertion, non-assertion]
    table = np.array([
        [rl_counts["assertion"], rl_failures - rl_counts["assertion"]],
        [dpo_counts["assertion"], dpo_failures - dpo_counts["assertion"]]
    ])

    # One-sided Fisher's exact test: RL assertion proportion > DPO
    odds_ratio, p_value = fisher_exact(table, alternative='greater')

    return {
        "rl_assertion_prop": rl_counts["assertion"] / rl_failures,
        "dpo_assertion_prop": dpo_counts["assertion"] / dpo_failures if dpo_failures > 0 else 0,
        "odds_ratio": odds_ratio,
        "p_value": p_value,
        "gate_pass": p_value < 0.05
    }
```

### Training Protocol

**⚠️ NO TRAINING REQUIRED for H-M1**

This is an **analysis hypothesis** that examines existing H-E1 results:
- No new model training needed
- No new model inference needed
- Analysis uses pre-computed error classifications from H-E1

**Analysis Protocol:**
1. Load H-E1 error classification results (already generated)
2. Extract assertion error counts for RL and DPO models
3. Compute Fisher's exact test for proportion comparison
4. Document CodeRL's reward structure from paper as causal explanation

**Computational Requirements:**
- **Duration**: < 1 second (pure statistical analysis)
- **GPU**: Not needed
- **Memory**: < 1 GB

### Evaluation

**Primary Metric**: Assertion error proportion P(assertion | failure)

**Statistical Test**: Fisher's exact test (one-sided)
- H0: P(assertion | failure, RL) ≤ P(assertion | failure, DPO)
- H1: P(assertion | failure, RL) > P(assertion | failure, DPO)

**Success Criteria (MUST_WORK Gate)**:
1. **Direction**: P(assertion | failure, RL) > P(assertion | failure, DPO)
2. **Significance**: Fisher's exact p < 0.05 (one-sided)

**Expected Values (from H-E1)**:
- RL assertion proportion: ~2.1% (5/235 failures)
- DPO assertion proportion: ~0.0% (0/530 failures)
- Expected: PASS (direction already consistent, testing for significance)

**Secondary Output**: Documented reward topology explanation
- CodeRL uses binary pass/fail reward (from paper + Exa findings)
- All non-executable programs receive zero reward
- This creates flat zero-reward basin as described in hypothesis

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical hypothesis testing
- Library: scipy.stats
- Code:
```python
from scipy.stats import fisher_exact
# One-sided test for RL > DPO
odds_ratio, p_value = fisher_exact(contingency_table, alternative='greater')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on H-M1's mechanism focus, generate:
1. **Assertion Proportion Comparison**: Bar chart comparing P(assertion | failure) for RL vs DPO
2. **Error Type Distribution**: Stacked bar chart showing full error breakdown (syntax/runtime/assertion) by model
3. **Reward Topology Diagram**: Conceptual visualization of binary reward structure showing zero-reward basin
4. **Contingency Table Heatmap**: Visual representation of 2x2 Fisher's exact test table

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 MUST_WORK Gate Check

**H-M1 MUST_WORK Gate Pass Condition:**
1. Code runs without error
2. P(assertion | failure, RL) > P(assertion | failure, DPO) (direction)
3. Fisher's exact p < 0.05 (one-sided significance)

**Mechanism Verification Protocol:**
- **Pre-condition**: H-E1 results exist and contain error classifications
- **Activation Indicator**: Non-zero assertion count for RL model
- **Architecture Compatibility**: Uses H-E1 error taxonomy (syntax/runtime/assertion)
- **Failure Detection**: If RL assertion count is 0, mechanism is NOT active
- **Mechanism Log Message**: "H-M1: RL assertion proportion = X%, DPO assertion proportion = Y%"
- **Hypothesis Support Threshold**: Fisher's exact p < 0.05
- **Hypothesis Support Metric**: One-sided Fisher's exact test p-value

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: Limited results for code generation RL
- **Type**: Knowledge base search
- **Query Used**: "RL execution reward code generation training"
- **Relevance**: Archon KB lacks specific code generation alignment content
- **Key Insights**:
  - No direct CodeRL-specific documentation found
  - Must rely on original paper and GitHub implementations
- **Used For**: Informed decision to prioritize Exa GitHub search

### B. GitHub Implementations (Exa)

**Repository B.1**: [salesforce/CodeRL](https://github.com/salesforce/CodeRL) (⭐ 558)
- **URL**: https://github.com/salesforce/CodeRL
- **Query Used**: "Salesforce CodeRL code generation execution reward training GitHub official implementation"
- **Relevance**: Official implementation confirming binary reward structure
- **Key Findings**:
  - CodeRL uses unit test pass/fail as binary reward
  - All execution failures (syntax, runtime) receive ZERO reward
  - Only passing programs receive positive reward
  - This confirms H-M1's zero-reward basin mechanism
- **Model**: `Salesforce/codet5-large-ntp-py` on HuggingFace
- **Used For**: Model specification, reward topology documentation

**Repository B.2**: [evalplus/evalplus](https://github.com/evalplus/evalplus) (⭐ 1701+)
- **URL**: https://github.com/evalplus/evalplus
- **Query Used**: "evalplus HumanEval MBPP code execution error classification Python"
- **Relevance**: Standard evaluation framework for HumanEval+ and MBPP+
- **Key Findings**:
  - HumanEval+: 164 problems with 80x test coverage
  - MBPP+: 399 problems with 35x test coverage
  - Provides execution with detailed error classification
- **Used For**: Dataset specification, error taxonomy

**Source B.3**: scipy.stats documentation
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html
- **Query Used**: "Python scipy Fisher exact test proportion comparison chi-square contingency table"
- **Relevance**: Statistical test implementation for proportion comparison
- **Key Findings**:
  - `fisher_exact(table, alternative='greater')` for one-sided test
  - Returns odds ratio and p-value
  - Appropriate for small expected cell counts
- **Used For**: Evaluation metrics, statistical test specification

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

**Serena Memory Used**:
- `global/phase45/dl4c_alignment_signatures_2026` - Provided context on validated infrastructure and reusable components

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-E1
- **File**: `h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: HumanEval+ and MBPP+ (proven stable)
  - Error classification: syntax/runtime/assertion taxonomy
  - Execution results: `h-e1/outputs/rl_execution_results.json`, `h-e1/outputs/dpo_execution_results.json`
- **Why Reused**: Enables controlled experiment - H-M1 analyzes the same data with different statistical test

**Key H-E1 Results**:
- Chi-square: 35.27 (p = 2.19e-08)
- Cramér's V: 0.2147
- RL: 5 assertion errors out of 235 failures (2.1%)
- DPO: 0 assertion errors out of 530 failures (0.0%)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (HumanEval+, MBPP+) | GitHub (Exa) | B.2 evalplus/evalplus |
| RL Model (CodeRL-770M) | GitHub (Exa) | B.1 salesforce/CodeRL |
| DPO Model (CodeLlama-7B) | Phase 2B | 02b_verification_plan.md |
| Binary reward structure | GitHub (Exa) | B.1 CodeRL paper + repo |
| Error classification | Previous | D.1 H-E1 validation report |
| Statistical test (Fisher's exact) | Documentation | B.3 scipy.stats |
| Execution results data | Previous | D.1 H-E1 outputs |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-24

### Workflow History for This Hypothesis
- H-E1 COMPLETED (2026-03-24): Chi-square highly significant (p=2.19e-08), Cramér's V = 0.2147
- H-M1 Phase 2C COMPLETED (2026-03-24): Experiment design generated, reusing H-E1 data for Fisher's exact test

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
