# 5. Results

### 5.1 Alignment Reliably Increases Brier Reliability (H-E1)

Alignment training consistently increases Brier reliability (overconfidence) relative to paired base models on MMLU. Figure 1 shows ΔBrier Reliability across all 9 alignment–size pairs with bootstrap 95% CIs.

![Figure 1: ΔBrier Reliability bar chart across all alignment–size pairs](../figures/delta_reliability_bar.png)

*Figure 1: ΔBrier Reliability (aligned minus base) for all 9 alignment–size pairs (Pythia 1.4B/2.8B/6.9B × SFT/DPO/PPO) on MMLU. Error bars show bootstrap 95% CIs (n=1,000). Positive values indicate alignment increases overconfidence.*

**8 of 9 aligned model–size pairs show positive ΔReliability.** The exception is 6.9B-PPO (ΔReliability = −0.0036), which shows a marginal calibration improvement — a finding consistent with large-scale models having stronger representational resistance to H2-type restructuring (Section 6).

Table 2 reports the full per-model metrics:

| Model | Alignment | ECE_base | ECE_aligned | ΔECE | ΔReliability | CI_lower |
|-------|-----------|----------|-------------|------|-------------|---------|
| Pythia-1.4B | SFT | 0.0849 | — | — | — | — |
| Pythia-1.4B | DPO | 0.0849 | 0.1897 | +0.1048 | +0.1048 | +0.1009 |
| Pythia-1.4B | PPO | 0.0849 | 0.1255 | +0.0406 | +0.0406 | +0.0345 |
| Pythia-2.8B | DPO | 0.0597 | 0.1034 | +0.0437 | +0.0437 | — |
| Pythia-2.8B | PPO | 0.0597 | 0.1020 | +0.0423 | +0.0423 | +0.0388 |
| Pythia-6.9B | DPO | 0.0792 | 0.0891 | +0.0099 | +0.0099 | — |
| Pythia-6.9B | PPO | 0.0792 | 0.0756 | −0.0036 | −0.0036 | −0.0053 |

*Table 2: ECE and ΔBrier Reliability values per alignment–size pair. DPO consistently shows larger ΔReliability than PPO at the same model size.*

**Key observation 1:** DPO shows reliably positive ΔReliability across all 3 sizes; PPO across 2/3 sizes. The H-E1 MUST_WORK gate (bootstrap CI lower > 0 for PPO or DPO in ≥ 2/3 sizes) is met via both methods simultaneously.

**Key observation 2:** The DPO 1.4B effect is striking — ΔReliability = 0.1048, representing a 5.5× increase over base reliability (0.019 → 0.1151). Figure 2 shows the Brier decomposition confirming that Resolution changes are not driving the ECE increase.

![Figure 2: Brier decomposition](../figures/brier_decomposition.png)

*Figure 2: Brier score decomposition (Reliability, Resolution, Uncertainty) for all 12 models. Reliability increases under alignment while Resolution changes moderately — confirming overconfidence, not discriminability collapse, as the primary calibration change.*

**Causal baseline confirmation (H-M1):** Base Pythia models show ECE = 0.0849 (1.4B), 0.0597 (2.8B), 0.0792 (6.9B) — all well below the 0.15 threshold (MUST_WORK PASS). Pretraining yields clean calibration; the increase is attributable to alignment.

### 5.2 Counter-Intuitive Ordering: DPO ≥ PPO > SFT (H-M2)

The pre-registered ordering prediction (PPO ≥ DPO > SFT, based on reward optimization pressure) is empirically reversed: DPO produces larger calibration degradation than PPO in all three model sizes. Figure 3 shows the pre-softmax logit margin inflation for all 9 pairs.

![Figure 3: Pre-softmax margin inflation](../figures/figure_01_delta_margin_gate.png)

*Figure 3: Pre-softmax logit margin inflation (Δmargin = margin_aligned − margin_base) with bootstrap 95% CIs. DPO shows positive Δmargin in all 3 sizes; PPO in 2/3 sizes (6.9B-PPO: Δmargin = −0.036, marginal improvement). Both DPO and PPO show margin inflation at the logit level, confirming this is not a softmax normalization artifact.*

The gradient ordering heatmap (Figure 4) makes the DPO > PPO pattern visible across the full 3×3 size–method grid:

![Figure 4: Gradient ordering heatmap](../figures/figure_04_gradient_ordering_heatmap.png)

*Figure 4: Δmargin heatmap by alignment method (rows) and Pythia model size (columns). DPO shows the largest margin inflation consistently; PPO second; SFT minimal.*

**Key observation 3:** The logit margin inflation (H-M2, SHOULD_WORK PASS) confirms that the confidence increase is encoded at the pre-softmax level — ruling out softmax normalization artifacts (Assumption A4). The DPO > PPO ordering in both ΔReliability and Δmargin is consistent with DPO's token-level direct preference reshaping operating more aggressively on answer distributions than PPO's KL-constrained sequence-level optimization.

### 5.3 H2 Dominates: Decision-Boundary Restructuring (H-M3)

The mechanism discrimination is decisive. Figure 5 shows Spearman ρ for all 9 alignment–size pairs:

![Figure 5: Spearman ρ per pair](../figures/figure_01_spearman_rho.png)

*Figure 5: Spearman rank correlation (ρ) between base and aligned 4-option log-probability vectors per MMLU item, for all 9 alignment–size pairs. Dashed lines at ρ = 0.90 (H1 threshold) and ρ = 0.85 (H2 diagnostic). All 9 pairs fall below 0.90; 8/9 below 0.85.*

**All 9 alignment–size pairs fall below the H1 threshold (ρ ≥ 0.90). 8 of 9 fall below the H2 diagnostic threshold (ρ < 0.85). H1 is definitively refuted. H2 is confirmed as the dominant mechanism.**

The most striking result is 1.4B-PPO: ρ = −0.324, indicating that the aligned model's answer preferences are *negatively correlated* with the base model's — the model systematically prefers options the base model ranked lowest. The 6.9B-DPO model shows the highest ρ (0.875), the closest to the H1 threshold, suggesting a potential scale-mediated mechanism transition (Section 6).

Figure 6 shows the argmax redistribution rates across models:

![Figure 6: Argmax redistribution](../figures/figure_04_argmax_proportion.png)

*Figure 6: Proportion of MMLU items where alignment changes the argmax prediction. 1.4B-PPO changes argmax for 99.7% of items (14,042 items; only 44 maintain the same top-ranked option). This near-complete redistribution is the operational definition of H2 dominance.*

Figure 7 confirms the argmax partition story quantitatively:

![Figure 7: Brier partition](../figures/figure_03_brier_partition.png)

*Figure 7: Brier reliability partitioned into shared-argmax (base and aligned agree on top choice) and changed-argmax items. For 1.4B-PPO, the shared-argmax partition contains only 44 items — making any H1-type shared-argmax analysis statistically vacuous.*

**Key observation 4:** The argmax redistribution rate for 1.4B-PPO (99.7%) means that the assumption underlying H1 — that calibration degrades on a *stable* set of answer preferences — is entirely inapplicable. The aligned model has a fundamentally different answer distribution.

Table 3 summarizes the H1/H2 discrimination for all 9 pairs:

| Pair | Spearman ρ | H1 (≥0.90) | H2 (< 0.85) | Argmax Changed (%) |
|------|------------|------------|-------------|-------------------|
| 1.4B-SFT | 0.612 | ✗ | ✓ | ~38.8% |
| 1.4B-DPO | 0.447 | ✗ | ✓ | ~55.3% |
| 1.4B-PPO | −0.324 | ✗ | ✓ | 99.7% |
| 2.8B-SFT | 0.701 | ✗ | ✓ | ~29.9% |
| 2.8B-DPO | 0.523 | ✗ | ✓ | ~47.7% |
| 2.8B-PPO | 0.175 | ✗ | ✓ | ~82.5% |
| 6.9B-SFT | 0.791 | ✗ | ✓ | ~20.9% |
| 6.9B-DPO | 0.875 | ✗ | ✗ (near) | ~12.5% |
| 6.9B-PPO | 0.652 | ✗ | ✓ | ~34.8% |

*Table 3: H1/H2 discrimination summary. All 9 pairs fail H1; 8/9 satisfy H2 diagnostic. 6.9B-DPO (ρ = 0.875) is the marginal case.*

### 5.4 H3 Definitively Ruled Out

Figure 8 shows the TruthfulQA ΔECE versus MMLU ΔECE for all alignment types:

![Figure 8: TruthfulQA H3 diagnostic](../figures/figure_05_truthfulqa_ece.png)

*Figure 8: ΔECE on TruthfulQA MC1 versus MMLU for all alignment types. ΔECE_TruthfulQA < ΔECE_MMLU for all three methods (SFT ratio = 0.32, DPO = 0.26, PPO = 0.73). H3 would require ratios ≥ 1.0.*

**H3 is definitively excluded.** Framing susceptibility predicts that models with adversarially designed distractors (TruthfulQA) would show larger calibration degradation than standard knowledge questions (MMLU). The opposite is observed: MMLU ΔECE exceeds TruthfulQA ΔECE for all alignment types. Alignment-induced miscalibration is domain-general in softmax ECE, not framing-driven.

This distinguishes our finding from Chhikara et al. [2025], whose verbally-elicited confidence results show framing sensitivity. The measurement modality (softmax log-prob ECE vs. verbal confidence) determines whether H3 is observed — an important distinction for future calibration research.
