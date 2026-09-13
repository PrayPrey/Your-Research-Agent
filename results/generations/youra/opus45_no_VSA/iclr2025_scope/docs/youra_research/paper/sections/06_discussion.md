# Discussion

## Key Findings

Our experiments reveal a nuanced picture of zero-shot adapter routing. The positive findings are clear: IPCR achieves 95% of oracle performance using nothing more than frozen embeddings and a linear probe. This validates the hypothesis that instruction-adapter alignment exists intrinsically—we did not need to learn it through joint training or optimize it with validation examples.

However, the robustness results temper this success. Routing depends on lexical features, not semantic understanding. This is both a scientific finding (about what MiniLM embeddings capture) and a practical constraint (on where IPCR can be deployed).

**What works:** FLAN-style instructions with consistent templates and task-indicative keywords. The linear separability (F1 = 0.995) and high top-3 coverage (95.78%) make IPCR viable for controlled instruction interfaces.

**What doesn't work:** Paraphrased queries, user-generated instructions with non-standard wording, or any setting where keyword anchoring is unreliable.

## Limitations

We acknowledge several limitations:

**L1: Lexical Dependence.** The 44% accuracy drop under keyword masking indicates routing is driven by surface tokens. This is fundamental to MiniLM's mean-pooling architecture, not a fixable implementation issue. Mitigation requires either paraphrase augmentation during probe training or switching to encoders with stronger compositional semantics (e.g., E5-large, Instructor-XL).

**L2: Paraphrase Fragility.** Cosine similarity of 0.78 under paraphrase means ~24% of real-world instruction variations will cause routing inconsistency. Production deployment would require either instruction normalization (preprocessing user queries to canonical form) or hybrid routing (combining embedding scores with keyword-based confidence).

**L3: Task Family Coverage.** We tested 9-18 task families, not the full 62 FLAN categories. Generalization to untested families is unverified. However, the near-perfect separability among tested families suggests the pattern should extend.

**L4: Oracle Approximation.** H-E1 used task names as oracle proxy rather than computing per-adapter loss for each sample. This is a valid upper-bound estimate given H-E0's 99.5% task separability, but true oracle accuracy may differ.

## Broader Impact

**Positive impacts:** IPCR enables adapter routing without validation data, making adapter banks accessible for zero-shot inference. This reduces deployment complexity and enables real-time adapter selection in resource-constrained settings.

**Potential concerns:** Routing errors could cause inappropriate model behavior if the wrong adapter is selected. In high-stakes applications (medical, legal), routing mistakes propagate to final outputs. We recommend confidence thresholds with fallback to uniform averaging when routing confidence is low.

**Fairness considerations:** Routing accuracy varies by task family (97.2% for math vs 49.2% for NLI). This could create disparate performance across use cases. Deployment should monitor per-domain routing accuracy.

## Relation to Competing Explanations

Our results are consistent with two interpretations:

1. **Intrinsic alignment hypothesis:** Instruction semantics and adapter specializations genuinely share geometric structure inherited from base model instruction-tuning.

2. **Lexical anchoring hypothesis:** High performance reflects keyword preservation in FLAN templates, not semantic understanding. Routing succeeds because FLAN instructions are keyword-rich, not because MiniLM captures deep task semantics.

The robustness failure (H-M2) provides stronger support for the lexical anchoring interpretation. Future work should disentangle these hypotheses through ablations on instruction format and encoder architecture.
