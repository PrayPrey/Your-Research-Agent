# Adaptive Diffusion Priors for Inverse Problems with Uncertain Forward Models

## 1. Introduction

### Background

Inverse problems, which involve inferring unknown causes from observed effects, are fundamental to numerous scientific and engineering disciplines. Applications range from medical imaging (CT, MRI reconstruction) to computational photography (deblurring, super-resolution), seismic exploration, and astronomical observation. Mathematically, an inverse problem seeks to recover a signal $x \in \mathbb{R}^n$ from measurements $y \in \mathbb{R}^m$ related through a forward model:

$$y = \mathcal{A}(x; \theta) + \epsilon$$

where $\mathcal{A}(\cdot; \theta)$ is the forward operator parameterized by $\theta$ (representing physical properties like blur kernels, sampling patterns, or sensor characteristics), and $\epsilon$ represents measurement noise.

Recent advances in deep learning, particularly diffusion models, have revolutionized inverse problem solving by providing powerful learned priors over natural signals. Diffusion models learn to denoise data through a sequence of refinement steps, effectively capturing the distribution of complex, high-dimensional data. When applied to inverse problems, these models can be conditioned on measurements to produce high-quality reconstructions that respect both data consistency and natural image statistics.

However, current state-of-the-art diffusion-based solvers operate under a critical assumption: **perfect knowledge of the forward model** $\mathcal{A}(\cdot; \theta)$. This assumption is frequently violated in practice:

- **Medical imaging**: Scanner calibration drifts over time, field inhomogeneities vary across patients, and noise characteristics depend on acquisition parameters
- **Computational photography**: Camera blur kernels are rarely known exactly and vary spatially
- **Scientific instrumentation**: Measurement operators involve unknown physical parameters (e.g., atmospheric turbulence in astronomy, unknown material properties in seismic imaging)

The mismatch between assumed and actual forward models can severely degrade reconstruction quality, introduce artifacts, and undermine the reliability of uncertainty estimates—critical factors for deployment in safety-critical applications.

### Research Objectives

This research proposes a novel framework called **Adaptive Diffusion Priors (ADP)** that addresses model uncertainty in diffusion-based inverse problem solvers. The primary objectives are:

1. **Develop a joint inference framework** that simultaneously estimates forward model parameters and performs posterior sampling for signal reconstruction
2. **Incorporate epistemic uncertainty** about the forward model into the reconstruction process through principled uncertainty propagation
3. **Enable self-supervised refinement** of both model estimates and reconstructions using internal consistency constraints
4. **Validate the approach** on realistic medical imaging scenarios with calibration errors and model misspecification

### Significance

This research addresses a critical gap identified in the workshop's call: developing algorithms for inverse problems where "we only have access to partial information about the system model." The significance includes:

- **Theoretical contribution**: A principled Bayesian framework for joint model-signal inference with diffusion priors that extends current theory beyond known forward models
- **Practical impact**: Enabling deployment of diffusion-based methods in real-world scenarios where perfect calibration is infeasible or where forward models vary over time
- **Trustworthy AI**: Providing calibrated uncertainty estimates that account for both aleatoric (measurement noise) and epistemic (model uncertainty) sources
- **Broader applicability**: The framework is agnostic to the specific inverse problem, applicable across medical imaging, computational photography, and scientific instrumentation

## 2. Methodology

### 2.1 Problem Formulation

We formulate the problem in a Bayesian framework where both the signal $x$ and forward model parameters $\theta$ are treated as random variables. Given measurements $y$, we seek the joint posterior:

$$p(x, \theta | y) \propto p(y | x, \theta) p(x) p(\theta)$$

where:
- $p(y | x, \theta) = \mathcal{N}(y; \mathcal{A}(x; \theta), \Sigma_\epsilon)$ is the likelihood
- $p(x)$ is the signal prior modeled by a pre-trained diffusion model
- $p(\theta)$ is a prior over forward model parameters (e.g., uniform or weakly informative)

The diffusion prior $p(x)$ is implicitly defined through the reverse diffusion process:

$$p(x) = \int p(x_0 | x_T) p(x_T) dx_T$$

where $x_T \sim \mathcal{N}(0, I)$ and the reverse process is parameterized by a learned denoising network $\epsilon_\phi(x_t, t)$.

### 2.2 Amortized Forward Model Estimation

#### 2.2.1 Variational Architecture

We introduce an **amortized inference network** $q_\psi(\theta | y)$ that predicts the distribution over forward model parameters directly from measurements. This network is trained to maximize a variational lower bound (ELBO):

$$\mathcal{L}_{\text{ELBO}} = \mathbb{E}_{q_\psi(\theta|y)} [\log p(y|x, \theta)] - D_{\text{KL}}(q_\psi(\theta|y) || p(\theta))$$

The inference network outputs parameters of a diagonal Gaussian: $q_\psi(\theta | y) = \mathcal{N}(\mu_\psi(y), \text{diag}(\sigma^2_\psi(y)))$.

#### 2.2.2 Training Procedure

The amortized network is trained on synthetic data where ground truth forward model parameters are known:

**Algorithm 1: Training the Amortized Model Estimator**
```
Input: Pre-trained diffusion model p(x), forward operator family A(·;θ)
Output: Trained inference network ψ

For each training iteration:
  1. Sample ground truth: x ~ p(x), θ ~ p(θ)
  2. Generate measurement: y = A(x; θ) + ε, ε ~ N(0, Σ_ε)
  3. Predict parameters: μ_ψ(y), σ²_ψ(y) = InferenceNet(y)
  4. Sample θ̂ ~ N(μ_ψ(y), diag(σ²_ψ(y)))
  5. Compute reconstruction loss using diffusion guidance
  6. Update ψ to minimize: -log p(y|x,θ̂) + KL(q_ψ(θ|y)||p(θ))
```

### 2.3 Uncertainty-Aware Diffusion Guidance

#### 2.3.1 Ensemble-Based Posterior Sampling

To incorporate epistemic uncertainty in $\theta$, we employ an **ensemble Kalman-inspired approach** adapted from EnKG but extended to handle parameter uncertainty. We maintain an ensemble of $K$ particle pairs $\{(x^{(k)}_t, \theta^{(k)})\}_{k=1}^K$ throughout the reverse diffusion process.

At each diffusion timestep $t$, the update combines:
1. **Unconditional diffusion step**: $\tilde{x}^{(k)}_{t-1} = \mu_\phi(x^{(k)}_t, t) + \sigma_t z^{(k)}$, where $z^{(k)} \sim \mathcal{N}(0, I)$
2. **Measurement-guided correction**: Using ensemble Kalman update

$$x^{(k)}_{t-1} = \tilde{x}^{(k)}_{t-1} + C_{x\hat{y}} C^{-1}_{\hat{y}\hat{y}} (y - \mathcal{A}(\tilde{x}^{(k)}_{t-1}; \theta^{(k)}))$$

where the covariances are computed empirically across the ensemble:

$$C_{x\hat{y}} = \frac{1}{K-1} \sum_{k=1}^K (\tilde{x}^{(k)}_{t-1} - \bar{\tilde{x}}_{t-1})(\hat{y}^{(k)} - \bar{\hat{y}})^T$$

$$C_{\hat{y}\hat{y}} = \frac{1}{K-1} \sum_{k=1}^K (\hat{y}^{(k)} - \bar{\hat{y}})(\hat{y}^{(k)} - \bar{\hat{y}})^T + \Sigma_\epsilon$$

with $\hat{y}^{(k)} = \mathcal{A}(\tilde{x}^{(k)}_{t-1}; \theta^{(k)})$.

#### 2.3.2 Adaptive Guidance Strength

We introduce a time-dependent and uncertainty-aware guidance weight:

$$\lambda_t = \lambda_0 \cdot \exp\left(-\frac{\text{Var}[\theta^{(1:K)}]}{\tau}\right) \cdot \left(\frac{t}{T}\right)^\gamma$$

This reduces guidance strength when parameter uncertainty is high and increases it as diffusion progresses toward clean samples.

### 2.4 Self-Supervised Refinement

To improve estimates without ground truth, we leverage two consistency principles:

#### 2.4.1 Multi-Trajectory Consistency

Run $M$ independent diffusion trajectories with the same parameter ensemble to obtain reconstructions $\{x^{(m)}_0\}_{m=1}^M$. Refine parameter estimates by minimizing:

$$\mathcal{L}_{\text{consistency}} = \sum_{m=1}^M ||y - \mathcal{A}(x^{(m)}_0; \theta)||^2_2 + \beta \cdot \text{Var}[x^{(1:M)}_0]$$

The second term penalizes excessive variance across trajectories, regularizing the estimates.

#### 2.4.2 Iterative Refinement

**Algorithm 2: Self-Supervised Adaptive Reconstruction**
```
Input: Measurement y, initial parameter estimate q_ψ(θ|y)
Output: Refined reconstruction x_0 and parameters θ̂

Initialize: Sample ensemble {θ^(k)} ~ q_ψ(θ|y)
For iteration i = 1 to N_refine:
  1. Run M diffusion trajectories with ensemble {θ^(k)}:
     {x^(m)_0} = DiffusionSample(y, {θ^(k)}, M)
  
  2. Compute consensus reconstruction: x̄_0 = (1/M)Σ_m x^(m)_0
  
  3. Refine parameters via gradient descent on:
     {θ^(k)} ← argmin_θ ||y - A(x̄_0; θ)||²_2
  
  4. Update parameter uncertainty based on gradient information:
     Σ_θ ← (H + λI)^(-1), H = Hessian of data-fit
  
  5. Check convergence: if ||θ^(i) - θ^(i-1)|| < ε, break

Return: x̄_0, {θ^(k)}
```

### 2.5 Data Collection and Experimental Design

#### 2.5.1 Datasets

**Medical Imaging:**
- **fastMRI knee dataset**: 10,000 fully-sampled knee MRI scans for training diffusion prior
- **Synthetic test set**: 500 scans with simulated calibration errors (coil sensitivity variations, off-resonance effects)
- **Clinical validation set**: 100 real scans with documented calibration drift

**Computational Photography:**
- **DIV2K high-resolution images**: 800 training images for diffusion prior
- **Test set with unknown blur**: 100 images degraded with spatially-varying unknown kernels

#### 2.5.2 Forward Model Parameterizations

**MRI reconstruction:**
$$\theta = \{\mathbf{c}, \Delta B_0, \sigma_n\}$$
where $\mathbf{c}$ are coil sensitivities, $\Delta B_0$ is field inhomogeneity, $\sigma_n$ is noise level.

**Image deblurring:**
$$\theta = \{k(r; \alpha, \beta), \sigma_n\}$$
where $k$ is a parametric blur kernel (e.g., motion blur with direction $\alpha$ and magnitude $\beta$).

#### 2.5.3 Evaluation Metrics

1. **Reconstruction Quality:**
   - Peak Signal-to-Noise Ratio (PSNR)
   - Structural Similarity Index (SSIM)
   - Learned Perceptual Image Patch Similarity (LPIPS)

2. **Parameter Estimation Accuracy:**
   - Mean Absolute Error (MAE) for estimated vs. true $\theta$
   - Expected Calibration Error (ECE) for uncertainty estimates

3. **Uncertainty Calibration:**
   - Coverage probability: $P(x_{\text{true}} \in \text{CI}_{95\%}(x))$
   - Prediction Interval Coverage Probability (PICP)
   - Continuous Ranked Probability Score (CRPS)

4. **Robustness Metrics:**
   - Performance degradation vs. model mismatch severity
   - Comparison to oracle (known $\theta$) and baseline (fixed wrong $\theta$)

#### 2.5.4 Baselines

- **DPS (Diffusion Posterior Sampling)**: Standard diffusion guidance with fixed assumed $\theta$
- **ΠGDM**: Posterior sampling with perfect model knowledge (oracle)
- **EnKG**: Ensemble Kalman guidance without explicit parameter inference
- **Self-diffusion**: Training-free approach without pre-trained prior
- **Deep image prior with hyperparameter tuning**: Optimizing over both signal and model parameters

#### 2.5.5 Ablation Studies

1. Effect of ensemble size $K$ on reconstruction quality and computational cost
2. Contribution of self-supervised refinement iterations
3. Impact of amortized initialization vs. random parameter initialization
4. Sensitivity to misspecification in parameter prior $p(\theta)$
5. Adaptive vs. fixed guidance strength

### 2.6 Implementation Details

- **Diffusion model**: EDM architecture with 200M parameters, trained for 500k iterations
- **Inference network**: ResNet-34 backbone with attention pooling, outputs 2D (mean/variance) for each parameter
- **Ensemble size**: $K=16$ particles for computational efficiency
- **Refinement iterations**: $N_{\text{refine}} = 5$
- **Optimization**: Adam optimizer with learning rate $10^{-4}$, batch size 32
- **Hardware**: Training on 4 NVIDIA A100 GPUs (estimated 3 days per diffusion prior)

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

#### Quantitative Improvements

Based on preliminary experiments, we anticipate:

1. **Reconstruction Quality Under Model Mismatch:**
   - 3-5 dB PSNR improvement over fixed-model baselines when forward model parameters deviate 20-30% from assumed values
   - SSIM scores approaching oracle performance (within 0.02) even with significant miscalibration
   - Graceful degradation: performance loss scaling logarithmically (rather than linearly) with parameter error magnitude

2. **Parameter Estimation Accuracy:**
   - MAE for noise level estimation within 5% of ground truth
   - Blur kernel parameters recovered to within 10% error for moderate blur magnitudes
   - Coil sensitivity maps estimated with normalized root-mean-square error < 0.15

3. **Uncertainty Calibration:**
   - Coverage probabilities within 0.05 of nominal 95% confidence intervals
   - Expected Calibration Error (ECE) < 0.08, significantly better than point-estimate methods
   - Epistemic uncertainty (over parameters) properly distinguished from aleatoric uncertainty (measurement noise)

#### Qualitative Outcomes

- **Artifact reduction**: Fewer hallucinated structures compared to fixed-model approaches when model is misspecified
- **Clinical validation**: Radiologist preference studies showing 70%+ preference for ADP reconstructions in cases with calibration drift
- **Interpretability**: Visualizable parameter estimates (e.g., blur kernels, coil maps) that provide diagnostic information about measurement system health

### 3.2 Scientific Impact

#### Theoretical Contributions

1. **Bayesian framework extension**: Formal treatment of joint signal-parameter inference with diffusion priors, including convergence analysis for the iterative refinement procedure
2. **Uncertainty propagation theory**: Characterization of how parameter uncertainty affects posterior sampling in diffusion models
3. **Identifiability analysis**: Conditions under which forward model parameters can be uniquely determined from measurements alone

#### Methodological Advances

1. **Amortized inference for inverse problems**: Efficient parameter estimation network applicable beyond diffusion models
2. **Ensemble-based guidance**: Principled way to handle parametric uncertainty in conditional generation
3. **Self-supervised refinement**: Training-free adaptation mechanism for test-time model calibration

### 3.3 Practical Impact

#### Medical Imaging

- **Reduced calibration requirements**: Enable high-quality reconstruction even with imperfect scanner calibration, reducing maintenance costs and downtime
- **Longitudinal consistency**: Automatic adaptation to gradual calibration drift, improving reliability of follow-up scans
- **Emergency scenarios**: Robust performance even when rapid acquisition protocols sacrifice careful calibration

#### Computational Photography

- **Blind deconvolution**: State-of-the-art performance on real-world images with unknown blur
- **Consumer devices**: Robust algorithms that work across diverse camera hardware without per-device tuning
- **Astronomical imaging**: Adaptation to time-varying atmospheric turbulence without ground-truth calibration data

#### Scientific Instrumentation

- **Adaptive measurement systems**: Inverse problem solvers that co-evolve with instruments as physical conditions change
- **Reduced expert dependency**: Less manual calibration expertise required, democratizing access to advanced imaging

### 3.4 Broader Impact and Future Directions

#### Trustworthy AI in Critical Domains

This work advances the deployment of AI in safety-critical applications by:
- Providing interpretable failure modes (visible in parameter uncertainty)
- Quantifying confidence in reconstructions accounting for model uncertainty
- Enabling human-in-the-loop verification through visualizable parameter estimates

#### Sustainability Considerations

- **Computational efficiency**: Ensemble methods add modest computational overhead (2-3× baseline) while enabling significant quality improvements
- **Resource optimization**: Reducing need for frequent hardware recalibration saves energy and extends equipment lifetime
- **Data efficiency**: Amortized networks trained once can generalize across many test scenarios

#### Future Research Directions

1. **Extension to sequential inverse problems**: Video reconstruction with time-varying forward models
2. **Active learning for parameter estimation**: Optimal measurement design when parameters are uncertain
3. **Multi-fidelity modeling**: Combining fast approximate forward models with slow accurate simulations
4. **Federated learning**: Training amortized networks across institutions without sharing sensitive calibration data
5. **Foundation models**: Pre-training on diverse inverse problems to enable rapid adaptation to new domains

#### Open Science Commitment

All code, pre-trained models, and synthetic datasets will be released under open-source licenses. We will provide:
- PyTorch implementation of the ADP framework
- Pre-trained diffusion models for medical imaging and natural images
- Benchmark suite for evaluating robustness to model uncertainty
- Tutorial notebooks for applying the method to new inverse problems

### 3.5 Validation and Dissemination Plan

**Year 1:**
- Develop core ADP framework and validate on synthetic experiments
- Submit to NeurIPS/ICML (ML theory and methods)
- Release initial code and pre-trained models

**Year 2:**
- Clinical validation studies with medical imaging partners
- Extended evaluations on diverse inverse problems
- Submit to IEEE Transactions on Medical Imaging / CVPR (applications)
- Workshop organization at MIDL or similar venue

**Year 3:**
- Large-scale deployment studies
- Comprehensive benchmark release
- Book chapter or survey paper on uncertainty in inverse problems

This research directly addresses the workshop's focus on developing "more effective, reliable, and trustworthy learning-based solutions to inverse problems" by tackling the fundamental challenge of model uncertainty. By enabling diffusion models to jointly infer both signals and forward model parameters, we remove a critical barrier to real-world deployment and open new avenues for collaboration between ML researchers and domain scientists.