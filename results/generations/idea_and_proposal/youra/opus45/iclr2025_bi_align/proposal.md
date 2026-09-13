# Research Proposal: Bidirectional Alignment Quality Index (BAQI)

## 1. Title

**BAQI: A Multi-Objective Framework for Measuring Bidirectional Human-AI Alignment Through Integrated Assessment of AI Quality, Human Agency, and Co-adaptation Dynamics**

---

## 2. Introduction

### 2.1 Background

The rapid proliferation of general-purpose AI systems, particularly large language models (LLMs), has fundamentally transformed human-computer interaction paradigms. These systems now serve as conversational assistants, decision-support tools, and collaborative partners across domains ranging from healthcare to creative writing. As AI assumes increasingly complex decision-making roles, the challenge of alignment—ensuring AI systems behave in accordance with human values, preferences, and goals—has emerged as one of the most critical research frontiers in artificial intelligence.

Traditional approaches to AI alignment have predominantly adopted a unidirectional perspective, focusing on shaping AI behavior to match human specifications. Reinforcement Learning from Human Feedback (RLHF) exemplifies this paradigm, where human preference data trains reward models that subsequently guide AI optimization. While RLHF has achieved remarkable success—producing models preferred by humans over 70% of the time in comparative evaluations—this approach systematically neglects a crucial dimension: the preservation of human agency within human-AI interactions.

Recent empirical findings from the HumanAgencyBench benchmark have exposed a critical gap in current alignment evaluation: "agency support does not appear to consistently result from RLHF." This revelation suggests that high-performing AI systems, as measured by traditional alignment metrics, may inadvertently disempower users over time by fostering over-reliance, reducing critical thinking, or undermining autonomous decision-making capabilities. The implications are profound: optimizing solely for user preference satisfaction may produce AI systems that users enjoy interacting with but that ultimately diminish their cognitive autonomy and self-efficacy.

This tension reflects a broader conceptual limitation in how the field has approached alignment. The bidirectional human-AI alignment framework, derived from systematic analysis of over 400 interdisciplinary papers, reconceptualizes alignment as a dynamic, evolving process involving two complementary directions: (1) aligning AI with humans through training, steering, and monitoring; and (2) aligning humans with AI by preserving agency and empowering critical evaluation. Current evaluation methodologies, however, lack frameworks capable of capturing this bidirectional nature.

### 2.2 Research Objectives

This research proposes the Bidirectional Alignment Quality Index (BAQI), a novel multi-objective evaluation framework designed to address the limitations of unidirectional alignment metrics. The primary objectives are:

1. **Develop a composite evaluation framework** integrating three complementary components: AI Alignment Score (AAS) capturing traditional alignment quality, Human Agency Score (HAS) measuring autonomy support across multiple dimensions, and Co-adaptation Trajectory (CAT) tracking agency dynamics over extended interactions.

2. **Validate the framework's predictive superiority** by demonstrating that BAQI achieves significantly stronger correlation with long-term user satisfaction and autonomy preservation than unidirectional metrics alone.

3. **Establish Pareto multi-objective optimization** as the integration mechanism, enabling identification of configurations that excel on both AI quality AND human empowerment without forcing artificial trade-offs.

4. **Provide actionable insights** for AI system designers seeking to balance performance optimization with agency preservation.

### 2.3 Research Significance

This research addresses a fundamental gap in AI alignment evaluation with significant theoretical and practical implications. Theoretically, BAQI operationalizes the bidirectional alignment framework, providing the first quantitative methodology for measuring both directions simultaneously. Practically, the framework offers AI developers concrete metrics for assessing whether their systems support or undermine human agency—a consideration increasingly relevant as AI assistants become embedded in high-stakes decision-making contexts.

The core hypothesis driving this research states: Under multi-turn human-AI dialogue interactions (10-50 turns), the BAQI framework integrating AAS, HAS, and CAT via Pareto optimization will achieve stronger correlation ($r > 0.6$) with long-term user satisfaction than unidirectional RLHF metrics ($r \leq 0.4$), because bidirectional measurement captures agency preservation dynamics that single-metric approaches systematically miss.

---

## 3. Methodology

### 3.1 Framework Architecture

The BAQI framework comprises three integrated components, each capturing distinct aspects of bidirectional alignment:

#### 3.1.1 AI Alignment Score (AAS)

The AI Alignment Score quantifies traditional alignment quality using normalized reward model outputs from RLHF-trained systems. For a given AI response $r$ to user input $u$ in context $c$, the AAS is computed as:

$$AAS(r|u,c) = \sigma\left(\frac{R_\theta(r|u,c) - \mu_R}{\sigma_R}\right)$$

where $R_\theta$ represents the reward model with parameters $\theta$, $\mu_R$ and $\sigma_R$ are the mean and standard deviation of reward scores across a calibration dataset, and $\sigma(\cdot)$ is the sigmoid function ensuring outputs in $[0,1]$. For multi-turn interactions with $T$ turns, the aggregate AAS is:

$$AAS_{total} = \frac{1}{T}\sum_{t=1}^{T} AAS(r_t|u_t,c_t)$$

#### 3.1.2 Human Agency Score (HAS)

The Human Agency Score measures autonomy support across six dimensions derived from the HumanAgencyBench framework: (1) Information Provision, (2) Option Generation, (3) Reasoning Transparency, (4) User Autonomy Acknowledgment, (5) Critical Thinking Encouragement, and (6) Appropriate Deference. Each dimension $d_i$ is evaluated using an LLM-as-judge approach:

$$HAS_{d_i}(r|u,c) = \text{LLM-Judge}(r, u, c, \text{rubric}_{d_i})$$

where the LLM-Judge function returns a score in $[0,1]$ based on dimension-specific evaluation rubrics. The composite HAS for a single turn is:

$$HAS(r|u,c) = \frac{1}{6}\sum_{i=1}^{6} HAS_{d_i}(r|u,c)$$

For multi-turn interactions:

$$HAS_{total} = \frac{1}{T}\sum_{t=1}^{T} HAS(r_t|u_t,c_t)$$

#### 3.1.3 Co-adaptation Trajectory (CAT)

The Co-adaptation Trajectory captures the temporal dynamics of agency support across extended interactions. CAT comprises two sub-metrics:

**Trajectory Slope ($\beta_{CAT}$):** The linear regression coefficient of HAS scores over turns:

$$\beta_{CAT} = \frac{\sum_{t=1}^{T}(t - \bar{t})(HAS_t - \overline{HAS})}{\sum_{t=1}^{T}(t - \bar{t})^2}$$

A positive slope indicates improving agency support; negative slope suggests declining support over time.

**Trajectory Variance ($\sigma^2_{CAT}$):** The variance of HAS scores around the regression line:

$$\sigma^2_{CAT} = \frac{1}{T-2}\sum_{t=1}^{T}(HAS_t - \hat{HAS}_t)^2$$

where $\hat{HAS}_t = \alpha + \beta_{CAT} \cdot t$ is the predicted HAS at turn $t$.

The composite CAT score normalizes these components:

$$CAT = \frac{1}{2}\left[\sigma(\beta_{CAT} \cdot k) + (1 - \min(\sigma^2_{CAT}/\sigma^2_{max}, 1))\right]$$

where $k$ is a scaling constant and $\sigma^2_{max}$ is the maximum acceptable variance.

#### 3.1.4 Pareto Multi-Objective Integration

Rather than combining AAS, HAS, and CAT through weighted averaging—which would impose arbitrary trade-off assumptions—BAQI employs Pareto multi-objective optimization. A configuration $\mathbf{x}_i = (AAS_i, HAS_i, CAT_i)$ Pareto-dominates $\mathbf{x}_j$ if:

$$\forall m \in \{AAS, HAS, CAT\}: x_i^m \geq x_j^m \quad \land \quad \exists m: x_i^m > x_j^m$$

The Pareto frontier $\mathcal{P}$ contains all non-dominated configurations. The BAQI rank for configuration $\mathbf{x}$ is determined by iterative Pareto frontier extraction:

$$BAQI_{rank}(\mathbf{x}) = \min\{k : \mathbf{x} \in \mathcal{P}_k\}$$

where $\mathcal{P}_1$ is the primary Pareto frontier, $\mathcal{P}_2$ is the frontier after removing $\mathcal{P}_1$, and so forth.

### 3.2 Data Collection

#### 3.2.1 Dialogue Dataset Construction

We will construct a dataset of 120 multi-turn human-AI dialogues stratified across three interaction lengths:

- **Short interactions:** 40 dialogues × 10 turns
- **Medium interactions:** 40 dialogues × 25 turns  
- **Long interactions:** 40 dialogues × 50 turns

Dialogues will span four task domains: (1) information seeking, (2) decision support, (3) creative collaboration, and (4) learning assistance. Participants will interact with three different AI systems representing varying alignment approaches: a standard RLHF-optimized model, an agency-enhanced model, and a baseline instruction-tuned model.

#### 3.2.2 Ground Truth Labels

For each interaction, we collect:

1. **Long-term User Satisfaction:** 7-point Likert scale administered post-interaction
2. **Autonomy Preservation:** 9-item General Human-AI Interaction Scale (GHAIs), adapted for AI contexts, yielding scores from 9-63
3. **Behavioral Proxies:** Task completion quality, time-to-decision, and follow-up question frequency

#### 3.2.3 Participant Recruitment

We will recruit 120 participants (balanced for gender, age 18-65, and prior AI experience) through university participant pools and online platforms. Each participant completes one extended interaction session, ensuring independence of observations.

### 3.3 Experimental Design

#### 3.3.1 Validation Study Structure

The validation study follows a between-subjects design with three conditions (AI system type) × three interaction lengths, yielding 9 experimental cells with approximately 13-14 participants each.

**Phase 1: Calibration (n=20)**
- Validate LLM-as-judge reliability against human expert annotations
- Establish inter-rater reliability thresholds (target: Cohen's $\kappa > 0.7$)
- Calibrate reward model normalization parameters

**Phase 2: Main Study (n=100)**
- Collect complete BAQI metrics for all interactions
- Administer post-interaction questionnaires
- Record behavioral measures

**Phase 3: Longitudinal Follow-up (n=50 subset)**
- Re-contact participants at 2-week interval
- Assess sustained satisfaction and autonomy perceptions

#### 3.3.2 Baseline Comparisons

BAQI will be compared against four baseline metrics:

1. **RLHF-only:** $AAS_{total}$ alone
2. **HumanAgencyBench-only:** $HAS_{total}$ alone
3. **Simple Average:** $(AAS + HAS + CAT)/3$
4. **Weighted Average:** Optimally-weighted combination determined via cross-validation

### 3.4 Statistical Analysis Plan

#### 3.4.1 Primary Analysis

The primary hypothesis test compares correlations between BAQI and user satisfaction versus AAS and user satisfaction using Fisher's z-transformation for dependent correlations:

$$z = \frac{z_{r_1} - z_{r_2}}{\sqrt{\frac{1}{n-3} + \frac{1}{n-3} - \frac{2r_{12}r_{13}r_{23}}{(1-r_{12}^2)(1-r_{13}^2)}}}$$

where $r_1 = r(BAQI, Satisfaction)$, $r_2 = r(AAS, Satisfaction)$, and $r_{12}, r_{13}, r_{23}$ are intercorrelations.

**Success Criteria:**
- Primary: $r(BAQI, Satisfaction) - r(AAS, Satisfaction) \geq 0.15$ with $p < 0.05$
- Expected effect sizes: $r_{BAQI} \geq 0.6$, $r_{AAS} \leq 0.4$

#### 3.4.2 Secondary Analyses

1. **CAT-Autonomy Correlation:** Pearson correlation between $\beta_{CAT}$ and GHAIs scores
2. **Pareto Dominance Analysis:** Verification that no single-metric baseline dominates across all dimensions
3. **Moderation Analysis:** Interaction length as moderator of BAQI predictive validity

#### 3.4.3 Power Analysis

With $n = 100$, $\alpha = 0.05$ (one-tailed), and expected correlation difference of 0.20, statistical power exceeds 0.80 for detecting the hypothesized effect.

### 3.5 Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Correlation with Satisfaction | Pearson $r$ between BAQI and user satisfaction | $r > 0.6$ |
| Correlation Improvement | $\Delta r = r_{BAQI} - r_{AAS}$ | $\Delta r \geq 0.15$ |
| LLM-Judge Reliability | Cohen's $\kappa$ with human annotators | $\kappa > 0.7$ |
| CAT-Autonomy Correlation | Pearson $r$ between trajectory slope and GHAIs | $r > 0.4$ |
| Pareto Coverage | Percentage of configurations on Pareto frontier | Reported descriptively |

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome:** We anticipate demonstrating that BAQI achieves correlation with long-term user satisfaction of $r \geq 0.6$, significantly exceeding the expected $r \leq 0.4$ for RLHF reward scores alone. This 0.20+ correlation improvement would validate the hypothesis that bidirectional measurement captures predictive information missed by unidirectional approaches.

**Secondary Outcomes:**
1. Empirical characterization of the AAS-HAS relationship across different AI systems, potentially revealing whether these dimensions are orthogonal, positively correlated, or inversely related
2. Validation of LLM-as-judge methodology for automated agency assessment at scale
3. Novel insights into co-adaptation dynamics, including identification of interaction patterns associated with agency preservation versus erosion
4. Open-source release of the BAQI evaluation toolkit, including calibrated LLM-judge prompts and Pareto optimization code

### 4.2 Theoretical Impact

This research advances the theoretical understanding of human-AI alignment in several ways. First, it operationalizes the bidirectional alignment framework, transforming a conceptual model into measurable constructs. Second, it challenges the implicit assumption in current alignment research that optimizing for user preferences automatically supports user agency. Third, it introduces temporal dynamics (via CAT) as a first-class consideration in alignment evaluation, recognizing that alignment quality may evolve across extended interactions.

### 4.3 Practical Impact

For AI practitioners, BAQI provides actionable guidance for system design. Developers can use the framework to identify whether their systems occupy favorable positions on the Pareto frontier or whether improvements in one dimension come at unacceptable costs to others. The decomposed metrics (AAS, HAS, CAT) enable targeted interventions: systems with high AAS but low HAS may benefit from agency-enhancing modifications, while systems with declining CAT trajectories may require mechanisms to prevent user disempowerment over time.

### 4.4 Societal Impact

As AI systems become increasingly embedded in consequential decisions—from medical diagnosis to financial planning—ensuring these systems support rather than undermine human agency becomes a matter of societal importance. BAQI contributes to this goal by providing evaluation tools that make agency preservation measurable and optimizable. This aligns with emerging policy frameworks emphasizing human oversight and autonomy in AI-assisted decision-making.

### 4.5 Limitations and Future Directions

We acknowledge several limitations. The LLM-as-judge approach, while scalable, may introduce systematic biases that differ from human evaluation. The 10-50 turn interaction range, while capturing meaningful dynamics, may not generalize to very short or extremely extended interactions. Individual differences in agency preferences may create heterogeneity that population-level metrics obscure.

Future research directions include: (1) extending BAQI to non-conversational AI systems, (2) developing personalized agency thresholds reflecting individual user preferences, (3) investigating causal mechanisms through controlled experiments manipulating specific BAQI components, and (4) longitudinal studies tracking agency dynamics over weeks or months of AI assistant use.

---

**Word Count:** ~2,150 words