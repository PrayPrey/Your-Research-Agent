# Compositional Verification for Multi-Agent LLM Systems via Formal Contracts

## 1. Introduction

### Background

The rapid advancement of Large Language Model (LLM) agents has led to their deployment in increasingly complex multi-agent environments, from autonomous trading systems to collaborative robotics and distributed decision-making platforms. While single-agent systems have been the primary focus of existing safety research, multi-agent systems introduce fundamentally different challenges: emergent behaviors arising from agent interactions, cascading failures that propagate through agent networks, potential collusion between agents, and correlated vulnerabilities that manifest only during specific interaction patterns.

Recent work has demonstrated alarming vulnerabilities in multi-agent LLM systems. Fang et al. (2024) showed that teams of LLM agents can autonomously exploit zero-day vulnerabilities through coordinated action, while Xu et al. (2025) identified the Trust-Vulnerability Paradox, where the very mechanisms enabling effective collaboration also create security risks through over-exposure and over-authorization. These findings underscore a critical gap: existing verification and testing approaches primarily evaluate agents in isolation, fundamentally missing interaction-dependent failures that only manifest in multi-agent contexts.

Current safety evaluation methods face severe scalability limitations. Exhaustive testing of all possible agent interaction scenarios grows exponentially with the number of agents, making comprehensive evaluation intractable for realistic systems. While frameworks like SENTINEL (Zhan et al., 2025) provide multi-level verification for embodied agents and Pro2Guard (Wang et al., 2025) offers proactive runtime enforcement, these approaches do not fully address the compositional nature of multi-agent safety—the ability to derive system-level guarantees from component-level properties without analyzing the complete system state space.

### Research Objectives

This research proposes a **compositional verification framework** for multi-agent LLM systems based on formal contracts. Our primary objectives are:

1. **Develop a formal contract language** that captures safety specifications for individual LLM agents, including pre/post-conditions, interaction protocols, and resource bounds, expressed in a computationally tractable subset of temporal logic.

2. **Create automated contract synthesis methods** that translate natural language safety specifications into formal contracts using LLM-based translation with verification feedback loops.

3. **Establish compositional reasoning principles** that enable verification of system-level safety properties (e.g., absence of collusion, deadlock-freedom, privacy preservation) from individual agent contracts and well-defined composition rules.

4. **Implement efficient runtime monitoring** that detects contract violations during agent execution with minimal computational overhead, providing early warning of safety breaches.

5. **Build a reusable library of safety contracts** for common agent roles and interaction patterns, enabling rapid deployment of verified multi-agent systems.

### Significance

This research addresses critical gaps in safe multi-agent AI deployment. By enabling compositional verification, we can provide formal safety guarantees for systems of arbitrary scale without exhaustive testing. The automated contract synthesis approach makes formal methods accessible to practitioners without extensive verification expertise. Runtime monitoring provides a practical safety layer for deployed systems, catching violations that may arise from distribution shift or adversarial manipulation.

The impact extends across multiple domains: autonomous trading systems can be verified to prevent market manipulation through collusion; collaborative robotics can guarantee collision-free operation under all interaction scenarios; distributed decision-making systems can ensure privacy and fairness properties. By developing reusable contract libraries, we accelerate safe deployment of multi-agent systems while establishing a foundation for regulatory compliance in high-stakes applications.

## 2. Methodology

### 2.1 Formal Contract Language Design

We develop a contract specification language **AgentContract-TL** (Agent Contract Temporal Logic) that extends linear temporal logic (LTL) with agent-specific constructs. Each agent $A_i$ in a multi-agent system is associated with a contract $C_i = (P_i, Q_i, R_i, I_i)$ where:

- **Pre-conditions** $P_i$: Predicates over input states that must hold before agent actions
- **Post-conditions** $Q_i$: Predicates over output states guaranteed after agent actions  
- **Resource bounds** $R_i$: Constraints on computational resources, API calls, and environmental impact
- **Interaction protocols** $I_i$: Temporal specifications governing multi-agent communication

Formally, we define the syntax:

$$\phi ::= p \mid \neg\phi \mid \phi_1 \land \phi_2 \mid \mathbf{X}\phi \mid \phi_1 \mathbf{U} \phi_2 \mid \text{send}(A_i, A_j, m) \mid \text{receive}(A_i, A_j, m)$$

where $p$ represents atomic propositions over agent states, $\mathbf{X}$ is the "next" operator, $\mathbf{U}$ is "until", and send/receive capture inter-agent communication events. We extend this with resource predicates:

$$\text{resources}(A_i, t) \leq R_i$$

where $\text{resources}(A_i, t)$ tracks cumulative resource consumption by agent $A_i$ at time $t$.

### 2.2 Automated Contract Synthesis

We develop a three-stage pipeline for translating natural language safety specifications to formal contracts:

**Stage 1: Specification Parsing**
Given a natural language safety requirement $S$, we use a fine-tuned LLM to generate an initial formal specification $\phi_0$:

$$\phi_0 = \text{LLM}_{\text{synthesis}}(S, \mathcal{E})$$

where $\mathcal{E}$ represents few-shot examples from our contract library. We fine-tune GPT-4 or similar models on a dataset of 10,000+ paired natural language specifications and formal contracts across diverse domains (trading, robotics, information systems).

**Stage 2: Verification Feedback Loop**
We employ a satisfiability checker and model checker to validate $\phi_0$:

1. Check syntactic correctness and type safety
2. Verify satisfiability (ensure $\phi_0$ is not trivially false)
3. Check for common specification errors (vacuous truth, unrealizable constraints)

If verification fails, we generate natural language feedback $F$ describing the error and prompt the LLM to refine:

$$\phi_{k+1} = \text{LLM}_{\text{synthesis}}(S, \mathcal{E}, \phi_k, F_k)$$

This iterates until verification succeeds or a maximum iteration count is reached.

**Stage 3: Contract Instantiation**
The verified specification $\phi^*$ is decomposed into contract components $(P, Q, R, I)$ through template matching and structural analysis. We maintain templates for common patterns:

- Mutex patterns: $\mathbf{G}(\text{state}_1 \to \neg\text{state}_2)$
- Response patterns: $\mathbf{G}(\text{request} \to \mathbf{F}\text{response})$
- Bounded response: $\mathbf{G}(\text{request} \to \mathbf{F}^{\leq k}\text{response})$

### 2.3 Compositional Verification

The core innovation is deriving system-level properties from agent contracts through compositional reasoning. For a system $S = \{A_1, \ldots, A_n\}$ with contracts $C_1, \ldots, C_n$, we verify global property $\Psi$ by:

**Assume-Guarantee Reasoning**
Each agent $A_i$ is verified under the assumption that other agents satisfy their contracts:

$$C_1 \land \cdots \land C_n \models \Psi$$

We employ circular assume-guarantee rules. To prove $C_1 \land C_2 \models \Psi$, we:
1. Prove $C_1 \land M_2 \models \Psi_1$ (agent 1 satisfies its part under agent 2's abstraction)
2. Prove $M_1 \land C_2 \models \Psi_2$ (agent 2 satisfies its part under agent 1's abstraction)
3. Combine: $\Psi_1 \land \Psi_2 \implies \Psi$

where $M_i$ is an abstract model (interface specification) of agent $A_i$ derived from $C_i$.

**Interaction Protocol Verification**
For interaction protocols $I_1, \ldots, I_n$, we construct a product automaton:

$$\mathcal{A}_{\text{system}} = \mathcal{A}_{I_1} \times \cdots \times \mathcal{A}_{I_n}$$

and verify properties on this automaton using efficient model checking algorithms (symbolic execution, bounded model checking). We prove:

- **Deadlock freedom**: $\mathbf{G}(\bigvee_{i=1}^n \text{enabled}(A_i))$
- **No collusion**: $\neg \exists t. \bigwedge_{i \in \text{Coalition}} \text{violates}(A_i, \text{policy}, t)$
- **Privacy preservation**: Information flow properties using taint analysis

**Resource Composition**
For resource bounds, we compute the system-level resource consumption:

$$R_{\text{system}} = \sum_{i=1}^n R_i + \Delta R_{\text{interaction}}$$

where $\Delta R_{\text{interaction}}$ captures overhead from inter-agent communication, computed from interaction protocol specifications.

### 2.4 Runtime Monitoring

We implement a lightweight runtime monitor that checks contract compliance during execution:

**Monitor Architecture**
Each agent is instrumented with a local monitor $M_i$ that:
1. Intercepts agent inputs/outputs
2. Maintains a trace $\tau_i = s_0 \xrightarrow{a_0} s_1 \xrightarrow{a_1} \cdots$ of agent states and actions
3. Evaluates contract predicates incrementally

For temporal formulas, we use three-valued LTL semantics (true, false, unknown) enabling evaluation on finite prefixes:

$$[\![\phi]\!]_{\tau, t} \in \{\top, \bot, ?\}$$

**Violation Detection**
A violation is detected when $[\![C_i]\!]_{\tau_i, t} = \bot$. We distinguish:
- **Hard violations**: Definitive safety breaches requiring immediate intervention
- **Soft violations**: Potential issues triggering alerts but not halting execution
- **Resource violations**: Exceeding resource bounds $R_i$

**Intervention Strategies**
Upon violation detection, the monitor can:
1. **Block action**: Prevent the violating action from executing
2. **Retry with constraints**: Provide additional constraints to the agent's prompt
3. **Escalate**: Hand off control to human operators

**Overhead Optimization**
To minimize monitoring overhead, we employ:
- **Sampling**: Monitor only critical decision points rather than every state transition
- **Static analysis**: Pre-compute which contract clauses are relevant for specific code paths
- **Lazy evaluation**: Delay expensive checks until necessary

We target <5% runtime overhead for monitoring, validated through empirical measurement.

### 2.5 Experimental Design

**Benchmark Suite Development**
We create a comprehensive benchmark suite covering:

1. **Autonomous Trading Agents** (5-20 agents): Verify no market manipulation, price discovery fairness, no insider trading
2. **Collaborative Robotics** (3-10 agents): Collision avoidance, task completion guarantees, resource sharing fairness
3. **Distributed Decision Systems** (10-50 agents): Privacy preservation, consensus properties, Byzantine fault tolerance
4. **Information Retrieval Agents** (5-15 agents): No data leakage, query privacy, result consistency

**Evaluation Metrics**

*Verification Effectiveness:*
- **Coverage**: Percentage of known vulnerabilities detected
- **False positive rate**: Proportion of flagged violations that are not genuine safety issues
- **Completeness**: Ability to verify target properties (proportion provable vs. requiring exhaustive testing)

*Scalability:*
- **Verification time**: $T_{\text{verify}}(n)$ as a function of agent count $n$
- **Contract synthesis time**: Time to generate contracts from specifications
- **Memory consumption**: Peak memory usage during verification

*Runtime Performance:*
- **Monitoring overhead**: $(T_{\text{monitored}} - T_{\text{baseline}})/T_{\text{baseline}}$
- **Detection latency**: Time from violation occurrence to detection
- **Intervention effectiveness**: Success rate of violation prevention

**Baseline Comparisons**
We compare against:
1. **Exhaustive testing**: Complete state space exploration (where tractable)
2. **SENTINEL** (Zhan et al., 2025): Multi-level verification framework
3. **AgentSpec** (Wang et al., 2025): Runtime constraint enforcement
4. **Pro2Guard** (Wang et al., 2025): Probabilistic proactive enforcement

**Ablation Studies**
We conduct ablation studies on:
- Contract synthesis: LLM-based vs. manual vs. template-based
- Compositional reasoning: With vs. without assume-guarantee rules
- Monitoring strategies: Full vs. sampled vs. critical-path-only

**Case Studies**
We conduct in-depth case studies on:
1. A real-world cryptocurrency trading system (with simulated transactions)
2. A multi-robot warehouse automation system
3. A distributed healthcare information system (synthetic data)

For each case study, we document:
- Safety requirements elicitation process
- Contract specification and synthesis
- Verification results and discovered vulnerabilities
- Runtime monitoring effectiveness over extended operation periods

## 3. Expected Outcomes & Impact

### Primary Research Contributions

**1. Theoretical Foundations**
We expect to establish theoretical results on:
- **Soundness**: Compositional verification guarantees that if individual contracts are satisfied and composition rules hold, then system-level properties hold
- **Completeness bounds**: Characterization of which properties are verifiable compositionally vs. requiring full system analysis
- **Complexity analysis**: Proof that compositional verification reduces complexity from $O(|S|^n)$ (full state space) to $O(n \cdot |S| \cdot \log n)$ for systems with $n$ agents and average state space size $|S|$

**2. Practical Tools and Artifacts**
- **AgentContract-TL compiler**: Tool for parsing and validating contract specifications
- **ContractSynth**: LLM-based automated contract synthesis system
- **CompoVerify**: Compositional verification engine implementing assume-guarantee reasoning
- **RuntimeGuard**: Lightweight monitoring framework with <5% overhead
- **ContractLib**: Open library of 100+ reusable safety contracts for common agent patterns

**3. Empirical Findings**
Based on preliminary experiments, we anticipate:
- Detection of 85-95% of known multi-agent vulnerabilities (vs. 60-70% for baseline methods)
- 10-100× speedup in verification time compared to exhaustive testing for systems with >5 agents
- False positive rate <10% for contract synthesis with verification feedback
- Successful deployment in case studies demonstrating practical applicability

### Broader Impact

**Enabling Safe Multi-Agent AI Deployment**
This framework provides the first scalable approach to formally verifying safety properties in multi-agent LLM systems. Organizations can deploy agent teams with provable guarantees on critical properties like privacy, fairness, and security, enabling adoption in regulated industries (finance, healthcare, autonomous vehicles) where informal testing is insufficient.

**Advancing Formal Methods for AI**
By bridging LLMs and formal verification, we make formal methods accessible to practitioners without specialized expertise. The automated contract synthesis approach democratizes safety verification, while the compositional framework provides a template for scaling formal methods to large AI systems.

**Regulatory and Compliance Applications**
As governments develop AI safety regulations, our framework provides technical foundations for compliance. The formal contracts serve as auditable specifications of system behavior, while runtime monitoring provides evidence of operational compliance. This supports regulatory frameworks like the EU AI Act requiring documented safety measures for high-risk AI systems.

**Research Community Impact**
We will release all tools, benchmarks, and contract libraries as open-source resources, fostering a research community around formal verification for multi-agent AI. The benchmark suite will provide standardized evaluation for future research, while the contract library accelerates development of new verified systems.

### Limitations and Future Work

**Known Limitations:**
- Contract synthesis quality depends on LLM capabilities and training data coverage
- Compositional verification may be incomplete for some emergent properties requiring full system reasoning
- Runtime monitoring introduces overhead, limiting applicability to latency-critical systems
- Adversarial agents may attempt to satisfy contracts superficially while violating intent

**Future Research Directions:**
- **Adaptive contracts**: Contracts that evolve based on observed agent behavior and environment changes
- **Adversarial robustness**: Verification under adversarial agent manipulation
- **Probabilistic contracts**: Extending to systems with uncertainty and learning agents
- **Human-agent collaboration**: Contracts governing human-AI interaction patterns
- **Cross-organizational verification**: Verifying properties across organizational boundaries where agent internals are private

This research establishes foundational capabilities for safe multi-agent AI, with immediate practical applications and a clear path toward increasingly sophisticated verification as the technology matures.