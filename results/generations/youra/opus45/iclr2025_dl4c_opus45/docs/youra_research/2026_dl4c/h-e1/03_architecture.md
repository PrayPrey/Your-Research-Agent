# Architecture: H-E1 - Alignment-Induced Error Type Divergence

**Applied**: minimal-pipeline pattern (EXISTENCE/PoC tier)
**Hypothesis Type**: EXISTENCE | **Gate**: MUST_WORK
**Generated**: 2026-03-24

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis code exists

---

## File Structure

- `code/`
  - `config.py` - single fixed configuration
  - `data_loader.py` - dataset loading (HumanEval+, MBPP+)
  - `generate.py` - code generation for both models
  - `execute.py` - EvalPlus execution and error capture
  - `analyze.py` - error classification + statistical analysis
  - `visualize.py` - figure generation
  - `run_experiment.py` - end-to-end orchestration entry point
- `outputs/` - generated JSONL, JSON, CSV results
- `figures/` - PNG visualizations

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Models
    rl_model_id: str = "Salesforce/codet5-large-ntp-py"
    dpo_model_id: str = "codellama/CodeLlama-7b-Instruct-hf"

    # Generation
    temperature: float = 0.8
    top_p: float = 0.95
    max_new_tokens: int = 512
    n_samples: int = 10
    seed: int = 42

    # Paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    # Thresholds
    chi2_p_threshold: float = 0.05
    cramers_v_threshold: float = 0.05

CONFIG = ExperimentConfig()
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: evalplus, config

```python
from typing import Dict, List

def load_humaneval_plus() -> Dict[str, dict]: ...
    # Returns: {task_id: {prompt, test, entry_point}}

def load_mbpp_plus() -> Dict[str, dict]: ...
    # Returns: {task_id: {prompt, test, entry_point}}

def load_combined_dataset() -> List[dict]: ...
    # Merges HumanEval+ (164) + MBPP+ (378) = 542 problems
    # Returns: [{task_id, prompt, test, entry_point, source}]
```

---

### Generator (`code/generate.py`)

**Dependencies**: transformers, torch, config, data_loader

```python
from typing import List, Dict
from transformers import PreTrainedModel, PreTrainedTokenizer

def load_rl_model(config: ExperimentConfig) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...
    # Loads Salesforce/codet5-large-ntp-py (T5ForConditionalGeneration)

def load_dpo_model(config: ExperimentConfig) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...
    # Loads codellama/CodeLlama-7b-Instruct-hf (AutoModelForCausalLM)

def generate_samples(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    problems: List[dict],
    model_id: str,
    config: ExperimentConfig
) -> List[dict]: ...
    # Returns: [{task_id, model, sample_idx, completion}]
    # 542 problems x 10 samples = 5420 per model

def save_samples(samples: List[dict], path: str) -> None: ...
    # Saves as JSONL to outputs/samples_{model_id}.jsonl
```

---

### Executor (`code/execute.py`)

**Dependencies**: evalplus, config

```python
from typing import List, Dict, Optional

def execute_sample(
    task_id: str,
    completion: str,
    problem: dict
) -> Optional[str]: ...
    # Returns None on PASS, error_trace string on failure
    # Timeout: 5 seconds (EvalPlus default)

def execute_all_samples(
    samples: List[dict],
    problems: Dict[str, dict]
) -> List[dict]: ...
    # Returns: [{task_id, model, sample_idx, completion, error_trace, status}]

def save_execution_results(results: List[dict], path: str) -> None: ...
    # Saves to outputs/execution_results.json
```

---

### Analyzer (`code/analyze.py`)

**Dependencies**: scipy, numpy, config

```python
from typing import Dict, Tuple, List
import numpy as np

ERROR_CATEGORIES = ["syntax", "runtime", "assertion"]

def classify_error(error_trace: Optional[str]) -> str: ...
    # Returns: "pass" | "syntax" | "runtime" | "assertion" | "other"
    # Uses ICSE 2025 taxonomy

def build_contingency_table(
    rl_results: List[dict],
    dpo_results: List[dict]
) -> np.ndarray: ...
    # Returns 2x3 array: [[rl_syntax, rl_runtime, rl_assertion],
    #                      [dpo_syntax, dpo_runtime, dpo_assertion]]

def chi_square_test(contingency: np.ndarray) -> Tuple[float, float, float, int]: ...
    # Returns: (chi2, p_value, cramers_v, dof)

def compute_proportions(results: List[dict]) -> Dict[str, float]: ...
    # Returns P(type | failure) for each error type

def check_effect_direction(
    rl_results: List[dict],
    dpo_results: List[dict]
) -> Tuple[float, float, bool]: ...
    # Returns: (rl_prop, dpo_prop, direction_matches)
    # direction_matches = rl_prop < dpo_prop

def run_analysis(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: ExperimentConfig
) -> Dict: ...
    # Returns full metrics dict saved to outputs/metrics.json
    # Keys: chi2, p_value, cramers_v, dof, direction_matches,
    #       rl_proportions, dpo_proportions, gate_pass
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy, config

```python
from typing import Dict
import numpy as np

def plot_gate_metrics(metrics: Dict, output_path: str) -> None: ...
    # Bar chart: target vs actual p-value and Cramér's V
    # Saves to figures/gate_metrics.png

def plot_error_distribution(metrics: Dict, output_path: str) -> None: ...
    # Grouped bar chart: P(type | failure) for RL vs DPO
    # Saves to figures/error_distribution.png

def plot_contingency_heatmap(contingency: np.ndarray, output_path: str) -> None: ...
    # 2x3 heatmap with count annotations
    # Saves to figures/contingency_heatmap.png

def plot_sample_sizes(rl_results: List[dict], dpo_results: List[dict], output_path: str) -> None: ...
    # Bar chart: failure counts per model
    # Saves to figures/sample_sizes.png

def generate_all_figures(metrics: Dict, contingency: np.ndarray,
                         rl_results: List[dict], dpo_results: List[dict],
                         config: ExperimentConfig) -> None: ...
```

---

### Orchestrator (`code/run_experiment.py`)

**Dependencies**: all modules

```python
def main(config: ExperimentConfig) -> None: ...
    # 1. load_combined_dataset()
    # 2. load_rl_model() + generate_samples() → save_samples()
    # 3. load_dpo_model() + generate_samples() → save_samples()
    # 4. execute_all_samples() for both models
    # 5. run_analysis(rl_results, dpo_results)
    # 6. generate_all_figures()
    # 7. Print gate pass/fail summary

if __name__ == "__main__":
    main(CONFIG)
```

---

## Data Flow

- `data_loader` → problems list
- `generate` → samples JSONL (per model)
- `execute` → execution results with error traces
- `analyze` → contingency table CSV + metrics JSON
- `visualize` → figures PNG

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment & Data Setup | Install evalplus/transformers, load HumanEval+ and MBPP+ (542 problems), verify dataset format | 6 | 2+1+1+2 |
| A-2 | Model Loading & Generation | Load CodeRL-770M (T5) and CodeLlama-7B, generate 10 samples per problem per model (10,840 total), save JSONL | 14 | 3+3+4+4 |
| A-3 | Execution & Error Capture | Run EvalPlus sandbox on all samples, capture error traces, handle timeouts, save execution results | 12 | 3+2+4+3 |
| A-4 | Error Classification & Statistics | Implement ICSE 2025 taxonomy classifier, build 2x3 contingency table, chi-square + Cramér's V, direction check | 10 | 3+2+3+2 |
| A-5 | Visualization & Gate Check | Generate all 4 figures, save metrics JSON, print pass/fail gate summary | 7 | 2+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4], Low(4-8): [A-1, A-5]

---

## External Libraries

| Library | Version | Usage |
|---------|---------|-------|
| `evalplus` | latest | HumanEval+/MBPP+ datasets + execution sandbox |
| `transformers` | >=4.36 | Model loading (T5ForConditionalGeneration, AutoModelForCausalLM) |
| `torch` | >=2.0 | Inference |
| `scipy` | latest | chi2_contingency |
| `numpy` | latest | Array operations |
| `matplotlib` | latest | Figures |
| `seaborn` | latest | Heatmap |

---

## Output Artifacts

| File | Format | Description |
|------|--------|-------------|
| `outputs/samples_rl.jsonl` | JSONL | CodeRL-770M generated samples |
| `outputs/samples_dpo.jsonl` | JSONL | CodeLlama-7B-DPO generated samples |
| `outputs/execution_results.json` | JSON | Per-sample error traces and status |
| `outputs/error_classifications.json` | JSON | Per-sample taxonomy labels |
| `outputs/contingency_table.csv` | CSV | 2x3 RL/DPO x syntax/runtime/assertion |
| `outputs/metrics.json` | JSON | chi2, p_value, cramers_v, gate_pass |
| `figures/gate_metrics.png` | PNG | Target vs actual metrics |
| `figures/error_distribution.png` | PNG | P(type\|failure) by model |
| `figures/contingency_heatmap.png` | PNG | Count heatmap |
| `figures/sample_sizes.png` | PNG | Failure counts sanity check |

---

*Generated by Phase 3 Architecture Agent | Anonymous Research Pipeline*
*Hypothesis: H-E1 | Type: EXISTENCE | Gate: MUST_WORK*
