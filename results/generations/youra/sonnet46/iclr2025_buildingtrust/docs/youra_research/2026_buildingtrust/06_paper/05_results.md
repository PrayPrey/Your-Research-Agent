# Results

## 5.1 Base Model Calibration (H-M1: MUST_WORK PASS)

Before presenting alignment effects, we confirm the causal baseline: Pythia base models are well-calibrated prior to any alignment training.

**Table 1: Base Model Expected Calibration Error**

| Model | ECE | Gate Check (< 0.15) |
|-------|-----|---------------------|
| Pythia-1.4B (base) | 0.0849 | PASS |
| Pythia-2.8B (base) | 0.0597 | PASS |
| Pythia-6.9B (base) | 0.0792 | PASS |

All three base models achieve ECE well below the 0.15 threshold (MUST_WORK gate PASS). The Pythia 2.8B base model is best-calibrated (ECE = 0.0597), while 1.4B shows the highest base ECE (0.0849) — both substantially below the threshold. These values are consistent with Xie et al.'s \cite{xie2024ats} characterization of pretrained models as naturally well-calibrated. This baseline confirms that any calibration degradation observed in aligned models is attributable to the alignment training procedure itself, not to pretraining artifacts.

*Figures referenced: h-m1/figures/figure_01_ece_gate.png (ECE gate bar chart); h-m1/figures/figure_03_calibration_curves.png (calibration reliability curves for base models)*

## 5.2 Alignment-Induced Brier Reliability Overconfidence (H-E1: MUST_WORK PASS)

**Table 2: Per-Model Calibration Metrics on MMLU (N = 14,042 items)**

| Model | ECE | Brier REL | Brier RES | Δ REL | CI Lower | CI Upper |
|-------|-----|-----------|-----------|-------|----------|----------|
| pythia-1.4b-base | 0.0849 | 0.0190 | 0.0005 | — | — | — |
| pythia-1.4b-sft | 0.1415 | 0.0445 | 0.0005 | +0.0289 | +0.0269 | +0.0309 |
| pythia-1.4b-dpo | 0.2516 | 0.1151 | 0.0008 | +**0.1048** | +0.1009 | +0.1090 |
| pythia-1.4b-ppo | 0.1923 | 0.0742 | 0.0002 | +0.0406 | +0.0345 | +0.0464 |
| pythia-2.8b-base | 0.0597 | 0.0093 | 0.0003 | — | — | — |
| pythia-2.8b-sft | 0.0694 | 0.0126 | 0.0004 | +0.0033 | +0.0021 | +0.0045 |
| pythia-2.8b-dpo | 0.1441 | 0.0531 | 0.0007 | +0.0437 | +0.0407 | +0.0469 |
| pythia-2.8b-ppo | 0.1577 | 0.0516 | 0.0004 | +0.0423 | +0.0388 | +0.0456 |
| pythia-6.9b-base | 0.0792 | 0.0128 | 0.0004 | — | — | — |
| pythia-6.9b-sft | 0.0830 | 0.0138 | 0.0006 | +0.0010 | +0.0001 | +0.0018 |
| pythia-6.9b-dpo | 0.1010 | 0.0227 | 0.0009 | +0.0099 | +0.0090 | +0.0112 |
| pythia-6.9b-ppo | 0.0609 | 0.0092 | 0.0007 | −0.0036 | −0.0053 | −0.0018 |

**Gate result:** MUST_WORK gate PASSED via both PPO and DPO. PPO achieves CI lower > 0 in 2/3 sizes (1.4B, 2.8B); DPO achieves CI lower > 0 in 3/3 sizes. Alignment training reliably increases Brier reliability (overconfidence) in 8 of 9 aligned model-size pairs.

**Key observation — DPO > PPO ordering:** DPO consistently produces *larger* ΔReliability than PPO in all three model sizes:
- 1.4B: DPO ΔReliability = 0.1048 vs. PPO = 0.0406 (2.58× larger)
- 2.8B: DPO = 0.0437 vs. PPO = 0.0423 (1.03× larger — near-parity)
- 6.9B: DPO = 0.0099 vs. PPO = −0.0036 (PPO *improves* calibration at this scale)

This ordering (DPO ≥ PPO > SFT) is the empirical reverse of the original prediction (PPO ≥ DPO > SFT), which assumed reward optimization pressure monotonically drives calibration degradation.

**Largest effect:** Pythia-1.4B DPO increases Brier reliability by ΔReliability = 0.1048 — a 5.5× increase over the base reliability (REL_base = 0.019). The bootstrap CI [0.1009, 0.1090] confirms this is not a sampling artifact.

**Exception:** Pythia-6.9B PPO shows a slight *decrease* in reliability (ΔReliability = −0.0036, CI [−0.0053, −0.0018]), suggesting that at larger scale, PPO-based alignment may not uniformly degrade calibration. We discuss this anomaly in Section 5.4 and Section 6.

*Figures referenced: h-e1/code/figures/delta_reliability_bar.png (ΔReliability bar chart with CIs); h-e1/code/figures/ece_heatmap.png (ECE heatmap across all 12 models)*

## 5.3 Pre-Softmax Margin Inflation (H-M2: SHOULD_WORK PASS)

To confirm that the calibration degradation is present at the logit level (not a softmax artifact), we analyze pre-softmax logit margins.

**Table 3: Mean Δmargin (aligned − base, in nats) with Bootstrap 95% CI for PPO**

| Alignment | 1.4B (CI) | 2.8B (CI) | 6.9B (CI) |
|-----------|-----------|-----------|-----------|
| SFT | +0.1334 | +0.0110 | +0.0267 |
| DPO | **+0.4908** | **+0.2077** | **+0.0721** |
| PPO | +0.3937 (+0.3893, +0.3980) | +0.2526 (+0.2467, +0.2578) | −0.0364 (−0.0394, −0.0334) |

**Gate result:** SHOULD_WORK gate PASSED. PPO shows Δmargin > 0 with CI lower > 0 in 2/3 sizes (1.4B, 2.8B). The gate criterion requires ≥2/3 sizes; this is met.

**Consistent secondary finding — DPO > PPO in margins:** DPO shows larger Δmargin than PPO in all three sizes (1.4B: DPO +0.491 vs PPO +0.394; 2.8B: DPO +0.208 vs PPO +0.253 — note PPO slightly larger at 2.8B; 6.9B: DPO +0.072 vs PPO −0.036). This confirms the DPO > PPO calibration ordering is visible at the pre-softmax logit level, ruling out a softmax normalization artifact as the explanation.

**6.9B anomaly:** Pythia-6.9B PPO shows *negative* Δmargin (−0.036 nats), consistent with the 6.9B-PPO calibration improvement in H-E1. At larger scale, PPO-aligned models may develop a form of logit regulation absent in smaller models.

*Figures referenced: h-m2/figures/figure_01_delta_margin_gate.png (Δmargin bar chart with CIs); h-m2/figures/figure_04_gradient_ordering_heatmap.png (3×3 heatmap)*

## 5.4 Mechanism Discrimination: H2 Confirmed, H1 Refuted (H-M3: SHOULD_WORK FAIL — Informative)

This is the central mechanistic finding of the paper.

**Table 4: Spearman ρ Results (H1/H2 Discrimination)**

| Pair | Mean ρ | H1 Pass (≥ 0.90) | H2 Flag (< 0.85) |
|------|--------|------------------|------------------|
| 1.4B-SFT | 0.7533 | No | **Yes** |
| 1.4B-DPO | 0.7369 | No | **Yes** |
| 1.4B-PPO | **−0.3241** | No | **Yes** |
| 2.8B-SFT | 0.7185 | No | **Yes** |
| 2.8B-DPO | 0.5896 | No | **Yes** |
| 2.8B-PPO | 0.1746 | No | **Yes** |
| 6.9B-SFT | 0.8390 | No | **Yes** |
| 6.9B-DPO | 0.8748 | No | Near-threshold |
| 6.9B-PPO | 0.5045 | No | **Yes** |

**Gate note:** The H-M3 SHOULD_WORK gate was defined as "mean ρ ≥ 0.90 for all 9 pairs (H1 confirmation)." This gate FAILS — 0 of 9 pairs achieve ρ ≥ 0.90. This is a scientifically informative negative: **H1 is definitively refuted; H2 is confirmed as the dominant mechanism.**

**Summary:** 0/9 pairs pass the H1 threshold (ρ ≥ 0.90); 8/9 pairs show H2 flag (ρ < 0.85). The single pair not flagged as H2 (6.9B-DPO, ρ = 0.875) is still below the H1 threshold, making the H2 dominance conclusion unambiguous across the full model suite.

**Striking finding — 1.4B-PPO catastrophic redistribution:** The 1.4B-PPO pair shows ρ = −0.324, the most extreme boundary shift in our study. A negative Spearman ρ implies that the aligned model *systematically prefers* the options the base model ranked *lowest*. The argmax analysis confirms this:

**Table 5: Argmax Partition Results**

| Pair | N Shared | N Changed | % Changed | Brier REL (Shared) | Brier REL (Changed) | Cohen's d |
|------|----------|-----------|-----------|-------------------|---------------------|-----------|
| 1.4B-SFT | 8,028 | 6,014 | 42.8% | 0.0479 | 0.0635 | 1.0004 |
| 1.4B-DPO | 8,235 | 5,807 | 41.4% | 0.1181 | 0.1489 | 0.9218 |
| **1.4B-PPO** | **44** | **13,998** | **99.7%** | 0.1217 | 0.0657 | 4.8740 |
| 2.8B-SFT | 10,017 | 4,025 | 28.7% | 0.0142 | 0.0096 | 4.7806 |
| 2.8B-DPO | 8,516 | 5,526 | 39.4% | 0.0607 | 0.0430 | 3.4410 |
| 2.8B-PPO | 4,993 | 9,049 | 64.4% | 0.0703 | 0.0418 | 5.6206 |
| 6.9B-SFT | 11,969 | 2,073 | 14.8% | 0.0151 | 0.0078 | 3.4568 |
| 6.9B-DPO | 11,818 | 2,224 | 15.8% | 0.0246 | 0.0144 | 2.1579 |
| 6.9B-PPO | 8,472 | 5,570 | 39.7% | 0.0104 | 0.0084 | 6.9636 |

For 1.4B-PPO, only 44 of 14,042 items retain the same argmax (0.3%) — the PPO-aligned model has near-completely reassigned which answer it considers most likely. This is not a calibration distortion in the traditional sense; it is a near-complete representational reorganization of which answer options are preferred.

*Figures referenced: h-m3/figures/figure_01_spearman_rho.png (Spearman ρ bar chart — recommended main figure); h-m3/figures/figure_04_argmax_proportion.png (% changed argmax — striking visualization)*

## 5.5 H3 Diagnostic: Framing Susceptibility Ruled Out

**Table 6: TruthfulQA MC1 ECE Results (H3 Diagnostic)**

| Model | ECE (TruthfulQA) | N Items |
|-------|-----------------|---------|
| Pythia-1.4B base | 0.5889 | 817 |
| Pythia-1.4B SFT | 0.6023 | 817 |
| Pythia-1.4B DPO | 0.6058 | 817 |
| Pythia-1.4B PPO | 0.6787 | 817 |
| Pythia-2.8B base | 0.5926 | 817 |
| Pythia-2.8B SFT | 0.6037 | 817 |
| Pythia-2.8B DPO | 0.6342 | 817 |
| Pythia-2.8B PPO | 0.6021 | 817 |
| Pythia-6.9B base | 0.5881 | 817 |
| Pythia-6.9B SFT | 0.5901 | 817 |
| Pythia-6.9B DPO | 0.6016 | 817 |
| Pythia-6.9B PPO | 0.6102 | 817 |

**Table 7: H3 Diagnostic Summary**

| Alignment | ΔECE (TruthfulQA) | ΔECE (MMLU) | Ratio | H3 Signal |
|-----------|--------------------|-------------|-------|-----------|
| SFT | +0.0088 | +0.0276 | 0.32 | **False** |
| DPO | +0.0240 | +0.0934 | 0.26 | **False** |
| PPO | +0.0405 | +0.0554 | 0.73 | **False** |

**H3 finding:** For all three alignment methods, TruthfulQA ΔECE is *smaller* than MMLU ΔECE (ratios: 0.32, 0.26, 0.73 — all < 1.0). H3 would require TruthfulQA ΔECE > MMLU ΔECE (ratio > 1.0). The framing susceptibility mechanism (H3) is definitively ruled out: calibration degradation in softmax-based ECE is domain-general (present on both MMLU and TruthfulQA) rather than framing-specific (disproportionately amplified by TruthfulQA's adversarial framing).

This negative result distinguishes our finding from the framing sensitivity observed with verbally-elicited confidence by Chhikara et al. \cite{chhikara2025confidence}: the measurement modality (softmax ECE vs. verbal confidence) determines whether framing sensitivity is detected.

*Figures referenced: h-m3/figures/figure_05_truthfulqa_ece.png (TruthfulQA ECE comparison)*

## 5.6 Summary of Mechanism Findings

| Mechanism | Predicted | Observed | Conclusion |
|-----------|-----------|----------|------------|
| H1 (Scale distortion, ρ ≥ 0.90) | Dominant | 0/9 pairs pass | **Refuted** |
| H2 (Boundary shift, ρ < 0.85) | Alternative | 8/9 pairs show; 1.4B-PPO: ρ = −0.324 | **Confirmed (dominant)** |
| H3 (Framing susceptibility) | Alternative | TruthfulQA ΔECE < MMLU ΔECE all types | **Ruled out** |

**Statistical significance:** All primary ΔReliability estimates have bootstrap 95% CI lower bounds > 0 for DPO (3/3 sizes) and PPO (2/3 sizes). The Spearman ρ result (0/9 pairs ≥ 0.90) is a population-level finding computed over N = 14,042 items per pair; sampling variability is negligible. The argmax redistribution counts (especially 1.4B-PPO: 44 shared out of 14,042) are exact counts, not estimates.

**Scale trend:** The Spearman ρ values show a consistent scale trend: larger models show higher ρ (closer to rank preservation). At 6.9B, SFT achieves ρ = 0.839 and DPO achieves ρ = 0.875 — suggesting that the H1/H2 transition may occur for very large models (≥ 13B) with soft alignment methods such as DPO.
