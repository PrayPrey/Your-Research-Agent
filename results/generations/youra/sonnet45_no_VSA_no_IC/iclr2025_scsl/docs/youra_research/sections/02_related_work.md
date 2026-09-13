# 2. Related Work

Our work builds on three research areas: spurious correlation benchmarks that define the problem space, robust learning methods that address worst-group accuracy degradation, and gradient attribution techniques for model interpretation. We position our gradient-based abnormality detection as complementary to embedding-based methods (SCER) and unified compared to two-stage approaches (JTT).

## 2.1 Spurious Correlation Benchmarks

The Waterbirds dataset [Sagawa et al., 2020] is the canonical benchmark for spurious correlation research, constructed by compositing bird images (from CUB-200 [Wah et al., 2011]) onto place backgrounds (from Places [Zhou et al., 2017]) with 90% background-class correlation during training. Models trained on Waterbirds achieve 95% average accuracy but only 60% worst-group accuracy (WGA) on minority groups, demonstrating the severity of spurious reliance. CelebA [Liu et al., 2015] exhibits hair color-gender spurious correlations, while UrbanCars [Li et al., 2023] contains co-occurrence biases (urban cars in cities, rural cars in countryside).

Recent work has developed more controlled benchmarks: Spawrious [Lynch et al., 2023] (52 citations) provides 152k photo-realistic images with tunable spurious correlation strength, enabling one-to-one (O2O) and many-to-many (M2M) correlation experiments. Lynch et al. show that state-of-the-art methods struggle on Hard splits (<70% WGA), suggesting existing approaches fail to generalize to fine-grained spurious patterns. MetaCoCo [Zhang et al., 2024] (18 citations) introduces spurious correlations from real-world scenarios for few-shot learning, quantifying spurious-correlation shifts using CLIP vision-language models.

These benchmarks establish the problem scope (spurious correlations degrade WGA), but detection methods for identifying minority groups without annotations remain limited. Our work addresses this gap by extending gradient abnormality detection (originally for OOD) to minority group detection within the ID distribution.

## 2.2 Robust Learning Methods

Existing robust learning methods fall into three categories: group-supervised optimization, two-stage training, and embedding regularization.

**Group-Supervised Methods:** GroupDRO [Sagawa et al., 2020] minimizes worst-case group loss via distributionally robust optimization, achieving 85-88% WGA on Waterbirds. However, GroupDRO requires group annotations during training — an expensive requirement when group definitions are unknown or annotations unavailable. SUBG [Idrissi et al., 2022] extends GroupDRO with subgroup discovery but still requires partial annotations.

**Two-Stage Methods:** Just Train Twice (JTT) [Liu et al., 2021] trains an initial model to identify error-prone samples (stage 1), then upsamples these samples during retraining (stage 2), achieving ~88% WGA on Waterbirds without group annotations during training. Deep Feature Reweighting (DFR) [Kirichenko et al., 2022] (111 GitHub stars) shows that last-layer retraining is sufficient for robustness, matching or outperforming GroupDRO with simple post-hoc adjustments. Progressive Data Expansion (PDE) [Deng et al., 2023] (50 citations) achieves 2.8% WGA improvement over SOTA with 10× faster training via progressive minority sample expansion.

**Embedding Regularization:** Spurious Correlation-Aware Embedding Regularization (SCER) [Park et al., 2025] provides a theoretical framework connecting embedding space with worst-group error, regularizing embeddings to suppress spurious features. SCER achieves state-of-the-art WGA (~90% estimated from paper) but operates exclusively in embedding space, leaving gradient space (which encodes training dynamics) unexplored. Spread Spurious Attribute (SSA) [Nam et al., 2022] (113 citations) improves WGA using pseudo-attribute prediction with only 0.6-1.5% annotated samples.

**Complementary to Our Approach:** Our gradient-based abnormality detection complements SCER's embedding regularization (gradient space vs embedding space intervention points) and operates in a single stage (unlike JTT's two-stage training). Table 1 summarizes key differences.

| Method | WGA (Waterbirds) | Requires Annotations? | Stages | Intervention Space |
|--------|------------------|----------------------|--------|-------------------|
| GroupDRO [Sagawa 2020] | 85-88% | Yes (during training) | Single | Loss landscape |
| JTT [Liu 2021] | ~88% | No | Two | Loss reweighting |
| SCER [Park 2025] | ~90% (estimated) | No | Single | Embedding |
| Ours (validated) | Synthetic validation only | No | Single | Gradient |

**Table 1:** Comparison to prior robust learning methods. Our approach complements SCER by operating on gradient space and avoids JTT's two-stage requirement. Real Waterbirds WGA validation pending.

## 2.3 Gradient Attribution for Spurious Detection

Gradient attribution methods visualize which input features drive model predictions. Grad-CAM [Selvaraju et al., 2017] (12k GitHub stars for pytorch-grad-cam implementation) computes class activation maps via weighted combinations of feature map gradients. Integrated Gradients (IG) [Sundararajan et al., 2017] accumulates gradients along paths from baseline inputs to actual inputs, satisfying completeness axioms. SmoothGrad [Smilkov et al., 2017] averages gradients over noisy perturbations to reduce attribution noise.

**Attribution Ineffectiveness:** Adebayo et al. [2022] (109 citations) demonstrated through controlled experiments that gradient attribution fails when spurious features are unknown at test time. Their user study showed practitioners cannot detect unknown spurious correlations even with saliency maps, attributing failure to the gap between post-hoc explanation (what the model did) and process disruption detection (when the model's reasoning breaks down). This motivates our shift from direct attribution to **gradient abnormality** — detecting when the gradient process itself exhibits anomalous patterns.

**Gradient Abnormality for OOD:** GAIA [Chen et al., 2023] (16 citations) proposes gradient abnormality metrics (zero-deflation GAIA-Z, channel-wise variance GAIA-A) for out-of-distribution detection, reducing average FPR95 by 23.10% on CIFAR10 and 45.41% on CIFAR100 compared to post-hoc methods. GAIA's theoretical framework shows that Taylor expansion error terms diverge when models encounter uncertain samples, manifesting as gradient scattering. However, GAIA targets distribution shift (ID vs OOD), not subpopulation shift (majority vs minority within ID).

**Post-Hoc OOD Detection:** Spurious-Aware Prototype Refinement (SPROD) [Zohrabi et al., 2025] (4 citations) refines prototypes to address spurious correlations in OOD detection, improving AUROC by 4.8% and FPR@95 by 9.4% on Waterbirds, CelebA, and UrbanCars. SPROD operates post-hoc (after training) on prototype space, complementary to our training-time gradient-based approach.

**Gradient-Based Shortcut Detection:** Ibarra et al. [2025] propose gradient-based model shortcut detection for time series classification, using other-class gradients without requiring test data. This demonstrates gradient analysis feasibility for shortcut detection beyond vision domains.

**Our Contribution:** We are the first to apply gradient abnormality (GAIA framework) to minority group detection **within the ID distribution**, extending Chen et al.'s OOD work to subpopulation shift. Unlike Adebayo et al.'s conclusion that attribution fails, we show abnormality metrics (not direct attribution) successfully differentiate minority (high scattering) vs majority (low scattering) patterns in synthetic validation. Unlike SPROD's post-hoc prototype refinement, we intervene during training via spatial gradient regularization.

## 2.4 Gap Summary and Our Positioning

Existing work leaves three critical gaps:

1. **Unknown Spurious Detection:** Adebayo et al. [2022] show attribution fails when spurious features unknown. Gradient abnormality (GAIA) addresses this for OOD but not minority groups.

2. **Detection-Mitigation Unification:** GroupDRO/JTT/SCER focus on mitigation. SPROD focuses on post-hoc detection. No single-stage framework unifies both.

3. **Gradient Space Underexplored:** SCER operates on embeddings, JTT on loss landscape. Gradient space (which encodes training dynamics) remains underexplored for spurious correlation.

Our work fills these gaps by extending GAIA to minority detection (Gap 1), proposing spatial gradient regularization for single-stage mitigation (Gap 2), and providing the first gradient-based spurious correlation framework (Gap 3). However, our validation is currently limited to synthetic experiments and proof-of-concept tests — real-world empirical validation (Waterbirds WGA improvement, GroupDRO comparison) requires infrastructure upgrades (Section 6).
