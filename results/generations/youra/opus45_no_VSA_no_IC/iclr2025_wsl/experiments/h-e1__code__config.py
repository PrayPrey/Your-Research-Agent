"""Config: fixed constants for H-E1 Statistics Baseline experiment."""

N_VALUES = [100, 250, 500, 1000, 2500, 5000]
N_SEEDS = 10
TEST_SIZE = 500
ALPHAS = [0.01, 0.1, 1, 10, 100]
CV_FOLDS = 5

ZOO_URL = "https://zenodo.org/records/6974029/files/cifar10_resnet18_train.zip"
ZOO_DIR = "data/model_zoo"
FEATURES_PATH = "outputs/statistics_features.npz"
RESULTS_PATH = "outputs/statistics_baseline_results.csv"
PLOT_PATH = "outputs/r2_vs_n.png"

SPLIT_SEED = 42
