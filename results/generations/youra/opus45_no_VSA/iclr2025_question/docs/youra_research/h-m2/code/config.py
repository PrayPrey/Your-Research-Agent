# config.py - h-m2 Low-entropy subset evaluation
import os

CODE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    "seed": 42,
    "h_e1_code_dir": os.path.abspath(os.path.join(CODE_DIR, "../../h-e1/code")),
    "feature_cache": os.path.join(CODE_DIR, "outputs/h_e1_features.npz"),
    "outputs_dir": os.path.join(CODE_DIR, "outputs"),
    "figures_dir": os.path.join(CODE_DIR, "../figures"),
    "entropy_percentile": 25,
    "n_bootstrap": 1000,
    "confidence_level": 0.95,
    "auroc_threshold": 0.55,
    "ci_lb_threshold": 0.50,
}
