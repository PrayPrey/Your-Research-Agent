# Hypothesis Context: H-E1

**Generated:** 2026-04-20
**Type:** EXISTENCE
**Prerequisites:** None

## Hypothesis Statement

Under neural theorem proving with LeanDojo ReProver, if we extract confidence derivatives (std dev of softmax entropy) from the first 15 proof steps, then these derivatives correlate with eventual timeout outcomes (r > 0.3), because confidence instability reflects the model's uncertainty about unfamiliar proof states.

## Rationale

This hypothesis validates the foundational assumption that LLM confidence signals contain predictive information about proof termination. Without this correlation, the entire approach fails.

## Experimental Setup

**Dataset:** LeanDojo Benchmark (standard)
- Source: Yang et al., 2023 - 98,734 theorems from Lean math library
- Path: https://github.com/lean-dojo/LeanDojo

**Model:** LeanDojo ReProver
- Type: Retrieval-augmented LLM for theorem proving
- Source: Yang et al., 2023

## Success Criteria (PoC: Direction-based)

- Primary: Correlation coefficient r > 0.3 OR ρ > 0.3
- Secondary: Confidence derivative separates success/timeout clusters visually

## Gate Condition

**Type:** MUST_WORK
**Pass Condition:** Correlation coefficient r > 0.3 OR ρ > 0.3
**Fail Action:** STOP, reassess entire hypothesis

## Verification Protocol

1. Run 100 extended-timeout experiments (100× normal = 300s budget per theorem)
2. Extract confidence trajectories from first 15 steps via LeanDojo get_tactics()
3. Calculate std dev of softmax entropy for each theorem
4. Label outcomes as success/timeout based on 300s results
5. Compute Pearson r and Spearman ρ correlations

## Dependencies

None (Foundation hypothesis)

## Previous Context

None (First hypothesis in sequence)
