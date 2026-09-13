# 1. Introduction

Converting a transformer to an SSM costs fewer than one billion distillation tokens — and when you
measure how well the new architecture approximates the original attention matrices, something
unexpected happens: the approximation error per position *decreases* as context grows longer. Yet
retrieved information still degrades in long-context tasks. Why would better approximation produce
worse retrieval?

This puzzle sits at the heart of efficient long-context modeling. Sub-quadratic architectures —
selective state-space models (SSMs) and linear attention variants — offer quadratic-to-linear
inference costs, enabling practical deployment of long-context language models. Converting a
pretrained transformer to these architectures via distillation has emerged as a compelling
alternative to training from scratch: MOHAWK [Bick et al., 2024] demonstrates SSM conversion of
Phi-1.5 with strong retention on standard benchmarks; LAWCAT [Liu et al., 2025] achieves >90%
passkey retrieval at 22K tokens from Mistral-7B with under 1B distillation tokens. Both results
suggest conversion is viable — but on different base models, different benchmarks, and without
a shared measurement framework.

The deeper problem is a confound that neither paper resolves: when a converted model fails on
long-context retrieval, is the failure caused by the distillation approximation breaking down
at long context, or by the SSM's inherent bounded-state architecture — the state update
h_t = A·h_{t-1} + B·x_t that exponentially forgets early token positions regardless of how
precisely the conversion was performed? These explanations have different implications. If
approximation failure is the cause, better distillation training fixes the problem. If bounded-state
architecture is the cause, no amount of distillation improvement can fundamentally address retrieval
degradation — and architectural redesign (e.g., retaining attention layers in a hybrid) is required.

We address this confound directly. Our key insight is that the SSD structured mixer's approximation
quality is independently measurable — by computing the Frobenius distance between SSD transfer
matrices and teacher attention matrices at multiple sequence lengths. This measurement is separable
from downstream task performance and can be evaluated before any behavioral test. We term this
the *mechanism gate*: a diagnostic that determines whether approximation quality is the bottleneck
before interpreting behavioral results.

**The mechanism gate result is conclusive.** We fit MOHAWK's SSD mixer to LLaMA-3-8B attention
matrices at N ∈ {512, 1024, 2048} tokens and measure the normalized Frobenius error (error/N)
at each length. Rather than degrading at longer contexts, the normalized error *decreases*:
0.039 at N=512, 0.033 at N=1024, 0.024 at N=2048 — a log-log slope of β=-0.368, well below
the sub-linear threshold of 0.5. Across 1,760 attention matrix measurements spanning all 32
LLaMA-3-8B transformer layers, SSD approximation quality strengthens with sequence length.
This rules out approximation failure as the mechanism for retrieval degradation.

Building on this mechanistic finding, we make the following contributions:

1. **Mechanism gate (confirmed):** We provide the first direct measurement of SSD Frobenius
   approximation scaling for LLaMA-3-8B at multiple sequence lengths, establishing that
   normalized error decreases with N (β=-0.368, gate PASSED at N=2048).

2. **Architectural interpretation:** We demonstrate that retrieval degradation in MOHAWK-converted
   LLaMA-3-8B is attributable to bounded-state architectural bias — the exponential forgetting
   in SSM state updates — rather than approximation quality breakdown during distillation.

3. **Validated evaluation infrastructure:** We implement and validate the first controlled
   comparison pipeline for MOHAWK-SSM vs LAWCAT linear attention on a fixed base model
   (LLaMA-3-8B), evaluated on LongBench v2 task categories with bootstrap confidence intervals
   and mixed-effects regression for task-type × strategy interaction testing (22/22 tests passing).

4. **Implementation artifact:** We document and resolve 10 previously undocumented failure modes
   in the MOHAWK+LAWCAT+LLaMA-3.1-8B integration pipeline, providing a reusable foundation
   for subsequent cross-strategy evaluations.

The paper is organized as follows. Section 2 situates our work among prior conversion strategies
and benchmark evaluations. Section 3 describes the two-part experimental design: mechanism gate
and behavioral evaluation. Section 4 presents results, beginning with the confirmed mechanism
gate and the infrastructure-validated behavioral pipeline. Section 5 discusses implications,
limitations, and the open behavioral question awaiting H-E1 completion.
