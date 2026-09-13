# Configuration: H-M1

**Date:** 2026-08-19
**Hypothesis:** Observed coupling persists when controlling for instance difficulty (partial phi ≥ 0.25)
**Type:** MECHANISM

Applied: Statistical analysis config pattern (hardcoded dict for analysis parameters)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** h-e1 config verified from actual code
**Config Files Found:** docs/youra_research/h-e1_code/config.py
**Pattern Used:** Hardcoded dict (CONFIG)

---

## Inherited Configuration (Base Hypothesis)

### Config Fields (From Actual Code)

From: `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_buildingtrust/docs/youra_research/h-e1_code/config.py`

```python
# Reused from h-e1 (actual code):
CONFIG = {
    "dataset": {
        "name": "thu-ml/MultiTrust",
        "samples": 500,
        "seed": 42,
        "dimensions": ["truthfulness", "robustness", "fairness", "safety", "privacy"]
    },
    "statistical": {
        "phi_threshold": 0.3,
        "p_threshold": 0.01
    },
    "paths": {
        "data": "data/",
        "results": "results/",
        "figures": "figures/",
        "logs": "logs/"
    }
}
```

**Note:** h-m1 reuses dataset config and paths. Models not needed (uses pre-generated h-e1 coupling data).

---

## M-1: Difficulty Generation [Complexity: 7, Budget: 1]

**Applied:** Statistical simulation pattern (scipy distributions)

### Configuration (Hardcoded Dict)

```python
CONFIG = {
    # Inherited from h-e1
    "h_e1_path": "docs/youra_research/h-e1_code",
    "dataset": {
        "name": "thu-ml/MultiTrust",
        "samples": 500,
        "seed": 42,
        "dimensions": ["truthfulness", "robustness", "fairness", "safety", "privacy"]
    },
    
    # New: Difficulty generation
    "difficulty": {
        "distribution": "normal",
        "mean": 0.5,
        "std": 0.15,
        "clip_range": [0.0, 1.0],
        "seed": 42,
        "independence_threshold": 0.2  # Max |corr| with dimensions
    },
    
    # New: Partial correlation analysis
    "analysis": {
        "method": "pingouin",
        "partial_phi_threshold": 0.25,  # Gate criterion
        "n_quartiles": 4,
        "min_quartile_samples": 50,     # Validation: ≥50 per quartile
        "min_persistence_quartiles": 3  # Coupling in ≥3 quartiles
    },
    
    # Inherited paths
    "paths": {
        "data": "data/",
        "results": "results/",
        "figures": "figures/",
        "logs": "logs/"
    },
    
    # Gate validation (from PRD)
    "gate": {
        "min_pairs_passing": 2,          # ≥2 pairs with partial phi ≥ 0.25
        "partial_phi_threshold": 0.25,
        "quartile_persistence_threshold": 3
    }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Analysis Config | Single hardcoded dict for statistical analysis parameters |

---

## Usage Notes

**Data Flow:**
1. Load h-e1 coupling data from `h_e1_path/results/`
2. Generate difficulty scores: `np.random.normal(mean, std, size=samples)`
3. Clip to [0, 1] and validate independence
4. Run partial correlation (pingouin) + quartile stratification
5. Dual validation against gate criteria

**No Training:** This is statistical analysis only. All parameters are analysis settings, not learnable weights.

**Reproducibility:** Fixed `seed=42` for difficulty generation ensures exact replication.
