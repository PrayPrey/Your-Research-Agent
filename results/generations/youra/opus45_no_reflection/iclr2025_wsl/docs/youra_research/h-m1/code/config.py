import os

SEED = 42
N_CLASSES = 10
TEST_SPLIT = 0.2
RIDGE_ALPHA = 1.0

DATA_PATH = os.path.join(os.path.dirname(__file__), "base", "data", "dataset_cifar_small_hyp_rand.pt")
CIFAR_ROOT = os.path.join(os.path.dirname(__file__), "base", "data")

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")
RESULTS_PATH = os.path.join(OUTPUTS_DIR, "results.json")

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

LAYER_KEYS = [
    "module_list.0.weight",
    "module_list.3.weight",
    "module_list.6.weight",
    "module_list.9.weight",
    "module_list.11.weight",
]
