## Related Work

**Related Papers**
1. **Title**: COPU - Conformal Prediction for LLMs
   - **Authors**: Wang et al.
   - **Summary**: Uses logit scores to measure nonconformity for conformal prediction on LLM outputs. However, assumes i.i.d. calibration sets and the sampling-based method cannot guarantee inclusion of ground truth.
   - **Year**: 2025

2. **Title**: CPQ - Conformal Prediction with Query-Only Access
   - **Authors**: Noorani et al.
   - **Summary**: Uses missing mass estimators for black-box LLMs, connecting to entropy via Good-Turing estimators. Provides framework validating entropy-based approaches for generative models.
   - **Year**: 2025

3. **Title**: U-TraCE - Traceable Uncertainty Conformal Estimation
   - **Authors**: Marchi & Liebl
   - **Summary**: Provides explicit numerical bound on error probability and demonstrates that black-box conformal prediction can achieve traceable uncertainty bounds via calibration.
   - **Year**: 2026

4. **Title**: A Mathematical Theory of Communication
   - **Authors**: Shannon
   - **Summary**: Established Shannon entropy as the canonical uncertainty measure for discrete distributions with well-established properties including non-negativity and maximization for uniform distributions.
   - **Year**: 1948

5. **Title**: Maximum Entropy Methods in Non-Equilibrium Statistical Physics
   - **Authors**: Jaynes
   - **Summary**: Provided framework for maximum entropy methods in non-equilibrium systems, establishing precedent for sequential entropy accumulation handling dependencies.
   - **Year**: 1957

6. **Title**: Classical Conformal Prediction Theory
   - **Authors**: Vovk et al.
   - **Summary**: Proved coverage guarantees under exchangeability assumption. Established that exchangeability is weaker than i.i.d. and that quantile-based threshold selection achieves coverage (n+1)/(n+2) ≥ 1-α.
   - **Year**: 2005

7. **Title**: Algorithmic Learning in a Random World
   - **Authors**: Vovk
   - **Summary**: Established that exchangeability is sufficient for conformal prediction coverage guarantees without requiring full i.i.d. assumptions.
   - **Year**: 1999

8. **Title**: Good-Turing Frequency Estimation
   - **Authors**: Good-Turing
   - **Summary**: Developed missing mass estimation theory that connects to entropy, providing theoretical foundation for probability estimation in sparse data scenarios.
   - **Year**: 1953

9. **Title**: Dataset Shift in Machine Learning
   - **Authors**: Quiñonero-Candela et al.
   - **Summary**: Documented distribution shift as a common challenge in ML deployment, relevant to calibration set representativeness assumption.
   - **Year**: 2009

**Key Challenges**
1. **I.I.D. Assumption Violation in Auto-Regressive Generation**: Standard conformal prediction methods (COPU, CPQ, U-TraCE) assume i.i.d. calibration sets or use static nonconformity measures, which fail to provide valid coverage guarantees for auto-regressive LLM generation due to sequential dependencies.

2. **Statistical Validation Methods for Black-Box Conformal Prediction**: Gap in methods that can provide formal coverage guarantees for generative outputs without requiring white-box access to model internals, while handling sequential dependencies in generation.

3. **Coverage Guarantees Under Weaker Assumptions**: Need for conformal prediction frameworks that work under exchangeability (weaker than i.i.d.) while maintaining distribution-free coverage guarantees.

4. **Token Probability Accessibility**: Many production LLM APIs do not provide token-level probability distributions, limiting applicability of probability-based nonconformity measures.

5. **Distribution Shift in Deployment**: Calibration set representativeness often violated in real deployment scenarios due to domain shift, temporal drift, and adversarial inputs, leading to coverage degradation.

6. **Computational Efficiency**: Need for conformal prediction methods that maintain O(n) complexity per token rather than O(n²) for naive CP adaptations to sequential generation.

7. **Context Length Adaptation**: Challenge of maintaining consistent coverage across varying context lengths in LLM generation tasks.

8. **Practical Usability**: Balancing coverage guarantees with prediction set size - sets that are too large (>20 candidates) become impractical for deployment despite achieving nominal coverage.
