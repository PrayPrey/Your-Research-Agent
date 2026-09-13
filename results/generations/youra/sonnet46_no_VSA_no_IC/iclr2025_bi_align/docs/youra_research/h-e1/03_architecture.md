# Architecture: H-E1 Data Infrastructure Verification

**Hypothesis:** h-e1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-20
**Author:** yoon303b@gmail.com

Applied: minimal single-file pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no local codebase to analyze
**Analyzed Path:** N/A
**Findings:** New self-contained Python pipeline. No existing code to discover patterns from.

---

## Overview

Single-script pipeline (~200 lines). No modules, no packages — one file does everything. The PRD's pseudo-code already constitutes the implementation skeleton; architecture maps it to concrete file assignments.

---

## File Structure

```
h-e1/
├── run_h_e1.py          # single entry point — all logic lives here
├── config.py            # constants only (URLs, thresholds, venue lists)
├── data/                # output JSON files
├── cache/s2ag/          # API response cache
├── figures/             # 4 PNG outputs
└── results/             # gate result JSON
```

---

## Modules

### Config (`config.py`)

**Dependencies:** none

```python
S2AG_BASE: str = "https://api.semanticscholar.org/graph/v1"
CORPUS_REPO: str = "https://github.com/huashen218/bidirectional-alignment-tax"
BATCH_FIELDS: str = "paperId,externalIds,title,venue,fieldsOfStudy,year"
REF_FIELDS: str = "citedPaper.paperId,citedPaper.title,citedPaper.venue,citedPaper.fieldsOfStudy"
COVERAGE_GATE: float = 0.70
CROSS_GROUP_GATE: int = 30
SLEEP_SECS: float = 1.5

ML_NLP_VENUES_S1: frozenset  # NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, COLING, Findings
ML_NLP_VENUES_S2: frozenset  # NeurIPS, ICML, ICLR only
HCI_VENUES: frozenset        # CHI, CSCW, IUI, UIST, ASSETS
SCHEMES: dict                # {scheme_name: {ml_nlp, hci, use_fos?}}
```

---

### Pipeline (`run_h_e1.py`)

**Dependencies:** config, requests, networkx, scipy, matplotlib, json, re, pathlib, time, subprocess, collections

```python
# ── Corpus Ingestion ─────────────────────────────────────────────────────────
def clone_corpus(dest: str = "corpus") -> Path: ...
def extract_paper_ids(corpus_dir: Path) -> list[str]: ...
    # regex: arxiv.org/abs/([\d.]+) → "arXiv:{id}"
    # regex: doi.org/(10\.\S+) → doi string
    # returns deduplicated list

# ── S2AG API (with cache + retry) ────────────────────────────────────────────
def _api_get(url: str, params: dict, cache_path: Path) -> dict | list: ...
    # cache hit → return json; miss → requests.get with 3-retry exponential backoff
    # raises on 4xx (except 404 → returns {}); sleeps SLEEP_SECS after miss

def resolve_papers(ids: list[str], cache_dir: Path) -> dict[str, dict | None]: ...
    # POST /paper/batch in ≤500-id chunks; cache per-chunk by hash(sorted ids)
    # returns {input_id: paper_data | None}

def fetch_references(paper_id: str, cache_dir: Path) -> list[dict]: ...
    # GET /paper/{id}/references; cache to refs_{paperId}.json
    # returns list of citedPaper dicts

# ── Classification ────────────────────────────────────────────────────────────
def classify_paper(paper: dict, scheme: dict) -> str | None: ...
    # returns "ML_NLP" | "HCI" | None
    # scheme3: fieldsOfStudy primary, venue fallback

def classify_all(resolved: dict, scheme: dict) -> dict[str, str | None]: ...
    # returns {paperId: group}

# ── Graph Construction ────────────────────────────────────────────────────────
def build_graph(
    resolved: dict[str, dict],
    groups: dict[str, str],
    cache_dir: Path
) -> tuple[nx.DiGraph, dict[tuple, int]]: ...
    # builds DiGraph; counts edge_counts[(src_group, tgt_group)]

# ── Gate Evaluation ───────────────────────────────────────────────────────────
def evaluate_gate(
    coverage: float,
    scheme_results: dict
) -> dict: ...
    # returns {coverage, resolved, total, schemes, gate_pass}

# ── Visualization (4 figures) ─────────────────────────────────────────────────
def plot_gate_metrics(coverage: float, scheme_results: dict, out: Path) -> None: ...
    # Figure 1: two-panel bar chart (coverage vs 70%; cross-group per scheme vs 30)

def plot_dropout_by_venue(unresolved: list[str], corpus_ids: list[str], out: Path) -> None: ...
    # Figure 2: bar chart unresolved papers by venue string

def plot_edge_heatmaps(scheme_results: dict, out: Path) -> None: ...
    # Figure 3: 2x2 heatmap per scheme (3 subplots)

def plot_venue_pie(groups: dict, out: Path) -> None: ...
    # Figure 4: pie chart ML_NLP / HCI / unclassified under scheme1

# ── Entry Point ───────────────────────────────────────────────────────────────
def main() -> None: ...
    # orchestrates steps 1-8; writes all JSON outputs; saves figures; prints gate result
```

---

## Data Flow

- `clone_corpus` → `extract_paper_ids` → `corpus_ids.json`
- `resolve_papers` → `resolved_papers.json`
- for each scheme: `classify_all` → `paper_groups_{scheme}.json`
- for each scheme: `build_graph` (calls `fetch_references`) → `edge_counts_{scheme}.json`
- `evaluate_gate` → `h_e1_gate_result.json`
- 4 plot functions → `figures/*.png`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Directory structure, config.py with venue lists and constants | 4 | Size:1 + Dep:1 + Alg:1 + Int:1 |
| A-2 | Corpus Ingestion | Clone repo, regex-parse arXiv/DOI IDs, deduplicate, save corpus_ids.json | 7 | Size:2 + Dep:1 + Alg:2 + Int:2 |
| A-3 | S2AG Resolution | Batch POST with chunk/cache/retry; save resolved_papers.json | 9 | Size:2 + Dep:2 + Alg:2 + Int:3 |
| A-4 | Classification + Reference Fetch | 3-scheme classify_paper; GET references with cache; save paper_groups and edge_counts | 11 | Size:3 + Dep:2 + Alg:3 + Int:3 |
| A-5 | Graph + Gate Eval | build_graph (DiGraph, edge_counts), evaluate_gate, write h_e1_gate_result.json | 8 | Size:2 + Dep:2 + Alg:2 + Int:2 |
| A-6 | Visualization | 4 matplotlib figures; gate metrics, dropout, heatmaps, pie | 7 | Size:2 + Dep:2 + Alg:1 + Int:2 |

**Distribution:** High(9-13): [A-4], Medium(7-8): [A-3, A-5, A-6], Low(4-6): [A-1, A-2]

---

## Notes

- `ponytail:` sequential `time.sleep(1.5)` per uncached API call — upgrade to `concurrent.futures` with semaphore if runtime matters with API key
- All S2AG responses cached before any graph logic runs; re-run is zero-API
- `scipy` imported but only used in downstream H-M* hypotheses; import is present for completeness
- API key read from `S2AG_API_KEY` env var; if set, omit sleep (100 req/sec tier)
