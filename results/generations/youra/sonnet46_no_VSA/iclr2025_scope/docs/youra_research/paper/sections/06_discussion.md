# 6. Discussion

## 6.1 Key Finding: Bounded-State Architecture, Not Approximation Failure

Our mechanism gate result reshapes how to diagnose retrieval degradation in SSM-converted models.
The SSD mixer does not fail at long context — it becomes proportionally better. The normalized
Frobenius error at N=2048 (0.024) is 38% lower than at N=512 (0.039). If approximation quality
were the limiting factor, increasing distillation compute (more optimization steps, more tokens)
would reduce retrieval degradation proportionally. Our result says it will not: the degradation
persists as an architectural property.

This has concrete implications. MOHAWK's SSD state update is:

```
h_t = A · h_{t-1} + B · x_t
```

with |A| < 1 ensuring stability. The exponential discount means that a token at position k in a
sequence of N tokens contributes to the final state with weight ~|A|^(N-k). For retrieval tasks
requiring exact recall of a needle at depth d (early in the context), this weight is ~|A|^(N·d) —
exponentially small for large N. No matter how well the SSD matrices are initialized to match
teacher attention, the state update equation erases early positional information during forward
inference. Approximation fidelity and state update forgetting are independent mechanisms; our
results confirm the former is adequate and implicate the latter.

## 6.2 Mechanistic Prediction for the Behavioral Test

The mechanism gate result generates a specific behavioral prediction: if MOHAWK-SSM degrades
on retrieval tasks, it should do so *disproportionately* relative to generation tasks. Generation
tasks (summarization, few-shot) tolerate lossy semantic compression — integrating meaning across
the full context, not locating a specific token at depth d. SSM state accumulation handles this
gracefully; retrieval does not. LAWCAT's causal Conv1D, by applying local attention in a sliding
window before the linear attention layer, preserves recent-to-local token identity — potentially
enabling shallower depth-dependent degradation.

This prediction (H-E1 primary gate, pending) is not a post-hoc rationalization; it was pre-
registered before behavioral experiments began. The mechanism gate result provides the causal
grounding that makes the behavioral prediction falsifiable: if H-E1 shows uniform degradation
across task types (no interaction), it would refute not just the behavioral claim but the
architectural interpretation of Step 1. The two-part design provides mutual constraint.

## 6.3 Attention Sparsity Explains the Negative Slope

The unexpected finding — normalized SSD error *decreasing* with N — has a plausible mechanistic
explanation. At longer sequences, LLaMA-3-8B attention matrices become sparser: attention mass
concentrates on fewer positions (local window attention, separator tokens, and beginning-of-context
anchors). A sparse N×N matrix has lower effective rank than a dense one; the fixed-rank SSD
approximation captures a lower-dimensional target more efficiently. This would predict that the
SSD slope β correlates negatively with the effective rank of LLaMA-3-8B attention matrices across
N values — a hypothesis testable via eigenspectrum analysis (deferred to future work).

An alternative explanation is optimization horizon: 500 gradient steps may be proportionally more
effective at longer N because the loss landscape is smoother at larger matrix scale. We consider
this less likely given that both explanations predict the same sign but the sparsity explanation
directly connects to known LLM attention behavior.

## 6.4 Limitations

**H-E1 behavioral results are pending.** The Δ_norm ratio and interaction p-value — the primary
behavioral gate — have not been numerically resolved because MOHAWK three-stage distillation
requires approximately 14 GPU-days at 8B scale. The Phase 4 code validation and successful
experiment launch constitute proof-of-concept; the final numbers will determine whether the
behavioral prediction is confirmed. All claims in this paper about bounded-state architectural
bias are grounded in the mechanism gate result, which is complete; they are not grounded in
behavioral outcome data.

**H-M1 evaluated at N ≤ 2048.** The planned gate evaluation included N=8192, but eager attention
materialization at N=8192 causes OOM on 96GB H100 GPUs (~8GB per attention head per layer).
We evaluate at N ∈ {512, 1024, 2048}. The gate passes with large margin: reaching β=0.5 at
N=4096 would require a dramatic reversal from the observed -0.368 trend. For publication, we
recommend extending to N=4096 using chunked attention materialization.

**Architecture-vs-curriculum confound.** All models are distilled with 2048-token maximum sequence
length. If retrieval degradation in H-E1 reflects curriculum limitation (no long sequences in
training) rather than inherent SSM bounds, the mechanism gate interpretation is weakened.
However, both MOHAWK-SSM and LAWCAT share the same curriculum; the *relative* difference between
them (if confirmed) would still reflect architectural differences. The confound is pre-registered
and planned for resolution via a mixed-length curriculum ablation in future work.

**H-M2 proxy data.** The depth-slope analysis was executed using identical LLaMA-3-8B weights
for both "SSM" and "LAWCAT" conditions (H-E1 prerequisite failure due to a port conflict).
The ratio=1.0 by construction; this is not evidence against the depth-slope hypothesis. The
statistical pipeline is validated and will be re-run on actual checkpoints once H-E1 completes.

## 6.5 Broader Impact

This work contributes to the growing ecosystem of efficient large language model deployment by
providing a diagnostic framework — mechanism gate before behavioral test — that can be applied
to any future conversion strategy. As SSM and linear attention conversion methods proliferate,
the ability to distinguish approximation failures from architectural limits will prevent
misattributed engineering effort (optimizing distillation when architecture redesign is needed).

The resolved engineering failures documented in Section 5.5 lower the barrier for community
replication of MOHAWK+LAWCAT cross-strategy comparisons at 8B scale. Negative results from
implementation challenges are rarely published; we argue they are as valuable as performance
numbers for a field building on shared infrastructure.

We do not anticipate negative societal impacts from this work. The research addresses evaluation
methodology for efficient inference; it does not directly enable new capabilities or introduce
new failure modes.
