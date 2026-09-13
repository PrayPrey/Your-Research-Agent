## Related Work

**Related Papers**
1. **Title**: Gradient Descent on Neural Networks Typically Occurs at the Edge of Stability (2021)
   - **Authors**: Cohen, Kaur, Li, Kolter, Talwalkar
   - **Summary**: Demonstrates empirically that the maximum eigenvalue of the Hessian (λ_max) hovers at 2/η during training, with non-monotonic loss behavior yet overall descent. This establishes the foundational empirical phenomenon of edge of stability in neural network training.
   - **Year**: 2021

2. **Title**: Understanding Gradient Descent on Edge of Stability in Deep Learning (2022)
   - **Authors**: Arora, Li, Panigrahi
   - **Summary**: Shows that gradient descent evolves along a flow that minimizes λ₁ on the loss manifold, providing a mechanism for understanding curvature minimization during training.
   - **Year**: 2022

3. **Title**: Sharpness-Aware Minimization for Efficiently Improving Generalization (2020)
   - **Authors**: Foret, Kleiner, Mobahi, Neyshabur
   - **Summary**: Establishes theoretical generalization bounds involving sharpness and demonstrates that SAM achieves state-of-the-art performance, providing the theoretical basis for the sharpness-generalization connection.
   - **Year**: 2020

4. **Title**: GenEFT (2024)
   - **Authors**: Not specified
   - **Summary**: Proposes an effective field theory approach for understanding generalization, taking a phenomenological perspective to the problem.
   - **Year**: 2024

5. **Title**: Edge of Stochastic Stability (2024)
   - **Authors**: Not specified
   - **Summary**: Extends the edge of stability phenomenon to SGD settings, providing a descriptive account of stability behavior in stochastic optimization.
   - **Year**: 2024

6. **Title**: Implicit Bias of Gradient Descent for Wide Two-layer Neural Networks (2020)
   - **Authors**: Chizat, Bach
   - **Summary**: Demonstrates the existence of implicit bias in gradient descent for wide two-layer networks, though without establishing connections to edge of stability phenomena.
   - **Year**: 2020

7. **Title**: Implicit Bias at the Edge of Stability (2023)
   - **Authors**: Wu et al.
   - **Summary**: Bridges edge of stability and implicit bias concepts, though the analysis is limited to logistic regression settings only.
   - **Year**: 2023

**Key Challenges**
1. **Phenomenological vs Mechanistic Understanding**: Existing approaches like GenEFT provide phenomenological descriptions of generalization but lack mechanistic explanations for the underlying processes.
2. **Descriptive vs Causal Explanations**: Current work on edge of stability (including stochastic extensions) remains largely descriptive without providing causal explanations for the observed phenomena.
3. **Disconnection Between Implicit Bias and Edge of Stability**: Prior work on implicit bias (e.g., Chizat & Bach) establishes its existence but fails to connect it to edge of stability dynamics.
4. **Limited Scope of Existing Bridges**: Work attempting to bridge implicit bias and edge of stability (Wu et al., 2023) is restricted to simple settings like logistic regression, leaving gaps for more complex neural network architectures.
