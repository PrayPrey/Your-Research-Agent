# Architecture: H-E1 Retrospective Corpus Collection

**Hypothesis**: h-e1 (EXISTENCE)  
**Created**: 2026-08-25  
**Architecture Version**: 1.0

Applied: ETL Pipeline Pattern (data-collection-workflows)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing code to analyze - corpus collection is a standalone data pipeline

---

## System Overview

Retrospective corpus collection pipeline extracting ML overhead measurements from published research. Three-stage ETL: collection (API queries + scraping), extraction (PDF parsing + regex), validation (completeness + stratification).

**Core Constraint**: EXISTENCE hypothesis - minimal viable pipeline, 4 scripts total.

---

## Module Structure

### CollectionModule (`code/collect.py`)

**Dependencies**: requests, beautifulsoup4

```python
def query_papers_with_code(tag: str = "ablation", max_results: int = 50) -> list[dict]:
    """Query PWC API for papers with timing data."""
    ...

def scrape_conference_papers(venue: str, year: int, keywords: list[str]) -> list[dict]:
    """Scrape NeurIPS/ICML/ICLR proceedings for timing keywords."""
    ...

def download_pdf(url: str, save_path: str, max_retries: int = 3) -> bool:
    """Download paper PDF with retry logic."""
    ...

def collect_all_sources(config: dict) -> list[dict]:
    """Execute collection from all sources (PWC + conferences + GitHub)."""
    ...
```

---

### ExtractionModule (`code/extract.py`)

**Dependencies**: PyMuPDF, re, pandas

```python
def parse_pdf_to_text(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    ...

def extract_timing_table(text: str) -> dict | None:
    """
    Parse timing measurements using regex patterns.
    Returns: {"micro_pilot": {...}, "full_scale": {...}} or None
    """
    ...

def compute_overhead_percent(time: float, baseline: float) -> float:
    """Calculate overhead percentage."""
    ...

def extract_metadata(text: str, paper_info: dict) -> dict:
    """Extract hardware, framework, hypothesis type from text."""
    ...

def process_papers_batch(pdf_paths: list[str], paper_metadata: list[dict]) -> list[dict]:
    """Process batch of papers, extract overhead measurements."""
    ...
```

---

### ValidationModule (`code/validate.py`)

**Dependencies**: numpy, pandas

```python
def validate_hypothesis_entry(entry: dict) -> tuple[bool, list[str]]:
    """
    Check completeness of overhead measurements.
    Returns: (is_valid, errors)
    """
    ...

def compute_stratification(corpus: list[dict]) -> dict:
    """
    Stratify corpus by overhead bins (low/mid/high).
    Returns: {"low": count, "mid": count, "high": count, "cv": float}
    """
    ...

def spot_check_sample(corpus: list[dict], sample_rate: float = 0.2) -> list[dict]:
    """Select random 20% sample for manual verification."""
    ...

def generate_validation_report(corpus: list[dict], output_path: str) -> dict:
    """
    Generate validation report with gate decision.
    Returns: {"valid_count": int, "decision": str, "stratification": dict}
    """
    ...
```

---

### MainOrchestrator (`code/main.py`)

**Dependencies**: CollectionModule, ExtractionModule, ValidationModule, json

```python
def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    ...

def save_corpus(corpus: list[dict], output_path: str) -> None:
    """Save corpus to JSON file."""
    ...

def save_checkpoint(data: dict, checkpoint_path: str) -> None:
    """Save intermediate results for recovery."""
    ...

def main() -> None:
    """
    Main pipeline execution:
    1. Load config
    2. Collect papers (with checkpoint)
    3. Extract timing data (with checkpoint)
    4. Validate corpus
    5. Generate report and gate decision
    """
    ...
```

---

## Data Schema

### Paper Metadata Entry

```python
{
  "paper_id": str,                    # Unique identifier
  "title": str,                       # Paper title
  "venue": str,                       # NeurIPS/ICML/ICLR/arXiv
  "year": int,                        # Publication year
  "hypothesis_type": str,             # attention/gradient/regularization
  "overhead_measurements": {
    "micro_pilot": {
      "sample_size": int,             # ≤50 samples
      "time_seconds": float,
      "baseline_time": float,
      "overhead_percent": float       # (time - baseline) / baseline * 100
    },
    "full_scale": {
      "sample_size": int,             # ≥1000 samples
      "time_seconds": float,
      "baseline_time": float,
      "overhead_percent": float
    }
  },
  "hardware": str,                    # GPU/CPU type if reported
  "framework": str,                   # PyTorch/TensorFlow
  "source_url": str                   # Provenance tracking
}
```

---

## File Organization

```
code/
├── collect.py           # Data collection (PWC API + scraping)
├── extract.py           # PDF parsing + timing extraction
├── validate.py          # Corpus validation + stratification
├── main.py              # Pipeline orchestrator
├── config.yaml          # API endpoints, search keywords, thresholds
└── requirements.txt     # Python dependencies

data/retrospective_corpus/
├── papers_metadata.json      # Final corpus (output)
├── raw_papers/               # Downloaded PDFs
│   └── *.pdf
├── checkpoints/              # Intermediate results
│   ├── collected_papers.json
│   └── extracted_data.json
└── validation_report.md      # Gate decision report
```

---

## Configuration (`config.yaml`)

```yaml
collection:
  pwc_api_url: "https://paperswithcode.com/api/v1/papers"
  pwc_tag: "ablation"
  pwc_max_results: 50
  
  conferences:
    - venue: "NeurIPS"
      years: [2020, 2021, 2022, 2023, 2024]
    - venue: "ICML"
      years: [2020, 2021, 2022, 2023, 2024]
    - venue: "ICLR"
      years: [2020, 2021, 2022, 2023, 2024]
  
  keywords: ["ablation study", "overhead", "sample size"]

extraction:
  timing_patterns:
    - "Table \\d+:.*overhead.*sample"
    - "(\\d+)\\s*samples?:\\s*(\\d+\\.?\\d*)\\s*sec"
    - "micro-pilot.*:(\\d+\\.?\\d*).*full.*:(\\d+\\.?\\d*)"
  
  micro_pilot_threshold: 50
  full_scale_threshold: 1000

validation:
  target_count: 30
  pass_threshold: 30
  fail_threshold: 20
  
  stratification:
    low_overhead_max: 20.0
    high_overhead_min: 80.0
    cv_threshold: 0.5
  
  spot_check_rate: 0.2

paths:
  corpus_output: "data/retrospective_corpus/papers_metadata.json"
  raw_papers_dir: "data/retrospective_corpus/raw_papers"
  checkpoints_dir: "data/retrospective_corpus/checkpoints"
  validation_report: "data/retrospective_corpus/validation_report.md"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Collection Pipeline | Query PWC API + scrape conferences + download PDFs | 12 | 3+3+2+4 |
| E-2 | Extraction Logic | PDF parsing + regex extraction + metadata parsing | 14 | 4+4+2+4 |
| E-3 | Validation & Stratification | Completeness checks + bin assignment + CV computation | 10 | 2+2+3+3 |
| E-4 | Orchestration & Reporting | Main pipeline + checkpointing + report generation | 11 | 3+2+3+3 |

**Total Complexity**: 47  
**Distribution**: High(14-17): [E-2], Medium(9-13): [E-1, E-3, E-4], Low(4-8): []

**Complexity Breakdown**:
- E-1: Module_Size(3) + Dependencies(3) + Algorithm(2) + Integration(4) = 12
  - Size: 3 functions (PWC, scrape, download)
  - Deps: requests + beautifulsoup4 + retry logic
  - Algorithm: HTTP GET + HTML parsing (standard)
  - Integration: Config loading + checkpoint saving + error handling
  
- E-2: Module_Size(4) + Dependencies(4) + Algorithm(2) + Integration(4) = 14
  - Size: 4 functions (PDF parse, regex extract, overhead calc, metadata)
  - Deps: PyMuPDF + regex + pandas + text parsing
  - Algorithm: Pattern matching (standard regex)
  - Integration: Batch processing + error handling + field validation
  
- E-3: Module_Size(2) + Dependencies(2) + Algorithm(3) + Integration(3) = 10
  - Size: 2 core functions (validate, stratify)
  - Deps: numpy + pandas (stats)
  - Algorithm: Binning + CV computation (moderate)
  - Integration: Report formatting + spot-check sampling
  
- E-4: Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(3) = 11
  - Size: 3 functions (load config, save corpus, checkpoint)
  - Deps: json + yaml + file I/O
  - Algorithm: State management + recovery logic (moderate)
  - Integration: Pipeline coordination + logging + gate decision

---

## Integration Flow

```
main.py
  ├─> load_config() → config dict
  ├─> collect.py::collect_all_sources(config)
  │     ├─> query_papers_with_code()
  │     ├─> scrape_conference_papers() × N venues
  │     └─> download_pdf() × M papers
  │   [CHECKPOINT: collected_papers.json]
  │
  ├─> extract.py::process_papers_batch(pdfs, metadata)
  │     ├─> parse_pdf_to_text() × M papers
  │     ├─> extract_timing_table()
  │     ├─> compute_overhead_percent()
  │     └─> extract_metadata()
  │   [CHECKPOINT: extracted_data.json]
  │
  ├─> validate.py::generate_validation_report(corpus)
  │     ├─> validate_hypothesis_entry() × N entries
  │     ├─> compute_stratification()
  │     └─> spot_check_sample()
  │   [OUTPUT: validation_report.md + gate decision]
  │
  └─> save_corpus(corpus, output_path)
```

---

## Gate Decision Logic

```python
def decide_gate(valid_count: int, cv: float) -> dict:
    if valid_count >= 30 and cv < 0.5:
        return {
            "decision": "PASS",
            "next_step": "Proceed to H-M1 (correlation analysis)",
            "action": "Use papers_metadata.json as input corpus"
        }
    elif 20 <= valid_count < 30:
        return {
            "decision": "PARTIAL",
            "next_step": "Explore combining retrospective + prospective",
            "action": "Extend collection OR supplement with micro-pilots"
        }
    else:
        return {
            "decision": "FAIL",
            "next_step": "PIVOT to prospective validation",
            "action": "Design 30 new micro-pilot experiments"
        }
```

---

## Dependencies

**Python Packages** (`requirements.txt`):
```
requests>=2.31.0
beautifulsoup4>=4.12.0
PyMuPDF>=1.23.0
pandas>=2.1.0
numpy>=1.24.0
pyyaml>=6.0
```

**External Services**:
- Papers with Code API (public, no auth)
- Conference proceedings (public access)
- GitHub public repos (no auth)

**Hardware**: CPU only, ~500MB storage

---

## Error Handling Strategy

**Collection Errors**:
- HTTP timeouts: Retry 3x with exponential backoff
- 404 Not Found: Log and skip paper
- Rate limits: Respect API limits (100 req/hour for PWC)

**Extraction Errors**:
- PDF parse failure: Log error, skip paper
- Regex no match: Log pattern failure, skip paper
- Missing fields: Mark entry as incomplete, exclude from valid count

**Validation Errors**:
- Invalid overhead calculation: Flag for manual review
- Sample size ratio <10x: Exclude from corpus

---

## Quality Metrics

**Completeness**: 90%+ entries with all required fields  
**Accuracy**: Spot-check validation passes for 80%+ entries  
**Diversity**: ≥3 hypothesis types, ≥2 venues  
**Stratification**: CV <0.5 across low/mid/high overhead bins

---

## Appendix: Regex Patterns

```python
TIMING_PATTERNS = [
    # Pattern 1: Table with overhead vs sample size
    r"Table\s+\d+:.*overhead.*sample.*\n(.*?\n){1,10}",
    
    # Pattern 2: Inline timing comparison
    r"(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec.*?(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec",
    
    # Pattern 3: Micro-pilot vs full-scale
    r"micro-pilot.*?(\d+\.?\d*)\s*sec.*?full.*?(\d+\.?\d*)\s*sec",
    
    # Pattern 4: Ablation timing table
    r"ablation.*?\n.*?(\d+)\s+(\d+\.?\d*).*?\n.*?(\d+)\s+(\d+\.?\d*)"
]
```

---

**Document Version**: 1.0  
**Created**: 2026-08-25  
**Hypothesis**: H-E1 (EXISTENCE, MUST_WORK)
