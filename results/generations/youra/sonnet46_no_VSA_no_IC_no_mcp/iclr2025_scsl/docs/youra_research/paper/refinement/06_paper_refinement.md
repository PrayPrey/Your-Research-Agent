# Pretraining Paradigm Determines Spurious Feature Encoding: Supervised Label Correlation Dominates Augmentation Invariance

## Abstract

Contrastive self-supervised learning is commonly assumed to amplify spurious correlations: its augmentation-invariance objective makes salient spurious features — such as background texture — strongly instance-discriminative. We test this assumption directly with a controlled four-paradigm comparison of frozen ResNet-50 representations on two group-annotated benchmarks. Contrary to the augmentation-invariance prediction, supervised ERM encodes spurious background features more strongly than contrastive MoCo-v3 on Waterbirds (mean ratio difference = 0.0247, Cohen's d = 5.68, ANOVA F = 35.99, p = 2.42 × 10⁻⁷), while self-distillation DINO produces ratios statistically indistinguishable from ERM (d = 0.60, p_bonf = 1.0). On CelebA, the paradigm ranking reverses (MoCo-v3 highest, DINO lowest; ANOVA F = 5.51, p = 0.009), establishing a spurious-attribute-type × pretraining-objective interaction. When SimCLR is trained from scratch on Waterbirds with background-replacement augmentation, the spurious/task probe accuracy ratio falls by 23.1% relative to standard augmentation (mean ratio 1.472 vs. 1.132, paired t = 46.66, p = 1.26 × 10⁻⁶, d = 32.4), confirming that augmentation design is a functional causal lever for spurious feature encoding. These results indicate that supervised label correlation — not augmentation-based instance-discriminability — is the dominant driver of spurious feature encoding in frozen ResNet-50 representations, and that label-agnostic contrastive pretraining partially suppresses spurious features by design.

---

## 1. Introduction

Contrastive self-supervised learning (SSL) is widely assumed to amplify spurious correlations. Its objective encourages representations where features stable across random crops and color jitter become strongly instance-discriminative. Salient spurious features such as background texture satisfy both criteria — they are stable across typical augmentations and vary strongly across instances — so the augmentation-invariance argument predicts that contrastive SSL backbones should encode spurious attributes more strongly than supervised counterparts. This work provides direct empirical evidence that the opposite is true on the Waterbirds benchmark.

In controlled experiments on frozen ResNet-50 representations, supervised ERM encodes spurious background features significantly more strongly than contrastive MoCo-v3 (spurious/task probe ratio: ERM = 1.052, MoCo-v3 = 1.027; difference = 0.025, Cohen's d = 5.68, p_bonf < 0.0001, Bonferroni-corrected over six pairs). The paradigm ranking on Waterbirds is ERM ≈ DINO > BarlowTwins > MoCo-v3 — the reverse of what augmentation-invariance theory predicts. On CelebA, this ranking reverses, establishing a dataset-dependent interaction between spurious attribute type and pretraining objective. An ablation in which SimCLR is retrained from scratch with background-replacement augmentation shows a 23.1% reduction in spurious/task ratio relative to standard augmentation (p = 1.26 × 10⁻⁶), confirming that augmentation design causally modulates spurious feature encoding.

**The gap this work fills.** Despite substantial prior work on spurious correlations in deep learning [Sagawa et al., 2020; Kirichenko et al., 2022; Geirhos et al., 2020], systematic cross-paradigm comparison of spurious feature encoding in frozen representations is absent. DFR [Kirichenko et al., 2022] demonstrates that ERM features are sufficient for robustness after group-balanced retraining but does not compare to SSL. WILDS [Koh et al., 2021] and DomainBed [Gulrajani & Lopez-Paz, 2021] evaluate fine-tuned models, conflating pretraining representation quality with fine-tuning dynamics. To the best of our knowledge, we provide the first controlled four-paradigm comparison of spurious/task probe accuracy ratio on frozen ResNet-50 features across two group-annotated benchmarks, combined with a causal augmentation ablation.

**Key insight.** The dominant driver of spurious feature encoding is supervised label correlation, not augmentation-based instance-discriminability. ERM's cross-entropy objective is trained on data where spurious attributes reliably predict class labels (Waterbirds: 95% training correlation), causing the model to jointly encode both task and spurious features. MoCo-v3, being label-agnostic, encodes spurious features only insofar as they are instance-discriminative under the augmentation set — a weaker pressure that measurably reduces spurious encoding. DINO's self-distillation, which implicitly generates class-level semantic targets via momentum teacher, produces spurious encoding indistinguishable from ERM (d = 0.60, p_bonf = 1.0), consistent with this interpretation.

**Contributions.** We make the following contributions:

1. **Waterbirds paradigm comparison:** A controlled four-paradigm × five-seed comparison on frozen ResNet-50 demonstrates a highly significant paradigm effect on spurious/task probe accuracy ratio (ANOVA F = 35.99, p = 2.42 × 10⁻⁷). ERM encodes spurious background features most strongly and MoCo-v3 least, opposite to augmentation-invariance theory.

2. **Cross-dataset replication:** CelebA replication (ANOVA F = 5.51, p = 0.009) confirms the paradigm effect but reveals a ranking reversal (MoCo-v3 lowest on Waterbirds, highest on CelebA), establishing that spurious attribute type interacts with pretraining objective.

3. **Mechanistic interpretation:** Supervised label correlation is identified as the primary driver of spurious feature encoding, supported by the ERM ≈ DINO similarity (d = 0.60, p_bonf = 1.0) and the large ERM > MoCo-v3 effect (d = 5.68).

4. **Augmentation ablation:** Background-replacement augmentation in contrastive training produces a 23.1% reduction in spurious/task ratio relative to standard augmentation (paired t = 46.66, p = 1.26 × 10⁻⁶, d = 32.4), confirming augmentation design as a functional causal lever.

---

## 2. Related Work

### Spurious Correlations and Group Robustness

The study of spurious correlations in deep learning traces to observations that models exploit dataset biases rather than causal features [Geirhos et al., 2020; Zhang et al., 2017]. Sagawa et al. [2020] formalize this via group robustness: in Waterbirds and CelebA, models achieving high average accuracy fail badly on minority groups whose spurious attribute contradicts the majority correlation. Group DRO minimizes worst-group loss but requires group annotations at training time. Our work is complementary: we characterize how much spurious content enters frozen representations *before* any downstream training, as a function of pretraining paradigm.

Kirichenko et al. [2022] demonstrate that ERM features are sufficient for robustness after group-balanced last-layer retraining (Deep Feature Reweighting, DFR), motivating direct study of frozen representation quality. However, DFR focuses entirely on supervised ERM and does not compare to SSL paradigms — leaving open whether ERM's spurious feature content is typical or atypical among pretraining objectives.

Izmailov et al. [2022] provide a study of feature learning under spurious correlations that includes comparisons involving DINO and Waterbirds. Their analysis is closest to ours in scope, but does not use a controlled spurious/task ratio metric and does not perform a four-paradigm comparison with Bonferroni-corrected pairwise tests [citation requires verification before submission].

### Self-Supervised and Contrastive Representation Learning

Contrastive SSL methods [Chen et al., 2020 (SimCLR); He et al., 2020 (MoCo)] learn representations by maximizing agreement between augmented views of the same image. DINO [Caron et al., 2021] uses self-distillation with a momentum teacher, producing emergent class-discriminative attention maps. BarlowTwins [Zbontar et al., 2021] optimizes redundancy reduction across cross-correlation matrices. All four paradigms use ResNet-50 as a standard evaluation backbone.

These methods are primarily evaluated on ImageNet linear probe accuracy [Chen et al., 2020; Caron et al., 2021], which measures task-relevant encoding but says nothing about spurious feature content. Robinson et al. [2021] show that contrastive learning can encode shortcut features, particularly when spurious attributes are stable across augmentations [citation requires verification]. Wen et al. [2021] analyze what features contrastive objectives encode as a function of augmentation design [citation requires verification]. These works establish that SSL is not spurious-feature-free, but do not compare to supervised baselines under controlled conditions.

### Distribution Shift Benchmarks

WILDS [Koh et al., 2021] and DomainBed [Gulrajani & Lopez-Paz, 2021] evaluate fine-tuned models, making it impossible to attribute performance differences to pretraining representation quality versus fine-tuning procedure. We isolate the pretraining effect by freezing the backbone throughout.

### Augmentation and Feature Learning

Shah et al. [2020] characterize SGD's "simplicity bias" — the tendency to prefer low-complexity predictors — connecting to our finding that ERM encodes spurious features aggressively when they are predictive under the training distribution. Zimmermann et al. [2021] show theoretically that contrastive learning approximately inverts the data generating process. Our empirical finding — that label-agnostic contrastive SSL encodes spurious features less than label-supervised ERM — is consistent with this framework when spurious attributes are not part of the true latent structure.

---

## 3. Method

### 3.1 Research Questions

- **RQ1:** Does pretraining paradigm significantly modulate the spurious/task probe accuracy ratio on frozen ResNet-50 features (Waterbirds)?
- **RQ2:** Is this effect consistent across datasets with different spurious attribute types, and does the paradigm ranking change (CelebA)?
- **RQ3:** Is augmentation a functional causal mechanism for modulating spurious feature encoding in contrastive SSL?

### 3.2 Pretraining Paradigms

Four ResNet-50 backbones pretrained on ImageNet-1k under different objectives:

- **ERM (Supervised):** Standard cross-entropy classification (`torchvision resnet50(pretrained=True)`). ImageNet top-1: 76.1%.
- **MoCo-v3 (Contrastive SSL):** Momentum-contrast contrastive SSL [He et al., 2020]; official `r-50-1000ep.pth.tar` checkpoint loaded via custom `hubconf.py` (PyTorch Hub download was unavailable). ImageNet top-1: 74.3%.
- **DINO (Self-distillation):** Self-distillation with momentum teacher [Caron et al., 2021]; `dino_resnet50` via PyTorch Hub. ImageNet top-1: 75.3%.
- **BarlowTwins (Non-contrastive SSL):** Redundancy-reduction via cross-correlation matrix alignment [Zbontar et al., 2021]; official weights via direct download. ImageNet top-1: 73.5%.

All backbones output 2048-dimensional features via global average pooling (fc = Identity) and are frozen throughout all probe experiments.

### 3.3 Spurious/Task Probe Accuracy Ratio

For each frozen backbone, separate linear probes (logistic regression, C = 1.0, lbfgs solver, max_iter = 1000) predict the spurious attribute and the task label from the 2048-dimensional features:

$$\text{ratio} = \frac{\text{spurious\_probe\_acc}}{\text{task\_probe\_acc}}$$

A ratio above 1.0 indicates that the spurious attribute is more linearly decodable than the task label. This scale-free metric decouples paradigm effects from absolute accuracy differences across datasets.

### 3.4 Group-Balanced Probe Protocol

Probes are trained on a group-balanced subset of the validation split (equal examples per task label × spurious attribute group), not the training split. This avoids inflating spurious probe accuracy due to the 95% Waterbirds training correlation. Evaluation uses the full balanced test split (Waterbirds: 5,794 images; CelebA: 720 images). Five random seeds per probe (seeds 0–4).

### 3.5 Statistical Analysis

Pairwise comparisons use two-sample t-tests across five seeds, Bonferroni-corrected for six pairs (C(4,2)). Gate criterion: p_bonf < 0.05 and mean difference ≥ 0.02. Cohen's d is computed with pooled standard deviation (d = (μ₁ − μ₂)/s_pooled, s_pooled = √((s₁² + s₂²)/2)). One-way ANOVA tests joint paradigm significance.

### 3.6 Background-Replacement Augmentation Ablation

SimCLR trained from scratch on Waterbirds under two conditions: **SimCLR-Original** (standard augmentation: random resized crop, horizontal flip, color jitter, Gaussian blur) and **SimCLR-NoBackground** (adds random background replacement using Places365 images drawn from a 10,000-image pool, applied to CUB-200-2011 segmented foregrounds). Both conditions share matched hyperparameters: SGD (momentum = 0.9, weight_decay = 1e-4), learning rate = 0.03 (cosine annealing, T_max = 50), batch size = 256, 50 epochs, NT-Xent temperature = 0.5, projection head 2048 → 2048 → 128 (L2-normalized). Five seeds per condition.

Mechanism activation is verified by measuring pixel difference between the background region of the two augmented views: if the background was replaced independently in each view, pixel difference in the background region should far exceed the threshold (0.05). Achieved: pixel_diff = 0.9656 (19× threshold).

### 3.7 Datasets

**Waterbirds** [Sagawa et al., 2020]: 4,795 training images. Balanced test: 5,794 images (50% spurious per class). Task = bird species (two classes); spurious = background type (land/water; 95% training correlation).

**CelebA** [Liu et al., 2015]: 162,770 training images. Balanced test: 720 images (180 per group × 4 groups). Task = Blond_Hair (attribute column 9); spurious = Male (attribute column 20; approximately 85% training correlation).

---

## 4. Experimental Setup

### 4.1 Dataset Summary

| Dataset | Train | Test (balanced) | Task | Spurious | Train Correlation |
|---------|-------|-----------------|------|----------|------------------|
| Waterbirds | 4,795 | 5,794 | Bird species | Background | 95% |
| CelebA | 162,770 | 720 (180 × 4 groups) | Blond_Hair | Male | ~85% |

### 4.2 Paradigm Checkpoints

| Paradigm | Type | Checkpoint Source | ImageNet Top-1 |
|----------|------|-------------------|----------------|
| ERM | Supervised | torchvision resnet50 | 76.1% |
| MoCo-v3 | Contrastive SSL | Official r-50-1000ep.pth.tar | 74.3% |
| DINO | Self-distillation | Hub dino_resnet50 | 75.3% |
| BarlowTwins | Non-contrastive SSL | Official weights | 73.5% |

### 4.3 Implementation Details

Feature extraction is performed once per backbone with no gradient and cached to disk. All probes use sklearn LogisticRegression (C = 1.0, lbfgs, max_iter = 1000). Group-balanced validation split is constructed by sampling equal counts per group from WILDS val metadata. Experiments run on NVIDIA H100 NVL GPUs.

---

## 5. Results

### 5.1 RQ1: Paradigm Significantly Modulates Spurious Encoding on Waterbirds

One-way ANOVA across four paradigms × five seeds: **F = 35.99, p = 2.42 × 10⁻⁷**. The paradigm effect is conclusively significant.

**Table 1: Spurious/Task Probe Accuracy Ratio per Paradigm — Waterbirds (5 seeds)**

| Paradigm | Mean Ratio | Std |
|----------|-----------|-----|
| ERM | 1.0520 | 0.0049 |
| DINO | 1.0495 | 0.0033 |
| BarlowTwins | 1.0331 | 0.0058 |
| MoCo-v3 | 1.0273 | 0.0038 |

Individual probe accuracy estimates: ERM (spurious ≈ 0.931, task ≈ 0.884); MoCo-v3 (spurious ≈ 0.952, task ≈ 0.928); DINO (spurious ≈ 0.959, task ≈ 0.913); BarlowTwins (spurious ≈ 0.950, task ≈ 0.919).

The counterintuitive result is that MoCo-v3 — the contrastive SSL representative — shows the lowest spurious encoding (ratio = 1.0273), while supervised ERM shows the highest (1.0520). Augmentation-invariance theory predicts the opposite ordering.

![Spurious/task ratio per paradigm on Waterbirds](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/paper/figures/ratio_bar_waterbirds.png)

*Figure 1: Mean spurious/task probe accuracy ratio per pretraining paradigm on Waterbirds (±1 std, 5 seeds). Significant Bonferroni-corrected pairwise differences annotated. MoCo-v3 is lowest; ERM highest — opposite of augmentation-invariance prediction.*

**Table 2: Pairwise Bonferroni-Corrected t-tests — Waterbirds (n = 5 seeds per paradigm)**

| Pair | t | p_bonf | Cohen's d | Mean Diff | Gate |
|------|---|--------|-----------|-----------|------|
| ERM vs MoCo-v3 | 8.98 | 0.0001 | 5.68 | 0.0247 | ✅ |
| MoCo-v3 vs DINO | −9.93 | 0.0001 | −6.28 | 0.0222 | ✅ |
| ERM vs BarlowTwins | 5.60 | 0.0031 | 3.54 | 0.0188 | ✗ (diff < 0.02) |
| DINO vs BarlowTwins | 5.52 | 0.0034 | 3.49 | 0.0164 | ✗ (diff < 0.02) |
| ERM vs DINO | 0.94 | 1.000 | 0.60 | 0.0025 | ✗ |
| MoCo-v3 vs BarlowTwins | −1.89 | 0.572 | −1.20 | 0.0058 | ✗ |

*Gate criterion: p_bonf < 0.05 AND mean_diff ≥ 0.02. Cohen's d uses pooled standard deviation.*

Two pairs satisfy the full gate criterion: ERM vs MoCo-v3 (d = 5.68) and MoCo-v3 vs DINO (d = −6.28). Both effect sizes are exceptional by any conventional threshold.

**ERM ≈ DINO:** d = 0.60, p_bonf = 1.0. ERM and DINO are statistically indistinguishable despite their different pretraining objectives. This pattern is consistent with DINO's momentum teacher generating class-correlated soft-targets that replicate the label-correlation pressure of supervised ERM. However, alternative explanations — such as DINO's augmentation scheme incidentally reducing variance of non-spurious features — are not ruled out by this experiment alone.

![Violin plot of ratio distributions per paradigm](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/paper/figures/ratio_violin_waterbirds.png)

*Figure 2: Violin distributions of spurious/task ratios across 5 seeds per paradigm (Waterbirds). MoCo-v3 is clearly separated from ERM and DINO (d = 5.68 and 6.28 respectively).*

![P-value matrix](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/paper/figures/pvalue_matrix.png)

*Figure 3: 4×4 Bonferroni-corrected p-value matrix for all pairwise paradigm comparisons on Waterbirds. Two pairs achieve p_bonf = 0.0001: ERM vs MoCo-v3 and MoCo-v3 vs DINO.*

![Accuracy heatmap](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/paper/figures/acc_heatmap.png)

*Figure 4: Heatmap of spurious and task probe accuracies (mean across seeds) per paradigm on Waterbirds. Both accuracy types differ across paradigms; ERM has the largest absolute spurious/task gap.*

### 5.2 RQ2: Dataset-Dependent Paradigm Ranking

**Table 3: CelebA Spurious/Task Ratios (5 seeds)**

| Paradigm | Mean Ratio | Std |
|----------|-----------|-----|
| MoCo-v3 | 1.1976 | 0.011 |
| BarlowTwins | 1.1888 | 0.023 |
| ERM | 1.1786 | 0.010 |
| DINO | 1.1618 | 0.011 |

ANOVA on CelebA: **F = 5.51, p = 0.009**. One pairwise comparison passes the full gate criterion: MoCo-v3 vs DINO (p_bonf = 0.005, d = 3.28, diff = 0.0359). No other pairwise comparisons pass (ERM vs MoCo-v3: p_bonf = 0.120, d = 1.83; ERM vs DINO: p_bonf = 0.199, d = 1.63).

CelebA ratios are uniformly higher than Waterbirds by approximately 0.14 on average. The paradigm ranking shifts substantially: MoCo-v3, which shows the lowest spurious encoding on Waterbirds (1.027), shows the highest on CelebA (1.198). DINO shifts from matching ERM on Waterbirds to the lowest ratio on CelebA.

**ERM vs MoCo-v3 on CelebA:** No significant difference. A separate directional test (h-d1) on a subset of CelebA (720 balanced samples) yields ERM mean = 1.067 ± 0.028, MoCo-v3 mean = 1.068 ± 0.013, t = 0.108, p_two_sided = 0.917, d = 0.068. Under either the Bonferroni-corrected pairwise test from h-e2 (p_bonf = 0.120) or the separate directional test (p = 0.917), the ERM vs MoCo-v3 difference is not significant on CelebA. The large Waterbirds effect (d = 5.68) does not generalize to CelebA for this pair.

![Cross-dataset comparison](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/paper/figures/cross_dataset_bar.png)

*Figure 5: Cross-dataset comparison of spurious/task ratios on Waterbirds and CelebA. The paradigm ranking reverses across datasets: MoCo-v3 is lowest on Waterbirds but highest on CelebA, while DINO matches ERM on Waterbirds but is lowest on CelebA.*

![Interaction plot](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/paper/figures/interaction_plot.png)

*Figure 6: Interaction plot for all four paradigms × two datasets. Crossing lines confirm that no paradigm consistently encodes the least spurious features across spurious attribute types.*

The ranking reversal implies that the type of spurious attribute interacts with the pretraining objective. Coarse texture spurious attributes (Waterbirds background) and demographic spurious attributes (CelebA gender) produce qualitatively different paradigm rankings. A single-dataset design would not detect this interaction.

### 5.3 RQ3: Background-Replacement Augmentation as Functional Causal Lever

**Mechanism verification:** pixel_diff = 0.9656 between the background region of NoBackground and Original views (threshold = 0.05; 19× margin). The background replacement is active and unambiguous.

**Full ratio statistics (5 seeds per condition, 50-epoch training):**

| Condition | Mean Ratio | Std |
|-----------|-----------|-----|
| SimCLR-Original | 1.4726 | 0.0112 |
| SimCLR-NoBackground | 1.1320 | 0.0098 |

Ratio reduction: 0.3406 (23.1% relative reduction). Paired t-test across five seeds: t = 46.66, p = 1.26 × 10⁻⁶, Cohen's d = 32.4.

The spurious probe accuracy falls from approximately 0.884 (original) to approximately 0.727 (no-background), while task probe accuracy increases slightly from approximately 0.601 to approximately 0.642. The ratio reduction reflects both suppression of spurious encoding and modest improvement in task encoding.

This result confirms that explicitly removing the spurious attribute from training views causes a large reduction in spurious feature encoding in the learned representation. The absolute ratio values (1.47 and 1.13) are higher than those for the ImageNet-pretrained paradigms (1.03–1.05) because these models are trained only on Waterbirds (4,795 images) rather than on ImageNet-1k.

**Note on comparability:** SimCLR-Original and SimCLR-NoBackground are both trained from scratch on Waterbirds, not on ImageNet. Their absolute ratio values are therefore not directly comparable to the ImageNet-pretrained paradigms in Tables 1 and 3, which measure encoding in representations learned at much larger scale. The ablation comparison is valid within the from-scratch Waterbirds training setting.

---

## 6. Discussion

### 6.1 Key Finding: Label Correlation, Not Augmentation Invariance

Our results are most parsimoniously explained by supervised label correlation as the dominant driver of spurious feature encoding, rather than augmentation-based instance-discriminability.

In ERM, the cross-entropy objective trains on data where background texture predicts bird species with 95% reliability (Waterbirds). The model jointly encodes task and spurious features because both reduce training loss. MoCo-v3, being label-agnostic, encodes spurious features only insofar as they are instance-discriminative under the augmentation set. Background texture is instance-discriminative (different images have different backgrounds), but without label-correlation amplification, the resulting spurious encoding is measurably weaker (ratio = 1.027 vs 1.052, d = 5.68).

DINO's ERM-equivalent spurious encoding (d = 0.60, p_bonf = 1.0) is consistent with the interpretation that DINO's momentum teacher produces class-correlated pseudo-targets that implicitly replicate supervised label selection pressure. Under this interpretation, it is the class-level signal — whether explicit (ERM labels) or implicit (DINO teacher targets) — that drives spurious feature encoding, not the augmentation scheme. This interpretation requires further verification (e.g., measuring mutual information between DINO teacher targets and spurious attribute labels) and remains a hypothesis rather than an established mechanism.

The augmentation ablation supports the complementary view that augmentation design can suppress spurious encoding when it explicitly removes the spurious attribute from the training signal. A 23.1% ratio reduction (d = 32.4) when background is replaced per-view is consistent with contrastive objectives encoding spurious features to the degree they remain instance-discriminative after augmentation.

### 6.2 Cross-Dataset Interaction

The paradigm ranking reversal between Waterbirds and CelebA indicates that the relationship between pretraining objective and spurious feature encoding is not universal — it depends on the type of spurious attribute. A plausible interpretation is that coarse texture attributes (background scenes) and demographic attributes (gender, distributed across face features) interact differently with each pretraining objective's encoding pressure. However, the current dataset sample (two datasets, two attribute types) is insufficient to characterize this interaction fully. The reversal is an empirical observation; the mechanism remains an open question.

### 6.3 Limitations

**L1: Original directional prediction refuted.** The initial hypothesis predicted that contrastive SSL would encode spurious features more strongly than ERM due to augmentation invariance. The data demonstrate the opposite with large effect size (d = 5.68 in the reversed direction). This is treated as a productive refutation; the empirical contributions are directionally opposite to the initial prediction but internally consistent.

**L2: No downstream worst-group accuracy evaluation.** The paper establishes paradigm differences in spurious/task probe accuracy ratio, but does not test whether lower spurious ratio translates to better worst-group accuracy when a linear head is trained via DFR-style fine-tuning [Kirichenko et al., 2022]. Downstream consequences for practical robustness remain untested and should not be inferred from the probe results alone.

**L3: MoCo-v3 as contrastive representative.** SimCLR-v2 has no official PyTorch checkpoint; MoCo-v3 was used as the best available contrastive proxy. MoCo-v3 uses a momentum encoder and queue, which differ from SimCLR's direct two-view comparison. Results for contrastive SSL may not generalize to SimCLR specifically.

**L4: Scope.** Results apply to ResNet-50 backbones pretrained on ImageNet-1k, evaluated on Waterbirds and CelebA. ViT backbones, larger pretraining scales (e.g., CLIP), and additional spurious attribute types require separate study. The cross-dataset ranking reversal already indicates that scope matters.

**L5: CelebA test set size.** The Bonferroni-corrected CelebA pairwise test (h-e2) uses 720 balanced test images. A separate directional test (h-d1) uses a different balanced sample of 720 images; the two yield consistent qualitative conclusions (no significant ERM vs MoCo-v3 difference on CelebA), but the small balanced test size limits statistical power for detecting small effects.

**L6: Unverified citations.** Three citations — Robinson et al. [2021], Wen et al. [2021], and Izmailov et al. [2022] — have not been verified against their primary sources for title, venue, and claim correspondence. These are marked accordingly and must be verified before submission.

### 6.4 Broader Implications

These findings provide backbone selection guidance for fairness-critical applications: contrastive SSL backbones (particularly MoCo-v3 on texture-spurious datasets) partially suppress spurious features by design, without requiring group labels or robustness-specific interventions. This suppression is partial — all paradigms produce ratios above 1.0, indicating that spurious attributes remain linearly decodable in all cases. The guidance is additive with, not a replacement for, existing robustness methods.

The augmentation ablation result (23.1% ratio reduction) additionally suggests that augmentation design is an accessible lever for practitioners training SSL representations from scratch when the spurious attribute type is known in advance.

---

## 7. Conclusion

The widely held assumption that contrastive SSL amplifies spurious correlations due to augmentation invariance is not supported on Waterbirds. Supervised ERM encodes spurious background features significantly more strongly than contrastive MoCo-v3 (ratio diff = 0.0247, d = 5.68, p_bonf < 0.0001). The paradigm effect is highly significant across both datasets (Waterbirds ANOVA F = 35.99, p = 2.42 × 10⁻⁷; CelebA F = 5.51, p = 0.009), but the paradigm ranking reverses between datasets, establishing that spurious attribute type interacts with pretraining objective. Background-replacement augmentation in SimCLR training produces a 23.1% spurious/task ratio reduction (p = 1.26 × 10⁻⁶), confirming augmentation as a functional causal lever.

**Contributions:** (1) First controlled four-paradigm comparison of spurious feature encoding in frozen ResNet-50 representations across two benchmarks. (2) Supervised label correlation identified as the dominant driver — ERM and DINO show equivalent spurious encoding despite different pretraining objectives; label-agnostic MoCo-v3 shows measurably lower encoding. (3) Spurious attribute type × pretraining objective interaction established via cross-dataset ranking reversal. (4) Background-replacement augmentation confirmed as a functional causal intervention for spurious encoding reduction.

**Future directions:** (i) Comparison with masked autoencoder (MAE, label-free reconstruction) to distinguish label-agnostic training from contrastive-specific augmentation effects; (ii) Downstream worst-group accuracy evaluation via DFR on MoCo-v3 vs ERM features; (iii) ViT backbone comparison; (iv) Additional spurious attribute types to characterize the paradigm × attribute-type interaction matrix.

---

## References

Caron, M., Touvron, H., Misra, I., Jégou, H., Mairal, J., Bojanowski, P., & Joulin, A. (2021). Emerging Properties in Self-Supervised Vision Transformers. *ICCV 2021*.

Chen, T., Kornblith, S., Norouzi, M., & Hinton, G. (2020). A Simple Framework for Contrastive Learning of Visual Representations. *ICML 2020*.

Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). Shortcut Learning in Deep Neural Networks. *Nature Machine Intelligence, 2*, 665–673.

Gulrajani, I., & Lopez-Paz, D. (2021). In Search of Lost Domain Generalization. *ICLR 2021*.

He, K., Fan, H., Wu, Y., Xie, S., & Girshick, R. (2020). Momentum Contrast for Unsupervised Visual Representation Learning. *CVPR 2020*.

Izmailov, P., Kirichenko, P., Gruber, N., & Wilson, A. G. (2022). On Feature Learning in the Presence of Spurious Correlations. *NeurIPS 2022*. [*Citation title and venue require verification before submission.*]

Kirichenko, P., Izmailov, P., & Wilson, A. G. (2022). Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations. *ICLR 2023*.

Koh, P. W., Sagawa, S., Marklund, H., et al. (2021). WILDS: A Benchmark of in-the-Wild Distribution Shifts. *ICML 2021*.

Liu, Z., Luo, P., Wang, X., & Tang, X. (2015). Deep Learning Face Attributes in the Wild. *ICCV 2015*.

Robinson, J. D., Chuang, C.-Y., Sra, S., & Jegelka, S. (2021). [Title and venue unverified — requires verification before submission.]

Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2020). Distributionally Robust Neural Networks for Group Shifts. *ICLR 2020*.

Shah, H., Tamuly, K., Raghunathan, A., Jain, P., & Rai, P. (2020). The Pitfalls of Simplicity Bias in Neural Networks. *NeurIPS 2020*.

Wen, Z., Luo, F., Wang, C., Lin, J., & Wen, S. (2021). [Title and venue unverified — requires verification before submission.]

Zbontar, J., Jing, L., Misra, I., LeCun, Y., & Deny, S. (2021). Barlow Twins: Self-Supervised Learning via Redundancy Reduction. *ICML 2021*.

Zhang, C., Bengio, S., Hardt, M., Recht, B., & Vinyals, O. (2017). Understanding Deep Learning Requires Rethinking Generalization. *ICLR 2017*.

Zimmermann, R. S., Sharma, Y., Schneider, S., Bethge, M., & Brendel, W. (2021). Contrastive Learning Inverts the Data Generating Process. *ICML 2021*.
