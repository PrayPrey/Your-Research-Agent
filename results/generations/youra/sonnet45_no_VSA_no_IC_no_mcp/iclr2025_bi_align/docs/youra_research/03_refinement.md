# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T04:12:00+00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: Gap_1
- **Gap Title**: Lack of Unified Metrics for Bidirectional Alignment Measurement
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 10

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights

1. **Paradigm Shift: Coupling vs. Sum** — Bidirectional alignment is not the SUM of AI-to-human + human-to-AI metrics, but their CORRELATION (coupling). This distinguishes multiplicative (interaction-level) from additive (model-level) alignment models.

2. **Alignment as Interaction Property** — Alignment is not a static model property ("GPT-4 is aligned") but an interaction-level property that varies by user population. Two users with different learning rates experience different alignment with the SAME model.

3. **Feasibility via Behavioral Proxies** — Shifted from infeasible MI growth (requires temporal dynamics) to behavioral coupling (reformulation slope × diversity correlation, computable on static datasets).

4. **No API Dependencies** — Addressed h-m3 failure mode by designing hypothesis executable on existing static datasets (HH-RLHF) without external API calls.

### Breakthrough Moments

- **Exchange 5 (Dr. Ally):** Pivot from entropy to behavioral adaptation signatures (reformulation rate + response diversity) resolved Prof. Pax's "frozen AI" barrier
- **Exchange 7 (Dr. Nova):** Introduction of behavioral coupling framework (correlation between user learning + AI responsiveness) vs. entropy/MI approaches
- **Exchange 9 (Prof. Pax):** Reframe from "AI adaptation" (temporal) to "AI policy responsiveness" (functional) unlocked feasibility on static data
- **Exchange 10 (Dr. Sage):** "Alignment as interaction property, not model property" elevated significance from methodological to conceptual contribution

---

## Final Hypothesis

### Title
Bidirectional Alignment via Behavioral Coupling

### Hypothesis ID
H-BiAlign-v1

### Core Claim

**Under-If-Then-Because Statement:**

Under conversational AI interactions with ≥5 turns, if we measure the coupling strength (Pearson correlation) between user learning rate (reformulation slope) and AI policy responsiveness (response diversity tracking query diversity), then conversations with higher coupling strength will have higher human helpfulness ratings, because bidirectional alignment emerges from co-adaptation where users learn AI capabilities AND AI policy exhibits responsiveness to user query patterns.

### Mechanism

Bidirectional alignment is the coupling (correlation) between two processes:

1. **User Adaptation (Human-to-AI):** Users learn AI response patterns over turns, manifesting as decreased reformulation rate (reformulation slope < 0). This is a within-conversation learning curve.

2. **AI Policy Responsiveness (AI-to-Human):** AI exhibits policy-level responsiveness where diverse user queries elicit diverse responses. Measured as correlation between query diversity (distinct-1 over query vocabulary) and response diversity (distinct-1 over response vocabulary).

3. **Coupling Mechanism:** Strong bidirectional alignment emerges when BOTH processes correlate. High coupling (Pearson r between reformulation slope and diversity correlation) indicates mutual predictability: users who learn faster interact with AI that is more responsive, creating aligned interaction dynamics. Weak coupling indicates asymmetric alignment (one-sided adaptation).

### Variables

**Independent Variable:**
- Coupling Strength (continuous, range [-1, 1]): Pearson correlation between user reformulation slope and AI diversity correlation per conversation

**Dependent Variables:**
- Human Helpfulness Rating (continuous, 0-1 scale, HH-RLHF) — PRIMARY
- Task Success Rate (binary: successful vs. abandoned conversation) — SECONDARY

**Controlled Variables:**
- Conversation Length (≥5 turns filter + turn count covariate)
- User Engagement Decay (stratify by outcome, test on successful conversations)
- Individual Metrics (reformulation slope alone, diversity correlation alone)

---

## Predictions

### P1: User Learning Predicts Task Success (PRIMARY)

**Statement:** Conversations with negative reformulation slope (user learning) have higher task success rates than flat/positive slope conversations, controlling for conversation length and engagement

**Test Method:** Logistic regression: `success ~ reformulation_slope + turn_count`, on successful conversations only (stratified by outcome to control engagement decay)

**Success Criterion:** Negative coefficient for reformulation_slope, p < 0.05, OR > 1.2 (12% increase in success odds per 0.1 decrease in slope)

**Falsification:** Coefficient NOT negative OR p ≥ 0.05 → reformulation slope does not measure learning

### P2: AI Responsiveness (Query-Response Diversity Correlation)

**Statement:** AI response diversity correlates with user query diversity (Pearson r > 0.4) in well-aligned conversations

**Test Method:** Compute query diversity (distinct-1 over query vocabulary) and response diversity (distinct-1 over response vocabulary) per conversation. Pearson correlation on conversations rated helpfulness > median.

**Success Criterion:** r > 0.4 AND p < 0.05

**Falsification:** r ≤ 0.4 OR p ≥ 0.05 → AI policy not responsive to query diversity

### P3: Coupling Matters Beyond Individual Metrics (PRIMARY)

**Statement:** Conversations where BOTH P1+P2 hold have higher helpfulness ratings than conversations where only one holds, demonstrating coupling matters beyond individual metrics

**Test Method:** Linear regression: `helpfulness ~ coupling_strength + reformulation_slope + diversity_correlation + turn_count`. Coupling_strength = Pearson(reformulation_slope, diversity_correlation). Test coupling coefficient significance.

**Success Criterion:** Positive coefficient for coupling_strength, p < 0.05, controlling for individual metrics → coupling predicts beyond components

**Falsification:** Coupling coefficient NOT significant when controlling for individual metrics → alignment is additive, not multiplicative

---

## Novelty

### Preserved Novelty
Bidirectional alignment as interaction-level coupling (correlation), not model-level property. First framework measuring co-adaptation (user learning × AI responsiveness) rather than summing individual metrics.

### Key Innovation
Coupling metric detects asymmetric alignment failures (e.g., responsive AI but users not learning, or users adapting but AI not responsive). Enables user-population-specific evaluation and deployment-time monitoring without new human studies.

### Differentiation from Prior Work

| Prior Work | Difference |
|------------|------------|
| RLHF (Ouyang et al. 2022) — AI-to-human only | We measure BOTH user-to-AI (reformulation) AND AI-to-user (diversity), test COUPLING as distinct mechanism |
| Interpretability metrics — human-to-AI in isolation | We measure bidirectional coupling, not isolated metrics. Coupling hypothesis: alignment is multiplicative (correlation), not additive (sum) |
| Bansal et al. 2021 (user mental models) — explicit predictions | We infer mental model accuracy from behavioral trace (reformulation slope), measurable on existing logs without explicit prediction tasks |

---

## Experimental Design

### Dataset
**HH-RLHF** (Anthropic Helpful-Harmless RLHF Dataset)
- 161k human-AI conversations with helpfulness ratings
- Multi-turn structure (filter ≥5 turns for slope estimation)
- Conversation metadata (outcome, length)

### Baselines
1. **Individual Metrics Only:** `helpfulness ~ reformulation_slope + diversity_correlation` (no coupling term)
2. **Conversation Length Only:** `helpfulness ~ turn_count`
3. **Random Baseline:** Permute helpfulness ratings, verify coupling correlation not spurious

### Measurement Plan

1. Extract user queries and AI responses per conversation
2. Compute reformulation rate: SBERT similarity + edit distance (high semantic + low syntactic = reformulation)
3. Compute reformulation slope: linear regression of reformulation rate over turn index
4. Compute query diversity: distinct-1 over query vocabulary
5. Compute response diversity: distinct-1 over response vocabulary
6. Compute diversity correlation: Pearson r between query diversity and response diversity
7. Compute coupling strength: Pearson r between reformulation slope and diversity correlation
8. Test P1, P2, P3 via regression analyses

---

## Limitations

### Known Limitations

1. **Short Conversations:** HH-RLHF median length ~3 turns. Even with ≥5-turn filter, slope estimation has weak statistical power. Mitigation: test on longer datasets (Anthropic logs), use Bayesian slope estimation.

2. **Reformulation Detection Ambiguity:** High SBERT similarity could be topic continuity, not reformulation. Mitigation: dual detection (semantic + syntactic — true reformulation has high semantic + low syntactic similarity).

3. **Threshold Sensitivity:** P2's correlation threshold (0.4) and P1's slope threshold (negative) affect outcomes. Mitigation: sensitivity analysis across ranges (0.3-0.5 for r, -0.05 to -0.2 for slope).

4. **Observational Study:** No causal intervention (correlation, not causation). Coupling correlation supports hypothesis but doesn't prove causality.

### Scope Boundaries

**Applies To:**
- Conversational AI interactions ≥5 turns
- Task-oriented or open-ended dialogue
- Datasets: HH-RLHF, Anthropic logs, OpenAI API logs

**Does NOT Apply To:**
- Single-turn Q&A (no learning curve)
- Non-conversational tasks (classification, translation)
- Conversations <5 turns (insufficient slope data)
- Synthetic/simulated conversations (may not exhibit natural learning)

---

## Key Assumptions

1. **A1 (Reformulation = Learning):** Reformulation rate decrease indicates user learning, not engagement decay. Testable by stratifying on outcome (test P1 on successful conversations only).

2. **A2 (Paraphrase Detection Validity):** SBERT + edit distance reliably detects reformulations vs. topic continuity. Dual detection (semantic + syntactic) controls confound.

3. **A3 (Diversity = Responsiveness):** Response diversity (distinct-n) captures AI policy responsiveness to query diversity. Conditioned on query diversity, isolates responsiveness.

4. **A4 (Statistical Power):** HH-RLHF conversations ≥5 turns have sufficient power for slope estimation. Bayesian estimation + sensitivity analysis mitigate weak power.

5. **A5 (Threshold Validity):** Pearson threshold (0.4) is meaningful, not arbitrary. Sensitivity analysis (0.3-0.5 range) validates robustness.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |
| **Phase 2B Readiness** | READY |

---

## Phase 2B Handoff Notes

**Existence Claims (SH1):**
- User reformulation rate must decrease over turns in successful conversations (learning curve)
- AI response diversity must correlate with query diversity (responsiveness)
- Both measurable on HH-RLHF ≥5-turn conversations

**Mechanism Claims (SH2):**
- Coupling between user learning rate and AI responsiveness
- Test via P3: coupling coefficient significant when controlling for individual metrics

**Comparison Claims (SH3):**
- Compare coupling metric to individual metrics (reformulation slope alone, diversity correlation alone)
- Compare to trivial baseline (conversation length)
- Hypothesis: coupling predicts helpfulness BEYOND components

**Open Questions for Phase 2B:**
- What coupling strength threshold constitutes "good" alignment? (Empirical calibration needed)
- Do coupling patterns generalize across model families (GPT vs. Claude vs. Llama)?
- Can coupling metric predict alignment degradation in deployed systems over time?

---

*Generated by Phase 2A-Dialogue (Self-Contained Tikitaka Loop, Independent-Controller Ablation)*
*Hypothesis ID: H-BiAlign-v1*
*Confidence: 0.85*
