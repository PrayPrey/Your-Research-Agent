# 1. Introduction

Current RLHF evaluation benchmarks measure preference agreement — how often humans prefer the aligned model's outputs — but ignore preference diversity. High agreement could indicate successful alignment (users genuinely prefer higher-quality responses) or problematic homogenization (users habituate to model style and lose critical evaluation capacity). Existing methods optimize for unidirectional alignment (does AI align to humans?) without measuring bidirectional alignment (do humans preserve agency when interacting with aligned AI?).

We propose preference entropy as an information-theoretic proxy for this bidirectional alignment gap. Shannon entropy H = -Σ p_i log(p_i) measures the diversity of human preference distributions: high entropy indicates diverse judgments (preserved critical evaluation), while low entropy indicates convergence (potential homogenization). Unlike self-reported user agency metrics that require dedicated surveys, preference entropy can be computed from existing RLHF benchmark data — if the data structure supports it.

Our validation reveals a critical methodological gap: standard RLHF datasets (Anthropic-HH, used in Constitutional AI) use pairwise comparison formats optimized for annotation cost, structurally incompatible with per-prompt entropy measurement. Each example in Anthropic-HH compares different response candidates (A1 vs B1, A2 vs B2, ...), preventing aggregation into preference distributions over fixed response sets. This format enables efficient reward model training but fundamentally cannot measure diversity — not a missing analysis, but a data structure limitation.

**Contributions:**

1. **Bidirectional Alignment Framework:** First application of information-theoretic entropy to measure RLHF impact on human preference diversity (not just AI→human agreement). Introduces "preference entropy" as lightweight proxy for collective critical evaluation capacity.

2. **Dataset Structure Taxonomy:** Identify critical distinction between pairwise-unique formats (Anthropic-HH: cost-efficient, entropy-incompatible) and multi-annotator-fixed formats (OpenAI Summarization: entropy-measurable, higher cost). Guides future benchmark design for diversity-aware evaluation.

3. **Methodological Validation:** Demonstrate entropy computation is technically feasible (100% success rate on Anthropic-HH) but yields constant value ln(2) ≈ 0.693 nats (zero variance) due to dataset format, not implementation issues. Root cause analysis confirms structural incompatibility.

4. **Alternative Measurement Proxies:** Propose three alternatives when multi-annotator data unavailable: (a) response diversity entropy (model outputs), (b) intra-annotator variance (longitudinal data), (c) entropy-regularized RLHF (algorithm modification).

**Key Finding:** Standard RLHF benchmarks (Anthropic-HH, WebGPT) cannot measure preference diversity even if desired. Dataset format optimizes one objective (annotation cost) at expense of another (diversity measurability). Future benchmarks must explicitly choose: train reward models efficiently (pairwise) OR evaluate bidirectional alignment (multi-annotator).

**Organization:** Section 2 reviews RLHF evaluation methods and bidirectional alignment gaps. Section 3 presents our entropy-based methodology and dataset structure taxonomy. Section 4 describes the H-E1 validation experiment. Section 5 reports findings (constant entropy, root cause analysis). Section 6 discusses implications for benchmark design and proposes alternative proxies. Section 7 concludes with future work.

