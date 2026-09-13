"""H-E1 constants and configuration."""
import os
from dataclasses import dataclass, field
from pathlib import Path

S2AG_BASE: str = "https://api.semanticscholar.org/graph/v1"
CORPUS_REPO: str = "https://github.com/huashen218/bidirectional-alignment-reading-list"
BATCH_FIELDS: str = "paperId,externalIds,title,venue,fieldsOfStudy,year"
REF_FIELDS: str = "citedPaper.paperId,citedPaper.title,citedPaper.venue,citedPaper.fieldsOfStudy"
COVERAGE_GATE: float = 0.70
CROSS_GROUP_GATE: int = 30
SLEEP_SECS: float = float(os.environ.get("H_E1_SLEEP", "1.5"))
MAX_RETRIES: int = 3
API_KEY: str = os.environ.get("S2AG_API_KEY", "")

# Authenticated tier: 100 req/sec → 0.01s sleep
if API_KEY:
    SLEEP_SECS = 0.01

ML_NLP_VENUES_S1: frozenset = frozenset({
    "neurips", "icml", "iclr", "acl", "emnlp", "naacl", "coling", "findings"
})
ML_NLP_VENUES_S2: frozenset = frozenset({"neurips", "icml", "iclr"})
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
        "ml_nlp": ML_NLP_VENUES_S1,
        "hci": HCI_VENUES,
        "use_fos": True,
    },
}


@dataclass
class S2AGConfig:
    base_url: str = S2AG_BASE
    batch_fields: str = BATCH_FIELDS
    ref_fields: str = REF_FIELDS
    batch_size: int = 500
    ref_limit: int = 1000
    sleep_secs: float = field(default_factory=lambda: SLEEP_SECS)
    max_retries: int = MAX_RETRIES
    api_key: str = field(default_factory=lambda: API_KEY)

    def __post_init__(self):
        if self.api_key:
            self.sleep_secs = 0.01


@dataclass
class GateConfig:
    coverage_gate: float = COVERAGE_GATE
    cross_group_gate: int = CROSS_GROUP_GATE


@dataclass
class PathConfig:
    corpus_dir: Path = Path("corpus")
    cache_dir: Path = Path("cache/s2ag")
    data_dir: Path = Path("data")
    figures_dir: Path = Path("figures")
    results_dir: Path = Path("results")

    def __post_init__(self):
        for d in (self.cache_dir, self.data_dir, self.figures_dir, self.results_dir):
            d.mkdir(parents=True, exist_ok=True)


@dataclass
class ExperimentConfig:
    s2ag: S2AGConfig = field(default_factory=S2AGConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    seed: int = 42
