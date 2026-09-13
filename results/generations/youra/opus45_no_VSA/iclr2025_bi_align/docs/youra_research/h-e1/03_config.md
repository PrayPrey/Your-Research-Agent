# Config: H-E1 Agency Proxy Extraction

**Type:** EXISTENCE (PoC) — single fixed config, no sweeps
**Applied:** Standard PyTorch/sklearn defaults (no KB pattern matched; hardcoded-dict pattern used per architecture.py spec)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design, no existing code
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (module-level constants in `config.py`)

---

## Config Schema (`h-e1/code/config.py`)

```python
RANDOM_STATE = 42

TFIDF_PARAMS = dict(
    ngram_range=(1, 2),
    max_features=5000,
)

LOGREG_PARAMS = dict(
    C=1.0,
    max_iter=1000,
    random_state=RANDOM_STATE,
)

PROXY_TYPES = [
    "clarifying_question",
    "option_enumeration",
    "epistemic_hedging",
    "explicit_deferral",
]

# FR-4 regex patterns per proxy (used by AgencyProxyDetector.match_pattern)
PROXY_PATTERNS = {
    "clarifying_question": [
        r"what do you mean",
        r"could you clarify",
        r"are you asking",
    ],
    "option_enumeration": [
        r"there are several options",
        r"you could either",
        r"^\s*\d+[.)]",  # numbered list item
    ],
    "epistemic_hedging": [
        r"i'?m not sure",
        r"it'?s possible",
        r"i think",
        r"\bmaybe\b",
    ],
    "explicit_deferral": [
        r"recommend consulting",
        r"a professional would",
        r"i can'?t advise",
    ],
}

AUROC_TARGET = 0.8          # MUST_WORK gate (mean AUROC across proxies)
AUROC_BASELINE_MIN = 0.5    # each proxy must beat random baseline
AUROC_STRONG_SIGNAL = 0.7   # >=3/4 proxies must reach this

TEST_SIZE = 0.2             # train/eval split fraction for classifier fit/predict_proba
DATASETS = ["Anthropic/hh-rlhf", "allenai/reward-bench"]  # HF dataset ids (harmless-base, helpful-base, safety subset)

FIGURES_DIR = "h-e1/figures"
```

**Non-standard**: `TEST_SIZE=0.2` is not in PRD/architecture — needed since evaluate.py computes AUROC on held-out predictions; standard sklearn default.

No hyperparameter grid, no ablations, no multi-seed — PoC gate is pass/fail on `AUROC_TARGET`.

---

## Subtasks

0/0 used — PoC scope, no subtask decomposition (per budget).
