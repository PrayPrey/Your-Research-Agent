1. **Title**: Differentially Private Federated Learning With Time-Adaptive Privacy Spending (arXiv:2502.18706)
   - **Authors**: Shahrzad Kiani, Nupur Kulkarni, Adam Dziedzic, Stark Draper, Franziska Boenisch
   - **Summary**: This paper introduces a time-adaptive differential privacy framework for federated learning, allowing clients to allocate their privacy budgets non-uniformly across training rounds. By spending less in early rounds and more in later ones, clients can improve model utility while maintaining privacy guarantees. The authors provide theoretical proofs and practical experiments demonstrating enhanced privacy-utility trade-offs compared to baseline methods.
   - **Year**: 2025

2. **Title**: Shift Happens: Mixture of Experts based Continual Adaptation in Federated Learning (arXiv:2506.18789)
   - **Authors**: Rahul Atul Bhope, K. R. Jayaram, Praveen Venkateswaran, Nalini Venkatasubramanian
   - **Summary**: Addressing distribution shifts in federated learning, this work presents ShiftEx, a mixture of experts framework that dynamically creates and trains specialized global models in response to detected shifts. Utilizing Maximum Mean Discrepancy for shift detection and a latent memory mechanism for expert reuse, the approach achieves significant accuracy improvements and faster adaptation in non-stationary environments.
   - **Year**: 2025

3. **Title**: An Adaptive Differential Privacy Method Based on Federated Learning (arXiv:2408.08909)
   - **Authors**: Zhiqiang Wang, Xinyue Yu, Qianli Huang, Yongguang Gong
   - **Summary**: This study proposes an adaptive differential privacy method in federated learning that adjusts the privacy budget based on factors like accuracy, loss, training rounds, and the number of datasets and clients. The method aims to reduce the overall privacy budget while maintaining model accuracy, achieving approximately a 16% reduction in privacy budget without significant accuracy loss.
   - **Year**: 2024

4. **Title**: Dordis: Efficient Federated Learning with Dropout-Resilient Differential Privacy (arXiv:2209.12528)
   - **Authors**: Zhifeng Jiang, Wei Wang, Ruichuan Chen
   - **Summary**: Dordis introduces a distributed differential privacy mechanism for federated learning that is resilient to client dropout. The 'add-then-remove' scheme ensures precise noise levels per training round, even with unpredictable client participation, optimizing the privacy-utility trade-off and accelerating training by up to 2.4 times compared to existing solutions.
   - **Year**: 2022

5. **Title**: A Distributed Privacy Preserving Model for the Detection of Alzheimer’s Disease (arXiv:2312.10237)
   - **Authors**: Paul K. Mandal
   - **Summary**: This paper presents a vertical federated learning model for Alzheimer's disease detection, enabling collaborative training across decentralized datasets while preserving privacy. The model achieves an accuracy rate of 82.9%, demonstrating the potential of federated learning in medical diagnostics without compromising patient data privacy.
   - **Year**: 2024

6. **Title**: Fed-EINI: An Efficient and Interpretable Inference Framework for Decision Tree Ensembles in Vertical Federated Learning (arXiv:2105.09540)
   - **Authors**: Xiaolin Chen, Shuai Zhou, Kai Yang, Hao Fao, Hu. Wang, Yongji. Wang
   - **Summary**: Fed-EINI proposes an inference framework for decision tree ensembles in vertical federated learning, enhancing interpretability by disclosing feature meanings while ensuring data privacy. The approach conceals decision paths and employs secure computation methods, balancing efficiency, accuracy, and interpretability in federated settings.
   - **Year**: 2021

**Key Challenges**:

1. **Dynamic Privacy Budget Allocation**: Developing mechanisms to adaptively allocate privacy budgets in response to distribution shifts without compromising overall privacy guarantees remains complex.

2. **Efficient Shift Detection**: Implementing lightweight, privacy-preserving methods to detect distribution shifts accurately and promptly is challenging, especially in resource-constrained federated environments.

3. **Balancing Privacy and Utility**: Achieving an optimal trade-off between maintaining strict privacy standards and ensuring high model utility, particularly during significant distribution shifts, is a persistent challenge.

4. **Client Dropout Resilience**: Designing federated learning systems that are robust to client dropout while maintaining privacy and model performance is essential but difficult.

5. **Interpretable Models**: Ensuring that models remain interpretable to stakeholders while implementing complex privacy-preserving techniques adds another layer of complexity to federated learning systems. 