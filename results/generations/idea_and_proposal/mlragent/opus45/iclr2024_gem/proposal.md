# Research Proposal: Adaptive Experimental Design with Uncertainty-Aware Generative Models for Protein Engineering

## 1. Introduction

### Background

Protein engineering represents one of the most promising frontiers in biotechnology, with applications spanning therapeutic antibody development, industrial enzyme optimization, and sustainable biocatalysis. Recent advances in generative machine learning have revolutionized computational protein design, with models based on diffusion processes, flow matching, and autoregressive architectures demonstrating remarkable capabilities in generating novel protein sequences and structures. However, a critical disconnect persists between computational predictions and experimental validation—a gap that significantly limits the real-world impact of these powerful generative tools.

Current generative models for protein design typically operate in a one-shot paradigm: they generate thousands or even millions of candidate sequences, from which researchers must somehow select a manageable subset for experimental characterization. This approach suffers from fundamental inefficiencies. High-throughput experimental methods, while increasingly sophisticated, remain expensive and time-consuming. A single round of gene synthesis, expression, purification, and activity assay for 96 protein variants can cost thousands of dollars and require weeks of laboratory work. When generative models propose candidates without principled mechanisms for prioritization, experimental resources are inevitably wasted on uninformative designs, and opportunities for iterative model improvement are missed.

The literature reveals promising but incomplete solutions to this challenge. Recent work such as ProSpero demonstrates the potential of active learning frameworks that integrate generative models with oracle feedback, enabling exploration beyond wild-type neighborhoods while maintaining biological plausibility. Similarly, Adam-PnP showcases adaptive guidance mechanisms for diffusion models using experimental gradients. However, these approaches often lack rigorous uncertainty quantification or fail to provide batch selection strategies compatible with practical experimental throughput constraints.

### Research Objectives

This proposal introduces CADENCE (**C**alibrated **A**ctive **D**esign with **E**nsemble-guided u**N**certainty for **C**losed-loop **E**ngineering), a comprehensive framework that tightly couples uncertainty-aware generative models with adaptive experimental design. Our specific objectives are:

1. **Develop calibrated uncertainty estimation methods** for protein generative models that produce reliable confidence scores reflecting true prediction accuracy across diverse sequence spaces.

2. **Design batch-aware acquisition functions** that optimally balance exploitation of high-predicted-fitness candidates with exploration of uncertain regions, respecting practical experimental throughput limitations.

3. **Establish a closed-loop integration protocol** where experimental results iteratively update both the generative model and surrogate fitness predictors, creating a self-improving design system.

4. **Validate the framework experimentally** on enzyme engineering tasks, demonstrating improved sample efficiency compared to existing approaches.

### Significance

This research directly addresses the ML-experiment gap highlighted by the GEM workshop, making generative models experimentally actionable rather than merely computationally impressive. By reducing the number of experimental rounds required to achieve target protein properties, CADENCE has the potential to accelerate protein engineering timelines by 2-3 fold while reducing associated costs proportionally. Furthermore, the framework generates valuable data for understanding the relationship between sequence, structure, and function—knowledge that feeds back into improved computational models.

## 2. Methodology

### 2.1 Overview

CADENCE operates through iterative cycles of generation, selection, experimentation, and model updating. Each cycle consists of four stages: (1) uncertainty-aware candidate generation, (2) batch selection via acquisition function optimization, (3) experimental characterization, and (4) model refinement. We describe each component in detail below.

### 2.2 Uncertainty-Aware Generative Model

#### Base Architecture

We build upon state-of-the-art protein diffusion models, specifically adapting the Genie architecture for sequence-structure co-generation. The forward diffusion process corrupts protein representations $\mathbf{x}_0$ through a noise schedule:

$$q(\mathbf{x}_t | \mathbf{x}_0) = \mathcal{N}(\mathbf{x}_t; \sqrt{\bar{\alpha}_t}\mathbf{x}_0, (1-\bar{\alpha}_t)\mathbf{I})$$

where $\bar{\alpha}_t = \prod_{s=1}^{t}(1-\beta_s)$ and $\{\beta_t\}_{t=1}^{T}$ defines the noise schedule.

#### Ensemble-Based Uncertainty Quantification

To obtain calibrated uncertainty estimates, we employ a deep ensemble approach with $M$ independently trained diffusion models. For a generated sequence $\mathbf{s}$, we compute:

**Predictive mean:** 
$$\hat{\mu}(\mathbf{s}) = \frac{1}{M}\sum_{m=1}^{M}f_m(\mathbf{s})$$

**Epistemic uncertainty:**
$$\sigma^2_{ep}(\mathbf{s}) = \frac{1}{M}\sum_{m=1}^{M}(f_m(\mathbf{s}) - \hat{\mu}(\mathbf{s}))^2$$

where $f_m(\mathbf{s})$ represents the fitness prediction from ensemble member $m$.

#### Evidential Learning Extension

To capture aleatoric uncertainty without multiple forward passes, we additionally implement an evidential learning head that parameterizes a Normal-Inverse-Gamma distribution over predictions:

$$p(y|\mathbf{s}) = \text{Student-t}_{2\alpha}(\mu, \frac{\beta(1+\nu^{-1})}{\alpha})$$

where $(\mu, \nu, \alpha, \beta) = g_\phi(\mathbf{s})$ are outputs of a learned neural network. The total uncertainty is:

$$\sigma^2_{total}(\mathbf{s}) = \frac{\beta}{\alpha - 1}\left(1 + \frac{1}{\nu}\right)$$

#### Calibration Procedure

We calibrate uncertainty estimates using temperature scaling on a held-out validation set. Given predicted uncertainties $\{\sigma_i\}$ and observed errors $\{|y_i - \hat{\mu}_i|\}$, we optimize temperature $\tau$ to minimize the calibration error:

$$\mathcal{L}_{cal} = \sum_{j=1}^{B}\left|\frac{|\{i: |y_i - \hat{\mu}_i| \leq \tau\sigma_i\}|}{N} - \Phi(1)\right|$$

where $B$ is the number of calibration bins and $\Phi$ is the standard normal CDF.

### 2.3 Batch-Aware Acquisition Functions

#### Problem Formulation

Given experimental throughput constraint $K$ (batch size), we seek to select a batch $\mathcal{B}^* = \{\mathbf{s}_1, ..., \mathbf{s}_K\}$ from candidate pool $\mathcal{C}$ that maximizes information gain:

$$\mathcal{B}^* = \arg\max_{\mathcal{B} \subset \mathcal{C}, |\mathcal{B}|=K} \alpha(\mathcal{B})$$

#### Acquisition Function Design

We propose a composite acquisition function combining three terms:

**Expected Improvement (Exploitation):**
$$\alpha_{EI}(\mathbf{s}) = \mathbb{E}[\max(f(\mathbf{s}) - f^*, 0)]$$

where $f^*$ is the best observed fitness value.

**Uncertainty Bonus (Exploration):**
$$\alpha_{UCB}(\mathbf{s}) = \hat{\mu}(\mathbf{s}) + \kappa \cdot \sigma_{total}(\mathbf{s})$$

with exploration coefficient $\kappa$ decayed over rounds.

**Diversity Term (Batch Coverage):**
$$\alpha_{div}(\mathcal{B}) = \sum_{i<j}\text{dist}(\mathbf{s}_i, \mathbf{s}_j)$$

using sequence edit distance or embedding-space distance.

The combined batch acquisition function is:

$$\alpha(\mathcal{B}) = \sum_{\mathbf{s} \in \mathcal{B}}\left[\lambda_1 \alpha_{EI}(\mathbf{s}) + \lambda_2 \alpha_{UCB}(\mathbf{s})\right] + \lambda_3 \alpha_{div}(\mathcal{B})$$

#### Optimization via Greedy Selection with Look-Ahead

Exact optimization of batch acquisition is NP-hard. We employ a greedy algorithm with one-step look-ahead:

```
Algorithm 1: Batch Selection
Input: Candidate pool C, batch size K, acquisition function α
Output: Selected batch B

B ← ∅
for k = 1 to K do
    s* ← argmax_{s ∈ C\B} [α(B ∪ {s}) + γ·max_{s' ∈ C\B\{s}} α(B ∪ {s, s'})]
    B ← B ∪ {s*}
end for
return B
```

### 2.4 Closed-Loop Integration Protocol

#### Surrogate Model Update

After each experimental round $r$, we update the fitness surrogate using all accumulated data $\mathcal{D}_r = \{(\mathbf{s}_i, y_i)\}_{i=1}^{r \cdot K}$:

$$\theta^{(r+1)} = \arg\min_\theta \mathcal{L}_{MSE}(\theta; \mathcal{D}_r) + \lambda_{reg}\|\theta\|_2^2$$

We employ transfer learning from protein language models (ESM-2) as the encoder backbone.

#### Generative Model Refinement

The generative diffusion model is fine-tuned using reward-weighted likelihood:

$$\mathcal{L}_{gen} = -\mathbb{E}_{\mathbf{s} \sim \mathcal{D}_r}\left[w(\mathbf{s}) \cdot \log p_\theta(\mathbf{s})\right]$$

where $w(\mathbf{s}) = \exp(y(\mathbf{s})/\tau_{reward})$ upweights high-fitness sequences.

### 2.5 Experimental Validation

#### Target System

We will validate CADENCE on engineering **TEM-1 β-lactamase** for improved catalytic efficiency against cephalosporin antibiotics. This system is ideal because: (1) high-throughput activity assays exist (colorimetric nitrocefin hydrolysis), (2) extensive mutational data enables surrogate pre-training, and (3) the fitness landscape contains both local optima and distant peaks.

#### Experimental Protocol

1. **Round 0 (Initialization):** Characterize 96 variants from a random walk starting from wild-type to establish baseline surrogate model.

2. **Rounds 1-5 (Active Learning):** Generate 10,000 candidates per round; select 96 via acquisition function; synthesize, express, and assay; update models.

3. **Baseline Comparisons:**
   - Random selection from generative model outputs
   - Greedy selection (top predicted fitness only)
   - ProSpero-style active learning
   - One-shot generation (no iteration)

#### Evaluation Metrics

- **Sample Efficiency:** Number of experimental rounds to reach 2× wild-type activity
- **Best Fitness Found:** Maximum activity across all tested variants
- **Diversity of Solutions:** Number of distinct sequence clusters achieving >1.5× activity
- **Calibration Error:** Expected calibration error (ECE) of uncertainty estimates
- **Acquisition Function Correlation:** Spearman correlation between acquisition scores and observed fitness improvements

## 3. Expected Outcomes & Impact

### Scientific Outcomes

We anticipate CADENCE will demonstrate **2-3× improved sample efficiency** compared to random selection baselines, reaching target fitness levels in 3 experimental rounds versus 7-9 for non-adaptive approaches. The calibrated uncertainty estimates should achieve ECE < 0.1, enabling reliable confidence assessment for generated candidates. We expect to discover multiple diverse sequence solutions achieving target activity, demonstrating effective exploration of the fitness landscape.

### Methodological Contributions

This work will produce: (1) open-source implementation of uncertainty-aware protein diffusion models, (2) batch acquisition algorithms for experimental design, (3) standardized protocols for closed-loop protein engineering, and (4) benchmark datasets from our experimental characterization.

### Broader Impact

By bridging the gap between generative ML and experimental biology, CADENCE has potential to transform protein engineering workflows across academia and industry. The framework is generalizable to other biomolecular design tasks including antibody optimization, RNA design, and small molecule discovery. Reduced experimental burden translates to faster development cycles for therapeutics and industrial enzymes, with significant economic and societal benefits.

The tight integration of computational and experimental workflows exemplifies the bidirectional knowledge transfer emphasized by the GEM workshop—computational methods become experimentally grounded, while experimental data continuously improves computational models. This virtuous cycle represents a new paradigm for biomolecular design that we believe will define the next generation of protein engineering.