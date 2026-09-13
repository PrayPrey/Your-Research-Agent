# Research Proposal: TPMOL: Trustworthy Pareto Multi-Objective Learning for Medical Foundation Models via Joint Explainability-Robustness-Privacy Optimization

## 1. Introduction

### 1.1 Background

The rapid advancement of large foundation models (FMs) has demonstrated remarkable capabilities in language understanding, visual recognition, and multimodal reasoning across general domains. Healthcare, as one of the most critical industries affecting every individual, stands to benefit enormously from these technological breakthroughs. The global healthcare system faces persistent challenges including high costs, limited medical professionals, and significant disparities in access to qualified care—particularly pronounced in rural and developing regions where doctor-to-population ratios remain critically low.

Medical Foundation Models (MFMs) have emerged as promising solutions to address these challenges, offering potential for automated diagnosis, prognosis, treatment planning, and clinical workflow optimization. Recent developments in vision-language models such as BiomedCLIP, MedCLIP, and specialized medical imaging models have demonstrated impressive diagnostic capabilities approaching expert-level performance on benchmark datasets. However, despite these technical achievements, a critical deployment barrier persists: the inability to simultaneously satisfy the trustworthiness requirements essential for clinical adoption.

Clinical deployment of AI systems demands concurrent satisfaction of multiple trustworthiness dimensions. **Explainability** ensures that medical professionals can understand and validate AI-driven decisions, maintaining the physician's role as the ultimate decision-maker. **Robustness** guarantees reliable performance across diverse patient populations, imaging equipment, and clinical scenarios—critical given the high-stakes nature of medical decisions. **Privacy** protects sensitive patient information throughout the model lifecycle, addressing regulatory requirements such as HIPAA and GDPR while maintaining patient trust.

### 1.2 Problem Statement

Current approaches to achieving trustworthy MFMs treat these dimensions as independent optimization problems, leading to fragmented solutions with unacceptable trade-offs. Improving privacy through differential privacy mechanisms often degrades diagnostic accuracy by 10-20%. Adversarial training for robustness can compromise model interpretability by encouraging complex, non-linear decision boundaries. Explainability constraints may limit model capacity, reducing overall performance. This siloed approach fundamentally fails to meet clinical deployment requirements where all trustworthiness dimensions must be satisfied concurrently.

The FUTURE-AI framework, developed by 117 international experts and published in BMJ (2024), established six unified principles for trustworthy medical AI, emphasizing that these dimensions are interconnected rather than independent. Yet, no existing methodology provides a principled approach to jointly optimize these competing objectives while maintaining diagnostic performance above clinical acceptability thresholds.

### 1.3 Research Objectives

This research proposes **TPMOL (Trustworthy Pareto Multi-Objective Learning)**, a constrained Pareto multi-objective optimization framework that jointly trains three trustworthiness objectives while maintaining diagnostic accuracy as a hard constraint. Our specific objectives are:

1. **Develop a unified optimization framework** that simultaneously addresses explainability, robustness, and privacy through multi-objective Pareto optimization
2. **Design novel trustworthiness components** including Attention Consistency Regularization (ACR) for explainability and Explanation-Level Differential Privacy (ELDP) for privacy preservation
3. **Validate theoretical synergies** between trustworthiness dimensions, demonstrating that joint optimization can achieve superior results compared to independent optimization
4. **Establish clinical deployment readiness** by ensuring all trustworthiness metrics meet predefined thresholds while maintaining AUC ≥ 0.85

### 1.4 Significance

This research addresses a fundamental gap between MFM capabilities and real-world healthcare deployment. By providing the first framework enabling clinically deployable MFMs satisfying all trustworthiness requirements simultaneously, TPMOL advances regulatory-compliant medical AI. The framework directly supports compliance with emerging AI regulations including the EU AI Act's requirements for high-risk medical AI systems. Success would establish a new paradigm for trustworthy medical AI development, potentially accelerating the responsible deployment of AI assistants in healthcare settings worldwide.

## 2. Methodology

### 2.1 Framework Overview

TPMOL formulates trustworthy MFM training as a constrained multi-objective optimization problem:

$$\min_{\theta} \mathcal{L}(\theta) = \left[ \mathcal{L}_{exp}(\theta), \mathcal{L}_{rob}(\theta), \mathcal{L}_{priv}(\theta) \right]$$

$$\text{subject to: } \text{AUC}(\theta) \geq 0.85$$

where $\theta$ represents model parameters, and the three loss components correspond to explainability, robustness, and privacy objectives respectively.

### 2.2 Trustworthiness Components

#### 2.2.1 Attention Consistency Regularization (ACR) for Explainability

ACR ensures stable, interpretable attention patterns by penalizing inconsistency in attention maps under semantically-preserving input perturbations. For an input image $x$ and its perturbed version $x' = x + \delta$ where $\delta$ represents clinically-irrelevant noise:

$$\mathcal{L}_{exp}(\theta) = \mathbb{E}_{x \sim \mathcal{D}} \left[ 1 - \frac{\text{Att}(x; \theta) \cdot \text{Att}(x'; \theta)}{\|\text{Att}(x; \theta)\| \cdot \|\text{Att}(x'; \theta)\|} \right]$$

where $\text{Att}(x; \theta)$ denotes the flattened attention map from the final transformer layer. The ACR score is computed as:

$$\text{ACR} = 1 - \mathcal{L}_{exp}(\theta)$$

This formulation is fully differentiable, enabling end-to-end optimization. Perturbations $\delta$ are sampled from a Gaussian distribution $\mathcal{N}(0, \sigma^2 I)$ with $\sigma = 0.05$ to simulate acquisition noise without altering diagnostic content.

#### 2.2.2 Adversarial Training for Robustness

We employ Projected Gradient Descent (PGD) adversarial training to enhance model robustness against input perturbations:

$$\mathcal{L}_{rob}(\theta) = \mathbb{E}_{x \sim \mathcal{D}} \left[ \max_{\|\delta\|_\infty \leq \epsilon} \mathcal{L}_{CE}(f_\theta(x + \delta), y) \right]$$

where $\mathcal{L}_{CE}$ is the cross-entropy loss, $f_\theta$ is the model, $y$ is the ground truth label, and $\epsilon = 8/255$ defines the perturbation budget. The inner maximization is solved using 7-step PGD with step size $\alpha = 2/255$:

$$\delta^{(t+1)} = \Pi_{\|\delta\|_\infty \leq \epsilon} \left[ \delta^{(t)} + \alpha \cdot \text{sign}(\nabla_\delta \mathcal{L}_{CE}(f_\theta(x + \delta^{(t)}), y)) \right]$$

Robust accuracy is evaluated as the classification accuracy on adversarially perturbed test samples.

#### 2.2.3 Explanation-Level Differential Privacy (ELDP)

Unlike traditional differential privacy applied during training, ELDP applies calibrated noise to model explanations post-training, decoupling privacy preservation from training dynamics:

$$\tilde{\text{Att}}(x) = \text{Att}(x; \theta) + \mathcal{N}\left(0, \sigma_{DP}^2 \cdot \Delta_A^2 \cdot I\right)$$

where $\Delta_A$ is the sensitivity of the attention mechanism and $\sigma_{DP}$ is calibrated to achieve target privacy budget $\epsilon$. The privacy loss is formulated as:

$$\mathcal{L}_{priv}(\theta) = \max\left(0, \Delta_A(\theta) - \Delta_{target}\right)$$

This encourages the model to learn attention patterns with bounded sensitivity, enabling stronger privacy guarantees (lower $\epsilon$) with less noise. The relationship between $\sigma_{DP}$ and $\epsilon$ follows the Gaussian mechanism:

$$\epsilon = \frac{\Delta_A}{\sigma_{DP}} \sqrt{2 \ln(1.25/\delta)}$$

where $\delta = 10^{-5}$ is the privacy failure probability.

### 2.3 Conflict-Averse Gradient Descent (CAGrad)

The three objectives often exhibit gradient conflicts during optimization. We employ CAGrad to find update directions that improve all objectives simultaneously. Given gradients $g_1, g_2, g_3$ for the three losses, CAGrad solves:

$$d^* = \arg\min_d \|d - g_{avg}\|^2 \quad \text{s.t.} \quad g_i^\top d \geq (1-c) \cdot g_i^\top g_{avg}, \forall i$$

where $g_{avg} = \frac{1}{3}(g_1 + g_2 + g_3)$ and $c \in [0, 1]$ controls the conflict-aversion strength. This quadratic program admits a closed-form solution when conflicts exist:

$$d^* = g_{avg} + \sum_{i \in \mathcal{C}} \lambda_i^* (g_i - g_{avg})$$

where $\mathcal{C}$ is the set of conflicting gradients and $\lambda_i^*$ are Lagrange multipliers. We set $c = 0.5$ based on preliminary experiments.

### 2.4 Constrained Optimization with Accuracy Guarantee

To enforce the diagnostic accuracy constraint $\text{AUC}(\theta) \geq 0.85$, we employ an augmented Lagrangian approach:

$$\mathcal{L}_{total}(\theta, \mu) = \mathcal{L}_{task}(\theta) + \mu \cdot \max(0, 0.85 - \text{AUC}(\theta)) + \frac{\rho}{2} \max(0, 0.85 - \text{AUC}(\theta))^2$$

where $\mathcal{L}_{task}$ is the standard classification loss, $\mu$ is the Lagrange multiplier updated via dual ascent, and $\rho = 10$ is the penalty coefficient. The multiplier update follows:

$$\mu^{(t+1)} = \mu^{(t)} + \rho \cdot \max(0, 0.85 - \text{AUC}(\theta^{(t)}))$$

### 2.5 Complete Training Algorithm

**Algorithm 1: TPMOL Training**

```
Input: Dataset D, Base model f_θ (BiomedCLIP), Epochs T, Learning rate η
Output: Trustworthy model parameters θ*

1: Initialize θ with pretrained BiomedCLIP weights
2: Initialize LoRA adapters (rank=16) for parameter-efficient tuning
3: Initialize Lagrange multiplier μ = 1.0
4: for epoch t = 1 to T do
5:     for each batch (x, y) ∈ D do
6:         // Compute trustworthiness losses
7:         Generate perturbation δ_exp ~ N(0, σ²I)
8:         L_exp ← ACR_loss(x, x + δ_exp, θ)
9:         Generate adversarial perturbation δ_adv via 7-step PGD
10:        L_rob ← CE_loss(f_θ(x + δ_adv), y)
11:        L_priv ← max(0, Δ_A(θ) - Δ_target)
12:        L_task ← CE_loss(f_θ(x), y)
13:        
14:        // Compute gradients
15:        g_1 ← ∇_θ L_exp; g_2 ← ∇_θ L_rob; g_3 ← ∇_θ L_priv
16:        
17:        // CAGrad conflict resolution
18:        d* ← CAGrad(g_1, g_2, g_3)
19:        
20:        // Update with accuracy constraint
21:        θ ← θ - η · (d* + ∇_θ L_task + μ · ∇_θ constraint_penalty)
22:    end for
23:    // Update Lagrange multiplier
24:    Evaluate AUC on validation set
25:    μ ← μ + ρ · max(0, 0.85 - AUC)
26: end for
27: return θ* = θ
```

### 2.6 Experimental Design

#### 2.6.1 Datasets

- **CheXpert**: 224,316 chest X-rays from 65,240 patients with 14 pathology labels
- **MIMIC-CXR**: 377,110 chest X-rays from 65,379 patients with associated radiology reports

Both datasets require Data Use Agreements and will be preprocessed following standard protocols with 70/10/20 train/validation/test splits.

#### 2.6.2 Base Model and Adaptation

We employ **BiomedCLIP ViT-B/16** as the base model, adapted using Low-Rank Adaptation (LoRA) with rank $r=16$ to enable parameter-efficient fine-tuning. This reduces trainable parameters from 86M to approximately 4M while maintaining model capacity.

#### 2.6.3 Baselines

1. **Single-Explainability**: Standard training + ACR loss only
2. **Single-Robustness**: Adversarial training only
3. **Single-Privacy**: Training with gradient-level DP (DP-SGD)
4. **Sequential**: Train for robustness, then fine-tune for explainability, then apply ELDP
5. **Naive Multi-Task**: Equal-weighted sum of all losses without CAGrad

#### 2.6.4 Evaluation Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Diagnostic AUC | ≥ 0.85 | Area under ROC curve on test set |
| ACR Score | ≥ 0.80 | Attention consistency under perturbations |
| Robust Accuracy | ≥ 70% | Accuracy under PGD attack (ε=8/255) |
| Privacy (ε) | ≤ 1.0 | ELDP privacy budget |
| Unified Trustworthiness | All above | Conjunction of all metrics |

#### 2.6.5 Statistical Analysis

- **Sample Size**: n = 25 independent training runs per condition (5 conditions × 25 runs = 125 total)
- **Statistical Tests**: One-way ANOVA with Tukey HSD post-hoc tests
- **Significance Level**: α = 0.05 with Bonferroni correction for multiple comparisons
- **Effect Size**: Cohen's d with target d ≥ 0.6 (medium effect)
- **Reporting**: Mean ± standard deviation, 95% confidence intervals, adjusted p-values

#### 2.6.6 Ablation Studies

1. **Component Ablation**: Remove each trustworthiness component individually
2. **CAGrad Ablation**: Replace with equal-weighted gradient averaging
3. **Constraint Ablation**: Remove AUC constraint to observe unconstrained Pareto front
4. **Synergy Analysis**: Measure pairwise interactions between objectives

### 2.7 Implementation Details

- **Hardware**: Single NVIDIA A100 (40GB)
- **Training**: 50 epochs, batch size 32, AdamW optimizer with learning rate $3 \times 10^{-4}$
- **CAGrad Overhead**: Approximately 20% additional computation for gradient conflict resolution
- **Reproducibility**: Fixed random seeds, deterministic operations, code release upon publication

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Outcome 1: Unified Trustworthiness Achievement**
We expect TPMOL to achieve all trustworthiness targets simultaneously:
- ACR Score ≥ 0.80 (vs. ~0.65 for robustness-only baseline)
- Robust Accuracy ≥ 70% (vs. ~50% for explainability-only baseline)
- ELDP ε ≤ 1.0 (vs. ε > 5.0 for training-time DP approaches)
- Diagnostic AUC ≥ 0.85 (maintained via constraint)

**Outcome 2: Synergy Validation**
We hypothesize that ACR regularization will enhance robustness by encouraging stable feature representations, demonstrating a positive synergy between explainability and robustness objectives. Quantitatively, we expect the joint optimization to outperform the sum of individual improvements by at least 10%.

**Outcome 3: Pareto Front Characterization**
TPMOL will reveal the achievable trade-off surface between trustworthiness dimensions, providing practitioners with actionable guidance for deployment decisions based on specific clinical requirements.

### 3.2 Scientific Contributions

1. **Theoretical**: First formal framework connecting multi-objective optimization theory to medical AI trustworthiness requirements
2. **Methodological**: Novel ELDP mechanism enabling privacy-preserving explanations without training-time accuracy degradation
3. **Empirical**: Comprehensive evaluation establishing benchmarks for unified trustworthiness in medical imaging

### 3.3 Clinical and Societal Impact

**Regulatory Compliance**: TPMOL directly addresses requirements of emerging AI regulations (EU AI Act, FDA guidance on AI/ML-based medical devices) by providing verifiable trustworthiness guarantees.

**Deployment Acceleration**: By resolving the trustworthiness trilemma, TPMOL removes a critical barrier to clinical deployment, potentially accelerating the availability of AI-assisted diagnosis in underserved regions.

**Trust Building**: Simultaneous satisfaction of explainability, robustness, and privacy requirements builds trust among clinicians, patients, and regulators—essential for sustainable AI adoption in healthcare.

### 3.4 Limitations and Future Directions

**Current Scope Limitations**: TPMOL is validated on medical image classification; extension to medical NLP, video analysis, and generative models requires additional research.

**Future Extensions**:
- Incorporation of fairness as a fourth trustworthiness dimension
- Extension to federated learning settings for multi-institutional deployment
- Real-time surgical assistance applications requiring latency constraints
- Integration with clinical decision support systems

### 3.5 Falsification Criteria

The hypothesis will be considered falsified if:
1. Any trustworthiness metric performs worse than the corresponding single-objective baseline
2. Diagnostic AUC falls below 0.85 (constraint violation)
3. Achieving one dimension requires >20% degradation in another
4. CAGrad fails to converge within 100 epochs

These clear falsification criteria ensure scientific rigor and enable definitive conclusions about the viability of joint trustworthiness optimization.

### 3.6 Timeline and Milestones

- **Months 1-2**: Implementation of TPMOL framework and baseline methods
- **Months 3-4**: Experiments on CheXpert dataset
- **Months 5-6**: Experiments on MIMIC-CXR dataset and ablation studies
- **Months 7-8**: Statistical analysis, paper writing, and code release

In conclusion, TPMOL represents a paradigm shift from fragmented trustworthiness optimization to unified multi-objective learning, addressing a critical gap in medical AI deployment. By demonstrating that explainability, robustness, and privacy can be jointly optimized without sacrificing diagnostic performance, this research paves the way for clinically deployable, regulatory-compliant Medical Foundation Models that can meaningfully improve healthcare delivery worldwide.