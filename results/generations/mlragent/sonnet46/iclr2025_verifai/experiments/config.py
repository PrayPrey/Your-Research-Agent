"""Configuration for ExecGuide experiments."""

# Model configuration
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MAX_NEW_TOKENS = 200
TEMPERATURE = 0.7
NUM_BEAMS = 3
BATCH_SIZE = 1

# ExecGuide parameters
LAMBDA_STEERING = 0.5  # Verifiability potential weight
EXEC_TIMEOUT = 2.0    # Seconds per test case
NUM_PROBLEMS = 20     # Number of HumanEval problems to evaluate

# Reward model
REWARD_SMT_WEIGHT = 0.4
REWARD_EXEC_WEIGHT = 0.6

# Paths
BASE_DIR = "/home/anonymous/mlbench/mlrbench/tasks_youra_result_sonnet46/iclr2025_verifai"
RESULTS_DIR = f"{BASE_DIR}/results"
CODE_DIR = f"{BASE_DIR}/claude_code"
LOG_FILE = f"{CODE_DIR}/log.txt"

# Experiment settings
SEED = 42
DEVICE = "cuda"
