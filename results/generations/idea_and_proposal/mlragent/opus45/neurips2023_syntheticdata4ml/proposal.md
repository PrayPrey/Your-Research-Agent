# Research Proposal

## Title
Privacy-Aware Synthetic Tabular Data Generation via LLM-Guided Differential Privacy Budget Allocation

## 1. Introduction

### Background
The proliferation of machine learning applications in high-stakes domains such as healthcare, finance, and education has created an unprecedented demand for high-quality training data. However, three fundamental challenges—data scarcity, privacy concerns, and representation bias—continue to impede the development of trustworthy ML systems. Synthetic data generation has emerged as a promising solution to address these interconnected challenges, offering the potential to create unlimited training samples while protecting individual privacy and correcting demographic imbalances.

Recent advances in Large Language Models (LLMs) have demonstrated remarkable capabilities in understanding and generating structured data, including tabular datasets that form the backbone of many critical applications. Concurrently, differential privacy (DP) has established itself as the gold standard for formal privacy guarantees in data release mechanisms. However, the intersection of LLM-based synthetic data generation and differential privacy remains underexplored, particularly regarding the optimization of privacy-utility trade-offs across heterogeneous data features and demographic subgroups.

Current approaches to differentially private synthetic data generation typically apply uniform privacy budgets ($\epsilon$) across all features and samples. This one-size-fits-all strategy fundamentally ignores two critical realities: (1) different features carry varying levels of sensitivity and privacy risk—a medical diagnosis is inherently more sensitive than a zip code; and (2) uniform noise injection disproportionately affects underrepresented groups, whose limited sample sizes make them more vulnerable to utility degradation under DP mechanisms.

### Research Objectives
This research proposes a novel framework called **LSPA (LLM-guided Semantic Privacy Allocation)** that leverages the semantic understanding capabilities of LLMs to intelligently allocate differential privacy budgets across features and demographic subgroups. Our specific objectives are:

1. To develop an LLM-based feature sensitivity analysis module that automatically categorizes tabular features based on their semantic privacy risk levels.
2. To design a fairness-aware adaptive privacy budget allocation mechanism that preserves utility for underrepresented groups while maintaining rigorous DP guarantees.
3. To create a group-conditioned synthetic data generation pipeline with semantically-calibrated noise injection.
4. To comprehensively evaluate the framework on benchmark healthcare and financial datasets, demonstrating improved privacy-utility-fairness trade-offs.

### Significance
This research addresses a critical gap at the intersection of privacy-preserving machine learning and algorithmic fairness. By bridging LLM semantic understanding with differential privacy mechanisms, we enable more nuanced and equitable synthetic data generation. The proposed framework has significant implications for enabling trustworthy ML in sensitive domains where data sharing is currently impeded by privacy regulations (e.g., HIPAA, GDPR) and fairness requirements.

## 2. Methodology

### 2.1 Framework Overview

The LSPA framework consists of three interconnected modules: (1) LLM-based Semantic Sensitivity Analysis, (2) Fairness-Aware Budget Allocation, and (3) Group-Conditioned Generation with Adaptive Noise Calibration. Figure 1 illustrates the overall architecture.

### 2.2 Module 1: LLM-based Semantic Sensitivity Analysis

Given a tabular dataset $D$ with features $\{f_1, f_2, ..., f_m\}$, we leverage pre-trained LLMs to analyze the semantic privacy sensitivity of each feature. We construct structured prompts that include:

- Feature name and description
- Sample values (with appropriate anonymization)
- Data type and domain context

The LLM assigns each feature to one of $K$ sensitivity tiers $S = \{s_1, s_2, ..., s_K\}$ where $s_1$ represents the highest sensitivity. Formally, we define the sensitivity scoring function:

$$\phi(f_i) = \text{LLM}(\text{prompt}(f_i, \text{context})) \rightarrow s_k \in S$$

To ensure robustness, we employ ensemble prompting with $T$ different prompt templates and aggregate responses:

$$\hat{s}_i = \text{mode}(\{\phi_t(f_i)\}_{t=1}^{T})$$

We further validate LLM assessments against established privacy frameworks (e.g., NIST Privacy Framework categories) through a calibration step that adjusts sensitivity scores based on domain-specific regulations.

### 2.3 Module 2: Fairness-Aware Budget Allocation

Given a total privacy budget $\epsilon_{total}$ and protected attribute $A$ with groups $\{g_1, g_2, ..., g_G\}$, we design an allocation mechanism that considers both feature sensitivity and group representation.

**Feature-level Budget Allocation:**
For features with sensitivity tier $s_k$, we allocate budget according to:

$$\epsilon_{f_i} = \frac{\epsilon_{feature} \cdot w_k}{\sum_{j=1}^{m} w_{\hat{s}_j}}$$

where $w_k$ is a sensitivity-dependent weight with $w_1 < w_2 < ... < w_K$, ensuring less sensitive features receive larger budgets (more utility).

**Group-level Budget Allocation:**
To ensure fairness, we reserve utility budgets proportional to the inverse of group representation:

$$\epsilon_{g_j} = \epsilon_{group} \cdot \frac{(1/n_{g_j})^\alpha}{\sum_{l=1}^{G} (1/n_{g_l})^\alpha}$$

where $n_{g_j}$ is the sample size of group $g_j$ and $\alpha \in [0, 1]$ controls the fairness-utility trade-off. When $\alpha = 0$, allocation is uniform; when $\alpha = 1$, it is fully proportional to inverse representation.

**Overall Budget Composition:**
The total budget satisfies:

$$\epsilon_{total} = \epsilon_{feature} + \epsilon_{group} + \epsilon_{generation}$$

where $\epsilon_{generation}$ is reserved for the generative model's DP mechanism.

### 2.4 Module 3: Group-Conditioned Generation with Adaptive Noise

We build upon the transformer-based tabular generation architecture, similar to recent approaches like TabDDPM and GReaT, but with group-conditioned noise calibration.

**Step 1: Data Encoding**
Continuous features are normalized, and categorical features are embedded. We obtain encoded representation:

$$\mathbf{x}_i = \text{Encode}(D_i) \in \mathbb{R}^d$$

**Step 2: Group-Conditioned Generation**
For each demographic group $g_j$, we train a conditional generator:

$$p_\theta(\mathbf{x} | g_j) = \prod_{i=1}^{m} p_\theta(x_i | x_{<i}, g_j)$$

The LLM backbone processes serialized tabular rows with group conditioning tokens.

**Step 3: Adaptive Noise Injection**
We apply the Gaussian mechanism with group and feature-specific noise:

$$\tilde{x}_i^{(g_j)} = x_i + \mathcal{N}(0, \sigma_{i,j}^2)$$

where the noise scale is calibrated as:

$$\sigma_{i,j} = \frac{\Delta_{f_i} \cdot \sqrt{2 \ln(1.25/\delta)}}{\epsilon_{f_i} \cdot \epsilon_{g_j} / \epsilon_{total}}$$

and $\Delta_{f_i}$ is the sensitivity of feature $f_i$.

**Step 4: Privacy Composition**
We employ Rényi Differential Privacy (RDP) for tight composition across features and groups:

$$\epsilon_{RDP}^{(\alpha)} = \sum_{i=1}^{m} \sum_{j=1}^{G} \frac{\alpha \Delta_{f_i}^2}{2\sigma_{i,j}^2}$$

Converting to $(\epsilon, \delta)$-DP via:

$$\epsilon = \epsilon_{RDP}^{(\alpha)} + \frac{\ln(1/\delta)}{\alpha - 1}$$

### 2.5 Experimental Design

**Datasets:**
1. **Healthcare:** MIMIC-III (ICU patient records), UCI Heart Disease
2. **Financial:** Adult Income, German Credit, Folktables (ACS)

**Baselines:**
- Uniform DP-GAN and DP-VAE
- PATE-GAN
- PrivBayes
- CuTS (customizable tabular synthesis)
- FLIP (fairness-aware DP generation)
- Non-private LLM-based generators (GReaT, TabLLM)

**Evaluation Metrics:**

*Privacy Metrics:*
- Membership Inference Attack (MIA) success rate
- Attribute Inference Attack accuracy
- Distance to Closest Record (DCR)

*Utility Metrics:*
- Machine Learning Efficacy: Train on Synthetic, Test on Real (TSTR) accuracy
- Statistical Fidelity: Jensen-Shannon Divergence, correlation preservation
- Query Accuracy: marginal and conditional distribution errors

*Fairness Metrics:*
- Demographic Parity Difference: $|P(\hat{Y}=1|A=0) - P(\hat{Y}=1|A=1)|$
- Equalized Odds Difference
- Group-wise utility gap: $\max_{g_i, g_j} |\text{TSTR}_{g_i} - \text{TSTR}_{g_j}|$

**Experimental Protocol:**
1. Split each dataset: 80% for training generators, 20% for held-out evaluation
2. Generate synthetic datasets at varying privacy budgets: $\epsilon \in \{0.1, 0.5, 1.0, 2.0, 5.0, 10.0\}$
3. Train downstream classifiers (XGBoost, MLP) on synthetic data
4. Evaluate on real held-out data
5. Repeat 5 times with different random seeds; report mean ± std

**Ablation Studies:**
- Impact of LLM sensitivity analysis vs. manual annotation
- Effect of fairness parameter $\alpha$ on group-wise utility
- Comparison of different LLM backbones (GPT-4, LLaMA, Mistral)

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Technical Outcomes:**
1. A novel semantic sensitivity scoring system achieving >85% agreement with human privacy experts on benchmark datasets.
2. Demonstrated improvement of 15-25% in TSTR accuracy for underrepresented groups compared to uniform DP baselines at equivalent privacy budgets ($\epsilon = 1.0$).
3. Reduction in group-wise utility gap by 30-40% while maintaining overall DP guarantees.
4. Comprehensive benchmark results establishing Pareto frontiers for privacy-utility-fairness trade-offs.

**Methodological Contributions:**
1. First framework integrating LLM semantic understanding into differential privacy budget allocation for tabular data.
2. Theoretical analysis of composition bounds under heterogeneous budget allocation.
3. Open-source implementation and reproducible experimental pipeline.

### Broader Impact

**Scientific Impact:**
This research bridges three traditionally separate research communities: LLM-based generation, differential privacy, and algorithmic fairness. The framework provides a template for future work on semantically-aware privacy mechanisms beyond tabular data.

**Practical Impact:**
The LSPA framework enables practitioners in healthcare and finance to generate high-quality synthetic data that:
- Satisfies regulatory privacy requirements (HIPAA, GDPR)
- Maintains utility for downstream ML tasks
- Ensures equitable representation of minority groups

**Societal Impact:**
By addressing the tension between privacy and fairness in synthetic data, this work contributes to more equitable AI systems. Improved synthetic data generation for underrepresented groups can help reduce algorithmic bias in critical applications affecting marginalized communities.

### Limitations and Future Directions
We acknowledge potential limitations including: (1) reliance on LLM quality for sensitivity analysis, (2) computational overhead of group-conditioned generation, and (3) applicability to extremely high-dimensional datasets. Future work will explore federated versions of LSPA and extensions to multi-modal data combining tabular and text features.