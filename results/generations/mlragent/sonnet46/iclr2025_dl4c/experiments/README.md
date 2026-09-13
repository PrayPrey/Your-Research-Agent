# HierAlign: Hierarchical Execution Feedback for Code Alignment

Experimental implementation of HierAlign - a post-training framework that constructs
hierarchical execution feedback signals to guide reinforcement learning for code alignment.

## Overview

This experiment tests the hypothesis that **hierarchical execution feedback provides better
training signal than binary pass/fail rewards** for code generation alignment.

### Reward Models Compared

1. **Binary (Pass/Fail)**: Traditional 0/1 reward based on test case execution
2. **Syntax Only**: Rewards syntactically valid code (ablation baseline)
3. **Coverage**: Syntax validity + partial test coverage score
4. **HierAlign (Full)**: 4-level hierarchical reward:
   - L1: Syntactic validity
   - L2: Runtime error classification with penalty shaping
   - L3: Partial test coverage
   - L4: Semantic distance via AST structure analysis

## Setup

Requirements: Python 3.8+, `anthropic` package

```bash
pip install anthropic numpy matplotlib scipy pandas
export ANTHROPIC_API_KEY=your_key_here
```

## Running the Experiment

```bash
cd claude_code/
python main.py
```

This will:
1. Generate code solutions at 3 quality levels (high/medium/low) using Claude API
2. Evaluate all solutions with 4 reward models
3. Compute discriminability metrics (Cohen's d, Kendall-tau)
4. Generate all figures
5. Save results to `results/`

## Output Files

```
results/
├── experiment_results.json   # Raw experiment data
├── log.txt                   # Execution log
└── figures/
    ├── reward_by_quality_level.png
    ├── discriminability_comparison.png
    ├── mean_rewards_by_level.png
    ├── reward_components_ablation.png
    ├── reward_guided_selection.png
    ├── per_problem_analysis.png
    └── summary_radar.png
```

## Key Metrics

- **Cohen's d**: Effect size for discriminating high vs low quality solutions
- **Kendall's tau**: Rank correlation between reward and true quality
- **Reward separation**: Difference in reward between full-pass and zero-pass solutions
- **Reward-guided selection**: How often the reward model selects a correct solution

## Files

- `main.py`: Entry point
- `run_experiment.py`: Core experiment logic
- `reward_models.py`: Reward model implementations
- `data.py`: HumanEval-style problem dataset
- `utils.py`: Code execution utilities
- `visualize.py`: Figure generation
