# Research Proposal: Coevolution Trajectory Metric: Quantifying Bidirectional Human-AI Adaptation via Temporal Contrastive Learning

## 1. Introduction

### 1.1 Background

The rapid proliferation of AI systems across critical domains—healthcare, education, criminal justice, and creative industries—has fundamentally transformed how humans interact with intelligent technologies. Unlike traditional software tools that remain static, modern AI systems, particularly those employing reinforcement learning from human feedback (RLHF) and continuous fine-tuning, adapt to user preferences over time. Simultaneously, humans modify their behaviors, expectations, and cognitive strategies in response to AI capabilities and limitations. This bidirectional adaptation process, termed Human-AI Coevolution (HAIC), represents a paradigm shift from viewing human-AI interaction as a unidirectional relationship to understanding it as a coupled dynamical system with emergent feedback loops.

Current evaluation paradigms in AI research predominantly focus on unidirectional metrics: AI performance benchmarks (accuracy, perplexity, task completion rates) or user-centric measures (satisfaction scores, trust ratings, usability metrics). While valuable, these approaches fundamentally miss the coupled nature of sustained human-AI interaction. When a user interacts with a coding assistant over months, both parties change: the AI may adapt its response style to the user's preferences, while the user develops new query formulation strategies, calibrates trust, and potentially alters their problem-solving approaches. Existing metrics cannot capture this mutual adaptation, leaving researchers and practitioners without tools to understand, measure, or optimize coevolutionary dynamics.

This gap has significant implications for high-stakes domains. In healthcare, prolonged physician-AI collaboration may shape diagnostic reasoning patterns in ways that current evaluation frameworks cannot detect. In education, student-AI tutoring relationships may produce cognitive adaptations that influence learning outcomes beyond immediate task performance. Without principled methods to quantify bidirectional adaptation, we cannot design AI systems that coevolve beneficially with users or identify potentially harmful feedback loops before they manifest.

### 1.2 Research Objectives

This research proposes the **Coevolution Trajectory Metric (CTM)**, a novel computational framework for quantifying bidirectional human-AI adaptation in sustained interaction contexts. Our primary objectives are:

1. **Develop a unified measurement framework** that captures both AI representation drift and human behavioral adaptation within a shared embedding space, enabling direct comparison of heterogeneous adaptation signals.

2. **Validate the CTM framework** through empirical studies demonstrating that computed coevolution scores correlate meaningfully with task performance improvements and collaboration quality.

3. **Establish falsification criteria** that rigorously test the underlying assumptions of the framework, ensuring scientific validity and identifying boundary conditions.

4. **Provide actionable insights** for designing AI systems that promote beneficial coevolution while mitigating risks of harmful feedback loops.

### 1.3 Significance

This research addresses a critical gap identified by the HAIC research community: the need for evaluation metrics that move "beyond AI performance benchmarks" to capture the dynamic, bidirectional nature of human-AI relationships. The CTM framework offers several significant contributions:

- **Theoretical Contribution:** Formalizes bidirectional coevolution as a measurable phenomenon, providing a mathematical foundation for studying coupled human-AI adaptation.
- **Methodological Innovation:** Introduces temporal contrastive learning as a mechanism for aligning heterogeneous signals (neural representations and behavioral patterns) into a unified metric space.
- **Practical Impact:** Enables practitioners to monitor coevolution dynamics in deployed systems, informing design decisions and identifying intervention points.
- **Safety Implications:** Provides tools for detecting potentially harmful feedback loops before they produce adverse outcomes in high-stakes domains.

## 2. Methodology

### 2.1 Overview of the CTM Framework

The Coevolution Trajectory Metric operates through three interconnected components: (1) AI representation drift tracking via Centered Kernel Alignment (CKA), (2) human behavioral adaptation capture through multi-proxy feature extraction, and (3) unified embedding space construction via temporal contrastive learning. The final CTM score combines trajectory alignment and coupling coefficient measures computed within this shared space.

### 2.2 Component 1: AI Representation Drift Tracking

**Centered Kernel Alignment (CKA)** provides a principled method for comparing neural network representations across different conditions. For an AI model with hidden layer activations, we extract representation matrices before and after user-specific interaction sessions.

Let $H_t^{(l)} \in \mathbb{R}^{n \times d}$ denote the hidden state activations at layer $l$ for $n$ input samples at time $t$. The CKA similarity between representations at times $t_1$ and $t_2$ is computed as:

$$\text{CKA}(H_{t_1}, H_{t_2}) = \frac{\text{HSIC}(K_{t_1}, K_{t_2})}{\sqrt{\text{HSIC}(K_{t_1}, K_{t_1}) \cdot \text{HSIC}(K_{t_2}, K_{t_2})}}$$

where $K_t = H_t H_t^T$ is the Gram matrix and HSIC (Hilbert-Schmidt Independence Criterion) is computed as:

$$\text{HSIC}(K, L) = \frac{1}{(n-1)^2} \text{tr}(\tilde{K}\tilde{L})$$

with $\tilde{K} = CKC$ being the centered kernel matrix and $C = I - \frac{1}{n}\mathbf{1}\mathbf{1}^T$.

For each user $u$ and session $s$, we compute the AI adaptation signal:

$$\alpha_u^{(s)} = 1 - \text{CKA}(H_{\text{pre}}^{(s)}, H_{\text{post}}^{(s)})$$

where lower CKA similarity (higher $\alpha$) indicates greater representation drift, suggesting stronger adaptation to the user.

### 2.3 Component 2: Human Behavioral Adaptation Capture

Human adaptation is captured through a multi-proxy feature vector extracted from interaction logs. For each session $s$, we compute:

1. **Query Complexity ($q_c$):** Average sentence length (ASL) of user queries, normalized to [0,1] based on observed range (5-25 words).

2. **Response Latency ($r_l$):** Mean time between AI response delivery and subsequent user action, normalized from observed range (500-5000ms).

3. **Correction Frequency ($c_f$):** Proportion of AI responses that receive explicit user corrections or regeneration requests.

4. **Trust Calibration Actions ($t_a$):** Count of trust-related behaviors (accepting suggestions without modification, requesting explanations, overriding recommendations), normalized per session.

The human behavioral feature vector for user $u$ at session $s$ is:

$$\beta_u^{(s)} = [q_c^{(s)}, r_l^{(s)}, c_f^{(s)}, t_a^{(s)}] \in \mathbb{R}^4$$

To capture adaptation rather than static behavior, we compute the behavioral change signal:

$$\Delta\beta_u^{(s)} = \beta_u^{(s)} - \beta_u^{(s-1)}$$

### 2.4 Component 3: Temporal Contrastive Learning for Unified Embedding

The core innovation of CTM is projecting heterogeneous AI and human signals into a shared embedding space using temporal contrastive learning. This approach leverages the insight that same-session AI states and human behaviors are temporally coupled and should be represented proximally.

**Encoder Architecture:**
- AI encoder $f_\theta: \mathbb{R}^{d_\alpha} \rightarrow \mathbb{R}^{d_e}$ maps CKA-derived features to embedding space
- Human encoder $g_\phi: \mathbb{R}^4 \rightarrow \mathbb{R}^{d_e}$ maps behavioral features to the same embedding space

where $d_e = 128$ is the embedding dimension.

**Contrastive Learning Objective:**
We employ the InfoNCE loss with temporal pairing. For a batch of $N$ user-session pairs, same-session AI-human pairs serve as positives:

$$\mathcal{L}_{\text{InfoNCE}} = -\frac{1}{N}\sum_{i=1}^{N} \log \frac{\exp(\text{sim}(z_i^\alpha, z_i^\beta)/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(z_i^\alpha, z_j^\beta)/\tau)}$$

where $z_i^\alpha = f_\theta(\alpha_u^{(s_i)})$, $z_i^\beta = g_\phi(\Delta\beta_u^{(s_i)})$, $\text{sim}(\cdot,\cdot)$ denotes cosine similarity, and $\tau = 0.07$ is the temperature parameter.

### 2.5 CTM Score Computation

Within the trained embedding space, CTM computes two complementary metrics:

**Trajectory Alignment Score (TAS):**
For a user $u$ with $S$ sessions, we compute the temporal trajectories:

$$T_u^\alpha = [z_u^{\alpha,(1)}, z_u^{\alpha,(2)}, ..., z_u^{\alpha,(S)}]$$
$$T_u^\beta = [z_u^{\beta,(1)}, z_u^{\beta,(2)}, ..., z_u^{\beta,(S)}]$$

The trajectory alignment score measures directional consistency:

$$\text{TAS}_u = \frac{1}{S-1}\sum_{s=1}^{S-1} \text{cos}(\Delta z_u^{\alpha,(s)}, \Delta z_u^{\beta,(s)})$$

where $\Delta z^{(s)} = z^{(s+1)} - z^{(s)}$.

**Coupling Coefficient (CC):**
The coupling coefficient captures the cross-correlation between adaptation rates:

$$\text{CC}_u = \max_{\tau \in [-k, k]} \frac{\text{Cov}(\|\Delta z_u^\alpha\|, \|\Delta z_u^\beta\|_{\tau})}{\sigma_\alpha \sigma_\beta}$$

where $\|\Delta z_u^\beta\|_{\tau}$ represents the lagged adaptation rate signal and $k=3$ sessions.

**Final CTM Score:**

$$\text{CTM}_u = \frac{1}{2}(\text{TAS}_u + 1) \cdot \frac{1}{2}(\text{CC}_u + 1)$$

normalized to $[0, 1]$ where 0 indicates no coevolution and 1 indicates perfect coupled adaptation.

### 2.6 Experimental Design

#### 2.6.1 Data Collection

**Primary Dataset:** We will collect longitudinal interaction data from three task domains:
- **Creative Writing:** Users collaborating with an LLM on story generation (target: 50 users × 50 sessions)
- **Coding Assistance:** Developers using an AI coding assistant (target: 50 users × 50 sessions)
- **Question Answering:** Users engaging in information-seeking dialogues (target: 50 users × 50 sessions)

**Data Sources:**
1. **Existing Datasets:** LMSYS-Chat-1M and ShareGPT for initial validation (filtered for users with 10+ sessions)
2. **Controlled Study:** IRB-approved longitudinal study recruiting participants for sustained interaction over 8 weeks

**Logged Variables:**
- Complete interaction transcripts with timestamps
- AI model hidden state activations (extracted via hooks at layers 12, 24, 36 for a 48-layer model)
- User behavioral metrics (query text, response times, correction actions)
- Post-session surveys (cognitive adaptation self-assessment, trust calibration)

#### 2.6.2 Validation Experiments

**Experiment 1: CTM Validity (Primary Prediction P1)**
- **Objective:** Validate that CTM scores correlate with task performance improvement
- **Method:** Compute CTM for all user-AI pairs; correlate with domain-specific performance metrics
- **Performance Metrics:**
  - Creative Writing: Human evaluation of story quality improvement (1-5 scale)
  - Coding: Task completion accuracy and code quality metrics
  - Q&A: Answer accuracy and user satisfaction ratings
- **Analysis:** Pearson correlation with bootstrapped 95% confidence intervals
- **Success Criterion:** $r > 0.4$, $p < 0.05$

**Experiment 2: Proxy Validity (Secondary Prediction P2)**
- **Objective:** Validate behavioral proxies against self-reported cognitive changes
- **Method:** Correlate behavioral feature changes with post-session cognitive adaptation surveys
- **Success Criterion:** $r > 0.3$, $p < 0.05$

**Experiment 3: Embedding Space Quality (Secondary Prediction P3)**
- **Objective:** Verify contrastive learning produces meaningful temporal alignment
- **Method:** Compute silhouette scores for embeddings clustered by session quality
- **Success Criterion:** Silhouette score $> 0.3$

**Experiment 4: Ablation Studies**
- **Objective:** Validate each component's contribution to CTM effectiveness
- **Conditions:**
  - Full CTM vs. AI-only (no human behavioral signal)
  - Full CTM vs. Human-only (no CKA signal)
  - Full CTM vs. No contrastive alignment (direct concatenation)
- **Analysis:** Compare correlation with task performance across conditions

#### 2.6.3 Falsification Tests

The hypothesis will be rejected if:
1. CTM-performance correlation $r < 0.2$ or $p > 0.10$
2. CKA variance across sessions $< 0.01$ (insufficient AI adaptation signal)
3. Embedding space silhouette score $< 0.3$ (contrastive alignment failure)
4. Coupling coefficient shows no relationship with observed mutual adaptation

### 2.7 Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| CTM-Performance Correlation | Pearson $r$ between CTM and task improvement | $r > 0.4$ |
| Proxy Validity Correlation | Behavioral features vs. cognitive surveys | $r > 0.3$ |
| Embedding Silhouette Score | Clustering quality in shared space | $> 0.3$ |
| CKA Variance | Variability of AI representation drift | $> 0.01$ |
| Contrastive Loss Convergence | InfoNCE loss reduction during training | $< 0.5$ |

### 2.8 Implementation Details

- **Compute Resources:** Single NVIDIA A100 GPU (40GB) for CKA computation and contrastive training
- **Software Stack:** PyTorch 2.0, Hugging Face Transformers, custom CKA implementation
- **Training:** Adam optimizer, learning rate $10^{-4}$, batch size 256, 100 epochs
- **Statistical Analysis:** SciPy for correlations, scikit-learn for clustering metrics

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcomes:**
1. A validated CTM framework demonstrating measurable bidirectional coevolution in sustained human-AI interaction, with correlation coefficients exceeding $r = 0.4$ between CTM scores and task performance improvements.

2. Empirical evidence that temporal contrastive learning effectively aligns heterogeneous adaptation signals (neural representations and behavioral patterns) into a unified metric space.

3. Domain-specific insights into coevolution dynamics across creative writing, coding assistance, and question-answering contexts, identifying task-dependent patterns in human-AI mutual adaptation.

**Secondary Outcomes:**
1. Validated behavioral proxy measures for human cognitive adaptation, enabling non-invasive monitoring of user-side coevolution.

2. Open-source implementation of the CTM framework, including CKA computation modules, contrastive learning pipelines, and visualization tools.

3. Benchmark dataset of longitudinal human-AI interactions with ground-truth coevolution annotations.

### 3.2 Theoretical Impact

This research advances the theoretical understanding of human-AI coevolution by:
- Formalizing bidirectional adaptation as a measurable, quantifiable phenomenon
- Establishing temporal contrastive learning as a principled method for aligning heterogeneous adaptation signals
- Providing a mathematical framework for studying coupled dynamical systems in human-AI interaction

### 3.3 Practical Impact

**For AI System Designers:**
- CTM enables monitoring of coevolution dynamics in deployed systems, informing design decisions
- Identification of beneficial vs. harmful feedback loops before adverse outcomes manifest
- Guidance for designing AI systems that promote positive coevolution

**For High-Stakes Domains:**
- Healthcare: Monitoring physician-AI diagnostic coevolution to ensure beneficial adaptation
- Education: Tracking student-AI tutoring relationships to optimize learning outcomes
- Criminal Justice: Detecting potentially biased feedback loops in AI-assisted decision-making

**For AI Safety Research:**
- CTM provides early warning indicators for harmful coevolution patterns
- Enables intervention before feedback loops produce irreversible outcomes
- Supports development of AI alignment strategies grounded in empirical coevolution data

### 3.4 Limitations and Future Directions

**Known Limitations:**
- Proxy validity requires ongoing validation against ground-truth cognitive assessments
- Results may require domain-specific calibration for generalization
- Causal attribution requires controlled experiments beyond correlational validation

**Future Directions:**
1. Extension to multi-agent settings (multiple humans, multiple AI systems)
2. Real-time CTM computation for online monitoring and intervention
3. Integration with RLHF pipelines for coevolution-aware model training
4. Cross-cultural validation of behavioral proxies

### 3.5 Broader Impact

This research contributes to the emerging field of Human-AI Coevolution by providing the first principled framework for quantifying bidirectional adaptation. By moving beyond unidirectional performance metrics, CTM enables researchers and practitioners to understand, measure, and ultimately shape the feedback loops that emerge through sustained human-AI collaboration. As AI systems become increasingly integrated into critical societal functions, such tools are essential for ensuring that coevolution proceeds in directions that benefit both humans and society.