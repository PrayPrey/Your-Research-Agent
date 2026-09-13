import os

# Experiment
SEEDS = [0, 1, 2, 3, 4]
PARADIGMS = ['erm', 'moco', 'dino', 'barlowtwins']
BATCH_SIZE = 256

# Paths — resolve relative to this file's location so script runs from any cwd
_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_CODE_DIR, '..', '..', '..', '..'))

DATA_ROOT = os.path.expanduser('~/.wilds_cache')
RESULTS_DIR = os.path.join(_CODE_DIR, '..', 'results')
FIGURES_DIR = os.path.join(_CODE_DIR, '..', 'figures')
LOG_DIR = os.path.join(_CODE_DIR, '..', 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'h-e1_run.log')

# Cache for extracted features (seed-independent)
CACHE_DIR = '/tmp/h-e1-cache'

# Probe (LogisticRegression)
PROBE_C = 1.0
PROBE_MAX_ITER = 1000
PROBE_SOLVER = 'lbfgs'
FEATURE_DIM = 2048

# Statistics
BONFERRONI_N = 6
GATE_ALPHA = 0.05
GATE_MIN_DIFF = 0.02

# Dataset
DATASET_NAME = 'waterbirds'
DATASET_DOWNLOAD = False

# Transform
RESIZE = 256
CROP = 224
IMG_MEAN = [0.485, 0.456, 0.406]
IMG_STD = [0.229, 0.224, 0.225]

# Hub model identifiers
HUB_MOCO = ('facebookresearch/moco-v3:main', 'resnet50')
HUB_DINO = ('facebookresearch/dino:main', 'dino_resnet50')
HUB_BARLOWTWINS = ('facebookresearch/barlowtwins:main', 'resnet50')

# Logging
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG_LEVEL = 'INFO'
