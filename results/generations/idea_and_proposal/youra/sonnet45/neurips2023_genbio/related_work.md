## Related Work

**Related Papers**

1. **Title**: Uehara et al. (2024) - RL-based gradient guidance for diffusion models
   - **Authors**: Not specified
   - **Summary**: Demonstrates RL-based gradient guidance for diffusion models can optimize biological rewards (stability, docking score); provides algorithmic foundation for Pareto gradient guidance.
   - **Year**: 2024

2. **Title**: Kang et al. (2025) - Self-improving closed-loop frameworks
   - **Authors**: Not specified
   - **Summary**: Identifies self-improving closed-loop frameworks as emerging but unrealized need in biological design; motivates active learning feedback architecture.
   - **Year**: 2025

3. **Title**: Das (2025) - Precision medicine challenges
   - **Authors**: Not specified
   - **Summary**: Reviews precision medicine challenges (toxicity, off-target effects, heterogeneity) requiring multi-objective optimization in therapeutic design.
   - **Year**: 2025

4. **Title**: Rudden et al. (2022) - Conformational flexibility in generative models
   - **Authors**: Not specified
   - **Summary**: Notes conformational flexibility missing from generative models; highlights need for multi-conformational constraint evaluation.
   - **Year**: 2022

5. **Title**: Watson et al. (2022) - RFdiffusion
   - **Authors**: Not specified
   - **Summary**: RFdiffusion demonstrates structure prediction + diffusion integration achieves 50-70% experimental success for single constraints; provides architectural foundation for diffusion-based generation.
   - **Year**: 2022

6. **Title**: Kennedy & O'Hagan (2000) - Multi-fidelity optimization theory
   - **Authors**: Kennedy, O'Hagan
   - **Summary**: Theoretical foundation for surrogate-based optimization with provable convergence guarantees in aerospace engineering.
   - **Year**: 2000

7. **Title**: Peherstorfer et al. (2018) - Multi-fidelity methods
   - **Authors**: Peherstorfer et al.
   - **Summary**: Survey of multi-fidelity methods for uncertainty quantification and optimization, establishing mathematical framework for hierarchical surrogate models.
   - **Year**: 2018

8. **Title**: Lookman et al. (2019) - Active learning in materials science
   - **Authors**: Lookman et al.
   - **Summary**: Demonstrates acquisition function design for materials discovery with 3-10x acceleration over random sampling through uncertainty-based experiment selection.
   - **Year**: 2019

9. **Title**: Ling et al. (2017) - Materials discovery acceleration
   - **Authors**: Ling et al.
   - **Summary**: Empirical demonstration of active learning acceleration in materials science, showing 3-10x speedup in materials property optimization.
   - **Year**: 2017

**Key Challenges**

1. **AI-to-Experiment Translation Gap**: Biological generative models achieve high computational success (70-90%) but suffer from 70-90% wet-lab failure rates due to disconnect between model predictions and experimental validation.

2. **Constraint Predictor Accuracy**: Existing constraint predictors for toxicity achieve only ~70-75% accuracy, below threshold needed for reliable biological design; stability and affinity predictors more achievable at ~85-90%.

3. **Multi-Objective Optimization Complexity**: Current approaches struggle with multi-objective gradient conflicts when optimizing 3+ biological constraints simultaneously; Pareto guidance unproven for biological design spaces.

4. **Computational Feasibility**: SE(3)-equivariant neural networks required for molecular geometry impose significant computational costs that may exceed academic lab capacity without acceleration strategies.

5. **Active Learning Cold Start Problem**: Initial constraint predictors may have poor accuracy before experimental feedback, limiting effectiveness of early active learning iterations.

6. **Distribution Shift**: Generative models may produce out-of-distribution molecules where constraint predictors fail to generalize, invalidating predictions on novel molecular structures.

7. **Experimental Noise**: Biological assay variability (thermal shift, binding affinity measurements) can corrupt predictor retraining if noise exceeds 10-20%, degrading rather than improving model performance.

8. **Single-Constraint Focus**: Most existing biological generative models (including RFdiffusion) optimize single constraints, achieving 50-70% success for single objectives but lacking frameworks for multi-constraint satisfaction.

9. **Limited Feedback Integration**: Current workflows lack systematic integration of experimental feedback to improve model predictions, treating generation and validation as separate steps rather than closed loops.

10. **Cross-Domain Transfer Validation**: While multi-fidelity optimization and active learning are proven in aerospace/materials science, their effectiveness in biological design remains unvalidated due to domain-specific challenges (biological variability, complex constraint landscapes).
