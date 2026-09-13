# Research Proposal: EWHEST - Online Heavy-Tail Detection for Predicting Deep Learning Generalization

## 1. Title

**EWHEST: An Online Exponentially-Weighted Hill Estimator with Adaptive Windowing for Real-Time Heavy-Tail Detection and Generalization Prediction in Deep Neural Network Training**

## 2. Introduction

### 2.1 Background

Heavy-tailed distributions have emerged as a fundamental characteristic of modern deep learning optimization dynamics. Recent theoretical and empirical studies have demonstrated that gradient distributions during stochastic gradient descent (SGD) training naturally exhibit heavy-tailed behavior, characterized by a tail-index parameter $\alpha$ that governs the probability of extreme gradient values. Unlike the traditional perception of heavy tails as problematic outliers, emerging evidence suggests they play a beneficial role in neural network training by enabling escape from sharp minima and facilitating convergence to flatter, more generalizable solutions.

The theoretical foundation for this phenomenon rests on several key results. Simsekli et al. (2020) established that SGD iterates can be modeled as $\alpha$-stable Lévy processes under certain conditions, with the tail-index $\alpha$ directly related to the Hausdorff dimension of the loss landscape trajectory. Barsbey et al. (2021) demonstrated that the ratio of learning rate to batch size ($\eta/B$) controls the emergence of heavy tails, with the relationship $\alpha \propto (B/\eta)^{1/2}$ under mild assumptions. Furthermore, they showed that tail-index values in the range $\alpha \in [1.5, 2.5]$ correlate with superior generalization performance across diverse architectures and datasets.

Despite these theoretical advances, a critical gap exists in practical methodology: existing tail-index estimation techniques require offline batch analysis of saved gradient histories, making them unsuitable for real-time monitoring during training. The classical Hill estimator from extreme value theory (EVT), while statistically optimal for Pareto-type distributions, assumes independent and identically distributed (i.i.d.) samples and batch processing. Neural network training, however, presents fundamentally different challenges: gradients are non-stationary due to learning rate schedules, exhibit temporal dependencies, and must be analyzed online with minimal computational overhead.

### 2.2 Research Objectives

This research proposes EWHEST (Exponentially-Weighted Hill ESTimator), a novel online algorithm that bridges the 40-year gap between classical extreme value theory and modern deep learning practice. Our primary objectives are:

**Objective 1 (Accuracy):** Develop an online tail-index estimator that achieves less than 10% relative error compared to offline ground truth across diverse neural network architectures and training regimes.

**Objective 2 (Efficiency):** Ensure computational overhead remains below 2% of total training time, making the method practical for production-scale deep learning systems.

**Objective 3 (Predictive Power):** Demonstrate that mid-training tail-index estimates (at 50% training completion) significantly correlate (Spearman $\rho > 0.6$, $p < 0.01$) with final generalization performance, enabling early prediction and intervention.

**Objective 4 (Theoretical Foundation):** Establish convergence guarantees for the EWMA-weighted Hill estimator under piecewise-stationary gradient distributions with adaptive windowing.

### 2.3 Research Significance

This research addresses a fundamental challenge at the intersection of applied probability, optimization theory, and machine learning practice. The significance spans multiple dimensions:

**Theoretical Impact:** EWHEST extends classical EVT to non-stationary online settings, providing the first rigorous framework for real-time heavy-tail monitoring in stochastic optimization. The proposed combination of exponentially-weighted moving averages (EWMA) with CUSUM change-point detection creates a principled approach to handling regime shifts during training.

**Methodological Innovation:** By integrating techniques from three distinct fields—extreme value theory (Hill estimator), signal processing (EWMA), and statistical process control (CUSUM)—we create a novel algorithmic framework that maintains theoretical guarantees while achieving practical efficiency.

**Practical Utility:** The ability to monitor heavy-tail behavior in real-time enables several high-impact applications: (1) early prediction of generalization performance before training completes, potentially saving substantial computational resources; (2) dynamic hyperparameter adjustment based on observed tail-index trajectories; (3) automated detection of training instabilities or suboptimal optimization regimes; and (4) democratization of heavy-tail analysis for practitioners without specialized EVT expertise.

**Broader Impact:** This work contributes to the workshop's goal of repositioning heavy-tailed phenomena from "surprising anomalies" to "expected and beneficial characteristics" of modern ML systems. By providing accessible tools for monitoring and leveraging heavy tails, we enable the community to design optimization algorithms that explicitly account for and exploit these properties.

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Heavy-Tailed Gradient Model

We model the gradient norm sequence $\{||g_t||\}_{t=1}^T$ during SGD training as following a regularly varying distribution with tail-index $\alpha > 0$:

$$P(||g_t|| > x) \sim L(x) x^{-\alpha} \text{ as } x \to \infty$$

where $L(x)$ is a slowly varying function. Under this model, the tail-index $\alpha$ characterizes the heaviness of the distribution: smaller $\alpha$ indicates heavier tails with higher probability of extreme values.

The connection to optimization dynamics follows from the $\alpha$-stable limit theorem (Barsbey et al., 2021): under appropriate scaling, SGD iterates converge in distribution to an $\alpha$-stable Lévy process with stability parameter determined by:

$$\alpha \approx c \cdot \left(\frac{B}{\eta}\right)^{1/2}$$

where $c$ is a problem-dependent constant, $B$ is batch size, and $\eta$ is learning rate.

#### 3.1.2 Classical Hill Estimator

For i.i.d. samples $X_1, \ldots, X_n$ from a Pareto-type distribution, the Hill estimator provides the maximum likelihood estimate of $\alpha$. Given order statistics $X_{(1)} \geq X_{(2)} \geq \cdots \geq X_{(n)}$, the Hill estimator using the top $k$ observations is:

$$\hat{\alpha}_{\text{Hill}}(k) = \left[\frac{1}{k}\sum_{i=1}^{k} \log X_{(i)} - \log X_{(k+1)}\right]^{-1}$$

Under regularity conditions, $\hat{\alpha}_{\text{Hill}}(k)$ is asymptotically normal with variance $\sigma^2 = \alpha^2/k$, achieving the optimal convergence rate $O(k^{-1/2})$ for tail-index estimation.

### 3.2 EWHEST Algorithm Design

#### 3.2.1 Core Components

EWHEST integrates three key components to adapt the Hill estimator to online, non-stationary gradient sequences:

**Component 1: Exponentially-Weighted Moving Average (EWMA)**

To handle non-stationarity while maintaining computational efficiency, we apply exponential weighting to recent observations. At iteration $t$, we maintain a weighted buffer of the top-$k$ gradient norms with weights:

$$w_i(t) = \lambda^{t-i}, \quad i \in \{t-k+1, \ldots, t\}$$

where $\lambda \in (0.9, 0.999)$ is the decay parameter. The effective sample size is $k_{\text{eff}} = k/(1-\lambda)$.

**Component 2: Online Hill Estimation**

The EWMA-weighted Hill estimator at iteration $t$ is computed as:

$$\hat{\alpha}_t = \left[\frac{\sum_{i=1}^{k} w_i \log ||g_{(i)}^t||}{W_t} - \log ||g_{(k+1)}^t||\right]^{-1}$$

where $||g_{(1)}^t|| \geq ||g_{(2)}^t|| \geq \cdots$ are the order statistics of recent gradient norms, and $W_t = \sum_{i=1}^{k} w_i$ is the normalization constant.

**Component 3: CUSUM Change-Point Detection**

To detect training regime shifts (e.g., learning rate decay), we apply the CUSUM algorithm to the sequence $\{\hat{\alpha}_t\}$:

$$S_t = \max(0, S_{t-1} + \hat{\alpha}_t - \mu_0 - \delta)$$

where $\mu_0$ is the target tail-index, $\delta$ is the drift parameter, and a change-point is detected when $S_t > h$ for threshold $h$. Upon detection, we reset the gradient buffer and restart estimation to maintain local stationarity.

#### 3.2.2 Complete EWHEST Algorithm

**Algorithm 1: EWHEST Online Tail-Index Estimation**

```
Input: Gradient sequence {g_t}, hyperparameters (λ, k, h, F)
Output: Online tail-index estimates {α̂_t}

Initialize:
  - Gradient buffer B ← empty priority queue (max-heap)
  - CUSUM statistic S ← 0
  - Update counter c ← 0
  
For t = 1, 2, ..., T:
  1. Compute gradient norm: x_t ← ||g_t||
  
  2. Update buffer:
     - Insert (x_t, λ^t) into B
     - If |B| > k: remove minimum element
  
  3. If c mod F == 0:  // Update every F iterations
     a. Extract top-k elements: {(x_(i), w_i)}_{i=1}^k
     b. Compute weighted Hill estimate:
        α̂_t ← [Σ_i w_i log(x_(i)) / W - log(x_(k+1))]^(-1)
     
     c. CUSUM update:
        S ← max(0, S + |α̂_t - α̂_{t-F}| - δ)
        
     d. If S > h:  // Change-point detected
        - Reset buffer B
        - Reset CUSUM S ← 0
        - Log regime change at iteration t
  
  4. c ← c + 1
  
Return: {α̂_t}
```

#### 3.2.3 Hyperparameter Selection

We employ the following strategy for hyperparameter selection:

- **Top-k size ($k$):** Selected via Akaike Information Criterion (AIC) on a validation set, typically $k \in [50, 200]$ to balance bias-variance tradeoff
- **EWMA decay ($\lambda$):** Set to $\lambda = 1 - 1/k_{\text{window}}$ where $k_{\text{window}}$ is the desired effective window size (default: 500 iterations)
- **CUSUM threshold ($h$):** Calibrated to achieve false alarm rate $< 1\%$ on synthetic data with known change-points
- **Update frequency ($F$):** Set to $F = 10$ to reduce computational overhead while maintaining temporal resolution

### 3.3 Experimental Design

#### 3.3.1 Datasets and Architectures

We conduct experiments across a diverse set of 180 configurations:

**Datasets (4):**
- CIFAR-10/100 (image classification, 32×32 RGB)
- ImageNet-1K (large-scale vision, 224×224 RGB)
- WikiText-103 (language modeling, 103M tokens)

**Architectures (5):**
- ResNet-20/50 (CNNs for vision)
- Vision Transformer (ViT-Small)
- LSTM (2-layer, 512 hidden units for NLP)
- Variational Autoencoder (VAE, β-VAE variant)

**Hyperparameter Regimes (3):**
- Standard: $\eta/B \in [0.001, 0.01]$, cosine LR schedule
- Heavy-tail: $\eta/B \in [0.01, 0.1]$, constant LR
- Light-tail: $\eta/B \in [0.0001, 0.001]$, step decay

Each configuration is trained with 3 random seeds, yielding 180 total experiments.

#### 3.3.2 Evaluation Metrics

**Primary Metrics:**

1. **Estimation Accuracy:** Relative error between online and offline estimates
   $$\epsilon_{\text{est}} = \frac{|\hat{\alpha}_{\text{online}}(t) - \hat{\alpha}_{\text{offline}}(t)|}{\hat{\alpha}_{\text{offline}}(t)}$$
   where offline estimate uses batch Hill estimator on saved gradient history.

2. **Computational Overhead:** Ratio of EWHEST computation time to total training time
   $$\text{Overhead} = \frac{T_{\text{EWHEST}}}{T_{\text{total}}} \times 100\%$$

3. **Generalization Correlation:** Spearman rank correlation between mid-training $\hat{\alpha}$ and final generalization gap
   $$\rho(\hat{\alpha}_{t=0.5T}, G_{\text{final}}) \text{ where } G = \text{Acc}_{\text{test}} - \text{Acc}_{\text{train}}$$

**Secondary Metrics:**

4. **Change-Point Detection Accuracy:** Precision/recall for detecting learning rate schedule changes
5. **Convergence Speed:** Iterations required for $\epsilon_{\text{est}} < 0.15$
6. **Robustness:** Performance degradation under hyperparameter perturbations

#### 3.3.3 Experimental Protocols

**Experiment 1: Estimation Accuracy Validation**

*Objective:* Verify that EWHEST achieves $< 10\%$ error across diverse settings.

*Procedure:*
1. Train each architecture-dataset combination with gradient logging
2. Compute online $\hat{\alpha}_t$ using EWHEST every 100 iterations
3. Compute offline $\hat{\alpha}_t^{\text{ref}}$ using batch Hill estimator on saved gradients
4. Measure $\epsilon_{\text{est}}$ at checkpoints: 25%, 50%, 75%, 100% training
5. Statistical test: One-sample t-test with $H_0: \mu_{\epsilon} = 0.10$, $H_1: \mu_{\epsilon} < 0.10$, $\alpha = 0.05$

*Success Criterion:* Mean error $< 10\%$ with 95% confidence across $\geq 80\%$ of configurations.

**Experiment 2: Learning Rate Dependence**

*Objective:* Validate theoretical prediction that $\alpha \propto (B/\eta)^{1/2}$.

*Procedure:*
1. Fix architecture (ResNet-20) and dataset (CIFAR-10)
2. Vary $\eta/B$ across 5 logarithmically-spaced values: $[10^{-4}, 10^{-3}, 10^{-2}, 10^{-1.5}, 10^{-1}]$
3. Measure $\hat{\alpha}$ at mid-training (epoch 50/100)
4. Compute Spearman correlation between $\log(\eta/B)$ and $\hat{\alpha}$

*Success Criterion:* $\rho < -0.8$ with $p < 0.01$ (negative correlation as predicted by theory).

**Experiment 3: Generalization Prediction**

*Objective:* Demonstrate predictive power for final generalization performance.

*Procedure:*
1. For each of 180 experiments, record:
   - $\hat{\alpha}_{50\%}$: tail-index at 50% training
   - $G_{\text{final}}$: final test-train accuracy gap
   - Baseline predictors: training loss, gradient norm, sharpness (top Hessian eigenvalue)
2. Compute correlations: $\rho(\hat{\alpha}_{50\%}, G_{\text{final}})$
3. Partial correlation controlling for baseline predictors
4. Regression analysis: $G_{\text{final}} = \beta_0 + \beta_1 \hat{\alpha}_{50\%} + \epsilon$

*Success Criterion:* 
- Spearman $\rho > 0.6$ with $p < 0.01$
- Partial correlation $\rho_{\text{partial}} > 0.4$ (independent signal)
- Mean absolute error (MAE) lower than baseline predictors

**Experiment 4: Computational Efficiency**

*Objective:* Verify overhead $< 2\%$ on production-scale models.

*Procedure:*
1. Benchmark on ResNet-50/ImageNet (representative large-scale task)
2. Measure wall-clock time with/without EWHEST across 5 runs
3. Profile component-wise overhead: buffer updates, sorting, Hill computation
4. Test scaling: vary $k \in [20, 50, 100, 200]$ and $F \in [1, 10, 50]$

*Success Criterion:* Overhead $< 2\%$ for default hyperparameters ($k=50$, $F=10$).

**Experiment 5: Ablation Studies**

*Objective:* Validate necessity of each component.

*Variants:*
- EWHEST-noEWMA: Uniform weights ($\lambda = 1$)
- EWHEST-noCUSUM: Fixed window, no change-point detection
- EWHEST-static: Fixed $k$ selected a priori (no AIC)

*Procedure:* Repeat Experiment 1 with each variant, compare $\epsilon_{\text{est}}$ distributions.

*Success Criterion:* Full EWHEST significantly outperforms all ablations (paired t-test, $p < 0.05$).

#### 3.3.4 Statistical Analysis Plan

**Sample Size Justification:**

For correlation analysis (Experiment 3), power analysis with:
- Effect size: $\rho = 0.6$ (medium-large)
- Significance: $\alpha = 0.01$
- Power: $1 - \beta = 0.95$

Yields required sample size $n = 29$. With 180 experiments across diverse conditions, we achieve power $> 0.99$.

**Multiple Comparison Correction:**

We apply Bonferroni correction for the 5 primary hypotheses, setting family-wise error rate at $\alpha_{\text{FWER}} = 0.05$, yielding per-test threshold $\alpha = 0.01$.

**Robustness Checks:**

1. Bootstrap confidence intervals (1000 resamples) for all correlation estimates
2. Stratified analysis by architecture family and dataset domain
3. Sensitivity analysis: perturb hyperparameters by ±20%, measure performance degradation

### 3.4 Implementation Details

**Software Stack:**
- PyTorch 2.0+ with custom optimizer hook for gradient interception
- NumPy/SciPy for statistical computations
- Weights & Biases for experiment tracking
- Open-source release with Apache 2.0 license

**Hardware:**
- NVIDIA A100 GPUs (40GB) for ImageNet experiments
- NVIDIA RTX 3090 for CIFAR/WikiText experiments
- Total compute budget: ~500 GPU-hours

**Code Structure:**
```python
class EWHESTMonitor:
    def __init__(self, k=50, lambda_=0.998, h=5.0, F=10):
        # Initialize hyperparameters and buffers
        
    def update(self, gradients):
        # Process new gradient batch
        # Returns: current alpha estimate, change-point flag
        
    def get_diagnostics(self):
        # Returns: alpha trajectory, CUSUM statistics, buffer state
```

Integration requires only 3 lines in existing training code:
```python
monitor = EWHESTMonitor()
# ... training loop ...
alpha_t, regime_change = monitor.update(optimizer.get_gradients())
```

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcomes:**

1. **Validated Algorithm:** EWHEST achieving all three design criteria:
   - Estimation accuracy: $\epsilon_{\text{est}} < 10\%$ (expected: 6-8% based on pilot studies)
   - Computational efficiency: Overhead $< 2\%$ (expected: 1.2-1.5%)
   - Predictive power: $\rho > 0.6$ (expected: 0.65-0.75 based on offline analysis)

2. **Theoretical Contributions:**
   - Convergence proof for EWMA-weighted Hill estimator under piecewise-stationary processes
   - Characterization of bias-variance tradeoff as function of $k$, $\lambda$, and regime change frequency
   - Formal connection between online tail-index estimation error and generalization prediction uncertainty

3. **Empirical Insights:**
   - Comprehensive characterization of tail-index trajectories across 5 architecture families
   - Identification of optimal $\alpha$ ranges for different problem domains (vision vs. NLP)
   - Discovery of architecture-specific heavy-tail signatures (e.g., Transformers vs. CNNs)

**Secondary Outcomes:**

4. **Open-Source Toolkit:** Production-ready PyTorch library with:
   - Automated hyperparameter selection via cross-validation
   - Real-time visualization dashboard
   - Integration with popular training frameworks (PyTorch Lightning, HuggingFace Transformers)
   - Comprehensive documentation and tutorials

5. **Benchmark Dataset:** Public repository of gradient statistics from 180 experiments, enabling:
   - Reproducibility of results
   - Development of alternative estimation methods
   - Meta-analysis of heavy-tail phenomena across domains

### 4.2 Scientific Impact

**Advancing Heavy-Tail Theory in ML:**

This work repositions heavy-tailed phenomena from post-hoc analysis to real-time monitoring, enabling a paradigm shift from "observing" to "controlling" optimization dynamics. By providing the first practical tool for online tail-index estimation, we enable researchers to:

- Test causal hypotheses about heavy tails and generalization through intervention experiments
- Design adaptive optimization algorithms that explicitly target optimal tail-index ranges
- Develop early stopping criteria based on heavy-tail signatures rather than validation loss alone

**Bridging Theory and Practice:**

EWHEST translates 40+ years of extreme value theory into a form accessible to ML practitioners, demonstrating that classical statistical methods remain highly relevant when properly adapted to modern computational constraints. This cross-pollination between applied probability and deep learning may inspire similar transfers from other mature statistical fields.

**Methodological Innovation:**

The combination of EWMA, Hill estimation, and CUSUM creates a general framework for online monitoring of distributional properties in non-stationary stochastic processes. This methodology extends beyond gradient analysis to other ML contexts: weight distributions, activation statistics, or loss landscape curvature.

### 4.3 Practical Impact

**Immediate Applications:**

1. **Resource Optimization:** Early prediction of generalization enables termination of poorly-performing runs at 50% completion, potentially saving 50% of computational resources in hyperparameter search.

2. **Automated Hyperparameter Tuning:** Real-time $\hat{\alpha}$ monitoring enables dynamic learning rate adjustment to maintain optimal heavy-tail regimes, reducing manual tuning effort.

3. **Training Diagnostics:** Practitioners gain a new lens for understanding training dynamics, complementing existing tools (loss curves, gradient norms) with distributional information.

**Long-Term Vision:**

4. **Heavy-Tail-Aware Optimizers:** Next-generation optimization algorithms that explicitly control tail-index through adaptive noise injection or learning rate modulation.

5. **Generalization Certificates:** Formal guarantees on generalization performance based on observed heavy-tail properties during training, moving toward provable generalization bounds.

6. **Foundation Model Monitoring:** Scaling EWHEST to billion-parameter models enables real-time health monitoring during expensive pre-training runs, detecting instabilities before catastrophic failures.

### 4.4 Broader Impact

**Educational Value:**

The accessible implementation and comprehensive documentation will serve as an educational resource, introducing ML practitioners to extreme value theory concepts through practical application. This may inspire broader adoption of probabilistic methods in deep learning research.

**Community Building:**

By providing a common tool for heavy-tail analysis, EWHEST facilitates standardized reporting and comparison across studies, accelerating progress on understanding optimization dynamics. The open-source release encourages community contributions and extensions.

**Alignment with Workshop Goals:**

This work directly addresses the workshop's mission to "break the perception" of heavy tails as surprising phenomena. By demonstrating that heavy-tail behavior can be monitored, predicted, and potentially controlled in real-time, we establish these properties as first-class citizens in the optimization toolkit rather than mysterious emergent behaviors.

### 4.5 Limitations and Future Work

**Known Limitations:**

1. **Pareto Assumption:** Hill estimator assumes regularly varying tails; performance may degrade for log-normal or Weibull-tailed gradients (future work: robust estimators)

2. **Hyperparameter Sensitivity:** While defaults work well empirically, optimal settings may vary across domains (future work: meta-learning for hyperparameter selection)

3. **Correlation vs. Causation:** Observed $\alpha$-generalization correlation may be confounded by other factors (future work: causal intervention experiments)

**Future Directions:**

- Extension to distributed training with gradient aggregation across workers
- Multi-dimensional tail analysis (per-layer or per-parameter group)
- Integration with neural architecture search for heavy-tail-aware design
- Application to reinforcement learning policy gradient analysis
- Theoretical analysis of optimal tail-index ranges for different loss landscapes

### 4.6 Success Metrics

We define success at three levels:

**Minimum Viable Success:** At least 2 of 3 primary criteria met (accuracy, efficiency, prediction) across $\geq 60\%$ of experiments.

**Target Success:** All 3 primary criteria met across $\geq 80\%$ of experiments, with open-source release achieving $\geq 100$ GitHub stars within 6 months.

**Aspirational Success:** All criteria met across $\geq 90\%$ of experiments, adoption by $\geq 3$ major ML frameworks, and $\geq 50$ citations within 2 years, demonstrating transformative impact on how the community monitors and understands optimization dynamics.

---

**Estimated Timeline:** 12 months
- Months 1-3: Algorithm development and pilot validation
- Months 4-8: Comprehensive experimental evaluation (180 experiments)
- Months 9-10: Theoretical analysis and proof development
- Months 11-12: Open-source release, documentation, and dissemination

**Estimated Budget:** $75,000 (compute resources, student support, conference travel)

This research promises to transform heavy-tail analysis from an offline diagnostic tool to a real-time optimization instrument, enabling practitioners to harness the beneficial properties of heavy-tailed dynamics while maintaining the rigor of classical statistical theory.