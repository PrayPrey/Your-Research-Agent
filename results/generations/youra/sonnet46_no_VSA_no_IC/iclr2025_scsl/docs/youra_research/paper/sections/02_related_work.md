## 2. Related Work

### 2.1 Group-Robust Training

The canonical approach to worst-group accuracy degradation is Group Distributionally Robust Optimization (Group DRO) [Sagawa et al., 2019], which minimizes the worst-case expected loss across predefined groups. Group DRO and its variants achieve 84–91% WGA on Waterbirds and CelebA — but require group annotations at training time. G2-SAM [Ji et al., 2025] extends this to SAM-based optimization, applying group-wise perturbation to reduce per-group sharpness in supervised settings. G2-SAM demonstrates that sharpness reduction improves worst-group accuracy — the geometric evidence that motivates our SSL extension. However, G2-SAM requires explicit group labels and operates in supervised cross-entropy settings; we remove both constraints.

Domain-Generalization SAM (DGSAM) [Song et al., 2025] applies SAM variants to domain generalization — train-to-test distribution shift — rather than within-distribution subgroup robustness. Our setting is orthogonal: we target spurious correlations where train and test distributions share the same label-spurious feature structure.

### 2.2 Annotation-Free Debiasing

Several methods achieve group robustness without group labels. Just Train Twice (JTT) [Liu et al., 2021] trains an initial model, identifies misclassified samples as likely minority examples, and upweights them in a second training run. Loss-based Feature Resampling (LFR) [Ghaznavi et al., 2023] uses high-loss samples from an initial linear probe as a proxy for minority group membership, enabling annotation-free resampling that matches oracle-labeled performance on Waterbirds and CelebA. EVaLS [Ghaznavi et al., 2024] extends LFR with environment inference for model selection. Environment Inference for Invariant Learning (EIIL) [Creager et al., 2021] infers environment structure from gradient statistics.

All of these methods operate *post-hoc on fixed representations*: they take an SSL or ERM model as given and apply downstream reweighting. They cannot change the geometric structure of the representation itself. Our approach instead intervenes during SSL pretraining — the geometric formation phase — to produce representations with lower spurious anisotropy from the start.

### 2.3 SSL and Spurious Correlations

Izmailov et al. [2022] demonstrated that SSL models (SimCLR, DINO, Barlow Twins) can achieve competitive worst-group accuracy on Waterbirds and CelebA with appropriate feature retraining (DFR), suggesting SSL representations contain the necessary information for core-feature classification. Zhang & Ré [2022] documented that CLIP models exhibit severe spurious correlation sensitivity despite strong average performance — a pattern consistent with our DINO findings. Cross-Variant SSL [Yadav et al., 2026] addresses shortcut reliance by diversifying the augmentation pipeline with generative models, achieving 92.5% WGA on Waterbirds. This approach modifies what the SSL model *sees* (augmentation diversity) rather than how it *optimizes* (loss landscape geometry). Our work is complementary: augmentation changes the data distribution; SAM changes the curvature structure.

A recent NeurIPS 2025 paper applies spectral regularization to SSL to reduce shortcut reliance [CITATION NEEDED]. Its approach modifies the objective function rather than the optimizer, and does not provide geometric (sharpness anisotropy) characterization of the learned representations.

### 2.4 Loss Landscape Geometry and Simplicity Bias

SAM [Foret et al., 2021] finds flat minima by minimizing the maximum loss within a perturbation ball. Flat minima generalize better empirically and connect theoretically to implicit regularization. Gatmiry et al. [2024] prove that SAM promotes rank-1 (simplicity) bias in supervised cross-entropy settings — SAM in supervised learning tends to learn simpler (lower-rank) features first. Since spurious features are typically simpler (lower-rank) than core features, this creates a theoretical tension: does SAM increase or decrease shortcut reliance in SSL?

The Spectral Curvature-Embedding Representation (SCER) framework [Park et al., 2025] theoretically links embedding geometry to worst-group error in SSL settings, providing motivation for directional curvature analysis. However, SCER does not provide empirical measurements of sharpness anisotropy, and does not address optimizer-level interventions.

We bridge these lines: we bring the geometric sharpness analysis of the SAM literature to the SSL spurious correlation setting, providing the first empirical measurement protocol and the first application of SAM during SSL pretraining for shortcut reduction. The critical theoretical question — whether Gatmiry's simplicity bias transfers to InfoNCE objectives — is the central empirical question this work addresses.

| Method | Annotation-Free | SSL Pretraining | Geometric Diagnosis | Training-Time |
|--------|----------------|-----------------|---------------------|---------------|
| Group DRO [Sagawa 2019] | No | No | No | Yes |
| JTT [Liu 2021] | Yes | No | No | Yes (2-stage) |
| LFR [Ghaznavi 2023] | Yes | No | No | Post-hoc |
| G2-SAM [Ji 2025] | No | No | Yes (sharpness) | Yes |
| Cross-Variant SSL [Yadav 2026] | Yes | Yes | No | Yes (augment) |
| **Ours** | **Yes** | **Yes** | **Yes (anisotropy)** | **Yes (optimizer)** |
