# Phase 2A Refinement Summary

**Date:** 2026-07-09  
**Workflow:** Phase 2A-Dialogue (Recursive v2)  
**Mode:** UNATTENDED  
**Exchanges:** 14 (11 discussion + Final Assessments)  
**Status:** ✅ CONVERGED

---

## Hypothesis Generated

**ID:** H-TokenEntropy-v1 (following Phase 4 failures of h-e1 v1/v2)  
**Type:** FOUNDATIONAL MECHANISM INVESTIGATION  
**Confidence:** 0.9 (High - All 6 personas converged)

### Core Statement

"Single-pass token entropy provides deployment-equivalent uncertainty quantification to 10-sample MC Dropout on factual QA (TriviaQA) and hallucination detection (TruthfulQA), with profiler-validated 90% cost reduction and matched risk-coverage behavior, contingent on MC Dropout providing non-trivial epistemic diversity (pairwise KL ≥ 0.05)."

### Key Innovation

The hypothesis evolved from a simple "comparison study" to a **foundational investigation** of whether MC Dropout provides meaningful epistemic diversity in modern LLMs. Either outcome advances the field:
- **If KL < 0.05:** Validates single-pass sufficiency, refutes ensemble assumptions
- **If KL ≥ 0.05:** Demonstrates token entropy approximates weight-space marginalization

---

## Convergence Criteria Met

All 6 criteria satisfied:

✅ **SPECIFIC:** Clear core claim with quantitative thresholds (AUROC Δ ≤ 0.03)  
✅ **MECHANISM:** Causal explanation via predictive distribution geometry  
✅ **PREDICTIONS:** 7 preregistered predictions (P0-P6) with falsification conditions  
✅ **NOVELTY:** First to test MC Dropout epistemic diversity assumption in modern LLMs  
✅ **FEASIBILITY:** All constraints met (existing datasets, no human annotation, infrastructure robustness)  
✅ **OBJECTIONS:** All persona concerns addressed with preregistered controls

---

## Preregistered Predictions

### P0: MUST_WORK_GATE_0 (Baseline Sanity)
MSP AUROC > 0.6 on TriviaQA (multi-source average, variance < 0.02)  
**Failure → STOP:** Diagnose dataset/implementation issue

### P1: Primary Performance
Token entropy AUROC within Δ ≤ 0.03 of MC Dropout on TriviaQA (5 seeds, 95% CI)

### P2: Ambiguity Mechanism
- Inter-seed Jaccard variance correlates with correctness (partial ρ ≤ -0.3 | length)
- Shuffled variance shows ρ ≈ 0 (negative control)
- Token entropy AUROC degrades ≥0.10 from LOW_AMB to HIGH_AMB terciles

### P3: Risk-Coverage Equivalence
- Risk @90% coverage within +0.02 of MC Dropout
- High-confidence error mass not significantly higher (Fisher's p > 0.05)

### P4: Compute Efficiency
- FLOPs per token ≤ 1.15×base in HIGH_AMB tercile
- Linear scaling with answer length (slopes within 10%)

### P5: Stable Transfer
- TriviaQA → TruthfulQA AUROC degradation < 0.10
- Kendall's τ > 95th percentile of permutation null

### P6: MC Dropout Divergence Diagnostic
- Pairwise KL between MC Dropout samples measured relative to calibrated noise scale
- **If KL < 0.05:** "Negligible epistemic diversity" (null interpretation)
- **If KL ≥ 0.05:** "Token entropy approximates ensemble" (strong interpretation)

---

## Methodological Contributions

1. **Inter-seed variance as zero-cost ambiguity proxy** (validated via intrinsic entropy + correctness correlation)
2. **MC Dropout divergence diagnostic** (KL-based test for epistemic diversity in ensembles)
3. **Risk-coverage + error mass as standard evaluation** (beyond AUROC leaderboards)
4. **Profiler-validated cost reporting** (FLOPs per token, stratified by ambiguity)
5. **Stable transfer criterion** (Kendall's τ ranking consistency across tasks)

---

## Failure Lessons Incorporated (h-e1 v1/v2)

✅ **No hidden-state probes** — Output-based uncertainty only  
✅ **Baseline sanity check FIRST** — MUST_WORK_GATE_0 validates experimental apparatus  
✅ **Multi-source dataset validation** — Reproducibility via 3 independent TriviaQA loads  
✅ **Infrastructure robustness** — datasets==2.10.0 pinned, profiler validation  
✅ **Multiple uncertainty signals tested** — Token entropy + MC Dropout + MSP  
✅ **No human annotation required** — Inter-seed variance proxy computable  
✅ **Feasibility constraints respected** — Existing datasets, no synthetic data, immediate testability

---

## Persona Consensus Scores

| Persona | Score | Assessment |
|---------|-------|------------|
| 🔭 Dr. Nova | 9/10 | Novel paradigm shift achieved |
| 🔬 Prof. Vera | 9/10 | Falsification framework meets standards |
| 🎯 Dr. Sage | 9/10 | Field-shaping contribution potential |
| ⚙️ Prof. Pax | 8/10 | Feasible with validated infrastructure |
| 🛡️ Dr. Ally | 9/10 | Defensible against adversarial review |
| 🔍 Prof. Rex | 9/10 | Adversarial stress tests passed |

**Average Consensus:** 8.8/10 (Strong Agreement)

---

## Phase 2B Readiness

**✅ READY FOR PHASE 2B (Research Planning)**

**Inputs to Phase 2B:**
- `03_refinement.yaml` — Structured hypothesis with preregistered predictions
- `02_synthesis.yaml` — Methodological framework and evaluation protocol
- `01_round_table/final_opinions.yaml` — Persona assessments and concerns
- `discussion_log.md` — Complete 14-exchange Tikitaka discussion

**Next Phase Actions:**
1. Design experiment protocol (datasets, models, evaluation metrics)
2. Specify falsification criteria as acceptance criteria
3. Identify implementation resources (cvs-health/uqlm, PyTorch profiler)
4. Estimate Phase 3 complexity (5-7 Epic tasks — MEDIUM tier)
5. Plan Phase 4 validation checkpoints (MUST_WORK gates)

---

## Research Questions Opened

1. Does MC Dropout KL divergence scale with model size (7B → 13B → 70B)?
2. Does token entropy's sufficiency break under domain shift (MedQA, legal reasoning)?
3. Can we formalize conditions for predictive entropy approximating Bayesian marginalization in overparameterized transformers?
4. Do other single-pass methods (attention entropy, semantic probes) exhibit stable transfer?

---

**Phase 2A Complete — Hypothesis validated by 6-persona convergence and ready for implementation planning.**
