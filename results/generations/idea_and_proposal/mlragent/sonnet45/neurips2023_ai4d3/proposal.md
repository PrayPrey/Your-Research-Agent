# Uncertainty-Aware Multi-Fidelity Learning for Accelerated Binding Affinity Prediction

## 1. Introduction

### Background

Drug discovery is a notoriously expensive and time-consuming process, with the average cost of bringing a new drug to market exceeding $2.6 billion and requiring 10-15 years of development. A critical bottleneck in this pipeline is the accurate prediction of binding affinity between potential drug compounds and their target proteins. This prediction fundamentally determines whether a molecule will effectively modulate a biological target, making it one of the most crucial steps in early-stage drug discovery.

Current approaches to binding affinity prediction face an inherent accuracy-cost dilemma. High-fidelity methods such as free energy perturbation calculations using molecular dynamics (MD) simulations can achieve chemical accuracy but require days to weeks of computational time per compound. Conversely, low-fidelity methods like molecular docking or fast machine learning models can screen thousands of compounds per hour but suffer from poor accuracy and high false positive rates. This trade-off forces researchers into a Catch-22: either screen many compounds inaccurately or few compounds accurately.

Recent advances in deep learning have shown promise in molecular property prediction, with graph neural networks and 3D convolutional architectures achieving impressive results. However, these approaches typically rely on single-fidelity training data and provide point estimates without uncertainty quantification. This limitation is particularly problematic in drug discovery, where overconfident predictions can lead to costly experimental validation of false positives or premature dismissal of viable candidates.

Multi-fidelity modeling, successfully applied in aerospace engineering and computational physics, offers a potential solution by learning correlations between cheap approximations and expensive ground truth. Meanwhile, Bayesian deep learning provides a principled framework for uncertainty quantification. Despite these parallel advances, their integration for binding affinity prediction remains largely unexplored.

### Research Objectives

This research proposes to develop and validate a novel **Uncertainty-Aware Multi-Fidelity Bayesian Neural Network (UMF-BNN)** framework with the following specific objectives:

1. **Develop a hierarchical multi-fidelity architecture** that efficiently integrates diverse data sources spanning molecular docking scores, quantum mechanical calculations, experimental binding assays, and MD simulations.

2. **Implement rigorous Bayesian uncertainty quantification** using scalable variational inference to provide calibrated confidence intervals for binding affinity predictions.

3. **Design an active learning strategy** that leverages uncertainty estimates to intelligently select compounds for expensive high-fidelity evaluation, maximizing information gain per computational investment.

4. **Validate the framework** on standard benchmarks and demonstrate 10-100x computational savings while maintaining or improving predictive accuracy compared to pure high-fidelity approaches.

5. **Establish generalizability** by extending the framework to related drug discovery tasks including solubility prediction and ADMET property estimation.

### Significance

This research addresses critical gaps in AI-driven drug discovery with significant scientific and practical implications:

**Scientific Impact**: The proposed framework advances the state-of-the-art by demonstrating how multi-fidelity learning and uncertainty quantification can be synergistically combined for molecular property prediction. It establishes theoretical foundations for understanding information flow across fidelity levels in chemical space and provides methodological innovations applicable to broader scientific machine learning problems.

**Practical Impact**: By reducing computational costs by 10-100x while maintaining accuracy, this work can dramatically accelerate early-stage drug screening. The uncertainty-aware predictions enable risk-stratified compound prioritization, reducing false discovery rates by 30-50% and allowing researchers to make more informed decisions about experimental resource allocation. This translates to faster identification of promising drug candidates, reduced development costs, and ultimately more rapid delivery of therapeutic solutions to patients.

## 2. Methodology

### 2.1 Data Collection and Preprocessing

#### Multi-Fidelity Data Sources

We will construct a comprehensive multi-fidelity dataset spanning four distinct fidelity levels:

**Level 0 (Lowest Fidelity)**: Molecular docking scores from AutoDock Vina and Glide, providing fast geometric-based binding estimates. We will generate docking scores for 500,000 protein-ligand pairs from PDBbind, DUD-E, and DEKOIS databases.

**Level 1 (Low-Medium Fidelity)**: Fast machine learning predictions from existing models (e.g., RF-Score, NNScore) and semi-empirical quantum mechanical calculations (PM6, AM1) for binding energy estimates. These will be computed for 100,000 carefully selected diverse compounds.

**Level 2 (Medium-High Fidelity)**: Experimental binding affinity measurements from IC50, Ki, and Kd assays compiled from ChEMBL, BindingDB, and PDBbind databases, comprising approximately 50,000 high-quality measurements.

**Level 3 (Highest Fidelity)**: Free energy perturbation (FEP) calculations using molecular dynamics simulations with explicit solvent. We will generate or collect 5,000 high-accuracy FEP calculations focusing on pharmaceutically relevant target classes.

#### Data Preprocessing

Molecular structures will be featurized using multiple complementary representations:
- **1D**: Extended-connectivity fingerprints (ECFP), molecular descriptors (RDKit)
- **2D**: Molecular graphs with atom and bond features
- **3D**: Atomic coordinates and electron density grids from docking poses or crystal structures

Protein targets will be represented using:
- Binding pocket residue sequences and structural features
- 3D voxel grids of binding sites with physicochemical properties
- Pre-trained protein language model embeddings (ESM-2)

### 2.2 Hierarchical Multi-Fidelity Neural Architecture

#### Mathematical Framework

Let $f_\ell(\mathbf{x})$ denote the prediction function at fidelity level $\ell \in \{0,1,2,3\}$ for input features $\mathbf{x}$ representing a protein-ligand complex. We model the relationship between fidelity levels using an additive correction framework:

$$f_\ell(\mathbf{x}) = \rho_\ell(\mathbf{x}) \cdot f_{\ell-1}(\mathbf{x}) + \delta_\ell(\mathbf{x})$$

where $\rho_\ell(\mathbf{x})$ is a learned scaling function and $\delta_\ell(\mathbf{x})$ is an additive correction, both parameterized by neural networks.

#### Network Architecture

Our hierarchical architecture consists of four interconnected modules:

**Shared Encoder ($E_{\text{shared}}$)**: A graph neural network processes molecular structure:

$$\mathbf{h}_v^{(k)} = \text{AGGREGATE}^{(k)}\left(\left\{\mathbf{h}_u^{(k-1)} : u \in \mathcal{N}(v)\right\}\right)$$

where $\mathbf{h}_v^{(k)}$ represents node $v$'s embedding at layer $k$, and $\mathcal{N}(v)$ denotes its neighborhood. We employ attention-based aggregation:

$$\mathbf{h}_v^{(k)} = \sigma\left(\sum_{u \in \mathcal{N}(v)} \alpha_{uv} \mathbf{W}^{(k)} \mathbf{h}_u^{(k-1)}\right)$$

with attention weights $\alpha_{uv} = \text{softmax}_u\left(\mathbf{a}^T [\mathbf{h}_v^{(k-1)} \| \mathbf{h}_u^{(k-1)}]\right)$.

**Fidelity-Specific Branches**: For each fidelity level $\ell$, we define:

$$f_0(\mathbf{x}) = \text{MLP}_0(E_{\text{shared}}(\mathbf{x}))$$

$$f_\ell(\mathbf{x}) = \rho_\ell(\mathbf{x}) \cdot f_{\ell-1}(\mathbf{x}) + \delta_\ell(\mathbf{x}), \quad \ell > 0$$

where $\rho_\ell(\mathbf{x}) = \text{sigmoid}(\text{MLP}_{\rho,\ell}([E_{\text{shared}}(\mathbf{x}), f_{\ell-1}(\mathbf{x})]))$ and $\delta_\ell(\mathbf{x}) = \text{MLP}_{\delta,\ell}([E_{\text{shared}}(\mathbf{x}), f_{\ell-1}(\mathbf{x})])$.

### 2.3 Bayesian Uncertainty Quantification

#### Variational Inference Framework

To quantify uncertainty, we place prior distributions over network weights $\mathbf{w}$: $p(\mathbf{w}) = \mathcal{N}(\mathbf{0}, \sigma_p^2 \mathbf{I})$. The posterior distribution $p(\mathbf{w}|\mathcal{D})$ for dataset $\mathcal{D} = \{(\mathbf{x}_i, y_i)\}_{i=1}^N$ is approximated using a variational distribution $q_\theta(\mathbf{w})$ parameterized by mean-field Gaussian: $q_\theta(\mathbf{w}) = \mathcal{N}(\boldsymbol{\mu}, \text{diag}(\boldsymbol{\sigma}^2))$.

The variational objective (ELBO) to maximize is:

$$\mathcal{L}(\theta) = \mathbb{E}_{q_\theta(\mathbf{w})}\left[\sum_{i=1}^N \log p(y_i | f_\mathbf{w}(\mathbf{x}_i))\right] - \text{KL}(q_\theta(\mathbf{w}) \| p(\mathbf{w}))$$

For multi-fidelity learning, we extend this to incorporate fidelity-specific likelihood terms:

$$\mathcal{L}_{\text{MF}}(\theta) = \sum_{\ell=0}^3 \lambda_\ell \mathbb{E}_{q_\theta(\mathbf{w})}\left[\sum_{i \in \mathcal{D}_\ell} \log p(y_i^{(\ell)} | f_{\mathbf{w},\ell}(\mathbf{x}_i))\right] - \text{KL}(q_\theta(\mathbf{w}) \| p(\mathbf{w}))$$

where $\mathcal{D}_\ell$ represents data at fidelity level $\ell$, and $\lambda_\ell$ are fidelity-specific weights learned during training.

#### Predictive Distribution

For a test input $\mathbf{x}^*$, the predictive distribution is:

$$p(y^* | \mathbf{x}^*, \mathcal{D}) = \int p(y^* | f_\mathbf{w}(\mathbf{x}^*)) q_\theta(\mathbf{w}) d\mathbf{w}$$

approximated via Monte Carlo sampling:

$$p(y^* | \mathbf{x}^*, \mathcal{D}) \approx \frac{1}{T} \sum_{t=1}^T p(y^* | f_{\mathbf{w}_t}(\mathbf{x}^*)), \quad \mathbf{w}_t \sim q_\theta(\mathbf{w})$$

yielding both predicted mean $\mu_{y^*} = \frac{1}{T}\sum_{t=1}^T f_{\mathbf{w}_t}(\mathbf{x}^*)$ and uncertainty estimate $\sigma_{y^*}^2 = \frac{1}{T}\sum_{t=1}^T (f_{\mathbf{w}_t}(\mathbf{x}^*) - \mu_{y^*})^2 + \sigma_{\text{aleatoric}}^2$.

### 2.4 Active Learning Strategy

#### Acquisition Function

We design an information-theoretic acquisition function that balances epistemic uncertainty with expected model improvement:

$$\alpha(\mathbf{x}) = \beta_1 \cdot \sigma_{y^*}(\mathbf{x}) + \beta_2 \cdot \text{EI}(\mathbf{x}) + \beta_3 \cdot \text{Cost}^{-1}(\mathbf{x})$$

where:
- $\sigma_{y^*}(\mathbf{x})$ is predictive uncertainty (epistemic + aleatoric)
- $\text{EI}(\mathbf{x}) = \mathbb{E}[\max(f(\mathbf{x}) - f(\mathbf{x}_{\text{best}}), 0)]$ is expected improvement
- $\text{Cost}(\mathbf{x})$ estimates computational cost of high-fidelity evaluation
- $\beta_1, \beta_2, \beta_3$ are weighting parameters optimized via cross-validation

#### Multi-Fidelity Active Learning Algorithm

```
Initialize: D_ℓ for all fidelity levels ℓ
for iteration = 1 to N_iterations:
    1. Train UMF-BNN on current D = {D_0, D_1, D_2, D_3}
    2. For unlabeled pool U:
       - Compute α(x) for all x in U
    3. Select k compounds: X_select = argmax_{X⊂U, |X|=k} Σ_{x∈X} α(x)
    4. Determine optimal fidelity level ℓ*(x) for each x ∈ X_select:
       ℓ*(x) = argmax_ℓ [Information_gain(x,ℓ) / Cost(x,ℓ)]
    5. Obtain labels y at selected fidelities and update D_{ℓ*(x)}
    6. If convergence criteria met, break
return Trained UMF-BNN model
```

### 2.5 Training Procedure

#### Loss Function

The complete training objective combines multi-fidelity predictions with uncertainty calibration:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MF}}(\theta) + \gamma \cdot \mathcal{L}_{\text{calib}}$$

where calibration loss enforces proper uncertainty quantification:

$$\mathcal{L}_{\text{calib}} = \sum_{q=1}^Q \left(\text{freq}(q) - \text{conf}(q)\right)^2$$

measuring deviation between predicted confidence levels $\text{conf}(q)$ and empirical frequencies $\text{freq}(q)$ across quantile bins.

#### Optimization

We employ Adam optimizer with learning rate scheduling: $\eta_t = \eta_0 \cdot \min(1, \frac{t_{\text{warmup}}}{t})$ for initial warmup, followed by cosine annealing. Batch construction samples proportionally from each fidelity level weighted by $\sqrt{|\mathcal{D}_\ell|}$ to balance representation.

### 2.6 Experimental Design and Validation

#### Benchmark Datasets

1. **PDBbind Core Set** (290 complexes): Standard benchmark with experimental binding affinities
2. **CASF-2016** (285 complexes): Diverse protein families for generalization testing
3. **Therapeutics Data Commons** (22 kinase datasets): Target-specific evaluation

#### Evaluation Metrics

- **Accuracy**: Pearson correlation ($r$), Spearman rank correlation ($\rho$), RMSE, MAE
- **Uncertainty Quality**: 
  - Calibration error: $\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$
  - Negative log-likelihood (NLL)
  - Sharpness: Average prediction interval width
- **Computational Efficiency**: 
  - Wall-clock time per prediction
  - Speedup factor vs. pure high-fidelity baseline
  - Area under efficiency curve (prediction quality vs. computational cost)

#### Experimental Protocol

1. **Baseline Comparison**: Compare UMF-BNN against:
   - Single-fidelity models (RF-Score, DeepDTA, EquiBind)
   - Ensemble methods (random forests, deep ensembles)
   - Existing uncertainty quantification methods (MC Dropout, evidential networks)
   - Traditional multi-fidelity methods (co-kriging)

2. **Ablation Studies**:
   - Impact of each fidelity level
   - Effectiveness of hierarchical vs. independent fidelity modeling
   - Contribution of uncertainty quantification to active learning performance

3. **Cross-Validation**: 5-fold cross-validation with scaffold splitting to assess generalization to novel chemical scaffolds

4. **Prospective Validation**: Apply to 1,000 unseen compounds from recent literature and compare predictions against newly published experimental data

5. **Active Learning Simulation**: Starting with 10% labeled high-fidelity data, simulate iterative data acquisition and measure learning curves

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Performance Targets**:

1. **Predictive Accuracy**: Achieve Pearson correlation $r \geq 0.85$ on held-out test sets, matching or exceeding pure high-fidelity MD simulation accuracy

2. **Computational Efficiency**: Demonstrate 10-100x speedup compared to direct high-fidelity calculations, with inference time <1 second per compound on standard GPU hardware

3. **Uncertainty Calibration**: Attain expected calibration error (ECE) <0.05, ensuring 95% prediction intervals contain true values 95% of the time

4. **Active Learning Gain**: Reduce amount of high-fidelity data needed by 50-70% to reach target accuracy through intelligent compound selection

5. **False Discovery Reduction**: Lower experimental false positive rate by 30-50% through uncertainty-guided filtering compared to confidence-agnostic top-k selection

**Qualitative Contributions**:

1. **Methodological Innovation**: First comprehensive framework integrating multi-fidelity learning with Bayesian uncertainty quantification specifically designed for binding affinity prediction

2. **Interpretable Uncertainty**: Decomposition of uncertainty into aleatoric (inherent noise) and epistemic (model uncertainty) components, enabling different downstream decision strategies

3. **Transferable Architecture**: Modular design allowing straightforward adaptation to other molecular property prediction tasks (solubility, permeability, toxicity)

4. **Open-Source Implementation**: Release of production-ready code, pre-trained models, and comprehensive tutorials to lower barriers to adoption

### Scientific Impact

This research advances multiple scientific frontiers:

**Machine Learning Theory**: Establishes theoretical understanding of information flow in hierarchical multi-fidelity models for high-dimensional chemical spaces, extending existing multi-fidelity theory beyond traditional engineering domains.

**Computational Chemistry**: Provides rigorous framework for combining physics-based simulations with data-driven models, bridging the gap between traditional computational chemistry and modern deep learning.

**Uncertainty Quantification**: Demonstrates practical Bayesian deep learning at scale for molecular sciences, addressing long-standing challenges in calibration and computational tractability for graph-structured chemical data.

**Active Learning**: Develops novel acquisition strategies specifically tailored to multi-fidelity scenarios common in scientific applications, balancing information gain against heterogeneous evaluation costs.

### Practical Impact

**Pharmaceutical Industry**: By reducing computational screening costs by 10-100x while maintaining accuracy, pharmaceutical companies can:
- Screen larger virtual libraries (millions vs. thousands of compounds)
- Perform more comprehensive lead optimization cycles
- Reduce time-to-candidate identification from months to weeks

**Academic Drug Discovery**: Resource-constrained academic labs gain access to capabilities previously requiring supercomputing infrastructure, democratizing AI-driven drug discovery.

**Precision Medicine**: Uncertainty-aware predictions enable patient-specific drug repurposing by identifying compounds with high confidence of efficacy for individual genetic profiles.

**Broader Applications**: The framework's generalizability extends impact beyond binding affinity to:
- Materials discovery (catalyst design, battery materials)
- Protein engineering (stability prediction, antibody design)
- Environmental chemistry (toxicity prediction, biodegradation)

### Risk Mitigation and Limitations

**Potential Limitations**:

1. **Data Quality Dependency**: Performance relies on quality of multi-fidelity training data; systematic biases in low-fidelity data may propagate

2. **Domain Shift**: Model trained on specific protein families may require fine-tuning for novel targets

3. **Computational Overhead**: Bayesian inference adds 5-10x computational cost compared to deterministic models, though still vastly cheaper than high-fidelity simulations

**Mitigation Strategies**:

- Develop robust data filtering pipelines to identify and remove low-quality training instances
- Implement domain adaptation techniques for transfer to new target classes
- Optimize inference through distillation and quantization for production deployment
- Establish clear guidelines on applicability domains where model predictions are trustworthy

### Timeline and Milestones

**Year 1**: 
- Months 1-3: Data collection and preprocessing pipeline
- Months 4-8: Architecture development and initial training
- Months 9-12: Baseline comparisons and ablation studies

**Year 2**:
- Months 13-16: Active learning implementation and validation
- Months 17-20: Prospective validation and real-world case studies
- Months 21-24: Manuscript preparation, code release, and dissemination

This research promises to fundamentally transform early-stage drug discovery by making high-accuracy binding affinity prediction both computationally tractable and uncertainty-aware, ultimately accelerating the development of life-saving therapeutics.