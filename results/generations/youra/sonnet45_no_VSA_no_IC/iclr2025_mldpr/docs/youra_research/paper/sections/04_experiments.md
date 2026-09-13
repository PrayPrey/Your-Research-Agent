# Experimental Setup

We designed experiments to answer three research questions testing our friction-completeness hypothesis through a hierarchical verification structure.

## Research Questions

**RQ1 (Cross-Platform Optional Fields):** Do platforms with higher friction scores show higher optional metadata presence rates?

**RQ2 (Enforcement Mechanism Validation):** Do required fields show high presence regardless of friction score, validating enforcement as distinct mechanism?

**RQ3 (Within-Platform Causal Evidence):** Do friction features causally reduce entry cost when controlling for platform-level confounds?

## Sub-Hypothesis Structure

Our verification follows a 4-hypothesis structure with gate conditions:

**H-E1 (Existence, MUST_WORK):** Platform friction-reduction features are objectively measurable from public documentation, and 10,000+ metadata records are extractable via APIs/scraping within 2-week timeframe.

**H-M1 (Mechanism, MUST_WORK):** Friction-reduction features causally reduce cognitive/time cost of metadata entry (tested via within-HuggingFace API vs manual upload comparison).

**H-M2 (Mechanism, SHOULD_WORK):** Lower friction increases voluntary completion rates for optional fields (tested via cross-platform presence comparison).

**H-M3 (Mechanism, SHOULD_WORK):** Enforcement and friction-reduction operate as magnitude-differentiated mechanisms — optional fields vary by friction (high friction <15%, low friction >60%), required fields remain high (~90%) regardless of friction.

## Datasets and Sampling

| Platform | Friction Score | Sample Size | Sampling Method | Justification |
|----------|---------------|-------------|-----------------|---------------|
| HuggingFace | 3 | 7,000 | Stratified random | Largest repository (~60k datasets), highest friction score |
| OpenML | 2 | 2,500 | Stratified random | Intermediate friction, mature API, ~20k datasets |
| UCI | 0 | 500 | Census (all) | Smallest repository (~600 datasets), zero friction baseline |

**Total:** 10,000 datasets across 3 platforms, stratified proportionally to platform size.

**Rationale:** This distribution ensures (1) statistical power for cross-platform comparison (n=10,000 provides power >0.99 for detecting 20pp+ differences), (2) representativeness (proportional sampling avoids over-representing small platforms), (3) variance in friction scores (0, 2, 3 enables correlation detection).

## Baselines

We compare against two baseline expectations:

**Null Hypothesis (H0):** Optional field presence rates are uniform (~40-50%) across platforms regardless of friction score. No significant difference between high-friction (HuggingFace) and low-friction (UCI) platforms.

**Yang 2024 Heterogeneity Benchmark:** HuggingFace subsection-level completion variability serves as reference — some sections 80%+, others <30%. We expect optional fields to show similar heterogeneity patterns if friction matters.

No external method baselines exist (first friction-UX study). We validate methodology feasibility through h-e1 pilot extraction before testing mechanism hypotheses.

## Implementation Details

**Extraction Infrastructure:**
- OpenML: `openml-python` library (v0.14.2), batch API requests, XML parsing
- HuggingFace: `huggingface_hub.list_datasets()` (v0.23.0), YAML frontmatter parsing
- UCI: BeautifulSoup (v4.12.0) web scraping, HTML table extraction

**Parsing Rules (Examples):**
- `preprocessing_code`: Regex `(python|julia|R)` + length >50 chars OR file extension `\.(py|R|ipynb)$`
- `data_source_url`: Regex `https?://[^\s]+` excluding placeholders `(example\.com|TODO|N/A)`
- `license`: Length >5 chars AND not in `[None, N/A, Unknown, TODO, TBD]`

**Validation Protocol:**
- 100-sample manual review (stratified 33-33-34 per platform)
- Inter-rater agreement target >90% (Cohen's kappa or percentage agreement)
- If accuracy <80% → refine parsing rules, re-validate

**Compute Resources:**
- Metadata extraction: ~6.0 hours estimated for 10k datasets (API rate limits accommodated)
- Parsing + analysis: Standard Python scientific stack (pandas, scipy, statsmodels)
- No GPU required (metadata-only analysis)

## Evaluation Metrics

**Primary Metric:** Presence rate (0-100%) = (datasets with field present) / (total datasets) × 100

**Statistical Tests:**
- Cross-platform comparison: Chi-squared test (categorical: present/absent × platform), Cramér's V effect size
- Within-platform comparison: Welch t-test (continuous: completeness scores), Cohen's d effect size
- Significance threshold: α=0.05 (two-sided tests)
- Effect size thresholds: Small (Cohen's h=0.2, d=0.2), Medium (h=0.5, d=0.5), Large (h=0.8, d=0.8)

**Secondary Metrics:**
- Gradient validation: Monotonic ordering (UCI < OpenML < HuggingFace) for optional fields
- Coefficient of Variation (CV): Measure presence rate stability for required vs optional fields
- Semantic accuracy: Manual validation of 100-sample subset (target >80%)

## Success Criteria

**H-E1 Success:** Friction scores assigned (HF=3, OpenML=2, UCI=0) with objective binary criteria AND pilot extraction achieves >80% success rate for OpenML/HF, >70% for UCI AND parsing accuracy >90% in manual validation.

**H-M1 Success:** API-uploaded datasets show higher completeness than manual-uploaded datasets (direction confirmed, μ_API > μ_manual) AND effect size ≥10pp AND p<0.05.

**H-M2 Success:** HuggingFace shows ≥60% presence for at least 2 of 3 optional fields (preprocessing_code, data_source_url, collection_date) AND UCI shows <15% presence for same fields AND difference ≥45pp AND p<0.05.

**H-M3 Success:** All 3 platforms show 80-95% presence for both license AND version fields AND no significant cross-platform difference for required fields (p>0.10) AND variance low (CV <0.20).

## Experimental Controls

To ensure fair cross-platform comparison:

**Temporal Control:** Single-timepoint extraction (2026-08-19 snapshot) eliminates temporal drift from platform evolution or dataset updates.

**Schema Normalization:** Explicit semantic mapping protocol documented (OpenML `original_data_url` → HF `source_url` → UCI `data source link` normalized to `data_source_url`). Manual validation (50-sample) confirms >80% semantic agreement.

**Parsing Consistency:** Same parsing rules applied to all platforms (no platform-specific thresholds). Validation sample stratified across platforms to detect platform-specific parsing failures.

**Sampling Stratification:** Proportional to platform size (HF 70%, OpenML 25%, UCI 5%) ensures representativeness while maintaining statistical power. Random sampling within each platform avoids selection bias.

**Upload Method Classification (H-M1 Only):** API vs manual classification validated via commit history analysis, README structure patterns, and metadata field formats. Target >85% classification accuracy before completeness comparison.
