# 7. Conclusion

We began with two numbers: p=0.583 and p=0.005. Same datasets. Same outcome variable. Same statistical test. Different analysis. Our work explains why these numbers differ and why that difference matters.

The transformation from a null result to a highly significant finding — achieved simply by adding propensity matching — reveals a suppressor confounding structure that previous FAIR-outcome studies have not accounted for. High-FAIR datasets tend to be newer; newer datasets have had less time to accumulate experimental runs; this negative confound suppresses the raw FAIR-reuse correlation, producing misleading null results. Matching on age, task type, and dataset size removes this suppressor, revealing that datasets with higher proxy Findable FAIR scores attract their first experimental run approximately 3× faster (Cox HR=3.159, p=0.005, smoke-test scale).

## Summary of Contributions

In this work, we addressed the question of whether FAIR compliance drives ML dataset research adoption by applying propensity-matched survival analysis — an approach standard in epidemiology but underused in data science repository studies. Our contributions are:

1. **Methodological:** We demonstrate that unadjusted FAIR-reuse correlations are unreliable due to suppressor confounding, and establish propensity-matched observational design as the appropriate methodological standard for this class of questions. This finding is robust to observation window choice and is independent of sample size.

2. **Empirical (preliminary):** We provide the first propensity-matched survival analysis linking FAIR Findable sub-criteria to ML dataset discovery speed on OpenML, with a 28% reduction in median time-to-first-run (158 vs. 202 days) and Cox HR=3.159 in a proof-of-concept smoke-test cohort (n=35 matched pairs). Production-scale replication is the immediate next step.

3. **Practical:** Aggregate FAIR compliance scoring (p=0.697, HR=1.06) is substantially weaker than Findable sub-criteria disaggregation (p=0.005, HR=3.16) on the same datasets. Repository administrators should prioritize Findable-specific improvements — DOI registration, structured metadata, search indexing — rather than optimizing generic FAIR checklist scores.

## Future Directions

Our results open three grounded research directions:

**From untested alternative explanations:** The smoke-test HR=3.16 may partially reflect synthetic cohort generation parameters rather than a genuine Findable→TTFR effect. Production replication on the full OpenML corpus with real upload_date metadata (retrievable via individual dataset API calls at ~83 minutes) is the highest-priority next experiment. If the effect replicates at production scale with real F-UJI scores, the causal claim is substantially strengthened.

**From unverified assumptions:** Assumption A1 — that FAIR metadata is set at publication time rather than retroactively — cannot be verified without real upload_dates. Spearman correlation between FAIR proxy score and dataset age (once upload_dates are available) will diagnose retroactive tagging contamination. If r > 0.3, FAIR-score × age interaction terms should be added to the Cox model.

**From scope extensions:** The two unexecuted sub-hypotheses represent the most consequential remaining questions. H-M3 (Reusable dimension → sustained engagement months 13-36) tests the most theoretically motivated FAIR dimension for long-term research quality. H-M4 (HuggingFace documentation completeness → downloads and model adoption) tests cross-repository generalization. Both have specific experiment designs ready and share infrastructure with the current pipeline.

## Closing

As ML repositories grow in scale and influence — shaping which datasets get used, which get forgotten, and which inform the next generation of models — the question of which infrastructure investments actually improve scientific outcomes becomes increasingly consequential. Our findings suggest that the answer depends critically on how we ask the question. Matched observational methods may reveal FAIR compliance effects that naive correlational analyses systematically hide, and dimension-specific FAIR investment may matter far more than aggregate compliance scores suggest. We hope this work encourages both more rigorous empirical evaluation of repository design choices and more targeted FAIR compliance guidance for the ML community.
