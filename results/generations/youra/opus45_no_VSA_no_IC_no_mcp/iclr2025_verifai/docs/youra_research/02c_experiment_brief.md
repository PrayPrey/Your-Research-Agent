# Experiment Brief: H-E1 Structured Error Format

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Date:** 2026-08-28

---

## 1. Hypothesis Statement

Structured error format achieves statistically significant higher repair success rate than raw compiler output on HumanEval+ and MBPP+ benchmarks across CodeLlama-7B, CodeLlama-34B, and GPT-4.

**Success Criteria:**
- Structured format > Raw format by ≥5% absolute improvement
- p < 0.05 (BH-FDR corrected)
- Effect size (Cohen's d) ≥ 0.3

---

## 2. Experimental Design

### 2.1 Independent Variable

**Error Format** (2 levels):
1. **Raw**: Direct compiler/interpreter output as-is
2. **Structured**: Formatted template with sections:
   ```
   PROBLEM: [error type]
   LOCATION: [file:line]
   CONTEXT: [relevant code snippet]
   ROOT CAUSE: [explanation]
   ```

### 2.2 Dependent Variable

**Repair Success Rate**: Proportion of failing test cases that pass after self-repair attempt.

### 2.3 Control Variables

| Variable | Control Method |
|----------|----------------|
| Information content | Structured format preserves all raw info |
| Temperature | Fixed at 0.0 (greedy decoding) |
| Max repair iterations | Fixed at 1 |
| Prompt template | Identical except error format section |
| Test cases | Same failing cases across conditions |

---

## 3. Dataset Specification

### 3.1 Primary Dataset

**EvalPlus (HumanEval+ and MBPP+)**
- Type: standard
- Source: https://github.com/evalplus/evalplus
- Installation: `pip install "evalplus[vllm] @ git+https://github.com/evalplus/evalplus"`

**Dataset Composition:**
| Benchmark | Problems | Test Cases per Problem |
|-----------|----------|------------------------|
| HumanEval+ | 164 | ~80x original (variable) |
| MBPP+ | 378 | ~35x original (variable) |

### 3.2 Data Preparation Pipeline

```
Step 1: Generate initial code with base model
        → CodeLlama-7B, CodeLlama-34B, GPT-4 on HumanEval+/MBPP+
        
Step 2: Execute against EvalPlus test suite
        → Collect failures with static analysis errors
        
Step 3: Filter by error type
        → Include: SyntaxError, TypeError, NameError, AttributeError
        → Exclude: Timeout, MemoryError (not format-addressable)
        
Step 4: Create paired samples
        → Same error in Raw and Structured format
```

### 3.3 Sample Size Estimation

**Minimum:** Full EvalPlus test sets (164 + 378 = 542 problems)

**Expected failure collection:**
- Assume 40% initial failure rate → ~217 failures
- Filter to static analysis errors (~60% of failures) → ~130 errors per model
- Total: ~390 paired samples across 3 models

**Power Analysis:**
- Effect size d = 0.3 (small-medium)
- α = 0.05, Power = 0.80
- Required N ≈ 175 per condition
- Available N ≈ 390 → Adequate power

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
    "temperature": 0.0,      # Greedy decoding
    "max_new_tokens": 512,   # Sufficient for repair
    "stop_sequences": ["```", "\ndef ", "\nclass "],
}
```

### 4.3 Self-Repair Prompt Template

```
The following code failed with an error:

```python
{generated_code}
```

{ERROR_FEEDBACK_SECTION}  # <- IV: Raw vs Structured

Fix the code to pass all tests. Output only the corrected code:

```python
```

---

## 5. Error Format Transformation

### 5.1 Raw Format (Control)

Direct output from Python interpreter:
```
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    result = add_numbers("1", 2)
TypeError: can only concatenate str (not "int") to str
```

### 5.2 Structured Format (Treatment)

Transformed template:
```
PROBLEM: TypeError - type mismatch in operation
LOCATION: test.py:5, function call add_numbers("1", 2)
CONTEXT:
    result = add_numbers("1", 2)
    ^^^^^^^^^^^^^^^^^^^^^^^^^
ROOT CAUSE: String "1" cannot concatenate with integer 2. 
The + operator requires matching types.
```

### 5.3 Transformation Rules

| Error Type | Extraction | Structured Mapping |
|------------|------------|-------------------|
| SyntaxError | Parse error message | PROBLEM: syntax, LOCATION: line/col |
| TypeError | Extract types involved | PROBLEM: type mismatch, ROOT CAUSE: type explanation |
| NameError | Extract undefined name | PROBLEM: undefined, ROOT CAUSE: name not in scope |
| AttributeError | Extract object/attr | PROBLEM: missing attribute, ROOT CAUSE: object type |

---

## 6. Evaluation Protocol

### 6.1 Execution Pipeline

```
For each model in [CodeLlama-7B, CodeLlama-34B, GPT-4]:
    For each benchmark in [HumanEval+, MBPP+]:
        1. Generate initial solutions
        2. Run evalplus.evaluate → collect failures
        3. Filter to static analysis errors
        4. For each failure:
            a. Create Raw prompt → generate repair
            b. Create Structured prompt → generate repair
            c. Evaluate both repairs against test suite
        5. Record: problem_id, error_type, raw_success, structured_success
```

### 6.2 Metrics

| Metric | Definition |
|--------|------------|
| Repair Success Rate | (Repaired & Passing) / Total Failures |
| Absolute Improvement | Structured_rate - Raw_rate |
| Relative Improvement | (Structured - Raw) / Raw |
| Cohen's d | (μ_structured - μ_raw) / σ_pooled |

### 6.3 Statistical Analysis

```python
from scipy.stats import ttest_rel, wilcoxon
from statsmodels.stats.multitest import multipletests

# Paired t-test per model
t_stat, p_value = ttest_rel(structured_success, raw_success)

# BH-FDR correction across 3 models × 2 benchmarks = 6 tests
_, p_corrected, _, _ = multipletests(p_values, method='fdr_bh')

# Effect size
cohens_d = (np.mean(structured) - np.mean(raw)) / np.std(pooled)
```

---

## 7. Implementation Dependencies

### 7.1 Required Packages

```
evalplus>=0.2.0
vllm>=0.2.0
openai>=1.0.0
transformers>=4.35.0
scipy>=1.11.0
statsmodels>=0.14.0
pandas>=2.0.0
```

### 7.2 Compute Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU VRAM | 24GB (7B) / 80GB (34B) | A100 80GB |
| RAM | 64GB | 128GB |
| Storage | 100GB | 200GB |
| API Budget | $50 (GPT-4) | $100 |

### 7.3 Reference Implementations

- EvalPlus: https://github.com/evalplus/evalplus
- Self-Repair (ICLR 2024): https://github.com/theoxo/self-repair (archived)
- BigCode Eval Harness: https://github.com/bigcode-project/bigcode-evaluation-harness

---

## 8. Baseline Comparison

### 8.1 Expected Baselines

| Condition | Expected Rate | Source |
|-----------|---------------|--------|
| No repair | 0% (by definition) | - |
| Raw format | ~30-40% | Self-repair paper estimate |
| Structured format | ~40-50% | Hypothesis target |

### 8.2 Minimum Detectable Effect

- With N=390, α=0.05, power=0.80
- MDE ≈ 8% absolute difference
- Target effect (5%) slightly below MDE
- Mitigation: Increase sample size via error type stratification

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Low failure count | Use full EvalPlus suite, not subset |
| Information confound | Verify via H-M2 reconstruction test |
| Model ceiling | Stratify by error type difficulty |
| API cost overrun | Batch requests, cache responses |

---

## 10. Success Criteria Summary

**Pass (Gate Satisfied):**
- Structured > Raw with p < 0.05 (corrected)
- Absolute improvement ≥ 5%
- Consistent direction across all 3 models

**Fail (Gate Not Satisfied):**
- p ≥ 0.05 OR improvement < 5%
- Pipeline STOPS if gate fails

---

## 11. Output Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| Raw results | JSONL | results/h-e1/raw_results.jsonl |
| Statistical analysis | Markdown | results/h-e1/analysis.md |
| Figures | PNG | results/h-e1/figures/ |
| Checkpoint | YAML | results/h-e1/checkpoint.yaml |

---

*Generated by Phase 2C Experiment Design*
*Status: COMPLETE*
