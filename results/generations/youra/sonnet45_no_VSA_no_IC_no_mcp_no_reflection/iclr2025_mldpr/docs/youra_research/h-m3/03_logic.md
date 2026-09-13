# Logic Design: h-m3 Citation Velocity Correlation Detector

**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Date:** 2026-08-28
**Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-m1 and h-m2 actual code
**Analyzed Path:** docs/youra_research/h-m1/code/, docs/youra_research/h-m2/code/
**Relevant Symbols:**
- h-m1: ConvergenceDetector, PWCDataLoader
- h-m2: CitationFetcher, LeadTimeAnalyzer

---

## Applied Patterns

Applied: **PyTorch-style forward pass** (from Archon KB)
Applied: **Time series rolling window** (from Archon KB)

---

## External Dependencies API (Base Hypotheses)

The following APIs are called from base hypotheses. Signatures verified from actual implementations.

```python
# From: h-m1/code/convergence_detector.py (ACTUAL CODE)
class ConvergenceDetector:
    def __init__(self, window_months: int = 6, threshold: float = 0.005, top_k: int = 5):
        """Initialize convergence detector."""
        ...

    def compute_rolling_std(self, df: pd.DataFrame, benchmark: str) -> pd.Series:
        """Compute rolling standard deviation. Returns: pd.Series[month -> std]"""
        ...

    def detect_first_convergence(
        self, rolling_std: pd.Series
    ) -> Tuple[Optional[str], Optional[float]]:
        """Detect first convergence point. Returns: (month_str or None, std_value or None)"""
        ...


# From: h-m1/code/data_loader.py (ACTUAL CODE)
class PWCDataLoader:
    def __init__(self, data_dir: Path):
        """Initialize data loader."""
        ...

    def load_benchmark(self, benchmark: str) -> pd.DataFrame:
        """Load benchmark data. Returns: DataFrame[submission_date, score, benchmark, model_name]"""
        ...

    def prepare_monthly_aggregation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add 'month' column. Returns: DataFrame with month column added"""
        ...


# From: h-m2/code/citation_fetcher.py (ACTUAL CODE)
class CitationFetcher:
    def __init__(self, cache_dir: Path = CACHE_DIR, rate_limit: tuple = RATE_LIMIT):
        """Initialize citation fetcher."""
        ...

    def fetch_citations(
        self, paper_id: str, force_refresh: bool = False
    ) -> pd.DataFrame:
        """Fetch monthly citation counts. Returns: DataFrame[date: str (YYYY-MM), citations: int]"""
        ...


# From: h-m2/code/lead_time_analyzer.py (ACTUAL CODE)
class LeadTimeAnalyzer:
    def __init__(self):
        """Initialize lead time analyzer."""
        ...

    def load_saturation_dates(
        self, h1_results_path: Path = H1_RESULTS_PATH
    ) -> Dict[str, str]:
        """Load saturation dates from h-m1. Returns: Dict[benchmark -> date_str (YYYY-MM)]"""
        ...

    def compute_lead_times(
        self,
        saturation_dates: Dict[str, str],
        adoption_dates: Dict[str, str],
        pairs: List[tuple] = BENCHMARK_SHIFT_PAIRS
    ) -> List[dict]:
        """Compute lead times. Returns: List[{benchmark, shift, lead_time_months, precedes}]"""
        ...
```

**Verified from:** h-m1/code/ and h-m2/code/ (actual implementation, NOT spec)

---

## M3-2: Velocity Computation [Complexity: 7, Budget: 1]

**Applied:** Time series rolling window

### API Signatures

```python
class VelocityDetector:
    def __init__(self, velocity_window: int = 3, spike_threshold: float = 2.0):
        """Initialize velocity detector."""
        self.velocity_window = velocity_window
        self.spike_threshold = spike_threshold

    def compute_velocity(self, citation_df: pd.DataFrame) -> pd.Series:
        """
        Compute monthly citation velocity with rolling window smoothing.
        
        Args:
            citation_df: DataFrame[date: str, citations: int]
        
        Returns:
            pd.Series[date -> velocity: float]
        """
        # citation_df: [T, 2] -> velocity_series: [T]
        ...

    def detect_spike(
        self, 
        velocity_series: pd.Series, 
        window_start: str, 
        window_end: str
    ) -> bool:
        """
        Detect velocity spike in time window (>2σ above mean).
        
        Args:
            velocity_series: pd.Series[date -> velocity]
            window_start: Start date (YYYY-MM)
            window_end: End date (YYYY-MM)
        
        Returns:
            True if spike detected, False otherwise
        """
        # velocity_series[window_start:window_end] -> scalar bool
        ...
```

### Pseudo-code

```
1. Sort citation_df by date
2. velocity = citations.rolling(window=3).apply(lambda x: (x[-1] - x[0]) / 3)
3. For spike detection:
   - Extract window: velocity[window_start:window_end]
   - Compute: mean, std = window.mean(), window.std()
   - Return: max(window) > mean + 2*std
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Rolling velocity | 3-month window differentiation with pandas |

---

## M3-5: Proposed Model - Saturation + Velocity [Complexity: 8, Budget: 2]

**Applied:** PyTorch-style forward pass

### API Signatures

```python
class CorrelationDetector:
    def __init__(
        self,
        saturation_dates: Dict[str, str],
        velocity_detector: VelocityDetector,
        search_window_pre: int = 3,
        search_window_post: int = 6
    ):
        """
        Initialize correlation detector.
        
        Args:
            saturation_dates: Dict[benchmark -> saturation_date (YYYY-MM)]
            velocity_detector: VelocityDetector instance
            search_window_pre: Months before saturation to search
            search_window_post: Months after saturation to search
        """
        self.saturation_dates = saturation_dates
        self.velocity_detector = velocity_detector
        self.search_window_pre = search_window_pre
        self.search_window_post = search_window_post

    def detect_shift(
        self, benchmark: str, citation_df: pd.DataFrame
    ) -> int:
        """
        Predict paradigm shift using saturation + velocity correlation.
        
        Args:
            benchmark: Benchmark name
            citation_df: DataFrame[date: str, citations: int]
        
        Returns:
            1 if shift predicted (saturation AND velocity spike), 0 otherwise
        """
        # citation_df: [T, 2] -> scalar int {0, 1}
        ...

    def detect_all(
        self, benchmarks: List[str], citation_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, int]:
        """
        Run detection on multiple benchmarks.
        
        Args:
            benchmarks: List of benchmark names
            citation_data: Dict[benchmark -> citation_df]
        
        Returns:
            Dict[benchmark -> prediction {0, 1}]
        """
        # benchmarks: [N] -> Dict[N -> {0, 1}]
        ...
```

### Pseudo-code

```
detect_shift(benchmark, citation_df):
  1. Check saturation: if benchmark not in saturation_dates, return 0
  2. Compute velocity: velocity_series = velocity_detector.compute_velocity(citation_df)
  3. Define search window: 
     - window_start = saturation_date - search_window_pre months
     - window_end = saturation_date + search_window_post months
  4. Detect spike: has_spike = velocity_detector.detect_spike(velocity_series, window_start, window_end)
  5. Return: 1 if has_spike else 0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Temporal alignment | Window extraction around saturation date |
| L-5-2 | AND logic | Combine saturation + velocity binary flags |

---

## M3-7: Metrics Computation [Complexity: 6, Budget: 1]

**Applied:** sklearn.metrics pattern

### API Signatures

```python
class PrecisionRecallEvaluator:
    def compute_metrics(self, y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
        """
        Compute binary classification metrics.
        
        Args:
            y_true: Ground truth labels [0 or 1]
            y_pred: Predicted labels [0 or 1]
        
        Returns:
            Dict with keys: precision, recall, f1, tp, fp, tn, fn
        """
        # y_true: [N], y_pred: [N] -> metrics_dict: 7 keys
        ...

    def generate_classification_report(
        self, y_true: List[int], y_pred: List[int]
    ) -> str:
        """
        Generate sklearn classification report.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
        
        Returns:
            Classification report string
        """
        ...
```

### Pseudo-code

```
1. precision = sklearn.metrics.precision_score(y_true, y_pred, zero_division=0)
2. recall = sklearn.metrics.recall_score(y_true, y_pred, zero_division=0)
3. f1 = sklearn.metrics.f1_score(y_true, y_pred, zero_division=0)
4. cm = sklearn.metrics.confusion_matrix(y_true, y_pred)
5. Extract tp, fp, tn, fn from cm
6. Return dict with all metrics
```

### Subtasks [0/1 used]

No additional subtasks needed (sklearn stdlib).

---

## Supporting Modules (Standard Implementation)

### GroundTruthLoader

```python
class GroundTruthLoader:
    def load_paradigm_shifts(self, path: Path) -> Dict[str, str]:
        """Load paradigm shift dates from JSON."""
        # JSON read -> Dict[benchmark -> date_str]
        ...

    def create_labels(
        self,
        saturation_dates: Dict[str, str],
        shift_dates: Dict[str, str],
        threshold_months: int = 6
    ) -> Dict[str, int]:
        """
        Create binary labels (shift within threshold of saturation).
        
        Returns:
            Dict[benchmark -> label {0, 1}]
        """
        # Compute: label = 1 if 0 < (shift_date - saturation_date) < threshold_months else 0
        ...
```

### MetricsVisualizer

```python
class MetricsVisualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    def plot_gate_metrics(
        self,
        precision: float,
        recall: float,
        target_precision: float = 0.8,
        target_recall: float = 0.7
    ) -> None:
        """Bar chart comparing target vs actual metrics. Saves to output_dir/gate_metrics.png"""
        ...

    def plot_citation_velocity_timeline(
        self,
        benchmark: str,
        citations_df: pd.DataFrame,
        saturation_date: str,
        shift_date: str
    ) -> None:
        """Line plot with velocity + event markers. Saves to output_dir/timeline_{benchmark}.png"""
        ...

    def plot_confusion_matrix(self, y_true: List[int], y_pred: List[int]) -> None:
        """2x2 heatmap with seaborn. Saves to output_dir/confusion_matrix.png"""
        ...
```

---

## Main Pipeline

```python
def run_correlation_experiment(
    h1_results_path: Path,
    h2_citation_cache: Path,
    ground_truth_path: Path,
    output_dir: Path
) -> Dict[str, Any]:
    """
    Run full h-m3 correlation experiment.
    
    Returns:
        Dict with keys: predictions, metrics, gate_pass
    """
    # 1. Load saturation dates from h-m1
    analyzer = LeadTimeAnalyzer()
    saturation_dates = analyzer.load_saturation_dates(h1_results_path)
    
    # 2. Load ground truth paradigm shifts
    gt_loader = GroundTruthLoader()
    shift_dates = gt_loader.load_paradigm_shifts(ground_truth_path)
    
    # 3. Create binary labels
    y_true_dict = gt_loader.create_labels(saturation_dates, shift_dates)
    
    # 4. Initialize detectors
    velocity_detector = VelocityDetector(velocity_window=3, spike_threshold=2.0)
    correlation_detector = CorrelationDetector(saturation_dates, velocity_detector)
    
    # 5. Load citation data
    citation_fetcher = CitationFetcher(cache_dir=h2_citation_cache)
    citation_data = {}
    for benchmark in saturation_dates.keys():
        # Fetch from cache or API
        citation_data[benchmark] = citation_fetcher.fetch_citations(benchmark)
    
    # 6. Run detection
    y_pred_dict = correlation_detector.detect_all(list(saturation_dates.keys()), citation_data)
    
    # 7. Compute metrics
    evaluator = PrecisionRecallEvaluator()
    y_true = [y_true_dict[b] for b in saturation_dates.keys()]
    y_pred = [y_pred_dict[b] for b in saturation_dates.keys()]
    metrics = evaluator.compute_metrics(y_true, y_pred)
    
    # 8. Gate evaluation
    gate_pass = metrics['precision'] > 0.8 and metrics['recall'] > 0.7
    
    # 9. Visualization
    visualizer = MetricsVisualizer(output_dir / 'figures')
    visualizer.plot_gate_metrics(metrics['precision'], metrics['recall'])
    visualizer.plot_confusion_matrix(y_true, y_pred)
    
    # 10. Save results
    return {'predictions': y_pred_dict, 'metrics': metrics, 'gate_pass': gate_pass}
```

---

## Budget Summary

| Task | Complexity | Budget Allocated | Subtasks Used |
|------|------------|------------------|---------------|
| M3-2 | 7 | 1 | 1 |
| M3-5 | 8 | 2 | 2 |
| M3-7 | 6 | 1 | 0 |
| **Total** | **21** | **4** | **3/4** |

**Status:** Within budget (3/4 subtasks used)
