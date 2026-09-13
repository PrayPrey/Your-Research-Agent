# Research Proposal: Hierarchical Explainable Multi-Agent Reinforcement Learning for Regulatory-Compliant Financial Trading via Active Inference

## 1. Introduction

### 1.1 Background

The financial industry is experiencing unprecedented transformation driven by artificial intelligence, with multi-agent reinforcement learning (MARL) systems increasingly deployed for algorithmic trading, portfolio optimization, and market-making operations. These systems demonstrate remarkable performance in capturing complex market dynamics and executing sophisticated trading strategies. However, a critical tension has emerged between algorithmic performance and regulatory compliance requirements.

Recent regulatory frameworks, including the European Union's AI Act and the Markets in Financial Instruments Directive II (MiFID II), mandate transparent and auditable decision-making processes for automated trading systems. These regulations require financial institutions to provide clear explanations of how AI systems arrive at trading decisions, particularly for high-stakes operations that may impact market stability. Current industry practice relies predominantly on post-hoc explanation methods such as SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) to interpret black-box trading algorithms. However, these approaches achieve only approximately 30% audit trail completeness, as they provide feature importance rankings rather than causal decision traces.

This explainability gap poses significant challenges for regulatory compliance, operator trust, and systemic risk management. Compliance officers struggle to validate trading decisions, regulators cannot effectively audit algorithmic behavior, and operators lack the transparency needed to intervene appropriately during market stress events. The fundamental limitation of post-hoc methods is their inability to reconstruct the actual decision-making process—they approximate explanations rather than revealing inherent decision logic.

### 1.2 Research Objectives

This research proposes a novel framework called Hierarchical Explainable Multi-Agent Reinforcement Learning (AI-HXMARL) that addresses the explainability-performance tension through Active Inference-based agent architectures. Our primary objectives are:

1. **Develop inherently explainable multi-agent trading systems** by replacing standard RL agents with Active Inference-based agents whose decisions naturally decompose via expected free energy minimization.

2. **Establish hierarchical explanation structures** that provide audit trails at three levels: agent-level (individual decision decomposition), interaction-level (belief propagation between agents), and system-level (collective behavior landscapes).

3. **Validate regulatory compliance capability** by demonstrating >90% audit trail completeness while maintaining trading performance within ±5% of state-of-the-art MARL baselines.

4. **Assess practical deployment feasibility** through compliance officer trust studies and computational overhead analysis.

### 1.3 Significance

This research addresses a critical gap in financial AI by providing the first framework for inherently explainable multi-agent trading systems. Unlike post-hoc explanation methods that approximate decision rationales, Active Inference agents produce explanations as a natural byproduct of their decision-making process. The expected free energy formulation mathematically separates into pragmatic (exploitation/reward-seeking) and epistemic (exploration/uncertainty-reduction) components, creating interpretable audit trails without computational approximation.

The significance extends across multiple dimensions: (1) regulatory compliance through complete decision traceability, (2) enhanced operator trust enabling appropriate human oversight, (3) improved systemic risk management through transparent multi-agent interactions, and (4) theoretical advancement in explainable AI for complex multi-agent systems. Success in this research would establish a new paradigm for responsible AI deployment in high-stakes financial applications.

## 2. Methodology

### 2.1 Theoretical Foundation: Active Inference Framework

Active Inference provides a principled framework for decision-making based on minimizing expected free energy. Unlike standard RL agents that maximize expected cumulative reward, Active Inference agents maintain generative world models and select actions that minimize uncertainty about future states while achieving goals.

**Expected Free Energy Formulation:**

For an Active Inference agent, the expected free energy $G(\pi)$ for a policy $\pi$ decomposes as:

$$G(\pi) = \underbrace{\mathbb{E}_{Q(\tilde{o}|\pi)}[D_{KL}[Q(\tilde{s}|\tilde{o}, \pi) \| Q(\tilde{s}|\pi)]]}_{\text{Epistemic Value (Information Gain)}} + \underbrace{\mathbb{E}_{Q(\tilde{o}|\pi)}[D_{KL}[Q(\tilde{o}|\pi) \| P(\tilde{o})]]}_{\text{Pragmatic Value (Goal Achievement)}}$$

where $\tilde{o}$ represents future observations, $\tilde{s}$ represents future states, $Q$ denotes the approximate posterior distribution, and $P(\tilde{o})$ represents preferred observations (goals).

This decomposition is central to our explainability approach:
- **Epistemic component**: Quantifies the agent's drive to reduce uncertainty about market states
- **Pragmatic component**: Quantifies the agent's drive to achieve trading objectives (profit, risk management)

### 2.2 Agent Architecture Design

**2.2.1 Single Agent Structure**

Each Active Inference trading agent comprises:

1. **Generative World Model**: A probabilistic model $P(o_t, s_t | s_{t-1}, a_{t-1})$ that predicts market observations given latent states and actions. We implement this using a variational autoencoder architecture with temporal dynamics:

$$P(s_t | s_{t-1}, a_{t-1}) = \mathcal{N}(\mu_\theta(s_{t-1}, a_{t-1}), \Sigma_\theta(s_{t-1}, a_{t-1}))$$

$$P(o_t | s_t) = \mathcal{N}(g_\phi(s_t), \sigma^2 I)$$

2. **Belief Update Module**: Performs variational inference to update beliefs about market states:

$$Q(s_t | o_{1:t}, a_{1:t-1}) \propto P(o_t | s_t) \int P(s_t | s_{t-1}, a_{t-1}) Q(s_{t-1}) ds_{t-1}$$

3. **Policy Selection**: Selects actions by minimizing expected free energy:

$$a_t = \arg\min_a G(a) = \arg\min_a [G_{epistemic}(a) + G_{pragmatic}(a)]$$

4. **Explanation Logger**: Records the free energy decomposition for each decision:

$$\mathcal{E}_t = \{G_{epistemic}(a_t), G_{pragmatic}(a_t), Q(s_t), \text{precision}_t\}$$

**2.2.2 Multi-Agent Interaction Protocol**

For $N$ agents interacting in a market environment, we introduce precision-weighted belief propagation:

$$Q_i(s_t^{market}) = \sum_{j \neq i} \pi_{ij} \cdot Q_j(s_t^{market}) + \pi_{ii} \cdot Q_i^{local}(s_t^{market})$$

where $\pi_{ij}$ represents the precision (confidence) agent $i$ assigns to agent $j$'s beliefs. This creates traceable information flow between agents.

**Interaction Explanation Structure:**

$$\mathcal{I}_{ij,t} = \{\pi_{ij,t}, \Delta Q_i(s_t | j), \text{influence\_direction}_{ij}\}$$

### 2.3 Hierarchical Explanation Framework

**Level 1 - Agent Explanations:**
For each trading decision, we generate:
- Free energy decomposition: $\{G_{epistemic}, G_{pragmatic}\}$
- Belief state summary: Key market state beliefs with confidence intervals
- Action rationale: Natural language translation of dominant component

**Level 2 - Interaction Explanations:**
For agent pairs with significant interaction:
- Belief propagation traces: $\mathcal{I}_{ij,t}$ for all $(i,j)$ pairs where $|\Delta Q_i| > \epsilon$
- Influence networks: Directed graph of precision-weighted information flow
- Coordination patterns: Detected emergent behaviors (herding, contrarian)

**Level 3 - System Explanations:**
For the collective multi-agent system:
- Collective free energy landscape: $G_{system} = \sum_i G_i + G_{interaction}$
- Market impact attribution: Contribution of each agent to price movements
- Systemic risk indicators: Concentration of beliefs, coordination intensity

### 2.4 Data Collection and Experimental Design

**2.4.1 Data Sources**

We utilize public limit order book (LOB) data from:
- LOBSTER dataset (NASDAQ equities): High-frequency order flow data
- Binance historical data: Cryptocurrency market microstructure
- Simulated markets: Controlled environments for mechanism validation

Data preprocessing includes:
- Order book state representation: 10-level bid/ask prices and volumes
- Feature engineering: Mid-price, spread, order imbalance, volatility indicators
- Temporal aggregation: 1-minute, 5-minute, and daily frequencies

**2.4.2 Experimental Conditions**

| Condition | Agent Type | Explanation Method | Purpose |
|-----------|------------|-------------------|---------|
| AI-HXMARL | Active Inference | Inherent (Free Energy) | Proposed method |
| MARL-SHAP | PPO/DQN | Post-hoc SHAP | Baseline 1 |
| MARL-LIME | PPO/DQN | Post-hoc LIME | Baseline 2 |
| MARL-None | PPO/DQN | None | Performance reference |

**2.4.3 Simulation Environment**

We implement a multi-agent market simulation using JAX for GPU acceleration:
- Agent count: 10, 25, 50 agents (scalability analysis)
- Market mechanism: Continuous double auction with LOB
- Episode length: 1000 trading steps (approximately 1 trading day)
- Training episodes: 10,000 episodes per configuration

**2.4.4 Evaluation Metrics**

**Primary Metric - Audit Trail Completeness (ATC):**

$$ATC = \frac{\text{Decisions with complete causal trace}}{\text{Total decisions}} \times 100\%$$

A complete causal trace requires: (1) input state logged, (2) belief update recorded, (3) free energy decomposition computed, (4) action selection rationale documented.

**Secondary Metrics:**

1. **Explanation Fidelity (EF):** Counterfactual consistency score
$$EF = \frac{1}{M}\sum_{m=1}^{M} \mathbb{1}[\text{explanation}_m \text{ predicts counterfactual}_m]$$

2. **Trading Performance:** Sharpe ratio
$$SR = \frac{\mathbb{E}[R_p - R_f]}{\sigma_p}$$

3. **Operator Trust Score:** Standardized questionnaire (1-7 Likert scale) administered to compliance officers

4. **Computational Overhead:** Wall-clock time ratio
$$CO = \frac{T_{AI-HXMARL}}{T_{baseline}}$$

**2.4.5 Statistical Analysis Plan**

- **Sample sizes:** 30 trading sessions for completeness analysis, 15 compliance officers for trust study, 20 independent runs for performance comparison
- **Statistical tests:** 
  - Chi-squared test for ATC comparison (α = 0.05)
  - Paired t-test for trust improvement (α = 0.05)
  - Two One-Sided Tests (TOST) for performance equivalence (δ = 5%)

### 2.5 Implementation Details

**Algorithm 1: AI-HXMARL Training Loop**

```
Input: Market environment E, N agents, T timesteps
Output: Trained agents, Explanation database

Initialize: Generative models {θ_i}, Belief states {Q_i(s_0)}

For episode = 1 to num_episodes:
    Reset environment, initialize beliefs
    For t = 1 to T:
        For each agent i:
            1. Observe o_i,t from environment
            2. Update belief: Q_i(s_t) ← BeliefUpdate(Q_i(s_{t-1}), o_i,t, a_i,t-1)
            3. Compute expected free energy for each action:
               G_i(a) = G_epistemic(a) + G_pragmatic(a)
            4. Select action: a_i,t = argmin_a G_i(a)
            5. Log explanation: E_i,t = {G_epistemic, G_pragmatic, Q_i(s_t)}
        
        Execute actions, receive rewards
        Update precision weights: π_ij ← PrecisionUpdate(Q_i, Q_j)
        Log interactions: I_t = {π_ij, ΔQ_i}
    
    Update generative models via variational inference
    Compute system-level explanations

Return trained agents, explanation database
```

**Computational Requirements:**
- Hardware: 8× NVIDIA A100 GPUs
- Training time estimate: 48-72 hours per configuration
- Inference overhead target: <50% increase over baseline MARL

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (P1 - Audit Trail Completeness):**
We expect AI-HXMARL to achieve >90% audit trail completeness compared to <30% for post-hoc SHAP/LIME methods. This represents a fundamental improvement in decision traceability, as Active Inference agents inherently log their decision-making process rather than approximating explanations post-hoc.

**Secondary Outcomes:**

**P2 - Operator Trust:** We anticipate ≥50% improvement in compliance officer trust scores when using AI-HXMARL explanations. The interpretable decomposition into exploration (epistemic) and exploitation (pragmatic) components maps naturally to financial concepts of risk management and return optimization.

**P3 - Performance Preservation:** Trading performance (Sharpe ratio) is expected to remain within ±5% of non-explainable MARL baselines. Active Inference has been shown theoretically equivalent to optimal RL under certain conditions, and our architecture preserves this optimality while adding explainability.

**P4 - Scalability:** The system should maintain explanation quality with 10-50 agents, with computational overhead <50% compared to baseline MARL.

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. Audit trail completeness ≤ 50%
2. Free energy decomposition fails to distinguish pragmatic vs epistemic components in >80% of decisions
3. Sharpe ratio degrades >10% compared to baseline
4. Compliance officer trust improvement <25%

### 3.3 Scientific Impact

This research contributes to multiple scientific domains:

1. **Explainable AI:** First demonstration of inherently explainable multi-agent systems using Active Inference, advancing beyond post-hoc explanation paradigms.

2. **Multi-Agent Systems:** Novel framework for tracing information flow and coordination in multi-agent environments through precision-weighted belief propagation.

3. **Financial AI:** Practical methodology for regulatory-compliant algorithmic trading that maintains competitive performance.

4. **Active Inference Theory:** Extension of Active Inference from single-agent to multi-agent settings with hierarchical explanation structures.

### 3.4 Practical Impact

**Regulatory Compliance:** AI-HXMARL provides a pathway for financial institutions to deploy AI trading systems that satisfy EU AI Act and MiFID II requirements for algorithmic transparency.

**Risk Management:** Hierarchical explanations enable better monitoring of systemic risks arising from multi-agent interactions, supporting financial stability objectives.

**Industry Adoption:** By demonstrating that explainability need not sacrifice performance, this research removes a key barrier to responsible AI adoption in finance.

**Stakeholder Trust:** Improved operator trust enables more effective human-AI collaboration in trading operations, with humans able to understand and appropriately intervene in algorithmic decisions.

### 3.5 Limitations and Future Work

**Known Limitations:**
- Computational overhead may limit applicability to ultra-low-latency HFT
- Regulatory acceptance of free energy-based explanations requires validation
- Scalability beyond 100 agents requires approximate tracing methods

**Future Directions:**
- Extension to high-frequency trading with optimized inference
- Integration with natural language generation for automated compliance reports
- Application to other regulated domains (healthcare AI, autonomous vehicles)

This research establishes a foundation for responsible AI deployment in high-stakes financial applications, demonstrating that transparency and performance can coexist in complex multi-agent systems.