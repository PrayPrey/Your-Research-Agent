"""H-M3 configuration: latent interpolation via EquiSSL-perm + graph decoder."""
import os
import torch
from dataclasses import dataclass, field
from typing import List

PROJECT_ROOT = os.environ.get(
    'PROJECT_ROOT', '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl'
)
H_M1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/code')
H_E1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-e1/code')
H_M3_ROOT = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m3')
H_M3_CODE = os.path.join(H_M3_ROOT, 'code')

HIDDEN_DIM = 256
LATENT_DIM = 128
NUM_LAYERS = 4
MAX_EDGE_DIM = 512

# Checkpoint paths
ENCODER_CKPT = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/checkpoints/equi_perm_seed0.pt')
# Decoder lives inside h-m1 checkpoint (key: decoder_state_dict)
DECODER_CKPT = ENCODER_CKPT

# Data paths
DATA_DIR = os.path.join(H_M3_ROOT, 'data')
RESULTS_DIR = os.path.join(H_M3_ROOT, 'results')
FIGURES_DIR = os.path.join(H_M3_ROOT, 'figures')
# Real zoo: SANE ModelZoo CIFAR-10 CNN checkpoints (Schürholt et al. 2022, zenodo:13144018)
REAL_ZOO_DIR = os.path.join(H_M3_ROOT, 'data', 'real_zoo')
ZOO_DIR = os.path.join(H_M3_ROOT, 'data', 'synthetic_zoo')  # legacy MLP zoo (unused in main)
PAIRS_JSON = os.path.join(DATA_DIR, 'real_cnn_pairs.json')

MIN_PAIRS = 500
PAIR_SEED = 42
TASKS = ['cifar10']

TASK_MLP_CONFIGS = {
    'mnist':   {'in_dim': 784,  'hidden_dims': [256, 256], 'out_dim': 10},
    'svhn':    {'in_dim': 3072, 'hidden_dims': [256, 256], 'out_dim': 10},
    'cifar10': {'in_dim': 3072, 'hidden_dims': [256, 256], 'out_dim': 10},
}

N_MODELS_PER_TASK = 50  # 50*3=150 models, C(50,2)*3=3675 pairs >> 500


@dataclass
class MLPArchConfig:
    in_dim: int
    hidden_dims: List[int]
    out_dim: int


@dataclass
class PairConfig:
    min_pairs: int = 500
    seed: int = 42
    tasks: List[str] = field(default_factory=lambda: ['mnist', 'svhn', 'cifar10'])
    pair_json_path: str = PAIRS_JSON

    def validate(self):
        assert self.min_pairs >= 1, "min_pairs must be >= 1"
        assert all(t in {'mnist', 'svhn', 'cifar10'} for t in self.tasks)


@dataclass
class TaskConfig:
    batch_size: int = 256
    data_root: str = os.path.join(PROJECT_ROOT, 'data')
    mlp_arch: dict = field(default_factory=lambda: {
        'mnist':   MLPArchConfig(in_dim=784,  hidden_dims=[256, 256], out_dim=10),
        'svhn':    MLPArchConfig(in_dim=3072, hidden_dims=[256, 256], out_dim=10),
        'cifar10': MLPArchConfig(in_dim=3072, hidden_dims=[256, 256], out_dim=10),
    })


@dataclass
class EvalConfig:
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size: int = 256
    data_root: str = os.path.join(PROJECT_ROOT, 'data')


@dataclass
class HM3Config:
    encoder_ckpt: str = ENCODER_CKPT
    decoder_ckpt: str = DECODER_CKPT
    hidden_dim: int = HIDDEN_DIM
    latent_dim: int = LATENT_DIM
    num_layers: int = NUM_LAYERS
    results_dir: str = RESULTS_DIR
    figures_dir: str = FIGURES_DIR
    data_dir: str = DATA_DIR
    pair: PairConfig = field(default_factory=PairConfig)
    task: TaskConfig = field(default_factory=TaskConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)

    def validate(self):
        assert os.path.exists(self.encoder_ckpt), f"Encoder checkpoint not found: {self.encoder_ckpt}"
        self.pair.validate()
