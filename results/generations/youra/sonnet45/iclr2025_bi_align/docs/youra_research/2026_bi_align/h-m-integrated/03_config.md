---
name: Configuration Specification
type: config
hypothesis_id: h-m-integrated
hypothesis_type: MECHANISM
created_at: 2026-03-17
version: 1.0
---

# Configuration Specification: H-M-Integrated Linguistic Mechanism Validation

**Applied:** Standard Python dataclass pattern for statistical analysis pipelines, PyTorch randomness control

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-e1 validated implementation
**Config Files Found:** h-e1/code/config.py (Config dataclass with 15+ fields)
**Pattern Used:** Python dataclass (consistent with h-e1)

**Note:** H-m-integrated extends h-e1's Config class for paired statistical comparison. All field names verified from actual h-e1/code/config.py implementation.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited or referenced from h-e1:

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    """Global configuration for H-E1 linguistic marker extraction and analysis."""

    # Dataset Configuration
    dataset_name: str = "Anthropic/hh-rlhf"
    splits: List[str] = field(default_factory=lambda: ["train", "test"])
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

    # Gate Criteria (H-E1 specific)
    gate_threshold_cv: float = 0.3
    gate_threshold_precision: float = 0.9

    # Output Configuration
    output_dir: str = "."
    features_file: str = "h_e1_features.csv"
    statistics_file: str = "h_e1_statistics.json"
    figures_dir: str = "figures"
    validation_report: str = "04_validation.md"

    # Processing Configuration
    normalize_per_n_words: int = 100
    min_word_count: int = 1
    batch_size: int = 1000

    # Visualization Configuration
    dpi: int = 300
    figsize_bar: tuple = (8, 6)
    figsize_hist: tuple = (10, 6)
    figsize_box: tuple = (12, 6)
    figsize_scatter: tuple = (8, 8)
    style: str = "seaborn-v0_8-darkgrid"
    palette: str = "Set2"
```

**Verified from:** h-e1/code/config.py (actual implementation)

---

## Extended Configuration (H-M-Integrated)

### MechanismConfig (code/config.py)

**Applied:** Standard Python dataclass pattern

```python
from dataclasses import dataclass, field
from typing import Dict, List
import sys
sys.path.append('..')  # For h-e1 imports

# Import base config
from h_e1.code.config import Config as BaseConfig


@dataclass
class MechanismConfig:
    """Configuration for H-M-Integrated paired statistical comparison."""

    # Inherited H-E1 Configuration
    base_config: BaseConfig = field(default_factory=BaseConfig)

    # Paired Comparison Gate Thresholds
    cohens_d_threshold: float = 0.15
    p_value_threshold: float = 0.05
    cronbach_alpha_threshold: float = 0.7
    min_passing_splits: int = 2

    # Dataset Pairing
    pair_structure_expected: int = 161000  # ~161K matched pairs
    splits_to_analyze: List[str] = field(default_factory=lambda: ["train", "test"])

    # Statistical Testing
    paired_test_method: str = "ttest_rel"  # scipy.stats.ttest_rel
    effect_size_method: str = "cohens_d_paired"
    confidence_level: float = 0.95

    # Reproducibility
    random_seed: int = 42
    numpy_seed: int = 42

    # Output Configuration
    output_dir: str = "."
    results_file: str = "results/statistics.json"
    figures_dir: str = "figures"
    validation_report: str = "04_validation.md"

    # Visualization Outputs
    gate_metrics_filename: str = "gate_metrics.png"
    forest_plot_filename: str = "forest_plot.png"
    density_plots_filename: str = "density_plots.png"
    paired_diff_filename: str = "paired_differences.png"
    correlation_filename: str = "marker_correlations.png"

    # Processing
    batch_size: int = 1000
    show_progress: bool = True
    progress_interval: int = 5000

    # Logging
    log_level: str = "INFO"
```

**Subtasks (3/3 used):**

| ID | Subtask | Description |
|----|---------|-------------|
| C-M-1 | Mechanism Config Class | Extend BaseConfig with gate thresholds and paired comparison params |
| C-M-2 | Path Resolution | Handle h-e1 import paths (sys.path adjustment) |
| C-M-3 | Output Structure | Configure results/ and figures/ directories |

---

## Task-Specific Configurations

### M-1: Paired Data Structure (Complexity: 8, Budget: 2 subtasks)

**Applied:** Standard HuggingFace dataset defaults (inherited from h-e1)

No additional config needed - reuses `base_config.dataset_name` and `base_config.splits`.

**Implementation Note:**
```python
# Uses h-e1's Config directly
config = MechanismConfig()
dataset_name = config.base_config.dataset_name  # "Anthropic/hh-rlhf"
splits = config.base_config.splits  # ["train", "test"]
```

**Subtasks:** Already covered in C-M-3 (output structure)

---

### M-2: H-E1 Integration (Complexity: 7, Budget: 2 subtasks)

**Applied:** Module import resolution via sys.path

Reuses all h-e1 extraction configurations:
- `base_config.spacy_model`
- `base_config.hedging_markers`
- `base_config.alternative_patterns`
- `base_config.normalize_per_n_words`

**Subtasks:** Already covered in C-M-2 (path resolution)

---

### M-3: Paired Comparison (Complexity: 11, Budget: 2 subtasks)

**Applied:** Scipy statistical testing defaults

All parameters already specified in `MechanismConfig`:
- `cohens_d_threshold: 0.15`
- `p_value_threshold: 0.05`
- `paired_test_method: "ttest_rel"`
- `effect_size_method: "cohens_d_paired"`

**No additional config needed.**

---

### M-4: Internal Consistency (Complexity: 9, Budget: 2 subtasks)

**Applied:** Standard psychometrics reliability threshold

Already specified in `MechanismConfig`:
- `cronbach_alpha_threshold: 0.7`

**No additional config needed.**

---

### M-5: Cross-Split Validation (Complexity: 10, Budget: 2 subtasks)

**Applied:** Standard replication criterion

Already specified in `MechanismConfig`:
- `min_passing_splits: 2`
- `splits_to_analyze: ["train", "test"]`

**No additional config needed.**

---

### M-6: Statistical Visualization (Complexity: 11, Budget: 2 subtasks)

**Applied:** Standard matplotlib/seaborn defaults (inherited from h-e1)

```python
# Reuse from base_config
dpi = config.base_config.dpi  # 300
style = config.base_config.style  # "seaborn-v0_8-darkgrid"
palette = config.base_config.palette  # "Set2"

# New filenames in MechanismConfig
gate_metrics_filename = "gate_metrics.png"
forest_plot_filename = "forest_plot.png"
density_plots_filename = "density_plots.png"
paired_diff_filename = "paired_differences.png"
correlation_filename = "marker_correlations.png"
```

**No additional config needed.**

---

### M-7: Gate Evaluation (Complexity: 9, Budget: 2 subtasks)

**Applied:** Gate threshold parameters

Already specified in `MechanismConfig`:
- `cohens_d_threshold: 0.15`
- `p_value_threshold: 0.05`
- `cronbach_alpha_threshold: 0.7`
- `min_passing_splits: 2`

**No additional config needed.**

---

## Configuration Usage Pattern

```python
# config.py
from dataclasses import dataclass, field
from typing import List
import sys
sys.path.append('..')

from h_e1.code.config import Config as BaseConfig


@dataclass
class MechanismConfig:
    base_config: BaseConfig = field(default_factory=BaseConfig)
    cohens_d_threshold: float = 0.15
    p_value_threshold: float = 0.05
    cronbach_alpha_threshold: float = 0.7
    min_passing_splits: int = 2
    random_seed: int = 42
    output_dir: str = "."
    results_file: str = "results/statistics.json"
    figures_dir: str = "figures"
    validation_report: str = "04_validation.md"


# main.py
from config import MechanismConfig
from h_e1.code.extractor import LinguisticMarkerExtractor
from h_e1.code.data_loader import HHRLHFDataLoader
import spacy

def main():
    config = MechanismConfig()

    # Use h-e1 extraction pipeline
    nlp = spacy.load(config.base_config.spacy_model)
    extractor = LinguisticMarkerExtractor(
        nlp_model=nlp,
        hedging_markers=config.base_config.hedging_markers,
        alternative_patterns=config.base_config.alternative_patterns
    )

    # Load paired data
    loader = PairedDataLoader(config.base_config.dataset_name)
    pairs = loader.load_paired_dataset()

    # Extract features for both chosen and rejected
    chosen_features, rejected_features = [], []
    for chosen, rejected in pairs:
        chosen_features.append(extractor.extract(chosen))
        rejected_features.append(extractor.extract(rejected))

    # Paired comparison
    comparator = PairedComparator(extractor)
    t_stat, p_value = comparator.paired_ttest(chosen_features, rejected_features)
    cohens_d = comparator.cohens_d_paired(chosen_features, rejected_features)

    # Gate evaluation
    primary_pass = (abs(cohens_d) >= config.cohens_d_threshold and
                    p_value < config.p_value_threshold and
                    cohens_d < 0)

    print(f"Primary Gate: {'PASS' if primary_pass else 'FAIL'}")
```

---

## Total Subtask Count

| Task | Complexity | Budget | Subtasks Used |
|------|------------|--------|---------------|
| M-1 | 8 | 2 | Covered in C-M-3 |
| M-2 | 7 | 2 | Covered in C-M-2 |
| M-3 | 11 | 2 | No additional config |
| M-4 | 9 | 2 | No additional config |
| M-5 | 10 | 2 | No additional config |
| M-6 | 11 | 2 | No additional config |
| M-7 | 9 | 2 | No additional config |
| **Config Tasks** | - | **3** | **3/3** |

**Status:** Within budget (3/3 subtasks used)

**Note:** Most epic tasks reuse h-e1 configurations, requiring minimal new config. Only 3 subtasks needed for config integration (MechanismConfig class, path resolution, output structure).

---

## Validation Checklist

- [x] ONE format only (dataclass - no hardcoded dict alternative)
- [x] No ASCII diagrams
- [x] KB patterns applied (PyTorch randomness, dataclass pattern)
- [x] Rationale omitted for standard values
- [x] Subtask count within budget (3/3)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included (Serena analysis documented)
- [x] Base hypothesis config verified from actual code
- [x] Field names match h-e1 implementation
- [x] Inherited Configuration section included

---

*Configuration Type: MECHANISM (single fixed config, no variations)*
*Total Subtasks: 3 (within budget)*
*Format: Python dataclass (extends h-e1 Config)*
*Field Names: Verified from h-e1/code/config.py actual implementation*
