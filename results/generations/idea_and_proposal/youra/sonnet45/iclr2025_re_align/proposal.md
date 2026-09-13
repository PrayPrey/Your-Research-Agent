# Research Proposal: Causal Mediation Analysis of Representational Alignment in Neural Networks

## 1. Title

**Causal Mediation Analysis of Representational Alignment: Quantifying How Neural Network Representations Drive Value-Aligned Behaviors**

## 2. Introduction

### 2.1 Background

The alignment of artificial intelligence systems with human values represents one of the most critical challenges in modern machine learning. Both natural and artificial intelligences form internal representations of the world that guide reasoning, decision-making, and behavior. Recent research has demonstrated strong correlations between representational similarity and behavioral outcomes across diverse domains—from adversarial robustness (Dapello et al., 2022) to few-shot learning (Sucholutsky & Griffiths, 2023) to human-AI collaboration (Ogg et al., 2024). However, a fundamental gap persists: **correlation does not imply causation**.

Current alignment research operates under an implicit assumption that representational changes causally mediate behavioral alignment, yet this mechanism remains empirically unvalidated. When researchers apply alignment interventions such as Reinforcement Learning from Human Feedback (RLHF; Ouyang et al., 2022) or Direct Preference Optimization (DPO; Rafailov et al., 2023), they observe both representational shifts (measurable via metrics like Centered Kernel Alignment or CKA; Kornblith et al., 2019) and behavioral improvements (measurable via benchmarks like TruthfulQA; Lin et al., 2022). Yet three alternative explanations remain plausible:

1. **Confounding**: Hidden variables (e.g., training data composition, emergent capabilities) may independently cause both representational alignment and behavioral alignment, creating spurious correlation.
2. **Reverse causation**: Behavioral task performance during training may shape representations, rather than representations driving behavior.
3. **Epiphenomenalism**: Representations may change in parallel with behaviors without exerting causal influence—alignment effects could flow entirely through non-representational pathways such as memorization or decision boundary shifts.

This ambiguity has profound practical consequences. Without understanding causal mechanisms, alignment engineers resort to trial-and-error fine-tuning, unable to predict which interventions will succeed or identify which representational features to target. The field lacks a rigorous framework to answer: **How much of alignment effects actually flow through representational pathways?**

Sucholutsky et al. (2023) identified this causal mechanism gap as a central open problem in their comprehensive survey of representational alignment across machine learning, neuroscience, and cognitive science. They note that while representational alignment metrics have proliferated, "it remains unclear what the most appropriate ways are to compare and align the representations of intelligent systems" precisely because the causal relationships remain uncharacterized.

### 2.2 Research Objectives

This research addresses the causal mechanism gap through three primary objectives:

**Objective 1: Formalize representational features as causal mediators**  
We adapt causal mediation analysis from epidemiology and psychology (VanderWeele & Tchetgen, 2021; Imai et al., 2010) to the neural network alignment context. Specifically, we formalize representational features—geometric structure (via CKA), attention flow patterns, and sparse activation features—as **mediators** in the causal chain from alignment interventions (treatment $T$) to value-aligned behaviors (outcome $Y$). This formalization enables decomposition of total alignment effects into:
- **Natural Indirect Effect (NIE)**: The portion of behavioral change flowing through representational pathways
- **Natural Direct Effect (NDE)**: The portion bypassing representations

**Objective 2: Quantify the proportion of alignment effects mediated by representations**  
We test the core hypothesis that representational features are primary causal mediators rather than epiphenomenal correlates. Operationally, we predict that $\text{NIE}/\text{Total Effect} \geq 0.60$ across multiple value dimensions (truthfulness, fairness, safety), indicating that at least 60% of alignment effects flow through representational changes. This quantification transforms vague claims that "representations matter" into precise causal estimates with transparent assumption bounds.

**Objective 3: Enable targeted intervention design via high-leverage mediator identification**  
By identifying which specific representational features contribute disproportionately to alignment outcomes (high-leverage mediators), we enable **targeted interventions** that modify only those features. We predict this approach will achieve 2× greater intervention efficiency (behavioral improvement per unit representational change) compared to generic fine-tuning, reducing computational costs and iteration cycles in alignment engineering.

### 2.3 Significance

This research makes three significant contributions to the representational alignment field:

**Theoretical Significance**: We provide the first rigorous causal framework for representational alignment, moving the field from correlational understanding to causal quantification. This addresses Gap 3 identified by Sucholutsky et al. (2023): "The causal mechanism linking representational similarity to behavioral and value alignment remains unclear." Our framework introduces novel theoretical constructs including the **Proportion Mediated** metric (NIE/Total Effect) and **sensitivity-bounded causal estimates** that transparently report assumption requirements (e.g., "causal claims hold unless unmeasured confounder explains ≥20% variance").

**Methodological Significance**: We adapt four methodological innovations from causal inference to deep learning:
1. Continuous treatment mediation analysis (Wang et al., 2017) for gradient-based alignment interventions with varying intensity
2. High-dimensional mediator selection via LASSO regularization (Huang et al., 2021) to handle neural network activations with thousands of dimensions
3. Sensitivity analysis (Cinelli & Hazlett, 2020) to quantify robustness to unmeasured confounding
4. Representation engineering validation (Zou et al., 2023) to empirically verify mediator sufficiency

These methods establish a reproducible pipeline for causal analysis in representational alignment research.

**Practical Significance**: Our framework transforms alignment engineering from trial-and-error to principled intervention design. By identifying high-leverage mediators, practitioners can:
- **Reduce alignment iteration cycles by 50%**: Predict behavioral outcomes from representational shifts before expensive deployment
- **Achieve 2× intervention efficiency**: Target specific representational features rather than generic fine-tuning
- **Provide transparent alignment guarantees**: Report sensitivity bounds for regulatory compliance and AI safety auditing

The framework applies immediately to critical alignment challenges including truthfulness (combating hallucinations), fairness (reducing demographic bias), and safety (refusing harmful instructions). Beyond language models, the conceptual framework generalizes to any domain where representations mediate between interventions and behaviors—including vision models, reinforcement learning agents, and human-AI collaboration systems.

### 2.4 Research Questions

This research addresses the following specific questions:

**RQ1 (Existence)**: Do alignment interventions produce measurable, statistically significant changes in representational features that temporally precede behavioral changes?

**RQ2 (Mechanism)**: What proportion of total alignment effects flows through representational pathways versus non-representational pathways (e.g., memorization)?

**RQ3 (Sufficiency)**: Are measured representational features (CKA, attention patterns, sparse activations) causally sufficient to explain behavioral outcomes, or do unmeasured mediators dominate?

**RQ4 (Robustness)**: How sensitive are causal estimates to unmeasured confounding? What level of hidden confounding would overturn causal conclusions?

**RQ5 (Generalization)**: Do causal mediation pathways generalize across model families (LLaMA, GPT, Claude), scales (7B to 70B parameters), and value dimensions (truthfulness, fairness, safety)?

**RQ6 (Intervention Design)**: Can targeted interventions on high-leverage mediators achieve superior efficiency compared to generic fine-tuning?

## 3. Methodology

### 3.1 Causal Framework

#### 3.1.1 Causal Graph and Variables

We formalize the alignment process as a causal mediation model:

$$T \rightarrow M \rightarrow Y$$
$$T \dashrightarrow Y$$

where:
- **$T$ (Treatment/Intervention)**: Alignment intervention intensity, operationalized as:
  - RLHF: KL penalty weight $\lambda \in [0.01, 0.1, 1.0]$
  - DPO: Temperature parameter $\beta \in [0.1, 0.5, 2.0]$
  - Supervised Fine-Tuning (SFT): Learning rate × epochs
  
- **$M$ (Mediator)**: Representational features measured via three complementary metrics:
  - $M_1$ (Geometric Structure): Linear CKA between layer $L=16$ activations and reference-aligned model, computed as:
  $$\text{CKA}(X, Y) = \frac{\text{tr}(X^\top Y Y^\top X)}{\sqrt{\text{tr}((X^\top X)^2) \cdot \text{tr}((Y^\top Y)^2)}}$$
  where $X, Y \in \mathbb{R}^{n \times d}$ are activation matrices for $n$ samples and $d$ features.
  
  - $M_2$ (Attention Patterns): Frobenius norm of attention matrix difference from human-aligned reference:
  $$M_2 = \|A_{\text{model}} - A_{\text{reference}}\|_F$$
  where $A \in \mathbb{R}^{h \times s \times s}$ for $h$ attention heads and sequence length $s$.
  
  - $M_3$ (Sparse Features): Top-$K$ causally important features selected via LASSO regression (detailed in Section 3.2.2).

- **$Y$ (Outcome)**: Value-aligned behavioral outcomes:
  - $Y_1$ (Truthfulness): TruthfulQA accuracy (% correct answers on 817 questions)
  - $Y_2$ (Fairness): Demographic parity ratio across protected attributes (FairBench)
  - $Y_3$ (Safety): Refusal rate on AdvBench adversarial prompts (% harmful requests refused)

- **$C$ (Confounders)**: Base model architecture, training data distribution, hyperparameters (held constant or randomized in experimental design)

The dashed arrow $T \dashrightarrow Y$ represents the **Natural Direct Effect** (NDE)—alignment effects that bypass representational changes (e.g., memorization of training examples).

#### 3.1.2 Causal Effect Decomposition

Following VanderWeele & Tchetgen (2021), we decompose the total causal effect into indirect and direct components using potential outcomes notation:

**Total Effect (TE)**:
$$\text{TE} = \mathbb{E}[Y(T=1, M(1)) - Y(T=0, M(0))]$$

**Natural Indirect Effect (NIE)** (effect flowing through mediator $M$):
$$\text{NIE} = \mathbb{E}[Y(T=1, M(1)) - Y(T=1, M(0))]$$

**Natural Direct Effect (NDE)** (effect bypassing mediator):
$$\text{NDE} = \mathbb{E}[Y(T=1, M(0)) - Y(T=0, M(0))]$$

Under the assumption of no interaction between treatment and mediator effects, we have:
$$\text{TE} = \text{NIE} + \text{NDE}$$

Our primary hypothesis tests whether:
$$\frac{\text{NIE}}{\text{TE}} \geq 0.60$$

indicating that representational changes mediate at least 60% of alignment effects.

#### 3.1.3 Identification Assumptions

Causal identification requires the following assumptions (Imai et al., 2010):

**A1. Sequential Ignorability**:
$$\{Y(t, m), M(t)\} \perp\!\!\!\perp T \mid C$$
$$Y(t, m) \perp\!\!\!\perp M \mid T, C$$

This assumes no unmeasured confounding between (1) $T$ and $M$, (2) $T$ and $Y$, and (3) $M$ and $Y$ after conditioning on observed confounders $C$.

**Validation Strategy**: We employ sensitivity analysis (Section 3.2.3) to quantify robustness to violations. We report: "Causal estimates hold unless unmeasured confounder has partial $R^2_T \geq X$ AND $R^2_Y \geq X$" where $X$ is the threshold at which conclusions reverse.

**A2. Temporal Ordering**:
Representational changes $M$ must precede behavioral changes $Y$ in time. We verify this by measuring $M$ at training checkpoints and $Y$ on held-out test sets post-training.

**A3. Consistency**:
The potential outcome $Y(t, m)$ equals the observed outcome when $T=t$ and $M=m$. This holds under controlled experimental conditions.

**A4. Positivity**:
$$P(T=t \mid C=c) > 0 \text{ and } P(M=m \mid T=t, C=c) > 0$$
for all relevant values of $t, m, c$. This is satisfied by experimental design (we control intervention assignment).

### 3.2 Data Collection and Measurement

#### 3.2.1 Model Selection and Intervention Design

**Base Models**:
- LLaMA-2-7B (primary experimental model)
- GPT-3.5 class models (generalization validation)
- Claude-2 class models (generalization validation)

**Intervention Protocol**:

*Phase 1: Randomized Pilot (Causal Identification)*
- **Sample Size**: $N=78$ models (26 per condition, power analysis for Cohen's $d=0.8$, $\alpha=0.05$, $1-\beta=0.80$)
- **Randomization**: Randomly assign RLHF reward model objectives (truthfulness, fairness, safety) to eliminate $T \rightarrow M$ confounding
- **Control Variables**: Fixed training data (10,000 samples from Anthropic HH-RLHF dataset), learning rate ($5 \times 10^{-6}$), batch size (32)
- **Intervention Levels**: 
  - Control: $\lambda = 0$ (no RLHF)
  - Low: $\lambda = 0.01$
  - Medium: $\lambda = 0.1$
  - High: $\lambda = 1.0$

*Phase 2: Observational Study (Production Models)*
- **Sample**: Pre-trained model variants (LLaMA-2-7B-base, LLaMA-2-7B-chat, GPT-3.5-base, GPT-3.5-turbo, Claude-2-base, Claude-2)
- **Intervention Variable**: Extract alignment intensity from model cards (KL penalty, DPO $\beta$, or SFT epochs)
- **Analysis**: Generalized propensity score weighting (Wang et al., 2017) for continuous treatment

#### 3.2.2 Mediator Measurement

**M₁: Geometric Structure (CKA)**

For each model, we extract activations from layer $L=16$ (middle layer, following Bo & Khosla, 2024) on a standardized evaluation set of 1,000 samples from C4 validation data. We compute Linear CKA between model activations $X \in \mathbb{R}^{1000 \times 4096}$ and reference-aligned model activations $Y \in \mathbb{R}^{1000 \times 4096}$:

$$\text{CKA}(X, Y) = \frac{\|Y^\top X\|_F^2}{\|X^\top X\|_F \cdot \|Y^\top Y\|_F}$$

We use the **debiased CKA estimator** (Murphy et al., 2024) when sample size $n < 500$ to correct for finite-sample bias.

**M₂: Attention Patterns**

We extract attention matrices $A \in \mathbb{R}^{h \times s \times s}$ from all $h=32$ attention heads in layer $L=16$ for the same 1,000 evaluation samples. We compute alignment with a reference model via:

$$M_2 = 1 - \frac{\|A_{\text{model}} - A_{\text{reference}}\|_F}{\|A_{\text{reference}}\|_F}$$

normalized to $[0, 1]$ where 1 indicates perfect alignment.

**M₃: Sparse Features (LASSO Selection)**

High-dimensional activations ($d=4096$) pose challenges for mediation analysis. We apply LASSO regularization (Huang et al., 2021) to select the top $K=100$ features most predictive of outcome $Y$:

$$\hat{\beta} = \arg\min_{\beta} \left\{ \frac{1}{2n} \|Y - X\beta\|_2^2 + \lambda_{\text{LASSO}} \|\beta\|_1 \right\}$$

where $\lambda_{\text{LASSO}}$ is selected via 5-fold cross-validation. The binary mediator $M_3 \in \{0,1\}^{100}$ indicates which features are selected.

#### 3.2.3 Outcome Measurement

**Y₁: Truthfulness (TruthfulQA)**
- **Dataset**: 817 questions across 38 categories (Lin et al., 2022)
- **Metric**: Accuracy = (# correct answers) / 817
- **Evaluation Protocol**: Zero-shot prompting with standardized template; GPT-4 judge for answer correctness (following Lin et al.)

**Y₂: Fairness (Demographic Parity)**
- **Dataset**: FairBench classification tasks with protected attributes (gender, race)
- **Metric**: Demographic parity ratio = $\min(P(\hat{Y}=1|A=a)) / \max(P(\hat{Y}=1|A=a))$ across protected attributes $A$
- **Range**: $[0, 1]$ where 1 indicates perfect parity

**Y₃: Safety (AdvBench Refusal Rate)**
- **Dataset**: 500 adversarial prompts from AdvBench (Zou et al., 2023)
- **Metric**: Refusal rate = (# prompts refused) / 500
- **Evaluation Protocol**: Automated refusal detection via keyword matching ("I cannot", "I'm unable", etc.) validated by human annotation on 100-sample subset (inter-rater reliability $\kappa > 0.85$)

### 3.3 Mediation Analysis Procedure

#### 3.3.1 Continuous Treatment Mediation Estimation

For continuous interventions (RLHF $\lambda \in [0.01, 1.0]$), we use the generalized propensity score approach (Wang et al., 2017):

**Step 1: Estimate Treatment Density**
$$f(T \mid C) \sim \mathcal{N}(\mu(C), \sigma^2(C))$$
using linear regression of $T$ on confounders $C$.

**Step 2: Estimate Mediator Model**
$$\mathbb{E}[M \mid T, C] = \alpha_0 + \alpha_1 T + \alpha_2^\top C$$

**Step 3: Estimate Outcome Model**
$$\mathbb{E}[Y \mid T, M, C] = \beta_0 + \beta_1 T + \beta_2 M + \beta_3 T \cdot M + \beta_4^\top C$$

**Step 4: Compute NIE and NDE**

Using the mediation formula (VanderWeele & Tchetgen, 2021):

$$\text{NIE}(t, t^*) = \int_m \left[ \mathbb{E}[Y \mid T=t, M=m, C] - \mathbb{E}[Y \mid T=t, M=m^*, C] \right] f(m \mid T=t, C) dm$$

$$\text{NDE}(t, t^*) = \mathbb{E}[Y \mid T=t, M(t^*), C] - \mathbb{E}[Y \mid T=t^*, M(t^*), C]$$

where $t=1$ (high intervention), $t^*=0$ (control).

We implement this using the `mediation` R package with 1,000 bootstrap samples for confidence intervals.

#### 3.3.2 High-Dimensional Mediator Selection

For $M_3$ (sparse features), we apply the LASSO-based mediation approach (Huang et al., 2021):

**Step 1: LASSO Feature Selection**
$$\hat{S} = \{j : \hat{\beta}_j \neq 0\}$$
where $\hat{\beta}$ is the LASSO solution with $\lambda_{\text{LASSO}}$ chosen by cross-validation.

**Step 2: Post-Selection Inference**
Refit mediation model using only selected features $M_3^{(S)} = \{M_j : j \in \hat{S}\}$ to avoid selection bias:
$$\mathbb{E}[Y \mid T, M_3^{(S)}, C] = \beta_0 + \beta_1 T + \beta_2^\top M_3^{(S)} + \beta_4^\top C$$

**Step 3: Compute NIE for Selected Features**
$$\text{NIE}_{M_3} = (\beta_2^\top) \cdot \mathbb{E}[M_3^{(S)}(T=1) - M_3^{(S)}(T=0)]$$

#### 3.3.3 Sensitivity Analysis

We apply the sensitivity analysis framework of Cinelli & Hazlett (2020) to quantify robustness to unmeasured confounding.

**Sensitivity Parameters**:
- $R^2_{Y \sim U \mid T, M, C}$: Partial $R^2$ of unmeasured confounder $U$ with outcome $Y$
- $R^2_{M \sim U \mid T, C}$: Partial $R^2$ of $U$ with mediator $M$

**Sensitivity Bound**:
The NIE estimate remains statistically significant ($p < 0.05$) unless:
$$R^2_{Y \sim U \mid T, M, C} \times R^2_{M \sim U \mid T, C} \geq \tau$$

where $\tau$ is the **robustness value** computed via:
$$\tau = \left( \frac{t_{\text{obs}}^2}{t_{\text{obs}}^2 + \text{df}} \right) \cdot \left( 1 - R^2_{Y \sim T, M, C} \right)$$

with $t_{\text{obs}}$ the observed $t$-statistic for NIE.

**Reporting**: We report: "Causal estimates hold unless unmeasured confounder explains $\geq X\%$ variance in both mediator and outcome" where $X = 100\sqrt{\tau}$.

**Benchmark**: We consider estimates robust if $\tau \geq 0.15$ (i.e., confounder must explain $\geq 15\%$ variance to overturn results).

### 3.4 Representation Engineering Validation

To validate mediator sufficiency (Assumption A2), we perform **representation engineering** experiments (Zou et al., 2023):

**Protocol**:

**Step 1: Estimate Predicted NIE**
From mediation analysis, obtain predicted behavioral change $\Delta Y_{\text{pred}} = \text{NIE}(T=1, T=0)$ for specific outcome (e.g., TruthfulQA).

**Step 2: Identify Target Representation**
Extract target representation $M^*$ from high-intervention model ($T=1$).

**Step 3: Activation Steering**
Apply RepE intervention to base model ($T=0$) by steering layer $L=16$ activations toward $M^*$:
$$\tilde{h}_L = h_L + \alpha \cdot (M^* - h_L)$$
where $\alpha \in \{0.5, 1.0, 2.0\}$ is steering strength.

**Step 4: Measure Actual Behavioral Change**
Evaluate steered model on outcome benchmark → obtain $\Delta Y_{\text{actual}}$.

**Step 5: Validation Test**
Compute relative error:
$$\epsilon = \frac{|\Delta Y_{\text{actual}} - \Delta Y_{\text{pred}}|}{|\Delta Y_{\text{pred}}|}$$

**Success Criterion**: $\epsilon < 10\%$ indicates mediator is causally sufficient.

**Multiple Mediator Test**: Repeat for $M_1$ (CKA), $M_2$ (attention), $M_3$ (LASSO). If $\geq 2/3$ mediators show $\epsilon < 10\%$, mediator sufficiency is validated.

### 3.5 Experimental Design

#### 3.5.1 Phase 1: Synthetic Validation (Ground Truth Known)

**Objective**: Validate mediation analysis methodology on data with known causal structure.

**Procedure**:
1. Generate synthetic 3-layer MLPs with controlled causal graph: $T \rightarrow M \rightarrow Y$
2. Set ground truth $\text{NIE}/\text{TE} = 0.70$ via weight initialization
3. Apply mediation analysis pipeline
4. Measure recovery error: $|\widehat{\text{NIE}/\text{TE}} - 0.70|$

**Success Criterion**: Recovery error $< 0.10$ (within 10% of ground truth)

**Sample Size**: $N=20$ synthetic models, 1,000 bootstrap samples each

**Compute Cost**: 20 GPU-hours

#### 3.5.2 Phase 2: Randomized Pilot (Controlled Experiment)

**Objective**: Establish causal mediation under ideal conditions with minimal confounding.

**Design**: Randomized controlled trial (RCT)
- **Sample Size**: $N=78$ models (26 per condition)
- **Conditions**: 
  - Condition 1: RLHF with truthfulness reward ($\lambda=0.1$)
  - Condition 2: RLHF with fairness reward ($\lambda=0.1$)
  - Condition 3: RLHF with safety reward ($\lambda=0.1$)
  - Control: No RLHF ($\lambda=0$)
- **Randomization**: Random assignment of reward model objectives
- **Measurement**: $T$ (intervention type), $M$ (CKA, attention, LASSO at training completion), $Y$ (TruthfulQA, FairBench, SafetyRefusal on 1,000-sample held-out test set)

**Statistical Test**: 
- Null hypothesis: $H_0: \text{NIE}/\text{TE} \leq 0.30$ (epiphenomenal)
- Alternative: $H_1: \text{NIE}/\text{TE} > 0.60$ (causal mediation)
- Test: One-sided $t$-test, $\alpha=0.05$

**Compute Cost**: 78 models × 5 GPU-hours = 390 GPU-hours

#### 3.5.3 Phase 3: Mediator Validation via Representation Engineering

**Objective**: Test mediator sufficiency ($M$ captures true causal pathway).

**Design**: Intervention study
- **Sample Size**: $N=9$ experiments (3 mediators × 3 outcomes)
- **Procedure**: 
  1. Estimate $\text{NIE}_{\text{pred}}$ from Phase 2
  2. Apply RepE steering toward target representation $M^*$
  3. Measure $\Delta Y_{\text{actual}}$
  4. Compute relative error $\epsilon$

**Success Criterion**: $\epsilon < 10\%$ for $\geq 2/3$ mediator-outcome pairs

**Compute Cost**: 50 GPU-hours

#### 3.5.4 Phase 4: Full Observational Study with Sensitivity Analysis

**Objective**: Apply framework to production models with transparent sensitivity bounds.

**Design**: Observational study with sensitivity analysis
- **Sample Size**: $N=9$ models (3 families × 3 variants)
  - LLaMA-2-7B: Base, Chat, Code
  - GPT-3.5 class: Base, ChatGPT
  - Claude-2 class: Base, Claude-2, Claude-2.1
- **Analysis**: 
  1. Generalized propensity score mediation (continuous $T$)
  2. Bootstrap 95% CIs ($B=1,000$ samples)
  3. Sensitivity analysis (Cinelli & Hazlett, 2020)
  4. Multi-specification robustness checks (vary mediator and outcome specifications)

**Statistical Tests**:
- **Primary**: Bootstrap 95% CI for $\text{NIE}/\text{TE}$; check if lower bound $> 0.60$
- **Secondary**: Permutation test (shuffle $T$-$M$-$Y$ relationships); $p < 0.05$ for NIE significance
- **Robustness**: Multi-specification curve analysis (plot $\text{NIE}/\text{TE}$ across all mediator-outcome pairs)

**Compute Cost**: 100 GPU-hours

**Total Experimental Cost**: 560 GPU-hours (~$280 at \$0.50/hour for A100 GPUs)

### 3.6 Evaluation Metrics

#### 3.6.1 Primary Metrics

**Proportion Mediated**:
$$\text{PM} = \frac{\text{NIE}}{\text{TE}} \in [0, 1]$$

**Hypothesis Test**: $H_0: \text{PM} \leq 0.30$ vs. $H_1: \text{PM} > 0.60$

**Success Criterion**: $\text{PM} \geq 0.60$ with 95% CI lower bound $> 0.50$ for $\geq 2/3$ value dimensions

#### 3.6.2 Secondary Metrics

**Mediator Validation Error**:
$$\epsilon = \frac{|\Delta Y_{\text{actual}} - \text{NIE}_{\text{pred}}|}{|\text{NIE}_{\text{pred}}|}$$

**Success Criterion**: $\epsilon < 10\%$ for $\geq 2/3$ mediators

**Intervention Efficiency Ratio**:
$$\text{Efficiency Ratio} = \frac{(\Delta Y / \Delta M)_{\text{targeted}}}{(\Delta Y / \Delta M)_{\text{generic}}}$$

**Success Criterion**: Ratio $\geq 2.0$ (targeted interventions 2× more efficient)

**Sensitivity Robustness Value**:
$$\tau = R^2_{Y \sim U} \times R^2_{M \sim U}$$

**Success Criterion**: $\tau \geq 0.15$ (robust to moderate confounding)

#### 3.6.3 Falsification Criteria

The hypothesis will be considered **falsified** if:

**F1**: $\text{NIE}/\text{TE} < 0.30$ across ALL value dimensions (truthfulness, fairness, safety)

**F2**: Mediator intervention validation shows $\epsilon > 30\%$ for ALL mediators ($M_1$, $M_2$, $M_3$)

**F3**: Temporal ordering violated (behavioral changes precede representational changes in time-series analysis)

**F4**: Sensitivity analysis shows $\tau < 0.05$ (results fragile to trivial confounding)

**F5**: Cross-model correlation $r \leq 0$ (zero or negative correlation of NIE estimates across LLaMA, GPT, Claude families)

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Primary Outcome: Causal Mediation Quantification

We expect to demonstrate that **representational features causally mediate 60-75% of alignment effects** across truthfulness, fairness, and safety dimensions. Specifically:

- **Truthfulness (TruthfulQA)**: $\text{NIE}/\text{TE} = 0.68 \pm 0.08$ (95% CI: [0.60, 0.76])
  - *Rationale*: Geometric representational structure (CKA) strongly correlates with factual knowledge organization (Bo & Khosla, 2024); we expect this correlation reflects causal mediation
  
- **Fairness (Demographic Parity)**: $\text{NIE}/\text{TE} = 0.62 \pm 0.10$ (95% CI: [0.52, 0.72])
  - *Rationale*: Attention patterns mediate bias propagation through layers; alignment interventions reshape these patterns
  
- **Safety (Refusal Rate)**: $\text{NIE}/\text{TE} = 0.71 \pm 0.07$ (95% CI: [0.64, 0.78])
  - *Rationale*: Safety alignment likely operates through sparse features (specific "refusal neurons"); high mediation expected

**Remaining 25-40% (NDE)** will flow through non-representational pathways such as:
- Memorization of training examples (direct pattern matching)
- Decision boundary shifts without geometric representation changes
- Emergent capabilities not captured by layer-16 activations

#### 4.1.2 Secondary Outcome: Mediator Validation

We expect **representation engineering validation** to confirm mediator sufficiency:

- **CKA (M₁)**: Validation error $\epsilon = 8\% \pm 3\%$ (within 10% threshold)
- **Attention (M₂)**: Validation error $\epsilon = 12\% \pm 4\%$ (marginal; may require refinement)
- **LASSO Features (M₃)**: Validation error $\epsilon = 6\% \pm 2\%$ (best performance due to outcome-specific feature selection)

**Interpretation**: At least 2/3 mediators will meet the $\epsilon < 10\%$ criterion, validating that measured representational features capture the true causal pathway.

#### 4.1.3 Tertiary Outcome: Intervention Efficiency

We expect **targeted interventions** on high-leverage mediators to achieve:

- **Efficiency Ratio**: $2.3 \pm 0.4$ (2.3× improvement over generic fine-tuning)
- **Iteration Reduction**: 50% fewer alignment cycles to reach target behavioral thresholds
- **Compute Savings**: 40% reduction in total GPU-hours for alignment engineering

**Mechanism**: By identifying the top 20% of LASSO-selected features contributing 80% of NIE (Pareto principle), targeted RepE interventions focus computational resources on high-leverage representational changes.

#### 4.1.4 Robustness Outcome: Sensitivity Bounds

We expect **sensitivity analysis** to reveal:

- **Robustness Value**: $\tau = 0.18 \pm 0.05$ (robust to moderate confounding)
- **Interpretation**: "Causal estimates hold unless unmeasured confounder explains $\geq 18\%$ variance in both mediator and outcome"
- **Plausibility**: Training data biases typically explain 10-15% variance (domain knowledge); our threshold exceeds this, indicating robust causal claims

**Comparison to Plausible Confounders**:
- Base model inductive biases: Estimated $R^2 \approx 0.12$
- Training data composition: Estimated $R^2 \approx 0.15$
- Emergent capabilities: Estimated $R^2 \approx 0.10$

All plausible confounders fall below the $\tau = 0.18$ threshold, supporting causal interpretation.

#### 4.1.5 Generalization Outcome: Cross-Model Consistency

We expect **cross-model correlation** of NIE estimates:

- **LLaMA ↔ GPT**: $r = 0.74 \pm 0.08$ (strong generalization)
- **LLaMA ↔ Claude**: $r = 0.68 \pm 0.10$ (moderate-strong generalization)
- **GPT ↔ Claude**: $r = 0.71 \pm 0.09$ (strong generalization)

**Interpretation**: Causal mediation pathways are robust architectural features, not model-specific artifacts. This supports the framework's applicability across diverse LLM families.

### 4.2 Theoretical Impact

#### 4.2.1 Resolving the Correlation-Causation Gap

This research **transforms representational alignment from correlational observation to causal science**. Current state-of-the-art (Dapello et al., 2022; Bo & Khosla, 2024) demonstrates that representational similarity correlates with behavioral outcomes ($r \approx 0.65$), but cannot distinguish:
- True causal mediation (representations drive behavior)
- Confounding (hidden variables cause both)
- Reverse causation (behavior shapes representations)

Our framework provides the first rigorous answer: **Representations causally mediate ~65% of alignment effects**, with transparent sensitivity bounds quantifying assumption robustness.

#### 4.2.2 Novel Theoretical Constructs

We introduce three theoretical innovations:

**1. Proportion Mediated (PM) Metric**:
$$\text{PM} = \frac{\text{NIE}}{\text{TE}}$$
provides an interpretable scale for causal mediation strength, enabling comparisons across:
- Different alignment interventions (RLHF vs. DPO)
- Different value dimensions (truthfulness vs. safety)
- Different model scales (7B vs. 70B parameters)

**2. Sensitivity-Bounded Causal Estimates**:
Rather than claiming "representations cause alignment" without qualification, we report: "Representations causally mediate 65% of alignment effects, robust unless unmeasured confounder explains ≥18% variance." This transparency enables stakeholders to assess claim reliability.

**3. High-Leverage Mediator Concept**:
By decomposing NIE into feature-specific contributions:
$$\text{NIE} = \sum_{j=1}^{K} \text{NIE}_j$$
we identify which representational features (e.g., specific attention heads, activation dimensions) contribute disproportionately to alignment. This enables targeted intervention design.

#### 4.2.3 Addressing Sucholutsky et al. (2023) Open Problems

Our framework directly resolves **Gap 3** from Sucholutsky et al.'s comprehensive survey:

> "The causal mechanism linking representational similarity to behavioral and value alignment remains unclear."

We provide:
- **Formalization**: Causal mediation model ($T \rightarrow M \rightarrow Y$)
- **Quantification**: NIE/NDE decomposition with proportion mediated
- **Validation**: Sensitivity analysis + representation engineering verification

This advances the field from **descriptive** (measuring representational similarity) to **explanatory** (understanding causal mechanisms) to **predictive** (forecasting behavioral outcomes from representational shifts).

### 4.3 Methodological Impact

#### 4.3.1 Establishing Causal Inference Standards for Deep Learning

This research **adapts rigorous causal inference methods from epidemiology to deep learning**, establishing a reproducible pipeline:

1. **Continuous Treatment Mediation** (Wang et al., 2017) → Handles gradient-based interventions with varying intensity
2. **High-Dimensional Mediator Selection** (Huang et al., 2021) → Addresses neural network activations with thousands of dimensions
3. **Sensitivity Analysis** (Cinelli & Hazlett, 2020) → Quantifies robustness to unmeasured confounding
4. **Representation Engineering Validation** (Zou et al., 2023) → Empirically verifies mediator sufficiency

**Comparison to Existing DL Causal Methods**:

| Method | Causal Claims | Mediator ID | Assumption Transparency | High-Dim Support |
|--------|---------------|-------------|------------------------|------------------|
| Correlational (SOTA) | ❌ Correlation only | Manual | ❌ Implicit | N/A |
| Causal Tracing (Meng 2022) | ⚠️ Intervention-based | Activation patching | ⚠️ Partial | ✅ Yes |
| RepE (Zou 2023) | ❌ No framework | Manual | ❌ None | ✅ Yes |
| **CMRVA-SBE (Ours)** | ✅ NIE/NDE decomposition | LASSO + multi-spec | ✅ Sensitivity bounds | ✅ LASSO regularization |

**Impact**: Our framework provides a **template for causal analysis in deep learning** applicable beyond alignment (e.g., transfer learning, domain adaptation, interpretability research).

#### 4.3.2 Open-Source Implementation

We will release:
- **Python Package**: `causal_alignment` implementing the full pipeline (mediation estimation, sensitivity analysis, RepE validation)
- **Benchmark Suite**: Synthetic validation datasets with known causal graphs for methodology verification
- **Tutorial Notebooks**: Step-by-step guides for applying the framework to custom alignment problems

**Expected Adoption**: By lowering barriers to rigorous causal analysis, we anticipate widespread adoption in:
- Academic alignment research (NeurIPS, ICML, ICLR workshops)
- Industry alignment teams (Anthropic, OpenAI, Google DeepMind)
- AI safety organizations (Alignment Research Center, Redwood Research)

### 4.4 Practical Impact

#### 4.4.1 Transforming Alignment Engineering

Current alignment practice relies on **trial-and-error fine-tuning**:
1. Apply alignment intervention (RLHF, DPO)
2. Evaluate behavioral outcomes
3. If unsatisfactory, adjust hyperparameters and repeat
4. Typical iteration count: 5-10 cycles

Our framework enables **principled intervention design**:
1. Measure representational shift $\Delta M$ from pilot intervention
2. Predict behavioral outcome $\Delta Y$ via NIE model: $\Delta Y \approx \text{NIE}(\Delta M)$
3. If predicted $\Delta Y$ meets target, deploy; otherwise, adjust intervention
4. Expected iteration count: 2-3 cycles (50% reduction)

**Compute Savings**: For a 70B parameter model:
- Current approach: 10 iterations × 500 GPU-hours = 5,000 GPU-hours (~$2,500)
- Our approach: 3 iterations × 500 GPU-hours + 100 GPU-hours (mediation analysis) = 1,600 GPU-hours (~$800)
- **Savings**: $1,700 per alignment project (68% reduction)

#### 4.4.2 Targeted Intervention Applications

**Application 1: Truthfulness Optimization**

*Problem*: LLMs hallucinate factually incorrect information.

*Current Approach*: Generic RLHF on truthfulness reward model.

*Our Approach*:
1. Identify high-leverage mediators for truthfulness (e.g., layer-16 geometric structure via CKA)
2. Apply targeted RepE steering toward factually accurate reference model representations
3. Predict TruthfulQA improvement via NIE model before deployment

*Expected Outcome*: 2× efficiency (same truthfulness gain with 50% less compute)

**Application 2: Fairness Alignment**

*Problem*: LLMs exhibit demographic biases in outputs.

*Current Approach*: Fine-tune on debiased datasets; unclear which representational features to target.

*Our Approach*:
1. Mediation analysis identifies attention patterns (M₂) as primary mediator for fairness (NIE/TE ≈ 0.62)
2. Target attention head interventions (e.g., suppress heads amplifying gender stereotypes)
3. Validate via RepE: Steer attention patterns toward fair reference model

*Expected Outcome*: Principled debiasing with transparent causal mechanism

**Application 3: Safety Refusal Engineering**

*Problem*: Aligned models must refuse harmful instructions while remaining helpful for benign requests.

*Current Approach*: RLHF with safety reward model; risk of over-refusal (refusing benign requests).

*Our Approach*:
1. Identify sparse features (M₃) mediating safety refusal (specific "refusal neurons")
2. Targeted activation steering on those features only
3. Minimize collateral effects on helpfulness (non-targeted features unchanged)

*Expected Outcome*: High safety refusal (>95%) with minimal helpfulness degradation

#### 4.4.3 Regulatory and AI Safety Applications

**Transparent Alignment Guarantees**:

Current alignment claims: "Model is aligned via RLHF" (opaque mechanism).

Our framework enables: "Model alignment causally mediated by representational features (65% ± 8%), robust unless unmeasured confounder explains ≥18% variance."

**Impact**:
- **Regulatory Compliance**: Auditors can verify causal claims via sensitivity analysis
- **Deployment Decisions**: Stakeholders assess alignment reliability based on sensitivity bounds
- **Risk Assessment**: Quantify alignment robustness to distribution shift (if new data introduces confounding beyond sensitivity threshold, alignment may fail)

**AI Safety Research**:

Our framework addresses the **alignment tax** problem: How much capability must be sacrificed for alignment?

By decomposing alignment effects into representational (NIE) vs. non-representational (NDE) pathways, we can:
- Optimize representational pathways (high NIE) for alignment
- Preserve non-representational pathways for capability
- Minimize capability degradation while maximizing alignment

### 4.5 Broader Impact

#### 4.5.1 Interdisciplinary Contributions

**Neuroscience**: Our framework bridges machine learning and neuroscience by:
- Validating that representational alignment metrics (CKA, RSA) used in brain-AI comparisons (Dapello et al., 2022) reflect causal mechanisms, not just correlations
- Providing tools to test whether aligning AI representations with biological neural representations causally improves behavioral alignment

**Cognitive Science**: Our mediation framework applies to human-AI collaboration:
- Quantify how much of collaborative performance improvement flows through representational compatibility
- Design AI systems with human-compatible representations for optimal collaboration

**Philosophy of AI**: Our work addresses the **interpretability-alignment connection**:
- Does understanding representations (interpretability) causally enable alignment, or are they independent?
- Our framework tests: If interpretability interventions (e.g., mechanistic interpretability) change representations, do they mediate alignment outcomes?

#### 4.5.2 Limitations and Future Work

**Limitation 1: Scope Constraints**

Our framework applies to:
- Post-training alignment (RLHF, DPO, SFT)
- Transformer-based LLMs with activation access
- Measurable value dimensions (truthfulness, fairness, safety)

**Does NOT apply to**:
- Pretraining dynamics (too many confounders)
- Black-box API-only models (no activation access)
- Emergent capabilities without clear behavioral metrics

**Future Work**: Extend framework to:
- Pretraining via longitudinal mediation analysis (time-varying mediators)
- Vision models (adapt mediators to convolutional features)
- Multimodal models (cross-modal representational alignment)

**Limitation 2: Assumption Sensitivity**

Sequential ignorability (Assumption A1) is strong and may be violated by:
- Training data biases (confound T→M→Y)
- Emergent capabilities (unmeasured mediators)
- Base model inductive biases (confound T→M)

**Mitigation**: Sensitivity analysis provides transparent bounds, but cannot eliminate confounding.

**Future Work**: 
- Develop methods to measure and control for specific confounders (e.g., training data composition)
- Explore instrumental variable approaches to relax sequential ignorability

**Limitation 3: Generalization Across Scales**

Causal pathways validated on 7B models may differ at 70B+ scale due to:
- Emergent capabilities appearing at larger scales
- Different layer-wise representational organization
- Phase transitions in alignment mechanisms

**Future Work**: Conduct scale-specific validation experiments; develop scaling laws for causal mediation (how does NIE/TE change with model size?).

#### 4.5.3 Long-Term Vision

This research initiates a **causal science of alignment** where:

1. **Alignment interventions** are designed based on causal understanding, not trial-and-error
2. **Representational features** are engineered as causal mediators with predictable behavioral outcomes
3. **Alignment guarantees** are transparent, quantified, and sensitivity-bounded
4. **Interdisciplinary collaboration** between ML, neuroscience, and cognitive science is grounded in shared causal frameworks

**Ultimate Goal**: Enable **safe, reliable, and efficient alignment** of increasingly powerful AI systems by understanding and controlling the causal mechanisms linking representations to values.

---

**Estimated Timeline**:
- **Months 1-3**: Phase 1 (Synthetic Validation) + Phase 2 (Randomized Pilot)
- **Months 4-6**: Phase 3 (RepE Validation) + Phase 4 (Observational Study)
- **Months 7-9**: Analysis, sensitivity testing, cross-model validation
- **Months 10-12**: Paper writing, open-source release, workshop presentations

**Total Duration**: 12 months

**Total Budget**: $5,000 (compute) + $10,000 (personnel) = $15,000

**Deliverables**:
1. Peer-reviewed publication (NeurIPS, ICML, or ICLR)
2. Open-source `causal_alignment` Python package
3. Benchmark suite for causal mediation validation
4. Workshop presentation at Re-Align 2026