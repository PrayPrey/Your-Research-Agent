# Conclusion

We began with a straightforward goal: measure how dataset documentation quality and benchmark concentration predict ML reproducibility failure, using HuggingFace Hub and OpenML as data sources. What we found instead was that the metadata infrastructure we assumed existed does not — and that this absence follows a pattern that has implications for any researcher attempting programmatic reproducibility auditing of pre-2018 ML literature.

In this work, we designed and executed a systematic infrastructure feasibility study (H-E1) to determine whether HF Hub and OpenML can serve as data sources for a dataset-metadata-to-reproducibility-outcome regression study on Raff's 255-paper corpus. Our main contributions are:

1. **The first empirical quantification of HF Hub and OpenML coverage for the Raff 2019 corpus:** HF Hub achieves 30% dataset card coverage (15/50 datasets found, all NLP benchmarks); OpenML achieves 22% pre-publication temporal coverage (11/50, all classical tabular). Both fall below the minimum thresholds required for valid regression analysis.

2. **Characterization of the domain-temporal selection bias in both APIs:** Coverage gaps are not random — they precisely follow each platform's founding community. HF Hub is NLP-centric; OpenML is tabular-ML-centric. DL vision, speech, and graph datasets — which dominate Raff's corpus — are absent from both platforms. This finding is informative for the broader reproducibility auditing community.

3. **Identification of Papers With Code as the appropriate primary data source:** Our findings provide a principled motivation for switching to Papers With Code API for a redesigned study, as PwC explicitly tracks paper-dataset linkages across all dataset domains and historical periods.

4. **A validated, reusable data acquisition pipeline:** RaffParser, HFCoverageChecker, OpenMLTemporalChecker, MetricsAggregator, and 18-test suite are available for immediate reuse in a redesigned infrastructure study.

## Future Directions

**Redesigned H-E1 using Papers With Code (highest priority):** The most direct path to answering the original research question is to replace HF+OpenML with Papers With Code as the primary data source for IV1 and IV2. PwC explicitly links papers to datasets with code implementations across all domains, making it the natural coverage-adequate alternative. A redesigned H-E1 should measure PwC coverage for Raff's 50 datasets and determine whether coverage reaches the ≥70% threshold required for valid regression.

**HF Hub name variant exploration:** Our pipeline used canonical dataset names. Alternate name variants (e.g., "uoft-cs/cifar10" instead of "cifar10") may recover additional HF Hub cards. Running the pipeline with systematic name variant expansion would determine whether the 30% figure is a lower bound (name mismatch) or a ceiling (structural domain gap). This is the lowest-cost next experiment.

**Post-2019 corpus extension:** The HF Hub ecosystem has grown substantially since 2020. A reproducibility auditing study targeting NeurIPS/ICML/ICLR 2020–2024 papers, using ML Reproducibility Challenge labels as the dependent variable, would encounter substantially higher HF card coverage (>60% expected) and would be able to test the documentation completeness hypothesis on a corpus better matched to HF Hub's design scope.

**Multi-source hybrid:** Combining HF Hub, OpenML, Papers With Code, and arXiv metadata via NER extraction would push coverage toward 80–90% for Raff's corpus, enabling the original regression study without requiring the assumptions about any single API's coverage.

The infrastructure gap we discovered is both a limitation of this paper and a contribution to the field. Any researcher planning to use HF Hub and OpenML to study pre-2018 ML reproducibility should quantify coverage for their specific corpus before proceeding — the structural domain biases in these platforms are invisible unless explicitly measured. We hope this work saves others from the same discovery at a later and more costly stage of their pipeline.
