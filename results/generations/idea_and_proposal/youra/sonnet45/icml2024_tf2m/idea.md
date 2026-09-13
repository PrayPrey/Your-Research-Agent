# Research Idea: Algorithmic Fairness in RLHF Alignment

## Title
Algorithmic Process Fairness in RLHF: Addressing Hidden Discrimination Through In-Context Algorithm Selection

## Motivation
Current RLHF alignment methods optimize only output-level fairness metrics (demographic parity, equalized odds), missing a critical dimension: algorithmic process fairness. Recent theory shows transformers implement different algorithms during in-context learning (ridge, Lasso, least squares) based on prompts. If demographic groups have distinct algorithmic preferences—conservative/hedging versus decisive/sparse reasoning—standard RLHF creates hidden discrimination by penalizing certain reasoning styles while appearing fair at the output level. This gap threatens responsible AI deployment in high-stakes domains like healthcare and finance where reasoning transparency matters.

## Main Idea
We hypothesize that output-only RLHF creates systematic algorithmic unfairness across demographic groups even when output metrics appear fair. Our core mechanism: different groups exhibit distinct algorithmic preferences (conservative→ridge, decisive→Lasso) that couple with prompt patterns, triggering different in-context algorithms. Standard RLHF's output-only optimization systematically penalizes minority algorithmic preferences—a fairness violation invisible to existing metrics.

We propose algorithm-aware RLHF extending MaxMin-RLHF with an algorithmic fairness term using social choice axioms (proportional veto, non-dictatorship). Methodology involves: (1) validating algorithmic preference diversity across groups (N=500 survey), (2) detecting ICL algorithms via probing classifiers (>75% accuracy target), (3) A/B testing algorithm-aware versus standard RLHF. Expected outcome: ≥30% reduction in algorithmic unfairness while maintaining output fairness (<5% regression), establishing algorithmic process as an independent fairness dimension in LLM alignment.