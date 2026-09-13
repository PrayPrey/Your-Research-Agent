---
title: "Logic: H-M1 - Base Calibration Verification"
hypothesis_id: h-m1
hypothesis_type: MECHANISM
phase: Phase 3
date: 2026-03-15
tier: FULL
---

Applied: custom pattern — Archon KB returned no relevant patterns (diffusion-focused KB)

# Logic: H-M1 — Base Calibration Verification (ECE_base < 0.15)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (read via Read tool — Serena project not activated)
**Analyzed Path**: `h-e1/code/calibration_analysis.py`, `h-e1/code/verify_gate.py`
**Findings**: Verified actual parameter names — `load_lmeval_samples(model_id, results_dir)`, `compute_ece(y_true, y_prob, n_bins)`, `compute_brier_decomposition(y_true, y_prob, n_bins)`. H-E1 verify_gate.py uses `evaluate_gate(results)` (not `evaluate_must_work_gate`) — H-M1 defines its own gate function with different semantics (ECE_base < 0.15 threshold, not delta_rel CI check).

---

## External Dependencies API (Base Hypothesis)

Signatures verified from `h-e1/code/calibration_analysis.py` (actual code, NOT spec):

```python
# From: h-e1/code/calibration_analysis.py

def load_lmeval_samples(
    model_id: str,             # e.g. "pythia-1.4b-base"
    results_dir: str = "./results",  # ← actual param name verified
) -> tuple[np.ndarray, np.ndarray]:
    """Glob results_dir/{model_id}/**/samples_mmlu*.jsonl.
    Returns: (logprobs: (N,4) float64, y_true: (N,) int64)
    """
    ...

def compute_ece(
    y_true: np.ndarray,   # (N,) int64 labels in {0,1,2,3}
    y_prob: np.ndarray,   # (N, 4) float64 softmax probabilities
    n_bins: int = 15,
) -> float:
    """Guo 2017 top-1 ECE. Returns scalar float in [0, 1]."""
    ...

def compute_brier_decomposition(
    y_true: np.ndarray,   # (N,) int64
    y_prob: np.ndarray,   # (N, 4) float64 softmax probabilities
    n_bins: int = 15,
) -> tuple[float, float, float]:
    """Murphy 1973. Returns: (reliability, resolution, uncertainty)."""
    ...

# Importable constants
BASE_MODEL_IDS: dict    # {"1.4b": "EleutherAI/pythia-1.4b", "2.8b": ..., "6.9b": ...}
CALIBRATION_CONFIG: dict  # {"n_bins": 15, "n_bootstrap": 1000, "seed": 42, ...}
MODELS: list[str]       # 12 entries: "pythia-{size}-{base|sft|dpo|ppo}"
```

**Import pattern (verified):**
```python
import sys
sys.path.insert(0, "../../h-e1/code/")
from calibration_analysis import (
    compute_ece, compute_brier_decomposition, load_lmeval_samples,
    BASE_MODEL_IDS, CALIBRATION_CONFIG,
)
from scipy.special import softmax
```

**Verified from**: actual `h-e1/code/calibration_analysis.py` (not 03_logic.md spec).

---

## M1-2: H-E1 Data Extraction (Path A) [Complexity: 10, Budget: 2 subtasks]

### API Signatures

```python
# h-m1/code/extract_h_e1_data.py

import re
import sys
import numpy as np
from pathlib import Path
from scipy.special import softmax

sys.path.insert(0, "../../h-e1/code/")
from calibration_analysis import compute_ece, load_lmeval_samples

BASE_SIZES = ["1.4b", "2.8b", "6.9b"]


def parse_h_e1_validation_report(
    validation_file: str,
) -> dict[str, float]:
    """Extract ECE_base for 3 Pythia base sizes from h-e1/04_validation.md.

    Returns: {"pythia-1.4b-base": float, "pythia-2.8b-base": float, "pythia-6.9b-base": float}
    Raises: FileNotFoundError if validation_file missing.
    Raises: ValueError if fewer than 3 base ECE values parseable.
    """
    # 1. text = Path(validation_file).read_text()
    # 2. For each size in ["1.4b", "2.8b", "6.9b"]:
    #      Try regex patterns in order:
    #        r"ece_base_" + re.escape(size) + r"[:\s=]+([0-9.]+)"
    #        r"pythia-" + re.escape(size) + r"-base.*?ECE.*?([0-9.]+)"
    #        table row: r"\|\s*pythia-" + re.escape(size) + r"-base\s*\|[^|]*\|\s*([0-9.]+)"
    #      parse float; validate 0.0 <= v <= 1.0
    # 3. If len(result) < 3: raise ValueError(f"Only {len(result)}/3 ECE_base found")
    # 4. return result
    ...


def reload_logprobs_from_results(
    h_e1_results_dir: str,
    n_bins: int = 15,
) -> dict[str, float]:
    """Load h-e1 JSONL logprobs for 3 base models and recompute ECE (Path A-extended).

    Uses load_lmeval_samples(model_id, results_dir) from h-e1/code/.
    Returns: {"pythia-1.4b-base": float, "pythia-2.8b-base": float, "pythia-6.9b-base": float}
    Raises: FileNotFoundError if any model_key produces 0 samples.
    """
    # ece_base = {}
    # for size in ["1.4b", "2.8b", "6.9b"]:
    #     model_key = f"pythia-{size}-base"
    #     logprobs, y_true = load_lmeval_samples(model_key, results_dir=h_e1_results_dir)
    #     if len(y_true) == 0:
    #         raise FileNotFoundError(f"No JSONL samples for {model_key} in {h_e1_results_dir}")
    #     y_prob = softmax(logprobs, axis=-1)   # (N, 4)
    #     ece_base[model_key] = compute_ece(y_true, y_prob, n_bins=n_bins)
    # return ece_base
    ...


def load_h_e1_ece_aligned(
    validation_file: str,
) -> dict[str, float]:
    """Parse h-e1/04_validation.md for aligned model ECE values (secondary metrics).

    Best-effort: returns partial dict if some values unavailable.
    Returns: {"pythia-{size}-{sft|dpo|ppo}": float, ...}
    """
    # table row regex for all 12 model keys
    # Return {} on FileNotFoundError or no matches (non-fatal)
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logprobs | (N, 4) | N ~ 14042 full MMLU |
| y_prob | (N, 4) | softmax(logprobs, axis=-1) |
| y_true | (N,) | int64, gold label 0-3 |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-2-1 | parse_h_e1_validation_report | Multi-pattern regex for ECE_base in 04_validation.md; validate [0,1]; raise ValueError if <3 found |
| L-M1-2-2 | reload_logprobs_from_results | load_lmeval_samples() per size; softmax; compute_ece(); raise FileNotFoundError if empty |

---

## M1-3: Path B Fallback lm-eval [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# h-m1/code/run_path_b.py

import subprocess
import sys
import os
import logging
from pathlib import Path
import numpy as np
from scipy.special import softmax

sys.path.insert(0, "../../h-e1/code/")
from calibration_analysis import compute_ece, load_lmeval_samples

logger = logging.getLogger(__name__)

BASE_HF_IDS = {
    "1.4b": "EleutherAI/pythia-1.4b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
}


def run_lmeval_base_model(
    size: str,
    output_dir: str,
    device: str = "cuda:0",
    batch_size: int = 8,
    n_bins: int = 15,
) -> float:
    """Run lm_eval CLI for one Pythia base model; return ECE.

    Retries with batch_size=4 on CalledProcessError containing 'CUDA out of memory'.
    Returns: ECE scalar float in [0, 1]
    Raises: RuntimeError if lm_eval fails after retry.
    """
    # model_key = f"pythia-{size}-base"
    # hf_id = BASE_HF_IDS[size]
    # model_out = os.path.join(output_dir, model_key)
    # os.makedirs(model_out, exist_ok=True)
    # cmd = ["lm_eval", "--model", "hf",
    #        "--model_args", f"pretrained={hf_id},dtype=float16",
    #        "--tasks", "mmlu", "--num_fewshot", "0",
    #        "--output_path", model_out + "/",
    #        "--log_samples", "--device", device,
    #        "--batch_size", str(batch_size)]
    # try:
    #     subprocess.run(cmd, check=True, timeout=7200)
    # except subprocess.CalledProcessError:
    #     if batch_size > 4:
    #         return run_lmeval_base_model(size, output_dir, device, batch_size=4, n_bins=n_bins)
    #     raise RuntimeError(f"lm_eval failed for {model_key}")
    # logprobs, y_true = load_lmeval_samples(model_key, results_dir=output_dir)
    # if len(y_true) == 0:
    #     raise RuntimeError(f"No samples after lm_eval for {model_key}")
    # y_prob = softmax(logprobs, axis=-1)
    # return compute_ece(y_true, y_prob, n_bins=n_bins)
    ...


def collect_path_b_results(
    output_dir: str,
    device: str = "cuda:0",
    n_bins: int = 15,
) -> dict[str, float]:
    """Sequential lm-eval execution for all 3 Pythia base model sizes.

    Returns: {"pythia-1.4b-base": float, "pythia-2.8b-base": float, "pythia-6.9b-base": float}
    Raises: RuntimeError if any size fails.
    """
    # ece_base = {}
    # for size in ["1.4b", "2.8b", "6.9b"]:
    #     logger.info("Path B: running lm_eval for pythia-%s-base ...", size)
    #     ece = run_lmeval_base_model(size, output_dir, device=device, n_bins=n_bins)
    #     ece_base[f"pythia-{size}-base"] = ece
    #     logger.info("pythia-%s-base ECE=%.4f", size, ece)
    # return ece_base
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-3-1 | run_lmeval_base_model | subprocess lm_eval CLI for single size; OOM retry batch 8->4; load JSONL; compute_ece |
| L-M1-3-2 | collect_path_b_results | Sequential loop over 3 sizes; aggregate into return dict; log ECE per size |

---

## M1-4: Gate Evaluation [Complexity: 9, Budget: 2 subtasks]

### API Signatures

```python
# h-m1/code/gate_and_report.py

import yaml
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

GATE_THRESHOLD = 0.15
BASE_SIZES = ["1.4b", "2.8b", "6.9b"]


def evaluate_must_work_gate(
    ece_base: dict[str, float],
    threshold: float = GATE_THRESHOLD,
) -> tuple[str, list[str]]:
    """MUST_WORK gate: ECE_base < threshold for ALL 3 Pythia base model sizes.

    Returns: ("PASS"|"FAIL", failed_model_ids)
    PASS iff len(failed_model_ids) == 0.
    """
    # failed = [k for k, v in ece_base.items() if v is None or v >= threshold]
    # return ("PASS" if not failed else "FAIL"), failed
    ...


def check_ece_ordering(
    ece_base: dict[str, float],
    ece_aligned: dict[str, float],
) -> dict[str, bool | None]:
    """Verify ECE_base < ECE_SFT for each size (secondary, non-gating).

    Returns: {"1.4b": bool|None, "2.8b": bool|None, "6.9b": bool|None}
    None if data unavailable for that size.
    """
    # ordering = {}
    # for size in ["1.4b", "2.8b", "6.9b"]:
    #     base_k = f"pythia-{size}-base"
    #     sft_k  = f"pythia-{size}-sft"
    #     if base_k in ece_base and sft_k in ece_aligned:
    #         ordering[size] = ece_base[base_k] < ece_aligned[sft_k]
    #     else:
    #         ordering[size] = None
    # return ordering
    ...


def verify_mechanism_activation(
    ece_base: dict[str, float],
) -> tuple[bool, dict]:
    """Validate all 3 ECE_base values are non-null floats in [0, 1].

    Returns: (valid: bool, indicators: dict)
    indicators keys: "all_present", "all_in_range", "n_valid", "values"
    Raises: ValueError if ece_base is empty or all values invalid.
    """
    # required = [f"pythia-{s}-base" for s in ["1.4b", "2.8b", "6.9b"]]
    # n_valid = sum(1 for k in required if isinstance(ece_base.get(k), float)
    #               and 0.0 <= ece_base[k] <= 1.0)
    # indicators = {
    #     "all_present": all(k in ece_base for k in required),
    #     "all_in_range": n_valid == 3,
    #     "n_valid": n_valid,
    #     "values": {k: ece_base.get(k) for k in required},
    # }
    # return indicators["all_in_range"], indicators
    ...


def generate_validation_report(
    ece_base: dict[str, float],
    ece_aligned: dict[str, float],
    gate_result: str,
    failed_checks: list[str],
    ordering: dict[str, bool | None],
    execution_path: str,
    output_path: str,
    figures_dir: str,
) -> None:
    """Write h-m1/04_validation.md with all required sections.

    Sections: metadata, gate_result, ece_table, secondary_metrics, figures, key_findings.
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-4-1 | evaluate_must_work_gate | Threshold check ECE < 0.15 for all 3 sizes; collect failed_model_ids; return ("PASS"/"FAIL", list) |
| L-M1-4-2 | check_ece_ordering | Per-size ECE_base < ECE_SFT check; returns dict[str, bool|None]; None if data missing |

---

## M1-7: Orchestrator [Complexity: 11, Budget: 2 subtasks]

### API Signatures

```python
# h-m1/code/run_experiment.py

import sys
import yaml
import logging
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, "../../h-e1/code/")
from calibration_analysis import compute_ece, load_lmeval_samples, CALIBRATION_CONFIG

from extract_h_e1_data import (
    parse_h_e1_validation_report,
    reload_logprobs_from_results,
    load_h_e1_ece_aligned,
)
from run_path_b import collect_path_b_results
from gate_and_report import (
    evaluate_must_work_gate, check_ece_ordering,
    verify_mechanism_activation, generate_validation_report,
)
from plot_results import generate_all_figures

logger = logging.getLogger(__name__)

H_E1_VALIDATION = "../../h-e1/04_validation.md"
H_E1_RESULTS_DIR = "../../h-e1/results"
H_M1_RESULTS_DIR = "./results"
H_M1_FIGURES_DIR = "./figures"
H_M1_REPORT_PATH = "../../04_validation.md"
VERIFICATION_STATE_PATH = "../../verification_state.yaml"


def dispatch_extraction_path(
    h_e1_validation: str = H_E1_VALIDATION,
    h_e1_results_dir: str = H_E1_RESULTS_DIR,
    h_m1_results_dir: str = H_M1_RESULTS_DIR,
    device: str = "cuda:0",
    n_bins: int = 15,
) -> tuple[dict[str, float], str]:
    """Try Path A (regex) -> Path A-extended (logprob reload) -> Path B (lm-eval).

    Returns: (ece_base: dict[str, float], execution_path: "A"|"A-extended"|"B")
    Raises: RuntimeError if all paths fail.
    """
    # Path A: regex parse of h-e1/04_validation.md
    # try:
    #     ece_base = parse_h_e1_validation_report(h_e1_validation)
    #     logger.info("Path A succeeded")
    #     return ece_base, "A"
    # except (FileNotFoundError, ValueError) as e:
    #     logger.warning("Path A failed: %s", e)
    #
    # Path A-extended: reload logprobs from h-e1/results/
    # try:
    #     ece_base = reload_logprobs_from_results(h_e1_results_dir, n_bins=n_bins)
    #     logger.info("Path A-extended succeeded")
    #     return ece_base, "A-extended"
    # except (FileNotFoundError, RuntimeError) as e:
    #     logger.warning("Path A-extended failed: %s", e)
    #
    # Path B fallback
    # logger.info("Activating Path B: re-running lm_eval for 3 base models")
    # ece_base = collect_path_b_results(h_m1_results_dir, device=device, n_bins=n_bins)
    # return ece_base, "B"
    ...


def write_gate_to_verification_state(
    gate_result: str,
    ece_base: dict[str, float],
    execution_path: str,
    verification_state_path: str = VERIFICATION_STATE_PATH,
) -> None:
    """Read verification_state.yaml, update h-m1 section, write back atomically.

    Sets: hypotheses.h-m1.gate_result, .gate_type, .ece_base, .execution_path, .updated_at
    Atomic write via .tmp rename to avoid corruption.
    """
    # state_path = Path(verification_state_path)
    # state = yaml.safe_load(state_path.read_text()) if state_path.exists() else {}
    # state.setdefault("hypotheses", {}).setdefault("h-m1", {}).update({
    #     "gate_result": gate_result,
    #     "gate_type": "MUST_WORK",
    #     "ece_base": ece_base,
    #     "execution_path": execution_path,
    #     "updated_at": datetime.utcnow().isoformat() + "Z",
    # })
    # tmp = state_path.with_suffix(".yaml.tmp")
    # tmp.write_text(yaml.dump(state, default_flow_style=False, allow_unicode=True))
    # tmp.replace(state_path)
    # logger.info("verification_state.yaml updated: h-m1 gate=%s", gate_result)
    ...


def main() -> None:
    """Full H-M1 pipeline: extract -> verify -> gate -> figures -> report -> yaml."""
    # 1. dispatch_extraction_path() -> ece_base, exec_path
    # 2. verify_mechanism_activation(ece_base)  # raises if invalid
    # 3. ece_aligned = load_h_e1_ece_aligned(H_E1_VALIDATION)
    # 4. gate_result, failed_checks = evaluate_must_work_gate(ece_base)
    # 5. ordering = check_ece_ordering(ece_base, ece_aligned)
    # 6. load logprobs_dict, y_true_dict for figure generation
    # 7. generate_all_figures(ece_base, ece_aligned, logprobs_dict, y_true_dict,
    #                          subject_labels=[], figures_dir=H_M1_FIGURES_DIR)
    # 8. generate_validation_report(ece_base, ece_aligned, gate_result, failed_checks,
    #                                ordering, exec_path, H_M1_REPORT_PATH, H_M1_FIGURES_DIR)
    # 9. write_gate_to_verification_state(gate_result, ece_base, exec_path)
    ...


if __name__ == "__main__":
    main()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-7-1 | dispatch_extraction_path | Try A (regex) -> A-extended (reload logprobs) -> B (subprocess); return (ece_base, path_label) |
| L-M1-7-2 | write_gate_to_verification_state | Read YAML; update h-m1 section with gate_result + ece_base; atomic .tmp rename write |

---

## Subtask Budget Summary

| Epic | Subtasks Used | Budget |
|------|--------------|--------|
| M1-2 | 2 | 2 |
| M1-3 | 2 | 2 |
| M1-4 | 2 | 2 |
| M1-7 | 2 | 2 |
| **Total** | **8** | **8** |

---

*Generated: Phase 3 Logic Agent*
*Hypothesis: H-M1 (MECHANISM, FULL tier) | Base: H-E1*
*Subtasks used: 8/8 (M1-2: 2, M1-3: 2, M1-4: 2, M1-7: 2)*
