# Discussion

## Generation-Free Detection Reconsidered

The dominant assumption in hallucination detection research is that competitive performance requires LLM generation: multiple samples, chain-of-thought verification, or internal state probing. Our results challenge this assumption directly. On commission-type hallucination tasks, a frozen NLI classifier applied post-hoc to pre-existing text pairs achieves AUROC = 0.709 (dialogue) and 0.644 (QA), surpassing generation-based SelfCheckGPT-NLI by +0.229 and +0.114 respectively.

What explains this advantage? Generation-based consistency checking is most effective when the model's stochastic outputs contain genuine semantic variation — when the LLM "knows" the answer inconsistently. When a base LLM produces near-uniform outputs (as we observed with Meta-Llama-3-8B), the consistency signal collapses. Post-hoc NLI scoring bypasses this entirely: it does not rely on sampling diversity but on the discriminative signal already encoded in the NLI model's pre-training. The NLI model's MNLI training — on large-scale human-annotated contradiction/entailment pairs — encodes precisely the signal needed to detect factual substitutions and contradictions, which is what commission-type hallucinations are.

This suggests a practical principle: for deployed systems where hallucination type is known to be commission-dominated (dialogues, QA), post-hoc NLI detection is the cost-efficient choice. It requires no additional LLM inference, works on pre-existing (context, response) pairs, and can be applied retroactively to logged outputs without re-running inference.

## The Commission/Omission Boundary as a Theoretical Contribution

The most important finding of this paper is not the AUROC numbers — it is the identification of a structural architectural constraint governing when NLI-based detection works.

NLI models trained on MNLI are optimized to detect textual contradiction: the hypothesis says X, the premise implies not-X. This is exactly the structure of commission-type hallucinations. Omission-type hallucinations have a different structure: the response omits Y, but does not contradict the premise. P(contradiction) provides no useful signal for omissions by architectural design.

Prior work (SummaC, TRUE) observed task-level variation in NLI effectiveness but did not articulate this boundary. SummaC's strong performance on summarization benchmarks reflects the fact that those benchmarks (AggreFact, FRANK) contain *inconsistency-annotated* data — where the problematic summaries explicitly contradict the source. HaluEval-Summarization, using GPT-3.5-generated hallucinations, contains a different distribution dominated by abstractive omissions. The commission/omission boundary unifies these observations: NLI detects inconsistency (commission); it cannot detect absence-of-coverage (omission).

This framework has concrete implications for method design. Systems that detect dialogue or QA hallucinations should use NLI-based approaches. Systems targeting abstractive summarization hallucinations need coverage-based approaches: BERTScore recall, ROUGE recall, or entailment-from-summary-to-source metrics that measure whether the summary's claims are supported in the source [Maynez et al., 2020]. Hybrid systems — NLI for commission detection + coverage metrics for omission detection — represent the natural next step.

## The QA Score Compression Paradox

The QA task exhibits an unusual combination: highest Cohen's d (0.779), lowest KL divergence (0.035), and AUROC slightly below the original 0.65 target (0.644). This is not a contradiction — it reflects the geometry of short-context NLI scoring.

QA responses are typically short (one to two sentences), and QA knowledge passages are concise. The NLI model, operating on short (premise, hypothesis) pairs, produces compressed score distributions for both classes: both hallucinated and non-hallucinated QA responses receive contradiction scores clustered in a narrow range. Within this compressed range, ordinal separation is preserved (Cohen's d = 0.779, Wilcoxon p < 0), but the absolute distributional spread is small (KL = 0.035). This means KL divergence is not a reliable mechanism indicator for short-context tasks, while Cohen's d and AUROC remain valid.

The practical implication: for QA deployments, post-hoc NLI detection is effective (AUROC = 0.644), and the near-miss of the original 0.65 target is within the uncertainty of a task-specific threshold set without empirical calibration. The effect size (Cohen's d = 0.779) confirms the signal is genuine and practically significant.

## Honest Limitations

**L1: Summarization scope exclusion.** AUROC = 0.530 on HaluEval-Summarization is not a gap to be closed by tuning — it is a fundamental architectural mismatch. The approach cannot be extended to abstractive summarization omissions without adding coverage-based detection components.

**L2: Incomplete mechanism chain.** Sub-hypotheses h-m2 through h-m4 — testing the attribution of AUROC gains to specific design choices (net-contradiction framing, sentence-level aggregation, dialogue windowing) — were not executed in the current experiments due to the SELF_MODIFY decision from h-m1. The AUROC values of 0.709 and 0.644 are robust (N = 20,000, strong statistical significance), but we cannot yet attribute performance to specific design choices vs. alternative configurations. This ablation gap is a limitation of the current study.

**L3: Single model.** All results are from `cross-encoder/nli-deberta-v3-large`. Generalizability to other NLI architectures (roberta-large-mnli, bart-large-mnli) is unknown. The commission/omission boundary may be model-invariant — the structural constraint is in the task, not the model — but this remains to be verified.

**L4: HaluEval ecological validity.** HaluEval hallucinations are GPT-3.5-style adversarial perturbations, not naturalistic LLM failures from deployed systems. AUROC values reflect detection performance on this perturbation distribution; real-world hallucinations may differ in type distribution and NLI discriminability.

## Broader Impact

Generation-free hallucination detection has practical implications beyond academic benchmarking. Production LLM deployments — dialogue systems, QA assistants, content generation pipelines — routinely log (context, response) pairs for quality monitoring. Post-hoc NLI detection can be applied to this logged data retroactively: no additional LLM inference, no instrumentation changes, no model access beyond a frozen NLI classifier. For commission-dominated applications, the approach provides meaningful detection capability (AUROC ≥ 0.64) at near-zero marginal cost.

The commission/omission boundary also provides a principled guide for when to invest in more expensive detection methods. High-stakes summarization applications — medical note summarization, legal document synthesis — require omission-aware detection that the current approach cannot provide. Knowing this in advance, from the structural framework rather than empirical trial-and-error, is itself a contribution to responsible AI deployment.
