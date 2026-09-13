1. **Title**: RDesign: Hierarchical Data-efficient Representation Learning for Tertiary Structure-based RNA Design (arXiv:2301.10774)
   - **Authors**: Cheng Tan, Yijie Zhang, Zhangyang Gao, Bozhen Hu, Siyuan Li, Zicheng Liu, Stan Z. Li
   - **Summary**: This paper introduces RDesign, a data-driven RNA design pipeline that constructs a large benchmark dataset and employs a hierarchical representation learning framework. The approach utilizes contrastive learning at both cluster and sample levels to effectively learn structural representations, incorporating secondary structures with base pairs as prior knowledge to facilitate the RNA design process.
   - **Year**: 2023

2. **Title**: RiboPO: Preference Optimization for Structure- and Stability-Aware RNA Design (arXiv:2510.21161)
   - **Authors**: Minghao Sun, Hanqun Cao, Zhou Zhang, Chen Wei, Liang Wang, Tianrui Jia, Zhiyuan Liu, Tianfan Fu, Xiangru Tang, Yejin Choi, Pheng-Ann Heng, Fang Wu, Yang Zhang
   - **Summary**: RiboPO presents a framework that addresses the multi-objective challenge of designing RNA sequences that adopt specified 3D structures while maintaining thermodynamic stability. It employs reinforcement learning from physical feedback to fine-tune models, constructing preference pairs from composite physical criteria that couple global 3D fidelity and thermodynamic stability.
   - **Year**: 2025

3. **Title**: RiboGen: RNA Sequence and Structure Co-Generation with Equivariant MultiFlow (arXiv:2503.02058)
   - **Authors**: Dana Rubin, Allan dos Santos Costa, Manvitha Ponnapati, Joseph Jacobson
   - **Summary**: RiboGen introduces a deep learning model capable of simultaneously generating RNA sequences and their all-atom 3D structures. Utilizing Euclidean Equivariant neural networks, the model efficiently processes and learns three-dimensional geometry, demonstrating the potential of co-generating sequence and structure for RNA modeling.
   - **Year**: 2025

4. **Title**: PanFoMa: A Lightweight Foundation Model and Benchmark for Pan-Cancer (arXiv:2512.03111)
   - **Authors**: Xiaoshui Huang, Tianlin Zhu, Yifan Zuo, Xue Xia, Zonghan Wu, Jiebin Yan, Dingli Hua, Zongyi Xu, Yuming Fang, Jian Zhang
   - **Summary**: PanFoMa introduces a lightweight hybrid neural network combining Transformers and state-space models to achieve a balance between performance and efficiency in pan-cancer research. The model captures complex gene interactions and integrates global context, demonstrating superior performance on a large-scale pan-cancer single-cell benchmark.
   - **Year**: 2025

5. **Title**: Efficient Transformers: A Survey (arXiv:2009.06732)
   - **Authors**: Yi Tay, Mostafa Dehghani, Dara Bahri, Donald Metzler
   - **Summary**: This survey provides a comprehensive overview of efficient Transformer architectures, discussing various techniques to reduce computational and memory complexity. It covers advancements relevant to modeling hierarchical structures in RNA sequences.
   - **Year**: 2020

6. **Title**: Llama 2: Open Foundation and Fine-Tuned Chat Models (arXiv:2307.09288)
   - **Authors**: Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine El-Kishky, Thomas Scialom, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, Aurelien Rodriguez, Armand Joulin, Edouard Grave, Guillaume Lample
   - **Summary**: Llama 2 presents open foundation and fine-tuned chat models, offering insights into the development of large-scale language models. The methodologies discussed can inform the creation of foundation models for RNA therapeutic design.
   - **Year**: 2023

7. **Title**: OpenELM: An Efficient Language Model Family with Open Training and Evaluation Frameworks (arXiv:2404.14619)
   - **Authors**: Anmol Gulati, Yu Zhang, Wei Han, Shankar Ananthakrishnan, Yonghui Wu
   - **Summary**: OpenELM introduces an efficient language model family with open training and evaluation frameworks. The paper discusses architectural choices and training methodologies that can be applied to develop efficient models for RNA sequence and structure prediction.
   - **Year**: 2024

8. **Title**: OLMo: Accelerating the Science of Language Models (arXiv:2402.00838)
   - **Authors**: Jason Phang, Hailey Schoelkopf, Ian Tenney, Alex Wang, Samuel R. Bowman
   - **Summary**: OLMo discusses strategies to accelerate the development of language models, emphasizing open science practices. The insights provided can be leveraged to expedite the creation of foundation models for RNA therapeutic design.
   - **Year**: 2024

9. **Title**: Advancing Multimodal Medical Capabilities of Gemini (arXiv:2405.03162)
   - **Authors**: Google Research Team
   - **Summary**: This paper explores the multimodal capabilities of the Gemini model in medical applications, highlighting the integration of various data types. The approaches discussed are relevant for developing models that consider multiple RNA modalities and structural scales.
   - **Year**: 2024

10. **Title**: Compute Trends Across Three Eras of Machine Learning (arXiv:2202.05924)
    - **Authors**: Jaime Sevilla, Lennart Heim, Anson Ho, Tamay Besiroglu, Ryan Greenblatt, Allan Dafoe
    - **Summary**: This paper analyzes the trends in computational requirements across different eras of machine learning, providing context for the resources needed to train large-scale models like RNAFoundation.
    - **Year**: 2022

**Key Challenges:**

1. **Data Scarcity and Quality**: The limited availability of high-quality, annotated RNA datasets hampers the training of comprehensive models that can generalize across various RNA types and functions.

2. **Modeling Complex RNA Structures**: Accurately capturing the hierarchical nature of RNA structures—from primary sequences to tertiary formations—remains a significant challenge due to the intricate folding patterns and interactions.

3. **Integration of Multimodal Data**: Effectively combining diverse data types, such as sequence information, structural data, and cellular context, requires sophisticated models capable of handling multimodal inputs.

4. **Computational Efficiency**: Developing models that are both computationally efficient and capable of processing large-scale RNA data is essential, especially given the resource-intensive nature of training deep learning models.

5. **Generalization to Novel RNA Therapeutics**: Ensuring that models can generalize to design novel RNA therapeutics with desired properties, such as enhanced translational efficiency and stability, is critical for practical applications. 