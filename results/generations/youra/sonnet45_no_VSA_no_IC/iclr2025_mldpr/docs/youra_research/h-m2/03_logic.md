# Logic Specification: h-m2 Lower Friction Increases Voluntary Completion

**Date:** 2026-08-19  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Tier:** 1

---

## Codebase Analysis (Serena)

**Project Type**: green-field with h-m1 parsing rule reuse
**Status**: New cross-platform implementation; reusing h-m1 field parsing logic
**Analyzed Path**: scripts/h-m1/main.py
**Relevant Symbols**: MetadataParser class (lines 141-227) — field presence detection rules

---

## 1. Core Algorithms

### 1.1 Cross-Platform Field Normalizer

**Purpose**: Map platform-specific field names to standard schema.

**Input**:
```python
raw_metadata: dict  # Platform-specific metadata
platform: Literal["HF", "OpenML", "UCI"]
```

**Output**:
```python
{
  "preprocessing_code": {"present": bool, "value": str | None, "source_field": str},
  "data_source_url": {"present": bool, "value": str | None, "source_field": str},
  "collection_date": {"present": bool, "value": str | None, "source_field": str}
}
```

**Mapping Rules**:

| Standard Field | HF Source | OpenML Source | UCI Source |
|---------------|-----------|---------------|------------|
| preprocessing_code | README code blocks OR YAML "code" | XML "processing_script" | HTML methodology section |
| data_source_url | YAML "source" OR "homepage" | XML "url" | HTML link with class="source" |
| collection_date | YAML "date_created" | XML "version_date" OR "upload_date" | HTML meta tag "publication_date" |

**Algorithm**:
```python
def normalize_field(field_name: str, raw_metadata: dict, platform: str) -> dict:
    mapping = FIELD_MAPPING[platform][field_name]  # List of potential source fields
    
    for source_field in mapping:
        value = extract_from_path(raw_metadata, source_field)  # Nested dict lookup
        if value is not None and len(str(value).strip()) > 0:
            return {
                "present": detect_presence(field_name, value),  # Binary rule
                "value": value,
                "source_field": source_field
            }
    
    return {"present": False, "value": None, "source_field": None}
```

**Edge Cases**:
- Multiple source fields present → Take first non-empty match
- Malformed XML/YAML → Graceful fallback to None
- Empty string vs null → Both treated as absent

---

### 1.2 Binary Field Presence Detection

**Purpose**: Detect if optional field is present (not placeholder/empty).

**Reused from h-m1** (MetadataParser lines 195-221):

**preprocessing_code**:
```python
def detect_preprocessing_code(text: str) -> bool:
    # Code blocks with >50 chars + keywords
    code_blocks = re.findall(r'```.*?\n(.*?)```', text, re.DOTALL)
    keywords = ['def ', 'import ', 'library(', 'function', 'class ']
    has_code = any(
        len(block) > 50 and any(kw in block for kw in keywords)
        for block in code_blocks
    )
    
    # OR script file references
    script_refs = any(re.search(p, text) for p in [r'\.py\b', r'\.R\b', r'\.ipynb\b'])
    
    return has_code or script_refs
```

**data_source_url**:
```python
def detect_data_source_url(text: str) -> bool:
    urls = re.findall(r'https?://[^\s]+', text)
    
    # Exclude platform self-references
    exclude = ["github.com", "huggingface.co", "gitlab.com", "openml.org"]
    external = [u for u in urls if not any(d in u for d in exclude)]
    
    return len(external) > 0
```

**collection_date**:
```python
def detect_collection_date(text: str) -> bool:
    patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # Month YYYY
        r'collected (on|in|during)',  # Prose indicators
        r'data (from|collected|gathered)'
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)
```

**Rejection Criteria** (false positive prevention):
- Placeholders: "TODO", "N/A", "TBD", "Unknown"
- Empty code blocks: ``` ``` (no content)
- Localhost URLs: http://localhost, http://127.0.0.1
- Invalid dates: 0000-00-00, 9999-12-31

---

### 1.3 Chi-Squared Test (2×2 and 3×3)

**Purpose**: Compare optional field presence rates across platforms.

**Applied**: scipy.stats.chi2_contingency

**2×2 Contingency (Primary: HF vs UCI)**:
```python
def chi_squared_2x2(hf_present: int, hf_absent: int, 
                    uci_present: int, uci_absent: int) -> dict:
    observed = np.array([
        [hf_present, hf_absent],
        [uci_present, uci_absent]
    ])
    
    chi2, p_value, dof, expected = scipy.stats.chi2_contingency(observed)
    
    return {
        "chi2": chi2,
        "p_value": p_value,
        "dof": dof,
        "expected": expected.tolist()
    }
```

**3×3 Contingency (Secondary: HF, OpenML, UCI)**:
```python
def chi_squared_3x3(counts: dict) -> dict:
    # counts = {"HF": {"present": X, "absent": Y}, "OpenML": {...}, "UCI": {...}}
    observed = np.array([
        [counts["HF"]["present"], counts["HF"]["absent"]],
        [counts["OpenML"]["present"], counts["OpenML"]["absent"]],
        [counts["UCI"]["present"], counts["UCI"]["absent"]]
    ])
    
    chi2, p_value, dof, expected = scipy.stats.chi2_contingency(observed)
    
    return {
        "chi2": chi2,
        "p_value": p_value,
        "dof": dof,
        "gradient_valid": validate_gradient(counts)  # UCI < OpenML < HF
    }
```

**Gradient Validation**:
```python
def validate_gradient(counts: dict) -> bool:
    hf_rate = counts["HF"]["present"] / (counts["HF"]["present"] + counts["HF"]["absent"])
    openml_rate = counts["OpenML"]["present"] / (counts["OpenML"]["present"] + counts["OpenML"]["absent"])
    uci_rate = counts["UCI"]["present"] / (counts["UCI"]["present"] + counts["UCI"]["absent"])
    
    return uci_rate < openml_rate < hf_rate
```

**Assumptions Check**:
- All expected cell counts ≥5 → Use chi-squared
- If any expected <5 → Use Fisher's exact test (scipy.stats.fisher_exact for 2×2 only)

---

### 1.4 Effect Size Calculation

**Purpose**: Quantify difference in proportions (HF - UCI).

**Algorithm**:
```python
def calculate_effect_size(hf_present: int, hf_total: int,
                         uci_present: int, uci_total: int) -> dict:
    hf_rate = hf_present / hf_total
    uci_rate = uci_present / uci_total
    
    diff_pp = (hf_rate - uci_rate) * 100  # Percentage points
    
    # Cohen's h for proportions
    h = 2 * (np.arcsin(np.sqrt(hf_rate)) - np.arcsin(np.sqrt(uci_rate)))
    
    return {
        "hf_rate": round(hf_rate * 100, 1),
        "uci_rate": round(uci_rate * 100, 1),
        "diff_pp": round(diff_pp, 1),
        "cohen_h": round(h, 3)
    }
```

**Interpretation**:
- diff_pp ≥30 → Substantial effect (gate threshold)
- Cohen's h ≥0.8 → Large effect (informational)

---

### 1.5 Validation Sampling Strategy

**Purpose**: Stratified manual review for parsing accuracy + semantic equivalence.

**Parsing Accuracy Validation** (100 samples):
```python
def stratified_parsing_sample(datasets: dict, n_total: int = 100) -> list:
    # Stratify by platform: 50 HF, 30 OpenML, 20 UCI
    strata = {
        "HF": 50,
        "OpenML": 30,
        "UCI": 20
    }
    
    samples = []
    for platform, n in strata.items():
        platform_datasets = datasets[platform]
        sampled = random.sample(platform_datasets, min(n, len(platform_datasets)))
        samples.extend([{**d, "platform": platform} for d in sampled])
    
    return samples
```

**Semantic Validation** (150 samples, only datasets with field present):
```python
def stratified_semantic_sample(datasets: dict, field: str, n_total: int = 150) -> list:
    # 50 per platform, only datasets where field is present
    samples = []
    for platform in ["HF", "OpenML", "UCI"]:
        present_datasets = [d for d in datasets[platform] if d[field]["present"]]
        sampled = random.sample(present_datasets, min(50, len(present_datasets)))
        samples.extend([{**d, "platform": platform} for d in sampled])
    
    return samples
```

**Manual Review Protocol**:
1. Human annotator views raw metadata + automated label
2. Marks presence: 0 (absent) or 1 (present)
3. For semantic validation: marks "equivalent" (1) or "mismatch" (0)
4. Agreement calculated: (matches / total) × 100

---

## 2. Platform-Specific Extractors

### 2.1 HuggingFace Extractor

**Applied**: huggingface_hub.HfApi

```python
def extract_hf_metadata(dataset_id: str) -> dict:
    api = HfApi()
    info = api.dataset_info(dataset_id)
    
    # Fetch README
    readme_text = str(getattr(info, 'card_data', ''))
    
    # Extract YAML frontmatter
    yaml_match = re.search(r'^---\n(.*?)\n---', readme_text, re.DOTALL)
    yaml_data = yaml.safe_load(yaml_match.group(1)) if yaml_match else {}
    
    return {
        "dataset_id": dataset_id,
        "readme_text": readme_text,
        "yaml_frontmatter": yaml_data,
        "platform": "HF"
    }
```

### 2.2 OpenML Extractor

**Applied**: openml.datasets.get_dataset

```python
def extract_openml_metadata(dataset_id: int) -> dict:
    dataset = openml.datasets.get_dataset(dataset_id)
    
    return {
        "dataset_id": dataset_id,
        "description": dataset.description,
        "xml_metadata": dataset._data,  # Raw XML structure
        "platform": "OpenML"
    }
```

### 2.3 UCI Scraper

**Applied**: BeautifulSoup

```python
def extract_uci_metadata(dataset_url: str) -> dict:
    response = requests.get(dataset_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract sections
    description = soup.find('div', class_='description')
    methodology = soup.find('div', class_='methodology')
    source_link = soup.find('a', class_='source')
    pub_date = soup.find('meta', attrs={'name': 'publication_date'})
    
    return {
        "dataset_url": dataset_url,
        "description": description.get_text() if description else "",
        "methodology": methodology.get_text() if methodology else "",
        "source_url": source_link.get('href') if source_link else None,
        "publication_date": pub_date.get('content') if pub_date else None,
        "platform": "UCI"
    }
```

---

## 3. Statistical Pipeline

### 3.1 End-to-End Analysis

```python
def run_statistical_analysis(hf_data: list, openml_data: list, uci_data: list) -> dict:
    results = {}
    
    for field in ["preprocessing_code", "data_source_url", "collection_date"]:
        # Count presence/absence per platform
        hf_counts = count_presence(hf_data, field)
        openml_counts = count_presence(openml_data, field)
        uci_counts = count_presence(uci_data, field)
        
        # Primary test: HF vs UCI (2×2)
        chi2_result = chi_squared_2x2(
            hf_counts["present"], hf_counts["absent"],
            uci_counts["present"], uci_counts["absent"]
        )
        
        # Effect size
        effect = calculate_effect_size(
            hf_counts["present"], hf_counts["present"] + hf_counts["absent"],
            uci_counts["present"], uci_counts["present"] + uci_counts["absent"]
        )
        
        # Secondary test: 3-platform gradient (3×3)
        gradient_result = chi_squared_3x3({
            "HF": hf_counts,
            "OpenML": openml_counts,
            "UCI": uci_counts
        })
        
        results[field] = {
            "primary_test": chi2_result,
            "effect_size": effect,
            "gradient_test": gradient_result
        }
    
    return results
```

### 3.2 Gate Decision Logic

```python
def evaluate_gate(results: dict, validation: dict) -> dict:
    # Primary: All 3 fields show HF > UCI direction + p < 0.05
    direction_confirmed = all(
        results[f]["effect_size"]["diff_pp"] > 0 
        for f in ["preprocessing_code", "data_source_url", "collection_date"]
    )
    
    significant = all(
        results[f]["primary_test"]["p_value"] < 0.05
        for f in ["preprocessing_code", "data_source_url", "collection_date"]
    )
    
    # Substantial effect: ≥2/3 fields with ≥30pp difference
    substantial_count = sum(
        1 for f in ["preprocessing_code", "data_source_url", "collection_date"]
        if results[f]["effect_size"]["diff_pp"] >= 30.0
    )
    
    substantial = substantial_count >= 2
    
    # Validation thresholds
    parsing_acc = validation["parsing_accuracy"]
    semantic_acc = validation["semantic_accuracy"]
    validation_ok = parsing_acc > 0.85 and semantic_acc > 0.80
    
    # Decision
    if direction_confirmed and significant and substantial and validation_ok:
        return {"result": "PASS", "rationale": "All primary + secondary criteria met"}
    elif not direction_confirmed:
        return {"result": "FAIL", "rationale": "Direction reversed or no difference"}
    elif not significant:
        return {"result": "FAIL", "rationale": "No statistical significance (p ≥ 0.05)"}
    elif not substantial:
        return {"result": "FAIL", "rationale": f"Effect size too small ({substantial_count}/3 fields ≥30pp)"}
    else:
        return {"result": "FAIL", "rationale": f"Validation failed (parsing={parsing_acc:.2%}, semantic={semantic_acc:.2%})"}
```

---

## 4. Complexity Analysis

| Algorithm | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| Field normalization | O(F × M) | O(1) | F=3 fields, M=avg mapping list length (~3) |
| Binary presence detection | O(L) | O(1) | L=text length, regex matching |
| Chi-squared test | O(1) | O(1) | Fixed 2×2 or 3×3 table |
| Stratified sampling | O(N log N) | O(S) | N=dataset count, S=sample size (100-150) |
| End-to-end pipeline | O(N × L) | O(N) | N=10k datasets, L=avg README length |

**Expected Runtime**: ~2-4 hours for 10k datasets (dominated by API calls, not computation).

---

## 5. Edge Case Handling

| Edge Case | Handling Strategy |
|-----------|------------------|
| Malformed YAML/XML | Graceful parse failure → return None, log error |
| Empty README | All fields marked absent (0) |
| Multiple source fields present | Take first non-empty match |
| Placeholder text ("TODO") | Rejected by presence rules |
| API rate limit exceeded | Exponential backoff (1s, 2s, 4s, 8s) + retry (3 attempts) |
| Expected cell count <5 | Fallback to Fisher's exact test (2×2 only) |
| Platform dataset count mismatch | Report confidence intervals per platform |

---

## 6. Validation Protocol Specifications

**Parsing Accuracy**:
- Sample: 100 datasets (50 HF, 30 OpenML, 20 UCI)
- Measure: (automated_label == manual_label) / total_samples
- Threshold: >85%

**Semantic Equivalence**:
- Sample: 150 datasets with field present (50 per platform)
- Measure: (semantically_equivalent) / total_samples
- Threshold: >80%

**Manual Review Interface** (minimal):
```python
def manual_review_prompt(dataset: dict, field: str, automated_label: int) -> dict:
    print(f"Dataset: {dataset['dataset_id']}")
    print(f"Platform: {dataset['platform']}")
    print(f"Field: {field}")
    print(f"Automated: {automated_label} (0=absent, 1=present)")
    print(f"Raw content: {dataset[field]['value'][:200]}...")
    
    manual_label = int(input("Manual label (0/1): "))
    
    return {"dataset_id": dataset['dataset_id'], "field": field, 
            "automated": automated_label, "manual": manual_label}
```

---

## 7. Output Specifications

**presence_rates.csv**:
```csv
platform,field,present_count,total_count,presence_rate
HF,preprocessing_code,4200,7000,60.0
HF,data_source_url,4550,7000,65.0
HF,collection_date,3850,7000,55.0
OpenML,preprocessing_code,900,2500,36.0
...
```

**statistical_results.json**:
```json
{
  "preprocessing_code": {
    "primary_test": {"chi2": 450.2, "p_value": 0.0000, "dof": 1},
    "effect_size": {"hf_rate": 60.0, "uci_rate": 12.0, "diff_pp": 48.0, "cohen_h": 1.12},
    "gradient_test": {"chi2": 520.3, "p_value": 0.0000, "gradient_valid": true}
  },
  ...
}
```

**validation_report.json**:
```json
{
  "parsing_accuracy": 0.92,
  "semantic_accuracy": 0.85,
  "sample_size_parsing": 100,
  "sample_size_semantic": 150,
  "agreement_by_platform": {
    "HF": 0.94,
    "OpenML": 0.90,
    "UCI": 0.88
  }
}
```

---

**Applied**: Standard chi-squared test from scipy.stats  
**Applied**: Field presence rules from h-m1 MetadataParser (lines 195-221)  
**Applied**: Stratified sampling with fixed seed (seed=42)

No tensor shapes (data structures only, not neural networks). Pseudo-code for critical functions only (field normalization, chi-squared, gate logic). Algorithm complexity: O(N × L) dominated by API I/O, not computation.

---

**Logic Specification Complete** | **Date:** 2026-08-19
