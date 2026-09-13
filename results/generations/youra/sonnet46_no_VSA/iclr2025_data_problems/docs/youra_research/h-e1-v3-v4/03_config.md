# H-E1-V3-V4 Configuration

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis extension (h-e1)
**Status**: config classes verified from base h-e1/03_config.md
**Config Files Found**: docs/youra_research/h-e1/03_config.md
**Pattern Used**: dataclass

Applied: Python dataclass config pattern (inherited from h-e1 baseline)

---

## Changes from h-e1

| Field | h-e1 | h-e1-v3-v4 | Reason |
|-------|------|------------|--------|
| `GateConfig.cramers_v_min` | 0.29 | **0.40** | Tighter lower bound from v3 calibration |
| `GateConfig.cramers_v_max` | 0.45 | **0.57** | Wider upper bound from v3 calibration |
| `MechanismConfig` | not present | **added** | Wider check bounds for mechanism verification |
| `OutputConfig.*` | h-e1/ | **h-e1-v3-v4/** | Path update for this hypothesis version |

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
    cramers_v_min: float = 0.40   # Non-standard: raised from 0.29 (v3 calibration result)
    cramers_v_max: float = 0.57   # Non-standard: raised from 0.45 (v3 calibration result)
    holm_p_max: float = 0.001

@dataclass
class MechanismConfig:
    # Wider bounds for mechanism verification pass (not gate)
    v_min: float = 0.38
    v_max: float = 0.60

@dataclass
class OutputConfig:
    results_path: str = "docs/youra_research/h-e1-v3-v4/results.json"
    gate_verdict_path: str = "docs/youra_research/h-e1-v3-v4/gate_verdict.json"
    figures_dir: str = "docs/youra_research/h-e1-v3-v4/figures/"
    figure_dpi: int = 150
    figure_format: str = "png"

@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    mechanism: MechanismConfig = field(default_factory=MechanismConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

CONFIG = ExperimentConfig()
```

**Usage**: `from config import CONFIG`

---

## YAML Schema (Reference)

```yaml
dataset:
  hf_dataset_id: "togethercomputer/RedPajama-Data-V2"
  hf_split: "sample"
  hf_name: "sample"
  cache_path: "docs/youra_research/redpajama_sample.parquet"
  expected_rows: 208263
  row_tolerance: 0.05
  min_rows: 190000
  languages: ["en", "de", "fr", "es", "it"]
  quality_signal_field: "quality_signals"
  perplexity_key: "ccnet_perplexity"
  max_nan_ratio: 0.01

analysis:
  k_values: [10, 20, 30, 40, 50]
  retention_rule: "less_than"
  cramer_method: "cramer"
  multiple_testing_method: "holm"
  seed: 42

gate:
  cramers_v_min: 0.40
  cramers_v_max: 0.57
  holm_p_max: 0.001

mechanism:
  v_min: 0.38
  v_max: 0.60

output:
  results_path: "docs/youra_research/h-e1-v3-v4/results.json"
  gate_verdict_path: "docs/youra_research/h-e1-v3-v4/gate_verdict.json"
  figures_dir: "docs/youra_research/h-e1-v3-v4/figures/"
  figure_dpi: 150
  figure_format: "png"
```
