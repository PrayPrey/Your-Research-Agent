import os

SEEDS = [0, 1, 2, 3, 4]
PARADIGMS = ['erm', 'moco', 'dino', 'barlowtwins']
BATCH_SIZE = 256
N_PER_GROUP = 180

BLOND_ATTR = 9
MALE_ATTR = 20

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_ROOT = os.path.expanduser('~/.wilds/celebA_v1.0')  # WILDS-format CelebA
RESULTS_DIR = os.path.join(_CODE_DIR, '..', 'results')
FIGURES_DIR = os.path.join(_CODE_DIR, '..', 'figures')
LOG_DIR = os.path.join(_CODE_DIR, '..', 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'h-e2_run.log')

CACHE_DIR = '/tmp/h-e2-cache'

PROBE_C = 1.0
PROBE_MAX_ITER = 1000
PROBE_SOLVER = 'lbfgs'
FEATURE_DIM = 2048

BONFERRONI_N = 6
GATE_ALPHA = 0.05
GATE_MIN_DIFF = 0.02

DATASET_NAME = 'celeba'
DATASET_DOWNLOAD = True

RESIZE = 256
CROP = 224
IMG_MEAN = [0.485, 0.456, 0.406]
IMG_STD = [0.229, 0.224, 0.225]

HUB_MOCO = ('facebookresearch/moco-v3:main', 'resnet50')
HUB_DINO = ('facebookresearch/dino:main', 'dino_resnet50')
HUB_BARLOWTWINS = ('facebookresearch/barlowtwins:main', 'resnet50')

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG_LEVEL = 'INFO'
