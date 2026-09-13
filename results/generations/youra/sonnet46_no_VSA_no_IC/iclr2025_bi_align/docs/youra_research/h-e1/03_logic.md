# Logic Design: H-E1 Data Infrastructure Verification

**Hypothesis:** h-e1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-20
**Author:** yoon303b@gmail.com

Applied: stateless-function pipeline pattern
Applied: cache-aside pattern for API calls

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** No local codebase to analyze — new self-contained pipeline.
**Findings:** All APIs designed from scratch; no existing symbols to verify.

---

## Subtask S-4a: Venue Classification Logic

### Data Shapes

```python
# Input: paper dict from S2AG (single resolved paper)
paper: dict = {
    "paperId": str,           # S2AG canonical ID
    "externalIds": dict,      # {"ArXiv": "...", "DOI": "..."}
    "title": str,
    "venue": str,             # e.g. "CHI 2023", "Proceedings of NeurIPS 2022"
    "fieldsOfStudy": list[str] | None,  # e.g. ["Computer Science", "Human-Computer Interaction"]
    "year": int | None,
}

# Scheme dict shapes
scheme_venue: dict = {
    "use_fos": False,         # scheme1, scheme2
    "ml_nlp": frozenset[str], # lowercase venue substrings
    "hci": frozenset[str],
}
scheme_fos: dict = {
    "use_fos": True,          # scheme3
    "ml_nlp": frozenset[str],
    "hci": frozenset[str],
}

# Output group label
GroupLabel = Literal["ML_NLP", "HCI"] | None

# Full classification output
paper_groups: dict[str, GroupLabel]  # {paperId: "ML_NLP" | "HCI" | None}
```

### API Signatures

```python
def classify_paper(paper: dict, scheme: dict) -> str | None:
    """
    Classify a single S2AG paper into ML_NLP, HCI, or None.

    Args:
        paper: S2AG paper dict with 'venue' and 'fieldsOfStudy' fields.
        scheme: Classification scheme dict with keys:
                - 'ml_nlp': frozenset of lowercase venue substrings
                - 'hci': frozenset of lowercase venue substrings
                - 'use_fos': bool (True → fieldsOfStudy primary, venue fallback)

    Returns:
        "ML_NLP" | "HCI" | None (unclassified)

    Logic:
        scheme3 (use_fos=True):
            fos = set(paper.get("fieldsOfStudy") or [])
            if "Human-Computer Interaction" in fos → "HCI"
            elif fos & {"Computer Science", "Linguistics"}:
                venue = paper.get("venue", "").lower()
                if any HCI venue substring in venue → "HCI"
                else → "ML_NLP"
            else → venue-string fallback (same as scheme1)
        scheme1/scheme2 (use_fos=False):
            venue = paper.get("venue", "").lower()
            if any hci substring in venue → "HCI"
            elif any ml_nlp substring in venue → "ML_NLP"
            else → None
    """


def classify_all(
    resolved: dict[str, dict | None],
    scheme: dict,
) -> dict[str, str | None]:
    """
    Classify all resolved papers under a single scheme.

    Args:
        resolved: {input_id: paper_data | None} from resolve_papers()
        scheme: Classification scheme dict

    Returns:
        {paperId: "ML_NLP" | "HCI" | None}
        Keys are S2AG paperIds (not input IDs); None-valued papers skipped.
    """
```

### Pseudo-code: classify_paper (all 3 paths)

```python
def classify_paper(paper, scheme):
    if scheme.get("use_fos"):
        fos = set(paper.get("fieldsOfStudy") or [])
        if "Human-Computer Interaction" in fos:
            return "HCI"
        if fos & {"Computer Science", "Linguistics"}:
            venue = (paper.get("venue") or "").lower()
            if any(v in venue for v in scheme["hci"]):
                return "HCI"
            return "ML_NLP"
        # fall through to venue-string check
    venue = (paper.get("venue") or "").lower()
    if any(v in venue for v in scheme["hci"]):
        return "HCI"
    if any(v in venue for v in scheme["ml_nlp"]):
        return "ML_NLP"
    return None
```

---

## Subtask S-4b: Graph Construction + Gate Evaluation Logic

### Data Shapes

```python
# Edge count matrix
EdgeKey = tuple[str, str]  # e.g. ("ML_NLP", "HCI")
edge_counts: dict[EdgeKey, int]  # defaultdict(int)
# Keys: ("ML_NLP","ML_NLP"), ("ML_NLP","HCI"), ("HCI","ML_NLP"), ("HCI","HCI")

# Graph
G: nx.DiGraph  # nodes = paperId strings; edges = within-corpus citation links

# Gate result
gate_result: dict = {
    "coverage": float,        # resolved / total
    "resolved": int,
    "total": int,
    "schemes": {
        "scheme1": {
            "ML_NLP_ML_NLP": int,
            "ML_NLP_HCI": int,
            "HCI_ML_NLP": int,
            "HCI_HCI": int,
            "cross_group_total": int,   # ML_NLP_HCI + HCI_ML_NLP
            "pass": bool,               # coverage>=0.70 AND cross_group>=30
        },
        "scheme2": { ... },
        "scheme3": { ... },
    },
    "gate_pass": bool,  # coverage>=0.70 AND any scheme cross_group_total>=30
}

# Reference item from S2AG /references endpoint
ref_item: dict = {
    "citedPaper": {
        "paperId": str | None,
        "title": str,
        "venue": str,
        "fieldsOfStudy": list[str] | None,
    }
}
```

### API Signatures

```python
def fetch_references(paper_id: str, cache_dir: Path) -> list[dict]:
    """
    Fetch outgoing references for a paper from S2AG with local cache.

    Args:
        paper_id: S2AG paperId string.
        cache_dir: Directory for JSON cache files.

    Returns:
        List of citedPaper dicts (fields: paperId, title, venue, fieldsOfStudy).
        Returns [] on 404, network error after 3 retries, or empty response.

    Side effects:
        Writes cache_dir/refs_{paper_id}.json on first fetch.
        Sleeps SLEEP_SECS after each uncached GET.
    """


def build_graph(
    resolved: dict[str, dict | None],
    groups: dict[str, str | None],
    cache_dir: Path,
) -> tuple[nx.DiGraph, dict[tuple[str, str], int]]:
    """
    Build within-corpus directed citation graph and count cross-group edges.

    Args:
        resolved: {input_id: paper_data} from resolve_papers(); None values ignored.
        groups: {paperId: "ML_NLP" | "HCI" | None} from classify_all().
        cache_dir: S2AG cache directory for fetch_references().

    Returns:
        (G, edge_counts) where:
          G: nx.DiGraph with corpus paperIds as nodes, within-corpus citation edges
          edge_counts: defaultdict(int) keyed by (src_group, tgt_group)

    Algorithm:
        corpus_ids = {p["paperId"] for p in resolved.values() if p and p.get("paperId")}
        G = nx.DiGraph(); G.add_nodes_from(corpus_ids)
        for paper_id in corpus_ids:
            refs = fetch_references(paper_id, cache_dir)
            src_group = groups.get(paper_id)
            for ref in refs:
                ref_id = ref.get("paperId")
                if ref_id and ref_id in corpus_ids:   # within-corpus only
                    G.add_edge(paper_id, ref_id)
                    tgt_group = groups.get(ref_id)
                    if src_group and tgt_group:
                        edge_counts[(src_group, tgt_group)] += 1
    """


def evaluate_gate(
    coverage: float,
    resolved_count: int,
    total_count: int,
    scheme_results: dict[str, dict],
) -> dict:
    """
    Evaluate H-E1 gate from coverage and per-scheme edge counts.

    Args:
        coverage: resolved_count / total_count
        resolved_count: number of papers with valid S2AG paperId
        total_count: total corpus IDs submitted
        scheme_results: {scheme_name: {edge_counts dict}} from build_graph per scheme

    Returns:
        gate_result dict (see data shape above).

    Gate logic:
        gate_pass = (coverage >= COVERAGE_GATE) and
                    any(s["cross_group_total"] >= CROSS_GROUP_GATE
                        for s in gate_result["schemes"].values())
    """
```

### Pseudo-code: _api_get (cache + retry)

```python
def _api_get(url: str, params: dict, cache_path: Path) -> dict | list:
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    for attempt in range(MAX_RETRIES):
        try:
            headers = {"x-api-key": API_KEY} if API_KEY else {}
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            data = resp.json()
            cache_path.write_text(json.dumps(data))
            time.sleep(SLEEP_SECS if not API_KEY else 0.01)
            return data
        except requests.RequestException:
            time.sleep(2 ** attempt)
    return {}  # exhausted retries
```

---

## Error Conditions

| Condition | Handling |
|-----------|----------|
| HTTP 429 (rate limit) | Exponential backoff, max 3 retries |
| HTTP 404 (paper not found) | Record as unresolved; `resolved[input_id] = None` |
| HTTP 5xx | Retry 3×; on exhaustion return `{}` / `[]` |
| Network timeout | 30s timeout per request; retry 3× |
| `fieldsOfStudy` is None | Treat as empty list in scheme3 |
| `venue` is None or empty | Return None (unclassified) |
| Paper in refs not in corpus | Skip (not a within-corpus edge) |
| `paperId` is None in ref | Skip ref |
