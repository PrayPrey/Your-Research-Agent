Here is a literature review on the development of Compositional Reasoning Probes (CRPs) for detecting and steering System-2 emergence in transformers, focusing on related works from 2023 to 2025.

**1. Related Papers:**

1. **Title**: Layer Specialization Underlying Compositional Reasoning in Transformers (arXiv:2510.17469)
   - **Authors**: Jing Liu
   - **Summary**: This study investigates how transformers develop compositional reasoning capabilities by analyzing layer specialization. Using the Random Hierarchy Model, the research demonstrates that transformers exhibit structured, hierarchically organized representations in specialized layers, correlating with improved generalization performance.
   - **Year**: 2025

2. **Title**: Strassen Attention: Unlocking Compositional Abilities in Transformers Based on a New Lower Bound Method (arXiv:2501.19215)
   - **Authors**: Alexander Kozachinskiy, Felipe Urrutia, Hector Jimenez, Tomasz Steifer, Germán Pizarro, Matías Fuentes, Francisco Meza, Cristian B. Calderon, Cristóbal Rojas
   - **Summary**: This paper introduces Strassen attention, a novel mechanism designed to enhance the compositional reasoning abilities of transformers. The authors provide theoretical proofs of the limitations of one-layer softmax transformers and demonstrate that Strassen attention can overcome these limitations, achieving sub-cubic running-time complexity.
   - **Year**: 2025

3. **Title**: Complexity Control Facilitates Reasoning-Based Compositional Generalization in Transformers (arXiv:2501.08537)
   - **Authors**: Zhongwang Zhang, Pengxiao Lin, Zhiwei Wang, Yaoyu Zhang, Zhi-Qin John Xu
   - **Summary**: The authors explore how complexity control strategies influence transformers' ability to generalize in compositional tasks. They find that lower complexity biases enable models to learn reasoning rules effectively, leading to improved out-of-distribution generalization.
   - **Year**: 2025

4. **Title**: Are Transformers Able to Reason by Connecting Separated Knowledge in Training Data? (arXiv:2501.15857)
   - **Authors**: Yutong Yin, Zhaoran Wang
   - **Summary**: This paper introduces the "FTCT" task to assess transformers' ability to perform compositional reasoning by integrating fragmented knowledge. The study shows that few-shot Chain-of-Thought prompting enables transformers to connect separated knowledge fragments, even when such combinations were absent during training.
   - **Year**: 2025

5. **Title**: Compositional Reasoning with Transformers, RNNs, and Chain of Thought (arXiv:2503.01544)
   - **Authors**: Gilad Yehudai, Noah Amsel, Joan Bruna
   - **Summary**: The authors compare the expressive power of transformers, RNNs, and transformers with Chain-of-Thought tokens on compositional reasoning tasks. They provide constructions for each architecture to solve these tasks, highlighting the strengths and weaknesses of each approach.
   - **Year**: 2025

6. **Title**: Faith and Fate: Limits of Transformers on Compositionality (arXiv:2305.18654)
   - **Authors**: Nouha Dziri, Ximing Lu, Melanie Sclar, Xiang Lorraine Li, Liwei Jiang, Bill Yuchen Lin, Peter West, Chandra Bhagavatula, Ronan Le Bras, Jena D. Hwang, Soumya Sanyal, Sean Welleck, Xiang Ren, Allyson Ettinger, Zaid Harchaoui, Yejin Choi
   - **Summary**: This work investigates the fundamental limits of transformer language models on tasks requiring multi-step compositional reasoning. The authors find that success largely arises from pattern memorization rather than systematic reasoning, with error propagation causing exponential degradation as task complexity increases.
   - **Year**: 2023

7. **Title**: Disentangling Reasoning Capabilities from Language Models with Compositional Reasoning Transformers (arXiv:2210.11265)
   - **Authors**: Wanjun Zhong, Tingting Ma, Jiahai Wang, Jian Yin, Tiejun Zhao, Chin-Yew Lin, Nan Duan
   - **Summary**: The authors present ReasonFormer, a unified reasoning framework that mirrors the modular and compositional reasoning process of humans. By decoupling representation and reasoning modules, the model dynamically activates and composes reasoning skills to solve complex problems.
   - **Year**: 2023

8. **Title**: Measuring and Narrowing the Compositionality Gap in Language Models (arXiv:2210.03350)
   - **Authors**: Ofir Press, Muru Zhang, Sewon Min, Ludwig Schmidt, Noah A. Smith, Mike Lewis
   - **Summary**: This paper investigates language models' ability to perform compositional reasoning tasks by measuring the compositionality gap—the difference between answering sub-problems correctly and generating the overall solution. The authors find that as model size increases, the compositionality gap does not decrease, suggesting that larger models memorize more factual knowledge without corresponding improvements in compositional reasoning.
   - **Year**: 2023

9. **Title**: Learning Compositional Functions with Transformers from Easy-to-Hard Data (arXiv:2505.23683)
   - **Authors**: Zixuan Wang, Eshaan Nichani, Alberto Bietti, Alex Damian, Daniel Hsu, Jason D. Lee, Denny Wu
   - **Summary**: The authors study the learnability of compositional functions with transformers, demonstrating that these functions can be efficiently learned using gradient descent on a logarithmic-depth transformer. The study highlights the importance of training data complexity in learning compositional functions.
   - **Year**: 2025

10. **Title**: Monotonicity Reasoning in the Age of Neural Foundation Models
    - **Authors**: Zeming Chen, Qiyue Gao
    - **Summary**: This paper explores monotonicity reasoning within neural foundation models, discussing the integration of symbolic reasoning with neural networks to enhance compositional reasoning capabilities.
    - **Year**: 2024

**2. Key Challenges:**

1. **Distinguishing Memorization from Genuine Compositional Reasoning**: Many models achieve success through pattern memorization rather than true compositional reasoning, making it difficult to assess their reasoning capabilities.

2. **Developing Effective Probing Mechanisms**: Creating diagnostic tools that can accurately detect when models engage in compositional reasoning versus retrieval-based processing remains a significant challenge.

3. **Ensuring Generalization Across Diverse Tasks**: Models often struggle to generalize compositional reasoning skills across tasks with varying complexity and structure.

4. **Balancing Model Complexity and Interpretability**: As models become more complex to handle compositional reasoning, maintaining interpretability and transparency becomes increasingly difficult.

5. **Integrating Symbolic and Neural Approaches**: Combining symbolic reasoning methods with neural networks to enhance compositional reasoning without compromising scalability and efficiency poses a significant challenge. 