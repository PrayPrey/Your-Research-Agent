## Related Work

**Related Papers**

1. **Title**: Understanding Gradient Descent on Edge of Stability (Arora et al., 2022)
   - **Authors**: Arora et al.
   - **Summary**: Foundation work for manifold flow during gradient descent, using induced metric on minimum loss manifold to explain Edge of Stability phenomenon.
   - **Year**: 2022
   - **Identifier**: SS ID: 0f3b6cb07a8edb78a40ee478708eedcd03242503

2. **Title**: Optimization on multifractal loss landscapes (Ly & Gong, 2025)
   - **Authors**: Ly & Gong
   - **Summary**: Multifractal framework that unifies Edge of Stability and non-smooth landscape phenomena in neural network optimization.
   - **Year**: 2025
   - **Identifier**: SS ID: 231ad4d997e40960db18d5b3882ed842e8630e8b

3. **Title**: Gluon: Bridging Theory and Practice of LMO-based Optimizers (Riabinin et al., 2025)
   - **Authors**: Riabinin et al.
   - **Summary**: Closes the gap between optimizer theory and practice, acknowledging layer-wise geometry in optimizer design.
   - **Year**: 2025
   - **Identifier**: SS ID: 7179e53d0315e53f8829a7027b75660eb0637b4b

4. **Title**: Leveraging Flatness to Improve Information-Theoretic Generalization Bounds (Peng et al., 2026)
   - **Authors**: Peng et al.
   - **Summary**: First information-theoretic bound incorporating flatness, showing generalization is proportional to √(tr(F(θ))/n) using Fisher information.
   - **Year**: 2026
   - **Identifier**: SS ID: 1625169b96fc4a658c5a3127d4090f069bc41bef

5. **Title**: Implicit Bias of Gradient Descent for Non-Homogeneous Deep Networks (Cai et al., 2025)
   - **Authors**: Cai et al.
   - **Summary**: Shows gradient descent has implicit bias toward margin maximization in non-homogeneous networks, reinterpretable as Fisher information minimization.
   - **Year**: 2025
   - **Identifier**: SS ID: af050060dbbbeb96de43c1e35314e66be576d498

6. **Title**: On Linear Stability of SGD and Input-Smoothness of Neural Networks (Ma & Ying, 2021)
   - **Authors**: Ma & Ying
   - **Summary**: Connects flatness to Sobolev regularization and input smoothness of neural networks, complementary to parameter space geometry perspective.
   - **Year**: 2021
   - **Identifier**: SS ID: 46de360b7a4ba6b9b6a498d1d80173eda743d287

7. **Title**: Scaling Laws and In-Context Learning: A Unified Theoretical Framework (Mehta & Gupta, 2025)
   - **Authors**: Mehta & Gupta
   - **Summary**: Unifies scaling laws with in-context learning, showing power-law scaling relationships for ICL emergence.
   - **Year**: 2025
   - **Identifier**: SS ID: 8b3bd7b9c64a1534eda345bf59a8d83514f24705

8. **Title**: Exact Learning Dynamics of In-Context Learning in Linear Transformers (Mainali & Teixeira, 2025)
   - **Authors**: Mainali & Teixeira
   - **Summary**: Provides exact learning dynamics for linear transformers, explaining sudden ICL emergence via fixed point analysis.
   - **Year**: 2025
   - **Identifier**: SS ID: 0490915cdafa0ca947a32babb1ebef754b3e0f92

9. **Title**: The Expressive Power of Transformers with Chain of Thought (Merrill & Sabharwal, 2024)
   - **Authors**: Merrill & Sabharwal
   - **Summary**: Complexity-theoretic foundation for chain of thought reasoning, analyzing the expressive power of transformers.
   - **Year**: 2024
   - **Identifier**: SS ID: 75c19f3249f644f5cb2182282fc117c089fd3f65

10. **Title**: Parameter Symmetry Potentially Unifies Deep Learning Theory (Ziyin et al., 2025)
    - **Authors**: Ziyin et al.
    - **Summary**: Proposes parameter symmetry as a unifying mechanism for deep learning theory, focusing on symmetry breaking during training.
    - **Year**: 2025
    - **Identifier**: SS ID: 2a779aaebb56a0505c84be39d546f6f636d5c446

11. **Title**: Deep Learning is Not So Mysterious or Different (Wilson, 2025)
    - **Authors**: Wilson
    - **Summary**: Argues for "soft inductive biases" as unifying principle and traditional frameworks rather than mysterious narratives in deep learning.
    - **Year**: 2025
    - **Identifier**: SS ID: b51e4bdcca2986553852796d19e672c12f1cd363

12. **Title**: Information Geometry and Its Applications (Amari, 2016)
    - **Authors**: Amari
    - **Summary**: Foundational work on Fisher information metric and natural gradient, establishing Fisher metric as canonical Riemannian geometry on probability manifolds.
    - **Year**: 2016
    - **Identifier**: Not specified

13. **Title**: Statistical Mechanics of Learning (Engel & Van den Broeck, 2001)
    - **Authors**: Engel & Van den Broeck
    - **Summary**: Establishes phase transitions in learning systems and order parameters, providing statistical physics framework for neural network learning.
    - **Year**: 2001
    - **Identifier**: Not specified

**Key Challenges**

1. **Fragmentation of Deep Learning Theory**: Optimization dynamics, generalization mechanisms, and emergent capabilities have been studied independently without unified mathematical framework connecting them.

2. **Optimization-Generalization Disconnect**: Optimization researchers study Edge of Stability without considering generalization, while generalization theorists study flatness without linking to optimization dynamics.

3. **Lack of Mechanistic Emergence Explanation**: Large language model research shows emergence phenomena like in-context learning but lacks mechanistic explanation for why emergence occurs at specific training points.

4. **Computational Intractability of Fisher Information**: Full Fisher information matrix computation is intractable for billion-parameter models, requiring efficient approximation methods.

5. **Missing Quantitative Emergence Prediction**: Existing scaling laws are descriptive (post-hoc analysis) rather than predictive, lacking ability to forecast emergence before expensive full training.

6. **Approximation-Accuracy Trade-offs**: Need to balance computational efficiency (diagonal Fisher, KFAC approximations) with maintaining sufficient geometric accuracy for predictions.

7. **Phase Transition Rigor in Finite Systems**: Neural networks are finite systems, but phase transition terminology from statistical physics requires adaptation and rigorous characterization.

8. **Architecture-Specific vs. Universal Theories**: Existing theories often apply to specific architectures (linear transformers, specific optimizers) rather than providing universal framework across architectures.

9. **Theory-Practice Gap in Optimizers**: Optimizer theory developments often fail to translate into practical improvements, with gap between theoretical understanding and engineering practice.

10. **Scalability of Theoretical Tools**: Theoretical analysis methods (e.g., loss landscape visualization, Fisher metric computation) struggle to scale from toy models to production-scale billion-parameter models.
