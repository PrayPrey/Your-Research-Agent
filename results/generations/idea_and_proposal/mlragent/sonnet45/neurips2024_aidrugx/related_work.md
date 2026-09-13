1. **Title**: MorphGen: Controllable and Morphologically Plausible Generative Cell-Imaging (arXiv:2510.01298)
   - **Authors**: Berker Demirel, Marco Fumero, Theofanis Karaletsos, Francesco Locatello
   - **Summary**: MorphGen introduces a diffusion-based generative model for fluorescent microscopy, enabling controllable generation across multiple cell types and perturbations. It preserves organelle-specific details by generating the complete set of fluorescent channels jointly, facilitating fine-grained morphological analysis essential for biological interpretation.
   - **Year**: 2025

2. **Title**: CRADLE-VAE: Enhancing Single-Cell Gene Perturbation Modeling with Counterfactual Reasoning-based Artifact Disentanglement (arXiv:2409.05484)
   - **Authors**: Seungheun Baek, Soyon Park, Yan Ting Chok, Junhyun Lee, Jueon Park, Mogan Gim, Jaewoo Kang
   - **Summary**: CRADLE-VAE presents a causal generative framework tailored for single-cell gene perturbation modeling, enhanced with counterfactual reasoning-based artifact disentanglement. It models the latent distribution of technical artifacts and perturbation effects, employing counterfactual reasoning to disentangle artifacts and learn robust features for generating cellular response data with improved quality.
   - **Year**: 2024

3. **Title**: Central Dogma Transformer: Towards Mechanism-Oriented AI for Cellular Understanding (arXiv:2601.01089)
   - **Authors**: Nobuyuki Ota
   - **Summary**: The Central Dogma Transformer (CDT) integrates pre-trained language models for DNA, RNA, and protein, following the directional logic of the Central Dogma. It employs directional cross-attention mechanisms to produce a unified Virtual Cell Embedding, validated on CRISPRi enhancer perturbation data, achieving significant predictive accuracy and mechanistic interpretability.
   - **Year**: 2026

4. **Title**: Morphologically Intelligent Perturbation Prediction with FORM (arXiv:2510.21337)
   - **Authors**: Reed Naidoo, Matt De Vries, Olga Fourkioti, Vicky Bousgouni, Mar Arias-Garcia, Maria Portillo-Malumbres, Chris Bakal
   - **Summary**: FORM is a machine learning framework for predicting perturbation-induced changes in three-dimensional cellular structure. It consists of a morphology encoder trained via a multi-channel VQGAN and a diffusion-based perturbation trajectory module, capturing how morphology evolves across perturbation conditions. Trained on a large-scale dataset, FORM supports both unconditional morphology synthesis and conditional simulation of perturbed cell states.
   - **Year**: 2025

5. **Title**: ChemVLM: Exploring the Power of Multimodal Large Language Models in Chemistry Area (arXiv:2408.07246)
   - **Authors**: Junxian Li, Di Zhang, Xunzhi Wang, Zeying Hao, Jingdi Lei, Qian Tan, Cai Zhou, Wei Liu, Yaotian Yang, Xinrui Xiong, Weiyun Wang, Zhe Chen, Wenhai Wang, Wei Li, Shufei Zhang, Mao Su, Wanli Ouyang, Yuqiang Li, Dongzhan Zhou
   - **Summary**: ChemVLM introduces an open-source chemical multimodal large language model designed for chemical applications. Trained on a curated bilingual multimodal dataset, it enhances understanding of both textual and visual chemical information, including molecular structures and reactions. ChemVLM demonstrates competitive performance across various chemical tasks.
   - **Year**: 2024

6. **Title**: Advancing Multimodal Medical Capabilities of Gemini (arXiv:2405.03162)
   - **Authors**: Not specified
   - **Summary**: This work discusses the advancements in multimodal medical capabilities of the Gemini model, focusing on integrating diverse data types to enhance medical understanding and prediction. It emphasizes the importance of multimodal integration in medical AI applications.
   - **Year**: 2024

**Key Challenges**:

1. **Data Integration and Standardization**: Combining diverse datasets from various modalities (genomic, transcriptomic, phenotypic) requires standardized formats and integration methods to ensure consistency and compatibility.

2. **Model Complexity and Interpretability**: Developing transformer-based architectures with modality-specific encoders and cross-attention mechanisms increases model complexity, making interpretation and validation of predictions challenging.

3. **Limited Availability of Large-Scale Multimodal Datasets**: The scarcity of comprehensive datasets that encompass the necessary modalities hinders the training and validation of robust foundation models.

4. **Generalization Across Diverse Patient Populations**: Ensuring that models generalize well across different genetic backgrounds and patient-specific factors is crucial for personalized therapy design.

5. **Experimental Validation and Active Learning Loops**: Implementing active learning loops with experimental validation is resource-intensive and requires seamless collaboration between computational and experimental teams to iteratively refine model predictions. 