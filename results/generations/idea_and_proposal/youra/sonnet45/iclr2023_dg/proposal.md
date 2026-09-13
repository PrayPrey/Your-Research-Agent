# Research Proposal: Adaptive Invariance Selection for Domain Generalization via Meta-Learned Confidence Estimation

## 1. Title

**Adaptive Invariance Selection for Domain Generalization via Meta-Learned Confidence Estimation**

## 2. Introduction

### 2.1 Background

Domain generalization (DG) represents one of the most critical challenges in modern machine learning: developing models that maintain robust performance when deployed in environments that differ from training conditions. Unlike domain adaptation, which assumes access to unlabeled target domain data, DG requires models to generalize to entirely unseen distributions using only source domain information. This problem is ubiquitous in real-world applications, from medical diagnosis systems that must work across different hospitals and imaging equipment, to autonomous vehicles that must operate safely in diverse weather and geographic conditions.

Recent years have witnessed an explosion of domain generalization methods, particularly those based on invariance principles. Invariant Risk Minimization (IRM) and its variants seek to learn representations that maintain predictive power across all training environments by enforcing gradient alignment across domains. The theoretical appeal is compelling: if we can identify features that are invariantly predictive across training domains, these features should generalize to new domains sharing the same causal structure.

However, empirical results have been disappointing. Meta-analyses of DG benchmarks reveal that sophisticated invariance-based methods often fail to consistently outperform standard Empirical Risk Minimization (ERM). This phenomenon, sometimes called the "DG paradox," has led the community to question whether general-purpose DG algorithms are fundamentally limited without additional information.

Recent theoretical work has begun to illuminate why invariance principles fail. Koyama & Yamaguchi (2020) proved that when invariant features capture all information about the label, enforcing invariance can actually harm out-of-distribution performance. Ahuja et al. (2021) demonstrated that combining invariance with information bottleneck objectives can mitigate these failures, but their approach requires manually tuning hyperparameters ($\lambda$ for IRM weight, $\beta$ for information bottleneck strength) separately for each dataset—a process that is both computationally expensive and methodologically problematic when target domain performance is unknown.

This creates a critical gap: practitioners lack principled, data-driven guidance on *when* to enforce invariance versus when to compress representations. The decision between these strategies currently relies on expensive trial-and-error or, worse, implicit selection bias where researchers report only the best-performing configuration.

### 2.2 Research Objectives

This research proposes **AIS-DG (Adaptive Invariance Selection for Domain Generalization)**, a meta-learning framework that automatically learns when to apply invariance-based optimization versus information compression. Our primary objectives are:

**O1. Develop a lightweight confidence estimator** that predicts whether invariance-based optimization will succeed on a given dataset by monitoring three observable signals: gradient disagreement across domains, mutual information between inputs and representations, and validation performance gaps.

**O2. Design a differentiable interpolation mechanism** that dynamically weights IRM and information bottleneck losses based on the learned confidence, enabling end-to-end training via bi-level optimization.

**O3. Operationalize theoretical optimality conditions** from Koyama & Yamaguchi (2020) and Ahuja et al. (2021) into practical, learnable criteria that can guide automated method selection.

**O4. Demonstrate consistent improvements** over static baseline methods across diverse benchmarks (PACS, OfficeHome, DomainNet) with statistical significance, while avoiding worst-case failures of either pure strategy.

**O5. Provide interpretable confidence scores** that offer practitioners actionable insights into when invariance principles are likely to succeed or fail on their specific datasets.

### 2.3 Research Hypothesis

Our core hypothesis is: **If a meta-learned confidence estimator predicts high invariance quality (based on gradient disagreement $\sigma^2(\nabla L)$, mutual information $I(X;Z)$, and validation gap $\Delta_{acc}$), then dynamically interpolating toward IRM ($c \to 1$) will improve out-of-distribution generalization compared to static combinations, because the learned confidence accurately identifies when data satisfies the theoretical conditions for invariance optimality.**

The causal mechanism operates through the following chain:

$$\text{Data Properties} \xrightarrow{\text{generates}} \text{Observable Signals} \xrightarrow{\text{meta-learner}} \text{Confidence Score} \xrightarrow{\text{interpolation}} \text{Adaptive Loss} \xrightarrow{\text{optimization}} \text{Improved OOD Performance}$$

When invariance quality is high (invariant features are informative but not exhaustive), high gradient disagreement signals the need for alignment, while moderate mutual information indicates room for invariance without information loss. Conversely, when invariance quality is low (spurious correlations dominate or invariant features are complete), the meta-learner should favor information bottleneck compression to avoid overfitting to spurious patterns.

### 2.4 Significance

This research addresses Gap 2 from the ICLR 2023 workshop on domain generalization: providing practical, actionable guidelines for when invariance-based methods will succeed. The significance spans three dimensions:

**Theoretical Significance:** We bridge the gap between theoretical optimality conditions (which are typically stated in terms of unobservable population quantities) and practical decision-making (which must rely on finite-sample estimates from observable signals). By formulating invariance quality as a learnable function, we extend binary theoretical results to continuous confidence scores suitable for real-world application.

**Methodological Significance:** AIS-DG introduces a novel meta-learning architecture specifically designed for invariance quality estimation, distinct from existing meta-learning DG methods that focus on general feature adaptation. The confidence-based interpolation framework is generalizable to other invariance-based methods beyond IRM, potentially benefiting the broader family of domain alignment techniques (CORAL, MMD, etc.).

**Practical Significance:** By automating method selection, AIS-DG eliminates days of manual experimentation and reduces the risk of selection bias in research reporting. The interpretable confidence scores support error analysis and scientific understanding, helping practitioners diagnose why their DG approach succeeds or fails. For the broader machine learning community deploying models in safety-critical domains, this represents a step toward more reliable and trustworthy domain generalization.

## 3. Methodology

### 3.1 Problem Formulation

We consider the standard multi-source domain generalization setting. Let $\mathcal{E} = \{e_1, e_2, \ldots, e_n\}$ denote $n \geq 3$ source domains (environments), where each domain $e_i$ is associated with a distribution $P_{e_i}(X, Y)$ over input-output pairs $(X, Y) \in \mathcal{X} \times \mathcal{Y}$. We have access to labeled training data $\mathcal{D}_{e_i}^{train}$ and validation data $\mathcal{D}_{e_i}^{val}$ from each source domain. The goal is to learn a predictor $f_\theta: \mathcal{X} \to \mathcal{Y}$ that generalizes to an unseen target domain $e_{target}$ with distribution $P_{e_{target}}(X, Y)$, where we have no access to target domain data during training.

### 3.2 Observable Signals for Invariance Quality

We define three observable signals that serve as inputs to our confidence estimator:

**Signal 1: Gradient Disagreement**

Gradient disagreement measures the variance in gradient directions across source domains, directly capturing the penalty term in IRM:

$$\sigma^2(\nabla L) = \frac{1}{n} \sum_{i=1}^{n} \|\nabla_\theta \mathcal{L}_{e_i}(\theta) - \bar{\nabla}\|^2$$

where $\mathcal{L}_{e_i}(\theta) = \mathbb{E}_{(x,y) \sim P_{e_i}}[\ell(f_\theta(x), y)]$ is the loss on domain $e_i$, and $\bar{\nabla} = \frac{1}{n}\sum_{i=1}^{n} \nabla_\theta \mathcal{L}_{e_i}(\theta)$ is the mean gradient. We normalize this to $[0,1]$ using running statistics across training batches.

**Signal 2: Mutual Information**

We estimate the mutual information between inputs $X$ and learned representations $Z = \phi_\theta(X)$ using the Mutual Information Neural Estimation (MINE) framework:

$$I(X; Z) = \sup_{T \in \mathcal{T}} \mathbb{E}_{P_{XZ}}[T(x,z)] - \log \mathbb{E}_{P_X \otimes P_Z}[e^{T(x,z)}]$$

where $T: \mathcal{X} \times \mathcal{Z} \to \mathbb{R}$ is a neural network (statistics network). We train $T$ jointly with the main model using the MINE objective and normalize estimates to $[0,1]$ by dividing by $\log(\dim(Z))$.

**Signal 3: Validation Performance Gap**

The validation gap captures the maximum performance difference across source domains:

$$\Delta_{acc} = \max_{i \in [n]} \text{Acc}_{e_i}^{val} - \min_{i \in [n]} \text{Acc}_{e_i}^{val}$$

where $\text{Acc}_{e_i}^{val}$ is the classification accuracy on the validation set of domain $e_i$. This signal is already in $[0, 1]$ (or $[0\%, 100\%]$).

### 3.3 Meta-Learned Confidence Estimator

The confidence estimator is a lightweight neural network $\phi_\psi: \mathbb{R}^3 \to [0,1]$ parameterized by $\psi$, which maps the three observable signals to a confidence score:

$$c = \phi_\psi(\sigma^2(\nabla L), I(X;Z), \Delta_{acc})$$

**Architecture:** We use a 2-layer multilayer perceptron (MLP):

$$\phi_\psi(s) = \sigma_{\text{sigmoid}}(W_2 \cdot \text{ReLU}(W_1 \cdot s + b_1) + b_2)$$

where $s \in \mathbb{R}^3$ is the input signal vector, $W_1 \in \mathbb{R}^{128 \times 3}$, $W_2 \in \mathbb{R}^{1 \times 64}$, and $\sigma_{\text{sigmoid}}$ ensures $c \in [0,1]$. This architecture has approximately 10,000 parameters, representing less than 0.01% of a typical ResNet-50 backbone.

### 3.4 Adaptive Loss Interpolation

Given the confidence score $c$, we define the adaptive loss as a smooth interpolation between IRM and information bottleneck objectives:

$$\mathcal{L}_{\text{AIS}}(\theta; c) = c \cdot \mathcal{L}_{\text{IRM}}(\theta) + (1-c) \cdot \mathcal{L}_{\text{IB-ERM}}(\theta)$$

**IRM Loss:** Following Arjovsky et al. (2019), the IRM loss is:

$$\mathcal{L}_{\text{IRM}}(\theta) = \sum_{i=1}^{n} \mathcal{L}_{e_i}(\theta) + \lambda \sum_{i=1}^{n} \|\nabla_{w|w=1.0} \mathcal{L}_{e_i}(w \cdot f_\theta)\|^2$$

where the penalty term enforces that the optimal classifier on top of the representation $f_\theta$ is the same across all domains.

**Information Bottleneck ERM Loss:** Following Ahuja et al. (2021):

$$\mathcal{L}_{\text{IB-ERM}}(\theta) = \sum_{i=1}^{n} \mathcal{L}_{e_i}(\theta) + \beta \cdot I(X; Z)$$

where $\beta$ controls the strength of representation compression.

### 3.5 Bi-Level Optimization

We train the system using bi-level optimization, where the inner loop optimizes the predictor $\theta$ for a given confidence $c$, and the outer loop optimizes the confidence estimator parameters $\psi$ to maximize validation performance:

**Inner Loop (Predictor Optimization):**

For $k = 1, \ldots, K$ steps:

$$\theta^{(k+1)} = \theta^{(k)} - \alpha_{\text{inner}} \nabla_\theta \mathcal{L}_{\text{AIS}}(\theta^{(k)}; c)$$

where $c = \phi_\psi(s)$ is computed from current signals, and $\alpha_{\text{inner}}$ is the inner learning rate.

**Outer Loop (Meta-Learner Optimization):**

After $K$ inner steps, we compute the meta-objective on source validation sets:

$$\mathcal{L}_{\text{meta}}(\psi) = -\frac{1}{n} \sum_{i=1}^{n} \text{Acc}_{e_i}^{val}(\theta^{(K)})$$

and update the meta-learner:

$$\psi \leftarrow \psi - \alpha_{\text{outer}} \nabla_\psi \mathcal{L}_{\text{meta}}(\psi)$$

The gradient $\nabla_\psi \mathcal{L}_{\text{meta}}(\psi)$ is computed through the inner loop updates using automatic differentiation, similar to MAML (Finn et al., 2017).

### 3.6 Training Algorithm

**Algorithm 1: AIS-DG Training**

```
Input: Source domains {D_e1, ..., D_en}, hyperparameters K, α_inner, α_outer, λ, β
Output: Predictor f_θ, confidence estimator φ_ψ

1. Initialize θ (e.g., pretrained ResNet-50), ψ (random), MINE network T
2. Split each D_ei into D_ei^train (80%) and D_ei^val (20%)
3. For epoch = 1 to N_epochs:
4.   For each mini-batch B from {D_e1^train, ..., D_en^train}:
5.     // Compute observable signals
6.     σ²(∇L) ← ComputeGradientDisagreement(θ, B)
7.     I(X;Z) ← EstimateMI_MINE(θ, T, B)
8.     Δ_acc ← ComputeValidationGap(θ, {D_e1^val, ..., D_en^val})
9.     
10.    // Meta-learner forward pass
11.    c ← φ_ψ(σ²(∇L), I(X;Z), Δ_acc)
12.    
13.    // Inner loop: optimize predictor
14.    θ_temp ← θ
15.    For k = 1 to K:
16.      L_AIS ← c·L_IRM(θ_temp) + (1-c)·L_IB-ERM(θ_temp)
17.      θ_temp ← θ_temp - α_inner·∇_θ L_AIS
18.    
19.    // Outer loop: optimize meta-learner
20.    L_meta ← -MeanAccuracy(θ_temp, {D_e1^val, ..., D_en^val})
21.    ψ ← ψ - α_outer·∇_ψ L_meta  // gradient through inner loop
22.    
23.    // Update main predictor
24.    θ ← θ_temp
25.    
26.    // Update MINE network
27.    T ← T - α_MINE·∇_T L_MINE(θ, T, B)
28.
29. Return θ, ψ
```

### 3.7 Data Collection and Experimental Design

**Datasets:**

We evaluate on three standard domain generalization benchmarks:

1. **PACS** (Photo, Art, Cartoon, Sketch): 9,991 images across 7 classes and 4 domains. Each domain serves as target once (leave-one-domain-out protocol).

2. **OfficeHome** (Art, Clipart, Product, Real-World): 15,588 images across 65 classes and 4 domains. Same leave-one-domain-out protocol.

3. **DomainNet** (Clipart, Infograph, Painting, Quickdraw, Real, Sketch): ~600,000 images across 345 classes and 6 domains. We use the standard subset with 6 domains.

**Data Preprocessing:**

- Images resized to 224×224
- Standard ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- Data augmentation: random horizontal flip, random crop, color jitter (training only)
- No augmentation on validation/test sets

**Train/Validation Split:**

For each source domain, we randomly split the data into 80% training and 20% validation. The validation sets are used exclusively for meta-optimization (outer loop) and are never used for inner loop predictor training. This ensures the meta-learner learns to predict generalization rather than overfitting to training performance.

### 3.8 Baseline Methods

We compare AIS-DG against the following baselines:

1. **ERM (Empirical Risk Minimization):** Standard supervised learning minimizing average loss across source domains.

2. **IRM (Invariant Risk Minimization):** Arjovsky et al. (2019) with penalty weight $\lambda \in \{1, 10, 100, 1000\}$ selected via grid search.

3. **IB-IRM:** Ahuja et al. (2021) with static weights $\lambda, \beta$ selected via grid search over $\lambda \in \{1, 10, 100\}$, $\beta \in \{0.01, 0.1, 1.0\}$.

4. **MLDG (Meta-Learning Domain Generalization):** Li et al. (2018) with meta-train/meta-test splits.

5. **MetaReg:** Balaji et al. (2018) with regularization toward meta-test performance.

6. **Meta-DMoE:** Current state-of-the-art mixture-of-experts approach with meta-learned gating.

All methods use the same ResNet-50 backbone (pretrained on ImageNet) for fair comparison. Hyperparameters for baselines are selected to maximize average source validation accuracy.

### 3.9 Evaluation Metrics

**Primary Metric:**

- **Target Domain Accuracy:** Classification accuracy on the held-out target domain, averaged over all leave-one-domain-out splits.

**Secondary Metrics:**

1. **Confidence Correlation:** Pearson correlation $\rho(c_{\text{learned}}, c_{\text{oracle}})$ between learned confidence and oracle confidence (computed by sweeping $c \in [0,1]$ and selecting the value that maximizes target accuracy).

2. **Worst-Case Performance:** Minimum accuracy across all target domains, measuring robustness.

3. **Computational Overhead:** Training time relative to ERM baseline, measured in GPU-hours.

4. **Statistical Significance:** Paired t-test comparing AIS-DG to the best baseline on each (dataset, target domain) pair, with Bonferroni correction for multiple comparisons.

5. **Effect Size:** Cohen's d to quantify the magnitude of improvement.

**Ablation Metrics:**

- Accuracy when removing each input signal (gradient disagreement, MI, validation gap)
- Accuracy with static confidence values $c \in \{0, 0.25, 0.5, 0.75, 1.0\}$
- Accuracy with different inner loop steps $K \in \{1, 3, 5, 10, 20\}$

### 3.10 Experimental Protocol

**Replication:**

Each experiment is repeated with 5 different random seeds. We report mean ± standard deviation across seeds and perform statistical tests on the distribution of results.

**Hyperparameter Selection:**

We perform grid search over:
- Inner learning rate: $\alpha_{\text{inner}} \in \{10^{-4}, 10^{-3}, 10^{-2}\}$
- Outer learning rate: $\alpha_{\text{outer}} \in \{10^{-5}, 10^{-4}, 10^{-3}\}$
- Inner loop steps: $K \in \{1, 3, 5, 10\}$
- IRM penalty: $\lambda \in \{1, 10, 100\}$
- IB penalty: $\beta \in \{0.01, 0.1, 1.0\}$

Selection criterion: Maximize average accuracy across source validation sets (not target, to avoid leakage). Once selected, hyperparameters are fixed for all target domains within a dataset.

**Computational Resources:**

- Hardware: 8× NVIDIA V100 GPUs (32GB each)
- Training time budget: 24 hours per (dataset, target domain) configuration
- Total estimated compute: ~1,000 GPU-hours for full experimental suite

**Statistical Testing:**

1. **Primary Test:** Paired t-test on target accuracy: $H_0: \mu_{\text{AIS-DG}} = \mu_{\text{best baseline}}$ vs. $H_1: \mu_{\text{AIS-DG}} > \mu_{\text{best baseline}}$, with significance level $\alpha = 0.05$.

2. **Multiple Comparison Correction:** Bonferroni correction for $m$ comparisons (number of target domains across all datasets).

3. **Non-Parametric Alternative:** Wilcoxon signed-rank test for robustness to non-normal distributions.

4. **Effect Size:** Cohen's d = $\frac{\bar{x}_{\text{AIS-DG}} - \bar{x}_{\text{baseline}}}{s_{\text{pooled}}}$ where $s_{\text{pooled}}$ is the pooled standard deviation.

### 3.11 Success Criteria

The hypothesis is supported if:

1. **Performance:** AIS-DG achieves target accuracy $\geq \max(\text{acc}_{\text{IRM}}, \text{acc}_{\text{IB-IRM}}, \text{acc}_{\text{ERM}}) + 1.0\%$ on average across all target domains, with $p < 0.05$.

2. **Consistency:** AIS-DG outperforms the best baseline on $\geq 75\%$ of individual (dataset, target domain) pairs.

3. **Confidence Quality:** Learned confidence correlates with oracle confidence: $\rho(c_{\text{learned}}, c_{\text{oracle}}) > 0.5$ across datasets.

4. **Computational Feasibility:** Training time $\leq 2.0 \times$ ERM baseline.

The hypothesis is **falsified** if:

1. AIS-DG performs worse than $\max(\text{IRM}, \text{IB-IRM})$ on $\geq 50\%$ of test configurations.
2. Confidence correlation $|\rho| < 0.1$ (no learned signal).
3. Bi-level optimization fails to converge (validation loss oscillates) in $> 30\%$ of runs.

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Outcomes:**

1. **Performance Improvements:** We expect AIS-DG to achieve:
   - PACS: 89-91% average accuracy (vs. 87-89% for current SOTA)
   - OfficeHome: 68-70% average accuracy (vs. 66-67% for IB-IRM)
   - DomainNet: 42-44% average accuracy (vs. 40-41% for Meta-DMoE)

2. **Confidence Correlation:** Pearson correlation $\rho > 0.6$ between learned and oracle confidence scores, demonstrating that the meta-learner successfully captures invariance quality.

3. **Robustness:** Worst-case performance (minimum accuracy across target domains) within 2% of average performance, indicating consistent behavior across diverse distribution shifts.

4. **Computational Overhead:** Training time 1.5-1.8× ERM baseline, acceptable for research benchmarks and practical deployment.

**Qualitative Outcomes:**

1. **Interpretable Confidence Patterns:** Visualization of learned confidence scores will reveal that:
   - High gradient disagreement + low MI → high confidence (favor IRM)
   - Low gradient disagreement + high MI → low confidence (favor IB-ERM)
   - These patterns align with theoretical predictions from Koyama & Yamaguchi (2020)

2. **Failure Mode Analysis:** Identification of specific dataset characteristics where AIS-DG struggles, providing insights for future improvements (e.g., very few source domains, extreme class imbalance).

3. **Generalization Beyond Images:** Preliminary experiments on non-vision domains (e.g., text classification with domain shift) will indicate whether the approach generalizes beyond computer vision.

### 4.2 Theoretical Impact

**Bridging Theory and Practice:**

AIS-DG operationalizes abstract theoretical conditions into learnable, observable signals. This demonstrates a pathway for translating domain generalization theory into practical algorithms, potentially inspiring similar approaches for other theoretical results in the field.

**Extension of Optimality Conditions:**

By formulating invariance quality as a continuous confidence score rather than a binary condition, we extend existing theory to handle the realistic scenario where optimality conditions are approximately (rather than exactly) satisfied. This contributes to a more nuanced understanding of when invariance principles succeed.

**Meta-Learning Theory:**

Our bi-level optimization framework provides a concrete instance of meta-learning for method selection (rather than feature adaptation), potentially opening new research directions in automated algorithm configuration for domain generalization.

### 4.3 Methodological Impact

**Automated Method Selection:**

AIS-DG eliminates the need for manual, per-dataset tuning of invariance vs. compression trade-offs. This has immediate practical value for researchers and practitioners, reducing experimental overhead from days to hours.

**Generalizable Framework:**

The confidence-based interpolation mechanism can be extended to other pairs of DG methods beyond IRM and IB-ERM. For example:
- IRM vs. CORAL (correlation alignment)
- IRM vs. MMD (maximum mean discrepancy)
- Invariance vs. data augmentation strategies

This creates a family of adaptive DG methods, each targeting different aspects of distribution shift.

**Interpretability:**

Unlike black-box ensemble methods, AIS-DG provides interpretable confidence scores that explain *why* a particular strategy was chosen. This supports scientific understanding and debugging, crucial for safety-critical applications.

### 4.4 Practical Impact

**Deployment Reliability:**

By avoiding worst-case failures of either pure invariance or pure compression, AIS-DG reduces the risk of catastrophic performance drops when deploying models to new domains. This is critical for applications like medical diagnosis, autonomous driving, and financial fraud detection.

**Reduced Selection Bias:**

Automated method selection mitigates the risk of researchers cherry-picking results by manually selecting the best-performing method post-hoc. This improves the reproducibility and credibility of domain generalization research.

**Actionable Guidelines:**

The learned confidence scores provide practitioners with actionable insights: "Your dataset has high gradient disagreement and low MI, suggesting invariance-based methods will work well." This democratizes access to domain generalization expertise.

### 4.5 Broader Impact

**Addressing the DG Paradox:**

By demonstrating that adaptive method selection can consistently outperform static baselines, this research provides evidence that the "DG paradox" (sophisticated methods failing to beat ERM) may be due to inappropriate method selection rather than fundamental limitations of DG approaches.

**Workshop Question:**

This work directly addresses the ICLR 2023 workshop question: "What do we need for successful domain generalization?" Our answer: **We need data-driven, automated method selection that adapts to each dataset's invariance quality, rather than one-size-fits-all algorithms.**

**Future Research Directions:**

This research opens several promising directions:
1. **Multi-method interpolation:** Extending beyond two methods to continuous mixtures of multiple DG strategies
2. **Online adaptation:** Updating confidence estimates during deployment as new data arrives
3. **Causal discovery:** Using confidence patterns to infer causal structure in observational data
4. **Theoretical guarantees:** Proving PAC-style bounds on the performance of adaptive method selection

### 4.6 Limitations and Risks

**Acknowledged Limitations:**

1. **Multi-source requirement:** AIS-DG requires $\geq 3$ source domains, limiting applicability to single-source scenarios.

2. **Computational overhead:** 1.5-2× training time may be prohibitive for extremely large-scale datasets or resource-constrained settings.

3. **MINE stability:** Mutual information estimation may be unstable in very high dimensions, requiring careful tuning or alternative estimators.

4. **Interpolation assumption:** Optimal predictors may lie outside the IRM-IB-ERM interpolation path, limiting potential gains.

**Mitigation Strategies:**

- Provide ablation studies with alternative MI estimators (InfoNCE, CLUB)
- Test sensitivity to number of source domains ($n \in \{3, 4, 5, 6\}$)
- Explore extrapolation beyond $c \in [0,1]$ in future work
- Clearly document applicability boundaries in documentation

### 4.7 Dissemination Plan

**Publications:**

- Target venue: ICLR 2024 (main conference) or NeurIPS 2024
- Workshop paper: ICLR 2023 Workshop on Domain Generalization (if timeline permits)

**Open Source Release:**

- Full implementation in PyTorch with pre-trained models
- Reproducibility package with exact hyperparameters and random seeds
- Documentation with tutorials for applying AIS-DG to new datasets

**Community Engagement:**

- Blog post explaining key insights for practitioners
- Presentation at domain generalization reading groups
- Collaboration with benchmark maintainers to include AIS-DG in standard evaluations

This research represents a significant step toward reliable, automated domain generalization, with the potential to improve the robustness of machine learning systems deployed in diverse real-world environments.