# Configuration: H-E1

**Hypothesis**: lean-auto Baseline Measurement on miniF2F  
**Type**: EXISTENCE (PoC)  
**Date**: 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: green-field - new config design  
**Config Files Found**: None - theorem proving baseline (no prior code)  
**Pattern Used**: Hardcoded dict (minimal PoC config)

---

## Configuration Schema

### Evaluation Config (Hardcoded Dict)

```python
CONFIG = {
    "timeout_per_problem": 300,
    "n_workers": 8,
    "checkpoint_freq": 10,
    "pilot_size": 20,
    "error_threshold": 0.05,
    "retry_limit": 3
}
```

### Environment Versions (Git SHA Pinning)

```python
VERSIONS = {
    "lean": "4.15.0",
    "minif2f_sha": "TBD",  # Pin after pilot run
    "lean_auto_sha": "TBD",  # Pin after pilot run
    "z3": "latest"  # From system package
}
```

### lean-auto Settings

```lean
-- In evaluation script template
set_option auto.smt false
set_option auto.tptp false
set_option auto.native true  -- Native Duper backend
set_option trace.auto true
set_option trace.auto.mono true  -- For tactic count extraction
```

### Logging Schema

```python
RESULT_SCHEMA = {
    "problem_id": "str",
    "source": "str",  # AMC/AIME/IMO
    "outcome": "str",  # solved | timeout | error
    "time_s": "float",
    "tactic_count": "int | None",
    "trace_log": "str | None"
}
```

---

## Validation Gates

```python
GATES = {
    "completeness": {
        "min_evaluated": 244,  # All test problems
        "min_logged": 244
    },
    "quality": {
        "max_error_rate": 0.05,
        "min_tactic_capture": 0.80  # 80% of solved problems
    },
    "hypothesis": {
        "min_success_rate": 0.10,
        "max_success_rate": 0.25,
        "max_cv_tactic": 1.00  # Variance not excessive
    }
}
```

---

## Rationale (Non-Standard Only)

- **timeout=300s**: Theorem proving harder than code generation; AlphaProof used similar timeouts
- **n_workers=8**: Balances parallelism vs memory (16GB/worker for mathlib)
- **checkpoint_freq=10**: Recovery overhead vs lost work (10 problems = ~50min)
- **error_threshold=5%**: Infrastructure quality gate (lean-auto is stable)

