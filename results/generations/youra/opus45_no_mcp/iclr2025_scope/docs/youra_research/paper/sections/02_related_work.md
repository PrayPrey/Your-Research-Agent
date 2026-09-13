# Related Work

Our work synthesizes three research threads — sub-quadratic architectures, efficient adaptation, and loss landscape analysis — to address the unexplored question of task-dependent adaptation under architecture conversion.

## Sub-Quadratic Architectures

The Transformer's quadratic attention complexity has motivated extensive work on sub-quadratic alternatives. Linear attention methods (Performer, cosFormer) replace softmax(QK^T)V with kernel-based approximations, achieving O(n) complexity but often degrading on tasks requiring precise attention patterns. State space models, particularly S4 and its successor Mamba, offer a fundamentally different approach: selective scan operations that evolve hidden state sequentially, achieving transformer-quality performance with linear complexity.

Mamba demonstrates SSM-attention duality, showing that attention and state space operations are structurally connected. Mamba-2 formalizes this duality, enabling principled conversion between architectures. However, existing evaluations focus on pretraining quality rather than post-conversion adaptation behavior. Hybrid architectures like Jamba interleave Mamba layers with sparse attention, suggesting that different architectural components serve different functions — a perspective our work makes precise through task-dependent analysis.

## Efficient Adaptation Methods

LoRA introduced low-rank weight decomposition for efficient fine-tuning, enabling adaptation of large models by training only O(rank × d) parameters. The method's success on Transformers led to variants (QLoRA, DoRA) and adoption across architectures. HuggingFace PEFT supports Mamba LoRA targeting on analogous projection layers (in_proj/out_proj versus QKV/O).

Yet all LoRA studies assume fixed architecture, missing how architecture change affects adaptation efficiency. Our work fills this gap by characterizing LoRA behavior under Transformer-to-Mamba conversion, discovering that effective rank varies systematically with task type after conversion — a phenomenon invisible in single-architecture studies.

## Loss Landscape Analysis

Sharpness-aware minimization (SAM) established the connection between loss landscape geometry and generalization: flatter minima generalize better. This insight spawned landscape analysis as a tool for understanding model behavior, with sharpness and curvature metrics predicting training dynamics.

We extend landscape analysis to architecture conversion, discovering that conversion itself transforms landscape geometry (219% sharpness change). More importantly, we connect landscape sharpness to LoRA effective rank (ρ=1.0), providing mechanistic explanation for task-dependent adaptation efficiency — a connection absent from both the SAM literature and efficient adaptation work.

## Positioning Our Work

Prior work addresses each component separately: Mamba achieves efficient pretraining, LoRA enables efficient adaptation on Transformers, SAM connects landscapes to generalization. Our contribution is the synthesis: first systematic study of how architecture conversion transforms LoRA adaptation efficiency in task-dependent ways, with loss landscape geometry as the explanatory mechanism. This enables a priori prediction of conversion success from task retrieval density — a capability no prior work provides.
