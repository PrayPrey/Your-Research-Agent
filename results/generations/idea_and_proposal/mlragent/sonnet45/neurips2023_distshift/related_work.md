1. **Title**: SELFOOD: Self-Supervised Out-Of-Distribution Detection via Learning to Rank (arXiv:2305.14696)
   - **Authors**: Dheeraj Mekala, Adithya Samavedhi, Chengyu Dong, Jingbo Shang
   - **Summary**: This paper introduces SELFOOD, a self-supervised method for out-of-distribution (OOD) detection that requires only in-distribution samples. By framing OOD detection as an inter-document intra-label ranking problem, the authors propose a pairwise ranking loss (IDIL loss) to train classifiers. The method demonstrates effectiveness across various classifiers and datasets, highlighting its applicability in both coarse- and fine-grained settings.
   - **Year**: 2023

2. **Title**: Towards Robust Artificial Intelligence: Self-Supervised Learning Approach for Out-of-Distribution Detection (arXiv:2510.12713)
   - **Authors**: Wissam Salhab, Darine Ameyed, Hamid Mcheick, Fehmi Jaafar
   - **Summary**: This work presents a self-supervised learning approach to enhance AI system robustness by improving OOD detection without labeled data. Leveraging self-supervised principles and graph-theoretical techniques, the proposed method efficiently identifies and categorizes OOD samples, achieving an AUROC of 0.99 compared to existing state-of-the-art methods.
   - **Year**: 2025

3. **Title**: Model-Based Runtime Monitoring with Interactive Imitation Learning (arXiv:2310.17552)
   - **Authors**: Huihan Liu, Shivin Dass, Roberto Martín-Martín, Yuke Zhu
   - **Summary**: The authors introduce a model-based runtime monitoring algorithm that learns to predict errors from deployment data. Integrated into an interactive imitation learning framework, the method ensures trustworthy long-term deployment by enabling robots to self-monitor and predict errors during task execution, thereby reducing human supervision over time.
   - **Year**: 2023

4. **Title**: Time-Series Forecasting for Out-of-Distribution Generalization Using Invariant Learning (arXiv:2406.09130)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study addresses the challenge of distribution shifts in time-series forecasting by proposing an invariant learning approach. The method aims to improve out-of-distribution generalization, demonstrating superior performance across multiple datasets and metrics compared to existing distribution shift methods.
   - **Year**: 2024

5. **Title**: SSL-Cleanse: Trojan Detection and Mitigation in Self-Supervised Learning (arXiv:2303.09079)
   - **Authors**: Mengxin Zheng, Jiaqi Xue, Zihao Wang, Xun Chen, Qian Lou, Lei Jiang, Xiaofeng Wang
   - **Summary**: SSL-Cleanse is proposed as a solution to detect and mitigate backdoor threats in self-supervised learning (SSL) encoders. The method effectively identifies and addresses triggers in SSL encoders without requiring labeled data, achieving an average detection success rate of 82.2% on ImageNet-100 and reducing backdoor attack success rates to 0.3% post-mitigation.
   - **Year**: 2023

6. **Title**: Self-training with Noisy Student improves ImageNet classification (arXiv:1911.04252)
   - **Authors**: Qizhe Xie, Minh-Thang Luong, Eduard Hovy, Quoc V. Le
   - **Summary**: The authors present Noisy Student Training, a semi-supervised learning approach that enhances ImageNet classification accuracy. By iteratively training larger student models with noise added during learning, the method achieves 88.4% top-1 accuracy on ImageNet and demonstrates improved robustness on various test sets.
   - **Year**: 2020

7. **Title**: UNCERTAINTY AS A PREDICTOR: LEVERAGING SELF-SUPERVISED LEARNING FOR ZERO-SHOT MOS PREDICTION (arXiv:2312.15616)
   - **Authors**: Aditya Ravuri, Erica Cooper, Junichi Yamagishi
   - **Summary**: This paper explores the use of uncertainty measures derived from pre-trained self-supervised learning models, such as wav2vec, for zero-shot Mean Opinion Score (MOS) prediction. The study demonstrates that these uncertainty measures correlate with MOS scores, providing insights into audio quality assessment without the need for labeled data.
   - **Year**: 2023

8. **Title**: CADet: Fully Self-Supervised Out-Of-Distribution Detection With Contrastive Learning (arXiv:2210.01742)
   - **Authors**: Charles Guille-Escuret, Pau Rodriguez, David Vazquez, Ioannis Mitliagkas, Joao Monteiro
   - **Summary**: CADet introduces a fully self-supervised method for detecting out-of-distribution samples using contrastive learning. The approach pairs self-supervised contrastive learning with the maximum mean discrepancy (MMD) two-sample test, effectively identifying both unseen classes and adversarial perturbations without requiring labeled data.
   - **Year**: 2022

9. **Title**: SSD: A Unified Framework for Self-Supervised Outlier Detection (arXiv:2103.12051)
   - **Authors**: Vikash Sehwag, Mung Chiang, Prateek Mittal
   - **Summary**: SSD proposes a self-supervised framework for outlier detection that relies solely on unlabeled in-distribution data. By combining self-supervised representation learning with Mahalanobis distance-based detection in the feature space, SSD outperforms existing detectors based on unlabeled data and achieves performance comparable to supervised methods.
   - **Year**: 2021

10. **Title**: Uncertainty as a Predictor: Leveraging Self-Supervised Learning for Zero-Shot MOS Prediction (arXiv:2312.15616)
    - **Authors**: Aditya Ravuri, Erica Cooper, Junichi Yamagishi
    - **Summary**: This study investigates the use of uncertainty measures from pre-trained self-supervised learning models for zero-shot Mean Opinion Score (MOS) prediction. The findings suggest that these uncertainty measures can serve as effective proxies for audio quality assessment, particularly in low-resource settings.
    - **Year**: 2023

**Key Challenges**:

1. **Detection of Out-of-Distribution Prompts**: Accurately identifying when prompts induce distribution shifts remains challenging, especially without access to labeled OOD data.

2. **Uncertainty Quantification**: Developing reliable self-supervised methods to quantify uncertainty in model predictions is complex, particularly in the absence of labeled data.

3. **Dynamic Calibration Mechanisms**: Implementing effective strategies to dynamically adjust model behavior based on estimated shift severity without compromising performance is a significant hurdle.

4. **Preserving Pretraining Robustness**: Ensuring that adaptation methods do not degrade the robustness acquired during pretraining poses a substantial challenge.

5. **Generalization Across Domains**: Achieving consistent performance across diverse and specialized domains, such as biomedicine or law, without domain-specific labeled data is difficult. 