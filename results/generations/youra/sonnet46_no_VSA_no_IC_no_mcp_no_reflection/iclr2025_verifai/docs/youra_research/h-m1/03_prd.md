# PRD: H-M1 Bug-Type Distribution Characterization

**Hypothesis:** H-M1
**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Type:** MECHANISM — characterization study (no training)

---

## 1. Goal

Characterize the bug-type distribution of GPT-4o-mini single-shot failures on 538 HumanEval+MBPP problems. Validate that no single bug type exceeds 80% of failures (mixed distribution precondition for H-M2/M3/M4 differential coverage hypotheses).

---

## 2. Success Criteria

| Criterion | Target | Priority |
|-----------|--------|----------|
| Mixed distribution | max(bug_type_fractions) < 0.80 | MUST |
| Classifier agreement | Pyright agreement ≥ 70% on 50-problem spot-check | SHOULD |
| Coverage | ≥ 10 failures per bug class | SHOULD |
| Code runs | No crash on all 538 problems | MUST |

---

## 3. Dataset

- **HumanEval**: 164 problems via `pip install human-eval`
- **MBPP**: 374 problems via `datasets.load_dataset("google-research-datasets/mbpp", "sanitized")`
- **Combined**: 538 problems, no preprocessing
- **Reuse**: H-E1 generated solutions (same temp=0.2 protocol) may be reused to save ~$0.06 API cost

---

## 4. Model & Generation

- **Model**: `gpt-4o-mini` via OpenAI Python SDK
- **Temperature**: 0.2 (same as H-E1)
- **Max tokens**: 512
- **Runs**: 1 (single-shot, no repair loop)
- **Rate limit**: 1 req/sec (~9 min for 538 problems)
- **Cost**: ~$0.06

---

## 5. Error Classification

Three-class heuristic classifier:

1. **type_error**: Pyright detects static type diagnostics (severity=error)
2. **runtime_error**: Execution produces TypeError/AttributeError/NameError/IndexError/KeyError/ValueError/ImportError
3. **logic_error**: AssertionError or test mismatch (wrong output, no exception)

Priority order: type_error > runtime_error > logic_error (Pyright checked first).

---

## 6. Outputs

- `results/h-m1/results.jsonl` — per-problem records: `{id, bug_type, execution_result}`
- `results/h-m1/summary.json` — distribution fractions, pass count, max_fraction, passed boolean
- `figures/` — bar chart (required), stacked bar HumanEval vs MBPP, spot-check agreement matrix

---

## 7. Implementation Scope

**In scope:**
- Dataset loading (HumanEval + MBPP)
- GPT-4o-mini generation loop (or reuse H-E1 outputs)
- Sandboxed execution via human_eval harness
- Three-class classifier (Pyright + exception parsing)
- 50-problem manual spot-check for classifier agreement
- Result summary + figures

**Out of scope:**
- Repair loops (H-M2+)
- Multi-model comparison
- Hyperparameter search

---

## 8. Dependencies

```
human-eval          # pip install human-eval
datasets            # HuggingFace
openai              # GPT-4o-mini API
pyright             # npm install -g pyright OR pip install pyright
scipy               # chi2_contingency for distribution summary
matplotlib          # figures
```

---

## 9. Risk & Fallback

| Risk | Fallback |
|------|---------|
| Pyright agreement < 60% | Collapse to 2-class: type_error vs non-type_error |
| Single type > 80% | SCOPE limitation; proceed with warning, document for P2 |
| H-E1 outputs unavailable | Re-generate (~$0.06, ~9 min) |
