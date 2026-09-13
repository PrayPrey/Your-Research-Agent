# Phase 2B Context: H-E1

**Generated:** 2026-08-19
**Source:** 02b_verification_plan.md (JIT extraction)

---

## Hypothesis Information

- **ID:** H-E1
- **Type:** EXISTENCE
- **Title:** Behavioral Information Exists Beyond Accuracy
- **Statement:** Under CNN model zoo scope, if we analyze class-wise accuracy profiles across models, then variance beyond overall accuracy will be observed, because different models encode different behavioral patterns in their weights.

## Gate Condition

- **Type:** MUST_WORK
- **Failure Action:** STOP - behavioral prediction meaningless if no behavioral variance exists

## Success Criteria (PoC)

- **Primary:** Class-wise variance NOT fully explained by overall accuracy
- **Secondary:** Different models show different per-class error patterns
- **Quantitative:** Residual variance > 5% of total variance

## Verification Protocol

1. Load Small CNN Zoo (~3000 models) stored predictions
2. Compute class-wise accuracy profiles for each model
3. Calculate variance explained by overall accuracy vs. residual per-class variance
4. Test: residual variance > 5% of total variance

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Small CNN Zoo (CIFAR-10 subset) | Contains ~3000 models with stored predictions |
| **Source** | github.com/HSG-AIML/model_zoos | Path: model_zoos/CIFAR10_small_cnn/ |

## Variables

- **Independent:** Model identity (different hyperparameters/seeds)
- **Dependent:** Class-wise accuracy profile variance
- **Controlled:** Architecture (fixed CNN), Dataset (CIFAR-10)

## Dependencies

- **Prerequisites:** None (foundation hypothesis)

## Risk Factors

- **R1 (Critical):** No meaningful class-wise variance in model zoo
- **Mitigation:** Early variance check on subset of 100 models first
