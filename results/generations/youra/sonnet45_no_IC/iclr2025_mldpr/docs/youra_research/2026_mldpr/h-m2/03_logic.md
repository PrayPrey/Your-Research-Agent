# Logic Design: H-M2 Protocol Consistency via Artifact Quality

**Date:** 2026-07-12  
**Hypothesis:** h-m2 (MECHANISM)  
**Type:** Observational Study (Content Analysis + Statistical Correlation)  
**Budget:** 11 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from H-M1 actual code  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Relevant Symbols:** PapersWithCodeCollector, QualityStudyConfig, cohen_kappa_score usage patterns

**Key Findings:**
- PapersWithCodeCollector: Uses `collect_with_retry()` method, not `fetch_with_retry()`
- QualityStudyConfig: Dataclass pattern with field() defaults for dicts/lists
- Kappa: Implemented via sklearn.metrics.cohen_kappa_score directly, no wrapper

---

## Applied Patterns (Archon KB)

**Applied:** Standard statistical libraries (scipy, sklearn), requests retry pattern, PyMuPDF for PDF parsing

KB searches confirmed:
- Spearman correlation: `scipy.stats.spearmanr`
- Cohen's kappa: `sklearn.metrics.cohen_kappa_score`
- PDF parsing: PyMuPDF (fitz) recommended for text extraction
- Protocol extraction: Regex-based NLP patterns

---

## M2-1: Benchmark Selection and Stratification [Complexity: 8, Budget: 3]

**Applied:** Pandas stratified sampling, H-M1 quality score integration

### API Signatures

```python
from typing import Dict
import pandas as pd
from dataclasses import dataclass, field


@dataclass
class ProtocolStudyConfig:
    """Configuration for H-M2 protocol consistency study."""
    
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
    PROTOCOL_DIMENSIONS: list = field(default_factory=lambda: [
        "data_splits", "preprocessing", "evaluation_protocol", "hyperparameters"
    ])
    
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


class BenchmarkSelector:
    """Select benchmarks from H-M1 quality scores, stratified by quality terciles."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize selector."""
        self.config = config
    
    def load_h_m1_quality_scores(self, file_path: str) -> pd.DataFrame:
        """Load H-M1 artifact quality scores. Returns: [20, ~6] (id, name, quality, dimensions)"""
        ...
    
    def stratify_by_quality(self, quality_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Stratify into High (>7.0), Medium (4-7), Low (<4).
        Returns: {'High': df_high, 'Medium': df_medium, 'Low': df_low}
        """
        ...
    
    def sample_benchmarks(
        self, 
        stratified: Dict[str, pd.DataFrame], 
        total_count: int = 10
    ) -> pd.DataFrame:
        """Proportional sampling from strata. Returns: [10, ~6]"""
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Load H-M1 CSV | pd.read_csv with validation |
| L-1-2 | Stratification logic | Cut into terciles by quality_score |
| L-1-3 | Proportional sampling | Sample 3/4/3 from High/Med/Low |

---

## M2-2: Paper Retrieval API Integration [Complexity: 14, Budget: 3]

**Applied:** Requests session with retry logic (H-M1 pattern), PDF download via S2 API

### API Signatures

```python
from typing import Optional
import requests
import pandas as pd


class PaperRetriever:
    """Retrieve citing papers via Papers with Code + Semantic Scholar APIs."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize retriever."""
        self.config = config
        self.session = requests.Session()
        self.last_request_time: float = 0
    
    def _rate_limit_wait(self) -> None:
        """Enforce rate limiting. Same pattern as H-M1."""
        ...
    
    def fetch_citing_papers(
        self, 
        benchmark_id: str, 
        max_papers: int = 5
    ) -> pd.DataFrame:
        """
        Query Papers with Code API for citing papers.
        Returns: [N_papers, ~8] (paper_id, title, authors, year, url, arxiv_id)
        """
        ...
    
    def download_pdf_from_s2(self, paper_id: str, output_dir: str) -> Optional[str]:
        """
        Download PDF via Semantic Scholar API.
        Returns: file path if successful, None otherwise
        """
        ...
    
    def download_pdf_from_arxiv(self, arxiv_id: str, output_dir: str) -> Optional[str]:
        """
        Fallback: Download from arXiv.
        Returns: file path if successful, None otherwise
        """
        ...
    
    def retrieve_papers_for_benchmarks(
        self, 
        benchmarks: pd.DataFrame, 
        output_dir: str
    ) -> pd.DataFrame:
        """
        Retrieve 5 papers per benchmark (50 total).
        Returns: [50, ~10] (benchmark_id, paper_id, pdf_path, title, year)
        """
        ...
```

### Pseudo-code

```
1. For each benchmark in sample:
   - Query PWC API: /papers/{benchmark_id}/citing
   - Extract paper metadata (title, authors, arxiv_id, S2_id)
   - Select first 5 papers with PDF availability
2. For each paper:
   - Try download_pdf_from_s2(S2_id)
   - If fails: download_pdf_from_arxiv(arxiv_id)
   - Save to output_dir/{benchmark_id}_{paper_idx}.pdf
3. Return DataFrame with pdf_path column
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | PWC API client | fetch_citing_papers with pagination |
| L-2-2 | S2 PDF download | HTTP download with retry logic |
| L-2-3 | arXiv fallback | Alternative download source |

---

## M2-3: PDF Parsing Infrastructure [Complexity: 12, Budget: 2]

**Applied:** PyMuPDF (fitz) for text extraction, regex for section detection

### API Signatures

```python
import fitz  # PyMuPDF
from typing import Optional


class PDFParser:
    """Extract Methods sections from academic PDFs."""
    
    def __init__(self):
        """Initialize parser."""
        pass
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from PDF.
        Returns: full text string
        """
        ...
    
    def identify_methods_section(self, full_text: str) -> Optional[str]:
        """
        Identify Methods/Experimental Setup section via regex.
        Patterns: "Methods", "Experimental Setup", "Implementation Details", "Experiments"
        Returns: extracted section text or None if not found
        """
        ...
```

### Pseudo-code

```
1. Open PDF with fitz.open(pdf_path)
2. Extract text page by page:
   - text = page.get_text()
   - Accumulate into full_text
3. Regex patterns for Methods section:
   - r'\n(?:Methods|Experimental Setup|Implementation Details)\s*\n'
   - Extract until next section header (Introduction, Results, etc.)
4. Return section text (typically 500-2000 words)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | PyMuPDF wrapper | fitz text extraction with error handling |
| L-3-2 | Section detection | Regex patterns for Methods section |

---

## M2-4: Protocol Extraction [Complexity: 16, Budget: 1]

**Applied:** Regex patterns for extracting structured information from Methods text

### API Signatures

```python
from typing import Dict, Optional
import re


class ProtocolExtractor:
    """Extract 4 protocol dimensions from Methods sections."""
    
    def __init__(self, rubric_dimensions: list):
        """Initialize extractor with dimension names."""
        self.dimensions = rubric_dimensions
    
    def extract_data_splits(self, methods_text: str) -> Dict[str, Optional[str]]:
        """
        Extract train/val/test split ratios.
        Pattern: "80/10/10", "train: 80%, val: 10%, test: 10%"
        Returns: {'train': '80', 'val': '10', 'test': '10'} or {'train': None, ...}
        """
        ...
    
    def extract_preprocessing(self, methods_text: str) -> Dict[str, Optional[str]]:
        """
        Extract normalization, augmentation, resizing specs.
        Returns: {'normalization': 'ImageNet mean/std', 'augmentation': 'RandomCrop', ...}
        """
        ...
    
    def extract_evaluation_protocol(self, methods_text: str) -> Dict[str, Optional[str]]:
        """
        Extract metrics (accuracy, F1), validation strategy (k-fold, holdout).
        Returns: {'metrics': 'accuracy', 'validation': '5-fold CV', ...}
        """
        ...
    
    def extract_hyperparameters(self, methods_text: str) -> Dict[str, Optional[str]]:
        """
        Extract optimizer, LR, batch size, epochs.
        Returns: {'optimizer': 'Adam', 'lr': '0.001', 'batch_size': '32', ...}
        """
        ...
    
    def extract_all_protocols(self, methods_text: str) -> Dict[str, Dict]:
        """
        Extract all 4 dimensions.
        Returns: {'data_splits': {...}, 'preprocessing': {...}, ...}
        """
        ...
```

### Pseudo-code

```
For data_splits:
  - Regex: r'(\d+)/(\d+)/(\d+)' or r'train.*?(\d+)%'
  - Extract numbers and map to train/val/test

For preprocessing:
  - Keyword search: "normalization", "augmentation", "resize"
  - Extract specs after keywords

For evaluation:
  - Metrics: "accuracy|F1|precision|recall"
  - Validation: "k-fold|cross-validation|holdout"

For hyperparameters:
  - Optimizer: "Adam|SGD|AdamW"
  - LR: r'learning rate.*?(\d+\.?\d*e?-?\d*)'
  - Batch size: r'batch.*?(\d+)'
  - Epochs: r'epoch.*?(\d+)'
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | 4 extraction functions | Regex patterns for each dimension |

---

## M2-5: Protocol Coding System [Complexity: 11, Budget: 1]

**Applied:** Binary comparison logic, benchmark spec loading

### API Signatures

```python
from typing import Dict
import pandas as pd


class ProtocolCoder:
    """Binary coding: Identical (1) vs Divergent (0) relative to benchmark spec."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize coder."""
        self.config = config
    
    def load_benchmark_spec(self, benchmark_id: str) -> Dict[str, Dict]:
        """
        Load ground-truth protocol from benchmark documentation.
        Returns: {'data_splits': {...}, 'preprocessing': {...}, ...}
        """
        ...
    
    def compare_protocols(
        self, 
        paper_protocol: Dict[str, Dict], 
        benchmark_spec: Dict[str, Dict]
    ) -> Dict[str, int]:
        """
        Binary comparison for each dimension.
        Returns: {'data_splits': 1, 'preprocessing': 0, ...}
        """
        ...
    
    def code_paper(
        self, 
        paper_id: str, 
        benchmark_id: str, 
        methods_text: str
    ) -> Dict[str, int]:
        """
        Code single paper against benchmark spec.
        Returns: {'data_splits': 1, 'preprocessing': 1, ...}
        """
        ...
    
    def code_all_papers(self, papers: pd.DataFrame, output_file: str) -> None:
        """
        Code all 50 papers and save to protocol_coding.csv.
        Output: [50, 6] (benchmark_id, paper_id, data_splits, preprocessing, eval, hyperparams)
        """
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Comparison logic | Binary matching for each dimension |

---

## M2-6: Inter-Rater Reliability [Complexity: 10, Budget: 1]

**Applied:** sklearn.metrics.cohen_kappa_score (same as H-M1)

### API Signatures

```python
from sklearn.metrics import cohen_kappa_score
import pandas as pd
from typing import Dict


class InterRaterValidator:
    """Validate coding reliability with 2 independent raters on 20% sample."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize validator."""
        self.config = config
    
    def sample_for_double_coding(
        self, 
        papers: pd.DataFrame, 
        sample_size: int = 10
    ) -> pd.DataFrame:
        """Random sample 10 papers. Returns: [10, ~10]"""
        ...
    
    def calculate_dimension_kappa(
        self, 
        rater1: pd.Series, 
        rater2: pd.Series
    ) -> float:
        """
        Cohen's kappa for single dimension.
        Both: [10] Returns: kappa in [-1, 1]
        """
        return cohen_kappa_score(rater1, rater2)
    
    def calculate_all_kappas(
        self, 
        rater1_df: pd.DataFrame, 
        rater2_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Kappa for each of 4 dimensions.
        Returns: {'data_splits': 0.85, 'preprocessing': 0.92, ...}
        """
        ...
    
    def check_reliability_gate(
        self, 
        kappa_results: Dict[str, float], 
        threshold: float = 0.8
    ) -> bool:
        """
        Validate kappa >= threshold for all dimensions.
        Returns: True if all kappas >= 0.8
        """
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Kappa calculation | sklearn wrapper for 4 dimensions |

---

## M2-7: Consistency Analysis [Complexity: 12, Budget: 0]

**Applied:** Pandas aggregation, stratum-level statistics

### API Signatures

```python
import pandas as pd


class ProtocolConsistencyCalculator:
    """Compute consistency rates per benchmark and stratum."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize calculator."""
        self.config = config
    
    def compute_benchmark_consistency(self, benchmark_papers: pd.DataFrame) -> float:
        """
        % of papers with >=3/4 dimensions identical.
        Input: [5, 6] (5 papers for 1 benchmark)
        Returns: consistency rate in [0, 1]
        """
        ...
    
    def compute_stratum_consistency(
        self, 
        benchmarks: pd.DataFrame, 
        quality_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Consistency rate by quality stratum.
        Returns: [3, 4] (High/Medium/Low, mean_consistency, std, n_benchmarks)
        """
        ...
    
    def save_consistency_results(
        self, 
        consistency_df: pd.DataFrame, 
        output_file: str
    ) -> None:
        """Save to CSV."""
        ...
```

---

## M2-8: Correlation Analysis [Complexity: 9, Budget: 0]

**Applied:** scipy.stats.spearmanr

### API Signatures

```python
from scipy.stats import spearmanr
import pandas as pd
from typing import Dict


class CorrelationAnalyzer:
    """Test correlation between artifact quality and protocol consistency."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize analyzer."""
        self.config = config
    
    def compute_spearman_correlation(
        self, 
        quality_scores: pd.Series, 
        consistency_rates: pd.Series
    ) -> Dict[str, float]:
        """
        Spearman rho and p-value.
        Both: [10] Returns: {'rho': 0.52, 'p_value': 0.03}
        """
        rho, p_value = spearmanr(quality_scores, consistency_rates)
        return {'rho': rho, 'p_value': p_value}
    
    def check_correlation_gate(self, rho: float, p_value: float) -> bool:
        """
        Is rho > 0.4 and p < 0.05?
        Returns: True if both conditions met
        """
        ...
```

---

## M2-9: Hypothesis Testing [Complexity: 10, Budget: 0]

**Applied:** Gate logic with OR condition

### API Signatures

```python
from typing import Dict
import json


class HypothesisTester:
    """Test primary and secondary success criteria."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize tester."""
        self.config = config
    
    def test_primary_metric(self, high_quality_consistency: float) -> Dict:
        """
        Is consistency rate > 70% for high-quality artifacts?
        Returns: {'value': 0.75, 'threshold': 0.70, 'pass': True}
        """
        ...
    
    def test_secondary_metric(self, rho: float, p_value: float) -> Dict:
        """
        Is Spearman rho > 0.4 with p < 0.05?
        Returns: {'rho': 0.52, 'p_value': 0.03, 'threshold': 0.4, 'pass': True}
        """
        ...
    
    def evaluate_gate(
        self, 
        primary_result: Dict, 
        secondary_result: Dict
    ) -> Dict:
        """
        Gate decision: PASS if primary OR secondary succeeds.
        Returns: {'primary': True, 'secondary': True, 'gate_decision': 'PASS'}
        """
        ...
    
    def save_results(self, gate_result: Dict, output_file: str) -> None:
        """Write to JSON."""
        with open(output_file, 'w') as f:
            json.dump(gate_result, f, indent=2)
```

---

## M2-10: Visualization Suite [Complexity: 13, Budget: 0]

**Applied:** Matplotlib/seaborn standard plotting

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict


class ProtocolVisualization:
    """Generate 4 required figures."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize with config."""
        self.config = config
    
    def plot_gate_metrics(
        self, 
        primary_actual: float, 
        secondary_rho: float, 
        save_path: str
    ) -> None:
        """
        MANDATORY: Bar chart comparing Target vs Actual.
        Bars: [Primary Target (0.70), Primary Actual, Secondary Target (0.4), Secondary Actual]
        """
        ...
    
    def plot_consistency_by_quality(
        self, 
        consistency_df: pd.DataFrame, 
        save_path: str
    ) -> None:
        """
        Box plot: X=stratum (High/Medium/Low), Y=consistency rate.
        Input: [3, 4]
        """
        ...
    
    def plot_quality_consistency_scatter(
        self, 
        quality_scores: pd.Series, 
        consistency_rates: pd.Series, 
        rho: float, 
        save_path: str
    ) -> None:
        """
        Scatter: X=quality_score, Y=consistency_rate.
        Add regression line and annotate with "rho = 0.52, p < 0.05".
        """
        ...
    
    def plot_dimension_heatmap(
        self, 
        protocol_coding: pd.DataFrame, 
        save_path: str
    ) -> None:
        """
        Heatmap: X=dimensions, Y=benchmarks, color=consistency rate.
        Input: [50, 6]
        """
        ...
    
    def generate_all_figures(self, results: Dict, output_dir: str) -> None:
        """Generate all 4 plots."""
        ...
```

---

## M2-11: Report Generation [Complexity: 11, Budget: 0]

**Applied:** Template-based markdown generation

### API Signatures

```python
from typing import Dict, Any


class ValidationReportGenerator:
    """Generate 04_validation.md with gate decision logic."""
    
    def __init__(self, config: ProtocolStudyConfig):
        """Initialize with config."""
        self.config = config
    
    def load_results(self, results_dir: str) -> Dict[str, Any]:
        """
        Load all metrics: kappa, consistency, correlation, gate.
        Returns: results dict
        """
        ...
    
    def determine_gate_status(self, primary_pass: bool, secondary_pass: bool) -> str:
        """
        PASS (either passes), EXPLORE (both fail).
        Returns: 'PASS' | 'EXPLORE'
        """
        ...
    
    def generate_report(self, results: Dict[str, Any], output_path: str) -> None:
        """Write 04_validation.md with full results."""
        ...
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual H-M1 Code)

The following APIs are verified from actual H-M1 implementation:

```python
# From: docs/youra_research/h-m1/code/config.py
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class QualityStudyConfig:
    """Configuration for artifact quality assessment."""
    API_BASE_URL: str = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    SAMPLE_SIZE: int = 20
    STRATIFICATION: Dict[str, int] = field(default_factory=lambda: {"CV": 10, "NLP": 10})
    RUBRIC_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "preprocessing", "data_splits", "evaluation_protocol", "hyperparameters"
    ])
    MIN_KAPPA: float = 0.8
    MIN_QUALITY: float = 7.0


# From: docs/youra_research/h-m1/code/data/collector.py
class PapersWithCodeCollector:
    """API client for Papers with Code."""
    
    def __init__(self, base_url: str, rate_limit: float = 1.0, max_retries: int = 3):
        """Initialize collector."""
        ...
    
    def collect_with_retry(
        self, 
        url: str, 
        params: Optional[Dict] = None, 
        retries: int = 3
    ) -> Dict:
        """Execute API request with exponential backoff. Returns: JSON response dict"""
        ...
    
    def fetch_benchmarks(
        self, 
        task: str, 
        start_year: int, 
        end_year: int
    ) -> pd.DataFrame:
        """
        Fetch benchmarks from API.
        Returns: [N_benchmarks, ~7] (benchmark_id, name, task, year, result_count, github_url)
        """
        ...
    
    def retrieve_artifact(
        self, 
        github_url: str, 
        output_dir: str
    ) -> Optional[str]:
        """Retrieve artifact content. Returns: file path or None"""
        ...
```

**Verified from**: docs/youra_research/h-m1/code/ (actual implementation)

**Key differences from spec:**
- Method name is `collect_with_retry`, not `fetch_with_retry`
- Config uses `field(default_factory=lambda: ...)` for mutable defaults
- API client has `_rate_limit_wait()` internal method

**Reuse strategy:**
- Import PapersWithCodeCollector for API client logic
- Extend QualityStudyConfig pattern for ProtocolStudyConfig
- Reuse RUBRIC_DIMENSIONS for protocol coding

---

## Summary

**Total Subtasks:** 11/11 used

**Design Principles:**
1. **Extend H-M1 patterns:** Reuse API client, config dataclass, kappa validation
2. **PDF parsing:** PyMuPDF for text extraction, regex for Methods section
3. **Protocol extraction:** Keyword/regex patterns for 4 dimensions
4. **Statistical rigor:** Kappa gate (0.8) before consistency analysis
5. **Gate logic:** OR condition (primary OR secondary) for PASS

**Critical Dependencies:**
- sklearn.metrics.cohen_kappa_score (inter-rater reliability)
- scipy.stats.spearmanr (correlation analysis)
- PyMuPDF (fitz) (PDF text extraction)
- pandas (data manipulation, aggregation)
- matplotlib/seaborn (visualization)

**External Dependencies (H-M1):**
- PapersWithCodeCollector: API client with retry logic
- QualityStudyConfig: Configuration pattern with field() defaults
- RUBRIC_DIMENSIONS: 4-dimension structure for protocol coding

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Code Implementation (Step 4)
