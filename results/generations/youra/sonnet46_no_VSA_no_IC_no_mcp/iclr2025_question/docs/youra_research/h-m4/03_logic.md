---
hypothesis_id: h-m4
phase: logic
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Logic: H-M4 — Verbalized Confidence (VC) Uncertainty Estimation

Applied: single-script-inference-with-cached-baselines, bootstrap-auroc-reuse-from-h-m2

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m3)
**Status**: API signatures verified from actual h-m3 code
**Analyzed Path**: `docs/youra_research/h-m3/code/evaluate.py`
**Relevant Symbols**:
- `load_bootstrap_auroc(hm2_code_dir: str)` — loads fn via importlib
- `bootstrap_auroc(scores, labels, n_bootstrap, seed) -> (float, float, float)` — verified from h-m3 call at line 32

---

## External Dependencies API

```python
# From: h-m3/code/evaluate.py (ACTUAL CODE, lines 6-34)
def load_bootstrap_auroc(hm2_code_dir: str):
    """Returns bootstrap_auroc callable from h-m2/code/evaluate.py."""
    ...

# bootstrap_auroc (from h-m2, called via load_bootstrap_auroc):
bootstrap_auroc(
    scores: list[float],  # uncertainty scores [N]
    labels: list[int],    # binary EM labels [N]
    n_bootstrap: int,     # 1000
    seed: int,            # 42
) -> tuple[float, float, float]  # (auroc_mean, ci_lo, ci_hi)
```

---

## A-4: VC Inference [Complexity: 12, Budget: 2 subtasks]

Applied: Llama-2-Chat prompt template, 3-pattern regex cascade

### L-4-1: build_vc_prompt()

```python
SYSTEM_PROMPT = (
    "You are a helpful and honest assistant. "
    "When answering, provide your answer and then state your confidence "
    "as a percentage (0-100%)."
)

def build_vc_prompt(question: str) -> str:
    """Build Llama-2-Chat [INST]...[/INST] prompt. Returns str."""
    user_content = (
        f"Question: {question}\n\n"
        "Please provide:\n"
        "1. Your answer\n"
        "2. Your confidence in your answer as a percentage (0-100%)\n\n"
        "Format: Answer: <your answer>\nConfidence: <number>%"
    )
    return (
        f"[INST] <<SYS>>\n{SYSTEM_PROMPT}\n<</SYS>>\n\n"
        f"{user_content} [/INST]"
    )
```

### L-4-2: extract_confidence()

```python
import re

def extract_confidence(response: str) -> tuple[float, bool]:
    """
    3-pattern regex cascade. Returns (confidence_0_1, parsed: bool).
    Fallback: (0.5, False).
    """
    # Pattern 1: "Confidence: 85%" or "Confidence: 85.5%"
    m = re.search(r"[Cc]onfidence[:\s]+(\d+(?:\.\d+)?)\s*%", response)
    if m:
        val = float(m.group(1))
        return min(max(val / 100.0, 0.0), 1.0), True

    # Pattern 2: standalone "85%" anywhere in response
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*%", response)
    if m:
        val = float(m.group(1))
        return min(max(val / 100.0, 0.0), 1.0), True

    # Pattern 3: "I am 85 percent confident"
    m = re.search(r"\b(\d+(?:\.\d+)?)\s+percent", response, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        return min(max(val / 100.0, 0.0), 1.0), True

    return 0.5, False
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | build_vc_prompt | Llama-2-Chat [INST] template with system prompt and confidence instruction |
| L-4-2 | extract_confidence | 3-pattern regex cascade with clamp and fallback |

---

## A-6: AUROC Evaluation [Complexity: 10, Budget: 2 subtasks]

Applied: bootstrap-auroc-reuse-from-h-m2, 10-bin ECE histogram

### L-6-1: compute_vc_auroc()

```python
def compute_vc_auroc(
    vc_uncertainties: list[float],  # [N] uncertainty = 1 - confidence
    em_labels: dict,                # {question_str: int} or {idx: int}
    cfg: "Config",
) -> dict:
    """
    Bootstrap AUROC for VC. Returns dict with auroc, CI, gate results, ECE.
    """
    bootstrap_auroc = load_bootstrap_auroc(cfg.hm2_code_dir)

    # Align labels to vc_uncertainties order (positional)
    qids = list(em_labels.keys())
    labels = [em_labels[q] for q in qids]
    # vc_uncertainties assumed to be in same positional order as qids
    scores = vc_uncertainties  # [N]

    auroc_vc, ci_lo, ci_hi = bootstrap_auroc(scores, labels, cfg.n_bootstrap, cfg.seed)

    # Confidences for ECE (inverse of uncertainty)
    vc_confidences = [1.0 - u for u in vc_uncertainties]
    ece = compute_ece(vc_confidences, em_labels)

    gate_vc_lt_te = auroc_vc < cfg.auroc_te_baseline  # < 0.4381
    gate_vc_lt_se = auroc_vc < cfg.auroc_se_baseline  # < 0.286
    gate_passed = gate_vc_lt_te and gate_vc_lt_se

    return {
        "auroc_vc": auroc_vc,
        "auroc_vc_ci": [ci_lo, ci_hi],
        "auroc_te": cfg.auroc_te_baseline,
        "auroc_se": cfg.auroc_se_baseline,
        "delta_te": abs(auroc_vc - cfg.auroc_te_baseline),
        "delta_se": abs(auroc_vc - cfg.auroc_se_baseline),
        "gate_vc_lt_te": gate_vc_lt_te,
        "gate_vc_lt_se": gate_vc_lt_se,
        "gate_passed": gate_passed,
        "ece": ece,
    }
```

### L-6-2: compute_ece()

```python
import numpy as np

def compute_ece(
    confidences: list[float],  # [N] in [0, 1]
    em_labels: dict,           # {key: int} — same positional order as confidences
    n_bins: int = 10,
) -> float:
    """10-bin ECE. Returns scalar float."""
    confs = np.array(confidences)           # [N]
    labels = np.array(list(em_labels.values()), dtype=float)  # [N]
    N = len(confs)

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)  # [11]
    ece = 0.0

    for i in range(n_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        # include right edge in last bin
        if i < n_bins - 1:
            mask = (confs >= lo) & (confs < hi)
        else:
            mask = (confs >= lo) & (confs <= hi)

        bin_count = mask.sum()
        if bin_count == 0:
            continue

        bin_conf = confs[mask].mean()      # mean predicted confidence
        bin_acc = labels[mask].mean()      # fraction correct
        ece += (bin_count / N) * abs(bin_acc - bin_conf)

    return float(ece)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | compute_vc_auroc | Bootstrap AUROC + gate logic (VC < TE, VC < SE) + ECE call |
| L-6-2 | compute_ece | 10-bin weighted ECE with edge-inclusive last bin |
