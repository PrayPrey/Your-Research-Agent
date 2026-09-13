# Phase 2B Context: h-m4

**Hypothesis ID:** h-m4
**Type:** MECHANISM
**Status:** IN_PROGRESS

---

## Hypothesis Statement

Under ML reengineering workflows with CI + Contracts deployed, if contracts execute at environment-setup time, then defect detection shifts from training-stage (median 68% per Jiang et al.) to environment-stage, with ≥5-hour earlier median time-to-first-failure compared to CI-only baseline.

---

## Rationale

Tests the final causal step and key outcome. Lifecycle shift is the practical benefit — earlier detection saves researcher time and enables faster debugging.

---

## Variables

- **Independent:** Validation strategy (No-CI / CI-only / CI+Contracts)
- **Dependent:** Time-to-first-failure (hours), stage-of-first-failure (environment vs. training)
- **Controlled:** Repository maturity, reporter type

---

## Verification Protocol

1. Conduct randomized PR-level trial on live GitHub repos (≥1K stars CV repos)
2. Stratify by repo maturity and reporter type (58% re-users per Jiang et al.)
3. Measure time-to-first-failure from CI log timestamps
4. Measure stage-of-first-failure (environment vs. training)
5. Calculate marginal detection improvement: CI+Contracts vs. CI-only

---

## Success Criteria

- **Primary:** Median time-to-first-failure reduced by ≥5 hours with CI+Contracts vs. CI-only
- **Secondary:** CI+Contracts detects ≥25% more environment-stage API defects than CI-only (marginal improvement)

---

## Gate Condition

- **Type:** SHOULD_WORK
- **Pass Condition:** Lifecycle shift ≥5h, marginal detection ≥25%
- **Fail Action:** If lifecycle shift <3h, insufficient practical impact — document as incremental improvement

---

## Prerequisites

- **h-m3:** Composition-level contracts validate binding assumptions across library interactions (COMPLETED)

---

## Experimental Setup (from Phase 2B Section 1.3)

### Dataset
- **Source:** Jiang et al. 348-Defect Corpus + Live GitHub Repos (standard + real-world)
- **Justification:** Jiang et al. provides ecological validity (real reengineering defects); live trial tests marginal value in practice
- **Path:** 
  - Phase 1: Retrospective coding
  - Phase 2: Version-Transition Benchmark
  - Phase 3: Randomized trial on live repos

### Model
- **Type:** API contract validation framework
- **Source:** Pre-built library for PyTorch/HuggingFace/JAX + auto-generation pipeline
- **Note:** Contracts are the 'model' — hypothesis tests their defect detection efficacy

---

## Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| No-CI (Control) | Version pinning only, no automated testing | Mirrors 75% of ML repos per Wolter et al. |
| CI-Only (Best-Practice Baseline) | pytest + integration tests + version pinning | Current best practice |
| Execution-Only (Adversarial Baseline) | Import + minimal forward pass | Catches obvious crashes, not subtle invariant violations |

---

## Dependency Chain

```
h-e1 → h-m1 → h-m2 → h-m3 → h-m4 (current)
```

---

## Source

Phase 2A Causal Step 4, Predictions P2 & P3
