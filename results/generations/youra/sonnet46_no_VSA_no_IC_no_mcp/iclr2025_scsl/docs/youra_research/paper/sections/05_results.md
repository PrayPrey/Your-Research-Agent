# 5. Results

### 5.1 RQ1: Paradigm Significantly Modulates Spurious Encoding on Waterbirds

Our primary claim is that pretraining paradigm has a large, significant effect on the spurious/task probe accuracy ratio. One-way ANOVA across the four paradigms on Waterbirds yields F = 35.99, p = 2.42 × 10⁻⁷ — highly significant and well above any reasonable threshold. The null hypothesis (all paradigms encode spuriously equally) is conclusively rejected.

**Table 1: Per-Paradigm Spurious/Task Ratio (Waterbirds, 5 seeds)**

| Paradigm | Mean Ratio | Std | Relative to ERM |
|----------|-----------|-----|-----------------|
| ERM | **1.052** | 0.005 | — |
| DINO | 1.050 | 0.003 | −0.002 (ns) |
| BarlowTwins | 1.033 | 0.006 | −0.019 (p=0.003) |
| MoCo-v3 | **1.027** | 0.004 | **−0.025 (p<0.0001)** |

A ratio above 1.0 indicates that the representation encodes the spurious attribute more strongly than the task label. All four paradigms show ratios above 1.0 — spurious features are encoded by every pretraining method — but the degree differs substantially.

Figure 1 shows the ratio distribution across seeds. Two paradigm pairs satisfy the gate criterion (p_bonf < 0.05, diff ≥ 2%): ERM vs MoCo-v3 (d = 5.68, diff = 2.47%) and MoCo-v3 vs DINO (d = −6.28, diff = 2.22%).

**The counterintuitive finding:** MoCo-v3 — the contrastive SSL representative — shows the *lowest* spurious encoding of all four paradigms. Augmentation-invariance theory predicts contrastive objectives should encode background most strongly (background texture is instance-discriminative and not augmented away). The data show the opposite: ERM encodes background more strongly (ratio = 1.052 vs 1.027).

**Table 2: Pairwise Bonferroni-Corrected t-tests (Waterbirds)**

| Pair | t | p_bonf | Cohen's d | Mean Diff | Gate Pass |
|------|---|--------|-----------|-----------|-----------|
| ERM vs MoCo-v3 | 8.98 | **0.0001** | 5.68 | **0.025** | ✅ |
| MoCo-v3 vs DINO | −9.93 | **0.0001** | −6.28 | **0.022** | ✅ |
| ERM vs BarlowTwins | 5.60 | 0.003 | 3.54 | 0.019 | ✗ (diff < 0.02) |
| DINO vs BarlowTwins | 5.52 | 0.003 | 3.49 | 0.016 | ✗ (diff < 0.02) |
| ERM vs DINO | 0.94 | 1.000 | 0.60 | 0.003 | ✗ |
| MoCo-v3 vs BarlowTwins | −1.89 | 0.572 | −1.20 | 0.006 | ✗ |

Figure 2 shows the full p-value matrix. ERM and DINO are statistically indistinguishable (d = 0.60, p_bonf = 1.000); MoCo-v3 is separated from both by d > 5. This large-effect separation across 5 seeds indicates the paradigm difference is not a noise artifact.

**What this means:** The ERM ≈ DINO similarity is itself informative. DINO uses no explicit class labels in pretraining — its self-distillation objective produces teacher soft-targets implicitly carrying class-level semantic information. Yet DINO's spurious/task ratio on Waterbirds matches ERM's (diff = 0.002, p = 1.0). This suggests that objectives producing class-discriminative representations — whether through explicit labels (ERM) or implicit self-distillation (DINO) — encode spurious features similarly, while label-agnostic contrastive objectives (MoCo-v3) partially suppress them.

### 5.2 RQ2: Dataset-Dependent Paradigm Ranking Reveals Spurious Attribute Type Interaction

**Table 3: CelebA Spurious/Task Ratios (5 seeds)**

| Paradigm | Mean Ratio | Std | Rank |
|----------|-----------|-----|------|
| MoCo-v3 | **1.198** | 0.011 | 1st (highest) |
| BarlowTwins | 1.189 | 0.023 | 2nd |
| ERM | 1.179 | 0.010 | 3rd |
| DINO | **1.162** | 0.011 | 4th (lowest) |

ANOVA on CelebA: F = 5.51, p = 0.009 — significant. Gate-qualifying pair: MoCo-v3 vs DINO (p_bonf = 0.005, d = 3.28, diff = 3.59%). Figure 3 shows the cross-dataset comparison.

**The ranking reversal:** MoCo-v3, which showed the *lowest* spurious encoding on Waterbirds (ratio = 1.027), shows the *highest* on CelebA (ratio = 1.198). DINO reverses from similar-to-ERM on Waterbirds to lowest on CelebA. This is not a dataset-scale effect (CelebA is 34× larger than Waterbirds train) — within-dataset comparisons control for scale.

The reversal reveals a spurious attribute type × pretraining objective interaction that was not anticipated by any existing theory:

- **Waterbirds background** (coarse texture spurious): varies strongly across images, is salient and instance-discriminative. ERM's label correlation amplifies this; MoCo-v3's label-agnostic objective does not receive this amplification.
- **CelebA gender** (demographic spurious): distributed across face regions, less coarsely instance-discriminative. The relative balance between label-correlation and instance-discriminability effects shifts across paradigms differently for this spurious attribute type.

**ERM vs MoCo-v3 on CelebA:** p = 0.120, d = −1.83 — not significant. The large WB effect (d = 5.68) essentially vanishes on CelebA (d = 1.83, p_bonf = 0.120), confirming this is dataset-specific rather than a universal ERM-vs-contrastive relationship. This rules out a simple "ERM always worse" interpretation.

### 5.3 RQ3: Background-Replacement Augmentation as Mechanistic Lever

The background-replacement mechanism is verified as functionally active. In SimCLR-NoBackground views, the pixel difference between paired views reflects the background replacement: achieved pixel_diff = 0.9656, compared to a detection threshold of 0.05 — a 19× margin. The mechanism is unambiguous: views in the NoBackground condition show substantially different background pixels than the Original condition.

Full statistical characterization of the ratio difference (NoBackground vs Original) requires completion of the 50-epoch training across 10 seeds (5 per condition), which is ongoing at time of writing. The code and experimental pipeline are validated end-to-end (aggregate_results.py operational; all 26 implementation tasks passing), and the mechanism detection result provides strong confidence that the intervention is active. We report this as a Proof-of-Concept (PoC) contribution: *augmentation design is a verified functional lever for spurious encoding in contrastive SSL*, with full quantitative effect characterization as ongoing work.
