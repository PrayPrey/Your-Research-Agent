# Config: H-E1-v2
**EvalPlus Failure Set Recovery Verification**

Applied: N/A — no relevant KB patterns found (CV-domain KB, unrelated to EvalPlus verification)

---

## Codebase Analysis

**Project Type**: green-field
**Status**: green-field — new single-script, no existing codebase to analyze
**Config Files Found**: None — new config design
**Pattern Used**: argparse + module-level constants (no dataclass needed)

---

## Constants

```python
# verify_h_e1_v2.py — top-level constants
EXPECTED_HE_FAILURES    = 34
EXPECTED_MBPP_FAILURES  = 100
EXPECTED_TOTAL_FAILURES = 134
EVALPLUS_VERSION        = "0.3.1"

ARCHIVE_FILES = {
    "he_eval":        "humaneval_samples_eval_results.json",
    "mbpp_eval":      "mbpp_samples_eval_results.json",
    "solutions_cache": "solutions_cache.jsonl",
}
```

---

## CLI Arguments (argparse)

```python
import argparse

def parse_args():
    p = argparse.ArgumentParser(description="Verify H-E1 failure set recovery")
    p.add_argument(
        "--archive",
        default="docs/youra_research/_archive/h-e1",
        help="Path to h-e1 results archive directory",
    )
    p.add_argument(
        "--output",
        default="docs/youra_research/h-e1-v2/results.json",
        help="Path for results.json output",
    )
    p.add_argument(
        "--figures",
        default="docs/youra_research/h-e1-v2/figures/",
        help="Directory for output figures",
    )
    p.add_argument(
        "--no-figure",
        action="store_true",
        help="Skip figure generation",
    )
    return p.parse_args()
```

---

## YAML Override Schema (optional)

```yaml
archive_path: "docs/youra_research/_archive/h-e1"
output_path: "docs/youra_research/h-e1-v2/results.json"
figures_dir: "docs/youra_research/h-e1-v2/figures/"
expected:
  he_failures: 34
  mbpp_failures: 100
  total: 134
evalplus_version: "0.3.1"
```

---

## Requirements

```
evalplus==0.3.1
matplotlib>=3.5.0
```
