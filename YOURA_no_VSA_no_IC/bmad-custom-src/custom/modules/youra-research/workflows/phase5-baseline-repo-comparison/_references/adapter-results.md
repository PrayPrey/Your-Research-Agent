# Adapter: Results Saver

> **Reference Guide for Phase 5 Step 7 - Task 5**
> Template for saving experiment results in YouRA comparison format

---

## Purpose

Save experiment results in YouRA comparison format (CSV).

**File:** `{adaptations_folder}/results_saver.py`

---

## Full Template

```python
"""Results Saver for YouRA Baseline Comparison.

Saves results in a standardized CSV format for comparison analysis.
"""

import os
import pandas as pd
from datetime import datetime

class ResultsSaver:
    """Save experiment results in YouRA comparison format.

    Outputs CSV with columns:
    - method: "ours" or baseline repo name
    - dataset: "primary" or "secondary"
    - lr: learning rate
    - seed: random seed
    - primary_metric: main metric (e.g., psi, accuracy)
    - secondary_metric: secondary metric (e.g., loss)
    - epochs_completed: number of epochs
    - timestamp: when the run completed

    Attributes:
        output_path: Path to save results CSV
        method_name: Name of the method (baseline repo name)
        results: List of result dictionaries
    """

    def __init__(self, output_path, method_name="baseline"):
        """Initialize results saver.

        Args:
            output_path: Path to save CSV file
            method_name: Name for this method (e.g., "baseline_1")
        """
        self.output_path = output_path
        self.method_name = method_name
        self.results = []

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def add_run(self, lr, seed, primary_metric, secondary_metric=None,
                epochs_completed=None, dataset="primary", **extra):
        """Add a single experiment run result.

        Args:
            lr: Learning rate used
            seed: Random seed used
            primary_metric: Main metric value (e.g., psi, accuracy)
            secondary_metric: Secondary metric value (e.g., loss)
            epochs_completed: Number of epochs completed
            dataset: Dataset name ("primary" or "secondary")
            **extra: Additional metrics to record
        """
        result = {
            'method': self.method_name,
            'dataset': dataset,
            'lr': lr,
            'seed': seed,
            'primary_metric': primary_metric,
            'secondary_metric': secondary_metric,
            'epochs_completed': epochs_completed,
            'timestamp': datetime.now().isoformat(),
            **extra
        }
        self.results.append(result)

    def add_from_tracker(self, tracker, lr, seed, dataset="primary"):
        """Add results from a MetricTracker.

        Args:
            tracker: MetricTracker instance with recorded metrics
            lr: Learning rate used
            seed: Random seed used
            dataset: Dataset name
        """
        summary = tracker.summary()
        self.add_run(
            lr=lr,
            seed=seed,
            primary_metric=summary.get('final_psi'),
            secondary_metric=summary.get('final_loss'),
            epochs_completed=summary.get('total_records'),
            dataset=dataset
        )

    def save(self):
        """Save all results to CSV file.

        Creates or appends to the output CSV file.
        """
        df = pd.DataFrame(self.results)

        # If file exists, append; otherwise create new
        if os.path.exists(self.output_path):
            existing_df = pd.read_csv(self.output_path)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_csv(self.output_path, index=False)
        print(f"Results saved to {self.output_path}")
        return self.output_path

    def get_dataframe(self):
        """Get results as pandas DataFrame."""
        return pd.DataFrame(self.results)

def create_comparison_csv(results_list, output_path):
    """Combine multiple result files into comparison CSV.

    Args:
        results_list: List of result CSV paths
        output_path: Path for combined comparison CSV

    Returns:
        Path to combined CSV
    """
    dfs = []
    for path in results_list:
        if os.path.exists(path):
            dfs.append(pd.read_csv(path))

    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        combined.to_csv(output_path, index=False)
        return output_path

    return None
```

---

## Related Files

| File | Purpose |
|------|---------|
| `step-07-adaptation-coding.md` | Orchestration step |
| `adapter-metrics.md` | MetricTracker used by add_from_tracker |
| `result-collection-guide.md` | How results are collected in Step 9 |
