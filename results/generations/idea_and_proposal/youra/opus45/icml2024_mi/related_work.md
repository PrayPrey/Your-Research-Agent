## Related Work

**Related Papers**
1. **Title**: RLHF Deciphered: A Critical Analysis of Reinforcement Learning from Human Feedback for LLMs (arXiv:2404.08555)
   - **Authors**: Chaudhari, Aggarwal, Murahari et al.
   - **Summary**: Provides critical analysis of RLHF for LLMs, documenting reward model misspecification, incorrect generalization, and sparse feedback as key problems in current approaches.
   - **Year**: 2024

2. **Title**: A Prospect-Theoretic Policy Gradient Framework for Behaviorally Nuanced RL (arXiv:2410.02605)
   - **Authors**: Lepel, Barakat
   - **Summary**: Derives a policy gradient theorem for Cumulative Prospect Theory (CPT) objectives, proving that prospect theory integration into reinforcement learning is tractable.
   - **Year**: 2025

3. **Title**: Learning Prospect Theory Value Function and Reference Point
   - **Authors**: Nar, Ratliff, Sastry
   - **Summary**: Demonstrates that prospect theory parameters can be learned from observed decisions using an Expectation-Maximization algorithm.
   - **Year**: Not specified

4. **Title**: Bounded Rationality for LLMs: Satisficing Alignment (arXiv:2505.23729)
   - **Authors**: Chehade et al.
   - **Summary**: Establishes precedent for applying bounded rationality concepts to LLM alignment, achieving 22.3% improvement over baseline methods.
   - **Year**: 2025

5. **Title**: Robust Reinforcement Learning from Corrupted Human Feedback
   - **Authors**: Bukharin et al.
   - **Summary**: Proposes the R³M method that treats feedback corruption as sparse outliers, providing a noise filtering approach to handling corrupted human feedback.
   - **Year**: 2024

6. **Title**: Distributionally Robust RLHF
   - **Authors**: Mandal et al.
   - **Summary**: Applies Distributionally Robust Optimization (DRO) for out-of-distribution robustness in RLHF settings.
   - **Year**: 2025

7. **Title**: Behavioral Neural Networks (AEA 2020)
   - **Authors**: Ke, Zhao, Wang, Hsieh
   - **Summary**: Provides axiomatic foundation for neural network models that capture behavioral effects including certainty effect and reference dependence, proving neural networks can model cognitive biases.
   - **Year**: 2020

8. **Title**: OpenAI Instruction Following Blog
   - **Authors**: Not specified
   - **Summary**: Documents the standard RLHF pipeline, operating under the assumption of consistent annotator preferences.
   - **Year**: Not specified

**Key Challenges**
1. **Reward Model Misspecification**: Current RLHF approaches suffer from reward models that do not accurately capture human preferences, leading to incorrect generalization and sparse feedback problems.

2. **Assumption of Consistent Annotator Preferences**: Standard RLHF pipelines assume annotators have consistent preferences, failing to account for systematic cognitive biases in human feedback.

3. **Noise vs. Systematic Bias Treatment**: Existing robust methods treat feedback inconsistencies as sparse outliers or noise rather than modeling the underlying systematic patterns of human cognitive biases.

4. **Limited Integration of Behavioral Economics**: Despite evidence that neural networks can model cognitive biases like certainty effects and reference dependence, current alignment methods do not leverage prospect theory or bounded rationality frameworks to model human decision-making.

5. **Out-of-Distribution Robustness**: Current approaches address distributional robustness without accounting for the behavioral mechanisms that cause preference inconsistencies across different contexts.
