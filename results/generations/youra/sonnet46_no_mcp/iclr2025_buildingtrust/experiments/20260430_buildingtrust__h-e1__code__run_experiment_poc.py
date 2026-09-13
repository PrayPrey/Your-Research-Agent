"""
Phase 4 PoC Experiment Runner for H-E1.

Runs the REAL lm-evaluation-harness pipeline on 30 open-weight instruction-tuned
LLMs, assembles the N×8 score matrix from real benchmark results, and executes
the full statistical analysis: partial Spearman ρ, BCa bootstrap CIs, factor
analysis, Tucker congruence, LOO logistic regression, gate evaluation, visualization,
and report generation.

This replaces the previous synthetic-data PoC — all data now comes from real
HuggingFace benchmarks via lm-evaluation-harness.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

import main as pipeline


if __name__ == "__main__":
    logger.info("=== H-E1 PoC Experiment (Real Data via lm-evaluation-harness) ===")
    gate_eval = pipeline.main()
    sys.exit(0 if gate_eval["PASS"] else 1)
