# H-C1 Configuration Schema

## YAML Schema

```yaml
# h-c1_config.yaml
experiment:
  id: "h-c1"
  name: "stratified_correlation_analysis"
  tier: "LIGHT"

models:
  base:  # 14 from h-e1
    - gpt2
    - gpt2-medium
    - gpt2-large
    - gpt2-xl
    - pythia-70m
    - pythia-160m
    - pythia-410m
    - pythia-1b
    - pythia-1.4b
    - pythia-2.8b
    - pythia-6.9b
    - pythia-12b
    - llama-7b
    - llama-13b
  instruction_tuned:  # 6 new
    - alpaca-7b
    - vicuna-7b
    - vicuna-13b
    - llama2-7b-chat
    - llama2-13b-chat
    - mistral-7b-instruct

hyperparameters:
  bootstrap_n: 1000
  threshold_r: 0.2      # gate: r > 0.2 per group
  min_samples: 30       # minimum samples per stratum
  confidence_level: 0.95
  random_seed: 42

paths:
  h_e1_cache: "../h-e1/cache/"
  output_dir: "./output/"
  results: "./output/results/"
  figures: "./output/figures/"

defaults:
  parallel_jobs: 4
  save_bootstrap_samples: false
  verbose: true
```

## Usage

```python
import yaml

with open("h-c1_config.yaml") as f:
    cfg = yaml.safe_load(f)

# Access
n_boot = cfg["hyperparameters"]["bootstrap_n"]
base_models = cfg["models"]["base"]
```

---
Skipped: validation schema, env overrides. Add when config grows beyond single file.
