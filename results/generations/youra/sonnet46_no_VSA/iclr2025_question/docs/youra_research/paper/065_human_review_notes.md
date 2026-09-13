# Human Review Notes — Phase 6.5 MINOR Issues

These issues were identified during adversarial review but not auto-fixed.
They require human judgment before Phase 6.5.1 (Overleaf compilation).

---

## MINOR-1: "Bidirectional NLI" Ambiguity

**Location:** Methodology Section 3.1, Experiments Section 4.2
**Issue:** The term "bidirectional NLI entailment" using `cross-encoder/nli-deberta-v3-small` may be read as a single bidirectional model pass. In practice, bidirectional means two separate calls: NLI(A→B) and NLI(B→A). Both must return ENTAIL for two samples to be in the same cluster.
**Suggested fix:** Add "(two asymmetric NLI calls per pair: A→B and B→A, both must return ENTAIL)" inline in Section 3.1.

---

## MINOR-2: Gabriel (2026) Timeline

**Location:** Introduction, Related Work 2.2, Results 5.4, References
**Issue:** Gabriel, M. (2026) arXiv:2605.05166 is dated 2026. If this paper targets ICML 2025, this reference would post-date the conference. The paper format header says "ICML2025."
**Options:**
- If the submission date is actually 2026 (ICML 2026 or later) — no change needed.
- If ICML 2025 — either remove Gabriel (2026) or add a note that it is concurrent/future work.
**Suggested action:** Clarify intended submission venue and year; adjust citation or format accordingly.

---

## MINOR-3: "Late-Position Tokens" Mechanism Claim

**Location:** Results Section 5.4, Introduction paragraph 4
**Issue:** The paper claims "late-position tokens where factual information is concentrated" as a mechanistic explanation for why min_logprob decorrelates from SE. This is a reasonable hypothesis but is not verified in this work (would require token position analysis).
**Suggested fix:** Hedge with "plausibly" or "consistent with the hypothesis that factual information is concentrated at late token positions" rather than stating it as an established fact.

---

## MINOR-4: LM-Judge Calibration

**Location:** Experiments Section 4.2, Discussion Section 6.2
**Issue:** The judge calibration (34.8% correct for Llama-3.1-8B on TriviaQA closed-book) is plausible but validated only through the circularity check, not against an independent correctness signal (e.g., exact string match against TriviaQA aliases without LM involvement). If the judge is miscalibrated, both the Spearman ρ and the partial R² are affected.
**Suggested fix:** Add a brief note in limitations that judge calibration is validated only through the circularity diagnostic, not against an independent ground truth.

---

## MINOR-5: LRT chi² Not Reported in Main Text

**Location:** Results Section 5.2, Table 5.2
**Issue:** The LRT chi²=1.632 (df=2) is in experiment_results.json and provides useful context (expected ~3.84 for p<0.05 at df=2) but is not reported in the main text — only p=0.442. Including chi² would allow readers to independently verify the p-value.
**Suggested fix:** Add LRT chi²=1.632 to the partial R² row in Table 5.2 or mention it in the text.
