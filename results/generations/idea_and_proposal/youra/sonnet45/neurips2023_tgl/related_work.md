## Related Work

**Related Papers**

1. **Title**: Scalable and Effective Temporal Graph Representation Learning With Hyperbolic Geometry
   - **Authors**: Yuanyuan Xu, Wenjie Zhang, Xiwei Xu, Binghao Li, Ying Zhang
   - **Summary**: Introduced Hyperbolic Temporal GNN (STGN^h) with hyperbolic update gate (HuG) and hyperbolic Transformer (HyT), achieving billion-scale capability for temporal graph learning using hyperbolic geometry for spatial graph hierarchies.
   - **Year**: 2024

2. **Title**: Towards Dynamic Spatial-Temporal Graph Learning: A Decoupled Perspective
   - **Authors**: Binwu Wang, Pengkun Wang, Yudong Zhang, et al.
   - **Summary**: Proposed Decoupled Learning Framework (DLF) and DSTG network that decomposes temporal dependencies into trend and seasonal terms, providing multi-scale temporal decomposition with fixed 2 scales for all nodes.
   - **Year**: 2024

3. **Title**: Scaling Up Dynamic Graph Representation Learning via Spiking Neural Networks
   - **Authors**: Jintang Li, Zhouxin Yu, Zulun Zhu, et al.
   - **Summary**: Developed SpikeNet framework using Spiking Neural Networks for dynamic graphs with event-driven processing, achieving significantly lower computational cost than RNN-based temporal GNNs through sparse spike-based computation.
   - **Year**: 2022

4. **Title**: Localised Adaptive Spatial-Temporal Graph Neural Network
   - **Authors**: Wenying Duan, Xiaoxi He, Zimu Zhou, Lothar Thiele, Hong Rao
   - **Summary**: Introduced Adaptive Graph Sparsification (AGS) demonstrating spatial graphs can be sparsified by >99.5% without accuracy loss, validating adaptive allocation principles for graph neural networks.
   - **Year**: 2023

5. **Title**: Dynamic Graph Representation Learning for Spatio-Temporal Neuroimaging Analysis
   - **Authors**: Rui Liu, Yao Hu, Jibin Wu, et al.
   - **Summary**: Proposed STIGR framework for neuroimaging analysis combining dynamic adaptive-neighbor GCN, Transformer attention, and contrastive learning, validating heterogeneous temporal dynamics exist in brain networks where different regions evolve at different rates.
   - **Year**: 2025

6. **Title**: Provably Expressive Temporal Graph Networks
   - **Authors**: Amauri Souza, Diego Mesquita, Samuel Kaski, Vikas K. Garg
   - **Summary**: Extended Weisfeiler-Leman (WL) test to temporal graphs and characterized expressive power of walk-aggregating versus message-passing temporal GNNs, providing theoretical foundation for temporal GNN expressiveness.
   - **Year**: 2022

7. **Title**: Towards Expressive Spectral-Temporal Graph Neural Networks
   - **Authors**: Ming Jin, Guangsi Shi, Yuan-Fang Li, et al.
   - **Summary**: Proved linear spectral-temporal GNNs are universal under mild assumptions and introduced TGGC model, providing theoretical justification for spectral temporal modeling including wavelet-based approaches.
   - **Year**: 2023

8. **Title**: Wavelet Analysis and Its Applications
   - **Authors**: Stéphane Mallat (1989), Ingrid Daubechies (1992)
   - **Summary**: Foundational works establishing Multiresolution Analysis (MRA), time-frequency localization, and wavelet basis functions in signal processing, providing theoretical basis for multi-scale signal decomposition.
   - **Year**: 1989-1992

9. **Title**: Information Bottleneck Theory
   - **Authors**: Naftali Tishby et al. (1999), Ravid Schwartz-Ziv & Naftali Tishby (2017)
   - **Summary**: Established trade-off between compression and prediction in learned representations, demonstrating neural networks learn to compress input into minimal sufficient representation for tasks while maximizing task-relevant information.
   - **Year**: 1999-2017

10. **Title**: TimeTraveler: Reinforcement Learning for Temporal Knowledge Graph Forecasting (Sun et al., 2021) and Chain-of-History Reasoning (Xia et al., 2024)
    - **Authors**: Sun et al. (2021), Xia et al. (2024)
    - **Summary**: Temporal knowledge graph forecasting methods focusing on discrete relational events, providing alternative approaches to temporal graph learning in knowledge graph domains.
    - **Year**: 2021-2024

11. **Title**: Streaming Graph Neural Networks (Wang et al., 2020; SGNN-GR: Wang et al., 2022)
    - **Authors**: Wang et al.
    - **Summary**: Online learning approaches for streaming graphs addressing catastrophic forgetting through continual learning mechanisms, enabling real-time graph neural network updates.
    - **Year**: 2020-2022

12. **Title**: Spatio-Temporal Graph Neural Networks: A Survey
    - **Authors**: Ming Jin et al.
    - **Summary**: Comprehensive review of 388 STGNN architectures for urban computing, identifying gap where most STGNNs use fixed temporal windows and calling for adaptive temporal modeling approaches.
    - **Year**: 2023

13. **Title**: A Survey of Dynamic Graph Neural Networks
    - **Authors**: Zheng et al.
    - **Summary**: Review categorizing dynamic GNNs and discussing large-scale challenges, identifying lack of diverse temporal dynamics modeling and systematic approaches to heterogeneity in temporal graphs.
    - **Year**: 2024

14. **Title**: Graph Attention Networks (GAT)
    - **Authors**: Petar Veličković et al.
    - **Summary**: Introduced attention mechanisms for graph neural networks enabling nodes to attend to neighbors with learned weights, establishing foundation for adaptive selection in spatial graph domains.
    - **Year**: 2018

15. **Title**: Hyperbolic Graph Neural Networks (Foundational Works)
    - **Authors**: Chami et al. (2019), Liu et al. (2019)
    - **Summary**: Pioneering works establishing hyperbolic geometry for static graph neural networks, demonstrating exponentially increasing capacity of hyperbolic space enables efficient hierarchical representation.
    - **Year**: 2019

**Key Challenges**

1. **Fixed Temporal Resolution Limitation**: Most temporal GNN methods apply uniform temporal granularity across all nodes, leading to wasted computation on slow-changing nodes when high resolution is used for fast-changing nodes, or loss of critical fast dynamics when coarse-graining is applied uniformly.

2. **Lack of Heterogeneous Temporal Dynamics Modeling**: Current temporal graph learning literature lacks formal characterization and systematic approaches to handle heterogeneity where different nodes/edges evolve at vastly different timescales within the same graph.

3. **Scalability Constraints**: Most temporal GNN methods scale to 10⁵-10⁶ nodes, creating a gap between temporal graph research on small benchmarks and industrial applications requiring billion-scale capability for web-scale graphs.

4. **Multi-Scale Temporal Modeling Rigidity**: Existing multi-scale approaches use fixed number of scales (typically 2: trend/seasonal) uniformly across all nodes, without node-specific adaptive selection based on individual temporal characteristics.

5. **Limited Cross-Domain Generalization**: Many temporal GNN methods are specialized for single domains (traffic, knowledge graphs, social networks) requiring domain-specific architecture changes, reducing generalizability and increasing engineering effort for new applications.

6. **Absence of Temporal Scale Hierarchy Theory**: Gap in connecting geometric representations (hyperbolic space) to temporal resolution hierarchies, with prior work focusing on spatial hierarchies rather than temporal scale hierarchies.

7. **Computational Efficiency Trade-offs**: Difficulty achieving both high predictive performance and computational efficiency simultaneously, with most methods sacrificing one for the other rather than achieving Pareto improvements.

8. **Non-Stationary Temporal Dynamics**: Challenge handling temporal dynamics that change characteristics over time (regime shifts, bursty patterns), as most methods assume relatively stationary temporal properties.
