# Configuration Design: H-M3

**Hypothesis:** Positional Analysis of Marker-Confidence Ordering
**Date:** 2026-08-19

---

## Applied Patterns

Applied: Dataclass Configuration Pattern
Applied: Path-Based Config Pattern

---

## Configuration Schema

### Main Configuration Dataclass

```python
# config.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class H_M3_Config:
    """Configuration for H-M3 positional analysis experiment."""
    
    # Hypothesis metadata
    hypothesis_id: str = "H-M3"
    hypothesis_type: str = "MECHANISM"
    gate_type: str = "SHOULD_WORK"
    
    # Input paths
    h_m2_cache_path: Path = field(
        default_factory=lambda: Path("../h-m2/code/results/h-m2_results.json")
    )
    
    # Output paths
    output_dir: Path = field(default_factory=lambda: Path("results"))
    figures_dir: Path = field(default_factory=lambda: Path("figures"))
    
    # Gate thresholds
    gate_1_threshold: float = 0.99  # CoT order rate
    gate_2_threshold: float = 0.95  # Markers precede rate
    
    # CoT order detection
    cot_position_threshold: float = 0.3  # Confidence must be after 30% of output
    
    # Hedging markers
    hedging_markers: List[str] = field(default_factory=lambda: [
        'might', 'possibly', 'could', 'perhaps', 'may', 'likely',
        'unlikely', 'however', 'uncertain', 'although', 'but',
        'difficult to determine', 'not certain', 'hard to say',
        'alternatively', 'on the other hand', 'it depends'
    ])
    
    # Confidence pattern
    confidence_pattern: str = r'Confidence:\s*(\d+)%'
    
    # Visualization
    figure_dpi: int = 150
    bar_color_pass: str = '#2ecc71'
    bar_color_fail: str = '#e74c3c'
    
    def __post_init__(self):
        """Ensure output directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
```

---

## YAML Configuration

```yaml
# config.yaml

hypothesis:
  id: "H-M3"
  type: "MECHANISM"
  gate_type: "SHOULD_WORK"
  prerequisites:
    - "H-M2"

paths:
  h_m2_cache: "../h-m2/code/results/h-m2_results.json"
  output_dir: "results"
  figures_dir: "figures"

gates:
  gate_1:
    name: "cot_order_rate"
    threshold: 0.99
    description: ">99% outputs have CoT-then-confidence ordering"
  gate_2:
    name: "markers_precede_rate"
    threshold: 0.95
    description: ">95% markers precede confidence when markers exist"

analysis:
  cot_position_threshold: 0.3
  hedging_markers:
    - "might"
    - "possibly"
    - "could"
    - "perhaps"
    - "may"
    - "likely"
    - "unlikely"
    - "however"
    - "uncertain"
    - "although"
    - "but"
    - "difficult to determine"
    - "not certain"
    - "hard to say"
    - "alternatively"
    - "on the other hand"
    - "it depends"
  confidence_pattern: 'Confidence:\s*(\d+)%'

visualization:
  figure_dpi: 150
  colors:
    pass: "#2ecc71"
    fail: "#e74c3c"
```

---

## Environment Configuration

### requirements.txt

```
pyyaml>=6.0
matplotlib>=3.5
```

### No GPU/CUDA required
This is a CPU-only text analysis experiment.

---

## Default Values Summary

| Parameter | Default | Description |
|-----------|---------|-------------|
| gate_1_threshold | 0.99 | CoT order rate threshold |
| gate_2_threshold | 0.95 | Markers precede rate threshold |
| cot_position_threshold | 0.3 | Min relative position for confidence |
| figure_dpi | 150 | Figure output resolution |

---

## Configuration Loading

```python
# Usage in run_experiment.py

from config import H_M3_Config
import yaml

def load_config(config_path: Path = None) -> H_M3_Config:
    """Load configuration from YAML or use defaults."""
    if config_path and config_path.exists():
        with open(config_path) as f:
            yaml_config = yaml.safe_load(f)
        return H_M3_Config(
            gate_1_threshold=yaml_config['gates']['gate_1']['threshold'],
            gate_2_threshold=yaml_config['gates']['gate_2']['threshold'],
            # ... map other fields
        )
    return H_M3_Config()  # Use defaults
```

---

*Configuration design for H-M3 positional analysis experiment*
