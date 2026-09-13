# Research Proposal: Causal Discovery in Temporal Graphs via Interventional Contrastive Learning

## 1. Introduction

### Background

Temporal graphs have emerged as a fundamental data structure for modeling dynamic systems across diverse domains, including social networks, financial markets, healthcare systems, and transportation networks. Unlike static graphs, temporal graphs capture the evolution of entities and their relationships over time, providing richer representations of real-world phenomena. Recent advances in temporal graph neural networks (TGNNs) have demonstrated remarkable success in tasks such as link prediction, node classification, and event forecasting by learning from the joint dynamics of graph topology and node features.

However, a critical limitation of existing temporal graph learning methods lies in their focus on capturing correlations rather than causal relationships. While correlation-based models can achieve high predictive accuracy, they often learn spurious associations that fail to generalize under distribution shifts and provide limited interpretability for understanding the underlying mechanisms driving observed patterns. This limitation becomes particularly problematic in high-stakes applications such as disease outbreak prediction, financial fraud detection, and policy intervention design, where understanding *why* events occur—not merely predicting *when* they will occur—is essential for effective decision-making.

The challenge of distinguishing causal relationships from spurious correlations in temporal graphs is compounded by several factors unique to dynamic settings. First, confounding variables may themselves evolve over time, creating complex patterns of association that mask true causal effects. Second, causal influences in temporal systems often manifest with delays, requiring methods that can capture lagged dependencies across multiple time scales. Third, the combinatorial nature of temporal graphs—where both node attributes and edge structures change simultaneously—makes it difficult to isolate the effects of specific interventions.

Existing approaches to causal discovery in temporal data have made progress on some of these challenges. Constraint-based methods such as those proposed by Rohekar et al. (2023) address latent confounders by iteratively refining causal structures from long-term to short-term temporal relations. Recent work on interventional causal discovery, including CAnDOIT (Castri et al., 2024) and RealTCD (Li et al., 2024), has demonstrated the value of combining observational and interventional data for more accurate causal structure learning. However, these methods are primarily designed for time-series data rather than graph-structured data and lack mechanisms for learning continuous representations suitable for downstream prediction tasks.

### Research Objectives

This research proposes **Temporal Causal Graph Networks (TCGN)**, a novel framework that integrates interventional reasoning into temporal graph representation learning to enable causal discovery while maintaining strong predictive performance. Our specific objectives are:

1. To develop a temporal intervention module that generates realistic counterfactual graph sequences by simulating soft interventions on node features and edge formations while preserving underlying causal mechanisms.

2. To design a time-aware causal attention mechanism that identifies edges exhibiting consistent causal influence across multiple time windows, distinguishing them from spurious temporal correlations.

3. To introduce a causal consistency regularizer that enforces representation stability under distribution shifts, improving model robustness and interpretability.

4. To validate the proposed framework on both synthetic benchmarks with known causal structures and real-world datasets from healthcare and finance domains.

### Significance

This research addresses a fundamental gap in temporal graph learning by bridging the divide between predictive modeling and causal inference. The proposed framework offers several significant contributions: (1) improved interpretability through explicit identification of causal edges in temporal graphs; (2) enhanced robustness to temporal distribution shifts by learning causally invariant representations; (3) actionable insights for intervention design in domains where understanding causal mechanisms is critical; and (4) a unified framework that combines the strengths of causal discovery and representation learning for temporal graphs.

## 2. Methodology

### 2.1 Problem Formulation

We consider a temporal graph $\mathcal{G} = \{G^{(1)}, G^{(2)}, \ldots, G^{(T)}\}$ consisting of $T$ snapshots, where each snapshot $G^{(t)} = (V, E^{(t)}, X^{(t)})$ contains a set of nodes $V$, time-varying edges $E^{(t)} \subseteq V \times V$, and node feature matrix $X^{(t)} \in \mathbb{R}^{|V| \times d}$. Our goal is to learn node representations $Z^{(t)} \in \mathbb{R}^{|V| \times h}$ that capture causal relationships while enabling accurate predictions for downstream tasks.

We assume the existence of an underlying causal graph $\mathcal{C} = (V, E_c)$ where $E_c$ represents true causal edges, which is a subset of observed correlational edges. Our framework aims to identify $E_c$ from observational data by leveraging interventional contrastive learning.

### 2.2 Temporal Intervention Module

The core innovation of TCGN is a temporal intervention module that generates counterfactual graph sequences to probe causal relationships. For each node $v_i$ at time $t$, we define a soft intervention operation:

$$\tilde{X}_i^{(t)} = (1 - \alpha) \cdot X_i^{(t)} + \alpha \cdot \delta_i^{(t)}$$

where $\alpha \in [0, 1]$ is the intervention strength and $\delta_i^{(t)}$ is a learned perturbation vector. The perturbation is generated by a parameterized intervention network:

$$\delta_i^{(t)} = f_{\text{int}}(X_i^{(t)}, Z_i^{(t-1)}, \mathcal{N}_i^{(t)}; \theta_{\text{int}})$$

where $\mathcal{N}_i^{(t)}$ represents the neighborhood information of node $v_i$ at time $t$, and $\theta_{\text{int}}$ are learnable parameters.

To preserve causal mechanisms during intervention, we impose a structural constraint that interventions should not affect the causal parents of the intervened node. This is implemented through a masking mechanism:

$$\tilde{A}_{ij}^{(t)} = A_{ij}^{(t)} \cdot (1 - M_{ij}^{(t)} \cdot \mathbb{1}[j \in \text{Int}^{(t)}])$$

where $A^{(t)}$ is the adjacency matrix, $M^{(t)}$ is a learned causal mask, and $\text{Int}^{(t)}$ is the set of intervened nodes at time $t$.

### 2.3 Time-Aware Causal Attention Mechanism

We propose a time-aware causal attention mechanism that identifies edges with consistent causal influence across multiple time windows. For each edge $(v_i, v_j)$, we compute a causal attention score:

$$\beta_{ij}^{(t)} = \sigma\left(\frac{(W_Q Z_i^{(t)})^T (W_K Z_j^{(t)})}{\sqrt{h}} + \gamma \cdot C_{ij}^{(t)}\right)$$

where $W_Q, W_K \in \mathbb{R}^{h \times h}$ are query and key projection matrices, $\gamma$ is a hyperparameter, and $C_{ij}^{(t)}$ is a causal consistency score computed as:

$$C_{ij}^{(t)} = \frac{1}{W} \sum_{w=1}^{W} \text{CosSim}\left(\Delta Z_j^{(t-w)} | \text{do}(X_i^{(t-w)}), \Delta Z_j^{(t)} | \text{do}(X_i^{(t)})\right)$$

where $W$ is the number of time windows considered, and $\Delta Z_j | \text{do}(X_i)$ represents the change in node $j$'s representation following an intervention on node $i$.

The node representations are updated using this causal attention:

$$Z_i^{(t)} = \text{GRU}\left(Z_i^{(t-1)}, \sum_{j \in \mathcal{N}_i^{(t)}} \beta_{ij}^{(t)} \cdot W_V Z_j^{(t)}\right)$$

where $W_V \in \mathbb{R}^{h \times h}$ is the value projection matrix and GRU captures temporal dependencies.

### 2.4 Interventional Contrastive Learning Objective

We design a contrastive learning objective that distinguishes causal edges from spurious correlations by comparing representations under different intervention scenarios. For each node pair $(v_i, v_j)$, we construct:

- **Positive pairs**: Representations where the causal influence from $v_i$ to $v_j$ is preserved after intervention on unrelated nodes.
- **Negative pairs**: Representations where the correlation between $v_i$ and $v_j$ breaks after intervention on confounding nodes.

The interventional contrastive loss is defined as:

$$\mathcal{L}_{\text{ICL}} = -\sum_{(i,j) \in E^{(t)}} \log \frac{\exp(\text{sim}(Z_i^{(t)}, Z_j^{(t)}) / \tau)}{\sum_{k \in \mathcal{N}_{\text{neg}}} \exp(\text{sim}(\tilde{Z}_i^{(t)}, \tilde{Z}_k^{(t)}) / \tau)}$$

where $\tau$ is a temperature parameter, $\mathcal{N}_{\text{neg}}$ is the set of negative samples, and $\tilde{Z}$ denotes representations under intervention.

### 2.5 Causal Consistency Regularizer

To enforce robustness to distribution shifts, we introduce a causal consistency regularizer that penalizes representation changes for causally related node pairs under different environmental conditions:

$$\mathcal{L}_{\text{CCR}} = \sum_{(i,j) \in E_c} \sum_{e \in \mathcal{E}} \left\| f(Z_i^{(t)}, Z_j^{(t)}) - f(Z_i^{(t,e)}, Z_j^{(t,e)}) \right\|_2^2$$

where $\mathcal{E}$ represents different environments (simulated through data augmentation or observed distribution shifts), and $f(\cdot)$ is a learned invariance function.

### 2.6 Overall Training Objective

The complete TCGN framework is trained end-to-end with the following objective:

$$\mathcal{L} = \mathcal{L}_{\text{task}} + \lambda_1 \mathcal{L}_{\text{ICL}} + \lambda_2 \mathcal{L}_{\text{CCR}} + \lambda_3 \mathcal{L}_{\text{sparse}}$$

where $\mathcal{L}_{\text{task}}$ is the task-specific loss (e.g., cross-entropy for classification), $\mathcal{L}_{\text{sparse}} = \|M\|_1$ encourages sparse causal masks, and $\lambda_1, \lambda_2, \lambda_3$ are hyperparameters.

### 2.7 Experimental Design

**Datasets**: We will evaluate TCGN on: (1) synthetic temporal graphs with known causal structures generated using structural causal models with time-varying confounders; (2) MIMIC-III healthcare dataset for disease progression modeling; (3) financial transaction networks for fraud detection; and (4) social network datasets for information diffusion prediction.

**Baselines**: We will compare against: (1) temporal GNN methods (TGN, TGAT, DySAT); (2) causal discovery methods (PCMCI, CAnDOIT, RealTCD adapted for graphs); and (3) robust/invariant learning methods (IRM, GroupDRO adapted for temporal graphs).

**Evaluation Metrics**: 
- Causal discovery: Structural Hamming Distance (SHD), F1-score for edge identification, Area Under Precision-Recall Curve (AUPRC)
- Prediction performance: AUC-ROC, Average Precision, accuracy
- Robustness: Performance degradation under distribution shift
- Interpretability: Alignment with domain expert annotations

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Novel Framework**: A principled framework for integrating causal discovery into temporal graph learning that can identify causal edges while learning predictive representations.

2. **Improved Interpretability**: Explicit identification of causal relationships in temporal graphs, providing actionable insights for intervention design in healthcare and finance applications.

3. **Enhanced Robustness**: Demonstrated improvement in model performance under temporal distribution shifts compared to correlation-based baselines, with expected improvements of 10-15% in out-of-distribution scenarios.

4. **Comprehensive Benchmarks**: New evaluation protocols and synthetic datasets for assessing causal discovery capabilities in temporal graph learning methods.

### Broader Impact

This research has significant implications for applications where understanding causal mechanisms is critical. In healthcare, TCGN could identify causal pathways in disease progression networks, enabling more targeted interventions. In financial systems, the framework could distinguish genuine fraud patterns from coincidental correlations, reducing false positives in detection systems. The proposed methods also contribute to the broader goal of developing trustworthy AI systems by improving model interpretability and robustness.

By bridging causal inference and temporal graph learning, this work opens new research directions at the intersection of these fields, potentially inspiring future work on causal representation learning for other dynamic data modalities.