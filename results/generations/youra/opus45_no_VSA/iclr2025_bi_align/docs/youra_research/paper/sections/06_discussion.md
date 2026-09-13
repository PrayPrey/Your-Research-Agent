# Discussion

## Independence Without Meaning

Our central finding is a productive tension: BAI is extractable and representationally independent, but semantically incoherent. This combination has important implications for bidirectional alignment research.

The strong performance on H-E1 and H-M1 demonstrates that preference data contains variance orthogonal to reward prediction. This variance survives aggressive adversarial suppression of reward-predictive information, confirming it occupies a genuinely independent representational subspace. The methodology is sound; gradient reversal successfully isolates BAI from reward.

However, H-C1's failure reveals that this orthogonal variance does not correspond to interpretable agency-preserving content. The disagreement slice clusters by generic conversational patterns — stopwords, politeness markers, greeting phrases — rather than agency vocabulary. Figure \ref{fig:umap_projection} visualizes this clustering, and Figure \ref{fig:topic_wordclouds} shows the dominant keywords.

The implication is clear: surface-level linguistic proxies capture syntax, not semantics. A response can match our regex patterns for clarifying questions or hedging markers without actually functioning to preserve user agency. The proxies detect grammatical structures, not communicative intent.

## Why Semantic Coherence Failed

Several factors may explain the disconnect between extractability and meaning.

**Proxy Detector Sensitivity.** Our regex-based detectors have low positive rates (0.12% – 11.66%), meaning most responses score near zero on all proxies. This floor effect compresses BAI variance (σ² = 0.0022), limiting the signal available for semantic analysis. More sensitive detectors — embedding-based classifiers or LLM-as-judge evaluations — might surface richer agency patterns.

**Dataset Artifacts.** HH-RLHF contains known quality issues including length biases and annotator disagreement patterns. The high-BAI/low-reward slice may reflect dataset-specific artifacts rather than genuine agency-reward orthogonality. The dominance of the HL quadrant (3,063) over LH (1,869) suggests responses with politeness markers receive lower reward scores — potentially a safety-helpfulness tradeoff artifact rather than agency preservation.

**Surface-to-Function Gap.** The HumanAgencyBench framework assumes surface behaviors (clarifying, hedging) correlate with functional agency preservation. Our results challenge this assumption. A response containing "Are you asking whether..." may be clarifying for clarification's sake or may be filler text; regex cannot distinguish. True agency preservation may require understanding communicative intent, which pattern matching cannot capture.

## Limitations

**Synthetic Data.** H-M1 used synthetic hidden states with planted structure rather than real LLM activations. While this validates the methodology, generalization to actual Llama-3-8B or other model hidden states remains to be confirmed. We chose this approach due to GPU memory constraints; real-model validation is straightforward follow-up work.

**Single Model Architecture.** All experiments used 4096-dimensional representations (Llama-3-8B equivalent). Other architectures (Mistral, Qwen) may behave differently. Cross-model validation would strengthen generalizability claims.

**Domain Scope.** Our analysis focused on advisory and safety-related prompts where agency preservation is conceptually most relevant. Results may not generalize to factual QA or multi-turn conversations where different dynamics apply.

**Proxy Design.** We tested only four proxies adapted from HumanAgencyBench. Other dimensions — supporting user reasoning, avoiding cognitive shortcuts — were not operationalized. A broader proxy set might capture richer agency signals.

## Implications for Bidirectional Alignment

Our negative result provides constructive guidance. Future operationalizations of Human→AI alignment should:

1. **Move beyond pattern matching.** Embedding-based classifiers or LLM-as-judge evaluations can distinguish communicative intent, not just grammatical structure.

2. **Validate semantics before claiming construct validity.** Extraction reliability (H-E1) and representational independence (H-M1) are necessary but not sufficient. Semantic coherence testing (H-C1) should be standard practice.

3. **Stratify by domain.** Different prompt types may require different operationalizations. Advisory prompts differ from factual QA in what agency preservation means.

4. **Collect ground-truth agency labels.** Human annotation of 500+ responses for functional agency preservation would enable supervised learning and proper validation of any operationalization.

The Bidirectional Alignment Framework remains conceptually compelling. Our work shows that naive operationalization does not suffice — but it also demonstrates the methodology for rigorous testing. Adversarial probing can validate independence claims; semantic clustering can test meaning claims. Future work should apply these tools to richer operationalizations.
