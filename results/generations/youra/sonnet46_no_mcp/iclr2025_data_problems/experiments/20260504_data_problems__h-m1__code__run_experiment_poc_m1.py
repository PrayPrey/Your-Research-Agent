#!/usr/bin/env python3
"""
H-M1 PoC Experiment Runner
===========================
Builds the 59x3 contamination matrix (59 benchmark sub-tasks x 3 corpora:
The Pile v1, C4 en.noclean, RedPajama-v1) using REAL HuggingFace datasets
via MinHash LSH streaming indices.

Delegates entirely to run_experiment.py which uses the real pipeline:
  DataLoader → CorpusIndexer (HF streaming) → MatrixBuilder → StatsAnalyzer

Gate: Kruskal-Wallis p < 0.05 for contamination variance across 3 corpora.
Secondary: at least one corpus pair mean diff > 2 pp.
"""
import sys
import os

# Ensure code directory is on the path
HERE = __file__
sys.path.insert(0, os.path.dirname(os.path.abspath(HERE)))

from run_experiment import main

if __name__ == "__main__":
    main()
