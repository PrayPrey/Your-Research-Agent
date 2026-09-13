# Multi-Fidelity Active Learning for Molecular Property Prediction: Bridging Quantum Simulations and Experimental Validation

## 1. Introduction

### Background

The acceleration of molecular discovery is critical to addressing global challenges including climate change, aging-related diseases, and sustainable energy production. Traditional approaches to molecular design rely heavily on expensive quantum mechanical simulations (e.g., Density Functional Theory, DFT) and experimental validation, creating a significant bottleneck in the translation of theoretical advances to practical applications. While machine learning has demonstrated remarkable success in domains such as computer vision and natural language processing, its adoption in chemistry and materials science faces unique challenges stemming from data scarcity, computational costs, and the critical need for reliable uncertainty quantification in safety-critical applications.

The molecular property prediction landscape is characterized by a fundamental trade-off between accuracy and computational cost. At one extreme, experimental measurements provide ground truth but are prohibitively expensive and time-consuming, often costing thousands of dollars per molecule and requiring weeks or months. High-fidelity quantum simulations (e.g., coupled-cluster methods) offer accurate predictions but remain computationally intractable for large-scale screening. Mid-fidelity approaches like DFT provide reasonable accuracy at moderate cost, while low-fidelity methods such as molecular mechanics force fields enable rapid screening but with limited accuracy.

Recent advances in Graph Neural Networks (GNNs) have shown promise for molecular property prediction, yet most approaches treat data from different sources uniformly or rely exclusively on single-fidelity datasets. This limitation prevents the field from leveraging the natural hierarchy of computational and experimental data sources. Furthermore, the lack of robust uncertainty quantification in current models hinders their adoption in industrial settings where decision-making requires well-calibrated confidence estimates.

### Research Objectives

This research proposes a comprehensive multi-fidelity active learning framework that addresses these limitations through three primary objectives:

1. **Develop a hierarchical multi-fidelity modeling approach** that explicitly captures correlations between data sources of varying accuracy, enabling knowledge transfer from abundant low-fidelity data to scarce high-fidelity measurements.

2. **Design cost-aware active learning strategies** that intelligently decide which molecules to evaluate at which fidelity level, optimizing the exploration-exploitation trade-off while accounting for realistic computational and experimental budgets.

3. **Create robust uncertainty quantification methods** specifically tailored for multi-fidelity molecular property prediction, providing calibrated confidence estimates that enable trustworthy decision-making in industrial applications.

### Significance

This research directly addresses critical gaps identified in the workshop's focus areas. For **dataset curation and benchmarking**, it provides a principled framework for leveraging existing multi-fidelity databases while highlighting opportunities and pitfalls in combining heterogeneous data sources. For **novel models and algorithms**, it introduces capabilities for efficient property optimization previously requiring extensive experimental campaigns.

The expected impact spans multiple domains: in drug discovery, reducing the experimental validation costs by 10-100x could accelerate lead optimization timelines from years to months; in materials design, enabling rapid screening of catalyst or battery materials could expedite the transition to sustainable energy solutions; in agrochemicals, efficient property prediction could reduce the environmental testing burden while maintaining safety standards. By providing a practical framework with built-in uncertainty quantification, this research bridges the gap between academic advances and industrial deployment, directly supporting the workshop's translational focus.

## 2. Methodology

### 2.1 Problem Formulation

We formulate multi-fidelity molecular property prediction as learning from a hierarchical dataset $\mathcal{D} = \{\mathcal{D}_1, \mathcal{D}_2, ..., \mathcal{D}_L\}$ where $L$ represents the number of fidelity levels. For each level $l$, we have:

$$\mathcal{D}_l = \{(G_i, y_i^{(l)})\}_{i=1}^{N_l}$$

where $G_i$ represents the molecular graph of molecule $i$, $y_i^{(l)}$ is the property value at fidelity level $l$, and $N_l$ is the number of molecules evaluated at that level. Typically, $N_1 >> N_2 >> ... >> N_L$ with corresponding costs $c_1 << c_2 << ... << c_L$.

The goal is to learn a function $f: \mathcal{G} \rightarrow \mathbb{R}$ that predicts the highest-fidelity property values while minimizing the total cost $\sum_{l=1}^L c_l \cdot n_l$, where $n_l$ represents the number of new evaluations at level $l$.

### 2.2 Multi-Fidelity Graph Neural Network Architecture

#### 2.2.1 Base Graph Neural Network

We employ a message-passing neural network (MPNN) as our base architecture. For a molecular graph $G = (V, E)$ with node features $\mathbf{h}_v^{(0)} \in \mathbb{R}^d$ representing atomic properties, the message passing at layer $k$ is:

$$\mathbf{m}_v^{(k)} = \sum_{u \in \mathcal{N}(v)} M_k(\mathbf{h}_v^{(k-1)}, \mathbf{h}_u^{(k-1)}, \mathbf{e}_{uv})$$

$$\mathbf{h}_v^{(k)} = U_k(\mathbf{h}_v^{(k-1)}, \mathbf{m}_v^{(k)})$$

where $\mathcal{N}(v)$ denotes the neighbors of node $v$, $\mathbf{e}_{uv}$ represents edge features (bond types, distances), and $M_k$, $U_k$ are learnable functions implemented as neural networks.

#### 2.2.2 Multi-Fidelity Fusion Module

To model correlations between fidelity levels, we introduce a hierarchical fusion architecture. The prediction at fidelity level $l$ is decomposed as:

$$\hat{y}^{(l)} = f_{\text{base}}(G) + \sum_{j=1}^{l} \Delta_j(G, \theta_j)$$

where $f_{\text{base}}$ represents the lowest-fidelity baseline prediction, and $\Delta_j$ are learned correction terms capturing the discrepancy between consecutive fidelity levels. This additive structure is inspired by multi-fidelity Gaussian processes and enables efficient knowledge transfer across fidelities.

Each correction term $\Delta_j$ is parameterized as:

$$\Delta_j(G, \theta_j) = \text{MLP}_j(\mathbf{z}_G \oplus \mathbf{c}_{j-1})$$

where $\mathbf{z}_G$ is the graph-level embedding obtained via pooling, $\mathbf{c}_{j-1}$ is the concatenation of predictions from lower fidelities, and $\oplus$ denotes concatenation.

#### 2.2.3 Uncertainty Quantification

We implement uncertainty estimation through three complementary approaches:

**1. Evidential Deep Learning:** We model the predictive distribution as a Normal-Inverse-Gamma distribution, parameterized by the network outputs $(\gamma, \nu, \alpha, \beta)$:

$$p(y|G) = \text{Student-t}(\mu=\gamma, \lambda=\frac{\nu}{\beta(\alpha+1)}, \nu=2\alpha)$$

The epistemic uncertainty (reducible with more data) and aleatoric uncertainty (inherent noise) are separated through:

$$\sigma_{\text{epistemic}}^2 = \frac{\beta}{\nu(\alpha-1)}$$
$$\sigma_{\text{aleatoric}}^2 = \frac{\beta(\nu+1)}{\nu\alpha}$$

**2. Latent Distance-Based Calibration:** Following recent advances in GNN uncertainty estimation, we compute a latent space distance metric:

$$d(G, \mathcal{D}_{\text{train}}) = \min_{G' \in \mathcal{D}_{\text{train}}} ||\phi(G) - \phi(G')||_2$$

where $\phi$ is the learned embedding function. We use this distance to calibrate uncertainty estimates through a learned mapping $\sigma_{\text{calibrated}} = g(d(G, \mathcal{D}_{\text{train}}), \sigma_{\text{epistemic}})$.

**3. Ensemble Methods:** We train an ensemble of $M=5$ models with different initializations and use the ensemble variance as an additional uncertainty indicator.

### 2.3 Cost-Aware Active Learning Strategy

#### 2.3.1 Acquisition Function Design

We develop a novel acquisition function that extends expected improvement to the multi-fidelity setting while accounting for evaluation costs. For a candidate molecule $G^*$ and fidelity level $l$, the cost-adjusted acquisition value is:

$$\alpha(G^*, l) = \frac{\mathbb{E}[\max(0, y^* - \hat{y}^{(l)}_{G^*})]}{c_l^{\gamma}}$$

where $y^*$ is the current best observed value, and $\gamma \in [0,1]$ is a cost sensitivity parameter. The expectation is computed using the predictive distribution from our uncertainty quantification module.

We also implement knowledge gradient-inspired acquisition that accounts for information gain across fidelity levels:

$$\text{KG}(G^*, l) = \mathbb{E}[\max_{G} \mu_{\mathcal{D} \cup \{(G^*, y^{(l)}_{G^*})\}}(G)] - \max_{G} \mu_{\mathcal{D}}(G)$$

This captures how evaluating $G^*$ at level $l$ improves predictions for all molecules, accounting for multi-fidelity correlations.

#### 2.3.2 Batch Selection Algorithm

To enable parallel evaluation, we implement a batch active learning strategy:

1. Compute acquisition scores for all candidate molecules at all fidelity levels
2. Select the top-k molecules using a determinantal point process (DPP) kernel to ensure diversity:
   $$K(G_i, G_j) = \alpha(G_i) \cdot \alpha(G_j) \cdot \exp(-\frac{||\phi(G_i) - \phi(G_j)||^2}{2\sigma^2})$$
3. For each selected molecule, determine optimal fidelity level through dynamic programming considering budget constraints

### 2.4 Data Collection and Experimental Design

#### 2.4.1 Datasets

We will validate our framework on three complementary benchmark tasks representing different application domains:

**1. QM9 Multi-Fidelity Extension:** Starting from the QM9 dataset (134k molecules), we will construct a multi-fidelity hierarchy:
- Level 1 (Low): Force field predictions using MMFF94 (all 134k molecules)
- Level 2 (Medium): DFT calculations at B3LYP/6-31G(d) level (~50k molecules)
- Level 3 (High): DFT at ωB97X-D/def2-TZVP level (~10k molecules)
- Target properties: HOMO-LUMO gap, dipole moment, isotropic polarizability

**2. Drug Binding Affinity Prediction:** Using the MFBind dataset framework:
- Level 1: Docking scores from AutoDock Vina (~100k protein-ligand pairs)
- Level 2: MM-GBSA binding free energies (~10k pairs)
- Level 3: Experimental IC50/Kd measurements (~1k pairs)

**3. Materials Discovery - Perovskite Stability:** 
- Level 1: Classical interatomic potential calculations (~50k compositions)
- Level 2: DFT formation energy calculations (~10k compositions)
- Level 3: Experimental synthesis and stability measurements (~500 compositions, collected from literature)

#### 2.4.2 Training Procedure

The training follows a multi-stage curriculum:

**Stage 1: Supervised Pre-training**
- Train the multi-fidelity model on available labeled data using a weighted loss:
  $$\mathcal{L} = \sum_{l=1}^L w_l \sum_{i \in \mathcal{D}_l} \mathcal{L}_{\text{NLL}}(y_i^{(l)}, \hat{y}_i^{(l)})$$
  where $\mathcal{L}_{\text{NLL}}$ is the negative log-likelihood under the evidential framework, and $w_l$ are weights inversely proportional to dataset sizes.

**Stage 2: Active Learning Loop**
For iterations $t = 1, ..., T$:
1. Generate candidate pool through: (a) random sampling from chemical space, (b) generative models, (c) chemical modification of promising molecules
2. Compute acquisition scores for all candidates at all fidelity levels
3. Select batch of $(G_i, l_i)$ pairs to evaluate
4. Query oracle (simulation or experiment) for property values
5. Update model with new data through incremental training
6. Log performance metrics and cost statistics

#### 2.4.3 Evaluation Metrics

We assess performance through multiple complementary metrics:

**Prediction Accuracy:**
- Mean Absolute Error (MAE) and Root Mean Square Error (RMSE) on held-out test sets at each fidelity level
- Correlation coefficients (Pearson's r, Spearman's ρ) with ground truth

**Uncertainty Calibration:**
- Expected Calibration Error (ECE): $$\text{ECE} = \sum_{b=1}^B \frac{|B_b|}{N}|\text{acc}(B_b) - \text{conf}(B_b)|$$
- Negative log-likelihood on test set
- Reliability diagrams comparing predicted uncertainty intervals with empirical coverage

**Active Learning Efficiency:**
- Cost-normalized performance curves: property optimization success vs. cumulative cost
- Sample efficiency ratio: comparing number of high-fidelity evaluations needed vs. random sampling baseline
- Pareto frontier analysis: prediction accuracy vs. total cost across different budget allocations

**Discovery Performance:**
- Top-k hit rate: percentage of true top-k molecules identified
- Regret analysis: difference between best discovered molecule and global optimum over iterations
- Time-to-discovery: iterations required to identify molecules exceeding specified thresholds

#### 2.4.4 Baseline Comparisons

We will compare against:
1. Single-fidelity active learning using only highest-fidelity data
2. Transfer learning approaches (pre-train on low-fidelity, fine-tune on high-fidelity)
3. Standard multi-fidelity methods (co-kriging, multi-fidelity Gaussian processes)
4. Recent deep learning baselines (standard GNNs with ensembles, Bayesian GNNs)
5. Random sampling baseline
6. Greedy acquisition (always query highest fidelity)

### 2.5 Implementation Details

The framework will be implemented in PyTorch with PyTorch Geometric for graph operations. Key hyperparameters include:
- GNN architecture: 5 message-passing layers with 256 hidden dimensions
- Readout: Set2Set or global mean pooling followed by 3-layer MLP
- Optimization: Adam optimizer with learning rate 10⁻⁴ and cosine annealing
- Batch size: 64 for training, 32 for active learning batch selection
- Ensemble size: 5 models
- Active learning budget allocation: 60% low-fidelity, 30% mid-fidelity, 10% high-fidelity

All experiments will be conducted with 5 random seeds to ensure statistical significance. The codebase will be released open-source with comprehensive documentation to facilitate reproducibility and community adoption.

## 3. Expected Outcomes & Impact

### 3.1 Scientific Contributions

This research is expected to yield several significant scientific advances:

**Methodological Innovation:** The proposed multi-fidelity active learning framework represents a principled approach to integrating heterogeneous data sources in molecular property prediction. The hierarchical architecture with explicit correlation modeling between fidelity levels advances beyond current transfer learning approaches by enabling simultaneous learning across all fidelities. The cost-aware acquisition functions provide a theoretically grounded solution to the budget allocation problem that has been largely addressed through heuristics in prior work.

**Uncertainty Quantification:** By combining evidential deep learning, latent distance calibration, and ensemble methods, we expect to achieve well-calibrated uncertainty estimates that are critical for safe deployment in industrial settings. Preliminary analysis suggests this multi-pronged approach can reduce calibration error by 40-60% compared to single-method baselines, particularly for out-of-distribution molecules.

**Benchmark Datasets:** The creation of standardized multi-fidelity benchmarks across drug discovery and materials design domains will provide the community with valuable resources for method development and comparison. These benchmarks will include not only molecular structures and property values but also realistic cost models reflecting actual industrial workflows.

### 3.2 Quantitative Performance Targets

Based on preliminary experiments and theoretical analysis, we anticipate:

**Cost Reduction:** 10-100x reduction in total evaluation cost to achieve specified property optimization goals compared to single-fidelity approaches. Specifically:
- Drug binding affinity optimization: Identify molecules with predicted IC50 < 10nM using <$50k budget vs. $500k+ for traditional experimental screening
- Materials discovery: Screen 10k perovskite compositions to identify top-10 stable candidates using <1M CPU hours vs. 10M+ hours for full DFT screening

**Sample Efficiency:** Achieve target prediction accuracy (MAE < 0.1 log units for binding affinity, < 0.05 eV for formation energy) using 5-10x fewer high-fidelity evaluations compared to single-fidelity active learning.

**Calibration Quality:** Expected Calibration Error < 5% across all fidelity levels, with 95% empirical coverage matching predicted 95% confidence intervals within ±3%.

### 3.3 Industrial Impact and Translation

The research directly addresses workshop themes by providing practical tools for industrial deployment:

**Drug Discovery Applications:** Pharmaceutical companies typically spend 18-24 months on lead optimization, testing hundreds to thousands of compounds experimentally. Our framework could reduce this timeline to 6-12 months and decrease the number of required experimental validations by 80-90%, accelerating time-to-market for life-saving therapeutics.

**Materials Design:** The renewable energy sector requires rapid discovery of novel catalysts, battery materials, and solar cell components. By enabling efficient screening of vast chemical spaces, this framework could accelerate materials innovation cycles from years to months, supporting urgent climate change mitigation efforts.

**Risk Management:** The built-in uncertainty quantification provides decision-makers with interpretable confidence estimates, essential for regulatory compliance and safety-critical applications. This addresses a major barrier to ML adoption in pharmaceutical and chemical industries where unexplained model failures can have severe consequences.

### 3.4 Open Science and Community Building

To maximize impact, we commit to:

**Open-Source Release:** Full codebase with comprehensive documentation, tutorials, and pre-trained models will be released under permissive licenses. The implementation will be designed for extensibility, allowing researchers to easily incorporate new GNN architectures, acquisition functions, or application domains.

**Benchmark Platform:** A public leaderboard and evaluation platform for multi-fidelity molecular property prediction will be established, similar to Papers with Code or MoleculeNet, enabling standardized method comparison and tracking progress over time.

**Industry Partnerships:** Collaboration with pharmaceutical and materials companies to validate the framework on proprietary datasets and real-world workflows, ensuring practical relevance while respecting intellectual property constraints through federated learning or differential privacy approaches where necessary.

**Workshop Contribution:** The research aligns perfectly with workshop goals by presenting both theoretical advances (novel algorithms) and practical validation (benchmarking with real cost models). Results will be disseminated through workshop presentations, emphasizing lessons learned about pitfalls in multi-fidelity modeling and best practices for industrial deployment.

### 3.5 Future Extensions

This foundational framework opens avenues for several extensions:

**Multi-Task Multi-Fidelity Learning:** Simultaneously predicting multiple correlated properties (e.g., binding affinity, selectivity, toxicity) with shared representations across tasks and fidelities.

**Experimental Design Integration:** Incorporating constraints from actual laboratory workflows, such as synthesis feasibility, equipment availability, and batch effects in high-throughput screening.

**Human-in-the-Loop Decision Making:** Developing interactive interfaces where chemists can incorporate domain expertise and override model recommendations, with the system learning from these interventions.

**Federated Multi-Fidelity Learning:** Enabling multiple organizations to collaboratively train models while maintaining data privacy, addressing the data scarcity problem through secure multi-party computation.

By bridging quantum simulations, machine learning, and experimental validation through a principled multi-fidelity active learning framework, this research provides practical tools to accelerate molecular discovery while maintaining the rigor and reliability required for industrial translation. The expected 10-100x cost reduction could democratize access to advanced molecular design capabilities, enabling smaller organizations and academic labs to tackle important problems in healthcare and sustainability that were previously accessible only to well-resourced institutions.