"""
Configuration file for Neural-Symbolic Repair experiments
"""
import os

# Model Configuration
LLM_MODEL = "gpt-4o-mini"  # Using OpenAI's GPT-4o-mini for code generation
FEEDBACK_MODEL = "gpt-4o-mini"  # Using same model for feedback synthesis
MAX_ITERATIONS = 5
TEMPERATURE = 0.0  # Zero temperature for deterministic generation

# Experiment Configuration
NUM_PROBLEMS = 10  # Number of problems to test (reduced for feasibility)
RANDOM_SEED = 42

# API Keys (from environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")

# Verification Tools Configuration
ENABLE_STATIC_ANALYSIS = True
ENABLE_UNIT_TESTS = True
TIMEOUT_SECONDS = 30

# Paths
RESULTS_DIR = "results"
LOGS_DIR = "logs"

# Evaluation Metrics
METRICS = [
    "repair_success_rate",
    "average_repair_iterations",
    "test_pass_rate",
    "convergence_rate"
]

# Baseline Methods
BASELINES = [
    "no_feedback",  # LLM without verification feedback
    "raw_feedback",  # Direct verification output to LLM
    "veril_static",  # VeriL with static analysis only
    "veril_dynamic"  # VeriL with full feedback synthesis (our method)
]
