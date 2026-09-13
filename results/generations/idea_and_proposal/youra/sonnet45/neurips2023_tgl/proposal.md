# Research Proposal: HyperWave-TGN: Adaptive Multi-Scale Temporal Graph Learning via Hyperbolic Embeddings and Wavelet Attention

## 1. Title

**HyperWave-TGN: Adaptive Multi-Scale Temporal Graph Learning via Hyperbolic Embeddings and Wavelet Attention for Heterogeneous Temporal Dynamics**

## 2. Introduction

### 2.1 Background

Temporal graphs, where nodes and edges evolve over time, are fundamental representations of real-world dynamic systems ranging from social networks and brain connectivity to molecular interactions and financial transactions. Recent advances in temporal graph neural networks (TGNs) have demonstrated significant improvements in tasks such as link prediction, node classification, and event forecasting. However, a critical limitation persists in current approaches: they apply uniform temporal resolution across all nodes, treating fast-evolving and slow-evolving components identically.

This uniform treatment creates a fundamental mismatch with real-world temporal graphs that exhibit **heterogeneous temporal dynamics**. In brain networks, neurons fire in milliseconds while structural connectivity evolves over months. In social networks, viral content spreads in hours while friendship formation occurs over years. In molecular dynamics, bond vibrations occur at femtosecond scales while conformational changes unfold over microseconds. This heterogeneity, quantifiable through the coefficient of variation (CV) of node update frequencies, characterizes many critical application domains.

Current state-of-the-art methods fall into three categories, each with limitations:

1. **Fixed-resolution methods** (e.g., TGAT, TGN) sample temporal neighborhoods uniformly, wasting computation on slow-changing nodes and under-sampling fast-changing ones.

2. **Event-driven methods** (e.g., SpikeNet) adapt to individual events but lack multi-scale temporal feature extraction and struggle with irregular sampling.

3. **Multi-scale methods** (e.g., Decoupled DSTG) decompose signals into trend and seasonal components but apply the same decomposition uniformly across all nodes, missing node-specific temporal characteristics.

Recent work has shown promise in two relevant directions: hyperbolic graph neural networks effectively capture hierarchical structures in spatial domains, while wavelet-based methods enable multi-resolution signal analysis. However, these approaches have not been integrated to address the fundamental challenge of heterogeneous temporal dynamics in graphs.

### 2.2 Research Objectives

This research proposes **HyperWave-TGN**, a novel framework that learns node-specific temporal resolutions through the synergistic integration of hyperbolic embeddings and wavelet-based multi-scale attention. Our primary objectives are:

**O1. Theoretical Foundation:** Develop a principled framework for representing temporal scale hierarchies in hyperbolic space, establishing the theoretical connection between hyperbolic distance and temporal resolution.

**O2. Methodological Innovation:** Design and implement an adaptive multi-scale temporal graph learning architecture that:
- Embeds nodes in hyperbolic space (Poincaré ball) where distance from origin encodes temporal resolution
- Applies three-scale wavelet decomposition (fine/medium/coarse) to extract multi-resolution temporal features
- Learns node-specific attention over wavelet scales to adaptively allocate computation

**O3. Empirical Validation:** Demonstrate that HyperWave-TGN achieves Pareto improvement over baselines—maintaining ≥95% predictive accuracy while reducing temporal processing costs by 30-50%—across diverse domains with heterogeneous temporal dynamics.

**O4. Scalability:** Enable billion-scale temporal graph learning through adaptive computation allocation, training on graphs with 10⁶ nodes within 24 hours on a single GPU.

### 2.3 Research Significance

This research addresses a critical gap in temporal graph learning with significant theoretical, methodological, and practical contributions:

**Theoretical Significance:**
- First framework connecting hyperbolic geometry to temporal scale hierarchies, extending hyperbolic representation learning from spatial to temporal domains
- Formal characterization of heterogeneous temporal dynamics and their computational implications
- Theoretical analysis of multi-scale temporal attention mechanisms in graph neural networks

**Methodological Significance:**
- Novel integration of hyperbolic embeddings, wavelet transforms, and attention mechanisms for temporal graphs
- Wavelet-based temporal graph signal processing framework applicable beyond this specific architecture
- Synthetic heterogeneous-temporal graph generation protocol for controlled evaluation

**Practical Significance:**
- 30-50% reduction in computational costs enables real-time processing of large-scale temporal graphs
- Cross-domain applicability to brain network analysis (neuroscience), molecular dynamics (chemistry/biology), fraud detection (finance), and recommendation systems (e-commerce)
- Scalability improvements democratize temporal graph learning for resource-constrained researchers

The proposed work directly addresses multiple topics from the Temporal Graph Learning Workshop, including temporal graph representation learning, scalability, multimodal temporal graph learning, brain network modeling, molecular dynamics, and anomaly detection.

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{T})$ denote a temporal graph where $\mathcal{V}$ is the set of $N$ nodes, $\mathcal{E}$ is the set of temporal edges, and $\mathcal{T} = \{t_1, t_2, \ldots, t_T\}$ represents discrete timesteps. Each node $v \in \mathcal{V}$ has a temporal feature sequence $\mathbf{X}_v = \{\mathbf{x}_v^{(t)}\}_{t=1}^T$ where $\mathbf{x}_v^{(t)} \in \mathbb{R}^d$.

We define **temporal heterogeneity** through the coefficient of variation of node update frequencies:
$$CV = \frac{\sigma(f_v)}{\mu(f_v)}, \quad f_v = \frac{|\{t : \mathbf{x}_v^{(t)} \neq \mathbf{x}_v^{(t-1)}\}|}{T}$$

where $f_v$ is the update frequency of node $v$. Graphs with $CV \geq 2.0$ exhibit high heterogeneous temporal dynamics and are the primary focus of this work.

**Task:** Given historical observations up to time $t$, predict node states, edge formations, or graph-level properties at time $t+\Delta t$.

### 3.2 HyperWave-TGN Architecture

The architecture consists of four integrated components:

#### 3.2.1 Hyperbolic Temporal Resolution Embedding

We embed each node $v$ in the Poincaré ball $\mathbb{B}^{d_h} = \{\mathbf{z} \in \mathbb{R}^{d_h} : \|\mathbf{z}\| < 1\}$ with hyperbolic distance:
$$d_{\mathbb{H}}(\mathbf{z}_i, \mathbf{z}_j) = \text{arcosh}\left(1 + 2\frac{\|\mathbf{z}_i - \mathbf{z}_j\|^2}{(1-\|\mathbf{z}_i\|^2)(1-\|\mathbf{z}_j\|^2)}\right)$$

The temporal resolution $r_v$ of node $v$ is encoded as:
$$r_v = \sigma_r(d_{\mathbb{H}}(\mathbf{z}_v, \mathbf{0})) = \sigma_r(\text{arcosh}(1 + 2\frac{\|\mathbf{z}_v\|^2}{1-\|\mathbf{z}_v\|^2}))$$

where $\sigma_r: \mathbb{R}^+ \to [r_{min}, r_{max}]$ maps hyperbolic distance to temporal resolution range. Nodes closer to the origin have finer temporal resolution (high-frequency), while nodes near the boundary have coarser resolution (low-frequency).

**Hyperbolic Update Rule:** Node embeddings are updated using exponential map:
$$\mathbf{z}_v^{(t+1)} = \exp_{\mathbf{z}_v^{(t)}}^{\mathbb{H}}(\mathbf{v}_v^{(t)})$$

where $\mathbf{v}_v^{(t)}$ is the tangent vector computed from temporal features and $\exp^{\mathbb{H}}$ is the exponential map in hyperbolic space.

#### 3.2.2 Wavelet-Based Multi-Scale Temporal Feature Extraction

For each node $v$, we apply continuous wavelet transform (CWT) using Morlet wavelets at three scales:

$$W_v^{(s)}(t) = \int_{-\infty}^{\infty} \mathbf{x}_v^{(\tau)} \psi^*\left(\frac{\tau - t}{s}\right) d\tau$$

where $\psi(t) = \pi^{-1/4} e^{i\omega_0 t} e^{-t^2/2}$ is the Morlet wavelet and $s \in \{s_{fine}, s_{medium}, s_{coarse}\}$ are the three scales.

In discrete implementation:
$$\mathbf{W}_v^{fine} = \text{CWT}(\mathbf{X}_v, s_{fine}), \quad \mathbf{W}_v^{medium} = \text{CWT}(\mathbf{X}_v, s_{medium}), \quad \mathbf{W}_v^{coarse} = \text{CWT}(\mathbf{X}_v, s_{coarse})$$

Each wavelet coefficient sequence is then processed through scale-specific temporal encoders:
$$\mathbf{h}_v^{(s)} = \text{TemporalEncoder}_s(\mathbf{W}_v^{(s)}), \quad s \in \{fine, medium, coarse\}$$

where TemporalEncoder can be implemented as GRU, LSTM, or Transformer layers.

#### 3.2.3 Node-Specific Wavelet Attention

The attention mechanism adaptively weights wavelet scales based on node characteristics:

$$\alpha_v^{(s)} = \frac{\exp(e_v^{(s)})}{\sum_{s' \in \{fine, medium, coarse\}} \exp(e_v^{(s')})}$$

where attention scores are computed using hyperbolic embeddings and temporal features:

$$e_v^{(s)} = \mathbf{w}_s^T \tanh\left(\mathbf{W}_1 \log_{\mathbf{0}}^{\mathbb{H}}(\mathbf{z}_v) + \mathbf{W}_2 \mathbf{h}_v^{(s)} + \mathbf{b}\right)$$

Here $\log_{\mathbf{0}}^{\mathbb{H}}$ is the logarithmic map from hyperbolic to tangent space at origin.

The aggregated temporal representation is:
$$\mathbf{h}_v^{temporal} = \sum_{s \in \{fine, medium, coarse\}} \alpha_v^{(s)} \mathbf{h}_v^{(s)}$$

#### 3.2.4 Hyperbolic Graph Convolution

Spatial message passing is performed in hyperbolic space using hyperbolic graph convolution:

$$\mathbf{m}_v = \bigoplus_{u \in \mathcal{N}(v)} \mathbf{W}_{spatial} \otimes_{\mathbb{H}} \log_{\mathbf{z}_v}^{\mathbb{H}}(\mathbf{z}_u)$$

where $\bigoplus$ is hyperbolic aggregation (Einstein midpoint), $\otimes_{\mathbb{H}}$ is hyperbolic matrix multiplication, and $\mathcal{N}(v)$ is the neighborhood of $v$.

Final node representation combines temporal and spatial information:
$$\mathbf{h}_v^{final} = \text{Combine}(\mathbf{h}_v^{temporal}, \mathbf{m}_v)$$

### 3.3 Training Procedure

**Loss Function:** Multi-objective loss combining task-specific loss and regularization:

$$\mathcal{L} = \mathcal{L}_{task} + \lambda_1 \mathcal{L}_{resolution} + \lambda_2 \mathcal{L}_{attention} + \lambda_3 \mathcal{L}_{hyperbolic}$$

where:
- $\mathcal{L}_{task}$: Cross-entropy (classification) or MSE (regression)
- $\mathcal{L}_{resolution} = -\text{Corr}(r_v, f_v)$: Encourages alignment between learned resolution and node frequency
- $\mathcal{L}_{attention} = \sum_v H(\alpha_v)$: Entropy regularization for attention specialization
- $\mathcal{L}_{hyperbolic}$: Constraint to keep embeddings within Poincaré ball

**Optimization:** Riemannian Adam optimizer with learning rate $\eta = 0.001$, batch size 512, and gradient clipping at norm 1.0.

### 3.4 Data Collection and Experimental Design

#### 3.4.1 Datasets

**D1. Synthetic Heterogeneous-Temporal Graphs:**
- Generate graphs with controlled temporal heterogeneity (CV ∈ {0.5, 1.0, 2.0, 4.0})
- Node dynamics: $\mathbf{x}_v^{(t)} = \sum_{k=1}^K A_{v,k} \sin(2\pi f_{v,k} t + \phi_{v,k})$
- Frequency distribution: Power-law $P(f) \propto f^{-\gamma}$ with $\gamma \in \{1.5, 2.0, 2.5\}$
- Sizes: 1K, 10K, 100K, 1M nodes
- Ground truth: Known node frequencies for resolution alignment validation

**D2. Brain Networks (HCP Dataset):**
- Human Connectome Project resting-state fMRI data
- 1000+ subjects, 360 ROIs (nodes), TR=0.72s
- Task: Predict cognitive scores from temporal brain dynamics
- Heterogeneity: Different brain regions exhibit vastly different temporal scales

**D3. Molecular Dynamics (MD17 Dataset):**
- Molecular dynamics simulations of small molecules
- Atoms as nodes, bonds as edges
- Task: Predict molecular energy and forces
- Heterogeneity: Bond vibrations vs. conformational changes

**D4. Social Networks (JODIE Dataset):**
- Reddit, Wikipedia, MOOC user-item interactions
- Task: Link prediction, user engagement forecasting
- Heterogeneity: Viral vs. organic content spread

#### 3.4.2 Baseline Methods

1. **TGAT** (Xu et al., 2020): Temporal graph attention with fixed resolution
2. **TGN** (Rossi et al., 2020): Memory-based temporal graph network
3. **SpikeNet** (Li et al., 2022): Event-driven spiking neural network
4. **Hyperbolic STGN** (Xu et al., 2024): Hyperbolic spatial hierarchy, fixed temporal resolution
5. **Decoupled DSTG** (Wang et al., 2024): Two-scale decomposition (trend/seasonal)

#### 3.4.3 Evaluation Metrics

**Predictive Performance:**
- Accuracy/F1-score (classification tasks)
- MAE/RMSE (regression tasks)
- AUC-ROC (link prediction)

**Computational Efficiency:**
- FLOPs: Total floating-point operations for temporal processing
- Wall-clock time: Actual training/inference time
- Memory consumption: Peak GPU memory usage
- Efficiency ratio: $\eta = \frac{\text{Accuracy}}{\text{FLOPs}} \times 100$

**Mechanism Validation:**
- Resolution alignment: Spearman correlation $\rho(r_v, f_v)$
- Attention specialization: Percentage of nodes with >60% attention on correct scale
- Scale assignment accuracy: Confusion matrix of attention distribution vs. ground truth frequency bins

**Scalability:**
- Maximum graph size trainable in 24 hours
- Scaling curve: Training time vs. number of nodes

### 3.5 Experimental Protocol

**Phase 1: Synthetic Validation (Month 3)**
- Train on synthetic graphs with known ground truth
- Validate resolution alignment (P2: $\rho > 0.6$)
- Validate attention specialization (P3: >60% correct assignment)
- Ablation studies: Remove hyperbolic/wavelet/attention components

**Phase 2: Real-World Validation (Months 4-5)**
- Train on HCP, MD17, JODIE datasets
- Compare against all baselines
- Validate Pareto improvement (P1: ≥95% accuracy, ≤70% FLOPs)
- Cross-domain analysis: Identify which domains benefit most

**Phase 3: Scalability Testing (Month 6)**
- Train on 1M-node synthetic graphs
- Measure training time, memory, convergence
- Validate P4: <24 hours on single A100 GPU

**Phase 4: Analysis and Ablation (Month 6)**
- Ablation matrix: 8 configurations (±hyperbolic, ±wavelet, ±attention)
- Hyperparameter sensitivity: Curvature, wavelet scales, attention temperature
- Visualization: t-SNE of hyperbolic embeddings colored by frequency
- Attention pattern analysis: Heatmaps of attention distribution

### 3.6 Falsification Criteria

The hypothesis will be considered **falsified** if:

1. **F1 (No Pareto Improvement):** HyperWave achieves <90% of best baseline accuracy on ≥3 out of 4 datasets
2. **F2 (No Resolution Alignment):** Spearman $\rho < 0.2$ between learned resolution and ground truth frequency on synthetic graphs
3. **F3 (No Attention Specialization):** Attention distribution is uniform/random (entropy >0.9 of maximum) across >50% of nodes
4. **F4 (Scalability Failure):** Out-of-memory or >72 hours training time on 1M-node graphs

### 3.7 Implementation Details

**Framework:** PyTorch 2.0, PyTorch Geometric 2.3
**Hyperbolic Operations:** geoopt library for Riemannian optimization
**Wavelet Transform:** PyWavelets (pywt) for CWT implementation
**Hardware:** NVIDIA A100 GPU (40GB), 128GB RAM
**Code Repository:** Open-source release on GitHub with full reproducibility

**Hyperparameters:**
- Hyperbolic dimension: $d_h = 64$
- Feature dimension: $d = 128$
- Wavelet scales: $s_{fine} = 2, s_{medium} = 8, s_{coarse} = 32$
- Curvature: $c = 1.0$ (learnable)
- Learning rate: $\eta = 0.001$ with cosine annealing
- Regularization: $\lambda_1 = 0.1, \lambda_2 = 0.01, \lambda_3 = 0.001$

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome (O1):** HyperWave-TGN will achieve Pareto improvement over state-of-the-art baselines on at least 2 out of 4 datasets, maintaining ≥95% predictive accuracy while reducing temporal processing FLOPs by 30-50%. This will be quantified through the computational efficiency ratio $\eta$ and validated through statistical significance testing (paired t-tests, $p < 0.05$).

**Mechanistic Validation (O2):** On synthetic graphs with ground truth, we expect:
- Resolution alignment: Spearman $\rho > 0.6$ between hyperbolic distance and node frequency
- Attention specialization: >70% of high-frequency nodes assign majority attention to fine wavelets, >60% of low-frequency nodes to coarse wavelets
- Interpretability: Clear clustering of nodes in hyperbolic space by temporal characteristics

**Scalability Demonstration (O3):** HyperWave-TGN will successfully train on 1M-node temporal graphs within 24 hours on a single A100 GPU, demonstrating 2-3× speedup over fixed-resolution baselines while maintaining competitive accuracy.

**Cross-Domain Applicability (O4):** The method will show consistent benefits across diverse domains:
- Brain networks: 15-25% FLOPs reduction (high heterogeneity, CV ≈ 3.5)
- Molecular dynamics: 20-30% reduction (moderate heterogeneity, CV ≈ 2.2)
- Social networks: 10-20% reduction (variable heterogeneity, CV ≈ 1.8)

**Theoretical Insights (O5):** Formal characterization of:
- Relationship between graph temporal heterogeneity (CV) and computational savings
- Conditions under which hyperbolic embeddings optimally encode temporal scales
- Theoretical bounds on attention specialization given frequency distributions

### 4.2 Scientific Impact

**Advancing Temporal Graph Learning Theory:**
This research establishes the first principled connection between hyperbolic geometry and temporal scale hierarchies, extending the theoretical foundations of geometric deep learning. The framework provides a new lens for understanding heterogeneous temporal dynamics in complex systems, with implications for temporal graph signal processing, multi-scale analysis, and adaptive computation.

**Methodological Contributions:**
The integration of hyperbolic embeddings, wavelet transforms, and attention mechanisms creates a new paradigm for adaptive temporal graph learning. The wavelet-based temporal graph signal processing framework can be adopted independently in other architectures, while the synthetic graph generation protocol enables controlled evaluation of temporal methods.

**Bridging Multiple Research Communities:**
This work connects temporal graph learning, hyperbolic representation learning, wavelet analysis, and neuroscience/chemistry/social network analysis, fostering cross-disciplinary collaboration as envisioned by the workshop.

### 4.3 Practical Impact

**Enabling Real-Time Large-Scale Applications:**
The 30-50% computational reduction enables real-time processing of billion-scale temporal graphs, democratizing temporal graph learning for:
- **Healthcare:** Real-time brain network analysis for seizure prediction, mental state decoding
- **Finance:** Fraud detection in transaction networks with millisecond latency requirements
- **E-commerce:** Personalized recommendations on billion-user platforms
- **Cybersecurity:** Anomaly detection in network traffic graphs

**Domain-Specific Applications:**

*Neuroscience:* Adaptive temporal resolution matches the multi-scale nature of brain dynamics (millisecond spikes to minute-scale BOLD signals), improving cognitive state prediction and brain-computer interfaces.

*Drug Discovery:* Efficient molecular dynamics simulation enables longer timescale predictions, accelerating conformational sampling and binding affinity estimation.

*Social Media:* Distinguishing viral (fast) from organic (slow) content spread improves misinformation detection and recommendation quality.

**Resource Efficiency:**
Reducing computational costs by 30-50% translates to:
- Lower energy consumption and carbon footprint
- Accessibility for researchers without access to large GPU clusters
- Faster iteration cycles in model development

### 4.4 Broader Impacts

**Open Science:** Full code release, pre-trained models, and synthetic datasets will accelerate research in temporal graph learning and hyperbolic neural networks.

**Educational Value:** The integration of concepts from differential geometry, signal processing, and graph neural networks provides rich educational material for graduate courses.

**Ethical Considerations:** Improved fraud detection and misinformation identification contribute to safer online ecosystems. However, we acknowledge potential dual-use concerns (e.g., surveillance) and will include ethical guidelines in documentation.

**Future Research Directions:**
This work opens multiple avenues:
- Extension to continuous-time temporal graphs with irregular timestamps
- Integration with causal reasoning for temporal graph interventions
- Application to temporal knowledge graphs and multi-modal temporal data
- Theoretical analysis of expressiveness and generalization bounds
- Hardware-aware optimization for edge devices

### 4.5 Success Metrics and Dissemination

**Publication Targets:**
- Top-tier ML conferences (NeurIPS, ICML, ICLR) for methodological contributions
- Domain-specific venues (MICCAI for brain networks, NeurIPS workshops for molecular dynamics)
- Journal articles in Nature Machine Intelligence or JMLR for comprehensive treatment

**Community Engagement:**
- Workshop presentation and poster at Temporal Graph Learning Workshop
- Tutorial sessions at major conferences
- Collaboration with domain experts for application papers

**Long-Term Vision:**
HyperWave-TGN represents a step toward **adaptive, domain-aware temporal graph learning** where models automatically discover and exploit the temporal structure of data. This paradigm shift from uniform to heterogeneous temporal processing has the potential to transform how we model dynamic complex systems across science and industry.

---

**Total Word Count:** ~4,800 words (extended for comprehensiveness; can be condensed to 2,000 words by reducing background and implementation details if required)