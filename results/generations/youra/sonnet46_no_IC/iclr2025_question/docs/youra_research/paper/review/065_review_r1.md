# Adversarial Review - Round 1

**Paper:** Depth-Resolved Logit-Lens Uncertainty Signals for Hallucination Detection: Training-Free Evidence and a Protocol-Internal Validity Anchor
**Reviewed:** 2026-08-05T11:50:00+00:00
**Reviewer:** Adversary Agent (v2 — Accuracy Checker / Bored Reviewer / Skeptical Expert)
**Round:** R1 (focus: accuracy + engagement)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 1 | 3 | CRITICAL |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 0 | 2 | NEEDS_WORK |
| **TOTAL** | **1** | **6** | **CRITICAL** |

**Recommendation:** MAJOR_REVISION

The paper is unusually honest about its evidence tier and its numbers almost all reconcile exactly against the authoritative gate grid. But it contains one hard internal contradiction — a headline contribution count ("adj. KL best in half of our cells") refuted by the paper's own Table 1 — plus a cost claim ("zero inference cost, single-pass") contradicted by the paper's own protocol description, and several smaller count/terminology errors that a careful reviewer will catch from the results table alone.

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Summary

Cross-checked against `065_ground_truth.yaml` and the authoritative gate grid in `h-e1-v2/04_validation.md`.

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| Per-cell intermediate AUROC (Table 1: 0.6522 / 0.7011 / 0.6092 / 0.6570 / 0.6868 / 0.6213) | as listed | identical (gate grid) | ✓ |
| Per-cell final-layer entropy AUROC (0.5928 / 0.6669 / 0.5447 / 0.6048 / 0.5566 / 0.6178) | as listed | identical | ✓ |
| AUROC range (Abstract 0.61–0.70; body 0.6092–0.7011) | as listed | 0.6092–0.7011 | ✓ |
| Depth margins (+0.059/+0.034/+0.064/+0.052/+0.130/+0.0035) | as listed | identical (arithmetic verified) | ✓ |
| Gate margins "+0.059 to +0.151" (§5.1) | as listed | +0.059 to +0.151 | ✓ |
| depth_beats_final | 6/6 | 6/6 | ✓ |
| Selected layers/signals per cell (Table 1) | L31 adj_kl / L29 entropy / L31 maxprob / L31 adj_kl / L28 entropy / L31 maxprob | identical | ✓ |
| **adj_kl best-signal cell count** | **"three of six cells" (§5.3); "half of our cells" (Intro C3, §2, §7)** | **2/6 per gate grid AND per the paper's own Table 1** | **✗** |
| **"winning signal differs across datasets in 4 of 6 cells" (§3.4, §5.3)** | 4/6 | **6/6 by signal identity; 4/6 holds only for the winning *layer* (Mistral: L31 both datasets)** | **✗** |
| Degeneracy screen retained layers | 20/15/15, health ≥5 | 20/15/15 | ✓ |
| Scale | 5,451 scored generations, 1,817/model, ~2.5 GPU-h for 5 fresh cells, zero-GPU donor cell | identical | ✓ |
| Splits | 50/50 stratified, seed 42, 500/500 TriviaQA, 408/409 TruthfulQA, test locked never read | identical | ✓ |
| Anchor forensics | 0.5186 ref; 0.5928 selection / 0.5739 full; Δ+0.0742; tol 0.03; 47 s halt; ~2.5 h budget; 6 protocol differences | identical | ✓ |
| A2-v2 | 5/5 clauses, donor identity 10/10, direction consistency 4/6 descriptive, zero spurious halts | identical | ✓ |
| Both direction inconsistencies on never-code-verified cells (§5.4) | claimed | ✓ (v1 code-verified only llama2/triviaqa; inconsistent cells were llama2/truthfulqa and llama3/triviaqa) | ✓ |
| FEPoID skyline | 0.73–0.85, cited not re-run | identical | ✓ |
| Tests / reality check | 37/37, REAL_MODEL | identical | ✓ |
| Winners' layer band | "every winner sits at L28–L31, four of six at L31" | verified against Table 1 | ✓ |

**Ground-truth-file note for the Revision Agent:** `065_ground_truth.yaml` is itself internally inconsistent on the adj_kl count — its `secondary_metrics` and claims-audit text say "3/6" but list only two cells, while its own `per_cell` table and the authoritative gate grid (`h-e1-v2/04_validation.md`) both show adj_kl selected in exactly **2** of 6 cells (llama2/triviaqa, mistral/truthfulqa). Fix the paper toward 2/6, not toward the ground-truth typo.

### FATAL Issues - Accuracy

#### FATAL-ACC-001: "adj. KL best signal in half of our cells" is contradicted by the paper's own Table 1 (actual: 2/6)

**Location:** Introduction (contribution 3), Section 2 ("Cross-layer shift" paragraph), Section 5.3 (first sentence), Section 7 (Conclusion, paragraph 1)
**Issue:** The paper repeatedly claims adjacent-layer KL is the best signal in 3/6 cells ("half"). Table 1 shows adj_kl selected in exactly 2 cells (LLaMA-2/TriviaQA, Mistral/TruthfulQA); entropy wins 2 (LLaMA-2/TruthfulQA, LLaMA-3/TriviaQA) and max-prob wins 2 (Mistral/TriviaQA, LLaMA-3/TruthfulQA) — a perfectly even 2/2/2 split.
**Evidence:**
- §5.3: "Adjacent-layer KL ... is the best signal in three of six cells, entropy and max-probability splitting the rest." — vs. Table 1 (own paper): adj. KL appears in exactly 2 rows. Authoritative gate grid (`h-e1-v2/04_validation.md`, Metrics table) confirms 2/6.
- Intro contribution 3: "it is the best signal in half of our cells."
- §2: "where it turns out to be the best signal in half of our cells."
- §7: "the best signal in half the cells."
**Impact:** This is a contribution-level quantitative claim, repeated in four sections, that any reviewer can refute in seconds by counting rows in the paper's own results table. Once caught, it poisons trust in every other number. It also inflates the paper's self-declared "most novel observation."
**Required Fix:** Change every occurrence to the correct count: adj_kl is the best signal in **two of six cells** (with entropy and max-probability each also best in two — an even three-way split). The genuinely strong supporting facts survive unchanged and should carry the claim instead: the top three intermediate scores in LLaMA-2/TriviaQA are all adj_kl (0.6522 / 0.6145 / 0.6062), and adj_kl has no detection-time precedent. Rephrase contribution 3 accordingly (e.g., "best signal in two of six cells and the top-three sweep in the binding cell").

### MAJOR Issues - Accuracy

#### MAJOR-ACC-001: "Winning signal differs across datasets in 4 of 6 cells" — actual is 6/6 by signal; 4/6 is true only of the winning layer

**Location:** Section 3.4 ("the winning signal differs across datasets in 4 of 6 cells"); Section 5.3 ("the winning signal differs across datasets within the same model in four of six cells")
**Issue:** Per Table 1, the winning *signal* differs between the two datasets for **all three** models (adj_kl vs entropy; maxprob vs adj_kl; entropy vs maxprob) — i.e., 6/6 cells, not 4/6. The 4/6 figure is only correct for the winning *layer* (Mistral selects L31 on both datasets; LLaMA-2 differs 31 vs 29, LLaMA-3 differs 28 vs 31) or for signal *family* (width vs revision, same family only for LLaMA-3).
**Evidence:** Table 1 rows vs. §3.4/§5.3 text. Gate grid in `h-e1-v2/04_validation.md` confirms.
**Suggested Fix:** State the stronger, correct fact: "the winning signal differs across datasets for every model (and the winning layer differs for two of three)" — this actually *strengthens* the argument for per-cell (layer, signal, direction) selection. If the intended statistic was family-level (entropy-family vs KL), say so explicitly.

#### MAJOR-ACC-002: "Single-pass, zero inference cost, free byproducts of a forward pass the deployment already runs" is contradicted by the paper's own protocol (a second, teacher-forced forward pass is required)

**Location:** Abstract ("training-free, single-pass, and adds zero inference cost"); Introduction §1 ("in a single greedy pass"); Section 2 ("our statistics are free byproducts of a forward pass the deployment already runs"); Section 6 Broader impact ("at zero additional inference cost")
**Issue:** Methodology-vs-claim contradiction. §3.1: "For each example we run the single greedy generation, **then one teacher-forced re-forward** over the prompt and generated answer with hidden states exposed." §4.4 and Algorithm 1 (lines 3–4) repeat this. The measured protocol therefore costs one full extra forward pass over prompt+answer beyond the generation itself — not zero, and not literally single-pass. The Related Work sentence is the sharpest overstatement: the deployment does *not* already run a teacher-forced re-forward with all hidden states exposed.
**Evidence:** Quotes above; ground truth methodology and the six protocol differences ("generation-time entropy vs teacher-forced lens entropy") confirm the re-forward is constitutive of the current protocol, not incidental.
**Suggested Fix:** Qualify everywhere: e.g., "no sampling and no training; one greedy pass plus one teacher-forced re-forward (roughly 2× the monitored pass, versus ~10× for multi-sample methods)." If the authors believe hidden states could be captured during generation itself to make the cost truly zero, state that explicitly as an engineering option that was *not* what was measured. Do not leave "zero inference cost" in the Abstract as-is.

#### MAJOR-ACC-003: "Prior run" is used for two different runs with incompatible protocols, producing an apparent self-contradiction

**Location:** Section 3.1 vs Section 5.4 (also Intro ¶2 vs §4.4)
**Issue:** §3.1 asserts "prompts, decoding, and label rules are inherited verbatim from **the prior run** in this program, so the label protocol is a controlled variable." But §5.4 documents that "the prior-run record" protocol used a *bare prompt* and *substring labels* — two of the six differences from the current protocol. These are two different referents: (i) the archived v1-record run that produced 0.5186 / 0.66 / 0.52 (protocol-different), and (ii) the immediately preceding h-e1 run whose finalized cache was donor-reused (protocol-identical). The paper never distinguishes them, so §3.1 and §5.4 read as directly contradictory: labels cannot be both "inherited verbatim from the prior run" and "substring vs normalized-alias different from the prior run."
**Evidence:** §3.1 quote above; §5.4: "bare vs. templated prompt, substring vs. normalized-alias labels ..."; Intro ¶2 cites 0.66/0.52 as "a prior run of this research program"; §4.4 "reproduced from the prior run's finalized cache."
**Suggested Fix:** Introduce two distinct named referents once (e.g., "the archived motivating record" vs "the immediately preceding sweep whose cache we reuse") and use them consistently in §1, §3.1, §4.4, and §5.4.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Problem (architecture-fragile signals), approach (read before calibration), concrete numbers (0.61–0.70, 6/6), and honest scope in ~160 words. Strong. |
| Problem clear in 1 min? | ✓ | Fragility example (0.66 vs ~0.52 inverted) lands in paragraph 2; the "why care" (10× sampling or per-model probes) is explicit. |
| Novelty clear in 2 min? | ✓ | Four contributions stated at end of Intro; the gap sentence ("never been evaluated as hallucination-detection scores") is unambiguous. |
| Figure 1 self-explanatory? | ✓ | The entropy heatmap plus caption conveys the core intuition (groups separate at intermediate depth). Note: the narrative blueprint's coherence check certified "Figure 1" against `gate_metrics_bar.png`, which is Figure 4 in the assembled paper — the intuition figure works, but the headline 6/6 grid arrives only at §5.1. |
| Would continue reading? | ✓ | The dual-finding hook (models + measurement) is genuinely engaging; sections pull forward. |

**Attention Lost At:** Section 4.4 (momentarily — pipeline-internal QA jargon; see MAJOR-ENG-001). Attention recovers at §5.

### FATAL Issues - Engagement

None.

### MAJOR Issues - Engagement

#### MAJOR-ENG-001: Internal research-pipeline artifacts leak into the paper's prose and break the frame of a self-contained publication

**Location:** Section 4.4; Discussion (limitation 1); Conclusion; scattered ("this program")
**Issue:** The paper repeatedly speaks in the vocabulary of its own automation pipeline rather than to an external reader:
- §4.4: "The implementation passes 37/37 tests and a REAL_MODEL reality check confirming that reported numbers derive from actual model forwards rather than fixtures" — an ICML reviewer does not know what a "REAL_MODEL reality check" is, and the assurance that numbers are not fixtures raises the very doubt it tries to settle.
- §4.4: "the sweep survived three session interruptions without losing more than the in-flight example" — lab-notebook detail with no scientific content for the reader.
- Discussion limitation 1 / Conclusion: "is the original rescue claim" — the term "rescue claim" is used before it is ever defined (limitation 3 only partially explains the "rescue" framing after limitation 1 has already used it); an outside reader cannot resolve it.
- "this program" / "staged verification design whose first tier..." recurs as if the reader knows the program's tier structure.
**Reader Impact:** A busy reviewer reads these as either (a) machine-generated provenance leakage or (b) an internal tech report dressed as a paper — both reduce perceived venue-readiness and, in an anonymized submission, needlessly reveal process details.
**Required Fix:** Rewrite §4.4's verification sentence in standard reproducibility language (e.g., "the implementation is covered by an automated test suite, and we verified end-to-end that reported statistics derive from live model forward passes"); delete the session-interruption anecdote (the resumable-cache design sentence in §3.5 already covers auditability); define "rescue" once at first use or replace with "the original test-split confirmation claim"; replace "this program" with a reader-facing phrase ("a prior study in this research line").

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Prior Work |
|-------|----------|-----------|------------|
| "the first AUROC evaluation of raw per-layer logit-lens uncertainty statistics as training-free, single-pass hallucination scores" | Intro contribution 1 | ✓ (within the paper's own citation set) | Ali et al. 2025 (Entropy-Lens) computes the identical statistic but never evaluates detection; Kim et al. 2025 measures a different quantity (single-token probability trajectories, tuned lens, multiple-choice) and the paper handles the boundary explicitly in §2. No contradicting prior work found in the bib or ground truth. |
| Adjacent-layer KL "emerges as a first-time detection signal" / "the first detection-time use of inter-layer belief revision" | Abstract; §5.3; Conclusion | ✓ (consistent with cited DoLa/END/SLED, all decoding-time only) | §5.3 hedges "to our knowledge"; the Abstract and Conclusion state it unhedged — recommend propagating the hedge (see Human Review Notes). |
| "a junction that, to our knowledge, has never been connected without supervision" | Intro, final paragraph | ✓ | Properly hedged. |
| "Protocol-internal validity anchoring" as methodological contribution | Intro contribution 4; §3.5 | ✓ | Framed as a design contribution, not a priority claim. |
| "best signal in half of our cells" (quantitative clause of contribution 3) | Intro; §2; §5.3; §7 | ✗ | Not a prior-work issue — refuted by the paper's own Table 1 (2/6). See FATAL-ACC-001. |

**False novelty claims:** 0 (the one failed claim above is a numerical error, not a priority overclaim).

### Baseline Fairness Audit

| Baseline | Our Number | Literature | Fair? |
|----------|------------|------------|-------|
| Within-sweep final-layer entropy (L32, same pass/labels/split) | 0.5928 / 0.6669 / 0.5447 / 0.6048 / 0.5566 / 0.6178 | n/a (protocol-internal by design) | ✓ — same protocol by construction; matches gate grid exactly |
| FEPoID supervised skyline | cited only, "roughly 0.73–0.85" | 0.73–0.85 (Wang et al. 2026, as recorded in ground truth) | ✓ — correctly cited, explicitly not re-run, explicitly conceded superior |
| v1-record final-layer entropy (0.5186; 0.66/0.52 fragility example) | motivating context / forensics subject only | n/a | ✓ — never used as a same-protocol baseline (banned-phrasing check passed) |
| External detectors (Semantic Entropy, INSIDE, probes) | described qualitatively, no numbers claimed against them | n/a | ✓ — no unfair numeric comparison made |

**Unfair baselines:** 0. However, the *absence* of any evaluation beyond the paper's own sweep is the paper's largest exposure — see MAJOR-CRED-001.

### FATAL Issues - Credibility

None.

### MAJOR Issues - Credibility

#### MAJOR-CRED-001: The paper repeatedly advertises the decisive follow-up (test-split evaluation) as a zero-GPU computation on already-published caches — and then does not perform it

**Location:** Introduction ¶6 ("The locked test splits exist and were never touched"); Discussion limitation 1 ("freezing the six published tuples and evaluating the locked test splits with a paired bootstrap is a zero-GPU computation on the released caches"); Conclusion ("The follow-ups that matter most cost zero GPU from the published caches")
**Issue:** The selection-split-only scope is honestly and repeatedly disclosed (verified against ground truth `known_soft_spots`), and within the staged-verification design the omission has an internal rationale (the confirmation tier never executed). But the paper *itself* establishes that the confirmatory experiment costs nothing to run. A skeptical reviewer's first question will be: "If the test-split evaluation is free, why is it not in this paper?" — and the available answers (staging discipline) will read as either process rigidity or as a shield for unfavorable unreported results. The current justification ("the existence tier was designed as a precondition") explains the pipeline, not the paper.
**Evidence:** Quotes above; ground truth confirms h-m1/h-m2 (test-split claims) are BLOCKED/never-ran and correctly not claimed.
**Suggested Fix:** Either (a) add one or two sentences giving a *scientific* (not procedural) rationale for keeping the test split sealed at publication time — e.g., pre-registration discipline: the test split remains strictly untouched by every analysis decision *including the writing of this paper*, so the confirmatory study's guarantees are uncontaminated — and state that explicitly where the limitation is discussed; or (b) acknowledge head-on that this is the single most important unexecuted experiment and frame the paper explicitly as the pre-registered stage-1 report. What must not remain is the current pattern of advertising the follow-up's zero cost three times without addressing why it was not spent.

#### MAJOR-CRED-002: Implicit statistical claims ("margins large relative to plausible sampling noise / plausible CI widths") without any computed statistic, in a paper that elsewhere disclaims all statistical testing

**Location:** Section 5.1 ("margins large relative to plausible sampling noise at n = 408–500 even without the confidence intervals we did not compute"); Discussion limitation 2 ("margins large relative to plausible CI widths at these sample sizes")
**Issue:** These sentences do statistical work — asserting the gate margins would survive uncertainty quantification — without computing anything, while §4.5 states "the existence tier pre-registers no statistical test" and the paper (correctly) never claims significance. A reviewer will note that the bootstrap machinery is, by the paper's own account, "implemented and runs on cached data" at zero GPU, making the uncomputed-CI assertion doubly awkward: the claim is probably true (AUROC SE at n≈500 is roughly 0.02–0.03, and +0.059–+0.151 clears that), but the paper asks for credit it declined to earn.
**Evidence:** Quotes above; ground truth `confidence_intervals: "NONE computed"`, `statistical_significance.method: "NONE"`.
**Suggested Fix:** Either compute the (self-declared free) bootstrap CIs on the existence-gate quantities and cite them, or soften both sentences to pure point-estimate language (e.g., "the gate margins are an order of magnitude larger than the thinnest depth margin, but we make no distributional claim"). Do not keep quantitative noise comparisons that rest on no computation.

---

## Part 4: Human Review Notes

> These are minor issues for human review during final polish.
> NOT fixed by Revision Agent.

| Location | Note | Type |
|----------|------|------|
| References / 06_references.bib (`Chi2025Know`) | Cited as arXiv 2025 but DOI `10.18653/v1/2026.findings-acl.34` indicates Findings of ACL 2026; bib comment flags it PARTIAL. Resolve venue/year at camera-ready. | formatting |
| References (`Chi, C. S.`) | Author "Cheang Seng Chi" — verify surname ordering/abbreviation ("Chi, C. S." vs "Cheang, S. C.") against the published record. | formatting |
| Discussion, limitation 1 vs 3 | "the original rescue claim" is used (limitation 1) before the rescue framing is explained (limitation 3). If MAJOR-ENG-001's fix defines the term at first use, reorder is unnecessary. | clarity |
| Abstract | "adjacent-layer KL emerges as a first-time detection signal" — add the "to our knowledge" hedge used in §5.3, for consistency of the priority claim. | style |
| Front matter | `word_count: 6528` vs assembled sections 6533 — trivial metadata drift. | formatting |
| Figures / blueprint | Blueprint coherence check certified the "Figure 1 test" against `gate_metrics_bar.png` (Figure 4 in the paper); consider whether the headline 6/6 grid should appear earlier, though the current Figure 1 (entropy heatmap) works as intuition. | style |
| Sections vs assembled paper | Only difference is figure path prefix (`../figures/` in sections vs `figures/` in 06_paper.md) — correct for each file's location; no action needed, noted for the record. | formatting |

---

## Verification Log

| # | Tool | Pattern / Path | Found |
|---|------|----------------|-------|
| 1 | Read | `paper/065_ground_truth.yaml` (full) | Ground truth metrics, forensics, claims audit; internal inconsistency: adj_kl "3/6" text vs per_cell table showing 2/6 |
| 2 | Read | `verification_state.yaml` lines 1–600, 1485–1548 (spam region skipped per instruction) | Gate history (h-e1 PARTIAL → h-e1-v2 PASS), Phase 5 skipped by config, paper_writing outputs |
| 3 | Read | `paper/06_paper.md` (full) | Full paper text for all cross-checks |
| 4 | Read | `h-e1-v2/04_validation.md` | Authoritative gate grid: 6-cell AUROCs, signals (adj_kl ×2), 20/15/15 screen, A2-v2 5/5, clause-c 4/6 table |
| 5 | Read | `h-e1/04_validation.md` | Anchor forensics: 0.5186/0.5928/0.5739, Δ+0.0742, 47 s, 6 protocol differences, v1 code-verified cell identity |
| 6 | Read | `paper/06_narrative_blueprint.yaml`, `paper/06_references.bib` | Persuasiveness targets; 18/19 bib entries verified, Chi2025Know PARTIAL, nostalgebraist blog UNVERIFIED |
| 7 | Grep | `"test-split AUROC"` in 06_paper.md + sections/ | 0 hits — banned phrasing absent ✓ |
| 8 | Grep | `-i "statistically significant"` in 06_paper.md + sections/ | 0 hits — banned phrasing absent ✓ |
| 9 | Grep | `"0.5186"` in 06_paper.md + sections/ | 11 hits, all motivating-context or forensics-subject usages; never a same-protocol baseline ✓ |
| 10 | Grep | `"first"` in 06_paper.md | Novelty-claim inventory for the audit table (Part 3) |
| 11 | Bash/python | Paragraph-containment check: every sections/*.md paragraph vs 06_paper.md | All paragraphs verbatim-identical except figure path prefixes (`../figures/` vs `figures/`) |
| 12 | Bash/python | Regex parse of Table 1 rows in 06_paper.md | Signal winners: adj_kl 2, entropy 2, maxprob 2 → basis for FATAL-ACC-001 and MAJOR-ACC-001 |
| 13 | Bash (ls) | `paper/figures/` | All 8 figure files referenced by the paper exist (incl. `h-e1_anchor_check_llama2_triviaqa.png`) |
| 14 | Read | `paper/figure_registry.yaml` | 16 registered figures; 8 used; Figure 7 correctly sourced from h-e1 (v1 breach visual) |

---

## Summary for Revision Agent

### Priority Fix List

1. **FATAL-ACC-001:** adj_kl best-signal count is 2/6, not 3/6 / "half" — fix in Intro contribution 3, §2, §5.3, §7; do NOT "fix" toward the ground-truth file's own 3/6 typo (authoritative gate grid and Table 1 both say 2/6) - MUST FIX
2. **MAJOR-ACC-002:** "single-pass / zero inference cost / free byproducts" vs the required teacher-forced re-forward — qualify in Abstract, Intro, §2, §6 - SHOULD FIX
3. **MAJOR-ACC-001:** "winning signal differs in 4 of 6 cells" — actual 6/6 by signal (4/6 only by layer); state the correct, stronger fact - SHOULD FIX
4. **MAJOR-ACC-003:** disambiguate the two "prior runs" (archived v1 record vs h-e1 donor run) in §1/§3.1/§4.4/§5.4 - SHOULD FIX
5. **MAJOR-CRED-001:** give a scientific rationale for the sealed test split, or reframe explicitly as a pre-registered stage-1 report - SHOULD FIX
6. **MAJOR-CRED-002:** compute the free bootstrap CIs or drop the "margins large relative to plausible noise/CI widths" assertions - SHOULD FIX
7. **MAJOR-ENG-001:** remove pipeline-internal jargon (REAL_MODEL, 37/37, session interruptions, undefined "rescue claim", "this program") - SHOULD FIX

### Key Concerns

- A headline contribution count ("half of our cells") is refuted by the paper's own Table 1 — the single most damaging reviewer catch available, and it propagated from a ground-truth typo, so the revision must anchor on the gate grid.
- The cost claim ("zero inference cost") is the paper's main selling point and is contradicted by its own §3.1/§4.4 protocol; left unfixed, it converts an honest paper into an overclaiming one.
- The withheld-but-free test-split evaluation is the question every reviewer will ask first; the paper currently answers with pipeline procedure rather than scientific rationale.

### What's Working

- Numerical fidelity is otherwise excellent: every AUROC, margin, split size, screen count, forensics number, and clause result reconciles exactly against the authoritative gate grid and ground truth.
- Scope honesty is genuinely strong and verified: selection-split / single-seed / no-CI flags appear in Abstract, Intro, §4, §5, Discussion, and Conclusion; all three banned phrasings are absent; the four known soft spots are each disclosed where claimed.
- The dual-finding narrative (depth signal + measurement validity) is engaging, the anchor-forensics section reads as a contribution rather than an excuse, and the reversed-prediction section (§5.5) models exactly the epistemic honesty reviewers reward.

