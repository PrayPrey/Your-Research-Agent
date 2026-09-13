## Related Work

**Related Papers**
1. **Title**: MoELoRA: Contrastive Learning Guided Mixture of Experts on Parameter-Efficient Fine-Tuning for Large Language Models (Semantic Scholar ID: af6aa336c25ead669da0df560376a32314e08006)
   - **Authors**: Tongxu Luo, Jiahe Lei, Fangyu Lei, et al.
   - **Summary**: Proposes contrastive learning to mitigate random routing phenomenon in MoE, achieving 4.2% improvement over vanilla LoRA across 11 math/common-sense reasoning tasks. Demonstrates that contrastive task embeddings enable effective routing specialization.
   - **Year**: 2024

2. **Title**: OLMoE: Open Mixture-of-Experts Language Models (Semantic Scholar ID: 817632c42e735911e14b89e851ceaf54ba2ad25f)
   - **Authors**: Niklas Muennighoff, Luca Soldaini, Dirk Groeneveld, et al. (Allen AI)
   - **Summary**: First fully open MoE model (7B params, 1B active) demonstrating high expert specialization through routing analysis. Establishes that expert specialization naturally emerges during training.
   - **Year**: 2024

3. **Title**: FSMoE: A Flexible and Scalable Training System for Sparse Mixture-of-Experts Models (Semantic Scholar ID: 103294b4f375e30f34e7e5463f06499cce3346a6)
   - **Authors**: Xinglin Pan, Wen-Jing Lin, Lin Zhang, et al.
   - **Summary**: Systems optimization achieving 1.18×-3.01× speedup over DeepSpeed-MoE through task scheduling and adaptive pipelining. Provides efficiency motivation for reducing expert over-activation.
   - **Year**: 2025

4. **Title**: Adapted-MoE
   - **Authors**: Not specified
   - **Summary**: Demonstrates calibration applied to MoE input features for anomaly detection, but does NOT apply calibration to routing decisions themselves.
   - **Year**: 2024

5. **Title**: Rewiring Experts
   - **Authors**: Not specified
   - **Summary**: Performs dynamic expert rerouting during inference but lacks a principled calibration framework for confidence quantification.
   - **Year**: 2025

6. **Title**: Mixtral-8x7B
   - **Authors**: Not specified
   - **Summary**: Standard sparse MoE baseline model using static top-K routing with fixed number of experts activated per input without adaptation.
   - **Year**: Not specified

**Key Challenges**
1. **Supervision Paradox**: Prior counterfactual approaches to routing quality assessment require ground truth labels for routing correctness, which are unavailable at test-time. This creates a paradox where evaluating routing quality requires the very supervision that test-time deployment lacks.

2. **Calibration Limited to Outputs**: Existing calibration methods (including temperature scaling) are applied only to final model predictions, not to routing decisions themselves. This leaves routing logits uncalibrated and prevents confidence-based adaptive expert activation.

3. **Static Routing Inefficiency**: Fixed top-K routing activates the same number of experts regardless of input difficulty or routing certainty, leading to unnecessary compute costs on high-confidence cases and potential underutilization of ensemble benefits on uncertain cases.

4. **Ensemble Agreement Ground Truth**: Establishing that ensemble agreement (low output entropy) correlates with routing quality requires validation without circular reasoning. Current literature demonstrates ensemble agreement indicates prediction confidence, but not specifically routing calibration quality.

5. **Cold-Start Calibration**: Initial temperature parameters for test-time calibration require either warm-up samples or pre-training on multi-task datasets. Transfer learning from pre-training to new deployment tasks is assumed but not validated in existing work.

6. **Task Embedding Generalization**: Contrastive learning-based task embeddings (as in MoELoRA) are shown to work across similar task distributions, but generalization to diverse downstream tasks at test-time without task labels remains an open question.

7. **Expert Specialization Dependency**: Adaptive routing mechanisms assume experts have already specialized during training. For randomly initialized or poorly trained MoE models, routing calibration cannot compensate for lack of underlying expert capacity.

8. **Multi-Task Benchmark Selection**: Evaluating routing quality across multiple tasks requires benchmarks with sufficient task diversity, but there is no consensus on appropriate benchmark selection (MMLU vs BIG-Bench vs custom multi-domain) for routing specialization assessment.
