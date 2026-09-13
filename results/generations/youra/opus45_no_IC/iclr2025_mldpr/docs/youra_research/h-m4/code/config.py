# config.py - H-M4 Configuration

# Data scope
VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)  # 2018-2024 inclusive
SEED = 42

# Paths (relative to h-m4/code/)
PWC_CACHE = "../../h-e1/code/"  # Reuse H-E1's PWC data structures
E1_RESULTS_PATH = "../../h-e1/code/results/hhi_metrics.csv"
OUTPUT_DIR = "../results/"
FIGURES_DIR = "../figures/"

# Statistical thresholds
MIN_PAPERS_PER_VY = 10       # min papers per venue-year to include
MIN_VENUE_YEARS_PER_VENUE = 3  # min venue-years for per-venue Spearman
ALPHA = 0.05                  # significance threshold
MIN_VENUES_WITH_EFFECT = 2    # gate: effect required in >=2/3 venues

# Visualization
FIGSIZE_SCATTER = (8, 6)
FIGSIZE_BAR = (7, 5)
FIGSIZE_BOX = (7, 5)
DPI = 150
VENUE_COLORS = {"NeurIPS": "#1f77b4", "ICML": "#ff7f0e", "ICLR": "#2ca02c"}
