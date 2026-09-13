# H-M2 Validation Report: Calibration-Alignment Divergence Gap

**Hypothesis ID:** H-M2
**Type:** MECHANISM (PoC — INCREMENTAL from H-M1)
**Gate Type:** MUST_WORK
**Gate Result:** PASS
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

---

## 1. Summary

H-M2 verifies that the calibration-alignment divergence gap (RM_norm − gold_preference), computed by applying min-max normalization to H-M1's validated output, is strictly positive at high-KL levels and grows monotonically with optimization pressure. Both primary gate conditions are satisfied.

**Gate Decision: PASS**
- `n_positive_high_kl = 5/5` ≥ threshold 3 ✓
- `rho_gap_kl = 1.000` > threshold 0 ✓

---

## 2. Hypothesis Statement

Under Coste et al. 2023 experimental data, if RM score is normalized to [0,1] range and gold preference rate is expressed as a fraction, then the calibration-alignment divergence gap (normalized RM score minus gold preference rate) is strictly positive at high KL levels and grows with increasing optimization pressure, because proxy-gold decoupling (confirmed in H-M1) creates a widening measurement gap.

---

## 3. Experiment Setup

### 3.1 Data

| Field | Value |
|-------|-------|
| Source | `h-m1/results/h_m1_divergence_curve.csv` (H-M1 validated output) |
| N | 10 KL-level observations |
| KL range | 0.0 – 8.0 nats |
| RM score range (raw) | [0.12, 2.08] |
| Gold preference range | [0.38, 0.63] |

### 3.2 Normalization

Min-max normalization applied to RM score:
```
rm_norm = (rm - 0.12) / (2.08 - 0.12)
```
- `rm_min = 0.12`, `rm_max = 2.08`
- `rm_norm[0] = 0.000` (KL=0), `rm_norm[-1] = 1.000` (KL=8)

### 3.3 Gap Computation

```
gap = rm_norm - gold_preference
```

High-KL subset: `kl > median_kl = 3.5` → KL ∈ {4, 5, 6, 7, 8} (N=5)

### 3.4 Environment

| Parameter | Value |
|-----------|-------|
| Conda env | youra-h-m2 |
| Python | 3.10 |
| GPU | 5× NVIDIA H100 NVL (available; not required for this experiment) |
| Runtime | < 1 second |

---

## 4. Results

### 4.1 Normalized Gap Values

| KL Budget | rm_score | rm_norm | gold_preference | gap |
|-----------|----------|---------|-----------------|-----|
| 0.0 | 0.12 | 0.0000 | 0.52 | -0.5200 |
| 0.5 | 0.48 | 0.1837 | 0.58 | -0.3963 |
| 1.0 | 0.81 | 0.3520 | 0.61 | -0.2580 |
| 2.0 | 1.24 | 0.5714 | 0.63 | -0.0586 |
| 3.0 | 1.55 | 0.7296 | 0.61 | +0.1196 |
| **4.0** | **1.78** | **0.8469** | **0.57** | **+0.2769** |
| **5.0** | **1.92** | **0.9184** | **0.53** | **+0.3884** |
| **6.0** | **2.01** | **0.9643** | **0.48** | **+0.4843** |
| **7.0** | **2.06** | **0.9898** | **0.43** | **+0.5598** |
| **8.0** | **2.08** | **1.0000** | **0.38** | **+0.6200** |

Bold rows = high-KL levels (KL > 3.5)

### 4.2 Gate Metrics

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| `n_positive_high_kl` | 5 | ≥ 3 | **PASS** |
| `rho_gap_kl` | 1.000 | > 0 | **PASS** |
| `p_rho_gap` | 6.6e-64 | — | (highly significant) |
| `max_gap` | 0.620 | > 0 | PASS (secondary) |
| `mean_gap_high_kl` | 0.466 | > 0 | PASS (secondary) |
| `prop_positive` | 0.60 | > 0.5 | PASS (secondary) |

### 4.3 H-M2 Gate Condition

**Primary Gate: PASS (both conditions satisfied)**
- Condition 1: `n_positive_high_kl = 5 >= 3` ✓
- Condition 2: `rho_gap_kl = 1.000 > 0` ✓

---

## 5. Generated Figures

| Figure | File | Description |
|--------|------|-------------|
| Gap Curve | `figures/gap_curve.png` | Divergence gap vs KL; zero line; shaded positive region; max_gap annotated |
| Dual Line | `figures/dual_line.png` | RM_norm and gold on [0,1] axis; crossover annotated |
| Gap Scatter | `figures/gap_scatter.png` | Scatter gap vs KL; Spearman ρ=1.000; OLS trend |
| Gate Metrics | `figures/gate_metrics.png` | Bar chart: gate metrics vs thresholds (all green = PASS) |

All 4 figures generated successfully.

---

## 6. Output Files

| File | Path |
|------|------|
| Results JSON | `results/h_m2_results.json` |
| Normalized gap CSV | `results/h_m2_normalized_gap.csv` |
| Figures (4 PNG) | `figures/` |
| Code | `code/` |

---

## 7. Interpretation

The calibration-alignment divergence gap is strictly positive at all 5 high-KL levels (KL ∈ {4,5,6,7,8}), with values ranging from +0.277 to +0.620. The Spearman rank correlation between KL budget and gap is ρ=1.000 (p=6.6e-64), confirming perfect monotonic growth. This formalizes H-M1's raw divergence result: in normalized [0,1] space, the proxy RM score strictly exceeds the gold preference rate under high optimization pressure, and this gap grows monotonically with KL budget. The result establishes the calibration-alignment divergence as a well-calibrated measurement artifact suitable for H-M3's OLS scaling law regression.

---

## 8. Gate Verdict

**MUST_WORK Gate: PASS**

Both primary conditions satisfied:
1. `n_positive_high_kl = 5 >= 3` — gap strictly positive at all high-KL levels
2. `rho_gap_kl = 1.000 > 0` — gap grows monotonically with KL

**Next step:** Proceed to Phase 5 (Baseline Comparison) or H-M3 hypothesis.

---

## 9. Code Quality (Validator Assessment)

| Check | Result |
|-------|--------|
| Code runs without errors | PASS |
| Mechanism correctly implemented | PASS |
| Gate logic verified | PASS |
| All required figures generated (4/4) | PASS |
| Results JSON saved | PASS |
| Gap CSV saved | PASS |
| Exit code = 0 (gate pass) | PASS |

**Coder-Validator Loop:** 1 cycle (first pass success)

---

*Generated by Phase 4 — PoC Implementation & Validation*
*Pipeline: Phase 0 → 1 → 2A → 2B → 2C → 3 → **Phase 4** (H-M2) → 4.5 → [5] → 6*
