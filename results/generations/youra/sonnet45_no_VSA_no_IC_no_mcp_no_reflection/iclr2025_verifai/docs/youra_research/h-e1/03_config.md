# Configuration: h-e1 SMT Constraint Extraction

**Date:** 2026-08-28
**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Author:** Phase 3 Configuration Agent

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new config schema
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict (PoC simplicity)

---

## Configuration Schema

**Format**: Hardcoded dict (PoC - single fixed config)

```python
# config.py - Complete PoC configuration

CONFIG = {
    # Dataset
    "dataset": {
        "name": "openai_humaneval",
        "subset_size": 100,
        "output_dir": "data/humaneval_pydantic"
    },
    
    # LLM Generation
    "llm": {
        "model": "claude-sonnet-3-5-20240620",
        "temperature": 0.2,
        "max_tokens": 512,
        "system_prompt": "Generate typed Python code using Pydantic BaseModel. Include @validator decorators for preconditions. Do not use eval, exec, or metaprogramming.",
        "api_rate_limit": 10,  # requests/minute
        "retry_max": 3
    },
    
    # Constraint Extraction
    "extraction": {
        "tool": "pyre-check",
        "output_format": "json",
        "command": "pyre analyze --output-format json"
    },
    
    # Quality Verification
    "quality": {
        "solver": "z3-solver",
        "timeout_ms": 5000,
        "threshold": 80  # % non-trivial constraints
    },
    
    # Metrics & Gates
    "metrics": {
        "extraction_rate_threshold": 90,  # %
        "quality_rate_threshold": 80,     # %
        "gate_type": "MUST_WORK"
    },
    
    # Paths
    "paths": {
        "data_dir": "data/humaneval_pydantic",
        "generated_code_dir": "outputs/generated_code",
        "constraints_dir": "outputs/constraints",
        "metrics_file": "outputs/metrics.json",
        "figures_dir": "figures"
    },
    
    # Environment
    "env": {
        "anthropic_api_key": "ANTHROPIC_API_KEY"  # env var name
    },
    
    # Dependencies (pip install)
    "dependencies": {
        "pyre-check": "latest",
        "z3-solver": "latest",
        "anthropic": "latest",
        "datasets": "latest",
        "pydantic": "latest",
        "matplotlib": "latest"
    }
}
```

---

## Environment Variables

**Required**:
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude Sonnet 3.5 access

**Setup**:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

---

## Dependencies

**Installation**:
```bash
pip install pyre-check z3-solver anthropic datasets pydantic matplotlib
```

**Versions**: Latest stable (PoC - no version pinning needed)

---

## File Structure

```
h-e1/
  data/humaneval_pydantic/          # Dataset output
  outputs/
    generated_code/                 # LLM code output
    constraints/                    # Extraction results (JSON)
    metrics.json                    # Final metrics
  figures/                          # Visualizations
    gate_metrics.png                # Mandatory
    success_by_complexity.png
    constraint_types.png
    failure_modes.png
```

---

## Usage (Phase 4 Copy-Paste)

```python
from config import CONFIG

# Access config values
dataset_name = CONFIG["dataset"]["name"]
llm_model = CONFIG["llm"]["model"]
extraction_threshold = CONFIG["metrics"]["extraction_rate_threshold"]

# Environment variable
import os
api_key = os.environ[CONFIG["env"]["anthropic_api_key"]]
```

---

## Rationale

**Non-standard values**:
- `temperature: 0.2` - Research default for deterministic code generation (vs 0.7 creative tasks)
- `timeout_ms: 5000` - Z3 solver timeout for 10-50 LOC programs (100ms typical, 5s safety margin)
- `subset_size: 100` - PoC validation subset (vs full 164 HumanEval problems)

All other values are standard from tool documentation.

---

**Self-Validation**:
- [x] Single format (hardcoded dict only)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Ready for copy-paste in Phase 4
