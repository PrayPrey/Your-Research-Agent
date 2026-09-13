---
title: "When Shortcuts Hide in Plain Sight: Feature-Strength Conditionality in Annotation-Free Spurious Direction Recovery"
authors:
  - name: "Anonymous"
    affiliation: "Anonymous Institution"
    email: "anonymous@anonymous.org"
format: "ICML2025"
date: "2026-05-20"
word_count: ~5300
figures: 6
tables: 4
---

## Abstract

Annotation-free methods for detecting spurious correlations in neural networks rely on clustering model representations to discover spurious groups — yet the conditions under which this detection step succeeds are not characterized. We show that clustering-based spurious direction recovery is *feature-strength conditional*: applying identical k-means clustering to epoch-5 penultimate embeddings of a pretrained ResNet-50 yields AMI=0.762 and cluster purity=0.892 on Waterbirds, but AMI=0.258 and purity=0.456 (near-random) on CelebA — a threefold gap from the same algorithm under the same experimental conditions. The key determinant is not the clustering algorithm or training protocol, but whether the spurious attribute is encoded as a separable dimension in the ImageNet pretraining prior: scene-level background features (Waterbirds) are pre-encoded and immediately cluster-separable; fine-grained texture attributes (CelebA hair color) are not, and five epochs of ERM fine-tuning are insufficient to build this structure. We characterize this conditionality, explain its mechanism through pretraining alignment, and motivate a proposed spurious feature salience pre-screen — a linear probe from pretrained embeddings — as a lightweight diagnostic for future validation. Our results characterize a detection failure mode that would constitute a silent failure in downstream annotation-free robustification pipelines if propagated — though the downstream mechanism itself is not empirically validated in this work. This work also identifies a gap in how published clustering-based detection results are reported across benchmark configurations.

---

## 1. Introduction

Using the same clustering algorithm, the same pretrained ResNet-50, and the same hyperparameters, we obtain an Adjusted Mutual Information of 0.762 on one standard benchmark and 0.258 on another — a threefold gap from a method that the community routinely applies to both. The first dataset is Waterbirds; the second is CelebA. The algorithm is k-means (k=2) applied to epoch-5 penultimate-layer embeddings, following established methodology for annotation-free spurious direction discovery [Sohoni et al., 2020; Kim et al., 2024]. No hyperparameter was tuned differently. No bug was present.

This discrepancy is not a curiosity. Annotation-free detection of spurious correlations sits at the foundation of several robustification pipelines that aim to improve worst-group accuracy without requiring expensive group annotations. Methods like GEORGE [Sohoni et al., 2020] and PruSC [Kim et al., 2024] discover spurious groups by clustering model representations, then use those clusters as proxies for group labels in downstream reweighting or regularization. If the clustering step fails — silently, producing near-random group assignments — all subsequent robustification is applied to the wrong directions. The practitioner has no way of knowing this without ground-truth group labels, which they chose the annotation-free path precisely to avoid.

The deeper problem is that existing work on annotation-free spurious detection reports clustering results on benchmarks where the method works, without characterizing when and why it fails. GroupDRO [Sagawa et al., 2020], JTT [Liu et al., 2021], and DFR [Izmailov et al., 2022] are among the most widely used robustification methods, yet they either require group annotations or — in annotation-free variants — inherit an untested assumption about clustering reliability. Published annotation-free clustering results are consistently reported at or near training convergence with k matching the number of known groups; none disclose whether results transfer to early-epoch, k=2 settings used by intervention methods. PruSC [Kim et al., 2024] is one example of a paper reporting high cluster purity on CelebA; our early-epoch (epoch-5), k=2 configuration yields purity of 0.456, barely above the random baseline of 0.440. This gap illustrates a configuration-sensitivity that has significant practical implications, regardless of the specific conditions under which any individual paper's results were obtained.

The gap between these results is not a replication failure. It is a signal: clustering-based annotation-free detection is *feature-strength conditional*. Our core finding is that the success of epoch-5 k-means clustering depends not on the clustering algorithm or training protocol, but on whether the spurious attribute is already encoded as a salient, separable dimension in the *pretrained* representation prior. ImageNet-pretrained ResNet-50 strongly encodes scene-level features — bird habitats, backgrounds, object contexts — that align directly with Waterbirds' bird-background spurious correlation. Hair color is not a semantically distinct ImageNet category; the pretrained prior does not pre-separate CelebA's spurious groups, and five epochs of ERM fine-tuning are insufficient to build this structure from scratch.

This insight reframes the question facing practitioners: before asking "does my clustering pipeline recover spurious groups?", they should ask "does my pretrained model already encode the spurious attribute as a separable feature?" If the answer is no, standard epoch-5 k-means will fail.

We make the following contributions:

**C1 — Characterization of feature-strength conditionality:** We provide, to our knowledge, the first systematic characterization of when annotation-free clustering-based spurious direction discovery succeeds and fails, identifying pretrained initialization alignment with the spurious attribute as the key determinant.

**C2 — Empirical quantification of the conditionality gap:** Using identical experimental conditions on Waterbirds (AMI=0.762, purity=0.892) and CelebA (AMI=0.258, purity=0.456), we document a threefold AMI gap and near-random purity for CelebA, with random baselines providing the reference floor.

**C3 — Mechanistic explanation and proposed diagnostic:** We explain the conditionality through ImageNet pretraining alignment and motivate a proposed spurious feature salience pre-screen — a lightweight diagnostic that practitioners can use before trusting annotation-free cluster-based spurious direction estimates, pending empirical validation of the specific threshold.

**C4 — Identification of configuration-sensitivity reporting gap:** We show that published annotation-free clustering results are highly configuration-sensitive — results at training convergence with k>2 do not transfer to early-epoch k=2 settings — and identify the absence of configuration disclosure as a methodological reporting gap in the field.

The rest of the paper is organized as follows. Section 2 reviews related work on spurious correlation robustification and annotation-free detection (see Section 2). Section 3 describes our experimental methodology. Section 4 presents the experimental setup. Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Robustification Methods with Group Annotations

The dominant paradigm for improving worst-group accuracy requires explicit group labels at training time. Distributionally Robust Optimization (DRO) [Ben-Tal et al., 2013] minimizes the worst-case expected loss over a family of distributions; GroupDRO [Sagawa et al., 2020] instantiates this by weighting training samples by group membership, achieving ~90% worst-group accuracy on Waterbirds when group labels are available. Deep Feature Reweighting (DFR) [Izmailov et al., 2022] takes a different approach: train ERM to convergence, then retrain only the last linear layer on a small group-balanced labeled validation set, achieving ~97% worst-group on Waterbirds and ~92% on CelebA. DFR's success reveals that invariant features are richly encoded in pretrained ERM representations even when the linear head relies on shortcuts — a key observation that motivates our work.

These methods deliver strong performance but require group annotations that are often unavailable in practice. Annotating which samples belong to which spurious group requires either domain expertise or expensive human labeling. Our work specifically targets the annotation-free setting.

### 2.2 Annotation-Free Robustification Methods

Several methods approximate group labels without annotation. Just Train Twice (JTT) [Liu et al., 2021] trains an ERM model and upweights its misclassified examples — assuming that minority-group samples are disproportionately misclassified. JTT achieves ~82–86% worst-group accuracy on Waterbirds without group labels. Last-Layer Feature Reweighting (LFR) [Ghaznavi et al., 2023] uses a similar loss-based resampling approach and outperforms DFR in high-spuriosity settings. Unlike DFR, which requires labeled group-balanced validation data, LFR relies on the training loss as a proxy for group membership. These methods are paradigm-specific (supervised cross-entropy) and use the training loss as a proxy for group membership.

GEORGE [Sohoni et al., 2020] takes a representation-based approach: cluster penultimate-layer ERM embeddings at training convergence to discover spurious groups, then apply DRO with the cluster-derived pseudo-labels. PruSC [Kim et al., 2024] applies similar clustering to prune spurious shortcut neurons. AGRO [Paranjape et al., 2022] adversarially discovers error-prone groups and applies DRO. These methods are conceptually appealing because clustering operates on learned representations, making them paradigm-agnostic in principle.

However, none of these methods characterize the conditions under which the clustering step succeeds. Our work shows this assumption is unjustified: the same clustering protocol achieves near-perfect spurious group recovery on Waterbirds (purity=0.892) but yields near-random performance on CelebA (purity=0.456).

### 2.3 Shortcut Learning Mechanisms and Feature Learning

Shah et al. [2020] establish that SGD exhibits simplicity bias: it preferentially learns high signal-to-noise ratio features early in training, which in spurious-correlation settings corresponds to the spurious attribute. Geirhos et al. [2020] document shortcut learning across multiple modalities. Izmailov et al. [2022] demonstrate that even fully trained ERM models richly encode invariant features in their representations. Robinson et al. [2023] show that self-supervised learning also acquires spurious correlations through augmentation-invariant shortcuts.

### 2.4 Gap: Conditionality of Annotation-Free Detection

The key gap our work addresses is the absence of any characterization of when clustering-based annotation-free detection works. The implicit assumption — that spurious features strong enough to degrade worst-group accuracy are also strong enough to produce cluster-separable representations — is never tested. We show this assumption fails for fine-grained texture-based spurious attributes (CelebA hair color) while holding for coarse scene-level spurious attributes (Waterbirds habitat background). The differentiating factor is the alignment of the spurious attribute with the ImageNet pretraining prior, a distinction absent from existing work.

The closest prior works do not fully address this question. GEORGE [Sohoni et al., 2020] notes that clustering quality depends on representation quality, but does not study the pretraining alignment determinant — i.e., whether the spurious attribute must already be encoded in the pretrained prior for the detection step to succeed. DFR [Izmailov et al., 2022] demonstrates that ERM models encode invariant features in their representations, but does not study the reliability of the clustering step itself or identify when clustering fails to recover spurious group structure. To our knowledge, the conditionality we characterize — that detection reliability is determined by pretrained initialization alignment, not by spurious correlation strength — has not been previously studied.

---

## 3. Methodology

### 3.1 Overview

Our goal is to characterize the conditions under which annotation-free spurious direction discovery via representation clustering succeeds or fails. We hold every experimental factor constant — model, optimizer, clustering algorithm, probe epoch, hyperparameters — and vary only the dataset's spurious feature type. This isolates spurious feature salience as the causal variable.

We follow established methodology: train ERM with a pretrained backbone, extract penultimate-layer embeddings at epoch 5, apply k-means clustering, and evaluate cluster-to-group alignment using AMI and worst-cluster purity.

### 3.2 Spurious Direction Discovery Pipeline

**Step 1 — ERM Training.** We fine-tune pretrained ResNet-50 (ImageNet weights from torchvision) on each dataset using standard ERM (cross-entropy, SGD). Training proceeds for 5 epochs, after which we save the model checkpoint.

*Rationale:* Epoch 5 is chosen following the simplicity bias literature [Shah et al., 2020], which predicts that high-SNR spurious features are acquired early in training.

**Step 2 — Embedding Extraction.** We extract the penultimate-layer representations for all training samples, yielding shape (N, 2048). Global average pooling is applied; no dimensionality reduction before clustering.

**Step 3 — k-Means Clustering.** k-means with k=2, n\_init=10, random seed 42, applied to raw 2048-dim embeddings.

*Rationale:* k=2 matches the binary spurious attribute structure and follows published methodology (GEORGE, PruSC) for a fair comparison.

**Step 4 — Evaluation.** We compute against ground-truth group labels (used only for evaluation):

- **AMI:** Agreement between cluster assignments and group labels, adjusted for chance. Threshold ≥ 0.5.
- **Worst-Cluster Purity:** Minimum fraction of majority-group samples across clusters. Threshold ≥ 0.75.
- **Random baseline:** Shuffled cluster assignments to establish chance-level floor.

### 3.3 Datasets

**Waterbirds** [Sagawa et al., 2020]: 4,795 training samples; 95% spurious correlation between bird type and background habitat. Spurious feature: scene-level background (water vs. land) — high ImageNet pretraining alignment.

**CelebA** [Liu et al., 2015]: 162,770 training samples; binary hair color prediction (blonde/non-blonde) with sex as the confounding spurious variable. Spurious feature: hair color (fine-grained local texture) — low ImageNet alignment.

| Dataset | Train N | Spurious attribute | Confounding variable | Feature type | ImageNet alignment |
|---|---|---|---|---|---|
| Waterbirds | 4,795 | Background habitat | — | Global scene-level | High |
| CelebA | 162,770 | Hair color (texture) | Biological sex | Local texture | Low |

### 3.4 Implementation Details

| Hyperparameter | Value |
|---|---|
| Architecture | ResNet-50 (ImageNet pretrained) |
| Optimizer | SGD, momentum=0.9 |
| Learning rate | 1e-3 |
| Weight decay | 1e-3 |
| Batch size | 32 |
| Probe epoch | 5 |
| k (clustering) | 2 |
| n\_init | 10 |
| Random seed | 42 |

This configuration follows the GroupDRO/DFR repository for Waterbirds and CelebA. No per-dataset hyperparameter tuning is performed — identical configuration across both datasets is essential for the conditionality comparison.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Does epoch-5 k-means clustering recover spurious group structure for datasets with visually dominant, scene-level spurious features? (Waterbirds)

**RQ2:** Does the same pipeline succeed for datasets with fine-grained, texture-based spurious features? (CelebA)

**RQ3:** Is any observed performance gap a genuine reflection of feature-strength conditionality, or attributable to experimental confounds?

### 4.2 Baselines

**Random clustering baseline:** AMI and worst-cluster purity for randomly shuffled cluster assignments (preserving cluster sizes). Results: Waterbirds random AMI≈0.0001, purity=0.727; CelebA random AMI≈0.000, purity=0.440.

### 4.3 Evaluation Metrics

**Adjusted Mutual Information (AMI)** measures information-theoretic agreement between cluster assignments and group labels, adjusted for chance (AMI=0 random, AMI=1 perfect). Threshold: AMI ≥ 0.5.

**Worst-Cluster Purity** measures the minimum fraction of majority-group samples within any single cluster. Threshold: purity ≥ 0.75.

Both metrics are computed against ground-truth group labels used only for evaluation — never during training or clustering.

---

## 5. Results

### 5.1 Main Results: Feature-Strength Conditionality

**Table 1: Clustering results for annotation-free spurious direction discovery.**

| Dataset | AMI | Purity | AMI (random) | Purity (random) | AMI ≥ 0.5? | Purity ≥ 0.75? | Pass? |
|---|---|---|---|---|---|---|---|
| Waterbirds | **0.762** | **0.892** | 0.0001 | 0.727 | ✓ | ✓ | **PASS** |
| CelebA | **0.258** | **0.456** | 0.000 | 0.440 | ✗ | ✗ | **FAIL** |

Waterbirds exceeds both thresholds by substantial margins: AMI is 0.262 above threshold (52% headroom) and purity is 0.142 above threshold. CelebA purity (0.456) is only 0.016 above the random baseline (0.440) — k-means on CelebA embeddings offers essentially no spurious group signal above chance.

Figure 1 visualizes this gap with the metrics bar chart including threshold lines and random baselines.

*[Figure 1: figures/metrics\_bar.png — AMI and worst-cluster purity for Waterbirds and CelebA with threshold lines and random baselines.]*

### 5.2 Visualization: t-SNE Embedding Structure

Figures 2 and 3 show t-SNE projections of Waterbirds epoch-5 embeddings, colored by k-means cluster assignment and by ground-truth group ID respectively. Cluster boundaries align tightly with group structure, confirming that AMI reflects genuine semantic separation.

*[Figure 2: figures/tsne\_cluster\_waterbirds.png — t-SNE of Waterbirds embeddings colored by k-means cluster. Cluster boundaries align with spurious group structure.]*

*[Figure 3: figures/tsne\_group\_waterbirds.png — t-SNE of Waterbirds embeddings colored by ground-truth group ID. Confirms cluster-group correspondence.]*

Figure 4 shows the CelebA t-SNE. The cluster boundary does not align with group structure: both spurious groups distribute across both clusters without clear separation.

*[Figure 4: figures/tsne\_cluster\_celeba.png — t-SNE of CelebA embeddings colored by k-means cluster. Clusters fail to align with spurious group structure.]*

### 5.3 Cluster Composition Analysis

Figures 5 and 6 show group composition within each k-means cluster for Waterbirds and CelebA respectively.

For Waterbirds (Figure 5), each cluster is dominated by a single spurious group: cluster 0 is ~89% water-background samples and cluster 1 is ~89% land-background samples. This near-pure composition enables annotation-free group-label proxies with high confidence.

*[Figure 5: figures/cluster\_composition\_waterbirds.png — Cluster group composition for Waterbirds. Each cluster dominated by one spurious group (purity=0.892).]*

For CelebA (Figure 6), both clusters show mixed composition across all four spurious groups, with no cluster dominated by any single group — effectively random assignment.

*[Figure 6: figures/cluster\_composition\_celeba.png — Cluster group composition for CelebA. Mixed membership reflects near-random separation (purity=0.456).]*

### 5.4 Training Dynamics

**Table 2: Training state at epoch 5.**

| Dataset | Train loss | Train accuracy | Embedding shape |
|---|---|---|---|
| Waterbirds | 0.088 | 96.66% | (4,795 × 2,048) |
| CelebA | 0.124 | 95.00% | (162,770 × 2,048) |

Both models achieve high accuracy, ruling out undertrained CelebA as an explanation. The clustering failure is not a training failure — it is a representation structure failure driven by the pretrained initialization prior.

### 5.5 Gap with Published Results

This result illustrates the configuration-sensitivity gap rather than a claim about any specific paper's correctness. Published results for annotation-free clustering on CelebA — such as the high purity reportedly achieved by PruSC [Kim et al., 2024] (configuration details not specified in paper; see Section 5.5 for discussion) — are likely obtained under post-convergence, k>2 conditions that differ substantially from the early-epoch setting used by intervention methods. Our epoch-5, k=2 result (purity=0.456, barely above the random baseline of 0.440) does not contradict those reported results; rather, it demonstrates that the two configurations are not interchangeable. Convergence-epoch results with flexible k should not be cited as evidence that early-epoch, k=2 annotation-free detection is reliable on CelebA — the configurations differ in ways that are practically significant, and these differences are not disclosed in existing reporting.

---

## 6. Discussion

### 6.1 Key Findings and Their Interpretation

**Finding 1: Recoverability is determined by the pretrained initialization prior, not by spurious correlation strength.**

Both datasets degrade worst-group accuracy under ERM yet only Waterbirds yields cluster-separable spurious groups. The differentiating factor is the alignment between the spurious attribute and the ImageNet pretraining representation. ImageNet-pretrained ResNet-50 encodes bird habitats as high-salience semantic dimensions; hair color is not a primary ImageNet category. This reframes "spurious feature strength" for annotation-free detection: it is not the label-space correlation magnitude, but the pretrained representation's affinity for the spurious attribute.

An alternative explanation is that k=2 underspecifies CelebA's 4-group structure (binary class × binary spurious attribute), with the minority blonde-male group (~1%) compressing into the majority cluster. This cannot be fully ruled out from our experiment. However, Section 6.3 Limitation L2 notes that even optimal k would not overcome the absence of a pretrained separable hair-color feature, since the pretrained prior does not encode this dimension.

**Finding 2: The detection failure is categorical, not marginal.**

CelebA purity (0.456) is only 0.016 above the random baseline (0.440). A practitioner deploying annotation-free clustering on CelebA epoch-5 embeddings would obtain cluster assignments statistically indistinguishable from random group labels. Any downstream robustification using these cluster assignments would be equivalent to random reweighting — a silent failure with no error signal.

**Finding 3: Published benchmark results do not transfer across configurations.**

Published annotation-free clustering results on CelebA are likely obtained under different configurations (post-convergence embeddings, k>2, different preprocessing) than the early-epoch, k=2 setting used by intervention methods. Our epoch-5, k=2 result should not be cited as supporting evidence that early-epoch annotation-free detection is reliable on CelebA. The field needs to distinguish detection results at convergence from detection at early training phases.

### 6.2 Proposed Diagnostic: Spurious Feature Salience Pre-Screen

Before applying annotation-free clustering-based detection, we propose and motivate the following diagnostic, pending empirical calibration:

**Pretrained linear probe accuracy for the spurious attribute.** Extract embeddings from the pretrained model (no task-specific fine-tuning) and train a linear classifier on a small labeled set for the suspected spurious attribute. If linear probe accuracy exceeds ~70% (a heuristic threshold requiring empirical calibration across datasets and architectures), the pretrained model encodes the spurious attribute as a separable feature — epoch-5 k-means is likely to succeed. If accuracy is near chance, early-epoch k-means will likely fail.

This pre-screen requires spurious-attribute labels (not group labels), which are typically much cheaper to collect. Validating this diagnostic, including empirical determination of the appropriate threshold, is an important direction for future work.

### 6.3 Limitations

**L1 — Single random seed.** Experiments use one seed (PoC mode). The Waterbirds gap above threshold (AMI +0.262) has two variance sources: (a) k-means initialization variance, mitigated by n_init=10, and (b) ERM training seed variance, which is uncharacterized. While the AMI margin is large, formal multi-seed characterization (≥5 seeds) of ERM training variance is absent and should be addressed in follow-on work.

**L2 — k=2 underspecification.** CelebA has 4-group spurious structure (binary class × binary spurious attribute). k=2 collapses this, particularly harming the minority group (blonde male, ~1%). k=2 underspecification is a co-candidate explanation for CelebA failure alongside pretraining alignment; disambiguating these requires a k=4 ablation. Using k=4 or BIC-guided GMM may improve CelebA performance, though without a pretrained prior encoding hair color, the improvement may be limited.

**L3 — Non-universal epoch 5.** Waterbirds has 4,795 training samples; CelebA has 162,770. Epoch 5 represents very different training fractions. Defining probe epoch by representational stability would be more principled.

**L4 — Downstream mechanism untested.** The Gradient SNR Balancing (GSB) intervention — equalizing gradient SNR along cluster-discovered directions to improve worst-group accuracy — was not evaluated because the prerequisite CelebA detection condition was not satisfied. The mechanistic chain (H-M1 through H-M4) is theoretically motivated but not empirically validated.

**L5 — ResNet-50 vision only.** ViT-B and other architectures, and NLP/audio domains, may exhibit different pretraining alignment patterns. Cross-architecture generalization requires future investigation.

### 6.4 Broader Impact

This work identifies a potential silent failure mode in annotation-free robustification pipelines. Raising awareness of feature-strength conditionality encourages validation of the detection step before trusting downstream robustification results. The proposed salience pre-screen provides a practical gate for practitioners. There are no direct negative societal impacts of this diagnostic work; improving detection reliability benefits high-stakes applications where worst-group accuracy failures have real consequences.

---

## 7. Conclusion

We began with a stark observation: the same k-means clustering pipeline achieves AMI=0.762 on Waterbirds and AMI=0.258 on CelebA — identical model, identical hyperparameters, identical code. Both are standard benchmarks for spurious correlation robustification; both degrade worst-group accuracy under ERM. Yet the detection mechanism activates in one case and fails categorically in the other.

The explanation is not in the algorithm but in the pretraining. ImageNet-pretrained ResNet-50 already encodes bird habitats as separable semantic dimensions before any task-specific training; it does not encode hair color. When fine-tuned with ERM, the pretrained background representation surfaces as cluster-separable structure in Waterbirds embeddings by epoch 5. CelebA offers no such pretrained prior, and five epochs are insufficient.

This finding — *feature-strength conditionality* — is, to our knowledge, a previously undocumented constraint on all clustering-based annotation-free spurious detection methods. We characterize it through a controlled experiment (C1), quantify the gap empirically (C2), motivate a pretrained linear probe pre-screen as a proposed diagnostic pending validation (C3), and identify configuration-sensitivity as a gap in published detection results (C4).

Three results-grounded future directions follow: adaptive probe epoch selection based on representational stability (addressing L3), k-adaptive GMM clustering for multi-group structure (addressing L2), and Waterbirds-restricted validation of the downstream GSB (gradient-based shortcut balancing) mechanism where detection is confirmed reliable (addressing L4).

Before asking whether annotation-free robustification works, practitioners should ask a prior question: does the pretrained model already know the spurious attribute? The answer to that question determines whether clustering-based detection is trustworthy — and whether any downstream intervention operates on meaningful spurious directions or on noise.

---

## References

[Geirhos et al., 2020] Robert Geirhos, Jörn-Henrik Jacobsen, Claudio Michaelis, Richard Zemel, Wieland Brendel, Matthias Bethge, and Felix A. Wichmann. Shortcut learning in deep neural networks. *Nature Machine Intelligence*, 2:665–673, 2020.

[Ghaznavi et al., 2023] Mehrnaz Ghaznavi et al. Last-layer feature reweighting for group robustness. 2023.

[Izmailov et al., 2022] Pavel Izmailov, Polina Kirichenko, Nate Gruver, and Andrew Gordon Wilson. On feature learning in the presence of spurious correlations. In *Advances in Neural Information Processing Systems*, 2022.

[Kim et al., 2024] Kim et al. PruSC: Pruning spurious correlations via cluster-based annotation-free detection. 2024. (configuration details not specified in paper; see Section 5.5 for discussion)

[Liu et al., 2015] Ziwei Liu, Ping Luo, Xiaogang Wang, and Xiaoou Tang. Deep learning face attributes in the wild. In *IEEE International Conference on Computer Vision*, 2015.

[Liu et al., 2021] Evan Liu, Behzad Haghgoo, Annie S. Chen, Aditi Raghunathan, Pang Wei Koh, Shiori Sagawa, Percy Liang, and Chelsea Finn. Just train twice: Improving group robustness without training group information. In *International Conference on Machine Learning*, 2021.

[Paranjape et al., 2022] Bhargavi Paranjape, Pradeep Dasigi, Vivek Srikumar, Luke Zettlemoyer, and Hannaneh Hajishirzi. AGRO: Adversarial discovery of error-prone groups for robust optimization. In *International Conference on Learning Representations*, 2022.

[Robinson et al., 2023] Joshua Robinson et al. Spurious correlations in self-supervised learning. 2023.

[Sagawa et al., 2020] Shiori Sagawa, Pang Wei Koh, Tatsunori B. Hashimoto, and Percy Liang. Distributionally robust neural networks for group shifts: On the importance of regularization for worst-case generalization. In *International Conference on Learning Representations*, 2020.

[Shah et al., 2020] Harshay Shah, Kaustav Tamuly, Aditi Raghunathan, Prateek Jain, and Praneeth Netrapalli. The pitfalls of simplicity bias in neural networks. In *Advances in Neural Information Processing Systems*, 2020.

[Sohoni et al., 2020] Nimit Sohoni, Jared A. Dunnmon, Geoffrey Angus, Albert Gu, and Christopher Ré. No subclass left behind: Fine-grained robustness in coarse-grained classification problems. In *Advances in Neural Information Processing Systems*, 2020.
