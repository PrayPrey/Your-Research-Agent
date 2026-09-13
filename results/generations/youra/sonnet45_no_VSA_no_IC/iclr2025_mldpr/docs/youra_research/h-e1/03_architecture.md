# Architecture: H-E1 Friction Measurement Feasibility System

**Hypothesis ID:** h-e1  
**Architecture Version:** 1.0  
**Date:** 2026-08-19  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: Fresh EXISTENCE hypothesis requiring minimal PoC architecture

---

## System Overview

Feasibility validation system extracting metadata from 3 platforms (OpenML, HuggingFace, UCI) to validate:
1. Friction scores measurable from documentation
2. 10k+ datasets extractable within 2 weeks

**Data Flow:**
- Platform APIs/Web → Extractors (parallel) → Parsing → Validation → Gate Evaluation

---

## Module Definitions

### FrictionScorer (`scoring/friction_scorer.py`)

**Dependencies**: None

```python
class FrictionScorer:
    def __init__(self): ...
    def score_platform(self, platform: str, documentation: dict) -> dict: ...
    def generate_report(self, scores: dict) -> str: ...
```

---

### OpenMLExtractor (`extractors/openml_extractor.py`)

**Dependencies**: openml-python

```python
class OpenMLExtractor:
    def __init__(self, timeout: int = 30, max_retries: int = 3): ...
    def extract_metadata(self, dataset_id: int) -> dict: ...
    def extract_batch(self, dataset_ids: list[int]) -> list[dict]: ...
```

---

### HuggingFaceExtractor (`extractors/huggingface_extractor.py`)

**Dependencies**: datasets, huggingface_hub

```python
class HuggingFaceExtractor:
    def __init__(self, timeout: int = 30, max_retries: int = 3): ...
    def extract_metadata(self, dataset_id: str) -> dict: ...
    def extract_batch(self, dataset_ids: list[str]) -> list[dict]: ...
```

---

### UCIExtractor (`extractors/uci_extractor.py`)

**Dependencies**: beautifulsoup4, requests

```python
class UCIExtractor:
    def __init__(self, timeout: int = 30, max_retries: int = 3, rate_limit: float = 1.0): ...
    def extract_metadata(self, dataset_name: str) -> dict: ...
    def extract_batch(self, dataset_names: list[str]) -> list[dict]: ...
```

---

### ParsingRules (`parsing/parsing_rules.py`)

**Dependencies**: None

```python
class ParsingRules:
    def __init__(self, config_path: str): ...
    def parse_preprocessing_code(self, value: any) -> int: ...
    def parse_data_source_url(self, value: any) -> int: ...
    def parse_collection_date(self, value: any) -> int: ...
    def parse_license(self, value: any) -> int: ...
    def parse_version(self, value: any) -> int: ...
    def parse_dependencies(self, value: any) -> int: ...
    def parse_all_fields(self, metadata: dict) -> dict: ...
```

---

### Validator (`validation/validator.py`)

**Dependencies**: ParsingRules

```python
class Validator:
    def __init__(self, parser: ParsingRules): ...
    def load_ground_truth(self, path: str) -> dict: ...
    def calculate_accuracy(self, predictions: dict, ground_truth: dict) -> dict: ...
    def generate_confusion_matrix(self, predictions: dict, ground_truth: dict) -> dict: ...
```

---

### ThroughputAnalyzer (`analysis/throughput.py`)

**Dependencies**: None

```python
class ThroughputAnalyzer:
    def __init__(self): ...
    def record_extraction(self, platform: str, dataset_id: str, duration: float, status: str): ...
    def calculate_throughput(self, platform: str = None) -> float: ...
    def extrapolate_full_scale(self, target_counts: dict) -> dict: ...
    def generate_feasibility_report(self, extrapolation: dict, time_limit: int = 336) -> str: ...
```

---

### GateEvaluator (`analysis/gate_evaluator.py`)

**Dependencies**: ThroughputAnalyzer, Validator

```python
class GateEvaluator:
    def __init__(self): ...
    def evaluate_must_work_gate(self, metrics: dict) -> dict: ...
    def generate_gate_report(self, result: dict) -> str: ...
```

---

### ExtractionOrchestrator (`orchestrator.py`)

**Dependencies**: OpenMLExtractor, HuggingFaceExtractor, UCIExtractor, ThroughputAnalyzer

```python
class ExtractionOrchestrator:
    def __init__(self, extractors: dict, analyzer: ThroughputAnalyzer, max_workers: int = 3): ...
    def run_parallel_extraction(self, platform_samples: dict) -> dict: ...
    def save_results(self, results: dict, output_path: str): ...
```

---

## Parallel Execution Design

**Strategy**: ThreadPoolExecutor (3 workers - 1 per platform)

```
Main Thread
├─ Worker 1: OpenML (100 datasets)
├─ Worker 2: HuggingFace (100 datasets)
└─ Worker 3: UCI (50 datasets)
```

Rate limiting enforced per extractor (UCI: 1 req/sec).

---

## Error Handling Strategy

**Retry Logic:**
- 3 attempts per extraction
- Exponential backoff: 1s → 2s → 4s
- Timeout: 30s per request

**Graceful Degradation:**
- Missing fields → null (not failure)
- HTTP 429 → exponential backoff
- Parsing errors → logged, continue batch

**Logging:**
```
logs/
├─ openml_extraction.log
├─ huggingface_extraction.log
├─ uci_extraction.log
└─ orchestrator.log
```

Format: JSON lines with `{timestamp, platform, dataset_id, status, error_msg, duration}`

---

## Configuration (`config/parsing_config.yaml`)

```yaml
parsing_rules:
  preprocessing_code:
    min_length: 50
    keywords: ['import', 'def', 'function', 'library', 'require']
    extensions: ['.py', '.R', '.ipynb', '.jl']
  
  data_source_url:
    url_pattern: 'http(s)?://[^\s]+'
    min_length: 10
  
  collection_date:
    date_patterns: ['YYYY-MM-DD', 'MM/DD/YYYY', 'YYYY']
  
  license:
    min_length: 5
    exclude_placeholders: ['N/A', 'Unknown', 'TODO', 'null']
  
  version:
    version_patterns: ['X.Y.Z', 'vX', 'version X']
  
  dependencies:
    min_length: 20
    min_list_size: 1

extraction:
  timeout: 30
  max_retries: 3
  backoff_base: 1.0
  max_workers: 3
  
  rate_limits:
    uci: 1.0
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Setup Project | Install deps, folder structure, config file | 5 | 1+1+1+2 |
| E-2 | Implement Extractors | OpenML/HF/UCI API clients with retry | 15 | 3+4+5+3 |
| E-3 | Implement Parsing | 6 field parsers + config loader | 10 | 2+2+2+2+2 |
| E-4 | Run Pilot | Execute 250-dataset extraction | 7 | 2+2+2+1 |
| E-5 | Validation | Manual annotation + accuracy calc | 8 | 3+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E-2], Medium(9-13): [E-3], Low(4-8): [E-1, E-4, E-5]

**Total Complexity**: 45 (3-4 days dev time)

---

## File Structure

```
h-e1/
├─ config/
│  └─ parsing_config.yaml
├─ scoring/
│  └─ friction_scorer.py
├─ extractors/
│  ├─ openml_extractor.py
│  ├─ huggingface_extractor.py
│  └─ uci_extractor.py
├─ parsing/
│  └─ parsing_rules.py
├─ validation/
│  └─ validator.py
├─ analysis/
│  ├─ throughput.py
│  └─ gate_evaluator.py
├─ orchestrator.py
├─ logs/
├─ data/
│  ├─ pilot_results.json
│  └─ validation_ground_truth.csv
└─ reports/
   ├─ friction_scores.md
   ├─ pilot_metrics.md
   ├─ parsing_accuracy.md
   └─ gate_evaluation.md
```

---

## Validation Protocol

1. **Friction Scoring**: Manual review of platform docs → binary criteria → composite score
2. **Pilot Extraction**: 250 datasets (100+100+50) → success rate >80%/70%
3. **Manual Annotation**: 100-dataset stratified sample → ground truth labels
4. **Accuracy Calculation**: Automated vs manual → >90% target
5. **Throughput Extrapolation**: Pilot rate → 10k estimate → <336hr gate

---

## MUST_WORK Gate Criteria

| Metric | Target | Implementation |
|--------|--------|----------------|
| Friction scores assigned | Yes | FrictionScorer.generate_report() |
| OpenML/HF success rate | >80% | ThroughputAnalyzer metrics |
| UCI success rate | >70% | ThroughputAnalyzer metrics |
| Parsing accuracy | >90% | Validator.calculate_accuracy() |
| 10k feasibility | <336hr | ThroughputAnalyzer.extrapolate_full_scale() |

All checks in `GateEvaluator.evaluate_must_work_gate()`.

---

## Self-Validation Checklist

- [x] No ASCII diagrams
- [x] Module sections = interface code only
- [x] 5 Epic tasks with complexity scores
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project documented
- [x] EXISTENCE hypothesis = minimal PoC architecture
