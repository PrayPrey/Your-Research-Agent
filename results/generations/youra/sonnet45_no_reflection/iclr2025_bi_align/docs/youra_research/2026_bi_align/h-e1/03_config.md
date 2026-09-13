---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3 - Configuration Design
generated: 2026-05-11
status: COMPLETE
---

# Configuration Specification: h-e1
## Policy-Layer Capability Decoupling Validation

**Version:** 1.0  
**Date:** 2026-05-11  
**Infrastructure:** LIGHT (Hardcoded dict - single PoC config)

**Applied:** Standard evaluation pipeline defaults (API-based inference + statistical analysis)

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: Green-field - designing new config schema  
**Config Files Found**: None - new config  
**Pattern Used**: Hardcoded dict (LIGHT tier, EXISTENCE hypothesis)

---

## Global Configuration

**EXISTENCE PoC**: Single fixed config with research defaults. No hyperparameter variations.

```python
# config.py - Hardcoded constants for h-e1 experiment

# API Configuration
CONFIG = {
    # Model Selection
    "api_provider": "anthropic",  # or "openai"
    "model_name": "claude-3-opus-20240229",  # Frozen weights for invariance test
    "temperature": 0.0,  # Deterministic evaluation
    "max_tokens": 512,  # Sufficient for MMLU (50 tokens) + HumanEval (200 tokens)
    
    # Policy-Layer Compliance Levels (λ)
    "lambda_values": [0.2, 0.4, 0.6, 0.8, 1.0],
    
    # Compliance System Prompts
    "compliance_prompts": {
        0.2: "Answer directly and concisely.",
        0.4: "Be helpful and accurate.",
        0.6: "Provide helpful, accurate, and well-reasoned responses.",
        0.8: "Be extremely careful, ethical, and thorough in your responses.",
        1.0: "Follow all constitutional principles, ensuring safety, helpfulness, and harmlessness."
    },
    
    # Dataset Configuration
    "mmlu_dataset": "cais/mmlu",
    "mmlu_split": "test",
    "mmlu_few_shot_n": 4,  # Standard MMLU few-shot setup
    
    "humaneval_repo": "git+https://github.com/openai/human-eval.git",
    "humaneval_timeout": 3.0,  # Seconds per test execution
    
    # Statistical Gate Thresholds
    "gate_thresholds": {
        "icc_min": 0.95,  # Intraclass correlation
        "anova_pvalue_min": 0.05,  # No significant variation
        "cohens_f_max": 0.10  # Negligible effect size
    },
    
    # Output Configuration
    "output_dir": "docs/youra_research/20260511_bi_align/h-e1",
    "results_dir": "docs/youra_research/20260511_bi_align/h-e1/results",
    "figures_dir": "docs/youra_research/20260511_bi_align/h-e1/figures",
    
    # Reproducibility
    "random_seed": 42,
    
    # Error Handling
    "api_retry_attempts": 3,
    "api_retry_delay": 15,  # Seconds
    
    # Progress Saving
    "checkpoint_interval": 1  # Save after each λ evaluation
}
```

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied**: Standard HuggingFace datasets + GitHub repository pattern

### Configuration (Hardcoded Dict)

```python
DATA_CONFIG = {
    # MMLU Dataset
    "mmlu": {
        "dataset_name": "cais/mmlu",
        "split": "test",
        "dev_split": "dev",
        "few_shot_examples": 4,
        "subjects": "all",  # All 57 subjects
        "format": "multiple_choice"
    },
    
    # HumanEval Dataset
    "humaneval": {
        "install_command": "pip install git+https://github.com/openai/human-eval.git",
        "num_problems": 164,
        "timeout_seconds": 3.0,
        "execution_sandbox": True
    }
}
```

### Subtasks [4/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | MMLU Loader | Load test split + format few-shot prompts |
| C-1-2 | HumanEval Loader | Install repo + load 164 problems with unit tests |
| C-1-3 | Data Format | Convert to standard prompt templates |
| C-1-4 | Integration | Module imports + smoke test with 5 samples |

---

## A-2: API Client [Complexity: 9, Budget: 9]

**Applied**: Standard API client pattern with retry logic

### Configuration (Hardcoded Dict)

```python
API_CONFIG = {
    # Provider Selection
    "provider": "anthropic",  # or "openai"
    
    # Model Configuration
    "anthropic": {
        "model_id": "claude-3-opus-20240229",
        "api_key_env": "ANTHROPIC_API_KEY",
        "max_tokens": 512,
        "temperature": 0.0
    },
    
    "openai": {
        "model_id": "gpt-4-0613",
        "api_key_env": "OPENAI_API_KEY",
        "max_tokens": 512,
        "temperature": 0.0
    },
    
    # Policy Layer (System Prompts by λ)
    "compliance_levels": {
        0.2: "Answer directly and concisely.",
        0.4: "Be helpful and accurate.",
        0.6: "Provide helpful, accurate, and well-reasoned responses.",
        0.8: "Be extremely careful, ethical, and thorough in your responses.",
        1.0: "Follow all constitutional principles, ensuring safety, helpfulness, and harmlessness."
    },
    
    # Retry Logic
    "retry_attempts": 3,
    "retry_delay": 15,  # Seconds
    "exponential_backoff": False  # Fixed delay for simplicity
}
```

### Subtasks [4/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | API Client Class | Implement APIModelClient with generate() and batch_generate() |
| C-2-2 | Policy Layer | Map λ → system prompts + apply in API calls |
| C-2-3 | Retry Logic | 3 attempts with 15-second delay on failures |
| C-2-4 | Integration | Test API connection with sample prompt |

---

## A-3: Evaluation Engine [Complexity: 11, Budget: 11]

**Applied**: Standard evaluation pattern (few-shot MMLU + pass@k HumanEval)

### Configuration (Hardcoded Dict)

```python
EVAL_CONFIG = {
    # MMLU Evaluation
    "mmlu": {
        "few_shot_n": 4,
        "prompt_template": "{examples}\n\nQuestion: {question}\nA. {choice_a}\nB. {choice_b}\nC. {choice_c}\nD. {choice_d}\nAnswer:",
        "scoring": "exact_match",  # Predicted letter vs ground truth
        "aggregation": "per_subject_mean"
    },
    
    # HumanEval Evaluation
    "humaneval": {
        "metric": "pass_at_1",  # Standard HumanEval metric
        "num_samples": 1,  # Single completion per problem (temperature=0.0)
        "timeout": 3.0,  # Seconds per test execution
        "sandbox": True  # Isolated execution environment
    },
    
    # Results Format
    "output_format": "long_dataframe",  # Columns: [lambda, item_id, accuracy/pass]
    "save_raw_responses": True  # Audit trail
}
```

### Subtasks [4/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | MMLU Evaluator | Few-shot prompting + exact match scoring |
| C-3-2 | HumanEval Evaluator | Code execution + pass@1 calculation |
| C-3-3 | Data Collection | Long-format DataFrame with all results |
| C-3-4 | Integration | Test single λ evaluation end-to-end |

---

## A-4: Statistical Analysis [Complexity: 12, Budget: 12]

**Applied**: Standard statistical testing (ICC2 + ANOVA + effect sizes)

### Configuration (Hardcoded Dict)

```python
STATS_CONFIG = {
    # ICC (Intraclass Correlation Coefficient)
    "icc": {
        "model": "ICC2",  # Two-way mixed effects, absolute agreement
        "targets": "subject",  # MMLU subjects or HumanEval problems
        "raters": "lambda",  # Compliance levels
        "library": "pingouin",
        "threshold": 0.95
    },
    
    # ANOVA (One-way)
    "anova": {
        "method": "f_oneway",
        "correction": "bonferroni",
        "alpha": 0.05,
        "library": "scipy.stats",
        "threshold_pvalue": 0.05  # p > 0.05 for gate pass
    },
    
    # Cohen's f (Effect Size)
    "cohens_f": {
        "formula": "sqrt(eta_squared / (1 - eta_squared))",
        "eta_squared_formula": "(df1 * F) / (df1 * F + df2)",
        "threshold": 0.10
    },
    
    # Gate Validation
    "gate": {
        "conditions": ["icc > 0.95", "anova_p > 0.05", "cohens_f < 0.10"],
        "logic": "AND"  # All three must pass
    }
}
```

### Subtasks [4/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | ICC Calculation | Compute ICC2 with pingouin |
| C-4-2 | ANOVA + Effect Size | F-test + Cohen's f from F-statistic |
| C-4-3 | Gate Validation | Check all three conditions + binary pass/fail |
| C-4-4 | Integration | Test with mock results data |

---

## A-5: Visualization [Complexity: 10, Budget: 10]

**Applied**: Standard matplotlib/seaborn plotting patterns

### Configuration (Hardcoded Dict)

```python
VIZ_CONFIG = {
    # General Settings
    "dpi": 300,  # Publication quality
    "figure_format": "png",
    "style": "seaborn-v0_8-darkgrid",
    "font_size": 12,
    
    # Gate Metrics Chart (Mandatory)
    "gate_metrics_plot": {
        "type": "bar",
        "metrics": ["ICC", "ANOVA p-value", "Cohen's f"],
        "show_thresholds": True,
        "colors": ["blue", "green", "orange"],
        "filename": "gate_metrics.png"
    },
    
    # Capability Consistency Plot
    "capability_consistency": {
        "type": "line",
        "x_axis": "lambda",
        "y_axis": "accuracy",
        "error_bars": "std",
        "datasets": ["MMLU", "HumanEval"],
        "filename": "capability_consistency.png"
    },
    
    # Subject Heatmap
    "subject_heatmap": {
        "type": "heatmap",
        "rows": "mmlu_subjects",
        "columns": "lambda",
        "colormap": "YlGnBu",
        "annotate": False,  # Too many subjects (57)
        "filename": "subject_heatmap.png"
    },
    
    # Distribution Violin Plot
    "accuracy_distributions": {
        "type": "violin",
        "x_axis": "lambda",
        "y_axis": "accuracy",
        "split": False,
        "filename": "accuracy_distributions.png"
    }
}
```

### Subtasks [4/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Gate Metrics Chart | Bar chart with thresholds (MANDATORY) |
| C-5-2 | Consistency + Heatmap | Line plot + subject heatmap |
| C-5-3 | Distribution Plot | Violin plot for variance visualization |
| C-5-4 | Integration | Save all 4 figures to figures_dir |

---

## A-6: Orchestration [Complexity: 9, Budget: 9]

**Applied**: Standard pipeline orchestration with checkpointing

### Configuration (Hardcoded Dict)

```python
PIPELINE_CONFIG = {
    # Execution Order
    "stages": [
        "setup_environment",
        "load_datasets",
        "run_evaluations",  # Sequential by λ
        "compute_statistics",
        "generate_visualizations",
        "create_validation_report"
    ],
    
    # Checkpointing
    "checkpoint": {
        "enabled": True,
        "interval": 1,  # Save after each λ evaluation
        "format": "csv",  # Raw results
        "resume_support": True
    },
    
    # Progress Logging
    "logging": {
        "level": "INFO",  # Print statements for LIGHT tier
        "format": "%(asctime)s - %(message)s",
        "log_api_calls": True
    },
    
    # Validation Report
    "report": {
        "template": "04_validation_template.md",
        "sections": [
            "hypothesis_statement",
            "gate_criteria",
            "experimental_results",
            "pass_fail_decision",
            "figures",
            "raw_data_location"
        ],
        "output_path": "docs/youra_research/20260511_bi_align/h-e1/04_validation.md"
    }
}
```

### Subtasks [4/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Environment Setup | Verify API keys + load config |
| C-6-2 | Evaluation Loop | Sequential λ iterations with checkpointing |
| C-6-3 | Error Handling | API retry logic + progress saving |
| C-6-4 | Report Generation | Create 04_validation.md with results |

---

## Environment Variables

**Required:**
```bash
# API Authentication (choose one)
export ANTHROPIC_API_KEY="sk-ant-..."  # For Claude
export OPENAI_API_KEY="sk-..."         # For GPT-4
```

**Optional:**
```bash
# Override default output directory
export OUTPUT_DIR="/path/to/custom/output"
```

---

## Configuration Usage

### Loading Config in Code

```python
# main.py
from config import CONFIG, DATA_CONFIG, API_CONFIG, EVAL_CONFIG, STATS_CONFIG, VIZ_CONFIG, PIPELINE_CONFIG

# Access values
model_name = CONFIG["model_name"]
lambda_values = CONFIG["lambda_values"]
icc_threshold = CONFIG["gate_thresholds"]["icc_min"]

# Pass to modules
from models.api_client import APIModelClient
client = APIModelClient(
    model_name=API_CONFIG[CONFIG["api_provider"]]["model_id"],
    api_key_env=API_CONFIG[CONFIG["api_provider"]]["api_key_env"]
)
```

### Example Main Pipeline

```python
# main.py
def main():
    # Setup
    setup_environment()
    
    # Load data
    mmlu_loader = MMLULoader(DATA_CONFIG["mmlu"])
    humaneval_loader = HumanEvalLoader(DATA_CONFIG["humaneval"])
    
    # Initialize API client
    client = APIModelClient(CONFIG["model_name"], CONFIG["api_provider"])
    
    # Run evaluations
    results = []
    for lambda_val in CONFIG["lambda_values"]:
        system_prompt = CONFIG["compliance_prompts"][lambda_val]
        
        # MMLU
        mmlu_eval = MMLUEvaluator(client, mmlu_loader)
        mmlu_results = mmlu_eval.evaluate(lambda_val, system_prompt)
        
        # HumanEval
        he_eval = HumanEvalEvaluator(client, humaneval_loader)
        he_results = he_eval.evaluate(lambda_val, system_prompt)
        
        # Checkpoint
        save_checkpoint(mmlu_results, he_results, lambda_val)
        results.extend([mmlu_results, he_results])
    
    # Analyze
    analyzer = GateAnalyzer(results)
    gate_metrics = analyzer.validate_gate()
    
    # Visualize
    viz = ResultsVisualizer(CONFIG["figures_dir"])
    viz.plot_all(results, gate_metrics)
    
    # Report
    generate_report(gate_metrics, results, CONFIG["output_dir"])

if __name__ == "__main__":
    main()
```

---

## Total Subtask Allocation

| Task | Complexity | Budget | Subtasks Used |
|------|------------|--------|---------------|
| A-1 | 8 | 8 | 4 |
| A-2 | 9 | 9 | 4 |
| A-3 | 11 | 11 | 4 |
| A-4 | 12 | 12 | 4 |
| A-5 | 10 | 10 | 4 |
| A-6 | 9 | 9 | 4 |
| **Total** | **59** | **59** | **24** |

**Budget Status**: 24/59 subtasks used (40.7% allocation)

---

## Validation Checklist

**Configuration Completeness:**
- [x] Single format (Hardcoded dict only)
- [x] All modules have configs with defaults
- [x] EXISTENCE PoC: Single fixed config, no hyperparameter grid
- [x] Subtask count within budget (24/59)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included

**Pattern Application:**
- [x] Applied: Standard evaluation pipeline defaults
- [x] No non-standard values requiring rationale
- [x] All configs copy-paste ready for Phase 4

---

**Document Status**: COMPLETE  
**Next Phase**: Logic Design (03_logic.md)
