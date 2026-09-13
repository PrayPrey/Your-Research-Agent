# Research Proposal: Data-Efficient Calibration via Selective Self-Training under Distribution Shift

## 1. Title

**Calibration-Aware Selective Self-Training (CASST): A Framework for Data-Efficient Model Calibration under Distribution Shift**

---

## 2. Introduction

### Background

Machine learning (ML) algorithms are increasingly deployed in high-stakes domains such as healthcare diagnostics, autonomous transportation, financial services, and criminal justice. In these contexts, the trustworthiness of ML systems extends beyond mere prediction accuracy to encompass the reliability of uncertainty estimates. Miscalibration—where a model's expressed confidence fails to reflect its true probability of correctness—poses severe risks in safety-critical applications. For instance, an overconfident medical diagnostic system might lead clinicians to overlook alternative diagnoses, while an underconfident autonomous vehicle might hesitate dangerously at critical decision points.

The challenge of achieving well-calibrated predictions is substantially exacerbated by two pervasive constraints in real-world ML deployments. First, **statistical limitations** manifest through the scarcity of high-quality labeled data, particularly in specialized domains where expert annotation is expensive and time-consuming. Standard calibration techniques such as temperature scaling and histogram binning require substantial held-out validation data to estimate calibration parameters effectively—a luxury rarely available in data-constrained settings. Second, **distribution shift** occurs when the deployment environment differs systematically from training conditions, causing even well-calibrated source models to become severely miscalibrated on target distributions.

Recent advances in semi-supervised and self-supervised learning have demonstrated remarkable success in leveraging unlabeled data to improve prediction accuracy under data scarcity. However, these approaches predominantly optimize for accuracy metrics while neglecting—or even exacerbating—calibration quality. Self-training methods, which iteratively assign pseudo-labels to unlabeled samples based on model confidence, are particularly prone to confirmation bias: overconfident predictions generate confident pseudo-labels, which in turn reinforce overconfidence in subsequent training iterations. This creates a dangerous feedback loop that degrades calibration precisely when reliable uncertainty estimates are most critical.

### Research Objectives

This research proposes **Calibration-Aware Selective Self-Training (CASST)**, a novel framework that jointly optimizes for accuracy and calibration under limited labeled data and distribution shift. Our specific objectives are:

1. To develop a theoretically grounded pseudo-label selection criterion that considers both prediction confidence and expected impact on model calibration.
2. To design a calibration-regularized training procedure that maintains calibration quality throughout the self-training process.
3. To empirically validate the framework on realistic benchmarks involving natural distribution shifts in medical imaging and autonomous driving domains.
4. To establish theoretical guarantees on the calibration-accuracy trade-off under our proposed selection mechanism.

### Significance

This research addresses a critical gap at the intersection of data-efficient learning and trustworthy ML. By enabling reliable calibration under realistic resource constraints, CASST will facilitate safer deployment of ML systems in domains where overconfident predictions can lead to catastrophic outcomes. The framework directly addresses the workshop's central concerns regarding trade-offs between computational/statistical limitations and trustworthiness, providing both theoretical insights and practical algorithms for the ML community.

---

## 3. Methodology

### 3.1 Problem Formulation

Consider a classification task with input space $\mathcal{X}$ and label space $\mathcal{Y} = \{1, \ldots, K\}$. We have access to a small labeled source dataset $\mathcal{D}_s = \{(x_i^s, y_i^s)\}_{i=1}^{n_s}$ drawn from source distribution $P_s(X, Y)$, and a larger unlabeled target dataset $\mathcal{D}_t = \{x_j^t\}_{j=1}^{n_t}$ drawn from target distribution $P_t(X)$, where typically $n_t \gg n_s$. The target distribution exhibits covariate shift: $P_t(X) \neq P_s(X)$ while $P_t(Y|X) = P_s(Y|X)$.

A model $f_\theta: \mathcal{X} \rightarrow \Delta^{K-1}$ maps inputs to probability simplices. Let $\hat{p}(x) = \max_k f_\theta(x)_k$ denote the predicted confidence and $\hat{y}(x) = \arg\max_k f_\theta(x)_k$ denote the predicted class. Perfect calibration requires:

$$P(\hat{y}(X) = Y \mid \hat{p}(X) = p) = p, \quad \forall p \in [0, 1]$$

We measure calibration quality using the Expected Calibration Error (ECE):

$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{n} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

where $B_m$ denotes the set of samples whose confidence falls into the $m$-th bin, $\text{acc}(B_m)$ is the accuracy within the bin, and $\text{conf}(B_m)$ is the average confidence.

### 3.2 CASST Framework Overview

The CASST framework consists of four integrated components:

**Phase 1: Calibration-Aware Initialization**
**Phase 2: Uncertainty-Guided Pseudo-Label Generation**
**Phase 3: Calibration-Impact-Based Sample Selection**
**Phase 4: Calibration-Regularized Iterative Refinement**

### 3.3 Phase 1: Calibration-Aware Initialization

We initialize the model on the limited labeled source data using focal loss to mitigate initial overconfidence:

$$\mathcal{L}_{\text{focal}}(x, y) = -\alpha_y (1 - f_\theta(x)_y)^\gamma \log f_\theta(x)_y$$

where $\gamma \geq 0$ is the focusing parameter that down-weights well-classified examples, and $\alpha_y$ provides class balancing. We set $\gamma = 2$ based on prior work. Additionally, we incorporate label smoothing with parameter $\epsilon = 0.1$:

$$y_{\text{smooth},k} = (1 - \epsilon) \cdot \mathbb{1}[k = y] + \frac{\epsilon}{K}$$

### 3.4 Phase 2: Uncertainty-Guided Pseudo-Label Generation

For each unlabeled target sample $x^t$, we compute two uncertainty measures:

**Predictive Confidence** using Monte Carlo (MC) Dropout with $T$ forward passes:

$$\bar{p}(x^t) = \frac{1}{T} \sum_{i=1}^{T} f_{\theta_i}(x^t)$$

$$\hat{p}(x^t) = \max_k \bar{p}(x^t)_k$$

**Calibration Uncertainty** measured via prediction disagreement:

$$u_{\text{cal}}(x^t) = \frac{1}{T} \sum_{i=1}^{T} \mathbb{1}\left[\arg\max_k f_{\theta_i}(x^t)_k \neq \hat{y}(x^t)\right]$$

This captures epistemic uncertainty relevant to calibration—high disagreement indicates samples where the model is unreliably confident.

### 3.5 Phase 3: Calibration-Impact-Based Sample Selection

The key innovation of CASST is selecting pseudo-labels based on their expected impact on calibration. For each candidate pseudo-labeled sample $(x^t, \hat{y}(x^t))$, we estimate the local calibration impact:

**Definition (Local Calibration Impact):** For sample $x^t$ with predicted confidence $\hat{p}(x^t)$ falling into bin $B_m$, the calibration impact score is:

$$\text{CI}(x^t) = \left| \hat{p}(x^t) - \widetilde{\text{acc}}_m \right| \cdot (1 - u_{\text{cal}}(x^t))$$

where $\widetilde{\text{acc}}_m$ is the estimated accuracy in bin $B_m$ computed using the labeled source data and previously selected pseudo-labeled samples.

Samples with high $\text{CI}$ scores have confidence levels inconsistent with their bin's empirical accuracy and low calibration uncertainty, making them valuable for calibration refinement. We select samples using a joint criterion:

$$\mathcal{S} = \left\{ x^t : \hat{p}(x^t) \geq \tau_p \text{ AND } u_{\text{cal}}(x^t) \leq \tau_u \text{ AND } \text{CI}(x^t) \geq \tau_c \right\}$$

The thresholds $\tau_p$, $\tau_u$, and $\tau_c$ are adapted dynamically using curriculum learning principles, starting with stringent values and relaxing them as training progresses:

$$\tau_p^{(t)} = \tau_p^{(0)} - \beta_p \cdot t, \quad \tau_u^{(t)} = \tau_u^{(0)} + \beta_u \cdot t, \quad \tau_c^{(t)} = \tau_c^{(0)} - \beta_c \cdot t$$

### 3.6 Phase 4: Calibration-Regularized Iterative Refinement

We train the model using a composite loss that balances accuracy and calibration:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{CE}} + \lambda_{\text{focal}} \mathcal{L}_{\text{focal}} + \lambda_{\text{MDCA}} \mathcal{L}_{\text{MDCA}} + \lambda_{\text{cons}} \mathcal{L}_{\text{cons}}$$

**Cross-Entropy Loss** on selected pseudo-labels:

$$\mathcal{L}_{\text{CE}} = -\frac{1}{|\mathcal{S}|} \sum_{x^t \in \mathcal{S}} \log f_\theta(x^t)_{\hat{y}(x^t)}$$

**Multi-class Difference in Confidence and Accuracy (MDCA)** regularizer:

$$\mathcal{L}_{\text{MDCA}} = \left| \frac{1}{|\mathcal{B}|} \sum_{x \in \mathcal{B}} \hat{p}(x) - \frac{1}{|\mathcal{B}|} \sum_{x \in \mathcal{B}} \mathbb{1}[\hat{y}(x) = y] \right|$$

**Consistency Regularization** to enforce prediction stability:

$$\mathcal{L}_{\text{cons}} = \frac{1}{|\mathcal{D}_t|} \sum_{x^t \in \mathcal{D}_t} \text{KL}\left( f_\theta(x^t) \| f_{\theta'}(x^t) \right)$$

where $\theta'$ is an exponential moving average of parameters.

### 3.7 Theoretical Analysis

**Theorem 1 (Calibration Preservation):** Under mild assumptions on the pseudo-label selection criterion, CASST maintains calibration error within a bounded increase per iteration:

$$\text{ECE}^{(t+1)} \leq \text{ECE}^{(t)} + \frac{\epsilon_{\text{sel}}}{|\mathcal{S}^{(t)}|} + O\left(\frac{1}{\sqrt{n_s + |\mathcal{S}^{(t)}|}}\right)$$

where $\epsilon_{\text{sel}}$ depends on the selection threshold stringency.

### 3.8 Experimental Design

**Datasets:**
1. **Medical Imaging:** Camelyon17 (pathology), with distribution shift across hospitals
2. **Autonomous Driving:** BDD100K → Cityscapes domain adaptation
3. **Natural Images:** DomainNet with controlled severity shifts

**Baselines:**
- Standard self-training (FixMatch, FlexMatch)
- Calibration methods (Temperature Scaling, Histogram Binning, ACE)
- Domain adaptation methods (TENT, CAFe)
- Combined approaches (FlexDA, anchored confidence methods)

**Data Efficiency Protocol:**
We evaluate under 1%, 5%, and 10% labeled data settings, simulating realistic resource constraints.

**Evaluation Metrics:**
- **Accuracy:** Top-1 classification accuracy
- **ECE:** Expected Calibration Error (15 bins)
- **MCE:** Maximum Calibration Error
- **Brier Score:** Combined accuracy-calibration measure
- **Reliability Diagrams:** Visual calibration assessment

**Ablation Studies:**
1. Impact of each selection criterion component
2. Sensitivity to threshold adaptation schedules
3. Effect of MC Dropout samples $T$
4. Contribution of calibration regularization terms

---

## 4. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following empirical outcomes:

1. **Improved Calibration Under Data Scarcity:** CASST will achieve 30-50% relative reduction in ECE compared to standard self-training methods when using only 5-10% of labeled data.

2. **Maintained Accuracy:** The calibration improvements will come with minimal accuracy trade-off (within 1-2% of accuracy-optimized baselines), demonstrating that the objectives are not fundamentally conflicting under our framework.

3. **Robustness to Distribution Shift:** Under natural distribution shifts (e.g., hospital-to-hospital in medical imaging), CASST will maintain calibration quality within 20% of source-domain levels, compared to 50-100% degradation in baseline methods.

4. **Theoretical Validation:** Empirical results will confirm our theoretical bounds on calibration preservation through self-training iterations.

### Broader Impact

**Scientific Contributions:**
- Novel theoretical framework connecting pseudo-label selection to calibration preservation
- Practical algorithm enabling trustworthy ML deployment under realistic constraints
- Comprehensive empirical analysis establishing benchmark results for calibration under data scarcity

**Practical Applications:**
- **Healthcare:** Enable reliable AI-assisted diagnosis with limited annotated medical images
- **Autonomous Systems:** Improve safety-critical uncertainty quantification in resource-constrained edge deployments
- **Democratization of Trustworthy ML:** Reduce data requirements for achieving calibrated models, enabling smaller organizations to deploy reliable ML systems

**Addressing Workshop Themes:**
This research directly addresses the workshop's core questions regarding how limited data affects ML trustworthiness and whether new algorithmic techniques can mitigate these problems. CASST demonstrates that careful integration of self-supervised learning principles with calibration-aware objectives can substantially reduce the data requirements for achieving trustworthy predictions, providing a template for addressing the calibration-efficiency trade-off in resource-constrained settings.

---

## References

Key references include works on adaptive calibrator ensembles (Zou et al., 2023), flexible distribution alignment (Aimar et al., 2023), anchored confidence for self-training (Joo & Klabjan, 2024), and covariance-aware feature alignment (2023), which collectively inform our approach to data-efficient calibration under distribution shift.