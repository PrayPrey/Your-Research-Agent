#!/usr/bin/env python3
"""
Phase 4 Experiment Entry Point for H-E1

Runs the real GRPO vs DPO experiment using:
- Training data: CodeAlpaca-20K (sahil2801/CodeAlpaca-20k)
- Evaluation: HumanEval+ via evalplus
- Models: DeepSeek-Coder-7B-instruct-v1.5
- Metrics: Semantic-edit-per-KL with bootstrap CI

Delegates to run_experiment.py for the full training + evaluation pipeline.
"""

import os
import sys

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

from run_experiment import run_experiment

if __name__ == "__main__":
    results = run_experiment()
    sys.exit(0 if results.get("gate_satisfied") else 1)
