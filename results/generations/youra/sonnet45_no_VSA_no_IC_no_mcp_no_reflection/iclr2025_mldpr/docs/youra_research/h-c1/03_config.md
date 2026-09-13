# Configuration: Expert Consensus Validation System (h-c1)

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis ID:** h-c1  
**Type:** CONDITION (EXISTENCE)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field implementation - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** Hardcoded dict (EXISTENCE hypothesis - single config)

---

## Applied Patterns

Applied: Statistical validation thresholds (PRD Section 6.1)  
Applied: Fixed window configuration (Architecture Section "Key Design Decisions")

---

## A-5: Integration [Complexity: 6, Budget: 1]

### Configuration (Hardcoded Dict)

```python
# config.py

# Data Validation
CONFIDENCE_THRESHOLD = 4  # High-confidence responses only (≥4/5)
MIN_SAMPLE_SIZE = 30  # Statistical power threshold (PRD FR-11)
VALID_YEAR_RANGE = (2017, 2024)  # Saturation date bounds
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]

# Statistical Thresholds (PRD Section 6.1)
AGREEMENT_WINDOW_MONTHS = 12  # ±1 year from modal date
AGREEMENT_THRESHOLD = 0.70  # Primary success criterion
KAPPA_THRESHOLD = 0.60  # Fleiss' kappa threshold (substantial agreement)

# Statistical Testing
BOOTSTRAP_ITERATIONS = 1000  # 95% CI estimation (PRD FR-6)
PERMUTATION_ITERATIONS = 1000  # Null hypothesis test (PRD FR-7)
RANDOM_SEED = 42  # Reproducibility

# Domain Balance
MIN_DOMAIN_RATIO = 0.4
MAX_DOMAIN_RATIO = 0.6

# Visualization
OUTPUT_FORMATS = ["csv", "json", "md"]  # Results export formats
PLOT_DPI = 150
PLOT_FORMATS = ["png"]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-5-1 | Config file | Create config.py with thresholds from PRD |

---

## Configuration Validation

**Self-Check:**
- [x] One format only (hardcoded dict - EXISTENCE hypothesis)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Codebase Analysis section included
- [x] Total length < 400 lines

**Serena Validation:**
- [x] Green-field project - Serena skip acceptable

**Values Source:**
- All thresholds from PRD Section 6.1 (Primary Metrics)
- Window size from PRD FR-4
- Iteration counts from PRD FR-6, FR-7
- Year range from PRD Section 5.1

---

## Usage Example

```python
# validate_consensus.py

from config import *
from src.data_loader import SurveyDataLoader
from src.metrics import calculate_modal_date, calculate_agreement_rate

loader = SurveyDataLoader("data/survey.csv", CONFIDENCE_THRESHOLD)
df = loader.load_raw()
df_filtered = loader.filter_high_confidence(df)

for benchmark in BENCHMARKS:
    subset = loader.get_benchmark_subset(df_filtered, benchmark)
    modal_date = calculate_modal_date(subset["saturation_date"])
    agreement = calculate_agreement_rate(subset["saturation_date"], modal_date, AGREEMENT_WINDOW_MONTHS)
    
    if agreement > AGREEMENT_THRESHOLD:
        print(f"{benchmark}: PASS ({agreement:.1%})")
```

---

**Config Status:** COMPLETE  
**Ready for Phase 4 (Coder):** YES  
**Format:** Hardcoded dict (copy-paste ready)
