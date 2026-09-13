# H-M1 Configuration

Characterization study only — no training. Single-shot GPT-4o-mini on 538 HumanEval+MBPP problems.

## Generation

```yaml
model: gpt-4o-mini
temperature: 0.2
max_tokens: 512
n: 1
rate_limit: 1  # req/sec
```

## Execution

```yaml
timeout: 10       # seconds per problem
sandbox: human_eval unsafe_execute  # restricted globals
tmp_dir: /tmp/h-m1/
```

## Classifier

```yaml
pyright_timeout: 10  # seconds
runtime_error_patterns:
  - TypeError
  - AttributeError
  - NameError
  - IndexError
  - KeyError
  - ValueError
  - ImportError
priority: type_error > runtime_error > logic_error
```

## Evaluation

```yaml
mixed_distribution_threshold: 0.80
classifier_agreement_threshold: 0.70
spot_check_n: 50
min_per_class: 10
```

## Output

```yaml
results_dir: results/h-m1/
figures_dir: docs/youra_research/h-m1/figures/
results_file: results.jsonl
summary_file: summary.json
```

## Cost Estimate

- 538 problems × ~200 output tokens × $0.60/1M ≈ **$0.06**
- Time: ~9 min at 1 req/sec
