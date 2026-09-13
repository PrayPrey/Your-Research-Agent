# Research Proposal: Predictive Coding Training for Principled Brain-AI Representational Alignment

## 1. Introduction

### 1.1 Background

Understanding how intelligent systems—both biological and artificial—form internal representations of the world remains one of the most fundamental challenges spanning machine learning, neuroscience, and cognitive science. Despite remarkable advances in deep learning and neuroimaging, the field lacks principled methods to systematically compare, measure, and align the representations learned by artificial neural networks (ANNs) with those observed in biological visual systems. This gap limits our ability to build brain-like AI systems and constrains the utility of ANNs as computational models of biological cognition.

Representational alignment refers to the degree to which two systems encode information in geometrically or functionally similar ways. Current approaches to improving brain-AI alignment have largely been incidental rather than designed—improvements emerge as byproducts of architectural choices or training objectives optimized for task performance rather than biological fidelity. This lack of principled intervention methods creates a critical bottleneck: researchers cannot systematically increase or decrease alignment to test hypotheses about shared computational strategies, nor can engineers deliberately design AI systems that process information in brain-like ways.

Predictive coding (PC) theory offers a compelling theoretical framework for addressing this challenge. Originating in neuroscience, predictive coding posits that biological neural systems continuously generate predictions about incoming sensory information and update their internal models based on prediction errors (Rao & Ballard, 1999). This hierarchical predictive processing has been proposed as a unifying principle of cortical computation, with substantial evidence suggesting that the visual cortex implements prediction error minimization across its hierarchical layers (Ali et al., 2021). Recent advances have demonstrated that ANNs trained with PC objectives exhibit brain-like mismatch responses (Gütlin & Auksztulewicz, 2025) and that precision-weighted PC enables stable training of deep networks (Qi et al., 2025).

### 1.2 Research Objectives

This research proposes to test the hypothesis that training neural networks with predictive coding objectives—the same computational principle hypothesized to govern biological visual processing—will produce measurably greater representational alignment with biological visual systems compared to standard supervised learning. Our specific objectives are:

1. **Establish existence of PC-induced alignment improvement**: Demonstrate that PC-trained networks achieve significantly higher representational alignment scores than standard supervised baselines on established brain-score benchmarks.

2. **Isolate the causal mechanism**: Distinguish the contribution of the PC training objective from architectural modifications (lateral connections) through controlled ablation experiments.

3. **Demonstrate controllable intervention**: Show that alignment can be systematically modulated through the PC objective's parametric structure, establishing PC training as a principled intervention method.

4. **Validate cross-species generalization**: Confirm that alignment improvements generalize across macaque, human, and mouse visual system benchmarks, supporting a computational principle explanation over species-specific effects.

### 1.3 Significance

This research addresses fundamental questions at the intersection of machine learning and neuroscience. If successful, it would establish predictive coding training as the first principled, controllable method for systematically increasing brain-AI representational alignment. This has profound implications for:

- **Neuroscience**: Validating PC as a shared computational principle between biological and artificial systems would provide strong evidence for predictive processing theories of cortical computation.
- **Machine Learning**: PC-trained networks could serve as better models of biological vision, enabling more rigorous hypothesis testing about neural computation.
- **AI Safety and Alignment**: Understanding how to systematically control representational alignment provides foundational tools for broader alignment research, including value alignment.
- **Reproducibility**: By providing a principled intervention method with clear parametric control, this work addresses ongoing debates about alignment metrics and measurement approaches.

## 2. Methodology

### 2.1 Experimental Design Overview

We employ a controlled experimental design with four training conditions to isolate the effect of predictive coding objectives on representational alignment:

| Condition | Architecture | Training Objective | Purpose |
|-----------|-------------|-------------------|---------|
| Baseline | Standard ResNet-50 | Cross-entropy (supervised) | Reference baseline |
| Architecture Control | ResNet-50 + lateral connections | Cross-entropy (supervised) | Isolate architectural effects |
| PC-Full | ResNet-50 + lateral connections | PC objective ($\alpha=0.5$) | Test main hypothesis |
| PC-Parametric | ResNet-50 + lateral connections | PC objective ($\alpha \in \{0, 0.25, 0.5, 0.75, 1.0\}$) | Test dose-response |

### 2.2 Network Architecture

We use ResNet-50 as the base architecture, modified following Qi et al. (2025) to incorporate lateral connections and precision weighting necessary for predictive coding:

**Lateral Connections**: For each residual block $l$, we add lateral connections that enable prediction signals to flow from higher to lower layers:

$$\hat{r}_l = W_l^{pred} \cdot r_{l+1}$$

where $\hat{r}_l$ is the predicted representation at layer $l$, $r_{l+1}$ is the representation at layer $l+1$, and $W_l^{pred}$ are learnable prediction weights.

**Precision Weighting**: Following Qi et al. (2025), we implement learnable precision parameters $\pi_l$ for each layer to balance prediction errors across the deep hierarchy:

$$e_l = \pi_l \odot (r_l - \hat{r}_l)$$

where $e_l$ is the precision-weighted prediction error and $\odot$ denotes element-wise multiplication.

### 2.3 Training Objectives

**Baseline and Architecture Control**: Standard cross-entropy loss for ImageNet classification:

$$\mathcal{L}_{CE} = -\sum_{c=1}^{C} y_c \log(\hat{y}_c)$$

**Predictive Coding Objective**: The PC loss combines predictive and contrastive components:

$$\mathcal{L}_{PC} = (1-\alpha) \cdot \mathcal{L}_{predictive} + \alpha \cdot \mathcal{L}_{contrastive}$$

where:

$$\mathcal{L}_{predictive} = \sum_{l=1}^{L-1} \|e_l\|_2^2 = \sum_{l=1}^{L-1} \|\pi_l \odot (r_l - \hat{r}_l)\|_2^2$$

$$\mathcal{L}_{contrastive} = -\log \frac{\exp(sim(r_L, r_L^+)/\tau)}{\sum_{j} \exp(sim(r_L, r_j)/\tau)}$$

The parameter $\alpha \in [0, 1]$ controls the balance between pure predictive error minimization ($\alpha = 0$) and contrastive learning ($\alpha = 1$). For PC-Full, we set $\alpha = 0.5$; for PC-Parametric, we systematically vary $\alpha$.

### 2.4 Training Protocol

**Dataset**: ImageNet-1K (1.28M training images, 50K validation images)

**Training Hyperparameters**:
- Optimizer: AdamW with weight decay 0.05
- Learning rate: 1e-4 with cosine annealing
- Batch size: 256
- Training epochs: 100
- Data augmentation: Standard ImageNet augmentation (random crop, horizontal flip, color jitter)

**Reproducibility**: Each condition is trained with 5 random seeds (seeds 0-4) for statistical analysis.

**Computational Requirements**: Estimated ~2x compute overhead for PC conditions due to lateral connection computations. Total: 45 model training runs.

### 2.5 Representational Alignment Measurement

We measure representational alignment using two complementary metrics applied to brain-score benchmarks:

**Debiased Centered Kernel Alignment (CKA)**: Following Murphy et al. (2024), we compute debiased CKA to avoid inflation from high-dimensional representations:

$$\text{CKA}(X, Y) = \frac{\text{HSIC}(X, Y)}{\sqrt{\text{HSIC}(X, X) \cdot \text{HSIC}(Y, Y)}}$$

where HSIC is the Hilbert-Schmidt Independence Criterion, computed with mean-centering to remove trivial correlations:

$$\text{HSIC}(X, Y) = \frac{1}{(n-1)^2} \text{tr}(\tilde{K}_X \tilde{K}_Y)$$

with $\tilde{K} = HKH$ being the centered kernel matrix.

**Representational Similarity Analysis (RSA)**: We compute RSA as the Spearman correlation between representational dissimilarity matrices (RDMs):

$$\text{RSA}(X, Y) = \rho_s(\text{vec}(D_X), \text{vec}(D_Y))$$

where $D_X$ and $D_Y$ are the RDMs computed as pairwise distances between stimulus representations.

### 2.6 Brain-Score Benchmarks

We evaluate alignment against three established benchmarks spanning species and recording modalities:

1. **Macaque V1-IT**: Neural recordings from macaque visual cortex (V1, V2, V4, IT) during passive viewing of natural images. Primary benchmark for ventral stream alignment.

2. **Human fMRI (Natural Scenes Dataset)**: High-resolution fMRI responses from human visual cortex to natural scene images.

3. **Mouse V1 (Allen Brain Observatory)**: Two-photon calcium imaging from mouse primary visual cortex.

For each benchmark, we extract layer-wise representations from trained networks and compute alignment scores against neural data using both CKA and RSA.

### 2.7 Statistical Analysis

**Primary Analysis (P1 - Alignment Improvement)**:
- Paired t-tests comparing PC-Full vs. Baseline and PC-Full vs. Architecture Control
- Effect size: Cohen's d with target $d > 0.5$ (medium effect)
- Significance threshold: $p < 0.05$ (Bonferroni-corrected for multiple comparisons)

**Secondary Analysis (P2 - Architecture Control)**:
- Paired t-test comparing Architecture Control vs. Baseline
- Expectation: No significant difference ($p > 0.05$)

**Dose-Response Analysis (P3)**:
- Pearson correlation between $\alpha$ values and alignment scores
- Target: $r > 0.5$ indicating systematic relationship

**Cross-Species Generalization (P4)**:
- Repeated measures ANOVA: Condition × Benchmark
- Expectation: Significant main effect of Condition across all benchmarks

**Sample Size Justification**: With $n = 5$ seeds per condition and 3 benchmarks, we have 15 observations per condition. Power analysis indicates 80% power to detect $d = 0.5$ effects at $\alpha = 0.05$.

### 2.8 Falsification Criteria

The hypothesis will be rejected if:

1. PC-Full shows no significant improvement over Baseline ($p > 0.05$) on any benchmark
2. Architecture Control shows equivalent or greater alignment than PC-Full
3. No dose-response relationship exists ($r < 0.3$) between $\alpha$ and alignment
4. Alignment improvement is observed on only one species/benchmark

### 2.9 Implementation Details

**Software Stack**: PyTorch 2.0+, brain-score API, custom PC training modules

**Hardware**: 8× NVIDIA A100 GPUs for parallel training runs

**Code Availability**: All code, trained models, and analysis scripts will be released publicly upon publication.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome**: We predict that PC-trained networks (PC-Full condition) will achieve significantly higher representational alignment scores than both Baseline and Architecture Control conditions. Based on current brain-score benchmarks where standard ResNet-50 achieves approximately 0.45-0.55 on V1-IT alignment, we expect PC-Full to achieve scores in the 0.55-0.65 range, representing a meaningful improvement.

**Mechanism Isolation**: We expect the Architecture Control condition to show no significant improvement over Baseline, demonstrating that lateral connections alone do not drive alignment improvements. This isolation is critical for establishing that the PC training objective—not architectural modifications—is the causal factor.

**Dose-Response Relationship**: We predict a systematic relationship between the $\alpha$ parameter and alignment scores, with intermediate values ($\alpha \approx 0.5$) potentially showing optimal alignment. This would demonstrate that PC training provides controllable intervention on brain-AI alignment.

**Cross-Species Generalization**: We expect alignment improvements to generalize across macaque, human, and mouse benchmarks, supporting the interpretation that PC training induces shared computational structure rather than species-specific pattern matching.

### 3.2 Scientific Impact

**For Neuroscience**: Positive results would provide strong computational evidence for predictive coding theories of cortical function. If ANNs trained with PC objectives align better with biological visual systems across species, this supports the hypothesis that predictive processing is a fundamental principle of visual computation rather than an implementation detail.

**For Machine Learning**: This work would establish the first principled method for systematically increasing brain-AI representational alignment. Unlike current approaches where alignment improvements are incidental, PC training would provide a theoretically motivated, controllable intervention.

**For Alignment Research**: Understanding how to systematically modulate representational alignment has implications beyond brain-AI comparison. The methods developed here could inform broader alignment research, including understanding relationships between representational alignment, behavioral alignment, and value alignment.

### 3.3 Methodological Contributions

**Reproducibility**: By providing a clear experimental protocol with controlled conditions, this work addresses ongoing debates about alignment metrics and measurement approaches. The parametric design ($\alpha$ variation) enables systematic investigation of how training objectives affect alignment.

**Benchmark Contribution**: The trained models and alignment scores will be released as a benchmark for future research, enabling direct comparison of alternative approaches to principled alignment.

**Hackathon Relevance**: This work directly addresses the Re-Align workshop's hackathon theme by providing concrete data on how different training paradigms affect alignment metrics, facilitating common language among researchers.

### 3.4 Limitations and Future Directions

**Scope Limitations**: This study focuses on vision with static images and feedforward-dominant architectures. Future work should extend to temporal processing, recurrent architectures, and other modalities.

**Behavioral Alignment**: We measure representational but not behavioral alignment. Future work should investigate whether PC-induced representational alignment translates to more brain-like behavioral patterns.

**Computational Cost**: PC training incurs approximately 2× computational overhead. Future work should explore more efficient implementations.

### 3.5 Broader Implications

If predictive coding training successfully produces principled brain-AI alignment, this opens several research directions:

1. **Controllable Alignment**: Engineers could deliberately tune AI systems to be more or less brain-like depending on application requirements.

2. **Hypothesis Testing**: Neuroscientists could use PC-trained networks as more valid computational models for testing hypotheses about biological visual processing.

3. **Understanding Alignment**: The parametric structure of PC training enables systematic investigation of what computational properties drive alignment, advancing our theoretical understanding.

4. **Cross-Domain Extension**: Success in vision would motivate extending PC training to language, audio, and multimodal systems, potentially revealing domain-general principles of biological-artificial alignment.

In conclusion, this research proposes a rigorous test of whether predictive coding training can serve as a principled intervention for brain-AI representational alignment. By carefully isolating the contribution of PC objectives from architectural factors and demonstrating controllable modulation through parametric variation, we aim to establish foundational methods for the emerging field of representational alignment research.