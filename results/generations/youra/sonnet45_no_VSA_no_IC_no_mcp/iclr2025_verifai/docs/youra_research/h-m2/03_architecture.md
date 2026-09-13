# System Architecture: h-m2 Combined Scoring Function

**Date:** 2026-08-25  
**Hypothesis:** h-m2 (MECHANISM)  
**Tier:** MECHANISM (Epic Range: 6-12 tasks)  
**Infrastructure Level:** Standard

**Applied:** Scoring Function Pattern, AST Validation Pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extends h-m1 validated beam search infrastructure  
**Analyzed Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m1/code/`  
**Findings:** h-m1 has vanilla beam search + basic validate_syntax(). Reuse model_loader, data_loader, beam_logger. Add timing instrumentation to AST validation and custom scoring to beam selection.

---

## Architecture Overview

### System Purpose
Implement combined scoring (α * log_likelihood + β * syntax_validity_score) for beam search. Validate AST parse latency <50ms. Verify valid beams rank higher than invalid beams ≥80% of steps. Compare against greedy and pure log-likelihood baselines.

### Design Philosophy
**Extend h-m1 with minimal additions:**
- Reuse h-m1 beam search infrastructure
- Add timing to existing validate_syntax()
- Add custom scoring to beam selection
- Add weight ablation loop
- Minimal new code (extend, don't rewrite)

---

## Module Structure

### Module 1: AST Validator with Timing (`ast_validator.py`)

**Dependencies:** stdlib only

```python
def validate_syntax_timed(code: str) -> tuple[bool, float]:
    """Return (valid, elapsed_ms)"""
    ...

def compute_latency_stats(timings: list[float]) -> dict:
    """Return {mean, median, p95, max}"""
    ...
```

---

### Module 2: Combined Scoring (`scoring.py`)

**Dependencies:** `ast_validator`

```python
def combined_score(log_likelihood: float, code: str, alpha: float = 0.7, beta: float = 0.3) -> tuple[float, bool, float]:
    """Return (final_score, validity, elapsed_ms)"""
    ...

def rank_beams(scores: list[float]) -> list[int]:
    """Return rank indices (0 = highest score)"""
    ...
```

---

### Module 3: Custom Beam Search (`beam_search_custom.py`)

**Dependencies:** `scoring`, `transformers`

```python
class CustomBeamScorer:
    def __init__(self, alpha: float = 0.7, beta: float = 0.3): ...
    def score_candidates(self, candidates: list[str], log_probs: list[float]) -> list[float]: ...
    def log_step(self, step: int, candidates: list[str], scores: list[float], ranks: list[int]): ...
    def get_logs(self) -> list[dict]: ...

def run_beam_search_scored(model, tokenizer, prompt: str, k: int, alpha: float, beta: float, max_tokens: int) -> tuple[list[str], list[dict]]:
    """Run beam search with combined scoring. Return (outputs, step_logs)"""
    ...
```

---

### Module 4: Experiment Runners (`experiments.py`)

**Dependencies:** `beam_search_custom`, `ast_validator`, h-m1 modules

```python
def experiment_a_latency(model, tokenizer, dataset: list[dict], k: int = 5) -> dict:
    """Measure AST parse latency across full dataset"""
    ...

def experiment_b_ranking(model, tokenizer, dataset: list[dict], alpha: float = 0.7, beta: float = 0.3) -> dict:
    """Verify beam ranking correctness"""
    ...

def experiment_c_ablation(model, tokenizer, subset: list[dict], weight_pairs: list[tuple]) -> dict:
    """Test α/β weight combinations"""
    ...

def baseline_comparison(model, tokenizer, dataset: list[dict]) -> dict:
    """Run greedy and pure log-likelihood baselines"""
    ...
```

---

### Module 5: Analysis (`analysis.py`)

**Dependencies:** `numpy`, `pandas`

```python
def analyze_latency(timings: list[float]) -> dict:
    """Compute latency statistics + gate check"""
    ...

def analyze_ranking(logs: list[dict]) -> dict:
    """Compute ranking correctness proportion"""
    ...

def compare_ablation(results: dict) -> dict:
    """Identify optimal α/β weights"""
    ...

def compare_baselines(greedy_errors: float, pure_beam_errors: float, combined_errors: float) -> dict:
    """Compute relative improvements"""
    ...
```

---

### Module 6: Main Execution (`run_experiments.py`)

**Dependencies:** All above + h-m1 modules

```python
def main():
    # Load config
    # Setup device, model (h-m1)
    # Load HumanEval (h-m1)
    # Create ablation subset
    # Run experiments A, B, C
    # Run baseline comparison
    # Analyze results
    # Save outputs
    # Check gate criteria
    ...
```

---

### Module 7: Config (`config.yaml`)

**Dependencies:** None

```yaml
model:
  name: "meta-llama/CodeLlama-7b-hf"
  device: "auto"
  dtype: "float16"

dataset:
  full_size: 164  # HumanEval-164
  ablation_size: 20  # Stratified subset

scoring:
  alpha_default: 0.7
  beta_default: 0.3
  weight_pairs:
    - [0.5, 0.5]
    - [0.6, 0.4]
    - [0.7, 0.3]
    - [0.8, 0.2]

beam_search:
  k: 5
  max_new_tokens: 512
  temperature: 0.8

gates:
  ast_latency_mean_ms: 50
  ast_latency_p95_ms: 100
  ranking_correctness_min: 0.8  # 80% of steps
  syntax_error_rate_max: 0.64  # Must beat greedy baseline
```

---

## File Organization

```
h-m2/
├── code/
│   ├── ast_validator.py         # Module 1
│   ├── scoring.py               # Module 2
│   ├── beam_search_custom.py    # Module 3
│   ├── experiments.py           # Module 4
│   ├── analysis.py              # Module 5
│   ├── run_experiments.py       # Module 6 (entry point)
│   ├── config.yaml              # Module 7
│   └── requirements.txt
└── results/
    ├── ast_latency_stats.json
    ├── beam_ranking_logs.csv
    ├── ablation_results.json
    └── baseline_comparison.json
```

---

## External Dependencies (h-m1 Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_humaneval | `from data_loader import load_humaneval` | h-m1/code/data_loader.py |
| extract_poc_subset | `from data_loader import extract_poc_subset` | h-m1/code/data_loader.py |
| load_codellama | `from model_loader import load_codellama` | h-m1/code/model_loader.py |
| setup_device | `from model_loader import setup_device` | h-m1/code/model_loader.py |
| BeamCountLogger | `from beam_logger import BeamCountLogger` | h-m1/code/beam_logger.py |

**Verified from:** h-m1/code/ actual implementation  
**Reuse Strategy:** Copy h-m1 base modules (data_loader, model_loader) to h-m2/code/. Use flat structure with local imports.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| S-1 | Setup h-m2 environment | Copy h-m1 base modules, install deps | 3 | 1+0+0+2 |
| S-2 | AST validator with timing | Add timing instrumentation to validate_syntax | 5 | 1+0+2+2 |
| S-3 | Combined scoring function | Implement α*LL + β*validity formula | 6 | 2+1+2+1 |
| S-4 | Custom beam scorer | Integrate scoring into beam selection | 10 | 3+2+3+2 |
| S-5 | Experiment A+B runners | Latency measurement + ranking verification | 8 | 2+1+2+3 |
| S-6 | Experiment C ablation | α/β weight grid search on subset | 7 | 2+1+2+2 |
| S-7 | Baseline comparison | Run greedy + pure LL beam search | 6 | 2+1+1+2 |
| S-8 | Analysis pipeline | Compute stats, check gates, save results | 9 | 2+2+2+3 |

**Total Epic Tasks:** 8 (within MECHANISM range 6-12)  
**Total Complexity:** 54/160  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [S-4, S-8], Low(4-8): [S-2, S-3, S-5, S-6, S-7], VeryLow(1-3): [S-1]

---

## External Dependencies

### Python Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| transformers | >=4.30.0 | Beam search + model |
| torch | >=2.0.0 | Model inference |
| datasets | >=2.12.0 | HumanEval |
| numpy | >=1.24.0 | Statistics |
| pandas | >=2.0.0 | Log analysis |

### h-m1 Prerequisites

- CodeLlama-7B cached (from h-m1)
- HumanEval dataset downloaded (from h-m1)
- h-m1 validated k=5 beam maintenance

---

## Success Criteria

**System Complete When:**
1. All 8 Epic tasks implemented
2. AST parse mean latency <50ms (Experiment A)
3. Beam ranking correctness ≥80% (Experiment B)
4. At least one α/β pair achieves ranking target (Experiment C)
5. Combined scoring beats greedy baseline (syntax error rate)
6. All result files saved to results/

---

**Document Status:** Ready for Phase 4 Implementation
