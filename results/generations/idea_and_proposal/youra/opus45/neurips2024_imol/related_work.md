## Related Work

**Related Papers**
1. **Title**: Exploration by Random Network Distillation (arXiv:1810.12894)
   - **Authors**: Burda, Edwards, Storkey, Klimov
   - **Summary**: RND provides an easy-to-implement exploration bonus via random network prediction error, achieving superhuman performance on Montezuma's Revenge.
   - **Year**: 2018

2. **Title**: Diversity is All You Need: Learning Skills without a Reward Function
   - **Authors**: Eysenbach, Gupta, Ibarz, Levine
   - **Summary**: DIAYN learns diverse skills by maximizing mutual information I(s;z) using maximum entropy policy without requiring external reward functions.
   - **Year**: 2018

3. **Title**: BAMDP Shaping: A Unified Framework for Intrinsic Motivation and Reward Shaping
   - **Authors**: Lidayan, Dennis, Russell
   - **Summary**: Demonstrates that potential-based shaping in BAMDPs is immune to reward hacking and provides theoretical grounding for safely combining intrinsic rewards.
   - **Year**: 2025

4. **Title**: Constrained Intrinsic Motivation for Reinforcement Learning (CIM)
   - **Authors**: Zheng, Ma, Shen, Wang
   - **Summary**: CIM surpasses 15 intrinsic motivation methods using constrained optimization for reward-free policy transfer.
   - **Year**: 2024

5. **Title**: Catching Two Birds with One Stone: Reward Shaping with Dual Random Networks (DuRND)
   - **Authors**: Ma, Li, Lim, Luo, Vo, Leong
   - **Summary**: Proposes dual random networks to balance exploration and exploitation efficiently through reward shaping.
   - **Year**: 2025

6. **Title**: The impact of intrinsic rewards on exploration in Reinforcement Learning
   - **Authors**: Kayal, Pignatelli, Toni
   - **Summary**: Demonstrates that different intrinsic reward types (State Count, ICM, MaxEnt, DIAYN) impact exploration differently, with DIAYN failing to promote exploration in some environments.
   - **Year**: 2025

7. **Title**: An Empowerment-based Solution to Robotic Manipulation Tasks with Sparse Rewards
   - **Authors**: Dai, Xu, Hofmann, Williams
   - **Summary**: Shows that integrating and balancing empowerment and curiosity yields superior performance in robotic manipulation tasks with sparse rewards.
   - **Year**: 2021

**Key Challenges**
1. **Single-Paradigm Limitations**: Individual intrinsic motivation approaches (prediction-based or competence-based) show inconsistent performance across different environments, with methods like DIAYN failing to promote exploration in certain settings.

2. **Adaptive Combination Need**: Different intrinsic reward types impact exploration differently, suggesting that static single-paradigm approaches are insufficient and adaptive combination strategies are required.

3. **Safe Reward Combination**: Combining multiple intrinsic reward signals risks reward hacking and instability, requiring theoretical frameworks to ensure safe integration.

4. **Exploration-Exploitation Balance**: Existing methods struggle to efficiently balance exploration and exploitation when using intrinsic motivation, particularly in sparse reward settings.
