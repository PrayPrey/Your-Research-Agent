# DynaMix: Adaptive Data Mixing Experiment

## Overview

This experiment tests the hypothesis that **DynaMix** — an adaptive data mixing framework using gradient signal-to-noise ratio (SNR) monitoring and a reinforcement learning (RL) controller — achieves better language model performance compared to static baseline mixing strategies.

## Methods Compared

| Method | Description |
|--------|-------------|
| **Static Uniform** | Equal mixture weights for all 5 domains (0.2 each) |
| **Static Tuned** | Manually tuned weights inspired by Llama-2 proportions |
| **DoReMi-style** | Dynamic weights proportional to per-domain loss (higher loss → more data) |
| **PiKE-style** | Adaptive weights minimizing gradient conflicts (Li et al., 2025) |
| **DynaMix** | Proposed method: PPO-based RL controller using gradient SNR signals |

## Data Domains

The experiment uses 5 real text domains loaded from HuggingFace:
1. **Web** — C4 (Common Crawl)
2. **Code** — CodeSearchNet Python
3. **Science** — Scientific papers (PubMed / arXiv abstracts)
4. **Wiki** — Wikipedia
5. **Instructions** — Alpaca instruction-following data

## Model

- Small GPT-2 style language model (128 embedding dims, 4 layers, 4 attention heads)
- Trained for 2000 steps with batch size 32, sequence length 128
- Evaluated on per-domain cross-entropy loss and perplexity

## Requirements

```bash
pip install torch transformers datasets scipy numpy matplotlib
```

## Running the Experiment

```bash
cd tasks_youra_result_sonnet46/iclr2025_data_problems/claude_code
python run_experiment.py
```

The script will:
1. Download data from HuggingFace (cached after first run)
2. Train models with each mixing strategy
3. Generate figures in `outputs/`
4. Save results in `outputs/results.json`
5. Log all output to `outputs/log.txt`

## Output Structure

```
claude_code/
├── outputs/
│   ├── results.json          # Raw experiment results
│   ├── log.txt               # Experiment log
│   ├── training_curves.png   # Train/eval loss curves
│   ├── domain_perplexity.png # Per-domain perplexity
│   ├── mixture_evolution.png # Mixture weight evolution
│   ├── overall_comparison.png # Method comparison
│   ├── convergence_speed.png  # Convergence comparison
│   ├── scaling_law.png        # Scaling law fit (DynaMix)
│   └── rl_training.png        # RL controller training
```

## Key Files

- `config.py` — Experiment hyperparameters
- `data_utils.py` — Data loading from HuggingFace
- `model.py` — Small GPT-2 style language model
- `baselines.py` — Static and adaptive baseline mixers
- `dynamix.py` — DynaMix RL controller implementation
- `trainer.py` — Training loop
- `visualization.py` — Figure generation
- `run_experiment.py` — Main experiment runner
- `analyze_results.py` — Post-hoc analysis and results.md generation
