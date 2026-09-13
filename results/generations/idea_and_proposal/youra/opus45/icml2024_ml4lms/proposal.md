# Research Proposal: Activity Cliff-Aware Conformal Prediction for Reliable Molecular Property Uncertainty Quantification

## 1. Title

**Cluster-Conditioned Activity Cliff-Aware Conformal Prediction (CC-ACCP): Bridging Uncertainty Quantification and Structural Similarity for Reliable Drug Discovery**

---

## 2. Introduction

### 2.1 Background

Machine learning (ML) has emerged as a transformative tool in drug discovery, enabling rapid prediction of molecular properties such as binding affinity, solubility, and toxicity. These predictions guide medicinal chemists in prioritizing compounds for synthesis and experimental validation, potentially reducing the time and cost of bringing new therapeutics to market. However, a critical and persistent challenge undermines the reliability of ML-based molecular property prediction: **activity cliffs**.

Activity cliffs are pairs of structurally similar molecules that exhibit dramatically different biological activities—often differing by more than 100-fold in potency despite sharing >90% structural similarity as measured by Tanimoto coefficients on molecular fingerprints. The seminal work by van Tilborg et al. (2022) through the MoleculeACE benchmark demonstrated that activity cliffs represent a systematic failure mode across all 24 tested ML architectures, from traditional random forests to state-of-the-art graph neural networks. This finding reveals a fundamental limitation: current models cannot reliably distinguish between structurally similar molecules when their activities diverge sharply.

The consequences for drug discovery are severe. When ML models make confident but incorrect predictions on cliff-adjacent molecules, pharmaceutical companies may invest significant resources synthesizing and testing compounds that ultimately fail. Conversely, promising candidates near activity cliffs may be incorrectly deprioritized. This reliability gap demands not just better point predictions, but robust **uncertainty quantification (UQ)** that appropriately flags high-risk predictions.

Conformal prediction (CP) has emerged as a principled framework for UQ, providing distribution-free coverage guarantees without assumptions about the underlying data distribution. Standard CP guarantees that prediction intervals contain the true value with a specified probability (e.g., 90%) marginally across the entire test set. However, this marginal guarantee masks heterogeneous performance: coverage may be excellent for "easy" molecules but poor for difficult cases like activity cliff-adjacent compounds. Recent work such as CoDrug (2023) addresses general covariate shift through density-weighted conformal prediction, achieving 35% coverage gap reduction. However, no existing method specifically targets the activity cliff failure mode that uniquely challenges molecular ML.

### 2.2 Research Objectives

This research proposes **Cluster-Conditioned Activity Cliff-aware Conformal Prediction (CC-ACCP)**, a novel uncertainty quantification framework that explicitly accounts for activity cliff proximity when constructing prediction intervals. Our primary objectives are:

1. **Develop a principled clustering mechanism** that stratifies molecules based on their Tanimoto similarity to known activity cliff pairs, creating homogeneous difficulty groups for calibration.

2. **Design and implement cluster-conditioned conformal prediction** that computes separate nonconformity score thresholds per cluster, ensuring conditional coverage guarantees within each difficulty stratum.

3. **Validate CC-ACCP comprehensively** on the 30 MoleculeACE benchmark datasets, demonstrating superior coverage gap reduction compared to standard CP and CoDrug baselines.

4. **Establish practical guidelines** for deploying activity cliff-aware UQ in prospective drug discovery campaigns.

### 2.3 Significance

This research addresses a critical gap at the intersection of ML reliability and pharmaceutical applications. By providing appropriately calibrated uncertainty estimates that account for activity cliff proximity, CC-ACCP enables:

- **Informed decision-making**: Medicinal chemists can trust that wide prediction intervals genuinely reflect model uncertainty, particularly for cliff-adjacent compounds.
- **Resource optimization**: Experimental validation efforts can be prioritized based on reliable confidence estimates.
- **Regulatory acceptance**: Transparent uncertainty quantification supports the growing regulatory interest in ML model reliability for drug development.

The proposed method bridges theoretical advances in conformal prediction with the practical reality of molecular property prediction, directly addressing the workshop's goal of translating ML research into real-world life science applications.

---

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathcal{D} = \{(x_i, y_i)\}_{i=1}^{n}$ denote a molecular property prediction dataset, where $x_i$ represents a molecule (encoded as a molecular graph or fingerprint) and $y_i \in \mathbb{R}$ is the corresponding property value (e.g., pIC50). Our goal is to construct prediction intervals $\hat{C}(x) = [\hat{y}(x) - q, \hat{y}(x) + q]$ that satisfy conditional coverage guarantees:

$$P(y \in \hat{C}(x) \mid x \in \mathcal{G}_k) \geq 1 - \alpha, \quad \forall k \in \{1, 2, 3\}$$

where $\mathcal{G}_k$ denotes the $k$-th cluster based on activity cliff proximity, and $\alpha = 0.1$ for 90% target coverage.

### 3.2 Activity Cliff Identification

**Definition**: An activity cliff pair $(m_i, m_j)$ satisfies:
1. Structural similarity: $\text{Tanimoto}(\text{ECFP4}(m_i), \text{ECFP4}(m_j)) > 0.9$
2. Activity difference: $|y_i - y_j| > 2$ (corresponding to >100-fold potency difference in pIC50 units)

We compute Extended Connectivity Fingerprints (ECFP4) with radius 2 and 2048 bits using RDKit. For each dataset, we identify all activity cliff pairs from the training set, creating a reference set $\mathcal{AC} = \{(m_i, m_j) : \text{cliff criteria satisfied}\}$.

### 3.3 Activity Cliff Proximity Score

For any molecule $x$, we define its **activity cliff proximity score** as:

$$\text{ACP}(x) = \max_{(m_i, m_j) \in \mathcal{AC}} \max\{\text{Tanimoto}(x, m_i), \text{Tanimoto}(x, m_j)\}$$

This score captures the maximum structural similarity between molecule $x$ and any molecule involved in a known activity cliff pair. Higher scores indicate greater proximity to the "danger zone" where ML models systematically struggle.

### 3.4 Cluster Assignment

Molecules are assigned to three clusters based on their ACP scores:

$$\mathcal{G}(x) = \begin{cases} 
\mathcal{G}_1 \text{ (non-cliff)} & \text{if } \text{ACP}(x) < 0.4 \\
\mathcal{G}_2 \text{ (borderline)} & \text{if } 0.4 \leq \text{ACP}(x) < 0.7 \\
\mathcal{G}_3 \text{ (cliff-adjacent)} & \text{if } \text{ACP}(x) \geq 0.7
\end{cases}$$

These thresholds are motivated by empirical observations that Tanimoto similarity >0.7 typically indicates high structural similarity in medicinal chemistry contexts, while <0.4 represents clearly dissimilar compounds.

### 3.5 Cluster-Conditioned Conformal Prediction Algorithm

**Algorithm: CC-ACCP**

**Input**: Training set $\mathcal{D}_{train}$, calibration set $\mathcal{D}_{cal}$, test molecule $x_{test}$, target coverage $1-\alpha$

**Step 1: Base Model Training**
- Train a Directed Message Passing Neural Network (D-MPNN) using Chemprop on $\mathcal{D}_{train}$
- Obtain point predictions $\hat{y}(x)$ for all molecules

**Step 2: Activity Cliff Identification**
- Identify all activity cliff pairs $\mathcal{AC}$ from $\mathcal{D}_{train}$
- Compute ACP scores for all calibration molecules

**Step 3: Calibration Set Clustering**
- Partition $\mathcal{D}_{cal}$ into clusters: $\mathcal{D}_{cal}^{(k)} = \{(x, y) \in \mathcal{D}_{cal} : \mathcal{G}(x) = \mathcal{G}_k\}$

**Step 4: Nonconformity Score Computation**
- For each calibration point $(x_i, y_i)$, compute the absolute residual:
$$s_i = |y_i - \hat{y}(x_i)|$$

**Step 5: Cluster-Specific Threshold Computation**
- For each cluster $k \in \{1, 2, 3\}$:
$$q_k = \text{Quantile}\left(\{s_i : (x_i, y_i) \in \mathcal{D}_{cal}^{(k)}\}, \frac{\lceil (n_k + 1)(1-\alpha) \rceil}{n_k}\right)$$
where $n_k = |\mathcal{D}_{cal}^{(k)}|$

**Step 6: Prediction Interval Construction**
- For test molecule $x_{test}$:
  1. Compute $\text{ACP}(x_{test})$ and determine cluster $k^* = \mathcal{G}(x_{test})$
  2. Construct interval: $\hat{C}(x_{test}) = [\hat{y}(x_{test}) - q_{k^*}, \hat{y}(x_{test}) + q_{k^*}]$

**Output**: Prediction interval $\hat{C}(x_{test})$ with cluster-conditional coverage guarantee

### 3.6 Handling Small Clusters

When cluster sizes are insufficient for reliable calibration (< 100 molecules), we employ a hierarchical fallback:

$$q_k^{adj} = \begin{cases}
q_k & \text{if } n_k \geq 100 \\
\lambda q_k + (1-\lambda) q_{global} & \text{if } 50 \leq n_k < 100 \\
q_{global} & \text{if } n_k < 50
\end{cases}$$

where $\lambda = (n_k - 50)/50$ provides smooth interpolation and $q_{global}$ is the standard marginal conformal threshold.

### 3.7 Experimental Design

#### 3.7.1 Datasets

We utilize all 30 datasets from the MoleculeACE benchmark, spanning diverse protein targets including kinases, GPCRs, and ion channels. Each dataset contains 500-5000 molecules with experimentally measured binding affinities (pIC50, pKi, or Ki values converted to pIC50 scale).

#### 3.7.2 Data Splitting Strategy

For each dataset, we employ:
- **Random split**: 60% training, 20% calibration, 20% test (5 random seeds)
- **Scaffold split**: Molecules grouped by Murcko scaffolds to simulate prospective deployment

#### 3.7.3 Baseline Methods

1. **Standard Conformal Prediction (CP)**: Marginal coverage guarantee without clustering
2. **CoDrug**: Density-weighted conformal prediction for covariate shift
3. **Mondrian CP**: Binning by predicted value rather than activity cliff proximity
4. **Oracle Clustering**: Clustering by true prediction error (upper bound)

#### 3.7.4 Evaluation Metrics

**Primary Metrics**:

1. **Cluster-Conditional Coverage**:
$$\text{Coverage}_k = \frac{1}{|\mathcal{D}_{test}^{(k)}|} \sum_{(x,y) \in \mathcal{D}_{test}^{(k)}} \mathbb{1}[y \in \hat{C}(x)]$$

2. **Coverage Gap**:
$$\text{Gap}_k = |0.9 - \text{Coverage}_k|$$

3. **Coverage Gap Reduction** (vs. standard CP):
$$\text{CGR} = \frac{\text{Gap}_{CP} - \text{Gap}_{CC-ACCP}}{\text{Gap}_{CP}} \times 100\%$$

**Secondary Metrics**:

4. **Mean Interval Width**:
$$\text{Width}_k = \frac{1}{|\mathcal{D}_{test}^{(k)}|} \sum_{x \in \mathcal{D}_{test}^{(k)}} (q_{upper}(x) - q_{lower}(x))$$

5. **Width Efficiency Ratio**: $\text{Width}_3 / \text{Width}_1$ (cliff-adjacent vs. non-cliff)

6. **Stratified Interval Score (SIS)**: Combines coverage and width into a single metric

#### 3.7.5 Statistical Analysis

- **Sample size**: 30 datasets × 5 seeds = 150 experiments
- **Primary test**: Paired t-test comparing CC-ACCP vs. baselines
- **Significance level**: $\alpha = 0.05$ (one-tailed)
- **Effect size**: Cohen's d with 95% confidence intervals
- **Multiple comparison correction**: Benjamini-Hochberg FDR control

#### 3.7.6 Ablation Studies

1. **Clustering threshold sensitivity**: Vary boundaries (0.3/0.6, 0.4/0.7, 0.5/0.8)
2. **Number of clusters**: Compare 2, 3, and 5 cluster configurations
3. **Alternative proximity metrics**: Test Dice similarity, MACCS keys, learned embeddings
4. **Base model impact**: Evaluate with Random Forest, XGBoost, and AttentiveFP

### 3.8 Implementation Details

- **Base model**: Chemprop v2.x with default D-MPNN architecture
- **Conformal prediction**: MAPIE library with custom cluster conditioning
- **Molecular processing**: RDKit for fingerprints and similarity calculations
- **Computational resources**: Single NVIDIA V100 GPU, ~1 hour per dataset
- **Code availability**: All code will be released on GitHub with MIT license

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

**Primary Outcome (P1)**: We expect CC-ACCP to achieve **>40% coverage gap reduction** compared to standard conformal prediction, exceeding CoDrug's 35% benchmark. This improvement stems from directly targeting the activity cliff failure mode rather than general covariate shift.

**Secondary Outcomes**:
- **P2**: The cliff-adjacent cluster ($\mathcal{G}_3$) will show the largest improvement, with coverage gap reduction >50%, as this group contains the most challenging predictions.
- **P3**: Prediction intervals for cliff-adjacent molecules will be 20-50% wider than non-cliff molecules, appropriately reflecting higher uncertainty without sacrificing coverage.

**Quantitative Targets**:

| Metric | Standard CP | CoDrug | CC-ACCP (Expected) |
|--------|-------------|--------|-------------------|
| Overall Coverage Gap | 8-12% | 5-8% | 3-5% |
| Cliff-Adjacent Coverage | 75-80% | 82-85% | 88-92% |
| Coverage Gap Reduction | 0% | 35% | >40% |

### 4.2 Scientific Contributions

1. **Novel UQ Framework**: First uncertainty quantification method specifically designed for activity cliff-aware molecular property prediction.

2. **Empirical Validation**: Comprehensive evaluation across 30 diverse datasets establishing the correlation between activity cliff proximity and prediction difficulty.

3. **Practical Guidelines**: Actionable recommendations for deploying reliable ML models in drug discovery pipelines.

4. **Open-Source Tools**: Publicly available implementation enabling immediate adoption by the community.

### 4.3 Broader Impact

**For Drug Discovery**: CC-ACCP enables pharmaceutical companies to make more informed decisions about compound prioritization. By providing reliable uncertainty estimates that account for activity cliffs, medicinal chemists can:
- Confidently advance compounds with narrow prediction intervals
- Flag cliff-adjacent predictions for additional experimental validation
- Reduce costly late-stage failures caused by overconfident predictions

**For ML Research**: This work demonstrates how domain-specific knowledge (activity cliffs) can be integrated into general-purpose UQ frameworks (conformal prediction), providing a template for other application domains.

**For Regulatory Science**: As regulatory agencies increasingly scrutinize ML models in drug development, CC-ACCP provides transparent, interpretable uncertainty estimates that support model validation and approval processes.

### 4.4 Limitations and Future Directions

**Acknowledged Limitations**:
- Requires pre-computed activity cliff annotations (addressed by automated identification)
- Fixed cluster boundaries may need target-specific tuning
- Does not address temporal distribution shift in prospective deployment

**Future Extensions**:
- Adaptive threshold learning using validation performance
- Integration with active learning for efficient experimental design
- Extension to multi-task and multi-fidelity settings
- Application to other molecular property prediction tasks (ADMET, toxicity)

### 4.5 Timeline and Milestones

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Implementation | Weeks 1-2 | CC-ACCP codebase, baseline reproductions |
| Validation | Weeks 3-4 | Results on 30 MoleculeACE datasets |
| Analysis | Week 5 | Statistical analysis, ablation studies |
| Documentation | Week 6 | Paper draft, code release |

This research directly addresses the workshop's focus on translating ML advances into practical solutions for life sciences, providing a principled approach to uncertainty quantification that accounts for the unique challenges of molecular property prediction.