# Related Work

We position our work at the intersection of parameter-efficient fine-tuning, adapter composition, and routing mechanisms for multi-task models.

## Parameter-Efficient Fine-Tuning

Low-Rank Adaptation (LoRA) [Hu et al., 2021] introduced rank-decomposition matrices injected into transformer layers, achieving comparable performance to full fine-tuning with <1% trainable parameters. This foundational work enabled the adapter paradigm we build upon. AdapterFusion [Pfeiffer et al., 2021] demonstrated that task-specific adapters can be combined non-destructively through learned attention, outperforming multi-task learning on 16 NLU tasks. These methods establish that adapter combination is both mathematically valid (LoRA deltas are additive) and empirically effective.

However, existing composition methods require knowing which adapters to combine for a given input—the routing problem we address.

## Dynamic Adapter Routing

Recent work has explored input-conditioned adapter selection. LoRAHub [Huang et al., 2023] achieves cross-task generalization via gradient-free composition, optimizing adapter weights over few-shot validation loss. The approach achieves upper-bound performance exceeding in-context learning on Big-Bench Hard, but requires validation examples to compute the optimization objective.

LORAUTER [Dhasade et al., 2026] routes queries using task embeddings computed from validation sets, achieving 101.2% of oracle performance on task-aligned adapters and +5.2 points on unseen tasks. The method scales to 1500+ adapters but fundamentally relies on 5+ validation examples per task to construct the routing representation.

MoELoRA [Luo et al., 2024] treats LoRA modules as MoE experts with contrastive learning to encourage distinct specialization, achieving +4.2% over vanilla LoRA on math reasoning. However, routing is jointly trained with adapters, precluding generalization to new tasks without retraining.

Multi-Head Adapter Routing (MHR) [Caccia et al., 2022] combines adapter subsets with learned routing weights, providing finer-grained expressivity. HMoRA [Liao et al., 2025] extends this to hierarchical routing with auxiliary losses.

**Gap:** All existing routing methods either require validation data (LoRAHub, LORAUTER), joint training (MoELoRA, MHR), or gradient signals at test time. None test whether instruction-adapter alignment exists intrinsically—without any task-specific training signal.

## Instruction Tuning and Task Representations

FLAN [Wei et al., 2022] demonstrated that instruction-tuned models condition behavior on instruction format across diverse task families. T0 [Sanh et al., 2022] showed zero-shot generalization through unified prompting. These works suggest that instruction prefixes encode meaningful task semantics.

Sentence encoders like MiniLM [Wang et al., 2020] and Sentence-BERT [Reimers and Gurevych, 2019] compress text into fixed-dimensional embeddings via contrastive pretraining. SimCSE [Gao et al., 2021] demonstrated that such embeddings provide paraphrase invariance—a property we test explicitly in our robustness experiments.

**Our position:** We ask whether frozen instruction embeddings, without any adapter-specific training, can route to specialized LoRAs. We test the simplest possible approach—linear probe on MiniLM embeddings—to determine if intrinsic alignment exists before adding complexity.
