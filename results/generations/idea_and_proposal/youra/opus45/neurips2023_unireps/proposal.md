# Research Proposal: SGD-Driven Attractor Dynamics Explain Representation Convergence Across Neural Network Initializations

## 1. Introduction

### 1.1 Background

A remarkable phenomenon has emerged across both neuroscience and artificial intelligence: neural systems—whether biological or artificial—tend to develop strikingly similar internal representations when exposed to similar stimuli. This convergence has been observed when different individuals perceive the same sensory input, when neural networks are trained from different random initializations, and when models process information from multiple modalities representing the same underlying concepts. The ubiquity of this phenomenon suggests fundamental principles governing how learning systems organize information, yet the mechanistic understanding of *why* this convergence occurs remains incomplete.

In artificial neural networks, this representational similarity has profound practical implications. The ability to predict and control representation alignment enables model merging—combining separately trained networks into unified systems without catastrophic interference. It facilitates model stitching, where components from different networks can be recombined to create new architectures. It also underlies successful transfer learning and fine-tuning strategies that have become foundational to modern deep learning practice. Despite these applications, current approaches predominantly measure similarity post-hoc using metrics like Centered Kernel Alignment (CKA), Representational Similarity Analysis (RSA), or Canonical Correlation Analysis (CCA), without providing a predictive framework for when and why convergence will occur.

Recent theoretical advances offer promising directions for understanding this phenomenon. Lin et al. (2024) demonstrated star-shaped connectivity in loss landscapes, showing that minima found by different training runs are connected via linear paths through a common center. Chen et al. (2025) established global convergence guarantees for SGD under maximal update parameterization (μP), proving that rich feature learning can occur with predictable dynamics. Williams (2024) unified various similarity metrics, showing CKA, RSA, and CCA capture equivalent geometric relationships under appropriate conditions. These findings suggest that representation convergence may be a predictable consequence of optimization dynamics rather than a mysterious emergent property.

### 1.2 Research Objectives

This research proposes and tests a unified theoretical framework—**SGD-driven Representation Attractor Theory (SRAT)**—that explains representation convergence through the lens of dynamical systems. Our central hypothesis posits that under standard supervised learning conditions with overparameterized networks, representation convergence emerges because SGD noise acts as an exploration mechanism guiding training trajectories into overlapping attractor basins, where basin structure is determined by task and data statistics.

The specific objectives are:

1. **Verify the existence of representation convergence** across architectures (ResNet, Vision Transformer, MLP) and datasets (MNIST, CIFAR-10, ImageNet subset), establishing quantitative thresholds (CKA > 0.8) for convergence.

2. **Validate the proposed three-step causal mechanism**: (a) task/data statistics shape loss landscape geometry, (b) SGD stochasticity enables trajectory exploration into common basins, (c) basin convergence produces representation similarity.

3. **Demonstrate predictive utility** by showing that early-epoch representation dynamics predict final similarity, enabling practical applications in model merging and transfer learning.

### 1.3 Significance

This research addresses a fundamental question at the intersection of machine learning theory and practice: what determines when independently trained neural networks will develop compatible representations? A validated attractor dynamics framework would transform representation alignment from an empirical observation into a predictable phenomenon, enabling:

- **Principled model merging**: Predicting which models can be successfully merged before attempting combination
- **Efficient transfer learning**: Identifying when representations will transfer across tasks or modalities
- **Modular deep learning**: Designing systems where components can be reliably interchanged
- **Cross-disciplinary insights**: Connecting artificial neural network dynamics to theories of biological neural representation

## 2. Methodology

### 2.1 Theoretical Framework

We formalize the SRAT hypothesis through a three-step causal mechanism:

**Step 1: Task/Data Statistics → Loss Landscape Geometry**

Let $\mathcal{D} = \{(x_i, y_i)\}_{i=1}^N$ denote the training dataset and $\mathcal{L}(\theta; \mathcal{D})$ the loss function parameterized by network weights $\theta \in \mathbb{R}^d$. The loss landscape $\mathcal{L}: \mathbb{R}^d \rightarrow \mathbb{R}$ contains regions of low loss (attractor basins) whose geometry is determined by the data distribution $p(x, y)$ and task structure. We hypothesize that for a given task, there exist dominant attractor basins $\mathcal{B}_1, \mathcal{B}_2, \ldots, \mathcal{B}_k$ such that:

$$\mathcal{B}_i = \{\theta : \mathcal{L}(\theta) < \epsilon \text{ and } \nabla^2 \mathcal{L}(\theta) \text{ has bounded condition number}\}$$

**Step 2: Loss Landscape + SGD Noise → Trajectory Convergence**

SGD dynamics can be approximated by a stochastic differential equation:

$$d\theta_t = -\nabla \mathcal{L}(\theta_t) dt + \sqrt{\frac{\eta}{B}} \Sigma(\theta_t)^{1/2} dW_t$$

where $\eta$ is the learning rate, $B$ is the batch size, $\Sigma(\theta)$ is the gradient noise covariance, and $W_t$ is a Wiener process. The noise term $\sqrt{\eta/B} \cdot \Sigma^{1/2}$ enables exploration, allowing trajectories from different initializations $\theta_0^{(1)}, \theta_0^{(2)}$ to discover common basins.

**Step 3: Trajectory Convergence → Representation Similarity**

When trajectories converge to the same basin, the learned representations become functionally similar. For networks $f_{\theta^{(1)}}$ and $f_{\theta^{(2)}}$ with penultimate layer representations $\phi^{(1)}(x)$ and $\phi^{(2)}(x)$, we measure similarity using Centered Kernel Alignment:

$$\text{CKA}(\phi^{(1)}, \phi^{(2)}) = \frac{\text{HSIC}(K^{(1)}, K^{(2)})}{\sqrt{\text{HSIC}(K^{(1)}, K^{(1)}) \cdot \text{HSIC}(K^{(2)}, K^{(2)})}}$$

where $K^{(i)}_{jk} = \phi^{(i)}(x_j)^\top \phi^{(i)}(x_k)$ and HSIC denotes the Hilbert-Schmidt Independence Criterion.

### 2.2 Experimental Design

**Architecture and Dataset Selection**

We conduct experiments across three architecture families and three datasets to ensure generalizability:

| Architecture | Configuration | Parameters |
|-------------|---------------|------------|
| ResNet-18 | Standard ImageNet configuration | ~11M |
| ViT-Small | Patch size 16, 6 layers, 384 dim | ~22M |
| MLP | 4 layers, 2048 hidden units | ~17M |

| Dataset | Classes | Training Size | Complexity |
|---------|---------|---------------|------------|
| MNIST | 10 | 60,000 | Low |
| CIFAR-10 | 10 | 50,000 | Medium |
| ImageNet-100 | 100 | 130,000 | High |

**Training Protocol**

For each architecture-dataset combination, we train 10 networks with different random seeds (0-9), yielding 45 unique pairs for pairwise comparison. Training uses:

- **Optimizer**: SGD with momentum 0.9
- **Learning rate**: Cosine annealing from 0.1 to 0.001
- **Batch size**: 128
- **Epochs**: 200 (MNIST), 300 (CIFAR-10), 100 (ImageNet-100)
- **Data augmentation**: Standard (random crop, horizontal flip)

**Measurement Protocol**

At epochs $\{1, 5, 10, 20, 50, 100, 150, 200\}$, we compute:

1. **Pairwise CKA**: For all 45 pairs, compute CKA on penultimate layer activations using 5,000 held-out samples
2. **Prediction agreement**: Fraction of test samples where both networks predict the same class
3. **Loss landscape probing**: Linear interpolation between weight vectors to assess connectivity

### 2.3 Verification of Predictions

**Prediction P1 (Convergence Existence)**

*Hypothesis*: Mean CKA > 0.8 for same-architecture, same-task pairs at convergence.

*Statistical test*: One-sample t-test with $H_0: \mu_{\text{CKA}} \leq 0.8$
- Sample size: $n = 45$ pairs per configuration
- Significance level: $\alpha = 0.05$ (Bonferroni corrected for 9 configurations: $\alpha' = 0.0056$)
- Power analysis: With $n = 45$, we achieve power > 0.9 for detecting effect size $d = 0.5$

*Success criterion*: Mean CKA > 0.8 with 95% CI lower bound > 0.75

**Prediction P2 (Timing Predictability)**

*Hypothesis*: Early-epoch CKA (epoch 20) predicts final CKA with correlation $r > 0.6$.

*Statistical test*: Pearson correlation with bootstrap confidence intervals
- Compute CKA at epoch 20 and final epoch for all pairs
- Test $H_0: \rho \leq 0.6$ using Fisher z-transformation

*Success criterion*: $r > 0.6$ with 95% CI lower bound > 0.4

**Prediction P3 (Complexity-Basin Relationship)**

*Hypothesis*: Higher task complexity yields greater CKA variance across seeds.

*Statistical test*: Levene's test for equality of variances across datasets
- Compare $\text{Var}(\text{CKA})$ for MNIST vs. CIFAR-10 vs. ImageNet-100

*Success criterion*: Monotonic increase in variance with complexity ($p < 0.05$)

### 2.4 Causal Mechanism Validation

To validate the three-step causal chain, we conduct targeted ablation experiments:

**Ablation A1: Task Statistics → Landscape (Step 1)**

Train networks on shuffled labels (destroying task structure) and measure CKA. If Step 1 is correct, shuffled-label networks should show significantly lower CKA than correctly-labeled networks.

**Ablation A2: SGD Noise → Convergence (Step 2)**

Compare SGD with different noise levels:
- Full-batch gradient descent (no noise)
- SGD with batch sizes $\{32, 128, 512, 2048\}$
- SGD with explicit noise injection

If Step 2 is correct, intermediate noise levels should maximize CKA, while zero noise (full-batch) should yield lower convergence.

**Ablation A3: Basin Convergence → Similarity (Step 3)**

For high-CKA pairs, verify functional equivalence:
- Prediction agreement > 90% on held-out data
- Similar confidence calibration curves
- Linear mode connectivity (loss barrier < 0.1 along interpolation path)

### 2.5 Baseline Comparisons

We compare SRAT predictions against alternative explanations:

1. **Architecture-only hypothesis**: Similarity arises purely from architectural constraints
   - *Test*: Compare CKA for same vs. different architectures on same task
   
2. **Random baseline**: Similarity is random/unpredictable
   - *Test*: Compare observed CKA distribution to permutation null distribution

3. **Post-hoc CKA**: Standard approach without predictive framework
   - *Test*: Compare early-prediction accuracy of SRAT vs. final-epoch-only measurement

### 2.6 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Mean CKA | Average pairwise CKA across seeds | > 0.8 |
| CKA Variance | Variance of pairwise CKA | Low for simple tasks |
| Prediction Agreement | Fraction of matching predictions | > 0.9 for high-CKA pairs |
| Early-Final Correlation | Pearson $r$ between epoch-20 and final CKA | > 0.6 |
| Linear Connectivity | Max loss along weight interpolation | < 0.1 × final loss |

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on preliminary evidence from the literature and our theoretical framework, we anticipate:

1. **Strong convergence for standard settings**: Mean CKA > 0.85 for ResNet and ViT on CIFAR-10 and ImageNet-100, with lower but still significant convergence (CKA > 0.75) for MLPs.

2. **Predictable dynamics**: Early-epoch CKA (by epoch 20) will predict final similarity with $r > 0.7$, enabling practical early-stopping criteria for model compatibility assessment.

3. **Complexity-dependent variance**: MNIST will show near-perfect convergence (CKA > 0.95, low variance), while ImageNet-100 will show higher variance but still significant convergence.

4. **Causal mechanism validation**: Ablations will confirm that (a) task structure is necessary (shuffled labels reduce CKA by > 0.3), (b) SGD noise facilitates convergence (optimal batch size exists), and (c) high CKA corresponds to functional similarity (prediction agreement > 90%).

### 3.2 Potential Falsification

The hypothesis would be falsified if:
- Mean CKA < 0.6 across same-architecture, same-task pairs
- High CKA (> 0.8) fails to correspond to prediction agreement (< 70%)
- No correlation between early and final CKA ($r < 0.3$)
- Full-batch training achieves equal or higher CKA than SGD

### 3.3 Scientific Impact

**Theoretical contributions**:
- First unified framework connecting loss landscape geometry, optimization dynamics, and representation similarity
- Quantitative predictions for representation convergence that can be tested and refined
- Bridge between dynamical systems theory and deep learning practice

**Methodological contributions**:
- Protocol for predicting model compatibility before full training
- Guidelines for hyperparameter selection to maximize representation alignment
- Benchmark suite for evaluating representation convergence theories

### 3.4 Practical Applications

**Model merging**: SRAT enables prediction of which models can be successfully merged, reducing failed attempts and computational waste. Organizations can assess merger compatibility using early-epoch CKA measurements.

**Transfer learning**: Understanding attractor dynamics allows practitioners to predict when pre-trained representations will transfer effectively to new tasks, guiding decisions about fine-tuning vs. training from scratch.

**Federated learning**: In distributed settings where models are trained on different data partitions, SRAT provides theoretical grounding for when and how model aggregation will succeed.

**Multi-modal learning**: The framework extends naturally to understanding when representations from different modalities (text, image, audio) will align, informing the design of multi-modal systems.

### 3.5 Broader Impact

This research contributes to the broader goal of understanding neural computation across biological and artificial systems. By establishing that representation convergence follows predictable dynamical principles, we provide a foundation for:

- **Neuroscience**: Hypotheses about why biological neural systems develop similar representations
- **Cognitive science**: Understanding the computational principles underlying shared mental representations
- **AI safety**: Predicting and controlling the representations learned by AI systems

The estimated computational cost of ~200 GPU-hours on A100 hardware is modest relative to the potential impact, and all code, trained models, and analysis pipelines will be released publicly to enable reproduction and extension of this work.