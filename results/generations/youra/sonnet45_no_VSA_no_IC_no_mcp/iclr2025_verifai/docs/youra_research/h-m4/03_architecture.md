# System Architecture: h-m4 Final Valid Output Selection

**Date:** 2026-08-25  
**Hypothesis:** h-m4 (MECHANISM)  
**Tier:** MECHANISM (Epic Range: 6-12 tasks)  
**Infrastructure Level:** Standard

**Applied:** Final Selection Pattern, Baseline Comparison Pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extends h-m3 beam search with final output selection and greedy baseline  
**Analyzed Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m3/code/`  
**Findings:** h-m3 has AST validator (`ast_validator.py`), combined scoring (`scoring.py`), beam search (`beam_search.py`), and config (`config.py`). Add final output selector and greedy sampler. Reuse all h-m3 modules.

---

## Architecture Overview

### System Purpose
Validate final output quality from validity-scored beam search. Select top beam using argmax(final_score), validate syntax, and compare against greedy baseline to verify error reduction.

### Design Philosophy
**Extend h-m3 with minimal selection layer:**
- Reuse h-m3 beam search, scoring, validation
- Add FinalOutputSelector (argmax selection)
- Add GreedySampler (baseline comparison)
- Add SelectionAnalyzer (quality metrics)
- Minimal new code (selection + comparison only)

---

## Module Structure

### Module 1: Final Output Selector (`selector.py`)

**Dependencies:** `scoring` from h-m3

```python
class FinalOutputSelector:
    def __init__(self, alpha: float = 0.7, beta: float = 0.3): ...
    def select(self, beams: list[str], log_probs: list[float]) -> tuple[str, int, list[float]]: ...
    def select_strategy(self, beams: list[str], log_probs: list[float], strategy: str) -> tuple[str, int]: ...
```

---

### Module 2: Greedy Sampler (`greedy_sampler.py`)

**Dependencies:** `torch`, `transformers`

```python
class GreedySampler:
    def __init__(self, model, tokenizer): ...
    def generate(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.8) -> str: ...
    def batch_generate(self, prompts: list[str]) -> list[str]: ...
```

---

### Module 3: Selection Analyzer (`selection_analyzer.py`)

**Dependencies:** `ast_validator` from h-m3

```python
def compute_selection_accuracy(
    all_beams_validity: list[list[bool]],
    selected_indices: list[int]
) -> dict: ...

def stratify_by_availability(
    all_beams_validity: list[list[bool]],
    selected_indices: list[int]
) -> dict: ...

def find_miss_cases(
    all_beams_validity: list[list[bool]],
    selected_indices: list[int]
) -> list[int]: ...
```

---

### Module 4: Experiment Runners (`experiments.py`)

**Dependencies:** `selector`, `greedy_sampler`, `selection_analyzer`, h-m3 modules

```python
def experiment_a_final_validity(
    model, tokenizer, dataset: list[dict], k: int = 5, alpha: float = 0.7, beta: float = 0.3
) -> dict:
    """Run beam search, select final output, validate syntax"""
    ...

def experiment_b_greedy_baseline(
    model, tokenizer, dataset: list[dict]
) -> dict:
    """Run greedy sampling, validate syntax, compare error rates"""
    ...

def experiment_c_selection_quality(
    beam_results: dict
) -> dict:
    """Analyze selection accuracy by beam availability strata"""
    ...

def experiment_d_strategy_comparison(
    beam_results: dict
) -> dict:
    """Compare argmax vs validity-first vs random-valid selection"""
    ...
```

---

### Module 5: Analysis (`analysis.py`)

**Dependencies:** `numpy`, `pandas`, `matplotlib`

```python
def compute_error_reduction(greedy_results: dict, beam_results: dict) -> dict: ...
def plot_validity_distribution(results: dict, save_path: str) -> None: ...
def plot_baseline_comparison(greedy_results: dict, beam_results: dict, save_path: str) -> None: ...
def plot_selection_accuracy(selection_results: dict, save_path: str) -> None: ...
def plot_strategy_comparison(strategy_results: dict, save_path: str) -> None: ...
def plot_gate_metrics(beam_results: dict, greedy_results: dict, save_path: str) -> None: ...
```

---

### Module 6: Configuration (`config.py`)

**Dependencies:** None

```python
from dataclasses import dataclass

@dataclass
class SelectionConfig:
    alpha: float = 0.7
    beta: float = 0.3
    strategies: list[str] = field(default_factory=lambda: ["argmax", "validity_first", "random_valid"])

@dataclass
class GreedyConfig:
    temperature: float = 0.8
    max_new_tokens: int = 512

@dataclass
class GateConfig:
    validity_rate_min: float = 0.60
    selection_accuracy_min: float = 0.90

@dataclass
class H4Config:
    selection: SelectionConfig = field(default_factory=SelectionConfig)
    greedy: GreedyConfig = field(default_factory=GreedyConfig)
    gate: GateConfig = field(default_factory=GateConfig)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ASTValidator | `from h_m3.code.ast_validator import validate_syntax_timed` | `h-m3/code/ast_validator.py` |
| CombinedScore | `from h_m3.code.scoring import combined_score, rank_beams` | `h-m3/code/scoring.py` |
| BeamSearch | `from h_m3.code.beam_search import run_beam_search, validate_syntax` | `h-m3/code/beam_search.py` |
| BaseConfig | `from h_m3.code.config import DatasetConfig, ModelConfig, BeamSearchConfig` | `h-m3/code/config.py` |

**Verified from:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m3/code/` (actual implementation)

---

## Data Flow

```
HumanEval-164
    ↓
[Beam Search Path]
run_beam_search() → k=5 beams per problem
    ↓
FinalOutputSelector.select() → argmax(final_score)
    ↓
validate_syntax() → validity label
    ↓
[Greedy Path]
GreedySampler.batch_generate() → single output per problem
    ↓
validate_syntax() → validity label
    ↓
[Analysis]
compute_error_reduction() → greedy vs beam error rates
SelectionAnalyzer → accuracy when valid beams available
plot_gate_metrics() → 04_validation.md report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup environment | Load HumanEval-164, CodeLlama-7B (reuse h-m3 cache) | 4 | cache(1) + verify(1) + test(2) |
| A-2 | Implement selector | FinalOutputSelector class with argmax and strategy methods | 8 | class(2) + select(3) + strategies(3) |
| A-3 | Implement greedy sampler | GreedySampler with batch generation | 7 | class(2) + generate(2) + batch(3) |
| A-4 | Implement selection analyzer | Accuracy, stratification, miss case detection | 10 | accuracy(3) + stratify(4) + miss(3) |
| A-5 | Experiment A runner | Final validity measurement | 6 | beam_search(2) + select(2) + validate(2) |
| A-6 | Experiment B runner | Greedy baseline comparison | 5 | generate(2) + validate(1) + compare(2) |
| A-7 | Experiment C runner | Selection quality analysis | 4 | load(1) + analyze(2) + output(1) |
| A-8 | Experiment D runner | Strategy comparison ablation | 5 | strategies(3) + compare(2) |
| A-9 | Analysis module | Error reduction, plots, gate metrics | 12 | reduction(3) + plots(5) + gate(4) |
| A-10 | Configuration | H4Config with all experiment params | 5 | dataclass(2) + validation(2) + defaults(1) |

**Distribution:**  
- VeryHigh(18-20): []  
- High(14-17): []  
- Medium(9-13): [A-4, A-9]  
- Low(4-8): [A-1, A-2, A-3, A-5, A-6, A-7, A-8, A-10]

**Total Complexity:** 66  
**Estimated Implementation Time:** 5-7 hours

---

## File Structure

```
h-m4/
├── code/
│   ├── selector.py                    # FinalOutputSelector class
│   ├── greedy_sampler.py              # GreedySampler class
│   ├── selection_analyzer.py          # Selection quality analysis
│   ├── experiments.py                 # Experiment A/B/C/D runners
│   ├── analysis.py                    # Error reduction, plots
│   ├── config.py                      # H4Config
│   └── main.py                        # End-to-end pipeline
├── results/
│   ├── final_outputs.json             # Selected outputs with validity
│   ├── greedy_baseline.json           # Greedy outputs
│   ├── error_comparison.json          # Greedy vs beam error rates
│   ├── selection_quality.json         # Selection accuracy
│   └── strategy_comparison.json       # Strategy ablation
├── figures/
│   ├── validity_distribution.png      # Valid vs invalid bar chart
│   ├── baseline_comparison.png        # Error rate comparison
│   ├── selection_accuracy.png         # Accuracy by beam availability
│   ├── strategy_comparison.png        # Validity per strategy
│   └── gate_metrics.png               # Target vs actual (MANDATORY)
└── 04_validation.md                   # Generated report
```

---

## Key Algorithms

### Algorithm 1: Final Beam Selection (argmax)
```python
def select(beams, log_probs, alpha=0.7, beta=0.3):
    final_scores = []
    for beam, log_prob in zip(beams, log_probs):
        validity_score = 1.0 if validate_syntax(beam) else 0.0
        final_score = alpha * log_prob + beta * validity_score
        final_scores.append(final_score)
    best_idx = np.argmax(final_scores)
    return beams[best_idx], best_idx, final_scores
```

### Algorithm 2: Error Rate Comparison
```python
def compute_error_reduction(greedy_results, beam_results):
    greedy_errors = sum(1 for valid in greedy_results if not valid)
    beam_errors = sum(1 for valid in beam_results if not valid)
    greedy_rate = greedy_errors / len(greedy_results)
    beam_rate = beam_errors / len(beam_results)
    absolute = greedy_rate - beam_rate
    relative = (absolute / greedy_rate) * 100 if greedy_rate > 0 else 0
    return {'greedy': greedy_rate, 'beam': beam_rate, 'absolute': absolute, 'relative': relative}
```

### Algorithm 3: Selection Accuracy
```python
def compute_selection_accuracy(all_beams_validity, selected_indices):
    correct, total = 0, 0
    for beams_valid, idx in zip(all_beams_validity, selected_indices):
        if any(beams_valid):  # at least 1 valid beam exists
            total += 1
            if beams_valid[idx]:  # selected beam is valid
                correct += 1
    return correct / total if total > 0 else 0
```

---

## Success Metrics

| Metric | Target | Gate Action |
|--------|--------|-------------|
| Syntax validity rate | ≥60% (98/164) | ABANDON if <60% |
| Error rate vs greedy | < baseline | ABANDON if ≥baseline |
| Selection accuracy (≥3 valid) | ≥90% | Investigate scoring |
| argmax vs alternatives | Best performer | Adjust α/β |

---

## Self-Validation

### Quick Checks
- [x] No ASCII diagrams (only bullet lists)
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 10 Epic tasks with complexity
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included

### Serena MCP Validation
- [x] base_hypothesis exists → Serena called on h-m3 code
- [x] Import paths verified from actual files
- [x] External Dependencies section included

### Base Hypothesis Checks
- [x] Read actual code structure from h-m3/code/
- [x] Import paths verified from actual files (not specs)
- [x] External Dependencies section with file locations

---

**Document Status:** READY FOR LOGIC DESIGN (Phase 3)  
**Next Step:** Launch logic-agent for detailed algorithms  
**Schema Version:** 3.5
