# SECACE: Self-Evolving Code Agents through Counterfactual Execution Feedback

This directory contains the implementation and experiments for the SECACE framework, which enables code generation agents to learn from execution failures through counterfactual reasoning.

## Overview

SECACE addresses the challenge of code generation by systematically analyzing execution failures and generating counterfactual code variants that could lead to success. The framework consists of:

1. **Execution Trace Analysis**: Identifies critical decision points in failed code
2. **Counterfactual Code Generation**: Creates minimal code modifications at critical points
3. **Contrastive Alignment**: Learns from (failure, counterfactual success) pairs
4. **Self-Evolution**: Continuously improves through deployment experience

## Project Structure

```
claude_code/
├── config.py                    # Configuration and hyperparameters
├── tasks.py                     # Programming task definitions
├── llm_interface.py             # LLM API interface (GPT-4o-mini)
├── code_executor.py             # Code execution and testing
├── counterfactual_generator.py  # Counterfactual code generation
├── agents.py                    # Agent implementations (Simple, Reflection, SECACE)
├── run_experiment.py            # Main experiment runner
├── visualize_results.py         # Results visualization
└── README.md                    # This file
```

## Requirements

- Python 3.8+
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)
- Required packages:
  - openai
  - matplotlib
  - numpy

Install dependencies:
```bash
pip install openai matplotlib numpy
```

## Running Experiments

### 1. Set up environment

Make sure your OpenAI API key is set:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Run all experiments

```bash
python run_experiment.py
```

This will:
- Run 20 programming tasks with 3 different methods:
  - Simple Retry Agent (baseline with error feedback)
  - Reflection Agent (self-reflection based debugging)
  - SECACE Agent (counterfactual execution feedback)
- Save results to `experiment_results.json`
- Log progress to `log.txt`

### 3. Generate visualizations

```bash
python visualize_results.py
```

This creates visualizations in the `figures/` directory:
- Success rate comparison
- Average attempts to solution
- Cumulative success by attempt number
- Time efficiency comparison
- Counterfactual generation statistics
- Task-wise performance comparison

## Experimental Design

### Tasks
The experiments use 20 programming tasks covering various algorithmic challenges:
- Array manipulation (sum, reverse, merge)
- String processing (palindrome, anagram)
- Data structures (searching, sorting)
- Algorithm implementation (Fibonacci, prime numbers)

Each task includes multiple test cases for validation.

### Methods Compared

1. **Simple Retry Agent**: Basic approach that generates code and retries with error messages
2. **Reflection Agent**: Uses structured self-reflection to analyze failures before fixing
3. **SECACE Agent**: Generates counterfactual code variants and learns from successful modifications

### Metrics

- **Success Rate**: Percentage of tasks solved within max attempts
- **Average Attempts**: Mean number of iterations to reach solution
- **Time Efficiency**: Average time for successful solutions
- **Counterfactuals Generated**: Number of code variants explored (SECACE only)

## Configuration

Key parameters in `config.py`:
- `MODEL_NAME`: LLM model to use (default: "gpt-4o-mini")
- `NUM_TASKS`: Number of tasks to evaluate (default: 20)
- `MAX_ATTEMPTS`: Maximum fix attempts per task (default: 5)
- `TIMEOUT`: Code execution timeout in seconds (default: 30)

## Results

After running experiments, results are stored in:
- `experiment_results.json`: Raw experimental data
- `log.txt`: Detailed execution log
- `figures/`: Visualization plots
- `results.md`: Analysis and summary (generated after experiments)

## Citation

If you use this code, please cite:

```
Self-Evolving Code Agents through Counterfactual Execution Feedback
Workshop on Deep Learning for Code (DL4C) at ICLR 2025
```

## License

MIT License - see LICENSE file for details.
