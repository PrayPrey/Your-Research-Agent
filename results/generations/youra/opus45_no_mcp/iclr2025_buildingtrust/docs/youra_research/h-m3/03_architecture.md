# Architecture Design: H-M3

**Hypothesis:** Positional Analysis of Marker-Confidence Ordering
**Date:** 2026-08-19
**Type:** MECHANISM (FULL tier)

---

## Codebase Analysis (Serena)

**Note:** Serena MCP unavailable. Architecture based on H-M2 codebase patterns.

**H-M2 Code Structure Reference:**
- `h-m2/code/` contains existing experiment infrastructure
- Reuse data loading and output format patterns from H-M2

---

## Applied Patterns

Applied: Text Parsing Pipeline Pattern
Applied: Gate Validation Pattern (from H-M1, H-M2)
Applied: Cached Result Reuse Pattern

---

## Module Structure

### 1. Data Loading Module
**Purpose:** Load H-M2 cached outputs for analysis
**Complexity:** Low (reuse existing cache)

### 2. Position Extraction Module
**Purpose:** Extract confidence and hedging marker positions
**Complexity:** Medium (regex patterns, position tracking)

### 3. Positional Analysis Module
**Purpose:** Compute marker-before-confidence relationships
**Complexity:** Medium (comparison logic)

### 4. Gate Metrics Module
**Purpose:** Calculate gate validation metrics
**Complexity:** Low (aggregation)

### 5. Visualization Module
**Purpose:** Generate required figures
**Complexity:** Low (matplotlib bar charts)

---

## File Structure

```
h-m3/
├── code/
│   ├── __init__.py
│   ├── data_loader.py          # Cache loading
│   ├── position_extractor.py   # Confidence/marker position extraction
│   ├── positional_analysis.py  # Main analysis logic
│   ├── gate_metrics.py         # Gate computation
│   ├── visualization.py        # Figure generation
│   ├── config.py               # Configuration
│   └── run_experiment.py       # Main entry point
├── results/
│   ├── h-m3_results.json
│   └── gate_metrics.yaml
└── figures/
    └── gate_comparison.png
```

---

## Epic Tasks

### Epic E1: Data Loading
**Description:** Load and validate H-M2 cached outputs
**Complexity Score:** 6/20
- Module_Size: 1
- Dependencies: 2 (H-M2 cache, json)
- Algorithm: 1
- Integration: 2

**Deliverables:**
- Load H-M2 results JSON
- Validate output format
- Return list of output texts

### Epic E2: Position Extraction
**Description:** Extract confidence and hedging marker positions from text
**Complexity Score:** 10/20
- Module_Size: 2
- Dependencies: 1 (re module)
- Algorithm: 4 (regex patterns)
- Integration: 3

**Deliverables:**
- `extract_confidence_position(output)` → (position, value)
- `extract_hedging_positions(output)` → List[(marker, position)]
- Handle edge cases (no confidence, no markers)

### Epic E3: Positional Analysis
**Description:** Analyze marker-confidence position relationships
**Complexity Score:** 12/20
- Module_Size: 2
- Dependencies: 2
- Algorithm: 5 (position comparison logic)
- Integration: 3

**Deliverables:**
- `PositionalAnalysis` dataclass with all metrics
- `analyze_output(output_id, output)` → PositionalAnalysis
- CoT-then-confidence order detection

### Epic E4: Gate Metrics
**Description:** Compute H-M3 gate validation metrics
**Complexity Score:** 8/20
- Module_Size: 1
- Dependencies: 2
- Algorithm: 3
- Integration: 2

**Deliverables:**
- `compute_gate_metrics(analyses)` → dict
- cot_order_rate calculation
- markers_precede_rate calculation
- Pass/fail determination

### Epic E5: Visualization
**Description:** Generate required figures
**Complexity Score:** 6/20
- Module_Size: 1
- Dependencies: 2 (matplotlib)
- Algorithm: 1
- Integration: 2

**Deliverables:**
- Gate metrics bar chart (mandatory)
- Position distribution histogram (optional)

### Epic E6: Experiment Runner
**Description:** Main orchestration and result saving
**Complexity Score:** 8/20
- Module_Size: 2
- Dependencies: 3
- Algorithm: 2
- Integration: 3

**Deliverables:**
- `run_experiment.py` main entry
- JSON results output
- YAML gate metrics output
- Summary logging

---

## Complexity Summary

| Epic | Score | Category |
|------|-------|----------|
| E1: Data Loading | 6/20 | Low |
| E2: Position Extraction | 10/20 | Medium |
| E3: Positional Analysis | 12/20 | Medium |
| E4: Gate Metrics | 8/20 | Low |
| E5: Visualization | 6/20 | Low |
| E6: Experiment Runner | 8/20 | Low |

**Total:** 6 Epic tasks (within 6-12 range for FULL tier)
**Average Complexity:** 8.3/20

---

## External Dependencies (from H-M2)

```python
# Import from H-M2 if shared utilities exist
# Otherwise implement standalone
```

---

## Integration Points

1. **H-M2 Cache:** Read from `../h-m2/code/results/h-m2_results.json`
2. **Output Format:** Match H-M1/H-M2 results structure
3. **Gate Format:** Standard gate_metrics.yaml schema

---

*Architecture designed for H-M3 positional analysis experiment*
