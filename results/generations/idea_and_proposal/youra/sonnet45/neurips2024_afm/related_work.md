## Related Work

**Related Papers**

1. **Title**: A Comprehensive Survey of Continual Learning with PEFT Methods (CL Survey)
   - **Authors**: Yang et al.
   - **Summary**: Provides a taxonomy of parameter-efficient fine-tuning (PEFT) methods for continual learning, establishing that PEFT approaches effectively reduce catastrophic forgetting in sequential learning scenarios.
   - **Year**: 2024

2. **Title**: RanPAC: Random Projections and Pre-trained Models for Continual Learning
   - **Authors**: McDonnell et al.
   - **Summary**: Demonstrates that limiting parameter updates through random projections prevents catastrophic forgetting, achieving 20-62% error reduction compared to naive sequential training. Shows parameter limitation is an effective mechanism for continual learning.
   - **Year**: 2023

3. **Title**: LLM-Adapters: An Adapter Family for Parameter-Efficient Fine-Tuning of Large Language Models
   - **Authors**: Hu et al.
   - **Summary**: Presents a framework for multi-adapter integration in large language models, demonstrating that adapter-based PEFT achieves comparable performance to full fine-tuning with only 0.1-2% of parameters. Validates that 7B models with adapters can match 175B model zero-shot performance.
   - **Year**: 2023

4. **Title**: PIECE: Parameter-Efficient Instance-wise Continual Learning
   - **Authors**: Wang et al.
   - **Summary**: Introduces parameter importance estimation for continual learning, focusing on identifying which parameters are critical for preventing forgetting while enabling efficient adaptation to new tasks.
   - **Year**: 2025

5. **Title**: FLoRA: Low-Rank Adaptation with Optimal Budget Allocation across Layers
   - **Authors**: Wen et al.
   - **Summary**: Proposes batched heterogeneous LoRA for per-example personalization, demonstrating that unique LoRA weights can be efficiently applied to different examples within the same batch for fine-grained adaptation.
   - **Year**: 2023

6. **Title**: Federated Learning with Personalized Adaptation for Heterogeneous Clients
   - **Authors**: Zhang et al.
   - **Summary**: Presents lightweight per-user personalized adapters in federated learning settings, achieving +25% improvement in recommender systems. Demonstrates that per-user adapter subsets enable effective personalization at scale.
   - **Year**: 2024

7. **Title**: UniAdapter: Unified Parameter-Efficient Transfer Learning for Cross-modal Foundation Models
   - **Authors**: Lu et al.
   - **Summary**: Validates cross-modal PEFT effectiveness, showing that adapter-based methods work across vision, language, and multi-modal domains. Establishes that LoRA-style approaches generalize beyond single-modality settings.
   - **Year**: 2023

8. **Title**: LoRA: Low-Rank Adaptation of Large Language Models
   - **Authors**: Not specified
   - **Summary**: Introduces the foundational low-rank decomposition mechanism (ΔW=BA) for parameter-efficient fine-tuning, achieving 98-99% parameter reduction while preserving performance. Core technical foundation for LoRA-based adaptation methods.
   - **Year**: Not specified

9. **Title**: Elastic Weight Consolidation (EWC)
   - **Authors**: Not specified
   - **Summary**: Regularization-based continual learning method that protects important weights using Fisher Information matrix. Achieves good continual learning (BWT ≈ -8%) but requires updating 100% of model parameters.
   - **Year**: Not specified

10. **Title**: X-LoRA: Mixture of LoRA Experts
   - **Authors**: Not specified
   - **Summary**: Implements gating network for adaptive LoRA adapter selection in multi-task settings, using winner-take-all routing. Provides moderate continual learning (BWT ≈ -15%) with parameter efficiency (~0.3% active parameters).
   - **Year**: Not specified

11. **Title**: PEFT Library Documentation
   - **Authors**: Not specified
   - **Summary**: Production infrastructure for parameter-efficient fine-tuning, providing standardized implementation of LoRA and related adapter methods. Establishes best practices for LoRA rank selection (r=8-16) and application to attention layers.
   - **Year**: Not specified

12. **Title**: AnimateDiff: Animate Your Personalized Text-to-Image Diffusion Models
   - **Authors**: Not specified
   - **Summary**: Demonstrates modular adapter injection pattern where a train-once module can be applied to all personalized model versions. Validates modular growth and scalability of adapter-based approaches. Published as ICLR 2024 spotlight.
   - **Year**: 2024

13. **Title**: CLIP: Contrastive Language-Image Pre-training
   - **Authors**: Not specified
   - **Summary**: Vision-language foundation model trained on 400M image-text pairs, providing strong zero-shot learning capabilities and semantic embeddings for multi-modal understanding. Used as base model and zero-shot encoder in this work.
   - **Year**: Not specified

14. **Title**: GPT-2: Language Models are Unsupervised Multitask Learners
   - **Authors**: Not specified
   - **Summary**: Transformer-based language model serving as a standard foundation model for text-only experiments. Used as baseline architecture for evaluating adapter-based adaptation methods.
   - **Year**: Not specified

15. **Title**: AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning
   - **Authors**: Not specified
   - **Summary**: Proposes adaptive rank selection for LoRA adapters on a per-task basis, allowing different tasks to use different ranks based on complexity. Enables flexible trade-off between efficiency and task-specific performance.
   - **Year**: Not specified

16. **Title**: SentenceTransformers
   - **Authors**: Not specified
   - **Summary**: Pre-trained text encoders fine-tuned on diverse NLP tasks, providing semantic embeddings for text similarity and zero-shot task classification. Used for task encoding and similarity-based routing in text-only settings.
   - **Year**: Not specified

**Key Challenges**

1. **Unified Multi-Objective Integration**: Existing methods address continual learning OR personalization OR parameter efficiency in isolation but lack unified frameworks that simultaneously optimize for all three objectives. Current SOTA methods achieve only one objective at the expense of others.

2. **Catastrophic Forgetting in Sequential Learning**: Neural networks suffer severe performance degradation on previously learned tasks when trained on new tasks (BWT < -50% for full fine-tuning). While regularization methods like EWC help (BWT ≈ -8%), they require updating 100% of parameters, sacrificing efficiency.

3. **Adapter Composition Risk**: No systematic study exists on how multiple LoRA adapters compose when combined via weighted linear combination. Unvalidated composition may lead to destructive interference and performance degradation, representing a critical technical risk.

4. **Cold-Start Problem for Novel Tasks**: Routing mechanisms require task-specific training data, creating challenges for generalizing to unseen task types. Zero-shot routing to novel task categories needs validation to ensure system applicability beyond training distribution.

5. **Parameter Efficiency vs Performance Trade-off**: While single LoRA adapters achieve 0.1-0.5% parameter overhead, using multiple adapters (k=3-5) increases overhead. Maintaining < 1% total active parameters while supporting multi-objective adaptation requires careful design.

6. **Personalization at Scale**: Per-user full fine-tuning achieves strong personalization (+15-20% gain) but requires 100% × U parameters for U users, making it impractical. Lightweight per-user adaptation methods need to maintain personalization benefits with linear storage costs O(U) and constant inference costs.

7. **Task Similarity Measurement**: Effective routing depends on meaningful task similarity metrics. Semantic embedding similarity (cosine distance in CLIP/SentenceTransformer space) needs empirical validation that it correlates with actual transfer learning potential (Pearson r > 0.5 expected).

8. **Production Deployment Gaps**: Most continual learning research focuses on benchmark performance rather than production deployment considerations like zero-downtime updates, failure mode protection, and graceful degradation. Real-world adaptive foundation models need robust operational characteristics.

9. **Multi-Modal Adaptation Complexity**: Extending adaptation methods from uni-modal (vision or language only) to multi-modal settings introduces additional complexity in task encoding, similarity measurement, and adapter composition across modality boundaries.

10. **Limited Theoretical Understanding**: While empirical results show PEFT methods work for continual learning, theoretical explanations for why parameter limitation prevents forgetting (e.g., parameter space orthogonality in modular PEFT) lack formal analysis and proofs.
