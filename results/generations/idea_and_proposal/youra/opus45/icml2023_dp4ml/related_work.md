## Related Work

**Related Papers**
1. **Title**: Rethinking Attention-Model Explainability through Faithfulness Violation Test (arXiv:2201.12114)
   - **Authors**: Liu, Li, Guo, Kong, Li, Wang
   - **Summary**: Demonstrates that raw attention explanations suffer from faithfulness violation where features with higher attention weights may actually suppress predictions. Proposes a diagnostic test for evaluating attention faithfulness.
   - **Year**: 2022

2. **Title**: On the Faithfulness of Vision Transformer Explanations (arXiv:2404.01415)
   - **Authors**: Wu, Kang, Tang, Hong, Yan
   - **Summary**: Introduces SaCo (Salience-guided Faithfulness Coefficient) as an evaluation metric and demonstrates that combining gradient information with multi-layer aggregation improves explanation faithfulness.
   - **Year**: 2024

3. **Title**: Sparse Continuous Distributions and Fenchel-Young Losses
   - **Authors**: Martins, Treviso, Farinhas, Aguiar, Figueiredo, Blondel, Niculae
   - **Summary**: Shows that Tsallis negentropy produces sparse probability distributions and introduces continuous-domain attention mechanisms using alpha-entmax.
   - **Year**: 2022

4. **Title**: Sparse Regularized Optimal Transport with Deformed q-Entropy
   - **Authors**: Bao, Sakaue
   - **Summary**: Demonstrates that q-deformed entropy produces sparse optimal transport plans with provable convergence guarantees.
   - **Year**: 2022

5. **Title**: Sinkformers
   - **Authors**: Not specified
   - **Summary**: Applies optimal transport attention mechanisms for computational efficiency purposes rather than interpretability.
   - **Year**: 2022

6. **Title**: Integrated Gradients
   - **Authors**: Sundararajan et al.
   - **Summary**: Proposes a gradient-based attribution method for explaining model predictions.
   - **Year**: 2017

7. **Title**: Attention Rollout
   - **Authors**: Abnar, Zuidema
   - **Summary**: Introduces an attention propagation method for aggregating attention across transformer layers.
   - **Year**: 2020

**Key Challenges**
1. **Faithfulness Violation in Attention**: Raw attention weights do not reliably indicate feature importance, as features with higher attention weights may actually suppress model predictions rather than support them.

2. **Lack of Unified OT-Interpretability Framework**: Optimal transport duality concepts and interpretability methods have been studied independently, with no existing implementations that combine OT duality principles with deep learning interpretability.

3. **Sparse Attention for Interpretability**: Existing optimal transport attention mechanisms (e.g., Sinkformers) focus on computational efficiency rather than producing interpretable, sparse attention distributions that improve explanation faithfulness.
