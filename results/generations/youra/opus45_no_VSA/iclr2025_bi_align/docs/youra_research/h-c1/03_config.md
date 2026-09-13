# Configuration: H-C1 Semantic Coherence Clustering

**Type:** CONDITION (fixed config, no hyperparameter sweep)
**Applied:** No matching KB pattern found (searched "experiment configuration dataclass YAML" — only unrelated diffusion-model hits). Used module-level constants pattern, matching H-M2/H-E1 convention.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: config classes verified from base code (`h-m2/code/config.py`, via H-C1 architecture doc's prior Serena analysis)
**Config Files Found**: `h-m2/code/config.py` (module-level constants, no dataclass)
**Pattern Used**: Module-level constants (dict-style), not dataclass — matching H-M2/H-E1 convention for consistency.

---

## Inherited Configuration (Base Hypothesis)

Verified from `h-m2/code/config.py` (actual code):

```python
# From: h-m2/code/config.py (ACTUAL CODE)
RANDOM_STATE = 42
```

H-C1's `slice_loader.py` reruns H-M2's pipeline (`bai.py`, `reward.py`, `analysis.py`) via `sys.path.insert`, reusing `RANDOM_STATE=42` for deterministic same-slice recomputation (no `disagreement_samples.json` exists on disk — confirmed absent by architecture doc's Serena analysis).

---

## H-C1 Configuration (`h-c1/code/config.py`)

Module-level constants, mirrors H-M2/H-E1 style (no dataclass):

```python
RANDOM_STATE = 42

# Embedding
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# UMAP
UMAP_N_NEIGHBORS = 15
UMAP_N_COMPONENTS = 5
UMAP_METRIC = "cosine"

# HDBSCAN
MIN_CLUSTER_SIZE = 50
HDBSCAN_METRIC = "euclidean"
HDBSCAN_SELECTION_METHOD = "eom"

# BERTopic
TOP_N_WORDS = 10

# Agency pattern classification
AGENCY_MATCH_THRESHOLD = 2  # min pattern categories matched (of 4)

# Gate thresholds (from PRD success criteria)
COVERAGE_PASS_THRESHOLD = 0.70
AGENCY_RATE_PASS_THRESHOLD = 0.50
AGENCY_RATE_PARTIAL_THRESHOLD = 0.30

FIGURES_DIR = "h-c1/figures"
```

All values taken directly from PRD/experiment brief (FR-3 UMAP/HDBSCAN params, FR-5/FR-6 gate thresholds) — no tuning needed for this CONDITION analysis (fixed config, single run).

### Agency Pattern Keywords (`h-c1/code/agency.py`)

```python
AGENCY_PATTERNS = {
    "clarifying": ["clarify", "understand", "mean", "asking", "question", "sure"],
    "deferring": ["prefer", "choice", "decide", "up to you", "your call", "depends"],
    "hedging": ["might", "perhaps", "possibly", "could be", "uncertain", "not sure"],
    "option_enum": ["option", "alternatively", "or", "either", "choices", "ways"],
}
```

### Subtasks

None — Budget is 0 subtasks; all 9 epic tasks (C-1..C-9) are Low complexity per architecture allocation table.

---

## Self-Validation

- [x] ONE format only: module-level constants (dict-style), matches H-M2/H-E1 convention
- [x] No ASCII diagrams
- [x] Archon KB searched — no match, noted
- [x] Rationale given only for non-obvious choices (thresholds sourced from PRD)
- [x] 0 subtasks used (budget: 0)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included with verified H-M2 field names
