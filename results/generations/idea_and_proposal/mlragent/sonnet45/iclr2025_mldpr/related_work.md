1. **Title**: CC30k: A Citation Contexts Dataset for Reproducibility-Oriented Sentiment Analysis (arXiv:2511.07790)
   - **Authors**: Rochana R. Obadage, Sarah M. Rajtmajer, Jian Wu
   - **Summary**: This paper introduces the CC30k dataset, comprising 30,734 citation contexts from machine learning papers, each labeled with reproducibility-oriented sentiments (Positive, Negative, or Neutral). The dataset aims to facilitate large-scale assessments of the reproducibility of machine learning papers by providing a resource for training models to predict reproducibility-oriented sentiments.
   - **Year**: 2025

2. **Title**: SAVeD: Semantic Aware Version Discovery (arXiv:2511.17298)
   - **Authors**: Artem Frenk, Roee Shraga
   - **Summary**: SAVeD is a contrastive learning-based framework designed to identify versions of structured datasets without relying on metadata or labels. By generating augmented table views through random transformations and embedding them via a custom transformer encoder, SAVeD effectively distinguishes semantically altered versions of datasets, addressing challenges in dataset versioning and reproducibility.
   - **Year**: 2025

3. **Title**: From Data to Decision: Data-Centric Infrastructure for Reproducible ML in Collaborative eScience (arXiv:2506.16051)
   - **Authors**: Zhiwei Li, Carl Kesselman, Tran Huy Nguyen, Benjamin Yixing Xu, Kyle Bolo, Kimberley Yu
   - **Summary**: This paper presents a data-centric framework for lifecycle-aware reproducibility in machine learning, centered around six structured artifacts: Dataset, Feature, Workflow, Execution, Asset, and Controlled Vocabulary. The framework formalizes relationships between data, code, and decisions, enabling versioned, interpretable, and traceable ML experiments over time, demonstrated through a clinical ML use case.
   - **Year**: 2025

4. **Title**: Enabling Reproducibility and Meta-learning Through a Lifelong Database of Experiments (LDE) (arXiv:2202.10979)
   - **Authors**: Jason Tsay, Andrea Bartezzaghi, Aleke Nolte, Cristiano Malossi
   - **Summary**: The Lifelong Database of Experiments (LDE) automatically extracts and stores linked metadata from AI experiment artifacts, providing features to reproduce these artifacts and perform meta-learning across them. By storing context from multiple stages of the AI development lifecycle, LDE assists in implementing meta-learning and may improve its performance through aggregation of results.
   - **Year**: 2022

5. **Title**: A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research (arXiv:1911.07698)
   - **Authors**: Maurice P. van den Akker, Martijn C. Willemsen, Alan Said
   - **Summary**: This analysis highlights issues in the reproducibility and progress of recommender systems research, emphasizing the need for standardized documentation and versioning of datasets to ensure consistent and reliable evaluation of models.
   - **Year**: 2021

6. **Title**: Draft version November 19, 2019 (arXiv:1905.05116)
   - **Authors**: [Authors not specified]
   - **Summary**: This draft discusses the challenges in reproducibility within machine learning, particularly emphasizing the need for trustworthy and interpretable algorithms, and the importance of standardized documentation and versioning of datasets to ensure consistent and reliable evaluation of models.
   - **Year**: 2021

**Key Challenges**:

1. **Lack of Standardized Dataset Versioning**: Many datasets undergo continuous updates without proper version tracking, leading to inconsistencies and reproducibility issues in research outcomes.

2. **Insufficient Documentation of Dataset Changes**: Modifications, corrections, and deprecations in datasets are often undocumented, making it difficult for researchers to be aware of and account for these changes.

3. **Propagation of Quality Issues**: Discoveries of biases or errors in datasets are not effectively communicated across all versions, resulting in the continued use of flawed data.

4. **Integration with Data Repositories**: There is a need for seamless integration of version-aware documentation frameworks with existing data repositories to enforce version pinning and enable temporal queries.

5. **Automated Impact Analysis**: Developing tools to automatically identify and assess the impact of specific dataset versions on research outcomes remains a significant challenge. 