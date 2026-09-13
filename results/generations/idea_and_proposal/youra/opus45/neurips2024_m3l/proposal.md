# Research Proposal: Curvature Homeostasis: A Self-Regulating Mechanism Linking Edge of Stability to Generalization in Deep Learning

## 1. Introduction

### 1.1 Background

Deep learning has achieved remarkable empirical success across diverse domains, yet the theoretical foundations explaining why gradient-based optimization finds well-generalizing solutions remain incomplete. Classical optimization theory predicts that gradient descent with learning rate $\eta$ should diverge when the loss curvature (measured by the largest Hessian eigenvalue $\lambda_{\max}$) exceeds $2/\eta$. However, recent empirical observations have revealed a striking phenomenon termed the **Edge of Stability (EoS)**: during training of overparameterized neural networks, the sharpness $\lambda_{\max}$ rises until it reaches approximately $2/\eta$, then hovers near this threshold while the training loss continues to decrease non-monotonically (Cohen et al., 2021).

This phenomenon challenges conventional optimization wisdom and suggests that gradient descent operates through mechanisms not captured by classical convergence theory. Simultaneously, a separate line of research has established empirical correlations between flat minima (regions of low curvature) and good generalization performance (Keskar et al., 2017; Foret et al., 2020). The Sharpness-Aware Minimization (SAM) algorithm explicitly seeks flat minima and achieves state-of-the-art generalization, providing practical evidence for this connection.

Despite these advances, a critical gap remains: **the mechanistic connection between EoS dynamics and generalization has not been established**. Current theories treat the sharpness-generalization correlation as coincidental rather than causal, leaving practitioners without principled guidance for hyperparameter selection. This gap becomes increasingly problematic as we enter the era of foundation models, where training billion-parameter models makes trial-and-error approaches prohibitively expensive in terms of computation, time, and environmental impact.

### 1.2 Research Objectives

This research proposes to establish **curvature homeostasis** as a fundamental self-regulating mechanism in deep learning optimization. Our central hypothesis posits that the learning rate $\eta$ acts as feedback gain in a dynamical system that drives Batch Sharpness toward $2/\eta$, which we term the **Edge of Stochastic Stability (EoSS)**. This self-regulation implicitly minimizes curvature complexity, causing convergence to flat minima with smaller generalization gaps.

Our specific objectives are:

1. **Demonstrate the existence of curvature homeostasis**: Empirically verify that Batch Sharpness self-regulates toward $2/\eta$ within a tight tolerance (±10%) across diverse experimental conditions.

2. **Establish the causal mechanism**: Validate a 4-step causal chain linking learning rate selection to generalization through curvature dynamics.

3. **Quantify predictive power**: Show that curvature homeostasis provides stronger predictive power for generalization than existing sharpness-correlation approaches.

### 1.3 Significance

This research addresses fundamental questions at the intersection of optimization theory and generalization in deep learning, directly aligned with the workshop's focus on reconciling theory with practice. The expected contributions include:

- **Theoretical advancement**: A mechanistic explanation connecting EoS dynamics to generalization through curvature self-regulation.
- **Practical guidance**: Principled learning rate selection rules based on the relationship $\text{Batch Sharpness} \approx 2/\eta$, reducing the need for expensive hyperparameter searches.
- **Foundation for scaling**: Understanding that can inform training strategies for large models where empirical tuning is impractical.

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Curvature Homeostasis Hypothesis

We formalize our hypothesis as follows:

**Main Hypothesis (H-CurvatureHomeostasis-v1):** Under overparameterized neural network training with constant learning rate $\eta$, if SGD is applied with batch size $B$, then Batch Sharpness self-regulates toward $2/\eta$ (Edge of Stochastic Stability), which implicitly minimizes curvature complexity $C(\theta)$, thereby causing convergence to flat minima with smaller generalization gap.

**Alternative Hypothesis (H0):** The observed correlation between flat minima and generalization is coincidental; SGD does not systematically regulate curvature, and any relationship is due to confounding factors.

#### 2.1.2 Mathematical Definitions

**Batch Sharpness:** For a mini-batch $\mathcal{B}$ of size $B$, we define Batch Sharpness as the expected directional curvature along stochastic gradient directions:

$$\text{BS}(\theta) = \mathbb{E}_{\mathcal{B}}\left[\frac{g_{\mathcal{B}}^T H(\theta) g_{\mathcal{B}}}{\|g_{\mathcal{B}}\|^2}\right]$$

where $g_{\mathcal{B}} = \nabla_\theta \mathcal{L}_{\mathcal{B}}(\theta)$ is the mini-batch gradient and $H(\theta) = \nabla^2_\theta \mathcal{L}(\theta)$ is the full Hessian.

**Curvature Complexity:** We adopt a PAC-Bayes inspired complexity measure:

$$C(\theta) = \log \det(I + \beta \cdot H(\theta))$$

where $\beta > 0$ is a scaling parameter. For computational tractability, we also consider the trace approximation:

$$C_{\text{trace}}(\theta) = \text{Tr}(H(\theta))$$

**Generalization Gap:** Defined as the difference between test and training accuracy:

$$\text{Gap} = \text{Acc}_{\text{test}} - \text{Acc}_{\text{train}}$$

#### 2.1.3 The 4-Step Causal Chain

Our proposed mechanism operates through the following causal chain:

**Step 1 (Instability Trigger):** Large learning rate $\eta$ causes the effective step size $\eta \cdot \lambda_{\max}$ to exceed the stability threshold of 2, triggering oscillatory behavior:

$$\eta \cdot \lambda_{\max}(\theta_t) > 2 \implies \text{oscillations in loss}$$

**Step 2 (Curvature Reduction):** Oscillations preferentially move the optimizer toward regions of lower curvature, as high-curvature directions experience larger repulsive forces:

$$\theta_{t+1} = \theta_t - \eta \nabla \mathcal{L}(\theta_t) \implies \text{drift toward low-curvature regions}$$

**Step 3 (Complexity Reduction):** Lower curvature directly reduces PAC-Bayes complexity:

$$\lambda_{\max} \downarrow \implies C(\theta) \downarrow$$

**Step 4 (Generalization Improvement):** Lower complexity yields tighter generalization bounds:

$$C(\theta) \downarrow \implies \text{Generalization Gap} \downarrow$$

### 2.2 Experimental Design

#### 2.2.1 Data Collection

**Datasets:**
- Primary: CIFAR-10 (50,000 training / 10,000 test images)
- Secondary validation: CIFAR-100 (for robustness checks)

**Architectures:**
- Primary: ResNet-18 (overparameterized for CIFAR-10)
- Secondary: VGG-16, Wide ResNet-28-10 (for architecture robustness)

**Training Configuration:**
- Optimizer: SGD with momentum 0.9
- Learning rates: $\eta \in \{0.01, 0.05, 0.1, 0.2, 0.5, 1.0\}$
- Batch sizes: $B \in \{32, 64, 128, 256, 512\}$
- Training duration: 200 epochs (sufficient for EoS equilibrium)
- No learning rate scheduling (constant LR throughout)
- Standard data augmentation (random crop, horizontal flip)

#### 2.2.2 Measurement Procedures

**Batch Sharpness Estimation via Hutchinson's Method:**

Computing the exact Hessian is intractable for large networks. We employ the Hutchinson trace estimator with Rademacher random vectors:

$$\text{BS}(\theta) \approx \frac{1}{K} \sum_{k=1}^{K} \frac{g_{\mathcal{B}}^T H v_k \cdot v_k^T g_{\mathcal{B}}}{\|g_{\mathcal{B}}\|^2}$$

where $v_k \sim \text{Rademacher}(\pm 1)$ and $Hv_k$ is computed via Hessian-vector products using automatic differentiation. We use $K = 50$ random vectors for stable estimates.

**Measurement Schedule:**
- Batch Sharpness: Every 100 iterations
- Curvature complexity $C(\theta)$: Every epoch
- Training/test accuracy: Every epoch
- Full Hessian eigenspectrum: Every 10 epochs (for validation)

#### 2.2.3 Algorithmic Steps for Verification

**Algorithm 1: Curvature Homeostasis Verification**

```
Input: Dataset D, architecture A, learning rates Η, batch sizes Β, n_runs
Output: Verification results for P1, P2, P3

1. For each η ∈ Η, B ∈ Β:
2.     For run = 1 to n_runs:
3.         Initialize network θ₀ ~ standard initialization
4.         For epoch = 1 to 200:
5.             For each mini-batch 𝓑:
6.                 Compute gradient g_𝓑 = ∇L_𝓑(θ)
7.                 Update θ ← θ - η·g_𝓑
8.                 If iteration % 100 == 0:
9.                     Estimate BS(θ) via Hutchinson
10.            Compute C(θ), train_acc, test_acc
11.        Record final BS_eq, C_eq, gap_eq
12.    
13.    # Verification P1: Homeostasis existence
14.    Compute deviation = |BS_eq - 2/η| / (2/η)
15.    Test H0: deviation > 0.10 via one-sample t-test
16.    
17.    # Verification P2: BS → C(θ) correlation
18.    Compute Pearson r(BS_eq, C_eq) across runs
19.    
20.    # Verification P3: C(θ) → Gap correlation
21.    Compute Pearson r(C_eq, gap_eq) across runs

22. Apply Bonferroni correction for multiple comparisons
23. Return verification results
```

### 2.3 Statistical Analysis Plan

#### 2.3.1 Sample Size and Power

- **Runs per condition:** $n \geq 20$ (different random seeds)
- **Target effect size:** Cohen's $d > 0.8$ (large effect)
- **Statistical power:** 0.80
- **Significance level:** $\alpha = 0.05$
- **Multiple comparison correction:** Bonferroni ($\alpha_{\text{adj}} = 0.05/3 \approx 0.017$)

#### 2.3.2 Prediction-Specific Tests

**P1 (Curvature Homeostasis Existence):**
- Null hypothesis: $|\text{BS} - 2/\eta| / (2/\eta) > 0.10$
- Test: One-sample t-test on relative deviation
- Success criterion: Mean deviation < 10%, $p < 0.017$

**P2 (Sharpness-Complexity Correlation):**
- Null hypothesis: $\rho(\text{BS}, C(\theta)) \leq 0$
- Test: Pearson correlation with Fisher z-transformation
- Success criterion: $r > 0.7$, $p < 0.017$

**P3 (Complexity-Generalization Correlation):**
- Null hypothesis: $\rho(C(\theta), \text{Gap}) \leq 0$
- Test: Pearson correlation
- Success criterion: $r > 0.5$, $p < 0.017$

#### 2.3.3 Falsification Criteria

The hypothesis will be considered falsified if:
1. **Primary failure:** BS deviation from $2/\eta$ exceeds 30% consistently
2. **Mechanism failure:** $|r| < 0.3$ between BS and $C(\theta)$
3. **Generalization failure:** $C(\theta)$-gap correlation $< 0.2$ or negative

### 2.4 Baseline Comparisons

To establish the value of curvature homeostasis as an explanatory framework, we compare against:

1. **Sharpness-correlation baseline:** Direct correlation between $\lambda_{\max}$ and generalization gap (Keskar et al., 2017)

2. **EoSS baseline:** Edge of Stochastic Stability framework without the complexity-generalization link

3. **GenEFT baseline:** Generalization via Effective Field Theory approach (Roberts et al., 2022)

**Comparison metrics:**
- Predictive $R^2$ for generalization gap
- Consistency across learning rates and batch sizes
- Robustness to architecture changes

### 2.5 Computational Requirements

- **Hardware:** 4× NVIDIA A100 GPUs
- **Estimated compute:** 2-4 GPU-days for primary experiments
- **Storage:** ~50GB for checkpoints and measurements
- **Software:** PyTorch 2.0+, custom Hutchinson estimator implementation

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect Batch Sharpness to stabilize within ±10% of $2/\eta$ after an initial transient phase (typically 20-50 epochs). This equilibrium should be robust across different random seeds, demonstrating that curvature homeostasis is a systematic phenomenon rather than a statistical artifact.

**Secondary Outcomes:**
- **P2:** Strong positive correlation ($r > 0.7$) between Batch Sharpness and curvature complexity, validating the mechanistic link between EoS dynamics and loss landscape geometry.
- **P3:** Moderate to strong correlation ($r > 0.5$) between curvature complexity and generalization gap, establishing the predictive value of our framework.

**Causal Chain Validation:** We expect each step of the 4-step causal chain to show statistically significant relationships, with the overall path analysis explaining substantial variance in generalization outcomes.

### 3.2 Theoretical Contributions

1. **Mechanistic Understanding:** This work provides the first mechanistic explanation connecting EoS dynamics to generalization through curvature self-regulation, moving beyond correlational observations.

2. **Unification:** Curvature homeostasis unifies previously disparate observations about learning rate effects, flat minima, and generalization into a coherent theoretical framework.

3. **Predictive Theory:** Unlike descriptive theories, curvature homeostasis makes quantitative predictions ($\text{BS} \approx 2/\eta$) that can guide practice.

### 3.3 Practical Impact

**Learning Rate Selection:** The relationship $\text{BS} \approx 2/\eta$ provides a principled approach to learning rate selection: practitioners can estimate the desired curvature regime and set $\eta \approx 2/\text{target BS}$.

**Large Model Training:** For foundation models where hyperparameter search is prohibitively expensive, curvature homeostasis offers guidance for setting learning rates based on desired generalization properties.

**Monitoring and Diagnostics:** Batch Sharpness can serve as a real-time training diagnostic, indicating whether the optimizer has reached the homeostatic regime.

### 3.4 Limitations and Future Directions

**Current Scope Limitations:**
- Validated primarily on CNNs; extension to Transformers requires additional investigation
- Constant learning rate assumption; interaction with LR schedules needs study
- SGD focus; behavior with Adam and other adaptive optimizers may differ

**Future Research Directions:**
1. Extension to Transformer architectures and attention mechanisms
2. Integration with learning rate scheduling strategies
3. Application to foundation model pretraining
4. Theoretical analysis of homeostatic dynamics using dynamical systems theory

### 3.5 Broader Impact

This research contributes to the workshop's goal of developing theory that guides practice in the large model era. By establishing curvature homeostasis as a fundamental mechanism, we provide:

- **Reduced computational waste:** Principled hyperparameter selection reduces failed training runs
- **Democratized access:** Smaller research groups can train models more efficiently with theoretical guidance
- **Environmental benefits:** Fewer wasted GPU hours translates to reduced energy consumption

The curvature homeostasis framework represents a step toward transforming deep learning from an art form requiring extensive trial-and-error into a principled engineering discipline guided by theoretical understanding.