# Research Proposal: Bias Competition Dynamics: Tracking Phase Transitions in Deep Learning via Multi-Axis Order Parameters

## 1. Introduction

### 1.1 Background

Deep neural networks exhibit a rich tapestry of learning phenomena that remain poorly understood despite their empirical success. Phenomena such as grokking—where networks suddenly generalize long after achieving perfect training accuracy—double descent in test error curves, and simplicity bias toward low-frequency functions suggest that training dynamics involve complex transitions between distinct learning regimes. These observations challenge classical statistical learning theory and demand new theoretical frameworks capable of explaining when and why networks shift between memorization and generalization, or between fitting simple versus complex functions.

Current theoretical approaches have made significant progress by analyzing individual inductive biases in isolation. The frequency bias literature demonstrates that neural networks preferentially learn low-frequency components of target functions before high-frequency components, a phenomenon linked to the spectral properties of gradient descent. Separately, complexity bias research has shown that networks exhibit preferences for functions with fewer linear regions, connecting architectural choices to the expressivity and generalization of learned representations. However, these perspectives remain disconnected, failing to capture the competitive dynamics that govern real training trajectories where multiple biases interact and potentially conflict.

The high-dimensional nature of neural network optimization landscapes further complicates our understanding. Classical intuitions from low-dimensional geometry often mislead when applied to the millions or billions of parameters in modern networks. Recent advances in statistical physics and random matrix theory have provided tools for analyzing such high-dimensional systems, revealing phase transitions analogous to those in physical systems. Yet, a unified framework connecting these mathematical tools to observable training dynamics remains elusive.

### 1.2 Research Objectives

This research proposes to develop and validate a novel theoretical framework—Bias Competition Dynamics (BCD)—that characterizes deep learning training dynamics through the lens of competing inductive biases. Our central hypothesis posits that training dynamics can be understood by tracking two coupled order parameters: the Spectral Smoothness Ratio (SSR), measuring frequency bias, and the Linear Region Density (LRD), measuring complexity bias. Under gradient flow, these parameters follow predictable trajectories in a two-dimensional phase space, with detectable crossings corresponding to behavioral phase transitions.

Our specific objectives are:

1. **Establish existence of coupled dynamics**: Demonstrate that SSR and LRD exhibit correlated, non-independent evolution during training with detectable phase transitions.

2. **Validate causal mechanisms**: Confirm that gradient flow induces the observed coupling through systematic interventions on architecture, data, and optimization.

3. **Develop predictive framework**: Create a practical methodology for predicting dominant biases and transition timing from initial conditions.

4. **Compare against baselines**: Demonstrate superior predictive power compared to single-bias frameworks and regime-based approaches.

### 1.3 Significance

This research addresses fundamental questions at the intersection of optimization theory, statistical physics, and deep learning practice. A successful BCD framework would provide:

- **Theoretical unification**: A principled way to understand how multiple inductive biases compete and cooperate during training.
- **Practical diagnostics**: Tools for practitioners to predict and diagnose training dynamics, enabling better hyperparameter selection.
- **Architectural insights**: Understanding of how network structure influences bias competition, informing architecture design.
- **Foundation for scaling**: A framework potentially extensible to larger models and more complex architectures.

## 2. Methodology

### 2.1 Order Parameter Definitions

#### 2.1.1 Spectral Smoothness Ratio (SSR)

The SSR quantifies the frequency content of the function learned by the network. For a network $f_\theta: \mathbb{R}^d \rightarrow \mathbb{R}$ with parameters $\theta$ at training step $t$, we define:

$$\text{SSR}(t) = \frac{E_{\text{low}}(t)}{E_{\text{high}}(t)}$$

where $E_{\text{low}}(t)$ and $E_{\text{high}}(t)$ represent the energy in low and high frequency bands respectively. Specifically, we sample the network output on a regular grid $\{x_i\}_{i=1}^N$ covering the input domain and compute the discrete Fourier transform:

$$\hat{f}_k = \sum_{i=1}^{N} f_\theta(x_i) e^{-2\pi i k \cdot x_i / N}$$

The energy in frequency band $\mathcal{B}$ is:

$$E_{\mathcal{B}}(t) = \sum_{k \in \mathcal{B}} |\hat{f}_k|^2$$

We partition frequencies at the median magnitude, with $\mathcal{B}_{\text{low}}$ containing the lower half and $\mathcal{B}_{\text{high}}$ the upper half. High SSR indicates dominance of smooth, low-frequency components; low SSR indicates high-frequency content.

#### 2.1.2 Linear Region Density (LRD)

For ReLU networks, the input space partitions into linear regions where the network computes an affine function. Following the methodology of Montúfar et al. and subsequent refinements, we define:

$$\text{LRD}(t) = \frac{R(t)}{V}$$

where $R(t)$ is the number of distinct linear regions and $V$ is the volume of the input domain. Direct enumeration is computationally prohibitive, so we employ a sampling-based approximation:

1. Sample $M$ random line segments in the input space
2. For each segment, count activation pattern changes (linear region boundaries crossed)
3. Estimate $R(t)$ using the relationship between boundary crossings and region count

Specifically, for a network with $L$ layers and widths $\{n_l\}$, we sample segments and count the number of times any ReLU unit changes activation state along each segment. The LRD estimate is:

$$\widehat{\text{LRD}}(t) = \frac{1}{M} \sum_{m=1}^{M} \frac{c_m + 1}{|s_m|}$$

where $c_m$ is the boundary crossing count for segment $m$ and $|s_m|$ is segment length.

#### 2.1.3 Generalization Gap Trajectory (GGT)

As a behavioral proxy for memorization versus generalization, we track:

$$\text{GGT}(t) = \mathcal{L}_{\text{train}}(t) - \mathcal{L}_{\text{test}}(t)$$

where $\mathcal{L}$ denotes cross-entropy loss. Positive GGT indicates memorization; negative or near-zero GGT indicates generalization.

### 2.2 Phase Space Dynamics

We hypothesize that the evolution of order parameters follows coupled dynamics:

$$\frac{d\text{SSR}}{dt} = F_1(\text{SSR}, \text{LRD}, \theta, \mathcal{D})$$

$$\frac{d\text{LRD}}{dt} = F_2(\text{SSR}, \text{LRD}, \theta, \mathcal{D})$$

where $\theta$ represents network parameters and $\mathcal{D}$ the data distribution. The functions $F_1, F_2$ encode how gradient descent on the loss landscape induces changes in these order parameters.

**Phase transitions** occur when trajectories cross critical manifolds in (SSR, LRD) space, corresponding to qualitative changes in the dominant bias. We detect transitions using change point detection algorithms (PELT - Pruned Exact Linear Time) applied to the normalized trajectory:

$$\tilde{\text{SSR}}(t) = \frac{\text{SSR}(t) - \mu_{\text{SSR}}}{\sigma_{\text{SSR}}}, \quad \tilde{\text{LRD}}(t) = \frac{\text{LRD}(t) - \mu_{\text{LRD}}}{\sigma_{\text{LRD}}}$$

### 2.3 Experimental Design

#### 2.3.1 Datasets and Tasks

We employ a progression from controlled to naturalistic settings:

1. **Modular Arithmetic** (Primary): $f(a, b) = (a \circ b) \mod p$ for operations $\circ \in \{+, \times\}$ and primes $p \in \{97, 113\}$. These tasks exhibit clear grokking and allow precise control over complexity.

2. **MNIST**: Standard digit classification with controlled label noise ($\eta \in \{0, 0.1, 0.2\}$) to modulate memorization pressure.

3. **CIFAR-10**: Natural image classification to test generalization to more complex data distributions.

#### 2.3.2 Architectures

| Architecture | Width | Depth | Parameters |
|--------------|-------|-------|------------|
| MLP-Small | 64 | 2 | ~8K |
| MLP-Medium | 256 | 4 | ~200K |
| MLP-Large | 512 | 6 | ~1.5M |
| CNN-Small | 32 channels | 4 conv | ~50K |
| ResNet-18 | Standard | 18 | ~11M |

All networks use ReLU activations to enable LRD computation.

#### 2.3.3 Optimization Configurations

We systematically vary:
- **Optimizer**: SGD (momentum 0.9), Adam ($\beta_1=0.9, \beta_2=0.999$)
- **Learning rate**: $\eta \in \{10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}\}$
- **Weight decay**: $\lambda \in \{0, 10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}\}$
- **Batch size**: Fixed at 64 (controlled variable)

#### 2.3.4 Measurement Protocol

For each experimental configuration:

1. Initialize network with standard Kaiming initialization
2. Train for $T$ steps (task-dependent: 50K for modular arithmetic, 100K for vision)
3. Every 100 steps, compute:
   - SSR via FFT on 10,000 sampled input points
   - LRD via 1,000 random line segments
   - GGT from held-out test set
   - Training/test accuracy and loss

4. Repeat with 5 random seeds minimum (15 for primary conditions)

### 2.4 Validation Experiments

#### 2.4.1 Experiment 1: Existence of Coupled Dynamics (SH1)

**Objective**: Establish that SSR and LRD exhibit correlated, non-independent dynamics.

**Protocol**:
- Run full measurement protocol on all architecture × dataset × optimizer combinations
- Compute Pearson correlation $r(\text{SSR}(t), \text{LRD}(t))$ across training
- Apply PELT change point detection to identify transitions
- Correlate detected transitions with GGT sign changes

**Success Criteria**:
- $|r| > 0.3$ in $\geq 70\%$ of runs (rejecting independence)
- $\geq 70\%$ of detected transitions correspond to GGT behavioral changes within 500 steps

**Falsification**: $|r| < 0.3$ in $\geq 80\%$ of runs indicates independent dynamics.

#### 2.4.2 Experiment 2: Causal Mechanism Validation (SH2)

**Objective**: Confirm gradient flow as the causal driver of phase transitions.

**Sub-experiments**:

**(H-M1) Initial Position Dependence**: 
- Vary initialization scale by factors of $\{0.5, 1.0, 2.0\}$
- Predict initial (SSR, LRD) position from architecture
- Success: $R^2 > 0.6$ for initial position prediction

**(H-M2) Gradient Flow Coupling**:
- Compare full gradient descent vs. layer-wise frozen training
- Success: Freezing disrupts coupling ($\Delta r > 0.2$)

**(H-M3) Weight Decay Modulation**:
- Systematic sweep of $\lambda \in \{0, 10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}\}$
- Success: Transition timing shifts $\geq 20\%$ between $\lambda=0$ and $\lambda=0.1$ ($p < 0.05$)

**(H-M4) Data Spectral Content**:
- Apply low-pass/high-pass filtering to input data
- Success: Filtered data shifts initial SSR and subsequent trajectory ($p < 0.05$)

#### 2.4.3 Experiment 3: Predictive Accuracy (SH3)

**Objective**: Demonstrate BCD predicts transitions better than baselines.

**Baselines**:
- **Random**: 33% accuracy (3-class: SSR-dominant, LRD-dominant, balanced)
- **Li2 Framework**: Single-axis frequency bias prediction
- **Geiger Phase Diagrams**: Regime classification without dynamics

**Protocol**:
- From initial 1000 steps, predict: (a) final dominant bias, (b) first transition timing
- Evaluate on held-out test runs

**Success Criteria**:
- Dominant bias prediction: $\geq 60\%$ accuracy (vs. 33% random)
- Transition timing: within $\pm 10\%$ of actual step in $\geq 60\%$ of cases

### 2.5 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Correlation Coefficient | $r(\text{SSR}, \text{LRD})$ | $|r| > 0.3$ |
| Transition Correspondence | % transitions matching GGT changes | $\geq 70\%$ |
| Prediction Accuracy | Correct dominant bias / total | $\geq 60\%$ |
| Timing Error | $|\hat{t} - t| / T$ | $\leq 10\%$ |
| Effect Size | Cohen's $d$ for interventions | $d > 0.5$ |

### 2.6 Statistical Analysis

All experiments use:
- **Sample size**: $n \geq 15$ per primary condition, $n \geq 5$ for secondary
- **Significance level**: $\alpha = 0.05$ with Bonferroni correction for multiple comparisons
- **Reporting**: Mean $\pm$ standard deviation, 95% confidence intervals, $p$-values, effect sizes
- **Change point detection**: PELT algorithm with BIC penalty selection

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (P1)**: We expect to observe that SSR and LRD trajectories exhibit significant correlation ($|r| > 0.3$) in the majority of experimental conditions, with detectable phase transitions corresponding to behavioral changes in at least 70% of cases. This would establish the existence of coupled bias dynamics as a fundamental feature of deep learning training.

**Secondary Outcomes**:

**(P2) Weight Decay Effects**: We anticipate that increased weight decay will accelerate SSR stabilization (favoring smooth functions earlier) while delaying LRD transitions (maintaining simpler region structure longer). Quantitatively, we expect timing shifts of at least 20% between extreme weight decay values.

**(P3) Predictive Framework**: The BCD framework should achieve at least 60% accuracy in predicting dominant biases and transition timing, significantly exceeding the 33% random baseline and providing practical value for training diagnostics.

**Potential Negative Results**: If SSR and LRD dynamics prove independent ($|r| < 0.3$), this would falsify the coupling hypothesis but still provide valuable insight that these biases operate through separate mechanisms. If transitions are undetectable (smooth trajectories), this would suggest continuous rather than phase-transition dynamics, requiring framework revision.

### 3.2 Theoretical Impact

This research would provide the first multi-axis dynamical framework for understanding bias competition in deep learning. By connecting concepts from statistical physics (order parameters, phase transitions) to neural network training, we establish a bridge between theoretical analysis and empirical phenomena. The framework offers:

- **Unified perspective**: Integration of frequency bias and complexity bias literatures
- **Mechanistic understanding**: Causal explanation for phenomena like grokking and double descent
- **Mathematical foundation**: Coupled ODE framework amenable to further theoretical analysis

### 3.3 Practical Impact

For practitioners, the BCD framework offers:

- **Training diagnostics**: Real-time monitoring of bias competition to detect problematic dynamics
- **Hyperparameter guidance**: Principled selection of weight decay and learning rate based on desired bias trajectory
- **Architecture selection**: Understanding of how network structure influences bias competition
- **Early stopping criteria**: Detection of phase transitions as indicators of generalization onset

### 3.4 Limitations and Future Directions

This initial study focuses on feedforward ReLU networks and classification tasks. Future work should extend to:

- **Transformers**: Adapting order parameters for attention-based architectures
- **Generative models**: Understanding bias competition in VAEs, GANs, and diffusion models
- **Scale**: Validating framework on larger models approaching production scale
- **Additional axes**: Incorporating other biases (e.g., locality, equivariance) into the framework

The computational cost of LRD estimation remains a practical limitation. Developing efficient approximations or alternative complexity measures would enhance applicability.

### 3.5 Timeline

- **Months 1-3**: Implementation of measurement infrastructure and pilot experiments
- **Months 4-6**: Experiment 1 (existence validation) and initial Experiment 2
- **Months 7-9**: Complete Experiment 2 (causal mechanisms) and Experiment 3 (prediction)
- **Months 10-12**: Analysis, framework refinement, and manuscript preparation

This research program promises to advance our fundamental understanding of deep learning dynamics while providing practical tools for the machine learning community.