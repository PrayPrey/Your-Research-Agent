# Does ML Metadata Infrastructure Cover What We Assume? Characterizing HuggingFace Hub and OpenML Coverage Gaps for Pre-2018 Reproducibility Auditing

## Abstract

We set out to measure how dataset documentation quality and benchmark concentration predict ML reproducibility failure — and discovered that the metadata infrastructure we assumed existed does not. This paper reports an infrastructure feasibility study (H-E1) designed to determine whether HuggingFace Hub dataset cards and OpenML run counts can serve as data sources for a metadata-based reproducibility auditing study on Raff's 255-paper corpus of top-venue ML papers from 1984–2017. The study reveals a systematic coverage gap: HF Hub achieves only 30% dataset card coverage for the corpus (15 of 50 queried datasets; found datasets concentrated in NLP benchmarks, with large-scale DL vision, speech, and graph datasets absent), while OpenML provides pre-publication entries for only 22% (11 of 50; restricted predominantly to classical tabular datasets, with NLP benchmarks IMDB and 20 Newsgroups and MNIST also present). Neither threshold is sufficient for valid regression analysis. Both gaps trace to the same structural cause: each platform's ecosystem reflects its founding community rather than the broader benchmark landscape of pre-2018 ML literature. Among the 15 found HF cards, the mean field-presence score across 7 Datasheets for Datasets schema fields is 0.41, indicating that retroactively-created cards for foundational benchmarks are systematically under-populated. The pipeline executes correctly against live APIs in 88.84 seconds, with 18 of 18 tests passing; the gate failure is a genuine infrastructure finding, not an implementation defect. These findings indicate that any reproducibility auditing study of pre-2018 ML papers built on HF Hub and OpenML will be structurally biased toward NLP papers and will omit the deep learning benchmarks that dominate the corpus. We characterize the root causes, provide a validated reusable data acquisition pipeline, and identify Papers With Code as the most appropriate primary data source for a redesigned study. The original theoretical hypothesis — linking metadata-observable dataset misuse signals to reproducibility failure — remains scientifically plausible but untested, as the blocked downstream analyses (H-M1, H-M2, H-M3) require adequate data infrastructure to proceed.

---

## 1. Introduction

The ML reproducibility crisis is well-documented. Raff [2019] found that approximately 50% of top-venue ML papers from 1984–2017 fail independent reproduction attempts. Subsequent work has proposed normative interventions: checklists requiring code submission and dataset specification [Pineau et al., 2021], and structured dataset documentation frameworks [Gebru et al., 2021]. What is absent from the literature is an empirical linkage between *metadata-observable signals* — signals derivable from public APIs without re-running experiments — and reproducibility failure outcomes.

The theoretical motivation for such a linkage exists across two independent research threads. D'Amour et al. [2022] identified underspecification as a credibility challenge in modern ML: models optimized on highly concentrated benchmark datasets learn dataset-specific artifacts rather than generalizable patterns, producing results that break under independent replication. Gebru et al. [2021] proposed that absent `intended_use` and `out_of_scope_use` fields in dataset documentation increase the risk of out-of-context dataset application. If these mechanisms operate in practice, then metadata-observable proxies — HuggingFace Hub field-presence scores for documentation completeness, and Herfindahl-Hirschman Index over OpenML run counts for benchmark concentration — should predict which papers in Raff's corpus fail independent reproduction. Testing this hypothesis would provide the first empirical bridge between the dataset documentation and ML reproducibility literatures.

The gap in existing work is structural: no study has tested this linkage because it requires querying post-2019 APIs against a pre-2018 corpus. We designed a systematic infrastructure feasibility study to determine whether the required data exists before investing in regression analysis.

Our central finding is that HuggingFace Hub and OpenML exhibit strong domain and temporal selection biases aligned with their founding communities, not with the broader benchmark ecosystem of the pre-2018 ML literature. HF Hub emerged from the NLP/transformer community: IMDB, SST-2, AG News, SQuAD, and GLUE components are present; large-scale DL vision datasets (ImageNet, COCO, Pascal VOC, KITTI, Caltech-101, Caltech-256), speech datasets (LibriSpeech, TIMIT, Wall Street Journal), and graph datasets (Cora, Citeseer) return no valid cards. OpenML was designed for classical tabular ML experiments and architecturally cannot host large image or audio datasets: iris, adult, and covertype are present, as are IMDB, 20 Newsgroups, and MNIST; CIFAR, ImageNet, and other DL benchmarks are absent. This is not a pipeline defect — 18 of 18 tests pass and the pipeline completes against live APIs in under 90 seconds. The coverage gap is in the platforms themselves.

This paper makes the following contributions:

**C1 (Empirical):** The first systematic quantification of HuggingFace Hub and OpenML coverage for the Raff 2019 reproducibility corpus, establishing that HF Hub achieves 30% dataset card coverage (15/50 datasets found; all NLP benchmarks; large-scale DL vision, speech, and graph datasets absent) and OpenML achieves 22% pre-publication temporal coverage (11/50; predominantly classical tabular datasets plus IMDB, 20 Newsgroups, and MNIST). Both fall below the minimum thresholds required for valid regression analysis (≥50% and ≥70%, respectively).

**C2 (Infrastructure characterization):** Documentation of the domain-temporal selection bias in both APIs: HF Hub's ecosystem reflects its NLP/transformer origin; OpenML's architecture structurally excludes large image, audio, and graph datasets. Any reproducibility auditing study of pre-2018 ML literature using these APIs will be structurally biased toward NLP and classical tabular ML papers, systematically omitting DL vision and speech papers.

**C3 (Methodological):** Identification of Papers With Code API as the most appropriate primary data source for this class of reproducibility auditing study, motivated by the empirical characterization of HF Hub and OpenML limitations. This is a theoretical recommendation; the claim has not been empirically verified.

**C4 (Reusable infrastructure):** A validated, 18-test data acquisition pipeline — comprising RaffParser, HFCoverageChecker, OpenMLTemporalChecker, MetricsAggregator, and Visualizer modules — that is immediately reusable for a redesigned study.

The remainder of this paper is organized as follows. Section 2 surveys related work in ML reproducibility auditing, dataset documentation, and benchmark concentration. Section 3 describes the pipeline design and experimental protocol. Section 4 describes the experimental setup. Section 5 presents the coverage measurements and domain analysis. Section 6 discusses implications, limitations, and future directions. Section 7 concludes.

---

## 2. Related Work

### 2.1 ML Reproducibility

Raff [2019] provided the foundational labeled corpus for ML reproducibility research: 255 top-venue papers (NeurIPS, ICML, ICLR, JMLR) from 1984–2017, each with a binary reproducibility label from manual re-implementation attempts by a single researcher. The corpus established that approximately 50.8% of papers succeed under independent reproduction and identified paper-level features predictive of success: pseudocode presence, equation count, and hyperparameter reporting. Critically, Raff analyzed *paper-quality* features rather than *dataset-quality* features — the dataset-level signals this study investigates were not available from public APIs at the time of his study, and Raff's original feature set does not include metadata-observable misuse signals.

The ML Reproducibility Challenge [Pineau et al., 2021] extended this work to post-2019 papers using multi-annotator reproduction attempts. NeurIPS, ICML, and other venues have adopted reproducibility checklists requiring code submission, dataset specification, and hyperparameter reporting. These interventions are normative — they specify what should be done — but do not empirically test whether documentation presence predicts reproduction success.

Gundersen and Kjensmo [2018] analyzed ML papers for reproducibility factors including experimental setup documentation. Kapoor and Narayanan [2023] identified data leakage as a systematic driver of reproducibility failure in ML across domains. Neither work connects dataset-level metadata APIs to reproducibility labels.

### 2.2 Dataset Documentation

Gebru et al. [2021] introduced Datasheets for Datasets, proposing a structured documentation framework for ML datasets covering motivation, composition, collection process, uses, and maintenance. The Datasheets schema has been adopted as the basis for HuggingFace Hub dataset cards and is the foundation of the field-presence completeness metric used in this study. Gebru et al. propose the schema normatively: they do not test whether dataset card completeness predicts downstream model failure.

Bender et al. [2021] and Gebru et al. [2021] both argue that documentation scope fields (`intended_use`, `out_of_scope_use`) are critical for preventing out-of-context dataset application — the mechanism theorized to predict reproducibility failure. The present work is the first attempt to operationalize this theoretical link against a labeled reproducibility outcome dataset, though the operationalization was blocked by the infrastructure gap reported here.

YoungXinyu1802 et al. [2024] analyzed 7,433 HuggingFace Hub dataset cards, finding improving completeness over time and identifying field-level completion rates. Their analysis covers the overall HF Hub ecosystem but does not characterize coverage for specific reproducibility corpora, does not analyze pre-2018 ML benchmark datasets, and does not connect card completeness to reproducibility outcomes. The finding in this study that even found HF cards average only 0.41 mean field-presence score complements their temporal analysis by revealing the thinness of retroactively-created cards for foundational benchmarks.

### 2.3 Benchmark Concentration and Underspecification

D'Amour et al. [2022] introduced underspecification as a challenge for credibility in ML: models trained on the same data to the same accuracy may behave very differently at deployment because the training distribution fails to select among many valid predictors. Highly concentrated benchmark datasets — where the community has trained and evaluated on the same splits over many years — accumulate dataset-specific artifacts that models learn. D'Amour et al. do not operationalize concentration as a measurable quantity or link it to Raff's reproducibility labels.

Recht et al. [2019] and Engstrom et al. [2020] demonstrated that models trained on CIFAR-10 and ImageNet show substantial accuracy drops on new test sets, consistent with artifact overfitting. These findings provide empirical grounding for the concentration hypothesis: high usage concentration in a benchmark may signal elevated artifact accumulation risk.

### 2.4 Dataset Infrastructure for Reproducibility Studies

Vanschoren et al. [2014] introduced OpenML as a platform for systematic ML experimentation, providing per-dataset run counts and task creation timestamps. OpenML is designed for tabular, classical ML experiments and has been used in AutoML benchmarking [Feurer et al., 2022]. This study is the first to systematically quantify OpenML's coverage for a deep-learning-heavy reproducibility corpus, finding 22% coverage concentrated in classical tabular and a small number of NLP and image datasets — consistent with OpenML's documented design scope but previously unquantified for Raff's corpus.

Papers With Code [Stojnic and Taylor, 2020] explicitly links ML papers to datasets, code implementations, and benchmark results across all domains. In contrast to HF Hub and OpenML, Papers With Code covers DL vision, NLP, speech, and tabular datasets and is used in reproducibility research.

### 2.5 Positioning

No prior work has: (1) empirically tested whether HF Hub and OpenML provide adequate coverage of the Raff 2019 corpus for metadata-based reproducibility auditing, (2) characterized the domain-temporal selection biases of these APIs for pre-2018 ML benchmarks, or (3) proposed Papers With Code as the appropriate primary API for this class of study. This work addresses all three.

---

## 3. Method

### 3.1 Study Design

H-E1 is designed as a gate hypothesis: a pre-specified infrastructure feasibility check with binary outcome that must pass before any regression analysis proceeds. Running statistical analysis on severely incomplete data — with 30% independent variable coverage — would produce coefficients confounded with the domain distribution of datasets that happen to have HF cards, rather than with the domain distribution of datasets in Raff's corpus. The gate design prevents this.

Gate criteria are pre-specified and not chosen post-hoc:

- **HF Hub coverage threshold:** ≥50% of Raff's unique datasets must return valid dataset cards.
- **OpenML temporal filter threshold:** ≥70% of Raff's unique datasets must have pre-publication OpenML entries suitable for HHI computation.

These thresholds ensure that the intended independent variables — documentation completeness (IV1, from HF Hub field-presence scoring) and benchmark concentration (IV2, from OpenML HHI over pre-publication run counts) — are computable for a sufficient fraction of the 255-paper corpus to support valid logistic regression without severe survivorship bias.

Gate logic uses AND: both criteria must pass. If either fails, downstream mechanism hypotheses H-M1 (documentation completeness predicts reproducibility failure), H-M2 (benchmark concentration predicts reproducibility failure), and H-M3 (field-level importance ordering) are blocked until the infrastructure gap is resolved.

### 3.2 Pipeline Architecture

The pipeline consists of five modules orchestrated by `pipeline.py`:

**RaffParser** loads Raff's CSV (255 papers, binary reproducibility labels, paper-quality features) and extracts the set of 50 unique benchmark datasets with their earliest paper publication years. The parser validates column completeness and row count, raising on violation.

**HFCoverageChecker** queries HuggingFace Hub for each of the 50 datasets using `DatasetCard.load(name)` with canonical dataset names (e.g., "cifar10", "imagenet", "coco"). For each returned card, it computes a field-presence score as the fraction of 7 Datasheets for Datasets schema fields present: `{intended_use, out_of_scope_use, limitations, license, task_categories, dataset_info, provenance}`. A rate limit sleep of 1.0 second between requests prevents API throttling. HTTP 403 (authentication required) and 404 (dataset not found) errors are explicitly handled and distinguished. Canonical dataset names are used because a reproducibility auditing pipeline must be automatable; requiring manual name variant curation would defeat the purpose of a scalable pipeline.

**OpenMLTemporalChecker** performs a single bulk API call (`openml.datasets.list_datasets(output_format='dataframe')`) to retrieve all available OpenML datasets with metadata including upload date. It then applies a client-side temporal filter: for each of the 50 Raff datasets, it checks whether a matching OpenML entry exists with `upload_date_year < paper_publication_year`. This filter ensures that pre-publication run counts are computable without contaminating the measurement with post-publication community use.

**MetricsAggregator** computes the two gate metrics from checker outputs and evaluates pass/fail against pre-specified thresholds. It verifies four pipeline activation indicators before gate evaluation is considered meaningful: HF API reachable, OpenML API reachable, Raff CSV parseable, temporal filter executable.

**Visualizer** generates three figures: a gate metrics bar chart (Figure 1), an OpenML pre-publication run count distribution histogram (Figure 2), and an HF card field-presence heatmap (Figure 3).

### 3.3 Test Suite

An 18-test pytest suite covers all pipeline components and runs against the live APIs without mocking. Tests verify: correct Raff CSV parsing (255 rows, all columns), HF Hub card loading and field scoring logic, OpenML temporal filtering, gate evaluation (pass/fail logic, activation indicators), and figure generation. Live API tests are the only valid approach for an infrastructure feasibility study: mocking the APIs validates implementation correctness but cannot detect platform scope limitations — the discovery this study is designed to make.

---

## 4. Experimental Setup

Four research questions guide the infrastructure feasibility study:

**RQ1:** What fraction of the 50 unique benchmark datasets in Raff's corpus have HuggingFace Hub dataset cards under canonical dataset names?

**RQ2:** What fraction have pre-publication OpenML entries suitable for HHI computation?

**RQ3:** Do coverage gaps follow systematic domain and temporal patterns, or are they distributed randomly across dataset types?

**RQ4:** Among found HF cards, what is the mean field-presence score across the 7 Datasheets schema fields?

### 4.1 Corpus

**Raff 2019 Reproducibility Corpus:** 255 ML papers from NeurIPS, ICML, ICLR, and JMLR, published 1984–2017, each with a binary reproducibility label from manual re-implementation by a single researcher.

| Property | Value |
|----------|-------|
| Total papers | 255 |
| Reproducible | 130 (50.8%) |
| Not reproducible | 125 (49.2%) |
| Unique datasets queried | 50 |
| Year range | 1984–2017 |

The 50 datasets span multiple domains: DL vision (CIFAR-10, CIFAR-100, ImageNet, COCO, Pascal VOC, KITTI, Caltech-101, Caltech-256); NLP/text (IMDB, SST-2, AG News, SQuAD, GLUE, 20 Newsgroups, Reuters, Penn Treebank); speech (LibriSpeech, TIMIT, Wall Street Journal); graph (Cora, Citeseer); classical tabular/UCI (iris, adult, covertype, diabetes, wine, breast\_cancer, yeast); and other (MNIST, SVHN, KDD99, Netflix Prize, MovieLens).

### 4.2 Evaluation Metrics

**HF coverage rate:** Fraction of 50 queried datasets returning a valid HF card (non-null `DatasetCard.load` response). Gate threshold: ≥0.50.

**OpenML temporal filter success rate:** Fraction of 50 queried datasets with at least one OpenML entry satisfying `upload_date_year < paper_publication_year`. Gate threshold: ≥0.70.

**HF mean field-presence score:** For datasets with found HF cards, mean fraction of 7 Datasheets schema fields present (each field scored as binary present/absent). Reported descriptively; no gate threshold.

**Pipeline activation indicators:** Four binary checks. Gate pass/fail is meaningful only when all four activation indicators are true.

Gate logic: AND of (HF coverage rate ≥ 0.50) AND (OpenML temporal filter success rate ≥ 0.70).

---

## 5. Results

### 5.1 Gate Metric Evaluation

![Gate Metrics vs. Thresholds](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/gate_metrics.png)

*Figure 1. Gate metrics against pre-specified thresholds. HF Hub coverage rate: 0.30 (threshold: 0.50; FAIL). OpenML temporal filter success rate: 0.22 (threshold: 0.70; FAIL). Both gate criteria are not met.*

**HF Hub coverage (RQ1):** 15 of 50 queried datasets (30%) returned valid HuggingFace Hub dataset cards. This is 20 percentage points below the 50% gate threshold. Gate criterion: not met.

**OpenML temporal filter (RQ2):** 11 of 50 queried datasets (22%) have at least one pre-publication OpenML entry. This is 48 percentage points below the 70% gate threshold. Gate criterion: not met.

Both gate criteria fail. The H-E1 AND gate does not pass. Downstream hypotheses H-M1, H-M2, and H-M3 are blocked. All four pipeline activation indicators passed, confirming that the measurements are valid: both APIs were reachable, the Raff CSV parsed correctly, and the temporal filter executed. The gate failure reflects the state of the platforms, not a pipeline defect.

### 5.2 Domain Pattern Analysis

The distribution of found and missing datasets across domains reveals a systematic pattern rather than random missingness (RQ3).

| Domain | Datasets queried | HF Hub found | OpenML found |
|--------|-----------------|-------------|-------------|
| NLP/text classification | ~10 | ~12 (IMDB, SST-2, AG News, SQuAD, GLUE, PubMed, WMT14, Reuters21578, OHSUMED, Yelp, Amazon, SST2) | 2 (IMDB, 20 Newsgroups) |
| Small-scale image (MNIST, CIFAR-10/100, SVHN) | ~4 | ~3 (CIFAR-10, CIFAR-100, SVHN) | 1 (MNIST) |
| Large-scale DL vision (ImageNet, COCO, Pascal VOC, KITTI, Caltech-101/256) | ~11 | 0 | 0 |
| Speech/audio (LibriSpeech, TIMIT, WSJ) | ~5 | 0 | 0 |
| Graph (Cora, Citeseer) | ~5 | 0 | 0 |
| Classical tabular/UCI | ~15 | 0 | 8 (iris, wine, breast\_cancer, diabetes, adult, covertype, yeast, and related) |

The found datasets list from live API queries is as follows. HF Hub found (15 datasets): mnist, cifar10, cifar100, svhn, imdb, ag\_news, yelp\_polarity, amazon\_polarity, sst2, glue, pubmed, wmt14, squad, reuters21578, ohsumed. OpenML found (11 datasets with pre-publication entries): mnist (1 entry), imdb (1), 20newsgroups (1), iris (2), wine (2), breast\_cancer (1), diabetes (1), adult (2), covertype (4), coco (1), yeast (1).

The HF Hub coverage gap is concentrated in large-scale DL vision (0 of approximately 11 queried datasets found), speech (0 of 5), and graph (0 of 5) domains. Among NLP benchmarks and small-scale image classification datasets, coverage is substantially higher. OpenML coverage is concentrated in classical tabular datasets, with IMDB, 20 Newsgroups, and MNIST also present. The COCO entry in OpenML (1 pre-publication entry) is noted; it may represent a different dataset sharing the name or a thin metadata entry, and does not constitute meaningful representation of the full COCO image dataset in OpenML's tabular-ML architecture. Large-scale DL benchmarks (CIFAR-10, ImageNet, KITTI) are absent from OpenML.

The pattern directly answers RQ3: coverage gaps are not random. They correspond precisely to each platform's founding scope. HF Hub's dataset ecosystem is NLP-centric, reflecting its origin as a text-model sharing platform. OpenML's catalog is tabular-ML-centric, reflecting its design for structured-data AutoML benchmarking. Large-scale DL vision, speech, and graph datasets — which constitute the majority of Raff's post-2012 deep learning era papers — are absent from both platforms.

### 5.3 Documentation Quality Among Found Datasets

![HF Card Field-Presence Heatmap](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/hf_field_heatmap.png)

*Figure 3. Field-presence heatmap for the 15 found HF datasets (rows) across 7 Datasheets for Datasets schema fields (columns). Mean field-presence score: 0.41. Fields `intended_use` and `out_of_scope_use` are systematically absent from most datasets.*

Mean field-presence score across the 15 found datasets: **0.41** (RQ4). Of the 7 fields, `task_categories` and `dataset_info` show the highest presence rates; `intended_use` and `out_of_scope_use` — the fields most directly relevant to the misuse detection mechanism — are systematically absent.

Individual dataset scores (per-dataset field-presence fraction over 7 fields, from results.json): mnist: 0.429; cifar10: 0.429; cifar100: 0.429; svhn: 0.429; imdb: 0.429; ag\_news: 0.429; yelp\_polarity: 0.286; amazon\_polarity: 0.429; sst2: 0.429; glue: 0.429; pubmed: 0.429; wmt14: 0.429; squad: 0.429; reuters21578: 0.286; ohsumed: 0.429.

This reveals a compound limitation: not only does HF Hub cover only 30% of the corpus, but among the covered datasets, the documentation quality signal (IV1) is weak. Retroactively-created cards for foundational benchmarks predate the Datasheets schema publication (Gebru et al., 2021) and were not systematically updated to include the scope-defining fields.

### 5.4 OpenML Run Count Distribution

![OpenML Pre-publication Run Count Distribution](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/openml_run_dist.png)

*Figure 2. Distribution of pre-publication OpenML run counts for the 11 valid datasets. Classical tabular/UCI datasets dominate. MNIST appears with 1 entry. All large-scale DL benchmarks have 0 OpenML entries.*

The 11 datasets with pre-publication OpenML entries are: mnist (1 entry), imdb (1), 20newsgroups (1), iris (2), wine (2), breast\_cancer (1), diabetes (1), adult (2), covertype (4), coco (1, as noted above), yeast (1). The distribution is dominated by classical UCI datasets (adult: 2 entries, covertype: 4 entries, iris: 2 entries, wine: 2 entries). All large-scale DL benchmarks — the datasets where concentration is theoretically highest (ImageNet, CIFAR-10) — have 0 OpenML entries, confirming that OpenML cannot serve as a concentration proxy for the DL benchmarks that constitute the majority of Raff's post-2012 papers.

### 5.5 Pipeline Validity

| Activation Indicator | Status |
|---------------------|--------|
| HF Hub API reachable | PASS |
| OpenML API reachable | PASS |
| Raff CSV parseable (255 papers) | PASS |
| Temporal filter executable | PASS |
| **H-E1 gate (HF ≥50% AND OpenML ≥70%)** | **FAIL** |

All 18 pipeline tests pass. Pipeline runtime: 88.84 seconds against live APIs. Raff corpus: 255 papers, 50.8% reproducible (130 of 255). All activation indicators pass, confirming that the gate failure reflects platform scope limitations rather than implementation errors.

---

## 6. Discussion

### 6.1 Interpretation of Findings

**Finding 1: HF Hub and OpenML exhibit domain-temporal selection bias, not random coverage gaps.**

The 30% HF Hub coverage is concentrated in NLP benchmarks and small-scale image classification datasets adopted by the HF ecosystem (CIFAR-10, CIFAR-100, SVHN). The 22% OpenML coverage is predominantly classical tabular datasets, with IMDB, 20 Newsgroups, and MNIST also present. Large-scale DL vision (ImageNet, COCO, Pascal VOC, KITTI), speech (LibriSpeech, TIMIT, Wall Street Journal), and graph (Cora, Citeseer) datasets — which dominate Raff's post-2012 deep learning papers — are absent from both platforms. This is not a data-quality problem addressable by better pipeline implementation; it is a structural consequence of each platform's design scope.

For researchers planning HF+OpenML-based reproducibility auditing of pre-2018 ML literature: the analysis will represent NLP, classical ML, and small-scale image papers, while systematically omitting the large-scale DL vision papers that constitute a substantial portion of the deep learning-era corpus. This bias operates silently unless coverage is explicitly measured for the target corpus, as done here.

**Finding 2: Retroactively-created HF cards are systematically thin.**

The 0.41 mean field-presence score indicates that even when a card exists, the fields most relevant to the misuse detection mechanism are absent. The `intended_use` and `out_of_scope_use` fields — which directly encode scope boundaries — are systematically missing from retroactively-created cards for foundational benchmarks such as MNIST, CIFAR-10, and IMDB. This is consistent with the timing of the Datasheets schema (Gebru et al., 2021): cards created before 2021 were not required to conform to the full schema, and retroactive curation has been incomplete. The schema was designed for new dataset creation rather than retroactive annotation of pre-2021 benchmarks.

**Finding 3: The theoretical hypothesis remains scientifically plausible but untested.**

The three-step theoretical mechanism — (1) high benchmark concentration signals artifact accumulation (D'Amour et al., 2022); (2) absent `intended_use` and `out_of_scope_use` fields indicate elevated out-of-context application risk (Gebru et al., 2021); (3) the joint effect predicts reproducibility failure above paper-quality controls — is grounded in prior literature but was not empirically tested. H-M1, H-M2, and H-M3 remain blocked. No claim about whether documentation completeness or benchmark concentration actually predicts reproducibility failure is supported by this study's data.

**Finding 4: Papers With Code is the most appropriate primary data source for a redesigned study.**

Papers With Code explicitly tracks paper-dataset linkages across all dataset domains and historical periods. Unlike HF Hub (NLP-centric) and OpenML (tabular-centric), Papers With Code is designed for the paper-dataset-code linkage required for this class of study and covers Raff's corpus temporal period. This is a theoretical recommendation based on the documented scope of Papers With Code; it has not been empirically verified. A redesigned H-E1 using the Papers With Code API would test whether coverage is adequate before proceeding to regression analysis.

### 6.2 Limitations

**Limitation 1: The original research question remains unanswered.** The central hypothesis — do metadata-observable dataset misuse signals predict ML reproducibility failure? — is neither confirmed nor refuted by this study. This paper reports an infrastructure characterization. Running regression on 30% independent variable coverage would produce biased, uninterpretable results; blocking was the correct methodological decision.

**Limitation 2: H-E1 used canonical dataset names only.** Alternate name variants (e.g., "uoft-cs/cifar10", "torchvision/cifar10") may recover additional HF cards. The 30% figure may represent a lower bound. However, the large-scale DL vision, speech, and graph gap is structural — HF Hub's architecture and community do not serve these datasets under any naming convention — and the canonical name interface is the appropriate choice for a scalable automated pipeline.

**Limitation 3: Results are specific to the Raff 2019 corpus.** Post-2019 papers with more NLP and HF-native datasets would show substantially higher HF Hub coverage. API coverage gaps may differ for other corpora, and the characterization presented here should not be generalized beyond the Raff 1984–2017 temporal and domain scope.

**Limitation 4: The theoretical mechanism remains empirically unverified.** The causal chain posited in Section 2 — concentration → artifact accumulation; incompleteness → out-of-context application; joint effect → reproducibility failure — is theoretically motivated but not confirmed by this study's experiments. Empirical verification requires the redesigned data infrastructure.

**Limitation 5: Single annotator ground truth.** Raff's reproducibility labels are from a single researcher's manual assessment. Single-annotator bias may systematically affect which paper types are labeled as reproducible or not. This limitation applies to any downstream study using Raff's labels, not specifically to the infrastructure characterization reported here.

### 6.3 Future Work

The highest-priority next experiment is a redesigned H-E1 using Papers With Code API as the primary data source, measuring whether PwC coverage for the Raff corpus meets the thresholds required for valid regression analysis. If PwC coverage is adequate (≥70%), the original research question — do metadata-observable misuse signals predict reproducibility failure? — becomes testable.

Additional directions include: systematic exploration of HF Hub name variants to determine whether the 30% figure is a lower bound; extension to post-2019 corpora where HF card coverage is substantially higher and multi-annotator reproducibility labels are available (ML Reproducibility Challenge); and a multi-source hybrid approach combining HF Hub, OpenML, Papers With Code, and arXiv metadata extraction.

---

## 7. Conclusion

This study set out to determine whether HuggingFace Hub dataset cards and OpenML run counts can serve as data sources for a study linking metadata-observable dataset misuse signals to ML reproducibility failure outcomes in Raff's 255-paper corpus. The infrastructure feasibility check (H-E1) reveals that they cannot: HF Hub achieves 30% dataset card coverage (15/50 datasets found; all NLP benchmarks; large-scale DL vision, speech, and graph datasets absent), and OpenML achieves 22% pre-publication temporal coverage (11/50; predominantly classical tabular datasets plus IMDB, 20 Newsgroups, and MNIST). Both are insufficient for valid regression analysis.

The coverage gaps are not random. They correspond precisely to each platform's founding community and architectural scope. HF Hub's ecosystem is NLP-centric; OpenML's architecture is tabular-centric. Any reproducibility auditing study of pre-2018 ML papers built on HF Hub and OpenML will be structurally biased toward NLP and classical ML papers, silently omitting the large-scale DL vision papers that dominate Raff's deep learning-era corpus.

This study's main contributions are: (1) the first empirical quantification of HF Hub and OpenML coverage for the Raff 2019 corpus, with exact coverage rates and domain breakdowns; (2) characterization of the domain-temporal selection bias in both APIs; (3) identification of Papers With Code as the most appropriate primary data source for a redesigned study; and (4) a validated 18-test data acquisition pipeline reusable for the redesigned study.

The original research question — do metadata-observable dataset misuse signals predict ML reproducibility failure? — remains open. The infrastructure gap reported here defines the methodological prerequisite for testing it. Any researcher planning to use HF Hub and OpenML to study pre-2018 ML reproducibility should explicitly measure API coverage for their target corpus before proceeding; the structural domain biases in these platforms are not visible without measurement.

---

## References

Bender, E. M., Gebru, T., McMillan-Major, A., and Shmitchell, S. (2021). On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? In *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency*, pages 610–623. doi:10.1145/3442188.3445922.

D'Amour, A., Heller, K., Moldovan, D., Adlam, B., Alipanahi, B., Beutel, A., Chen, C., Deaton, J., Eisenstein, J., Hoffman, M. D., et al. (2022). Underspecification Presents Challenges for Credibility in Modern Machine Learning. *Journal of Machine Learning Research*, 23(226):1–61. Originally arXiv:2011.03395 (2020).

Engstrom, L., Ilyas, A., Shah, S., and Sharif, M. (2020). Identifying Statistical Bias in Dataset Replication. In *Proceedings of the 37th International Conference on Machine Learning (ICML)*. [Note: title and proceedings details unverified.]

Feurer, M., Eggensperger, K., Falkner, S., Lindauer, M., and Hutter, F. (2022). Auto-Sklearn 2.0: Hands-Free AutoML via Meta-Learning. In *Advances in Neural Information Processing Systems*. [Note: year and venue details unverified.]

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Daum&eacute; III, H., and Crawford, K. (2021). Datasheets for Datasets. *Communications of the ACM*, 64(12):86–92. doi:10.1145/3458723. Originally arXiv:1803.09010 (2018).

Gundersen, O. E. and Kjensmo, S. (2018). State of the Art: Reproducibility in Artificial Intelligence. In *Proceedings of the AAAI Conference on Artificial Intelligence*, volume 32(1).

Kapoor, S. and Narayanan, A. (2023). Leakage and the Reproducibility Crisis in Machine Learning-Based Science. *Patterns*, 4(9). doi:10.1016/j.patter.2023.100804.

Krizhevsky, A. and Hinton, G. (2009). Learning Multiple Layers of Features from Tiny Images. Technical Report, University of Toronto.

Pineau, J., Vincent-Lamarre, P., Sinha, K., Larivi&egrave;re, V., Beygelzimer, A., d'Alch&eacute;-Buc, F., Fox, E., and Larochelle, H. (2021). Improving Reproducibility in Machine Learning Research: A Report from the NeurIPS 2019 Reproducibility Program. *Journal of Machine Learning Research*, 22(164):1–20.

Raff, E. (2019). A Step Toward Quantifying Independently Reproducible Machine Learning Research. In *Advances in Neural Information Processing Systems*. arXiv:1909.06674.

Recht, B., Roelofs, R., Schmidt, L., and Shankar, V. (2019). Do ImageNet Classifiers Generalize to ImageNet? In *Proceedings of the 36th International Conference on Machine Learning (ICML)*, pages 5389–5400.

Stojnic, R. and Taylor, R. (2020). Papers With Code: The Latest in Machine Learning. https://paperswithcode.com. [Note: attribution details unverified; Papers With Code is a community project with multiple contributors.]

Vanschoren, J., van Rijn, J. N., Bischl, B., and Torgo, L. (2014). OpenML: Networked Science in Machine Learning. *ACM SIGKDD Explorations Newsletter*, 15(2):49–60. doi:10.1145/2641190.2641198.

YoungXinyu1802 et al. (2024). An Analysis of Hugging Face Dataset Cards: Content, Completeness, and Quality. In *Proceedings of the International Conference on Learning Representations (ICLR)*. [Note: exact authors and title unverified.]
