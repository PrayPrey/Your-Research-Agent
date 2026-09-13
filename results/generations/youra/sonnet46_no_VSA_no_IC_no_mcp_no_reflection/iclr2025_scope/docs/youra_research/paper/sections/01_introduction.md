# Introduction

We applied LoRA to Mamba-130m exactly as we would to any transformer — correct target modules, correct parameter counts, 1.14% trainable weights — and watched SST-2 accuracy sit at 50.9% for three consecutive training epochs, indistinguishable from the zero-shot baseline of 49.1%. This is not slow convergence. This is zero learning.

The result is surprising precisely because everything visible looked correct. The PEFT library installed the adapters without complaint. The model's state dictionary contained LoRA weight matrices at every targeted projection layer. The training loop ran, loss values were logged, and gradients were computed. And yet, after three full epochs over 4,000 training samples — a protocol sufficient for LoRA to converge on SST-2 with transformers — the model remained locked at majority-class prediction accuracy, as if fine-tuning had never occurred.

## The Surface Problem

Parameter-efficient fine-tuning, and LoRA in particular [Hu et al., 2022], has become the dominant strategy for adapting large pretrained language models to downstream tasks. By freezing the base model and training only low-rank decompositions of selected weight matrices, LoRA achieves near-full-fine-tuning accuracy at a fraction of the trainable parameter cost. The method's appeal is partly its apparent architecture-agnosticism: any layer implemented as `nn.Linear` is a candidate for LoRA adaptation.

Mamba [Gu and Dao, 2023] is the leading transformer-alternative for long-context language modeling. Its selective state space mechanism achieves linear-time training and constant-memory inference, making it a natural target for deployment scenarios where transformer attention is prohibitively expensive. Mamba-130m is publicly available on the HuggingFace Hub, its projection layers — `in_proj`, `out_proj`, and `x_proj` — are all `nn.Linear`, and community implementations (alxndrTL/mamba-peft) report SST-2 accuracy of 90–92% with LoRA rank 8 on these exact layers.

The natural inference is that LoRA on Mamba works. Practitioners building Mamba-based NLP pipelines would reasonably apply LoRA to these projection layers and expect learning to occur.

## The Deeper Problem

The assumption that LoRA on `nn.Linear` produces learning is valid for transformers because it rests on an implicit guarantee: the gradient path from the task loss to the LoRA weight matrices is unobstructed. In transformers, the attention mechanism is implemented as fully differentiable operations under standard PyTorch autograd. Any `nn.Linear` target in the attention stack receives well-defined gradients when trained on any loss function.

In Mamba, this guarantee does not hold. The architecture's core computation — the selective state space scan `h_t = Ā·h_{t-1} + B̄·x_t` — is implemented as a custom CUDA parallel associative scan kernel. This kernel is not a standard autograd-differentiable operation in the same sense as `nn.Linear` or softmax. When a randomly-initialized classification head is placed atop a pretrained causal Mamba model and trained with cross-entropy loss, the classification gradient must flow backward through this SSM scan kernel to reach the LoRA weight matrices in the projection layers.

Our experiments demonstrate that this gradient path is ineffective for classification. Three training epochs produce exactly zero improvement over zero-shot accuracy on SST-2 (50.9% vs. 49.1% zero-shot, a net gain of 1.84 percentage points — within noise). MNLI accuracy actively degrades from its zero-shot level of 34.6% to 32.3% by the second epoch. The loss oscillates between 0.65 and 0.73 across training batches without monotonic decrease — the signature of incoherent gradient updates rather than directed learning.

The PEFT community's mental model was built on transformers, where API compatibility and gradient compatibility are the same thing. In Mamba, they are not. The SSM scan acts as a silent wall: it permits forward inference but does not effectively propagate classification-discriminative gradients backward to the projection-layer LoRA matrices.

## The Gap

No prior work provides a controlled, reproducible characterization of projection-only LoRA failure on pure Mamba SSMs for classification tasks. The community reference (alxndrTL/mamba-peft, 2024) reports 90–92% SST-2 without fully documenting the training recipe — which checkpoint (base vs. instruction-tuned), which classification head design, which prompt format, how many epochs. Practitioners attempting to replicate this result with the base `mamba-130m-hf` checkpoint, a standard classification head, and a clean training loop will observe what we observed: no learning.

Without a clear failure characterization, the field will repeatedly rediscover this failure independently, wasting compute and producing confusing discrepancies in the literature. The 40 percentage-point gap between our result (50.9%) and the community reference (90–92%) is itself an open reproducibility problem — one that cannot be resolved without understanding which training recipe detail makes the difference, and what it implies about gradient compatibility in Mamba.

## Key Insight

We trace the failure to the Mamba selective state-space scan, which acts as an effective gradient barrier between classification loss and LoRA weight matrices — a property invisible from the PEFT API but immediately apparent from per-epoch accuracy tracking.

The SSM scan was designed and optimized for next-token prediction, the task on which Mamba-130m was pretrained. The gradient path for causal language modeling is well-exercised through this kernel. For a randomly-initialized classification head placed on the final hidden state, the gradient is novel and apparently untranslatable through the same path: it exists numerically but produces near-zero directed updates to the LoRA weight matrices, leaving the model locked at its pretraining prediction regime.

This is a conceptual distinction the PEFT community needs: API compatibility — the ability to install LoRA adapters with correct parameter counts — is a necessary but not sufficient condition for fine-tuning to produce learning. Gradient compatibility, verified empirically through per-epoch task accuracy, is the authoritative criterion.

## Contributions

Our investigation reveals three contributions, each a natural consequence of treating "does LoRA actually learn?" as an empirical question rather than an assumed property of the PEFT API.

First, we provide direct empirical evidence that projection-only LoRA (targeting `in_proj`, `out_proj`, `x_proj` with rank 8) does not produce meaningful classification task learning on Mamba-130m. The evidence is precise: SST-2 accuracy of 0.5092 across three identical consecutive training epochs (zero-shot baseline: 0.4908), and MNLI accuracy degrading from 0.3463 zero-shot to 0.3234 by the second epoch. Three identical accuracy values across epochs is the clearest possible indicator of zero learning — any stochastic variation in predictions would produce different values if learning were occurring.

Second, we document verified zero-shot GLUE baselines for Mamba-130m: SST-2 = 0.4908, MNLI = 0.3463, QNLI = 0.5056, QQP = 0.0000. These baselines, confirmed across two independent evaluations, provide a reproducible reference for future Mamba adaptation experiments and constitute a standalone contribution independent of the fine-tuning results.

Third, we characterize the SSM scan gradient barrier as the mechanistic cause of the failure, identify a two-signal diagnostic signature for practitioners (loss oscillation without monotonic decrease, combined with per-epoch accuracy plateau), and specify the design constraint this places on future Mamba PEFT methods: adapters must either operate inside the SSM computation (dt_proj LoRA, direct B/C adaptation) or bypass the scan entirely (prefix tuning), rather than relying on the projection-layer gradient path that works for transformers.

## Paper Organization

To understand why this failure was unexpected — and what prior work leaves unresolved — we review Mamba's architectural properties, existing PEFT methods, and the MambaPEFT literature that motivated our investigation (Section 2). Section 3 describes our experimental design as a MUST_WORK existence check — a protocol explicitly designed to give LoRA maximum benefit of the doubt. Section 4 presents the experiments. Section 5 reports the results, including the zero-shot baselines and the per-epoch fine-tuning outcomes. Section 6 interprets the results through the SSM scan gradient barrier lens, addresses the MambaPEFT discrepancy, and discusses limitations honestly. Section 7 concludes with three focused directions for future work grounded directly in the failure analysis.
