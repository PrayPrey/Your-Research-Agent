"""H-E1 Configuration: Factuality-Robustness Correlation Study"""

MODEL_IDS = [
    "meta-llama/Llama-2-7b-hf",
    "meta-llama/Llama-2-13b-hf",
    "meta-llama/Llama-2-70b-hf",
    "meta-llama/Meta-Llama-3-8B",
    "meta-llama/Meta-Llama-3-70B",
    "mistralai/Mistral-7B-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "google/flan-t5-base",
    "google/flan-t5-large",
    "google/flan-t5-xl",
    "microsoft/phi-2",
    "microsoft/Phi-3-mini-4k-instruct",
]

MODEL_FAMILY = {
    "meta-llama/Llama-2-7b-hf": "llama2",
    "meta-llama/Llama-2-13b-hf": "llama2",
    "meta-llama/Llama-2-70b-hf": "llama2",
    "meta-llama/Meta-Llama-3-8B": "llama3",
    "meta-llama/Meta-Llama-3-70B": "llama3",
    "mistralai/Mistral-7B-v0.1": "mistral",
    "mistralai/Mistral-7B-Instruct-v0.1": "mistral",
    "google/flan-t5-base": "flan-t5",
    "google/flan-t5-large": "flan-t5",
    "google/flan-t5-xl": "flan-t5",
    "microsoft/phi-2": "phi",
    "microsoft/Phi-3-mini-4k-instruct": "phi",
}

MODEL_PARAMS = {
    "meta-llama/Llama-2-7b-hf": 7.0,
    "meta-llama/Llama-2-13b-hf": 13.0,
    "meta-llama/Llama-2-70b-hf": 70.0,
    "meta-llama/Meta-Llama-3-8B": 8.0,
    "meta-llama/Meta-Llama-3-70B": 70.0,
    "mistralai/Mistral-7B-v0.1": 7.0,
    "mistralai/Mistral-7B-Instruct-v0.1": 7.0,
    "google/flan-t5-base": 0.25,
    "google/flan-t5-large": 0.78,
    "google/flan-t5-xl": 3.0,
    "microsoft/phi-2": 2.7,
    "microsoft/Phi-3-mini-4k-instruct": 3.8,
}

LARGE_MODELS = {"meta-llama/Llama-2-70b-hf", "meta-llama/Meta-Llama-3-70B"}

TRUTHFULQA_TASK = "truthfulqa_mc1"
TRUTHFULQA_SPLIT = "validation"
TRUTHFULQA_NUM_QUESTIONS = 817

SST2_DATASET = "glue"
SST2_SUBSET = "sst2"
SST2_SPLIT = "validation"
TEXTFOOLER_RECIPE = "textfooler"
TEXTFOOLER_NUM_EXAMPLES = 500

BATCH_SIZE = 4
SEED = 42
N_BOOTSTRAP = 1000

R_THRESHOLD = 0.5
P_THRESHOLD = 0.05
BOOTSTRAP_CI_EXCLUDES = 0.3
PARTIAL_R_THRESHOLD = 0.3

RESULTS_PATH = "results/results.json"
ANALYSIS_PATH = "results/analysis.json"
FIGURES_DIR = "figures/"
