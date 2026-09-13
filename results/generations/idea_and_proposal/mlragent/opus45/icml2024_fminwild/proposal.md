# Research Proposal: Adaptive Confidence Calibration for Foundation Models Under Distribution Shift

## 1. Introduction

### Background

Foundation models (FMs) have emerged as transformative tools across diverse domains, from natural language processing to computer vision, healthcare diagnostics, and financial decision-making. These large-scale models, trained on vast datasets, exhibit remarkable capabilities in capturing comprehensive knowledge that can be transferred to downstream tasks. However, their deployment "in the wild" presents critical challenges that threaten their reliability and trustworthiness in real-world applications.

A fundamental issue with deployed foundation models is their tendency to produce overconfident predictions when encountering inputs that deviate from their training distribution—a phenomenon known as distribution shift. In high-stakes domains such as clinical diagnosis, autonomous driving, or financial risk assessment, such miscalibrated confidence can lead to catastrophic consequences. For instance, a medical AI system that confidently misdiagnoses a rare condition or a financial model that fails to signal uncertainty during market anomalies could result in significant harm.

Recent research has revealed nuanced calibration behaviors in foundation models. Hekler et al. (2025) demonstrated that foundation models exhibit complex calibration patterns—being underconfident on in-distribution data while showing improved calibration under distribution shifts. This finding challenges conventional assumptions about model calibration and highlights the need for adaptive approaches that can dynamically adjust confidence estimates based on the nature of incoming data.

Existing calibration methods, such as temperature scaling and Platt scaling, assume static test distributions and fail to adapt when data characteristics shift dynamically. While recent works like the Adaptive Calibrator Ensemble (ACE) by Zou et al. (2023) have begun addressing out-of-distribution calibration, they rely on discrete categorizations of distribution shift rather than continuous, real-time adaptation. Similarly, conformal prediction methods adapted for subpopulation shifts (Wang et al., 2025) require assumptions about coverage guarantees that may not hold in truly novel scenarios.

### Research Objectives

This research proposes the development of a **Dynamic Calibration Network (DCN)**, a novel framework designed to adaptively calibrate foundation model predictions in real-time based on detected distribution characteristics. The primary objectives are:

1. **Design and implement a lightweight shift detection module** capable of characterizing the degree and type of distribution shift between incoming data and the training manifold.

2. **Develop a meta-learned calibration adjustment mechanism** that dynamically modifies confidence scores conditioned on detected shift characteristics.

3. **Create an uncertainty decomposition framework** that separates aleatoric and epistemic uncertainty components to provide actionable confidence signals for human-AI collaboration.

4. **Validate the approach** across multiple foundation model architectures and diverse distribution shift scenarios, demonstrating improved calibration with minimal computational overhead.

### Significance

This research addresses the fundamental question of how foundation models can reliably communicate uncertainty when facing novel, out-of-distribution scenarios. The significance extends across multiple dimensions:

- **Trustworthy AI Deployment**: Enabling foundation models to provide reliable "I don't know" signals is essential for safe deployment in critical applications.
- **Human-AI Collaboration**: Well-calibrated uncertainty enables effective deferral mechanisms, allowing systems to escalate decisions to human experts when appropriate.
- **Resource Efficiency**: Unlike ensemble-based uncertainty methods, DCN aims to achieve robust calibration with minimal computational overhead, making it practical for real-time applications.
- **Generalization**: The meta-learning approach enables generalization to unseen distribution shifts, addressing a key limitation of existing methods.

## 2. Methodology

### 2.1 Overall Framework Architecture

The Dynamic Calibration Network consists of three interconnected modules that operate in conjunction with a frozen foundation model $f_\theta$. Given an input $x$, the foundation model produces logits $z = f_\theta(x)$, which are then processed through DCN to produce calibrated probabilities $\hat{p}$.

### 2.2 Shift Detection Module

The shift detection module learns to characterize distribution shift through a learned embedding space. Let $\mathcal{D}_{train}$ denote the training distribution and $x$ denote an incoming test sample.

**Distribution Embedding Network**: We employ a lightweight encoder $g_\phi: \mathcal{X} \rightarrow \mathbb{R}^d$ that maps inputs to a $d$-dimensional embedding space. This encoder is trained to capture distribution-relevant features while remaining computationally efficient.

**Reference Distribution Representation**: During training, we compute a set of reference statistics from $\mathcal{D}_{train}$:
$$\mu_{ref} = \mathbb{E}_{x \sim \mathcal{D}_{train}}[g_\phi(x)], \quad \Sigma_{ref} = \text{Cov}_{x \sim \mathcal{D}_{train}}[g_\phi(x)]$$

**Shift Characterization Vector**: For an incoming sample $x$, we compute a shift characterization vector $s(x) \in \mathbb{R}^{k}$ that captures multiple aspects of distribution deviation:

$$s(x) = \left[ d_M(x), \; d_{cos}(x), \; \sigma_{local}(x), \; h_{entropy}(x) \right]$$

where:
- $d_M(x) = \sqrt{(g_\phi(x) - \mu_{ref})^T \Sigma_{ref}^{-1} (g_\phi(x) - \mu_{ref})}$ is the Mahalanobis distance
- $d_{cos}(x) = 1 - \frac{g_\phi(x) \cdot \mu_{ref}}{\|g_\phi(x)\| \|\mu_{ref}\|}$ is the cosine distance
- $\sigma_{local}(x)$ captures local density estimation using k-nearest neighbors in the embedding space
- $h_{entropy}(x) = -\sum_i p_i(x) \log p_i(x)$ is the predictive entropy from the foundation model

### 2.3 Calibration Adjustment Layer

The calibration adjustment layer implements a meta-learned temperature scaling function conditioned on the shift characterization vector.

**Conditional Temperature Function**: Rather than using a fixed temperature parameter, we learn a function $T_\psi: \mathbb{R}^k \times \mathbb{R}^c \rightarrow \mathbb{R}^+$ that outputs a calibration temperature conditioned on both the shift vector and the original logits:

$$T(x) = T_\psi(s(x), z) = \text{softplus}\left(W_2 \cdot \text{ReLU}(W_1 \cdot [s(x); \bar{z}] + b_1) + b_2\right) + \epsilon$$

where $\bar{z}$ represents summary statistics of the logit vector (max, mean, std), and $\epsilon > 0$ ensures numerical stability.

**Calibrated Probability Computation**: The calibrated probabilities are computed as:

$$\hat{p}_i(x) = \frac{\exp(z_i / T(x))}{\sum_j \exp(z_j / T(x))}$$

**Meta-Learning Training Procedure**: We employ a meta-learning approach inspired by MAML to train the calibration parameters across diverse distribution shifts:

1. Sample a batch of shift scenarios $\{\mathcal{S}_1, \mathcal{S}_2, ..., \mathcal{S}_n\}$
2. For each scenario $\mathcal{S}_i$, compute the inner loss on calibration data
3. Update parameters using the outer loss aggregated across scenarios

The training objective minimizes the Expected Calibration Error (ECE) plus a regularization term:

$$\mathcal{L} = \sum_{i=1}^{n} \text{ECE}(\mathcal{S}_i; \psi, \phi) + \lambda \|\psi\|_2^2$$

### 2.4 Uncertainty Decomposition Module

To provide actionable uncertainty signals, we decompose total uncertainty into aleatoric and epistemic components.

**Aleatoric Uncertainty Estimation**: Aleatoric uncertainty is estimated directly from the calibrated predictive distribution:

$$U_{alea}(x) = -\sum_i \hat{p}_i(x) \log \hat{p}_i(x)$$

**Epistemic Uncertainty Estimation**: We estimate epistemic uncertainty using a lightweight approach based on gradient-based sensitivity analysis:

$$U_{epis}(x) = \left\| \nabla_x \log \hat{p}_{y^*}(x) \right\|_2 \cdot d_M(x)$$

where $y^* = \arg\max_i \hat{p}_i(x)$. This formulation captures model uncertainty through the interaction of prediction sensitivity and distributional novelty.

**Deferral Decision Function**: We define a deferral score that combines both uncertainty types:

$$D(x) = \alpha \cdot U_{alea}(x) + (1-\alpha) \cdot U_{epis}(x)$$

where $\alpha$ is learned or set based on domain requirements. When $D(x) > \tau$, the system recommends deferral to human experts.

### 2.5 Experimental Design

**Datasets and Foundation Models**: We will evaluate DCN across multiple settings:

- **Vision**: CLIP and DINOv2 on ImageNet variants (ImageNet-C, ImageNet-R, ImageNet-Sketch, ImageNet-A)
- **Language**: BERT-large and LLaMA-7B on sentiment analysis (SST-2 → Amazon Reviews) and NLI tasks with domain shifts
- **Medical Imaging**: Med-CLIP on chest X-ray datasets (CheXpert → MIMIC-CXR → external hospital data)

**Distribution Shift Scenarios**: We construct a comprehensive evaluation covering:
1. Synthetic corruptions (15 types, 5 severity levels)
2. Natural domain shifts (style, context, demographics)
3. Subpopulation shifts (class imbalance variations)
4. Temporal shifts (data from different time periods)

**Baselines**: We compare against:
- Temperature Scaling (Guo et al., 2017)
- Focal Loss Calibration
- Monte Carlo Dropout
- Deep Ensembles (computational upper bound)
- ACE (Zou et al., 2023)
- Conformal Prediction methods

**Evaluation Metrics**:

1. **Expected Calibration Error (ECE)**:
$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{n} |\text{acc}(B_m) - \text{conf}(B_m)|$$

2. **Maximum Calibration Error (MCE)**
3. **Brier Score**: $\text{BS} = \frac{1}{n}\sum_{i=1}^{n}(\hat{p}_i - y_i)^2$
4. **Area Under the Risk-Coverage Curve (AURC)** for selective prediction
5. **Deferral Efficiency**: Accuracy improvement per percentage of deferred samples
6. **Computational Overhead**: FLOPs and latency increase relative to base model

**Ablation Studies**: We will systematically evaluate:
- Contribution of each shift characterization component
- Impact of meta-learning versus standard training
- Sensitivity to reference distribution size
- Generalization to entirely unseen shift types

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Improvements**: Based on preliminary analysis and related work performance gaps, we anticipate:
- 30-50% reduction in ECE under moderate to severe distribution shifts compared to static calibration methods
- Comparable or improved in-distribution calibration (addressing the underconfidence issue identified by Hekler et al.)
- Less than 5% computational overhead relative to base model inference
- 15-25% improvement in AURC for selective prediction tasks

**Qualitative Contributions**:
- A unified framework for real-time adaptive calibration applicable across modalities
- Novel shift characterization methodology combining multiple complementary measures
- Principled uncertainty decomposition enabling interpretable deferral decisions
- Comprehensive benchmark for evaluating calibration under diverse distribution shifts

### Broader Impact

**Trustworthy AI Systems**: DCN directly addresses the reliability challenges identified by the FM in the Wild workshop. By providing well-calibrated confidence estimates, the framework enables foundation models to effectively communicate their limitations, a prerequisite for trustworthy deployment.

**Clinical and Safety-Critical Applications**: In healthcare settings, properly calibrated uncertainty allows AI systems to flag cases requiring expert review, potentially preventing misdiagnosis while maintaining efficiency for routine cases. The uncertainty decomposition specifically enables clinicians to understand whether uncertainty stems from inherent case ambiguity or model limitations.

**Efficient Deployment**: Unlike ensemble methods that multiply computational costs, DCN achieves robust calibration with minimal overhead, making it practical for resource-constrained deployments and real-time applications.

**Foundation for Future Research**: The shift detection module and meta-learning framework provide building blocks for broader adaptation and reliability research, potentially extending to continual learning and active data collection scenarios.

### Limitations and Future Directions

We acknowledge potential limitations including: (1) dependence on the quality of reference distribution statistics, (2) challenges in extremely low-data regimes, and (3) the need for careful hyperparameter selection for the deferral threshold. Future work will explore online updating of reference statistics, integration with retrieval-augmented approaches, and extension to multi-modal foundation models.

In conclusion, this research addresses a critical gap in foundation model deployment by developing adaptive calibration mechanisms that respond to dynamic distribution shifts. The proposed DCN framework offers a principled, efficient, and generalizable solution for enhancing the reliability of foundation models in real-world applications.