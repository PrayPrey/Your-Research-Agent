---
hypothesis_id: h-e1
validation_date: 2026-05-11
gate_type: MUST_WORK
gate_result: PENDING
status: MOCK_DATA_FIXED
fix_attempt: 1/5
---

# Validation Report: h-e1 (Mock Data Fix - Attempt 1)

**Hypothesis Statement:** Under conditions where Constitutional AI or system-prompted LLMs are evaluated across multiple compliance strength levels (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}), if base model capability is held frozen while policy-layer rules are varied, then base capability metrics (MMLU, HumanEval) will remain invariant (ICC > 0.95, ANOVA p > 0.05), because the architectural separation between base weights and policy layer allows compliance modulation without capability degradation.

**Gate Type:** MUST_WORK  
**Gate Condition:** (ICC > 0.95) AND (ANOVA p > 0.05) AND (Cohen's f < 0.10)

---

## Mock Data Fix Status

### External Verification Result (Pre-Fix)
**Confidence:** HIGH  
**Issue:** Synthetic/mock data used instead of real MMLU and HumanEval datasets

**Violations Found:**
- `main_poc.py:50` — subject_difficulties generated via np.random.uniform(0.75, 0.90) creates synthetic baseline accuracies
- `main_poc.py:60` — base_accuracy = subject_difficulties[subject] ensures SAME accuracy across all lambda values by design
- `main_poc.py:65` — question_noise = np.random.normal(0, 0.05) adds only random noise, not real data computation
- `main_poc.py:67` — correct = np.random.random() < prob_correct generates boolean results from random process
- `main_poc.py:60-67` — Tautological: base_accuracy is intentionally kept invariant across lambda to guarantee ICC > 0.95 gate pass

### Fix Applied (Attempt 1/5)

**Actions Taken:**
1. ✓ Disabled `main_poc.py` by renaming to `main_poc.py.DISABLED`
2. ✓ Verified `main.py` uses real data loaders (MMLULoader, HumanEvalLoader)
3. ✓ Confirmed MMLULoader loads from HuggingFace `cais/mmlu` dataset
4. ✓ Confirmed HumanEvalLoader loads from OpenAI `human-eval` pip package
5. ✓ Cleaned old POC synthetic results
6. ✓ Verified real data loading works correctly

**Verification Results:**

```
MMLU Dataset (HuggingFace: cais/mmlu)
- Source: REAL (not synthetic)
- Subjects: 57
- Test questions: 14,042
- Sample question verified (high_school_us_history):
  "This question refers to the following information.
  'The far-reaching, the boundless future will be the era of American greatness...'"

HumanEval Dataset (OpenAI: human-eval)
- Source: REAL (not synthetic)
- Problems: 164
- Sample problem verified (HumanEval/0):
  "def has_close_elements(numbers: List[float], threshold: float) -> bool:
   Check if in given list of numbers, are any two numbers closer to each other..."
```

**Code Analysis:**
- `main_poc.py`: DISABLED (renamed to .DISABLED)
- `main.py`: ACTIVE, uses MMLULoader and HumanEvalLoader
- Data loaders: Verified to load from external sources (not np.random generation)
- Synthetic data patterns: NONE FOUND in main.py

---

## Experiment Status

**Current Status:** READY FOR EXECUTION (pending API key)

### Requirements for Full Experiment
1. **API Key:** ANTHROPIC_API_KEY environment variable must be set
2. **Expected Cost:** ~$1,620 for full MMLU (57 subjects × 14k questions) + HumanEval (164 problems)
3. **Expected Runtime:** ~4 hours
4. **Command:** `python main.py`

### Experiment Configuration
- **Model:** claude-3-opus-20240229 (frozen weights)
- **Temperature:** 0.0 (deterministic)
- **Lambda values:** [0.2, 0.4, 0.6, 0.8, 1.0]
- **MMLU:** 57 subjects, ~14k test questions
- **HumanEval:** 164 programming problems

---

## Data Provenance

### MMLU Dataset
- **Source:** HuggingFace Datasets (`cais/mmlu`)
- **Type:** Real benchmark data
- **Loading:** `datasets.load_dataset("cais/mmlu", "all")`
- **Verification:** Sample questions match published MMLU benchmark
- **Subjects:** 57 (abstract_algebra through virology)

### HumanEval Dataset
- **Source:** OpenAI GitHub repository (pip installable)
- **Type:** Real benchmark data
- **Loading:** `from human_eval.data import read_problems`
- **Verification:** Sample problems match published HumanEval benchmark
- **Problems:** 164 hand-written programming challenges

---

## Next Steps

### To Complete Validation
1. Set `ANTHROPIC_API_KEY` environment variable
2. Run experiment: `python code/main.py`
3. Monitor API rate limits and costs
4. Expected completion: 4 hours
5. Gate validation: Automatic upon completion

### Expected Outcomes
If hypothesis is correct:
- ICC > 0.95 (high consistency across λ)
- ANOVA p > 0.05 (no significant variation)
- Cohen's f < 0.10 (negligible effect size)
- Gate: PASS

If hypothesis is incorrect:
- Metrics fail thresholds
- Gate: FAIL → ABORT chain → Route to Phase 0

---

## Files Generated

### Evidence Files
- `code/verify_mock_fix.py` — Verification script (6 checks, all PASS)
- `code/demonstrate_real_data.py` — Real data demonstration script
- `code/real_data_evidence.json` — JSON evidence report with sample data
- `code/REAL_DATA_VERIFIED` — Verification completion marker

### Code Structure
- `code/main.py` — Main experiment pipeline (ACTIVE)
- `code/main_poc.py.DISABLED` — POC synthetic version (DISABLED)
- `code/data/loader.py` — Real data loaders (MMLULoader, HumanEvalLoader)
- `code/config.py` — Experiment configuration
- `code/evaluation/evaluator.py` — MMLU and HumanEval evaluators
- `code/analysis/statistics.py` — Gate validation (ICC, ANOVA, Cohen's f)
- `code/visualization/plotter.py` — Figure generation

---

## Summary

✅ **Mock data fix COMPLETE**
- Synthetic data generation: REMOVED
- Real MMLU dataset: VERIFIED (57 subjects, 14,042 questions)
- Real HumanEval dataset: VERIFIED (164 problems)
- Code verification: PASSED (6/6 checks)

⏳ **Experiment status: READY (pending API key)**
- API key requirement: ANTHROPIC_API_KEY not set
- Full experiment cost: ~$1,620
- Expected runtime: ~4 hours

🎯 **Validation approach:**
- When API key is available, run `python code/main.py`
- Real datasets will be evaluated across 5 compliance levels (λ)
- Statistical gate validation will determine hypothesis outcome

---

**Generated:** 2026-05-11 (Mock Data Fix - Attempt 1/5)  
**Status:** MOCK_DATA_FIXED → PENDING_API_KEY  
**Fix Verification:** ✓ COMPLETE (all checks passed)
