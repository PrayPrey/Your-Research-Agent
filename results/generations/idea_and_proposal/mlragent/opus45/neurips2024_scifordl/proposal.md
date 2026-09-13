# Research Proposal

## Title
**Falsifying the Superposition Hypothesis: A Systematic Empirical Investigation of Feature Compression in Neural Networks**

---

## 1. Introduction

### Background

The interpretability of deep neural networks has emerged as one of the most pressing challenges in modern machine learning. As these systems are deployed in high-stakes domains—from medical diagnosis to autonomous vehicles—understanding *how* they arrive at decisions becomes crucial for ensuring safety, fairness, and reliability. Within the mechanistic interpretability community, the **superposition hypothesis** has become a foundational assumption guiding much of the research agenda. This hypothesis posits that neural networks represent more conceptual features than they have dimensions by encoding features as nearly-orthogonal vectors that share overlapping subspaces within activation spaces.

The theoretical appeal of superposition is clear: if a network needs to represent $k$ sparse features but only has $d < k$ dimensions available, it can exploit the geometry of high-dimensional spaces to encode these features with minimal interference, provided the features are rarely active simultaneously. This idea has been formalized through toy models demonstrating that optimal representations under sparsity constraints naturally lead to superposition-like structures. The implications are profound—if superposition is ubiquitous, then individual neurons cannot be interpreted in isolation, and methods like sparse autoencoders become essential for "disentangling" the compressed representations.

However, despite its widespread adoption, the superposition hypothesis rests primarily on theoretical arguments and experiments with simplified toy models. Critical questions remain unanswered: Does superposition actually occur at the scales predicted by theory in production networks? Under what conditions does it emerge or fail to emerge? Are the interference patterns predicted by superposition theory observable in practice? Recent work by Bereska et al. (2025) has begun quantifying superposition through information-theoretic measures, finding evidence that networks encode more features than neurons. Yet, the field lacks systematic falsification attempts—controlled experiments specifically designed to test whether the hypothesis could be wrong.

### Research Objectives

This research proposes a rigorous empirical investigation designed to **test, validate, or falsify** the superposition hypothesis across diverse neural network architectures and scales. Our specific objectives are:

1. **Quantify superposition prevalence**: Establish empirical bounds on how often and to what degree superposition occurs in trained networks, comparing observations against theoretical predictions.

2. **Identify boundary conditions**: Determine the architectural parameters (width, depth), training regimes, and task characteristics that promote or prevent superposition.

3. **Validate interference predictions**: Test whether the error patterns and representational interference predicted by superposition theory actually manifest in network behavior.

4. **Examine scale dependence**: Investigate whether larger models exhibit systematically different superposition behaviors, potentially explaining emergent capabilities.

### Significance

This work directly addresses a critical gap in mechanistic interpretability research. If the superposition hypothesis proves to be overstated or applies only under specific conditions, current interpretability tools may require fundamental revision. Conversely, if superposition is validated and its conditions clarified, we can develop more targeted interpretability methods. Either outcome represents significant progress in our scientific understanding of deep learning. This proposal exemplifies the scientific method applied to deep learning: forming a precise, falsifiable hypothesis and designing controlled experiments to test it.

---

## 2. Methodology

Our methodology comprises four interconnected experimental streams, each targeting different aspects of the superposition hypothesis.

### 2.1 Controlled Experiments with Known Ground-Truth Features

**Experimental Design**: We construct synthetic tasks where the ground-truth feature count is precisely controlled. Following the approach of toy superposition models but at realistic scales, we create datasets where inputs are generated from exactly $k$ independent binary features, each associated with a known direction in the input space.

**Task Construction**: For a task with $k$ features, we generate inputs as:
$$\mathbf{x} = \sum_{i=1}^{k} s_i \cdot \mathbf{v}_i + \epsilon$$
where $s_i \sim \text{Bernoulli}(p)$ indicates feature presence, $\mathbf{v}_i$ are feature vectors, and $\epsilon$ is noise. The sparsity parameter $p$ controls how often features co-occur.

**Width Variation Protocol**: For each value of $k \in \{16, 32, 64, 128, 256, 512\}$, we train networks with varying widths $d \in \{8, 16, 32, ..., 1024\}$, creating scenarios ranging from severe compression ($d \ll k$) to overcomplete representations ($d \gg k$).

**Superposition Detection Metric**: We measure superposition using the **representation capacity ratio** (RCR):
$$\text{RCR} = \frac{\hat{k}_{\text{effective}}}{d}$$
where $\hat{k}_{\text{effective}}$ is the estimated number of features encoded (measured via sparse autoencoders or probing classifiers), and $d$ is the layer width. RCR $> 1$ indicates superposition.

**Prediction from Superposition Theory**: The theory predicts a phase transition: when $d < k$ and features are sufficiently sparse, networks should exhibit RCR $> 1$. We test whether this transition occurs at the predicted $d/k$ ratio and whether the transition sharpness matches theoretical predictions.

### 2.2 Geometric Analysis of Feature Representations

**Dimensionality Estimation**: We employ multiple complementary methods to estimate the intrinsic dimensionality of learned representations, following recommendations from Chun et al. (2025) for bias correction.

**Participation Ratio**: For activation covariance matrix $\mathbf{C}$ with eigenvalues $\{\lambda_i\}$:
$$\text{PR} = \frac{(\sum_i \lambda_i)^2}{\sum_i \lambda_i^2}$$

**Bias-Corrected Estimator**: We implement the finite-sample correction from Chun et al. (2025):
$$\text{PR}_{\text{corrected}} = \text{PR}_{\text{observed}} - \frac{d(d+1)}{2n}$$
where $n$ is the sample size and $d$ is the ambient dimension.

**Intrinsic Dimension via Maximum Likelihood**: We also employ the MLE estimator for intrinsic dimension:
$$\hat{d}_{\text{MLE}} = \left[ \frac{1}{n-1} \sum_{i=1}^{n-1} \log \frac{r_{k}(x_i)}{r_1(x_i)} \right]^{-1}$$
where $r_j(x_i)$ is the distance to the $j$-th nearest neighbor.

**Comparison Protocol**: For each trained network, we measure:
- **Observed dimensionality** $d_{\text{obs}}$: Using the estimators above
- **Predicted dimensionality under superposition**: $d_{\text{pred}} = \min(d, k)$ if no superposition, or potentially $d_{\text{pred}} < d$ if features compress
- **Feature utilization efficiency**: $\eta = \hat{k}_{\text{effective}} / d_{\text{obs}}$

A key prediction: superposition implies $\eta > 1$, meaning more features are encoded than the effective dimensionality suggests.

### 2.3 Interference Detection Through Targeted Probing

**Theoretical Prediction**: If features share dimensions via superposition, activating multiple features simultaneously should produce predictable interference patterns. Specifically, if features $i$ and $j$ have representations $\mathbf{r}_i$ and $\mathbf{r}_j$ with inner product $\langle \mathbf{r}_i, \mathbf{r}_j \rangle = \cos(\theta_{ij})$, then simultaneous activation should produce cross-talk errors proportional to $|\cos(\theta_{ij})|$.

**Interference Probing Protocol**:

1. **Single-feature baseline**: Train linear probes to detect individual features from network activations, measuring accuracy $a_i$ for each feature $i$.

2. **Multi-feature interference test**: Present inputs with feature pairs $(i, j)$ simultaneously active. Measure the deviation from expected probe outputs:
$$\Delta_{ij} = |p_i(\mathbf{h}_{ij}) - p_i(\mathbf{h}_i)| + |p_j(\mathbf{h}_{ij}) - p_j(\mathbf{h}_j)|$$
where $p_i$ is the probe for feature $i$ and $\mathbf{h}$ denotes hidden activations.

3. **Correlation with geometric overlap**: Compute the correlation between $\Delta_{ij}$ and the measured representational overlap:
$$\rho = \text{Corr}(\Delta_{ij}, |\cos(\theta_{ij})|)$$

**Falsification Criterion**: If superposition causes interference, we expect $\rho > 0$ with statistical significance. Absence of correlation ($\rho \approx 0$) would falsify the prediction that superposition produces detectable interference.

**Interference Scaling Analysis**: We examine how interference scales with the degree of superposition:
$$\Delta_{\text{total}} = f(\text{RCR}, p, d)$$
Theory predicts interference increases with RCR and decreases with sparsity $p$.

### 2.4 Scale Analysis Across Model Sizes

**Model Selection**: We analyze pretrained models across scales:
- **Vision**: ResNet-18/50/152, ViT-S/B/L
- **Language**: GPT-2 (124M, 355M, 774M, 1.5B parameters)
- **Controlled scaling**: Custom transformers trained with identical data, varying only width and depth

**Measurements at Scale**:
1. **Layer-wise RCR profiles**: Measure RCR at each layer, tracking how superposition evolves through the network
2. **Width-normalized feature counts**: $\hat{k}/d$ at each layer as a function of total model parameters
3. **Task-specific superposition**: Using probing tasks, measure superposition for different feature types (syntactic vs. semantic in language models)

**Emergent Capability Connection**: We hypothesize that emergent capabilities might correlate with reduced superposition (less interference enabling cleaner computation). We test this by:
- Measuring superposition in layers responsible for specific capabilities
- Comparing superposition metrics before and after capability emergence during training

### 2.5 Experimental Infrastructure and Evaluation

**Datasets**:
- Synthetic controlled tasks (Section 2.1)
- CIFAR-10/100, ImageNet (vision)
- WikiText-103, The Pile (language)

**Evaluation Metrics Summary**:
| Metric | Description | Superposition Prediction |
|--------|-------------|-------------------------|
| RCR | Representation Capacity Ratio | RCR > 1 when $d < k$ |
| $\rho$ | Interference-overlap correlation | $\rho > 0$ |
| PR | Participation ratio | PR < $k$ if compression occurs |
| $\eta$ | Feature utilization efficiency | $\eta > 1$ |

**Statistical Rigor**: All experiments include:
- Multiple random seeds (minimum 5)
- Confidence intervals via bootstrap resampling
- Correction for multiple comparisons (Bonferroni)
- Effect size reporting (Cohen's d)

---

## 3. Expected Outcomes & Impact

### Expected Findings

Based on preliminary observations and theoretical considerations, we anticipate the following outcomes:

1. **Partial Validation**: Superposition likely occurs but may be less ubiquitous than assumed. We expect to find that superposition is task-dependent, emerging strongly for highly sparse feature distributions but diminishing when features co-occur frequently.

2. **Scale Effects**: Larger models may exhibit less superposition in absolute terms but similar RCR values, suggesting they learn more features proportionally to their capacity rather than reducing compression.

3. **Interference Detectability**: We predict measurable but modest interference effects, potentially weaker than theoretical predictions assume due to learned interference-mitigation strategies.

4. **Architecture Dependence**: Different architectures (CNNs vs. Transformers) may exhibit qualitatively different superposition patterns, with attention mechanisms potentially reducing superposition through dynamic routing.

### Scientific Contributions

1. **Empirical Foundation**: First systematic falsification attempt for a core interpretability hypothesis, establishing a model for hypothesis-driven deep learning research.

2. **Quantitative Benchmarks**: Concrete measurements of superposition prevalence across architectures and scales, enabling calibration of interpretability methods.

3. **Methodological Toolkit**: Validated protocols for measuring superposition that can be applied by other researchers.

4. **Theoretical Refinement**: Empirical constraints that can guide development of more accurate theoretical models.

### Broader Impact

If superposition is validated with quantified bounds, interpretability researchers can proceed with greater confidence in sparse autoencoder approaches while understanding their limitations. If falsified or shown to be condition-dependent, the field can redirect effort toward alternative frameworks, potentially accelerating progress toward genuine neural network understanding.

This work exemplifies how the scientific method—with its emphasis on falsifiable predictions and controlled experiments—can advance our understanding of deep learning beyond what purely theoretical or benchmark-driven approaches achieve. By building a rigorous empirical foundation, we enable the interpretability community to move from assumption to knowledge, ultimately contributing to the development of AI systems we can genuinely understand and trust.