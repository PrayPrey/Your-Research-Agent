1. **Title**: Language Model Uncertainty Quantification with Attention Chain (arXiv:2503.19168)
   - **Authors**: Yinghao Li, Rushi Qiang, Lama Moukheiber, Chao Zhang
   - **Summary**: This paper introduces UQAC, a method that constructs an "attention chain" to identify semantically crucial tokens influencing the final answer. By iteratively backtracking from answer tokens using attention weights, the method approximates marginal probabilities, providing reliable uncertainty estimates for LLM outputs.
   - **Year**: 2025

2. **Title**: Revisiting Uncertainty Estimation and Calibration of Large Language Models (arXiv:2505.23854)
   - **Authors**: Linwei Tao, Yi-Fan Yeh, Minjing Dong, Tao Huang, Philip Torr, Chang Xu
   - **Summary**: This comprehensive study evaluates 80 LLMs on uncertainty estimation methods, including token probability-based, numerical verbal, and linguistic verbal uncertainties. The findings highlight that linguistic verbal uncertainty offers superior calibration and interpretability, emphasizing the need for multi-perspective evaluation in LLM reliability.
   - **Year**: 2025

3. **Title**: Graph-based Confidence Calibration for Large Language Models (arXiv:2411.02454)
   - **Authors**: Yukun Li, Sijia Wang, Lifu Huang, Li-Ping Liu
   - **Summary**: The authors propose a method combining LLM self-consistency with labeled data to train an auxiliary model for estimating response correctness. Utilizing a weighted graph to represent response consistency, a graph neural network is trained to predict correctness probabilities, improving confidence calibration across multiple benchmarks.
   - **Year**: 2024

4. **Title**: Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey (arXiv:2503.15850)
   - **Authors**: Xiaoou Liu, Tiejin Chen, Longchao Da, Chacha Chen, Zhen Lin, Hua Wei
   - **Summary**: This survey addresses the challenges of LLM reliability by introducing a taxonomy categorizing uncertainty quantification methods based on computational efficiency and uncertainty dimensions. It evaluates existing techniques, assesses real-world applicability, and identifies open challenges, emphasizing the need for scalable and interpretable approaches.
   - **Year**: 2025

5. **Title**: On Leveraging Large Language Models for Uncertainty Estimation (arXiv:2401.03426)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper explores methods for leveraging LLMs to estimate uncertainty in their outputs. It discusses various approaches and evaluates their effectiveness in reducing uncertainty across different datasets and budget constraints.
   - **Year**: 2024

6. **Title**: Uncertainty of Thoughts: Uncertainty-Aware Planning (arXiv:2402.03271)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors introduce a framework for uncertainty-aware planning in LLMs, emphasizing the importance of considering uncertainty in decision-making processes. The study evaluates various models and methods, highlighting the benefits of incorporating uncertainty estimation in planning tasks.
   - **Year**: 2024

7. **Title**: Large Language Models have Intrinsic Self-Correction (arXiv:2406.15673)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper investigates the intrinsic self-correction capabilities of LLMs, providing theoretical analyses and empirical experiments. It argues that intrinsic self-correction is a form of self-verification and chain-of-thought reasoning, emphasizing the importance of zero temperature and fair prompts.
   - **Year**: 2024

8. **Title**: TASTE: Teaching Large Language Models to Translate (arXiv:2406.08434)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors present TASTE, a method for teaching LLMs to perform translation tasks. The study evaluates various models and training strategies, highlighting the effectiveness of the proposed approach in improving translation quality.
   - **Year**: 2024

**Key Challenges:**

1. **Overconfidence in Incorrect Outputs**: LLMs often generate factually incorrect or fabricated content with high confidence, leading users to trust unreliable outputs.

2. **Poor Calibration of Confidence Estimates**: Existing methods for estimating confidence in LLM outputs are often poorly calibrated, failing to accurately reflect the reliability of the generated content.

3. **Computational Constraints**: Traditional uncertainty quantification methods may struggle with LLMs due to computational constraints and decoding inconsistencies, making it challenging to implement effective uncertainty estimation.

4. **Complexity of Intermediate Reasoning Steps**: Incorporating intermediate reasoning steps in LLM responses adds complexity to uncertainty quantification, as probabilities assigned to answer tokens are conditioned on a vast space of preceding reasoning tokens.

5. **Lack of Interpretability**: Many existing uncertainty estimation methods lack interpretability, making it difficult for users to understand and trust the confidence scores provided by LLMs. 