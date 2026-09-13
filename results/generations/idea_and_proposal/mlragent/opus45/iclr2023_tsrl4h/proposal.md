# Research Proposal

## Title
**UncertainCL: Contrastive Learning with Temporal Uncertainty Quantification for Irregular Clinical Time Series**

---

## 1. Introduction

### Background

Time series data form the backbone of modern healthcare monitoring and decision-making, from continuous vital sign recordings in Intensive Care Units (ICUs) to longitudinal patient tracking in chronic disease management. These temporal data streams hold immense potential for early diagnosis, disease progression prediction, and personalized treatment planning. However, clinical time series present unique challenges that significantly limit the applicability of conventional machine learning methods. Most notably, real-world clinical data are characterized by irregular sampling intervals—measurements taken at non-uniform time points based on clinical necessity rather than fixed schedules—and pervasive missing values arising from equipment failures, patient mobility, or resource constraints.

Current representation learning approaches for clinical time series typically address these challenges through two primary strategies: imputation-based methods that fill in missing values before learning representations, or architecture modifications that handle irregular inputs directly. However, both approaches share a critical limitation: they produce point estimates that fail to capture the inherent uncertainty arising from data quality issues. This limitation is particularly problematic in healthcare settings where clinicians require not only predictions but also reliable confidence estimates to inform high-stakes decisions.

The challenge is further amplified for minority patient groups—including pediatric populations, patients with rare diseases, and underrepresented demographics—where data sparsity is more severe. In these settings, learned representations may appear confident despite being derived from highly incomplete information, potentially leading to inappropriate clinical actions.

### Research Objectives

This research proposes **UncertainCL**, a novel contrastive representation learning framework that explicitly models and propagates temporal uncertainty arising from irregular sampling and missingness in clinical time series. Our specific objectives are:

1. To develop an uncertainty-aware temporal encoding mechanism that learns distributional representations rather than point embeddings, where variance explicitly captures uncertainty from missing observations and irregular sampling intervals.

2. To design a missingness-informed contrastive learning objective that prevents the model from learning spurious correlations based on data availability patterns rather than true clinical signals.

3. To establish a principled uncertainty propagation mechanism that provides calibrated confidence intervals for downstream clinical predictions.

4. To validate the framework's effectiveness on real-world clinical datasets, with particular emphasis on robustness for sparse patient subgroups and calibration of uncertainty estimates.

### Significance

This research addresses a fundamental gap in clinical time series analysis by unifying representation learning with principled uncertainty quantification. The proposed framework has the potential to transform clinical decision support systems by providing interpretable confidence estimates that help clinicians identify when predictions are unreliable due to data quality issues. This is particularly impactful for minority patient populations where current methods often fail silently due to data sparsity.

---

## 2. Methodology

### 2.1 Problem Formulation

Consider a clinical time series dataset $\mathcal{D} = \{(\mathbf{X}^{(i)}, \mathbf{T}^{(i)}, \mathbf{M}^{(i)})\}_{i=1}^{N}$, where for patient $i$:
- $\mathbf{X}^{(i)} = \{x_1, x_2, \ldots, x_{L_i}\}$ represents observed values across $D$ clinical variables
- $\mathbf{T}^{(i)} = \{t_1, t_2, \ldots, t_{L_i}\}$ denotes irregular observation timestamps
- $\mathbf{M}^{(i)} \in \{0,1\}^{L_i \times D}$ is the missingness mask indicating which variables are observed at each timestamp

Our goal is to learn a representation function $f_\theta$ that maps each time series to a distributional embedding $\mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$ in a latent space, where the variance $\boldsymbol{\Sigma}$ captures uncertainty arising from data quality issues.

### 2.2 Uncertainty-Aware Temporal Encoding

**Temporal Point Process Encoding.** To handle irregular sampling, we first encode observation times using a continuous-time representation. For each observation at time $t_j$, we compute a temporal encoding:

$$\mathbf{e}_{\text{time}}(t_j) = \left[\cos(\omega_1 t_j), \sin(\omega_1 t_j), \ldots, \cos(\omega_K t_j), \sin(\omega_K t_j)\right]$$

where $\{\omega_k\}_{k=1}^{K}$ are learnable frequency parameters.

**Missingness-Aware Input Embedding.** For each observation, we construct an augmented input that explicitly encodes missingness information:

$$\mathbf{h}_j = \text{MLP}\left([\mathbf{x}_j \odot \mathbf{m}_j; \mathbf{m}_j; \Delta t_j; \mathbf{e}_{\text{time}}(t_j)]\right)$$

where $\odot$ denotes element-wise multiplication, $\mathbf{m}_j$ is the missingness mask at time $t_j$, and $\Delta t_j = t_j - t_{j-1}$ captures the time gap since the last observation.

**Distributional Sequence Encoder.** We employ a modified Transformer architecture that outputs distributional representations. The encoder processes the sequence $\{\mathbf{h}_j\}_{j=1}^{L}$ through self-attention layers with a novel uncertainty-aware attention mechanism:

$$\alpha_{jk} = \frac{\exp\left(\frac{\mathbf{q}_j^\top \mathbf{k}_k}{\sqrt{d}} \cdot \gamma(\mathbf{m}_j, \mathbf{m}_k)\right)}{\sum_{l=1}^{L} \exp\left(\frac{\mathbf{q}_j^\top \mathbf{k}_l}{\sqrt{d}} \cdot \gamma(\mathbf{m}_j, \mathbf{m}_l)\right)}$$

where $\gamma(\mathbf{m}_j, \mathbf{m}_k) = \sigma\left(\mathbf{w}^\top [\mathbf{m}_j; \mathbf{m}_k]\right)$ is a learned gating function that modulates attention based on missingness patterns.

The final layer outputs both mean and variance:

$$\boldsymbol{\mu} = \mathbf{W}_\mu \cdot \text{Pool}(\mathbf{H}^{(L)}), \quad \log \boldsymbol{\sigma}^2 = \mathbf{W}_\sigma \cdot \text{Pool}(\mathbf{H}^{(L)})$$

where Pool(·) is an attention-weighted pooling operation and $\mathbf{H}^{(L)}$ represents the final layer hidden states.

### 2.3 Missingness-Informed Contrastive Learning

**Positive Pair Construction.** Traditional contrastive learning constructs positive pairs through data augmentation. However, in clinical time series with missingness, naive augmentation may create pairs with drastically different information content. We propose a missingness-aware positive pair construction strategy.

For an anchor sample with missingness pattern $\mathbf{M}^{(i)}$, we define the missingness similarity:

$$s_{\text{miss}}(i, j) = \frac{1}{D} \sum_{d=1}^{D} \frac{|\mathcal{T}_d^{(i)} \cap \mathcal{T}_d^{(j)}|}{|\mathcal{T}_d^{(i)} \cup \mathcal{T}_d^{(j)}|}$$

where $\mathcal{T}_d^{(i)}$ denotes the set of timestamps where variable $d$ is observed for patient $i$.

Positive pairs are constructed by: (1) temporal cropping with overlap constraints, and (2) selective masking that maintains similar missingness patterns. Specifically, for augmentation $\tilde{\mathbf{X}}$ of sample $\mathbf{X}$, we ensure $s_{\text{miss}}(\mathbf{X}, \tilde{\mathbf{X}}) > \tau_{\text{miss}}$.

**Distributional Contrastive Loss.** Given distributional embeddings, we employ a probabilistic contrastive objective. For anchor distribution $p_i = \mathcal{N}(\boldsymbol{\mu}_i, \boldsymbol{\Sigma}_i)$ and positive distribution $p_i^+ = \mathcal{N}(\boldsymbol{\mu}_i^+, \boldsymbol{\Sigma}_i^+)$, we define the similarity using expected likelihood:

$$\text{sim}(p_i, p_j) = -D_{\text{W}_2}(p_i, p_j) = -\left(\|\boldsymbol{\mu}_i - \boldsymbol{\mu}_j\|_2^2 + \|\boldsymbol{\Sigma}_i^{1/2} - \boldsymbol{\Sigma}_j^{1/2}\|_F^2\right)^{1/2}$$

where $D_{\text{W}_2}$ is the 2-Wasserstein distance.

The contrastive loss becomes:

$$\mathcal{L}_{\text{contrast}} = -\log \frac{\exp(\text{sim}(p_i, p_i^+) / \tau)}{\sum_{j=1}^{2N} \mathbb{1}_{[j \neq i]} \exp(\text{sim}(p_i, p_j) / \tau)}$$

**Uncertainty Regularization.** To prevent variance collapse, we include a regularization term:

$$\mathcal{L}_{\text{reg}} = \lambda_1 \cdot \max(0, \sigma_{\min} - \bar{\sigma}) + \lambda_2 \cdot D_{\text{KL}}(q(\boldsymbol{\sigma}) \| p(\boldsymbol{\sigma}))$$

where $p(\boldsymbol{\sigma})$ is a prior encouraging higher uncertainty for samples with more missingness.

The total training objective is:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{contrast}} + \mathcal{L}_{\text{reg}}$$

### 2.4 Uncertainty Propagation to Downstream Tasks

For downstream classification or regression tasks, we propagate uncertainty through a Bayesian prediction head. Given the distributional representation $\mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$, we perform Monte Carlo estimation:

$$\hat{y} = \frac{1}{S} \sum_{s=1}^{S} g_\phi(\mathbf{z}^{(s)}), \quad \mathbf{z}^{(s)} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$$

The predictive uncertainty is decomposed into:
- **Epistemic uncertainty**: $\text{Var}[g_\phi(\mathbf{z})]$ capturing model uncertainty
- **Aleatoric uncertainty**: derived from $\boldsymbol{\Sigma}$, capturing data quality uncertainty

### 2.5 Experimental Design

**Datasets:**
1. **MIMIC-IV**: Adult ICU data with 50+ clinical variables, ~70,000 patients
2. **eICU**: Multi-center ICU database for external validation
3. **Pediatric ICU Dataset**: Hospital-specific pediatric data (~5,000 patients) representing minority population

**Downstream Tasks:**
- In-hospital mortality prediction (binary classification)
- Length of stay prediction (regression)
- Sepsis onset prediction (early warning, time-sensitive)

**Baselines:**
- GRU-D: Decay-based imputation with GRU
- Transformer with time embeddings
- mTAN: Multi-time attention network
- CLOCS: Contrastive learning for clinical signals
- STraTS: Self-supervised pretraining for irregular time series

**Evaluation Metrics:**
1. **Predictive Performance**: AUROC, AUPRC, F1-score
2. **Uncertainty Calibration**: Expected Calibration Error (ECE), Brier Score
3. **Robustness Analysis**: Performance stratified by missingness rate (0-30%, 30-50%, >50%)
4. **Subgroup Performance**: Metrics computed separately for pediatric, rare disease, and minority demographic groups

**Ablation Studies:**
- Impact of uncertainty-aware attention vs. standard attention
- Effect of missingness-informed positive pair construction
- Contribution of distributional vs. point embeddings

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Robustness on Sparse Data**: We anticipate UncertainCL will demonstrate 5-10% improvement in AUROC on patient subgroups with >50% missing data compared to baselines, as the uncertainty-aware mechanism prevents overconfident predictions from incomplete information.

2. **Well-Calibrated Uncertainty Estimates**: The framework is expected to achieve ECE < 0.05, providing clinicians with reliable confidence intervals. Critically, we expect uncertainty estimates to correlate strongly with missingness rates, offering interpretable indicators of data quality.

3. **Equitable Performance Across Subgroups**: By explicitly modeling uncertainty, we expect reduced performance gaps between majority and minority patient populations (pediatric, rare diseases), addressing a key fairness concern in clinical ML.

4. **Transferable Representations**: Pre-trained representations should transfer effectively across institutions (MIMIC-IV → eICU), with uncertainty estimates helping identify out-of-distribution samples.

### Broader Impact

**Clinical Translation**: UncertainCL directly addresses a critical barrier to clinical adoption of ML systems—the lack of actionable confidence estimates. By flagging predictions where data quality is insufficient, the framework enables clinicians to make informed decisions about when to trust model outputs versus seeking additional information.

**Advancing Health Equity**: The explicit focus on minority patient populations addresses systematic biases in clinical ML, where models often perform worse for underrepresented groups due to data sparsity. Our uncertainty quantification provides transparency about when models may be unreliable for specific patient populations.

**Methodological Contributions**: The integration of contrastive learning with distributional representations and missingness-aware objectives provides a template for uncertainty-aware representation learning applicable beyond healthcare to other domains with irregular, incomplete data.

**Open Science**: We will release our code, pre-trained models, and detailed experimental protocols to facilitate reproducibility and extension by the research community, contributing to the broader goal of making time series representation learning research actionable in clinical practice.

---

This research represents a significant step toward trustworthy AI in healthcare by ensuring that representation learning systems honestly communicate their limitations, enabling more informed and ultimately safer clinical decision-making.