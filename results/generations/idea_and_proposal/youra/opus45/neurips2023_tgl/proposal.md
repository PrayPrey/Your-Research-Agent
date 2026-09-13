# Research Proposal: HITM: Curvature-Guided Hebbian Memory for Efficient Long-Range Temporal Graph Learning

## 1. Introduction

### 1.1 Background

Temporal graphs have emerged as a fundamental data structure for modeling complex systems that evolve over time, including social networks, transportation systems, financial markets, and biological processes. Unlike static graphs, temporal graphs capture the dynamic nature of real-world relationships, where nodes and edges appear, disappear, or change their attributes across time. This temporal dimension introduces both opportunities and challenges for machine learning: while temporal information can significantly enhance predictive power, effectively modeling long-range temporal dependencies remains computationally prohibitive.

Current state-of-the-art spatial-temporal graph neural networks (STGNNs) such as STGCN, Graph WaveNet, and DCRNN have achieved remarkable success in short-term forecasting tasks. However, these methods typically rely on attention mechanisms or recurrent architectures that scale quadratically with sequence length, i.e., $O(T^2)$, where $T$ represents the temporal horizon. This quadratic complexity severely limits their applicability to long-range forecasting scenarios—such as week-scale traffic prediction or seasonal pattern recognition—where capturing dependencies across hundreds or thousands of timesteps is essential.

Recent approaches have attempted to address this scalability challenge through different strategies. BigST employs pre-computation of long-range features to enable scaling to graphs with over 100,000 nodes, while STEP leverages pre-training paradigms to capture extended temporal patterns. However, these methods sacrifice dynamic adaptability: pre-computed features cannot respond to real-time structural changes, and pre-trained models may fail to generalize to distribution shifts. This creates a fundamental trade-off between computational efficiency and adaptive responsiveness that current methods have not resolved.

### 1.2 Research Motivation

Our research is motivated by a key observation from network science: not all temporal events carry equal predictive importance. Specifically, we hypothesize that structurally significant events—those that fundamentally alter the graph's topological properties—carry disproportionate predictive information compared to routine fluctuations. This insight suggests that selective attention to important events, rather than uniform processing of all timesteps, could dramatically reduce computational requirements while preserving or even enhancing predictive accuracy.

Graph curvature, particularly Ollivier-Ricci curvature (ORC), provides a principled mathematical framework for quantifying structural importance. ORC measures the local geometry of a graph by comparing geodesic distances to optimal transport distances, effectively capturing bottlenecks, community boundaries, and information flow constraints. Recent work (ORC-STGNN, PIORF) has demonstrated that incorporating curvature information improves spatial reasoning in traffic forecasting by approximately 10% RMSE. We extend this insight to the temporal domain: changes in curvature over time signal structurally important events that warrant selective memory consolidation.

Furthermore, biological memory systems offer inspiration for efficient long-range information processing. The hippocampal memory system achieves remarkable efficiency through selective consolidation—strengthening memories of important events while allowing routine information to decay. Hebbian learning, summarized as "neurons that fire together wire together," provides a computational principle for this selective consolidation. By combining curvature-guided importance detection with Hebbian memory mechanisms, we propose a biologically-inspired approach to temporal graph learning that achieves linear complexity while maintaining dynamic adaptability.

### 1.3 Research Objectives

This research aims to develop and validate HITM (Hebbian-Inspired Temporal Memory), a novel module that augments existing STGNNs to enable efficient long-range temporal graph learning. Our specific objectives are:

1. **Develop a curvature-guided event detection mechanism** that identifies structurally important temporal events through Ollivier-Ricci curvature changes, providing a principled criterion for selective attention.

2. **Design a Hebbian memory consolidation system** that efficiently stores important events in a compact memory bank, enabling $O(n)$ complexity scaling with sequence length.

3. **Implement sparse associative retrieval** that integrates historical context with current predictions through top-k attention over the memory bank.

4. **Validate the approach** on standard traffic forecasting benchmarks, demonstrating ≥10% MAE improvement over STGCN baselines while achieving linear time complexity.

### 1.4 Significance

This research addresses a critical gap in temporal graph learning by providing a scalable, adaptive solution for long-range dependency modeling. Success would establish graph curvature as a principled criterion for temporal importance—a novel theoretical contribution bridging network science and deep learning. Practically, HITM would enable week-scale forecasting in applications such as traffic management, energy grid optimization, and epidemic modeling, where current methods are limited to short-term predictions. The biologically-inspired design also contributes to the broader goal of developing more efficient and interpretable neural architectures.

## 2. Methodology

### 2.1 Problem Formulation

We consider a discrete-time temporal graph $\mathcal{G} = \{G_1, G_2, \ldots, G_T\}$, where each snapshot $G_t = (V, E_t, X_t)$ consists of a fixed node set $V$ with $|V| = N$ nodes, time-varying edges $E_t$, and node features $X_t \in \mathbb{R}^{N \times F}$. The forecasting task is to predict future node features $\hat{X}_{t+1:t+H}$ given historical observations $X_{t-W+1:t}$, where $W$ is the lookback window and $H$ is the forecast horizon.

Our goal is to extend $W$ to week-scale (e.g., $W > 1000$ timesteps for 5-minute intervals) while maintaining $O(N \cdot W)$ complexity, compared to the $O(N \cdot W^2)$ complexity of standard attention mechanisms.

### 2.2 HITM Architecture Overview

HITM operates as a plug-in module that augments any base STGNN through four sequential steps:

$$\text{HITM}: (X_t, G_t, \mathcal{M}_{t-1}) \rightarrow (h_t^{\text{enhanced}}, \mathcal{M}_t)$$

where $\mathcal{M}_t$ represents the memory bank at time $t$, and $h_t^{\text{enhanced}}$ is the enhanced representation for prediction.

### 2.3 Step 1: Curvature-Based Event Detection

**Ollivier-Ricci Curvature Computation.** For each edge $(u, v) \in E_t$, we compute the Ollivier-Ricci curvature as:

$$\kappa_t(u, v) = 1 - \frac{W_1(\mu_u, \mu_v)}{d(u, v)}$$

where $W_1(\mu_u, \mu_v)$ is the Wasserstein-1 distance between probability measures $\mu_u$ and $\mu_v$ defined on the neighborhoods of nodes $u$ and $v$, and $d(u, v)$ is the graph distance. We use the lazy random walk measure:

$$\mu_u(w) = \begin{cases} \alpha & \text{if } w = u \\ \frac{1-\alpha}{\deg(u)} & \text{if } w \in \mathcal{N}(u) \\ 0 & \text{otherwise} \end{cases}$$

with $\alpha = 0.5$ as the laziness parameter.

**Curvature Change Detection.** We aggregate edge curvatures to node-level importance scores:

$$\text{OR}_t(v) = \frac{1}{|\mathcal{N}(v)|} \sum_{u \in \mathcal{N}(v)} \kappa_t(u, v)$$

The curvature change is computed as:

$$\Delta\text{OR}_t(v) = |\text{OR}_t(v) - \text{OR}_{t-1}(v)|$$

**Adaptive Thresholding.** Events are flagged as important when curvature change exceeds an adaptive threshold:

$$\mathcal{I}_t = \{v \in V : \Delta\text{OR}_t(v) > \tau_t\}$$

where $\tau_t = \mu(\Delta\text{OR}_t) + \sigma(\Delta\text{OR}_t)$ is computed from the current timestep's statistics, ensuring automatic adaptation to different graph dynamics.

### 2.4 Step 2: Hebbian Memory Consolidation

**Memory Bank Structure.** The memory bank $\mathcal{M} = \{(m_i, s_i, t_i)\}_{i=1}^{k}$ stores $k$ memory slots, each containing a memory vector $m_i \in \mathbb{R}^d$, a strength score $s_i \in [0, 1]$, and a timestamp $t_i$.

**Hebbian Write Rule.** For important events at time $t$, we compute a candidate memory vector:

$$c_t = \text{Aggregate}(\{h_t^v : v \in \mathcal{I}_t\})$$

where $h_t^v$ is the hidden representation from the base STGNN and Aggregate is a learnable attention-based pooling. The memory update follows a Hebbian-inspired rule:

$$m_i^{\text{new}} = m_i + \eta \cdot \text{sim}(c_t, m_i) \cdot (c_t - m_i)$$

$$s_i^{\text{new}} = s_i + \eta \cdot \text{sim}(c_t, m_i) - \lambda$$

where $\eta$ is the learning rate, $\text{sim}(\cdot, \cdot)$ is cosine similarity, and $\lambda \in [0.01, 0.5]$ is the decay rate. This rule strengthens memories similar to current important events while gradually forgetting dissimilar ones.

**Memory Replacement.** When all memory slots are occupied and a new important event occurs, we replace the slot with the lowest strength score:

$$i^* = \arg\min_i s_i, \quad m_{i^*} \leftarrow c_t, \quad s_{i^*} \leftarrow 1.0, \quad t_{i^*} \leftarrow t$$

**Adaptive Memory Size.** The memory bank size adapts to graph complexity:

$$k = \min(k_{\max}, \lceil \log_2(|V|) \rceil \times \alpha)$$

where $k_{\max} = 128$ and $\alpha$ is a scaling factor, ensuring larger graphs have proportionally more memory capacity.

### 2.5 Step 3: Sparse Associative Retrieval

**Query Formation.** The current hidden state $h_t$ from the base STGNN serves as the query:

$$q_t = W_q \cdot h_t$$

where $W_q \in \mathbb{R}^{d \times d}$ is a learnable projection matrix.

**Top-k Sparse Attention.** We retrieve the $k'$ most relevant memories through sparse attention:

$$\alpha_i = \frac{\exp(\text{sim}(q_t, m_i) / \sqrt{d})}{\sum_{j \in \text{top-}k'} \exp(\text{sim}(q_t, m_j) / \sqrt{d})}$$

where top-$k'$ selects the $k' \ll k$ memories with highest similarity scores. This ensures $O(k)$ retrieval complexity, which is constant with respect to sequence length $T$.

**Context Aggregation.** The retrieved context is:

$$r_t = \sum_{i \in \text{top-}k'} \alpha_i \cdot m_i$$

### 2.6 Step 4: Enhanced Prediction Integration

**Gated Fusion.** We integrate retrieved context with current representations through a gating mechanism:

$$g_t = \sigma(W_g [h_t; r_t] + b_g)$$

$$h_t^{\text{enhanced}} = g_t \odot h_t + (1 - g_t) \odot r_t$$

where $\sigma$ is the sigmoid function, $[;]$ denotes concatenation, and $\odot$ is element-wise multiplication.

**Final Prediction.** The enhanced representation is passed to the prediction head:

$$\hat{X}_{t+1:t+H} = \text{MLP}(h_t^{\text{enhanced}})$$

### 2.7 Training Procedure

**Loss Function.** We use a composite loss:

$$\mathcal{L} = \mathcal{L}_{\text{pred}} + \beta \mathcal{L}_{\text{mem}}$$

where $\mathcal{L}_{\text{pred}} = \frac{1}{NH} \sum_{v,h} |X_{t+h}^v - \hat{X}_{t+h}^v|$ is the MAE prediction loss, and $\mathcal{L}_{\text{mem}}$ is a memory diversity regularizer:

$$\mathcal{L}_{\text{mem}} = \frac{1}{k^2} \sum_{i \neq j} \max(0, \text{sim}(m_i, m_j) - \gamma)$$

encouraging diverse memory representations with margin $\gamma = 0.5$.

**Warmup Period.** The first $T_0$ timesteps (10-50) are used to initialize the memory bank before prediction training begins.

### 2.8 Experimental Design

**Datasets.** We evaluate on two standard traffic forecasting benchmarks:
- **METR-LA:** 207 sensors, 4 months of data, 5-minute intervals (34,272 timesteps)
- **PEMS-BAY:** 325 sensors, 6 months of data, 5-minute intervals (52,116 timesteps)

**Baselines.** We compare against:
- **STGCN:** Base spatial-temporal graph convolutional network
- **Graph WaveNet:** Adaptive adjacency learning with dilated convolutions
- **STEP:** Pre-training approach for long-range patterns
- **BigST:** Pre-computation approach for scalability

**Evaluation Metrics.**
- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)
- Mean Absolute Percentage Error (MAPE)
- Wall-clock training and inference time

**Experimental Protocol.**
1. **Main Comparison:** Week-scale forecasting (H = 2016 for one week at 5-minute intervals)
2. **Ablation Studies:** Remove each component (curvature detection, Hebbian memory, sparse retrieval) to isolate contributions
3. **Complexity Analysis:** Measure time vs. sequence length $T$ to verify $O(n)$ scaling
4. **Interpretability Analysis:** Visualize high-curvature events and their correspondence to traffic incidents

**Statistical Validation.** All experiments are repeated 25 times with different random seeds. We report mean ± standard deviation, 95% confidence intervals, and Cohen's d effect size. Paired t-tests with $\alpha = 0.05$ determine statistical significance.

**Falsification Criteria.** The hypothesis is rejected if:
1. MAE ≥ 3.17 (worse than STGCN baseline of 2.88)
2. Curvature selection shows no advantage over random selection ($p > 0.10$)
3. Complexity scaling is $O(T^2)$ rather than $O(T)$

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1 - Accuracy):** We expect HITM-augmented STGCN to achieve MAE < 2.60 on week-scale traffic forecasting, representing ≥10% improvement over the STGCN baseline (MAE = 2.88). This would match or exceed STEP's performance (MAE = 2.61) while maintaining dynamic adaptability.

**Secondary Outcome (P2 - Complexity):** We expect computational time to scale linearly with sequence length $T$, with $R^2 > 0.95$ for the linear fit. This would enable processing of week-scale sequences (T > 2000) that are infeasible with quadratic-complexity attention.

**Tertiary Outcome (P3 - Interpretability):** We expect high-curvature events to correspond to interpretable structural changes such as traffic incidents, road closures, or demand surges, providing explainable predictions.

### 3.2 Scientific Impact

**Theoretical Contributions:**
1. **Curvature as Temporal Importance:** Establishing graph curvature changes as a principled criterion for temporal event importance bridges network science theory with deep learning practice.
2. **Biological Memory Principles:** Demonstrating that Hebbian consolidation principles transfer effectively to neural network memory systems contributes to the broader understanding of biologically-inspired AI.

**Methodological Contributions:**
1. **Scalable Long-Range Modeling:** HITM provides a general framework for extending any STGNN to long-range forecasting without architectural redesign.
2. **Adaptive Memory Systems:** The curvature-guided memory consolidation mechanism offers a new paradigm for selective attention that could generalize beyond temporal graphs.

### 3.3 Practical Impact

**Application Domains:**
- **Traffic Management:** Week-scale forecasting enables proactive infrastructure planning and congestion mitigation.
- **Energy Systems:** Long-range demand prediction improves grid stability and renewable integration.
- **Epidemic Modeling:** Extended temporal horizons support public health intervention planning.
- **Financial Networks:** Detecting structurally important market events enables better risk management.

**Deployment Considerations:** HITM's linear complexity and plug-in architecture facilitate integration with existing production systems. The ~5% curvature computation overhead is acceptable for most applications, and the interpretable high-curvature events support human-in-the-loop decision making.

### 3.4 Limitations and Future Work

**Current Limitations:**
1. **Discrete-Time Assumption:** HITM is designed for regular snapshots and may not directly apply to continuous-time event streams.
2. **Warmup Requirement:** The $T_0$ warmup period delays initial predictions.
3. **Domain Specificity:** Curvature thresholds may require tuning for domains with different dynamics.

**Future Directions:**
1. **Continuous-Time Extension:** Adapting HITM for event-driven temporal graphs using temporal point processes.
2. **Multi-Scale Memory:** Hierarchical memory banks capturing patterns at different temporal resolutions.
3. **Cross-Domain Transfer:** Investigating whether curvature-importance relationships transfer across application domains.

### 3.5 Conclusion

This research proposes HITM, a novel approach to long-range temporal graph learning that combines curvature-guided event detection with Hebbian memory consolidation. By selectively attending to structurally important events, HITM achieves linear complexity scaling while preserving dynamic adaptability—resolving a fundamental trade-off in current methods. Successful validation would establish new theoretical foundations for temporal importance in graphs and enable practical applications requiring week-scale forecasting. The biologically-inspired design contributes to the broader goal of developing efficient, interpretable, and scalable neural architectures for dynamic network analysis.