# Product Requirements Document: H-C1

**Hypothesis:** SA-correctness correlation generalizes across 3+ LLMs with variance std(r) < 0.15, demonstrating model-agnostic predictive signal.

**Date:** 2026-08-24
**Author:** Anonymous
**Type:** CONDITION (SHOULD_WORK Gate)
**Prerequisite:** H-M1 (VALIDATED)

---

## 1. Executive Summary

Validate that the SA-correctness correlation discovered in H-M1 (pylint r=0.873, radon_cc r=-0.569) generalizes across multiple LLMs. Success requires std(r) < 0.15 across 4 models, demonstrating model-agnostic predictive signal.

## 2. Problem Statement

H-M1 established SA metrics correlate with code correctness on a single model's outputs. For this signal to be useful in practice, it must generalize across different LLMs. If correlation varies wildly between models (high std(r)), the signal lacks model-agnostic utility.

## 3. Scope

### In Scope
- Collect code completions from 4 LLMs (GPT-4, Claude-3, CodeLlama-70B, Codestral)
- Run SA metrics (pylint_score, radon_cc) on each completion
- Execute test cases to determine pass/fail
- Compute per-model partial correlations (LOC-controlled)
- Calculate cross-model variance std(r)

### Out of Scope
- Training any ML models
- New SA metric development
- Real-time inference systems

## 4. Data Specification

### 4.1 Primary Datasets

| Dataset | Source | Size | Download |
|---------|--------|------|----------|
| HumanEval | `openai/openai_humaneval` | 164 problems | HuggingFace (auto) |
| MBPP-sanitized | `google-research-datasets/mbpp` | 257 problems | HuggingFace (auto) |

**Total:** 421 problems per model = 1,684 code samples total

### 4.2 Multi-Model Code Completions

| Model | Source | Samples |
|-------|--------|---------|
| GPT-4 | OpenAI API or cached | 421 |
| Claude-3 (Sonnet) | Anthropic API or cached | 421 |
| CodeLlama-70B | HuggingFace Inference | 421 |
| Codestral | Mistral API or cached | 421 |

**Data Schema:**
```
task_id: str
model_id: str (gpt4|claude3|codellama|codestral)
code: str
passed: int (0|1)
pylint_score: float
radon_cc: float
loc: int
```

### 4.3 Preprocessing
- Reuse H-M1 SA extraction pipeline
- Add model_id column for groupby operations
- Same LOC counting method as H-M1

## 5. Functional Requirements

### FR-1: Multi-Model Data Collection
Load or generate code completions for all 4 models on HumanEval + MBPP.

### FR-2: SA Metric Extraction
Run pylint and radon on each completion, extract scores.

### FR-3: Test Execution
Execute test cases for each completion, record pass/fail.

### FR-4: Per-Model Correlation
Compute partial correlation (LOC-controlled) for each model separately.

### FR-5: Cross-Model Variance
Calculate std(r) across the 4 per-model correlations.

### FR-6: Gate Evaluation
Report PASS if std(r) < 0.15, else FAIL.

### FR-7: Visualization
Generate per-model correlation bar chart with mean ± std.

## 6. Non-Functional Requirements

### NFR-1: Execution Time
Complete analysis within 4 hours (dominated by API calls if generating completions).

### NFR-2: Reproducibility
All random seeds fixed. Cached completions preferred.

### NFR-3: Statistical Rigor
Report p-values for each per-model correlation.

## 7. Dependencies

### 7.1 Python Packages
```
scipy>=1.10.0
pingouin>=0.5.3
pandas>=2.0.0
numpy>=1.24.0
datasets>=2.14.0
pylint>=3.0.0
radon>=6.0.0
matplotlib>=3.7.0
```

### 7.2 External References
- H-M1 codebase: `docs/youra_research/h-m1/code/`
  - `sa_tools.py`: Pylint/radon wrappers
  - `correlate.py`: Partial correlation
  - `dataset.py`: HumanEval/MBPP loading

### 7.3 API Access (Optional)
- OpenAI API key (if generating GPT-4 completions)
- Anthropic API key (if generating Claude-3 completions)
- HuggingFace token (for CodeLlama inference)
- Mistral API key (for Codestral)

## 8. Success Criteria

### Primary (Gate)
- **std(r) < 0.15** across 4 models for pylint_score metric

### Secondary
- mean(r) > 0.35 (consistent with H-M1 threshold)
- All per-model p-values < 0.05
- min(r) > 0.20 (no model shows weak correlation)

## 9. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limits | Use cached completions |
| Model unavailability | Minimum 3 models required |
| High variance due to model quality | Report per-model breakdown |

## 10. Timeline

| Phase | Duration |
|-------|----------|
| Data collection | 2 hours (with caching) |
| SA extraction | 1 hour |
| Correlation analysis | 30 min |
| Visualization | 30 min |

---

*Generated from Phase 2C Experiment Brief*
