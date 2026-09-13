# Product Requirements Document: H-E1

**stepsCompleted:** [1, 2, 3, 4, 5]
**Hypothesis:** h-e1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-20
**Author:** yoon303b@gmail.com

---

## Executive Summary

This PRD defines implementation requirements for H-E1: a data infrastructure existence check confirming that the huashen218 bidirectional alignment corpus can be (a) resolved against the Semantic Scholar Academic Graph (S2AG) at ≥70% coverage, and (b) yields ≥30 directed cross-group within-corpus citation edges under at least one of three pre-specified venue classification schemes. H-E1 is the MUST_WORK gate hypothesis; its failure blocks all downstream statistical testing (H-M1, H-M2, H-M3).

---

## Problem Statement

The main research study requires a directed citation graph where nodes are papers from the huashen218 bidirectional alignment corpus and edges represent citation links within the corpus. Before any statistical analysis (chi-squared tests of citation directionality between ML/NLP and HCI venue groups) can be performed, two infrastructure facts must be empirically established:

1. S2AG successfully indexes ≥70% of the ~400 corpus papers (paper ID resolution coverage).
2. The resolved corpus contains ≥30 directed cross-group within-corpus citation edges (AI→HCI or HCI→AI), establishing that statistical tests are non-trivial.

This pipeline has not been run before. The experiment is novel infrastructure validation, not reproduction of existing work.

---

## Functional Requirements

### FR-1: Corpus Ingestion

- Clone `https://github.com/huashen218/bidirectional-alignment-tax` to local `corpus/` directory.
- Parse all `.md` files recursively to extract arXiv IDs (`arXiv:XXXX.XXXXX` format) and DOIs (`10.XXXX/...`).
- Deduplicate extracted IDs; store as list of ~400 paper identifiers.
- Output: `data/corpus_ids.json` — list of extracted paper ID strings.

### FR-2: S2AG Paper ID Resolution (Baseline Check)

- Call `POST https://api.semanticscholar.org/graph/v1/paper/batch` with fields `paperId,externalIds,title,venue,fieldsOfStudy,year`.
- Process IDs in chunks of ≤500 (API limit); sleep 1.5s between chunks (unauthenticated rate: 40 req/min).
- Cache all responses to `cache/s2ag/batch_{hash}.json` (skip API call if cache exists).
- Record: total IDs submitted, resolved count (non-null `paperId`), unresolved list.
- **Baseline metric:** `coverage_rate = resolved_count / total_corpus_ids`; gate threshold ≥0.70.
- Output: `data/resolved_papers.json` — dict `{input_id: paper_data | null}`.

### FR-3: Venue Group Classification (3 Pre-specified Schemes)

Implement three classification schemes applied to all resolved papers:

| Scheme | ML_NLP Venues | HCI Venues | Primary Signal |
|--------|--------------|-----------|----------------|
| scheme1 | NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, COLING, Findings | CHI, CSCW, IUI, UIST, ASSETS | venue string |
| scheme2 | NeurIPS, ICML, ICLR only (bridge-neutral) | CHI, CSCW, IUI, UIST, ASSETS | venue string |
| scheme3 | scheme1 venues + fos fallback | scheme1 HCI venues | fieldsOfStudy primary, venue fallback |

- Classification uses case-insensitive substring match on `venue` field.
- Scheme 3 uses `fieldsOfStudy` list from S2AG as primary signal ("Human-Computer Interaction" → HCI; "Computer Science"/"Linguistics" → ML_NLP, unless venue also matches HCI).
- Papers matching neither group → `unclassified`.
- Output: `data/paper_groups_{scheme}.json` — dict `{paperId: "ML_NLP" | "HCI" | null}`.

### FR-4: S2AG Reference Retrieval

- For each resolved paper, call `GET /paper/{paperId}/references` with fields `citedPaper.paperId,citedPaper.title,citedPaper.venue,citedPaper.fieldsOfStudy`; `limit=1000`.
- Cache each response to `cache/s2ag/refs_{paperId}.json`.
- Rate-limit: 1.5s sleep per uncached request.
- Output: `cache/s2ag/refs_{paperId}.json` files.

### FR-5: Within-Corpus Directed Citation Graph Construction

- Build `networkx.DiGraph` where nodes = resolved corpus paper IDs.
- Add directed edge `(src, tgt)` if `tgt` appears in `src`'s references AND `tgt` is in the corpus.
- For each scheme, compute 2×2 edge count matrix:
  - `(ML_NLP→ML_NLP)`, `(ML_NLP→HCI)`, `(HCI→ML_NLP)`, `(HCI→HCI)`.
- Cross-group edges = `(ML_NLP→HCI) + (HCI→ML_NLP)`.
- **Gate metric:** `cross_group_total ≥ 30` under ≥1 scheme.
- Output: `data/edge_counts_{scheme}.json` — nested dict of edge counts.

### FR-6: Ablation Variants (Classification Scheme Comparison)

- FR-3 + FR-5 repeated for all three schemes independently.
- Report edge counts and cross-group totals for each scheme in a comparison table.
- Check stability: scheme2 and scheme3 counts within ±20% of scheme1 (diagnostic).

### FR-7: H-E1 Gate Evaluation

- Compute `gate_pass = (coverage_rate >= 0.70) AND (any scheme has cross_group_total >= 30)`.
- Document failure modes with pre-planned responses:
  - 50–70% coverage: proceed with non-systematic dropout argument documented.
  - <30 edges under all schemes: pivot note in output report.
  - <30% coverage: experiment terminates with feasibility report output.
- Output: `results/h_e1_gate_result.json` — `{coverage, resolved, total, schemes: {...}, gate_pass}`.

### FR-8: Visualization

Generate the following figures saved to `h-e1/figures/`:

- **Figure 1 (MANDATORY):** Two-panel bar chart — panel (a) coverage rate vs 70% threshold; panel (b) cross-group edge count per scheme vs 30-edge threshold.
- **Figure 2:** Bar chart of unresolved papers by venue (non-systematic dropout check).
- **Figure 3:** 2×2 heatmap of edge count matrix under each of 3 schemes.
- **Figure 4:** Pie chart of resolved papers by venue group under Scheme 1.

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- All S2AG responses cached to `cache/s2ag/` as JSON files.
- Full experiment re-runs hit cache only (no API calls if cache populated).
- Deterministic execution: no random seeds needed (no stochastic components).

### NFR-2: Performance
- Unauthenticated: ~15–40 minutes for full corpus (400 reference requests at 40 req/min).
- With S2AG API key (100 req/sec): <5 minutes.
- Batch resolution: ≤2 API calls for ~400 papers (500 IDs/call limit).

### NFR-3: Dependencies (Minimal)
- `requests` — HTTP API calls
- `networkx` — directed citation graph
- `scipy.stats` — chi2_contingency, fisher_exact (downstream use)
- `matplotlib` — figures
- `pathlib`, `json`, `re`, `collections`, `time` — stdlib only beyond above

### NFR-4: Error Handling
- HTTP 429 (rate limit): exponential backoff, max 3 retries.
- HTTP 404 (paper not found): record as unresolved, continue.
- API key optional: read from `S2AG_API_KEY` environment variable if set; fall back to unauthenticated.
- Network error: retry 3×; log failure; skip paper (do not crash pipeline).

### NFR-5: Output Structure
```
h-e1/
├── data/
│   ├── corpus_ids.json
│   ├── resolved_papers.json
│   ├── paper_groups_scheme1.json
│   ├── paper_groups_scheme2.json
│   ├── paper_groups_scheme3.json
│   ├── edge_counts_scheme1.json
│   ├── edge_counts_scheme2.json
│   └── edge_counts_scheme3.json
├── cache/
│   └── s2ag/
│       ├── batch_{hash}.json
│       └── refs_{paperId}.json
├── figures/
│   ├── figure1_gate_metrics.png
│   ├── figure2_dropout_by_venue.png
│   ├── figure3_edge_heatmaps.png
│   └── figure4_venue_pie.png
├── results/
│   └── h_e1_gate_result.json
└── run_h_e1.py
```

---

## Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| S2AG resolution coverage | ≥70% | `resolved / total_corpus_ids` |
| Cross-group edges (≥1 scheme) | ≥30 | `ML_NLP→HCI + HCI→ML_NLP` |
| Classification rate | ≥80% | `classified / resolved` |
| Edge stability across schemes | ±20% of scheme1 | scheme2/3 vs scheme1 cross-group count |
| Pipeline runs without error | 100% | No unhandled exceptions |
| All 4 figures generated | 100% | File existence check |
| Full cache coverage | 100% | Re-run hits 0 API calls |

---

## Dependencies and Constraints

- **External:** S2AG API availability (free tier, no auth required; API key optional for speed).
- **Data:** huashen218 GitHub repo publicly accessible.
- **Constraint:** No ML training; no GPU required; runs on any Python 3.10+ environment.
- **Downstream dependency:** H-M1, H-M2, H-M3 reuse `resolved_papers.json` and `cache/s2ag/refs_*.json`; these must be persisted after H-E1 run.
- **Gate:** MUST_WORK — if `gate_pass = False`, downstream hypotheses are blocked.
