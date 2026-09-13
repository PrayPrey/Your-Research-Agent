# Research Proposal: Algorithmic Process Fairness in RLHF Alignment

## 1. Title

**Algorithmic Process Fairness in Reinforcement Learning from Human Feedback: Addressing Hidden Discrimination Through In-Context Algorithm Selection**

## 2. Introduction

### 2.1 Background

Recent advancements in foundation models, particularly large language models (LLMs), have demonstrated remarkable capabilities across diverse tasks. A critical component of their success is Reinforcement Learning from Human Feedback (RLHF), which aligns model outputs with human preferences. However, as these models are deployed in high-stakes domains such as healthcare, finance, and legal decision-making, concerns about fairness and bias have intensified.

Current RLHF fairness research focuses exclusively on output-level metrics such as demographic parity and equalized odds. While these metrics ensure that model predictions are distributed fairly across demographic groups, they overlook a fundamental dimension: **algorithmic process fairness**. Recent theoretical work by Bai et al. (2023) has demonstrated that transformers implement different algorithms during in-context learning (ICL)—including ridge regression, Lasso, least squares, and generalized linear models—based on prompt structure and context. This discovery reveals a critical gap: if different demographic groups have distinct algorithmic preferences (e.g., conservative/hedging versus decisive/sparse reasoning styles), standard RLHF may create systematic discrimination by penalizing certain reasoning processes while appearing fair at the output level.

This hidden form of discrimination is particularly concerning in domains where reasoning transparency matters. For instance, in healthcare, some cultural groups may prefer conservative treatment recommendations (analogous to ridge regression's hedging behavior), while others may prefer decisive, targeted interventions (analogous to Lasso's sparse solutions). If RLHF optimization systematically penalizes one reasoning style to achieve output-level fairness, it creates a form of algorithmic injustice invisible to existing metrics.

### 2.2 Research Objectives

This research aims to establish algorithmic process fairness as an independent and essential dimension of RLHF alignment. Our specific objectives are:

1. **Validate the existence of algorithmic preference diversity**: Empirically demonstrate that different demographic groups exhibit statistically significant differences in algorithmic preferences (conservative/regularized versus decisive/sparse reasoning).

2. **Detect and measure algorithmic unfairness**: Develop methods to identify which in-context learning algorithms transformers implement during RLHF training and measure fairness violations at the algorithmic process level.

3. **Design algorithm-aware RLHF**: Extend existing RLHF frameworks (specifically MaxMin-RLHF) with an algorithmic fairness term that respects diverse reasoning styles while maintaining output-level fairness.

4. **Empirically validate improvements**: Demonstrate that algorithm-aware RLHF reduces algorithmic unfairness by ≥30% compared to standard approaches while maintaining output fairness metrics (regression <5%).

### 2.3 Research Significance

This research addresses a critical gap at the intersection of three theoretical communities: in-context learning theory, RLHF fairness, and social choice theory. Its significance spans multiple dimensions:

**Theoretical Impact**: This work challenges the prevailing assumption that output-level fairness metrics are sufficient for responsible AI alignment. By establishing algorithmic process fairness as an independent dimension, we provide a more complete framework for understanding fairness in foundation models. This extends MaxMin-RLHF from output-level optimization to meta-level reasoning, incorporating ICL algorithm selection theory and social choice axioms (non-dictatorship, proportional veto).

**Methodological Impact**: We introduce novel techniques including algorithm-aware reward modeling, ICL algorithm detection via mechanistic interpretability, and multi-group algorithmic preference elicitation. These methods operationalize abstract concepts of "reasoning style" and "algorithmic preference" into measurable, optimizable quantities.

**Practical Impact**: This research directly addresses fairness concerns in high-stakes AI deployment. In healthcare, finance, and legal domains where reasoning transparency is critical, ensuring that AI systems respect diverse problem-solving approaches is essential for equitable access and trust. Our framework provides actionable metrics and training procedures for practitioners deploying RLHF-aligned models.

**Policy Impact**: As regulatory frameworks for AI fairness emerge, this work provides evidence that output-only fairness audits are insufficient. Algorithmic process fairness offers a new dimension for responsible AI governance, particularly relevant for the EU AI Act and similar regulations requiring transparency in automated decision-making.

## 3. Methodology

### 3.1 Research Design Overview

Our methodology follows a phased validation approach with three main stages:

- **Phase 1A**: Validate algorithmic preference diversity across demographic groups (human study)
- **Phase 1B**: Develop and validate ICL algorithm detection methods (proof-of-concept)
- **Phase 2**: Design and implement algorithm-aware RLHF framework
- **Phase 3**: Comparative evaluation via A/B testing

### 3.2 Phase 1A: Algorithmic Preference Diversity Study

**Objective**: Empirically validate that different demographic groups exhibit distinct algorithmic preferences.

**Study Design**: Between-subjects survey with N=500+ participants, stratified across demographic groups (age, gender, ethnicity, education level).

**Procedure**:

1. **Scenario Development**: Create 20 decision-making scenarios with accessible framing that map to algorithmic styles:
   - **Conservative/Hedging scenarios**: "Would you prefer a treatment plan that moderately addresses all symptoms (ridge-like) or focuses intensely on the primary symptom (Lasso-like)?"
   - **Risk-taking scenarios**: "When making financial decisions, do you prefer diversified moderate investments (ridge) or concentrated high-conviction bets (Lasso)?"

2. **Response Collection**: Participants rate preferences on 7-point Likert scales. Responses are aggregated into algorithmic preference scores:
   $$\text{AlgPref}_i = \frac{1}{20}\sum_{j=1}^{20} w_j \cdot r_{ij}$$
   where $w_j$ are weights mapping scenarios to algorithm types, and $r_{ij}$ is participant $i$'s response to scenario $j$.

3. **Statistical Analysis**:
   - **Primary test**: One-way ANOVA to detect group differences in algorithmic preferences
   - **Null hypothesis**: $H_0: \mu_1 = \mu_2 = \ldots = \mu_k$ (no group differences)
   - **Alternative hypothesis**: $H_1:$ At least one group mean differs significantly
   - **Significance threshold**: $p < 0.05$
   - **Post-hoc analysis**: Tukey HSD for pairwise comparisons
   - **Effect size**: Cohen's $f$ to quantify practical significance (target: $f \geq 0.25$, medium effect)

4. **Power Analysis**: With N=500 distributed across 4 groups (n=125 per group), we achieve 80% power to detect medium effect sizes ($f = 0.25$) at $\alpha = 0.05$.

**Success Criteria**: Statistical significance ($p < 0.05$) in ANOVA with at least one pairwise comparison showing meaningful difference (Cohen's $d \geq 0.5$).

### 3.3 Phase 1B: ICL Algorithm Detection Proof-of-Concept

**Objective**: Demonstrate feasibility of detecting which algorithm transformers implement during in-context learning.

**Model Architecture**: GPT-2 (124M parameters) as proof-of-concept, with plans to scale to larger models (1B+ parameters) in Phase 2.

**Task Design**: Linear regression tasks with varying regularization to trigger different ICL algorithms:

1. **Ridge-inducing prompts**: High-dimensional contexts with correlated features
2. **Lasso-inducing prompts**: Sparse ground-truth with irrelevant features
3. **Least squares prompts**: Low-dimensional, well-conditioned problems
4. **GLM prompts**: Non-linear relationships requiring generalized linear models

**Detection Method**: Train linear probing classifiers on transformer internal representations.

**Procedure**:

1. **Data Generation**: Create 10,000 ICL tasks per algorithm type (40,000 total)
   - Input format: Few-shot examples + query point
   - Ground truth labels: {ridge, Lasso, least_squares, GLM}

2. **Activation Extraction**: Extract hidden states from layers 8-12 (middle-to-late layers where algorithm selection likely occurs):
   $$\mathbf{h}^{(l)}_t \in \mathbb{R}^{d_{\text{model}}}$$
   where $l \in \{8, 9, 10, 11, 12\}$ and $t$ is the final token position.

3. **Probing Classifier**: Train linear classifier:
   $$\hat{y} = \text{softmax}(\mathbf{W}\mathbf{h}^{(l)}_t + \mathbf{b})$$
   where $\mathbf{W} \in \mathbb{R}^{4 \times d_{\text{model}}}$ and $\mathbf{b} \in \mathbb{R}^4$.

4. **Training**: 80/20 train-test split, cross-entropy loss, Adam optimizer ($\text{lr} = 10^{-3}$)

5. **Evaluation Metrics**:
   - **Primary**: Classification accuracy (target: >75%, chance: 25%)
   - **Secondary**: Per-class F1 scores (ensure balanced performance)
   - **Robustness**: Test on out-of-distribution prompts (different task domains)

**Success Criteria**: Achieve >75% classification accuracy with balanced F1 scores (>0.70 for each algorithm class).

### 3.4 Phase 2: Algorithm-Aware RLHF Framework

**Objective**: Design and implement RLHF training that optimizes both output fairness and algorithmic fairness.

**Baseline**: MaxMin-RLHF (Chakraborty et al., 2024), which optimizes:
$$\max_{\theta} \min_{g \in \mathcal{G}} \mathbb{E}_{(x,y) \sim \mathcal{D}_g}[r_{\text{output}}(y|x)]$$
where $\mathcal{G}$ is the set of demographic groups and $r_{\text{output}}$ is the output-level reward.

**Our Extension**: Algorithm-aware reward function:
$$R_{\text{total}}(x, y, a, g) = R_{\text{output}}(y|x, g) + \lambda \cdot R_{\text{alg}}(a|x, g)$$

where:
- $a \in \{\text{ridge}, \text{Lasso}, \text{LS}, \text{GLM}\}$ is the detected ICL algorithm
- $\lambda$ is a hyperparameter balancing output and algorithmic fairness
- $R_{\text{alg}}$ is the algorithmic fairness reward

**Algorithmic Fairness Reward Design**:

We incorporate two social choice axioms:

1. **Non-Dictatorship**: No single group's algorithmic preference dominates
   $$R_{\text{non-dict}}(a|x, g) = -\max_{g' \in \mathcal{G}} \left|\mathbb{P}(a|g') - \mathbb{P}(a|g)\right|$$

2. **Proportional Veto**: Minority groups can veto algorithms systematically disfavoring their preferences
   $$R_{\text{veto}}(a|x, g) = \mathbb{I}\left[\mathbb{P}(a|g) \geq \tau \cdot \mathbb{P}(a)\right]$$
   where $\tau \in [0.5, 1]$ is the veto threshold (e.g., $\tau = 0.7$ means group usage should be ≥70% of population average).

Combined algorithmic fairness reward:
$$R_{\text{alg}}(a|x, g) = \alpha \cdot R_{\text{non-dict}}(a|x, g) + (1-\alpha) \cdot R_{\text{veto}}(a|x, g)$$

**Training Procedure**:

1. **Preference Data Collection**: Gather human feedback on outputs from diverse demographic groups (N=10,000 comparisons per group)

2. **Reward Model Training**: Train reward model $r_\phi(x, y, a, g)$ using Bradley-Terry model:
   $$\mathbb{P}(y_1 \succ y_2 | x, g) = \sigma(r_\phi(x, y_1, a_1, g) - r_\phi(x, y_2, a_2, g))$$
   where $a_1, a_2$ are detected algorithms for outputs $y_1, y_2$.

3. **Policy Optimization**: Use PPO (Proximal Policy Optimization) with algorithm-aware objective:
   $$\max_{\theta} \min_{g \in \mathcal{G}} \mathbb{E}_{x \sim \mathcal{D}_g, y \sim \pi_\theta(\cdot|x)} \left[R_{\text{total}}(x, y, a, g)\right] - \beta \cdot \text{KL}(\pi_\theta || \pi_{\text{ref}})$$
   where $\beta$ controls deviation from reference policy $\pi_{\text{ref}}$.

4. **Hyperparameter Tuning**: Grid search over $\lambda \in \{0.1, 0.3, 0.5, 0.7, 1.0\}$ and $\alpha \in \{0.3, 0.5, 0.7\}$ to find Pareto-optimal trade-off between output and algorithmic fairness.

### 3.5 Phase 3: Comparative Evaluation

**Objective**: Validate that algorithm-aware RLHF improves algorithmic fairness without sacrificing output fairness.

**Experimental Design**: Randomized A/B testing with within-subjects comparisons.

**Conditions**:
- **Condition A (Baseline)**: Standard MaxMin-RLHF (output-level only)
- **Condition B (Treatment)**: Algorithm-aware RLHF (with $R_{\text{alg}}$ term)

**Evaluation Metrics**:

**Primary Metrics (Algorithmic Fairness)**:

1. **Algorithm Usage Parity**: KL divergence between group-specific and population-wide algorithm distributions
   $$\text{KL-Parity} = \frac{1}{|\mathcal{G}|} \sum_{g \in \mathcal{G}} D_{\text{KL}}(\mathbb{P}(a|g) || \mathbb{P}(a))$$
   Target: KL-Parity < 0.1 (low disparity)

2. **Proportional Veto Satisfaction**: Percentage of group-algorithm pairs satisfying veto constraint
   $$\text{Veto-Sat} = \frac{1}{|\mathcal{G}| \cdot |\mathcal{A}|} \sum_{g, a} \mathbb{I}[\mathbb{P}(a|g) \geq \tau \cdot \mathbb{P}(a)]$$
   Target: Veto-Sat > 0.90 (90% satisfaction)

**Secondary Metrics (Output Fairness - Must Maintain)**:

3. **Demographic Parity**: Difference in positive prediction rates
   $$\text{DP-Gap} = \max_{g, g'} |\mathbb{P}(\hat{y}=1|g) - \mathbb{P}(\hat{y}=1|g')|$$
   Target: DP-Gap < 0.05

4. **Equalized Odds**: Maximum TPR/FPR disparity
   $$\text{EO-Gap} = \max_{g, g'} \max\{|\text{TPR}_g - \text{TPR}_{g'}|, |\text{FPR}_g - \text{FPR}_{g'}|\}$$
   Target: EO-Gap < 0.05

**Tertiary Metrics (User Experience)**:

5. **User Satisfaction**: Survey-based satisfaction scores across groups (7-point Likert scale)
   Target: No group < 70% satisfaction (scores ≥5/7)

**Statistical Testing**:

1. **Algorithmic Fairness Improvement**:
   - **Test**: Paired t-test comparing KL-Parity and Veto-Sat between conditions
   - **Hypothesis**: $H_1: \mu_{\text{Treatment}} - \mu_{\text{Baseline}} \geq 0.3$ (30% improvement)
   - **Significance**: $p < 0.05$, one-tailed

2. **Output Fairness Maintenance**:
   - **Test**: Two One-Sided Tests (TOST) for equivalence
   - **Equivalence margin**: $\Delta = 0.05$ (5% regression acceptable)
   - **Hypothesis**: $H_0: |\mu_{\text{Treatment}} - \mu_{\text{Baseline}}| < \Delta$
   - **Significance**: $p < 0.05$

3. **Sample Size**: N=1,000 ICL tasks per condition, stratified across 4 demographic groups (250 tasks per group)
   - **Power**: 90% to detect 30% improvement in algorithmic fairness at $\alpha = 0.05$

**Confound Controls**:
- Randomize task order to control for learning effects
- Stratify by task difficulty (context length, noise level)
- Blind human raters to condition for satisfaction surveys
- Use identical base model architecture across conditions
- Control for prompt engineering effects via standardized templates

### 3.6 Falsification Criteria

The hypothesis will be considered **falsified** if any of the following occur:

1. **Phase 1A Failure**: No statistically significant algorithmic preference diversity across groups ($p > 0.05$ in ANOVA) → Framework unnecessary

2. **Phase 1B Failure**: Algorithm detection accuracy < 60% → Cannot reliably measure algorithmic fairness

3. **Phase 3 Failure (No Unfairness)**: Baseline MaxMin-RLHF shows no algorithmic unfairness violations ($p > 0.05$) → Output fairness is sufficient

4. **Phase 3 Failure (Unacceptable Trade-off)**: Algorithm-aware RLHF causes >10% output fairness regression → Trade-off unacceptable for deployment

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome**: We expect to demonstrate that algorithmic process fairness is an independent and measurable dimension of RLHF alignment, distinct from output-level fairness.

**Quantitative Predictions**:

1. **Algorithmic Preference Diversity** (Phase 1A): At least one demographic group will show statistically significant differences in algorithmic preferences ($p < 0.05$, Cohen's $d \geq 0.5$), with effect sizes suggesting 20-40% preference variation across groups.

2. **Algorithm Detection Feasibility** (Phase 1B): Probing classifiers will achieve >75% accuracy in detecting ICL algorithms at GPT-2 scale, with balanced performance across algorithm types (F1 > 0.70 for each class).

3. **Hidden Unfairness Exists** (Phase 3): Standard MaxMin-RLHF will exhibit algorithmic unfairness violations (KL-Parity > 0.15, Veto-Sat < 0.70) even when output fairness metrics are satisfied (DP-Gap < 0.05, EO-Gap < 0.05), confirming the measurement gap.

4. **Algorithm-Aware RLHF Improves Fairness** (Phase 3): Our framework will reduce algorithmic unfairness by ≥30% (KL-Parity reduction from ~0.15 to <0.10, Veto-Sat improvement from ~0.70 to >0.90) while maintaining output fairness (DP-Gap and EO-Gap regression <5%).

5. **User Satisfaction**: No demographic group will report satisfaction below 70%, with algorithm-aware RLHF showing 10-15% higher satisfaction among groups whose algorithmic preferences were previously penalized.

**Qualitative Outcomes**:

- **Theoretical Framework**: A formal decomposition of RLHF fairness into output and algorithmic dimensions, with mathematical definitions and social choice axioms.

- **Methodological Toolkit**: Open-source implementation of algorithm detection probes, algorithmic fairness metrics, and algorithm-aware RLHF training code.

- **Empirical Evidence**: Comprehensive dataset documenting algorithmic preference diversity across demographic groups, serving as a resource for future fairness research.

### 4.2 Theoretical Impact

This research fundamentally challenges the prevailing paradigm in RLHF fairness by establishing that **output-level metrics are incomplete**. Our work provides:

1. **New Fairness Taxonomy**: A formal decomposition of fairness into:
   - **Output Fairness**: Distribution parity of predictions/outcomes
   - **Algorithmic Fairness**: Process parity in reasoning styles and algorithm selection
   - **Interaction Effects**: How output and algorithmic fairness trade off or reinforce each other

2. **Bridge Across Communities**: First work connecting in-context learning theory (Bai et al., 2023), RLHF fairness (Chakraborty et al., 2024), and social choice theory (Ramseyer & Goel, 2023; Kondratev & Ianovski, 2024), creating a unified framework.

3. **Mechanistic Interpretability for Fairness**: Demonstrates how mechanistic interpretability techniques (probing classifiers, activation analysis) can operationalize abstract fairness concepts, opening new research directions.

4. **Axiomatic Fairness Design**: Applies social choice axioms (non-dictatorship, proportional veto) to LLM alignment, providing a principled alternative to ad-hoc fairness constraints.

### 4.3 Practical Impact

**High-Stakes Domain Applications**:

1. **Healthcare AI**: Ensures medical AI systems respect diverse cultural approaches to treatment (conservative vs. aggressive), preventing algorithmic discrimination in care recommendations. Expected impact: 20-30% improvement in patient trust across demographic groups.

2. **Financial AI**: Protects diverse risk preferences in automated financial advice, ensuring both risk-averse and risk-seeking clients receive algorithmically fair recommendations. Expected impact: Reduced algorithmic bias complaints by 40%.

3. **Educational AI**: Respects diverse learning styles (hedging/exploratory vs. decisive/focused), ensuring personalized education systems don't systematically disadvantage certain cognitive approaches. Expected impact: 15-25% improvement in engagement among previously underserved groups.

**Industry Adoption**:

- **Deployment Guidelines**: Practical recommendations for practitioners implementing RLHF, including when algorithmic fairness matters (high-stakes, transparency-critical domains) and when output fairness suffices (pure prediction tasks).

- **Auditing Tools**: Open-source toolkit for detecting and measuring algorithmic unfairness in deployed LLMs, enabling continuous fairness monitoring.

- **Computational Trade-offs**: Benchmarking data on the computational overhead of algorithm-aware RLHF (expected: 15-25% increase in training time), helping organizations make informed deployment decisions.

### 4.4 Policy and Regulatory Impact

As AI regulation evolves globally, this research provides:

1. **Expanded Fairness Auditing**: Evidence that output-only fairness audits (currently standard in regulatory proposals) are insufficient. Algorithmic process fairness offers a new dimension for compliance frameworks.

2. **Transparency Requirements**: Supports arguments for algorithmic transparency in high-stakes AI systems (EU AI Act, US Executive Order on AI), demonstrating that "how" AI reasons matters, not just "what" it outputs.

3. **Standardization**: Proposed metrics (KL-Parity, Veto-Sat) can inform development of fairness standards (e.g., IEEE, NIST AI Risk Management Framework).

### 4.5 Limitations and Future Directions

**Known Limitations**:

1. **Computational Overhead**: Algorithm detection adds 15-25% training time, potentially limiting adoption in resource-constrained settings.

2. **Demographic Label Dependency**: Requires demographic labels, raising privacy concerns and risks of reinforcing stereotypes if misused.

3. **Generalization Uncertainty**: Bai et al.'s ICL theory proved for specific architectures; generalization to GPT-4/LLaMA-3 scale requires empirical validation.

4. **Context Specificity**: Algorithmic preferences may vary across task domains; cross-domain stability needs investigation.

**Future Research Directions**:

1. **Scaling Studies**: Validate framework on production-scale LLMs (70B+ parameters) and diverse architectures (state-space models, mixture-of-experts).

2. **Dynamic Fairness**: Investigate how algorithmic fairness evolves during deployment and develop adaptive monitoring systems.

3. **Intersectional Fairness**: Extend framework to handle intersectional identities (e.g., age × gender × ethnicity) and their algorithmic preferences.

4. **Preference Elicitation**: Develop implicit methods for inferring algorithmic preferences without explicit surveys, reducing participant burden.

5. **Multi-Objective Optimization**: Explore Pareto-optimal frontiers balancing output fairness, algorithmic fairness, model performance, and computational efficiency.

### 4.6 Broader Impact Statement

This research advances responsible AI by ensuring that foundation models respect not only what diverse groups prefer (output fairness) but also how they reason (algorithmic fairness). By making algorithmic process fairness measurable and optimizable, we provide tools for building AI systems that are equitable at both outcome and process levels—a critical requirement for trustworthy deployment in high-stakes domains.

However, we acknowledge potential risks: demographic labeling could reinforce stereotypes if misapplied, and increased model complexity may create new opacity. We commit to open-sourcing our methods, engaging with affected communities in preference elicitation, and providing clear guidance on when algorithmic fairness interventions are appropriate versus when they risk over-engineering. Our goal is not to impose a single fairness framework, but to expand the toolkit available to practitioners and policymakers navigating the complex landscape of responsible AI alignment.