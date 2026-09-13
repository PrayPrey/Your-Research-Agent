# Adversarial Review — Round 1

**Paper:** Contracts Catch What Tests Miss: Measuring Execution-Based Oracle Strength for LLM-Generated Code
**Reviewed:** 2026-08-03
**Reviewer:** Adversary Agent v2 (3-Persona)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 2 | Numbers verified; two framing inconsistencies |
| Engagement | 0 | 1 | Hook works; Table 4 misleads reader |
| Credibility | 0 | 3 | Two unverified citations; CVT scope under-disclosed; language overclaim |
| **TOTAL** | **0** | **6** | MAJOR_REVISION — revisable, no fatal blockers |

**Recommendation:** Major revision required on credibility and framing issues before submission. Core empirical work is solid and all numbers check out cleanly against ground truth.

---

## Part 1: Accuracy Check (Persona 1: Accuracy Checker)

### Ground Truth Verification Table

| Claim (Section) | Paper Value | Ground Truth | Match? | Notes |
|----------------|-------------|--------------|--------|-------|
| Oracle-isolation gap (Abs, Table 1) | 0.4012 | 0.4012 | ✅ | |
| 95% CI oracle gap (Table 1) | [0.358, 0.445] | [0.3576, 0.4451] | ✅ | Acceptable rounding |
| Wilcoxon p (Table 1) | 5.88e-38 | 5.88e-38 | ✅ | |
| CU mass (Table 1) | 0.4023 | 0.4023 | ✅ | |
| CU mass 95% CI lower (Table 1) | 0.360 | 0.3595 | ✅ | Acceptable rounding |
| CU mass 95% CI full (Results body) | [0.360, 0.447] | [0.3595, 0.4465] | ✅ | |
| n triples (Intro) | 10,432 | confirmed | ✅ | |
| Task coverage (Table 1) | 364/364 | confirmed | ✅ | |
| Adaptive contribution mean (Table 2) | 0.0999 | 0.0999 | ✅ | |
| Adaptive contribution p (Table 2) | 2.64e-22 | 2.64e-22 | ✅ | |
| Per-model range (Sec 5.2) | 0.099–0.103 | [0.0993, 0.1033] | ✅ | |
| 0.004 range claim (Sec 5.2) | 0.0040 | 0.0040 | ✅ | |
| 72.6% positive tasks (Table 2) | 257/354 | 257/354 | ✅ | |
| Spearman ρ (Table 3) | 0.136 | 0.136 | ✅ | |
| ρ p-value (Table 3) | 5.30e-03 | 5.30e-03 | ✅ | |
| Kendall τ (Table 4) | 0.40 | 0.40 | ✅ | |
| Permutation p (Table 4) | 0.4833 | 0.4833 | ✅ | |
| ΔR² (Table 4) | 0.0044 | 0.0044 | ✅ | |
| HumanEval+ gap (Sec 5.1) | 0.520 | 0.520 | ✅ | |
| MBPP+ gap (Sec 5.1) | 0.345 | 0.345 | ✅ | |
| Min p at n=5 (Sec 3.7) | ≈0.017 | confirmed structural | ✅ | |
| icontract-hypothesis compatibility (Sec 3.5) | 94.6% (17,226/18,200) | confirmed | ✅ | |
| ContractEval tasks split (Sec 4.1) | 117 + 247 = 364 | confirmed | ✅ | |
| Mean contract failure rate (Sec 5.1 body) | 0.997 | 0.9967 (h-m1 val.) | ✅ | Match with validation file |
| Mean differential failure rate (Sec 5.1 body) | 0.596 | 0.5955 (h-m1 val.) | ✅ | Match with validation file |
| h-e1: 62.6% ≥1 violation (Summary table) | 62.6% | denominator unclear | ⚠️ | Denominator not stated |

### FATAL Issues — Accuracy

None.

### MAJOR Issues — Accuracy

**[MAJOR-A1] Unaddressed ceiling effect: contract failure rate ≈ 0.997 on CVT inputs**

**Location:** Section 5.1 body, Figure 1 description

**Issue:** The mean contract failure rate is 0.997 on CVT inputs. This near-ceiling value — the contract oracle fires on essentially 100% of CVT inputs — is stated in the text but not addressed as a potential confound. The oracle-isolation gap = contract_rate − differential_rate = 0.997 − 0.596 = 0.401. If the contract oracle fires on essentially all CVT inputs by construction (CVT inputs are designed to trigger contract violations), then the contract oracle is not demonstrating *semantic discrimination* — it is functioning as a near-trivial acceptor of the input class. The paper must explicitly address: "Is the contract oracle a meaningful discriminator on CVT inputs, or does it near-trivially reject all of them?" The distinction matters because the CU mass (0.40) does show discrimination — 40% of programs pass the differential oracle while failing the contract oracle on the same CVT input, which is the meaningful finding. But the high contract rate needs a line of explicit explanation connecting these two quantities, or reviewers will raise this question as a methodological concern.

**Suggested Fix:** Add one sentence in Section 5.1 after reporting contract failure rate: "The near-unity contract failure rate (0.997) on CVT inputs is expected by construction — CVT inputs are specifically designed to trigger contract violations. The scientifically informative quantity is the CU mass (0.40): among the 40.2% of CVT evaluations where the LLM program returns the same output as the reference canonical (differential oracle: PASS), the contract oracle identifies 40% as semantically invalid."

---

**[MAJOR-A2] h-e1 summary table: 62.6% lacks explicit numerator/denominator**

**Location:** Results Section 5.4 summary table

**Issue:** The summary table reports "h-e1: 62.6% show ≥1 violation; mean max gap 0.471." The 62.6% figure lacks an explicit "X/364" statement. Working backward: 62.6% × 364 ≈ 228 tasks, but the paper elsewhere (Section 5.2 Table 2 row "Tasks with positive contribution") gives 257/354 (72.6%) for a different metric with a different denominator (354 ≠ 364). Without an explicit "228/364 tasks" or similar, this number is unverifiable and may confuse readers who conflate it with the 257/354 figure.

**Suggested Fix:** Change to "h-e1: 228/364 tasks show ≥1 violation (62.6%); mean max gap 0.471" — or whatever the correct numerator is. Confirm denominator is 364 (all tasks) not some subset.

---

## Part 2: Engagement Check (Persona 2: Bored Reviewer)

### Bored Reviewer Verdict

| Checkpoint | Pass? | Notes |
|-----------|-------|-------|
| Opening hook grabs attention | ✅ | "764 tests, still wrong 40% — if you ask a contract" is genuinely arresting |
| Hook payoff clear by paragraph 3 | ✅ | "The gap is this" paragraph delivers crisply |
| Contribution list is scannable | ✅ | Numbered 1–4, well-differentiated |
| Problem-solution flow | ✅ | Three-level framing (surface/deeper/gap) is effective |
| Results tables 1–3 self-explanatory | ✅ | Tables 1–2 are clean with threshold/status columns |
| Table 4 framing | ❌ | Three ❌ rows signal failure before prose explains the structural constraint |
| Figures described in text | ⚠️ | Figures are citation-only — "Figure 1 shows..." with no content description in text |
| Discussion adds insight | ✅ | Threshold-effect interpretation (§6.1) is the paper's strongest prose |
| Conclusion callback to hook | ✅ | Returns cleanly |

**Attention Lost At:** Table 4 (Section 5.4). A reader hits four Status rows, three of which show ❌ FAIL, and must read the following paragraph carefully to understand this is a deliberate null result with a structural justification, not a failed hypothesis test. The visual signal (three ❌) will cause a bored reviewer scanning tables to pre-judge the paper before reading the explanation.

### FATAL Issues — Engagement

None.

### MAJOR Issues — Engagement

**[MAJOR-E1] Table 4 Status column misleads before prose corrects**

**Location:** Section 5.4, Table 4

**Issue:** Table 4 uses the same ✅/❌ Status column format as Tables 1–3, where ✅ = good result and ❌ = failed result. In Tables 1–3, every ❌ would indicate a methodological problem. In Table 4, three ❌ rows indicate structural constraints that are *expected and informative*, not methodological failures. A reviewer scanning Tables 1–4 in sequence will register the pattern as "RQ4 fails" before reading the explanation.

**Suggested Fix:** Option A: Add a table header note — "Note: ❌ in this table indicates an underpowered structural constraint (n=5), not a hypothesis failure. ΔR²=0.004 is a genuine null finding." Option B: Rename the Status column for Table 4 to "Finding" with values "CONSISTENT" / "UNDERPOWERED" / "NULL" instead of ✅/❌ PASS/FAIL.

---

## Part 3: Credibility Check (Persona 3: Skeptical Expert)

### Novelty Claims Audit

| Claim | Section | Defensible? | Notes |
|-------|---------|-------------|-------|
| "first clean methodology for oracle-type comparison on any benchmark with formal contract annotations" | Contribution 1 | ✅ | ContractEval used Z3/SMT, not output-equality comparison; claim is appropriately scoped |
| "first study to compare differential and contract oracles on identical inputs" | Intro | ✅ | No counterexample found in related work; implicit in positioning |
| "100% tractability vs. 25.82% for Z3" | §2.3, §5 | ✅ | Concrete, verifiable, well-scoped |
| "model-invariant" adaptive PBT contribution | Abstract, §5.2, Conclusion | ⚠️ | 5 models, one benchmark — "model-consistent" is correct epistemic level |

### Baseline Fairness Audit

| Baseline | Fairness | Notes |
|---------|----------|-------|
| EvalPlus differential oracle (764 tests) | ✅ | Explicitly strongest test-based baseline |
| ContractEval Z3 SMT baseline | ✅ | Tractability limitation clearly acknowledged |
| Bose [Bose2025Prompts]: "no formal contract annotations" | ⚠️ | Table 2.4 lists Bose annotation as "Manual" — implies some annotation exists. "Formal (benchmark-provided)" vs. "Manual (researcher-authored)" distinction should be made explicit |
| CVT inputs as comparison set | ⚠️ | CVT inputs are purpose-selected to be maximally contract-violating. This inflates apparent contract oracle advantage. L1 limitation is present but disclosure should extend to the abstract (see MAJOR-C2) |

### FATAL Issues — Credibility

None.

### MAJOR Issues — Credibility

**[MAJOR-C1] Two [UNVERIFIED] citations present in live reference list**

**Location:** References section; Section 2.4

**Issue:** "OpenAI. Code Monitor: Hidden Correctness Check Analysis, 2026. [UNVERIFIED]" and "Liguori et al. Factors Explaining Code Correctness Variance in LLMs, 2026. [UNVERIFIED]" appear in the reference list with explicit [UNVERIFIED] tags. At any major venue (ICML, NeurIPS, ICLR), an unverifiable or fabricated citation triggers immediate credibility loss and may result in desk rejection for academic integrity. The [UNVERIFIED] tag is not a mitigation — it announces the problem. These citations must be verified before submission or removed entirely. The Section 2.4 claims that rely on them (52.9% figure; 83% variance explanation) must also be removed if the citations cannot be verified.

**Suggested Fix:** Remove both citations and their Section 2.4 paragraphs. The paper's core argument does not depend on either claim — the OpenAI Monitor claim is used for "external validation" that is not needed when the primary result (0.40 gap, p=5.88e-38) is already strong; the Liguori claim supports the ΔR²=0.004 finding which stands independently.

---

**[MAJOR-C2] CVT input scope qualifier absent from abstract**

**Location:** Abstract (two instances); Introduction hook sentence

**Issue:** The abstract states "programs returning the ground-truth output on contract-violating inputs nonetheless fail reference postconditions 40% of the time." The phrase "contract-violating inputs" is present but its significance is not clear to a general reader — CVT inputs are purpose-selected inputs that are maximally likely to trigger contract violations. The abstract's second clause about "40% contract-unique mass" similarly lacks this qualifier. The opening hook — "A program that outputs the correct answer on 764 tests is still wrong 40% of the time — if you ask a formal contract" — implies the 40% is measured on the 764-test inputs (or general inputs), when in fact it is measured on a completely different, purpose-selected input set. A careful reviewer will catch this and object that the hook is misleading.

**Suggested Fix:** Add "(on contract-violating test inputs)" after the first 40% mention in the abstract. Revise the hook sentence or add a one-clause qualifier: "on the inputs most relevant for contract evaluation — contract-violating test inputs — a program that outputs the correct answer is still wrong 40% of the time."

---

**[MAJOR-C3] "Model-invariant" language overclaims theoretical universality**

**Location:** Abstract (last sentence); Section 5.2 body; Conclusion

**Issue:** "model-invariant" as a theoretical term implies the property holds universally across all models. The paper tests 5 model families on 1 benchmark. The 0.004 range is empirically narrow and impressive, but "model-invariant" implies the finding would hold for GPT-4o, Gemini Ultra, Llama-70B, etc. — none of which were tested. The paper is otherwise careful about scope (L2: n=5 underpowering; L3: ContractEval scope), making this the one place where the language is disproportionate to the evidence.

**Suggested Fix:** Replace "model-invariant" with "model-consistent across tested families" or "uniform across all 5 tested model families" in all three locations.

---

## Part 4: Human Review Notes

*(Minor issues — NOT for Revision Agent auto-fix; collected for human final polish)*

| Location | Note | Type |
|----------|------|------|
| §3.4 vs §6.2 | "Precondition checks" in 3.4 but "postcondition-only analysis" in L4 — what is the actual pre/post breakdown in ContractEval? State explicitly. | clarity |
| §5.2 | "The most striking result of Experiment B" — oracle-isolation gap of 0.40 is the headline finding by most measures; this superlative creates emphasis confusion | style |
| §3.6 Tier table | Tier 2 BoolOp interpretation as input guard is asserted but not demonstrated; one linking sentence to preconditions would make the explanation falsifiable | clarity |
| §4.1 Table | Experiment B triples (17,226) vs Experiment A (10,432) — the discrepancy is unexplained; footnote on join condition needed | clarity |
| Frontmatter | word_count: ~6200 (header) vs ~4950 body text (stats block) — reconcile for camera ready | formatting |
| §1 Contribution 1 | "first clean methodology" — "clean" is informal; prefer "controlled" or "confound-free" | style |
| §1 (Intro) | Contributions section uses em-dash bullets within ordered list; minor formatting inconsistency | formatting |

---

## Summary for Revision Agent

### Priority Fix List (FATAL then MAJOR)

*No FATAL issues. Fix all MAJOR:*

1. **[MAJOR-C1] MUST FIX:** Remove or verify the two [UNVERIFIED] citations (OpenAI Code Monitor; Liguori et al.) before submission. If unverifiable, remove from reference list and excise the Section 2.4 paragraphs relying on them. No [UNVERIFIED] tags in submitted paper.

2. **[MAJOR-C2] MUST FIX:** Add CVT scope qualifier to abstract ("on contract-violating test inputs"). Revise or add a qualifier to the Introduction hook sentence so the 40% is not misread as a general-input finding.

3. **[MAJOR-A1] SHOULD FIX:** Add one sentence in Section 5.1 explicitly addressing the near-ceiling contract failure rate (0.997) and clarifying that the scientifically informative quantity is the CU mass (0.40), not the absolute contract rate. This pre-empts a methodological objection from reviewers.

4. **[MAJOR-C3] SHOULD FIX:** Replace "model-invariant" with "model-consistent across tested families" or equivalent in Abstract, Section 5.2, and Conclusion.

5. **[MAJOR-E1] SHOULD FIX:** Revise Table 4 Status column or add a pre-table note framing the cross-model experiment as an informative null with structural power constraint, not a failed test. Prevent visual ❌ misread.

6. **[MAJOR-A2] SHOULD FIX:** Add explicit numerator/denominator for h-e1 "62.6%" in summary table (state X/364 tasks).

### What's Working

- **Numbers are airtight.** Every verifiable claim matches ground truth. The empirical work will survive numerical scrutiny.
- **Oracle isolation design** is the genuine methodological contribution — clearly explained, reproducible, fills a real gap.
- **Hook and conclusion callback** work well. "764 tests, still wrong 40%" is memorable.
- **Negative results handled honestly.** ρ=0.136 and n=5 underpowering presented as principled negatives with structural explanations — reviewers who expect buried negatives will appreciate this.
- **Related work table (2.4)** makes positioning legible at a glance.
- **Limitations section (L1–L4)** is specific and complete.
- **Discussion threshold-effect interpretation** (§6.1, Finding 3) is the paper's strongest prose.
