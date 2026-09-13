# Research Proposal: Adversarial Memory Injection Attacks on LLM Agents and Retrieval-Augmented Defenses

## 1. Introduction

### Background

Large Language Model (LLM) agents have rapidly evolved from simple conversational interfaces to sophisticated autonomous systems capable of executing complex, multi-step tasks across diverse domains including web browsing, code generation, and personal assistance. A critical enabler of this advancement is the integration of persistent memory systems—typically implemented through vector databases, conversation histories, and experience retrieval mechanisms—that allow agents to maintain context across interactions, learn from past experiences, and personalize their responses over time.

However, this architectural evolution introduces significant security vulnerabilities that remain poorly understood. Unlike traditional prompt injection attacks that target single interactions and have transient effects, memory injection attacks can implant malicious information that persists indefinitely within an agent's knowledge store. Recent work such as MemoryGraft (Srivastava & He, 2025) has demonstrated that adversaries can exploit experience retrieval mechanisms to cause systematic behavioral drift, while BackdoorAgent (Feng et al., 2026) has shown that triggers implanted at the memory stage can propagate through multiple execution steps. These findings reveal that memory systems, designed to enhance agent capabilities, simultaneously create attack surfaces with potentially devastating long-term consequences.

The emerging defense landscape, exemplified by RAGPart/RAGMask (Pathmanathan et al., 2025) and A-MemGuard (Wei et al., 2025), demonstrates promising approaches to mitigating corpus poisoning and memory manipulation. However, these defenses address specific attack vectors and lack a unified framework for understanding the full spectrum of memory-based threats. Furthermore, the trade-off between security and utility remains insufficiently characterized, limiting practical deployment.

### Research Objectives

This research aims to establish a comprehensive framework for understanding and defending against adversarial memory injection attacks on LLM agents. Our specific objectives are:

1. **Systematic Attack Characterization**: Develop a taxonomy of memory injection attack vectors, including indirect injection through processed documents, retrieval-optimized adversarial entries, and semantic trojans with conditional activation.

2. **Defense Framework Development**: Design and implement a multi-layered memory verification system combining provenance tracking, consistency verification, and adversarial retrieval filtering.

3. **Comprehensive Evaluation**: Create benchmarks spanning multiple agent architectures and task domains to measure attack efficacy, defense effectiveness, computational overhead, and utility preservation.

4. **Practical Security Guidelines**: Establish deployment-ready security standards and tools for protecting agent memory systems.

### Significance

This research addresses a critical gap in LLM agent safety with implications across security, privacy, and trustworthiness. As agents increasingly handle sensitive data and make consequential decisions, understanding memory vulnerabilities is essential for responsible deployment. Our work contributes to the Workshop on Safe & Trustworthy Agents by directly addressing adversarial attacks, security, and agent control—core themes in establishing trustworthy agentic AI systems.

## 2. Methodology

### 2.1 Attack Framework Development

#### 2.1.1 Attack Taxonomy

We define three primary attack categories based on injection mechanism and activation pattern:

**Type I: Indirect Document Injection**
Adversaries embed malicious content within documents that agents process during normal operation. Let $D = \{d_1, d_2, ..., d_n\}$ represent documents ingested by an agent. An adversarial document $d_{adv}$ contains payload $p$ designed to be stored in memory $M$ and retrieved for target queries $Q_t$:

$$d_{adv} = \text{Craft}(p, Q_t, \theta_{embed})$$

where $\theta_{embed}$ represents the embedding model parameters used by the agent's retrieval system.

**Type II: Retrieval-Optimized Adversarial Entries**
We formulate memory injection as an optimization problem. Given target query set $Q_t$ and existing memory entries $M$, we craft adversarial entry $m_{adv}$ to maximize retrieval probability:

$$m_{adv} = \arg\max_{m} \sum_{q \in Q_t} \text{sim}(E(m), E(q)) - \lambda \cdot \text{Detectability}(m, M)$$

where $E(\cdot)$ denotes the embedding function, $\text{sim}(\cdot, \cdot)$ measures cosine similarity, and $\text{Detectability}(\cdot)$ quantifies anomaly detection risk.

**Type III: Semantic Trojans**
Conditional payloads activate only under specific semantic contexts. We define a trojan memory entry as:

$$m_{trojan} = (c_{trigger}, a_{malicious}, c_{benign})$$

where $c_{trigger}$ specifies activation conditions, $a_{malicious}$ defines the harmful behavior, and $c_{benign}$ provides innocuous content for non-trigger contexts.

#### 2.1.2 Attack Implementation

For each attack type, we develop concrete attack algorithms:

**Algorithm 1: Gradient-Based Retrieval Optimization**
```
Input: Target queries Q_t, embedding model E, perturbation budget ε
Output: Adversarial memory entry m_adv

1. Initialize m_0 with semantically relevant content
2. For iteration t = 1 to T:
   a. Compute gradient: g_t = ∇_m Σ_{q∈Q_t} sim(E(m), E(q))
   b. Update: m_t = m_{t-1} + α · sign(g_t)
   c. Project to feasible set: m_t = Π_ε(m_t)
3. Apply fluency refinement via LLM rewriting
4. Return m_T
```

**Algorithm 2: Semantic Trojan Construction**
```
Input: Trigger condition c_trigger, malicious action a_mal
Output: Trojan memory entry m_trojan

1. Generate benign cover story c_benign relevant to agent domain
2. Encode trigger using semantic paraphrasing to evade detection
3. Construct conditional payload:
   m_trojan = "When [c_trigger], recommend [a_mal]. Otherwise, [c_benign]"
4. Optimize embedding alignment with expected trigger queries
5. Return m_trojan
```

### 2.2 Defense Framework: Memory Verification Layer (MVL)

We propose a three-component defense architecture that operates at the retrieval stage, requiring no modifications to the base LLM.

#### 2.2.1 Component A: Provenance Tracking with Cryptographic Attribution

Each memory entry $m_i$ is augmented with provenance metadata:

$$m_i^{+} = (m_i, \text{hash}(m_i), \text{source}_i, \text{timestamp}_i, \text{sig}_i)$$

where $\text{sig}_i = \text{Sign}_{sk}(\text{hash}(m_i) || \text{source}_i || \text{timestamp}_i)$ provides cryptographic attribution using the source's signing key $sk$.

**Trust Score Computation:**
$$\text{Trust}(m_i) = w_1 \cdot \text{SourceRep}(\text{source}_i) + w_2 \cdot \text{Age}(\text{timestamp}_i) + w_3 \cdot \text{SigValid}(\text{sig}_i)$$

where weights $w_1, w_2, w_3$ are tuned based on deployment context.

#### 2.2.2 Component B: Consistency Verification Against Trusted Knowledge

Retrieved memories are validated against a trusted knowledge base $K_{trusted}$. We employ a three-stage verification process:

**Stage 1: Claim Extraction**
Given memory entry $m_i$, extract factual claims $C_i = \{c_1, c_2, ..., c_k\}$ using an LLM with structured prompting.

**Stage 2: Evidence Retrieval**
For each claim $c_j$, retrieve relevant evidence $E_j$ from $K_{trusted}$:
$$E_j = \text{TopK}(\{k \in K_{trusted} : \text{sim}(E(c_j), E(k)) > \tau_{retrieval}\})$$

**Stage 3: Consistency Scoring**
Compute consistency score using natural language inference:
$$\text{Consistency}(m_i) = \frac{1}{|C_i|} \sum_{c_j \in C_i} \text{NLI}(E_j, c_j)$$

where $\text{NLI}(\cdot)$ returns entailment probability.

#### 2.2.3 Component C: Adversarial Retrieval Filtering

Inspired by RAGMask (Pathmanathan et al., 2025), we detect anomalously high-similarity entries through perturbation analysis:

**Algorithm 3: Anomaly Detection via Masked Retrieval**
```
Input: Query q, retrieved entries R = {r_1, ..., r_k}, threshold θ_anomaly
Output: Filtered entries R_filtered

1. For each entry r_i in R:
   a. Generate masked variants: r_i^{(1)}, ..., r_i^{(m)} by token masking
   b. Compute similarity variance:
      σ_i = Var({sim(E(q), E(r_i^{(j)})) : j = 1, ..., m})
   c. Compute similarity drop:
      δ_i = sim(E(q), E(r_i)) - mean({sim(E(q), E(r_i^{(j)}))})
   d. Anomaly score: A(r_i) = δ_i / (σ_i + ε)
2. Filter: R_filtered = {r_i : A(r_i) < θ_anomaly}
3. Return R_filtered
```

**Integrated Defense Pipeline:**

The MVL combines all components through weighted aggregation:

$$\text{SafeScore}(m_i) = \alpha \cdot \text{Trust}(m_i) + \beta \cdot \text{Consistency}(m_i) + \gamma \cdot (1 - \text{Anomaly}(m_i))$$

Memory entries with $\text{SafeScore}(m_i) < \theta_{safe}$ are quarantined and flagged for review.

### 2.3 Experimental Design

#### 2.3.1 Agent Architectures and Tasks

We evaluate across three representative agent configurations:

1. **Web Browsing Agent**: Based on WebArena benchmark, performing information retrieval and form completion tasks.
2. **Coding Assistant**: Integrated with code repositories, executing code generation and debugging tasks.
3. **Personal Assistant**: Managing calendar, email, and document tasks with persistent user preferences.

#### 2.3.2 Attack Evaluation Protocol

For each attack type and agent configuration, we measure:

- **Attack Success Rate (ASR)**: Percentage of trials where the adversarial objective is achieved.
- **Persistence Duration**: Number of interactions before malicious memory naturally decays.
- **Stealth Score**: Inverse of detection rate by baseline anomaly detectors.

$$\text{ASR} = \frac{|\{t : \text{Objective}(t) = \text{True}\}|}{|T|}$$

#### 2.3.3 Defense Evaluation Metrics

- **Defense Effectiveness Rate (DER)**: Reduction in ASR when defense is active.
- **False Positive Rate (FPR)**: Proportion of benign entries incorrectly filtered.
- **Utility Preservation (UP)**: Task success rate with defense relative to undefended baseline.
- **Computational Overhead**: Additional latency and memory requirements.

$$\text{DER} = \frac{\text{ASR}_{undefended} - \text{ASR}_{defended}}{\text{ASR}_{undefended}}$$

$$\text{UP} = \frac{\text{TaskSuccess}_{defended}}{\text{TaskSuccess}_{undefended}}$$

#### 2.3.4 Dataset Construction

We construct evaluation datasets comprising:
- 1,000 benign memory entries per domain from authentic agent interactions
- 500 adversarial entries per attack type, generated using our attack algorithms
- 200 test queries covering normal operation and targeted attack scenarios

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Comprehensive Attack Taxonomy**: A systematic classification of memory injection vulnerabilities with quantified threat levels across agent architectures, providing researchers and practitioners with a structured understanding of the attack landscape.

2. **Validated Defense Framework**: The Memory Verification Layer (MVL) with empirically demonstrated effectiveness. Based on preliminary analysis and related work (A-MemGuard achieves >95% attack reduction), we anticipate:
   - Defense Effectiveness Rate > 90% across attack types
   - False Positive Rate < 5% for benign entries
   - Utility Preservation > 95% on standard tasks
   - Computational overhead < 15% latency increase

3. **Benchmark Suite**: Open-source evaluation framework including attack implementations, defense modules, and standardized metrics enabling reproducible research and fair comparison of future approaches.

4. **Security Guidelines**: Practical deployment recommendations specifying memory architecture choices, monitoring requirements, and incident response procedures for production LLM agents.

### Broader Impact

**Scientific Contributions**: This research advances the theoretical understanding of adversarial vulnerabilities in retrieval-augmented systems, bridging security research with LLM agent development. Our optimization-based attack formulation and multi-layered defense architecture provide foundational frameworks for future research.

**Practical Applications**: The MVL framework offers immediately deployable protection for commercial and open-source agent platforms. By releasing implementation code and pre-trained detection models, we enable rapid adoption across the ecosystem.

**Policy Implications**: Our findings inform regulatory discussions around AI safety requirements, providing concrete technical criteria for evaluating agent security. The provenance tracking component specifically supports accountability and audit requirements emerging in AI governance frameworks.

**Community Building**: Through benchmark release and standardized evaluation protocols, we foster a research community focused on agent memory security, addressing a critical gap identified in the Workshop on Safe & Trustworthy Agents mission.

### Limitations and Future Directions

We acknowledge that adversarial attacks and defenses exist in an ongoing arms race. Our defense framework may require continuous updates as attackers develop evasion techniques. Future work should explore adaptive defenses using online learning, formal verification of memory integrity guarantees, and extension to multi-agent scenarios where memory poisoning can propagate across agent networks. Additionally, investigating the intersection with privacy-preserving computation could enable secure memory systems that protect both against adversarial manipulation and unauthorized information leakage.