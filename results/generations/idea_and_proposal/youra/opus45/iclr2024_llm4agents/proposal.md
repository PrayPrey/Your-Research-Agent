# Research Proposal: Parameter-Free Spreading Activation Memory Consolidation for Long-Running LLM Agents

## 1. Title

**Parameter-Free Spreading Activation Memory Consolidation (SAMC) for Robust Long-Term Memory in Persistent LLM Agents: A Cognitively-Inspired Graph-Based Approach**

---

## 2. Introduction

### 2.1 Background

Large Language Model (LLM) agents have emerged as transformative systems capable of performing complex tasks through natural language reasoning. Unlike traditional chatbots, these agents maintain persistent memory across extended interactions, enabling them to serve as knowledge workers, personal assistants, and customer service representatives over prolonged engagement periods. However, as conversation length increases beyond 100 turns, these agents face a critical challenge: the degradation of long-term memory recall and the phenomenon of catastrophic forgetting, where early-session information becomes increasingly inaccessible.

Current approaches to addressing this memory limitation fall into two primary categories. First, Retrieval-Augmented Generation (RAG) systems store episodic memories in vector databases and retrieve relevant information based on embedding similarity. While computationally efficient, static RAG suffers from recency bias and fails to capture semantic connections between temporally distant memories, resulting in poor multi-hop reasoning performance. Second, parameter-update approaches such as LoRA-based fine-tuning during simulated "sleep" phases can consolidate memories into model weights. However, these methods require GPU resources, risk degrading base model capabilities, and cannot operate asynchronously during agent idle time.

Recent advances in cognitive neuroscience have illuminated the mechanisms underlying human memory consolidation during sleep. Singh et al. (2022) demonstrated that the hippocampal-neocortical memory transfer occurs through distinct phases: NREM (Non-Rapid Eye Movement) sleep facilitates tight replay of recent experiences and strengthening of important connections, while REM sleep enables free exploration and integration of memories into broader semantic structures. This dual-phase architecture has proven essential for robust long-term memory formation in biological systems.

Concurrently, research on spreading activation dynamics in memory retrieval has shown promise for LLM agents. The SYNAPSE system demonstrated that propagating activation through semantic graphs outperforms embedding-only retrieval on multi-hop reasoning tasks. However, SYNAPSE focuses exclusively on retrieval mechanisms without addressing the consolidation of memories over time.

### 2.2 Research Gap

A critical gap exists at the intersection of these research directions: **Can we achieve robust memory consolidation through pure graph operations, preserving base LLM capabilities while improving long-term recall?** Specifically, no existing system combines cognitively-inspired consolidation phases with parameter-free graph operations to address the memory challenges of long-running LLM agents.

### 2.3 Research Objectives

This research proposes **Spreading Activation Memory Consolidation (SAMC)**, a parameter-free mechanism inspired by cognitive sleep consolidation. Our primary objectives are:

1. **Design and implement** a dual-phase consolidation mechanism operating on episodic-semantic memory graphs through NREM-like tight replay and REM-like free exploration.
2. **Validate** that SAMC improves multi-hop recall accuracy by ≥15% and reduces catastrophic forgetting by ≥20% compared to static RAG baselines.
3. **Demonstrate** practical feasibility through asynchronous CPU-based consolidation during agent idle time without gradient computation.
4. **Establish** a theoretical framework mapping cognitive consolidation principles to computational memory architectures.

### 2.4 Significance

This research addresses fundamental challenges in deploying persistent conversational agents at scale. By eliminating the need for parameter updates, SAMC enables memory consolidation on commodity hardware, preserves base LLM capabilities, and provides interpretable, inspectable memory operations critical for enterprise deployment. The theoretical contribution establishes the first principled mapping from sleep-consolidation theory to LLM agent memory without parameter modifications, opening new research directions in cognitively-inspired AI systems.

---

## 3. Methodology

### 3.1 System Architecture Overview

SAMC operates on a hybrid episodic-semantic memory graph $G = (V, E, W)$ where $V$ comprises episodic nodes (specific interaction memories) and semantic nodes (abstracted concepts), $E$ represents typed edges (temporal, semantic, causal), and $W$ denotes edge weights reflecting connection strength.

The system alternates between two operational modes:
- **Online Phase:** Rapid encoding of new episodic memories during user interactions
- **Offline Phase:** Consolidation through spreading activation dynamics during idle periods

### 3.2 Memory Graph Construction

During the online phase, each user interaction $i_t$ at time $t$ generates an episodic node $v_t^{ep}$ with the following attributes:

$$v_t^{ep} = \{content, embedding, timestamp, importance, activation\}$$

The importance score is computed as:

$$importance(v_t^{ep}) = \alpha \cdot novelty(v_t^{ep}) + \beta \cdot emotional\_salience(v_t^{ep}) + \gamma \cdot user\_engagement(v_t^{ep})$$

where $\alpha + \beta + \gamma = 1$ are domain-specific weights. Episodic nodes connect to existing semantic nodes through edges weighted by embedding similarity:

$$w(v_t^{ep}, v_s^{sem}) = \cos(emb(v_t^{ep}), emb(v_s^{sem})) \cdot \mathbb{1}[\cos > \theta_{connect}]$$

where $\theta_{connect} = 0.7$ is the connection threshold.

### 3.3 NREM-like Tight Replay Phase

The NREM-like phase implements selective memory replay with edge strengthening and pruning. The algorithm proceeds as follows:

**Algorithm 1: NREM-like Consolidation**
```
Input: Memory graph G, recent episodic nodes R, decay factor α=0.85, 
       inhibition strength λ=0.3, pruning threshold θ_prune=0.1
Output: Consolidated graph G'

1. Initialize activation: A(v) = importance(v) for v ∈ R, else 0
2. For iteration k = 1 to K_NREM:
   a. For each node v with A(v) > 0:
      - Propagate: A'(u) += α · w(v,u) · A(v) for all neighbors u
   b. Apply lateral inhibition:
      - For competing nodes u₁, u₂ with semantic overlap > 0.8:
        A(u_min) = max(0, A(u_min) - λ · A(u_max))
   c. Strengthen co-activated edges:
      - Δw(u,v) = η · A(u) · A(v) for edges where both endpoints active
   d. Prune weak edges:
      - Remove edge (u,v) if w(u,v) < θ_prune
3. Return G' with updated weights
```

The spreading activation follows the mathematical formulation:

$$A^{(k+1)}(v) = \sum_{u \in N(v)} \alpha \cdot w(u,v) \cdot A^{(k)}(u) - \lambda \cdot \max_{u' \in C(v)} A^{(k)}(u')$$

where $N(v)$ denotes neighbors of $v$, $C(v)$ denotes competing nodes, and $\alpha = 0.85$ ensures activation decay over propagation distance.

Edge weight updates follow Hebbian learning principles:

$$w^{(k+1)}(u,v) = w^{(k)}(u,v) + \eta \cdot A^{(k)}(u) \cdot A^{(k)}(v)$$

with learning rate $\eta = 0.1$.

### 3.4 REM-like Free Exploration Phase

The REM-like phase enables discovery of distant semantic connections and gist extraction:

**Algorithm 2: REM-like Exploration**
```
Input: Consolidated graph G', exploration steps K_REM, 
       gist threshold θ_gist=0.6
Output: Graph G'' with new semantic nodes

1. Initialize activation uniformly: A(v) = 1/|V| for all v
2. For iteration k = 1 to K_REM:
   a. Free propagation (no inhibition):
      - A'(v) = Σ_u α · w(u,v) · A(u) + noise(σ=0.1)
   b. Identify activation clusters:
      - Clusters C = {c₁, c₂, ...} where nodes have correlated activation
   c. For each cluster c with |c| ≥ 3:
      - Extract gist using LLM: gist_c = LLM_summarize(contents(c))
      - If novelty(gist_c) > θ_gist:
        Create semantic node v_c^{sem} with content = gist_c
        Connect v_c^{sem} to all nodes in c
3. Return G'' with new semantic structure
```

The gist extraction leverages the base LLM without fine-tuning:

$$gist_c = \text{LLM}(\text{prompt}_{gist}, \{content(v) : v \in c\})$$

where $\text{prompt}_{gist}$ instructs the model to identify common themes and abstract patterns.

### 3.5 Consolidation Triggering and Scheduling

Consolidation is triggered by either:
1. **Interaction count:** Every $N \in \{25, 50, 100\}$ interactions
2. **Idle timeout:** After $T \in \{1, 5, 10\}$ minutes of inactivity

The consolidation runs asynchronously on CPU, with the following time complexity:
- NREM phase: $O(K_{NREM} \cdot |E|)$
- REM phase: $O(K_{REM} \cdot |V|^2)$ for cluster detection

For graphs with $|V| \leq 5000$ nodes, total consolidation time is targeted at $<5$ seconds.

### 3.6 Retrieval with Consolidated Memory

Post-consolidation retrieval combines embedding similarity with spreading activation:

$$score(v, q) = \beta \cdot \cos(emb(v), emb(q)) + (1-\beta) \cdot A_q(v)$$

where $A_q(v)$ is the activation of node $v$ after propagating from query-relevant seed nodes, and $\beta = 0.5$ balances the two signals.

### 3.7 Experimental Design

#### 3.7.1 Datasets and Benchmarks

1. **LoCoMo Benchmark:** Long-context conversational memory evaluation with 100-500 turn conversations
2. **Custom Multi-hop QA:** Synthetic conversations requiring 2-hop and 3-hop reasoning across temporally distant memories
3. **Domain-specific datasets:** Customer service logs, knowledge worker interactions, personal assistant conversations

#### 3.7.2 Experimental Conditions

We employ a 3×3×3 mixed factorial design:

| Factor | Levels | Type |
|--------|--------|------|
| Consolidation Method | SAMC, Static RAG, MemGPT | Between-subjects |
| Consolidation Frequency | 25, 50, 100 interactions | Within-subjects |
| Conversation Length | 100, 200, 500 turns | Within-subjects |

#### 3.7.3 Baselines

1. **Static RAG:** Embedding-based retrieval without consolidation
2. **MemGPT:** Hierarchical memory with paging mechanism
3. **SYNAPSE:** Spreading activation retrieval without consolidation
4. **Let Them Sleep (ablation):** Sleep-cycle approach with LoRA (parameter-update comparison)

#### 3.7.4 Evaluation Metrics

**Primary Metrics:**
- **Long-term Recall Accuracy:** Percentage of correct answers on queries about interactions >50 turns ago
- **Multi-hop Recall F1:** F1 score on reasoning tasks requiring 2+ memory retrievals
- **Catastrophic Forgetting Rate:** $\Delta_{accuracy} = Acc_{early}^{post} - Acc_{early}^{pre}$ on early-session facts after 200+ turns

**Secondary Metrics:**
- **Retrieval Latency:** Time from query to relevant memory retrieval (ms)
- **Consolidation Overhead:** Time per consolidation cycle (seconds)
- **Memory Efficiency:** Graph size growth rate over conversation length

#### 3.7.5 Statistical Analysis

**Sample Size:** Based on power analysis with effect size $d=0.5$, power $=0.8$, $\alpha=0.05$, we require $N \geq 64$ conversation sessions per condition.

**Statistical Tests:**
- Primary: Mixed-effects ANOVA with Tukey HSD post-hoc comparisons
- Secondary: Paired t-tests for within-condition comparisons
- Effect sizes: Cohen's $d$ for pairwise comparisons, $\eta^2$ for overall effects

**Multiple Comparison Correction:** Bonferroni correction with $\alpha_{adj} = 0.05/12 = 0.004$ for 12 primary comparisons.

#### 3.7.6 Ablation Studies

To validate the contribution of each component:

| Ablation | Configuration | Purpose |
|----------|---------------|---------|
| A1 | NREM-only | Validate REM phase contribution |
| A2 | REM-only | Validate NREM phase contribution |
| A3 | No lateral inhibition | Validate inhibition mechanism |
| A4 | No edge pruning | Validate pruning contribution |
| A5 | Random gist extraction | Validate LLM-based gist quality |

#### 3.7.7 Implementation Details

- **Base LLM:** GPT-4-turbo or Claude-3.5-Sonnet (fixed across conditions)
- **Embedding Model:** text-embedding-3-small (1536 dimensions)
- **Graph Database:** NetworkX for prototyping, Neo4j for production evaluation
- **Hardware:** Consolidation on CPU (Intel Xeon 8-core); inference on GPU (NVIDIA A100)

### 3.8 Falsification Criteria

The hypothesis is **falsified** if any of the following conditions hold:
1. SAMC shows $<5\%$ improvement over static RAG on long-term recall
2. Consolidation overhead exceeds 30 seconds per cycle for graphs with $\leq 5000$ nodes
3. Parameter-update approaches outperform SAMC by $>10\%$ on all metrics
4. Spreading activation retrieval underperforms embedding-only retrieval

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

Based on our hypothesis and preliminary analysis, we anticipate the following outcomes:

**Primary Outcomes:**
1. **Long-term Recall Improvement:** SAMC will achieve $\geq 80\%$ accuracy on long-term recall tasks, representing a $\geq 15\%$ absolute improvement over static RAG ($\sim 60\%$) and $\geq 5\%$ improvement over SYNAPSE ($\sim 75\%$).

2. **Multi-hop Reasoning Enhancement:** Multi-hop F1 scores will reach $\geq 0.70$, compared to $0.45$ for static RAG and $0.62$ for SYNAPSE, demonstrating the value of consolidated semantic connections.

3. **Catastrophic Forgetting Reduction:** The forgetting rate on early-session facts will decrease by $\geq 20\%$ compared to non-consolidating baselines, with important memories preserved through edge strengthening.

4. **Practical Efficiency:** Consolidation will complete in $<5$ seconds for graphs with $\leq 5000$ nodes, enabling deployment in production conversational agents.

**Secondary Outcomes:**
- Dual-phase consolidation (NREM+REM) will outperform single-phase approaches by $\geq 8\%$ on recall accuracy
- Optimal consolidation frequency will be identified (expected: every 50 interactions)
- Lateral inhibition will reduce interference on overlapping memory scenarios by $\geq 15\%$

### 4.2 Theoretical Impact

This research establishes the **first principled computational framework mapping cognitive sleep-consolidation theory to LLM agent memory without parameter updates**. Key theoretical contributions include:

1. **Formal Model of Graph-Based Consolidation:** Mathematical formalization of spreading activation dynamics, lateral inhibition, and Hebbian edge strengthening in the context of LLM memory systems.

2. **Dual-Phase Architecture Validation:** Empirical evidence that NREM-like (tight replay) and REM-like (free exploration) phases serve complementary functions in artificial memory systems, paralleling biological findings.

3. **Parameter-Free Consolidation Paradigm:** Demonstration that meaningful memory consolidation can occur entirely through external graph operations, challenging the assumption that weight updates are necessary for continual learning.

### 4.3 Methodological Impact

SAMC introduces novel methodological contributions to the LLM agent research community:

1. **Spreading Activation Consolidation Algorithm:** A reusable algorithm combining activation propagation, lateral inhibition, and edge modulation for memory graph maintenance.

2. **Gist Extraction Protocol:** A systematic approach for leveraging LLMs to create semantic abstractions from episodic clusters without fine-tuning.

3. **Evaluation Framework:** Comprehensive metrics and experimental protocols for assessing long-term memory in conversational agents, including forgetting rate measurement and multi-hop reasoning evaluation.

### 4.4 Practical Impact

The practical implications of SAMC extend to multiple deployment scenarios:

1. **Enterprise Conversational Agents:** Customer service bots maintaining accurate recall of customer history across hundreds of interactions without expensive GPU-based fine-tuning.

2. **Personal Assistants:** Long-running assistants that remember user preferences, past decisions, and contextual information over months of interaction.

3. **Knowledge Workers:** AI collaborators that consolidate project knowledge, meeting notes, and decision rationales into accessible semantic structures.

4. **Resource Efficiency:** Async CPU-based consolidation during idle time eliminates the need for dedicated GPU resources for memory maintenance, reducing operational costs by an estimated 60-80% compared to LoRA-based approaches.

### 4.5 Broader Implications

Beyond immediate applications, this research opens several future directions:

1. **Multimodal Extension:** Applying SAMC principles to vision-language agent memory, consolidating visual experiences alongside textual interactions.

2. **Hierarchical Consolidation:** Scaling to graphs with $>10,000$ nodes through hierarchical consolidation strategies.

3. **Interpretable AI:** The graph-based approach provides inherent interpretability, enabling users and developers to inspect, audit, and modify agent memories—critical for trustworthy AI deployment.

4. **Cognitive Science Validation:** The computational model may provide testable predictions for cognitive science research on human memory consolidation.

### 4.6 Limitations and Future Work

We acknowledge several limitations that define future research directions:

1. **Scaling Constraints:** Current design targets graphs with $\leq 10,000$ nodes; larger deployments require hierarchical approaches.

2. **Domain Generalization:** Initial validation focuses on conversational domains; extension to structured reasoning tasks requires additional study.

3. **Hyperparameter Sensitivity:** Optimal values for decay factor ($\alpha$), inhibition strength ($\lambda$), and pruning threshold ($\theta_{prune}$) may vary across domains.

4. **Gist Quality Dependence:** Semantic node creation relies on LLM summarization quality, which may degrade for highly technical or specialized content.

### 4.7 Timeline and Milestones

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Implementation | Months 1-3 | SAMC algorithm, memory graph infrastructure |
| Baseline Development | Months 2-4 | RAG, MemGPT, SYNAPSE implementations |
| Primary Experiments | Months 4-7 | Main comparison study on LoCoMo |
| Ablation Studies | Months 6-8 | Component contribution analysis |
| Analysis & Writing | Months 8-10 | Statistical analysis, paper preparation |
| Revision & Submission | Months 10-12 | Conference submission, code release |

---

## Conclusion

This proposal presents Spreading Activation Memory Consolidation (SAMC), a parameter-free approach to memory consolidation for long-running LLM agents. By implementing cognitively-inspired dual-phase consolidation through pure graph operations, SAMC addresses the critical challenges of catastrophic forgetting and poor multi-hop recall without requiring gradient computation or risking degradation of base model capabilities. Through rigorous experimental validation against state-of-the-art baselines, we aim to demonstrate that SAMC achieves ≥15% improvement in long-term recall and ≥20% reduction in forgetting, while maintaining practical efficiency for production deployment. This research contributes both theoretical foundations for understanding memory consolidation in artificial agents and practical tools for building more capable, persistent conversational AI systems.