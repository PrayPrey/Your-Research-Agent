---
title: "Config: H-E1 - Alignment-Induced Brier Reliability Overconfidence"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3
tier: LIGHT
date: 2026-03-14
---

Applied: hardcoded-dict-poc (EXISTENCE PoC single fixed config; no domain KB match)

# Config: H-E1 — Alignment-Induced Brier Reliability Overconfidence

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze; no base hypothesis
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict

---

## A-4: Gate Evaluation + Validation Report [Complexity: 9, Budget: 2 subtasks]

### Configuration (Python — hardcoded dicts)

```python
# ── Calibration / metrics constants ──────────────────────────────────────────
CALIBRATION_CONFIG = {
    "n_bins": 15,
    "n_bootstrap": 1000,
    "seed": 42,
    "results_dir": "./results",
    "calibration_results_file": "calibration_results.json",
}

# ── Evaluation runner constants ───────────────────────────────────────────────
EVAL_CONFIG = {
    "batch_size": 8,
    "batch_size_fallback": 4,   # Non-standard: OOM fallback per NFR-2
    "num_fewshot": 0,
    "task": "mmlu",
    "dtype": "float16",
    "output_base": "./results",
}

# ── Gate condition ────────────────────────────────────────────────────────────
GATE_CONFIG = {
    "methods": ["ppo", "dpo"],
    "min_sizes_passing": 2,     # Non-standard: >=2/3 Pythia sizes required per MUST_WORK spec
    "sizes": ["1.4b", "2.8b", "6.9b"],
    "alignments": ["sft", "dpo", "ppo"],
}

# ── Validation report output ──────────────────────────────────────────────────
REPORT_CONFIG = {
    "output_path": "04_validation.md",
    "gate_result_path": "./results/gate_result.json",
    "sections": [
        "gate_result",
        "per_model_metrics_table",
        "key_findings",
        "failure_analysis",
        "mechanism_activation_indicators",
    ],
}

# ── Model registry: model_size x alignment -> HuggingFace ID ─────────────────
# Non-standard: aligned IDs are placeholders — verify from Li et al. 2024
# Appendix B before running (Risk R1). Fall back to LLaMA-2 family if unavailable.
MODEL_REGISTRY = {
    # Base models (confirmed public)
    "1.4b-base": "EleutherAI/pythia-1.4b",
    "2.8b-base": "EleutherAI/pythia-2.8b",
    "6.9b-base": "EleutherAI/pythia-6.9b",
    # Aligned models (verify HF IDs from Li et al. 2024 Appendix B)
    "1.4b-sft": "RLHFlow/pythia-1.4b-sft",
    "1.4b-dpo": "RLHFlow/pythia-1.4b-dpo",
    "1.4b-ppo": "RLHFlow/pythia-1.4b-ppo",
    "2.8b-sft": "RLHFlow/pythia-2.8b-sft",
    "2.8b-dpo": "RLHFlow/pythia-2.8b-dpo",
    "2.8b-ppo": "RLHFlow/pythia-2.8b-ppo",
    "6.9b-sft": "RLHFlow/pythia-6.9b-sft",
    "6.9b-dpo": "RLHFlow/pythia-6.9b-dpo",
    "6.9b-ppo": "RLHFlow/pythia-6.9b-ppo",
}
# CRITICAL (Risk R1): If RLHFlow IDs not found, search HF for pythia-*-{sft,dpo,ppo}
# referencing Li et al. 2024. Document any ID substitution in 04_validation.md.

# Flat ordered list for run_evaluation.sh iteration
MODEL_IDS = list(MODEL_REGISTRY.values())
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Gate + Registry Config | GATE_CONFIG, MODEL_REGISTRY, CALIBRATION_CONFIG, EVAL_CONFIG dicts |
| C-4-2 | Report Format Config | REPORT_CONFIG: output path, gate_result_path, and section list for 04_validation.md |

---

*Generated: Phase 3 Config Agent*
*Hypothesis: H-E1 (EXISTENCE, FOUNDATION, LIGHT tier)*
