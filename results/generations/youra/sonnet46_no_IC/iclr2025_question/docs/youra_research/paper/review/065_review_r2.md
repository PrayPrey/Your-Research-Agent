# Adversarial Review - Round 2

**Paper:** Depth-Resolved Logit-Lens Uncertainty Signals for Hallucination Detection: Training-Free Evidence and a Protocol-Internal Validity Anchor
**Paper file:** `paper/06_paper_r1.md` (R1-revised version)
**Reviewed:** 2026-08-05T12:10:00+00:00
**Reviewer:** Adversary Agent (v2)
**Round:** R2 (focus: numerical verification + credibility; personas: Accuracy Checker + Skeptical Expert only)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 3 | NEEDS_WORK |
| Engagement | — | — | not in scope this round |
| Credibility | 0 | 0 | OK |
| **TOTAL** | **0** | **3** | NEEDS_WORK |

**Recommendation:** MINOR_REVISION

All seven R1 FATAL/MAJOR fixes landed and were re-verified against the raw Phase 4 artifacts (not just the ground-truth file). Every headline number — Table 1 AUROCs, all six depth margins, both gate margins, split sizes, generation counts, anchor forensics arithmetic, top-3 sweep, layer-band counts — reconciles exactly against `h-e1-v2/experiment_results.json`, `h-e1-v2/code/outputs/results.csv`, the per-example caches, and `h-e1/04_validation.md`. This round's raw-artifact audit found three residual numerical inaccuracies the R1 pass (which checked against the gate-grid summary and ground-truth file) could not have caught: the degeneracy-screen counts "20/15/15" are contradicted by the released per-cell artifacts (actual 20/20/15/16/15/16), the "~2.5 GPU-hours" compute figure is roughly double the logged sweep time and collides with the v1 *budget* figure quoted in §5.4, and the Abstract's "an order of magnitude below multi-sample methods" does not survive strict arithmetic on the paper's own 2x-vs-10x numbers. No FATAL issues; no mathematical impossibilities; no baseline-fairness issues; no new contradictions introduced by the R1 revision beyond the Abstract phrase noted.

---

## Part 1: Accuracy Check (Persona 1 — Numerical Verification)

### Ground Truth Verification Table

Sources: `h-e1-v2/experiment_results.json` (raw), `h-e1-v2/code/outputs/results.csv` (306-row AUROC grid), `h-e1-v2/results/cache_*.csv` + `meta_*.json` + `test_split_locked_*.json`, `h-e1-v2/04_validation.md`, `h-e1/04_validation.md`, `h-e1-v2/code/constants.py`, `h-e1-v2/code/experiment.log`, `045_validated_hypothesis.md`, `065_ground_truth.yaml`.

| Claim | Paper | Source file value | Match |
|-------|-------|-------------------|-------|
| Intermediate AUROC, llama2/triviaqa (L31 adj_kl) | 0.6522 | 0.65216345 (experiment_results.json) | ✓ |
| Intermediate AUROC, llama2/truthfulqa (L29 entropy) | 0.7011 | 0.70109661 | ✓ |
| Intermediate AUROC, mistral/triviaqa (L31 maxprob) | 0.6092 | 0.60915706 | ✓ |
| Intermediate AUROC, mistral/truthfulqa (L31 adj_kl) | 0.6570 | 0.65697127 | ✓ |
| Intermediate AUROC, llama3/triviaqa (L28 entropy) | 0.6868 | 0.68682393 | ✓ |
| Intermediate AUROC, llama3/truthfulqa (L31 maxprob) | 0.6213 | 0.62126643 | ✓ |
| Final-layer entropy AUROCs (Table 1 col 4) | 0.5928/0.6669/0.5447/0.6048/0.5566/0.6178 | 0.59281898/0.66694517/0.54473250/0.60480452/0.55663122/0.61775687 | ✓ |
| Depth margins (Table 1, recomputed per cell) | +0.059/+0.034/+0.064/+0.052/+0.130/+0.0035 | 0.0593/0.0342/0.0644/0.0522/0.1302/0.0035 (recomputed from raw grid) | ✓ |
| Depth-margin range (Intro) | "+0.0035 to +0.130" | min 0.0035, max 0.1302 | ✓ |
| Gate margins (§5.1, §6) | "+0.059 (Mistral/TriviaQA) to +0.151 (LLaMA-2/TruthfulQA)" | 0.6092−0.55=0.0592; 0.7011−0.55=0.1511 | ✓ |
| Abstract rounding vs body | 0.61–0.70 vs 0.6092–0.7011 | consistent rounding | ✓ |
| "thinnest gate margin an order of magnitude larger than thinnest depth margin" (§5.1) | claimed | 0.0592 / 0.0035 = 16.9x — ≥10x holds | ✓ |
| "five of six margins exceed 0.03" (§5.2, §6) | 5/6 | 0.0342, 0.0522, 0.0593, 0.0644, 0.1302 > 0.03; 0.0035 not | ✓ |
| adj_kl best-signal count (Intro C3, §2, §5.3, §7) | 2/6, even 2/2/2 three-way split | raw grid argmax: adj_kl 2, entropy 2, maxprob 2 | ✓ |
| Winning signal differs across datasets "for every model" (§3.4, §5.3) | 3/3 models | adj_kl↔entropy; maxprob↔adj_kl; entropy↔maxprob | ✓ |
| Winning layer differs "for two of the three" (§3.4, §5.3) | 2/3 | llama2 L31↔L29 differ; mistral L31=L31 same; llama3 L28↔L31 differ | ✓ |
| Top-3 llama2/triviaqa intermediates all adj_kl (§5.3) | L31 0.6522, L17 0.6145, L30 0.6062 | results.csv sorted: (31,adj_kl) 0.6522, (17,adj_kl) 0.6145, (30,adj_kl) 0.6062; 4th is (16,maxprob) 0.5909 | ✓ |
| Winners' layer band (§5.1, §7) | all L28–L31, four of six at L31 | L31,L29,L31,L31,L28,L31 — 4 at L31 | ✓ |
| Scale | 5,451 generations; 1,817/model; 1000+817=1817 | caches: 1000+817 rows/model x 3 = 5,451; 1817x3=5451 | ✓ |
| Splits | 500/500 TriviaQA; 408/409 TruthfulQA (selection/test); test locked | cache split column: 500/500 and 408 selection/409 test; 6 `test_split_locked_*.json` present (test_idx 500/409) | ✓ |
| "+0.0035 on 408 selection examples" (§5.2) | 408 | meta_llama3_truthfulqa.json n_selection=408 | ✓ |
| Degeneracy screen counts (§3.3, Fig. 2 caption) | 20 / "15 each" | **per-cell raw: llama2 20/20, mistral 15/16, llama3 15/16** (experiment_results.json retained_layers; corroborated by 306 = (20+20+15+16+15+16)x3 rows in results.csv) | ✗ (MAJOR-ACC-001) |
| Screen health gate | ≥5 retained per model | min retained 15 ≥ 5 (holds under either count) | ✓ |
| Anchor reference | 0.5186 | constants.py H_E1_REFERENCES llama2/triviaqa = 0.5186 | ✓ |
| Anchor observed | 0.5928 selection / 0.5739 full set | h-e1/04_validation.md: 0.5928 (Δ+0.0742) / 0.5739 (Δ+0.0553) | ✓ |
| Deviation arithmetic | +0.0742 vs 0.03 tolerance | 0.5928−0.5186=0.0742; tolerance ±0.03 (BASELINE_TOLERANCE=0.03) | ✓ |
| Abstract rounding "moved a reference baseline from 0.52 to 0.59" | 0.52→0.59 | 0.5186→0.5928 | ✓ |
| Halt timing | 47 seconds; "~2.5-hour GPU campaign" (budget, §5.4) | h-e1: "Duration 47 s"; "stopped ... after 47 s instead of ~2.5 h" | ✓ |
| Six protocol differences (§1, §5.4) | sample/prompt/labels/signal/precision/split | h-e1 forensics: identical six items | ✓ |
| Motivating record 0.66 (LLaMA-3) / ~0.52 inverted (LLaMA-2) (§1) | 0.66 / ~0.52 | H_E1_REFERENCES llama3/triviaqa 0.6583; llama2/triviaqa 0.5186; V1_DIRECTION_RECORD llama2 flipped=True | ✓ |
| Direction consistency 4/6, both inconsistencies on never-code-verified cells (§5.4) | 4/6 | h-e1-v2 clause-c table: inconsistent = llama2/truthfulqa, llama3/triviaqa; h-e1 record code-verified only llama2/triviaqa | ✓ |
| Zero spurious halts; "passed all five clauses" (§5.4) | 5/5 | h-e1-v2 gate: 5/5 criteria PASS; experiment.log exit=0, no halt (see Human Review Note on "clauses" wording) | ✓ |
| Donor identity check | 10/10 | h-e1-v2 gate A2-v2(a): 10/10; log "donor cache reused, 1000 rows copied, 0 full-sweep GPU calls" | ✓ |
| Test suite | "37 tests, all passing" | h-e1-v2: 37/37 | ✓ |
| Fresh-cell compute (§4.4) | "~2.5 GPU-hours" | **h-e1-v2/04_validation.md: "~1h 15m GPU sweep"; experiment.log 09:00:23→10:14:59 (~75 min incl. analysis+figures); meta elapsed_s sum 2,645 s (final chain)** | ✗ (MAJOR-ACC-002) |
| Cost claim, Abstract | "roughly twice the monitored pass and an order of magnitude below multi-sample methods" | 2x total vs ~10x total = 5x, not 10x (10x holds only on the extra-cost reading: 1 extra pass vs ~10 extra) | ✗ (MAJOR-ACC-003) |
| TruthfulQA final-layer range (§5.2) | 0.6048–0.6669 | 0.6048, 0.6178, 0.6669 | ✓ |
| TriviaQA final-layer range (§5.2) | 0.54–0.59 | 0.5447, 0.5566, 0.5928 | ✓ |
| §5.5 TriviaQA margin ordering | llama3 +0.130 > mistral +0.064 > llama2 +0.059 | matches raw grid and 045 §mechanism step 3 | ✓ |
| FEPoID skyline | "roughly 0.73–0.85", cited not re-run | ground truth + 045 literature table: 0.73–0.85, not re-run | ✓ |
| Phase 5 / external baselines | "No external baselines were re-executed" (§4.3) | verification state: Phase 5 SKIPPED by config | ✓ |

### FATAL Issues - Accuracy

None.

### MAJOR Issues - Accuracy

#### MAJOR-ACC-001 (R2): Degeneracy-screen counts "20/15/15" are contradicted by the released raw artifacts — the screen is per-cell and retains 20/20/15/16/15/16

**Location:** Section 3.3 ("The screen retained 20 layers on LLaMA-2-7B and 15 each on Mistral-7B-v0.1 and LLaMA-3-8B-Instruct (Figure 2)"); Figure 2 caption ("20/15/15 retained").
**Issue:** `h-e1-v2/experiment_results.json` records per-cell `retained_layers`: llama2 20 (both datasets), mistral 15 (TriviaQA) / **16** (TruthfulQA), llama3 15 (TriviaQA) / **16** (TruthfulQA). The AUROC grid `code/outputs/results.csv` has exactly 306 rows = (20+20+15+16+15+16) x 3 signals — arithmetic proof that the screen ran per cell, not per model, and that "15 each" is wrong for both TruthfulQA cells. `analysis.py` confirms per-cell application (`build_auroc_grid(cache_df, retained_layers)` on the selection split of each cell; `screen_healthy` checks every cell's list). The 20/15/15 summary originated in `h-e1-v2/04_validation.md` and propagated through `045_validated_hypothesis.md` and `065_ground_truth.yaml` — which is why R1's check (against those summaries) passed it.
**Evidence:** Raw JSON retained_layers arrays (mistral/truthfulqa: L17–L32 = 16; llama3/truthfulqa: L17–L32 = 16) vs. the quoted §3.3 sentence and Figure 2 caption.
**Impact:** No gate or claim is affected (health gate ≥5 holds by a wide margin either way), but the paper releases the caches and grid it is contradicted by; a reviewer who counts rows in the released grid refutes a Methods sentence and a figure caption in one step — precisely the failure mode FATAL-ACC-001 exhibited in R1. It also mischaracterizes the screen's granularity (per model vs. per model x dataset).
**Required Fix:** State the per-cell truth: e.g., "The screen, applied per model x dataset on the selection split, retained 20 layers on LLaMA-2 (both datasets), 15/16 on Mistral, and 15/16 on LLaMA-3 (TriviaQA/TruthfulQA)"; fix the Figure 2 caption accordingly. Also correct `065_ground_truth.yaml` (`degeneracy screen retained layers`) so R3 does not re-inherit the summary's error.

#### MAJOR-ACC-002 (R2): "~2.5 GPU-hours" for the five fresh cells is roughly double the logged compute and collides with the v1 budget figure the paper quotes two sections later

**Location:** Section 4.4 ("the remaining five cells were generated fresh (~2.5 GPU-hours)").
**Issue:** The pipeline's own records put the fresh sweep at ~1h15m of GPU: `h-e1-v2/04_validation.md` states "~1h 15m GPU sweep across interrupted-and-resumed chain"; `experiment.log` spans 09:00:23→10:14:59 (~75 min wall on one H100, including analysis and figure generation); the final-chain `meta_*.json` `elapsed_s` sum to 2,645 s. The ~2.5-hour figure is the **v1 budget** — h-e1's forensics ("stopped the campaign after 47 s instead of ~2.5 h of GPU sweeps"), which the paper itself quotes in §5.4 as "what was budgeted as a ~2.5-hour GPU campaign". §4.4 presents the same number as the *actual measured* cost of the v2 sweep. The error also lives in `065_ground_truth.yaml` (`hardware: "single H100, ~2.5 GPU-hours for 5 fresh cells"`), which is why it survived R1; the raw logs are unambiguous.
**Evidence:** Quotes and log timestamps above. 2.5 h ≈ 2x the ~1.25 h actual.
**Impact:** Misreported compute in a paper whose central selling point is cost. The direction is conservative (overstates own cost), but it is checkable, and the reuse of the identical "~2.5 h" number for both the v1 *budget* (§5.4) and the v2 *actual* (§4.4) reads as conflation once noticed.
**Required Fix:** §4.4: report the measured figure (e.g., "~1.25 GPU-hours on a single H100 for the five fresh cells; the LLaMA-2/TriviaQA cell cost zero GPU via the verified donor cache"). Keep "~2.5-hour" only in §5.4 where it correctly denotes the v1 budget. Correct `065_ground_truth.yaml` `methodology.training_details.hardware`.

#### MAJOR-ACC-003 (R2): Abstract's "an order of magnitude below multi-sample methods" fails strict arithmetic on the paper's own numbers (2x vs ~10x is 5x)

**Location:** Abstract, final sentence ("one greedy generation plus one teacher-forced re-forward, roughly twice the monitored pass and an order of magnitude below multi-sample methods").
**Issue:** By the paper's own accounting, the method costs ~2x the monitored pass and multi-sample methods cost ~10x (§1: "roughly ten forward passes per query"; §2: "roughly twice the monitored pass, against the tenfold cost above"). 10/2 = 5x — not an order of magnitude. The claim is defensible only on the *additional*-cost reading (1 extra pass vs ~10 extra passes), which is the framing §6 correctly uses ("roughly one extra forward pass ... far below the tenfold cost"), but the Abstract sentence anchors on total cost ("roughly twice the monitored pass and...") and then switches basis mid-clause. This is residue of the R1 MAJOR-ACC-002 rewrite: the overclaim shrank from "zero inference cost" to a 2x-inflated ratio, in the paper's most-read section.
**Evidence:** Quoted Abstract sentence vs. §1/§2/§6 quantities.
**Suggested Fix:** One clause: either "...roughly twice the monitored pass, a fifth of the cost of multi-sample methods" or "...one extra forward pass per monitored generation, an order of magnitude less added inference than multi-sample methods". Any variant that keeps a single cost basis is fine.

---

## Part 2: Engagement Check (Persona 2)

Not in scope for R2 (Accuracy Checker + Skeptical Expert only, per round configuration). R1's engagement verdict stands; the MAJOR-ENG-001 fixes were verified as landed (see Part 3.5 below).

---

## Part 3: Credibility Check (Persona 3 — Skeptical Expert)

### Novelty Claims Audit

| Claim | Location | Verified? | Prior Work |
|-------|----------|-----------|------------|
| First AUROC evaluation of raw per-layer logit-lens uncertainty statistics as training-free, sampling-free hallucination scores | Intro C1 | ✓ (within the paper's citation set; unchanged from R1) | Ali et al. 2025 computes the statistic, never detection; Kim et al. 2025 boundary handled explicitly in §2 |
| Adjacent-layer KL "first-time detection signal" / "first detection-time use of inter-layer belief revision" | Abstract; §5.3; §7 | ✓ (consistent with cited DoLa/END/SLED, decoding-time only) | §5.3 hedges "to our knowledge"; Abstract and Conclusion still unhedged — carried Human Review Note |
| "best signal in two of our six cells — an even three-way split" | Intro C3; §2; §5.3; §7 | ✓ — R1's FATAL-ACC-001 fix verified against raw grid (2/2/2) | n/a |
| "a junction that, to our knowledge, has never been connected without supervision" | Intro | ✓ | properly hedged |

**False novelty claims:** 0.

### Baseline Fairness Audit

| Baseline | Our Number | Literature | Fair? |
|----------|------------|------------|-------|
| Within-sweep final-layer L32 entropy (same pass/labels/split, per cell) | 0.5928/0.6669/0.5447/0.6048/0.5566/0.6178 | n/a (protocol-internal by design) | ✓ — matches raw grid exactly; §4.3 gives a substantive rationale (anchor forensics) for why this is the only within-protocol comparison, and records final-layer max-prob alongside |
| FEPoID supervised skyline | cited only, "roughly 0.73–0.85" | 0.73–0.85 (Wang et al. 2026, per ground truth) | ✓ — explicitly "cited as a skyline but not re-run", explicitly conceded superior, resource-class difference stated |
| v1-record numbers (0.5186; 0.66/0.52) | motivating context / forensics subject only | n/a | ✓ — never used as same-protocol baselines; §3.1/§5.4 keep the two runs distinct after the R1 fix |
| External detectors (Semantic Entropy, INSIDE, probes) | qualitative only | n/a | ✓ — no numeric comparison implied; §4.3: "No external baselines were re-executed" matches Phase-5-skipped config |

**Baseline fairness issues:** 0. The within-sweep-only baseline is honestly framed as a consequence of the forensics, the FEPoID skyline concession is explicit, and nothing implies external baselines were re-run.

### Signal-performance-gap audit (claims vs. 0.61–0.70 selection-split AUROCs)

- "Class-separable" is used strictly as AUROC-above-gate on the selection split, flagged as such in Abstract, §1, §4, §5.1, §6, §7. ✓
- "Beats the final layer in every cell" is everywhere qualified as point estimates; the +0.0035 cell is explicitly counted "direction-consistent rather than as evidence" (§5.2). ✓
- Residual implicit statistical claims after the R1 MAJOR-CRED-002 fix: none found. The two former "large relative to plausible noise/CI widths" sentences are now pure point-estimate comparisons; the one quantitative comparison retained ("order of magnitude larger than the thinnest depth margin", §5.1) verifies arithmetically (16.9x). ✓
- Mechanism language stays capped at "consistent with"; §5.5 reports the reversed prediction descriptively. ✓

### FATAL Issues - Credibility

None.

### MAJOR Issues - Credibility

None this round. (The Abstract cost phrase is filed under Accuracy as MAJOR-ACC-003.)

### 3.5 R1 Fix Verification (regression check)

| R1 issue | Fix landed? | Evidence (R1 paper) | New contradiction? |
|----------|-------------|---------------------|--------------------|
| FATAL-ACC-001 (adj_kl "half"/3/6 → 2/6) | ✓ | Greps for "half of our cells", "half the cells", "3/6": 0 hits. "two of (our/the) six cells" + "even three-way split" in Intro C3, §2, §5.3, §7 — all verified correct vs raw grid | None |
| MAJOR-ACC-001 (signal differs 4/6 → 6/6) | ✓ | §3.4 and §5.3: "winning signal differs across datasets for every model, and the winning layer for two of the three" — both counts verified vs Table 1 and raw grid | None |
| MAJOR-ACC-002 (zero cost / single-pass) | ✓ (with residue) | Greps "zero inference", "zero additional", "free byproduct": 0 hits. Sole remaining "single-pass" describes Kossen et al.'s probes (correct usage). New consistent 2x framing in Abstract/§2/§3.1/§6; §3.1 adds the honest "measured cost, not in-principle" sentence | MAJOR-ACC-003: the replacement Abstract clause "an order of magnitude below multi-sample methods" is a smaller overclaim of the same family |
| MAJOR-ACC-003 (two "prior runs" conflated) | ✓ | "Motivating record" vs "immediately preceding sweep" defined at first use (§1, §3.1) and used consistently in §4.4, §5.4; §3.1 now states the two are distinct and never conflated | None |
| MAJOR-CRED-001 (free-but-unrun test split) | ✓ | Intro ¶6 pre-registration rationale; Discussion limitation 1 "sealed at publication for a scientific reason ... stage-one report of that pre-registered design"; Conclusion mirrors it | None |
| MAJOR-CRED-002 (implicit noise claims) | ✓ | Both sentences now pure point-estimate language; retained comparison verifies (16.9x ≥ 10x) | None |
| MAJOR-ENG-001 (pipeline jargon) | ✓ | Greps "REAL_MODEL", "interruption", "this program": 0 hits; "rescue" appears once, defined inline with quotes at limitation 3; §4.4 uses standard reproducibility language ("automated test suite (37 tests, all passing) ... live forward passes") | None |

**R1 fixes verified: 7/7 landed.** One residue (Abstract cost ratio) filed as MAJOR-ACC-003.

---

## Part 4: Human Review Notes

> Minor issues for human final polish. NOT for the Revision Agent.

| Location | Note | Type |
|----------|------|------|
| Abstract | "adjacent-layer KL emerges as a first-time detection signal" and Conclusion's "the first detection-time use" remain unhedged while §5.3 says "to our knowledge" — propagate the hedge (carried from R1) | style |
| Abstract | "beats the final layer's own entropy readout in every cell" — accurate as point estimates, but consider signaling the thinnest margin (+0.0035) the way §5.2 does; optional | clarity |
| §5.4 | "passed all five clauses" — §3.5 defines three lettered clauses (a)–(c); the "five" are the five gate criteria (existence, a, b, screen health, c). Say "all five gate criteria" or "all three clauses plus both health checks" | clarity |
| Front matter | `word_count: 6822` vs ~7,300–7,400 by whitespace count over the body incl. references/captions — metadata drift, method-dependent | formatting |
| References (`Chi2025Know`) | Venue/year ambiguity (arXiv 2025 vs Findings ACL 2026 DOI) and author-name ordering — carried from R1, unchanged; resolve at camera-ready | formatting |

---

## Verification Log

Every search/read performed this round (mandatory numerical-verification log). Serena find_file/search_for_pattern/list_dir unavailable in this build; Grep/Glob/Read/Bash used as equivalents.

| # | Tool | Pattern / Path | Result |
|---|------|----------------|--------|
| 1 | Read | `bmad-custom-src/.../adversary-agent-v2.md` | Agent definition, personas, output format |
| 2 | Read | `paper/06_paper_r1.md` (full) | R1-revised paper text for all cross-checks |
| 3 | Read | `paper/review/065_review_r1.md` (full) | R1 findings + fix list to re-verify |
| 4 | Read | `paper/065_ground_truth.yaml` (full) | GT values incl. corrected adj_kl 2/6 note; GT's screen-count and GPU-hours entries later found stale vs raw artifacts |
| 5 | Read | `h-e1-v2/04_validation.md` (full) | Authoritative gate grid; "~1h 15m GPU sweep"; 20/15/15 summary (source of propagated screen-count error); clause-c 4/6 table |
| 6 | Bash (ls) | `h-e1-v2/results/`, `h-e1-v2/code/outputs/` | 6 caches, 6 metas, 6 locked-test-split JSONs, 6 reports, results.csv present |
| 7 | Read | `h-e1-v2/experiment_results.json` (full) | Raw per-cell gate values + retained_layers arrays (20/20/15/16/15/16) |
| 8 | Bash (wc/head) | `results/cache_*.csv`, `code/outputs/results.csv` | 1001/818 lines per cache (headers) → 1000+817 rows/model = 1817 x 3 = 5451 ✓; grid CSV 306 data rows |
| 9 | Read | `h-e1/04_validation.md` (full) | Anchor forensics: 0.5186 ref, 0.5928/0.5739 observed, Δ+0.0742/+0.0553, 47 s halt, ~2.5 h budget, 6 protocol differences, top-5 adj_kl list, v1 code-verified cell = llama2/triviaqa only |
| 10 | Grep | `half of our cells\|half the cells\|3/6\|zero inference\|zero additional\|free byproduct\|single-pass\|single pass\|2/6\|two of (our )?six\|two of the six` in 06_paper_r1.md | 0 regression hits; all "two of six" occurrences correct; sole "single-pass" is Kossen et al. description |
| 11 | Bash (python) | Parse `code/outputs/results.csv` + `experiment_results.json` + caches: recompute per-cell argmax, depth margins, gate margins, top-5 llama2/triviaqa, retained counts, split sizes, cache split column | Table 1 fully reconciled; margins/gate margins exact; top-3 all adj_kl confirmed; retained per cell 20/20/15/16/15/16; splits 500/500 and 408 sel/409 test |
| 12 | Bash | `results/meta_*.json` key scan + `code/experiment.log` head/grep/tail | Log: start 09:00:23, resumed 09:37:33, complete 10:14:59 (exit=0, no halt); donor cell "0 full-sweep GPU calls" |
| 13 | Bash (python) | Sum `elapsed_s` across meta_*.json | 2,645 s (0.73 h) final-chain; corroborates ~1h15m total GPU sweep, refutes "~2.5 GPU-hours" |
| 14 | Grep | `2\.5 GPU\|GPU-hour\|20/15/15\|retained\|0\.66\|0\.52` in `045_validated_hypothesis.md` | 045 propagates 20/15/15 per-model summary; no independent 2.5-GPU-hours source in 045; 3/6 typo origin visible at line 136 |
| 15 | Grep | `GPU` in 045; `0\.66\|0\.5186\|REFERENCE\|DIRECTION` in `h-e1*/code/constants.py`; `motivating` in 045 | Located H_E1_REFERENCES + V1_DIRECTION_RECORD |
| 16 | Read | `h-e1-v2/code/constants.py` (full) | 0.5186 ref; llama3/triviaqa 0.6583 → "0.66" motivating claim ✓; llama2 flipped=True → "inverted direction" ✓; tolerance 0.03; gate 0.55; screen constants 0.01/0.05; TRIVIAQA_N 1000, TRUTHFULQA_N 817 |
| 17 | Bash (grep/python) | Count `![` figures; whitespace word count of paper body | 8 figures ✓ front matter; word count ~7,379 vs metadata 6822 (note) |
| 18 | Grep | `REAL_MODEL\|interruption\|rescue\|this program\|order of magnitude` in 06_paper_r1.md | ENG fixes landed; "order of magnitude" occurrences audited → MAJOR-ACC-003 (Abstract) and verified-correct §5.1 usage |
| 19 | Grep | `def degeneracy_screen\|retained\|per.cell\|selection` in `h-e1-v2/code/analysis.py` | Screen applied per cell on selection split; `screen_healthy` checks all cells' retained lists — confirms per-cell granularity for MAJOR-ACC-001 |

Searches/reads performed: 19 (several multi-file).

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-ACC-001 (R2):** §3.3 + Figure 2 caption screen counts → per-cell truth 20/20 (llama2), 15/16 (mistral), 15/16 (llama3); also correct `065_ground_truth.yaml` — SHOULD FIX
2. **MAJOR-ACC-002 (R2):** §4.4 "~2.5 GPU-hours" → measured ~1.25 GPU-hours (~75 min) for the five fresh cells; keep "~2.5 h" only as the v1 budget in §5.4; also correct `065_ground_truth.yaml` — SHOULD FIX
3. **MAJOR-ACC-003 (R2):** Abstract cost clause → single cost basis (e.g., "a fifth of the cost of multi-sample methods" or "an order of magnitude less *added* inference") — SHOULD FIX

### Key Concerns

- Both remaining hard-number errors (screen counts, GPU-hours) propagated from Phase-4/4.5 summary documents into `065_ground_truth.yaml`; the raw artifacts (`experiment_results.json`, `results.csv`, `experiment.log`, `meta_*.json`) are the only reliable arbiters, and the ground-truth file needs the two corrections noted above before R3 gate-checks against it.
- The Abstract's cost sentence is the last residue of the R1 "zero cost" overclaim family; a one-clause edit closes it.

### What's Working

- All seven R1 FATAL/MAJOR fixes landed cleanly, with zero regressions in the fixed claims themselves; the 2/6, 6/6-signal, two-referent, pre-registration, and point-estimate rewrites are all correct against raw data.
- Headline numerics are now airtight at the raw-artifact level: every Table 1 value, margin, gate margin, split size, generation count, forensics delta, and layer-band count recomputes exactly from `experiment_results.json` / `results.csv` / caches.
- Baseline framing is fair and self-consistent: within-sweep-only comparisons with a stated forensic rationale, an explicitly conceded supervised skyline, and no implied external re-runs (consistent with Phase 5 being skipped).

