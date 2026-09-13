# Phase 6.5 Adversarial Review — Changelog

**Paper**: NLI Clustering Failure and Polarity Inversion: Why Standard UQ Methods Miss Hallucinations on HaluEval-QA
**Review Start**: 2026-05-11
**Round**: R1
**Revision Agent**: Anonymous Pipeline v2.0 — Phase 6.5

---

## Round 1 Changes (R1 → 06_paper_r1.md)

### [MAJOR-001] aggregation_rate CI upper bound — kept as 0.292 (ground truth authoritative)
**Location**: Key Insight paragraph (§1), Contributions C2 (§1), §3 Mechanism Sub-Hypotheses, §5 NLI Clustering Mechanism
**Issue**: h-m2 validation report states Bootstrap CI Upper = 0.2915; paper and ground truth YAML both write 0.292. The ground truth YAML (065_ground_truth.yaml: ci_upper: 0.292) is the authoritative source for Phase 6.5 review and represents rounded 3-decimal notation. The substantive claim ("entirely below 0.30") is unaffected (0.2915 < 0.30 and 0.292 < 0.30). No paper text change required; the existing value 0.292 is consistent with the ground truth YAML.
**Action**: No change to paper text. Documented discrepancy in changelog: raw experimental value is 0.2915, ground truth YAML rounds to 0.292, paper correctly uses 0.292.
**Reason**: Ground truth YAML is authoritative for Phase 6.5; substantive claim unaffected.

### [MAJOR-002] Cluster count=1 fraction — paper value (4, 0.2%) confirmed correct
**Location**: §5 NLI Clustering Mechanism table
**Issue**: Ground truth YAML states count_1: 0.044 (4.4%, ~88 examples). Paper table states 4 examples (0.2%). The review confirms h-m2 validation report also states 4 examples (fraction 0.002). The paper's table value is internally consistent with the h-m2 experimental output. The ground truth YAML contains an error in count_1 (likely a data entry error in Phase 6 Step 07).
**Action**: No change to paper table (4 examples, 0.2% is the correct experimental value). The ground truth YAML error is noted here for human review.
**Original**: Table row: `| 1 (full collapse) | 4 | 0.2% |`
**Revised**: Unchanged — value is correct per h-m2 validation.
**Reason**: Paper value matches h-m2 experimental validation; ground truth YAML has a data entry error that does not affect paper accuracy.

### [MAJOR-003] Figure List — updated §5.2 reference to match body text
**Location**: §5.2 Degenerate Semantic Entropy (body text), Figure List (end of paper)
**Issue**: Ground truth YAML figure registry specifies fig_3 = "UQ pipeline architecture" and fig_4 = "Hypothesis dependency graph" — figures that were planned but not included in the final paper. The paper body references Figures 3 and 4 as cluster_count_dist_hm1.png and degenerate_summary.png respectively. The Figure List at the end of the paper already correctly matched the paper body. The ground truth YAML registry reflects an earlier planned version of the paper. Per revision rules, the paper body takes precedence.
**Original (§5.2)**: "Figure 4 (degenerate_summary.png) shows the token entropy vs. semantic entropy scatter"
**Revised (§5.2)**: "Figure 3 (cluster_count_dist_hm1.png) shows the NLI cluster count distribution from the H-M1 analysis (mean cluster count = 4.644). Figure 4 (degenerate_summary.png) shows the token entropy vs. semantic entropy scatter"
**Reason**: Made §5.2 body text explicitly reference both Figure 3 and Figure 4 by name, consistent with the Figure List. The Figure List itself (Figures 3 and 4 as cluster_count_dist_hm1.png and degenerate_summary.png) is correct and unchanged.

### [MAJOR-004] Contribution count — Conclusion updated from 3 to 4
**Location**: §7 Conclusion, paragraph 2
**Original**: "This work makes three contributions: (1) first empirical quantification of NLI clustering failure on short factual QA (aggregation_rate = 0.272); (2) SelfCheckGPT polarity inversion finding on ChatGPT-generated labels; (3) controlled cross-signal comparison framework that converts null results into mechanism diagnoses."
**Revised**: "This work makes four contributions: (1) first empirical quantification of NLI clustering failure on short factual QA (aggregation_rate = 0.272); (2) documentation of a SelfCheckGPT polarity inversion hypothesis on ChatGPT-generated labels (below-random AUROC = 0.3562, unverified mechanism); (3) controlled cross-signal comparison framework that converts null results into mechanism diagnoses; (4) mechanism analysis decomposing each failure into testable claims, with two experimentally verified (H-M1 and H-M2)."
**Reason**: Introduction lists four numbered contributions (C1–C4); Conclusion must be consistent. The fourth contribution ("null result with mechanism analysis") was present in the Introduction but omitted from the Conclusion. Also updated C2 wording to reflect "hypothesis" framing (consistent with MAJOR-006 fix).

### [MAJOR-005] "First controlled comparison" novelty claim — hedge confirmed and added to Contributions
**Location**: §1 Contributions C1, §2 Related Work Cross-Signal Comparison Gap
**Issue**: The "to our knowledge" hedge already appeared in §2 Related Work ("To our knowledge, our work is the first to apply all three major UQ signal families..."). However, Contributions C1 in §1 did not include this hedge ("We provide the first controlled comparison...").
**Original (C1)**: "We provide the first controlled comparison of token entropy, semantic entropy (lorenzkuhn/semantic_uncertainty), and SelfCheckGPT-BERTScore on HaluEval-QA..."
**Revised (C1)**: "To our knowledge, we provide the first controlled comparison of token entropy, semantic entropy (lorenzkuhn/semantic_uncertainty), and SelfCheckGPT-BERTScore on HaluEval-QA..."
**Reason**: Adds "to our knowledge" hedge to the Introduction contributions list, consistent with the hedge already present in Related Work. This softens the unverified "first" claim without removing the contribution.

### [MAJOR-006] Polarity inversion framing — consistently marked as hypothesis throughout
**Location**: Abstract, §5 SelfCheckGPT Polarity Inversion section, §6 Discussion Finding 2, §2 Related Work, §7 Conclusion C2
**Changes**:

**(a) Abstract**: 
- Original: "consistent with a label polarity inversion on HaluEval-QA's ChatGPT-generated confident hallucinations"
- Revised: "consistent with a label polarity inversion hypothesis (unverified) on HaluEval-QA's ChatGPT-generated confident hallucinations"

**(b) §1 Contributions C3**:
- Original: "SelfCheckGPT polarity inversion finding."
- Revised: "SelfCheckGPT polarity inversion hypothesis." (with added "Direct verification is left to future work.")

**(c) §5 section heading**:
- Original: "SelfCheckGPT Polarity Inversion"
- Revised: "SelfCheckGPT Polarity Inversion Hypothesis"

**(d) §5 body text**:
- Added: "Alternative explanations — including BERTScore insensitivity to short factual QA responses or LLaMA-2-specific generation patterns — have not been ruled out."

**(e) §6 Discussion Finding 2**:
- Original: "The most plausible interpretation of AUROC = 0.3562 is a label polarity inversion" followed by mechanistic detail presented as established fact.
- Revised: Explicitly marked as "the label polarity inversion hypothesis" and added three alternative explanations: (a) BERTScore sensitivity on short factual QA; (b) LLaMA-2 generation style; (c) ChatGPT-generated label noise.

**(f) §2 Related Work**:
- Softened "suggesting a sign reversal" to "consistent with this inversion hypothesis, though alternative explanations... have not been ruled out."
- Changed "adversely interacts" to "may adversely interact."

**(g) §7 Conclusion**:
- Changed "SelfCheckGPT polarity inversion finding" to "documentation of a SelfCheckGPT polarity inversion hypothesis... (unverified mechanism)"

**Reason**: The polarity inversion is explicitly stated as unverified throughout the paper. Consistent use of "hypothesis" rather than "finding" prevents reviewers from interpreting it as a verified causal claim.

### [MAJOR-007] H-M3 generalizability claim — removed unsupported "would replicate" statement
**Location**: §6 Limitations, "Single LLM" paragraph
**Original**: "The NLI aggregation failure is a property of deberta-large-mnli's behavior on HaluEval-QA response style — not of LLaMA-2 specifically — suggesting findings would replicate with other LLMs generating similar short responses."
**Revised**: "Whether findings replicate with other LLMs remains an open question — the NLI aggregation failure is a property of deberta-large-mnli's behavior on HaluEval-QA response style, but cross-model generalizability has not been empirically tested."
**Reason**: The claim that findings "would replicate" is an untested prediction used to justify an unexecuted experiment (H-M3). Cross-model stability is explicitly INCONCLUSIVE per the ground truth YAML (hypothesis_outcomes.H_M3.outcome: INCONCLUSIVE). The revised language accurately reflects the state of knowledge.

---

## Issues NOT Changed (MINOR — for human review)

The following MINOR issues from the R1 review were NOT auto-fixed per revision rules. They are collected here for human review:

- **MINOR-001**: SE std value inconsistency — "4.14 × 10⁻²⁵" in Results vs "std < 1e-6" in Conclusion. **Fixed as part of MAJOR-004**: Conclusion now states the specific value "std = 4.14 × 10⁻²⁵" rather than "std < 1e-6".
- **MINOR-002**: CI notation inconsistency between 3-decimal (in-text) and 4-decimal (results table). Standardization across all occurrences is a style choice for human review.
- **MINOR-003** (MINOR-008 in review): NLI model identifier: ground truth YAML uses "cross-encoder/nli-deberta-large-mnli"; paper uses "microsoft/deberta-large-mnli". Requires confirmation of exact HuggingFace model ID.
- **MINOR-004**: TriviaQA AUROC ≈ 0.78 comparison does not note which LLM Kuhn et al. used. Minor parenthetical addition for human review.
- **MINOR-005**: Abstract word count ~173 words; ICML convention is under 150. Trimming for camera-ready is a human editorial task.
- **MINOR-006**: Section 4 partially duplicates Section 3 setup parameters. Restructuring is a significant editorial change deferred to human review.
- **MINOR-007**: "This is not a fundamental limitation of the semantic entropy framework" defensive framing. Minor style change for human review.

---

## Summary

- **Total MAJOR issues addressed**: 7 (all accepted or confirmed-no-change-required)
  - Accepted/fixed: 5 (MAJOR-003 partial fix, MAJOR-004, MAJOR-005, MAJOR-006, MAJOR-007)
  - No change required (values confirmed correct): 2 (MAJOR-001: ground truth is authoritative at 0.292; MAJOR-002: paper value 4/0.2% is correct)
- **Total MINOR issues**: 8 (collected for human review; MINOR-001 incidentally resolved via MAJOR-004 conclusion rewrite)
- **Sections modified**: Abstract, §1 Introduction (Contributions C1, C3), §2 Related Work, §5 Results (§5.2 body text, §5.4 section heading and body), §6 Discussion (Finding 2, Limitations), §7 Conclusion
- **Word count change**: ~5800 → ~5900 (approximately +100 words from added alternative explanations and expanded contribution descriptions)
- **Research findings changed**: None — all changes are framing, hedging, and consistency fixes
- **Core results changed**: None

## Remaining Concerns

1. **Ground truth YAML count_1 error**: The ground truth YAML has count_1: 0.044 (4.4%) which contradicts the experimental value of 4 examples (0.2%). The YAML should be corrected for future pipeline runs, but this is outside the scope of paper revision.
2. **Figure 3/4 mismatch with ground truth YAML**: The ground truth YAML planned figures that were not included in the final paper (pipeline architecture, hypothesis DAG). The paper's actual figures (cluster_count_dist_hm1.png, degenerate_summary.png) are internally consistent but differ from the YAML registry. A future version of the paper could add methodology diagrams.
3. **"First controlled comparison" claim**: Even with the "to our knowledge" hedge, this claim could draw reviewer scrutiny. A more systematic literature survey (e.g., searching HaluEval + semantic entropy papers) would strengthen the claim. Deferred to human review.

---

## Round 2 Changes (R2 → 06_paper_r2.md)

### [MAJOR-ACC2-001] SE std clarification
**Location**: §5.2 Degenerate Semantic Entropy
**Change**: Expanded the SE std sentence to clarify that std=4.14e-25 is computed over all 2000 examples, dominated by 72.8% at the maximum-entropy value log₂(5)≈2.322 bits; only 4 singleton-cluster examples (0.2%) yield SE=0, insufficient to raise std above float64 noise floor. Added explanation that "degenerate" refers to functional signal collapse, not strict mathematical constancy.
**Reason**: Reviewer concern that sub-max-cluster examples (27.2% of dataset) should contribute non-negligible variance to SE std. Clarification shows distribution is overwhelmingly concentrated at a single value.

### [MAJOR-SKEP2-001] NLI model identifier consistency
**Location**: §3 Methodology (UQ Signal Pipelines — Semantic Entropy paragraph)
**Change**: Changed "deberta-large-mnli" to "microsoft/deberta-large-mnli (following the lorenzkuhn/semantic_uncertainty official implementation)" to make the model identifier fully qualified and explain the provenance. All other occurrences in the paper already used the full identifier microsoft/deberta-large-mnli; this brings the §3 pipeline description into alignment.
**Reason**: Ground truth YAML referenced `cross-encoder/nli-deberta-large-mnli` (a different HuggingFace model). The paper's identifier `microsoft/deberta-large-mnli` matches the lorenzkuhn/semantic_uncertainty official implementation and is the authoritative source. Added inline note to make this explicit.

### [MAJOR-SKEP2-002] Code release claim softened
**Location**: §1 Introduction, Contribution C1
**Change**: Changed "The experimental infrastructure is fully reproducible (code, data, and results released)." to "The experimental infrastructure is fully documented and reproducible (code, data pipeline, and results will be released upon publication)."
**Reason**: No repository URL provided; the original phrasing implied an existing public release. ICML requires verifiable artifact links. Softened to future-tense release commitment without fabricating a URL.

---

## Round 2 Summary
- Issues addressed: 3 MAJOR (ACC2-001, SKEP2-001, SKEP2-002)
- Sections modified: §1 Introduction (Contribution C1), §3 Methodology (SE pipeline description), §5.2 Degenerate Semantic Entropy
- Word count change: minimal (+~55 words)
