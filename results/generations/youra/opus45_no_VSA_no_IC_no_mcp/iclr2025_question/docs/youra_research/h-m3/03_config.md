# Configuration: H-M3 Orthogonal Signals Complementary Detection

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass (loaded from config.yaml)

**Applied**: Standard statistical-analysis config pattern (thresholds + I/O paths only, no training hyperparameters — pure post-hoc analysis of existing H-M1/H-M2 outputs).

---

## A-1: Orthogonality Verification [Complexity: 1, Budget: 1]

Single fixed config — MECHANISM hypothesis with deterministic statistical pipeline, no tuning/sweeps.

### config.yaml

```yaml
# H-M3 config
paths:
  h_m1_results: "../h-m1/results/entropy_scores.json"
  h_m2_results: "../h-m2/results/consistency_scores.json"
  output_dir: "results/"
  figures_dir: "results/figures/"
  correlation_output: "results/correlation_analysis.json"
  discordant_output: "results/discordant_cases.csv"
  subset_auroc_output: "results/subset_auroc.json"
  scatter_plot: "results/figures/scatter_entropy_consistency.png"
  quadrant_plot: "results/figures/quadrant_analysis.png"

thresholds:
  correlation_threshold: 0.3          # Primary: Pearson r must be below this
  discordant_rank_diff: 0.5           # Rank-diff cutoff for discordant cases
  discordant_proportion_threshold: 0.15
  subset_auroc_threshold: 0.6
  min_subset_size: 50                 # Min samples required to compute subset AUROC

seed: 42
n_questions: 817
```

### Python Dataclass

```python
from dataclasses import dataclass, field

@dataclass
class PathsConfig:
    h_m1_results: str = "../h-m1/results/entropy_scores.json"
    h_m2_results: str = "../h-m2/results/consistency_scores.json"
    output_dir: str = "results/"
    figures_dir: str = "results/figures/"
    correlation_output: str = "results/correlation_analysis.json"
    discordant_output: str = "results/discordant_cases.csv"
    subset_auroc_output: str = "results/subset_auroc.json"
    scatter_plot: str = "results/figures/scatter_entropy_consistency.png"
    quadrant_plot: str = "results/figures/quadrant_analysis.png"


@dataclass
class ThresholdsConfig:
    correlation_threshold: float = 0.3
    discordant_rank_diff: float = 0.5
    discordant_proportion_threshold: float = 0.15
    subset_auroc_threshold: float = 0.6
    min_subset_size: int = 50


@dataclass
class HM3Config:
    paths: PathsConfig = field(default_factory=PathsConfig)
    thresholds: ThresholdsConfig = field(default_factory=ThresholdsConfig)
    seed: int = 42
    n_questions: int = 817

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "HM3Config":
        import yaml
        with open(path) as f:
            raw = yaml.safe_load(f)
        return cls(
            paths=PathsConfig(**raw.get("paths", {})),
            thresholds=ThresholdsConfig(**raw.get("thresholds", {})),
            seed=raw.get("seed", 42),
            n_questions=raw.get("n_questions", 817),
        )
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Config loading | Implement `HM3Config.from_yaml()` and wire into `orthogonality.py` main() |
