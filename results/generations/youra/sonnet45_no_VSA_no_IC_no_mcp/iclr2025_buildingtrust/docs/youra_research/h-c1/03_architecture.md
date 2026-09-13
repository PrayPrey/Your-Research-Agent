# Architecture: h-c1

**Date:** 2026-08-24  
**Hypothesis:** h-c1 (CONDITION)  
**Type:** Validation (no training)  
**Applied:** Standard validation pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New validation implementation  
**Analyzed Path**: N/A (no existing codebase for h-c1)  
**Findings**: Standard library-based validation (spaCy + Wikipedia API)

---

## System Overview

**Goal:** Validate two pre-conditions (NER F1 ≥ 0.90, Wikipedia coverage ≥ 0.90) on TruthfulQA entity subset.

**Components:**
- Data loader (TruthfulQA → gold annotations)
- NER validator (spaCy scorer)
- Wikipedia checker (API-based existence)
- Gate evaluator (threshold comparison)
- Reporter (figures + validation.md)

**Data Flow:**
1. Load TruthfulQA subset → filter 100 entity samples
2. NER validation → spaCy scorer → F1 score
3. Wikipedia validation → API existence check → coverage
4. Gate evaluation → compare thresholds → PASS/FAIL
5. Report generation → 4 figures + validation.md

---

## Modules

### DataLoader (`data/loader.py`)

**Dependencies:** None

```python
from typing import List, Dict, Tuple
from datasets import load_dataset

class TruthfulQALoader:
    def load_entity_subset(self) -> Tuple[List[Dict], List[str]]:
        """
        Returns:
            gold_data: [(text, {"entities": [(start, end, label)]})]
            entity_names: [str] for Wikipedia lookup
        """
        ...
    
    def _filter_single_entity_questions(self, dataset) -> List[Dict]: ...
```

### NERValidator (`validation/ner_validator.py`)

**Dependencies:** DataLoader

```python
import spacy
from spacy.training import Example
from spacy.scorer import Scorer

class NERValidator:
    def __init__(self, model_name: str = "en_core_web_lg"): ...
    
    def validate(self, gold_data: List[Tuple]) -> Dict[str, float]:
        """
        Returns:
            {"ner_f1": float, "precision": float, "recall": float}
        """
        ...
```

### WikipediaChecker (`validation/wikipedia_checker.py`)

**Dependencies:** DataLoader

```python
import wikipediaapi
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

class WikipediaChecker:
    def __init__(self, max_workers: int = 10): ...
    
    def check_coverage(self, entities: List[str]) -> Dict[str, float]:
        """
        Returns:
            {"coverage": float, "found": int, "total": int}
        """
        ...
    
    def _check_entity(self, entity: str) -> bool:
        """Page exists + non-stub (>100 chars)"""
        ...
```

### GateEvaluator (`validation/gate_evaluator.py`)

**Dependencies:** NERValidator, WikipediaChecker

```python
from typing import Dict

class GateEvaluator:
    def __init__(self, ner_threshold: float = 0.90, 
                 coverage_threshold: float = 0.90): ...
    
    def evaluate(self, ner_f1: float, coverage: float) -> Dict:
        """
        Returns:
            {
                "gate_status": "PASS" | "FAIL",
                "ner_f1": float,
                "coverage": float,
                "ner_passed": bool,
                "coverage_passed": bool
            }
        """
        ...
```

### Reporter (`reporting/reporter.py`)

**Dependencies:** GateEvaluator

```python
import matplotlib.pyplot as plt
from typing import Dict

class Reporter:
    def __init__(self, output_dir: str): ...
    
    def generate_report(self, gate_result: Dict, 
                       ner_details: Dict, 
                       wiki_details: Dict) -> None:
        """Writes 04_validation.md + 4 figures"""
        ...
    
    def _plot_target_vs_actual(self, ner_f1: float, coverage: float): ...
    def _plot_ner_confusion_matrix(self, ner_details: Dict): ...
    def _plot_coverage_by_type(self, wiki_details: Dict): ...
    def _plot_f1_distribution(self, ner_details: Dict): ...
```

### Main Script (`validate.py`)

**Dependencies:** All above modules

```python
from data.loader import TruthfulQALoader
from validation.ner_validator import NERValidator
from validation.wikipedia_checker import WikipediaChecker
from validation.gate_evaluator import GateEvaluator
from reporting.reporter import Reporter

def main():
    # Load data
    loader = TruthfulQALoader()
    gold_data, entity_names = loader.load_entity_subset()
    
    # Run validations
    ner_validator = NERValidator()
    ner_result = ner_validator.validate(gold_data)
    
    wiki_checker = WikipediaChecker()
    wiki_result = wiki_checker.check_coverage(entity_names)
    
    # Evaluate gate
    gate_evaluator = GateEvaluator()
    gate_result = gate_evaluator.evaluate(
        ner_result["ner_f1"], 
        wiki_result["coverage"]
    )
    
    # Generate report
    reporter = Reporter("./figures")
    reporter.generate_report(gate_result, ner_result, wiki_result)
    
    # Exit code based on gate
    return 0 if gate_result["gate_status"] == "PASS" else 1

if __name__ == "__main__":
    exit(main())
```

---

## File Structure

```
h-c1/
├── code/
│   ├── data/
│   │   └── loader.py
│   ├── validation/
│   │   ├── ner_validator.py
│   │   ├── wikipedia_checker.py
│   │   └── gate_evaluator.py
│   ├── reporting/
│   │   └── reporter.py
│   └── validate.py
├── figures/
│   ├── target_vs_actual.png
│   ├── ner_confusion_matrix.png
│   ├── coverage_by_type.png
│   └── f1_distribution.png
└── 04_validation.md
```

---

## Error Handling

**Strategy:** Fail early with clear diagnostics

| Error Condition | Handling |
|----------------|----------|
| spaCy model not found | Exit with download instructions |
| Wikipedia API timeout | Retry once, skip entity if fails, log |
| Missing gold annotations | Fail with file path diagnostic |
| Invalid entity span | Skip entity, log warning, continue |
| Empty subset | Fail with "No samples to validate" |

**Logging:** Python `logging` module, INFO level default

---

## Dependencies

**Python Libraries:**
- `spacy==3.7.0` (NER validation)
- `wikipediaapi==0.6.0` (coverage check)
- `datasets==2.14.0` (TruthfulQA loader)
- `matplotlib==3.8.0` (visualization)

**External Downloads:**
- spaCy model: `python -m spacy download en_core_web_lg` (~800MB)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C1-1 | Data Pipeline | Load TruthfulQA, filter 100 entity samples, create gold annotations | 8 | loader(3) + filter(2) + format(3) |
| C1-2 | NER Validation | Implement spaCy scorer integration | 6 | scorer_setup(2) + example_format(2) + extract_f1(2) |
| C1-3 | Wikipedia Validation | API-based coverage check with concurrency | 7 | api_setup(2) + concurrent(3) + stub_filter(2) |
| C1-4 | Gate Logic | Threshold comparison + result formatting | 4 | compare(2) + format(2) |
| C1-5 | Reporting | Generate 4 figures + validation.md | 9 | target_vs_actual(2) + confusion(3) + coverage_plot(2) + report_md(2) |

**Distribution:** Low(4-8): [C1-2, C1-4], Medium(9-13): [C1-1, C1-3, C1-5]

**Total Complexity:** 34 (mid-range for validation task)

---

## Validation Success Criteria

**Pass Condition:**
```python
gate_pass = (ner_f1 >= 0.90) and (coverage >= 0.90)
```

**Expected Outcome:** PASS (baseline spaCy ~0.88, Wikipedia coverage ~0.95)

---

## Notes

- No training loops (CONDITION type)
- No model checkpoints (pre-trained only)
- No hyperparameter tuning
- Deterministic evaluation (no random seeds needed)
- Runtime estimate: <5 minutes (100 samples + API calls)

---

*Architecture for pure validation experiment*  
*Next: Phase 4 Implementation*
