# Configuration: H-M2 Hedging Marker Detection

**Applied**: hardcoded dict pattern (single-condition MECHANISM experiment, no sweep) — consistent with H-M1 precedent

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: H-M1 code read directly (MCP unavailable this run; manual file read performed per architecture doc).
**Config Files Found**: H-M1 has no dedicated `config.py` — parameters are hardcoded inline in `api_client.py`/`run_experiment.py` (model="gpt-3.5-turbo", temp=0, max_tokens=500, max_retries=3). H-M2 follows same inline-dict pattern; no shared config module to inherit.
**Pattern Used**: hardcoded dict (module-level constants), not dataclass/YAML — matches base hypothesis style.

---

## Configuration (Single Module: `config.py`)

```python
CONFIG = {
    "model": {
        "name": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 500,
    },
    "dataset": {
        "name": "truthful_qa",
        "config": "generation",
        "split": "validation",
        "n_items": 817,  # full set, no subsampling (FR-1)
    },
    "hedging": {
        "markers": [
            "might", "may", "could", "possibly", "perhaps", "uncertain",
            "unsure", "alternatively", "however", "although", "probably",
            "likely", "unlikely", "but", "not sure", "hard to say",
            "difficult to determine",
        ],
        # EXPLORE fallback if gate fails (FR-3 / Appendix)
        "extended_markers": [
            "seem", "appears", "tends", "generally", "typically",
            "in some cases", "it depends", "not always", "sometimes",
            "often", "rarely", "approximately", "roughly", "around",
            "i think", "i believe", "in my opinion", "arguably",
        ],
        "confidence_split_markers": ["confidence:", "my confidence", "i am confident"],
        "presence_rate_threshold": 0.30,  # SHOULD_WORK gate (FR-5, PRD Success Criteria)
    },
    "api": {
        "max_retries": 3,
        "backoff_base": 2,     # exponential: backoff_base ** attempt seconds
        "timeout": 60,
    },
    "paths": {
        "cache_path": "h-m2/code/.cache/responses.jsonl",
        "results_path": "h-m2/code/results/h-m2_results.json",
        "summary_path": "h-m2/code/results/summary.yaml",
        "figures_dir": "h-m2/figures",
    },
    "seed": 42,
}
```

### Equivalent YAML (reference only; code reads the dict above directly)

```yaml
model:
  name: gpt-3.5-turbo
  temperature: 0
  max_tokens: 500

dataset:
  name: truthful_qa
  config: generation
  split: validation
  n_items: 817

hedging:
  markers: [might, may, could, possibly, perhaps, uncertain, unsure,
            alternatively, however, although, probably, likely, unlikely,
            but, "not sure", "hard to say", "difficult to determine"]
  extended_markers: [seem, appears, tends, generally, typically, "in some cases",
                      "it depends", "not always", sometimes, often, rarely,
                      approximately, roughly, around, "i think", "i believe",
                      "in my opinion", arguably]
  confidence_split_markers: ["confidence:", "my confidence", "i am confident"]
  presence_rate_threshold: 0.30

api:
  max_retries: 3
  backoff_base: 2
  timeout: 60

paths:
  cache_path: h-m2/code/.cache/responses.jsonl
  results_path: h-m2/code/results/h-m2_results.json
  summary_path: h-m2/code/results/summary.yaml
  figures_dir: h-m2/figures

seed: 42
```

### Environment Variables

```python
import os
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]  # required, no default (fail fast if missing)
```

No other env vars required — all experiment params are fixed in `CONFIG` (no sweep, no ablation; MECHANISM test is single-condition per PRD).

---

## Subtasks Mapping (No New Subtasks — Config Consumed by Architecture's A-1..A-8)

| Task | Config Section Used |
|------|---------------------|
| A-1 (Data loading) | `dataset` |
| A-2 (Prompt template) | `model` (max_tokens context) |
| A-3 (API client + cache) | `model`, `api`, `paths.cache_path` |
| A-4 (Reasoning chain extraction) | `hedging.confidence_split_markers` |
| A-5 (Hedging marker detection) | `hedging.markers`, `hedging.extended_markers` |
| A-6 (Metrics computation) | `hedging.presence_rate_threshold` |
| A-7 (Experiment orchestration) | `paths.results_path`, `paths.summary_path`, `seed` |
| A-8 (Visualization) | `paths.figures_dir`, `hedging.presence_rate_threshold` |

No config subtasks allocated — single dict, no variations (MECHANISM, single-condition, matches EXISTENCE-style brevity for config given no hyperparameter search is in scope).
