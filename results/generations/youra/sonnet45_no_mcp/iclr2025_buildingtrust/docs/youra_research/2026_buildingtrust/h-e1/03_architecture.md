# System Architecture: H-E1 Data Extraction Experiment

**Date:** 2026-04-14
**Hypothesis:** H-E1 (EXISTENCE)
**Type:** Data Extraction PoC
**Author:** Architecture Agent
**Phase:** Phase 3 - Implementation Planning

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch (EXISTENCE PoC - no base hypothesis)
**Analyzed Path:** N/A
**Findings:** No existing codebase to analyze. Archived attempts found but starting fresh per EXISTENCE rules.

---

## Knowledge Base Patterns Applied

**MCP Status:** Archon KB unavailable (no_mcp test environment)
**Fallback:** Applied standard data extraction patterns for benchmark analysis experiments

**Applied Patterns:**
- Data extraction pipeline with staged processing (collect → parse → validate → analyze)
- Modular parsers for multiple data formats (PDF, HTML)
- Validation-first architecture with early failure detection
- Structured output with metadata tracking

---

## Architecture Overview

**Project Type:** EXISTENCE (PoC) - Data extraction and validation
**Scope:** Minimal structure to verify that published technical reports contain category-level error rates

**Key Constraints:**
- No model training (data extraction only)
- No GPU required (text processing)
- Runtime target: <5 minutes
- Single-run execution (not iterative training)

---

## Module Structure

### 1. DataCollector (`src/data_collector.py`)

**Dependencies:** requests, BeautifulSoup4

```python
class TechnicalReportCollector:
    def __init__(self, output_dir: str): ...
    def download_report(self, url: str, model_family: str, timepoint: str) -> str: ...
    def list_downloaded_reports(self) -> List[Dict[str, str]]: ...
    def get_metadata(self) -> Dict: ...
```

### 2. ReportParser (`src/parser.py`)

**Dependencies:** DataCollector, PyPDF2, BeautifulSoup4, pandas

```python
class PDFTableParser:
    def __init__(self, pdf_path: str): ...
    def extract_tables(self) -> List[pd.DataFrame]: ...
    def find_benchmark_table(self, benchmark_name: str) -> Optional[pd.DataFrame]: ...

class HTMLTableParser:
    def __init__(self, html_path: str): ...
    def extract_tables(self) -> List[pd.DataFrame]: ...
    def find_benchmark_table(self, benchmark_name: str) -> Optional[pd.DataFrame]: ...

class CategoryExtractor:
    def __init__(self, parser: Union[PDFTableParser, HTMLTableParser]): ...
    def extract_category_data(self, benchmark: str) -> pd.DataFrame: ...
    def normalize_schema(self, raw_df: pd.DataFrame) -> pd.DataFrame: ...
```

### 3. DataValidator (`src/validator.py`)

**Dependencies:** pandas

```python
class DataAvailabilityValidator:
    def __init__(self, extracted_df: pd.DataFrame): ...
    def check_model_family_coverage(self) -> Tuple[bool, int]: ...
    def check_timepoint_coverage(self) -> Dict[str, bool]: ...
    def check_category_granularity(self) -> Dict[str, int]: ...
    def check_data_completeness(self) -> float: ...
    def validate_all(self) -> Dict[str, Any]: ...
```

### 4. MetricsAnalyzer (`src/analyzer.py`)

**Dependencies:** DataValidator, pandas

```python
class GateMetricsAnalyzer:
    def __init__(self, extracted_df: pd.DataFrame): ...
    def compute_family_coverage(self) -> int: ...
    def compute_granularity_metrics(self) -> Dict[str, int]: ...
    def compute_completeness(self) -> float: ...
    def evaluate_gate_condition(self) -> Dict[str, Any]: ...
```

### 5. Visualizer (`src/visualizer.py`)

**Dependencies:** MetricsAnalyzer, matplotlib, seaborn

```python
class ExperimentVisualizer:
    def __init__(self, extracted_df: pd.DataFrame, metrics: Dict): ...
    def plot_gate_metrics(self, save_path: str) -> None: ...
    def plot_granularity_heatmap(self, save_path: str) -> None: ...
    def plot_completeness_matrix(self, save_path: str) -> None: ...
    def plot_temporal_timeline(self, metadata: Dict, save_path: str) -> None: ...
    def generate_all_figures(self, output_dir: str) -> List[str]: ...
```

### 6. ExperimentConfig (`src/config.py`)

**Dependencies:** None

```python
class ExperimentConfig:
    MODEL_FAMILIES: List[str] = ["GPT", "Claude", "Llama"]
    BENCHMARKS: List[str] = ["TruthfulQA", "MMLU"]
    TIMEPOINTS: List[str] = ["baseline", "current"]
    
    REPORT_URLS: Dict[str, Dict[str, str]] = {...}
    
    SUCCESS_THRESHOLDS: Dict[str, Union[int, float]] = {
        "min_families": 3,
        "min_categories": 10,
        "min_completeness": 90.0
    }
    
    OUTPUT_SCHEMA: List[str] = ["model_family", "timepoint", "benchmark", "category", "error_rate"]

def get_config() -> ExperimentConfig: ...
```

### 7. ExperimentRunner (`run_experiment.py`)

**Dependencies:** All modules above

```python
class H_E1_ExperimentRunner:
    def __init__(self, config: ExperimentConfig): ...
    def setup_environment(self) -> None: ...
    def collect_reports(self) -> None: ...
    def parse_and_extract(self) -> pd.DataFrame: ...
    def validate_data(self, df: pd.DataFrame) -> Dict: ...
    def compute_metrics(self, df: pd.DataFrame) -> Dict: ...
    def generate_visualizations(self, df: pd.DataFrame, metrics: Dict) -> None: ...
    def save_outputs(self, df: pd.DataFrame, metrics: Dict) -> None: ...
    def run(self) -> Dict: ...

def main(): ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── data_collector.py      # Report download and storage
│   │   ├── parser.py               # PDF/HTML table extraction
│   │   ├── validator.py            # Data quality checks
│   │   ├── analyzer.py             # Metrics computation
│   │   ├── visualizer.py           # Figure generation
│   │   └── config.py               # Configuration constants
│   ├── run_experiment.py           # Main execution script
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # Setup instructions
├── data/
│   ├── reports/                    # Downloaded technical reports
│   │   ├── gpt4_report.pdf
│   │   ├── claude3_report.html
│   │   └── llama3_report.pdf
│   └── extracted/                  # Processed data outputs
│       ├── h-e1_extracted_data.csv
│       ├── h-e1_metadata.json
│       └── h-e1_validation.json
├── figures/
│   ├── gate_metrics.png
│   ├── granularity_heatmap.png
│   ├── completeness_matrix.png
│   └── temporal_timeline.png
└── logs/
    └── extraction.log
```

---

## Data Flow

1. **Collection Phase**
   - DataCollector downloads reports from configured URLs
   - Stores files in `data/reports/` with metadata

2. **Parsing Phase**
   - PDFTableParser/HTMLTableParser extract tables from reports
   - CategoryExtractor identifies benchmark-specific tables
   - Schema normalization to [model_family, timepoint, benchmark, category, error_rate]

3. **Validation Phase**
   - DataValidator checks coverage, granularity, completeness
   - Early failure if gate condition cannot be met

4. **Analysis Phase**
   - MetricsAnalyzer computes success metrics
   - Gate condition evaluation (≥3 families, ≥10 categories, ≥90% complete)

5. **Visualization Phase**
   - Generate 4 required figures
   - Save to `figures/` directory

6. **Output Phase**
   - Save extracted_data.csv
   - Save metadata.json and validation.json
   - Generate final summary report

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Environment Setup | Install dependencies, create folder structure, configure URLs | 5 | Module(1) + Deps(1) + Algo(1) + Integration(2) |
| E2 | Report Collection | Implement download logic, handle PDF/HTML formats, save metadata | 8 | Module(2) + Deps(2) + Algo(2) + Integration(2) |
| E3 | Table Extraction | Parse PDF/HTML tables, locate benchmark results, extract category data | 12 | Module(3) + Deps(3) + Algo(3) + Integration(3) |
| E4 | Data Validation | Implement coverage checks, granularity checks, completeness metrics | 9 | Module(2) + Deps(2) + Algo(3) + Integration(2) |
| E5 | Metrics & Analysis | Compute gate metrics, evaluate success criteria, generate validation report | 7 | Module(2) + Deps(1) + Algo(2) + Integration(2) |
| E6 | Visualization | Generate 4 required figures, save to figures directory | 10 | Module(2) + Deps(2) + Algo(3) + Integration(3) |
| E7 | Integration & Testing | End-to-end pipeline test, verify outputs, document results | 9 | Module(2) + Deps(2) + Algo(2) + Integration(3) |

**Total Complexity:** 60 points across 7 epics
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E3, E4, E6, E7], Low(4-8): [E1, E2, E5]

**Complexity Scoring:**
- Module_Size: Lines of code estimate (1=<50, 2=50-150, 3=150-300, 4=300-500, 5=>500)
- Dependencies: External libraries needed (1=stdlib, 2=1-2 libs, 3=3-4 libs, 4=5+ libs, 5=complex deps)
- Algorithm: Logic complexity (1=trivial, 2=simple, 3=moderate, 4=complex, 5=very complex)
- Integration: Cross-module interaction (1=isolated, 2=1-2 deps, 3=3-4 deps, 4=5+ deps, 5=full system)

---

## Dependencies

### Python Packages

```txt
pandas>=1.3.0
requests>=2.26.0
beautifulsoup4>=4.10.0
PyPDF2>=2.0.0
matplotlib>=3.4.0
seaborn>=0.11.0
```

### External Resources

**Technical Reports (Manual Download Required):**
- GPT-4: https://arxiv.org/abs/2303.08774
- Claude-3: https://www.anthropic.com/claude-3
- Llama-3: https://ai.meta.com/blog/meta-llama-3/
- GPT-3.5: OpenAI documentation
- Claude-2: Anthropic technical report
- Llama-2: Meta AI research page

**Reference Datasets (Optional):**
- TruthfulQA: `load_dataset("truthful_qa", "generation")`
- MMLU: `load_dataset("cais/mmlu", "all")`

---

## Success Criteria Implementation

### Gate Condition Check

```python
def check_gate_condition(metrics: Dict) -> bool:
    """
    MUST_WORK gate: ≥3 model families with category-level data for both timepoints
    """
    families_ok = metrics['families_with_data'] >= 3
    granularity_ok = (
        metrics['categories_truthfulqa'] >= 10 and
        metrics['categories_mmlu'] >= 10
    )
    completeness_ok = metrics['data_completeness_pct'] >= 90.0
    
    return families_ok and granularity_ok and completeness_ok
```

### Output Validation

**Required Files:**
1. `h-e1_extracted_data.csv` - Structured dataset
2. `h-e1_metadata.json` - Source URLs and timestamps
3. `h-e1_validation.json` - Gate metrics and pass/fail status
4. `figures/gate_metrics.png` - Primary visualization (MANDATORY)
5. `figures/granularity_heatmap.png` - Granularity analysis
6. `figures/completeness_matrix.png` - Coverage matrix
7. `figures/temporal_timeline.png` - Publication timeline

---

## Execution Protocol

### Phase 4 Implementation Steps

1. **Task E1: Environment Setup**
   - Create directory structure
   - Install requirements.txt
   - Configure report URLs in config.py

2. **Task E2: Report Collection**
   - Implement DataCollector
   - Download 6 technical reports (3 families × 2 timepoints)
   - Save metadata (publication dates, URLs)

3. **Task E3: Table Extraction**
   - Implement PDFTableParser and HTMLTableParser
   - Implement CategoryExtractor
   - Test on each downloaded report

4. **Task E4: Data Validation**
   - Implement DataAvailabilityValidator
   - Run validation checks
   - Early exit if gate condition cannot be met

5. **Task E5: Metrics & Analysis**
   - Implement MetricsAnalyzer
   - Compute all success metrics
   - Generate validation report

6. **Task E6: Visualization**
   - Implement ExperimentVisualizer
   - Generate 4 required figures
   - Verify all figures saved correctly

7. **Task E7: Integration & Testing**
   - Implement run_experiment.py main orchestration
   - Run end-to-end test
   - Verify all outputs generated

### Runtime Expectations

- Total execution time: <5 minutes
- GPU: Not required
- Manual intervention: Report downloads may require manual steps if URLs change

---

## Error Handling Strategy

### Graceful Degradation

**Scenario 1: Report Download Fails**
- Retry with exponential backoff (3 attempts)
- Log failure and continue with available reports
- Flag missing data in validation report

**Scenario 2: Table Parsing Fails**
- Try alternative parsing strategy (PDF → text extraction)
- Manual extraction prompt with clear instructions
- Document parsing failures in metadata

**Scenario 3: Insufficient Data**
- If <3 families have data → GATE FAILED
- Generate partial visualization showing gaps
- Clear failure message in validation report

**Scenario 4: Format Variations**
- Implement fallback parsers for common table formats
- Log unrecognized formats
- Provide manual extraction template

---

## Testing Strategy

### Unit Tests (Optional for PoC)

- `test_data_collector.py` - Download and metadata tests
- `test_parser.py` - Table extraction accuracy
- `test_validator.py` - Validation logic correctness
- `test_analyzer.py` - Metrics computation

### Integration Test (Mandatory)

```python
def test_end_to_end():
    """Full pipeline test with mock reports"""
    runner = H_E1_ExperimentRunner(config)
    results = runner.run()
    
    assert results['gate_passed'] == True
    assert os.path.exists('data/extracted/h-e1_extracted_data.csv')
    assert os.path.exists('figures/gate_metrics.png')
    assert len(results['metrics']) == 4
```

---

## Non-Functional Requirements

### Performance
- Report download: <30s per file
- Table extraction: <10s per report
- Full pipeline: <5 minutes total

### Reliability
- Handle missing/malformed tables gracefully
- Validate all outputs before saving
- Atomic writes (temp files → rename)

### Maintainability
- Clear separation of concerns (collection, parsing, validation, analysis)
- Configurable thresholds and URLs
- Comprehensive logging

### Reproducibility
- Deterministic parsing (no random elements)
- Timestamp all operations
- Store source URLs and access dates

---

## Phase 4 Handoff Checklist

Phase 4 Coder must implement:

- [ ] All 7 modules with specified interfaces
- [ ] All 7 Epic tasks completed sequentially
- [ ] Requirements.txt with exact versions
- [ ] run_experiment.py main entry point
- [ ] All 4 required figures generated
- [ ] CSV output with correct schema
- [ ] Metadata and validation JSON files
- [ ] Gate condition evaluation logic
- [ ] Error handling for all failure modes
- [ ] End-to-end integration test
- [ ] README with setup instructions

**Critical Output:** `h-e1_validation.json` must contain `gate_passed: true/false` field

---

## Architecture Validation

### Self-Check

- [x] No ASCII diagrams
- [x] No KB search logs (graceful degradation noted)
- [x] Module sections = interface code only
- [x] 7 Epic tasks with complexity scores
- [x] Total length < 500 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] EXISTENCE rules applied (minimal PoC structure)

### EXISTENCE Compliance

- [x] 4-8 Epic tasks (have 7)
- [x] Minimal file structure (no ablation, no hyperparameter sweeps)
- [x] Single model.py equivalent (parser.py for core logic)
- [x] Simple validation (validator.py + analyzer.py)
- [x] Basic visualization (4 required figures)

---

**Document Status:** ✅ Complete
**Next Phase:** Phase 4 - Implementation (Coder Agent)
**Estimated Implementation Time:** 4-6 hours (development) + <5 minutes (execution)
