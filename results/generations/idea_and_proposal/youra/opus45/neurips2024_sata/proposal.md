# Research Proposal: Adaptive Safety Immune System (ASIS): A Three-Tier Bio-Inspired Framework for Reducing False Positives in LLM Agent Safety

## 1. Introduction

### 1.1 Background

Large Language Model (LLM) agents have rapidly evolved from simple text generators to sophisticated autonomous systems capable of executing complex tasks through tool use, web browsing, code execution, and API interactions. This evolution brings unprecedented capabilities but also introduces significant safety challenges. As these agents interact with real-world systems and make consequential decisions, ensuring their safe operation becomes paramount.

Current safety mechanisms for LLM agents predominantly rely on static guardrails—predefined rule sets, keyword filters, and fixed constraint libraries that attempt to block unsafe actions before execution. Systems such as TrustAgent and NeMo Guardrails represent the state-of-the-art in this domain, implementing various strategies from in-planning safety constraints to parallel guardrail orchestration. However, these approaches suffer from a fundamental limitation: their static nature leads to unacceptably high false positive rates.

Recent empirical studies reveal that static guardrails can exhibit false positive rates as high as 92%, blocking legitimate user actions and severely degrading user experience. While subsequent filtering can reduce this to approximately 6.3%, the computational overhead and user friction remain substantial. This creates a critical tension in agent safety: overly aggressive systems frustrate users and reduce utility, while permissive systems expose users to genuine risks.

The biological immune system offers an elegant solution to an analogous problem. Rather than relying solely on fixed responses, biological immunity operates through multiple tiers: innate immunity provides rapid, non-specific responses to common threats; adaptive immunity generates highly specific responses to novel pathogens; and immunological memory accelerates responses to previously encountered threats. This tiered architecture achieves remarkable precision in distinguishing genuine threats from benign stimuli while maintaining rapid response times.

Recent advances in understanding LLM internal representations provide a foundation for translating this biological insight to agent safety. Research on hidden state detection demonstrates that LLM activations encode safety-relevant signals, enabling tuning-free detection of unsafe prompts through activation pattern analysis. Simultaneously, work on dynamic constraint generation shows that safety constraints can be contextually generated rather than retrieved from fixed sets. However, no existing framework unifies these insights into a coherent, adaptive safety architecture.

### 1.2 Research Objectives

This research proposes the Adaptive Safety Immune System (ASIS), a three-tier bio-inspired framework designed to address the false positive problem in LLM agent safety. Our primary objectives are:

1. **Design and implement a three-tier adaptive safety architecture** comprising an innate detection layer for rapid risk scoring, an adaptive constraint generation layer for context-specific interventions, and an immune memory layer for accelerated handling of repeated threat patterns.

2. **Validate the hypothesis** that this tiered architecture reduces false positive rates by at least 30% compared to static guardrails while maintaining greater than 90% unsafe action prevention.

3. **Establish the causal mechanisms** underlying performance improvements through systematic ablation studies and mechanism verification experiments.

4. **Demonstrate practical viability** through latency analysis ensuring the system remains suitable for interactive agent deployment.

### 1.3 Significance

This research addresses a critical gap in the safe deployment of LLM agents. By reducing false positives while maintaining high threat prevention, ASIS would enable broader adoption of agentic AI systems in sensitive domains where both safety and usability are essential. The bio-inspired framework also contributes a novel conceptual lens for thinking about adaptive AI safety, potentially inspiring future research directions. Furthermore, the modular architecture allows individual components to be adopted independently, maximizing practical impact even if the full system proves unnecessary for certain applications.

## 2. Methodology

### 2.1 System Architecture Overview

ASIS implements a three-tier architecture inspired by biological immune systems. Each tier serves a distinct function with specific computational characteristics:

**Tier 1 - Innate Layer (1-5ms latency):** Extracts activation patterns from the LLM backbone to compute rapid risk scores without requiring model fine-tuning. This layer processes all incoming queries and routes them based on risk classification.

**Tier 2 - Adaptive Layer (10-50ms latency):** Generates context-specific safety constraints for high-risk queries using a small transformer decoder trained on threat-constraint pairs. This layer activates only when the innate layer identifies elevated risk.

**Tier 3 - Memory Layer (O(log n) retrieval):** Stores successful interventions indexed by threat embeddings, enabling rapid retrieval for previously encountered threat patterns and continuous system improvement.

### 2.2 Innate Detection Layer

The innate layer leverages the observation that LLM hidden states encode safety-relevant information. Given an input query $q$ processed by the LLM backbone, we extract activation patterns from intermediate layers.

**Activation Extraction:** For a query $q$ processed through an $L$-layer transformer, we extract activations from layers $\{l_1, l_2, ..., l_k\}$ where $k \ll L$ (typically $k=3$ layers selected via validation). The activation vector is:

$$\mathbf{a}_q = \text{Concat}[\mathbf{h}_{l_1}^{[\text{CLS}]}, \mathbf{h}_{l_2}^{[\text{CLS}]}, \mathbf{h}_{l_3}^{[\text{CLS}]}]$$

where $\mathbf{h}_{l_i}^{[\text{CLS}]}$ denotes the hidden state at the classification token position for layer $l_i$.

**Risk Scoring:** A lightweight classifier $f_\theta: \mathbb{R}^{3d} \rightarrow [0,1]$ maps activation vectors to risk scores:

$$r_q = f_\theta(\mathbf{a}_q) = \sigma(\mathbf{W}_2 \cdot \text{ReLU}(\mathbf{W}_1 \cdot \mathbf{a}_q + \mathbf{b}_1) + \mathbf{b}_2)$$

where $\mathbf{W}_1 \in \mathbb{R}^{256 \times 3d}$, $\mathbf{W}_2 \in \mathbb{R}^{1 \times 256}$, and $\sigma$ is the sigmoid function. This two-layer MLP contains approximately 1M parameters, ensuring sub-5ms inference.

**Tiered Routing:** Based on the risk score $r_q$, queries are routed according to:

$$\text{Route}(q) = \begin{cases} \text{PASS} & \text{if } r_q < \tau_{\text{low}} \\ \text{ADAPTIVE} & \text{if } \tau_{\text{low}} \leq r_q < \tau_{\text{high}} \\ \text{BLOCK} & \text{if } r_q \geq \tau_{\text{high}} \end{cases}$$

where thresholds $\tau_{\text{low}} = 0.3$ and $\tau_{\text{high}} = 0.9$ are determined via validation set optimization.

### 2.3 Adaptive Constraint Generation Layer

For queries routed to the adaptive layer, we generate context-specific safety constraints rather than retrieving from a fixed library.

**Threat Embedding:** The query is encoded into a threat embedding using the LLM backbone's final layer representation:

$$\mathbf{e}_q = \text{MeanPool}(\mathbf{H}_L^q)$$

where $\mathbf{H}_L^q \in \mathbb{R}^{n \times d}$ contains all token representations from the final layer.

**Constraint Generation:** A small transformer decoder $G_\phi$ with approximately 10M parameters generates safety constraints autoregressively:

$$c_1, c_2, ..., c_m = G_\phi(\mathbf{e}_q, r_q)$$

The decoder is trained on a dataset $\mathcal{D} = \{(q_i, c_i^*)\}_{i=1}^N$ of threat-constraint pairs using standard cross-entropy loss:

$$\mathcal{L}_{\text{gen}} = -\sum_{i=1}^N \sum_{j=1}^{|c_i^*|} \log P_\phi(c_{i,j}^* | c_{i,<j}^*, \mathbf{e}_{q_i}, r_{q_i})$$

**Constraint Application:** Generated constraints are injected into the agent's planning process following the in-planning safety strategy. The agent's action space is restricted according to:

$$\mathcal{A}_{\text{safe}} = \mathcal{A} \setminus \{a : \text{Violates}(a, c_1, ..., c_m)\}$$

### 2.4 Immune Memory Layer

The memory layer stores successful interventions for rapid retrieval, implementing immunological memory.

**Memory Structure:** The memory $\mathcal{M}$ consists of entries $(e_i, c_i, s_i)$ where $e_i$ is the threat embedding, $c_i$ is the generated constraint, and $s_i$ is a success score updated based on intervention outcomes.

**Indexing and Retrieval:** We use FAISS with IVF indexing for efficient approximate nearest neighbor search:

$$\mathcal{N}_k(q) = \text{FAISS-Search}(\mathbf{e}_q, \mathcal{M}, k)$$

retrieving the $k$ nearest memory entries in $O(\log |\mathcal{M}|)$ time.

**Memory-Augmented Generation:** When memory hits exist with similarity above threshold $\tau_{\text{mem}} = 0.85$, retrieved constraints are used directly or combined with generated constraints:

$$c_{\text{final}} = \begin{cases} c_{\text{retrieved}} & \text{if } \text{sim}(\mathbf{e}_q, \mathbf{e}_{\text{retrieved}}) > \tau_{\text{mem}} \\ G_\phi(\mathbf{e}_q, r_q, c_{\text{retrieved}}) & \text{otherwise} \end{cases}$$

**Memory Update:** After each intervention, memory is updated based on outcome:

$$s_i \leftarrow s_i + \alpha \cdot (\mathbb{1}[\text{success}] - s_i)$$

where $\alpha = 0.1$ is the learning rate. Entries with $s_i < 0.3$ are pruned to maintain memory quality.

### 2.5 Training Procedure

**Phase 1 - Innate Classifier Training:**
- Dataset: HarmBench (400+ scenarios) with binary safety labels
- Training: Binary cross-entropy loss, Adam optimizer ($\text{lr}=10^{-4}$), 50 epochs
- Validation: 20% holdout for threshold optimization

**Phase 2 - Constraint Generator Training:**
- Dataset: Synthetic (threat, constraint) pairs generated via GPT-4 annotation of HarmBench scenarios, augmented with Agent-SafetyBench examples (target: 10K pairs)
- Training: Cross-entropy loss, AdamW optimizer ($\text{lr}=5 \times 10^{-5}$), 30 epochs
- Architecture: 6-layer transformer decoder, 512 hidden dimension, 8 attention heads

**Phase 3 - End-to-End Fine-tuning:**
- Joint optimization of routing thresholds and memory parameters
- Objective: Minimize $\mathcal{L} = \lambda_1 \cdot \text{FPR} + \lambda_2 \cdot (1 - \text{TPR}) + \lambda_3 \cdot \text{Latency}$
- Grid search over $\lambda$ values with validation set

### 2.6 Experimental Design

**Datasets:**
- **HarmBench:** 400+ adversarial scenarios covering diverse harm categories
- **Agent-SafetyBench:** 500+ agent-specific safety scenarios with tool-use contexts
- **Benign Test Set:** 1000 legitimate queries sampled from ToolBench for FPR measurement

**Baselines:**
1. **No Safety:** Agent operates without safety interventions (lower bound)
2. **TrustAgent:** State-of-the-art in-planning safety constraints
3. **NeMo Guardrails:** Parallel guardrail orchestration with 5 guardrail types
4. **Static Keyword Filter:** Traditional keyword-based blocking (upper bound for FPR)

**Evaluation Metrics:**

| Metric | Definition | Target |
|--------|------------|--------|
| Unsafe Action Prevention Rate (UAPR) | $\frac{\text{Blocked Unsafe Actions}}{\text{Total Unsafe Actions}}$ | >90% |
| False Positive Rate (FPR) | $\frac{\text{Blocked Benign Actions}}{\text{Total Benign Actions}}$ | ≤20% (≥30% reduction) |
| P50 Latency | Median response time | <20ms |
| P99 Latency | 99th percentile response time | <100ms |
| Memory Hit Rate | $\frac{\text{Memory Retrievals}}{\text{Adaptive Layer Calls}}$ | >40% after warmup |

**Statistical Analysis:**
- Primary comparison: Two-proportion z-test for FPR reduction (α = 0.05, one-tailed)
- Sample size: n ≥ 500 queries per condition (power = 0.80 for detecting 30% reduction)
- Latency comparison: Mann-Whitney U test (non-parametric due to skewed distributions)
- Multiple comparison correction: Bonferroni adjustment for 4 baseline comparisons

**Ablation Studies:**
1. **Innate-only:** Remove adaptive and memory layers
2. **No-memory:** Remove memory layer, keep innate and adaptive
3. **Fixed-adaptive:** Replace constraint generator with retrieval from fixed library
4. **Random-routing:** Replace risk-based routing with random assignment

### 2.7 Mechanism Verification

To establish causal mechanisms, we conduct targeted experiments:

**H-M1 (Activation Encoding):** Train innate classifier on activation patterns vs. random projections. Success criterion: AUC > 0.75 for activations, AUC ≈ 0.50 for random.

**H-M2 (Routing Accuracy):** Measure routing precision/recall on held-out labeled set. Success criterion: >85% accuracy in risk categorization.

**H-M3 (Constraint Specificity):** Compare generated constraints to fixed library using semantic diversity metrics (unique n-grams, embedding variance). Success criterion: >20% higher diversity.

**H-M4 (Memory Acceleration):** Measure latency for repeated vs. novel threats after memory population. Success criterion: >50% latency reduction for repeated patterns.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and supporting evidence, we anticipate the following outcomes:

**Primary Outcome:** ASIS will achieve a false positive rate of ≤14% compared to TrustAgent's estimated 20%+ FPR, representing a ≥30% relative reduction. This improvement stems from the adaptive constraint generation producing more precise, context-specific interventions than fixed rule sets.

**Secondary Outcomes:**
- Unsafe action prevention rate >92%, comparable to or exceeding static guardrails
- P50 latency <15ms for the majority of queries (handled by innate layer)
- P99 latency <80ms for full pipeline execution
- Memory hit rate >45% after processing 1000 queries, demonstrating effective learning

**Ablation Predictions:**
- Innate-only configuration will show ~15% higher FPR than full ASIS
- No-memory configuration will show ~30% higher latency for repeated threats
- Fixed-adaptive configuration will show ~20% higher FPR than adaptive generation

### 3.2 Potential Challenges and Mitigations

**Challenge 1:** Insufficient training data for constraint generator.
*Mitigation:* Augment HarmBench with synthetic generation using GPT-4; if insufficient, fall back to retrieval-augmented generation from curated constraint library.

**Challenge 2:** Activation patterns may not generalize across LLM architectures.
*Mitigation:* Initial experiments focus on Llama-3-8B-Instruct; extension to other architectures treated as future work with architecture-specific classifier fine-tuning.

**Challenge 3:** Memory may accumulate low-quality entries over time.
*Mitigation:* Implement success-based pruning and periodic memory consolidation; limit memory size to 10K entries with LRU eviction.

### 3.3 Broader Impact

**Scientific Contributions:**
- First unified framework integrating activation-based detection, adaptive constraint generation, and immune memory for agent safety
- Empirical validation of bio-inspired tiered architecture for AI safety
- Open-source implementation enabling reproducibility and extension

**Practical Applications:**
- Deployable safety layer for production LLM agents with tool-use capabilities
- Reduced user friction in safety-critical applications (healthcare, finance, legal)
- Modular components adoptable independently based on deployment constraints

**Research Community Impact:**
- New benchmark results on HarmBench and Agent-SafetyBench with standardized evaluation protocol
- Framework for thinking about adaptive AI safety inspired by biological systems
- Foundation for future work on multi-agent safety and cross-domain transfer

### 3.4 Limitations and Future Directions

**Current Limitations:**
- Scope limited to single-agent, text-only scenarios
- Fixed memory size constrains long-term learning
- Domain-specific threats (medical, financial) may require specialized training

**Future Directions:**
- Extension to multi-modal agents (vision-language models)
- Multi-agent coordination with PeerGuard-style inter-agent safety protocols
- Continual learning mechanisms for adapting to emerging threat patterns
- Formal verification of safety guarantees under specified conditions

This research represents a significant step toward adaptive, context-aware safety systems for LLM agents, addressing the critical false positive problem while maintaining robust threat prevention. By drawing inspiration from biological immune systems and leveraging recent advances in LLM interpretability, ASIS offers a principled framework for the next generation of trustworthy agentic AI systems.