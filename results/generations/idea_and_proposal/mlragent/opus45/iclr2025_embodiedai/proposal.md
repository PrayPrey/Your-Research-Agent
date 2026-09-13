# Research Proposal: Hierarchical Spatial Memory Networks for Long-Horizon Navigation of LLM Agents in Open City Environments

## 1. Introduction

### Background

The development of embodied artificial intelligence in open city environments represents one of the most challenging frontiers in modern AI research. While large language models (LLMs) have demonstrated remarkable capabilities in text understanding, reasoning, and generation, their application to embodied tasks in large-scale outdoor environments remains significantly limited. A fundamental barrier is the lack of persistent, structured spatial memory—a capability that humans naturally possess through cognitive maps developed over a lifetime of navigation experience.

Human spatial cognition operates through hierarchical mental representations that span multiple abstraction levels. Cognitive science research has established that humans construct spatial knowledge at the level of landmarks (distinctive locations), routes (paths connecting landmarks), and survey knowledge (bird's-eye view regional understanding). This hierarchical organization enables efficient navigation, shortcut discovery, backtracking, and reasoning about locations never directly observed together. In contrast, current LLM agents process spatial information in a flat, context-limited manner, constrained by token limitations and lacking mechanisms for persistent spatial memory accumulation.

Recent advances have begun addressing aspects of this challenge. Mem4Nav (He et al., 2025) introduced hierarchical spatial-cognition memory combining octree structures with semantic topology graphs. CityNavAgent (Zhang et al., 2025) demonstrated the value of hierarchical semantic planning with global memory for aerial navigation. SSR-ZSON (Meng et al., 2025) showed how spatial-semantic relations within hierarchical frameworks improve zero-shot object navigation. However, these approaches have not fully captured the multi-level abstraction characteristic of human cognitive maps, nor have they demonstrated robust generalization across diverse urban environments.

### Research Objectives

This research proposes the development of a **Hierarchical Spatial Memory Network (HSMN)** that augments LLM agents with a biologically-inspired, multi-level spatial memory structure. Our specific objectives are:

1. To design and implement a three-layer hierarchical memory architecture consisting of landmark, route, and region layers that mirrors human cognitive map organization.
2. To develop a graph neural network-based mechanism for dynamically updating this hierarchy during exploration and enabling efficient memory retrieval based on task requirements.
3. To evaluate HSMN on city-scale navigation benchmarks, measuring improvements in success rate, path efficiency, and generalization to unseen urban areas.
4. To demonstrate the interpretability of HSMN memory structures for enhanced human-agent collaboration in urban applications.

### Significance

This research addresses critical gaps in embodied AI by providing LLM agents with human-like spatial memory capabilities. Success in this endeavor will enable more robust autonomous navigation for delivery robots, emergency response systems, and urban assistance applications. Furthermore, the interpretable nature of hierarchical memory structures will facilitate trust and collaboration between humans and AI agents in safety-critical urban scenarios.

## 2. Methodology

### 2.1 Overall Architecture

The Hierarchical Spatial Memory Network (HSMN) consists of three primary components: (1) a three-layer spatial memory structure, (2) a Graph Neural Network (GNN) for dynamic memory construction and update, and (3) a memory-augmented LLM interface for task-driven query and reasoning. Figure 1 (conceptual) illustrates the overall architecture.

### 2.2 Three-Layer Spatial Memory Structure

#### Landmark Layer ($\mathcal{L}$)

The landmark layer stores salient visual-semantic features of key locations encountered during navigation. Each landmark node $l_i \in \mathcal{L}$ is represented as:

$$l_i = (p_i, v_i, s_i, t_i)$$

where $p_i \in \mathbb{R}^3$ is the GPS coordinate, $v_i \in \mathbb{R}^{d_v}$ is the visual feature vector extracted using a pre-trained vision encoder (CLIP-ViT-L/14), $s_i \in \mathbb{R}^{d_s}$ is the semantic embedding derived from detected objects and scene descriptions, and $t_i$ is the timestamp of last observation.

Landmark saliency is computed using an attention-based mechanism:

$$\text{saliency}(l_i) = \sigma(W_s \cdot [v_i; s_i; f_{\text{freq}}(l_i)])$$

where $f_{\text{freq}}(l_i)$ encodes visitation frequency and $\sigma$ is the sigmoid function. Only locations exceeding a saliency threshold $\tau_l$ are retained as landmarks.

#### Route Layer ($\mathcal{R}$)

The route layer encodes traversable paths connecting landmarks. Each route edge $r_{ij} \in \mathcal{R}$ connecting landmarks $l_i$ and $l_j$ is represented as:

$$r_{ij} = (d_{ij}, a_{ij}, \Delta s_{ij}, c_{ij})$$

where $d_{ij}$ is the estimated travel distance, $a_{ij} \in [0,1]$ is the accessibility score (accounting for obstacles, terrain), $\Delta s_{ij}$ is a scene transition descriptor capturing environmental changes along the route, and $c_{ij}$ is a confidence score based on traversal count.

Route attributes are updated incrementally:

$$d_{ij}^{(t+1)} = \alpha \cdot d_{ij}^{(t)} + (1-\alpha) \cdot d_{ij}^{\text{obs}}$$

where $\alpha$ is a smoothing parameter and $d_{ij}^{\text{obs}}$ is the newly observed distance.

#### Region Layer ($\mathcal{G}$)

The region layer captures abstract neighborhood-level representations. Regions are formed by clustering landmarks based on spatial proximity and semantic similarity:

$$g_k = \text{Cluster}(\{l_i : l_i \in \mathcal{N}_k\})$$

Each region node $g_k \in \mathcal{G}$ is represented as:

$$g_k = (\bar{p}_k, e_k, \mathcal{L}_k, A_k)$$

where $\bar{p}_k$ is the centroid coordinate, $e_k \in \mathbb{R}^{d_g}$ is an aggregated embedding computed via attention-weighted pooling over constituent landmarks, $\mathcal{L}_k$ is the set of landmarks within the region, and $A_k$ is the adjacency information to neighboring regions.

### 2.3 Graph Neural Network for Dynamic Memory Update

We employ a heterogeneous graph neural network (HGNN) to maintain and update the hierarchical memory structure during exploration. The HGNN operates on the combined graph $\mathcal{H} = (\mathcal{L} \cup \mathcal{R} \cup \mathcal{G}, \mathcal{E})$ where $\mathcal{E}$ includes intra-layer and inter-layer edges.

**Message Passing Update:**

For each layer, node embeddings are updated through message passing:

$$h_i^{(k+1)} = \text{UPDATE}\left(h_i^{(k)}, \text{AGG}\left(\{m_{ji}^{(k)} : j \in \mathcal{N}(i)\}\right)\right)$$

where the message from node $j$ to node $i$ is:

$$m_{ji}^{(k)} = \text{MSG}(h_j^{(k)}, h_i^{(k)}, e_{ji})$$

We use relation-specific transformations for different edge types (landmark-landmark, landmark-region, region-region):

$$m_{ji}^{(k)} = W_r^{(k)} h_j^{(k)} + b_r^{(k)}$$

where $r$ denotes the relation type.

**Hierarchical Attention Mechanism:**

To enable selective information flow between layers, we introduce a hierarchical attention mechanism:

$$\alpha_{ij}^{\text{cross}} = \frac{\exp(\text{LeakyReLU}(a^T[W_q h_i \| W_k h_j]))}{\sum_{j' \in \mathcal{N}^{\text{cross}}(i)} \exp(\text{LeakyReLU}(a^T[W_q h_i \| W_k h_{j'}]))}$$

This allows landmarks to attend to relevant regions and vice versa, enabling bidirectional information propagation.

### 2.4 Memory-Augmented LLM Interface

The LLM agent interacts with HSMN through a structured query interface. Given a navigation task $T$, the agent generates queries at appropriate abstraction levels:

**Task Decomposition:** The LLM first decomposes the task into sub-goals:
$$T \rightarrow \{g_1^{\text{target}}, g_2^{\text{target}}, ..., g_n^{\text{target}}\}$$

**Hierarchical Query:** For each sub-goal, the agent queries:
1. Region layer for high-level path planning: "Which regions connect current location to target?"
2. Route layer for path selection: "What are the routes between relevant landmarks?"
3. Landmark layer for local navigation: "What visual features indicate the next waypoint?"

**Memory Retrieval:** We implement a relevance-based retrieval mechanism:

$$\text{Retrieve}(q, \mathcal{M}, k) = \text{TopK}_{m \in \mathcal{M}}\left(\cos(f_q(q), f_m(m))\right)$$

where $f_q$ and $f_m$ are learned projection functions and $k$ is the number of retrieved memory items.

### 2.5 Training Procedure

**Stage 1: Memory Construction Pre-training**

We pre-train the GNN on synthetic navigation trajectories generated from OpenStreetMap data. The objective combines reconstruction and contrastive losses:

$$\mathcal{L}_{\text{pre}} = \mathcal{L}_{\text{recon}} + \lambda_1 \mathcal{L}_{\text{contrastive}} + \lambda_2 \mathcal{L}_{\text{hierarchy}}$$

where $\mathcal{L}_{\text{hierarchy}}$ enforces consistency between hierarchical levels.

**Stage 2: Navigation Fine-tuning**

We fine-tune the complete system on navigation tasks using reinforcement learning with shaped rewards:

$$R = R_{\text{success}} + \gamma_1 R_{\text{progress}} + \gamma_2 R_{\text{efficiency}} + \gamma_3 R_{\text{memory}}$$

where $R_{\text{memory}}$ rewards appropriate memory utilization.

### 2.6 Experimental Design

**Datasets and Benchmarks:**
- **Touchdown** (street-level navigation in New York City)
- **AVDN** (aerial view drone navigation dataset)
- **UrbanNav** (proposed new benchmark covering 5 cities with varying complexity)

**Baselines:**
- Mem4Nav (He et al., 2025)
- CityNavAgent (Zhang et al., 2025)
- Vanilla LLM agent with flat memory
- LLM agent with episodic memory only

**Evaluation Metrics:**
1. **Success Rate (SR):** Percentage of successfully completed navigation tasks
2. **Success weighted by Path Length (SPL):** $\text{SPL} = \frac{1}{N}\sum_{i=1}^{N} S_i \frac{l_i^*}{\max(l_i, l_i^*)}$
3. **Navigation Error (NE):** Average distance to goal at termination
4. **Generalization Gap (GG):** Performance difference between seen and unseen areas
5. **Memory Efficiency (ME):** Task performance relative to memory size

**Ablation Studies:**
- Impact of each memory layer
- Effect of hierarchical attention mechanism
- Comparison of GNN architectures
- Analysis of memory retrieval strategies

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Performance Improvements:** We anticipate HSMN will achieve 15-25% improvement in success rate and 20-30% improvement in SPL compared to existing methods on long-horizon navigation tasks (>1km trajectories).

2. **Generalization Capability:** The hierarchical structure should enable better zero-shot transfer to unseen urban areas, reducing the generalization gap by approximately 40% compared to flat memory approaches.

3. **Interpretable Memory Representations:** The three-layer structure will produce human-interpretable spatial representations, with landmark and region layers directly corresponding to concepts humans use in spatial communication.

4. **Computational Efficiency:** The hierarchical organization will reduce memory retrieval complexity from $O(n)$ to $O(\log n)$ for typical navigation queries.

### Broader Impact

This research will contribute to multiple domains of embodied AI in urban environments:

**Practical Applications:** Improved navigation capabilities will benefit autonomous delivery systems, emergency response robots, and assistive technologies for visually impaired individuals in urban settings.

**Human-Agent Collaboration:** The interpretable memory structures will facilitate natural communication between humans and AI agents about spatial information, enabling more effective collaboration in urban applications.

**Scientific Contribution:** HSMN provides a computational model of human-like spatial cognition, contributing to both AI research and cognitive science understanding of navigation.

**Benchmark Development:** The proposed UrbanNav benchmark and evaluation protocols will provide standardized resources for the research community to advance embodied AI in city environments.

### Limitations and Future Work

We acknowledge potential limitations including computational overhead during memory construction and challenges in highly dynamic environments. Future work will explore temporal dynamics in memory structures and multi-agent memory sharing for collaborative urban navigation.