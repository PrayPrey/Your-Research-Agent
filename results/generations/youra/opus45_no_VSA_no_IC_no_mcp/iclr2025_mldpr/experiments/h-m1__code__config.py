"""Configuration for h-m1 correlation analysis."""

CONFIG = {
    "n_bootstrap": 10000,
    "seed": 42,
    "success_r_threshold": -0.4,
    "fail_r_threshold": -0.2,
    "ci_level": 0.95,
    "figures_dir": "figures",
    "results_dir": "results",
}

GAP_DATA = {
    "ImageNet": 0.125,
    "CIFAR-10": 0.040,
    "ObjectNet": 0.425,
    "HANS": 0.400,
}
