## Related Work

**Related Papers**
1. **Title**: Towards Scaling Deep Neural Networks with Predictive Coding: Theory and Practice (arXiv:2510.23323)
   - **Authors**: Francesco Innocenti
   - **Summary**: Demonstrates that μPC parameterization enables stable training of 100+ layer predictive coding networks and shows that learning dynamics are approximate trust-region methods.
   - **Year**: 2025

2. **Title**: Predictive Coding Networks and Inference Learning: Tutorial and Survey (arXiv:2407.04117)
   - **Authors**: van Zwol, Jefferson, van den Broek
   - **Summary**: Provides a comprehensive PCN framework and introduces the PRECO Python library, establishing PCNs as a superset of traditional feedforward neural networks.
   - **Year**: 2024

3. **Title**: Predictive Coding algorithms induce brain-like responses in ANNs
   - **Authors**: Gütlin, Auksztulewicz
   - **Summary**: Demonstrates that PC-inspired training creates biologically plausible networks exhibiting mismatch responses, validating the transfer of predictive coding principles to deep learning.
   - **Year**: 2025

4. **Title**: Physics-informed neural networks: A deep learning framework for solving forward and inverse problems
   - **Authors**: Raissi, Perdikaris, Karniadakis
   - **Summary**: Introduces the framework of encoding PDE constraints as neural network loss functions, establishing a unidirectional Scientific→ML approach.
   - **Year**: 2019

5. **Title**: Neural Ordinary Differential Equations
   - **Authors**: Chen, Rubanova, Bettencourt, Duvenaud
   - **Summary**: Proposes continuous-depth models using ODE solvers with O(1) memory backpropagation, enabling a unidirectional ML→Sci approach.
   - **Year**: 2018

6. **Title**: Physics-Guided, Physics-Informed, and Physics-Encoded Neural Networks
   - **Authors**: Faroughi et al.
   - **Summary**: Categorizes neural network approaches into PgNN, PiNN, and PeNN, demonstrating that none of these existing paradigms achieve true bidirectionality.
   - **Year**: 2024

7. **Title**: Scientific Machine Learning Through PINNs: Where we are and What's Next
   - **Authors**: Cuomo et al.
   - **Summary**: Provides a comprehensive review of physics-informed neural networks, identifying their limitations and outlining future research directions.
   - **Year**: 2022

8. **Title**: DeepXDE
   - **Authors**: Not specified
   - **Summary**: A multi-backend library for physics-informed learning that provides differentiable physics implementation capabilities.
   - **Year**: Not specified

9. **Title**: torchdiffeq
   - **Authors**: Not specified
   - **Summary**: Provides differentiable ODE solvers with GPU support for neural network integration with differential equations.
   - **Year**: Not specified

**Key Challenges**
1. **Unidirectional Knowledge Transfer**: Existing approaches like PINNs only transfer knowledge from scientific domains to ML (Sci→ML) or vice versa (ML→Sci), but none achieve true bidirectional integration between scientific computing and machine learning.

2. **Lack of Bidirectionality in Physics-Neural Architectures**: Current categorizations of physics-guided, physics-informed, and physics-encoded neural networks reveal that no existing paradigm supports simultaneous bidirectional information flow.

3. **Scaling Predictive Coding Networks**: Training deep predictive coding networks (100+ layers) requires specialized parameterization (μPC) to maintain stability, presenting challenges for applying PC principles to large-scale architectures.

4. **PINN Limitations**: Despite widespread adoption, physics-informed neural networks have identified limitations that constrain their applicability and effectiveness in scientific machine learning tasks.
