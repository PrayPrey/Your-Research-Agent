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

PROXY_PATTERNS = {
    "clarifying_question": [
        r"what do you mean",
        r"could you clarify",
        r"could you explain",
        r"could you specify",
        r"are you asking",
        r"do you mean",
    ],
    "option_enumeration": [
        r"there are several options",
        r"there are multiple options",
        r"here are several",
        r"here are a few",
        r"you could either",
        r"you could choose",
        r"^\s*\d+[.)]",
        r"\bfirst\b.*\bsecond\b",
        r"\balternatively\b",
    ],
    "epistemic_hedging": [
        r"i'?m not sure",
        r"i am not sure",
        r"i'?m not certain",
        r"it'?s possible",
        r"it is possible",
        r"\bi think\b",
        r"\bi believe\b",
        r"\bmaybe\b",
        r"\bperhaps\b",
        r"\bpossibly\b",
    ],
    "explicit_deferral": [
        r"recommend consulting",
        r"recommend speaking",
        r"a professional would",
        r"a doctor would",
        r"a lawyer would",
        r"an expert would",
        r"i can'?t advise",
        r"i cannot advise",
        r"i shouldn'?t advise",
        r"seek professional",
        r"seek medical",
        r"seek legal",
    ],
}

AUROC_TARGET = 0.8
AUROC_BASELINE_MIN = 0.5
AUROC_STRONG_SIGNAL = 0.7

TEST_SIZE = 0.2
FIGURES_DIR = "h-e1/figures"
