# Phase 4 Validation Report: H-E1

**Hypothesis:** A statistically significant positive correlation (Spearman r > 0.2) exists between cumulative 13-gram benchmark overlap percentage and benchmark score inflation residual across Pythia model checkpoints.

**Date:** 2026-08-10  
**Gate Type:** MUST_WORK  
**Validation Status:** MOCK DATA FIXED - AWAITING REAL EXPERIMENT

---

## Mock Data Fix Summary

### Previous Issue
The original PoC validation used synthetic data with hard-coded correlation formula, making the experiment unable to fail. This was detected by external mock verification.

### What Was Fixed

1. **Removed `run_poc.py`** — Deleted file containing synthetic data generation with formula `contam_boost = effective_contam * 0.008`

2. **Updated `contamination.py`** — Removed silent mock fallback. Now requires:
   - `PILE_NGRAMS_DIR` environment variable for real Pile n-gram index, OR
   - `USE_LITERATURE_CONTAMINATION=1` for published research values (Yang et al. 2023)

3. **Updated `run.py`** — Main runner now tracks `poc_mode=False` and `data_source`

### Verification

```bash
# Without real data config, fails with clear error:
$ python -c "from contamination import contamination_by_task; contamination_by_task()"
ValueError: No Pile n-gram index provided. Either:
  1. Pass pile_ngrams argument with pre-loaded index
  2. Set PILE_NGRAMS_DIR environment variable
  3. Build index using: lm-eval-harness scripts/clean_training_data
  4. Set USE_LITERATURE_CONTAMINATION=1 to use published research values
```

---

## Data Sources (Post-Fix)

### Evaluation (Real)
- **Method:** lm-eval-harness via `evaluate.py`
- **Models:** Pythia checkpoints (410M, 1B, 1.4B, 2.8B, 6.9B, 12B)
- **Steps:** 12 key checkpoints per model
- **Benchmarks:** MMLU, ARC-Challenge, HellaSwag, WinoGrande
- **Capability measure:** WikiText-103 perplexity

### Contamination Options
| Option | Method | Validity |
|--------|--------|----------|
| Pile N-gram Index | `PILE_NGRAMS_DIR=/path` | Ground truth |
| Literature Values | `USE_LITERATURE_CONTAMINATION=1` | Published research baseline |

---

## Previous PoC Results (INVALID - Mock Data)

These results were from synthetic data and should NOT be used for scientific conclusions:

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Spearman r | 0.326 | > 0.2 | ~~PASS~~ (invalid) |
| p-value | 0.003 | < 0.05 | ~~PASS~~ (invalid) |

---

## How to Run Real Experiment

```bash
cd /home/PrayPrey/YouRA_no_IC_opus45/TEST_data_problems/docs/youra_research/h-e1/code

# Option A: With Pile n-gram index (preferred)
export PILE_NGRAMS_DIR=/path/to/pile_ngrams
./run_experiment.sh

# Option B: With literature contamination values
export USE_LITERATURE_CONTAMINATION=1
python run.py

# Test mode (reduced checkpoints)
H_E1_TEST_MODE=1 USE_LITERATURE_CONTAMINATION=1 python run.py
```

---

## Expected Runtime (Real Experiment)
- Evaluation: ~144 GPU-hours (72 checkpoints × ~2 hours each)
- N-gram extraction: ~48 CPU-hours (one-time, if building index)
- Correlation analysis: <1 minute

---

## Code Artifacts

| File | Purpose | Status |
|------|---------|--------|
| code/config.py | Experiment configuration | ✓ Updated |
| code/evaluate.py | lm-eval-harness runner | ✓ Unchanged |
| code/contamination.py | 13-gram overlap detection | ✓ Fixed |
| code/analysis.py | Detrending + correlation | ✓ Unchanged |
| code/visualize.py | Figure generation | ✓ Unchanged |
| code/run.py | Full pipeline orchestration | ✓ Updated |
| code/run_poc.py | Mock data generator | **DELETED** |
| code/run_experiment.sh | Shell wrapper | ✓ New |

---

## Gate Decision

**PENDING** - Requires real experiment run

The mock data fix is complete. Real experiment must be run to determine if correlation exists.

---

## Next Steps

1. Build Pile n-gram index OR use literature contamination mode
2. Run full experiment with real Pythia evaluations
3. Update this report with real results
4. If PASS: Proceed to Phase 5 baseline comparison

---

*Mock data fix applied: 2026-08-10*
*Original PoC runtime: 0.64 seconds (invalid mock data)*
