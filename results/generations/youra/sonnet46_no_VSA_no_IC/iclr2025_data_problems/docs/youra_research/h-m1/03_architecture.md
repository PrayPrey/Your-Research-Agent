---
hypothesis_id: H-M1
phase: architecture
date: 2026-08-20
author: yoon303b@gmail.com
---

# Architecture: H-M1 — Cognitive Task Pattern Proxies in The Pile

Applied: N/A — Archon KB not indexed for this domain (similarity < 0.51, image-gen content only)

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (H-E1 code present, but not directly reused)
**Status**: H-E1 code found at `docs/youra_research/h-e1/code/`; loader.py is MMapIndexedDataset/Pythia checkpoint infrastructure — no modules applicable to H-M1 content analysis pipeline
**Analyzed Path**: `docs/youra_research/h-e1/code/src/data/loader.py`
**Findings**: H-E1 established `pile_set_name` 22-domain taxonomy and lm_dataformat streaming pattern (reference). No importable modules reused. H-M1 is standalone.

---

## File Structure

```
docs/youra_research/h-m1/code/
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py          # Pile streaming + stratified sampler
│   ├── proxies/
│   │   ├── __init__.py
│   │   └── compute.py         # spaCy proxy computation + parallel dispatch
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── stats.py           # Welch ANOVA, eta-sq, Tukey HSD
│   └── visualization/
│       ├── __init__.py
│       └── figures.py         # 4 required figures
├── config.py                  # All constants in one place
├── run_experiment.py          # CLI entrypoint
└── results/                   # auto-created at runtime
figures/                       # → docs/youra_research/h-m1/figures/
```

---

## Modules

### Config (`config.py`)

**Dependencies**: stdlib only

```python
SEED: int = 42
DOCS_PER_DOMAIN: int = 1000
MIN_TOKENS: int = 100
MAX_CHARS: int = 50_000
SPACY_MODEL: str = "en_core_web_sm"
POOL_CHUNKSIZE: int = 128

PILE_DOMAINS: list[str] = [
    "Wikipedia (en)", "BookCorpus2", "Bibliotik", "Github",
    "PubMed Central", "ArXiv", "FreeLaw", "StackExchange",
    "USPTO Backgrounds", "OpenWebText2", "EuroParl", "HackerNews",
    "YoutubeSubtitles", "PhilPapers", "NIH ExPorter", "Enron Emails",
    "DM Mathematics", "Ubuntu IRC", "OpenSubtitles", "Gutenberg (PG-19)",
    "Pile-CC", "OpenWebText2",
]
FOCAL_DOMAINS: list[str] = ["Wikipedia (en)", "BookCorpus2", "Github"]

CONNECTIVES: frozenset[str] = frozenset({
    "however", "therefore", "moreover", "furthermore", "nevertheless",
    "consequently", "subsequently", "meanwhile", "although", "because",
    "whereas", "thus", "hence", "indeed", "additionally",
})
FORMAL_SYNTAX_PATTERN: str = r'[{}\[\]()<>;]|def |class |import |return '

RESULTS_DIR: str = "results"
FIGURES_DIR: str = "docs/youra_research/h-m1/figures"
```

---

### DataLoader (`src/data/loader.py`)

**Dependencies**: config, datasets (HF), lm_dataformat, langdetect, spacy

```python
def stream_pile_hf(seed: int = SEED) -> Iterator[tuple[str, str]]:
    """Yields (text, domain) from HF streaming validation split."""
    ...

def stream_pile_lmd(path: str, seed: int = SEED) -> Iterator[tuple[str, str]]:
    """Yields (text, domain) from lm_dataformat val.jsonl.zst."""
    ...

def is_english(text: str) -> bool:
    """langdetect; returns False on detection failure."""
    ...

def sample_domains(
    stream: Iterator[tuple[str, str]],
    docs_per_domain: int = DOCS_PER_DOMAIN,
    min_tokens: int = MIN_TOKENS,
    nlp_tokenizer,
) -> dict[str, list[str]]:
    """
    Stratified sampling. Stops per-domain once quota met.
    Logs warning if domain exhausted before quota.
    Returns {domain: [text, ...]} with len <= docs_per_domain each.
    """
    ...
```

---

### ProxyCompute (`src/proxies/compute.py`)

**Dependencies**: config, spacy, re, multiprocessing

```python
FORMAL_SYNTAX_RE: re.Pattern  # compiled at import time

def load_nlp() -> spacy.Language:
    """Load en_core_web_sm; cache in module-level singleton."""
    ...

def compute_proxies(text: str) -> dict[str, float]:
    """
    Truncates to MAX_CHARS, runs spaCy, returns:
      entity_density, narrative_coherence, formal_syntax_density
    Safe for multiprocessing (no shared state).
    """
    ...

def compute_domain_scores(
    domain_texts: dict[str, list[str]],
    chunksize: int = POOL_CHUNKSIZE,
) -> dict[str, dict[str, list[float]]]:
    """
    Parallel dispatch via multiprocessing.Pool.imap_unordered.
    Returns {domain: {proxy: [float, ...]}}
    """
    ...
```

---

### Stats (`src/analysis/stats.py`)

**Dependencies**: scipy, statsmodels, pandas, numpy

```python
def welch_anova(
    domain_scores: dict[str, list[float]]
) -> dict:
    """
    scipy.stats.f_oneway across all domains.
    Returns {F, p_value, eta_squared}.
    eta_sq from statsmodels anova_lm typ=2.
    """
    ...

def tukey_hsd(
    domain_scores: dict[str, list[float]],
    alpha: float = 0.05,
) -> "TukeyHSDResults":
    """
    statsmodels pairwise_tukeyhsd on long-format DataFrame.
    Returns statsmodels result object (has reject matrix + summary).
    """
    ...

def domain_summary_stats(
    domain_scores: dict[str, list[float]]
) -> pd.DataFrame:
    """Per-domain mean, std, 95% CI for one proxy."""
    ...

def evaluate_gate(
    domain_scores: dict[str, dict[str, list[float]]],
    anova_results: dict[str, dict],
    tukey_results: dict[str, object],
) -> dict:
    """
    Returns gate_metrics dict including gate_pass bool.
    Checks: entity_density wiki>books p<0.05 eta²>0.1,
            narrative_coherence books>wiki p<0.05.
    """
    ...
```

---

### Figures (`src/visualization/figures.py`)

**Dependencies**: matplotlib, seaborn, pandas, numpy

```python
def plot_domain_proxy_comparison(
    summary: pd.DataFrame,
    out_path: str,
) -> None:
    """Bar chart mean ± 95CI, 3 proxies × 22 domains, sorted by entity_density."""
    ...

def plot_focal_domain_violins(
    domain_scores: dict[str, dict[str, list[float]]],
    focal_domains: list[str],
    out_path: str,
) -> None:
    """Violin plots for 3 focal domains × 3 proxies."""
    ...

def plot_tukey_heatmap(
    tukey_result,
    out_path: str,
) -> None:
    """22×22 Tukey HSD reject matrix heatmap for entity_density."""
    ...

def plot_proxy_correlation_scatter(
    domain_scores: dict[str, dict[str, list[float]]],
    out_path: str,
) -> None:
    """entity_density vs narrative_coherence scatter, colored by domain."""
    ...
```

---

### Entrypoint (`run_experiment.py`)

**Dependencies**: all modules above, argparse, json, pickle, pathlib, tqdm

```python
def parse_args() -> argparse.Namespace:
    """--data-path, --loader {hf,lmd}, --skip-sampling (reuse saved scores)."""
    ...

def main() -> None:
    """
    1. Load/sample domain texts
    2. Save raw texts to results/domain_texts.pkl
    3. Compute proxies (parallel)
    4. Save domain_scores to results/domain_scores.json
    5. Run stats (ANOVA + Tukey per proxy)
    6. Save results/statistical_results.csv
    7. Evaluate gate → results/h_m1_results.json
    8. Generate 4 figures
    9. Print GATE PASS / GATE FAIL
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Module Dependency Graph

```
run_experiment.py
  → config
  → src/data/loader       (config)
  → src/proxies/compute   (config)
  → src/analysis/stats    (config)
  → src/visualization/figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | File structure, requirements.txt, config.py, figures dir | 5 | 1+1+1+2 |
| A-2 | Data Loader | HF + lmd streaming, lang filter, stratified sampler | 13 | 3+2+4+4 |
| A-3 | Proxy Computation | spaCy load, 3 proxy formulas, multiprocessing dispatch | 14 | 3+2+5+4 |
| A-4 | Per-Domain Aggregation | domain_scores structure, save pkl/json, summary stats | 8 | 2+2+2+2 |
| A-5 | Statistical Analysis | Welch ANOVA, eta-sq, Tukey HSD, gate evaluation | 15 | 3+3+5+4 |
| A-6 | Visualization | 4 figures (bar, violin, heatmap, scatter) | 12 | 3+2+4+3 |
| A-7 | CLI Entrypoint | run_experiment.py orchestration, --skip-sampling flag | 10 | 2+3+2+3 |
| A-8 | Results Reporting | JSON gate metrics, CSV stats, stdout GATE PASS/FAIL | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-5], Medium(9-13): [A-2, A-6, A-7], Low(4-8): [A-1, A-4, A-8]

---

## Notes

- `compute_proxies` is a module-level function (not a method) so multiprocessing.Pool can pickle it without issues on Linux fork; spaCy nlp object is loaded inside each worker via module singleton pattern.
- `--skip-sampling` flag allows re-running stats/figures without re-streaming The Pile (saves 2-4 hrs on re-runs).
- Results checkpoint: raw texts saved before proxy computation, proxy scores saved before stats — each stage resumable independently.
