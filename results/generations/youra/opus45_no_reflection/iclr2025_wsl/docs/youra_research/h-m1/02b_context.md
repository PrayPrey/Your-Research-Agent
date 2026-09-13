# Phase 2B Context: H-M1

**Hypothesis ID:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK

## Hypothesis Statement

Under Small CNN Zoo scope, if we extract features from weight matrices, then these features will correlate with class-wise accuracy profiles, because weights encode functionally salient directions per Meynent et al.

## Rationale

Tests first causal step: weights contain behavioral information extractable by any method, not just NF-Layers.

## Variables

- **Independent:** Weight feature extraction method
- **Dependent:** Correlation with class-wise accuracy
- **Controlled:** Model architecture, dataset

## Verification Protocol

1. Extract basic weight statistics (mean, std, norms per layer)
2. Train linear probe to predict class-wise accuracy from weight features
3. Compare R² against stratified baseline (overall accuracy + per-class difficulty)
4. Test: R² > stratified baseline R²

## Success Criteria (PoC)

- **Primary:** Weight features predict class-wise accuracy better than stratified baseline
- **Secondary:** Multiple weight statistics contribute to prediction

## Failure Response

- IF fails: PIVOT to alternative feature extraction

## Prerequisites

- H-E1: COMPLETED (PASSED)
  - Result: residual_ratio = 0.6758 > threshold 0.05
  - Validated at: 2026-08-19T01:52:00+00:00

## Gate Condition

- Type: MUST_WORK
- Failure Action: STOP workflow

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Small CNN Zoo (CIFAR-10 subset) | Contains ~3000 models with stored predictions |
| **Model** | Linear probe on weight statistics | Minimal mechanism test before NF-Layer |

## Dataset Details

- Source: github.com/HSG-AIML/model_zoos
- Path: model_zoos/CIFAR10_small_cnn/
- Models: ~3000 CNNs with varying hyperparameters/seeds

## Continuation Context

Building on H-E1 success (residual_ratio = 0.6758), we now test whether weight features can predict the observed class-wise variance. H-E1 established behavioral variance exists; H-M1 tests whether weights encode it.
