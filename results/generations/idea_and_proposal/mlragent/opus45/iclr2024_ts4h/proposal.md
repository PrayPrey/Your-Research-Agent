# Research Proposal: Self-Supervised Contrastive Learning for Irregular Health Time Series with Missingness-Aware Augmentations

## 1. Introduction

### Background

Time series data are foundational to modern healthcare, spanning electronic health records (EHRs), wearable devices, and medical monitoring systems such as ECG, EEG, and continuous glucose monitors. These temporal data streams hold immense potential for predicting clinical outcomes, detecting early warning signs, and personalizing patient care. However, translating this potential into practical clinical tools remains challenging due to the inherent complexities of health time series data.

Unlike time series in other domains, health data exhibit two pervasive and interrelated challenges: **irregular sampling** and **systematic missing values**. Vital signs in ICU settings are recorded at variable intervals depending on patient acuity; wearable devices capture data intermittently based on user behavior and device connectivity; laboratory values are measured only when clinically indicated. Critically, the pattern of missingness itself often carries clinical information—a patient with fewer vital sign measurements may be more stable, while increased monitoring frequency often signals clinical concern.

Self-supervised learning (SSL) has emerged as a powerful paradigm for learning representations from unlabeled data, with contrastive learning achieving remarkable success in computer vision and natural language processing. Recent works have begun applying SSL to time series data, but existing methods predominantly assume regular, complete observations. Standard augmentation strategies such as random cropping, scaling, and masking—designed for uniformly sampled data—can inadvertently destroy clinically meaningful patterns or generate physiologically implausible samples when applied to irregular health time series. For instance, randomly masking observations in an already sparse signal may eliminate critical clinical events, while time-warping without respecting actual measurement timestamps creates unrealistic temporal relationships.

### Research Objectives

This research proposes **MissAware-CL** (Missingness-Aware Contrastive Learning), a novel self-supervised framework specifically designed for irregular health time series with pervasive missing values. Our objectives are:

1. To develop **missingness-aware augmentation strategies** that preserve clinically informative observation patterns while generating semantically consistent positive pairs for contrastive learning.

2. To design an **irregularity-preserving encoder architecture** that jointly models continuous temporal dynamics and discrete missingness patterns as complementary information sources.

3. To formulate a **hierarchical contrastive objective** that captures both local (event-level) and global (patient-level) temporal patterns in health time series.

4. To empirically validate that representations learned by MissAware-CL improve downstream clinical prediction tasks, particularly in low-label regimes where labeled data is scarce.

### Significance

This research addresses a critical gap between the theoretical advances in self-supervised learning and the practical requirements of healthcare applications. By explicitly modeling the unique structure of irregular, incomplete health time series, MissAware-CL has the potential to: (1) improve predictive performance for clinical tasks such as mortality prediction and disease diagnosis; (2) reduce the dependence on expensive expert annotations; (3) enable more effective transfer learning across healthcare institutions with different data collection protocols; and (4) preserve clinically meaningful missingness information that existing methods inadvertently discard.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathbf{X} = \{(\mathbf{x}_i, \mathbf{t}_i, \mathbf{m}_i)\}_{i=1}^{N}$ denote a dataset of $N$ irregular health time series, where for patient $i$:
- $\mathbf{x}_i = \{x_{i,1}, x_{i,2}, ..., x_{i,L_i}\}$ represents observed values with variable length $L_i$
- $\mathbf{t}_i = \{t_{i,1}, t_{i,2}, ..., t_{i,L_i}\}$ denotes corresponding observation timestamps
- $\mathbf{m}_i \in \{0,1\}^{L_i \times D}$ is the observation mask indicating which of $D$ features are observed at each timestamp

Our goal is to learn an encoder $f_\theta: (\mathbf{x}, \mathbf{t}, \mathbf{m}) \rightarrow \mathbf{z} \in \mathbb{R}^d$ that maps irregular time series to fixed-dimensional representations $\mathbf{z}$ useful for downstream clinical tasks.

### 2.2 Missingness-Aware Augmentations

We propose four augmentation strategies specifically designed for irregular health time series:

**1. Timestamp-Respecting Time Warping (TRTW):** Rather than uniformly warping the time axis, we apply smooth deformations that respect the actual measurement times:

$$t'_j = t_j + \epsilon \cdot \sum_{k=1}^{K} a_k \sin\left(\frac{2\pi k t_j}{T}\right)$$

where $\epsilon$ controls warping magnitude, $a_k$ are random coefficients, and $T$ is the total time span. This preserves relative ordering and realistic inter-observation intervals.

**2. Clinically-Informed Channel Dropout (CICD):** Instead of random feature masking, we drop channels following realistic clinical missingness patterns learned from the data:

$$P(\text{drop channel } d) = \alpha \cdot \bar{m}_d + (1-\alpha) \cdot \text{Uniform}(0, p_{max})$$

where $\bar{m}_d$ is the empirical missingness rate for channel $d$, and $\alpha$ balances between realistic and uniform dropout.

**3. Observation-Preserving Cropping (OPC):** We crop time windows while ensuring a minimum number of observations are retained:

$$\text{crop}(\mathbf{x}, \mathbf{t}, \mathbf{m}) = \{(x_j, t_j, m_j) : t_j \in [t_s, t_e], |\{j: t_j \in [t_s, t_e]\}| \geq n_{min}\}$$

where $[t_s, t_e]$ is randomly selected to contain at least $n_{min}$ observations.

**4. Missingness Pattern Perturbation (MPP):** We slightly perturb observation masks to create variations while preserving overall missingness structure:

$$m'_{j,d} = m_{j,d} \cdot \text{Bernoulli}(1-p_{drop}) + (1-m_{j,d}) \cdot \text{Bernoulli}(p_{fill})$$

with small $p_{drop}$ and $p_{fill}$ to maintain pattern similarity.

### 2.3 Irregularity-Preserving Encoder Architecture

Our encoder consists of three components:

**1. Continuous-Time Dynamics Module:** We employ Neural Ordinary Differential Equations (Neural ODEs) to model the underlying continuous dynamics:

$$\frac{d\mathbf{h}(t)}{dt} = f_\phi(\mathbf{h}(t), t)$$

where $f_\phi$ is parameterized by a neural network. At each observation time $t_j$, we update the hidden state using a GRU-style update:

$$\mathbf{h}(t_j^+) = \text{GRU-Update}(\mathbf{h}(t_j^-), \mathbf{x}_j, \mathbf{m}_j)$$

**2. Missingness Embedding Module:** We explicitly encode observation patterns as informative signals:

$$\mathbf{e}_j^{miss} = \text{MLP}([\mathbf{m}_j; \Delta t_j; \text{cumsum}(\mathbf{m})_{<j}])$$

where $\Delta t_j = t_j - t_{j-1}$ captures inter-observation intervals and $\text{cumsum}(\mathbf{m})_{<j}$ encodes cumulative observation history.

**3. Fusion and Aggregation:** The final representation combines dynamics and missingness information:

$$\mathbf{z}_j = \text{LayerNorm}(\mathbf{h}(t_j) + \mathbf{W}_{fuse} \mathbf{e}_j^{miss})$$

Global representation is obtained via attention-weighted aggregation:

$$\mathbf{z} = \sum_{j=1}^{L} \alpha_j \mathbf{z}_j, \quad \alpha_j = \frac{\exp(\mathbf{w}^\top \mathbf{z}_j)}{\sum_k \exp(\mathbf{w}^\top \mathbf{z}_k)}$$

### 2.4 Hierarchical Contrastive Objective

We design a two-level contrastive loss to capture multi-scale temporal patterns:

**Local Contrastive Loss:** For each time series, we extract overlapping windows and contrast augmented pairs within local neighborhoods:

$$\mathcal{L}_{local} = -\frac{1}{W}\sum_{w=1}^{W} \log \frac{\exp(\text{sim}(\mathbf{z}_w, \mathbf{z}_w')/\tau)}{\sum_{k \neq w} \exp(\text{sim}(\mathbf{z}_w, \mathbf{z}_k)/\tau)}$$

where $\mathbf{z}_w$ and $\mathbf{z}_w'$ are representations of augmented window pairs, and $\tau$ is the temperature parameter.

**Global Contrastive Loss:** At the patient level, we contrast entire time series representations:

$$\mathcal{L}_{global} = -\frac{1}{B}\sum_{i=1}^{B} \log \frac{\exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_i')/\tau)}{\sum_{j=1}^{B} \mathbb{1}_{[j \neq i]} \exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_j)/\tau)}$$

The total loss combines both levels:

$$\mathcal{L}_{total} = \lambda_{local} \mathcal{L}_{local} + \lambda_{global} \mathcal{L}_{global}$$

### 2.5 Experimental Design

**Datasets:**
1. **MIMIC-IV**: ICU patient records with 17 vital signs and lab values, highly irregular with >60% missing values. Tasks: 48-hour mortality prediction, phenotype classification.
2. **PhysioNet 2012**: ICU time series benchmark for mortality prediction.
3. **GLOBEM** (wearable dataset): Multi-modal behavioral data from smartwatches for mental health assessment.

**Baselines:**
- Standard SSL: SimCLR, MoCo adapted for time series
- Time series SSL: TS2Vec, TNC, TS-TCC
- Irregular time series models: GRU-D, SeFT, mTAN
- Recent methods: BRITS, TANDEM, ImputeINR

**Evaluation Protocol:**
1. **Pre-training**: Train MissAware-CL on unlabeled time series
2. **Linear evaluation**: Freeze encoder, train linear classifier
3. **Fine-tuning**: End-to-end fine-tuning with varying label fractions (1%, 5%, 10%, 100%)
4. **Transfer learning**: Pre-train on MIMIC-IV, evaluate on PhysioNet 2012

**Evaluation Metrics:**
- Classification: AUROC, AUPRC, F1-score
- Calibration: Expected Calibration Error (ECE)
- Representation quality: t-SNE visualization, silhouette score

**Ablation Studies:**
- Individual contribution of each augmentation strategy
- Impact of missingness embedding module
- Local vs. global contrastive objectives
- Sensitivity to hyperparameters ($\tau$, $\lambda_{local}$, $\lambda_{global}$)

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Representation Quality**: We expect MissAware-CL to learn representations that better capture the underlying patient state by treating missingness as informative signal rather than noise. Quantitatively, we anticipate 3-5% improvement in AUROC for mortality prediction compared to state-of-the-art baselines.

2. **Superior Low-Label Performance**: The explicit modeling of irregular structure should yield representations that generalize better with limited labels. We expect particularly strong improvements (5-10% relative gain) in the 1-5% label regime, which is most relevant for real clinical settings.

3. **Transferability**: Representations learned on large datasets like MIMIC-IV should transfer effectively to smaller clinical cohorts, addressing the challenge of hospital-specific data scarcity.

4. **Interpretable Missingness Patterns**: The missingness embedding module will provide insights into how observation patterns contribute to predictions, enhancing clinical interpretability.

### Broader Impact

This research has significant implications for healthcare machine learning:

**Clinical Impact**: By improving prediction accuracy with limited labels, MissAware-CL can accelerate the development of clinical decision support tools for hospitals with insufficient resources for large-scale annotation efforts. The explicit modeling of missingness patterns also aligns with clinical intuition, potentially increasing clinician trust in model outputs.

**Methodological Contributions**: Our missingness-aware augmentation strategies and irregularity-preserving encoder architecture provide a principled foundation for self-supervised learning on irregular time series that extends beyond healthcare to other domains such as environmental monitoring and financial data.

**Equity Considerations**: By reducing dependence on labeled data, our approach may help address disparities in clinical AI development between well-resourced academic medical centers and community hospitals. The ability to transfer representations across institutions could democratize access to advanced predictive tools.

**Future Directions**: This work opens avenues for investigating foundation models for health time series, multi-modal integration with clinical notes and imaging, and federated learning approaches that leverage MissAware-CL's representations while preserving patient privacy.

In conclusion, MissAware-CL represents a significant step toward making self-supervised learning practical for the unique challenges of health time series data, with potential for substantial impact on clinical prediction and patient care.