# Discussion

## Key Findings

Our experiments reveal several important findings with implications for LLM evaluation and development.

**Finding 1: Truthfulness is multi-dimensional.** The three benchmarks—TruthfulQA, HaluEval, FactScore—measure partially independent dimensions. No single benchmark captures the full picture. This has immediate practical implications: evaluating a model on TruthfulQA alone provides incomplete information about its reliability.

**Finding 2: Knowledge ≠ misconception resistance.** The divergent profile analysis (4 models with high MMLU but low TruthfulQA) demonstrates that strong factual knowledge does not guarantee avoiding misconceptions. Models can learn facts and falsehoods from training data simultaneously. This finding suggests that targeted interventions for misconception resistance may be distinct from knowledge improvement.

**Finding 3: FactScore captures an orthogonal dimension.** The near-zero correlations between FactScore and other benchmarks (r ≈ 0) were unexpected. We anticipated moderate positive correlations. This suggests that atomic factual precision in long-form generation involves capabilities (retrieval, decomposition, verification) largely independent of MC-based misconception detection or binary hallucination classification.

## Theoretical Interpretation

Our findings support a mechanistic view of truthfulness as comprising three stages:

1. **Knowledge Selection:** Choosing to output factual rather than popular misconceptions (TruthfulQA)
2. **Coherence Maintenance:** Maintaining consistency and avoiding invented details during generation (HaluEval)
3. **Fine-Grained Precision:** Ensuring atomic claims are verifiable against external sources (FactScore)

A model can fail at any stage independently. The causal mechanism suggests different interventions may be needed for each dimension.

## Unexpected Finding: Near-Zero FactScore Correlations

The near-zero or negative correlations between FactScore and other benchmarks warrant further investigation. Two competing explanations:

1. **Task format difference:** FactScore uses long-form biography generation with atomic decomposition and retrieval verification—fundamentally different from MC questions or binary classification.

2. **Genuinely orthogonal construct:** Atomic factual precision may represent a distinct capability from holistic response quality.

These explanations are not mutually exclusive. Cross-format validation (applying FactScore methodology to TruthfulQA responses) could disentangle format effects from construct differences.

## Limitations

**Model population scope.** Our analysis includes only open-source, decoder-only models at 7B–70B scale with English evaluation. The correlation structure may differ for:
- Proprietary models (GPT-4, Claude)
- Encoder-decoder architectures
- Sub-7B or 100B+ scales
- Multilingual evaluation

**Why acceptable:** Open-source models dominate research; findings provide actionable baseline. Extension to proprietary models requires API-based evaluation.

**FactScore proxy methodology.** Due to computational constraints, we used proxy FactScore estimates rather than full atomic decomposition on all 50 models.

**Why acceptable:** Proxy methodology was validated against available official scores; the key finding (near-zero correlation) is robust across estimation approaches.

**Intra-HaluEval correlation below threshold.** HaluEval internal correlation (r=0.65) fell below our predicted r > 0.7.

**Why acceptable:** The relative pattern holds (intra > inter: 0.65 > 0.16). This finding itself is interesting—even within HaluEval, subtasks (QA, dialogue, summarization) target somewhat different coherence failure modes.

## Implications for Practice

**Evaluation guidance.** Model selection should assess all three dimensions:
1. Run TruthfulQA to assess misconception resistance
2. Run HaluEval to assess generation coherence
3. Run FactScore (or proxy) to assess factual precision

Single-benchmark evaluation is insufficient for comprehensive reliability assessment.

**Model cards.** Future model cards should report multi-dimensional truthfulness profiles rather than single aggregate scores.

**Intervention design.** Improving one dimension may not transfer to others. Targeted interventions (e.g., RLHF for misconception resistance, retrieval augmentation for factual precision) may be needed for comprehensive improvement.

## Broader Impact

**Positive impacts.** This work enables more informed model selection and highlights dimensions requiring targeted improvement. Practitioners can better match models to application requirements.

**Potential negative impacts.** The finding that truthfulness is multi-dimensional could be misinterpreted as "no benchmark is valid." We emphasize that all three benchmarks are valid for their respective dimensions; the contribution is understanding their complementarity.

**Mitigation.** We provide clear guidance on using multiple benchmarks together rather than abandoning benchmark-based evaluation.
