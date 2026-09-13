1. **Title**: On-the-fly adaptivity for nonlinear twoscale simulations using artificial neural networks and reduced order modeling (arXiv:1902.07443)
   - **Authors**: Felix Fritzen, Mauricio Fernández, Fredrik Larsson
   - **Summary**: This paper introduces a multi-fidelity surrogate model for nonlinear multiscale problems, combining reduced order modeling (ROM) and artificial neural networks (ANNs). An adaptive on-the-fly switching mechanism selects the appropriate surrogate to balance efficiency and accuracy. The approach is validated on three-phase composite simulations, demonstrating significant performance improvements.
   - **Year**: 2019

2. **Title**: Uncertainty quantification for noisy inputs-outputs in physics-informed neural networks and neural operators (arXiv:2311.11262)
   - **Authors**: Zongren Zou, Xuhui Meng, George Em Karniadakis
   - **Summary**: The authors present a Bayesian approach to quantify uncertainty in physics-informed neural networks (PINNs) and neural operators (NOs) when dealing with noisy inputs and outputs. This method enhances the reliability of SciML models by addressing uncertainties in spatial-temporal coordinates and input functions, crucial for trustworthy deployment in scientific applications.
   - **Year**: 2023

3. **Title**: Context-aware learning of hierarchies of low-fidelity models for multi-fidelity uncertainty quantification (arXiv:2211.10835)
   - **Authors**: Ionut-Gabriel Farcas, Benjamin Peherstorfer, Tobias Neckel, Frank Jenko, Hans-Joachim Bungartz
   - **Summary**: This work proposes a context-aware multi-fidelity Monte Carlo method that optimally balances the costs of training low-fidelity models with Monte Carlo sampling. By considering the context in which low-fidelity models are used, the approach achieves significant speedups in uncertainty quantification tasks, demonstrated in plasma fusion simulations.
   - **Year**: 2022

4. **Title**: Probabilistic neural operators for functional uncertainty quantification (arXiv:2502.12902)
   - **Authors**: Christopher Bülte, Philipp Scholl, Gitta Kutyniok
   - **Summary**: The paper introduces Probabilistic Neural Operators (PNOs), extending neural operators with generative modeling based on strictly proper scoring rules. PNOs integrate uncertainty information directly into the training process, leading to well-calibrated predictive distributions and improved performance in quantifying uncertainty across various domains.
   - **Year**: 2025

5. **Title**: The Cost-Accuracy Trade-Off in Operator Learning with Neural Networks (arXiv:2203.13181)
   - **Authors**: Maarten V. de Hoop, Daniel Zhengyu Huang, Elizabeth Qian, Andrew M. Stuart
   - **Summary**: This study provides a numerical analysis of various neural network architectures for operator approximation in PDE models. It evaluates the cost-accuracy trade-offs, offering insights into the computational resources required to achieve desired accuracy levels, guiding the selection of appropriate surrogate modeling techniques.
   - **Year**: 2022

6. **Title**: Physics-Aware Motion Simulation for T2*-Weighted Brain MRI (arXiv:2303.10987)
   - **Authors**: Hannah Eichhorn, Kerstin Hammernik, Veronika Spieker, Samira M. Epp, Daniel Rueckert, Christine Preibisch, Julia A. Schnabel
   - **Summary**: The authors propose a physics-aware motion simulation procedure for T2*-weighted MRI, incorporating real recorded subject motion and realistic effects of motion-induced magnetic field inhomogeneity changes. This approach improves learning-based motion correction, enhancing the accuracy of MRI simulations.
   - **Year**: 2023

7. **Title**: Contact-conditioned learning of locomotion policies (arXiv:2408.00776)
   - **Authors**: Michal Ciebielski, Majid Khadiv
   - **Summary**: This paper introduces a novel goal representation for learning low-level locomotion policies, conditioning the policy on the location and timing of contacts. The approach enables a single policy network to generate multiple gaits and transitions, demonstrating improved robustness and performance in biped robot simulations.
   - **Year**: 2024

8. **Title**: Heavy-Ball Momentum Accelerated Actor-Critic (arXiv:2408.06945)
   - **Authors**: Yanjie Dong, Haijun Zhang, Gang Wang, Shisheng Cui, Xiping Hu
   - **Summary**: The authors propose a heavy-ball momentum accelerated actor-critic algorithm to improve the convergence speed and stability of reinforcement learning. The approach is validated through theoretical analysis and experiments, showing enhanced performance in various tasks.
   - **Year**: 2024

9. **Title**: Statistical Mechanics and Artificial Neural Networks (arXiv:2405.10957)
   - **Authors**: Not specified
   - **Summary**: This work explores the intersection of statistical mechanics and artificial neural networks, discussing foundational concepts and their applications in understanding neural network behavior and learning dynamics.
   - **Year**: 2024

10. **Title**: Journal of Machine Learning for Biomedical Imaging. 2022:026. pp 1-54 (arXiv:2112.10074)
    - **Authors**: Not specified
    - **Summary**: This journal article compiles various studies on machine learning applications in biomedical imaging, covering topics such as uncertainty quantification, simulation-based inference, and neural surrogates, providing a comprehensive overview of recent advancements in the field.
    - **Year**: 2022

**Key Challenges:**

1. **Uncertainty Quantification**: Accurately estimating and calibrating uncertainties in neural surrogates remains challenging, especially in complex, high-dimensional systems.

2. **Adaptive Fidelity Switching**: Developing efficient and reliable mechanisms to switch between low and high-fidelity models in real-time without introducing significant computational overhead.

3. **Generalization Across Scales**: Ensuring that neural surrogates can generalize effectively across different scales and regimes in multi-scale physical simulations.

4. **Computational Efficiency**: Balancing the trade-off between computational speed and accuracy, particularly when integrating neural surrogates with traditional solvers.

5. **Robustness to Noisy Data**: Enhancing the robustness of neural surrogates to noisy inputs and outputs, which is critical for their deployment in real-world scientific applications. 