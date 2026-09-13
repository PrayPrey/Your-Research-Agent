# Research Proposal: Temporal Drift Detection for Human-AI Trust Calibration in Healthcare Decision Support

## 1. Introduction

### Background

The integration of artificial intelligence (AI) into healthcare decision support systems has transformed clinical practice, with AI-powered diagnostic tools now assisting clinicians in radiology, pathology, dermatology, and numerous other specialties. While these systems demonstrate impressive standalone performance on benchmark evaluations, their real-world effectiveness depends fundamentally on how clinicians interact with and respond to AI recommendations over extended periods. This longitudinal dimension of human-AI collaboration introduces complex coevolutionary dynamics that current evaluation frameworks fail to capture.

When clinicians repeatedly interact with AI diagnostic systems over months or years, both parties undergo subtle but consequential adaptations. Clinicians may develop automation bias—an over-reliance on AI recommendations that diminishes critical evaluation—or alternatively, algorithm aversion that leads to systematic underutilization of valuable AI insights. Simultaneously, AI systems that incorporate feedback from clinician decisions may drift toward confirming existing human biases, creating reinforcing loops that progressively degrade diagnostic accuracy. These bidirectional adaptation patterns constitute what we term "coevolutionary drift," a phenomenon that can systematically erode care quality without either party recognizing the shift.

Current approaches to human-AI collaboration in healthcare predominantly focus on point-in-time evaluations: measuring AI accuracy, assessing initial user trust, or evaluating explanation quality at specific moments. The literature review reveals significant advances in trust-adaptive interventions (Srinivasan & Thomason, 2025), interface design optimization (Chen et al., 2025), and trust calibration strategies leveraging correctness likelihoods (Ma et al., 2023). However, these approaches largely treat human-AI interaction as static episodes rather than evolving relationships. The temporal dynamics of trust calibration and the detection of systematic drift patterns remain critically underexplored, representing a significant gap in ensuring sustainable, high-quality human-AI collaboration in healthcare.

### Research Objectives

This research proposes developing and validating a **Coevolutionary Drift Monitor (CDM)** framework designed to continuously track, quantify, and address bidirectional adaptation patterns between clinicians and AI diagnostic systems. The specific objectives are:

1. To develop computational methods for modeling clinician trust trajectories from sequential decision data, enabling identification of emerging over-reliance and under-reliance patterns before they become clinically significant.

2. To create techniques for detecting AI recommendation drift by comparing current system outputs against established baselines, quantifying the degree and direction of systematic shifts.

3. To design and validate intervention mechanisms that trigger appropriately when drift metrics exceed calibrated thresholds, providing targeted recalibration strategies.

4. To demonstrate framework effectiveness through longitudinal simulation and prospective pilot deployment in a radiology decision support context.

### Significance

This research directly addresses the HAIC 2025 workshop's focus on dynamic feedback loops in socially impactful domains and bidirectional learning beyond performance metrics. By providing practical tools for detecting and addressing coevolutionary drift, this work offers healthcare institutions mechanisms for ensuring sustained human-AI collaboration quality. The framework contributes novel metrics for trust miscalibration, early warning systems for problematic adaptation patterns, and evidence-based recalibration interventions—advancing both theoretical understanding of human-AI coevolution and practical implementation of safer AI-assisted healthcare.

## 2. Methodology

### 2.1 Overall Framework Architecture

The Coevolutionary Drift Monitor (CDM) framework comprises four interconnected modules: (1) Clinician Trust Trajectory Modeling, (2) AI Recommendation Drift Detection, (3) Integrated Drift Assessment, and (4) Adaptive Intervention System. These modules operate continuously during human-AI collaboration, processing decision data to detect emerging drift patterns and trigger appropriate interventions.

### 2.2 Clinician Trust Trajectory Modeling

#### Data Collection

For each clinical decision episode $t$, we collect a feature vector $\mathbf{x}_t$ comprising:
- AI recommendation confidence: $c_t^{AI} \in [0,1]$
- Clinician's final decision: $d_t^{clin} \in \{0,1\}$ (accept/reject AI recommendation)
- Time spent reviewing case: $\tau_t$
- Explanation interaction depth: $e_t$ (clicks, hovers on explanation elements)
- Case complexity indicators: $\mathbf{k}_t$
- Diagnostic outcome (when available): $y_t$

#### Trust State Estimation

We model clinician trust as a latent state $\theta_t$ evolving according to a state-space model:

$$\theta_t = f(\theta_{t-1}, \mathbf{x}_{t-1}, \epsilon_t)$$

where $f(\cdot)$ is a transition function capturing trust dynamics and $\epsilon_t$ represents stochastic variation. The observable acceptance behavior follows:

$$P(d_t^{clin} = 1 | \theta_t, c_t^{AI}, \mathbf{k}_t) = \sigma(\beta_0 + \beta_1 \theta_t + \beta_2 c_t^{AI} + \boldsymbol{\beta}_3^T \mathbf{k}_t)$$

where $\sigma(\cdot)$ is the sigmoid function. We employ a particle filter approach to estimate the posterior distribution $P(\theta_t | \mathbf{x}_{1:t})$ at each time step, maintaining uncertainty quantification essential for reliable drift detection.

#### Reliance Pattern Classification

From the trust trajectory, we compute reliance metrics within sliding windows of $W$ decisions:

**Over-reliance score:**
$$OR_t = \frac{1}{|S_t^{incorrect}|} \sum_{i \in S_t^{incorrect}} \mathbb{1}[d_i^{clin} = 1]$$

where $S_t^{incorrect}$ denotes cases in the window where AI recommendations were subsequently determined incorrect.

**Under-reliance score:**
$$UR_t = \frac{1}{|S_t^{correct}|} \sum_{i \in S_t^{correct}} \mathbb{1}[d_i^{clin} = 0]$$

where $S_t^{correct}$ denotes cases where AI recommendations were correct.

We detect drift toward problematic reliance using change-point detection:

$$\Delta OR_t = OR_t - \bar{OR}_{baseline}, \quad \Delta UR_t = UR_t - \bar{UR}_{baseline}$$

Alert thresholds are established through bootstrap analysis of baseline clinician behavior during an initial calibration period.

### 2.3 AI Recommendation Drift Detection

#### Baseline Establishment

We maintain a held-out reference dataset $\mathcal{D}_{ref}$ comprising cases representative of the clinical distribution, with ground truth labels determined through expert consensus or follow-up confirmation. At regular intervals, we evaluate current AI system outputs on this reference set.

#### Drift Quantification

For classification tasks, we measure recommendation drift using:

**Distributional Shift:**
$$D_{KL}(P_{ref} || P_t) = \sum_{c} P_{ref}(c) \log \frac{P_{ref}(c)}{P_t(c)}$$

where $P_{ref}$ and $P_t$ are the distributions of AI confidence scores on the reference dataset at baseline and time $t$, respectively.

**Accuracy Drift:**
$$\Delta Acc_t = Acc_{baseline}(\mathcal{D}_{ref}) - Acc_t(\mathcal{D}_{ref})$$

**Bias Amplification Index:**

For protected attributes $A$ (e.g., patient demographics), we compute:

$$BAI_t = \frac{|FPR_t^{A=1} - FPR_t^{A=0}|}{|FPR_{baseline}^{A=1} - FPR_{baseline}^{A=0}|}$$

where values exceeding 1.0 indicate amplification of pre-existing biases.

### 2.4 Integrated Drift Assessment

We combine clinician and AI drift metrics into a unified assessment using a multivariate control chart approach. Define the drift vector:

$$\mathbf{D}_t = [OR_t, UR_t, D_{KL,t}, \Delta Acc_t, BAI_t]^T$$

The integrated drift score uses Hotelling's $T^2$ statistic:

$$T^2_t = (\mathbf{D}_t - \boldsymbol{\mu}_{baseline})^T \mathbf{S}_{baseline}^{-1} (\mathbf{D}_t - \boldsymbol{\mu}_{baseline})$$

where $\boldsymbol{\mu}_{baseline}$ and $\mathbf{S}_{baseline}$ are the mean vector and covariance matrix estimated during the baseline period. Control limits are established at the 95th and 99th percentiles under baseline conditions.

### 2.5 Adaptive Intervention System

When drift metrics exceed thresholds, the CDM triggers targeted interventions:

**Tier 1 (Yellow Alert: $T^2_t > T^2_{95}$):**
- Personalized AI explanations emphasizing uncertainty for clinicians showing over-reliance
- Performance feedback summaries showing recent accuracy patterns
- "Trust-resetting cases": deliberately selected cases where AI recommendations diverge from ground truth to recalibrate expectations

**Tier 2 (Red Alert: $T^2_t > T^2_{99}$):**
- Mandatory cognitive forcing functions requiring explicit justification before accepting/rejecting AI recommendations
- Scheduled recalibration sessions with curated case sets
- System-level review triggering potential AI model recalibration

The intervention selection follows a decision tree incorporating the dominant drift component identified through contribution analysis of the $T^2$ decomposition.

### 2.6 Validation Study Design

#### Phase 1: Longitudinal Simulation Study

We will construct a simulation environment using retrospective data from a chest X-ray interpretation dataset (MIMIC-CXR or similar), comprising approximately 200,000 images with radiologist reports. The simulation includes:

- **Synthetic Clinician Agents**: Behavioral models calibrated to empirical trust dynamics from published human-AI interaction studies, with parameters governing trust updating, attention allocation, and decision thresholds
- **AI System with Drift Injection**: A diagnostic classifier with controllable drift mechanisms (concept drift, feedback loop bias amplification)
- **Outcome Model**: Ground truth determination based on held-out expert consensus

We will simulate 50 clinician-AI dyads over 12 simulated months (approximately 500 cases per clinician), systematically varying drift injection parameters and evaluating CDM detection performance.

**Evaluation Metrics:**
- Drift detection sensitivity and specificity
- Time-to-detection (number of decisions before drift identified)
- False alarm rate under stable conditions
- Intervention effectiveness (recovery of baseline reliance patterns)

#### Phase 2: Prospective Pilot Study

Following simulation validation, we will conduct a 6-month pilot deployment in a radiology department focusing on chest radiograph interpretation for pneumonia detection.

**Participants**: 12-16 radiologists with varying experience levels

**Design**: Within-subject crossover with CDM-enabled (intervention) and standard AI assistance (control) periods, counterbalanced across participants

**Primary Outcomes**:
- Trust calibration accuracy: correlation between clinician reliance and AI correctness
- Diagnostic accuracy on consensus-labeled validation cases
- Clinician-reported workload and system usability (NASA-TLX, SUS)

**Secondary Outcomes**:
- Intervention trigger frequency and type distribution
- Qualitative feedback on intervention acceptability
- Observed drift patterns and trajectory characteristics

**Statistical Analysis**: Mixed-effects models accounting for clinician random effects and temporal autocorrelation, with primary hypothesis testing at $\alpha = 0.05$ following pre-registration.

## 3. Expected Outcomes & Impact

### Expected Outcomes

This research is expected to produce several concrete deliverables:

1. **Validated CDM Framework**: A fully specified and tested system for continuous drift monitoring in clinical AI decision support, with documented implementation requirements and deployment guidelines.

2. **Drift Metrics Suite**: Novel quantitative metrics for measuring trust miscalibration ($OR_t$, $UR_t$), AI recommendation drift ($D_{KL}$, $BAI$), and integrated coevolutionary drift ($T^2$), with established baseline distributions and threshold calibration procedures.

3. **Intervention Toolkit**: Evidence-based intervention strategies matched to specific drift patterns, including personalized explanation templates, cognitive forcing function designs, and trust-resetting case selection algorithms.

4. **Empirical Insights**: Quantitative characterization of coevolutionary drift dynamics in healthcare AI, including typical trajectory patterns, drift timescales, and intervention effectiveness estimates.

We anticipate demonstrating that CDM can detect clinically meaningful drift patterns with sensitivity exceeding 80% while maintaining false alarm rates below 10%, with time-to-detection averaging under 50 decision episodes.

### Broader Impact

This work contributes to the nascent field of Human-AI Coevolution in several significant ways:

**Theoretical Contributions**: The framework advances understanding of bidirectional adaptation dynamics, providing formal models for trust evolution and drift quantification that extend beyond healthcare to other high-stakes human-AI collaboration contexts.

**Practical Tools**: Healthcare institutions adopting AI decision support systems currently lack mechanisms for detecting degradation in human-AI collaboration quality over time. CDM provides actionable monitoring capabilities, addressing a critical gap in AI safety infrastructure.

**Methodological Advancement**: By demonstrating evaluation approaches that capture temporal dynamics rather than static snapshots, this work contributes to the workshop's goal of moving beyond traditional performance benchmarks toward holistic assessment of human-AI systems.

**Policy Relevance**: As regulatory frameworks increasingly require ongoing monitoring of AI systems in healthcare (as noted in the literature review regarding global AI governance), CDM provides a technical foundation for compliance with emerging post-deployment surveillance requirements.

**Ethical Implications**: By detecting and addressing coevolutionary drift toward bias amplification or inappropriate trust, the framework contributes to ensuring that AI-assisted healthcare maintains fairness and quality over extended deployment periods.

The successful completion of this research will establish a paradigm for sustainable human-AI collaboration in healthcare, providing both theoretical frameworks and practical tools for ensuring that the benefits of AI diagnostic support endure throughout the coevolutionary journey of clinicians and AI systems working together.