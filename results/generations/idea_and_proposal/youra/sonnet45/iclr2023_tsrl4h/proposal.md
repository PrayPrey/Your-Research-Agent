# Research Proposal: Fairness-Aware Contrastive Learning with Subgroup-Adaptive Augmentation for Healthcare Time Series

## 1. Title

**Fairness-Aware Contrastive Learning with Subgroup-Adaptive Augmentation for Healthcare Time Series: Addressing Performance Disparities Across Patient Demographics in Limited-Label Settings**

## 2. Introduction

### 2.1 Background

Healthcare time series data—ranging from continuous vital sign monitoring in intensive care units (ICUs) to long-term wearable sensor recordings—have become increasingly central to clinical decision-making. These data enable critical applications including disease diagnosis, progression prediction, patient stratification, and dynamic treatment optimization. However, the clinical deployment of machine learning (ML) models for time series analysis faces fundamental challenges that limit their real-world impact and threaten equitable healthcare delivery.

First, **labeling healthcare time series is exceptionally resource-intensive**. Long-term recordings spanning days or weeks require expert clinicians to annotate clinically relevant events, a process constrained by limited clinical time and expertise availability. Consequently, most healthcare time series data remain unlabeled, creating a critical bottleneck for supervised learning approaches. Second, **patient subgroup imbalances** pervade healthcare datasets. Minority populations—including pediatric patients, elderly individuals, and those with rare diseases—are systematically underrepresented in training data, leading to performance disparities that exacerbate existing healthcare inequities. Third, **missing values and measurement irregularities** are ubiquitous in real-world clinical settings due to sensor failures, patient movement, clinical procedures, and varying measurement protocols across institutions.

Self-supervised learning (SSL), particularly contrastive learning methods, has emerged as a promising paradigm to address the labeled data scarcity challenge. By learning representations from unlabeled data through pretext tasks, SSL methods can leverage vast amounts of unannotated time series to create meaningful embeddings for downstream clinical tasks. Recent healthcare-specific SSL frameworks such as COMET (hierarchical contrastive learning) and CARLA (masking-invariant contrastive learning) have demonstrated substantial improvements in label efficiency and missing data robustness.

However, **current SSL methods apply uniform augmentation strategies across all patient subgroups**, treating pediatric, adult, and elderly populations identically during representation learning. This one-size-fits-all approach ignores fundamental physiological differences: pediatric patients exhibit faster heart rates (80-180 bpm vs. 60-100 bpm in adults), shorter clinical episode durations, and distinct disease manifestation patterns; elderly patients experience higher sensor noise due to comorbidity burden and age-related physiological changes. Empirical evidence from recent studies reveals that uniform augmentation strategies produce **fairness gaps of 12-20% in model performance across age groups**, with minority populations like pediatric ICU patients suffering the most severe degradation.

### 2.2 Research Objectives

This research proposes **Fairness-Aware Contrastive Learning with Subgroup-Adaptive Augmentation (FACLSA)**, a novel SSL framework designed to simultaneously address three critical challenges in healthcare time series analysis: (1) limited labeled data availability, (2) fairness disparities across patient demographics, and (3) robustness to missing values. Our primary objectives are:

**Objective 1 (Fairness):** Reduce performance disparities across patient age subgroups (pediatric, adult, elderly) from current baselines of 12-20% fairness gaps to <5%, achieving at least 60% reduction in fairness gap while maintaining overall model performance (AUROC >0.80).

**Objective 2 (Robustness):** Achieve missing data robustness with AUROC >0.75 on test data containing 30-50% missing values, representing at least 15% relative improvement over uniform augmentation baselines (~0.65 AUROC).

**Objective 3 (Label Efficiency):** Demonstrate that physiologically-informed heuristic initialization enables effective subgroup-adaptive policy learning with only 100-200 labeled samples per subgroup (300-600 total), matching performance of fully-learned policies requiring 10× more labeled data.

**Objective 4 (Mechanism Validation):** Empirically validate the three-step causal mechanism: (1) subgroup-adaptive augmentation improves within-subgroup representation quality, (2) fairness-constrained optimization prevents majority group dominance during pretraining, and (3) fair pretraining transfers to downstream tasks with preserved fairness properties and missing data robustness.

### 2.3 Research Hypothesis

**Main Hypothesis (H-FACLSA-v1):** Under conditions of limited labeled healthcare time series data with patient subgroup imbalances (pediatric/adult/elderly), **if** subgroup-adaptive augmentation policies are applied in contrastive self-supervised learning combined with fairness-constrained optimization, **then** downstream task performance will achieve fairness gaps <5% across age groups while maintaining missing data robustness (AUROC >0.75 at 30-50% missing) **because** subgroup-specific augmentation respects physiological differences and fairness constraints prevent minority group performance degradation.

The proposed causal mechanism operates through three sequential steps:

1. **Physiologically-informed augmentation creates subgroup-appropriate representations**: Pediatric data receives lower masking rates (20% vs. 40% baseline) to preserve short-duration clinical patterns; elderly data receives elevated noise simulation (0.15 vs. 0.1 jitter amplitude) to build robustness to sensor artifacts common in this population.

2. **Fairness constraints prevent majority group dominance**: Explicit optimization constraints (maximum performance gap <5%) ensure that adult patients (typically the majority group) do not dominate learned representations, with group-level importance weighting ensuring minority groups contribute equally.

3. **Fair pretraining transfers to downstream tasks**: Representations learned with fairness constraints maintain fairness properties during transfer learning, while missing-pattern-specific augmentation creates masking-invariant representations robust to real-world data quality issues.

### 2.4 Significance

This research addresses critical gaps at the intersection of fairness, robustness, and label efficiency in healthcare ML—three themes explicitly prioritized by the Workshop on Time Series Representation Learning for Health. The significance spans multiple dimensions:

**Clinical Impact:** By reducing fairness gaps to <5%, FACLSA enables equitable clinical deployment of ML models across diverse patient populations, directly addressing healthcare disparities that disproportionately affect minority groups. Pediatric ICU patients, who currently experience 15-20% performance degradation compared to adult patients, would receive comparable quality of ML-assisted clinical decision support.

**Methodological Contribution:** FACLSA introduces the first SSL framework that jointly optimizes for fairness and robustness through subgroup-adaptive augmentation, advancing beyond uniform augmentation strategies that dominate current SSL literature. The physiologically-informed heuristic initialization approach demonstrates how domain knowledge can reduce labeled data requirements by 10×, offering a practical pathway for clinical deployment.

**Actionable for Minority Populations:** The workshop explicitly encourages research targeting minority data groups (pediatrics, critical care, rare diseases). FACLSA directly addresses this priority by designing augmentation policies tailored to underrepresented populations, with immediate applicability to pediatric ICU, geriatric care, and rare disease contexts where data scarcity and fairness concerns are most acute.

**Broader Implications:** Beyond healthcare, the subgroup-adaptive augmentation paradigm generalizes to any domain with demographic imbalances and physiological/behavioral heterogeneity—including mental health monitoring, rehabilitation tracking, and personalized medicine applications. The fairness-constrained optimization framework provides a template for incorporating equity considerations into SSL methods across diverse application areas.

## 3. Methodology

### 3.1 Research Design Overview

This research employs a **controlled experimental design** with stratified cross-validation to rigorously test the FACLSA hypothesis against established baselines. The methodology comprises four integrated components: (1) subgroup-adaptive augmentation policy design, (2) fairness-constrained contrastive learning optimization, (3) downstream task evaluation with missing data simulation, and (4) mechanistic validation through ablation studies.

### 3.2 Data Collection and Preprocessing

**Dataset:** We will utilize the MIMIC-III (Medical Information Mart for Intensive Care) and MIMIC-IV databases, which contain de-identified health records from 46,520 and 73,181 ICU patients respectively. These datasets provide multivariate time series including vital signs (heart rate, blood pressure, respiratory rate, oxygen saturation), laboratory measurements, and clinical interventions, with temporal resolution ranging from 1-minute to hourly measurements.

**Subgroup Definition:** Patients will be stratified into three age-based subgroups following clinical conventions:
- **Pediatric:** Age <18 years
- **Adult:** Age 18-65 years  
- **Elderly:** Age >65 years

**Inclusion Criteria:**
- ICU stay duration ≥24 hours (to ensure sufficient time series length)
- At least 4 vital sign measurements available (heart rate, blood pressure, respiratory rate, SpO2)
- Age metadata available for subgroup assignment
- Minimum 500 patients per subgroup in test set for statistical power

**Preprocessing Pipeline:**
1. **Time series extraction:** Extract 24-hour windows preceding clinical events (mortality, sepsis onset, acute kidney injury) for downstream tasks
2. **Normalization:** Apply z-score normalization per vital sign channel using training set statistics
3. **Resampling:** Standardize temporal resolution to 5-minute intervals using forward-fill imputation for irregular measurements
4. **Train/validation/test split:** 70%/10%/20% stratified by subgroup and outcome label to ensure balanced representation
5. **Missing data documentation:** Record original missing data patterns for realistic simulation in robustness evaluation

**Sample Size Justification:** With minimum 500 patients per subgroup in the test set (1,500 total) and 5-fold cross-validation with 5 runs per fold (25 total runs), we achieve statistical power >0.8 for detecting medium effect sizes (Cohen's d = 0.5) at α = 0.05 significance level.

### 3.3 Subgroup-Adaptive Augmentation Policy Design

**3.3.1 Augmentation Operations**

We define three core augmentation operations for time series, following established SSL literature:

**Masking ($\mathcal{A}_{\text{mask}}$):** Randomly mask contiguous segments of time series with probability $p_{\text{mask}}$:

$$\mathbf{x}'_{\text{mask}}(t) = \begin{cases} 
\mathbf{x}(t) & \text{if } t \notin \mathcal{M} \\
\mathbf{0} & \text{if } t \in \mathcal{M}
\end{cases}$$

where $\mathcal{M}$ represents masked time indices sampled from a Bernoulli distribution with parameter $p_{\text{mask}}$.

**Jittering ($\mathcal{A}_{\text{jitter}}$):** Add Gaussian noise with amplitude $\sigma_{\text{jitter}}$:

$$\mathbf{x}'_{\text{jitter}}(t) = \mathbf{x}(t) + \epsilon(t), \quad \epsilon(t) \sim \mathcal{N}(0, \sigma_{\text{jitter}}^2 \mathbf{I})$$

**Scaling ($\mathcal{A}_{\text{scale}}$):** Apply random amplitude scaling with factor $\alpha \sim \mathcal{U}(1-s, 1+s)$:

$$\mathbf{x}'_{\text{scale}}(t) = \alpha \cdot \mathbf{x}(t)$$

**3.3.2 Subgroup-Specific Augmentation Policies**

Based on physiological characteristics documented in medical literature, we define three subgroup-specific augmentation policies $\pi_{\text{pediatric}}$, $\pi_{\text{adult}}$, $\pi_{\text{elderly}}$:

**Pediatric Policy ($\pi_{\text{pediatric}}$):**
- $p_{\text{mask}} = 0.20$ (lower masking to preserve short-duration patterns)
- $\sigma_{\text{jitter}} = 0.05$ (lower noise to maintain fast transient features)
- $s = 0.10$ (moderate scaling)
- **Rationale:** Pediatric vital signs exhibit faster dynamics (heart rate 80-180 bpm) and shorter clinical episodes; aggressive masking would destroy critical short-duration patterns.

**Adult Policy ($\pi_{\text{adult}}$):**
- $p_{\text{mask}} = 0.40$ (baseline masking rate)
- $\sigma_{\text{jitter}} = 0.10$ (baseline noise)
- $s = 0.15$ (baseline scaling)
- **Rationale:** Adult population serves as reference group with standard augmentation intensity.

**Elderly Policy ($\pi_{\text{elderly}}$):**
- $p_{\text{mask}} = 0.35$ (moderate masking)
- $\sigma_{\text{jitter}} = 0.15$ (elevated noise to simulate sensor artifacts)
- $s = 0.20$ (higher scaling to account for physiological variability)
- **Rationale:** Elderly patients experience higher sensor noise due to comorbidities and age-related changes; elevated noise augmentation builds robustness to real-world data quality issues.

**3.3.3 Policy Refinement with Limited Labels**

While initial policies are heuristically defined from medical literature, we refine them using a small labeled validation set (100-200 samples per subgroup):

$$\pi^*_g = \arg\max_{\pi_g} \mathbb{E}_{(\mathbf{x}, y) \sim \mathcal{D}_{\text{val}}^g} \left[ \mathcal{L}_{\text{downstream}}(f_\theta(\mathcal{A}_{\pi_g}(\mathbf{x})), y) \right]$$

where $g \in \{\text{pediatric, adult, elderly}\}$, $f_\theta$ is the pretrained encoder, and $\mathcal{L}_{\text{downstream}}$ is the downstream task loss (e.g., binary cross-entropy for mortality prediction).

We employ grid search over parameter ranges:
- $p_{\text{mask}} \in \{0.15, 0.20, 0.25\}$ (pediatric), $\{0.35, 0.40, 0.45\}$ (adult), $\{0.30, 0.35, 0.40\}$ (elderly)
- $\sigma_{\text{jitter}} \in \{0.03, 0.05, 0.07\}$ (pediatric), $\{0.08, 0.10, 0.12\}$ (adult), $\{0.13, 0.15, 0.17\}$ (elderly)

This limited search space (27 configurations per subgroup) is computationally feasible with 100-200 labeled samples.

### 3.4 Fairness-Constrained Contrastive Learning

**3.4.1 Base Contrastive Learning Framework**

We build upon the COMET (Contrastive Learning for Multivariate Time Series) framework, which employs hierarchical contrastive learning with instance-level and temporal-level objectives. For a batch of $N$ time series samples $\{\mathbf{x}_i\}_{i=1}^N$ with subgroup labels $\{g_i\}_{i=1}^N$, we generate two augmented views for each sample:

$$\tilde{\mathbf{x}}_i^{(1)} = \mathcal{A}_{\pi_{g_i}}(\mathbf{x}_i), \quad \tilde{\mathbf{x}}_i^{(2)} = \mathcal{A}_{\pi_{g_i}}(\mathbf{x}_i)$$

where $\mathcal{A}_{\pi_{g_i}}$ applies the subgroup-specific augmentation policy.

The encoder network $f_\theta: \mathbb{R}^{T \times D} \rightarrow \mathbb{R}^d$ (where $T$ is time series length, $D$ is number of channels, $d$ is embedding dimension) maps augmented views to representations:

$$\mathbf{z}_i^{(1)} = f_\theta(\tilde{\mathbf{x}}_i^{(1)}), \quad \mathbf{z}_i^{(2)} = f_\theta(\tilde{\mathbf{x}}_i^{(2)})$$

The standard contrastive loss (InfoNCE) maximizes agreement between positive pairs while minimizing agreement with negative pairs:

$$\mathcal{L}_{\text{contrast}} = -\frac{1}{2N} \sum_{i=1}^N \left[ \log \frac{\exp(\text{sim}(\mathbf{z}_i^{(1)}, \mathbf{z}_i^{(2)})/\tau)}{\sum_{k=1}^{2N} \mathbb{1}_{k \neq i} \exp(\text{sim}(\mathbf{z}_i^{(1)}, \mathbf{z}_k)/\tau)} + \log \frac{\exp(\text{sim}(\mathbf{z}_i^{(2)}, \mathbf{z}_i^{(1)})/\tau)}{\sum_{k=1}^{2N} \mathbb{1}_{k \neq i} \exp(\text{sim}(\mathbf{z}_i^{(2)}, \mathbf{z}_k)/\tau)} \right]$$

where $\text{sim}(\mathbf{u}, \mathbf{v}) = \mathbf{u}^\top \mathbf{v} / (\|\mathbf{u}\| \|\mathbf{v}\|)$ is cosine similarity and $\tau$ is temperature parameter.

**3.4.2 Fairness Constraint Formulation**

To prevent majority group dominance, we introduce a fairness constraint that bounds the maximum performance gap across subgroups during pretraining. We define subgroup-specific performance on a small labeled validation set:

$$\text{Perf}_g = \mathbb{E}_{(\mathbf{x}, y) \sim \mathcal{D}_{\text{val}}^g} \left[ \mathbb{1}[\hat{y}(\mathbf{x}) = y] \right]$$

where $\hat{y}(\mathbf{x}) = h_\phi(f_\theta(\mathbf{x}))$ is the prediction from a linear probe $h_\phi$ trained on top of frozen encoder $f_\theta$.

The fairness constraint requires:

$$\max_{g, g'} |\text{Perf}_g - \text{Perf}_{g'}| \leq \epsilon$$

where $\epsilon = 0.05$ (5% maximum gap) is the fairness tolerance parameter.

**3.4.3 Group-Weighted Contrastive Loss**

To operationalize the fairness constraint during optimization, we employ group-level importance weighting. Let $w_g$ denote the weight for subgroup $g$, computed to balance representation quality across groups:

$$w_g = \frac{1}{|\mathcal{D}_{\text{train}}^g|} \cdot \frac{\sum_{g'} |\mathcal{D}_{\text{train}}^{g'}|}{|\mathcal{G}|}$$

where $|\mathcal{D}_{\text{train}}^g|$ is the number of training samples in subgroup $g$ and $|\mathcal{G}| = 3$ is the number of subgroups.

The fairness-aware contrastive loss becomes:

$$\mathcal{L}_{\text{fair-contrast}} = \sum_{g \in \mathcal{G}} w_g \cdot \mathcal{L}_{\text{contrast}}^g$$

where $\mathcal{L}_{\text{contrast}}^g$ is the contrastive loss computed only over samples from subgroup $g$.

**3.4.4 Constrained Optimization Algorithm**

We employ a two-stage optimization procedure:

**Stage 1 (Pretraining):** Optimize encoder $f_\theta$ using fairness-aware contrastive loss:

$$\theta^* = \arg\min_\theta \mathcal{L}_{\text{fair-contrast}}(\theta)$$

using Adam optimizer with learning rate $\eta = 10^{-4}$, batch size 256, for 200 epochs.

**Stage 2 (Fairness Validation):** Every 10 epochs, evaluate fairness gap on validation set:

$$\Delta_{\text{fair}} = \max_{g, g'} |\text{Perf}_g - \text{Perf}_{g'}|$$

If $\Delta_{\text{fair}} > \epsilon$, adjust group weights:

$$w_g \leftarrow w_g \cdot \exp\left(-\beta \cdot (\text{Perf}_g - \bar{\text{Perf}})\right)$$

where $\bar{\text{Perf}} = \frac{1}{|\mathcal{G}|} \sum_g \text{Perf}_g$ is mean performance and $\beta = 0.1$ is adaptation rate.

This adaptive weighting scheme dynamically upweights underperforming subgroups during training, enforcing the fairness constraint.

### 3.5 Downstream Task Evaluation

**3.5.1 Clinical Prediction Tasks**

We evaluate FACLSA on three clinically relevant binary classification tasks:

1. **In-hospital mortality prediction:** Predict death within ICU stay using first 24 hours of data
2. **Sepsis onset prediction:** Predict sepsis development within next 6 hours
3. **Acute kidney injury (AKI) prediction:** Predict AKI onset within next 12 hours

For each task, we train a linear classifier $h_\phi: \mathbb{R}^d \rightarrow [0,1]$ on top of frozen pretrained encoder $f_\theta$:

$$\phi^* = \arg\min_\phi \mathbb{E}_{(\mathbf{x}, y) \sim \mathcal{D}_{\text{train}}} \left[ \text{BCE}(h_\phi(f_\theta(\mathbf{x})), y) \right]$$

where $\text{BCE}$ is binary cross-entropy loss.

**3.5.2 Missing Data Robustness Evaluation**

To evaluate robustness to missing values, we synthetically introduce realistic missing patterns into the test set:

**Pediatric Missing Pattern (Burst Missing):** Simulate missing data during clinical procedures by removing contiguous 30-minute segments with probability 0.3:

$$\mathbf{x}_{\text{test}}^{\text{ped}}(t) = \begin{cases}
\mathbf{x}(t) & \text{if } t \notin \bigcup_{j} [t_j, t_j + 30\text{min}] \\
\text{NaN} & \text{otherwise}
\end{cases}$$

**Elderly Missing Pattern (Gradual Degradation):** Simulate sensor failures by progressively increasing missing rate from 10% to 50% over the 24-hour window:

$$p_{\text{miss}}(t) = 0.1 + 0.4 \cdot \frac{t}{T}$$

**Adult Missing Pattern (Random Missing):** Uniform random missing with 40% probability per time point.

We measure AUROC on test data with 30%, 40%, and 50% overall missing rates, using mean imputation as baseline handling strategy.

**3.5.3 Evaluation Metrics**

**Primary Metrics:**

1. **Fairness Gap:** 
$$\Delta_{\text{fair}} = \max_{g \in \mathcal{G}} \text{AUROC}_g - \min_{g \in \mathcal{G}} \text{AUROC}_g$$

2. **Missing Data Robustness:** 
$$\text{AUROC}_{\text{missing}} = \text{AUROC}(\mathcal{D}_{\text{test}}^{30-50\% \text{ missing}})$$

**Secondary Metrics:**

3. **Overall Performance:** Mean AUROC across all subgroups
4. **Label Efficiency:** AUROC achieved with 100-200 labeled samples per subgroup
5. **Worst-Group Performance:** $\min_{g \in \mathcal{G}} \text{AUROC}_g$ (ensures no subgroup left behind)

### 3.6 Experimental Design and Validation Protocol

**3.6.1 Baseline Comparisons**

We compare FACLSA against three baselines:

1. **COMET (Uniform Augmentation):** Original COMET framework with uniform augmentation ($p_{\text{mask}} = 0.40$, $\sigma_{\text{jitter}} = 0.10$ for all subgroups), no fairness constraint
2. **CARLA (Masking-Invariant):** Contrastive learning with masking-invariant objective for missing data robustness
3. **Supervised Baseline:** Fully supervised training with available labeled data (no SSL pretraining)

**3.6.2 Cross-Validation Protocol**

We employ **stratified 5-fold cross-validation** to ensure robust evaluation:

1. Partition data into 5 folds, stratified by subgroup and outcome label
2. For each fold $k \in \{1, 2, 3, 4, 5\}$:
   - Train on folds $\{1, ..., 5\} \setminus \{k\}$
   - Validate on fold $k$
   - Repeat with 5 different random seeds: $\{42, 123, 456, 789, 1011\}$
3. Total runs: $5 \text{ folds} \times 5 \text{ seeds} = 25$ runs

**3.6.3 Statistical Testing**

**Primary Hypothesis Test (Fairness Gap Reduction):**

Paired t-test comparing FACLSA vs. COMET baseline fairness gaps across 25 runs:

$$H_0: \mu_{\Delta_{\text{FACLSA}}} \geq \mu_{\Delta_{\text{COMET}}} \quad \text{vs.} \quad H_1: \mu_{\Delta_{\text{FACLSA}}} < \mu_{\Delta_{\text{COMET}}}$$

Significance level: $\alpha = 0.05$ (one-tailed)

Effect size: Cohen's d = $\frac{\bar{\Delta}_{\text{COMET}} - \bar{\Delta}_{\text{FACLSA}}}{s_{\text{pooled}}}$, target $d > 0.5$ (medium effect)

**Secondary Hypothesis Tests (Robustness, Label Efficiency):**

Independent t-tests with Bonferroni correction for multiple comparisons: $\alpha_{\text{corrected}} = 0.05 / 3 = 0.0167$

Report format: Mean ± Std Dev, 95% Confidence Interval, Cohen's d, p-value

### 3.7 Ablation Studies for Mechanism Validation

To validate the three-step causal mechanism, we conduct four ablation studies:

**Ablation 1 (Subgroup-Adaptive Augmentation Only):**
- Remove fairness constraint ($w_g = 1$ for all $g$)
- Keep subgroup-specific augmentation policies
- **Tests:** Whether augmentation adaptation alone reduces fairness gap (Step 1 → Step 2 link)

**Ablation 2 (Fairness Constraint Only):**
- Use uniform augmentation ($\pi_{\text{pediatric}} = \pi_{\text{adult}} = \pi_{\text{elderly}}$)
- Keep fairness-constrained optimization
- **Tests:** Whether fairness constraint alone reduces fairness gap (Step 2 → Step 3 link)

**Ablation 3 (No Fairness Mechanisms):**
- Uniform augmentation + no fairness constraint (equivalent to COMET baseline)
- **Tests:** Necessity of both components

**Ablation 4 (Augmentation Strength Sensitivity):**
- Vary pediatric masking rate: $p_{\text{mask}} \in \{0.10, 0.20, 0.30, 0.40\}$
- **Tests:** Whether weaker augmentation for pediatric subgroup outperforms uniformly strong augmentation (resolves tension from literature)

**Mechanism Validation Criteria:**

- **Step 1 → Step 2:** Within-subgroup SSL convergence should differ significantly between adaptive vs. uniform augmentation (measured by contrastive loss per subgroup at epoch 100)
- **Step 2 → Step 3:** Fairness gap should increase by ≥50% when fairness constraint removed (Ablation 1 vs. full FACLSA)
- **Step 3 → Outcome:** Downstream fairness gap should be ≤2× pretraining fairness gap (transfer learning preserves fairness)

### 3.8 Implementation Details

**Encoder Architecture:** 
- Temporal Convolutional Network (TCN) with 4 residual blocks
- Hidden dimension: 128
- Embedding dimension: $d = 64$
- Receptive field: 64 time steps

**Training Configuration:**
- Optimizer: Adam with $\beta_1 = 0.9$, $\beta_2 = 0.999$
- Learning rate: $\eta = 10^{-4}$ with cosine annealing
- Batch size: 256
- Pretraining epochs: 200
- Temperature: $\tau = 0.07$
- Hardware: NVIDIA A100 GPU (40GB memory)

**Computational Resources:**
- Estimated training time: ~8 hours per fold (200 epochs)
- Total experiment time: $5 \text{ folds} \times 5 \text{ seeds} \times 8 \text{ hours} = 200$ GPU-hours
- Storage: ~500GB for MIMIC-III/IV preprocessed data

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1 (Fairness Gap Reduction):**
We expect FACLSA to achieve fairness gaps <5% across pediatric/adult/elderly subgroups, representing ≥60% reduction from COMET baseline (~12-15% gap). Statistical significance will be established through paired t-test (p < 0.05) with medium-to-large effect size (Cohen's d > 0.5). This outcome directly validates the core hypothesis that subgroup-adaptive augmentation combined with fairness constraints reduces performance disparities.

**Primary Outcome 2 (Missing Data Robustness):**
We anticipate AUROC >0.75 on test data with 30-50% missing values, representing ≥15% relative improvement over COMET baseline (~0.65 AUROC). Subgroup-specific missing pattern simulation (pediatric burst missing, elderly gradual degradation) should outperform uniform masking strategies by better matching real-world missing data distributions.

**Secondary Outcome 1 (Label Efficiency):**
FACLSA with physiologically-informed heuristic initialization should achieve performance within 2% AUROC of fully-learned policies using 10× fewer labeled samples (100-200 vs. 1000-2000 per subgroup). This validates the practical feasibility of the approach in limited-label clinical settings.

**Secondary Outcome 2 (Mechanism Validation):**
Ablation studies will confirm the three-step causal mechanism:
- Adaptive augmentation improves within-subgroup representation quality (contrastive loss convergence differs by ≥10% between adaptive vs. uniform)
- Fairness constraint prevents majority group dominance (fairness gap increases ≥50% when constraint removed)
- Fair pretraining transfers to downstream tasks (downstream gap ≤2× pretraining gap)

**Falsification Scenarios:**
The hypothesis will be rejected if: (1) fairness gap ≥10% (no meaningful improvement), (2) missing data robustness <0.70 AUROC (below clinical utility threshold), (3) fairness constraint optimization fails to converge (infeasible constraint region), or (4) downstream fairness gap >2× pretraining gap (transfer learning failure).

### 4.2 Scientific Impact

**Advancing Self-Supervised Learning Theory:**
FACLSA introduces the first principled framework for incorporating fairness constraints into contrastive learning through subgroup-adaptive augmentation. This extends SSL theory beyond uniform augmentation paradigms, demonstrating that **augmentation policies should respect data heterogeneity** rather than applying one-size-fits-all strategies. The physiologically-informed heuristic initialization approach provides a template for integrating domain knowledge into SSL, reducing labeled data requirements by an order of magnitude.

**Fairness in Healthcare ML:**
This research operationalizes fairness as a first-class optimization objective in SSL, moving beyond post-hoc bias mitigation. By achieving <5% fairness gaps while maintaining overall performance >0.80 AUROC, FACLSA demonstrates that **fairness and accuracy are not inherently in conflict** when appropriate inductive biases (subgroup-adaptive augmentation) are incorporated. The explicit fairness constraint formulation provides a reproducible framework for future healthcare ML research.

**Robustness to Missing Data:**
The subgroup-specific missing pattern simulation approach advances missing data handling beyond simple random masking. By matching augmentation strategies to real-world missing data distributions (pediatric burst missing, elderly gradual degradation), FACLSA achieves robustness that transfers to deployment settings. This addresses a critical gap in current SSL methods, which often fail when test-time missing patterns differ from training-time augmentation.

### 4.3 Clinical Impact

**Equitable Clinical Decision Support:**
By reducing fairness gaps from 12-20% to <5%, FACLSA enables equitable deployment of ML-assisted clinical decision support across diverse patient populations. Pediatric ICU patients, who currently experience severe performance degradation with uniform SSL methods, would receive comparable quality predictions as adult patients. This directly addresses healthcare disparities that disproportionately affect minority populations.

**Actionable for Underrepresented Groups:**
The workshop explicitly prioritizes research targeting minority data groups (pediatrics, critical care, rare diseases). FACLSA's subgroup-adaptive framework is immediately applicable to:
- **Pediatric ICU:** Tailored augmentation for faster physiological dynamics and shorter episodes
- **Geriatric care:** Robustness to elevated sensor noise and comorbidity burden
- **Rare diseases:** Label-efficient learning with 100-200 samples per subgroup enables feasibility for low-prevalence conditions

**Clinical Validation Pathway:**
The 5-fold cross-validation protocol with 25 runs provides robust evidence for clinical validation studies. Achieving AUROC >0.75 with 30-50% missing data demonstrates real-world deployment readiness, as clinical data routinely contains 20-40% missing values. The linear probe evaluation (frozen encoder + simple classifier) ensures interpretability for clinical stakeholders.

### 4.4 Broader Impact

**Generalization Beyond Healthcare:**
The subgroup-adaptive augmentation paradigm generalizes to any domain with demographic imbalances and behavioral heterogeneity:
- **Mental health monitoring:** Depression detection across age groups with different symptom manifestations
- **Rehabilitation tracking:** Gait analysis for pediatric vs. elderly populations with distinct movement patterns
- **Personalized medicine:** Treatment response prediction across genetic subgroups

**Open Science Contributions:**
We will release:
1. **FACLSA codebase:** PyTorch implementation with COMET integration, enabling reproducibility
2. **Preprocessed MIMIC benchmarks:** Stratified train/val/test splits with subgroup labels for fair comparison
3. **Augmentation policy library:** Physiologically-informed heuristics for 10+ clinical time series types (ECG, EEG, vital signs)

**Policy Implications:**
This research provides empirical evidence for regulatory frameworks requiring fairness evaluation in clinical ML systems. The <5% fairness gap threshold offers a concrete benchmark for FDA approval processes and hospital procurement decisions, advancing the translation of ML research into equitable clinical practice.

### 4.5 Limitations and Future Work

**Limitations:**
1. **Coarse subgroup definition:** Three-way age grouping may miss intersectional fairness issues (e.g., pediatric + rare disease). Future work should explore hierarchical subgroup taxonomies.
2. **Single modality:** This research focuses on time series only, excluding multimodal fusion (text + time series, imaging + time series) explicitly to manage complexity.
3. **Heuristic policy initialization:** While data-efficient, heuristics may be suboptimal compared to fully learned policies. Future work should investigate meta-learning approaches for automatic policy discovery.
4. **COMET framework dependency:** Implementation tied to COMET architecture. Generalization to other SSL frameworks (SimCLR, MoCo, BYOL) requires validation.

**Future Directions:**
1. **Causal fairness:** Extend beyond demographic parity to counterfactual fairness using causal graphs of physiological mechanisms
2. **Interpretable representations:** Integrate attention mechanisms to identify which time series features drive subgroup-specific predictions
3. **Federated learning:** Adapt FACLSA for multi-institutional settings where data cannot be centralized due to privacy constraints
4. **Prospective clinical trials:** Validate FACLSA in real-world deployment with clinician-in-the-loop evaluation

### 4.6 Timeline and Milestones

**Months 1-3:** Data preprocessing, baseline implementation, initial experiments
**Months 4-6:** FACLSA development, hyperparameter tuning, ablation studies
**Months 7-9:** Full experimental evaluation (25 runs × 3 tasks = 75 experiments)
**Months 10-12:** Statistical analysis, manuscript preparation, code release

This research directly addresses the Workshop on Time Series Representation Learning for Health's call for **robust, fair, and actionable methods** targeting **minority data groups** with **limited labels** and **missing values**. By achieving <5% fairness gaps while maintaining >0.75 AUROC on missing data, FACLSA provides a concrete pathway toward equitable clinical AI deployment.