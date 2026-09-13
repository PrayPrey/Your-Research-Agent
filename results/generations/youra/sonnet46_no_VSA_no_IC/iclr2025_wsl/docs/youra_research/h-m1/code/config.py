import os

MZDATASET_CODE_PATH = "/home/PrayPrey/YOURA_camera_ready/YouRA/results/generations/youra/opus45_no_IC/iclr2025_wsl/docs/youra_research/h-m4/data/ModelZooDataset/code"
ZOO_PT_PATH = "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt"
DWSNETS_PATH = "/tmp/DWSNets"

H_E1_CODE_DIR = os.path.join(os.path.dirname(__file__), "../../h-e1/code")
H_E1_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "../../h-e1/results")
GNN_CKPT = os.path.join(H_E1_RESULTS_DIR, "gnn_nfn_best.pt")
FLAT_CKPT = os.path.join(H_E1_RESULTS_DIR, "flat_mlp_best.pt")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_M1_DIR = os.path.dirname(_THIS_DIR)
FIGURES_DIR = os.path.join(_H_M1_DIR, "figures")
RESULTS_DIR = os.path.join(_H_M1_DIR, "results")

SEED = 42
N_MODELS = 200
N_PERMS = 50
TOL_EQUIV = 1e-5
TOL_NON_EQUIV = 1e-3

GNN_HIDDEN_DIM = 64
GNN_NUM_LAYERS = 4
