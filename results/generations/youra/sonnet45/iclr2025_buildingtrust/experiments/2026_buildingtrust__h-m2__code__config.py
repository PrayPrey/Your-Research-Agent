"""config.py — H-M2 constants and paths (A-1, C-9, C-10)."""
import os

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_DIR = os.path.dirname(BASE_DIR)           # h-m2/
HM1_CODE_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "..", "h-m1", "code")
)
HE1_CACHE_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "..", "h-e1", "cache")
)

FIGURES_DIR   = os.path.join(HYPOTHESIS_DIR, "figures")
CACHE_OUT_DIR = os.path.join(HYPOTHESIS_DIR, "cache")
RESULTS_PATH  = os.path.join(HYPOTHESIS_DIR, "experiment_results.json")

# ─── Experiment constants ───────────────────────────────────────────────────────
SEED          = 1
N_QUINTILES   = 5
MIN_QUINTILE_N = 100       # warn if quintile has fewer items
N_BOOTSTRAP   = 5000       # bootstrap iterations for 95% CI

# ─── Gate thresholds ────────────────────────────────────────────────────────────
GATE_THRESHOLDS = {
    "pvalue_max":         0.05,
    "variance_ratio_min": 1.0,
    "benchmarks_min":     2,   # must be significant on >= 2/3 datasets
}

# ─── Model pairs (H-M2 uses only pair2 DPO and pair4 SFT) ──────────────────────
MODEL_PAIRS = [
    {"pair_id": "pair2", "method": "DPO",
     "base": "allenai/tulu-2-7b",
     "aligned": "allenai/tulu-2-dpo-7b"},
    {"pair_id": "pair4", "method": "SFT",
     "base": "EleutherAI/pythia-6.9b",
     "aligned": "dvruette/oasst-pythia-6.9b-4000-steps"},
]

# ─── Datasets ───────────────────────────────────────────────────────────────────
DATASETS = [
    {"name": "mmlu",       "n": 14042},
    {"name": "truthfulqa", "n": 817},
    {"name": "arc",        "n": 1172},
]

# ─── Logging ────────────────────────────────────────────────────────────────────
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "log_file": os.path.join(HYPOTHESIS_DIR, "run.log"),
}

# ─── Visualization ──────────────────────────────────────────────────────────────
VIZ_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "save_formats": ["pdf", "png"],
    "color_palette": "colorblind",
    "n_quintiles": 5,
}

FIG1_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "bar_colors": {"DPO": "steelblue", "SFT": "darkorange"},
    "save_name": "fig1_q1_variance_bar",
}

FIG2_CONFIG = {
    "figsize": (12, 5),
    "dpi": 150,
    "save_name": "fig2_quintile_trend",
}

FIG3_CONFIG = {
    "figsize": (9, 7),
    "dpi": 150,
    "cmap": "viridis",
    "alpha": 0.6,
    "save_name": "fig3_kl_scatter",
}

FIG4_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "capsize": 4,
    "save_name": "fig4_benchmark_q1_grouped",
}

FIG5_CONFIG = {
    "figsize": (10, 5),
    "dpi": 150,
    "cmap": "RdBu_r",
    "save_name": "fig5_variance_ratio_heatmap",
}
