## Related Work

**Related Papers**
1. **Title**: Addressing the Challenge of Biomedical Data Inequality: An Artificial Intelligence Perspective (Gao et al. 2023)
   - **Authors**: Gao et al.
   - **Summary**: Conceptual framework identifying low representation as health risk for non-European populations in biomedical data. Documented that biomedical data underrepresents non-European populations, creating health risk through biased ML models.
   - **Year**: 2023

2. **Title**: Randomized Clinical Trials of Machine Learning Interventions in Health Care (Plana et al. 2022)
   - **Authors**: Plana et al.
   - **Summary**: Systematic review finding only 41 ML RCTs exist in healthcare, with limited diverse inclusion. Documents deployment gap and limited generalizability due to restricted demographic representation.
   - **Year**: 2022

3. **Title**: Estimating Group Fairness Using Pairwise Similarity (Supeesun et al. 2024)
   - **Authors**: Supeesun et al.
   - **Summary**: Applied Generalized Entropy (GE) indices to ML fairness measurement as post-hoc metrics. Validated that GE indices capture group inequality in ML contexts and correlate with human fairness perception.
   - **Year**: 2024

4. **Title**: What Is the Point of Equality in Machine Learning Fairness? Beyond Equality of Opportunity (Kong 2025)
   - **Authors**: Kong
   - **Summary**: Provides philosophical grounding of ML fairness in distributive justice theory from economics. Demonstrates that distributive justice theory from economics applies to ML representation contexts.
   - **Year**: 2025

5. **Title**: Fairness Overfitting in Machine Learning: An Information-Theoretic Perspective (Laakom et al. 2025)
   - **Authors**: Laakom et al.
   - **Summary**: Information-theoretic proof that fairness achieved during training generalizes better than post-hoc corrections. Provides theoretical bound showing fairness generalization error is lower for training-time methods.
   - **Year**: 2025

6. **Title**: Small-Sample Bias Correction of Inequality Estimators in Complex Surveys (De Nicolò et al. 2021)
   - **Authors**: De Nicolò et al.
   - **Summary**: Developed Jackknife bias correction for GE indices in small samples (<100) in economic surveys. Shows correction reduces bias in GE estimates for samples under 100.
   - **Year**: 2021

7. **Title**: Algorithmic Accountability in Small Data: Sample-Size-Induced Bias Within Classification Metrics (Briscoe et al. 2025)
   - **Authors**: Briscoe et al.
   - **Summary**: Model-agnostic sample-size bias correction for classification metrics. Validates need for small-sample corrections in fairness evaluation contexts.
   - **Year**: 2025

8. **Title**: ChildGrowthMonitor (Welthungerhilfe GitHub)
   - **Authors**: Welthungerhilfe
   - **Summary**: Offline-first ML deployment system designed for resource-constrained settings. Demonstrates deployment architecture for equity-focused ML in low-resource environments.
   - **Year**: Not specified

9. **Title**: Reweighting (Kamiran & Calders 2012)
   - **Authors**: Kamiran and Calders
   - **Summary**: Baseline fairness method using sample reweighting to address demographic imbalances. Referenced as baseline comparison method.
   - **Year**: 2012

10. **Title**: Fairness constraints (Agarwal et al. 2018)
    - **Authors**: Agarwal et al.
    - **Summary**: Established approach for incorporating fairness constraints in machine learning training. Referenced as baseline comparison method.
    - **Year**: 2018

11. **Title**: FairLearn ExponentiatedGradient
    - **Authors**: Not specified
    - **Summary**: Established fairness library providing exponentiated gradient method for fair classification. Referenced as baseline comparison method.
    - **Year**: Not specified

12. **Title**: Differentiable Soft Sorting (Grover et al. ICML 2019)
    - **Authors**: Grover et al.
    - **Summary**: Developed soft-sorting approximations to make Gini coefficient differentiable. Demonstrates technical challenge in making non-differentiable fairness metrics trainable, which GE indices avoid.
    - **Year**: 2019

13. **Title**: Chen et al. (2024) - State-of-the-Art Reference
    - **Authors**: Chen et al.
    - **Summary**: Referenced as SOTA target for fairness methods in medical ML contexts. Used as benchmark baseline.
    - **Year**: 2024

**Key Challenges**
1. **Representation Inequality in Medical Data**: Biomedical data systematically underrepresents non-European populations, leading to biased ML models that create health risks for these groups (Gao et al. 2023, 32 citations).

2. **Limited Deployment with Diverse Populations**: Only 41 ML randomized clinical trials exist, with limited diverse inclusion, creating a deployment gap between model development and real-world generalizability (Plana et al. 2022, 130 citations).

3. **Data Collection Barriers**: Collecting more data from underrepresented groups is expensive, slow, and sometimes impossible (historical data, rare diseases), necessitating methods that work with existing imbalanced datasets.

4. **Post-Hoc vs Training-Time Fairness**: Prior work using inequality indices (GE) applied them only as post-hoc measurement metrics, not as training objectives. Post-hoc corrections generalize worse than training-time fairness interventions (Laakom et al. 2025).

5. **Differentiability Challenges**: Traditional fairness metrics like Gini coefficient require sorting operations that are non-differentiable, necessitating approximations with error (Grover et al. 2019). Need for naturally differentiable inequality measures.

6. **Small Sample Statistical Bias**: Minority groups with small sample sizes (<100) produce high-variance fairness metric estimates, leading to noisy gradient signals and unstable training (De Nicolò et al. 2021, Briscoe et al. 2025).

7. **Single-Dimensional Fairness Metrics**: Existing approaches often focus on sample count only, missing important aspects like feature coverage and label diversity, which can hide representation problems even when counts appear balanced.

8. **Fairness-Accuracy Tradeoff**: Fundamental tension exists between improving fairness (balancing representation) and maintaining task accuracy, requiring careful navigation of Pareto frontier.

9. **Cross-Domain Transfer Validity**: Uncertainty about whether inequality metrics designed for economic income distribution meaningfully capture representation inequality in ML contexts (addressed by Supeesun et al. 2024, Kong 2025).

10. **Deployment in Resource-Constrained Settings**: Medical AI fairness solutions must be deployable in low-resource environments without requiring extensive computational resources or additional data collection (ChildGrowthMonitor example).

11. **Multiple Testing and Statistical Power**: Testing fairness across multiple demographic groups, datasets, and metrics creates multiple testing challenges and requires sufficient sample sizes per group (≥30-100 samples) for statistical validity.

12. **Demographic Label Availability and Ethics**: Protected demographic attributes must be known, accurate, and ethically usable during training, which is context-dependent and raises privacy concerns for clinical deployment.
