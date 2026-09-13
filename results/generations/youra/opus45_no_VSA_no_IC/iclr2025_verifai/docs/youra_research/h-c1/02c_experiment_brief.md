# Experiment Design: H-C1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** SA-correctness correlation generalizes across 3+ LLMs with variance std(r) < 0.15, demonstrating model-agnostic predictive signal.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASS: pylint r=0.873, radon_cc r=-0.569)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION
- **Prerequisites:** H-M1 (VALIDATED)

### Gate Condition
Verify SA-correctness correlation holds across 3+ LLMs with std(r) < 0.15 variance.

---

## Continuation Context

### Previous Hypothesis Results (H-M1)
- **pylint_score**: r_partial = 0.873, p < 0.001 (LOC-controlled)
- **radon_cc**: r_partial = -0.569, p < 0.001
- **mypy_errors**: Discarded (numerical artifact)
- **Finding**: pylint_score and radon_cc both exceed r≥0.35 threshold

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB lacks direct references to SA-correctness correlation studies. Domain coverage focused on deep learning infrastructure (diffusers, PyTorch optimization). No relevant prior cases found for this hypothesis type.

### Archon Code Examples

No directly applicable code examples in Archon for static analysis correlation measurement. However, standard scipy/pingouin correlation patterns applicable.

### Exa GitHub Implementations

**Key Sources Found:**
1. **bigcode-evaluation-harness** (github.com/bigcode-project/bigcode-evaluation-harness)
   - Standard framework for HumanEval/MBPP evaluation across LLMs
   - Supports multiple models, produces code completions with pass/fail status

2. **radon** (github.com/rubik/radon, pypi.org/project/radon)
   - Python static analysis: cyclomatic complexity, maintainability index
   - Commands: `radon cc -a -j` for JSON output

3. **Static Analysis of Code Quality** (doi.org/10.64589/juri/215034)
   - Research using Radon + Pylint + Flake8 together
   - Validated metric extraction methodology

4. **MultiPL-E** (github.com/nuprl/MultiPL-E)
   - Multi-language code generation benchmark
   - HuggingFace dataset: nuprl/MultiPL-E

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

No prior publication on SA-correctness cross-model generalization exists. This is novel research.

**Recommended Implementation Path:**
- Primary: Extend H-M1 codebase with multi-model data collection loop
- Fallback: Use bigcode-evaluation-harness for model inference if needed
- Justification: H-M1 code already implements SA metric extraction and correlation computation; only need to add per-model grouping

### Code Analysis (Serena MCP)

**H-M1 Codebase Analysis (reusable components):**
- `sa_tools.py`: Pylint/mypy/radon wrappers with ToolResult dataclass
- `correlate.py`: Point-biserial and partial correlation (LOC-controlled) via scipy/pingouin
- `dataset.py`: HumanEval/MBPP loading
- `config.py`: CONFIG dataclass with thresholds

All components directly reusable for H-C1. Only new code needed:
1. Multi-model data ingestion (add `model_id` column)
2. Per-model correlation groupby
3. Cross-model variance computation

---

## Experiment Specification

### Dataset

**Primary Dataset:** HumanEval + MBPP-sanitized (same as H-M1)
- HumanEval: 164 problems
- MBPP-sanitized-test: 257 problems
- Total: 421 problems per model

**Multi-Model Code Completions Required:**
| Model | Source | Min Samples |
|-------|--------|-------------|
| GPT-4 | OpenAI API / cached outputs | 421 |
| Claude-3 (Sonnet/Opus) | Anthropic API / cached outputs | 421 |
| CodeLlama-70B | HF Inference / cached outputs | 421 |
| Codestral | Mistral API / cached outputs | 421 |

**Data Structure:**
- One completion per problem per model
- Columns: `task_id`, `model_id`, `code`, `passed` (0/1), `pylint_score`, `radon_cc`, `loc`

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + API calls OR cached completions
- Identifier: `openai/openai_humaneval`, `google-research-datasets/mbpp`
- Code:
```python
from datasets import load_dataset
humaneval = load_dataset("openai/openai_humaneval", split="test")
mbpp = load_dataset("google-research-datasets/mbpp", "sanitized", split="test")
```

### Models

#### Baseline Model

**No ML model training required.** This is a statistical analysis experiment.

Baseline = per-model correlation coefficients computed independently:
- r_gpt4: correlation(SA_metric, pass@1) for GPT-4 outputs
- r_claude3: correlation(SA_metric, pass@1) for Claude-3 outputs
- r_codellama: correlation(SA_metric, pass@1) for CodeLlama outputs
- r_codestral: correlation(SA_metric, pass@1) for Codestral outputs

**Loading Information** (for Phase 4 download):
- Method: N/A (no pretrained model needed)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Statistical variance analysis across model correlations

**Core Mechanism Implementation:**

```python
import numpy as np
import pandas as pd
from scipy.stats import pointbiserialr
import pingouin as pg

def compute_per_model_correlations(
    df: pd.DataFrame,
    metric: str = "pylint_score",
    models: list[str] = ["gpt4", "claude3", "codellama", "codestral"]
) -> dict[str, float]:
    """Compute partial correlation (LOC-controlled) for each model."""
    correlations = {}
    for model in models:
        model_df = df[df["model_id"] == model]
        result = pg.partial_corr(
            data=model_df, x=metric, y="passed", covar="loc", method="pearson"
        )
        correlations[model] = float(result["r"].iloc[0])
    return correlations

def check_cross_model_generalization(
    correlations: dict[str, float],
    variance_threshold: float = 0.15
) -> tuple[bool, float, float]:
    """Check if std(r) < threshold across models."""
    r_values = list(correlations.values())
    mean_r = np.mean(r_values)
    std_r = np.std(r_values)
    passed = std_r < variance_threshold
    return passed, mean_r, std_r

# Main execution
df = load_multi_model_data()  # DataFrame with model_id column
correlations = compute_per_model_correlations(df, metric="pylint_score")
passed, mean_r, std_r = check_cross_model_generalization(correlations)
print(f"PASS: {passed}, mean(r)={mean_r:.3f}, std(r)={std_r:.3f}")
```

### Training Protocol

**No training required.** This is a statistical analysis experiment.

**Execution Protocol:**
1. Load HumanEval + MBPP problems
2. For each model in [GPT-4, Claude-3, CodeLlama-70B, Codestral]:
   - Load or generate code completions
   - Run test execution to determine pass/fail
   - Extract SA metrics (pylint_score, radon_cc)
   - Record LOC for partial correlation control
3. Compute per-model partial correlations
4. Compute cross-model variance std(r)
5. Evaluate gate: std(r) < 0.15

### Evaluation

**Primary Metric:** std(r_per_model) - standard deviation of correlation coefficients across models

**Success Criterion:** std(r) < 0.15

**Secondary Metrics:**
- mean(r) across models (expected ~0.5-0.8 based on H-M1)
- min(r), max(r) to identify outlier models
- Per-model p-values (all should be < 0.05)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical correlation analysis
- Library: scipy, pingouin, numpy
- Code:
```python
import numpy as np
from scipy.stats import pointbiserialr
import pingouin as pg

# Variance across models
std_r = np.std([r_gpt4, r_claude3, r_codellama, r_codestral])
gate_passed = std_r < 0.15
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Per-model correlation bar chart with error bars

#### Additional Figures (LLM Autonomous)

1. **Per-Model Correlation Comparison** (bar chart)
   - X-axis: Model names
   - Y-axis: Partial correlation r (pylint_score)
   - Horizontal line at mean(r), shaded region for ±std(r)

2. **Correlation Heatmap** (matrix)
   - Rows: SA metrics (pylint, radon_cc)
   - Columns: Models
   - Cell values: r coefficients

3. **Distribution Overlap** (violin/boxplot)
   - Compare SA metric distributions across models to visualize why correlations might vary

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `std(r_per_model) < 0.15` across 3+ LLMs

---

## Appendix: Reference Implementations

### Primary References

1. **H-M1 Codebase** (local)
   - Path: `docs/youra_research/h-m1/code/`
   - Files: `sa_tools.py`, `correlate.py`, `dataset.py`, `config.py`
   - Status: Validated, directly reusable

2. **bigcode-evaluation-harness**
   - URL: https://github.com/bigcode-project/bigcode-evaluation-harness
   - Purpose: Multi-model HumanEval/MBPP evaluation framework
   - Use: Reference for model inference patterns

3. **Radon Documentation**
   - URL: https://radon.readthedocs.io/en/latest/
   - Purpose: Cyclomatic complexity and maintainability index computation
   - Command: `radon cc -a -j <file>` for JSON output

4. **OpenAI HumanEval Dataset**
   - URL: https://huggingface.co/datasets/openai/openai_humaneval
   - Purpose: Standard code generation benchmark

5. **MBPP Dataset**
   - URL: https://huggingface.co/datasets/google-research-datasets/mbpp
   - Purpose: Mostly Basic Python Problems benchmark

### Statistical Methods

1. **Point-biserial correlation**
   - scipy.stats.pointbiserialr
   - For binary (pass/fail) vs continuous (SA metric)

2. **Partial correlation**
   - pingouin.partial_corr
   - Control for LOC confound

### Code Snippets from Research

**SA Metric Extraction (from H-M1):**
```python
def run_pylint(code: str, timeout: int = 30) -> ToolResult:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = subprocess.run(
            ["pylint", f.name, "--score=y"],
            capture_output=True, text=True, timeout=timeout
        )
        match = re.search(r"rated at ([\d.-]+)/10", result.stdout + result.stderr)
        return ToolResult(True, float(match.group(1)), None)
```

**Partial Correlation (from H-M1):**
```python
import pingouin as pg
result = pg.partial_corr(data=df, x="pylint_score", y="passed", covar="loc")
r_partial = float(result["r"].iloc[0])
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C started

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
