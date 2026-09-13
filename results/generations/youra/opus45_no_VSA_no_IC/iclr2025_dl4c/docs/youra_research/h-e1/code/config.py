"""Fixed configuration for H-E1 experiment."""

MODELS = {
    "7B": "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
    "70B": "codellama/CodeLlama-70b-Instruct-hf",
    "proprietary": "gpt-4o",
}

TEMPERATURE = 0
MAX_TOKENS = 512
SEED = 1
P_VALUE_THRESHOLD = 0.05
MIN_SAMPLE_SIZE = 500

PROMPT_TEMPLATE = """You are a code correctness judge. Given a programming problem and a candidate solution, determine if the solution is CORRECT or INCORRECT.

Problem:
{problem}

Candidate Solution:
```python
{solution}
```

Analyze the solution and respond with exactly one word: CORRECT or INCORRECT."""

DATASET_NAME = "evalplus/humanevalplus"
NUM_PROBLEMS = 164
SOLUTIONS_PER_PROBLEM = 5

DOCKER_IMAGE = "python:3.10-slim"
EXECUTION_TIMEOUT = 30

OUTPUT_DIR = "outputs"
