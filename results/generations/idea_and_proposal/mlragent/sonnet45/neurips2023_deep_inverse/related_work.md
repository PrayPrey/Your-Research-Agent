1. **Title**: Ensemble Kalman Diffusion Guidance: A Derivative-free Method for Inverse Problems (arXiv:2409.20175)
   - **Authors**: Hongkai Zheng, Wenda Chu, Austin Wang, Nikola Kovachki, Ricardo Baptista, Yisong Yue
   - **Summary**: This paper introduces Ensemble Kalman Diffusion Guidance (EnKG), a derivative-free approach that utilizes pre-trained diffusion models as priors for solving inverse problems. EnKG operates without requiring derivatives or full knowledge of the forward model, making it suitable for applications with limited information about the system. The method is demonstrated on various inverse problems, including fluid flow and astronomical object inference.
   - **Year**: 2024

2. **Title**: Parameter Inference and Uncertainty Quantification with Diffusion Models: Extending CDI to 2D Spatial Conditioning (arXiv:2601.17224)
   - **Authors**: Dmitrii Torbunov, Yihui Ren, Lijun Wu, Yimei Zhu
   - **Summary**: This work extends the Conditional Diffusion Model-based Inverse Problem Solver (CDI) to two-dimensional spatial data, enabling probabilistic parameter inference directly from spatial observations. Applied to convergent beam electron diffraction (CBED) parameter inference, the method produces well-calibrated posterior distributions that accurately reflect measurement constraints, distinguishing between well-determined and ambiguous parameters.
   - **Year**: 2026

3. **Title**: Self-diffusion for Solving Inverse Problems (arXiv:2510.21417)
   - **Authors**: Guanxiong Luo, Shoujin Huang, Yanlong Yang
   - **Summary**: The authors propose 'self-diffusion,' a framework that solves inverse problems without relying on pre-trained generative models. It employs an iterative process alternating between noising and denoising steps, using a self-denoiser—a randomly initialized convolutional network trained via data fidelity loss. This approach adapts to arbitrary forward operators and noisy observations, demonstrating competitive performance across various linear inverse problems.
   - **Year**: 2025

4. **Title**: DAWN-SI: Data-Aware and Noise-Informed Stochastic Interpolation for Solving Inverse Problems (arXiv:2412.04766)
   - **Authors**: Shadab Ahamed, Eldad Haber
   - **Summary**: DAWN-SI introduces a generative framework that integrates deterministic and stochastic processes to map a simple reference distribution to the target distribution. Incorporating data and noise embeddings, the model explicitly accesses representations about measured data and accounts for noise, enhancing robustness in noisy or incomplete data scenarios. The method is validated on tasks like image deblurring and tomography.
   - **Year**: 2024

5. **Title**: Efficiency and Robustness in Monte Carlo Sampling of 3-D Geophysical Inversions with Obsidian v0.1.2
   - **Authors**: Scalzo et al.
   - **Summary**: This paper discusses the challenges in 3-D geophysical inversions, emphasizing the need for efficient and robust Monte Carlo sampling methods. The authors present Obsidian v0.1.2, a software platform designed to address these challenges by providing a flexible framework for sampling complex posterior distributions in high-dimensional spaces.
   - **Year**: 2024

6. **Title**: Uncertainty of Thoughts: Uncertainty-Aware Planning
   - **Authors**: Besta et al.
   - **Summary**: The authors explore uncertainty-aware planning in the context of large language models, proposing methods to incorporate uncertainty quantification into the planning process. This approach aims to improve decision-making under uncertainty by leveraging probabilistic models and uncertainty estimates.
   - **Year**: 2024

7. **Title**: Technical Report. In Progress
   - **Authors**: Anonymous
   - **Summary**: This technical report introduces Matryoshka Diffusion Models (MDM), a new class of diffusion models trained end-to-end in high-resolution space while exploiting the hierarchical structure of data formation. MDM generalizes standard diffusion models in an extended space, proposing specialized nested architectures and training procedures.
   - **Year**: 2024

8. **Title**: Differentiable Implicit Soft-Body Physics
   - **Authors**: Rojas et al.
   - **Summary**: The paper presents a differentiable soft-body physics simulator that can be integrated with neural networks as a differentiable layer. Focusing on implicit state transitions defined via function minimization, the approach allows for efficient policy optimization in locomotion tasks, achieving better sample efficiency than model-free reinforcement learning.
   - **Year**: 2024

9. **Title**: A Time-Stepping Deep Gradient Flow Method for Option Pricing in (Rough) Diffusion Models
   - **Authors**: Papapantoleon and Rou
   - **Summary**: This work develops a deep learning approach for pricing European options in diffusion models, efficiently handling high-dimensional problems resulting from Markovian approximations of rough volatility models. The method reformulates the option pricing partial differential equation as an energy minimization problem, approximated in a time-stepping fashion by deep neural networks.
   - **Year**: 2024

10. **Title**: Using Human Feedback to Fine-tune Diffusion Models
    - **Authors**: Anonymous
    - **Summary**: The authors employ human feedback to fine-tune diffusion models, enhancing their performance in generating images aligned with human preferences. The approach involves iterative refinement based on human evaluations, leading to improved image quality and alignment with desired outcomes.
    - **Year**: 2024

**Key Challenges**:

1. **Model Uncertainty**: Accurately estimating and incorporating uncertainties in forward models, such as miscalibrated sensors or unknown noise distributions, remains a significant challenge.

2. **Data Quality and Noise**: Handling incomplete, noisy, or corrupted data effectively is crucial for reliable inverse problem solutions.

3. **Computational Efficiency**: Developing methods that are computationally efficient, especially for high-dimensional and complex inverse problems, is essential for practical applications.

4. **Generalization Across Domains**: Ensuring that models trained on specific datasets or problem types generalize well to other domains or varying conditions is a persistent issue.

5. **Uncertainty Quantification**: Providing accurate and interpretable uncertainty estimates in the solutions of inverse problems is vital for assessing the reliability of the results. 