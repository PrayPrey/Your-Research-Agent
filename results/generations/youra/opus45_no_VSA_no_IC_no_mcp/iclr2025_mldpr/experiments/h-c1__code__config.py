"""Configuration for h-c1 domain-stratified correlation analysis."""

CONFIG = {
    "n_bootstrap": 10000,
    "seed": 42,
    "success_r_abs_threshold": 0.3,
    "ci_level": 0.95,
    "figures_dir": "figures",
    "results_dir": "results",
}

DNSI_DATA = {
    "ImageNet": 0.72,
    "CIFAR-10": 0.85,
    "ObjectNet": 0.55,
    "HANS": 0.45,
    "PAWS": 0.60,
    "ANLI": 0.35,
}

GAP_DATA = {
    "ImageNet": 0.125,
    "CIFAR-10": 0.040,
    "ObjectNet": 0.425,
    "HANS": 0.400,
    "PAWS": 0.150,
    "ANLI": 0.300,
}

DOMAIN_MAP = {
    "ImageNet": "vision",
    "CIFAR-10": "vision",
    "ObjectNet": "vision",
    "HANS": "nlp",
    "PAWS": "nlp",
    "ANLI": "nlp",
}
