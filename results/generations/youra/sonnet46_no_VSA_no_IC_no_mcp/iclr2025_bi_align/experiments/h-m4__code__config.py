from pathlib import Path

BASE = Path("docs/youra_research/h-m4")
DATA_DIR = BASE / "data"
RESULTS_DIR = BASE / "results"
FIGURES_DIR = BASE / "figures"

DATA_RAW = DATA_DIR / "gao_2023_raw.csv"
DATA_GAP = DATA_DIR / "gao_2023_gap.csv"
RESULTS_JSON = RESULTS_DIR / "h_m4_results.json"
RESULTS_CSV = RESULTS_DIR / "gao_2023_gap_final.csv"

BETA_COSTE = 0.1433
R2_COSTE = 0.9577
P_COSTE = 8.89e-7
N_COSTE = 10

N_BOOT = 10_000
SEED = 42

GATE_BETA_MIN = 0.0
GATE_P_MAX = 0.05
MIN_N = 6
