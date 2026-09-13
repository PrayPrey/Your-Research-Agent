## Related Work

**Related Papers**
1. **Title**: Deja Vu: Contextual Sparsity for Efficient LLMs at Inference Time (Semantic Scholar ID: 95240dda409e28acccdc5cf619ad0c036cf4292d)
   - **Authors**: Liu et al.
   - **Summary**: Demonstrated that contextual sparsity exists in LLMs and is predictable, achieving 2x inference speedup without accuracy loss through exploiting this sparsity pattern.
   - **Year**: 2023

2. **Title**: ShadowLLM: Predictor-based Contextual Sparsity for Large Language Models (Semantic Scholar ID: 7628db8e0dee79557a0014296f53459f13bf016b)
   - **Authors**: Akhauri et al.
   - **Summary**: Introduced neural predictors that shadow LLM behavior to predict contextual sparsity, achieving 15% better sparsity accuracy compared to prior methods.
   - **Year**: 2024

3. **Title**: Interpretable Steering with Feature Guided Activation Additions (Semantic Scholar ID: 89f55a1eb9bb1794998cb0cd4251abf8c1964a97)
   - **Authors**: Soo et al.
   - **Summary**: Demonstrated that SAE features enable precise model steering through activation manipulation, validating that SAE features can guide activation-level decisions.
   - **Year**: 2025

4. **Title**: Gemma Scope: Open Sparse Autoencoders on Gemma 2 (Semantic Scholar ID: 890efc891e9b59e8cb5e8c244428f6b81ec0a4da)
   - **Authors**: Lieberum et al.
   - **Summary**: Released JumpReLU SAEs trained across all layers of Gemma 2 models (2B, 9B, 27B parameters), providing open pre-trained sparse autoencoders for the research community.
   - **Year**: 2024

5. **Title**: Sparse Autoencoder Features for Classifications and Transferability (Semantic Scholar ID: d7c37ff4a8de31c5a30346ff85aec79056e30b48)
   - **Authors**: Gallifant et al.
   - **Summary**: Showed that SAE features transfer across models and achieve high classification accuracy, validating that SAE features capture task-relevant information.
   - **Year**: 2025

6. **Title**: R-Sparse
   - **Authors**: Not specified
   - **Summary**: A training-free rank-aware sparsity approach that serves as an alternative method for efficient LLM inference.
   - **Year**: Not specified

**Key Challenges**
1. **Disconnected Research Tracks**: SAE interpretability research and dynamic sparsity research have developed as parallel tracks without an existing bridge connecting their methodologies and insights.

2. **Unweighted Sparsity Predictions**: Current contextual sparsity methods like DejaVu use unweighted approaches that do not leverage semantic importance information when making sparsity decisions.

3. **Limited Semantic Awareness in Predictors**: Existing neural predictors for sparsity (e.g., ShadowLLM) do not incorporate interpretable feature representations like SAE weights to inform their predictions.

4. **Unexplored SAE-Sparsity Integration**: No prior work has explored using SAE features specifically for sparsity prediction, as confirmed by knowledge base searches returning no matches for "SAE sparsity prediction."
