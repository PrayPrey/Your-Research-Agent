# Risk Analysis
Generated: 2026-08-19
Source: Phase 2B Planning

## Technical Risks

### R1: Sample Size Inadequacy (MEDIUM)
**Risk:** 500 instances insufficient for detecting phi = 0.3 coupling at 80% power.

**Likelihood:** MEDIUM (40%)
**Impact:** HIGH (blocks H-E1 MUST_WORK)

**Mitigation:**
- Power analysis completed: 500 × 20% failure rate = 100 failures/dimension
- Expected overlap: ≥25 co-failures for phi = 0.3 detection
- Contingency: Increase to 1000 instances if initial power analysis incorrect

**Residual Risk:** LOW

---

### R2: Difficulty Proxy Validity (HIGH)
**Risk:** Model confidence scores do NOT validly proxy instance difficulty.

**Likelihood:** HIGH (60%)
**Impact:** HIGH (H-M1 MUST_WORK invalid)

**Mitigation:**
- Primary: Use confidence-based partial correlation
- Secondary: Difficulty-stratified analysis (within-quartile coupling)
- Validation: Compare with human difficulty ratings if available
- Qualitative check: High-coupling instances should show shared semantic features

**Residual Risk:** MEDIUM (Prof. Vera's concern unresolved)

**Escalation:** If partial correlation AND stratified analysis both fail, route to Phase 2A-Dialogue (mechanism revision needed)

---

### R3: MMTrustEval Framework Limitations (MEDIUM)
**Risk:** Framework instances do NOT cover full trustworthiness landscape.

**Likelihood:** MEDIUM (50%)
**Impact:** MEDIUM (generalization limited)

**Mitigation:**
- Scope claim correctly: "coupling patterns in MMTrustEval instances" (not "all LLM trustworthiness")
- Phase 2 extension: Cross-benchmark validation (TruthfulQA × AdvBench) if Phase 1 succeeds
- Transparency: Acknowledge benchmark-specific findings in Phase 6

**Residual Risk:** LOW (claim scoping sufficient)

---

### R4: API Rate Limits / Cost (LOW)
**Risk:** API quotas block data collection (500 instances × 3 models × 5 dimensions = 7,500 API calls).

**Likelihood:** LOW (20%)
**Impact:** MEDIUM (delays Phase 4)

**Mitigation:**
- Budget estimate: $150-200 (GPT-4 most expensive)
- Rate limiting: Batch requests, exponential backoff
- Caching: Store responses to avoid re-evaluation
- Contingency: Use fewer models (GPT-4 + Claude 3 only) if cost prohibitive

**Residual Risk:** VERY LOW

---

## Statistical Risks

### R5: Null Result on H-E1 (HIGH)
**Risk:** No dimension pairs show phi ≥ 0.3 → coupling does NOT exist.

**Likelihood:** MEDIUM (30%)
**Impact:** CRITICAL (H-E1 MUST_WORK fails → route to Phase 0)

**Mitigation:**
- Tier 3 success criterion: Negative result is publishable (answers research question)
- Lesson learned: Trustworthiness dimensions are behaviorally independent
- Route to Phase 0: New research direction (dimension independence exploitation)

**Residual Risk:** NONE (negative result is valid outcome)

---

### R6: Coupling Disappears with Difficulty Control (HIGH)
**Risk:** Partial phi < 0.2 for all pairs → coupling was spurious difficulty correlation.

**Likelihood:** MEDIUM (40%)
**Impact:** CRITICAL (H-M1 MUST_WORK fails → route to Phase 0)

**Mitigation:**
- Pre-registered qualitative validation: High-coupling instances SHOULD show shared semantic/structural features
- If coupling disappears BUT qualitative analysis shows patterns → investigate alternative mechanisms
- Route to Phase 2A-Dialogue: Revise mechanism (difficulty-adjusted coupling thresholds)

**Residual Risk:** MEDIUM (Prof. Rex's concern)

---

### R7: Weak Effect Sizes (MEDIUM)
**Risk:** Phi values 0.15-0.25 (below threshold but non-zero).

**Likelihood:** MEDIUM (30%)
**Impact:** MEDIUM (weaker contribution claim)

**Mitigation:**
- Tier 2 partial success criterion defined
- Framing: "Coupling exists but weak → dimensions relatively independent (deployment reassurance)"
- Still publishable: Answers whether coupling exists

**Residual Risk:** LOW

---

## Interpretation Risks

### R8: Cross-Model Homogeneity (MEDIUM)
**Risk:** All models show identical coupling patterns (Mantel r > 0.9) → fingerprint claim fails.

**Likelihood:** MEDIUM (40%)
**Impact:** LOW (H-C1 SHOULD_WORK fails, does NOT block Phase 5)

**Mitigation:**
- Reframe as "universal coupling architecture" (different contribution, still novel)
- Implications: Coupling is fundamental to transformer architecture (not training-specific)
- Alternative framing: "Coupling invariant across models → robust phenomenon"

**Residual Risk:** VERY LOW (reframing preserves contribution)

---

### R9: Qualitative Validation Failure (HIGH)
**Risk:** High-coupling instances are random (no shared features) → coupling is statistical noise despite significance.

**Likelihood:** MEDIUM (30%)
**Impact:** HIGH (coupling real but not interpretable)

**Mitigation:**
- Pre-registered criteria: Embedding similarity > 0.7 for high-coupling instances
- Secondary check: Expert annotation (if budget allows)
- Transparency: Report null qualitative result honestly
- Interpretation: "Coupling is real but not semantic/structural → attention-level mechanism"

**Residual Risk:** MEDIUM (Prof. Rex's critical recommendation)

**Escalation:** If qualitative validation fails, downgrade contribution claim from "shared vulnerabilities" to "co-occurrence phenomenon requiring further investigation"

---

## Pipeline Risks

### R10: Route to Phase 0 Trigger (MEDIUM)
**Risk:** H-E1 or H-M1 MUST_WORK failure routes to Phase 0 mid-pipeline.

**Likelihood:** MEDIUM (30% combined from R5 + R6)
**Impact:** HIGH (research direction change)

**Mitigation:**
- Clear routing logic: MUST_WORK failure → Phase 0 brainstorming
- Serena memory: Preserve failure context for new research direction
- Lesson learned: "Trustworthiness dimensions are independent" or "Difficulty confound dominates coupling"

**Residual Risk:** NONE (routing is correct behavior)

---

## Risk Priority Matrix

| Risk | Likelihood | Impact | Mitigation | Residual |
|------|------------|--------|------------|----------|
| R2 (Difficulty Proxy) | HIGH | HIGH | Partial correlation + stratification | MEDIUM |
| R6 (Coupling Disappears) | MEDIUM | CRITICAL | Qualitative validation | MEDIUM |
| R5 (Null Result) | MEDIUM | CRITICAL | Tier 3 criterion | NONE |
| R9 (Qualitative Failure) | MEDIUM | HIGH | Pre-registered criteria | MEDIUM |
| R3 (Framework Limits) | MEDIUM | MEDIUM | Claim scoping | LOW |
| R7 (Weak Effects) | MEDIUM | MEDIUM | Tier 2 criterion | LOW |
| R8 (Homogeneity) | MEDIUM | LOW | Reframing | VERY LOW |
| R1 (Sample Size) | MEDIUM | HIGH | Power analysis | LOW |
| R10 (Route to Phase 0) | MEDIUM | HIGH | Routing logic | NONE |
| R4 (API Limits) | LOW | MEDIUM | Batching/caching | VERY LOW |

## Critical Path Blockers

**MUST_WORK Gate Risks:**
- R5: H-E1 null result (30% likelihood)
- R6: H-M1 difficulty confound (40% likelihood)

**Combined MUST_WORK Failure Probability:** ~58% (sequential dependency)

**Mitigation Strategy:**
- Accept routing to Phase 0 as valid outcome
- Preserve failure context in Serena memory
- Position as "empirical test answered question honestly"

## Recommendations

**For Phase 2C:**
1. Define pre-registered qualitative validation criteria (Prof. Rex's recommendation)
2. Specify embedding similarity threshold (0.7) for high-coupling instances
3. Flag causality limitation explicitly (observational, not causal)

**For Phase 3:**
4. Build abstract benchmark interface (future TrustLLM extensibility)

**For Phase 4:**
5. Implement qualitative validation BEFORE reporting coupling strength
6. Compare confidence-based difficulty with human ratings if available
7. Use both partial correlation AND stratified analysis (belt + suspenders)

**For Phase 6:**
8. Discuss null qualitative result interpretation
9. Emphasize regulatory value (coupling signature disclosure)
10. Address cross-model pattern difference reviewer question
