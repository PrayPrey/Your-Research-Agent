# Logic Design: H-E1

**Date:** 2026-03-18
**Hypothesis:** Human Inter-Annotator Agreement Ceiling
**Type:** EXISTENCE (Proof of Concept)
**Designer:** Phase 3 Logic Agent
**Budget:** 7 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type**: green-field with archived reference
**Status**: New implementation - H-E1 focuses on human annotation agreement (Cohen's kappa), differs from archived MVR-BCS/ICC analysis
**Analyzed Path**: Archived code at `_archive/20260318T055954_routing_recovery/h-e1/code/`
**Relevant Symbols**: Archived implementation provides modular patterns (DataCollector, Analyzer, Visualizer) but different statistical focus (ICC vs kappa)

---

## E1-1: Dataset Collection Pipeline [Complexity: 12, Budget: 1]

**Applied**: Standard pandas API pattern

### API Signatures

```python
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional

class DataCollector:
    """Multi-repository dataset collector with stratified sampling"""

    def __init__(self, config: dict):
        """Initialize collector with configuration."""
        self.config = config
        self.random_seed = config.get("random_seed", 42)

    def collect_all(self) -> pd.DataFrame:
        """Collect 30 datasets across 3 repositories. Returns: [30, columns]"""
        ...

    def collect_huggingface(self, n: int = 10, modality_split: Optional[Dict] = None) -> pd.DataFrame:
        """Collect n datasets from HuggingFace Hub. Returns: [n, columns]"""
        ...

    def collect_openml(self, n: int = 10, modality_split: Optional[Dict] = None) -> pd.DataFrame:
        """Collect n datasets from OpenML API. Returns: [n, columns]"""
        ...

    def collect_uci(self, n: int = 10) -> pd.DataFrame:
        """Collect n datasets from UCI via web scraping. Returns: [n, columns]"""
        ...

    def stratify_by_quality(self, df: pd.DataFrame, n_per_stratum: int = 10) -> pd.DataFrame:
        """Stratify into high/medium/low quality. Returns: [3*n_per_stratum, columns]"""
        ...

    def save_metadata(self, df: pd.DataFrame, output_path: Path) -> None:
        """Save metadata CSV with schema: dataset_id, repository, modality, quality_stratum"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| df | [30, 4] | dataset_id, repository, modality, quality_stratum |
| hf_df | [10, 4] | HuggingFace subset |
| openml_df | [10, 4] | OpenML subset |
| uci_df | [10, 4] | UCI subset |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Multi-repo collection | HF/OpenML/UCI API integration with stratification |

---

## E1-2: Documentation Extraction [Complexity: 8, Budget: 1]

**Applied**: Standard file I/O pattern

### API Signatures

```python
class DocumentationExtractor:
    """Extract and format dataset documentation from API responses"""

    def __init__(self, config: dict):
        """Initialize with output directory configuration."""
        self.output_dir = Path(config.get("documentation_dir", "data/h-e1/documentation"))

    def extract_from_metadata(self, df: pd.DataFrame) -> None:
        """Extract documentation for all datasets in df. Creates 30 text files."""
        ...

    def extract_hf_documentation(self, dataset_id: str, output_path: Path) -> bool:
        """Extract HuggingFace dataset card. Returns: success status"""
        ...

    def extract_openml_documentation(self, dataset_id: str, output_path: Path) -> bool:
        """Extract OpenML metadata JSON as text. Returns: success status"""
        ...

    def extract_uci_documentation(self, dataset_id: str, output_path: Path) -> bool:
        """Extract UCI HTML description. Returns: success status"""
        ...

    def format_filename(self, repository: str, index: int) -> str:
        """Generate filename: hf_001.txt, openml_001.txt, uci_001.txt"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | File naming | Configure output paths and naming patterns |

---

## E1-3: Annotation Protocol Implementation [Complexity: 9, Budget: 1]

**Applied**: CSV-based annotation workflow pattern

### API Signatures

```python
class AnnotationProtocol:
    """Binary presence annotation protocol for DTS sections"""

    def __init__(self, config: dict):
        """Initialize with DTS section definitions."""
        self.dts_sections = config.get("dts_sections", [
            "Dataset_Description", "Task_Description", "Source_Attribution",
            "Data_Collection_Method", "Known_Limitations", "Ethical_Considerations"
        ])

    def generate_annotation_template(self, metadata_df: pd.DataFrame, output_path: Path) -> None:
        """Create annotation CSV. Schema: [30, 7] - dataset_id + 6 DTS columns (binary 0/1)"""
        ...

    def load_annotations(self, coder_a_path: Path, coder_b_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load two coder annotations. Returns: ([30, 7], [30, 7])"""
        ...

    def validate_annotations(self, df_a: pd.DataFrame, df_b: pd.DataFrame) -> dict:
        """Check completeness and format. Returns: {valid: bool, errors: List[str]}"""
        ...

    def align_annotations(self, df_a: pd.DataFrame, df_b: pd.DataFrame) -> pd.DataFrame:
        """Merge coder A/B annotations by dataset_id. Returns: [30, 13] - id + 6 cols × 2 coders"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| template | [30, 7] | dataset_id + 6 DTS sections |
| coder_a | [30, 7] | Coder A annotations |
| coder_b | [30, 7] | Coder B annotations |
| aligned | [30, 13] | id + 6 sections × 2 coders |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | CSV workflow + validation | Template generation, validation, and alignment logic |

---

## E1-4: Cohen's Kappa Calculator [Complexity: 11, Budget: 2]

**Applied**: Statistical analysis with scipy.stats bootstrap

### API Signatures

```python
from scipy import stats
import numpy as np

class KappaCalculator:
    """Cohen's kappa with bootstrap confidence intervals"""

    def __init__(self, config: dict):
        """Initialize with bootstrap configuration."""
        self.n_bootstrap = config.get("bootstrap_iterations", 1000)
        self.confidence_level = config.get("confidence_level", 0.95)
        self.random_seed = config.get("random_seed", 42)

    def compute_cohens_kappa(self, coder_a: np.ndarray, coder_b: np.ndarray) -> float:
        """Compute Cohen's kappa. coder_a, coder_b: [n] binary arrays. Returns: κ ∈ [-1, 1]"""
        ...

    def bootstrap_confidence_interval(
        self,
        coder_a: np.ndarray,
        coder_b: np.ndarray
    ) -> tuple[float, float]:
        """Bootstrap 95% CI. Returns: (ci_lower, ci_upper)"""
        ...

    def compute_percent_agreement(self, coder_a: np.ndarray, coder_b: np.ndarray) -> float:
        """Percent agreement = (# agree) / n. Returns: float ∈ [0, 1]"""
        ...

    def interpret_kappa(self, kappa: float) -> str:
        """Landis-Koch interpretation. Returns: 'Substantial' | 'Almost Perfect' | ..."""
        ...

    def compute_all_sections(self, aligned_df: pd.DataFrame) -> pd.DataFrame:
        """Compute κ for all 6 DTS sections. Returns: [6, 6] - section, κ, ci_lower, ci_upper, interpretation, pct_agree"""
        ...
```

### Pseudo-code

```
1. For each section:
   a. Extract coder_a[:, section_idx] and coder_b[:, section_idx]  # [30] arrays
   b. Compute Cohen's kappa:
      - observed_agreement = mean(coder_a == coder_b)
      - p_a = mean(coder_a)  # Marginal probability
      - p_b = mean(coder_b)
      - expected_agreement = p_a * p_b + (1 - p_a) * (1 - p_b)
      - kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)
   c. Bootstrap CI:
      - For i in 1..1000:
          - Resample 30 indices with replacement
          - Compute kappa on resampled data
          - Store kappa_i
      - ci_lower = percentile(kappas, 2.5)
      - ci_upper = percentile(kappas, 97.5)
   d. Interpret using Landis-Koch thresholds
2. Return results as DataFrame
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Bootstrap CI | Implement bootstrap_confidence_interval() |
| C-4-1 | Landis-Koch thresholds | Configure interpretation ranges |

---

## E1-5: Gate Validation Logic [Complexity: 7, Budget: 1]

**Applied**: Threshold checking pattern

### API Signatures

```python
class GateValidator:
    """MUST_WORK gate validation for kappa thresholds"""

    def __init__(self, config: dict):
        """Initialize with gate thresholds."""
        self.kappa_threshold = config.get("kappa_min", 0.60)
        self.sections_min = config.get("sections_min", 5)

    def check_section_pass(self, kappa: float, ci_lower: float) -> bool:
        """Check if section passes. Returns: κ ≥ 0.60"""
        ...

    def evaluate_gate(self, kappa_results_df: pd.DataFrame) -> dict:
        """
        Evaluate MUST_WORK gate.
        Returns: {
            gate_passed: bool,
            sections_passing: int,
            sections_total: int,
            failing_sections: List[str]
        }
        """
        ...

    def format_gate_report(self, gate_result: dict, kappa_results_df: pd.DataFrame) -> str:
        """Generate human-readable gate report with PASS/FAIL status"""
        ...

    def compute_overall_kappa(self, kappa_results_df: pd.DataFrame) -> float:
        """Compute mean kappa across all sections. Returns: mean(κ)"""
        ...
```

### Pseudo-code

```
1. For each section in kappa_results_df:
   - Check if kappa >= 0.60
   - Count passing sections
2. Gate passes if sections_passing >= 5
3. Format report:
   - "✅ MUST_WORK gate PASSED (5/6 sections)" OR
   - "❌ MUST_WORK gate FAILED (3/6 sections)"
   - List failing sections with kappa values
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Gate evaluation + reporting | Implement threshold checking, gate evaluation, and report formatting |

---

## E1-6: Visualization Suite [Complexity: 10, Budget: 2]

**Applied**: Matplotlib/seaborn visualization pattern

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class Visualizer:
    """Generate 4 required figures for validation report"""

    def __init__(self, config: dict):
        """Initialize with figure styling configuration."""
        self.figures_dir = Path(config.get("figures_dir", "h-e1/figures"))
        self.dpi = config.get("dpi", 300)

    def plot_gate_metrics(self, kappa_results_df: pd.DataFrame, output_path: Path) -> None:
        """
        Figure 1: Bar chart of κ per section with threshold line.
        - x-axis: 6 DTS sections
        - y-axis: Cohen's kappa [-1, 1]
        - Red dashed line at κ = 0.60
        - Error bars: 95% CI
        """
        ...

    def plot_confusion_matrices(
        self,
        aligned_df: pd.DataFrame,
        output_path: Path
    ) -> None:
        """
        Figure 2: 6 confusion matrices in 2×3 grid.
        - Each subplot: 2×2 confusion matrix (agree/disagree)
        - Colormap: Blues
        - Annotations: counts
        """
        ...

    def plot_agreement_heatmap(self, aligned_df: pd.DataFrame, output_path: Path) -> None:
        """
        Figure 3: 30×6 heatmap of agreement.
        - Rows: 30 datasets
        - Columns: 6 DTS sections
        - Cell color: Green (agree), Red (disagree)
        """
        ...

    def plot_baserate_vs_kappa(self, kappa_results_df: pd.DataFrame, output_path: Path) -> None:
        """
        Figure 4: Scatter plot of base rate vs kappa.
        - x-axis: Base rate (mean presence across coders)
        - y-axis: Cohen's kappa
        - Trendline: linear regression
        """
        ...

    def generate_all_figures(
        self,
        kappa_results_df: pd.DataFrame,
        aligned_df: pd.DataFrame
    ) -> None:
        """Generate all 4 figures and save to figures_dir"""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure styling | Configure layout, colors, DPI for 4 figures |
| C-6-2 | Output paths | Configure figures_dir and filenames |

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count = 7 (within budget)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Applied patterns noted per task
- [x] EXISTENCE hypothesis → minimal pseudo-code (only for kappa computation)

---

*Generated for Phase 4 Implementation*
*Next: Configuration agent (03_config.md)*
