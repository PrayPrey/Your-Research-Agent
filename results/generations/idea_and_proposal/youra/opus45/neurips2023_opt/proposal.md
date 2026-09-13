# Research Proposal: Criticality-Aware Optimizer Scheduling for Accelerating Generalization Phase Transitions

## 1. Introduction

### 1.1 Background

Deep learning optimization has witnessed remarkable empirical success, yet fundamental phenomena governing generalization remain poorly understood. Two particularly puzzling observations—*grokking* and *double descent*—challenge conventional wisdom about the relationship between training dynamics and generalization. Grokking, first documented by Power et al. (2022), describes the sudden emergence of generalization long after a model has achieved perfect training accuracy, sometimes requiring orders of magnitude more training steps. Double descent reveals non-monotonic test error behavior as model complexity increases, contradicting classical bias-variance tradeoffs.

These phenomena are not merely academic curiosities; they represent significant computational waste in modern deep learning. When training large language models (LLMs) costing millions of dollars, unpredictable generalization timing translates directly to wasted compute, energy, and carbon emissions. The inability to predict when—or whether—a model will generalize forces practitioners into conservative over-training strategies.

Recent theoretical advances offer a promising lens for understanding these phenomena. Research on neural network criticality (Vock & Meisel, 2025) demonstrates that deep networks perform optimally when operating near dynamical criticality—a regime borrowed from statistical physics where systems exhibit maximal information processing capacity. Simultaneously, Kumar et al. (2023) established that grokking corresponds to a transition from "lazy" training (where networks behave like linear models) to "rich" training (where networks learn meaningful representations). The edge-of-stability phenomenon (Cohen et al., 2021) further reveals that gradient descent naturally navigates toward critical Hessian dynamics.

Despite these insights, no existing method actively exploits the connection between criticality and generalization phase transitions. Current optimizer scheduling approaches—cosine annealing, warmup strategies, adaptive methods like Adam—are designed without consideration of the network's dynamical state relative to criticality.

### 1.2 Research Objectives

This research proposes **Criticality-Aware Optimizer Scheduling (CAOS)**, a principled framework for accelerating and predicting generalization phase transitions by adaptively maintaining neural networks near critical dynamics. Our specific objectives are:

1. **Develop computationally tractable criticality proxy metrics** suitable for large-scale training, combining gradient flow statistics with Hutchinson-based Hessian trace estimation.

2. **Design a PID-style adaptive control mechanism** that modulates optimizer hyperparameters (learning rate, weight decay, momentum) to maintain networks near criticality.

3. **Establish causal relationships** between criticality maintenance and accelerated phase transitions through bidirectional modulation experiments.

4. **Validate scale-transferable critical exponents** that enable predictions from small-scale experiments to inform large-scale training decisions.

### 1.3 Significance

Success in this research would yield transformative benefits for the machine learning community:

- **Computational Efficiency**: Achieving ≥30% faster grokking translates to substantial cost savings in LLM training, potentially millions of dollars per model.
- **Predictability**: Scale-transferable critical exponents would enable practitioners to predict generalization timing from small-scale experiments, fundamentally changing hyperparameter search strategies.
- **Theoretical Understanding**: Establishing causal links between criticality and generalization would unify disparate observations (grokking, double descent, edge-of-stability) under a coherent theoretical framework.
- **Environmental Impact**: Reduced training time directly decreases energy consumption and carbon footprint of AI development.

## 2. Methodology

### 2.1 Theoretical Framework

We formalize the hypothesis that optimal learning occurs at criticality through a three-step causal mechanism:

**Step 1 (Optimizer → Dynamics):** Optimizer hyperparameters $\theta_{opt} = (\eta, \lambda, \beta)$ (learning rate, weight decay, momentum) modulate the gradient and Hessian dynamics of the loss landscape:

$$\frac{d\mathbf{w}}{dt} = -\eta \nabla_\mathbf{w} \mathcal{L}(\mathbf{w}) - \lambda \mathbf{w} + \beta \frac{d\mathbf{w}}{dt}\bigg|_{t-1}$$

**Step 2 (Dynamics → Criticality):** These dynamics determine the network's proximity to criticality, characterized by the spectral properties of the Hessian $\mathbf{H} = \nabla^2_\mathbf{w} \mathcal{L}$. At criticality, the ratio of the maximum Hessian eigenvalue to the learning rate approaches a critical value:

$$\chi = \frac{\lambda_{max}(\mathbf{H})}{\eta} \approx 2$$

**Step 3 (Criticality → Transitions):** Near criticality, the network achieves maximum information processing capacity, facilitating the lazy-to-rich transition that underlies grokking:

$$\mathcal{I}_{capacity} \propto \xi^{d_{eff}}$$

where $\xi$ is the correlation length (diverging at criticality) and $d_{eff}$ is the effective dimensionality.

### 2.2 Criticality Proxy Metrics

Direct computation of Hessian eigenvalues is intractable for large models. We propose two complementary proxy metrics:

**Metric 1: Gradient Flow Statistics (GFS)**

We track the normalized gradient covariance across mini-batches:

$$\text{GFS} = \frac{\text{Tr}(\text{Cov}[\nabla_\mathbf{w} \mathcal{L}_b])}{\|\mathbb{E}[\nabla_\mathbf{w} \mathcal{L}_b]\|^2}$$

where $\mathcal{L}_b$ denotes the loss on mini-batch $b$. At criticality, gradient directions exhibit maximal diversity (high GFS) while maintaining coherent descent (bounded denominator).

**Metric 2: Hutchinson Hessian Trace Estimator (HHTE)**

Using the Hutchinson trace estimator with $k$ random vectors $\mathbf{v}_i \sim \mathcal{N}(0, \mathbf{I})$:

$$\text{Tr}(\mathbf{H}) \approx \frac{1}{k} \sum_{i=1}^{k} \mathbf{v}_i^\top \mathbf{H} \mathbf{v}_i$$

The Hessian-vector products $\mathbf{H}\mathbf{v}_i$ are computed efficiently via automatic differentiation. We normalize by parameter count to obtain:

$$\text{HHTE} = \frac{\text{Tr}(\mathbf{H})}{|\mathbf{w}|}$$

**Combined Criticality Score:**

$$C_{proxy} = \alpha \cdot \text{normalize}(\text{GFS}) + (1-\alpha) \cdot \text{normalize}(\text{HHTE})$$

where $\alpha$ is tuned per architecture family. The target criticality score is $C_{target} \approx 1.0$ (after normalization).

### 2.3 PID-Style Adaptive Control

We employ a proportional-integral-derivative (PID) controller to modulate optimizer hyperparameters based on the criticality error $e_t = C_{target} - C_{proxy}(t)$:

$$\Delta \eta_t = K_p \cdot e_t + K_i \cdot \sum_{\tau=0}^{t} e_\tau + K_d \cdot (e_t - e_{t-1})$$

The learning rate update follows:

$$\eta_{t+1} = \text{clip}(\eta_t + \Delta \eta_t, \eta_{min}, \eta_{max})$$

Similar controllers modulate weight decay $\lambda$ and momentum $\beta$, with architecture-specific gain parameters $(K_p, K_i, K_d)$ determined through preliminary calibration.

**Control Logic:**
- When $C_{proxy} < C_{target}$ (subcritical): Increase $\eta$, decrease $\lambda$ to amplify dynamics
- When $C_{proxy} > C_{target}$ (supercritical): Decrease $\eta$, increase $\lambda$ to stabilize dynamics

### 2.4 Experimental Design

#### 2.4.1 Staged Validation Protocol

**Stage 1: Toy Scale ($10^5$ parameters)**
- Architectures: 3-layer MLPs on modular arithmetic (grokking benchmark)
- Purpose: Validate basic mechanism, tune PID gains
- Compute: ~100 GPU-hours

**Stage 2: Medium Scale ($10^7$ parameters)**
- Architectures: ResNet-18 on CIFAR-10/100, small Transformers on WikiText-2
- Purpose: Test generalization across architectures, validate scale transfer
- Compute: ~1,000 GPU-hours

**Stage 3: Large Scale ($10^9$ parameters)**
- Architectures: GPT-2 scale Transformers on OpenWebText
- Purpose: Validate practical applicability, measure real-world speedups
- Compute: ~10,000 GPU-hours

#### 2.4.2 Baseline Comparisons

1. **Standard Training**: Constant learning rate with step decay
2. **Cosine Annealing**: Standard cosine schedule with warmup
3. **AdamW**: Adaptive learning rate baseline
4. **Lookahead + RAdam**: State-of-the-art optimizer combination
5. **Edge-of-Stability Aware**: Learning rate clipped to maintain $\eta \lambda_{max} < 2$

#### 2.4.3 Causality Verification (Bidirectional Modulation)

To establish causality rather than mere correlation, we conduct intervention experiments:

**Experiment A (Push Toward Criticality):**
Starting from subcritical initialization, actively modulate toward $C_{target} = 1.0$.
- Prediction: Accelerated grokking

**Experiment B (Push Away from Criticality):**
Starting from near-critical state, actively modulate toward $C_{target} = 0.5$ (subcritical) or $C_{target} = 1.5$ (supercritical).
- Prediction: Delayed or prevented grokking

**Experiment C (Maintain Criticality vs. Natural Drift):**
Compare CAOS against allowing natural drift from critical initialization.
- Prediction: CAOS maintains faster generalization

#### 2.4.4 Scale Transfer Validation

We extract critical exponents from small-scale experiments:

$$T_{grok} \propto N^{\gamma}$$

where $T_{grok}$ is grokking time and $N$ is parameter count. We measure $\gamma$ at toy scale and predict medium-scale timing, validating within 20% error tolerance.

### 2.5 Evaluation Metrics

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| Grokking Speedup | $\frac{T_{grok}^{baseline} - T_{grok}^{CAOS}}{T_{grok}^{baseline}}$ | ≥30% |
| Proxy-Transition Correlation | Pearson $r$ between $C_{proxy}$ trajectory and $T_{grok}$ | $r > 0.5$ |
| Scale Prediction Error | $\frac{|T_{grok}^{predicted} - T_{grok}^{actual}|}{T_{grok}^{actual}}$ | <20% |
| Final Test Accuracy | Post-transition test accuracy | ≥ baseline |
| Compute Overhead | Additional FLOPs for criticality estimation | <20% |

### 2.6 Statistical Analysis

- **Sample Size**: $n \geq 15$ random seeds per condition (power analysis: $d=0.8$, power$=0.8$, $\alpha=0.05$)
- **Primary Test**: Paired t-test with Bonferroni correction for multiple comparisons
- **Effect Size**: Cohen's $d$ with 95% confidence intervals
- **Reporting**: Mean ± SD, exact p-values, effect sizes for all comparisons

### 2.7 Implementation Details

**Software Stack:**
- PyTorch with custom optimizer wrapper
- Automatic differentiation for Hessian-vector products
- Distributed training via PyTorch DDP for large-scale experiments

**Computational Requirements:**
- Hutchinson estimator: $k=10$ random vectors, computed every 100 steps
- GFS: Rolling window of 50 mini-batches
- PID update frequency: Every 100 training steps

## 3. Expected Outcomes & Impact

### 3.1 Primary Outcomes

1. **Validated CAOS Framework**: A principled, computationally tractable method for criticality-aware optimizer scheduling, demonstrated across MLPs, ResNets, and Transformers.

2. **Causal Evidence**: Rigorous bidirectional modulation experiments establishing that criticality maintenance *causes* (not merely correlates with) accelerated generalization.

3. **Scale-Transferable Predictions**: Empirically validated critical exponents enabling small-scale experiments to predict large-scale training dynamics within 20% error.

4. **Open-Source Implementation**: Production-ready code integrated with PyTorch, enabling immediate adoption by the community.

### 3.2 Quantitative Targets

- **P1**: ≥30% reduction in grokking time ($p < 0.05$, $n \geq 15$)
- **P2**: Proxy-transition correlation $r > 0.5$
- **P3**: Scale prediction error <20%
- **P4**: Bidirectional modulation confirms causality with effect size $d > 0.8$

### 3.3 Broader Impact

**Scientific Impact:**
This work would unify three previously disconnected phenomena—grokking, double descent, and edge-of-stability—under the theoretical framework of dynamical criticality. This represents a significant step toward a principled theory of deep learning optimization.

**Practical Impact:**
For organizations training large language models, a 30% reduction in training time translates to:
- Cost savings of millions of dollars per model
- Reduced energy consumption and carbon emissions
- Faster iteration cycles enabling more rapid AI development

**Methodological Impact:**
The PID-style control framework for optimizer scheduling introduces a new paradigm: treating neural network training as a dynamical system to be controlled rather than a static optimization problem. This perspective opens avenues for applying control theory to deep learning more broadly.

### 3.4 Limitations and Future Directions

**Known Limitations:**
- Compute overhead (~10-20%) for criticality estimation
- Applicability limited to supervised learning with phase transitions
- Scale invariance is approximate; architecture-specific calibration required

**Future Directions:**
- Extension to reinforcement learning and online learning settings
- Integration with neural architecture search (NAS) for criticality-aware architecture design
- Theoretical analysis connecting criticality to information-theoretic generalization bounds

### 3.5 Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Proxy metrics don't correlate with true criticality | Medium | Multiple proxy candidates; ablation studies |
| PID control too slow to modulate dynamics | Low | Adaptive gain scheduling; faster update frequency |
| Results don't transfer across scales | Medium | Staged validation; architecture-specific exponents |
| Compute overhead prohibitive at scale | Low | Sparse estimation; amortized computation |

## 4. Conclusion

This proposal presents Criticality-Aware Optimizer Scheduling (CAOS), a principled framework for accelerating generalization phase transitions in deep learning by maintaining networks near dynamical criticality. By combining computationally tractable proxy metrics with PID-style adaptive control, CAOS addresses a critical gap in optimization for large models: the unpredictability and computational waste associated with phenomena like grokking and double descent.

The proposed research directly addresses the OPT 2024 focus on "scaling up optimization" by providing scale-transferable predictions that could fundamentally change how practitioners approach hyperparameter selection and training budget allocation. Success would yield both immediate practical benefits—reduced training costs and environmental impact—and deeper theoretical understanding of the optimization-generalization interface in deep learning.