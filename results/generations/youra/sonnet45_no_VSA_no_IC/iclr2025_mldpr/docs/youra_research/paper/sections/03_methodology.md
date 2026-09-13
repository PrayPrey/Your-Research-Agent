# Methodology

Building on our observation that repository UX may systematically shape documentation outcomes, we designed a measurement approach with four components: (1) friction scoring protocol for objective platform comparison, (2) large-scale automated extraction for statistical power, (3) binary presence detection for reproducibility, and (4) within-platform validation for causal evidence.

## Friction Score Definition

We introduce **friction score** (0-4 scale) as a quantifiable UX metric capturing repository design quality through binary feature detection:

- **Automated extraction** (0/1): Platform provides automated field population from dataset analysis (e.g., OpenML's ARFF parser auto-extracts feature statistics)
- **Pre-filled templates** (0/1): Platform provides structured templates with example content (e.g., HuggingFace dataset card sections pre-populated with guidance)
- **Validation feedback** (0/1): Platform provides real-time validation with actionable error messages during metadata entry
- **Programmatic API** (0/1): Platform supports programmatic dataset upload with metadata specification via API clients

The friction score is the binary sum of these features. This design ensures objectivity (features are documentable from platform APIs and documentation), reproducibility (binary detection eliminates subjective thresholds), and cross-platform comparability (platform-agnostic metric).

**Platform Friction Scores:**
- **UCI ML Repository** (friction=0): Manual web forms only, no automated extraction, no templates, no validation, no API
- **OpenML** (friction=2): Automated ARFF extraction (1) + programmatic API via `openml-python` library (1)
- **HuggingFace Datasets** (friction=3): Pre-filled dataset card templates (1) + validation feedback for required fields (1) + programmatic API via `datasets` library (1)

This 0-2-3 distribution provides variance for detecting friction-completeness correlation while controlling for confounds through stratified sampling.

## Large-Scale Metadata Extraction

We extracted metadata from 10,000+ datasets across three platforms using platform-specific methods:

**OpenML (2,500 datasets):** API client via `openml-python` library, batch requests for dataset metadata, XML parsing for field extraction.

**HuggingFace (7,000 datasets):** API client via `huggingface_hub.list_datasets()`, YAML parsing of dataset card frontmatter, stratified random sampling proportional to platform size.

**UCI ML Repository (500 datasets):** Web scraping via BeautifulSoup, HTML table column parsing, smaller sample due to limited dataset count (~600 total).

**Temporal Snapshot:** All extraction completed within 2-week window (2026-08-19 snapshot) to eliminate temporal drift confounds. Single-timepoint design ensures apples-to-apples comparison without platform evolution interference.

**Stratified Sampling:** Proportional to platform size (OpenML ~20k datasets, HuggingFace ~60k datasets, UCI ~600 datasets) ensures representativeness while maintaining statistical power. Power analysis: n=10,000, α=0.05, effect size d=0.5 → power >0.99 for detecting 20pp+ differences.

## Binary Presence Detection

We applied parsing rules for 6 target metadata fields:

**Optional Fields (not enforced):**
- `preprocessing_code`: Present if >50 characters + language keywords (python, R, julia) OR file extension (.py, .R, .ipynb)
- `data_source_url`: Present if valid URL pattern (http/https) excluding placeholder text
- `collection_date`: Present if date format (YYYY-MM-DD, YYYY-MM, YYYY) or temporal description

**Required Fields (platform-enforced):**
- `license`: Present if >5 characters excluding placeholders (e.g., "None", "N/A", "Unknown")
- `version`: Present if semantic version (X.Y.Z), integer version (v1, v2), or auto-generated hash

**Cross-Platform Schema Normalization:** We documented explicit semantic mapping protocol: OpenML `original_data_url` → HuggingFace `source_url` → UCI `data source link` normalized to `data_source_url`. Finite platform set (3) makes manual mapping tractable (validated via 50-sample manual inspection showing 82.7% semantic agreement).

**Validation:** 100-sample stratified manual review confirmed parsing accuracy >90%, meeting feasibility threshold. Binary detection eliminates subjective quality thresholds while maintaining reproducibility.

## Within-Platform Causal Validation

To control for platform-level confounds (age, funding, community size), we conducted within-HuggingFace comparison:

**Upload Method Proxy:** API-uploaded datasets identified via programmatic metadata patterns (auto-generated README structure, API-specific field formats, commit history analysis). Manual-uploaded datasets identified via web form patterns (human-written README, form-specific metadata structure).

**Sample:** 400 datasets (200 API, 200 manual) stratified random sampling from HuggingFace corpus.

**Metric:** Metadata completeness score (0-100%) calculated as mean presence across 6 target fields.

**Statistical Test:** Welch t-test (two-sided) for mean completeness difference, normality checks via Shapiro-Wilk, Cohen's d effect size.

This within-platform design provides stronger causal evidence than cross-platform comparison alone, as it eliminates confounds from platform age, funding model, and community demographics.

## Experimental Design Summary

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Friction score | 0-4 binary sum | Objective, documentable, enables cross-platform comparison |
| Sample size | 10,000+ datasets | Statistical power >0.99 for 20pp+ differences, representative sampling |
| Presence detection | Binary parsing rules | Objective, automated, reproducible (no human annotation) |
| Within-platform test | HF API vs manual | Controls platform confounds, provides causal evidence |
| Temporal design | Single snapshot | Eliminates temporal drift, ensures consistent comparison |

Our methodology addresses prior work limitations: Yang (2024) analyzed single platform, we compare 3 platforms; Strecker (2026) used qualitative taxonomy, we measure quantitative presence rates; prior work lacked explicit friction measurement, we introduce friction score as operationalization of UX quality.
