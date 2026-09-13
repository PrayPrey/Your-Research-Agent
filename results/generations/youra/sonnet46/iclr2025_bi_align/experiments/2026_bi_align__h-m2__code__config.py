"""
config.py - Configuration dataclasses for h-m2 bidirectional C_sem experiment.

Provides ExperimentConfig, CacheConfig, StatisticsConfig, FigureConfig
with load_config(yaml_path) function.
"""
import os
import yaml
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CacheConfig:
    """Cache configuration for datasets and embeddings."""
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m1/code/embeddings"  # Reuse h-m1 cache
    models: List[str] = field(default_factory=lambda: [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
        "all-mpnet-base-v2",
    ])
    tiers: List[str] = field(default_factory=lambda: [
        "helpful-base",
        "helpful-rejection-sampled",
        "helpful-online",
    ])
    encode_batch_size: int = 256  # Verified from h-m1 embedder.py
    # h-m1 keys (already cached)
    h_m1_cache_key_templates: List[str] = field(default_factory=lambda: [
        "{model}_H_next_{tier}.npy",
        "{model}_A_curr_{tier}.npy",
    ])
    # h-m2 new keys (may need encoding)
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
    knn_n_jobs: int = 1  # CRITICAL: never -1 at 155k scale
    tiers_required: int = 2   # >= 2/3 tiers must pass for model gate
    models_required: int = 2  # >= 2/3 models must pass for overall gate
    min_n_pairs: int = 1000
    cohen_d_threshold: float = 0.1


@dataclass
class FigureConfig:
    """Figure output configuration."""
    figures_dir: str = "../figures"
    dpi: int = 150
    save_format: str = "png"


@dataclass
class ExperimentConfig:
    """Top-level experiment configuration for h-m2."""
    hypothesis_id: str = "h-m2"
    cache: CacheConfig = field(default_factory=CacheConfig)
    stats: StatisticsConfig = field(default_factory=StatisticsConfig)
    figures: FigureConfig = field(default_factory=FigureConfig)
    output_dir: str = "outputs"
    embedding_cache_dir: str = "../h-m1/code/embeddings"
    dry_run: bool = False
    n_samples_dry_run: int = 500

    @property
    def cache_dir(self) -> str:
        return self.cache.cache_dir

    @property
    def figures_dir(self) -> str:
        return self.figures.figures_dir


def load_config(yaml_path: Optional[str] = None) -> ExperimentConfig:
    """Load ExperimentConfig from YAML file with defaults.

    Args:
        yaml_path: Path to config.yaml. If None, returns default config.

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

    # Apply top-level fields
    for key in ("hypothesis_id", "output_dir", "embedding_cache_dir", "dry_run", "n_samples_dry_run"):
        if key in data:
            setattr(config, key, data[key])

    # Apply cache sub-config
    if "cache" in data:
        for k, v in data["cache"].items():
            if hasattr(config.cache, k):
                setattr(config.cache, k, v)

    # Apply stats sub-config
    if "stats" in data:
        for k, v in data["stats"].items():
            if hasattr(config.stats, k):
                setattr(config.stats, k, v)

    # Apply figures sub-config
    if "figures" in data:
        for k, v in data["figures"].items():
            if hasattr(config.figures, k):
                setattr(config.figures, k, v)

    return config


def verify_cache(cache_config: CacheConfig):
    """Verify all 36 required .npy cache files exist.

    Args:
        cache_config: CacheConfig instance.

    Returns:
        Tuple of (all_present: bool, status: {key: exists_bool})
    """
    status = {}
    templates = cache_config.h_m1_cache_key_templates + cache_config.h_m2_cache_key_templates
    embeddings_dir = cache_config.embeddings_dir

    for template in templates:
        for model in cache_config.models:
            model_slug = (
                model.replace("all-MiniLM-L6-v2", "minilm")
                     .replace("paraphrase-MiniLM-L6-v2", "paraphrase")
                     .replace("all-mpnet-base-v2", "mpnet")
            )
            for tier in cache_config.tiers:
                tier_slug = (
                    tier.replace("helpful-", "")
                        .replace("-", "_")
                )
                key = template.format(model=model_slug, tier=tier_slug)
                path = os.path.join(embeddings_dir, key)
                status[key] = os.path.exists(path)

    all_present = all(status.values())
    return all_present, status


def get_missing_h_m2_keys(cache_config: CacheConfig):
    """Return list of missing h-m2-specific cache keys.

    Args:
        cache_config: CacheConfig instance.

    Returns:
        List of missing key strings (A_next, H_curr templates only).
    """
    missing = []
    embeddings_dir = cache_config.embeddings_dir

    for template in cache_config.h_m2_cache_key_templates:
        for model in cache_config.models:
            model_slug = (
                model.replace("all-MiniLM-L6-v2", "minilm")
                     .replace("paraphrase-MiniLM-L6-v2", "paraphrase")
                     .replace("all-mpnet-base-v2", "mpnet")
            )
            for tier in cache_config.tiers:
                tier_slug = (
                    tier.replace("helpful-", "")
                        .replace("-", "_")
                )
                key = template.format(model=model_slug, tier=tier_slug)
                path = os.path.join(embeddings_dir, key)
                if not os.path.exists(path):
                    missing.append(key)

    return missing
