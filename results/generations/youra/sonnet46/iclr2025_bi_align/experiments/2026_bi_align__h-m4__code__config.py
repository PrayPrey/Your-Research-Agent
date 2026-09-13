"""
config.py - Configuration dataclasses for h-m4 PM-Score OLS Mediation Regression.

Extends h-m2 ExperimentConfig with RegressionConfig, surface feature constants,
and chosen/rejected branch cache prefix support.
"""
import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional


# Module-level constants
POLITENESS_TOKENS: FrozenSet[str] = frozenset({
    'please', 'thank', 'sorry', 'appreciate', 'certainly', 'happy'
})

SURFACE_FEATURE_COLS: List[str] = [
    'response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len'
]

TIER_ORDER: List[str] = [
    "helpful-base", "helpful-rejection-sampled", "helpful-online"
]

MODEL_NAMES: List[str] = [
    "all-MiniLM-L6-v2", "paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2"
]

BRANCH_LABELS = ("chosen", "rejected")

PM_PROXY_MAP: Dict[str, int] = {"chosen": 1, "rejected": 0}

FEATURE_VALIDATION_THRESHOLDS: Dict[str, Dict] = {
    'response_length': {'min': 0,   'max': 10000},
    'bullet_density':  {'min': 0.0, 'max': 1.0},
    'politeness_freq': {'min': 0.0, 'max': 1.0},
    'ttr':             {'min': 0.0, 'max': 1.0},
    'mean_sent_len':   {'min': 0.0, 'max': 500.0},
}

REGRESSION_PLOT_CONFIG: Dict = {
    "ci_level": 0.95,
    "reference_line_y": 0.0,
    "reference_line_style": "--",
    "reference_line_color": "gray",
    "axis_label_beta_pm": r"$\hat{\beta}_{PM}$",
    "axis_label_csem": r"$C_{sem}^{H \leftarrow A}$",
    "axis_label_pm_proxy": "PM Proxy (1=chosen, 0=rejected)",
    "axis_label_model": "SBERT Model",
    "figsize_default": (8, 5),
    "figsize_forest": (10, 7),
}


@dataclass
class CacheConfig:
    """Cache configuration for datasets and embeddings."""
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m2/code/embeddings"  # reuse h-m2 embeddings cache
    models: List[str] = field(default_factory=lambda: MODEL_NAMES)
    tiers: List[str] = field(default_factory=lambda: TIER_ORDER)
    encode_batch_size: int = 256
    chosen_cache_prefix: str = "a_chosen"
    rejected_cache_prefix: str = "a_rejected"
    # h-m2 compat: cache key templates
    h_m1_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_H_next_{tier}.npy",
        "{model}_A_curr_{tier}.npy",
    ])
    h_m2_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_A_next_{tier}.npy",
        "{model}_H_curr_{tier}.npy",
    ])


@dataclass
class StatisticsConfig:
    """Statistical test configuration."""
    seed: int = 42
    alpha: float = 0.05
    n_bootstrap: int = 1000
    knn_k: int = 5
    knn_n_jobs: int = 1   # CRITICAL: never -1 at 155k scale
    tiers_required: int = 2   # h-m2 compat field
    models_required: int = 2  # >=2/3 for gate
    min_n_pairs: int = 1000
    cohen_d_threshold: float = 0.1  # h-m2 compat field


@dataclass
class RegressionConfig:
    """OLS regression configuration for h-m4 mediation analysis."""
    cov_type: str = 'HC3'
    tier_reference: str = 'helpful-base'
    min_nobs: int = 1000
    vif_warn_threshold: float = 10.0


@dataclass
class FigureConfig:
    """Figure output configuration."""
    figures_dir: str = "../figures"
    dpi: int = 150
    save_format: str = "png"
    tier_palette: Dict[str, str] = field(default_factory=lambda: {
        "helpful-base": "#4C72B0",
        "helpful-rejection-sampled": "#DD8452",
        "helpful-online": "#55A868",
    })
    branch_palette: Dict[str, str] = field(default_factory=lambda: {
        "chosen": "#2196F3",
        "rejected": "#F44336",
    })


@dataclass
class ExperimentConfig:
    """Top-level experiment configuration for h-m4."""
    hypothesis_id: str = "h-m4"
    cache: CacheConfig = field(default_factory=CacheConfig)
    stats: StatisticsConfig = field(default_factory=StatisticsConfig)
    regression: RegressionConfig = field(default_factory=RegressionConfig)
    figures: FigureConfig = field(default_factory=FigureConfig)
    output_dir: str = "outputs"
    results_dir: str = "../results"
    dry_run: bool = False
    n_samples_dry_run: int = 500
    ipw_ks_threshold: float = 0.05
    singularity_warn: bool = True

    @property
    def cache_dir(self) -> str:
        return self.cache.cache_dir

    @property
    def figures_dir(self) -> str:
        return self.figures.figures_dir


def verify_cache(cache_config: CacheConfig):
    """Verify required .npy cache files exist (h-m2 compat function).

    Returns:
        Tuple of (all_present: bool, status: {key: exists_bool})
    """
    import os
    status = {}
    templates = [
        "{model}_H_next_{tier}.npy",
        "{model}_A_curr_{tier}.npy",
        "{model}_A_next_{tier}.npy",
        "{model}_H_curr_{tier}.npy",
    ]
    model_slug_map = {
        "all-MiniLM-L6-v2": "minilm",
        "paraphrase-MiniLM-L6-v2": "paraphrase",
        "all-mpnet-base-v2": "mpnet",
    }
    tier_slug_map = {
        "helpful-base": "base",
        "helpful-rejection-sampled": "rejection_sampled",
        "helpful-online": "online",
    }
    embeddings_dir = cache_config.embeddings_dir
    for template in templates:
        for model in cache_config.models:
            model_slug = model_slug_map.get(model, model)
            for tier in cache_config.tiers:
                tier_slug = tier_slug_map.get(tier, tier.replace("-", "_"))
                key = template.format(model=model_slug, tier=tier_slug)
                path = os.path.join(embeddings_dir, key)
                status[key] = os.path.exists(path)
    all_present = all(status.values())
    return all_present, status


def get_missing_h_m2_keys(cache_config: CacheConfig):
    """Return list of missing h-m2-specific cache keys (h-m2 compat function)."""
    import os
    missing = []
    model_slug_map = {
        "all-MiniLM-L6-v2": "minilm",
        "paraphrase-MiniLM-L6-v2": "paraphrase",
        "all-mpnet-base-v2": "mpnet",
    }
    tier_slug_map = {
        "helpful-base": "base",
        "helpful-rejection-sampled": "rejection_sampled",
        "helpful-online": "online",
    }
    templates = [
        "{model}_A_next_{tier}.npy",
        "{model}_H_curr_{tier}.npy",
    ]
    embeddings_dir = cache_config.embeddings_dir
    for template in templates:
        for model in cache_config.models:
            model_slug = model_slug_map.get(model, model)
            for tier in cache_config.tiers:
                tier_slug = tier_slug_map.get(tier, tier.replace("-", "_"))
                key = template.format(model=model_slug, tier=tier_slug)
                path = os.path.join(embeddings_dir, key)
                if not os.path.exists(path):
                    missing.append(key)
    return missing


def load_config(yaml_path: Optional[str] = None) -> ExperimentConfig:
    """Load ExperimentConfig from YAML with defaults.

    Args:
        yaml_path: Path to config YAML. If None, returns default config.

    Returns:
        ExperimentConfig with values merged from YAML.
    """
    config = ExperimentConfig()

    if yaml_path is None:
        return config

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return config

    for key in ("hypothesis_id", "output_dir", "results_dir", "dry_run",
                "n_samples_dry_run", "ipw_ks_threshold", "singularity_warn"):
        if key in data:
            setattr(config, key, data[key])

    for sub, obj in [("cache", config.cache), ("stats", config.stats),
                     ("regression", config.regression), ("figures", config.figures)]:
        if sub in data:
            for k, v in data[sub].items():
                if hasattr(obj, k):
                    setattr(obj, k, v)

    return config
