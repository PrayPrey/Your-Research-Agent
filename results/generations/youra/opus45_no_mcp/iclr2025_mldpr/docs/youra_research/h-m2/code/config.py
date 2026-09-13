import os

DATA_DIR = "/home/PrayPrey/.cache/torch/datasets/"
DTD_DIR = "data/dtd/images/"
CHECKPOINT_DIR = "checkpoints/"
RESULTS_DIR = "results/"
FIGURES_DIR = "figures/"

BATCH_SIZE = 128
EPOCHS = 30
LR_INIT = 0.1
LR_MIN = 0.001
MOMENTUM = 0.9
WEIGHT_DECAY = 5e-4
SEED = 42
EFFECT_SIZE_THRESHOLD = 0.05

CROP_SIZE = 32
CROP_PADDING = 4


def ensure_dirs():
    for d in [DATA_DIR, DTD_DIR, CHECKPOINT_DIR, RESULTS_DIR, FIGURES_DIR]:
        os.makedirs(d, exist_ok=True)


def check_dtd_present(dtd_dir=DTD_DIR):
    if not os.path.exists(dtd_dir):
        raise FileNotFoundError(f"DTD directory not found: {dtd_dir}")
    subdirs = [d for d in os.listdir(dtd_dir) if os.path.isdir(os.path.join(dtd_dir, d))]
    if len(subdirs) < 5:
        raise FileNotFoundError(f"DTD appears incomplete: only {len(subdirs)} texture categories found (expected 47)")
    return True
