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
FORMAL_SYNTAX_RE: re.Pattern = re.compile(FORMAL_SYNTAX_PATTERN)

# ── Paths ─────────────────────────────────────────────────────────────────────

RESULTS_DIR: str = "results"
FIGURES_DIR: str = "docs/youra_research/h-m1/figures"

# ── Stats ─────────────────────────────────────────────────────────────────────

ALPHA: float = 0.05
ETA_SQ_THRESHOLD: float = 0.1


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
    anova_typ: int = 2


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
    loader: str = "hf"
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
