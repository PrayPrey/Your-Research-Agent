# Research Proposal: Evidential Deep Learning with Hierarchical Protein Priors for Calibrated Uncertainty in Biomolecular Property Prediction

## 1. Introduction

### 1.1 Background

Biomolecular design represents one of the most promising frontiers in modern science, with applications spanning drug discovery, enzyme engineering, and therapeutic protein development. Generative machine learning has emerged as a powerful tool in this domain, enabling the computational design of novel proteins, small molecules, and nucleic acids with desired properties. However, a critical disconnect persists between computational predictions and experimental validation workflows: current ML models predominantly provide point predictions without reliable uncertainty estimates, fundamentally limiting their utility in guiding experimental decisions.

In drug discovery and protein engineering pipelines, researchers routinely face the challenge of prioritizing which computationally designed candidates to synthesize and test experimentally. When a model predicts binding affinities or protein stability values, practitioners cannot distinguish between confident predictions backed by substantial training evidence and uncertain predictions extrapolating beyond the model's knowledge. This limitation leads to inefficient experimental campaigns where resources are wasted validating low-quality candidates that the model was inherently uncertain about. The cost implications are substantial: experimental validation of a single protein-ligand binding affinity can require weeks of effort and thousands of dollars, making intelligent prioritization essential.

Uncertainty quantification (UQ) in deep learning has received considerable attention, with approaches including deep ensembles, Monte Carlo dropout, and Bayesian neural networks. However, these methods face significant limitations in the biomolecular domain. Deep ensembles require training multiple independent models, increasing computational costs by 5-10×. Monte Carlo dropout provides only approximate uncertainty estimates that are often poorly calibrated. Bayesian neural networks suffer from computational intractability for large protein language models. More fundamentally, none of these approaches naturally decompose uncertainty into its constituent components: aleatoric uncertainty arising from inherent measurement noise in experimental data, and epistemic uncertainty reflecting gaps in model knowledge.

Evidential deep learning offers a principled alternative by parameterizing higher-order distributions over prediction outputs, enabling direct estimation of both prediction values and their associated uncertainties in a single forward pass. Recent work has demonstrated the promise of this approach for drug-target interaction classification, but its application to continuous property regression in biomolecular design remains unexplored.

### 1.2 Research Objectives

This research proposes EPOEA (Evidential Protein Oracle with Epistemic Awareness), a novel framework that integrates Normal-Inverse-Gamma (NIG) evidential output layers with ESM-2 protein language model embeddings and hierarchical Pfam-based priors. Our primary objectives are:

1. **Develop a calibrated uncertainty quantification framework** for biomolecular property prediction that achieves Expected Calibration Error (ECE) below 0.15 on held-out experimental data.

2. **Enable efficient experimental prioritization** through uncertainty-guided candidate selection, targeting a 40% reduction in validation candidates required to identify top binders.

3. **Establish cross-family transfer capabilities** via hierarchical protein family priors that share uncertainty parameters across related proteins, maintaining ≥80% calibration performance on unseen protein families.

### 1.3 Significance

This research directly addresses the computational-experimental divide highlighted as a central challenge in biomolecular design. By providing well-calibrated uncertainty estimates that decompose into interpretable aleatoric and epistemic components, EPOEA enables experimentalists to make informed decisions about which predictions to trust and validate. The hierarchical prior structure leverages the rich taxonomic organization of protein families (Pfam), enabling knowledge transfer across related proteins and improving predictions for understudied targets.

The expected outcomes have immediate practical implications: reducing experimental validation costs while maintaining or improving hit rates in drug discovery campaigns, enabling more efficient directed evolution experiments in protein engineering, and providing a principled framework for adaptive experimental design where uncertainty estimates guide the selection of informative experiments.

## 2. Methodology

### 2.1 Data Collection and Preprocessing

**Primary Training Data:**
We will utilize the PDBbind v2020 refined set, comprising approximately 5,000 high-quality protein-ligand complexes with experimentally measured binding affinities (Kd, Ki, or IC50 values). This curated dataset ensures reliable ground truth labels derived from crystal structures with resolution ≤2.5 Å and binding measurements from peer-reviewed literature.

**Supplementary Data:**
To increase protein family diversity, we will incorporate a curated subset of BindingDB focusing on kinase, protease, and GPCR families, adding approximately 15,000 additional binding measurements. Data quality filters will exclude entries with ambiguous measurements or conflicting values across sources.

**Protein Family Annotation:**
Each protein sequence will be annotated with Pfam family assignments using HMMER searches against Pfam 35.0. Proteins will be organized into a hierarchical structure reflecting Pfam clan relationships, enabling multi-level uncertainty sharing.

**Data Splits:**
- Training: 70% (stratified by protein family)
- Validation: 10% (for hyperparameter tuning)
- Test: 20% (held-out for final evaluation)
- Cross-family test: One complete protein family held out for transfer evaluation

### 2.2 Model Architecture

**Backbone: ESM-2 Protein Language Model**

We employ ESM-2 (650M parameters) as the protein encoder, extracting per-residue embeddings that capture evolutionary and structural information:

$$\mathbf{h}_{\text{protein}} = \text{MeanPool}(\text{ESM-2}(s_1, s_2, ..., s_L))$$

where $s_i$ represents amino acid tokens and $L$ is sequence length. The mean-pooled representation $\mathbf{h}_{\text{protein}} \in \mathbb{R}^{1280}$ serves as input to subsequent layers.

**Ligand Encoding:**

Small molecule ligands are encoded using a message-passing neural network (MPNN) operating on molecular graphs:

$$\mathbf{h}_{\text{ligand}} = \text{MPNN}(G_{\text{mol}})$$

where $G_{\text{mol}}$ represents the molecular graph with atom features and bond connectivity.

**Fusion Layer:**

Protein and ligand representations are combined through a bilinear attention mechanism:

$$\mathbf{h}_{\text{complex}} = \text{BilinearAttention}(\mathbf{h}_{\text{protein}}, \mathbf{h}_{\text{ligand}})$$

**Evidential Output Layer:**

The core innovation lies in the Normal-Inverse-Gamma (NIG) evidential output layer. Instead of predicting a single binding affinity value, the network outputs four parameters $(\gamma, \nu, \alpha, \beta)$ that parameterize a NIG distribution:

$$\text{NIG}(\mu, \sigma^2 | \gamma, \nu, \alpha, \beta) = \frac{\beta^\alpha \sqrt{\nu}}{\Gamma(\alpha)\sqrt{2\pi\sigma^2}} \left(\frac{1}{\sigma^2}\right)^{\alpha+1} \exp\left\{-\frac{2\beta + \nu(\gamma - \mu)^2}{2\sigma^2}\right\}$$

The predicted mean and uncertainties are derived as:

$$\hat{y} = \gamma \quad \text{(predicted binding affinity)}$$

$$\sigma^2_{\text{aleatoric}} = \frac{\beta}{\alpha - 1} \quad \text{(measurement noise)}$$

$$\sigma^2_{\text{epistemic}} = \frac{\beta}{\nu(\alpha - 1)} \quad \text{(model uncertainty)}$$

$$\sigma^2_{\text{total}} = \sigma^2_{\text{aleatoric}} + \sigma^2_{\text{epistemic}}$$

### 2.3 Hierarchical Pfam-Based Priors

To enable cross-family transfer, we introduce hierarchical priors on the evidential parameters. Let $f \in \mathcal{F}$ denote a protein family and $c(f)$ its parent clan. The prior structure is:

$$\beta_f \sim \text{Gamma}(\beta_{c(f)}, \tau_c)$$

$$\alpha_f \sim \text{Gamma}(\alpha_{c(f)}, \tau_c)$$

where clan-level parameters $(\alpha_c, \beta_c)$ are learned during training. This hierarchical structure allows uncertainty parameters to be shared across related protein families while permitting family-specific adjustments.

### 2.4 Training Procedure

**Loss Function:**

We employ the evidential regression loss combining negative log-likelihood with a regularization term:

$$\mathcal{L} = \mathcal{L}_{\text{NLL}} + \lambda \mathcal{L}_{\text{reg}}$$

The NLL component is:

$$\mathcal{L}_{\text{NLL}} = \frac{1}{2}\log\left(\frac{\pi}{\nu}\right) - \alpha\log(\Omega) + \left(\alpha + \frac{1}{2}\right)\log\left((y - \gamma)^2\nu + \Omega\right) + \log\left(\frac{\Gamma(\alpha)}{\Gamma(\alpha + \frac{1}{2})}\right)$$

where $\Omega = 2\beta(1 + \nu)$.

The regularization term penalizes evidence on incorrect predictions:

$$\mathcal{L}_{\text{reg}} = |y - \gamma| \cdot (2\nu + \alpha)$$

**Training Configuration:**
- Optimizer: AdamW with learning rate $1 \times 10^{-4}$
- Batch size: 32 complexes
- ESM-2 backbone: Frozen for first 10 epochs, then fine-tuned with learning rate $1 \times 10^{-5}$
- Training epochs: 100 with early stopping (patience=10)
- Regularization weight: $\lambda = 0.1$

### 2.5 Experimental Design and Evaluation

**Evaluation Metrics:**

1. **Expected Calibration Error (ECE):**

$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{N} |\text{acc}(B_b) - \text{conf}(B_b)|$$

where $B_b$ represents samples in confidence bin $b$, $\text{acc}(B_b)$ is the fraction of predictions within the confidence interval, and $\text{conf}(B_b)$ is the average predicted confidence. We use $B=10$ equal-width bins. Target: ECE < 0.15.

2. **Experimental Efficiency:**

$$\text{Efficiency} = \frac{N_{\text{random}} - N_{\text{uncertainty}}}{N_{\text{random}}} \times 100\%$$

where $N$ represents candidates needed to identify top-10% binders. Target: ≥40% reduction.

3. **Cross-Family Transfer Retention:**

$$\text{Retention} = \frac{\text{ECE}_{\text{in-family}}}{\text{ECE}_{\text{transfer}}} \times 100\%$$

Target: ≥80% retention.

4. **Prediction Accuracy:** Root Mean Square Error (RMSE) and Pearson correlation for binding affinity predictions.

**Baseline Comparisons:**

1. **Deep Ensemble (5 models):** Standard uncertainty quantification baseline using prediction variance across ensemble members.

2. **MC Dropout (50 forward passes):** Approximate Bayesian inference with dropout rate 0.1 at inference time.

3. **Temperature Scaling:** Post-hoc calibration applied to a standard regression model.

**Ablation Studies:**

1. **NIG Layer Ablation:** Replace evidential output with standard regression head to isolate uncertainty quantification contribution.

2. **Hierarchical Prior Ablation:** Compare flat priors (no family structure) vs. hierarchical Pfam-based priors.

3. **ESM-2 Ablation:** Replace with simpler protein encoders (CNN, LSTM) to assess backbone contribution.

**Statistical Analysis:**

- Bootstrap confidence intervals (1000 resamples) for all metrics
- Paired t-tests for baseline comparisons with Bonferroni correction
- Effect size reporting (Cohen's d) for practical significance

### 2.6 Mechanism Validation

To verify the causal mechanism, we conduct targeted experiments:

**Step 1 Validation (ESM-2 → Structural Representations):**
- Probe ESM-2 embeddings for structural information using linear probes for secondary structure and contact prediction
- Compare binding affinity prediction with and without ESM-2 features

**Step 2 Validation (NIG → Calibrated Uncertainty):**
- Verify uncertainty-error correlation: Spearman $\rho > 0.5$ between predicted uncertainty and absolute prediction error
- Confirm aleatoric/epistemic decomposition: epistemic uncertainty should decrease with more training data for a given protein family

**Step 3 Validation (Uncertainty → Prioritization):**
- Oracle curve analysis: plot cumulative hits vs. candidates examined under uncertainty ranking
- Compare to random selection and prediction-score ranking baselines

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome:** EPOEA will achieve calibrated uncertainty estimates with ECE < 0.15 on held-out experimental binding affinity data, representing a significant improvement over existing uncertainty quantification methods in the biomolecular domain.

**Secondary Outcomes:**

1. **Experimental Efficiency:** Uncertainty-guided candidate selection will reduce the number of experimental validations required by ≥40% while maintaining equivalent hit rates, directly translating to cost and time savings in drug discovery pipelines.

2. **Cross-Family Generalization:** Hierarchical Pfam-based priors will enable effective transfer to unseen protein families, retaining ≥80% of calibration performance and expanding the applicability of the model to understudied targets.

3. **Uncertainty Decomposition:** The model will provide interpretable decomposition of prediction uncertainty into aleatoric (measurement noise, expected ~0.5-1.0 kcal/mol for binding affinity) and epistemic (model knowledge gaps) components, enabling targeted data collection strategies.

### 3.2 Scientific Impact

This research advances the field of machine learning for biomolecular design in several ways:

1. **Methodological Contribution:** EPOEA represents the first application of evidential deep learning with hierarchical priors to continuous biomolecular property prediction, establishing a new paradigm for uncertainty-aware molecular oracles.

2. **Bridging Computation and Experiment:** By providing calibrated uncertainty estimates, EPOEA directly addresses the disconnect between computational predictions and experimental validation highlighted as a central challenge in the GEM workshop. Experimentalists can use uncertainty estimates to make informed decisions about resource allocation.

3. **Enabling Adaptive Experimental Design:** Calibrated epistemic uncertainty identifies regions of chemical and protein space where the model lacks knowledge, enabling intelligent selection of informative experiments that maximally improve model performance.

### 3.3 Practical Impact

1. **Drug Discovery:** Pharmaceutical companies can prioritize lead compounds for experimental validation based on prediction confidence, reducing the cost and time of hit-to-lead optimization campaigns.

2. **Protein Engineering:** Directed evolution experiments can be guided by uncertainty estimates, focusing experimental effort on mutations where computational predictions are most reliable.

3. **Resource Optimization:** The 40% reduction in validation candidates translates directly to reduced experimental costs, enabling smaller research groups to compete effectively in biomolecular design.

### 3.4 Limitations and Future Directions

We acknowledge several limitations that define future research directions:

1. **Data Dependency:** Calibration quality depends on training data diversity; expanding to additional protein families and property types will improve generalization.

2. **Computational Overhead:** The evidential output layer adds ~10-20% inference time compared to standard regression; optimization for high-throughput screening applications is warranted.

3. **Scope Boundaries:** The current framework focuses on binding affinity prediction; extension to kinetic properties, selectivity profiles, and multi-objective optimization represents important future work.

### 3.5 Conclusion

EPOEA addresses a critical gap in biomolecular design by providing calibrated uncertainty estimates that enable efficient experimental prioritization. By integrating evidential deep learning with protein language model embeddings and hierarchical protein family priors, we establish a principled framework for uncertainty-aware molecular property prediction. The expected outcomes—well-calibrated predictions, improved experimental efficiency, and cross-family transfer—directly serve the GEM workshop's mission of bridging generative ML and experimental biology, with immediate practical applications in drug discovery and protein engineering.