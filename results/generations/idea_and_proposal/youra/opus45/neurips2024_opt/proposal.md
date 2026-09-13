# Research Proposal: Sharpness-Triggered Optimizer Scheduling for Efficient Large-Scale Transformer Training

## 1. Introduction

### 1.1 Background

The training of large language models (LLMs) has become one of the most computationally expensive endeavors in modern artificial intelligence. Training a single frontier model can cost tens of millions of dollars and consume energy equivalent to thousands of households' annual consumption. Despite these enormous costs, practitioners predominantly rely on a single optimizer—Adam—throughout the entire training process, applying it uniformly from initialization to convergence. This one-size-fits-all approach persists despite mounting theoretical and empirical evidence that the loss landscape curvature evolves dramatically across different training phases.

Recent advances in understanding neural network optimization dynamics have revealed that training naturally progresses through distinct regimes characterized by different sharpness properties. The "edge of stability" phenomenon, first rigorously characterized by Cohen et al. (2021), demonstrates that gradient descent operates at a critical boundary where the maximum Hessian eigenvalue $\lambda_{\max}$ stabilizes near $2/\eta$ (where $\eta$ is the learning rate). Subsequent work by Kalra and Barkeshli (2023) identified four distinct training phases: early transient, saturation, progressive sharpening, and edge of stability. These findings suggest that different optimization strategies may be optimal at different phases, yet no principled method exists to exploit this insight for improved training efficiency at scale.

The challenge of scaling optimization has become increasingly urgent with the advent of LLMs. Scaling laws established by Kaplan et al. (2020) and refined by Hoffmann et al. (2022) provide guidance on model size and data allocation, but the interaction between scaling and optimization dynamics remains poorly understood. Recent work by Noci et al. (2024) on "super consistency" of neural network landscapes under maximal update parameterization (μP) suggests that sharpness dynamics may be predictable across scales, potentially enabling principled optimizer scheduling that transfers across model sizes.

### 1.2 Research Objectives

This research proposes to develop and validate **Sharpness-Triggered Optimizer Scheduling (STOS)**, a principled framework for dynamically transitioning between optimizers during large-scale Transformer training based on real-time sharpness monitoring. Our specific objectives are:

1. **Validate the existence and reliability of edge of stability phenomena** in large-scale Transformer training (125M–1B+ parameters) across multiple random seeds and architectures.

2. **Develop a computationally efficient sharpness monitoring protocol** using critical sharpness measurements that adds less than 5% computational overhead.

3. **Establish optimal transition protocols** for switching from Adam to SGD (or other optimizers) when sharpness stabilizes at the edge of stability plateau.

4. **Demonstrate 10–20% improvement in compute efficiency** (measured as final loss achieved per FLOP) compared to fixed Adam baselines.

5. **Characterize scale-dependent transition dynamics** to enable extrapolation of optimal scheduling from smaller to larger models.

### 1.3 Significance

Success in this research would have substantial practical and scientific impact:

**Economic Impact:** A 10–20% reduction in training compute for large models translates to millions of dollars in savings per training run. For organizations training multiple models annually, cumulative savings could reach tens of millions of dollars.

**Environmental Impact:** Reduced compute directly translates to lower energy consumption and carbon emissions, addressing growing concerns about AI's environmental footprint.

**Scientific Contribution:** This work would establish the first principled framework connecting loss landscape geometry to optimizer selection, advancing our theoretical understanding of deep learning optimization.

**Democratization:** More efficient training enables smaller organizations and academic institutions to train competitive models, broadening participation in AI research.

## 2. Methodology

### 2.1 Theoretical Framework

Our approach is grounded in the hypothesis that training efficiency can be improved by matching optimizer characteristics to the evolving loss landscape geometry. We formalize this through the following framework.

**Definition 1 (Critical Sharpness).** Following Kalra et al. (2026), we define the critical sharpness $\lambda_c$ as:

$$\lambda_c = \frac{2 \cdot (L(\theta + \Delta\theta) - L(\theta))}{\|\Delta\theta\|^2}$$

where $\Delta\theta$ is a perturbation in the direction of the top Hessian eigenvector, estimated via power iteration. This measure approximates $\lambda_{\max}$ using only forward passes, requiring approximately 10 forward passes per measurement.

**Definition 2 (Edge of Stability Plateau).** We define the edge of stability plateau as the training regime where:

$$\left|\lambda_c - \frac{2}{\eta}\right| < \epsilon \cdot \frac{2}{\eta}$$

for a tolerance $\epsilon = 0.1$ (10% deviation) sustained over a window of $W$ consecutive measurements.

**Hypothesis (Optimizer-Phase Matching).** Under large-scale Transformer training, if we transition from Adam to SGD when the edge of stability plateau is detected, training efficiency improves because:
- Adam's per-parameter adaptivity efficiently navigates high-curvature early training
- SGD's implicit regularization provides advantages after the edge of stability plateau, helping find flatter, better-generalizing solutions

### 2.2 Sharpness Monitoring Protocol

We implement efficient sharpness tracking using the critical sharpness measure:

**Algorithm 1: Critical Sharpness Estimation**
```
Input: Model parameters θ, loss function L, perturbation scale δ, iterations K
Output: Critical sharpness estimate λ_c

1. Initialize random unit vector v ∈ R^d
2. For k = 1 to K:
   a. Compute gradient g = ∇L(θ)
   b. Compute Hessian-vector product: Hv ≈ (∇L(θ + δv) - g) / δ
   c. Update v ← Hv / ||Hv||
3. Compute perturbation: Δθ = δ · v
4. Compute λ_c = 2 · (L(θ + Δθ) - L(θ)) / ||Δθ||²
5. Return λ_c
```

We set $K = 5$ power iterations and $\delta = 10^{-4}$ based on preliminary experiments. Measurements are taken every $M = 100$ training steps, resulting in approximately 2–3% computational overhead.

### 2.3 Transition Detection and Execution

**Algorithm 2: Sharpness-Triggered Optimizer Scheduling (STOS)**
```
Input: Initial optimizer (Adam), target optimizer (SGD), 
       plateau window W, tolerance ε, measurement interval M
Output: Trained model with dynamic optimizer scheduling

1. Initialize Adam optimizer with learning rate η
2. Initialize sharpness history buffer H = []
3. transition_triggered = False

4. For each training step t:
   a. Perform standard training step with current optimizer
   
   b. If t mod M == 0:
      i.   Compute λ_c using Algorithm 1
      ii.  Append λ_c to H
      iii. If len(H) ≥ W and not transition_triggered:
           - Compute plateau_ratio = mean(|H[-W:] - 2/η|) / (2/η)
           - If plateau_ratio < ε:
             * Log transition point t_switch = t
             * Execute optimizer transition (Algorithm 3)
             * transition_triggered = True

5. Return trained model, transition_point t_switch
```

**Algorithm 3: Optimizer Transition Protocol**
```
Input: Current Adam state, target SGD configuration, blend_steps N_blend
Output: Initialized SGD optimizer

1. Extract Adam first moment m and second moment v
2. Initialize SGD with momentum μ = 0.9
3. Set SGD momentum buffer: b ← m / (√v + ε)  # Normalized direction
4. For steps 1 to N_blend:
   - Linearly interpolate: update = (1 - α) · Adam_update + α · SGD_update
   - where α increases from 0 to 1
5. Return fully transitioned SGD optimizer
```

We investigate both hard transitions ($N_{\text{blend}} = 0$) and gradual blending ($N_{\text{blend}} = 1000$ steps) in ablation studies.

### 2.4 Experimental Design

#### 2.4.1 Model Configurations

We use GPT-style decoder-only Transformers with the following configurations:

| Scale | Parameters | Layers | Hidden Dim | Heads | Batch Size |
|-------|------------|--------|------------|-------|------------|
| Small | 125M | 12 | 768 | 12 | 256 |
| Medium | 350M | 24 | 1024 | 16 | 256 |
| Large | 760M | 24 | 1536 | 16 | 512 |
| XL | 1.3B | 24 | 2048 | 32 | 512 |

All models use maximal update parameterization (μP) to ensure consistent sharpness dynamics across scales and enable hyperparameter transfer.

#### 2.4.2 Training Configuration

- **Dataset:** OpenWebText (38GB) or C4 subset (100B tokens)
- **Sequence Length:** 1024 tokens
- **Learning Rate:** Base LR = $3 \times 10^{-4}$ (transferred via μP)
- **Schedule:** Linear warmup (2000 steps) + cosine decay
- **Total Steps:** 100K steps (Small/Medium), 200K steps (Large/XL)
- **Precision:** Mixed precision (BF16) with FP32 master weights

#### 2.4.3 Experimental Conditions

**Condition 1 (Baseline):** Adam optimizer throughout training
- Adam hyperparameters: $\beta_1 = 0.9$, $\beta_2 = 0.95$, $\epsilon = 10^{-8}$, weight decay = 0.1

**Condition 2 (STOS):** Sharpness-triggered Adam → SGD transition
- Adam phase: Same as baseline
- SGD phase: Momentum = 0.9, weight decay = 0.1
- Transition: Triggered by edge of stability detection

**Condition 3 (Fixed-Schedule Ablation):** Adam → SGD at fixed fractions
- Transition points: 25%, 50%, 75% of total training
- Purpose: Isolate benefit of sharpness-based timing vs. any transition

**Condition 4 (Alternative Transitions):** Adam → Lion, Adam → AdaFactor
- Purpose: Evaluate generality across optimizer pairs

#### 2.4.4 Evaluation Metrics

**Primary Metric: Compute Efficiency**
$$\text{Efficiency} = \frac{L_{\text{baseline}}(F) - L_{\text{STOS}}(F)}{L_{\text{baseline}}(F)} \times 100\%$$

where $L(F)$ is the validation loss at compute budget $F$ (measured in FLOPs).

**Secondary Metrics:**
1. **FLOP-to-Target:** FLOPs required to reach target validation loss
2. **Final Validation Loss:** Cross-entropy on held-out validation set
3. **Downstream Performance:** Zero-shot accuracy on HellaSwag, LAMBADA, WinoGrande
4. **Transition Timing Consistency:** Standard deviation of detected transition points across seeds

#### 2.4.5 Statistical Analysis

- **Sample Size:** 5 random seeds per configuration (power analysis: Cohen's d = 0.8, power = 0.8, α = 0.05)
- **Primary Test:** Paired t-test comparing STOS vs. baseline at matched compute
- **Multiple Comparisons:** Bonferroni correction for scale-wise comparisons
- **Effect Size:** Report Cohen's d with 95% confidence intervals
- **Significance Threshold:** α = 0.05 (one-tailed for improvement hypothesis)

### 2.5 Validation Experiments

**Experiment 1: Edge of Stability Existence (SH1)**
- Train all model scales with Adam baseline
- Record sharpness trajectory every 100 steps
- Verify plateau detection at $\lambda_c \approx 2/\eta$ across scales and seeds
- Success criterion: Plateau detected in >90% of runs with <20% timing variance

**Experiment 2: Mechanism Validation (SH2)**
- Compare phase-specific optimizer performance:
  - Adam-only in early phase (steps 0 to transition)
  - SGD-only in late phase (transition to end)
  - Reversed schedule (SGD → Adam) as negative control
- Success criterion: Adam outperforms SGD in early phase; SGD matches/exceeds Adam in late phase

**Experiment 3: Efficiency Comparison (SH3)**
- Full STOS vs. baseline comparison across all scales
- Generate loss-vs-FLOP curves with confidence bands
- Success criterion: ≥10% efficiency improvement with p < 0.05

**Experiment 4: Scale-Dependent Dynamics**
- Analyze transition timing as function of model scale
- Test prediction: relative transition point (step/total) decreases with scale
- Fit scaling law: $t_{\text{switch}}/t_{\text{total}} = a \cdot N^{-b}$ where $N$ is parameter count

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical framework and preliminary evidence from the literature, we anticipate the following outcomes:

**Primary Outcome:** STOS will achieve 10–20% improvement in compute efficiency compared to Adam baselines. Specifically:
- 125M scale: 8–12% improvement (smaller models have less pronounced phase separation)
- 350M scale: 12–15% improvement
- 760M scale: 15–18% improvement
- 1.3B scale: 18–22% improvement (larger models benefit more from phase-matched optimization)

**Secondary Outcomes:**
1. Edge of stability plateau will be reliably detected at all scales with <15% timing variance across seeds
2. Optimal transition timing will shift earlier (relatively) at larger scales, following approximate power law
3. Gradual transition protocol will outperform hard switching by 2–3% additional efficiency
4. Downstream task performance will improve by 1–2% due to flatter minima from SGD regularization

### 3.2 Potential Challenges and Mitigations

**Challenge 1:** Sharpness plateau may be noisy or undetectable at certain scales.
*Mitigation:* Implement smoothed detection with exponential moving average; use ensemble of sharpness estimates.

**Challenge 2:** Optimizer transition may cause training instability.
*Mitigation:* Gradual blending protocol; learning rate re-warmup after transition; momentum transfer from Adam to SGD.

**Challenge 3:** Computational overhead of sharpness tracking may exceed efficiency gains.
*Mitigation:* Reduce measurement frequency; use cheaper sharpness approximations; amortize measurements across data parallel workers.

### 3.3 Broader Impact

**Scientific Impact:** This research establishes a new paradigm for adaptive optimization in deep learning, connecting geometric properties of the loss landscape to algorithmic choices. The framework opens avenues for:
- Automated optimizer selection based on training dynamics
- Theoretical analysis of optimizer-landscape interactions
- Extension to other training phases (fine-tuning, RLHF)

**Practical Impact:** Immediate applications include:
- Reduced training costs for LLM developers
- Lower barrier to entry for academic and smaller-scale research
- Integration into popular training frameworks (PyTorch, JAX)

**Environmental Impact:** A 15% reduction in training compute across the industry would save approximately 50,000 MWh annually (based on estimated 2024 LLM training energy consumption), equivalent to removing 7,000 cars from roads.

### 3.4 Future Directions

Success in this research opens several promising directions:
1. **Multi-phase scheduling:** Extending beyond two-phase (Adam → SGD) to multi-optimizer sequences
2. **Architecture-specific scheduling:** Adapting transition protocols for different architectures (MoE, SSMs)
3. **Scaling law integration:** Incorporating optimizer scheduling into compute-optimal scaling predictions
4. **Automated hyperparameter transfer:** Using sharpness dynamics to transfer not just learning rates but full optimizer configurations across scales

In conclusion, this research addresses a critical gap in large-scale optimization by developing principled, sharpness-aware optimizer scheduling. The potential for significant efficiency improvements, combined with strong theoretical grounding and practical applicability, positions this work to make substantial contributions to both the science and practice of training large language models.