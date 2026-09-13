# Adversarial Review - Round 1

**Paper:** Measuring Doctest Executability in Python Corpora: Feasibility of Execution-Filtered SFT Data Curation
**Reviewed:** 2026-08-04T20:01:00Z
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 1 | One numerical inconsistency; dataset attribution needs clarification |
| Engagement | 0 | 1 | Paper risks rejection for scope: a negative feasibility result with no SFT experiment |
| Credibility | 0 | 2 | "First" claim overstated; compile-only claim is unverified speculation in print |
| **TOTAL** | **0** | **4** | MAJOR REVISION required |

**Recommendation:** MAJOR_REVISION — No fatal errors, but four significant weaknesses that a program committee would likely cite as rejection reasons. The core finding is valid and clearly measured; the framing and scope claims need recalibration.

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Summary Table

| Claim | Paper Value | Ground Truth | Match? |
|-------|-------------|--------------|--------|
| Phase A rate | 3.1% (310/10,000) | 310, 0.031 | PASS |
| Phase B rate | 2.0% (204/10,000) | 204, 0.0204 | PASS |
| Phase C rate | 0.1% (10/10,000) | 10, 0.001 | PASS |
| Gap multiplier | 31× | 0.031/0.001 = 31.0 | PASS |
| Token pool | 0.004M tokens | 0.004376M | PASS (rounded correctly) |
| Token pool gap | 125,000× | 500/0.004 = 125,000 | PASS |
| Scan duration | 129.8 seconds | 129.83 | PASS (rounded correctly) |
| Unit tests | 28/28 | 28/28 | PASS |
| n_sampled | 10,000 | 10,000 | PASS |
| Workers | 4 (ProcessPoolExecutor) | n_workers=4 | PASS |
| Full-corpus executable files | 12,960 | 12,960 | PASS |
| EffiCoder +13pp | 44.8% → 57.7% Qwen2.5-Coder-7B | VERIFIED-SCHOLAR | PASS |
| phi-1 50.6% HumanEval | 1.3B parameters | VERIFIED-SCHOLAR | PASS |
| The Stack Python ~12.96M files | ~49.7GB | MEDIUM confidence | PASS |
| StarCoder 40% HumanEval | 15.5B parameters | VERIFIED-SCHOLAR | PASS |
| Dataset used | codeparrot-clean-valid | codeparrot fallback confirmed | PASS (paper states correctly) |

### FATAL Issues - Accuracy

None.

### MAJOR Issues - Accuracy

**MAJOR-A1: Numerical inconsistency in Section 5.1 Figure 1 caption vs. table.**

Section 5.1 table text reads: "The pattern rate (3.1%) meets the threshold; the executable rate (0.1%) falls **30×** below it." This contradicts the paper's own primary finding of a **31×** gap stated in the Abstract, Introduction (Section 1.1), and Section 1.4. The ratio 3.1% / 0.1% = 31 (not 30). The figure caption says "31× collapse" (correct). This inconsistency, though appearing minor, will be caught by any careful reviewer and undermines confidence in numerical precision throughout.

- Location: Section 5.1, paragraph after Table (Figure 1 description): "falls 30× below it"
- Fix: Change "30×" to "31×" to match the paper's own primary finding everywhere else.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract — would I continue? | BORDERLINE | The finding is clear and the number (1 in 1,000) is concrete. But the abstract front-loads a negative result and closes with "future work." A reviewer picking the accept pile may move on. |
| Introduction — am I hooked? | YES | Section 1.2 does well: framing prior work's untested assumption is compelling. Section 1.4 contributions are crisp. |
| Figure 1 reference — self-explanatory? | UNCLEAR | The paper describes Figure 1 as `gate_metrics_comparison.png` but the figure is not embedded in the markdown. Whether Figure 1 is self-explanatory cannot be verified from the paper text alone. The caption adequately describes what should be shown. |
| Results — meaningful improvements? | PARTIAL | The finding (0.1%) is meaningful. But Section 5.2 (H-E1: Pending) is a placeholder. Reviewers are reading a half-experiment. |

**Attention Lost At:** Section 5.2 — "The SFT training experiment is designed and pending execution." At this point a bored reviewer may close the paper. The entire H-E1 subsection contributes nothing beyond a design summary and a speculative expected outcome range.

### FATAL Issues - Engagement

None.

### MAJOR Issues - Engagement

**MAJOR-E1: Scope is a negative feasibility result with no executed SFT experiment.**

The paper's title and abstract promise insight about "Feasibility of Execution-Filtered SFT Data Curation," but the SFT half (H-E1) is explicitly pending. A reviewer will reasonably ask: "What does this paper contribute beyond a frequency count of doctests in one corpus?" The finding (0.1% executable rate) is real and useful, but as a standalone workshop finding it sits at an unusual scope level for ICML — it is a measurement study, not a training study.

The paper partially defends this (Section 6.2 L2, Abstract last sentence) but does not make a strong enough case in the venue framing. The Section 5.2 "Expected outcome" speculation (2-5pp HumanEval improvement) adds unverified content that a skeptical reviewer will mark as unfounded promise.

- Risk: MAJOR rejection reason — "insufficient experimental validation"
- Mitigation options: (a) Reframe as a workshop/findings paper; (b) Execute H-E1 before submission; (c) Strengthen the pipeline contribution framing as the primary contribution and relegate H-E1 design to an appendix

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Assessment |
|-------|------------|
| "First empirical characterization of Python doctest executability at corpus scale" (Section 1.4, Contribution 1) | OVERSTATED — The Stack paper (Kocetkov et al., 2022) performed compile() validity analysis on 10,000 sampled Python files. While they did not characterize doctest executability specifically, the methodology (10K sample, three-phase) is not categorically novel. The "first to" framing is plausible but fragile under review. |
| "No prior work performed a controlled comparison of unfiltered vs. compile-only vs. doctest-passing SFT filtering on a raw Python corpus at equal token budget" (Section 1.2) | ACCURATE — This specific controlled comparison has not been done. This is the legitimate novelty. |
| "validated three-phase pipeline" and "validated compile-only pipeline is production-ready" (Section 6.3) | OVERCLAIM — "Production-ready" is not justified by 28 unit tests on a 10,000-file sample with a fallback dataset. |

### Baseline Fairness Audit

| Baseline | Assessment |
|----------|------------|
| EffiCoder comparison | FAIR — explicitly noted as instruction-tuning pairs, not raw corpus |
| phi-1 comparison | FAIR — explicitly noted as GPT-4 curated, not execution-gated |
| StarCoder comparison | FAIR — heuristic-only, correctly positioned |
| Summary table (Section 2.5) | FAIR — "Yes (planned)" for Equal Budget accurately flags H-E1 as planned |

### Tone Assessment

Section 6.1 uses "The practical recommendation is clear" and Section 6.3 states "The validated compile-only pipeline is production-ready." These phrases are disproportionate to the evidence: the entire SFT quality benefit of compile-only filtering is undemonstrated. The paper correctly notes H-E1 is pending, but these phrases assert practical utility that has not been empirically established for the SFT use case.

Section 5.2 presents a speculative "expected outcome" (2-5pp HumanEval improvement) citing phi-1 and EffiCoder as "precedents" — but these operate in different regimes (GPT-4 curation vs. compile() syntax gate; instruction tuning vs. raw corpus). The analogy is weak and the presented range carries false precision.

### FATAL Issues - Credibility

None.

### MAJOR Issues - Credibility

**MAJOR-C1: "First" novelty claim is fragile and should be weakened.**

Contribution 1 in Section 1.4 claims "First empirical characterization of Python doctest executability at corpus scale." While likely true for the specific three-phase doctest characterization, the word "First" is an invitation for a reviewer to find any prior study that measured doctest rates in Python repositories (e.g., studies of documentation quality, doctest adoption in OSS projects). The claim should be scoped more precisely: "First measurement of the gap between doctest pattern prevalence and subprocess executability in a curated code LLM corpus."

- Location: Section 1.4, Contribution 1; also Abstract ("We document this finding through a systematic three-phase feasibility scan")
- Fix: Replace "First empirical characterization" with more precisely scoped novelty language

**MAJOR-C2: Compile-only SFT benefit is presented as near-established when it is entirely unverified.**

The paper presents compile-only filtering as "the practical recommendation" (Section 6.1) and the pipeline as "production-ready" (Section 6.3) without any SFT training evidence. The extrapolation from phi-1 (GPT-4 textbook curation) and EffiCoder (execution-selected instruction tuning) to compile-only syntax filtering on raw corpus code is a leap of approximately two regime changes. A skeptical reviewer will note:

1. phi-1's quality signal was semantic (GPT-4 judged content quality), not syntactic (compile() tests syntax only)
2. EffiCoder's execution signal was functional (test cases passed), not syntactic
3. Compile() filters syntactically broken code, but The Stack's heuristic filters already remove much of this
4. The actual marginal benefit of compile() over The Stack's existing heuristics is unknown

The paper acknowledges H-E1 is pending but does not acknowledge that the expected benefit could be zero or negative.

- Location: Section 6.1 "The practical recommendation is clear"; Section 6.3 "production-ready"; Section 5.2 "Expected outcome: 2-5pp"
- Fix: Reframe Section 6.1 to say "compile-only filtering is *feasible* as a quality gate" (not that the recommendation is *clear*). Remove or caveat the "production-ready" claim. Add a sentence acknowledging the improvement could be negligible if heuristic filters already remove most syntactically invalid files.

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| Abstract, line 1 | "Only 1 in 1,000" — cleaner to write "fewer than 1 in 1,000" since 10/10,000 = exactly 0.1%, but 0.1% = 1 in 1,000 exactly. Fine as is, but verify the arithmetic matches the "31×" claim: 3.1% / 0.1% = 31, not 10×. | Clarity |
| Section 2.5 Table | Column header "Equal Budget" — the "Yes (planned)" entry for "This work" is honest but a reviewer may circle this as the crux of scope concern | Framing |
| Section 3.4 Gate Evaluation table | "SCOPE: 1.0–3.0%" — the paper uses "scope_threshold=0.01" in gate code (per 04_validation.md) but the table shows "1.0–3.0%". The lower bound of SCOPE should be 1.0%, which matches, but the gate_satisfied check uses 0.01 (1%) as scope_threshold. Consistent. | Verify |
| Section 5.1 | "import_error | Dominant (~95%)" — the ~95% figure appears nowhere in ground_truth.yaml or 04_validation.md with a specific number. This should be cited or footnoted. | Unsupported value |
| Section 5.3 | "ruling out file size as a confound" — this is a strong inference from a distribution plot. The sample of executable files (n=10) is too small for statistical power. This sentence should be softened. | Overclaim |
| References | [Kocetkov et al., 2022] is listed as UNVERIFIED in citations. Should be verified before submission. | Citation |
| References | [Hui et al., 2024] is listed as UNVERIFIED. Should be verified before submission. | Citation |
| Section 3.3 | Phase B code snippet — `return True` at end is logically clear but the function context is missing; could confuse readers unfamiliar with the codebase structure. Consider adding a one-line comment. | Minor clarity |
| Section 6.2 L2 | "supported by theoretical precedent (phi-1, EffiCoder)" — these are empirical precedents, not theoretical. | Word choice |
| Figure 4 description | "Import errors dominate, confirming third-party dependency isolation as the primary failure mode" — "confirming" implies the hypothesis was independently verified. Should be "consistent with" since import errors were the predicted cause. | Epistemic precision |

---

## Summary for Revision Agent

### Priority Fix List

1. **[MAJOR-A1]** Fix "30×" to "31×" in Section 5.1 Figure 1 description paragraph (trivial fix, high credibility impact)

2. **[MAJOR-E1]** Reframe the paper's scope in Abstract and Introduction. Options:
   - Add explicit statement that H-C1 is the primary contribution and H-E1 is designated future work with experimental design provided for reproducibility
   - OR remove Section 5.2's speculative "expected outcome" range entirely (it adds hype without evidence)
   - The paper needs a clearer contract with the reader about what is claimed vs. planned

3. **[MAJOR-C1]** Scope the "First empirical characterization" claim more precisely:
   - Current: "First empirical characterization of Python doctest executability at corpus scale"
   - Suggested: "First systematic measurement of the gap between `>>>` pattern prevalence and subprocess executability in a curated Python code corpus used for LLM training"

4. **[MAJOR-C2]** Recalibrate compile-only benefit language:
   - Remove "The practical recommendation is clear" from Section 6.1 — replace with "compile-only filtering is *feasible* at scale and avoids the import isolation problem"
   - Remove "production-ready" from Section 6.3
   - Add explicit acknowledgment that H-E1 could find negligible marginal improvement if The Stack's heuristic filters already exclude most syntactically invalid files

5. **[Human Review]** Verify or remove the "~95%" import error fraction in Section 5.1 — either cite the source (04_validation.md error type distribution) with an actual percentage or soften to "large majority"

6. **[Human Review]** Soften Section 5.3 "ruling out file size as a confound" given n=10 executable files

7. **[Human Review]** Verify citations for Kocetkov et al., 2022 and Hui et al., 2024 via Semantic Scholar before submission

### Key Concerns

1. **Scope mismatch with ICML**: A paper whose SFT experiment is pending is at best a workshop paper or findings note. The strongest version of the argument for full-paper scope requires either executing H-E1 or repositioning the pipeline as the primary contribution with more implementation detail.

2. **Speculative expected outcome harms credibility**: Section 5.2's 2-5pp prediction invites a reviewer to ask "why not just run the experiment?" The answer (future work) is correct, but presenting a confident numerical prediction without evidence looks like undisciplined optimism.

3. **Dataset discrepancy (AT5 from ground truth)**: results.json records `"dataset": "bigcode/the-stack-dedup"` but the actual scan used `codeparrot/codeparrot-clean-valid`. The paper addresses this correctly in Section 3.2 and Limitations, but if a reviewer examines the released artifacts, the discrepancy in results.json could raise a reproducibility concern. Consider adding a note to results.json or the README explaining this.

### What's Working

- The core finding (31× gap, 0.1% executable rate) is clearly measured, consistently reported, and the numbers are internally consistent throughout the paper.
- Limitations section is unusually honest: L1, L2, L3 are all present and adequately disclosed.
- The three-phase methodology is well-described with enough implementation detail for reproducibility.
- The Summary Table in Section 2.5 positions prior work fairly and the "Yes (planned)" flag is appropriately honest.
- The abstract is concrete and the "1 in 1,000" framing is memorable.
- The gate framework (PASS/SCOPE/PIVOT) is a clean contribution that prevents post-hoc rationalization.
