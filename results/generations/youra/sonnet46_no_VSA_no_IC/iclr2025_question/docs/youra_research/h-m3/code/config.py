import os

_THIS  = os.path.dirname(os.path.abspath(__file__))
_HM3   = os.path.dirname(_THIS)
_YOURA = os.path.dirname(_HM3)

H_E1_RESULTS_DIR = os.path.join(_YOURA, "h-e1", "results")
H_M2_RESULTS_DIR = os.path.join(_YOURA, "h-m2", "results")
RESULTS_DIR      = os.path.join(_HM3, "results")
FIGURES_DIR      = os.path.join(_HM3, "figures")

DATASETS            = ["trivia_qa", "nq", "truthful_qa"]
MODELS_TO_RUN       = ["llama2", "mistral"]
AGGREGATION_METHODS = ["min", "mean", "raw_sum"]

N_RESAMPLES_BOOTSTRAP = 1000
SEED                  = 42
CONFIDENCE_LEVEL      = 0.95
P1_THRESHOLD          = 0.02
P2_THRESHOLD          = 0.02
