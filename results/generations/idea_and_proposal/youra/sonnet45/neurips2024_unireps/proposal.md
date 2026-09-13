# Research Proposal: Bio-Constrained Training for Unified Neural Representations

## 1. Title

**Bio-Constrained Training for Unified Neural Representations: Bridging Biological and Artificial Convergence Through Identifiability-Promoting Constraints**

## 2. Introduction

### Background

Recent discoveries in neuroscience and artificial intelligence have revealed a striking phenomenon: different learning systems—whether biological brains or artificial neural networks—tend to develop remarkably similar internal representations when processing similar stimuli. This convergence has been documented across multiple scales: between different artificial neural network architectures trained on the same tasks, between artificial networks and biological neural recordings from visual cortex, and even across different species' neural systems. The Platonic Representation Hypothesis (Huh et al., 2024) formalizes this observation, suggesting that diverse learning systems converge toward a shared representational geometry.

However, despite growing empirical evidence for this convergence, we lack a mechanistic explanation for *why* it occurs. Current research approaches this phenomenon from two largely disconnected perspectives. The neuroscience-inspired approach focuses on bio-plausible training methods—such as Hebbian learning, sparse coding, and local learning rules—that mimic biological constraints but rarely analyze their effect on representational convergence systematically. The machine learning approach studies identifiability in neural networks—the conditions under which different training runs converge to functionally equivalent solutions—but typically ignores biological constraints as a potential mechanism for promoting identifiability.

This theoretical gap has significant practical consequences. Without understanding the causal mechanisms driving bio-artificial convergence, we cannot systematically design artificial models that align with biological systems while maintaining competitive performance. This limitation affects multiple application domains: neuroscience validation (using artificial models to test biological theories), model merging and stitching (combining independently trained models), energy-efficient architectures (leveraging biological efficiency principles), and multi-modal learning (aligning representations across modalities).

Recent work provides crucial building blocks for addressing this gap. Huang et al. (2023) demonstrated that deep spiking neural networks (SNNs) achieve 6.6% higher similarity to biological visual cortex compared to standard CNNs, suggesting that biological constraints can enhance bio-similarity. However, SNNs require specialized neuromorphic hardware and sacrifice task performance. Murphy et al. (2024) developed debiased CKA (Centered Kernel Alignment), enabling accurate measurement of similarity between artificial and biological neural representations despite dimensionality mismatches. Reizinger et al. (2025) formalized the Singular Identifiability Theory, providing mathematical tools for analyzing when neural networks converge to unique solutions.

### Research Objectives

This research proposes a unified theoretical framework that bridges biological and artificial neural representation convergence through the lens of identifiability-promoting constraints. Our central hypothesis is that enforcing biological constraints—specifically sparse coding, energy efficiency, and local learning—as auxiliary training objectives in standard artificial neural networks promotes convergence toward representations similar to both biological neural systems and other artificial models. The causal mechanism we propose is that bio-constraints define an identifiability-promoting solution space that overlaps with the space biological systems occupy through evolutionary optimization under similar resource constraints.

Our specific research objectives are:

**Objective 1 (Dual Convergence):** Demonstrate that bio-constrained training enhances similarity to both biological neural recordings (measured via debiased CKA against fMRI data) and other bio-constrained artificial models (cross-model similarity), achieving bio-similarity improvements of 3-5% and cross-model similarity improvements of 2-4% over baseline.

**Objective 2 (Mechanistic Understanding):** Establish that bio-constraints function as identifiability-promoting conditions by showing that combined constraints (sparse + energy + local) outperform individual constraints by >2%, and that representational properties (sparsity, energy efficiency, locality) correlate with convergence metrics.

**Objective 3 (Practical Validation):** Demonstrate that bio-constrained models maintain competitive task performance (ImageNet Top-1 accuracy >74%) while achieving 10-20% reduction in computational cost (FLOPs), and outperform or match existing bio-plausible baselines including deep SNNs.

### Significance

This research makes three categories of contributions:

**Theoretical Contributions:** We provide the first unified framework explaining bio-artificial convergence through identifiability theory, formalizing bio-constraints as identifiability-promoting conditions. This resolves a fundamental gap in understanding why different neural systems converge to similar representations, connecting evolutionary optimization in biological systems to optimization dynamics in artificial networks.

**Methodological Contributions:** We develop a bio-constrained training framework with three auxiliary loss functions (sparse coding, energy efficiency, local learning) that can be applied to standard architectures without requiring specialized hardware. We establish a dual-benchmark validation methodology that simultaneously measures bio-similarity and cross-model similarity, providing comprehensive assessment of representational convergence.

**Practical Contributions:** Our framework enables neuroscience validation (testing biological theories using controllable artificial models), bio-inspired design principles (achieving bio-alignment while maintaining performance), and energy-efficient architectures (reducing computational cost through biological constraints). The 10-20% FLOPs reduction has direct implications for deploying models on resource-constrained devices.

## 3. Methodology

### Research Design Overview

We employ a mixed factorial experimental design with three factors: (1) constraint condition (7 levels: unconstrained baseline, 3 individual constraints, 3 pairwise combinations, 1 full combination), (2) architecture (2 levels: ResNet-50, ViT-B/16), and (3) random seed (5 replications). This yields 70 total models (7×2×5), enabling comprehensive analysis of constraint effects, architectural generalization, and statistical reliability.

### Data Collection

**Training Data:** We use ImageNet-1K (1.28M training images, 1K classes) as the primary training dataset, following standard data augmentation protocols (random resizing and cropping to 224×224, horizontal flipping, color jittering, normalization).

**Biological Neural Data:** We use two publicly available datasets for bio-similarity measurement:
- **THINGS fMRI dataset:** Human fMRI responses to 1,854 natural images across visual cortex (V1, V2, V4, IT), with 3 subjects, providing high-level visual representations
- **Allen Brain Observatory:** Mouse visual cortex calcium imaging responses to natural images, providing complementary cross-species validation

**Validation Data:** ImageNet validation set (50K images) for task performance evaluation.

### Bio-Constrained Training Framework

Our core methodological contribution is a bio-constrained training framework that augments standard supervised learning with three auxiliary loss functions representing biological constraints.

**Total Loss Function:**

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \lambda_{\text{sparse}} \mathcal{L}_{\text{sparse}} + \lambda_{\text{energy}} \mathcal{L}_{\text{energy}} + \lambda_{\text{local}} \mathcal{L}_{\text{local}}$$

where $\lambda_{\text{sparse}}, \lambda_{\text{energy}}, \lambda_{\text{local}} \in [0, 1]$ are constraint weights.

**Sparse Coding Loss ($\mathcal{L}_{\text{sparse}}$):** Biological neurons exhibit sparse activation patterns, with only 1-4% of neurons active for any given stimulus. We enforce sparsity through L1 regularization on activations:

$$\mathcal{L}_{\text{sparse}} = \frac{1}{L} \sum_{l=1}^{L} \frac{1}{N_l} \sum_{i=1}^{N_l} |a_i^{(l)}|$$

where $L$ is the number of layers, $N_l$ is the number of neurons in layer $l$, and $a_i^{(l)}$ is the activation of neuron $i$ in layer $l$. Target sparsity level: L0 norm of 0.4-0.6 (40-60% of neurons active).

**Energy Efficiency Loss ($\mathcal{L}_{\text{energy}}$):** Biological brains operate under severe energy constraints (~20W for human brain). We approximate metabolic cost through computational cost (FLOPs), which correlates with energy consumption:

$$\mathcal{L}_{\text{energy}} = \frac{1}{B} \sum_{b=1}^{B} \text{FLOPs}(x_b)$$

where $B$ is batch size and $\text{FLOPs}(x_b)$ is the floating-point operations for input $x_b$. We implement this using dynamic computation graphs and torch.profiler to measure layer-wise FLOPs during forward passes. Target: 10-20% reduction from baseline (ResNet-50: 4.1 GFLOPs → 3.3-3.7 GFLOPs).

**Local Learning Loss ($\mathcal{L}_{\text{local}}$):** Biological synaptic plasticity depends only on locally available information (pre-synaptic activity, post-synaptic activity, and local neuromodulatory signals), not global error signals. We approximate this through Hebbian-style local learning:

$$\mathcal{L}_{\text{local}} = -\frac{1}{L-1} \sum_{l=1}^{L-1} \text{CKA}(a^{(l)}, a^{(l+1)})$$

where $\text{CKA}(a^{(l)}, a^{(l+1)})$ measures the similarity between consecutive layer activations using Centered Kernel Alignment. This encourages smooth representational transitions that can be learned through local rules. We use linear CKA for computational efficiency:

$$\text{CKA}(X, Y) = \frac{\|Y^T X\|_F^2}{\|X^T X\|_F \|Y^T Y\|_F}$$

where $X \in \mathbb{R}^{n \times p_1}$ and $Y \in \mathbb{R}^{n \times p_2}$ are centered activation matrices.

### Training Procedure

**Architectures:** 
- ResNet-50: 25.6M parameters, 4.1 GFLOPs baseline
- ViT-B/16: 86M parameters, 17.6 GFLOPs baseline

**Hyperparameters:**
- Optimizer: SGD with momentum (0.9), weight decay (1e-4)
- Learning rate: 0.1 with cosine annealing schedule
- Batch size: 256
- Epochs: 90 (standard ImageNet training)
- Constraint weights: Grid search over $\lambda \in \{0, 0.01, 0.05, 0.1, 0.5, 1.0\}$ for each constraint
- Random seeds: 5 replications (42, 123, 456, 789, 2024)

**Constraint Conditions:**
1. **Baseline:** $\lambda_{\text{sparse}} = \lambda_{\text{energy}} = \lambda_{\text{local}} = 0$
2. **Sparse-only:** $\lambda_{\text{sparse}} = 0.1$, others = 0
3. **Energy-only:** $\lambda_{\text{energy}} = 0.05$, others = 0
4. **Local-only:** $\lambda_{\text{local}} = 0.1$, others = 0
5. **Sparse+Energy:** $\lambda_{\text{sparse}} = 0.1, \lambda_{\text{energy}} = 0.05$, $\lambda_{\text{local}} = 0$
6. **Sparse+Local:** $\lambda_{\text{sparse}} = 0.1, \lambda_{\text{local}} = 0.1$, $\lambda_{\text{energy}} = 0$
7. **Energy+Local:** $\lambda_{\text{energy}} = 0.05, \lambda_{\text{local}} = 0.1$, $\lambda_{\text{sparse}} = 0$
8. **Full Bio-Constrained:** $\lambda_{\text{sparse}} = 0.1, \lambda_{\text{energy}} = 0.05, \lambda_{\text{local}} = 0.1$

### Evaluation Metrics

**Primary Metrics:**

**Bio-Similarity:** We measure similarity between artificial model representations and biological neural recordings using debiased CKA (Murphy et al., 2024):

$$\text{CKA}_{\text{debiased}}(X, Y) = \text{CKA}(X, Y) - \mathbb{E}[\text{CKA}(X_{\text{perm}}, Y)]$$

where $X_{\text{perm}}$ is a permuted version of $X$ that breaks stimulus correspondence. This corrects for spurious correlations due to dimensionality mismatch. We compute bio-similarity for each layer against corresponding cortical areas:
- Early layers (conv1-conv3) → V1, V2
- Middle layers (conv4) → V4
- Late layers (conv5, fc) → IT

Target: Bio-similarity > 0.50 (baseline ~0.45), improvement > 3-5%.

**Cross-Model Similarity:** We measure representational similarity between independently trained bio-constrained models using standard CKA:

$$\text{Sim}_{\text{cross}} = \frac{1}{L} \sum_{l=1}^{L} \text{CKA}(X_{\text{model1}}^{(l)}, X_{\text{model2}}^{(l)})$$

Target: Cross-model similarity > 0.60 (baseline ~0.55), improvement > 2-4%.

**Secondary Metrics:**

**Task Performance:** ImageNet Top-1 and Top-5 accuracy. Minimum acceptable: Top-1 > 74% (ResNet-50 baseline: 76.2%, allowing 2% degradation).

**Sparsity:** L0 norm (fraction of active neurons) and L1 norm of activations. Target: L0 = 0.4-0.6.

**Energy Efficiency:** Total FLOPs measured using torch.profiler. Target: 10-20% reduction (3.3-3.7 GFLOPs for ResNet-50).

**Representational Geometry:** 
- Effective dimensionality: $D_{\text{eff}} = \frac{(\sum_i \lambda_i)^2}{\sum_i \lambda_i^2}$ where $\lambda_i$ are eigenvalues of activation covariance
- Representational dissimilarity matrix (RDM) correlation with biological RDMs

### Baseline Comparisons

We compare against five baselines:

1. **Standard ResNet-50/ViT:** Unconstrained training (primary baseline)
2. **Deep SNNs (Huang et al., 2023):** Critical baseline showing 6.6% higher bio-similarity; we must achieve within 2% of this performance
3. **Oja Networks (Oja et al., 2024):** Hebbian local learning
4. **Sparse Networks (Stricker et al., 2024):** Architectural sparsity
5. **Random Controls:** Models with randomized constraint weights to test for measurement artifacts

### Statistical Analysis

**Hypothesis Testing:**

**H1 (Bio-Similarity Enhancement):** Paired t-test comparing bio-constrained vs. baseline bio-similarity across 5 seeds, one-tailed, $\alpha = 0.05$. Effect size requirement: Cohen's $d > 0.5$ (medium effect).

**H2 (Cross-Model Similarity Enhancement):** Paired t-test comparing bio-constrained vs. baseline cross-model similarity, one-tailed, $\alpha = 0.05$, $d > 0.5$.

**H3 (Constraint Necessity):** One-way ANOVA comparing 7 constraint conditions, followed by Tukey HSD post-hoc tests with Bonferroni correction ($\alpha = 0.05/21 = 0.0024$ for 21 pairwise comparisons). Prediction: Full combination significantly outperforms all individual constraints.

**H4 (Dose-Response):** Linear regression of bio-similarity on constraint weight $\lambda$, testing for positive slope ($\beta > 0$, $p < 0.05$).

**H5 (Layer-Specific Effects):** Two-way ANOVA with factors: constraint condition × layer group (early/middle/late), testing for interaction effect ($p < 0.05$).

**Power Analysis:** With $n=5$ seeds, $\alpha=0.05$, and expected effect size $d=0.8$, we achieve power $>0.80$ for detecting bio-similarity differences of 3% (calculated using G*Power 3.1).

**Falsification Criteria:**
- Bio-similarity improvement ≤ 1% (no meaningful effect)
- Task accuracy < baseline - 5% (unacceptable performance degradation)
- Individual constraints perform as well as combined (constraints are not complementary)
- SNNs outperform by >2% (spiking architecture necessary)
- Randomized controls match principled constraints (measurement artifact)

### Ablation Studies

**Constraint Ablation:** Systematically remove each constraint from the full combination to assess individual contributions.

**Hyperparameter Sensitivity:** Test constraint weights $\lambda \in \{0.01, 0.05, 0.1, 0.5, 1.0\}$ to map the accuracy-biosimilarity Pareto frontier.

**Architectural Generalization:** Test on additional architectures (ResNet-18, ResNet-101, ViT-S/16, ViT-L/16) to assess generalization beyond primary architectures.

**Dataset Generalization:** Fine-tune on downstream tasks (CIFAR-100, Places365) to test whether bio-constrained representations transfer better.

### Implementation Details

**Software:** PyTorch 2.0, torchvision, NumPy, SciPy, scikit-learn

**Hardware:** 8× NVIDIA A100 GPUs (40GB), estimated 8 GPU-days for 30 primary models

**Reproducibility:** Fixed random seeds, deterministic CUDA operations, version-controlled code repository, detailed hyperparameter logging

**Computational Budget:** 
- Training: 30 models × 90 epochs × 4 hours = 10,800 GPU-hours ≈ $1,300
- Baselines: 10 models × 4 hours = 40 GPU-hours ≈ $500
- Total: ≈ $1,800 (within $5K budget)

## 4. Expected Outcomes & Impact

### Expected Outcomes

**Primary Outcomes:**

**Outcome 1 (Dual Convergence Validation):** We expect bio-constrained models to achieve bio-similarity scores of 0.48-0.50 (baseline: 0.45), representing 3-5% improvement, and cross-model similarity of 0.57-0.60 (baseline: 0.55), representing 2-4% improvement. Statistical tests will confirm these improvements are significant ($p < 0.05$, $d > 0.5$) and reproducible across random seeds.

**Outcome 2 (Constraint Synergy):** We expect the full combination of constraints to outperform any individual constraint by >2%, demonstrating that sparse coding, energy efficiency, and local learning are complementary mechanisms. Specifically, we predict: Full > Sparse-only by 2.5%, Full > Energy-only by 3%, Full > Local-only by 2%.

**Outcome 3 (Performance-Efficiency Trade-off):** We expect bio-constrained ResNet-50 to achieve 74-75% Top-1 accuracy (baseline: 76.2%) while reducing FLOPs to 3.3-3.7 GFLOPs (baseline: 4.1 GFLOPs), demonstrating a favorable trade-off between task performance and biological alignment.

**Outcome 4 (Layer-Specific Convergence):** We expect early layers to show higher similarity to V1/V2 (CKA > 0.55), middle layers to V4 (CKA > 0.50), and late layers to IT (CKA > 0.45), validating hierarchical correspondence between artificial and biological visual processing.

**Outcome 5 (Baseline Comparison):** We expect bio-constrained models to achieve bio-similarity within 2% of deep SNNs (target: >0.48 vs. SNN: 0.50) while maintaining higher task accuracy (74% vs. 70-72%) and using standard hardware, demonstrating practical advantages over specialized neuromorphic approaches.

**Secondary Outcomes:**

- Sparsity levels of 40-60% (L0 norm: 0.4-0.6)
- Monotonic dose-response relationship between constraint weight and bio-similarity
- Higher effective dimensionality in bio-constrained representations
- Better transfer performance on downstream vision tasks
- Reproducible results across ResNet and ViT architectures

### Theoretical Impact

This research provides the first unified theoretical framework explaining why biological and artificial neural systems converge to similar representations. By formalizing bio-constraints as identifiability-promoting conditions, we connect two previously separate research streams: bio-plausible learning in neuroscience and identifiability theory in machine learning. This framework generates testable predictions about which constraints are necessary and sufficient for convergence, opening new research directions in both fields.

The framework resolves a fundamental puzzle: why do systems optimized under different objectives (evolutionary fitness vs. supervised learning loss) and different mechanisms (synaptic plasticity vs. backpropagation) arrive at similar solutions? Our answer—that shared resource constraints define overlapping solution spaces—provides a parsimonious explanation that can be extended beyond vision to other domains (language, audition, motor control).

### Methodological Impact

The bio-constrained training framework provides a practical tool for neuroscience research. By training artificial models with controllable biological constraints, neuroscientists can test hypotheses about which constraints are critical for biological representations. For example, if removing sparse coding eliminates bio-similarity, this suggests sparsity is a fundamental organizing principle in biological vision. This approach complements traditional neuroscience methods (lesion studies, pharmacological manipulations) with computational experiments.

The dual-benchmark validation methodology (bio-similarity + cross-model similarity) establishes a new standard for evaluating representational convergence. Previous work typically measured only one dimension; our approach demonstrates that true convergence requires alignment along both biological and artificial axes simultaneously.

### Practical Impact

**Energy-Efficient AI:** The 10-20% FLOPs reduction achieved through bio-constraints has direct implications for deploying models on edge devices (smartphones, IoT sensors, robotics). If biological constraints improve efficiency without sacrificing accuracy, this provides a principled approach to model compression that goes beyond ad-hoc pruning methods.

**Model Merging and Stitching:** Higher cross-model similarity enables combining independently trained models without expensive retraining. Bio-constrained models with 60% cross-model similarity (vs. 55% baseline) should enable more effective model merging for federated learning, continual learning, and multi-task learning scenarios.

**Bio-Inspired Architecture Design:** Our findings will inform design principles for next-generation neural architectures. If sparse coding + energy efficiency + local learning are sufficient for bio-alignment, future architectures can incorporate these constraints from the ground up rather than retrofitting them onto existing designs.

**Neuroscience Validation Tools:** The framework enables testing biological theories using artificial models. For example, researchers can test whether predictive coding (a prominent neuroscience theory) emerges naturally from bio-constraints, or whether additional mechanisms are required.

### Broader Impact

This research contributes to the workshop's goal of unifying representations in neural models by providing both theoretical understanding (why convergence occurs) and practical methods (how to promote convergence). By bridging neuroscience and AI, we facilitate cross-pollination between fields: neuroscientists gain computational tools for testing theories, while AI researchers gain principled bio-inspired design principles.

The framework also has implications for AI safety and interpretability. If bio-constrained models develop representations more similar to human visual cortex, they may exhibit more human-like failure modes and biases, making their behavior more predictable and interpretable. This could inform development of more robust and trustworthy AI systems.

### Limitations and Future Directions

**Limitations:** This research focuses on vision domain and feedforward architectures, leaving open questions about generalization to language, audio, and recurrent processing. The identifiability-promoting mechanism is tested empirically but requires formal mathematical proof. The biological neural data (THINGS: n=3 subjects) has limited sample size, requiring validation on larger datasets.

**Future Directions:** 
- Extend to language models (testing whether bio-constraints promote convergence in transformers trained on text)
- Develop formal identifiability proofs connecting bio-constraints to convergence guarantees
- Test on recurrent architectures and temporal processing tasks
- Investigate additional biological constraints (dendritic computation, neuromodulation, oscillatory dynamics)
- Apply framework to multi-modal learning (vision-language alignment)
- Explore evolutionary algorithms that discover optimal constraint combinations

This research establishes bio-constrained training as a principled approach to unifying biological and artificial neural representations, with implications spanning theoretical neuroscience, machine learning methodology, and practical AI applications.