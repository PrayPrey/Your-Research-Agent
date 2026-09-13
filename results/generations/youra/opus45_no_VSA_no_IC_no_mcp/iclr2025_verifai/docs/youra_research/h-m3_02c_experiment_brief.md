# Experiment Brief: H-M3 Fix Specificity Inverted-U Pattern

**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-28
**Prerequisites:** h-e1 (VALIDATED)

---

## 1. Hypothesis Statement

Fix specificity shows inverted-U pattern: Levels 1-2 (general strategy, specific pattern) achieve higher repair success than both Level 0 (no hint) and Level 3 (exact fix), with significant quadratic contrast.

**Success Criteria:**
- Quadratic contrast significant (p < 0.05)
- Level 1 or 2 achieves highest repair success
- Inverted-U pattern replicated across models

---

## 2. Experimental Design

### 2.1 Independent Variable

**Fix Specificity Level** (4 levels):

| Level | Name | Description | Example |
|-------|------|-------------|---------|
| 0 | No Hint | Error info only, no fix direction | "TypeError: can only concatenate str to str" |
| 1 | General Strategy | Category of fix needed | "Convert types to match before operation" |
| 2 | Specific Pattern | Code pattern to apply | "Use int() to convert string to integer" |
| 3 | Exact Fix | Complete solution | "Change add_numbers(\"1\", 2) to add_numbers(int(\"1\"), 2)" |

### 2.2 Dependent Variable

**Repair Success Rate**: Proportion of failing test cases that pass after self-repair attempt.

### 2.3 Control Variables

| Variable | Control Method |
|----------|----------------|
| Error format | Fixed at Structured (from h-e1) |
| Temperature | Fixed at 0.0 (greedy decoding) |
| Max repair iterations | Fixed at 1 |
| Prompt template | Identical except hint section |
| Test cases | Same failing cases across all 4 levels |

---

## 3. Dataset Specification

### 3.1 Primary Dataset

**Reuse from h-e1:**
- EvalPlus (HumanEval+ and MBPP+)
- Type: standard
- Source: https://github.com/evalplus/evalplus

### 3.2 Data Preparation

**Inherit failure set from h-e1:**
- Use same filtered errors (SyntaxError, TypeError, NameError, AttributeError)
- Expected N ≈ 390 errors across 3 models
- Each error tested at all 4 specificity levels

### 3.3 Sample Size

**Required for polynomial contrast:**
- 4 levels × ~130 errors per model = 520 observations per model
- Total: ~1560 observations across 3 models
- Power for quadratic contrast: >0.90 at this N

---

## 4. Model Configuration

### 4.1 Models Under Test

| Model | Source | Access Method |
|-------|--------|---------------|
| CodeLlama-7B | HuggingFace | Local (vLLM) |
| CodeLlama-34B | HuggingFace | Local (vLLM) |
| GPT-4 | OpenAI | API |

### 4.2 Generation Parameters

```python
generation_config = {
    "temperature": 0.0,
    "max_new_tokens": 512,
    "stop_sequences": ["```", "\ndef ", "\nclass "],
}
```

---

## 5. Fix Specificity Templates

### 5.1 Level 0: No Hint

```
PROBLEM: TypeError - type mismatch in operation
LOCATION: test.py:5, function call add_numbers("1", 2)
CONTEXT:
    result = add_numbers("1", 2)
ROOT CAUSE: String "1" cannot concatenate with integer 2.
```

### 5.2 Level 1: General Strategy

```
PROBLEM: TypeError - type mismatch in operation
LOCATION: test.py:5, function call add_numbers("1", 2)
CONTEXT:
    result = add_numbers("1", 2)
ROOT CAUSE: String "1" cannot concatenate with integer 2.
HINT: Convert types to match before performing the operation.
```

### 5.3 Level 2: Specific Pattern

```
PROBLEM: TypeError - type mismatch in operation
LOCATION: test.py:5, function call add_numbers("1", 2)
CONTEXT:
    result = add_numbers("1", 2)
ROOT CAUSE: String "1" cannot concatenate with integer 2.
HINT: Use int() to convert string argument to integer, e.g., int(x).
```

### 5.4 Level 3: Exact Fix

```
PROBLEM: TypeError - type mismatch in operation
LOCATION: test.py:5, function call add_numbers("1", 2)
CONTEXT:
    result = add_numbers("1", 2)
ROOT CAUSE: String "1" cannot concatenate with integer 2.
FIX: Change the call to add_numbers(int("1"), 2).
```

---

## 6. Hint Generation Pipeline

### 6.1 Automated Hint Generation

```python
def generate_hints(error_info: dict) -> dict:
    """Generate all 4 specificity levels for an error."""
    base = format_structured_error(error_info)  # From h-e1
    
    # Level 0: Base only
    level_0 = base
    
    # Level 1: General strategy (template-based)
    strategy = ERROR_TYPE_STRATEGIES[error_info["type"]]
    level_1 = f"{base}\nHINT: {strategy}"
    
    # Level 2: Specific pattern (LLM-generated, cached)
    pattern = get_specific_pattern(error_info)
    level_2 = f"{base}\nHINT: {pattern}"
    
    # Level 3: Exact fix (LLM-generated, validated)
    exact_fix = get_exact_fix(error_info)
    level_3 = f"{base}\nFIX: {exact_fix}"
    
    return {0: level_0, 1: level_1, 2: level_2, 3: level_3}
```

### 6.2 Strategy Templates (Level 1)

| Error Type | General Strategy |
|------------|------------------|
| SyntaxError | Check syntax structure and matching delimiters |
| TypeError | Convert types to match or use compatible operation |
| NameError | Define the variable or import the module before use |
| AttributeError | Check object type and use appropriate method |

### 6.3 Pattern Generation (Level 2)

- Use GPT-4 to generate specific patterns
- Cache for consistency across models
- Validate patterns are actionable but not complete solutions

### 6.4 Exact Fix Generation (Level 3)

- Use GPT-4 to generate exact fixes
- Validate fix is correct (passes tests)
- This is the "oracle" condition

---

## 7. Evaluation Protocol

### 7.1 Execution Pipeline

```
For each model in [CodeLlama-7B, CodeLlama-34B, GPT-4]:
    For each error in filtered_errors:
        hints = generate_hints(error)
        For level in [0, 1, 2, 3]:
            1. Create prompt with hints[level]
            2. Generate repair
            3. Evaluate against test suite
            4. Record: problem_id, error_type, level, success
```

### 7.2 Metrics

| Metric | Definition |
|--------|------------|
| Success Rate per Level | (Repaired & Passing) / Total at Level |
| Linear Contrast | Tests monotonic increase/decrease |
| Quadratic Contrast | Tests inverted-U pattern |
| Peak Level | Level with highest success rate |

### 7.3 Statistical Analysis

```python
import numpy as np
from scipy.stats import f_oneway
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Polynomial contrast coding for ordinal IV
contrasts = {
    'linear': [-3, -1, 1, 3],
    'quadratic': [1, -1, -1, 1],
    'cubic': [-1, 3, -3, 1]
}

# Fit polynomial regression
model = ols('success ~ C(level, Poly)', data=df).fit()

# Test quadratic term
quadratic_coef = model.params['C(level, Poly).Quadratic']
quadratic_pval = model.pvalues['C(level, Poly).Quadratic']

# Alternative: Contrast analysis
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.contrast import ContrastResults

# Test specific contrast
quadratic_test = model.t_test(contrasts['quadratic'])
```

---

## 8. Expected Results

### 8.1 Predicted Pattern

```
Success Rate
    ^
    |      ___
    |     /   \
    |    /     \
    |   /       \
    |  /         \
    | /           \
    +--0---1---2---3--> Level
       No  Gen  Spec Exact
       Hint Strat Pat  Fix
```

### 8.2 Predicted Values

| Level | Predicted Success Rate | Rationale |
|-------|------------------------|-----------|
| 0 | 35-40% | Baseline structured format (from h-e1) |
| 1 | 45-50% | Activates relevant knowledge |
| 2 | 50-55% | Optimal guidance level |
| 3 | 40-45% | Copy-paste bypasses reasoning |

### 8.3 Model Interaction Prediction

- GPT-4: Flatter curve (less sensitive to hints)
- CodeLlama-7B: Steeper curve (more sensitive to hints)
- CodeLlama-34B: Intermediate

---

## 9. Implementation Dependencies

### 9.1 Required Packages

```
evalplus>=0.2.0
vllm>=0.2.0
openai>=1.0.0
transformers>=4.35.0
scipy>=1.11.0
statsmodels>=0.14.0
pandas>=2.0.0
numpy>=1.24.0
```

### 9.2 Compute Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU VRAM | 24GB (7B) / 80GB (34B) | A100 80GB |
| RAM | 64GB | 128GB |
| Storage | 100GB | 200GB |
| API Budget | $100 (GPT-4 for hints + eval) | $150 |

---

## 10. Baseline Comparison

### 10.1 Baselines from h-e1

| Condition | Expected Rate | Source |
|-----------|---------------|--------|
| Raw format (no hint) | ~30-35% | h-e1 control |
| Structured format (no hint) | ~40-45% | h-e1 treatment |

### 10.2 Comparison Points

- Level 0 should match h-e1 Structured condition
- Levels 1-2 should exceed Level 0
- Level 3 tests ceiling effect

---

## 11. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Hint quality variance | Cache hints, validate before use |
| Level 3 not truly "exact" | Validate fixes pass tests before using |
| Monotonic instead of inverted-U | Report pattern regardless, adjust interpretation |
| Low power for interaction | Pool across benchmarks for model comparison |

---

## 12. Success Criteria Summary

**Pass (Gate Satisfied):**
- Quadratic contrast coefficient negative (inverted-U)
- p < 0.05 for quadratic term
- Level 1 or 2 highest in at least 2/3 models

**Alternative Pass:**
- If monotonic increasing: hints always help, no ceiling
- If monotonic decreasing: model capability ceiling reached
- Report observed pattern, adjust mechanism interpretation

**Fail (Gate Not Satisfied):**
- No significant pattern (flat across levels)
- Random variation dominates

---

## 13. Output Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| Raw results | JSONL | results/h-m3/raw_results.jsonl |
| Hint cache | JSON | results/h-m3/hint_cache.json |
| Statistical analysis | Markdown | results/h-m3/analysis.md |
| Figures | PNG | results/h-m3/figures/ |
| Checkpoint | YAML | results/h-m3/checkpoint.yaml |

---

## 14. Research Contribution

**Novelty:** First systematic test of fix specificity as ordinal treatment in LLM self-repair.

**Theoretical Contribution:** Tests scaffolded learning hypothesis (ZPD) in code generation context.

**Practical Contribution:** Identifies optimal hint specificity for error formatting tools.

---

*Generated by Phase 2C Experiment Design*
*Status: COMPLETE*
