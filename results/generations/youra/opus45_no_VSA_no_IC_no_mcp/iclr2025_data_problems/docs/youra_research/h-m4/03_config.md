# H-M4: Scale Transfer Validation - Experiment Configuration

## Experiment Schema

```yaml
experiment:
  id: h-m4-scale-transfer
  hypothesis: "Optimal perplexity threshold (44.5 percentile) transfers across model scales"
  seeds: [42, 1337, 2024]
  conditions:
    - name: optimal_threshold
      percentile: 44.5
    - name: default_threshold
      percentile: 50.0
```

## Model Configurations

### GPT-2 125M

```yaml
model_125m:
  architecture: gpt2
  n_embd: 768
  n_layer: 12
  n_head: 12
  vocab_size: 50257
  block_size: 1024
  dropout: 0.1
  bias: false
```

### GPT-2 1B

```yaml
model_1b:
  architecture: gpt2
  n_embd: 1600
  n_layer: 48
  n_head: 25
  vocab_size: 50257
  block_size: 1024
  dropout: 0.1
  bias: false
```

## Training Hyperparameters

```yaml
training_125m:
  learning_rate: 6.0e-4
  min_lr: 6.0e-5
  warmup_tokens: 375_000_000  # ~3.75% of total
  total_tokens: 10_000_000_000
  batch_size: 480  # micro_batch * grad_accum * gpus
  micro_batch_size: 60
  gradient_accumulation: 8
  weight_decay: 0.1
  beta1: 0.9
  beta2: 0.95
  grad_clip: 1.0
  precision: fp16
  optimizer: adamw

training_1b:
  learning_rate: 2.0e-4
  min_lr: 2.0e-5
  warmup_tokens: 750_000_000  # ~3.75% of total
  total_tokens: 20_000_000_000
  batch_size: 960
  micro_batch_size: 30
  gradient_accumulation: 8
  weight_decay: 0.1
  beta1: 0.9
  beta2: 0.95
  grad_clip: 1.0
  precision: bf16
  optimizer: adamw
```

## Data Pipeline

```yaml
data:
  dataset: openwebtext  # or pile/c4
  tokenizer: gpt2
  
  filtering:
    optimal:
      percentile_threshold: 44.5
      # Computed from teacher model perplexity distribution
    default:
      percentile_threshold: 50.0
  
  preprocessing:
    shuffle: true
    pack_sequences: true
    seed_dependent: true  # Different shuffle per seed
  
  validation:
    split_ratio: 0.001
    fixed_seed: 0  # Same val set across runs
```

## Evaluation

```yaml
evaluation:
  checkpoints:
    - tokens: 1_000_000_000
    - tokens: 5_000_000_000
    - tokens: 10_000_000_000
    - tokens: 20_000_000_000  # 1B only
    - final: true
  
  benchmarks:
    - name: hellaswag
      metric: accuracy
      shots: 0
    - name: arc_easy
      metric: accuracy
      shots: 0
    - name: piqa
      metric: accuracy
      shots: 0
    - name: winogrande
      metric: accuracy
      shots: 0
  
  perplexity:
    datasets: [wikitext2, lambada]
  
  framework: lm-eval-harness
```

## Resource Requirements

```yaml
resources_125m:
  gpu: A100-40GB
  num_gpus: 1
  memory_per_gpu: 20GB
  time_per_run: ~8h
  total_runs: 6  # 2 conditions x 3 seeds
  total_gpu_hours: 48

resources_1b:
  gpu: A100-80GB
  num_gpus: 4
  memory_per_gpu: 60GB
  time_per_run: ~72h
  total_runs: 6
  total_gpu_hours: 1728

storage:
  checkpoints_per_run: 5
  checkpoint_size_125m: 500MB
  checkpoint_size_1b: 4GB
  logs_per_run: 100MB
  total_estimate: 200GB
```

## Run Matrix

```yaml
runs:
  # 125M scale
  - model: 125m
    condition: optimal
    seeds: [42, 1337, 2024]
  - model: 125m
    condition: default
    seeds: [42, 1337, 2024]
  
  # 1B scale
  - model: 1b
    condition: optimal
    seeds: [42, 1337, 2024]
  - model: 1b
    condition: default
    seeds: [42, 1337, 2024]

total_runs: 12
```
