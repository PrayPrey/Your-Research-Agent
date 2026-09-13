# Configuration Design: h-e1

**Hypothesis:** Dimensional Separability in Trustworthiness Benchmarks  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-04-14  
**Applied Pattern:** Hardcoded dict (minimal evaluation config)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch - designing new config schema  
**Config Files Found**: None - new config  
**Pattern Used**: Hardcoded dict

---

## Applied Patterns

Applied: Standard evaluation config (hardcoded dict for PoC simplicity)

---

## E3: Baseline Evaluation [Complexity: 9, Budget: 1]

### Configuration (Hardcoded Dict)

```python
# src/config.py
# EXISTENCE (PoC) Configuration - Fixed values for "does it work?" validation

CONFIG = {
    # Model ensemble (8 diverse LLMs)
    "model_names": [
        "gpt2",
        "gpt2-medium",
        "meta-llama/Llama-2-7b-hf",
        "mistralai/Mistral-7B-v0.1",
        "microsoft/phi-2",
        "tiiuae/falcon-7b",
        "facebook/opt-6.7b",
        "EleutherAI/pythia-6.9b"
    ],
    
    # Benchmark specifications
    "benchmarks": {
        "truthfulqa": {
            "dataset_name": "truthful_qa",
            "config": "multiple_choice",
            "tasks": ["mc1", "mc2"],
            "dimension": "truthfulness"
        },
        "bold": {
            "dataset_name": "AlexaAI/bold",
            "config": None,
            "domains": ["race", "gender", "religion", "profession", "political_ideology"],
            "dimension": "fairness"
        },
        "halueval": {
            "dataset_name": "pminervini/HaluEval",
            "config": None,
            "tasks": ["qa", "dialogue", "summarization"],
            "dimension": "hallucination"
        },
        "textattack": {
            "attack_recipe": "TextFoolerJin2019",
            "perturbation_constraint": 0.8,  # Semantic similarity threshold
            "dimension": "robustness"
        }
    },
    
    # Trustworthiness dimensions
    "dimensions": ["truthfulness", "fairness", "hallucination", "robustness"],
    
    # Dimension pairs for asymmetry analysis
    "dimension_pairs": [
        ("fairness", "robustness"),
        ("truthfulness", "hallucination"),
        ("truthfulness", "robustness"),
        ("fairness", "truthfulness")
    ],
    
    # Gate validation thresholds
    "gate_thresholds": {
        "asymmetry_threshold": 0.2,  # |Δτ| ≥ 0.2 required
        "min_significant_pairs": 2,  # Minimum pairs meeting threshold
        "p_value": 0.01,  # Statistical significance threshold
        "variance_threshold": 0.02  # Secondary criterion
    },
    
    # Model inference settings
    "inference": {
        "torch_dtype": "float16",  # FP16 for efficiency
        "device_map": "auto",  # Single GPU via CUDA_VISIBLE_DEVICES
        "batch_size": 4,  # Adaptive based on model size
        "max_new_tokens": 100  # Generation limit
    },
    
    # Output paths
    "output_paths": {
        "results_dir": "results",
        "figures_dir": "figures",
        "baseline_scores": "results/baseline_scores.csv",
        "stressed_scores": "results/stressed_scores.csv",
        "rankings": "results/rankings.csv",
        "statistics": "results/statistics.csv",
        "validation_report": "04_validation.md"
    },
    
    # Reproducibility
    "random_seed": 42
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E3-1 | Baseline evaluation implementation | Load models, run 4 benchmark evaluations, compute rankings |

---

## Configuration Notes

**EXISTENCE (PoC) Design Principles:**
- Fixed configuration values (no hyperparameter tuning)
- Single seed for reproducibility
- Minimal evaluation settings (FP16, batch size 4)
- Hardcoded dict format (no dataclass overhead for one-off experiment)

**Non-Standard Values:**
- `batch_size: 4` - Conservative default to avoid OOM on 7B models
- `max_new_tokens: 100` - Sufficient for benchmark tasks while preventing excessive generation

**Model Selection Rationale:**
- Architecture diversity: GPT-style (GPT-2, OPT, Pythia), Llama-style (Llama-2), Mistral (sliding window), Falcon (MQA), Phi-2 (compact)
- Scale range: 117M to 7B parameters
- Expected baseline performance range: [0.3, 0.7] (within required [0.2, 0.9])

**Benchmark Configuration:**
- TruthfulQA: HuggingFace dataset with MC1/MC2 tasks
- BOLD: 5 demographic domains for fairness evaluation
- HaluEval: 3 task types (QA, dialogue, summarization)
- TextAttack: TextFooler attack recipe with semantic similarity > 0.8

**Gate Thresholds:**
- Primary: |Δτ| ≥ 0.2 in ≥2 dimension pairs (p < 0.01)
- Secondary: Variance(Δτ) > 0.02
- Derived from Phase 2B verification plan specifications

---

**Document Status**: Complete  
**Next Phase**: Phase 4 (Implementation)  
**Configuration Format**: Hardcoded dict (copy-paste ready)  
**Estimated Configuration LOC**: ~70 lines
