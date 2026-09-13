"""H-M2 experiment constants — proxy verification, no new training."""
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
METHODS: list = ["erm", "groupdro", "sam", "dfr"]
SEEDS: list = [1, 2, 3]

# ── Gradient norm analysis (FR-2) ─────────────────────────────────────────────
N_GRAD_BATCHES: int = 50
GRAD_BATCH_SIZE: int = 32
GRAD_LOSS_TYPES: list = ["erm", "groupdro"]
N_GROUPS: int = 4

# ── Linear probe (FR-3) — consistent with H-P0 proven protocol ───────────────
PROBE_C: float = 1e9
PROBE_SOLVER: str = "lbfgs"
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
PROBE_N_TEST_SAMPLES: int = 5794

# ── Weight difference analysis (FR-1) ────────────────────────────────────────
LAYER4_BLOCKS: list = [0, 1, 2]
WEIGHT_DIFF_EPSILON: float = 1e-6
PAIRED_METHODS: list = [
    ("erm", "groupdro"),
    ("erm", "sam"),
    ("erm", "dfr"),
]

# ── ImageNet normalization ────────────────────────────────────────────────────
IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]
