# Logic Design: h-e1 - DTS Inter-Annotator Agreement Study

**Date:** 2026-03-18
**Hypothesis Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK (κ ≥ 0.60 in ≥5/6 DTS sections)
**Total Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** Green-field implementation
**Status:** New DTS annotation study - no existing code to reuse
**Analyzed Path:** N/A (existing h-e1 code is unrelated MDS-12 psychometric validation)
**Relevant Symbols:** None - fresh implementation required

**Rationale:** Previous h-e1 implementation focused on MDS-12 factor analysis. Current hypothesis measures Cohen's kappa for DTS binary annotations - completely different statistical methodology and data requirements.

---

## Applied Patterns

**Applied:** Python Google Style Guide (docstrings, type hints)
**Applied:** HuggingFace Datasets API (programmatic collection)
**Applied:** Sklearn statistical patterns (Cohen's kappa, bootstrap CI)
**Applied:** CSV-based annotation workflow (pandas DataFrame operations)

---

## E1-1: Dataset Collection Pipeline [Complexity: 12, Budget: 1 subtask]

**Applied:** HuggingFace datasets library, OpenML API, BeautifulSoup web scraping

### API Signatures

```python
from typing import List, Dict, Optional
import pandas as pd

class DataCollector:
    """Collects datasets from three repositories with stratified sampling."""

    def __init__(self, n_per_repo: int = 10, random_seed: int = 42):
        """Initialize collector.

        Args:
            n_per_repo: Number of datasets per repository
            random_seed: For reproducible stratified sampling
        """
        self.n_per_repo = n_per_repo
        self.random_seed = random_seed

    def collect_huggingface_datasets(self) -> List[Dict]:
        """Collect datasets from HuggingFace Hub.

        Returns:
            List of dicts with keys: id, name, repo, url, description
        """
        ...

    def collect_openml_datasets(self) -> List[Dict]:
        """Collect datasets from OpenML API.

        Returns:
            List of dicts with keys: id, name, repo, url, description
        """
        ...

    def collect_uci_datasets(self) -> List[Dict]:
        """Collect datasets from UCI ML Repository.

        Returns:
            List of dicts with keys: id, name, repo, url, description
        """
        ...

    def stratify_by_quality(
        self,
        datasets: List[Dict],
        target_counts: Dict[str, int] = {"high": 10, "medium": 10, "low": 10}
    ) -> List[Dict]:
        """Stratify datasets by preliminary DTS quality scoring.

        Args:
            datasets: List of collected datasets
            target_counts: Desired counts per quality stratum

        Returns:
            Stratified subset of 30 datasets with quality_stratum field added
        """
        ...

    def extract_documentation(self, dataset: Dict) -> str:
        """Extract full documentation text from dataset metadata.

        Args:
            dataset: Dataset dict with url and repo fields

        Returns:
            Plain text documentation string
        """
        ...

    def save_metadata(self, datasets: List[Dict], path: str) -> None:
        """Save datasets metadata to CSV.

        Args:
            datasets: List of dataset dicts
            path: Output CSV path (e.g., data/h-e1/datasets_metadata.csv)
        """
        ...

    def save_documentation_files(
        self,
        datasets: List[Dict],
        output_dir: str
    ) -> None:
        """Save 30 plain text documentation files.

        Args:
            datasets: List of dataset dicts with id and description
            output_dir: Output directory (e.g., data/h-e1/documentation/)
        """
        ...
```

### Pseudo-code

```
1. HuggingFace Collection:
   - Use datasets.list_datasets() API
   - Filter: has dataset card + published 2020-2024
   - Sample randomly with seed=42
   - Extract dataset card markdown

2. OpenML Collection:
   - Use openml.datasets.list_datasets()
   - Filter: active=True, status='active'
   - Extract description from metadata
   - Download via API

3. UCI Collection:
   - Scrape https://archive.ics.uci.edu/ml/datasets.php
   - Parse HTML table with BeautifulSoup
   - Extract dataset description from detail pages
   - Fallback: use known dataset list if scraping fails

4. Stratification:
   - Score each dataset on 6 DTS sections (0-6 scale)
   - Bin: high (5-6), medium (3-4), low (0-2)
   - Randomly sample 10 per stratum per repository
   - Total: 30 datasets (10 per repo × balanced quality)

5. Save outputs:
   - datasets_metadata.csv: 30 rows with id, name, repo, quality_stratum
   - documentation/*.txt: 30 plain text files (one per dataset)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Multi-repo collection | HF + OpenML + UCI API integration with stratification |

---

## E1-3: Annotation Protocol Implementation [Complexity: 9, Budget: 1 subtask]

**Applied:** CSV-based workflow with pandas DataFrame validation

### API Signatures

```python
import pandas as pd
from typing import List, Tuple

class AnnotationProtocol:
    """Binary presence judgment protocol for DTS sections."""

    def __init__(self, dts_sections: List[str]):
        """Initialize protocol.

        Args:
            dts_sections: 6 DTS section names
                ["Motivation", "Composition", "Collection",
                 "Preprocessing", "Uses", "Maintenance"]
        """
        self.dts_sections = dts_sections

    def load_documentation(self, dataset_id: str, doc_dir: str) -> str:
        """Load documentation text for annotation.

        Args:
            dataset_id: Dataset identifier (e.g., "hf_001")
            doc_dir: Documentation directory path

        Returns:
            Plain text documentation content
        """
        ...

    def judge_section_presence(self, doc_text: str, section: str) -> int:
        """Binary judgment of section presence.

        Args:
            doc_text: Full documentation text
            section: DTS section name

        Returns:
            1 if section present, 0 if absent

        Note: Human annotator implements this logic manually.
        """
        ...

    def generate_annotation_template(
        self,
        datasets: List[str],
        output_path: str
    ) -> None:
        """Generate empty CSV template for annotators.

        Args:
            datasets: List of dataset IDs
            output_path: Path to save template CSV

        Creates:
            CSV with columns: dataset_id, Motivation, Composition,
                             Collection, Preprocessing, Uses, Maintenance
            Rows: 30 (one per dataset)
        """
        ...

    def load_annotations(
        self,
        coder_a_path: str,
        coder_b_path: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load completed annotation CSVs.

        Args:
            coder_a_path: Path to Coder A annotations
            coder_b_path: Path to Coder B annotations

        Returns:
            (coder_a_df, coder_b_df): Both shape [30, 7]
                (dataset_id + 6 DTS sections)
        """
        ...

    def validate_annotations(
        self,
        coder_a: pd.DataFrame,
        coder_b: pd.DataFrame
    ) -> bool:
        """Validate annotation data quality.

        Args:
            coder_a: Coder A annotations
            coder_b: Coder B annotations

        Returns:
            True if valid, raises ValueError otherwise

        Checks:
            - Same 30 dataset IDs
            - No missing values
            - All values binary (0 or 1)
            - Same column structure
        """
        ...
```

### Pseudo-code

```
1. Generate annotation template:
   - Create CSV with 30 rows (dataset IDs)
   - Columns: dataset_id + 6 DTS sections
   - Initialize all cells as empty

2. Human annotation process (NOT automated):
   - Coder A: Read doc, judge binary presence per section
   - Coder B: Same (blind - no communication)
   - Time limit: 5-10 minutes per dataset
   - Save to coder_a_annotations.csv, coder_b_annotations.csv

3. Validation:
   - Check row count = 30
   - Check no NaN values
   - Check all values in {0, 1}
   - Check same dataset IDs in same order
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | CSV workflow | Template generation + validation logic |

---

## E1-4: Cohen's Kappa Calculator [Complexity: 11, Budget: 1 subtask]

**Applied:** sklearn.metrics.cohen_kappa_score + scipy.stats.bootstrap

### API Signatures

```python
import numpy as np
from typing import Tuple, Dict, List
from sklearn.metrics import cohen_kappa_score
from scipy.stats import bootstrap

class KappaCalculator:
    """Cohen's kappa with bootstrap confidence intervals."""

    def __init__(self, n_bootstrap: int = 1000, random_state: int = 42):
        """Initialize calculator.

        Args:
            n_bootstrap: Bootstrap resamples for CI estimation
            random_state: For reproducible bootstrap
        """
        self.n_bootstrap = n_bootstrap
        self.random_state = random_state

    def compute_cohen_kappa(
        self,
        coder_a: np.ndarray,
        coder_b: np.ndarray
    ) -> float:
        """Compute Cohen's kappa.

        Args:
            coder_a: Binary annotations [N]
            coder_b: Binary annotations [N]

        Returns:
            Cohen's kappa value
        """
        ...

    def bootstrap_confidence_interval(
        self,
        coder_a: np.ndarray,
        coder_b: np.ndarray,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Bootstrap 95% CI for kappa.

        Args:
            coder_a: Binary annotations [N]
            coder_b: Binary annotations [N]
            confidence_level: CI level (default 0.95)

        Returns:
            (ci_lower, ci_upper): 95% confidence interval bounds
        """
        ...

    def compute_percent_agreement(
        self,
        coder_a: np.ndarray,
        coder_b: np.ndarray
    ) -> float:
        """Compute percent agreement (p_o).

        Args:
            coder_a: Binary annotations [N]
            coder_b: Binary annotations [N]

        Returns:
            Proportion of exact matches (0.0 to 1.0)
        """
        ...

    def compute_positive_agreement(
        self,
        coder_a: np.ndarray,
        coder_b: np.ndarray
    ) -> float:
        """Compute positive-specific agreement.

        Args:
            coder_a: Binary annotations [N]
            coder_b: Binary annotations [N]

        Returns:
            Agreement proportion for positive cases (both = 1)
        """
        ...

    def compute_negative_agreement(
        self,
        coder_a: np.ndarray,
        coder_b: np.ndarray
    ) -> float:
        """Compute negative-specific agreement.

        Args:
            coder_a: Binary annotations [N]
            coder_b: Binary annotations [N]

        Returns:
            Agreement proportion for negative cases (both = 0)
        """
        ...

    def interpret_kappa(self, kappa: float) -> str:
        """Landis-Koch interpretation.

        Args:
            kappa: Cohen's kappa value

        Returns:
            Interpretation string:
                < 0.00: "Poor"
                0.00-0.20: "Slight"
                0.21-0.40: "Fair"
                0.41-0.60: "Moderate"
                0.61-0.80: "Substantial"
                0.81-1.00: "Almost Perfect"
        """
        ...

    def analyze_all_sections(
        self,
        coder_a: pd.DataFrame,
        coder_b: pd.DataFrame,
        sections: List[str]
    ) -> Dict[str, Dict]:
        """Analyze kappa for all 6 DTS sections.

        Args:
            coder_a: Coder A annotations [30, 7]
            coder_b: Coder B annotations [30, 7]
            sections: 6 DTS section names

        Returns:
            {
                "Motivation": {
                    "kappa": 0.72,
                    "ci_95": (0.65, 0.79),
                    "percent_agreement": 0.87,
                    "interpretation": "Substantial"
                },
                ...
            }
        """
        ...
```

### Pseudo-code

```
1. Cohen's kappa computation (sklearn):
   - kappa = cohen_kappa_score(coder_a, coder_b)
   - Formula: κ = (p_o - p_e) / (1 - p_e)
     where p_o = observed agreement, p_e = expected by chance

2. Bootstrap CI (scipy):
   - Define kappa_stat function for bootstrap
   - rng = np.random.default_rng(seed=42)
   - res = bootstrap((coder_a, coder_b), kappa_stat,
                      n_resamples=1000, random_state=rng,
                      method='percentile', confidence_level=0.95)
   - Extract CI: (res.confidence_interval.low, res.confidence_interval.high)

3. Percent agreement:
   - p_o = np.mean(coder_a == coder_b)

4. Positive agreement:
   - both_positive = (coder_a == 1) & (coder_b == 1)
   - either_positive = (coder_a == 1) | (coder_b == 1)
   - pos_agreement = both_positive.sum() / either_positive.sum()

5. Analyze all sections:
   - Iterate over 6 DTS section columns
   - Compute kappa + CI + agreement metrics per section
   - Return dict with all metrics
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Kappa computation | sklearn + scipy bootstrap CI implementation |

---

## E1-5: Gate Validation Logic [Complexity: 7, Budget: 1 subtask]

**Applied:** Simple threshold checking with formatted reporting

### API Signatures

```python
from typing import Dict

class GateValidator:
    """MUST_WORK gate validation for hypothesis success/failure."""

    def __init__(self, kappa_threshold: float = 0.60, min_sections: int = 5):
        """Initialize validator.

        Args:
            kappa_threshold: Minimum kappa for section pass (0.60)
            min_sections: Minimum passing sections (5 out of 6)
        """
        self.kappa_threshold = kappa_threshold
        self.min_sections = min_sections

    def check_section_pass(self, kappa: float) -> bool:
        """Check if section passes gate.

        Args:
            kappa: Section Cohen's kappa value

        Returns:
            True if kappa >= threshold, False otherwise
        """
        ...

    def evaluate_gate(self, section_results: Dict) -> Dict:
        """Evaluate MUST_WORK gate.

        Args:
            section_results: Dict from KappaCalculator.analyze_all_sections()
                {
                    "Motivation": {"kappa": 0.72, ...},
                    "Composition": {"kappa": 0.68, ...},
                    ...
                }

        Returns:
            {
                "gate_passed": bool,
                "sections_passing": int,
                "sections_failing": int,
                "failing_sections": List[str],
                "margin": float  # sections_passing - min_sections
            }
        """
        ...

    def format_gate_report(self, gate_results: Dict) -> str:
        """Format human-readable gate report.

        Args:
            gate_results: Output from evaluate_gate()

        Returns:
            Multi-line report string with:
                - "✅ MUST_WORK gate PASSED" or "❌ MUST_WORK gate FAILED"
                - Section-by-section pass/fail status
                - Summary statistics
        """
        ...
```

### Pseudo-code

```
1. Evaluate gate:
   - sections_passing = sum(1 for s in results.values() if s["kappa"] >= 0.60)
   - gate_passed = sections_passing >= 5
   - failing_sections = [name for name, s in results.items() if s["kappa"] < 0.60]

2. Format report:
   - Print header: "✅ PASSED" or "❌ FAILED"
   - List each section: "Motivation: κ=0.72 ✅"
   - Summary: "5/6 sections passed (threshold: ≥5)"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Gate logic | Threshold checking + report formatting |

---

## E1-6: Visualization Suite [Complexity: 10, Budget: 0 subtasks]

**Note:** Complexity 10 does not warrant subtask allocation (budget constraint).

**Applied:** matplotlib + seaborn plotting patterns

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List

class Visualizer:
    """Generate 4 figures for validation report."""

    def __init__(self, output_dir: str):
        """Initialize visualizer.

        Args:
            output_dir: Directory to save figures (e.g., h-e1/figures/)
        """
        self.output_dir = output_dir

    def plot_gate_metrics(
        self,
        section_results: Dict,
        threshold: float = 0.60
    ) -> None:
        """Plot kappa values per section with gate threshold.

        Args:
            section_results: Dict from KappaCalculator.analyze_all_sections()
            threshold: Gate threshold (red dashed line at 0.60)

        Saves:
            gate_metrics.png: Bar chart with error bars (95% CI)
        """
        ...

    def plot_confusion_matrices(
        self,
        coder_a: pd.DataFrame,
        coder_b: pd.DataFrame,
        sections: List[str]
    ) -> None:
        """Plot 6 confusion matrices (2×3 grid).

        Args:
            coder_a: Coder A annotations [30, 7]
            coder_b: Coder B annotations [30, 7]
            sections: 6 DTS section names

        Saves:
            confusion_matrices.png: 2×3 subplot grid
        """
        ...

    def plot_agreement_heatmap(
        self,
        coder_a: pd.DataFrame,
        coder_b: pd.DataFrame,
        sections: List[str]
    ) -> None:
        """Plot agreement heatmap (30 datasets × 6 sections).

        Args:
            coder_a: Coder A annotations [30, 7]
            coder_b: Coder B annotations [30, 7]
            sections: 6 DTS section names

        Saves:
            agreement_heatmap.png:
                - Green: both agree presence (1,1)
                - Red: both agree absence (0,0)
                - Yellow: disagreement (0,1) or (1,0)
        """
        ...

    def plot_baserate_vs_kappa(self, section_results: Dict) -> None:
        """Plot section base rate vs. kappa scatter.

        Args:
            section_results: Dict from KappaCalculator.analyze_all_sections()

        Saves:
            baserate_vs_kappa.png: Scatter plot with trend line
        """
        ...

    def save_all_figures(
        self,
        coder_a: pd.DataFrame,
        coder_b: pd.DataFrame,
        section_results: Dict
    ) -> None:
        """Generate and save all 4 figures.

        Args:
            coder_a: Coder A annotations [30, 7]
            coder_b: Coder B annotations [30, 7]
            section_results: Dict from KappaCalculator.analyze_all_sections()
        """
        ...
```

---

## E1-2: Documentation Extraction [Complexity: 8, Budget: 0 subtasks]

**Note:** Covered by DataCollector.extract_documentation() and save_documentation_files() APIs above. No separate module needed.

---

## Main Orchestration Flow

### API Signatures

```python
from pathlib import Path
import json
from typing import Dict

def load_configuration() -> Dict:
    """Load configuration from config.py.

    Returns:
        Config dict with repositories, sections, thresholds, paths
    """
    ...

def run_data_collection(config: Dict) -> List[Dict]:
    """Execute dataset collection pipeline.

    Args:
        config: Configuration dict

    Returns:
        List of 30 collected datasets

    Side effects:
        - Saves datasets_metadata.csv
        - Saves 30 documentation/*.txt files
    """
    ...

def prepare_annotation_materials(datasets: List[Dict], config: Dict) -> None:
    """Generate annotation templates for human coders.

    Args:
        datasets: List of collected datasets
        config: Configuration dict

    Side effects:
        - Saves annotation_template.csv
        - Saves annotation_protocol.md (instructions)
    """
    ...

def compute_interrater_reliability(
    coder_a_path: str,
    coder_b_path: str,
    config: Dict
) -> Dict:
    """Compute Cohen's kappa for all sections.

    Args:
        coder_a_path: Path to Coder A annotations CSV
        coder_b_path: Path to Coder B annotations CSV
        config: Configuration dict

    Returns:
        Section-level results dict from KappaCalculator.analyze_all_sections()
    """
    ...

def validate_gate(section_results: Dict, config: Dict) -> Dict:
    """Validate MUST_WORK gate.

    Args:
        section_results: Kappa results per section
        config: Configuration dict

    Returns:
        Gate evaluation results from GateValidator.evaluate_gate()
    """
    ...

def generate_visualizations(
    coder_a: pd.DataFrame,
    coder_b: pd.DataFrame,
    section_results: Dict,
    config: Dict
) -> None:
    """Generate 4 figures.

    Args:
        coder_a: Coder A annotations
        coder_b: Coder B annotations
        section_results: Kappa results
        config: Configuration dict

    Side effects:
        - Saves 4 PNG files to h-e1/figures/
    """
    ...

def save_results(results: Dict, config: Dict) -> None:
    """Save validation results to JSON.

    Args:
        results: Combined dict with section_results + gate_results
        config: Configuration dict

    Side effects:
        - Saves h-e1/results/validation_results.json
    """
    ...

def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 if gate passed, 1 if failed

    Execution flow:
        1. Load configuration
        2. Run data collection (if not already done)
        3. Prepare annotation materials
        4. [MANUAL] Human annotation phase (10-12 hours)
        5. Load completed annotations
        6. Compute inter-rater reliability
        7. Validate gate
        8. Generate visualizations
        9. Save results
        10. Print gate status
    """
    ...
```

### Execution Flow

```
Phase 1: Data Collection (Automated)
├─ DataCollector.collect_huggingface_datasets()
├─ DataCollector.collect_openml_datasets()
├─ DataCollector.collect_uci_datasets()
├─ DataCollector.stratify_by_quality()
└─ Save: datasets_metadata.csv + 30 documentation/*.txt

Phase 2: Annotation Preparation (Automated)
├─ AnnotationProtocol.generate_annotation_template()
└─ Save: annotation_template.csv + annotation_protocol.md

Phase 3: Human Annotation (MANUAL - 10-12 hours)
├─ Coder A: Reads docs, fills coder_a_annotations.csv
├─ Coder B: Reads docs, fills coder_b_annotations.csv (blind)
└─ Both: Follow annotation_protocol.md

Phase 4: Statistical Analysis (Automated)
├─ AnnotationProtocol.load_annotations()
├─ AnnotationProtocol.validate_annotations()
├─ KappaCalculator.analyze_all_sections()
└─ Compute κ + 95% CI for 6 sections

Phase 5: Gate Validation (Automated)
├─ GateValidator.evaluate_gate()
├─ GateValidator.format_gate_report()
└─ Print: "✅ PASSED" or "❌ FAILED"

Phase 6: Visualization (Automated)
├─ Visualizer.save_all_figures()
└─ Save: 4 PNG files

Phase 7: Results Export (Automated)
└─ Save: validation_results.json
```

---

## Subtask Budget Summary

| Task ID | Task Name | Complexity | Subtasks Allocated | Subtasks Used |
|---------|-----------|------------|-------------------|---------------|
| E1-1 | Dataset Collection Pipeline | 12 | 1 | 1 |
| E1-2 | Documentation Extraction | 8 | 0 | 0 |
| E1-3 | Annotation Protocol | 9 | 1 | 1 |
| E1-4 | Cohen's Kappa Calculator | 11 | 1 | 1 |
| E1-5 | Gate Validation Logic | 7 | 1 | 1 |
| E1-6 | Visualization Suite | 10 | 0 | 0 |
| **TOTAL** | | **57** | **4** | **4** |

**Budget Status:** 4/4 subtasks used (100% utilization)

---

## Implementation Notes for Phase 4 Coder

### Critical Dependencies

```python
# requirements.txt
datasets>=2.10.0      # HuggingFace Hub API
openml>=0.14.0        # OpenML Python client
beautifulsoup4>=4.11.0  # UCI web scraping
requests>=2.28.0      # HTTP requests
scikit-learn>=1.2.0   # cohen_kappa_score
scipy>=1.10.0         # bootstrap CI
numpy>=1.24.0         # Array operations
matplotlib>=3.7.0     # Plotting
seaborn>=0.12.0       # Advanced visualizations
pandas>=1.5.0         # DataFrame operations
```

### Random Seed Management

**Critical:** All random operations must use `random_state=42` for reproducibility:
- Dataset stratified sampling: `random.seed(42)`
- Bootstrap CI: `np.random.default_rng(seed=42)`
- Repository sampling: Set seed before each collection API call

### Human Annotation Phase

**NOT automated!** Phase 4 implementation must:
1. Generate annotation template CSV
2. Save annotation protocol instructions to markdown
3. **STOP** and wait for manual annotation
4. Resume after annotation CSVs are manually created

**Annotation protocol instructions (for humans):**
- Study Gebru et al. (2021) DTS framework (1 hour)
- Complete calibration on 5 Rondina et al. (2025) datasets
- Require 100% agreement on calibration before proceeding
- Blind annotation: No communication between coders
- Time limit: 5-10 minutes per dataset
- Break protocol: 10-minute break every hour

### Error Handling

**API rate limits:**
- Add 1-second delay between HuggingFace API calls
- Add 1-second delay between OpenML API calls
- Retry up to 3 times on API failures

**UCI scraping failures:**
- Fallback to manual dataset list if web scraping fails
- Log failures with dataset URL

**Annotation validation:**
- Raise ValueError if row count ≠ 30
- Raise ValueError if any NaN values
- Raise ValueError if any non-binary values

### Gate Success/Failure Handling

```python
if gate_results["gate_passed"]:
    print("✅ MUST_WORK gate PASSED")
    print(f"   {gate_results['sections_passing']}/6 sections ≥ κ=0.60")
    return 0  # Success exit code
else:
    print("❌ MUST_WORK gate FAILED - ABANDON hypothesis")
    print(f"   Only {gate_results['sections_passing']}/6 sections passed")
    print(f"   Failing sections: {gate_results['failing_sections']}")
    return 1  # Failure exit code
```

### File Output Checklist

**Phase 4 must produce:**
- [ ] `data/h-e1/datasets_metadata.csv` (30 rows)
- [ ] `data/h-e1/documentation/*.txt` (30 files)
- [ ] `data/h-e1/annotations/annotation_template.csv`
- [ ] `data/h-e1/annotations/annotation_protocol.md`
- [ ] `h-e1/figures/gate_metrics.png`
- [ ] `h-e1/figures/confusion_matrices.png`
- [ ] `h-e1/figures/agreement_heatmap.png`
- [ ] `h-e1/figures/baserate_vs_kappa.png`
- [ ] `h-e1/results/validation_results.json`

**Note:** `coder_a_annotations.csv` and `coder_b_annotations.csv` are created manually by human annotators (not by Phase 4 code).

---

**Logic Design Completed:** 2026-03-18
**Next Phase:** Phase 4 - Implementation
**Total Lines:** 590 (within 500-600 target)
