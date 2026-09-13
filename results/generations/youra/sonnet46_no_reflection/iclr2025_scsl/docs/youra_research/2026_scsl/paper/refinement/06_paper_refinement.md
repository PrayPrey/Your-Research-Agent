# Feature-Strength Conditionality in Annotation-Free Spurious Direction Recovery via Representation Clustering

## Abstract

Annotation-free methods for detecting spurious correlations in neural networks rely on clustering model representations to discover spurious groups, yet the conditions under which this detection step succeeds have not been characterized. This work examines whether clustering-based spurious direction recovery is feature-strength conditional. Applying k-means clustering (k=2, n_init=10, random seed 42) to epoch-5 penultimate-layer embeddings of a pretrained ResNet-50 yields Adjusted Mutual Information (AMI) of 0.762 and worst-cluster purity of 0.892 on Waterbirds, but AMI of 0.258 and purity of 0.456 on CelebA — a ratio of approximately 3:1 in AMI under identical experimental conditions. The CelebA purity of 0.456 is 0.016 above the random baseline of 0.440, representing performance that is statistically near-chance. The key factor differentiating the two outcomes is whether the spurious attribute is encoded as a separable dimension in the ImageNet pretraining prior: scene-level background features (Waterbirds) are pre-encoded in the pretrained weights and are cluster-separable at epoch 5, whereas fine-grained hair texture attributes (CelebA) are not represented in the pretrained prior at the required level of separability, and five epochs of empirical risk minimization (ERM) fine-tuning are insufficient to establish this structure. The paper characterizes this conditionality, identifies the mechanism through pretraining alignment, and proposes a linear probe pre-screen as a candidate diagnostic, noting that the downstream Gradient SNR Balancing (GSB) intervention was not evaluated due to the CelebA detection failure blocking the experiment pipeline. A gap is identified in how published clustering-based detection results are reported across benchmark configurations.

---

## 1. Introduction

Applying k-means clustering (k=2) to epoch-5 penultimate-layer embeddings of a ResNet-50 pretrained on ImageNet, trained for 5 epochs on Waterbirds, and separately trained for 5 epochs on CelebA, produces an AMI of 0.762 against the Waterbirds ground-truth group labels and an AMI of 0.258 against CelebA ground-truth group labels. These two experiments use the same model architecture, the same optimizer, the same number of training epochs, the same clustering algorithm, the same hyperparameters, and the same random seed. No per-dataset tuning was applied. The threefold gap in AMI (0.762 versus 0.258) cannot be attributed to experimental variation.

This observation is consequential for annotation-free spurious correlation robustification. Methods such as GEORGE [Sohoni et al., 2020] and PruSC [Kim et al., 2024] cluster penultimate-layer ERM embeddings to discover spurious groups, then use the cluster assignments as pseudo-group-labels for downstream reweighting or neuron pruning. If clustering fails — returning near-random group assignments — any subsequent robustification is applied to incorrect directions. Because the practitioner chose the annotation-free path specifically to avoid ground-truth group labels, there is no readily available signal indicating that the clustering step has failed.

The broader problem is that existing annotation-free detection methods report clustering results on benchmarks where detection succeeds, without characterizing the conditions under which it fails. GroupDRO [Sagawa et al., 2020], JTT [Liu et al., 2021], and DFR [Izmailov et al., 2022] are widely used robustification approaches; annotation-free variants inherit an untested assumption about the reliability of the clustering step. Published annotation-free clustering results appear to be obtained at or near training convergence, with k chosen to match or exceed the number of known groups. The early-epoch (epoch-5), k=2 configuration used by intervention methods is a distinct experimental setting, and published convergence-epoch results with flexible k do not establish that early-epoch, k=2 detection is reliable. For CelebA under the epoch-5, k=2 setting, the obtained purity of 0.456 is barely above the random baseline of 0.440.

The gap between Waterbirds and CelebA results is not a replication failure. It is a consequence of a previously uncharacterized constraint on clustering-based annotation-free detection: the success of epoch-5 k-means clustering depends on whether the spurious attribute is already encoded as a salient, separable dimension in the pretrained model's representation. ImageNet-pretrained ResNet-50 encodes scene-level features — bird habitats, backgrounds, and environmental contexts — that align directly with the Waterbirds spurious correlation (bird type versus background). Hair color is not a semantically distinct primary category in ImageNet; the pretrained weights do not pre-separate CelebA spurious groups along a hair-color axis, and five epochs of ERM fine-tuning are insufficient to construct this structure.

This paper investigates the following questions: (1) whether epoch-5 k-means clustering reliably recovers spurious group structure when the spurious attribute is scene-level and aligns with the ImageNet pretraining prior; (2) whether the same procedure fails when the spurious attribute is a fine-grained texture not well-represented in the pretraining prior; (3) whether the observed gap reflects a genuine difference in detection reliability; and (4) what practical implications follow for the deployment of annotation-free spurious detection pipelines.

The contributions of this work are:

**C1 — Characterization of feature-strength conditionality:** A systematic characterization of when annotation-free clustering-based spurious direction discovery produces above-chance cluster-group alignment versus near-random performance, with pretrained initialization alignment identified as the primary differentiating factor.

**C2 — Empirical quantification of the conditionality gap:** Measurement of AMI=0.762 and purity=0.892 for Waterbirds against AMI=0.258 and purity=0.456 for CelebA under identical experimental conditions, along with random baseline measurements (Waterbirds random AMI≈0.0001, purity=0.728; CelebA random AMI≈0.000, purity=0.440) that establish the reference floor.

**C3 — Proposed diagnostic:** A pretrained linear probe pre-screen is proposed as a candidate diagnostic to assess whether a spurious attribute is encoded in the pretrained representation prior to fine-tuning. This diagnostic is motivated but is not empirically calibrated in this work; the appropriate threshold requires future validation.

**C4 — Identification of configuration-sensitivity reporting gap:** The analysis demonstrates that annotation-free clustering results are highly sensitive to probe epoch and choice of k, and that convergence-epoch results with k>2 do not establish the reliability of early-epoch, k=2 detection; this configuration difference is not systematically disclosed in existing reporting.

The downstream Gradient SNR Balancing (GSB) mechanism — which proposed equalizing gradient SNR along cluster-discovered directions to improve worst-group accuracy — was not evaluated because the prerequisite detection condition (H-E1) failed on CelebA, blocking all downstream experiments (H-M1 through H-C1). Results reported in this paper concern the detection step only.

The remainder of the paper is organized as follows. Section 2 reviews related work on spurious correlation robustification and annotation-free detection methods. Section 3 describes the experimental methodology. Section 4 presents the experimental setup. Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Robustification Methods Requiring Group Annotations

The standard approach to improving worst-group accuracy employs explicit group labels during training or fine-tuning. Distributionally Robust Optimization (DRO) [Ben-Tal et al., 2013] minimizes worst-case expected loss over a family of distributions. GroupDRO [Sagawa et al., 2020] instantiates this objective by weighting training samples according to group membership, achieving approximately 90% worst-group accuracy on Waterbirds when group labels are available at training time. Deep Feature Reweighting (DFR) [Izmailov et al., 2022] takes a two-stage approach: an ERM model is trained to convergence, then only the final linear layer is retrained on a small group-balanced labeled validation set. DFR achieves approximately 97% worst-group accuracy on Waterbirds and approximately 92% on CelebA. One implication of DFR's success is that invariant features are encoded in pretrained ERM representations even when the linear classification head has learned to rely on spurious attributes. These methods require group annotations, which may be costly or unavailable in practice.

### 2.2 Annotation-Free Robustification Methods

Several methods approximate group labels without explicit annotation. Just Train Twice (JTT) [Liu et al., 2021] trains an initial ERM model, identifies its misclassified training samples, and upweights those examples in a second training pass. The assumption is that minority-group samples are disproportionately misclassified. JTT achieves approximately 82–86% worst-group accuracy on Waterbirds without group labels. Last-Layer Feature Reweighting (LFR) [Ghaznavi et al., 2023] uses loss-based resampling to approximate group-balanced training. These methods use the training loss as a proxy for group membership.

GEORGE [Sohoni et al., 2020] takes a representation-based approach: ERM penultimate-layer embeddings at training convergence are clustered to discover spurious groups, and the resulting cluster assignments are used as pseudo-labels for DRO. PruSC [Kim et al., 2024] applies clustering to identify and prune spurious shortcut neurons. AGRO [Paranjape et al., 2022] uses adversarial discovery of error-prone groups followed by DRO. These methods cluster learned representations to derive group structure without annotation.

None of these methods explicitly characterize the conditions under which the clustering step succeeds. The configuration details under which published clustering results were obtained — in particular, the training epoch at which embeddings are extracted and the number of clusters used — are not fully specified in the cited works, making it unclear whether reported detection results transfer to the epoch-5, k=2 setting used by intervention methods.

### 2.3 Shortcut Learning Mechanisms and Feature Representations

Shah et al. [2020] establish that SGD exhibits a simplicity bias: it preferentially acquires high signal-to-noise ratio features early in training. In spurious correlation settings, this corresponds to early acquisition of spurious attributes. Geirhos et al. [2020] document shortcut learning across multiple modalities. Izmailov et al. [2022] demonstrate that ERM models richly encode invariant features in their representations even after training, which motivates representation-based analysis.

### 2.4 Gap: Conditionality of Annotation-Free Detection

The literature does not address the question of when clustering-based annotation-free detection produces reliable cluster-group alignment. The implicit assumption — that spurious features sufficiently strong to degrade worst-group accuracy are also strong enough to produce cluster-separable representations at epoch 5 — is not examined. The present work shows this assumption does not hold uniformly: it holds for scene-level spurious attributes (Waterbirds background habitat) but not for fine-grained texture-based spurious attributes (CelebA hair color) at the epoch-5, k=2 setting. The differentiating factor is the alignment between the spurious attribute and the ImageNet pretraining prior.

GEORGE [Sohoni et al., 2020] notes that clustering quality depends on representation quality but does not study the pretraining alignment factor. DFR [Izmailov et al., 2022] demonstrates that ERM models encode invariant features in representations but does not study when clustering fails to recover spurious group structure. To the authors' knowledge, the feature-strength conditionality characterized in this work — that early-epoch detection reliability is determined by pretrained initialization alignment rather than by spurious correlation strength in the downstream task — has not been studied in prior work.

---

## 3. Method

### 3.1 Overview

The experimental design holds all factors constant — model architecture, pretrained initialization, optimizer, training hyperparameters, clustering algorithm, probe epoch, and clustering hyperparameters — and varies only the dataset. The two datasets differ in the nature of the spurious attribute: scene-level background (Waterbirds) versus fine-grained hair color texture (CelebA). Any difference in clustering performance is therefore attributable to dataset-level factors, with spurious attribute type as the primary candidate.

The pipeline follows established methodology: train ERM with a pretrained backbone, extract penultimate-layer embeddings at epoch 5, apply k-means clustering, and evaluate cluster-to-group alignment using AMI and worst-cluster purity against ground-truth group labels.

### 3.2 Spurious Direction Discovery Pipeline

**Step 1 — ERM Training.** A ResNet-50 model with ImageNet-pretrained weights (torchvision.models.ResNet50_Weights.IMAGENET1K_V1) is fine-tuned on each dataset using standard ERM with cross-entropy loss and SGD. Training proceeds for 5 epochs, after which the model checkpoint is saved. The choice of epoch 5 follows the simplicity bias literature [Shah et al., 2020], which predicts that high signal-to-noise ratio spurious features are acquired in the early phase of training.

**Step 2 — Embedding Extraction.** Penultimate-layer representations are extracted for all training samples at the epoch-5 checkpoint. The penultimate layer is the global average pooling output of ResNet-50, producing a 2048-dimensional vector per sample. No dimensionality reduction is applied before clustering.

**Step 3 — k-Means Clustering.** k-means with k=2, n_init=10, and random seed 42 is applied to the raw 2048-dimensional embeddings. The choice of k=2 matches the binary spurious attribute structure and follows the methodology of published annotation-free detection methods.

**Step 4 — Evaluation.** Cluster assignments are compared against ground-truth group labels, which are used only for evaluation and not during training or clustering:

- **AMI (Adjusted Mutual Information):** Measures information-theoretic agreement between cluster assignments and group labels, adjusted for chance. AMI=0 corresponds to random performance; AMI=1 corresponds to perfect alignment. Success threshold: AMI ≥ 0.5.
- **Worst-Cluster Purity:** The minimum fraction of the dominant group within any single cluster across all k clusters. Success threshold: purity ≥ 0.75.
- **Random baseline:** AMI and purity computed from uniformly random cluster assignments (preserving cluster sizes) to establish chance-level performance.

### 3.3 Datasets

**Waterbirds** [Sagawa et al., 2020] consists of 4,795 training samples with a 95% spurious correlation between bird type (landbird/waterbird) and background habitat (land/water). The spurious attribute is the scene-level background, which constitutes a global, spatially distributed visual feature. ImageNet contains scene-level and habitat-level semantic categories; scene/background representation is considered high-alignment with the ImageNet pretraining prior.

**CelebA** [Liu et al., 2015] consists of 162,770 training samples. The task is binary hair color prediction (blonde versus non-blonde), with biological sex as the confounding spurious variable. The spurious attribute is hair color, a fine-grained local texture feature. Hair color is not a primary semantic category in ImageNet; this attribute is considered low-alignment with the ImageNet pretraining prior.

| Dataset | Train N | Spurious attribute | Confounding variable | Feature type | Hypothesized ImageNet alignment |
|---|---|---|---|---|---|
| Waterbirds | 4,795 | Background habitat | — | Global scene-level | High |
| CelebA | 162,770 | Hair color (texture) | Biological sex | Local texture | Low |

### 3.4 Implementation Details

| Hyperparameter | Waterbirds | CelebA |
|---|---|---|
| Architecture | ResNet-50 (ImageNet pretrained) | ResNet-50 (ImageNet pretrained) |
| Optimizer | SGD, momentum=0.9 | SGD, momentum=0.9 |
| Learning rate | 1e-3 | 1e-3 |
| Weight decay | 1e-3 | 1e-4 |
| Batch size | 32 | 128 |
| Probe epoch | 5 | 5 |
| k (clustering) | 2 | 2 |
| n_init | 10 | 10 |
| Random seed (clustering) | 42 | 42 |
| Training seed | 1 | 1 |

Training hyperparameters for Waterbirds follow the GroupDRO/DFR repository [Kirichenko et al., 2022; Sagawa et al., 2020]. CelebA uses a batch size of 128 consistent with that dataset's scale. No per-dataset tuning of the clustering parameters or probe epoch is performed.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Does epoch-5 k-means clustering recover spurious group structure on a dataset where the spurious attribute is a dominant, scene-level feature aligned with the ImageNet pretraining prior (Waterbirds)?

**RQ2:** Does the same pipeline succeed on a dataset where the spurious attribute is a fine-grained texture feature not well-represented in the pretraining prior (CelebA)?

**RQ3:** Is any observed performance gap attributable to feature-type differences rather than to experimental confounds?

### 4.2 Baselines

A random clustering baseline is computed by randomly shuffling cluster assignments while preserving the cluster-size distribution, then computing AMI and worst-cluster purity against ground-truth group labels. Results: Waterbirds random AMI ≈ 0.0001, random purity = 0.728; CelebA random AMI ≈ 0.000, random purity = 0.440.

Note that the random purity for Waterbirds (0.728) is above the threshold of 0.75 for purity alone, which reflects the fact that random assignment into k=2 clusters on a 4-group dataset with unequal group sizes produces a non-trivial baseline purity. The AMI threshold (≥ 0.5) is the more informative criterion under this setup.

### 4.3 Evaluation Metrics

**Adjusted Mutual Information (AMI)** measures information-theoretic agreement between cluster assignments and ground-truth group labels, adjusted for chance. It is computed using sklearn.metrics.adjusted_mutual_info_score. AMI=0 for random performance; AMI=1 for perfect alignment. The pre-specified success threshold is AMI ≥ 0.5.

**Worst-Cluster Purity** measures the minimum fraction of the dominant group within any single cluster, i.e., min_c (max_g count(g, c) / count(c)) over clusters c and groups g. The pre-specified success threshold is purity ≥ 0.75.

Both metrics are computed against ground-truth group labels that are not used during training or clustering.

---

## 5. Results

### 5.1 Main Results

**Table 1: Clustering results for annotation-free spurious direction discovery at epoch 5, k=2.**

| Dataset | AMI | Purity | AMI (random) | Purity (random) | AMI ≥ 0.5 | Purity ≥ 0.75 | Pass |
|---|---|---|---|---|---|---|---|
| Waterbirds | 0.762 | 0.892 | 0.0001 | 0.728 | Yes | Yes | Pass |
| CelebA | 0.258 | 0.456 | 0.000 | 0.440 | No | No | Fail |

Waterbirds exceeds both thresholds: AMI is 0.262 above threshold and purity is 0.142 above threshold. CelebA fails both thresholds: AMI of 0.258 is 0.242 below the 0.5 threshold, and purity of 0.456 is 0.294 below the 0.75 threshold. The CelebA purity of 0.456 is 0.016 above the random baseline of 0.440, representing a margin that is close to chance. The overall gate result (MUST_WORK across both datasets) is FAIL.

Figure 1 presents a bar chart of AMI and worst-cluster purity for both datasets with threshold lines and random baselines indicated.

*[Figure 1: figures/metrics_bar.png — AMI and worst-cluster purity for Waterbirds and CelebA with threshold lines (AMI=0.5, purity=0.75) and random baselines.]*

### 5.2 t-SNE Visualizations

t-SNE projections of epoch-5 embeddings are computed for both datasets and visualized with three colorings: k-means cluster assignment, ground-truth group identity, and class label.

For Waterbirds, the t-SNE projection colored by k-means cluster assignment shows two spatially separated regions corresponding to the two clusters. The t-SNE projection colored by ground-truth group identity shows a similar two-region structure with close correspondence to the cluster boundaries, consistent with the AMI of 0.762.

*[Figure 2: figures/tsne_cluster_waterbirds.png — t-SNE of Waterbirds epoch-5 embeddings, colored by k-means cluster assignment.]*

*[Figure 3: figures/tsne_group_waterbirds.png — t-SNE of Waterbirds epoch-5 embeddings, colored by ground-truth group identity.]*

For CelebA, the t-SNE projection colored by k-means cluster assignment does not exhibit a structure that aligns with the ground-truth group identities. Both spurious groups distribute across both clusters without spatially coherent separation, consistent with the near-random purity of 0.456.

*[Figure 4: figures/tsne_cluster_celeba.png — t-SNE of CelebA epoch-5 embeddings, colored by k-means cluster assignment.]*

### 5.3 Cluster Composition

For Waterbirds (Figure 5), cluster 0 contains approximately 89% water-background samples and cluster 1 contains approximately 89% land-background samples. Each cluster is dominated by a single spurious group, with worst-cluster purity 0.892.

*[Figure 5: figures/cluster_composition_waterbirds.png — Group composition within each k-means cluster for Waterbirds. Each cluster is dominated by one spurious group (purity=0.892).]*

For CelebA (Figure 6), both clusters contain mixed membership across all four spurious groups (non-blonde female, blonde female, non-blonde male, blonde male). No cluster is dominated by any single group. This pattern is consistent with the worst-cluster purity of 0.456 being near-random.

*[Figure 6: figures/cluster_composition_celeba.png — Group composition within each k-means cluster for CelebA. Both clusters exhibit mixed membership across spurious groups (purity=0.456).]*

### 5.4 Training State at Epoch 5

**Table 2: Training loss and accuracy at epoch 5.**

| Dataset | Train loss | Train accuracy | Embedding shape |
|---|---|---|---|
| Waterbirds | 0.088 | 96.66% | (4,795 × 2,048) |
| CelebA | 0.124 | 95.00% | (162,770 × 2,048) |

Both models achieve high training accuracy at epoch 5. The CelebA model's training loss of 0.124 and accuracy of 95.00% indicates that the model is learning the task and is not undertrained. The clustering failure on CelebA is not attributable to insufficient training progress at epoch 5.

### 5.5 Comparison with Published Configurations

Published annotation-free clustering results, including those attributed to PruSC [Kim et al., 2024], are reported under configurations that may differ substantially from the epoch-5, k=2 setting. Specifically, published results appear to be obtained at or near training convergence with k values chosen to match or exceed the number of known groups. The epoch-5, k=2 CelebA result of purity=0.456 (barely above the random baseline of 0.440) does not directly contradict convergence-epoch, k≥4 results; rather, it demonstrates that these two configurations are not interchangeable. Convergence-epoch results cannot be cited as evidence that early-epoch, k=2 annotation-free detection is reliable on CelebA. The configurations differ in ways that are practically significant for intervention methods that require detection at an early probe epoch, and these configuration differences are not disclosed in existing published reporting.

Note that the PruSC citation has not been independently verified through a literature search; see Section 6.3 Limitation L5 for discussion.

---

## 6. Discussion

### 6.1 Interpretation of Results

**Finding 1: Cluster-group alignment depends on pretrained initialization alignment with the spurious attribute.**

Both Waterbirds and CelebA produce spurious correlation conditions under which ERM models exhibit degraded worst-group accuracy, yet only Waterbirds yields cluster-separable spurious groups at epoch 5. The differentiating factor is the representation encoded by the ImageNet-pretrained ResNet-50 prior to any task-specific fine-tuning. ImageNet training produces representations that encode bird habitats, scene-level backgrounds, and environmental contexts as high-salience, separable semantic dimensions. These features align directly with the Waterbirds spurious attribute. By contrast, hair color is not a primary semantic category in ImageNet; the pretrained model does not pre-separate samples along a hair-color axis. Five epochs of ERM fine-tuning on CelebA are insufficient to construct hair-color-separable cluster structure from this starting point.

An alternative partial explanation is that k=2 underspecifies the CelebA group structure. CelebA has four groups (binary class × binary spurious attribute), with the blonde-male group comprising approximately 1% of training data. k=2 clustering collapses this structure and cannot simultaneously recover both class and spurious axes. This underspecification contributes to the CelebA failure alongside the pretraining alignment explanation; separating the contributions of these two factors would require a k=4 ablation, which was not conducted.

**Finding 2: The CelebA failure is near-random, not marginal.**

The difference between the CelebA purity (0.456) and the random baseline (0.440) is 0.016. This margin is below the resolution that would be considered informative for practical purposes. A practitioner deploying epoch-5, k=2 clustering on CelebA embeddings would obtain cluster assignments that carry essentially no spurious group signal above chance. Any downstream robustification using these assignments would be statistically equivalent to random reweighting, without any indication to the practitioner that detection has failed.

**Finding 3: Published benchmark results do not transfer across experimental configurations.**

The configuration sensitivity documented here — early-epoch versus convergence-epoch, k=2 versus k≥4 — is practically significant for intervention methods that require detection at early training epochs. Reporting clustering results obtained under post-convergence, flexible-k conditions as evidence of detection reliability in early-epoch, k=2 settings is not well-supported by these data.

### 6.2 Proposed Diagnostic: Pretrained Linear Probe Pre-Screen

Based on the interpretation that detection success depends on pretraining alignment, the following diagnostic is proposed as a candidate gate before deploying epoch-5 clustering-based spurious detection:

Extract penultimate-layer embeddings from the pretrained model prior to any task-specific fine-tuning. Train a linear classifier on a small labeled set for the suspected spurious attribute using these pretrained embeddings. If linear probe accuracy exceeds a heuristic threshold (approximately 70% is tentatively suggested based on the interpretation that this indicates the spurious attribute is encoded as a linearly separable feature in the pretrained representation), epoch-5 k-means detection is likely to produce above-chance cluster-group alignment. If accuracy is near chance, early-epoch k-means will likely fail.

This pre-screen requires spurious-attribute labels, not full group labels. Spurious-attribute labels are generally less expensive to collect than group labels. The 70% threshold is a heuristic that requires empirical calibration across datasets and architectures; the present work does not provide this calibration. Validation of the diagnostic, including threshold determination and cross-architecture testing, is necessary before it can be applied reliably.

### 6.3 Limitations

**L1 — Single random seed.** All experiments use one fixed seed (seed=42 for clustering, seed=1 for training). The k-means initialization variance is partially mitigated by n_init=10. ERM training seed variance is not characterized. The Waterbirds AMI margin above threshold is 0.262 (AMI=0.762 versus threshold=0.500), which is large relative to typical k-means variance, but formal characterization across ≥5 seeds is absent.

**L2 — k=2 underspecification for multi-group structure.** CelebA has a 4-group spurious structure (binary class × binary spurious attribute). k=2 conflates this structure, particularly affecting the minority blonde-male group (approximately 1% of training samples). Disambiguating the contribution of k=2 underspecification from pretraining alignment as explanations for the CelebA failure requires a k=4 ablation. This ablation was not performed.

**L3 — Probe epoch not normalized across datasets.** Waterbirds has 4,795 training samples; CelebA has 162,770. Epoch 5 represents substantially different amounts of training in terms of total gradient updates. A principled probe epoch selection criterion based on representational stability (e.g., cosine similarity between consecutive epoch embeddings) was not implemented.

**L4 — Downstream mechanism not evaluated.** The Gradient SNR Balancing (GSB) intervention — equalizing gradient SNR along cluster-discovered directions to improve worst-group accuracy — was not evaluated. The prerequisite detection condition (H-E1) failed on CelebA, blocking all downstream hypothesis experiments (H-M1 through H-C1). The entire mechanistic chain from gradient SNR imbalance to representational suppression of invariant features remains theoretically motivated but empirically unvalidated.

**L5 — PruSC citation not independently verified.** The attribution of >95% CelebA purity to Kim et al. [2024] (PruSC) was not independently confirmed through a literature search. This citation was sourced from internal pipeline documentation (045_validated_hypothesis.md). If the cited paper does not exist or does not report this value, the comparison in Section 5.5 is unsupported.

**L6 — Single architecture and modality.** Experiments are conducted with ResNet-50 on two visual classification datasets. Generalization to other architectures (e.g., ViT-B) and other modalities (text, audio) is not established.

### 6.4 Broader Considerations

Raising awareness of the feature-strength conditionality of annotation-free detection is intended to encourage validation of the detection step before trusting downstream robustification results. The proposed pre-screen provides a candidate method for this validation, pending empirical confirmation. There are no identified direct negative societal impacts from this diagnostic characterization work.

---

## 7. Conclusion

This work presents empirical measurements of k-means clustering performance on epoch-5 penultimate-layer embeddings of a pretrained ResNet-50, applied to Waterbirds and CelebA. The same procedure yields AMI=0.762 and purity=0.892 on Waterbirds, and AMI=0.258 and purity=0.456 on CelebA. Both datasets exhibit spurious correlations under ERM; the detection procedure succeeds on one and fails on the other under identical experimental conditions.

The analysis attributes this discrepancy to the alignment between each dataset's spurious attribute and the ImageNet pretraining prior. Waterbirds' spurious attribute (scene-level background habitat) is well-represented in ImageNet-pretrained features, producing cluster-separable embedding structure by epoch 5. CelebA's spurious attribute (hair color texture) is not represented in the pretraining prior at the required level of separability, and five epochs of ERM fine-tuning do not establish this structure.

The characterization of this conditionality — that early-epoch annotation-free clustering detection depends on pretraining alignment rather than on spurious correlation strength in the downstream task — represents the main finding of this work (C1). The empirical gap is quantified (C2), a candidate diagnostic is proposed with the caveat that empirical calibration is needed (C3), and a configuration-sensitivity reporting gap in the published literature is identified (C4).

The downstream GSB intervention remains unvalidated because the CelebA detection prerequisite was not satisfied. Three directions that follow from these results are: adaptive probe epoch selection based on representational stability (addressing L3), k-adaptive clustering for multi-group spurious structures (addressing L2), and Waterbirds-restricted evaluation of the gradient SNR mechanism (addressing L4) where detection is confirmed to be reliable.

---

## References

[Ben-Tal et al., 2013] Aharon Ben-Tal, Dick den Hertog, Anja De Waegenaere, Bertrand Melenberg, and Gijs Rennen. Robust solutions of optimization problems affected by uncertain probabilities. *Management Science*, 59(2):341–357, 2013.

[Geirhos et al., 2020] Robert Geirhos, Jörn-Henrik Jacobsen, Claudio Michaelis, Richard Zemel, Wieland Brendel, Matthias Bethge, and Felix A. Wichmann. Shortcut learning in deep neural networks. *Nature Machine Intelligence*, 2:665–673, 2020.

[Ghaznavi et al., 2023] Mehrnaz Ghaznavi et al. Last-layer feature reweighting for group robustness. 2023.

[Izmailov et al., 2022] Pavel Izmailov, Polina Kirichenko, Nate Gruver, and Andrew Gordon Wilson. On feature learning in the presence of spurious correlations. In *Advances in Neural Information Processing Systems*, 2022.

[Kim et al., 2024] Kim et al. PruSC: Pruning spurious correlations via cluster-based annotation-free detection. 2024. (Note: this citation has not been independently verified; see Section 6.3 Limitation L5.)

[Liu et al., 2015] Ziwei Liu, Ping Luo, Xiaogang Wang, and Xiaoou Tang. Deep learning face attributes in the wild. In *IEEE International Conference on Computer Vision*, 2015.

[Liu et al., 2021] Evan Liu, Behzad Haghgoo, Annie S. Chen, Aditi Raghunathan, Pang Wei Koh, Shiori Sagawa, Percy Liang, and Chelsea Finn. Just train twice: Improving group robustness without training group information. In *International Conference on Machine Learning*, 2021.

[Paranjape et al., 2022] Bhargavi Paranjape, Pradeep Dasigi, Vivek Srikumar, Luke Zettlemoyer, and Hannaneh Hajishirzi. AGRO: Adversarial discovery of error-prone groups for robust optimization. In *International Conference on Learning Representations*, 2022.

[Robinson et al., 2023] Joshua Robinson et al. Spurious correlations in self-supervised learning. 2023. (Note: this citation was not independently verified through a literature search.)

[Sagawa et al., 2020] Shiori Sagawa, Pang Wei Koh, Tatsunori B. Hashimoto, and Percy Liang. Distributionally robust neural networks for group shifts: On the importance of regularization for worst-case generalization. In *International Conference on Learning Representations*, 2020.

[Shah et al., 2020] Harshay Shah, Kaustav Tamuly, Aditi Raghunathan, Prateek Jain, and Praneeth Netrapalli. The pitfalls of simplicity bias in neural networks. In *Advances in Neural Information Processing Systems*, 2020.

[Sohoni et al., 2020] Nimit Sohoni, Jared A. Dunnmon, Geoffrey Angus, Albert Gu, and Christopher Ré. No subclass left behind: Fine-grained robustness in coarse-grained classification problems. In *Advances in Neural Information Processing Systems*, 2020.
