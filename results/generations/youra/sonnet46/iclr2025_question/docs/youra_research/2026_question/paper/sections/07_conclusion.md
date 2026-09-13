# Conclusion

We opened with a counterintuitive question: does the information needed to detect hallucinations already exist in a single forward pass of a frozen NLI classifier? After evaluating 60,000 (context, response) pairs across three HaluEval tasks, the answer is: yes — for some hallucinations, and no for others. Which ones, and why, is the contribution.

## Summary

Generation-free post-hoc NLI contradiction scoring achieves AUROC = 0.709 on HaluEval-Dialogue and AUROC = 0.644 on HaluEval-QA using `cross-encoder/nli-deberta-v3-large` frozen at inference time. These results surpass generation-based SelfCheckGPT-NLI by +0.229 and +0.114 respectively, with zero LLM generation overhead. The detection mechanism — DeBERTa's graded support sensitivity — is confirmed via Wilcoxon rank-sum tests (p ≈ 0 and p = 1.52e-271) and large effect sizes (Cohen's d = 0.714, 0.779).

On HaluEval-Summarization, the approach fails (AUROC = 0.530, near chance). This is not a performance gap but a structural result: summarization hallucinations are predominantly omissions — content that fails to capture the source document without explicitly contradicting it. NLI contradiction scoring cannot detect what does not contradict. The structural ceiling analysis confirms the theoretical maximum AUROC for contradiction-based detection on omission-dominated summarization is approximately 0.52.

The commission/omission boundary unifies these observations: NLI-based generation-free detection is viable for commission-type hallucinations (dialogue, QA) and structurally insufficient for omission-type hallucinations (abstractive summarization). This is not just a finding about our method — it is a framework for selecting hallucination detection approaches in general.

## Future Work Vision

Three directions follow directly from our findings:

**Omission-aware detection.** The natural complement to commission detection is coverage-based omission detection: BERTScore recall, ROUGE recall, or source-entailment metrics measuring whether the summary's claims are present in the source. A hybrid detector — NLI for commissions, coverage for omissions — should close the summarization gap without requiring LLM generation. We predict AUROC > 0.65 on HaluEval-Summarization for such a hybrid.

**Design choice attribution.** The AUROC values of 0.709 and 0.644 are established. What drives them is not. Sub-hypotheses h-m2 through h-m4 — testing net-contradiction framing advantage (≥0.02 AUROC delta), sentence-level aggregation benefit, and dialogue windowing — remain unexecuted. Completing this ablation chain will determine whether these gains are robust design choices or whether simpler configurations achieve comparable performance.

**Cross-model generalization.** The commission/omission boundary is a property of the *hallucination types*, not a property of DeBERTa specifically. Replicating the h-e1 experiment with roberta-large-mnli and bart-large-mnli will determine whether the AUROC values are DeBERTa-specific or whether any MNLI-trained model achieves comparable commission detection.

## The Map

The commission/omission boundary is not just a limitation — it is a map. It tells us where generation-free NLI detection works (dialogue, QA), where it doesn't (abstractive summarization), and why. Knowing where the territory ends is as valuable as knowing where to go.

For production systems where dialogue and QA hallucinations are the primary concern, the answer is now clear: a frozen NLI classifier, applied post-hoc to logged (context, response) pairs, provides meaningful hallucination detection at near-zero cost. The overhead of LLM generation at monitoring time is a choice, not a requirement — at least for commission-type hallucinations.
