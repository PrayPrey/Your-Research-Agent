# Logic: H-E1 - Alignment-Induced Error Type Divergence

**Applied**: Standard HuggingFace inference pipeline (green-field)
**Hypothesis Type**: EXISTENCE | **Gate**: MUST_WORK
**Generated**: 2026-03-24

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Environment & Data Setup [Complexity: 6, Budget: 2]

**Applied**: Standard evalplus dataset loading

### API Signatures

```python
# data_loader.py
from typing import Dict, List

def load_humaneval_plus() -> Dict[str, dict]:
    """Load 164 HumanEval+ problems. Returns {task_id: {prompt, test, entry_point}}"""
    ...

def load_mbpp_plus() -> Dict[str, dict]:
    """Load 378 MBPP+ problems. Returns {task_id: {prompt, test, entry_point}}"""
    ...

def load_combined_dataset() -> List[dict]:
    """Merge HumanEval+ (164) + MBPP+ (378) = 542 problems.
    Returns: [{task_id, prompt, test, entry_point, source}]
    source: "humaneval" | "mbpp"
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | install_deps | pip install evalplus transformers torch scipy matplotlib seaborn |
| L-1-2 | verify_dataset | Load and assert len(humaneval)==164, len(mbpp)==378 |

---

## A-2: Model Loading & Generation [Complexity: 14, Budget: 3]

**Applied**: T5ForConditionalGeneration for CodeRL; AutoModelForCausalLM for CodeLlama

### API Signatures

```python
# generate.py
from typing import List, Dict, Tuple
from transformers import PreTrainedModel, PreTrainedTokenizer
from config import ExperimentConfig

def load_rl_model(config: ExperimentConfig) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load Salesforce/codet5-large-ntp-py (T5ForConditionalGeneration, 770M).
    Returns: (model, tokenizer) on cuda, eval mode.
    """
    ...

def load_dpo_model(config: ExperimentConfig) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load codellama/CodeLlama-7b-Instruct-hf (AutoModelForCausalLM, 7B).
    Returns: (model, tokenizer) on cuda, eval mode; 8-bit quantization if OOM.
    """
    ...

def generate_samples(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    problems: List[dict],
    model_id: str,       # "rl" | "dpo"
    config: ExperimentConfig,
) -> List[dict]:
    """Generate n_samples completions per problem.
    Returns: [{task_id, model, sample_idx, completion}]
    Total: 542 * 10 = 5420 per model.
    """
    ...

def save_samples(samples: List[dict], path: str) -> None:
    """Save samples as JSONL to outputs/samples_{model_id}.jsonl."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | Tokenized prompt; L varies by problem |
| output_ids (T5) | [1, G] | G <= max_new_tokens=512 |
| output_ids (CausalLM) | [1, L+G] | Full sequence including prompt |

### Pseudo-code

```
for problem in problems:
    prompt = format_prompt(problem, model_id)   # T5 vs causal format differ
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    for i in range(config.n_samples):
        set_seed(config.seed + i)
        with torch.no_grad():
            out = model.generate(**inputs, temperature=0.8, top_p=0.95,
                                 max_new_tokens=512, do_sample=True)
        completion = tokenizer.decode(out[0], skip_special_tokens=True)
        samples.append({task_id, model_id, sample_idx=i, completion})
return samples
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_rl_model | T5ForConditionalGeneration from HF; set eval(), cuda |
| L-2-2 | load_dpo_model | AutoModelForCausalLM; handle 8-bit quantization fallback |
| L-2-3 | generate_and_save | Loop over all 542 problems; generate 10 samples each; save JSONL |

---

## A-3: Execution & Error Capture [Complexity: 12, Budget: 2]

**Applied**: EvalPlus sandbox execution with timeout handling

### API Signatures

```python
# execute.py
from typing import List, Dict, Optional

def execute_sample(
    task_id: str,
    completion: str,
    problem: dict,
) -> Optional[str]:
    """Execute completion against EvalPlus test suite.
    Returns: None on PASS, error_trace str on failure.
    Timeout: 5 seconds.
    """
    ...

def execute_all_samples(
    samples: List[dict],
    problems: Dict[str, dict],
) -> List[dict]:
    """Execute all samples. Adds error_trace and status fields.
    Returns: [{task_id, model, sample_idx, completion, error_trace, status}]
    status: "pass" | "fail"
    """
    ...

def save_execution_results(results: List[dict], path: str) -> None:
    """Save to outputs/execution_results.json."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | execute_with_timeout | Wrap EvalPlus execution with 5s timeout; capture full traceback |
| L-3-2 | batch_execute | Process all 10840 samples; log progress every 100; save JSON |

---

## A-4: Error Classification & Statistics [Complexity: 10, Budget: 2]

**Applied**: ICSE 2025 taxonomy + scipy chi2_contingency

### API Signatures

```python
# analyze.py
from typing import Dict, Tuple, List, Optional
import numpy as np

ERROR_CATEGORIES: List[str] = ["syntax", "runtime", "assertion"]

def classify_error(error_trace: Optional[str]) -> str:
    """Classify error_trace using ICSE 2025 taxonomy.
    Returns: "pass" | "syntax" | "runtime" | "assertion" | "other"
    """
    ...

def build_contingency_table(
    rl_results: List[dict],
    dpo_results: List[dict],
) -> np.ndarray:
    """Build 2x3 contingency table from failed samples only (exclude pass).
    Returns: shape [2, 3]  rows=[rl, dpo], cols=[syntax, runtime, assertion]
    """
    ...

def chi_square_test(contingency: np.ndarray) -> Tuple[float, float, float, int]:
    """Run scipy.stats.chi2_contingency; compute Cramér's V.
    Returns: (chi2, p_value, cramers_v, dof)
    cramers_v = sqrt(chi2 / (n * (min(r, c) - 1)))
    """
    ...

def compute_proportions(results: List[dict]) -> Dict[str, float]:
    """Compute P(type | failure) for each ERROR_CATEGORY.
    Returns: {"syntax": float, "runtime": float, "assertion": float}
    """
    ...

def check_effect_direction(
    rl_results: List[dict],
    dpo_results: List[dict],
) -> Tuple[float, float, bool]:
    """Check if P(syntax+runtime | failure, RL) < P(syntax+runtime | failure, DPO).
    Returns: (rl_prop, dpo_prop, direction_matches)
    direction_matches = rl_prop < dpo_prop
    """
    ...

def run_analysis(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: "ExperimentConfig",
) -> Dict:
    """Full analysis pipeline. Saves outputs/metrics.json.
    Returns: {chi2, p_value, cramers_v, dof, direction_matches,
              rl_proportions, dpo_proportions, gate_pass}
    gate_pass = (p_value < config.chi2_p_threshold) and (cramers_v > config.cramers_v_threshold)
    """
    ...
```

### Pseudo-code (chi_square_test)

```
chi2, p, dof, expected = scipy.stats.chi2_contingency(contingency)
n = contingency.sum()
cramers_v = sqrt(chi2 / (n * (min(contingency.shape) - 1)))  # min(2,3)-1 = 1
return chi2, p, cramers_v, dof
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | classify_errors | Apply taxonomy to all results; save error_classifications.json |
| L-4-2 | stats_and_gate | Build contingency table; chi-square + Cramér's V; direction check; save metrics.json |

---

## A-5: Visualization & Gate Check [Complexity: 7, Budget: 2]

**Applied**: matplotlib/seaborn standard figure patterns

### API Signatures

```python
# visualize.py
from typing import Dict, List
import numpy as np

def plot_gate_metrics(metrics: Dict, output_path: str) -> None:
    """Bar chart: target vs actual p-value and Cramér's V. Saves PNG."""
    ...

def plot_error_distribution(metrics: Dict, output_path: str) -> None:
    """Grouped bar: P(type | failure) for RL vs DPO per error type. Saves PNG."""
    ...

def plot_contingency_heatmap(contingency: np.ndarray, output_path: str) -> None:
    """2x3 seaborn heatmap with count annotations. Saves PNG."""
    ...

def plot_sample_sizes(
    rl_results: List[dict],
    dpo_results: List[dict],
    output_path: str,
) -> None:
    """Bar chart: failure counts per model (sanity check). Saves PNG."""
    ...

def generate_all_figures(
    metrics: Dict,
    contingency: np.ndarray,
    rl_results: List[dict],
    dpo_results: List[dict],
    config: "ExperimentConfig",
) -> None:
    """Generate all 4 figures. Saves to config.figures_dir/."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | generate_figures | Call all 4 plot functions; save PNGs to figures/ |
| L-5-2 | print_gate_summary | Print PASS/FAIL with chi2, p_value, cramers_v, direction_matches |

---

## Orchestrator

```python
# run_experiment.py
from config import ExperimentConfig, CONFIG

def main(config: ExperimentConfig) -> None:
    """End-to-end pipeline.
    1. load_combined_dataset() -> problems
    2. load_rl_model() -> generate_samples() -> save_samples("outputs/samples_rl.jsonl")
    3. load_dpo_model() -> generate_samples() -> save_samples("outputs/samples_dpo.jsonl")
    4. execute_all_samples(rl_samples, problems) -> rl_results
    5. execute_all_samples(dpo_samples, problems) -> dpo_results
    6. run_analysis(rl_results, dpo_results, config) -> metrics
    7. generate_all_figures(metrics, contingency, rl_results, dpo_results, config)
    8. Print gate_pass summary: PASS/FAIL with chi2, p_value, cramers_v
    """
    ...

if __name__ == "__main__":
    main(CONFIG)
```

---

*Generated by Phase 3 Logic Agent | Anonymous Research Pipeline*
*Hypothesis: H-E1 | Type: EXISTENCE | Gate: MUST_WORK*
