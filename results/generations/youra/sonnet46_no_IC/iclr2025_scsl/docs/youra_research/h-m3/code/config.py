"""H-M3 experiment constants — background linear decodability test."""
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"
CHECKPOINT_ARCHIVE: str = (
    "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research"
    "/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"
)
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR: str = os.path.join(BASE_DIR, "figures")
RESULTS_JSON: str = os.path.join(BASE_DIR, "results.json")
VALIDATION_REPORT: str = os.path.join(BASE_DIR, "04_validation.md")

# ── Experiment scope ──────────────────────────────────────────────────────────
METHODS: list = ["erm", "groupdro", "sam"]
SEEDS: list = [1, 2, 3]
PRIMARY_METHODS: list = ["erm", "groupdro"]

# ── Data loading ──────────────────────────────────────────────────────────────
BATCH_SIZE: int = 100

# ── ImageNet normalization ────────────────────────────────────────────────────
IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]

# ── Linear probe ─────────────────────────────────────────────────────────────
PROBE_C: float = 1e9
PROBE_SOLVER: str = "lbfgs"
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
PROBE_N_TEST_SAMPLES: int = 5794

# ── Verdict thresholds ────────────────────────────────────────────────────────
VERDICT_CONFIRMED_P: float = 0.05
VERDICT_CONFIRMED_D: float = 0.0
VERDICT_SUGGESTIVE_P: float = 0.10
VERDICT_SUGGESTIVE_D: float = 0.5

# ── WGA values (from H-M1 results) for Fig4 ──────────────────────────────────
WGA_BY_METHOD_SEED: dict = {
    "erm_seed1": 0.72, "erm_seed2": 0.72, "erm_seed3": 0.72,
    "groupdro_seed1": 0.88, "groupdro_seed2": 0.88, "groupdro_seed3": 0.88,
    "sam_seed1": 0.78, "sam_seed2": 0.78, "sam_seed3": 0.78,
}
