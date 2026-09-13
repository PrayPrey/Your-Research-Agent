# Product Requirements Document: h-e1

**Hypothesis:** DNSI can be reliably computed from PapersWithCode SOTA histories using 6-month windowing and difficulty normalization (class count proxy)

**Type:** EXISTENCE (PoC Validation)
**Date:** 2026-08-28
**Author:** Anonymous

---

## Executive Summary

Validate that the Difficulty-Normalized Saturation Index (DNSI) metric can be reliably computed from archived PapersWithCode SOTA history data. This is a metric computation experiment (not ML model training) that tests whether DNSI produces valid, finite values for >50% of target benchmarks.

---

## Problem Statement

Benchmark saturation analysis requires a normalized metric that accounts for task difficulty. Raw entropy metrics are not comparable across benchmarks with different class counts. DNSI proposes normalizing observed entropy by expected entropy (log of difficulty proxy).

**Core Question:** Can DNSI be computed reliably from available PWC data?

---

## Functional Requirements

### FR-1: Data Acquisition
- Clone paperswithcode/paperswithcode-data repository
- Parse evaluation-tables.json for SOTA histories
- Filter benchmarks with >50 SOTA entries and >3 year history

### FR-2: DNSI Computation Pipeline
- Implement 6-month windowed improvement aggregation
- Compute Shannon entropy of improvement distribution
- Normalize by log(difficulty_proxy) where difficulty_proxy = class count
- Handle edge cases: insufficient data, single-class tasks

### FR-3: Baseline Metric Computation
- Raw Entropy (H): Unnormalized Shannon entropy
- Improvement Rate (IR): Mean accuracy gain per year
- Time Since Last SOTA (TSLS): Days since last improvement

### FR-4: Target Benchmark Coverage
| Benchmark | Domain | Difficulty Proxy |
|-----------|--------|------------------|
| ImageNet | Vision | 1000 |
| CIFAR-10 | Vision | 10 |
| CIFAR-100 | Vision | 100 |
| MNIST | Vision | 10 |
| GLUE | NLP | varies |
| SQuAD | NLP | vocab_size |
| WMT En-De | Translation | vocab_size |
| COCO Detection | Vision | 80 |

### FR-5: Visualization
- Bar chart: DNSI computation success rate vs 50% threshold
- Histogram: DNSI value distribution
- Scatter: DNSI vs Raw Entropy comparison

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Deterministic computation (no randomness)
- Single seed: 1

### NFR-2: Performance
- Complete computation in <5 minutes for all target benchmarks

### NFR-3: Data Integrity
- Use archived PWC data (July 2025 snapshot)
- No external API dependencies during computation

---

## Success Criteria

| Metric | Threshold | Gate Type |
|--------|-----------|-----------|
| Computation Success Rate | >50% of target benchmarks | MUST_WORK |
| Value Range Validity | 100% in [0, 2] | MUST_WORK |
| Benchmark Coverage | ≥8 benchmarks attempted | Informational |

---

## Dependencies

- scipy.stats.entropy
- numpy
- pandas (for windowing)
- matplotlib (for visualization)
- paperswithcode-data repository (git clone)

---

## Out of Scope

- ML model training
- Generalization gap prediction (future hypothesis)
- Real-time PWC API access (archived data only)
