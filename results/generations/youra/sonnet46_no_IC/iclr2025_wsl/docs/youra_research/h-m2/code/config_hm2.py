"""H-M2 config: Scale vs Permutation Equivariance Ablation."""
import os
import sys
from dataclasses import dataclass, field
from typing import List

PROJECT_ROOT = os.environ.get('PROJECT_ROOT',
    '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')
HM1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/code')
if HM1_CODE not in sys.path:
    sys.path.insert(0, HM1_CODE)


@dataclass
class HM2PathConfig:
    project_root: str = PROJECT_ROOT
    he1_checkpoint_dir: str = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-e1/checkpoints')
    hm1_checkpoint_dir: str = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/checkpoints')
    checkpoint_dir: str = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m2/checkpoints')
    results_dir: str = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m2/results')
    figures_dir: str = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m2/figures')
    vit_zoo_root: str = os.path.join(PROJECT_ROOT, 'data/vit_zoo')
    multizoo_root: str = os.environ.get('MULTIZOO_ROOT',
        os.path.join(PROJECT_ROOT, 'data/multizoo'))


@dataclass
class AblationConfig:
    experiment_id: str = 'h-m2'
    ablation_mode: bool = True
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])  # 3 seeds (h-e1 has 0,1,2)
    gate_threshold: float = 0.05
    gate_type: str = 'SHOULD_WORK'
    sane_r2: float = 0.0721
    seed0_equissl_r2: float = 0.2098
    seed0_equi_perm_r2: float = 0.2305
