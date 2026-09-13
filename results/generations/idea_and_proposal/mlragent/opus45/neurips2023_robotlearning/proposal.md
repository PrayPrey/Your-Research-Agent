# Research Proposal: Embodiment-Aware Residual Adapters for Hardware-Efficient Fine-Tuning of Vision-Language Models in Robotics

## 1. Introduction

### Background

The emergence of large pre-trained vision-language models (VLMs) has catalyzed remarkable progress across diverse machine learning applications, from image captioning to visual reasoning. In robotics, these models offer unprecedented potential for scene understanding, task planning, and generalization to novel environments. Models such as CLIP, Flamingo, and their successors have demonstrated impressive zero-shot capabilities that could revolutionize how robots perceive and interact with their environments.

However, a fundamental tension exists between the computational demands of these massive models and the practical constraints of robotic systems. While VLMs are typically trained on clusters of high-end GPUs, real-world robots must operate with limited onboard computing resources—often constrained to single consumer-grade GPUs with 8-16GB of memory. Furthermore, the distribution of pre-training data rarely aligns with the specific embodiment characteristics, sensor configurations, and operational environments of individual robotic platforms. This creates an imperative for fine-tuning, yet traditional approaches that update all model parameters are computationally prohibitive for most robotic applications.

Recent work has begun addressing these challenges. LoRA-based approaches have enabled fine-tuning of Vision-Language-Action (VLA) models on consumer hardware, while compact models like SmolVLA have demonstrated that smaller architectures can achieve competitive performance. However, existing parameter-efficient fine-tuning methods remain agnostic to the unique requirements of robotics: they do not account for robot proprioception, action histories, or the safety-critical nature of physical deployment.

### Research Objectives

This research proposes **Embodiment-Aware Residual Adapters (EARA)**, a novel fine-tuning framework specifically designed for adapting large VLMs to robotic applications under severe computational constraints. Our primary objectives are:

1. To develop action-conditioned adapter modules that leverage robot proprioceptive state and action history for embodiment-specific feature modulation
2. To create an automated progressive layer selection mechanism that identifies optimal adaptation points while minimizing trainable parameters to less than 2% of total model size
3. To integrate safety-constrained optimization with uncertainty quantification for reliable out-of-distribution detection during deployment
4. To validate the framework across diverse robotic manipulation and navigation benchmarks, demonstrating practical deployability on resource-constrained hardware

### Significance

This research addresses a critical barrier to real-world deployment of foundation models in robotics. By enabling efficient adaptation with 10x reduction in fine-tuning compute while maintaining 90%+ task performance, EARA will democratize access to powerful vision-language capabilities for robotic applications. The embodiment-aware design philosophy represents a paradigm shift from generic parameter-efficient fine-tuning toward robotics-specific adaptation, potentially establishing new standards for how the field approaches model deployment. Furthermore, the integrated safety mechanisms directly address concerns about deploying large models in physical systems where failures carry real-world consequences.

## 2. Methodology

### 2.1 Overview

EARA consists of three interconnected components: (1) Action-Conditioned Adapter Modules that inject embodiment-specific information into frozen VLM representations, (2) a Progressive Layer Selection algorithm that automatically identifies critical adaptation points, and (3) a Safety-Constrained Optimization framework that ensures reliable uncertainty estimation. Figure 1 illustrates the overall architecture.

### 2.2 Action-Conditioned Adapter Modules

Unlike conventional adapters that process only visual or textual features, EARA modules explicitly incorporate robot state information. For a frozen VLM layer $l$ with hidden representation $\mathbf{h}_l \in \mathbb{R}^d$, we define the adapted representation as:

$$\mathbf{h}'_l = \mathbf{h}_l + \alpha_l \cdot \mathcal{A}_l(\mathbf{h}_l, \mathbf{s}, \mathbf{a}_{1:t})$$

where $\mathbf{s} \in \mathbb{R}^{d_s}$ denotes the current proprioceptive state (joint positions, velocities, end-effector pose), $\mathbf{a}_{1:t}$ represents the action history, and $\alpha_l$ is a learnable scaling factor.

The adapter module $\mathcal{A}_l$ follows a bottleneck architecture with embodiment conditioning:

$$\mathcal{A}_l(\mathbf{h}_l, \mathbf{s}, \mathbf{a}_{1:t}) = \mathbf{W}_{up}^l \cdot \sigma\left(\mathbf{W}_{down}^l \mathbf{h}_l + \mathbf{W}_{emb}^l \mathbf{e}\right)$$

where $\mathbf{W}_{down}^l \in \mathbb{R}^{r \times d}$ projects to a low-rank space of dimension $r \ll d$, $\mathbf{W}_{up}^l \in \mathbb{R}^{d \times r}$ projects back, and $\sigma$ is a non-linear activation (GELU). The embodiment embedding $\mathbf{e}$ is computed as:

$$\mathbf{e} = \text{MLP}_s(\mathbf{s}) + \text{TemporalAttn}(\mathbf{a}_{1:t})$$

The temporal attention mechanism processes action history through a lightweight transformer encoder with $K=2$ layers and 4 attention heads, enabling the adapter to capture action-observation dependencies critical for robotic control.

### 2.3 Progressive Layer Selection

Not all VLM layers require equal adaptation for robotic tasks. We develop an automated selection mechanism based on task-specific gradient analysis during a short calibration phase.

**Calibration Phase**: Given a small calibration dataset $\mathcal{D}_{cal}$ of task-relevant examples, we compute the gradient magnitude at each layer with respect to a task-specific loss $\mathcal{L}_{task}$:

$$g_l = \mathbb{E}_{(\mathbf{x}, y) \sim \mathcal{D}_{cal}} \left[ \left\| \frac{\partial \mathcal{L}_{task}(\mathbf{x}, y)}{\partial \mathbf{h}_l} \right\|_2 \right]$$

**Importance Scoring**: We compute normalized importance scores:

$$\pi_l = \frac{g_l \cdot \text{depth}(l)^\beta}{\sum_{l'} g_{l'} \cdot \text{depth}(l')^\beta}$$

where $\text{depth}(l)$ is the relative position of layer $l$ in the network and $\beta$ is a hyperparameter controlling preference for deeper layers (we find $\beta=0.5$ works well empirically).

**Selection**: We select the top-$k$ layers where $k$ is determined by a parameter budget constraint:

$$\mathcal{L}_{select} = \{l : \pi_l \geq \tau\} \quad \text{s.t.} \quad \sum_{l \in \mathcal{L}_{select}} |\theta_l| \leq B$$

where $B$ is set to 2% of total model parameters. This typically results in 4-8 adapter modules for a 1B parameter VLM.

### 2.4 Safety-Constrained Optimization

For safe deployment, EARA integrates uncertainty quantification through a Bayesian treatment of adapter parameters.

**Variational Adapters**: Instead of point estimates, adapter weights follow distributions:

$$\mathbf{W}_{down}^l \sim \mathcal{N}(\boldsymbol{\mu}_{down}^l, \text{diag}(\boldsymbol{\sigma}_{down}^l))$$

We optimize the variational lower bound:

$$\mathcal{L}_{ELBO} = \mathbb{E}_{q(\theta)}[\log p(\mathcal{D}|\theta)] - \lambda_{KL} \cdot D_{KL}(q(\theta) \| p(\theta))$$

where $p(\theta)$ is a zero-mean Gaussian prior encouraging adapters to remain close to identity (minimal deviation from frozen model).

**Out-of-Distribution Detection**: At inference, we perform $M$ stochastic forward passes and compute predictive entropy:

$$H(\mathbf{y}|\mathbf{x}) = -\sum_c \bar{p}_c \log \bar{p}_c, \quad \bar{p}_c = \frac{1}{M}\sum_{m=1}^M p_c^{(m)}$$

Inputs exceeding entropy threshold $\tau_H$ (calibrated on validation data) trigger safety fallback behaviors.

**Constraint-Aware Training**: We incorporate explicit safety constraints via Lagrangian relaxation:

$$\mathcal{L}_{total} = \mathcal{L}_{task} + \mathcal{L}_{ELBO} + \sum_i \lambda_i \max(0, c_i(\theta))$$

where $c_i$ represents constraint violations (e.g., maximum predicted force, proximity to obstacles).

### 2.5 Data Collection and Experimental Design

**Datasets**: We evaluate EARA on three established benchmarks:

1. **RLBench** (simulation): 18 manipulation tasks with varying complexity, providing 100 demonstrations per task
2. **CALVIN** (simulation): Long-horizon manipulation with language conditioning, 24 hours of play data
3. **Real Robot Experiments**: Franka Panda manipulation with 50 demonstrations for 5 tasks (pick-place, stacking, insertion, pouring, folding)

**Base Models**: We apply EARA to three VLM backbones of varying scale:
- CLIP ViT-B/16 (86M parameters)
- OpenCLIP ViT-L/14 (428M parameters)  
- PaLI-style VLM (1B parameters)

**Baselines**:
1. Full fine-tuning (upper bound)
2. Frozen VLM + MLP head
3. LoRA (rank 4, 8, 16)
4. Standard residual adapters (without embodiment conditioning)
5. Prompt tuning

**Evaluation Metrics**:
- **Task Success Rate**: Primary metric for manipulation/navigation tasks
- **Computational Efficiency**: Training FLOPs, wall-clock time, peak GPU memory
- **Parameter Efficiency**: Percentage of trainable parameters
- **Generalization**: Performance on held-out task variations and novel objects
- **Safety Metrics**: OOD detection accuracy (AUROC), calibration error (ECE)

**Ablation Studies**:
1. Impact of action conditioning vs. standard adapters
2. Progressive layer selection vs. uniform placement
3. Variational vs. deterministic adapter weights
4. Bottleneck dimension $r \in \{4, 8, 16, 32, 64\}$
5. Temporal attention depth for action history

**Hardware Configurations**:
- Training: Single NVIDIA RTX 3090 (24GB) to validate accessibility claims
- Deployment: NVIDIA Jetson AGX Orin to demonstrate real robot feasibility

### 2.6 Implementation Details

Training uses AdamW optimizer with learning rate $10^{-4}$, cosine annealing schedule, and batch size 32. The calibration phase for layer selection requires only 500 forward-backward passes. Adapter bottleneck dimension defaults to $r=16$. Action history length is $t=10$ timesteps. We use mixed-precision training (FP16) throughout. Total training time targets under 4 hours on a single GPU.

## 3. Expected Outcomes & Impact

### Expected Results

We anticipate the following outcomes:

1. **Computational Efficiency**: 10x reduction in training FLOPs compared to full fine-tuning, with peak memory usage under 16GB enabling consumer GPU deployment
2. **Task Performance**: 90-95% of full fine-tuning performance across RLBench and CALVIN benchmarks with only 1.5-2% trainable parameters
3. **Embodiment Adaptation**: 15-20% improvement over standard adapters on tasks requiring tight action-observation coupling (e.g., insertion, pouring)
4. **Safety**: AUROC >0.90 for OOD detection, enabling reliable safety fallbacks
5. **Generalization**: Improved zero-shot transfer to novel objects/environments compared to baselines, attributed to preserved pre-training knowledge

### Broader Impact

**Democratizing Robot Learning**: By enabling effective VLM adaptation on accessible hardware, EARA lowers barriers for research groups and organizations without access to high-end computing infrastructure. This aligns with the growing emphasis on sustainable and accessible AI.

**Safety-First Deployment**: The integrated uncertainty quantification provides a template for responsible deployment of foundation models in physical systems. As VLMs become more prevalent in robotics, principled uncertainty handling becomes essential.

**Bridging Communities**: This work explicitly connects advances in parameter-efficient fine-tuning (primarily from NLP) with the unique requirements of robotics, fostering cross-disciplinary collaboration.

**Limitations and Future Work**: Current limitations include the requirement for proprioceptive state access (not available in all robotic systems) and computational overhead of multiple stochastic passes for uncertainty estimation. Future work will explore single-pass uncertainty methods and extension to multi-robot adaptation with shared adapters.

### Conclusion

EARA represents a principled approach to adapting powerful vision-language models for robotic applications under realistic computational constraints. By explicitly incorporating embodiment information, automatically selecting adaptation points, and ensuring safe deployment through uncertainty quantification, this framework addresses key barriers to real-world foundation model deployment in robotics. We believe this research will contribute meaningfully to the ongoing dialogue at the intersection of large-scale pre-training and practical robot learning.