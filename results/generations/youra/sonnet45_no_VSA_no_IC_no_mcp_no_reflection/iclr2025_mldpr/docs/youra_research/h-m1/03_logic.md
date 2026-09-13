# Logic Design Document: h-m1 Score Convergence Detection

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Date:** 2026-08-28  
**Subtask Budget:** 4 tasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-e1 actual code  
**Analyzed Path:** docs/youra_research/h-e1/src/  
**Relevant Symbols:** DataValidator, PWCLeaderboardScraper, Submission

---

## Applied Patterns

Applied: **Statistical Analysis Pipeline** (rolling window time-series detection)

---

## API Signatures

### data_loader.py

```python
from pathlib import Path
import pandas as pd
from typing import Dict

class PWCDataLoader:
    def __init__(self, data_dir: Path):
        """Load h-e1 validated JSONL data."""
        self.data_dir = Path(data_dir)
    
    def load_benchmark(self, benchmark: str) -> pd.DataFrame:
        """
        Load JSONL to DataFrame. Returns: [submission_date, score, benchmark, model_name]
        """
        pass
    
    def prepare_monthly_aggregation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add month column. Returns: df with 'month' as Period[M]
        """
        pass
```

### convergence_detector.py

```python
import pandas as pd
from typing import Tuple, Optional

class ConvergenceDetector:
    def __init__(self, window_months: int = 6, threshold: float = 0.005, top_k: int = 5):
        self.window_months = window_months
        self.threshold = threshold
        self.top_k = top_k
    
    def compute_rolling_std(self, df: pd.DataFrame, benchmark: str) -> pd.Series:
        """
        Compute 6-month rolling std of top-5 scores.
        df: [month, score] -> Series[month] -> float
        """
        pass
    
    def detect_first_convergence(self, rolling_std: pd.Series) -> Tuple[Optional[str], Optional[float]]:
        """
        Find first month where std < threshold.
        Returns: (convergence_date: str, final_std: float) or (None, None)
        """
        pass
```

### statistical_validator.py

```python
from scipy import stats
import pandas as pd
from typing import Dict

class StatisticalValidator:
    def levene_test(self, pre_scores: pd.Series, post_scores: pd.Series) -> Dict[str, float]:
        """
        Levene's test for variance homogeneity.
        Returns: {'stat': float, 'pvalue': float}
        """
        pass
    
    def validate_convergence(self, df: pd.DataFrame, convergence_date: str, benchmark: str) -> Dict:
        """
        Split pre/post convergence, run Levene test.
        Returns: {'pre_count': int, 'post_count': int, 'stat': float, 'pvalue': float, 'significant': bool}
        """
        pass
```

### visualizer.py

```python
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

class ConvergenceVisualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_timeline(
        self,
        benchmark: str,
        dates: pd.Series,
        std_values: pd.Series,
        threshold: float,
        convergence_date: Optional[str] = None
    ) -> None:
        """
        Line plot: rolling std over time, threshold line, convergence marker.
        Save to figures/convergence_timeline_{benchmark}.png
        """
        pass
    
    def plot_gate_metrics(self, target_benchmarks: int, actual_benchmarks: int) -> None:
        """
        Bar chart: target vs actual convergence count.
        Save to figures/gate_metrics.png
        """
        pass
```

### main_experiment.py

```python
from pathlib import Path
import json
from data_loader import PWCDataLoader
from convergence_detector import ConvergenceDetector
from statistical_validator import StatisticalValidator
from visualizer import ConvergenceVisualizer

def run_convergence_experiment(data_dir: Path, output_dir: Path) -> dict:
    """
    Pipeline: load data -> detect convergence -> validate -> visualize -> report.
    Returns: {'results': {benchmark: {...}}, 'gate_pass': bool}
    """
    pass

if __name__ == "__main__":
    results = run_convergence_experiment(
        data_dir=Path("../data"),
        output_dir=Path("../results")
    )
    print(json.dumps(results, indent=2))
```

---

## Pseudo-code

### Convergence Detection Algorithm

```
1. Load JSONL data from h-e1/data/pwc_leaderboards/{benchmark}_raw.jsonl
2. For each benchmark:
   a. df['month'] = pd.to_datetime(df['submission_date']).dt.to_period('M')
   b. monthly_top5 = df.groupby('month')['score'].nlargest(top_k)
   c. monthly_std = monthly_top5.groupby(level=0).std()
   d. rolling_std = monthly_std.rolling(window=6, min_periods=3).mean()
   e. mask = rolling_std < threshold
   f. first_idx = mask.idxmax() if mask.any() else None
   g. convergence_date = str(first_idx) if first_idx else None
3. Statistical validation:
   a. pre = df[df['month'] < convergence_date]
   b. post = df[df['month'] >= convergence_date]
   c. stat, pvalue = scipy.stats.levene(pre['score'], post['score'])
4. Gate check: count benchmarks where (convergence_date is not None and pvalue < 0.05)
5. Pass if count >= 2
```

---

## Subtasks [4/4 used]

| ID | Subtask | Description | Complexity |
|----|---------|-------------|------------|
| M1-1 | Data Loading | JSONL to DataFrame, monthly aggregation | 4 |
| M1-2 | Rolling Window | Top-5 extraction, 6-month rolling std | 9 |
| M1-3 | Convergence Detection | First convergence date per benchmark | 6 |
| M1-4 | Statistical Validation | Levene's test, visualization, orchestration | 11 |

**Total Complexity:** 30  
**Budget Compliance:** PASS (allocated: 4, actual: 4)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1/src/data_validator.py
class DataValidator:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
    
    def validate_pwc_data(self) -> Dict[str, Any]:
        """Validate PWC leaderboard data completeness."""
        pass
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        pass

# From: docs/youra_research/h-e1/src/pwc_scraper.py
class Submission(BaseModel):
    benchmark: str
    model_name: str
    score: float
    submission_date: str
    paper_title: str = ""
    paper_url: str = ""
```

**Data Schema (h-e1 JSONL format):**
```json
{"benchmark": "imagenet", "model_name": "ResNet-152", "score": 78.3, "submission_date": "2020-01-15", "paper_title": "...", "paper_url": "..."}
```

**Verified from:** docs/youra_research/h-e1/src/ (actual implementation)

---

## Data Flows

```
h-e1/data/pwc_leaderboards/{benchmark}_raw.jsonl
    ↓
PWCDataLoader.load_benchmark() → pd.DataFrame
    ↓
ConvergenceDetector.compute_rolling_std() → pd.Series (rolling std)
    ↓
ConvergenceDetector.detect_first_convergence() → (convergence_date, std)
    ↓
StatisticalValidator.validate_convergence() → {'pvalue': float, 'significant': bool}
    ↓
ConvergenceVisualizer.plot_timeline() → figures/{benchmark}.png
    ↓
run_convergence_experiment() → results/convergence_results.json
```

---

## Next Steps

**Phase 4 Implementation Order:**
1. M1-1: Data loading (prerequisite)
2. M1-2: Rolling window statistics (core mechanism)
3. M1-3: Convergence detection
4. M1-4: Validation + visualization + orchestration

**Document Status:** READY FOR PHASE 4
