# Configuration Specification: h-e1
## MCP Trace Data Availability Validation

**Date:** 2026-07-13  
**Hypothesis Type:** EXISTENCE (PoC)  
**Complexity Tier:** LIGHT  
**Subtask Budget:** 2 subtasks used

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch - no existing config to analyze  
**Config Files Found:** None - designing new config schema  
**Pattern Used:** Python dataclass (validation pipeline standard)

---

## Knowledge Base Patterns Applied

**Applied:** Modular configuration pattern (PyTorch Inductor config.py)  
**Applied:** Path-based config with dataclass defaults (Stable Diffusion workflow)

---

## Configuration Overview

This is a data validation task requiring:
1. File path specifications (trace folder, output locations)
2. Validation thresholds (completeness, word count)
3. Visualization settings (DPI, figure sizes)
4. Logging configuration

**Format:** Python dataclass (single source of truth)

---

## C-1: Base Configuration [Complexity: 1, Budget: 1/2]

**Applied:** Standard Python dataclass pattern with pathlib integration

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class ValidationConfig:
    """Base configuration for MCP trace validation."""
    
    # File paths
    trace_folder: str = ""
    hypothesis_folder: str = ""
    
    # Validation thresholds
    completeness_threshold: float = 0.95
    min_word_count: int = 10
    
    # Required fields for tool calls
    required_fields: List[str] = field(default_factory=lambda: [
        'tool_name', 
        'parameters', 
        'result'
    ])
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    
    def __post_init__(self):
        """Validate and convert paths."""
        if not self.trace_folder:
            raise ValueError("trace_folder must be specified")
        if not self.hypothesis_folder:
            raise ValueError("hypothesis_folder must be specified")
        
        self.trace_folder_path = Path(self.trace_folder)
        self.hypothesis_folder_path = Path(self.hypothesis_folder)
        
        # Derived paths
        self.figures_dir = self.hypothesis_folder_path / "figures"
        self.results_file = self.hypothesis_folder_path / "h_e1_results.json"
        
        # Create directories if needed
        self.figures_dir.mkdir(parents=True, exist_ok=True)
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ValidationConfig dataclass | Core config with paths, thresholds, field validation |

---

## C-2: Visualization Configuration [Complexity: 1, Budget: 2/2]

**Applied:** Matplotlib defaults with DPI override for publication quality

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class VisualizationConfig:
    """Configuration for figure generation."""
    
    # Figure output settings
    figure_dpi: int = 300
    figure_format: str = "png"
    
    # Figure sizes (width, height in inches)
    gate_metrics_size: tuple = (8, 6)
    per_file_size: tuple = (10, 6)
    breakdown_size: tuple = (8, 6)
    nl_content_size: tuple = (10, 6)
    
    # Color scheme
    success_color: str = "#2ecc71"
    failure_color: str = "#e74c3c"
    threshold_color: str = "#95a5a6"
    mean_color: str = "#3498db"
    
    # Font sizes
    title_fontsize: int = 14
    label_fontsize: int = 12
    tick_fontsize: int = 10
    legend_fontsize: int = 10
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | VisualizationConfig dataclass | Figure settings, colors, sizes for 4 plots |

---

## Usage Example

```python
from pathlib import Path

# Initialize configuration
config = ValidationConfig(
    trace_folder=str(Path.home() / "research" / "mcp_traces"),
    hypothesis_folder=str(Path.home() / "research" / "h-e1")
)

viz_config = VisualizationConfig()

# Access configuration
print(f"Results will be saved to: {config.results_file}")
print(f"Completeness threshold: {config.completeness_threshold}")
print(f"Figure DPI: {viz_config.figure_dpi}")

# Use in modules
parser = TraceParser(config.trace_folder_path)
visualizer = Visualizer(config.figures_dir, viz_config)
```

---

## Command-Line Integration

```python
# In main.py
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Validate MCP trace completeness"
    )
    parser.add_argument(
        "--trace_folder",
        type=str,
        required=True,
        help="Path to folder containing MCP trace files (.jsonl)"
    )
    parser.add_argument(
        "--hypothesis_folder",
        type=str,
        required=True,
        help="Path to hypothesis output folder"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="Completeness threshold (default: 0.95)"
    )
    parser.add_argument(
        "--min_words",
        type=int,
        default=10,
        help="Minimum word count for NL content (default: 10)"
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    config = ValidationConfig(
        trace_folder=args.trace_folder,
        hypothesis_folder=args.hypothesis_folder,
        completeness_threshold=args.threshold,
        min_word_count=args.min_words
    )
    
    # Run validation pipeline...
```

---

## Configuration Files Structure

```
{hypothesis_folder}/
├── code/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── validation_config.py    # ValidationConfig dataclass
│   │   └── visualization_config.py # VisualizationConfig dataclass
│   └── src/
│       └── main.py                 # CLI integration
└── figures/                         # Auto-created by config
```

---

## Environment Variables (Optional)

For CI/CD environments, support environment variable overrides:

```python
import os

@dataclass
class ValidationConfig:
    trace_folder: str = field(
        default_factory=lambda: os.getenv("MCP_TRACE_FOLDER", "")
    )
    hypothesis_folder: str = field(
        default_factory=lambda: os.getenv("HYPOTHESIS_FOLDER", "")
    )
    completeness_threshold: float = field(
        default_factory=lambda: float(os.getenv("COMPLETENESS_THRESHOLD", "0.95"))
    )
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
```

---

## Validation Logic

```python
def validate_config(config: ValidationConfig):
    """Validate configuration values."""
    assert 0.0 <= config.completeness_threshold <= 1.0, \
        "completeness_threshold must be in [0, 1]"
    assert config.min_word_count > 0, \
        "min_word_count must be positive"
    assert config.trace_folder_path.exists(), \
        f"trace_folder does not exist: {config.trace_folder_path}"
    assert len(config.required_fields) > 0, \
        "required_fields cannot be empty"
    assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"], \
        f"Invalid log_level: {config.log_level}"
```

---

## Self-Validation Checklist

- [x] ONE format only (Python dataclass)
- [x] No ASCII diagrams
- [x] KB patterns applied (2 patterns noted)
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Green-field project - Serena skip acceptable

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 Coder - Implement config classes per subtasks  
**Total Configuration Complexity:** 2 (LIGHT tier, within budget)
