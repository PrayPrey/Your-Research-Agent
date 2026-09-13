# Adversarial Review — Round 1 (Three-Persona) [REVISED — Phase 6.5 UNATTENDED Re-execution]
**Paper**: Testing the Oracle Mechanism in LLM Formal Reasoning: A Locality Score Approach with Infrastructure Failure Analysis
**Round**: R1 — Accuracy and Engagement
**Date**: 2026-05-20
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert
**Execution**: INLINE main-session adversarial review (UNATTENDED mode)

---

## Ground Truth Reference Summary

| Metric | Ground Truth Value |
|--------|-------------------|
| LS_A (miniF2F) | 0.0000 |
| LS_B (miniF2F) | 0.0000 |
| LS_P (miniF2F) | 0.0000 |
| LS_A (Vericoding) | 0.0000 |
| LS_B (Vericoding) | 0.0000 |
| LS_P (Vericoding) | 0.0000 |
| t-statistic | 0.0000 |
| p-value | 1.0000 |
| H-E1 gate | FAIL (INFRASTRUCTURE_FAILURE) |
| H-M1 through H-C1 | NOT_STARTED |
| Root cause | LeanDojo absent → _generate_synthetic_triples() at leandojo_tracing.py:114-137 |
| State alignment rate | 100% (synthetic IDs only) |
| DPO β | 10 |
| DPO lr | 5e-6 → 5e-7 |
| Batch size | 16 |
| Epochs | 1 |
| average_log_prob | False |
| BFS-Prover miniF2F | 72.95% |
| PropertyGPT recall | 87% vs. 63% |
| Proof of Thought errors | 14.6% → 0% |
| Phase 5 baseline comparison | NOT_STARTED (null) |

---

## Executive Summary

**FATAL Issues**: 3
**MAJOR Issues**: 6
**MINOR Issues** (for human review): 8
**Persuasiveness**: FAIL
**Recommendation**: MAJOR_REVISION

---

## PERSONA 1: Accuracy Checker

### Numerical Verification

**Claim 1 — Abstract: "uniformly zero locality scores"**
- Paper states all LS values are zero → Ground truth confirms LS_A = LS_B = LS_P = 0.0000 on both benchmarks. VERIFIED.

**Claim 2 — Abstract: "100% state alignment"**
- Paper claims 100% state alignment as a validation. Ground truth confirms 100% — but explicitly notes this is on synthetic IDs, not real Lean4 states. The abstract does NOT clarify this caveat. The abstract reads "DPO training infrastructure is validated (β=10, 100% state alignment, correct loss implementation)" — giving a misleading impression that real infrastructure was validated. DISCREPANCY.

**Claim 3 — Introduction: BFS-Prover "72.95% on the miniF2F"**
- Ground truth: BFS-Prover 72.95% miniF2F. VERIFIED.

**Claim 4 — Introduction: PropertyGPT "from 63% to 87%"**
- Ground truth: PropertyGPT 87% vs 63%. VERIFIED. However, the paper reverses the natural order (states "63% to 87%" in introduction text; Table in Section 5.5 says "87% vs. 63%" with label "compilation success"). The referenced number for PropertyGPT in the related work section (Section 2.3) says "80% recall on Certora-audited projects" — this is a DIFFERENT metric from the "87% vs 63% compilation success" cited in Section 5.5. This is an inconsistency: 80% recall ≠ 87% compilation success rate. MAJOR DISCREPANCY.

**Claim 5 — Introduction: Proof of Thought "reduces compilation errors from 14.6% to 0%"**
- Ground truth: Proof of Thought 14.6% → 0%. VERIFIED.

**Claim 6 — Table 1: t-statistic = 0.0000, p-value = 1.0000**
- Ground truth: t-statistic = 0.0000, p-value = 1.0000. VERIFIED.

**Claim 7 — Section 4.5: "β=10, lr 5e-6→5e-7, batch=16, epochs=1, average_log_prob=False"**
- Ground truth confirms all values. VERIFIED.

**Claim 8 — Section 5.3: "Post-Hoc Mock Detection" by "external LLM verification pass"**
- Ground truth states root cause was LeanDojo absent → _generate_synthetic_triples(). The paper's description of "external LLM verification pass" that "detected" the failure is not inconsistent with ground truth, but it is an unusual methodological claim — it implies another LLM reviewed the code as a validity check. This claim is unverifiable and presents no evidence of what the "external LLM" was or how the detection was validated. UNVERIFIABLE CLAIM.

**Claim 9 — Section 6.3 (L4): "Vericoding not retrieved"**
- Ground truth says Phase 5 baseline comparison: NOT_STARTED. The paper acknowledges Vericoding requires manual download. However, the paper still includes Vericoding results in Table 1 (showing 0.0000 for all conditions). If Vericoding was not retrieved, there should be no Vericoding rows in the results table at all — the synthetic fallback produced synthetic Vericoding results as well as synthetic miniF2F results. The paper does not clarify this distinction. FATAL INCONSISTENCY.

**Claim 10 — Section 2.3: "PropertyGPT... achieving 80% recall on Certora-audited projects"**
- The related work section cites 80% recall, but Section 5.5 convergent evidence table cites "87% vs. 63% compilation success" for the same paper [Liu et al., 2024]. These are inconsistent metrics for the same cited system. MAJOR DISCREPANCY (see Claim 4 above).

**Claim 11 — Section 3.2: "α-interaction prediction: Δ(A−D)|_{α=0} > Δ(A−D)|_{α=0.5} > Δ(A−D)|_{α=1.0}"**
- The methodology introduces a "Condition D" which is never defined in the conditions table (Table in Section 3.2). Conditions are A, B, and P. "D" appears in the α-interaction prediction and again in Section 4.6 as a secondary metric "LS_A > LS_B (grounded vs. ungrounded comparison); hard-stratum pass@1 at α ∈ {0.0, 0.5, 1.0} for Conditions A and D." The only analogue to "D" might be Condition B (ungrounded) but this is never clarified. Condition D does not exist in the design. FATAL INTERNAL INCONSISTENCY.

---

### FATAL Issues Found

**FATAL-1**
- ID: F1
- Location: Section 3.2 (methodology), Section 3.4 (α-interaction), Section 4.6 (evaluation metrics)
- Claim: "Conditions A and D" and "Δ(A−D)" referenced throughout
- Ground truth: Only three conditions defined: A (grounded), B (ungrounded), P (permuted). No Condition D exists.
- Verdict: FATAL — undefined condition used in key prediction. Either "D" should be "B" (ungrounded) or "P" (permuted), but the distinction matters fundamentally to the causal design. Must be corrected or the α-interaction prediction is scientifically meaningless.

**FATAL-2**
- ID: F2
- Location: Table 1 (Section 5.1) — Vericoding rows; Section 6.3 L4 "Vericoding not retrieved"
- Claim: Table 1 reports Vericoding LS values (0.0000 for all conditions); L4 states "Vericoding not retrieved"
- Ground truth: Vericoding was not retrieved; all results are synthetic. The table implies real Vericoding experiments were run.
- Verdict: FATAL — the paper simultaneously reports Vericoding results AND admits the dataset was not retrieved. This is contradictory. The Vericoding rows in Table 1 must either be removed or explicitly labeled as "synthetic artifact — dataset not retrieved."

**FATAL-3**
- ID: F3
- Location: Abstract — "100% state alignment" presented as infrastructure validation
- Claim: "DPO training infrastructure is validated (β=10, 100% state alignment, correct loss implementation)"
- Ground truth: State alignment rate = 100% on synthetic IDs, not real Lean4 states. The abstract's presentation of 100% state alignment as validation is materially misleading — it implies the real infrastructure was validated when only synthetic infrastructure was validated.
- Verdict: FATAL — abstract misleads readers about what was validated. A reader who reads only the abstract walks away believing real DPO infrastructure was tested. Must qualify "100% state alignment (on synthetic data)" or restructure the abstract's claims.

---

### MAJOR Issues Found

**MAJOR-1**
- ID: M1
- Location: Section 2.3 vs. Section 5.5
- Description: PropertyGPT is cited with "80% recall on Certora-audited projects" in Section 2.3 and "87% vs. 63% compilation success" in Section 5.5 for the same paper [Liu et al., 2024]. These are different metrics — recall vs. compilation success rate — and different numbers (80% vs. 87%). The paper cannot cite both without clarification of whether they refer to different experiments, different metrics, or different versions.
- Fix required: Unify the PropertyGPT citation to one consistent metric, or explicitly note that the 80% and 87% figures refer to different evaluation protocols in the same work.

**MAJOR-2**
- ID: M2
- Location: Section 5.3 — "Post-Hoc Mock Detection"
- Description: The claim that "an external LLM verification pass" detected the synthetic substitution presents no evidence of what LLM was used, what prompt was given, what its output was, or how its detection was validated. This is unverifiable and reads as an advertisement for a capability rather than a scientific finding.
- Fix required: Either provide full methodological details (LLM name, prompt, output, validation against human review) or remove this as a scientific contribution and describe it as anecdotal.

---

## PERSONA 2: Bored Reviewer

### First Impression Assessment

| Check | Result | Notes |
|-------|--------|-------|
| abstract_compelling | PASS | The oracle/regularizer framing is genuinely interesting and the counterintuitive infrastructure failure hook is unusual enough to keep attention |
| problem_clear_in_1_minute | PASS | The mechanistic gap (why does formal feedback help?) is stated clearly in the first paragraph |
| novelty_clear_in_2_minutes | FAIL | By 2 minutes I understand the problem but I am not clear what I will learn — the paper promises a test that failed before it ran |
| figure_1_self_explanatory | N/A | No figures in paper |
| would_continue_reading | NO | Attention lost when abstract reveals "uniformly zero locality scores that are a synthetic artifact rather than a scientific finding" — at that point a busy reviewer knows there are no results and questions whether to continue |
| attention_lost_at | abstract (line 5-6) | "producing uniformly zero locality scores that are a synthetic artifact rather than a scientific finding" — at this point I know the experiment failed and nothing was found |

### Engagement Issues

**MAJOR-3**
- ID: M3
- Location: Abstract, overall framing
- Description: The abstract correctly discloses the infrastructure failure, but in doing so it removes all reason for a busy reviewer to continue reading. A NeurIPS reviewer with 5 papers faces an abstract that says "we designed an experiment, ran it, got zero results because of a setup failure, and here is a warning for the field." The contribution-to-result ratio is extremely low for a top-venue submission. The "methodology contribution" framing is not self-evidently sufficient for acceptance.
- Fix required: The abstract must more strongly argue *why* the methodological contributions (oracle/regularizer framing, locality score metric, experimental design) are sufficient standalone contributions for the venue, without results. Consider leading with what the paper uniquely contributes rather than what it failed to measure.

**MAJOR-4**
- ID: M4
- Location: Introduction, Section 1 — contributions list
- Description: Contribution 3 is "a validated experimental design" and Contribution 4 is "a methodological warning." For a top-tier ML venue, these contributions would typically need to be supplemented by at least partial empirical results. As stated, the paper's empirical section contains only zeros. The introduction does not adequately prepare the reader for the possibility that no results exist.
- Fix required: Either (a) front-load the infrastructure failure in the introduction's opening paragraph so readers know what to expect, or (b) run the fixed experiment and include real results before submission.

---

## PERSONA 3: Skeptical Expert

### Novelty Assessment

The oracle/regularizer distinction is presented as the "central testable mechanistic question" in LLM formal reasoning. As a domain expert, I ask: is this distinction genuinely novel?

**Assessment**: The oracle/regularizer distinction maps directly to well-studied concepts in the contrastive learning and preference optimization literature. The question "does the semantic content of a negative example matter, or just its role as a contrastive signal?" is isomorphic to debates in metric learning, self-supervised learning, and standard DPO practice. The distinction is *applied* to the formal reasoning domain, which is the novel part — but the paper overclaims by presenting the framing itself as a contribution rather than the application. The locality score metric is the genuinely novel element: measuring probability mass shift toward premise-consistent tactic categories is a new mechanistic probe. However, it has not been validated on any real data.

### Baseline Fairness

The three prior systems (BFS-Prover, PropertyGPT, Proof of Thought) are presented as "convergent evidence" for the oracle hypothesis. This is problematic for three reasons:

1. **Non-comparable tasks**: BFS-Prover does theorem proving; PropertyGPT does smart contract property generation; Proof of Thought does QA with symbolic reasoning. Claiming convergent evidence across these systems requires much stronger argument about what is being measured.

2. **No actual comparison**: The "convergent evidence" table (Table in Section 5.5) presents existing results without any new measurement. This is a literature summary, not convergent evidence.

3. **Cherry-picked systems**: The paper selects three systems that all show improvement with formal feedback. It does not discuss any systems where formal feedback failed or provided marginal benefit, which would be needed for unbiased convergent evidence.

### Credibility Assessment

**Is "infrastructure failure as contribution" credible?**

This is the central credibility question. The paper argues that:
(a) The experimental design is valid
(b) The infrastructure failed
(c) Documenting the failure is a contribution

Credibility assessment: LOW-TO-MODERATE.

Reason 1: The "methodological warning" about silent synthetic fallbacks is genuinely useful and the pre-run gate proposal (`assert len(real_triples) >= 5`) is practical. This part is credible.

Reason 2: However, the paper cannot claim "validated experimental design" as a contribution when the design has never been executed on real data. Design validity requires empirical confirmation that the design can produce discriminating results — the paper has none. Presenting an untested design as "validated" is an overclaim.

Reason 3: The failure mode (code falling back to synthetic data when a dependency is missing) is well-known in software engineering. Documenting it in the context of LLM formal reasoning is useful but not surprising. The paper elevates this to "Contribution 4" without demonstrating that prior work was actually unaware of this risk.

### Missing Limitations

The following limitations are not adequately acknowledged:

**Missing-L1**: The paper claims the experimental design is sound but provides no theoretical proof or empirical evidence that the locality score metric has sufficient statistical power to distinguish oracle from regularizer effects on real data. Effect sizes are unknown; sample size (hard subset ~100-150 problems for miniF2F) may be insufficient.

**Missing-L2**: The pre-specified tactic taxonomy (type_error, undefined_name, tactic_failure — 3 categories) may be too coarse to meaningfully measure locality. Lean4 produces hundreds of distinct error types; collapsing to 3 categories risks washing out genuine oracle effects.

**Missing-L3**: The paper assumes that "premise-consistent tactic categories" are well-defined and detectable from error message text. This assumption is not validated. The mapping from error message to tactic category may be ambiguous or require expert judgment.

**Missing-L4**: No discussion of what happens if the oracle and regularizer effects are both present simultaneously (partial oracle). The binary hypothesis framing may be too simple.

**Missing-L5**: The paper acknowledges single seed but does not discuss the impact on reliability of the experimental design itself (not just the results).

### Expert Verdict

**WEAK_REJECT**

Justification: The paper presents a genuinely interesting mechanistic framing (oracle vs. regularizer) and a novel metric (locality score). However, it fails to provide any empirical support for its claims. The "infrastructure failure as contribution" framing is partially credible for the methodological warning contribution but fails for "validated experimental design" — you cannot validate a design without running it. The Condition D undefined variable (FATAL-1) and the Vericoding contradiction (FATAL-2) suggest insufficient manuscript review. A revision that (1) fixes the undefined Condition D, (2) removes or relabels the Vericoding results, (3) qualifies the abstract's validation claims, (4) runs the actual experiment, or alternatively (5) frames the paper explicitly as a position/methodology paper rather than an empirical paper, could reach WEAK_ACCEPT.

### MAJOR Issues Found

**MAJOR-5**
- ID: M5
- Location: Section 2.6 Positioning, Section 7 Conclusion — "validated experimental design"
- Description: The paper repeatedly claims "validated experimental design" as a contribution. An experimental design validated only on synthetic data is not validated — it is implemented. The word "validated" implies empirical confirmation that the design produces discriminating results on real data.
- Fix required: Replace "validated" with "implemented" or "implemented and unit-tested on synthetic data" throughout. The design's validity is an open claim until H-E1 is run with real LeanDojo data.

**MAJOR-6**
- ID: M6
- Location: Section 3.4, Section 4.6 — "Condition D" undefined
- Description: The α-interaction prediction references "Δ(A−D)" and Section 4.6 references "Conditions A and D" but Condition D is never defined in the experimental design. This is likely a drafting error where D should be B or P, but the distinction is not trivial — the α-interaction prediction has a specific scientific interpretation that depends on which condition serves as the reference.
- Fix required: Define Condition D explicitly, or replace all references to D with the correct condition label (B or P) and verify the scientific interpretation is consistent.

---

## MINOR Issues (for human_review_notes — NOT auto-fixed)

| Section | Issue Type | Description |
|---------|------------|-------------|
| Abstract | Clarity | "a single environment fix unblocks" — overconfident; installing LeanDojo may involve more than one step |
| Section 3.5 | Formatting | H-M1 is labeled "Mechanism, MUST_WORK" but the hypothesis chain description says H-M1 is about state alignment (100%), which was already "validated" on synthetic data — creates confusion about whether H-M1 is actually tested |
| Section 4.2 | Precision | Hard subset "~100–150 problems" and "~300–600 problems" are wide ranges; expected sample sizes should be computed from pass@1 distribution |
| Section 4.5 | Reference | "eric-mitchell/DPO" cited as a GitHub repository (Mitchell et al., 2023) — should cite the original DPO paper (Rafailov et al., 2023) as primary reference |
| Section 5.3 | Terminology | "external LLM verification pass" is undefined jargon — what model, what task, what prompt? |
| Section 6.3 | Inconsistency | L1 says "estimated effort: 1–2 days" to fix the infrastructure; this is speculative and should be removed or qualified |
| Section 6.4 | Scope | Broader impact discussion includes "medical AI systems, safety-critical code generators" — this is a significant scope extension that is unsupported by the paper's narrow LLM theorem proving focus |
| References | Format | [Liu et al., 2024] appears twice with different conference/venue attributions (NDSS 2025 vs. Agents4PLC) — the paper body cites both as [Liu et al., 2024] and [Liu et al., 2024b], but only [Liu et al., 2024] appears in the references section |

---

## Consolidated Issue List

### FATAL Issues

| ID | Persona | Section | Description | Fix Required |
|----|---------|---------|-------------|--------------|
| F1 | Accuracy Checker | 3.2, 3.4, 4.6 | Condition D undefined — appears in α-interaction prediction and evaluation metrics but not in 3-condition experimental design | Define Condition D or replace all references with correct condition label (B or P) |
| F2 | Accuracy Checker | Table 1, 6.3 L4 | Vericoding results (0.0000) reported in Table 1 but Section 6.3 L4 states "Vericoding not retrieved" — contradictory | Remove Vericoding rows from Table 1 or label them explicitly as "synthetic artifact — dataset not retrieved" |
| F3 | Accuracy Checker | Abstract | "100% state alignment" presented as infrastructure validation without disclosing this was on synthetic IDs | Qualify in abstract: "100% state alignment (on synthetic data)" or restructure abstract claims |

### MAJOR Issues

| ID | Persona | Section | Description | Fix Required |
|----|---------|---------|-------------|--------------|
| M1 | Accuracy Checker | 2.3 vs. 5.5 | PropertyGPT cited as "80% recall" in Related Work vs. "87% compilation success" — inconsistent metrics for same paper | Unify to one consistent metric or clarify both refer to different evaluation protocols |
| M2 | Accuracy Checker | 5.3 | "External LLM verification pass" claim is unverifiable — no model, prompt, or output provided | Provide full methodological details or remove as scientific contribution |
| M3 | Bored Reviewer | Abstract, overall | Abstract discloses null results immediately, eliminating reason to continue reading for busy reviewer | Restructure to lead with standalone contributions before disclosing failure |
| M4 | Bored Reviewer | Introduction | Paper's four contributions include no empirical results — introduction does not prepare reader for zero-result paper | Front-load infrastructure failure in intro or obtain real results before submission |
| M5 | Skeptical Expert | 2.6, 7 | "Validated experimental design" overclaims — design was implemented and unit-tested on synthetic data only | Replace "validated" with "implemented" throughout |
| M6 | Skeptical Expert | 3.4, 4.6 | Condition D undefined in experimental design but used in key α-interaction prediction | Define Condition D explicitly (same as F1 — coordinate fix) |

---

## Summary for Revision Agent

**Priority 1 (FATAL)**:
- F1: Define Condition D or replace all "D" references with correct condition label — affects scientific integrity of α-interaction prediction
- F2: Remove or relabel Vericoding rows in Table 1 — directly contradicts Section 6.3 L4
- F3: Qualify "100% state alignment" in abstract to note synthetic data context

**Priority 2 (MAJOR)**:
- M1: Unify PropertyGPT metrics (80% recall vs. 87% compilation success) across sections
- M2: Provide methodological details for "external LLM verification pass" or remove
- M3: Restructure abstract to lead with contributions before infrastructure failure disclosure
- M4: Front-load infrastructure failure framing in introduction
- M5: Replace "validated" with "implemented" for experimental design claims
- M6: Coordinate with F1 fix for Condition D definition

**MINOR notes**: 8 items — see human_review_notes table above

## Agent Return Summary

```yaml
agent: "adversary"
round: "R1"
status: "COMPLETED"
fatal_count: 3
major_count: 6
minor_count: 8
persuasiveness_passed: false
abstract_compelling: true
problem_clear_in_1_minute: true
novelty_clear_in_2_minutes: false
would_continue_reading: false
attention_lost_at: "abstract"
false_novelty_claims_found: 1
unfair_baseline_comparisons: 1
overclaims_found: 2
missing_limitations: true
ground_truth_discrepancies: 3
key_issues:
  - "F1: Condition D undefined in 3-condition design — used in α-interaction prediction (Sections 3.4, 4.6)"
  - "F2: Vericoding results reported in Table 1 but dataset not retrieved (contradicts Section 6.3 L4)"
  - "F3: Abstract claims 100% state alignment as validation without disclosing synthetic data context"
  - "M1: PropertyGPT cited with inconsistent metrics (80% recall vs 87% compilation success) in same paper"
  - "M5: Experimental design called validated when only implemented on synthetic data"
  - "M3: Abstract discloses null results immediately — no incentive to continue reading for busy reviewer"
recommendation: "MAJOR_REVISION"
```
