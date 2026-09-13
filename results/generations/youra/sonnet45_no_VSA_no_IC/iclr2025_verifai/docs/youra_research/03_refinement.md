# Phase 2A Hypothesis Refinement Summary

**Hypothesis ID:** H-MechanisticBaseline-v1  
**Generated:** 2026-08-20T03:33:00Z  
**Confidence:** 0.76 (6 persona consensus)  
**Status:** READY_FOR_PHASE2B_WITH_PILOTS

---

## Core Hypothesis Statement

**Under** miniF2F Olympiad-level formal mathematics benchmark (Lean 4 subset, N≥50 problems),

**IF** we compare LLM-guided theorem proving (LeanCopilot) against pure automated provers (lean-auto hammers) with controlled tactic evaluation budgets (10 evaluations/problem),

**THEN** LLM-guided approaches achieve significantly higher success rates (predicted: 65% vs 15%, Δ=50 percentage points),

**BECAUSE** LLMs exploit three distinct mechanisms:
1. **Natural language hint understanding** (60% of gap) - linguistic pattern matching from problem statements
2. **Long-range proof search capability** (30% of gap) - context maintenance across 5-10 tactic steps where hammers timeout at depth 3
3. **Mathlib corpus pattern matching** (10% of gap) - learned human proof tactic distributions

---

## Mechanistic Dissection Design

| Configuration | NL Hints | Proof Depth | Tactic Budget | Predicted Success | Falsification |
|---------------|----------|-------------|---------------|-------------------|---------------|
| **Baseline-Hammer** (lean-auto) | N/A | All | 1000* | 15% | Reference |
| **SOTA-LLM** (LeanCopilot-full) | Yes | All | 10 | 65% | Reference |
| **Ablation-NL** (no comments) | No | All | 10 | 35% | Δ<10% rejects NL claim |
| **Ablation-Depth** (≤3 tactics) | Yes | ≤3 | 10 | 50% | Δ<5% or Δ>30% rejects |
| **Control-Corpus** (Random-Mathlib) | N/A | All | 10 | 20% | <18% or >25% rejects |

\* Measured empirically @ 300s timeout, then matched to LLM evaluations

**Mechanistic Attribution:**
- If predictions hold: 15% → 20% (corpus +5%) → 35% (no NL +15%) → 50% (shallow +15%) → 65% (full)
- NL contribution: (65-35)/50 = 60%
- Depth contribution: (65-50)/50 = 30%
- Corpus contribution: (20-15)/50 = 10%

---

## Novelty Claim

**What's New:**

First work to quantitatively attribute LLM theorem proving advantage to specific mechanisms via controlled ablation study. Prior work (Thor, DeepSeek-V2, Numina-Lean-Agent) reports aggregate success rates but does NOT decompose WHY LLMs outperform automated provers.

**Comparison to SOTA:**

| Work | Contribution | Limitation | Our Advance |
|------|--------------|------------|-------------|
| Thor (2022) | 8.2% unique hybrid solutions | "39%" baseline ambiguous | Unambiguous prover-only baseline + mechanistic decomposition |
| DeepSeek-V2 (2025) | 88.9% SOTA on miniF2F | No non-LLM baseline | Baseline comparison + attribution applicable to any LLM |
| RLMEval (2025) | Research-level benchmark | No mechanistic analysis | Difficulty stratification reveals LLM-friendly vs hammer-friendly problems |

---

## Feasibility Assessment

**Infrastructure:**
- ✅ lean-auto (leanprover-community/lean-auto, 164 stars)
- ✅ LeanCopilot (lean-dojo/LeanCopilot, 1309 stars)
- ✅ miniF2F Lean 4 subset (facebookresearch/miniF2F fork)
- ✅ Lean 4 proof checker (deterministic binary validation)

**Critical Pilots (BLOCKERS for full experiment):**

1. **NL Ablation Feasibility (Gate 1 - BLOCKER):**
   - Remove NL comments from 10 problems
   - Verify Lean type-checking passes
   - Fallback: Pivot to informal Mathlib docs removal

2. **Tactic Budget Measurement (Gate 2 - BLOCKER):**
   - Run lean-auto on 20 problems @ 300s timeout
   - Measure average tactic evaluations
   - Use mean to set LLM budget (or median if CV > 50%)

3. **Metadata Availability (Optional Enhancement):**
   - Check for AMC/AIME/IMO difficulty labels
   - If present: Per-stratum analysis
   - If absent: Aggregate results only

4. **Depth Measurement Validation (Optional):**
   - Inspect 10 solved proofs
   - Confirm tactic count extraction from proof terms
   - Fallback: Use proof script length (lines) as proxy

---

## Persona Verdicts

| Persona | Icon | Verdict | Confidence | Key Concern |
|---------|------|---------|------------|-------------|
| Dr. Nova | 🔭 | SUPPORT | 0.85 | Lean 4 subset representativeness |
| Prof. Vera | 🔬 | SUPPORT | 0.80 | Pre-registration required |
| Dr. Sage | 🎯 | SUPPORT | 0.75 | Mechanistic percentages must hold |
| Prof. Pax | ⚙️ | CONDITIONAL | 0.70 | Feasibility gates MUST pass |
| Dr. Ally | 🛡️ | SUPPORT | 0.82 | Corpus bias in random sampling |
| Prof. Rex | 🔍 | CONDITIONAL | 0.72 | Pre-register before experiments |

**Consensus:** 6/6 support proceeding to Phase 2B with pilots as first tasks.

---

## Phase 2B Transition Checklist

**READY** status requires completing these tasks:

- [ ] **Verify Lean 4 Subset Size** (N≥50 for pilot study)
- [ ] **NL Ablation Pilot** (10 problems, BLOCKER)
- [ ] **Tactic Budget Baseline** (20 problems, BLOCKER)
- [ ] **Pre-Register Predictions** (document before data collection)
- [ ] **Metadata Check** (optional, enables stratification)

**If Pilots Pass:**
→ Proceed to full experiment design (Phase 2C)

**If Gate 1 Fails (NL ablation breaks type-checking):**
→ Pivot to alternative ablation (informal Mathlib docs removal)

**If Gate 2 Variance Too High (CV > 50%):**
→ Use median tactic budget instead of mean

**If Metadata Absent:**
→ Report aggregate results only, acknowledge stratification limitation

---

## Established Facts (Build On, No Re-Verification)

1. **Deterministic validation via Lean proof checker eliminates custom extraction bottleneck** (h-e1 failure was custom extraction at 49.5%)
2. **SOTA LLM-guided proving achieves 88.9% on miniF2F-test** (DeepSeek-V2, Phase 1 evidence)
3. **Thor hybrid achieves 8.2% unique solutions** (neither LLM nor prover solves alone)
4. **miniF2F provides 244 Olympiad problems with deterministic evaluation** (benchmark standard)

## Claims to Prove (Require New Experiments)

1. **Thor's "39%" baseline is ambiguous** → Establish unambiguous lean-auto baseline
2. **Pure automated prover baseline on miniF2F is unmeasured** → Measure lean-auto success rate
3. **LLM advantage is attributable to NL (60%), depth (30%), corpus (10%)** → Validate via ablation studies

---

**Next Phase:** Phase 2B - Research Planning  
**Expected Outputs:** Detailed experiment protocol, pre-registered predictions, resource allocation, Archon task breakdown
