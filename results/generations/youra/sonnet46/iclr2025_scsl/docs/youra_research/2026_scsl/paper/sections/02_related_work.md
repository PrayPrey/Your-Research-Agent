# 2. Related Work

## 2.1 Spurious Correlation Robustness

The problem of spurious correlations — statistical associations between features and labels that do not hold across all subgroups — was formalized as a benchmark challenge by Sagawa et al. [2019] with the introduction of Waterbirds and the GroupDRO training objective. GroupDRO minimizes the maximum group-specific loss at each step, achieving strong WGA on Waterbirds and CelebA, but requires group annotations for all training samples, making it an oracle method in the label-free setting. Subsequent work has focused on achieving GroupDRO-competitive WGA without group supervision.

Idrissi et al. [2022] showed that simple data balancing — subsampling to equalize class and group representation — serves as a surprisingly competitive baseline, often matching more complex methods. This underscores that the core challenge is identifying which samples to treat as minority, since once identified, balanced retraining works well. Our work directly addresses the identification problem.

## 2.2 Label-Free Two-Stage Methods

The dominant paradigm for label-free spurious correlation debiasing is the two-stage approach: train an ERM model, use some signal to identify pseudo-minority samples, then retrain with minority overrepresentation.

**Just Train Twice (JTT)** [Liu et al., 2021] uses binary misclassification by an ERM model trained for a small number of epochs as a minority proxy: the error set E = {i : model(xᵢ) ≠ yᵢ} is upweighted in a second training stage. JTT achieves strong WGA improvements (+21pp on Waterbirds) but uses a binary, coarse signal. JTT's proxy is implicit — it captures minority samples because they are the samples the ERM model fails to fit, not because it explicitly targets the gradient dynamics that explain why they fail.

**Learning from Failure (LfF)** [Nam et al., 2020] trains two networks simultaneously and uses the generalized CE loss ratio between a biased network and a debiased network to identify hard (minority) samples. The relative loss serves as a continuous proxy, but it requires running two parallel training streams and the signal is not grounded in a mechanistic decomposition of the learning dynamics.

**Loss-based Reweighting (LFR)** [Ghaznavi et al., 2023] uses high-loss samples as minority proxies during the early training phase. Like LfF, this is a loss-magnitude-based proxy. While conceptually similar to our gradient-norm signal (high loss → high gradient), raw loss magnitude does not account for feature-scale differences across groups or the last-layer gradient structure.

**DFR (Deep Feature Reweighting)** [Kirichenko et al., 2022] demonstrates that ERM-trained features already encode the non-spurious (core) features needed for good WGA — the problem is in the classifier head's weighting. DFR freezes the ERM backbone and retrains only the last classification layer using a group-balanced validation subset, achieving 92.9% WGA on Waterbirds. DFR establishes the theoretical foundation that GNR-LLR builds on: if we can construct a pseudo-group-balanced subset without oracle group labels, we can apply the same last-layer retraining principle. DFR requires group labels for the balanced subset; our work addresses exactly this labeling requirement.

No existing work in this paradigm uses per-sample gradient norms as the minority identification signal.

## 2.3 Gradient Dynamics and Training Theory

Several theoretical frameworks analyze the relationship between gradient behavior and group membership during spurious correlation learning.

**Norm Hierarchy Theory (NHT)** [Khanh & Hoa, 2026] provides a formal framework predicting that during ERM training on spuriously correlated data, shortcut representations are norm-accessible first (majority groups learn the shortcut early) while minority groups resist the shortcut attractor basin. NHT predicts that minority samples should produce persistently elevated gradient norms relative to majority samples during early training — precisely the signal our work confirms experimentally. Our finding of ratio=8.8x at epoch 5 and 8.5x at epoch 10 is consistent with NHT's temporal persistence predictions, though we do not directly measure T_peak_sc.

**Edge of Stability (EOS) Dynamics** [Cohen et al., 2021] establish that gradient noise (from large learning rates near the EOS regime) can amplify differences in per-sample learning rates, potentially contributing to gradient norm disparity between groups. Our experimental observation that the gradient norm ratio increases monotonically from epochs 1–10 aligns with the co-occurrence of EOS dynamics in early ResNet-50 training.

**Heavy-Tailed Gradient Frameworks** [Rosenfeld & Risteski, 2023] provide theoretical grounding for why minority groups produce opposing gradient signals during the shortcut learning phase. This work confirms the asymmetric learning dynamics that our method exploits, though it focuses on the directional (oscillation) properties of gradients rather than the magnitude signal we use.

## 2.4 Group Discovery Methods

**GEORGE** [Zhang et al., 2022] discovers pseudo-groups via unsupervised clustering in the model's representation space, then applies GroupDRO with the discovered groups. This approach requires a full clustering step over the training set and is sensitive to clustering hyperparameters. In contrast, GNR-LLR uses a scalar per-sample signal that requires no clustering.

**Contrastive and Self-Supervised Approaches** [Creager et al., 2021; Liu et al., 2023] use representation learning objectives to discover spurious correlations without group labels. These methods typically involve more complex training pipelines and are complementary to our proxy-signal-based approach.

## 2.5 Our Position

GNR-LLR occupies a distinct position in this landscape: it provides a continuous, theoretically grounded minority proxy signal derived directly from last-layer training dynamics, requiring no changes to the training objective, no parallel networks, no clustering, and no group labels. The outer-product decomposition of the CE gradient provides a mechanistic interpretation that other proxy signals lack. While we establish the quality of this proxy signal (AUC=0.914), the complete two-stage pipeline — gradient norm identification followed by last-layer retraining — represents the natural next step connecting our signal to the WGA outcomes demonstrated by JTT and DFR.
