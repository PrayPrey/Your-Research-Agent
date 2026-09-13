## Related Work

**Related Papers**
1. **Title**: SPARC: Concept-Aligned Sparse Autoencoders for Cross-Model and Cross-Modal Interpretability (arXiv:2507.06265)
   - **Authors**: Ali Nasiri-Sarvi, Hassan Rivaz, Mahdi S. Hosseini
   - **Summary**: Introduces cross-reconstruction loss with Global TopK achieving Jaccard similarity 0.80 across models, providing technique for feature-expert affinity learning and semantic consistency between models.
   - **Year**: 2025

2. **Title**: Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts (arXiv:2408.15664)
   - **Authors**: Lean Wang, Huazuo Gao, et al.
   - **Summary**: Expert-wise bias achieves load balance without gradient interference, validating loss-free balancing approach compatible with feature-based routing.
   - **Year**: 2024

3. **Title**: SAEBench: A Comprehensive Benchmark for Sparse Autoencoders in Language Model Interpretability (arXiv:2503.09532)
   - **Authors**: Adam Karvonen, Can Rager, Johnny Lin, et al.
   - **Summary**: Establishes feature disentanglement metrics; demonstrates that Matryoshka SAEs outperform on disentanglement despite lower proxy metrics, providing evaluation framework for interpretability validation.
   - **Year**: 2025

4. **Title**: Demons in the Detail: On Implementing Load Balancing Loss for Training Specialized Mixture-of-Expert Models
   - **Authors**: Zihan Qiu, Zeyu Huang, et al.
   - **Summary**: Global-batch load balancing enables corpus-level expert specialization, informing routing strategy for domain-specific expert development.
   - **Year**: 2025

5. **Title**: Standard Learned MoE Routing (e.g., Mixtral 8×7B)
   - **Authors**: Not specified
   - **Summary**: Baseline approach using opaque learned routing weights without interpretability, serving as benchmark for performance parity target (≥95% of learned routing accuracy).
   - **Year**: Not specified

6. **Title**: Post-Hoc SAE Interpretability Methods
   - **Authors**: Not specified
   - **Summary**: SAEs trained after model deployment for analysis (not integrated in routing), serving as benchmark for integration overhead and interpretability-efficiency tradeoff comparison.
   - **Year**: Not specified

7. **Title**: SAELens Framework
   - **Authors**: Not specified
   - **Summary**: Implementation resource demonstrating that existing SAE tools focus on post-hoc analysis rather than co-training with MoE routing.
   - **Year**: Not specified

8. **Title**: makeMoE + scattermoe
   - **Authors**: Not specified
   - **Summary**: MoE implementations lacking interpretability integration; scattermoe provides Triton optimization baseline for hardware efficiency comparison.
   - **Year**: Not specified

**Key Challenges**
1. **Post-Hoc vs. Online Interpretability**: Existing SAE interpretability tools (e.g., SAELens) focus on post-hoc analysis after model deployment, not integration during training with routing mechanisms.

2. **Performance-Interpretability Tradeoff**: Standard MoE routing (e.g., Mixtral 8×7B) achieves high performance through opaque learned weights but lacks interpretability, creating need for methods that maintain ≥95% performance while adding interpretability.

3. **Cross-Reconstruction Loss Transfer**: SPARC's cross-reconstruction loss was designed for post-hoc model alignment (static analysis), requiring adaptation for online routing optimization (dynamic training) context.

4. **Feature Stability During Co-Training**: Risk of catastrophic feature collapse when co-training SAEs with MoE routing objectives, requiring validation that features remain semantically stable across training epochs.

5. **Load Balance Without Gradient Interference**: Need for routing mechanisms that maintain balanced expert utilization without auxiliary loss gradient interference, addressed by expert-wise bias approaches.

6. **Expert Specialization Measurement**: Lack of standardized metrics for measuring expert specialization patterns and domain-specific routing concentration in MoE systems.

7. **Hardware Efficiency for Interpretable Routing**: Integration of interpretability mechanisms must maintain competitive inference speed and memory overhead compared to standard learned routing approaches.

8. **Multi-Objective Training Complexity**: Balancing multiple loss objectives (reconstruction, routing alignment, task performance) requires careful hyperparameter tuning and staged training protocols.
