# Per-Hypothesis Context: H-M1

**Generated:** 2026-08-26 (JIT by Phase 2C step-01 from 02b_verification_plan.md)
**Source:** docs/youra_research/02b_verification_plan.md — Section 2.2

---

## Hypothesis Info

- **ID:** H-M1
- **Type:** MECHANISM
- **Gate:** MUST_WORK
- **Prerequisites:** H-E1 (VALIDATED, PASS)

**Statement:** Under RLHF optimization on the same model family (Coste et al. 2023), if KL budget increases from 0 to high optimization pressure (~10 nats), then the RM score increases monotonically while gold human preference rate peaks (at intermediate KL) and reverses, because the reward model is trained to maximize a proxy that diverges from actual human judgment under sustained optimization.

**Rationale:** Tests the first causal step — whether proxy-gold decoupling empirically occurs in the digitized data. Established by Coste et al. but must be confirmed in our digitized version to ensure data fidelity for subsequent regression analysis.

---

## Variables

- **Independent:** KL budget (continuous, 0 to ~10 nats)
- **Dependent:** RM score trajectory (monotone?), gold preference trajectory (peak-reversal?)
- **Controlled:** Model family (Coste et al. same pretrained LLM), evaluation task domain

---

## Experimental Setup (from Phase 2A via Phase 2B Section 2.2)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Coste et al. 2023 figure data (digitized), Gao et al. 2023 (preliminary check) | Only published datasets providing paired (KL, RM_score, gold_preference) at ≥5 KL levels for same model family |
| **Model** | No model training — statistical re-analysis of published experimental results | Experiment is verification of digitized figure data, not training reproduction |

**Dataset Details:**
- **Source 1 (Primary):** Published figures from arXiv:2310.02743 (Coste et al. 2023), Figures 3–4; digitized using WebPlotDigitizer
- **Source 2 (Secondary):** Published figures from arXiv:2210.10760 (Gao et al. 2023), Figure 2; preliminary pattern check
- **Variables:** `kl_budget` (nats), `rm_score` (normalized), `gold_preference` (fraction)
- **Dataset Type:** real published experimental data extracted via figure digitization

**Model Details:**
- No neural model. "Baseline" = KL=0 measurement from Coste et al. CSV (leftmost point).

---

## Verification Protocol

1. Digitize Coste et al. 2023 Fig 3/4 using WebPlotDigitizer → export CSV with columns (kl_budget, rm_score, gold_preference)
2. Perform dual digitization (two independent passes per figure); use mean; report ±σ per point
3. Confirm Spearman ρ(kl_budget, rm_score) > 0.8 (monotone RM increase)
4. Identify peak KL for gold_preference (np.argmax); confirm gold[peak] > gold[final] (reversal)
5. Compute preliminary divergence: rm_score[-1] − gold_preference[-1]
6. Run preliminary pattern check on Gao et al. data (same structure)

---

## Success Criteria (PoC: Direction-based)

- **Primary:** `rho_rm_kl > 0.8` AND `reversal_confirmed == True` in Coste et al. digitized data
- **Secondary:** `divergence_final > 0` AND `peak_kl` in [3, 7] nats (consistent with paper figure)

---

## Failure Response

- `rho ≤ 0.8`: Re-digitize Fig 3 independently; compare visual trend
- `reversal_confirmed == False`: Check if wrong figure; may indicate digitization error — EXPLORE
- Confirmed no reversal: PIVOT — request raw data from authors (Open Question Q1 from Phase 2B)

---

## Baseline & Comparison Targets

| Method | Performance | Dataset | Role |
|--------|-------------|---------|------|
| KL=0 measurement (pre-RLHF baseline) | RM score and gold preference at KL=0 | Coste et al. 2023 Fig 3 leftmost point | Reference level for trajectory analysis |

---

## Dependencies and Gate Conditions

- **Prerequisites:** H-E1 (VALIDATED, PASS) — both curves confirmed present, ≥5 KL levels, digitization feasible
- **Gate Type:** MUST_WORK
- **Pass Condition:** Spearman ρ > 0.8 for RM monotonicity AND reversal_confirmed == True
- **Fail Action:** EXPLORE digitization; PIVOT to raw data request if confirmed no reversal
- **Downstream:** H-M2, H-M3, H-M4 all depend on this
