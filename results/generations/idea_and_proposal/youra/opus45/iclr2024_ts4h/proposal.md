# Research Proposal: SENTINEL-ADAPT: An Immunology-Inspired Framework for Maintaining Healthcare ML Model Performance Under Distribution Shift

## 1. Introduction

### 1.1 Background

Time series data pervade modern healthcare systems, from continuous vital sign monitoring in intensive care units to wearable device streams tracking patient activity and physiological states. Machine learning models trained on such data hold immense promise for improving clinical decision-making, enabling early warning systems for patient deterioration, and personalizing treatment recommendations. However, a fundamental barrier prevents the widespread deployment of these models in real clinical environments: **distribution shift**.

Distribution shift occurs when the statistical properties of data encountered during deployment differ from those observed during training. In healthcare settings, such shifts are not exceptional events but routine occurrences. Patient populations evolve as demographics change; clinical protocols are updated based on new evidence; seasonal variations alter disease prevalence and presentation; and extraordinary events—such as the COVID-19 pandemic—can fundamentally transform the data landscape overnight. Studies have documented that deployed healthcare ML models can experience performance degradation exceeding 15-20% within months of deployment due to these shifts, rendering initially accurate models unreliable or even dangerous.

Current approaches to addressing distribution shift suffer from significant limitations. **Full model retraining** requires substantial computational resources, large amounts of newly labeled data, and extended validation cycles—often taking weeks to months. **Periodic retraining schedules** (e.g., quarterly updates) cannot respond to sudden shifts and may trigger unnecessary updates during stable periods. **Online learning methods** risk catastrophic forgetting, where adaptation to new distributions erases knowledge of previous patterns. These limitations create a critical gap between the controlled research environment where models are developed and the dynamic clinical environment where they must operate.

### 1.2 Research Objectives

This research proposes **SENTINEL-ADAPT**, an immunology-inspired framework designed to maintain healthcare ML model performance under distribution shift through continuous monitoring and adaptive response. Drawing inspiration from the immune system's surveillance and response mechanisms, SENTINEL-ADAPT integrates three complementary components:

1. **Sentinel-based drift detection** that continuously monitors model inputs to identify distribution shifts early, analogous to how sentinel cells patrol tissues for foreign antigens.

2. **Reptile-style meta-learning adaptation** that enables rapid model updates with minimal samples, mimicking the immune system's ability to mount targeted responses quickly.

3. **Experience replay with distribution-tagged exemplars** that preserves knowledge of previous distributions, similar to immunological memory that maintains protection against previously encountered threats.

The primary research objectives are:

- **Objective 1:** Develop and validate a drift detection mechanism capable of identifying distribution shifts in healthcare time series data with high sensitivity and specificity.

- **Objective 2:** Implement and evaluate a lightweight meta-learning adaptation strategy that achieves performance recovery with fewer than 100 labeled samples from the shifted distribution.

- **Objective 3:** Design an experience replay system that prevents catastrophic forgetting while enabling continuous adaptation.

- **Objective 4:** Demonstrate that the integrated SENTINEL-ADAPT framework maintains model AUROC within 5% of original performance under realistic distribution shift scenarios.

### 1.3 Significance

This research addresses a fundamental barrier to healthcare ML deployment identified by the workshop's call for papers: the challenge of maintaining model reliability over time in dynamic clinical environments. The significance of this work spans multiple dimensions:

**Clinical Impact:** Reliable ML models that maintain performance under distribution shift can provide consistent decision support to clinicians, reducing the risk of model-induced errors during periods of data drift.

**Operational Efficiency:** By enabling targeted adaptation rather than full retraining, SENTINEL-ADAPT can reduce the computational and human resources required for model maintenance by an estimated 10-100x.

**Research Advancement:** The framework introduces novel connections between immunological principles and continual learning, potentially inspiring new approaches to adaptive ML systems.

**Deployment Enablement:** By addressing a key barrier to real-world deployment, this research brings healthcare time series models closer to practical clinical use, advancing the workshop's central mission.

---

## 2. Methodology

### 2.1 Framework Architecture

SENTINEL-ADAPT operates through a four-step causal chain: **Sentinel Module → Shift Detection → Adaptation Trigger → Model Update → Performance Maintenance**. We detail each component below.

#### 2.1.1 Sentinel-Based Drift Detection

The Sentinel Module continuously monitors the distribution of incoming data by analyzing feature embeddings extracted from a frozen encoder layer of the base model. Let $\mathbf{z}_t = f_\theta(\mathbf{x}_t)$ denote the embedding of input $\mathbf{x}_t$ at time $t$, where $f_\theta$ is the encoder with parameters $\theta$.

We accumulate embeddings into batches $\mathcal{B}_k = \{\mathbf{z}_i\}_{i \in \text{batch } k}$ and compare each batch against a reference distribution $\mathcal{R}$ derived from the training data. Two complementary statistical tests are employed:

**Kolmogorov-Smirnov (KS) Test:** For each embedding dimension $d$, we compute:

$$D_d = \sup_z |F_{\mathcal{B}_k,d}(z) - F_{\mathcal{R},d}(z)|$$

where $F_{\mathcal{B}_k,d}$ and $F_{\mathcal{R},d}$ are the empirical cumulative distribution functions for dimension $d$. The aggregate statistic is $D_{KS} = \max_d D_d$.

**Maximum Mean Discrepancy (MMD):** We compute the kernel-based distance:

$$\text{MMD}^2(\mathcal{B}_k, \mathcal{R}) = \mathbb{E}[k(\mathbf{z}, \mathbf{z}')] - 2\mathbb{E}[k(\mathbf{z}, \mathbf{z}'')] + \mathbb{E}[k(\mathbf{z}'', \mathbf{z}''')]$$

where $\mathbf{z}, \mathbf{z}' \sim \mathcal{B}_k$, $\mathbf{z}'', \mathbf{z}''' \sim \mathcal{R}$, and $k(\cdot, \cdot)$ is a Gaussian RBF kernel with bandwidth selected via the median heuristic.

A shift is detected when either test yields $p < \alpha$ (configurable threshold, default $\alpha = 0.01$) for $n_{consecutive}$ consecutive batches (default $n_{consecutive} = 3$) to reduce false positives.

#### 2.1.2 Reptile-Style Meta-Learning Adaptation

Upon shift detection, the Adaptation Module updates model parameters using Reptile-style first-order meta-learning. Unlike standard fine-tuning, Reptile is designed to find parameter initializations that enable rapid adaptation to new tasks with minimal data.

Given a small set of labeled samples $\mathcal{D}_{shift} = \{(\mathbf{x}_i, y_i)\}_{i=1}^{N}$ from the shifted distribution (target: $N < 100$), we perform $K$ inner-loop gradient steps:

$$\theta'_k = \theta'_{k-1} - \alpha_{inner} \nabla_{\theta'_{k-1}} \mathcal{L}(\theta'_{k-1}; \mathcal{D}_{shift})$$

where $\theta'_0 = \theta$ (current model parameters), $\alpha_{inner}$ is the inner learning rate, and $\mathcal{L}$ is the task loss (binary cross-entropy for classification).

The outer update follows the Reptile rule:

$$\theta \leftarrow \theta + \alpha_{outer}(\theta'_K - \theta)$$

where $\alpha_{outer}$ is the outer learning rate (meta-step size). This update moves parameters toward configurations that perform well on the shifted distribution while maintaining proximity to the original parameters.

**Validation Gate:** Before committing updates, we evaluate performance on a held-out validation set from the shifted distribution. Updates are only applied if:

$$\text{AUROC}_{shifted}(\theta'_K) > \text{AUROC}_{shifted}(\theta) + \delta_{min}$$

where $\delta_{min} = 0.01$ is the minimum improvement threshold.

#### 2.1.3 Experience Replay with Distribution-Tagged Exemplars

To prevent catastrophic forgetting, we maintain an experience replay buffer $\mathcal{M}$ of size $|\mathcal{M}| = 10,000$ samples. Each exemplar is tagged with its source distribution identifier:

$$\mathcal{M} = \{(\mathbf{x}_i, y_i, d_i)\}_{i=1}^{|\mathcal{M}|}$$

where $d_i \in \{d_{original}, d_{shift_1}, d_{shift_2}, ...\}$ indicates the distribution from which the sample originated.

During adaptation, we augment the shifted distribution samples with replay samples:

$$\mathcal{D}_{combined} = \mathcal{D}_{shift} \cup \text{Sample}(\mathcal{M}, n_{replay})$$

where $\text{Sample}(\mathcal{M}, n_{replay})$ draws $n_{replay}$ samples from the buffer using stratified sampling to ensure representation from all tagged distributions.

**Buffer Update Strategy:** When new samples are added, we use reservoir sampling to maintain buffer size while preserving distribution diversity:

$$P(\text{include sample } i) = \min\left(1, \frac{|\mathcal{M}|}{n_{seen}}\right)$$

where $n_{seen}$ is the total number of samples observed.

### 2.2 Data Collection and Preprocessing

#### 2.2.1 Dataset

We utilize the **MIMIC-III** and **MIMIC-IV** databases, which contain de-identified health records from ICU patients at Beth Israel Deaconess Medical Center. These datasets provide:

- **Temporal coverage:** MIMIC-III (2001-2012) and MIMIC-IV (2008-2019), enabling natural temporal splits
- **Rich time series:** Vital signs (heart rate, blood pressure, respiratory rate, SpO2, temperature), laboratory values, and medication administrations
- **Clinical outcomes:** Mortality, length of stay, and readmission labels

#### 2.2.2 Distribution Shift Simulation

We create realistic distribution shift scenarios through temporal splits:

1. **Gradual Shift:** Training on 2008-2012 data, testing on sequential yearly cohorts (2013, 2014, ..., 2019)

2. **Sudden Shift:** Training on pre-2015 data, testing on post-2015 data (simulating protocol changes)

3. **Covariate Shift:** Stratifying by patient demographics (age groups, comorbidity profiles) to simulate population changes

4. **Concept Shift:** Using different outcome definitions (e.g., 24-hour vs. 48-hour mortality) to simulate label distribution changes

#### 2.2.3 Preprocessing Pipeline

Time series data are preprocessed following established protocols:

1. **Resampling:** Irregular measurements are resampled to hourly intervals using forward-fill interpolation
2. **Normalization:** Features are z-score normalized using training set statistics
3. **Missing value handling:** Missing values are imputed using last-observation-carried-forward with missingness indicators
4. **Sequence truncation:** Sequences are truncated/padded to 48-hour windows

### 2.3 Base Model Architecture

We employ a **STraTS-inspired architecture** (Self-supervised Transformer for Time Series) as the base model, consisting of:

- **Embedding layer:** Projects multivariate time series to $d_{model} = 256$ dimensional space
- **Temporal encoder:** 4-layer Transformer encoder with 8 attention heads
- **Classification head:** Two-layer MLP with dropout ($p = 0.3$)

The model is pre-trained using masked imputation on the training distribution before SENTINEL-ADAPT deployment.

### 2.4 Experimental Design

#### 2.4.1 Experimental Conditions

We evaluate five conditions:

1. **Static Baseline:** Model trained once, no updates during deployment
2. **Periodic Retraining:** Full retraining every 3 months on accumulated data
3. **Simple Online Learning:** Continuous gradient updates on incoming labeled data
4. **SENTINEL-ADAPT (Full):** Complete framework with all components
5. **SENTINEL-ADAPT (Ablations):** Variants with individual components removed

#### 2.4.2 Ablation Studies

To validate each component's contribution, we conduct ablations:

- **No Sentinel:** Random periodic adaptation instead of drift-triggered
- **No Meta-Learning:** Standard fine-tuning instead of Reptile
- **No Replay:** Adaptation without experience replay buffer
- **No Validation Gate:** Updates applied without performance verification

#### 2.4.3 Evaluation Metrics

**Primary Metrics:**

- **AUROC Retention:** $\frac{\text{AUROC}_{shifted}}{\text{AUROC}_{original}} \times 100\%$ (Target: $\geq 95\%$)

- **Adaptation Latency:** Hours from shift detection to performance recovery (Target: $\leq 24$ hours)

- **Forgetting Rate:** $\frac{\text{AUROC}_{original,after} - \text{AUROC}_{original,before}}{\text{AUROC}_{original,before}} \times 100\%$ (Target: $\leq 3\%$ degradation)

**Secondary Metrics:**

- **Drift Detection Accuracy:** Precision and recall of shift detection
- **Sample Efficiency:** Number of labeled samples required for adaptation
- **Computational Overhead:** Additional inference time and memory usage

#### 2.4.4 Statistical Analysis

All experiments are repeated across 5 random seeds. We report:

- Mean ± standard deviation for all metrics
- 95% confidence intervals
- Paired t-tests for condition comparisons ($\alpha = 0.05$)
- Cohen's d effect sizes
- Bonferroni correction for multiple comparisons

**Sample Size Justification:** With 5 seeds × 4 shift scenarios × 5 conditions = 100 experimental runs, we achieve statistical power $> 0.8$ for detecting medium effect sizes (Cohen's d $\geq 0.6$).

### 2.5 Implementation Details

- **Framework:** PyTorch 2.0 with PyTorch Lightning
- **Hardware:** NVIDIA A100 GPUs (40GB)
- **Hyperparameters:** 
  - Inner learning rate $\alpha_{inner} = 0.001$
  - Outer learning rate $\alpha_{outer} = 0.01$
  - Inner loop steps $K = 5$
  - Batch size for drift detection: 256 samples
  - Monitoring frequency: Hourly
  - Detection threshold $\alpha = 0.01$

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (P1):** We expect SENTINEL-ADAPT to maintain AUROC retention $\geq 95\%$ under distribution shift, compared to static baselines that degrade to $< 85\%$ retention. This represents a clinically meaningful improvement in model reliability.

**Secondary Outcomes:**

- **P2 (Adaptation Latency):** Performance recovery within 24 hours of shift detection, enabling next-day clinical relevance
- **P3 (Forgetting Prevention):** Original distribution performance maintained within 3% after adaptation, demonstrating effective memory preservation

**Ablation Insights:** We anticipate that:
- Removing drift detection will increase unnecessary adaptations by 3-5x
- Removing meta-learning will increase required samples by 5-10x
- Removing experience replay will increase forgetting rate to $> 10\%$

### 3.2 Scientific Contributions

1. **Novel Framework:** First integration of immunology-inspired surveillance with meta-learning for healthcare ML maintenance

2. **Validated Components:** Empirical evidence for the effectiveness of each framework component through rigorous ablation studies

3. **Practical Guidelines:** Recommendations for threshold selection, monitoring frequency, and buffer sizing based on experimental results

4. **Open-Source Implementation:** Publicly available code and pre-trained models to enable reproducibility and adoption

### 3.3 Broader Impact

**Clinical Translation:** By addressing distribution shift—a fundamental barrier to deployment—this research brings healthcare time series models closer to practical clinical use. The framework's design prioritizes interpretability and safety, with validation gates preventing harmful updates.

**Resource Efficiency:** Reducing the need for full retraining by 10-100x lowers the computational and human resources required for model maintenance, making ML deployment more accessible to resource-constrained healthcare settings.

**Research Directions:** The immunology-inspired approach opens new research avenues connecting biological principles with machine learning, potentially inspiring adaptive systems in other domains.

### 3.4 Limitations and Future Work

**Current Limitations:**
- Batched monitoring introduces minimum 1-hour detection latency
- Validation on MIMIC may not generalize to all healthcare settings
- Research scope precludes immediate regulatory-approved deployment

**Future Directions:**
- Extension to streaming data with reduced latency
- Multi-site validation across diverse healthcare systems
- Integration with federated learning for privacy-preserving adaptation
- Regulatory pathway exploration for clinical deployment

---

## 4. Conclusion

SENTINEL-ADAPT addresses a critical gap in healthcare ML deployment by providing a principled framework for maintaining model performance under distribution shift. Through the integration of drift detection, meta-learning adaptation, and experience replay, the framework enables continuous model reliability without the costs of full retraining. Rigorous experimental validation on MIMIC datasets will demonstrate the framework's effectiveness and provide actionable insights for the healthcare ML community. This research directly advances the workshop's mission of bringing time series health models closer to deployment, with potential for significant clinical and societal impact.