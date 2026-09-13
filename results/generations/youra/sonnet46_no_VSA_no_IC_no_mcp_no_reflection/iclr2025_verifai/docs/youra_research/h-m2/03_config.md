# H-M2 Configuration

Applied: experiment-config-dataclass pattern
**Applied**: experiment-config-dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Green-field config — no existing config files in H-M2 code directory
**Config Files Found**: None — new config design
**Pattern Used**: dataclass

---

## A-7: measure_all + parallel runner [Complexity: M, Budget: 1]

**Applied**: Standard subprocess parallelism defaults

### C-7-1: Worker / Timeout / Parallelism Settings

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VerifierConfig:
    timeout_secs: int = 10
    workers: int = 4
    pyright_cmd: list[str] = field(default_factory=lambda: ["pyright", "--outputjson"])
    mypy_cmd: list[str] = field(default_factory=lambda: ["mypy", "--no-error-summary"])


@dataclass
class Z3ExtractorConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 512
    expected_coverage: float = 0.4  # ~40% of problems have extractable Z3 constraints


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "H-M2"
    h_m1_results_path: str = "results/h-m1/results.jsonl"
    output_dir: str = "results/h-m2/"
    figures_dir: str = "figures/"
    seed: int = 42
    verifier: VerifierConfig = field(default_factory=VerifierConfig)
    z3: Z3ExtractorConfig = field(default_factory=Z3ExtractorConfig)

    def validate(self) -> None:
        assert Path(self.h_m1_results_path).exists(), f"H-M1 results not found: {self.h_m1_results_path}"
        assert self.verifier.workers >= 1, "workers must be >= 1"
        assert self.verifier.timeout_secs > 0, "timeout_secs must be > 0"
        assert 0.0 <= self.z3.expected_coverage <= 1.0, "expected_coverage must be in [0, 1]"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | ParallelRunnerConfig | Worker count, per-verifier timeout, subprocess command defaults |

---

## A-9: Visualization [Complexity: M, Budget: 1]

**Applied**: Standard matplotlib figure defaults

### C-9-1: Figure Output Settings

```python
@dataclass
class VisualizationConfig:
    dpi: int = 150
    format: str = "png"
    figsize: tuple[int, int] = (10, 6)
    verifier_colors: dict[str, str] = field(default_factory=lambda: {
        "execution": "steelblue",
        "pyright": "coral",
        "mypy": "mediumseagreen",
        "z3": "mediumpurple",
    })

    def validate(self) -> None:
        assert self.dpi > 0, "dpi must be > 0"
        assert self.format in ("png", "pdf", "svg"), f"unsupported format: {self.format}"
        assert set(self.verifier_colors) == {"execution", "pyright", "mypy", "z3"}, \
            "verifier_colors must have exactly 4 keys: execution, pyright, mypy, z3"


@dataclass
class StatisticsConfig:
    alpha: float = 0.05
    effect_size_threshold: float = 0.06   # epsilon-squared moderate
    pairwise_diff_threshold: float = 0.20  # 20% min for adjacent categories
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | VisualizationConfig | DPI, format, figsize, per-verifier color palette |

---

## Full Assembled Config (copy-paste ready)

```python
# config.py — single source of truth for H-M2
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VerifierConfig:
    timeout_secs: int = 10
    workers: int = 4
    pyright_cmd: list[str] = field(default_factory=lambda: ["pyright", "--outputjson"])
    mypy_cmd: list[str] = field(default_factory=lambda: ["mypy", "--no-error-summary"])


@dataclass
class Z3ExtractorConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 512
    expected_coverage: float = 0.4


@dataclass
class StatisticsConfig:
    alpha: float = 0.05
    effect_size_threshold: float = 0.06
    pairwise_diff_threshold: float = 0.20


@dataclass
class VisualizationConfig:
    dpi: int = 150
    format: str = "png"
    figsize: tuple[int, int] = (10, 6)
    verifier_colors: dict[str, str] = field(default_factory=lambda: {
        "execution": "steelblue",
        "pyright": "coral",
        "mypy": "mediumseagreen",
        "z3": "mediumpurple",
    })

    def validate(self) -> None:
        assert self.dpi > 0
        assert self.format in ("png", "pdf", "svg")
        assert set(self.verifier_colors) == {"execution", "pyright", "mypy", "z3"}


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "H-M2"
    h_m1_results_path: str = "results/h-m1/results.jsonl"
    output_dir: str = "results/h-m2/"
    figures_dir: str = "figures/"
    seed: int = 42
    verifier: VerifierConfig = field(default_factory=VerifierConfig)
    z3: Z3ExtractorConfig = field(default_factory=Z3ExtractorConfig)
    statistics: StatisticsConfig = field(default_factory=StatisticsConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    def validate(self) -> None:
        assert Path(self.h_m1_results_path).exists(), \
            f"H-M1 results not found: {self.h_m1_results_path}"
        assert self.verifier.workers >= 1
        assert self.verifier.timeout_secs > 0
        assert 0.0 <= self.z3.expected_coverage <= 1.0
        self.visualization.validate()


# Default singleton
DEFAULT_CONFIG = ExperimentConfig()
```

---

## YAML Schema (reference only — code uses dataclasses)

```yaml
experiment:
  hypothesis_id: "H-M2"
  h_m1_results_path: "results/h-m1/results.jsonl"
  output_dir: "results/h-m2/"
  figures_dir: "figures/"
  seed: 42

verifier:
  timeout_secs: 10
  workers: 4
  pyright_cmd: ["pyright", "--outputjson"]
  mypy_cmd: ["mypy", "--no-error-summary"]

z3:
  model: "gpt-4o-mini"
  temperature: 0.0
  max_tokens: 512
  expected_coverage: 0.4

statistics:
  alpha: 0.05
  effect_size_threshold: 0.06
  pairwise_diff_threshold: 0.20

visualization:
  dpi: 150
  format: "png"
  figsize: [10, 6]
  verifier_colors:
    execution: "steelblue"
    pyright: "coral"
    mypy: "mediumseagreen"
    z3: "mediumpurple"
```
