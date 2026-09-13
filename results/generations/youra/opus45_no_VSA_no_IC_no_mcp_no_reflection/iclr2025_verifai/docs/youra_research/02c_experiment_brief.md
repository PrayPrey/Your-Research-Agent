# Experiment Brief: H-E1 Static Analyzer Signal Existence

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Date:** 2026-08-29

---

## 1. Hypothesis Statement

Static analyzers (pylint) produce meaningful, actionable warnings on LLM-generated code for at least 30% of HumanEval problems.

## 2. Variables

| Variable | Type | Description |
|----------|------|-------------|
| **IV** | Independent | Running pylint on LLM-generated code |
| **DV** | Dependent | Fraction of solutions with ≥1 warning (target: ≥30%) |
| **CV** | Control | Pylint config (severity filter: error+warning), HumanEval problems, base LLM |

## 3. Dataset Specification

| Attribute | Value |
|-----------|-------|
| **Name** | HumanEval |
| **Type** | standard |
| **Source** | OpenAI (huggingface: openai_humaneval) |
| **Size** | 164 problems |
| **Split** | Full test set (no train/val split needed for existence test) |

### Data Preparation Steps
1. Load HumanEval dataset via `datasets` library
2. Generate one solution per problem using base LLM (GPT-4 or CodeLlama-34B)
3. Extract function code from model output
4. Store solutions in standardized format for pylint analysis

## 4. Model Specification

| Attribute | Value |
|-----------|-------|
| **Name** | GPT-4 (primary) / CodeLlama-34B (secondary) |
| **Type** | LLM (code generation) |
| **Access** | OpenAI API / HuggingFace Transformers |
| **Temperature** | 0.0 (deterministic) |
| **Max tokens** | 512 |

## 5. Experimental Protocol

### 5.1 Procedure
```
For each problem in HumanEval (N=164):
    1. Generate solution using base LLM with standard prompt
    2. Extract function code from response
    3. Run pylint with severity filter (--fail-under=0 --disable=C,R)
    4. Record: problem_id, has_warning, warning_count, warning_types
```

### 5.2 Pylint Configuration
```ini
[MASTER]
fail-under = 0

[MESSAGES CONTROL]
# Disable convention (C) and refactor (R) - keep error (E) and warning (W)
disable = C, R

[FORMAT]
output-format = json
```

### 5.3 Success Metrics

| Metric | Formula | Threshold |
|--------|---------|-----------|
| **Warning prevalence** | solutions_with_warning / total_solutions | ≥0.30 |
| **Non-trivial ratio** | (E + W categories) / total_warnings | ≥0.50 |

## 6. Analysis Plan

### 6.1 Primary Analysis
- Count solutions with ≥1 pylint warning (E or W severity)
- Calculate warning prevalence rate
- 95% CI using Wilson score interval

### 6.2 Secondary Analysis
- Categorize warning types (undefined-variable, type-mismatch, etc.)
- Distribution of warnings per solution
- Correlation with problem difficulty (if available)

### 6.3 Visualization
- Histogram: warnings per solution
- Bar chart: warning type distribution
- Table: top-10 most frequent warning codes

## 7. Gate Criteria

| Outcome | Condition | Action |
|---------|-----------|--------|
| **PASS** | warning_prevalence ≥ 0.30 | Proceed to h-m1 |
| **FAIL** | warning_prevalence < 0.30 | Terminate chain - no signal to add |

## 8. Resource Estimates

| Resource | Estimate |
|----------|----------|
| **API calls** | 164 (one per problem) |
| **Compute time** | ~30 min (generation) + ~5 min (pylint) |
| **Cost** | ~$5-10 GPT-4 API |

## 9. Implementation Notes

### 9.1 Code Structure
```
src/
├── data/
│   └── humaneval_loader.py      # HumanEval dataset loading
├── generation/
│   └── llm_generator.py         # Solution generation
├── analysis/
│   └── pylint_runner.py         # Static analysis runner
└── experiments/
    └── h_e1_existence.py        # Main experiment script
```

### 9.2 Dependencies
- `datasets` (HuggingFace)
- `openai` (GPT-4 API)
- `pylint`
- `pandas`, `numpy`, `matplotlib`

## 10. Risks and Mitigations

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Low warning rate | Medium | Pilot on 50 problems first; adjust severity filter |
| API rate limits | Low | Use exponential backoff |
| Model output parsing | Medium | Robust extraction regex; manual validation on subset |

---

## Appendix: Sample Pylint Output Format

```json
{
  "problem_id": "HumanEval/0",
  "has_warning": true,
  "warning_count": 2,
  "warnings": [
    {
      "type": "E",
      "symbol": "undefined-variable",
      "message": "Undefined variable 'x'",
      "line": 5
    },
    {
      "type": "W",
      "symbol": "unused-variable",
      "message": "Unused variable 'result'",
      "line": 3
    }
  ]
}
```
