# Human Review Notes — Round 1
# Paper: "Eviction-Aware LoRA: Training LoRA Adapters Under KV Cache Budget Constraints"
# Source: 065_review_r1.md Section 6 (HRN-1 through HRN-10)
# Date: 2026-05-04
# Status: Collected for author judgment — NOT auto-fixed in R1 revision

---

These items were flagged by the adversarial review as style, tone, and clarity improvements. They are recommended but not mandatory for submission. The revision agent has NOT applied these changes; they require author judgment on whether the suggested rewording preserves intended meaning.

---

## HRN-1 — Conclusion: "right kind" is vague

**Location:** Section 7 (Conclusion)

**Current text:**
> "We show that the intervention produces the right *kind* of change in adapter representations"

**Reviewer suggestion:**
Replace with more descriptive framing: "produces structurally distinct adapter representations"

**Author note:** "Right kind" intentionally echoes the paper's framing that mechanistic results confirm *preconditions* for accuracy gains. The suggested replacement is more precise but loses the connective link to the mechanistic precondition argument. Consider whether "structurally distinct adapter representations consistent with the mechanistic preconditions for accuracy improvement" better captures both.

---

## HRN-2 — Section 5.1: "striking" is evaluative

**Location:** Section 5.1, narrative paragraph after results table

**Current text (R1 revised):**
> "The mean cosine similarity of 0.053 is substantially lower than typical same-task LoRA similarity (>0.8 for different tasks; >0.95 for same-task different seeds)."

**Status:** Partially addressed in R1 — "striking" was replaced with the comparative framing suggested. No further action required unless author prefers different phrasing.

---

## HRN-3 — Abstract: closing on infrastructure is anticlimactic

**Location:** Abstract (final sentence)

**Current text (R1 revised):**
> "Full accuracy evaluation on LLaMA-2-7B and Mistral-7B-v0.1 is the immediate next step, supported by the validated BudgetSweepEvaluator and SpearmanAnalyzer infrastructure we provide."

**Reviewer suggestion:**
Close the abstract on the mechanistic implication rather than on infrastructure. Example alternative closing: "These mechanistic results establish that eviction-aware training creates the right representational conditions for accuracy recovery under KV cache constraints; full accuracy evaluation on LLaMA-2-7B and Mistral-7B-v0.1 is the immediate next step."

**Author note:** This is a structural choice. The current closing correctly orients readers toward the next step (H-M3). The reviewer's alternative is stronger for mechanistic framing but may underemphasize the infrastructure contribution. Consider the conference context — a workshop paper benefits from the mechanistic close; a full conference paper may want both.

---

## HRN-4 — Section 2.2: LongLoRA ghost citation

**Location:** Section 2.2 and References

**Status:** RESOLVED in R1 revision — LongLoRA is now discussed in Section 2.2 with explicit contrast to Eviction-Aware LoRA. No further action required.

---

## HRN-5 — Section 3.2.1: Algorithm 1 else-branch dead code

**Location:** Algorithm 1, Step 2, else branch

**Current text:**
```
else:
  return standard_attention(Q, K, V)
```

**Issue:** Section 3.2.2 states the hook is deregistered during inference. If true, the else branch is dead code that will never execute. This creates a minor technical inconsistency.

**Options:**
1. Remove the else branch and add a comment: `# hook is deregistered at inference; this branch not reached`
2. Keep the else branch as defensive code and add a comment explaining it
3. Reframe Section 3.2.2 to say the hook remains registered but the else branch handles non-training forward passes (e.g., during validation within training loop)

**Author note:** Option 3 may be most accurate if the hook is active during eval() calls within the training loop (e.g., `model.eval()` for loss logging). Clarify the exact lifecycle before fixing.

---

## HRN-6 — Section 6.1: Interpretation A vs B not linked to conclusion

**Location:** Section 6.1, Interpretation B discussion

**Status:** Partially addressed in R1 — Section 7 conclusion now explicitly states H-M3 will distinguish Interpretation A from Interpretation B. No further action required unless author wants the link also added to Section 6.1 directly.

---

## HRN-7 — Section 4.2: "multi-sentence" understates evaluation data

**Location:** Section 4.2, Evaluation Data (H-M1)

**Status:** Addressed in R1 — Section 4.2 now reads "Five synthetic multi-sentence samples (short sequences, not LongBench-length documents)" with explanation. No further action required unless author wants additional detail on approximate sequence lengths used.

---

## HRN-8 — Section 1 Contribution #3: "Critically" over-weights n=5 result

**Location:** Section 1, contribution #3

**Status:** Addressed in R1 — "Critically" was removed from contribution #3. No further action required.

---

## HRN-9 — Paper length: sparse at ~8 pages (now ~8.6 pages post-R1)

**Location:** Paper Statistics block / submission metadata

**Issue:** ICML 2025 main conference limit is 9 pages (content) + references. The paper is within limit. Reviewers may note the shorter-than-typical length.

**Author note:** The mechanistic study framing justifies the length — the paper reports two passed experiments, one scope limitation, and an infrastructure component. Padding to 9 pages would weaken the paper. Consider addressing this in the cover letter or camera-ready note if accepted. The R1 revision added ~380 words, bringing the paper to ~8.6 pages, which is a more comfortable length. No structural changes needed.

---

## HRN-10 — Section 2.4: Ben-David et al. domain adaptation analogy is informal

**Location:** Section 2.4 (Joint Optimization Perspective)

**Current text:**
> "the observation — implicit in the domain adaptation literature [Ben-David et al., 2010] — that models trained on a distribution P and evaluated on a different distribution Q suffer a performance penalty proportional to the divergence between P and Q"

**Issue:** The Ben-David et al. [2010] bound (ε(target) ≤ ε(source) + d_H(P,Q) + λ) applies formally to classifiers, not generative LLMs with attention mechanisms. Applying it to LLM attention distributions is informal.

**Options:**
1. Add qualifier: "While Ben-David et al.'s formal bound applies to classifiers, the intuition — that training-inference distribution divergence degrades performance — applies broadly."
2. Replace with a less formal citation or phrase the observation without the formal bound implication.
3. Keep as-is and accept that the analogy is informal/intuitive (common practice in related work sections).

**Author note:** Option 1 is the safest. Option 3 is acceptable given that Section 2.4 explicitly frames this as a "joint optimization perspective" rather than a formal theorem application. A skeptical reviewer who knows the Ben-David bound will appreciate the qualifier; most reviewers will not check.

---

## Summary

| ID | Location | Type | Status after R1 |
|----|----------|------|-----------------|
| HRN-1 | Section 7 | Style | Partially addressed; author judgment needed on final phrasing |
| HRN-2 | Section 5.1 | Tone | Addressed in R1 |
| HRN-3 | Abstract | Structure | Not changed; author judgment on closing sentence |
| HRN-4 | Section 2.2 | Consistency | Resolved in R1 |
| HRN-5 | Section 3.2.1 | Technical | Not changed; requires author to verify hook lifecycle |
| HRN-6 | Section 6.1 | Narrative | Addressed in R1 (conclusion link added) |
| HRN-7 | Section 4.2 | Clarity | Addressed in R1 |
| HRN-8 | Section 1 | Tone | Addressed in R1 |
| HRN-9 | Paper Stats | Meta | No change needed; length acceptable post-R1 |
| HRN-10 | Section 2.4 | Accuracy | Not changed; author judgment on formality level |

**Items requiring author action before final submission:** HRN-1, HRN-3, HRN-5, HRN-10

---

# Human Review Notes — Round 2
# Paper: "Eviction-Aware LoRA: Training LoRA Adapters Under KV Cache Budget Constraints"
# Source: 065_review_r2.md Section 9 (HRN-R2-1 through HRN-R2-6)
# Date: 2026-05-04
# Status: Collected for author judgment — NOT auto-fixed in R2 revision

---

These items were flagged by the R2 adversarial review as style, precision, and clarity improvements. They are recommended but not mandatory for submission. The revision agent has NOT applied these changes; they require author judgment.

---

## HRN-R2-1 — Section 5.1: "detection threshold" is unusual terminology

**Location:** Section 5.1, sentence: "all 24 LoRA layers diverging beyond the detection threshold"

**Issue:** "Detection threshold" is an unusual term for what is simply an experimental gate criterion (cosine similarity < 0.95). In signal processing, "detection threshold" has a specific technical meaning that does not apply here.

**Reviewer suggestion:** Replace "detection threshold" with "gate criterion (0.95)" or "divergence threshold (0.95)" for terminological precision.

**Type:** Terminology

---

## HRN-R2-2 — Section 4.3: No mention that SnapKV comparison was deferred

**Location:** Section 4.3 (Baselines)

**Issue:** SnapKV is discussed in related work (Section 2.1) as a comparable eviction method, but the baselines section does not explain why no SnapKV comparison appears in experiments. A reviewer may wonder why SnapKV is highlighted in related work but absent from experiments.

**Reviewer suggestion:** Add a single sentence noting that SnapKV comparison was deferred to future work alongside the H-M3 full-scale evaluation.

**Type:** Clarity

---

## HRN-R2-3 — Section 5.2 / Section 6.1: −0.0199 nats magnitude should be qualified as modest

**Location:** Section 5.2 (results) and Section 6.1 (discussion)

**Issue:** The paper reports "lower mean attention entropy (−0.0199 nats)" without qualifying whether this is a large or small effect. The magnitude is small; a reviewer familiar with attention entropy scales may question whether this difference is practically meaningful, even if statistically significant (p < 0.05).

**Reviewer suggestion:** Add a qualifier such as "a modest but statistically significant effect" when describing the −0.0199 nats difference, to avoid implying large-magnitude restructuring from a small-n experiment.

**Type:** Calibration

---

## HRN-R2-4 — Abstract: closing on infrastructure is anticlimactic (repeated from R1 HRN-3)

**Location:** Abstract (final sentence)

**Issue:** The abstract closes: "Full accuracy evaluation on LLaMA-2-7B and Mistral-7B-v0.1 is the immediate next step, supported by the validated BudgetSweepEvaluator and SpearmanAnalyzer infrastructure we provide." Ending on infrastructure rather than on the mechanistic implication is structurally anticlimactic for a mechanistic paper. This issue was raised in R1 as HRN-3 and was not addressed.

**Reviewer suggestion:** Consider restructuring the final sentence to close on the mechanistic implication: "These mechanistic results establish that eviction-aware training creates the right representational conditions for accuracy recovery under KV cache constraints; full accuracy evaluation on LLaMA-2-7B and Mistral-7B-v0.1 is the immediate next step, supported by the validated BudgetSweepEvaluator and SpearmanAnalyzer infrastructure we provide."

**Type:** Structure

---

## HRN-R2-5 — References: dual "Zhang et al. 2023" citations may confuse reviewers

**Location:** References section and all in-text citations of H2O and AdaLoRA

**Issue:** Both H2O [Zhang et al., 2023] and AdaLoRA [Zhang et al., 2023] appear as "Zhang et al. 2023" in citations. The bibliography correctly distinguishes them (H2O: Zhang, Zhenyu et al., arXiv:2306.14048; AdaLoRA: Zhang, Qingru et al., arXiv:2303.10512), but a reviewer scanning the reference list may initially flag two identical "Zhang et al. 2023" entries.

**Reviewer suggestion:** Disambiguate using "[Zhang et al., 2023a]" (H2O, June 2023) and "[Zhang et al., 2023b]" (AdaLoRA, March 2023) throughout in-text citations and the reference list.

**Type:** Citation

---

## HRN-R2-6 — Section 3.3 Table: `attn_implementation` description imprecise

**Location:** Section 3.3 hyperparameter table, `attn_implementation='eager'` row

**Current text:** "Required for H2O+SDPA compatibility"

**Issue:** The `attn_implementation='eager'` setting is the FIX for an incompatibility, not a compatibility requirement. The current wording implies H2O and SDPA are compatible with this setting, whereas the truth is that SDPA is incompatible with H2O, and 'eager' is the workaround.

**Reviewer suggestion:** Change to "Required to avoid H2O+SDPA incompatibility (see Section 6.3)" for precision.

**Type:** Precision

---

## Summary — R2 Human Review Notes

| ID | Location | Type | Status after R2 |
|----|----------|------|-----------------|
| HRN-R2-1 | Section 5.1 | Terminology | Not changed; author judgment needed |
| HRN-R2-2 | Section 4.3 | Clarity | Not changed; author judgment needed |
| HRN-R2-3 | Section 5.2, 6.1 | Calibration | Not changed; author judgment needed |
| HRN-R2-4 | Abstract | Structure | Not changed; repeated from R1 HRN-3 |
| HRN-R2-5 | References | Citation | Not changed; author judgment needed |
| HRN-R2-6 | Section 3.3 | Precision | Not changed; author judgment needed |

**Items requiring author action before final submission:** HRN-R2-1, HRN-R2-2, HRN-R2-3, HRN-R2-5, HRN-R2-6
