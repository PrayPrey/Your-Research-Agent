# Phase 2A Extended: Hypothesis Summary (Phase 2B Input)

**Date:** 2026-02-06
**Hypothesis ID:** H-ZPD-AI-2026-01
**Confidence:** 85%
**Status:** Ready for Phase 2B Verification Planning

---

## Core Hypothesis

**IF** an AI collaboration system dynamically adjusts its agency level (Tutor ↔ Peer) based on real-time Zone of Proximal Development (ZPD) assessment **THEN** learning outcomes across diverse competency levels will improve by 10-15% compared to fixed-role AI systems **BECAUSE** ZPD-calibrated scaffolding optimizes the match between learner competency and support intensity, preventing both over-scaffolding (reduced autonomy) and under-scaffolding (cognitive overload).

---

## Key Variables

| Variable | Type | Operationalization |
|----------|------|-------------------|
| AI Agency Level | Independent | Binary: Tutor mode (high scaffolding) vs. Peer mode (collaborative). Threshold: P(mastery) > 0.6 → Peer |
| Student Competency | Independent | Deep Knowledge Tracing probability: P(mastery\|interaction_history), range 0.0-1.0 |
| Learning Outcomes | Dependent (primary) | Composite: (1) Knowledge retention (pre/post Δ), (2) Transfer accuracy, (3) Time to mastery |
| Learner Autonomy | Dependent (secondary) | Self-Regulated Learning score: MAI + behavioral metrics |

---

## Causal Mechanism (First Principles)

**Fundamental Causal Chain:**
1. **DKT Continuous Assessment** → Real-time P(mastery) updates after each dialogue turn
2. **ZPD Binary Classification** → P > 0.6 = Peer mode; P ≤ 0.6 = Tutor mode
3. **Role-Switching** → AI transitions between high scaffolding (Tutor) and collaborative (Peer)
4. **Cognitive Load Optimization** → Scaffolding matches competency, preventing overload/underload
5. **Dual Outcomes:**
   - **Pathway A:** Optimized load → faster acquisition → reduced time to mastery
   - **Pathway B:** Graduated support → increased autonomy → enhanced metacognition → better transfer

**Key Tension:** Dynamic adaptation benefits assume (1) low transition costs, (2) ≥70% DKT accuracy, (3) consistent LLM personas. If violated, overhead may negate gains.

---

## Testable Predictions

**Primary:** ZPD-AI > best fixed-role baseline by 10-15% (p < 0.05, d ≥ 0.4)

**Secondary:**
1. **Low competency students:** ZPD-AI ≈ Always-Tutor, but +25-35% vs. Always-Peer
2. **High competency students:** ZPD-AI ≈ Always-Peer, but +20-30% vs. Always-Tutor
3. **Autonomy:** SRL score +20-30% vs. fixed roles (for students with ≥3 transitions)
4. **Transfer:** Novel problem accuracy +15-25% vs. fixed roles

**Falsification:** If ZPD-AI ≤ 5% gain vs. best baseline, or >10% worse for any subgroup, or no autonomy benefit → hypothesis rejected.

---

## Key Assumptions

1. DKT accuracy ≥70% for dialogue-based assessment (Piech et al. 2015: 75-85%)
2. Binary ZPD sufficient for Phase 1 MVP (Phase 2: continuous spectrum)
3. LLM persona consistency via prompt engineering (requires pilot validation)
4. Students adapt to dynamic AI behavior without confusion (UI indicators planned)
5. Mathematics domain suitable for DKT (established knowledge components)
6. 10-session window sufficient for observable effects

---

## Contributions

**Theoretical:** First computational operationalization of Vygotsky's ZPD for AI role-switching; bridges 45-year gap between pedagogy theory and AI systems; extends Yan's APCP framework with implementation methodology

**Methodological:** ZPD-driven role-switching algorithm; DKT adaptation for dialogue assessment; prompt engineering framework for pedagogical personas; phased validation (2-level MVP → 4-level expansion)

**Practical:** Addresses over-reliance (advanced learners) and under-support (struggling learners); deployment via Khan Academy, Coursera, Duolingo; educator transparency dashboard; open-source implementation planned

---

## Statistical Design

**RCT Design:** N=200 (80/condition after attrition), α=0.05, Power=0.80, d=0.4

**Conditions:**
1. ZPD-AI (dynamic Tutor↔Peer)
2. Always-Tutor (high scaffolding)
3. Always-Peer (collaborative)

**Stratification:** Prior math achievement (low/medium/high tertiles)

**Primary Analysis:** One-way ANOVA + planned contrasts

**Validation:** Pilot (N=30 Wizard-of-Oz) → Main RCT (N=200) → Subgroup analysis

---

## Sub-Hypothesis Preview (Phase 2B)

**SH1 (Existence):** DKT achieves ≥70% accuracy for ZPD classification
- **Verify:** Correlation with ground-truth tests (r ≥ 0.70), binary accuracy ≥75%

**SH2 (Mechanism):** ZPD-matched scaffolding optimizes cognitive load
- **Verify:** Cognitive load surveys + behavioral indicators, matched conditions 15-20% better

**SH3 (Comparison):** Dynamic > Fixed by 10-15%
- **Verify:** RCT composite outcomes, p < 0.05, d ≥ 0.4

---

## Key Sources

1. **Yan (2025):** APCP 4-level framework - theoretical foundation [Extension]
2. **Piech et al. (2015):** Deep Knowledge Tracing - competency assessment [Methodology]
3. **Chounta et al. (2017):** Computational ZPD model - feasibility validation [Foundation]
4. **Al-Hamadi & Yousif (2025):** AI-ZPD integration - empirical support [Inspiration]
5. **Córdova-Esparza (2025):** Hybrid > autonomous - graduated autonomy evidence [Foundation]
6. **Vygotsky (1978):** ZPD theory - core pedagogical principle [Foundation]

---

## Scope & Limitations

**Applies:** Structured domains (math, programming), 1-on-1 dialogue, ages 14-18, supplemental tutoring

**Does NOT Apply:** Ill-structured domains (creative writing), group learning, children <12, physical skills

**Limitations:** Binary classification (Phase 1), single-domain validation (math), platform integration required, cold-start problem (first 2-3 sessions)

---

## Readiness Status

✅ **READY FOR PHASE 2B VERIFICATION PLANNING**

- [x] If-Then-Because structure complete
- [x] Variables operationalized
- [x] Causal mechanism decomposed (First Principles)
- [x] Assumptions explicit with evidence
- [x] Falsification criteria defined
- [x] Related work mapped (13 sources)
- [x] Statistical design specified
- [x] Sub-hypotheses previewed

---

**Full Documentation:** See `02a_extended_hypothesis_full.md` for complete analysis (13 sections, evidence tables, detailed methodology)

**Next Phase:** Phase 2B - Verification Planning (decompose into detailed sub-hypotheses with experiment designs)

---

*Generated: 2026-02-06 via /phase2a-extended (YOLO MODE)*
*Source: 02a_round_1_discussion.md (Round 1 FEASIBLE)*
