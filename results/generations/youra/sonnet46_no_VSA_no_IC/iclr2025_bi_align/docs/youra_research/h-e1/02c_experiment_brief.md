# Experiment Design: h-e1

**Date:** 2026-08-20
**Author:** yoon303b@gmail.com
**Hypothesis Statement:** Under the huashen218 bidirectional alignment corpus (~400 papers, 2018-2024), if all paper IDs are resolved against S2AG and venue groups are classified via fieldsOfStudy + venue string fallback, then ≥70% of corpus papers resolve successfully AND ≥30 cross-group directed within-corpus edges are found, confirming the data infrastructure exists to support chi-squared analysis of citation directionality.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (H-E1 is the root hypothesis)
**Gate Status:** MUST_WORK — failure blocks all downstream hypotheses (H-M1, H-M2, H-M3)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation layer)

### Gate Condition

**Primary Gate (both must pass):**
1. S2AG paper ID resolution coverage ≥ 70% of huashen218 corpus (~400 papers)
2. Cross-group directed within-corpus edge count ≥ 30 (AI→HCI or HCI→AI edges where both endpoints are in corpus)

**Failure Response:**
- Coverage 50–70%: Document unresolved papers; proceed if non-systematic dropout argued
- Coverage <50% OR edges <30: PIVOT to descriptive statistics only; bridge paper analysis still feasible
- Coverage <30%: ABANDON chi-squared analysis; study becomes feasibility report

---

## Continuation Context

This is the first hypothesis in the chain H-E1 → H-M1 → H-M2 → H-M3. No prior hypotheses to continue from. The study depends entirely on this data infrastructure being confirmed before any statistical testing occurs. The BUILD_ON evidence (S2AG indexes 205M+ publications, 2.5B edges; huashen218 papers are from well-indexed venues) makes success plausible but empirically unverified for this specific curated corpus.

Key design choice: local JSON cache for all S2AG responses eliminates redundant API calls and allows re-runs without re-fetching.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the root; no prior sub-hypothesis results.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB search for "Semantic Scholar API paper resolution S2AG" returned low-similarity matches (max ~0.48) from general ML papers (arxiv.org abstracts), indicating no prior case studies in the KB specifically covering S2AG paper ID resolution pipelines. The KB does not contain domain-specific precedents for this task.

Search for "citation network analysis cross-group directionality chi-squared" returned similarly weak matches (~0.37 max), suggesting no prior work in the KB on cross-group citation contingency table analysis.

**KB Assessment:** No relevant prior cases found. Implementation must be designed from scratch using official S2AG documentation and established Python libraries.

### Archon Code Examples

Code example search for "Semantic Scholar API paper lookup fieldsOfStudy venue classification" returned only BibTeX formatting examples (irrelevant). No S2AG API client code examples are in the Archon KB.

**Code Example Assessment:** No usable templates. Rely on S2AG official API documentation and PyPI `semanticscholar` library.

### Exa GitHub Implementations

Exa GitHub search found the following relevant implementations:

1. **smaniches/semantic-scholar-mcp** (GitHub, MIT, 2025): MCP server with 14 typed tools for paper search, citation graphs, author profiles. Python. Demonstrates S2AG citation graph API usage patterns.
   - URL: https://github.com/smaniches/semantic-scholar-mcp

2. **mirandrom/PyS2** (GitHub, MIT, 2021): Python library for S2 API with typed pydantic objects. Demonstrates `build_url()` for `/paper/{id}`, `/paper/{id}/references`, `/paper/{id}/citations` endpoints.
   - URL: https://github.com/mirandrom/PyS2/blob/master/s2/api.py
   - Key pattern: `API_URL = "https://api.semanticscholar.org/v1"` with `f"{API_URL}/{endpoint}/{api_id}"`

3. **zongmin-yu/semantic-scholar-skills** (GitHub): `resolve.py` with `PaperBatchDetailsRequest`, `PaperDetailsRequest`, multi-ID resolution via `externalIds`, `paperId`, `title` fallback chain.
   - URL: https://github.com/zongmin-yu/semantic-scholar-skills/blob/main/skills/paper-triage/scripts/_vendor/semantic_scholar_skills/engine/resolve.py
   - Key pattern: RESOLVE_FIELDS includes `paperId`, `corpusId`, `externalIds`, `title`, `venue`, `authors`, `citationCount`

4. **EvoScientist/EvoSkills fetch_paper.py** (GitHub): `normalize_paper_id()` and `_strip_arxiv_version()` — demonstrates DOI/arXiv ID normalization before S2AG lookup.
   - URL: https://github.com/EvoScientist/EvoSkills/blob/main/skills/paper-navigator/scripts/fetch_paper.py

5. **S2AG Official API Docs** (https://api.semanticscholar.org/api-docs/): Batch paper endpoint `POST /graph/v1/paper/batch` (up to 500 IDs per call); `/paper/{id}/references` with `fields=paperId,title,venue,fieldsOfStudy`; `/paper/{id}/citations` similarly.
   - `fieldsOfStudy` field on paper object returns list of study fields (e.g., "Computer Science", "Human-Computer Interaction")
   - `venue` field returns extracted publication venue string

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a data infrastructure experiment, not a paper reproduction. No official author implementation exists for this specific analysis. Implementation is novel.

**Assessment:**
- S2AG batch API (`POST /paper/batch`) is the most efficient approach: resolves up to 500 paper IDs in one call, reducing API calls from ~400 to ~1.
- `semanticscholar` PyPI package (https://pypi.org/project/semanticscholar/) wraps the S2AG API with Python-friendly interfaces for `get_paper()`, `get_paper_references()`, `get_paper_citations()`.
- For ~400 papers × references retrieval: ~400 sequential GET requests to `/paper/{id}/references`. At 40 req/min (unauthenticated rate limit), this takes ~10 minutes. With an API key (100 req/sec), <10 seconds.

**Recommended Implementation Path:**
- Primary: Direct `requests` calls to S2AG REST API with local JSON cache (no external dependencies beyond `requests`, `networkx`, `scipy`)
- Fallback: `semanticscholar` PyPI package if direct API proves cumbersome
- Justification: Minimal dependencies, full control over caching and rate limiting, transparent for reproducibility. The experiment is ~100 lines of Python — no need for a wrapper library.

### Code Analysis (Serena MCP)

Step 04 skipped per workflow instructions: no local codebase to analyze for this data infrastructure experiment. The experiment is a self-contained new pipeline, not a modification of existing code.

---

## Experiment Specification

### Dataset

**Source:** huashen218/bidirectional-alignment-reading-list GitHub repository (~400 papers, 2018–2024)
- GitHub URL: https://github.com/huashen218/bidirectional-alignment-tax
- Paper list format: Reading list (markdown or structured file) containing paper references with DOI/arXiv IDs and venue information
- Corpus characteristics: Interdisciplinary alignment papers spanning ML/NLP venues (NeurIPS, ICML, ICLR, ACL, EMNLP) and HCI venues (CHI, CSCW, IUI)
- Reference paper: Shen et al. 2024 (arXiv:2406.09264) — describes corpus construction and systematic review methodology

**Citation edge source:** Semantic Scholar Academic Graph API (S2AG)
- Base URL: https://api.semanticscholar.org/graph/v1
- Endpoints used:
  - `POST /paper/batch` — resolve paper IDs (batch up to 500); fields: `paperId,externalIds,title,venue,fieldsOfStudy,year`
  - `GET /paper/{id}/references` — retrieve outgoing citations; fields: `citedPaper.paperId,citedPaper.title,citedPaper.venue,citedPaper.fieldsOfStudy`
- Rate limit: 40 req/min unauthenticated; 100 req/sec with API key
- Local JSON cache: all responses cached by paper ID to `cache/s2ag/` directory

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: https://github.com/huashen218/bidirectional-alignment-tax + https://api.semanticscholar.org/graph/v1
- Code:
```python
# Step 1: Clone corpus
import subprocess
subprocess.run(["git", "clone", "https://github.com/huashen218/bidirectional-alignment-tax", "corpus"])

# Step 2: Parse paper IDs from corpus (adjust path based on actual repo structure)
import json, re
from pathlib import Path

def extract_paper_ids(corpus_dir):
    """Extract DOI/arXiv IDs from corpus files."""
    ids = []
    for f in Path(corpus_dir).rglob("*.md"):
        text = f.read_text()
        arxiv_ids = re.findall(r'arxiv\.org/abs/([\d.]+)', text, re.I)
        ids.extend([f"arXiv:{aid}" for aid in arxiv_ids])
        dois = re.findall(r'doi\.org/(10\.\S+)', text)
        ids.extend(dois)
    return list(set(ids))
```

### Models

#### Baseline Model

**Type:** Paper ID resolution rate only (no citation graph)
**Baseline check:** Resolve paper IDs against S2AG without any citation retrieval. Measure coverage rate (% of IDs that return a valid S2AG `paperId`). This establishes the upper bound for citation graph construction.

**Baseline metric:** Coverage rate = resolved_count / total_corpus_ids

**Loading Information** (for Phase 4 download):
- Method: S2AG batch API — no model download required
- Identifier: `POST https://api.semanticscholar.org/graph/v1/paper/batch`
- Code:
```python
import requests, time, json
from pathlib import Path

CACHE_DIR = Path("cache/s2ag")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
S2AG_BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "paperId,externalIds,title,venue,fieldsOfStudy,year"

def resolve_papers_batch(paper_ids: list[str]) -> dict:
    """Batch resolve paper IDs via S2AG. Returns {input_id: paper_data}."""
    cache_key = "batch_" + "_".join(sorted(paper_ids))[:50]
    cache_file = CACHE_DIR / f"{hash(cache_key)}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    
    # S2AG batch endpoint: up to 500 IDs
    chunks = [paper_ids[i:i+500] for i in range(0, len(paper_ids), 500)]
    results = {}
    for chunk in chunks:
        resp = requests.post(
            f"{S2AG_BASE}/paper/batch",
            params={"fields": FIELDS},
            json={"ids": chunk}
        )
        resp.raise_for_status()
        for item, pid in zip(resp.json(), chunk):
            results[pid] = item  # None if not found
        time.sleep(1.5)  # ~40 req/min unauthenticated
    
    cache_file.write_text(json.dumps(results))
    return results
```

#### Proposed Model

**Architecture:** Baseline + citation graph construction + venue classification + cross-group edge counting

**Core Mechanism Implementation:**

```python
import networkx as nx
from scipy.stats import chi2_contingency, fisher_exact
from collections import defaultdict

# ── Venue Classification ──────────────────────────────────────────────────────

ML_NLP_VENUES = {"neurips", "icml", "iclr", "acl", "emnlp", "naacl", "coling", "findings"}
HCI_VENUES = {"chi", "cscw", "iui", "uist", "assets"}
ML_NLP_FOL = {"Computer Science", "Linguistics"}  # fieldsOfStudy values
HCI_FOL = {"Human-Computer Interaction"}

# Three pre-specified classification schemes (pre-registered before data inspection)
SCHEMES = {
    "scheme1": {  # ACL/EMNLP as ML_NLP
        "ml_nlp": ML_NLP_VENUES | {"acl", "emnlp"},
        "hci": HCI_VENUES,
    },
    "scheme2": {  # ACL/EMNLP excluded (bridge-neutral)
        "ml_nlp": {"neurips", "icml", "iclr"},
        "hci": HCI_VENUES,
    },
    "scheme3": {  # fieldsOfStudy-primary, venue-fallback
        # Uses S2AG fieldsOfStudy field primarily; venue string as fallback
        "use_fos": True,
        "ml_nlp": ML_NLP_VENUES | {"acl", "emnlp"},
        "hci": HCI_VENUES,
    }
}

def classify_paper(paper: dict, scheme: dict) -> str | None:
    """Return 'ML_NLP', 'HCI', or None (unclassified)."""
    if scheme.get("use_fos"):
        fos = set(paper.get("fieldsOfStudy") or [])
        if "Human-Computer Interaction" in fos:
            return "HCI"
        if fos & {"Computer Science", "Linguistics"}:
            venue = (paper.get("venue") or "").lower()
            if any(v in venue for v in HCI_VENUES):
                return "HCI"
            return "ML_NLP"
    # Venue-string-based fallback
    venue = (paper.get("venue") or "").lower()
    if any(v in venue for v in scheme["hci"]):
        return "HCI"
    if any(v in venue for v in scheme["ml_nlp"]):
        return "ML_NLP"
    return None

# ── Citation Graph Construction ───────────────────────────────────────────────

def get_references_cached(paper_id: str) -> list[dict]:
    """Fetch paper references from S2AG with local cache."""
    cache_file = CACHE_DIR / f"refs_{paper_id}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    resp = requests.get(
        f"{S2AG_BASE}/paper/{paper_id}/references",
        params={"fields": "citedPaper.paperId,citedPaper.title,citedPaper.venue,citedPaper.fieldsOfStudy", "limit": 1000}
    )
    if resp.status_code == 200:
        data = [r["citedPaper"] for r in resp.json().get("data", []) if r.get("citedPaper")]
        cache_file.write_text(json.dumps(data))
        time.sleep(1.5)
        return data
    time.sleep(2)
    return []

def build_citation_graph(resolved_papers: dict, scheme: dict) -> tuple[nx.DiGraph, dict, dict]:
    """Build directed citation graph; return graph, group assignments, cross-group edge counts."""
    corpus_ids = {p["paperId"] for p in resolved_papers.values() if p and p.get("paperId")}
    groups = {}
    for p in resolved_papers.values():
        if p and p.get("paperId"):
            g = classify_paper(p, scheme)
            if g:
                groups[p["paperId"]] = g

    G = nx.DiGraph()
    G.add_nodes_from(corpus_ids)
    
    edge_counts = defaultdict(int)  # (src_group, tgt_group) -> count
    
    for paper_id in corpus_ids:
        refs = get_references_cached(paper_id)
        src_group = groups.get(paper_id)
        if not src_group:
            continue
        for ref in refs:
            ref_id = ref.get("paperId")
            if ref_id and ref_id in corpus_ids:  # within-corpus edge only
                G.add_edge(paper_id, ref_id)
                tgt_group = groups.get(ref_id)
                if tgt_group:
                    edge_counts[(src_group, tgt_group)] += 1
    
    return G, groups, edge_counts

# ── H-E1 Verification ────────────────────────────────────────────────────────

def verify_h_e1(paper_ids: list[str]) -> dict:
    """Run full H-E1 verification. Returns coverage rate, edge counts, pass/fail."""
    resolved = resolve_papers_batch(paper_ids)
    valid = {k: v for k, v in resolved.items() if v and v.get("paperId")}
    coverage = len(valid) / len(paper_ids)
    
    results = {"coverage": coverage, "resolved": len(valid), "total": len(paper_ids), "schemes": {}}
    
    for scheme_name, scheme in SCHEMES.items():
        G, groups, edge_counts = build_citation_graph(valid, scheme)
        ai_hci = edge_counts[("ML_NLP", "HCI")]
        hci_ai = edge_counts[("HCI", "ML_NLP")]
        cross_group_total = ai_hci + hci_ai
        results["schemes"][scheme_name] = {
            "AI_HCI": ai_hci, "HCI_AI": hci_ai,
            "AI_AI": edge_counts[("ML_NLP", "ML_NLP")],
            "HCI_HCI": edge_counts[("HCI", "HCI")],
            "cross_group_total": cross_group_total,
            "pass": coverage >= 0.70 and cross_group_total >= 30
        }
    
    results["gate_pass"] = (
        coverage >= 0.70 and
        any(s["cross_group_total"] >= 30 for s in results["schemes"].values())
    )
    return results
```

### Training Protocol

Not applicable — this is a data infrastructure existence check, not a training experiment. No model parameters are learned or optimized. The pipeline is fully deterministic:

1. Clone huashen218 corpus → extract paper IDs (~400)
2. Batch-resolve all IDs via S2AG `/paper/batch` → measure coverage
3. Classify resolved papers into ML_NLP / HCI groups under all 3 schemes
4. Retrieve reference lists for all resolved papers → build within-corpus directed edge graph
5. Count cross-group edges (AI→HCI, HCI→AI) under each scheme
6. Evaluate H-E1 gate: coverage ≥70% AND any scheme has cross-group total ≥30
7. Cache all S2AG responses locally for downstream hypotheses (H-M1/M2/M3 reuse same data)

**Runtime estimate:** ~15–40 minutes for full corpus at unauthenticated rate (40 req/min × ~400 references requests). With S2AG API key: <5 minutes.

**ponytail:** sequential API calls with sleep(1.5), upgrade to concurrent.futures if throughput is a bottleneck.

### Evaluation

**Primary metrics (H-E1 gate):**
1. **Coverage rate** = resolved_papers / total_corpus_ids (target: ≥0.70)
2. **Cross-group edge count** = AI→HCI + HCI→AI within-corpus edges (target: ≥30, under ≥1 of 3 schemes)

**Secondary metrics (diagnostic):**
3. Classification rate = classified_papers / resolved_papers (target: ≥80%)
4. Edge count stability across 3 schemes (target: ±20% of Scheme 1 count)
5. Venue distribution of unresolved papers (non-systematic dropout check)

**Failure mode documentation:**
- Unresolved paper reasons: no DOI/arXiv, preprint not indexed, indexing lag
- Unclassified paper reasons: ambiguous venue (workshop papers, interdisciplinary journals)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: data infrastructure verification (coverage + graph edge counting)
- Library: `scipy.stats` (chi2_contingency, fisher_exact for downstream use), `networkx` (DiGraph), `collections.defaultdict`, `requests`
- Code:
```python
# No special metrics loading — all computed from graph edge_counts dict
# H-E1 pass: coverage >= 0.70 AND cross_group >= 30
gate_pass = (coverage >= 0.70) and (cross_group_total >= 30)
print(f"Coverage: {coverage:.1%} | Cross-group edges: {cross_group_total} | Gate: {'PASS' if gate_pass else 'FAIL'}")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Two-panel bar chart — (1) coverage rate vs 70% threshold; (2) cross-group edge count vs 30-edge threshold, shown for all 3 classification schemes

#### Additional Figures (LLM Autonomous)

1. **Resolution failure distribution**: Bar chart of unresolved papers by venue — confirms non-systematic dropout
2. **Edge count matrix heatmap**: 2×2 heatmap of (AI→AI, AI→HCI, HCI→AI, HCI→HCI) under each of 3 schemes — establishes data ready for H-M1/M2/M3
3. **Corpus venue breakdown**: Pie chart of resolved papers by venue group (ML_NLP / HCI / unclassified) under Scheme 1

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (S2AG API accessible; corpus cloned successfully)
2. Coverage ≥ 70% of corpus papers resolved
3. Cross-group edges ≥ 30 (under ≥1 of 3 pre-specified venue classification schemes)

**Failure exits are pre-planned (not improvised):**
- 50–70% coverage: proceed with non-systematic dropout argument; document in output
- <30 edges: pivot to descriptive statistics + bridge paper analysis; no chi-squared test
- API unavailable: check S2AG status; use locally cached responses if available

---

## Appendix: Reference Implementations

| Source | URL | Relevance |
|--------|-----|-----------|
| smaniches/semantic-scholar-mcp | https://github.com/smaniches/semantic-scholar-mcp | S2AG citation graph API usage patterns |
| mirandrom/PyS2 | https://github.com/mirandrom/PyS2/blob/master/s2/api.py | S2AG endpoint URL construction, session management |
| zongmin-yu/semantic-scholar-skills resolve.py | https://github.com/zongmin-yu/semantic-scholar-skills | Multi-ID resolution fallback chain (DOI → arXiv → title search) |
| EvoScientist/EvoSkills fetch_paper.py | https://github.com/EvoScientist/EvoSkills/blob/main/skills/paper-navigator/scripts/fetch_paper.py | `normalize_paper_id()`, `_strip_arxiv_version()` patterns |
| S2AG Official API Docs | https://api.semanticscholar.org/api-docs/ | Batch paper endpoint, fieldsOfStudy field, references endpoint spec |
| S2AG Tutorial | https://www.semanticscholar.org/product/api/tutorial | fieldsOfStudy filtering, venue filtering, pagination with token |
| semanticscholar PyPI docs | https://semanticscholar.readthedocs.io/en/stable/ | Python library wrapper: `get_paper_references()`, `get_paper_citations()` |
| huashen218/bidirectional-alignment-tax | https://github.com/huashen218/bidirectional-alignment-tax | Target corpus — source of ~400 paper IDs |
| Shen et al. 2024 | arXiv:2406.09264 | Corpus methodology; 57% scope reduction: BUILD_ON |
| Wahle et al. 2023 EMNLP | arXiv:2310.14870 | S2AG cross-field citation precedent; 10-30x within-field rate prior |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20T00:00:00+00:00

### Workflow History for This Hypothesis

| Phase | Action | Date | Status |
|-------|--------|------|--------|
| Phase 2B | H-E1 specification written | 2026-08-20 | COMPLETE |
| Phase 2C | Experiment brief designed | 2026-08-20 | COMPLETE |
| Phase 3 | Implementation planning | TBD | NOT_STARTED |
| Phase 4 | Code implementation | TBD | NOT_STARTED |

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant prior cases found), Exa (GitHub — 5 S2AG implementation references found), Serena (skipped — no local codebase)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
