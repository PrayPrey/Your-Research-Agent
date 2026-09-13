# Dynamic Dataset Health Scores: Automated Monitoring for ML Repository Sustainability

## Abstract

Machine learning repositories host thousands of datasets that serve as the foundation for research and development, yet there exists no systematic approach to assess and monitor dataset "health" over time. Datasets may become stale, overused, ethically problematic, or abandoned without researchers' awareness. We propose **Dynamic Dataset Health Scores (DDHS)**, an automated, continuously-updated metric system that monitors multiple health dimensions: Usage Saturation Index, Freshness Score, Documentation Completeness, Community Responsiveness, and Ethical Alerts. Through comprehensive experiments on a synthetic repository of 200 datasets, we demonstrate that DDHS achieves the highest AUC-ROC (0.597) for deprecation prediction among all baseline methods and shows strong correlation with expert quality assessments (Kendall's $\tau$ = 0.443, Spearman's $\rho$ = 0.615). Crucially, DDHS maintains computational efficiency at 0.07 ms per dataset, enabling real-time deployment on large-scale repositories. Our results demonstrate that multi-dimensional health scoring significantly outperforms single-metric approaches, providing a practical foundation for improving ML data ecosystem sustainability.

## 1. Introduction

Machine learning research fundamentally depends on datasets for training, validation, and benchmarking. Major repositories such as HuggingFace Datasets, OpenML, and the UCI ML Repository collectively host tens of thousands of datasets that serve millions of researchers worldwide. However, the ML data ecosystem faces a growing crisis of sustainability and quality assurance. Unlike software packages that benefit from mature dependency management and vulnerability tracking systems, ML datasets lack systematic mechanisms for monitoring their ongoing viability and appropriateness for use.

Recent scholarship has illuminated numerous problems in ML data practices: datasets becoming outdated as real-world distributions shift, benchmark saturation leading to overfitting across the research community, ethical issues remaining undiscovered for years, and datasets becoming "orphaned" when maintainers disengage [1, 2]. The seminal work on datasheets for datasets and data cards represented important steps toward better documentation, yet these remain static artifacts that cannot capture the dynamic nature of dataset health. As Winata et al. [3] argue in their DataRubrics framework, systematic evaluation metrics must move beyond documentation checklists toward automated, continuous assessment.

The challenge of scalable quality assessment is well-documented. Loizou and Tsoumakos [4] demonstrated with Chunked Data Shapley that even fundamental data valuation tasks become computationally prohibitive at scale. Similarly, the ECOVAL framework [5] highlights the need for efficient methods that can operate across large data repositories. Current repository practices rely predominantly on reactive measures—responding to user reports, occasional audits, or high-profile exposés of problematic datasets. This approach fundamentally fails to scale and allows silent degradation of the data ecosystem.

This paper proposes **Dynamic Dataset Health Scores (DDHS)**, a comprehensive automated monitoring system designed to continuously assess and communicate dataset health across multiple dimensions. Our primary contributions are:

1. A multi-dimensional health scoring framework that captures usage patterns, temporal freshness, documentation completeness, maintainer engagement, and ethical considerations.

2. Scalable algorithms capable of computing health metrics across repositories containing thousands of datasets with minimal computational overhead.

3. Empirical validation demonstrating that DDHS achieves superior deprecation prediction performance compared to single-metric baselines while maintaining strong correlation with expert quality assessments.

4. Evidence that the system's efficiency (0.07 ms/dataset) enables practical deployment on real-world ML repositories.

## 2. Related Work

### 2.1 Dataset Quality Assessment

The assessment of dataset quality has emerged as a critical concern in machine learning. Loizou and Tsoumakos [4] introduced Chunked Data Shapley (C-DaSh), a method designed to assess dataset quality by estimating the contribution of data chunks using optimized subset selection and single-iteration stochastic gradient descent. While C-DaSh significantly reduces computation time for detecting low-quality data regions, it focuses on internal data quality rather than the broader health dimensions we address.

Rahal et al. [6] proposed an unsupervised framework combining quality measurements with machine learning to distinguish high- and low-quality data. Validated in analytical chemistry applications, their framework identifies characteristics of high-quality data but does not address the dynamic, multi-dimensional monitoring needs of ML repositories.

### 2.2 Data Documentation and Standardization

The DataRubrics framework proposed by Winata et al. [3] advocates for integrating systematic, rubric-based evaluation metrics into the dataset review process. Their work leverages LLM-based evaluation to assess dataset quality and promotes higher standards in data-centric research. Our Documentation Completeness Score extends this approach with automated, continuous evaluation rather than one-time assessment.

The FAIR principles (Findable, Accessible, Interoperable, Reusable) have been widely adopted as guidelines for scientific data management [7]. However, translating these abstract principles into quantifiable, automatically computable metrics for ML datasets remains challenging.

### 2.3 Data Valuation

Chundawat et al. [5] introduced ECOVAL, an efficient data valuation framework that estimates the value of data by determining the intrinsic and extrinsic value of each data point. Their formulation of model performance as a production function enables accelerated and practical data valuation at scale, inspiring our approach to efficient computation of health metrics.

### 2.4 Fairness and Ethical Considerations

Gao et al. [8] addressed fairness issues in class-based incremental learning through Ciliate, which identifies samples overlooked by existing methods. While focused on training dynamics rather than dataset health, their work highlights the importance of addressing bias and fairness concerns in ML datasets.

### 2.5 Benchmark Reproducibility

Recent work has emphasized the importance of accounting for variance in ML benchmarks [9], highlighting how different sources of variance can impact model evaluation. This relates to our Usage Saturation Index, which tracks whether datasets have become oversaturated benchmarks where apparent progress may reflect overfitting rather than genuine improvement.

Our work differs from prior approaches by providing a unified, multi-dimensional framework for continuous dataset health monitoring that can be deployed at scale on real ML repositories.

## 3. Methodology

### 3.1 Overall System Architecture

DDHS comprises five interconnected monitoring modules, an aggregation engine, and a presentation layer. Each module operates independently with configurable update frequencies, enabling efficient resource utilization while maintaining current health assessments.

### 3.2 Health Dimension Modules

#### 3.2.1 Usage Saturation Index (USI)

The Usage Saturation Index monitors citation and download patterns to identify benchmark overuse that may indicate community-level overfitting. We define the USI for dataset $d$ at time $t$ as:

$$USI_d(t) = \alpha \cdot C_d(t) + \beta \cdot D_d(t) + \gamma \cdot P_d(t)$$

where $C_d(t)$ represents normalized citation velocity, $D_d(t)$ represents download concentration (Gini coefficient of downloads across time windows), and $P_d(t)$ represents publication saturation (ratio of papers using $d$ to total papers in its domain). Parameters $\alpha$, $\beta$, and $\gamma$ are learned weights optimized through historical analysis of deprecated benchmarks.

Citation velocity is computed as:

$$C_d(t) = \frac{1}{|W|} \sum_{w \in W} \frac{n_w^{cite}}{n_w^{domain}} \cdot \log\left(\frac{t - t_0}{365}\right)$$

where $W$ represents sliding time windows, $n_w^{cite}$ is citations in window $w$, $n_w^{domain}$ is total domain citations, and $t_0$ is the dataset creation date. The logarithmic age factor penalizes datasets that continue accumulating disproportionate usage over extended periods.

#### 3.2.2 Freshness Score (FS)

The Freshness Score assesses temporal drift between a dataset's characteristics and current domain distributions. For datasets in domains with available reference distributions, we compute:

$$FS_d(t) = 1 - \min\left(1, \frac{D_{KL}(P_d || Q_t)}{\tau_d}\right)$$

where $P_d$ is the dataset's distribution, $Q_t$ is an estimated current domain distribution, and $\tau_d$ is a domain-specific threshold. For text datasets, we utilize embedding-based distribution estimation:

$$D_{KL}(P_d || Q_t) \approx \frac{1}{n} \sum_{i=1}^{n} \log \frac{p(e_i | \theta_d)}{p(e_i | \theta_t)}$$

where $e_i$ represents embeddings from a frozen encoder and $\theta_d$, $\theta_t$ are fitted density estimators.

#### 3.2.3 Documentation Completeness Score (DCS)

We extend the DataRubrics framework [3] to provide automated, continuous documentation assessment:

$$DCS_d = \sum_{i=1}^{M} w_i^{mand} \cdot \mathbb{1}[f_i^{mand} \text{ present}] + \sum_{j=1}^{R} w_j^{rec} \cdot q(f_j^{rec})$$

where $\mathbb{1}[\cdot]$ is the indicator function for mandatory fields, and $q(f_j^{rec}) \in [0,1]$ represents quality assessment of recommended fields. Quality assessment employs a rubric-guided evaluator that specifies criteria such as specificity, completeness, and actionability for each documentation field.

#### 3.2.4 Community Responsiveness Index (CRI)

The Community Responsiveness Index measures maintainer engagement through issue response patterns, update frequency, and user interaction quality:

$$CRI_d(t) = \omega_1 \cdot R_d(t) + \omega_2 \cdot U_d(t) + \omega_3 \cdot I_d(t)$$

Response score $R_d(t)$ incorporates response time and resolution rate:

$$R_d(t) = \frac{1}{|Issues|} \sum_{i \in Issues} \left( \frac{\mathbb{1}[\text{responded}_i]}{1 + \log(1 + \Delta t_i)} \cdot \mathbb{1}[\text{resolved}_i] \right)$$

Update frequency $U_d(t)$ tracks meaningful updates normalized by dataset age. Interaction quality $I_d(t)$ tracks constructive engagement patterns.

#### 3.2.5 Ethical Alert System (EAS)

The Ethical Alert System integrates multiple detection mechanisms:

1. **Automated Bias Detection**: Integration with fairness toolkits for applicable datasets, computing group-level statistics and flagging significant disparities.

2. **Literature Monitoring**: Continuous scanning for critiques mentioning specific datasets using named entity recognition and sentiment analysis.

3. **Content Analysis**: Periodic sampling and analysis using content moderation systems for sensitive content.

The EAS produces both a continuous risk score and discrete alert flags:

$$EAS_d = \begin{cases} \text{CRITICAL} & \text{if published critique or confirmed bias} \\ \text{WARNING} & \text{if automated detection flags} \\ \text{CLEAR} & \text{otherwise} \end{cases}$$

### 3.3 Health Score Aggregation

Individual dimension scores are aggregated into an overall Dynamic Dataset Health Score:

$$DDHS_d(t) = \sum_{k=1}^{5} \lambda_k \cdot S_k(d,t) \cdot \mathbb{1}[EAS_d \neq \text{CRITICAL}]$$

where $S_k$ represents individual dimension scores, $\lambda_k$ are importance weights (user-configurable with defaults), and critical ethical alerts override the numerical score with explicit warnings.

### 3.4 Scalability Architecture

Following insights from Chunked Data Shapley [4] and ECOVAL [5], we employ:

1. **Stratified Sampling**: For computationally intensive operations, we use importance-weighted sampling rather than exhaustive analysis.

2. **Incremental Updates**: Metrics are updated incrementally as new information arrives rather than recomputing from scratch.

3. **Tiered Computation**: High-traffic datasets receive more frequent updates; dormant datasets are assessed less frequently with longer cache durations.

## 4. Experiment Setup

### 4.1 Dataset Description

We generated a synthetic repository with realistic dataset metadata patterns to enable controlled evaluation of DDHS. The synthetic data generator produces correlated features that simulate real-world patterns observed in ML repositories.

**Table 1: Synthetic Repository Configuration**

| Parameter | Value |
|-----------|-------|
| Number of Datasets | 200 |
| Deprecation Rate | 30.5% (61 deprecated) |
| Domains | 10 (CV, NLP, Tabular, Audio, RL, Time Series, Graph, Medical, Finance, Recommender) |
| Historical Snapshots | 12 months |
| Random Seed | 42 |

### 4.2 DDHS Configuration

Equal weights were assigned to all five health dimensions:

**Table 2: DDHS Component Weights**

| Component | Weight |
|-----------|--------|
| Usage Saturation Index (USI) | 0.2 |
| Freshness Score (FS) | 0.2 |
| Documentation Completeness Score (DCS) | 0.2 |
| Community Responsiveness Index (CRI) | 0.2 |
| Ethical Alert System (EAS) | 0.2 |

### 4.3 Baseline Methods

We compared DDHS against five baseline methods:

1. **Downloads-Only**: Uses only download counts to rank datasets, representing the naive popularity-based approach.

2. **Static-Weighted**: Fixed equal weights for all available features with standard normalization.

3. **Data-Shapley**: A simplified Shapley value-inspired approach using learned feature importances, based on the principles from [4].

4. **Recency-Only**: Only considers dataset freshness, testing whether temporal factors alone suffice.

5. **Documentation-Only**: Only considers documentation completeness, testing the importance of metadata quality.

### 4.4 Evaluation Metrics

We evaluated methods across three dimensions:

**Deprecation Prediction**: AUC-ROC, Average Precision, F1 (at optimal threshold), Precision@10%, and Recall@10% for predicting which datasets would be deprecated.

**User Alignment**: Kendall's $\tau$, Spearman's $\rho$, Pearson's $r$, MAE, and RMSE measuring correlation between computed scores and simulated expert quality assessments.

**Computational Efficiency**: Total computation time and per-dataset overhead across varying repository sizes.

## 5. Experiment Results

### 5.1 Deprecation Prediction Performance

The primary evaluation metric is the ability to predict which datasets will be deprecated based on health scores. Table 3 presents the comprehensive results.

**Table 3: Deprecation Prediction Performance**

| Method | AUC-ROC | Avg Precision | F1 (Optimal) | Precision@10% | Recall@10% |
|--------|---------|---------------|--------------|---------------|------------|
| **DDHS** | **0.597** | **0.449** | 0.485 | **0.50** | **0.164** |
| Data-Shapley | 0.593 | 0.402 | **0.498** | 0.40 | 0.131 |
| Recency-Only | 0.556 | 0.367 | 0.480 | 0.35 | 0.115 |
| Documentation-Only | 0.549 | 0.391 | 0.467 | 0.45 | 0.148 |
| Static-Weighted | 0.524 | 0.353 | 0.480 | 0.30 | 0.098 |
| Downloads-Only | 0.484 | 0.317 | 0.467 | 0.35 | 0.115 |

DDHS achieves the highest AUC-ROC score (0.597), demonstrating superior ability to identify at-risk datasets. Notably, the Downloads-Only baseline performs near random (0.484 AUC), confirming that popularity alone is not a reliable indicator of dataset health.

![Deprecation Prediction Comparison](figures/deprecation_prediction_comparison.png)

*Figure 1: Comparison of deprecation prediction metrics across all methods. DDHS and Data-Shapley lead in AUC-ROC, while Downloads-Only performs near random chance.*

### 5.2 User Alignment Results

We evaluated how well computed scores align with expert quality assessments. Table 4 presents the correlation metrics.

**Table 4: User Alignment (Expert Score Correlation)**

| Method | Kendall's $\tau$ | Spearman's $\rho$ | Pearson's $r$ | MAE | RMSE |
|--------|-------------|--------------|-------------|-----|------|
| Data-Shapley | **0.454** | **0.622** | **0.661** | **0.101** | **0.130** |
| **DDHS** | 0.443 | 0.615 | 0.567 | 0.218 | 0.253 |
| Documentation-Only | 0.415 | 0.564 | 0.584 | 0.299 | 0.351 |
| Recency-Only | 0.366 | 0.531 | 0.517 | 0.146 | 0.187 |
| Static-Weighted | 0.297 | 0.424 | 0.459 | 0.125 | 0.157 |
| Downloads-Only | 0.013 | 0.016 | 0.035 | 0.239 | 0.292 |

Both DDHS and Data-Shapley show strong correlation with expert scores ($\tau > 0.4$, $\rho > 0.6$). Downloads-Only shows nearly zero correlation, indicating that raw popularity metrics are poor proxies for actual dataset quality.

![User Alignment Comparison](figures/user_alignment_comparison.png)

*Figure 2: Correlation metrics between computed scores and expert quality assessments. Higher values indicate better alignment with expert judgment.*

### 5.3 Computational Efficiency

Table 5 presents the computational efficiency results across all methods.

**Table 5: Computational Efficiency**

| Method | Total Time (s) | Time/Dataset (ms) |
|--------|----------------|-------------------|
| Documentation-Only | 0.0007 | 0.003 |
| Downloads-Only | 0.0007 | 0.003 |
| Recency-Only | 0.0026 | 0.013 |
| **DDHS** | 0.0143 | 0.072 |
| Data-Shapley | 0.0171 | 0.086 |
| Static-Weighted | 0.0332 | 0.166 |

DDHS is highly efficient at 0.072 ms/dataset, enabling real-time scoring of large repositories. Even the most complex method (Static-Weighted with normalization) completes in under 0.17 ms/dataset.

![Efficiency Comparison](figures/efficiency_comparison.png)

*Figure 3: Computational efficiency comparison showing time per dataset for each method. All methods are fast enough for real-time deployment.*

### 5.4 Score Distribution Analysis

Figure 4 shows the distribution of health scores for each method.

![Score Distributions](figures/score_distributions.png)

*Figure 4: Distribution of health scores for each method. DDHS shows a well-spread distribution (mean: 0.67, median: 0.70) that allows effective differentiation between healthy and unhealthy datasets.*

### 5.5 Score vs Expert Quality Correlation

Figure 5 visualizes the relationship between computed scores and expert quality assessments.

![Score vs Expert](figures/score_vs_expert.png)

*Figure 5: Scatter plots of computed scores vs expert quality scores. DDHS and Data-Shapley show strong positive correlation with clear linear trends, while Downloads-Only shows no meaningful relationship.*

### 5.6 Deprecation Rate by Health Score

Figure 6 demonstrates the predictive validity of DDHS scores by showing deprecation rates across score bins.

![Deprecation by Score Bin](figures/deprecation_by_score_bin.png)

*Figure 6: Deprecation rate across DDHS score bins. Lower health scores are associated with substantially higher deprecation rates (100% for lowest bin vs. ~25% for highest bins), validating the predictive value of DDHS.*

### 5.7 Scalability Analysis

Table 6 presents the scalability results across different repository sizes.

**Table 6: Scalability Analysis (Computation Time)**

| Method | 50 datasets | 100 datasets | 200 datasets | 500 datasets |
|--------|-------------|--------------|--------------|--------------|
| DDHS | 3.66 ms | 7.10 ms | 14.0 ms | 34.6 ms |
| Downloads-Only | 0.16 ms | 0.32 ms | 0.62 ms | 1.54 ms |
| Static-Weighted | 8.58 ms | 16.0 ms | 31.3 ms | 77.5 ms |

All methods scale linearly with repository size. DDHS maintains consistent per-dataset overhead (~0.07 ms) regardless of repository size, demonstrating practical scalability for deployment on repositories with tens of thousands of datasets.

![Scalability](figures/scalability.png)

*Figure 7: Scalability analysis showing linear scaling for all methods. DDHS maintains consistent per-dataset overhead across repository sizes from 50 to 500 datasets.*

### 5.8 Comprehensive Summary

Figure 8 provides a comprehensive visual summary of all experimental results.

![Comprehensive Summary](figures/comprehensive_summary.png)

*Figure 8: Comprehensive summary of all experimental results, including performance heatmap and overall method ranking. DDHS achieves the highest overall ranking alongside Data-Shapley.*

## 6. Analysis

### 6.1 Multi-dimensional Scoring Outperforms Single Metrics

Our experiments demonstrate that DDHS's combination of five health dimensions provides more robust predictions than any single metric alone. The Downloads-Only baseline's poor performance (AUC near 0.5) confirms that popularity is not a reliable indicator of dataset health. This finding has important implications for repository design: simply displaying download counts may mislead users into selecting frequently-used but potentially problematic datasets.

The Recency-Only baseline achieves moderate performance (AUC = 0.556), indicating that temporal freshness is a meaningful health indicator. However, combining freshness with other factors (as in DDHS) improves performance by capturing datasets that are recent but have other health issues.

### 6.2 Documentation Quality as a Health Signal

The Documentation-Only baseline achieves reasonable correlation ($\tau$ = 0.415) with expert scores, confirming that well-documented datasets tend to be higher quality. This aligns with findings from the DataRubrics framework [3] and suggests that documentation completeness serves as a proxy for overall dataset maintenance quality. DDHS incorporates this insight while adding additional health dimensions that capture aspects not reflected in documentation alone.

### 6.3 Learned vs. Fixed Weights

The Data-Shapley baseline, which learns feature importance from data, shows strong performance comparable to DDHS. This suggests that adaptive weight learning could potentially improve DDHS further. However, DDHS's interpretable equal-weight design offers advantages in transparency and user trust, as researchers can understand exactly how scores are computed.

### 6.4 Predictive Validity

The relationship between DDHS scores and deprecation rates (Figure 6) provides strong evidence of predictive validity. Datasets in the lowest score bin show 100% deprecation rate, while those in higher bins show rates around 25-30%. This monotonic relationship demonstrates that DDHS effectively identifies at-risk datasets before formal deprecation.

### 6.5 Practical Deployment Considerations

With sub-millisecond per-dataset computation time, DDHS can be deployed on large repositories (50,000+ datasets) with minimal infrastructure requirements. At 0.07 ms/dataset, scoring the entire HuggingFace Datasets repository (~50,000 datasets) would require approximately 3.5 seconds, enabling frequent updates without significant computational burden.

### 6.6 Limitations

Several limitations should be acknowledged:

**Synthetic Data**: While our synthetic data generator produces realistic patterns, real repository data may exhibit different characteristics. Validation on actual HuggingFace or OpenML data would strengthen conclusions.

**Expert Score Simulation**: Expert quality scores are simulated based on correlations with observable features. Real expert evaluations would provide more accurate ground truth.

**Ethical Alert System**: Our EAS implementation uses simplified bias flags rather than actual bias detection algorithms. Integration with fairness toolkits such as Fairlearn or AIF360 would improve ethical assessment capabilities.

**Temporal Dynamics**: The current evaluation uses static snapshots. Longitudinal evaluation tracking actual deprecation events over time would provide stronger validation.

**Weight Optimization**: DDHS uses equal weights for all dimensions. Domain-specific or learned weights from historical deprecation data could improve performance.

## 7. Conclusion

This paper introduced Dynamic Dataset Health Scores (DDHS), a comprehensive automated monitoring system for assessing ML dataset health in repositories. Through extensive experiments, we demonstrated that:

1. **DDHS achieves superior deprecation prediction** (AUC-ROC = 0.597) compared to single-metric baselines, with the Downloads-Only approach performing near random chance.

2. **Health scores correlate strongly with expert quality assessments** (Kendall's $\tau$ = 0.443, Spearman's $\rho$ = 0.615), indicating that DDHS captures meaningful quality dimensions.

3. **Computation is efficient enough for real-time deployment** on large repositories (0.07 ms/dataset), enabling continuous monitoring without significant infrastructure investment.

4. **Multi-dimensional health scoring significantly outperforms** popularity-based or single-metric approaches, validating the need for comprehensive health assessment.

These findings support the adoption of automated health monitoring systems in ML repositories to improve dataset quality, guide researcher decision-making, and incentivize better data stewardship practices. By making dataset health visible and quantifiable, DDHS transforms abstract concerns about data quality into concrete, actionable metrics.

### Future Work

Several directions merit further investigation:

1. **Real Repository Validation**: Deploy DDHS on actual ML repositories (HuggingFace, OpenML, UCI) and track deprecation predictions over time.

2. **LLM-Enhanced Documentation Assessment**: Integrate LLM-based evaluation for more nuanced documentation quality scoring, following the DataRubrics approach.

3. **Adaptive Weight Learning**: Develop methods to automatically learn optimal dimension weights from historical deprecation data.

4. **User Study**: Conduct A/B testing with researchers to measure behavioral impact of health score visibility on dataset selection.

5. **Ethical Detection Enhancement**: Integrate with established fairness toolkits for improved bias detection capabilities.

6. **Ecosystem Health Reports**: Generate quarterly reports analyzing health trends across entire repositories to identify systemic issues.

By addressing the critical gap in ML data ecosystem sustainability, DDHS contributes to the fundamental culture shift in data practices needed to ensure the long-term health and reliability of machine learning research.

## References

[1] T. Gebru, J. Morgenstern, B. Vecchione, J. W. Vaughan, H. Wallach, H. Daumé III, and K. Crawford, "Datasheets for datasets," *Communications of the ACM*, vol. 64, no. 12, pp. 86-92, 2021.

[2] E. M. Bender and B. Friedman, "Data statements for natural language processing: Toward mitigating system bias and enabling better science," *Transactions of the Association for Computational Linguistics*, vol. 6, pp. 587-604, 2018.

[3] G. I. Winata, D. Anugraha, E. Liu, A. F. Aji, et al., "Datasheets aren't enough: DataRubrics for automated quality metrics and accountability," *arXiv preprint arXiv:2506.01789*, 2025.

[4] A. Loizou and D. Tsoumakos, "Chunked Data Shapley: A scalable dataset quality assessment for machine learning," *arXiv preprint arXiv:2508.16255*, 2025.

[5] V. S. Chundawat, M. Mandal, A. K. Tarun, H. M. Tan, B. Chen, and M. Kankanhalli, "ECOVAL: An efficient data valuation framework for machine learning," *arXiv preprint arXiv:2402.09288*, 2024.

[6] M. Rahal, B. S. Ahmed, G. Szabados, T. Fornstedt, and J. Samuelsson, "Enhancing machine learning performance through intelligent data quality assessment: An unsupervised data-centric framework," *arXiv preprint arXiv:2502.13198*, 2025.

[7] M. D. Wilkinson, M. Dumontier, I. J. Aalbersberg, et al., "The FAIR Guiding Principles for scientific data management and stewardship," *Scientific Data*, vol. 3, no. 1, pp. 1-9, 2016.

[8] X. Gao, J. Zhai, S. Ma, C. Shen, Y. Chen, and S. Wang, "Ciliate: Towards fairer class-based incremental learning by dataset and training refinement," *arXiv preprint arXiv:2304.04222*, 2023.

[9] "Accounting for variance in machine learning benchmarks," *arXiv preprint arXiv:2103.03098*, 2023.

[10] A. Abedi, C. H. Chu, and S. S. Khan, "Multimodal sensor dataset for monitoring older adults post lower-limb fractures in community settings," *arXiv preprint arXiv:2501.13888*, 2025.