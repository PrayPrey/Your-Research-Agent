## Related Work

**Related Papers**

1. **Title**: Automated Reinforcement Learning (AutoRL): A Survey and Open Problems
   - **Authors**: Parker-Holder, Rajan, Song, Biedenkapp, et al.
   - **Summary**: Defines AutoRL taxonomy and identifies "little crossover" between LLM, Meta-RL, and AutoML communities despite solving related problems. Establishes foundational framework for categorizing automated RL approaches.
   - **Year**: 2022

2. **Title**: Meta-Learning in Neural Networks: A Survey
   - **Authors**: Hospedales, Antoniou, Micaelli, Storkey
   - **Summary**: Comprehensive survey of meta-learning foundations including MAML and Bayesian meta-learning. Establishes that meta-learning performance depends critically on task distribution quality.
   - **Year**: 2020

3. **Title**: In-Context Reinforcement Learning: A Survey
   - **Authors**: Moeini, Wang, Beck, et al.
   - **Summary**: Surveys Algorithm Distillation mechanism enabling zero-shot adaptation without gradient updates by conditioning on action-observation histories. Establishes parameter-free adaptation through in-context learning.
   - **Year**: 2025

4. **Title**: Kimi k1.5: Scaling Reinforcement Learning with LLMs
   - **Authors**: Kimi Team (70+ authors)
   - **Summary**: State-of-the-art LLM+RL integration using LLM for reasoning and planning without AutoML or closed-loop feedback. Demonstrates large-scale integration of language models with reinforcement learning.
   - **Year**: 2025

5. **Title**: Multiple Weaks Win Single Strong: LLM Ensemble for RL (LLM-Ens)
   - **Authors**: Song, Hao, Liao, Yuan, Li
   - **Summary**: LLM-based agent ensemble achieving 20.9% improvement via semantic task understanding for online agent selection. Demonstrates LLMs can categorize RL task states semantically.
   - **Year**: 2025

6. **Title**: HPO-RL-Bench: A Zero-Cost Benchmark for HPO in RL
   - **Authors**: Shala, Pineda-Arango, Biedenkapp, Hutter, Grabocka
   - **Summary**: Benchmark for evaluating AutoML hyperparameter optimization methods in reinforcement learning. Demonstrates hyperparameters significantly affect RL performance and provides evaluation infrastructure.
   - **Year**: 2024

7. **Title**: SML-AutoML: A Smart Meta-Learning Automated Machine Learning Framework
   - **Authors**: Gomaa, Mokhtar, El-Tazi, Zidane
   - **Summary**: Integrates meta-learning with AutoML for supervised learning on tabular data, lacking LLM component and task clustering refinement for RL domains.
   - **Year**: 2024

8. **Title**: EXPLORA: Efficient Exemplar Subset Selection for Complex Reasoning
   - **Authors**: Purohit, Venktesh, Devalla, et al.
   - **Summary**: LLM-based algorithm selection focusing on in-context learning exemplar selection for complex reasoning tasks.
   - **Year**: 2024

9. **Title**: Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks (MAML)
   - **Authors**: Finn
   - **Summary**: Foundational gradient-based meta-learning algorithm enabling rapid adaptation to novel tasks with few gradient steps. Establishes that task clustering quality correlates with meta-learning transfer performance.
   - **Year**: 2017

10. **Title**: Experience Replay in the Hippocampus (Neuroscience)
    - **Authors**: Foster, Wilson
    - **Summary**: Biological research on hippocampal experience replay providing inspiration for prioritized replay mechanisms in machine learning. Demonstrates how the brain consolidates important experiences during offline periods.
    - **Year**: 2010

11. **Title**: Exponential Moving Average / Polyak Averaging
    - **Authors**: Polyak, Juditsky
    - **Summary**: Theoretical foundations for convergence guarantees in online learning with momentum methods, establishing EMA theory for continuous optimization.
    - **Year**: 1992

12. **Title**: Algorithm Distillation for In-Context Learning
    - **Authors**: Laskin, Wang, Oh, et al.
    - **Summary**: Parameter-free meta-learning via context conditioning enabling adaptation without gradient updates.
    - **Year**: 2022

13. **Title**: AutoML Book / BOHB Algorithm
    - **Authors**: Feurer, Hutter
    - **Summary**: Foundational work on Bayesian Optimization for hyperparameter tuning in machine learning, establishing standard BO methods for single-task HPO.
    - **Year**: 2015

14. **Title**: MetaLLMix: LLM-Guided Meta-Learning for Medical Imaging
    - **Authors**: Not specified
    - **Summary**: Domain-specific integration of LLM, meta-learning, and AutoML for medical imaging applications without task clustering or closed-loop feedback mechanisms.
    - **Year**: 2025

15. **Title**: Options Framework (Hierarchical RL)
    - **Authors**: Sutton, Precup, Singh
    - **Summary**: Foundational work on hierarchical reinforcement learning for single-task temporal abstraction using options framework.
    - **Year**: 1999

16. **Title**: Curriculum Learning for RL Survey
    - **Authors**: Narvekar, Peng, et al.
    - **Summary**: Survey on task ordering and curriculum design for improved RL learning, focusing on temporal sequencing from easy to hard tasks.
    - **Year**: 2020

**Key Challenges**

1. **Disjoint Research Communities**: Meta-learning, AutoML, and LLM-based approaches remain largely separate despite solving related AutoRL problems, with "little crossover" between communities limiting potential synergies.

2. **Static LLM Integration**: Existing LLM+RL systems (e.g., Kimi k1.5) use static LLM guidance without feedback loops, missing opportunities for performance-based refinement of task representations.

3. **Task Distribution Quality**: Meta-learning performance depends critically on task clustering quality, yet automated approaches either ignore semantics (pure AutoML) or lack performance feedback (static LLM clustering).

4. **Lack of Convergence Guarantees**: Existing AutoRL integration approaches lack formal convergence guarantees for closed-loop feedback systems, limiting theoretical understanding and practical reliability.

5. **Missing Bidirectional Information Flow**: No existing work integrates LLM task semantics, meta-learning, and AutoML with bidirectional closed-loop feedback where AutoML discoveries update LLM context.

6. **Semantic-Parametric Gap**: Hyperparameters encode implicit task properties not obvious from language descriptions, but this "revealed preference" signal is not exploited to complement semantic task representations.

7. **Limited Cross-Domain Transfer**: Pure AutoML approaches underperform on cross-domain transfer because they miss semantic structure, while LLM-only approaches lack performance-based refinement.

8. **Manual Engineering Burden**: Current AutoRL systems require manual task engineering (expert-designed task distributions) or ignore task semantics entirely, creating scalability and performance trade-offs.

9. **Single-Task Focus**: AutoML benchmarks (HPO-RL-Bench) focus on single-task hyperparameter optimization without leveraging cross-task feedback for improving task clustering.

10. **Domain-Specific Solutions**: Integration attempts (e.g., MetaLLMix for medical imaging, SML-AutoML for supervised learning) are domain-specific and don't generalize to reinforcement learning task clustering scenarios.
