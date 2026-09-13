# System Architecture: h-m3 Invalid Beam Pruning

**Date:** 2026-08-25  
**Hypothesis:** h-m3 (MECHANISM)  
**Tier:** MECHANISM (Epic Range: 6-12 tasks)  
**Infrastructure Level:** Standard

**Applied:** Temporal Tracking Pattern, Beam Validity Logging Pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extends h-m2 validated combined scoring infrastructure  
**Analyzed Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m2/code/`  
**Findings:** h-m2 has combined scoring (scoring.py), AST validation (ast_validator.py), and custom beam search (beam_search_custom.py). Add per-step validity tracking to beam search. Reuse all h-m2 validation/scoring modules.

---

## Architecture Overview

### System Purpose
Track beam validity status over generation timeline to verify invalid beams are pruned. Measure reduction rate (start → end), final validity distribution, and temporal pruning dynamics. Compare against pure log-likelihood baseline.

### Design Philosophy
**Extend h-m2 with minimal tracking layer:**
- Reuse h-m2 scoring, validation, beam search
- Add BeamValidityTracker to log per-step states
- Add temporal analysis (early/middle/late phases)
- Minimal new code (instrumentation only)

---

## Module Structure

### Module 1: Beam Validity Tracker (`beam_validity_tracker.py`)

**Dependencies:** `ast_validator` from h-m2

```python
class BeamValidityTracker:
    def __init__(self): ...
    def track_step(self, step_id: int, beams: list[str]) -> None: ...
    def compute_reduction(self) -> float: ...
    def get_temporal_log(self) -> list[dict]: ...
    def get_phase_stats(self, total_steps: int) -> dict: ...
```

---

### Module 2: Tracked Beam Search (`beam_search_tracked.py`)

**Dependencies:** `beam_search_custom` from h-m2, `beam_validity_tracker`

```python
def run_beam_search_with_tracking(
    model,
    tokenizer,
    prompt: str,
    k: int,
    alpha: float,
    beta: float,
    max_tokens: int
) -> tuple[list[str], dict]:
    """Return (outputs, tracking_data)"""
    ...
```

---

### Module 3: Experiment Runners (`experiments.py`)

**Dependencies:** `beam_search_tracked`, h-m2 modules

```python
def experiment_a_tracking(model, tokenizer, dataset: list[dict], k: int = 5, alpha: float = 0.7, beta: float = 0.3) -> dict:
    """Track invalid proportion over time across all problems"""
    ...

def experiment_b_final_validity(tracking_results: dict) -> dict:
    """Analyze final beam validity distribution"""
    ...

def experiment_c_temporal_dynamics(tracking_results: dict) -> dict:
    """Compute early/middle/late phase statistics"""
    ...

def baseline_comparison(model, tokenizer, dataset: list[dict], k: int = 5) -> dict:
    """Run pure log-likelihood (alpha=1.0, beta=0.0) with tracking"""
    ...
```

---

### Module 4: Analysis (`analysis.py`)

**Dependencies:** `numpy`, `pandas`

```python
def analyze_reduction_rates(tracking_results: dict) -> dict:
    """Compute mean/median reduction across problems"""
    ...

def analyze_final_validity(tracking_results: dict) -> dict:
    """Compute valid proportion statistics"""
    ...

def analyze_temporal_pattern(tracking_results: dict) -> dict:
    """Phase-wise invalid proportion, monotonicity check"""
    ...

def compare_baseline(combined_results: dict, pure_results: dict) -> dict:
    """Compare pruning patterns"""
    ...
```

---

### Module 5: Main Execution (`run_experiments.py`)

**Dependencies:** All above + h-m2 modules

```python
def main():
    # Load config
    # Setup device, model (h-m2)
    # Load HumanEval (h-m2)
    # Run Experiment A (tracking on full dataset)
    # Run Experiment B (final validity analysis)
    # Run Experiment C (temporal dynamics)
    # Run baseline comparison
    # Analyze results
    # Save outputs
    # Check gate criteria
    ...
```

---

### Module 6: Config (`config.py`)

**Dependencies:** None

```python
CONFIG = {
    'model': {
        'name': 'meta-llama/CodeLlama-7b-hf',
        'device': 'auto',
        'dtype': 'float16'
    },
    'dataset': {
        'full_size': 164
    },
    'scoring': {
        'alpha': 0.7,
        'beta': 0.3
    },
    'baseline': {
        'alpha': 1.0,
        'beta': 0.0
    },
    'beam_search': {
        'k': 5,
        'max_new_tokens': 512,
        'temperature': 0.8
    },
    'gates': {
        'reduction_rate_mean': 0.50,
        'final_valid_proportion': 0.60,
        'final_valid_problems_pct': 0.70
    }
}
```

---

## File Organization

```
h-m3/
├── code/
│   ├── beam_validity_tracker.py  # Module 1
│   ├── beam_search_tracked.py    # Module 2
│   ├── experiments.py             # Module 3
│   ├── analysis.py                # Module 4
│   ├── run_experiments.py         # Module 5 (entry point)
│   ├── config.py                  # Module 6
│   └── requirements.txt
└── results/
    ├── beam_validity_logs.csv
    ├── reduction_rates.json
    ├── final_validity.json
    ├── temporal_dynamics.json
    └── baseline_comparison.json
```

---

## External Dependencies (h-m2 Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| validate_syntax_timed | `from ast_validator import validate_syntax_timed` | h-m2/code/ast_validator.py |
| combined_score | `from scoring import combined_score` | h-m2/code/scoring.py |
| CustomBeamScorer | `from beam_search_custom import CustomBeamScorer` | h-m2/code/beam_search_custom.py |
| run_beam_search_scored | `from beam_search_custom import run_beam_search_scored` | h-m2/code/beam_search_custom.py |
| load_humaneval | `from data_loader import load_humaneval` | h-m2/code/data_loader.py |
| load_codellama | `from model_loader import load_codellama` | h-m2/code/model_loader.py |

**Verified from:** h-m2/code/ actual implementation  
**Reuse Strategy:** Copy h-m2 modules (ast_validator, scoring, beam_search_custom, data_loader, model_loader) to h-m3/code/. Use flat structure with local imports.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| T-1 | Setup h-m3 environment | Copy h-m2 modules, install deps | 3 | 1+0+0+2 |
| T-2 | Beam validity tracker | Implement per-step tracking class | 7 | 2+1+2+2 |
| T-3 | Tracked beam search | Integrate tracker into beam search | 8 | 2+2+2+2 |
| T-4 | Experiment A runner | Invalid proportion tracking on full dataset | 9 | 2+2+2+3 |
| T-5 | Experiment B+C analysis | Final validity + temporal dynamics | 6 | 2+1+1+2 |
| T-6 | Baseline comparison | Pure log-likelihood with tracking | 6 | 2+1+1+2 |
| T-7 | Analysis pipeline | Reduction stats, phase analysis, gate checks | 10 | 3+2+2+3 |
| T-8 | Results saving | CSV logs, JSON summaries | 5 | 1+1+1+2 |

**Total Epic Tasks:** 8 (within MECHANISM range 6-12)  
**Total Complexity:** 54/160  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [T-4, T-7], Low(4-8): [T-2, T-3, T-5, T-6, T-8], VeryLow(1-3): [T-1]

---

## External Dependencies

### Python Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| transformers | >=4.30.0 | Model inference |
| torch | >=2.0.0 | Backend |
| datasets | >=2.12.0 | HumanEval |
| numpy | >=1.24.0 | Statistics |
| pandas | >=2.0.0 | Log analysis |

### h-m2 Prerequisites

- CodeLlama-7B cached (from h-m2)
- HumanEval dataset downloaded (from h-m2)
- h-m2 validated combined scoring (α=0.7, β=0.3)
- AST validation latency <0.05ms

---

## Success Criteria

**System Complete When:**
1. All 8 Epic tasks implemented
2. Mean reduction rate ≥50% (Experiment A)
3. Mean final valid proportion ≥60% (Experiment B)
4. Invalid proportion decreases monotonically (Experiment C)
5. Combined scoring shows pruning, pure beam search doesn't (Baseline)
6. All result files saved to results/

---

**Document Status:** Ready for Phase 4 Implementation
