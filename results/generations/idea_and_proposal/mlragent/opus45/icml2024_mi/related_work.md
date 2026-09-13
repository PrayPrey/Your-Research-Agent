1. **Title**: Aligning Humans and Robots via Reinforcement Learning from Implicit Human Feedback (arXiv:2507.13171)
   - **Authors**: Suzie Kim, Hye-Bin Shin, Seong-Whan Lee
   - **Summary**: This paper introduces a framework that utilizes non-invasive EEG signals, specifically error-related potentials (ErrPs), to provide continuous, implicit feedback for reinforcement learning. By decoding these neural signals into probabilistic reward components, the approach enables effective policy learning in robotic systems, even under sparse external rewards.
   - **Year**: 2025

2. **Title**: Reinforcement Learning from Implicit Neural Feedback for Human-Aligned Robot Control (arXiv:2512.00050)
   - **Authors**: Suzie Kim
   - **Summary**: Building upon previous work, this study further explores the use of EEG-derived ErrPs as implicit feedback in reinforcement learning. The method demonstrates that agents trained with decoded EEG feedback achieve performance comparable to those trained with dense, manually designed rewards, validating the potential of implicit neural feedback for scalable and human-aligned reinforcement learning in interactive robotics.
   - **Year**: 2025

3. **Title**: Governance Challenges in Reinforcement Learning from Human Feedback: Evaluator Rationality and Reinforcement Stability (arXiv:2504.13972)
   - **Authors**: Dana Alsagheer, Abdulrahman Kamal, Mohammad Kamal, Weidong Shi
   - **Summary**: This paper examines how the cognitive capacity of evaluators, specifically their level of rationality, affects the stability of reinforcement signals in RLHF. The study reveals that evaluators with higher rationality scores produce more consistent and expert-aligned feedback, while lower-rationality participants demonstrate considerable variability in their reinforcement decisions.
   - **Year**: 2025

4. **Title**: Reinforcement Learning from Human Feedback with High-Confidence Safety Constraints (arXiv:2506.08266)
   - **Authors**: Yaswanth Chittepu, Blossom Metevier, Will Schwarzer, Austin Hoag, Scott Niekum, Philip S. Thomas
   - **Summary**: This work proposes HC-RLHF, a method that provides high-confidence safety guarantees while maximizing helpfulness in language model alignment. By decoupling human preferences into helpfulness and harmlessness, and employing a two-step process to find safe solutions, HC-RLHF ensures reliable performance in sensitive domains.
   - **Year**: 2025

5. **Title**: RRHF: Rank Responses to Align Language Models with Human Feedback without Tears (arXiv:2304.05302)
   - **Authors**: Zheng Yuan, Hongyi Yuan, Chuanqi Tan, Wei Wang, Songfang Huang, Fei Huang
   - **Summary**: This paper introduces RRHF, a novel learning paradigm that scores sampled responses from different sources via a logarithm of conditional probabilities and learns to align these probabilities with human preferences through ranking loss. RRHF offers a simpler and more efficient alternative to traditional RLHF methods.
   - **Year**: 2023

6. **Title**: OpenRLHF: An Easy-to-use, Scalable and High-performance RLHF Framework (arXiv:2405.11143)
   - **Authors**: Not specified
   - **Summary**: OpenRLHF is an open-source RLHF framework built upon Ray, vLLM, DeepSpeed, and HuggingFace Transformers. It features a simplified design, clear code structure, and comprehensive documentation to facilitate entry for researchers and practitioners, achieving superior training efficiency compared to state-of-the-art frameworks.
   - **Year**: 2024

7. **Title**: Explainable Reinforcement Learning from Human Feedback to Improve Alignment (arXiv:2512.13837)
   - **Authors**: Not specified
   - **Summary**: This work introduces XRLHF, a post-training framework that explains unsatisfactory outputs via an explainable, data-driven projection onto the convex hull of training data differences. It improves behavior by unlearning the contributing data from the reward model and fine-tuning the policy under a KL-constrained objective.
   - **Year**: 2025

8. **Title**: Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback (arXiv:2307.15217)
   - **Authors**: Stephen Casper, Xander Davies, Claudia Shi, Thomas Krendl Gilbert, Jérémy Scheurer, Javier Rando, Rachel Freedman, Tomasz Korbak, David Lindner, Pedro Freire, Tony Wang, Samuel Marks, Charbel-Raphaël Segerie, Micah Carroll, Andi Peng, Phillip Christoffersen, Mehul Damani, Stewart Slocum, Usman Anwar, Anand Siththaranjan, Max Nadeau, Eric J. Michaud
   - **Summary**: This paper analyzes the limitations and flaws of RLHF, providing suggestions for improvement, complementation, and oversight to enhance safer AI development.
   - **Year**: 2023

9. **Title**: Bayesian Reinforcement Learning With Limited Cognitive Load (Open Mind)
   - **Authors**: Dilip Arumugam, Noah D. Goodman, Benjamin Van Roy
   - **Summary**: This study provides an account of capacity-limited Bayesian reinforcement learning, a unifying normative framework for modeling the effect of processing constraints on learning and action selection. It bridges ideas from reinforcement learning, Bayesian decision-making, and rate-distortion theory.
   - **Year**: 2024

10. **Title**: A Survey of Reinforcement Learning from Human Feedback (arXiv:2312.14925)
    - **Authors**: Not specified
    - **Summary**: This paper surveys RLHF, outlining how human input can supplant hand-crafted reward functions to better align AI systems with human values. It provides a comprehensive taxonomy of feedback types, discusses data collection methods, and details reward-model and policy-learning pipelines.
    - **Year**: 2023

**Key Challenges**:

1. **Cognitive Load Impact on Feedback Quality**: Human annotators' feedback quality can degrade under mental fatigue and high cognitive load, leading to noisy and inconsistent data that misaligns AI systems with true human values.

2. **Implicit Feedback Interpretation**: Decoding and interpreting implicit human feedback, such as EEG signals, pose significant challenges due to variability and noise in the data, requiring robust models to extract meaningful information.

3. **Evaluator Rationality and Bias**: Variations in evaluator rationality and inherent biases can affect the consistency and reliability of reinforcement signals, complicating the alignment of AI systems with human preferences.

4. **Safety Constraints in RLHF**: Ensuring that reinforcement learning from human feedback adheres to high-confidence safety constraints is challenging, especially in sensitive domains where safety and helpfulness must be balanced.

5. **Scalability and Efficiency**: Developing scalable and efficient RLHF frameworks that are easy to use and maintain high performance remains a significant challenge, particularly when integrating complex human feedback mechanisms. 