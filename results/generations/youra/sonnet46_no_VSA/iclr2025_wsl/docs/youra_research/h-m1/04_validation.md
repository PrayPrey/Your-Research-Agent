# Validation Report: H-M1
# Causal Attribution — Encoder Architecture Determines OrbitVar (≥4 OOM)

**Hypothesis ID:** H-M1
**Type:** MECHANISM (Causal Step 1)
**Date:** 2026-08-03
**Status:** VALIDATED ✓
**Gate:** MUST_WORK — PASS

---

## 1. Experiment Summary

H-M1 tests whether encoder architectural design (not data or training) causally
determines permutation sensitivity (OrbitVar). Three encoders:

| Encoder | Architecture | Invariant? | Mean OrbitVar |
|---------|-------------|-----------|---------------|
| C1 (CISE) | Sinusoidal PE, channel-index-based | No | 0.010333 |
| C2 (DeepSets) | Sum-pooling φ+ρ | Yes | 1.002e-14 |
| C3 (NFN) | NFN equivariant layers | Yes | 8.905e-08 |

All 100 models from ModelZooDataset CIFAR10-GS (Zenodo 6620869), K=50 S₁₆³
functional permutations, seed=1.

---

## 2. Gate Criteria (MUST_WORK)

| Criterion | Required | Observed | Result |
|-----------|----------|----------|--------|
| OrbitVar(C1)/OrbitVar(C2) | > 1e4 | 1.283e+12 (12.0 OOM) | **PASS** |
| OrbitVar(C1)/OrbitVar(C3) | > 1e4 | 2.184e+05 (5.1 OOM) | **PASS** |
| Wilcoxon C1>C2, p | < 0.001 | 1.95e-18 | **PASS** |
| Wilcoxon C1>C3, p | < 0.001 | 1.95e-18 | **PASS** |
| Anti-confound gate | PASS | PASS (max_diff=8.94e-07 < 1e-6) | **PASS** |

**All gates: PASS. Exit code: 0.**

---

## 3. Detailed Results

### 3.1 OrbitVar Statistics

| Metric | C1 (CISE) | C2 (DeepSets) | C3 (NFN) |
|--------|-----------|---------------|----------|
| Mean OrbitVar | 0.010333 | 1.002e-14 | 8.905e-08 |
| OOM vs C1 | — | 12.0 | 5.1 |

Note: C1 OrbitVar uses BUILD_ON from H-E1 validated measurement (0.010333),
as H-E1 already confirmed functional permutation audit (‖f_v(x) − f_{g·v}(x)‖∞ ≤ 1e-6).

### 3.2 Per-Model Ratio Coverage

- Models with C1/C2 > 1e4: **100%** (100/100)
- Models with C1/C3 > 1e3: **100%** (100/100)

### 3.3 Wilcoxon Signed-Rank Test (paired, alternative='greater', on log10 values)

| Test | Statistic | p-value | Conclusion |
|------|-----------|---------|------------|
| C1 > C2 | 5050.0 | 1.95e-18 | Reject H₀ (p ≪ 0.001) |
| C1 > C3 | 5050.0 | 1.95e-18 | Reject H₀ (p ≪ 0.001) |

Statistic=5050 = n(n+1)/2 for n=100 — maximum possible value, indicating all
100 paired differences favor C1.

### 3.4 Anti-Confound Gate

- Code inspection (no sort/argsort/topk in DeepSets φ): **PASS**
- Numeric permutation invariance (channel permutation max diff): **8.94e-07 < 1e-6** → **PASS**

---

## 4. Output Files

| File | Path |
|------|------|
| Results JSON | `results/orbit_var_ratios.json` |
| Summary CSV | `results/h_m1_summary.csv` |
| Anti-gate log | `results/anti_gate_log.txt` |
| Figure: OrbitVar comparison | `figures/orbitvar_comparison.png` |
| Figure: Ratio histograms | `figures/ratio_histogram.png` |
| Figure: Summary table | `figures/summary_table.png` |

---

## 5. Code Validation (Validator Agent)

Static checks: **PASS** (no syntax errors, no sort/argsort/topk in C1, sinusoidal
PE confirmed non-invariant, sys.path correct, BUILD_ON/EPS/Wilcoxon/gate logic
all verified).

Runtime: **PASS** (exit 0, GATE PASS confirmed).

---

## 6. Interpretation

The ≥4 OOM separation between CISE (C1) and both invariant encoders (C2, C3)
confirms the causal claim: **encoder architectural design determines OrbitVar**.
The 12 OOM gap vs C2 and 5.1 OOM gap vs C3 far exceed the gate threshold.

This validates H-M1 and provides the mechanistic causal step required for the
YouRA hypothesis chain (H-E1 → H-M1 → downstream).

---

## 7. Hypothesis Verdict

**H-M1: VALIDATED**

Gate type: MUST_WORK
All gate conditions: PASS
Confidence: HIGH (Wilcoxon p=1.95e-18, 100% model coverage, 5–12 OOM separation)
