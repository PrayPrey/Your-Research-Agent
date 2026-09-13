# Per-Hypothesis Context: H-E1

**Generated:** 2026-08-26 (JIT by Phase 2C step-01 from 02b_verification_plan.md)
**Source:** docs/youra_research/02b_verification_plan.md — Section 2.2

---

## Hypothesis Info

- **ID:** H-E1
- **Type:** EXISTENCE
- **Gate:** MUST_WORK
- **Prerequisites:** None (foundation)

**Statement:** Under published RLHF experimental settings (Coste et al. 2023, Gao et al. 2023), if the experimental design tracks both reward model (RM) score and held-out gold human preference across varying KL budget levels for the same model family, then both signals co-exist as separable time-series in the same dataset, because the experimental protocols report both proxy and gold metrics at each KL checkpoint.

**Rationale:** Validates the foundational data infrastructure for the main hypothesis. Without confirmed co-existence of both directional signals in the same experiment, the divergence curve cannot be computed and all downstream H-M hypotheses are moot.

---

## Variables

- **Independent:** RLHF Optimization Pressure (KL budget)
- **Dependent:** RM score series + gold preference rate series (both must be present)
- **Controlled:** Same model family, same evaluation protocol across KL levels

---

## Experimental Setup (from Phase 2A via Phase 2B Section 1.3)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Coste et al. 2023 + Gao et al. 2023 figure data (digitized) (standard) | Only published datasets providing both AI→Human proxy (RM score) and Human→AI-adjacent signal (gold preference) at varying optimization pressure for same model family |
| **Model** | Reward model + base LLM (as used in Coste et al. / Gao et al.) | Re-analysis of published experimental results — no new model training required |

**Dataset Details:**
- **Source 1:** Published figures from arXiv:2310.02743 (Coste et al. 2023); digitized using WebPlotDigitizer
- **Source 2:** Published figures from arXiv:2210.10760 (Gao et al. 2023); digitized using WebPlotDigitizer
- **Path:** Available from published papers; raw data may be available in author GitHub repos
- **Dataset Type:** standard (digitized from published figures)

**Model Details:**
- Type: Autoregressive language model with RLHF fine-tuning
- Source: Described in Coste et al. 2023 and Gao et al. 2023

---

## Verification Protocol

1. Access Coste et al. 2023 (arXiv 2310.02743) figures/data
2. Confirm both RM score and gold preference curves are reported at ≥5 KL levels
3. Access Gao et al. 2023 (arXiv 2210.10760) figures/data; confirm same structure
4. Apply WebPlotDigitizer to extract numerical values from both curves in both papers
5. Confirm digitized data has ≥5 paired (KL, RM_score, gold_preference) observations per paper

---

## Success Criteria (PoC: Direction-based)

- **Primary:** Both RM score and gold preference curves present in ≥2 independent datasets with ≥5 KL levels each
- **Secondary:** Digitized data precision within ±5% visual inspection estimate

---

## Failure Response

- IF fails: PIVOT — contact authors for raw data; if unavailable, document as fundamental data availability limitation and reassess scope

---

## Baseline & Comparison Targets

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Standard RLHF evaluation (RM score only) | High RM scores correlate with human preference at low KL; diverge at high KL | Coste et al. 2023 | Only measures AI→Human proxy; misses calibration degradation signal |

---

## Dependencies and Gate Conditions

- **Prerequisites:** None (this is the foundation)
- **Gate Type:** MUST_WORK
- **Pass Condition:** Both RM + gold preference data present ≥2 datasets, ≥5 KL levels each
- **Fail Action:** STOP — contact authors for raw data, reassess scope
- **Downstream:** H-M1, H-M2, H-M3, H-M4 all depend on this
