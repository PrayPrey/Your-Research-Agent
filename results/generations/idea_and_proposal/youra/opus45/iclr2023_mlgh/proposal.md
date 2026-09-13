# Research Proposal: Socioeconomic Context Embeddings with Sister-Region Transfer Learning for Pandemic Prediction Under Data Scarcity

## 1. Introduction

### 1.1 Background

The COVID-19 pandemic exposed critical limitations in the application of machine learning to global health challenges. Despite decades of impressive advances in ML methodologies, the field's contributions during the pandemic were modest at best, particularly during the crucial early outbreak phases when accurate predictions were most needed for policy decisions. A fundamental challenge emerged: ML models require substantial historical data to make reliable predictions, yet at pandemic onset—precisely when forecasts are most valuable—local data is extremely scarce.

Traditional epidemiological models and ML approaches using raw socioeconomic features have struggled to address this data scarcity problem. While researchers have long recognized that socioeconomic factors—including income inequality, housing density, occupational exposure, and healthcare access—significantly influence disease transmission and outcomes, existing methods fail to capture transferable community vulnerability patterns that could enable knowledge sharing across regions.

A critical insight remains largely unexploited: socioeconomically similar regions often exhibit comparable disease dynamics, regardless of geographic proximity. Communities with similar demographic compositions, economic structures, and healthcare infrastructures tend to experience analogous pandemic trajectories. This observation suggests a promising avenue for addressing data scarcity through intelligent knowledge transfer.

### 1.2 Research Objectives

This research proposes to develop and validate **Socioeconomic Context Embeddings (SCE)** combined with **multi-criteria sister-region transfer learning** to enable accurate pandemic outcome predictions under data-sparse conditions. Our specific objectives are:

1. **Pre-train SCE representations** on census and American Community Survey (ACS) data using contrastive learning to encode community vulnerability profiles in a semantically meaningful embedding space.

2. **Develop a multi-criteria sister-region matching algorithm** that identifies analogous regions using SCE distance, geographic proximity, and healthcare infrastructure similarity.

3. **Design a cross-attention fusion architecture** that integrates transferred knowledge from data-rich sister regions with local clinical features for pandemic outcome prediction.

4. **Validate the approach** across diverse US counties, demonstrating both accuracy improvements and equitable performance across socioeconomic strata.

### 1.3 Research Significance

This research addresses the critical gap between ML capabilities and global health needs identified during COVID-19. By enabling knowledge transfer from data-rich to data-sparse regions during early pandemic stages, our approach has the potential to:

- **Improve early warning systems** for underserved communities that typically lack robust surveillance infrastructure
- **Reduce health inequities** by ensuring prediction accuracy is not contingent on historical data availability
- **Support evidence-based policy decisions** during the critical first weeks of outbreak response
- **Establish a reusable framework** for future pandemic preparedness

The work directly responds to workshop themes regarding lessons from COVID-19, leveraging ML for proactive pandemic response, and addressing health inequalities through improved data utilization practices.

## 2. Methodology

### 2.1 Data Collection and Preprocessing

#### 2.1.1 Socioeconomic Data Sources

We will collect comprehensive socioeconomic indicators from the following sources:

- **American Community Survey (ACS) 5-year estimates**: Demographics, income distribution, educational attainment, housing characteristics, employment sectors, health insurance coverage, and commuting patterns at census tract and county levels.
- **CDC Social Vulnerability Index (SVI)**: Composite vulnerability scores across four themes (socioeconomic status, household composition/disability, minority status/language, housing type/transportation).
- **Area Health Resources Files (AHRF)**: Healthcare infrastructure indicators including hospital beds per capita, physician density, and ICU capacity.
- **Bureau of Labor Statistics**: Monthly employment data by sector for temporal dynamics.

#### 2.1.2 Epidemiological Data Sources

- **Johns Hopkins University CSSE COVID-19 Dataset**: Daily confirmed cases and deaths at county level.
- **CDC COVID-19 Case Surveillance**: Hospitalization data with demographic breakdowns.
- **HHS Protect Public Data Hub**: Hospital utilization metrics.
- **COVID-19 Forecast Hub**: Ensemble model predictions for baseline comparison.

#### 2.1.3 Preprocessing Pipeline

All socioeconomic features will be standardized using z-score normalization. Missing values will be imputed using k-nearest neighbors imputation within geographic regions. Epidemiological time series will be smoothed using 7-day rolling averages to reduce reporting artifacts.

### 2.2 Socioeconomic Context Embedding (SCE) Pre-training

#### 2.2.1 Contrastive Learning Framework

We employ a contrastive learning approach to pre-train SCE representations that capture meaningful socioeconomic structure. Let $\mathbf{x}_i \in \mathbb{R}^d$ denote the raw socioeconomic feature vector for region $i$, where $d$ represents the number of socioeconomic indicators.

The encoder network $f_\theta: \mathbb{R}^d \rightarrow \mathbb{R}^m$ maps raw features to an $m$-dimensional embedding space (default $m=128$):

$$\mathbf{z}_i = f_\theta(\mathbf{x}_i)$$

#### 2.2.2 Positive and Negative Pair Construction

For contrastive learning, we construct positive pairs using two strategies:

1. **Augmentation-based positives**: Apply feature dropout and Gaussian noise to create augmented views $\tilde{\mathbf{x}}_i$ of the same region.
2. **Similarity-based positives**: Identify regions within the same SVI decile as soft positives.

Negative pairs are sampled from regions in different SVI quartiles, ensuring semantic dissimilarity.

#### 2.2.3 Contrastive Loss Function

We optimize the InfoNCE loss:

$$\mathcal{L}_{\text{SCE}} = -\log \frac{\exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_j^+) / \tau)}{\sum_{k=1}^{K} \exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_k) / \tau)}$$

where $\text{sim}(\cdot, \cdot)$ denotes cosine similarity, $\mathbf{z}_j^+$ is a positive pair embedding, $K$ is the number of negative samples, and $\tau$ is a temperature parameter (default $\tau=0.07$).

The encoder architecture consists of a 3-layer MLP with hidden dimensions [256, 256, 128], batch normalization, and ReLU activations.

### 2.3 Multi-Criteria Sister-Region Matching

#### 2.3.1 Similarity Metrics

For a target region $t$ and candidate region $c$, we compute three similarity components:

**Socioeconomic Similarity (SCE-based):**
$$S_{\text{socio}}(t, c) = \frac{\mathbf{z}_t \cdot \mathbf{z}_c}{\|\mathbf{z}_t\| \|\mathbf{z}_c\|}$$

**Geographic Proximity:**
$$S_{\text{geo}}(t, c) = \exp\left(-\frac{d_{\text{haversine}}(t, c)}{\sigma_{\text{geo}}}\right)$$

where $d_{\text{haversine}}$ is the great-circle distance and $\sigma_{\text{geo}}$ is a scaling parameter (default 500 km).

**Healthcare Infrastructure Similarity:**
$$S_{\text{health}}(t, c) = 1 - \frac{\|\mathbf{h}_t - \mathbf{h}_c\|}{\max_{i,j} \|\mathbf{h}_i - \mathbf{h}_j\|}$$

where $\mathbf{h}$ represents normalized healthcare capacity indicators.

#### 2.3.2 Composite Matching Score

The overall sister-region score combines these components:

$$S_{\text{sister}}(t, c) = \alpha S_{\text{socio}}(t, c) + \beta S_{\text{geo}}(t, c) + \gamma S_{\text{health}}(t, c)$$

where $\alpha + \beta + \gamma = 1$. Default weights are $\alpha=0.5$, $\beta=0.2$, $\gamma=0.3$, emphasizing socioeconomic similarity while incorporating geographic and healthcare factors.

For each target region, we select the top-$k$ sister regions (default $k=10$) based on $S_{\text{sister}}$.

### 2.4 Cross-Attention Fusion Architecture

#### 2.4.1 Feature Representations

For the target region $t$ at time $T$, we construct:

- **Local clinical features**: $\mathbf{c}_t^{(T)} \in \mathbb{R}^{p}$ containing 14-day lookback of case counts, test positivity, and hospitalization rates.
- **SCE embedding**: $\mathbf{z}_t \in \mathbb{R}^{m}$
- **Sister-region epidemic curves**: $\{\mathbf{e}_{s_1}, \ldots, \mathbf{e}_{s_k}\}$ where $\mathbf{e}_{s_i} \in \mathbb{R}^{q}$ represents the epidemic trajectory of sister region $s_i$.

#### 2.4.2 Cross-Attention Mechanism

We employ cross-attention to learn context-appropriate weighting of sister-region knowledge:

$$\mathbf{Q} = \mathbf{W}_Q [\mathbf{c}_t^{(T)}; \mathbf{z}_t]$$
$$\mathbf{K} = \mathbf{W}_K [\mathbf{e}_{s_1}; \ldots; \mathbf{e}_{s_k}]$$
$$\mathbf{V} = \mathbf{W}_V [\mathbf{e}_{s_1}; \ldots; \mathbf{e}_{s_k}]$$

$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_k}}\right)\mathbf{V}$$

where $[\cdot; \cdot]$ denotes concatenation and $\mathbf{W}_Q, \mathbf{W}_K, \mathbf{W}_V$ are learnable projection matrices.

#### 2.4.3 Prediction Head

The fused representation is passed through a prediction head:

$$\hat{y}_t^{(T+h)} = g_\phi\left(\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) \oplus \mathbf{z}_t \oplus \mathbf{c}_t^{(T)}\right)$$

where $g_\phi$ is a 2-layer MLP, $\oplus$ denotes concatenation, and $h \in \{7, 14, 21\}$ is the forecast horizon in days.

### 2.5 Experimental Design

#### 2.5.1 Dataset Construction

We construct evaluation datasets from 25+ US counties stratified by:
- Population size (small, medium, large)
- Income quintile (Q1-Q5)
- Geographic region (Northeast, Southeast, Midwest, Southwest, West)
- Urban/rural classification

#### 2.5.2 Data Scarcity Simulation

To simulate early-outbreak conditions, we restrict training data to the first $n$ days of local epidemic data, where $n \in \{7, 14, 21, 28\}$. Sister regions are assumed to have full epidemic curves available (simulating earlier outbreak onset).

#### 2.5.3 Baseline Models

1. **Clinical-only LSTM**: LSTM using only local epidemiological features
2. **Raw-feature baseline**: LSTM with concatenated raw socioeconomic features
3. **Geographic transfer**: Transfer from $k$-nearest geographic neighbors only
4. **Random transfer**: Transfer from randomly selected regions (ablation)
5. **COVID Forecast Hub ensemble**: State-of-the-art ensemble predictions

#### 2.5.4 Ablation Studies

- **SCE ablation**: Replace SCE with raw features in sister-region matching
- **Sister-region ablation**: Remove transfer component entirely
- **Attention ablation**: Replace cross-attention with simple concatenation
- **Component weighting**: Vary $\alpha, \beta, \gamma$ in matching score

### 2.6 Evaluation Metrics

#### 2.6.1 Primary Metrics

**Mean Absolute Percentage Error (MAPE):**
$$\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^{n} \left|\frac{y_i - \hat{y}_i}{y_i}\right|$$

**Root Mean Square Error (RMSE):**
$$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$

#### 2.6.2 Equity Metrics

**Subgroup Performance Gap:**
$$\Delta_{\text{equity}} = \max_{g \in \mathcal{G}} \text{MAPE}_g - \min_{g \in \mathcal{G}} \text{MAPE}_g$$

where $\mathcal{G}$ represents demographic subgroups (income quintiles, racial composition categories).

#### 2.6.3 Statistical Testing

- Paired t-tests comparing SCE-enhanced model against each baseline
- Significance level $\alpha = 0.05$ (one-tailed)
- Effect size reporting using Cohen's $d$
- 95% confidence intervals for all metrics

### 2.7 Success Criteria

**Primary (P1):** MAPE < 20% for 14-day case forecasts with $p < 0.05$ improvement over baselines

**Secondary (P2):** Sister-region transfer outperforms geographic-only transfer by >5% MAPE reduction

**Equity (P3):** Performance gap between income quintiles < 5% MAPE

**Falsification:** Hypothesis rejected if MAPE ≥ 25% or sister-region transfer performs equal to random transfer

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

We anticipate the following outcomes from this research:

1. **Pre-trained SCE models** that capture meaningful socioeconomic structure, with embeddings clustering communities by vulnerability profiles. Visualization and cluster analysis will demonstrate semantic coherence.

2. **Validated sister-region matching algorithm** showing that socioeconomic similarity predicts epidemic trajectory similarity beyond geographic proximity alone.

3. **Prediction accuracy improvements** of >15% relative MAPE reduction compared to raw-feature baselines, achieving target MAPE < 20% for 14-day forecasts under data-sparse conditions.

4. **Equitable performance** with <5% MAPE gap between highest and lowest income quintile counties, compared to typical 10-15% gaps in baseline models.

5. **Interpretable attention weights** revealing which sister regions and socioeconomic factors most influence predictions, supporting model transparency for policy applications.

### 3.2 Scientific Impact

This research contributes to multiple scientific domains:

- **Machine Learning**: Novel application of contrastive learning for socioeconomic representation learning; demonstration of cross-attention fusion for heterogeneous data integration in forecasting tasks.

- **Computational Epidemiology**: New paradigm for knowledge transfer in epidemic modeling; principled approach to incorporating social determinants of health into disease forecasting.

- **Health Equity Research**: Quantitative framework for measuring and reducing prediction disparities across socioeconomic groups.

### 3.3 Practical Impact

The practical implications extend to pandemic preparedness and response:

- **Early Warning Systems**: Enables accurate predictions for underserved communities lacking historical surveillance data, supporting proactive resource allocation.

- **Policy Decision Support**: Provides interpretable predictions with uncertainty quantification during critical early outbreak phases when intervention decisions have maximum impact.

- **Transferable Framework**: Methodology generalizes to other respiratory disease outbreaks and potentially other health outcomes with socioeconomic gradients.

### 3.4 Limitations and Future Directions

We acknowledge several limitations that define future research directions:

- **Geographic scope**: Initial validation focuses on US counties; adaptation to international contexts requires equivalent census infrastructure or alternative data sources.
- **Ecological inference**: Tract/county-level predictions do not imply individual-level outcomes; clinical applications require additional validation.
- **Temporal dynamics**: Census data latency may miss rapid demographic shifts; integration of real-time mobility and economic indicators represents a promising extension.

Future work will explore dynamic SCE updates using high-frequency economic indicators, extension to hospitalization and mortality outcomes, and adaptation to non-US healthcare systems with different data availability patterns.

### 3.5 Conclusion

This research directly addresses the workshop's central challenge: closing the gap between ML advances and global health practice. By enabling knowledge transfer from data-rich to data-sparse regions during early pandemic stages, we provide a concrete methodological contribution to pandemic preparedness. The emphasis on equitable performance across socioeconomic strata ensures that ML advances benefit all communities, not just those with robust data infrastructure. Success in this research would demonstrate that sophisticated ML methods can deliver policy-relevant impact in global health when designed with domain-specific challenges in mind.