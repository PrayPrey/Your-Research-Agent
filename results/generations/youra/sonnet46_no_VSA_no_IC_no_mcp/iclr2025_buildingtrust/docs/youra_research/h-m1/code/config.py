"""H-M1 configuration constants."""
import os

# Paths relative to project root — resolved at runtime
_PROJECT_ROOT = os.environ.get(
    "YOURA_PROJECT_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)

H_E1_CODE_PATH: str = os.path.join(_PROJECT_ROOT, "docs/youra_research/h-e1/code")
H_E1_RESULTS_DIR: str = os.path.join(
    _PROJECT_ROOT,
    "docs/youra_research/h-e1/docs/youra_research/h-e1/results"
)
RESULTS_DIR: str = os.path.join(_PROJECT_ROOT, "docs/youra_research/h-m1/results")
FIGURES_DIR: str = os.path.join(_PROJECT_ROOT, "docs/youra_research/h-m1/figures")

SEED: int = 1
N_BINS: int = 15
CLEAN_ECE_H_E1: float = 0.279   # measured in H-E1 on GLUE MNLI N=200
DELTA_ECE_H_E1: float = 0.071   # H-E1 overall NLI delta (AdvGLUE MNLI)
PRESERVE_RATE_GATE: float = 0.80
SUBSAMPLE_CLEAN: int = 2000     # cap for clean MNLI (h-e1 used 200; use all available)

# H-E1 JSONL per-example cache filenames (located in H_E1_RESULTS_DIR)
SPLIT_FILE_MAP: dict = {
    "advglue_mnli": "Llama-2-7b-hf_nli_adversarial_examples.jsonl",
    "anli_r1":      "Llama-2-7b-hf_nli_anli_r1_examples.jsonl",
    "anli_r2":      "Llama-2-7b-hf_nli_anli_r2_examples.jsonl",
    "anli_r3":      "Llama-2-7b-hf_nli_anli_r3_examples.jsonl",
    "mnli":         "Llama-2-7b-hf_nli_clean_examples.jsonl",
}

SPLITS: list = ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3", "mnli"]
