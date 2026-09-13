# Research Proposal: Curriculum-Guided Diffusion Samplers for Multi-Modal Boltzmann Distributions

## 1. Introduction

### Background

Sampling from high-dimensional probability distributions defined by unnormalized densities constitutes a fundamental problem in computational science, with applications spanning molecular dynamics simulation, Bayesian inference, statistical physics, and modern generative modeling. Of particular importance are Boltzmann distributions of the form $p(x) \propto \exp(-U(x)/k_BT)$, where $U(x)$ represents an energy function. These distributions frequently exhibit complex multi-modal structures with modes separated by high energy barriers, making accurate sampling extraordinarily challenging.

Classical Markov Chain Monte Carlo (MCMC) methods, while asymptotically correct, suffer from poor mixing between isolated modes, requiring exponentially long simulation times to achieve ergodicity. Recent advances in learning-based samplers, particularly diffusion-based approaches, have shown promise in accelerating sampling by learning transport maps from simple distributions to complex targets. Methods such as the Adjoint Schrödinger Bridge Sampler (ASBS) and Learned Reference-based Diffusion Sampler (LRDS) have demonstrated effectiveness on various challenging distributions. However, these approaches frequently suffer from mode collapse—a phenomenon where the learned sampler fails to discover or appropriately weight all modes of the target distribution.

The challenge is particularly acute in molecular systems where accurate multi-modal sampling is essential for computing thermodynamic quantities such as free energy differences, binding affinities, and conformational equilibria. For instance, in alanine dipeptide—a benchmark system in molecular dynamics—the Ramachandran plot exhibits multiple metastable states whose relative populations directly determine experimentally observable properties. Current methods often fail to capture correct mode weights, leading to biased estimates of these critical quantities.

### Research Objectives

This research proposes a novel curriculum learning framework for training diffusion-based samplers on multi-modal unnormalized densities. Our primary objectives are:

1. **Develop a principled curriculum strategy** that decomposes the challenging multi-modal sampling problem into a sequence of progressively harder subproblems, enabling stable training and comprehensive mode discovery.

2. **Design importance-weighted training objectives** that ensure correct relative mode weights are preserved throughout the curriculum, addressing the critical challenge of accurate mode ratio estimation.

3. **Demonstrate superior performance** on challenging molecular benchmarks, including alanine dipeptide and Lennard-Jones clusters, with particular emphasis on accurate free energy estimation.

### Significance

This research addresses a critical gap at the intersection of classical sampling methods and modern machine learning approaches. By bridging curriculum learning principles with diffusion-based sampling, we aim to enable reliable sampling from complex multi-modal distributions that have remained intractable. The resulting methodology will have immediate applications in computational chemistry and drug discovery, where accurate conformational sampling is essential, and broader implications for any domain requiring sampling from unnormalized multi-modal densities.

## 2. Methodology

### 2.1 Problem Formulation

Consider a target Boltzmann distribution defined by an energy function $U(x)$:

$$p_{\text{target}}(x) = \frac{1}{Z} \exp(-U(x))$$

where $Z = \int \exp(-U(x)) dx$ is the intractable normalizing constant and we have absorbed the temperature into the energy function. Our goal is to learn a diffusion-based sampler that can generate samples from $p_{\text{target}}(x)$ with accurate mode coverage and correct relative mode weights.

### 2.2 Curriculum Distribution Family

We construct a family of interpolating distributions between a tractable base distribution $p_0(x)$ (typically Gaussian) and the target distribution $p_{\text{target}}(x)$ using a geometric tempering scheme:

$$p_\lambda(x) \propto p_0(x)^{1-\lambda} \cdot p_{\text{target}}(x)^\lambda = p_0(x)^{1-\lambda} \cdot \exp(-\lambda U(x))$$

where $\lambda \in [0, 1]$ controls the curriculum stage. At $\lambda = 0$, we have the tractable base distribution; at $\lambda = 1$, we recover the target. Critically, for intermediate values, the energy barriers between modes are effectively reduced by a factor of $\lambda$, facilitating inter-mode transitions.

We define a curriculum schedule $\{\lambda_k\}_{k=0}^K$ with $\lambda_0 = 0$ and $\lambda_K = 1$. The schedule is adaptively determined based on an effective sample size (ESS) criterion:

$$\lambda_{k+1} = \max\left\{\lambda : \text{ESS}\left(\frac{p_\lambda}{p_{\lambda_k}}\right) \geq \tau \cdot N\right\}$$

where $\tau \in (0, 1)$ is a threshold parameter (typically 0.5) and $N$ is the number of samples.

### 2.3 Diffusion Sampler Architecture

At each curriculum stage $k$, we train a score-based diffusion model. Following the denoising score matching framework, we consider a forward diffusion process:

$$dx_t = f(t)x_t \, dt + g(t) \, dW_t$$

where $f(t)$ and $g(t)$ are drift and diffusion coefficients, and $W_t$ is a Wiener process. The corresponding reverse-time process is:

$$dx_t = \left[f(t)x_t - g(t)^2 \nabla_x \log p_t(x_t)\right] dt + g(t) \, d\bar{W}_t$$

We parameterize the score function $s_\theta(x_t, t) \approx \nabla_x \log p_t(x_t)$ using a neural network with architecture inspired by recent advances in molecular generative modeling, incorporating equivariant features where appropriate.

### 2.4 Curriculum Training Algorithm

**Stage 1: Initialization ($k=0$)**

Train an initial diffusion sampler $s_{\theta_0}$ on the base distribution $p_0(x)$ using standard denoising score matching:

$$\mathcal{L}_0(\theta) = \mathbb{E}_{t, x_0 \sim p_0, x_t | x_0}\left[\|s_\theta(x_t, t) - \nabla_{x_t} \log p(x_t | x_0)\|^2\right]$$

**Stage $k > 0$: Curriculum Progression**

For each subsequent stage, we employ an importance-weighted training objective that leverages samples from the previous stage:

1. **Sample Generation**: Generate $N$ samples $\{x^{(i)}\}_{i=1}^N$ using the sampler from stage $k-1$.

2. **Importance Weight Computation**: Compute unnormalized importance weights:
$$\tilde{w}^{(i)} = \frac{p_{\lambda_k}(x^{(i)})}{p_{\lambda_{k-1}}(x^{(i)})} = \exp\left(-(\lambda_k - \lambda_{k-1})U(x^{(i)}) + (\lambda_k - \lambda_{k-1})\log p_0(x^{(i)})\right)$$

3. **Self-Normalized Weights**: Compute normalized weights $w^{(i)} = \tilde{w}^{(i)} / \sum_j \tilde{w}^{(j)}$.

4. **Importance-Weighted Score Matching Loss**:
$$\mathcal{L}_k(\theta) = \sum_{i=1}^N w^{(i)} \mathbb{E}_{t, x_t | x^{(i)}}\left[\|s_\theta(x_t, t) - \nabla_{x_t} \log p(x_t | x^{(i)})\|^2\right]$$

5. **Regularization**: To prevent overfitting to high-weight samples and encourage mode exploration, we add an entropy regularization term:
$$\mathcal{L}_{\text{reg}}(\theta) = -\alpha \cdot \mathbb{E}_{x \sim p_\theta}\left[\log p_{\lambda_k}(x)\right]$$

The complete training objective becomes:
$$\mathcal{L}_{\text{total}}(\theta) = \mathcal{L}_k(\theta) + \mathcal{L}_{\text{reg}}(\theta)$$

**Algorithm: Curriculum-Guided Diffusion Sampler (CGDS)**

```
Input: Target energy U(x), base distribution p_0, schedule threshold τ, stages K
Output: Trained diffusion sampler s_θ

1. Initialize θ_0 by training on p_0
2. Set λ_0 = 0, k = 0
3. While λ_k < 1:
   a. Generate samples {x^(i)} from s_{θ_k}
   b. Compute adaptive λ_{k+1} using ESS criterion
   c. Compute importance weights w^(i)
   d. Initialize θ_{k+1} ← θ_k (warm start)
   e. Train s_{θ_{k+1}} using L_total with early stopping
   f. k ← k + 1
4. Return s_{θ_K}
```

### 2.5 Mode Weight Correction via Sequential Monte Carlo

To ensure accurate final mode weights, we incorporate a Sequential Monte Carlo (SMC) correction step. After training, we run SMC with the learned sampler as the proposal distribution:

$$\hat{Z}_{\lambda_k} / \hat{Z}_{\lambda_{k-1}} = \frac{1}{N} \sum_{i=1}^N \tilde{w}^{(i)}$$

The product of these ratios provides an unbiased estimate of the normalizing constant ratio, enabling accurate free energy computation.

### 2.6 Experimental Design

**Benchmark Systems:**

1. **Gaussian Mixture Models (GMM)**: 2D and 10D mixtures with varying mode separations to validate basic mode coverage.

2. **Müller-Brown Potential**: A 2D benchmark with three metastable states commonly used in enhanced sampling literature.

3. **Alanine Dipeptide**: A 22-atom molecular system in explicit solvent with well-characterized Ramachandran plot modes.

4. **Lennard-Jones Clusters (LJ-13, LJ-38)**: Challenging molecular benchmarks with hundreds of local minima.

**Evaluation Metrics:**

1. **Mode Coverage**: Percentage of known modes discovered by the sampler.

2. **Total Variation Distance**: $\text{TV}(p_\theta, p_{\text{target}}) = \frac{1}{2}\int |p_\theta(x) - p_{\text{target}}(x)| dx$, estimated via kernel density estimation on low-dimensional projections.

3. **Relative Mode Weight Error**: For known modes $\{m_i\}$, compute:
$$\epsilon_{\text{weight}} = \sum_i \left|\frac{\hat{w}_i}{\sum_j \hat{w}_j} - \frac{w_i^*}{\sum_j w_j^*}\right|$$

4. **Free Energy Error**: $|\Delta \hat{F} - \Delta F^*|$ where $\Delta F = -k_BT \log(Z_A/Z_B)$.

5. **Effective Sample Size (ESS)**: Measure of sample efficiency relative to independent sampling.

**Baselines:**

- Parallel Tempering MCMC
- Flow Annealed Importance Sampling Bootstrap (FAB)
- Diffusion Generative Flow Sampler (DGFS)
- Learned Reference-based Diffusion Sampler (LRDS)
- Adjoint Schrödinger Bridge Sampler (ASBS)

**Implementation Details:**

Neural network architecture: U-Net with attention layers for 2D systems; SE(3)-equivariant graph neural networks for molecular systems. Training: Adam optimizer with learning rate $10^{-4}$, batch size 256, early stopping based on validation ESS. Curriculum: Adaptive schedule with $\tau = 0.5$, maximum 20 stages.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Mode Coverage**: We anticipate achieving >95% mode coverage on all benchmark systems, compared to 60-80% for existing diffusion-based methods on challenging multi-modal distributions.

2. **Accurate Mode Weights**: Relative mode weight errors below 5% on alanine dipeptide and LJ clusters, enabling reliable free energy estimation with errors <0.5 kcal/mol.

3. **Computational Efficiency**: 10-100× speedup over parallel tempering MCMC for achieving equivalent sampling quality, measured by effective samples per unit computation.

4. **Theoretical Insights**: Formal analysis of curriculum schedule design and convergence properties of importance-weighted diffusion training.

### Broader Impact

**Scientific Applications**: The ability to accurately sample from multi-modal Boltzmann distributions will enable more reliable predictions in drug discovery, materials science, and protein engineering. Accurate free energy estimation is crucial for predicting binding affinities, reaction rates, and phase transitions.

**Methodological Contributions**: The curriculum learning framework is general and can be extended to other generative modeling settings, including fine-tuning of diffusion models and large language models with complex reward landscapes.

**Community Resources**: We will release open-source implementations, trained models, and benchmark datasets to facilitate reproducibility and future research in learning-based sampling methods.

This research directly addresses the workshop themes of connecting sampling methods to optimal transport (through the diffusion framework), accelerating classical sampling with learning (via curriculum-guided training), and applications to natural sciences (molecular dynamics benchmarks). By tackling the fundamental challenge of multi-modal sampling, this work aims to advance the frontier of probabilistic inference methods.