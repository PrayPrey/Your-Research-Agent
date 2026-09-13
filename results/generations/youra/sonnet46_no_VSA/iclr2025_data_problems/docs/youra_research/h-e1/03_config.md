# H-E1 Configuration

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Configuration

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class DatasetConfig:
    hf_dataset_id: str = "togethercomputer/RedPajama-Data-V2"
    hf_split: str = "sample"
    hf_name: str = "sample"
    cache_path: str = "docs/youra_research/redpajama_sample.parquet"
    expected_rows: int = 208263
    row_tolerance: float = 0.05
    min_rows: int = 190000
    languages: List[str] = field(default_factory=lambda: ["en", "de", "fr", "es", "it"])
    quality_signal_field: str = "quality_signals"
    perplexity_key: str = "ccnet_perplexity"
    max_nan_ratio: float = 0.01

@dataclass
class AnalysisConfig:
    k_values: List[int] = field(default_factory=lambda: [10, 20, 30, 40, 50])
    retention_rule: str = "less_than"  # retain if perplexity < threshold
    cramer_method: str = "cramer"
    multiple_testing_method: str = "holm"
    seed: int = 42

@dataclass
class GateConfig:
    cramers_v_min: float = 0.29
    cramers_v_max: float = 0.45
    holm_p_max: float = 0.001

@dataclass
class OutputConfig:
    results_path: str = "docs/youra_research/h-e1/results.json"
    gate_verdict_path: str = "docs/youra_research/h-e1/gate_verdict.json"
    figures_dir: str = "docs/youra_research/h-e1/figures/"
    figure_dpi: int = 150
    figure_format: str = "png"

@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

CONFIG = ExperimentConfig()
```

**Usage**: `from config import CONFIG`
