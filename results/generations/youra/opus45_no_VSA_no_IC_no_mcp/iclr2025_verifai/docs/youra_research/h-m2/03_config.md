# Configuration: H-M2 (MECHANISM)

**Applied**: Hardcoded-dict experiment config pattern (matches H-E1 precedent, McNemar paired-binary evaluation config)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: Serena unavailable — read `h-e1/code/config.py` directly via file tool.
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` — plain `CONFIG` dict (no dataclass), plus `OPENAI_API_KEY` from env.
**Pattern Used**: Hardcoded dict (verified from H-E1 actual code; H-M2 follows same pattern per architecture spec).

---

## M2-1: config.py [Complexity: 5, Budget: 0 subtasks]

**Applied**: Hardcoded-dict pattern (single fixed PoC config, no tuning/grid)

### Configuration (Hardcoded Dict)

```python
CONFIG = {
    "base_model_id": "codellama/CodeLlama-7b-Instruct-hf",
    "temperature": 0.8,
    "top_p": 0.95,
    "max_new_tokens": 512,
    "min_samples": 500,
    "bootstrap_replicas": 10000,
    "significance_alpha": 0.05,
    "sections": ["PROBLEM", "LOCATION", "CONTEXT", "ROOT_CAUSE"],
    "exec_timeout_sec": 5,
    "seed": 42,
    "torch_dtype": "float16",
    "device_map": "auto",
    "failed_samples_path": "data/failed_samples.json",
    "results_path": "data/paired_results.json",
    "figures_dir": "outputs/figures/",
}
```

No hyperparameter grid — mechanism gate uses a single fixed run (temperature/top_p from PRD FR-3.2, min_samples/bootstrap_replicas/alpha from PRD FR-1.3/FR-4.3/success criteria). `seed` added (not in architecture snippet) for global reproducibility per NFR-3; per-sample scramble seeds are derived separately in `sections.py`/`dataset.py` (e.g., `seed + sample_index`), not stored in `CONFIG`.

### Subtasks [0/0 used]
No breakdown — task is a single flat dict, no decomposition needed within a 0-subtask budget.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
CONFIG = {
    "temperature": 0.0,
    "max_new_tokens": 512,
    "seed": 42,
    "torch_dtype": "float16",
    "device_map": "auto",
    "exec_timeout_sec": 3.0,
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
```

H-E1 uses a dict, not a dataclass — H-M2 must NOT introduce a dataclass to stay consistent (no format mixing).

### Extended Config (Current Hypothesis)

H-M2's `CONFIG` is a fresh dict (not inheriting via Python subclassing, since H-E1 uses a plain dict). Overridden/new fields vs H-E1:

| Field | H-E1 value | H-M2 value | Reason |
|-------|-----------|------------|--------|
| `temperature` | 0.0 (greedy, initial gen) | 0.8 | PRD FR-3.2 repair uses sampling |
| `top_p` | — | 0.95 | new field, PRD FR-3.2 |
| `exec_timeout_sec` | 3.0 | 5 | slightly higher timeout for repair exec |
| `results_path` | `outputs/results.json` | `data/paired_results.json` | per architecture file org |
| `OPENAI_API_KEY` | present | omitted | H-M2 uses only CodeLlama-7B, no GPT-4 |

`torch_dtype`, `device_map`, `seed` reused unchanged from H-E1 convention.

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)
