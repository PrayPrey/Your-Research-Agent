# Conclusion

The most-studied benchmarks may indeed be teaching models the wrong lessons. Our experiments demonstrate that models trained on high-popularity datasets exhibit generalization gaps 21 percentage points larger than those trained on less-popular alternatives from the same domain—a substantial effect with clear implications for how the research community evaluates progress.

We provide the first systematic evidence linking dataset popularity (measured via repository run-rates and research paper counts) to generalization failure. Popular benchmarks attract disproportionate optimization investment—nearly 25 times more research papers focus on high-use datasets compared to low-use alternatives. However, the mechanism is not straightforward: contrary to expectations from texture bias literature, modern architectures show *improved* shape-based generalization, suggesting that the co-evolution effect operates through pathways other than texture exploitation.

Our findings call for a simple but impactful change in ML evaluation practice: complement popular benchmarks with diverse alternatives. A model that excels on CIFAR-10 may fail dramatically on CINIC-10; validating on less-optimized held-out data before deployment could prevent such failures. For the research community, reporting performance on diverse benchmarks—including less-popular ones—would provide a more complete picture of model capabilities.

Several directions remain for future work. First, identifying the true causal mechanism: we ruled out texture bias, but spurious correlations, background features, or test set leakage remain viable hypotheses. Second, extending to other domains: NLP, tabular data, and audio benchmarks may exhibit similar or different patterns. Third, developing practical tools for "popularity-aware" benchmark selection that help practitioners identify overfitted evaluation targets.

The popularity paradox is real: the benchmarks we trust most may be the ones we should trust least. Addressing this requires not abandoning established benchmarks, but thoughtfully diversifying our evaluation portfolios.
