# Experiment Brief: h-c1 Format × Model Scale Interaction

**Hypothesis ID:** h-c1
**Type:** CONDITION
**Gate:** SHOULD_WORK
**Prerequisite:** h-e1 (VALIDATED)
**Date:** 2026-08-28

---

## 1. Hypothesis Statement

Format benefits are larger for smaller models: Format × Model Scale interaction is significant with larger effect sizes for CodeLlama-7B than CodeLlama-34B than GPT-4.

**Prediction:** Structured error format improves repair success more for smaller models (7B > 34B > GPT-4), suggesting smaller models benefit more from representational alignment.

---

## 2. Experimental Design

### 2.1 Design Type
**2×3 Factorial Design**
- Factor A: Format (Raw, Structured)
- Factor B: Model Scale (CodeLlama-7B, CodeLlama-34B, GPT-4)

### 2.2 Variables

| Variable | Type | Levels |
|----------|------|--------|
| Error Format | IV | Raw, Structured |
| Model Scale | IV | 7B, 34B, ~100B+ |
| Repair Success Rate | DV | Binary (0/1) per sample |
| Information Content | CV | Controlled (same errors) |
| Temperature | CV | Fixed (0.0) |
| Max Repair Iterations | CV | Fixed (3) |

### 2.3 Sample Size Calculation

**Per Cell:** 
- Full HumanEval+ test set: 164 problems
- Full MBPP+ test set: 378 problems
- Total: 542 problems per model

**Expected Failures (for repair testing):**
- CodeLlama-7B: ~60% failure rate → ~325 samples
- CodeLlama-34B: ~40% failure rate → ~217 samples  
- GPT-4: ~15% failure rate → ~81 samples

**Minimum per cell for interaction test:** 80+ samples (GPT-4 is limiting factor)

**Total samples:** ~1,246 repair attempts (2 formats × 3 models × failure counts)

---

## 3. Dataset Specification

### 3.1 Primary Dataset
**Name:** EvalPlus (HumanEval+ and MBPP+)
**Type:** standard
**Source:** https://github.com/evalplus/evalplus
**License:** MIT

### 3.2 Dataset Preparation
1. Download EvalPlus dataset via `evalplus` package
2. Run initial code generation with each model
3. Collect static analysis errors from failures
4. Apply both format conditions to each error
5. Ensure same error samples tested across all conditions

### 3.3 Error Collection Protocol
```python
# Pseudocode for error collection
for problem in evalplus_problems:
    for model in [codellama_7b, codellama_34b, gpt4]:
        code = model.generate(problem.prompt)
        result = static_analyzer.check(code, problem.tests)
        if result.has_errors:
            errors.append({
                'problem_id': problem.id,
                'model': model.name,
                'code': code,
                'errors': result.errors,
                'error_types': classify_errors(result.errors)
            })
```

---

## 4. Model Specification

| Model | Parameters | Source | Access |
|-------|------------|--------|--------|
| CodeLlama-7B | 7B | HuggingFace | Local inference |
| CodeLlama-34B | 34B | HuggingFace | Local inference |
| GPT-4 | ~100B+ | OpenAI API | API calls |

### 4.1 Inference Configuration
```yaml
temperature: 0.0
max_tokens: 1024
max_repair_iterations: 3
stop_sequences: ["```"]
```

---

## 5. Format Conditions

### 5.1 Raw Format (Control)
Direct compiler/static analyzer output:
```
TypeError: 'NoneType' object is not subscriptable
  File "solution.py", line 12, in solve
    return arr[0]
```

### 5.2 Structured Format (Treatment)
```
PROBLEM: Type error in array access
LOCATION: Line 12, function solve()
CONTEXT: Attempting to index variable 'arr'
ROOT CAUSE: Variable 'arr' may be None when accessed
```

---

## 6. Statistical Analysis Plan

### 6.1 Primary Analysis
**Two-way ANOVA with interaction term**
```
repair_success ~ format * model_scale
```

**Hypothesis tests:**
1. Main effect of format: F-test
2. Main effect of model scale: F-test  
3. **Interaction effect (primary):** F-test for format × model_scale

### 6.2 Planned Contrasts
Test monotonic interaction pattern:
- Effect_7B > Effect_34B
- Effect_34B > Effect_GPT4

**Contrast coding:**
```
Model: [-1, 0, 1] for linear trend
Format: [-0.5, 0.5] for Raw vs Structured
```

### 6.3 Effect Size Metrics
- η² (eta-squared) for interaction
- Cohen's d per model level
- 95% CI for each simple effect

### 6.4 Significance Criteria
- α = 0.05 (BH-FDR corrected)
- Significant interaction: p < 0.05
- Pattern confirmation: Effect_7B > Effect_34B > Effect_GPT4

---

## 7. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Interaction significance | p < 0.05 | Format × Scale F-test |
| Effect ordering | 7B > 34B > GPT-4 | Simple effects comparison |
| η² for interaction | > 0.01 | Partial eta-squared |

**Pass condition:** Significant interaction AND correct effect ordering

---

## 8. Implementation Reuse

h-c1 reuses h-e1 infrastructure:
- Error parser and formatter from h-e1
- Self-repair loop implementation from h-e1
- EvalPlus dataset loading from h-e1
- Model inference wrappers from h-e1

**New components needed:**
- Interaction analysis module (ANOVA)
- Effect size calculator
- Contrast coding for ordered hypothesis

---

## 9. Baseline Comparison

| Condition | Expected Pass@1 | Expected Repair Rate |
|-----------|-----------------|---------------------|
| CodeLlama-7B + Raw | ~40% | ~10-15% |
| CodeLlama-7B + Structured | ~40% | ~20-30% |
| CodeLlama-34B + Raw | ~60% | ~15-20% |
| CodeLlama-34B + Structured | ~60% | ~22-28% |
| GPT-4 + Raw | ~85% | ~25-30% |
| GPT-4 + Structured | ~85% | ~28-32% |

**Expected interaction pattern:** Larger Δ for smaller models

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Low GPT-4 failure count | Pool similar problems, supplement with MBPP+ |
| Ceiling effect on GPT-4 | Focus on Type/Semantic errors |
| Unequal cell sizes | Use Type III SS in ANOVA |
| Model API instability | Cache all generations |

---

## 11. Execution Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Data collection | 1 day | Run all models on EvalPlus |
| Error formatting | 0.5 day | Apply both formats |
| Repair runs | 2 days | Run repairs for all conditions |
| Analysis | 0.5 day | ANOVA, effect sizes, plots |

**Total:** 4 days

---

## 12. Deliverables

1. `results/h-c1_interaction_analysis.json` - Raw results
2. `results/h-c1_anova_summary.md` - Statistical summary
3. `figures/h-c1_interaction_plot.png` - Format × Scale visualization
4. `04_validation_h-c1.md` - Final validation report

---

*Generated by Phase 2C Experiment Design*
*Hypothesis: h-c1 (CONDITION)*
*Status: COMPLETE*
