# Research Proposal: Inference-Time Noise Modulation for Controllable Memory-Generation Trade-off in Diffusion Models

## 1. Introduction

### 1.1 Background

Associative memory (AM) represents a fundamental cognitive mechanism enabling the retrieval of complete patterns from partial cues—a capability central to human cognition, from recognizing faces to recalling experiences. The mathematical formalization of associative memory, pioneered through Hopfield Networks in the 1980s, established foundational principles that continue to influence modern machine learning. The 2024 Nobel Prize in Physics, awarded for "foundational discoveries and inventions that enable machine learning with artificial neural networks," underscores the enduring significance of these contributions and their profound impact on contemporary AI systems.

Recent theoretical advances have revealed deep connections between associative memory frameworks and modern generative models, particularly diffusion models. Ambrogioni (2023) established a formal equivalence between diffusion model energy landscapes and Hopfield associative memory attractors, demonstrating that the denoising process in diffusion models can be understood as gradient descent on an energy surface where training patterns correspond to attractor states. This theoretical bridge suggests that concepts from associative memory—such as attractor basins, memory capacity, and retrieval dynamics—may provide powerful tools for understanding and controlling diffusion model behavior.

Diffusion models have emerged as state-of-the-art generative models across diverse domains, from image synthesis to molecular design. However, a fundamental tension exists in their operation: models trained on discrete pattern sets exhibit dual behavior, sometimes faithfully retrieving memorized training samples and other times generating novel outputs that interpolate between or extrapolate beyond training data. This duality, while potentially useful, currently lacks principled control mechanisms. Users cannot specify whether they desire faithful retrieval of stored patterns or creative generation of novel samples without retraining the model—a significant limitation for practical deployment.

### 1.2 Research Objectives

This research proposes to develop and validate a training-free, single-parameter control mechanism that enables users to predictably shift diffusion model outputs between memory retrieval and novel generation. Specifically, we hypothesize that scaling the inference-time noise schedule by a parameter $\lambda \in [0,1]$ will predictably control this trade-off through a well-defined causal mechanism: $\lambda$ directly scales noise variance $\sigma(t)$, which controls trajectory exploration depth in the energy landscape—low noise confines trajectories to single attractor basins (yielding memorized patterns), while high noise enables cross-basin exploration (yielding novel interpolations).

Our primary objectives are:

1. **Demonstrate existence**: Establish that inference-time noise variance modulation systematically affects output characteristics in diffusion models trained on discrete patterns.

2. **Validate mechanism**: Confirm that the causal chain ($\lambda \rightarrow \sigma(t) \rightarrow$ trajectory dynamics $\rightarrow$ memory/generation outcome) operates as theorized.

3. **Quantify control**: Characterize the monotonic relationship between $\lambda$ and the memory-generation trade-off with sufficient precision for practical deployment.

### 1.3 Significance

This research bridges associative memory theory with practical diffusion model deployment, addressing a gap identified as central to the New Frontiers in Associative Memories workshop agenda. The proposed mechanism offers several significant contributions:

- **Theoretical integration**: Provides empirical validation of the diffusion-AM equivalence established by Ambrogioni (2023), strengthening the theoretical foundations connecting these fields.

- **Practical utility**: Enables application-specific control without retraining—users requiring exact recall (e.g., medical image retrieval) can operate at low $\lambda$, while those seeking creative synthesis (e.g., artistic generation) can use high $\lambda$.

- **Methodological advancement**: Establishes a paradigm for inference-time control of generative models grounded in energy-based interpretations, potentially extensible to other architectures.

## 2. Methodology

### 2.1 Theoretical Framework

We formalize the noise modulation mechanism within the diffusion-associative memory framework. Let $\mathbf{x}_0$ denote a clean data sample and $\mathbf{x}_t$ the noised version at timestep $t$. The standard DDPM forward process is:

$$\mathbf{x}_t = \sqrt{\bar{\alpha}_t}\mathbf{x}_0 + \sqrt{1-\bar{\alpha}_t}\boldsymbol{\epsilon}, \quad \boldsymbol{\epsilon} \sim \mathcal{N}(0, \mathbf{I})$$

where $\bar{\alpha}_t = \prod_{s=1}^{t}\alpha_s$ and $\alpha_t = 1 - \beta_t$ for noise schedule $\{\beta_t\}_{t=1}^T$.

We introduce the noise modulation parameter $\lambda \in [0,1]$ that scales the effective noise variance:

$$\sigma_{\text{controlled}}(t) = \lambda \cdot \sigma_{\text{base}}(t)$$

where $\sigma_{\text{base}}(t) = \sqrt{1-\bar{\alpha}_t}$. The modified reverse process becomes:

$$\mathbf{x}_{t-1} = \frac{1}{\sqrt{\alpha_t}}\left(\mathbf{x}_t - \frac{1-\alpha_t}{\sqrt{1-\bar{\alpha}_t}}\boldsymbol{\epsilon}_\theta(\mathbf{x}_t, t)\right) + \lambda \cdot \sigma_t \mathbf{z}$$

where $\mathbf{z} \sim \mathcal{N}(0, \mathbf{I})$ and $\sigma_t$ is the standard deviation of the reverse process noise.

Under the diffusion-AM equivalence (Ambrogioni, 2023), the score function $\nabla_{\mathbf{x}} \log p_t(\mathbf{x})$ approximated by the trained model corresponds to the negative gradient of a Hopfield-like energy:

$$E(\mathbf{x}) = -\log \sum_{i=1}^{N} \exp\left(-\frac{\|\mathbf{x} - \boldsymbol{\xi}_i\|^2}{2\sigma^2}\right)$$

where $\{\boldsymbol{\xi}_i\}_{i=1}^N$ are the stored patterns (training data). The parameter $\lambda$ modulates the effective temperature of this energy landscape, controlling the depth and breadth of attractor basin exploration.

### 2.2 Data Collection and Preparation

**Dataset**: We use MNIST as our primary testbed, selecting $N = 1000$ discrete patterns through stratified sampling (100 samples per digit class). This controlled setting enables precise measurement of retrieval versus generation behavior.

**Preprocessing**: Images are normalized to $[-1, 1]$ range and resized to $32 \times 32$ pixels for computational efficiency. We compute and store the pairwise distance matrix $\mathbf{D} \in \mathbb{R}^{N \times N}$ where $D_{ij} = \|\boldsymbol{\xi}_i - \boldsymbol{\xi}_j\|_2$ for novelty threshold calibration.

**Train/Test Protocol**: The diffusion model is trained on the full 1000-pattern set. Evaluation generates samples conditioned on random noise seeds, with no overlap between training patterns and evaluation seeds.

### 2.3 Model Architecture and Training

**Architecture**: We employ a standard U-Net architecture following Ho et al. (2020), with:
- 4 resolution levels (32→16→8→4)
- 128 base channels with multipliers [1, 2, 2, 2]
- 2 residual blocks per resolution
- Sinusoidal timestep embeddings
- Group normalization and SiLU activations

**Training Protocol**:
- Optimizer: Adam with learning rate $2 \times 10^{-4}$
- Batch size: 64
- Training steps: 100,000
- Noise schedule: Linear $\beta_t$ from $10^{-4}$ to $0.02$ over $T = 1000$ timesteps
- Loss: Standard MSE on predicted noise

### 2.4 Experimental Design

#### Stage 1: Baseline Noise Modulation

**Independent Variable**: $\lambda \in \{0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0\}$

**Procedure**:
1. For each $\lambda$ value, generate $n = 200$ samples using the modified reverse process
2. Use identical random seeds across $\lambda$ values for paired comparisons
3. Repeat with 5 different seed sets for statistical robustness (total: 7000 samples)

**Dependent Variables and Metrics**:

*Retrieval Accuracy*: Proportion of generated samples with cosine similarity $> 0.95$ to nearest training pattern:

$$\text{Retrieval}(\mathbf{x}) = \mathbb{1}\left[\max_{i} \frac{\mathbf{x} \cdot \boldsymbol{\xi}_i}{\|\mathbf{x}\| \|\boldsymbol{\xi}_i\|} > 0.95\right]$$

*Generation Novelty*: Proportion of samples with minimum L2 distance exceeding threshold:

$$\text{Novelty}(\mathbf{x}) = \mathbb{1}\left[\min_{i} \|\mathbf{x} - \boldsymbol{\xi}_i\|_2 > 0.7 \cdot D_{\max}\right]$$

where $D_{\max} = \max_{i,j} D_{ij}$ is the maximum pairwise distance in the training set.

*Trade-off Score*: Continuous measure combining retrieval and novelty:

$$S(\mathbf{x}) = 1 - \frac{\min_i \|\mathbf{x} - \boldsymbol{\xi}_i\|_2}{D_{\max}}$$

where $S \approx 1$ indicates retrieval and $S \approx 0$ indicates maximal novelty.

*Monotonicity*: Pearson correlation coefficient between $\lambda$ and mean novelty score across samples.

#### Stage 2: Trajectory-Aware Enhancement (Conditional)

If Stage 1 achieves $< 80\%$ of performance targets, we implement trajectory-aware modulation:

**Algorithm**:
```
Input: Initial noise x_T, trained model ε_θ, λ parameter, training patterns {ξ_i}
Output: Generated sample x_0

for t = T to 1 do:
    # Compute predicted clean sample
    x̂_0 = (x_t - √(1-ᾱ_t) · ε_θ(x_t, t)) / √ᾱ_t
    
    # Compute distance to nearest attractor
    d_min = min_i ||x̂_0 - ξ_i||_2
    
    # Adaptive noise scaling based on attractor proximity
    λ_adaptive = λ · (1 + γ · d_min / D_max)  # γ is sensitivity parameter
    
    # Modified reverse step
    x_{t-1} = μ_θ(x_t, t) + λ_adaptive · σ_t · z
end for
return x_0
```

This enhancement modulates noise based on trajectory proximity to attractors, providing finer control at basin boundaries where Pham et al. (2025) identified spurious states.

### 2.5 Statistical Analysis Plan

**Primary Hypothesis Tests**:

*P1 (Retrieval at Low λ)*: One-sample t-test
- $H_0$: Retrieval accuracy at $\lambda \leq 0.2$ is $\leq 90\%$
- $H_1$: Retrieval accuracy at $\lambda \leq 0.2$ is $> 90\%$
- Significance level: $\alpha = 0.05$ (one-tailed)

*P2 (Novelty at High λ)*: One-sample t-test
- $H_0$: Generation novelty at $\lambda \geq 0.8$ is $\leq 80\%$
- $H_1$: Generation novelty at $\lambda \geq 0.8$ is $> 80\%$
- Significance level: $\alpha = 0.05$ (one-tailed)

*P3 (Monotonicity)*: Pearson correlation with bootstrapped confidence intervals
- Target: $r > 0.9$ with 95% CI excluding 0.5
- Bootstrap iterations: 10,000

**Power Analysis**: With $n = 200$ samples per condition and expected large effect size ($d > 0.8$), statistical power exceeds 0.95 for detecting the hypothesized effects.

**Falsification Criteria**:
1. Retrieval accuracy at $\lambda \leq 0.2$ below 70% (primary failure)
2. Pearson $r < 0.5$ between $\lambda$ and novelty (mechanism failure)
3. Performance at $\lambda = 1.0$ differs significantly from standard DDPM (implementation error)

### 2.6 Ablation Studies

1. **Noise schedule variants**: Test linear, cosine, and learned schedules to assess generalization
2. **Dataset scale**: Evaluate with $N \in \{100, 500, 1000, 5000\}$ patterns
3. **Pattern complexity**: Extend to CIFAR-10 discrete subsets
4. **Modulation timing**: Apply $\lambda$ only to early/late timesteps to identify critical phases

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical framework and supporting literature, we anticipate:

**Primary Outcomes**:
- At $\lambda \leq 0.2$: Retrieval accuracy $\geq 90\%$, with generated samples exhibiting high fidelity to training patterns
- At $\lambda \geq 0.8$: Generation novelty $\geq 80\%$, with samples representing meaningful interpolations or extrapolations
- Monotonic trade-off: Pearson $r > 0.9$ between $\lambda$ and novelty score

**Secondary Outcomes**:
- Identification of critical $\lambda$ threshold (estimated $\lambda^* \approx 0.4-0.6$) marking the phase transition between retrieval-dominated and generation-dominated regimes
- Characterization of the transition sharpness, informing practical parameter selection
- Computational overhead $< 5\%$ for Stage 1 (no additional forward passes required)

### 3.2 Theoretical Impact

This research provides empirical validation of the diffusion-associative memory equivalence, strengthening theoretical foundations connecting energy-based models, Hopfield networks, and modern generative architectures. The demonstration that inference-time noise modulation controls attractor basin exploration offers a concrete, testable prediction derived from this theoretical framework.

The work contributes to understanding the memorization-generalization spectrum in generative models—a topic of significant interest given concerns about training data reproduction in large-scale models. Our mechanistic explanation, grounded in energy landscape dynamics, provides interpretable insights beyond empirical observations.

### 3.3 Practical Impact

The proposed single-parameter control mechanism offers immediate practical utility:

- **Medical imaging**: Low $\lambda$ for faithful retrieval of reference patterns in diagnostic applications
- **Creative applications**: High $\lambda$ for novel synthesis in artistic and design contexts
- **Data augmentation**: Intermediate $\lambda$ for controlled variation generation
- **Privacy-aware generation**: Tunable trade-off between utility and training data exposure

The training-free nature of our approach enables deployment on existing models without computational overhead of retraining, democratizing access to controllable generation.

### 3.4 Broader Impact on Associative Memory Research

This work exemplifies the productive integration of associative memory theory with modern deep learning practice—a central goal of the New Frontiers in Associative Memories workshop. By demonstrating that classical concepts (attractor basins, energy landscapes, memory retrieval) provide actionable insights for controlling state-of-the-art generative models, we strengthen the case for continued cross-pollination between these communities.

The methodology established here—deriving control mechanisms from theoretical equivalences and validating through systematic experimentation—provides a template for future work exploring other AM-inspired interventions in modern architectures, including memory-augmented transformers, energy-based models, and hybrid systems.

### 3.5 Limitations and Future Directions

We acknowledge several limitations that define future research directions:

1. **Scope restriction**: Initial validation on discrete pattern sets; extension to continuous distributions requires separate investigation
2. **Computational scaling**: Stage 2 trajectory-aware enhancement may introduce overhead for large-scale applications
3. **Theoretical gaps**: The cross-domain analogy from dynamical systems, while well-motivated, requires formal proof of the noise-attractor relationship

Future work will extend validation to larger-scale models and datasets, develop theoretical guarantees for the control mechanism, and explore integration with text-conditioned generation where the memory-generation trade-off has significant implications for copyright and creativity.