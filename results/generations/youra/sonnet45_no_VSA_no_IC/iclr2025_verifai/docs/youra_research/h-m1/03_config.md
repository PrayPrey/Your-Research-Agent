# Configuration Specification: h-m1
# NL Hint Ablation Experiment

## Configuration Schema

All configuration values use Python dict format for copy-paste readiness.

---

## Dataset Configuration

```python
DATASET = {
    "name": "miniF2F-v2c",
    "repo": "roozbeh-yz/miniF2F_v2",
    "config": "v2c",
    "split": "test",
    "size": 244,
    "lean_version": "4.17.0"
}
```

**Field Descriptions**:
- `repo`: HuggingFace dataset identifier
- `config`: Dataset configuration name (v2c = version 2c)
- `split`: test split (244 problems)
- `lean_version`: Lean 4.17.0 required for miniF2F-v2c

---

## LeanCopilot Configuration

```python
LEANCOPILOT = {
    "model": "ReProver",
    "tactic": "search_proof",
    "sampling_budget": 32,
    "timeout": 300,
    "max_concurrent_proofs": 8
}
```

**Field Descriptions**:
- `sampling_budget`: Number of proof search attempts per problem (@32 sampling)
- `timeout`: Maximum time per problem in seconds (5 minutes)
- `max_concurrent_proofs`: Parallel workers for evaluation (8 workers)

**Valid Ranges**:
- `sampling_budget`: 1-128 (32 is standard for miniF2F)
- `timeout`: 60-600 seconds (300s is dataset default)
- `max_concurrent_proofs`: 1-16 (limited by GPU memory)

---

## Ablation Configuration

```python
ABLATION = {
    "strip_docstrings": True,
    "strip_inline_comments": True,
    "preserve_theorem_structure": True,
    "docstring_pattern": r'/--!.*?-/',
    "comment_pattern": r'--[^\n]*'
}
```

**Field Descriptions**:
- `strip_docstrings`: Remove `/--! ... -/` blocks
- `strip_inline_comments`: Remove `-- ...` comments
- `preserve_theorem_structure`: Keep theorem declarations and type signatures
- Patterns are Python regex for preprocessing

---

## Pilot Configuration

```python
PILOT = {
    "sample_size": 20,
    "random_seed": 42,
    "go_criteria": {
        "max_type_check_failures": 3,
        "min_measurable_effect": 0.05
    }
}
```

**Field Descriptions**:
- `sample_size`: Number of problems for pilot validation (20)
- `go_criteria.max_type_check_failures`: Threshold for NL ablation quality (≤3 failures)
- `go_criteria.min_measurable_effect`: Minimum delta to proceed (≥5%)

**Go/No-Go Logic**:
- PASS: type_check_failures ≤ 3 AND delta ≥ 0.05
- FAIL: escalate to fallback (external Mathlib docs removal)

---

## Statistical Configuration

```python
STATISTICAL = {
    "test": "mcnemar",
    "alpha": 0.05,
    "power": 0.80,
    "confidence_interval": 0.95,
    "bootstrap_resamples": 10000,
    "random_seed": 42
}
```

**Field Descriptions**:
- `test`: McNemar's test for paired binary outcomes
- `alpha`: Significance level (0.05)
- `power`: Statistical power (0.80)
- `bootstrap_resamples`: Number of resamples for CI estimation (10k)

**Validation Criteria**:
- Primary: 0.25 ≤ delta ≤ 0.35 AND p < 0.05
- Falsification: delta < 0.10 OR p ≥ 0.05

---

## Execution Configuration

```python
EXECUTION = {
    "random_seed": 42,
    "output_dir": "results/h-m1",
    "checkpoint_interval": 50,
    "log_level": "INFO"
}
```

**Field Descriptions**:
- `random_seed`: Reproducibility seed (42)
- `checkpoint_interval`: Save progress every N problems (50)
- `log_level`: Python logging level (INFO for production)

---

## Environment Variables

```bash
# GPU allocation
export CUDA_VISIBLE_DEVICES=0

# Output paths
export HM1_OUTPUT_DIR=/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_verifai/results/h-m1
export HM1_CACHE_DIR=/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_verifai/.cache

# Reproducibility
export PYTHONHASHSEED=42
export LEAN_PATH=/home/PrayPrey/.elan/toolchains/leanprover-lean4-4.17.0
```

**Note**: Adjust CUDA_VISIBLE_DEVICES based on GPU availability.

---

## Complete Configuration Module

```python
# config.py - Copy-paste ready configuration for h-m1

DATASET = {
    "name": "miniF2F-v2c",
    "repo": "roozbeh-yz/miniF2F_v2",
    "config": "v2c",
    "split": "test",
    "size": 244,
    "lean_version": "4.17.0"
}

LEANCOPILOT = {
    "model": "ReProver",
    "tactic": "search_proof",
    "sampling_budget": 32,
    "timeout": 300,
    "max_concurrent_proofs": 8
}

ABLATION = {
    "strip_docstrings": True,
    "strip_inline_comments": True,
    "preserve_theorem_structure": True,
    "docstring_pattern": r'/--!.*?-/',
    "comment_pattern": r'--[^\n]*'
}

PILOT = {
    "sample_size": 20,
    "random_seed": 42,
    "go_criteria": {
        "max_type_check_failures": 3,
        "min_measurable_effect": 0.05
    }
}

STATISTICAL = {
    "test": "mcnemar",
    "alpha": 0.05,
    "power": 0.80,
    "confidence_interval": 0.95,
    "bootstrap_resamples": 10000,
    "random_seed": 42
}

EXECUTION = {
    "random_seed": 42,
    "output_dir": "results/h-m1",
    "checkpoint_interval": 50,
    "log_level": "INFO"
}

# Derived constants
TOTAL_COMPARISONS = DATASET["size"] * 2  # 244 baseline + 244 ablated = 488
ESTIMATED_RUNTIME_HOURS = (TOTAL_COMPARISONS * LEANCOPILOT["timeout"]) / (
    LEANCOPILOT["max_concurrent_proofs"] * 3600
)  # ~41 hours
```

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dict (consistent with existing h-e1 config.py)

Applied: Standard experimental config pattern from archived h-e1.
