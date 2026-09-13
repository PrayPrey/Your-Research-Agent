1. **Title**: ACCIO: Table Understanding Enhanced via Contrastive Learning with Aggregations (arXiv:2411.04443)
   - **Authors**: Whanhee Cho
   - **Summary**: This paper introduces ACCIO, a novel approach that enhances table understanding by contrasting original tables with their pivot summaries through contrastive learning. The method trains an encoder to bring these table pairs closer together, achieving competitive performance in column type annotation tasks.
   - **Year**: 2024

2. **Title**: StructCoh: Structured Contrastive Learning for Context-Aware Text Semantic Matching (arXiv:2509.02033)
   - **Authors**: Chao Xue, Ziyuan Gao
   - **Summary**: StructCoh presents a graph-enhanced contrastive learning framework that combines structural reasoning with representation space optimization. It constructs semantic graphs via dependency parsing and topic modeling, employing graph isomorphism networks to propagate structural features, and enforces consistency at multiple granularities through hierarchical contrastive objectives.
   - **Year**: 2025

3. **Title**: Structure-aware Contrastive Learning for Diagram Understanding of Multimodal Models (arXiv:2509.01959)
   - **Authors**: Hiroshi Sasaki
   - **Summary**: This work introduces a training paradigm designed to enhance the comprehension of diagrammatic images within vision-language models. It incorporates specialized loss functions that leverage the inherent structural properties of diagrams, enabling models to develop a more structured and semantically coherent understanding of diagrammatic content.
   - **Year**: 2025

4. **Title**: Bridge the Gap between Language Models and Tabular Understanding (arXiv:2302.09302)
   - **Authors**: Nuo Chen, Linjun Shou, Ming Gong, Jian Pei, Chenyu You, Jianhui Chang, Daxin Jiang, Jia Li
   - **Summary**: The paper proposes UTP, an approach that dynamically supports three types of multi-modal inputs: table-text, table, and text. UTP is pre-trained with a universal mask language modeling objective and a cross-modal contrastive regularization, aiming to bridge the input gap between pre-training and fine-tuning phases in tabular language models.
   - **Year**: 2023

5. **Title**: Table Pre-training: A Survey on Model Architectures, Pre-training Objectives, and Downstream Tasks (arXiv:2201.09745)
   - **Authors**: Haoyu Dong, Zhoujun Cheng, Xinyi He, Mengyu Zhou, Anda Zhou, Fan Zhou, Ao Liu, Shi Han, Dongmei Zhang
   - **Summary**: This survey provides a comprehensive review of different model designs, pre-training objectives, and downstream tasks for table pre-training. It discusses various tabular language models, particularly with specially-designed attention mechanisms, and shares thoughts on existing challenges and future opportunities in the field.
   - **Year**: 2022

6. **Title**: Mimic In-Context Learning for Multimodal Tasks (arXiv:2504.08851)
   - **Authors**: Yuchu Jiang, Jiale Fu, Chenduo Hao, Xinting Hu, Yingzhe Peng, Xin Geng, Xu Yang
   - **Summary**: The paper introduces MimIC, a method that learns stable and generalizable shift effects from in-context demonstrations in multimodal tasks. It aims to enhance the performance of large multimodal models by addressing the sensitivity of in-context learning to the configurations of in-context demonstrations.
   - **Year**: 2025

7. **Title**: Tap4LLM: Table Provider on Sampling, Augmenting, and Packing Semi-structured Data for Large Language Model Reasoning (arXiv:2312.09039)
   - **Authors**: Yuan Sui, Jiaru Zou, Mengyu Zhou, Xinyi He, Lun Du, Shi Han, Dongmei Zhang
   - **Summary**: Tap4LLM presents a method for enhancing large language model reasoning over semi-structured data by sampling, augmenting, and packing tables. It focuses on improving the interpretability and effectiveness of table representations in language models.
   - **Year**: 2023

8. **Title**: Identifying Common Semantics Across Modalities via Contrastive Latent Alignment (Preprints.org:202507.0008)
   - **Authors**: Shengqiong Wu, Hao Fei, Wei Ji, Tat-Seng Chua
   - **Summary**: This paper explores a contrastive learning framework for aligning latent representations across different modalities to identify common semantics. It aims to improve the understanding and integration of multimodal data by leveraging contrastive latent alignment techniques.
   - **Year**: 2025

9. **Title**: Reverse Engineering-Based Optimization for Text-to-SQL Oriented Table Acquisition (Findings of the Association for Computational Linguistics: EMNLP 2025)
   - **Authors**: Not specified
   - **Summary**: The paper proposes a reverse engineering-based optimization approach for text-to-SQL oriented table acquisition. It addresses the heterogeneous semantic gap by generating potentially matched questions conditioned on table schemas and promoting semantic consistency verification between homogeneous questions.
   - **Year**: 2025

10. **Title**: Improving Table Retrieval with Question Generation from Partial Tables (Proceedings of the 4th Table Representation Learning Workshop)
    - **Authors**: Hsing-Ping Liang, Che-Wei Chang, Yao-Chung Fan
    - **Summary**: This work introduces QGpT, a method that uses large language models to generate synthetic questions based on small portions of a table. It aims to enhance table retrieval by improving how tables are represented in embedding space to better align with questions.
    - **Year**: 2025

**Key Challenges**:

1. **Schema Heterogeneity**: Real-world tabular data often exhibit extreme schema heterogeneity, where the same semantic concept appears under different column names, types, and formats across tables. This variability poses significant challenges for models attempting to capture semantic similarities across diverse schemas.

2. **Limited Generalization Across Domains**: Existing table representation models may struggle to generalize across different domains, especially when faced with tables that have inconsistent schemas. This limitation affects their effectiveness in tasks such as data integration and preparation.

3. **Dependence on Manual Annotation**: Many current approaches rely heavily on manual annotation to understand and integrate tables. This process is both time-consuming and expensive, making it impractical for large-scale applications.

4. **Capturing Semantic Equivalence**: Developing models that can recognize semantic equivalence across heterogeneous schemas is challenging. It requires innovative methods, such as contrastive learning frameworks, to pre-train table encoders effectively.

5. **Robustness Without Task-Specific Fine-Tuning**: Achieving robust table understanding across various domains without the need for task-specific fine-tuning remains a significant challenge. Models must be designed to handle diverse data without extensive customization for each specific task. 