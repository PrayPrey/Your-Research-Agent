import os

_THIS  = os.path.dirname(os.path.abspath(__file__))
_HM2   = os.path.dirname(_THIS)
_YOURA = os.path.dirname(_HM2)

H_E1_RESULTS_DIR = os.path.join(_YOURA, "h-e1", "results")
H_M1_RESULTS_DIR = os.path.join(_YOURA, "h-m1", "results")
RESULTS_DIR      = os.path.join(_HM2, "results")
FIGURES_DIR      = os.path.join(_HM2, "figures")
OUTPUTS_DIR      = os.path.join(_HM2, "code", "outputs")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

DATASETS = ["trivia_qa", "nq", "truthful_qa"]
N_SAMPLES = {"trivia_qa": 400, "nq": 400, "truthful_qa": 817}

MODELS = {
    "llama2":  "meta-llama/Llama-2-7b-hf",
    "mistral": "mistralai/Mistral-7B-v0.1",
}
MODELS_TO_RUN = ["llama2", "mistral"]

MAX_NEW_TOKENS = 20
SEED = 42
FEW_SHOT_K = {"trivia_qa": 4, "nq": 4, "truthful_qa": 0}

AGGREGATION_METHODS = ["min", "mean", "raw_sum"]

N_RESAMPLES_BOOTSTRAP = 1000
CONFIDENCE_LEVEL = 0.95
BOOTSTRAP_METHOD = "percentile"

MIN_GENERATED_TOKENS  = 2
DEGENERATE_FRACTION_MAX = 0.05
