# Research Idea

## Title
Multi-Signal Surprise-Weighted Replay for Efficient LLM Training

## Motivation
Foundation model training is computationally expensive, yet current approaches treat all training samples equally despite vast differences in their informativeness. While data-centric AI research has shown that sample selection matters, existing methods either require costly post-hoc attribution or use simplistic difficulty metrics. Inspired by hippocampal memory consolidation—where the brain prioritizes surprising experiences for replay—we propose that combining multiple surprise signals can efficiently identify high-value training samples online, significantly reducing training costs without sacrificing model quality.

## Main Idea
We hypothesize that weighting sample replay probability by a multi-signal surprise score (combining normalized loss deviation with gradient magnitude) accelerates LLM training convergence by 20-40%. The core mechanism operates in three steps: (1) compute surprise scores using both loss deviation and gradient magnitude with tunable balance parameter λ, (2) prioritize high-surprise samples in a replay buffer with temporal decay, and (3) accumulate more informative gradients per training step. 

We will validate this on LLaMA-7B pretraining with C4 data, measuring time-to-target-perplexity against random sampling baselines across 15+ seeds. Success requires ≥20% efficiency gain while maintaining quality within 1%. The approach adds minimal overhead (O(1) statistics updates) while providing a principled, biologically-grounded framework for online data curation in foundation model training.