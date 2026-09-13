# Product Requirements Document: H-M1

**Date:** 2026-08-24
**Hypothesis:** TruthfulQA specifically measures resistance to popular misconceptions (imitative falsehoods), a capability distinct from general knowledge retrieval measured by MMLU.
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## 1. Problem Statement

H-E1 established moderate correlations exist among hallucination benchmarks. H-M1 tests whether TruthfulQA measures a distinct construct from MMLU by comparing inter-benchmark correlation to intra-benchmark (MMLU subtask) correlation.

---

## 2. Success Criteria

### Gate Condition
1. r(TruthfulQA, MMLU) < r(MMLU subtasks internal mean)
2. At least 1 divergent profile model exists (high MMLU z>1, low TruthfulQA z<0)

### Metrics
- **Primary:** Spearman correlation r(TruthfulQA, MMLU)
- **Secondary:** Mean pairwise MMLU subtask correlation
- **Tertiary:** Count of divergent profile models

---

## 3. Scope

### In Scope
- Retrieve MMLU per-subject scores for N=50 models from H-E1
- Compute TruthfulQA-MMLU correlation
- Compute mean MMLU internal correlation
- Identify divergent profile models
- Generate comparison visualizations

### Out of Scope
- Running new model evaluations (use published scores)
- Error pattern analysis (future hypothesis)
- Model training

---

## 4. Data Requirements

### Input Data
1. **H-E1 Model Population:** N=50 models with TruthfulQA scores
2. **MMLU Overall Scores:** Per-model average MMLU
3. **MMLU Subject Scores:** 57 subject-level scores per model

### Data Sources
- Primary: Open LLM Leaderboard (huggingface.co/datasets/open-llm-leaderboard/results)
- Fallback: lm-evaluation-harness if subjects unavailable

---

## 5. Technical Requirements

### Dependencies
- pandas >= 2.0
- scipy >= 1.11
- numpy >= 1.24
- matplotlib >= 3.8

### Computational Resources
- Minimal: Correlation analysis only
- Estimated runtime: < 1 minute

---

## 6. Deliverables

1. `run_experiment.py` - Main experiment script
2. `results/h_m1_results.json` - Correlation analysis results
3. `figures/gate_comparison.png` - Required visualization
4. `04_validation.md` - Validation report

---

## 7. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| MMLU subject scores unavailable | Medium | Use lm-eval-harness on subset |
| <50 models have full data | Low | Analyze available subset |
| TruthfulQA version mismatch | Low | Standardize on MC2 format |

---

## 8. Timeline

| Phase | Duration |
|-------|----------|
| Data collection | 5 min |
| Analysis | 1 min |
| Visualization | 2 min |
| Validation | 5 min |

**Total:** ~15 minutes execution time

---

*PRD generated from 02c_experiment_brief.md*
