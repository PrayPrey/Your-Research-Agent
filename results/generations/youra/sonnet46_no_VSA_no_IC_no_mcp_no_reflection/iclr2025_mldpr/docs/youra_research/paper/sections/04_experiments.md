# Experimental Setup

We design four research questions to test the infrastructure feasibility of our proposed misuse-reproducibility auditing study. Each question maps to a specific claim from the Introduction.

**RQ1 (C1):** What fraction of the 50 unique benchmark datasets in Raff's corpus have HuggingFace Hub dataset cards under canonical dataset names?

**RQ2 (C1):** What fraction have pre-publication OpenML entries suitable for Herfindahl-Hirschman Index computation?

**RQ3 (C2):** Do the coverage gaps follow systematic domain and temporal patterns, or are they random?

**RQ4 (C1/C3):** Among the HF cards that do exist, what is the mean field-presence score across the Datasheets for Datasets schema fields?

## Corpus

**Raff 2019 Reproducibility Corpus:** 255 ML papers from top venues (NeurIPS, ICML, ICLR, JMLR), published 1984–2017, with binary reproducibility labels from manual re-implementation. We extract 50 unique benchmark datasets from the corpus's paper-dataset linkage annotations (the same dataset names as appear in Raff's original analysis). The corpus is chosen because it is the standard labeled dataset for ML reproducibility auditing research and provides the dependent variable (binary reproducibility outcome) for the intended downstream regression study.

| Corpus Property | Value |
|----------------|-------|
| Total papers | 255 |
| Reproducible | 130 (50.8%) |
| Not reproducible | 125 (49.2%) |
| Unique datasets queried | 50 |
| Year range | 1984–2017 |
| Venues | NeurIPS, ICML, ICLR, JMLR |

The 50 queried datasets span domain types representative of the corpus: DL vision (CIFAR-10, CIFAR-100, ImageNet, COCO, Pascal VOC, KITTI, Caltech-101/256), NLP/text (IMDB, SST-2, AG News, SQuAD, GLUE, 20 Newsgroups), speech (LibriSpeech, TIMIT, Wall Street Journal), graph (Cora, Citeseer), and classical tabular/UCI (iris, adult, covertype, diabetes, wine, breast\_cancer).

## Data Sources

**HuggingFace Hub API:** `huggingface_hub` Python library, `DatasetCard.load(name)` method. Canonical dataset names used (no namespace prefix exploration). Rate limit: 1.0s sleep between requests. 403 (authentication required) and 404 (not found) errors explicitly distinguished.

**OpenML Python API:** `openml.datasets.list_datasets(output_format='dataframe')` for a single bulk fetch of all available datasets. Client-side temporal filter: `upload_date_year < paper_publication_year`. Dataset name matching: exact canonical match against Raff dataset names.

**Baseline comparison:** No ML baselines — this is an infrastructure feasibility study, not a comparative ML experiment. The relevant "comparison" is the pre-specified threshold (50% for HF, 70% for OpenML) against the measured coverage rate.

## Implementation Details

All code implemented in a single `pipeline.py` script (five classes: RaffParser, HFCoverageChecker, OpenMLTemporalChecker, MetricsAggregator, Visualizer). No GPU required; the pipeline is a data acquisition and measurement script.

| Parameter | Value |
|-----------|-------|
| HF rate limit sleep | 1.0 second |
| HF field set | intended\_use, out\_of\_scope\_use, limitations, license, task\_categories, dataset\_info, provenance (7 fields) |
| HF token | None (unauthenticated) |
| OpenML query mode | Bulk fetch (single API call) |
| OpenML temporal filter | `upload_date_year < paper_publication_year` |
| Total runtime | 88.84 seconds |
| Test suite | 18 pytest tests, all live (no mocking) |

## Evaluation Metrics

**HF coverage rate:** Fraction of 50 queried datasets returning a valid HF card (non-null DatasetCard object). Gate threshold: ≥0.50. This is the minimum coverage required for IV1 (documentation completeness) to be computable for a representative fraction of Raff's corpus.

**OpenML temporal filter success rate:** Fraction of 50 queried datasets with at least one pre-publication OpenML entry (upload\_date\_year < paper\_publication\_year). Gate threshold: ≥0.70. This is the minimum coverage required for IV2 (HHI concentration) to be computable for a representative fraction of the corpus.

**HF mean field-presence score:** For found HF cards, mean fraction of 7 Datasheets schema fields present. Reports documentation quality conditional on card existence.

**Pipeline activation indicators:** Four binary indicators verifying that the pipeline reached each component successfully (HF API reachable, OpenML API reachable, Raff CSV parseable, temporal filter executable). Gate pass/fail is meaningful only when all four indicators are true.

Gate logic: AND of (HF coverage rate ≥ 0.50) AND (OpenML temporal filter success rate ≥ 0.70). Both must hold for the EXISTENCE gate to pass and downstream mechanism hypotheses to proceed.
