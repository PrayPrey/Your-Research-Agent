# Phase 6.5 Adversarial Review Changelog

## Round 1 Revisions

**Generated**: 2026-05-21T13:45:00
**Review File**: paper/review/065_review_r1.md
**Input**: paper/06_paper.md
**Output**: paper/06_paper_r1.md

---

### Changes Made

#### R1-FIX-001: SelfCheckGPT-NLI "robust alternative" overclaim — Abstract
- **Issue**: MAJOR-1 / MAJOR-BR-1
- **Location**: Abstract
- **Before**: "show that token-probability and SelfCheckGPT-NLI remain valid and competitive (AUROC>0.68) in the degenerate regime"
- **After**: "show that token-probability remains valid and competitive (AUROC>0.68 on both datasets), and find that SelfCheckGPT-NLI is competitive on TriviaQA (AUROC=0.6862) but underperforms on NQ (AUROC=0.4508), suggesting dataset-dependent reliability for sampling-based alternatives"
- **Rationale**: The original claim "AUROC>0.68" applies to NLI only on TriviaQA; on NQ NLI scores 0.4508 (below chance). The abstract must accurately reflect the cross-dataset evidence.

#### R1-FIX-002: SelfCheckGPT-NLI characterization — Section 2 Related Work
- **Issue**: MAJOR-1 / MAJOR-BR-1
- **Location**: Section 2, SelfCheckGPT paragraph
- **Before**: "Our results show that SelfCheckGPT-NLI remains competitive with token-probability (AUROC=0.6862) even under high degeneracy—because NLI-based entailment detection exploits subtle paraphrase variations among the 11% of diverse queries, providing sufficient discriminative signal without requiring the clustering structure that SE requires."
- **After**: "Our results show that SelfCheckGPT-NLI is competitive with token-probability on TriviaQA (AUROC=0.6862) but underperforms substantially on NQ (AUROC=0.4508)—because NLI-based entailment detection exploits subtle paraphrase variations among the 11% of diverse TriviaQA queries but does not generalize this advantage to the NQ distribution (which has 19.4% correctness rate and different answer characteristics)."
- **Rationale**: Accurately characterizes the dataset-dependent nature of NLI performance.

#### R1-FIX-003: SelfCheckGPT-NLI characterization — Section 1 Contribution 2
- **Issue**: MAJOR-1 / MAJOR-BR-1
- **Location**: Section 1 (Introduction), contribution statement paragraph
- **Before**: "Second, we *validate token-probability and SelfCheckGPT-NLI as robust alternatives* in the low-diversity regime: both achieve AUROC>0.68 and remain valid across datasets without requiring semantic diversity."
- **After**: "Second, we *evaluate token-probability and SelfCheckGPT-NLI in the low-diversity regime*: token-probability achieves AUROC>0.68 and remains valid across both datasets; SelfCheckGPT-NLI is competitive on TriviaQA but exhibits dataset-dependent performance (AUROC=0.4508 on NQ), highlighting the need for method selection to account for dataset characteristics."
- **Rationale**: Removes unwarranted "robust alternatives" framing; accurately scopes each method's performance.

#### R1-FIX-004: SelfCheckGPT-NLI characterization — Section 1 paragraph 4
- **Issue**: MAJOR-1 / MAJOR-BR-1
- **Location**: Section 1 (Introduction), paragraph 4 (regime description)
- **Before**: "Token-probability and SelfCheckGPT-NLI, by contrast, remain valid: they do not rely on semantic diversity and achieve AUROC of 0.6835 and 0.6862 on TriviaQA respectively."
- **After**: "Token-probability, by contrast, remains valid across both datasets: it does not rely on semantic diversity and achieves AUROC of 0.6835 (TriviaQA) and 0.6551 (NQ). SelfCheckGPT-NLI achieves AUROC of 0.6862 on TriviaQA but only 0.4508 on NQ, indicating its utility varies across datasets."
- **Rationale**: Distinguishes token_prob (robust) from NLI (TriviaQA-specific). Adding NQ values for token_prob also improves completeness.

#### R1-FIX-005: SelfCheckGPT-NLI — Section 4 Key Contrasts
- **Issue**: MAJOR-1 / MAJOR-BR-1
- **Location**: Section 4, Key Contrasts subsection
- **Before**: "SelfCheckGPT-NLI matches token_prob on TriviaQA (0.6862 vs. 0.6835) despite identical degenerate_fraction: NLI entailment detects semantic variation in the 11% of diverse queries more sensitively than BERTScore's cosine similarity."
- **After**: "SelfCheckGPT-NLI matches token_prob on TriviaQA (0.6862 vs. 0.6835) despite identical degenerate_fraction: NLI entailment detects semantic variation in the 11% of diverse queries more sensitively than BERTScore's cosine similarity. However, SelfCheckGPT-NLI fails on NQ (0.4508, below chance), indicating its utility is dataset-dependent rather than universally robust to low diversity."
- **Rationale**: The results section must present both the TriviaQA success and NQ failure.

#### R1-FIX-006: SelfCheckGPT-NLI — Section 5 Practical Recommendations
- **Issue**: MAJOR-1 / MAJOR-BR-1
- **Location**: Section 5, Practical Recommendations
- **Before**: "Use SelfCheckGPT-NLI when a sampling-based method is required: competitive with token-probability, robust to low diversity."
- **After**: "Use SelfCheckGPT-NLI with caution when a sampling-based method is required: competitive with token-probability on TriviaQA (AUROC=0.6862), but underperforms on NQ (AUROC=0.4508). Dataset characteristics—including correctness rate distribution—appear to influence its reliability."
- **Rationale**: The recommendation must warn practitioners about the NQ failure.

#### R1-FIX-007: SelfCheckGPT-NLI — Section 6 Conclusion
- **Issue**: MAJOR-1 / MAJOR-BR-1
- **Location**: Section 6, Conclusion
- **Before**: "Token-probability (AUROC=0.6835) and SelfCheckGPT-NLI (AUROC=0.6862) remain valid and competitive in the degenerate regime, providing robust alternatives for base-model deployment."
- **After**: "Token-probability (AUROC=0.6835 on TriviaQA, 0.6551 on NQ) provides a robust alternative across both datasets. SelfCheckGPT-NLI is competitive on TriviaQA (AUROC=0.6862) but underperforms on NQ (AUROC=0.4508), suggesting its utility depends on dataset characteristics and should not be assumed universally robust in the degenerate regime."
- **Rationale**: Conclusion must reflect accurate cross-dataset characterization.

#### R1-FIX-008: Causal "root cause" language — Abstract
- **Issue**: MAJOR-2 / MAJOR-SE-2
- **Location**: Abstract
- **Before**: "The root cause is *sampling degeneracy*: 89% of TriviaQA queries..."
- **After**: "The evidence is consistent with *sampling degeneracy* as the primary cause: 89% of TriviaQA queries..."
- **Rationale**: The causal attribution is mechanistically compelling but not confirmed by a controlled experiment (e.g., comparing instruct vs. base or sweeping temperature). Hedging to "consistent with" accurately represents the inferential status.

#### R1-FIX-009: Causal language — Section 1 Introduction sentence 3
- **Issue**: MAJOR-2 / MAJOR-SE-2
- **Location**: Section 1, paragraph 1
- **Before**: "It is a systematic collapse caused by a structural property of base model sampling..."
- **After**: "It is a systematic collapse consistent with a structural property of base model sampling..."
- **Rationale**: Consistent softening of causal language throughout.

#### R1-FIX-010: Causal language + explicit caveat — Section 5 Discussion
- **Issue**: MAJOR-2 / MAJOR-SE-2
- **Location**: Section 5, "Why Base Models Are Degenerate" subsection
- **Before**: "The discrepancy between our results (SE AUROC=0.47–0.55) and Farquhar et al. (2024) (SE AUROC=0.72–0.79) is fully explained by this model-type difference."
- **After**: "The discrepancy between our results (SE AUROC=0.47–0.55) and Farquhar et al. (2024) (SE AUROC=0.72–0.79) is fully accounted for by this model-type difference. We note that the mechanistic account (K=1 → SE=0 → no discriminative signal) is well-supported by the data, though confirming the causal direction formally would require a controlled experiment that independently varies sampling diversity—for instance, by comparing base versus instruct variants or sweeping temperature (planned as future work F1 and F2)."
- **Rationale**: Adds the explicit caveat that the causal direction is mechanistically motivated but requires confirmation, as noted in the ground truth inference_claims.

#### R1-FIX-011: Causal language — Section 6 Conclusion
- **Issue**: MAJOR-2 / MAJOR-SE-2
- **Location**: Section 6, Conclusion paragraph 2
- **Before**: "The explanation is precise and actionable: Llama-3-8B-Base produces semantically identical responses for 89% of TriviaQA queries..."
- **After**: "The explanation is mechanistically precise and actionable: Llama-3-8B-Base produces semantically identical responses for 89.4% of TriviaQA queries... The evidence is strongly consistent with sampling degeneracy as the mechanistic account of this failure; confirming the causal direction requires controlled diversity manipulation experiments (F1, F2), which we identify as the highest-priority future work."
- **Rationale**: Conclusion states causal hedge explicitly and frames confirmatory experiments correctly.

#### R1-FIX-012: Novelty claim for degenerate_fraction — Section 2 Related Work
- **Issue**: MAJOR-3 / MAJOR-SE-1
- **Location**: Section 2 Related Work, after "The sampling diversity assumption" subsection
- **Before**: [No paragraph acknowledging prior sampling diversity literature]
- **After**: Added new subsection "Sampling diversity metrics in prior work" acknowledging Li et al. (2016), Vijayakumar et al. (2016), Self-BLEU [Zhu et al., 2018], and distinct-n metrics, and explaining how `degenerate_fraction` specifically differs as a UQ validity diagnostic rather than a general diversity metric.
- **Rationale**: The paper's novelty claim for degenerate_fraction is vulnerable to reviewers familiar with the diversity literature. This addition acknowledges the prior work and repositions the contribution as a specifically-framed UQ diagnostic rather than a wholly new diversity concept.

#### R1-FIX-013: New references for diversity literature
- **Issue**: MAJOR-3 (supporting fix)
- **Location**: References section
- **Before**: [No Li et al. 2016, Vijayakumar et al. 2016, or Zhu et al. 2018]
- **After**: Added three references: Li et al. (2016) NAACL diversity-promoting objective; Vijayakumar et al. (2016) Diverse Beam Search; Zhu et al. (2018) Texygen/Self-BLEU.
- **Rationale**: Required to support the diversity literature paragraph in Related Work.

---

### Summary

- FATAL issues fixed: 0/0
- MAJOR issues fixed: 3/3
  - MAJOR-1 (SelfCheckGPT-NLI overclaim): Fixed in Abstract, Introduction, Related Work (Section 2), Results (Section 4), Practical Recommendations (Section 5), and Conclusion (Section 6) — 7 location fixes (R1-FIX-001 through R1-FIX-007)
  - MAJOR-2 (Causal "root cause" language): Fixed in Abstract, Introduction, Discussion, and Conclusion — 4 location fixes (R1-FIX-008 through R1-FIX-011)
  - MAJOR-3 (degenerate_fraction novelty claim): Fixed by adding sampling diversity literature paragraph in Related Work with 3 new references — 2 fixes (R1-FIX-012 through R1-FIX-013)
- MINOR issues collected (not fixed): 7 (see 065_human_review_notes.md)

---

## Round 2 Revisions

**Generated**: 2026-05-21T14:15:00
**Review File**: paper/review/065_review_r2.md
**Input**: paper/06_paper_r1.md
**Output**: paper/06_paper_r2.md

### Changes Made

#### R2-FIX-001: Define mean_K in Table 2
- **Issue**: MAJOR-R2-1
- **Location**: Section 4, Table 2 (after table rows, before prose)
- **Before**: Table 2 presented "mean_K" column header with no definition in text; natural reading (mean number of clusters) is mathematically impossible given degenerate_fraction=0.894 with N=10.
- **After**: Added italicized note immediately below Table 2: "*Note: `degenerate_fraction` = proportion of queries where all N=10 samples fall into a single semantic cluster (K=1). `mean_K` = mean number of samples in the dominant (largest) semantic cluster per query, out of N=10 total samples. For queries with K=1 (all samples identical), mean_K contribution = 10; the overall mean of 9.884 reflects that the dominant cluster captures on average 98.84% of samples per query on TriviaQA. mean_K is NOT the mean number of clusters—that interpretation is mathematically inconsistent with degenerate_fraction given N=10.*"
- **Rationale**: Prevents misleading interpretation of mean_K as mean number of clusters, which would be mathematically impossible (would require ~84.8 clusters in 10.6% of queries given N=10 samples).

#### R2-FIX-002: Correct "AUROC>0.68 on both datasets" — Abstract
- **Issue**: MAJOR-R2-2
- **Location**: Abstract
- **Before**: "show that token-probability remains valid and competitive (AUROC>0.68 on both datasets)"
- **After**: "show that token-probability remains valid and competitive (AUROC of 0.6835 on TriviaQA and 0.6551 on NQ)"
- **Rationale**: NQ token_prob AUROC = 0.6551 < 0.68; the ">0.68" claim was factually incorrect.

#### R2-FIX-003: Correct "AUROC>0.68" — Section 1 Introduction (contribution 2)
- **Issue**: MAJOR-R2-2
- **Location**: Section 1, second contribution paragraph
- **Before**: "token-probability achieves AUROC>0.68 and remains valid across both datasets"
- **After**: "token-probability achieves AUROC>0.65 on both datasets (0.6835 on TriviaQA, 0.6551 on NQ) and remains valid across both datasets"
- **Rationale**: Both actual values (0.6835, 0.6551) are above 0.65, making ">0.65" factually correct. Exact values also provided for precision.

#### R2-FIX-004: Correct "AUROC>0.68" — Section 5 Practical Recommendations
- **Issue**: MAJOR-R2-2
- **Location**: Section 5, Practical Recommendations, token-probability bullet
- **Before**: "Use token-probability for base model factual QA: AUROC>0.68 on both TriviaQA and NQ, single forward pass, no diversity requirement."
- **After**: "Use token-probability for base model factual QA: AUROC of 0.6835 (TriviaQA) and 0.6551 (NQ), both above 0.65, single forward pass, no diversity requirement."
- **Rationale**: Replaces factually incorrect ">0.68" with the precise values; ">0.65" is a correct lower bound for both.

### Summary
- FATAL issues fixed: 0/0
- MAJOR issues fixed: 2/2
  - MAJOR-R2-1 (mean_K undefined): Fixed by adding definition note below Table 2 (R2-FIX-001)
  - MAJOR-R2-2 (AUROC>0.68 incorrect): Fixed in Abstract, Introduction, and Practical Recommendations — 3 location fixes (R2-FIX-002 through R2-FIX-004)
- MINOR issues collected (not fixed): 6 (see 065_human_review_notes.md Round 2 Issues section)

---

## Final Summary (v2.0)

**Total Revisions Made**: 17 (13 in R1, 4 in R2)
**Sections Modified**: Abstract, Introduction, Related Work, Results (Table 2), Discussion, Conclusion, References
**Rounds**: 2

**Review Process**:
- Started: 2026-05-21T13:30:00
- Completed: 2026-05-21T14:30:00
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Issues Summary**:
- R1: 0 FATAL, 3 MAJOR found → 3 MAJOR resolved
- R2: 0 FATAL, 2 MAJOR found → 2 MAJOR resolved
- Total MAJOR resolved: 5/5
- MINOR collected (not auto-fixed): 13

**Files Generated**:
- paper/06_paper_r1.md (R1 revised)
- paper/06_paper_r2.md (R2 revised)
- paper/06_paper_final.md (final paper)
- paper/review/065_review_r1.md (R1 adversary review)
- paper/review/065_review_r2.md (R2 adversary review)
- paper/review/065_review_summary.md (consolidated review)
- paper/review/065_human_review_notes.md (MINOR issues for human review)
- paper/review/065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
