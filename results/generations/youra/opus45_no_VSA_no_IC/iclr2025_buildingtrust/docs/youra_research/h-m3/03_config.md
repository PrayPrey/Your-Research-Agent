# Config: H-M3

**Tier:** LIGHT — single fixed config, no grid/variations (correlation + PCA analysis)
**Applied:** No close KB match for stats/PCA config pattern; used standard dataclass defaults.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no `h-m3/code/` or base hypothesis to analyze)
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field


@dataclass
class PathsConfig:
    base_scores_csv: str = "h-m2/model_scores.csv"
    factscore_csv: str = "h-m3/factscore_results.csv"
    merged_scores_csv: str = "h-m3/model_scores.csv"
    correlation_results_json: str = "h-m3/correlation_results.json"
    pca_results_json: str = "h-m3/pca_results.json"
    validation_report_md: str = "h-m3/04_validation.md"
    figures_dir: str = "h-m3/figures/"


@dataclass
class ColumnsConfig:
    factscore_col: str = "factscore"
    truthfulqa_col: str = "truthfulqa_mc2"
    halueval_col: str = "halueval_agg"
    model_id_col: str = "model_id"

    @property
    def benchmark_cols(self) -> list[str]:
        return [self.factscore_col, self.truthfulqa_col, self.halueval_col]


@dataclass
class CorrelationConfig:
    threshold: float = 0.7       # gate: r(FS,TQA) and r(FS,HE) must be < this
    bootstrap_n: int = 1000
    ci: float = 0.95
    seed: int = 42
    min_n: int = 3                # below this, return degenerate (0.0, 1.0)
    min_models_warn: int = 10     # warn in report if merged N < this


@dataclass
class PCAConfig:
    n_components: int = 3         # capped at min(3, len(benchmark_cols)) at runtime
    variance_target: float = 0.80
    min_components_for_pass: int = 2  # secondary gate condition


@dataclass
class ExperimentConfig:
    paths: PathsConfig = field(default_factory=PathsConfig)
    columns: ColumnsConfig = field(default_factory=ColumnsConfig)
    correlation: CorrelationConfig = field(default_factory=CorrelationConfig)
    pca: PCAConfig = field(default_factory=PCAConfig)
```

## Subtasks

None (0 subtask budget, LIGHT tier — config used directly by Phase 4 modules).
