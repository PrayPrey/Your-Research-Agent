DATASET_ID = "openai_humaneval"
NUM_PROBLEMS = 164

MODEL_ID = "gpt-3.5-turbo"
TEMPERATURE = 0.0
MAX_TOKENS = 512

PYLINT_ARGS = ["--output-format=json", "--disable=C,R"]
PYLINT_TIMEOUT_SEC = 30
ACTIONABLE_TYPES = ("error", "warning")

GATE_THRESHOLD = 0.30

OUTPUT_DIR = "results/"
FIGURES_DIR = "figures/"
GENERATIONS_FILE = "results/generations.json"
PYLINT_RESULTS_FILE = "results/pylint_results.json"
METRICS_FILE = "results/metrics.json"
