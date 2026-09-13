# Conclusion

We investigated whether signals related to human agency preservation can be extracted from existing AI preference data and validated as an independent alignment dimension. Our experiments demonstrated that the Bidirectional Alignment Index (BAI), computed from four agency proxies, achieves high extraction reliability (mean AUROC 0.98) and survives adversarial probing designed to remove reward-predictive variance (AUROC 0.99 post-gradient-reversal). However, semantic analysis revealed that high-BAI responses cluster by generic conversational patterns rather than interpretable agency vocabulary.

This combination of positive and negative results refines our understanding of what current methods can and cannot achieve. We can reliably extract signals that are statistically independent from reward — but these signals may not capture what we intend them to measure. The gap between extractability and interpretability is the core lesson.

Our methodological contributions remain valid. Adversarial probing via gradient reversal can verify representational independence between candidate alignment dimensions. Semantic clustering can test whether extracted signals carry meaningful content. These tools should become standard practice for any proposed operationalization of bidirectional alignment.

Future work should pursue richer operationalizations. Embedding-based classifiers or LLM-as-judge approaches can distinguish communicative intent from grammatical pattern. Human annotation of functional agency preservation can provide ground truth for supervised learning. Domain stratification — separating advisory prompts from factual QA — can clarify where agency preservation is most relevant.

The Bidirectional Alignment Framework posits that complete AI alignment requires both AI→Human and Human→AI components. Our work shows that the second component resists naive operationalization — surface-level linguistic proxies do not capture semantic agency content. But it also demonstrates that the methodological infrastructure for rigorous validation exists. The path forward requires richer operationalizations tested with equal rigor.
