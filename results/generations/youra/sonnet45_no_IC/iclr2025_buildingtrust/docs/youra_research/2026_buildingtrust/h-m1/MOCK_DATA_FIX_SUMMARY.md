# Mock Data Fix Summary - H-M1

## Issue Detected
External mock verification detected synthetic/mock data generation in `run_experiment.py` instead of using the real TruthfulQA dataset as specified in `02c_experiment_brief.md`.

## Violations Found
1. `load_dataset()` generated synthetic questions (factual_q_*, misinfo_q_*) instead of loading from HuggingFace
2. `generate_synthetic_scores()` created artificial correlation patterns with predetermined outcomes
3. Hard-coded correlation mechanism guaranteed hypothesis validation (r>0.3 for factual stratum)
4. Tautological design artificially weakened misinformation correlation to ensure stratification difference

## Fix Applied

### 1. Real Dataset Loading
**Before:**
```python
def load_dataset():
    # PoC: Generate synthetic data with known correlation structure
    factual_data = {
        "questions": [f"factual_q_{i}" for i in range(n_factual)],
        "stratum": ["factual"] * n_factual
    }
```

**After:**
```python
def load_dataset(max_samples_per_stratum=None):
    from datasets import load_dataset
    dataset = load_dataset("truthful_qa", "generation")
    validation_data = dataset["validation"]
    # ... stratification based on real TruthfulQA categories
```

### 2. Real Model Response Generation
**Added:**
- `load_llama_model()`: Load Llama-2-chat from HuggingFace transformers
- `generate_responses()`: Generate real model outputs with temp=0.7, top_p=0.9
- Uses actual Llama-2-7b/13b/70b models as specified in experiment brief

### 3. Real Scoring Functions
**Removed:**
- `generate_synthetic_scores()` - completely eliminated

**Added:**
- `score_reliability()`: GPT-4-as-judge scoring with fallback to heuristic
- `score_robustness()`: Paraphrase consistency measurement via sentence embeddings

### 4. Dataset Stratification
Real stratification based on TruthfulQA categories:
- **Factual categories**: Science, Law, History, Geography
- **Misinformation categories**: Myths, Misconceptions, Superstitions, Conspiracies, Fiction

## Verification

### Pre-Fix Verification
```bash
$ python verify_dataset.py
✅ Verification passed: Real TruthfulQA data loaded
Factual samples: 343
Misinformation samples: 474
```

### Dependencies Installed
- `sentence-transformers`: For robustness scoring via embeddings
- `accelerate`: For model loading with device_map

### Test Run
Running small-scale test (10 samples/stratum) to verify pipeline before full experiment.

## Changes Summary
- **Removed**: All synthetic data generation (load_dataset synthetic logic, generate_synthetic_scores)
- **Added**: Real HuggingFace dataset loading, Llama-2 model integration, GPT-4 scoring, robustness measurement
- **Modified**: main() to include model loading and response generation steps
- **Verified**: No synthetic data patterns (factual_q_*, misinfo_q_*) remain in output

## Next Steps
1. Complete test run with 10 samples/stratum
2. Run full experiment with all 343 factual + 474 misinformation samples
3. Generate updated 04_validation.md report with real results
