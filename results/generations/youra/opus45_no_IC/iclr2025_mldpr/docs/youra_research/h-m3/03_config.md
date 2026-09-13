# Config: H-M3 (Citation-Benchmark Overlap)

**Applied**: no relevant KB pattern found (best match: pytorch/_inductor/config.py, similarity 0.31 — unrelated domain); using module-level constants dict pattern per architecture spec (no config.py file, few constants inline).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: h-m2/code/ does not exist (confirmed absent per architecture doc) — no base config classes to verify. New config design.
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (single fixed experiment, MECHANISM validation — not a training pipeline, no hyperparameter search)

---

## A-1 through A-9: Single Pipeline Config [Complexity: Low, Budget: 0 subtasks]

All tasks share one config — this is a statistical analysis pipeline, not per-module tunable components.

### Configuration (Hardcoded Dict)

```python
CONFIG = {
    # Scope
    "VENUES": ("NeurIPS", "ICML", "ICLR"),
    "YEARS": range(2018, 2025),  # 2018-2024 inclusive
    "SEED": 42,

    # Semantic Scholar API
    "S2_BASE": "https://api.semanticscholar.org/graph/v1",
    "S2_API_KEY_ENV": "S2_API_KEY",
    "S2_RATE_LIMIT_RPS": 100,       # requests/sec with key
    "S2_MAX_RETRIES": 5,
    "S2_BACKOFF_BASE": 2.0,          # seconds, exponential: base * 2^attempt
    "S2_BACKOFF_MAX": 60.0,          # cap backoff at 60s
    "S2_TIMEOUT": 30,                # request timeout, seconds

    # Gate thresholds (SHOULD_WORK)
    "P_VALUE_THRESHOLD": 0.01,       # Mann-Whitney U, alternative='greater'
    "COHENS_D_THRESHOLD": 0.3,       # medium effect size
    "MIN_N_CITING_PAIRS": 1000,

    # Paths
    "CACHE_DIR": "h-m3/cache/",
    "FIGURES_DIR": "h-m3/figures/",
    "RESULTS_DIR": "h-m3/results/",
}
```

### Subtasks [0/0 used]

No subtask breakdown — all tasks A-1 through A-9 are Low complexity (4-8), no decomposition budget allocated.

---

## Notes

- No dataclass used: single fixed run, no per-field validation/typing benefit over dict for this scope.
- `S2_API_KEY` read from environment at runtime (`os.environ["S2_API_KEY"]`), not hardcoded.
- Cache key: `CACHE_DIR/{paper_id}.json` (per architecture `fetch_citations`).
- No YAML — single Python process, no external config loading needed.
