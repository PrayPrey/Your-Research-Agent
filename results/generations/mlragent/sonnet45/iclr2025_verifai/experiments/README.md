# Neural-Symbolic Repair: Experimental Implementation

This directory contains the implementation and experiments for the Neural-Symbolic Repair framework, which integrates formal verification with LLM-based code generation through iterative feedback synthesis.

## Overview

The Neural-Symbolic Repair (VeriL) framework addresses the challenge of LLM-generated code containing subtle bugs by:
1. Generating initial code from natural language specifications
2. Running formal verification and unit tests
3. Synthesizing actionable feedback from verification results
4. Iteratively repairing code until it passes all checks

## Project Structure

```
claude_code/
├── config.py              # Configuration parameters
├── data.py                # Problem dataset generation
├── model.py               # LLM interface for code generation
├── verification.py        # Code verification and feedback synthesis
├── evaluation.py          # Evaluation metrics and analysis
├── utils.py               # Utility functions
├── run_experiment.py      # Main experiment script
├── visualize_results.py   # Visualization script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup

### Prerequisites
- Python 3.8+
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running Experiments

### Full Experiment

Run all baseline methods and generate results:

```bash
python run_experiment.py
```

This will:
- Generate a dataset of programming problems
- Run 4 baseline methods:
  - `no_feedback`: LLM without verification feedback
  - `raw_feedback`: Direct verification output to LLM
  - `veril_static`: VeriL with template-based feedback
  - `veril_dynamic`: VeriL with LLM-based feedback synthesis (our method)
- Save results to JSON files
- Log progress to `log.txt`

### Visualization

After running experiments, generate visualizations:

```bash
python visualize_results.py
```

This creates:
- `model_comparison.png`: Comparison of methods across metrics
- `learning_curve_comparison.png`: Success rate vs iterations
- `success_failure_comparison.png`: Success/failure distribution
- `iteration_distribution.png`: Histogram of iterations needed
- `test_pass_progression.png`: Test pass rate improvement

## Configuration

Edit `config.py` to modify:
- `NUM_PROBLEMS`: Number of problems to test (default: 50)
- `MAX_ITERATIONS`: Maximum repair iterations (default: 5)
- `LLM_MODEL`: Model for code generation (default: gpt-4o-mini)
- `BASELINES`: List of methods to evaluate

## Output Files

- `log.txt`: Detailed execution log
- `all_results.json`: Complete results for all problems and methods
- `baseline_results.json`: Aggregated metrics per method
- `problems_dataset.json`: Generated problem dataset
- `*.png`: Visualization figures

## Baselines

### 1. No Feedback
LLM generates code but receives no verification feedback, just retries on failure.

### 2. Raw Feedback
LLM receives raw error messages from verification tools without processing.

### 3. VeriL Static
Uses template-based feedback synthesis with predefined patterns.

### 4. VeriL Dynamic (Our Method)
Uses LLM-based feedback synthesis to generate natural language explanations, counterexamples, and repair hints.

## Evaluation Metrics

- **Repair Success Rate (RSR)**: Percentage of problems successfully verified
- **Average Repair Iterations (ARI)**: Mean iterations for successful repairs
- **Test Pass Rate**: Percentage of test cases passed
- **Convergence Rate**: Percentage reaching stable state

## Expected Results

The VeriL Dynamic method should demonstrate:
- Higher repair success rates (40-60% improvement over baselines)
- Fewer iterations needed for successful repairs
- Better test pass rates across problems

## Troubleshooting

### API Rate Limits
If you encounter rate limits, adjust the sleep time in `run_experiment.py` or reduce `NUM_PROBLEMS`.

### Missing Dependencies
Ensure all packages in `requirements.txt` are installed.

### OpenAI API Key
Verify the `OPENAI_API_KEY` environment variable is set:
```bash
echo $OPENAI_API_KEY
```

## Citation

If you use this code, please cite:
```
Neural-Symbolic Repair: Self-Correcting LLM Code Generation via
Iterative Formal Feedback Synthesis (2025)
```
