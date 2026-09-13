import os

SEEDS = [0, 1, 2, 3, 4]
PARADIGMS = ['erm', 'moco', 'dino', 'barlowtwins']
PRIMARY_PARADIGMS = ['erm', 'moco']
BATCH_SIZE = 256
CELEBA_MIN_GROUP_SIZE = 500

CELEBA_ROOT = os.path.expanduser('~/.wilds/celebA_v1.0')

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
_H_D1_DIR = os.path.dirname(_CODE_DIR)
_RESEARCH_DIR = os.path.dirname(_H_D1_DIR)

RESULTS_DIR = _H_D1_DIR
FIGURES_DIR = os.path.join(_H_D1_DIR, 'figures')
WB_RATIOS_CSV = os.path.join(_RESEARCH_DIR, 'h-e1', 'results', 'h-e1_ratios.csv')

CELEBA_FEATURES_PATH = {
    'erm': os.path.join(RESULTS_DIR, 'celeba_features_erm.pt'),
    'moco': os.path.join(RESULTS_DIR, 'celeba_features_moco.pt'),
}
CELEBA_PROBE_RESULTS_PATH = os.path.join(RESULTS_DIR, 'celeba_probe_results.json')
H_D1_RESULTS_PATH = os.path.join(RESULTS_DIR, 'h_d1_results.json')

PROBE_C = 1.0
PROBE_MAX_ITER = 1000
FEATURE_DIM = 2048

ALPHA_DIRECTIONAL = 0.05
ALPHA_NULL = 0.1
BOOTSTRAP_N = 1000
