# code/config.py
# H-E1: Corpus Curation Generalization Balance — EXISTENCE PoC
# All constants here. No magic numbers elsewhere.

# ── Model IDs & Revisions ──────────────────────────────────────────────────
PYTHIA_ID       = "EleutherAI/pythia-6.9b"
PYTHIA_REVISION = "step143000"
PYTHIA_TOKENS   = 143_000 * 2_097_152   # ~300B

OLMO_ID         = "allenai/OLMo-7B"
OLMO_REVISION   = "step68000-tokens301B"  # ~300B (301B, 0.3% deviation); requires trust_remote_code
OLMO_TOKENS     = 301_000_000_000        # taken directly from branch name step68000-tokens301B

# ── Evaluation Tasks ───────────────────────────────────────────────────────
TASKS        = ["mmlu", "hellaswag", "arc_easy", "arc_challenge"]
FEWSHOT_MAP  = {"mmlu": 5, "hellaswag": 0, "arc_easy": 25, "arc_challenge": 25}

# ── Token Matching ─────────────────────────────────────────────────────────
TARGET_TOKENS   = 300e9
TOKEN_TOLERANCE = 0.10   # ±10%

# ── Statistical Thresholds ─────────────────────────────────────────────────
RATIO_THRESHOLD    = 0.02   # primary: olmo_ratio - pythia_ratio must exceed this
P_THRESHOLD        = 0.05   # one-sided bootstrap p-value
COHENS_D_THRESHOLD = 0.2    # minimum effect size
ARC_DELTA_P_THRESHOLD = 0.10  # secondary criterion

# ── Bootstrap ──────────────────────────────────────────────────────────────
BOOTSTRAP_N = 1000
SEED        = 42

# ── Paths ──────────────────────────────────────────────────────────────────
RESULTS_DIR = "results"
FIGURES_DIR = "docs/youra_research/h-e1/figures"

# ── Figure Styling (E5-C1) ─────────────────────────────────────────────────
# Wong colorblind-safe palette
COLOR_PYTHIA = "#0072B2"   # blue
COLOR_OLMO   = "#E69F00"   # orange

FIG_STYLE = {
    "figsize":   (10, 6),
    "dpi":        300,
    "font_size":  12,
    "title_size": 14,
    "label_size": 11,
    "tick_size":  10,
    "legend_fontsize": 10,
    "savefig_format": "png",
    "savefig_bbox_inches": "tight",
}

# Heatmap gets taller to fit 57 MMLU subjects
HEATMAP_FIGSIZE = (8, 18)

# ── Figure Annotation (E5-C2) ──────────────────────────────────────────────
BOOTSTRAP_VLINE_ZERO = {
    "color":     "#CC79A7",
    "linestyle": "--",
    "linewidth": 1.5,
    "label":     "null (0)",
    "zorder":    3,
}

BOOTSTRAP_VLINE_THRESHOLD = {
    "color":     "#D55E00",
    "linestyle": "-.",
    "linewidth": 1.5,
    "label":     f"threshold ({RATIO_THRESHOLD})",
    "zorder":    3,
}

ERRORBAR_STYLE = {
    "fmt":        "none",
    "ecolor":     "#333333",
    "elinewidth": 1.5,
    "capsize":    5,
    "capthick":   1.5,
    "zorder":     4,
}

# ── Bar kwargs ─────────────────────────────────────────────────────────────
BAR_KWARGS_PYTHIA = {"color": COLOR_PYTHIA, "label": "Pythia-6.9B", "alpha": 0.85}
BAR_KWARGS_OLMO   = {"color": COLOR_OLMO,   "label": "OLMo-7B",     "alpha": 0.85}

SAVEFIG_KWARGS = {
    "dpi":         FIG_STYLE["dpi"],
    "bbox_inches": FIG_STYLE["savefig_bbox_inches"],
    "format":      FIG_STYLE["savefig_format"],
}
