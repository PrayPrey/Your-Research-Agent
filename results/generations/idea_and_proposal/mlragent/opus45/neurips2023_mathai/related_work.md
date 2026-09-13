1. **Title**: SMART: Self-Generating and Self-Validating Multi-Dimensional Assessment for LLMs' Mathematical Problem Solving (arXiv:2505.16646)
   - **Authors**: Yujie Hou, Ting Zhang, Mei Wang, Xuetao Ma, Hu Huang
   - **Summary**: This paper introduces SMART, a framework that decomposes mathematical problem-solving into four dimensions: understanding, reasoning, arithmetic, and reflection & refinement. It employs an automated mechanism to generate and validate benchmark data, enabling scalable and reliable evaluation of LLMs' mathematical reasoning capabilities.
   - **Year**: 2025

2. **Title**: Mathador-LM: A Dynamic Benchmark for Mathematical Reasoning on Large Language Models (arXiv:2406.12572)
   - **Authors**: Eldar Kurtic, Amir Moeini, Dan Alistarh
   - **Summary**: Mathador-LM presents a dynamic benchmark inspired by the Mathador game, where LLMs generate evaluation instances with controllable difficulty levels. This approach addresses concerns about test-set leakage and provides a more accurate assessment of LLMs' mathematical reasoning abilities.
   - **Year**: 2024

3. **Title**: DyVal: Dynamic Evaluation of Large Language Models for Reasoning Tasks (arXiv:2309.17167)
   - **Authors**: Kaijie Zhu, Jiaao Chen, Jindong Wang, Neil Zhenqiang Gong, Diyi Yang, Xing Xie
   - **Summary**: DyVal introduces a protocol for dynamically evaluating LLMs by generating challenging evaluation sets with controllable complexities. It focuses on reasoning tasks, including mathematics, logical reasoning, and algorithm problems, highlighting the significance of dynamic evaluation in assessing LLMs' capabilities.
   - **Year**: 2023

4. **Title**: DARG: Dynamic Evaluation of Large Language Models via Adaptive Reasoning Graph (arXiv:2406.17271)
   - **Authors**: Zhehao Zhang, Jiaao Chen, Diyi Yang
   - **Summary**: DARG proposes a framework that dynamically extends current benchmarks by perturbing reasoning graphs to generate novel testing data with varying complexity levels. This method aims to adaptively evaluate LLMs' reasoning abilities and maintain benchmark relevance as models evolve.
   - **Year**: 2024

5. **Title**: DeepSeek LLM (arXiv:2401.02954)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: DeepSeek LLM is a large language model that demonstrates exceptional performance on math-related tasks across different languages. It utilizes programs to solve math problems, showcasing its superiority in mathematical reasoning and problem-solving capabilities.
   - **Year**: 2024

6. **Title**: PlanBench: An Extensible Benchmark for Evaluating Large Language Models on Planning and Reasoning about Change (arXiv:2206.10498)
   - **Authors**: Karthik Valmeekam, Matthew Marquez, Alberto Olmo, Sarath Sreedharan, Subbarao Kambhampati
   - **Summary**: PlanBench introduces a benchmark suite based on domains used in automated planning to test LLMs' capabilities in planning and reasoning about actions and change. It provides diversity in task domains and planning capabilities, highlighting areas where LLMs' performance falls short.
   - **Year**: 2023

7. **Title**: ACTIONREASONINGBENCH: Reasoning about Actions (arXiv:2406.04046)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This benchmark evaluates LLMs across various aspects of reasoning about actions and change, including object tracking, fluent tracking, state tracking, and action executability. It identifies performance degradation with increasing action-sequence lengths and challenges in reasoning about negated fluents.
   - **Year**: 2024

8. **Title**: On Scalable Oversight with Weak LLMs Judging Strong LLMs (arXiv:2407.04622)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper discusses the concept of using weaker LLMs to oversee and judge the outputs of stronger LLMs, aiming to address challenges in scalable oversight and evaluation of advanced language models.
   - **Year**: 2024

9. **Title**: Towards A Unified View of Answer Calibration for Multi-Step Reasoning (arXiv:2311.09101)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The paper presents an empirical study on answer calibration strategies for multi-step reasoning tasks, proposing a unified method that integrates step-level and path-level answer calibration to enhance accuracy and consistency in LLMs' reasoning processes.
   - **Year**: 2023

**Key Challenges:**

1. **Static Benchmark Saturation**: Traditional static benchmarks quickly become outdated as LLMs improve, leading to inflated performance metrics that do not accurately reflect genuine reasoning capabilities.

2. **Distinguishing True Understanding from Pattern Matching**: Existing benchmarks often fail to differentiate between models that truly understand mathematical concepts and those that rely on pattern recognition, resulting in misleading assessments of reasoning abilities.

3. **Dynamic Evaluation Frameworks**: Developing evaluation frameworks that adapt to the evolving capabilities of LLMs while maintaining consistent difficulty calibration is challenging but necessary for meaningful progress measurement.

4. **Scalability and Reliability of Benchmark Data**: Ensuring that dynamically generated benchmark data is both scalable and reliable requires automated mechanisms for data generation and validation, which can be complex to implement effectively.

5. **Early Detection of Reasoning Shortcuts**: Identifying and mitigating reasoning shortcuts that models may exploit is crucial to ensure that benchmarks accurately assess genuine mathematical reasoning rather than superficial problem-solving strategies. 