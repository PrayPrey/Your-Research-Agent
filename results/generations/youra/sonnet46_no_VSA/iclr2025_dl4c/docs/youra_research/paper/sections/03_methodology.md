## 3. Methodology

### 3.1 Conceptual Framework

Our hypothesis is that SFT training source identity — which dataset the training problems
come from — is the dominant causal factor governing post-SFT code benchmark performance.
The causal chain has three steps:

**Step 1:** Different code sources (HumanEval training problems, MBPP utility scripts,
LeetCode competitive programming) define distinct distributions in embedding space.
If sources are indistinguishable, the mechanism is untestable.

**Step 2:** SFT gradient updates bias model weights toward the training distribution.
A model trained on HumanEval-style problems should develop representational patterns
aligned with HumanEval+; a model trained on LeetCode problems should develop patterns
aligned with LeetCode's competitive programming style.

**Step 3:** The resulting performance on benchmark B is higher when the training
distribution is closer to the test distribution of B in embedding space.

The key design insight is that **token-budget equalization** is essential to isolate
Step 1–3 causally. Without equalizing the total training tokens across source conditions,
observed performance differences could reflect data quantity rather than source identity.
With equalization, source identity is the sole experimental variable.

### 3.2 Experimental Design

We compare four SFT training source conditions on DeepSeek-Coder-Base [Guo et al., 2024]:

| Condition | Dataset | Problems | Description |
|-----------|---------|----------|-------------|
| HumanEval-only | openai/humaneval (train split) | 164 | Function completion with doctests |
| MBPP-only | google-research-datasets/mbpp (sanitized) | 120 | Utility scripts with I/O examples |
| LeetCode-only | newfacade/LeetCodeDataset | subsampled | Competitive programming problems |
| Equal-mix | Equal proportions from all three | — | Structural falsifier for diversity |

**Why these four conditions:** The first three isolate different Python problem styles;
the Equal-mix condition tests whether diversity beats alignment. If Equal-mix dominates,
diversity-over-alignment is the publishable null result. If single-source conditions
dominate, alignment governs — which is what we find.

### 3.3 Token-Budget Equalization

**Rationale:** Without this, a condition with more unique problems or more epochs would
confound source identity with data quantity. We equalize by matching total training tokens
across all conditions through unique-problem count × repetition rate balancing.

All four conditions receive the same effective token budget. HumanEval-only (164 problems)
uses more epochs to match token count; LeetCode-only subsamples from a larger pool.

### 3.4 Deduplication Protocol

**Rationale:** Near-duplicate contamination inflates benchmark scores regardless of source
identity. We apply the validated deduplication pipeline: all-MiniLM-L6-v2 encoder, cosine
similarity threshold > 0.95, against both HumanEval+ (164 test problems) and MBPP+ (374
test problems). Any training problem with cosine similarity > 0.95 to a test problem is
removed before training set construction.

This ensures that pass@1 differences reflect generalization rather than memorization.

### 3.5 Supervision Format Normalization

**Rationale:** HumanEval problems naturally use docstrings; MBPP problems include I/O
examples in prompts. Without format normalization, pass@1 differences could reflect
prompt style rather than source identity. We apply a standardized instruction template
across all sources:

```
[INSTRUCTION]
Complete the following Python function.

[CODE]
{problem_prompt}
```

All conditions use the same template, eliminating format as a confounding variable.

### 3.6 Distributional Alignment Measurement

We measure embedding-space similarity between each training source and each test benchmark
using two complementary encoders:

- **CodeBERT** (`microsoft/codebert-base`): code-pretrained encoder capturing programming
  syntax and semantics
- **all-MiniLM-L6-v2**: sentence-level encoder capturing problem description style

For each (source, benchmark) pair, we compute the mean pairwise cosine similarity between
all training source embeddings and all test benchmark embeddings. The result is a 4×2
similarity matrix per encoder, which we use to rank conditions by alignment.

Figure 1 shows both similarity matrices. MiniLM shows clearer distributional separation
(range 0.247–0.311) than CodeBERT (range 0.909–0.975), reflecting that problem description
style diverges more than code-level syntax across sources.

![Figure 1: Dual-encoder similarity matrices](figures/similarity_heatmaps.png)
*Figure 1: CodeBERT (left) and MiniLM (right) cosine similarity between training sources
and test benchmarks. Both encoders confirm distinct distributions; MiniLM shows stronger
separation.*

### 3.7 Mechanistic Alignment Test (P3)

To test whether embedding alignment predicts performance rank, we compute Spearman ρ
between the embedding similarity rank of each condition to HumanEval+ and the pass@1 rank
of each condition on HumanEval+.

Statistical significance is assessed via permutation test: we randomly shuffle source-condition
labels 10,000 times, recompute ρ each time, and report the fraction of shuffles achieving ρ
≥ the observed ρ as the p-value. This is a one-sided test (alternative: greater), appropriate
for our directional hypothesis that higher alignment predicts higher performance.

With n=4 conditions, the permutation distribution has 4!=24 possible orderings; the minimum
achievable p-value is 1/24 ≈ 0.042. We therefore require both statistical significance and
dual-encoder concordance (both CodeBERT and MiniLM showing ρ > 0) for mechanistic validation.

### 3.8 Scale Comparison (1.3B vs 7B)

We replicate the four-condition experiment at 7B scale (DeepSeek-Coder-7B-Base) using
DeepSpeed ZeRO-3 across 4 GPUs. This probes whether source identity effects are robust
across model sizes. We report both absolute condition spread (max mean − min mean pass@1)
and η² (between-condition variance ratio) as complementary metrics, with the rationale
that η² can be inflated when within-condition seed variance collapses at larger scale.

### 3.9 Training Configuration

**1.3B scale:**
- Base model: `deepseek-ai/deepseek-coder-1.3b-base`
- Optimizer: AdamW, learning rate 2.0e-5
- Batch size: 4 per device, gradient accumulation 4 (effective 16)
- Scheduler: cosine with 5% warmup
- Precision: bfloat16, completion-only loss
- Seeds: 42, 123, 777 (3 independent training runs per condition)

**7B scale:**
- Base model: `deepseek-ai/deepseek-coder-7b-base`
- 4 GPUs, DeepSpeed ZeRO-3
- Learning rate: 2.0e-5, 3 epochs, batch size 4 (accumulation 8, effective 32)

**Evaluation:** EvalPlus harness [CITATION NEEDED: evalplus], greedy decoding (temperature=0),
HumanEval+ (164 problems) and MBPP+ (374 problems).
