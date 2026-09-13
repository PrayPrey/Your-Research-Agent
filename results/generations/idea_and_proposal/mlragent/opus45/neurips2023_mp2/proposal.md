# Research Proposal: Moral Foundations-Aware Alignment (MFAA): Bridging Moral Psychology and Pluralistic Value Alignment in Large Language Models

## 1. Introduction

### Background

The rapid deployment of Large Language Models (LLMs) across diverse global contexts has intensified concerns about whose values these systems embody. Current alignment methodologies, particularly Reinforcement Learning from Human Feedback (RLHF), rely heavily on human annotators to provide preference signals that shape model behavior. However, these annotator pools are often demographically homogeneous, drawing predominantly from Western, Educated, Industrialized, Rich, and Democratic (WEIRD) populations. This creates a fundamental tension: systems designed to serve humanity broadly are calibrated to reflect narrow moral perspectives while claiming universal alignment.

Recent research has begun documenting this limitation. Ali et al. (2025) demonstrated systematic demographic effects in alignment data, revealing trade-offs between safety, inclusivity, and model behavior when incorporating preferences from different social groups. Abdulhai et al. (2023) analyzed LLMs through the lens of Moral Foundations Theory (MFT), exposing significant biases in moral values and political affiliations that influence downstream task performance. These findings underscore the urgent need for alignment frameworks that can accommodate moral pluralism rather than suppress it.

Moral Foundations Theory, developed by Jonathan Haidt and colleagues in moral psychology, offers a principled framework for understanding cross-cultural moral diversity. MFT posits six foundational moral intuitions—Care/Harm, Fairness/Cheating, Loyalty/Betrayal, Authority/Subversion, Sanctity/Degradation, and Liberty/Oppression—that vary in emphasis across cultures, political orientations, and individual moral profiles. This theoretical foundation provides a structured vocabulary for diagnosing and addressing the monolithic value problem in AI systems.

### Research Objectives

This research proposes **Moral Foundations-Aware Alignment (MFAA)**, a comprehensive framework that integrates MFT into the LLM alignment pipeline. The specific objectives are:

1. **Develop a diagnostic tool** that profiles LLM outputs across the six moral foundations, enabling systematic identification of over- and under-represented moral perspectives.

2. **Create a stratified feedback dataset** where annotators are recruited and categorized according to their moral foundation profiles, ensuring balanced representation across the moral spectrum.

3. **Design a pluralistic reward modeling approach** that learns foundation-specific reward functions, enabling nuanced value representation rather than collapsing diverse moral perspectives into a single optimization signal.

4. **Implement and evaluate a steerable alignment system** capable of generating responses calibrated to different moral frameworks or explicitly acknowledging moral trade-offs.

### Significance

This research addresses critical gaps identified in the literature. While recent work like COUPLE (Guo et al., 2025) has explored counterfactual reasoning for value steerability, and MoralCLIP (Condez et al., 2025) has integrated MFT into multimodal learning, no existing framework comprehensively applies MFT across the entire alignment pipeline—from data collection through reward modeling to inference-time steering. MFAA provides this end-to-end integration, offering both theoretical grounding from moral psychology and practical methodological innovations for ethical AI development.

## 2. Methodology

### 2.1 Phase 1: Moral Foundations Diagnostic Tool

#### Data Collection

We will construct a diagnostic evaluation dataset by curating 5,000 morally-relevant scenarios across diverse domains including healthcare, governance, interpersonal relationships, environmental issues, and economic decisions. Each scenario will be annotated by trained moral philosophers for relevance to each of the six moral foundations using a multi-label scheme.

#### Moral Foundation Classifier

We will develop a multi-label classifier $f_{\text{MF}}: \mathcal{X} \rightarrow [0,1]^6$ that maps textual content to foundation activation scores. The classifier will be built on a fine-tuned transformer architecture with the following training objective:

$$\mathcal{L}_{\text{classifier}} = -\sum_{i=1}^{N}\sum_{j=1}^{6} \left[ y_{ij} \log(\sigma(f_{\text{MF}}(x_i)_j)) + (1-y_{ij}) \log(1-\sigma(f_{\text{MF}}(x_i)_j)) \right]$$

where $y_{ij} \in \{0,1\}$ indicates whether foundation $j$ is relevant to sample $i$, and $\sigma$ denotes the sigmoid function.

#### LLM Profiling Protocol

To profile an LLM's moral foundation distribution, we generate responses to a standardized set of 1,000 morally-charged prompts $\mathcal{P} = \{p_1, ..., p_{1000}\}$. For each prompt, we sample $k=5$ responses and compute the aggregate foundation profile:

$$\text{Profile}(M) = \frac{1}{|\mathcal{P}| \cdot k} \sum_{p \in \mathcal{P}} \sum_{r \in R_p} f_{\text{MF}}(r)$$

where $R_p$ denotes the set of responses generated for prompt $p$. We quantify foundation imbalance using the normalized entropy:

$$H_{\text{norm}} = -\frac{1}{\log 6} \sum_{j=1}^{6} \hat{p}_j \log \hat{p}_j$$

where $\hat{p}_j$ is the normalized activation for foundation $j$. Lower entropy indicates more imbalanced foundation representation.

### 2.2 Phase 2: Stratified Feedback Dataset Construction

#### Annotator Recruitment and Profiling

We will recruit 600 annotators stratified across three dimensions:
- **Geographic diversity**: 200 participants each from North America, South/Southeast Asia, and Sub-Saharan Africa
- **Political orientation**: Balanced representation of conservative, moderate, and liberal perspectives
- **Moral foundation profiles**: Measured using the validated 30-item Moral Foundations Questionnaire (MFQ-30)

Each annotator will complete the MFQ-30, yielding individual moral profiles $\mathbf{m}_a \in \mathbb{R}^6$ representing their relative endorsement of each foundation.

#### Preference Data Collection

Annotators will evaluate 50 pairs of LLM responses each, for a total of 30,000 pairwise comparisons. For each comparison, annotators indicate which response they prefer and rate the importance of each moral foundation to their judgment. This yields preference data of the form:

$$\mathcal{D} = \{(x_i, y_i^+, y_i^-, \mathbf{m}_{a_i}, \mathbf{w}_i)\}_{i=1}^{30000}$$

where $x_i$ is the prompt, $y_i^+$ and $y_i^-$ are the preferred and dispreferred responses, $\mathbf{m}_{a_i}$ is the annotator's moral profile, and $\mathbf{w}_i \in \mathbb{R}^6$ captures the self-reported foundation relevance weights for that judgment.

### 2.3 Phase 3: Pluralistic Reward Modeling

#### Foundation-Specific Reward Functions

Rather than training a single reward model, we train six foundation-specific reward models $\{R_j\}_{j=1}^{6}$, each capturing preferences particularly relevant to one moral foundation. For foundation $j$, we weight training samples by the product of annotator foundation endorsement and judgment relevance:

$$w_{ij} = m_{a_i,j} \cdot w_{i,j}$$

The foundation-specific reward model is trained using weighted Bradley-Terry loss:

$$\mathcal{L}_j = -\sum_{i=1}^{N} w_{ij} \log \sigma\left(R_j(x_i, y_i^+) - R_j(x_i, y_i^-)\right)$$

#### Composite Reward with Configurable Weights

At inference time, the composite reward for a response $y$ to prompt $x$ is computed as:

$$R_{\text{composite}}(x, y; \boldsymbol{\alpha}) = \sum_{j=1}^{6} \alpha_j R_j(x, y)$$

where $\boldsymbol{\alpha} = (\alpha_1, ..., \alpha_6)$ with $\sum_j \alpha_j = 1$ represents the desired moral foundation weighting. This enables steering toward specific moral frameworks or balanced pluralistic representation.

#### Training the Aligned Model

We fine-tune the base LLM using Proximal Policy Optimization (PPO) with the composite reward. The objective is:

$$\mathcal{L}_{\text{PPO}} = \mathbb{E}_{x \sim \mathcal{P}, y \sim \pi_\theta(y|x)} \left[ R_{\text{composite}}(x, y; \boldsymbol{\alpha}) - \beta \cdot \text{KL}(\pi_\theta \| \pi_{\text{ref}}) \right]$$

where $\pi_\theta$ is the policy being optimized, $\pi_{\text{ref}}$ is the reference policy, and $\beta$ controls the KL divergence penalty.

### 2.4 Phase 4: Steerable Generation and Trade-off Acknowledgment

#### Moral Foundation Steering

We implement inference-time steering through foundation-weighted decoding:

$$P(y_t | y_{<t}, x, \boldsymbol{\alpha}) \propto P_{\text{base}}(y_t | y_{<t}, x) \cdot \exp\left(\gamma \sum_{j=1}^{6} \alpha_j \cdot s_j(y_{\leq t})\right)$$

where $s_j(\cdot)$ is a foundation-specific scoring function derived from the reward models, and $\gamma$ controls steering strength.

#### Trade-off Transparency Module

For prompts where different foundations suggest conflicting responses, we implement a trade-off detection mechanism. Given foundation-specific response candidates $\{y^{(j)}\}_{j=1}^{6}$, we compute the foundation disagreement score:

$$D(x) = 1 - \frac{2}{6 \cdot 5} \sum_{j < k} \text{cos}(R_j(x, \cdot), R_k(x, \cdot))$$

When $D(x) > \tau$ (threshold), the system generates responses that explicitly acknowledge moral trade-offs, presenting considerations from conflicting foundations.

### 2.5 Experimental Design and Evaluation

#### Baselines

We compare MFAA against:
1. Standard RLHF with homogeneous annotator pool
2. COUPLE (Guo et al., 2025) counterfactual reasoning approach
3. Steerable Pluralism (Adams et al., 2025) few-shot method
4. CultureSPA (2025) self-pluralising approach

#### Evaluation Metrics

1. **Foundation Balance Score (FBS)**: Measures evenness of moral foundation representation:
$$\text{FBS} = H_{\text{norm}}(\text{Profile}(M))$$

2. **Cross-Cultural Preference Alignment (CCPA)**: Measures alignment with held-out annotators from each cultural group:
$$\text{CCPA}_g = \mathbb{E}_{a \in g}\left[\text{Accuracy}(R_{\text{composite}}, \text{Prefs}_a)\right]$$

3. **Steerability Index (SI)**: Quantifies the model's ability to shift foundation emphasis under different $\boldsymbol{\alpha}$ configurations:
$$\text{SI} = \frac{1}{6}\sum_{j=1}^{6} \text{corr}(\alpha_j, \text{Profile}(M; \boldsymbol{\alpha})_j)$$

4. **Trade-off Recognition Accuracy (TRA)**: Measures correct identification of morally contested scenarios, evaluated against expert annotations.

5. **Safety and Helpfulness**: Standard benchmarks including ToxiGen, BBQ, and MT-Bench to ensure alignment improvements don't compromise core capabilities.

#### Human Evaluation

We conduct human evaluation with 300 participants (balanced across cultural and political demographics) rating model outputs on:
- Perceived fairness of moral representation
- Appropriateness of trade-off acknowledgments
- Overall response quality and helpfulness

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Diagnostic Insights**: A comprehensive analysis of moral foundation distributions in major LLMs (GPT-4, Claude, Llama), quantifying specific biases and underrepresented moral perspectives.

2. **Open-Source Resources**: 
   - Moral Foundations diagnostic toolkit and classifier
   - Stratified preference dataset with 30,000 annotated comparisons
   - Foundation-specific reward models

3. **Empirical Findings**: Quantitative evidence demonstrating:
   - Improved Foundation Balance Scores (target: >0.85 normalized entropy vs. <0.70 for baselines)
   - Higher cross-cultural preference alignment (target: >15% improvement across all cultural groups)
   - Effective steerability (target: SI >0.80)

4. **Methodological Contributions**: A validated framework for incorporating moral psychology theory into alignment pipelines, applicable beyond MFT to other psychological frameworks.

### Broader Impact

**For AI Development Practice**: MFAA provides practitioners with concrete tools to diagnose and address value homogeneity in their systems. The foundation-specific reward modeling approach offers a principled alternative to current homogenizing practices.

**For Interdisciplinary Research**: This work demonstrates how theoretical frameworks from moral psychology can directly inform technical AI methodology, encouraging deeper collaboration between AI researchers, moral philosophers, and psychologists.

**For AI Governance**: By making embedded values transparent and steerable, MFAA supports regulatory efforts requiring AI systems to document and justify their value commitments.

**For Global AI Equity**: Systems developed using MFAA will better serve diverse global populations rather than privileging majority perspectives, contributing to more equitable AI deployment.

### Limitations and Future Work

We acknowledge that MFT, while well-validated, is not universally accepted in moral psychology, and some foundations may be more culturally specific than the theory suggests. Future work should explore integration with complementary frameworks such as Schwartz's Theory of Basic Human Values. Additionally, the steerable approach raises questions about potential misuse for manipulative purposes, requiring careful consideration of deployment safeguards.

This research represents a significant step toward AI systems that respect and reflect the genuine diversity of human moral reasoning, moving beyond superficial claims of alignment toward substantive moral pluralism.