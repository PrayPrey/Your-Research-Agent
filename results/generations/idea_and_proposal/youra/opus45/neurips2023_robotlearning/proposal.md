# Research Proposal: Safety-Constrained LoRA for Vision-Language-Action Model Fine-Tuning

## 1. Title

**Hierarchical Safety-Constrained LoRA (HSC-LoRA): Integrating Surrogate Control Barrier Functions into Vision-Language-Action Model Fine-Tuning for Safe Robotic Deployment**

---

## 2. Introduction

### 2.1 Background

The emergence of large-scale pre-trained models has revolutionized machine learning across diverse domains, from natural language processing to computer vision. In robotics, Vision-Language-Action (VLA) models such as OpenVLA and RT-2 represent a paradigm shift, enabling robots to interpret multimodal inputs and generate contextually appropriate actions through unified architectures. These models leverage massive pre-training datasets to acquire generalizable representations that can be adapted to specific robotic tasks through fine-tuning.

However, deploying VLA models in real-world robotic systems presents a fundamental safety challenge. Pre-trained models, while powerful, do not inherently encode safety constraints specific to deployment environments. Traditional approaches to ensuring safe robot behavior rely on runtime safety mechanisms such as Control Barrier Functions (CBFs), which provide formal guarantees by constraining the robot's action space in real-time. While theoretically sound, these runtime filters introduce significant computational overhead—often requiring dedicated hardware accelerators or substantial processing time that conflicts with the real-time requirements of robotic control.

The robotics community currently faces a critical dilemma: practitioners must choose between deploying safe-but-slow systems with runtime safety filters or fast-but-risky systems using standard fine-tuning without safety considerations. This trade-off is particularly acute for edge deployment scenarios where computational resources are limited, such as mobile manipulators, drones, or consumer-grade robotic platforms. Neither option is acceptable for widespread real-world deployment, creating a significant barrier to the democratization of safe robotic systems.

Low-Rank Adaptation (LoRA) has emerged as an efficient fine-tuning paradigm that updates only a small subset of model parameters through low-rank decomposition, enabling adaptation on consumer-grade hardware. Recent work such as OpenVLA-OFT has demonstrated that LoRA fine-tuning can achieve remarkable task performance improvements (from 76.5% to 97.1% success rate on LIBERO benchmarks) while requiring only 1% of the parameters to be updated. However, existing LoRA approaches focus exclusively on task performance, leaving safety considerations unaddressed.

### 2.2 Research Objectives

This research proposes Hierarchical Safety-Constrained LoRA (HSC-LoRA), a novel fine-tuning framework that embeds safety awareness directly into adapter weights during training, thereby eliminating the need for runtime safety computation. Our primary objectives are:

1. **Develop a differentiable surrogate CBF loss** that can be integrated into the LoRA optimization process, constraining gradient updates to parameter regions that preserve safety boundaries.

2. **Design a hierarchical adapter architecture** with dedicated safety and task branches that can capture complex constraint geometry while maintaining task performance.

3. **Validate the approach empirically** on the SafeLIBERO benchmark, demonstrating significant safety improvements with minimal task performance degradation and computational overhead.

4. **Establish design principles** for safety-constrained fine-tuning that can generalize to other VLA architectures and robotic domains.

### 2.3 Research Significance

This research addresses a critical gap at the intersection of large-scale model deployment and safe robotics. The significance of our contribution is threefold:

**Scientific Contribution:** We establish a novel theoretical framework for integrating safety constraints into parameter-efficient fine-tuning, bridging the gap between formal safety methods (CBFs) and modern deep learning adaptation techniques.

**Practical Impact:** By eliminating runtime safety computation, HSC-LoRA enables safe VLA deployment on resource-constrained platforms, democratizing access to safe robotic systems for researchers and practitioners without access to high-end computing infrastructure.

**Community Advancement:** Our work directly addresses key workshop themes including safe real-world deployment of pre-trained models, fine-tuning mechanisms for deploying pre-trained models, and the combination of large models with multimodal training for robotics.

---

## 3. Methodology

### 3.1 Problem Formulation

Consider a pre-trained VLA model $f_\theta: \mathcal{O} \times \mathcal{L} \rightarrow \mathcal{A}$ that maps observations $o \in \mathcal{O}$ and language instructions $l \in \mathcal{L}$ to actions $a \in \mathcal{A}$. The model parameters $\theta$ are decomposed as $\theta = \theta_0 + \Delta\theta$, where $\theta_0$ represents frozen pre-trained weights and $\Delta\theta$ represents trainable adaptation parameters.

In standard LoRA, $\Delta\theta$ is parameterized as low-rank matrices: for a weight matrix $W_0 \in \mathbb{R}^{d \times k}$, the adaptation is $\Delta W = BA$ where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$, and $r \ll \min(d, k)$.

We define safety through a Control Barrier Function $h: \mathcal{X} \rightarrow \mathbb{R}$, where the safe set is $\mathcal{C} = \{x \in \mathcal{X} : h(x) \geq 0\}$. A safety violation occurs when the robot state $x$ exits the safe set, i.e., $h(x) < 0$.

### 3.2 HSC-LoRA Architecture

Our proposed architecture introduces a hierarchical adapter structure with two branches:

**Task Adapter Branch ($\Delta\theta_{\text{task}}$):** Standard LoRA adapters with rank $r_{\text{task}} = 16$ applied to attention layers, optimized for task performance.

**Safety Adapter Branch ($\Delta\theta_{\text{safety}}$):** Dedicated adapters with higher rank $r_{\text{safety}} = 64$ applied to action-critical layers, optimized to encode safety boundaries.

The combined adaptation is:

$$\Delta\theta = \Delta\theta_{\text{task}} + \alpha_s \cdot \Delta\theta_{\text{safety}}$$

where $\alpha_s$ is a learnable scaling factor that balances task and safety contributions.

### 3.3 Surrogate Safety Loss Design

The core innovation is a differentiable surrogate CBF loss that can be backpropagated through the VLA model. For a predicted action $a = f_{\theta_0 + \Delta\theta}(o, l)$ and resulting next state $x' = g(x, a)$ (where $g$ is a differentiable dynamics model or learned predictor), we define:

$$\mathcal{L}_{\text{safety}} = \mathbb{E}_{(o,l,x) \sim \mathcal{D}} \left[ \max(0, -h(x') + \gamma \cdot h(x) + \epsilon) \right]$$

where $\gamma \in (0, 1)$ is the CBF decay rate and $\epsilon > 0$ is a safety margin. This loss penalizes actions that would decrease the safety margin below the required rate.

For manipulation tasks, we instantiate $h(x)$ as a composite safety function:

$$h(x) = \min\left( h_{\text{collision}}(x), h_{\text{boundary}}(x), h_{\text{force}}(x) \right)$$

where each component captures specific safety constraints:
- $h_{\text{collision}}(x) = d_{\min}(x) - d_{\text{safe}}$: minimum distance to obstacles minus safety threshold
- $h_{\text{boundary}}(x) = \min_i(x_i^{\max} - x_i, x_i - x_i^{\min})$: workspace boundary constraints
- $h_{\text{force}}(x) = F_{\max} - \|F(x)\|$: force limit constraints

### 3.4 Training Objective

The complete HSC-LoRA training objective combines task loss with safety constraints:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \lambda \cdot \mathcal{L}_{\text{safety}} + \beta \cdot \mathcal{L}_{\text{reg}}$$

where:
- $\mathcal{L}_{\text{task}}$ is the standard behavior cloning loss (cross-entropy for discretized actions)
- $\lambda \in [0.1, 1.0]$ is the safety constraint weight (key hyperparameter)
- $\mathcal{L}_{\text{reg}} = \|\Delta\theta_{\text{safety}}\|_F^2$ is a regularization term preventing safety adapter overfitting
- $\beta$ is the regularization coefficient

### 3.5 Adversarial Safety Augmentation

To improve robustness, we augment training data with adversarial safety scenarios. For each training batch, a proportion $\rho \in [0.1, 0.5]$ of samples are replaced with adversarially perturbed versions:

$$o_{\text{adv}} = o + \delta^*, \quad \delta^* = \arg\max_{\|\delta\| \leq \epsilon_{\text{adv}}} \mathcal{L}_{\text{safety}}(f_\theta(o + \delta, l))$$

This is approximated using projected gradient descent (PGD) with 5 steps.

### 3.6 Algorithm

The complete HSC-LoRA training procedure is:

**Algorithm 1: HSC-LoRA Training**
```
Input: Pre-trained VLA model f_θ₀, training dataset D, safety function h(x)
Output: Trained adapters Δθ_task, Δθ_safety

1. Initialize Δθ_task ~ N(0, σ²) with rank r_task = 16
2. Initialize Δθ_safety ~ N(0, σ²) with rank r_safety = 64
3. Initialize scaling factor α_s = 1.0

4. For epoch = 1 to E do:
5.   For batch (O, L, X, A) in D do:
6.     // Adversarial augmentation
7.     O_aug = AdversarialPerturbation(O, ρ, ε_adv)
8.     
9.     // Forward pass with combined adapters
10.    Δθ = Δθ_task + α_s · Δθ_safety
11.    A_pred = f_{θ₀+Δθ}(O_aug, L)
12.    
13.    // Compute losses
14.    L_task = CrossEntropy(A_pred, A)
15.    X' = DynamicsPredictor(X, A_pred)
16.    L_safety = mean(max(0, -h(X') + γ·h(X) + ε))
17.    L_reg = ||Δθ_safety||²_F
18.    L_total = L_task + λ·L_safety + β·L_reg
19.    
20.    // Backward pass and update
21.    Compute gradients ∇L_total w.r.t. Δθ_task, Δθ_safety, α_s
22.    Update parameters using AdamW optimizer
23.  End For
24. End For

25. Return Δθ_task, Δθ_safety
```

### 3.7 Experimental Design

**Model and Benchmark:** We use OpenVLA-7B (openvla/openvla-7b checkpoint) as the backbone VLA model and evaluate on the SafeLIBERO benchmark, which extends LIBERO manipulation tasks with explicit safety constraints including collision avoidance, workspace boundaries, and force limits.

**Baselines:**
1. **Standard LoRA:** OpenVLA fine-tuned with standard LoRA (r=16) without safety constraints
2. **VLSA:** Vision-Language Safety Alignment with runtime safety filtering
3. **SafeVLA:** VLA with post-hoc safety layer (if available)

**Independent Variables:**
- CBF constraint weight: $\lambda \in \{0.1, 0.3, 0.5, 0.7, 1.0\}$
- Safety adapter rank: $r_{\text{safety}} \in \{16, 32, 64\}$
- Adversarial augmentation ratio: $\rho \in \{0.1, 0.25, 0.5\}$

**Dependent Variables:**
- Safety violation rate: percentage of episodes with at least one constraint violation
- Task success rate: percentage of episodes achieving task goal
- Inference latency: milliseconds per action prediction

**Experimental Protocol:**
- 25 independent runs per condition (different random seeds)
- 100 evaluation episodes per run across 10 SafeLIBERO tasks
- Statistical significance: paired t-test with $\alpha = 0.05$
- Effect size: Cohen's d with target $d \geq 0.8$

**Ablation Studies:**
1. **Safety loss ablation:** Compare $\lambda = 0$ vs. $\lambda > 0$ to isolate CBF contribution
2. **Adapter rank ablation:** Compare $r_{\text{safety}} \in \{16, 32, 64\}$ to determine capacity requirements
3. **Augmentation ablation:** Compare $\rho = 0$ vs. $\rho > 0$ to isolate adversarial training contribution
4. **Transfer test:** Evaluate on held-out scenarios not seen during training

**Evaluation Metrics:**
- Primary: Safety violation rate reduction (target: >30%)
- Secondary: Task success rate preservation (target: within 5% of baseline)
- Tertiary: Inference latency overhead (target: <10%)

### 3.8 Implementation Details

- **Hardware:** Single NVIDIA A100 (40GB) or 2× RTX 4090 (24GB each)
- **Training:** 50 epochs, batch size 32, learning rate 1e-4 with cosine decay
- **Optimizer:** AdamW with weight decay 0.01
- **Safety margin:** $\epsilon = 0.1$, CBF decay $\gamma = 0.9$
- **Adversarial perturbation:** $\epsilon_{\text{adv}} = 0.01$ (normalized observation space)

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

Based on our hypothesis and preliminary analysis, we anticipate the following outcomes:

**Primary Outcome (Safety Improvement):** HSC-LoRA with optimal hyperparameters ($\lambda \in [0.3, 0.7]$, $r_{\text{safety}} = 64$) will achieve >30% reduction in safety violation rate compared to standard LoRA fine-tuning. We expect the optimal configuration to reduce violations from approximately 25% (baseline) to below 17%.

**Secondary Outcome (Task Preservation):** Task success rate will remain within 5% of the standard LoRA baseline. Given OpenVLA-OFT's reported 97.1% success rate, we target maintaining >92% success rate with safety constraints.

**Tertiary Outcome (Computational Efficiency):** Inference latency overhead will be <10% compared to standard LoRA, as safety computation is embedded in adapter weights rather than requiring runtime filtering. This contrasts with runtime CBF methods that typically add 50-200% overhead.

**Ablation Insights:** We expect to demonstrate that:
- The surrogate CBF loss (not just adversarial augmentation) is the primary driver of safety improvement
- Higher safety adapter rank ($r = 64$) is necessary for complex constraint geometry
- Adversarial augmentation provides additional robustness but is not sufficient alone

### 4.2 Potential Challenges and Mitigations

**Challenge 1: Safety-Task Trade-off Severity**
If the safety-task trade-off proves more severe than anticipated (>10% task degradation), we will explore:
- Curriculum learning: gradually increasing $\lambda$ during training
- Task-specific $\lambda$ calibration
- Pareto-optimal hyperparameter selection

**Challenge 2: Surrogate Loss Gradient Quality**
If surrogate CBF gradients prove uninformative, we will:
- Implement gradient smoothing techniques
- Explore alternative differentiable safety formulations
- Consider learned safety critics as gradient sources

**Challenge 3: Distribution Shift at Deployment**
If safety does not transfer to novel scenarios, we will:
- Increase adversarial augmentation diversity
- Implement online adaptation mechanisms
- Develop uncertainty-aware safety margins

### 4.3 Broader Impact

**Democratization of Safe Robotics:** By enabling safe VLA fine-tuning on consumer-grade hardware without runtime safety filters, HSC-LoRA lowers the barrier to entry for safe robot deployment. Research labs and practitioners without access to high-end computing infrastructure can deploy safety-aware robotic systems.

**Advancing Pre-training Paradigms:** This work establishes principles for integrating domain-specific constraints (safety) into general-purpose fine-tuning methods (LoRA), potentially inspiring similar approaches for other constraints such as energy efficiency, human comfort, or task-specific preferences.

**Real-World Deployment Pathway:** HSC-LoRA provides a practical pathway from pre-trained VLA models to safe real-world deployment, addressing a critical gap that currently limits the adoption of large-scale models in robotics.

**Limitations and Responsible Deployment:** We emphasize that HSC-LoRA provides empirical safety improvements, not formal guarantees. For safety-critical applications requiring provable guarantees, runtime verification remains necessary. Our approach is best suited for applications where empirical safety improvement is valuable but formal certification is not required.

### 4.4 Future Directions

This research opens several promising directions:
1. **Theoretical analysis:** Formal characterization of the safety-preserving parameter subspace
2. **Multi-robot extension:** Scaling HSC-LoRA to multi-agent coordination with collective safety constraints
3. **Online adaptation:** Combining HSC-LoRA with online learning for continuous safety improvement
4. **Cross-embodiment transfer:** Investigating whether safety-constrained adapters transfer across robot platforms

In conclusion, HSC-LoRA represents a significant step toward practical, safe deployment of large-scale VLA models in robotics, directly addressing the workshop's focus on fine-tuning mechanisms and safe real-world deployment of pre-trained models.