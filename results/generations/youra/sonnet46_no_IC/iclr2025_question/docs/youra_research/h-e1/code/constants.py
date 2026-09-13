"""h-e1 config — module-level constants (LIGHT tier, 03_config.md verbatim)."""
import os
from pathlib import Path

SEED = 42

MODEL_IDS = {
    "llama2": "meta-llama/Llama-2-7b-hf",
    "mistral": "mistralai/Mistral-7B-v0.1",
    "llama3": "meta-llama/Meta-Llama-3-8B-Instruct",
}
N_LAYERS = 32
EXPECTED_HIDDEN_STATES = N_LAYERS + 1  # 33 = embedding output + 32 layer outputs

# PRD FR-3.1 "h-e1-identical max_new_tokens": no numeric value in PRD/brief;
# external h-e1 artifact not present in repo. Confirmed default per 03_config.md.
MAX_NEW_TOKENS = 32

DEGENERACY_ENTROPY_PCT = 0.01     # drop layer if entropy within 1% of ln|V|
DEGENERACY_AGREEMENT_MIN = 0.05   # drop layer if <5% top-1 agreement with final layer
AUROC_GATE = 0.55
BASELINE_TOLERANCE = 0.03

H_E1_REFERENCES = {  # (model_key, dataset) -> final-layer entropy AUROC, FR-4.3
    ("llama2", "triviaqa"): 0.5186, ("llama2", "truthfulqa"): 0.5153,
    ("mistral", "triviaqa"): 0.5268, ("mistral", "truthfulqa"): 0.5886,
    ("llama3", "triviaqa"): 0.6583, ("llama3", "truthfulqa"): 0.6161,
}

_H_E1_ROOT = Path(__file__).resolve().parents[1]   # .../h-e1
RESULTS_DIR = str(_H_E1_ROOT / "results")
FIGURES_DIR = str(_H_E1_ROOT / "figures")
SMOKE_N = 10

TRIVIAQA_N = 1000
TRUTHFULQA_N = 817

HF_TOKEN = os.environ.get("HF_TOKEN")
if HF_TOKEN is None:
    raise RuntimeError(
        "HF_TOKEN env var required (gated meta-llama/* repos, FR-2.4). "
        "Set via: export HF_TOKEN=<your_token>"
    )
