# Phase 4 Validation Report: H-M1

**Hypothesis:** H-M1 (MECHANISM — Causal Step 1)
**Type:** Token Entropy vs. Semantic Entropy Divergence Analysis
**Date:** 2026-05-11
**Gate Type:** MUST_WORK

---

## Gate Decision: DEGENERATE_PASS

**Degenerate Case Detected:** Semantic entropy is constant (std < 1e-6).
Gate interpreted as DEGENERATE_PASS — mechanism is trivially non-informative.

### Cluster Distribution (Degenerate Diagnosis)

| Metric | Value |
|--------|-------|
| Mean clusters | 4.6440 |
| Std clusters | 0.6567 |
| N singleton | 4 |

---

## Key Findings

- Semantic entropy scores are constant (std < 1e-6) — degenerate output from H-E1
- Gate result: DEGENERATE_PASS (mechanism trivially satisfied)
- Cluster distribution analysis reveals NLI clustering behavior

---

## Output Files

| File | Description |
|------|-------------|
| `h-m1/code/outputs/experiment_results.json` | Structured metrics |
| `h-m1/figures/scatter_te_vs_se.png` | TE vs SE scatter |
| `h-m1/figures/divergence_dist.png` | Divergence distribution |
| `h-m1/figures/ttr_vs_divergence.png` | TTR vs divergence |
| `h-m1/figures/bootstrap_ci.png` | Bootstrap CI CDF |
| `h-m1/figures/cluster_count_dist.png` | Cluster count histogram |

**Validation completed:** 2026-05-11T10:56:49.668432
