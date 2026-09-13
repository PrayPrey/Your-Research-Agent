# Related Work

Our work sits at the intersection of three bodies of literature: corpus curation and its
effects on model generalization, evaluation benchmark design for generalization measurement,
and data attribution methods. We review each in turn, highlighting why existing work leaves
the specific question we address unanswered.

## Pre-training Corpus Curation and Model Generalization

The empirical evidence that corpus curation improves average benchmark performance is
substantial but consistently confounded. **Biderman et al. [2023]** demonstrate, via the
Pythia suite, that deduplication (Pythia vs. Pythia-dedup) yields small but consistent
improvements on several benchmarks, including a modest HellaSwag gain. However, this
within-architecture, within-corpus comparison tests only deduplication as an isolated
intervention — it does not address multi-stage quality curation, and the HellaSwag gains
are small enough (~0.01 absolute) to be consistent with the near-saturation behavior we
observe at 300B tokens. Critically, the Pythia suite's consistent training procedure and
fixed data ordering make it a uniquely controlled environment, but no cross-quality study
at matched training scale has leveraged these properties for generalization balance analysis.

**Penedo et al. [2023]** show that web-filtered data (RefinedWeb) outperforms unfiltered
data when training Falcon models on average benchmark performance. While this is evidence
for a curation benefit, the comparison involves different model architectures (Falcon vs.
GPT-NeoX), different training durations, and focuses on average performance rather than
generalization balance ratios. The architecture confound remains unresolved.

**Groeneveld et al. [2024]** document OLMo's design, including the Dolma corpus with its
multi-stage curation pipeline. They report that OLMo-7B at full training (~2T tokens)
achieves competitive MMLU performance relative to models of similar size, and attribute
part of this to Dolma's academic content inclusion (S2ORC, Wikipedia). However, this
comparison is not matched by training scale — comparing OLMo at 2T tokens to Pythia at
300B tokens conflates corpus quality with training duration. Our work tests the same
corpus pairing at a matched intermediate scale, revealing that the advantage observed at
full training does not manifest at ~300B tokens.

**Muennighoff et al. [2023]** establish a data quality × training scale interaction:
the benefits of higher-quality data may compound with more training tokens, with
lower-quality models "catching up" as token count increases. Our finding of a null
result at 300B tokens is consistent with this interaction — the Dolma advantage may
emerge later — but it also underscores that intermediate-scale comparisons cannot be
used to make sweeping claims about curation benefits without acknowledging the scale dependency.

**Soldaini et al. [2024]** describe the Dolma corpus in detail, including the multi-stage
curation pipeline, domain composition, and deduplication methodology. This paper provides
the primary documentation of Dolma's quality advantages that motivated our hypothesis.
The gap between Dolma's documented curation investment and the null result we observe
at 300B tokens is precisely what drives the methodological insight of our work.

## Generalization Evaluation Metrics

The benchmarks we use — MMLU [Hendrycks et al., 2021], HellaSwag [Zellers et al., 2019],
and ARC [Clark et al., 2018] — are standard tools for evaluating LLM capabilities, but
their sensitivity to specific factors (training scale, architecture, corpus composition)
has received limited systematic study.

**Hendrycks et al. [2021]** introduce MMLU as a measure of multi-task language understanding
spanning 57 subjects including STEM, humanities, and social sciences. The benchmark is
designed to test knowledge-intensive generalization. Our finding that MMLU differences
between Pythia and OLMo may be architecture-confounded raises questions about MMLU's
suitability as a corpus-quality metric without architectural controls.

**Zellers et al. [2019]** introduce HellaSwag as a commonsense reasoning completion task
designed to be challenging for models while remaining easy for humans. Its 0-shot
evaluation measures the degree to which models have acquired web-sourced commonsense
knowledge from pre-training. Our observation of identical HellaSwag scores (0.4580) for
both models at ~300B tokens suggests a scale-dependent saturation effect that limits
HellaSwag's discriminative power in cross-quality comparisons at this training scale.

The use of performance *ratios* as generalization balance metrics has precedent in the
OOD generalization literature, where ID/OOD performance gaps are used to characterize
a model's generalization behavior [Miller et al., 2021; Koh et al., 2021]. However,
ratio metrics require that both the numerator and denominator remain discriminative at
the comparison point — a requirement that our study shows is violated when the denominator
task saturates.

## Data Attribution and Quality Proxy Methods

Beyond direct comparison, the field has developed tools for attributing model behavior
to training data. Influence functions [Koh and Liang, 2017], TRAK [Park et al., 2023],
and TracIn [Pruthi et al., 2020] identify which training examples most influenced specific
predictions. These methods could in principle quantify the contribution of high-quality
vs. low-quality data subsets to generalization performance, but they have not been applied
to the corpus-quality × generalization-balance question at the scale of 300B-token pre-training.
Such attribution analyses represent a promising direction for moving beyond the descriptive
comparisons we report, but require architecture-matched designs to avoid confounding
attribution results with architecture effects.

## Positioning Our Contribution

Our work differs from prior literature in three ways. First, we use a **matched training scale**
(~300B tokens, both models within 0.5% of target) to eliminate training duration as a confound.
Second, we focus on **generalization balance** (ratio and delta metrics) rather than absolute
performance, asking whether a model's knowledge acquisition and commonsense reasoning grow
in proportion — a question more directly linked to the corpus-quality hypothesis than
average benchmark improvement. Third, we report a **scope-qualified null result** with
explicit characterization of the conditions under which the comparison breaks down, rather
than drawing causal conclusions from an architecturally confounded design. Our finding
that HellaSwag saturates at identical values for both models provides a structural
explanation for the null result that goes beyond simply reporting "no difference was found."
