# Experiment Design: H-M1

**Date:** 2026-08-24
**Author:** yoon303b@gmail.com
**Hypothesis Statement:** At least one SA metric (pylint score OR mypy error count OR radon CC) shows point-biserial correlation r ≥ 0.35 with pass@1, controlling for code length, on combined HumanEval+MBPP dataset.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Testing whether SA metrics correlate with functional correctness.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** Yes (H-E1 validated: SA tools achieve 100% valid rate on 664 samples)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
At least one SA metric achieves point-biserial correlation r ≥ 0.35 with pass@1, with p < 0.05, after controlling for code length (LOC) as confounding variable.

---

## Continuation Context

**Previous Hypothesis:** H-E1 (EXISTENCE)
- **Result:** PASS - All 3 SA tools (pylint, mypy, radon) achieved 100% valid output rate on 664 HumanEval+MBPP samples
- **Reusable Components:** 
  - SA metric extraction wrappers (timeout handling, null value guards)
  - HumanEval + MBPP dataset loading
  - Code sample preprocessing pipeline

### Previous Hypothesis Results (if applicable)
- H-E1 validated infrastructure: pylint, mypy, radon all produce numeric outputs reliably
- No tool crashes or timeouts observed
- Ready for correlation analysis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "static analysis correlation code correctness"**
- Limited direct matches - KB focuses on diffusion models
- Key insight: Evaluation metrics pattern (CLIP score computation) provides template for metric computation pipelines

**Query 2: "point-biserial correlation code metrics"**
- No direct matches in KB
- Alternative: Use scipy.stats.pointbiserialr documentation patterns

### Archon Code Examples

**Code Example 1**: Calculate CLIP Score (pattern for metric computation)
- Source: HuggingFace Diffusers evaluation
- Pattern: Batch metric computation with normalization
- Applicable to: SA metric aggregation pipeline

### Exa GitHub Implementations

**Repository 1**: openai/human-eval (⭐ 3350)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Official HumanEval benchmark implementation
- **Key Code**:
  ```python
  from human_eval.data import write_jsonl, read_problems
  problems = read_problems()
  # evaluate_functional_correctness samples.jsonl
  # Returns: {'pass@1': ..., 'pass@10': ..., 'pass@100': ...}
  ```
- **Dataset Format**: JSONL with task_id, prompt, completion, passed
- **Results**: Provides per-sample pass/fail (binary outcome for correlation)

**Repository 2**: google-research/mbpp
- **URL**: https://github.com/google-research/google-research/tree/master/mbpp
- **Relevance**: Official MBPP benchmark (974 problems, 427 sanitized)
- **Splits**: Test IDs 11-510, Validation 511-600, Training 601-974
- **Format**: task_id, text (prompt), code (solution), test_list

**Repository 3**: HuggingFace datasets MBPP
- **URL**: https://huggingface.co/datasets/google-research-datasets/mbpp
- **Loading**: `load_dataset("mbpp", "sanitized")` → 427 samples
- **Code**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("google-research-datasets/mbpp", "sanitized")
  # Features: source_file, task_id, prompt, code, test_imports, test_list
  ```

### 🎯 Implementation Priority Assessment

**CRITICAL: For correlation analysis, use established statistical libraries**

**Recommended Implementation Path:**
- Primary: scipy.stats.pointbiserialr + pingouin.partial_corr
- Fallback: statsmodels for partial correlation
- Justification: scipy provides point-biserial correlation; pingouin provides partial correlation controlling for covariates (code length)

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Statistical analysis uses standard scipy/pingouin APIs.

---

## Experiment Specification

### Dataset

**Combined Dataset: HumanEval + MBPP**

| Component | Details |
|-----------|---------|
| HumanEval | 164 hand-crafted problems |
| MBPP (sanitized) | 427 problems |
| **Total** | **591 unique problems** |

**Note:** H-E1 used 664 samples (includes duplicates/variations). For correlation analysis, use 591 unique problem-solution pairs to avoid inflation.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + openai/human-eval
- Identifier: `"openai/human-eval"`, `"google-research-datasets/mbpp"`
- Code:
  ```python
  from datasets import load_dataset
  from human_eval.data import read_problems
  
  # HumanEval
  humaneval = read_problems()  # 164 problems
  
  # MBPP (sanitized subset)
  mbpp = load_dataset("google-research-datasets/mbpp", "sanitized")
  # Use test split: task_ids 11-510 → 500 problems
  # Or sanitized full: 427 problems
  ```

### Models

#### Baseline Model

**This is a correlation study, not a model training experiment.**

- **Model Role:** LLM-generated code samples (pre-existing)
- **Source:** Use existing LLM outputs from HumanEval/MBPP leaderboards OR generate fresh samples
- **For reproducibility:** Use a single LLM (e.g., GPT-4, Claude-3, CodeLlama-34B)
- **Sample count:** 1 completion per problem (pass@1 setting)

**Loading Information** (for Phase 4 download):
- Method: API call OR pre-generated samples
- Identifier: Model-specific (e.g., `gpt-4`, `claude-3-opus`)
- Code:
  ```python
  # Option 1: Load pre-generated samples
  samples = load_jsonl("samples_gpt4.jsonl")
  
  # Option 2: Generate fresh (requires API key)
  # completion = llm.generate(prompt, max_tokens=512)
  ```

#### Proposed Model

**Architecture:** Not applicable (correlation study, not model modification)

**Core Mechanism Implementation:**

```python
# Core Mechanism: SA-Correctness Correlation Analysis
# Based on: scipy.stats + pingouin

import subprocess
from scipy.stats import pointbiserialr
import pingouin as pg
import pandas as pd

def extract_sa_metrics(code: str) -> dict:
    """Extract SA metrics from code sample.
    
    Args:
        code: Python code string
    Returns:
        dict with pylint_score, mypy_errors, radon_cc, loc
    """
    # Pylint score (0-10 scale)
    pylint_result = subprocess.run(
        ["pylint", "--output-format=json", "-"],
        input=code, capture_output=True, text=True, timeout=30
    )
    pylint_score = parse_pylint_score(pylint_result.stdout)
    
    # Mypy error count
    mypy_result = subprocess.run(
        ["mypy", "--ignore-missing-imports", "-"],
        input=code, capture_output=True, text=True, timeout=30
    )
    mypy_errors = count_mypy_errors(mypy_result.stdout)
    
    # Radon cyclomatic complexity (average)
    radon_cc = compute_radon_cc(code)
    
    # Code length (confounding variable)
    loc = len([l for l in code.split('\n') if l.strip()])
    
    return {
        "pylint_score": pylint_score,
        "mypy_errors": mypy_errors,
        "radon_cc": radon_cc,
        "loc": loc
    }

def compute_correlations(df: pd.DataFrame) -> dict:
    """Compute point-biserial and partial correlations.
    
    Args:
        df: DataFrame with columns [passed, pylint_score, mypy_errors, radon_cc, loc]
    Returns:
        dict with correlation results per metric
    """
    results = {}
    
    for metric in ["pylint_score", "mypy_errors", "radon_cc"]:
        # Raw point-biserial correlation
        r_raw, p_raw = pointbiserialr(df["passed"], df[metric])
        
        # Partial correlation controlling for LOC
        partial = pg.partial_corr(
            data=df, x=metric, y="passed", covar="loc"
        )
        r_partial = partial["r"].values[0]
        p_partial = partial["p-val"].values[0]
        
        results[metric] = {
            "r_raw": r_raw, "p_raw": p_raw,
            "r_partial": r_partial, "p_partial": p_partial
        }
    
    return results
```

### Training Protocol

**Not applicable - this is a statistical analysis, not model training.**

**Analysis Protocol:**
1. Load HumanEval + MBPP problems (N ≈ 591)
2. For each problem, obtain LLM-generated code completion
3. Run test cases to determine pass/fail (binary: pass@1)
4. Extract SA metrics (pylint, mypy, radon) for each completion
5. Extract code length (LOC) as covariate
6. Compute point-biserial correlations (raw)
7. Compute partial correlations controlling for LOC
8. Report max(r_pylint, r_mypy, r_radon) with p-values

**Seeds:** 1 (deterministic analysis; no training randomness)

### Evaluation

**Primary Metrics:**
- Point-biserial correlation coefficient (r) for each SA metric vs pass@1
- Partial correlation coefficient (r) controlling for LOC
- P-value for statistical significance

**Success Criteria:**
- **PASS:** max(|r_pylint|, |r_mypy|, |r_radon|) ≥ 0.35 with p < 0.05
- **FAIL:** All correlations < 0.35 OR all p ≥ 0.05

**Expected Results (from literature):**
- Code quality metrics typically show r = 0.2-0.4 with correctness
- SA metrics on LLM code: limited prior work, exploratory

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification correlation
- Library: scipy.stats, pingouin
- Code:
  ```python
  from scipy.stats import pointbiserialr
  import pingouin as pg
  
  r, p = pointbiserialr(passed_binary, sa_metric)
  partial = pg.partial_corr(data=df, x="metric", y="passed", covar="loc")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing r values for pylint, mypy, radon with threshold line at r=0.35
- **Scatter plots**: SA metric vs pass@1 (jittered for binary outcome) with regression line

#### Additional Figures (LLM Autonomous)
- Correlation matrix heatmap (SA metrics + LOC + passed)
- Distribution plots of SA metrics by pass/fail group
- Partial correlation comparison (raw vs controlled for LOC)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **Mechanism Exists:** SA metrics extraction functions operational (validated in H-E1)
- **Mechanism Isolatable:** Each SA metric computed independently
- **Baseline Measurable:** Pass@1 binary outcome from test execution

### Architecture Compatibility
- **Compatible:** Statistical analysis requires no model architecture changes
- **Dependencies:** scipy, pingouin, pylint, mypy, radon (all standard Python packages)

### Activation Indicators
- **Mechanism Log Message:** "Computing correlations for {N} samples across 3 SA metrics"
- **Tensor Shape Change:** N/A (statistical analysis, not tensor operations)
- **Metric Delta Expected:** Correlation coefficient r ∈ [-1, 1], expect |r| ∈ [0.1, 0.5]

### Mechanism Verification Code
```python
def verify_mechanism_activation(df, results):
    """Verify correlation analysis mechanism worked correctly."""
    checks = {
        "sample_count": len(df) >= 500,  # Sufficient sample size
        "metrics_extracted": all(col in df.columns for col in 
                                 ["pylint_score", "mypy_errors", "radon_cc", "loc", "passed"]),
        "correlations_computed": all(m in results for m in 
                                     ["pylint_score", "mypy_errors", "radon_cc"]),
        "valid_r_values": all(-1 <= results[m]["r_partial"] <= 1 for m in results),
        "p_values_computed": all("p_partial" in results[m] for m in results),
    }
    
    print("Mechanism Verification:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}: {passed}")
    
    return all(checks.values())
```

### Hypothesis Support Threshold
- **Metric:** max(|r_partial|) across SA metrics
- **Threshold:** ≥ 0.35
- **Interpretation:** At least one SA metric shows moderate correlation with functional correctness after controlling for code length

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (correlation analysis completes)
2. At least one SA metric achieves |r| ≥ 0.35 with p < 0.05

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Limited relevant results* - KB focused on diffusion models, not code analysis.

### B. GitHub Implementations (Exa)

**Repository 1**: openai/human-eval (⭐ 3350)
- **URL**: https://github.com/openai/human-eval
- **Query Used**: "HumanEval MBPP pass@1 evaluation python"
- **Relevance**: Official benchmark for code generation evaluation
- **Used For**: Dataset format, pass@1 computation

**Repository 2**: google-research/mbpp
- **URL**: https://github.com/google-research/google-research/tree/master/mbpp
- **Query Used**: (same)
- **Relevance**: Official MBPP dataset
- **Used For**: Dataset loading, problem structure

**Repository 3**: raphaelvallat/pingouin
- **URL**: https://github.com/raphaelvallat/pingouin
- **Query Used**: "scipy pointbiserialr partial correlation pingouin"
- **Relevance**: Partial correlation implementation
- **Used For**: Core statistical analysis methodology
- **Key Code**:
  ```python
  pg.partial_corr(data=df, x="x", y="y", covar="cv1")
  # Returns: n, r, CI95%, p-val
  ```

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

### D. Previous Hypothesis Context

**Source**: H-E1 Validation (PASS)
- **Reused Components:**
  - SA metric extraction wrappers (pylint, mypy, radon)
  - HumanEval + MBPP dataset loading pipeline
  - Timeout handling (30s per tool)
- **Why Reused**: Infrastructure validated; enables controlled correlation study

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (HumanEval) | GitHub | openai/human-eval |
| Dataset (MBPP) | GitHub | google-research/mbpp |
| SA metric extraction | Previous | H-E1 validated code |
| Point-biserial correlation | SciPy docs | scipy.stats.pointbiserialr |
| Partial correlation | GitHub + Docs | pingouin.partial_corr |
| Pass@1 evaluation | GitHub | openai/human-eval |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- Phase 2C Step 1: Initialized, loaded H-E1 prerequisite (PASS)
- Phase 2C Step 2-3: MCP research (Archon, Exa) completed
- Phase 2C Step 4: Serena skipped (code clear)
- Phase 2C Step 5: Dataset/baseline confirmed (HumanEval+MBPP, correlation study)
- Phase 2C Step 6: Experiment specification synthesized
- Phase 2C Step 7: References documented
- Phase 2C Step 8: Validation PASSED, marked COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Skipped)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
