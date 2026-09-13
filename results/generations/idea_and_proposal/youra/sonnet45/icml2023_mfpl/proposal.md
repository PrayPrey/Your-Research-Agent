# Research Proposal: Nash-Fair Multi-Objective Reinforcement Learning from Human Preferences

## 1. Title

**Nash-Fair Multi-Objective Reinforcement Learning: Integrating Game-Theoretic Stakeholder Fairness with Demographic Parity Constraints through Preference-Based Learning**

## 2. Introduction

### 2.1 Background

Preference-based learning has emerged as a cornerstone methodology in modern artificial intelligence, enabling systems to learn from human feedback without requiring precise numerical annotations. This paradigm has proven particularly transformative in large language model alignment (Bai et al., 2022), where reinforcement learning from human feedback (RLHF) has enabled models to follow instructions and engage in helpful dialogue. The fundamental insight—that humans provide more reliable relative judgments than absolute ratings—has extended to robotics, recommender systems, healthcare decision support, and autonomous vehicles.

Despite these successes, contemporary preference-based systems face a critical **fairness-utility-preference trilemma**. Current approaches fall into three inadequate categories:

1. **Utility-maximizing systems** that optimize stakeholder preferences without fairness guarantees, creating regulatory compliance risks under emerging frameworks like the EU AI Act and algorithmic accountability laws.

2. **Post-hoc fairness correction** methods that apply demographic parity constraints after optimization, violating theoretical optimality properties and lacking axiomatic foundations for stakeholder fairness.

3. **Hand-crafted reward engineering** approaches that attempt to balance objectives through weighted combinations, suffering from reward misspecification bias and inability to capture true Pareto-optimal trade-offs.

This trilemma is particularly acute in high-stakes domains. In healthcare resource allocation, a system must balance patient outcomes (clinical stakeholders), cost efficiency (administrative stakeholders), and demographic fairness across protected groups. In lending, models must satisfy lender profit objectives, borrower access preferences, and statistical parity requirements. Current methods cannot simultaneously guarantee axiomatic stakeholder fairness, statistical demographic parity, and multi-objective preference aggregation.

Recent theoretical advances provide building blocks for addressing this challenge. Mu et al. (2025) demonstrated that Pareto-optimal policies can be derived directly from preference data, eliminating reward engineering bias. Yang et al. (2023) showed 31% fairness improvements through explicit demographic constraints in clinical machine learning. Nash Bargaining solutions (Nash, 1950) provide 70+ years of validated axiomatic foundations for fair multi-stakeholder decision-making, recently applied to ethical AI systems (Skorin-Kapov, 2025). However, these advances remain isolated—no existing framework integrates preference-based Pareto derivation, demographic fairness constraints, and game-theoretic stakeholder fairness.

### 2.2 Research Objectives

This research proposes **Nash-Fair Multi-Objective Reinforcement Learning (Nash-Fair MORL)**, a novel three-stage framework that uniquely integrates:

1. **Preference-based Pareto derivation** (Stage 1) that learns multi-objective reward models from pairwise comparisons and derives Pareto-optimal policies without reward engineering.

2. **Demographic fairness filtering** (Stage 2) that enforces statistical parity constraints (disparity < 5%) across protected groups.

3. **Nash Bargaining selection** (Stage 3) that chooses the final policy by maximizing stakeholder utility products while satisfying all four Nash axioms: Pareto efficiency, symmetry, independence of irrelevant alternatives, and scale invariance.

**Primary Research Question:** Can sequential integration of preference-based learning, demographic fairness constraints, and game-theoretic stakeholder fairness simultaneously satisfy regulatory compliance, axiomatic optimality, and multi-stakeholder preference aggregation without sacrificing task performance?

**Specific Objectives:**

- **O1:** Develop a theoretically grounded framework proving Nash axiom preservation under discrete fairness constraints through convex hull approximation.

- **O2:** Design robust algorithmic implementations handling practical challenges (empty fairness sets, stakeholder utility learning, computational tractability).

- **O3:** Empirically validate across three domains (simulated control, LLM alignment, recommender systems) that Nash-Fair MORL achieves ≥1.5× improvement in stakeholder utility product versus single-objective baselines while maintaining demographic parity < 0.05.

- **O4:** Establish conditions under which the framework fails (boundary analysis) and develop mitigation strategies.

### 2.3 Significance

This research addresses critical gaps at the intersection of preference-based learning, multi-objective optimization, and algorithmic fairness:

**Theoretical Contributions:**
- First axiomatic fairness foundation for multi-stakeholder preference-based machine learning, unifying game-theoretic and algorithmic fairness paradigms.
- Formal analysis proving sequential integration preserves Nash axioms on convex hulls with bounded approximation error.

**Methodological Contributions:**
- Robust three-stage pipeline with novel techniques for stakeholder utility learning from stratified preference data.
- Integration protocol for heterogeneous fairness criteria (axiomatic + statistical) with adaptive relaxation mechanisms.

**Practical Impact:**
- Regulatory compliance tool for EU AI Act Article 10 (bias monitoring) and US algorithmic accountability frameworks.
- Transparent visualization enabling stakeholders to understand trade-offs between utility and fairness.
- Dynamic re-weighting capability allowing policy adjustment without costly retraining.

The framework is particularly timely given increasing regulatory pressure. The EU AI Act mandates fairness monitoring for high-risk AI systems, while US agencies are developing algorithmic accountability standards. Nash-Fair MORL provides a principled methodology satisfying both legal requirements and ethical desiderata.

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Problem Formulation

We consider a Markov Decision Process (MDP) $\mathcal{M} = (\mathcal{S}, \mathcal{A}, \mathcal{T}, \gamma)$ with state space $\mathcal{S}$, action space $\mathcal{A}$, transition dynamics $\mathcal{T}$, and discount factor $\gamma \in [0,1)$. The system involves:

- **K objectives**: Each objective $k \in \{1, \ldots, K\}$ has reward function $r_k: \mathcal{S} \times \mathcal{A} \rightarrow \mathbb{R}$.
- **M stakeholders**: Each stakeholder $m \in \{1, \ldots, M\}$ has utility function $U_m: \Pi \rightarrow \mathbb{R}$ over policy space $\Pi$.
- **Protected attribute**: $A \in \{a_1, \ldots, a_L\}$ defining demographic groups.

**Preference Data**: We collect dataset $\mathcal{D} = \{(\tau_i^{(1)}, \tau_i^{(2)}, y_i)\}_{i=1}^N$ where $\tau_i^{(j)}$ are trajectory segments and $y_i \in \{1, 2\}$ indicates human preference.

**Demographic Fairness**: For binary decision $\hat{y}$, demographic parity requires:

$$\Delta_{DP} = \max_{a, a' \in \mathcal{A}} |P(\hat{y}=1|A=a) - P(\hat{y}=1|A=a')| < \epsilon$$

where $\epsilon$ is the fairness threshold (typically 0.05 for regulatory compliance).

#### 3.1.2 Nash Bargaining Solution

Given stakeholder utilities $\mathbf{u} = (U_1(\pi), \ldots, U_M(\pi))$ and disagreement point $\mathbf{d} = (d_1, \ldots, d_M)$, the Nash Bargaining solution maximizes:

$$\mathbf{u}^* = \arg\max_{\mathbf{u} \in \mathcal{F}} \prod_{m=1}^M (u_m - d_m)$$

where $\mathcal{F}$ is the feasible utility set. This solution uniquely satisfies four axioms:

1. **Pareto Efficiency**: No alternative improves one stakeholder without harming another.
2. **Symmetry**: Identical stakeholders receive identical utilities.
3. **Independence of Irrelevant Alternatives**: Removing inferior options doesn't change the solution.
4. **Scale Invariance**: Affine transformations of utilities don't affect the solution.

### 3.2 Nash-Fair MORL Algorithm

#### Stage 1: Preference-Based Pareto Derivation

**Step 1.1: Multi-Objective Reward Learning**

We model preferences using the Bradley-Terry model extended to multi-objective settings:

$$P(\tau^{(1)} \succ \tau^{(2)}) = \sigma\left(\sum_{k=1}^K w_k \left[\sum_{t} r_k^\theta(s_t^{(1)}, a_t^{(1)}) - \sum_{t} r_k^\theta(s_t^{(2)}, a_t^{(2)})\right]\right)$$

where $\sigma$ is the sigmoid function, $r_k^\theta$ are parameterized reward models, and $w_k$ are objective weights sampled from simplex $\Delta^{K-1}$.

We optimize reward parameters $\theta$ via maximum likelihood:

$$\theta^* = \arg\max_\theta \sum_{i=1}^N \log P(\tau_i^{(y_i)} \succ \tau_i^{(3-y_i)} | \theta)$$

**Step 1.2: Pareto Frontier Approximation**

For each weight vector $\mathbf{w}^{(j)} \in \Delta^{K-1}$ (sampled uniformly with $J=50$ samples), we train a policy $\pi_j$ via reinforcement learning maximizing scalarized reward:

$$\pi_j = \arg\max_\pi \mathbb{E}_{\pi}\left[\sum_{t=0}^\infty \gamma^t \sum_{k=1}^K w_k^{(j)} r_k^\theta(s_t, a_t)\right]$$

We use Proximal Policy Optimization (PPO) with the following hyperparameters:
- Learning rate: $3 \times 10^{-4}$ with cosine annealing
- Batch size: 2048 transitions
- Epochs per update: 10
- Clip parameter: 0.2
- GAE parameter $\lambda$: 0.95

The Pareto frontier approximation is:

$$\mathcal{P} = \{\pi_j : \pi_j \text{ is non-dominated}, j=1,\ldots,J\}$$

where $\pi_j$ is non-dominated if no other policy achieves strictly better rewards on all objectives.

#### Stage 2: Demographic Fairness Filtering

**Step 2.1: Fairness Evaluation**

For each policy $\pi \in \mathcal{P}$, we evaluate demographic parity on held-out data $\mathcal{D}_{test}$:

$$\Delta_{DP}(\pi) = \max_{a, a'} \left|\frac{1}{|\mathcal{D}_a|}\sum_{i \in \mathcal{D}_a} \mathbb{1}[\hat{y}_i^\pi = 1] - \frac{1}{|\mathcal{D}_{a'}|}\sum_{i \in \mathcal{D}_{a'}} \mathbb{1}[\hat{y}_i^\pi = 1]\right|$$

where $\mathcal{D}_a = \{i : A_i = a\}$ and $\hat{y}_i^\pi$ is the decision under policy $\pi$.

**Step 2.2: Fairness-Compliant Subset**

We filter policies satisfying the fairness constraint:

$$\mathcal{P}_{fair} = \{\pi \in \mathcal{P} : \Delta_{DP}(\pi) < \epsilon\}$$

**Adaptive Relaxation**: If $|\mathcal{P}_{fair}| < 3$, we incrementally increase $\epsilon$ by 10% until $|\mathcal{P}_{fair}| \geq 3$ or $\epsilon > 0.15$ (at which point we report failure).

#### Stage 3: Nash Bargaining Selection

**Step 3.1: Stakeholder Utility Learning**

We learn stakeholder-specific utility functions from stratified preference data. For stakeholder $m$, we collect preferences $\mathcal{D}_m = \{(\tau_i^{(1)}, \tau_i^{(2)}, y_i^m)\}$ where annotators belong to stakeholder group $m$.

We train utility predictors $U_m^\phi: \Pi \rightarrow \mathbb{R}$ using neural networks with architecture:
- Input: Policy performance vector (K-dimensional objective returns)
- Hidden layers: [128, 64, 32] with ReLU activations
- Output: Scalar utility estimate
- Loss: Mean squared error on held-out preferences

**Step 3.2: Convex Hull Approximation**

We compute utility vectors for fairness-compliant policies:

$$\mathcal{U}_{fair} = \{(U_1^\phi(\pi), \ldots, U_M^\phi(\pi)) : \pi \in \mathcal{P}_{fair}\}$$

We approximate the convex hull using QuickHull algorithm:

$$\mathcal{H}(\mathcal{U}_{fair}) = \text{ConvexHull}(\mathcal{U}_{fair})$$

**Step 3.3: Nash Bargaining Optimization**

We solve the Nash Bargaining problem on the convex hull:

$$\mathbf{u}^* = \arg\max_{\mathbf{u} \in \mathcal{H}(\mathcal{U}_{fair})} \prod_{m=1}^M (u_m - d_m)$$

where disagreement point $\mathbf{d}$ is set to the minimum utility each stakeholder receives from any policy in $\mathcal{P}_{fair}$:

$$d_m = \min_{\pi \in \mathcal{P}_{fair}} U_m^\phi(\pi)$$

We solve this using log-barrier interior point method:

$$\mathbf{u}^* = \arg\max_{\mathbf{u} \in \mathcal{H}(\mathcal{U}_{fair})} \sum_{m=1}^M \log(u_m - d_m)$$

**Step 3.4: Policy Selection**

We select the policy closest to the Nash solution:

$$\pi^* = \arg\min_{\pi \in \mathcal{P}_{fair}} \|\mathbf{u}(\pi) - \mathbf{u}^*\|_2$$

where $\mathbf{u}(\pi) = (U_1^\phi(\pi), \ldots, U_M^\phi(\pi))$.

### 3.3 Experimental Design

#### 3.3.1 Domains and Datasets

We validate across three domains representing diverse preference-based learning applications:

**Domain 1: Simulated Continuous Control (MuJoCo)**
- Environment: HalfCheetah-v4 with 3 objectives (speed, energy efficiency, stability)
- Stakeholders: 3 groups (performance-focused, efficiency-focused, safety-focused)
- Protected attribute: Simulated user demographics (3 groups)
- Preference data: 50K pairwise comparisons from synthetic annotators
- Metrics: Average return, energy consumption, fall rate

**Domain 2: Large Language Model Alignment**
- Base model: GPT-2 (124M parameters)
- Task: Helpful and harmless dialogue responses
- Objectives: Helpfulness, harmlessness, engagement
- Stakeholders: Users, content moderators, platform operators
- Protected attribute: User demographic groups from Anthropic HH dataset
- Preference data: 52K human comparisons from Anthropic HH-RLHF dataset
- Metrics: Win rate vs baseline, toxicity score (Perspective API), engagement score

**Domain 3: Recommender Systems**
- Dataset: MovieLens-1M with demographic annotations
- Objectives: Accuracy, diversity, novelty
- Stakeholders: Users, content creators, platform
- Protected attribute: User age groups and gender
- Preference data: 100K implicit preferences from click-through data
- Metrics: NDCG@10, diversity (intra-list distance), novelty (popularity complement)

#### 3.3.2 Baseline Methods

We compare against six baselines:

1. **Weighted Sum (WS)**: Scalarized reward $r = \sum_k w_k r_k$ with hand-tuned weights
2. **Random Pareto (RP)**: Random selection from Pareto frontier $\mathcal{P}$
3. **Post-Hoc Fairness (PHF)**: Optimize unconstrained Nash, then apply fairness correction
4. **Unconstrained Nash (UN)**: Nash Bargaining without fairness constraints
5. **FairDICE**: Offline Nash social welfare optimization (Kim et al., 2025)
6. **Nash-Fair MORL (Ours)**: Full three-stage pipeline

#### 3.3.3 Evaluation Metrics

**Primary Metrics:**

1. **Stakeholder Utility Product**: 
$$\text{SUP} = \prod_{m=1}^M (U_m(\pi^*) - d_m)$$

2. **Demographic Parity Violation**:
$$\Delta_{DP} = \max_{a,a'} |P(\hat{y}=1|A=a) - P(\hat{y}=1|A=a')|$$

3. **Nash Axiom Satisfaction**: Binary indicators for each axiom (Pareto efficiency, symmetry, IIA, scale invariance) verified through formal tests

4. **Task Performance**: Domain-specific metrics normalized by unconstrained optimum

**Secondary Metrics:**

5. **Pareto Frontier Coverage**: Hypervolume indicator
6. **Fairness Set Size**: $|\mathcal{P}_{fair}|$
7. **Approximation Error**: $\|\mathbf{u}(\pi^*) - \mathbf{u}^*\|_2$
8. **Computational Cost**: Wall-clock time and GPU hours

#### 3.3.4 Statistical Analysis

**Experimental Design:**
- Factorial design: 6 methods × 3 domains × 3 problem sizes (small/medium/large)
- Sample size: 30 independent runs per condition
- Total experiments: 1,620
- Power analysis: 80% power to detect Cohen's d = 0.5 at α = 0.01

**Hypothesis Tests:**

**H1 (Utility Improvement)**: Nash-Fair MORL achieves higher stakeholder utility product than all baselines
- Test: Paired t-test with Bonferroni correction (α = 0.01/5 = 0.002)
- Effect size: Cohen's d
- Prediction: SUP(Nash-Fair) ≥ 1.5 × max(SUP(baselines))

**H2 (Fairness Compliance)**: Nash-Fair MORL satisfies demographic parity constraint
- Test: One-sample t-test against threshold 0.05
- Prediction: $\Delta_{DP} < 0.05$ with 95% confidence

**H3 (Axiom Satisfaction)**: Nash-Fair MORL satisfies all four Nash axioms
- Test: Exact binomial test for each axiom
- Prediction: 100% satisfaction rate (30/30 runs)

**H4 (Performance Trade-off)**: Task performance remains acceptable
- Test: Paired t-test against 90% threshold
- Prediction: Performance ≥ 0.90 × unconstrained optimum

**Falsification Criteria**: The hypothesis is rejected if:
- Utility product < 1.0× best baseline (no improvement)
- Demographic parity > 0.10 in >10% of runs (regulatory violation)
- ≥2 Nash axioms fail in >20% of runs (theoretical claim invalid)
- Task performance < 0.80× unconstrained in >30% of runs (unacceptable degradation)

#### 3.3.5 Ablation Studies

We conduct ablation studies to isolate component contributions:

1. **Stage Ablations**:
   - No Stage 1: Use hand-crafted rewards instead of preference-based learning
   - No Stage 2: Skip fairness filtering
   - No Stage 3: Random selection instead of Nash Bargaining

2. **Hyperparameter Sensitivity**:
   - Fairness threshold: ε ∈ {0.01, 0.03, 0.05, 0.07, 0.10}
   - Pareto samples: J ∈ {10, 25, 50, 100, 200}
   - Preference dataset size: N ∈ {1K, 5K, 10K, 50K, 100K}

3. **Robustness Analysis**:
   - Annotator disagreement: Krippendorff's α ∈ {0.4, 0.6, 0.8}
   - Stakeholder conflict: Correlation between utilities ∈ {-0.8, -0.4, 0, 0.4, 0.8}
   - Protected group imbalance: Ratio ∈ {1:1, 2:1, 5:1, 10:1}

### 3.4 Implementation Details

**Software Stack:**
- PyTorch 2.0 for neural network training
- Stable-Baselines3 for RL algorithms
- SciPy for convex optimization
- Weights & Biases for experiment tracking

**Computational Resources:**
- 4× NVIDIA A100 GPUs (40GB)
- Estimated 2,000 GPU hours total
- Parallel execution across conditions

**Reproducibility:**
- Fixed random seeds for all experiments
- Version-controlled codebase (GitHub)
- Containerized environment (Docker)
- Public release of code and preprocessed datasets

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Predictions:**

Based on preliminary theoretical analysis and related work, we predict:

1. **Stakeholder Utility Product**: 1.5-2.0× improvement over single-objective baselines, with 95% CI: [1.3, 2.2]

2. **Demographic Parity**: Mean violation 0.03 ± 0.01, with 95% of runs achieving < 0.05 threshold

3. **Nash Axiom Satisfaction**: 100% satisfaction for Pareto efficiency and scale invariance; 95%+ for symmetry and IIA (allowing for numerical approximation errors)

4. **Task Performance**: 92% ± 5% of unconstrained optimum across domains

5. **Pareto Coverage**: Hypervolume indicator 0.85 ± 0.08 relative to true Pareto frontier

**Qualitative Insights:**

- **Failure Modes**: We expect the framework to struggle when:
  - Preference data is insufficient (N < 5K) or highly inconsistent (α < 0.4)
  - Stakeholder utilities are strongly anti-correlated (ρ < -0.6)
  - Fairness constraints are extremely strict (ε < 0.02) with small Pareto frontiers
  
- **Domain Variations**: We anticipate stronger results in MuJoCo (controlled environment) compared to LLM alignment (noisy human preferences) and recommender systems (sparse feedback)

- **Scalability**: Computational cost should scale linearly with number of Pareto samples J and quadratically with number of stakeholders M

### 4.2 Theoretical Impact

This research will advance preference-based learning theory by:

1. **Unifying Fairness Paradigms**: Providing the first formal framework integrating game-theoretic (Nash axioms) and algorithmic (demographic parity) fairness notions, demonstrating they are complementary rather than contradictory.

2. **Approximation Guarantees**: Establishing theoretical bounds on how convex hull approximation and discrete policy selection affect Nash axiom satisfaction, extending classical bargaining theory to practical ML settings.

3. **Preference-Fairness Interaction**: Characterizing conditions under which preference-based learning preserves or violates fairness properties, informing future RLHF research.

### 4.3 Methodological Impact

The framework will provide practitioners with:

1. **Regulatory Compliance Tool**: Turnkey solution for EU AI Act Article 10 (bias monitoring) and emerging US algorithmic accountability requirements, with automated fairness certification.

2. **Transparent Trade-off Visualization**: Interactive dashboards showing stakeholder utility frontiers and fairness impact, enabling informed policy selection by non-technical decision-makers.

3. **Modular Design**: Each stage can be independently improved or replaced, allowing integration with future advances in preference learning, fairness constraints, or multi-objective optimization.

4. **Dynamic Adaptation**: Stakeholder preferences can be re-weighted without retraining policies (re-run Stage 3 only), enabling rapid response to changing priorities.

### 4.4 Practical Impact

**High-Stakes Applications:**

- **Healthcare Resource Allocation**: Balance patient outcomes, cost efficiency, and demographic equity in treatment recommendations, with provable fairness guarantees for regulatory approval.

- **Financial Services**: Lending and credit scoring systems satisfying both lender profitability and borrower access preferences while meeting fair lending laws (ECOA, FCRA).

- **Content Moderation**: Social media platforms balancing user engagement, advertiser interests, and content creator welfare with demographic fairness across user populations.

**Broader Societal Impact:**

- **Algorithmic Accountability**: Provides auditable framework for demonstrating fairness compliance to regulators and affected communities.

- **Stakeholder Participation**: Enables meaningful inclusion of diverse stakeholder preferences in AI system design, addressing power imbalances in current development processes.

- **Trust and Adoption**: Transparent fairness guarantees may increase public trust in AI systems, particularly in communities historically harmed by algorithmic bias.

### 4.5 Limitations and Future Work

**Known Limitations:**

1. **Preference Data Requirements**: Requires substantial pairwise comparisons (10K+), which may be expensive to collect in some domains.

2. **Computational Cost**: Three-stage pipeline is more expensive than single-objective optimization, though still tractable for offline policy selection.

3. **Static Fairness Constraints**: Demographic parity may not capture all fairness desiderata (e.g., individual fairness, causal fairness).

4. **Stakeholder Identification**: Assumes stakeholder groups are pre-defined, which may be contested in practice.

**Future Research Directions:**

- **Active Preference Learning**: Adaptive query selection to minimize annotation cost while maintaining Pareto coverage.

- **Online Nash-Fair MORL**: Extend to online settings with streaming preferences and evolving fairness constraints.

- **Causal Fairness Integration**: Incorporate causal graph constraints alongside demographic parity.

- **Participatory Design**: Methods for stakeholder group identification and preference elicitation in contested settings.

- **Theoretical Extensions**: Tighter approximation bounds, alternative bargaining solutions (Kalai-Smorodinsky, egalitarian), and connections to social choice theory.

### 4.6 Dissemination Plan

**Academic Outputs:**
- Conference submission: NeurIPS 2026 Workshop on Preference-Based Learning (target venue)
- Journal submission: Journal of Machine Learning Research (extended version)
- Workshop presentations at ICML, ICLR, FAccT

**Open-Source Release:**
- GitHub repository with full implementation
- PyPI package for easy integration
- Documentation and tutorials
- Benchmark datasets and evaluation scripts

**Community Engagement:**
- Blog posts explaining methodology for practitioners
- Webinar series on fairness in preference-based learning
- Collaboration with regulatory bodies (NIST AI Risk Management Framework)

This research addresses a critical gap at the intersection of preference-based learning, multi-objective optimization, and algorithmic fairness. By providing the first framework simultaneously satisfying axiomatic stakeholder fairness, statistical demographic parity, and multi-objective preference aggregation, Nash-Fair MORL has potential to transform how AI systems are designed, evaluated, and deployed in high-stakes societal applications.