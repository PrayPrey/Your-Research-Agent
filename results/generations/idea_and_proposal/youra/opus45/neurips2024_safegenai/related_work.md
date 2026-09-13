## Related Work

**Related Papers**
1. **Title**: The Bayesian brain: the role of uncertainty in neural coding and computation
   - **Authors**: Knill & Pouget
   - **Summary**: Demonstrates that neural systems represent uncertainty probabilistically and that precision is encoded in population codes, providing theoretical foundations for learning uncertainty representations.
   - **Year**: 2004

2. **Title**: Uncertainty-modulated prediction errors in cortical microcircuits
   - **Authors**: Wilmes et al.
   - **Summary**: Shows that cortical circuits generate precision-weighted prediction errors and that precision modulates learning signals, providing direct inspiration for precision head architecture and training objectives.
   - **Year**: 2025

3. **Title**: ConU: Conformal Uncertainty in LLMs (arXiv:2407.00499)
   - **Authors**: Wang et al.
   - **Summary**: Demonstrates that self-consistency correlates with correctness in LLMs and enables conformal prediction, validating self-consistency as a supervision signal for uncertainty quantification.
   - **Year**: 2024

4. **Title**: COPU: Conformal Prediction for UQ in NLG (arXiv:2502.12601)
   - **Authors**: Wang et al.
   - **Summary**: Addresses ground truth inclusion for conformal prediction in text generation, representing state-of-the-art post-hoc uncertainty quantification methods.
   - **Year**: 2025

5. **Title**: MC Dropout for Bayesian Approximation
   - **Authors**: Gal & Ghahramani
   - **Summary**: Establishes that dropout at test time approximates Bayesian inference, providing a standard uncertainty baseline approach using perturbation-based methods.
   - **Year**: 2016

6. **Title**: pyhgf: A neural network library for predictive coding
   - **Authors**: Legrand et al.
   - **Summary**: Demonstrates that predictive coding networks can be implemented with precision learning, supporting the feasibility of learning precision in neural network architectures.
   - **Year**: 2024

7. **Title**: Full-ECE: Token-level Calibration for LLMs
   - **Authors**: Liu et al.
   - **Summary**: Shows that traditional calibration metrics are inadequate for LLMs and that new approaches are needed for proper calibration assessment.
   - **Year**: 2024

**Key Challenges**
1. **Inadequate Traditional Calibration Metrics**: Traditional calibration metrics designed for classification tasks are inadequate for evaluating LLM calibration, necessitating new approaches for proper uncertainty assessment.
2. **Post-hoc Uncertainty Limitations**: Current state-of-the-art methods rely on post-hoc uncertainty quantification rather than learning uncertainty representations directly during training.
3. **Gap Between Neural Theory and LLM Practice**: While neuroscience demonstrates that biological systems learn precision-weighted representations, translating these principles to practical LLM architectures remains underexplored.
4. **Self-Consistency as Indirect Supervision**: Existing approaches use self-consistency as a proxy for uncertainty, but direct learning of precision representations could provide more principled uncertainty quantification.
