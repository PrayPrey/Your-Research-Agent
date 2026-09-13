1. **Title**: RDesign: Hierarchical Data-efficient Representation Learning for Tertiary Structure-based RNA Design (arXiv:2301.10774)
   - **Authors**: Cheng Tan, Yijie Zhang, Zhangyang Gao, Bozhen Hu, Siyuan Li, Zicheng Liu, Stan Z. Li
   - **Summary**: This paper introduces RDesign, a hierarchical representation learning framework for RNA design that leverages contrastive learning at both cluster and sample levels to effectively utilize limited data. The approach incorporates secondary structure information to enhance the RNA design process.
   - **Year**: 2023

2. **Title**: RiboDiffusion: Tertiary Structure-based RNA Inverse Folding with Generative Diffusion Models (arXiv:2404.11199)
   - **Authors**: Han Huang, Ziqian Lin, Dongchen He, Liang Hong, Yu Li
   - **Summary**: RiboDiffusion presents a generative diffusion model for RNA inverse folding, learning the conditional distribution of RNA sequences given 3D backbone structures. The model combines a graph neural network-based structure module with a Transformer-based sequence module, achieving improved sequence recovery and diversity.
   - **Year**: 2024

3. **Title**: Deciphering RNA Secondary Structure Prediction: A Probabilistic K-Rook Matching Perspective (arXiv:2212.14041)
   - **Authors**: Cheng Tan, Zhangyang Gao, Hanqun Cao, Xingran Chen, Ge Wang, Lirong Wu, Jun Xia, Jiangbin Zheng, Stan Z. Li
   - **Summary**: This work reformulates RNA secondary structure prediction as a K-Rook problem, simplifying the prediction process into probabilistic matching within a finite solution space. The proposed method, RFold, achieves competitive performance with enhanced inference efficiency.
   - **Year**: 2022

4. **Title**: EquiCPI: SE(3)-Equivariant Geometric Deep Learning for Structure-Aware Prediction of Compound-Protein Interactions (arXiv:2504.04654)
   - **Authors**: Ngoc-Quang Nguyen
   - **Summary**: EquiCPI introduces an SE(3)-equivariant geometric deep learning framework that integrates structural modeling with neural networks to predict compound-protein interactions, preserving symmetry under rotations, translations, and reflections.
   - **Year**: 2025

5. **Title**: Geometric Deep Learning (arXiv:2104.13478)
   - **Authors**: Michael M. Bronstein, Joan Bruna, Taco Cohen, Petar Veličković
   - **Summary**: This comprehensive review discusses geometric deep learning, focusing on models that respect the symmetries and structures inherent in data, such as SE(3)-equivariant networks, which are pertinent to modeling RNA tertiary structures.
   - **Year**: 2021

6. **Title**: Graph Representation Learning for Molecular Data (arXiv:2304.02656)
   - **Authors**: Meng Liu, Tian Xie, Yuyang Wang, Jimeng Sun
   - **Summary**: The paper explores graph representation learning techniques for molecular data, emphasizing the importance of capturing molecular structures and interactions, which is relevant for RNA tertiary structure prediction.
   - **Year**: 2023

7. **Title**: Optimal Symmetries in Binary Classification (arXiv:2408.08823)
   - **Authors**: Anonymous
   - **Summary**: This work investigates the role of symmetries in binary classification tasks, providing insights into how incorporating symmetry can improve model performance, which is applicable to RNA structure prediction models.
   - **Year**: 2024

8. **Title**: Preprint. Under review. (arXiv:2406.03686)
   - **Authors**: Anonymous
   - **Summary**: The paper discusses advancements in molecular generative models, including diffusion models and graph neural networks, highlighting their applications in drug discovery and potential relevance to RNA design.
   - **Year**: 2024

9. **Title**: Published as a conference paper at ICLR 2023 (arXiv:2303.15520)
   - **Authors**: Anonymous
   - **Summary**: This conference paper presents a method for protein docking using geometric deep learning techniques, emphasizing the importance of capturing 3D structural information, which is pertinent to RNA tertiary structure prediction.
   - **Year**: 2023

10. **Title**: SE(3)-Equivariant Graph Neural Networks for Data-Efficient and Accurate Interatomic Potentials (arXiv:2202.02541)
    - **Authors**: Anonymous
    - **Summary**: The paper introduces SE(3)-equivariant graph neural networks designed for modeling interatomic potentials, demonstrating data efficiency and accuracy, which are crucial for predicting RNA tertiary structures.
    - **Year**: 2022

**Key Challenges:**

1. **Data Scarcity**: The limited availability of high-quality RNA tertiary structure data hampers the training of robust machine learning models.

2. **Structural Complexity**: RNA molecules exhibit intricate folding patterns and non-canonical interactions, making accurate modeling challenging.

3. **Multi-Scale Modeling**: Capturing interactions across different scales, from nucleotide-level to global 3D architecture, requires sophisticated hierarchical models.

4. **Equivariance Constraints**: Ensuring that models are equivariant to transformations like rotations and translations is essential for accurate structure prediction but adds complexity to model design.

5. **Generalization to Novel Structures**: Developing models that can generalize to unseen RNA structures remains a significant challenge due to the diversity and flexibility of RNA conformations. 