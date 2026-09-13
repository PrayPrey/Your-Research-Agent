# Logic Design: H-E1 Retrospective Corpus Collection

**Hypothesis**: h-e1 (EXISTENCE)  
**Created**: 2026-08-25  
**Budget**: 8 subtasks (E-2: 4, E-1/E-3/E-4: 4)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch - no existing code to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - designing new data collection pipeline

---

## Knowledge Base Patterns

**Applied**: ETL Pipeline Pattern (data collection, extraction, validation stages with checkpointing)

---

## E-1: Collection Pipeline [Complexity: 12, Budget: 1/8]

### API Signatures

```python
def query_papers_with_code(
    tag: str = "ablation",
    max_results: int = 50,
    api_url: str = "https://paperswithcode.com/api/v1/papers"
) -> list[dict]:
    """Query PWC API. Returns: [{"paper_id": str, "title": str, "pdf_url": str}, ...]"""
    ...

def scrape_conference_papers(venue: str, year: int, keywords: list[str]) -> list[dict]:
    """Scrape proceedings. Returns: [{"paper_id": str, "pdf_url": str}, ...]"""
    ...

def download_pdf(url: str, save_path: str, max_retries: int = 3) -> bool:
    """Download with retry. Returns: success flag"""
    ...

def collect_all_sources(config: dict) -> list[dict]:
    """Execute collection. Returns: [{"paper_id": str, "pdf_path": str}, ...]"""
    ...
```

### Subtasks [1/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Collection orchestration | requests.get() + BeautifulSoup + retry logic |

---

## E-2: Extraction Logic [Complexity: 14, Budget: 4/8]

### API Signatures

```python
def parse_pdf_to_text(pdf_path: str) -> str:
    """Extract text. Returns: full text string"""
    ...

def extract_timing_table(text: str, patterns: list[str]) -> dict | None:
    """
    Parse timing measurements.
    Returns: {"micro_pilot": {"sample_size": int, "time_seconds": float, "baseline_time": float},
              "full_scale": {"sample_size": int, "time_seconds": float, "baseline_time": float}} or None
    """
    ...

def compute_overhead_percent(time: float, baseline: float) -> float:
    """Calculate overhead. Returns: (time - baseline) / baseline * 100"""
    return (time - baseline) / baseline * 100

def extract_metadata(text: str, paper_info: dict) -> dict:
    """Extract hardware/framework/type. Returns: {"hardware": str, "framework": str, "hypothesis_type": str}"""
    ...

def process_papers_batch(pdf_paths: list[str], paper_metadata: list[dict], config: dict) -> list[dict]:
    """Process batch. Returns: [{...overhead_measurements...}, ...]"""
    ...
```

### Regex Patterns

```python
TIMING_PATTERNS = [
    r"(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec.*?(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec",
    r"micro-pilot.*?(\d+\.?\d*)\s*sec.*?full.*?(\d+\.?\d*)\s*sec"
]
```

### Subtasks [4/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | PDF parsing | PyMuPDF fitz.open() |
| L-2-2 | Regex extraction | re.findall() for timing patterns |
| L-2-3 | Overhead computation | Percentage calculation with 10x ratio check |
| L-2-4 | Metadata parsing | Keyword search for hardware/framework |

---

## E-3: Validation & Stratification [Complexity: 10, Budget: 2/8]

### API Signatures

```python
def validate_hypothesis_entry(entry: dict) -> tuple[bool, list[str]]:
    """Check completeness. Returns: (is_valid, ["error_msg", ...])"""
    ...

def compute_stratification(corpus: list[dict]) -> dict:
    """
    Stratify by overhead bins.
    Returns: {"low": int, "mid": int, "high": int, "cv": float}
    """
    ...

def spot_check_sample(corpus: list[dict], sample_rate: float = 0.2) -> list[dict]:
    """Random sample. Returns: sampled entries"""
    ...

def generate_validation_report(corpus: list[dict], output_path: str) -> dict:
    """
    Generate report with gate decision.
    Returns: {"valid_count": int, "decision": str, "stratification": dict}
    """
    ...
```

### Gate Decision Logic

```python
def decide_gate(valid_count: int, cv: float) -> dict:
    if valid_count >= 30 and cv < 0.5:
        return {"decision": "PASS", "next_step": "Proceed to H-M1"}
    elif 20 <= valid_count < 30:
        return {"decision": "PARTIAL", "next_step": "Extend collection"}
    else:
        return {"decision": "FAIL", "next_step": "PIVOT to prospective"}
```

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Entry validation | Field completeness checks |
| L-3-2 | Stratification | Binning + CV computation (np.std / np.mean) |

---

## E-4: Orchestration & Reporting [Complexity: 11, Budget: 1/8]

### API Signatures

```python
def load_config(config_path: str = "code/config.yaml") -> dict:
    """Load config. Returns: config dict"""
    ...

def save_corpus(corpus: list[dict], output_path: str) -> None:
    """Save to JSON."""
    ...

def save_checkpoint(data: dict, checkpoint_path: str) -> None:
    """Save intermediate results."""
    ...

def main() -> None:
    """
    Pipeline execution:
    1. Load config
    2. Collect papers → checkpoint
    3. Extract timing data → checkpoint
    4. Validate corpus
    5. Generate report
    """
    ...
```

### Subtasks [1/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Main orchestrator | Pipeline coordination with checkpointing |

---

## Budget Summary

| Epic | Used | Total |
|------|------|-------|
| E-1 | 1 | 8 |
| E-2 | 4 | 8 |
| E-3 | 2 | 8 |
| E-4 | 1 | 8 |
| **Total** | **8** | **8** |

---

## Data Schema (Output)

```python
# data/retrospective_corpus/papers_metadata.json
[
  {
    "paper_id": str,
    "title": str,
    "venue": str,
    "year": int,
    "hypothesis_type": str,
    "overhead_measurements": {
      "micro_pilot": {
        "sample_size": int,           # <= 50
        "time_seconds": float,
        "baseline_time": float,
        "overhead_percent": float
      },
      "full_scale": {
        "sample_size": int,           # >= 1000
        "time_seconds": float,
        "baseline_time": float,
        "overhead_percent": float
      }
    },
    "hardware": str,
    "framework": str,
    "source_url": str
  }
]
```

---

**Document Version**: 1.0  
**Created**: 2026-08-25  
**Hypothesis**: H-E1 (EXISTENCE, MUST_WORK)
