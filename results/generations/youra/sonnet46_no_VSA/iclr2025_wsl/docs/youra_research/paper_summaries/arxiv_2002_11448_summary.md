---
source_paper: "arxiv_2002_11448.md"
generated_at: "2026-08-03T17:29:27.154176"
model: "openai/gpt-5.2"
summary_chars: 12951
---

# Predicting Neural Network Accuracy from Weights

## Key Metadata
- **Authors:** Thomas Unterthiner et al.
- **Year:** 2020
- **Venue:** arXiv (preprint 2002.11448)
- **Core Contribution:** Introduces a formal and empirical framework showing that a model’s (test) accuracy can be predicted—and models can be ranked—using only their trained weights (often via simple per-layer weight statistics), including transfer across datasets and architectures.

## Section Summaries

### Abstract
We show experimentally that the accuracy of
a trained neural network can be predicted surpris-
ingly well by looking only at its weights, with-
out evaluating it on input data. We motivate this
task and introduce a formal setting for it. Even
when using simple statistics of the weights, the
predictors are able to rank neural networks by
their performance with very high accuracy (R2
score more than 0.98). Furthermore, the predic-
tors are able to rank networks trained on differ-
ent, unobserved datasets and with different archi-
tectures. We release a collection of 120k con-
volutional neural networks trained on four dif-
ferent datasets to encourage further research in
this area, with the goal of understanding network
training and performance better.

### Introduction & Motivation
The paper studies whether a trained neural network’s accuracy can be inferred from its **weights alone**, without evaluating on any input data. This is motivated by scientific interest (understanding training/generalization phenomena) and practical applications (e.g., early termination of poor runs without running inference). The authors focus first on an **under-parameterized** CNN regime where train/test accuracies are similar, then test transfer to **over-parameterized** ResNets. A key goal is to probe for **invariant properties** of trained weights that generalize across **dataset shift** and **architecture shift**.

### Methodology
The authors formalize “predict accuracy from weights” as learning a regression map from trained parameters to expected accuracy under a fixed but unknown data distribution. Let \(P(X,Y)\) be the (unknown) data-generating distribution and \(S_N=\{(X_i,Y_i)\}_{i=1}^N\) be the training set sampled i.i.d. from \(P\). A learning procedure \(A\) with hyperparameters \(\lambda\) (architecture choices, optimizer settings, initialization, regularization, training-set fraction, etc.) produces trained weights
\[
W = A(S_N,\lambda).
\]
The corresponding classifier is \(h(\cdot;W):\mathcal{X}\to\mathcal{Y}\), with training accuracy \(\widehat{\mathrm{Acc}}(W,S_N)=\frac{1}{N}\sum_{i=1}^N \mathbf{1}\{h(X_i;W)=Y_i\}\) and expected accuracy \(\mathrm{Acc}_P(W)=\mathbb{E}_{(X,Y)\sim P}[\mathbf{1}\{h(X;W)=Y\}]\). The goal is to learn an estimator \(\widehat{F}: W\mapsto [0,1]\) approximating \(W\mapsto \mathrm{Acc}_P(W)\), trained on a collection \(C=\{(W_k,T_k)\}_{k=1}^K\) where \(T_k\) is **test accuracy** measured on an independent test set \(S'_M\): \(T_k=\widehat{\mathrm{Acc}}(W_k,S'_M)\). Estimators are trained by minimizing **mean squared error (MSE)** on such pairs.

They instantiate \(\widehat{F}\) using three off-the-shelf regressors: (i) **logit-linear model (L-Linear)** trained with mini-batch SGD/Adam (tuning learning rate, batch size, initialization, \(\ell_2\) regularization); (ii) **gradient boosting machine (GBM)** via LightGBM (tuning tree depth/leaves, learning rate, \(\ell_1/\ell_2\) regularization, feature/example subsampling); and (iii) a **fully-connected DNN regressor** with ReLU hidden layers and sigmoid output, trained with mini-batch SGD/Adam (tuning depth/width, learning rate, \(\ell_2\), initialization type/variance, batch size). Inputs to \(\widehat{F}\) vary: raw flattened weights \(W\in\mathbb{R}^{4970}\); single-layer weights \(W^\ell\) (notably \(W^4\) = last dense layer); global weight summary \(\widehat{W}\in\mathbb{R}^7\) (mean, variance, and percentiles at \(q\in\{0,25,50,75,100\}\)); per-layer kernel/bias summaries \(\widehat{W}_L\in\mathbb{R}^{56}\) (4 layers \(\times\) {kernel,bias} \(\times 7\)); and per-layer norms \(W^{\ell_1}_L, W^{\ell_2}_L \in\mathbb{R}^8\). They also compare to predicting from hyperparameters \(\lambda\) (7 parameters) and \((\lambda,W)\).

A key methodological theme is **domain shift**: training \(\widehat{F}\) on networks trained on one dataset/architecture and evaluating its ability to rank networks trained on *unseen* datasets or architectures, measured primarily via **Kendall’s \(\tau\)** rank correlation when absolute calibration drifts.

### Experiments & Results
**Small CNN Zoo dataset.** The core empirical resource is a new dataset of ~120k trained CNNs: 4 collections of ~30k models each (after filtering numerical instabilities): MNIST \(C_M\) (29,996), Fashion-MNIST \(C_F\) (29,999), grayscale CIFAR-10 \(C_C\) (29,999), grayscale SVHN \(C_S\) (29,987). All models share a fixed small CNN: **3 convolutional layers** with **16 filters each**, then **global average pooling**, then a **fully-connected layer**, totaling **4,970 learnable weights**. Inputs are grayscale; pixel values are scaled to \([-1,1]\). Training runs use **86 epochs**, **no data augmentation**, **no batch normalization**. For each dataset, they sample **30k hyperparameter configurations** (one random seed per configuration to reduce train/test leakage across splits), varying optimizer (SGD vs Adam/RMSProp), learning rate, initialization type and variance, fraction of training data, activation function, dropout, and \(\ell_2\) weight regularization.

**Train/validation/test protocol (for regressors).** For each dataset’s CNN collection, **15k networks** are used to train/choose the regressor and the remainder held out as test. Model selection uses **3-fold CV** on the 15k training networks. For each (estimator type × feature choice × dataset), they evaluate **1,000 randomly sampled regressor hyperparameter configurations**.

**Metrics.** Regressors optimize **MSE** and report **MAE** and **\(R^2\)** (coefficient of determination). Under dataset transfer, they emphasize **Kendall’s \(\tau\)** because absolute accuracy scales differ across datasets.

**Main within-dataset results (predict test accuracy).** GBM and DNN strongly outperform the logit-linear model. For CIFAR10-GS (Table 1), \(R^2\) with GBM is \(\approx 0.97\) on raw \(W\) and rises to **0.984** with per-layer statistics \(\widehat{W}_L\). Across all four datasets (Table 2), the best-performing features are consistently **per-layer statistics \(\widehat{W}_L\)**, reaching \(R^2\) of **0.993 (MNIST)**, **0.993 (Fashion-MNIST)**, **0.984 (CIFAR10-GS)**, **0.986 (SVHN-GS)**. Using only the final dense layer \(W^4\) is surprisingly competitive (e.g., CIFAR10-GS \(R^2=0.969\), SVHN-GS \(R^2=0.967\)). Using norms \(W^{\ell_1}_L\) or \(W^{\ell_2}_L\) is slightly worse than raw \(W\)/\(W^4\). Predicting from hyperparameters \(\lambda\) alone is very poor (e.g., CIFAR10-GS \(R^2=0.015\)); adding \(\lambda\) to \(W\) does not help.

**Transfer across datasets (domain shift).** When a GBM trained on one dataset is evaluated on another, calibration drifts, but **ranking remains strong**. Using Kendall’s \(\tau\) (Table 3) with \(\widehat{W}_L\): e.g., training on CIFAR10-GS and testing on SVHN-GS yields \(\tau=0.75\); training on MNIST and testing on CIFAR10-GS yields \(\tau=0.80\). The worst reported transfer is SVHN-GS \(\to\) MNIST with \(\tau=0.60\); many cross-dataset transfers are \(\tau\approx 0.65\)–0.80, indicating substantial invariant signal in weights.

**Transfer to larger architectures (ResNet).** They test architecture shift using **DEMOGEN** (from Jiang et al., 2019): **216 Wide-ResNet32** models (ResNet32×1/×2/×4; 72 each) trained on **colored CIFAR-10**, achieving up to **100% train** and **93% test** accuracy. Because \(\widehat{W}^4_L\) (final-layer statistics) has fixed dimension (\(\in\mathbb{R}^{14}\)) across architectures, they apply a CIFAR10-GS-trained GBM (trained on small CNNs) to ResNets and evaluate ranking vs train/test accuracy. Kendall’s \(\tau\) (Table 4): for width ×2, predictions vs train \(\tau=0.62\), vs test \(\tau=0.59\); width ×4, vs train \(\tau=0.50\), vs test \(\tau=0.32\); width ×1, vs train \(\tau=0.30\), vs test \(\tau=0.28\). As reference, train vs test rank correlation drops with width (0.83 → 0.64), consistent with increased overfitting; predictors correlate slightly more with train than test, suggesting a potential “train-accuracy shortcut.”

**Ablations / diagnostic analyses.**
- **Feature ablations:** \(\widehat{W}_L\) > raw \(W\) > norms > global stats \(\widehat{W}\) > hyperparameters \(\lambda\). Subset-layer statistics \(\widehat{W}^4_L\) and \(\widehat{W}^{1,4}_L\) are strong but slightly worse than full \(\widehat{W}_L\).
- **Invariance probes:** For a predictor trained on raw \(W\), perturbations \(W\mapsto \phi(W)\) yield mean absolute deviation (MAD) in predictions ranging **0.01–0.13**. Scaling by \(c\in\{2,10,100\}\) or permuting within conv layers gives MAD < 0.05; permuting within final dense layer gives MAD ≈ 0.06; global permutation or scaling by \(c\in\{10^{-1},10^{-3}\}\) yields MAD > 0.11. Thus, learned predictors are partially robust to conv-layer parameter ordering and large positive rescalings, but sensitive to final-layer structure and strong downscaling.
- **Qualitative weight-statistic signal:** For CIFAR10-GS, they observe bias range \((\max-\min)\) in first and last layer correlates with accuracy; SGD-trained models cluster differently than Adam/RMSProp; a failure mode (“tentacles” near chance) can be separated via max bias in final dense layer (<0.1 vs >0.1).

#### Compact main results tables (from the paper)

**Table A: Within-dataset \(R^2\) using GBM (selected rows; full Table 2 in text)**

| Features (GBM) | MNIST | Fashion-MNIST | CIFAR10-GS | SVHN-GS |
|---|---:|---:|---:|---:|
| \(W^4\) (last layer weights) | 0.987 | 0.989 | 0.969 | 0.967 |
| \(W\) (all weights) | 0.988 | 0.989 | 0.970 | 0.971 |
| \(\widehat{W}\) (global 7 stats) | 0.953 | 0.955 | 0.914 | 0.908 |
| **\(\widehat{W}_L\) (per-layer stats; 56 dims)** | **0.993** | **0.993** | **0.984** | **0.986** |
| \(\lambda\) (hyperparameters only) | 0.024 | 0.035 | 0.015 | 0.034 |

**Table B: Cross-dataset transfer (Kendall’s \(\tau\); Table 3)**

| Train \(\to\) Test | MNIST | Fashion-MNIST | CIFAR10-GS | SVHN-GS |
|---|---:|---:|---:|---:|
| MNIST | 0.92 | 0.77 | 0.80 | 0.73 |
| Fashion-MNIST | 0.70 | 0.92 | 0.77 | 0.65 |
| CIFAR10-GS | 0.68 | 0.68 | 0.93 | 0.75 |
| SVHN-GS | 0.60 | 0.63 | 0.74 | 0.85 |

**Table C: Architecture transfer to Wide-ResNet32 on CIFAR-10 (Kendall’s \(\tau\); Table 4)**

| ResNet width | Pred vs Train | Pred vs Test | Train vs Test (baseline) |
|---|---:|---:|---:|
| ×1 | 0.30 | 0.28 | 0.83 |
| ×2 | 0.62 | 0.59 | 0.77 |
| ×4 | 0.50 | 0.32 | 0.64 |

### Discussion & Conclusion
The experiments demonstrate that trained weights encode a surprisingly strong signal for predicting/ranking model accuracy, and that simple per-layer statistics can outperform using the full flattened weight vector. Transfer results (cross-dataset Kendall’s \(\tau\approx 0.6\)–0.8; cross-architecture positive \(\tau\)) suggest the existence of partially **invariant weight–performance relationships**, though predictors may sometimes correlate more with **train** than **test** accuracy in over-parameterized regimes. The authors propose exploring predictors with stronger inductive biases (e.g., permutation invariance via **Deep Sets**) and extending beyond CNNs to other domains (NLP, RL, unsupervised learning).

## Key Contributions
- Proposes a **formal supervised-learning setting** for mapping trained weights \(W\) to expected accuracy \(\mathrm{Acc}_P(W)\), and highlights **domain shift** (dataset/architecture transfer) as a key test of invariances.
- Releases the **Small CNN Zoo**: ~120k trained CNNs on 4 datasets with rich hyperparameter variation, enabling regression from network weights to performance.
- Empirically shows **high-fidelity accuracy prediction/ranking from weights alone**, often with simple features (per-layer quantiles/moments) achieving **\(R^2>0.98\)** within dataset and strong **rank transfer** across datasets and to ResNet architectures.

## Potential Relevance
This work provides a concrete experimental recipe and dataset modality for studying “what trained weights reveal,” which can support hypotheses about **weight statistics as proxies** for optimization quality, implicit regularization, or training dynamics. The strong performance of tiny feature sets (e.g., \(\widehat{W}_L\), \(\widehat{W}^4_L\)) suggests promising baselines for **model selection without data access** (or without inference), and the domain-shift results offer a framework for testing whether proposed generalization indicators are **dataset-/architecture-invariant** or merely correlated within a narrow training regime.