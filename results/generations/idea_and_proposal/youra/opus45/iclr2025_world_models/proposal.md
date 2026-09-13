# Research Proposal: Duet Dynamics: Uncertainty-Gated Hybrid SSM-Diffusion World Models for Efficient Video Prediction

## 1. Title

**Duet Dynamics: Uncertainty-Gated Hybrid SSM-Diffusion World Models for Efficient Video Prediction**

---

## 2. Introduction

### 2.1 Background

World models represent a fundamental paradigm in artificial intelligence, enabling intelligent agents to construct internal representations of their environments for prediction, planning, and decision-making. The evolution of world models has progressed from early recurrent neural network (RNN) architectures modeling low-level physical dynamics to contemporary large-scale systems capable of generating complex, high-dimensional environments. Recent advances exemplified by Sora and Genie demonstrate the potential of world models for realistic video generation and interactive simulation, yet significant challenges remain in balancing computational efficiency with prediction quality.

Current approaches to world modeling face a fundamental architectural tradeoff. State Space Models (SSMs), particularly the recently introduced Mamba architecture, offer linear-complexity $O(n)$ inference with selective state mechanisms that enable content-aware reasoning. Mamba has demonstrated 5× faster inference than Transformers while achieving competitive performance across sequence modeling tasks. However, SSMs struggle with highly stochastic dynamics where multiple plausible futures exist, as their deterministic state transitions cannot adequately capture multimodal distributions.

Conversely, diffusion models have emerged as the state-of-the-art approach for high-fidelity visual generation, with Video Diffusion Models achieving unprecedented quality in video prediction and generation tasks. The iterative denoising process inherent to diffusion models naturally captures stochastic dynamics and multimodal distributions. However, this iterative nature imposes substantial computational overhead, with typical inference requiring 20-100 denoising steps, rendering real-time applications challenging.

Existing hybrid approaches, such as StateSpaceDiffuser, have attempted to combine SSM and diffusion architectures by using SSMs for memory and context management while diffusion handles generation. However, these approaches do not exploit the functional separation between deterministic and stochastic dynamics—a principle with strong foundations in neuroscience. Recent work on duet predictive coding has revealed that the brain employs dual pathways for processing expected versus unexpected events, using separate prediction error signals for deviance detection. This neurobiological insight suggests that intelligent systems may benefit from architecturally separating the processing of predictable dynamics from novel or stochastic events.

### 2.2 Research Objectives

This research proposes **Duet Dynamics**, a novel dual-pathway world model architecture that functionally separates deterministic dynamics from stochastic dynamics using learned uncertainty gating. Our primary objectives are:

1. **Develop an uncertainty-gated routing mechanism** that accurately distinguishes between low-uncertainty (deterministic) and high-uncertainty (stochastic) dynamics using ensemble-based epistemic uncertainty estimation.

2. **Design a dual-pathway architecture** where an efficient SSM (Mamba) pathway handles deterministic predictions while a lightweight diffusion pathway processes stochastic dynamics.

3. **Demonstrate superior efficiency-quality tradeoffs** achieving prediction quality within 5% of pure diffusion baselines (measured by Fréchet Video Distance) while attaining 2-3× faster inference.

4. **Validate the functional separation hypothesis** by showing that uncertainty-based routing outperforms memory-based integration approaches across multiple benchmark domains.

### 2.3 Research Significance

This research addresses critical challenges in scaling world models for real-world applications. The significance spans multiple dimensions:

**Theoretical Contribution:** We provide the first application of duet predictive coding principles from neuroscience to hybrid SSM-Diffusion architecture design, establishing a theoretical foundation for functional dynamics separation in world models.

**Methodological Innovation:** The proposed uncertainty-gated routing mechanism represents a novel approach to combining complementary architectures, moving beyond simple ensemble or memory-based integration toward principled functional separation.

**Practical Impact:** Achieving real-time capable world models with high-fidelity predictions enables deployment in robotics, embodied AI, and autonomous systems where both quality and latency are critical constraints. A 2-3× speedup while maintaining quality parity would substantially expand the applicability of world models in time-sensitive domains.

**Broader Applications:** The principles developed in this research extend beyond video prediction to healthcare simulation, scientific modeling, and social science applications where understanding the boundary between deterministic and stochastic dynamics is essential.

---

## 3. Methodology

### 3.1 Architecture Overview

The Duet Dynamics architecture comprises four primary components: (1) an ensemble of SSM heads for uncertainty estimation, (2) a learned gating network for pathway routing, (3) an efficient SSM pathway for deterministic dynamics, and (4) a lightweight diffusion pathway for stochastic dynamics.

**Formal Problem Setting:** Given a sequence of observations $\{o_1, o_2, \ldots, o_t\}$ and actions $\{a_1, a_2, \ldots, a_t\}$, the world model predicts future observations $\{\hat{o}_{t+1}, \hat{o}_{t+2}, \ldots, \hat{o}_{t+H}\}$ over horizon $H$. Let $x_t = (o_t, a_t)$ denote the input state at time $t$.

### 3.2 Uncertainty Estimation via Ensemble SSM Heads

We employ an ensemble of $K$ SSM heads (where $K \in \{3, 5\}$) to estimate epistemic uncertainty through prediction variance. Each SSM head $f_k$ is implemented using the Mamba architecture with selective state space dynamics:

$$h_t^{(k)} = \bar{A}^{(k)} h_{t-1}^{(k)} + \bar{B}^{(k)} x_t$$

$$\hat{y}_t^{(k)} = C^{(k)} h_t^{(k)}$$

where $\bar{A}^{(k)}$ and $\bar{B}^{(k)}$ are discretized state matrices with input-dependent selection, and $h_t^{(k)}$ is the hidden state for ensemble member $k$.

The epistemic uncertainty is computed as the variance across ensemble predictions:

$$\sigma^2(x_t) = \frac{1}{K} \sum_{k=1}^{K} \left\| \hat{y}_t^{(k)} - \bar{y}_t \right\|^2$$

where $\bar{y}_t = \frac{1}{K} \sum_{k=1}^{K} \hat{y}_t^{(k)}$ is the ensemble mean prediction.

### 3.3 Learned Gating Network

The gating network $g_\phi: \mathbb{R}^+ \rightarrow [0, 1]$ maps uncertainty estimates to routing probabilities. We parameterize this as a small MLP with sigmoid output:

$$g_\phi(\sigma^2(x_t)) = \text{sigmoid}\left( W_2 \cdot \text{ReLU}(W_1 \cdot \sigma^2(x_t) + b_1) + b_2 \right)$$

The routing decision is determined by a learnable threshold $\tau$:

$$\text{route}(x_t) = \begin{cases} \text{Diffusion} & \text{if } g_\phi(\sigma^2(x_t)) > \tau \\ \text{SSM} & \text{otherwise} \end{cases}$$

To encourage sparse diffusion activation, we apply entropy regularization to the gating distribution:

$$\mathcal{L}_{\text{gate}} = -\lambda_g \cdot \mathbb{E}\left[ g_\phi \log g_\phi + (1 - g_\phi) \log(1 - g_\phi) \right]$$

where $\lambda_g$ controls the regularization strength. The threshold $\tau$ is initialized at the 70th percentile of training uncertainty values and updated via gradient descent.

### 3.4 Dual Prediction Pathways

**SSM Pathway:** For low-uncertainty states ($g_\phi(\sigma^2(x_t)) \leq \tau$), predictions are generated by the primary Mamba encoder-decoder:

$$\hat{o}_{t+1}^{\text{SSM}} = \text{Decoder}_{\text{SSM}}\left( \text{Encoder}_{\text{SSM}}(x_t) \right)$$

This pathway operates with $O(n)$ complexity, enabling efficient processing of deterministic dynamics.

**Diffusion Pathway:** For high-uncertainty states ($g_\phi(\sigma^2(x_t)) > \tau$), we employ a lightweight Diffusion Transformer (DiT) head with reduced denoising steps ($T_{\text{diff}} \in \{4, 8\}$):

$$\hat{o}_{t+1}^{\text{Diff}} = \text{DiT}_\theta\left( z_T, \text{Encoder}_{\text{SSM}}(x_t), T_{\text{diff}} \right)$$

where $z_T \sim \mathcal{N}(0, I)$ is the initial noise and the SSM encoder provides conditioning context. The diffusion process follows the standard formulation:

$$p_\theta(z_{t-1} | z_t, c) = \mathcal{N}\left( z_{t-1}; \mu_\theta(z_t, t, c), \Sigma_\theta(z_t, t, c) \right)$$

where $c = \text{Encoder}_{\text{SSM}}(x_t)$ is the conditioning signal.

### 3.5 Output Combination

Final predictions are computed via uncertainty-weighted combination:

$$\hat{o}_{t+1} = (1 - g_\phi) \cdot \hat{o}_{t+1}^{\text{SSM}} + g_\phi \cdot \hat{o}_{t+1}^{\text{Diff}}$$

This soft combination allows gradient flow through both pathways during training while enabling hard routing during inference for maximum efficiency.

### 3.6 Training Procedure

Training proceeds in two phases:

**Phase 1 (SSM Pre-training):** Train the ensemble SSM heads and primary SSM encoder-decoder using standard next-frame prediction loss:

$$\mathcal{L}_{\text{SSM}} = \mathbb{E}\left[ \left\| o_{t+1} - \hat{o}_{t+1}^{\text{SSM}} \right\|^2 \right]$$

**Phase 2 (Joint Training):** Freeze SSM weights and train the diffusion pathway and gating network jointly:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{recon}} + \lambda_d \mathcal{L}_{\text{diff}} + \lambda_g \mathcal{L}_{\text{gate}}$$

where $\mathcal{L}_{\text{recon}}$ is the reconstruction loss on final predictions, $\mathcal{L}_{\text{diff}}$ is the diffusion denoising loss, and hyperparameters $\lambda_d, \lambda_g$ balance the objectives.

### 3.7 Experimental Design

**Datasets and Benchmarks:**

1. **DMControl Suite:** 6 continuous control tasks (Walker, Cheetah, Hopper, Quadruped, Humanoid, Finger) with 64×64 visual observations.

2. **Atari 100k:** 26 games following the standard 100k interaction budget, evaluating world model quality through downstream policy performance.

3. **Video Prediction Benchmarks:** RoboNet (robotic manipulation) and Something-Something V2 (human-object interactions) for real-world video prediction.

**Baseline Comparisons:**

| Baseline | Type | Purpose |
|----------|------|---------|
| Pure SSM (Mamba) | SSM-only | Efficiency upper bound, quality lower bound |
| Pure Diffusion (DiT) | Diffusion-only | Quality upper bound, efficiency lower bound |
| StateSpaceDiffuser | Hybrid (memory-based) | Architecture comparison |
| STORM | Transformer WM | SOTA Transformer baseline |
| DIAMOND | Diffusion WM | SOTA Diffusion baseline |

**Evaluation Metrics:**

- **Prediction Quality:** Fréchet Video Distance (FVD), Learned Perceptual Image Patch Similarity (LPIPS), Peak Signal-to-Noise Ratio (PSNR)
- **Computational Efficiency:** FLOPs per frame, inference latency (ms), throughput (frames/second)
- **Mechanism Validation:** Diffusion activation rate, uncertainty calibration (Expected Calibration Error)
- **Downstream Performance:** Human Normalized Score (HNS) on Atari 100k

**Statistical Analysis:**

- Sample size: $n \geq 20$ runs per condition with different random seeds
- Primary test: Paired t-test with Bonferroni correction ($\alpha = 0.05/3 = 0.017$)
- Effect size: Cohen's d with 95% confidence intervals
- Ablation studies: Gating threshold sensitivity ($\tau \in \{50\text{th}, 70\text{th}, 90\text{th}\}$ percentile), ensemble size ($K \in \{2, 3, 5\}$)

**Success Criteria:**

- **Primary (P1):** FVD $\leq 1.05 \times$ Diffusion-only FVD AND Latency $\leq 0.5 \times$ Diffusion-only latency
- **Secondary (P2):** Diffusion activation rate $< 30\%$
- **Secondary (P3):** P1 criteria met on $\geq 2$ of 3 benchmark domains

**Falsification Criteria:**

1. FVD $> 1.2 \times$ Diffusion-only (quality failure)
2. Latency $> 0.8 \times$ Diffusion-only (efficiency failure)
3. Diffusion activation $> 60\%$ (mechanism failure)
4. Underperforms SSM-only on both quality AND efficiency (baseline failure)

### 3.8 Implementation Details

- **Model Capacity:** ~500M total parameters (matched across ablations)
- **SSM Configuration:** Mamba-based encoder-decoder with 24 layers, hidden dimension 1024
- **Diffusion Configuration:** DiT-S/2 with 4-8 denoising steps, classifier-free guidance
- **Training:** AdamW optimizer, learning rate $3 \times 10^{-4}$, batch size 64, 8 A100 GPU-days
- **Inference:** Hard routing with threshold $\tau$, mixed precision (FP16)

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome:** We expect Duet Dynamics to achieve prediction quality within 5% of pure diffusion baselines (FVD ratio $\leq 1.05$) while demonstrating 2-3× faster inference (latency ratio $\leq 0.5$). Based on preliminary analysis of SSM and diffusion characteristics, we anticipate:

- **DMControl:** FVD $< 100$ with inference latency $< 15$ms per frame
- **Atari 100k:** Human Normalized Score $> 1.3$ (competitive with DIAMOND's 1.46)
- **Video Prediction:** LPIPS $< 0.15$ on RoboNet with $> 60$ FPS throughput

**Mechanism Validation:** We expect the uncertainty gating mechanism to route approximately 70% of frames to the efficient SSM pathway, with diffusion activation concentrated on:
- Scene transitions and novel object appearances
- High-entropy action outcomes (e.g., object collisions, stochastic physics)
- Frames with multiple plausible futures

**Ablation Insights:** We anticipate demonstrating that:
- Ensemble size $K=3$ provides sufficient uncertainty estimation with minimal overhead
- Gating threshold at the 70th percentile optimally balances efficiency and quality
- Two-phase training outperforms end-to-end joint training for stability

### 4.2 Theoretical Impact

This research establishes a principled framework for combining complementary neural architectures based on functional dynamics separation. The key theoretical contributions include:

1. **Duet Predictive Coding for AI:** Translating neuroscience insights about dual prediction error pathways into architectural design principles for world models.

2. **Uncertainty-Guided Architecture Selection:** Demonstrating that learned routing based on epistemic uncertainty can effectively allocate computational resources to match task demands.

3. **Efficiency-Quality Pareto Frontier:** Characterizing the tradeoff space between prediction quality and computational efficiency for hybrid world models.

### 4.3 Practical Impact

**Robotics and Embodied AI:** Real-time world models are essential for model-based reinforcement learning in physical systems. A 2-3× speedup enables:
- Closed-loop imagination-based planning at control frequencies ($> 30$ Hz)
- On-device deployment for mobile robots with limited compute
- Longer planning horizons within fixed latency budgets

**Healthcare and Scientific Simulation:** The functional separation principle extends to domains where deterministic physical laws interact with stochastic biological processes:
- Drug interaction modeling with deterministic pharmacokinetics and stochastic patient responses
- Climate simulation with deterministic physics and stochastic weather events

**Foundation World Models:** The architectural principles inform the design of large-scale world models (following Genie and Sora) by providing efficient inference strategies for deployment.

### 4.4 Broader Impact

**Computational Sustainability:** By routing 70% of predictions through efficient SSM pathways, Duet Dynamics reduces the carbon footprint of world model inference compared to pure diffusion approaches.

**Democratization of World Models:** Faster inference enables deployment on consumer hardware, expanding access to world model capabilities beyond well-resourced research labs.

**Safety Considerations:** Improved world models enhance the predictability and interpretability of AI systems, supporting safer deployment in high-stakes applications. The explicit uncertainty estimation provides calibrated confidence signals for downstream decision-making.

### 4.5 Limitations and Future Work

**Known Limitations:**
- Ensemble SSM heads add ~20% parameter overhead
- Two-phase training requires careful hyperparameter tuning
- Performance on extremely long sequences ($> 1000$ frames) remains unvalidated

**Future Directions:**
- Extension to 3D world models and multi-view prediction
- Integration with language conditioning for instruction-following world models
- Application to scientific simulation domains (molecular dynamics, climate modeling)
- Theoretical analysis of uncertainty calibration guarantees

---

**Conclusion:** This research proposal presents Duet Dynamics, a novel dual-pathway world model architecture that addresses the fundamental efficiency-quality tradeoff in world modeling through principled functional separation of deterministic and stochastic dynamics. By combining the linear-complexity efficiency of State Space Models with the generative capacity of diffusion models via learned uncertainty gating, we aim to enable real-time world models suitable for robotics, embodied AI, and scientific simulation applications. The proposed methodology includes rigorous experimental validation across multiple benchmarks with clearly defined success and falsification criteria, ensuring scientific rigor and reproducibility.