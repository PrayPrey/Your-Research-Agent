# Configuration Specification: H-M3
# Random Mathlib Tactic Sampling Baseline

**Hypothesis ID:** h-m3  
**Date:** 2026-08-20  
**Phase:** 3 Implementation Planning  
**Type:** PoC (EXISTENCE hypothesis)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: Green-field project - designing new config schema  
**Config Files Found**: None - new config  
**Pattern Used**: YAML config file + Python validation

---

## Configuration Schema

### Primary Config (YAML)

```yaml
# h_m3_config.yaml
experiment:
  hypothesis_id: h-m3
  name: Random Mathlib Tactic Sampling Baseline
  seed: 42

tactic_distribution:
  simp: 0.35
  rfl: 0.15
  intro: 0.08
  intros: 0.04
  cases: 0.06
  induction: 0.04
  ring: 0.04
  linarith: 0.02
  omega: 0.02
  norm_num: 0.03
  apply: 0.07
  constructor: 0.03
  exact: 0.04
  have: 0.02
  calc: 0.01

proof_search:
  budget: 15
  timeout_seconds: 300
  goal_selection: random
  rng_seeding: deterministic

evaluation:
  dataset: minif2f_test
  problem_count: 244
  workers: 8
  memory_mb_per_worker: 16384

logging:
  per_problem_file: h_m3_results.jsonl
  aggregate_file: h_m3_aggregate.yaml
  console_progress: true
  
  fields:
    - problem_id
    - source
    - outcome
    - wall_clock_time
    - tactics_used
    - tactic_sequence
    - rng_seed
```

### Validation Rules (Python)

```python
# config_validator.py
def validate_config(config: dict) -> None:
    """Validate H-M3 configuration."""
    
    # Tactic weights must sum to 1.0
    weights = config['tactic_distribution']
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, expected 1.0"
    
    # All weights positive
    assert all(w > 0 for w in weights.values()), "Negative weight found"
    
    # Budget positive
    assert config['proof_search']['budget'] > 0, "Budget must be positive"
    
    # Timeout positive
    assert config['proof_search']['timeout_seconds'] > 0, "Timeout must be positive"
    
    # Workers positive
    assert config['evaluation']['workers'] > 0, "Workers must be positive"
    
    # Goal selection valid
    assert config['proof_search']['goal_selection'] in ['random', 'first'], \
        "Invalid goal_selection"
    
    # RNG seeding valid
    assert config['proof_search']['rng_seeding'] in ['deterministic', 'random'], \
        "Invalid rng_seeding"
```

---

## Parameter Rationale

### Tactic Distribution

**Source**: Empirical Mathlib corpus analysis from literature (LeanDojo 2023, Structured Hints 2026).

**Top 5 tactics**:
- `simp` (35%): Most common Mathlib simplifier
- `rfl` (15%): Reflexivity, common proof closer
- `intro`/`intros` (12%): Hypothesis introduction
- `cases`/`induction` (10%): Structural case analysis
- `ring`/`linarith`/`omega` (8%): Algebraic automation

**Validation**: Spot-check 10 random Mathlib files expected to show ±10% variance.

### Proof Search Parameters

**Budget: 15 evaluations**
- H-E1 measured mean=9.2±4.1 tactics per solved problem
- 15 provides buffer above mean (1.4σ)
- Prevents premature exhaustion while avoiding excessive computation

**Timeout: 300 seconds**
- Reuses H-E1 infrastructure value
- Aligned with lean-auto baseline for fair comparison
- Prevents infinite loops on unsolvable problems

**Goal selection: random**
- When tactic produces multiple subgoals, pick randomly
- Simpler than semantic ordering (no heuristics)
- Tests pure corpus frequency effect

**RNG seeding: deterministic**
- Use problem index as seed
- Guarantees reproducibility on rerun
- 10% subset validation ensures exact match

### Evaluation Settings

**Workers: 8 parallel**
- Reuses H-E1 infrastructure
- 244 problems @ 300s timeout = 20h sequential → 2.5h parallel
- Memory budget: 8 workers × 16GB = 128GB total

**Dataset: miniF2F test (244 problems)**
- Standard benchmark, reuses H-E1 setup
- No validation split needed for baseline
- Stratification by source (AMC/AIME/IMO) optional

### Logging Configuration

**Per-problem JSONL**:
```json
{
  "problem_id": "minif2f_test_001",
  "source": "AMC",
  "outcome": "solved",
  "wall_clock_time": 12.3,
  "tactics_used": 8,
  "tactic_sequence": ["simp", "intro", "rfl", "..."],
  "rng_seed": 0
}
```

**Aggregate YAML**:
```yaml
success_rate: 0.20
ci_95: [0.153, 0.255]
solved_count: 49
delta_vs_lean_auto: 0.044
z_statistic: 2.13
p_value: 0.017
```

---

## Reproducibility Guarantees

### Seeding Strategy

```python
def get_problem_seed(problem_index: int, base_seed: int = 42) -> int:
    """Deterministic seed per problem."""
    return base_seed + problem_index
```

**Properties**:
- Each problem gets unique seed
- Rerun with same base_seed produces identical results
- Independent of execution order (parallelism safe)

### Deterministic Execution

**Requirements**:
- Lean 4.15.0 (pinned version)
- Mathlib cache (fixed snapshot)
- RNG state tracked per problem
- Tactic application order deterministic

**Validation**:
- Rerun 10% subset (24 problems)
- Expected: 100% match on outcome + tactic sequence
- If match_rate < 1.0, investigate non-determinism source

---

## Environment Variables

```bash
# evaluate_h_m3.sh
export LEAN_VERSION="4.15.0"
export MINIF2F_PATH="/path/to/miniF2F"
export CONFIG_PATH="./h_m3_config.yaml"
export RESULTS_PATH="./results/h_m3/"
export WORKERS=8
export TIMEOUT=300
```

**Separation of concerns**:
- **Config file**: Experiment parameters (tactics, budget, logging)
- **Environment**: Infrastructure paths (Lean version, dataset location)
- **Command-line**: Runtime overrides (workers, timeout)

---

## Example Configurations

### Default (PoC)

```yaml
# h_m3_config.yaml (default from above)
proof_search:
  budget: 15
  timeout_seconds: 300
```

**Use case**: Primary experiment run (18-25% target).

### Ablation: Budget Sensitivity (Optional)

```yaml
# h_m3_config_budget10.yaml
proof_search:
  budget: 10
  timeout_seconds: 300

# h_m3_config_budget20.yaml
proof_search:
  budget: 20
  timeout_seconds: 300
```

**Use case**: Test sensitivity to budget parameter (optional analysis).

### Ablation: Uniform Distribution (Optional)

```yaml
# h_m3_config_uniform.yaml
tactic_distribution:
  simp: 0.067
  rfl: 0.067
  intro: 0.067
  # ... all 15 tactics equal weight
```

**Use case**: Compare corpus frequency vs uniform random (optional control).

---

## Statistical Analysis Configuration

```python
# analyze_h_m3.py configuration
ANALYSIS_CONFIG = {
    'baseline': {
        'name': 'H-E1 lean-auto',
        'success_count': 38,
        'total_problems': 244,
        'success_rate': 0.156
    },
    
    'statistical_test': {
        'test': 'one_proportion_z_test',
        'alternative': 'greater',
        'alpha': 0.05
    },
    
    'confidence_interval': {
        'method': 'wilson',
        'level': 0.95
    },
    
    'stratification': {
        'enabled': True,
        'field': 'source',
        'categories': ['AMC', 'AIME', 'IMO']
    }
}
```

---

## Configuration Loading

```python
# load_config.py
import yaml
from pathlib import Path

def load_h_m3_config(path: str = 'h_m3_config.yaml') -> dict:
    """Load and validate H-M3 configuration."""
    with open(path) as f:
        config = yaml.safe_load(f)
    
    validate_config(config)
    return config

# Usage in Lean evaluator
config = load_h_m3_config()
tactics = list(config['tactic_distribution'].keys())
weights = list(config['tactic_distribution'].values())
budget = config['proof_search']['budget']
```

---

## Success Criteria Thresholds

```yaml
# Embedded in config for Phase 4 validation
success_criteria:
  success_rate:
    min: 0.18
    max: 0.25
    predicted: 0.20
  
  delta_vs_baseline:
    min: 0.03
    max: 0.10
    predicted: 0.044
  
  statistical_significance:
    p_value_max: 0.05
    test: one_sided_z_test
    
  quality_gates:
    error_rate_max: 0.05
    rerun_match_rate_min: 1.00
```

---

## Parameter Summary Table

| Category | Parameter | Value | Source | Rationale |
|----------|-----------|-------|--------|-----------|
| Tactics | simp | 0.35 | LeanDojo 2023 | Most common simplifier |
| Tactics | rfl | 0.15 | Literature | Reflexivity proof closer |
| Tactics | intro/intros | 0.12 | Mathlib | Hypothesis introduction |
| Proof Search | budget | 15 | H-E1 | 1.4σ above measured mean=9.2 |
| Proof Search | timeout | 300s | H-E1 | Infrastructure baseline |
| Proof Search | goal_selection | random | Design | Pure frequency test |
| Proof Search | rng_seeding | deterministic | Reproducibility | problem_index → seed |
| Evaluation | workers | 8 | H-E1 | Parallel infrastructure |
| Evaluation | dataset | miniF2F test | Benchmark | 244 problems |
| Logging | format | JSONL+YAML | Standard | Per-problem + aggregate |
| Reproducibility | seed | 42 | Convention | Base RNG seed |

---

## Configuration File Locations

```
h-m3/
├── h_m3_config.yaml              # Primary config
├── config_validator.py           # Validation logic
├── load_config.py               # Config loader
├── evaluate_h_m3.sh             # Shell wrapper (env vars)
└── results/
    ├── h_m3_results.jsonl       # Per-problem output
    └── h_m3_aggregate.yaml      # Aggregate statistics
```

---

## Notes

**Applied**: PyTorch reproducibility patterns (deterministic RNG, seed management).

**PoC Simplification**: No hyperparameter grid, no ablation configs in primary experiment (optional for sensitivity analysis).

**Validation**: 10% subset rerun guarantees deterministic execution.
