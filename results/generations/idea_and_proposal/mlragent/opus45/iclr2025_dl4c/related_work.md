1. **Title**: CosmoCore: Affective Dream-Replay Reinforcement Learning for Code Generation (arXiv:2510.18895)
   - **Authors**: Santhosh Kumar Ravindran
   - **Summary**: This paper introduces CosmoCore, a reinforcement learning architecture inspired by neuroscience that integrates affective signals to enhance code generation in large language models. By tagging code generation trajectories with valence and surprise, the system prioritizes high-negative valence episodes for replay, reducing hallucinated code and accelerating self-correction.
   - **Year**: 2025

2. **Title**: Aligning Crowd-sourced Human Feedback for Reinforcement Learning on Code Generation by Large Language Models (arXiv:2503.15129)
   - **Authors**: Man Fai Wong, Chee Wei Tan
   - **Summary**: This study explores the integration of crowd-sourced human feedback into reinforcement learning to enhance code generation by large language models. The authors propose a Bayesian optimization framework that distributes the feedback collection burden, demonstrating improved text-to-code generation through effective alignment with human preferences.
   - **Year**: 2025

3. **Title**: ACE-RLHF: Automated Code Evaluation and Socratic Feedback Generation Tool using Large Language Models and Reinforcement Learning with Human Feedback (arXiv:2504.04657)
   - **Authors**: Tasnia Rahman, Sathish A. P. Kumar, Sumit Jha, Arvind Ramanathan
   - **Summary**: The authors present ACE-RLHF, a tool that fine-tunes large language models with reinforcement learning from human feedback to generate Socratic feedback for erroneous code. The system combines open-source LLMs with optimization techniques, achieving higher accuracy in code feedback generation compared to state-of-the-art methods.
   - **Year**: 2025

4. **Title**: Process Supervision-Guided Policy Optimization for Code Generation (arXiv:2410.17621)
   - **Authors**: Ning Dai, Zheng Wu, Renjie Zheng, Ziyun Wei, Wenlei Shi, Xing Jin, Guanlin Liu, Chen Dun, Liang Huang, Lin Yan
   - **Summary**: This paper proposes a Process Reward Model (PRM) that provides dense, line-level feedback on code correctness during generation. By delivering immediate guidance, the PRM enhances reinforcement learning efficiency, particularly in long-horizon code generation tasks.
   - **Year**: 2024

5. **Title**: OpenRLHF: An Easy-to-use, Scalable and High-performance RLHF Framework (arXiv:2405.11143)
   - **Authors**: Not specified
   - **Summary**: OpenRLHF introduces a user-friendly, scalable, and high-performance framework for reinforcement learning from human feedback. Built upon Ray, vLLM, DeepSpeed, and HuggingFace Transformers, it simplifies the design and implementation of RLHF, achieving superior training efficiency across different model sizes.
   - **Year**: 2024

6. **Title**: Reinforcement Learning from Human Feedback for Enhanced Code Generation and Debugging Capabilities in LLMs
   - **Authors**: Aarthi Anbalagan, Muthuraman Saminathan, Vincent Kanka
   - **Summary**: This research focuses on developing and optimizing RLHF pipelines to improve the coding accuracy of large language models. By integrating human feedback mechanisms, the study aims to enhance code generation and debugging capabilities, addressing challenges like logical errors and adherence to best practices.
   - **Year**: 2024

7. **Title**: RRHF: Rank Responses to Align Language Models with Human Feedback without Tears (arXiv:2304.05302)
   - **Authors**: Zheng Yuan, Hongyi Yuan, Chuanqi Tan, Wei Wang, Songfang Huang, Fei Huang
   - **Summary**: The authors propose RRHF, a learning paradigm that scores sampled responses via conditional probabilities and aligns them with human preferences through ranking loss. RRHF efficiently aligns language models with human feedback without complex hyperparameter tuning, demonstrating comparable performance to PPO.
   - **Year**: 2023

8. **Title**: Learning to Solve and Verify: A Self-Play Framework for Code and Test Generation (arXiv:2502.14948)
   - **Authors**: Zi Lin, Sheng Shen, Jingbo Shang, Jason Weston, Yixin Nie
   - **Summary**: Sol-Ver is a self-play solver-verifier framework that jointly improves a single model's code and test generation capacity. By generating and verifying its own solutions, the model enhances its performance on coding benchmarks without relying on external data.
   - **Year**: 2025

9. **Title**: Self-Challenging Language Model Agents (arXiv:2506.01716)
   - **Authors**: Yifei Zhou, Sergey Levine, Jason Weston, Xian Li, Sainbayar Sukhbaatar
   - **Summary**: This paper introduces the Self-Challenging framework, where language model agents generate their own tasks and solutions, using a novel "Code-as-Task" approach. This method allows agents to create and solve high-quality tasks, improving their problem-solving capabilities through self-play.
   - **Year**: 2025

10. **Title**: Execution Guided Line-by-Line Code Generation (arXiv:2506.10948)
    - **Authors**: Boaz Lavon, Shahar Katz, Lior Wolf
    - **Summary**: The authors present EG-CFG, a method that incorporates real-time execution signals into the code generation process. By providing line-by-line feedback during generation, the system guides the model toward executable solutions, enhancing the quality and correctness of generated code.
    - **Year**: 2025

**Key Challenges:**

1. **Sparse and Delayed Rewards**: Many reinforcement learning approaches in code generation rely on pass/fail signals, leading to sparse and delayed rewards that hinder efficient learning and incremental improvements.

2. **Dependence on High-Quality Human Feedback**: Obtaining high-quality human feedback is resource-intensive and doesn't scale well, limiting the effectiveness of RLHF methods in code generation tasks.

3. **Error Accumulation in Self-Generated Data**: Naively training on a model's own outputs can cause error accumulation, especially in coding tasks, where generalization may collapse due to overly simple or erroneous training data.

4. **Complexity of Reinforcement Learning Frameworks**: Existing RLHF frameworks often face challenges such as inference bottlenecks and complexity barriers, restricting their accessibility and scalability.

5. **Alignment with Human Preferences**: Ensuring that code generation models align with human preferences and values is challenging, particularly when relying on automated feedback mechanisms that may not fully capture nuanced human requirements. 