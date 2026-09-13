---
name: Configuration Specification
type: config
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_at: 2026-03-17
version: 1.0
---

# Configuration Specification: H-E1 Linguistic Marker Extraction

**Applied:** Standard Python dataclass pattern for NLP analysis pipelines

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - new config design (no existing codebase in current h-e1)
**Config Files Found:** None - new implementation
**Pattern Used:** Python dataclass (consistent with archived h-e1 versions)

**Note:** Archived versions found in `_archive/` folders use dataclass pattern. Current h-e1 is fresh implementation.

---

## Global Configuration

```python
from dataclasses import dataclass, field
from typing import Set, List


@dataclass
class Config:
    """Global configuration for H-E1 linguistic marker extraction and analysis."""

    # Dataset Configuration
    dataset_name: str = "Anthropic/hh-rlhf"
    splits: List[str] = field(default_factory=lambda: [
        "train",
        "test"
    ])
    random_seed: int = 42

    # NLP Processing
    spacy_model: str = "en_core_web_sm"

    # Linguistic Marker Definitions
    hedging_markers: Set[str] = field(default_factory=lambda: {
        'perhaps', 'maybe', 'might', 'could', 'possibly',
        'probably', 'likely', 'seems', 'appears', 'suggests',
        'tend', 'often', 'sometimes', 'generally', 'typically'
    })

    alternative_patterns: List[str] = field(default_factory=lambda: [
        r'\byou (could|might|may)\b',
        r'\b(one|another) (option|approach|alternative|way)\b',
        r'\balternatively\b',
        r'\bon the other hand\b',
        r'\byou (can|have) the option\b'
    ])

    # Gate Criteria
    gate_threshold_cv: float = 0.3
    gate_threshold_precision: float = 0.9

    # Output Configuration
    output_dir: str = "."
    features_file: str = "h_e1_features.csv"
    statistics_file: str = "h_e1_statistics.json"
    figures_dir: str = "figures"
    validation_report: str = "04_validation.md"
```

---

## Task-Specific Configurations

### A-1: Data Pipeline (Complexity: 8, Budget: 2 subtasks)

**Applied:** Standard HuggingFace dataset defaults

```python
@dataclass
class DataLoaderConfig:
    """Configuration for HH-RLHF dataset loading."""

    dataset_name: str = "Anthropic/hh-rlhf"
    splits: List[str] = field(default_factory=lambda: ["train", "test"])
    cache_dir: str = None  # Uses default HF cache
    remove_special_tokens: bool = True
    special_tokens: List[str] = field(default_factory=lambda: ["Human:", "Assistant:"])
```

**Subtasks (2/2 used):**

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Dataset Loading | Load 3 splits via HuggingFace API |
| C-1-2 | Text Preprocessing | Remove special tokens, compute word counts |

---

### A-2: Feature Extraction (Complexity: 11, Budget: 2 subtasks)

**Applied:** Standard spaCy POS tagging + regex patterns

```python
@dataclass
class ExtractorConfig:
    """Configuration for linguistic marker extraction."""

    spacy_model: str = "en_core_web_sm"
    batch_size: int = 1000

    # Modal verb extraction
    modal_pos_tag: str = "MD"

    # Hedging extraction
    hedging_markers: Set[str] = field(default_factory=lambda: {
        'perhaps', 'maybe', 'might', 'could', 'possibly',
        'probably', 'likely', 'seems', 'appears', 'suggests',
        'tend', 'often', 'sometimes', 'generally', 'typically'
    })

    # Alternative-framing extraction
    alternative_patterns: List[str] = field(default_factory=lambda: [
        r'\byou (could|might|may)\b',
        r'\b(one|another) (option|approach|alternative|way)\b',
        r'\balternatively\b',
        r'\bon the other hand\b',
        r'\byou (can|have) the option\b'
    ])

    # Normalization
    normalize_per_n_words: int = 100
    min_word_count: int = 1
```

**Subtasks (2/2 used):**

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Modal & Hedging Extraction | Implement spaCy POS + lexicon matching |
| C-2-2 | Alternative-Framing Extraction | Implement regex pattern matching |

---

### A-3: Statistical Analysis (Complexity: 9, Budget: 2 subtasks)

**Applied:** Standard NumPy statistics defaults

```python
@dataclass
class StatisticalAnalyzerConfig:
    """Configuration for distributional statistics computation."""

    # Gate criteria thresholds
    gate_threshold_cv: float = 0.3
    gate_threshold_precision: float = 0.9

    # Statistics to compute
    compute_mean: bool = True
    compute_std: bool = True
    compute_cv: bool = True
    compute_min_max: bool = True
    compute_median: bool = True

    # Cross-split validation
    per_split_analysis: bool = True
    cv_tolerance: float = 0.05
```

**Subtasks (2/2 used):**

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | CV Computation | Compute mean, SD, CV for all markers |
| C-3-2 | Gate Evaluation | Evaluate gate condition (CV > 0.3) |

---

### A-4: Visualization (Complexity: 7, Budget: 2 subtasks)

**Applied:** Standard matplotlib/seaborn defaults

```python
@dataclass
class VisualizerConfig:
    """Configuration for figure generation."""

    figures_dir: str = "figures"
    dpi: int = 300
    figsize_bar: tuple = (8, 6)
    figsize_hist: tuple = (10, 6)
    figsize_box: tuple = (12, 6)
    figsize_scatter: tuple = (8, 8)

    # Gate metrics plot (MANDATORY)
    gate_metrics_filename: str = "gate_metrics.png"

    # Optional plots
    distribution_filename: str = "distribution.png"
    split_comparison_filename: str = "split_comparison.png"
    correlation_filename: str = "correlation.png"

    # Styling
    style: str = "seaborn-v0_8-darkgrid"
    palette: str = "Set2"
```

**Subtasks (2/2 used):**

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Gate Metrics Plot | Bar chart comparing targets vs actuals (MANDATORY) |
| C-4-2 | Optional Plots | Distribution, box plots, correlation scatter |

---

### A-5: Integration (Complexity: 10, Budget: 2 subtasks)

**Applied:** Simple CLI argument parsing

```python
@dataclass
class MainConfig:
    """Configuration for main runner and orchestration."""

    # Logging
    log_level: str = "INFO"
    log_to_file: bool = False
    log_file: str = "experiment.log"

    # Progress reporting
    show_progress: bool = True
    progress_interval: int = 5000

    # Output files
    features_file: str = "h_e1_features.csv"
    statistics_file: str = "h_e1_statistics.json"
    validation_report: str = "04_validation.md"

    # Reproducibility
    random_seed: int = 42
```

**Subtasks (2/2 used):**

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Main Runner | Orchestrate pipeline execution |
| C-5-2 | Results Report | Generate 04_validation.md with gate decision |

---

## Configuration Usage Pattern

```python
# config.py
from dataclasses import dataclass, field
from typing import Set, List


@dataclass
class Config:
    # Global settings
    dataset_name: str = "Anthropic/hh-rlhf"
    random_seed: int = 42
    spacy_model: str = "en_core_web_sm"

    # Marker definitions
    hedging_markers: Set[str] = field(default_factory=lambda: {
        'perhaps', 'maybe', 'might', 'could', 'possibly',
        'probably', 'likely', 'seems', 'appears', 'suggests',
        'tend', 'often', 'sometimes', 'generally', 'typically'
    })

    alternative_patterns: List[str] = field(default_factory=lambda: [
        r'\byou (could|might|may)\b',
        r'\b(one|another) (option|approach|alternative|way)\b',
        r'\balternatively\b',
        r'\bon the other hand\b',
        r'\byou (can|have) the option\b'
    ])

    # Gate thresholds
    gate_threshold_cv: float = 0.3
    gate_threshold_precision: float = 0.9

    # Output paths
    output_dir: str = "."
    figures_dir: str = "figures"


# main.py
from config import Config

def main():
    config = Config()

    # Use config throughout pipeline
    loader = DataLoader(config.dataset_name)
    extractor = LinguisticExtractor(config.spacy_model,
                                    config.hedging_markers,
                                    config.alternative_patterns)
    analyzer = StatisticalAnalyzer(config.gate_threshold_cv)
    visualizer = Visualizer(config.figures_dir)

    # Pipeline execution
    data = loader.load_dataset()
    features = extractor.extract_all_features(data)
    stats = analyzer.compute_statistics(features)
    visualizer.plot_gate_metrics(stats)

    # Gate evaluation
    gate_passed = stats['modal_cv'] > config.gate_threshold_cv
    print(f"Gate Decision: {'PASS' if gate_passed else 'FAIL'}")
```

---

## Total Subtask Count

| Task | Complexity | Budget | Subtasks Used |
|------|------------|--------|---------------|
| A-1 | 8 | 2 | 2/2 |
| A-2 | 11 | 2 | 2/2 |
| A-3 | 9 | 2 | 2/2 |
| A-4 | 7 | 2 | 2/2 |
| A-5 | 10 | 2 | 2/2 |
| **TOTAL** | **45** | **10** | **10/10** |

**Status:** Within budget (10/10 subtasks used)

---

## Validation Checklist

- [x] ONE format only (dataclass - no hardcoded dict alternative)
- [x] No ASCII diagrams
- [x] KB patterns applied (noted in header)
- [x] Rationale omitted for standard values
- [x] Subtask count within budget (10/10)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Per-task configs are copy-paste ready
- [x] EXISTENCE hypothesis - single fixed config (no hyperparameter grid)

---

*Configuration Type: EXISTENCE PoC (single fixed config, no variations)*
*Total Subtasks: 10 (within 2 per task budget)*
*Format: Python dataclass (consistent with project pattern)*
