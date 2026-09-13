# Research Proposal: Group-Aware Compression via Fisher Information for Fair Model Deployment in Resource-Constrained Settings

## 1. Introduction

### 1.1 Background

The democratization of machine learning (ML) across developing countries faces a fundamental tension: state-of-the-art models require substantial computational resources, while resource-constrained environments demand lightweight, efficient solutions. Model compression techniques—including pruning, quantization, and knowledge distillation—have emerged as essential tools for deploying ML on edge devices, mobile phones, and low-power infrastructure prevalent in developing regions. These techniques enable healthcare diagnostics in rural clinics, agricultural monitoring on farmers' smartphones, and financial inclusion services in areas with limited connectivity.

However, a critical and largely overlooked problem threatens the equitable deployment of compressed models: standard compression methods systematically harm minority group accuracy. When models are compressed using global importance metrics such as magnitude-based pruning or Fisher Information scoring, the resulting lightweight models exhibit disproportionately degraded performance on underrepresented demographic groups. This phenomenon occurs because minority groups contribute fewer training samples, resulting in lower gradient magnitudes for features critical to minority classification. Consequently, these "endemic features"—weights disproportionately important for minority groups—receive lower importance scores and are preferentially removed during compression.

Recent empirical evidence substantiates this concern. Kamal and Talbert (2024) demonstrated that compression type and amount substantially impact fairness metrics on the COMPAS dataset, while Vlontzou et al. (2025) showed that proper mitigation strategies can achieve 40-57% improvement in equalized odds. Li et al. (2024) provided theoretical grounding by establishing that group-level generalization depends critically on group covariance structure and minority fraction in training data. Despite these findings, existing fairness-aware ML research predominantly focuses on training-time interventions, leaving compression-induced bias as an open problem with significant real-world implications.

### 1.2 Research Objectives

This research proposes **Group-Aware Compression via Fisher Information Scoring (GACFIS)**, a novel compression framework that explicitly accounts for demographic group structure when determining weight importance. Our primary objectives are:

1. **Quantify compression-induced fairness degradation**: Establish empirical baselines measuring how standard compression methods (magnitude pruning, quantization-aware training) affect accuracy gaps between demographic groups across multiple fairness benchmarks.

2. **Develop group-conditional importance scoring**: Design and implement a Fisher Information-based method that computes per-group importance scores, identifies endemic features, and protects minority-critical weights during compression.

3. **Validate fairness-accuracy tradeoffs**: Demonstrate that GACFIS achieves >30% reduction in majority-minority accuracy gaps with <5% overall accuracy cost across compression ratios from 4x to 16x.

4. **Enable fair deployment in resource-constrained settings**: Provide practical guidelines and open-source implementations for deploying fairness-aware compressed models on resource-limited hardware.

### 1.3 Significance

This research directly addresses the PML4LRS mission of democratizing ML while ensuring equitable outcomes. In developing countries, compressed models deployed in healthcare (diagnostic systems), finance (credit scoring), and education (adaptive learning) may systematically underserve already marginalized populations if compression-induced bias is not addressed. By developing methods that maintain fairness under compression, we enable:

- **Equitable healthcare AI**: Diagnostic models that perform equally well across demographic groups when deployed on low-power devices in rural clinics.
- **Fair financial inclusion**: Credit scoring models that do not discriminate against minority populations when running on mobile banking platforms.
- **Inclusive educational technology**: Adaptive learning systems that serve all students equitably regardless of demographic background.

Furthermore, this work advances the theoretical understanding of how model compression interacts with fairness, establishing foundations for future research at this critical intersection.

## 2. Methodology

### 2.1 Problem Formulation

Consider a classification model $f_\theta: \mathcal{X} \rightarrow \mathcal{Y}$ with parameters $\theta \in \mathbb{R}^d$, trained on dataset $\mathcal{D} = \{(x_i, y_i, g_i)\}_{i=1}^N$ where $g_i \in \{0, 1\}$ denotes demographic group membership (majority: $g=0$, minority: $g=1$). Let $\mathcal{D}_0$ and $\mathcal{D}_1$ denote the majority and minority subsets respectively, with $|\mathcal{D}_0| \gg |\mathcal{D}_1|$ reflecting typical imbalanced scenarios.

Standard compression methods compute global importance scores:

$$I_{\text{global}}(w_j) = \mathbb{E}_{(x,y) \sim \mathcal{D}}\left[\left(\frac{\partial \mathcal{L}(f_\theta(x), y)}{\partial w_j}\right)^2\right]$$

where $\mathcal{L}$ is the loss function and $w_j$ is the $j$-th weight. Due to majority group dominance, this expectation is biased toward majority-critical features.

### 2.2 Group-Conditional Fisher Information

GACFIS computes group-conditional Fisher Information for each demographic group:

$$F_g(w_j) = \mathbb{E}_{(x,y) \sim \mathcal{D}_g}\left[\left(\frac{\partial \mathcal{L}(f_\theta(x), y)}{\partial w_j}\right)^2\right], \quad g \in \{0, 1\}$$

We define the **Endemic Feature Score (EFS)** to identify weights disproportionately important for minority groups:

$$\text{EFS}(w_j) = \frac{F_1(w_j)}{F_0(w_j) + \epsilon} - 1$$

where $\epsilon > 0$ prevents division by zero. Weights with $\text{EFS}(w_j) > \tau$ (threshold $\tau$) are classified as endemic features requiring protection during compression.

### 2.3 GACFIS Algorithm

**Algorithm 1: Group-Aware Compression via Fisher Information Scoring**

**Input:** Trained model $f_\theta$, dataset $\mathcal{D}$ with group labels, compression ratio $r$, fairness weight $\lambda \in [0,1]$, endemic threshold $\tau$

**Output:** Compressed model $f_{\theta'}$ with fairness-aware weight selection

1. **Compute Group-Conditional Fisher Information:**
   - For each group $g \in \{0, 1\}$:
     - Sample mini-batches from $\mathcal{D}_g$
     - Compute $F_g(w_j) = \frac{1}{|\mathcal{D}_g|}\sum_{(x,y) \in \mathcal{D}_g}\left(\frac{\partial \mathcal{L}}{\partial w_j}\right)^2$ for all weights

2. **Identify Endemic Features:**
   - Compute $\text{EFS}(w_j) = \frac{F_1(w_j)}{F_0(w_j) + \epsilon} - 1$ for all weights
   - Mark weights with $\text{EFS}(w_j) > \tau$ as endemic: $\mathcal{E} = \{j : \text{EFS}(w_j) > \tau\}$

3. **Compute Fairness-Aware Importance Scores:**
   - For non-endemic weights ($j \notin \mathcal{E}$):
     $$I_{\text{GACFIS}}(w_j) = (1-\lambda) \cdot F_0(w_j) + \lambda \cdot F_1(w_j)$$
   - For endemic weights ($j \in \mathcal{E}$):
     $$I_{\text{GACFIS}}(w_j) = \max(F_0(w_j), F_1(w_j)) \cdot (1 + \alpha \cdot \text{EFS}(w_j))$$
   where $\alpha > 0$ is the endemic protection factor

4. **Apply Compression:**
   - **For Pruning:** Remove weights with lowest $I_{\text{GACFIS}}$ scores until target sparsity achieved
   - **For Quantization:** Allocate higher bit-widths to weights with higher $I_{\text{GACFIS}}$ scores using mixed-precision quantization

5. **Fine-tune with Fairness Regularization:**
   - Optimize: $\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \beta \cdot \mathcal{L}_{\text{fairness}}$
   - Where $\mathcal{L}_{\text{fairness}} = |\text{Acc}_0 - \text{Acc}_1|$ (accuracy parity) or equalized odds penalty

**Return:** Compressed model $f_{\theta'}$

### 2.4 Computational Considerations

The diagonal Fisher approximation used in GACFIS requires computing per-sample gradients for each group, introducing computational overhead. For a model with $d$ parameters and group sizes $n_0, n_1$:

- **Time Complexity:** $O((n_0 + n_1) \cdot d)$ for Fisher computation, compared to $O(N \cdot d)$ for standard methods
- **Space Complexity:** $O(2d)$ for storing group-conditional Fisher matrices

We estimate 20-40% additional training time compared to standard compression, which remains tractable for the model sizes and datasets considered.

### 2.5 Experimental Design

#### 2.5.1 Datasets

| Dataset | Task | Demographic Attribute | Minority Fraction | Size |
|---------|------|----------------------|-------------------|------|
| COMPAS | Recidivism prediction | Race (African-American) | ~35% | 7,214 |
| Adult Income | Income prediction | Sex (Female) | ~33% | 48,842 |
| CelebA | Attribute classification | Age (Young) | ~23% | 202,599 |
| Folktables (ACS) | Employment prediction | Race (Black) | ~12% | 1.5M |

#### 2.5.2 Model Architectures

- **Tabular data (COMPAS, Adult):** 3-layer MLP (256-128-64 hidden units)
- **Image data (CelebA):** ResNet18, MobileNetV2

#### 2.5.3 Compression Configurations

| Method | Compression Ratios | Implementation |
|--------|-------------------|----------------|
| Magnitude Pruning | 4x, 8x, 16x | Global unstructured pruning |
| Quantization-Aware Training (QAT) | 4x (8-bit), 8x (4-bit), 16x (2-bit) | PyTorch quantization |
| GACFIS-Pruning | 4x, 8x, 16x | Algorithm 1 with pruning |
| GACFIS-Quantization | 4x, 8x, 16x | Algorithm 1 with mixed-precision |

#### 2.5.4 Hyperparameter Search

- Fairness weight $\lambda \in \{0.1, 0.3, 0.5, 0.7, 0.9\}$
- Endemic threshold $\tau \in \{0.5, 1.0, 2.0\}$
- Endemic protection factor $\alpha \in \{0.5, 1.0, 2.0\}$
- Fine-tuning fairness weight $\beta \in \{0.01, 0.1, 1.0\}$

#### 2.5.5 Evaluation Metrics

**Accuracy Metrics:**
- Overall accuracy: $\text{Acc} = \frac{1}{N}\sum_{i=1}^N \mathbb{1}[\hat{y}_i = y_i]$
- Group-specific accuracy: $\text{Acc}_g$ for $g \in \{0, 1\}$
- Accuracy gap: $\Delta\text{Acc} = |\text{Acc}_0 - \text{Acc}_1|$

**Fairness Metrics:**
- Equalized Odds Ratio: $\text{EO} = \min\left(\frac{\text{TPR}_1}{\text{TPR}_0}, \frac{\text{FPR}_0}{\text{FPR}_1}\right)$
- Demographic Parity Difference: $\text{DPD} = |P(\hat{Y}=1|G=0) - P(\hat{Y}=1|G=1)|$

**Efficiency Metrics:**
- Model size (MB), parameter count
- Inference latency on target hardware (Raspberry Pi 4, NVIDIA Jetson Nano)

**Primary Success Metric:**
$$\text{Gap Reduction} = \frac{\Delta\text{Acc}_{\text{standard}} - \Delta\text{Acc}_{\text{GACFIS}}}{\Delta\text{Acc}_{\text{standard}}} \times 100\%$$

Target: Gap Reduction > 30% with overall accuracy cost < 5%

#### 2.5.6 Statistical Analysis

- **Sample size:** 20 runs per configuration (5 random seeds × 4 datasets)
- **Statistical tests:** Paired t-test with Bonferroni correction for multiple comparisons
- **Significance level:** $\alpha = 0.05$
- **Effect size:** Cohen's d reported for all comparisons
- **Reporting:** Mean ± standard deviation, 95% confidence intervals

#### 2.5.7 Ablation Studies

1. **Endemic feature identification:** Compare EFS-based selection vs. random selection vs. magnitude-based selection
2. **Fairness weight sensitivity:** Pareto frontier analysis of $\lambda$ vs. accuracy-fairness tradeoff
3. **Compression ratio scaling:** How does fairness degradation scale with compression aggressiveness?
4. **Architecture dependence:** Compare results across MLP, ResNet18, MobileNetV2

### 2.6 Baseline Methods

1. **Standard Magnitude Pruning:** Remove weights with smallest absolute values
2. **Standard QAT:** Uniform quantization with straight-through estimator
3. **Post-hoc Fairness Calibration:** Apply threshold adjustment after standard compression
4. **Reweighted Compression:** Oversample minority group during compression fine-tuning
5. **FairGRAPE (if available):** State-of-the-art fairness-aware pruning baseline

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and preliminary analysis, we anticipate the following outcomes:

**Primary Outcome (P1):** GACFIS will achieve >30% reduction in accuracy gap between majority and minority groups compared to standard compression methods across all tested compression ratios (4x-16x) and datasets. Specifically:
- At 8x compression on COMPAS: Expected gap reduction from ~12% to <8%
- At 8x compression on CelebA: Expected gap reduction from ~15% to <10%

**Secondary Outcomes:**
- **P2:** Equalized odds ratio improvement from baseline <0.7 to >0.85 after GACFIS compression
- **P3:** Identification of Pareto-optimal fairness weight $\lambda^*$ achieving optimal fairness-accuracy tradeoff
- **P4:** Endemic Feature Score variance $\sigma_{\text{EFS}} > 0.5$, validating that minority-critical weights are identifiable

**Efficiency Outcomes:**
- Computational overhead of 20-40% during compression (one-time cost)
- No inference latency increase compared to standard compressed models
- Equivalent model sizes at same compression ratios

### 3.2 Potential Limitations

1. **Demographic label requirement:** GACFIS requires group labels during compression, raising privacy concerns. Future work will explore unsupervised proxy methods.

2. **Binary demographic focus:** Current formulation addresses binary group splits; extension to intersectional fairness requires further research.

3. **Diagonal Fisher approximation:** May miss weight interactions; K-FAC approximation could improve accuracy at computational cost.

4. **Dataset-specific tuning:** Optimal hyperparameters ($\lambda$, $\tau$, $\alpha$) may vary across datasets, requiring validation procedures.

### 3.3 Broader Impact

**Scientific Contributions:**
- First systematic study of compression-induced fairness degradation with group-conditional importance scoring
- Novel Endemic Feature Score metric for identifying minority-critical weights
- Empirical characterization of fairness-accuracy-efficiency tradeoff surfaces

**Practical Impact for Resource-Constrained Settings:**
- Open-source GACFIS implementation compatible with PyTorch and TensorFlow
- Deployment guidelines for fairness-aware compressed models on edge devices
- Benchmark suite for evaluating compression fairness

**Policy Implications:**
- Evidence base for regulatory frameworks requiring fairness audits of compressed models
- Guidelines for ML practitioners in developing countries deploying compressed models in sensitive domains

**Alignment with PML4LRS Goals:**
This research directly addresses the workshop's focus on algorithms tailored for resource-constrained environments while explicitly considering fairness implications. By enabling fair model compression, we support the democratic development of ML infrastructure that serves all populations equitably, regardless of demographic group membership or geographic location.

### 3.4 Future Directions

1. **Unsupervised endemic feature detection:** Develop methods to identify minority-critical weights without explicit demographic labels
2. **Intersectional fairness:** Extend GACFIS to handle multiple, intersecting demographic attributes
3. **Dynamic compression:** Adapt compression ratios based on deployment context and fairness requirements
4. **Federated fairness-aware compression:** Enable fair compression in privacy-preserving distributed settings common in developing regions

---

**Timeline:** 12 months
- Months 1-3: Implementation and baseline establishment
- Months 4-6: Core GACFIS experiments and ablation studies
- Months 7-9: Extended benchmarking and hardware deployment testing
- Months 10-12: Analysis, paper writing, and open-source release

**Resources Required:**
- Compute: 4 NVIDIA A100 GPUs for training experiments
- Edge devices: Raspberry Pi 4, NVIDIA Jetson Nano for deployment testing
- Personnel: 2 graduate researchers, 1 postdoctoral advisor