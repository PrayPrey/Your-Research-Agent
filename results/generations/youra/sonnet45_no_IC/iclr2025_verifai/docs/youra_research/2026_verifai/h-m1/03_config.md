# Configuration Specification: h-m1
## Natural Language Content Validation

**Date:** 2026-07-14  
**Hypothesis Type:** MECHANISM (Data Analysis)  
**Complexity Tier:** LIGHT  
**Subtask Budget:** 2 subtasks (M2, M3) - Medium complexity

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - H-E1 specs available but no actual code exists  
**Config Files Found:** None - designing new config schema  
**Pattern Used:** Python dataclass (validation pipeline standard)

**Note:** H-E1 was specified in archived routing_recovery folders but not implemented in current workspace. H-M1 inherits conceptual design from h-e1/03_config.md but implements from scratch.

---

## Knowledge Base Patterns Applied

**Applied:** Modular configuration pattern (validation pipeline with dataclass defaults)

---

## M2: Implement NL Validator [Complexity: 10, Budget: 1/2]

**Applied:** Regex-based text processing pattern (standard NLP preprocessing)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
import re

@dataclass
class NLValidatorConfig:
    """Configuration for natural language content validation."""
    
    # NL word counting
    min_word_count: int = 10
    nl_word_pattern: str = r'\b[a-zA-Z]{2,}\b'
    
    # Source type detection
    source_types: list = None
    
    def __post_init__(self):
        """Initialize source type categories."""
        if self.source_types is None:
            self.source_types = [
                'query_only',
                'result_only', 
                'both',
                'neither'
            ]
        
        # Compile regex pattern for performance
        self.compiled_pattern = re.compile(self.nl_word_pattern)
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M2-1 | NLValidatorConfig dataclass | Regex pattern, min word threshold, source types |

---

## M3: Extend Metrics Calculator [Complexity: 11, Budget: 2/2]

**Applied:** Statistical binning pattern for word count distribution

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class MetricsConfig:
    """Configuration for metrics calculation."""
    
    # NL presence threshold
    nl_presence_threshold: float = 0.90
    
    # Word count distribution bins
    word_count_bins: List[tuple] = field(default_factory=lambda: [
        (0, 5),
        (5, 10),
        (10, 20),
        (20, 50),
        (50, float('inf'))
    ])
    
    # Tool type categories
    research_tools: List[str] = field(default_factory=lambda: [
        'rag_search_knowledge_base',
        'rag_search_code_examples',
        'rag_read_full_page'
    ])
    
    data_processing_tools: List[str] = field(default_factory=lambda: [
        'serena_find_file',
        'serena_search_for_pattern',
        'serena_read_file'
    ])
    
    # Output schema keys
    required_metrics: List[str] = field(default_factory=lambda: [
        'nl_presence_rate',
        'source_breakdown',
        'tool_type_breakdown',
        'word_count_distribution'
    ])
    
    def get_bin_label(self, count: int) -> str:
        """Generate bin label for word count."""
        for lower, upper in self.word_count_bins:
            if lower <= count < upper:
                if upper == float('inf'):
                    return f"{lower}+"
                return f"{lower}-{upper}"
        return "0-5"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M3-1 | MetricsConfig dataclass | Threshold, bins, tool categories, output schema |

---

## Unified Configuration Module

```python
# code/config/config.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict
import re

@dataclass
class ValidationConfig:
    """Unified configuration for H-M1 NL validation pipeline."""
    
    # === File Paths ===
    trace_folder: str = ""
    hypothesis_folder: str = ""
    
    # === NL Validation (M2) ===
    min_word_count: int = 10
    nl_word_pattern: str = r'\b[a-zA-Z]{2,}\b'
    source_types: List[str] = field(default_factory=lambda: [
        'query_only', 'result_only', 'both', 'neither'
    ])
    
    # === Metrics Calculation (M3) ===
    nl_threshold: float = 0.90
    word_count_bins: List[tuple] = field(default_factory=lambda: [
        (0, 5), (5, 10), (10, 20), (20, 50), (50, float('inf'))
    ])
    
    research_tools: List[str] = field(default_factory=lambda: [
        'rag_search_knowledge_base',
        'rag_search_code_examples',
        'rag_read_full_page'
    ])
    
    data_processing_tools: List[str] = field(default_factory=lambda: [
        'serena_find_file',
        'serena_search_for_pattern',
        'serena_read_file'
    ])
    
    # === Visualization ===
    figure_dpi: int = 300
    figure_format: str = "png"
    
    # === Required Fields ===
    required_fields: List[str] = field(default_factory=lambda: [
        'tool_name', 'parameters', 'result'
    ])
    
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
        self.results_file = self.hypothesis_folder_path / "h_m1_results.json"
        
        # Create directories
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        # Compile regex pattern
        self.compiled_nl_pattern = re.compile(self.nl_word_pattern)
    
    def get_bin_label(self, count: int) -> str:
        """Generate bin label for word count."""
        for lower, upper in self.word_count_bins:
            if lower <= count < upper:
                return f"{lower}+" if upper == float('inf') else f"{lower}-{upper}"
        return "0-5"
```

---

## Usage Example

```python
from pathlib import Path
from config.config import ValidationConfig

# Initialize configuration
config = ValidationConfig(
    trace_folder=str(Path.home() / "research" / "mcp_traces"),
    hypothesis_folder=str(Path.home() / "research" / "h-m1")
)

# Access NL validator settings
print(f"NL word pattern: {config.nl_word_pattern}")
print(f"Minimum word count: {config.min_word_count}")
print(f"Compiled regex: {config.compiled_nl_pattern}")

# Access metrics settings
print(f"NL threshold: {config.nl_threshold}")
print(f"Word count bins: {config.word_count_bins}")

# Use in modules
from src.nl_content_validator import NLContentValidator
from src.metrics_calculator import MetricsCalculator

validator = NLContentValidator(
    min_word_count=config.min_word_count,
    pattern=config.compiled_nl_pattern
)

calculator = MetricsCalculator(
    validator=validator,
    threshold=config.nl_threshold
)
```

---

## Command-Line Integration

```python
# code/src/main.py
import argparse
from pathlib import Path
from config.config import ValidationConfig

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="H-M1: Validate natural language content in MCP traces"
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
        default=0.90,
        help="NL presence threshold (default: 0.90)"
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
        nl_threshold=args.threshold,
        min_word_count=args.min_words
    )
    
    print(f"H-M1: NATURAL LANGUAGE CONTENT VALIDATION")
    print(f"Threshold: {config.nl_threshold * 100}%")
    print(f"Minimum words: {config.min_word_count}")
    
    # Run validation pipeline
    from src.trace_parser import TraceParser
    from src.nl_content_validator import NLContentValidator
    from src.metrics_calculator import MetricsCalculator
    from src.evaluator import Evaluator
    from src.visualizer import Visualizer
    
    parser = TraceParser(config.trace_folder_path)
    validator = NLContentValidator(config.min_word_count, config.compiled_nl_pattern)
    calculator = MetricsCalculator(validator, config.nl_threshold)
    evaluator = Evaluator(calculator, config.nl_threshold)
    visualizer = Visualizer(config.figures_dir, config.figure_dpi)
    
    traces = parser.load_all_traces()
    results = evaluator.evaluate_hypothesis(traces)
    evaluator.save_results(results, config.results_file)
    visualizer.generate_all_figures(traces, results)
    
    print(f"\nGate Result: {results['gate_result']}")
    print(f"NL Presence Rate: {results['nl_presence_rate']:.2f}%")

if __name__ == "__main__":
    main()
```

---

## File Organization

```
{hypothesis_folder}/
├── code/
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py                # ValidationConfig (unified)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── trace_parser.py
│   │   ├── nl_content_validator.py  # Uses ValidationConfig
│   │   ├── metrics_calculator.py    # Uses ValidationConfig
│   │   ├── evaluator.py
│   │   ├── visualizer.py
│   │   └── main.py                  # CLI integration
│   ├── tests/
│   │   └── test_nl_validation.py
│   └── requirements.txt
├── figures/                          # Auto-created by config
└── h_m1_results.json
```

---

## Configuration Validation

```python
def validate_config(config: ValidationConfig):
    """Validate configuration values."""
    assert 0.0 <= config.nl_threshold <= 1.0, \
        "nl_threshold must be in [0, 1]"
    assert config.min_word_count > 0, \
        "min_word_count must be positive"
    assert config.trace_folder_path.exists(), \
        f"trace_folder does not exist: {config.trace_folder_path}"
    assert len(config.required_fields) > 0, \
        "required_fields cannot be empty"
    assert len(config.word_count_bins) > 0, \
        "word_count_bins cannot be empty"
    
    # Validate regex pattern
    try:
        re.compile(config.nl_word_pattern)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")
```

---

## Self-Validation Checklist

- [x] ONE format only (Python dataclass)
- [x] No ASCII diagrams
- [x] KB patterns applied (1 pattern noted)
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Green-field project - Serena skip acceptable

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 Coder - Implement config module per M2, M3 subtasks  
**Total Configuration Complexity:** 2 subtasks (M2: 1, M3: 1) - Within budget
