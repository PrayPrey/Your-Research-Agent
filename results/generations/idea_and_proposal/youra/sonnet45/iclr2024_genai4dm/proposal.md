# Research Proposal: Narrative Coherence as Intrinsic Motivation for Exploration in Sparse-Reward Sequential Decision Making

## 1. Title

**Leveraging Large Language Model Priors for Semantically-Guided Exploration: A Narrative Coherence Approach to Sample-Efficient Reinforcement Learning in Long-Horizon Sparse-Reward Environments**

## 2. Introduction

### 2.1 Background

Reinforcement learning (RL) has achieved remarkable success in domains with dense reward signals and well-defined state spaces, from game playing to robotic manipulation. However, real-world sequential decision-making tasks often present fundamentally different challenges: sparse rewards that provide feedback only upon task completion, long causal chains requiring dozens or hundreds of coordinated actions, and semantically-rich environments where success depends on understanding object relationships and causal dependencies rather than low-level sensorimotor patterns.

Traditional exploration strategies in RL fall into two broad categories. Random exploration methods (ε-greedy, entropy bonuses) scale poorly to high-dimensional spaces and fail to discover structured behaviors. Curiosity-driven approaches like Random Network Distillation (RND) and Intrinsic Curiosity Module (ICM) provide more directed exploration by rewarding agents for encountering novel states or state transitions. While effective in many domains, these methods suffer from a critical limitation: they prioritize syntactic novelty over semantic meaningfulness. An agent using RND might repeatedly explore visually distinct but causally irrelevant states (e.g., different wall textures in a dungeon) while missing crucial narrative progressions (e.g., obtaining a key before attempting to unlock a door).

Concurrently, the field of generative AI has witnessed transformative advances with large language models (LLMs) demonstrating sophisticated understanding of causal relationships, temporal dependencies, and narrative coherence across diverse domains. These models, pretrained on vast corpora of human knowledge, encode rich priors about how events typically unfold, which entities interact meaningfully, and what constitutes a coherent sequence of actions. Despite this potential, the integration of LLM priors into exploration strategies remains largely unexplored, representing a significant gap at the intersection of generative models and decision-making.

From a cognitive science perspective, Loewenstein's Information Gap Theory (1994) posits that curiosity arises from the perception of a gap between what one knows and what one wants to know, with particular emphasis on narrative incompleteness as a driver of information-seeking behavior. This theoretical framework suggests that exploration guided by narrative coherence—the degree to which a sequence of events forms a causally complete and predictable story—might align more closely with human-like exploration strategies and prove more effective in semantically-rich environments.

### 2.2 Research Objectives

This research proposes **Narrative Coherence Intrinsic Motivation (NCIM)**, a novel exploration framework that augments traditional curiosity-driven RL with LLM-evaluated narrative coherence scores. Our primary objectives are:

1. **Develop a computational framework** for converting RL state trajectories into natural language representations and evaluating their narrative coherence using frozen pretrained LLMs.

2. **Design and validate dual-metric coherence scoring** combining causal completeness (measuring unresolved entity references and dangling causal threads) and prediction violation (measuring semantic surprisal in event sequences).

3. **Empirically demonstrate** that narrative coherence-guided exploration improves sample efficiency and task success rates in long-horizon sparse-reward environments compared to state-of-the-art curiosity-driven baselines.

4. **Establish theoretical foundations** connecting Information Gap Theory from cognitive science to computational exploration strategies in RL.

5. **Investigate generalization properties** of narrative coherence priors across different semantically-rich environments and task structures.

### 2.3 Research Questions

**RQ1:** Can LLM-based narrative coherence scores provide exploration signals that are both distinct from and complementary to state-novelty metrics?

**RQ2:** Does augmenting exploration bonuses with narrative coherence improve sample efficiency and success rates in long-horizon sparse-reward tasks requiring causal reasoning?

**RQ3:** What is the optimal balance between semantic coherence and state novelty for exploration in different task structures?

**RQ4:** Do narrative coherence priors transfer effectively across semantically-rich environments with different surface characteristics but similar causal structures?

### 2.4 Significance

This research addresses critical challenges in both the RL and generative AI communities:

**For Reinforcement Learning:** Current exploration methods struggle with tasks requiring long causal chains and semantic understanding. NCIM offers a principled approach to incorporating high-level semantic priors into exploration, potentially enabling RL agents to tackle previously intractable long-horizon tasks without extensive reward engineering.

**For Generative AI Integration:** While LLMs have been explored for high-level planning and reward specification, their potential for continuous exploration guidance remains underutilized. This work establishes a new role for generative models in the RL pipeline: evaluation-based exploration bonus generation.

**For Sample Efficiency:** By directing exploration toward semantically meaningful state sequences, NCIM has the potential to dramatically reduce the number of environment interactions required to solve sparse-reward tasks, making RL more practical for data-constrained real-world applications.

**For Transfer Learning:** Narrative coherence represents a domain-general principle that may transfer more effectively than task-specific exploration heuristics, potentially enabling better zero-shot and few-shot adaptation to new environments.

The expected impact includes 20-30% improvement in task success rates and 40-50% increase in unique causal sequence discovery in semantically-rich sparse-reward environments, with broader implications for human-AI interaction, educational game design, and interactive narrative systems.

## 3. Methodology

### 3.1 Overall Framework Architecture

The NCIM framework consists of four primary components operating in a closed loop with the RL training process:

**Component 1: State-to-Narrative Conversion Module**  
**Component 2: LLM-Based Coherence Evaluation Module**  
**Component 3: Intrinsic Reward Computation Module**  
**Component 4: Policy Optimization Module**

### 3.2 Detailed Algorithmic Design

#### 3.2.1 State-to-Narrative Conversion

For each trajectory segment of length $W$ (window size), we convert the sequence of states $\{s_t, s_{t+1}, ..., s_{t+W}\}$ into natural language descriptions $\{d_t, d_{t+1}, ..., d_{t+W}\}$.

**For text-based environments** (NetHack, TextWorld): Direct extraction using template-based entity recognition:

$$d_t = \text{Template}(\text{EntityExtract}(s_t))$$

where EntityExtract identifies objects, agents, locations, and actions, and Template converts them to natural language following the pattern: "The agent [action] [object] in [location]. Visible entities: [entity_list]. Status: [state_variables]."

**For vision-language environments** (Crafter, ALFWorld): Utilize pretrained vision-language models (e.g., CLIP-based captioning) to generate state descriptions:

$$d_t = \text{VLM}_{\text{caption}}(o_t)$$

where $o_t$ is the visual observation at time $t$.

#### 3.2.2 Narrative Coherence Scoring

We define narrative coherence through two complementary metrics:

**Metric 1: Causal Completeness Score ($C_{\text{causal}}$)**

This metric identifies unresolved entity references and dangling causal threads using few-shot prompted LLM analysis:

$$C_{\text{causal}}(D_W) = 1 - \frac{\text{count}(\text{dangling\_refs}(D_W))}{\text{count}(\text{total\_entities}(D_W))}$$

where $D_W = \{d_t, ..., d_{t+W}\}$ is the narrative segment, and dangling_refs are entities introduced but never resolved (e.g., "picked up key" without subsequent "unlocked door").

The LLM prompt structure:
```
Given this sequence of events:
[narrative segment]

Identify entities that are introduced but never used or resolved.
Format: {"dangling_entities": [...], "total_entities": [...]}
```

**Metric 2: Prediction Violation Score ($C_{\text{predict}}$)**

This metric measures semantic surprisal by comparing LLM predictions with actual next events:

$$C_{\text{predict}}(d_t, d_{t+1}) = 1 - \text{cosine}(\text{embed}(p_t), \text{embed}(d_{t+1}))$$

where $p_t$ is the LLM-predicted next event given context $\{d_{t-k}, ..., d_t\}$, and embed() uses the LLM's final hidden state as semantic embedding.

The prediction prompt:
```
Given these events:
[context window]

What is the most likely next event? Provide a brief description.
```

**Combined Coherence Score:**

$$r_{\text{narrative}} = w_1 \cdot C_{\text{causal}} + w_2 \cdot C_{\text{predict}}$$

where $w_1, w_2$ are learned weights (initialized at 0.5 each) subject to $w_1 + w_2 = 1$.

#### 3.2.3 Intrinsic Reward Computation

The total intrinsic reward combines narrative coherence with traditional state-novelty exploration:

$$r_{\text{intrinsic}}(s_t) = \alpha \cdot r_{\text{RND}}(s_t) + (1-\alpha) \cdot r_{\text{narrative}}(s_t)$$

where:
- $r_{\text{RND}}(s_t) = ||\hat{f}(s_t) - f(s_t)||^2$ is the Random Network Distillation prediction error
- $\alpha \in [0, 1]$ is the balance parameter (explored in range [0.6, 0.8])
- $r_{\text{narrative}}$ is computed every $W$ steps and distributed uniformly across the window

The final reward for policy optimization:

$$r_{\text{total}}(s_t, a_t) = r_{\text{env}}(s_t, a_t) + \beta \cdot r_{\text{intrinsic}}(s_t)$$

where $\beta$ is the intrinsic reward scaling factor (typically 0.1-1.0).

#### 3.2.4 Policy Optimization

We employ Proximal Policy Optimization (PPO) as the base algorithm with the following objective:

$$L^{\text{CLIP}}(\theta) = \mathbb{E}_t[\min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t)]$$

where $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$ and $\hat{A}_t$ is the advantage estimate computed using Generalized Advantage Estimation (GAE) with the total reward $r_{\text{total}}$.

### 3.3 Experimental Design

#### 3.3.1 Environments

We evaluate NCIM across four semantically-rich environments with varying characteristics:

**Environment 1: NetHack Learning Environment**
- **Task:** Navigate dungeon, collect amulet, return to surface
- **Characteristics:** Extremely sparse rewards, 100+ step episodes, complex causal dependencies (e.g., key-door, potion-monster interactions)
- **State space:** Text-based symbolic representation
- **Success metric:** Amulet retrieval rate

**Environment 2: Crafter**
- **Task:** Survival and achievement completion (collect resources, craft tools, defeat enemies)
- **Characteristics:** Multiple sparse achievement rewards, 50-200 step causal chains
- **State space:** 2D pixel observations (64×64×3)
- **Success metric:** Achievement completion rate, survival time

**Environment 3: TextWorld**
- **Task:** Interactive fiction quest completion
- **Characteristics:** Pure text-based, explicit causal dependencies in quest structure
- **State space:** Natural language descriptions
- **Success metric:** Quest completion rate

**Environment 4: ALFWorld**
- **Task:** Household manipulation tasks (e.g., "put heated apple in fridge")
- **Characteristics:** Vision-language grounding, 10-50 step tasks
- **State space:** Visual observations + text instructions
- **Success metric:** Task success rate

#### 3.3.2 Baseline Methods

**Baseline 1: Random Network Distillation (RND)**
- Pure state-novelty exploration
- Represents current state-of-the-art for exploration in sparse-reward settings

**Baseline 2: Intrinsic Curiosity Module (ICM)**
- Forward dynamics prediction error as curiosity signal
- Alternative curiosity-driven approach

**Baseline 3: PPO with ε-greedy**
- Standard random exploration baseline

**Baseline 4: NCIM-ablations**
- NCIM-causal: Only $C_{\text{causal}}$ component ($w_2=0$)
- NCIM-predict: Only $C_{\text{predict}}$ component ($w_1=0$)
- NCIM-random: Random coherence scores (control for computational overhead)

#### 3.3.3 Experimental Protocol

**Design:** Between-subjects factorial design with repeated measures
- **Factors:** Method (6 levels) × Environment (4 levels) × $\alpha$ (4 levels: 0.6, 0.7, 0.8, 0.9)
- **Replications:** 5 random seeds per condition
- **Total runs:** 6 × 4 × 4 × 5 = 480 training runs

**Training procedure:**
1. Initialize policy network (2-layer MLP, 256 hidden units) and RND networks
2. Load frozen LLM (Llama-3-8B-Instruct) for coherence evaluation
3. Train for 10M environment steps (NetHack: extend to 20M if needed)
4. Evaluate every 500K steps using 100 episodes with deterministic policy
5. Log: success rate, sample efficiency (steps to first success), unique causal sequences discovered, coherence scores, computational overhead

**Hyperparameters (PPO standard):**
- Learning rate: 3e-4 with linear decay
- Batch size: 2048 steps
- Epochs per update: 4
- GAE λ: 0.95
- Discount γ: 0.99
- Clip parameter ε: 0.2
- Intrinsic reward scale β: 0.5
- Narrative window W: 50 steps
- LLM evaluation frequency: Every W steps

#### 3.3.4 Evaluation Metrics

**Primary Metrics:**

1. **Task Success Rate:** Proportion of evaluation episodes achieving the goal
   $$\text{Success Rate} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\text{goal achieved in episode } i]$$

2. **Sample Efficiency:** Number of environment steps to first successful episode
   $$\text{Steps to Success} = \min\{t : \text{episode ending at } t \text{ succeeds}\}$$

**Secondary Metrics:**

3. **Causal Sequence Discovery:** Number of unique meaningful causal chains discovered
   - Operationalized as unique (entity, action, consequence) tuples extracted from successful trajectories

4. **Exploration Coverage:** State space coverage measured by:
   $$\text{Coverage} = |\{s : s \text{ visited during training}\}|$$

5. **Coherence-Value Correlation:** Pearson correlation between narrative coherence scores and trajectory returns
   $$r = \text{corr}(r_{\text{narrative}}, G_t)$$
   where $G_t$ is the discounted return from state $s_t$

**Computational Metrics:**

6. **Overhead:** Additional wall-clock time compared to RND baseline
   $$\text{Overhead} = \frac{T_{\text{NCIM}} - T_{\text{RND}}}{T_{\text{RND}}} \times 100\%$$

7. **LLM Inference Latency:** Time per coherence evaluation call

#### 3.3.5 Statistical Analysis

**Primary Analysis:** Two-way ANOVA on task success rate with factors Method and Environment, followed by Tukey HSD post-hoc tests for pairwise comparisons.

**Hypotheses:**
- $H_1$: NCIM achieves 20-30% higher success rate than RND (effect size Cohen's $d > 0.5$)
- $H_0$: No significant difference between NCIM and RND ($p > 0.05$)

**Power Analysis:** With 5 seeds per condition, assuming σ=0.15 and target effect size d=0.5, power = 0.80 at α=0.05 (Bonferroni corrected for multiple comparisons).

**Robustness Checks:**
1. **Cross-LLM validation:** Repeat key experiments with Mistral-7B and GPT-3.5-Turbo to verify coherence scoring is not model-specific
2. **Human baseline:** Collect human ratings of narrative coherence for 50 trajectory segments (3 raters, Krippendorff's α for inter-rater reliability)
3. **Sensitivity analysis:** Grid search over $\alpha \in [0.5, 0.95]$ and $w_1, w_2$ to identify optimal configurations

#### 3.3.6 Validation of Key Assumptions

**Assumption 1: Semantic Describability**
- **Test:** Human evaluation study (N=30 participants) rating whether state-to-text conversions preserve causal information
- **Criterion:** Mean rating > 4.0 on 5-point Likert scale

**Assumption 2: Coherence-Value Correlation**
- **Test:** Retrospective analysis computing correlation between coherence scores and trajectory returns
- **Criterion:** Pearson $r > 0.4$ in at least 75% of environments

**Assumption 3: Stable Prompting**
- **Test:** Test-retest reliability across 3 different LLMs on 100 fixed trajectory segments
- **Criterion:** Intraclass correlation coefficient (ICC) > 0.7

**Assumption 4: Computational Feasibility**
- **Test:** Empirical timing measurements during training
- **Criterion:** Overhead < 20% compared to RND baseline

**Assumption 5: Domain Generalization**
- **Test:** Transfer learning experiment: train on NetHack, evaluate on Crafter with frozen coherence weights
- **Criterion:** Performance degradation < 15% compared to environment-specific training

### 3.4 Implementation Details

**Hardware:** Single NVIDIA RTX 3090 (24GB VRAM) for RL training, with LLM inference batched and cached

**Software Stack:**
- RL framework: Stable-Baselines3 (PPO implementation)
- LLM inference: HuggingFace Transformers with 8-bit quantization
- Environments: NetHack Learning Environment, Crafter (official implementations), TextWorld, ALFWorld

**Optimization Strategies:**
1. **Caching:** Store LLM embeddings for repeated state descriptions
2. **Batching:** Accumulate narrative segments and evaluate in batches of 16
3. **Asynchronous evaluation:** Run LLM inference in parallel with environment stepping
4. **Quantization:** Use 8-bit quantized LLM to reduce memory footprint

**Expected Training Time:** ~48 hours per environment per seed (10M steps) on single RTX 3090

### 3.5 Falsification Criteria

The hypothesis will be considered falsified if any of the following occur:

1. **No significant improvement:** NCIM shows no statistically significant improvement over RND in any environment after 10M steps ($p > 0.05$)

2. **Consistent underperformance:** NCIM underperforms RND by >10% in more than 50% of test environments

3. **No coherence-value relationship:** Narrative coherence scores show no correlation with trajectory value ($|r| < 0.2$) across all environments

4. **Excessive computational cost:** Computational overhead exceeds 20% threshold, making practical deployment infeasible

5. **Failure to transfer:** Hyperparameters optimized on one environment degrade by >30% when applied to other semantically-rich environments

## 4. Expected Outcomes & Impact

### 4.1 Anticipated Results

Based on preliminary theoretical analysis and related work in curiosity-driven RL and LLM-guided decision-making, we anticipate the following outcomes:

**Primary Outcomes:**

1. **Improved Task Success Rates:** NCIM will achieve 20-30% higher success rates compared to RND baseline in NetHack and Crafter environments within 10M training steps, with statistical significance ($p < 0.01$).

2. **Enhanced Sample Efficiency:** NCIM will reach first successful episode 40-50% faster than baselines in tasks with explicit causal dependencies (NetHack key-door sequences, Crafter tool crafting chains).

3. **Richer Exploration Patterns:** NCIM will discover 40-50% more unique causal sequences in the first 5M steps, as measured by unique (entity, action, consequence) tuples.

4. **Optimal Balance Parameter:** The optimal $\alpha$ will fall in range [0.65, 0.75], indicating that narrative coherence should contribute 25-35% of the intrinsic reward signal for best performance.

**Secondary Outcomes:**

5. **Coherence-Value Correlation:** Narrative coherence scores will show moderate positive correlation ($r = 0.4-0.6$) with trajectory returns, validating that coherence captures exploration value.

6. **Cross-Environment Transfer:** Coherence evaluation weights ($w_1, w_2$) will transfer across environments with <15% performance degradation, suggesting domain-general applicability.

7. **Computational Feasibility:** With optimization strategies (batching, caching, quantization), overhead will remain below 15%, making NCIM practical for real-world deployment.

**Ablation Insights:**

8. **Component Contributions:** Both causal completeness and prediction violation will contribute significantly, with causal completeness showing stronger effects in long-horizon tasks (NetHack) and prediction violation in shorter-horizon tasks (ALFWorld).

9. **Degradation Under Pixel-Only:** When state descriptions are degraded to pixel coordinates only, NCIM performance will drop to within 5% of RND, confirming that semantic content drives the improvement.

### 4.2 Theoretical Contributions

**Contribution 1: Formalization of Narrative Coherence for RL**

This work provides the first computational operationalization of narrative coherence as an intrinsic motivation principle, bridging cognitive science theory (Information Gap Theory) with practical RL algorithms. The dual-metric framework (causal completeness + prediction violation) offers a principled approach to quantifying semantic exploration value.

**Contribution 2: Extension of LLM-RL Taxonomy**

Current taxonomies of LLM applications in RL focus on planning, reward specification, and policy representation. NCIM establishes a new category: **evaluation-based exploration bonus generation**, where LLMs serve as frozen semantic evaluators rather than active decision-makers.

**Contribution 3: Hybrid Exploration Framework**

The weighted combination of semantic coherence and state novelty ($\alpha \cdot r_{\text{RND}} + (1-\alpha) \cdot r_{\text{narrative}}$) provides a theoretically grounded approach to multi-objective exploration, with graceful degradation properties when semantic information is unavailable.

### 4.3 Methodological Contributions

**Contribution 4: State-to-Narrative Pipeline**

The template-based entity extraction and vision-language captioning pipeline provides a reusable framework for converting diverse RL state representations into natural language suitable for LLM processing, with demonstrated applicability across text-based, symbolic, and visual environments.

**Contribution 5: Few-Shot Coherence Evaluation Protocol**

The prompt engineering approach for extracting causal completeness and prediction violation scores demonstrates how frozen LLMs can be leveraged for structured evaluation tasks without fine-tuning, reducing computational requirements and improving generalization.

**Contribution 6: Validation Methodology**

The comprehensive validation framework—including human baseline studies, cross-LLM robustness checks, and assumption-specific tests—establishes best practices for evaluating LLM-augmented RL systems.

### 4.4 Practical Impact

**Impact 1: Enabling New Application Domains**

By improving sample efficiency in long-horizon sparse-reward tasks, NCIM makes RL practical for domains previously considered intractable:
- **Interactive narrative systems:** Educational games, therapeutic applications
- **Household robotics:** Multi-step manipulation tasks with semantic constraints
- **Scientific discovery:** Hypothesis generation in domains with sparse experimental feedback

**Impact 2: Reducing Reward Engineering Burden**

NCIM's semantic exploration reduces the need for hand-crafted reward shaping in tasks with clear causal structure, lowering the barrier to applying RL in new domains.

**Impact 3: Computational Accessibility**

With demonstrated feasibility on consumer-grade hardware (single RTX 3090) and <20% overhead, NCIM is accessible to academic researchers and small organizations, democratizing access to advanced exploration techniques.

**Impact 4: Human-AI Alignment**

Exploration guided by narrative coherence—a principle aligned with human curiosity—may produce more interpretable agent behaviors and facilitate human oversight in safety-critical applications.

### 4.5 Broader Implications

**For the Generative AI Community:**

This work demonstrates a novel use case for pretrained LLMs beyond generation tasks, showing how their semantic understanding can be leveraged for evaluation and guidance in interactive settings. This opens new research directions in using generative models as "semantic oracles" for decision-making systems.

**For the RL Community:**

NCIM provides empirical evidence that high-level semantic priors can be effectively integrated with low-level exploration mechanisms, challenging the prevailing focus on purely state-based curiosity. This may inspire new hybrid approaches combining learned representations with pretrained knowledge.

**For Cognitive Science:**

The computational validation of Information Gap Theory in RL settings provides a bridge between theoretical models of human curiosity and practical AI systems, potentially informing both fields through bidirectional insights.

### 4.6 Limitations and Future Work

**Known Limitations:**

1. **Semantic Environment Requirement:** NCIM requires environments where states can be meaningfully described in natural language, limiting applicability to abstract or purely continuous control tasks.

2. **Computational Overhead:** Despite optimization, LLM inference adds 10-20% overhead, which may be prohibitive in real-time systems requiring <10ms latency.

3. **LLM Bias:** Coherence evaluations may reflect biases in LLM pretraining data, potentially favoring stereotypical narratives over novel but valid causal sequences.

**Future Research Directions:**

1. **Adaptive Weighting:** Learn $\alpha$ dynamically based on task phase (e.g., higher semantic weight early, higher novelty weight later)

2. **Hierarchical Coherence:** Extend to multi-scale coherence evaluation (local action sequences, mid-level subgoals, global task narratives)

3. **Active Coherence Queries:** Allow agents to query LLM for coherence predictions to guide action selection, not just evaluate past trajectories

4. **Cross-Modal Coherence:** Extend to video prediction models for pixel-based environments without language grounding

5. **Real-World Robotics:** Validate in physical manipulation tasks with vision-language models (e.g., RT-2, PaLM-E)

### 4.7 Success Metrics and Timeline

**6-Month Milestones:**
- Month 1-2: Implementation and validation of state-to-narrative pipeline
- Month 3-4: Core NCIM experiments in Crafter and TextWorld
- Month 5-6: NetHack experiments and cross-environment transfer studies

**Success Criteria:**
- **Minimum viable success:** 15% improvement over RND in at least 2 environments
- **Target success:** 20-30% improvement in 3+ environments with <20% overhead
- **Exceptional success:** 30%+ improvement with demonstrated transfer and human validation

**Dissemination Plan:**
- Conference submission: NeurIPS, ICML, or ICLR (Generative Models for Decision Making track)
- Open-source release: Code, trained models, and evaluation datasets
- Workshop presentation: Findings and community feedback

This research represents a significant step toward bridging generative AI and decision-making, with potential to fundamentally change how we approach exploration in semantically-rich environments. By grounding exploration in narrative coherence—a principle central to human cognition—we aim to create RL agents that explore more intelligently, learn more efficiently, and behave more interpretably.