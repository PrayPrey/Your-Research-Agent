## Related Work

**Related Papers**
1. **Title**: Contrastive Learning Inverts the Data Generating Process (2021)
   - **Authors**: Zimmermann, Sharma, Schneider, Bethge, Brendel
   - **Summary**: Establishes that contrastive learning provably inverts generative models, providing a theoretical basis for understanding how self-supervised methods recover underlying data-generating factors.
   - **Year**: 2021

2. **Title**: To Compress or Not to Compress—SSL and Information Theory: A Review (2023)
   - **Authors**: Shwartz-Ziv, LeCun
   - **Summary**: Provides a unified information-theoretic framework for self-supervised learning, cataloging viable approaches while acknowledging mutual information estimation challenges.
   - **Year**: 2023

3. **Title**: Chaos is a Ladder: Augmentation Overlap (2022)
   - **Authors**: Wang, Zhang, Wang, Yang, Lin
   - **Summary**: Demonstrates that augmentation properties quantifiably affect representation quality, providing empirical support for designing fitness functions based on augmentation characteristics.
   - **Year**: 2022

4. **Title**: A Probabilistic Model Behind Self-Supervised Learning (2024)
   - **Authors**: Bizeul, Schölkopf, Allen
   - **Summary**: Proposes a unified generative latent variable model for discriminative self-supervised learning, providing theoretical foundations for proxy-based evaluation of SSL methods.
   - **Year**: 2024

5. **Title**: Self-Supervised Learning: Generative or Contrastive (2020)
   - **Authors**: Liu et al.
   - **Summary**: Provides a comprehensive taxonomy of self-supervised learning methods across generative and contrastive paradigms, revealing the absence of prescriptive frameworks for method selection.
   - **Year**: 2020

6. **Title**: E5 Text Embeddings
   - **Authors**: Not specified
   - **Summary**: Demonstrates manual domain-specific design approaches for text embeddings, highlighting the need for automated framework development.
   - **Year**: Not specified

7. **Title**: SetFit
   - **Authors**: Not specified
   - **Summary**: Illustrates manual domain-specific design for few-shot learning scenarios, motivating the need for automated SSL task selection frameworks.
   - **Year**: Not specified

**Key Challenges**
1. **Absence of Prescriptive Frameworks**: Existing taxonomies comprehensively categorize SSL methods but provide no guidance for selecting appropriate tasks for specific domains or datasets.
2. **Mutual Information Estimation Difficulties**: While information-theoretic frameworks offer unified perspectives on SSL, practical challenges in estimating mutual information limit their direct applicability.
3. **Manual Domain-Specific Design**: Current best practices rely on manual, domain-specific engineering (e.g., SimCLR for vision, MLM for text), lacking automated methods for task selection.
4. **Quantifying Augmentation Effects**: Understanding how augmentation properties affect representation quality remains an open challenge for principled SSL design.
