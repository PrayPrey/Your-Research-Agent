# System Architecture: h-m1 Beam Search Mechanism Validation

**Date:** 2026-08-25  
**Author:** Anonymous  
**Hypothesis:** h-m1 (MECHANISM)  
**Tier:** MECHANISM (Epic Range: 6-12 tasks)  
**Infrastructure Level:** Standard

**Applied:** Beam Search Instrumentation Pattern, Diversity Measurement Pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-e1 validated implementation  
**Analyzed Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-e1/code/`  
**Findings:** h-e1 uses flat module structure with local imports. Beam search via vanilla HuggingFace generate(). No custom LogitsProcessor. Reuse data_loader, model_loader, metrics modules.

---

## Architecture Overview

### System Purpose
Validate beam search maintains k parallel sequences throughout generation. Measure beam count at each step and diversity of final outputs. Test k∈{3,5,10} ablation study.

### Design Philosophy
**Extend h-e1 minimal infrastructure:**
- Reuse h-e1 data/model loading (no changes needed)
- Add beam count logging callback
- Add diversity measurement function
- Add ablation study loop
- Minimal new code (YAGNI principle)

---

## Module Structure

### Module 1: Beam Count Logger (`beam_logger.py`)

**Dependencies:** `transformers`

```python
class BeamCountLogger:
    def __init__(self): ...
    def __call__(self, input_ids, scores, **kwargs) -> bool: ...
    def get_counts(self) -> list[int]: ...
    def beam_maintained(self, expected_k: int) -> bool: ...
```

---

### Module 2: Diversity Measurement (`diversity.py`)

**Dependencies:** None (stdlib only)

```python
def measure_diversity(outputs: list[str]) -> dict:
    """Return {unique_count: int, diversity_ratio: float, unique_outputs: list}"""
    ...
```

---

### Module 3: Ablation Study Runner (`ablation.py`)

**Dependencies:** `beam_logger`, `diversity`, h-e1 modules

```python
def run_ablation_study(model, tokenizer, prompts, k_values: list[int], max_tokens: int) -> dict:
    """Run beam search for each k, return metrics"""
    ...

def compare_ablation_results(results: dict) -> dict:
    """Compute comparison statistics"""
    ...
```

---

### Module 4: Visualization (`visualizations.py`)

**Dependencies:** `matplotlib`

```python
def plot_beam_count_over_steps(beam_counts: list[int], k: int, save_path: str): ...

def plot_diversity_by_k(results: dict, save_path: str): ...

def plot_compute_time_vs_k(results: dict, save_path: str): ...
```

---

### Module 5: Main Execution (`run_mechanism_poc.py`)

**Dependencies:** All above + h-e1 modules

```python
def main():
    # Load config
    # Setup device, model (h-e1)
    # Load data (h-e1)
    # Run ablation study
    # Measure diversity
    # Generate figures
    # Save results
    ...
```

---

### Module 6: Config (`config.yaml`)

**Dependencies:** None

```yaml
model:
  name: "meta-llama/CodeLlama-7b-hf"
  device: "auto"

dataset:
  poc_subset_size: 3

ablation:
  k_values: [3, 5, 10]
  max_new_tokens: 256

gates:
  beam_maintenance: 1.0  # 100% steps must maintain k
  diversity_ratio_min: 0.6  # >=60% unique for k=5
```

---

## File Organization

```
h-m1/
├── code/
│   ├── beam_logger.py           # Module 1
│   ├── diversity.py             # Module 2
│   ├── ablation.py              # Module 3
│   ├── visualizations.py        # Module 4
│   ├── run_mechanism_poc.py     # Module 5 (entry point)
│   ├── config.yaml              # Module 6
│   └── requirements.txt
├── figures/
│   ├── beam_count_steps.png     # Mandatory
│   ├── diversity_by_k.png
│   └── compute_time_vs_k.png
└── outputs/
    ├── ablation_results.json
    └── mechanism_log.txt
```

---

## External Dependencies (h-e1 Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_humaneval | `from data_loader import load_humaneval` | h-e1/code/data_loader.py |
| extract_poc_subset | `from data_loader import extract_poc_subset` | h-e1/code/data_loader.py |
| load_codellama | `from model_loader import load_codellama` | h-e1/code/model_loader.py |
| setup_device | `from model_loader import setup_device` | h-e1/code/model_loader.py |
| time_generation | `from metrics import time_generation` | h-e1/code/metrics.py |

**Verified from:** h-e1/code/ actual implementation  
**Reuse Strategy:** Copy h-e1 modules to h-m1/code/ (flat structure, local imports)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup h-m1 environment | Copy h-e1 modules, install deps | 3 | 1+0+0+2 |
| M-2 | Beam count logger | Implement BeamCountLogger callback | 7 | 2+1+2+2 |
| M-3 | Diversity measurement | Implement diversity metrics | 4 | 1+0+2+1 |
| M-4 | Greedy baseline | Run k=1 greedy baseline | 3 | 1+0+1+1 |
| M-5 | Ablation study | Run k∈{3,5,10} ablation loop | 9 | 2+2+2+3 |
| M-6 | Visualization | Generate 3 mandatory figures | 6 | 2+1+1+2 |
| M-7 | Validation pipeline | Orchestrate PoC + gate checks | 5 | 1+2+0+2 |

**Total Epic Tasks:** 7 (within MECHANISM range 6-12)  
**Total Complexity:** 37/140  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-5], Low(4-8): [M-2, M-3, M-6, M-7], VeryLow(1-3): [M-1, M-4]

---

## External Dependencies

### Python Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| transformers | >=4.30.0 | Beam search callbacks |
| torch | >=2.0.0 | Model inference |
| datasets | >=2.12.0 | HumanEval (h-e1) |
| matplotlib | >=3.5.0 | Figures |

### h-e1 Prerequisites

- CodeLlama-7B cached (from h-e1 validation)
- HumanEval dataset downloaded (from h-e1)

---

## Success Criteria

**System Complete When:**
1. All 7 Epic tasks implemented
2. Beam count = k at ALL steps (100% maintenance)
3. Diversity ratio ≥ 60% for k=5
4. 3 figures generated
5. results.json saved

---

**Document Status:** Ready for Phase 4 Implementation
