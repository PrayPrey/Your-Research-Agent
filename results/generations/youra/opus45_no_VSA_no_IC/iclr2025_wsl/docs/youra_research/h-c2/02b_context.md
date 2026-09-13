# Phase 2B Context: H-C2

**Hypothesis ID:** H-C2
**Type:** CONDITION
**Statement:** Crossing point N* where NFN matches Statistics R² exists at N* < 2500

## Gate Condition

**Type:** SHOULD_WORK
**Target:** Find N* where NFN R² ≈ Statistics R² at N* < 2500

## Prerequisites

- **H-M2:** VALIDATED - NFN R²=0.9985 vs MLP R²=-1.50 at N=500

## Experimental Setup

From Phase 2B roadmap:
- **Dataset:** CIFAR-10 
- **Architecture:** ResNet-20 (homogeneous model zoo)
- **Training sizes:** N ∈ {100, 250, 500, 1000, 2500, 5000}
- **Test size:** 500 held-out models (fixed)
- **Seeds:** 10 per (N, method) pair
- **Methods:** NFN, Statistics baseline

## Baseline & Comparison

- **Statistics baseline:** Weight statistics (mean, std, norms per layer)
- **NFN:** Permutation-equivariant Neural Functional Networks
- **Goal:** Find crossing point where learned features match handcrafted

## Success Criteria

- Identify N* where |NFN R² - Statistics R²| < 0.03
- N* must be < 2500
- Statistically significant with confidence intervals

## Key Context from H-M2

- NFN achieves near-perfect R²=0.9985 at N=500
- Statistics baseline expected to be stable across N
- NFN likely improves faster with more data due to learned representations
