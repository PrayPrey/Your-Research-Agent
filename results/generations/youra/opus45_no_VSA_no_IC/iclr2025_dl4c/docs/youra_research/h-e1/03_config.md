# Config: H-E1 (EXISTENCE PoC)

**Format**: Hardcoded dict (single fixed config per PoC rules)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: Hardcoded dict

---

## A-1: Data loading [Complexity: 8, Budget: 2 subtasks]

**Applied**: Standard PyTorch/eval-harness defaults (no matching KB pattern found)

### Configuration

```python
CONFIG = {
    "dataset_name": "evalplus/humanevalplus",
    "num_problems": 164,          # full HumanEval+ set
    "solutions_source": "generate",  # "generate" | "pregenerated"
    "generation_temperature": 0,
    "generation_max_tokens": 512,
    "seed": 1,
}
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Load problems | Fetch HumanEval+ via evalplus.data.get_human_eval_plus() |
| C-1-2 | Get solutions | Generate or load pre-generated solutions per problem |

---

## A-5: Statistical analysis [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard scipy chi-square test defaults (no matching KB pattern found)

### Configuration

```python
CONFIG = {
    "p_value_threshold": 0.05,
    "min_sample_size": 500,
    "contingency_dims": ["scale", "error_type"],  # error_type in {TP,TN,FP,FN}
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | Chi-square gate | Build contingency table, run chi2 test, verify mechanism active (sample size + p-value gate) |

---

## Shared Global Config (Reference)

```python
MODELS = {
    "7B": "deepseek-ai/deepseek-coder-7b-instruct",
    "70B": "codellama/CodeLlama-70b-Instruct-hf",
    "proprietary": "gpt-4",
}
SEED = 1
```
