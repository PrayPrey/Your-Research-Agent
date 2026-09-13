# Architecture: h-m2 — Lower Friction Increases Voluntary Completion

**Date:** 2026-08-19  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Tier:** 1  
**Gate:** SHOULD_WORK

Applied: Cross-platform metadata extraction patterns (API wrappers, field normalization, statistical comparison)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extractors found in h-m1 (HF classifier/parser) and h-e1 (multi-platform collector)  
**Analyzed Path:** `scripts/h-m1/main.py`, `h-e1/code/data_collection.py`  
**Findings:** h-m1 has HF-specific parser with 6-field rules; h-e1 has multi-platform collector skeleton (HF/OpenML/UCI). Reuse parser rules and adapt collector structure.

---

## Module Breakdown

### 1. Config (`h-m2/config.py`)

**Dependencies:** None

```python
CONFIG = {
    'seed': 42,
    'platforms': {
        'hf': {'friction': 3, 'sample_size': 7000, 'api': 'huggingface_hub'},
        'openml': {'friction': 2, 'sample_size': 2500, 'api': 'openml-python'},
        'uci': {'friction': 0, 'sample_size': 500, 'method': 'scraper'}
    },
    'target_fields': ['preprocessing_code', 'data_source_url', 'collection_date'],
    'validation': {'parsing_threshold': 0.85, 'semantic_threshold': 0.80},
    'statistical': {'alpha': 0.05, 'effect_size_min_pp': 30},
    'output_dir': 'data/h-m2'
}
```

### 2. Platform Extractors (`h-m2/extractors/`)

#### HFExtractor (`extractors/hf_extractor.py`)

**Dependencies:** huggingface_hub, yaml

```python
class HFExtractor:
    def __init__(self, config: dict): ...
    def fetch_datasets(self, n: int) -> list[str]: ...
    def extract_metadata(self, dataset_id: str) -> dict: ...
    def _parse_readme(self, readme_text: str) -> dict: ...
```

**Reuse:** h-m1 README parsing logic (code blocks, YAML frontmatter)

#### OpenMLExtractor (`extractors/openml_extractor.py`)

**Dependencies:** openml-python, lxml

```python
class OpenMLExtractor:
    def __init__(self, config: dict): ...
    def fetch_datasets(self, n: int) -> list[int]: ...
    def extract_metadata(self, dataset_id: int) -> dict: ...
    def _parse_xml(self, xml_content: str) -> dict: ...
```

**Reuse:** h-e1 collector structure

#### UCIExtractor (`extractors/uci_extractor.py`)

**Dependencies:** BeautifulSoup, requests

```python
class UCIExtractor:
    def __init__(self, config: dict): ...
    def fetch_datasets(self, n: int) -> list[str]: ...
    def extract_metadata(self, dataset_url: str) -> dict: ...
    def _parse_html(self, html_content: str) -> dict: ...
```

### 3. Field Normalizer (`h-m2/normalizer.py`)

**Dependencies:** None

```python
class FieldNormalizer:
    FIELD_MAPPING = {
        'preprocessing_code': {
            'hf': ['README code blocks', 'dataset card YAML'],
            'openml': ['processing_script'],
            'uci': ['methodology section']
        },
        'data_source_url': {
            'hf': ['source', 'homepage'],
            'openml': ['url'],
            'uci': ['source URL']
        },
        'collection_date': {
            'hf': ['date_created'],
            'openml': ['upload_date', 'version_date'],
            'uci': ['publication_date']
        }
    }
    
    def normalize(self, raw_metadata: dict, platform: str) -> dict: ...
    def _map_field(self, field_name: str, platform_data: dict, platform: str) -> any: ...
```

### 4. Field Parser (`h-m2/parser.py`)

**Dependencies:** re

```python
class FieldParser:
    def parse_preprocessing_code(self, text: str) -> int: ...
    def parse_data_source_url(self, text: str) -> int: ...
    def parse_collection_date(self, text: str) -> int: ...
    def parse_all(self, normalized_data: dict) -> dict: ...
```

**Reuse:** h-m1 parsing rules (>50 chars, keywords, URL patterns, date patterns)

### 5. Statistical Analyzer (`h-m2/statistical_analysis.py`)

**Dependencies:** scipy.stats, numpy

```python
class StatisticalAnalyzer:
    def chi_squared_test(self, contingency_table: np.ndarray) -> dict: ...
    def effect_size(self, platform_rates: dict) -> float: ...
    def gradient_analysis(self, hf_rate: float, openml_rate: float, uci_rate: float) -> dict: ...
```

### 6. Validator (`h-m2/validation.py`)

**Dependencies:** random

```python
class Validator:
    def sample_for_manual_review(self, metadata_list: list[dict], n: int) -> list[dict]: ...
    def calculate_parsing_accuracy(self, automated: list[dict], manual: list[dict]) -> float: ...
    def calculate_semantic_accuracy(self, cross_platform_samples: list[dict]) -> float: ...
```

### 7. Pipeline Orchestrator (`h-m2/main.py`)

**Dependencies:** All above modules

```python
def main():
    config = load_config()
    
    # Step 1: Extract metadata
    extractors = {
        'hf': HFExtractor(config),
        'openml': OpenMLExtractor(config),
        'uci': UCIExtractor(config)
    }
    raw_metadata = {}
    for platform, extractor in extractors.items():
        datasets = extractor.fetch_datasets(config['platforms'][platform]['sample_size'])
        raw_metadata[platform] = [extractor.extract_metadata(ds) for ds in datasets]
    
    # Step 2: Normalize fields
    normalizer = FieldNormalizer()
    normalized = {p: [normalizer.normalize(m, p) for m in metadata] 
                  for p, metadata in raw_metadata.items()}
    
    # Step 3: Parse presence
    parser = FieldParser()
    presence_data = {p: [parser.parse_all(m) for m in metadata] 
                     for p, metadata in normalized.items()}
    
    # Step 4: Statistical analysis
    analyzer = StatisticalAnalyzer()
    results = analyzer.chi_squared_test(...)
    
    # Step 5: Validation
    validator = Validator()
    parsing_acc = validator.calculate_parsing_accuracy(...)
    
    # Step 6: Gate decision
    gate_result = decide_gate(results, parsing_acc, config)
    
    # Step 7: Write report
    write_validation_report(gate_result, results, config)
```

---

## Data Flow

```
Platform APIs (HF/OpenML/UCI)
  → Extractors (fetch + parse platform-specific formats)
    → Normalizer (map to standard schema: preprocessing_code, data_source_url, collection_date)
      → Parser (binary presence detection: 0/1 per field)
        → Analyzer (chi-squared test, effect size)
          → Validator (parsing accuracy, semantic validation)
            → Gate Decision (PASS/FAIL based on p<0.05, effect≥30pp, accuracy>85%)
              → validation report (04_validation.md)
```

---

## File Structure

```
h-m2/
├── config.py                     # Configuration constants
├── extractors/
│   ├── __init__.py
│   ├── hf_extractor.py           # HuggingFace API wrapper
│   ├── openml_extractor.py       # OpenML API wrapper
│   └── uci_extractor.py          # UCI web scraper
├── normalizer.py                 # Cross-platform field mapping
├── parser.py                     # Binary presence detection
├── statistical_analysis.py       # Chi-squared test, effect size
├── validation.py                 # Parsing + semantic accuracy
└── main.py                       # Pipeline orchestrator

data/h-m2/
├── hf_metadata.json              # Raw HF data
├── openml_metadata.json          # Raw OpenML data
├── uci_metadata.json             # Raw UCI data
├── presence_rates.csv            # Aggregated presence rates
├── statistical_results.json      # Test results
└── validation_report.json        # Validation metrics
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| HF API | huggingface_hub>=0.20.0 |
| OpenML API | openml>=0.14.0 |
| UCI Scraper | beautifulsoup4>=4.12.0, requests>=2.31.0 |
| Statistical | scipy>=1.11.0, numpy>=1.24.0 |
| Data | pandas>=2.0.0 |
| Parsing | re (stdlib), lxml>=4.9.0 |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup extractors | Adapt h-m1 HF extractor + h-e1 OpenML/UCI collectors for 3-field extraction | 9 | Platform adapters(3) + field mapping(3) + error handling(2) + testing(1) |
| A-2 | Cross-platform normalizer | Map platform-specific field names to standard schema (preprocessing_code, data_source_url, collection_date) | 8 | Mapping rules(3) + semantic equivalence(3) + edge cases(2) |
| A-3 | Field parser | Reuse h-m1 binary presence rules for 3 optional fields | 6 | Regex patterns(2) + keyword matching(2) + URL/date validation(2) |
| A-4 | Statistical analysis | Chi-squared test + effect size calculation for HF vs UCI comparison | 7 | Contingency table(2) + scipy integration(2) + gradient analysis(2) + reporting(1) |
| A-5 | Validation pipeline | Parsing accuracy + semantic validation (manual review protocol) | 10 | Sampling(2) + manual review interface(3) + accuracy calculation(2) + semantic equivalence(3) |
| A-6 | Data extraction | Fetch 10k+ datasets from 3 platforms with retry logic and checkpointing | 11 | API calls(3) + rate limiting(2) + checkpointing(3) + parallel I/O(2) + error recovery(1) |
| A-7 | Gate decision | Evaluate SHOULD_WORK criteria and generate 04_validation.md | 5 | Criteria checks(2) + report generation(2) + visualizations(1) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-5, A-6], Low(4-8): [A-2, A-3, A-4, A-7]

---

## Reuse Strategy

### From h-m1 (`scripts/h-m1/main.py`)

**Reuse Components:**
- `MetadataParser` class → Field parsing rules for preprocessing_code, data_source_url, collection_date
- Binary presence detection logic (>50 chars, keywords, URL patterns, date patterns)
- Statistical validation framework (t-test/Mann-Whitney, validation thresholds)

**Adaptations:**
- Remove HF-specific fields (dependencies, version, license) — h-m2 focuses only on 3 optional fields
- Extend to cross-platform (not just API vs manual within HF)

### From h-e1 (`h-e1/code/data_collection.py`)

**Reuse Components:**
- `DataCollector` structure → Multi-platform extractor pattern
- Retry logic with exponential backoff
- Platform-specific extraction methods (_extract_hf_fields, _extract_openml_fields, _extract_uci_fields)

**Adaptations:**
- Replace synthetic data generation with actual API calls
- Add field normalization layer (h-e1 extracted binary vectors without semantic mapping)

---

## Interface Contracts

### Extractor Interface

```python
class BaseExtractor(ABC):
    @abstractmethod
    def fetch_datasets(self, n: int) -> list: ...
    
    @abstractmethod
    def extract_metadata(self, dataset_id: any) -> dict: ...
```

**Output Schema (per extractor):**
```json
{
  "dataset_id": "string",
  "platform": "hf | openml | uci",
  "raw_fields": {
    "field1": "value or null",
    "field2": "value or null"
  },
  "extraction_timestamp": "ISO 8601"
}
```

### Normalizer Interface

**Input:** Raw platform-specific metadata  
**Output:** Standardized schema

```json
{
  "dataset_id": "string",
  "platform": "hf | openml | uci",
  "fields": {
    "preprocessing_code": {"present": 0|1, "source_field": "string", "value": "string|null"},
    "data_source_url": {"present": 0|1, "source_field": "string", "value": "string|null"},
    "collection_date": {"present": 0|1, "source_field": "string", "value": "string|null"}
  }
}
```

### Statistical Analyzer Interface

**Input:** Presence rates per platform (dict)  
**Output:** Test results

```json
{
  "chi_squared_statistic": 12.345,
  "p_value": 0.0002,
  "effect_size_pp": 42.5,
  "hf_rate": 58.2,
  "openml_rate": 32.1,
  "uci_rate": 15.7,
  "gradient_confirmed": true
}
```

---

## Non-Functional Requirements

### Performance
- Total runtime ≤4 hours for 10k+ datasets
- API rate limits: HF (100 req/min), OpenML (60 req/min), UCI (1 req/sec)
- Parallel extraction per platform (async I/O)

### Reliability
- Retry logic: 3 attempts with exponential backoff [1s, 5s, 15s]
- Graceful degradation: skip malformed metadata, log errors
- Checkpointing: resume from last successful batch (every 100 datasets)

### Reproducibility
- Fixed seed: 42
- Pinned dependencies in requirements.txt
- Timestamped extraction: all datasets fetched on 2026-08-19

---

## Validation Requirements

**Parsing Accuracy:**
- Sample: 100 datasets (50 HF, 30 OpenML, 20 UCI)
- Manual review: binary presence annotation
- Threshold: >85% agreement

**Semantic Equivalence:**
- Sample: 50 datasets per platform with field present
- Manual review: verify HF preprocessing_code ≈ OpenML processing_script ≈ UCI methodology
- Threshold: >80% semantic agreement

---

## Gate Criteria (SHOULD_WORK)

**Primary (required for PASS):**
1. Direction confirmed: HF > UCI for all 3 fields
2. p < 0.05 for HF vs UCI chi-squared test
3. Effect size ≥30pp for ≥2/3 fields

**Secondary (desirable):**
- Gradient: UCI < OpenML < HF
- Parsing accuracy >85%
- Semantic validity >80%

**Outcome:** PASS → Proceed to h-m3; FAIL → Document partial support, continue verification plan

---

**Architecture Complete** | **Next:** Phase 4 Implementation | **Date:** 2026-08-19
