# Logic Design: H-E1 Benchmark Data Validation

**Date:** 2026-07-12  
**Hypothesis:** h-e1 - Papers with Code benchmark database contains ≥100 classification benchmarks (2019-2024) with ≥5 independent reproduction attempts each  
**Type:** EXISTENCE (PoC Validation)  
**Phase:** 3 - Logic Design

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** New implementation from scratch (data validation study)  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - original API collection and statistical analysis implementation

**Rationale:** This is a standalone observational study with no existing codebase or base hypothesis. All components (API client, validators, statistical analyzers, visualizers) are designed from scratch based on Papers with Code REST API and scipy statistical libraries.

---

## E1-1: Data Collection Module [Complexity: 10, Budget: 10]

**Applied:** REST API client with exponential backoff retry logic

### API Signatures

```python
from typing import Optional, Dict, List
import pandas as pd
import requests
import time
from pathlib import Path


class PapersWithCodeCollector:
    def __init__(
        self,
        base_url: str = "https://paperswithcode.com/api/v1/",
        rate_limit: float = 1.0,
        output_dir: str = "data/raw"
    ):
        """Initialize API collector."""
        ...

    def fetch_benchmarks(
        self,
        task: str = "classification",
        start_year: int = 2019,
        end_year: int = 2024
    ) -> pd.DataFrame:
        """Fetch benchmarks. Returns: [benchmark_id, name, task, url]"""
        ...

    def fetch_results_count(self, benchmark_id: str) -> int:
        """Get reproduction count for benchmark."""
        ...

    def collect_with_retry(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        retries: int = 3
    ) -> Dict:
        """HTTP GET with exponential backoff."""
        ...

    def save_raw_response(self, data: Dict, filename: str) -> None:
        """Save JSON to disk for reproducibility."""
        ...
```

### Pseudo-code

```
1. fetch_benchmarks(task, start_year, end_year):
   a. url = base_url + "benchmarks/"
   b. params = {task: task, published_after: f"{start_year}-01-01"}
   c. response = collect_with_retry(url, params)
   d. benchmarks = []
   e. for item in response['results']:
      - benchmarks.append({id, name, task, url})
   f. save_raw_response(response, "benchmarks_raw.json")
   g. return pd.DataFrame(benchmarks)

2. collect_with_retry(endpoint, params, retries):
   a. for attempt in range(retries):
      - try:
          * time.sleep(rate_limit)
          * response = session.get(endpoint, params=params)
          * response.raise_for_status()
          * return response.json()
      - except RequestException:
          * backoff = 2 ** attempt
          * time.sleep(backoff)
   b. raise RuntimeError("API failed after retries")
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HTTP Client Setup | Configure requests.Session with headers |
| L-1-2 | Rate Limiter | Implement 1 req/sec throttling |
| L-1-3 | Retry Logic | Exponential backoff on HTTP errors |
| L-1-4 | Benchmark Fetcher | Parse /benchmarks/ endpoint |
| L-1-5 | Results Counter | Fetch /results/ count |
| L-1-6 | JSON Parser | Extract {id, name, task, url} |
| L-1-7 | DataFrame Builder | Convert to pandas DataFrame |
| L-1-8 | Raw Data Saver | Write JSON to data/raw/ |
| L-1-9 | Error Handler | Log HTTP errors |
| L-1-10 | Progress Logger | Log API call counts |

---

## E1-2: Validation Module [Complexity: 8, Budget: 8]

**Applied:** DataFrame filtering with boolean indexing

### API Signatures

```python
import pandas as pd
from typing import Dict, List


class BenchmarkValidator:
    def __init__(
        self,
        min_count: int = 100,
        min_results: int = 5,
        allowed_metrics: List[str] = ["accuracy", "f1"]
    ):
        """Initialize validator."""
        ...

    def filter_by_criteria(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter by result_count and metric_type. df -> filtered_df"""
        ...

    def validate_hypothesis(self, df: pd.DataFrame) -> Dict[str, any]:
        """Check gate threshold. Returns: {passes, count, threshold, message}"""
        ...

    def check_primary_gate(self, count: int) -> bool:
        """Binary gate: count >= min_count"""
        ...
```

### Pseudo-code

```
1. filter_by_criteria(df):
   a. mask_results = df['result_count'] >= min_results
   b. mask_metrics = df['metric_type'].isin(allowed_metrics)
   c. filtered = df[mask_results & mask_metrics]
   d. return filtered.reset_index(drop=True)

2. validate_hypothesis(df):
   a. count = len(df)
   b. passes = check_primary_gate(count)
   c. message = f"Found {count} benchmarks (threshold: {min_count})"
   d. return {passes, count, threshold: min_count, message}
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Result Count Filter | Boolean mask: result_count >= 5 |
| L-2-2 | Metric Type Filter | Boolean mask: metric in allowed |
| L-2-3 | Combined Filter | Apply AND operation |
| L-2-4 | DataFrame Cleaner | Drop nulls and reset index |
| L-2-5 | Count Calculator | len(filtered_df) |
| L-2-6 | Gate Checker | count >= 100 comparison |
| L-2-7 | Result Builder | Build result dict |
| L-2-8 | CSV Exporter | Save to data/processed/ |

---

## E1-3: Statistical Analysis Module [Complexity: 11, Budget: 11]

**Applied:** scipy.stats power analysis and pandas aggregation

### API Signatures

```python
import numpy as np
import pandas as pd
from scipy.stats import norm
from typing import Dict


class StatisticalAnalyzer:
    def __init__(
        self,
        effect_size: float = 0.57,
        alpha: float = 0.05,
        power: float = 0.80
    ):
        """Initialize analyzer. effect_size: Cohen's d"""
        ...

    def calculate_required_n(self) -> int:
        """Calculate sample size for two-sample t-test."""
        ...

    def check_power_sufficiency(self, actual_n: int) -> Dict[str, any]:
        """Compare actual vs required. Returns: {power_sufficient, required_n, actual_n}"""
        ...

    def analyze_domain_coverage(self, df: pd.DataFrame) -> Dict[str, any]:
        """Count per domain. df['task'] -> {domain_counts, n_domains, meets_minimum}"""
        ...

    def analyze_reproduction_depth(self, df: pd.DataFrame) -> Dict[str, any]:
        """Reproduction stats. df['result_count'] -> {median, mean, std, bins}"""
        ...
```

### Pseudo-code

```
1. calculate_required_n():
   a. z_alpha = norm.ppf(1 - alpha/2)  # Two-tailed
   b. z_beta = norm.ppf(power)
   c. n_per_group = 2 * ((z_alpha + z_beta) / effect_size) ** 2
   d. return int(np.ceil(n_per_group))

2. check_power_sufficiency(actual_n):
   a. required_n = calculate_required_n()
   b. sufficient = actual_n >= required_n
   c. return {power_sufficient: sufficient, required_n, actual_n}

3. analyze_domain_coverage(df):
   a. domain_counts = df['task'].value_counts().to_dict()
   b. n_domains = len(domain_counts)
   c. meets_minimum = n_domains >= 2
   d. return {domain_counts, n_domains, meets_minimum}

4. analyze_reproduction_depth(df):
   a. median = df['result_count'].median()
   b. mean = df['result_count'].mean()
   c. std = df['result_count'].std()
   d. bins = pd.cut(df['result_count'], bins=[5, 10, 20, 50, 100]).value_counts()
   e. return {median, mean, std, bins}
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Z-score Calculator | norm.ppf() for alpha/beta |
| L-3-2 | Sample Size Formula | N = 2 * ((z_alpha + z_beta) / d)^2 |
| L-3-3 | Power Comparator | actual_n >= required_n check |
| L-3-4 | Domain Counter | df.groupby('task').size() |
| L-3-5 | Domain Minimum Check | len(unique_domains) >= 2 |
| L-3-6 | Median Calculator | df['result_count'].median() |
| L-3-7 | Mean/Std Calculator | Descriptive statistics |
| L-3-8 | Histogram Binner | pd.cut() with bins [5,10,20,50,100] |
| L-3-9 | Result Dict Builder | Aggregate metrics |
| L-3-10 | Timeline Grouper | Group by publication_year |
| L-3-11 | Validation Logger | Save to logs/statistics.json |

---

## E1-4: Visualization Module [Complexity: 12, Budget: 12]

**Applied:** matplotlib/seaborn figure generation

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List
from pathlib import Path


class ReportGenerator:
    def __init__(
        self,
        output_dir: str = "figures",
        style: str = "seaborn-v0_8"
    ):
        """Initialize generator."""
        ...

    def generate_gate_metric_chart(
        self,
        threshold: int,
        actual: int,
        passes: bool
    ) -> str:
        """Bar chart: threshold vs actual. Returns: filepath"""
        ...

    def generate_reproduction_histogram(
        self,
        df: pd.DataFrame,
        bins: List[int] = [5, 10, 20, 50, 100]
    ) -> str:
        """Histogram of result_count. df -> filepath"""
        ...

    def generate_domain_pie_chart(self, domain_counts: Dict[str, int]) -> str:
        """Pie chart of domain distribution."""
        ...

    def generate_timeline_chart(self, df: pd.DataFrame) -> str:
        """Line chart: cumulative count over time. df['publication_year'] -> filepath"""
        ...

    def generate_power_chart(self, required_n: int, actual_n: int) -> str:
        """Bar chart: required vs actual sample size."""
        ...

    def generate_validation_report(
        self,
        results: Dict,
        figures: List[str]
    ) -> str:
        """Generate 04_validation.md with embedded figures."""
        ...
```

### Pseudo-code

```
1. generate_gate_metric_chart(threshold, actual, passes):
   a. fig, ax = plt.subplots(figsize=(8, 6))
   b. colors = ["green", "green"] if passes else ["red", "orange"]
   c. ax.bar(["Threshold", "Actual"], [threshold, actual], color=colors)
   d. ax.set_ylabel("Benchmark Count")
   e. filepath = output_dir / "gate_metric.png"
   f. fig.savefig(filepath, dpi=300, bbox_inches='tight')
   g. return str(filepath)

2. generate_reproduction_histogram(df, bins):
   a. fig, ax = plt.subplots()
   b. ax.hist(df['result_count'], bins=bins, edgecolor='black')
   c. ax.set_xlabel("Reproductions")
   d. filepath = output_dir / "reproduction_depth.png"
   e. fig.savefig(filepath, dpi=300)
   f. return str(filepath)

3. generate_validation_report(results, figures):
   a. template = MARKDOWN_TEMPLATE (Executive Summary, Metrics, Figures, Conclusion)
   b. populate with results dict values
   c. embed figures as ![Caption](path)
   d. write to 04_validation.md
   e. return filepath
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Style Setup | plt.style.use() configuration |
| L-4-2 | Gate Bar Chart | 2-bar comparison with colors |
| L-4-3 | Histogram Generator | ax.hist() with bins |
| L-4-4 | Pie Chart Generator | ax.pie() with percentages |
| L-4-5 | Timeline Plot | Cumulative line chart |
| L-4-6 | Power Bar Chart | Required vs actual bars |
| L-4-7 | Axis Labeler | Set labels and titles |
| L-4-8 | Color Palette | Conditional coloring |
| L-4-9 | Figure Saver | savefig(dpi=300) |
| L-4-10 | Markdown Template | String template with placeholders |
| L-4-11 | Figure Embedder | Insert ![](path) syntax |
| L-4-12 | Report Writer | Write to 04_validation.md |

---

## E1-5: Pipeline Integration [Complexity: 7, Budget: 7]

**Applied:** Sequential stage execution with logging

### API Signatures

```python
import logging
from typing import Dict
from pathlib import Path


def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """Configure file and console logging."""
    ...

def run_validation_pipeline(config: ValidationConfig) -> Dict:
    """Execute full pipeline. Returns: {stage_results, figures, status}"""
    ...

def save_results(results: Dict, output_path: str = "results.json") -> None:
    """Save results to JSON."""
    ...

def main() -> None:
    """Entry point."""
    ...
```

### Pseudo-code

```
1. run_validation_pipeline(config):
   a. logger = setup_logging()
   b. collector = PapersWithCodeCollector(config.API_BASE_URL)
   c. benchmarks_df = collector.fetch_benchmarks(config.TASK_FILTER, config.START_YEAR, config.END_YEAR)
   d. for idx, row in benchmarks_df.iterrows():
      - result_count = collector.fetch_results_count(row['benchmark_id'])
      - benchmarks_df.at[idx, 'result_count'] = result_count
   
   e. validator = BenchmarkValidator(config.MIN_BENCHMARKS)
   f. filtered_df = validator.filter_by_criteria(benchmarks_df)
   g. validation_result = validator.validate_hypothesis(filtered_df)
   
   h. analyzer = StatisticalAnalyzer(config.EFFECT_SIZE)
   i. power_result = analyzer.check_power_sufficiency(len(filtered_df))
   j. domain_result = analyzer.analyze_domain_coverage(filtered_df)
   k. repro_result = analyzer.analyze_reproduction_depth(filtered_df)
   
   l. generator = ReportGenerator()
   m. figures = [
      generator.generate_gate_metric_chart(...),
      generator.generate_reproduction_histogram(filtered_df),
      generator.generate_domain_pie_chart(domain_result['domain_counts']),
      generator.generate_timeline_chart(filtered_df),
      generator.generate_power_chart(...)
   ]
   
   n. report_path = generator.generate_validation_report({...}, figures)
   o. return {stage_results, figures, status: "PASS" if validation_result['passes'] else "FAIL"}
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Logger Setup | Configure logging handlers |
| L-5-2 | Module Imports | Import all 4 core modules |
| L-5-3 | Stage 1 Orchestration | Data collection loop |
| L-5-4 | Stage 2 Orchestration | Validation and gate check |
| L-5-5 | Stage 3 Orchestration | Statistical analysis |
| L-5-6 | Stage 4 Orchestration | Figure generation |
| L-5-7 | Stage 5 Orchestration | Report generation |

---

## E1-6: Report Generation [Complexity: 6, Budget: 6]

**Applied:** Markdown templating with embedded figures

### API Signatures

```python
from typing import Dict, List
from pathlib import Path


class ValidationReportWriter:
    def __init__(self, output_path: str = "04_validation.md"):
        """Initialize writer."""
        ...

    def build_executive_summary(self, results: Dict) -> str:
        """Generate summary section."""
        ...

    def build_metrics_section(self, results: Dict) -> str:
        """Generate metrics section."""
        ...

    def build_figures_section(self, figures: List[str]) -> str:
        """Embed figures with captions."""
        ...

    def build_conclusion_section(self, results: Dict) -> str:
        """Generate conclusion with gate decision."""
        ...

    def write_report(self, results: Dict, figures: List[str]) -> str:
        """Assemble and write report."""
        ...
```

### Pseudo-code

```
1. build_executive_summary(results):
   a. status = "PASS" if results['validation']['passes'] else "FAIL"
   b. markdown = f"Status: {status}, Count: {results['validation']['count']}"
   c. return markdown

2. build_figures_section(figures):
   a. captions = ["Gate Metric", "Reproduction Depth", "Domain Coverage", "Timeline", "Power Analysis"]
   b. for figure, caption in zip(figures, captions):
      - markdown += f"![{caption}]({figure})"
   c. return markdown

3. write_report(results, figures):
   a. sections = [build_executive_summary(), build_metrics_section(), build_figures_section(), build_conclusion_section()]
   b. full_report = "\n\n".join(sections)
   c. with open(output_path, 'w') as f: f.write(full_report)
   d. return output_path
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Executive Summary Builder | Format status and key metrics |
| L-6-2 | Data Collection Builder | Format API query details |
| L-6-3 | Metrics Builder | Format primary/secondary metrics |
| L-6-4 | Figures Embedder | Loop and insert ![](path) |
| L-6-5 | Conclusion Builder | Conditional PASS/FAIL content |
| L-6-6 | Report Assembler | Concatenate and write |

---

## Configuration Module

### API Signatures

```python
from dataclasses import dataclass


@dataclass
class ValidationConfig:
    """Configuration constants."""
    
    API_BASE_URL: str = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT: float = 1.0
    TASK_FILTER: str = "classification"
    START_YEAR: int = 2019
    END_YEAR: int = 2024
    MIN_BENCHMARKS: int = 100
    MIN_RESULTS_PER_BENCHMARK: int = 5
    ALLOWED_METRICS: list = None
    EFFECT_SIZE: float = 0.57
    ALPHA: float = 0.05
    POWER: float = 0.80
    OUTPUT_DIR: str = "."
    
    def __post_init__(self):
        if self.ALLOWED_METRICS is None:
            self.ALLOWED_METRICS = ["accuracy", "f1"]
```

---

## Summary

### Budget Allocation

| Epic | Complexity | Subtasks |
|------|------------|----------|
| E1-1 | 10 | 10 |
| E1-2 | 8 | 8 |
| E1-3 | 11 | 11 |
| E1-4 | 12 | 12 |
| E1-5 | 7 | 7 |
| E1-6 | 6 | 6 |
| **Total** | **54** | **54** |

### Key Patterns

1. REST API client with exponential backoff
2. scipy.stats power analysis (N = 2 * ((z_alpha + z_beta) / d)^2)
3. DataFrame filtering with boolean indexing
4. matplotlib/seaborn figure generation
5. Sequential pipeline orchestration
6. Markdown templating

---

**Next Phase:** Phase 4 - Implementation
