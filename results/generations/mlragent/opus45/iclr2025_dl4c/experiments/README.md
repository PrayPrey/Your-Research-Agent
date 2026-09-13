# ExePlay: Execution-Guided Self-Play for Code Agent Alignment

This repository contains the implementation of **ExePlay**, a self-play framework for code agent alignment that uses execution feedback to train code generation models without human annotation.

## Overview

ExePlay operates in three phases:
1. **Generation**: The agent generates multiple solutions for programming tasks
2. **Critique Generation**: A critic module analyzes execution failures and generates natural language explanations
3. **Contrastive Alignment**: Preference pairs are constructed from solutions with different quality scores, weighted by the Execution Quality Score (EQS)

## Key Features

- **Execution Quality Score (EQS)**: A multi-dimensional score combining:
  - Test pass rate (40%)
  - Code coverage (20%)
  - Error proximity (20%)
  - Behavior similarity (20%)

- **Weighted DPO Training**: Preference pairs are weighted by their EQS margin for more informative training signals

- **Self-Repair**: Failed solutions can be repaired using execution feedback

## Project Structure

```
claude_code/
├── config.py              # Configuration parameters
├── data_loader.py         # Dataset loading utilities
├── execution_feedback.py  # Execution and EQS computation
├── exeplay_framework.py   # Main ExePlay framework
├── baselines.py           # Baseline methods
├── visualization.py       # Result visualization
├── run_experiment.py      # Main experiment runner
└── README.md              # This file
```

## Requirements

- Python 3.8+
- PyTorch 2.0+
- Transformers
- datasets
- matplotlib
- numpy

## Installation

```bash
pip install torch transformers datasets matplotlib numpy
```

## Running the Experiment

### Basic Usage

```bash
python run_experiment.py
```

### With Custom Parameters

```bash
python run_experiment.py \
    --num_tasks 50 \
    --num_iterations 3 \
    --samples_per_task 4 \
    --dataset synthetic \
    --seed 42
```

### Parameters

- `--num_tasks`: Number of programming tasks to use (default: 30)
- `--num_iterations`: Number of ExePlay self-play iterations (default: 3)
- `--samples_per_task`: Number of code samples to generate per task (default: 4)
- `--dataset`: Dataset to use (`synthetic`, `mbpp`, or `humaneval`)
- `--seed`: Random seed for reproducibility (default: 42)

## Output

Results are saved in the `outputs/` directory:
- `results.json`: Complete experiment results
- `log.txt`: Experiment execution log
- `*.png`: Visualization figures

## Baselines

The experiment compares ExePlay against:
1. **Base Model**: Direct generation without alignment
2. **Binary Execution**: Pass/fail feedback only
3. **Self-Repair**: Simple error-based repair

## Citation

If you use this code, please cite:

```bibtex
@article{exeplay2025,
  title={Execution-Guided Self-Play for Code Agent Alignment},
  year={2025}
}
```
