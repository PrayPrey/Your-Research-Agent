# Related Work

Our work intersects three research areas: self-supervised learning fairness, spurious correlation detection, and geometric analysis of learned representations. We position our contribution by identifying gaps in each area.

## Self-Supervised Learning and Fairness

Recent advances in self-supervised learning (Chen et al., 2020; He et al., 2020) have achieved competitive performance with supervised methods across diverse computer vision tasks. However, SSL models trained on biased datasets inherit and amplify spurious correlations. Mehta et al. (2022) demonstrated that high-capacity SSL models (ViT-H-14 with 600M parameters) achieve 88.5-90% worst-group accuracy on Waterbirds using frozen embeddings and linear ERM, significantly outperforming supervised baselines. This empirical success suggests that SSL embeddings encode fairness-relevant structure, but the geometric nature of this structure remains uncharacterized.

Learning-speed aware SSL (LA-SSL) (Zhu et al., 2023) improves fairness by resampling training data based on per-sample learning dynamics, upweighting slow-learning samples that typically belong to minority groups. LA-SSL achieves WGA improvements of 2-5 percentage points across multiple spurious correlation benchmarks. However, the mechanistic explanation for why learning-speed resampling improves fairness remains theoretical. Our work provides the first empirical test of the hypothesis that LA-SSL operates by dispersing spurious cluster structure.

**Gap:** Prior SSL fairness work demonstrates that linear classifiers achieve high WGA, creating the impression that geometric cluster structure exists. However, no work has directly measured embedding clusterability or tested whether clusterability predicts intervention efficacy. We fill this gap by providing the first AMI measurements of SSL embeddings on spurious correlation datasets.

## Spurious Correlation Detection and Mitigation

Supervised methods for handling spurious correlations typically require group labels. GroupDRO (Sagawa et al., 2020) reweights training samples by group to maximize worst-group performance, achieving WGA improvements of 10.9 percentage points on Waterbirds. Just Train Twice (JTT) (Liu et al., 2021) identifies error-prone samples in an initial training phase and upweights them in a second phase, improving WGA without explicit group labels. GEORGE (Sohoni et al., 2021) clusters embeddings to discover subgroups and applies group-aware reweighting, achieving competitive performance with label-based methods.

These cluster-based approaches assume that spurious features manifest as discrete, separable clusters that can be identified via k-means or similar algorithms. However, this assumption has not been validated. Our work tests whether this geometric assumption holds in SSL settings.

**Gap:** Existing cluster-based mitigation methods (JTT, GEORGE) assume clusters exist but do not measure clusterability or test the cluster assumption. If spurious features form continuous gradients rather than discrete clusters, these methods may fail or succeed for unrelated reasons. We provide direct evidence that clusters do not form under standard SSL training.

## Geometric Analysis of Learned Representations

Research on representation geometry has revealed important properties of learned embeddings. Ethayarajh (2019) showed that contextual embeddings in language models suffer from anisotropy, where word vectors occupy a narrow cone in embedding space. Gao et al. (2019) demonstrated that this degeneracy harms downstream task performance. In computer vision, Wang and Isola (2020) analyzed contrastive learning through the lens of uniformity and alignment, showing that InfoNCE loss creates uniformly distributed representations on the unit hypersphere.

However, this prior work focuses on overall embedding geometry, not the specific geometric structure of spurious features within the embedding space. Our contribution is to characterize how spurious correlations manifest geometrically in SSL embeddings, revealing that they form continuous gradients rather than discrete clusters.

**Gap:** No prior work has measured the geometric clusterability of spurious features in SSL embeddings using clustering metrics like AMI. Geometric analysis has focused on global properties (uniformity, anisotropy) rather than subgroup structure relevant to fairness.

## Positioning Our Work

Our work is the first to:
1. Directly measure embedding clusterability (AMI) for spurious correlation detection in SSL settings
2. Empirically test whether clusterability predicts cluster-based intervention efficacy
3. Evaluate the mechanistic hypothesis that LA-SSL operates via geometric cluster dispersion

By falsifying the cluster hypothesis, we eliminate an incorrect mechanistic theory and redirect SSL fairness research toward linear separability-based diagnostics that better match the actual geometric structure of spurious features.
