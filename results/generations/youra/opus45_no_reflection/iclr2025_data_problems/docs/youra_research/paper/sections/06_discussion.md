# Discussion

## Key Findings

Our experiments reveal that transformer attention structure creates measurable but method-dependent effects on data attribution performance.

**TRAK's Architecture-Invariance.** The most striking finding is TRAK's remarkable consistency across architectures (<1% AUC difference at all compute budgets). This confirms that random projection effectively averages out architecture-specific gradient patterns. For practitioners working with diverse model architectures, TRAK provides a robust default that doesn't require architecture-specific tuning or method selection.

**TracIn's Encoder Preference.** TracIn's consistent BERT advantage (~3% at low compute) aligns with the hypothesis that gradient dot-products benefit from dense bidirectional gradients. In encoder-only pipelines, TracIn may offer advantages worth exploiting.

**EK-FAC's Unexpected Robustness.** The absence of EK-FAC's predicted GPT-2 advantage is surprising. Prior theoretical analysis suggested Kronecker factorization fits causal attention structure better (Grosse et al., 2023). Our results indicate this advantage either doesn't manifest at the 100M parameter scale, doesn't apply to mislabeled detection, or was overestimated in prior analysis.

## Mechanistic Interpretation

We validated the causal chain from attention structure to attribution performance:

1. **Attention sparsity** differs by 98.8% (BERT: 1.2%, GPT-2: 100%)
2. **Hessian curvature** shows 11× eigenvalue difference (GPT-2: 0.502, BERT: 0.046)
3. **Attribution methods** respond differently to these structural differences

The mechanism explains TracIn's behavior: bidirectional attention creates denser gradient flow, providing more information for gradient dot-products to capture. TRAK's random projection is architecture-agnostic by design—it treats gradients as unstructured vectors. EK-FAC's Kronecker structure doesn't exploit the causal attention pattern as strongly as predicted.

## Practical Implications

For practitioners choosing attribution methods:

| Use Case | Recommended Method | Rationale |
|----------|-------------------|-----------|
| Cross-architecture pipelines | TRAK | <1% variation guarantees consistency |
| Encoder-only (BERT) work | TracIn or TRAK | TracIn may offer ~3% advantage |
| Decoder-only (GPT-2) work | TRAK or EK-FAC | Both perform equivalently |
| Unknown/variable architectures | TRAK | Architecture-agnostic |

## Limitations

### Statistical Power

Our 2-seed experiments provide directional evidence but cannot achieve p<0.05 significance for moderate effect sizes. P1 (EK-FAC) and P2 (TracIn) predictions are characterized as "directionally supported" rather than statistically confirmed. Future work should use 5+ seeds for adequate power.

### Single Dataset

All experiments use SST-2 sentiment classification. Results may not generalize to:
- Other task types (NER, QA, summarization)
- Different domains (medical, legal, scientific)
- Higher noise rates (>5%)

The methodology is designed for replication on other benchmarks.

### Model Scale

We tested ~110-125M parameter models. Effects may differ at larger scales (1B+). The 11× Hessian eigenvalue difference could amplify or attenuate at scale. EK-FAC's predicted decoder advantage might emerge only at the 10B+ scale where Grosse et al. (2023) conducted their analysis.

### Architectural Scope

We compare encoder-only (BERT) vs decoder-only (GPT-2). Missing from analysis:
- Encoder-decoder (T5, BART)
- Sparse attention variants
- Flash attention implementations
- Instruction-tuned or RLHF models

## Comparison with Prior Work

Our results are consistent with but extend prior findings:

- **Park et al. (2023)**: Reported TRAK works well on BERT; we confirm this extends to GPT-2 with <1% difference
- **Grosse et al. (2023)**: Reported EK-FAC works well on decoder-only LLMs; we confirm this but find no encoder disadvantage
- **Pruthi et al. (2020)**: Reported TracIn on various models; we quantify its encoder preference

The novel contribution is the matched comparison revealing architecture-method interactions invisible in single-architecture evaluations.

## Broader Impact

This work provides actionable guidance for responsible AI development. Data attribution enables:
- **Model debugging**: Identifying training examples causing errors
- **Data quality**: Detecting mislabeled or harmful training data
- **Audit and compliance**: Tracing model behavior to training sources

By clarifying which methods work best across architectures, we lower barriers to applying these techniques in production ML systems.
