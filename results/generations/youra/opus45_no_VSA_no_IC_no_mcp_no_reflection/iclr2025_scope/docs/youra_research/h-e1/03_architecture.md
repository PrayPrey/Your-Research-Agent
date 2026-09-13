# Architecture Design: h-e1

**Version:** 1.0
**Date:** 2026-08-29
**Hypothesis:** h-e1 (EXISTENCE)
**Budget:** LIGHT tier (max 15 tasks, 4-8 epics)

---

## Codebase Analysis (Serena)

Green-field implementation. No existing codebase to analyze.

Applied: Modular DL Experiment Pattern (Archon KB)
Applied: Single-File PoC Pattern for EXISTENCE hypotheses

---

## Module Structure

```
h-e1/
├── code/
│   ├── __init__.py
│   ├── duality_conversion.py    # Core: BERT → SSM conversion
│   ├── selective_scan.py        # Reference selective scan
│   ├── stability_validation.py  # Validation pipeline
│   ├── data_loader.py           # WikiText-103 loading
│   └── run_experiment.py        # Main entry point
├── configs/
│   └── experiment_config.yaml
├── figures/
│   └── (generated at runtime)
└── results/
    └── validation_results.json
```

---

## File Organization

| File | Purpose | Size Est. |
|------|---------|-----------|
| `duality_conversion.py` | Core duality equations, SVD decomposition | ~150 LOC |
| `selective_scan.py` | Reference scan implementation | ~80 LOC |
| `stability_validation.py` | NaN/Inf checks, magnitude ratio | ~60 LOC |
| `data_loader.py` | WikiText-103 preprocessing | ~50 LOC |
| `run_experiment.py` | Orchestration, figure generation | ~120 LOC |

Total: ~460 LOC (appropriate for EXISTENCE PoC)

---

## Proposed Tasks

### Epic Tasks with Complexity Scores

| Task ID | Name | Complexity | Breakdown |
|---------|------|------------|-----------|
| E-1 | Environment Setup | 6 (Low) | Module: 1, Deps: 2, Algo: 1, Int: 2 |
| E-2 | Data Pipeline | 8 (Low) | Module: 2, Deps: 2, Algo: 2, Int: 2 |
| E-3 | Duality Conversion Module | 14 (High) | Module: 3, Deps: 2, Algo: 6, Int: 3 |
| E-4 | Selective Scan Implementation | 12 (Medium) | Module: 2, Deps: 2, Algo: 5, Int: 3 |
| E-5 | Stability Validation | 10 (Medium) | Module: 2, Deps: 2, Algo: 3, Int: 3 |
| E-6 | Experiment Runner & Visualization | 9 (Medium) | Module: 2, Deps: 2, Algo: 2, Int: 3 |

**Total Epics:** 6 (within 4-8 range)

### Complexity Distribution

- Very High (18-20): 0
- High (14-17): 1 (E-3)
- Medium (9-13): 3 (E-4, E-5, E-6)
- Low (4-8): 2 (E-1, E-2)

---

## Budget Allocation

| Category | Count |
|----------|-------|
| Epic Tasks | 6 |
| Subtask Budget | 15 - 6 = 9 |
| High Priority Subtasks | 4 (E-3: Duality Conversion) |
| Medium Priority Subtasks | 5 (E-4, E-5) |

---

## Dependencies

### External Libraries

```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.0.0
matplotlib>=3.7.0
pyyaml>=6.0
```

### Model Dependencies

- BERT-base-uncased (HuggingFace Hub)

### Dataset Dependencies

- WikiText-103 (HuggingFace Datasets)

---

## Integration Points

1. **BERT Weight Extraction** → Duality Conversion
2. **Duality Conversion** → SSM Parameters
3. **SSM Parameters** → Selective Scan
4. **Selective Scan Output** → Stability Validation
5. **Validation Results** → Visualization

---

*Architecture designed for EXISTENCE hypothesis validation*
*Next: Logic Design (Step 5)*
