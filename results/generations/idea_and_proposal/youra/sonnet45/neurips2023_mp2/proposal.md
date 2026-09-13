# Research Proposal: Voting-Theoretic RLHF for Pluralistic AI Alignment

## 1. Title

**Voting-Theoretic RLHF: Pluralistic AI Alignment Through Fairness-Constrained Social Choice Aggregation**

## 2. Introduction

### 2.1 Background

The rapid deployment of large language models (LLMs) in society has raised critical questions about whose values these systems represent. Current Reinforcement Learning from Human Feedback (RLHF) approaches, while effective at improving model performance on aggregate metrics, suffer from a fundamental limitation: they implicitly employ majority-voting mechanisms that systematically marginalize minority moral perspectives. Recent empirical studies demonstrate that minority viewpoints achieve representation scores below 0.3 in standard RLHF systems, meaning that 70% or more of their preferences are overridden by majority consensus.

This problem is not merely technical but deeply philosophical. Moral philosophy has long grappled with questions of value pluralism—the recognition that multiple, sometimes incompatible moral frameworks can be simultaneously valid. From Isaiah Berlin's value pluralism to contemporary work in political philosophy on democratic representation, scholars have developed sophisticated theories for respecting diverse perspectives in collective decision-making. Similarly, moral psychology research demonstrates that individuals differ systematically in their moral foundations (care, fairness, loyalty, authority, sanctity), and that these differences reflect genuine variation in moral reasoning rather than error or ignorance.

Yet current AI alignment practices largely ignore this rich theoretical foundation. Standard RLHF aggregates human feedback through simple averaging or Bradley-Terry models that effectively implement majority rule, with no formal guarantees against minority exclusion and no interpretable mechanisms for understanding which values are embedded in the resulting systems. This creates AI systems that amplify dominant voices rather than reflecting society's genuinely pluralistic values—a critical failure mode as these systems increasingly mediate important social decisions.

Social choice theory, a branch of economics and political science, offers powerful formal tools for aggregating preferences while respecting diverse viewpoints. Voting rules such as Borda count, Copeland's method, and Maximal Lottery have well-understood axiomatic properties and fairness guarantees. Meanwhile, recent work in participatory budgeting has developed fairness constraints—Individual Fairness Share (IFS) and Group Fairness Share (GFS)—that provide formal guarantees against systematic marginalization. These tools have never been systematically applied to AI alignment.

### 2.2 Research Objectives

This research aims to develop and validate a novel framework for pluralistic AI alignment that:

1. **Replaces implicit majority aggregation** in RLHF with explicit, differentiable voting rules from social choice theory (Borda, Copeland, Kemeny, Maximal Lottery)

2. **Incorporates formal fairness constraints** (IFS, GFS) from participatory budgeting to guarantee each perspective receives ≥1/n influence, preventing systematic marginalization

3. **Enables interpretable value representation** through membership vectors that reveal annotators' positions in moral dimension space

4. **Implements context-adaptive voting rule selection** that varies by moral dilemma characteristics (e.g., Copeland for high-stakes decisions, Maximal Lottery for value-diverse scenarios)

5. **Provides formal theoretical guarantees** connecting social choice axioms to pluralistic alignment properties

6. **Demonstrates practical viability** through empirical validation on established benchmarks with acceptable performance trade-offs

### 2.3 Significance

This research addresses a critical gap at the intersection of moral philosophy, moral psychology, and AI alignment. Its significance spans multiple dimensions:

**Theoretical Contribution**: This work establishes the first formal connection between social choice axioms and AI pluralistic alignment guarantees, providing a rigorous foundation for reasoning about value representation in AI systems.

**Methodological Innovation**: By systematically combining voting theory, fairness constraints, and interpretable personalization, this framework offers a principled alternative to ad-hoc approaches for incorporating diverse values.

**Practical Impact**: The framework enables verifiable representation of minority perspectives in deployed AI systems, with direct implications for fairness in AI-mediated decisions affecting diverse populations.

**Cross-Disciplinary Bridge**: This work demonstrates how theories from moral philosophy (value pluralism) and moral psychology (moral foundations theory) can directly inform AI system design, exemplifying the productive integration the workshop seeks to promote.

**Democratic AI Governance**: By making value trade-offs explicit and interpretable, the framework supports more democratic oversight of AI systems, enabling stakeholders to understand and contest the values embedded in these systems.

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Voting-Theoretic Reward Aggregation

Let $\mathcal{A} = \{a_1, ..., a_n\}$ denote a set of $n$ human annotators, each representing a distinct moral perspective. For a given prompt-response pair $(x, y)$, each annotator $a_i$ provides a preference ranking or rating $r_i(x, y)$.

We formalize four voting rules as differentiable aggregation functions:

**Borda Count** (baseline majority rule):
$$R_{\text{Borda}}(x, y) = \frac{1}{n} \sum_{i=1}^{n} r_i(x, y)$$

**Copeland's Method** (pairwise majority comparisons):
$$R_{\text{Copeland}}(x, y) = \sum_{(x', y') \in \mathcal{C}} \mathbb{1}\left[\sum_{i=1}^{n} \text{sgn}(r_i(x,y) - r_i(x',y')) > 0\right]$$

where $\mathcal{C}$ is the set of competing responses.

**Maximal Lottery** (probabilistic fairness):
$$R_{\text{ML}}(x, y) = \max_{p \in \Delta(\mathcal{Y})} \min_{i \in [n]} \mathbb{E}_{y' \sim p}[r_i(x, y') \mid y' = y]$$

where $\Delta(\mathcal{Y})$ is the probability simplex over responses.

**Kemeny-Young** (optimal consensus ranking):
$$R_{\text{Kemeny}}(x, y) = \arg\max_{\sigma} \sum_{i=1}^{n} K(\sigma, \pi_i)$$

where $K(\sigma, \pi_i)$ is the Kendall tau distance between consensus ranking $\sigma$ and individual ranking $\pi_i$.

#### 3.1.2 Fairness Constraints

We adapt Individual Fairness Share (IFS) and Group Fairness Share (GFS) from participatory budgeting:

**Individual Fairness Share (IFS)**:
$$\forall i \in [n]: \quad \frac{1}{|\mathcal{D}|} \sum_{(x,y) \in \mathcal{D}} w_i(x, y) \geq \frac{1}{n} - \epsilon_{\text{IFS}}$$

where $w_i(x, y)$ is the influence weight of annotator $i$ on the final reward for $(x, y)$, and $\epsilon_{\text{IFS}}$ is a small tolerance parameter.

**Group Fairness Share (GFS)**:
For any group $G \subseteq \mathcal{A}$ with $|G| = k$:
$$\frac{1}{|\mathcal{D}|} \sum_{(x,y) \in \mathcal{D}} \max_{i \in G} w_i(x, y) \geq \frac{k}{n} - \epsilon_{\text{GFS}}$$

#### 3.1.3 Interpretable Membership Vectors

We model each annotator $a_i$ as a point in a $d$-dimensional moral space:
$$\mathbf{m}_i \in \mathbb{R}^d, \quad \|\mathbf{m}_i\|_2 = 1$$

These membership vectors are learned jointly with the reward model through:
$$\mathcal{L}_{\text{membership}} = \sum_{i=1}^{n} \sum_{(x,y) \in \mathcal{D}_i} \left(r_i(x,y) - \mathbf{m}_i^\top \phi(x, y)\right)^2$$

where $\phi(x, y)$ is a learned feature representation of the prompt-response pair.

#### 3.1.4 Context-Adaptive Voting Rule Selection

We define a context function $c(x)$ that maps prompts to voting rules:
$$c(x) = \arg\max_{v \in \mathcal{V}} \psi_v^\top \theta(x)$$

where $\mathcal{V} = \{\text{Borda, Copeland, ML, Kemeny}\}$, $\theta(x)$ encodes prompt characteristics (stakes, value diversity, consensus level), and $\psi_v$ are learned rule-selection parameters.

### 3.2 Algorithm Design

#### 3.2.1 Training Procedure

**Algorithm 1: Fairness-Constrained Voting-Theoretic RLHF**

```
Input: Dataset D, annotators A, fairness parameters ε_IFS, ε_GFS, λ
Output: Reward model R_θ, membership vectors {m_i}, context selector c

1. Initialize:
   - Reward model R_θ with pretrained LLM
   - Membership vectors {m_i} ~ N(0, I/d)
   - Context selector parameters ψ

2. For each epoch:
   a. Sample batch B from D
   
   b. For each (x, y) in B:
      - Compute voting rule: v* = c(x)
      - Aggregate rewards: r_agg = R_v*(x, y | {r_i}, {m_i})
      - Compute influence weights: {w_i(x,y)}
   
   c. Compute losses:
      - Alignment loss: L_align = -E[r_agg]
      - IFS violation: L_IFS = Σ_i max(0, 1/n - ε_IFS - w̄_i)
      - GFS violation: L_GFS = Σ_G max(0, |G|/n - ε_GFS - w̄_G)
      - Membership loss: L_mem (as defined above)
   
   d. Combined objective:
      L_total = L_align + λ_IFS·L_IFS + λ_GFS·L_GFS + λ_mem·L_mem
   
   e. Update θ, {m_i}, ψ via gradient descent

3. Return R_θ, {m_i}, c
```

#### 3.2.2 Differentiable Voting Rule Implementation

For gradient-based optimization, we use smooth approximations:

**Soft Copeland**:
$$R_{\text{Copeland}}^{\text{soft}}(x, y) = \sum_{(x', y')} \sigma\left(\tau \sum_{i=1}^{n} (r_i(x,y) - r_i(x',y'))\right)$$

where $\sigma$ is the sigmoid function and $\tau$ is a temperature parameter.

**Differentiable Maximal Lottery**:
Implemented via entropic regularization:
$$R_{\text{ML}}^{\text{soft}}(x, y) = \max_{p} \min_{i} \mathbb{E}_{p}[r_i] + \beta H(p)$$

where $H(p)$ is entropy and $\beta$ controls smoothness.

### 3.3 Data Collection

#### 3.3.1 Primary Dataset: PERSONA Benchmark

We utilize the PERSONA benchmark, which contains:
- 1,500 moral dilemmas across 6 categories (healthcare, justice, privacy, environment, education, technology)
- Annotations from 300 diverse annotators with documented demographic and ideological profiles
- Multiple response options per dilemma (typically 4-6)
- Rich metadata including dilemma stakes, value conflicts, and consensus levels

#### 3.3.2 Annotator Profiling

For each annotator, we collect:
- Moral Foundations Questionnaire (MFQ) scores across 5 dimensions
- Political orientation (7-point scale)
- Demographic information (age, gender, education, location)
- Domain expertise indicators

This enables validation of learned membership vectors against ground-truth moral profiles.

#### 3.3.3 Synthetic Augmentation

To test edge cases and controlled scenarios, we generate synthetic annotator populations:
- **Polarized**: Two distinct clusters with opposing preferences
- **Uniform**: Evenly distributed across moral space
- **Minority-heavy**: 80% majority, 20% coherent minority
- **Multi-modal**: 3-5 distinct moral communities

### 3.4 Experimental Design

#### 3.4.1 Baseline Comparisons

**Primary Baselines**:
1. **Standard RLHF**: Borda count aggregation only
2. **Distributional RLHF**: Uniform weights across annotators
3. **Constitutional AI**: Principle-based constraints without voting
4. **Separate Models**: Oracle upper bound (one model per persona)

**Ablation Studies**:
- Voting rules only (no fairness constraints)
- Fairness constraints only (Borda aggregation)
- Fixed voting rule (no context adaptation)
- No membership vectors (black-box aggregation)

#### 3.4.2 Evaluation Metrics

**Minority Representation Score (MRS)**:
$$\text{MRS} = \frac{1}{|\mathcal{M}|} \sum_{i \in \mathcal{M}} \frac{\sum_{(x,y)} \mathbb{1}[r_i(x, y^*) > \text{median}(r_i)]}{|\mathcal{D}|}$$

where $\mathcal{M}$ is the set of minority annotators (bottom 30% by agreement with majority).

**Individual Fairness Share Satisfaction**:
$$\text{IFS-Sat} = \frac{|\{i : w̄_i \geq 1/n - \epsilon\}|}{n}$$

**Group Fairness Share Satisfaction**:
$$\text{GFS-Sat} = \frac{|\{G : w̄_G \geq |G|/n - \epsilon\}|}{|\mathcal{G}|}$$

where $\mathcal{G}$ is the set of all possible groups.

**Distributional Calibration Error**:
$$\text{DCE} = \mathbb{E}_{(x,y)} \left[\text{KL}\left(P_{\text{human}}(r|x,y) \| P_{\text{model}}(r|x,y)\right)\right]$$

**Alignment Tax**:
$$\text{Tax} = \frac{\text{Performance}_{\text{baseline}} - \text{Performance}_{\text{ours}}}{\text{Performance}_{\text{baseline}}}$$

measured on standard benchmarks (MMLU, TruthfulQA, HHH).

**Interpretability Accuracy**:
Correlation between learned membership vectors $\mathbf{m}_i$ and ground-truth MFQ profiles.

#### 3.4.3 Experimental Conditions

**Experiment 1: Voting Rule Comparison**
- **Hypothesis**: Maximal Lottery achieves MRS > 0.5 vs. Borda's < 0.3
- **Design**: Train 4 models (one per voting rule) on PERSONA
- **Analysis**: Compare MRS, IFS-Sat, alignment tax across rules

**Experiment 2: Fairness Constraint Impact**
- **Hypothesis**: IFS/GFS constraints prevent systematic marginalization
- **Design**: Vary $\lambda_{\text{IFS}}, \lambda_{\text{GFS}} \in \{0, 0.1, 0.5, 1.0\}$
- **Analysis**: Measure IFS-Sat vs. alignment tax trade-off curve

**Experiment 3: Context-Adaptive Selection**
- **Hypothesis**: Adaptive selection outperforms fixed rules
- **Design**: Compare adaptive vs. 4 fixed-rule baselines
- **Analysis**: Stratify performance by dilemma characteristics

**Experiment 4: Interpretability Validation**
- **Hypothesis**: Membership vectors predict annotator profiles with >70% accuracy
- **Design**: Train linear classifiers from $\mathbf{m}_i$ to MFQ scores
- **Analysis**: Correlation, classification accuracy, qualitative inspection

**Experiment 5: Robustness Testing**
- **Hypothesis**: Copeland improves alignment with Condorcet winners by 20%
- **Design**: Identify dilemmas with Condorcet winners, measure agreement
- **Analysis**: Copeland vs. Borda on Condorcet-consistent scenarios

#### 3.4.4 Statistical Analysis Plan

- **Sample size**: 1,500 dilemmas × 300 annotators = 450,000 data points
- **Significance testing**: Paired t-tests for metric comparisons (α = 0.05)
- **Multiple comparison correction**: Bonferroni correction for 5 primary hypotheses
- **Effect size**: Cohen's d for MRS improvements
- **Confidence intervals**: Bootstrap 95% CIs for all reported metrics

### 3.5 Implementation Details

**Software Stack**:
- PyTorch for model training
- Transformers library (HuggingFace) for LLM backbone
- Custom voting rule implementations with autograd support
- Weights & Biases for experiment tracking

**Computational Resources**:
- 4× NVIDIA A100 GPUs for model training
- Estimated 200 GPU-hours per full experimental run
- Total budget: ~2,000 GPU-hours for all experiments

**Reproducibility**:
- All code released under MIT license on GitHub
- Docker containers with frozen dependencies
- Random seeds fixed and documented
- Hyperparameter configurations version-controlled

**Interpretability Dashboard**:
Web-based interface displaying:
- Learned membership vectors in 2D (t-SNE projection)
- Per-dilemma voting rule selections with explanations
- Influence weight distributions across annotators
- Fairness constraint satisfaction over training

## 4. Expected Outcomes & Impact

### 4.1 Quantitative Outcomes

Based on our theoretical analysis and preliminary experiments, we predict:

1. **Minority Representation**: MRS > 0.5 for Maximal Lottery (vs. < 0.3 for standard RLHF), representing a 67% improvement in minority perspective inclusion

2. **Fairness Guarantees**: IFS-Sat > 90% and GFS-Sat > 85%, demonstrating near-universal satisfaction of fairness constraints

3. **Acceptable Trade-offs**: Alignment tax < 10% on standard benchmarks, showing that pluralistic alignment need not sacrifice overall performance

4. **Interpretability**: Correlation > 0.7 between learned membership vectors and ground-truth MFQ profiles, enabling meaningful interpretation of value dimensions

5. **Context Sensitivity**: Adaptive voting rule selection improves MRS by 15-20% over best fixed rule, demonstrating value of context-awareness

### 4.2 Theoretical Contributions

**Formal Guarantees**: We will establish theorems connecting social choice axioms (e.g., Condorcet consistency, participation, monotonicity) to pluralistic alignment properties (minority representation, fairness share satisfaction).

**Impossibility Results**: Following Arrow's theorem tradition, we will characterize fundamental trade-offs between different fairness criteria in the AI alignment context.

**Complexity Analysis**: We will provide computational complexity bounds for voting rule optimization under fairness constraints.

### 4.3 Methodological Innovations

**Differentiable Social Choice**: First implementation of classical voting rules as differentiable loss functions suitable for gradient-based optimization.

**Fairness-Constrained RLHF**: Novel training framework combining reward learning with explicit fairness guarantees.

**Interpretable Value Representation**: Systematic approach to learning and visualizing moral dimensions from preference data.

### 4.4 Practical Impact

**Deployment-Ready Framework**: Open-source library enabling practitioners to implement voting-theoretic RLHF with minimal code changes.

**Policy Implications**: Concrete methodology for AI developers to demonstrate compliance with emerging fairness regulations.

**Democratic Oversight**: Interpretability dashboard enables stakeholders to audit value representation in deployed systems.

### 4.5 Cross-Disciplinary Contributions

**To Moral Philosophy**: Empirical validation of value pluralism theories in AI systems; new insights into practical implementation of pluralistic ethics.

**To Moral Psychology**: Novel measurement approach for moral dimensions through revealed preferences in AI feedback; validation of moral foundations theory in AI context.

**To Social Choice Theory**: Extension of classical voting theory to continuous, high-dimensional preference spaces; new fairness axioms for AI alignment.

**To AI Safety**: Formal framework for reasoning about value alignment in pluralistic societies; concrete alternative to monolithic alignment approaches.

### 4.6 Limitations and Future Work

**Known Limitations**:
- Computational overhead of complex voting rules (addressed through approximations)
- Assumption of fixed annotator populations (future work: dynamic populations)
- Focus on text-based moral dilemmas (extension to multimodal scenarios needed)

**Future Directions**:
- Extension to multi-agent systems with strategic voting
- Integration with constitutional AI for hybrid approaches
- Application to specific domains (healthcare AI, judicial AI, educational AI)
- Longitudinal studies of value drift in deployed systems
- Cross-cultural validation beyond Western moral frameworks

### 4.7 Timeline and Milestones

**Months 1-2**: Theoretical framework development, algorithm implementation
**Months 3-4**: Baseline experiments, voting rule comparisons
**Months 5-6**: Fairness constraint experiments, interpretability validation
**Months 7-8**: Context-adaptive selection, robustness testing
**Months 9-10**: Dashboard development, documentation
**Months 11-12**: Paper writing, open-source release

### 4.8 Broader Impact Statement

This research directly addresses one of the most pressing challenges in AI ethics: ensuring that AI systems represent the values of diverse populations rather than amplifying dominant voices. By providing formal guarantees against minority marginalization and interpretable mechanisms for understanding embedded values, this work contributes to more democratic and equitable AI governance.

The framework is particularly relevant for AI systems deployed in pluralistic societies where moral disagreement is legitimate and expected. Rather than seeking false consensus or imposing majority preferences, our approach embraces value pluralism as a feature rather than a bug, enabling AI systems that respect genuine moral diversity.

By bridging moral philosophy, moral psychology, and machine learning, this research exemplifies the productive cross-disciplinary collaboration necessary for developing truly ethical AI systems—precisely the goal of this workshop.