1. **Title**: Avoiding Spurious Correlations via Logit Correction (arXiv:2212.01433)
   - **Authors**: Sheng Liu, Xu Zhang, Nitesh Sekhar, Yue Wu, Prateek Singhal, Carlos Fernandez-Granda
   - **Summary**: This paper introduces the Logit Correction (LC) loss, a method designed to mitigate the impact of spurious correlations in machine learning models. By adjusting the sample logit, the LC loss aims to maximize group-balanced accuracy, thereby reducing reliance on spurious features. The authors demonstrate that their approach outperforms existing methods on multiple benchmarks without requiring access to spurious attribute labels.
   - **Year**: 2022

2. **Title**: Improving Group Robustness on Spurious Correlation via Evidential Alignment (arXiv:2506.11347)
   - **Authors**: Wenqian Ye, Guangtao Zheng, Aidong Zhang
   - **Summary**: This work presents Evidential Alignment, a framework that leverages uncertainty quantification to identify and suppress spurious correlations without the need for group annotations. By calibrating biased models through evidential calibration techniques, the method enhances group robustness across various architectures and data modalities.
   - **Year**: 2025

3. **Title**: Let Samples Speak: Mitigating Spurious Correlation by Exploiting the Clusterness of Samples (arXiv:2512.22874)
   - **Authors**: Weiwei Li, Junzhuo Liu, Yuanyuan Ren, Yuchen Zheng, Yahao Liu, Wen Li
   - **Summary**: The authors propose a data-oriented approach to mitigate spurious correlations by observing that samples influenced by spurious features tend to exhibit a dispersed distribution in the learned feature space. Their method involves identifying, neutralizing, and eliminating spurious features through a simple grouping strategy, resulting in improved worst-group accuracy on image and NLP debiasing benchmarks.
   - **Year**: 2025

4. **Title**: Spurious Correlations in Machine Learning: A Survey (arXiv:2402.12715)
   - **Authors**: Wenqian Ye, Guangtao Zheng, Xu Cao, Yunsheng Ma, Aidong Zhang
   - **Summary**: This survey provides a comprehensive review of spurious correlations in machine learning, offering a taxonomy of current methods for addressing this issue. It also summarizes existing datasets, benchmarks, and metrics, and discusses recent advancements and future challenges in the field.
   - **Year**: 2024

5. **Title**: Interpretability Beyond Feature Attribution: Quantitative Testing with Concept Activation Vectors (TCAV) (arXiv:1711.11279)
   - **Authors**: Been Kim, Martin Wattenberg, Justin Gilmer, Carrie Cai, James Wexler, Fernanda Viégas, Rory Sayres
   - **Summary**: The paper introduces Concept Activation Vectors (CAVs) and the TCAV technique, which quantify the influence of user-defined concepts on model predictions. This approach provides insights into model behavior beyond traditional feature attributions, facilitating the identification of spurious correlations.
   - **Year**: 2018

6. **Title**: Domain Generalization for Vision-based Driving (arXiv:2109.13858)
   - **Authors**: [Authors not specified]
   - **Summary**: This study addresses the challenge of domain generalization in vision-based driving by proposing a method that does not rely on domain knowledge, pixel reconstruction, or multiple model ensembling. The approach aims to improve the generalization ability of driving models across different domains, thereby reducing the impact of spurious correlations.
   - **Year**: 2021

7. **Title**: Fed-EINI: An Efficient and Interpretable Inference Framework for Decision Tree Ensembles in Vertical Federated Learning (arXiv:2105.09540)
   - **Authors**: Xiaolin Chen, Shuai Zhou, Kai Yang, Hao Fao, Hu Wang, Yongji Wang
   - **Summary**: The authors propose Fed-EINI, a framework that enhances the interpretability of decision tree ensembles in vertical federated learning by disclosing feature meanings while ensuring efficiency and accuracy. This approach aids in understanding and mitigating spurious correlations in federated learning scenarios.
   - **Year**: 2021

8. **Title**: The Alzheimer’s Disease Prediction Of Longitudinal Evolution (TADPOLE) Challenge (arXiv:2002.03419)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper presents the TADPOLE Challenge, which evaluates predictive models for Alzheimer's disease progression. The challenge highlights the importance of addressing spurious correlations in medical imaging and provides benchmarks for assessing model robustness.
   - **Year**: 2020

9. **Title**: Invariant Risk Minimization (arXiv:1907.02893)
   - **Authors**: Martin Arjovsky, Léon Bottou, Ishaan Gulrajani, David Lopez-Paz
   - **Summary**: The authors introduce Invariant Risk Minimization (IRM), a framework that aims to learn representations that are invariant across different environments, thereby reducing reliance on spurious correlations. IRM seeks to improve out-of-distribution generalization by focusing on causal features.
   - **Year**: 2019

10. **Title**: Learning to Discover and Mitigate Spurious Correlations in Image Classification (arXiv:2007.04250)
    - **Authors**: [Authors not specified]
    - **Summary**: This work proposes a method for discovering and mitigating spurious correlations in image classification by leveraging feature attribution techniques and model ensembles. The approach aims to identify non-causal features that models may rely on and adjust training accordingly.
    - **Year**: 2020

**Key Challenges:**

1. **Lack of Prior Knowledge**: Many existing methods for identifying spurious correlations require prior knowledge of potential spurious features or access to group labels, which are often unavailable in practice.

2. **Model Interpretability**: Understanding and interpreting the internal workings of complex models, especially deep neural networks, remains a significant challenge, hindering the identification of spurious correlations.

3. **Generalization Across Domains**: Ensuring that models generalize well across different domains and distributions is difficult, as spurious correlations may vary between datasets.

4. **Computational Efficiency**: Techniques such as model ensembling and complex attribution methods can be computationally intensive, making them less practical for large-scale applications.

5. **Human Verification**: Even when potential spurious correlations are identified, human verification is often required to confirm their validity, which can be time-consuming and subjective. 