## Related Work

**Related Papers**
1. **Title**: The Psychology of Curiosity: A Review and Reinterpretation
   - **Authors**: Loewenstein, G.
   - **Summary**: Establishes Information Gap Theory - proposes that humans explore to resolve narrative tension and knowledge gaps, providing the theoretical foundation for narrative coherence as an exploration driver.
   - **Year**: 1994

2. **Title**: Exploration by Random Network Distillation
   - **Authors**: Burda et al.
   - **Summary**: Establishes RND as state-of-the-art state-novelty exploration method using prediction error to drive exploration in reinforcement learning.
   - **Year**: 2018

3. **Title**: Curiosity-driven Exploration by Self-supervised Prediction
   - **Authors**: Pathak et al.
   - **Summary**: Introduces Intrinsic Curiosity Module (ICM) that uses forward model prediction error as exploration bonus for reinforcement learning agents.
   - **Year**: 2017

4. **Title**: Survey on LLM-Enhanced RL (Semantic Scholar ID: c44471e846846bde281779405a3b5c132fd60b00)
   - **Authors**: Not specified
   - **Summary**: Comprehensive survey identifying LLM roles in RL (planner, reward generator, information processor) and identifying the gap that no existing work addresses LLM-based exploration bonuses.
   - **Year**: 2024

5. **Title**: RL/LLM Taxonomy Tree (Semantic Scholar ID: c362015d426c90ec01e1ad02bf3fd66ab8fd0fd9)
   - **Authors**: Not specified
   - **Summary**: Provides taxonomy of LLM-RL integration approaches, confirming that no "exploration" category exists in current taxonomy frameworks.
   - **Year**: 2024

6. **Title**: Goal-Guided RL
   - **Authors**: Not specified
   - **Summary**: Uses LLMs to generate intermediate subgoals for long-horizon tasks, providing a comparison approach that uses discrete subgoals rather than continuous intrinsic rewards.
   - **Year**: 2025

7. **Title**: TinyVLA (Semantic Scholar ID: dc62bc6536e9e3ad80242f10f44c046e4c7bd3d1)
   - **Authors**: Not specified
   - **Summary**: Vision-language-action model for robotic control with efficient state encoding, demonstrating feasibility of state-to-text conversion for reinforcement learning applications.
   - **Year**: 2024

8. **Title**: Prediction with Action (PAD) (Semantic Scholar ID: 3fbf40b6d2125b0593f34d8e5e597abc00c976eb)
   - **Authors**: Not specified
   - **Summary**: Uses visual pretraining to improve sample efficiency in RL, demonstrating the value of semantic priors for decision making.
   - **Year**: 2024

9. **Title**: Generative Skill Chaining (Semantic Scholar ID: 7090d35c316afe869440ede6ad61fdeec85b8bc8)
   - **Authors**: Not specified
   - **Summary**: Uses generative models to chain skills for long-horizon tasks, addressing similar long-horizon problems through skill composition rather than exploration.
   - **Year**: 2023

10. **Title**: Narrative Coherence Metrics (NLP Literature)
    - **Authors**: Not specified
    - **Summary**: Establishes methods for evaluating story completeness in text generation, providing foundation for operationalizing narrative coherence in RL context through technique transfer.
    - **Year**: Not specified

11. **Title**: Curiosity and Boring Environments
    - **Authors**: Schmidhuber
    - **Summary**: Original intrinsic motivation work that laid the foundation for exploration driven by novelty and curiosity in artificial agents.
    - **Year**: 1991

12. **Title**: CLIP
    - **Authors**: Radford et al.
    - **Summary**: Vision-language model used for state encoding in vision-language environments, enabling multimodal state representations.
    - **Year**: 2021

13. **Title**: NetHack environment paper
    - **Authors**: Küttler et al.
    - **Summary**: Introduces the NetHack learning environment, a complex roguelike game used for testing long-horizon reinforcement learning algorithms.
    - **Year**: 2020

14. **Title**: Crafter benchmark
    - **Authors**: Hafner
    - **Summary**: Introduces Crafter, a benchmark environment for evaluating reinforcement learning agents on survival skills and long-term planning.
    - **Year**: 2021

**Key Challenges**
1. **Semantic vs Syntactic Exploration**: Traditional exploration methods (RND, ICM) operate on syntactic/pixel-level patterns rather than semantic understanding of causal narratives, missing opportunities for meaningful exploration in semantically-rich environments.

2. **No LLM-based Exploration Bonuses**: Existing LLM-RL integration work focuses on planning, reward generation, and information processing, but no prior work addresses using LLMs to generate exploration bonuses based on narrative understanding.

3. **Long-Horizon Sparse Rewards**: Current exploration methods struggle with tasks requiring >50 step causal dependencies where reward signals are sparse and delayed, making random exploration inefficient.

4. **State-to-Text Conversion Gap**: While vision-language models exist, there's limited work on converting RL environment states to natural language descriptions that preserve task-relevant causal information for downstream reasoning.

5. **Coherence-Value Correlation Unknown**: It's unclear whether LLM-assessed narrative incompleteness actually correlates with exploration value for task progress, representing a critical validation gap.

6. **Computational Overhead**: Integrating LLM inference into RL training loops introduces computational overhead that may limit practical applicability, requiring efficiency optimizations.

7. **Generalization Across Environments**: Whether narrative coherence principles transfer across different semantically-rich environments (text games, vision-language robotics, simulators) remains unvalidated.

8. **Prompt Stability**: Few-shot prompting consistency across trajectory segments and different LLM models is uncertain, potentially introducing noise into exploration signals.
