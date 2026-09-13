# Research Proposal: Planning-Aware Occupancy Networks for Autonomous Driving

## 1. Title

**Planning-Aware Occupancy Networks: Bridging Perception and Planning through Cost-Conditioned Future Prediction and Differentiable Planning Gradients**

---

## 2. Introduction

### 2.1 Background

Autonomous driving systems have witnessed remarkable progress through modular architectures that decompose the driving task into perception, prediction, and planning components. Recent advances in 3D occupancy networks have emerged as a powerful scene representation paradigm, offering dense geometric understanding that surpasses traditional object-centric approaches. Methods such as SurroundOcc and Occ3D have demonstrated impressive capabilities in reconstructing 3D semantic occupancy from multi-camera inputs, providing rich environmental context for downstream tasks.

However, a fundamental disconnect persists in current autonomous driving pipelines: 3D occupancy representations are predominantly optimized for perception accuracy metrics (e.g., mean Intersection over Union) rather than downstream planning utility. This misalignment creates representations that excel at scene understanding but fail to capture planning-critical features such as collision risks, trajectory feasibility, and dynamic obstacle interactions. While recent work on joint perception-prediction systems (e.g., UniAD, VAD) has demonstrated the benefits of unified architectures, integrating planning into this framework remains challenging due to task interference and weak gradient signals from planning objectives.

The state-of-the-art VAD-Base achieves 1.05m L2 error at 3-second horizon with 0.22% average collision rate on nuScenes, representing significant progress over earlier methods like UniAD (1.65m L2, 0.31% collision). Nevertheless, these approaches still treat occupancy prediction and planning as loosely coupled components, missing opportunities for representation-level optimization that directly serves planning objectives.

### 2.2 Research Objectives

This research proposes **Planning-Aware Occupancy Networks (PAO-Net)**, a novel framework that jointly trains 3D occupancy networks with a cost-conditioned future prediction module and differentiable planning layer. Our primary objectives are:

1. **Develop a cost-conditioned future occupancy prediction module** that conditions future scene predictions on planning-relevant costs (collision, comfort, progress), guiding the representation toward planning-critical features.

2. **Design a differentiable planning layer** that enables gradient flow from planning objectives back to the shared 3D representation, optimizing the encoder for trajectory-critical features.

3. **Demonstrate improved planning performance** (target: <0.95m L2 error at 3s, representing 10% improvement over VAD-Base) while maintaining perception quality (>20% mIoU).

4. **Validate the causal mechanism** through systematic ablations isolating contributions of cost-conditioning versus differentiable planning gradients.

### 2.3 Significance

This research addresses a critical gap in autonomous driving systems by proposing representation-level optimization for planning rather than post-hoc integration. The significance is threefold:

- **Scientific Contribution:** Establishes a principled framework for bridging perception and planning through cost-conditioned representations, advancing understanding of how planning objectives can shape learned scene representations.

- **Practical Impact:** Improved planning accuracy directly translates to safer autonomous vehicles, with potential to reduce collision rates and improve trajectory quality in real-world deployments.

- **Methodological Innovation:** The proposed differentiable planning layer and cost-conditioning mechanism provide reusable components for future research on end-to-end autonomous driving systems.

---

## 3. Methodology

### 3.1 System Architecture Overview

PAO-Net consists of four main components: (1) a multi-camera encoder, (2) a 3D occupancy decoder, (3) a cost-conditioned future prediction module, and (4) a differentiable planning layer. The architecture enables end-to-end training with gradients flowing from planning objectives through future prediction to the shared 3D representation.

### 3.2 Multi-Camera Encoder and 3D Occupancy Decoder

We adopt SurroundOcc as our backbone architecture. Given multi-camera images $\mathbf{I} = \{I_1, ..., I_N\}$ from $N$ cameras, the encoder extracts multi-scale features:

$$\mathbf{F} = \text{Encoder}(\mathbf{I}) \in \mathbb{R}^{C \times H \times W}$$

The 3D occupancy decoder transforms these 2D features into a 3D voxel representation through view transformation:

$$\mathbf{O}_t = \text{Decoder}(\mathbf{F}) \in \mathbb{R}^{X \times Y \times Z \times K}$$

where $X, Y, Z$ denote voxel grid dimensions and $K$ represents semantic classes. This produces the current-frame occupancy prediction used for perception evaluation.

### 3.3 Cost-Conditioned Future Prediction Module

The core innovation lies in conditioning future occupancy predictions on planning-relevant costs. We define a cost vector $\mathbf{c} = [c_{\text{collision}}, c_{\text{comfort}}, c_{\text{progress}}]^T$ representing planning priorities.

**Cost Embedding:** The cost vector is embedded into a high-dimensional representation:

$$\mathbf{e}_c = \text{MLP}(\mathbf{c}) \in \mathbb{R}^{D}$$

**Feature Modulation via FiLM:** We employ Feature-wise Linear Modulation (FiLM) to condition the future prediction decoder:

$$\gamma, \beta = \text{FiLM}_{\text{gen}}(\mathbf{e}_c)$$
$$\tilde{\mathbf{F}} = \gamma \odot \mathbf{F} + \beta$$

**Temporal Prediction:** The modulated features are processed through a temporal prediction network to generate future occupancy states:

$$\mathbf{O}_{t+\tau} = \text{TemporalDecoder}(\tilde{\mathbf{F}}, \mathbf{O}_t, \tau) \quad \text{for } \tau \in \{1s, 2s, 3s\}$$

The temporal decoder employs a recurrent architecture with 3D convolutional layers:

$$\mathbf{h}_{\tau} = \text{GRU}(\mathbf{h}_{\tau-1}, \text{Conv3D}(\mathbf{O}_{t+\tau-1}))$$
$$\mathbf{O}_{t+\tau} = \text{OutputHead}(\mathbf{h}_{\tau})$$

**Cost-Conditioned Loss:** The future prediction is supervised with cost-weighted losses:

$$\mathcal{L}_{\text{future}} = \sum_{\tau} \left[ w_{\text{col}} \cdot \mathcal{L}_{\text{col}}^{\tau} + w_{\text{com}} \cdot \mathcal{L}_{\text{com}}^{\tau} + w_{\text{prog}} \cdot \mathcal{L}_{\text{prog}}^{\tau} \right]$$

where $\mathcal{L}_{\text{col}}^{\tau}$ emphasizes occupied voxels near the ego trajectory, $\mathcal{L}_{\text{com}}^{\tau}$ penalizes rapid occupancy changes, and $\mathcal{L}_{\text{prog}}^{\tau}$ rewards accurate prediction along the planned path.

### 3.4 Differentiable Planning Layer

To enable gradient flow from planning to representation, we design a differentiable planning layer based on sampling-based optimization.

**Trajectory Sampling:** We sample $M$ candidate trajectories from a learned trajectory prior:

$$\{\boldsymbol{\xi}_1, ..., \boldsymbol{\xi}_M\} \sim p_{\theta}(\boldsymbol{\xi} | \mathbf{O}_{t:t+T})$$

where each trajectory $\boldsymbol{\xi}_i = \{(x_\tau, y_\tau, \theta_\tau)\}_{\tau=1}^{T}$ represents waypoints over the planning horizon.

**Cost Evaluation:** Each trajectory is evaluated against the predicted future occupancy:

$$C(\boldsymbol{\xi}_i) = \sum_{\tau=1}^{T} \left[ \alpha_1 \cdot C_{\text{collision}}(\boldsymbol{\xi}_i^\tau, \mathbf{O}_{t+\tau}) + \alpha_2 \cdot C_{\text{comfort}}(\boldsymbol{\xi}_i) + \alpha_3 \cdot C_{\text{progress}}(\boldsymbol{\xi}_i) \right]$$

The collision cost is computed via differentiable occupancy querying:

$$C_{\text{collision}}(\boldsymbol{\xi}_i^\tau, \mathbf{O}_{t+\tau}) = \sum_{p \in \text{EgoFootprint}(\boldsymbol{\xi}_i^\tau)} \sigma(\mathbf{O}_{t+\tau}[p] - \theta_{\text{occ}})$$

where $\sigma$ is a sigmoid function ensuring differentiability and $\theta_{\text{occ}}$ is an occupancy threshold.

**Soft Trajectory Selection:** The final trajectory is computed as a soft weighted combination:

$$\boldsymbol{\xi}^* = \sum_{i=1}^{M} w_i \cdot \boldsymbol{\xi}_i, \quad w_i = \frac{\exp(-C(\boldsymbol{\xi}_i) / \tau_{\text{temp}})}{\sum_j \exp(-C(\boldsymbol{\xi}_j) / \tau_{\text{temp}})}$$

**Planning Loss:** The planning loss compares against ground-truth trajectories:

$$\mathcal{L}_{\text{plan}} = \sum_{\tau=1}^{T} \|\boldsymbol{\xi}^*_\tau - \boldsymbol{\xi}^{\text{GT}}_\tau\|_2^2$$

### 3.5 Joint Training Objective

The complete training objective combines perception, future prediction, and planning losses:

$$\mathcal{L}_{\text{total}} = \lambda_{\text{perc}} \cdot \mathcal{L}_{\text{perc}} + \lambda_{\text{future}} \cdot \mathcal{L}_{\text{future}} + \lambda_{\text{plan}} \cdot \mathcal{L}_{\text{plan}}$$

where $\lambda_{\text{perc}} \in [0.3, 0.5]$, $\lambda_{\text{future}} \in [0.2, 0.4]$, and $\lambda_{\text{plan}} \in [0.2, 0.4]$ are hyperparameters balancing task contributions.

The perception loss follows standard occupancy prediction:

$$\mathcal{L}_{\text{perc}} = \text{CE}(\mathbf{O}_t, \mathbf{O}_t^{\text{GT}}) + \lambda_{\text{lovasz}} \cdot \text{Lovasz}(\mathbf{O}_t, \mathbf{O}_t^{\text{GT}})$$

### 3.6 Data Collection and Experimental Setup

**Dataset:** We use the nuScenes dataset with Occ3D annotations, comprising 700 training scenes and 150 validation scenes. The dataset provides multi-camera images, 3D occupancy ground truth, and ego-vehicle trajectories.

**Implementation Details:**
- Backbone: SurroundOcc with ResNet-101 encoder
- Voxel resolution: 0.5m × 0.5m × 0.5m
- Perception range: [-50m, 50m] × [-50m, 50m] × [-5m, 3m]
- Planning horizon: 3 seconds with 0.5s intervals
- Trajectory samples: $M = 256$
- Training: 24 epochs, AdamW optimizer, learning rate 2e-4
- Hardware: 8 × NVIDIA A100 GPUs

**Cost Weight Ranges:**
- $w_{\text{collision}} \in [0.3, 0.7]$
- $w_{\text{comfort}} \in [0.1, 0.3]$
- $w_{\text{progress}} \in [0.2, 0.4]$

### 3.7 Evaluation Metrics

**Planning Metrics:**
- L2 Error: Average L2 distance between predicted and ground-truth trajectories at 1s, 2s, 3s horizons
- Collision Rate: Percentage of predicted trajectories intersecting with ground-truth obstacles

**Perception Metrics:**
- mIoU: Mean Intersection over Union for 3D semantic occupancy on Occ3D-nuScenes benchmark

### 3.8 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

**A1: Cost-Conditioning Ablation**
- Baseline: Standard future prediction without cost-conditioning
- Variant: Cost-conditioned future prediction
- Metric: Planning L2 error improvement

**A2: Differentiable Planning Ablation**
- Baseline: Non-differentiable planning (stop gradient)
- Variant: Full differentiable planning
- Metric: Gradient magnitude analysis, planning L2 error

**A3: Joint vs. Sequential Training**
- Baseline: Sequential training (perception → prediction → planning)
- Variant: Joint end-to-end training
- Metric: Task interference analysis, final performance

**A4: Cost Weight Sensitivity**
- Sweep: $w_{\text{collision}} \in \{0.3, 0.5, 0.7\}$
- Metric: Planning L2 error, collision rate trade-offs

### 3.9 Statistical Analysis

Following rigorous experimental design:
- **Runs:** $n = 25$ independent training runs with different random seeds
- **Statistical Test:** Paired t-test with $\alpha = 0.05$ (one-tailed)
- **Effect Size:** Target Cohen's $d \geq 0.5$ (medium effect)
- **Reporting:** Mean difference, 95% confidence intervals, p-values

### 3.10 Falsification Criteria

The hypothesis is falsified if:
1. **Primary Failure:** L2 error $\geq 1.35$m at 3s horizon
2. **Mechanism Failure:** Ablations show cost-conditioning or differentiable planning contribute $<1\%$ improvement
3. **Trade-off Failure:** Perception mIoU drops $>5\%$ from baseline (below 15.56%)

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

Based on our hypothesis and supporting evidence from related work, we anticipate the following outcomes:

**Primary Outcomes:**
- Planning L2 error: <0.95m at 3s horizon (10% improvement over VAD-Base's 1.05m)
- Collision rate: <0.20% average (improvement over VAD-Base's 0.22%)
- Perception mIoU: >20% (maintaining SurroundOcc baseline of 20.59%)

**Ablation Insights:**
- Cost-conditioning expected to contribute 4-6% L2 improvement
- Differentiable planning expected to contribute 3-5% L2 improvement
- Joint training expected to outperform sequential training by 2-4%

### 4.2 Scientific Impact

This research will advance the field in several ways:

1. **Unified Representation Theory:** Establishes theoretical and empirical foundations for planning-aware scene representations, demonstrating that perception representations can be optimized for downstream planning without sacrificing perception quality.

2. **Cost-Conditioning Framework:** Introduces a generalizable mechanism for conditioning neural network predictions on task-specific objectives, applicable beyond autonomous driving to robotics and embodied AI.

3. **Differentiable Planning Integration:** Provides a practical solution for integrating planning gradients into perception training, addressing the long-standing challenge of weak gradient signals in end-to-end systems.

### 4.3 Practical Impact

**Safety Improvements:** Reduced collision rates directly translate to safer autonomous vehicles. A 10% reduction in planning error could prevent accidents in edge cases where current systems fail.

**Computational Efficiency:** By optimizing representations for planning at training time, inference-time planning becomes more efficient, reducing computational requirements for real-time deployment.

**Industry Adoption:** The modular design allows integration with existing autonomous driving stacks, facilitating adoption by industry practitioners.

### 4.4 Broader Impact

This research contributes to the workshop's goals of promoting real-world ML impact for autonomous driving by:

- Addressing the integration challenge between perception and planning components
- Providing interpretable intermediate representations through cost-conditioned predictions
- Establishing benchmarking protocols for planning-aware representations

### 4.5 Limitations and Future Work

**Limitations:**
- Occupancy resolution (0.5m) may limit fine-grained planning in tight spaces
- 3-second temporal horizon may be insufficient for highway scenarios
- Computational cost of joint training may limit real-time adaptation

**Future Directions:**
- Extension to longer temporal horizons and higher resolution
- Integration with LiDAR inputs for improved geometric accuracy
- Application to simulation and closed-loop evaluation
- Transfer learning to diverse driving environments (Waymo, KITTI)

This research represents a significant step toward truly integrated autonomous driving systems, where perception representations are inherently optimized for the ultimate goal of safe and efficient vehicle planning.