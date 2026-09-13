# H-E1: Jacobian Stable Rank Regularization

**Phase 4 Implementation - EXISTENCE Proof-of-Concept**

---

## Quick Start

### Running the Experiment

```bash
cd /home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_scsl_sonnet45_no_reflection/docs/youra_research/20260512_scsl/h-e1

# Install dependencies
pip install -r code/requirements.txt

# Run experiment (with GPU selection and timeout)
AVAILABLE_GPU=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 1000 {print $1; exit}')
export CUDA_VISIBLE_DEVICES=$AVAILABLE_GPU
timeout 14400 python code/run_experiment.py 2>&1 | tee experiment.log
```

### After Experiment Completes

```bash
# Generate validation report and update state
./finalize_phase4.sh
```

---

## Directory Structure

```
h-e1/
├── code/                      # Implementation
│   ├── config.py             # Configuration dataclasses
│   ├── data.py               # C4 streaming dataset
│   ├── model.py              # Baseline + Regularized GPT-2
│   ├── train.py              # Training loop
│   ├── evaluate.py           # Metrics evaluator
│   ├── visualize.py          # Figure generation
│   ├── run_experiment.py     # Main experiment runner
│   └── requirements.txt      # Dependencies
├── tests/                     # Test suite (23 tests)
│   ├── test_data.py
│   ├── test_model.py
│   ├── test_config.py
│   ├── test_evaluate.py
│   └── test_visualize.py
├── checkpoints/               # Model checkpoints
│   ├── baseline/
│   └── proposed/
├── figures/                   # Generated visualizations
├── results/                   # Experiment results (JSON)
├── 02b_context.md            # Phase 2B context
├── 02c_experiment_brief.md   # Phase 2C design
├── 03_architecture.md        # Phase 3 architecture
├── 03_config.md              # Phase 3 configuration
├── 03_logic.md               # Phase 3 logic
├── 03_prd.md                 # Phase 3 PRD
├── 03_tasks.yaml             # Phase 3 tasks
├── 04_validation.md          # Phase 4 validation report (after experiment)
├── 04_validation_template.md # Report template
├── IMPLEMENTATION_SUMMARY.md # Implementation details
├── check_status.sh           # Status checker
├── generate_validation_report.py  # Report generator
├── update_verification_state.py   # State updater
├── finalize_phase4.sh        # Finalization script
├── experiment.log            # Full experiment log
└── README.md                 # This file
```

---

## Hypothesis

**Statement:**
Under pretraining with explicit residual-corrected Jacobian stable rank (sr_ℓ^res) regularization, if models are trained to minimize sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2 per layer, then mean stable rank reduces by ≥20% relative to baseline while maintaining iso-perplexity (≤1% deviation).

**Gate Type:** MUST_WORK

**Success Criteria:**
1. Mean stable rank reduction ≥20%
2. Perplexity deviation ≤1%
3. Layer variance <2× mean
4. Measurement CV <15%

---

## Implementation Overview

### Key Components

**1. Stable Rank Regularizer** (`model.py`)
- Hutchinson trace estimator (10 probes)
- Power iteration spectral norm (5 iterations)
- Residual correction: J̃_ℓ = J_ℓ - I
- Stable rank: sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2

**2. Adaptive Lambda Tuning** (`train.py`)
- Monitors perplexity vs baseline
- Adjusts regularization strength
- Target: ±1% perplexity tolerance

**3. Data Pipeline** (`data.py`)
- C4 streaming (HuggingFace)
- GPT-2 tokenization
- Batch size 32, effective 128

**4. Evaluation** (`evaluate.py`)
- Perplexity computation
- Per-layer stable rank
- Layer variance (CV)
- Measurement precision

**5. Visualization** (`visualize.py`)
- Gate metrics (4-panel)
- Training trajectories
- Layer-wise distributions

---

## PoC Configuration

**Training:**
- Steps: 5,000 (vs 78,125 full)
- Tokens: ~320M (vs 10B full)
- Duration: ~30-60 min (vs 3-5 days full)

**Model:**
- GPT-2 125M (12 layers, 768 hidden)
- Random initialization
- Single seed (42)

**Hyperparameters:**
- Learning rate: 3e-4
- Batch size: 32 (effective 128)
- Lambda init: 0.01 (adaptive)
- Warmup: 2000 steps

---

## Monitoring Experiment

### Check Status

```bash
./check_status.sh
```

### Monitor Training

```bash
# Watch progress
tail -f experiment.log | grep -E "Step|PPL|GATE"

# Check GPU usage
watch -n 1 nvidia-smi
```

### Estimated Timeline

- Dataset download: ~2-5 min
- Baseline training: ~15-30 min
- Proposed training: ~15-30 min
- Evaluation: ~5 min
- Total: ~40-70 min

---

## After Completion

### 1. Check Results

```bash
# View gate validation
cat results/gate_validation.json | python3 -m json.tool

# View baseline metrics
cat results/baseline_poc_results.json | python3 -m json.tool

# View proposed metrics
cat results/proposed_poc_results.json | python3 -m json.tool
```

### 2. Generate Report

```bash
python3 generate_validation_report.py
cat 04_validation.md
```

### 3. Update Pipeline State

```bash
python3 update_verification_state.py
```

### 4. View Figures

```bash
ls -lh figures/
# gate_metrics.png
# layer_evolution.png
# stable_rank_distribution.png
# perplexity_trajectory.png
# measurement_precision.png
```

### 5. All-in-One

```bash
./finalize_phase4.sh
```

---

## Testing

### Run Test Suite

```bash
cd tests
python3 -m pytest -v
```

### Test Coverage

- **test_data.py:** Data loading (3 tests)
- **test_model.py:** Models (7 tests)
- **test_config.py:** Configuration (7 tests)
- **test_evaluate.py:** Evaluation (3 tests)
- **test_visualize.py:** Visualization (3 tests)

**Total:** 23 tests

---

## Troubleshooting

### Experiment Hangs

```bash
# Check if process is running
pgrep -f run_experiment.py

# Check GPU usage
nvidia-smi

# Kill if needed
pkill -f run_experiment.py
```

### Out of Memory

```bash
# Reduce batch size in code/config.py
# Change batch_size: int = 32 to batch_size: int = 16
```

### Dataset Download Issues

```bash
# Set HF cache directory
export HF_HOME=/path/to/large/disk
export HF_DATASETS_CACHE=/path/to/large/disk
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r code/requirements.txt
```

---

## Files Generated by Experiment

### Checkpoints
- `checkpoints/baseline/checkpoint_step_*.pt`
- `checkpoints/baseline/training_logs.json`
- `checkpoints/proposed/checkpoint_step_*.pt`
- `checkpoints/proposed/training_logs.json`

### Results
- `results/baseline_poc_results.json`
- `results/proposed_poc_results.json`
- `results/gate_validation.json`

### Figures
- `figures/gate_metrics.png` (mandatory)
- `figures/layer_evolution.png`
- `figures/stable_rank_distribution.png`
- `figures/perplexity_trajectory.png`
- `figures/measurement_precision.png`

### Reports
- `04_validation.md` (generated after experiment)
- `experiment.log` (full output)

---

## Next Steps

### If Gate PASSES

1. Review `04_validation.md`
2. Proceed to Phase 5 (Baseline Comparison)
3. Run full 10B token training (optional)
4. Multi-seed validation (optional)

### If Gate FAILS

1. Review failure analysis in `04_validation.md`
2. **Pipeline STOPS** (MUST_WORK gate)
3. Consider pivot options:
   - SVD-based rank regularization
   - Alternative Jacobian estimation
   - Gradient flow analysis

---

## Contact & Support

**Pipeline:** YouRA Phase 4 (Code Generation & Validation)  
**Date:** 2026-05-12  
**Status:** Implementation Complete, Experiment Running

For issues or questions, check:
- `IMPLEMENTATION_SUMMARY.md` for implementation details
- `experiment.log` for runtime errors
- `04_validation.md` for gate validation analysis
