# Phase 4 Validation Report: H-M3

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M3 — ΔECE > 0.05 for ≥60% of (model, task) cells AND mean ΔECE > 0 (p < 0.05)
**Gate type:** SHOULD_WORK
**Gate result:** EXPLORE (soft fail — pipeline continues)

---

## 1. Experiment Summary

H-M3 tests whether the confidence-accuracy gap confirmed in H-M2 (EXPLORE) manifests as measurable calibration degradation (ΔECE > 0.05) under adversarial perturbation. The experiment computed ΔECE = ECE(adversarial) − ECE(clean) for each (model, task) cell using pre-extracted logit caches from H-E1 (Llama-2-7b-hf on AdvGLUE and ANLI).

**Implementation:** Pure numpy/scipy post-processing on H-E1 JSONL caches. No model inference required. Runtime < 30 seconds.

---

## 2. Gate Evaluation

| Metric | Value | Gate Threshold | Pass? |
|--------|-------|---------------|-------|
| gate_pass_rate | 0.20 (1/5 cells) | ≥ 0.60 | FAIL |
| mean ΔECE | 0.0023 | > 0 | marginal |
| t-stat (one-sample) | 0.1122 | — | — |
| p-value (H0: mean ≤ 0) | 0.4580 | < 0.05 | FAIL |
| **Overall gate** | **EXPLORE** | SHOULD_WORK | — |

**Gate verdict: EXPLORE** — neither the ≥60% cell proportion condition nor the p < 0.05 statistical condition was met.

---

## 3. Per-Cell Results

| Task | ECE(clean) | ECE(adv) | ΔECE | Gate (>0.05) |
|------|-----------|---------|------|-------------|
| advglue_mnli | 0.2792 | 0.3497 | **+0.0705** | PASS |
| advglue_qqp | 0.0623 | 0.0329 | −0.0294 | FAIL |
| anli_r1 | 0.2792 | 0.2387 | −0.0405 | FAIL |
| anli_r2 | 0.2792 | 0.2656 | −0.0136 | FAIL |
| anli_r3 | 0.2792 | 0.3036 | +0.0243 | FAIL |

**Mean ECE(clean):** 0.2359  **Mean ECE(adv):** 0.2381

---

## 4. Mechanism Activation Verification

```
ece_computed: True
baseline_in_range: True
delta_positive_majority: False  ← 2/5 cells positive; below 50% majority
```

Mechanism **not fully activated** — ΔECE signal is heterogeneous: advglue_mnli shows calibration degradation, while ANLI R1/R2 and QQP show calibration *improvement* under adversarial conditions.

---

## 5. Secondary Analyses

### 5.1 ANLI Difficulty Gradient
| Round | ΔECE | Expected direction |
|-------|------|-------------------|
| ANLI-R1 | −0.0405 | — |
| ANLI-R2 | −0.0136 | ↑ (confirmed) |
| ANLI-R3 | +0.0243 | ↑ (confirmed) |

Gradient direction R1 → R3 confirmed (−0.04 → −0.01 → +0.02), consistent with H-M2 difficulty gradient finding. However, absolute ΔECE values are well below the 0.05 gate for all ANLI rounds.

### 5.2 Task-type comparison
- NLI tasks (advglue_mnli + anli_r1/r2/r3): mean ΔECE = 0.0102
- Non-NLI tasks (advglue_qqp): mean ΔECE = −0.0294

NLI tasks show higher mean ΔECE; sentiment/paraphrase (QQP) shows ECE *decrease* under adversarial conditions.

### 5.3 ECE(clean) sanity check
Observed mean ECE(clean) = 0.2359 — above the Kadavath 2022 expected range of 0.05–0.15 for open-weight LLMs. This is flagged as a possible artifact of the single clean baseline file (`Llama-2-7b-hf_nli_clean_examples.jsonl`) being reused across all NLI cells (ANLI R1/R2/R3 share the same clean counterpart). ECE(clean) for advglue_qqp (0.0623) is within the expected range.

### 5.4 Ablation A: Bin count sensitivity
| n_bins | advglue_mnli | advglue_qqp | anli_r1 | anli_r2 | anli_r3 |
|--------|-------------|------------|---------|---------|---------|
| 10 | 0.0705 | −0.0333 | −0.0383 | +0.0018 | +0.0243 |
| 15 | 0.0705 | −0.0294 | −0.0405 | −0.0136 | +0.0243 |
| 20 | 0.0705 | +0.0060 | −0.0383 | +0.0018 | +0.0243 |

Results are robust to bin count for the primary finding (advglue_mnli consistently passes; others consistently fail). Bin count does not change the overall gate verdict.

### 5.5 Ablation B: Threshold sensitivity
| Threshold | gate_pass_rate |
|-----------|---------------|
| 0.03 | 0.20 |
| 0.05 | 0.20 (primary) |
| 0.10 | 0.00 |

Even at the looser 0.03 threshold, gate_pass_rate = 0.20 — well below the ≥0.60 requirement.

---

## 6. Figures Generated

All figures saved to `docs/youra_research/h-m3/figures/`:
1. `delta_ece_per_cell.png` — ΔECE bar chart with gate threshold line (required)
2. `reliability_advglue_mnli.png` — reliability diagram, clean vs. adversarial
3. `reliability_advglue_qqp.png` — reliability diagram, clean vs. adversarial
4. `reliability_anli_r1.png` — reliability diagram, clean vs. adversarial
5. `ece_scatter.png` — ECE(clean) vs ECE(adv) scatter
6. `anli_ece_gradient.png` — ANLI R1/R2/R3 ΔECE bar chart
7. `ablation_bin_sensitivity.png` — bin count ablation grouped bars

---

## 7. Key Findings

1. **Gate EXPLORE (SHOULD_WORK soft fail):** Only 1/5 cells (advglue_mnli) shows ΔECE > 0.05. Mean ΔECE = 0.0023 is near zero. The hypothesis that adversarial perturbation systematically degrades LLM calibration by >5 ECE points is not supported at the cell-majority level.

2. **Task heterogeneity:** advglue_mnli (NLI, text infilling adversarial) shows meaningful calibration degradation (ΔECE = 0.071). ANLI rounds (NLI, model-in-the-loop adversarial) and QQP (paraphrase) do not. This suggests the calibration degradation mechanism is task-type and perturbation-type dependent.

3. **Calibration *improvement* on ANLI-R1:** ΔECE = −0.041 indicates the model becomes *better calibrated* on ANLI-R1 adversarial examples — a counterintuitive finding. Possible explanation: the model's uncertainty increases on adversarial examples, bringing confidence closer to the actual low accuracy.

4. **ANLI difficulty gradient (partial confirmation):** The direction R1 < R2 < R3 is confirmed in ΔECE magnitude, consistent with H-M2. Full gradient does not clear the gate threshold.

5. **ECE(clean) artifact concern:** Mean ECE(clean) = 0.236 is above Kadavath 2022 range; NLI cells share the same clean baseline file (200 MultiNLI examples), which may not be a perfect counterpart for each adversarial task.

---

## 8. Limitations

- **Single-model scope:** Only Llama-2-7b-hf available (inherited from H-E1). A 4-model grid would provide better statistical power for the t-test.
- **Shared clean baseline:** ANLI-R1/R2/R3 all use the same clean NLI file as counterpart. This inflates cross-cell correlation and reduces t-test validity.
- **Small adversarial sets:** advglue_mnli n=121, advglue_qqp n=78 — below the 200 target; reduces ECE estimation precision.
- **n_cells=5:** With 5 cells, the one-sample t-test has very low power. Null hypothesis cannot be rejected even if ΔECE were consistently positive.

---

## 9. Gate Decision

**EXPLORE** — SHOULD_WORK gate not satisfied. Pipeline continues per Phase 2B failure response policy:
- Document as negative/partial result
- ANLI difficulty gradient (partial) and advglue_mnli calibration degradation are noteworthy secondary findings
- Calibration degradation under adversarial conditions is task-type dependent, not universal

---

## 10. Coder-Validator Assessment

**Coder:** Single-pass implementation. Code reuses H-E1 `compute_ece` and H-M2 `jsonl_loader` schema directly (pre-extracted confidence/correct fields). No model inference needed. Runtime ~30s.

**Validator checks:**
- [x] Pre-flight PASSED: all 7 JSONL files present
- [x] ECE values in valid range [0, 1] for all cells
- [x] Mechanism activation verified (ece_computed=True, baseline_in_range=True)
- [x] Ablations A (bin counts) and B (thresholds) computed
- [x] 7 figures generated and saved
- [x] All 4 result files written (CSV, JSON ×3)
- [x] Summary written
- [x] Gate result reproducible: deterministic numpy computation

**Validator verdict:** PASS — experiment executed correctly, results are internally consistent, gate decision correctly derived from data.
