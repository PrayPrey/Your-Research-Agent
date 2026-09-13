# Causal Temporal Graph Neural Networks with Counterfactual Reasoning for Robust Event Forecasting

## 1. Introduction

### Background

Temporal graphs have emerged as a powerful paradigm for modeling dynamic systems across diverse domains, including social networks, financial markets, recommendation systems, and fraud detection. Unlike static graphs, temporal graphs capture the evolution of entities and their relationships over time, enabling more nuanced analysis of complex phenomena. Recent advances in graph neural networks (GNNs) have demonstrated remarkable success in learning representations from such data. However, a critical limitation persists: most existing methods excel at identifying correlations but fail to distinguish genuine causal relationships from spurious associations.

This distinction becomes paramount in high-stakes applications. For instance, in fraud detection, understanding whether a suspicious transaction pattern *causes* fraudulent behavior versus merely *correlating* with it is essential for effective intervention. Similarly, in financial forecasting, distinguishing causal market drivers from coincidental trends can mean the difference between profitable investment decisions and catastrophic losses. Moreover, temporal graphs are inherently susceptible to distribution shifts—when the statistical properties of data change over time—and adversarial perturbations, rendering correlation-based models unreliable in dynamic real-world environments.

Recent work has begun exploring the intersection of causal inference and graph learning. Event-CausNet (2025) demonstrated the value of extracting causal knowledge from text for spatio-temporal forecasting, while CTGCN (2023) showed that integrating causal discovery into temporal GNNs can improve prediction performance by up to 40%. However, these approaches lack comprehensive frameworks for counterfactual reasoning—the ability to answer "what-if" questions about alternative scenarios—which is crucial for both interpretability and actionable decision-making.

### Research Objectives

This research proposes a novel framework that integrates causal inference principles with temporal graph neural networks through counterfactual reasoning mechanisms. Our specific objectives are:

1. **Develop a causal structure learning module** that automatically discovers time-varying causal relationships from temporal interaction data, distinguishing genuine causality from spurious correlations
2. **Design a counterfactual graph generator** capable of synthesizing alternative temporal scenarios by intervening on learned causal structures
3. **Create causally-informed message passing mechanisms** that prioritize causal neighbors during temporal aggregation, enhancing robustness to distribution shifts
4. **Validate the framework** on event forecasting tasks across multiple domains, demonstrating improved accuracy, robustness, and interpretability

### Significance

This research addresses fundamental challenges at the intersection of causal inference, temporal graph learning, and robust machine learning. The expected contributions include:

- **Theoretical advances**: A principled framework bridging structural causal models with temporal graph neural networks, advancing our understanding of causality in dynamic networks
- **Methodological innovations**: Novel algorithms for causal discovery, counterfactual generation, and causally-aware message passing in temporal graphs
- **Practical impact**: Enhanced performance in critical applications such as fraud detection, financial forecasting, and anomaly detection, with demonstrated robustness to distribution shifts and improved interpretability for decision-makers
- **Benchmark contributions**: Comprehensive evaluation protocols and potentially new datasets for assessing causal temporal graph learning methods

## 2. Methodology

### 2.1 Problem Formulation

We formulate a temporal graph as $\mathcal{G} = \{G_1, G_2, ..., G_T\}$, where $G_t = (V_t, E_t, X_t)$ represents the graph at timestamp $t$, with node set $V_t$, edge set $E_t$, and node features $X_t \in \mathbb{R}^{|V_t| \times d}$. Each edge $e_{ij}^t \in E_t$ may have associated features $a_{ij}^t$ and timestamp information.

Our objective is to learn a function $f: \mathcal{G}_{\leq t} \rightarrow Y_{t+\tau}$ that predicts future events or states at time $t+\tau$ based on historical observations up to time $t$, while explicitly modeling causal relationships and enabling counterfactual reasoning.

### 2.2 Causal Structure Learning Module

#### 2.2.1 Temporal Structural Causal Model

We adopt a time-varying structural causal model (SCM) framework where the causal graph evolves over time. For each time window $[t-w, t]$, we define:

$$X_t^i = f_i(\text{PA}(X_t^i), U_t^i, \theta_t)$$

where $X_t^i$ represents features of node $i$ at time $t$, $\text{PA}(X_t^i)$ denotes the causal parents (both spatial neighbors and temporal predecessors), $U_t^i$ captures unobserved confounders, and $\theta_t$ are time-specific parameters.

#### 2.2.2 Causal Discovery Algorithm

We employ a hybrid approach combining constraint-based and score-based methods:

**Step 1: Temporal Granger Causality Testing**

For each pair of nodes $(i, j)$ over time window $[t-w, t]$, we test whether past values of $X^j$ provide statistically significant information about $X^i$ beyond what is already contained in past values of $X^i$:

$$X_t^i = \sum_{k=1}^{p} \alpha_k X_{t-k}^i + \sum_{k=1}^{p} \beta_k X_{t-k}^j + \epsilon_t$$

We perform an F-test with null hypothesis $H_0: \beta_1 = \beta_2 = ... = \beta_p = 0$. Rejection indicates potential Granger causality from $j$ to $i$.

**Step 2: Structure Learning via Continuous Optimization**

To learn the adjacency matrix $A_t$ representing causal relationships at time $t$, we adapt the NOTEARS framework for temporal graphs:

$$\min_{A_t, \Theta_t} \mathcal{L}(A_t, \Theta_t; \mathcal{G}_t) + \lambda_1 ||A_t||_1 + \lambda_2 h(A_t)$$

where $\mathcal{L}$ is the negative log-likelihood, $||A_t||_1$ promotes sparsity, and $h(A_t) = \text{tr}(e^{A_t \odot A_t}) - d$ enforces acyclicity in the learned structure.

**Step 3: Temporal Smoothness Regularization**

To ensure temporal consistency in the learned causal structures:

$$\mathcal{L}_{\text{temporal}} = \sum_{t=2}^{T} ||A_t - A_{t-1}||_F^2$$

The final optimization combines spatial structure learning with temporal smoothness:

$$\min_{A_1, ..., A_T, \Theta} \sum_{t=1}^{T} \left[\mathcal{L}(A_t, \Theta_t; \mathcal{G}_t) + \lambda_1 ||A_t||_1 + \lambda_2 h(A_t)\right] + \lambda_3 \mathcal{L}_{\text{temporal}}$$

### 2.3 Counterfactual Graph Generator

#### 2.3.1 Intervention Mechanism

Given the learned causal graph $A_t$, we define interventions using Pearl's do-calculus. For an intervention $do(X_k^j = x')$ on node $j$'s feature $k$ at time $t$:

$$X_t^{i,CF} = \begin{cases} 
x' & \text{if } i = j, k \\
f_i(\text{PA}(X_t^i)^{CF}, U_t^i, \theta_t) & \text{otherwise}
\end{cases}$$

where superscript $CF$ denotes counterfactual values.

#### 2.3.2 Counterfactual Graph Construction

The counterfactual temporal graph generation proceeds as follows:

**Algorithm 1: Counterfactual Graph Generation**

```
Input: Original temporal graph G_t, causal graph A_t, intervention targets I
Output: Counterfactual graph G_t^CF

1. Initialize G_t^CF ← G_t
2. For each intervention (node i, feature k, value x') in I:
   a. Set X_t^{i,k,CF} ← x'
   b. Identify descendants D(i) from A_t
   c. For each descendant j ∈ D(i) in topological order:
      - Compute X_t^{j,CF} using learned causal mechanisms
      - Update edge features if j's state change affects relationships
3. Return G_t^CF
```

#### 2.3.3 Counterfactual Propagation Through Time

To generate multi-step counterfactual trajectories:

$$G_{t+1}^{CF} = \Phi(G_t^{CF}, A_t, \Theta_t)$$

where $\Phi$ represents the learned temporal evolution dynamics under the counterfactual intervention.

### 2.4 Causally-Informed Message Passing

#### 2.4.1 Causal Attention Mechanism

We design an attention mechanism that weights messages based on causal strength rather than mere correlation:

$$\alpha_{ij}^t = \frac{\exp(\phi(A_t[i,j], h_i^t, h_j^t))}{\sum_{k \in \mathcal{N}(i)} \exp(\phi(A_t[i,k], h_i^t, h_k^t))}$$

where $\phi$ is a learnable function combining causal adjacency $A_t[i,j]$ with node representations $h_i^t, h_j^t$:

$$\phi(a, h_i, h_j) = \text{LeakyReLU}(w_1^T[a \cdot h_i || h_j] + b_1)$$

Here, $a$ represents the causal edge weight, and $||$ denotes concatenation.

#### 2.4.2 Temporal Aggregation with Causal Masking

For temporal aggregation, we incorporate causal constraints:

$$h_i^{t+1} = \sigma\left(\sum_{j \in \mathcal{N}(i)} \alpha_{ij}^t W_c h_j^t + \sum_{\tau=1}^{K} \beta_\tau W_t h_i^{t-\tau}\right)$$

where $\beta_\tau$ are learned temporal attention weights subject to:

$$\beta_\tau = \frac{\exp(\gamma_\tau)}{\sum_{k=1}^{K} \exp(\gamma_k)}, \quad \gamma_\tau = g(h_i^t, h_i^{t-\tau}, \Delta_\tau)$$

with $\Delta_\tau$ encoding the time lag.

#### 2.4.3 Invariant Causal Representation Learning

To enhance robustness to distribution shifts, we learn invariant causal representations:

$$\mathcal{L}_{\text{invariance}} = \sum_{e \in \mathcal{E}} ||\mathbb{E}_{(i,j,t) \in e}[\nabla_{h_i} \ell(y_{ij}^t, \hat{y}_{ij}^t)]||^2$$

where $\mathcal{E}$ represents different environments or time periods, encouraging gradient alignment across domains for causally-determined features.

### 2.5 Overall Architecture

The complete framework integrates the three modules:

$$\hat{Y}_{t+\tau} = \text{Decoder}(\text{CausalTGNN}(\mathcal{G}_{\leq t}, A_{\leq t}))$$

The total loss function combines multiple objectives:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{pred}} + \alpha \mathcal{L}_{\text{causal}} + \beta \mathcal{L}_{\text{invariance}} + \gamma \mathcal{L}_{\text{CF}}$$

where:
- $\mathcal{L}_{\text{pred}}$ is the primary prediction loss (e.g., cross-entropy for event classification)
- $\mathcal{L}_{\text{causal}}$ ensures consistency with learned causal structures
- $\mathcal{L}_{\text{invariance}}$ promotes domain-invariant representations
- $\mathcal{L}_{\text{CF}}$ is the counterfactual consistency loss ensuring predictions align with interventional distributions

### 2.6 Data Collection and Experimental Design

#### 2.6.1 Datasets

We will evaluate on diverse benchmark datasets:

1. **Financial Networks**: Bitcoin transaction graphs for fraud detection (Bitcoin-OTC, Bitcoin-Alpha)
2. **Social Networks**: Reddit hyperlink networks and Twitter interaction graphs for community evolution prediction
3. **E-commerce**: Taobao user-item interaction graphs for recommendation
4. **Traffic Networks**: METR-LA and PeMS-BAY for traffic forecasting
5. **Knowledge Graphs**: ICEWS and GDELT for event forecasting

#### 2.6.2 Baseline Methods

- **Temporal GNN baselines**: TGAT, TGN, DyRep, JODIE
- **Causal baselines**: CTGCN, Event-CausNet
- **Counterfactual baselines**: Graph counterfactual fairness methods adapted for temporal settings
- **Classical methods**: Temporal random walks, recurrent GCNs

#### 2.6.3 Evaluation Metrics

**Prediction Performance:**
- Accuracy, F1-score, AUC-ROC for classification tasks
- Mean Absolute Error (MAE), Root Mean Squared Error (RMSE) for regression
- Mean Reciprocal Rank (MRR), Hits@K for link prediction

**Robustness Evaluation:**
- Performance degradation under temporal distribution shifts
- Robustness to adversarial edge/node perturbations
- Out-of-distribution (OOD) generalization metrics

**Causal Quality Metrics:**
- Structural Hamming Distance (SHD) between learned and ground-truth causal graphs (on synthetic data)
- Intervention accuracy: correctness of predictions under known interventions
- Counterfactual fidelity: consistency between counterfactual predictions and actual outcomes in held-out interventional data

**Interpretability:**
- Human evaluation of causal explanations
- Attention weight alignment with domain knowledge
- Case studies on critical prediction scenarios

#### 2.6.4 Experimental Protocols

**Training Strategy:**
1. Split temporal data chronologically (70% train, 15% validation, 15% test)
2. Use early stopping based on validation performance
3. Hyperparameter tuning via Bayesian optimization

**Robustness Testing:**
1. Create temporal distribution shifts by training on early periods and testing on later periods with different statistics
2. Generate adversarial perturbations using gradient-based attacks
3. Introduce synthetic confounders to test causal discovery robustness

**Ablation Studies:**
1. Remove each component (causal learning, counterfactual generation, causal attention) to assess contribution
2. Vary time window sizes and causal discovery hyperparameters
3. Test different intervention strategies for counterfactual generation

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Improved Prediction Accuracy:** We anticipate 15-25% improvement in prediction accuracy on event forecasting tasks compared to correlation-based temporal GNNs, particularly in scenarios with distribution shifts. Based on CTGCN's reported 40% improvement with basic causal integration, our comprehensive framework should achieve substantial gains.

**Enhanced Robustness:** The framework should demonstrate superior robustness to:
- Temporal distribution shifts (maintaining >80% of original performance when tested on data from different time periods)
- Adversarial perturbations (>30% improvement in robustness metrics)
- Missing data and incomplete observations

**Interpretable Causal Explanations:** The system will provide human-interpretable causal explanations for predictions, including:
- Identification of top-k causal factors influencing each prediction
- Counterfactual explanations ("this event occurred because X; if X hadn't happened, Y would have been the outcome")
- Visualization of time-varying causal structures

**Effective Counterfactual Reasoning:** Demonstrated capability to:
- Generate realistic counterfactual scenarios with >85% fidelity to actual interventional data
- Support decision-making through "what-if" analysis
- Enable data augmentation for rare events, improving performance on long-tail predictions by 20-30%

### 3.2 Theoretical Impact

This research will advance the theoretical understanding of:

1. **Causality in Temporal Graphs:** Formalize the integration of structural causal models with temporal graph neural networks, providing theoretical guarantees on identifiability and consistency of causal discovery in dynamic settings

2. **Counterfactual Graph Generation:** Establish theoretical foundations for valid counterfactual inference in temporal graphs, including conditions under which counterfactual predictions are reliable

3. **Robustness through Causality:** Provide theoretical analysis of how causal invariance principles enhance robustness to distribution shifts, potentially deriving generalization bounds for causal temporal GNNs

### 3.3 Practical Impact

**High-Stakes Applications:**

1. **Fraud Detection:** Enable financial institutions to understand not just correlations between suspicious activities but causal patterns, allowing preemptive intervention and more accurate risk assessment

2. **Financial Forecasting:** Support investors and analysts with causal explanations of market movements and counterfactual scenario analysis for risk management

3. **Recommendation Systems:** Provide causally-grounded recommendations that account for why users might prefer items, reducing biases and improving user satisfaction

4. **Disease Outbreak Prediction:** Help public health officials understand causal transmission patterns and evaluate counterfactual intervention strategies

**Industry Adoption:** The framework's emphasis on interpretability and robustness addresses key barriers to deploying graph learning systems in regulated industries (finance, healthcare), potentially accelerating adoption of AI technologies in these domains.

### 3.4 Broader Scientific Impact

**Cross-Disciplinary Contributions:** This work bridges machine learning, causal inference, network science, and domain applications, fostering collaboration across fields and potentially inspiring new research directions.

**Benchmark and Evaluation Standards:** We will release:
- Open-source implementation of the framework
- Comprehensive benchmark suite for causal temporal graph learning
- Evaluation protocols for assessing causal quality and counterfactual fidelity
- Potentially new datasets with ground-truth causal annotations (using controlled simulations)

**Educational Impact:** The research will contribute to curriculum development at the intersection of causality and graph learning, with tutorial materials and workshops to disseminate knowledge to the broader community.

### 3.5 Long-term Vision

This research represents a step toward *causally-aware AI systems* that not only predict but also explain and reason about interventions in complex dynamic networks. Long-term, such systems could:

- Enable automated causal discovery at scale, reducing reliance on manual domain expertise
- Support adaptive systems that detect when causal structures change and update accordingly
- Facilitate human-AI collaboration by providing interpretable, actionable insights
- Contribute to the development of safe and reliable AI systems through enhanced robustness and transparency

By addressing the fundamental limitation of correlation-based learning in temporal graphs and providing principled mechanisms for causal and counterfactual reasoning, this research has the potential to transform how we analyze, predict, and intervene in dynamic networked systems across science, industry, and society.