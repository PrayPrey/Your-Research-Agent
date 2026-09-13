# H-M2 Configuration

**Applied**: LIGHT-tier correlation analysis config (pattern from H-M1/H-E1 sibling experiments)

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (sibling experiments h-e1, h-m1 present)
**Status**: Existing patterns found — H-M1/H-E1 use Python constants module, not YAML. Task explicitly requests YAML format for H-M2; no existing YAML config to reuse.
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`, `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: YAML (per task spec) — flat key groups, single fixed config (no grid/variants)

---

## A-1: H-M2 Correlation Analysis [Complexity: 1, Budget: 1]

### Configuration (YAML)

```yaml
data:
  model_scores_path: "../h-m1/code/results/model_scores.csv"  # fallback if no dedicated HaluEval source
  halueval_scores_path: "data_cache/halueval_scores.csv"
  truthfulqa_col: "truthfulqa_mc2"
  halueval_cols:
    - "halueval_qa"
    - "halueval_dialogue"
    - "halueval_summarization"
  min_models: 30
  n_target_models: 50

analysis:
  correlation_method: "spearman"
  alpha: 0.05
  bootstrap:
    n_iterations: 1000
    ci_level: 0.95
  seed: 42

gate:
  threshold: 0.7
  primary_condition: "r(halueval_agg, truthfulqa) < threshold"
  secondary_condition: "r(halueval_intra) > r(halueval_vs_truthfulqa)"

output:
  results_dir: "results/"
  figures_dir: "figures/"
  report_path: "04_validation.md"
  figures:
    - "figures/gate_metrics.png"
    - "figures/correlation_heatmap.png"
    - "figures/scatter_halueval_truthfulqa.png"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Load config | Parse YAML into dict/dataclass at script start |

---

## Environment Setup

```
pandas, scipy, numpy, matplotlib, seaborn  # CPU only, ~1 min runtime
```

No env vars required (no API keys — uses cached leaderboard scores from H-M1 or local CSV).
