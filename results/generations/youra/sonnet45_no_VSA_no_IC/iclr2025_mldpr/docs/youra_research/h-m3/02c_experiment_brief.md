# Experiment Brief: h-m3 — Enforcement vs Friction Mechanism Distinction

**Date:** 2026-08-19  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Tier:** 1  
**Prerequisites:** h-m2 (VALIDATED - HF>UCI for all 3 optional fields, 45-61pp differences, p<0.0001)

---

## 1. Hypothesis Statement

**Statement:** Under scope of metadata fields classified as optional (not enforced) vs required (enforced by platform validation), if friction-reduction mechanism operates as proposed, then optional field presence rates vary by friction score (high friction platforms <15%, low friction platforms >60%) while required field presence rates remain consistently high (~90%) across all platforms regardless of friction level, because enforcement mechanism (required field blocking) operates independently of UX tooling for must-have fields.

**Rationale:** Third mechanism step validating enforcement vs friction-reduction distinction. Tests whether two independent mechanisms drive completeness: enforcement for required fields (platform blocks upload without field), friction reduction for optional fields (tooling enables voluntary completion).

**Gate:** SHOULD_WORK  
**Success Criteria:** Required fields show ~80-95% presence across all platforms (no friction effect, p>0.10); contrast with optional field variance confirmed in h-m2 (significant cross-platform difference).

---

## 2. Experimental Design

### 2.1 Core Research Question

Do **required metadata fields** (enforced by platform validation) exhibit **consistent high presence rates** (~90%) across platforms **regardless of friction score**, while **optional fields** (validated in h-m2) vary significantly by friction level (HF>60%, UCI<15%)?

This tests the hypothesis that **enforcement** and **friction reduction** are **independent mechanisms**:
- Enforcement: Platform blocks upload if required field empty → high presence regardless of UX quality
- Friction reduction: Good UX enables voluntary completion → only affects optional fields

### 2.2 Variables

| Type | Variable | Operationalization |
|------|----------|-------------------|
| **Independent** | Field type (optional vs required) | Optional: preprocessing_code, data_source_url, collection_date (NOT enforced); Required: license, version (enforced by validation) |
| **Independent** | Platform friction score (0-4 scale) | HF=3 (templates + validation + API), OpenML=2 (API + basic templates), UCI=0 (manual web forms only) |
| **Dependent** | Field presence rate (0-100%) | Percentage of datasets with field present, calculated per field per platform |
| **Controlled** | Same dataset sample | Reuse exact 10k+ sample from h-m2 extraction (no re-sampling) |
| **Controlled** | Same parsing rules | Apply h-m2 parsing rules to required fields (license present if non-empty string, version present if semantic version pattern) |
| **Controlled** | Same timepoint | h-m2 extraction timestamp (2026-08-19) |

### 2.3 Causal Mechanism: Two Independent Pathways

```
PATHWAY 1: Enforcement (Required Fields)
Platform enforces field → Upload blocked if empty → Creator fills field to publish → High presence (~90%) REGARDLESS of friction score

PATHWAY 2: Friction Reduction (Optional Fields, validated h-m2)
Platform has low friction UX → Lower entry cost → Creator voluntarily completes → High presence (>60%)
Platform has high friction UX → High entry cost → Creator skips optional field → Low presence (<15%)
```

**Key Prediction:** If these mechanisms are independent, then:
- Required fields: NO friction effect (HF≈OpenML≈UCI, all ~90%, p>0.10)
- Optional fields: FRICTION effect (HF>60%, UCI<15%, validated h-m2, p<0.0001)

**Counterfactual:** If enforcement and friction are NOT independent (single mechanism hypothesis), then required fields would also vary by friction score (HF>OpenML>UCI).

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Type:** standard (reuse h-m2 extraction)  
**Sources:**
- **HuggingFace Datasets Hub** (huggingface.co/datasets) — friction=3, n=6,500
- **OpenML** (openml.org) — friction=2, n=2,990
- **UCI ML Repository** (archive.ics.uci.edu/ml/datasets) — friction=0, n=500

**Reuse Justification:**
- h-m2 already extracted 10k+ datasets (same temporal snapshot, same platforms)
- Required field presence can be calculated from SAME metadata records (no new extraction needed)
- Eliminates temporal drift (h-m2 extraction = 2026-08-19, h-m3 uses identical sample)
- Statistically stronger (paired comparison: same datasets evaluated for optional vs required)

**Access Methods:**
- No new API calls required
- Read cached h-m2 extraction results from `h-m2/data/raw/`
- Apply required field parsing rules to existing metadata records

### 3.2 Dataset Characteristics

| Property | Specification |
|----------|--------------|
| **Total sample size** | 9,990 datasets (h-m2 extraction) |
| **Platform distribution** | HF: 6,500 (65%), OpenML: 2,990 (30%), UCI: 500 (5%) |
| **Sampling strategy** | Stratified random (completed in h-m2) |
| **Temporal scope** | Datasets extracted 2026-08-19 (h-m2 timepoint) |
| **Target fields (required)** | license, version |

**Parsing Results from h-m2:**
- Total valid metadata records: 9,990
- Parsing accuracy: 90.0% (h-m2 validation)
- Semantic validation: 82.7% (h-m2 validation)

### 3.3 Field Classification: Required vs Optional

**Required Fields (h-m3 focus):**

| Field | Enforcement Mechanism | Cross-Platform Status |
|-------|----------------------|----------------------|
| **license** | HF: Dropdown selection required (blocking); OpenML: Required metadata field (upload fails without); UCI: Not enforced (web form allows empty) | HF=enforced, OpenML=enforced, UCI=NOT enforced |
| **version** | HF: Auto-generated semantic version (always present); OpenML: Required metadata field (upload fails without); UCI: Not enforced (web form allows empty) | HF=auto-enforced, OpenML=enforced, UCI=NOT enforced |

**CRITICAL NUANCE:** Enforcement varies by platform:
- HF+OpenML: Both fields enforced → expect ~90% presence
- UCI: Neither field enforced → if friction mechanism operates alone, expect <15%; if enforcement mechanism dominates, expect ~90% anyway (dataset creators know license is standard practice)

**Optional Fields (h-m2 validated, reference for contrast):**

| Field | h-m2 Results | Status |
|-------|-------------|--------|
| **preprocessing_code** | HF 61.0%, UCI 0.0%, diff=61.0pp, p=0.0000 | Validated: friction effect confirmed |
| **data_source_url** | HF 66.2%, UCI 15.2%, diff=51.0pp, p=0.0000 | Validated: friction effect confirmed |
| **collection_date** | HF 55.4%, UCI 10.0%, diff=45.4pp, p=0.0000 | Validated: friction effect confirmed |

### 3.4 Cross-Platform Field Mapping: Required Fields

Platforms define required fields differently. Explicit semantic mapping:

| Platform | license Field | version Field |
|----------|--------------|--------------|
| **HuggingFace** | YAML frontmatter `license: <SPDX-id>` OR README dropdown selection | Auto-generated semantic version in dataset card metadata (`version: "1.0.0"`) |
| **OpenML** | XML metadata `<oml:licence>` field (required upload field) | XML metadata `<oml:version>` field (required, integer incremental) |
| **UCI** | HTML page `<div class="license">` OR plaintext in description (NOT enforced) | HTML page version label OR implicit version via last-modified date (NOT enforced) |

**Parsing Rules (Parallel to h-m2 Optional Field Rules):**

**license Presence Detection:**
```python
def is_license_present(metadata):
    # HuggingFace: YAML frontmatter license field OR README dropdown
    if platform == 'HF':
        return metadata.get('license') not in [None, '', 'unknown', 'other']
    
    # OpenML: XML <oml:licence> field (required field)
    if platform == 'OpenML':
        return metadata.get('licence') not in [None, '']
    
    # UCI: HTML div.license OR plaintext keyword (NOT enforced)
    if platform == 'UCI':
        license_text = metadata.get('license', '')
        # Present if contains recognizable license keywords
        license_keywords = ['CC-BY', 'MIT', 'Apache', 'GPL', 'BSD', 'Public Domain', 'Creative Commons']
        return any(kw.lower() in license_text.lower() for kw in license_keywords) and len(license_text) > 10
    
    return False
```

**version Presence Detection:**
```python
def is_version_present(metadata):
    # HuggingFace: Auto-generated semantic version (always present in dataset card)
    if platform == 'HF':
        version_str = metadata.get('version', '')
        # Present if semantic version pattern (e.g., "1.0.0")
        import re
        return bool(re.match(r'^\d+\.\d+\.\d+', version_str))
    
    # OpenML: Required integer version field
    if platform == 'OpenML':
        return metadata.get('version') is not None
    
    # UCI: HTML version label OR last-modified date (NOT enforced)
    if platform == 'UCI':
        version_text = metadata.get('version', '')
        # Present if contains version keywords or date pattern
        version_keywords = ['version', 'v1', 'v2', 'release', 'updated']
        has_keyword = any(kw.lower() in version_text.lower() for kw in version_keywords)
        has_date = bool(re.search(r'\d{4}-\d{2}-\d{2}', version_text))  # YYYY-MM-DD pattern
        return (has_keyword or has_date) and len(version_text) > 5
    
    return False
```

**Validation:** Manual review of 100-sample stratified subset (same methodology as h-m2 parsing validation, target >85% agreement).

---

## 4. Model/Algorithm Specification

### 4.1 Statistical Test

**Primary Test:** Chi-squared test of independence (2×3 contingency table per field)

**Contingency Table Structure:**
```
                    HuggingFace  OpenML  UCI
license present          ?         ?      ?
license absent           ?         ?      ?

                    HuggingFace  OpenML  UCI
version present          ?         ?      ?
version absent           ?         ?      ?
```

**Null Hypothesis (H0):** Required field presence rates are independent of platform (no friction effect).

**Alternative Hypothesis (H1):** Required field presence rates vary by platform (friction effect detected, contradicts hypothesis).

**Test Implementation:**
```python
from scipy.stats import chi2_contingency
import pandas as pd

# License field contingency table
license_table = pd.DataFrame({
    'HF': [hf_license_present, hf_license_absent],
    'OpenML': [openml_license_present, openml_license_absent],
    'UCI': [uci_license_present, uci_license_absent]
}, index=['present', 'absent'])

chi2_stat, p_value, dof, expected = chi2_contingency(license_table)

# Success criterion: p > 0.10 (NO significant difference across platforms)
if p_value > 0.10:
    print(f"PASS: No friction effect detected (p={p_value:.4f})")
else:
    print(f"FAIL: Friction effect detected for required field (p={p_value:.4f})")
```

**Repeat for version field.**

### 4.2 Comparison with h-m2 Optional Fields

**Contrast Test:** Compare required field variance (h-m3) vs optional field variance (h-m2)

**Metric:** Coefficient of variation (CV) of presence rates across platforms
```python
import numpy as np

# Required field (license) presence rates
required_rates = [hf_license_pct, openml_license_pct, uci_license_pct]
required_cv = np.std(required_rates) / np.mean(required_rates)

# Optional field (preprocessing_code, h-m2 result) presence rates
optional_rates = [61.0, 0.0, 0.0]  # HF, OpenML, UCI from h-m2
optional_cv = np.std(optional_rates) / np.mean(optional_rates)

# Success criterion: required_cv << optional_cv (required fields stable, optional fields vary)
if required_cv < 0.20 and optional_cv > 1.0:
    print(f"PASS: Required fields stable (CV={required_cv:.2f}), optional fields vary (CV={optional_cv:.2f})")
else:
    print(f"PARTIAL: Required CV={required_cv:.2f}, Optional CV={optional_cv:.2f}")
```

### 4.3 Effect Size Calculation

**Cramér's V:** Measure of association strength between field type and platform

```python
from scipy.stats.contingency import association

# Cramér's V for required fields (expect weak association, V < 0.15)
cramers_v_license = association(license_table, method='cramer')
cramers_v_version = association(version_table, method='cramer')

# Compare with optional fields from h-m2 (expect strong association, V > 0.50)
# Success criterion: V_required < 0.20, V_optional > 0.40
```

---

## 5. Baseline Specification

### 5.1 Baseline Methods

**No direct baselines for h-m3 (novel mechanism distinction test).** But reference points:

| Reference | Finding | Relation to h-m3 |
|-----------|---------|------------------|
| **Yang 2024** | HuggingFace subsection-level completion heterogeneity (7,433 datasets); Dataset Description sections more complete than Considerations sections | Single platform, no required vs optional distinction. h-m3 extends to cross-platform comparison with explicit enforcement classification. |
| **Strecker 2026** | Metadata conflicts in 8 geoscience repositories; both implementation and inter-standard conflicts drive incomplete DataCite metadata | Qualitative taxonomy, non-ML domain. h-m3 quantifies presence rates for ML repositories with explicit enforcement vs voluntary distinction. |
| **h-m2 (VALIDATED)** | Optional field presence rates: HF 55-66%, OpenML 0-15%, UCI 0-15%; all p<0.0001 | Establishes friction effect for optional fields. h-m3 tests whether enforcement mechanism operates independently (required fields stable). |

### 5.2 Expected Performance: Required vs Optional Fields

| Field Type | Platform | Expected Presence Rate | Rationale |
|-----------|----------|----------------------|-----------|
| **Required (license)** | HuggingFace | 85-95% | Enforced dropdown selection (blocking upload) |
| **Required (license)** | OpenML | 85-95% | Required metadata field (upload fails without) |
| **Required (license)** | UCI | 70-85% | NOT enforced, but dataset creators know license is standard practice (social norm, not platform enforcement) |
| **Required (version)** | HuggingFace | 90-100% | Auto-generated semantic version (always present) |
| **Required (version)** | OpenML | 85-95% | Required integer version field |
| **Required (version)** | UCI | 60-80% | NOT enforced, implicit version via last-modified date (lower than license due to less standardization) |
| **Optional (preprocessing_code, h-m2)** | HuggingFace | 61.0% (validated) | Friction reduction enables voluntary completion |
| **Optional (preprocessing_code, h-m2)** | UCI | 0.0% (validated) | High friction discourages voluntary completion |

**Key Prediction:** Required field rates show **small cross-platform variance** (CV<0.20) vs optional field rates show **large cross-platform variance** (CV>1.0, validated h-m2).

### 5.3 Success Criteria (Gate: SHOULD_WORK)

**Primary Criteria:**

1. **No friction effect for required fields (p>0.10):** Chi-squared test shows no significant cross-platform difference for license AND version fields
2. **Contrast with optional fields:** Required field CV < 0.20 (stable) vs optional field CV > 1.0 (variable, h-m2 validated)
3. **High absolute presence for required fields:** Mean presence rate across platforms ≥80% for both license and version

**Secondary Criteria:**

4. **Direction check:** HF≥OpenML≥UCI for required fields (weak gradient allowed, but NOT 45pp+ differences like optional fields)
5. **Effect size:** Cramér's V < 0.20 for required fields (weak association with platform) vs V > 0.40 for optional fields (strong association, h-m2)

**Failure Modes:**

- **FAIL:** Required fields show significant cross-platform difference (p<0.05) with large effect size (V>0.40) → Enforcement and friction are NOT independent, single mechanism hypothesis
- **PARTIAL:** Required fields show moderate difference (p<0.10) or moderate CV (0.20-0.50) → Enforcement dominates but friction still influences (mechanisms partially coupled)

---

## 6. Experimental Procedure

### 6.1 Data Preparation (Reuse h-m2 Extraction)

**Step 1:** Load h-m2 cached metadata records
```bash
# No new extraction required
INPUT_DIR=h-m2/data/raw/
OUTPUT_DIR=h-m3/data/results/

# Expected files from h-m2:
# - huggingface_metadata.json (6,500 records)
# - openml_metadata.json (2,990 records)
# - uci_metadata.json (500 records)
```

**Step 2:** Verify data integrity (same sample as h-m2)
```python
import json

# Load h-m2 extraction
with open('h-m2/data/raw/huggingface_metadata.json') as f:
    hf_data = json.load(f)

# Sanity checks
assert len(hf_data) == 6500, "Sample size mismatch"
assert all('license' in rec or 'version' in rec for rec in hf_data), "Required fields missing"

print(f"Loaded {len(hf_data)} HF records from h-m2 extraction")
```

**Step 3:** Apply required field parsing rules
```python
def parse_required_fields(metadata_records, platform):
    results = []
    for record in metadata_records:
        results.append({
            'dataset_id': record['id'],
            'platform': platform,
            'license_present': is_license_present(record),
            'version_present': is_version_present(record),
        })
    return results

hf_required = parse_required_fields(hf_data, 'HF')
openml_required = parse_required_fields(openml_data, 'OpenML')
uci_required = parse_required_fields(uci_data, 'UCI')
```

### 6.2 Validation: Parsing Accuracy Check

**Manual Review (100-sample stratified subset):**

```python
import random

# Stratified sample: 50 HF, 30 OpenML, 20 UCI
validation_sample = (
    random.sample(hf_required, 50) +
    random.sample(openml_required, 30) +
    random.sample(uci_required, 20)
)

# Export for manual review
with open('h-m3/validation_sample.json', 'w') as f:
    json.dump(validation_sample, f, indent=2)

# MANUAL STEP: Human reviewer checks each record
# - license_present: correct yes/no?
# - version_present: correct yes/no?
# Target accuracy: >85% agreement (same threshold as h-m2)
```

**If accuracy <85%:** Refine parsing rules and re-validate (same mitigation as h-m2 R1).

### 6.3 Statistical Analysis

**Step 4:** Calculate presence rates per platform
```python
import pandas as pd

# License presence rates
hf_license_rate = sum(r['license_present'] for r in hf_required) / len(hf_required) * 100
openml_license_rate = sum(r['license_present'] for r in openml_required) / len(openml_required) * 100
uci_license_rate = sum(r['license_present'] for r in uci_required) / len(uci_required) * 100

print(f"License presence: HF {hf_license_rate:.1f}%, OpenML {openml_license_rate:.1f}%, UCI {uci_license_rate:.1f}%")

# Version presence rates
hf_version_rate = sum(r['version_present'] for r in hf_required) / len(hf_required) * 100
openml_version_rate = sum(r['version_present'] for r in openml_required) / len(openml_required) * 100
uci_version_rate = sum(r['version_present'] for r in uci_required) / len(uci_required) * 100

print(f"Version presence: HF {hf_version_rate:.1f}%, OpenML {openml_version_rate:.1f}%, UCI {uci_version_rate:.1f}%")
```

**Step 5:** Chi-squared test (per field)
```python
from scipy.stats import chi2_contingency

# License contingency table
license_table = pd.DataFrame({
    'HF': [sum(r['license_present'] for r in hf_required), 
           sum(not r['license_present'] for r in hf_required)],
    'OpenML': [sum(r['license_present'] for r in openml_required), 
               sum(not r['license_present'] for r in openml_required)],
    'UCI': [sum(r['license_present'] for r in uci_required), 
            sum(not r['license_present'] for r in uci_required)]
}, index=['present', 'absent'])

chi2_license, p_license, dof_license, expected_license = chi2_contingency(license_table)

print(f"License chi-squared test: χ²={chi2_license:.2f}, p={p_license:.4f}, dof={dof_license}")
print(f"Expected frequencies:\n{expected_license}")

# Success check: p > 0.10 (no friction effect)
if p_license > 0.10:
    print("✓ PASS: No significant friction effect for license field")
else:
    print("✗ FAIL: Significant friction effect detected for license field")

# Repeat for version field
version_table = pd.DataFrame({
    'HF': [sum(r['version_present'] for r in hf_required), 
           sum(not r['version_present'] for r in hf_required)],
    'OpenML': [sum(r['version_present'] for r in openml_required), 
               sum(not r['version_present'] for r in openml_required)],
    'UCI': [sum(r['version_present'] for r in uci_required), 
            sum(not r['version_present'] for r in uci_required)]
}, index=['present', 'absent'])

chi2_version, p_version, dof_version, expected_version = chi2_contingency(version_table)

print(f"Version chi-squared test: χ²={chi2_version:.2f}, p={p_version:.4f}, dof={dof_version}")
```

**Step 6:** Effect size and variance comparison
```python
from scipy.stats.contingency import association
import numpy as np

# Cramér's V
cramers_v_license = association(license_table, method='cramer')
cramers_v_version = association(version_table, method='cramer')

print(f"Cramér's V: license={cramers_v_license:.3f}, version={cramers_v_version:.3f}")
print(f"Interpretation: V < 0.20 = weak association (expected for required fields)")

# Coefficient of variation (CV)
required_cv_license = np.std([hf_license_rate, openml_license_rate, uci_license_rate]) / np.mean([hf_license_rate, openml_license_rate, uci_license_rate])
required_cv_version = np.std([hf_version_rate, openml_version_rate, uci_version_rate]) / np.mean([hf_version_rate, openml_version_rate, uci_version_rate])

# h-m2 optional field CV (reference)
optional_cv_preprocessing = np.std([61.0, 0.0, 0.0]) / np.mean([61.0, 0.0, 0.0])

print(f"CV: required_license={required_cv_license:.3f}, required_version={required_cv_version:.3f}, optional_preprocessing={optional_cv_preprocessing:.3f}")
print(f"Success criterion: required CV < 0.20, optional CV > 1.0")
```

### 6.4 Result Synthesis

**Step 7:** Generate validation report
```python
results_summary = {
    'hypothesis_id': 'h-m3',
    'status': 'VALIDATED' if (p_license > 0.10 and p_version > 0.10 and required_cv_license < 0.20) else 'PARTIAL',
    'required_fields': {
        'license': {
            'hf_presence_pct': hf_license_rate,
            'openml_presence_pct': openml_license_rate,
            'uci_presence_pct': uci_license_rate,
            'chi2_statistic': chi2_license,
            'p_value': p_license,
            'cramers_v': cramers_v_license,
            'cv': required_cv_license
        },
        'version': {
            'hf_presence_pct': hf_version_rate,
            'openml_presence_pct': openml_version_rate,
            'uci_presence_pct': uci_version_rate,
            'chi2_statistic': chi2_version,
            'p_value': p_version,
            'cramers_v': cramers_v_version,
            'cv': required_cv_version
        }
    },
    'contrast_with_h-m2': {
        'optional_field_cv': optional_cv_preprocessing,
        'required_vs_optional_cv_ratio': required_cv_license / optional_cv_preprocessing
    },
    'key_findings': [
        f"Required field (license) presence: HF {hf_license_rate:.1f}%, OpenML {openml_license_rate:.1f}%, UCI {uci_license_rate:.1f}%",
        f"Required field (version) presence: HF {hf_version_rate:.1f}%, OpenML {openml_version_rate:.1f}%, UCI {uci_version_rate:.1f}%",
        f"Chi-squared test: license p={p_license:.4f}, version p={p_version:.4f}",
        f"Effect size: license V={cramers_v_license:.3f}, version V={cramers_v_version:.3f}",
        f"Variance: required CV={required_cv_license:.3f}, optional CV={optional_cv_preprocessing:.3f}",
        "Mechanism distinction: " + ("VALIDATED" if p_license > 0.10 and p_version > 0.10 else "NOT VALIDATED")
    ]
}

with open('h-m3/data/results/validation_summary.json', 'w') as f:
    json.dump(results_summary, f, indent=2)
```

---

## 7. Evaluation Metrics

### 7.1 Primary Metrics (Gate: SHOULD_WORK)

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Chi-squared p-value (license)** | p > 0.10 | No significant friction effect for required field |
| **Chi-squared p-value (version)** | p > 0.10 | No significant friction effect for required field |
| **Coefficient of variation (required)** | CV < 0.20 | Required fields stable across platforms |
| **Mean presence rate (required)** | ≥80% | High absolute presence due to enforcement |

### 7.2 Secondary Metrics (Mechanism Distinction)

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Cramér's V (required)** | V < 0.20 | Weak association between required fields and platform |
| **Cramér's V (optional, h-m2)** | V > 0.40 | Strong association between optional fields and platform (reference) |
| **CV ratio (required/optional)** | < 0.25 | Required field variance much smaller than optional field variance |

### 7.3 Success/Failure Thresholds

**PASS (VALIDATED):**
- All primary metrics met (p>0.10, CV<0.20, mean≥80%)
- Mechanism distinction clear (required CV << optional CV, ratio<0.25)
- Conclusion: Enforcement and friction reduction are independent mechanisms

**PARTIAL:**
- Primary metrics partially met (1-2 fields p>0.10, CV=0.20-0.40)
- Mechanism distinction unclear (required CV moderately lower than optional CV, ratio=0.25-0.50)
- Conclusion: Enforcement dominates but friction still influences (mechanisms partially coupled)

**FAIL:**
- Primary metrics not met (p<0.05, CV>0.40)
- No mechanism distinction (required CV similar to optional CV, ratio>0.50)
- Conclusion: Single mechanism hypothesis (enforcement and friction conflated)

---

## 8. Implementation Plan

### 8.1 Task Breakdown (Epic-Level)

**Epic 1: Data Preparation (Tier 1)**
- Task 1.1: Load h-m2 cached metadata records (HF, OpenML, UCI)
- Task 1.2: Verify data integrity (sample size, field availability)
- Task 1.3: Implement required field parsing rules (license, version)
- **Duration:** 2 hours
- **Dependencies:** h-m2 extraction completed

**Epic 2: Validation (Tier 1)**
- Task 2.1: Generate 100-sample stratified validation subset
- Task 2.2: Manual review of parsing accuracy (license, version)
- Task 2.3: Calculate parsing agreement rate (target >85%)
- Task 2.4: Refine parsing rules if accuracy <85%
- **Duration:** 3 hours
- **Dependencies:** Epic 1 completed

**Epic 3: Statistical Analysis (Tier 1)**
- Task 3.1: Calculate presence rates per platform (license, version)
- Task 3.2: Chi-squared test (license field)
- Task 3.3: Chi-squared test (version field)
- Task 3.4: Effect size calculation (Cramér's V)
- Task 3.5: Variance comparison (CV for required vs optional)
- **Duration:** 2 hours
- **Dependencies:** Epic 2 completed

**Epic 4: Result Synthesis (Tier 1)**
- Task 4.1: Generate validation summary JSON
- Task 4.2: Create comparison table (required vs optional fields)
- Task 4.3: Visualize presence rates (bar chart per field)
- Task 4.4: Write validation report (04_validation.md)
- **Duration:** 2 hours
- **Dependencies:** Epic 3 completed

**Total Duration:** 9 hours (1 day)  
**Complexity Tier:** 1 (reuses h-m2 extraction, straightforward statistical comparison)

### 8.2 Resource Requirements

**Data:**
- h-m2 cached metadata (9,990 records) — already extracted
- No new API calls required

**Compute:**
- Statistical tests: scipy.stats (chi2_contingency, association)
- Data manipulation: pandas
- Visualization: matplotlib/seaborn

**Manual Effort:**
- Parsing validation: 3 hours (100-sample review)

**Output Artifacts:**
- `h-m3/data/results/required_field_presence.csv` (presence rates per platform)
- `h-m3/data/results/validation_summary.json` (statistical test results)
- `h-m3/data/results/comparison_table.md` (required vs optional contrast)
- `h-m3/04_validation.md` (full validation report)

### 8.3 Risk Mitigation

**Risk R1: Parsing Misclassification (license, version)**
- **Mitigation:** Manual validation (100 samples, target >85% agreement)
- **Trigger:** If accuracy <85%, refine parsing rules and re-validate

**Risk R2: UCI Enforcement Ambiguity**
- **Description:** UCI does not enforce license/version, but dataset creators may include them anyway (social norm)
- **Mitigation:** Document UCI presence rates separately; if UCI shows high presence (>80%), still consistent with enforcement hypothesis (creators know license is standard)
- **Interpretation:** High UCI presence supports "enforcement by social norm" (not platform-enforced, but professionally expected)

**Risk R3: Platform-Specific Field Definitions**
- **Description:** HF auto-generates version, OpenML requires integer version, UCI has implicit version via last-modified date
- **Mitigation:** Explicit semantic mapping (Section 3.4); parsing rules account for platform-specific formats
- **Validation:** Manual review checks cross-platform equivalence

---

## 9. Expected Results & Interpretation

### 9.1 Predicted Outcome (SHOULD_WORK Gate)

**Hypothesis h-m3 predicts:**

| Field | Platform | Predicted Presence | Mechanism |
|-------|----------|-------------------|-----------|
| license | HuggingFace | 85-95% | Enforced (dropdown blocking) |
| license | OpenML | 85-95% | Enforced (required field) |
| license | UCI | 70-85% | Social norm (not platform-enforced, but professionally expected) |
| version | HuggingFace | 90-100% | Auto-generated (always present) |
| version | OpenML | 85-95% | Enforced (required field) |
| version | UCI | 60-80% | Implicit (last-modified date) |

**Key Statistical Predictions:**
- Chi-squared test: p > 0.10 (no significant cross-platform difference)
- Cramér's V: V < 0.20 (weak association between required fields and platform)
- CV: required CV < 0.20 (stable across platforms) vs optional CV > 1.0 (variable, h-m2)

**Contrast with h-m2 Optional Fields:**
- Optional fields: HF 55-66%, UCI 0-15%, p<0.0001, V>0.40
- Required fields: HF≈OpenML≈UCI, p>0.10, V<0.20

### 9.2 Alternative Outcomes

**Outcome A: VALIDATED (Hypothesis Confirmed)**
- Required fields: p>0.10, CV<0.20, mean≥80%
- Conclusion: Enforcement and friction reduction are independent mechanisms
- Implication: Repository design has TWO levers: (1) Enforce critical fields, (2) Reduce friction for optional fields

**Outcome B: PARTIAL (Mechanisms Partially Coupled)**
- Required fields: p=0.05-0.10, CV=0.20-0.40
- Conclusion: Enforcement dominates, but friction still influences
- Implication: Good UX matters even for required fields (reduces creator frustration, improves quality)

**Outcome C: FAIL (Single Mechanism Hypothesis)**
- Required fields: p<0.05, CV>0.40, large cross-platform variance
- Conclusion: Enforcement and friction are NOT independent (confounded)
- Implication: PIVOT to single mechanism model (completeness driven by platform UX quality, not enforcement)

### 9.3 Decision Tree (Gate: SHOULD_WORK)

```
Chi-squared test (license & version): p > 0.10?
├─ YES → CV < 0.20?
│  ├─ YES → VALIDATED (Outcome A)
│  └─ NO → PARTIAL (Outcome B)
└─ NO → p < 0.05?
   ├─ YES → FAIL (Outcome C)
   └─ NO → PARTIAL (Outcome B)
```

**Post-Validation Actions:**
- VALIDATED → Proceed to Phase 5 (baseline comparison with Yang 2024, Strecker 2026)
- PARTIAL → Document limitations in 04_validation.md, proceed to Phase 5 with nuanced interpretation
- FAIL → STOP h-m3, reassess main hypothesis H-FrictionMetadata-v1 (enforcement/friction distinction invalid)

---

## 10. Validation Report Template

### 10.1 04_validation.md Structure

```markdown
# Validation Report: h-m3 — Enforcement vs Friction Mechanism Distinction

**Date:** 2026-08-19  
**Hypothesis ID:** h-m3  
**Status:** [VALIDATED / PARTIAL / FAIL]

## 1. Hypothesis Recap
[Statement, rationale, gate, success criteria]

## 2. Experimental Setup
[Dataset: h-m2 extraction reused, n=9,990]
[Fields: license (required), version (required)]
[Platforms: HF (friction=3), OpenML (friction=2), UCI (friction=0)]

## 3. Results Summary

### 3.1 Required Field Presence Rates
| Field | HuggingFace | OpenML | UCI | Mean | CV |
|-------|------------|--------|-----|------|-----|
| license | X.X% | X.X% | X.X% | X.X% | X.XX |
| version | X.X% | X.X% | X.X% | X.X% | X.XX |

### 3.2 Statistical Tests
| Field | χ² | p-value | dof | Cramér's V | Interpretation |
|-------|-----|---------|-----|-----------|----------------|
| license | X.XX | X.XXXX | X | X.XXX | [Weak/Moderate/Strong association] |
| version | X.XX | X.XXXX | X | X.XXX | [Weak/Moderate/Strong association] |

### 3.3 Contrast with h-m2 Optional Fields
| Metric | Required (license) | Required (version) | Optional (preprocessing_code, h-m2) |
|--------|-------------------|-------------------|-------------------------------------|
| CV | X.XX | X.XX | 2.45 |
| Cramér's V | X.XXX | X.XXX | 0.XXX |
| p-value | X.XXXX | X.XXXX | 0.0000 |

## 4. Validation Decision
[PASS / PARTIAL / FAIL]

**Rationale:**
- Primary criteria: [Met / Partially Met / Not Met]
- Mechanism distinction: [Clear / Unclear / None]
- Gate: SHOULD_WORK → [PASS / PARTIAL]

## 5. Key Findings
1. [Direction confirmed: required fields stable across platforms]
2. [Statistical significance: p > 0.10 (no friction effect) OR p < 0.05 (friction effect detected)]
3. [Effect size: weak/moderate/strong]
4. [Contrast with h-m2: required CV << optional CV (mechanism distinction validated)]

## 6. Limitations
- [UCI enforcement ambiguity: social norm vs platform validation]
- [Platform-specific field formats: HF auto-version, OpenML integer version, UCI implicit version]
- [Parsing accuracy: X.X% (manual validation)]

## 7. Implications
- [Repository design implications: two levers (enforcement + friction reduction)]
- [Phase 5 comparison: Yang 2024 single-platform vs h-m3 cross-platform mechanism test]

## 8. Next Steps
- [Proceed to Phase 5: baseline comparison]
- [Update verification_state.yaml: h-m3.validation.status = VALIDATED/PARTIAL]
```

---

## 11. Summary

**h-m3 Experiment Brief:**

| Component | Specification |
|-----------|--------------|
| **Hypothesis** | Required field presence rates stable across platforms (no friction effect) vs optional field presence varies by friction (h-m2 validated) |
| **Dataset** | h-m2 extraction (9,990 datasets: HF 6,500, OpenML 2,990, UCI 500) |
| **Fields** | license (required), version (required) |
| **Statistical Test** | Chi-squared test (p>0.10 = PASS), Cramér's V (<0.20 = weak association), CV (<0.20 = stable) |
| **Success Criteria** | No friction effect (p>0.10), high presence (≥80%), contrast with optional fields (CV required << CV optional) |
| **Tier** | 1 (reuses h-m2 data, straightforward comparison) |
| **Duration** | 9 hours (1 day) |
| **Gate** | SHOULD_WORK |

**Key Innovation:** First cross-platform test of enforcement vs friction-reduction mechanism distinction in ML repository metadata completion.

---

**Experiment Brief Complete** | **Next:** Phase 3 Implementation Planning | **Date:** 2026-08-19
