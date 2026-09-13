# Research Proposal: Diversity-Aware Synthetic Data Generation with Automatic Distribution Calibration

## 1. Introduction

### Background

The remarkable success of modern machine learning models is fundamentally tied to access to large-scale, high-quality training data. However, accessing such data increasingly faces significant barriers including privacy regulations (GDPR, HIPAA), copyright concerns, fairness requirements, and safety considerations. Synthetic data generation has emerged as a promising solution to these data access challenges, with generative AI models demonstrating impressive capabilities in producing realistic samples across various domains including text, images, and structured data.

Despite this promise, recent research has uncovered critical limitations in synthetic data that threaten its viability as a replacement for real data. Zverev et al. (2025) demonstrate that training models iteratively on synthetic data introduces significant bias and variance, leading to distribution drift and eventual model collapse. Shi et al. (2025) further characterize this phenomenon as a transition from generalization to memorization, driven by declining entropy in synthetic training data. Kazdan et al. (2024) confirm that replacing real data entirely with successive generations of synthetic data leads to model collapse, though they note that accumulating synthetic data alongside real data can prevent this degradation.

A particularly concerning yet underexplored limitation is **mode collapse** and **distribution drift** in synthetic data generation. Synthetic data generators, whether based on GANs, diffusion models, or large language models, tend to produce samples that cluster around common patterns while systematically underrepresenting rare but critical edge cases. This limitation is especially problematic in high-stakes domains such as healthcare diagnostics, autonomous vehicle systems, and financial fraud detection, where failures on tail distributions can have severe consequences.

### Research Objectives

This research proposes **AutoCalib**, a comprehensive framework for diversity-aware synthetic data generation with automatic distribution calibration. Our primary objectives are:

1. **Develop principled methods** for detecting distributional gaps between synthetic and target data distributions without requiring direct access to sensitive real data
2. **Design adaptive regeneration mechanisms** that guide synthetic data generators to adequately cover underrepresented regions of the data distribution
3. **Create verification protocols** that certify distributional coverage with statistical guarantees
4. **Validate the framework** across multiple domains and demonstrate improved downstream model robustness

### Significance

This research addresses fundamental reliability concerns that currently limit synthetic data's ability to serve as a trustworthy substitute for real data. By providing automated mechanisms to detect and correct distributional mismatches, AutoCalib enables practitioners to generate synthetic datasets that maintain the diversity and coverage properties essential for training robust models. This is particularly significant for sensitive domains where real data access is restricted but model reliability is paramount.

## 2. Methodology

### 2.1 Overview of the AutoCalib Framework

AutoCalib consists of three interconnected components: (1) Distribution Gap Detection, (2) Guided Regeneration, and (3) Coverage Verification. The framework operates iteratively, progressively improving the synthetic dataset's distributional properties until coverage certification is achieved.

### 2.2 Distribution Gap Detection

The first component identifies regions where synthetic data under-represents or over-represents the target distribution. Crucially, our approach operates without direct access to raw real data, relying instead on summary statistics, pretrained embeddings, or differentially private representations.

**Kernel Density Ratio Estimation**: We employ kernel-based density ratio estimation to compare synthetic and target distributions. Let $p(x)$ denote the (unknown) target distribution and $q(x)$ the synthetic distribution. We estimate the density ratio $r(x) = p(x)/q(x)$ using the following approach:

Given synthetic samples $\{x_i^{syn}\}_{i=1}^n$ and target distribution statistics (mean $\mu_p$, covariance $\Sigma_p$, and higher-order moments), we construct a kernel-based estimator:

$$\hat{r}(x) = \sum_{j=1}^m \alpha_j K(x, c_j)$$

where $K(\cdot, \cdot)$ is a Gaussian RBF kernel with bandwidth $\sigma$, $\{c_j\}_{j=1}^m$ are representative centroids, and $\alpha_j$ are coefficients learned by minimizing:

$$\mathcal{L}_{ratio} = \frac{1}{2}\mathbb{E}_{q}[\hat{r}(x)^2] - \mathbb{E}_{p}[\hat{r}(x)]$$

The expectation under $p$ is approximated using moment-matching constraints derived from available summary statistics.

**Embedding-Based Gap Detection**: For domains where pretrained encoders exist (e.g., CLIP for images, sentence transformers for text), we project both synthetic samples and real data summaries into a shared embedding space $\mathcal{Z}$. We partition $\mathcal{Z}$ into regions using a Gaussian Mixture Model and compute coverage scores:

$$C_k = \frac{|\{z_i^{syn} : z_i^{syn} \in \mathcal{R}_k\}|/n}{\pi_k}$$

where $\mathcal{R}_k$ is the $k$-th region and $\pi_k$ is its expected probability mass under the target distribution. Regions with $C_k < \tau_{low}$ are flagged as underrepresented, while regions with $C_k > \tau_{high}$ indicate overrepresentation.

**Maximum Mean Discrepancy (MMD) Analysis**: We compute localized MMD scores to quantify distributional differences:

$$\text{MMD}^2_k = \mathbb{E}_{x,x'\sim p_k}[K(x,x')] + \mathbb{E}_{y,y'\sim q_k}[K(y,y')] - 2\mathbb{E}_{x\sim p_k, y\sim q_k}[K(x,y)]$$

where $p_k$ and $q_k$ are the target and synthetic distributions restricted to region $k$.

### 2.3 Guided Regeneration

Based on detected gaps, we employ targeted generation strategies to improve distributional coverage.

**Prompt-Based Conditioning for Language Models**: For text or multimodal generators, we construct targeted prompts that emphasize underrepresented characteristics. Given gap analysis results identifying sparse feature combinations $\{f_1, f_2, ..., f_k\}$, we generate conditioning prompts:

$$\text{prompt}_j = \text{Template}(f_1^{(j)}, f_2^{(j)}, ..., f_k^{(j)}) + \text{DiversityInstruction}$$

where DiversityInstruction encourages variation within the specified constraints.

**Latent Space Manipulation for Diffusion/GAN Models**: For generative models with explicit latent spaces, we employ guided sampling. Let $z \sim \mathcal{N}(0, I)$ be the standard latent code. We define a guidance function:

$$g(z) = \sum_{k \in \mathcal{U}} w_k \cdot \phi_k(G(z))$$

where $\mathcal{U}$ is the set of underrepresented regions, $w_k$ is proportional to the coverage deficit, and $\phi_k$ measures membership in region $k$. Modified sampling follows:

$$z^* = z + \eta \nabla_z g(z)$$

**Importance Reweighting**: For scenarios where regeneration is expensive, we assign importance weights to existing synthetic samples:

$$w(x_i) = \min\left(\hat{r}(x_i), M\right) / \sum_j \min\left(\hat{r}(x_j), M\right)$$

where $M$ is a clipping threshold for stability. Downstream models train on the reweighted dataset.

### 2.4 Coverage Verification

The verification module provides statistical guarantees on distributional coverage using conformal prediction principles, building on recent advances by Zheng & Zhu (2024).

**Conformal Coverage Certificates**: We define a coverage function $\mathcal{C}: \mathcal{X} \rightarrow [0,1]$ that maps each point to its local coverage quality. Using a held-out calibration set with known properties, we compute non-conformity scores:

$$s_i = 1 - \mathcal{C}(x_i)$$

The $(1-\alpha)$ quantile of these scores, denoted $\hat{q}_{1-\alpha}$, defines our coverage threshold. A synthetic dataset achieves certified coverage if:

$$\mathbb{P}_{x \sim p}\left[\mathcal{C}(x) \geq 1 - \hat{q}_{1-\alpha}\right] \geq 1 - \alpha$$

**Regional Coverage Bounds**: For each identified region $k$, we compute coverage bounds:

$$\hat{C}_k^{lower} = \hat{C}_k - z_{1-\alpha/2K}\sqrt{\frac{\hat{C}_k(1-\hat{C}_k)}{n_k}}$$

where $K$ is the number of regions and $n_k$ is the sample count in region $k$. The synthetic dataset passes verification if $\hat{C}_k^{lower} \geq \tau_{min}$ for all regions.

### 2.5 Iterative Calibration Algorithm

The complete AutoCalib algorithm proceeds as follows:

```
Algorithm: AutoCalib
Input: Generator G, target statistics S_target, coverage threshold τ, max iterations T
Output: Calibrated synthetic dataset D_syn

1. Initialize D_syn ← Generate(G, n_initial)
2. For t = 1 to T:
   a. Compute embeddings Z_syn ← Encode(D_syn)
   b. Estimate density ratios R ← DensityRatioEstimation(Z_syn, S_target)
   c. Identify gaps: U ← {k : C_k < τ_low}, O ← {k : C_k > τ_high}
   d. If U = ∅ and CoverageVerification(D_syn, S_target) passes:
      Return D_syn
   e. Generate targeted samples: D_new ← GuidedGeneration(G, U, n_targeted)
   f. Update dataset: D_syn ← D_syn ∪ D_new
   g. Apply importance reweighting if needed
3. Return D_syn with coverage report
```

### 2.6 Experimental Design

**Datasets and Domains**: We evaluate AutoCalib across three domains:
- **Healthcare**: MIMIC-III clinical notes with rare disease conditions
- **Computer Vision**: Long-tailed ImageNet variants (ImageNet-LT)
- **Tabular Data**: UCI Adult dataset with minority demographic groups

**Baseline Methods**: 
- Standard synthetic generation without calibration
- Rejection sampling based on estimated densities
- SMOTE and its variants for oversampling
- Entropy-based selection (Shi et al., 2025)

**Evaluation Metrics**:
1. **Distribution Quality**: MMD, Fréchet Distance, Coverage and Density metrics
2. **Downstream Performance**: Accuracy on tail classes, worst-group accuracy, balanced accuracy
3. **Robustness**: Performance under distribution shift, adversarial evaluation
4. **Efficiency**: Computational overhead, sample efficiency

**Experimental Protocol**: For each domain, we:
1. Split real data into reference (for statistics extraction) and held-out test sets
2. Generate synthetic data using baseline and AutoCalib approaches
3. Train identical downstream models on each synthetic dataset
4. Evaluate on held-out test sets with emphasis on tail distribution performance

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Improvements**: Based on preliminary analysis and related work, we anticipate:
- 15-30% improvement in tail-class accuracy compared to uncalibrated synthetic data
- 20-40% reduction in worst-group error rates
- Achieving certified coverage guarantees with 95% confidence across 90%+ of the data distribution
- Computational overhead below 20% of base generation cost

**Methodological Contributions**:
- First principled framework for automatic distributional calibration without direct real data access
- Novel combination of density ratio estimation with conformal prediction for coverage certification
- Generalizable approach applicable across generative model architectures (LLMs, diffusion models, GANs)

**Empirical Insights**:
- Characterization of failure modes in synthetic data generation across domains
- Understanding of trade-offs between coverage, diversity, and sample quality
- Guidelines for practitioners on when and how to apply distributional calibration

### Broader Impact

**Enabling Trustworthy Synthetic Data**: By providing mechanisms to detect and correct distributional gaps with statistical guarantees, AutoCalib addresses fundamental reliability concerns that currently limit synthetic data adoption. This enables organizations to confidently use synthetic data in high-stakes applications where real data access is restricted.

**Advancing Fair and Robust ML**: The explicit focus on tail distributions and underrepresented regions directly addresses fairness concerns in machine learning. Models trained on AutoCalib-generated data will exhibit more equitable performance across demographic groups and edge cases.

**Facilitating Privacy-Preserving ML**: By operating without direct access to real data (using only summary statistics or differentially private representations), AutoCalib complements existing privacy-preserving methods like federated learning and differential privacy.

**Domain-Specific Applications**: The framework's flexibility enables application across critical domains:
- Healthcare: Generating diverse patient cohorts for rare disease research
- Autonomous Systems: Creating comprehensive edge-case scenarios for safety validation
- Finance: Producing representative fraud patterns for detection systems

### Limitations and Future Directions

We acknowledge several limitations that warrant future investigation:
- Reliance on meaningful summary statistics from the target distribution
- Potential computational costs for very high-dimensional data
- Need for domain-specific encoder selection

Future work will explore integration with federated learning systems, extension to streaming data scenarios, and theoretical analysis of convergence guarantees.

## Conclusion

This proposal presents AutoCalib, a comprehensive framework for addressing the critical challenges of mode collapse and distribution drift in synthetic data generation. By combining kernel-based distribution gap detection, guided regeneration mechanisms, and conformal prediction-based coverage verification, AutoCalib provides the first principled approach to automatic distributional calibration for synthetic data. The successful completion of this research will significantly advance our ability to use synthetic data as a reliable substitute for real data, ultimately helping solve the data access problem in machine learning while maintaining model robustness and fairness.