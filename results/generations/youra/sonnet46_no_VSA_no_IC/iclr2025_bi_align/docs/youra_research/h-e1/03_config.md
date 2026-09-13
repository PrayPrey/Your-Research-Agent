# Configuration: h-e1

**Applied**: standard-dataclass-with-env-override pattern (green-field; no KB prior cases)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass + module-level constants

---

## S-3a: API Configuration and Rate-Limiting Parameter Schema [Complexity: 1, Budget: 1]

### Configuration (Python Dataclass)

```python
import os
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class S2AGConfig:
    base_url: str = "https://api.semanticscholar.org/graph/v1"
    batch_fields: str = "paperId,externalIds,title,venue,fieldsOfStudy,year"
    ref_fields: str = "citedPaper.paperId,citedPaper.title,citedPaper.venue,citedPaper.fieldsOfStudy"
    batch_size: int = 500
    ref_limit: int = 1000
    sleep_secs: float = 1.5   # unauthenticated: ~40 req/min
    max_retries: int = 3
    api_key: str = field(default_factory=lambda: os.environ.get("S2AG_API_KEY", ""))

    def __post_init__(self):
        if self.api_key:
            self.sleep_secs = 0.01  # authenticated: 100 req/sec


@dataclass
class GateConfig:
    coverage_gate: float = 0.70
    cross_group_gate: int = 30


@dataclass
class PathConfig:
    corpus_dir: Path = Path("corpus")
    cache_dir: Path = Path("cache/s2ag")
    data_dir: Path = Path("data")
    figures_dir: Path = Path("h-e1/figures")
    results_dir: Path = Path("h-e1/results")

    def __post_init__(self):
        for d in (self.cache_dir, self.data_dir, self.figures_dir, self.results_dir):
            d.mkdir(parents=True, exist_ok=True)


@dataclass
class ExperimentConfig:
    s2ag: S2AGConfig = field(default_factory=S2AGConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    seed: int = 42
```

### Venue Classification Constants

```python
# Scheme 1: ACL/EMNLP/NAACL/COLING/Findings counted as ML_NLP
ML_NLP_VENUES_S1: frozenset = frozenset({
    "neurips", "icml", "iclr", "acl", "emnlp", "naacl", "coling", "findings"
})

# Scheme 2: Core ML only (bridge-neutral)
ML_NLP_VENUES_S2: frozenset = frozenset({"neurips", "icml", "iclr"})

# HCI venues (shared across all schemes)
HCI_VENUES: frozenset = frozenset({"chi", "cscw", "iui", "uist", "assets"})

SCHEMES: dict = {
    "scheme1": {
        "ml_nlp": ML_NLP_VENUES_S1,
        "hci": HCI_VENUES,
        "use_fos": False,
    },
    "scheme2": {
        "ml_nlp": ML_NLP_VENUES_S2,
        "hci": HCI_VENUES,
        "use_fos": False,
    },
    "scheme3": {
        # fieldsOfStudy-primary; venue string as fallback
        "ml_nlp": ML_NLP_VENUES_S1,
        "hci": HCI_VENUES,
        "use_fos": True,
    },
}
```

### YAML Schema (config.yaml)

```yaml
# h-e1/config.yaml — all fields with defaults shown
s2ag:
  base_url: "https://api.semanticscholar.org/graph/v1"
  batch_fields: "paperId,externalIds,title,venue,fieldsOfStudy,year"
  ref_fields: "citedPaper.paperId,citedPaper.title,citedPaper.venue,citedPaper.fieldsOfStudy"
  batch_size: 500
  ref_limit: 1000
  sleep_secs: 1.5        # overridden to 0.01 when S2AG_API_KEY is set
  max_retries: 3

gate:
  coverage_gate: 0.70    # fraction of corpus IDs that must resolve
  cross_group_gate: 30   # minimum AI↔HCI within-corpus edges

paths:
  corpus_dir: "corpus"
  cache_dir: "cache/s2ag"
  data_dir: "data"
  figures_dir: "h-e1/figures"
  results_dir: "h-e1/results"

seed: 42
```

### Environment Variable Spec

| Variable | Required | Effect |
|----------|----------|--------|
| `S2AG_API_KEY` | Optional | Enables 100 req/sec tier; sets `sleep_secs = 0.01` |

Set via: `export S2AG_API_KEY=your_key_here`

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| S-3a | API config + rate limiting | S2AGConfig, GateConfig, PathConfig, venue constants, YAML schema |
