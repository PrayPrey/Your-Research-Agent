## Related Work

**Related Papers**
1. **Title**: Replay in Deep Learning: Current Approaches and Missing Biological Elements
   - **Authors**: Hayes, Krishnan, Bazhenov, Siegelmann, Sejnowski, Kanan
   - **Summary**: First comprehensive comparison of biological and artificial replay mechanisms; identifies surprise-based prioritization as a key missing element in deep learning systems.
   - **Year**: 2021

2. **Title**: Understanding Black-box Predictions via Influence Functions
   - **Authors**: Koh, Liang
   - **Summary**: Establishes foundational technique for tracing model predictions to training data through gradient-based influence computation with O(n) complexity per test point.
   - **Year**: 2017

3. **Title**: Improving Data Efficiency for LLM RL Fine-tuning Through Difficulty-targeted Online Data Selection
   - **Authors**: Sun, Shen, Wang, Chen, Wang, Zhou, Zhang
   - **Summary**: Achieves 23-62% training time reduction through adaptive difficulty targeting, validating online data selection approaches for LLM training.
   - **Year**: 2025

4. **Title**: Estimating Training Data Influence by Tracking Gradient Descent (TracIn)
   - **Authors**: Pruthi et al.
   - **Summary**: Proposes a checkpoint-based attribution method for estimating training data influence on model predictions.
   - **Year**: 2020

5. **Title**: What is Your Data Worth to GPT? (LoGra)
   - **Authors**: Choe et al.
   - **Summary**: State-of-the-art post-hoc attribution method achieving 6,500x speedup over prior approaches while maintaining O(n) complexity.
   - **Year**: 2024

6. **Title**: Consistency Models Training Patterns (Archon KB)
   - **Authors**: Not specified
   - **Summary**: Analysis from OpenAI consistency_models repository revealing that current training pipelines lack real-time attribution feedback mechanisms.
   - **Year**: Not specified

7. **Title**: Align Your Steps (Archon KB)
   - **Authors**: Not specified
   - **Summary**: NVIDIA research demonstrating that sampling strategies significantly impact training dynamics, supporting importance-weighted training approaches.
   - **Year**: Not specified

**Key Challenges**
1. **Missing Surprise-Based Prioritization**: Current deep learning replay mechanisms lack the surprise-based prioritization found in biological systems, limiting their effectiveness for selective data replay.
2. **Computational Complexity of Influence Estimation**: Existing influence function methods require O(n) complexity per test point, making real-time attribution computationally prohibitive for large-scale training.
3. **Lack of Real-Time Attribution Feedback**: Current training pipelines do not incorporate real-time attribution feedback, preventing adaptive data selection during training.
4. **Post-Hoc vs. Online Attribution**: State-of-the-art attribution methods remain post-hoc analyses rather than integrated online components, limiting their utility for dynamic training optimization.
