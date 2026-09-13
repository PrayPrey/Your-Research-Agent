# Research Proposal: Causal Dissection of Representational Alignment and Computational Mechanisms in Vision Transformers

## 1. Title

**Causal Dissection of Representational Alignment and Computational Mechanisms in Vision Transformers: An Interventional Study of the Alignment-Computation Relationship**

## 2. Introduction

### 2.1 Background

Representational alignment—the similarity between internal representations of different intelligent systems—has emerged as a central concept bridging machine learning, neuroscience, and cognitive science. Recent work demonstrates correlations between alignment and beneficial properties including generalization performance, computational efficiency, and teaching effectiveness. However, a fundamental question remains unresolved: **Does representational alignment causally drive computational mechanisms, or is it merely an epiphenomenal byproduct of shared optimization objectives?**

This question has profound implications for AI safety and interpretability. If alignment causally affects how neural networks process information, it becomes an actionable intervention lever for steering model behavior toward desired outcomes. Conversely, if alignment and computational mechanisms are dissociable properties, high representational similarity may not guarantee similar computational strategies, fundamentally limiting what alignment measurements can tell us about model behavior.

Current research provides only correlational evidence. Khosla et al. (2024) showed that aligned representational axes correlate with reduced wiring costs and better generalization, while Mahner et al. (2024) demonstrated that humans and deep neural networks (DNNs) can achieve similar task performance via different representational strategies. Sucholutsky et al. (2023) established a unified framework for representational alignment research but identified the mechanistic understanding of alignment-to-computation relationships as a critical open problem. No prior work has employed controlled interventions to test the causal direction of this relationship.

This research gap is particularly critical given recent advances in alignment intervention methods. The REPA (Representation Alignment) framework, presented at ICLR 2025, demonstrated successful manipulation of representational alignment in diffusion models through weighted loss functions: $L_{total} = (1-\lambda)L_{task} + \lambda L_{align}$. This provides a methodological foundation for controlled alignment manipulation, but its application to discriminative models and its effects on computational mechanisms remain unexplored.

### 2.2 Research Objectives

This study aims to establish the causal relationship between representational alignment and computational mechanisms through a rigorous interventional design. Our specific objectives are:

**Primary Objective:** Determine whether manipulating representational alignment (via REPA-style intervention) causally affects computational flow patterns in Vision Transformers, or whether these properties are dissociable.

**Secondary Objectives:**
1. Validate REPA-style alignment intervention for discriminative Vision Transformer training on ImageNet classification
2. Establish computational flow metrics (attention entropy, mutual information) as valid indicators of computational mechanism differences
3. Characterize the relationship between alignment strength and out-of-distribution robustness
4. Provide empirical evidence to inform AI safety strategies regarding alignment-based versus computation-based interventions

### 2.3 Research Hypotheses

**Main Hypothesis (H1 - Causal):** Representational alignment causally affects computational mechanisms. Systematically increasing alignment strength ($\lambda$: 0 → 0.5 → 1.0) while controlling task accuracy (±5%) will produce monotonic changes in computational flow metrics (attention entropy, attention concentration, mutual information $I(X;T)$ and $I(T;Y)$).

**Alternative Hypothesis (H0 - Epiphenomenal):** Representational alignment and computational mechanisms are dissociable properties. Increasing alignment strength will change representational similarity (CKA) without systematically affecting computational flow patterns.

**Quantitative Prediction (H1):** At least 2 of 4 computational metrics will show statistically significant monotonic relationships with $\lambda$ (p < 0.05 after FDR correction, Cohen's d > 0.5 between $\lambda=0$ and $\lambda=1.0$).

**Quantitative Prediction (H0):** All 4 computational metrics will show p > 0.05 or effect sizes d < 0.2 across $\lambda$ conditions.

### 2.4 Significance

This research makes three distinct contributions:

**Theoretical Significance:** Resolves the fundamental causality question in alignment research by distinguishing whether alignment is a causal driver or diagnostic indicator. This directly addresses the mechanistic understanding gap identified by Sucholutsky et al. (2023) and provides theoretical grounding for interpreting alignment measurements across cognitive science, neuroscience, and machine learning.

**Methodological Significance:** Introduces the first interventional study combining controlled alignment manipulation, dual measurement (alignment + computational flow), and confound control (task accuracy). This neuroscience-inspired dual-measurement paradigm—separating "what representations look like" (CKA) from "how information flows" (attention/MI)—provides a reusable experimental framework for future alignment-computation studies.

**Practical Significance:** Informs AI safety and representation engineering strategies by determining whether alignment-based interventions (e.g., REPA, contrastive methods) should be prioritized for controlling model behavior. If alignment causally affects computation, strengthening alignment with human cognitive representations becomes a viable path to behavioral alignment. If not, alternative intervention targets must be identified, fundamentally reshaping AI safety research priorities.

## 3. Methodology

### 3.1 Experimental Design Overview

We employ a **3×3 factorial design with controlled confound**:
- **Factor 1:** Alignment intervention strength ($\lambda \in \{0, 0.5, 1.0\}$)
- **Factor 2:** Random seed (3 independent training runs per condition)
- **Controlled confound:** Task accuracy (76±4% tolerance via hyperparameter adjustment)
- **Total models:** 9 (3 alignment conditions × 3 seeds)

The study proceeds in three phases:

**Phase 1 (Validation Pilot):** Verify that computational flow metrics capture meaningful computational differences by comparing Vision Transformer (ViT-B/16) versus Convolutional Neural Network (ResNet-50) on identical ImageNet classification tasks.

**Phase 2 (Intervention Study):** Train 9 ViT-B/16 models with varying alignment pressure while controlling task accuracy, measuring both alignment (CKA) and computational flow (attention entropy, Gini coefficient, mutual information).

**Phase 3 (Causal Analysis):** Statistical testing to determine whether alignment changes causally affect computational mechanisms or whether these properties are dissociable.

### 3.2 Data Collection

#### 3.2.1 Training Data
- **Dataset:** ImageNet-1K (ILSVRC2012)
- **Size:** 1,281,167 training images, 50,000 validation images
- **Classes:** 1,000 object categories
- **Preprocessing:** Standard ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), random resized crop (224×224), random horizontal flip

#### 3.2.2 Evaluation Data
- **In-Distribution:** ImageNet-1K validation set (50,000 images)
- **Out-of-Distribution:** ImageNet-V2 matched-frequency variant (10,000 images) for robustness analysis

#### 3.2.3 Reference System for Alignment
We use a **pre-trained ViT-B/16 aligned to human brain representations** as the reference system for CKA measurement. This choice balances biological grounding with computational tractability. The reference model is obtained by:
1. Fine-tuning ViT-B/16 on the Algonauts 2023 fMRI prediction task
2. Selecting the model checkpoint with highest correlation to human ventral visual stream representations
3. Freezing this model to serve as fixed alignment target

**Alternative considered:** Direct human fMRI representations from Algonauts dataset. We chose the aligned DNN approach to avoid fMRI-to-layer mapping complexities while maintaining biological grounding through the intermediate alignment step.

### 3.3 Model Architecture and Training

#### 3.3.1 Architecture
- **Model:** Vision Transformer Base (ViT-B/16)
- **Parameters:** 86M
- **Layers:** 12 transformer blocks
- **Attention heads:** 12 per block
- **Hidden dimension:** 768
- **Patch size:** 16×16
- **Input resolution:** 224×224

#### 3.3.2 Training Procedure

**Baseline Condition ($\lambda=0$):**
Standard supervised training with cross-entropy loss:
$$L_{total} = L_{CE} = -\sum_{i=1}^{C} y_i \log(\hat{y}_i)$$

where $C=1000$ classes, $y_i$ is the true label, and $\hat{y}_i$ is the predicted probability.

**Alignment Intervention Conditions ($\lambda \in \{0.5, 1.0\}$):**
REPA-style weighted loss combining task objective and alignment objective:
$$L_{total} = (1-\lambda)L_{CE} + \lambda L_{align}$$

The alignment loss $L_{align}$ is defined as:
$$L_{align} = 1 - \text{CKA}(Z^{model}_L, Z^{ref}_L)$$

where $Z^{model}_L \in \mathbb{R}^{N \times d}$ represents activations from layer $L$ of the training model (N samples, d dimensions), $Z^{ref}_L$ represents corresponding activations from the reference system, and CKA is Centered Kernel Alignment:

$$\text{CKA}(X, Y) = \frac{\text{HSIC}(K, L)}{\sqrt{\text{HSIC}(K, K) \cdot \text{HSIC}(L, L)}}$$

where $K = XX^T$ and $L = YY^T$ are Gram matrices, and HSIC (Hilbert-Schmidt Independence Criterion) is:

$$\text{HSIC}(K, L) = \frac{1}{(N-1)^2}\text{tr}(KHLH)$$

with centering matrix $H = I - \frac{1}{N}\mathbf{1}\mathbf{1}^T$.

**Layer Selection:** We compute alignment loss at layer $L=6$ (middle layer) to capture intermediate representations that balance low-level features and high-level semantics.

**Hyperparameters:**
- Optimizer: AdamW ($\beta_1=0.9$, $\beta_2=0.999$)
- Base learning rate: 3e-4 with cosine decay
- Weight decay: 0.05
- Batch size: 512 (distributed across 4 GPUs)
- Training epochs: 90 (with early stopping)
- Warmup epochs: 5
- Data augmentation: RandAugment, Mixup ($\alpha=0.8$), CutMix ($\alpha=1.0$)

**Accuracy Control Mechanism:**
To maintain task accuracy within ±5% across alignment conditions:
1. **Primary control:** Early stopping based on validation accuracy plateau
2. **Secondary adjustment:** Learning rate fine-tuning (±20% from base rate)
3. **Monitoring:** Track validation accuracy every 2 epochs; halt training when accuracy stabilizes within target range (76±4%)

### 3.4 Measurement Procedures

#### 3.4.1 Alignment Measurement

**Metric:** Linear CKA with RBF kernel (debiased estimator following Murphy et al. 2024)

**Procedure:**
1. Extract activations $Z^{model}_L \in \mathbb{R}^{50000 \times 768}$ from layer 6 for all ImageNet validation images
2. Extract corresponding activations $Z^{ref}_L$ from reference system
3. Compute debiased CKA:
$$\text{CKA}_{debiased} = \text{CKA}_{raw} - \frac{d_1 d_2}{N(N-3)}$$
where $d_1, d_2$ are feature dimensions and $N$ is sample size

**Expected range:** [0, 1], with higher values indicating stronger alignment

#### 3.4.2 Computational Flow Metrics

**Metric 1: Attention Entropy**

Measures the dispersion of attention weights, indicating whether the model uses focused or distributed attention patterns.

For each attention head $h$ in layer $l$:
$$H(A_h^l) = -\sum_{i=1}^{S}\sum_{j=1}^{S} a_{ij}^{(h,l)} \log(a_{ij}^{(h,l)})$$

where $a_{ij}^{(h,l)}$ is the attention weight from token $i$ to token $j$, and $S$ is sequence length (196 patches + 1 CLS token = 197).

**Aggregation:** Average entropy across all heads and layers:
$$H_{avg} = \frac{1}{12 \times 12}\sum_{l=1}^{12}\sum_{h=1}^{12} H(A_h^l)$$

**Expected range:** [0, $\log(197)$] ≈ [0, 5.28] bits

**Metric 2: Attention Concentration (Gini Coefficient)**

Measures inequality in attention weight distribution, with higher values indicating more concentrated attention.

For attention weights $\{a_1, a_2, ..., a_n\}$ sorted in ascending order:
$$G = \frac{\sum_{i=1}^{n}(2i - n - 1) \cdot a_i}{n \sum_{i=1}^{n} a_i}$$

**Aggregation:** Average Gini coefficient across all attention heads and layers

**Expected range:** [0, 1], where 0 = perfectly uniform, 1 = maximally concentrated

**Metric 3: Mutual Information $I(X;T)$**

Measures information preserved from input $X$ to intermediate layer representation $T$.

We use MINE (Mutual Information Neural Estimation):
$$I(X;T) = \sup_{\theta} \mathbb{E}_{P_{X,T}}[T_\theta] - \log(\mathbb{E}_{P_X \otimes P_T}[e^{T_\theta}])$$

where $T_\theta$ is a neural network (statistics network) trained to maximize this lower bound.

**Implementation:**
- Statistics network: 3-layer MLP (input: concatenated $X$ and $T$ features; hidden: 512 units; output: scalar)
- Training: 10,000 iterations with Adam optimizer
- Batch size: 256 samples
- Input $X$: Patch embeddings (197×768)
- Layer $T$: Layer 6 output (197×768)

**Expected range:** [0, ∞) bits, typically [5, 15] for vision tasks

**Metric 4: Mutual Information $I(T;Y)$**

Measures task-relevant information in layer representation $T$ about output $Y$.

Same MINE estimator as $I(X;T)$, but with:
- Input: Layer 6 output $T$ (197×768)
- Output: One-hot encoded labels $Y$ (1000 classes)

**Expected range:** [0, $\log(1000)$] ≈ [0, 6.91] bits

#### 3.4.3 Task Performance Metrics

- **Primary:** Top-1 accuracy on ImageNet-1K validation set
- **Secondary:** Top-5 accuracy
- **OOD Robustness:** Top-1 accuracy on ImageNet-V2
- **Calibration:** Expected Calibration Error (ECE) with 15 bins

### 3.5 Validation Pilot (Phase 1)

**Objective:** Verify that computational flow metrics capture meaningful computational differences before main study.

**Design:** Compare ViT-B/16 versus ResNet-50 (similar parameter count, ~86M vs 25M) on identical ImageNet classification task.

**Hypothesis:** Metrics should differ significantly because ViT (self-attention) and ResNet (convolution) use fundamentally different computational mechanisms.

**Metrics:**
- Attention entropy (ViT only; ResNet uses activation pattern entropy as proxy)
- Gini coefficient (adapted for ResNet: spatial activation concentration)
- $I(X;T)$ and $I(T;Y)$ (applicable to both architectures)

**Success Criterion:** At least 2 of 4 metrics show significant difference (independent samples t-test, p < 0.05, Cohen's d > 0.5).

**Contingency:** If criterion not met, metrics do not capture computational strategy differences → revise metric selection (e.g., add gradient flow analysis, layer activation patterns) before proceeding to Phase 2.

### 3.6 Statistical Analysis Plan

#### 3.6.1 Primary Analysis: Causal Effect Test

**Research Question:** Does alignment intervention ($\lambda$) causally affect computational mechanisms?

**Statistical Model:** Mixed-effects ANOVA with accuracy as covariate
$$\text{ComputationalMetric}_{ijk} = \mu + \alpha_i + \beta \cdot \text{Accuracy}_{ijk} + u_k + \epsilon_{ijk}$$

where:
- $i \in \{0, 0.5, 1.0\}$ indexes alignment condition
- $j \in \{1, 2, 3\}$ indexes replicate seed
- $k$ indexes random seed effect
- $\alpha_i$ is fixed effect of alignment condition
- $\beta$ is accuracy covariate coefficient
- $u_k \sim N(0, \sigma_u^2)$ is random seed effect
- $\epsilon_{ijk} \sim N(0, \sigma_\epsilon^2)$ is residual error

**Hypothesis Test:** F-test for $\alpha_i$ main effect (H0: $\alpha_0 = \alpha_{0.5} = \alpha_{1.0}$)

**Significance Level:** $\alpha = 0.05$

**Effect Size:** Partial $\eta^2 = \frac{SS_{alignment}}{SS_{alignment} + SS_{error}}$, with medium effect threshold $\eta^2 > 0.06$

**Post-hoc Comparisons:** Tukey HSD for pairwise comparisons ($\lambda=0$ vs 0.5, 0 vs 1.0, 0.5 vs 1.0)

**Multiple Comparison Correction:** Benjamini-Hochberg FDR correction at q = 0.05 across 4 computational metrics

#### 3.6.2 Monotonicity Test

**Research Question:** Does alignment effect show dose-response relationship?

**Statistical Test:** Jonckheere-Terpstra trend test

**Hypothesis:** Ordered alternative H1: $\mu(\lambda=0) < \mu(\lambda=0.5) < \mu(\lambda=1.0)$ OR reversed ordering

**Significance:** p < 0.05 indicates systematic monotonic relationship

#### 3.6.3 Accuracy Control Verification

**Research Question:** Was task accuracy successfully controlled across conditions?

**Statistical Test:** One-way ANOVA testing accuracy differences across $\lambda$ conditions

**Null Hypothesis:** H0: $\mu_{acc}(\lambda=0) = \mu_{acc}(\lambda=0.5) = \mu_{acc}(\lambda=1.0)$

**Success Criterion:** Non-significant result (p > 0.05) AND all conditions within 76±4% range

**Contingency:** If accuracy differs significantly, use ANCOVA with accuracy as covariate in all subsequent analyses; report results with/without covariate adjustment for sensitivity analysis.

#### 3.6.4 Failure Mode Analysis

**Research Question:** Does alignment affect error patterns on out-of-distribution data?

**Data:** Confusion matrices for top-5 most confused class pairs on ImageNet-V2

**Metric:** Frobenius norm distance between confusion matrices:
$$D_{Frob}(C_1, C_2) = \sqrt{\sum_{i,j}(C_1(i,j) - C_2(i,j))^2}$$

**Statistical Test:** Bootstrap resampling (1000 iterations) to estimate p-value for distance between $\lambda=0$ and $\lambda=1.0$ conditions

**Significance:** p < 0.05 indicates different error patterns

#### 3.6.5 Power Analysis

**Assumed Effect Size:** Cohen's d = 0.6 (medium-large, based on pilot expectations)

**Sample Size:** n = 3 seeds per condition (9 total models)

**Significance Level:** $\alpha = 0.05$ (two-tailed)

**Statistical Power:** ~0.65 for detecting medium effects

**Interpretation:**
- If pilot shows larger effects (d > 0.8), power exceeds 0.80
- If smaller effects (d < 0.4), acknowledge as limitation and recommend follow-up with larger sample

**Robustness Checks:**
1. Non-parametric alternative: Kruskal-Wallis H-test if normality assumptions violated (Shapiro-Wilk test, p < 0.05)
2. Outlier sensitivity: Report results with/without outlier removal (>3 SD from mean)
3. Accuracy covariate sensitivity: Test both with and without accuracy covariate

### 3.7 Evaluation Metrics Summary

| Metric Category | Specific Metric | Purpose | Range | Success Criterion |
|-----------------|-----------------|---------|-------|-------------------|
| **Alignment** | CKA (debiased) | Measure representational similarity | [0, 1] | Monotonic increase with $\lambda$ |
| **Computational Flow** | Attention Entropy | Measure attention dispersion | [0, 5.28] bits | Systematic change with $\lambda$ (H1) or invariance (H0) |
| **Computational Flow** | Gini Coefficient | Measure attention concentration | [0, 1] | Systematic change with $\lambda$ (H1) or invariance (H0) |
| **Computational Flow** | $I(X;T)$ | Measure input information preservation | [0, ∞) bits | Systematic change with $\lambda$ (H1) or invariance (H0) |
| **Computational Flow** | $I(T;Y)$ | Measure task-relevant information | [0, 6.91] bits | Systematic change with $\lambda$ (H1) or invariance (H0) |
| **Task Performance** | ImageNet-1K Top-1 | Control variable | [0, 100]% | 76±4% across conditions |
| **OOD Robustness** | ImageNet-V2 Top-1 | Generalization measure | [0, 100]% | Exploratory analysis |
| **Calibration** | ECE | Confidence calibration | [0, 1] | Exploratory analysis |

### 3.8 Implementation Details

**Software Stack:**
- PyTorch 2.0+ for model training
- Hugging Face Transformers for ViT-B/16 implementation
- Custom REPA loss implementation adapted from sihyun-yu/REPA
- CKA implementation from yuanli2333/CKA-similarity (debiased variant)
- MINE implementation from sungyubkim/MINE-Mutual-Information-Neural-Estimation

**Computational Resources:**
- Hardware: 4× NVIDIA A100 (40GB) GPUs per training run
- Estimated training time: 48 hours per model × 9 models = 432 GPU-hours
- Validation pilot: 2 models × 48 hours = 96 GPU-hours
- Total: ~528 GPU-hours (~$10,000 estimated cost)

**Reproducibility:**
- Fixed random seeds: {42, 123, 456} for three replicates
- Deterministic CUDA operations enabled
- All hyperparameters logged with Weights & Biases
- Code and trained models released on GitHub upon publication

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Scenario 1: Causal Hypothesis Supported (H1)

**Expected Pattern:**
- CKA increases monotonically: 0.45 ($\lambda=0$) → 0.68 ($\lambda=0.5$) → 0.82 ($\lambda=1.0$)
- At least 2 of 4 computational metrics show significant monotonic changes:
  - Attention entropy decreases (more focused attention with alignment)
  - Gini coefficient increases (more concentrated attention)
  - $I(X;T)$ decreases (alignment compresses representations)
  - $I(T;Y)$ maintained or slightly increases (preserves task information)
- Statistical significance: p < 0.05 after FDR correction, Cohen's d > 0.5

**Interpretation:** Representational alignment causally affects computational mechanisms. Increasing alignment systematically changes how information flows through the network, supporting alignment as an actionable intervention lever for steering model behavior.

**Implications:**
- AI Safety: Alignment-based interventions (REPA, contrastive methods) should be prioritized for controlling model behavior
- Interpretability: High CKA similarity indicates not just representational similarity but also computational strategy similarity
- Theory: Alignment is a causal driver, not merely a diagnostic indicator

#### 4.1.2 Scenario 2: Epiphenomenal Hypothesis Supported (H0)

**Expected Pattern:**
- CKA increases monotonically (intervention works)
- All 4 computational metrics show p > 0.05 OR effect sizes d < 0.2
- Computational flow patterns remain statistically invariant across alignment conditions

**Interpretation:** Representational alignment and computational mechanisms are dissociable properties. Models can achieve high representational similarity while using different computational strategies, analogous to biological neural synchrony dissociating from functional connectivity (Damatac et al. 2024).

**Implications:**
- AI Safety: Alternative intervention targets needed beyond alignment (e.g., direct computational mechanism manipulation)
- Interpretability: CKA measurements reveal representational geometry but not computational strategy; dual measurement required
- Theory: Alignment is diagnostic indicator of shared optimization but not causal driver of computation

#### 4.1.3 Scenario 3: Mixed Results

**Expected Pattern:**
- 1 metric shows significant effect, 3 do not
- Effect sizes in medium range (d = 0.3-0.5)
- Inconsistent patterns across metrics

**Interpretation:** Weak causal effect requiring larger sample size or refined metrics. Alignment may affect specific computational aspects (e.g., attention patterns) but not others (e.g., information flow).

**Implications:**
- Methodological: Current metrics capture partial computational picture; additional metrics needed
- Follow-up: Larger-scale study (n=5-7 seeds) or layer-wise analysis to clarify weak effects

### 4.2 Scientific Impact

#### 4.2.1 Theoretical Contributions

**Resolves Fundamental Causality Question:** This study provides the first interventional evidence for or against the causal relationship between representational alignment and computational mechanisms, directly addressing the mechanistic understanding gap identified by Sucholutsky et al. (2023).

**Establishes Dual-Measurement Paradigm:** Introduces neuroscience-inspired separation of alignment measurement (CKA - "what representations look like") from computational mechanism measurement (attention/MI - "how information flows"), providing a conceptual framework for future alignment research.

**Informs Alignment Theory:** Determines whether alignment is a causal driver (actionable intervention target) or epiphenomenal indicator (diagnostic tool), fundamentally shaping how alignment should be conceptualized in AI safety and interpretability research.

#### 4.2.2 Methodological Contributions

**First Interventional Study:** Combines controlled alignment manipulation (REPA), dual measurement, and confound control (task accuracy) in a single experimental design, establishing a methodological template for causal alignment research.

**Validated Metric Suite:** Validation pilot (Phase 1) establishes whether attention entropy, Gini coefficient, and mutual information validly capture computational mechanism differences, providing vetted metrics for future studies.

**Reusable Experimental Protocol:** Modular design (alignment intervention + computational profiling) can be adapted for:
- Other architectures (CNNs, RNNs, language models)
- Other tasks (object detection, segmentation, language understanding)
- Other alignment targets (human brain, expert models, multimodal systems)

#### 4.2.3 Practical Impact

**AI Safety Strategy Guidance:** Provides empirical evidence for practitioners choosing between alignment-based interventions (if H1 supported) versus direct computational mechanism interventions (if H0 supported) for controlling model behavior.

**Interpretability Method Refinement:** Clarifies what CKA/RSA measurements reveal about models:
- If H1: High alignment → similar computational strategies (strong interpretability signal)
- If H0: High alignment ≠ similar strategies (dual measurement required for full understanding)

**Robustness Engineering:** ImageNet-V2 failure mode analysis reveals whether alignment-driven training affects out-of-distribution generalization, informing deployment decisions for safety-critical applications.

### 4.3 Broader Impact

#### 4.3.1 Cross-Disciplinary Contributions

**Neuroscience-ML Bridge:** Demonstrates successful transfer of neuroscience's dual-measurement paradigm (neural synchrony vs functional connectivity) to deep learning research, encouraging further cross-disciplinary methodological exchange.

**Cognitive Science Implications:** If alignment and computation dissociate in artificial systems, this may inform theories of biological intelligence where similar dissociations occur (e.g., representational similarity structure vs processing dynamics).

#### 4.3.2 Future Research Directions

**Immediate Extensions:**
1. **Architecture Generalization:** Test whether findings transfer to CNNs, RNNs, language transformers
2. **Layer-wise Analysis:** Extend from single-layer (L=6) to full layer-wise characterization
3. **Alternative Alignment Targets:** Compare brain-aligned vs expert-model-aligned vs multimodal-aligned systems

**Long-term Research Program:**
1. **Causal Intervention Toolkit:** Develop suite of alignment manipulation methods beyond REPA (contrastive, adversarial, curriculum-based)
2. **Computational Mechanism Taxonomy:** Characterize full space of computational strategies via comprehensive metric suite
3. **Alignment-Behavior Relationship:** Extend from computational mechanisms to behavioral alignment (value alignment, safety properties)

#### 4.3.3 Limitations and Scope

**Acknowledged Limitations:**
1. **Architecture-Specific:** Findings for ViT-B/16 may not generalize to other architectures without validation
2. **Task-Specific:** Image classification results may differ for other tasks (detection, segmentation, generation)
3. **Proxy Metrics:** Attention entropy and MI are computational proxies for "strategy"; true ground truth is conceptual
4. **Sample Size:** n=3 seeds provides limited power for small effects (d < 0.4)
5. **Reference System Dependency:** Alignment measurement depends on choice of reference (brain-aligned DNN vs direct fMRI)

**Scope Boundaries:**
- **Applies to:** Vision Transformers, image classification, supervised learning, representation-level analysis
- **Does NOT apply to:** CNNs, language models, reinforcement learning, training dynamics (without separate validation)

### 4.4 Dissemination Plan

**Publications:**
1. **Primary Paper:** Submit to NeurIPS 2026 or ICLR 2027 (main results)
2. **Workshop Paper:** Present at Re-Align Workshop 2026 (preliminary findings)
3. **Methodology Paper:** Publish dual-measurement protocol in Journal of Machine Learning Research

**Open Science:**
- Code repository: GitHub (MIT license)
- Trained models: Hugging Face Model Hub
- Data: Alignment measurements and computational metrics (Zenodo)
- Reproducibility package: Docker container with full experimental pipeline

**Community Engagement:**
- Tutorial: "Causal Alignment Research Methods" at CVPR 2027
- Blog post: Distill-style interactive explanation of findings
- Twitter thread: Accessible summary for broader ML community

### 4.5 Timeline

**Month 1-2:** Validation pilot (Phase 1)
- Train ViT-B/16 and ResNet-50 baselines
- Compute computational flow metrics
- Validate metric sensitivity

**Month 3-5:** Main intervention study (Phase 2)
- Train 9 ViT-B/16 models (3 conditions × 3 seeds)
- Monitor accuracy control
- Collect alignment and computational measurements

**Month 6-7:** Analysis and interpretation (Phase 3)
- Statistical testing (ANOVA, trend tests, failure mode analysis)
- Robustness checks
- Visualization and interpretation

**Month 8:** Manuscript preparation and submission

**Total Duration:** 8 months

**Estimated Budget:** $15,000 (compute) + $5,000 (personnel) = $20,000

---

This research proposal establishes a rigorous experimental framework for testing the causal relationship between representational alignment and computational mechanisms in Vision Transformers. By combining controlled interventions, dual measurement, and statistical rigor, this study will provide definitive evidence to resolve a fundamental question in alignment research, with profound implications for AI safety, interpretability, and our theoretical understanding of what alignment represents in artificial intelligence systems.