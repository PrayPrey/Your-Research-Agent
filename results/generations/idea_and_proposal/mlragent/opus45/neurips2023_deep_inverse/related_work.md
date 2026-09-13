1. **Title**: Ensemble Kalman Diffusion Guidance: A Derivative-free Method for Inverse Problems (arXiv:2409.20175)
   - **Authors**: Hongkai Zheng, Wenda Chu, Austin Wang, Nikola Kovachki, Ricardo Baptista, Yisong Yue
   - **Summary**: This paper introduces Ensemble Kalman Diffusion Guidance (EnKG), a derivative-free approach that leverages pre-trained diffusion models as priors to solve inverse problems without requiring derivatives or full knowledge of the forward model. EnKG is particularly effective in scenarios where only black-box access to the forward model is available, such as in scientific applications like fluid flow and astronomical object inference.
   - **Year**: 2024

2. **Title**: Parameter Inference and Uncertainty Quantification with Diffusion Models: Extending CDI to 2D Spatial Conditioning (arXiv:2601.17224)
   - **Authors**: Dmitrii Torbunov, Yihui Ren, Lijun Wu, Yimei Zhu
   - **Summary**: This work extends the Conditional Diffusion Model-based Inverse Problem Solver (CDI) to two-dimensional spatial data, enabling probabilistic parameter inference directly from spatial observations. The method is validated on convergent beam electron diffraction (CBED) data, demonstrating well-calibrated posterior distributions that accurately reflect measurement constraints, thereby providing genuine uncertainty information required for robust scientific inference.
   - **Year**: 2026

3. **Title**: DAWN-SI: Data-Aware and Noise-Informed Stochastic Interpolation for Solving Inverse Problems (arXiv:2412.04766)
   - **Authors**: Shadab Ahamed, Eldad Haber
   - **Summary**: DAWN-SI introduces a generative framework that integrates deterministic and stochastic processes to map a simple reference distribution to the target distribution. By incorporating data and noise embeddings, the model explicitly accounts for noisy or incomplete observations, making it robust in such scenarios. The approach is validated through numerical experiments on tasks like image deblurring and tomography.
   - **Year**: 2024

4. **Title**: DMPlug: A Plug-in Method for Solving Inverse Problems with Diffusion Models (arXiv:2405.16749)
   - **Authors**: Hengkang Wang, Xu Zhang, Taihui Li, Yuxiang Wan, Tiancong Chen, Ju Sun
   - **Summary**: DMPlug proposes a novel plug-in method for solving inverse problems using pre-trained diffusion models. By viewing the reverse process in diffusion models as a function, DMPlug addresses issues of manifold and measurement feasibility in a principled manner. The method demonstrates robustness to unknown types and levels of noise and outperforms state-of-the-art methods across various inverse problem tasks, including both linear and nonlinear cases.
   - **Year**: 2024

5. **Title**: Uncertainty of Thoughts: Uncertainty-Aware Planning (arXiv:2402.03271)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper discusses the integration of uncertainty quantification into planning processes, emphasizing the importance of accounting for uncertainty in decision-making. While the specific methodologies are not detailed in the provided excerpt, the work highlights the relevance of uncertainty-aware approaches in complex systems.
   - **Year**: 2024

6. **Title**: Technical report. In progress (arXiv:2310.15111)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This technical report introduces Matryoshka Diffusion Models (MDM), a new class of diffusion models trained end-to-end in high-resolution space while exploiting the hierarchical structure of data formation. MDM generalizes standard diffusion models in an extended space and proposes specialized nested architectures and training procedures to handle high-resolution image generation efficiently.
   - **Year**: 2024

7. **Title**: Efficiency and Robustness in Monte Carlo Sampling of 3-D Geophysical Inversions with Obsidian v0.1.2 (arXiv:1812.00318)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work presents Obsidian v0.1.2, a framework for efficient and robust Monte Carlo sampling in 3-D geophysical inversions. The paper addresses challenges in characterizing and fusing disparate sources of probabilistic information, emphasizing the importance of Bayesian statistical techniques for uncertainty quantification in complex geophysical problems.
   - **Year**: 2024

8. **Title**: Using Human Feedback to Fine-tune Diffusion Models (arXiv:2311.13231)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper explores the use of human feedback to fine-tune diffusion models, aiming to enhance the quality and safety of generated images. The approach involves incorporating human annotations to guide the training process, resulting in improved alignment between generated images and desired outcomes, as well as reduced generation of unsafe content.
   - **Year**: 2024

9. **Title**: Uncertainty-driven Trajectory Truncation for Data (arXiv:2304.04660)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work introduces Trajectory Truncation with Uncertainty (TATU), a method that utilizes uncertainty quantification to truncate imagined trajectories in model-based reinforcement learning. By incorporating uncertainty measures, TATU aims to improve the reliability and robustness of policy learning in offline settings.
   - **Year**: 2024

10. **Title**: A Bayesian Drift-Diffusion Model of Schachter-Singer’s Two Factor Theory of Emotion (arXiv:2406.11086)
    - **Authors**: Lance Ying, Audrey Michal, Jun Zhang
    - **Summary**: This paper presents a Bayesian drift-diffusion model that computationally implements Schachter-Singer’s Two-Factor theory of emotion. The model conceptualizes emotion recognition as a Bayesian inference process, combining physiological arousal patterns with contextual information to simulate emotional labeling and intensity.
    - **Year**: 2024

**Key Challenges:**

1. **Model Uncertainty and Calibration**: Accurately estimating and calibrating unknown forward model parameters remains a significant challenge, as discrepancies between assumed and actual models can lead to reconstruction artifacts and unreliable uncertainty estimates.

2. **Robustness to Noise and Incomplete Data**: Developing methods that are resilient to varying noise levels and incomplete observations is crucial, especially in practical scenarios where data quality cannot be guaranteed.

3. **Computational Efficiency**: Balancing the computational demands of complex hierarchical models and high-resolution data with the need for real-time or near-real-time processing is a persistent challenge.

4. **Generalization Across Domains**: Ensuring that diffusion-based inverse problem solvers generalize well across different application domains, each with unique characteristics and requirements, is essential for broader applicability.

5. **Integration of Human Feedback**: Effectively incorporating human feedback into the training and fine-tuning of diffusion models to improve performance and safety without introducing biases or compromising model integrity is a complex task. 