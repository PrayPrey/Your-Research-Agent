1. **Title**: Gaze on the Prize: Shaping Visual Attention with Return-Guided Contrastive Learning (arXiv:2510.08442)
   - **Authors**: Andrew Lee, Ian Chuang, Dechen Gao, Kai Fukazawa, Iman Soltani
   - **Summary**: This paper introduces a framework that enhances visual reinforcement learning (RL) by incorporating a learnable foveal attention mechanism inspired by human visual foveation. The mechanism is guided by a self-supervised signal derived from the agent's experiences in pursuing higher returns. By employing return-guided contrastive learning, the attention mechanism is trained to focus on task-relevant features, leading to up to 2.4x improvement in sample efficiency across various manipulation tasks.
   - **Year**: 2025

2. **Title**: EyeFormer: Predicting Personalized Scanpaths with Transformer-Guided Reinforcement Learning (arXiv:2404.10163)
   - **Authors**: Yue Jiang, Zixin Guo, Hamed Rezazadegan Tavakoli, Luis A. Leiva, Antti Oulasvirta
   - **Summary**: EyeFormer leverages a Transformer architecture as a policy network to guide a deep reinforcement learning algorithm that controls gaze locations. The model predicts personalized scanpaths, including fixation positions and durations, across individuals and various stimulus types. It demonstrates applications in graphical user interface layout optimization, highlighting the potential of integrating gaze prediction into machine learning tasks.
   - **Year**: 2024

3. **Title**: Normalization Enhances Generalization in Visual Reinforcement Learning (arXiv:2306.00656)
   - **Authors**: Lu Li, Jiafei Lyu, Guozheng Ma, Zilin Wang, Zhenjie Yang, Xiu Li, Zhiheng Li
   - **Summary**: This study explores the integration of normalization techniques into visual reinforcement learning to improve generalization capabilities. By incorporating CrossNorm and SelfNorm, the authors demonstrate significant enhancements in generalization performance on benchmarks like DMControl and CARLA, with minimal impact on sample efficiency.
   - **Year**: 2023

4. **Title**: Leveraging Locality to Boost Sample Efficiency in RLBench (arXiv:2406.10615)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The paper introduces SGRv2, a visuomotor policy framework that emphasizes action locality to enhance sample efficiency in reinforcement learning. By integrating an encoder-decoder architecture for point-wise feature extraction and applying point-wise weights to highlight critical local regions, SGRv2 achieves exceptional sample efficiency, outperforming previous methods across various benchmarks.
   - **Year**: 2024

5. **Title**: LCRL: Certified Policy Synthesis via Logically-Constrained Reinforcement Learning (arXiv:2209.10341)
   - **Authors**: Hosein Hasanbeig, Daniel Kroening, Alessandro Abate
   - **Summary**: LCRL is a software tool that implements model-free reinforcement learning algorithms over unknown Markov Decision Processes, synthesizing policies that satisfy given linear temporal specifications with maximal probability. By leveraging Limit Deterministic Büchi Automata, LCRL shapes reward functions on-the-fly, ensuring convergence to optimal policies that maximize satisfaction probabilities.
   - **Year**: 2022

6. **Title**: ASHA: Assistive Teleoperation via Human-in-the-Loop Reinforcement Learning (arXiv:2202.02465)
   - **Authors**: Sean Chen, Jensen Gao, Siddharth Reddy, Glen Berseth, Anca D. Dragan, Sergey Levine
   - **Summary**: ASHA presents a hierarchical solution that learns efficiently from sparse user feedback in assistive teleoperation. By using offline pre-training to acquire a latent embedding space of high-level robot behaviors, the system focuses on mapping user inputs to desired behaviors, achieving efficient learning from sparse rewards in under 10 minutes of online training.
   - **Year**: 2022

7. **Title**: MoDem: Accelerating Visual Model-Based Reinforcement Learning with Demonstrations (arXiv:2212.05698)
   - **Authors**: Nicklas Hansen, Yixin Lin, Hao Su, Xiaolong Wang, Vikash Kumar, Aravind Rajeswaran
   - **Summary**: MoDem addresses the sample efficiency challenge in visual reinforcement learning by leveraging a handful of demonstrations. The framework identifies key ingredients for integrating demonstrations into model learning, including policy pretraining, targeted exploration, and oversampling of demonstration data, resulting in significant improvements in completing sparse reward tasks.
   - **Year**: 2022

8. **Title**: Efficient Learning of Safe Driving Policy via Human-AI Copilot Optimization (arXiv:2202.10341)
   - **Authors**: Quanyi Li, Zhenghao Peng, Bolei Zhou
   - **Summary**: This paper introduces HACO, a human-in-the-loop learning method that allows human experts to intervene and demonstrate how to avoid dangerous situations during reinforcement learning. HACO effectively utilizes data from both exploration and human demonstrations to train high-performing agents, achieving substantial sample efficiency in safe driving benchmarks.
   - **Year**: 2022

9. **Title**: THÖR: Human-Robot Navigation Data Collection and Accurate Motion Trajectories Dataset (arXiv:1909.04403)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: THÖR presents a dataset that includes accurate motion capture data, head orientations, eye gaze directions, and data from stationary 3D lidar sensors and RGB cameras. The dataset captures a variety of human motion behaviors and interactions, providing valuable insights for human-robot navigation research.
   - **Year**: 2019

10. **Title**: Gaze Meets ML: Bridging Human Cognition and AI in Machine Learning Research and Development
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This workshop focuses on integrating eye gaze data into machine learning to infer human perception, intentions, beliefs, and goals. It aims to bring together experts from various backgrounds to address core problems in gaze-assisted machine learning, covering topics like gaze estimation, attention mechanisms, and applications in domains such as NLP, computer vision, and reinforcement learning.
    - **Year**: 2026

**Key Challenges:**

1. **Data Collection and Quality**: Acquiring high-quality, large-scale eye-tracking data is resource-intensive and may introduce noise, affecting the reliability of gaze-guided learning approaches.

2. **Modeling Human Attention**: Accurately modeling human attention patterns and integrating them into reinforcement learning agents is complex, requiring sophisticated algorithms to capture temporal and spatial dynamics.

3. **Generalization Across Tasks**: Ensuring that gaze-guided reinforcement learning models generalize well across different tasks and environments remains a significant challenge, as human attention patterns can vary widely.

4. **Real-Time Processing**: Implementing gaze-guided learning in real-time applications demands efficient processing of eye-tracking data to provide timely and relevant guidance to the learning agent.

5. **Ethical and Privacy Concerns**: Utilizing human gaze data raises ethical and privacy issues, necessitating careful consideration of data usage, consent, and potential biases in the learning process. 