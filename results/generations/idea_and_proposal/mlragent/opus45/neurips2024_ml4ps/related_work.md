1. **Title**: Towards a Foundation Model for Partial Differential Equations Across Physics Domains (arXiv:2511.21861)
   - **Authors**: Eduardo Soares, Emilio Vital Brazil, Victor Shirasuna, Breno W. S. R. de Carvalho, Cristiano Malossi
   - **Summary**: This paper introduces PDE-FM, a modular foundation model designed for physics-informed machine learning. PDE-FM unifies spatial, spectral, and temporal reasoning across diverse partial differential equation (PDE) systems. It combines spatial-spectral tokenization, physics-aware conditioning, and a Mamba-based state-space backbone with an operator-theoretic decoder. The model is pretrained on various PDE datasets and can be transferred to new physical regimes without architectural modifications. Evaluations on multiple 2D and 3D datasets demonstrate state-of-the-art accuracy and robust cross-physics generalization.
   - **Year**: 2025

2. **Title**: Foundation Neural-Network Quantum States (arXiv:2502.09488)
   - **Authors**: Riccardo Rende, Luciano Loris Viteritti, Federico Becca, Antonello Scardicchio, Alessandro Laio, Giuseppe Carleo
   - **Summary**: The authors propose Foundation Neural-Network Quantum States (FNQS), a paradigm for studying quantum many-body systems. FNQS leverage principles of foundation models to define variational wave functions based on a single, versatile architecture that processes multimodal inputs, including spin configurations and Hamiltonian physical couplings. Unlike specialized architectures tailored for individual Hamiltonians, FNQS can generalize to physical Hamiltonians beyond those encountered during training, offering a unified framework adaptable to various quantum systems and tasks.
   - **Year**: 2025

3. **Title**: Guaranteeing Conservation of Integrals with Projection in Physics-Informed Neural Networks (arXiv:2511.09048)
   - **Authors**: Anthony Baez, Wang Zhang, Ziwen Ma, Lam Nguyen, Subhro Das, Luca Daniel
   - **Summary**: This work introduces a projection method that ensures the conservation of integral quantities in Physics-Informed Neural Networks (PINNs). By solving constrained non-linear optimization problems, the authors derive projection formulas that guarantee the conservation of linear and quadratic integrals. The proposed PINN-Proj method significantly reduces errors in conservation quantities compared to traditional soft constraints and marginally improves PDE solution accuracy.
   - **Year**: 2025

4. **Title**: Towards a Physics Foundation Model (arXiv:2509.13805)
   - **Authors**: Florian Wiesner, Matthias Wessling, Stephen Baek
   - **Summary**: The authors present the General Physics Transformer (GPhyT), a model trained on diverse simulation data that demonstrates foundation model capabilities in physics. GPhyT can simulate various physical systems without retraining, achieving superior performance and zero-shot generalization. This work suggests that a single model can learn generalizable physical principles from data alone, paving the way toward a universal Physics Foundation Model.
   - **Year**: 2025

5. **Title**: Machine Learning of Independent Conservation Laws Through Neural Deflation (Phys. Rev. E 108, L022301)
   - **Authors**: Wei Zhu
   - **Summary**: This paper introduces "neural deflation," a methodology for discovering conservation laws within Hamiltonian dynamical systems. By iteratively training neural networks to minimize a regularized loss function that accounts for conserved quantities' involution and functional independence, the method successfully identifies conservation laws in both integrable and nonintegrable systems.
   - **Year**: 2023

6. **Title**: Universally Converging Representations of Matter Across Scientific Foundation Models (arXiv:2512.03750)
   - **Authors**: [Authors not specified]
   - **Summary**: This study investigates whether scientific foundation models across molecules, materials, and proteins learn a universal latent representation of matter. Analyzing approximately 60 diverse models using various metrics, the authors find strong representational alignment that increases with model performance, suggesting convergence toward a common physical representation. They also identify failure regimes highlighting current limits of generality and the need for more diverse training data.
   - **Year**: 2025

7. **Title**: Cosmos World Foundation Model Platform for Physical AI (arXiv:2501.03575)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper introduces the Cosmos World Foundation Model Platform, a modular system combining pre-trained World Foundation Models with a scalable video-curation pipeline, tokenizers, and post-training to tailor models to applications like camera control, robotics, and autonomous driving. The platform aims to address the data bottleneck in Physical AI by providing a robust data pipeline and guardrails for safe, scalable world simulation.
   - **Year**: 2025

8. **Title**: Machine Learning Conservation Laws from Differential Equations (Phys. Rev. E 106, 045307)
   - **Authors**: Ziming Liu, Varun Madhavan, Max Tegmark
   - **Summary**: The authors present a machine learning algorithm that discovers conservation laws from differential equations, both numerically and symbolically, ensuring their functional independence. The method can handle inductive biases for conservation laws and is validated with examples including the three-body problem, the KdV equation, and the nonlinear Schrödinger equation.
   - **Year**: 2022

9. **Title**: Towards Foundation Models for Materials Science: The Open MatSci ML Toolkit (arXiv:2310.07864)
   - **Authors**: Kin Long Kelvin Lee, Carmelo Gonzales, Matthew Spellings, Mikhail Galkin, Santiago Miret, Nalini Kumar
   - **Summary**: This manuscript reviews the development of the Open MatSci ML Toolkit and details experiments laying the groundwork for foundation model research in materials science. The authors describe a new pretraining task using synthetic data generated from symmetry operations and reveal complex training dynamics at large scales.
   - **Year**: 2023

10. **Title**: Learning Physical Models That Can Respect Conservation Laws (Physica D: Nonlinear Phenomena, Volume 457, January 2024, 133952)
    - **Authors**: Derek Hansen, Danielle Maddix, Shima Alizadeh, Gaurav Gupta, Michael W. Mahoney
    - **Summary**: This work proposes ProbConserv, a framework for incorporating constraints into a black-box probabilistic deep-learning architecture. By combining the integral form of a conservation law with a Bayesian update, ProbConserv enforces physical conservation constraints, maintains probabilistic uncertainty quantification, and handles shocks and heteroscedasticity. The framework is demonstrated on the Generalized Porous Medium Equation, achieving superior predictive performance on downstream tasks.
    - **Year**: 2024

**Key Challenges:**

1. **Balancing Flexibility and Physical Consistency**: Integrating conservation laws into foundation models without compromising their flexibility remains a significant challenge. Ensuring that models adhere to physical laws while maintaining adaptability to diverse tasks is complex.

2. **Discovering and Enforcing Conservation Laws**: Developing methods to automatically identify and enforce conservation laws from data is non-trivial. Techniques like neural deflation and projection methods are promising but require further refinement and validation across various systems.

3. **Generalization Across Physical Regimes**: Ensuring that foundation models can generalize to out-of-distribution physical regimes while maintaining strict conservation properties is challenging. Models must be robust to variations in physical systems and capable of accurate predictions beyond their training data.

4. **Data Limitations and Model Training**: The availability of diverse and high-quality datasets is crucial for training foundation models. Data limitations can hinder the development of models that accurately capture conservation laws and generalize across different physical systems.

5. **Computational Complexity**: Incorporating conservation laws into machine learning models often increases computational complexity. Efficient algorithms and scalable architectures are needed to handle the additional computational burden without sacrificing performance. 