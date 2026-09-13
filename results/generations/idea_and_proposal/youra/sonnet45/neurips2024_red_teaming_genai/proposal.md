# Research Proposal: ImmuneLM - Immune-Inspired Two-Tier Defense Against Multi-Turn LLM Jailbreaks

## 1. Title

**ImmuneLM: A Biologically-Inspired Two-Tier Architecture for Detecting Multi-Turn Jailbreak Attacks in Large Language Models Through Conversational Memory and Semantic Drift Analysis**

## 2. Introduction

### 2.1 Background

The rapid deployment of Large Language Models (LLMs) in production chatbot systems has introduced critical security vulnerabilities that threaten user safety and organizational liability. While significant progress has been made in detecting single-turn jailbreak attacks—malicious prompts designed to bypass safety guardrails—recent research reveals a fundamental gap in current defense mechanisms: the inability to detect sophisticated multi-turn attacks that gradually manipulate conversations from benign to harmful content.

Recent benchmarks demonstrate the severity of this vulnerability. The RACE (Recursive Adversarial Conversation Evolution) framework achieves an 82% attack success rate (ASR) on GPT-4 using carefully crafted multi-turn state machines that progressively shift conversational context. Similarly, the MM-ART (Multi-Modal Adversarial Red Teaming) benchmark shows that LLMs become 71% more vulnerable after five conversational turns compared to single-turn interactions. These findings expose a critical architectural deficiency: existing defenses operate statelessly, evaluating each prompt independently without tracking conversational evolution over time.

Current state-of-the-art defenses like JBShield achieve impressive 95% accuracy on single-turn jailbreak detection through concept activation vectors extracted from LLM hidden states. However, when applied to multi-turn scenarios, these defenses only flag individual harmful turns—typically the final turn when the jailbreak has already succeeded—rather than detecting the gradual semantic drift that precedes the attack completion. This reactive approach leaves production chatbots critically exposed to adversaries who exploit conversational context to circumvent safety mechanisms.

The theoretical foundation for addressing this gap exists in an unexpected domain: biological immune systems. Natural immune systems employ a two-tier architecture combining innate immunity (fast pattern recognition receptors for immediate threats) and adaptive immunity (memory-based systems tracking pathogen evolution over time). This architectural principle, optimized through billions of years of evolution, provides a compelling blueprint for LLM defense systems that must similarly balance rapid response with temporal threat tracking.

### 2.2 Research Objectives

This research proposes **ImmuneLM**, a novel two-tier defense architecture that addresses the multi-turn jailbreak detection gap through biologically-inspired design principles and temporal semantic analysis. The primary objectives are:

**Objective 1: Develop a stateful defense architecture** that tracks conversational state evolution across multiple turns, enabling detection of gradual semantic drift from benign to harmful content before jailbreak completion.

**Objective 2: Validate the immune system analogy** by implementing a two-tier system combining fast single-turn concept activation screening (Tier 1: innate immunity analog) with LSTM-based conversational memory tracking (Tier 2: adaptive immunity analog).

**Objective 3: Achieve quantifiable performance improvements** of ≥20% attack success rate reduction on multi-turn benchmarks (RACE, MM-ART) compared to single-turn baselines, while maintaining ≤5% false positive rates and ≤500ms per-turn latency suitable for production deployment.

**Objective 4: Establish a reproducible methodology** for constructing attack pattern libraries from automated red teaming datasets (PyRIT, DeepTeam) and integrating human adversarial evaluation to ensure generalization beyond synthetic attacks.

### 2.3 Research Significance

This research makes three categories of contributions with significant theoretical, methodological, and practical implications:

**Theoretical Significance:** ImmuneLM introduces the first formal framework for stateful LLM defense, conceptualizing multi-turn jailbreaks as temporal trajectories in semantic space rather than static prompt features. This paradigm shift enables rigorous analysis of attack progression dynamics and optimal intervention points. The principled application of biological immune system architecture to LLM security establishes a new research direction in bio-inspired AI safety mechanisms, moving beyond ad-hoc metaphors to systematic architectural transfer.

**Methodological Significance:** The proposed hybrid architecture combining concept activation vectors with LSTM temporal modeling represents the first integration of interpretable semantic features with sequential deep learning for LLM defense. The hybrid feature approach—concatenating concept vectors with raw turn embeddings—addresses error propagation in multi-stage ML systems, providing a reusable engineering pattern for robust pipeline design. The attack pattern library construction methodology bridges academic benchmarking and industry practice, enabling continuous defense improvement as new attack vectors emerge.

**Practical Significance:** ImmuneLM directly addresses urgent industry needs for chatbot safety in production systems deployed by OpenAI, Anthropic, Microsoft, and other major providers. The ≥20% ASR reduction target translates to preventing thousands of successful jailbreaks in high-volume deployments. With medium implementation difficulty (1-2 GPUs, standard deep learning frameworks) and production-feasible latency (<500ms), the system lowers barriers to adoption for both research labs and industry teams. The integration with automated red teaming infrastructure (PyRIT, DeepTeam) provides a practical pathway for organizations to operationalize continuous security testing.

The research aligns with the workshop's core questions by: (1) identifying multi-turn semantic drift as an emerging security risk, (2) providing quantitative evaluation through controlled benchmarks and human adversarial testing, (3) proposing a concrete mitigation strategy through the two-tier architecture, (4) acknowledging limitations including adaptive adversary scenarios and multimodal attack extensions, and (5) establishing falsification criteria that enable rigorous assessment of safety claims.

## 3. Methodology

### 3.1 Research Design Overview

The research follows a five-phase experimental design: (0) Phase 0 validates the foundational assumption that concept activation vectors contain sufficient temporal signal; (1-2) Phases 1-2 implement and train the two-tier architecture; (3) Phase 3 conducts controlled benchmark evaluation; (4) Phase 4 performs human adversarial testing; (5) Phase 5 analyzes robustness and failure modes. This section details the complete methodology.

### 3.2 Data Collection and Preparation

**3.2.1 Attack Datasets**

We construct a comprehensive multi-turn attack corpus from four sources:

1. **RACE Dataset** (N≈500): Multi-turn attack state machines targeting GPT-4, with labeled state transitions (benign → intermediate → harmful). Each conversation contains 3-15 turns with ground-truth attack progression annotations.

2. **MM-ART Dataset** (N≈300): Multilingual multi-turn attacks spanning 5-10 turns, including cross-lingual semantic drift patterns.

3. **PyRIT Synthetic Attacks** (N≈1000): Automatically generated multi-turn conversations using the PyRIT (Python Risk Identification Toolkit) framework, with controlled variation in attack strategies (role-playing, context manipulation, gradual escalation).

4. **Human Red Team Attacks** (N≈100): Adversarial conversations generated by security researchers instructed to jailbreak target LLMs through multi-turn interactions, providing naturalistic attack patterns.

**3.2.2 Benign Datasets**

To establish false positive baselines, we use:

1. **DailyDialog** (N≈1000): Multi-turn everyday conversations covering 10 topics, providing realistic benign conversational patterns.

2. **PersonaChat** (N≈500): Persona-conditioned dialogues with 5-15 turns, capturing diverse conversational styles.

**3.2.3 Data Preprocessing**

For each conversation $C = \{t_1, t_2, ..., t_n\}$ with $n$ turns:

1. **Tokenization**: Apply target LLM tokenizer (e.g., GPT-4 tiktoken, Llama-3 tokenizer)
2. **Turn Segmentation**: Separate user and assistant turns, maintaining temporal ordering
3. **Label Assignment**: For attack datasets, annotate each turn with attack state $s_i \in \{benign, intermediate, harmful\}$
4. **Train/Val/Test Split**: 60%/20%/20% stratified by turn count (3-5, 6-10, 11-20) and attack type

### 3.3 ImmuneLM Architecture

**3.3.1 Tier 1: Innate Immunity (Fast Concept Activation Screening)**

Tier 1 replicates and extends JBShield's concept activation approach for per-turn screening:

**Step 1: Concept Direction Extraction**

For target LLM with hidden dimension $d$, extract concept directions via linear probing:

$$\mathbf{w}_{toxic} = \arg\min_{\mathbf{w}} \sum_{i=1}^{N_{train}} \mathcal{L}(y_i^{toxic}, \sigma(\mathbf{w}^T \mathbf{h}_i))$$

$$\mathbf{w}_{jailbreak} = \arg\min_{\mathbf{w}} \sum_{i=1}^{N_{train}} \mathcal{L}(y_i^{jailbreak}, \sigma(\mathbf{w}^T \mathbf{h}_i))$$

where $\mathbf{h}_i \in \mathbb{R}^d$ is the LLM hidden state for prompt $i$, $y_i^{toxic}, y_i^{jailbreak} \in \{0,1\}$ are binary labels, $\sigma$ is sigmoid activation, and $\mathcal{L}$ is binary cross-entropy loss.

**Step 2: Per-Turn Concept Activation**

For conversation turn $t_j$ with hidden state $\mathbf{h}_j$:

$$a_j^{toxic} = \sigma(\mathbf{w}_{toxic}^T \mathbf{h}_j)$$

$$a_j^{jailbreak} = \sigma(\mathbf{w}_{jailbreak}^T \mathbf{h}_j)$$

$$\mathbf{c}_j = [a_j^{toxic}, a_j^{jailbreak}] \in \mathbb{R}^2$$

**Step 3: Single-Turn Decision**

Flag turn $t_j$ if:

$$\max(a_j^{toxic}, a_j^{jailbreak}) > \theta_1$$

where $\theta_1$ is calibrated to achieve 95% single-turn accuracy (matching JBShield baseline).

**3.3.2 Tier 2: Adaptive Immunity (LSTM Conversational Memory)**

Tier 2 models temporal evolution of concept activations across conversation turns:

**Step 1: Hybrid Feature Construction**

For turn $t_j$, construct hybrid input combining concept activations and raw embeddings:

$$\mathbf{x}_j = [\mathbf{c}_j; \mathbf{e}_j] \in \mathbb{R}^{2+d_{embed}}$$

where $\mathbf{e}_j \in \mathbb{R}^{d_{embed}}$ is the mean-pooled token embedding for turn $t_j$, and $d_{embed} = 768$ (e.g., BERT-base dimension for computational efficiency).

**Step 2: LSTM Sequential Modeling**

Process conversation sequence through LSTM:

$$\mathbf{h}_j^{LSTM}, \mathbf{c}_j^{LSTM} = \text{LSTM}(\mathbf{x}_j, \mathbf{h}_{j-1}^{LSTM}, \mathbf{c}_{j-1}^{LSTM})$$

where $\mathbf{h}_j^{LSTM} \in \mathbb{R}^{d_{hidden}}$ is the LSTM hidden state, $\mathbf{c}_j^{LSTM}$ is the cell state, and $d_{hidden} \in \{64, 128\}$ (determined via ablation study).

**Step 3: Attack Pattern Library Matching**

Construct attack pattern library $\mathcal{P} = \{\mathbf{p}_1, ..., \mathbf{p}_K\}$ where each pattern $\mathbf{p}_k$ is a prototypical LSTM hidden state trajectory for known attack types (extracted via k-means clustering on training attack trajectories with $K=20$ clusters).

For current conversation state $\mathbf{h}_j^{LSTM}$, compute minimum distance to attack patterns:

$$d_j^{attack} = \min_{k=1,...,K} ||\mathbf{h}_j^{LSTM} - \mathbf{p}_k||_2$$

**Step 4: Temporal Decision**

Flag conversation at turn $j$ if:

$$d_j^{attack} < \theta_2$$

where $\theta_2$ is calibrated on validation set to achieve ≤5% false positive rate.

**3.3.3 Two-Tier Integration**

Final decision combines both tiers:

$$\text{Flag}(C, j) = \begin{cases} 
\text{True} & \text{if Tier 1 flags turn } j \text{ OR Tier 2 flags conversation at turn } j \\
\text{False} & \text{otherwise}
\end{cases}$$

This OR-logic ensures Tier 1 catches obvious single-turn attacks while Tier 2 detects gradual multi-turn drift.

### 3.4 Training Procedure

**3.4.1 Tier 1 Training**

1. **Dataset**: Single-turn toxic/jailbreak labeled prompts (N≈10,000 from existing benchmarks)
2. **Optimization**: Adam optimizer, learning rate $\alpha = 10^{-3}$, batch size 32, 10 epochs
3. **Validation**: Achieve ≥95% accuracy on held-out single-turn test set (matching JBShield)

**3.4.2 Tier 2 Training**

1. **Dataset**: Multi-turn conversations with turn-level attack state labels
2. **Loss Function**: Binary cross-entropy on conversation-level attack classification:

$$\mathcal{L}_{LSTM} = -\frac{1}{N} \sum_{i=1}^{N} [y_i \log(\hat{y}_i) + (1-y_i) \log(1-\hat{y}_i)]$$

where $y_i \in \{0,1\}$ indicates if conversation $i$ is an attack, and $\hat{y}_i = \sigma(\mathbf{w}_{cls}^T \mathbf{h}_{final}^{LSTM})$ is the prediction from final LSTM hidden state.

3. **Optimization**: Adam optimizer, learning rate $\alpha = 10^{-4}$, batch size 16, gradient clipping at norm 1.0, 20 epochs with early stopping (patience=3)
4. **Regularization**: Dropout 0.3 on LSTM outputs, L2 weight decay $\lambda = 10^{-5}$

**3.4.3 Attack Pattern Library Construction**

1. **Trajectory Extraction**: For each training attack conversation, extract LSTM hidden state sequence $\{\mathbf{h}_1^{LSTM}, ..., \mathbf{h}_n^{LSTM}\}$
2. **Clustering**: Apply k-means clustering (K=20) on final hidden states to identify attack archetypes
3. **Prototype Selection**: Store cluster centroids as attack patterns $\mathcal{P}$

### 3.5 Experimental Validation

**3.5.1 Phase 0: Concept-Attack Correlation Validation**

**Objective**: Verify that per-turn concept activation vectors correlate with attack progression.

**Procedure**:
1. Extract concept activation sequences $\{\mathbf{c}_1, ..., \mathbf{c}_n\}$ for RACE attack conversations
2. Compute Pearson correlation between concept activation magnitude $||\mathbf{c}_j||$ and attack state progression (benign=0, intermediate=0.5, harmful=1)
3. **Success Criterion**: Correlation $\rho \geq 0.6$
4. **Fallback**: If $\rho < 0.6$, validate hybrid features $[\mathbf{c}_j; \mathbf{e}_j]$ achieve $\rho \geq 0.5$

**3.5.2 Phase 1-2: Architecture Implementation and Training**

**Objective**: Implement ImmuneLM and train on multi-turn attack corpus.

**Procedure**:
1. Implement Tier 1 concept extraction pipeline (PyTorch)
2. Implement Tier 2 LSTM architecture with hybrid features
3. Train on combined dataset (RACE + MM-ART + PyRIT + human red team)
4. Hyperparameter tuning on validation set: $d_{hidden} \in \{64, 128, 256\}$, $\theta_2 \in [0.1, 0.5]$

**3.5.3 Phase 3: Benchmark Evaluation**

**Objective**: Quantify performance on standardized multi-turn attack benchmarks.

**Metrics**:

1. **Attack Success Rate (ASR)**: Proportion of attacks that successfully jailbreak without being flagged:

$$ASR = \frac{\text{Successful Attacks}}{\text{Total Attacks}}$$

2. **ASR Reduction**: Relative improvement over baseline:

$$ASR_{reduction} = \frac{ASR_{baseline} - ASR_{ImmuneLM}}{ASR_{baseline}}$$

3. **False Positive Rate (FPR)**: Proportion of benign conversations incorrectly flagged:

$$FPR = \frac{FP}{FP + TN}$$

4. **Detection Latency**: 95th percentile per-turn inference time (ms)

5. **Early Detection Rate**: Proportion of attacks flagged before final harmful turn:

$$EDR = \frac{\text{Attacks flagged at turn } j < n}{\text{Total detected attacks}}$$

**Experimental Conditions**:

1. **Baseline**: JBShield applied per-turn independently (stateless)
2. **ImmuneLM Variants**: Tier 1 only, Tier 2 only, Tier 1+2 combined
3. **Benchmarks**: RACE (N=100 held-out attacks), MM-ART (N=60 held-out)
4. **Stratification**: By turn count (3-5, 6-10, 11-20 turns)

**Statistical Testing**:

1. **Primary Test**: Paired t-test comparing $ASR_{baseline}$ vs. $ASR_{ImmuneLM}$ on same attack set
   - Null hypothesis $H_0$: $\mu_{ASR_{reduction}} \leq 0$
   - Alternative $H_1$: $\mu_{ASR_{reduction}} > 0$
   - Significance threshold: $p < 0.05$

2. **Robustness**: Bootstrap confidence intervals (1000 resamples) for ASR reduction estimate

**3.5.4 Phase 4: Human Adversarial Evaluation**

**Objective**: Validate generalization to naturalistic human attacks.

**Procedure**:
1. **Red Team Recruitment**: 10 security researchers with LLM jailbreaking experience
2. **Attack Protocol**: Each researcher conducts 10 multi-turn jailbreak attempts (3-15 turns) against GPT-4 protected by ImmuneLM
3. **Blinding**: Researchers unaware of specific defense mechanisms
4. **Success Criteria**: Attack succeeds if harmful output generated without flagging
5. **Evaluation Metrics**: ASR on human attacks, comparison to automated attack ASR

**Expected Outcome**: Human attack ASR ≥ 70% (demonstrating generalization beyond synthetic patterns)

**3.5.5 Phase 5: Robustness and Ablation Studies**

**Ablation Experiments**:

1. **LSTM Hidden Dimension**: Compare $d_{hidden} \in \{32, 64, 128, 256\}$ on validation ASR
2. **Feature Ablation**: Concept-only vs. embedding-only vs. hybrid input
3. **Pattern Library Size**: Vary $K \in \{5, 10, 20, 50\}$ attack patterns
4. **Turn Count Sensitivity**: Performance vs. conversation length

**Robustness Experiments**:

1. **Tier 1 Error Injection**: Simulate concept extraction errors by adding Gaussian noise $\mathcal{N}(0, \sigma^2)$ to $\mathbf{c}_j$, measure Tier 2 degradation
2. **LLM Version Stability**: Test concept direction transfer across GPT-4 checkpoints (0613 vs. 1106)
3. **Adversarial Robustness**: Evaluate against adaptive attacks with white-box access to ImmuneLM architecture (future work preview)

### 3.6 Implementation Details

**Computational Requirements**:
- **Hardware**: 1-2 NVIDIA A100 GPUs (40GB VRAM)
- **Software**: PyTorch 2.0, HuggingFace Transformers, Python 3.10
- **Training Time**: ~48 hours for full pipeline (Tier 1: 4 hours, Tier 2: 40 hours, pattern library: 4 hours)
- **Inference Latency Budget**: <500ms per turn (Tier 1: ~100ms, Tier 2: ~400ms)

**Reproducibility**:
- Public code repository (GitHub) with documented random seeds
- Model checkpoints released on HuggingFace Hub
- Dataset construction scripts and preprocessing pipelines
- Experiment configuration files (YAML) for all ablations

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Quantified Multi-Turn Defense Improvement**

We expect ImmuneLM to achieve ≥20% relative ASR reduction on RACE and MM-ART benchmarks compared to JBShield baseline, translating to:
- RACE: ASR reduction from 82% → ≤66%
- MM-ART: ASR reduction from baseline → ≤20% improvement

This improvement will be statistically significant (p < 0.05) with 95% confidence intervals excluding zero effect.

**Primary Outcome 2: Production-Feasible Performance Profile**

The system will maintain:
- False positive rate ≤5% on benign dialogues (DailyDialog, PersonaChat)
- 95th percentile latency ≤500ms per turn on NVIDIA A100
- Early detection rate ≥60% (flagging attacks before final harmful turn)

**Primary Outcome 3: Generalization to Human Attacks**

Human adversarial evaluation will demonstrate ≥70% detection rate on naturalistic attacks, validating that patterns learned from automated red teaming (PyRIT, RACE) transfer to creative human adversaries.

**Secondary Outcome 1: Validated Immune System Analogy**

Ablation studies will confirm the two-tier architecture's necessity:
- Tier 1 alone: Matches JBShield single-turn performance but fails on gradual multi-turn attacks
- Tier 2 alone: Detects multi-turn drift but misses obvious single-turn attacks
- Tier 1+2 combined: Achieves superior performance across attack types

**Secondary Outcome 2: Hybrid Feature Robustness**

Error injection experiments will demonstrate that hybrid features $[\mathbf{c}_j; \mathbf{e}_j]$ maintain ≥90% of clean performance when Tier 1 concept extraction error rate reaches 20%, while concept-only features degrade >30%.

**Secondary Outcome 3: Temporal Sensitivity Characterization**

Analysis will reveal that ImmuneLM's advantage over single-turn baselines increases with conversation length, with maximum benefit at 6-10 turns (the "sweet spot" where attacks are gradual enough to evade single-turn detection but not so long that Tier 1 eventually flags them).

### 4.2 Theoretical Impact

**Paradigm Shift in LLM Defense Architecture**

ImmuneLM establishes stateful defense as a fundamental requirement for conversational AI security, shifting research focus from static prompt analysis to temporal trajectory modeling. This framework enables:

1. **Formal Analysis of Attack Dynamics**: Conceptualizing jailbreaks as state machines in semantic space allows rigorous study of attack progression, optimal intervention points, and theoretical detection limits.

2. **Cross-Domain Transfer Validation**: Successful application of biological immune principles to LLM security validates bio-inspired AI safety as a productive research direction, potentially inspiring defenses against other temporal threats (e.g., gradual model poisoning, slow-burn data exfiltration).

3. **Multi-Stage Defense Theory**: The hybrid feature approach contributes to broader ML systems engineering by demonstrating error-tolerant pipeline design through parallel information flow.

### 4.3 Methodological Impact

**Reusable Defense Infrastructure**

The research delivers:

1. **Open-Source Implementation**: Production-ready PyTorch codebase enabling rapid deployment and extension by industry practitioners and researchers.

2. **Attack Pattern Library Methodology**: Systematic approach for constructing and updating attack pattern databases from automated red teaming tools, bridging research and operational security.

3. **Evaluation Protocol**: Standardized benchmark suite combining automated attacks (RACE, MM-ART, PyRIT) and human adversarial testing, establishing best practices for multi-turn defense evaluation.

### 4.4 Practical Impact

**Industry Deployment Pathway**

ImmuneLM's medium implementation difficulty and production-feasible performance profile enable immediate adoption:

1. **Chatbot Safety Enhancement**: Organizations deploying conversational AI (customer service, education, healthcare) can integrate ImmuneLM as an external guardrail, reducing jailbreak risk by ≥20% without model retraining.

2. **Cost-Benefit Analysis**: At $50K research cost and 6-month development timeline, the system is accessible to mid-size organizations. For high-volume deployments (1M conversations/day), preventing 20% of jailbreaks translates to thousands of safety incidents avoided.

3. **Regulatory Compliance**: As AI safety regulations emerge (EU AI Act, US Executive Order 14110), ImmuneLM provides auditable defense mechanisms with quantified performance metrics, supporting compliance documentation.

**Red Teaming Ecosystem Integration**

The research strengthens the red teaming feedback loop:

1. **Automated Testing Acceleration**: Integration with PyRIT and DeepTeam enables continuous security testing, reducing manual red team burden.

2. **Defense-Attack Co-Evolution**: Attack pattern library updates create a systematic process for incorporating new attack discoveries, preventing defense obsolescence.

3. **Benchmark Contribution**: Evaluation datasets and protocols contribute to community benchmarks, enabling standardized comparison of future defense systems.

### 4.5 Limitations and Future Work

**Known Limitations**:

1. **Adaptive Adversary Assumption**: Current design assumes attackers lack white-box access to ImmuneLM architecture. Future work must address adversarial robustness against adaptive attacks.

2. **Text-Only Scope**: Multimodal jailbreaks (image/audio manipulation) require architecture extensions, potentially incorporating vision/speech encoders into Tier 2.

3. **LLM Version Dependency**: Concept directions require retraining on major LLM updates, necessitating operational procedures for version migration.

**Future Research Directions**:

1. **Theoretical Guarantees**: Develop formal bounds on detection probability as a function of attack gradualness (semantic drift rate).

2. **Multimodal Extension**: Extend LSTM to process multimodal conversational features, addressing image-based jailbreaks.

3. **Federated Defense Learning**: Enable collaborative attack pattern library construction across organizations while preserving privacy.

4. **Explainable Interventions**: Develop interpretability methods to explain why specific conversations were flagged, supporting human-in-the-loop review.

### 4.6 Alignment with Workshop Goals

This research directly addresses the workshop's fundamental questions:

- **New Security Risks**: Identifies multi-turn semantic drift as an emerging threat vector requiring stateful defenses.
- **Quantitative Evaluation**: Provides rigorous benchmarking methodology combining automated and human adversarial testing.
- **Risk Mitigation**: Delivers concrete defense system with validated performance improvements.
- **Red Teaming Limitations**: Acknowledges adaptive adversary scenarios and multimodal attack gaps.
- **Safety Guarantees**: Establishes falsification criteria and statistical validation protocols, moving toward principled safety claims.

The expected ≥20% ASR reduction, if achieved, represents a significant step toward safer conversational AI systems, while the open-source implementation and evaluation protocols contribute lasting infrastructure for the AI safety research community.