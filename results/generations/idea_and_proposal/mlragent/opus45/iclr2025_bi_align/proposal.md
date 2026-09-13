# Research Proposal: Adaptive Alignment Calibration: Learning When Humans Should Defer to AI vs. Override AI Decisions

## 1. Introduction

### Background

The rapid proliferation of general-purpose AI systems has fundamentally transformed how humans interact with intelligent technologies across high-stakes domains including healthcare, finance, autonomous driving, and legal decision-making. Traditional AI alignment research has predominantly adopted a unidirectional perspective—focusing on making AI systems conform to human values and preferences. However, this paradigm fails to capture the inherently dynamic, reciprocal nature of human-AI interaction. The emerging framework of bidirectional human-AI alignment recognizes that effective collaboration requires not only aligning AI with human specifications but also empowering humans to appropriately calibrate their trust and reliance on AI systems.

A critical yet underexplored challenge within this bidirectional framework concerns the calibration problem: determining when humans should defer to AI recommendations versus when human judgment should take precedence. Current research reveals concerning patterns at both extremes. Automation bias leads users to over-rely on AI systems, accepting recommendations uncritically even when human expertise would yield superior outcomes. Conversely, algorithm aversion causes users to under-trust capable AI systems, dismissing valuable assistance due to skepticism or misunderstanding of AI capabilities. As demonstrated by Li et al. (2024), both overconfident and underconfident AI systems exacerbate these problems, creating a cascading effect that undermines effective human-AI collaboration.

The challenge is further complicated by findings from Chen et al. (2025), who showed that revealing AI reasoning, while increasing trust, paradoxically crowds out unique human knowledge—suggesting that transparency alone is insufficient for achieving appropriate calibration. This tension between transparency and human agency preservation represents a fundamental gap in current bidirectional alignment approaches.

### Research Objectives

This research proposes the **Mutual Calibration Framework (MCF)**, a novel approach to adaptive alignment calibration that addresses the following primary objectives:

1. **Develop a meta-learning architecture** that enables AI systems to learn personalized deference policies for individual users, recognizing when to confidently provide recommendations versus when to explicitly defer to human judgment.

2. **Design adaptive interface mechanisms** that guide appropriate trust calibration by communicating AI uncertainty boundaries in ways that preserve rather than diminish human agency and expertise utilization.

3. **Establish a joint optimization objective** that simultaneously maximizes AI accuracy, human decision quality post-interaction, and appropriate reliance metrics—creating a unified framework for bidirectional calibration.

4. **Validate the framework** through comprehensive human-subjects experiments measuring both performance outcomes and calibration quality across diverse task contexts.

### Significance

This research addresses a critical gap in bidirectional alignment by reconceptualizing the human-AI boundary as dynamic and context-aware rather than fixed. The framework directly contributes to the workshop's dual focus: from the AI-centered perspective, it advances methods for training AI systems that can appropriately defer to human judgment; from the human-centered perspective, it empowers humans to critically evaluate AI capabilities and maintain meaningful agency. The practical implications extend to any domain where human-AI collaborative decision-making occurs, offering a principled approach to the fundamental question of when humans should trust versus override AI recommendations.

## 2. Methodology

### 2.1 Framework Architecture

The Mutual Calibration Framework comprises three integrated components: (1) an Uncertainty-Aware AI Module, (2) a Personalized Deference Policy Learner, and (3) an Adaptive Calibration Interface.

#### 2.1.1 Uncertainty-Aware AI Module

The foundation of MCF is an AI system capable of producing well-calibrated uncertainty estimates. Let $f_\theta(x)$ denote the AI model's prediction for input $x$ with parameters $\theta$. We employ an ensemble-based approach combined with learned calibration:

$$p(y|x) = \frac{1}{K}\sum_{k=1}^{K} f_{\theta_k}(x)$$

where $K$ ensemble members provide both predictive estimates and epistemic uncertainty quantification. The calibrated confidence $c(x)$ is computed as:

$$c(x) = \sigma\left(g_\phi\left([\mu(x), \sigma^2(x), h(x)]\right)\right)$$

where $\mu(x)$ and $\sigma^2(x)$ represent the ensemble mean and variance, $h(x)$ encodes task-specific features, $g_\phi$ is a learned calibration network, and $\sigma$ is the sigmoid function ensuring $c(x) \in [0,1]$.

#### 2.1.2 Personalized Deference Policy Learner

The core innovation of MCF is a meta-learning approach that learns when the AI should defer to human judgment. For each user $u$, we maintain a user expertise profile $e_u$ learned from interaction history. The deference policy $\pi_\psi(d|x, c(x), e_u)$ outputs a deference decision $d \in [0,1]$ indicating the degree to which the AI should recommend human override.

The policy is formulated as:

$$\pi_\psi(d|x, c(x), e_u) = \text{MLP}_\psi\left([x, c(x), e_u, \tau(x)]\right)$$

where $\tau(x)$ represents task context features. The user expertise profile is updated through a recurrent mechanism:

$$e_u^{(t+1)} = \text{GRU}_\omega\left(e_u^{(t)}, [x^{(t)}, y_{\text{human}}^{(t)}, y_{\text{AI}}^{(t)}, y_{\text{true}}^{(t)}]\right)$$

This enables the system to learn individualized models of when each user's judgment tends to outperform AI recommendations.

#### 2.1.3 Adaptive Calibration Interface

The interface component translates AI confidence and deference signals into human-interpretable guidance. Rather than simply displaying confidence scores, which can paradoxically increase over-reliance, we design adaptive explanations:

$$E(x) = \text{Generate}\left(x, c(x), \pi_\psi(d|x, c(x), e_u), R(x)\right)$$

where $R(x)$ represents relevant reasoning elements selected based on deference level. When deference is high ($d > \tau_{\text{high}}$), explanations emphasize uncertainty sources and invite human expertise; when deference is low ($d < \tau_{\text{low}}$), explanations provide supporting evidence for the AI recommendation.

### 2.2 Joint Optimization Objective

The key methodological contribution is a multi-objective loss function that jointly optimizes for AI accuracy, human decision quality, and calibration appropriateness:

$$\mathcal{L}_{\text{total}} = \lambda_1 \mathcal{L}_{\text{accuracy}} + \lambda_2 \mathcal{L}_{\text{calibration}} + \lambda_3 \mathcal{L}_{\text{reliance}} + \lambda_4 \mathcal{L}_{\text{deference}}$$

**Accuracy Loss**: Standard cross-entropy for AI prediction quality:
$$\mathcal{L}_{\text{accuracy}} = -\mathbb{E}_{(x,y)}\left[\log f_\theta(y|x)\right]$$

**Calibration Loss**: Expected Calibration Error ensuring confidence estimates match actual accuracy:
$$\mathcal{L}_{\text{calibration}} = \sum_{b=1}^{B} \frac{|B_b|}{n} \left|\text{acc}(B_b) - \text{conf}(B_b)\right|$$

**Reliance Loss**: A novel component measuring the appropriateness of human reliance patterns:
$$\mathcal{L}_{\text{reliance}} = \mathbb{E}\left[\mathbf{1}[y_{\text{AI}} = y_{\text{true}}] \cdot (1 - r) + \mathbf{1}[y_{\text{AI}} \neq y_{\text{true}}] \cdot r\right]$$

where $r$ is the observed human reliance rate. This loss penalizes under-reliance when AI is correct and over-reliance when AI errs.

**Deference Loss**: Encourages appropriate deference recommendations:
$$\mathcal{L}_{\text{deference}} = \mathbb{E}\left[(d - d^*)^2\right]$$

where $d^* = \mathbf{1}[y_{\text{human}} \succ y_{\text{AI}}]$ indicates whether human judgment was superior.

### 2.3 Training Procedure

**Phase 1: AI Module Pre-training**
Train the ensemble model and calibration network on standard supervised data, optimizing $\mathcal{L}_{\text{accuracy}} + \mathcal{L}_{\text{calibration}}$.

**Phase 2: Human Interaction Data Collection**
Conduct preliminary human studies to collect interaction data including human decisions, reliance patterns, and outcomes across varying AI confidence levels.

**Phase 3: Joint Optimization**
Using collected human interaction data, jointly optimize all components using the full $\mathcal{L}_{\text{total}}$ objective through alternating minimization:
1. Fix deference policy, update AI model and calibration network
2. Fix AI components, update deference policy using policy gradient methods
3. Update user expertise profiles based on accumulated interaction data

### 2.4 Experimental Design

#### Datasets and Tasks
We will evaluate MCF across three domains representing varying expertise requirements:
- **Medical Diagnosis**: Skin lesion classification (ISIC dataset) with simulated clinician expertise levels
- **Financial Forecasting**: Stock movement prediction with varying analyst experience
- **Image Classification**: CIFAR-100 with controlled difficulty manipulation

#### Participant Recruitment
We will recruit 200 participants through Prolific, stratified by domain expertise (novice, intermediate, expert) based on pre-screening assessments.

#### Experimental Conditions
1. **Baseline**: Standard AI system with confidence display
2. **Transparency+**: AI with detailed reasoning explanations
3. **MCF-Static**: Our framework without personalization
4. **MCF-Full**: Complete Mutual Calibration Framework

#### Evaluation Metrics

**Performance Metrics**:
- Joint Decision Accuracy: Accuracy of final human-AI collaborative decisions
- AI-Alone Accuracy: Baseline AI performance
- Human-Alone Accuracy: Human performance without AI assistance

**Calibration Metrics**:
- Appropriate Reliance Rate (ARR): $\frac{\text{Correct Agreements} + \text{Correct Overrides}}{\text{Total Decisions}}$
- Over-Reliance Rate: Frequency of accepting incorrect AI recommendations
- Under-Reliance Rate: Frequency of rejecting correct AI recommendations

**Trust Metrics**:
- Subjective Trust Scale (adapted from Jian et al., 2000)
- Perceived AI Competence
- Self-reported Decision Confidence

**Agency Metrics**:
- Unique Human Knowledge Utilization: Rate at which humans contribute information beyond AI input
- Override Appropriateness: Correlation between human overrides and AI errors

#### Statistical Analysis
We will employ mixed-effects models to account for repeated measures and individual differences, with expertise level and experimental condition as fixed effects and participant as a random effect. Effect sizes (Cohen's d) and confidence intervals will be reported alongside significance tests.

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Technical Contributions**:
1. A validated Mutual Calibration Framework that produces AI systems capable of learning personalized deference policies
2. A novel joint optimization objective balancing multiple alignment goals
3. Adaptive interface designs that communicate uncertainty while preserving human agency
4. Open-source implementation and pre-trained models for community use

**Empirical Findings**:
1. Quantified improvements in appropriate reliance rates compared to baseline approaches (hypothesized 15-25% improvement in ARR)
2. Evidence of reduced automation bias without inducing algorithm aversion
3. Demonstrated preservation of unique human knowledge utilization
4. Personalization effects showing adaptation to individual user expertise profiles

**Design Guidelines**:
1. Principles for communicating AI uncertainty that support rather than undermine human judgment
2. Recommendations for implementing deference mechanisms in deployed systems
3. Metrics and benchmarks for evaluating bidirectional calibration quality

### Broader Impact

This research directly addresses the workshop's core mission of fostering bidirectional human-AI alignment. By making the human-AI decision boundary dynamic and context-aware, MCF offers a principled approach to one of the most pressing practical challenges in AI deployment: ensuring that humans and AI systems collaborate effectively without sacrificing human agency.

**Scientific Impact**: The framework contributes to multiple disciplines—machine learning (meta-learning for human-AI interaction), HCI (adaptive interface design for trust calibration), and cognitive science (understanding human reliance decision-making).

**Societal Impact**: In high-stakes domains like healthcare and finance, inappropriate reliance on AI can have severe consequences. MCF provides tools for achieving appropriate calibration, potentially reducing both automation-induced errors and missed opportunities for beneficial AI assistance.

**Policy Implications**: The AI Autonomy Coefficient proposed by Mairittha et al. (2025) represents growing interest in quantifying human-AI balance. MCF provides concrete mechanisms for implementing such balance, informing regulatory frameworks requiring appropriate human oversight.

**Limitations and Ethical Considerations**: We acknowledge that personalized deference policies could potentially be exploited to manipulate user trust. We will develop safeguards ensuring transparency about the system's adaptive mechanisms and user control over personalization features. Additionally, the framework's effectiveness depends on accurate ground truth labels, which may be unavailable in some real-world contexts—a limitation we will explicitly address in deployment guidelines.

In conclusion, the Mutual Calibration Framework represents a significant step toward realizing the promise of bidirectional human-AI alignment by transforming the calibration problem from a static design choice into a dynamic, learnable, and personalized aspect of human-AI collaboration.