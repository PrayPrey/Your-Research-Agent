# Product Requirements Document: H-C1

**Hypothesis:** High feedback diversity H(Schema|ErrorClass)>2.5 bits necessary for superadditivity
**Date:** 2026-08-08
**Type:** CONDITION
**Gate:** SHOULD_WORK

---

## 1. Objective

Test whether high feedback diversity (measured by conditional entropy H(Schema|ErrorClass) > 2.5 bits) is a **necessary condition** for the Training×Refinement superadditive interaction effect observed in H-E1.

## 2. Success Criteria

| Criterion | Metric | Threshold |
|-----------|--------|-----------|
| Primary | Interaction(High) - Interaction(Low) | > 0 (measurable gap) |
| Secondary | H manipulation verified | High > 2.5, Low < 1.5 bits |
| Code | Exit code | 0 |

## 3. Experimental Design

### 3.1 Conditions (2×2 with Diversity Manipulation)

| Condition | Training | Refinement | Feedback Diversity |
|-----------|----------|------------|-------------------|
| RL-High-Refine | RL | K=3 | H > 2.5 bits |
| RL-Low-Refine | RL | K=3 | H < 1.5 bits |
| RL-High-Single | RL | None | H > 2.5 bits |
| RL-Low-Single | RL | None | H < 1.5 bits |

### 3.2 Core Mechanism

FeedbackDiversityController that filters training batches to achieve target entropy:
- High diversity: oversample minority error types → H > 2.5
- Low diversity: concentrate on dominant error type → H < 1.5

### 3.3 Model & Data

- **Model:** CodeT5+-base (Salesforce/codet5p-220m)
- **Datasets:** HumanEval+ (164), MBPP+ (500+)
- **Evaluation:** pass@1 via evalplus

## 4. Deliverables

| Artifact | Description |
|----------|-------------|
| `results.json` | Raw experimental results |
| `results.csv` | Tabular results |
| `figures/interaction_vs_entropy.png` | Gate metrics figure |
| `04_validation.md` | Validation report |

## 5. Constraints

- Single seed (CONDITION hypothesis)
- Reuse H-E1 infrastructure where applicable
- 10 epochs critic training, then RL finetuning

## 6. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Cannot achieve H > 2.5 | Extend error taxonomy beyond 4 types |
| No difference in interaction | Document as negative result (diversity not necessary) |

## 7. Dependencies

- H-E1 validated (COMPLETE)
- evalplus library
- CodeT5+ pretrained weights
