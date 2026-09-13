**Related Papers**

1. **Title**: Edge-AI for Agriculture: Lightweight Vision Models for Disease Detection in Resource-Limited Settings (arXiv:2412.18635)
   - **Authors**: Harsh Joshi
   - **Summary**: This paper presents a lightweight computer vision pipeline designed to assist farmers in detecting orange diseases using minimal resources. The system integrates object detection, classification, and segmentation models optimized for deployment on edge devices, ensuring functionality in resource-limited environments. Notably, the Vision Transformer achieved 96% accuracy in orange species classification, and the lightweight YOLOv8-S model demonstrated exceptional object detection performance with minimal computational overhead.
   - **Year**: 2024

2. **Title**: TinyML-Enabled IoT for Sustainable Precision Irrigation (arXiv:2601.13054)
   - **Authors**: Kamogelo Taueatsoala, Caitlyn Daniels, Angelina J. Ramsunar, Petrus Bronkhorst, Absalom E. Ezugwu
   - **Summary**: This study introduces an edge-first IoT framework integrating Tiny Machine Learning (TinyML) for intelligent, offline-capable precision irrigation. Utilizing low-cost hardware, including an ESP32 microcontroller and a Raspberry Pi, the system enables autonomous decision-making without cloud dependency. The optimized gradient boosting model, deployed as a lightweight TinyML inference engine on the ESP32, predicts irrigation needs with exceptional accuracy (MAPE < 1%). Experimental validation demonstrated a significant reduction in water usage compared to traditional methods, confirming the system's viability for sustainable deployment in resource-constrained rural settings.
   - **Year**: 2026

3. **Title**: Non-Linear Model-Based Sequential Decision-Making in Agriculture (arXiv:2509.01924)
   - **Authors**: Sakshi Arya, Wentao Lin
   - **Summary**: This paper proposes a family of nonlinear, model-based bandit algorithms that embed domain-specific response curves into the exploration-exploitation loop for sustainable agricultural management. By coupling principled uncertainty quantification with rapidly computable profit optima, these algorithms achieve sublinear regret and near-optimal sample complexity while preserving interpretability. Extensive simulations emulating real-world fertilizer-rate decisions show consistent improvements over both linear and nonparametric baselines in the low-sample regime, supporting sustainable, inclusive, and transparent sequential decision-making in agriculture.
   - **Year**: 2025

4. **Title**: ReinDSplit: Reinforced Dynamic Split Learning for Pest Recognition in Precision Agriculture (arXiv:2506.13935)
   - **Authors**: Vishesh Kumar Tanwar, Soumik Sarkar, Asheesh K. Singh, Sajal K. Das
   - **Summary**: ReinDSplit introduces a reinforcement learning-driven framework that dynamically tailors deep neural network split points for each device in a split learning setup, optimizing efficiency without sacrificing accuracy. A Q-learning agent acts as an adaptive orchestrator, balancing workloads and latency thresholds across devices to mitigate computational starvation or overload. Evaluated on insect classification datasets using ResNet18, GoogleNet, and MobileNetV2, ReinDSplit achieves 94.31% accuracy with MobileNetV2, pioneering a paradigm shift in split learning by harmonizing reinforcement learning for resource efficiency, privacy, and scalability in heterogeneous environments.
   - **Year**: 2025

5. **Title**: Cheetah: Natural Language Generation for 517 African Languages (arXiv:2401.01053)
   - **Authors**: Ife Adebara, AbdelRahim Elmadany, Muhammad Abdul-Mageed
   - **Summary**: Cheetah is a massively multilingual natural language generation model supporting 517 African languages and language varieties across 14 language families. The model addresses the scarcity of NLG resources and provides a solution to foster linguistic diversity. Comprehensive evaluations across six generation downstream tasks demonstrate Cheetah's remarkable performance in generating coherent and contextually appropriate text in a wide range of African languages, contributing to advancing NLP research in low-resource settings.
   - **Year**: 2024

6. **Title**: SmartChoices: Augmenting Software with Learned Implementations (arXiv:2304.13033)
   - **Authors**: Eric Chen, Daniel Golovin, Gábor Bartók, Emily Donahue, Tzu-Kuo Huang, Efi Kokiopoulou, Ruoyan Qin, Nikhil Sarda, Justin Sybrandt, Vincent Tjeng
   - **Summary**: SmartChoices presents a novel approach that reduces the cost to deploy production-ready machine learning solutions for contextual bandit problems. The framework enables non-experts to rapidly deploy ML solutions by eliminating many sources of technical debt common to ML systems. Engineers have independently used SmartChoices to improve a wide range of software, resulting in better latency, throughput, and click-through rates.
   - **Year**: 2023

7. **Title**: Uncertainty as a Predictor: Leveraging Self-Supervised Learning for Zero-Shot MOS Prediction (arXiv:2312.15616)
   - **Authors**: Aditya Ravuri, Erica Cooper, Junichi Yamagishi
   - **Summary**: This paper explores the ability of pre-trained self-supervised learning models to perform zero-shot Mean Opinion Score (MOS) prediction. The study demonstrates that uncertainty measures derived from models like wav2vec correlate with MOS scores, providing insights into how inherent uncertainties in SSL models can serve as effective proxies for audio quality assessment, especially in low-resource settings where extensive MOS data may be unavailable.
   - **Year**: 2023

8. **Title**: ECOVAL: An Efficient Data Valuation Framework for Machine Learning (arXiv:2402.09288)
   - **Authors**: Vikram S Chundawat, Murari Mandal, Ayush K Tarun, Hong Ming Tan, Bowei Chen, Mohan Kankanhalli
   - **Summary**: ECOVAL introduces an efficient data valuation framework to estimate the value of data for machine learning models in a fast and practical manner. By determining the value of clusters of similar data points and formulating the performance of a model as a production function, the framework addresses the core challenge of efficient data valuation at scale in machine learning models.
   - **Year**: 2024

9. **Title**: Tiny Machine Learning: Progress and Futures (arXiv:2403.19076)
   - **Authors**: Ji Lin, Ligeng Zhu, Wei-Ming Chen, Wei-Chen Wang, Song Han
   - **Summary**: This review discusses the definition, challenges, and applications of Tiny Machine Learning (TinyML). It surveys recent progress in TinyML and deep learning on microcontrollers, introduces MCUNet, and extends the solution from inference to training, presenting future directions in the area. The paper emphasizes the importance of system-algorithm co-design in enabling TinyML for both inference and training.
   - **Year**: 2024

10. **Title**: Adaptive Curriculum Learning with Local Data Valuation for Low-Resource Agricultural Applications
    - **Authors**: [Your Name]
    - **Summary**: This paper proposes an adaptive curriculum learning framework that intelligently combines limited local data with abundant but mismatched global agricultural datasets. The approach consists of a local data valuation module, a curriculum transfer strategy, and an active sample recommendation component. Expected outcomes include significant improvement in prediction accuracy with minimal labeled local samples, deployable on smartphones, directly addressing data scarcity and computational constraints in resource-limited agricultural settings.
    - **Year**: 2026

**Key Challenges**

1. **Data Scarcity and Quality**: Limited availability of labeled local agricultural data hampers the development of accurate models. Additionally, the quality of available data may be compromised due to inconsistencies and noise.

2. **Domain Shift and Generalization**: Models trained on global datasets often face challenges when applied to local contexts due to domain shifts, leading to reduced generalization and reliability.

3. **Computational Constraints**: Deploying machine learning models in resource-limited environments requires optimization for low-power devices, balancing model complexity with computational efficiency.

4. **Efficient Data Valuation**: Determining the value of scarce local data is crucial for effective model training and active learning strategies, yet existing methods may be computationally expensive or impractical.

5. **Sustainable Deployment**: Ensuring that machine learning solutions are sustainable and scalable in low-resource agricultural settings involves addressing challenges related to infrastructure, maintenance, and user adoption. 