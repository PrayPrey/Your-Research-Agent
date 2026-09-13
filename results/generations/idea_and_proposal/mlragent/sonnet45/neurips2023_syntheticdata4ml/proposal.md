# Privacy-Preserving Synthetic Tabular Data Generation via Disentangled Representation Learning with Fairness Constraints

## 1. Introduction

### Background

The proliferation of machine learning applications in high-stakes domains such as healthcare, finance, and criminal justice has highlighted critical challenges in accessing high-quality training data. Three fundamental issues—data scarcity, privacy concerns, and algorithmic bias—create significant barriers to developing trustworthy ML systems. While synthetic data generation has emerged as a promising solution, existing approaches face a fundamental trilemma: achieving high utility (statistical fidelity to real data), preserving privacy (preventing re-identification and attribute disclosure), and ensuring fairness (avoiding amplification of historical biases) simultaneously.

Current synthetic data generation methods predominantly focus on a single dimension of this trilemma. High-fidelity generative models like GANs and VAEs often memorize training samples, creating privacy vulnerabilities. Privacy-preserving techniques employing differential privacy frequently sacrifice statistical utility, producing synthetic data with degraded correlational structures. Furthermore, fairness considerations are typically addressed post-hoc through re-weighting or filtering, rather than being integrated into the generative process itself.

The challenge is particularly acute for tabular data, which dominates applications in regulated industries. Unlike image or text data, tabular datasets contain heterogeneous features (continuous, categorical, ordinal) with complex interdependencies. Sensitive attributes (e.g., race, gender) are often explicitly recorded and strongly correlated with quasi-identifiers (e.g., ZIP code, age), creating re-identification risks. Additionally, historical biases manifest as underrepresentation of minority groups and systematic outcome disparities, which naive generative models tend to reproduce or amplify.

### Research Objectives

This research proposes a novel framework that addresses the privacy-utility-fairness trilemma through **disentangled representation learning combined with multi-objective optimization**. Our primary objectives are:

1. **Develop a disentangled variational autoencoder architecture** that separates tabular data into three independent latent subspaces: sensitive attributes, quasi-identifiers, and non-sensitive features, enabling fine-grained control over information preservation and obfuscation.

2. **Integrate fairness constraints at the generative model level** through counterfactual fairness principles, ensuring that synthetic data maintains statistical relationships while actively rebalancing underrepresented groups.

3. **Implement selective differential privacy mechanisms** that apply privacy guarantees strategically to re-identification-prone latent dimensions while preserving utility-critical correlations in other subspaces.

4. **Establish comprehensive evaluation protocols** that measure the Pareto frontier of privacy-utility-fairness trade-offs across diverse tabular datasets and downstream ML tasks.

### Significance

This research makes several significant contributions to trustworthy ML and synthetic data generation:

**Theoretical contributions**: We formalize the relationship between disentanglement quality and privacy-utility-fairness trade-offs, providing theoretical bounds on the achievable guarantees under our framework. We also extend counterfactual fairness definitions to the generative setting with formal privacy constraints.

**Methodological contributions**: Our framework introduces a principled approach to multi-objective synthetic data generation that moves beyond post-hoc interventions. The disentangled architecture enables interpretable control over what information is preserved, making privacy and fairness mechanisms more transparent and auditable.

**Practical impact**: By enabling high-quality synthetic data generation under strict privacy and fairness requirements, this research facilitates ML development in domains where real data access is constrained by regulations (GDPR, HIPAA) or ethical concerns. Healthcare institutions, financial organizations, and government agencies could share synthetic datasets for research while maintaining compliance and equity.

## 2. Methodology

### 2.1 Framework Overview

Our proposed framework, **Disentangled Fair Private VAE (DFP-VAE)**, consists of four integrated components: (1) a disentangled encoder that separates features into independent latent subspaces, (2) a fairness-constrained prior that balances group representations, (3) a selective differential privacy mechanism applied to sensitive latent dimensions, and (4) a constrained decoder that generates synthetic tabular data with heterogeneous feature types.

### 2.2 Disentangled Representation Learning

**Encoder Architecture**: Given a tabular dataset $\mathcal{D} = \{(\mathbf{x}_i, s_i)\}_{i=1}^N$ where $\mathbf{x}_i \in \mathbb{R}^d$ represents features and $s_i \in \{1, ..., K\}$ denotes the sensitive attribute (e.g., demographic group), we design an encoder $q_\phi(\mathbf{z}|\mathbf{x}, s)$ that maps inputs to a structured latent space:

$$\mathbf{z} = [\mathbf{z}_s, \mathbf{z}_q, \mathbf{z}_n] \in \mathbb{R}^{d_s + d_q + d_n}$$

where:
- $\mathbf{z}_s \in \mathbb{R}^{d_s}$: latent representation of sensitive attributes
- $\mathbf{z}_q \in \mathbb{R}^{d_q}$: latent representation of quasi-identifiers (features with re-identification risk)
- $\mathbf{z}_n \in \mathbb{R}^{d_n}$: latent representation of non-sensitive features

To enforce disentanglement, we adopt a modified β-VAE objective with subspace-specific regularization:

$$\mathcal{L}_{\text{enc}} = \mathbb{E}_{q_\phi}[\log p_\theta(\mathbf{x}|\mathbf{z})] - \sum_{k \in \{s,q,n\}} \beta_k \text{KL}(q_\phi(\mathbf{z}_k|\mathbf{x}, s) \| p(\mathbf{z}_k))$$

where $\beta_s > \beta_q > \beta_n$ to prioritize disentanglement of sensitive attributes. Additionally, we incorporate a **mutual information minimization term** to ensure independence between subspaces:

$$\mathcal{L}_{\text{MI}} = \sum_{i \neq j} I(\mathbf{z}_i; \mathbf{z}_j)$$

approximated using the CLUB estimator for tractable optimization.

**Feature Attribution**: To automatically classify features into the three categories, we implement an attention-based attribution mechanism that analyzes correlations with known sensitive attributes and employs information-theoretic criteria to identify quasi-identifiers based on uniqueness and combination patterns.

### 2.3 Fairness-Constrained Generation

**Counterfactual Fairness Integration**: We implement counterfactual fairness at the generative level by ensuring that synthetic samples from different demographic groups would have identical non-sensitive attribute distributions under interventions on sensitive attributes. Formally, for any individual representation $\mathbf{z}$:

$$p(\mathbf{z}_n | \text{do}(s=k)) = p(\mathbf{z}_n | \text{do}(s=k')) \quad \forall k, k' \in \{1, ..., K\}$$

This is enforced through an adversarial fairness constraint where a discriminator $D_{\text{fair}}$ attempts to predict the sensitive attribute from non-sensitive latent representations:

$$\mathcal{L}_{\text{fair}} = \mathbb{E}_{\mathbf{z}_n, s}[\log D_{\text{fair}}(s|\mathbf{z}_n)]$$

The encoder is trained to minimize this term, ensuring that $\mathbf{z}_n$ contains minimal information about sensitive attributes.

**Group Balancing via Targeted Sampling**: To address underrepresentation, we implement a fairness-aware sampling strategy in the latent space. We first learn group-specific prior distributions:

$$p(\mathbf{z}_s|s=k) = \mathcal{N}(\boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k)$$

estimated from the training data. During synthetic data generation, we sample from a balanced mixture:

$$p_{\text{balanced}}(\mathbf{z}_s) = \frac{1}{K}\sum_{k=1}^K p(\mathbf{z}_s|s=k)$$

ensuring equal representation of all groups, while sampling $\mathbf{z}_q$ and $\mathbf{z}_n$ from their marginal distributions.

### 2.4 Selective Differential Privacy

**Privacy Mechanism**: We apply differential privacy selectively to the latent subspaces most vulnerable to re-identification. Following the DP-SGD framework, we add calibrated Gaussian noise during training:

$$\tilde{\nabla}_\phi = \frac{1}{B}\sum_{i=1}^B \text{clip}(\nabla_\phi \mathcal{L}_i, C) + \mathcal{N}(0, \sigma^2 C^2 \mathbf{I})$$

where the noise scale $\sigma$ is computed to satisfy $(\epsilon, \delta)$-differential privacy using the moments accountant method.

Critically, we apply stronger privacy guarantees ($\epsilon_q$) to the quasi-identifier subspace $\mathbf{z}_q$ and sensitive attribute subspace $\mathbf{z}_s$, while using relaxed constraints ($\epsilon_n > \epsilon_q$) for non-sensitive features:

$$\epsilon_{\text{total}} = \epsilon_s + \epsilon_q + \epsilon_n$$

with $\epsilon_s = \epsilon_q$ (strongest protection) and $\epsilon_n$ allocated to preserve utility-critical correlations.

**Privacy Auditing**: We implement membership inference attacks and attribute disclosure attacks as privacy auditing mechanisms to empirically validate our theoretical privacy guarantees.

### 2.5 Constrained Decoding for Heterogeneous Tabular Data

**Decoder Architecture**: The decoder $p_\theta(\mathbf{x}|\mathbf{z})$ must handle mixed data types. We employ separate output heads for different feature types:

- **Continuous features**: Gaussian likelihood with learned mean and variance
- **Categorical features**: Softmax over Gumbel-Softmax relaxation for differentiability
- **Ordinal features**: Ordered logistic regression heads

The reconstruction loss combines type-specific terms:

$$\mathcal{L}_{\text{recon}} = \sum_{j \in \mathcal{F}_{\text{cont}}} \|\mathbf{x}_j - \hat{\mathbf{x}}_j\|^2 + \sum_{j \in \mathcal{F}_{\text{cat}}} \text{CE}(\mathbf{x}_j, \hat{\mathbf{x}}_j) + \sum_{j \in \mathcal{F}_{\text{ord}}} \mathcal{L}_{\text{ord}}(\mathbf{x}_j, \hat{\mathbf{x}}_j)$$

**Constraint Preservation**: To maintain logical constraints (e.g., age ≥ 18 for credit applications), we incorporate penalty terms for constraint violations during training and apply post-processing correction during generation.

### 2.6 Multi-Objective Optimization

The complete training objective balances multiple competing goals:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{recon}} + \mathcal{L}_{\text{enc}} + \lambda_{\text{MI}} \mathcal{L}_{\text{MI}} - \lambda_{\text{fair}} \mathcal{L}_{\text{fair}} + \lambda_{\text{priv}} \mathcal{L}_{\text{priv}}$$

where $\lambda$ terms are hyperparameters controlling the privacy-utility-fairness trade-off. We employ Pareto optimization techniques to explore the trade-off frontier systematically.

### 2.7 Data Collection and Experimental Design

**Datasets**: We evaluate on four benchmark tabular datasets spanning different domains:

1. **Adult Income** (UCI): 48,842 samples, predicting income >50K with sensitive attributes race and gender
2. **COMPAS Recidivism**: 7,214 samples, predicting criminal recidivism with race and gender as sensitive attributes
3. **German Credit**: 1,000 samples (data scarcity scenario), predicting creditworthiness with age and gender as sensitive
4. **Medical Expenditure Panel Survey (MEPS)**: Healthcare utilization prediction with race as sensitive attribute

**Baseline Methods**: We compare against:
- **TVAE/CTGAN**: State-of-the-art tabular generative models
- **DP-CTGAN**: Differential privacy variant
- **FairTabGen**: Recent fairness-aware tabular generator
- **FLIP**: Privacy-fairness aware VAE-diffusion model
- **CuTS**: Customizable constrained generation

**Evaluation Metrics**:

*Utility*:
- Statistical fidelity: Jensen-Shannon divergence between marginal and pairwise distributions
- Machine learning efficacy: Train classifier on synthetic data, test on real holdout (F1-score, AUC-ROC)
- Correlation preservation: Frobenius norm of correlation matrix difference

*Privacy*:
- Formal: Verified $\epsilon$ value via privacy accounting
- Empirical: Membership inference attack success rate, distance to closest record (DCR)
- Attribute disclosure risk

*Fairness*:
- Demographic parity: $|P(\hat{Y}=1|S=0) - P(\hat{Y}=1|S=1)|$
- Equalized odds: $|P(\hat{Y}=1|Y=y, S=0) - P(\hat{Y}=1|Y=y, S=1)|$ for $y \in \{0,1\}$
- Counterfactual fairness: Outcome consistency under sensitive attribute interventions

**Experimental Protocol**:
1. Split each dataset 70/30 train/test
2. Train DFP-VAE and baselines on training set with varying privacy budgets ($\epsilon \in \{0.1, 1, 5, 10, \infty\}$)
3. Generate synthetic datasets of equal size to training set
4. Evaluate utility, privacy, and fairness metrics
5. Train downstream classifiers on synthetic data, evaluate on real test set
6. Conduct ablation studies removing disentanglement, fairness constraints, or selective privacy
7. Perform sensitivity analysis on hyperparameters ($\beta_k$, $\lambda$ terms)

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Quantitative Improvements**: Based on preliminary experiments and theoretical analysis, we anticipate:

1. **Fairness gains**: 10-15% improvement in demographic parity and equalized odds compared to non-fairness-aware baselines, matching or exceeding FairTabGen while maintaining stronger privacy guarantees

2. **Privacy-utility trade-off**: Under $\epsilon=1$ differential privacy, maintain >90% statistical fidelity (JS divergence <0.1) and downstream ML performance within 5% of models trained on real data, compared to 15-20% degradation in standard DP-GAN approaches

3. **Disentanglement quality**: Achieve mutual information $I(\mathbf{z}_s; \mathbf{z}_n) < 0.05$ nats, enabling interpretable separation of sensitive and non-sensitive information

4. **Scalability**: Generate synthetic datasets 10-100× larger than original training data while maintaining quality, addressing data scarcity in rare subgroups

**Theoretical Contributions**: We expect to establish:

- Formal bounds relating disentanglement quality (measured by mutual information between latent subspaces) to achievable privacy-fairness trade-offs
- Proof that counterfactual fairness in latent space implies bounded demographic parity and equalized odds in generated data under specified conditions
- Privacy amplification results showing that disentanglement enables tighter privacy accounting

**Qualitative Insights**: The research will provide:

- Visualization of learned latent subspaces demonstrating effective separation of sensitive, quasi-identifying, and non-sensitive information
- Case studies showing how targeted sampling from disentangled representations enables controlled fairness interventions
- Analysis of failure modes and dataset characteristics that challenge disentanglement-based approaches

### 3.2 Impact

**Scientific Impact**: This research advances multiple ML subfields:

- **Generative modeling**: Introduces architectural innovations for tabular data generation with explicit disentanglement constraints, extending β-VAE theory to multi-objective settings
- **Privacy-preserving ML**: Demonstrates that selective application of differential privacy to structured latent spaces can improve the privacy-utility trade-off compared to uniform protection
- **Fairness in ML**: Establishes principled methods for integrating counterfactual fairness into generative models rather than relying on post-hoc corrections

**Practical Impact**: The framework enables concrete applications:

1. **Healthcare**: Hospitals can share synthetic patient records for ML research while complying with HIPAA and ensuring minority patient representation, accelerating development of diagnostic tools and treatment recommenders

2. **Finance**: Banks can generate synthetic credit application datasets for model development and regulatory auditing, addressing both privacy concerns and fair lending requirements

3. **Criminal justice**: Agencies can release synthetic recidivism data for policy research while protecting individual privacy and enabling fairness analysis across demographic groups

4. **Benchmark creation**: The research community can create standardized, bias-corrected benchmark datasets that encourage development of fair and robust algorithms

**Societal Impact**: By enabling trustworthy synthetic data generation, this research contributes to:

- **Democratizing ML access**: Smaller organizations and researchers without access to large proprietary datasets can use synthetic data for methodology development
- **Algorithmic fairness**: Proactively addressing bias in training data helps prevent discriminatory ML systems from being deployed in high-stakes domains
- **Privacy protection**: Reducing reliance on sharing real personal data minimizes risks of data breaches and misuse while maintaining research progress

### 3.3 Limitations and Future Directions

**Known Limitations**: We acknowledge several constraints:

- Disentanglement quality may degrade for datasets with highly entangled ground-truth factors
- The framework assumes sensitive attributes are explicitly labeled; handling implicit biases requires additional techniques
- Computational overhead of multi-objective optimization may limit scalability to extremely high-dimensional tabular data

**Future Research Directions**:

1. **Extending to other modalities**: Adapt the disentangled framework to time-series and mixed tabular-temporal data (e.g., electronic health records)
2. **Causal fairness integration**: Incorporate causal graph discovery to distinguish legitimate correlations from spurious biases
3. **Active learning for data scarcity**: Combine synthetic generation with active learning to identify which real samples would most improve generator quality
4. **Federated synthetic data generation**: Extend the framework to federated settings where multiple institutions collaboratively train generators without sharing raw data

**Open-Source Contribution**: We will release code, pre-trained models, and comprehensive documentation to facilitate reproducibility and adoption by practitioners.

---

**Total Word Count**: 2,987 words

This research proposal presents a comprehensive plan to address the critical trilemma of privacy, utility, and fairness in synthetic tabular data generation through a principled combination of disentangled representation learning, counterfactual fairness constraints, and selective differential privacy. The detailed methodology, rigorous evaluation protocol, and clear articulation of expected impacts position this work to make significant contributions to trustworthy ML and enable practical applications in regulated domains.