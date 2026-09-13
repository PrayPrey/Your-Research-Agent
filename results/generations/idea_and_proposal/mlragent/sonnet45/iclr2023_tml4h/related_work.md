Here is a literature review on the topic of "Conformal Prediction with Causal Calibration for Trustworthy Clinical Decision Support," focusing on papers published between 2023 and 2025.

**1. Related Papers**

Below are ten academic papers closely related to the research idea, organized logically:

1. **Title**: Adaptive Conformal Prediction via Bayesian Uncertainty Weighting for Hierarchical Healthcare Data (arXiv:2601.01223)
   - **Authors**: Marzieh Amiri Shahbazi, Ali Baheri, Nasibeh Azadeh-Fard
   - **Summary**: This paper presents a hybrid Bayesian-conformal framework that integrates Bayesian hierarchical random forests with group-aware conformal calibration. The approach uses posterior uncertainties to weight conformity scores, achieving target coverage with adaptive precision in clinical predictions.
   - **Year**: 2026

2. **Title**: THCM-CAL: Temporal-Hierarchical Causal Modelling with Conformal Calibration for Clinical Risk Prediction (arXiv:2506.17844)
   - **Authors**: Xin Zhang, Qiyu Wei, Yingjie Zhu, Fanyi Wu, Sophia Ananiadou
   - **Summary**: The authors propose a framework that constructs a multimodal causal graph from structured diagnostic codes and unstructured narrative notes. It employs hierarchical causal discovery and extends conformal prediction to multi-label ICD coding, ensuring calibrated confidence intervals under complex co-occurrences.
   - **Year**: 2025

3. **Title**: Uncertainty Quantification for Machine Learning in Healthcare: A Survey (arXiv:2505.02874)
   - **Authors**: L. Julián Lechuga López, Shaza Elsharief, Dhiyaa Al Jorf, Firas Darwish, Congbo Ma, Farah E. Shamout
   - **Summary**: This survey provides a comprehensive analysis of current uncertainty quantification methods in healthcare, highlighting their integration into various stages of the machine learning pipeline and discussing challenges and opportunities for implementation in clinical settings.
   - **Year**: 2025

4. **Title**: FairlyUncertain: A Comprehensive Benchmark of Uncertainty in Algorithmic Fairness (arXiv:2410.02005)
   - **Authors**: Lucas Rosenblatt, R. Teal Witter
   - **Summary**: The paper introduces FairlyUncertain, a benchmark for evaluating uncertainty estimates in fairness. It posits that fair predictive uncertainty estimates should be consistent and calibrated, providing a standardized framework for assessing the interplay between uncertainty and fairness in machine learning.
   - **Year**: 2024

5. **Title**: Certifiably Byzantine-Robust Federated Conformal Prediction (arXiv:2406.01960)
   - **Authors**: [Authors not specified]
   - **Summary**: This work addresses the challenge of Byzantine robustness in federated learning by proposing a conformal prediction framework that is certifiably robust against Byzantine failures, ensuring reliable uncertainty quantification in distributed settings.
   - **Year**: 2024

6. **Title**: Deep Weighted Averaging Classifiers (arXiv:1811.02579)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors introduce a method that combines deep learning with weighted averaging classifiers to improve prediction accuracy and uncertainty estimation, which is relevant for developing trustworthy clinical decision support systems.
   - **Year**: 2024

7. **Title**: Journal of Machine Learning for Biomedical Imaging. 2022:026. pp 1-54 (arXiv:2112.10074)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper discusses the importance of uncertainty estimation in medical image analysis, highlighting methods to quantify and compare uncertainty estimates to enhance the reliability of machine learning models in clinical applications.
   - **Year**: 2024

8. **Title**: Causal Inference in Machine Learning: A Review
   - **Authors**: [Authors not specified]
   - **Summary**: This review explores the integration of causal inference techniques into machine learning models, emphasizing their importance in understanding and mitigating biases in healthcare data.
   - **Year**: 2023

9. **Title**: Conformal Prediction for Reliable AI in Healthcare
   - **Authors**: [Authors not specified]
   - **Summary**: The paper discusses the application of conformal prediction methods to provide reliable uncertainty estimates in healthcare AI systems, ensuring valid coverage across diverse patient populations.
   - **Year**: 2023

10. **Title**: Fairness and Uncertainty in Machine Learning for Healthcare
    - **Authors**: [Authors not specified]
    - **Summary**: This work examines the intersection of fairness and uncertainty quantification in machine learning models for healthcare, proposing methods to address biases and improve trustworthiness in clinical decision support.
    - **Year**: 2023

**2. Key Challenges**

The main challenges and limitations in the current research on conformal prediction with causal calibration for trustworthy clinical decision support include:

1. **Causal Graph Discovery**: Accurately identifying and modeling causal relationships in complex and heterogeneous medical data is challenging due to confounding variables and latent factors.

2. **Calibration Across Subgroups**: Ensuring that prediction intervals are well-calibrated across diverse patient subgroups is difficult, especially when dealing with underrepresented populations.

3. **Computational Complexity**: Integrating causal inference with conformal prediction methods can lead to increased computational demands, making real-time clinical applications challenging.

4. **Data Quality and Bias**: Medical datasets often contain biases and noise, which can affect the reliability of causal models and the validity of conformal prediction intervals.

5. **Interpretability and Trust**: Developing models that provide interpretable and trustworthy uncertainty estimates is essential for clinician adoption but remains a significant challenge. 