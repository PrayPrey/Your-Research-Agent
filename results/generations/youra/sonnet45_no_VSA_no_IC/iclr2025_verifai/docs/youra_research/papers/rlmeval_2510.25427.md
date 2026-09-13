# RLMEval: Evaluating Research-Level Neural Theorem Proving

**arXiv ID:** 2510.25427  
**Authors:** Poiroux, A., Bosselut, A., Kuncak, V.  
**Year:** 2025  
**Citations:** 6

## Key Contributions

- **Research-Level Benchmark:** 613 theorems from 6 real Lean projects (much harder than miniF2F)
- **Performance Baseline:** 10.3% pass rate on research-level problems (vs 88.9% on miniF2F-test)
- **Realistic Evaluation:** Tests neural theorem proving on actual research mathematics, not curated problems
- **Validation:** Uses Lean proof checker for deterministic correctness validation

## Relevance to Research Question

Provides context for difficulty scaling - miniF2F success rates (56-89%) represent curated Olympiad problems, while research-level mathematics remains challenging (10.3% pass rate). Confirms deterministic validation via proof checkers.

**Critical Gap:** Like other papers, reports LLM-guided success rates but not pure automated prover baseline for comparison.
