# H-E1: Data Extraction Experiment

**Hypothesis Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Objective:** Verify that published technical reports from major LLM labs contain category-level error rate data suitable for building an error taxonomy.

## Overview

This experiment extracts and validates category-level benchmark results from technical reports for:
- **Model Families:** GPT, Claude, Llama
- **Timepoints:** Baseline vs. Current
- **Benchmarks:** TruthfulQA, MMLU

## Success Criteria

### Primary (Gate Condition)
- ≥3 model families with category-level data for both timepoints

### Secondary
- Data granularity: ≥10 categories per benchmark
- Data completeness: ≥90%

## Installation

```bash
# Create conda environment
conda create -n youra-h-e1 python=3.10 -y
conda activate youra-h-e1

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run with Mock Data (Testing)
```bash
python run_experiment.py --mock
```

### Run with Real Downloads
```bash
python run_experiment.py
```

## Output Files

### Data
- `data/extracted/h-e1_extracted_data.csv` - Extracted category-level error rates
- `data/extracted/h-e1_validation.json` - Validation results
- `data/extracted/h-e1_metadata.json` - Report metadata

### Figures
- `figures/gate_metrics.png` - Gate metric visualization (MANDATORY)
- `figures/granularity_heatmap.png` - Category counts by family/benchmark
- `figures/completeness_matrix.png` - Data availability matrix
- `figures/temporal_timeline.png` - Timeline of baseline vs. current

### Logs
- `logs/extraction.log` - Detailed execution log

## Architecture

```
src/
├── config.py           # Configuration constants
├── data_collector.py   # Report downloading with retry logic
├── parser.py           # PDF/HTML table extraction
├── validator.py        # Data quality validation
├── analyzer.py         # Gate metrics computation
└── visualizer.py       # Figure generation
```

## Gate Evaluation

The experiment evaluates the **MUST_WORK** gate condition:
- ✅ **PASS:** ≥3 families with both timepoints → Continue to H-M1
- ❌ **FAIL:** <3 families → ABORT (approach infeasible)

## Notes

- **Execution Time:** <5 minutes (data extraction only, no model training)
- **GPU Required:** No (text processing only)
- **Mock Data:** Available for testing without downloads
