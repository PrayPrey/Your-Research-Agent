# Research Proposal: StigmaLLM: Stigmergic Coordination via Hierarchical Semantic Pheromone Fields for Multi-Agent Urban Navigation

## 1. Introduction

### 1.1 Background

The emergence of Large Language Models (LLMs) has revolutionized artificial intelligence, demonstrating remarkable capabilities in reasoning, planning, and natural language understanding. However, when deployed as embodied agents in open urban environments, LLM-based systems face significant challenges that remain largely unsolved. Unlike controlled indoor settings where substantial progress has been made, outdoor city environments present unique complexities: vast spatial scales spanning kilometers, dynamic obstacles including pedestrians and vehicles, unpredictable environmental conditions, and the need for real-time coordination among multiple agents.

Current approaches to multi-agent LLM coordination predominantly rely on direct peer-to-peer communication paradigms. Methods such as CAMON employ centralized communication with dynamic leadership, while SAMALM utilizes decentralized actor-critic architectures for social-aware navigation. Although these approaches have demonstrated promising results in constrained scenarios, they suffer from fundamental scalability limitations. Direct communication methods exhibit $O(N^2)$ message complexity as agent count increases, creating prohibitive communication overhead for deployments involving eight or more agents. More critically, these systems experience catastrophic failure under communication disruptions—a common occurrence in real-world urban deployments where signal interference, network congestion, and infrastructure failures are inevitable.

Biological systems have evolved elegant solutions to similar coordination challenges through stigmergy—indirect communication via environmental markers. Ant colonies coordinate foraging activities through pheromone trails without requiring direct ant-to-ant communication. This mechanism enables robust, scalable coordination that gracefully degrades under individual failures rather than experiencing system-wide collapse. Recent advances in swarm robotics, particularly the automatic design of stigmergic behaviors demonstrated in Nature 2024, have validated the feasibility of implementing stigmergy-based coordination in artificial systems.

### 1.2 Research Objectives

This research proposes **StigmaLLM**, a novel framework that bridges swarm intelligence principles with LLM reasoning capabilities to enable robust, scalable multi-agent coordination in open urban environments. Our primary objectives are:

1. **Develop Hierarchical Semantic Pheromone Fields (H-SPF):** Design and implement an octree-based spatial memory structure that supports typed semantic pheromones (EXPLORE, OBSTACLE, CROWD, GOAL) with temporal decay mechanisms.

2. **Establish O(1) Communication Complexity:** Demonstrate that per-agent communication load remains constant regardless of total agent count, enabling scalable coordination for 8-16+ agents.

3. **Achieve Failure-Resilient Coordination:** Validate that stigmergic coordination maintains task completion with less than 20% degradation under 50% communication failure rates.

4. **Outperform Direct Communication Baselines:** Show statistically significant improvements over CAMON and SAMALM in coordination efficiency, scalability, and resilience metrics.

### 1.3 Research Significance

This research addresses a critical gap in embodied AI for urban environments, with significant implications for multiple application domains. Search-and-rescue operations require rapid, coordinated exploration of disaster-affected urban areas where communication infrastructure may be compromised. Multi-robot delivery systems in smart cities demand scalable coordination without centralized bottlenecks. Autonomous vehicle coordination for traffic optimization requires resilient communication mechanisms that function under adverse conditions.

By establishing stigmergic coordination as a viable paradigm for LLM-based agents, this work contributes both theoretical foundations and practical methodologies that advance the field of embodied intelligence in open city environments.

## 2. Methodology

### 2.1 System Architecture Overview

The StigmaLLM framework consists of four integrated components: (1) Semantic Pheromone Representation, (2) Octree-based Spatial Memory, (3) Hierarchical Propagation Mechanism, and (4) Pheromone-Augmented LLM Reasoning.

### 2.2 Semantic Pheromone Representation

We define four typed semantic pheromones that capture essential coordination information:

**Definition 1 (Semantic Pheromone):** A semantic pheromone $\phi$ is a tuple:
$$\phi = (type, intensity, timestamp, agent\_id, position)$$

where $type \in \{EXPLORE, OBSTACLE, CROWD, GOAL\}$, $intensity \in [0, 1]$, $timestamp \in \mathbb{R}^+$, $agent\_id \in \mathbb{N}$, and $position \in \mathbb{R}^3$.

Each pheromone type serves a distinct coordination function:
- **EXPLORE:** Marks visited regions to prevent redundant exploration
- **OBSTACLE:** Indicates detected obstacles or hazards
- **CROWD:** Signals high pedestrian/vehicle density for social-aware navigation
- **GOAL:** Marks discovered targets or objectives

Pheromone intensity decays exponentially over time:
$$I(t) = I_0 \cdot e^{-\frac{t - t_0}{\tau}}$$

where $I_0$ is initial intensity, $t_0$ is deposit timestamp, and $\tau$ is the decay time constant. We investigate $\tau \in \{10s, 30s, 60s\}$ to determine optimal information currency.

### 2.3 Octree-based Spatial Memory

The spatial memory utilizes an octree structure with depth $d = 8$ and base resolution $r = 0.5m$, covering a $128m \times 128m \times 128m$ volume per octree (multiple octrees tile larger environments).

**Definition 2 (Octree Node):** Each node $n$ at depth $l$ maintains:
$$n = (bounds, children[8], pheromones[], aggregates)$$

where $bounds$ defines spatial extent, $children$ contains child node references (null for leaves), $pheromones$ stores local pheromone list, and $aggregates$ contains hierarchically propagated statistics.

**Pheromone Write Operation:** When agent $a$ deposits pheromone $\phi$ at position $p$:

```
Algorithm 1: PheromoneWrite(octree, φ, p)
1: node ← octree.root
2: while node.depth < max_depth do
3:     child_idx ← ComputeOctant(p, node.bounds)
4:     if node.children[child_idx] is null then
5:         node.children[child_idx] ← CreateNode()
6:     node ← node.children[child_idx]
7: node.pheromones.append(φ)
8: PropagateAggregates(node)  // Update parent statistics
```

**Complexity Analysis:** Write operations require $O(\log d) = O(8) = O(1)$ traversal steps for fixed depth.

### 2.4 Hierarchical Propagation Mechanism

Parent nodes maintain aggregated pheromone statistics from children, enabling multi-scale queries:

**Definition 3 (Aggregate Statistics):** For node $n$ with children $C$:
$$agg_n^{type} = \left( \max_{c \in C} I_c^{type}, \max_{c \in C} t_c^{type}, \sum_{c \in C} count_c^{type} \right)$$

This enables coarse-to-fine queries: agents first query parent nodes for regional pheromone presence, then drill down to leaves only when relevant signals exist.

**Pheromone Read Operation:** Agents query a bounded perception window $W$ centered at current position:

```
Algorithm 2: PheromoneRead(octree, position, radius)
1: window ← BoundingBox(position, radius)
2: relevant_nodes ← []
3: QueryOctree(octree.root, window, relevant_nodes)
4: pheromones ← []
5: for node in relevant_nodes do
6:     for φ in node.pheromones do
7:         if φ.intensity > threshold then
8:             pheromones.append(ApplyDecay(φ, current_time))
9: return AggregatePheromones(pheromones)
```

**Complexity Analysis:** With fixed perception radius $r$, the query intersects $O(1)$ leaf nodes regardless of total agent count, achieving constant per-agent communication complexity.

### 2.5 Pheromone-Augmented LLM Reasoning

Retrieved pheromone state is formatted as structured context for LLM navigation decisions:

**Prompt Template:**
```
[AGENT_STATE]
Position: (x, y, z), Heading: θ, Goal: (gx, gy, gz)

[PHEROMONE_CONTEXT]
EXPLORE: {direction: NE, intensity: 0.8, age: 5s, gradient: -0.2}
EXPLORE: {direction: SW, intensity: 0.3, age: 25s, gradient: +0.1}
OBSTACLE: {direction: N, intensity: 0.9, age: 2s, distance: 5m}
CROWD: {direction: E, intensity: 0.6, age: 10s}

[TASK]
Navigate toward goal while avoiding redundant exploration and obstacles.
Select action from: {FORWARD, LEFT, RIGHT, BACKWARD, WAIT}
```

The LLM reasons about pheromone gradients to produce navigation decisions:
- High EXPLORE intensity → region already covered → avoid
- Positive EXPLORE gradient → approaching unexplored frontier → attractive
- High OBSTACLE intensity → hazard nearby → avoid
- High CROWD intensity → congested area → social-aware detour

### 2.6 Experimental Design

#### 2.6.1 Simulation Environment

Experiments utilize the **EmbodiedCity** simulator with the **Multi-Agent CityEQA** benchmark extension. The environment covers a 1 km² urban area with realistic building geometry, road networks, pedestrian dynamics, and vehicle traffic.

**Environment Parameters:**
- Map size: 1000m × 1000m
- Building count: ~200 structures
- Dynamic pedestrians: 500-1000
- Dynamic vehicles: 100-200
- Simulation timestep: 0.5s

#### 2.6.2 Task Design

We evaluate on three task categories:

1. **Collaborative Exploration:** Agents must collectively explore and map an unknown urban region, minimizing overlap and maximizing coverage within time limits.

2. **Multi-Target Search:** Agents search for multiple hidden targets (simulating search-and-rescue), with success measured by targets found and time efficiency.

3. **Coordinated Navigation:** Agents navigate from distributed starting positions to assigned goals while avoiding collisions and minimizing total path length.

#### 2.6.3 Independent Variables

| Variable | Values | Rationale |
|----------|--------|-----------|
| Agent count | 2, 4, 8, 12, 16 | Test scalability hypothesis |
| Communication failure rate | 0%, 25%, 50%, 75% | Test resilience hypothesis |
| Pheromone decay rate (τ) | 10s, 30s, 60s | Optimize information currency |

#### 2.6.4 Baseline Methods

1. **CAMON (2024):** Centralized LLM coordination with dynamic leadership
2. **SAMALM (2025):** Decentralized actor-critic multi-agent LLM
3. **MMCNav (2025):** Multi-agent outdoor VLN with perception-cognition-action loop
4. **Random Baseline:** Agents make random navigation decisions
5. **Greedy Baseline:** Agents navigate directly toward goals without coordination

#### 2.6.5 Evaluation Metrics

**Primary Metrics:**

1. **Per-Agent Communication Load:**
$$L_{comm} = \frac{\sum_{t} (reads_t + writes_t)}{T \cdot N}$$
where $T$ is total timesteps and $N$ is agent count.

2. **Coordination Efficiency:**
$$E_{coord} = 1 - \frac{\sum_{i,j} overlap(traj_i, traj_j)}{\sum_i length(traj_i)}$$

3. **Task Completion Rate:**
$$R_{complete} = \frac{tasks\_completed}{tasks\_total}$$

4. **Failure Degradation:**
$$D_{failure} = \frac{R_{complete}^{0\%} - R_{complete}^{50\%}}{R_{complete}^{0\%}}$$

**Secondary Metrics:**
- Average path length to goal
- Time to task completion
- Collision rate
- LLM inference latency

#### 2.6.6 Statistical Analysis

**Sample Size:** 20 runs per configuration with different random seeds, totaling 1,200 experimental runs across all conditions.

**Statistical Tests:**
- Paired t-tests for method comparisons (same seeds)
- Bonferroni correction for multiple comparisons ($\alpha = 0.05/k$)
- Effect size reporting via Cohen's d
- 95% confidence intervals for all metrics

**Success Criteria:**
- P1 (Scalability): Communication load regression slope < 0.1 for StigmaLLM vs > 0.5 for baselines
- P2 (Efficiency): Coordination efficiency exceeds baselines by > 15 percentage points ($p < 0.05$)
- P3 (Resilience): Failure degradation < 20% for StigmaLLM vs > 50% for baselines

### 2.7 Implementation Details

**LLM Configuration:** GPT-4 or Claude-3 with temperature 0.3 for consistent reasoning. Maximum context length 4096 tokens with pheromone context limited to 512 tokens.

**Octree Parameters:** Depth 8, base resolution 0.5m, maximum pheromones per node 100 (oldest evicted when exceeded).

**Agent Configuration:** Perception radius 20m, action frequency 2 Hz, maximum speed 1.5 m/s.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical analysis and preliminary investigations, we anticipate the following outcomes:

**Scalability (P1):** StigmaLLM will demonstrate constant $O(1)$ per-agent communication load as agent count scales from 2 to 16. Specifically, we expect per-agent operations to remain within 10-15 read/write operations per timestep regardless of total agents, while CAMON and SAMALM will show linear or quadratic growth reaching 50-100+ operations at 16 agents.

**Coordination Efficiency (P2):** The stigmergic mechanism will reduce redundant exploration by 15-25% compared to direct communication baselines. EXPLORE pheromones will effectively mark visited regions, enabling agents to prioritize unexplored frontiers without explicit coordination messages.

**Failure Resilience (P3):** Under 50% communication failure, StigmaLLM task completion will degrade by less than 20% (from ~85% to ~70%), while direct communication methods will experience greater than 50% degradation (from ~80% to ~35%). The persistence of pheromones in spatial memory provides coordination continuity even when real-time communication fails.

**Optimal Decay Rate:** We expect $\tau = 30s$ to provide the best balance between information currency and persistence, though this may vary by task type (shorter for dynamic tasks, longer for exploration).

### 3.2 Theoretical Contributions

This research establishes the first formal framework for stigmergic coordination among LLM-based embodied agents. Key theoretical contributions include:

1. **Semantic Pheromone Formalization:** Mathematical definition of typed, decaying semantic pheromones suitable for LLM reasoning, extending biological stigmergy concepts to semantic communication.

2. **Complexity Analysis:** Formal proof that hierarchical pheromone fields achieve $O(1)$ local perception and $O(\log d)$ hierarchical queries, establishing theoretical foundations for scalable coordination.

3. **Emergent Coordination Theory:** Analysis of how local pheromone-following behaviors produce emergent collective coordination without centralized planning.

### 3.3 Practical Impact

**Search and Rescue:** StigmaLLM enables deployment of 10+ coordinated drones or ground robots in disaster-affected urban areas where communication infrastructure is compromised. The failure-resilient design ensures continued operation even with significant communication disruptions.

**Autonomous Delivery:** Multi-robot delivery fleets can coordinate efficiently without centralized servers, reducing infrastructure costs and single points of failure. Pheromone-based coordination naturally handles dynamic fleet sizes as robots join or leave.

**Smart City Infrastructure:** The framework provides a foundation for coordinated autonomous systems in smart cities, from traffic management to environmental monitoring, with graceful scalability as deployments expand.

### 3.4 Benchmark Contributions

We will release the **Multi-Agent CityEQA** benchmark extension, including:
- Standardized multi-agent task definitions for urban navigation
- Evaluation protocols and metrics for coordination assessment
- Baseline implementations for reproducible comparisons
- Simulation configurations for consistent experimental conditions

### 3.5 Limitations and Future Directions

**Current Limitations:**
- Discrete semantic pheromones may not capture continuous gradient information as effectively as biological systems
- LLM inference latency (~500ms) limits real-time responsiveness for high-speed scenarios
- Pheromone decay rates may require task-specific tuning

**Future Directions:**
- Extension to continuous pheromone representations using neural field networks
- Integration with visual-language models for richer environmental perception
- Transfer learning of pheromone policies across different urban environments
- Hardware deployment on physical robot platforms

### 3.6 Conclusion

StigmaLLM represents a paradigm shift from direct peer-to-peer communication to environment-mediated stigmergic coordination for LLM-based embodied agents. By leveraging hierarchical semantic pheromone fields on octree spatial memory, we enable scalable, efficient, and failure-resilient multi-agent coordination in open urban environments. This research advances both theoretical understanding and practical capabilities for embodied AI in city-scale deployments, opening new possibilities for search-and-rescue, autonomous delivery, and smart city applications.