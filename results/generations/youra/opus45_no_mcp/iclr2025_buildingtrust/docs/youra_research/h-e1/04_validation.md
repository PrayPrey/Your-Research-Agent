# Validation Report: H-E1 ECE Measurability

**Date:** 2026-08-19 (Updated)
**Hypothesis:** H-E1 (EXISTENCE)
**Gate Type:** MUST_WORK
**Result:** BLOCKED (awaiting API key)

---

## Executive Summary

Mock data generation code has been **removed** from api_client.py. The experiment now requires OPENAI_API_KEY to run. Previous results (shown below) were generated with mock/synthetic data and are **invalid**.

**Status:** Code fixed. Waiting for OPENAI_API_KEY to re-run with real LLM responses.

### Mock Fix Applied (Attempt 1)
- Removed `MOCK_MODE` global variable
- Removed `_mock_response()` function generating random confidence/answers
- Added `RuntimeError` if OPENAI_API_KEY not set
- Cleared mock response cache (603KB)

---

## Previous Results (INVALID - Mock Data)

**WARNING:** These results used synthetic random responses, not real GPT-3.5-turbo outputs.

---

## Gate Evaluation

| Condition | Extraction Rate | ECE | Accuracy | Gate |
|-----------|----------------|-----|----------|------|
| baseline | 99.27% | 0.2163 | 47.84% | PASS |
| cot_only | 99.27% | 0.2693 | 50.31% | PASS |
| confidence_only | 99.51% | 0.1754 | 50.31% | PASS |
| cot_confidence | 98.78% | 0.2594 | 51.67% | PASS |
| token_padding | 99.02% | 0.1822 | 50.06% | PASS |

**Threshold:** Extraction rate >= 95%, ECE in [0,1]

---

## Success Criteria Verification

| Criterion | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Confidence extraction rate | >95% per condition | 98.78-99.51% | PASS |
| ECE computability | 100% (all conditions) | 5/5 | PASS |
| ECE value range | [0,1] | 0.1754-0.2693 | PASS |

---

## Experimental Setup

- **Dataset:** TruthfulQA mc1 (817 items)
- **Model:** GPT-3.5-turbo-0125 (MOCK MODE)
- **Conditions:** 5 prompting strategies
- **ECE bins:** 15 (equal-width)

---

## Generated Outputs

### Data Files
- `results/results.json` - Full experimental data
- `outputs/results.csv` - Summary metrics

### Figures
- `figures/extraction_rate.png` - Gate metrics chart
- `figures/ece_comparison.png` - ECE by condition
- `figures/reliability_*.png` - Reliability diagrams (5)
- `figures/failure_breakdown.png` - Extraction failure types

---

## Code Structure

```
h-e1/code/
  config.py         - Configuration dataclasses
  data.py           - TruthfulQA loader
  prompts.py        - 5 condition templates
  api_client.py     - OpenAI wrapper + cache + mock
  extract.py        - Regex extraction
  metrics.py        - ECE computation
  run_experiment.py - Main orchestration
  visualize.py      - Figure generation
```

---

## Limitations

1. ~~**Mock Mode:** Results generated without actual API calls~~ FIXED
2. ~~**Random Accuracy:** ~50% accuracy reflects random answer selection in mock~~ FIXED

---

## Next Steps

1. **Set OPENAI_API_KEY:** `export OPENAI_API_KEY='sk-...'`
2. **Re-run experiment:** `python run_experiment.py`
3. **Validate with real data** then proceed to H-M1

---

## Code Changes (Mock Fix)

```diff
# api_client.py
- MOCK_MODE = not os.getenv("OPENAI_API_KEY")
- def _mock_response(self, prompt: str) -> str:
-     # ... random.randint, random.choice ...
+ if not os.getenv("OPENAI_API_KEY"):
+     raise RuntimeError("OPENAI_API_KEY environment variable required.")
```

---

*Phase 4 Validation - Mock Fix Applied, Awaiting Real API Key*
