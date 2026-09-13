# Research Proposal: Auditing Language Models for Differential Privacy Leakage Across Demographic Groups

## 1. Introduction

### Background

Large language models (LLMs) have become ubiquitous in modern applications, from conversational assistants to content generation and decision support systems. These models are trained on massive datasets scraped from the internet, encompassing diverse linguistic patterns, personal information, and cultural expressions from billions of users worldwide. However, this training paradigm introduces significant privacy risks, as LLMs have been demonstrated to memorize and regurgitate sensitive information from their training data, including personally identifiable information (PII), medical records, and private communications.

Current privacy auditing methodologies for language models primarily focus on aggregate-level measurements of memorization and data extraction vulnerabilities. Techniques such as membership inference attacks, training data extraction attacks, and differential privacy analysis provide valuable insights into overall model behavior but fail to account for how these risks are distributed across different demographic groups. This oversight represents a critical gap in our understanding of LLM safety, particularly given that demographic representation in training corpora is highly skewed toward majority populations in terms of language, geography, socioeconomic status, and cultural background.

A paradoxical phenomenon emerges from this imbalance: underrepresented communities may face disproportionately higher privacy risks precisely because their unique linguistic patterns, names, cultural references, and personal information stand out as rare features in the training distribution. When a model encounters data that deviates significantly from the majority distribution, it may encode this information more distinctly, making it more susceptible to extraction attacks. This creates an inequitable privacy landscape where those already marginalized face additional vulnerabilities from AI systems.

Recent research has begun exploring the intersection of fairness and privacy in machine learning systems. Studies on demographic bias in language model memorization (arXiv:2307.11234) have shown that underrepresented groups are more susceptible to memorization effects. Similarly, work on fairness-aware differential privacy (arXiv:2303.04567) has proposed frameworks for balancing privacy and fairness constraints. However, a comprehensive auditing methodology that systematically quantifies and addresses demographic disparities in privacy leakage remains absent from the literature.

### Research Objectives

This research proposes to develop a comprehensive framework for **demographic-stratified privacy auditing** of language models, with the following specific objectives:

1. **Construct benchmark datasets** with controlled demographic distributions and embedded synthetic personal information ("canaries") to enable systematic measurement of privacy leakage across demographic groups.

2. **Develop novel extraction attack methodologies** tailored to measure memorization rates and extraction success across different demographic categories, accounting for linguistic and cultural variations.

3. **Introduce the Demographic Privacy Disparity (DPD) metric**, a quantitative measure for assessing the inequality of privacy risks across demographic groups in language models.

4. **Propose and evaluate mitigation strategies**, including group-balanced differential privacy training and demographic-aware fine-tuning techniques, to reduce privacy disparities.

### Significance

This research addresses a critical gap at the intersection of privacy, fairness, and safety in language modeling—three pillars of socially responsible AI development. By providing tools to quantify and mitigate demographic disparities in privacy risks, this work contributes to the development of LLMs that protect all users equitably, regardless of their demographic background. The proposed framework aligns with the SoLaR workshop's emphasis on fairness, equity, and accountability, while bridging the historically separate research communities focused on privacy and fairness.

## 2. Methodology

### 2.1 Dataset Construction

#### Canary Design and Demographic Stratification

We will construct evaluation datasets containing synthetic personal information ("canaries") distributed across demographic groups with varying representation levels. The canary framework follows established methodology while introducing demographic stratification:

**Demographic Categories:** We define demographic groups along multiple axes:
- **Linguistic/Ethnic background**: Names and linguistic patterns from 10+ ethnic groups (e.g., Anglo-Saxon, Hispanic, East Asian, South Asian, African, Middle Eastern, Slavic, Nordic)
- **Geographic representation**: High-resource regions (North America, Western Europe) vs. low-resource regions (Sub-Saharan Africa, Southeast Asia, South America)
- **Socioeconomic indicators**: Professional titles, institutional affiliations, residential patterns

**Canary Structure:** Each canary follows the template:
$$C_i = \{n_i, e_i, p_i, a_i, c_i\}$$

where $n_i$ represents a demographically-coded name, $e_i$ is a synthetic email address, $p_i$ is a phone number, $a_i$ is an address, and $c_i$ is contextual information (occupation, interests).

**Distribution Simulation:** To simulate realistic training data imbalances, we create datasets where demographic groups appear with frequencies $f_g$ matching estimated real-world training data distributions:

$$f_g = \frac{|D_g|}{\sum_{g' \in G} |D_{g'}|}$$

where $D_g$ represents documents associated with demographic group $g$, and $G$ is the set of all demographic groups. We will create multiple dataset versions with varying imbalance ratios (1:1, 1:5, 1:10, 1:50) to study the relationship between representation and privacy vulnerability.

**Dataset Size:** The complete dataset will contain 50,000 canaries across 10 demographic groups, with controlled distribution across representation levels.

### 2.2 Extraction Attack Methodology

We develop a suite of extraction attacks designed to probe demographic-specific memorization:

#### Prefix-Based Extraction

Given a prefix $x_{1:k}$ containing partial demographic information, we measure the model's completion accuracy:

$$P_{extract}(g) = \frac{1}{|C_g|} \sum_{c \in C_g} \mathbb{1}[\text{LM}(x_{1:k}) \approx c]$$

where $C_g$ is the set of canaries for demographic group $g$, and the indicator function measures successful extraction within an edit distance threshold.

#### Membership Inference Attacks

We adapt membership inference to demographic contexts by computing:

$$\text{MIA}_g = \text{AUC}(\{(\text{PPL}(c), y_c) : c \in C_g\})$$

where $\text{PPL}(c)$ is the perplexity of canary $c$ and $y_c$ indicates membership status.

#### Template-Based Probing

We design demographic-specific prompt templates:
- "The phone number of [NAME] is..."
- "You can reach [NAME] at email address..."
- "The home address of [NAME] is..."

Templates are adapted to reflect culturally appropriate phrasing patterns across demographic groups.

### 2.3 Demographic Privacy Disparity (DPD) Metric

We introduce the **Demographic Privacy Disparity (DPD)** metric to quantify inequality in privacy risks:

$$\text{DPD} = \frac{\max_{g \in G} P_{extract}(g)}{\min_{g \in G} P_{extract}(g)}$$

A DPD of 1.0 indicates perfect equality, while higher values indicate greater disparity. We also propose a weighted variant accounting for group sizes:

$$\text{DPD}_w = \sum_{g \in G} w_g \cdot \left| P_{extract}(g) - \bar{P}_{extract} \right|$$

where $w_g = f_g$ is the representation frequency and $\bar{P}_{extract}$ is the mean extraction rate.

For statistical rigor, we compute confidence intervals using bootstrap resampling:

$$\text{CI}_{95}(\text{DPD}) = [\text{DPD}^*_{2.5\%}, \text{DPD}^*_{97.5\%}]$$

### 2.4 Mitigation Strategies

#### Group-Balanced Differential Privacy (GB-DP)

Standard differential privacy applies uniform noise across all data. We propose group-balanced DP where noise levels are calibrated per demographic group:

$$\tilde{\theta} = \theta + \mathcal{N}(0, \sigma_g^2 \cdot I)$$

where $\sigma_g$ is determined by:

$$\sigma_g = \sigma_{base} \cdot \sqrt{\frac{f_{max}}{f_g}}$$

This ensures minority groups (lower $f_g$) receive stronger privacy protection through higher noise addition during training.

#### Representation-Aware Regularization

We introduce a regularization term during training that penalizes disproportionate memorization:

$$\mathcal{L}_{total} = \mathcal{L}_{LM} + \lambda \cdot \text{Var}_{g \in G}[\text{Mem}(g)]$$

where $\text{Mem}(g)$ measures memorization scores for group $g$, and $\lambda$ controls the fairness-utility tradeoff.

### 2.5 Experimental Design

#### Models Under Evaluation

We will audit models across scales and architectures:
- **Open-source models**: LLaMA-2 (7B, 13B, 70B), Mistral-7B, Falcon-40B
- **API-accessible models**: GPT-3.5, GPT-4, Claude-2 (via black-box probing)
- **Custom-trained models**: Models trained on our canary-augmented datasets with controlled demographic distributions

#### Experimental Conditions

1. **Baseline auditing**: Measure extraction rates across demographic groups for pre-trained models
2. **Controlled training study**: Train models on datasets with known demographic distributions and measure resulting privacy disparities
3. **Mitigation evaluation**: Compare standard training vs. GB-DP vs. representation-aware regularization

#### Evaluation Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| Extraction Success Rate (ESR) | Per-group extraction accuracy | $P_{extract}(g)$ |
| Demographic Privacy Disparity | Ratio of max to min ESR | DPD formula above |
| Privacy-Fairness Pareto Frontier | Tradeoff between overall privacy and disparity | Multi-objective optimization curve |
| Utility Preservation | Model performance post-mitigation | Perplexity on held-out test sets |

#### Statistical Analysis

All experiments will be conducted with 5 random seeds. We will report means, standard deviations, and 95% confidence intervals. Significance testing will use paired t-tests with Bonferroni correction for multiple comparisons. Effect sizes (Cohen's d) will quantify the magnitude of demographic disparities.

### 2.6 Implementation Details

- **Computational resources**: Experiments will be conducted on A100 GPUs (8× for large models)
- **Codebase**: PyTorch-based implementation with HuggingFace Transformers
- **Reproducibility**: All code, datasets, and trained models will be released under open-source licenses

## 3. Expected Outcomes & Impact

### Expected Results

Based on preliminary analysis and prior literature, we hypothesize:

1. **Disparity confirmation**: Minority demographic groups will exhibit 2-3× higher extraction success rates compared to majority groups, with DPD values ranging from 2.0-4.0 for unmitigated models.

2. **Scale effects**: Larger models will show increased absolute memorization but potentially lower DPD due to better generalization, creating a complex relationship between model scale and fairness.

3. **Mitigation effectiveness**: GB-DP training will reduce DPD by 40-60% while maintaining within 5% of baseline perplexity, demonstrating that privacy equity is achievable without substantial utility loss.

### Deliverables

1. **DemPriv Benchmark**: A comprehensive benchmark dataset for demographic-stratified privacy auditing, including 50,000+ canaries across 10 demographic groups with varying representation levels.

2. **AuditLM Toolkit**: Open-source software for conducting demographic privacy audits, implementing all attack methodologies and metrics described above.

3. **Empirical findings**: Detailed analysis of privacy disparities across major open-source and commercial LLMs, providing actionable insights for model developers.

4. **Mitigation guidelines**: Best practices for training privacy-equitable language models, including hyperparameter recommendations for GB-DP and regularization approaches.

### Broader Impact

This research contributes to multiple dimensions of socially responsible language modeling:

**Scientific impact**: By formalizing the demographic-privacy intersection, we establish a new research direction bridging the fairness and privacy communities, enabling future work on equitable AI systems.

**Practical impact**: The proposed auditing framework provides model developers with tools to assess and address demographic privacy disparities before deployment, supporting proactive rather than reactive safety measures.

**Policy implications**: Quantitative evidence of demographic disparities in privacy risks can inform regulatory frameworks and industry standards for LLM deployment, ensuring that privacy protections extend equitably to all populations.

**Social equity**: By highlighting and addressing the paradox that marginalized communities face heightened privacy risks from AI systems, this work supports the development of technology that serves all users fairly.

### Limitations and Future Directions

We acknowledge that demographic categories are inherently complex and intersectional. Future work should explore intersectional privacy risks (e.g., combinations of ethnicity, language, and socioeconomic factors) and extend the framework to multimodal models where visual and textual information intersect. Additionally, longitudinal studies tracking how privacy disparities evolve through model updates and fine-tuning would provide valuable insights for continuous auditing practices.

In conclusion, this research addresses a critical yet underexplored dimension of language model safety, providing both theoretical frameworks and practical tools for ensuring that the benefits and risks of AI systems are distributed equitably across all demographic groups.