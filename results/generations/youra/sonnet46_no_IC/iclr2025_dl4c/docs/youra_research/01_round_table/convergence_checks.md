# Phase 2A Convergence Checks (Self-Judged — IC-Ablation)
## Architecture: Claude Self-Play Loop (no external orchestrator)

---

## Convergence Check @ Exchange 15

**Date:** 2026-08-04
**Exchange Count:** 15 (min_exchanges = 15 from phase2a_config.yaml)
**All Personas Spoke:** YES

| Criterion | Verdict | Evidence (Exchange #) |
|-----------|---------|----------------------|
| SPECIFIC | PASS | Exchanges 11, 14: "exec-filtered SFT from The Stack Python outperforms unfiltered SFT at equal token budget on HumanEval + MBPP with Qwen2.5-Coder-1.5B/7B" |
| MECHANISM | PASS | Exchanges 11, 12, 15: Four-step causal chain (filtration → noise reduction/alignment → benchmark improvement); mechanism-agnostic framing; P3 stratum check |
| PREDICTIONS | PASS | Exchanges 8, 14: P1 (≥2pp HumanEval, p<0.05), P2 (ordering), P3 (stratum check within 1pp), each with explicit falsification |
| NOVELTY | PASS | Exchanges 4, 10, 14: No prior work applies exec filtering to raw corpus SFT at equal token budget with compile vs. doctest comparison confirmed by Phase 1 research |
| FEASIBILITY | PASS | Exchanges 3, 9, 15: All conditions in-process (compile(), doctest), token budget feasibility at 5% prevalence confirmed, standard eval stack |
| OBJECTIONS | PASS | Exchanges 6, 12, 14: exec() concern (doctest solution), mechanism commitment (agnostic framing), corpus confound (P3), survivorship bias (scoped) |

**All personas participated:**
- Dr. Nova: Exchanges 1, 7, 13
- Prof. Vera: Exchanges 2, 8, 14
- Prof. Pax: Exchanges 3, 9, 15
- Dr. Sage: Exchanges 4, 10
- Dr. Ally: Exchanges 5, 11
- Prof. Rex: Exchanges 6, 12

**Verdict: CONVERGED**
**Convergence Type:** Natural convergence at minimum threshold
