# Effort-Aware Preference Learning: Modeling Cognitive Cost in Human Feedback for AI Alignment

## 1. Introduction

### Background

The alignment of artificial intelligence systems with human intentions and values represents one of the most critical challenges in deploying AI safely and ethically across diverse domains. Current state-of-the-art approaches, including Reinforcement Learning from Human Feedback (RLHF) and Learning from Demonstrations (LfD), have demonstrated remarkable success in fine-tuning large language models and training robotic systems. However, these methods rest on fundamentally questionable assumptions about human feedback. Specifically, they typically assume that humans act as rational agents, provide unbiased and consistent feedback, and invest uniform effort across all feedback instances.

These assumptions are systematically violated in practice. Behavioral economics and cognitive science have long established that human decision-making is subject to bounded rationality, cognitive limitations, and varying levels of effort investment. When asked to provide preferences between AI-generated outputs or demonstrate desired behaviors, humans engage in "satisficing" rather than optimizing—providing feedback that is "good enough" rather than optimal, especially when faced with difficult comparisons, high cognitive load, or fatigue. This variability in feedback quality creates a fundamental challenge: alignment algorithms cannot distinguish between carefully considered preferences that reflect true human values and low-effort responses that may be arbitrary or inconsistent.

Recent work has begun to address some aspects of noisy human feedback. Energy-Based Reward Models (EBRM) explicitly model reward distributions to capture uncertainty in preferences, while Active Preference Optimization (APO) seeks to query the most informative samples to improve sample efficiency. However, these approaches do not explicitly model the *cognitive effort* that humans invest in providing feedback—a critical latent variable that fundamentally influences feedback reliability and quality.

### Research Objectives

This research proposes a comprehensive framework for **Effort-Aware Preference Learning (EAPL)** that explicitly models cognitive effort as a first-class component of the human feedback process. Our specific objectives are:

1. **Develop mathematical models** that jointly represent human preferences and the cognitive effort invested in expressing them, treating effort as a latent variable that modulates feedback reliability.

2. **Design effort-conditional reward models** that appropriately weight human feedback based on estimated cognitive cost, as inferred from observable signals such as response time, choice difficulty, and attention patterns.

3. **Create active querying strategies** that optimize the effort-information tradeoff, adaptively selecting queries that balance the value of information gained against the cognitive burden imposed on human annotators.

4. **Implement hierarchical Bayesian models** that can learn both individual-specific effort patterns and task-specific difficulty characteristics, enabling personalized and context-aware feedback interpretation.

5. **Validate the framework** empirically on both RLHF for large language models and preference-based reinforcement learning in robotics tasks.

### Significance

This research addresses a fundamental gap in AI alignment methodology. By explicitly accounting for cognitive effort, we can:

- **Improve alignment quality** by appropriately weighting feedback based on reliability rather than treating all feedback equally
- **Enhance sample efficiency** by focusing human effort on queries where careful consideration matters most
- **Reduce annotator burden** by recognizing when simpler queries suffice and avoiding unnecessarily difficult comparisons
- **Better handle heterogeneity** across users and contexts by learning personalized effort models
- **Provide theoretical grounding** for understanding when and why human feedback may be unreliable

The framework bridges cognitive science, behavioral economics, and machine learning, offering both theoretical insights into human feedback mechanisms and practical improvements to AI alignment systems. This work directly addresses the workshop's goals of better understanding human feedback models and their shortcomings while proposing promising directions for improved AI alignment.

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Effort-Augmented Preference Model

We extend the Bradley-Terry preference model commonly used in RLHF to incorporate cognitive effort. Let $\mathcal{X}$ be the space of items to be compared (e.g., LLM responses, robot trajectories), and let $r^*: \mathcal{X} \rightarrow \mathbb{R}$ represent the true latent reward function reflecting human values. 

For a comparison between items $x_i$ and $x_j$, we model the probability that a human selects $x_i$ as:

$$P(x_i \succ x_j | e_{ij}) = \sigma\left(\beta(e_{ij}) \cdot (r^*(x_i) - r^*(x_j))\right)$$

where $\sigma$ is the sigmoid function, $e_{ij}$ represents the cognitive effort invested in this comparison, and $\beta(e_{ij})$ is an effort-dependent inverse temperature parameter. The key innovation is that $\beta$ increases with effort, such that:

$$\beta(e_{ij}) = \beta_0 + \gamma \cdot e_{ij}$$

where $\beta_0 > 0$ represents baseline rationality and $\gamma > 0$ captures how increased effort improves decision quality. When effort is low ($e_{ij} \approx 0$), preferences become nearly random; when effort is high, preferences more accurately reflect the true reward difference.

#### 2.1.2 Effort Cost Function

We model cognitive effort as incurring a cost to the human annotator:

$$C(e_{ij}) = \alpha \cdot e_{ij} + \lambda \cdot d(x_i, x_j)$$

where $d(x_i, x_j)$ represents the inherent difficulty of comparing $x_i$ and $x_j$ (e.g., when items are very similar or of comparable quality), $\alpha$ represents the marginal cost of effort, and $\lambda$ captures how difficulty amplifies cost. Humans are assumed to choose effort to balance comparison accuracy against this cost.

#### 2.1.3 Effort Inference from Observable Signals

Since effort is latent, we infer it from observable proxies:

$$e_{ij} = f(\tau_{ij}, a_{ij}, m_{ij}; \theta_e)$$

where:
- $\tau_{ij}$ is response time for the comparison
- $a_{ij}$ represents attention patterns (e.g., eye-tracking data, mouse movements, or number of re-reads)
- $m_{ij}$ captures meta-cognitive signals (e.g., self-reported confidence)
- $\theta_e$ are parameters learned from data

We implement $f$ as a neural network trained on auxiliary tasks where ground truth effort can be established (e.g., when correct answers exist).

### 2.2 Effort-Conditional Reward Learning

#### 2.2.1 Weighted Maximum Likelihood Estimation

Given a dataset $\mathcal{D} = \{(x_i^{(k)}, x_j^{(k)}, y^{(k)}, e^{(k)})\}_{k=1}^N$ where $y^{(k)} \in \{0,1\}$ indicates which item was preferred and $e^{(k)}$ is the inferred effort, we learn a reward model $r_\theta$ by maximizing the effort-weighted likelihood:

$$\theta^* = \arg\max_\theta \sum_{k=1}^N w(e^{(k)}) \cdot \log P(y^{(k)} | x_i^{(k)}, x_j^{(k)}, e^{(k)}; \theta)$$

where the weight function $w(e)$ increases with effort:

$$w(e) = \frac{e + \epsilon}{\mathbb{E}[e] + \epsilon}$$

with $\epsilon > 0$ preventing zero weights. This naturally down-weights low-effort feedback.

#### 2.2.2 Hierarchical Bayesian Model

To capture individual differences and task-specific effects, we employ a hierarchical Bayesian framework:

$$\begin{aligned}
\text{Population level:} \quad & \beta_0 \sim \mathcal{N}(\mu_\beta, \sigma_\beta^2), \quad \gamma \sim \text{Gamma}(a_\gamma, b_\gamma) \\
\text{Individual level:} \quad & \beta_0^{(u)} \sim \mathcal{N}(\beta_0, \tau_\beta^2), \quad \gamma^{(u)} \sim \mathcal{N}(\gamma, \tau_\gamma^2) \\
\text{Task level:} \quad & \lambda_{ij} \sim \text{Gamma}(a_\lambda, b_\lambda)
\end{aligned}$$

where $u$ indexes individual annotators. We use variational inference or MCMC for posterior estimation.

### 2.3 Active Query Selection

#### 2.3.1 Information-Effort Tradeoff

For active learning, we select queries that maximize expected information gain per unit of expected cognitive cost:

$$x_i^*, x_j^* = \arg\max_{x_i, x_j} \frac{I(r_\theta; y | x_i, x_j)}{\mathbb{E}[C(e_{ij}) | x_i, x_j]}$$

The information gain $I(r_\theta; y | x_i, x_j)$ quantifies how much the comparison reduces uncertainty about the reward model, computed via:

$$I(r_\theta; y | x_i, x_j) = H(r_\theta) - \mathbb{E}_{y}[H(r_\theta | y, x_i, x_j)]$$

where $H$ denotes entropy. We approximate this using ensemble disagreement or Bayesian active learning by disagreement (BALD).

#### 2.3.2 Adaptive Difficulty Control

When detecting low annotator engagement (via declining response times or increasing response variance), we adaptively simplify queries by:

1. Selecting pairs with larger predicted reward differences (easier comparisons)
2. Reducing the dimensionality of items to compare (e.g., showing shorter text excerpts)
3. Switching to simpler feedback modalities (binary ratings instead of rankings)

### 2.4 Experimental Design

#### 2.4.1 Domain 1: RLHF for Large Language Models

**Task**: Fine-tune a language model (e.g., Llama-2-7B) on summarization and instruction-following tasks.

**Data Collection**:
- Generate response pairs using the base model for 1,000 prompts from the Anthropic HH-RLHF dataset
- Recruit 50 annotators via Prolific, each providing 100 comparisons
- Record response times, mouse tracking data, and self-reported confidence
- Manipulate task difficulty by varying response similarity and prompt complexity

**Experimental Conditions**:
1. **Baseline RLHF**: Standard Bradley-Terry model with uniform weighting
2. **Time-weighted**: Weight by response time only
3. **EAPL (ours)**: Full effort-aware model with hierarchical structure
4. **EAPL + Active**: EAPL with effort-aware query selection

**Evaluation Metrics**:
- **Alignment quality**: Win rate against baseline when evaluated by held-out expert annotators
- **Sample efficiency**: Performance as a function of training dataset size
- **Preference consistency**: Test-retest reliability on repeated comparisons
- **Annotator burden**: Average cognitive load (NASA-TLX questionnaire)

#### 2.4.2 Domain 2: Preference-Based Robot Learning

**Task**: Learn reaching and manipulation policies from human preferences in simulation (using PyBullet/MuJoCo).

**Data Collection**:
- Generate trajectory pairs using behavior cloning on suboptimal demonstrations
- Collect preferences via video interface showing side-by-side trajectory comparisons
- Record dwell time, number of replays, and gaze patterns (eye-tracking subset)
- Include degraded videos to manipulate comparison difficulty

**Experimental Conditions**: Same as Domain 1

**Evaluation Metrics**:
- **Task success rate**: Percentage of successful task completions
- **Policy quality**: Expected return in ground-truth reward environment
- **Sample efficiency**: Success rate vs. number of queries
- **Robustness**: Performance degradation under distribution shift

#### 2.4.3 Ablation Studies

To validate components of our framework:

1. **Effort signals**: Compare performance using different subsets of effort proxies (time only, time + attention, all signals)
2. **Weighting schemes**: Compare different functional forms for $w(e)$
3. **Hierarchical structure**: Evaluate gain from modeling individual differences
4. **Active learning**: Compare different acquisition functions (information gain, effort-adjusted, random)

### 2.5 Implementation Details

**Software Stack**: PyTorch for neural models, Stan/PyMC for Bayesian inference, Hugging Face Transformers for LLMs, Stable-Baselines3 for RL.

**Effort Predictor Architecture**: 3-layer MLP with inputs normalized by z-scoring, trained with MSE loss on synthetic tasks where ground truth effort is known (e.g., arithmetic problems with varying difficulty).

**Computational Resources**: 4x NVIDIA A100 GPUs for LLM fine-tuning, standard CPU resources for robotic simulation.

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Quantitative Improvements**:
- **20-30% improvement** in sample efficiency (achieving target performance with fewer human comparisons) relative to standard RLHF
- **15-25% reduction** in alignment error (measured by agreement with expert preferences on held-out test set)
- **30-40% decrease** in annotator cognitive load while maintaining or improving alignment quality
- **Improved calibration**: Tighter correlation between model confidence and actual preference accuracy

**Qualitative Insights**:
- **Effort patterns**: Characterization of how cognitive effort varies with comparison difficulty, domain expertise, and individual differences
- **Failure modes**: Identification of systematic biases introduced when effort is ignored (e.g., algorithmic preference collapse on nuanced comparisons)
- **Design principles**: Guidelines for optimal query design that balances information value against cognitive cost

**Methodological Contributions**:
- **Theoretical framework**: Formal treatment of effort-preference coupling with provable guarantees on convergence and sample complexity under effort-aware learning
- **Open-source toolkit**: Release of EAPLlib, a Python package for effort-aware preference learning with pre-trained effort estimators
- **Benchmark datasets**: Curated datasets with rich effort annotations for RLHF and robotics domains

### 3.2 Scientific Impact

**Advancing AI Alignment Theory**: This work challenges the assumption of uniform feedback quality that underlies most alignment approaches. By demonstrating that effort-aware modeling significantly improves outcomes, we establish cognitive effort as a critical variable that future alignment research must address. This opens new theoretical questions about optimal feedback elicitation under cognitive constraints and the sample complexity of learning from bounded-rational humans.

**Bridging Disciplines**: The framework synthesizes insights from behavioral economics (bounded rationality), cognitive science (mental effort models), and machine learning (active learning, robust optimization). This interdisciplinary approach provides a template for incorporating human factors into AI systems more broadly.

**Improving Human-AI Collaboration**: Beyond alignment, effort-aware models improve human-AI collaboration by making AI systems more "aware" of human cognitive states. This has implications for adaptive interfaces, intelligent tutoring systems, and collaborative decision support tools.

### 3.3 Practical Impact

**Reducing Annotation Costs**: By achieving better alignment with fewer high-quality annotations, EAPL directly reduces the financial and time costs of RLHF pipelines. For organizations fine-tuning LLMs, this could translate to substantial savings while improving model quality.

**Enhancing User Experience**: Adaptive querying that respects cognitive load makes participation in AI alignment less burdensome, potentially improving annotator retention and engagement. This is particularly important for domains requiring expert feedback (medical AI, legal reasoning) where annotator time is expensive and limited.

**Enabling Personalized AI**: The hierarchical modeling approach naturally supports learning user-specific preferences while accounting for individual differences in feedback effort patterns. This enables more personalized AI assistants that adapt to each user's interaction style.

**Informing Policy and Standards**: As AI alignment becomes increasingly critical for safe deployment, this work provides evidence-based recommendations for best practices in collecting and utilizing human feedback. Regulatory frameworks (e.g., EU AI Act) may benefit from effort-aware standards for training data quality.

### 3.4 Limitations and Future Directions

**Limitations**: 
- Effort inference relies on observable proxies that may not perfectly correlate with true cognitive investment
- Additional instrumentation (response time logging, attention tracking) creates implementation overhead
- The framework assumes annotators have intrinsic preferences; it does not address preference construction or value learning

**Future Directions**:
- **Effort elicitation**: Develop interfaces that more directly measure or incentivize effort revelation
- **Multi-modal feedback**: Extend to settings combining demonstrations, comparisons, and natural language critiques
- **Long-horizon alignment**: Apply effort-aware learning to constitutional AI and recursive reward modeling
- **Theoretical guarantees**: Prove PAC-style bounds for convergence rates under effort-aware learning
- **Neuroimaging validation**: Use fMRI or EEG to validate effort proxies against neural correlates of cognitive load

By explicitly modeling the cognitive effort underlying human feedback, this research provides a more realistic and robust foundation for AI alignment. The expected outcomes promise both immediate practical benefits and long-term theoretical insights that will shape how we build AI systems that truly align with human values.