# Research Proposal

## Title: Understanding the Disconnect Between Loss Landscape Flatness and Generalization in Large-Scale Models: Towards Scale-Aware Generalization Theory

---

## 1. Introduction

### Background

The relationship between loss landscape geometry and generalization has been a cornerstone of deep learning theory for over two decades. The influential work of Hochreiter and Schmidhuber (1997) first proposed that "flat minima" in the loss landscape correspond to solutions with better generalization properties. This intuition has since shaped both theoretical developments and practical algorithm design, leading to optimizers like Sharpness-Aware Minimization (SAM) that explicitly seek flat regions of the loss landscape.

The theoretical foundation for the flatness-generalization connection stems from PAC-Bayesian bounds, which suggest that solutions residing in flat basins permit larger perturbations without significantly increasing the loss, implying robustness and better generalization. This perspective has been reinforced by observations that stochastic gradient descent (SGD) with small batch sizes tends to find flatter minima compared to large batch training, and that SGD noise acts as an effective regularizer favoring flat solutions.

However, the advent of large-scale models, particularly Large Language Models (LLMs) with billions of parameters, has revealed significant cracks in this theoretical edifice. Recent empirical studies have documented troubling inconsistencies: (1) LLMs frequently converge to sharp minima yet demonstrate remarkable generalization capabilities across diverse tasks; (2) traditional flatness measures exhibit scale sensitivity and can be artificially manipulated through reparameterization without affecting actual generalization performance; and (3) models trained with vastly different batch sizes—and consequently different flatness characteristics—achieve comparable generalization performance. Furthermore, recent work by Mason-Williams et al. (2025) demonstrates that sharp minima can emerge under regularization and coincide with improved generalization, calibration, and robustness.

These observations suggest that the flatness-generalization hypothesis, while potentially valid in certain regimes, fails to capture the full picture of generalization in modern deep learning systems. The work by Dinh et al. (2017) formally demonstrated that network symmetries allow construction of equivalent models with arbitrarily sharp minima, fundamentally challenging whether flatness can be meaningfully related to generalization without additional constraints.

### Research Objectives

This research aims to systematically investigate the disconnect between flatness-based generalization theory and practical outcomes in large-scale deep learning. Our specific objectives are:

1. **Empirical Characterization**: Conduct controlled experiments across model scales (from small CNNs to billion-parameter transformers) to precisely identify regimes where flatness-generalization correlations hold, weaken, or completely break down.

2. **Development of Scale-Aware Metrics**: Design novel flatness measures that account for parameter count, layer-wise heterogeneity, and architectural properties to provide more reliable generalization predictions.

3. **Theoretical Framework Construction**: Develop a refined theoretical framework introducing "effective flatness" that incorporates the interaction between model architecture, optimization trajectory, and data structure.

4. **Practical Guidelines**: Establish actionable recommendations for practitioners regarding when flatness-based insights apply and when alternative indicators should be prioritized.

### Significance

This research addresses a fundamental gap between deep learning theory and practice, directly aligned with the workshop's core mission. By identifying when and why flatness-based theories fail, we contribute to: (i) more honest assessment of existing theoretical tools, (ii) development of tighter, practically relevant generalization bounds, (iii) informed application of flatness-seeking optimizers, and (iv) inspiration for new theoretical frameworks that better capture the generalization mechanisms in modern architectures.

---

## 2. Methodology

Our methodology comprises three interconnected components: systematic empirical investigation, development of scale-aware flatness metrics, and construction of a refined theoretical framework.

### 2.1 Systematic Empirical Investigation

#### Model Selection and Training Setup

We will conduct experiments across a carefully designed spectrum of model architectures and scales:

- **Small-scale models**: ResNet-18/34 on CIFAR-10/100, with approximately $10^7$ parameters
- **Medium-scale models**: ResNet-50/101 and ViT-B on ImageNet, with approximately $10^8$ parameters  
- **Large-scale models**: GPT-2 variants (124M, 355M, 774M, 1.5B parameters) on language modeling tasks
- **Very large-scale models**: Open-source LLMs (Llama-2 7B/13B) evaluated via fine-tuning experiments

For each model class, we will vary:
- **Batch size**: $\{32, 128, 512, 2048, 8192\}$
- **Learning rate schedules**: Constant, cosine annealing, warmup+decay
- **Optimizers**: SGD, Adam, AdamW, SAM, GAM
- **Regularization**: Weight decay $\in \{0, 10^{-4}, 10^{-3}, 10^{-2}\}$, dropout, data augmentation

#### Flatness Metrics

We will compute multiple complementary flatness measures for each trained model:

1. **Hessian-based measures**:
   - Top-$k$ eigenvalues of the Hessian: $\lambda_1, \lambda_2, \ldots, \lambda_k$
   - Trace of the Hessian: $\text{Tr}(H) = \sum_{i=1}^{d} \lambda_i$
   - Spectral norm: $\|H\|_2 = \lambda_{\max}$

2. **PAC-Bayes sharpness**: Following Keskar et al. (2017),
   $$S_{\text{PAC}}(\theta, \rho) = \max_{\|\epsilon\|_2 \leq \rho} \left[ L(\theta + \epsilon) - L(\theta) \right]$$

3. **Average-case perturbation sensitivity**:
   $$S_{\text{avg}}(\theta, \sigma) = \mathbb{E}_{\epsilon \sim \mathcal{N}(0, \sigma^2 I)} \left[ L(\theta + \epsilon) - L(\theta) \right]$$

4. **Soft-rank Hessian measure** (following Shoham et al., 2025):
   $$R_{\tau}(H) = \sum_{i=1}^{d} \frac{\lambda_i^2}{\lambda_i^2 + \tau^2}$$

5. **First-order flatness** (Zhang et al., 2023):
   $$F_1(\theta, \rho) = \max_{\|\epsilon\|_2 \leq \rho} \|\nabla L(\theta + \epsilon)\|_2$$

#### Generalization Gap Measurement

The true generalization gap is computed as:
$$G(\theta) = L_{\text{test}}(\theta) - L_{\text{train}}(\theta)$$

For language models, we additionally measure perplexity on held-out validation sets and performance on downstream tasks via zero-shot and few-shot evaluation.

#### Statistical Analysis Protocol

For each (model, training configuration) pair, we will:
1. Train 5 independent runs with different random seeds
2. Compute all flatness metrics at convergence
3. Measure generalization gaps
4. Compute Spearman and Pearson correlations between each flatness metric and generalization
5. Perform regression analysis to quantify predictive power: $R^2$ values for $G(\theta) \sim f(S(\theta))$

### 2.2 Scale-Aware Flatness Metrics

Based on preliminary analysis, we will develop novel flatness measures addressing identified limitations:

#### Normalized Spectral Sharpness

We propose normalizing Hessian eigenvalues by parameter count:
$$S_{\text{norm}}(\theta) = \frac{1}{d} \sum_{i=1}^{k} \lambda_i$$

where $d$ is the total parameter count and $k$ is chosen adaptively.

#### Layer-Wise Heterogeneous Flatness

Recognizing that different layers contribute differently to generalization, we define:
$$S_{\text{hetero}}(\theta) = \sum_{\ell=1}^{L} w_\ell \cdot S_\ell(\theta_\ell)$$

where $S_\ell$ is a layer-specific flatness measure, $\theta_\ell$ are parameters in layer $\ell$, and $w_\ell$ are learnable or architecture-dependent weights. We will investigate:
$$w_\ell = \frac{d_\ell}{\sum_{\ell'} d_{\ell'}} \quad \text{(parameter-proportional)}$$
$$w_\ell = \frac{\|\nabla_{\theta_\ell} L\|_2}{\sum_{\ell'} \|\nabla_{\theta_{\ell'}} L\|_2} \quad \text{(gradient-proportional)}$$

#### Reparameterization-Invariant Flatness

Building on Petzka et al. (2019), we construct measures invariant to positive rescaling:
$$S_{\text{inv}}(\theta) = \frac{\text{Tr}(H(\theta))}{L(\theta)^2}$$

and investigate volume-based measures that remain invariant under the symmetry group of the network.

#### Effective Flatness with Data Dependence

We propose conditioning flatness on the data distribution:
$$S_{\text{eff}}(\theta; \mathcal{D}) = \mathbb{E}_{(x,y) \sim \mathcal{D}} \left[ \text{Tr}\left( \nabla^2_\theta \ell(\theta; x, y) \right) \right]$$

This measure captures how flatness varies across the data manifold rather than treating it as a single scalar.

### 2.3 Theoretical Framework: Effective Flatness

We develop a theoretical framework that decomposes generalization into flatness-dependent and flatness-independent components:

#### Decomposition Theorem (Proposed)

We conjecture and aim to prove that for a model $f_\theta$ trained on distribution $\mathcal{D}$:
$$G(\theta) \leq \underbrace{\alpha(d, n) \cdot S_{\text{eff}}(\theta)}_{\text{flatness-dependent}} + \underbrace{\beta(\mathcal{A}, \mathcal{D}) \cdot C(\theta)}_{\text{architecture-data term}} + \underbrace{\gamma \cdot \Omega(\theta)}_{\text{trajectory term}}$$

where:
- $\alpha(d, n)$ captures the scaling behavior with parameter count $d$ and sample size $n$
- $\beta(\mathcal{A}, \mathcal{D})$ encodes architecture-data alignment
- $C(\theta)$ measures model complexity independent of local geometry
- $\Omega(\theta)$ captures optimization trajectory properties

#### Scale-Dependent Flatness Relevance

We hypothesize that:
$$\alpha(d, n) = \begin{cases} \Theta(1) & \text{if } d = O(n^c), c < 1 \\ o(1) & \text{if } d = \Omega(n^c), c \geq 1 \end{cases}$$

This formalizes the intuition that flatness becomes less predictive in the highly overparameterized regime characteristic of modern LLMs.

### 2.4 Experimental Validation of Theoretical Framework

To validate our theoretical framework, we will:

1. **Ablation studies**: Systematically vary $d/n$ ratios while controlling other factors
2. **Controlled interventions**: Apply flatness-modifying techniques (SAM, weight perturbation) and measure generalization changes
3. **Architecture comparisons**: Compare flatness-generalization relationships across CNNs, Transformers, and MLPs of matched parameter counts
4. **Trajectory analysis**: Track flatness evolution during training and correlate with final generalization

#### Evaluation Metrics

- **Correlation coefficients**: Spearman's $\rho$ and Pearson's $r$ between proposed metrics and generalization gap
- **Predictive accuracy**: $R^2$ and RMSE for generalization gap prediction
- **Regime identification accuracy**: Correctly classifying when flatness-based predictions are reliable
- **Bound tightness**: For theoretical bounds, measure gap between bound and actual generalization

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Empirical Map of Flatness-Generalization Relationship**: A comprehensive characterization identifying:
   - Model scale thresholds where traditional flatness measures lose predictive power
   - Architecture-specific patterns (CNNs vs. Transformers vs. MLPs)
   - Training condition effects (batch size, optimizer, regularization)

2. **Suite of Scale-Aware Flatness Metrics**: Novel measures with:
   - Demonstrated correlation with generalization across scales
   - Computational tractability for large models
   - Reparameterization invariance

3. **Refined Theoretical Framework**: Including:
   - Formal characterization of when flatness bounds are tight
   - New generalization bounds incorporating effective flatness
   - Scaling laws for flatness relevance

4. **Practical Guidelines**: Decision framework for practitioners specifying:
   - When to use flatness-seeking optimizers (SAM, GAM)
   - Alternative indicators for large-scale models
   - Model selection criteria beyond flatness

### Impact

**Theoretical Impact**: This work will fundamentally reshape understanding of the flatness-generalization relationship, providing nuanced characterization that resolves apparent contradictions in the literature. Our theoretical framework will inspire new directions in generalization theory that better account for modern architectural and scale considerations.

**Practical Impact**: Practitioners will gain actionable insights on when flatness-based intuitions apply, preventing misguided optimization strategies for large-scale models. This could improve efficiency in LLM training by avoiding unnecessary computational overhead from flatness-seeking methods when they provide no benefit.

**Methodological Impact**: The scale-aware metrics we develop will become standard tools for model analysis, providing more reliable generalization predictions across the full spectrum of modern deep learning systems.

**Community Impact**: By rigorously documenting the gap between theory and practice, we contribute to the workshop's mission of raising awareness and inspiring solutions, fostering a more honest dialogue about the limitations and applicability of existing theoretical frameworks.

---

## References

- Dinh, L., et al. (2017). Sharp Minima Can Generalize For Deep Nets.
- Mason-Williams, I., et al. (2025). A Function Centric Perspective On Flat and Sharp Minima.
- Petzka, H., et al. (2019). A Reparameterization-Invariant Flatness Measure for Deep Neural Networks.
- Shoham, N., et al. (2025). Flatness After All?
- Zhang, X., et al. (2023). Gradient Norm Aware Minimization Seeks First-Order Flatness and Improves Generalization.