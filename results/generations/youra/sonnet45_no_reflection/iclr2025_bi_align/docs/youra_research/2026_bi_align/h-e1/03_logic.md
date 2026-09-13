---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3 - Logic Design
generated: 2026-05-11
status: COMPLETE
---

# Logic Design: h-e1
## Policy-Layer Capability Decoupling Validation

**Version:** 1.0  
**Date:** 2026-05-11  
**Budget:** 5 subtasks

**Applied**: Standard Python API pattern, Statistical analysis pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 8, Budget: 5]

**Applied**: HuggingFace datasets pattern

### API Signatures

```python
from typing import Dict, List
from datasets import load_dataset
import pandas as pd

class MMLULoader:
    def __init__(self):
        """Initialize MMLU loader."""
        self.dataset = None
        self.subjects = []
    
    def load_dataset(self) -> Dict:
        """Load MMLU dataset. Returns: {split: Dataset}"""
        ...
    
    def get_few_shot_examples(self, subject: str, n: int = 4) -> List[Dict]:
        """Get few-shot examples. Returns: list of dicts with question, choices, answer"""
        ...
    
    def format_question(self, item: Dict) -> str:
        """Format question with choices. Returns: formatted string"""
        ...

class HumanEvalLoader:
    def __init__(self):
        """Initialize HumanEval loader."""
        self.problems = []
    
    def load_dataset(self) -> Dict:
        """Load HumanEval problems. Returns: {task_id: problem_dict}"""
        ...
    
    def format_problem(self, task_id: str) -> str:
        """Format problem with signature and docstring. Returns: formatted string"""
        ...
```

### Pseudo-code

```
MMLULoader.load_dataset():
1. dataset = load_dataset("cais/mmlu", "all")
2. subjects = extract_unique_subjects(dataset["test"])
3. return {"dev": dataset["dev"], "test": dataset["test"]}

MMLULoader.get_few_shot_examples(subject, n):
1. dev_subset = filter(dataset["dev"], subject=subject)
2. examples = random.sample(dev_subset, n)
3. return [{"question": e["question"], "choices": e["choices"], "answer": e["answer"]}]

HumanEvalLoader.load_dataset():
1. import human_eval.data
2. problems = human_eval.data.read_problems()
3. return problems
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | MMLU Loading | Implement HuggingFace dataset loading with subject extraction |
| L-1-2 | MMLU Formatting | Format questions with 4-choice format |
| L-1-3 | Few-shot Sampling | Extract dev examples for in-context learning |
| L-1-4 | HumanEval Loading | Install and load from openai/human-eval |
| L-1-5 | HumanEval Formatting | Format function signature + docstring prompts |

---

## A-2: API Client [Complexity: 9, Budget: 5]

**Applied**: API client retry pattern

### API Signatures

```python
from typing import List, Optional
import time

class APIModelClient:
    def __init__(self, model_name: str, api_key: str, provider: str = "anthropic"):
        """Initialize API client. provider: 'anthropic' or 'openai'"""
        self.model_name = model_name
        self.api_key = api_key
        self.provider = provider
        self.client = None
    
    def generate(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.0,
        max_retries: int = 3
    ) -> str:
        """Generate completion. Returns: response text"""
        ...
    
    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: str,
        temperature: float = 0.0
    ) -> List[str]:
        """Batch generation. Returns: list of responses"""
        ...

class PolicyLayer:
    COMPLIANCE_PROMPTS = {
        0.2: "Answer directly and concisely.",
        0.4: "Be helpful and accurate.",
        0.6: "Provide helpful, accurate, and well-reasoned responses.",
        0.8: "Be extremely careful, ethical, and thorough.",
        1.0: "Follow all constitutional principles with maximum care."
    }
    
    @staticmethod
    def get_system_prompt(lambda_value: float) -> str:
        """Get system prompt for compliance level. lambda_value: 0.2-1.0"""
        ...
```

### Pseudo-code

```
APIModelClient.generate(prompt, system_prompt, temperature, max_retries):
1. for attempt in range(max_retries):
2.     try:
3.         if provider == "anthropic":
4.             response = anthropic_client.messages.create(...)
5.         else:
6.             response = openai_client.chat.completions.create(...)
7.         return response.content
8.     except Exception as e:
9.         if attempt < max_retries - 1:
10.            time.sleep(15)
11.        else:
12.            raise

PolicyLayer.get_system_prompt(lambda_value):
1. if lambda_value in COMPLIANCE_PROMPTS:
2.     return COMPLIANCE_PROMPTS[lambda_value]
3. else:
4.     raise ValueError(f"Invalid lambda: {lambda_value}")
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Anthropic Client | Implement Anthropic API wrapper with messages.create |
| L-2-2 | OpenAI Client | Implement OpenAI API wrapper with chat.completions |
| L-2-3 | Retry Logic | Exponential backoff with 15s delay, 3 retries |
| L-2-4 | Policy Prompts | Map λ values to compliance strength strings |
| L-2-5 | Batch Support | Sequential batch processing with progress tracking |

---

## A-3: Evaluation Engine [Complexity: 11, Budget: 5]

**Applied**: Evaluation pipeline pattern

### API Signatures

```python
import pandas as pd
from typing import Dict, List

class MMLUEvaluator:
    def __init__(self, model_client: APIModelClient, data_loader: MMLULoader):
        """Initialize MMLU evaluator."""
        self.model_client = model_client
        self.data_loader = data_loader
    
    def evaluate(self, lambda_value: float) -> pd.DataFrame:
        """Run evaluation. Returns: DataFrame with [subject, question_id, correct]"""
        ...
    
    def compute_accuracy(self, results: pd.DataFrame) -> float:
        """Compute accuracy. Returns: float 0-1"""
        ...
    
    def _parse_answer(self, response: str) -> str:
        """Extract A/B/C/D from response. Returns: single letter"""
        ...

class HumanEvalEvaluator:
    def __init__(self, model_client: APIModelClient, data_loader: HumanEvalLoader):
        """Initialize HumanEval evaluator."""
        self.model_client = model_client
        self.data_loader = data_loader
    
    def evaluate(self, lambda_value: float) -> pd.DataFrame:
        """Run evaluation. Returns: DataFrame with [task_id, passed]"""
        ...
    
    def execute_tests(self, completions: List[Dict]) -> List[bool]:
        """Execute unit tests. Returns: list of pass/fail"""
        ...
    
    def compute_pass_at_k(self, results: pd.DataFrame, k: int = 1) -> float:
        """Compute pass@k. Returns: float 0-1"""
        ...
```

### Pseudo-code

```
MMLUEvaluator.evaluate(lambda_value):
1. system_prompt = PolicyLayer.get_system_prompt(lambda_value)
2. results = []
3. for subject in data_loader.subjects:
4.     few_shot = data_loader.get_few_shot_examples(subject)
5.     for item in test_data[subject]:
6.         prompt = format_few_shot(few_shot) + format_question(item)
7.         response = model_client.generate(prompt, system_prompt)
8.         predicted = _parse_answer(response)
9.         correct = (predicted == item["answer"])
10.        results.append({"subject": subject, "correct": correct})
11. return pd.DataFrame(results)

HumanEvalEvaluator.evaluate(lambda_value):
1. system_prompt = PolicyLayer.get_system_prompt(lambda_value)
2. results = []
3. for task_id, problem in data_loader.problems.items():
4.     prompt = data_loader.format_problem(task_id)
5.     completion = model_client.generate(prompt, system_prompt)
6.     passed = execute_tests([{"task_id": task_id, "completion": completion}])[0]
7.     results.append({"task_id": task_id, "passed": passed})
8. return pd.DataFrame(results)

HumanEvalEvaluator.execute_tests(completions):
1. from human_eval.execution import check_correctness
2. results = []
3. for comp in completions:
4.     result = check_correctness(comp["task_id"], comp["completion"], timeout=3.0)
5.     results.append(result["passed"])
6. return results
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | MMLU Evaluation Loop | Iterate subjects/questions, call API, parse answers |
| L-3-2 | Answer Parsing | Extract A/B/C/D from model response with regex |
| L-3-3 | HumanEval Loop | Generate completions for all 164 problems |
| L-3-4 | Test Execution | Use human_eval.execution.check_correctness |
| L-3-5 | Metrics Computation | Accuracy for MMLU, pass@1 for HumanEval |

---

## A-4: Statistical Analysis [Complexity: 12, Budget: 5]

**Applied**: Statistical testing pattern (pingouin, scipy)

### API Signatures

```python
import pandas as pd
import numpy as np
from typing import Tuple, Dict
from pingouin import intraclass_corr
from scipy.stats import f_oneway

class GateAnalyzer:
    def __init__(self, results_df: pd.DataFrame):
        """Initialize analyzer. results_df: long format [lambda, item_id, accuracy]"""
        self.results_df = results_df
        self.icc_threshold = 0.95
        self.anova_p_threshold = 0.05
        self.cohens_f_threshold = 0.10
    
    def compute_icc(self) -> Tuple[float, float]:
        """Compute ICC2 (two-way mixed). Returns: (icc_value, confidence_interval_lower)"""
        ...
    
    def compute_anova(self) -> Tuple[float, float, int, int]:
        """Compute one-way ANOVA. Returns: (f_stat, p_value, df1, df2)"""
        ...
    
    def compute_cohens_f(self, f_stat: float, df1: int, df2: int) -> float:
        """Compute Cohen's f from F-statistic. Returns: effect_size"""
        ...
    
    def validate_gate(self) -> Dict:
        """Run all gate checks. Returns: {metric: {value, threshold, passed}, overall_pass}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| results_df | [N_items × N_lambda, 3] | Columns: lambda, item_id, accuracy |
| grouped_data | [N_lambda, N_items] | Pivot for ANOVA input |

### Pseudo-code

```
GateAnalyzer.compute_icc():
1. # Reshape to pingouin format: targets (items), raters (lambda), ratings (accuracy)
2. icc_data = results_df.rename(columns={"item_id": "targets", "lambda": "raters", "accuracy": "ratings"})
3. icc_result = intraclass_corr(data=icc_data, targets="targets", raters="raters", ratings="ratings")
4. icc2_row = icc_result[icc_result["Type"] == "ICC2"]
5. return (icc2_row["ICC"].values[0], icc2_row["CI95%"][0][0])

GateAnalyzer.compute_anova():
1. # Group by lambda condition
2. groups = [results_df[results_df["lambda"] == lam]["accuracy"].values for lam in [0.2, 0.4, 0.6, 0.8, 1.0]]
3. f_stat, p_value = f_oneway(*groups)
4. df1 = len(groups) - 1  # 4
5. df2 = len(results_df) - len(groups)
6. return (f_stat, p_value, df1, df2)

GateAnalyzer.compute_cohens_f(f_stat, df1, df2):
1. eta_squared = (df1 * f_stat) / (df1 * f_stat + df2)
2. cohens_f = sqrt(eta_squared / (1 - eta_squared))
3. return cohens_f

GateAnalyzer.validate_gate():
1. icc, _ = compute_icc()
2. f_stat, p_value, df1, df2 = compute_anova()
3. cohens_f = compute_cohens_f(f_stat, df1, df2)
4. return {
5.     "icc": {"value": icc, "threshold": 0.95, "passed": icc > 0.95},
6.     "anova_p": {"value": p_value, "threshold": 0.05, "passed": p_value > 0.05},
7.     "cohens_f": {"value": cohens_f, "threshold": 0.10, "passed": cohens_f < 0.10},
8.     "overall_pass": (icc > 0.95) and (p_value > 0.05) and (cohens_f < 0.10)
9. }
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | ICC Computation | Use pingouin.intraclass_corr with ICC2 type |
| L-4-2 | ANOVA Test | Group by lambda, run scipy.stats.f_oneway |
| L-4-3 | Effect Size | Compute Cohen's f from eta-squared formula |
| L-4-4 | Gate Logic | Check all three conditions, return pass/fail |
| L-4-5 | Data Formatting | Reshape wide/long formats for different libraries |

---

## A-5: Visualization [Complexity: 10, Budget: 5]

**Applied**: Matplotlib/seaborn plotting pattern

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict
import os

class ResultsVisualizer:
    def __init__(self, output_dir: str):
        """Initialize visualizer with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_gate_metrics(self, metrics: Dict, save_path: str) -> None:
        """Plot gate metrics comparison. metrics: from GateAnalyzer.validate_gate()"""
        ...
    
    def plot_capability_consistency(self, results_df: pd.DataFrame, save_path: str) -> None:
        """Plot accuracy vs lambda with error bars. results_df: [lambda, accuracy]"""
        ...
    
    def plot_subject_heatmap(self, results_df: pd.DataFrame, save_path: str) -> None:
        """Plot MMLU subject × lambda heatmap. results_df: [subject, lambda, accuracy]"""
        ...
    
    def plot_distributions(self, results_df: pd.DataFrame, save_path: str) -> None:
        """Plot violin plots per lambda. results_df: [lambda, accuracy]"""
        ...
```

### Pseudo-code

```
ResultsVisualizer.plot_gate_metrics(metrics, save_path):
1. fig, axes = plt.subplots(1, 3, figsize=(12, 4))
2. for i, metric in enumerate(["icc", "anova_p", "cohens_f"]):
3.     value = metrics[metric]["value"]
4.     threshold = metrics[metric]["threshold"]
5.     axes[i].bar(["Actual"], [value])
6.     axes[i].axhline(threshold, color='red', linestyle='--', label='Threshold')
7. plt.savefig(save_path, dpi=300)

ResultsVisualizer.plot_capability_consistency(results_df, save_path):
1. grouped = results_df.groupby("lambda")["accuracy"].agg(["mean", "std"])
2. plt.errorbar(grouped.index, grouped["mean"], yerr=grouped["std"], marker='o')
3. plt.xlabel("Compliance Level (λ)")
4. plt.ylabel("Accuracy")
5. plt.savefig(save_path, dpi=300)

ResultsVisualizer.plot_subject_heatmap(results_df, save_path):
1. pivot = results_df.pivot_table(values="accuracy", index="subject", columns="lambda")
2. sns.heatmap(pivot, cmap="YlGnBu", annot=False, cbar_kws={"label": "Accuracy"})
3. plt.savefig(save_path, dpi=300)

ResultsVisualizer.plot_distributions(results_df, save_path):
1. sns.violinplot(data=results_df, x="lambda", y="accuracy")
2. plt.xlabel("Compliance Level (λ)")
3. plt.ylabel("Accuracy")
4. plt.savefig(save_path, dpi=300)
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Gate Metrics Plot | Bar chart with threshold lines for ICC, ANOVA p, Cohen's f |
| L-5-2 | Consistency Line Plot | Accuracy vs lambda with standard deviation error bars |
| L-5-3 | Subject Heatmap | Seaborn heatmap for 57 subjects × 5 lambda conditions |
| L-5-4 | Distribution Violin | Violin plots showing variance within each lambda |
| L-5-5 | Figure Formatting | 300 DPI, axis labels, legends, consistent style |

---

## A-6: Orchestration [Complexity: 9, Budget: 5]

**Applied**: Experiment pipeline pattern

### API Signatures

```python
import os
import json
from typing import Dict, List
import pandas as pd

def setup_environment() -> Dict:
    """Setup API keys and paths. Returns: config dict"""
    ...

def run_experiment(lambda_values: List[float]) -> pd.DataFrame:
    """Run full evaluation. Returns: combined results [dataset, lambda, item_id, accuracy]"""
    ...

def analyze_results(results_df: pd.DataFrame) -> Dict:
    """Run statistical analysis. Returns: gate metrics"""
    ...

def generate_report(metrics: Dict, results_df: pd.DataFrame, output_path: str) -> None:
    """Generate validation report markdown. metrics: from analyze_results()"""
    ...

def save_checkpoint(results_df: pd.DataFrame, lambda_value: float, output_dir: str) -> None:
    """Save intermediate results after each lambda evaluation."""
    ...

def main():
    """Main entry point."""
    ...
```

### Pseudo-code

```
setup_environment():
1. api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
2. if not api_key:
3.     raise ValueError("API key not found")
4. output_dir = "docs/youra_research/20260511_bi_align/h-e1"
5. os.makedirs(f"{output_dir}/results", exist_ok=True)
6. os.makedirs(f"{output_dir}/figures", exist_ok=True)
7. return {"api_key": api_key, "output_dir": output_dir}

run_experiment(lambda_values):
1. config = setup_environment()
2. mmlu_loader = MMLULoader()
3. humaneval_loader = HumanEvalLoader()
4. model_client = APIModelClient("claude-3-opus-20240229", config["api_key"])
5. mmlu_eval = MMLUEvaluator(model_client, mmlu_loader)
6. he_eval = HumanEvalEvaluator(model_client, humaneval_loader)
7. all_results = []
8. for lambda_val in lambda_values:
9.     print(f"Evaluating lambda={lambda_val}")
10.    mmlu_results = mmlu_eval.evaluate(lambda_val)
11.    he_results = he_eval.evaluate(lambda_val)
12.    mmlu_results["dataset"] = "MMLU"
13.    he_results["dataset"] = "HumanEval"
14.    all_results.append(pd.concat([mmlu_results, he_results]))
15.    save_checkpoint(all_results[-1], lambda_val, config["output_dir"])
16. return pd.concat(all_results)

analyze_results(results_df):
1. analyzer = GateAnalyzer(results_df)
2. gate_metrics = analyzer.validate_gate()
3. return gate_metrics

generate_report(metrics, results_df, output_path):
1. report = f"# Validation Report: h-e1\n\n"
2. report += f"## Gate Results\n\n"
3. report += f"- ICC: {metrics['icc']['value']:.4f} (threshold: {metrics['icc']['threshold']})\n"
4. report += f"- ANOVA p-value: {metrics['anova_p']['value']:.4f} (threshold: {metrics['anova_p']['threshold']})\n"
5. report += f"- Cohen's f: {metrics['cohens_f']['value']:.4f} (threshold: {metrics['cohens_f']['threshold']})\n"
6. report += f"\n**Overall Pass:** {metrics['overall_pass']}\n"
7. with open(output_path, 'w') as f:
8.     f.write(report)

main():
1. lambda_values = [0.2, 0.4, 0.6, 0.8, 1.0]
2. results = run_experiment(lambda_values)
3. metrics = analyze_results(results)
4. visualizer = ResultsVisualizer("docs/youra_research/20260511_bi_align/h-e1/figures")
5. visualizer.plot_gate_metrics(metrics, "gate_metrics.png")
6. visualizer.plot_capability_consistency(results, "capability_consistency.png")
7. visualizer.plot_subject_heatmap(results[results["dataset"] == "MMLU"], "subject_heatmap.png")
8. visualizer.plot_distributions(results, "accuracy_distributions.png")
9. generate_report(metrics, results, "docs/youra_research/20260511_bi_align/h-e1/04_validation.md")
10. print(f"Gate Passed: {metrics['overall_pass']}")
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Environment Setup | Load API keys, create output directories, validate config |
| L-6-2 | Experiment Loop | Iterate lambda values, run both evaluations, concatenate results |
| L-6-3 | Progress Checkpointing | Save intermediate CSVs after each lambda completion |
| L-6-4 | Report Generation | Format markdown with gate metrics and pass/fail status |
| L-6-5 | Error Handling | Try-except blocks, retry logic integration, clear error messages |

---

## Summary

**Total Subtasks**: 30/30 (6 tasks × 5 subtasks each)

**Design Principles**:
- Minimal complexity (EXISTENCE PoC)
- API-based evaluation (no model training)
- Hardcoded configs (LIGHT tier)
- Single-file modules
- Sequential execution (no parallelization)

**Key Dependencies**:
- Anthropic/OpenAI APIs for model inference
- HuggingFace datasets for MMLU
- openai/human-eval for HumanEval
- pingouin for ICC computation
- scipy for ANOVA

**Next Phase**: Config Design (03_config.md)

---

**Document Status**: COMPLETE
**Generated**: 2026-05-11
