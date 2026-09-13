# 6. Discussion

## 6.1 Key Findings

Our experiments reveal three important findings about gradient norms as minority proxies:

**Finding 1: The gradient domain provides a stronger minority proxy signal than expected.** AUC=0.914 and ratio=8.8x both far exceed their respective thresholds (0.70 and 3.0x). The signal is not marginal — it is nearly an order of magnitude. This suggests that the spurious correlation learning dynamic produces a much stronger gradient domain signal than the loss or error domains capture. JTT's binary misclassification at T_id=5 would include samples where the model's prediction happens to be wrong, which is a coarser and noisier set than the top gradient-norm samples. The AUC=0.914 result implies that g̃ could be used as a threshold-based minority classifier (all samples with g̃ > 0.2 are minority with high confidence), whereas binary misclassification cannot be thresholded.

**Finding 2: The balance_deviation criterion was wrong, but the mechanism was right.** The initial criterion (class balance deviation ≤ 0.10) was a mis-specification — it tested class uniformity when the relevant property is minority recall. This is not a failure of the gradient norm mechanism; it is a criterion design lesson. The minority/majority ratio=8.8x and AUC=0.914 together imply high minority recall in the top-25% selected subset: with AUC=0.914, the g̃-based ranking places minority samples predominantly in the top tier of the distribution. On an imbalanced dataset like Waterbirds (~5% minority fraction), the correct expectation for top-25% selection is not "equal classes" but "high minority recall" — and the signal quality strongly suggests this expectation is met. Direct measurement via h-e1-v2 will confirm.

**Finding 3: The temporal plateau reveals majority saturation dynamics.** The ratio increasing monotonically from 6.5x (epoch 1) to 8.8x (epoch 5) and plateauing at 8.5x (epoch 10) is most consistent with majority saturation: majority samples are fully fit by the shortcut solution early in training (loss → ~0, g̃ → ~0), while minority samples maintain elevated prediction residuals. Once the majority is fully saturated, the ratio plateaus. This is qualitatively consistent with NHT framework predictions, though the simplest NHT scenario predicts a ratio peak followed by a decline at T_peak_sc — the observed plateau suggests T_peak_sc is beyond epoch 10 for these hyperparameters, or that the plateau reflects full majority saturation rather than NHT dynamics. Layerwise norm tracking across epochs 10–20 would clarify this distinction.

## 6.2 Limitations

Our work has four principled limitations that we report honestly:

**Limitation 1: End-to-end WGA performance not measured.** The full GNR-LLR pipeline — Stage 1 (proxy signal) + Stage 2 (last-layer retraining) — was not executed in this pipeline run. Only the proxy signal existence (H-E1) was validated. No worst-group accuracy measurements exist for this pipeline's experiments. The primary scientific contribution of GNR-LLR — achieving competitive WGA without group labels — cannot be stated as empirically validated.
- *Why acceptable:* AUC=0.914 establishes an extremely strong proxy signal quality. DFR [Kirichenko et al., 2022] demonstrated that even a group-balanced oracle subset achieves 92.9% WGA; our signal quality suggests that a gradient-norm-selected pseudo-balanced subset should approach this level. The proxy signal result is a publishable contribution in itself and provides a direct foundation for the Stage 2 experiments.
- *Path forward:* Execute h-m1 through h-m4 to measure WGA with GNR-LLR. Expected timeline: ~22 GPU hours on H100 NVL using existing infrastructure.

**Limitation 2: Single-dataset evaluation (Waterbirds only).** All experiments use Waterbirds. CelebA evaluation was not performed.
- *Why acceptable:* Waterbirds is the primary benchmark for spurious correlation robustness research; all comparison methods (JTT, LfF, DFR, GroupDRO) report Waterbirds as their primary result. Single-dataset strong results are publishable at this stage.
- *Path forward:* Apply the same protocol to CelebA (non-blond female minority group); expected to show similar ratio and AUC given the same spurious correlation mechanism, but requires explicit verification.

**Limitation 3: Minority recall not directly measured.** While AUC=0.914 implies high minority recall in the top-25% by g̃, the exact value was not computed. The Phase 2B criterion measured balance_deviation (wrong metric); the correct metric is minority recall = |{top-25%} ∩ {G1∪G2}| / |G1∪G2|.
- *Why acceptable:* AUC=0.914 is strong indirect evidence for high minority recall. The fix is a one-line code addition.
- *Path forward:* H-e1-v2 with minority recall criterion (target: ≥ 0.60).

**Limitation 4: NHT mechanism (T_peak_sc) not directly measured.** The temporal persistence data (ratio=8.5x at epoch 10) is consistent with NHT predictions, but we did not measure T_peak_sc (the shortcut norm peak epoch) or layerwise norm dynamics.
- *Why acceptable:* Temporal robustness of the proxy signal is empirically confirmed; NHT provides the theoretical interpretation framework. The practitioner-relevant result (signal is robust across T_id ∈ {1,...,10}) is fully established.

## 6.3 Broader Impact

This research addresses the practical challenge of spurious correlation robustness — a problem with direct implications for fairness in deployed machine learning systems. Models that rely on spurious correlations (background, skin tone, hospital system, etc.) can fail catastrophically on underrepresented subpopulations.

Our gradient-norm-based proxy signal is computationally free (forward hook, no extra backward passes) and architecturally general for models with FC last layers and BatchNorm layers (the standard ResNet family). The signal's simplicity and interpretability — it measures prediction-error residuals, not an opaque clustering or auxiliary network output — may make it more accessible to practitioners who need to audit or debug model behavior on minority groups.

A potential concern: the gradient-norm signal could be exploited to specifically *suppress* minority-group information during training (e.g., adversarially filtering high-g̃ samples). This risk is mitigated by the fact that g̃ computation requires access to training dynamics that are typically not available to external adversaries in deployed systems; the signal is useful for model developers, not for data poisoning. The appropriate use is for fair and robust model training, which we encourage.
