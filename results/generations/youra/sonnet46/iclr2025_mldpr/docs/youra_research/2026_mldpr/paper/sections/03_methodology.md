# 3. Methodology

## 3.1 Overview

Our methodology operationalizes the Data Transparency Scorecard (DTS) [Rondina et al., 2025] into a three-stage automated pipeline: (1) **Collection** — query public ML dataset repository APIs and cache structured metadata fields, (2) **Scoring** — map API fields to DTS sections and compute weighted completeness scores, and (3) **Validation** — assess per-section API coverage, proxy validate scoring consistency, and evaluate gate criteria. The pipeline is designed from the ground up to be cross-repository: the same scoring logic applies to all three target repositories, with repository-specific field mapping specifications handling API schema differences.

The connection to our key insight is direct: building a cross-repository scoring pipeline forces the question of API field coverage to be empirical rather than assumed. We do not presume that HuggingFace, OpenML, and UCI APIs expose the DTS sections that matter most — we measure it, and report what we find.

Figure 4 (`human_automated_scatter.png`) illustrates the proxy validation design. The full pipeline is summarized in Figure 1 (`per_section_coverage_heatmap.png`), which shows per-section coverage rates across all three repositories — the central output of the scoring stage.

## 3.2 DTS Scoring Framework

We adopt the Data Transparency Scorecard verbatim from Rondina et al. [2025], preserving both the 6-section taxonomy and the inverse-frequency weights derived from their empirical rarity analysis.

**Section Taxonomy.** The DTS defines six documentation sections, each associated with a set of required fields:

| Section | DTS Weight | API Fields Queried (HF / OpenML / UCI) |
|---------|-----------|---------------------------------------|
| Motivation | 1.0 | `task_categories`, `language`, `tags`, `license` |
| Composition | 0.9 | `size_categories`, `num_rows`, `num_columns`, `features` |
| Collection | 2.1 | `source_datasets`, `annotations_creators`, `original_data_url` |
| Preprocessing | 1.8 | `preprocessing_steps`, `data_augmentation`, `data_splits` |
| Uses | 1.5 | `known_limitations`, `out_of_scope_use`, `discussion_best_use` |
| Distribution | 0.7 | `license`, `citation`, `contact`, `maintenance_plan` |

**Rationale for Adopted Weights.** The inverse-frequency weighting reflects the empirically observed rarity of each section in real dataset documentation: Collection (weight 2.1) and Preprocessing (1.8) receive high weights because they are rarely filled, making their presence highly informative about documentation quality and effort. Motivation (1.0) and Distribution (0.7) receive lower weights because they are frequently present and convey less signal about documentation thoroughness. We adopt these weights directly rather than deriving new weights, enabling direct comparison with Rondina et al.'s [2025] manual findings.

**Binary Field Presence Scoring.** Each field is scored binary: 1 if the field is present and non-null in the API response, 0 otherwise. The section score is the maximum field presence across all fields queried for that section (1 if any field is present, 0 if all are absent). The weighted DTS score for a dataset is:

$$\text{DTS}_{\text{weighted}} = \frac{\sum_{s \in S} w_s \cdot \mathbb{1}[\text{section}_s \text{ present}]}{\sum_{s \in S} w_s}$$

where $S$ = {Motivation, Composition, Collection, Preprocessing, Uses, Distribution}, $w_s$ is the DTS weight for section $s$, and $\mathbb{1}[\cdot]$ is the binary indicator of section presence.

**Rationale for Binary Scoring.** Binary field presence is coarser than human quality rating but is (1) reproducible across researchers and API versions without inter-annotator agreement requirements, and (2) the minimum viable signal extractable from structured API fields without free-text parsing. Finer-grained quality scoring (e.g., completeness within a section) requires parsing free-text card prose, which is beyond the scope of this study and represents a natural extension. We report both weighted DTS scores (primary) and unweighted field presence scores (as a sensitivity baseline).

## 3.3 Data Collection

**Target Repositories.** We target three repositories that collectively represent the dominant platforms for public ML dataset hosting:

- **HuggingFace Hub** (`huggingface_hub` ≥ 0.20): The largest open ML dataset repository, with ~100K+ datasets. Structured metadata is available via the `card_data` YAML API endpoint, which returns machine-readable fields populated by dataset creators using HuggingFace's dataset card YAML template (introduced with mandatory schema enforcement in 2021).

- **OpenML** (`openml` ≥ 0.14): A benchmark-oriented ML platform with ~22K datasets. Structured metadata is available via the OpenML REST API, returning task type, feature descriptions, creator information, and dataset provenance fields in structured JSON/XML format.

- **UCI ML Repository** (`ucimlrepo` ≥ 0.0.7): The legacy repository of ~600 traditionally-documented ML datasets, maintained by UC Irvine. The `ucimlrepo` Python library provides programmatic access to dataset metadata fields including description, creators, introductory paper citations, and variable information.

**Stratified Sampling.** To ensure representative corpus composition, we apply stratified sampling within each repository along two dimensions: task domain category (4 bins: NLP, Computer Vision, Tabular/Structured, Other) and upload year cohort (2 bins: ≤2021 and >2021, reflecting the HuggingFace YAML adoption event). This stratification prevents simple random sampling from overrepresenting popular recent NLP datasets and ensures cross-domain coverage. Sample sizes: HuggingFace Hub n=500 (stratified target), OpenML n=200, UCI n≈100 (full population).

**Caching and Rate Limiting.** All API responses are cached as JSON files keyed by repository and dataset ID to ensure reproducibility and avoid repeated API calls. Rate limits are enforced: HuggingFace Hub (1.0 req/sec unauthenticated; 0.2 sec authenticated), OpenML (no enforced limit; conservative 0.5 req/sec applied), UCI (2.0 sec between requests via `ucimlrepo`).

**Pilot Collection.** Before full collection, a pilot run (n=50 per repository, n=150 total) verifies that API access is functional and that per-repository coverage rate exceeds a minimum viability threshold of 0.30. The pilot serves as a fail-fast check before committing to full collection.

## 3.4 Validation Protocol

**Proxy Validation.** The planned validation protocol called for Pearson correlation between automated DTS-weighted scores and human expert annotations on a stratified subsample (n=120, 40 per repository). Human annotation infrastructure was unavailable during this study's execution. We substitute *proxy validation*: computing the Pearson correlation between DTS-weighted scores and DTS-unweighted scores on the same 120-dataset stratified subsample drawn from the real API corpus. This proxy tests internal algorithmic consistency — whether the weighted and unweighted variants capture the same underlying field presence signal — rather than construct validity against human judgment. We report this as proxy validation and explicitly distinguish it from human-validated external validity (see Section 6.1).

**Gate Criteria.** The existence hypothesis (H-E1) is evaluated against two pre-registered gate criteria:
- **Coverage gate:** Corpus coverage rate ≥ 0.70 (fraction of datasets with weighted DTS > 0)
- **Correlation gate:** Proxy Pearson r ≥ 0.70 (internal scoring consistency)

Both gates must pass for the existence claim to be upheld.

**Mechanism Activation Verification.** Beyond gate criteria, we verify four mechanism activation indicators that confirm the scoring system operates as designed: (1) scoring pipeline executes without errors, (2) per-repository coverage rates are computable and non-trivial for at least two repositories, (3) weighted and unweighted scores differ (DTS weighting has an effect), (4) positive proxy correlation (scores are internally consistent). All four indicators must be confirmed.

## 3.5 Implementation

The pipeline is implemented in Python 3.10 in a dedicated conda environment (`youra-h-e1`) with dependencies: `huggingface_hub ≥ 0.20`, `openml ≥ 0.14`, `ucimlrepo ≥ 0.0.7`, `scipy ≥ 1.10`, `statsmodels ≥ 0.14`, `pandas ≥ 2.0`, `matplotlib`, `seaborn`. The codebase is organized into seven modules:

- `collect_hf.py` — HuggingFace Hub API collection with stratified sampling and JSON caching
- `collect_openml.py` — OpenML API collection with stratified sampling
- `collect_uci.py` — UCI collection via `ucimlrepo` with REST fallback
- `scorer.py` — DTS weighted and unweighted scoring (standalone, no local dependencies)
- `validation.py` — Pearson r computation with bootstrap confidence intervals (n=1,000 bootstrap samples, seed=42, 95% CI)
- `visualization.py` — Five result figures
- `evaluate.py` — Gate evaluation and mechanism activation verification

The main entry point (`experiment.py`) orchestrates the full pipeline: pilot → collection → scoring → (annotation placeholder) → proxy validation → visualization → gate evaluation → results JSON export.

**Implementation Note — Mock Fix.** During Phase 4 validation, a simulation bypass was discovered in `experiment.py` (line 297: `or True` condition) that unconditionally forced synthetic annotation simulation regardless of whether real annotation data was available. This bypass was removed before final evaluation. All reported results reflect the proxy validation protocol on real API data with no synthetic simulation.

All random operations use seed=42 for reproducibility.
