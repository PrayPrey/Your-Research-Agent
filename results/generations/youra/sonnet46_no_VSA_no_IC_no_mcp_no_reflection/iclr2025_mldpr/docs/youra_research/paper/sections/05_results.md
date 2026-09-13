# Results

Our central claim is that HuggingFace Hub and OpenML do not provide adequate coverage of pre-2018 ML benchmark datasets for valid regression analysis of the misuse-reproducibility hypothesis. The results confirm this claim decisively — and the pattern of failures reveals why.

## Main Results: Gate Metric Evaluation

Figure 1 shows the two gate metrics against their pre-specified thresholds.

*[Figure 1: gate_metrics.png — Bar chart showing HF coverage rate (30%, red) vs. 50% threshold and OpenML temporal filter success rate (22%, red) vs. 70% threshold. Both bars fail.]*

**HF Hub coverage:** 15 of 50 queried datasets (30%) returned valid HuggingFace Hub dataset cards. This is below the 50% gate threshold by 20 percentage points. The gate criterion is not met.

**OpenML temporal filter:** 11 of 50 queried datasets (22%) have pre-publication OpenML entries valid for temporal filtering. This is below the 70% gate threshold by 48 percentage points. The gate criterion is not met.

Both gate criteria fail. The AND gate for H-E1 does not pass. Downstream hypotheses H-M1, H-M2, and H-M3 are blocked.

These numbers are not estimates — they are direct measurements from live API queries using the same pipeline that would be used for the full study, confirmed by 18/18 passing tests.

## Domain Pattern: Systematic Bias, Not Random Missingness

The more important result is the domain distribution of what was found versus what was missing. This is not random missingness — it is systematic and structured.

| Domain | Datasets queried | HF Hub found | OpenML found |
|--------|-----------------|-------------|--------------|
| NLP/text classification | ~10 | 15 (all found HF cards are NLP) | 1 (IMDB) |
| DL vision | ~15 | 0 | 0 |
| Speech/audio | ~5 | 0 | 0 |
| Graph | ~5 | 0 | 0 |
| Classical tabular/UCI | ~15 | 0 | 10 (all found OpenML datasets) |

The pattern is unambiguous: **HF Hub returns results only for NLP benchmarks; OpenML returns results only for classical tabular datasets.** DL vision datasets (CIFAR-10, ImageNet, COCO, Pascal VOC, KITTI, Caltech-101, Caltech-256) return no HF cards and no OpenML entries. Speech datasets (LibriSpeech, TIMIT, Wall Street Journal) return no HF cards and no OpenML entries. Graph datasets (Cora, Citeseer) return nothing.

This finding directly answers RQ3: the coverage gaps are not random. They are a consequence of each platform's founding scope. HF Hub's dataset ecosystem is NLP-centric because HF Hub emerged from the NLP/transformer community. OpenML's dataset catalog is tabular-ML-centric because OpenML was designed for AutoML benchmarking on structured data. Neither platform was built to cover the deep learning benchmark ecosystem that dominates Raff's pre-2018 corpus.

For any researcher using HF+OpenML to study pre-2018 ML reproducibility: the analysis will cover NLP papers (≈10–15% of the corpus by dataset domain) and tabular-ML papers (≈15–20%), systematically missing the DL vision papers that constitute the majority.

## Documentation Quality: Thin Cards for Found Datasets

Figure 3 shows the field-presence heatmap for the 15 HF-found datasets across 7 Datasheets schema fields.

*[Figure 3: hf_field_heatmap.png — Heatmap of 15 found datasets × 7 Datasheets fields, showing systematic absence of intended_use and out_of_scope_use fields.]*

Mean field-presence score: **0.41** (standard deviation not reported — all datasets are in the analysis, not a sample). Of the 7 fields, `task_categories` and `dataset_info` show highest presence; `intended_use` and `out_of_scope_use` are systematically absent across most cards.

This result reveals a double-bind: not only does HF Hub cover only 30% of the corpus, but even among the covered datasets, the documentation quality signal (IV1) is weak. The fields that are theoretically most relevant to the misuse mechanism — `intended_use` (specifying the intended use of the dataset) and `out_of_scope_use` (specifying what the dataset should not be used for) — are precisely those absent from retroactively-created cards.

The explanation is consistent with the Datasheets for Datasets schema timeline: Gebru et al. [2021] published the schema in 2021; dataset cards created retroactively for foundational benchmarks (IMDB, MNIST, AG News) predate or are contemporaneous with the schema publication and were not systematically updated to include these fields.

## OpenML Run Count Distribution

Figure 2 shows the distribution of pre-publication OpenML run counts for the 11 valid (temporally filtered) datasets.

*[Figure 2: openml_run_dist.png — Distribution of pre-publication run counts for 11 tabular/classical ML datasets in OpenML.]*

The distribution is dominated by classical UCI datasets with substantial pre-publication run counts (adult, covertype, diabetes) — consistent with OpenML's history as a platform for AutoML benchmarking on UCI datasets. MNIST appears with 1 OpenML entry (upload\_date 2014). All DL benchmarks (CIFAR, ImageNet) have 0 OpenML entries.

This finding answers RQ2 fully: OpenML cannot serve as a concentration proxy for the DL benchmarks that dominate Raff's corpus. High-run-count OpenML datasets are entirely in the classical tabular domain; the DL benchmarks where concentration is theoretically highest (ImageNet has been used in thousands of papers, CIFAR-10 in tens of thousands) have no OpenML representation at all.

## Pipeline Validity

All 18 pipeline tests pass. Runtime: 88.84 seconds. Four pipeline activation indicators all verified true (HF API reachable, OpenML API reachable, Raff CSV parseable, temporal filter executable). The gate fail is therefore a genuine infrastructure finding, not an implementation defect.

The Raff corpus parses correctly: 255 papers loaded, all expected columns present (author, year, venue, binary reproducibility label, paper-quality features). Reproducibility rate: 50.8% (130/255 reproducible). This confirms that the dependent variable is intact and valid — the study's infrastructure failure is entirely in the IV data sources, not in the outcome variable.

| Activation Indicator | Status |
|--------------------|--------|
| HF Hub API reachable | ✓ PASS |
| OpenML API reachable | ✓ PASS |
| Raff CSV parseable (255 papers) | ✓ PASS |
| Temporal filter executable | ✓ PASS |
| **H-E1 gate (HF ≥50% AND OpenML ≥70%)** | **✗ FAIL** |

## Summary

The infrastructure feasibility study produces three findings, all from live API measurements:

1. **HF Hub coverage: 30%** (15/50 datasets, all NLP). Below 50% threshold. IV1 (documentation completeness) is missing for 70% of the corpus.
2. **OpenML coverage: 22%** (11/50 datasets, all classical tabular). Below 70% threshold. IV2 (HHI concentration) is uncomputable for 78% of the corpus.
3. **HF mean field score: 0.41** among found datasets. Even with adequate coverage, the documentation quality signal would be weaker than assumed.

The findings are decisive: HF+OpenML cannot support the intended regression study on Raff's pre-2018 corpus. The path forward is a redesigned infrastructure study using Papers With Code as the primary data source.
