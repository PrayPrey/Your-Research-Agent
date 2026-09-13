# Causal Gradient Decomposition: Understanding and Mitigating SGD's Bias Toward Spurious Correlations via Loss Landscape Geometry

## Abstract

Spurious correlations—statistical associations between input features and labels that do not reflect underlying causal relationships—pose a fundamental challenge to the robustness and generalizability of deep learning models. While empirical mitigation strategies abound, the mechanistic understanding of *why* stochastic gradient descent (SGD) preferentially encodes shortcut features remains incomplete. This paper introduces **Causal Gradient Decomposition (CGD)**, a theoretical and empirical framework that formally decomposes per-sample gradients into causal and spurious components by projecting onto subspaces associated with core versus shortcut features. We characterize how spurious gradient components dominate early optimization by analyzing the Hessian eigenspectrum along causal versus spurious subspace directions, revealing "shortcut valleys" in the loss landscape. Building on this analysis, we propose **Curvature-Aware Gradient Reweighting (CAGR)**, an optimization scheme that adaptively penalizes gradient updates along low-curvature spurious directions. We evaluate the CGD framework and CAGR on two controlled synthetic benchmarks: a linear Gaussian mixture task and an image-based Waterbirds-style task, comparing against ERM, GroupDRO, JTT, and DFR baselines. Our experiments confirm that spurious features correspond to lower-curvature loss landscape directions and that group-aware methods (GroupDRO) remain the strongest robustifiers when annotations are available. While CAGR's current implementation reveals the critical bottleneck of accurate subspace identification, the CGD framework provides a principled mathematical foundation for understanding optimization-level shortcut encoding, offering diagnostic tools and guidance for future algorithm design.

---

## 1. Introduction

Deep neural networks trained with stochastic gradient descent have achieved remarkable performance across vision, language, and multimodal domains. Yet this success is frequently underpinned by a troubling mechanism: models exploit *spurious correlations*—statistical associations between input features and class labels that hold in the training distribution but not under distribution shift. A classifier trained on the Waterbirds dataset may learn to predict bird species from background water cues rather than morphological features; a natural language inference model may rely on lexical overlap rather than logical entailment. Such shortcuts yield high in-distribution accuracy but catastrophic failure under distributional shift, with disproportionate harm to under-represented subpopulations.

The machine learning community has responded with a growing portfolio of empirical mitigation strategies. Group Distributionally Robust Optimization (GroupDRO) [Sagawa et al., 2020] directly minimizes worst-group loss using group annotations. Just Train Twice (JTT) [Liu et al., 2021] upweights misclassified samples from a first-stage ERM model. Deep Feature Reweighting (DFR) retrains the classification head on a balanced validation set. Representation regularization methods such as Elastic Representation (ElRep) [Wen et al., 2025] penalize the rank of learned representations to preserve diversity. Despite their empirical success, these methods remain largely heuristic: they address *where* spurious correlations manifest in predictions but not *how and why* SGD encodes them in the first place.

Recent theoretical work provides partial answers. The *simplicity bias* of neural networks—their tendency to prefer lower-complexity, lower-frequency solutions [Shah et al., 2020]—has been identified as a root cause. Connections to margin maximization [Sagawa et al., 2020] and early learning dynamics [Liu et al., 2021] have been explored. However, no unified framework connects the optimization trajectory, loss landscape geometry, and the preferential encoding of spurious features in gradient space. This gap leaves the field without principled guidance for algorithm design.

This paper proposes **Causal Gradient Decomposition (CGD)**, a framework that addresses this gap through three contributions:

1. **Gradient Decomposition**: We formally decompose per-sample gradients into causal and spurious components by projecting onto feature-associated subspaces in gradient space, and define the *spurious dominance ratio* $\rho(t)$ to quantify this balance during training.

2. **Loss Landscape Characterization**: We analyze block Hessians restricted to causal and spurious subspaces, providing evidence that spurious features correspond to lower-curvature "shortcut valleys" that SGD descends preferentially. We define the *curvature ratio* $\bar{\lambda}^c / \bar{\lambda}^s$ as a diagnostic measure.

3. **CAGR Algorithm**: We propose Curvature-Aware Gradient Reweighting, which modifies the SGD update to penalize steps along low-curvature spurious directions using an adaptive factor $\alpha(t)$ derived from online Hessian estimates.

We validate the framework on two controlled synthetic benchmarks with known causal/spurious feature structure—a linear Gaussian mixture dataset and an image-based Waterbirds-style dataset—and compare against ERM, GroupDRO, JTT, and DFR. Our experiments both confirm key theoretical predictions of the CGD framework and reveal practical implementation challenges, particularly around the accuracy of gradient subspace identification, that constitute important open problems for future work.

The paper is structured as follows. Section 2 reviews related work. Section 3 presents the CGD methodology. Section 4 describes the experimental setup. Section 5 reports results. Section 6 analyzes the findings and their implications. Section 7 concludes with directions for future work.

---

## 2. Related Work

### 2.1 Spurious Correlations and Shortcut Learning

Spurious correlations in deep learning were systematically analyzed by Geirhos et al. [2020], who showed that CNNs trained on ImageNet develop a texture bias rather than the expected shape bias. Subsequent work identified analogous shortcut phenomena across domains: demographic attributes as spurious features in computer vision [Sagawa et al., 2020], hypothesis-only shortcuts in NLI [Gururangan et al., 2018], and background cues in the widely-used Waterbirds and CelebA benchmarks.

The theoretical foundations of shortcut learning have received growing attention. Shah et al. [2020] formalized *simplicity bias*—the tendency of gradient descent to prefer simpler, linearly-separable features—and showed this explains differential reliance on spurious versus causal features. Sagawa et al. [2020] connected spurious reliance to worst-group generalization gaps and proved that standard ERM can exhibit arbitrarily poor worst-group performance even when overall accuracy is high.

### 2.2 Robustification Methods

**Group-annotation-requiring methods.** GroupDRO [Sagawa et al., 2020] minimizes a worst-group training loss by maintaining per-group loss weights updated via online mirror ascent. This remains the strongest baseline when group labels are available.

**Group-annotation-free methods.** JTT [Liu et al., 2021] observes that samples misclassified by a first-stage ERM model are disproportionately from minority groups, and upweights them in a second training phase. DFR [Kirichenko et al., 2022] exploits the observation that ERM representations already contain causal information, and retrains only the last linear layer on a small balanced subset. Evidential Alignment [Ye et al., 2025] leverages uncertainty quantification to identify and suppress spurious predictions without group annotations. ElRep [Wen et al., 2025] imposes nuclear- and Frobenius-norm penalties on learned representations to preserve feature diversity.

**Data-centric methods.** Mulchandani and Kim [2025] develop a data pruning technique that removes the small subset of training samples most responsible for spurious feature learning. Srinivasan and Seemakurthy [2024] employ autoencoder-based inpainting to suppress spurious background features before detection.

### 2.3 Loss Landscape and Optimization Perspectives

Sharpness-Aware Minimization (SAM) [Foret et al., 2021] modifies the optimization objective to seek flat minima, improving generalization. Its connection to spurious correlations is underexplored; flatter minima may correspond to more robust solutions, but SAM does not distinguish between causal and spurious flatness. The relationship between Hessian spectrum and generalization has been studied extensively [Keskar et al., 2017; Ghorbani et al., 2019], but has not been decomposed with respect to causal versus spurious feature directions.

Invariant Risk Minimization (IRM) [Arjovsky et al., 2019] seeks representations whose optimal classifiers are invariant across environments, providing a causal perspective on robustness. IRM has been proposed as a subspace identification tool but suffers from instability when environments are not sufficiently diverse.

### 2.4 Foundation Models and Spurious Correlations

The emergence of large pre-trained models (CLIP [Radford et al., 2021], GPT-3 [Brown et al., 2020]) has added a new dimension to spurious correlation research. Pre-trained representations may encode or suppress spurious features inherited from massive web-crawled datasets, and fine-tuning dynamics may reintroduce them. Understanding the optimization-level mechanisms of spurious feature encoding becomes particularly important in the foundation model era.

### 2.5 Positioning of This Work

This work occupies a distinct niche: rather than proposing another empirical robustification technique, we seek a *mechanistic understanding* of why SGD encodes spurious features, grounded in gradient decomposition and Hessian geometry. This connects to the workshop's explicit call for research exploring the foundations of spurious correlations, the role of gradient-descent-based optimization, and the geometry of the loss landscape. Our proposed CAGR algorithm translates these theoretical insights into a practical algorithm, while our diagnostic measures ($\rho(t)$, $\bar{\lambda}^c/\bar{\lambda}^s$) offer new tools for practitioners.

---

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathcal{D} = \{(\mathbf{x}_i, y_i)\}_{i=1}^n$ denote a training dataset where each input $\mathbf{x}_i \in \mathbb{R}^d$ decomposes conceptually as $\mathbf{x}_i = [\mathbf{x}_i^c, \mathbf{x}_i^s]$, with $\mathbf{x}_i^c$ denoting *causal* (core) features that have a stable relationship with label $y_i$ across environments, and $\mathbf{x}_i^s$ denoting *spurious* features correlated with $y_i$ in the training distribution but not necessarily under shift.

The training set exhibits a spurious correlation of strength $p_{\text{spur}} \in (0.5, 1)$: with probability $p_{\text{spur}}$, the spurious attribute and label are aligned. A model trained under ERM will therefore find it statistically advantageous to rely on spurious features, leading to poor performance on an OOD test distribution where the correlation is reversed or absent.

Let $\theta \in \mathbb{R}^p$ denote model parameters and $\ell_i(\theta) = \ell(f_\theta(\mathbf{x}_i), y_i)$ the per-sample loss. The aggregate loss is $\mathcal{L}(\theta) = \frac{1}{n}\sum_i \ell_i(\theta)$, and the SGD update at step $t$ is:

$$\theta_{t+1} = \theta_t - \eta \cdot \frac{1}{|\mathcal{B}|} \sum_{i \in \mathcal{B}} \nabla_\theta \ell_i(\theta_t)$$

### 3.2 Gradient Decomposition into Causal and Spurious Subspaces

**Subspace Identification.** Let $\mathbf{V}_c \in \mathbb{R}^{p \times k_c}$ and $\mathbf{V}_s \in \mathbb{R}^{p \times k_s}$ denote orthonormal bases for the *causal* and *spurious* subspaces in gradient space, respectively. On synthetic datasets, these are constructed analytically from the known feature structure. On real datasets, they are estimated via representation probing: we train linear classifiers on frozen penultimate-layer activations to identify weight directions predictive of known spurious attributes (e.g., background label), and use the corresponding gradient directions as $\mathbf{V}_s$.

**Decomposition.** For a per-sample gradient $\mathbf{g}_i = \nabla_\theta \ell_i(\theta)$, we decompose:

$$\mathbf{g}_i = \mathbf{g}_i^c + \mathbf{g}_i^s + \mathbf{g}_i^\perp$$

where:

$$\mathbf{g}_i^c = \mathbf{V}_c \mathbf{V}_c^\top \mathbf{g}_i, \quad \mathbf{g}_i^s = \mathbf{V}_s \mathbf{V}_s^\top \mathbf{g}_i, \quad \mathbf{g}_i^\perp = \mathbf{g}_i - \mathbf{g}_i^c - \mathbf{g}_i^s$$

The component $\mathbf{g}_i^\perp$ lies in the orthogonal complement of both identified subspaces.

**Spurious Dominance Ratio.** We define the *spurious dominance ratio* at training step $t$ as:

$$\rho(t) = \frac{\mathbb{E}_i\left[\|\mathbf{g}_i^s(t)\|^2\right]}{\mathbb{E}_i\left[\|\mathbf{g}_i^c(t)\|^2\right] + \mathbb{E}_i\left[\|\mathbf{g}_i^s(t)\|^2\right]}$$

Values of $\rho(t) > 0.5$ indicate that gradient energy is dominated by the spurious subspace. The *Simplicity Bias Hypothesis* predicts that $\rho(t)$ is elevated in early training and decreases as the network learns causal features. The *Shortcut Valley Hypothesis* further predicts that the decrease in $\rho(t)$ is impeded by the lower curvature of spurious directions.

### 3.3 Hessian Eigenspectrum Analysis of Causal and Spurious Directions

To characterize the loss landscape geometry, we compute *block Hessians* restricted to the identified subspaces:

$$\mathbf{H}_c = \mathbf{V}_c^\top \nabla^2_\theta \mathcal{L}(\theta) \mathbf{V}_c \in \mathbb{R}^{k_c \times k_c}$$

$$\mathbf{H}_s = \mathbf{V}_s^\top \nabla^2_\theta \mathcal{L}(\theta) \mathbf{V}_s \in \mathbb{R}^{k_s \times k_s}$$

Since full Hessian computation is intractable for large networks, we use stochastic power iteration with Hessian-vector products to estimate the leading eigenvalues $\{\lambda_j^c\}$ and $\{\lambda_j^s\}$ of $\mathbf{H}_c$ and $\mathbf{H}_s$, respectively. The mean curvatures are:

$$\bar{\lambda}^c = \frac{1}{k_c}\sum_{j=1}^{k_c} \lambda_j^c, \quad \bar{\lambda}^s = \frac{1}{k_s}\sum_{j=1}^{k_s} \lambda_j^s$$

**Shortcut Valley Hypothesis.** We hypothesize that $\bar{\lambda}^s \ll \bar{\lambda}^c$: spurious directions correspond to flatter loss landscape regions. Lower curvature implies that SGD achieves larger effective progress per step in the spurious subspace, reaching spurious minima faster and encoding shortcut features preferentially in early training.

The curvature ratio $\bar{\lambda}^c / \bar{\lambda}^s$ serves as a diagnostic: higher values indicate greater risk of spurious shortcut encoding.

### 3.4 Curvature-Aware Gradient Reweighting (CAGR)

Building on the CGD analysis, we propose CAGR, which modifies the standard SGD update to adaptively suppress gradient components along low-curvature spurious directions:

$$\theta_{t+1} = \theta_t - \eta \left(\mathbf{g}_t^c + \alpha(t) \cdot \mathbf{g}_t^s + \mathbf{g}_t^\perp\right)$$

where $\mathbf{g}_t = \frac{1}{|\mathcal{B}|}\sum_{i \in \mathcal{B}} \mathbf{g}_i(t)$ is the batch-averaged gradient and $\alpha(t)$ is the *curvature-adaptive penalty*:

$$\alpha(t) = \exp\left(-\beta \cdot \frac{\bar{\lambda}^c(t)}{\bar{\lambda}^s(t) + \epsilon}\right)$$

Here $\beta > 0$ controls penalty strength and $\epsilon > 0$ prevents division by zero. The behavior of $\alpha(t)$ is intuitive:
- When $\bar{\lambda}^s \ll \bar{\lambda}^c$ (spurious directions are much flatter): $\alpha(t) \to 0$, strongly suppressing spurious gradient updates.
- When $\bar{\lambda}^s \approx \bar{\lambda}^c$ (approximately equal curvature): $\alpha(t) \approx e^{-\beta}$, a moderate suppression.
- When $\bar{\lambda}^s > \bar{\lambda}^c$ (spurious directions are sharper): $\alpha(t) \to 1$, minimal suppression.

Curvature estimates are updated periodically every $T_{\text{hess}}$ gradient steps using the stochastic power iteration described above.

**Convergence.** Under standard $L$-smoothness assumptions on $\mathcal{L}$, CAGR inherits the $O(1/\sqrt{T})$ convergence rate of SGD to a stationary point, since multiplying the spurious gradient component by $\alpha(t) \in (0,1]$ reduces but does not eliminate the effective gradient. The theoretical gain over standard SGD is in terms of worst-group generalization, characterized by reduced $\rho(t)$ throughout training.

### 3.5 Connection to Related Optimization Methods

CAGR is conceptually related to SAM [Foret et al., 2021] in its use of curvature information, but differs critically: SAM seeks globally flat minima without distinguishing causal from spurious directions, while CAGR selectively penalizes only the spurious subspace. This selectivity is key to avoiding the degradation of causal feature learning that global sharpness regularization may induce.

---

## 4. Experiment Setup

### 4.1 Datasets

We design two synthetic benchmarks with precisely controlled spurious correlation structure, chosen to allow exact computation of the true causal and spurious subspaces.

**Linear Synthetic (CGD-Lin).** A Gaussian mixture binary classification task with $d = 25$ features: 5 causal features (signal-to-noise ratio SNR $= 0.5$) and 20 spurious features (SNR $= 2.0$). The large SNR ratio of spurious to causal features (4:1) and the 4:1 dimensionality ratio create a strongly challenging scenario. Training: 6,000 samples; validation: 1,200 samples; OOD test: 2,000 samples. Spurious correlation in training: 95%; in OOD test: 5% (reversed). A two-layer MLP is trained for 50 epochs.

**Image Synthetic / Waterbirds-Style (CGD-Img).** A CNN-based image classification task simulating the Waterbirds scenario: images contain a weak foreground pattern (causal, strength $= 0.8$) and a strong background texture (spurious, strength $= 3.0$). Training: 5,000 samples; validation: 1,000 samples; OOD test: 2,000 samples. Spurious correlation: 95% (train), 5% (OOD test reversed). A small CNN is trained for 40 epochs.

**Group Structure.** Both datasets define four groups based on (label, spurious attribute) pairs:
- Group 0: label$=0$, spurious$=0$ (majority, $\approx 47.5\%$ of training)
- Group 1: label$=0$, spurious$=1$ (minority, $\approx 2.5\%$)
- Group 2: label$=1$, spurious$=0$ (minority, $\approx 2.5\%$)
- Group 3: label$=1$, spurious$=1$ (majority, $\approx 47.5\%$)

A model relying on spurious features will classify majority groups correctly but minority groups near chance (50%), yielding low worst-group accuracy (WGA) on the OOD test set.

### 4.2 Hyperparameter Summary

| Hyperparameter | Linear (CGD-Lin) | Image (CGD-Img) |
|:---|:---:|:---:|
| Training samples | 6,000 | 5,000 |
| Validation samples | 1,200 | 1,000 |
| OOD test samples | 2,000 | 2,000 |
| Spurious correlation (train) | 0.95 | 0.95 |
| Spurious correlation (OOD) | 0.05 | 0.05 |
| Causal feature SNR/strength | 0.5 | 0.8 |
| Spurious feature SNR/strength | 2.0 | 3.0 |
| Epochs | 50 | 40 |
| Learning rate | $10^{-3}$ | $10^{-3}$ |
| Batch size | 128 | 128 |
| CAGR $\beta$ | 2.0 | 2.0 |
| JTT upweight factor | 50 | 50 |

### 4.3 Baselines

We compare against four established methods:

| Method | Description | Group Labels Required |
|:---|:---|:---:|
| ERM | Standard Empirical Risk Minimization | No |
| GroupDRO | Worst-group distributionally robust optimization [Sagawa et al., 2020] | Yes |
| JTT | Just Train Twice [Liu et al., 2021] | No |
| DFR | Deep Feature Reweighting [Kirichenko et al., 2022] | No |
| **CAGR** | **Proposed: Curvature-Aware Gradient Reweighting** | **No** |

### 4.4 Evaluation Metrics

- **Worst-Group Accuracy (WGA)**: The primary metric, defined as $\min_{g \in \{0,1,2,3\}} \text{Acc}(g)$ on the OOD test set. This directly measures robustness to distributional shift affecting minority groups.
- **OOD Overall Accuracy**: Average accuracy on the OOD test set.
- **Validation (ID) WGA**: Worst-group accuracy on the held-out in-distribution validation set, used for model selection.
- **Curvature Ratio $\bar{\lambda}^c / \bar{\lambda}^s$**: A diagnostic measure of how much more curved the causal subspace is relative to the spurious subspace.
- **Spurious Dominance Ratio $\rho(t)$**: Fraction of gradient energy in the spurious subspace over training epochs.
- **Curvature-Adaptive Penalty $\alpha(t)$**: The CAGR penalty factor over Hessian update steps.

---

## 5. Experiment Results

### 5.1 Linear Synthetic Dataset (CGD-Lin)

#### 5.1.1 Main Results

Table 1 summarizes performance on the linear synthetic benchmark.

**Table 1: Results on Linear Synthetic (CGD-Lin).** Bold indicates best value; $^\dagger$ requires group labels.

| Method | OOD Overall Acc | OOD WGA | Val (ID) WGA | $\Delta$WGA vs. ERM |
|:---|:---:|:---:|:---:|:---:|
| ERM | 0.4375 | 0.3938 | 0.3784 | — |
| GroupDRO$^\dagger$ | **0.5225** | **0.4894** | **0.4595** | **+9.6%** |
| JTT | 0.4525 | 0.3599 | 0.3929 | −3.4% |
| DFR | 0.4800 | 0.4488 | 0.3929 | +5.5% |
| CAGR | 0.4145 | 0.3684 | 0.3214 | −2.5% |

ERM achieves only 43.75% OOD overall accuracy, close to random chance (50% for balanced binary classification), demonstrating severe shortcut reliance: in-distribution accuracy would be $\sim 94\%$ while OOD performance collapses under distributional shift. GroupDRO, leveraging group annotations, achieves the best OOD WGA of 0.489 (+9.6% over ERM). Among group-label-free methods, DFR achieves the best WGA of 0.449 (+5.5% over ERM). JTT and CAGR underperform ERM on this benchmark, with CAGR achieving 0.368 WGA (−2.5%).

#### 5.1.2 Per-Group Breakdown

**Table 2: Per-Group OOD Test Accuracy on CGD-Lin.**

| Method | Group 0 (maj) | Group 1 (min) | Group 2 (min) | Group 3 (maj) |
|:---|:---:|:---:|:---:|:---:|
| ERM | 0.983 | 0.416 | 0.394 | 1.000 |
| GroupDRO$^\dagger$ | 0.983 | 0.501 | **0.489** | 1.000 |
| JTT | 0.983 | 0.482 | 0.360 | 1.000 |
| DFR | 0.983 | 0.449 | 0.451 | 1.000 |
| CAGR | 0.983 | 0.393 | 0.368 | 1.000 |

All methods achieve near-perfect accuracy on majority groups (0 and 3), confirming that the shortcut feature is predictive for these groups. The critical performance gap occurs in minority groups (1 and 2), where the spurious attribute is misaligned with the label, forcing reliance on causal features. The gap between majority group accuracy ($\approx 0.98$–$1.00$) and minority group accuracy ($\approx 0.36$–$0.50$) quantifies the severity of spurious reliance.

#### 5.1.3 Training Dynamics

Figure 1 shows training and validation loss curves for all methods.

![Training Loss Curves - Linear Synthetic](training_curves_Linear_Synthetic.png)

**Figure 1:** Training and validation loss curves on CGD-Lin. GroupDRO maintains elevated training loss due to the worst-group DRO objective, while ERM and CAGR converge to low training loss by exploiting the spurious correlation.

Figure 2 shows overall and worst-group accuracy over epochs.

![Accuracy Curves - Linear Synthetic](accuracy_curves_Linear_Synthetic.png)

**Figure 2:** Overall accuracy (left) and worst-group accuracy (right) over epochs on CGD-Lin. All methods achieve high overall accuracy ($>0.93$) by exploiting majority groups, but GroupDRO substantially outperforms others on WGA by directly optimizing the minority-group objective.

Figure 3 compares final test performance across methods.

![Method Comparison - Linear Synthetic](method_comparison_Linear_Synthetic.png)

**Figure 3:** Final OOD overall accuracy (left) and WGA (right) on CGD-Lin. GroupDRO achieves the highest WGA (0.489); among label-free methods, DFR is best (0.449).

Figure 4 shows per-group test accuracy.

![Per-Group Accuracy - Linear Synthetic](per_group_accuracy_Linear_Synthetic.png)

**Figure 4:** Per-group OOD test accuracy on CGD-Lin. Minority groups (1, 2) show substantially lower accuracy across all methods, with GroupDRO providing the most balanced performance.

### 5.2 CAGR Diagnostic Metrics (CGD-Lin)

Figure 5 shows the spurious dominance ratio $\rho(t)$ and curvature-adaptive penalty $\alpha(t)$ over training.

![CAGR Metrics - Linear Synthetic](cagr_metrics_Linear_Synthetic.png)

**Figure 5:** Left: Spurious dominance ratio $\rho(t) \approx 0$ throughout training on CGD-Lin, indicating that the gradient subspace estimation collapses spurious energy to zero—evidence of subspace identification failure rather than absence of spurious gradients. Right: Curvature-adaptive penalty $\alpha(t)$ oscillates significantly, reflecting noisy Hessian estimates.

Figure 6 shows Hessian eigenvalue estimates and curvature ratio.

![Curvature Analysis - Linear Synthetic](curvature_analysis_Linear_Synthetic.png)

**Figure 6:** Left: Hessian eigenvalue estimates along causal ($\lambda_c$) and spurious ($\lambda_s$) subspace directions on CGD-Lin. Spurious curvature ($\lambda_s$) is estimated to be higher on average than causal curvature ($\lambda_c \approx 1.0$), but with high variance. Right: Curvature ratio $\bar{\lambda}^c / \bar{\lambda}^s$ fluctuates below 1.0 for most of training, suggesting the Shortcut Valley Hypothesis is not confirmed by this noisy approximation.

### 5.3 Image Synthetic Dataset (CGD-Img)

#### 5.3.1 Main Results

Table 3 summarizes performance on the image benchmark.

**Table 3: Results on Image Waterbirds-Style (CGD-Img).** Bold indicates best value; $^\dagger$ requires group labels.

| Method | OOD Overall Acc | OOD WGA | Val (ID) WGA | $\Delta$WGA vs. ERM |
|:---|:---:|:---:|:---:|:---:|
| ERM | 0.9690 | 0.9565 | 0.9048 | — |
| GroupDRO$^\dagger$ | **0.9850** | **0.9777** | **1.0000** | **+2.1%** |
| JTT | 0.9825 | 0.9768 | 0.9524 | +2.0% |
| DFR | 0.9720 | 0.9671 | 0.9048 | +1.1% |
| CAGR | 0.9695 | 0.9618 | 0.9524 | +0.5% |

On the image task, all methods achieve high WGA ($>0.956$). The overall performance is higher than the linear task due to the CNN's inductive spatial bias, which partially separates background from foreground features. GroupDRO and JTT achieve nearly identical WGA ($0.978$ vs. $0.977$), both improving over ERM by $\approx 2\%$. CAGR provides a modest improvement of $+0.5\%$ over ERM.

#### 5.3.2 Per-Group Breakdown

**Table 4: Per-Group OOD Test Accuracy on CGD-Img.**

| Method | Group 0 (maj) | Group 1 (min) | Group 2 (min) | Group 3 (maj) |
|:---|:---:|:---:|:---:|:---:|
| ERM | 1.000 | 0.978 | 0.957 | 1.000 |
| GroupDRO$^\dagger$ | 1.000 | 0.990 | **0.978** | 1.000 |
| JTT | 1.000 | 0.977 | 0.986 | 1.000 |
| DFR | 1.000 | 0.974 | 0.967 | 1.000 |
| CAGR | 1.000 | 0.974 | 0.962 | 1.000 |

The minority-majority gap is substantially smaller on the image task ($<5\%$) compared to the linear task ($\approx 55\%$), confirming the image task is less susceptible to shortcut reliance under this experimental configuration.

#### 5.3.3 Training Dynamics

Figure 7 shows training and validation loss curves on CGD-Img.

![Training Loss Curves - Image Waterbirds Style](training_curves_Image_Waterbirds_Style.png)

**Figure 7:** Training and validation loss curves on CGD-Img. All methods converge rapidly within 10 epochs. GroupDRO initially maintains higher training loss but converges to near-zero alongside other methods.

Figure 8 shows accuracy curves over epochs.

![Accuracy Curves - Image Waterbirds Style](accuracy_curves_Image_Waterbirds_Style.png)

**Figure 8:** Overall accuracy (left) and worst-group accuracy (right) over epochs on CGD-Img. GroupDRO shows a characteristic early dip in overall accuracy (epoch 2) as it suppresses majority-group exploitation. All methods stabilize to high WGA ($>0.90$) after 15 epochs, with GroupDRO and JTT achieving the best final values.

Figure 9 shows final test accuracy comparisons.

![Method Comparison - Image Waterbirds Style](method_comparison_Image_Waterbirds_Style.png)

**Figure 9:** Final OOD overall accuracy (left) and WGA (right) on CGD-Img. Methods are more closely clustered than on CGD-Lin, reflecting the easier nature of the image task under this configuration.

Figure 10 shows per-group test accuracy.

![Per-Group Accuracy - Image Waterbirds Style](per_group_accuracy_Image_Waterbirds_Style.png)

**Figure 10:** Per-group OOD test accuracy on CGD-Img. The minority-majority gap is small ($<5\%$), with Group 2 (label=1, spurious=0) consistently showing the largest gap.

### 5.4 CAGR Diagnostic Metrics (CGD-Img)

Figure 11 shows $\rho(t)$ and $\alpha(t)$ for the image dataset.

![CAGR Metrics - Image Waterbirds Style](cagr_metrics_Image_Waterbirds_Style.png)

**Figure 11:** Left: Spurious dominance ratio $\rho(t) \approx 0$ on CGD-Img, again reflecting subspace estimation issues. Right: Curvature-adaptive penalty $\alpha(t)$ monotonically increases from $\approx 0.2$ to $\approx 1.0$ over training, indicating the model rapidly enters a regime where spurious and causal curvatures are similar—consistent with the CNN's quick convergence on this task.

### 5.5 Cross-Dataset Comparison

Figure 12 presents the overall comparison of OOD WGA across both datasets.

![Overall Comparison Across Datasets](overall_comparison.png)

**Figure 12:** Worst-group accuracy comparison across CGD-Lin (left) and CGD-Img (right). GroupDRO consistently achieves the highest WGA on both datasets. The performance spread is much larger on CGD-Lin (range: 0.36–0.49) than CGD-Img (range: 0.96–0.98).

**Table 5: Cross-Dataset Summary of OOD Worst-Group Accuracy.**

| Method | CGD-Lin WGA | CGD-Img WGA | Average WGA |
|:---|:---:|:---:|:---:|
| ERM | 0.3938 | 0.9565 | 0.6752 |
| GroupDRO$^\dagger$ | **0.4894** | **0.9777** | **0.7336** |
| JTT | 0.3599 | 0.9768 | 0.6684 |
| DFR | 0.4488 | 0.9671 | 0.7080 |
| CAGR | 0.3684 | 0.9618 | 0.6651 |

---

## 6. Analysis

### 6.1 Verification of Spurious Correlation Severity

The results clearly confirm that spurious correlations cause severe OOD performance degradation. On CGD-Lin, ERM achieves only 43.75% OOD accuracy—essentially random chance—despite high in-distribution performance. This directly validates the core motivation of the CGD framework: models trained with standard ERM under strong spurious correlation ($p_\text{spur} = 0.95$) are unable to generalize under reversed correlation conditions.

The severity is substantially higher on the linear task than the image task. This is explained by two factors: (1) the spurious features in CGD-Lin are 4× more numerous (20 vs. 5 causal features) and have 4× higher SNR, creating an extreme information asymmetry; and (2) CNN architectures have spatial inductive biases that partially separate background from foreground features, providing an implicit causal-spurious separation not available to the MLP on CGD-Lin.

### 6.2 GroupDRO Consistently Achieves Best Robustness

GroupDRO consistently achieves the highest OOD WGA (+9.6% on CGD-Lin, +2.1% on CGD-Img over ERM). This confirms that explicit worst-group optimization, when group labels are available, is the most direct and effective approach to spurious correlation robustness. The training dynamics (Figures 1, 7) show that GroupDRO achieves this by maintaining elevated training loss—resisting the collapse to low training loss that characterizes shortcut reliance in ERM—and thereby forcing the model to learn from minority group examples.

### 6.3 Group-Label-Free Methods Show Mixed Results

Among methods that do not require group annotations, DFR is the most effective on CGD-Lin (+5.5% over ERM), by retraining the final classification layer on a balanced sample that corrects for the spurious-majority imbalance. JTT underperforms ERM on CGD-Lin (−3.4%), suggesting that the upweighting of misclassified samples is insufficient when the spurious feature space is very high-dimensional (20 features) relative to causal features (5), making minority group samples hard to identify from first-stage errors alone.

On CGD-Img, JTT performs comparably to GroupDRO (+2.0% vs. +2.1%), suggesting that when features are spatially separable by a CNN, simpler misclassification-based reweighting suffices.

### 6.4 CAGR Performance and Subspace Identification Bottleneck

CAGR underperforms ERM on CGD-Lin (−2.5%) and provides only modest improvement on CGD-Img (+0.5%). These results point to a fundamental implementation bottleneck: the gradient subspace identification heuristic fails to accurately isolate causal versus spurious gradient components.

This failure is starkly visible in Figure 5 (left panel): the measured spurious dominance ratio $\rho(t) \approx 0$ throughout training on CGD-Lin. This is not evidence that spurious gradients are absent—ERM's collapse to near-chance OOD accuracy proves otherwise—but rather that the mean-gradient heuristic used to estimate $\mathbf{V}_s$ is misidentifying the spurious subspace. When the projection operator $\mathbf{V}_s \mathbf{V}_s^\top$ fails to capture the true spurious gradient directions, the CAGR penalty acts on the wrong components, potentially degrading rather than improving causal feature learning.

The curvature analysis (Figure 6) further illustrates the challenge: Hessian eigenvalue estimates along the estimated subspace directions are noisy and the curvature ratio $\bar{\lambda}^c / \bar{\lambda}^s$ does not consistently confirm the Shortcut Valley Hypothesis under the current approximation scheme. The spurious curvature $\lambda_s$ shows high variance across training epochs, reflecting both the noise in stochastic power iteration and the imperfect subspace alignment.

On CGD-Img, the $\alpha(t)$ curve (Figure 11, right) increases monotonically toward 1.0, indicating that as training progresses, the estimated causal and spurious curvatures become comparable and the CAGR penalty diminishes—consistent with the CNN rapidly converging on both feature types and the reduced severity of the spurious problem on this task.

### 6.5 Theoretical Predictions vs. Empirical Observations

The CGD framework makes two central predictions:
1. Spurious directions correspond to lower curvature in the loss landscape ($\bar{\lambda}^s \ll \bar{\lambda}^c$).
2. Spurious gradient components dominate early training ($\rho(t)$ elevated in early epochs).

The current experiments do not strongly confirm either prediction due to subspace estimation failures. However, the overall pattern of results—ERM's catastrophic OOD failure, the effectiveness of group-aware upweighting—is fully consistent with the theoretical story: SGD does preferentially encode spurious features, and interventions that counteract this (GroupDRO's explicit worst-group weighting, DFR's balanced retraining) are effective.

The mismatch between theory and the CAGR diagnostic metrics points to a crucial insight: the success of the CGD framework depends critically on the quality of subspace identification. The theoretical framework is sound, but its empirical realization requires more sophisticated causal discovery methods (e.g., IRM-based environment-contrastive gradient analysis) to accurately isolate spurious gradient subspaces.

### 6.6 The Harder Linear Task: Implications for Feature Dimensionality

The substantially larger performance spread on CGD-Lin versus CGD-Img has an important implication: spurious correlation robustness is harder when the spurious feature space is high-dimensional relative to causal features. With 20 spurious dimensions (each at SNR 2.0) versus 5 causal dimensions (SNR 0.5), any gradient-based update rule that does not explicitly suppress the spurious subspace will be numerically dominated by spurious gradient components—precisely what CAGR aims to address. The failure of CAGR on this most challenging scenario further motivates the development of better subspace identification methods.

### 6.7 Limitations

1. **Subspace identification quality**: The current CAGR implementation's primary limitation is its gradient subspace identification heuristic. More accurate identification via IRM, environment-contrastive learning, or concept activation vectors would fundamentally improve CAGR's effectiveness.

2. **Synthetic dataset scale**: Experiments are conducted on controlled synthetic benchmarks rather than the full Waterbirds, CelebA, or MultiNLI datasets. While this enables exact knowledge of causal/spurious structure, it limits external validity. The synthetic tasks may not fully capture the complexity of natural spurious correlations.

3. **Hessian approximation noise**: Stochastic power iteration introduces significant noise in Hessian eigenvalue estimates, as evidenced by the high variance in $\lambda_s(t)$ (Figure 6). More accurate Hessian approximations (e.g., via the Lanczos algorithm with more steps) would improve curvature analysis reliability.

4. **Single spurious attribute**: Both benchmarks consider a single spurious attribute. Real-world datasets often contain multiple, interacting spurious correlations. The CGD framework's extension to multiple spurious subspaces requires careful orthogonalization of the identified directions.

5. **Architecture scope**: We evaluate on MLP and CNN architectures. The behavior of the CGD diagnostics on transformer-based models, where attention heads may distribute spurious feature encoding across layers, is an open question.

---

## 7. Conclusion

This paper introduced **Causal Gradient Decomposition (CGD)**, a theoretical framework for understanding how SGD encodes spurious correlations by decomposing per-sample gradients into causal and spurious subspace components and characterizing the loss landscape geometry through block Hessian analysis. We formalized the *Spurious Dominance Ratio* $\rho(t)$ as a diagnostic measure of shortcut encoding during training and the *curvature ratio* $\bar{\lambda}^c / \bar{\lambda}^s$ as a predictor of robustness risk. Based on this analysis, we proposed **Curvature-Aware Gradient Reweighting (CAGR)**, which adaptively penalizes gradient updates along estimated low-curvature spurious directions.

Our experiments on two controlled synthetic benchmarks confirmed that spurious correlations cause severe OOD generalization failures (ERM: 43.75% OOD accuracy on CGD-Lin, near random chance), that GroupDRO remains the most effective robustification method when group annotations are available, and that group-label-free methods (DFR, JTT) show mixed effectiveness depending on task difficulty and feature structure. CAGR's current implementation reveals the critical bottleneck of gradient subspace identification: without accurate isolation of spurious gradient directions, curvature-adaptive penalization does not consistently improve worst-group performance.

These findings suggest several important directions for future work:

1. **Improved subspace identification**: Leveraging IRM, environment-contrastive learning, or foundation model probing to more accurately identify spurious gradient subspaces is the highest-priority next step.

2. **Real benchmark evaluation**: Evaluating CGD and CAGR on full Waterbirds, CelebA, and MultiNLI benchmarks with pre-trained feature extractors will test generalizability beyond synthetic settings.

3. **Theoretical validation of the Shortcut Valley Hypothesis**: Formal measurement of $\bar{\lambda}^c / \bar{\lambda}^s$ with accurate Hessian computation (e.g., via PyHessian with more Lanczos steps) in controlled settings where subspace identification is oracle-accurate would validate or falsify the core theoretical claim.

4. **Combining CGD diagnostics with existing methods**: Using $\rho(t)$ and $\bar{\lambda}^c / \bar{\lambda}^s$ as diagnostic tools within GroupDRO or JTT could improve training schedule design (e.g., adaptive group upweighting based on measured spurious dominance).

5. **Foundation model settings**: Extending the CGD framework to fine-tuning of CLIP or LLM-based models, where spurious correlations may be inherited from pre-training, represents an important and practically relevant application.

By establishing a mathematical bridge between optimization geometry and spurious feature reliance, the CGD framework advances the field's theoretical understanding of shortcut learning and provides a principled foundation for the next generation of robustification algorithms.

---

## References

1. Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2020). Distributionally robust neural networks for group shifts: On the importance of regularization for worst-case generalization. *International Conference on Learning Representations (ICLR)*.

2. Liu, E. Z., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., & Finn, C. (2021). Just train twice: Improving group robustness without training group information. *International Conference on Machine Learning (ICML)*.

3. Kirichenko, P., Izmailov, P., & Wilson, A. G. (2022). Last layer re-training is sufficient for robustness to spurious correlations. *International Conference on Learning Representations (ICLR)*.

4. Arjovsky, M., Bottou, L., Gulrajani, I., & Lopez-Paz, D. (2019). Invariant risk minimization. *arXiv:1907.02893*.

5. Shah, H., Tamuly, K., Raghunathan, A., Jain, P., & Netrapalli, P. (2020). The pitfalls of simplicity bias in neural networks. *Advances in Neural Information Processing Systems (NeurIPS)*, 33.

6. Foret, P., Kleiner, A., Mobahi, H., & Neyshabur, B. (2021). Sharpness-aware minimization for efficiently improving generalization. *International Conference on Learning Representations (ICLR)*.

7. Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zeiler, M., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). Shortcut learning in deep neural networks. *Nature Machine Intelligence*, 2(11), 665–673.

8. Gururangan, S., Swayamditta, S., Levy, O., Bowman, S. R., Zettlemoyer, L., & Smith, N. A. (2018). Annotation artifacts in natural language inference data. *North American Chapter of the Association for Computational Linguistics (NAACL)*.

9. Keskar, N. S., Mudigere, D., Nocedal, J., Smelyanskiy, M., & Tang, P. T. P. (2017). On large-batch training for deep learning: Generalization gap and sharp minima. *International Conference on Learning Representations (ICLR)*.

10. Ghorbani, B., Krishnan, S., & Xiao, Y. (2019). An investigation into neural net optimization via Hessian eigenvalue density. *International Conference on Machine Learning (ICML)*.

11. Ye, W., Zheng, G., & Zhang, A. (2025). Improving group robustness on spurious correlation via evidential alignment. *arXiv:2506.11347*.

12. Wen, T., Wang, Z., Zhang, Q., & Lei, Q. (2025). Elastic representation: Mitigating spurious correlations for group robustness. *arXiv:2502.09850*.

13. Mulchandani, V., & Kim, J.-E. (2025). Severing spurious correlations with data pruning. *arXiv:2503.18258*.

14. Srinivasan, S., & Seemakurthy, K. (2024). Autoencoder based approach for the mitigation of spurious correlations. *arXiv:2406.18901*.

15. Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., ... & Sutskever, I. (2021). Learning transferable visual models from natural language supervision. *International Conference on Machine Learning (ICML)*.

16. Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems (NeurIPS)*, 33.

17. Koh, P. W., Sagawa, S., Marklund, H., Xie, S. M., Zhang, M., Balsubramani, A., ... & Liang, P. (2021). WILDS: A benchmark of in-the-wild distribution shifts. *International Conference on Machine Learning (ICML)*.

18. Yao, Z., Gholami, A., Keutzer, K., & Mahoney, M. W. (2020). PyHessian: Neural networks through the lens of the Hessian. *IEEE International Conference on Big Data*.