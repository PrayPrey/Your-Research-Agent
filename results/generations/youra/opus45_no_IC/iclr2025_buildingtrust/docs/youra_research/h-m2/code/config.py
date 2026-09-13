"""H-M2 Configuration: Per-cluster temperature scaling variation."""

import sys
import importlib.util
from pathlib import Path

# Load h-e1 config without circular import
_he1_config_path = Path(__file__).parent.parent.parent / "h-e1" / "code" / "config.py"
_spec = importlib.util.spec_from_file_location("he1_config", _he1_config_path)
_he1_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_he1_config)

# Re-export h-e1 constants
SEED = _he1_config.SEED
MODEL_ID = _he1_config.MODEL_ID
DTYPE = _he1_config.DTYPE
DEVICE_MAP = _he1_config.DEVICE_MAP
DATASET_ID = _he1_config.DATASET_ID
DATASET_CONFIG = _he1_config.DATASET_CONFIG
DATASET_SPLIT = _he1_config.DATASET_SPLIT
BATCH_SIZE = _he1_config.BATCH_SIZE
CATEGORY_TO_CLUSTER = _he1_config.CATEGORY_TO_CLUSTER
CLUSTER_NAMES = _he1_config.CLUSTER_NAMES
MIN_CLUSTER_SIZE = _he1_config.MIN_CLUSTER_SIZE

N_CLUSTERS = 7
N_FOLDS = 5
T_BOUNDS = (0.1, 10.0)
T_INIT = 1.0
MIN_SAMPLES_PER_FOLD = 80
N_BOOTSTRAP = 1000
CI = 0.95
CV_GATE_THRESHOLD = 0.1
RANGE_GATE_THRESHOLD = 0.3
EPS = 1e-10

RESULTS_JSON = "outputs/results.json"
VALIDATION_MD = "../04_validation.md"
FIGURES_DIR = "figures/"

ABLATION_BOUNDS = [(0.5, 5.0), (0.1, 10.0)]
ABLATION_T_INIT = [0.5, 1.0, 2.0]
