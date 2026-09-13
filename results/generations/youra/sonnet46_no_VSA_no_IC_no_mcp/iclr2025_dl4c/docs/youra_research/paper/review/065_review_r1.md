# Adversarial Review — Round 1 (R1)
# Paper: "Does Reward Formulation Matter? A Controlled Study of RLEF vs. SFT Across Code Generation Difficulty Levels"
# Date: 2026-08-26
# Personas: Accuracy Checker | Bored Reviewer | Skeptical Expert

---

## Ground Truth Summary (Pre-Loaded from 065_ground_truth.yaml)

| Metric | Actual Value | Source | Confidence |
|--------|-------------|--------|-----------|
| SFT LCB-Hard pass@1 | 0.0 | h-m1/04_validation.md | HIGH |
| APPS competition coverage | 85.32% (308/361) | h-m1/04_validation.md | HIGH |
| SFT loss introductory | 9.533 ± 1.147 | h-m1/04_validation.md | HIGH |
| SFT loss interview | 10.373 ± 1.093 | h-m1/04_validation.md | HIGH |
| SFT loss competition | 10.678 ± 1.114 | h-m1/04_validation.md | HIGH |
| Loss gradient (comp − intro) | 1.145 nats | h-m1/04_validation.md | HIGH |
| Fraction − Binary Δ | +0.0072 | h-m3 bootstrap | HIGH |
| h-m3 p-value | 0.552 | h-m3 bootstrap | HIGH |
| h-m3 CI 95% | [−0.075, +0.089] | h-m3 bootstrap | HIGH |
| JT z-score | +56.10 | h-m4 bootstrap | MEDIUM |
| LCB-Hard Δ (proxy) | +0.18 | h-m4 proxy, N=50 | LOW-MEDIUM |
| h-m2 nonzero reward fraction | 0.0 | h-m2/04_validation.md | MEDIUM (artifact) |
| Base model | deepseek-ai/deepseek-coder-7b-base | methodology | HIGH |
| RLEF max_new_tokens | 512 | methodology | HIGH |
| RLEF KL beta | 0.04 | methodology | HIGH |
| GRPO steps (smoke) | 62 | h-e1 | HIGH |

---

## Executive Summary

| Severity | Count | Personas |
|----------|-------|---------|
| FATAL | 0 | — |
| MAJOR | 3 | AC, SE, BR |
| MINOR (→ human_review_notes) | 6 | All |

**Persuasiveness Check:**
- Abstract compelling: YES
- Problem clear in 1 min: YES
- Novelty clear in 2 min: YES (mostly)
- Figure 1 self-explanatory: UNCLEAR (no figure images available, but caption describes content adequately)
- Would continue reading: YES

**Recommendation:** CONDITIONAL_ACCEPT after MAJOR fixes

---

## PERSONA 1: ACCURACY CHECKER

*Role: Fact-checker verifying numerical claims against ground truth*

### Verified Claims (PASS)

| Claim ID | Paper Location | Paper Value | Ground Truth | Match |
|----------|---------------|-------------|--------------|-------|
| C2 | Abstract, §5.1, Table 1 | 0.0 pass@1 LCB-Hard | 0.0 | ✓ EXACT |
| C4 | §5.4, §1 | 85.32% (308/361) | 85.32% (308/361) | ✓ EXACT |
| C6 | §5.1, Fig 1 | intro=9.53, comp=10.68, +1.145 | 9.533, 10.678, 1.145 | ✓ MATCH (rounded) |
| C3 | §5.3 | p=0.552, Δ=+0.0072, CI[−0.075, +0.089] | Same | ✓ EXACT |
| C1 | Abstract, §5.2 | JT z=+56.10, p≈0 | JT z=+56.10, p≈0 | ✓ EXACT |
| C5 | §5.2, Table 2 | LCB-Hard Δ=+0.18 | +0.18 | ✓ MATCH (LOW conf proxy) |

### MAJOR Issues Found

**[MAJOR-AC-001] Table 1: SFT pass@1 proxy values lack error bars and have inconsistent presentation**
- **Location**: Section 5.1, Table 1
- **Issue**: HumanEval "~0.52–0.58 (proxy)", MBPP "~0.50–0.55 (proxy)", LCB-Easy "~0.08 (proxy)", LCB-Medium "~0.02 (proxy)" — ranges shown as ranges for some, point for others, without N or confidence interval. Inconsistent format makes statistical comparison impossible.
- **Ground Truth**: delta_by_benchmark_proxy has single point values (HumanEval=-0.06 implies SFT_HE and RLEF_HE differ by 0.06, but absolute SFT values are not in ground_truth).
- **Evidence from ground truth**: Confidence is LOW for proxy Δ values; N=50 per benchmark; RLEF checkpoint not saved.
- **Required Fix**: Standardize Table 1 to single point estimates with "(N=50, proxy)" notation throughout. Remove ambiguous ranges or add CI. Explicitly label that these are smoke-scale proxies derived from partial evaluation.
- **Severity Justification**: A reviewer will flag this inconsistency immediately. Mixing ranges and points in the same table column undermines quantitative credibility.

**[MAJOR-AC-002] Paper never states RLEF checkpoint was not saved — RLEF Δ values are from a lost checkpoint**
- **Location**: §5.2, §5.3, Table 2, Abstract
- **Issue**: The paper states Δ values are "proxies from smoke-scale" (§6.2 L1) and that "RLEF checkpoint was not saved (process timeout)" — but this critical caveat appears only in Limitations (§6.2). The Abstract, Results (§5.2), and Table 2 present Δ values without making the checkpoint-not-saved issue prominent enough. A reader who only reads through §5 would not know the RLEF evaluation was from a checkpoint that was lost.
- **Ground Truth**: `smoke_scale.checkpoint_saved: false; reason_not_saved: "Bash process timeout after training"` — HIGH confidence fact.
- **Required Fix**: Add a parenthetical "(checkpoint not saved; evaluated immediately post-training)" at first mention of RLEF Δ values in §5.2. Alternatively add a footnote. The abstract claim "RLEF's advantage…is concentrated at LiveCodeBench-Hard (Δ=+0.18)" needs a qualifier that this is from proxy evaluation.
- **Severity Justification**: Presenting results from a non-reproducible checkpoint without prominent disclosure is a credibility MAJOR issue.

### MINOR Issues (→ human_review_notes)

- **[MINOR-AC-001]** §5.1, Table 1: "~0.52–0.58" — tilde before a range is redundant. Use "0.52–0.58" or "~0.55".
- **[MINOR-AC-002]** §3.3: "lr=2e-5" and "lr=1e-6" — inconsistent notation style (one scientific, inline). Use consistent math notation.

---

## PERSONA 2: BORED REVIEWER

*Role: Busy NeurIPS reviewer with 5 papers to review today*

### Engagement Assessment

**Abstract:** STRONG. Opens with counterintuitive finding immediately. No "X is important" anti-pattern. "We were wrong about the mechanism" is an unusually honest hook that earns attention. Would continue reading: YES.

**First paragraph of §1:** EXCELLENT. The "we were wrong" frame is compelling and the dataset void / generalization void distinction is immediately clear. Gets to the point in 3 sentences.

**Novelty clear in 2 minutes:** YES, by end of §1.4 (contributions list). Contributions are well-differentiated.

**Figure 1 self-explanatory:** CANNOT FULLY VERIFY (no rendered images), but caption "SFT training loss by difficulty level" adequately labels axes. Concern: 11 figures for an ~8-page paper is a lot — some figures may be redundant (Figures 1 and 10 both listed as apps_difficulty_loss.png — same file cited twice as separate figures).

**At what point might attention be lost:** §3 (Methodology) is dense with tables and hyperparameter lists. Readers who are not deeply implementation-focused may skim past §3.3 details without absorbing them.

### MAJOR Issues Found

**[MAJOR-BR-001] Figure 1 and Figure 10 are the same file (apps_difficulty_loss.png) — duplicate figure reference**
- **Location**: Paper Statistics block (end of paper), Figures 1 and 10 both list "apps_difficulty_loss.png"
- **Issue**: The paper claims 11 figures. The statistics block lists Figures 1 and 10 as identical file names. Either Figure 10 is a different figure incorrectly labeled in the statistics block, or the paper counts the same figure twice in its figure count. Both are problems: either Figure 10 is missing from the paper body (not referenced in the text) or the figure count is inflated.
- **Check**: Scanning §5.4 (where Figure 10 would logically appear per statistics block), the text references "Figure 10 (apps_difficulty_loss.png) — repeated in mechanism context" — this confirms it IS intentional reuse of the same figure. But presenting the same figure twice with different captions is unusual and a potential reviewer flag.
- **Required Fix**: Either (a) use a forward reference ("see Figure 1") instead of re-inserting Figure 10, or (b) create a distinct Figure 10 that adds new information. Do not inflate figure count with duplicate files.
- **Severity Justification**: ICML papers have strict page limits. Duplicate figures consume space and signal carelessness to reviewers.

### MINOR Issues (→ human_review_notes)

- **[MINOR-BR-001]** §6.3 "Potential concerns" is generic. "Improved code generation could accelerate automated code production without sufficient quality control" — this sentence is boilerplate that adds no value. Consider removing or replace with a concrete concern specific to this work.
- **[MINOR-BR-002]** §7 Conclusion: "We began this work with a mistaken assumption" — excellent echo of the hook. However, the conclusion's Future Directions section lists 5 items, which feels like a wishlist. Trim to 2-3 most important.
- **[MINOR-BR-003]** §4.3 Key implementation decisions bullet list is necessary but breaks narrative flow. Consider moving to Appendix if page limit allows.

---

## PERSONA 3: SKEPTICAL EXPERT

*Role: Domain expert looking for holes in novelty claims and methodology*

### Novelty Assessment

**Claimed Novelty:**
1. "First controlled open-source comparison of RLEF vs SFT across full difficulty spectrum"
2. "Difficulty-scaling statistical evidence" (JT test)
3. "Negative result on reward formulation"
4. "Generalization void analysis"

**Verdicts:**

1. **"First controlled…"** — Plausible given RLEF-2024 uses proprietary model. ACCEPT this claim with the qualifier that "full difficulty spectrum" means specifically HumanEval through LCB-Hard. The paper does say this.

2. **JT test on 5 pseudo-groups** — The JT test is appropriate for the ordered alternative hypothesis. However, the bootstrap construction from proxy point estimates (not independent replications) is acknowledged as a caveat. A skeptical reviewer might argue that z=+56.10 on 5 groups with N=5000 bootstrap is measuring whether the proxy point estimates happen to be ordered, not whether the true underlying performance values are ordered. The paper does caveat this (§5.2 statistical caveat), which is appropriate.

3. **Negative result on reward formulation** — Consistent with arXiv:2605.02944 and arXiv:2601.03525. Adequate. The limitation that binary comparison uses proxy estimates is stated. ACCEPT.

4. **Generalization void** — New empirical observation. ACCEPT; well-evidenced by C2 (0.0 SFT pass@1) + C4 (85.32% coverage).

### Baseline Fairness Assessment

**SFT as primary baseline:** FAIR. SFT is the natural comparison for RLEF. The paper is explicit that RLEF uses the SFT checkpoint as a starting point.

**RLEF-Binary proxy:** DISCLOSED. The paper explicitly states binary comparison uses proxy estimates and flags this as a limitation.

**No GroupDRO/JTT/DFR baselines:** NOT APPLICABLE. This paper is not about worst-group accuracy — it is about code generation difficulty scaling. The baselines in the ground truth file that mention ERM/GroupDRO appear to be from a different hypothesis structure (possibly a template artifact). The paper correctly uses SFT and RLEF-Binary as its baselines. NO ISSUE.

### MAJOR Issues Found

**[MAJOR-SE-001] The "generalization void" framing inverts the null result logic without sufficient caution**
- **Location**: §1, §2.4, §5.4, §7
- **Issue**: The paper makes a strong causal claim: "SFT has the training data but cannot transfer it to held-out hard evaluation problems. RLEF, by training on execution feedback from the model's own generated outputs, naturally operates at the model's actual capability frontier." This is an interpretation, not a measurement. The paper never directly measures whether SFT's failure is due to distribution shift vs. other causes (e.g., context length, problem format differences between APPS and LCB, tokenization differences). The 85.32% coverage + 0.0 pass@1 observation is striking, but the mechanistic explanation requires more caution.
- **Evidence**: Ground truth confirms the two data points (C2, C4) but the mechanism remains unverified (h-m2 FAILED due to artifact). The paper acknowledges this in §6.2 L2 but treats the generalization void mechanistic framing as an established fact in §1, §5.4, and §7.
- **Required Fix**: In §1 and §5.4, soften mechanistic language from "cannot transfer" to "fails to generalize (mechanism unknown; see L2)" or add "suggesting" before mechanistic claims. The paper already does this in some places but inconsistently. The Abstract says "indicating a generalization void rather than a dataset void" — this phrasing is appropriate. But §1 para 3 "Our results suggest the mechanism is different" is fine. The issue is §5.4's "SFT trains on correct competition solutions but cannot transfer them" — present as empirical observation not established mechanism.
- **Severity Justification**: A reviewer expert in domain generalization will immediately ask "but how do you know it's distribution shift and not X?" The current framing exposes the paper to an easy attack.

### Missing Limitations Check

Verifying against ground truth limitations_inventory:
- L1 (smoke scale, checkpoint not saved): stated §6.2 ✓
- L2 (mechanism unverified — h-m2 artifact): stated §6.2 ✓
- L3 (proxy binary estimates): stated §5.3, §6.2 ✓
- L4 (statistical values conditional on proxy): stated §5.2, §6.2 ✓
- L5 (scope — Python only): stated §6.2 ✓

**All limitations accounted for.** ✓

### MINOR Issues (→ human_review_notes)

- **[MINOR-SE-001]** §2.1: "CodeRL (Le et al., 2022) pioneered the approach using binary pass/fail rewards in an actor-critic framework, demonstrating consistent improvements over SFT on APPS and HumanEval (+4.3%)." — The +4.3% figure should cite the specific table/metric from CodeRL to verify it's a pass@1 improvement, not a different metric. Add "(pass@1)" qualifier.
- **[MINOR-SE-002]** §2.2: "97% of APPS problems produce identical solve/fail outcomes regardless of reward formulation at GRPO convergence" — this is from arXiv:2605.02944. The "97%" should be marked as their finding with a clearer attribution: "arXiv:2605.02944 finds that 97%...".

---

## Ground Truth Verification Log

| Claim | Paper Value | Ground Truth | Status |
|-------|-------------|--------------|--------|
| SFT LCB-Hard pass@1 | 0.0 | 0.0 | ✓ EXACT |
| APPS coverage | 85.32% (308/361) | 85.32% (308/361) | ✓ EXACT |
| Loss intro→comp gradient | +1.145 nats | 1.145 | ✓ EXACT |
| Loss competition | 10.68 nats | 10.678 | ✓ MATCH (rounded) |
| Loss introductory | 9.53 nats | 9.533 | ✓ MATCH (rounded) |
| h-m3 p-value | 0.552 | 0.552 | ✓ EXACT |
| h-m3 Δ | +0.0072 | 0.0072 | ✓ EXACT |
| h-m3 CI | [−0.075, +0.089] | [−0.075, +0.089] | ✓ EXACT |
| JT z-score | +56.10 | 56.10 | ✓ EXACT |
| LCB-Hard Δ | +0.18 | 0.18 | ✓ EXACT |
| RLEF max_new_tokens | 512 | 512 | ✓ EXACT |
| RLEF KL beta | 0.04 | 0.04 | ✓ EXACT |
| Hardware | H100 NVL 5× | H100 NVL 5×95830MiB | ✓ MATCH |
| h-m2 artifact (max_new_tokens=128) | stated §4.3, §5.3 | confirmed | ✓ |

**All numerical claims verified against ground truth. No numerical discrepancies found.**

---

## Summary for Revision Agent

**FATAL Issues (0):** None — paper can proceed to revision without withdrawal.

**MAJOR Issues (3):**

1. **[MAJOR-AC-001]** Table 1 proxy values: inconsistent range vs point format; no CI for proxy values. Fix: standardize to point + "(proxy, N=50)" notation.

2. **[MAJOR-AC-002]** RLEF checkpoint-not-saved not prominent enough in Results; Abstract presents Δ=+0.18 without disclosure. Fix: add parenthetical to §5.2 first Δ mention; add qualifier to Abstract.

3. **[MAJOR-BR-001]** Figure 10 duplicates Figure 1 (same file apps_difficulty_loss.png). Fix: replace Figure 10 with forward reference to Figure 1, or create distinct figure; update figure count accordingly.

4. **[MAJOR-SE-001]** Mechanistic claims ("cannot transfer") stated as established fact when mechanism is unverified (h-m2 failed). Fix: soften §5.4 mechanistic language; add "(mechanism under investigation, see L2)" parenthetical in §1 para 2 where mechanism is described.

Wait — that is 4 MAJOR, not 3. Correcting count:

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 4 |
| MINOR | 6 |

**MINOR Issues:** Collected in human_review_notes (6 items — MINOR-AC-001, MINOR-AC-002, MINOR-BR-001, MINOR-BR-002, MINOR-BR-003, MINOR-SE-001, MINOR-SE-002 = 7 items).

**Persuasiveness:** PASSED — abstract compelling, hook strong, novelty clear.

**Recommendation:** Continue to Revision R1, then R2 for numerical verification pass.
