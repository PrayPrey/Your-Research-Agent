# h-m3 Logic: Unanimous Agreement vs Verdict Reliability

**Applied**: Standard scipy.stats (two-proportion z-test) — no KB match for this stats pattern.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (pure statistical analysis script, no base code)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Verdict Agreement Statistical Analysis [Complexity: 3, Budget: 6]

### API Signatures

```python
import pandas as pd
from typing import TypedDict

def load_verdicts(path: str) -> pd.DataFrame:
    """Load CSV, validate required columns, dtypes."""
    ...

def classify_agreement(df: pd.DataFrame) -> pd.DataFrame:
    """Group by problem_id; add unanimous, consensus_verdict, n_agreeing."""
    ...

class AccuracyResults(TypedDict):
    unanimous_acc: float
    split_acc: float
    n_unanimous: int
    n_split: int
    improvement: float  # unanimous_acc - split_acc

def compute_accuracy(classified_df: pd.DataFrame) -> AccuracyResults:
    """Accuracy of consensus_verdict vs ground_truth, split by unanimous flag."""
    ...

class ZTestResults(TypedDict):
    z_stat: float
    p_value: float
    significant: bool  # p_value < 0.05

def run_ztest(results: AccuracyResults) -> ZTestResults:
    """Two-proportion z-test: unanimous_acc vs split_acc."""
    ...

def generate_figures(results: AccuracyResults, output_dir: str) -> None:
    """Write bar_chart.png (acc ± SE) and pie_chart.png (agreement dist) to output_dir."""
    ...

def evaluate_gate(results: AccuracyResults, ztest: ZTestResults) -> str:
    """Return 'PASS' | 'FAIL' | 'INCONCLUSIVE'."""
    ...
```

### Tensor / Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| df (raw) | 656 rows x 4 cols | problem_id, judge_model, verdict, ground_truth |
| classified_df | 656 rows x 7 cols | + unanimous, consensus_verdict, n_agreeing |
| per-problem group | 4 rows (1 problem_id, 4 judges) | groupby unit |

### Pseudo-code

**classify_agreement**:
```
1. group by problem_id
2. n_agreeing = size of majority verdict value_counts().max()
3. unanimous = (n_agreeing == 4)
4. consensus_verdict = mode of verdict (ties -> first/majority label)
5. merge back onto per-problem row (or per-judge rows, keep flag)
```

**compute_accuracy**:
```
1. unanimous_rows = classified_df[unanimous == True], dedup per problem_id
2. split_rows = classified_df[unanimous == False], dedup per problem_id
3. unanimous_acc = mean(consensus_verdict == ground_truth) over unanimous_rows
4. split_acc = mean(consensus_verdict == ground_truth) over split_rows
5. improvement = unanimous_acc - split_acc
```

**run_ztest** (two-proportion z-test, pooled):
```
1. p_pool = (n1*acc1 + n2*acc2) / (n1 + n2)
2. se = sqrt(p_pool*(1-p_pool)*(1/n1 + 1/n2))
3. z_stat = (unanimous_acc - split_acc) / se
4. p_value = 2 * (1 - norm.cdf(abs(z_stat)))   # scipy.stats.norm
5. significant = p_value < 0.05
```

**evaluate_gate**:
```
1. IF n_unanimous < 5 OR n_split < 5: return "INCONCLUSIVE"  # too few samples per group
2. IF improvement >= 0.10 AND significant: return "PASS"
3. ELSE: return "FAIL"
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A-1-1 | load_verdicts | CSV load + column/dtype validation |
| L-A-1-2 | classify_agreement | Groupby, unanimous flag, consensus verdict |
| L-A-1-3 | compute_accuracy | Split-group accuracy computation |
| L-A-1-4 | run_ztest | scipy two-proportion z-test |
| L-A-1-5 | generate_figures | matplotlib bar + pie chart |
| L-A-1-6 | evaluate_gate | PASS/FAIL/INCONCLUSIVE gate logic |
