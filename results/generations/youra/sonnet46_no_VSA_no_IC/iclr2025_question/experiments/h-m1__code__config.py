import os
import sys

_THIS_DIR       = os.path.dirname(os.path.abspath(__file__))
_H_M1_ROOT      = os.path.dirname(_THIS_DIR)           # h-m1/
_YOURA_RESEARCH = os.path.dirname(_H_M1_ROOT)          # youra_research/

H_E1_CODE_DIR    = os.path.join(_YOURA_RESEARCH, "h-e1", "code")
H_E1_RESULTS_DIR = os.path.join(_YOURA_RESEARCH, "h-e1", "results")

RESULTS_DIR = os.path.join(_H_M1_ROOT, "results")
FIGURES_DIR = os.path.join(_H_M1_ROOT, "figures")

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("h_e1_config", os.path.join(H_E1_CODE_DIR, "config.py"))
_h_e1_cfg = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_h_e1_cfg)
MODELS = _h_e1_cfg.MODELS
SEED = _h_e1_cfg.SEED
MAX_NEW_TOKENS = _h_e1_cfg.MAX_NEW_TOKENS

DATASETS = ["trivia_qa", "nq"]
MODELS_TO_RUN = ["llama2"]

MAX_SAMPLES = {
    "trivia_qa": 2000,
    "nq": 2000,
}

P_VALUE_THRESHOLD = 0.05
