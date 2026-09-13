# Research Proposal

## Title: Lab-in-the-Loop: Reinforcement Learning with Automated Experimental Feedback for Genomic Foundation Model Alignment

---

## 1. Introduction

### Background

The integration of machine learning with genomics has emerged as a transformative paradigm in drug discovery, offering unprecedented opportunities to decode the complex biological mechanisms underlying human diseases. Despite remarkable advances in genomic foundation models—such as Gene42, JanusDNA, and BioReason—a fundamental limitation persists: these models are predominantly trained and evaluated using static computational datasets that may not accurately reflect true biological outcomes in living systems. This disconnect between computational predictions and biological reality represents a critical bottleneck in translating machine learning advances into practical therapeutic applications.

Recent developments in Reinforcement Learning from Human Feedback (RLHF) have revolutionized the alignment of Large Language Models (LLMs) with human preferences, demonstrating that iterative feedback-driven optimization can dramatically improve model utility. However, the genomics domain presents a unique and underexplored opportunity: the availability of automated wet-lab systems—including robotic laboratories, high-throughput CRISPR screening platforms, and automated cell culture systems—that can provide ground-truth biological feedback rather than subjective human preferences.

The challenge lies in the nature of experimental biological feedback: it is inherently expensive (requiring significant reagent and equipment costs), noisy (subject to biological variability and measurement error), delayed (experimental cycles range from hours to weeks), and sparse (limited throughput compared to computational iterations). These characteristics create a uniquely challenging reinforcement learning setting that existing methods, designed for abundant and rapid feedback, inadequately address.

### Research Objectives

This research proposes a novel framework termed "Reinforcement Learning with Lab Feedback" (RLLF) that efficiently aligns genomic foundation models using sparse, delayed, and noisy experimental signals from automated wet-lab systems. Our specific objectives are:

1. **Develop batch-efficient reward modeling techniques** that construct accurate surrogate models of experimental outcomes from limited wet-lab data while quantifying predictive uncertainty.

2. **Design asynchronous policy optimization algorithms** that effectively handle variable feedback delays characteristic of biological experiments while maintaining training stability.

3. **Create active experimental design strategies** that intelligently balance model improvement against experimental costs, prioritizing experiments that maximize information gain.

4. **Validate the framework** on CRISPR essentiality screen prediction tasks, demonstrating improved prediction of essential genes for drug target identification.

### Significance

This research addresses a fundamental gap in the genomics machine learning literature by establishing a principled methodology for incorporating real-world biological validation into foundation model training. Success in this endeavor would:

- **Accelerate drug target identification** by producing models whose predictions more reliably translate to biological outcomes
- **Reduce experimental waste** by intelligently selecting the most informative experiments
- **Establish a new paradigm** for human-out-of-the-loop biological AI systems that continuously improve through automated experimental feedback
- **Bridge computational and experimental biology** by creating frameworks that treat experiments as integral components of the learning process

---

## 2. Methodology

### 2.1 Overall Framework Architecture

The RLLF framework consists of three interconnected components operating in a continuous loop: (1) a genomic foundation model serving as the policy network, (2) an uncertainty-aware reward model ensemble, and (3) an active experimental design module that interfaces with automated wet-lab systems.

Let $\pi_\theta$ denote our genomic foundation model parameterized by $\theta$, which takes genomic sequences or perturbation specifications $x$ as input and produces predictions $y = \pi_\theta(x)$ relevant to biological outcomes (e.g., gene essentiality scores, expression changes). The objective is to optimize:

$$\theta^* = \arg\max_\theta \mathbb{E}_{x \sim \mathcal{D}} \left[ R_{\text{bio}}(\pi_\theta(x)) - \beta \cdot \text{KL}(\pi_\theta || \pi_{\text{ref}}) \right]$$

where $R_{\text{bio}}$ represents the true biological reward (experimental outcome), $\pi_{\text{ref}}$ is a reference policy (pre-trained foundation model), and $\beta$ controls the deviation from the reference to prevent catastrophic forgetting.

### 2.2 Batch-Efficient Reward Modeling

Given the expense of experimental feedback, we develop surrogate reward models that predict experimental outcomes while accurately quantifying uncertainty.

**Ensemble Architecture**: We train an ensemble of $K$ reward models $\{r_{\phi_k}\}_{k=1}^K$, each predicting experimental outcomes from model predictions and genomic context:

$$\hat{R}_k(x, y) = r_{\phi_k}(x, y; c)$$

where $c$ represents contextual information (cell type, experimental conditions). Each model is implemented as a lightweight transformer head attached to the frozen foundation model embeddings.

**Uncertainty Quantification**: We estimate both epistemic (model) and aleatoric (data) uncertainty:

$$\mu_R(x, y) = \frac{1}{K}\sum_{k=1}^K \hat{R}_k(x, y)$$

$$\sigma^2_{\text{epistemic}}(x, y) = \frac{1}{K}\sum_{k=1}^K (\hat{R}_k(x, y) - \mu_R(x, y))^2$$

$$\sigma^2_{\text{aleatoric}}(x, y) = \frac{1}{K}\sum_{k=1}^K \hat{\sigma}_k^2(x, y)$$

where each reward model also predicts its aleatoric uncertainty $\hat{\sigma}_k^2$.

**Training with Limited Data**: We employ a bootstrapped training procedure where each ensemble member is trained on a different bootstrap sample of available experimental data. To improve data efficiency, we incorporate:

1. **Pre-training on computational proxies**: Initialize reward models using large-scale computational predictions (e.g., DepMap scores, predicted expression changes) before fine-tuning on experimental data.

2. **Multi-task learning**: Train reward models jointly across related experimental readouts (viability, expression, morphology) to leverage shared representations.

The reward model loss combines prediction accuracy with calibration:

$$\mathcal{L}_{\text{reward}} = \mathbb{E}_{(x,y,R) \sim \mathcal{D}_{\text{exp}}} \left[ \frac{(R - \hat{R}(x,y))^2}{2\hat{\sigma}^2} + \frac{1}{2}\log\hat{\sigma}^2 \right] + \lambda \mathcal{L}_{\text{calibration}}$$

### 2.3 Asynchronous Policy Optimization

Biological experiments exhibit variable delays—from hours for cell-based assays to weeks for complex phenotypic screens. We develop an asynchronous variant of Proximal Policy Optimization (PPO) that handles these delays.

**Stratified Experience Buffer**: We maintain separate experience buffers based on validation status:

- $\mathcal{B}_{\text{pending}}$: Experiences awaiting experimental validation
- $\mathcal{B}_{\text{surrogate}}$: Experiences with surrogate reward model predictions
- $\mathcal{B}_{\text{validated}}$: Experiences with ground-truth experimental rewards

**Two-Phase Update Rule**: Policy updates proceed in two phases:

*Phase 1 (Surrogate Updates)*: Between experimental batches, we perform standard PPO updates using surrogate rewards with uncertainty penalties:

$$\mathcal{L}_{\text{surrogate}}(\theta) = \mathbb{E}_{(x,y) \sim \mathcal{B}_{\text{surrogate}}} \left[ \min\left( \rho_t(\theta) \hat{A}_t, \text{clip}(\rho_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]$$

where $\rho_t(\theta) = \frac{\pi_\theta(y|x)}{\pi_{\theta_{\text{old}}}(y|x)}$ and the advantage $\hat{A}_t$ incorporates uncertainty penalties:

$$\hat{A}_t = \mu_R(x_t, y_t) - \alpha \sigma_{\text{epistemic}}(x_t, y_t) - V(x_t)$$

*Phase 2 (Validated Updates)*: When experimental results arrive, we perform importance-weighted updates to correct for the temporal gap:

$$\mathcal{L}_{\text{validated}}(\theta) = \mathbb{E}_{(x,y,R) \sim \mathcal{B}_{\text{validated}}} \left[ w(x,y) \cdot (R - \mu_R(x,y))^2 \right]$$

where $w(x,y) = \min\left(\frac{\pi_\theta(y|x)}{\pi_{\theta_{\text{submit}}}(y|x)}, w_{\max}\right)$ accounts for policy drift since experiment submission.

**Delay-Aware Value Function**: We augment the value function to condition on expected delay:

$$V(x, \tau) = \mathbb{E}\left[ \sum_{t=0}^{\infty} \gamma^t R_t | x_0 = x, \text{delay} = \tau \right]$$

This enables appropriate discounting of rewards based on when feedback is expected.

### 2.4 Active Experimental Design

Given limited experimental budgets, we develop acquisition functions that prioritize experiments maximizing model improvement.

**Information-Theoretic Acquisition**: For each candidate experiment $x$, we compute the expected information gain about model parameters:

$$\alpha_{\text{info}}(x) = \mathbb{E}_{y \sim \pi_\theta(x)} \left[ H(\theta | \mathcal{D}) - H(\theta | \mathcal{D} \cup \{(x, y, R(x,y))\}) \right]$$

In practice, we approximate this using the reward model ensemble uncertainty:

$$\alpha_{\text{info}}(x) \approx \mathbb{E}_{y \sim \pi_\theta(x)} \left[ \sigma^2_{\text{epistemic}}(x, y) \right]$$

**Cost-Aware Selection**: We incorporate experimental costs into a composite acquisition function:

$$\alpha(x) = \frac{\alpha_{\text{info}}(x) + \lambda_{\text{exploit}} \mu_R(x, \pi_\theta(x))}{\text{Cost}(x)^\gamma}$$

where $\lambda_{\text{exploit}}$ balances exploration with exploitation and $\gamma$ controls cost sensitivity.

**Batch Experimental Design**: For batch selection of $B$ experiments, we use a greedy submodular optimization:

$$\mathcal{X}_B = \arg\max_{|\mathcal{X}|=B} \sum_{x \in \mathcal{X}} \alpha(x) - \lambda_{\text{div}} \sum_{x, x' \in \mathcal{X}} k(x, x')$$

where $k(x, x')$ is a similarity kernel encouraging diversity.

### 2.5 Experimental Validation Design

**Dataset**: We will validate RLLF using CRISPR essentiality screen data from the Cancer Dependency Map (DepMap) project. We partition cell lines into training (60%), validation (20%), and test (20%) sets, simulating realistic scenarios where models must generalize to new biological contexts.

**Simulated Lab Environment**: To enable rapid iteration before wet-lab deployment, we develop a simulation environment that:
- Uses held-out DepMap screens as ground truth
- Simulates realistic noise distributions based on replicate variance
- Models variable delays (exponential distribution with mean 72 hours)
- Implements cost structures reflecting reagent and throughput constraints

**Evaluation Metrics**:
1. **Prediction Accuracy**: Pearson correlation and AUROC for essential gene classification
2. **Sample Efficiency**: Model performance as a function of experimental budget
3. **Generalization**: Performance on held-out cell lines and perturbation types
4. **Calibration**: Expected calibration error of uncertainty estimates

**Baselines**: We compare against:
- Standard supervised learning on computational proxies
- RLHF with computational reward models only
- Random experimental selection
- Uncertainty sampling without delay handling

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Quantitative Performance Improvements**: We anticipate 20-30% improvement in essential gene prediction accuracy compared to purely computationally-aligned models, with particularly strong gains in out-of-distribution cell types where computational proxies are least reliable.

2. **Sample Efficiency**: We expect RLLF to achieve equivalent performance to uniform experimental sampling with 40-50% fewer experiments, demonstrating the value of active experimental design.

3. **Methodological Contributions**: Novel algorithms for asynchronous RL with delayed feedback and uncertainty-aware reward modeling specifically designed for biological applications.

4. **Open-Source Framework**: A modular, extensible software package enabling other researchers to implement lab-in-the-loop learning for diverse genomics applications.

### Broader Impact

**Accelerating Drug Discovery**: By producing foundation models whose predictions more reliably translate to biological outcomes, RLLF directly addresses a critical bottleneck in target identification. More accurate essentiality predictions will help prioritize drug targets with higher probability of clinical success.

**Paradigm Shift in Biological AI**: This work establishes a template for continuously learning biological AI systems that improve through automated experimental feedback, moving beyond static train-test paradigms toward dynamic, self-improving systems.

**Resource Efficiency**: Intelligent experimental design will reduce the cost and environmental impact of genomics research by eliminating uninformative experiments.

**Interdisciplinary Bridge**: RLLF creates structured interfaces between computational and experimental biology, fostering collaboration and establishing best practices for integrating ML into experimental workflows.

### Limitations and Future Directions

We acknowledge limitations including the initial reliance on simulated experiments and restriction to CRISPR screens. Future work will extend RLLF to diverse experimental modalities (proteomics, imaging), deploy in real robotic laboratory settings, and develop theoretical guarantees for convergence under delayed feedback conditions.

---

This research represents a significant step toward genomic foundation models that are truly aligned with biological reality, leveraging the unique affordances of automated experimentation to create AI systems that continuously learn from the physical world.