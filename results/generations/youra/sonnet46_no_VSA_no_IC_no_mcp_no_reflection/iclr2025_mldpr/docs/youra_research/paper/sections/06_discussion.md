# Discussion

## Key Findings and Their Implications

**Finding 1: Both HF Hub and OpenML exhibit domain-temporal selection bias, not random coverage gaps.**

The most important result is not that coverage is low — it is *why* coverage is low and *which* datasets are missing. The 30% HF coverage is not distributed randomly across the 50 queried datasets; it consists entirely of NLP benchmarks (IMDB, SST-2, GLUE, SQuAD, AG News). The 22% OpenML coverage consists entirely of classical tabular datasets (iris, adult, covertype, diabetes, breast\_cancer). The datasets that are missing — CIFAR-10, ImageNet, COCO, KITTI, LibriSpeech, TIMIT, Cora — are precisely the datasets that dominate the deep learning and early neural network literature in Raff's corpus.

This has an important implication for any researcher planning a metadata-based reproducibility auditing study of pre-2018 ML papers: using HF+OpenML will produce a study that is structurally restricted to analyzing the NLP and classical ML subsets of the corpus, even if the researcher is unaware of this restriction. The coverage gap is invisible if you only look at hit counts without examining which datasets were missed.

**Finding 2: Papers With Code is the appropriate primary data source for a redesigned study.**

Papers With Code explicitly links papers to datasets with code implementations across all dataset domains — vision, NLP, speech, tabular, graph. Unlike HF Hub (NLP-centric) and OpenML (tabular-centric), Papers With Code is designed for the paper-dataset-code linkage we require and covers the Raff corpus's temporal period (1984–2017 papers appear in PwC because they are still cited in recent work that links to their datasets). The theoretical hypothesis — documentation completeness and concentration predict reproducibility failure — remains scientifically plausible and worth testing, but requires PwC as the data source for IV1 and IV2.

**Finding 3: Retroactively-created HF cards are systematically thin.**

The 0.41 mean field-presence score for found HF cards reveals a second infrastructure problem beyond coverage: even when a card exists, it may not contain the fields most relevant to the misuse mechanism. The `intended_use` and `out_of_scope_use` fields — the Datasheets schema fields that directly encode scope boundaries and therefore out-of-context application risk — are systematically absent from retroactively-created cards. This is consistent with the timing: the Datasheets schema (Gebru et al., 2021) was published after most of these foundational benchmark cards were created. A redesigned study using PwC would need to account for this field-level coverage problem as well, potentially using PwC task tags as a proxy for scope specification.

## Limitations

**Limitation 1: The original research question remains unanswered.**

The central hypothesis — do documentation completeness and benchmark concentration predict ML reproducibility failure in Raff's corpus? — is neither confirmed nor refuted by this paper. H-M1, H-M2, and H-M3 were blocked by H-E1's gate failure. We report an infrastructure characterization, not an empirical test of the misuse-reproducibility linkage.

This is acceptable because (a) running regression on severely incomplete data (30% IV1 coverage, 22% IV2 coverage) would produce biased, uninterpretable results; (b) blocking was the correct decision per the pre-specified pipeline design; and (c) the infrastructure characterization is itself a contribution — it defines the preconditions that any future study must satisfy.

**Limitation 2: H-E1 used canonical dataset names only.**

The HF Hub queries used canonical dataset names as they appear in Raff's CSV (e.g., "cifar10", "imagenet-1k"). HF Hub name resolution is namespace-sensitive: CIFAR-10 may exist under "uoft-cs/cifar10" or "torchvision/cifar10" rather than the canonical "cifar10". Our 30% coverage figure may therefore be a lower bound — alternate name variants might recover some datasets.

We judge this limitation acceptable for two reasons. First, a reproducibility auditing pipeline that requires manual curation of name variants for each dataset defeats the purpose of automated auditing at scale. Second, even if name variants recovered 15–20% additional coverage, the DL vision and speech datasets that constitute the majority of missing coverage are simply absent from HF Hub under any name — their absence is structural, not a naming artifact.

**Limitation 3: Results are specific to the Raff 2019 corpus.**

Our coverage characterization applies to the 50 datasets in Raff's pre-2018 ML corpus. Post-2019 ML papers have a different dataset distribution — more NLP benchmarks (BERT-era, GPT-era tasks), more HF Hub-native datasets, and less emphasis on the pre-2018 DL vision benchmarks. A reproducibility auditing study of post-2020 literature would likely find substantially higher HF coverage.

**Limitation 4: The theoretical mechanism remains empirically unverified.**

The three-step causal chain — (1) benchmark concentration → artifact accumulation; (2) documentation incompleteness → out-of-context application; (3) joint effect → reproducibility failure — is theoretically grounded in D'Amour et al. [2021] and Gebru et al. [2021] but has not been tested empirically. We cannot claim the mechanism operates without the regression analysis that H-E1's failure blocked.

## Broader Impact

This research has three categories of impact:

**Positive:** Our infrastructure characterization directly benefits any researcher planning to use HF Hub and OpenML for metadata-based reproducibility auditing of pre-2018 ML literature. Without this characterization, such researchers would build pipelines that silently fail to represent 70–78% of the target corpus. The coverage measurement (30%, 22%) and root-cause analysis (domain-temporal selection bias) are immediately actionable.

Our reusable pipeline components (RaffParser, HFCoverageChecker, OpenMLTemporalChecker, MetricsAggregator, 18-test suite) provide a validated starting point for the redesigned study using Papers With Code. Researchers can adopt the Raff corpus parsing and gate evaluation framework without reimplementing from scratch.

**Negative/Risks:** We do not identify significant negative impacts. The paper reports infrastructure limitations and suggests a redesigned study; it does not deploy a model or system that could be misused. The finding that HF Hub and OpenML have coverage gaps for pre-2018 DL benchmarks is descriptive and methodological.

**Reflexivity note:** The Datasheets for Datasets schema we use to measure documentation completeness was designed for new dataset creation, not retroactive annotation of foundational benchmarks. Evaluating CIFAR-10 by whether its HF card contains an `out_of_scope_use` field conflates absence-of-documentation with absence-of-concern-for-misuse — Krizhevsky et al. [2009] could not have annotated a schema published in 2021. A redesigned study should grapple with this temporal validity problem in the documentation quality operationalization.
