1. **Title**: Autotelic Reinforcement Learning: Exploring Intrinsic Motivations for Skill Acquisition in Open-Ended Environments (arXiv:2502.04418)
   - **Authors**: Prakhar Srivastava, Jasmeet Singh
   - **Summary**: This paper provides a comprehensive overview of autotelic reinforcement learning, emphasizing the role of intrinsic motivations in the open-ended formation of skill repertoires. It distinguishes between knowledge-based and competence-based intrinsic motivations and explores Intrinsically Motivated Goal Exploration Processes (IMGEPs), focusing on their implications for multi-goal reinforcement learning and developmental robotics. The authors frame the autotelic learning problem within a reward-free Markov Decision Process, addressing challenges in evaluating such agents and proposing metrics for measuring exploration, generalization, and robustness in complex environments.
   - **Year**: 2025

2. **Title**: Entropy-Controlled Intrinsic Motivation Reinforcement Learning for Quadruped Robot Locomotion in Complex Terrains (arXiv:2512.06486)
   - **Authors**: Wanru Gong, Xinyi Zheng, Xiaopeng Yang, Xiaoqing Zhu
   - **Summary**: This study introduces Entropy-Controlled Intrinsic Motivation (ECIM), an entropy-based reinforcement learning algorithm designed to reduce premature convergence by combining intrinsic motivation with adaptive exploration. Applied to quadrupedal robot locomotion across various terrains, ECIM demonstrates improved performance metrics, including increased task rewards, reduced body pitch oscillation, decreased joint acceleration, and lower joint torque consumption, highlighting its effectiveness in enhancing stability and efficiency in complex robotic control tasks.
   - **Year**: 2025

3. **Title**: Curiosity-Driven Reinforcement Learning from Human Feedback (arXiv:2501.11463)
   - **Authors**: Haoran Sun, Yekun Chai, Shuohuan Wang, Yu Sun, Hua Wu, Haifeng Wang
   - **Summary**: This paper introduces Curiosity-Driven Reinforcement Learning from Human Feedback (CD-RLHF), a framework that incorporates intrinsic rewards for novel states alongside traditional sparse extrinsic rewards to optimize both output diversity and alignment quality. Through experiments on tasks like text summarization and instruction following, CD-RLHF achieves significant gains in diversity while maintaining alignment with human preferences comparable to standard RLHF.
   - **Year**: 2025

4. **Title**: Dynamic Memory-based Curiosity: A Bootstrap Approach for Exploration (arXiv:2208.11349)
   - **Authors**: Zijian Gao, YiYing Li, Kele Xu, Yuanzhao Zhai, Dawei Feng, Bo Ding, XinJun Mao, Huaimin Wang
   - **Summary**: This work presents Dynamic Memory-based Curiosity (DyMeCu), a curiosity mechanism inspired by human curiosity and information theory. DyMeCu consists of a dynamic memory and dual online learners, where curiosity arises if memorized information cannot address the current state. The information gap between dual learners is formulated as the intrinsic reward, and such state information is consolidated into the dynamic memory. Empirical experiments demonstrate that DyMeCu outperforms competitive curiosity-based methods with or without extrinsic rewards.
   - **Year**: 2023

5. **Title**: Reinforcement Learning to Optimize Long-term User Engagement in Recommender Systems (arXiv:1902.05570)
   - **Authors**: Lixin Zou, Long Xia, Zhuoye Ding, Jiaxing Song, Weidong Liu, Dawei Yin
   - **Summary**: This paper introduces FeedRec, a reinforcement learning framework designed to optimize long-term user engagement in recommender systems. FeedRec comprises a hierarchical LSTM-based Q-Network for modeling complex user behaviors and an S-Network that simulates the environment to assist the Q-Network, mitigating instability in policy learning. Experiments on synthetic and real-world data demonstrate that FeedRec effectively optimizes long-term user engagement, outperforming state-of-the-art methods.
   - **Year**: 2023

6. **Title**: Hierarchical Approaches for Reinforcement Learning in Parameterized Action Space (arXiv:1810.09656)
   - **Authors**: Ermo Wei, Drew Wicke, Sean Luke
   - **Summary**: This study explores deep reinforcement learning in parameterized action spaces, proposing a compact architecture where the parameter policy is conditioned on the output of the discrete action policy. The authors extend state-of-the-art algorithms, such as Trust Region Policy Optimization (TRPO) and Stochastic Value Gradient (SVG), to train this architecture efficiently. Experiments demonstrate that these methods outperform the Parameterized Action DDPG on test domains.
   - **Year**: 2023

7. **Title**: ELSIM: End-to-end Learning of Reusable Skills through Intrinsic Motivation (arXiv:2006.12903)
   - **Authors**: Arthur Aubret, Laetitia Matignon, Salima Hassas
   - **Summary**: Inspired by developmental learning, this paper presents a reinforcement learning architecture that hierarchically learns and represents self-generated skills in an end-to-end manner. The architecture focuses on task-rewarded skills while maintaining a bottom-up learning process, allowing for transferable skills across tasks and improved exploration in sparse reward settings. The approach combines a mutual information objective with a novel curriculum learning algorithm, creating an unlimited and explorable tree of skills.
   - **Year**: 2020

8. **Title**: Learning Reward Functions by Integrating Human Demonstrations and Preferences (arXiv:1906.08928)
   - **Authors**: Malayandi Palan, Nicholas C. Landolfi, Gleb Shevchuk, Dorsa Sadigh
   - **Summary**: This paper addresses the challenge of learning reward functions by integrating human demonstrations and preferences. The authors propose a method that combines these two sources of information to infer a reward function that aligns with human intentions. The approach is validated through experiments demonstrating its effectiveness in capturing complex human preferences.
   - **Year**: 2023

9. **Title**: Safe Driving via Expert Guided Policy Optimization (arXiv:2105.10899)
   - **Authors**: Zhenghao Peng, Quanyi Li, Chunxiao Liu, Bolei Zhou
   - **Summary**: This study introduces a method for safe driving by leveraging expert guidance in policy optimization. The authors propose an approach that integrates expert demonstrations to guide the learning process, ensuring safety constraints are met during policy optimization. Experiments in autonomous driving scenarios demonstrate the effectiveness of the proposed method in achieving safe and efficient driving behaviors.
   - **Year**: 2023

10. **Title**: Shared Autonomy via Deep Reinforcement Learning (arXiv:1802.01744)
    - **Authors**: Siddharth Reddy, Anca D. Dragan, Sergey Levine
    - **Summary**: This paper presents a framework for shared autonomy using deep reinforcement learning. The authors propose a method that allows for seamless collaboration between human operators and autonomous agents by learning policies that can effectively interpret and respond to human inputs. The approach is validated through experiments demonstrating improved performance in shared control tasks.
    - **Year**: 2023

**Key Challenges:**

1. **Skill Composition and Hierarchical Learning**: Developing mechanisms that enable agents to autonomously discover and compose simple skills into complex, hierarchical behaviors remains a significant challenge. Existing approaches often rely on predefined hierarchies or fail to generalize across domains.

2. **Intrinsic Motivation Design**: Crafting effective intrinsic motivation signals that drive exploration and skill acquisition without leading to premature convergence or suboptimal behaviors is complex. Balancing exploration and exploitation through intrinsic rewards requires careful design.

3. **Scalability and Generalization**: Ensuring that learned skills and behaviors generalize to new tasks and environments is crucial. Many current methods struggle with scalability and fail to transfer learned skills effectively across diverse settings.

4. **Evaluation Metrics**: Establishing robust metrics for evaluating the performance of intrinsically motivated agents, particularly in open-ended and reward-free environments, is challenging. Traditional metrics may not capture the nuances of exploration and skill acquisition.

5. **Integration of Human Feedback**: Incorporating human demonstrations and preferences into the learning process to guide skill acquisition and ensure alignment with human intentions presents both technical and ethical challenges. Balancing autonomy with human oversight requires careful consideration. 