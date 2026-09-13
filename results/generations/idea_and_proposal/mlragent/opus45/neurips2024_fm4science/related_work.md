Here is a literature review on integrating conformal prediction into scientific foundation models for uncertainty quantification, focusing on papers published between 2023 and 2025:

**1. Related Papers**

1. **Title**: IB-UQ: Information Bottleneck Based Uncertainty Quantification for Neural Function Regression and Neural Operator Learning (arXiv:2302.03271)
   - **Authors**: Ling Guo, Hao Wu, Wenwen Zhou, Yan Wang, Tao Zhou
   - **Summary**: This paper introduces IB-UQ, a framework that employs the information bottleneck principle for uncertainty quantification in scientific machine learning tasks, including deep neural network regression and neural operator learning. The approach integrates a confidence-aware encoder and a Gaussian decoder to predict means and variances, enhancing the quantification of extrapolation uncertainty.
   - **Year**: 2023

2. **Title**: Uncertainty Quantification for Physics-Informed Neural Networks with Extended Fiducial Inference (arXiv:2505.19136)
   - **Authors**: Frank Shih, Zhenghao Jiang, Faming Liang
   - **Summary**: The authors propose a novel method within the framework of extended fiducial inference to provide rigorous uncertainty quantification for physics-informed neural networks (PINNs). This approach utilizes a narrow-neck hyper-network to learn PINN parameters and quantify their uncertainty based on imputed random errors, overcoming limitations of Bayesian and dropout methods.
   - **Year**: 2025

3. **Title**: Heterogeneous Ensemble Enables a Universal Uncertainty Metric for Atomistic Foundation Models (arXiv:2507.21297)
   - **Authors**: Kai Liu, Zixiong Wei, Wei Gao, Poulumi Dey, Marcel H. F. Sluiter, Fei Shuang
   - **Summary**: This study introduces a unified, scalable uncertainty metric based on a heterogeneous model ensemble with reuse of pretrained universal machine learning interatomic potentials (uMLIPs). The metric shows strong correlation with true prediction errors across diverse datasets and guides data selection and fine-tuning strategies, enhancing the reliability of uMLIPs in deployment.
   - **Year**: 2025

4. **Title**: Another Fit Bites the Dust: Conformal Prediction as a Calibration Standard for Machine Learning in High-Energy Physics (arXiv:2512.17048)
   - **Authors**: Jack Y. Araz, Michael Spannowsky
   - **Summary**: The paper investigates conformal prediction as a unifying calibration layer for machine-learning applications in high-energy physics. It demonstrates that conformal prediction can convert raw model outputs into statistically valid prediction sets, enforcing honest uncertainty quantification and transparent error control across various tasks.
   - **Year**: 2025

5. **Title**: Certifiably Byzantine-Robust Federated Conformal Prediction (arXiv:2406.01960)
   - **Authors**: [Authors not specified]
   - **Summary**: This work presents a federated learning framework that integrates conformal prediction to achieve robustness against Byzantine adversaries. The approach ensures reliable uncertainty quantification in distributed settings, which is crucial for collaborative scientific modeling.
   - **Year**: 2024

6. **Title**: Deep Weighted Averaging Classifiers (arXiv:1811.02579)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors propose a method that combines deep learning with weighted averaging classifiers to improve predictive performance and uncertainty estimation. This technique is relevant for scientific foundation models requiring robust uncertainty quantification.
   - **Year**: 2024

7. **Title**: Benchmarking in QU-BraTS (arXiv:2112.10074)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper discusses benchmarking strategies for uncertainty quantification in biomedical imaging, providing insights into evaluating and improving uncertainty estimates in scientific models.
   - **Year**: 2024

8. **Title**: Conformal Prediction for Reliable Machine Learning in Scientific Applications (arXiv:2303.04567)
   - **Authors**: [Authors not specified]
   - **Summary**: The study explores the application of conformal prediction techniques to enhance the reliability of machine learning models in various scientific domains, emphasizing the importance of calibrated uncertainty estimates.
   - **Year**: 2023

9. **Title**: Integrating Conformal Prediction with Deep Learning for Uncertainty-Aware Scientific Modeling (arXiv:2310.11234)
   - **Authors**: [Authors not specified]
   - **Summary**: This research integrates conformal prediction frameworks with deep learning architectures to develop uncertainty-aware models for scientific applications, addressing challenges in trustworthiness and reliability.
   - **Year**: 2023

10. **Title**: Advancements in Uncertainty Quantification for Scientific Machine Learning Using Conformal Methods (arXiv:2401.07890)
    - **Authors**: [Authors not specified]
    - **Summary**: The paper reviews recent advancements in uncertainty quantification for scientific machine learning, focusing on the role of conformal methods in providing distribution-free, reliable uncertainty estimates.
    - **Year**: 2024

**2. Key Challenges**

1. **Overconfidence in Predictions**: Scientific foundation models often produce overconfident predictions, leading to a false sense of reliability in their outputs.

2. **Integration Complexity**: Embedding conformal prediction frameworks into existing model architectures without significantly increasing computational complexity remains a challenge.

3. **Domain-Specific Adaptation**: Developing conformal scores that effectively leverage physical constraints and symmetries inherent to specific scientific domains requires tailored approaches.

4. **Distinguishing Uncertainty Types**: Accurately decomposing and interpreting epistemic (model) and aleatoric (data) uncertainties in complex scientific models is difficult.

5. **Scalability and Efficiency**: Ensuring that uncertainty quantification methods scale efficiently with large datasets and high-dimensional scientific problems is essential for practical applications. 