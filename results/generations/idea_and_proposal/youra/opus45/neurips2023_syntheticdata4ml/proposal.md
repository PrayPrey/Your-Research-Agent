# Research Proposal: IB-FAIR-SYNTH: Information Bottleneck with Ensemble Teacher Distillation for Privacy-Fair Synthetic Tabular Data Generation

## 1. Introduction

### 1.1 Background

The advancement of machine learning (ML) has been fundamentally driven by access to high-quality training datasets. However, in many high-stakes domains such as healthcare, finance, and criminal justice, obtaining such datasets remains challenging due to three interconnected issues: data scarcity, privacy concerns, and bias/fairness problems. Data scarcity arises from inherent limitations in collecting samples from rare populations or the prohibitive costs of data acquisition. Privacy concerns stem from the sensitive nature of individual-level data, creating legal and ethical barriers to data sharing. Bias and under-representation in benchmark datasets can perpetuate or amplify societal inequities when ML models are deployed in consequential decision-making contexts.

Synthetic data generation has emerged as a promising solution to these challenges. By generating artificial data that preserves the statistical properties of real datasets, synthetic data can potentially address data scarcity through unlimited sample generation, protect privacy by avoiding direct use of real records, and mitigate bias through targeted augmentation of under-represented groups. Recent advances in Large Language Models (LLMs) have demonstrated remarkable capabilities in generating high-fidelity tabular data, with models like GPT-4 outperforming traditional approaches such as CTGAN in zero-shot generation tasks.

However, existing approaches to synthetic data generation suffer from a fundamental limitation: they typically optimize for data fidelity, privacy, and fairness as separate objectives, often in sequential pipelines. This creates inherent conflicts—privacy mechanisms that add noise or suppress information can disproportionately affect minority groups, undermining fairness objectives. Conversely, fairness interventions that preserve group-specific information may compromise privacy guarantees. The research community lacks a unified framework that simultaneously addresses these three objectives in a principled manner.

### 1.2 Research Objectives

This research proposes IB-FAIR-SYNTH, a novel framework that combines variational Information Bottleneck (IB) compression with ensemble teacher distillation for LLM-based tabular data generation. Our primary objectives are:

1. **Develop a unified framework** that simultaneously achieves differential privacy guarantees, demographic fairness constraints, and high data utility in synthetic tabular data generation.

2. **Establish a principled mechanism** for controlling information flow through variational IB at the sequence representation level, enabling selective suppression of individual-identifying and sensitive-attribute information while preserving task-relevant features.

3. **Design an ensemble teacher distillation approach** where specialized privacy and fairness teachers optimize their respective objectives independently, then combine through weighted distillation to resolve inherent conflicts.

4. **Validate the framework** on standard fairness benchmarks, demonstrating that ensemble distillation resolves privacy-fairness conflicts that naive sequential approaches cannot achieve.

### 1.3 Significance

This research addresses a critical gap at the intersection of generative modeling, differential privacy, and algorithmic fairness. The significance of this work is threefold:

**Theoretical Contribution:** We provide a principled information-theoretic framework for understanding and managing the privacy-fairness-utility trade-off in synthetic data generation, grounded in the Information Bottleneck principle.

**Methodological Innovation:** The ensemble teacher distillation approach offers a novel solution to multi-objective optimization in generative settings, where conflicting objectives have traditionally required ad-hoc balancing.

**Practical Impact:** Successful development of IB-FAIR-SYNTH would enable trustworthy synthetic data generation for sensitive domains, potentially unlocking ML applications in healthcare, finance, and criminal justice where data access has been a significant barrier.

## 2. Methodology

### 2.1 Framework Overview

IB-FAIR-SYNTH operates through a four-stage pipeline that transforms tabular data into privacy-preserving, fair synthetic samples:

**Stage 1: LLM Encoding.** Tabular records are serialized into text sequences and encoded by a pre-trained LLM into dense sequence representations.

**Stage 2: IB Compression.** A variational Information Bottleneck layer compresses these representations to suppress individual-identifying and sensitive-attribute information while preserving task-relevant features.

**Stage 3: Ensemble Teacher Training.** Two specialized teacher models are trained independently—a privacy teacher optimizing differential privacy objectives and a fairness teacher optimizing demographic parity constraints.

**Stage 4: Weighted Distillation.** A student generator is trained through weighted distillation from both teachers, achieving a balanced trade-off across all objectives.

### 2.2 Mathematical Formulation

#### 2.2.1 LLM Encoding

Given a tabular dataset $\mathcal{D} = \{(\mathbf{x}_i, y_i, s_i)\}_{i=1}^{N}$ where $\mathbf{x}_i \in \mathbb{R}^d$ represents features, $y_i$ is the target label, and $s_i \in \{0, 1\}$ is the sensitive attribute, we first serialize each record into a text sequence $t_i$ using a template-based approach. The LLM encoder $f_\theta$ maps this sequence to a latent representation:

$$\mathbf{z}_i = f_\theta(t_i) \in \mathbb{R}^h$$

where $h$ is the hidden dimension of the LLM.

#### 2.2.2 Variational Information Bottleneck

The IB principle seeks to learn a compressed representation $\mathbf{z}$ that maximizes information about the target $Y$ while minimizing information about the input $X$. We extend this to simultaneously minimize information about the sensitive attribute $S$. The IB objective becomes:

$$\mathcal{L}_{IB} = -I(\mathbf{Z}; Y) + \beta_1 I(\mathbf{Z}; X) + \beta_2 I(\mathbf{Z}; S)$$

where $\beta_1$ and $\beta_2$ are Lagrangian multipliers controlling the compression strength for privacy and fairness, respectively.

Since mutual information is intractable in high dimensions, we employ variational bounds. For the compression term, we use a variational approximation:

$$I(\mathbf{Z}; X) \leq \mathbb{E}_{p(\mathbf{x})}\left[D_{KL}(p(\mathbf{z}|\mathbf{x}) \| r(\mathbf{z}))\right]$$

where $r(\mathbf{z})$ is a variational prior (standard Gaussian). For the utility term, we use the InfoNCE lower bound:

$$I(\mathbf{Z}; Y) \geq \mathbb{E}\left[\log \frac{\exp(g(\mathbf{z}, y))}{\sum_{y' \in \mathcal{Y}} \exp(g(\mathbf{z}, y'))}\right]$$

where $g(\cdot, \cdot)$ is a learned critic function.

The compressed representation is obtained through a stochastic encoder:

$$\mathbf{z}_{IB} = \mu_\phi(\mathbf{z}) + \sigma_\phi(\mathbf{z}) \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

where $\mu_\phi$ and $\sigma_\phi$ are neural networks parameterizing the mean and variance.

#### 2.2.3 Privacy Teacher

The privacy teacher $G_P$ is trained to generate synthetic data satisfying $(\epsilon, \delta)$-differential privacy. We employ Rényi Differential Privacy (RDP) for tighter composition bounds. The training objective combines reconstruction loss with DP-SGD:

$$\mathcal{L}_P = \mathbb{E}_{\mathbf{z}_{IB}}\left[\|\mathbf{x} - G_P(\mathbf{z}_{IB})\|^2\right]$$

Gradients are clipped to norm $C$ and Gaussian noise $\mathcal{N}(0, \sigma^2 C^2 I)$ is added:

$$\tilde{\nabla}\mathcal{L}_P = \frac{1}{B}\left(\sum_{i=1}^{B} \text{clip}(\nabla\mathcal{L}_P^{(i)}, C) + \mathcal{N}(0, \sigma^2 C^2 I)\right)$$

The privacy budget is tracked using RDP composition with conversion to $(\epsilon, \delta)$-DP.

#### 2.2.4 Fairness Teacher

The fairness teacher $G_F$ is trained to minimize demographic disparity in generated data. We optimize for Statistical Parity Difference (SPD):

$$\text{SPD} = |P(\hat{Y}=1|S=0) - P(\hat{Y}=1|S=1)|$$

The fairness loss incorporates a regularization term:

$$\mathcal{L}_F = \mathbb{E}_{\mathbf{z}_{IB}}\left[\|\mathbf{x} - G_F(\mathbf{z}_{IB})\|^2\right] + \lambda_F \cdot \text{SPD}(G_F(\mathbf{z}_{IB}))$$

Additionally, we enforce Equalized Odds (EO) through conditional generation:

$$\mathcal{L}_{EO} = \sum_{y \in \{0,1\}} |P(\hat{Y}=1|Y=y, S=0) - P(\hat{Y}=1|Y=y, S=1)|$$

#### 2.2.5 Ensemble Distillation

The student generator $G_S$ is trained through weighted distillation from both teachers:

$$\mathcal{L}_S = \alpha_P \cdot D_{KL}(G_S(\mathbf{z}_{IB}) \| G_P(\mathbf{z}_{IB})) + \alpha_F \cdot D_{KL}(G_S(\mathbf{z}_{IB}) \| G_F(\mathbf{z}_{IB}))$$

where $\alpha_P + \alpha_F = 1$ are ensemble weights. The optimal weights are determined through Pareto frontier analysis on a validation set.

### 2.3 Algorithm

The complete IB-FAIR-SYNTH algorithm proceeds as follows:

**Algorithm 1: IB-FAIR-SYNTH Training**

```
Input: Dataset D, LLM encoder f_θ, IB parameters (β₁, β₂), 
       DP parameters (ε_target, δ, C, σ), Fairness weight λ_F,
       Ensemble weights (α_P, α_F)

Phase 1: IB Layer Training
1. For each batch B ⊂ D:
   a. Encode: z_i = f_θ(serialize(x_i)) for all i ∈ B
   b. Compress: z_IB = μ_φ(z) + σ_φ(z) ⊙ ε
   c. Compute L_IB and update φ via gradient descent
2. Until convergence or validation loss plateaus

Phase 2: Privacy Teacher Training  
3. Initialize G_P with pre-trained weights
4. For each epoch until privacy budget exhausted:
   a. Sample batch, compute L_P
   b. Clip gradients, add noise (DP-SGD)
   c. Update G_P, accumulate RDP budget
5. Convert RDP to (ε, δ)-DP guarantee

Phase 3: Fairness Teacher Training
6. Initialize G_F with pre-trained weights  
7. For each epoch:
   a. Sample batch, compute L_F + λ_F · L_EO
   b. Update G_F via standard SGD
8. Until SPD < 0.1 on validation set

Phase 4: Ensemble Distillation
9. Initialize G_S
10. For each epoch:
    a. Generate samples from G_P and G_F
    b. Compute L_S with weights (α_P, α_F)
    c. Update G_S
11. Until convergence

Output: Student generator G_S
```

### 2.4 Experimental Design

#### 2.4.1 Datasets

We evaluate on four standard fairness benchmarks:

1. **Adult Income** (48,842 samples): Predict income >$50K; sensitive attribute: gender/race
2. **COMPAS** (7,214 samples): Predict recidivism; sensitive attribute: race
3. **German Credit** (1,000 samples): Predict credit risk; sensitive attribute: gender
4. **Bank Marketing** (45,211 samples): Predict subscription; sensitive attribute: age group

#### 2.4.2 Baselines

We compare against:
- **CTGAN**: Standard GAN-based tabular generator
- **DP-CTGAN**: CTGAN with differential privacy
- **FairTabGen**: Fairness-aware tabular generation
- **PF-WGAN**: Recent privacy-fair Wasserstein GAN
- **Sequential DP+Fair**: Naive sequential application of DP then fairness post-processing

#### 2.4.3 Evaluation Metrics

**Privacy Metrics:**
- Rényi DP epsilon ($\epsilon$) with target $\epsilon \leq 8.0$
- Membership Inference Attack (MIA) AUC < 0.6

**Fairness Metrics:**
- Statistical Parity Difference (SPD) < 0.1
- Equalized Odds Difference (EO) < 0.1

**Utility Metrics:**
- Downstream classification accuracy within 5% of real data baseline
- Machine Learning Efficacy (MLE): ratio of synthetic-trained to real-trained model performance

#### 2.4.4 Experimental Protocol

1. **Hyperparameter Selection:** Grid search over $\beta \in \{0.001, 0.01, 0.1, 1.0\}$, $\alpha_P \in \{0.2, 0.4, 0.5, 0.6, 0.8\}$
2. **Statistical Rigor:** 5 random seeds per configuration, report mean ± std
3. **Ablation Studies:** 
   - IB layer removal (direct LLM representations)
   - Single teacher (privacy-only, fairness-only)
   - Weight sensitivity analysis
4. **Statistical Tests:** Paired t-test with significance level $\alpha = 0.05$, Cohen's d for effect size

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect IB-FAIR-SYNTH to achieve the triple constraint simultaneously: $\epsilon \leq 8.0$, SPD < 0.1, and accuracy within 5% of baseline across all four benchmark datasets. Based on preliminary analysis of related work (PFGuard, RFIB), we anticipate:
- Privacy: $\epsilon \approx 6.0-8.0$ with MIA AUC $\approx 0.52-0.58$
- Fairness: SPD $\approx 0.05-0.09$, EO $\approx 0.04-0.08$
- Utility: Accuracy drop of 2-4% compared to non-private baseline

**Mechanism Validation (P2):** We expect monotonic relationships between IB compression rate $\beta$ and privacy/fairness metrics, with higher $\beta$ improving privacy and fairness at moderate utility cost, validating the information-theoretic foundation.

**Ensemble Superiority (P3):** We expect balanced ensemble weights ($\alpha_P \approx \alpha_F \approx 0.5$) to achieve Pareto-optimal trade-offs, outperforming single-teacher and sequential baselines by 10-15% on composite metrics.

### 3.2 Potential Challenges and Mitigations

1. **Computational Overhead:** Ensemble training requires approximately 1.5x baseline compute. Mitigation: Efficient teacher sharing of backbone parameters.

2. **Small Dataset Performance:** German Credit (1,000 samples) may challenge LLM fine-tuning. Mitigation: Pre-training on larger tabular corpora, few-shot adaptation.

3. **Hyperparameter Sensitivity:** Multiple interacting parameters ($\beta_1$, $\beta_2$, $\alpha_P$, $\alpha_F$). Mitigation: Automated Pareto frontier search, sensitivity analysis.

### 3.3 Broader Impact

**Scientific Impact:** This work bridges three traditionally separate research communities—generative modeling, differential privacy, and algorithmic fairness—providing a unified information-theoretic framework for understanding their interactions.

**Practical Applications:** Successful validation would enable:
- Healthcare: Synthetic patient records for rare disease research
- Finance: Fair credit scoring model development without privacy violations
- Criminal Justice: Bias-aware recidivism prediction without exposing individual records

**Limitations and Ethical Considerations:** While synthetic data can enhance privacy and fairness, it is not a panacea. We acknowledge:
- Synthetic data cannot guarantee perfect privacy; residual risks remain
- Fairness definitions are context-dependent; SPD/EO may not capture all fairness concerns
- Generated data should complement, not replace, efforts to collect representative real data

### 3.4 Future Directions

This research opens several avenues for future work:
1. Extension to multi-class sensitive attributes and intersectional fairness
2. Application to other modalities (time series, text, images)
3. Theoretical analysis of privacy-fairness-utility Pareto frontiers
4. Integration with federated learning for distributed synthetic data generation

In conclusion, IB-FAIR-SYNTH represents a principled approach to the fundamental challenge of generating synthetic data that is simultaneously private, fair, and useful. By grounding our framework in information theory and leveraging ensemble learning, we aim to advance the state of trustworthy synthetic data generation for high-stakes ML applications.