# Uncertainty-Quantified Representation Learning for Irregular Pediatric Clinical Time Series with Missing Data

## 1. Introduction

### Background

Time series data in healthcare represent a fundamental modality for understanding patient health trajectories, disease progression, and treatment responses. In pediatric care, these data streams are particularly critical as they capture the dynamic nature of growth, development, and response to interventions. However, pediatric time series present unique challenges that distinguish them from adult clinical data: smaller patient populations due to lower disease prevalence, ethical constraints on data collection from vulnerable populations, and highly irregular sampling patterns driven by clinical necessity rather than standardized protocols.

Current representation learning approaches for clinical time series have made significant advances, with methods like STraTS (Tipirneni & Reddy, 2021) and multi-view integration frameworks (Lee et al., 2021) demonstrating improved performance on irregular data. Recent work has also explored leveraging large language models for temporal reasoning (VITAL, 2025) and combining sequence and image representations (Chen et al., 2025). However, these methods typically produce point estimates of representations without adequately quantifying the uncertainty inherent in predictions made from sparse, irregular data. This limitation is particularly problematic in pediatric settings where the consequences of overconfident predictions can be severe and where clinicians require transparent uncertainty estimates to make informed decisions.

The challenge of uncertainty quantification becomes even more critical when dealing with minority pediatric populations—rare diseases, specific age groups, or underrepresented demographic cohorts—where data scarcity compounds the difficulty of learning reliable representations. Standard deep learning approaches often fail silently in these scenarios, producing seemingly confident predictions that may be unreliable extrapolations beyond the training distribution.

### Research Objectives

This research proposes a novel framework for **Confidence-Aware Representation Learning** specifically designed for irregular and sparse pediatric time series. Our primary objectives are:

1. **Develop a variational encoder architecture** that explicitly models temporal uncertainty, producing distributions over latent representations rather than deterministic embeddings, enabling principled uncertainty propagation through downstream tasks.

2. **Design an attention-based irregular sampling module** that adaptively weighs observations based on their informativeness, temporal context, and reliability, accounting for pediatric-specific measurement patterns.

3. **Create pediatric-specific data augmentation strategies** that simulate realistic missing data patterns based on actual clinical protocols, improving model robustness and enabling better uncertainty calibration.

4. **Implement interpretable uncertainty decomposition** mechanisms that separate aleatoric uncertainty (irreducible measurement noise) from epistemic uncertainty (model uncertainty due to limited data), providing clinicians with actionable insights about prediction reliability.

5. **Validate the framework** on multiple pediatric datasets representing different clinical scenarios, with particular emphasis on rare conditions and minority populations.

### Significance

This research addresses several critical gaps at the intersection of representation learning, uncertainty quantification, and pediatric healthcare:

**Clinical Impact**: By providing calibrated uncertainty estimates alongside predictions, our framework enables clinicians to identify when models are extrapolating beyond reliable training data, thereby preventing potentially harmful overconfident decisions in pediatric care.

**Methodological Contribution**: The proposed approach advances the state-of-the-art in time series representation learning by jointly optimizing for predictive performance and uncertainty calibration in the presence of irregular sampling and missing data.

**Equity and Fairness**: By explicitly addressing challenges in minority pediatric populations, this work contributes to more equitable AI systems in healthcare, ensuring that vulnerable populations are not systematically disadvantaged by data scarcity.

**Trustworthy AI**: The interpretable uncertainty decomposition mechanism aligns with the growing need for explainable and trustworthy AI in clinical decision support, addressing a key barrier to adoption identified in the workshop themes.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathcal{D} = \{(X_i, y_i)\}_{i=1}^N$ represent a pediatric time series dataset, where each patient $i$ has irregular observations $X_i = \{(t_{ij}, v_{ij}, m_{ij})\}_{j=1}^{T_i}$ with observation times $t_{ij}$, variable values $v_{ij} \in \mathbb{R}^d$, and missingness indicators $m_{ij} \in \{0,1\}^d$. The outcome $y_i$ represents the downstream task target (e.g., diagnosis, risk prediction).

Our goal is to learn a representation function $f_\theta: X_i \rightarrow \mathcal{Z}_i$ that maps irregular time series to a latent distribution $\mathcal{Z}_i$ from which we can: (1) sample representations for downstream tasks, and (2) quantify uncertainty in predictions arising from data irregularity and model limitations.

### 2.2 Variational Encoder Architecture

We propose a **Variational Irregular Time Series Encoder (VITSE)** that extends variational autoencoders to explicitly model temporal uncertainty:

$$q_\phi(z|X) = \mathcal{N}(z; \mu_\phi(X), \Sigma_\phi(X))$$

where $\mu_\phi$ and $\Sigma_\phi$ are parameterized by neural networks that process irregular time series. The architecture consists of three key components:

**1. Temporal Encoding Layer**: For each observation triplet $(t_{ij}, v_{ij}, m_{ij})$, we compute:

$$e_{ij} = \text{MLP}_{\text{temp}}([v_{ij} \odot m_{ij}; \sin(\omega t_{ij}); \cos(\omega t_{ij}); m_{ij}])$$

where $\odot$ denotes element-wise multiplication, and sinusoidal encodings capture temporal periodicity. The explicit inclusion of missingness indicators allows the model to distinguish between missing and observed values.

**2. Attention-Based Aggregation**: We employ a modified self-attention mechanism that accounts for irregular sampling:

$$\alpha_{ij} = \frac{\exp(s_{ij})}{\sum_{k=1}^{T_i} \exp(s_{ik})}$$

$$s_{ij} = \frac{(W_q e_{ij})^T (W_k e_{ij})}{\sqrt{d_k}} - \lambda \cdot \text{TD}(t_{ij})$$

where $\text{TD}(t_{ij})$ is a time-decay function that down-weights distant observations, and $\lambda$ controls the strength of temporal decay. The attended representation is:

$$h_i = \sum_{j=1}^{T_i} \alpha_{ij} (W_v e_{ij})$$

**3. Uncertainty-Aware Latent Space**: The attended representation is mapped to distributional parameters:

$$\mu_\phi(X_i) = \text{MLP}_\mu(h_i), \quad \log \sigma^2_\phi(X_i) = \text{MLP}_\sigma(h_i)$$

We use the log-variance parameterization to ensure positive definite covariance and apply a lower bound $\sigma_{\min}^2$ to prevent mode collapse.

### 2.3 Training Objective

The model is trained to maximize the evidence lower bound (ELBO):

$$\mathcal{L}(\theta, \phi) = \mathbb{E}_{q_\phi(z|X)}[\log p_\theta(y|z)] - \beta \cdot \text{KL}(q_\phi(z|X) \| p(z))$$

where $p(z) = \mathcal{N}(0, I)$ is the prior, and $\beta$ controls the regularization strength. We employ a $\beta$-VAE formulation to balance reconstruction quality and latent space regularization.

To encourage well-calibrated uncertainty estimates, we augment the loss with an uncertainty-aware term:

$$\mathcal{L}_{\text{total}} = \mathcal{L}(\theta, \phi) + \gamma \cdot \mathcal{L}_{\text{calib}}$$

where the calibration loss $\mathcal{L}_{\text{calib}}$ is computed using temperature scaling and reliability diagrams on a held-out calibration set.

### 2.4 Pediatric-Specific Data Augmentation

To improve robustness and uncertainty calibration, we develop augmentation strategies that simulate realistic missing patterns in pediatric data:

**1. Clinical Protocol-Based Masking**: We analyze real clinical protocols to identify typical measurement frequencies and apply masking that respects these patterns:

$$\mathbb{P}(\text{mask } v_{ij}) = f(\text{var}_j, \text{age}_i, \Delta t_{ij})$$

where the masking probability depends on the variable type, patient age, and time since last measurement.

**2. Temporal Jittering**: We add small perturbations to observation times to simulate scheduling variations:

$$t'_{ij} \sim \mathcal{N}(t_{ij}, \sigma_{\text{jitter}}^2)$$

**3. Mixup for Time Series**: We implement a time-aware mixup strategy:

$$\tilde{X} = \lambda X_i + (1-\lambda) X_j, \quad \tilde{y} = \lambda y_i + (1-\lambda) y_j$$

where $\lambda \sim \text{Beta}(\alpha, \alpha)$ and time series are aligned before mixing.

### 2.5 Uncertainty Decomposition

We decompose total predictive uncertainty into aleatoric and epistemic components:

**Aleatoric Uncertainty** (data uncertainty): Estimated from the variance of the predictive distribution for a single forward pass:

$$\mathcal{U}_{\text{aleatoric}} = \mathbb{E}_{z \sim q_\phi(z|X)}[\text{Var}[y|z]]$$

**Epistemic Uncertainty** (model uncertainty): Estimated via Monte Carlo dropout or ensemble methods:

$$\mathcal{U}_{\text{epistemic}} = \text{Var}_{z \sim q_\phi(z|X)}[\mathbb{E}[y|z]]$$

This decomposition is visualized for clinicians, highlighting regions where predictions are uncertain due to limited training data (epistemic) versus inherent measurement noise (aleatoric).

### 2.6 Experimental Design

**Datasets**: We evaluate on three pediatric datasets:
1. **MIMIC-IV Pediatric Subset**: ICU time series for critically ill children
2. **eICU-Pediatric**: Multi-center pediatric ICU data
3. **Synthetic Rare Disease Dataset**: Simulated data for rare pediatric conditions with controlled missingness patterns

**Baselines**: We compare against:
- Standard LSTM and GRU models with mean imputation
- STraTS (self-supervised transformer)
- GRU-D (handles missingness via decay)
- Multi-view integration learning
- Deterministic variational autoencoders without uncertainty quantification

**Evaluation Metrics**:

1. **Predictive Performance**: AUROC, AUPRC, accuracy for classification tasks; RMSE, MAE for regression
2. **Calibration**: Expected Calibration Error (ECE), Maximum Calibration Error (MCE), Brier score
3. **Uncertainty Quality**: Negative log-likelihood (NLL), continuous ranked probability score (CRPS)
4. **Reliability**: Selective prediction performance at various confidence thresholds
5. **Fairness**: Performance stratified by patient demographics and data availability

**Ablation Studies**: We conduct ablations to assess:
- Impact of variational formulation vs. deterministic encoding
- Effect of pediatric-specific augmentation strategies
- Contribution of attention-based irregular sampling module
- Sensitivity to hyperparameters ($\beta$, $\gamma$, $\lambda$)

**Clinical Validation**: We conduct a user study with pediatric clinicians to evaluate:
- Interpretability of uncertainty visualizations
- Trust calibration when presented with confidence intervals
- Decision-making changes when uncertainty information is available

### 2.7 Implementation Details

The model is implemented in PyTorch with the following specifications:
- Hidden dimension: 128
- Latent dimension: 64
- Number of attention heads: 4
- Learning rate: 1e-3 with cosine annealing
- Batch size: 32
- Training epochs: 100 with early stopping
- $\beta$ annealing schedule: linear from 0 to 1 over first 50 epochs
- Monte Carlo samples for uncertainty estimation: 30

All experiments are conducted with 5-fold cross-validation, and results are reported with 95% confidence intervals.

## 3. Expected Outcomes & Impact

### 3.1 Expected Technical Outcomes

**Superior Uncertainty Calibration**: We anticipate that our framework will achieve significantly better calibration than baseline methods, with ECE improvements of 20-30% on pediatric datasets. The explicit modeling of uncertainty through the variational formulation should produce well-calibrated confidence estimates that reliably indicate prediction reliability.

**Maintained or Improved Predictive Performance**: Despite the focus on uncertainty quantification, we expect comparable or better predictive performance (AUROC, AUPRC) compared to state-of-the-art deterministic methods. The regularization effects of the variational framework and enhanced data augmentation should improve generalization.

**Robust Performance on Sparse Data**: The attention-based irregular sampling module and pediatric-specific augmentation strategies should enable strong performance even with 40-60% missing data, outperforming imputation-based baselines by 10-15% in AUROC.

**Interpretable Uncertainty Decomposition**: The separation of aleatoric and epistemic uncertainty will provide clinically meaningful insights. We expect epistemic uncertainty to be highest for rare conditions and underrepresented patient subgroups, correctly identifying when the model is extrapolating beyond training data.

### 3.2 Clinical Impact

**Enhanced Decision Support**: By providing calibrated uncertainty estimates, our framework will enable clinicians to make more informed decisions, particularly in ambiguous cases. The ability to identify low-confidence predictions will reduce the risk of harmful overconfident recommendations in pediatric care.

**Improved Trust and Adoption**: The interpretable uncertainty visualizations and decomposition into aleatoric/epistemic components align with clinical reasoning patterns, potentially increasing trust and adoption of AI-assisted decision support systems in pediatric settings.

**Risk Stratification for Rare Conditions**: For rare pediatric diseases where data scarcity is most severe, the explicit modeling of epistemic uncertainty will help identify patients who require additional monitoring or specialist consultation, improving safety in resource-constrained settings.

**Reduced Annotation Burden**: The uncertainty-aware framework can guide active learning strategies, prioritizing data collection and labeling efforts for cases where the model is most uncertain, thereby reducing the annotation burden on time-constrained pediatric specialists.

### 3.3 Scientific Contributions

**Methodological Advancement**: This work will contribute a principled framework for joint representation learning and uncertainty quantification in irregular time series, with potential applications beyond healthcare to fields like environmental monitoring, finance, and IoT sensor networks.

**Benchmark and Evaluation Protocol**: The comprehensive evaluation framework, including uncertainty-specific metrics and clinical validation protocols, will establish best practices for assessing confidence-aware models in healthcare applications.

**Open-Source Tools**: We will release code, pre-trained models, and preprocessing pipelines to facilitate reproduction and extension of our work, contributing to the broader open-science initiative in medical AI.

### 3.4 Broader Impact on Healthcare Equity

**Addressing Minority Populations**: By explicitly modeling epistemic uncertainty, our framework will help identify when models have insufficient data about specific patient subgroups, enabling targeted data collection efforts and preventing systematic underperformance on minority populations.

**Pediatric-Specific Design**: The pediatric-focused augmentation strategies and evaluation on rare diseases will advance AI capabilities in an underserved clinical domain, potentially improving outcomes for vulnerable pediatric patients.

**Fairness Monitoring**: The uncertainty decomposition provides a mechanism for continuous fairness monitoring, as high epistemic uncertainty in specific demographic groups can signal potential bias or insufficient representation in training data.

### 3.5 Future Research Directions

This work will establish foundations for several promising research directions:

**Causal Uncertainty Quantification**: Extending the framework to quantify uncertainty in causal effect estimates from observational pediatric data, enabling more reliable treatment effect prediction for individualized medicine.

**Federated Learning with Uncertainty**: Adapting the uncertainty-aware framework for federated learning across multiple pediatric hospitals, enabling collaborative learning while preserving privacy and quantifying uncertainty arising from distribution shifts across institutions.

**Multi-Task Uncertainty**: Extending the architecture to jointly model multiple clinical tasks (diagnosis, prognosis, treatment response) while capturing task-specific and shared uncertainty components.

**Continual Learning**: Incorporating uncertainty-guided continual learning mechanisms that update models safely as new pediatric data becomes available, while detecting and adapting to distribution shifts.

In conclusion, this research proposal addresses critical challenges at the intersection of representation learning, uncertainty quantification, and pediatric healthcare. By developing methods that are not only accurate but also transparent about their limitations, we aim to create trustworthy AI systems that support—rather than replace—clinical expertise, ultimately improving care for vulnerable pediatric populations. The emphasis on minority populations, interpretability, and rigorous uncertainty quantification aligns directly with the workshop's call for actionable, robust approaches to time series representation learning in healthcare.