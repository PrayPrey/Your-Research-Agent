1. **Title**: Collaborative Representation Learning for Alignment of Tactile, Language, and Vision Modalities (arXiv:2511.11512)
   - **Authors**: Yiyun Zhou, Mingjing Xu, Jingwei Shi, Quanjiang Li, Jingyuan Chen
   - **Summary**: This paper introduces TLV-CoRe, a CLIP-based method for collaborative representation learning across tactile, language, and vision modalities. It addresses the lack of standardization in tactile sensors by proposing a Sensor-Aware Modulator to unify tactile features and a Unified Bridging Adapter to enhance tri-modal interaction. The approach aims to improve sensor-agnostic representation learning and cross-modal alignment.
   - **Year**: 2025

2. **Title**: Transferable Tactile Transformers for Representation Learning Across Diverse Sensors and Tasks (arXiv:2406.13640)
   - **Authors**: Jialiang Zhao, Yuxiang Ma, Lirui Wang, Edward H. Adelson
   - **Summary**: The authors present T3, a framework designed to learn tactile representations that generalize across various sensors and tasks. By constructing a shared transformer architecture with sensor-specific encoders and task-specific decoders, T3 achieves zero-shot transferability and can be fine-tuned with minimal domain-specific data. The framework is validated using the Foundation Tactile dataset, comprising over 3 million data points from 13 sensors and 11 tasks.
   - **Year**: 2024

3. **Title**: HyperTaxel: Hyper-Resolution for Taxel-Based Tactile Signals Through Contrastive Learning (arXiv:2408.08312)
   - **Authors**: Hongyu Li, Snehal Dikhale, Jinda Cui, Soshi Iba, Nawid Jamali
   - **Summary**: This work proposes HyperTaxel, a framework that enhances the spatial resolution of taxel-based tactile signals using contrastive learning. By mapping sparse, low-resolution taxel signals to high-resolution contact surfaces, the method captures geometric features such as flatness and curvature, improving performance in tasks like surface classification and in-hand pose estimation.
   - **Year**: 2024

4. **Title**: RA-Touch: Retrieval-Augmented Touch Understanding with Enriched Visual Data (arXiv:2505.14270)
   - **Authors**: Yoorhim Cho, Hongyeob Kim, Semin Kim, Youjia Zhang, Yunseok Choi, Sungeun Hong
   - **Summary**: RA-Touch introduces a retrieval-augmented framework that leverages visual data enriched with tactile semantics to improve visuo-tactile perception. By recaptioning a large-scale visual dataset with tactile-focused descriptions and integrating them with tactile inputs, the model enhances understanding of tactile properties without direct tactile supervision.
   - **Year**: 2025

5. **Title**: Universal Visuo-Tactile Video Understanding for Embodied Interaction
   - **Authors**: Yifan Xie, Mingyang Li, Shoujie Li, Xingting Li, Guangyu Chen, Fei Ma, Fei Richard Yu, Wenbo Ding
   - **Summary**: The authors present VTV-LLM, a multi-modal large language model designed for universal visuo-tactile video understanding. The model is trained on the VTV150K dataset, comprising 150,000 video frames from diverse objects captured across three tactile sensors, annotated with fundamental tactile attributes. The framework enables sophisticated tactile reasoning capabilities, including feature assessment and scenario-based decision making.
   - **Year**: 2025

6. **Title**: Canonical Representation and Force-Based Pretraining of 3D Tactile for Dexterous Visuo-Tactile Policy Learning
   - **Authors**: [Authors not specified]
   - **Summary**: This paper proposes a novel standard representation for 3D tactile feature learning and introduces a force-based self-supervised pretraining task to capture both local and net force characteristics. The approach aims to address challenges in learning effective tactile features due to the high dimensionality of tactile data and the lack of standardized datasets.
   - **Year**: 2025

7. **Title**: Visual-Tactile Sensing for In-Hand Object Reconstruction (arXiv:2303.14498)
   - **Authors**: Wenqiang Xu, Zhenjun Yu, Han Xue, Ruolin Ye, Siqiong Yao, Cewu Lu
   - **Summary**: The authors introduce VTacO, a visual-tactile in-hand object reconstruction framework that utilizes a tactile sensor and a simulated environment to reconstruct both rigid and deformable objects. The framework demonstrates superior performance in capturing fine-grained object details by integrating visual and tactile data.
   - **Year**: 2023

8. **Title**: Toward Artificial Palpation: Representation Learning of Touch on Soft Bodies
   - **Authors**: Zohar Rimon, Elisei Shafer, Tal Tepper, Efrat Shimron, Aviv Tamar
   - **Summary**: This work investigates a proof of concept for artificial palpation using self-supervised learning. By developing a simulation environment and collecting real-world datasets of soft objects, the authors train a model to predict sensory readings at different positions, enabling applications in tactile imaging and change detection.
   - **Year**: 2025

9. **Title**: UniT: Unified Tactile Representation for Robot Learning (arXiv:2408.06481)
   - **Authors**: Zhengtong Xu, Raghava Uppuluri, Xinwei Zhang, Cael Fitch, Philip Glen Crandall, Wan Shou, Dongyi Wang, Yu She
   - **Summary**: UniT introduces a novel approach to tactile representation learning using VQVAE to learn a compact latent space. Trained on tactile images from a single object, the representation demonstrates zero-shot transferability to various downstream tasks, including perception and manipulation policy learning.
   - **Year**: 2024

10. **Title**: Sensor-Invariant Tactile Representation
    - **Authors**: Harsh Gupta, Yuchen Mo, Shengmiao Jin, Wenzhen Yuan
    - **Summary**: The authors propose a method for extracting Sensor-Invariant Tactile Representations (SITR) to enable zero-shot transfer across optical tactile sensors. Utilizing a transformer-based architecture trained on a diverse dataset of simulated sensor designs, the approach generalizes to new sensors with minimal calibration, facilitating data and model transferability.
    - **Year**: 2025

**Key Challenges:**

1. **Sensor Heterogeneity**: The lack of standardization among tactile sensors leads to redundant features and hinders cross-sensor generalization, making it challenging to develop models that work seamlessly across different hardware platforms.

2. **Data Scarcity and Annotation**: Collecting and annotating large-scale tactile datasets is labor-intensive and costly, limiting the availability of diverse and comprehensive datasets necessary for training robust models.

3. **Cross-Modal Integration**: Effectively integrating tactile data with other modalities, such as vision and language, remains a significant challenge due to differences in data structures and the need for sophisticated alignment techniques.

4. **Temporal Dynamics**: Capturing and modeling the fine-grained temporal dynamics inherent in tactile interactions is complex, requiring models to process sequential data effectively to understand contact events and object properties.

5. **Transferability and Generalization**: Developing tactile representation learning methods that generalize across diverse sensors, tasks, and environments is difficult, necessitating strategies that can adapt to varying conditions without extensive retraining. 