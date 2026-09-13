# Related Work

Our work connects three research threads: sub-quadratic sequence models, efficient adaptation methods, and architecture conversion. Each thread has made significant progress independently, but none addresses the adaptation preservation problem during conversion.

## Sub-Quadratic Sequence Models

The quadratic complexity of transformer attention has motivated extensive work on efficient alternatives. Longformer [Beltagy et al., 2020] and BigBird [Zaheer et al., 2020] introduce sparse attention patterns that reduce complexity to O(n). Linear attention methods [Katharopoulos et al., 2020] reformulate attention as a kernel feature map, achieving O(n) complexity but sacrificing expressiveness.

More recently, state space models have emerged as a principled sub-quadratic alternative. Mamba [Gu and Dao, 2023] introduces selective state spaces with input-dependent gating, achieving transformer-level performance at O(n) complexity. RWKV [Peng et al., 2023] combines linear attention with RNN-style recurrence. These architectures excel at efficiency but provide no mechanism for task-specific adaptation during deployment. Our work extends Mamba with task conditioning that preserves adaptation capability.

## Efficient Adaptation Methods

Adapting large models to downstream tasks efficiently has driven development of parameter-efficient methods. LoRA [Hu et al., 2021] learns low-rank updates to pretrained weights, reducing trainable parameters to ~0.1% while maintaining performance. Adapters [Houlsby et al., 2019] insert small bottleneck modules between transformer layers. Prompt tuning [Lester et al., 2021] optimizes soft prompts prepended to inputs.

These methods assume the base model preserves adaptation capability—an assumption that breaks when converting architectures. LoRA applied post-conversion must work with degraded internal representations. TC-SSM differs fundamentally: we integrate task conditioning *during* conversion, preserving the adaptation manifold rather than compensating for its loss.

## Model Conversion and Distillation

Knowledge distillation [Hinton et al., 2015] transfers knowledge from teacher to student models by matching output distributions. For architecture conversion, distillation typically optimizes KL divergence on logits and MSE on hidden states. StreamingLLM [Xiao et al., 2023] and H2O [Zhang et al., 2023] focus on KV cache compression for efficient inference, maintaining output quality without changing the architecture.

The conversion literature optimizes for output fidelity, not adaptation preservation. A converted model may match teacher accuracy on fixed tasks while losing the ability to quickly adapt to new ones. TC-SSM introduces an adaptation regularizer during conversion training that explicitly preserves task-conditioned dynamics, addressing a gap that pure output matching cannot fill.

## Positioning TC-SSM

Prior work addresses efficiency (Mamba, RWKV), adaptation (LoRA, adapters), or output preservation (distillation) in isolation. TC-SSM is the first method to co-design conversion and adaptation, integrating task conditioning into the conversion process itself. This enables sub-quadratic models that retain transformer-level few-shot capability without post-hoc compensation.
