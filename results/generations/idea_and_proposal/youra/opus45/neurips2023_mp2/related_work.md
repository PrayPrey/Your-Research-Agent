## Related Work

**Related Papers**
1. **Title**: Intuitive physics learning in a deep-learning model inspired by developmental psychology
   - **Authors**: Piloto et al.
   - **Summary**: Demonstrates that developmental psychology can successfully inform AI architecture design, achieving state-of-the-art performance in intuitive physics through developmentally-inspired training approaches.
   - **Year**: 2022

2. **Title**: On The Power of Curriculum Learning in Training Deep Networks (arXiv:1904.03626)
   - **Authors**: Hacohen & Weinshall
   - **Summary**: Provides theoretical and empirical grounding showing that curriculum learning improves convergence speed and final performance in deep network training through ordered training procedures.
   - **Year**: 2019

3. **Title**: Continual Lifelong Learning with Neural Networks: A Review
   - **Authors**: Fayek et al.
   - **Summary**: Presents a progressive learning framework incorporating curriculum procedures, progression criteria, and capacity management, serving as a direct implementation blueprint for continual learning systems.
   - **Year**: 2020

4. **Title**: Deep Reinforcement Learning from Human Preferences
   - **Authors**: Christiano et al.
   - **Summary**: Introduces standard RLHF methodology using flat preference optimization without curriculum structure, serving as a primary baseline for alignment approaches.
   - **Year**: 2017

5. **Title**: Training language models to follow instructions with human feedback
   - **Authors**: Ouyang et al.
   - **Summary**: Extends RLHF to large language models for instruction following, using flat preference data without structured curriculum.
   - **Year**: 2022

6. **Title**: Direct Preference Optimization
   - **Authors**: Rafailov et al.
   - **Summary**: Proposes a simplified alignment approach without reinforcement learning, though still utilizing flat preference data without developmental structure.
   - **Year**: 2023

7. **Title**: The Convergent Ethics of AI? Analyzing Moral Foundation Priorities in LLMs
   - **Authors**: Coleman et al.
   - **Summary**: Evaluates LLMs on Kohlberg developmental stages for assessment purposes but does not utilize this framework for training, identifying a gap in developmental approaches to moral learning.
   - **Year**: 2025

8. **Title**: Moral disagreement and the limits of AI value alignment
   - **Authors**: Schuster, Kilov
   - **Summary**: Demonstrates that current RLHF approaches fail to accommodate moral complexity and disagreement, motivating the need for more structured alignment approaches.
   - **Year**: 2025

9. **Title**: MoralBench: Moral Evaluation of LLMs (arXiv:2406.04428)
   - **Authors**: Ji et al.
   - **Summary**: Provides a benchmark for evaluating moral reasoning capabilities in language models, offering metrics for measuring effectiveness of moral learning approaches.
   - **Year**: 2024

**Key Challenges**
1. **Flat Preference Structure**: Current RLHF and DPO methods use unstructured preference data without developmental ordering, potentially limiting the depth of moral reasoning acquired.

2. **Moral Complexity Accommodation**: Existing alignment approaches fail to adequately handle moral complexity and disagreement, treating ethics as monolithic rather than developmentally structured.

3. **Evaluation-Training Gap**: While developmental psychology frameworks like Kohlberg stages have been used to evaluate LLM moral reasoning, they have not been leveraged for training, representing an unexploited opportunity.

4. **Lack of Progressive Learning in Alignment**: Current methods do not incorporate curriculum procedures, progression criteria, or capacity management principles from continual learning into moral alignment training.
