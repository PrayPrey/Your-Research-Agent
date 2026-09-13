# Architecture Design: H-M2 Protocol Consistency via Artifact Quality

**Date:** 2026-07-12  
**Hypothesis:** h-m2 (MECHANISM)  
**Type:** Observational Study (Content Analysis + Statistical Analysis)  
**Applied Patterns:** API-based paper retrieval, PDF text extraction, statistical correlation analysis, rubric-based coding

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from H-M1 code  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Findings:** Reusing PapersWithCodeCollector (API client), ArtifactQualityRubric pattern, inter-rater reliability calculation, and visualization suite structure. Extending to multi-paper protocol extraction and consistency analysis.

---

## Overview

H-M2 tests whether high-quality ML benchmark artifacts lead to higher protocol consistency rates across independent research groups. This extends H-M1's artifact quality assessment by analyzing citing papers to measure how consistently researchers implement protocols.

**Key Differences from H-M1:**
- H-M1: Assessed artifact quality via rubric scoring
- H-M2: Analyzes protocol consistency across citing papers
- New components: Paper retrieval, PDF parsing, protocol extraction, Spearman correlation analysis
- Reused: Rubric dimensions, inter-rater reliability validation, API client patterns

---

## Module Structure

### 1. Configuration (`config.py`)

**Dependencies:** None

```python
class ProtocolStudyConfig:
    """Configuration for protocol consistency study."""
    
    # API Settings (reused from H-M1)
    PWC_API_URL: str = "https://paperswithcode.com/api/v1/"
    S2_API_URL: str = "https://api.semanticscholar.org/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # Sampling Parameters
    BENCHMARK_COUNT: int = 10
    PAPERS_PER_BENCHMARK: int = 5
    INTER_RATER_SAMPLE_SIZE: int = 10
    
    # Protocol Dimensions (from H-M1 rubric)
    PROTOCOL_DIMENSIONS: list = ["data_splits", "preprocessing", "evaluation_protocol", "hyperparameters"]
    
    # Gate Thresholds
    MIN_KAPPA: float = 0.8
    PRIMARY_THRESHOLD: float = 0.70
    SECONDARY_RHO_THRESHOLD: float = 0.4
    SECONDARY_P_THRESHOLD: float = 0.05
    
    # Paths
    H_M1_QUALITY_FILE: str = "../h-m1/outputs/artifact_quality.csv"
    RAW_PAPERS_DIR: str = "data/citing_papers"
    PROTOCOL_CODING_FILE: str = "data/protocol_coding.csv"
    CONSISTENCY_RESULTS_FILE: str = "results/consistency_by_stratum.csv"
    HYPOTHESIS_TEST_FILE: str = "results/hypothesis_test.json"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"
```

---

### 2. Data Collection (`data/paper_retrieval.py`)

**Dependencies:** requests, pandas, config

```python
class BenchmarkSelector:
    """Select benchmarks from H-M1 quality scores, stratified by quality."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def load_h_m1_quality_scores(self, file_path: str) -> pd.DataFrame: ...
    
    def stratify_by_quality(self, quality_df: pd.DataFrame) -> dict:
        """Stratify into High (>7.0), Medium (4-7), Low (<4)."""
        ...
    
    def sample_benchmarks(self, stratified: dict, total_count: int = 10) -> pd.DataFrame: ...


class PaperRetriever:
    """Retrieve citing papers using Papers with Code + Semantic Scholar APIs."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def fetch_citing_papers(self, benchmark_id: str, max_papers: int = 5) -> pd.DataFrame:
        """Query Papers with Code API for benchmark citations."""
        ...
    
    def download_pdf_from_s2(self, paper_id: str, output_dir: str) -> str:
        """Download full paper PDF via Semantic Scholar API."""
        ...
    
    def download_pdf_from_arxiv(self, arxiv_id: str, output_dir: str) -> str:
        """Fallback: Download from arXiv if Semantic Scholar fails."""
        ...
    
    def retrieve_papers_for_benchmarks(self, benchmarks: pd.DataFrame, output_dir: str) -> pd.DataFrame:
        """Retrieve 5 papers per benchmark (50 total)."""
        ...
```

---

### 3. Protocol Extraction (`extraction/protocol_parser.py`)

**Dependencies:** PyMuPDF (or pdfplumber), re, pandas

```python
class PDFParser:
    """Extract Methods sections from academic PDFs."""
    
    def __init__(self): ...
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract all text from PDF using PyMuPDF."""
        import fitz
        ...
    
    def identify_methods_section(self, full_text: str) -> str:
        """Identify Methods/Experimental Setup section via regex."""
        ...


class ProtocolExtractor:
    """Extract protocol details from Methods sections."""
    
    def __init__(self, rubric_dimensions: list): ...
    
    def extract_data_splits(self, methods_text: str) -> dict:
        """Extract train/val/test split ratios."""
        ...
    
    def extract_preprocessing(self, methods_text: str) -> dict:
        """Extract normalization, augmentation, resizing specs."""
        ...
    
    def extract_evaluation_protocol(self, methods_text: str) -> dict:
        """Extract metrics, validation strategy."""
        ...
    
    def extract_hyperparameters(self, methods_text: str) -> dict:
        """Extract optimizer, LR, batch size, epochs."""
        ...
    
    def extract_all_protocols(self, methods_text: str) -> dict:
        """Extract all 4 dimensions."""
        ...
```

---

### 4. Protocol Coding (`coding/rubric_coder.py`)

**Dependencies:** pandas, config

```python
class ProtocolCoder:
    """Binary coding: Identical (1) vs Divergent (0) relative to benchmark spec."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def load_benchmark_spec(self, benchmark_id: str) -> dict:
        """Load ground-truth protocol from benchmark documentation."""
        ...
    
    def compare_protocols(self, paper_protocol: dict, benchmark_spec: dict) -> dict:
        """Binary comparison for each dimension (1=identical, 0=divergent)."""
        ...
    
    def code_paper(self, paper_id: str, benchmark_id: str, methods_text: str) -> dict:
        """Code single paper against benchmark spec."""
        ...
    
    def code_all_papers(self, papers: pd.DataFrame, output_file: str):
        """Code all 50 papers and save to protocol_coding.csv."""
        ...


class InterRaterValidator:
    """Validate coding reliability with 2 independent raters on 20% sample."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def sample_for_double_coding(self, papers: pd.DataFrame, sample_size: int = 10) -> pd.DataFrame: ...
    
    def calculate_dimension_kappa(self, rater1: pd.Series, rater2: pd.Series) -> float:
        """Cohen's kappa for single dimension."""
        from sklearn.metrics import cohen_kappa_score
        ...
    
    def calculate_all_kappas(self, rater1_df: pd.DataFrame, rater2_df: pd.DataFrame) -> dict:
        """Kappa for each of 4 dimensions."""
        ...
    
    def check_reliability_gate(self, kappa_results: dict, threshold: float = 0.8) -> bool: ...
```

---

### 5. Consistency Analysis (`analysis/consistency.py`)

**Dependencies:** pandas, numpy, scipy.stats

```python
class ProtocolConsistencyCalculator:
    """Compute consistency rates per benchmark and stratum."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def compute_benchmark_consistency(self, benchmark_papers: pd.DataFrame) -> float:
        """% of papers with ≥3/4 dimensions identical."""
        ...
    
    def compute_stratum_consistency(self, benchmarks: pd.DataFrame, quality_df: pd.DataFrame) -> pd.DataFrame:
        """Consistency rate by quality stratum (High/Medium/Low)."""
        ...
    
    def save_consistency_results(self, consistency_df: pd.DataFrame, output_file: str): ...


class CorrelationAnalyzer:
    """Test correlation between artifact quality and protocol consistency."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def compute_spearman_correlation(self, quality_scores: pd.Series, consistency_rates: pd.Series) -> dict:
        """Spearman ρ and p-value."""
        from scipy.stats import spearmanr
        ...
    
    def check_correlation_gate(self, rho: float, p_value: float) -> bool:
        """Is ρ > 0.4 and p < 0.05?"""
        ...
```

---

### 6. Statistical Testing (`analysis/hypothesis_test.py`)

**Dependencies:** numpy, scipy.stats

```python
class HypothesisTester:
    """Test primary and secondary success criteria."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def test_primary_metric(self, high_quality_consistency: float) -> dict:
        """Is consistency rate > 70% for high-quality artifacts?"""
        ...
    
    def test_secondary_metric(self, rho: float, p_value: float) -> dict:
        """Is Spearman ρ > 0.4 with p < 0.05?"""
        ...
    
    def evaluate_gate(self, primary_result: dict, secondary_result: dict) -> dict:
        """Gate decision: PASS if primary OR secondary succeeds."""
        ...
    
    def save_results(self, gate_result: dict, output_file: str): ...
```

---

### 7. Visualization (`visualization/plots.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class ProtocolVisualization:
    """Generate 4 required figures."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def plot_gate_metrics(self, primary_actual: float, secondary_rho: float, save_path: str):
        """MANDATORY: Bar chart comparing Target vs Actual for both metrics."""
        ...
    
    def plot_consistency_by_quality(self, consistency_df: pd.DataFrame, save_path: str):
        """Box plot of consistency rates by stratum."""
        ...
    
    def plot_quality_consistency_scatter(self, quality_scores: pd.Series, consistency_rates: pd.Series, 
                                          rho: float, save_path: str):
        """Scatter plot with regression line and Spearman ρ annotation."""
        ...
    
    def plot_dimension_heatmap(self, protocol_coding: pd.DataFrame, save_path: str):
        """Heatmap: benchmarks × dimensions consistency."""
        ...
    
    def generate_all_figures(self, results: dict, output_dir: str): ...
```

---

### 8. Report Generation (`reporting/validator.py`)

**Dependencies:** All analysis modules

```python
class ValidationReportGenerator:
    """Generate 04_validation.md with gate decision logic."""
    
    def __init__(self, config: ProtocolStudyConfig): ...
    
    def load_results(self, results_dir: str) -> dict: ...
    
    def determine_gate_status(self, primary_pass: bool, secondary_pass: bool) -> str:
        """PASS (either passes), EXPLORE (both fail)."""
        ...
    
    def generate_report(self, results: dict, output_path: str): ...
```

---

### 9. Main Orchestration (`main.py`)

**Dependencies:** All modules

```python
def run_protocol_consistency_study():
    """Execute H-M2 protocol consistency study."""
    
    # Phase 1: Benchmark selection (stratified by H-M1 quality)
    selector = BenchmarkSelector(config)
    quality_scores = selector.load_h_m1_quality_scores(config.H_M1_QUALITY_FILE)
    stratified = selector.stratify_by_quality(quality_scores)
    benchmarks = selector.sample_benchmarks(stratified, total_count=10)
    
    # Phase 2: Paper retrieval
    retriever = PaperRetriever(config)
    papers = retriever.retrieve_papers_for_benchmarks(benchmarks, config.RAW_PAPERS_DIR)
    
    # Phase 3: Protocol extraction
    parser = PDFParser()
    extractor = ProtocolExtractor(config.PROTOCOL_DIMENSIONS)
    for idx, row in papers.iterrows():
        pdf_path = row['pdf_path']
        full_text = parser.extract_text(pdf_path)
        methods_text = parser.identify_methods_section(full_text)
        protocols = extractor.extract_all_protocols(methods_text)
        # Store protocols for coding
    
    # Phase 4: Protocol coding (manual or semi-automated)
    coder = ProtocolCoder(config)
    coder.code_all_papers(papers, config.PROTOCOL_CODING_FILE)
    
    # Phase 5: Inter-rater reliability validation (on 20% sample)
    validator = InterRaterValidator(config)
    sample_papers = validator.sample_for_double_coding(papers, sample_size=10)
    # Two raters independently code sample
    kappa_results = validator.calculate_all_kappas(rater1_df, rater2_df)
    if not validator.check_reliability_gate(kappa_results, threshold=0.8):
        print("⚠️ Kappa < 0.8: Refine rubric and re-code")
        return
    
    # Phase 6: Consistency analysis
    consistency_calc = ProtocolConsistencyCalculator(config)
    consistency_df = consistency_calc.compute_stratum_consistency(benchmarks, quality_scores)
    consistency_calc.save_consistency_results(consistency_df, config.CONSISTENCY_RESULTS_FILE)
    
    # Phase 7: Correlation analysis
    corr_analyzer = CorrelationAnalyzer(config)
    corr_result = corr_analyzer.compute_spearman_correlation(
        quality_scores['quality_score'], 
        consistency_df['mean_consistency']
    )
    
    # Phase 8: Hypothesis testing
    tester = HypothesisTester(config)
    primary_result = tester.test_primary_metric(
        consistency_df[consistency_df['stratum'] == 'High']['mean_consistency'].mean()
    )
    secondary_result = tester.test_secondary_metric(corr_result['rho'], corr_result['p_value'])
    gate_result = tester.evaluate_gate(primary_result, secondary_result)
    tester.save_results(gate_result, config.HYPOTHESIS_TEST_FILE)
    
    # Phase 9: Visualization
    viz = ProtocolVisualization(config)
    viz.generate_all_figures(results, config.FIGURES_DIR)
    
    # Phase 10: Report
    reporter = ValidationReportGenerator(config)
    results = {
        'primary_metric': primary_result,
        'secondary_metric': secondary_result,
        'gate_result': gate_result,
        'kappa_results': kappa_results,
        'consistency_df': consistency_df
    }
    reporter.generate_report(results, config.OUTPUT_FILE)


if __name__ == "__main__":
    config = ProtocolStudyConfig()
    run_protocol_consistency_study()
```

---

## File Organization

```
h-m2/
├── code/
│   ├── config.py                          # Study configuration
│   ├── main.py                            # Orchestration script
│   ├── data/
│   │   ├── paper_retrieval.py             # BenchmarkSelector, PaperRetriever
│   ├── extraction/
│   │   ├── protocol_parser.py             # PDFParser, ProtocolExtractor
│   ├── coding/
│   │   ├── rubric_coder.py                # ProtocolCoder, InterRaterValidator
│   ├── analysis/
│   │   ├── consistency.py                 # ProtocolConsistencyCalculator, CorrelationAnalyzer
│   │   ├── hypothesis_test.py             # HypothesisTester
│   ├── visualization/
│   │   ├── plots.py                       # ProtocolVisualization
│   ├── reporting/
│   │   ├── validator.py                   # ValidationReportGenerator
│   └── tests/
│       ├── test_protocol_extraction.py
│       ├── test_consistency.py
│       └── test_correlation.py
├── data/
│   ├── selected_benchmarks.csv            # 10 benchmarks (stratified)
│   ├── citing_papers/                     # 50 PDFs
│   │   ├── benchmark1_paper1.pdf
│   │   └── ...
│   ├── protocol_coding.csv                # 50 rows × 4 dimensions (binary)
│   └── rater_validation/                  # Inter-rater sample (10 papers)
│       ├── rater1_scores.csv
│       └── rater2_scores.csv
├── results/
│   ├── consistency_by_stratum.csv         # High/Medium/Low consistency rates
│   └── hypothesis_test.json               # Gate decision
├── figures/
│   ├── gate_metrics.png                   # MANDATORY
│   ├── consistency_by_quality.png
│   ├── quality_consistency_scatter.png
│   └── dimension_heatmap.png
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md                     # This document
└── 04_validation.md                       # Generated by code
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-M1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| PapersWithCodeCollector | `from h_m1.data.collector import PapersWithCodeCollector` | `h-m1/code/data/collector.py` |
| ArtifactQualityRubric | `from h_m1.main import ArtifactQualityRubric` | `h-m1/code/main.py` |
| QualityStudyConfig | `from h_m1.config import QualityStudyConfig` | `h-m1/code/config.py` |

**Verified from:** `docs/youra_research/h-m1/code/` (actual implementation)

**Reuse Strategy:**
- PapersWithCodeCollector: Reuse API client class directly (same rate limiting, retry logic)
- ArtifactQualityRubric: Reuse RUBRIC_DIMENSIONS structure for protocol coding
- Config pattern: Extend dataclass structure with H-M2-specific parameters

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Benchmark Selection | Load H-M1 quality scores, stratify by quality, sample 10 benchmarks | 8 | 2+2+2+2 (load CSV=2, stratification=2, sampling=2, validation=2) |
| M2-2 | Paper Retrieval API Integration | Papers with Code + Semantic Scholar API clients for citing papers | 14 | 4+3+4+3 (PWC API=4, S2 API=3, PDF download=4, error handling=3) |
| M2-3 | PDF Parsing Infrastructure | PyMuPDF integration, Methods section extraction via regex | 12 | 3+3+4+2 (PyMuPDF wrapper=3, text extraction=3, section detection=4, validation=2) |
| M2-4 | Protocol Extraction | Extract 4 dimensions from Methods text (NLP + regex patterns) | 16 | 4+4+4+4 (data_splits=4, preprocessing=4, evaluation=4, hyperparameters=4) |
| M2-5 | Protocol Coding System | Binary comparison against benchmark specs, coding rubric | 11 | 3+2+4+2 (rubric definition=3, spec loading=2, comparison logic=4, CSV output=2) |
| M2-6 | Inter-Rater Reliability | Cohen's kappa for 4 dimensions on 20% sample | 10 | 2+3+3+2 (sampling=2, kappa calculation=3, validation=3, reporting=2) |
| M2-7 | Consistency Analysis | Compute consistency rates per benchmark and stratum | 12 | 3+3+4+2 (benchmark-level=3, stratum aggregation=3, statistical tests=4, output=2) |
| M2-8 | Correlation Analysis | Spearman correlation between quality and consistency | 9 | 2+2+3+2 (data prep=2, Spearman computation=2, interpretation=3, gate check=2) |
| M2-9 | Hypothesis Testing | Primary (>70%) and secondary (ρ>0.4) metric gates | 10 | 2+3+3+2 (primary test=2, secondary test=3, gate logic=3, JSON output=2) |
| M2-10 | Visualization Suite | 4 plots (gate metrics, box plot, scatter, heatmap) | 13 | 3+3+4+3 (gate metrics=3, box plot=3, scatter+regression=4, heatmap=3) |
| M2-11 | Report Generation | 04_validation.md with gate decision + metrics | 11 | 3+2+4+2 (markdown template=3, data aggregation=2, gate rendering=4, file I/O=2) |
| M2-12 | Testing Suite | Unit tests for protocol extraction, consistency, correlation | 12 | 3+3+4+2 (extraction tests=3, consistency tests=3, correlation tests=4, fixtures=2) |

**Complexity Distribution:**
- High (14-17): [M2-2, M2-4]
- Medium (9-13): [M2-1, M2-3, M2-5, M2-6, M2-7, M2-8, M2-9, M2-10, M2-11, M2-12]
- Low (4-8): []

**Total Complexity:** 138 (average 11.5 per task)

---

## Key Design Decisions

1. **Reuse H-M1 API Client:** PapersWithCodeCollector provides proven rate limiting and retry logic. No need to reimplement.

2. **PDF Parsing Strategy:** PyMuPDF (fitz) primary, pdfplumber fallback. Methods section detection via regex patterns (common headings: "Methods", "Experimental Setup", "Implementation Details").

3. **Protocol Coding Approach:** Binary (1/0) instead of Likert scale. Reduces inter-rater disagreement. Identical=1 only if explicit match with benchmark spec.

4. **Inter-Rater Reliability Gate:** Same κ ≥ 0.8 threshold as H-M1. Checked before consistency analysis (hierarchical validation).

5. **Gate Logic:** OR condition (primary OR secondary). More lenient than H-M1 MUST_WORK. Reflects exploratory nature of mechanism testing.

6. **Stratified Sampling:** Ensures quality distribution coverage. Prevents all-high or all-low quality benchmarks which would prevent dose-response analysis.

---

## Gate Decision Logic

```
IF kappa < 0.8:
    → Measurement unreliable
    → Refine rubric and re-code
    → DO NOT proceed to consistency analysis
ELIF primary_metric > 0.70:
    → PASS: High-quality artifacts enable consistency
    → Proceed to H-M3
ELIF secondary_metric (rho > 0.4 AND p < 0.05):
    → PASS: Dose-response relationship confirmed
    → Proceed to H-M3
ELSE:
    → EXPLORE: Identify missing specifications
    → Analyze which dimensions (splits, preprocessing, etc.) fail
```

---

## Statistical Validation Requirements

1. **Inter-Rater Reliability (Cohen's Kappa):**
   - Metric: `sklearn.metrics.cohen_kappa_score(rater1, rater2)` per dimension
   - Threshold: > 0.8 (same as H-M1)
   - Sample: 10 papers (20% of corpus)

2. **Primary Metric (Protocol Consistency Rate):**
   - Metric: Mean consistency for High quality stratum (>7.0)
   - Threshold: > 70%
   - Calculation: % of benchmarks where ≥80% of papers use identical protocols

3. **Secondary Metric (Spearman Correlation):**
   - Metric: `scipy.stats.spearmanr(quality_scores, consistency_rates)`
   - Thresholds: ρ > 0.4 AND p < 0.05
   - Interpretation: Moderate positive correlation

4. **Baseline Comparison (Exploratory):**
   - One-sample t-test vs 50% random baseline
   - Purpose: Demonstrate consistency > chance

---

## Implementation Notes

**PDF Parsing Challenges:**
- Papers use diverse formatting (columns, fonts, sections)
- Methods section may be named differently ("Experiments", "Methodology")
- Solution: Multiple regex patterns + manual verification of extraction quality

**Protocol Extraction Strategy:**
- Start with keyword matching (e.g., "train/val/test: 80/10/10")
- Fallback to manual extraction for ambiguous cases
- Flag papers with insufficient detail for exclusion

**API Rate Limiting:**
- Papers with Code: 1 req/sec
- Semantic Scholar: 1 req/sec  
- Total data collection: ~3-5 hours for 50 papers

**Error Handling:**
- Missing PDFs: Skip and log (require min 3 papers per benchmark)
- Parsing failures: Manual fallback for Methods section
- API failures: Retry with exponential backoff (same as H-M1)

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)
