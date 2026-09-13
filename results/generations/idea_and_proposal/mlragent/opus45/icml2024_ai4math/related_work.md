1. **Title**: Autoformalize Mathematical Statements by Symbolic Equivalence and Semantic Consistency (arXiv:2410.20936)
   - **Authors**: Zenan Li, Yifan Wu, Zhaoyu Li, Xinming Wei, Xian Zhang, Fan Yang, Xiaoxing Ma
   - **Summary**: This paper introduces a framework that enhances autoformalization accuracy by scoring and selecting the best result from multiple candidates using symbolic equivalence and semantic consistency. Symbolic equivalence identifies logical homogeneity among candidates using automated theorem provers, while semantic consistency evaluates the preservation of the original meaning by informalizing the candidates and computing the similarity between the embeddings of the original and informalized texts.
   - **Year**: 2024

2. **Title**: ReForm: Reflective Autoformalization with Prospective Bounded Sequence Optimization (arXiv:2510.24592)
   - **Authors**: Guoxin Chen, Jing Wu, Xinjie Chen, Wayne Xin Zhao, Ruihua Song, Chengxi Li, Kai Fan, Dayiheng Liu, Minpeng Liao
   - **Summary**: ReForm is a reflective autoformalization method that integrates semantic consistency evaluation into the autoformalization process. It enables the model to iteratively generate formal statements, assess their semantic fidelity, and self-correct identified errors through progressive refinement. The training employs Prospective Bounded Sequence Optimization to ensure accurate autoformalization and correct semantic validations.
   - **Year**: 2025

3. **Title**: FormalAlign: Automated Alignment Evaluation for Autoformalization (arXiv:2410.10135)
   - **Authors**: Jianqiao Lu, Yingjia Wan, Yinya Huang, Jing Xiong, Zhengying Liu, Zhijiang Guo
   - **Summary**: FormalAlign is an automated framework designed to evaluate the alignment between natural and formal languages in autoformalization. It trains on both the autoformalization sequence generation task and the representational alignment between input and output, employing a dual loss that combines autoformalization and alignment tasks.
   - **Year**: 2024

4. **Title**: FormaRL: Enhancing Autoformalization with no Labeled Data (arXiv:2508.18914)
   - **Authors**: Yanxing Huang, Xinling Jin, Sijie Liang, Peng Li, Yang Liu
   - **Summary**: FormaRL is a reinforcement learning framework for autoformalization that requires only a small amount of unlabeled data. It integrates syntax checks from Lean compiler and consistency checks from large language models to calculate rewards, adopting the GRPO algorithm to update the formalizer.
   - **Year**: 2025

5. **Title**: LTRAG: Enhancing Autoformalization and Self-refinement for Logical Reasoning with Thought-Guided RAG
   - **Authors**: Ruikang Hu, Shaoyu Lin, Yeliang Xiu, Yongmei Liu
   - **Summary**: LTRAG is a framework that enhances autoformalization and self-refinement for logical reasoning using Retrieval-Augmented Generation (RAG). It builds knowledge bases of thought-guided examples to improve performance on logical reasoning tasks.
   - **Year**: 2025

6. **Title**: Consistent Autoformalization for Constructing Mathematical Libraries
   - **Authors**: Lan Zhang, Xin Quan, Andre Freitas
   - **Summary**: This paper proposes mechanisms such as most-similar retrieval augmented generation (MS-RAG), denoising steps, and auto-correction with syntax error feedback (Auto-SEF) to improve the consistency of autoformalization results, making them syntactically, terminologically, and semantically more consistent.
   - **Year**: 2024

7. **Title**: Rethinking and Improving Autoformalization: Towards a Faithful Metric and a Dependency Retrieval-based Approach
   - **Authors**: Qi Liu, Xinhao Zheng, Xudong Lu, Qinxiang Cao, Junchi Yan
   - **Summary**: This paper addresses the absence of faithful and universal automated evaluation for autoformalization results and the lack of contextual information, which induces severe hallucination of formal definitions and theorems. It proposes BEq (Bidirectional Extended Definitional Equivalence), an automated neuro-symbolic method to determine the equivalence between two formal statements.
   - **Year**: 2025

8. **Title**: Autoformalization with Large Language Models
   - **Authors**: Yuhuai Wu, Albert Jiang, Charles Edgar Staats, Christian Szegedy, Markus Rabe, Mateja Jamnik, Wenda Li
   - **Summary**: This study demonstrates that large language models can correctly translate a significant portion of mathematical competition problems to formal specifications in Isabelle/HOL. The autoformalized theorems improve the performance of a neural theorem prover, achieving state-of-the-art results on the MiniF2F benchmark.
   - **Year**: 2022

9. **Title**: Natural Language Translation of Formal Proofs through Informalization of Proof Steps and Recursive Summarization along Proof Structure
   - **Authors**: Seiji Hattori, Takuya Matsuzaki, Makoto Fujiwara
   - **Summary**: This paper presents a method for translating formal proofs into natural language by informalizing proof steps and recursively summarizing along the proof structure, aiming to make formal proofs more accessible and understandable.
   - **Year**: 2025

10. **Title**: Towards Autoformalization of Mathematics and Code Correctness: Experiments with Elementary Proofs
    - **Authors**: Garett Cunningham, Razvan Bunescu, David Juedes
    - **Summary**: This work explores the autoformalization of elementary mathematical proofs and code correctness, conducting experiments to assess the feasibility and challenges of translating informal proofs into formal language.
    - **Year**: 2022

**Key Challenges:**

1. **Data Scarcity**: The limited availability of parallel corpora of informal and formal mathematical statements hampers the training of effective autoformalization models.

2. **Semantic Drift**: Ensuring that the formalized statements accurately preserve the original meaning of the informal statements remains a significant challenge.

3. **Evaluation Metrics**: The absence of faithful and universal automated evaluation methods for autoformalization results makes it difficult to assess and compare model performance.

4. **Contextual Understanding**: Models often lack the ability to incorporate contextual information, leading to hallucinations or inaccuracies in formal definitions and theorems.

5. **Bidirectional Consistency**: Developing methods that enforce consistency between autoformalization and auto-informalization processes to create reliable self-supervised training signals without extensive human annotation is challenging. 