# Experiment Brief: h-m1 — Friction Features Lower Entry Cost

**Date:** 2026-08-19  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Tier:** 1  
**Prerequisites:** h-e1 (VALIDATED)

---

## 1. Hypothesis Statement

**Statement:** Under scope of ML repositories with documented UX features, if platforms implement friction-reduction features (automated extraction, pre-filled templates, validation feedback, API access), then cognitive/time cost of metadata entry decreases for dataset creators, because automation eliminates manual typing, templates pre-populate fields, validation provides real-time feedback, and API enables programmatic submission.

**Rationale:** First mechanism step validating that friction-reduction features causally reduce entry cost. Tests whether tooling/automation objectively lowers burden compared to manual web forms.

**Gate:** MUST_WORK  
**Success Criteria:** API-uploaded datasets show higher completeness than manual-uploaded datasets (direction confirmed); difference ≥10 percentage points (effect size validation).

---

## 2. Experimental Design

### 2.1 Core Research Question

Does the **upload method** (API programmatic vs manual web form) on HuggingFace predict metadata completeness, serving as a proxy for entry cost reduction via friction-reduction features?

### 2.2 Variables

| Type | Variable | Operationalization |
|------|----------|-------------------|
| **Independent** | Upload method (binary) | API-programmatic vs manual web form |
| **Dependent** | Metadata completeness score (0-100%) | Mean presence rate across 6 target fields (dependencies, version, data_source_url, preprocessing_code, license, collection_date) |
| **Controlled** | Platform (HuggingFace only) | Within-platform comparison controls for platform-level confounds (age, community size, funding) |
| **Controlled** | Temporal snapshot (2026-08-19) | Same extraction timepoint for both groups |

### 2.3 Causal Mechanism

```
API Upload (programmatic metadata patterns)
    ↓
Lower friction (automation eliminates manual typing, enables bulk field population)
    ↓
Lower cognitive/time cost
    ↓
Higher metadata completeness
```

**Counterfactual:** Manual web form upload requires field-by-field manual entry → higher friction → lower completeness.

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Type:** standard (existing public datasets)  
**Source:** HuggingFace Datasets Hub (huggingface.co/datasets)  
**Access Method:** HuggingFace API via `datasets` library and `huggingface_hub` API

### 3.2 Dataset Characteristics

| Property | Specification |
|----------|--------------|
| **Platform** | HuggingFace Datasets Hub |
| **Sample size** | ~2,000 datasets total (stratified: ~1,000 API-uploaded, ~1,000 manual-uploaded) |
| **Sampling strategy** | Stratified random sampling per upload method |
| **Temporal scope** | Datasets uploaded before 2026-08-19 |
| **Metadata fields** | dependencies, version, data_source_url, preprocessing_code, license, collection_date |

### 3.3 Upload Method Detection

**Detection Strategy:** Programmatic upload patterns from HuggingFace dataset metadata

**API-Upload Indicators:**
1. **Dataset card creation patterns:** Datasets created via `push_to_hub()` include specific metadata patterns (e.g., auto-generated `dataset_info` YAML block from `datasets-cli test`)
2. **README structure:** API uploads often have minimal or template-based README vs manually-crafted descriptions
3. **Commit history:** API uploads show programmatic commit messages (e.g., "Upload dataset", "Update dataset" with huggingface_hub user-agent)
4. **File structure:** API uploads via `datasets` library create standardized file layouts (data/, dataset_info.json, README.md)

**Manual Upload Indicators:**
1. **Web form metadata UI usage:** Datasets with hand-filled metadata UI tags (visible in YAML frontmatter with specific formatting patterns)
2. **Drag-and-drop file uploads:** File structure reflects manual file additions (Files and versions tab timestamps)
3. **Custom README prose:** Manually-written dataset descriptions (varied formatting, non-template text)

**Validation:** Manual inspection of 100-sample pilot (50 per group) to confirm upload method classification accuracy (target >85% agreement).

### 3.4 Metadata Field Parsing Rules

Following h-e1 validated parsing rules:

| Field | Presence Criteria | Example |
|-------|------------------|---------|
| **dependencies** | Listed in requirements.txt, README, or dataset card YAML | `pandas>=1.0.0` |
| **version** | Version number in dataset card metadata or README | `v1.2.0`, `2023-05-01` |
| **data_source_url** | URL to original data source | `https://example.com/data` |
| **preprocessing_code** | Code snippets >50 chars + language keywords OR file extensions (.py, .R, .ipynb) | Python preprocessing script |
| **license** | License identifier in YAML or README | `MIT`, `Apache-2.0`, `CC-BY-4.0` |
| **collection_date** | Date/timestamp of data collection | `2023-05-01`, `May 2023` |

**Binary Presence:** Each field scored 0 (absent) or 1 (present).  
**Completeness Score:** Mean presence across 6 fields × 100 = percentage 0-100%.

---

## 4. Model/Algorithm Specification

### 4.1 Algorithm Type

**Binary field presence detection** via rule-based parsing (same as h-e1).

No machine learning model required — automated extraction pipeline with regex/keyword matching.

### 4.2 Implementation Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Dataset extraction** | HuggingFace `datasets` library + `huggingface_hub` API | Fetch dataset metadata, README content, commit history |
| **Upload method classifier** | Rule-based heuristics (commit patterns, file structure, metadata formatting) | Classify datasets as API vs manual upload |
| **Metadata parser** | Python regex + keyword matching | Detect presence of 6 target fields |
| **Statistical test** | Independent samples t-test (scipy.stats.ttest_ind) | Compare mean completeness scores |

### 4.3 Baseline Comparison

**No baseline required** — this is a within-platform comparison (API vs manual on HuggingFace).

h-m1 IS the baseline mechanism test for subsequent cross-platform comparisons (h-m2, h-m3).

---

## 5. Experimental Protocol

### 5.1 Data Collection Steps

**Step 1: Dataset Discovery**
- Query HuggingFace API for ~5,000 dataset IDs (broad sample)
- Filter: datasets with README.md and created before 2026-08-19
- Target: candidate pool of 3,000+ datasets

**Step 2: Upload Method Classification**
- For each dataset:
  - Fetch commit history via `huggingface_hub` API
  - Analyze README.md structure (template patterns, YAML formatting)
  - Check for `dataset_info.json` presence (API upload marker)
  - Classify as API-programmatic or manual-web-form
- Target: ~1,000 confirmed API uploads, ~1,000 confirmed manual uploads

**Step 3: Metadata Extraction**
- For each classified dataset:
  - Fetch README.md content
  - Apply h-e1 parsing rules for 6 target fields
  - Calculate completeness score (mean presence × 100)
- Output: `dataset_id, upload_method, completeness_score, field_presence_vector`

**Step 4: Validation Pilot**
- Manually inspect 100-sample subset (50 API, 50 manual)
- Verify upload method classification accuracy (target >85%)
- Verify parsing rule accuracy for completeness scores (target >90% agreement with manual review)

### 5.2 Statistical Analysis

**Hypothesis Test:** Independent samples t-test (two-tailed)

**Null Hypothesis (H0):** No difference in mean completeness between API and manual uploads (μ_API = μ_manual).

**Alternative Hypothesis (H1):** API uploads show higher completeness than manual uploads (μ_API > μ_manual, one-tailed for directional prediction).

**Test Configuration:**
- Significance level: α = 0.05
- Power: >0.80 (n~1,000 per group provides power >0.99 for detecting 10pp difference with d=0.5)
- Effect size: Cohen's d (standardized mean difference)

**Success Thresholds:**
- **Primary (MUST_WORK):** Direction confirmed (μ_API > μ_manual with p < 0.05)
- **Secondary:** Effect size ≥10 percentage points (absolute difference)

### 5.3 Sample Size Justification

**Target:** 1,000 datasets per upload method (2,000 total)

**Power Analysis:**
- Assumed effect size: 10 percentage points difference (small-medium effect, d~0.4)
- Significance: α = 0.05 (two-tailed)
- Power: With n=1,000 per group, power >0.95 for detecting 10pp difference
- Conservative: Accounts for potential classification noise (~85% upload method accuracy)

**Rationale:** Exceeds minimum required sample for detecting theoretically-predicted 20pp difference (from Phase 2A P3: API ≥70% vs manual ≤50%), provides buffer for smaller-than-expected effects.

---

## 6. Success Criteria & Failure Modes

### 6.1 Success Criteria (PoC)

**Primary (MUST_WORK gate):**
- Direction confirmed: API uploads show higher completeness than manual uploads (p < 0.05)
- Statistical significance: Independent samples t-test rejects H0 at α=0.05

**Secondary (Effect size validation):**
- Absolute difference ≥10 percentage points (e.g., API 65% vs manual 55%)
- Cohen's d ≥0.3 (small-to-medium effect size)

**Validation checks:**
- Upload method classification accuracy >85% (pilot validation)
- Parsing rule accuracy >90% (agreement with manual review)

### 6.2 Failure Modes & Contingencies

| Failure Mode | Probability | Mitigation | Response |
|--------------|------------|------------|----------|
| **No difference detected** | Medium | Within-platform controls for confounds | IF μ_API ≈ μ_manual: ABANDON causal mechanism claim, report null result, PIVOT to cross-platform analysis only (h-m2) |
| **Reverse direction** | Low | Upload method classifier validated | IF μ_API < μ_manual: STOP, inspect classification errors, re-validate upload detection heuristics |
| **Classification errors** | Medium | 100-sample pilot validation | IF pilot accuracy <85%: REFINE heuristics, add manual review for ambiguous cases |
| **Parsing misclassification** | Low | h-e1 validated parsing rules | IF parsing accuracy <90%: REUSE h-e1 stricter rules, reduce field set to high-confidence subset |
| **Effect size too small** | Medium | Large sample size (n=2,000) | IF difference <5pp: REPORT limited evidence, acknowledge weaker mechanism than predicted |

### 6.3 Gate Decision Logic

**MUST_WORK gate passes IF:**
- Primary criterion met (direction confirmed, p < 0.05)
- AND upload method validation >85% accurate
- AND parsing validation >90% accurate

**MUST_WORK gate fails IF:**
- No difference detected (p ≥ 0.05) OR reverse direction (μ_API < μ_manual)
- OR classification/parsing validation fails thresholds

**FAIL response:** STOP verification plan (h-m2, h-m3 blocked), reassess causal mechanism claim, consider alternative friction proxies.

---

## 7. Implementation Risks & Mitigations

### 7.1 Risk Assessment

| Risk ID | Risk | Severity | Likelihood | Mitigation |
|---------|------|----------|-----------|------------|
| **R1** | Upload method classification unreliable (heuristics misclassify datasets) | High | Medium | 100-sample pilot validation, refine heuristics based on pilot errors, add manual review for ambiguous cases |
| **R2** | Platform-level confounds despite within-platform comparison (e.g., API users are power-users with higher quality datasets regardless of friction) | Medium | Medium | Acknowledge limitation, frame as "friction feature availability" proxy not pure causal effect |
| **R3** | Small effect size (<10pp) undetectable despite large sample | Medium | Low | n=2,000 provides power >0.95 for 10pp, accept smaller effects as weaker evidence |
| **R4** | Temporal confounds (API upload feature availability changed over time) | Low | Low | Temporal snapshot (2026-08-19), all datasets collected same timepoint |
| **R5** | Parsing rule failures inherited from h-e1 | Low | Low | h-e1 validation passed (>90% accuracy), reuse same rules |

### 7.2 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| **A1** | Upload method is detectable from commit history + file structure patterns | GEO Uploader 2026 paper demonstrates programmatic upload pattern detection; HuggingFace commit messages include API user-agent strings | If heuristics <85% accurate: Add manual review, reduce sample size, or PIVOT to user surveys |
| **A2** | API upload is a valid proxy for "friction reduction" (automation/tooling usage) | HuggingFace docs show `push_to_hub()` enables batch metadata population, templates, automated validation; manual web form requires field-by-field entry | If API users manually fill fields anyway: Mechanism claim weakened, acknowledge limitation |
| **A3** | Within-platform comparison controls for platform-level confounds | Same community, same timepoint, same documentation; only upload method varies | If API users systematically different (power-users): Selection bias acknowledged, results interpreted as "friction feature availability" not pure causality |
| **A4** | h-e1 parsing rules transfer to HuggingFace-only dataset | h-e1 validated HuggingFace extraction (90%+ success), same platform, same fields | If parsing fails: Reuse h-e1 validation data, stricter rules |

---

## 8. Validation & Quality Assurance

### 8.1 Validation Protocol

**Upload Method Classification Validation:**
- Sample: 100 datasets (50 API, 50 manual) stratified random
- Manual review: Inspect commit history, README structure, file timestamps
- Metric: Classification accuracy (% agreement with manual ground truth)
- Threshold: >85% accuracy required to proceed

**Parsing Rule Validation:**
- Sample: 100 datasets (reuse upload method validation sample)
- Manual review: Read README, verify field presence/absence for 6 fields
- Metric: Parsing accuracy (% agreement with manual review across all fields)
- Threshold: >90% accuracy required (inherited from h-e1)

**Statistical Validity Checks:**
- Normality: Shapiro-Wilk test (if violated: use Mann-Whitney U instead of t-test)
- Equal variance: Levene's test (if violated: use Welch's t-test)
- Outliers: Identify extreme completeness scores (>95% or <5%), inspect for anomalies

### 8.2 Reproducibility

**Code Repository:**
- Extraction scripts: `scripts/h-m1/extract_hf_datasets.py`
- Upload classifier: `scripts/h-m1/classify_upload_method.py`
- Parsing pipeline: `scripts/h-m1/parse_metadata_fields.py` (reused from h-e1)
- Statistical analysis: `notebooks/h-m1_analysis.ipynb`

**Data Artifacts:**
- Raw dataset list: `data/h-m1/hf_dataset_ids.csv`
- Classified uploads: `data/h-m1/upload_method_classified.csv`
- Completeness scores: `data/h-m1/completeness_scores.csv`
- Validation sample: `data/h-m1/validation_pilot_100.csv`

**Random Seed:** 42 (all sampling operations)

---

## 9. Expected Outcomes

### 9.1 Primary Prediction (Phase 2A P3)

**Predicted:** API-uploaded datasets ≥70% completeness vs manual-uploaded datasets ≤50% completeness (≥20pp difference).

**Basis:** Phase 2A Section 1.6 P3 (within-platform comparison), Batzner 2026 (automated converters enabled 22k+ voluntary entries), GEO Uploader 2026 (automated upload reduced submission time 2-3h → 20s).

### 9.2 Threshold for PoC Success

**Minimum detectable effect:** 10 percentage points (conservative, half of predicted 20pp).

**Rationale:** Even 10pp difference demonstrates friction-reduction mechanism operates at meaningful scale, sufficient to support h-m2/h-m3 cross-platform tests.

### 9.3 Interpretation Scenarios

| Scenario | Outcome | Interpretation | Next Steps |
|----------|---------|----------------|-----------|
| **Strong support** | Difference ≥20pp, p<0.01 | Friction mechanism validated, causal evidence strong | Proceed to h-m2 (cross-platform) |
| **Moderate support** | Difference 10-20pp, p<0.05 | Friction mechanism operates but weaker than predicted | Proceed to h-m2, document effect size limitation |
| **Weak support** | Difference <10pp, p<0.05 | Direction correct but effect small, may lack practical significance | Consider STOP, reassess mechanism claim |
| **No support** | p≥0.05 or reverse direction | Causal mechanism fails, platform confounds dominate | STOP, ABANDON friction-reduction hypothesis |

---

## 10. Timeline & Resources

### 10.1 Timeline (2 weeks)

| Week | Phase | Tasks |
|------|-------|-------|
| **Week 1** | Data collection | Query HuggingFace API (days 1-2), classify upload methods (days 3-4), extract metadata (day 5) |
| **Week 2** | Validation & analysis | Pilot validation (days 1-2), statistical analysis (days 3-4), report writing (day 5) |

**Total Duration:** 10 working days (2 weeks)

### 10.2 Resource Requirements

**Computational:**
- HuggingFace API access (free, rate-limited to ~1,000 requests/hour)
- Metadata extraction: ~2,000 datasets × 5 API calls each = 10,000 API calls (~10 hours with rate limits)
- Statistical analysis: lightweight (scipy t-test, <1 minute runtime)

**Manual Effort:**
- Upload method validation: 100 datasets × 3 minutes each = 5 hours
- Parsing validation: 100 datasets × 2 minutes per field × 6 fields = 20 hours (can reuse h-e1 validation if same datasets)
- Analysis + reporting: 8 hours

**Dependencies:**
- Python libraries: `datasets`, `huggingface_hub`, `pandas`, `scipy`, `matplotlib`
- h-e1 validation dataset (if available, reduces manual effort by ~15 hours)

---

## 11. Archon KB Insights (Unavailable)

**Note:** Archon KB connection unavailable during experiment design. No past experiment examples retrieved.

**Fallback:** Design based on:
1. **GEO Uploader 2026** (Semantic Scholar): Automated GEO repository submission reduced entry time 2-3h → 20s, demonstrated friction reduction via programmatic upload
2. **HuggingFace API documentation** (Exa code search): `push_to_hub()` method enables batch metadata population, template-based README generation
3. **Phase 2A predictions** (02b_verification_plan.md): P3 within-platform comparison (API vs manual)

---

## 12. Code Search Insights (Exa)

**Key findings from HuggingFace documentation:**

1. **API upload method (`push_to_hub()`):**
   - Enables programmatic metadata population via Python dictionary
   - Auto-generates `dataset_info` YAML block from dataset structure
   - Supports batch field updates (no manual field-by-field entry)
   - Commit messages include `huggingface_hub` user-agent

2. **Manual upload method (web UI):**
   - Drag-and-drop file upload via Files and versions tab
   - Metadata UI with manual field selection (license, language, task categories)
   - Hand-written README via browser editor
   - "Import dataset card template" link for pre-filled structure

3. **Upload method detection signals:**
   - Commit history: API uploads show `huggingface_hub` commits vs browser commits
   - File structure: API uploads create `dataset_info.json`, standardized `data/` folder
   - README formatting: API uploads use auto-generated YAML vs manually-crafted prose

**Detection feasibility:** HIGH (multiple distinct signals available via HuggingFace API).

---

## 13. Related Work

### 13.1 Supporting Evidence

**GEO Uploader (Domi et al. 2026):**
- Automated GEO repository submission reduced entry time from 2-3 hours to <20 seconds
- Key features: parallel upload processing, automated MD5 validation, template-based metadata completion
- Demonstrated friction reduction via automation eliminates manual data entry burden

**Batzner 2026 (Unified Evaluation Schema):**
- Automated converters enabled 22,235+ model evaluation entries (voluntary contribution)
- Friction-reduction mechanism: automated ingestion vs manual submission
- Large-scale voluntary completion supports hypothesis that automation enables higher contribution rates

**Yang 2024 (HuggingFace Metadata Completeness):**
- Single-platform analysis (7,433 datasets) showed heterogeneous completion patterns
- Subsections vary: Dataset Description/Structure completed more than Considerations
- Suggests tooling/automation access variability drives completeness (aligns with h-m1 mechanism)

### 13.2 Novelty

h-m1 is the **first within-platform controlled comparison** testing friction-reduction mechanism via upload method proxy. Prior work (Yang 2024) measured completion heterogeneity but did not isolate friction features as causal variable. h-m1 controls for platform-level confounds (community, age, funding) by comparing API vs manual uploads on same platform (HuggingFace).

---

## 14. Summary

**Hypothesis:** API-uploaded HuggingFace datasets show higher metadata completeness than manual-uploaded datasets, demonstrating friction-reduction features lower entry cost.

**Key Innovation:** Within-platform comparison (API vs manual) controls for platform confounds, provides causal evidence stronger than cross-platform correlation (h-m2).

**Gate:** MUST_WORK — h-m1 PASS required for h-m2/h-m3 to proceed.

**PoC Threshold:** Direction confirmed (μ_API > μ_manual, p<0.05) + effect size ≥10pp.

**Risk:** Upload method classification reliability (mitigated by 100-sample pilot validation).

**Timeline:** 2 weeks (data collection week 1, validation + analysis week 2).

---

**Status:** Experiment brief COMPLETED  
**Next Step:** Phase 3 Implementation Planning (PRD, Architecture, Epic tasks)
