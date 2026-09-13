# Reflection Report — h-m3
**Generated:** 2026-03-15T05:00:00Z
**Step:** 06b-reflection
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL
**Reflection Outcome:** LIMITATION_RECORDED

---

## 1. Experiment Summary

**Hypothesis h-m3:** The dominant alignment-induced logit perturbation mechanism is H1 (monotonic scale distortion): Spearman rank correlation between base and aligned 4-option log-prob vectors is ≥0.9, and Brier reliability increase is concentrated in shared-argmax items (confidence inflation, not accuracy collapse).

**What was tested:**
- Spearman ρ per-item between base and aligned log-prob vectors (9 model-alignment pairs)
- Argmax partition: shared-argmax vs changed-argmax Brier reliability subsets
- TruthfulQA MC1 ECE (H3 diagnostic)

---

## 2. Key Findings

### What Succeeded
- Full experiment pipeline executed successfully
- 5 figures generated
- experiment_results.json and 04_validation.md produced
- H3 diagnostic (framing susceptibility) cleanly ruled out: TruthfulQA ECE increase < MMLU ECE increase for all alignments
- 6.9b-DPO shows the highest rho (0.8748) — nearest to H1 boundary, suggesting soft DPO partially preserves rank order

### What Failed (Gate Criteria)
- **H1 not confirmed:** 0/9 Spearman rho ≥ 0.90 threshold
  - max_rho = 0.8748 (6.9b-dpo) — below 0.90 gate
  - 1.4b-ppo: rho = -0.3241 (catastrophic rank reversal)
- **H2 (boundary shift) is dominant:** 8/9 pairs flag H2 (rho < 0.85)
  - PPO causes catastrophic argmax redistribution: 1.4b-ppo changes argmax for 99.7% of items
  - Brier reliability increase NOT concentrated in shared-argmax items

### Root Cause Analysis
The H1 hypothesis assumed alignment introduces monotonic scale inflation (confidence up, rank preserved). The data clearly refutes this:

1. **PPO induces catastrophic boundary restructuring** — logit rank orders invert dramatically (rho < 0 for 1.4b-ppo). This is H2 (decision boundary shift), not H1 (scale distortion).
2. **DPO partially preserves rank** (0.74–0.87 rho range) but still fails the ≥0.90 H1 gate.
3. **SFT shows moderate boundary disruption** (0.72–0.84 rho range) — between H1 and H2 behavior.
4. The argmax partition confirms H2: majority of Brier reliability increase occurs in changed-argmax (boundary-shift) items, not shared-argmax (confidence-inflation) items.

### Key Insight
H2 is the dominant mechanism across the Pythia alignment ladder. The prior H-M2 finding that alignment inflates logit margins (confidence) is consistent with H2 (boundary shift causes both accuracy changes AND margin inflation simultaneously). The research framing should pivot from "confidence inflation" to "decision boundary restructuring."

---

## 3. Reflection Decision

**Decision:** LIMITATION_RECORDED

**Rationale:** This is a SHOULD_WORK gate with gate_result=FAIL and reflection_type=null (first occurrence, no prior self-recovery attempts). The failure represents a genuine scientific finding: the tested H1 mechanism is definitively not the dominant explanation. The experimental evidence strongly supports H2 as the dominant mechanism.

- No modification path can change the fundamental scientific result
- The data is high quality and the code ran correctly
- H2 dominance is a scientifically meaningful finding — valuable for h-m4 and paper writing
- SHOULD_WORK failures do not route to Phase 0 or Phase 2A-Dialogue

**Pipeline continues to h-m4** with this limitation recorded.

---

## 4. Lessons Learned

1. **Alignment method matters more than scale:** PPO and DPO cause qualitatively different logit restructuring (H2), not just quantitative scale inflation (H1).
2. **H1 and H2 are not just threshold differences** — PPO induces genuine rank inversion (rho < 0), which is categorically H2 behavior.
3. **6.9b-DPO as boundary case:** With rho=0.875, soft DPO barely misses H1 threshold, suggesting H1 may hold for weaker alignment methods at larger scales.
4. **H3 cleanly ruled out:** TruthfulQA ECE diagnostic confirms framing susceptibility is not a primary mechanism.
5. **For h-m4:** ATS post-hoc correction should be evaluated against H2-dominated models (expect different correction efficiency for boundary-shift vs scale-inflation scenarios).

---

## 5. State Updates

| Field | Value |
|-------|-------|
| `reflection_outcome` | LIMITATION_RECORDED |
| `should_work_failed` | true |
| `limitation_note` | h-m3 SHOULD_WORK FAIL — H2 dominant, H1 not confirmed |
| `route_to` | null (continue to h-m4) |
| `new_hypothesis_id` | null |

---

## 6. Impact on Dependent Hypotheses

**h-m4** (prerequisite: h-m3):
- h-m4 tests ATS post-hoc correction reduces ECE by ≥50% for aligned models
- h-m3's finding that H2 is dominant (not H1) is scientifically relevant context for h-m4
- h-m4 status: NOT_STARTED → proceeds normally (LIMITATION_RECORDED does not block dependents)

---

## 7. Serena Memory

**Memory type:** LIMITATION
**Record:** h-m3 SHOULD_WORK FAIL — H1 (scale distortion) mechanism not confirmed. H2 (boundary shift) is dominant with 8/9 Spearman rho < 0.85. PPO causes catastrophic argmax redistribution (rho=-0.324 for 1.4b). H3 cleanly ruled out. Limitation recorded, pipeline continues.

---

*Reflection completed at 2026-03-15T05:00:00Z by step-06b-reflection v3.8.1*
