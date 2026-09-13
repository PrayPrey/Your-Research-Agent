# Conclusion

We opened this paper with a reversal: semantic entropy wins on TriviaQA by 0.155 AUROC, then loses on TruthfulQA by 0.066 AUROC. That reversal is not a failure of the method — it is a diagnostic signal that reveals the condition under which semantic-level uncertainty estimation provides genuine value.

## Summary

This paper provides the first unified comparison of semantic entropy (SE), token entropy (TE), SelfCheckGPT BERTScore (SCG), and verbalized confidence (VC) at Llama-2-7B scale, with direct measurement of the mechanism driving the primary performance gap and cross-benchmark testing of its scope.

**We establish that SE substantially outperforms TE on TriviaQA at 7B scale (AUROC 0.717 vs. 0.562, gap = +0.155, non-overlapping 95% CIs).** This confirms that the SE > TE ordering observed by Kuhn et al. [2023] at 65B is not scale-specific noise — the relative advantage holds at a scale where most deployed models operate.

**We identify the mechanism:** within NLI-equivalent paraphrase clusters, token entropy varies 71× above the practical threshold (mean = 7.152 nats²), confirming that TE aggregates surface-form variation that does not reflect semantic uncertainty. SE's NLI clustering removes this paraphrase noise before computing entropy — the mechanism is real, large, and active in 76 of 98 TriviaQA questions.

**We identify the task-structure scope condition.** The ordering reverses on TruthfulQA (TE = 0.511 > SE = 0.445), where adversarial misconceptions produce deterministic-wrong outputs that SE cannot distinguish from correct answers. This scope condition — SE requires tasks where incorrect outputs are paraphrase-diverse — was unidentified in prior work that evaluated SE only on TriviaQA and NaturalQuestions.

**We characterize two alternative method failure modes:** BERTScore-based SCG diverges from SE by 0.336 AUROC on short QA (BERTScore's lexical overlap failing at the 1-3 word span level), and VC at 7B scale produces near-constant confidence (ECE = 0.430, 5 distinct values) that cannot be used as a reliable uncertainty proxy without calibration correction.

## Future Directions

**From untested alternative explanations.** The TruthfulQA reversal has two competing explanations: task-structure dependence (our favored interpretation) and NLI model size (H-C1 used the smaller nli-deberta-v3-small). Re-running H-C1 with nli-deberta-v3-large would isolate these factors. If SE AUROC on TruthfulQA remains low with the large NLI model, the task-structure interpretation is confirmed. If it recovers, the reversal is an NLI model artifact.

**From unverified assumptions.** Our primary finding (N=98, seed=42, TriviaQA dev) represents one sample from the TriviaQA distribution. The pre-specified N=500 extension would confirm whether the SE-TE gap is stable at larger sample sizes — critical before claiming robustness of the ordering.

**From scope extensions.** Testing SelfCheckNLI (NLI-based consistency) as an SCG variant would determine whether the SCG-SE gap is specific to BERTScore or inherent to self-consistency as a paradigm. If SelfCheckNLI matches SE on short QA, the equivalence is real but method-variant-specific. Extending the four-way comparison to Llama-13B and Llama-70B would determine whether the SE > TE gap grows with scale (as Kuhn et al. [2023] suggest from 7B to 65B).

## Closing Thought

The uncertainty method that wins on TriviaQA loses on TruthfulQA. Rather than choosing between benchmarks, we should ask what each benchmark's incorrect outputs look like — diverse or deterministic — and select accordingly. The paraphrase-noise filtering that makes SE powerful on open-domain factual recall becomes a liability when the model's errors are consistent. Understanding this scope condition is more valuable than an unconditional method ranking, and provides a foundation for principled uncertainty method selection as deployment settings grow more varied.
