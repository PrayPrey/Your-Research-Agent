# H-M1 Configuration

## Fixed Statistical Parameters

```python
N_PAIRS        = 6
P_NULL         = 0.5
ALTERNATIVE    = "greater"       # one-sided: DPO > SFT
GATE_K_BBQ     = 4               # k_BBQ >= 4
GATE_P_BBQ     = 0.125           # p_BBQ <= 0.125
FISHER_EPS     = 1e-8            # var denominator guard
```

No tuning parameters. All values are fixed by hypothesis specification.

---

## Model Pair Registry

```python
# Key format: experiment_results.json model_scores keys (dashes, not slashes)
PAIRS = [
    {
        "sft": "mistralai-Mistral-7B-Instruct-v0.1",
        "dpo": "HuggingFaceH4-zephyr-7b-alpha",
        "base": "mistralai/Mistral-7B-v0.1",
    },
    {
        "sft": "teknium-OpenHermes-2.5-Mistral-7B",
        "dpo": "HuggingFaceH4-zephyr-7b-beta",
        "base": "mistralai/Mistral-7B-v0.1",
    },
    {
        "sft": "allenai-tulu-2-7b",
        "dpo": "allenai-tulu-2-dpo-7b",
        "base": "meta-llama/Llama-2-7b-hf",
    },
    {
        "sft": "meta-llama-Llama-2-7b-chat-hf",
        "dpo": "Intel-neural-chat-7b-v3-1",
        "base": "meta-llama/Llama-2-7b-hf",
    },
    {
        "sft": "openchat-openchat_3.5",
        "dpo": "berkeley-nest-Starling-LM-7B-alpha",
        "base": "mistralai/Mistral-7B-v0.1",
    },
    {
        "sft": "mistralai-Mistral-7B-Instruct-v0.3",
        "dpo": "Intel-neural-chat-7b-v3-3",
        "base": "mistralai/Mistral-7B-v0.3",
    },
]

BENCHMARKS = ["bbq", "winogender_all", "winogrande", "truthfulqa_mc2"]
```

---

## Paths

```python
import os

REPO_ROOT       = os.path.dirname(os.path.abspath(__file__))   # h-m1/code/
HE1_RESULTS_PATH = os.path.join(
    REPO_ROOT, "../../h-e1/experiment_results.json"
)
FIGURES_DIR     = os.path.join(REPO_ROOT, "../figures")
RESULTS_OUT_PATH = os.path.join(REPO_ROOT, "../hm1_results.json")
```

---

## Software Requirements

```
Python   >= 3.10
scipy    >= 1.7     # binomtest added in 1.7
numpy    >= 1.21
matplotlib >= 3.5
```

No GPU, no model weights, no training dependencies.
