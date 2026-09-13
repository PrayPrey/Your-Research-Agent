# Research Proposal: Moral Curriculum Learning: Kohlberg-Inspired Progressive Training for LLM Value Alignment

## 1. Introduction

### 1.1 Background

The alignment of Large Language Models (LLMs) with human values represents one of the most pressing challenges in contemporary artificial intelligence research. As LLMs increasingly participate in value-laden decisions—from content moderation to healthcare recommendations—ensuring their moral reasoning capabilities generalize robustly to novel ethical dilemmas becomes paramount. Current alignment methodologies, predominantly Reinforcement Learning from Human Feedback (RLHF), train models on moral scenarios without systematic consideration of complexity structure. This approach treats moral learning as a flat optimization problem, potentially limiting the model's capacity to generalize beyond training distributions.

Human moral development, by contrast, follows a well-documented hierarchical progression. Lawrence Kohlberg's seminal theory of moral development, validated across six decades of psychological research, describes how individuals advance through distinct stages: from preconventional reasoning (self-interest and punishment avoidance) through conventional reasoning (social norms and authority) to postconventional reasoning (universal ethical principles). James Rest's Defining Issues Test (DIT) provides quantitative operationalization of these stages, demonstrating that moral complexity is measurable and follows developmental prerequisites.

Recent advances in developmental psychology-inspired AI training have demonstrated remarkable success in other domains. Piloto et al. (2022) showed that structuring AI training according to principles from developmental psychology significantly improved generalization in intuitive physics tasks. This cross-disciplinary transfer suggests that developmental frameworks may offer principled approaches to AI training more broadly. However, this methodology remains unexplored for moral reasoning—a critical gap given the fundamental differences between physical and ethical cognition.

The curriculum learning literature provides additional theoretical grounding. Hacohen and Weinshall (2019) demonstrated that ordered exposure to training examples by complexity improves representation quality and learning efficiency. Fayek et al. (2020) showed that progressive learning frameworks enable stage-based representation learning with superior transfer properties. These findings suggest that the structure of training data presentation, not merely its content, significantly impacts model capabilities.

### 1.2 Research Objectives

This research proposes **Moral Curriculum Learning (MCL)**, a novel alignment methodology that structures LLM fine-tuning as a Kohlberg-inspired moral curriculum. Our primary objectives are:

1. **Develop and validate a Kohlberg-structured moral curriculum** for LLM fine-tuning, with operationalized stage definitions and mastery criteria based on Rest's DIT methodology.

2. **Empirically test whether progressive moral complexity training yields superior generalization** compared to flat RLHF training on novel ethical dilemmas.

3. **Investigate the causal mechanisms** underlying any observed improvements, specifically whether curriculum structure creates hierarchical moral representations that enable compositional generalization.

4. **Establish developmental psychology as a principled framework** for value alignment methodology, providing theoretical grounding for future alignment research.

### 1.3 Research Significance

This research addresses fundamental questions at the intersection of moral psychology and AI alignment. If successful, MCL would:

- **Provide a theoretically-grounded alternative to RLHF** that leverages decades of validated psychological research on moral development.
- **Improve moral generalization** in LLMs, reducing failures on novel ethical dilemmas not represented in training data.
- **Establish a new research paradigm** connecting developmental psychology to AI alignment methodology.
- **Offer practical guidance** for structuring alignment training data and curricula.

The work directly addresses workshop themes concerning how theories of developmental moral psychology can inform AI development, and what methodological alternatives to RLHF might better teach AI systems human values.

## 2. Methodology

### 2.1 Theoretical Framework

Our methodology operationalizes Kohlberg's six stages of moral development into a structured training curriculum:

**Preconventional Level (Stages 1-2):**
- Stage 1: Obedience and punishment orientation (avoiding negative consequences)
- Stage 2: Self-interest orientation (instrumental exchange)

**Conventional Level (Stages 3-4):**
- Stage 3: Interpersonal accord and conformity (social approval)
- Stage 4: Authority and social-order maintaining orientation (law and duty)

**Postconventional Level (Stages 5-6):**
- Stage 5: Social contract orientation (democratic agreement)
- Stage 6: Universal ethical principles (justice, human rights)

We operationalize stage classification using Rest's DIT P-score methodology, adapted for scenario annotation:
- Preconventional: P-score < 30
- Conventional: P-score 30-50
- Postconventional: P-score > 50

### 2.2 Data Collection and Curriculum Construction

**Dataset Sources:**
We aggregate moral reasoning scenarios from multiple established benchmarks:
- **ETHICS dataset** (Hendrycks et al., 2021): 130,000+ examples across justice, deontology, virtue ethics, utilitarianism, and commonsense morality
- **MoralBench**: Stage-annotated moral dilemmas with Kohlberg classifications
- **Moral Machine dataset**: Cross-cultural moral decision scenarios
- **Custom DIT-annotated scenarios**: Classic moral dilemmas (Heinz dilemma, trolley problems) with expert stage annotations

**Annotation Protocol:**
For datasets lacking Kohlberg stage annotations, we employ:
1. Expert annotation by trained moral psychologists using DIT scoring rubrics
2. Inter-rater reliability threshold: Cohen's κ ≥ 0.75
3. Consensus resolution for disagreements

**Curriculum Structure:**
Each stage $s \in \{1, 2, 3, 4, 5, 6\}$ contains:
- Training set $\mathcal{D}_s^{train}$: ~5,000 scenarios per stage
- Validation set $\mathcal{D}_s^{val}$: ~500 scenarios per stage
- Mastery test set $\mathcal{D}_s^{test}$: ~500 scenarios per stage

### 2.3 Moral Curriculum Learning Algorithm

**Algorithm 1: Moral Curriculum Learning (MCL)**

**Input:** Base model $M_0$, curriculum stages $\{(\mathcal{D}_s, \theta_s)\}_{s=1}^{6}$, mastery threshold $\tau \in [0.8, 0.9]$

**Output:** Aligned model $M_{aligned}$

```
1: Initialize M ← M_0
2: for stage s = 1 to 6 do
3:     repeat
4:         // Stage-specific fine-tuning
5:         for batch B ∈ D_s^train do
6:             Compute alignment loss: L_s(M, B)
7:             Update M via gradient descent
8:         end for
9:         // Mastery evaluation
10:        accuracy_s ← Evaluate(M, D_s^test)
11:    until accuracy_s ≥ τ
12:    // Stage advancement gate
13:    Log stage completion metrics
14: end for
15: return M_aligned ← M
```

**Loss Function:**
For each stage $s$, we employ a preference-based alignment loss:

$$\mathcal{L}_s(M, B) = -\mathbb{E}_{(x, y^+, y^-) \sim B}\left[\log \sigma\left(\beta \cdot (r_M(x, y^+) - r_M(x, y^-))\right)\right]$$

where $x$ is the moral scenario, $y^+$ is the stage-appropriate response, $y^-$ is an inappropriate response, $r_M$ is the model's implicit reward, $\beta$ is a temperature parameter, and $\sigma$ is the sigmoid function.

**Mastery Gate Mechanism:**
Stage advancement requires:

$$\text{Accuracy}_s = \frac{1}{|\mathcal{D}_s^{test}|}\sum_{(x,y) \in \mathcal{D}_s^{test}} \mathbb{1}[M(x) = y] \geq \tau$$

where $\tau \in [0.8, 0.9]$ is the mastery threshold (hyperparameter tuned on validation set).

### 2.4 Experimental Design

**Conditions:**

1. **MCL (Treatment):** Kohlberg-structured 6-stage curriculum with mastery gates
2. **Flat RLHF (Baseline 1):** Standard RLHF training on all moral scenarios without ordering
3. **Random Curriculum (Baseline 2):** 6-stage curriculum with randomly assigned scenarios (controls for curriculum structure vs. Kohlberg ordering)
4. **Reverse Curriculum (Baseline 3):** Kohlberg stages in reverse order (Stage 6 → Stage 1)

**Controlled Variables:**
- Base model: Llama-2 7B and 13B (replication across scales)
- Total training compute: Fixed FLOP budget ($10^{18}$ FLOPs)
- Total training data: Equal scenario counts across conditions
- Hyperparameters: Learning rate, batch size, optimizer (AdamW)

**Sample Size:**
- $n = 20$ independent training runs per condition
- Statistical power: 0.8 for detecting Cohen's $d = 0.8$
- Significance level: $\alpha = 0.05$

### 2.5 Evaluation Metrics and Benchmarks

**Primary Metrics:**

1. **Moral Alignment Accuracy:** Agreement rate with human moral judgments on held-out test sets

$$\text{Accuracy} = \frac{\text{Correct moral judgments}}{\text{Total scenarios}} \times 100\%$$

2. **Generalization Gap:** Performance difference between in-distribution and out-of-distribution moral scenarios

$$\Delta_{gen} = \text{Accuracy}_{ID} - \text{Accuracy}_{OOD}$$

3. **Stage-Wise Performance:** Accuracy breakdown by Kohlberg stage to assess hierarchical competence

**Secondary Metrics:**

4. **Training Efficiency:** Compute required to reach mastery at each stage
5. **Robustness Score:** Performance under adversarial moral scenario perturbations
6. **Cross-Cultural Generalization:** Performance on Moral Machine scenarios from diverse cultural contexts

**Evaluation Benchmarks:**
- ETHICS test set (held-out)
- MoralBench novel dilemmas
- Custom out-of-distribution moral scenarios (expert-constructed)
- Adversarial moral scenarios (paraphrased, context-shifted)

### 2.6 Causal Mechanism Verification

To validate the proposed causal mechanism, we conduct ablation studies:

**Ablation 1: Representation Analysis**
- Extract intermediate representations at each training stage
- Apply probing classifiers to assess stage-specific moral concept encoding
- Hypothesis: MCL produces more separable stage representations than flat RLHF

**Ablation 2: Mastery Gate Necessity**
- Compare MCL with vs. without mastery gates (time-based stage advancement)
- Hypothesis: Mastery gates are necessary for hierarchical foundation building

**Ablation 3: Stage Ordering Sensitivity**
- Test alternative orderings (random, reverse, partial shuffles)
- Hypothesis: Kohlberg ordering provides unique advantage over alternatives

**Representation Similarity Analysis:**
We compute centered kernel alignment (CKA) between stage representations:

$$\text{CKA}(K, L) = \frac{\text{HSIC}(K, L)}{\sqrt{\text{HSIC}(K, K) \cdot \text{HSIC}(L, L)}}$$

where $K$ and $L$ are kernel matrices of representations from different stages.

### 2.7 Statistical Analysis Plan

**Primary Analysis:**
- Paired t-test comparing MCL vs. RLHF accuracy on novel dilemmas
- Effect size: Cohen's $d$ with 95% confidence intervals
- Bonferroni correction for multiple comparisons (3 primary predictions)

**Secondary Analyses:**
- ANOVA across all four conditions with post-hoc Tukey HSD
- Regression analysis: Stage mastery → subsequent stage performance
- Bootstrap confidence intervals for generalization gap estimates

**Reporting Standards:**
All results reported as: Mean ± Std Dev, 95% CI, Cohen's $d$, $p$-value

## 3. Expected Outcomes & Impact

### 3.1 Primary Predictions

**P1 (Moral Generalization Superiority):**
We predict MCL-trained models will achieve ≥10 percentage points higher accuracy on novel moral dilemmas compared to flat RLHF baselines. This prediction is grounded in curriculum learning theory and the developmental psychology transfer precedent established by Piloto et al. (2022).

**P2 (Stage-Wise Learning Dynamics):**
MCL will demonstrate monotonically increasing training time per stage (Stage 1 fastest, Stage 6 slowest), reflecting the genuine complexity gradient in Kohlberg's hierarchy. This validates that the curriculum structure captures meaningful moral complexity differences.

**P3 (Distribution Shift Robustness):**
MCL-trained models will show smaller performance degradation (≤5% vs. ≥15% for RLHF) on out-of-distribution moral scenarios, indicating more robust moral representations.

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. MCL accuracy on novel dilemmas ≤ RLHF accuracy
2. Stage mastery shows no correlation with subsequent stage performance
3. Random ordering performs equivalently to Kohlberg ordering

### 3.3 Broader Impact

**Scientific Contributions:**
- Establishes developmental psychology as a principled framework for AI alignment
- Provides empirical evidence for/against hierarchical moral representation learning
- Introduces novel evaluation methodology for moral generalization

**Practical Applications:**
- Offers practitioners a theoretically-grounded curriculum design methodology
- Potentially reduces alignment failures on novel ethical scenarios
- Provides interpretable stage-wise competence assessments

**Limitations and Ethical Considerations:**
- Kohlberg's framework has documented Western individualistic bias (Gilligan's critique of care ethics underrepresentation)
- Initial experiments limited to English-language scenarios
- Stage boundaries may be fuzzier than discrete operationalization assumes
- Results may not transfer to real-time moral decision systems

**Future Directions:**
- Extend curriculum to incorporate Gilligan's ethics of care
- Cross-cultural validation with non-Western moral frameworks
- Integration with constitutional AI and other alignment approaches
- Application to multimodal moral reasoning

### 3.4 Timeline and Resources

**Phase 1 (Months 1-3):** Dataset curation and Kohlberg stage annotation
**Phase 2 (Months 4-6):** MCL algorithm implementation and pilot experiments
**Phase 3 (Months 7-9):** Full experimental runs across all conditions
**Phase 4 (Months 10-12):** Analysis, ablations, and manuscript preparation

**Compute Requirements:** ~$10^{19}$ total FLOPs across all experimental conditions

This research represents a principled attempt to bridge moral psychology theory and AI alignment practice, potentially establishing a new paradigm for value alignment methodology grounded in decades of validated developmental research.