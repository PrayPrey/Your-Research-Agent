# Discussion

## Interpretation

Our results support the hypothesis that transformer hidden states encode a *knowledge confidence* signal distinct from output-level token confidence. The probe's +26 AUROC point advantage over token entropy indicates that middle-layer representations capture information about factual accuracy that is compressed or lost by the time the model produces output probabilities.

The inverted-U layer pattern aligns with transformer interpretability findings: early layers process local features, middle layers build semantic representations, and late layers format output for next-token prediction. Correctness-relevant information peaks at ~50% depth—precisely where semantic content is richest but output formatting has not yet dominated.

**Mechanistic hypothesis.** We speculate that middle layers encode a "retrieval confidence" signal: the degree to which the model successfully retrieved relevant knowledge during the forward pass. This differs from "generation confidence" (output probability), which may be high even when retrieval failed but the model produces fluent text.

## Unexpected Findings

**Peak at 50%, not 60%.** Prior work (Aiersilan 2026) suggested 56% depth for hallucination signals. We find 50% optimal, though CIs overlap substantially. This may reflect model-specific variation (Llama-3 vs. prior architectures) or task-specific differences (correctness vs. hallucination detection).

**Early layers above 0.60.** We predicted L3 (12.5% depth) would achieve <0.60 AUROC, but observed 0.629. This suggests even early layers encode some correctness-relevant features—possibly lexical patterns correlated with answer types. However, the 0.63 → 0.85 jump to middle layers confirms the bulk of the correctness signal develops in semantic processing stages.

## Limitations

**Single model family.** We validate only on Llama-3-8B-Instruct. While this is representative of modern instruction-tuned LLMs, cross-architecture generalization (Mistral, Qwen, GPT) remains untested. Layer depth percentages may not transfer directly; architectural differences could shift the optimal extraction point.

**Exact-match labeling.** Our correctness labels come from exact string match with reference answers. Semantically correct answers with different phrasing are labeled incorrect. This may cause the probe to partially learn format matching rather than pure factual accuracy. Future work could use F1 overlap or human evaluation for softer labels.

**English QA only.** All experiments use English datasets. Cross-lingual generalization is unknown—multilingual models may exhibit different layer-wise dynamics.

**Untested predictions.** We validated P1 (middle-layer peak) and P3 (probe >> entropy) but left P4 (semantic entropy parity), P5 (confident-but-wrong detection), and P6 (TruthfulQA transfer) for future work.

## Broader Impact

**Practical deployment.** Our method enables efficient correctness estimation: a single forward pass plus lightweight probe inference. This could support real-time flagging of potentially incorrect responses, calibrated confidence displays, or routing uncertain queries to human reviewers.

**Limitations of deployment.** A probe trained on TriviaQA may not generalize to other domains (medical, legal, technical). Deployment requires domain-specific validation. Additionally, correctness detection should complement—not replace—retrieval-augmented generation and source citation practices.
