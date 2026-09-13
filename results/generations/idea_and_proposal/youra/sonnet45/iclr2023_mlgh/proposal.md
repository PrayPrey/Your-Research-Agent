# Research Proposal: Economic Inequality Regularization for Fair Medical Machine Learning

## 1. Title

**Economic Inequality Regularization for Fair Medical Machine Learning: Training with Generalized Entropy Indices to Address Healthcare Algorithmic Bias**

## 2. Introduction

### 2.1 Background

The COVID-19 pandemic starkly revealed the limitations of machine learning in addressing global health challenges, particularly in ensuring equitable healthcare delivery across diverse populations. Despite impressive advances in medical AI, systematic performance disparities persist across demographic groups, with models consistently underperforming for underrepresented populations. This algorithmic bias is not merely a technical inconvenience—it represents a critical barrier to achieving health equity and threatens to exacerbate existing healthcare disparities.

The root cause of this problem lies in fundamental data inequality. Biomedical datasets exhibit severe demographic imbalances, with non-European populations comprising less than 10% of samples in major genomic and clinical databases (Gao et al., 2023). This representation gap translates directly into performance gaps: machine learning models trained on such data systematically fail to generalize to minority populations, creating what Gao et al. term "biomedical data inequality"—a structural health risk that perpetuates and amplifies existing healthcare disparities.

Current approaches to algorithmic fairness in healthcare predominantly rely on post-hoc corrections—adjusting model outputs or decision thresholds after biased learning has already occurred. While these methods can improve fairness metrics, they suffer from fundamental limitations. Post-hoc corrections cannot recover information that was never learned during training, and recent theoretical work by Laakom et al. (2025) demonstrates that fairness interventions applied during training generalize better than post-processing approaches. This suggests that addressing bias at its source—the training process itself—offers superior potential for achieving robust, generalizable fairness.

Meanwhile, economics has developed sophisticated tools for measuring and analyzing distributional inequality over seven decades. The Generalized Entropy (GE) family of indices, grounded in distributive justice theory and social welfare optimization, provides theoretically principled methods for quantifying inequality across populations. These indices possess desirable mathematical properties—including decomposability, scale invariance, and sensitivity to different parts of the distribution—that make them particularly suitable for measuring representation inequality in machine learning contexts. However, despite their theoretical elegance and empirical validation in economics, GE indices remain largely unexplored as training objectives in machine learning.

### 2.2 Research Gap

The current landscape reveals three critical gaps:

**Gap 1: Post-hoc vs. Training-time Interventions.** Existing fairness methods predominantly operate after model training, limiting their effectiveness. While Supeesun et al. (2024) demonstrated that GE indices can measure group fairness in ML contexts, they employed these metrics only for post-hoc evaluation, not as training objectives. No prior work has incorporated economic inequality indices as differentiable regularization terms in neural network training.

**Gap 2: Theoretical Grounding.** Many fairness interventions rely on ad-hoc constraints or heuristics without deep theoretical justification. The rich theoretical foundation of economic inequality measurement—connecting to egalitarian principles, social welfare functions, and distributive justice—remains untapped in machine learning fairness research.

**Gap 3: Multi-dimensional Representation.** Current approaches typically address representation inequality along a single dimension (sample count), ignoring that effective representation encompasses multiple facets: not just how many samples exist for a group, but how well those samples cover the feature space and capture label diversity.

### 2.3 Research Objectives

This research aims to bridge economics and machine learning by developing a novel training framework that incorporates Generalized Entropy indices as differentiable regularization terms in neural network loss functions. Specifically, we will:

1. **Develop a theoretically-grounded fairness regularization framework** that adapts GE indices from economics for use as training objectives in medical machine learning, creating gradient-based optimization pressure toward equitable representation.

2. **Operationalize multi-dimensional representation inequality** by defining a three-dimensional "representation wealth" vector capturing sample count, feature space coverage, and label diversity across demographic groups.

3. **Adapt small-sample bias corrections** from econometrics (jackknife methods) to handle minority groups in ML training contexts, ensuring robust inequality measurement even for underrepresented populations.

4. **Empirically validate the approach** on medical datasets (MIMIC-III hospital data, UK Biobank) targeting ≥30% reduction in representation inequality while maintaining clinical accuracy (AUROC ≥0.80).

5. **Characterize the fairness-accuracy tradeoff** through systematic hyperparameter analysis, providing practitioners with explicit control mechanisms via the regularization coefficient λ.

### 2.4 Research Hypothesis

**Main Hypothesis:** If we incorporate Generalized Entropy (GE) inequality indices as differentiable regularization terms in the training loss function ($L_{total} = L_{task} + \lambda \cdot GE_\alpha$), then medical ML models will exhibit reduced representation inequality across demographic groups (measured by post-training Gini coefficient and Demographic Parity gaps), because the GE indices quantitatively penalize models that amplify data imbalances during gradient descent, creating optimization pressure toward equitable representation distribution.

**Causal Mechanism:** During backpropagation, the gradient $\frac{\partial L_{total}}{\partial \theta} = \frac{\partial L_{task}}{\partial \theta} + \lambda \cdot \frac{\partial GE_\alpha}{\partial \theta}$ creates dual pressure on model parameters. As predictions shift during training, group-wise representation distributions evolve. When representation becomes skewed (GE increases), the gradient magnitude from the inequality term grows, steering parameter updates toward configurations that balance representation across groups. This training-time feedback mechanism allows models to learn fair representations from initialization, rather than retrofitting fairness after biased learning.

### 2.5 Significance

This research addresses critical challenges at the intersection of machine learning and global health:

**Health Equity Impact:** By directly addressing biomedical data inequality, this work could reduce algorithmic harm to non-European populations and other underrepresented groups, contributing to more equitable healthcare delivery globally.

**Methodological Innovation:** The framework provides the first application of distributive justice theory from economics to ML training objectives, opening new research directions connecting economics, statistics, and fairness communities.

**Practical Deployability:** Unlike methods requiring expensive additional data collection, this approach works with existing datasets and integrates seamlessly into standard ML frameworks, providing practitioners with tunable fairness-accuracy tradeoff control.

**Policy Relevance:** The quantitative inequality metrics provide concrete tools for evaluating and enforcing equitable AI in healthcare regulation, supporting evidence-based policy development.

**Pandemic Preparedness:** By improving ML model performance across diverse populations, this work contributes to more robust and equitable disease surveillance, risk prediction, and resource allocation systems for future public health emergencies.

## 3. Methodology

### 3.1 Research Design Overview

We employ a mixed-methods approach combining algorithm development, theoretical analysis, and empirical validation through controlled experiments on medical datasets. The research proceeds in four phases: (1) mathematical formulation and implementation, (2) small-scale validation experiments, (3) large-scale benchmark evaluation, and (4) sensitivity and generalization analysis.

### 3.2 Mathematical Formulation

#### 3.2.1 Generalized Entropy Indices

The Generalized Entropy family of inequality indices is defined as:

$$GE_\alpha(x) = \frac{1}{\alpha(\alpha-1)} \left[ \frac{1}{n} \sum_{i=1}^{n} \left(\frac{x_i}{\mu}\right)^\alpha - 1 \right]$$

where $x = (x_1, ..., x_n)$ represents the distribution of a resource across $n$ units, $\mu = \frac{1}{n}\sum_{i=1}^{n} x_i$ is the mean, and $\alpha$ is a sensitivity parameter. Special cases include:

- $\alpha = 0$ (Theil-L index, bottom-sensitive): $GE_0 = \frac{1}{n} \sum_{i=1}^{n} \ln\left(\frac{\mu}{x_i}\right)$
- $\alpha = 1$ (Theil-T index, top-sensitive): $GE_1 = \frac{1}{n} \sum_{i=1}^{n} \frac{x_i}{\mu} \ln\left(\frac{x_i}{\mu}\right)$
- $\alpha = 2$ (half coefficient of variation squared): $GE_2 = \frac{1}{2}\left[\frac{1}{n}\sum_{i=1}^{n}\left(\frac{x_i}{\mu}\right)^2 - 1\right]$

The index equals 0 for perfect equality and increases with inequality, with no upper bound.

#### 3.2.2 Multi-Dimensional Representation Wealth

For $K$ demographic groups, we define a three-dimensional representation wealth vector for group $g$:

$$R_g = (R_g^{count}, R_g^{coverage}, R_g^{diversity})$$

where:

1. **Sample Count:** $R_g^{count} = n_g$ (number of samples in group $g$)

2. **Feature Coverage:** $R_g^{coverage} = \frac{|\mathcal{F}_g|}{|\mathcal{F}_{total}|}$, where $\mathcal{F}_g$ represents the feature space volume occupied by group $g$ samples, operationalized as:
   $$|\mathcal{F}_g| = \prod_{j=1}^{d} (\max_{i \in g} x_{ij} - \min_{i \in g} x_{ij})$$
   for $d$-dimensional feature space.

3. **Label Diversity:** $R_g^{diversity} = H(Y_g) = -\sum_{c=1}^{C} p_g(c) \log p_g(c)$, the Shannon entropy of the label distribution within group $g$ for $C$ classes.

#### 3.2.3 Composite Inequality Regularization

The total training loss combines task-specific loss with inequality regularization:

$$L_{total}(\theta) = L_{task}(\theta) + \lambda \sum_{d \in \{count, coverage, diversity\}} w_d \cdot GE_\alpha(R^d)$$

where:
- $\theta$ represents model parameters
- $L_{task}$ is the standard task loss (e.g., binary cross-entropy for classification)
- $\lambda > 0$ is the regularization coefficient controlling the fairness-accuracy tradeoff
- $w_d$ are dimension weights (default: $w_d = 1/3$ for equal weighting)
- $R^d = (R_1^d, ..., R_K^d)$ is the vector of dimension $d$ values across $K$ groups

#### 3.2.4 Small-Sample Bias Correction

For groups with $n_g < 100$ samples, we apply jackknife bias correction following De Nicolò et al. (2021):

$$\widehat{GE}_\alpha^{corrected}(R_g) = n_g \cdot \widehat{GE}_\alpha(R_g) - \frac{n_g - 1}{n_g} \sum_{i=1}^{n_g} \widehat{GE}_\alpha(R_g^{(-i)})$$

where $R_g^{(-i)}$ denotes the representation vector with the $i$-th sample removed. This correction reduces bias in inequality estimates for small samples.

#### 3.2.5 Gradient Computation

The gradient of the total loss with respect to model parameters is:

$$\frac{\partial L_{total}}{\partial \theta} = \frac{\partial L_{task}}{\partial \theta} + \lambda \sum_d w_d \frac{\partial GE_\alpha(R^d)}{\partial \theta}$$

The inequality gradient decomposes via chain rule:

$$\frac{\partial GE_\alpha(R^d)}{\partial \theta} = \sum_{g=1}^{K} \frac{\partial GE_\alpha}{\partial R_g^d} \cdot \frac{\partial R_g^d}{\partial \theta}$$

For differentiability, we compute $R_g^d$ from model predictions $\hat{y}$ rather than hard labels, enabling gradient flow through the representation statistics.

### 3.3 Data Collection and Preparation

#### 3.3.1 Datasets

**Primary Dataset: MIMIC-III Clinical Database**
- **Description:** De-identified health records from 40,000+ ICU patients at Beth Israel Deaconess Medical Center (2001-2012)
- **Task:** 30-day hospital readmission prediction (binary classification)
- **Demographics:** Race/ethnicity (White, Black, Hispanic, Asian, Other), sex, age groups
- **Features:** Vital signs, lab values, medications, diagnoses (ICD-9 codes), procedures
- **Sample Size:** N = 40,000 patients after preprocessing
- **Access:** Publicly available via PhysioNet with credentialing

**Secondary Dataset: UK Biobank**
- **Description:** Prospective cohort study with 500,000+ participants
- **Task:** Cardiovascular disease risk prediction
- **Demographics:** Ethnicity (White British, South Asian, Black, Chinese, Mixed), sex, age
- **Features:** Genetic data, biomarkers, lifestyle factors, medical history
- **Sample Size:** N = 100,000 subset with complete demographic labels
- **Access:** Approved researcher access required

**Synthetic Dataset (Controlled Experiments)**
- **Description:** Simulated medical data with controlled representation imbalance
- **Purpose:** Ablation studies isolating specific inequality patterns
- **Generation:** Gaussian mixture models with varying group sizes, feature overlap, label distributions
- **Sample Size:** N = 10,000 per configuration

#### 3.3.2 Preprocessing Pipeline

1. **Missing Data Handling:** Multiple imputation by chained equations (MICE) for <20% missingness; exclude features with >20% missing
2. **Feature Engineering:** Extract temporal features (time since admission, trend slopes), aggregate lab values (mean, std, min, max over ICU stay)
3. **Normalization:** Z-score standardization per feature across training set
4. **Demographic Label Validation:** Manual review of demographic coding consistency; exclude records with ambiguous/missing demographic labels
5. **Train/Validation/Test Split:** 60%/20%/20% stratified by demographic groups and outcome labels

### 3.4 Implementation Details

#### 3.4.1 Model Architecture

**Base Model:** Multilayer Perceptron (MLP) for tabular data
- Input layer: dimension = number of features
- Hidden layers: 3 layers with [256, 128, 64] units
- Activation: ReLU
- Dropout: 0.3 after each hidden layer
- Output layer: sigmoid activation for binary classification

**Framework:** PyTorch 2.0 with automatic differentiation

#### 3.4.2 Training Procedure

```
Algorithm: GE-Regularized Training

Input: Training data D = {(x_i, y_i, g_i)}, hyperparameters λ, α
Output: Trained model parameters θ*

1. Initialize model parameters θ randomly
2. For epoch = 1 to max_epochs:
   3. For each mini-batch B:
      4. Forward pass: compute predictions ŷ = f(x; θ)
      5. Compute task loss: L_task = BCE(ŷ, y)
      6. Compute group-wise representation:
         For each group g:
            R_g^count = |{i ∈ B : g_i = g}|
            R_g^coverage = feature_space_volume(x[g_i = g])
            R_g^diversity = entropy(ŷ[g_i = g])
      7. Compute GE indices:
         For d ∈ {count, coverage, diversity}:
            GE_α(R^d) = generalized_entropy(R^d, α)
            If any n_g < 100: apply jackknife_correction()
      8. Compute total loss:
         L_total = L_task + λ * mean(GE_α(R^count), GE_α(R^coverage), GE_α(R^diversity))
      9. Backward pass: compute ∂L_total/∂θ
      10. Update parameters: θ ← θ - η * ∂L_total/∂θ
   11. Evaluate on validation set
   12. If validation loss plateaus for 10 epochs: early stopping
13. Return θ*
```

**Hyperparameters:**
- Learning rate: η = 0.001 (Adam optimizer)
- Batch size: 256
- Max epochs: 100
- Early stopping patience: 10 epochs
- λ search space: [0.001, 0.01, 0.1, 1.0, 10.0] (log scale)
- α values: {0, 0.5, 1.0}

### 3.5 Experimental Design

#### 3.5.1 Experiment 1: Baseline Comparison

**Objective:** Compare GE regularization against established fairness methods

**Conditions:**
1. **Standard ERM:** Minimize $L_{task}$ only (no fairness intervention)
2. **Inverse Sample Weighting:** Weight loss by $1/n_g$ per group
3. **Post-hoc Demographic Parity:** Adjust decision thresholds per group after training
4. **Reweighting (Kamiran & Calders 2012):** Pre-process data to balance groups
5. **Fairness Constraints (Agarwal et al. 2018):** Lagrangian optimization with DP constraints
6. **FairLearn ExponentiatedGradient:** State-of-the-art fairness toolkit
7. **GE Regularization (Proposed):** $\lambda = 0.1$, $\alpha = 0.5$

**Procedure:**
- Train each method on MIMIC-III with 5-fold cross-validation
- Stratified sampling ensuring each fold maintains demographic proportions
- Fixed random seeds for reproducibility
- Hyperparameter tuning via grid search on validation set

**Evaluation Metrics:**

*Fairness Metrics:*
- **Demographic Parity Gap:** $\max_g P(\hat{y}=1|g) - \min_g P(\hat{y}=1|g)$
- **Equalized Odds Gap:** $\max_g |P(\hat{y}=1|y=1,g) - P(\hat{y}=1|y=1)|$
- **GE Index (post-training):** $GE_{0.5}(R^{count}, R^{coverage}, R^{diversity})$
- **Max/Min Ratio:** $\frac{\max_g \text{AUROC}_g}{\min_g \text{AUROC}_g}$

*Accuracy Metrics:*
- **Overall AUROC:** Area under ROC curve on full test set
- **Per-Group AUROC:** AUROC computed separately for each demographic group
- **Sensitivity (Recall):** Per-group true positive rate
- **Specificity:** Per-group true negative rate
- **F1-Score:** Harmonic mean of precision and recall

**Statistical Testing:**
- Paired two-sample t-test comparing GE method vs. each baseline on fairness metrics
- Bonferroni correction for multiple comparisons: $p_{threshold} = 0.05/6 \approx 0.008$
- Cohen's d effect size calculation (target: $d \geq 0.5$)
- Two one-sided tests (TOST) for accuracy equivalence (within ±5% of best baseline)

#### 3.5.2 Experiment 2: Hyperparameter Sensitivity Analysis

**Objective:** Characterize fairness-accuracy tradeoff and parameter sensitivity

**Design:** Full factorial grid search
- $\lambda \in \{0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0\}$ (9 values)
- $\alpha \in \{0, 0.5, 1.0\}$ (3 values)
- Total: 27 configurations

**Analysis:**
1. **Pareto Frontier:** Plot fairness vs. accuracy for all configurations; identify Pareto-optimal points
2. **α Sensitivity:** Compare $\alpha=0$ (bottom-sensitive) vs. $\alpha=1$ (top-sensitive) on smallest minority group performance
3. **λ Trajectory:** Plot fairness and accuracy as functions of $\lambda$; fit power-law curves
4. **Interaction Effects:** Two-way ANOVA testing $\lambda \times \alpha$ interaction on fairness metrics

#### 3.5.3 Experiment 3: Small-Sample Correction Validation

**Objective:** Validate jackknife correction for minority groups

**Design:** Controlled subsampling
- Create artificial minority groups by subsampling MIMIC-III to $n \in \{20, 50, 100, 200, 500\}$
- Train with and without jackknife correction
- Measure variance in fairness metrics across 10 random subsamples

**Metrics:**
- Coefficient of variation (CV) in GE estimates: $CV = \sigma/\mu$
- Bias: difference between corrected and uncorrected GE
- Target: ≥20% reduction in CV with correction for $n < 100$

#### 3.5.4 Experiment 4: Generalization Across Domains

**Objective:** Test method transferability to different medical tasks

**Datasets:**
1. **MIMIC-III:** Hospital readmission (tabular EHR)
2. **UK Biobank:** CVD risk prediction (tabular + genetic)
3. **CheXpert:** Chest X-ray diagnosis (medical imaging)

**Procedure:**
- Apply optimal hyperparameters from MIMIC-III to UK Biobank and CheXpert
- Measure relative fairness improvement: $\frac{\Delta \text{Fairness}_{new}}{\Delta \text{Fairness}_{MIMIC}}$
- Target: ≥50% effectiveness on new domains

#### 3.5.5 Experiment 5: Temporal Validation

**Objective:** Assess fairness stability over time

**Design:**
- Train on MIMIC-III 2008-2012 data
- Test on 2013-2016 data (temporal hold-out)
- Measure fairness metric drift over time

**Metrics:**
- Temporal fairness degradation: $|\text{Fairness}_{2013-16} - \text{Fairness}_{2008-12}|$
- Compare GE method vs. baselines on temporal stability

### 3.6 Validation and Reproducibility

**Power Analysis:**
- Minimum detectable effect size: $d = 0.5$ (medium effect)
- Statistical power: 0.80
- Significance level: $\alpha = 0.05$
- Required sample size: $N \geq 8,000$ (G*Power calculation)
- MIMIC-III ($N = 40,000$) provides sufficient power

**Reproducibility Measures:**
1. Fixed random seeds (42 for all experiments)
2. Open-source code release on GitHub with MIT license
3. Detailed hyperparameter configurations in supplementary materials
4. Docker container with exact software environment
5. Training logs and checkpoints archived
6. Report mean ± standard deviation across 5 CV folds

**Falsification Criteria:**

The hypothesis is **falsified** if any of:
1. GE regularization produces <10% fairness improvement over baseline ERM
2. Accuracy drops >15% at fairness-optimal $\lambda$
3. Post-training $GE_{0.5}$ index is higher than baseline
4. No statistically significant difference ($p > 0.05$) in Demographic Parity vs. post-hoc correction
5. Method fails to converge on ≥2 out of 3 test datasets

## 4. Expected Outcomes & Impact

### 4.1 Primary Expected Outcomes

**Quantitative Performance Targets:**

1. **Fairness Improvement:** ≥30% reduction in post-training $GE_{0.5}$ index compared to standard ERM baseline, measured across MIMIC-III test set

2. **Demographic Parity:** ≥40% reduction in Demographic Parity gap (max-min positive rate across groups), from baseline ~0.12 to ≤0.07

3. **Accuracy Preservation:** Maintain overall AUROC ≥0.80 with ≤5% accuracy drop from baseline, ensuring clinical utility

4. **Per-Group Performance:** Reduce max/min AUROC ratio across demographic groups from ~1.4 to ≤1.2, indicating more balanced performance

5. **Statistical Significance:** Achieve $p < 0.008$ (Bonferroni-corrected) on paired t-tests comparing GE method vs. ≥4 out of 6 baseline methods

**Methodological Contributions:**

1. **Novel Training Framework:** First implementation of economic inequality indices as differentiable loss terms in neural network training, with open-source PyTorch implementation (~500 lines of code)

2. **Multi-Dimensional Inequality Measurement:** Validated operationalization of 3D representation wealth (count, coverage, diversity) capturing richer inequality structure than sample count alone

3. **Small-Sample Adaptation:** Demonstrated effectiveness of jackknife bias correction from econometrics in ML mini-batch contexts, enabling robust fairness for minority groups

4. **Fairness-Accuracy Characterization:** Empirical Pareto frontier mapping the tradeoff space, providing practitioners with decision-support tools for selecting appropriate $\lambda$ values based on application requirements

### 4.2 Theoretical Contributions

**Bridging Economics and Machine Learning:**

This research establishes formal connections between distributive justice theory (70+ years of economic research) and machine learning fairness. By grounding fairness interventions in social welfare optimization principles, we provide theoretical justification beyond empirical correlation for why representation inequality matters. This opens new research directions:

- **Axiomatic Fairness:** Leveraging economic axioms (scale invariance, transfer principle, decomposability) to design ML fairness metrics with desirable mathematical properties
- **Welfare-Theoretic ML:** Connecting model optimization to social welfare functions, enabling explicit encoding of egalitarian vs. utilitarian objectives
- **Inequality Dynamics:** Applying economic theories of inequality evolution to understand how representation gaps emerge and persist during training

**Causal Mechanism Validation:**

The research will provide empirical evidence for the causal chain: GE regularization → gradient pressure → balanced representation → improved fairness. By decomposing this mechanism through ablation studies (Experiment 2), we validate each link, contributing to mechanistic understanding of fairness interventions rather than black-box empiricism.

### 4.3 Practical Impact

**Healthcare Equity:**

By reducing algorithmic bias against underrepresented populations, this work directly addresses health disparities documented by Gao et al. (2023). Potential applications include:

- **Clinical Decision Support:** More equitable risk prediction for hospital readmission, mortality, sepsis across racial/ethnic groups
- **Resource Allocation:** Fair prioritization of ICU beds, organ transplants, specialist referrals during resource scarcity
- **Pandemic Preparedness:** Equitable disease surveillance and outbreak prediction across diverse communities, addressing COVID-19 lessons

**Deployability:**

The framework integrates seamlessly into existing ML pipelines:
- Compatible with standard frameworks (PyTorch, TensorFlow)
- Minimal computational overhead (~10% training time increase)
- No additional data collection required
- Tunable tradeoff via single hyperparameter $\lambda$

This lowers adoption barriers for healthcare institutions and ML practitioners.

**Regulatory and Policy Applications:**

The quantitative inequality metrics provide concrete tools for:
- **Algorithmic Auditing:** Regulatory bodies can measure and enforce fairness standards using GE indices
- **Certification Standards:** Establishing thresholds (e.g., $GE_{0.5} < 0.1$) for medical AI deployment approval
- **Transparency Requirements:** Mandating reporting of representation inequality alongside accuracy in clinical validation studies

### 4.4 Broader Impact on Global Health

**Addressing Workshop Themes:**

1. **COVID-19 Lessons:** The pandemic revealed how algorithmic bias in risk prediction and resource allocation disproportionately harmed minority communities. This work provides tools to prevent such inequities in future health emergencies.

2. **ML Applicability in Global Health:** Demonstrates that ML can be useful for health equity when combined with domain-appropriate fairness interventions, while acknowledging limitations (requires demographic labels, may not address all fairness definitions).

3. **Data Sharing Practices:** By working with existing data rather than requiring new collection, the method is compatible with privacy-preserving practices. Future work could extend to federated learning contexts.

4. **Proactive Pandemic Response:** Equitable disease surveillance models enable early detection of outbreaks in underserved communities, supporting proactive rather than reactive public health.

**Scalability to Low-Resource Settings:**

While initial validation uses US/UK datasets, the framework is particularly relevant for global health contexts where data inequality is even more severe:

- **Low- and Middle-Income Countries (LMICs):** Often underrepresented in training data; GE regularization could improve model performance when deployed in these settings
- **Rare Diseases:** Small patient populations benefit from small-sample bias corrections
- **Multi-Country Studies:** GE decomposability enables measuring within-country and between-country inequality simultaneously

### 4.5 Limitations and Future Directions

**Known Limitations:**

1. **Demographic Label Requirement:** Method requires protected attributes during training, raising privacy concerns for clinical deployment (mitigated in research settings)
2. **Single-Axis Fairness:** Current formulation addresses one demographic dimension at a time; intersectional fairness (race × sex × age) requires extension
3. **Fairness Definition Scope:** Focuses on group fairness (demographic parity, equalized odds); does not address individual fairness or counterfactual fairness
4. **Computational Cost:** Per-epoch GE computation adds overhead; may be prohibitive for very large-scale models (>1B parameters)

**Future Research Directions:**

1. **Intersectional Extension:** Develop hierarchical GE decomposition for intersectional groups without exponential complexity
2. **Dynamic Regularization:** Investigate curriculum learning approaches where $\lambda$ increases during training
3. **Federated Fairness:** Adapt GE regularization for federated learning contexts where demographic labels cannot be centralized
4. **Causal Fairness:** Combine GE regularization with causal inference to address confounding and ensure counterfactual fairness
5. **Multi-Task Learning:** Extend to joint optimization across multiple clinical tasks (e.g., predict multiple diagnoses simultaneously)
6. **Interpretability:** Develop visualization tools explaining to clinicians how GE regularization improves fairness

### 4.6 Dissemination and Knowledge Translation

**Academic Outputs:**
- Peer-reviewed publication in top-tier ML conference (NeurIPS, ICML) or medical informatics journal (JAMIA, npj Digital Medicine)
- Workshop presentation at ML & Global Health workshop
- Open-source software package with documentation and tutorials

**Practitioner Engagement:**
- Webinar series for healthcare data scientists
- Integration with popular ML fairness toolkits (FairLearn, AIF360)
- Case studies with partner healthcare institutions

**Policy Impact:**
- White paper for regulatory agencies (FDA, EMA) on algorithmic fairness standards
- Testimony to health equity task forces
- Collaboration with WHO on global health AI guidelines

### 4.7 Success Metrics

**Short-term (1 year):**
- Achieve quantitative performance targets (≥30% fairness improvement, ≤5% accuracy drop)
- Publish peer-reviewed paper with ≥10 citations within first year
- Release open-source implementation with ≥100 GitHub stars

**Medium-term (3 years):**
- Adoption by ≥3 healthcare institutions for clinical decision support systems
- Integration into ≥1 major ML fairness toolkit
- Follow-up work by ≥5 independent research groups

**Long-term (5 years):**
- Influence regulatory standards for medical AI fairness
- Demonstrate measurable reduction in health outcome disparities in deployed systems
- Establish economic inequality measurement as standard practice in ML fairness research

This research represents a critical step toward closing the gap between ML advances and equitable global health outcomes, directly addressing the workshop's mission to foster lasting connections between machine learning researchers, public health practitioners, and policymakers.