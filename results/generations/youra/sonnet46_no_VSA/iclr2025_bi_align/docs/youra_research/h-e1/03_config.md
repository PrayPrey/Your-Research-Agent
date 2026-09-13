# Configuration: H-E1
# Fuzzy Join Data Infrastructure Audit

Applied: No relevant KB pattern (Archon KB contains diffusers/image-gen content — standard Python defaults used)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing code to analyze
**Config Files Found**: None - new config design
**Pattern Used**: dataclass + YAML

---

## A-C1: Package Versions Config [Complexity: 1, Budget: 1]

**Applied**: Standard pinned versions from PRD section 7.1

### `h-e1/code/requirements.txt`

```
rapidfuzz==3.9.7
pandas==2.2.3
datasets==3.3.0
requests==2.32.3
matplotlib==3.9.4
matplotlib-venn==0.11.10
scipy==1.13.1
numpy==1.26.4
PyYAML==6.0.2
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Pin versions | requirements.txt with latest stable compatible set |

---

## A-C2: Threshold Config [Complexity: 1, Budget: 1]

**Applied**: Threshold=75 sourced from prior run match_rate=0.857 (PRD FR-4); fallback chain from FR-5

### `h-e1/code/config.yaml`

```yaml
# H-E1 Audit Config

data:
  llm_lb_url: "https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv"
  llm_lb_cache: "./data/llm_leaderboard_v1/llm.csv"
  bbq_cache: "./data/bbq_scores/bbq_per_model.csv"
  helm_lite_dataset: "stanford-crfm/helm-lite"

fuzzy:
  threshold: 75
  processor: "default_process"
  fallback_thresholds: [70, 65]
  fallback_scorer: "token_set_ratio"
  match_rate_fallback_trigger: 0.55

gate:
  n_complete_min: 30
  match_rate_min: 0.55

output:
  figures_dir: "./docs/youra_research/h-e1/figures"
  save_csv: true

sensitivity:
  thresholds: [65, 70, 75, 80]

seed: 42
```

### `h-e1/code/config.py`

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class AuditConfig:
    # Data sources
    llm_lb_url: str = "https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv"
    llm_lb_cache: str = "./data/llm_leaderboard_v1/llm.csv"
    bbq_cache: str = "./data/bbq_scores/bbq_per_model.csv"
    helm_lite_dataset: str = "stanford-crfm/helm-lite"

    # Fuzzy join — threshold=75 validated by prior run (match_rate=0.857 at t=75)
    fuzzy_threshold: int = 75
    fuzzy_processor: str = "default_process"
    fallback_thresholds: List[int] = field(default_factory=lambda: [70, 65])
    fallback_scorer: str = "token_set_ratio"
    match_rate_fallback_trigger: float = 0.55

    # Gate criteria (PRD section 6)
    n_complete_min: int = 30
    match_rate_min: float = 0.55

    # Output
    figures_dir: str = "./docs/youra_research/h-e1/figures"
    save_csv: bool = True

    # Sensitivity sweep
    sensitivity_thresholds: List[int] = field(default_factory=lambda: [65, 70, 75, 80])

    seed: int = 42


def load_config(yaml_path: str = None) -> AuditConfig:
    """Load config from YAML or return defaults."""
    if yaml_path is None:
        return AuditConfig()
    import yaml
    with open(yaml_path) as f:
        raw = yaml.safe_load(f)
    d = raw.get("data", {})
    fz = raw.get("fuzzy", {})
    g = raw.get("gate", {})
    o = raw.get("output", {})
    s = raw.get("sensitivity", {})
    return AuditConfig(
        llm_lb_url=d.get("llm_lb_url", AuditConfig.llm_lb_url),
        llm_lb_cache=d.get("llm_lb_cache", AuditConfig.llm_lb_cache),
        bbq_cache=d.get("bbq_cache", AuditConfig.bbq_cache),
        helm_lite_dataset=d.get("helm_lite_dataset", AuditConfig.helm_lite_dataset),
        fuzzy_threshold=fz.get("threshold", AuditConfig.fuzzy_threshold),
        fuzzy_processor=fz.get("processor", AuditConfig.fuzzy_processor),
        fallback_thresholds=fz.get("fallback_thresholds", [70, 65]),
        fallback_scorer=fz.get("fallback_scorer", AuditConfig.fallback_scorer),
        match_rate_fallback_trigger=fz.get("match_rate_fallback_trigger", AuditConfig.match_rate_fallback_trigger),
        n_complete_min=g.get("n_complete_min", AuditConfig.n_complete_min),
        match_rate_min=g.get("match_rate_min", AuditConfig.match_rate_min),
        figures_dir=o.get("figures_dir", AuditConfig.figures_dir),
        save_csv=o.get("save_csv", AuditConfig.save_csv),
        sensitivity_thresholds=s.get("thresholds", [65, 70, 75, 80]),
        seed=raw.get("seed", AuditConfig.seed),
    )
```

### Threshold Justification

- `fuzzy_threshold=75`: WRatio at 75 yielded match_rate=0.857 in prior run — well above the 0.55 gate; primary scorer.
- `fallback_thresholds=[70, 65]`: Only triggered if match_rate < 0.55 (unlikely given prior data); descending to catch edge cases.
- `match_rate_fallback_trigger=0.55`: Mirrors the gate threshold — below gate = try looser match before reporting failure.
- `sensitivity_thresholds=[65,70,75,80]`: Bracketing primary threshold on both sides for ablation plot (Figure 4).

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Threshold chain | Primary WRatio=75 + fallback [70, 65] + gate values + sweep list |

---

*Generated: 2026-07-30 | Hypothesis: H-E1 | Phase: 3 - Configuration*
