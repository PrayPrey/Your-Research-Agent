# Research Proposal: Uncertainty-Aware Self-Training for Label-Efficient Medical Image Segmentation

## 1. Introduction

### Background

Medical imaging has become indispensable in modern healthcare, enabling non-invasive diagnosis, treatment planning, and disease monitoring across virtually all clinical specialties. The interpretation of medical images—including MRI, CT, X-ray, and ultrasound—demands exceptional precision, as even subtle misinterpretations can lead to delayed diagnoses, inappropriate treatments, or missed pathologies. However, the exponential growth in imaging volume, coupled with increasingly complex multi-modal acquisitions, has created an unsustainable burden on radiologists and clinical specialists. This reality has catalyzed significant interest in machine learning approaches for automated medical image analysis.

Deep learning methods, particularly convolutional neural networks, have achieved remarkable success in medical image segmentation tasks. However, these methods typically require large amounts of pixel-level annotated data for training—a requirement that presents formidable challenges in the medical domain. Unlike natural images that can be annotated by crowdsourcing, medical image annotation demands expert knowledge, often requiring board-certified radiologists or subspecialists. Annotating a single volumetric medical scan can require several hours, making large-scale annotation prohibitively expensive and time-consuming.

Semi-supervised learning has emerged as a promising paradigm to address this annotation bottleneck by leveraging abundant unlabeled data alongside limited labeled examples. Self-training, a classical semi-supervised approach, iteratively generates pseudo-labels for unlabeled data and incorporates them into training. While effective in natural image domains, naive self-training in medical imaging faces critical challenges: the high cost of errors means that incorrectly propagated pseudo-labels can reinforce dangerous mistakes, potentially leading to clinically unacceptable outcomes. Current methods lack principled mechanisms to quantify prediction reliability and utilize this information strategically during training.

### Research Objectives

This research proposes an uncertainty-aware self-training framework that addresses the fundamental challenge of reliable pseudo-label utilization in label-efficient medical image segmentation. Our specific objectives are:

1. To develop a principled uncertainty estimation mechanism based on Monte Carlo (MC) dropout that quantifies epistemic uncertainty at the pixel level during pseudo-label generation.

2. To design an adaptive selective pseudo-labeling strategy that generates training signals only for image regions with sufficiently low uncertainty, preventing error propagation from unreliable predictions.

3. To formulate an uncertainty-weighted loss function that modulates the contribution of each pseudo-labeled pixel based on prediction confidence, enabling nuanced learning from partially reliable pseudo-labels.

4. To implement a curriculum-based training strategy that progressively expands the pseudo-labeled set as model confidence improves, maximizing utilization of unlabeled data throughout training.

### Significance

This research addresses critical challenges at the intersection of machine learning and medical imaging. By enabling effective learning with minimal annotation, our framework could dramatically reduce the cost and time required to develop clinical segmentation tools. The uncertainty quantification component provides clinicians with interpretable confidence maps, supporting informed decision-making in clinical workflows. Furthermore, the principled integration of uncertainty into self-training establishes a methodological foundation applicable across diverse medical imaging tasks and modalities.

## 2. Methodology

### 2.1 Problem Formulation

Consider a medical image segmentation task with a small labeled dataset $\mathcal{D}_L = \{(x_i, y_i)\}_{i=1}^{N_L}$ and a large unlabeled dataset $\mathcal{D}_U = \{x_j\}_{j=1}^{N_U}$, where $N_U \gg N_L$. Each image $x \in \mathbb{R}^{H \times W \times C}$ has spatial dimensions $H \times W$ and $C$ channels, and ground truth segmentation masks $y \in \{0, 1, ..., K-1\}^{H \times W}$ define pixel-wise class labels for $K$ classes.

Our goal is to train a segmentation network $f_\theta: \mathbb{R}^{H \times W \times C} \rightarrow [0,1]^{H \times W \times K}$ that achieves performance comparable to fully-supervised training using only 5-10% labeled data.

### 2.2 Uncertainty Estimation via Monte Carlo Dropout

We employ MC dropout to estimate epistemic uncertainty, which captures model uncertainty arising from limited training data. During inference, we perform $T$ stochastic forward passes with dropout enabled, generating a distribution of predictions:

$$\hat{p}^{(t)}(x) = f_\theta(x; \text{dropout}^{(t)}), \quad t = 1, ..., T$$

The mean prediction aggregates these samples:

$$\bar{p}(x) = \frac{1}{T} \sum_{t=1}^{T} \hat{p}^{(t)}(x)$$

We quantify pixel-wise uncertainty using predictive entropy:

$$\mathcal{U}(x)_{h,w} = -\sum_{k=1}^{K} \bar{p}(x)_{h,w,k} \log \bar{p}(x)_{h,w,k}$$

This formulation captures both aleatoric uncertainty (inherent data noise) and epistemic uncertainty (model uncertainty). High entropy indicates regions where the model is uncertain, often corresponding to ambiguous boundaries, novel patterns, or underrepresented anatomical structures.

### 2.3 Adaptive Selective Pseudo-Labeling

Rather than using all pseudo-labels indiscriminately, we employ an adaptive thresholding mechanism that selects only reliable predictions. For each unlabeled image $x_j$, we generate a pseudo-label mask:

$$\tilde{y}_j = \arg\max_k \bar{p}(x_j)_{:,:,k}$$

We compute an adaptive uncertainty threshold $\tau^{(e)}$ at epoch $e$ based on the distribution of uncertainties across the unlabeled set:

$$\tau^{(e)} = \text{Percentile}_{\alpha^{(e)}}\left(\{\mathcal{U}(x_j)_{h,w} : x_j \in \mathcal{D}_U, \forall h,w\}\right)$$

where $\alpha^{(e)}$ is a curriculum-controlled percentile parameter. A binary selection mask identifies reliable pixels:

$$M_j^{(e)}(h,w) = \mathbb{1}\left[\mathcal{U}(x_j)_{h,w} < \tau^{(e)}\right]$$

### 2.4 Uncertainty-Weighted Loss Function

For pixels that pass the selection threshold, we further modulate their contribution using uncertainty-based weights. The weight for each selected pixel is computed as:

$$w_j(h,w) = \exp\left(-\lambda \cdot \mathcal{U}(x_j)_{h,w}\right) \cdot M_j^{(e)}(h,w)$$

where $\lambda$ is a temperature parameter controlling weight sensitivity to uncertainty. The total training loss combines supervised and unsupervised components:

$$\mathcal{L}_{total} = \mathcal{L}_{sup} + \mu^{(e)} \cdot \mathcal{L}_{unsup}$$

The supervised loss uses standard cross-entropy with Dice loss:

$$\mathcal{L}_{sup} = \frac{1}{N_L} \sum_{i=1}^{N_L} \left[\mathcal{L}_{CE}(f_\theta(x_i), y_i) + \mathcal{L}_{Dice}(f_\theta(x_i), y_i)\right]$$

The unsupervised loss incorporates uncertainty weighting:

$$\mathcal{L}_{unsup} = \frac{1}{N_U} \sum_{j=1}^{N_U} \frac{\sum_{h,w} w_j(h,w) \cdot \ell(f_\theta(x_j)_{h,w}, \tilde{y}_j(h,w))}{\sum_{h,w} w_j(h,w) + \epsilon}$$

where $\ell(\cdot)$ denotes the pixel-wise cross-entropy loss and $\epsilon$ prevents division by zero.

### 2.5 Curriculum Strategy

We implement a curriculum that progressively incorporates more challenging pseudo-labels as training proceeds. The percentile parameter evolves according to:

$$\alpha^{(e)} = \alpha_{min} + (\alpha_{max} - \alpha_{min}) \cdot \left(\frac{e}{E_{max}}\right)^\gamma$$

where $\alpha_{min}$ and $\alpha_{max}$ define the range of percentiles (e.g., 30% to 80%), $E_{max}$ is the total training epochs, and $\gamma$ controls the curriculum pace. Similarly, the unsupervised loss weight ramps up:

$$\mu^{(e)} = \mu_{max} \cdot \left(1 - \exp\left(-5 \cdot \frac{e}{E_{ramp}}\right)\right)$$

### 2.6 Algorithm Summary

The complete training procedure is summarized as:

1. **Initialization**: Pre-train network $f_\theta$ on labeled data $\mathcal{D}_L$ for warm-up epochs.
2. **For each epoch $e$**:
   - Compute adaptive threshold $\tau^{(e)}$ using current curriculum percentile
   - For each mini-batch containing labeled and unlabeled images:
     - Compute supervised loss on labeled samples
     - Generate pseudo-labels via $T$ MC dropout forward passes
     - Compute uncertainty maps and selection masks
     - Compute uncertainty-weighted unsupervised loss
     - Update parameters via gradient descent on $\mathcal{L}_{total}$
3. **Output**: Trained model $f_\theta$ with uncertainty estimation capability

### 2.7 Experimental Design

**Datasets**: We evaluate on two complementary medical imaging tasks:
- **ACDC (Cardiac MRI)**: 100 patients with expert annotations for left ventricle, right ventricle, and myocardium segmentation
- **ChestX-ray14 (Chest X-ray)**: Subset with lung and heart segmentation annotations

**Labeled Data Scenarios**: We simulate label-scarce settings using 5%, 10%, and 20% of available annotations, with remaining data used as unlabeled.

**Baselines**: 
- Fully-supervised training (upper bound)
- Supervised-only with limited labels (lower bound)
- Mean Teacher
- FixMatch adapted for segmentation
- Uncertainty-aware co-training (Zheng et al., 2021)
- UPL-SFDA (Wu et al., 2023)

**Evaluation Metrics**:
- Dice Similarity Coefficient (DSC) for segmentation accuracy
- 95th percentile Hausdorff Distance (HD95) for boundary precision
- Expected Calibration Error (ECE) for uncertainty calibration
- Negative Log-Likelihood (NLL) for probabilistic prediction quality

**Implementation Details**: We use a U-Net architecture with ResNet-34 encoder, $T=10$ MC dropout samples, dropout rate 0.5, and training for 300 epochs with Adam optimizer (learning rate $10^{-4}$).

## 3. Expected Outcomes & Impact

### Expected Results

We anticipate our uncertainty-aware self-training framework will achieve the following outcomes:

**Segmentation Performance**: With only 10% labeled data, we expect to achieve 90-95% of fully-supervised Dice scores across both cardiac MRI and chest X-ray tasks. This would represent a significant improvement over standard self-training baselines, which typically plateau at 80-85% of fully-supervised performance due to error propagation from unreliable pseudo-labels.

**Uncertainty Calibration**: The MC dropout-based uncertainty estimates should demonstrate strong calibration, with high uncertainty concentrated at anatomical boundaries, pathological regions, and areas with imaging artifacts. We expect ECE below 0.05, indicating well-calibrated confidence estimates suitable for clinical decision support.

**Curriculum Effectiveness**: Ablation studies will demonstrate that the progressive curriculum strategy outperforms fixed thresholding approaches by 2-4% DSC, validating the importance of adaptive pseudo-label expansion.

### Scientific Impact

This research contributes methodologically by establishing principled connections between Bayesian uncertainty estimation and semi-supervised learning in medical imaging. The framework provides a template for uncertainty-guided learning that can extend to other medical imaging tasks including detection, registration, and image reconstruction.

### Clinical Impact

By dramatically reducing annotation requirements, our method could accelerate the development of AI tools for underserved clinical applications where expert annotation is scarce. The uncertainty maps provide interpretable confidence indicators that support human-AI collaboration in clinical workflows, addressing a critical barrier to clinical adoption of AI systems. Radiologists can focus their attention on regions flagged as uncertain, improving efficiency while maintaining safety.

### Broader Implications

The uncertainty-aware self-training paradigm addresses fundamental challenges of reliability and label efficiency that extend beyond medical imaging. As healthcare systems worldwide face increasing imaging volumes with constrained specialist resources, methods that maximize learning from limited supervision while quantifying prediction reliability become essential for sustainable, trustworthy AI deployment in clinical practice.