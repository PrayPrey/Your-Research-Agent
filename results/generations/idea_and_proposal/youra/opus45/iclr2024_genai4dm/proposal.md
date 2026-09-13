# Research Proposal: Bidirectional Predictive Gradients: Shared Dynamics Encoders for Faster Model-Based Reinforcement Learning Adaptation

## 1. Introduction

### 1.1 Background

Model-based reinforcement learning (MBRL) has emerged as a promising paradigm for sample-efficient decision making, enabling agents to learn internal world models that simulate environment dynamics and support planning without exhaustive real-world interaction. Recent advances in generative models—particularly diffusion models and transformers—have dramatically enhanced the expressiveness and accuracy of learned world models, as demonstrated by systems like DreamerV3, TD-MPC2, and various diffusion-based planners. These methods have achieved remarkable success across continuous control benchmarks, robotic manipulation, and autonomous driving scenarios.

However, a fundamental inefficiency persists in current MBRL architectures: world models and policies are typically trained with separate objectives, leading to what recent literature identifies as "objective mismatch." The world model optimizes for prediction accuracy across the entire state space, while the policy optimizes for reward maximization along specific trajectories. This separation creates representation mismatch—the world model may allocate capacity to regions irrelevant for decision making, while the policy may exploit inaccuracies in task-critical regions. Consequently, when adapting to new tasks or environments, both components must independently converge, resulting in slow adaptation and suboptimal sample efficiency.

Intriguingly, neuroscience research offers a compelling alternative perspective. Studies by Gale et al. (2021) demonstrate that motor cortex (M1) and sensory cortex (S1) share predictive representations during motor planning, with descending predictive feedback creating unified sensorimotor codes. This biological architecture suggests that prediction and action selection need not be separate processes but can emerge from shared representational substrates. Translating this insight to artificial systems motivates a fundamental architectural change: unifying world model and policy learning through shared encoders with bidirectional gradient flow.

### 1.2 Research Objectives

This research proposes **Bidirectional Predictive Gradients (BPG)**, a novel architecture that addresses the objective mismatch problem through three key innovations:

1. **Shared Dynamics Encoder:** A transformer-based encoder produces unified latent representations used by both world model prediction and policy action selection, ensuring representational coherence.

2. **Bidirectional Gradient Flow:** Both world model prediction loss and policy optimization gradients flow through the common encoder, creating aligned optimization signals that jointly shape the latent space.

3. **Gradient Conflict Resolution:** PCGrad-style projection prevents destructive interference between potentially conflicting gradients, enabling stable joint training.

Our primary research objectives are:
- **RO1:** Demonstrate that BPG achieves 3-5× faster online adaptation compared to state-of-the-art MBRL methods (DreamerV3, TD-MPC2) across diverse continuous control tasks.
- **RO2:** Validate that shared latent dynamics reduce policy-world model mismatch by ≥50% as measured by KL divergence.
- **RO3:** Establish that BPG maintains ≥95% of baseline final performance while achieving faster adaptation.
- **RO4:** Characterize the conditions under which shared representations provide maximal benefit versus potential limitations.

### 1.3 Significance

This research addresses a critical challenge at the intersection of generative models and decision making: how to leverage the representational power of modern generative architectures while maintaining sample efficiency for online adaptation. Success would establish shared latent dynamics as a principled approach for deploying MBRL in data-constrained real-world settings, including robotics, autonomous systems, and interactive AI applications where rapid adaptation is essential.

The broader impact extends to understanding how insights from biological intelligence can inform artificial system design, potentially opening new research directions in neurally-inspired reinforcement learning architectures.

---

## 2. Methodology

### 2.1 Architecture Design

#### 2.1.1 Shared Dynamics Encoder

The core of BPG is a transformer-based encoder $E_\theta$ that maps observations to a unified latent space:

$$z_t = E_\theta(o_t, a_{t-1}, z_{t-1})$$

where $o_t$ is the observation at time $t$, $a_{t-1}$ is the previous action, and $z_{t-1}$ is the previous latent state. The encoder consists of 6 transformer layers with 512-dimensional latent representations and 8 attention heads, following architectural choices validated in Decision Transformer.

The latent state $z_t$ serves dual purposes:
1. **World Model Input:** A dynamics decoder $D_\phi$ predicts future states: $\hat{z}_{t+1} = D_\phi(z_t, a_t)$
2. **Policy Input:** A policy head $\pi_\psi$ selects actions: $a_t \sim \pi_\psi(z_t)$

This shared representation ensures that features useful for prediction are immediately available for action selection, and vice versa.

#### 2.1.2 World Model Components

Following DreamerV3's recurrent state-space model (RSSM) design, we decompose the world model into:

**Dynamics Predictor:**
$$h_t = f_\phi(h_{t-1}, z_{t-1}, a_{t-1})$$
$$\hat{z}_t \sim q_\phi(z_t | h_t)$$

**Reward Predictor:**
$$\hat{r}_t = R_\phi(z_t, h_t)$$

**Continuation Predictor:**
$$\hat{c}_t = C_\phi(z_t, h_t)$$

The world model loss combines reconstruction, dynamics, and reward prediction:

$$\mathcal{L}_{wm} = \mathbb{E}\left[\sum_t \left( \|o_t - \hat{o}_t\|^2 + \beta_1 D_{KL}(z_t \| \hat{z}_t) + \beta_2 \|r_t - \hat{r}_t\|^2 \right)\right]$$

#### 2.1.3 Policy Components

The policy uses an actor-critic architecture operating in the shared latent space:

**Actor:**
$$\pi_\psi(a_t | z_t) = \mathcal{N}(\mu_\psi(z_t), \sigma_\psi(z_t))$$

**Critic:**
$$V_\xi(z_t) = \mathbb{E}\left[\sum_{k=0}^{H} \gamma^k r_{t+k}\right]$$

The policy loss follows standard actor-critic objectives:

$$\mathcal{L}_\pi = -\mathbb{E}\left[\sum_t \left( \lambda_t \log \pi_\psi(a_t | z_t) - \alpha H(\pi_\psi(\cdot | z_t)) \right)\right]$$

where $\lambda_t = r_t + \gamma V_\xi(z_{t+1}) - V_\xi(z_t)$ is the advantage estimate and $\alpha$ controls entropy regularization.

### 2.2 Bidirectional Gradient Flow with Conflict Resolution

#### 2.2.1 Joint Optimization Objective

The total loss combines world model and policy objectives:

$$\mathcal{L}_{total} = w_{wm} \mathcal{L}_{wm} + w_\pi \mathcal{L}_\pi$$

Critically, both losses backpropagate through the shared encoder $E_\theta$, creating bidirectional gradient flow:

$$g_{wm} = \nabla_\theta \mathcal{L}_{wm}, \quad g_\pi = \nabla_\theta \mathcal{L}_\pi$$

#### 2.2.2 PCGrad-Style Gradient Projection

When gradients conflict (point in opposing directions), naive summation can cause destructive interference. We employ PCGrad-style projection to resolve conflicts:

**Step 1:** Compute cosine similarity between gradients:
$$\cos(\theta) = \frac{g_{wm} \cdot g_\pi}{\|g_{wm}\| \|g_\pi\|}$$

**Step 2:** If $\cos(\theta) < \tau$ (threshold, default $\tau = 0$), project conflicting gradient:
$$g_{wm}' = g_{wm} - \frac{g_{wm} \cdot g_\pi}{\|g_\pi\|^2} g_\pi$$

**Step 3:** Combine projected gradients:
$$g_{total} = g_{wm}' + g_\pi$$

This ensures that world model gradients do not oppose policy improvement, while preserving components that are orthogonal or aligned.

#### 2.2.3 Adaptive Loss Weighting

Rather than fixed weights, we employ uncertainty-based adaptive weighting inspired by multi-task learning:

$$w_{wm} = \frac{1}{2\sigma_{wm}^2}, \quad w_\pi = \frac{1}{2\sigma_\pi^2}$$

where $\sigma_{wm}$ and $\sigma_\pi$ are learned parameters representing task uncertainty. The total loss becomes:

$$\mathcal{L}_{total} = \frac{1}{2\sigma_{wm}^2}\mathcal{L}_{wm} + \frac{1}{2\sigma_\pi^2}\mathcal{L}_\pi + \log \sigma_{wm} + \log \sigma_\pi$$

### 2.3 Training Algorithm

**Algorithm 1: BPG Training**

```
Input: Environment E, replay buffer B, encoder E_θ, world model D_φ, policy π_ψ
Initialize: θ, φ, ψ, σ_wm, σ_π randomly

For episode = 1 to N:
    o_0 ← E.reset()
    z_0 ← E_θ(o_0)
    
    For t = 0 to T:
        # Action selection
        a_t ~ π_ψ(z_t)
        o_{t+1}, r_t, done ← E.step(a_t)
        B.add(o_t, a_t, r_t, o_{t+1}, done)
        z_{t+1} ← E_θ(o_{t+1}, a_t, z_t)
        
    # Training (every K steps)
    Sample batch {(o, a, r, o')} from B
    
    # Compute losses
    L_wm ← WorldModelLoss(E_θ, D_φ, batch)
    L_π ← PolicyLoss(E_θ, π_ψ, batch)
    
    # Compute gradients
    g_wm ← ∇_θ L_wm
    g_π ← ∇_θ L_π
    
    # Gradient projection (if conflicting)
    If cos(g_wm, g_π) < τ:
        g_wm ← g_wm - (g_wm · g_π / ||g_π||²) g_π
    
    # Adaptive weighting
    g_total ← (1/2σ²_wm) g_wm + (1/2σ²_π) g_π
    
    # Update parameters
    θ ← θ - η · g_total
    φ ← φ - η · ∇_φ L_wm
    ψ ← ψ - η · ∇_ψ L_π
    σ_wm, σ_π ← Update via gradient descent

Return E_θ, D_φ, π_ψ
```

### 2.4 Experimental Design

#### 2.4.1 Benchmark Environments

We evaluate across three diverse benchmark suites totaling 15+ tasks:

**DeepMind Control Suite (DMC):** 5 locomotion tasks
- Walker-Walk, Walker-Run, Cheetah-Run, Quadruped-Walk, Humanoid-Walk

**Meta-World:** 5 manipulation tasks
- Door-Open, Drawer-Close, Button-Press, Reach, Pick-Place

**CARLA:** 2 autonomous driving scenarios
- Lane-Following, Intersection-Navigation

#### 2.4.2 Baselines

1. **DreamerV3:** State-of-the-art MBRL with separate world model and policy training
2. **TD-MPC2:** Model-predictive control with learned dynamics
3. **BPG-NoProjection:** Ablation without gradient projection
4. **BPG-FixedWeights:** Ablation with fixed 1:1 loss weighting
5. **BPG-SmallEncoder:** Ablation with reduced encoder capacity (256-dim)

#### 2.4.3 Evaluation Metrics

**Primary Metric - Adaptation Speed:**
$$\text{Speedup} = \frac{N_{baseline}^{90\%}}{N_{BPG}^{90\%}}$$

where $N^{90\%}$ is interactions to reach 90% of optimal performance.

**Secondary Metrics:**

*Policy-World Mismatch:*
$$\text{Mismatch} = \mathbb{E}_{s,a \sim \pi}\left[D_{KL}(P_{env}(s'|s,a) \| P_{wm}(s'|s,a))\right]$$

*Final Performance:*
$$\text{Performance Ratio} = \frac{R_{BPG}}{R_{baseline}}$$

*Training Stability:*
- Gradient norm variance
- Loss convergence rate
- Policy entropy trajectory

#### 2.4.4 Statistical Analysis

- **Sample Size:** 5 random seeds per task × 12 tasks = 60 runs per method
- **Statistical Test:** Paired t-test (one-tailed), α = 0.05
- **Effect Size:** Target Cohen's d ≥ 0.8
- **Confidence Intervals:** 95% bootstrap intervals for all metrics

#### 2.4.5 Ablation Studies

**A1 - Gradient Projection Impact:**
Compare BPG with and without PCGrad projection to isolate conflict resolution benefits.

**A2 - Adaptive vs. Fixed Weighting:**
Compare uncertainty-based weighting against fixed 1:1 ratio.

**A3 - Encoder Capacity:**
Vary latent dimension {256, 512, 768} to characterize capacity requirements.

**A4 - Projection Threshold:**
Sweep τ ∈ {-0.5, 0.0, 0.5} to identify optimal conflict sensitivity.

### 2.5 Implementation Details

- **Compute:** 8 A100 GPU-hours per task
- **Interaction Budget:** 1M environment steps per task
- **Optimizer:** AdamW with learning rate 3e-4, weight decay 1e-4
- **Batch Size:** 256 sequences of length 50
- **Replay Buffer:** 1M transitions with prioritized sampling
- **Imagination Horizon:** 15 steps for policy optimization

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1 - Adaptation Speed):**
We predict BPG will achieve 90% optimal performance in 100K-170K interactions compared to DreamerV3's ~500K interactions, representing a 3-5× speedup. This prediction is grounded in:
- Elimination of separate convergence requirements
- Coherent gradient signals preventing representation drift
- Immediate feature sharing between prediction and action selection

**Secondary Outcomes:**

*P2 - Mismatch Reduction:*
We expect 50% lower KL divergence between world model predictions and actual transitions under the learned policy, as the shared encoder naturally aligns representations for task-relevant regions.

*P3 - Performance Parity:*
BPG should achieve ≥95% of baseline final performance, as gradient projection prevents destructive interference while shared representations provide complementary learning signals.

### 3.2 Falsification Criteria

The hypothesis will be **rejected** if:
1. Speedup falls below 2× on ≥60% of tasks
2. KL divergence is not significantly reduced
3. Final performance drops below 90% of baseline
4. Training exhibits persistent instability despite gradient projection

### 3.3 Scientific Impact

**Theoretical Contributions:**
- Establishes shared latent dynamics as a principled solution to objective mismatch in MBRL
- Provides empirical validation of neuroscience-inspired architectural choices
- Characterizes conditions where unified representations outperform separate optimization

**Methodological Contributions:**
- Novel gradient projection scheme for joint world model-policy training
- Adaptive uncertainty-based loss weighting for MBRL
- Comprehensive benchmark protocol for adaptation speed evaluation

### 3.4 Practical Impact

**Sample Efficiency:**
3-5× faster adaptation directly translates to reduced real-world interaction requirements, critical for:
- Robotic learning where physical interactions are costly
- Autonomous systems requiring rapid domain adaptation
- Interactive AI applications with limited user feedback

**Computational Efficiency:**
Despite ~10% overhead from gradient projection, total training time decreases due to faster convergence, making BPG practical for resource-constrained deployment.

### 3.5 Broader Implications for Generative Models in Decision Making

This research contributes to the workshop's core theme by demonstrating how architectural innovations in generative world models can fundamentally improve decision making efficiency. Specifically:

1. **Generative Models as Decision Making Agents:** BPG shows that world models and policies need not be separate—unified architectures can serve both functions.

2. **Sample Efficiency through Priors:** Shared representations implicitly encode priors about which features matter for both prediction and action, reducing redundant learning.

3. **Transfer Learning Potential:** Unified latent spaces may transfer more effectively to new domains, as representations are optimized for decision-relevant features rather than pure prediction accuracy.

### 3.6 Limitations and Future Directions

**Current Limitations:**
- Evaluation limited to continuous control; discrete action spaces require architectural modifications
- Shared encoder may limit capacity for extremely complex environments
- Gradient projection adds computational overhead

**Future Directions:**
- Extension to hierarchical representations for long-horizon tasks
- Integration with large pre-trained vision-language models
- Application to real-world robotic systems
- Theoretical analysis of representation alignment dynamics

---

## 4. Conclusion

This proposal presents Bidirectional Predictive Gradients (BPG), a novel architecture addressing the fundamental objective mismatch problem in model-based reinforcement learning. By unifying world model and policy learning through shared dynamics encoders with bidirectional gradient flow and conflict resolution, BPG promises 3-5× faster online adaptation while maintaining competitive final performance. Grounded in neuroscience insights about shared sensorimotor representations, this research bridges generative models and decision making, offering both theoretical advances and practical benefits for deploying RL in data-constrained real-world settings.