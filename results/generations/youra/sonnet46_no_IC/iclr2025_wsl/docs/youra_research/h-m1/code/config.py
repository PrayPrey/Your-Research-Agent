"""H-M1 configuration: EquiSSL-perm ablation vs EquiSSL vs SANE on ViT linear probe."""
import os
from dataclasses import dataclass, field
from typing import List

# ── Shared with H-E1 (do not change — controlled ablation) ─────────────────
HIDDEN_DIM   = 256
LATENT_DIM   = 128
NUM_LAYERS   = 4
LR           = 1e-3
WEIGHT_DECAY = 1e-4
BETAS        = (0.9, 0.999)
BATCH_SIZE   = 64
EPOCHS       = 100
T_MAX        = 100
ETA_MIN      = 1e-5
TEMPERATURE  = 0.07
LAMBDA_REC   = 0.1   # Best from H-E1
VAL_FRACTION = 0.1

# ── H-M1 specific ────────────────────────────────────────────────────────────
SEEDS        = [0, 1, 2]   # 3 seeds (matching H-E1 available checkpoints)

# Paths
PROJECT_ROOT   = os.environ.get('PROJECT_ROOT',
                    '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')
H_E1_CODE      = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-e1/code')
H_E1_CKPT_DIR = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-e1/checkpoints')
H_M1_ROOT      = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1')
CHECKPOINT_DIR = os.path.join(H_M1_ROOT, 'checkpoints')
RESULTS_DIR    = os.path.join(H_M1_ROOT, 'code/results')
FIGURES_DIR    = os.path.join(H_M1_ROOT, 'figures')
OUTPUTS_DIR    = os.path.join(H_M1_ROOT, 'code/outputs')

# ViT zoo data
VIT_ZOO_ROOT = os.path.join(PROJECT_ROOT,
    'data/vit_zoo/vit-modelzoo/vit_imagenet_pretrained')

# MultiZoo data (shared from H-E1 environment)
MULTIZOO_ROOT = os.environ.get('MULTIZOO_ROOT',
    os.path.join(PROJECT_ROOT, 'data/multizoo'))

# Linear probe config
RIDGE_ALPHAS   = [0.1, 1.0, 10.0, 100.0]
PROBE_TEST_FRAC = 0.2   # 80/20 split

@dataclass
class EquiSSLPermConfig:
    symmetry: str = "permutation"
    node_dim: int = 64
    edge_dim: int = 64
    hidden_dim: int = HIDDEN_DIM
    latent_dim: int = LATENT_DIM
    num_layers: int = NUM_LAYERS
    lr: float = LR
    weight_decay: float = WEIGHT_DECAY
    batch_size: int = BATCH_SIZE
    epochs: int = EPOCHS
    temperature: float = TEMPERATURE
    lambda_rec: float = LAMBDA_REC
    seeds: List[int] = field(default_factory=lambda: list(SEEDS))
