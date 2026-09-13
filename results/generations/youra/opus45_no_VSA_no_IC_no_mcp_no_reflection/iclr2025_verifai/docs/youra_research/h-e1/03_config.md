# Config: h-e1 (EXISTENCE / PoC)

**Applied**: fixed hardcoded dict for single-run PoC (no hyperparameter search)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design, no existing code
**Config Files Found**: None
**Pattern Used**: hardcoded dict (module-level constants in `config.py`)

---

## Configuration

Single fixed config — no variations, no seeds/tuning needed (deterministic pipeline, temperature=0).

```python
# code/config.py

DATASET_ID = "openai_humaneval"
NUM_PROBLEMS = 164

MODEL_ID = "gpt-3.5-turbo"          # or "codellama/CodeLlama-7b-Instruct-hf"
TEMPERATURE = 0.0                    # NFR-2: deterministic generation
MAX_TOKENS = 512

PYLINT_ARGS = ["--output-format=json", "--disable=C,R"]
PYLINT_TIMEOUT_SEC = 30
ACTIONABLE_TYPES = ("error", "warning")  # pylint msg types counted as actionable

GATE_THRESHOLD = 0.30                # FR-5: warning_rate >= 0.30 to pass

OUTPUT_DIR = "results/"
FIGURES_DIR = "figures/"
GENERATIONS_FILE = "results/generations.json"
PYLINT_RESULTS_FILE = "results/pylint_results.json"
METRICS_FILE = "results/metrics.json"
```

Matches `03_architecture.md` config.py exactly — no changes.

### Subtasks

None (budget: 0). All tasks (A-1..A-7) are Low complexity per architecture; no decomposition applied.
