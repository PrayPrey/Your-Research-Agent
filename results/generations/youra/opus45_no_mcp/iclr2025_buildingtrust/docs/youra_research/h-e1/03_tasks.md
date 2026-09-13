# Tasks: H-E1 ECE Measurability Validation

**Type**: EXISTENCE (LIGHT tier)
**Budget**: 8 tasks / 15 max

## Task List

| ID | Task | Description | Complexity | Files |
|----|------|-------------|------------|-------|
| A-1 | Data loading | Load TruthfulQA mc1, format choices | 4 | data.py |
| A-2 | Prompt templates | 5 condition templates + builder | 3 | prompts.py |
| A-3 | API client + cache | OpenAI wrapper, JSONL disk cache | 6 | api_client.py |
| A-4 | Confidence extraction | Regex extraction, failure handling | 4 | extract.py |
| A-5 | Answer extraction | Regex extraction, letter validation | 3 | extract.py |
| A-6 | ECE computation | 15-bin ECE + extraction_rate fn | 5 | metrics.py |
| A-7 | Experiment orchestration | Run 5 conditions, save results JSON | 7 | run_experiment.py |
| A-8 | Visualization | Gate chart, reliability diagrams, ECE bar, failure pie | 6 | visualize.py |

## Dependencies

```
A-1 (data) -> A-7 (orchestration)
A-2 (prompts) -> A-7 (orchestration)
A-3 (api_client) -> A-7 (orchestration)
A-4 (extract) -> A-7 (orchestration)
A-5 (extract) -> A-7 (orchestration)
A-6 (metrics) -> A-7 (orchestration)
A-7 (orchestration) -> A-8 (visualization)
```

## Execution Order

1. A-1, A-2, A-3, A-4, A-5, A-6 (parallel)
2. A-7 (depends on all above)
3. A-8 (depends on A-7)

## Summary

- **Total**: 8 tasks
- **Complexity sum**: 38
- **Budget compliance**: ✓ (8 ≤ 15 LIGHT)
