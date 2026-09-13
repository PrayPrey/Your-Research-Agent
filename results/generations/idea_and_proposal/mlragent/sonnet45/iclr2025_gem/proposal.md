# Active Learning with Uncertainty-Aware Generative Models for Efficient Protein Fitness Landscape Exploration

## 1. Introduction

### Background

Protein engineering has emerged as a cornerstone technology for addressing critical challenges in medicine, biotechnology, and environmental sustainability. The ability to design proteins with enhanced or novel functions enables the development of superior therapeutics, industrial enzymes, and biosensors. Traditional protein engineering approaches, such as directed evolution, have achieved remarkable successes but are fundamentally limited by the vast combinatorial space of possible protein sequences—for a protein of just 100 amino acids, there are $20^{100} \approx 10^{130}$ possible sequences, far exceeding the number of atoms in the universe.

Recent advances in generative machine learning have opened unprecedented opportunities for rational protein design. Models such as variational autoencoders (VAEs), generative adversarial networks (GANs), and diffusion models have demonstrated the ability to generate novel protein sequences with desired structural and functional properties. These approaches leverage large-scale protein sequence and structure databases to learn the underlying principles of protein folding and function. However, a critical bottleneck persists: the gap between computational generation and experimental validation. While generative models can produce thousands of candidate sequences in silico, experimental characterization of even a single variant can cost hundreds to thousands of dollars and require days to weeks of laboratory work.

This disconnect is further exacerbated by the lack of reliable uncertainty quantification in most generative models. Current approaches typically produce point predictions without calibrated confidence estimates, making it difficult for experimentalists to prioritize which designs merit costly validation. Moreover, most protein design workflows operate in a "one-shot" paradigm, where models generate candidates without incorporating feedback from experimental results, missing opportunities for iterative refinement.

### Research Objectives

This research proposes an **active learning framework** that integrates uncertainty-quantified generative models with adaptive experimental design to efficiently navigate protein fitness landscapes. Our specific objectives are:

1. **Develop uncertainty-aware generative models** that provide calibrated confidence scores for generated protein sequences through ensemble-based and Bayesian approaches
2. **Design novel acquisition functions** tailored for protein engineering that optimally balance exploration and exploitation under experimental budget constraints
3. **Implement an iterative refinement protocol** that progressively improves both generation quality and uncertainty calibration through experimental feedback
4. **Validate the framework** on real wet-lab protein engineering tasks, demonstrating measurable improvements in experimental efficiency

### Significance

This research addresses fundamental challenges at the intersection of computational biology and experimental validation. The expected 3-5x reduction in experimental iterations needed to identify high-fitness variants would substantially lower the barrier for resource-limited laboratories to leverage generative ML, democratizing access to cutting-edge protein engineering capabilities. Beyond efficiency gains, the uncertainty-aware framework will provide experimentalists with actionable confidence estimates, enabling more informed decision-making about which designs to pursue.

The integration of active learning with generative protein design represents a paradigm shift from static, one-shot generation to dynamic, experiment-driven exploration. This approach aligns with the emerging recognition that effective biomolecular design requires tight coupling between computational and experimental workflows. By demonstrating this integration on therapeutically and industrially relevant tasks (enzyme engineering and antibody optimization), we will establish practical blueprints for translating generative ML advances into real-world impact.

## 2. Methodology

### 2.1 Uncertainty-Aware Generative Models

We will develop two complementary approaches for uncertainty quantification in protein sequence generation:

#### 2.1.1 Deep Ensemble Diffusion Models

Building on recent advances in diffusion models for protein design, we will implement an ensemble-based architecture. The forward diffusion process gradually adds noise to protein sequences:

$$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar{\alpha}_t}x_0, (1-\bar{\alpha}_t)I)$$

where $x_0$ represents the original protein sequence embedding, $x_t$ is the noised version at timestep $t$, and $\bar{\alpha}_t$ controls the noise schedule.

The reverse process learns to denoise through a neural network $\epsilon_\theta$:

$$p_\theta(x_{t-1}|x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t), \Sigma_\theta(x_t, t))$$

We will train an ensemble of $M=5$ independent diffusion models $\{\epsilon_{\theta_i}\}_{i=1}^M$ with different random initializations. For a generated sequence $s$, the epistemic uncertainty is quantified as:

$$\sigma_{epistemic}^2(s) = \frac{1}{M}\sum_{i=1}^M ||f_{\theta_i}(s) - \bar{f}(s)||^2$$

where $f_{\theta_i}(s)$ represents the predicted fitness from model $i$ and $\bar{f}(s)$ is the ensemble mean.

#### 2.1.2 Bayesian Variational Autoencoder

In parallel, we will develop a Bayesian VAE that places distributions over model weights. The standard VAE objective:

$$\mathcal{L}_{VAE} = \mathbb{E}_{q_\phi(z|x)}[\log p_\theta(x|z)] - D_{KL}(q_\phi(z|x) || p(z))$$

is extended to incorporate weight uncertainty through variational inference:

$$\mathcal{L}_{BVAE} = \mathbb{E}_{q(\theta)q(\phi)}[\mathcal{L}_{VAE}] - D_{KL}(q(\theta)||p(\theta)) - D_{KL}(q(\phi)||p(\phi))$$

This enables sampling multiple decoder parameterizations to estimate both aleatoric and epistemic uncertainty for generated sequences.

### 2.2 Fitness Prediction and Surrogate Modeling

To guide the generative process, we will train surrogate fitness models that predict experimental outcomes. We employ Gaussian Process (GP) regression with a specialized protein kernel:

$$k(s_i, s_j) = \sigma^2 \exp\left(-\frac{d(s_i, s_j)^2}{2l^2}\right)$$

where $d(s_i, s_j)$ is a learned distance metric in protein sequence space, combining evolutionary information (BLOSUM62 similarity) and structural embeddings from pre-trained protein language models (ESM-2).

The GP posterior provides both fitness predictions and uncertainty:

$$\mu(s_{new}) = k(s_{new}, S)^T(K + \sigma_n^2I)^{-1}y$$
$$\sigma^2(s_{new}) = k(s_{new}, s_{new}) - k(s_{new}, S)^T(K + \sigma_n^2I)^{-1}k(s_{new}, S)$$

where $S$ represents observed sequences and $y$ their measured fitness values.

### 2.3 Acquisition Functions for Protein Design

We propose three novel acquisition functions tailored for expensive protein engineering experiments:

#### 2.3.1 Uncertainty-Weighted Expected Improvement (UWEI)

$$\alpha_{UWEI}(s) = \text{EI}(s) \cdot w(\sigma_{model}(s), \sigma_{GP}(s))$$

where:
$$\text{EI}(s) = \mathbb{E}[\max(f(s) - f^+, 0)]$$
$$w(\sigma_m, \sigma_{GP}) = \frac{\sigma_m}{\sigma_m + \sigma_{GP} + \epsilon}$$

This balances exploiting high predicted fitness with exploring regions where the generative model is uncertain.

#### 2.3.2 Batch Diversity-Aware Selection

For selecting batches of $B$ sequences to test simultaneously:

$$S_{batch} = \arg\max_{|S|=B} \sum_{s \in S} \alpha(s) - \lambda \sum_{s_i, s_j \in S, i<j} \text{sim}(s_i, s_j)$$

where $\text{sim}(s_i, s_j)$ ensures diversity within the experimental batch and $\lambda$ controls the diversity-quality tradeoff.

#### 2.3.3 Cost-Aware Thompson Sampling

To account for varying experimental costs:

$$s^* = \arg\max_s \frac{\tilde{f}(s)}{c(s)^\gamma}$$

where $\tilde{f}(s)$ is sampled from the posterior distribution and $c(s)$ estimates experimental cost (e.g., expression difficulty, synthesis complexity), with $\gamma$ controlling cost sensitivity.

### 2.4 Iterative Active Learning Protocol

The complete workflow consists of the following algorithmic steps:

**Algorithm 1: Uncertainty-Aware Active Learning for Protein Design**

```
Input: Wild-type sequence s_wt, initial dataset D_0, budget T, batch size B
Initialize: Train generative model G and surrogate model M on D_0

For round t = 1 to T:
    1. Generate candidate pool C_t of N=1000 sequences using G
    2. For each s in C_t:
        - Compute σ_model(s) from generative model ensemble
        - Compute μ_M(s), σ_GP(s) from surrogate model M
        - Calculate acquisition score α(s)
    3. Select batch S_t of B sequences maximizing acquisition with diversity
    4. Perform wet-lab experiments to measure fitness f(s) for s in S_t
    5. Augment dataset: D_t = D_{t-1} ∪ {(s, f(s)) | s in S_t}
    6. Retrain generative model G on D_t
    7. Update surrogate model M with D_t
    8. Recalibrate uncertainty estimates using observed vs predicted fitness

Output: Best sequence s* = argmax_{s in ∪D_t} f(s)
```

### 2.5 Data Collection and Experimental Design

#### 2.5.1 Target Systems

We will validate the framework on two complementary experimental systems:

**System 1: TEM-1 β-lactamase enzyme engineering** (Exploitation-focused)
- Objective: Enhance antibiotic resistance to third-generation cephalosporins
- Initial dataset: Deep mutational scanning data (~4,000 variants)
- Fitness assay: Minimum inhibitory concentration (MIC) measurements
- Budget: 200 experimental validations across 4 active learning rounds

**System 2: Antibody affinity maturation** (Exploration-focused)
- Objective: Improve binding affinity to therapeutic target (PD-L1)
- Initial dataset: 500 characterized variants from library screening
- Fitness assay: Surface plasmon resonance (SPR) for $K_D$ measurement
- Budget: 150 experimental validations across 3-4 rounds

#### 2.5.2 Baseline Comparisons

We will compare our approach against:
1. **Random sampling**: Random selection from generative model outputs
2. **Greedy selection**: Top-predicted fitness by surrogate model only
3. **Standard active learning**: GP-based acquisition without generative model uncertainty
4. **ProSpero**: State-of-the-art active learning for protein design (see literature review)
5. **Directed evolution**: Traditional site-saturation mutagenesis

### 2.6 Evaluation Metrics

#### 2.6.1 Experimental Efficiency
- **Iterations to target fitness**: Number of rounds needed to achieve 2x, 5x, and 10x improvement over wild-type
- **Area under fitness curve**: Cumulative fitness discovered as a function of experimental budget
- **Success rate**: Fraction of tested variants exceeding target fitness threshold

#### 2.6.2 Uncertainty Calibration
- **Expected calibration error (ECE)**: 
$$ECE = \sum_{m=1}^M \frac{|B_m|}{n}|\text{acc}(B_m) - \text{conf}(B_m)|$$
where sequences are binned by predicted uncertainty
- **Negative log-likelihood**: $-\log p(y_{true}|s, \mathcal{D})$ for held-out experimental measurements
- **Sharpness**: Average width of 95% confidence intervals

#### 2.6.3 Generative Quality
- **Novelty**: Average sequence distance from training data
- **Structural validity**: Predicted folding stability (pLDDT scores from AlphaFold2)
- **Functional relevance**: Conservation of critical catalytic/binding residues

## 3. Expected Outcomes & Impact

### 3.1 Scientific Contributions

**Methodological Advances**: This research will establish the first comprehensive framework for uncertainty-aware generative protein design with experimental validation. Key innovations include:

1. **Calibrated uncertainty quantification** for protein generative models, addressing a critical gap in current approaches that typically provide point predictions without confidence estimates
2. **Domain-specific acquisition functions** that account for unique constraints of protein engineering (experimental cost heterogeneity, structural constraints, batch selection requirements)
3. **Demonstration of closed-loop integration** between generative ML and wet-lab experiments, providing a blueprint for future biomolecular design workflows

**Quantitative Performance Targets**:
- Achieve **3-5x reduction** in experimental iterations compared to baselines while reaching equivalent fitness improvements
- Demonstrate **well-calibrated uncertainty** with ECE < 0.10 for fitness predictions
- Generate variants with **>80% structural validity** as assessed by AlphaFold2, ensuring biological plausibility
- Identify at least **2-3 variants with >10x fitness improvement** over wild-type for each target system

### 3.2 Practical Impact

**Democratizing Protein Engineering**: By substantially reducing the number of required experiments, this framework will enable resource-constrained academic laboratories and small biotechnology companies to leverage state-of-the-art generative ML. A 3x reduction in experimental rounds translates to potential savings of $50,000-$150,000 per protein engineering campaign, making advanced capabilities accessible to a broader research community.

**Accelerating Therapeutic Development**: For antibody optimization, the ability to efficiently explore sequence space could reduce discovery timelines from 12-18 months to 6-9 months, accelerating the development of novel biologics for cancer immunotherapy, autoimmune diseases, and infectious diseases.

**Industrial Enzyme Engineering**: The framework's application to enzyme engineering will benefit industrial biotechnology, enabling rapid optimization of biocatalysts for sustainable chemical production, plastic degradation, and environmental remediation.

### 3.3 Broader Scientific Impact

**Bridging Computation and Experiment**: This work directly addresses the workshop's core mission of connecting computational and experimental perspectives in biomolecular design. By demonstrating tangible experimental validation, we will:

- Provide evidence-based guidance for experimentalists on when and how to integrate generative ML into their workflows
- Establish best practices for uncertainty communication between computational and experimental researchers
- Create open-source tools and datasets that facilitate future research at this interface

**Transferable Framework**: While validated on protein engineering, the uncertainty-aware active learning principles are broadly applicable to other biomolecular design domains including:
- RNA therapeutics design and optimization
- Small molecule drug discovery with synthesis constraints
- Metabolic pathway engineering
- Biomaterial design for tissue engineering

### 3.4 Deliverables

1. **Open-source software package**: Fully documented Python implementation including pre-trained models, acquisition functions, and experimental integration tools
2. **Curated datasets**: Public release of all experimental measurements with associated uncertainties, enabling benchmarking of future methods
3. **Validated protocols**: Detailed wet-lab protocols for implementing the active learning workflow
4. **High-impact publications**: Target submissions to Nature Biotechnology (through GEM fast-track) and complementary ML venues (NeurIPS, ICML)

### 3.5 Alignment with Workshop Themes

This proposal directly addresses multiple GEM workshop priorities:

**ML Track Contributions**:
- *Generative ML advancements*: Novel uncertainty-quantified diffusion models and Bayesian VAEs
- *Model interpretability*: Uncertainty decomposition revealing which sequence regions drive predictions
- *Modeling biomolecular data*: Specialized kernels and embeddings for protein fitness landscapes

**Biology Track Contributions**:
- *Wet lab experimental results*: Comprehensive validation on two complementary protein engineering systems
- *Adaptive experimental design*: Active learning protocol optimized for laboratory constraints
- *Benchmarks and datasets*: Public release of experimental data with uncertainty annotations

The iterative, experiment-driven nature of this research embodies the workshop's vision of tight integration between computational innovation and biological validation, positioning it as an ideal contribution to bridging the generative ML-experimental biology divide.