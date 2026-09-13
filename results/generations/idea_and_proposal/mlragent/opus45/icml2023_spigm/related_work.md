1. **Title**: Conformal Prediction Beyond the Seen: A Missing Mass Perspective for Uncertainty Quantification in Generative Models (arXiv:2506.05497)
   - **Authors**: Sima Noorani, Shayan Kiyani, George Pappas, Hamed Hassani
   - **Summary**: This paper introduces Conformal Prediction with Query Oracle (CPQ), a framework for uncertainty quantification in generative models. CPQ addresses the challenge of constructing prediction sets solely from finite queries to a black-box generative model, balancing coverage, query budget, and informativeness. The approach is rooted in the missing mass problem in statistics and is demonstrated on language models, yielding more informative prediction sets than existing conformal methods.
   - **Year**: 2025

2. **Title**: Foundation Molecular Grammar: Multi-Modal Foundation Models Induce Interpretable Molecular Graph Languages (arXiv:2505.22948)
   - **Authors**: Michael Sun, Weize Yuan, Gang Liu, Wojciech Matusik, Jie Chen
   - **Summary**: The authors propose Foundation Molecular Grammar (FMG), which leverages multi-modal foundation models to induce interpretable molecular graph languages. FMG renders molecules as images, describes them as text, and aligns information across modalities using prompt learning. This approach excels in synthesizability, diversity, and data efficiency, offering built-in chemical interpretability for automated molecular discovery workflows.
   - **Year**: 2025

3. **Title**: GraphDF: A Discrete Flow Model for Molecular Graph Generation (arXiv:2102.01189)
   - **Authors**: Youzhi Luo, Keqiang Yan, Shuiwang Ji
   - **Summary**: GraphDF introduces a discrete latent variable model for molecular graph generation based on normalizing flow methods. By using invertible modulo shift transforms to map discrete latent variables to graph nodes and edges, GraphDF reduces computational costs and eliminates the negative effects of dequantization. The model outperforms prior methods in random generation, property optimization, and constrained optimization tasks.
   - **Year**: 2021

4. **Title**: Compound Probabilistic Context-Free Grammars (arXiv:1906.10225)
   - **Authors**: Yoon Kim, Chris Dyer, Alexander M. Rush
   - **Summary**: This work studies grammar induction by modeling sentences with a compound probabilistic context-free grammar (PCFG). Unlike traditional methods that learn a single stochastic grammar, this approach introduces a per-sentence continuous latent variable, inducing marginal dependencies beyond context-free assumptions. Inference is performed using collapsed variational inference, marginalizing out latent trees with dynamic programming.
   - **Year**: 2020

5. **Title**: Automated Statistical Model Discovery with Language Models (arXiv:2402.17879)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper presents a framework for automated model discovery using language models (LMs). It leverages LMs to propose probabilistic programs for datasets, fit these programs, and evaluate them. The approach integrates model building and criticism, guided by natural language feedback, to develop statistical models of real-world datasets.
   - **Year**: 2024

6. **Title**: Structured Variational Inference in (arXiv:1906.03161)
   - **Authors**: [Authors not specified]
   - **Summary**: This work addresses scalable inference in structured probabilistic models by introducing a variational inference framework that incorporates inducing variables. The approach enables efficient posterior estimation in models with complex dependencies, facilitating applications in various domains requiring structured data modeling.
   - **Year**: 2020

7. **Title**: Generative Modeling of Complex Data (arXiv:2202.02145)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors explore generative modeling techniques for complex data structures, focusing on methods that capture intricate dependencies and structures within the data. The paper discusses advancements in model architectures and inference methods that enhance the capability to generate realistic and diverse data samples.
   - **Year**: 2022

8. **Title**: Preprint. Under review. (arXiv:2406.03686)
   - **Authors**: [Authors not specified]
   - **Summary**: This preprint discusses advancements in molecular docking and generative modeling for drug discovery. It highlights the integration of deep learning techniques with traditional methods to improve the accuracy and efficiency of molecular generation and binding affinity prediction.
   - **Year**: 2024

**Key Challenges:**

1. **Chemical Validity Constraints**: Ensuring generated molecules adhere to chemical rules and are synthesizable remains a significant challenge.

2. **Hierarchical Substructure Capture**: Effectively modeling and generating molecules with complex hierarchical substructures, such as functional groups and ring systems, is difficult.

3. **Uncertainty Quantification**: Providing reliable and principled uncertainty estimates for generated molecules to guide decision-making in drug discovery is an ongoing challenge.

4. **Scalability of Inference Methods**: Developing scalable inference techniques that can handle the complexity of structured molecular data without compromising performance is essential.

5. **Integration of Multi-Modal Data**: Combining information from various modalities (e.g., textual descriptions, images) to enhance molecular generation and interpretation poses integration challenges. 