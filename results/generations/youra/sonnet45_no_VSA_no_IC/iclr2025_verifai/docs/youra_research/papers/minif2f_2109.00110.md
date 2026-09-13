# MiniF2F: a cross-system benchmark for formal Olympiad-level mathematics

**arXiv ID:** 2109.00110  
**Authors:** Zheng, K., Han, J. M., Polu, S.  
**Year:** 2021  
**Citations:** 441

## Key Contributions

- **Benchmark Standard:** 488 Olympiad-level problems (244 test set)
- **Multi-System:** Supports Metamath, Lean, Isabelle, HOL Light
- **Unified Evaluation:** Establishes standardized protocol for neural theorem proving evaluation
- **Deterministic Validation:** All systems use proof checkers for binary correctness (valid/invalid)

## Relevance to Research Question

Establishes the primary benchmark (miniF2F-test) for evaluating LLM-guided theorem proving approaches. Confirms deterministic validation approach via proof checkers (eliminates custom extraction bottleneck).

**Critical Gap:** Benchmark paper does not report pure automated prover (no LLM) baseline success rates - only establishes evaluation protocol.
