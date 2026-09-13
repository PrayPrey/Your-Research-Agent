# System Architecture: h-e1
# API Contract Validation Framework

**Date:** 2026-07-11  
**Hypothesis:** h-e1 (EXISTENCE)  
**Type:** PoC - Research Tool Validation  
**Applied Patterns:** Research module pattern, validation framework structure

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing codebase to analyze. This is a foundation hypothesis implementing a novel API contract validation framework for ML library defects.

---

## Architecture Overview

This is an EXISTENCE (PoC) hypothesis testing contractability of API defects. Architecture prioritizes:
- Minimal file structure (6 modules total)
- Single-pass retrospective analysis (no training loops)
- Research-focused organization (defect corpus → contracts → metrics → visualization)

**Core Flow:** Load defects → Generate contracts → Validate with timeout → Calculate metrics → Visualize results

---

## Module Structure

### 1. DefectCorpusLoader (`data/corpus_loader.py`)

**Dependencies:** pandas, requests

```python
class DefectCorpusLoader:
    def __init__(self, repo_url: str = "https://github.com/wenxin-jiang/emse-cvreengineering-artifact"):
        """Load and filter Jiang et al. 348-defect corpus"""
        ...
    
    def load_corpus(self) -> pd.DataFrame:
        """Returns: DataFrame with columns [defect_id, type, description, source_project, api_name]"""
        ...
    
    def filter_environment_api_defects(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter for environment-stage API defects only"""
        ...
    
    def categorize_defects(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize by type: structural | metamorphic | composition"""
        ...
```

---

### 2. ContractGenerator (`contracts/generator.py`)

**Dependencies:** DefectCorpusLoader, torch

```python
from abc import ABC, abstractmethod

class Contract(ABC):
    def __init__(self, defect_id: str, invariant_type: str):
        self.defect_id = defect_id
        self.invariant_type = invariant_type
        self.execution_time = None
        self.description = ""
    
    @abstractmethod
    def validate(self, timeout: int = 10) -> bool:
        """Execute contract with timeout enforcement"""
        ...

class StructuralContract(Contract):
    """Tensor shapes, dtypes, device placement"""
    def __init__(self, defect_id: str, shape_constraint: str, dtype: str, device: str):
        ...
    
    def validate(self, timeout: int = 10) -> bool:
        """Returns: True if contract expressible and passes, False otherwise"""
        ...

class MetamorphicContract(Contract):
    """Autocast mode, training/eval state transitions"""
    def __init__(self, defect_id: str, state_property: str, expected_behavior: str):
        ...
    
    def validate(self, timeout: int = 10) -> bool:
        ...

class CompositionContract(Contract):
    """Cross-library device consistency (PyTorch + CUDA, PyTorch + NumPy)"""
    def __init__(self, defect_id: str, library1: str, library2: str, consistency_rule: str):
        ...
    
    def validate(self, timeout: int = 10) -> bool:
        ...

class ContractGenerator:
    def generate_from_defect(self, defect: pd.Series) -> Contract | None:
        """
        Args: defect - Single row from corpus with type, description, api_name
        Returns: Contract object or None if not expressible
        """
        ...
    
    def parse_invariant(self, description: str, defect_type: str) -> dict:
        """Extract invariant parameters from defect description"""
        ...
```

---

### 3. ContractValidator (`contracts/validator.py`)

**Dependencies:** ContractGenerator, signal (timeout enforcement)

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class ValidationResult:
    defect_id: str
    status: Literal["PASS", "FAIL", "TIMEOUT", "NOT_EXPRESSIBLE"]
    execution_time: float
    error_message: str = ""

class ContractValidator:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def validate_contract(self, contract: Contract) -> ValidationResult:
        """Execute single contract with timeout enforcement using signal.alarm()"""
        ...
    
    def batch_validate(self, contracts: list[Contract]) -> list[ValidationResult]:
        """Execute all contracts and collect results"""
        ...
    
    def check_version_stability(self, contract: Contract, versions: list[str]) -> dict:
        """
        Test contract across PyTorch versions (e.g., ["1.11", "1.12", "1.13"])
        Returns: {version: bool} stability matrix
        """
        ...
```

---

### 4. RetrospectiveCoder (`analysis/retrospective_coder.py`)

**Dependencies:** ContractValidator, sklearn.metrics, scipy.stats

```python
class RetrospectiveCoder:
    def __init__(self, defects: pd.DataFrame, random_seed: int = 42):
        """Apply 2-coder independent coding with 3-question filter"""
        self.defects = defects.sample(frac=1, random_state=random_seed)  # Randomize presentation
        self.random_seed = random_seed
    
    def apply_3q_filter(self, defect: pd.Series, contract: Contract) -> bool:
        """
        Returns: True if contractable (passes all 3 questions)
        Q1: Documented invariant exists? (check contract.description)
        Q2: Evaluable in ≤10s? (check execution_time)
        Q3: Version-stable ±2 releases? (run cross-version check)
        """
        ...
    
    def code_corpus(self, validator: ContractValidator) -> tuple[list[bool], list[bool]]:
        """
        Returns: (coder1_labels, coder2_labels) - binary arrays
        Simulates 2 independent coders applying 3Q filter
        """
        ...
    
    def calculate_kappa(self, coder1: list[bool], coder2: list[bool]) -> float:
        """Returns: Cohen's kappa coefficient using sklearn.metrics.cohen_kappa_score"""
        ...
    
    def get_disagreements(self, coder1: list[bool], coder2: list[bool]) -> pd.DataFrame:
        """Returns: Subset of defects where coders disagreed"""
        ...
```

---

### 5. MetricsCalculator (`analysis/metrics.py`)

**Dependencies:** RetrospectiveCoder, scipy.stats

```python
from dataclasses import dataclass

@dataclass
class ContractabilityMetrics:
    overall_rate: float
    structural_rate: float
    metamorphic_rate: float
    composition_rate: float
    ci_lower: float
    ci_upper: float
    kappa: float
    gate_status: Literal["PASS", "FAIL"]

class MetricsCalculator:
    def calculate_contractability_rate(
        self, 
        coder1: list[bool], 
        coder2: list[bool], 
        defect_types: list[str]
    ) -> ContractabilityMetrics:
        """
        Calculate overall + stratified rates with 95% CI
        Uses Wilson score method via scipy.stats.proportion_confint
        """
        ...
    
    def compute_confidence_interval(self, successes: int, total: int) -> tuple[float, float]:
        """Returns: (ci_lower, ci_upper) using Wilson score method"""
        ...
    
    def evaluate_gate_condition(self, metrics: ContractabilityMetrics) -> bool:
        """Returns: True if contractability_rate >= 40% AND kappa >= 0.7"""
        ...
    
    def compare_to_baselines(self, contractability_rate: float) -> dict:
        """
        Returns: {
            "no_ci_baseline": 0.0,
            "ci_only_baseline": 0.175,  # 15-20% from Wolter et al.
            "proposed": contractability_rate,
            "improvement_over_ci": (contractability_rate - 0.175) / 0.175 * 100
        }
        """
        ...
```

---

### 6. Visualizer (`visualization/plots.py`)

**Dependencies:** MetricsCalculator, matplotlib, pandas

```python
class Visualizer:
    def __init__(self, output_dir: str = "figures"):
        self.output_dir = output_dir
    
    def plot_gate_metrics(self, metrics: ContractabilityMetrics) -> None:
        """
        Mandatory: Bar chart with threshold line at 40%
        Saves to: {output_dir}/gate_metrics_comparison.png
        """
        ...
    
    def plot_defect_distribution(self, defects: pd.DataFrame) -> None:
        """Pie chart of structural/metamorphic/composition proportions"""
        ...
    
    def plot_execution_times(self, validation_results: list[ValidationResult]) -> None:
        """Histogram of contract execution times (should cluster <10s)"""
        ...
    
    def plot_version_stability(self, stability_matrix: dict) -> None:
        """Line chart showing success rate across library versions"""
        ...
    
    def plot_kappa_heatmap(self, coder1: list[bool], coder2: list[bool]) -> None:
        """2x2 agreement matrix between coders"""
        ...
```

---

### 7. ExperimentRunner (`run_experiment.py`)

**Dependencies:** All above modules

```python
def main():
    # 1. Load corpus
    loader = DefectCorpusLoader()
    defects = loader.load_corpus()
    
    # 2. Generate contracts
    generator = ContractGenerator()
    contracts = [generator.generate_from_defect(d) for _, d in defects.iterrows()]
    
    # 3. Validate contracts
    validator = ContractValidator(timeout=10)
    results = validator.batch_validate([c for c in contracts if c is not None])
    
    # 4. Retrospective coding
    coder = RetrospectiveCoder(defects, random_seed=42)
    coder1_labels, coder2_labels = coder.code_corpus(validator)
    
    # 5. Calculate metrics
    calc = MetricsCalculator()
    metrics = calc.calculate_contractability_rate(
        coder1_labels, coder2_labels, defects['type'].tolist()
    )
    
    # 6. Generate visualizations
    viz = Visualizer(output_dir="figures")
    viz.plot_gate_metrics(metrics)
    viz.plot_defect_distribution(defects)
    viz.plot_execution_times(results)
    
    # 7. Gate evaluation
    print(f"Contractability Rate: {metrics.overall_rate:.1f}%")
    print(f"Cohen's Kappa: {metrics.kappa:.2f}")
    print(f"Gate Status: {metrics.gate_status}")

if __name__ == "__main__":
    main()
```

---

## File Organization

```
h-e1/
├── code/
│   ├── data/
│   │   └── corpus_loader.py         # FR-1: Defect loading
│   ├── contracts/
│   │   ├── generator.py             # FR-2, FR-3, FR-4: Contract generation
│   │   └── validator.py             # FR-5, FR-7: Validation + version testing
│   ├── analysis/
│   │   ├── retrospective_coder.py   # FR-6: 2-coder protocol
│   │   └── metrics.py               # FR-8, FR-9: Metrics + baselines
│   ├── visualization/
│   │   └── plots.py                 # FR-10: All visualizations
│   ├── run_experiment.py            # Main entry point
│   └── requirements.txt
├── figures/                          # Generated visualizations
└── outputs/                          # Results CSV, logs
```

---

## External Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| PyTorch | 1.11-1.13 | Runtime assertions, target API for contracts |
| pandas | ≥1.3.0 | Defect corpus DataFrame operations |
| scikit-learn | ≥1.0.0 | Cohen's kappa calculation |
| scipy | ≥1.7.0 | Wilson score confidence intervals |
| matplotlib | ≥3.4.0 | Visualization generation |
| numpy | ≥1.21.0 | Numerical operations |
| requests | ≥2.26.0 | GitHub corpus download |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Corpus Loading | Download Jiang corpus, filter environment API defects, categorize by type | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| E-2 | Contract Generation | Implement 3 contract types (Structural, Metamorphic, Composition) with invariant parsing | 14 | Module(4) + Deps(3) + Algo(4) + Integ(3) |
| E-3 | Contract Validation | Execute contracts with timeout enforcement, version stability testing | 12 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| E-4 | Retrospective Coding | 2-coder protocol with 3Q filter, Cohen's kappa calculation | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| E-5 | Metrics Calculation | Contractability rate + CI, stratified analysis, gate evaluation | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| E-6 | Visualization | Generate 6 figures (gate metrics, defect distribution, execution times, etc.) | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [E-2], Medium(9-13): [E-3, E-4, E-5, E-6], Low(4-8): [E-1]

**Total Complexity:** 63 (within LIGHT tier budget: 15 tasks max, ~70 complexity)

---

## Design Rationale

### Why This Architecture?

1. **Minimal File Count:** 6 modules (not over-engineered) - appropriate for EXISTENCE PoC
2. **Research-Oriented:** Flow matches retrospective coding protocol, not software product lifecycle
3. **Timeout-First:** Validation module enforces ≤10s constraint at execution layer
4. **Statistical Rigor:** Dedicated retrospective coder module ensures proper 2-coder + kappa protocol
5. **Version Stability Integrated:** Validator handles cross-version testing (FR-7) without separate module

### Key Simplifications for PoC

- Single config file embedded in `run_experiment.py` (no separate config module)
- No separate "baseline" model (this is tool validation, not model comparison)
- Contract generation uses rule-based parsing (not LLM-based) for reproducibility
- No web UI or API (standalone CLI execution)

### What We're NOT Building

- Real-time contract monitoring (retrospective analysis only)
- Automated defect repair (detection only)
- Multi-framework support beyond PyTorch (focus on PyTorch ecosystem)
- Production deployment infrastructure (research PoC)

---

## Self-Validation Checks

- [x] No ASCII diagrams
- [x] KB search summary: "Applied: Research module pattern, validation framework structure"
- [x] Module sections = interface code only (no prose)
- [x] 6 Epic tasks with complexity scores (E-1 through E-6)
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included (green-field status documented)
- [x] EXISTENCE PoC rules: 6 tasks (within 4-8 range), minimal structure, baseline+proposed only

---

**End of Architecture Document**

*Next Phase: Phase 4 - Implementation (Code generation from this architecture)*
