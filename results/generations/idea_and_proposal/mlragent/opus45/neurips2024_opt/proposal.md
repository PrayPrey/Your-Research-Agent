# Research Proposal: Scale-Adaptive Learning Rates via Loss Landscape Curvature Transfer

## 1. Introduction

### Background

The advent of large language models (LLMs) has fundamentally transformed the machine learning landscape, with models scaling from millions to hundreds of billions of parameters. Training these models requires astronomical computational resources—GPT-3's training alone consumed an estimated 3,640 petaflop-days of compute, costing millions of dollars in electricity and hardware utilization. Central to training efficiency is the selection of hyperparameters, among which the learning rate stands as the most critical yet challenging to optimize.

Current practice for learning rate selection follows one of two problematic approaches: either conducting expensive grid searches at full scale, which can multiply training costs by an order of magnitude, or applying unreliable heuristics when transferring configurations from smaller proxy models. The latter approach frequently leads to suboptimal performance or training instabilities, as learning rate sensitivities do not transfer trivially across model scales. Empirical observations from Kaplan et al. (2020) and subsequent work on scaling laws have established that model performance follows predictable power-law relationships with size, data, and compute. However, the analogous scaling behavior of optimal hyperparameters—particularly learning rates—remains poorly understood and largely unexploited.

Recent advances provide promising foundations for addressing this challenge. Kalra et al. (2026) introduced critical sharpness as a scalable measure of loss landscape curvature, demonstrating that curvature dynamics exhibit consistent patterns across model sizes up to 7 billion parameters. Fan et al. (2025) established weight-decay scaling rules that enable zero-shot transfer across model widths by analyzing singular value distributions. Luo et al. (2025) proposed multi-power laws for loss curve prediction across learning rate schedules. These developments suggest that the geometric properties of loss landscapes—particularly curvature statistics—may encode transferable information about optimal optimization configurations.

### Research Objectives

This research aims to develop a principled framework for predicting optimal learning rates for large-scale models based on curvature measurements from computationally tractable small-scale experiments. Our specific objectives are:

1. **Characterize the scaling relationships** between model size, loss landscape curvature statistics, and empirically optimal learning rates across a systematic sequence of model scales.

2. **Derive a curvature-based scaling function** that maps optimal learning rates from small proxy models to large target models with quantifiable uncertainty.

3. **Develop efficient curvature profiling protocols** that minimize computational overhead while maintaining predictive accuracy for hyperparameter transfer.

4. **Validate the transfer methodology** on realistic LLM training scenarios, demonstrating practical compute savings without sacrificing final model performance.

### Significance

Success in this endeavor would yield transformative benefits for the machine learning community and beyond. From a practical standpoint, reducing hyperparameter tuning costs by 100x or more would democratize access to large-scale model training, enabling smaller research groups and organizations to participate in frontier AI development. The environmental implications are equally significant: if learning rate optimization alone requires 10-50 training runs at scale, eliminating this overhead could prevent thousands of tons of carbon emissions annually across the industry. From a theoretical perspective, this work would bridge classical optimization theory—where step sizes are intimately connected to curvature—with modern empirical scaling law research, potentially revealing fundamental principles governing optimization at scale.

## 2. Methodology

### 2.1 Overall Framework

Our methodology consists of three interconnected phases: (1) curvature profiling across model scales, (2) scaling law derivation for learning rate transfer, and (3) validation and deployment protocols. We focus on decoder-only transformer architectures, the dominant paradigm for modern LLMs, though our framework generalizes to other architectures.

### 2.2 Curvature Profiling Protocol

#### Model Family Construction

We construct a systematic sequence of $K$ models with parameter counts $\{N_1, N_2, \ldots, N_K\}$ spanning approximately three orders of magnitude (e.g., 10M to 10B parameters). Models share architectural hyperparameters in normalized form:

$$N_k = 12 \cdot d_k^2 \cdot L_k$$

where $d_k$ is the model dimension and $L_k$ is the number of layers for model $k$. We maintain consistent aspect ratios $d_k / L_k$ across the sequence to isolate size effects from architectural variations.

#### Curvature Statistics Estimation

For each model $k$, we measure the following curvature statistics at initialization and at checkpoints during early training (first 1-5% of tokens):

**Top Hessian Eigenvalue ($\lambda_{\max}^{(k)}$)**: Estimated via power iteration on the Hessian-vector product:

$$\lambda_{\max} \approx \frac{v^T H v}{v^T v}, \quad Hv = \lim_{\epsilon \to 0} \frac{\nabla L(\theta + \epsilon v) - \nabla L(\theta)}{\epsilon}$$

where $v$ is iteratively refined over 50-100 iterations.

**Hessian Trace ($\text{Tr}(H^{(k)})$)**: Estimated via the Hutchinson stochastic trace estimator:

$$\text{Tr}(H) \approx \frac{1}{M} \sum_{m=1}^{M} z_m^T H z_m$$

where $z_m \sim \mathcal{N}(0, I)$ are random probe vectors and $M \approx 100$ provides sufficient accuracy.

**Critical Sharpness ($S_c^{(k)}$)**: Following Kalra et al. (2026), we compute:

$$S_c = \frac{\|\nabla L\|^2}{\lambda_{\max}}$$

which captures the effective sharpness along the optimization trajectory.

**Effective Hessian Rank ($r_{\text{eff}}^{(k)}$)**: Approximated as:

$$r_{\text{eff}} = \frac{(\text{Tr}(H))^2}{\text{Tr}(H^2)} \approx \frac{(\text{Tr}(H))^2}{\sum_{i} \lambda_i^2}$$

estimated via additional stochastic trace computations.

#### Optimal Learning Rate Determination

For each model $k$, we conduct learning rate sweeps across a logarithmically-spaced grid:

$$\eta \in \{\eta_{\min} \cdot 2^{j/4} : j = 0, 1, \ldots, J\}$$

where $J$ is chosen to span approximately two orders of magnitude. The optimal learning rate $\eta_k^*$ is defined as:

$$\eta_k^* = \arg\min_{\eta} L_k(\eta; T_{\text{eval}})$$

where $L_k(\eta; T_{\text{eval}})$ is the validation loss after training for $T_{\text{eval}}$ tokens with learning rate $\eta$.

### 2.3 Scaling Law Derivation

#### Power-Law Ansatz

We hypothesize that optimal learning rates follow a curvature-corrected power law:

$$\eta^*(N) = \alpha \cdot N^{-\beta} \cdot g(\mathbf{c}(N))$$

where $\alpha, \beta$ are base scaling parameters, $N$ is parameter count, and $g(\mathbf{c}(N))$ is a curvature correction function depending on the curvature statistics vector $\mathbf{c} = [\lambda_{\max}, \text{Tr}(H), S_c, r_{\text{eff}}]$.

#### Correction Function Parameterization

We parameterize $g$ as a multiplicative correction:

$$g(\mathbf{c}) = \prod_{i} \left(\frac{c_i}{c_i^{\text{ref}}}\right)^{\gamma_i}$$

where $c_i^{\text{ref}}$ are reference curvature values (e.g., at the smallest model) and $\gamma_i$ are learned exponents capturing the sensitivity of optimal learning rate to each curvature statistic.

#### Parameter Fitting

Given measurements $\{(N_k, \mathbf{c}_k, \eta_k^*)\}_{k=1}^{K}$, we fit parameters $\{\alpha, \beta, \gamma_1, \ldots, \gamma_4\}$ via nonlinear least squares:

$$\min_{\alpha, \beta, \boldsymbol{\gamma}} \sum_{k=1}^{K} \left(\log \eta_k^* - \log \hat{\eta}(N_k, \mathbf{c}_k; \alpha, \beta, \boldsymbol{\gamma})\right)^2$$

We employ bootstrap resampling to quantify parameter uncertainty and derive prediction intervals.

### 2.4 Transfer Protocol

Given a target model with $N_{\text{target}}$ parameters:

1. **Initialize** the target model and compute curvature profile $\mathbf{c}_{\text{target}}$ using $M=100$ Hutchinson samples (computational cost: ~5 forward-backward passes).

2. **Predict** optimal learning rate:
$$\hat{\eta}_{\text{target}}^* = \alpha \cdot N_{\text{target}}^{-\beta} \cdot g(\mathbf{c}_{\text{target}})$$

3. **Quantify uncertainty** via the fitted prediction interval, enabling risk-aware decisions.

4. **Optional refinement**: Conduct a narrow local search within the 95% prediction interval if compute budget permits.

### 2.5 Experimental Design

#### Datasets and Models

- **Training corpus**: A subset of RedPajama or C4 dataset, ensuring consistent data distribution across experiments
- **Model sizes**: 10M, 50M, 125M, 350M, 1.3B, 2.7B, 6.7B parameters (fitting); 13B, 30B parameters (validation)
- **Architecture**: GPT-style decoder-only transformers with rotary position embeddings

#### Baselines

1. **Constant learning rate transfer**: Apply small-model optimal $\eta$ directly
2. **Linear scaling rule**: $\eta \propto \sqrt{N}$ heuristic
3. **$\mu$P transfer**: Maximal update parameterization (Yang et al.)
4. **Full grid search**: Gold standard (but computationally prohibitive at scale)

#### Evaluation Metrics

- **Prediction accuracy**: $|\log(\hat{\eta}^*/\eta^*)|$, targeting $<0.1$ (within 10% of optimal)
- **Final loss gap**: $L(\hat{\eta}^*) - L(\eta^*)$ after full training
- **Compute efficiency**: Total FLOPs for hyperparameter selection vs. grid search
- **Transfer stability**: Variance of predictions across random seeds and initialization

#### Ablation Studies

1. Impact of curvature measurement timing (initialization vs. early training)
2. Number of proxy model sizes required
3. Sensitivity to architectural variations (depth/width ratio changes)
4. Generalization across optimization algorithms (AdamW, Lion, Sophia)

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Primary Deliverables**:
1. A validated curvature-based scaling law relating optimal learning rates to model size and loss landscape geometry
2. An efficient transfer protocol achieving learning rate predictions within 10% of grid-search optimal for models 10-100x larger than training proxies
3. Open-source implementation integrated with popular deep learning frameworks (PyTorch, JAX)

**Quantitative Targets**:
- Reduce hyperparameter tuning compute by 50-100x compared to full-scale grid search
- Achieve final validation loss within 1% of oracle-tuned baselines
- Curvature profiling overhead under 1% of total training compute

### Scientific Impact

This work bridges two historically separate research communities: classical optimization theory and empirical scaling law research. By demonstrating that curvature statistics encode transferable optimization information, we provide a mechanistic explanation for hyperparameter scaling behavior, moving beyond purely empirical fitting. The framework also opens avenues for investigating other hyperparameters (batch size, weight decay, warmup schedules) through similar curvature-based lenses.

### Practical Impact

The immediate practical benefit is democratizing large-scale model training by dramatically reducing the barrier to entry. Organizations with limited compute budgets can leverage small-scale experiments to configure billion-parameter training runs with confidence. For well-resourced organizations, the methodology accelerates experimentation cycles, enabling faster iteration on model architectures and training procedures.

### Environmental Impact

At industry scale, eliminating redundant hyperparameter searches could prevent tens of thousands of GPU-hours annually, translating to significant reductions in carbon emissions. If adopted broadly, this methodology contributes meaningfully to sustainable AI development practices—a growing concern as model scales continue to increase exponentially.

### Limitations and Future Directions

We acknowledge potential limitations: the power-law ansatz may not capture all scaling regimes, and transferability may degrade for architecturally novel models. Future work will extend the framework to encompass additional hyperparameters, non-transformer architectures, and continual learning scenarios where curvature evolves during deployment. The interplay between data quality and curvature-based transfer, highlighted by recent DeepSeek LLM research, also warrants deeper investigation.