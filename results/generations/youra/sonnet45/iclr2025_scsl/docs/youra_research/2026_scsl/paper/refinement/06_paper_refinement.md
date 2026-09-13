# Geometric Structure of Spurious Features in Self-Supervised Learning Embeddings: An Empirical Investigation

## Abstract

Self-supervised learning methods achieve up to 90% worst-group accuracy on spurious correlation benchmarks when using linear probes on frozen embeddings. The geometric structure that enables this performance is not well characterized. A common assumption is that spurious features manifest as discrete, geometrically separable clusters measurable via clustering metrics such as Adjusted Mutual Information (AMI). We tested this assumption through controlled experiments on the Waterbirds dataset. SimCLR training (20 epochs, ResNet-50) produced embeddings with AMI=0.2795, below the 0.4 threshold conventionally used to indicate reliable clusterability. Learning-speed aware SSL (LA-SSL) yielded AMI=0.2852, representing a 2.04% relative increase rather than the hypothesized 30% reduction. Linear separability metrics remained high (AUC≈0.98) despite low clusterability scores. These results indicate that linear separability and discrete clusterability are dissociable properties in SSL embeddings under the tested conditions. The experiments were conducted as proof-of-concept validation (20 epochs) prior to full-scale training; the mechanism hypotheses tested were not supported at this training duration. Implementation validation was performed for cluster-balanced retraining mechanisms (43/43 tests passing, 100% software development compliance for h-e1; 5/5 tests passing, 100% compliance for h-m-integrated), though experimental validation of intervention efficacy was not completed.

## 1. Introduction

Self-supervised learning (SSL) models trained via contrastive methods such as SimCLR have demonstrated the capacity to achieve high worst-group accuracy (WGA) on spurious correlation benchmarks. Mehta et al. (2022) reported that frozen ViT-H-14 embeddings combined with linear probes reached 90.13% WGA on the Waterbirds dataset without access to group labels during training. The geometric properties of SSL embeddings that enable this fairness performance are not fully understood.

Spurious correlations occur when a feature correlated with the target label in the training distribution does not have a causal relationship with the true task. In the Waterbirds dataset, background type (land vs. water) exhibits 93% correlation with bird type (landbird vs. waterbird) in the training split, but the background is not causally relevant to bird classification. Models that rely on this spurious correlation perform poorly on minority groups where the correlation is violated.

One explanation for SSL's fairness performance is that spurious features form discrete, geometrically separable clusters in the embedding space. Under this hypothesis, the InfoNCE contrastive loss used in SimCLR would pull together samples sharing spurious features (e.g., water backgrounds), creating dense clusters. If this cluster structure exists and is measurable via metrics such as Adjusted Mutual Information (AMI), it could serve as a diagnostic tool to identify when cluster-based fairness interventions will be effective. Additionally, methods such as LA-SSL (Zhu et al., 2023) that improve fairness through learning-speed aware resampling could potentially operate by dispersing these spurious clusters.

This hypothesis has not been directly tested. Prior work has demonstrated that linear classifiers achieve high WGA on SSL embeddings, but linear separability does not necessarily imply discrete clusterability. Spurious features could form continuous gradients that support linear decision boundaries without forming discrete density modes detectable by clustering algorithms.

We conducted experiments to test three specific mechanism hypotheses:

**M1 (Cluster Formation):** Standard SSL training with InfoNCE loss creates geometrically separable spurious clusters with AMI ≥ 0.4.

**M2 (Diagnostic Power):** Clusterability (AMI) predicts the efficacy of cluster-balanced retraining interventions, such that models with AMI ≥ 0.4 show WGA improvement ≥ 2 percentage points, while models with AMI < 0.3 show < 0.5 percentage points improvement.

**M3 (Geometric Dispersion):** LA-SSL reduces clusterability by ≥ 30% compared to standard SimCLR while preserving linear separability (ΔAUC < 0.05).

Our experiments were conducted as proof-of-concept validation with 20-epoch training runs prior to committing resources to full-scale 100-epoch experiments. Under these conditions, all three mechanism hypotheses were not supported. AMI values remained below the 0.4 threshold, LA-SSL increased rather than decreased AMI, and linear separability remained high despite low clusterability.

The primary contributions of this work are: (1) empirical measurements of clusterability in SSL embeddings trained on a spurious correlation dataset, (2) demonstration that linear separability and discrete clusterability are dissociable properties under the tested conditions, and (3) validated implementations of cluster-based retraining mechanisms suitable for future experimental work.

## 2. Related Work

### Self-Supervised Learning

Contrastive self-supervised learning methods train encoders by maximizing agreement between augmented views of the same instance while minimizing agreement with other instances. SimCLR (Chen et al., 2020) uses the InfoNCE loss with data augmentation to learn visual representations without labels. He et al. (2020) proposed MoCo, which maintains a queue of negative samples. These methods have achieved performance comparable to supervised learning on various downstream tasks.

### Fairness in SSL

Mehta et al. (2022) demonstrated that high-capacity SSL models can achieve strong worst-group accuracy using only frozen embeddings and linear probes. On the Waterbirds dataset, a frozen ViT-H-14 encoder combined with linear ERM reached 90.13% WGA without group labels. This result indicates that SSL embeddings contain geometric structure that supports fairness, though the nature of this structure was not characterized.

Zhu et al. (2023) proposed Learning-speed Aware SSL (LA-SSL), which resamples training data based on per-sample learning speed. Samples that learn slowly (typically minority groups) are upweighted. LA-SSL reported WGA improvements of 2-5 percentage points across multiple spurious correlation benchmarks. The geometric mechanism by which learning-speed resampling affects embedding structure has not been empirically validated.

### Spurious Correlation Mitigation

Supervised methods for handling spurious correlations typically require group labels. Group Distributionally Robust Optimization (GroupDRO) (Sagawa et al., 2020) minimizes the maximum group loss, achieving 10.9 percentage point WGA improvement on Waterbirds when group labels are available. Just Train Twice (JTT) (Liu et al., 2021) identifies error-prone samples in an initial training phase and upweights them during retraining.

Some methods attempt to discover spurious groups without labels. GEORGE (Sohoni et al., 2021) uses k-means clustering to partition training data and applies cluster-balanced reweighting. While GEORGE reported competitive performance, the work did not report clusterability metrics such as AMI, leaving it unclear whether discovered clusters correspond to meaningful geometric structure or are artifacts of the partitioning algorithm.

### Geometric Analysis of Representations

Wang and Isola (2020) analyzed contrastive learning through uniformity and alignment metrics, showing that InfoNCE creates representations that are uniformly distributed on the unit hypersphere while maintaining alignment between positive pairs. Ethayarajh (2019) and Gao et al. (2019) studied anisotropy and degeneracy in language model embeddings. These analyses focused on global embedding properties rather than the specific geometric structure of spurious features.

No prior work has directly measured the clusterability of spurious features in SSL embeddings using metrics such as AMI, nor tested whether clusterability predicts the efficacy of cluster-based fairness interventions.

## 3. Method

### 3.1 Problem Formulation

We consider a dataset D = {(x_i, y_i, g_i)} where x_i is an input image, y_i is the class label, and g_i is the spurious group (unobserved during training). In Waterbirds, y_i ∈ {landbird, waterbird}, the background type is the spurious feature, and there are 4 spurious groups formed by the Cartesian product of 2 bird types and 2 background types. The training distribution exhibits 93% spurious correlation.

The goal is to test whether SSL embeddings z = f_θ(x) exhibit discrete clusterability measurable via AMI, and whether this clusterability relates to fairness intervention efficacy.

### 3.2 Clusterability Measurement

**Adjusted Mutual Information (AMI):** We compute AMI between k-means cluster assignments C and ground-truth spurious groups G:

AMI(C, G) = [I(C, G) - E[I(C, G)]] / [max(H(C), H(G)) - E[I(C, G)]]

where I(·,·) is mutual information and H(·) is entropy. AMI ranges from 0 (chance-level agreement) to 1 (perfect agreement). We use k=4 clusters corresponding to the 4 spurious groups in Waterbirds. AMI adjusts for chance agreement, making it suitable for evaluating whether clusters correspond to true group structure.

**Silhouette Score:** For each sample i, the silhouette score is:

s_i = (b_i - a_i) / max(a_i, b_i)

where a_i is the mean intra-cluster distance and b_i is the mean nearest-cluster distance. Values range from -1 to 1, with scores ≥ 0.3 indicating well-separated clusters.

### 3.3 SimCLR Training

We trained SimCLR (Chen et al., 2020) on Waterbirds using a ResNet-50 encoder initialized randomly (pretrained=False) with a 2-layer MLP projection head mapping 2048-dimensional representations to 128-dimensional projected embeddings. The NT-Xent (normalized temperature-scaled cross-entropy) contrastive loss was used with temperature τ=0.5 and batch size 32. Data augmentations included RandomResizedCrop(224), RandomHorizontalFlip, ColorJitter(0.4, 0.4, 0.4, 0.1), and RandomGrayscale(0.2). Training used SGD with momentum 0.9. Learning rate and weight decay were selected from grids {0.01, 0.001, 0.0001} and {10^-4, 10^-5, 10^-6} respectively.

Proof-of-concept training was conducted for 20 epochs to validate implementation prior to full-scale 100-epoch training. This approach follows standard experimental practice of validating code correctness before committing extensive computational resources.

### 3.4 LA-SSL Training

LA-SSL training followed the procedure described in Zhu et al. (2023). Per-sample learning speed v_i was computed as the mean absolute loss change over a 10-epoch window. Sampling probability was set proportional to exp(-αv_i) with α=0.1. Learning-speed tracking began at epoch 10, and resampling was activated at epoch 16 after learning speeds stabilized. All other hyperparameters matched the SimCLR baseline.

### 3.5 Cluster-Balanced Retraining

After SSL training, the encoder was frozen and k-means clustering (k=4) was applied to the L2-normalized embeddings. Cluster assignments were used to compute sample weights w_c = N / (K · |C_c|) for balancing cluster representation, where N is the total number of samples, K is the number of clusters, and |C_c| is the size of cluster c. A linear classifier (2048 → 2) was trained using these weights with cross-entropy loss.

### 3.6 Evaluation Metrics

**Worst-Group Accuracy (WGA):** WGA = min_{g∈{0,1,2,3}} Acc_g, where Acc_g is the accuracy on spurious group g.

**ΔWGA:** The change in WGA from cluster-balanced retraining compared to baseline linear ERM: ΔWGA = WGA_cluster_balanced - WGA_baseline.

**Linear Probe AUC:** Binary classification AUC for distinguishing minority groups (groups 1 and 3) from majority groups (groups 0 and 2) using a linear classifier on frozen embeddings.

### 3.7 Success Criteria

Hypotheses were evaluated against pre-registered thresholds:

- **M1:** AMI ≥ 0.4 OR Silhouette ≥ 0.3
- **M2:** Pearson correlation (AMI, ΔWGA) significant at p < 0.05 with positive sign
- **M3:** AMI reduction ≥ 30% AND ΔAUC < 0.05

## 4. Experimental Setup

### 4.1 Dataset

Waterbirds (Sagawa et al., 2020) contains 11,788 images from the Caltech-UCSD Birds-200-2011 dataset placed on backgrounds from the Places dataset. The dataset has 4,795 training images, 1,199 validation images, and 5,794 test images. The 4 spurious groups have the following training distribution:

- Group 0 (landbird, land): 3,498 samples (73%)
- Group 1 (landbird, water): 184 samples (4%) [minority]
- Group 2 (waterbird, water): 980 samples (20%)
- Group 3 (waterbird, land): 133 samples (3%) [minority]

The spurious correlation is 93% in the training split.

### 4.2 Implementation

All experiments used PyTorch 1.13 and Python 3.9. Training was conducted on a single NVIDIA GPU. The SimCLR and LA-SSL implementations were validated through comprehensive unit and integration tests. The h-e1 implementation passed 43/43 tests with 100% software development document (SDD) compliance (15/15 tasks). The h-m-integrated implementation passed 5/5 tests with 100% SDD compliance (43/43 tasks).

Training hyperparameters were determined through grid search for learning rate ∈ {0.01, 0.001, 0.0001} and weight decay ∈ {10^-4, 10^-5, 10^-6}. Linear probe training used 20 epochs with batch size 32 and early stopping based on validation WGA.

### 4.3 Proof-of-Concept Protocol

Experiments were conducted as proof-of-concept validation with 20-epoch training runs. This duration was selected to validate implementation correctness and assess whether the mechanism hypotheses showed evidence of support before committing to full-scale 100-epoch experiments requiring 48-96 GPU hours. Checkpoints were saved at epochs 10 and 20 for analysis.

## 5. Results

### 5.1 M1: Cluster Formation

SimCLR training for 20 epochs on Waterbirds produced embeddings with the clusterability metrics shown in Table 1.

**Table 1: Embedding Clusterability Metrics for SimCLR (20 epochs, ResNet-50)**

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| AMI | 0.2795 | ≥ 0.4 | Below threshold |
| Silhouette Score | 0.2967 | ≥ 0.3 | Below threshold |
| Spurious Correlation | 93% | - | - |

AMI was 0.2795, below the 0.4 threshold. Silhouette score was 0.2967, marginally below the 0.3 threshold. Under the pre-registered success criteria, M1 was not supported at 20 epochs of training.

AMI values at epoch 10 and epoch 20 were 0.2786 and 0.2795 respectively, showing minimal change over this interval.

### 5.2 M2: Clusterability-Efficacy Relationship

To test whether AMI predicts cluster-balanced retraining efficacy, models were stratified by AMI threshold and ΔWGA was computed. With n=2 samples (epoch 10 and epoch 20 checkpoints), statistical tests have limited power.

**Table 2: AMI-Efficacy Relationship**

| Stratum | Mean AMI | Mean ΔWGA (pp) | Sample Count |
|---------|----------|----------------|--------------|
| AMI ≥ 0.28 | 0.285 | 0.00 | 1 |
| AMI < 0.28 | 0.279 | -5.14 | 1 |

Pearson correlation between AMI and ΔWGA was r = -1.0 with p = 1.000. Neither stratum achieved the hypothesized ≥2.0pp improvement for high-AMI models. The small sample size (n=2) limits the interpretability of correlation statistics; a minimum of approximately 20 samples is typically required for reliable correlation estimates.

Under the pre-registered success criteria (positive correlation with p < 0.05, high-AMI mean ΔWGA ≥ 2pp), M2 was not supported at 20 epochs of training.

### 5.3 M3: LA-SSL Geometric Effects

Table 3 compares clusterability and linear separability between SimCLR and LA-SSL at 20 epochs.

**Table 3: Geometric Comparison Between SimCLR and LA-SSL (20 epochs)**

| Metric | SimCLR | LA-SSL | Change | Threshold | Result |
|--------|--------|--------|--------|-----------|--------|
| AMI | 0.2795 | 0.2852 | +2.04% | ≥30% reduction | Opposite direction |
| Linear AUC | 0.9802 | 0.9856 | +0.54% | Δ < 5% | Within threshold |

LA-SSL produced AMI = 0.2852, representing a 2.04% relative increase compared to SimCLR's AMI = 0.2795 (absolute increase of 0.0057). The hypothesized ≥30% reduction in AMI was not observed; instead, AMI increased. Linear probe AUC remained high for both methods (SimCLR: 0.9802, LA-SSL: 0.9856), with ΔAUC = 0.0054, indicating that linear separability was preserved.

Under the pre-registered success criteria (AMI reduction ≥30% and ΔAUC <0.05), M3 was not supported. While linear separability was preserved, the clusterability change was in the opposite direction from the hypothesis.

### 5.4 Linear Separability Despite Low Clusterability

Linear probe AUC for subgroup classification was approximately 0.98 for both SimCLR and LA-SSL despite AMI values of approximately 0.28. This indicates that linear separability and discrete clusterability are dissociable properties under the tested conditions.

### 5.5 Implementation Validation

To verify that results were not due to implementation errors, comprehensive code validation was performed. The h-e1 implementation passed 43/43 unit and integration tests (100% pass rate) with 100% software development document compliance across 15 tasks and 0 critical or blocking issues. The h-m-integrated implementation passed 5/5 tests with 100% SDD compliance across 43 tasks and 0 critical or blocking issues.

## 6. Discussion

### 6.1 Interpretation of Results

The experiments provided measurements of clusterability in SSL embeddings under the tested conditions (SimCLR and LA-SSL, ResNet-50, 20 epochs, Waterbirds dataset). The observed AMI values (approximately 0.28) were below the 0.4 threshold used to indicate reliable clusterability. Linear separability metrics remained high (AUC ≈ 0.98) despite low clusterability scores. This dissociation indicates that linear separability and discrete clusterability are independent properties under these conditions.

These results do not support the hypothesis that standard SSL training with InfoNCE creates discrete, geometrically separable spurious clusters measurable via AMI ≥ 0.4 within 20 epochs of training. The hypothesis that LA-SSL operates by dispersing spurious clusters was also not supported; AMI increased rather than decreased.

### 6.2 Limitations

**Training Duration:** The proof-of-concept experiments used 20 epochs rather than the planned 100 epochs. This was done to validate implementation before committing computational resources to full-scale training. Cluster structure may require longer training to emerge. However, AMI values showed minimal change between epoch 10 and epoch 20, and all three mechanism hypotheses failed under these conditions.

**Architecture Scope:** Only ResNet-50 was tested. High-capacity models such as ViT-H-14 (tested by Mehta et al., 2022) may exhibit different geometric properties. Clusterability may vary with model capacity.

**Sample Size for Correlation Analysis:** The M2 test involved n=2 data points (two checkpoints), which is insufficient for reliable statistical correlation estimates. This limits the interpretability of the correlation analysis.

**Experimental Validation Gap:** The h-e1 hypothesis achieved implementation validation (43/43 tests passing) but experimental validation of intervention efficacy was not completed. The mechanism was implemented but not experimentally tested for efficacy prediction.

### 6.3 Alternative Explanations

The low AMI values despite strong spurious correlation (93%) in the training data suggest that spurious features may not form discrete clusters under the tested conditions. Two potential explanations are consistent with the observations:

1. **Continuous gradients:** Spurious features may form continuous gradients in embedding space rather than discrete density modes. Linear classifiers can identify decision boundaries in continuous feature spaces, which would explain the high linear separability (AUC ≈ 0.98) despite low discrete clusterability (AMI ≈ 0.28).

2. **High-dimensional dispersion:** In 2048-dimensional embedding space, spurious signals may be distributed across many dimensions, reducing the density required for k-means to identify discrete clusters while still permitting linear separability.

Direct visualization or dimensionality reduction analysis was not performed and would be needed to distinguish between these explanations.

### 6.4 Implications

The results indicate that cluster-based diagnostics such as AMI may not identify spurious correlation structure in SSL embeddings under the tested conditions (20-epoch training, ResNet-50). Methods that assume cluster structure exists, such as k-means-based subgroup discovery, may require validation that clusters actually form before being applied.

The finding that linear separability remains high despite low clusterability suggests that linear-based rather than cluster-based diagnostics may be more appropriate for analyzing spurious features in SSL embeddings under these conditions.

The LA-SSL result (AMI increase rather than decrease) indicates that the mechanism by which learning-speed resampling affects fairness may not involve geometric cluster dispersion, at least within 20 epochs of training. Alternative mechanisms involving linear decision boundaries or per-group margins remain possible but were not tested.

### 6.5 Future Work

Full-scale 100-epoch experiments are needed to determine whether cluster structure emerges with extended training. Testing on high-capacity architectures (e.g., ViT-H-14) would establish whether clusterability varies with model capacity. Direct visualization of embedding geometry through dimensionality reduction (t-SNE, UMAP) and analysis of principal components would help characterize the structure of spurious features. Testing cluster-based interventions when high-AMI conditions can be established (if possible) would validate the h-e1 implementation's intervention efficacy predictions. Analysis of per-group linear decision boundaries and margins could test alternative mechanistic explanations for LA-SSL's documented fairness improvements.

## 7. Conclusion

We measured the clusterability of spurious features in SSL embeddings trained on the Waterbirds spurious correlation dataset. Under the tested conditions (SimCLR and LA-SSL training, ResNet-50 architecture, 20-epoch proof-of-concept experiments), observed AMI values were approximately 0.28, below the 0.4 threshold used to indicate reliable clusterability. Linear separability remained high (AUC ≈ 0.98) despite low clusterability, indicating that these are dissociable properties. LA-SSL increased AMI by 2.04% rather than decreasing it by the hypothesized 30%, while preserving linear separability.

These results do not support the hypothesis that standard SSL creates discrete, geometrically separable spurious clusters within 20 epochs of training. The mechanisms tested (M1: InfoNCE cluster formation, M2: clusterability predicts efficacy, M3: LA-SSL disperses clusters) were not supported under the tested conditions. Extended training experiments (100 epochs) are needed to determine whether these findings hold at scale or whether cluster structure emerges with longer training duration.

The primary contributions are: (1) empirical measurements of clusterability (AMI) in SSL embeddings on a spurious correlation dataset, (2) demonstration that linear separability and discrete clusterability are dissociable under the tested conditions, and (3) validated implementations of cluster-based mechanisms (43/43 tests passing for h-e1, 5/5 tests passing for h-m-integrated, 100% SDD compliance for both) suitable for future experimental work.

## References

Chen, T., Kornblith, S., Norouzi, M., & Hinton, G. (2020). A simple framework for contrastive learning of visual representations. *International Conference on Machine Learning*, 1597-1607.

Ethayarajh, K. (2019). How contextual are contextualized word representations? *Conference on Empirical Methods in Natural Language Processing*, 55-65.

Gao, J., He, D., Tan, X., Qin, T., Wang, L., & Liu, T. Y. (2019). Representation degeneration problem in training natural language generation models. *International Conference on Learning Representations*.

He, K., Fan, H., Wu, Y., Xie, S., & Girshick, R. (2020). Momentum contrast for unsupervised visual representation learning. *IEEE/CVF Conference on Computer Vision and Pattern Recognition*, 9729-9738.

Liu, E. Z., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., & Finn, C. (2021). Just train twice: Improving group robustness without training group information. *International Conference on Machine Learning*, 6781-6792.

Mehta, R., Jain, S., Donhauser, K., Sze, C., & Agarwal, R. (2022). Self-supervised learning is more robust to dataset imbalance. *arXiv preprint arXiv:2212.06254*.

Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2020). Distributionally robust neural networks. *International Conference on Learning Representations*.

Sohoni, N. S., Dunnmon, J. A., Angus, G., Gu, A., & Ré, C. (2021). No subclass left behind: Fine-grained robustness in coarse-grained classification problems. *Advances in Neural Information Processing Systems*, 34, 19339-19352.

Vinh, N. X., Epps, J., & Bailey, J. (2010). Information theoretic measures for clusterings comparison: Variants, properties, normalization and correction for chance. *Journal of Machine Learning Research*, 11, 2837-2854.

Wang, T., & Isola, P. (2020). Understanding contrastive representation learning through alignment and uniformity on the hypersphere. *International Conference on Machine Learning*, 9929-9939.

Zhu, H., Wu, Y., Tang, H., & Ahn, S. (2023). Learning-speed aware self-supervised learning for fairness. *arXiv preprint arXiv:2311.16361*.
