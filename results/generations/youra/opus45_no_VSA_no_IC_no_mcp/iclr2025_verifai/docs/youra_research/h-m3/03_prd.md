# Product Requirements Document: H-M3

**Hypothesis:** Fix specificity shows inverted-U pattern: Levels 1-2 (general strategy, specific pattern) achieve higher repair success than both Level 0 (no hint) and Level 3 (exact fix), with significant quadratic contrast

**Date:** 2026-08-28
**Author:** Anonymous
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## 1. Executive Summary

This experiment tests whether intermediate fix specificity levels (1-2) optimize code repair success compared to no hints (level 0) or exact fixes (level 3), following scaffolding theory's inverted-U prediction.

## 2. Problem Statement

Self-repair systems provide error feedback to LLMs, but the optimal specificity of fix hints is unknown. Too little guidance leaves models stuck; too much (exact solutions) may reduce model engagement and learning transfer. We hypothesize intermediate specificity achieves optimal repair.

## 3. Functional Requirements

### FR-1: Fix Specificity Hint Generator
Generate hints at 4 levels:
- Level 0: No hint (baseline)
- Level 1: Strategy hint ("check boundary conditions")
- Level 2: Pattern hint ("use try-except for IndexError")
- Level 3: Exact fix ("change line 5 to: if i < len(arr):")

### FR-2: Repair Loop with Structured Feedback
Extend H-E1 structured error format with fix specificity parameter.
- Max 3 repair iterations
- Temperature 0.0 (deterministic)
- Track per-iteration success

### FR-3: Model Inference Pipeline
Support 3 models:
- CodeLlama-7B-Instruct (HuggingFace)
- CodeLlama-34B-Instruct (HuggingFace)
- GPT-4-turbo (OpenAI API)

### FR-4: Evaluation on EvalPlus
Run on both benchmarks:
- HumanEval+: 164 problems, 80x test coverage
- MBPP+: 378 problems, 35x test coverage

### FR-5: Statistical Analysis
Polynomial contrast model for inverted-U:
```
success ~ level + level^2 + (1|error_id) + (1|model)
```
Test quadratic term significance (p < 0.05).

### FR-6: Ablation Conditions
All 4 levels tested per error instance:
- Within-subject design
- Randomized order per error
- 3 repetitions for variance

## 4. Data Specification

### Primary Dataset
- **Name:** EvalPlus (HumanEval+, MBPP+)
- **Source:** https://github.com/evalplus/evalplus
- **Loading:** `pip install evalplus`, Python API
- **Sample Size:** ~500 error instances per model (30% failure rate estimate)

### Data Flow
1. Generate initial code with base model
2. Collect failures via evalplus execution
3. Filter to repairable errors (syntax, type, runtime, semantic)
4. Apply 4 fix specificity levels per error
5. Record repair success per level

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Temperature 0.0 for deterministic outputs
- Fixed random seeds for ordering
- 3 repetitions per condition

### NFR-2: Scalability
- Support batch inference for CodeLlama
- Rate limiting for GPT-4 API
- Estimated runtime: ~24 hours total

### NFR-3: Resource Requirements
- GPU: 1x A100 (40GB) for CodeLlama-34B
- Storage: ~50GB for model caches
- API: OpenAI API key for GPT-4

## 6. Success Criteria

### Primary Gate (SHOULD_WORK)
1. Quadratic term (level^2) has negative coefficient (inverted-U shape)
2. Quadratic term significant at p < 0.05
3. Peak performance at Level 1 or 2

### Secondary Criteria
- Level 1-2 > Level 0 (better than no hint)
- Level 1-2 > Level 3 (better than exact fix)
- Effect consistent across models

## 7. Dependencies

### 7.1 Python Packages
```
evalplus>=0.2.0
transformers>=4.35.0
torch>=2.0.0
openai>=1.0.0
scipy>=1.10.0
statsmodels>=0.14.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### 7.2 External References
- H-E1 structured error format (prerequisite)
- theoxo/self-repair framework (reference)
- evalplus/evalplus benchmark

### 7.3 API Keys
- OPENAI_API_KEY for GPT-4-turbo

## 8. Visualization Requirements

### Required Figure
- **Gate Metrics**: Repair success rate by fix specificity level (bar chart)
- X: Level (0, 1, 2, 3)
- Y: Success Rate (%)
- Expected: Inverted-U shape

### Additional Figures
1. Polynomial fit overlay (inverted-U curve)
2. Success by Level × Model heatmap
3. Success by Level × Error Type
4. Iterations to success per level

---

*Phase 3 PRD for H-M3 | Next: Architecture Design*
