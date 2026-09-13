---
hypothesis_id: H-M1
phase: config
date: 2026-08-20
author: yoon303b@gmail.com
---

# Configuration: H-M1 — Cognitive Task Pattern Proxies in The Pile

Applied: N/A — Archon KB not indexed for this domain (similarity < 0.43, image-gen content only)

---

## Codebase Analysis (Serena)

**Project Type**: green-field (H-M1 standalone; H-E1 code not reused)
**Status**: green-field — new config design
**Config Files Found**: None — h-m1/code/ not yet created
**Pattern Used**: dataclass (ExperimentConfig) + module-level constants for frozenset/regex

---

## A-6: Visualization [Complexity: 12, Budget: 2 subtasks]

**Applied**: Standard matplotlib/seaborn defaults

### Configuration

```python
from dataclasses import dataclass, field

@dataclass
class FigureConfig:
    figures_dir: str = "docs/youra_research/h-m1/figures"
    dpi: int = 150
    fig_width: float = 14.0       # inches — wide enough for 22-domain bar chart
    fig_height: float = 6.0
    violin_fig_width: float = 10.0
    violin_fig_height: float = 8.0
    heatmap_fig_size: float = 10.0  # square — 22×22 matrix
    scatter_fig_width: float = 8.0
    scatter_fig_height: float = 6.0
    style: str = "seaborn-v0_8-whitegrid"
    palette: str = "tab20"          # 20-color tab palette covers 22 domains approx
    ci_alpha: float = 0.95
    bar_capsize: float = 4.0
    heatmap_cmap: str = "RdYlGn"
    focal_colors: dict = field(default_factory=lambda: {
        "Wikipedia (en)": "#1f77b4",
        "BookCorpus2": "#ff7f0e",
        "Github": "#2ca02c",
    })
    format: str = "png"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | FigureConfig dataclass | Fields above: dirs, dimensions, style, palette, CI alpha |
| C-6-2 | Per-figure output paths | Filenames: domain_proxy_comparison.png, focal_domain_violins.png, tukey_heatmap_entity_density.png, proxy_correlation_scatter.png |

---

## A-7: CLI Entrypoint [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard argparse pattern

### Configuration

```python
from dataclasses import dataclass

@dataclass
class RunConfig:
    # Data loading
    loader: str = "hf"              # "hf" | "lmd"
    data_path: str = ""             # required if loader="lmd"
    skip_sampling: bool = False     # reuse results/domain_texts.pkl
    skip_proxies: bool = False      # reuse results/domain_scores.json

    # Output
    results_dir: str = "results"
    log_level: str = "INFO"

    # Reproducibility
    seed: int = 42
```

### Argparse Schema (run_experiment.py)

```python
import argparse

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="H-M1: Cognitive Task Pattern Proxies in The Pile"
    )
    p.add_argument(
        "--loader", choices=["hf", "lmd"], default="hf",
        help="Data source: HuggingFace streaming (hf) or local lm_dataformat (lmd)"
    )
    p.add_argument(
        "--data-path", default="",
        help="Path to val.jsonl.zst (required when --loader=lmd)"
    )
    p.add_argument(
        "--skip-sampling", action="store_true",
        help="Skip streaming/sampling; reuse results/domain_texts.pkl"
    )
    p.add_argument(
        "--skip-proxies", action="store_true",
        help="Skip proxy computation; reuse results/domain_scores.json"
    )
    p.add_argument(
        "--results-dir", default="results",
        help="Directory for intermediate and final results"
    )
    p.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING"],
    )
    return p.parse_args()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | RunConfig dataclass | CLI-mapped fields with defaults matching parse_args |
| C-7-2 | Argparse schema | parse_args() with --loader, --data-path, --skip-sampling, --skip-proxies, --results-dir, --log-level |

---

## Full ExperimentConfig (config.py)

Single file — all constants and dataclasses in one place for Phase 4 copy-paste.

```python
# config.py — H-M1 experiment constants
from __future__ import annotations
import re
from dataclasses import dataclass, field

# ── Sampling ──────────────────────────────────────────────────────────────────

SEED: int = 42
DOCS_PER_DOMAIN: int = 1000
MIN_TOKENS: int = 100
MAX_CHARS: int = 50_000
SPACY_MODEL: str = "en_core_web_sm"
POOL_CHUNKSIZE: int = 128

# ── Domains ───────────────────────────────────────────────────────────────────

PILE_DOMAINS: list[str] = [
    "Wikipedia (en)", "BookCorpus2", "Bibliotik", "Github",
    "PubMed Central", "ArXiv", "FreeLaw", "StackExchange",
    "USPTO Backgrounds", "OpenWebText2", "EuroParl", "HackerNews",
    "YoutubeSubtitles", "PhilPapers", "NIH ExPorter", "Enron Emails",
    "DM Mathematics", "Ubuntu IRC", "OpenSubtitles", "Gutenberg (PG-19)",
    "Pile-CC",
]
FOCAL_DOMAINS: list[str] = ["Wikipedia (en)", "BookCorpus2", "Github"]

# ── Proxy constants ───────────────────────────────────────────────────────────

CONNECTIVES: frozenset[str] = frozenset({
    "however", "therefore", "moreover", "furthermore", "nevertheless",
    "consequently", "subsequently", "meanwhile", "although", "because",
    "whereas", "thus", "hence", "indeed", "additionally",
})
FORMAL_SYNTAX_PATTERN: str = r'[{}\[\]()<>;]|def |class |import |return '
# Compiled at import time — safe to share across processes (read-only)
FORMAL_SYNTAX_RE: re.Pattern = re.compile(FORMAL_SYNTAX_PATTERN)

# ── Paths ─────────────────────────────────────────────────────────────────────

RESULTS_DIR: str = "results"
FIGURES_DIR: str = "docs/youra_research/h-m1/figures"

# ── Stats ─────────────────────────────────────────────────────────────────────

ALPHA: float = 0.05
ETA_SQ_THRESHOLD: float = 0.1   # gate criterion: η² > 0.1

# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class SamplingConfig:
    seed: int = SEED
    docs_per_domain: int = DOCS_PER_DOMAIN
    min_tokens: int = MIN_TOKENS
    max_chars: int = MAX_CHARS
    spacy_model: str = SPACY_MODEL
    pool_chunksize: int = POOL_CHUNKSIZE


@dataclass
class ProxyConfig:
    proxies: list[str] = field(default_factory=lambda: [
        "entity_density",
        "narrative_coherence",
        "formal_syntax_density",
    ])


@dataclass
class StatsConfig:
    alpha: float = ALPHA
    eta_sq_threshold: float = ETA_SQ_THRESHOLD
    anova_typ: int = 2              # statsmodels anova_lm type


@dataclass
class FigureConfig:
    figures_dir: str = FIGURES_DIR
    dpi: int = 150
    fig_width: float = 14.0
    fig_height: float = 6.0
    violin_fig_width: float = 10.0
    violin_fig_height: float = 8.0
    heatmap_fig_size: float = 10.0
    scatter_fig_width: float = 8.0
    scatter_fig_height: float = 6.0
    style: str = "seaborn-v0_8-whitegrid"
    palette: str = "tab20"
    ci_alpha: float = 0.95
    bar_capsize: float = 4.0
    heatmap_cmap: str = "RdYlGn"
    focal_colors: dict = field(default_factory=lambda: {
        "Wikipedia (en)": "#1f77b4",
        "BookCorpus2": "#ff7f0e",
        "Github": "#2ca02c",
    })
    format: str = "png"


@dataclass
class RunConfig:
    loader: str = "hf"          # "hf" | "lmd"
    data_path: str = ""
    skip_sampling: bool = False
    skip_proxies: bool = False
    results_dir: str = RESULTS_DIR
    log_level: str = "INFO"
    seed: int = SEED


@dataclass
class ExperimentConfig:
    sampling: SamplingConfig = field(default_factory=SamplingConfig)
    proxies: ProxyConfig = field(default_factory=ProxyConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    figures: FigureConfig = field(default_factory=FigureConfig)
    run: RunConfig = field(default_factory=RunConfig)
```

---

## YAML Schema (reference for CLI/config file support)

```yaml
# h_m1_config.yaml — optional override file (argparse takes precedence)
sampling:
  seed: 42
  docs_per_domain: 1000
  min_tokens: 100
  max_chars: 50000
  spacy_model: "en_core_web_sm"
  pool_chunksize: 128

stats:
  alpha: 0.05
  eta_sq_threshold: 0.1
  anova_typ: 2

figures:
  dpi: 150
  style: "seaborn-v0_8-whitegrid"
  palette: "tab20"
  format: "png"

run:
  loader: "hf"        # "hf" | "lmd"
  data_path: ""
  skip_sampling: false
  skip_proxies: false
  results_dir: "results"
  log_level: "INFO"
```

---

## Non-Standard Value Rationale

| Field | Value | Reason |
|-------|-------|--------|
| `dpi` | 150 | Lower than publication-quality 300 — sufficient for exploratory figures, faster write |
| `palette` | tab20 | Covers 20 of 22 domains; last 2 domains will cycle — acceptable for bar chart sorted by value |
| `heatmap_cmap` | RdYlGn | Diverging red-green for binary reject matrix; perceptually clear for True/False |
| `anova_typ` | 2 | Type II SS required for η² from statsmodels anova_lm per FR-4.2 |
| `pool_chunksize` | 128 | Balances IPC overhead vs granularity for ~22K short NLP tasks on single machine |
