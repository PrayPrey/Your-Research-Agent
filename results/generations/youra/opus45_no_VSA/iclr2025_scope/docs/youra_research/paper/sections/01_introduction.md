# Introduction

A model achieving 95% accuracy on standard benchmarks can fail to generalize when adapter selection depends on task-specific validation data that doesn't exist at deployment. This gap between benchmark performance and real-world applicability is particularly acute for multi-task language models that rely on specialized LoRA adapters—the dominant approach for parameter-efficient fine-tuning of modern LLMs.

The surface problem is well understood: multi-task models benefit from task-specialized adapters, but selecting the right adapter at inference requires knowing the task. Current routing methods address this through various mechanisms: LoRAHub [Huang et al., 2023] uses gradient-free optimization over validation loss; LORAUTER [Dhasade et al., 2026] routes via task embeddings computed from validation examples; MoELoRA [Luo et al., 2024] trains routing jointly with adapters. All assume access to task-specific validation data—at least 5 examples per task—to make routing decisions.

A deeper challenge emerges in zero-shot settings. When a model encounters a novel instruction for the first time, no validation examples exist. The instruction itself is all we have. This raises a fundamental question that prior work has not addressed: *Does the instruction contain sufficient signal for adapter routing, without any task examples?*

We hypothesize that the answer is yes—and that the alignment between instruction semantics and adapter specializations already exists intrinsically, inherited from the base model's instruction-tuning. If true, zero-shot routing becomes possible without validation data or gradient computation.

Our key insight is that **instruction prefixes embedded by frozen sentence encoders are linearly separable by task family**. Using MiniLM-L6-v2 embeddings of FLAN instruction prefixes, we find that a simple logistic regression achieves macro-F1 = 0.995 on task family classification. This near-perfect separability enables a linear probe to predict the optimal adapter with 72.67% top-1 accuracy (95.78% top-3), and the resulting zero-shot routing achieves 95% of oracle adapter performance.

Building on this insight, we make the following contributions:

1. **Empirical demonstration of intrinsic alignment.** We show that instruction embeddings from a frozen sentence encoder cluster by task family with near-perfect linear separability (F1 = 0.995), suggesting that instruction semantics and adapter specializations share geometric structure without requiring joint training.

2. **Zero-shot adapter routing (IPCR).** We introduce Instruction-Prefix-Conditioned Routing, a simple approach using frozen MiniLM embeddings and a linear probe that achieves 95% of oracle performance on FLAN task families—eliminating the need for validation data.

3. **Characterization of routing fragility.** We identify a critical limitation: routing depends on lexical keywords rather than deep semantic invariants. Paraphrase perturbations cause embedding drift (cosine 0.78), and keyword masking produces 44% accuracy drops. This honest characterization informs when IPCR is—and is not—appropriate.

The remainder of this paper is organized as follows. Section 2 discusses related work on adapter composition and routing. Section 3 describes our methodology. Section 4 presents experimental setup, and Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes with future directions.
