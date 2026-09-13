# ExecGuide: Execution-Guided Constrained Decoding for Verified Code Generation

## Overview

This directory contains the implementation and experiments for **ExecGuide**, a constrained decoding framework that interleaves LLM token generation with incremental formal verification signals (SMT solver + execution sandbox) to improve code correctness.

## Hypothesis

**ExecGuide improves pass@1 on HumanEval** by soft-steering beam search candidates using verifiability potential scores derived from:
1. SMT consistency checks (Z3 solver)
2. Execution sandbox feedback (test case pass rates)
3. A learned reward model that estimates verifiability potential

## Files

- `config.py` - Experiment configuration
- `spec_augment.py` - HumanEval augmentation with SMT-checkable specifications
- `reward_model.py` - Verifiability potential reward model (Transformer-based)
- `execguide.py` - ExecGuide core framework
- `baselines.py` - Baseline methods (greedy, sampling, post-hoc repair, exec-only, SMT-only)
- `evaluation.py` - Evaluation utilities (pass@k, SCR, FPC, IOR)
- `run_experiment.py` - Main experiment runner
- `visualize.py` - Result visualization

## Running the Experiment

```bash
cd /path/to/claude_code

# Run full experiment
python run_experiment.py

# Generate visualizations
python visualize.py
```

## Methods Compared

| Method | Description |
|--------|-------------|
| Standard Greedy | Baseline beam search, no guidance |
| Multiple Sampling | Sample k completions, select any passing |
| Post-hoc Repair | Generate → test → repair loop (max 2 rounds) |
| Exec-Only Steering | Select best candidate by test pass rate only |
| SMT-Only Steering | Select best candidate by SMT consistency only |
| **ExecGuide (Ours)** | Soft-steer beams with SMT + execution + reward model |

## Evaluation Metrics

- **pass@1**: Fraction of problems solved in one attempt
- **FPC (First-Pass Correctness)**: Problems solved without repair
- **SCR (Specification Compliance Rate)**: Programs passing SMT checks
- **IOR (Inference Overhead Ratio)**: Time relative to standard decoding

## Requirements

- Python 3.8+
- PyTorch 2.0+
- transformers
- datasets
- z3-solver
- matplotlib
- numpy
