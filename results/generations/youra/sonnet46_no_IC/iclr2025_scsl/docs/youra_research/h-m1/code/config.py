import os

WILDS_CACHE = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET = "waterbirds"
CHECKPOINT_ARCHIVE = "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"

MINORITY_FRACTION_THRESHOLD = 0.10

MINORITY_GROUPS = [1, 2]
MAJORITY_GROUPS = [0, 3]
GROUP_LABELS = {
    0: "Landbird+Land (majority)",
    1: "Landbird+Water (minority)",
    2: "Waterbird+Land (minority)",
    3: "Waterbird+Water (majority)",
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
RESULTS_JSON = os.path.join(BASE_DIR, "results.json")
VALIDATION_REPORT = os.path.join(BASE_DIR, "04_validation.md")
