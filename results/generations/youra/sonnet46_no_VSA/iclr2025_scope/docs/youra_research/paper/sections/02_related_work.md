# 2. Related Work

## 2.1 Sub-Quadratic Architecture Conversion

**MOHAWK [Bick et al., NeurIPS 2024]** establishes a three-stage distillation pipeline (matrix
alignment → hidden-state alignment → logit distillation) for converting transformers to SSMs
with SSD structured mixers. Phi-Mamba (Phi-1.5 → Mamba) achieves competitive performance on
lm-eval standard benchmarks (Winogrande, ARC, HellaSwag) with 3B distillation tokens. MOHAWK
reports SSD Frobenius approximation error ≈0.097 at N=64/512, establishing a baseline for
mechanism-level evaluation. However, MOHAWK evaluates on short-context tasks only and does not
report LongBench v2 task-category breakdowns. Critically, MOHAWK uses Phi-1.5 (1.3B) rather
than a production-scale model, preventing direct comparison with LAWCAT.

**LAWCAT [Liu et al., EMNLP 2025]** converts Mistral-7B to linear attention using a depth-separable
Conv1D layer and normalized gated linear attention, achieving >90% passkey retrieval at 22K tokens
with under 1B distillation tokens. LAWCAT demonstrates that linear attention conversion can
preserve retrieval on synthetic tasks (S-NIAH, BABILong). However, LAWCAT evaluates only on
synthetic needle-in-a-haystack benchmarks and does not compare against SSM conversion strategies.
The different base model (Mistral-7B vs Phi-1.5 for MOHAWK) prevents any cross-strategy
comparison from existing papers.

**Our work** addresses this gap by fixing the base model (LLaMA-3-8B) across both conversion
strategies. This eliminates the capability confound that dominates cross-family comparisons —
a 20+ percentage point accuracy difference between Phi-1.5 and Mistral-7B on LongBench v2 would
mask any conversion effect. Holding the base model constant enables a pure within-subject
measurement of conversion strategy effects.

## 2.2 Long-Context Evaluation of Recurrent Models

**Overflow Prevention [arXiv:2505.07793]** evaluates scratch-trained SSMs (Falcon3-Mamba-7B,
RecurrentGemma-9B, RWKV6-7B) on LongBench v2 with chunk-based inference, finding that recurrent
models are competitive on most categories but exhibit systematic degradation on multi-document QA
and synthetic retrieval. This work provides the most directly relevant empirical baseline for
SSM retrieval limits — and motivates our mechanism gate, since scratch-trained SSMs and
converted SSMs may exhibit different failure modes.

**LongBench v2 [Bai et al., ACL 2025]** provides the evaluation framework we adopt: 503 questions
across 6 task categories (single-document QA, multi-document QA, summarization, few-shot,
synthetic, code) at 8K–2M context lengths. The category structure enables the task-type interaction
test central to our behavioral hypothesis.

**SSM Theoretical Limits** are characterized by [arXiv:2507.00449], which proves SSMs cannot
solve multi-query joint recall in sub-quadratic time. This theoretical result provides a principled
ground for expecting SSM retrieval degradation — and motivates our focus on the mechanism
(bounded-state vs approximation failure) rather than just the behavioral outcome.

## 2.3 Hybrid SSM-Transformer Architectures

**Falcon-H1 [arXiv:2507.22448]** and **Apriel-H1 [arXiv:2511.02651]** demonstrate that
retaining a small fraction of standard attention layers in an otherwise-SSM architecture
substantially recovers long-context task performance. MOHAWK's Hybrid-4 variant (retaining 4
middle attention layers) achieves 66.0 vs 67.2 teacher average on lm-eval tasks, approaching
full recovery. These results motivate our Hybrid-4 control condition, which tests whether
4 attention layers are sufficient to restore the retrieval behavior that SSM bounded-state
forgetting would otherwise eliminate.

## 2.4 Our Position

Prior work evaluates conversion strategies and recurrent architectures in isolation, on different
base models, and with different benchmarks. No prior study:
(a) compares MOHAWK-SSM and LAWCAT on the same base model and benchmark,
(b) separately measures the SSD approximation mechanism before interpreting behavioral results, or
(c) uses a mixed-effects task-type × strategy interaction test on LongBench v2 for converted models.

Our work provides all three, establishing the mechanism-separated framework needed to correctly
attribute retrieval degradation in converted models.
