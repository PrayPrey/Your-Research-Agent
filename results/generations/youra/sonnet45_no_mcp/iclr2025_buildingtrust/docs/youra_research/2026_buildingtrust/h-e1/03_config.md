# Configuration Specification: H-E1 Data Extraction Experiment

**Date:** 2026-04-14
**Hypothesis:** H-E1 (EXISTENCE)
**Type:** Data Extraction PoC
**Author:** Configuration Agent
**Phase:** Phase 3 - Implementation Planning

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new config schema
**Config Files Found:** None - new config
**Pattern Used:** dataclass

---

## Knowledge Base Patterns

**Applied:** Standard data extraction pipeline configuration pattern
**Applied:** EXISTENCE PoC minimal config pattern (single fixed configuration)

---

## Configuration Overview

**Design Philosophy:** Single fixed configuration for PoC validation. No hyperparameter tuning, no ablation configs, no parameter sweeps.

**Format:** Python dataclass (copy-paste ready for Phase 4)

**Budget Usage:** 4 subtasks allocated to E6 (Visualization) and E7 (Integration & Testing)

---

## E6: Visualization Configuration

**Complexity:** 10 | **Budget:** 2 subtasks

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import Tuple

@dataclass
class VisualizationConfig:
    """Visualization settings for H-E1 experiment figures"""
    
    # Figure dimensions (width, height in inches)
    figure_size_default: Tuple[int, int] = (10, 6)
    figure_size_heatmap: Tuple[int, int] = (12, 8)
    figure_size_timeline: Tuple[int, int] = (14, 4)
    
    # DPI for saved figures
    dpi: int = 300
    
    # Color scheme
    color_primary: str = "#2E86AB"  # Blue for bars
    color_secondary: str = "#A23B72"  # Purple for secondary elements
    color_success: str = "#06A77D"  # Green for passing metrics
    color_warning: str = "#F18F01"  # Orange for warnings
    color_failure: str = "#C73E1D"  # Red for failures
    
    # Heatmap colormap
    heatmap_cmap: str = "YlOrRd"  # Yellow-Orange-Red for granularity
    completeness_cmap: str = "RdYlGn"  # Red-Yellow-Green for completeness
    
    # Font settings
    font_size_title: int = 14
    font_size_label: int = 12
    font_size_tick: int = 10
    font_family: str = "sans-serif"
    
    # Output format
    output_format: str = "png"
    
    # Figure output directory (relative to h-e1/)
    output_dir: str = "figures"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E6-1 | Plot Settings | Implement figure size, DPI, color schemes for 4 required plots |
| E6-2 | Output Management | Configure save paths, file naming, format validation |

---

## E7: Integration & Testing Configuration

**Complexity:** 9 | **Budget:** 2 subtasks

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TestConfig:
    """Test and validation settings for H-E1 pipeline"""
    
    # Mock data parameters
    mock_model_families: List[str] = None
    mock_timepoints: List[str] = None
    mock_categories_truthfulqa: int = 12
    mock_categories_mmlu: int = 15
    
    # Validation thresholds (from PRD success criteria)
    min_families: int = 3
    min_categories_per_benchmark: int = 10
    min_completeness_pct: float = 90.0
    
    # Test execution settings
    use_mock_data: bool = False  # Set to True for testing without downloads
    test_timeout_seconds: int = 300  # 5 minutes max runtime
    
    # Output validation rules
    required_output_files: List[str] = None
    required_figure_files: List[str] = None
    
    def __post_init__(self):
        if self.mock_model_families is None:
            self.mock_model_families = ["GPT", "Claude", "Llama"]
        if self.mock_timepoints is None:
            self.mock_timepoints = ["baseline", "current"]
        if self.required_output_files is None:
            self.required_output_files = [
                "data/extracted/h-e1_extracted_data.csv",
                "data/extracted/h-e1_metadata.json",
                "data/extracted/h-e1_validation.json"
            ]
        if self.required_figure_files is None:
            self.required_figure_files = [
                "figures/gate_metrics.png",
                "figures/granularity_heatmap.png",
                "figures/completeness_matrix.png",
                "figures/temporal_timeline.png"
            ]

@dataclass
class IntegrationConfig:
    """End-to-end pipeline integration settings"""
    
    # Pipeline execution order
    pipeline_stages: List[str] = None
    
    # Retry settings for report downloads
    max_download_retries: int = 3
    retry_delay_seconds: int = 2
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: str = "logs/extraction.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Output atomicity (use temp files then rename)
    use_atomic_writes: bool = True
    temp_file_suffix: str = ".tmp"
    
    def __post_init__(self):
        if self.pipeline_stages is None:
            self.pipeline_stages = [
                "setup_environment",
                "collect_reports",
                "parse_and_extract",
                "validate_data",
                "compute_metrics",
                "generate_visualizations",
                "save_outputs"
            ]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E7-1 | Test Parameters | Mock data generation settings, validation thresholds, timeout limits |
| E7-2 | Integration Settings | Pipeline orchestration, retry logic, logging, atomic file writes |

---

## Core Experiment Configuration

**Note:** This section provides the main experiment config referenced by all modules.

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ExperimentConfig:
    """Main configuration for H-E1 data extraction experiment"""
    
    # Model families and timepoints
    model_families: List[str] = field(default_factory=lambda: ["GPT", "Claude", "Llama"])
    timepoints: List[str] = field(default_factory=lambda: ["baseline", "current"])
    benchmarks: List[str] = field(default_factory=lambda: ["TruthfulQA", "MMLU"])
    
    # Technical report URLs (manual download required)
    report_urls: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "GPT": {
            "baseline": "https://arxiv.org/abs/2005.14165",  # GPT-3
            "current": "https://arxiv.org/abs/2303.08774"     # GPT-4
        },
        "Claude": {
            "baseline": "https://www.anthropic.com/claude-2-1",
            "current": "https://www.anthropic.com/claude-3"
        },
        "Llama": {
            "baseline": "https://ai.meta.com/research/publications/llama-2-open-foundation-and-fine-tuned-chat-models/",
            "current": "https://ai.meta.com/blog/meta-llama-3/"
        }
    })
    
    # Success thresholds (gate condition)
    success_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "min_families": 3,
        "min_categories": 10,
        "min_completeness": 90.0
    })
    
    # Output schema
    output_columns: List[str] = field(default_factory=lambda: [
        "model_family", "timepoint", "benchmark", "category", "error_rate"
    ])
    
    # File paths (relative to h-e1/)
    data_dir: str = "data"
    reports_dir: str = "data/reports"
    extracted_dir: str = "data/extracted"
    figures_dir: str = "figures"
    logs_dir: str = "logs"
    
    # Output filenames
    output_csv: str = "h-e1_extracted_data.csv"
    output_metadata: str = "h-e1_metadata.json"
    output_validation: str = "h-e1_validation.json"
    
    # Execution settings
    max_runtime_minutes: int = 5
    enable_logging: bool = True
    
    # Visualization config
    viz_config: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Test config
    test_config: TestConfig = field(default_factory=TestConfig)
    
    # Integration config
    integration_config: IntegrationConfig = field(default_factory=IntegrationConfig)
```

---

## Configuration Usage Examples

### Basic Usage

```python
from src.config import ExperimentConfig

# Initialize with defaults
config = ExperimentConfig()

# Access report URLs
gpt4_url = config.report_urls["GPT"]["current"]

# Check success thresholds
min_families = config.success_thresholds["min_families"]

# Get output paths
import os
output_path = os.path.join(config.extracted_dir, config.output_csv)
```

### Testing Mode

```python
# Enable mock data for testing
config = ExperimentConfig()
config.test_config.use_mock_data = True
config.test_config.mock_categories_truthfulqa = 12
config.test_config.mock_categories_mmlu = 15
```

### Custom Visualization

```python
# Override default figure sizes
config = ExperimentConfig()
config.viz_config.figure_size_default = (12, 8)
config.viz_config.dpi = 150  # Lower DPI for faster rendering
```

---

## Directory Structure Setup

```python
import os

def setup_directories(config: ExperimentConfig) -> None:
    """Create required directory structure"""
    dirs = [
        config.data_dir,
        config.reports_dir,
        config.extracted_dir,
        config.figures_dir,
        config.logs_dir
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
```

---

## Validation Configuration

### Gate Condition Implementation

```python
def check_gate_condition(metrics: Dict, config: ExperimentConfig) -> bool:
    """
    Evaluate MUST_WORK gate condition
    
    Args:
        metrics: Dict with keys ['families_with_data', 'categories_truthfulqa', 
                                  'categories_mmlu', 'data_completeness_pct']
        config: ExperimentConfig instance
    
    Returns:
        bool: True if gate condition passed
    """
    thresholds = config.success_thresholds
    
    families_ok = metrics['families_with_data'] >= thresholds['min_families']
    granularity_ok = (
        metrics['categories_truthfulqa'] >= thresholds['min_categories'] and
        metrics['categories_mmlu'] >= thresholds['min_categories']
    )
    completeness_ok = metrics['data_completeness_pct'] >= thresholds['min_completeness']
    
    return families_ok and granularity_ok and completeness_ok
```

---

## Output File Specifications

### CSV Schema (h-e1_extracted_data.csv)

```python
EXPECTED_SCHEMA = {
    'model_family': 'str',   # One of: GPT, Claude, Llama
    'timepoint': 'str',      # One of: baseline, current
    'benchmark': 'str',      # One of: TruthfulQA, MMLU
    'category': 'str',       # Category/subject name
    'error_rate': 'float'    # Percentage (0-100)
}

EXPECTED_ROWS = "60-120"  # 3 families × 2 timepoints × 2 benchmarks × 10-20 categories
```

### Metadata Schema (h-e1_metadata.json)

```python
METADATA_SCHEMA = {
    'extraction_timestamp': 'ISO 8601 datetime string',
    'report_sources': {
        'GPT': {
            'baseline': {'url': 'str', 'access_date': 'str', 'publication_date': 'str'},
            'current': {'url': 'str', 'access_date': 'str', 'publication_date': 'str'}
        },
        # ... same for Claude, Llama
    },
    'extraction_version': 'str',  # e.g., "1.0.0"
    'total_reports_processed': 'int'
}
```

### Validation Schema (h-e1_validation.json)

```python
VALIDATION_SCHEMA = {
    'gate_passed': 'bool',
    'families_with_data': 'int',
    'categories_truthfulqa': 'int',
    'categories_mmlu': 'int',
    'data_completeness_pct': 'float',
    'validation_timestamp': 'ISO 8601 datetime string',
    'issues': 'List[str]'  # Empty if gate_passed=True
}
```

---

## Environment Variables (Optional)

**Note:** Not required for PoC, but useful for deployment.

```bash
# Optional overrides
export H_E1_DATA_DIR="/custom/path/to/data"
export H_E1_LOG_LEVEL="DEBUG"
export H_E1_USE_MOCK_DATA="true"
```

---

## Configuration Validation

### Self-Check Checklist

**Format Compliance:**
- [x] Single format only (Python dataclass)
- [x] No ASCII diagrams
- [x] No full KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Total length < 400 lines

**EXISTENCE Rules:**
- [x] Single fixed config (no hyperparameter grids)
- [x] Default values from standard practices
- [x] No ablation configs
- [x] Minimal epochs equivalent (N/A - no training)

**Budget Compliance:**
- [x] 4 subtasks allocated (E6: 2, E7: 2)
- [x] Focused on medium-complexity modules only

**Serena/Archon Compliance:**
- [x] Codebase Analysis section included
- [x] Green-field project noted (Serena skip acceptable)
- [x] KB patterns noted (MCP unavailable - standard patterns applied)

---

## Phase 4 Integration Notes

### Copy-Paste Instructions

1. Create `h-e1/code/src/config.py`
2. Copy all dataclass definitions from this document
3. Import in other modules:
   ```python
   from src.config import ExperimentConfig, VisualizationConfig, TestConfig
   ```

### Key Configuration Points

- **Report URLs:** May require updates if links change (check accessibility before execution)
- **Success Thresholds:** Fixed per PRD requirements (do not modify without hypothesis change)
- **Output Paths:** All relative to `h-e1/` directory
- **Mock Data:** Enable `test_config.use_mock_data = True` for integration testing without downloads

---

**Document Status:** ✅ Complete
**Budget Used:** 4/4 subtasks (E6: 2, E7: 2)
**Next Phase:** Phase 4 - Implementation (Coder Agent)
**Config Format:** Python Dataclass (ready for copy-paste)
