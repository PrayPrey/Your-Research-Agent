from dataclasses import dataclass, field
import yaml


@dataclass
class DataConfig:
    data_dir: str = "./data/waterbirds"
    download_url: str = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    splits: tuple = ("train", "val", "test")


@dataclass
class FeatureConfig:
    clip_model: str = "ViT-B/16"
    device: str = "cuda"
    batch_size: int = 100
    feature_dim: int = 512
    cache_path: str = "./data/features_cache.npz"


@dataclass
class CVProbeConfig:
    n_subsets: int = 5
    subset_frac: float = 0.2
    n_epochs: int = 10
    c_range: tuple = (0.001, 100.0)
    solver: str = "lbfgs"
    max_iter: int = 1000


@dataclass
class EvaluateConfig:
    auc_threshold: float = 0.75


@dataclass
class OutputConfig:
    figures_dir: str = "./figures"
    results_path: str = "./results.yaml"


@dataclass
class ExperimentConfig:
    seed: int = 42
    data: DataConfig = field(default_factory=DataConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    cv_probe: CVProbeConfig = field(default_factory=CVProbeConfig)
    evaluate: EvaluateConfig = field(default_factory=EvaluateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "ExperimentConfig":
        with open(path) as f:
            raw = yaml.safe_load(f)
        return cls(
            seed=raw.get("seed", 42),
            data=DataConfig(**raw.get("data", {})),
            features=FeatureConfig(**raw.get("features", {})),
            cv_probe=CVProbeConfig(**raw.get("cv_probe", {})),
            evaluate=EvaluateConfig(**raw.get("evaluate", {})),
            output=OutputConfig(**raw.get("output", {})),
        )
